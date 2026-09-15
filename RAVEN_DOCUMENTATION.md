# RAVEN (Responsive Autonomous Vehicle/Environment Network) Documentation

This document provides a comprehensive technical overview of the RAVEN project, covering its architecture, algorithms, implementation details, limitations, and future deployment plans.

---

## 1. Problem Statement
Modern autonomous vehicles and edge-robotic systems operate in complex environments where hardware sensor failure, physical impacts, or system anomalies can compromise safety. Detecting these anomalies directly at the edge requires low-latency, resilient monitoring systems that can differentiate between physical events (like hitting an obstacle) and hardware failures (like a sensor wire disconnecting). 
RAVEN aims to provide a lightweight, multi-agent-architected monitoring system capable of running on constrained edge devices (like a Raspberry Pi 4) with hard real-time operating systems (QNX), ensuring rapid detection and graceful recovery from both environmental and hardware faults.

## 2. System Architecture
RAVEN is structured into three primary layers, ensuring decoupling and portability:
- **Sensor Layer (C/QNX):** (Currently stubbed) Responsible for hard-real-time polling of hardware sensors.
- **AI Pipeline (Python):** Processes telemetry through a `WindowBuffer` and extracts features for three independent ML models (Isolation Forest, XGBoost, 1D CNN).
- **Agent Layer (Python):** A set of decoupled agents communicating via explicit message queues (`message_bus.py`). They evaluate ML outputs, fuse the results, make decisions, and initiate recovery actions.

## 3. Sensor Layer
The system models a vehicle equipped with four primary sensors:
- **DHT11 (Thermal/Humidity):** Monitors system/ambient temperature to detect overheating.
- **MPU6050 (Inertial/6-DoF):** Monitors acceleration and gyroscopic rates to detect impacts and vibration.
- **HC-SR04 (Ultrasonic Proximity):** Detects obstacle approach.
- **PIR (Passive Infrared):** Detects unexpected motion/occupancy.

## 4. Synthetic Telemetry Engine
Because the physical hardware is not yet connected, RAVEN employs a `SyntheticTelemetryEngine` (in `simulation/engine.py`). It generates 50Hz multivariate time-series data mirroring the expected outputs of the sensors, incorporating realistic baseline noise. This allows for rigorous, reproducible software development and testing without physical dependencies.

## 5. Fault Injection
The synthetic engine can inject 8 specific classes of faults/scenarios by mathematically perturbing the baseline signals:
1. `NORMAL`
2. `OVERHEATING`
3. `IMPACT_LIKE_EVENT`
4. `HIGH_VIBRATION`
5. `OBSTACLE_APPROACH`
6. `SENSOR_STUCK`
7. `SENSOR_DROPOUT`
8. `MULTI_SENSOR_ANOMALY`

## 6. Feature Engineering
A 2.56-second window (128 samples at 50Hz) of raw telemetry is condensed into 13 scalar features by the `FeatureExtractor`. These include:
- Acceleration and Gyro magnitudes (mean, std).
- Channel-specific variances.
- Vibration zero-crossing rates (ZCR) on the Z-axis.
- Rate of Change (ROC) for temperature and distance.
- Boolean validity flags to handle `NaN` values resulting from sensor dropouts.

## 7. Isolation Forest (Unsupervised)
An Isolation Forest model provides novelty detection. Its role is to catch structural outliers that the supervised classifiers were not trained on. The anomaly threshold is empirically derived from the 1st percentile of a hold-out normal dataset, ensuring a controlled false-positive rate (1%).

## 8. XGBoost (Supervised Tabular)
An XGBoost classifier evaluates the 13 engineered features. It is highly effective at detecting explicit validity shifts (e.g., `SENSOR_DROPOUT` via validity flags) and sustained shifts (e.g., `OVERHEATING`). It operates rapidly and handles `NaN` values natively.

