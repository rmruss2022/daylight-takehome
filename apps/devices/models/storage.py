from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base import Device


class Battery(Device):
    """Stationary battery for energy storage."""

    capacity_kwh = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Total battery capacity in kWh"
    )
    current_charge_kwh = models.FloatField(
        validators=[MinValueValidator(0.0)],
        default=0.0,
        help_text="Current charge level in kWh"
    )
    max_charge_rate_kw = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Maximum charging rate in kW"
    )
    max_discharge_rate_kw = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Maximum discharging rate in kW"
    )

    class Meta:
        verbose_name = "Battery"
        verbose_name_plural = "Batteries"

    def save(self, *args, **kwargs):
        # Ensure current charge doesn't exceed capacity
        if self.current_charge_kwh > self.capacity_kwh:
            self.current_charge_kwh = self.capacity_kwh
        super().save(*args, **kwargs)

    @property
    def charge_percentage(self):
        """Return current charge as percentage."""
        if self.capacity_kwh == 0:
            return 0
        return (self.current_charge_kwh / self.capacity_kwh) * 100


class EVMode(models.TextChoices):
    CHARGING = 'charging', 'Charging'
    DISCHARGING = 'discharging', 'Discharging'
    OFFLINE = 'offline', 'Offline (Driving)'


class ElectricVehicle(Device):
    """Electric vehicle that can charge or discharge (V2H)."""

    capacity_kwh = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Total battery capacity in kWh"
    )
    current_charge_kwh = models.FloatField(
        validators=[MinValueValidator(0.0)],
        default=0.0,
        help_text="Current charge level in kWh"
    )
    max_charge_rate_kw = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Maximum charging rate in kW"
    )
    max_discharge_rate_kw = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Maximum discharging rate in kW (V2H)"
    )
    mode = models.CharField(
        max_length=20,
        choices=EVMode.choices,
        default=EVMode.CHARGING,
        help_text="Current operating mode"
    )
    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time the EV was connected"
    )
    driving_efficiency_kwh_per_hour = models.FloatField(
        default=3.0,
        validators=[MinValueValidator(0.1)],
        help_text="Energy consumption while driving (kWh/hour)"
    )

    class Meta:
        verbose_name = "Electric Vehicle"
        verbose_name_plural = "Electric Vehicles"

    def save(self, *args, **kwargs):
        # Ensure current charge doesn't exceed capacity
        if self.current_charge_kwh > self.capacity_kwh:
            self.current_charge_kwh = self.capacity_kwh
        # Ensure current charge is non-negative
        if self.current_charge_kwh < 0:
            self.current_charge_kwh = 0
        super().save(*args, **kwargs)

    @property
    def charge_percentage(self):
        """Return current charge as percentage."""
        if self.capacity_kwh == 0:
            return 0
        return (self.current_charge_kwh / self.capacity_kwh) * 100
