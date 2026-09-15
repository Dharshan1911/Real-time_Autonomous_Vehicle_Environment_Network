$ErrorActionPreference = 'Stop'

Write-Host "Running Host-Side Simulation Tests for RAVEN..."

$venv = "$PSScriptRoot\..\venv\Scripts\Activate.ps1"
if (Test-Path $venv) {
    . $venv
} else {
    Write-Warning "No virtual environment found at $venv. Running with global python."
}

$env:PYTHONPATH = "$PSScriptRoot\.."

Write-Host "`n[1/3] Running Feature Engineering Tests..."
pytest "$PSScriptRoot\..\tests\test_features.py" -v

Write-Host "`n[2/3] Running AI Model Tests..."
pytest "$PSScriptRoot\..\tests\test_isolation_forest.py" -v
pytest "$PSScriptRoot\..\tests\test_xgboost.py" -v
pytest "$PSScriptRoot\..\tests\test_cnn_1d.py" -v

Write-Host "`n[3/3] Running End-to-End Multi-Agent Integration Tests..."
pytest "$PSScriptRoot\..\tests\test_end_to_end.py" -v

Write-Host "`nAll Host-Side Tests Completed Successfully." -ForegroundColor Green
