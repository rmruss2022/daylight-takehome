"""Electric vehicle simulator with connection schedule."""
from datetime import datetime, timedelta
from typing import Dict, Any
import random
from django.utils import timezone
from .base import BaseSimulator
from apps.devices.models import EVMode


class EVSimulator(BaseSimulator):
    """
    Simulates EV behavior with connection schedule.
    Schedule: Away 7 AM - 6 PM on weekdays, connected otherwise
    """

    def _make_naive(self, dt):
        """Convert timezone-aware datetime to naive UTC."""
        if dt and dt.tzinfo:
            return dt.replace(tzinfo=None)
        return dt

    def simulate(self, timestamp: datetime) -> Dict[str, Any]:
        """Simulate EV behavior based on time and connection status."""
        if self.device.status != 'online':
            return {
                **self.get_base_data(timestamp, 0.0),
                'capacity_wh': self.device.capacity_kwh * 1000,
                'current_level_wh': self.device.current_charge_kwh * 1000,
                'flow_w': 0.0,
                'mode': self.device.mode,
            }

        # Determine if EV should be connected based on schedule
        is_weekday = timestamp.weekday() < 5  # Monday = 0, Friday = 4
        hour = timestamp.hour
        should_be_away = is_weekday and 7 <= hour < 18

        current_charge_kwh = self.device.current_charge_kwh
        capacity_kwh = self.device.capacity_kwh

        if should_be_away:
            # EV is away (driving)
            if self.device.mode != EVMode.OFFLINE:
                # Just disconnected, store last seen
                self.device.mode = EVMode.OFFLINE
                self.device.last_seen_at = timestamp
                self.device.save(update_fields=['mode', 'last_seen_at'])

            # Calculate energy consumed while driving
            if self.device.last_seen_at:
                # Ensure both timestamps are naive UTC for comparison
                last_seen = self._make_naive(self.device.last_seen_at)
                ts = self._make_naive(timestamp)
                hours_away = (ts - last_seen).total_seconds() / 3600
                # Update every minute, so small incremental consumption
                energy_consumed_kwh = (self.device.driving_efficiency_kwh_per_hour / 60)
                new_charge_kwh = max(0, current_charge_kwh - energy_consumed_kwh)
                self.device.current_charge_kwh = new_charge_kwh
                self.device.last_seen_at = timestamp
                self.device.save(update_fields=['current_charge_kwh', 'last_seen_at'])
            else:
                new_charge_kwh = current_charge_kwh

            return {
                **self.get_base_data(timestamp, 0.0),
                'capacity_wh': capacity_kwh * 1000,
                'current_level_wh': new_charge_kwh * 1000,
                'flow_w': 0.0,
                'mode': EVMode.OFFLINE.value,
            }
        else:
            # EV is connected
            charge_percentage = (current_charge_kwh / capacity_kwh) * 100

            # Charge until 90% capacity
            if charge_percentage < 90:
                # Charging mode
                if self.device.mode != EVMode.CHARGING:
                    self.device.mode = EVMode.CHARGING
                    self.device.last_seen_at = timestamp
                    self.device.save(update_fields=['mode', 'last_seen_at'])

                # Charge at random rate up to max
                charge_rate_kw = random.uniform(0.7, 1.0) * self.device.max_charge_rate_kw
                flow_w = charge_rate_kw * 1000

                # Update charge level (60 seconds = 1/60 hour)
                new_charge_kwh = min(
                    capacity_kwh,
                    current_charge_kwh + (charge_rate_kw / 60)
                )
                self.device.current_charge_kwh = new_charge_kwh
                self.device.last_seen_at = timestamp
                self.device.save(update_fields=['current_charge_kwh', 'last_seen_at'])

                return {
                    **self.get_base_data(timestamp, 0.0),
                    'capacity_wh': capacity_kwh * 1000,
                    'current_level_wh': new_charge_kwh * 1000,
                    'flow_w': flow_w,
                    'mode': EVMode.CHARGING.value,
                }
            else:
                # Idle (fully charged)
                if self.device.mode != EVMode.CHARGING:
                    self.device.mode = EVMode.CHARGING
                    self.device.save(update_fields=['mode'])

                return {
                    **self.get_base_data(timestamp, 0.0),
                    'capacity_wh': capacity_kwh * 1000,
                    'current_level_wh': current_charge_kwh * 1000,
                    'flow_w': 0.0,
                    'mode': EVMode.CHARGING.value,
                }
