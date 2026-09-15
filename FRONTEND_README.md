# RAVEN Dashboard

This is the official presentation-ready frontend for the RAVEN (Responsive Autonomous Vehicle/Environment Network) platform. It provides a complete visual overview of the simulated sensor telemetry, AI model inferences, multi-agent fusion logic, and system architecture.

## Architecture
- **Frontend:** React 19, Vite, TypeScript, Tailwind CSS (v4), Recharts.
- **Backend Adapter:** FastAPI + uvicorn. A thin wrapper (`api/server.py`) around the existing Python `SyntheticTelemetryEngine` and multi-agent pipeline. It does not rewrite any ML models or engine logic; it simply drives the existing pipeline tick-by-tick and streams results over SSE (Server-Sent Events) and REST.
- **Data Flow:** React polls `/api/status` for connection state and `/api/events` for logs, while listening to `/api/stream` (SSE) for high-frequency 1Hz telemetry and AI inference updates.

## Dependencies
- Node.js (v22+)
- Python 3.10+ (Existing RAVEN `venv` with `fastapi` and `uvicorn` added)

## Quick Start (How to Launch)

You will need two terminal windows.

### 1. Start the Backend API
The backend must run from the repository root to access the models and data correctly.
```powershell
cd C:\Users\dhars\Desktop\RAVEN
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH = (Get-Location).Path
python api/server.py
```
*The backend will run on `http://localhost:8000`.*

### 2. Start the Frontend UI
```powershell
cd C:\Users\dhars\Desktop\RAVEN\dashboard
npm run dev
```
*The frontend will run on `http://localhost:5173`. Open this URL in your browser.*

## Presentation Mode
For a streamlined demo during a presentation:
1. Open the Dashboard (`http://localhost:5173`).
2. Click **Presentation Mode** in the bottom left of the sidebar.
3. Use the left-hand scenario selector to run through the 5 major demonstration states:
   - **NORMAL:** Shows baseline healthy telemetry.
   - **IMPACT_LIKE_EVENT:** Demonstrates the 1D CNN catching transient temporal shapes.
   - **SENSOR_STUCK:** Demonstrates XGBoost catching flat-lined variance.
   - **OVERHEATING:** Demonstrates multi-model consensus on threshold violation.
   - **SENSOR_DROPOUT:** Demonstrates XGBoost natively handling `NaN` values from simulated I2C bus loss.

## Limitations & Honesty
- **Simulation Mode:** The UI displays a prominent banner indicating it is in Simulation Mode. Raspberry Pi and physical sensors are NOT connected.
- **Hardware Metrics:** CPU/RAM metrics are intentionally omitted. The UI does not fabricate hardware performance numbers.
- **Recovery Actions:** Decisions and recovery actions shown in the UI are software-level dispatch stubs, as physical actuation requires the future QNX deployment.

## Troubleshooting
- **"Cannot reach RAVEN API" Error:** Ensure the Python backend is running on port 8000. Check the terminal for any Python stack traces (e.g., missing model files).
- **Models failing to load:** Ensure you have generated the synthetic data and trained the models using `scripts/generate_all.ps1` and `scripts/train_all.ps1` in the main RAVEN repo first.
