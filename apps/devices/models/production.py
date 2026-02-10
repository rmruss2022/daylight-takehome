from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base import Device


class SolarPanel(Device):
    """Solar panel that generates electricity based on sunlight."""

    panel_area_m2 = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Panel area in square meters"
    )
    efficiency = models.FloatField(
        validators=[MinValueValidator(0.01), MaxValueValidator(1.0)],
        help_text="Panel efficiency (0.0 to 1.0)"
    )
    max_capacity_w = models.FloatField(
        validators=[MinValueValidator(1.0)],
        help_text="Maximum power output in watts"
    )
    latitude = models.FloatField(
        default=37.77,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        help_text="Installation latitude (default: San Francisco)"
    )
    longitude = models.FloatField(
        default=-122.42,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        help_text="Installation longitude (default: San Francisco)"
    )

    class Meta:
        verbose_name = "Solar Panel"
        verbose_name_plural = "Solar Panels"


class Generator(Device):
    """Backup generator that produces consistent power."""

    rated_output_w = models.FloatField(
        validators=[MinValueValidator(1.0)],
        help_text="Rated power output in watts"
    )

    class Meta:
        verbose_name = "Generator"
        verbose_name_plural = "Generators"
