"""
RAVEN API Server
----------------
Thin FastAPI adapter that wraps the existing RAVEN simulation + AI pipeline.
Does NOT rewrite any backend logic - only exposes it over HTTP/SSE.
"""
import sys
import os
import json
import time
import asyncio
import threading
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# --- RAVEN imports ---
from simulation.engine import SyntheticTelemetryEngine
from ai.features import FeatureExtractor
from ai.models.isolation_forest import IsolationForestModel
from ai.models.xgboost_classifier import XGBoostFaultClassifier
from ai.models.cnn_1d import TemporalCNNModel
from agents.contracts import ModelOutputs, TelemetryMetadata
from agents.fusion_agent import FusionAgent
from agents.decision_agent import DecisionAgent
from agents.recovery_agent import RecoveryAgent
from agents.verification_agent import VerificationAgent
from agents.message_bus import fusion_to_decision, decision_to_recovery, recovery_to_verification
from config.paths import MODELS_DIR, SYNTHETIC_DATA_DIR

# -------------------------------------------------------
# Global state (thread-safe via lock)
# -------------------------------------------------------
_lock = threading.Lock()
_state: Dict[str, Any] = {
    "scenario": "NORMAL",
    "running": False,
    "start_time": time.time(),
    "tick": 0,
    "telemetry_history": [],   # last N frames
    "latest_result": None,
    "event_log": [],
}
MAX_HISTORY = 100
MAX_EVENTS = 200

# -------------------------------------------------------
# Load models once at startup
# -------------------------------------------------------
iso_model: Optional[IsolationForestModel] = None
xgb_model: Optional[XGBoostFaultClassifier] = None
cnn_model: Optional[TemporalCNNModel] = None
feature_extractor: Optional[FeatureExtractor] = None
fusion_agent: Optional[FusionAgent] = None
decision_agent: Optional[DecisionAgent] = None
recovery_agent: Optional[RecoveryAgent] = None
verification_agent: Optional[VerificationAgent] = None
models_loaded = False
models_error: Optional[str] = None

def load_models():
    global iso_model, xgb_model, cnn_model, feature_extractor
    global fusion_agent, decision_agent, recovery_agent, verification_agent
    global models_loaded, models_error
    try:
        iso_model = IsolationForestModel(model_path=str(MODELS_DIR))
        xgb_model = XGBoostFaultClassifier(model_path=str(MODELS_DIR))
        cnn_model = TemporalCNNModel(model_path=str(MODELS_DIR))
        feature_extractor = FeatureExtractor(fps=50)
        fusion_agent = FusionAgent()
        decision_agent = DecisionAgent()
        recovery_agent = RecoveryAgent()
        verification_agent = VerificationAgent()
        models_loaded = True
    except Exception as e:
        models_error = str(e)
        models_loaded = False

# -------------------------------------------------------
# Background simulation loop
# -------------------------------------------------------
_sim_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()

VALID_SCENARIOS = [
    "NORMAL", "OVERHEATING", "IMPACT_LIKE_EVENT", "HIGH_VIBRATION",
    "OBSTACLE_APPROACH", "SENSOR_STUCK", "SENSOR_DROPOUT", "MULTI_SENSOR_ANOMALY"
]

