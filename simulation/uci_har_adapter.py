import time
from simulation.sensor_interface import SensorInterface, SensorReading

class UCIHarAdapter(SensorInterface):
    def __init__(self, sensor_id="mpu6050_sim", fps=50):
        self.sensor_id = sensor_id
        self.seq = 0
        self.interval = 1.0 / fps
        # In the future, this will read from the Inertial Signals files

    def connect(self) -> bool:
        return True

    def read(self) -> SensorReading:
        self.seq += 1
        # Stub: returning dummy raw values for Acc and Gyro (6-axis)
        values = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        # Simulate physical reading delay
        time.sleep(self.interval)
        return SensorReading(
            timestamp=time.time(),
            sensor_id=self.sensor_id,
            values=values,
            status='VALID',
            sequence_num=self.seq
        )

    def disconnect(self) -> None:
        pass
