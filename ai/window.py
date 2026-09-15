from typing import List, Optional
from simulation.sensor_interface import SensorReading

class WindowBuffer:
    def __init__(self, size: int, stride: int):
        self.size = size
        self.stride = stride
        self.buffer: List[SensorReading] = []

    def add(self, reading: SensorReading):
        self.buffer.append(reading)

    def get_window(self) -> Optional[List[SensorReading]]:
        if len(self.buffer) >= self.size:
            window = self.buffer[:self.size]
            # Advance by stride
            self.buffer = self.buffer[self.stride:]
            return window
        return None
