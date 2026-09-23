# NAHIDA — AI-Enabled Smart Mine Subsidence Monitoring & Early-Warning Control Center
**Repository Location: `Y:\NAHIDA`**

---

## 1. Project Overview

**NAHIDA** is an intelligent geotechnical monitoring and early-warning control center designed for open-cast and underground mine subsidence zones. It bridges rugged edge sensor nodes (ESP32) with a high-throughput FastAPI ingestion engine, a multi-factor geomechanical risk scoring pipeline, an Isolation Forest anomaly detection model, real-time WebSocket pub/sub streams, and an industrial control-room React dashboard with role-based access control.

---

## 2. System Architecture

```
                 ┌────────────────────────────────┐
                 │       ESP32 EDGE NODES         │
                 │  - MPU6500 IMU (Tilt)          │
                 │  - SW-420 ×3 (Ground Vib)      │
                 │  - LVDT / Pot (Crack Gauge)    │
                 │  - DHT11 (Temp & Humidity)     │
                 │  - NEO-6M GNSS & DS3231 RTC    │
                 │  - MicroSD (Offline Blackbox)  │
                 └───────────────┬────────────────┘
                                 │
                   HTTP POST /api/sensors/data
                                 │
                                 ▼
                 ┌────────────────────────────────┐
                 │        FASTAPI BACKEND         │
                 │  - Role-Based Auth (JWT)       │
                 │  - Schema Validation (Pydantic)│
                 │  - Kinematic Rate Extraction   │
                 │  - Multi-Factor Risk Engine    │
                 │  - Isolation Forest ML Service │
                 │  - Alert Generation & Cooldown │
                 │  - WebSocket ConnectionManager │
                 └───────────────┬────────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             ▼                   ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │  DATA STORAGE   │ │   ML ENGINE     │ │ WEBSOCKET /ws   │
    │  PostgreSQL /   │ │ Isolation Forest│ │ Real-time JSON  │
    │  TimescaleDB    │ │ Outlier Scoring │ │ Event Stream    │
    │  (Standby Fall- │ │ (0.00 to 1.00)  │ │                 │
    │   back Storage) │ └─────────────────┘ └────────┬────────┘
    └─────────────────┘                              │
                                                     ▼
                                     ┌────────────────────────────────┐
                                     │     REACT VITE DASHBOARD       │
                                     │  - Worker / Head / Admin Views │
                                     │  - Top KPI Metrics Cards       │
                                     │  - Interactive Leaflet Risk Map│
                                     │  - Live Recharts (Tilt, Vib)   │
                                     │  - Early Warning Dispatch      │
                                     │  - AI Anomaly Monitor Gauge    │
                                     │  - 9-Node Telemetry Matrix     │
                                     │  - Real-Time Alert Stream      │
                                     └────────────────────────────────┘
```

---

## 3. Role-Based Access Control

The platform features three distinct operational access levels:

| Role | Operational Scope | Authorized Actions |
|---|---|---|
| **WORKER** | Field Monitoring | View real-time dashboard, interactive risk map, zone status, and live sensor matrix. |
| **HEAD** | Operations Management | Comprehensive monitoring, trend analytics, and **alert acknowledgement**. |
| **ADMINISTRATIVE** | System Administration | User account creation/management, sensor node placement calibration, and safety threshold tuning. |

### Default Development Accounts:
- **Worker:** `worker` / `worker123` (Role: `worker`)
- **Head:** `head` / `head123` (Role: `head`)
- **Administrative:** `admin` / `admin123` (Role: `administrative`)

---

## 4. Multi-Factor Risk Assessment Engine

The risk engine computes a continuous composite score from **0 to 100** by evaluating instantaneous displacement, deformation velocity/acceleration, and AI outlier confidence:

$$\text{Risk Score} = w_1 \cdot \text{Tilt}_{\text{norm}} + w_2 \cdot \text{Vib}_{\text{norm}} + w_3 \cdot \text{Crack}_{\text{norm}} + w_4 \cdot \text{Rate}_{\text{norm}} + w_5 \cdot \text{ML}_{\text{norm}}$$

