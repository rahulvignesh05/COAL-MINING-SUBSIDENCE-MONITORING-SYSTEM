import os
import hmac
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import BASE_DIR

JWT_SECRET = os.getenv("JWT_SECRET", "nahida-super-secure-production-control-center-secret-key-2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # 12 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# Role definitions & Centralized Permissions
VALID_ROLES = ["worker", "head", "administrative"]

ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "worker": [
        "view_dashboard",
        "view_sensors",
        "view_alerts"
    ],
    "head": [
        "view_dashboard",
        "view_sensors",
        "view_alerts",
        "acknowledge_alerts",
        "view_history"
    ],
    "administrative": [
        "view_dashboard",
        "view_sensors",
        "view_alerts",
        "acknowledge_alerts",
        "manage_users",
        "manage_nodes",
        "manage_zones",
        "system_configuration"
    ]
}


def hash_password(password: str) -> str:
    """Secure PBKDF2-HMAC-SHA256 password hashing with random salt."""
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return f"{salt.hex()}:{pw_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a plain password against the stored salt:hash."""
    try:
        parts = stored_hash.split(":")
        if len(parts) != 2:
            return False
        salt = bytes.fromhex(parts[0])
        expected_hash = bytes.fromhex(parts[1])
        actual_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return hmac.compare_digest(actual_hash, expected_hash)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


# In-memory session tracking for logout invalidation
blacklisted_tokens = set()


def invalidate_token(token: str):
    blacklisted_tokens.add(token)


def is_token_blacklisted(token: str) -> bool:
    return token in blacklisted_tokens


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been logged out. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    role = payload.get("role")
    if not username or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from app.database import in_memory_store
    user = in_memory_store.get_user_by_username(username)
    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or not found.",
        )

    return user


def require_roles(allowed_roles: List[str]):
    """Role-based access control dependency."""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role", "").lower()
        if user_role not in [r.lower() for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {', '.join(allowed_roles)}",
            )
        return current_user
    return role_checker
