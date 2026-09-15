import time
import random
from simulation.sensor_interface import SensorInterface, SensorReading

class SyntheticDHT11(SensorInterface):
    def __init__(self, sensor_id="dht11_1"):
        self.sensor_id = sensor_id
        self.seq = 0
        self.temp = 25.0
        self.hum = 50.0

    def connect(self) -> bool:
        return True

    def read(self) -> SensorReading:
        self.seq += 1
        # Gaussian random walk simulating temperature and humidity
        self.temp += random.gauss(0, 0.1)
        self.hum += random.gauss(0, 0.5)
        return SensorReading(
            timestamp=time.time(),
            sensor_id=self.sensor_id,
            values=[self.temp, self.hum],
            status='VALID',
            sequence_num=self.seq
        )

    def disconnect(self) -> None:
        pass
