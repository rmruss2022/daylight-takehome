"""Tests for device models."""

import pytest
from apps.devices.models import (
    SolarPanel, Battery, ElectricVehicle, Generator,
    AirConditioner, Heater, EVMode
)


@pytest.mark.django_db
class TestDeviceModels:
    """Test device model functionality."""

    def test_solar_panel_creation(self, user):
        """Test creating a solar panel."""
        panel = SolarPanel.objects.create(
            user=user,
            name='Rooftop Solar',
            panel_area_m2=25.0,
            efficiency=0.20,
            max_capacity_w=5000.0,
        )
        assert panel.name == 'Rooftop Solar'
        assert panel.get_device_type() == 'solar_panel'
        assert panel.user == user

    def test_battery_charge_percentage(self, battery):
        """Test battery charge percentage calculation."""
        assert battery.charge_percentage == 50.0

        battery.current_charge_kwh = 10.0
        assert battery.charge_percentage == 100.0

    def test_battery_charge_clamping(self, battery):
        """Test battery doesn't exceed capacity."""
        battery.current_charge_kwh = 15.0  # Exceeds capacity
        battery.save()
        battery.refresh_from_db()
        assert battery.current_charge_kwh == 10.0  # Clamped to capacity

    def test_ev_mode_transitions(self, electric_vehicle):
        """Test EV mode transitions."""
        assert electric_vehicle.mode == EVMode.CHARGING

        electric_vehicle.mode = EVMode.DISCHARGING
        electric_vehicle.save()
        electric_vehicle.refresh_from_db()
        assert electric_vehicle.mode == EVMode.DISCHARGING

        electric_vehicle.mode = EVMode.OFFLINE
        electric_vehicle.save()
        electric_vehicle.refresh_from_db()
        assert electric_vehicle.mode == EVMode.OFFLINE

    def test_ev_charge_percentage(self, electric_vehicle):
        """Test EV charge percentage calculation."""
        assert electric_vehicle.charge_percentage == 50.0

    def test_device_type_detection(self, solar_panel, battery, electric_vehicle):
        """Test get_device_type method."""
        assert solar_panel.get_device_type() == 'solar_panel'
        assert battery.get_device_type() == 'battery'
        assert electric_vehicle.get_device_type() == 'electric_vehicle'

    def test_generator_creation(self, generator):
        """Test generator creation."""
        assert generator.rated_output_w == 3000.0
        assert generator.get_device_type() == 'generator'

    def test_consumption_device_creation(self, air_conditioner, heater):
        """Test consumption device creation."""
        assert air_conditioner.rated_power_w == 3500.0
        assert air_conditioner.get_device_type() == 'air_conditioner'

        assert heater.rated_power_w == 2000.0
        assert heater.get_device_type() == 'heater'
