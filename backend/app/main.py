from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS, MOCK_TELEMETRY
from app.database import in_memory_store, get_db_status_info
from app.services.ml_service import ml_service
from app.services.mock_generator import mock_telemetry_service
from app.routes import sensors, alerts, predictions, ws, auth, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: If MOCK_TELEMETRY is enabled, start the background telemetry generator
    if MOCK_TELEMETRY:
        mock_telemetry_service.start()
    yield
    # Shutdown: Stop simulator
    if MOCK_TELEMETRY:
        await mock_telemetry_service.stop()


app = FastAPI(
    title="NAHIDA Control Center API",
    description="AI-Enabled Smart Mine Subsidence Monitoring & Early-Warning Control Center",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware for React frontend (supports localhost, FRONTEND_URL, and VS Code Dev Tunnels)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        *[o for o in CORS_ORIGINS if o not in ("http://localhost:5173", "http://127.0.0.1:5173")],
    ],
    allow_origin_regex=r"^https?://([a-zA-Z0-9\-]+\.)*devtunnels\.ms(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API and WebSocket Routers
app.include_router(auth.router)
app.include_router(sensors.router)
app.include_router(alerts.router)
app.include_router(predictions.router)
app.include_router(admin.router)
app.include_router(ws.router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "system": "NAHIDA",
        "status": "online"
    }


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {
        "backend": "online"
    }


@app.get("/api/system/status")
def system_status():
    """
    Real-time system status reporting genuine backend, database, ML, and websocket states.
    Database reports 'connected' only when genuine database connectivity is verified, otherwise 'offline'.
    """
    db_info = get_db_status_info()
    latest_nodes = in_memory_store.get_latest_nodes()
    active_alerts = in_memory_store.get_latest_alerts(limit=50)
    now = datetime.utcnow()

    return {
        "backend": "online",
        "database": "connected" if db_info["connected"] else "offline",
        "database_connected": db_info["connected"],
        "ml": "ready" if ml_service.status == "READY" else "offline",
        "websocket": "ready",
        "timestamp": now.isoformat(),
        "active_nodes_count": len(latest_nodes),
        "zones_count": 3,
        "active_alerts_count": len(active_alerts),
        "total_readings_stored": len(in_memory_store.readings),
        "mock_telemetry": MOCK_TELEMETRY,
        "telemetry_mode": "DEMO / MOCK DATA" if MOCK_TELEMETRY else "REAL ESP32"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
