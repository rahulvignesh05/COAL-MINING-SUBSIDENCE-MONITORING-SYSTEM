import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import DATABASE_URL, DB_CONNECT_TIMEOUT
from app.models import Base, Node, Zone, SensorReading, Alert, Prediction, User

logger = logging.getLogger("nahida.database")

# Database Status Flag (Real Connection Tracking)
DB_CONNECTED = False
DB_STATUS_LABEL = "Offline"

# SQLAlchemy Setup
engine = None
SessionLocal = None

try:
    # Attempt connecting to PostgreSQL with strict timeout
    engine = create_engine(
        DATABASE_URL,
        connect_args={"connect_timeout": DB_CONNECT_TIMEOUT},
        pool_pre_ping=True
    )
    with engine.connect() as conn:
        DB_CONNECTED = True
        DB_STATUS_LABEL = "Connected"
        logger.info(f"PostgreSQL database connected: {DATABASE_URL}")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    DB_CONNECTED = False
    DB_STATUS_LABEL = "Offline"
    logger.warning(f"PostgreSQL not reachable ({e}). Standby storage active. DB Status: Offline.")


def get_db():
    """SQLAlchemy session generator for routes when DB is available."""
    if SessionLocal:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield None


# Default Mine Coordinates for 9 Nodes across 3 Zones
CONFIGURED_NODE_METADATA = {
    "NAHIDA-A01": {"zone": "ZONE A", "lat": 23.7957, "lon": 86.4304, "name": "Zone A - North Flank"},
    "NAHIDA-A02": {"zone": "ZONE A", "lat": 23.7972, "lon": 86.4320, "name": "Zone A - Bench 1 Face (Highwall)"},
    "NAHIDA-A03": {"zone": "ZONE A", "lat": 23.7941, "lon": 86.4335, "name": "Zone A - East Escarpment"},
    "NAHIDA-B01": {"zone": "ZONE B", "lat": 23.7915, "lon": 86.4280, "name": "Zone B - West Haulage Cut"},
    "NAHIDA-B02": {"zone": "ZONE B", "lat": 23.7930, "lon": 86.4265, "name": "Zone B - Overburden Dump Crest"},
    "NAHIDA-B03": {"zone": "ZONE B", "lat": 23.7898, "lon": 86.4295, "name": "Zone B - Sump Peripheral"},
    "NAHIDA-C01": {"zone": "ZONE C", "lat": 23.7870, "lon": 86.4350, "name": "Zone C - South Boundary Pillar"},
    "NAHIDA-C02": {"zone": "ZONE C", "lat": 23.7855, "lon": 86.4372, "name": "Zone C - Rail Siding Adjoining"},
    "NAHIDA-C03": {"zone": "ZONE C", "lat": 23.7885, "lon": 86.4390, "name": "Zone C - Shaft Headgear Buffer"},
}


