$ErrorActionPreference = 'Stop'
$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"

Write-Host "Training RAVEN AI Models..."

Write-Host "`n--- Training Isolation Forest ---"
python scripts/train_isolation_forest.py

Write-Host "`n--- Training XGBoost Classifier ---"
python scripts/train_xgboost.py

Write-Host "`n--- Training Temporal 1D CNN ---"
python scripts/train_cnn.py

Write-Host "`nTraining complete."
