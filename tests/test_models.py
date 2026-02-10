"""Comprehensive tests for device models."""

import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from apps.devices.models import (
    Device, DeviceStatus, SolarPanel, Battery, ElectricVehicle,
    Generator, AirConditioner, Heater, EVMode
)


@pytest.mark.django_db
class TestDeviceBaseModel:
    """Test base Device model functionality."""

    def test_device_creation(self, user):
        """Test creating a base device."""
        device = Device.objects.create(
            user=user,
            name='Test Device',
            status=DeviceStatus.ONLINE
        )
        assert device.name == 'Test Device'
        assert device.status == DeviceStatus.ONLINE
        assert device.user == user
        assert device.created_at is not None
        assert device.updated_at is not None

    def test_device_status_transitions(self, user):
        """Test device status can transition between states."""
        device = Device.objects.create(user=user, name='Test Device')
        
        assert device.status == DeviceStatus.ONLINE
        
        device.status = DeviceStatus.OFFLINE
        device.save()
        device.refresh_from_db()
        assert device.status == DeviceStatus.OFFLINE
        
        device.status = DeviceStatus.ERROR
        device.save()
        device.refresh_from_db()
        assert device.status == DeviceStatus.ERROR

    def test_device_timestamps(self, user):
        """Test device timestamps are automatically set."""
        device = Device.objects.create(user=user, name='Test Device')
        created_at = device.created_at
        updated_at = device.updated_at
        
        assert created_at is not None
        assert updated_at is not None
        
        # Update device
        device.name = 'Updated Device'
        device.save()
        device.refresh_from_db()
        
        assert device.updated_at > updated_at
        assert device.created_at == created_at

    def test_device_user_relationship(self, user, another_user):
        """Test devices are properly associated with users."""
        device1 = Device.objects.create(user=user, name='Device 1')
        device2 = Device.objects.create(user=another_user, name='Device 2')
        
        assert device1.user == user
        assert device2.user == another_user
        assert device1 in user.devices.all()
        assert device2 in another_user.devices.all()
        assert device1 not in another_user.devices.all()


@pytest.mark.django_db
class TestBatteryModel:
    """Test Battery model functionality."""

    def test_battery_creation(self, user):
        """Test creating a battery."""
        battery = Battery.objects.create(
            user=user,
            name='Home Battery',
            capacity_kwh=13.5,
            current_charge_kwh=6.75,
            max_charge_rate_kw=5.0,
            max_discharge_rate_kw=5.0
        )
        assert battery.name == 'Home Battery'
        assert battery.capacity_kwh == 13.5
        assert battery.current_charge_kwh == 6.75
        assert battery.get_device_type() == 'battery'

    def test_battery_charge_percentage(self, battery):
        """Test battery charge percentage calculation."""
        assert battery.charge_percentage == 50.0
        
        battery.current_charge_kwh = 2.5
        assert battery.charge_percentage == 25.0
        
        battery.current_charge_kwh = 10.0
        assert battery.charge_percentage == 100.0
        
        battery.current_charge_kwh = 0.0
        assert battery.charge_percentage == 0.0

    def test_battery_charge_percentage_with_zero_capacity(self, user):
        """Test charge percentage returns 0 when capacity is 0."""
        battery = Battery.objects.create(
            user=user,
            name='Empty Battery',
            capacity_kwh=0.1,  # Minimum valid capacity
            current_charge_kwh=0.0,
            max_charge_rate_kw=1.0,
            max_discharge_rate_kw=1.0
        )
        battery.capacity_kwh = 0  # Set to 0 after creation
        assert battery.charge_percentage == 0

    def test_battery_charge_clamping(self, battery):
        """Test battery charge is clamped to capacity."""
        battery.current_charge_kwh = 15.0  # Exceeds capacity of 10.0
        battery.save()
        battery.refresh_from_db()
        assert battery.current_charge_kwh == 10.0

    def test_battery_charge_not_negative(self, battery):
        """Test battery charge cannot be negative."""
        battery.current_charge_kwh = -5.0
        with pytest.raises(ValidationError):
            battery.full_clean()

    def test_battery_capacity_positive(self, user):
        """Test battery capacity must be positive."""
        battery = Battery(
            user=user,
            name='Invalid Battery',
            capacity_kwh=-10.0,
            current_charge_kwh=0.0,
            max_charge_rate_kw=5.0,
            max_discharge_rate_kw=5.0
        )
        with pytest.raises(ValidationError):
            battery.full_clean()


