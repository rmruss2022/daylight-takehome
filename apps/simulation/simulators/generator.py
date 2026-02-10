"""Generator simulator."""

import random
from datetime import datetime
from typing import Dict, Any
from .base import BaseSimulator


class GeneratorSimulator(BaseSimulator):
    """Simulates generator with steady output and slight variation."""

    def simulate(self, timestamp: datetime) -> Dict[str, Any]:
        """Generate steady output with ±5% random variation."""

        if self.device.status != 'online':
            return self.get_base_data(timestamp, 0.0)

        # Base output
        base_output = self.device.rated_output_w

        # Add ±5% variation
        variation = random.uniform(-0.05, 0.05)
        power_w = base_output * (1 + variation)

        return self.get_base_data(timestamp, power_w)
