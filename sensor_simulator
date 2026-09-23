"""
NAHIDA Multi-Node Sensor Telemetry Simulator
Simulates 9 IoT sensor nodes across Zones A, B, and C with realistic random-walk behavior.
Zone B Node NAHIDA-B02 demonstrates an active HIGH RISK subsidence event.

All telemetry packets are sent to:
POST /api/sensors/data
using the identical schema and payload format as real ESP32 field units.

DISCLAIMER: DEMO / SIMULATED DATA ONLY — NOT REAL MINE SENSOR MEASUREMENTS.
"""

import time
import math
import random
import logging
from datetime import datetime
import urllib.request
import urllib.error
import json
import os
import sys

# Ensure backend root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.abspath(os.path.join(current_dir, ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.services.mock_generator import MOCK_NODE_SPECS, MockNodeState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SIMULATOR] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("nahida.simulator")

BACKEND_URL = os.getenv("BACKEND_INGEST_URL", "http://localhost:8000/api/sensors/data")
SEND_INTERVAL_SECONDS = float(os.getenv("MOCK_INTERVAL_SECONDS", "3.0"))


def post_reading(payload: dict) -> bool:
    # Convert datetime to isoformat if needed
    if isinstance(payload.get("timestamp"), datetime):
        payload["timestamp"] = payload["timestamp"].isoformat()

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BACKEND_URL,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "NAHIDA-Simulator/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            return resp.status == 200
    except Exception as e:
        logger.warning(f"Failed to post reading for {payload['node_id']}: {e}")
        return False


def run_simulator(duration_seconds: float = None):
    print("=" * 65)
    print("NAHIDA SENSOR TELEMETRY SIMULATOR")
    print(f"Target Endpoint: {BACKEND_URL}")
    print("Nodes: 9 (Zones A, B, C) | Interval: 3s")
    print("Active Alert Node: NAHIDA-B02 (HIGH RISK — 82/100, vib ~0.72g, crack ~4.8mm)")
    print("Labels: DEMO / SIMULATED DATA ONLY")
    print("=" * 65)

    node_states = [MockNodeState(spec) for spec in MOCK_NODE_SPECS]

    start_time = time.time()
    cycle = 0

    while True:
        elapsed = time.time() - start_time
        if duration_seconds and elapsed >= duration_seconds:
            logger.info("Simulation completed allotted duration.")
            break

        cycle += 1
        logger.info(f"--- Telemetry Cycle #{cycle} (Elapsed: {elapsed:.1f}s) ---")

        for node in node_states:
            node.step()
            payload = node.build_payload()
            success = post_reading(payload)

            if node.node_id == "NAHIDA-B02":
                logger.info(
                    f"  [{node.node_id}] {node.category} ALERT | "
                    f"Risk: {payload['risk_score']} | Vib: {payload['vibration']:.3f}g | "
                    f"Crack: {payload['crack_displacement']:.2f}mm | Anomaly: {payload['anomaly_score']:.3f}"
                )

        time.sleep(SEND_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_simulator()
