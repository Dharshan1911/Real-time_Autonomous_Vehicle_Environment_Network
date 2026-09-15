# RAVEN Synthetic Telemetry Scenarios

The Synthetic Telemetry Engine generates physical simulations of sensor data to test the RAVEN AI pipeline.

## 1. NORMAL
**Description:** Baseline sensor operation. Constant values with minimal white noise.
**Purpose:** Trains the Isolation Forest to recognize normal operating variance. 

## 2. OVERHEATING
**Description:** Gradual temperature rise and humidity drop.
**Purpose:** Tests slow-drift detection mechanisms.

## 3. SUDDEN_ACCELERATION
**Description:** Smooth but rapid surge in forward acceleration (Y-axis).
**Purpose:** Tests temporal models (CNN) on valid physical maneuvers vs crashes.

## 4. IMPACT_LIKE_EVENT
**Description:** Very short, extreme amplitude spike in acceleration and gyroscope (all axes).
**Purpose:** Tests immediate fault trigger logic in the Decision Agent.

## 5. HIGH_VIBRATION
**Description:** High frequency sine wave overlaid on the Z-axis accelerometer.
**Purpose:** Simulates driving over rough terrain or mechanical engine imbalance.

## 6. OBSTACLE_APPROACH
**Description:** Ultrasonic distance decreases linearly to a critical minimum.
**Purpose:** Tests rule-based thresholds and Verification Agent recovery.

## 7. PIR_ACTIVITY
**Description:** Motion sensor triggers in random bursts.
**Purpose:** Contextual evaluation (e.g., motion combined with vibration might indicate tampering).

## 8. SENSOR_STUCK
**Description:** A sensor value freezes exactly at its last valid reading without dropping to zero.
**Purpose:** Evaluates variance-monitoring logic (since simple thresholding won't catch this).

## 9. SENSOR_NOISE
**Description:** Ultrasonic sensor experiences extreme variance but mean stays roughly accurate.
**Purpose:** Tests filtering and rolling-average capabilities of Feature Engineering.

## 10. SENSOR_DROPOUT
**Description:** Sensor returns NaN or completely drops out.
**Purpose:** Tests null-handling, imputation strategies, and error state transitions.

## 11. MULTI_SENSOR_ANOMALY
**Description:** Simultaneous high vibration and overheating.
**Purpose:** Tests the AI Fusion Layer's ability to combine anomaly confidence from different models.
