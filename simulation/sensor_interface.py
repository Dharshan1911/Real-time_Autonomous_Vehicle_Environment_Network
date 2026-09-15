from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass
class SensorReading:
    timestamp: float
    sensor_id: str
    values: List[float]
    status: str # e.g., 'VALID', 'ERROR', 'STALE'
    sequence_num: int

class SensorInterface(ABC):
    @abstractmethod
    def connect(self) -> bool:
        """Initialize connection to the sensor (real or simulated)."""
        pass

    @abstractmethod
    def read(self) -> SensorReading:
        """Read the next data point from the sensor."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Clean up resources."""
        pass
