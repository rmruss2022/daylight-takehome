from django.db import models
from django.core.validators import MinValueValidator
from .base import Device


class AirConditioner(Device):
    """Air conditioning unit for cooling."""

    rated_power_w = models.FloatField(
        validators=[MinValueValidator(1.0)],
        help_text="Rated power consumption in watts"
    )
    min_power_w = models.FloatField(
        validators=[MinValueValidator(1.0)],
        help_text="Minimum power consumption in watts"
    )
    max_power_w = models.FloatField(
        validators=[MinValueValidator(1.0)],
        help_text="Maximum power consumption in watts"
    )

    class Meta:
        verbose_name = "Air Conditioner"
        verbose_name_plural = "Air Conditioners"

    def save(self, *args, **kwargs):
        # Ensure min <= rated <= max
        if self.min_power_w > self.rated_power_w:
            self.min_power_w = self.rated_power_w
        if self.max_power_w < self.rated_power_w:
            self.max_power_w = self.rated_power_w
        super().save(*args, **kwargs)


class Heater(Device):
    """Heating unit for warming."""

    rated_power_w = models.FloatField(
        validators=[MinValueValidator(1.0)],
        help_text="Rated power consumption in watts"
    )
    min_power_w = models.FloatField(
        validators=[MinValueValidator(1.0)],
        help_text="Minimum power consumption in watts"
    )
    max_power_w = models.FloatField(
        validators=[MinValueValidator(1.0)],
        help_text="Maximum power consumption in watts"
    )

    class Meta:
        verbose_name = "Heater"
        verbose_name_plural = "Heaters"

    def save(self, *args, **kwargs):
        # Ensure min <= rated <= max
        if self.min_power_w > self.rated_power_w:
            self.min_power_w = self.rated_power_w
        if self.max_power_w < self.rated_power_w:
            self.max_power_w = self.rated_power_w
        super().save(*args, **kwargs)
