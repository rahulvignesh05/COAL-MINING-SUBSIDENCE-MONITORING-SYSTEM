"""
NAHIDA ML Training Script
SIH Problem ID: SIH26025

Trains an Isolation Forest anomaly detector on synthetic baseline mine telemetry.
IMPORTANT:
This model is an unsupervised anomaly detector calibrated on synthetic normal
operational patterns. It does NOT claim certified mine-collapse prediction.
"""

import os
from pathlib import Path
import joblib
from sklearn.ensemble import IsolationForest
from preprocess import generate_synthetic_normal_dataset, FEATURE_COLUMNS

BASE_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"

DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def train():
    print("=" * 60)
    print("NAHIDA ML Anomaly Detection Training (Isolation Forest)")
    print("=" * 60)

    print("[1/4] Generating synthetic normal mine geomechanical baseline data...")
    df = generate_synthetic_normal_dataset(n_samples=4000, random_seed=42)

    raw_csv_path = DATA_RAW_DIR / "baseline_mine_telemetry.csv"
    processed_csv_path = DATA_PROCESSED_DIR / "features_dataset.csv"

    df.to_csv(raw_csv_path, index=False)
    df.to_csv(processed_csv_path, index=False)
    print(f"      Saved {len(df)} samples to {processed_csv_path}")

    print("[2/4] Initializing IsolationForest (n_estimators=120, contamination=0.03)...")
    model = IsolationForest(
        n_estimators=120,
        contamination=0.03,
        random_state=42,
        n_jobs=-1
    )

    print("[3/4] Fitting model on normal behavior envelope...")
    model.fit(df[FEATURE_COLUMNS])

    # Test baseline predictions
    predictions = model.predict(df[FEATURE_COLUMNS])
    anomaly_ratio = (predictions == -1).mean()
    print(f"      Contamination achieved: {anomaly_ratio * 100:.2f}% (Expected ~3%)")

    model_path = MODELS_DIR / "isolation_forest.joblib"
    print(f"[4/4] Serializing model bundle to {model_path}...")

    bundle = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "algorithm": "IsolationForest",
        "contamination": 0.03,
        "n_samples_trained": len(df),
        "disclaimer": "AI Anomaly Detection Prototype — Trained on synthetic normal mine baselines.",
    }
    joblib.dump(bundle, model_path)

    print("=" * 60)
    print("SUCCESS: Isolation Forest trained and saved successfully.")
    print("=" * 60)


if __name__ == "__main__":
    train()