def _push_event(level: str, message: str, agent: str, fault: str = ""):
    with _lock:
        _state["event_log"].append({
            "id": _state["tick"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "agent": agent,
            "fault": fault,
        })
        if len(_state["event_log"]) > MAX_EVENTS:
            _state["event_log"] = _state["event_log"][-MAX_EVENTS:]

def _simulation_tick(scenario: str, seed: int, noise_level: float = 1.0):
    """Run one full RAVEN pipeline tick for given scenario."""
    if not models_loaded:
        return None

    engine = SyntheticTelemetryEngine(fps=50, duration=2.56, seed=seed, noise_level=noise_level)
    df = engine.generate(scenario, fault_start=0.0, fault_end=1.0)
    df_window = df.iloc[:128]

    # Extract raw telemetry snapshot (last sample)
    last = df_window.iloc[-1]
    telemetry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario": scenario,
        "dht_temp": None if np.isnan(last["dht_temp"]) else round(float(last["dht_temp"]), 2),
        "dht_hum": None if np.isnan(last["dht_hum"]) else round(float(last["dht_hum"]), 2),
        "mpu_acc_x": round(float(last["mpu_acc_x"]), 4),
        "mpu_acc_y": round(float(last["mpu_acc_y"]), 4),
        "mpu_acc_z": round(float(last["mpu_acc_z"]), 4),
        "mpu_gyro_x": round(float(last["mpu_gyro_x"]), 4),
        "mpu_gyro_y": round(float(last["mpu_gyro_y"]), 4),
        "mpu_gyro_z": round(float(last["mpu_gyro_z"]), 4),
        "ultra_dist": None if np.isnan(last["ultra_dist"]) else round(float(last["ultra_dist"]), 2),
        "pir_motion": int(last["pir_motion"]),
        "label": str(last["label"]),
    }

    # Build time-series arrays for charts (subsample to 32 pts)
    step = max(1, len(df_window) // 32)
    ts_df = df_window.iloc[::step].copy()
    time_series = {
        "acc_mag": [],
        "gyro_mag": [],
        "temperature": [],
        "humidity": [],
        "distance": [],
        "pir": [],
    }
    for _, row in ts_df.iterrows():
        acc_m = float(np.sqrt(row["mpu_acc_x"]**2 + row["mpu_acc_y"]**2 + row["mpu_acc_z"]**2))
        gyro_m = float(np.sqrt(row["mpu_gyro_x"]**2 + row["mpu_gyro_y"]**2 + row["mpu_gyro_z"]**2))
        time_series["acc_mag"].append(round(acc_m, 4))
        time_series["gyro_mag"].append(round(gyro_m, 4))
        time_series["temperature"].append(None if np.isnan(row["dht_temp"]) else round(float(row["dht_temp"]), 2))
        time_series["humidity"].append(None if np.isnan(row["dht_hum"]) else round(float(row["dht_hum"]), 2))
        time_series["distance"].append(None if np.isnan(row["ultra_dist"]) else round(float(row["ultra_dist"]), 2))
        time_series["pir"].append(int(row["pir_motion"]))

    # Features
    features = feature_extractor.extract(df_window)

    # Model inference
    iso_res = iso_model.predict(features)
    xgb_res = xgb_model.predict(features)
    cnn_res = cnn_model.predict(df_window)

    outputs = ModelOutputs(
        iso_is_anomaly=iso_res["is_anomaly"],
        iso_score=iso_res["anomaly_score"],
        xgb_class=xgb_res["predicted_class"],
        xgb_confidence=xgb_res["confidence"],
        xgb_probs=xgb_res["class_probabilities"],
        cnn_class=cnn_res["predicted_class"],
        cnn_confidence=cnn_res["confidence"],
        cnn_probs=cnn_res["class_probabilities"],
    )
    metadata = TelemetryMetadata(
        timestamp_start=float(df_window["timestamp"].iloc[0]),
        timestamp_end=float(df_window["timestamp"].iloc[-1]),
        window_size=128,
    )

    # Clear leftover queue items before pipeline
    for q in [fusion_to_decision, decision_to_recovery, recovery_to_verification]:
        while not q.empty():
            try:
                q.get_nowait()
            except Exception:
                pass

    fusion_state = fusion_agent.process(outputs, metadata)
    decision_cmd = decision_agent.process(fusion_state)

    recovery_action = None
    verification_result = None
    if decision_cmd and decision_cmd.action_type not in ("NONE", None):
        recovery_action = recovery_agent.process(decision_cmd)
        if recovery_action:
            verification_result = verification_agent.process(recovery_action)

    return {
        "telemetry": telemetry,
        "time_series": time_series,
        "features": {k: (None if (isinstance(v, float) and np.isnan(v)) else v)
                     for k, v in features.items()},
        "models": {
            "isolation_forest": {
                "is_anomaly": iso_res["is_anomaly"],
                "score": round(iso_res["anomaly_score"], 4),
                "threshold": round(iso_model.empirical_threshold, 4),
            },
            "xgboost": {
                "predicted_class": xgb_res["predicted_class"],
                "confidence": round(xgb_res["confidence"], 4),
                "class_probabilities": {k: round(v, 4) for k, v in xgb_res["class_probabilities"].items()},
            },
            "cnn": {
                "predicted_class": cnn_res["predicted_class"],
                "confidence": round(cnn_res["confidence"], 4),
                "latency_ms": round(cnn_res["latency_ms"], 3),
                "class_probabilities": {k: round(v, 4) for k, v in cnn_res["class_probabilities"].items()},
            },
        },
        "fusion": {
            "level": fusion_state.level,
            "primary_fault": fusion_state.primary_fault,
            "confidence": round(fusion_state.confidence, 4),
            "reasoning": fusion_state.reasoning,
        },
        "decision": {
            "action_type": decision_cmd.action_type if decision_cmd else "NONE",
            "target": decision_cmd.target if decision_cmd else "NONE",
        },
        "recovery": {
            "action_taken": recovery_action.action_taken if recovery_action else "NONE",
            "success": recovery_action.success if recovery_action else None,
        },
        "verification": {
            "status": verification_result.status if verification_result else "N/A",
            "message": verification_result.message if verification_result else "No recovery required",
        },
    }

def _sim_loop():
    seed = 42
    while not _stop_event.is_set():
        with _lock:
            scenario = _state["scenario"]
            running = _state["running"]

        if not running:
            time.sleep(0.2)
            continue

        seed += 1
        result = _simulation_tick(scenario, seed)
        if result:
            with _lock:
                _state["tick"] += 1
                _state["latest_result"] = result
                _state["telemetry_history"].append(result["telemetry"])
                if len(_state["telemetry_history"]) > MAX_HISTORY:
                    _state["telemetry_history"] = _state["telemetry_history"][-MAX_HISTORY:]

            fusion = result["fusion"]
            if fusion["level"] != "NORMAL":
                _push_event(
                    level=fusion["level"],
                    message=f"Fusion: {fusion['primary_fault']} — {fusion['reasoning'][:60]}",
                    agent="FusionAgent",
                    fault=fusion["primary_fault"],
                )
            if result["decision"]["action_type"] not in ("NONE", None):
                _push_event(
                    level="INFO",
                    message=f"Decision: {result['decision']['action_type']} → {result['decision']['target']}",
                    agent="DecisionAgent",
                    fault=fusion["primary_fault"],
                )
            if result["recovery"]["action_taken"] not in ("NONE", None):
                _push_event(
                    level="INFO",
                    message=f"Recovery: {result['recovery']['action_taken']} ({'OK' if result['recovery']['success'] else 'FAIL'})",
                    agent="RecoveryAgent",
                    fault=fusion["primary_fault"],
                )

        time.sleep(1.0)  # 1-second tick rate for the UI

# -------------------------------------------------------
# FastAPI App
# -------------------------------------------------------
app = FastAPI(title="RAVEN API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    load_models()
    _stop_event.clear()
    t = threading.Thread(target=_sim_loop, daemon=True)
    t.start()
    _push_event("INFO", "RAVEN API started — simulation mode active", "System")

@app.on_event("shutdown")
def shutdown():
    _stop_event.set()

# -------------------------------------------------------
# Endpoints
# -------------------------------------------------------
@app.get("/api/status")
def get_status():
    with _lock:
        uptime = int(time.time() - _state["start_time"])
        return {
            "mode": "SIMULATION",
            "hardware_connected": False,
            "models_loaded": models_loaded,
            "models_error": models_error,
            "scenario": _state["scenario"],
            "running": _state["running"],
            "tick": _state["tick"],
            "uptime_seconds": uptime,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agents": {
                "isolation_forest": "ONLINE" if models_loaded else "ERROR",
                "xgboost": "ONLINE" if models_loaded else "ERROR",
                "cnn": "ONLINE" if models_loaded else "ERROR",
                "fusion": "ONLINE" if models_loaded else "ERROR",
                "decision": "ONLINE" if models_loaded else "ERROR",
                "recovery": "ONLINE" if models_loaded else "ERROR",
                "verification": "ONLINE" if models_loaded else "ERROR",
            }
        }

@app.get("/api/latest")
def get_latest():
    with _lock:
        result = _state["latest_result"]
    if result is None:
        raise HTTPException(status_code=503, detail="No simulation result yet. Start a scenario first.")
    return result

@app.get("/api/history")
def get_history():
    with _lock:
        return {"history": list(_state["telemetry_history"])}

@app.get("/api/events")
def get_events(limit: int = 50):
    with _lock:
        return {"events": list(_state["event_log"][-limit:])}

class ScenarioRequest(BaseModel):
    scenario: str

@app.post("/api/scenario/start")
def start_scenario(req: ScenarioRequest):
    if req.scenario not in VALID_SCENARIOS:
        raise HTTPException(status_code=400, detail=f"Unknown scenario: {req.scenario}")
    with _lock:
        _state["scenario"] = req.scenario
        _state["running"] = True
    _push_event("INFO", f"Scenario started: {req.scenario}", "System")
    return {"status": "started", "scenario": req.scenario}

@app.post("/api/scenario/stop")
def stop_scenario():
    with _lock:
        _state["running"] = False
    _push_event("INFO", "Scenario stopped", "System")
    return {"status": "stopped"}

@app.post("/api/scenario/reset")
def reset_scenario():
    with _lock:
        _state["running"] = False
        _state["scenario"] = "NORMAL"
        _state["latest_result"] = None
        _state["telemetry_history"] = []
        _state["event_log"] = []
        _state["tick"] = 0
    return {"status": "reset"}

@app.get("/api/scenarios")
def list_scenarios():
    return {"scenarios": VALID_SCENARIOS}

@app.get("/api/model_info")
def get_model_info():
    """Return static model metadata from training artifacts."""
    import os
    models_dir = Path(MODELS_DIR)
    def sz(f): return round(os.path.getsize(models_dir / f) / 1024, 1) if (models_dir / f).exists() else None

    return {
        "isolation_forest": {
            "type": "IsolationForest",
            "version": "1.0.0",
            "contamination": "auto",
            "n_estimators": 100,
            "threshold": round(iso_model.empirical_threshold, 4) if iso_model else None,
            "size_kb": sz("iso_forest.joblib"),
        },
        "xgboost": {
            "type": "XGBClassifier",
            "version": "1.0.0",
            "n_estimators": 50,
            "max_depth": 4,
            "classes": [
                "NORMAL","OVERHEATING","IMPACT_LIKE_EVENT","HIGH_VIBRATION",
                "OBSTACLE_APPROACH","SENSOR_STUCK","SENSOR_DROPOUT","MULTI_SENSOR_ANOMALY"
            ],
            "test_accuracy": 0.89,
            "size_kb": sz("xgb_model.json"),
        },
        "cnn": {
            "type": "1D CNN (ONNX)",
            "version": "1.0.0",
            "in_channels": 10,
            "num_classes": 8,
            "test_accuracy": 0.99,
            "host_latency_ms": 0.11,
            "size_kb": (sz("cnn_1d.onnx") or 0) + (sz("cnn_1d.onnx.data") or 0),
        },
    }

@app.get("/api/dataset_info")
def get_dataset_info():
    synthetic_dir = Path(SYNTHETIC_DATA_DIR)
    file_count = len(list(synthetic_dir.glob("*.csv"))) if synthetic_dir.exists() else 0
    return {
        "synthetic": {
            "name": "RAVEN Synthetic Telemetry",
            "description": "Parametric multi-variate sensor simulation at 50Hz across 8 fault scenarios.",
            "file_count": file_count,
            "sampling_rate_hz": 50,
            "window_size": 128,
            "features": [
                "dht_temp","dht_hum","mpu_acc_x","mpu_acc_y","mpu_acc_z",
                "mpu_gyro_x","mpu_gyro_y","mpu_gyro_z","ultra_dist","pir_motion"
            ],
            "classes": [
                "NORMAL","OVERHEATING","IMPACT_LIKE_EVENT","HIGH_VIBRATION",
                "OBSTACLE_APPROACH","SENSOR_STUCK","SENSOR_DROPOUT","MULTI_SENSOR_ANOMALY"
            ],
        },
        "uci_har": {
            "name": "UCI Human Activity Recognition",
            "role": "Auxiliary — architecture exploration only",
            "note": "Used to verify the 1D CNN architecture can learn from real-world 6-axis IMU data. NOT the primary RAVEN vehicle-fault dataset. No metrics reported from UCI HAR.",
            "sampling_rate_hz": 50,
            "window_size": 128,
        }
    }

@app.get("/api/stream")
async def stream_events():
    """Server-Sent Events stream for live UI updates."""
    async def event_generator():
        last_tick = -1
        while True:
            with _lock:
                current_tick = _state["tick"]
                result = _state["latest_result"]
            if current_tick != last_tick and result is not None:
                last_tick = current_tick
                yield f"data: {json.dumps(result)}\n\n"
            await asyncio.sleep(0.5)
    return StreamingResponse(event_generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=False)
