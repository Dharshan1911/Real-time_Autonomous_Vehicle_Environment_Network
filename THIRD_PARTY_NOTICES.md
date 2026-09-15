# Third-Party Notices

The RAVEN project integrates several open-source technologies, third-party libraries, and external datasets. This document provides attribution for those components. Ownership of the components listed below belongs to their respective creators and is not claimed by Dharshan J.

## 1. Datasets

### UCI Human Activity Recognition (UCI HAR)
- **Purpose:** Auxiliary dataset used for early architectural exploration of the 1D CNN for kinetic shape recognition.
- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones)
- **Status:** External dependency (Not bundled/distributed in this repository).

## 2. Python Frameworks and Libraries

### scikit-learn
- **Purpose:** Machine learning (Isolation Forest anomaly detection, scalers, and metrics).
- **License:** BSD 3-Clause License
- **Status:** Dependency

### XGBoost
- **Purpose:** Extreme Gradient Boosting classification (tabular fault classification).
- **License:** Apache License 2.0
- **Status:** Dependency

### PyTorch (torch)
- **Purpose:** Deep learning framework used for defining and training the 1D CNN.
- **License:** BSD-style license
- **Status:** Dependency

### ONNX / ONNX Runtime
- **Purpose:** Format and runtime for executing the 1D CNN inference on edge/host efficiently.
- **License:** MIT License (ONNX) / MIT License (ONNX Runtime)
- **Status:** Dependency

### FastAPI / Uvicorn
- **Purpose:** REST and Server-Sent Events (SSE) backend server serving telemetry to the dashboard.
- **License:** MIT License (FastAPI) / BSD 3-Clause License (Uvicorn)
- **Status:** Dependency

### NumPy / Pandas / Joblib
- **Purpose:** Data manipulation, vector math, and model serialization.
- **License:** BSD 3-Clause License
- **Status:** Dependency

## 3. Frontend Technologies (JavaScript/React)

### React
- **Purpose:** UI framework for the dashboard.
- **License:** MIT License
- **Status:** Dependency

### Vite
- **Purpose:** Frontend build tooling and development server.
- **License:** MIT License
- **Status:** Dependency

### Tailwind CSS (v4)
- **Purpose:** Utility-first CSS styling for the dashboard.
- **License:** MIT License
- **Status:** Dependency

### Recharts
- **Purpose:** Interactive time-series and radar visualizations.
- **License:** MIT License
- **Status:** Dependency

### Lucide React
- **Purpose:** SVG icon set.
- **License:** ISC License
- **Status:** Dependency

## 4. Hardware/OS Targets (Future)

### QNX Neutrino RTOS
- **Purpose:** Real-Time Operating System planned as the future deployment target for the Raspberry Pi 4 edge device.
- **License:** Proprietary (BlackBerry QNX). The RAVEN repository contains only original interface stubs (`sensor_bridge.c`) written for the project, and does **not** include or distribute any QNX BSPs, SDP binaries, headers, or intellectual property.
- **Status:** External Target Dependency
