"""Base simulator class."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any


class BaseSimulator(ABC):
    """Base class for all device simulators."""

    def __init__(self, device):
        self.device = device

    @abstractmethod
    def simulate(self, timestamp: datetime) -> Dict[str, Any]:
        """
        Simulate device behavior at given timestamp.

        Returns a dictionary with simulation results:
        {
            'power_w': float,  # Current power (+ for production/consumption, - for discharging)
            'timestamp': str,  # ISO format timestamp
            'status': str,     # Device status
            ...additional device-specific fields
        }
        """
        pass

    def get_base_data(self, timestamp: datetime, power_w: float) -> Dict[str, Any]:
        """Get base data common to all devices."""
        return {
            'device_id': self.device.id,
            'power_w': power_w,
            'timestamp': timestamp.isoformat(),
            'status': self.device.status,
        }