@pytest.mark.django_db
class TestElectricVehicleModel:
    """Test Electric Vehicle model functionality."""

    def test_ev_creation(self, user):
        """Test creating an electric vehicle."""
        ev = ElectricVehicle.objects.create(
            user=user,
            name='Tesla Model 3',
            capacity_kwh=75.0,
            current_charge_kwh=50.0,
            max_charge_rate_kw=11.0,
            max_discharge_rate_kw=7.0,
            mode=EVMode.CHARGING,
            driving_efficiency_kwh_per_hour=3.0
        )
        assert ev.name == 'Tesla Model 3'
        assert ev.mode == EVMode.CHARGING
        assert ev.driving_efficiency_kwh_per_hour == 3.0
        assert ev.get_device_type() == 'electric_vehicle'

    def test_ev_charge_percentage(self, electric_vehicle):
        """Test EV charge percentage calculation."""
        assert electric_vehicle.charge_percentage == 50.0
        
        electric_vehicle.current_charge_kwh = 75.0
        assert electric_vehicle.charge_percentage == 100.0
        
        electric_vehicle.current_charge_kwh = 0.0
        assert electric_vehicle.charge_percentage == 0.0

    def test_ev_mode_transitions(self, electric_vehicle):
        """Test EV can transition between modes."""
        assert electric_vehicle.mode == EVMode.CHARGING
        
        electric_vehicle.mode = EVMode.DISCHARGING
        electric_vehicle.save()
        electric_vehicle.refresh_from_db()
        assert electric_vehicle.mode == EVMode.DISCHARGING
        
        electric_vehicle.mode = EVMode.OFFLINE
        electric_vehicle.save()
        electric_vehicle.refresh_from_db()
        assert electric_vehicle.mode == EVMode.OFFLINE

    def test_ev_charge_clamping(self, electric_vehicle):
        """Test EV charge is clamped to capacity."""
        electric_vehicle.current_charge_kwh = 100.0  # Exceeds capacity of 75.0
        electric_vehicle.save()
        electric_vehicle.refresh_from_db()
        assert electric_vehicle.current_charge_kwh == 75.0

    def test_ev_charge_not_negative(self, electric_vehicle):
        """Test EV charge is clamped to zero when negative."""
        electric_vehicle.current_charge_kwh = -10.0
        electric_vehicle.save()
        electric_vehicle.refresh_from_db()
        assert electric_vehicle.current_charge_kwh == 0.0

    def test_ev_driving_efficiency(self, electric_vehicle):
        """Test EV driving efficiency is stored correctly."""
        assert electric_vehicle.driving_efficiency_kwh_per_hour == 3.0
        
        electric_vehicle.driving_efficiency_kwh_per_hour = 2.5
        electric_vehicle.save()
        electric_vehicle.refresh_from_db()
        assert electric_vehicle.driving_efficiency_kwh_per_hour == 2.5


@pytest.mark.django_db
class TestSolarPanelModel:
    """Test Solar Panel model functionality."""

    def test_solar_panel_creation(self, user):
        """Test creating a solar panel."""
        panel = SolarPanel.objects.create(
            user=user,
            name='Rooftop Solar',
            panel_area_m2=25.0,
            efficiency=0.20,
            max_capacity_w=5000.0,
            latitude=37.77,
            longitude=-122.42
        )
        assert panel.name == 'Rooftop Solar'
        assert panel.panel_area_m2 == 25.0
        assert panel.efficiency == 0.20
        assert panel.max_capacity_w == 5000.0
        assert panel.get_device_type() == 'solar_panel'

    def test_solar_panel_efficiency_range(self, user):
        """Test solar panel efficiency is within valid range."""
        # Valid efficiency
        panel = SolarPanel.objects.create(
            user=user,
            name='Panel 1',
            panel_area_m2=20.0,
            efficiency=0.18,
            max_capacity_w=3600.0
        )
        assert panel.efficiency == 0.18
        
        # Test boundary values
        panel.efficiency = 0.25
        panel.save()
        assert panel.efficiency == 0.25

    def test_solar_panel_location(self, solar_panel):
        """Test solar panel location coordinates."""
        assert solar_panel.latitude == 37.77
        assert solar_panel.longitude == -122.42


