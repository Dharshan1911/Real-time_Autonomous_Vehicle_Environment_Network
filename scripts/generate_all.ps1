$ErrorActionPreference = 'Stop'
$env:PYTHONPATH = (Get-Location).Path

Write-Host "Generating RAVEN Synthetic Telemetry Datasets..."

$scenarios = @('NORMAL', 'OVERHEATING', 'IMPACT_LIKE_EVENT', 'HIGH_VIBRATION', 'OBSTACLE_APPROACH', 'SENSOR_STUCK', 'SENSOR_DROPOUT', 'MULTI_SENSOR_ANOMALY')
$seeds = @(1, 42, 101, 102, 103, 200)

foreach ($sc in $scenarios) {
    foreach ($seed in $seeds) {
        Write-Host "Generating $sc with seed $seed..."
        python simulation/generate.py --scenario $sc --duration 300 --seed $seed
    }
}

Write-Host "Generation complete."
