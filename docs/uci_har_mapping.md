# UCI-HAR to MPU6050 Abstraction Mapping

**Purpose:**
The UCI-HAR dataset is used strictly as an auxiliary proxy to simulate a 6-axis MPU6050 IMU for training the Temporal Deep Learning models in RAVEN. It does NOT represent vehicle faults directly; it is used to teach the temporal network to extract structural time-series features.

## Signal Mapping
The dataset provides raw inertial signals sampled at 50Hz, divided into 128-sample windows (2.56 seconds).

| UCI-HAR File | RAVEN MPU6050 Attribute | Measurement |
|---|---|---|
| `body_acc_x_*.txt` | `mpu_acc_x` | Body linear acceleration (X axis) in standard 'g' |
| `body_acc_y_*.txt` | `mpu_acc_y` | Body linear acceleration (Y axis) in standard 'g' |
| `body_acc_z_*.txt` | `mpu_acc_z` | Body linear acceleration (Z axis) in standard 'g' |
| `body_gyro_x_*.txt` | `mpu_gyro_x` | Angular velocity (X axis) in rad/s |
| `body_gyro_y_*.txt` | `mpu_gyro_y` | Angular velocity (Y axis) in rad/s |
| `body_gyro_z_*.txt` | `mpu_gyro_z` | Angular velocity (Z axis) in rad/s |

*Note:* Total acceleration (`total_acc_*`) files from UCI-HAR are ignored in our pipeline because the MPU6050 raw output corresponds more closely to body acceleration (after standard gravity filtering applied by the MPU DMP).

## Windowing and Standardization
- Raw data shape: `(N_samples, 128, 6)`
- **Data Leakage Prevention:** We standardize all 6 channels using the Mean and Standard Deviation derived **strictly from the Train set**. The Test set is transformed using the Train set parameters.
