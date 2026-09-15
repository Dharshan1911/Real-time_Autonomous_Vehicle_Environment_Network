from ai.window import WindowBuffer
from simulation.sensor_interface import SensorReading
import time

def test_window_buffer():
    buffer = WindowBuffer(size=3, stride=2)
    # Add 2 items (no window yet)
    buffer.add(SensorReading(time.time(), "s1", [0.0], 'VALID', 1))
    buffer.add(SensorReading(time.time(), "s1", [0.0], 'VALID', 2))
    assert buffer.get_window() is None
    
    # Add 1 more (window of size 3 should be returned)
    buffer.add(SensorReading(time.time(), "s1", [0.0], 'VALID', 3))
    window = buffer.get_window()
    assert window is not None
    assert len(window) == 3
    assert window[0].sequence_num == 1
    
    # Buffer should now have 1 item left (3 - 2 = 1)
    assert len(buffer.buffer) == 1
