import pytest
from simulation.engine import SyntheticTelemetryEngine
import numpy as np

def test_engine_normal():
    engine = SyntheticTelemetryEngine(fps=50, duration=2)
    df = engine.generate('NORMAL')
    assert len(df) == 100
    assert 'dht_temp' in df.columns
    assert df['label'].iloc[0] == 'NORMAL'

def test_engine_overheating():
    engine = SyntheticTelemetryEngine(fps=50, duration=2)
    df = engine.generate('OVERHEATING', fault_start=0.5, fault_end=0.9)
    # Check that temperature increases
    start_temp = df['dht_temp'].iloc[0]
    end_temp = df['dht_temp'].iloc[-1]
    assert end_temp > start_temp + 10.0
    assert df['label'].iloc[-1] == 'OVERHEATING'

def test_engine_reproducibility():
    engine1 = SyntheticTelemetryEngine(seed=123)
    df1 = engine1.generate('NORMAL')
    
    engine2 = SyntheticTelemetryEngine(seed=123)
    df2 = engine2.generate('NORMAL')
    
    assert np.allclose(df1['mpu_acc_x'], df2['mpu_acc_x'])

def test_sensor_dropout():
    engine = SyntheticTelemetryEngine(fps=50, duration=2)
    df = engine.generate('SENSOR_DROPOUT', fault_start=0.5, fault_end=0.9)
    # Middle of dropout
    mid_idx = int(100 * 0.7)
    assert np.isnan(df['dht_temp'].iloc[mid_idx])
