from django.db import models
from django.contrib.auth.models import User


class DeviceStatus(models.TextChoices):
    ONLINE = 'online', 'Online'
    OFFLINE = 'offline', 'Offline'
    ERROR = 'error', 'Error'


class Device(models.Model):
    """Base model for all smart home devices."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=DeviceStatus.choices,
        default=DeviceStatus.ONLINE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_device_type()})"

    def get_device_type(self):
        """Return the specific device type name."""
        if hasattr(self, 'solarpanel'):
            return 'solar_panel'
        elif hasattr(self, 'generator'):
            return 'generator'
        elif hasattr(self, 'battery'):
            return 'battery'
        elif hasattr(self, 'electricvehicle'):
            return 'electric_vehicle'
        elif hasattr(self, 'airconditioner'):
            return 'air_conditioner'
        elif hasattr(self, 'heater'):
            return 'heater'
        return 'unknown'

    def get_specific_device(self):
        """Return the specific device instance (SolarPanel, Battery, etc.)."""
        device_type = self.get_device_type()
        if device_type == 'solar_panel':
            return self.solarpanel
        elif device_type == 'generator':
            return self.generator
        elif device_type == 'battery':
            return self.battery
        elif device_type == 'electric_vehicle':
            return self.electricvehicle
        elif device_type == 'air_conditioner':
            return self.airconditioner
        elif device_type == 'heater':
            return self.heater
        return self
