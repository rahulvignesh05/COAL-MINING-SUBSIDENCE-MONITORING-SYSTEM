from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SensorDataCreate(BaseModel):
    """
    Sensor data ingestion schema.
    Compatible with both real ESP32 edge nodes and the sensor simulator.
    """
    node_id: str = Field(..., description="Unique sensor node identifier (e.g. NAHIDA-A01)")
    zone: str = Field(..., description="Monitored mine zone (e.g. ZONE A)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Reading timestamp in ISO format")
    tilt: float = Field(..., description="Tilt inclination angle in degrees")
    vibration: float = Field(..., description="Ground vibration peak amplitude in g or mm/s")
    crack_displacement: float = Field(..., description="Crack displacement opening in mm")

    # Extended hardware telemetry fields
    temperature: Optional[float] = Field(None, description="Ambient temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Relative humidity percentage")
    latitude: Optional[float] = Field(None, description="GNSS latitude coordinate")
    longitude: Optional[float] = Field(None, description="GNSS longitude coordinate")
    acceleration_x: Optional[float] = Field(None, description="MPU6500 X-axis acceleration")
    acceleration_y: Optional[float] = Field(None, description="MPU6500 Y-axis acceleration")
    acceleration_z: Optional[float] = Field(None, description="MPU6500 Z-axis acceleration")
    vibration_zone_1: Optional[float] = Field(None, description="SW-420 Sensor 1 vibration level")
    vibration_zone_2: Optional[float] = Field(None, description="SW-420 Sensor 2 vibration level")
    vibration_zone_3: Optional[float] = Field(None, description="SW-420 Sensor 3 vibration level")
    battery: Optional[float] = Field(None, description="Battery voltage level (V)")
    gps_fix: Optional[bool] = Field(None, description="NEO-6M GNSS fix status")
    imu_status: Optional[str] = Field(None, description="MPU6500 IMU operational status")
    rtc_status: Optional[str] = Field(None, description="DS3231 RTC sync status")
    sd_status: Optional[str] = Field(None, description="MicroSD offline logging status")
    data_source: str = Field(default="SIMULATED", description="Data origin: SIMULATED or ESP32")

    # Additional standardized mine telemetry fields
    tilt_x: Optional[float] = Field(None, description="X-axis tilt angle (deg)")
    tilt_y: Optional[float] = Field(None, description="Y-axis tilt angle (deg)")
    tilt_z: Optional[float] = Field(None, description="Z-axis tilt angle (deg)")
    tilt_rate: Optional[float] = Field(0.0, description="Tilt rate of change")
    displacement: Optional[float] = Field(None, description="Total displacement magnitude (mm)")
    strain: Optional[float] = Field(None, description="Geotechnical strain measurement")
    crack_event: Optional[bool] = Field(None, description="Binary crack event detection flag")
    vibration_count: Optional[int] = Field(None, description="Vibration trigger threshold count")
    gps_status: Optional[str] = Field(None, description="GNSS lock status")
    anomaly_status: Optional[str] = Field(None, description="Anomaly state label (NORMAL / ANOMALY)")
    anomaly_score: Optional[float] = Field(None, description="Precomputed or simulated anomaly score")
    is_anomaly: Optional[bool] = Field(None, description="Binary anomaly flag")
    risk_score: Optional[float] = Field(None, description="Calibrated risk score override")
    risk_level: Optional[str] = Field(None, description="Calibrated risk level override")


class SensorReadingResponse(SensorDataCreate):
    id: Optional[int] = None
    risk_score: float
    risk_level: str
    anomaly_score: float
    is_anomaly: bool


class LatestNodeStatusResponse(BaseModel):
    node_id: str
    zone: str
    timestamp: datetime
    tilt: float
    vibration: float
    crack_displacement: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    battery: Optional[float] = None
    risk_score: float
    risk_level: str  # NORMAL, WATCH, HIGH, CRITICAL
    anomaly_score: float
    is_anomaly: bool
    status: str  # ONLINE, DEGRADED, OFFLINE
    data_source: str
    tilt_rate: float = 0.0
    crack_rate: float = 0.0
    tilt_x: Optional[float] = None
    tilt_y: Optional[float] = None
    tilt_z: Optional[float] = None
    displacement: Optional[float] = None
    strain: Optional[float] = None
    crack_event: Optional[bool] = None
    vibration_count: Optional[int] = None
    gps_status: Optional[str] = None
    anomaly_status: Optional[str] = None


class IngestionResultResponse(BaseModel):
    success: bool
    node_id: str
    zone: str
    risk_score: float
    risk_level: str
    anomaly_score: float
    is_anomaly: bool
    alert_generated: bool
    timestamp: datetime
    message: str


class AlertCreate(BaseModel):
    node_id: str
    zone: str
    severity: str  # WATCH, HIGH, CRITICAL
    risk_score: float
    anomaly_score: float
    factors: Dict[str, float]
    message: str
    recommended_action: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AlertResponse(AlertCreate):
    alert_id: str
    status: str = "ACTIVE"  # ACTIVE, ACKNOWLEDGED, RESOLVED


class PredictionResponse(BaseModel):
    node_id: str
    zone: str
    timestamp: datetime
    anomaly_score: float
    is_anomaly: bool
    model_status: str
    features: Dict[str, float]


class SystemStatusResponse(BaseModel):
    backend: str
    database: str
    ml: str
    simulator: str
    websocket: str
    timestamp: datetime
    active_nodes_count: int
    zones_count: int
    active_alerts_count: int
    total_readings_stored: int
