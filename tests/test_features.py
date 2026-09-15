import pytest
import pandas as pd
import numpy as np
from ai.features import FeatureExtractor

def test_feature_extraction_normal():
    extractor = FeatureExtractor(fps=50)
    
    # Create a synthetic normal window
    t = np.linspace(0, 1, 50, endpoint=False)
    df = pd.DataFrame({
        'timestamp': t,
        'dht_temp': np.full(50, 25.0),
        'dht_hum': np.full(50, 50.0),
        'mpu_acc_x': np.full(50, 0.0),
        'mpu_acc_y': np.full(50, 0.0),
        'mpu_acc_z': np.full(50, 1.0),
        'mpu_gyro_x': np.full(50, 0.0),
        'mpu_gyro_y': np.full(50, 0.0),
        'mpu_gyro_z': np.full(50, 0.0),
        'ultra_dist': np.full(50, 100.0),
        'pir_motion': np.zeros(50)
    })
    
    features = extractor.extract(df)
    
    assert features['acc_mag_mean'] == 1.0
    assert features['acc_mag_std'] == 0.0
    assert features['temp_roc'] == 0.0
    assert features['dht_valid'] == 1

def test_feature_extraction_vibration():
    extractor = FeatureExtractor(fps=50)
    t = np.linspace(0, 1, 50, endpoint=False)
    # High frequency alternating Z acceleration
    acc_z = np.sin(t * 20 * np.pi) 
    
    df = pd.DataFrame({
        'timestamp': t,
        'dht_temp': np.full(50, 25.0),
        'dht_hum': np.full(50, 50.0),
        'mpu_acc_x': np.zeros(50),
        'mpu_acc_y': np.zeros(50),
        'mpu_acc_z': acc_z,
        'mpu_gyro_x': np.zeros(50),
        'mpu_gyro_y': np.zeros(50),
        'mpu_gyro_z': np.zeros(50),
        'ultra_dist': np.full(50, 100.0),
        'pir_motion': np.zeros(50)
    })
    
    features = extractor.extract(df)
    assert features['vibration_zcr'] > 15.0 # Should detect many zero crossings

def test_sensor_invalidity():
    extractor = FeatureExtractor(fps=50)
    df = pd.DataFrame({
        'timestamp': [0.0, 0.02],
        'dht_temp': [25.0, np.nan],
        'dht_hum': [50.0, 50.0],
        'mpu_acc_x': [0.0, 0.0],
        'mpu_acc_y': [0.0, 0.0],
        'mpu_acc_z': [1.0, 1.0],
        'mpu_gyro_x': [0.0, 0.0],
        'mpu_gyro_y': [0.0, 0.0],
        'mpu_gyro_z': [0.0, 0.0],
        'ultra_dist': [100.0, 100.0],
        'pir_motion': [0, 0]
    })
    
    features = extractor.extract(df)
    assert features['dht_valid'] == 0
    assert features['mpu_valid'] == 1
