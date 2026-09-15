# RAVEN QNX Deployment Status

This document strictly defines the operational boundaries of the RAVEN platform as it exists today, explicitly separating simulated components developed on the Windows host from native QNX binaries built for the Raspberry Pi 4 target.

## 1. What is QNX-Buildable Now
Using the installed QNX SDP 8.0 toolkit (`C:\Users\dhars\qnx800`), we have successfully configured cross-compilation for the AArch64 (ARMv8) target.

*   **`qnx/src/sensor_bridge.c`**: A native C wrapper program that successfully builds using the `qcc` compiler with the `-Vgcc_ntoaarch64le` target flag. 
*   **Build Automation (`scripts/build_qnx.ps1`)**: A PowerShell script that loads the QNX SDP environment variables and drives the `make` process to produce QNX-native ELF binaries.

## 2. What is Host-Side Simulation (Portable Layer)
The entire analytical brain of RAVEN is built as a portable Python layer. Because it uses universally supported data structures, it can execute on any host (Windows, Linux, or QNX Python).

*   **Synthetic Telemetry Engine (`ai/features.py`, etc.)**: Completely simulated sensor generation (injecting faults, normal states, drops).
*   **AI Pipeline**: 
    *   Isolation Forest (`scikit-learn`)
    *   XGBoost fault classifier (`xgboost`)
    *   Lightweight 1D CNN (`onnxruntime` inference)
*   **Multi-Agent Decision Core (`agents/`)**: The Fusion, Decision, Recovery, and Verification agents all run purely in simulation space, communicating via memory queues.
*   **Host-Side Tests (`scripts/test_host.ps1`)**: All unit and end-to-end integration tests execute against the simulation layer.

## 3. What Still Requires the Raspberry Pi 4 Hardware
*   **Execution of the QNX Native Binaries**: We can *build* the `sensor_bridge` ELF binary on Windows, but we cannot run or test it without flashing it to the QNX target OS running on the actual Raspberry Pi hardware.
*   **Inference Latency Validation**: While the CNN inference clocked at 0.12ms on the Windows Host x86_64 CPU, the actual latency must be re-measured on the Broadcom BCM2711 ARM Cortex-A72 processor inside the Raspberry Pi.
*   **End-to-End System Integration**: Piping real memory/IPC messages from the C sensor bridge into the Python AI layer under target RTOS constraints.

## 4. What Needs Real Sensor Drivers Later
Currently, the `sensor_bridge.c` is a skeleton. To deploy in a real vehicle/environment, the following hardware integration is required:
*   **MPU6050 Driver**: Requires opening `/dev/i2c1` (or equivalent QNX I2C Resource Manager) and writing specific I2C configurations (e.g. setting power management, configuring gyro/accelerometer scale ranges), then actively polling FIFO buffers.
*   **DHT11 / Ultrasonic Drivers**: Requires custom GPIO bit-banging or specific kernel timer interactions depending on how the QNX BSP exposes standard GPIO pins on the RPi.
*   **Real Fault Injection**: Currently, fault generation is mathematical. We will eventually need to induce real-world physical stress (e.g. hitting the IMU) to validate against real data.
