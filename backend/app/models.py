from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, String, Boolean, DateTime, Text
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(50), unique=True, index=True, nullable=False)
    zone = Column(String(50), index=True, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(20), default="ONLINE")
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    polygon_geojson = Column(Text, nullable=True)
    risk_level = Column(String(20), default="NORMAL")
    risk_score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(50), index=True, nullable=False)
    zone = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    tilt = Column(Float, nullable=False)
    vibration = Column(Float, nullable=False)
    crack_displacement = Column(Float, nullable=False)

    # Optional hardware telemetry
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    acceleration_x = Column(Float, nullable=True)
    acceleration_y = Column(Float, nullable=True)
    acceleration_z = Column(Float, nullable=True)
    vibration_zone_1 = Column(Float, nullable=True)
    vibration_zone_2 = Column(Float, nullable=True)
    vibration_zone_3 = Column(Float, nullable=True)
    battery = Column(Float, nullable=True)
    gps_fix = Column(Boolean, nullable=True)
    imu_status = Column(String(50), nullable=True)
    rtc_status = Column(String(50), nullable=True)
    sd_status = Column(String(50), nullable=True)
    data_source = Column(String(50), default="SIMULATED")

    # Evaluated risk and ML metrics
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="NORMAL")
    anomaly_score = Column(Float, default=0.0)
    is_anomaly = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(64), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    node_id = Column(String(50), index=True, nullable=False)
    zone = Column(String(50), index=True, nullable=False)
    severity = Column(String(20), index=True, nullable=False)  # WATCH, HIGH, CRITICAL
    risk_score = Column(Float, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    factors_json = Column(Text, nullable=True)
    message = Column(String(255), nullable=False)
    recommended_action = Column(String(255), nullable=False)
    status = Column(String(20), default="ACTIVE")  # ACTIVE, ACKNOWLEDGED, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True, nullable=False)
    node_id = Column(String(50), index=True, nullable=False)
    zone = Column(String(50), index=True, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    is_anomaly = Column(Boolean, default=False)
    model_status = Column(String(50), default="ready")
    features_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # worker, head, administrative
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

