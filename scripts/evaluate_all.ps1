$ErrorActionPreference = 'Stop'
$env:PYTHONPATH = (Get-Location).Path

Write-Host "Evaluating RAVEN AI Models..."

Write-Host "`n--- Evaluating Isolation Forest ---"
python scripts/evaluate_isolation_forest.py

Write-Host "`nEvaluation complete."
