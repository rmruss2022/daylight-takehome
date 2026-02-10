"""Pytest configuration and fixtures."""

import pytest
from django.contrib.auth.models import User
from apps.devices.models import (
    SolarPanel, Generator, Battery, ElectricVehicle,
    AirConditioner, Heater
)


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def another_user(db):
    """Create another test user for isolation tests."""
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='testpass123'
    )


@pytest.fixture
def solar_panel(user):
    """Create a test solar panel."""
    return SolarPanel.objects.create(
        user=user,
        name='Test Solar Panel',
        panel_area_m2=20.0,
        efficiency=0.20,
        max_capacity_w=4000.0,
        latitude=37.77,
        longitude=-122.42,
    )


@pytest.fixture
def battery(user):
    """Create a test battery."""
    return Battery.objects.create(
        user=user,
        name='Test Battery',
        capacity_kwh=10.0,
        current_charge_kwh=5.0,
        max_charge_rate_kw=5.0,
        max_discharge_rate_kw=5.0,
    )


@pytest.fixture
def electric_vehicle(user):
    """Create a test EV."""
    return ElectricVehicle.objects.create(
        user=user,
        name='Test EV',
        capacity_kwh=75.0,
        current_charge_kwh=37.5,
        max_charge_rate_kw=11.0,
        max_discharge_rate_kw=7.0,
        mode='charging',
        driving_efficiency_kwh_per_hour=3.0,
    )


@pytest.fixture
def generator(user):
    """Create a test generator."""
    return Generator.objects.create(
        user=user,
        name='Test Generator',
        rated_output_w=3000.0,
    )


@pytest.fixture
def air_conditioner(user):
    """Create a test AC."""
    return AirConditioner.objects.create(
        user=user,
        name='Test AC',
        rated_power_w=3500.0,
        min_power_w=1500.0,
        max_power_w=4500.0,
    )


@pytest.fixture
def heater(user):
    """Create a test heater."""
    return Heater.objects.create(
        user=user,
        name='Test Heater',
        rated_power_w=2000.0,
        min_power_w=800.0,
        max_power_w=2500.0,
    )
