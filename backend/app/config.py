import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

# Load .env if present
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BASE_DIR / ".env")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nahida_db")
DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "2"))

# ML configuration
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", str(PROJECT_ROOT / "ml" / "models" / "isolation_forest.joblib"))

# CORS settings
raw_cors = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,https://1ggc4w77-5173.inc1.devtunnels.ms,https://1qgc4w77-5173.in1.devtunnels.ms"
)
origins = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]

frontend_url = os.getenv("FRONTEND_URL", "").strip()
if frontend_url and frontend_url not in origins:
    origins.append(frontend_url)

# Add explicit frontend dev tunnel origins
for tunnel_origin in [
    "https://1ggc4w77-5173.inc1.devtunnels.ms",
    "https://1qgc4w77-5173.in1.devtunnels.ms",
    "https://1ggc4w77-8000.inc1.devtunnels.ms",
    "https://1qgc4w77-8000.in1.devtunnels.ms",
]:
    if tunnel_origin not in origins:
        origins.append(tunnel_origin)

CORS_ORIGINS = origins

# Mock Telemetry Settings (Switchable via .env MOCK_TELEMETRY=true/false)
MOCK_TELEMETRY = os.getenv("MOCK_TELEMETRY", "true").strip().lower() in ("true", "1", "yes", "on")
MOCK_INTERVAL_SECONDS = float(os.getenv("MOCK_INTERVAL_SECONDS", "3.0"))

# Risk Engine Thresholds (Configurable Prototype Values - Not Engineering Certified)
RISK_CONFIG = {
    "disclaimer": "DEMO / CONFIGURABLE THRESHOLDS — NOT CERTIFIED MINE SAFETY THRESHOLDS",
    "weights": {
        "tilt": 0.25,
        "vibration": 0.20,
        "crack_displacement": 0.25,
        "rate_of_change": 0.15,
        "ml_anomaly": 0.15,
    },
    "thresholds": {
        "tilt_max_deg": 1.2,
        "vibration_max_g": 1.0,
        "crack_max_mm": 7.0,
        "crack_rate_max_mm_per_s": 0.5,
        "tilt_rate_max_deg_per_s": 0.5,
    },
    "levels": {
        "WATCH": 45.0,
        "HIGH": 70.0,
        "CRITICAL": 85.0,
    }
}