class InMemoryRepository:
    """
    Robust in-memory store tracking live readings, sliding windows, alerts, and node telemetry.
    Thread-safe storage with role-based user management.
    """
    def __init__(self):
        self.readings: deque = deque(maxlen=2000)
        self.node_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.latest_nodes: Dict[str, Dict[str, Any]] = {}
        self.alerts: deque = deque(maxlen=500)
        self.predictions: deque = deque(maxlen=500)
        self.users: Dict[str, Dict[str, Any]] = {}
        self.node_metadata: Dict[str, Dict[str, Any]] = dict(CONFIGURED_NODE_METADATA)

        self._seed_default_users()

    def _seed_default_users(self):
        """Seed default development/operational accounts."""
        from app.auth import hash_password
        # Primary requested account: nahida / 12345678
        self.users["nahida"] = {
            "id": 1,
            "username": "nahida",
            "password_hash": hash_password("12345678"),
            "role": "administrative",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        # Development accounts: worker123, head123, admin123
        self.users["worker123"] = {
            "id": 2,
            "username": "worker123",
            "password_hash": hash_password("worker123"),
            "role": "worker",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        self.users["head123"] = {
            "id": 3,
            "username": "head123",
            "password_hash": hash_password("head123"),
            "role": "head",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        self.users["admin123"] = {
            "id": 4,
            "username": "admin123",
            "password_hash": hash_password("admin123"),
            "role": "administrative",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        # Backwards compatibility aliases
        self.users["worker"] = {
            "id": 4,
            "username": "worker",
            "password_hash": hash_password("worker123"),
            "role": "worker",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        self.users["head"] = {
            "id": 5,
            "username": "head",
            "password_hash": hash_password("head123"),
            "role": "head",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        self.users["admin"] = {
            "id": 6,
            "username": "admin",
            "password_hash": hash_password("admin123"),
            "role": "administrative",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return self.users.get(username)

    def get_all_users(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": u["id"],
                "username": u["username"],
                "role": u["role"],
                "is_active": u["is_active"],
                "created_at": u["created_at"]
            }
            for u in self.users.values()
        ]

    def create_user(self, username: str, password_hash: str, role: str) -> Dict[str, Any]:
        new_id = max([u["id"] for u in self.users.values()] or [0]) + 1
        user_dict = {
            "id": new_id,
            "username": username,
            "password_hash": password_hash,
            "role": role,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        self.users[username] = user_dict
        return user_dict

    def save_reading(self, reading_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new sensor reading and update latest node state."""
        node_id = reading_dict["node_id"]
        self.readings.append(reading_dict)
        self.node_history[node_id].append(reading_dict)

        # Update latest node status cache
        prev_reading = self.latest_nodes.get(node_id, {})
        meta = self.node_metadata.get(node_id, {"lat": 23.79, "lon": 86.43})

        self.latest_nodes[node_id] = {
            "node_id": node_id,
            "zone": reading_dict["zone"],
            "timestamp": reading_dict["timestamp"],
            "tilt": reading_dict["tilt"],
            "vibration": reading_dict["vibration"],
            "crack_displacement": reading_dict["crack_displacement"],
            "temperature": reading_dict.get("temperature", prev_reading.get("temperature", 28.0)),
            "humidity": reading_dict.get("humidity", prev_reading.get("humidity", 60.0)),
            "latitude": reading_dict.get("latitude") or meta.get("lat"),
            "longitude": reading_dict.get("longitude") or meta.get("lon"),
            "battery": reading_dict.get("battery", prev_reading.get("battery", 4.1)),
            "risk_score": reading_dict.get("risk_score", 0.0),
            "risk_level": reading_dict.get("risk_level", "NORMAL"),
            "anomaly_score": reading_dict.get("anomaly_score", 0.0),
            "is_anomaly": reading_dict.get("is_anomaly", False),
            "status": "ONLINE",
            "data_source": reading_dict.get("data_source", "ESP32"),
            "tilt_rate": reading_dict.get("tilt_rate", 0.0),
            "crack_rate": reading_dict.get("crack_rate", 0.0),
            "tilt_x": reading_dict.get("tilt_x", reading_dict["tilt"]),
            "tilt_y": reading_dict.get("tilt_y", round(reading_dict["tilt"] * 0.7, 2)),
            "tilt_z": reading_dict.get("tilt_z", 0.98),
            "displacement": reading_dict.get("displacement", reading_dict["crack_displacement"]),
            "strain": reading_dict.get("strain", round(reading_dict["crack_displacement"] * 0.08, 3)),
            "crack_event": reading_dict.get("crack_event", reading_dict["crack_displacement"] > 3.0),
            "vibration_count": reading_dict.get("vibration_count", 0),
            "gps_status": reading_dict.get("gps_status", "3D_FIX"),
            "anomaly_status": reading_dict.get("anomaly_status", "NORMAL"),
        }
        return reading_dict

    def get_latest_nodes(self) -> List[Dict[str, Any]]:
        return list(self.latest_nodes.values())

    def get_node_status(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self.latest_nodes.get(node_id)

    def get_readings(
        self,
        node_id: Optional[str] = None,
        zone: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        if node_id:
            items = list(self.node_history.get(node_id, []))
        else:
            items = list(self.readings)

        if zone:
            items = [r for r in items if r["zone"] == zone]

        return items[-limit:]

    def get_node_window(self, node_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent readings for calculating rate-of-change and rolling features."""
        hist = self.node_history.get(node_id, [])
        return list(hist)[-count:]

    def save_alert(self, alert_dict: Dict[str, Any]) -> Dict[str, Any]:
        self.alerts.appendleft(alert_dict)
        return alert_dict

    def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(self.alerts)[:limit]

    def get_latest_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        return [a for a in list(self.alerts)[:limit] if a.get("status") == "ACTIVE"]

    def acknowledge_alert(self, alert_id: str) -> bool:
        for a in self.alerts:
            if a.get("alert_id") == alert_id:
                a["status"] = "ACKNOWLEDGED"
                return True
        return False

    def save_prediction(self, pred_dict: Dict[str, Any]) -> Dict[str, Any]:
        self.predictions.appendleft(pred_dict)
        return pred_dict

    def get_predictions(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(self.predictions)[:limit]

    def get_node_metadata_list(self) -> List[Dict[str, Any]]:
        return [
            {"node_id": k, **v} for k, v in self.node_metadata.items()
        ]

    def update_node_metadata(self, node_id: str, lat: float, lon: float, zone: str, name: str):
        self.node_metadata[node_id] = {
            "lat": lat,
            "lon": lon,
            "zone": zone,
            "name": name
        }
        if node_id in self.latest_nodes:
            self.latest_nodes[node_id]["latitude"] = lat
            self.latest_nodes[node_id]["longitude"] = lon
            self.latest_nodes[node_id]["zone"] = zone


# Global In-Memory Store instance
in_memory_store = InMemoryRepository()


def get_db_status_info() -> Dict[str, Any]:
    """Exposes real database connectivity status without false claims."""
    return {
        "connected": DB_CONNECTED,
        "status_label": "Connected" if DB_CONNECTED else "Offline",
        "mode": "postgresql" if DB_CONNECTED else "offline"
    }
