# AI Fusion Logic

The AI Fusion component integrates signals from three independent models:
1. **Isolation Forest (Unsupervised):** Detects general deviation from normal states. Outputs an anomaly boolean and an anomaly score (lower/negative is more anomalous).
2. **XGBoost (Supervised, Tabular):** Classifies faults using 13 scalar feature-engineered averages. Highly accurate for binary sensor dropouts, constant shifts, or explicit validity shifts.
3. **Lightweight 1D CNN (Supervised, Temporal):** Classifies faults using raw temporal window shapes. Highly accurate for transient physical events (e.g., impacts, sudden vibration) that might average out in feature extraction.

## Fusion Mechanism
The fusion algorithm evaluates model agreement, model strengths, and severity to determine the overall system state (`NORMAL`, `SUSPICIOUS`, `WARNING`, `CRITICAL`).

### Base Confidence Logic
- **High Confidence:** `> 0.75`
- **Medium Confidence:** `0.5 - 0.75`
- **Low Confidence:** `< 0.5`

### State Evaluation Matrix

1. **Unanimous Normal:** 
   - IF = Normal, XGB = NORMAL, CNN = NORMAL.
   - Result: **NORMAL**.

2. **Explicit Hardware Failures (Sensor Dropout, Stuck, Multi-Sensor):**
   - XGBoost explicitly detects `SENSOR_DROPOUT`, `MULTI_SENSOR_ANOMALY`, or `SENSOR_STUCK` with High Confidence.
   - Result: **CRITICAL**. (These are discrete hardware states where XGBoost's tabular validity rules are authoritative).

3. **Supervised Agreement (Physical Faults):**
   - Both XGBoost and CNN predict the *same* non-normal physical fault (e.g., `OVERHEATING`, `HIGH_VIBRATION`, `OBSTACLE_APPROACH`, `IMPACT_LIKE_EVENT`).
   - Result: **CRITICAL**. High confidence in physical anomaly due to cross-model consensus.

4. **Supervised Disagreement (CNN vs XGBoost):**
   - CNN detects a transient event but XGBoost misses it (or vice-versa). 
   - *Tie-breaker:* The system relies on the unsupervised Isolation Forest.
   - If IF detects an anomaly (score < 0): Result is **WARNING** (Fault is assigned to whichever supervised model had higher confidence).
   - If IF is normal (score >= 0): Result is **SUSPICIOUS** (Models disagree, and no overall anomaly was flagged).

5. **Unsupervised Outlier (Novel Anomaly):**
   - XGBoost and CNN both confidently predict `NORMAL`, but Isolation Forest strongly flags an anomaly.
   - Result: **SUSPICIOUS** (A potentially novel/unknown anomaly detected that the supervised classifiers were not trained on).
