"""
NAHIDA Standalone ML Inference & Validation Script
SIH Problem ID: SIH26025
"""

import sys
from pathlib import Path
import joblib
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "isolation_forest.joblib"


def run_prediction(feature_dict: dict):
    if not MODEL_PATH.exists():
        print(f"Error: Model not found at {MODEL_PATH}. Run python ml/train.py first.")
        return None

    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    # Construct input vector in exact column order
    vector = [feature_dict.get(col, 0.0) for col in feature_columns]
    X = np.array([vector], dtype=float)

    # In Scikit-Learn IsolationForest:
    # decision_function yields: positive for inliers, negative for outliers.
    # Lower score = more anomalous.
    raw_score = float(model.decision_function(X)[0])
    raw_prediction = int(model.predict(X)[0])  # 1 = normal, -1 = anomaly

    # Normalize into 0.0 (perfectly normal) to 1.0 (extreme anomaly)
    # Typically raw_score spans from approx -0.35 to +0.25
    anomaly_score = round(float(np.clip(0.5 - (raw_score * 2.5), 0.0, 1.0)), 3)
    is_anomaly = raw_prediction == -1 or anomaly_score >= 0.55

    return {
        "anomaly_score": anomaly_score,
        "is_anomaly": is_anomaly,
        "raw_decision_score": round(raw_score, 4),
        "model_status": "ready"
    }


if __name__ == "__main__":
    print("Testing ML Inference...")
    # Test Normal Case
    normal_case = {
        "tilt": 1.5,
        "vibration": 0.05,
        "crack_displacement": 0.5,
        "tilt_rate": 0.01,
        "crack_rate": 0.005,
        "crack_acceleration": 0.0,
        "rolling_tilt_mean": 1.48,
        "rolling_tilt_std": 0.02,
        "rolling_vibration_mean": 0.05,
        "rolling_vibration_std": 0.01,
        "rolling_crack_mean": 0.5,
        "rolling_crack_std": 0.01,
    }
    res_normal = run_prediction(normal_case)
    print(f"Normal Case Inference: {res_normal}")

    # Test Anomaly Case (High tilt + crack acceleration + vibration)
    anom_case = {
        "tilt": 8.5,
        "vibration": 1.2,
        "crack_displacement": 8.0,
        "tilt_rate": 0.45,
        "crack_rate": 0.40,
        "crack_acceleration": 0.15,
        "rolling_tilt_mean": 7.2,
        "rolling_tilt_std": 1.1,
        "rolling_vibration_mean": 0.95,
        "rolling_vibration_std": 0.25,
        "rolling_crack_mean": 6.8,
        "rolling_crack_std": 1.0,
    }
    res_anom = run_prediction(anom_case)
    print(f"Anomaly Case Inference: {res_anom}")
