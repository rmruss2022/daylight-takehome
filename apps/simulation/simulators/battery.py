"""Battery simulator."""

import random
from datetime import datetime
from typing import Dict, Any
from .base import BaseSimulator


class BatterySimulator(BaseSimulator):
    """Simulates battery charging/discharging behavior."""

    def simulate(self, timestamp: datetime) -> Dict[str, Any]:
        """
        Simulate battery behavior.

        Positive power = charging
        Negative power = discharging
        """

        if self.device.status != 'online':
            return {
                **self.get_base_data(timestamp, 0.0),
                'capacity_wh': self.device.capacity_kwh * 1000,
                'current_level_wh': self.device.current_charge_kwh * 1000,
                'flow_w': 0.0,
            }

        # Current charge level
        current_charge_kwh = self.device.current_charge_kwh
        capacity_kwh = self.device.capacity_kwh
        charge_percentage = (current_charge_kwh / capacity_kwh) * 100

        # Determine charging/discharging based on current state
        # Simple logic: charge if below 50%, discharge if above 70%, idle otherwise
        if charge_percentage < 50:
            # Charging mode
            # Random charging rate up to max
            charge_rate_kw = random.uniform(0.5, 1.0) * self.device.max_charge_rate_kw
            flow_w = charge_rate_kw * 1000  # Positive = charging

            # Update charge level (60 seconds = 1/60 hour)
            new_charge_kwh = min(
                capacity_kwh,
                current_charge_kwh + (charge_rate_kw / 60)
            )
        elif charge_percentage > 70:
            # Discharging mode
            # Random discharging rate up to max
            discharge_rate_kw = random.uniform(0.5, 1.0) * self.device.max_discharge_rate_kw
            flow_w = -discharge_rate_kw * 1000  # Negative = discharging

            # Update charge level
            new_charge_kwh = max(
                0,
                current_charge_kwh - (discharge_rate_kw / 60)
            )
        else:
            # Idle
            flow_w = 0.0
            new_charge_kwh = current_charge_kwh

        # Update database
        self.device.current_charge_kwh = new_charge_kwh
        self.device.save(update_fields=['current_charge_kwh'])

        return {
            **self.get_base_data(timestamp, 0.0),  # Power_w is not used for storage
            'capacity_wh': capacity_kwh * 1000,
            'current_level_wh': new_charge_kwh * 1000,
            'flow_w': flow_w,
        }
