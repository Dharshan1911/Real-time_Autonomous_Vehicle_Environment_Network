# RAVEN Quickstart Guide

This guide provides the exact commands required to set up the RAVEN environment, generate synthetic data, train the AI models, and run the end-to-end simulation on a Windows host. 

> **Note:** Real hardware (Raspberry Pi 4) and QNX execution are deferred to the physical deployment phase. This guide covers the Host-Side Simulation.

## 1. Clone Repository & Setup Environment

Open PowerShell and run the following commands:

```powershell
# Clone the repository (Replace URL when published)
git clone https://github.com/Dharshan1911/Real-time_Autonomous_Vehicle_Environment_Network.git RAVEN
cd RAVEN

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

## 2. Dataset Generation

Generate the primary RAVEN synthetic telemetry dataset containing 8 simulated physical and sensor fault scenarios.

```powershell
# Set the project path for module resolution
$env:PYTHONPATH = (Get-Location).Path

# Run the dataset generation script
.\scripts\generate_all.ps1
```

## 3. Model Training

Train the Isolation Forest (Unsupervised), XGBoost (Supervised), and Temporal 1D CNN (Deep Learning) models. 

```powershell
# Fix console encoding for ONNX export logs
$env:PYTHONIOENCODING = "utf-8"

# Train all models sequentially
.\scripts\train_all.ps1
```

## 4. Evaluation and Tests

Evaluate the models and run unit/integration tests to ensure the AI pipeline is robust.

```powershell
# Run the test suite (Verifies ML components and agent message buses)
.\scripts\test_host.ps1
```

## 5. Run the RAVEN Dashboard

The RAVEN platform features a modern React + Vite dashboard with a FastAPI backend that visually tracks telemetry, AI analysis, and multi-agent decisions in real time.

**Terminal 1 (Backend API):**
```powershell
# Ensure you are at the project root with the venv activated
$env:PYTHONPATH = (Get-Location).Path
python api/server.py
```

**Terminal 2 (Frontend UI):**
```powershell
# Navigate to the dashboard directory
cd dashboard

# Install dependencies (only required once)
npm install

# Start the Vite development server
npm run dev
```

Open `http://localhost:5173` in your browser. You can control the simulation scenarios directly from the UI.

## 6. CLI Simulation (Optional)

If you prefer to run the simulation headless without the React frontend, you can use the CLI demo runner.

```powershell
# Run the terminal-based simulation dashboard
python scripts/demo_runner.py
```

A detailed log of all events, probabilities, and agent states will be saved to `logs/demo_run.log`.