## 9. Temporal DL Model (Supervised Deep Learning)
A Lightweight 1D Convolutional Neural Network (CNN) processes the raw, scaled temporal window (128 samples x 10 channels). Unlike XGBoost which uses averaged features, the CNN is sensitive to temporal *shape*. This is particularly effective for transient physical events like an `IMPACT_LIKE_EVENT` (which spans only ~10 samples and gets diluted in a window average).

## 10. AI Fusion
The `FusionAgent` receives the outputs of all three models and applies deterministic, auditable rule-based logic to determine the system state (`NORMAL`, `SUSPICIOUS`, `WARNING`, `CRITICAL`). 
- Unanimous normal results in `NORMAL`.
- XGBoost hardware fault consensus results in `CRITICAL`.
- Disagreements fall back to the Isolation Forest novelty check to determine if the state is `WARNING` or merely `SUSPICIOUS`.

## 11. Multi-Agent Architecture
RAVEN uses a multi-agent-architected design pattern. While currently executed sequentially in a single Python process using `queue.Queue` objects, the contracts (`contracts.py`) and message bus (`message_bus.py`) are strictly decoupled. This allows the agents to easily transition to independent concurrent processes in a future deployment environment.

## 12. Decision, Recovery, and Verification
- **Decision Agent:** Maps the fused system state to a specific `DecisionCommand` (e.g., `THROTTLE_LIMIT`, `EMERGENCY_STOP`).
- **Recovery Agent:** Dispatches the recovery action. (Currently logs a success message as a software stub for hardware APIs).
- **Verification Agent:** Confirms the recovery action was dispatched successfully.

## 13. QNX Architecture
RAVEN is designed to run on QNX OS 8.0. QNX provides the deterministic hard-real-time guarantees necessary for jitter-free 50Hz sensor polling (critical for protocols like the DHT11). The architecture explicitly separates the C/QNX real-time sensor polling layer (`qnx/src/sensor_bridge.c`) from the Python AI/Agent stack, communicating via Inter-Process Communication (IPC).

## 14. Current Simulation-Only Limitations
**CRITICAL:** RAVEN is currently in a Simulation-First development phase.
1. All metrics (such as the 99% CNN accuracy) are evaluated on synthetic test data generated by the same parametric engine used for training. This establishes that the models can distinguish the simulator's mathematical fault signatures, *not* real-world physical performance.
2. The multi-agent system runs synchronously on the host; true concurrency is not yet realized.
3. Recovery actions are software stubs, not physical hardware actuations.
4. UCI HAR was used exclusively for preliminary architecture exploration and does not contribute to the final metrics.

## 15. Future Raspberry Pi Deployment
The next phase involves physical deployment to a Raspberry Pi 4 (4GB). This will entail:
1. Flashing QNX OS 8.0 to the target.
2. Compiling the C sensor drivers against the QNX BSP to interface with physical GPIO/I2C/SPI pins.
3. Deploying the Python AI stack (potentially utilizing C-bindings for ONNX runtime to optimize memory/speed).
4. Gathering physical ground-truth telemetry to retrain and validate the models.

## 16. Results
Host-side evaluations on the synthetic dataset confirm the architectural integrity of the pipeline:
- **Total Model Footprint:** 1.1 MB (CNN 57.5 KB, XGB 341 KB, IF 707 KB).
- **Inference Latency:** < 0.5ms per window on the host CPU.
- **Ablation Studies:** XGBoost (89% acc) marginally outperforms a Random Forest (87.5% acc) while providing critical `NaN` handling support.

## 17. Reproduction Instructions
All components can be reproduced cleanly on a Windows host using PowerShell.

1. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
2. **Generate Synthetic Data:**
   ```powershell
   .\scripts\generate_all.ps1
   ```
3. **Train Models:**
   ```powershell
   $env:PYTHONIOENCODING = "utf-8"
   .\scripts\train_all.ps1
   ```
4. **Evaluate AI Pipeline:**
   ```powershell
   .\scripts\test_host.ps1
   .\scripts\evaluate_all.ps1
   ```
5. **Run Demonstration:**
   ```powershell
   python scripts\demo_runner.py --noise_level 1.5
   ```
