"""Consumption device simulators."""

import random
from datetime import datetime
from typing import Dict, Any
from .base import BaseSimulator


class ConsumptionSimulator(BaseSimulator):
    """Simulates consumption devices (AC, Heater) with variable power."""

    def simulate(self, timestamp: datetime) -> Dict[str, Any]:
        """Generate variable power consumption within min/max range."""

        if self.device.status != 'online':
            return self.get_base_data(timestamp, 0.0)

        # Random power within min and max range
        power_w = random.uniform(
            self.device.min_power_w,
            self.device.max_power_w
        )

        return self.get_base_data(timestamp, power_w)