@pytest.mark.django_db
class TestGeneratorModel:
    """Test Generator model functionality."""

    def test_generator_creation(self, user):
        """Test creating a generator."""
        gen = Generator.objects.create(
            user=user,
            name='Backup Generator',
            rated_output_w=5000.0
        )
        assert gen.name == 'Backup Generator'
        assert gen.rated_output_w == 5000.0
        assert gen.get_device_type() == 'generator'

    def test_generator_output_ratings(self, generator):
        """Test generator output ratings."""
        assert generator.rated_output_w == 3000.0
        
        generator.rated_output_w = 7500.0
        generator.save()
        generator.refresh_from_db()
        assert generator.rated_output_w == 7500.0


@pytest.mark.django_db
class TestConsumptionDevices:
    """Test consumption device models (AC, Heater)."""

    def test_air_conditioner_creation(self, user):
        """Test creating an air conditioner."""
        ac = AirConditioner.objects.create(
            user=user,
            name='Living Room AC',
            rated_power_w=3500.0,
            min_power_w=1500.0,
            max_power_w=4500.0
        )
        assert ac.name == 'Living Room AC'
        assert ac.rated_power_w == 3500.0
        assert ac.min_power_w == 1500.0
        assert ac.max_power_w == 4500.0
        assert ac.get_device_type() == 'air_conditioner'

    def test_air_conditioner_power_range(self, air_conditioner):
        """Test AC power range."""
        assert air_conditioner.min_power_w <= air_conditioner.rated_power_w
        assert air_conditioner.rated_power_w <= air_conditioner.max_power_w

    def test_heater_creation(self, user):
        """Test creating a heater."""
        heater = Heater.objects.create(
            user=user,
            name='Bedroom Heater',
            rated_power_w=2000.0,
            min_power_w=800.0,
            max_power_w=2500.0
        )
        assert heater.name == 'Bedroom Heater'
        assert heater.rated_power_w == 2000.0
        assert heater.min_power_w == 800.0
        assert heater.max_power_w == 2500.0
        assert heater.get_device_type() == 'heater'

    def test_heater_power_range(self, heater):
        """Test heater power range."""
        assert heater.min_power_w <= heater.rated_power_w
        assert heater.rated_power_w <= heater.max_power_w


@pytest.mark.django_db
class TestDeviceTypeDetection:
    """Test device type detection across all models."""

    def test_get_device_type_for_all_types(
        self, solar_panel, battery, electric_vehicle,
        generator, air_conditioner, heater
    ):
        """Test get_device_type returns correct type for all devices."""
        assert solar_panel.get_device_type() == 'solar_panel'
        assert battery.get_device_type() == 'battery'
        assert electric_vehicle.get_device_type() == 'electric_vehicle'
        assert generator.get_device_type() == 'generator'
        assert air_conditioner.get_device_type() == 'air_conditioner'
        assert heater.get_device_type() == 'heater'

    def test_get_specific_device(
        self, solar_panel, battery, electric_vehicle,
        generator, air_conditioner, heater
    ):
        """Test get_specific_device returns the correct instance."""
        # Cast to base Device and retrieve specific
        devices = Device.objects.filter(
            pk__in=[solar_panel.pk, battery.pk, electric_vehicle.pk]
        )
        
        for device in devices:
            specific = device.get_specific_device()
            assert specific is not None
            assert isinstance(specific, Device)
