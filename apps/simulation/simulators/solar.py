"""Solar panel simulator with solar elevation model."""

import math
import random
from datetime import datetime
from typing import Dict, Any
from .base import BaseSimulator


class SolarPanelSimulator(BaseSimulator):
    """Simulates solar panel output based on sun position."""

    def simulate(self, timestamp: datetime) -> Dict[str, Any]:
        """Calculate solar panel output based on time and location."""

        if self.device.status != 'online':
            return self.get_base_data(timestamp, 0.0)

        # Calculate solar elevation angle
        elevation = self._calculate_solar_elevation(
            timestamp,
            self.device.latitude,
            self.device.longitude
        )

        # Zero output at night
        if elevation <= 0:
            power_w = 0.0
        else:
            # Calculate irradiance based on elevation
            # Max irradiance: 1000 W/m² at solar noon
            base_irradiance = 1000 * math.sin(math.radians(elevation))

            # Apply atmospheric attenuation
            air_mass = 1 / math.sin(math.radians(elevation)) if elevation > 0 else float('inf')
            atmospheric_factor = 0.7 ** (air_mass - 1) if air_mass < 10 else 0

            irradiance = base_irradiance * atmospheric_factor

            # Calculate power: irradiance * area * efficiency
            power_w = irradiance * self.device.panel_area_m2 * self.device.efficiency

            # Add random variation (0.85-1.0) to simulate cloud cover
            cloud_factor = random.uniform(0.85, 1.0)
            power_w *= cloud_factor

            # Cap at max capacity
            power_w = min(power_w, self.device.max_capacity_w)

        return self.get_base_data(timestamp, power_w)

    def _calculate_solar_elevation(self, timestamp: datetime, latitude: float, longitude: float) -> float:
        """
        Calculate solar elevation angle in degrees.

        Uses simplified formula based on:
        - Day of year
        - Hour of day
        - Latitude
        """
        # Day of year (1-365)
        day_of_year = timestamp.timetuple().tm_yday

        # Solar declination angle (simplified)
        # Varies from -23.45° to +23.45° over the year
        declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))

        # Hour angle (0° at solar noon, -15°/hour in morning, +15°/hour in afternoon)
        # Approximate solar noon at 12:00 + longitude correction
        solar_noon_offset = longitude / 15.0  # Convert longitude to hours
        local_solar_time = timestamp.hour + timestamp.minute / 60.0 - solar_noon_offset
        hour_angle = 15.0 * (local_solar_time - 12.0)

        # Calculate elevation angle
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        hour_rad = math.radians(hour_angle)

        sin_elevation = (
            math.sin(lat_rad) * math.sin(dec_rad) +
            math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hour_rad)
        )

        elevation = math.degrees(math.asin(max(-1, min(1, sin_elevation))))

        return elevation
