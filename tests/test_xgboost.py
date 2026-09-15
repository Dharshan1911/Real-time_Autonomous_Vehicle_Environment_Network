import pytest
import pandas as pd
import numpy as np
from ai.models.xgboost_classifier import XGBoostFaultClassifier

def test_xgboost_pipeline(tmp_path):
    model = XGBoostFaultClassifier()
    
    # Create dummy training data
    train_data = []
    labels = []
    
    for _ in range(5):
        for i, cls in enumerate(model.classes):
            train_data.append({
                'acc_mag_mean': 1.0, 'acc_mag_std': 0.0, 'gyro_mag_mean': 0.0, 'gyro_mag_std': 0.0,
                'acc_x_var': 0.0, 'acc_y_var': 0.0, 'acc_z_var': 0.0,
                'temp_roc': float(i), 'dist_roc': 0.0,
                'vibration_zcr': 2.0 * i,
                'dht_valid': 1.0, 'ultra_valid': 1.0, 'mpu_valid': 1.0
            })
            labels.append(cls)
        
    df_train = pd.DataFrame(train_data)
    y_train = pd.Series(labels)
    
    model.fit(df_train, y_train)
    assert model.is_trained == True
    
    # Save and load
    model.save(tmp_path)
    model2 = XGBoostFaultClassifier(model_path=tmp_path)
    assert model2.is_trained == True
    
    # Predict NORMAL
    pred = model2.predict(train_data[0])
    assert pred['predicted_class'] == 'NORMAL'
    assert pred['confidence'] > 0.5
    assert 'class_probabilities' in pred
    assert pred['class_probabilities']['NORMAL'] > 0.5
    
    # Predict HIGH_VIBRATION
    pred2 = model2.predict(train_data[3])
    assert pred2['predicted_class'] == 'HIGH_VIBRATION'
    assert pred2['confidence'] > 0.5
