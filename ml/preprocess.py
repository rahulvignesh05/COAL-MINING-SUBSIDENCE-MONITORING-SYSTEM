"""
NAHIDA ML Preprocessing & Feature Engineering
SIH Problem ID: SIH26025

Prepares feature vectors for Isolation Forest anomaly detection.
Features include instantaneous telemetry, kinematic rates (velocity/acceleration),
and temporal rolling statistics.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any


FEATURE_COLUMNS = [
    "tilt",
    "vibration",
    "crack_displacement",
    "tilt_rate",
    "crack_rate",
    "crack_acceleration",
    "rolling_tilt_mean",
    "rolling_tilt_std",
    "rolling_vibration_mean",
    "rolling_vibration_std",
    "rolling_crack_mean",
    "rolling_crack_std",
]


def extract_features_from_window(recent_readings: List[Dict[str, Any]], current_reading: Dict[str, Any]) -> Dict[str, float]:
    """
    Computes all 12 ML feature metrics from a sliding window of historical readings
    for a single node.
    """
    tilt = float(current_reading.get("tilt", 0.0))
    vibration = float(current_reading.get("vibration", 0.0))
    crack = float(current_reading.get("crack_displacement", 0.0))

    if not recent_readings:
        return {
            "tilt": tilt,
            "vibration": vibration,
            "crack_displacement": crack,
            "tilt_rate": 0.0,
            "crack_rate": 0.0,
            "crack_acceleration": 0.0,
            "rolling_tilt_mean": tilt,
            "rolling_tilt_std": 0.0,
            "rolling_vibration_mean": vibration,
            "rolling_vibration_std": 0.0,
            "rolling_crack_mean": crack,
            "rolling_crack_std": 0.0,
        }

    # Extract sequences
    all_readings = recent_readings + [current_reading]
    tilts = np.array([r.get("tilt", 0.0) for r in all_readings], dtype=float)
    vibs = np.array([r.get("vibration", 0.0) for r in all_readings], dtype=float)
    cracks = np.array([r.get("crack_displacement", 0.0) for r in all_readings], dtype=float)

    # Rates of change (using previous step difference)
    if len(all_readings) >= 2:
        tilt_rate = float(tilts[-1] - tilts[-2])
        crack_rate = float(cracks[-1] - cracks[-2])
    else:
        tilt_rate = 0.0
        crack_rate = 0.0

    # Acceleration (second derivative)
    if len(all_readings) >= 3:
        prev_crack_rate = float(cracks[-2] - cracks[-3])
        crack_acceleration = float(crack_rate - prev_crack_rate)
    else:
        crack_acceleration = 0.0

    return {
        "tilt": tilt,
        "vibration": vibration,
        "crack_displacement": crack,
        "tilt_rate": tilt_rate,
        "crack_rate": crack_rate,
        "crack_acceleration": crack_acceleration,
        "rolling_tilt_mean": float(np.mean(tilts)),
        "rolling_tilt_std": float(np.std(tilts)) if len(tilts) > 1 else 0.0,
        "rolling_vibration_mean": float(np.mean(vibs)),
        "rolling_vibration_std": float(np.std(vibs)) if len(vibs) > 1 else 0.0,
        "rolling_crack_mean": float(np.mean(cracks)),
        "rolling_crack_std": float(np.std(cracks)) if len(cracks) > 1 else 0.0,
    }


def generate_synthetic_normal_dataset(n_samples: int = 3000, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates realistic, physically plausible baseline geomechanical readings under
    stable mine conditions (thermal diurnal cycles, benign ground vibrations, stable fractures).
    """
    np.random.seed(random_seed)

    # Baseline steady states
    base_tilt = 1.4 + 0.3 * np.sin(np.linspace(0, 8 * np.pi, n_samples))
    tilt_noise = np.random.normal(0, 0.08, n_samples)
    tilt = np.clip(base_tilt + tilt_noise, 0.5, 3.0)

    # Benign mine micro-tremors and haulage vibrations
    vibration = np.clip(np.random.exponential(scale=0.04, size=n_samples) + np.random.normal(0, 0.01, n_samples), 0.01, 0.15)

    # Stable crack displacement
    base_crack = 0.5 + 0.05 * np.sin(np.linspace(0, 4 * np.pi, n_samples))
    crack_noise = np.random.normal(0, 0.03, n_samples)
    crack = np.clip(base_crack + crack_noise, 0.2, 1.2)

    df = pd.DataFrame({
        "tilt": tilt,
        "vibration": vibration,
        "crack_displacement": crack
    })

    # Rolling & Rate features
    df["tilt_rate"] = df["tilt"].diff().fillna(0.0)
    df["crack_rate"] = df["crack_displacement"].diff().fillna(0.0)
    df["crack_acceleration"] = df["crack_rate"].diff().fillna(0.0)

    df["rolling_tilt_mean"] = df["tilt"].rolling(window=10, min_periods=1).mean()
    df["rolling_tilt_std"] = df["tilt"].rolling(window=10, min_periods=1).std().fillna(0.0)

    df["rolling_vibration_mean"] = df["vibration"].rolling(window=10, min_periods=1).mean()
    df["rolling_vibration_std"] = df["vibration"].rolling(window=10, min_periods=1).std().fillna(0.0)

    df["rolling_crack_mean"] = df["crack_displacement"].rolling(window=10, min_periods=1).mean()
    df["rolling_crack_std"] = df["crack_displacement"].rolling(window=10, min_periods=1).std().fillna(0.0)

    return df[FEATURE_COLUMNS]
