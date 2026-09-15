# RAVEN Feature Schema

This document outlines the engineered features extracted from the raw synthetic vehicle telemetry window (e.g., a 128-sample rolling window). These scalar features are fed into the auxiliary ML models (Isolation Forest, XGBoost).

| Feature Name | Description | Purpose |
|---|---|---|
| `acc_mag_mean` | Mean of acceleration magnitude | Captures overall kinetic energy of the vehicle. |
| `acc_mag_std` | Standard deviation of acceleration magnitude | Identifies erratic movement or instability. |
| `gyro_mag_mean` | Mean of gyroscope magnitude | Captures average rotational momentum. |
| `gyro_mag_std` | Standard deviation of gyroscope magnitude | Identifies erratic rotation or tumbling. |
| `acc_x_var`, `acc_y_var`, `acc_z_var` | Variance of individual acceleration axes | High Z variance indicates bumps/vibration; Y variance indicates sudden braking/acceleration. |
| `vibration_zcr` | Zero-crossing rate of mean-centered Z acceleration | Proxies high-frequency mechanical vibration from engines or rough terrain. |
| `delta_temp` | Change in temperature over the window | Detects overheating progression. |
| `temp_roc` | Rate of change of temperature (°C/s) | Differentiates normal heating from catastrophic thermal events. |
| `delta_dist` | Change in ultrasonic distance over the window | Detects approaching obstacles. |
| `dist_roc` | Rate of change of distance (cm/s) | Calculates closure rate to obstacle. |
| `dht_valid`, `ultra_valid`, `mpu_valid` | Boolean indicators (0 or 1) of sensor data validity | Signals sensor dropout or fault conditions explicitly. |
