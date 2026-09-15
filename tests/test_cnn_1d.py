import pytest
import pandas as pd
import numpy as np
from ai.models.cnn_1d import TemporalCNNModel
from config.paths import MODELS_DIR

def test_cnn_onnx_inference():
    onnx_path = MODELS_DIR / "cnn_1d.onnx"
    if not onnx_path.exists():
        pytest.skip("ONNX model not generated yet")
        
    model = TemporalCNNModel(model_path=MODELS_DIR)
    
    # Create dummy 128-sample window
    t = np.linspace(0, 2.56, 128)
    df = pd.DataFrame({
        'timestamp': t,
        'dht_temp': np.full(128, 25.0),
        'dht_hum': np.full(128, 50.0),
        'mpu_acc_x': np.zeros(128),
        'mpu_acc_y': np.zeros(128),
        'mpu_acc_z': np.ones(128),
        'mpu_gyro_x': np.zeros(128),
        'mpu_gyro_y': np.zeros(128),
        'mpu_gyro_z': np.zeros(128),
        'ultra_dist': np.full(128, 100.0),
        'pir_motion': np.zeros(128),
        'label': ['NORMAL'] * 128
    })
    
    pred = model.predict(df)
    
    assert 'predicted_class' in pred
    assert 'latency_ms' in pred
    assert pred['confidence'] >= 0.0
    assert pred['latency_ms'] > 0.0
