import pytest
import pandas as pd
from ai.models.isolation_forest import IsolationForestModel
from config.model_config import ISO_FOREST_CONTAMINATION
import numpy as np

def test_isolation_forest_pipeline(tmp_path):
    model = IsolationForestModel(contamination=ISO_FOREST_CONTAMINATION)
    
    # Create dummy training data
    np.random.seed(42)
    train_data = []
    for _ in range(100):
        # Normal data baseline
        train_data.append({
            'acc_mag_mean': np.random.normal(1.0, 0.05),
            'acc_mag_std': np.random.normal(0.01, 0.005),
            'gyro_mag_mean': np.random.normal(0.0, 0.01),
            'gyro_mag_std': np.random.normal(0.0, 0.01),
            'acc_x_var': np.random.normal(0.0, 0.01),
            'acc_y_var': np.random.normal(0.0, 0.01),
            'acc_z_var': np.random.normal(0.0, 0.01),
            'temp_roc': np.random.normal(0.0, 0.01),
            'dist_roc': np.random.normal(0.0, 0.01),
            'vibration_zcr': np.random.normal(2.0, 0.5),
            'dht_valid': 1.0,
            'ultra_valid': 1.0,
            'mpu_valid': 1.0
        })
    df_train = pd.DataFrame(train_data)
    
    model.fit(df_train)
    assert model.is_trained == True
    
    # Save and load
    model.save(tmp_path)
    model2 = IsolationForestModel(model_path=tmp_path)
    assert model2.is_trained == True
    
    # Predict normal
    normal_feat = {
        'acc_mag_mean': 1.0,
        'acc_mag_std': 0.01,
        'gyro_mag_mean': 0.0,
        'gyro_mag_std': 0.0,
        'acc_x_var': 0.0,
        'acc_y_var': 0.0,
        'acc_z_var': 0.0,
        'temp_roc': 0.0,
        'dist_roc': 0.0,
        'vibration_zcr': 2.0,
        'dht_valid': 1.0,
        'ultra_valid': 1.0,
        'mpu_valid': 1.0
    }
    pred_normal = model2.predict(normal_feat)
    assert not pred_normal['is_anomaly']
    
    # Predict anomaly
    anomaly_feat = {
        'acc_mag_mean': 5.0, # High acceleration
        'acc_mag_std': 2.0,
        'gyro_mag_mean': 1.0,
        'gyro_mag_std': 1.0,
        'acc_x_var': 1.0,
        'acc_y_var': 1.0,
        'acc_z_var': 1.0,
        'temp_roc': 10.0, # Huge temp spike
        'dist_roc': 0.0,
        'vibration_zcr': 50.0,
        'dht_valid': 0.0, # Sensor dropped out
        'ultra_valid': 1.0,
        'mpu_valid': 1.0
    }
    pred_anomaly = model2.predict(anomaly_feat)
    assert pred_anomaly['is_anomaly']
    assert pred_anomaly['anomaly_score'] < pred_normal['anomaly_score']