| Component | Default Weight | Normalization Ceiling | Physical Role |
|---|---|---|---|
| **Tilt Inclination** | 0.25 | 10.0° | Detects highwall, bench, or escarpment angular rotation |
| **Ground Vibration** | 0.20 | 1.5 g | Detects blasting shocks, overburden shifts, or rock burst |
| **Crack Opening** | 0.25 | 10.0 mm | Detects tension fracture expansion |
| **Deformation Rate** | 0.15 | 0.5 mm/s / 0.5°/s | Evaluates kinematic velocity and acceleration |
| **AI Anomaly Score** | 0.15 | 1.0 (Outlier Index) | Unsupervised isolation of anomalous operational vectors |

### Threat Levels:
- **NORMAL (0 – 29):** Stable geotechnical baseline. Routine monitoring active.
- **WATCH (30 – 59):** Advisory alert. Increase telemetry observation cadence.
- **HIGH (60 – 79):** Significant acceleration. Inspect affected zone, restrict heavy vehicle haulage.
- **CRITICAL (80 – 100):** Imminent failure hazard. Immediate site evacuation and geotechnical inspection per safety protocol.

---

## 5. Machine Learning Pipeline (Isolation Forest)

The ML pipeline extracts a 12-dimensional feature vector from a sliding time window:
`tilt`, `vibration`, `crack_displacement`, `tilt_rate`, `crack_rate`, `crack_acceleration`, `rolling_tilt_mean/std`, `rolling_vibration_mean/std`, `rolling_crack_mean/std`.

### Retraining the Model:
```powershell
cd Y:\NAHIDA\backend
.\venv\Scripts\python.exe ..\ml\train.py
```

### Validating Inference:
```powershell
.\venv\Scripts\python.exe ..\ml\predict.py
```

---

## 6. How to Run the Complete System

Follow these three steps to run the complete system locally:

### Step 1: Start the FastAPI Backend
```powershell
cd Y:\NAHIDA\backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
- Open Swagger Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Verify Status Endpoint: [http://localhost:8000/api/system/status](http://localhost:8000/api/system/status)

### Step 2: Start the React Dashboard
```powershell
cd Y:\NAHIDA\frontend
npm run dev
```
- Open Control Center: [http://localhost:5173/](http://localhost:5173/)
- The application opens directly on the **NAHIDA Login** screen.

### Step 3: Start the 9-Node Telemetry Transmitter
```powershell
cd Y:\NAHIDA\backend
.\venv\Scripts\python.exe .\simulator\sensor_simulator.py
```

---

## 7. Operational Demonstration Procedure

1. **Access Login Screen:** Navigate to `http://localhost:5173/`.
2. **Login as Worker:** Select **WORKER**, enter `worker` / `worker123`, click Access Control Center. The dashboard displays real-time telemetry, map, and charts.
3. **Login as Head:** Logout, select **HEAD**, enter `head` / `head123`. Observe active alerts and acknowledge any triggered incident.
4. **Login as Admin:** Logout, select **ADMINISTRATIVE**, enter `admin` / `admin123`. Click the **Administration** button in the header to manage accounts, node coordinates, and risk weights.

---

## 8. ESP32 Hardware Integration Spec

Real ESP32 field units transmit data directly to `POST /api/sensors/data` using HTTP POST. A complete Arduino sketch is provided at:
[`docs/esp32_firmware_sample.ino`](file:///Y:/NAHIDA/docs/esp32_firmware_sample.ino)

---

## 9. Automated Test Commands

To verify all system endpoints programmatically:

```powershell
# Root & Health Endpoints
Invoke-RestMethod -Uri "http://127.0.0.1:8000/"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health"

# Authentication Login (Worker)
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"worker","password":"worker123","role":"worker"}'

# System Status
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/system/status"

# Ingest Telemetry Packet
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/sensors/data" -Method POST -ContentType "application/json" -Body '{"node_id":"NAHIDA-A01","zone":"ZONE A","tilt":1.5,"vibration":0.05,"crack_displacement":0.5,"data_source":"ESP32"}'

# Query Active Alerts
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/alerts"
```
