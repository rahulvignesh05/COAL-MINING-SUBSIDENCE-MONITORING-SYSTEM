"""
Smart Mine Subsidence Sentinel — Dashboard Backend Bridge
Routes all traffic, REST endpoints, and WebSocket streaming to the Central AI Backend (ai.backend.main).
Maintains 100% backward compatibility with existing launch scripts and test runners.
"""

import sys
import os
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import centralized FastAPI application and services
from ai.backend.main import (
    app,
    broadcaster,
    manager,
    ingest_sensor_data,
    ingest_satellite_data,
    get_dashboard_summary,
    list_sensors,
    get_risk_status,
)

__all__ = [
    "app",
    "broadcaster",
    "manager",
]

if __name__ == "__main__":
    import uvicorn
    from ai.backend.config import settings
    uvicorn.run(
        "dashboard.BACKEND.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
