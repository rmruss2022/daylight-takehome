"""Comprehensive tests for REST API endpoints."""

import pytest
import json
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from apps.devices.models import (
    Device, Battery, ElectricVehicle, SolarPanel,
    Generator, AirConditioner, Heater, DeviceStatus, EVMode
)


@pytest.fixture
def api_client():
    """Create an API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def admin_client(api_client, admin_user):
    """Create an authenticated admin API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.mark.django_db
class TestUserEndpoints:
    """Test user-related API endpoints."""

    def test_list_users_as_admin(self, admin_client, user):
        """Test admin can list all users."""
        response = admin_client.get('/api/users/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 2  # admin + test user

    def test_list_users_as_non_admin(self, authenticated_client):
        """Test non-admin cannot list users."""
        response = authenticated_client.get('/api/users/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_user_as_admin(self, admin_client, user):
        """Test admin can retrieve user details."""
        response = admin_client.get(f'/api/users/{user.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username

    def test_me_endpoint(self, authenticated_client, user):
        """Test authenticated user can get own info."""
        response = authenticated_client.get('/api/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email

    def test_me_endpoint_unauthenticated(self, api_client):
        """Test unauthenticated user cannot access me endpoint."""
        response = api_client.get('/api/users/me/')
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


@pytest.mark.django_db
class TestDeviceEndpoints:
    """Test device API endpoints."""

    def test_list_devices(self, authenticated_client, battery, electric_vehicle):
        """Test authenticated user can list their devices."""
        response = authenticated_client.get('/api/devices/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_list_devices_filtered_by_user(
        self, authenticated_client, battery, user, another_user
    ):
        """Test users only see their own devices."""
        # Create device for another user
        Battery.objects.create(
            user=another_user,
            name='Another Battery',
            capacity_kwh=10.0,
            current_charge_kwh=5.0,
            max_charge_rate_kw=5.0,
            max_discharge_rate_kw=5.0
        )
        
        response = authenticated_client.get('/api/devices/')
        assert response.status_code == status.HTTP_200_OK
        # Should only see own device
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == battery.name

    def test_list_devices_as_admin(self, admin_client, battery, another_user):
        """Test admin can see all devices."""
        # Create device for another user
        Battery.objects.create(
            user=another_user,
            name='Another Battery',
            capacity_kwh=10.0,
            current_charge_kwh=5.0,
            max_charge_rate_kw=5.0,
            max_discharge_rate_kw=5.0
        )
        
        response = admin_client.get('/api/devices/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_retrieve_device(self, authenticated_client, battery):
        """Test retrieving a specific device."""
        response = authenticated_client.get(f'/api/devices/{battery.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == battery.name

    def test_retrieve_other_user_device(
        self, authenticated_client, another_user
    ):
        """Test user cannot retrieve another user's device."""
        other_battery = Battery.objects.create(
            user=another_user,
            name='Other Battery',
            capacity_kwh=10.0,
            current_charge_kwh=5.0,
            max_charge_rate_kw=5.0,
            max_discharge_rate_kw=5.0
        )
        
        response = authenticated_client.get(f'/api/devices/{other_battery.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_device_stats(self, authenticated_client, battery, electric_vehicle):
        """Test device statistics endpoint."""
        # Set different statuses
        battery.status = DeviceStatus.ONLINE
        battery.save()
        
        electric_vehicle.status = DeviceStatus.OFFLINE
        electric_vehicle.save()
        
        response = authenticated_client.get('/api/devices/stats/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total'] == 2
        assert response.data['online'] == 1
        assert response.data['offline'] == 1
        assert response.data['error'] == 0

    def test_unauthenticated_device_access(self, api_client):
        """Test unauthenticated user cannot access devices."""
        response = api_client.get('/api/devices/')
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


@pytest.mark.django_db
class TestBatteryEndpoints:
    """Test battery-specific API endpoints."""

    def test_list_batteries(self, authenticated_client, battery):
        """Test listing batteries."""
        response = authenticated_client.get('/api/batteries/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == battery.name

    def test_create_battery(self, authenticated_client, user):
        """Test creating a battery."""
        data = {
            'name': 'New Battery',
            'capacity_kwh': 15.0,
            'current_charge_kwh': 7.5,
            'max_charge_rate_kw': 7.0,
            'max_discharge_rate_kw': 7.0,
            'status': 'online'
        }
        
        response = authenticated_client.post(
            '/api/batteries/',
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Battery'
        assert Battery.objects.filter(user=user, name='New Battery').exists()

    def test_update_battery(self, authenticated_client, battery):
        """Test updating a battery."""
        data = {
            'name': 'Updated Battery',
            'capacity_kwh': battery.capacity_kwh,
            'current_charge_kwh': 8.0,
            'max_charge_rate_kw': battery.max_charge_rate_kw,
            'max_discharge_rate_kw': battery.max_discharge_rate_kw,
            'status': 'online'
        }
        
        response = authenticated_client.put(
            f'/api/batteries/{battery.id}/',
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Battery'
        assert response.data['current_charge_kwh'] == 8.0

    def test_partial_update_battery(self, authenticated_client, battery):
        """Test partial update of battery."""
        data = {'current_charge_kwh': 9.0}
        
        response = authenticated_client.patch(
            f'/api/batteries/{battery.id}/',
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['current_charge_kwh'] == 9.0
        assert response.data['name'] == battery.name  # Unchanged

    def test_delete_battery(self, authenticated_client, battery):
        """Test deleting a battery."""
        battery_id = battery.id
        response = authenticated_client.delete(f'/api/batteries/{battery_id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Battery.objects.filter(id=battery_id).exists()


@pytest.mark.django_db
class TestElectricVehicleEndpoints:
    """Test EV-specific API endpoints."""

    def test_list_evs(self, authenticated_client, electric_vehicle):
        """Test listing electric vehicles."""
        response = authenticated_client.get('/api/electric-vehicles/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_create_ev(self, authenticated_client, user):
        """Test creating an electric vehicle."""
        data = {
            'name': 'New EV',
            'capacity_kwh': 82.0,
            'current_charge_kwh': 41.0,
            'max_charge_rate_kw': 11.0,
            'max_discharge_rate_kw': 7.0,
            'mode': 'charging',
            'driving_efficiency_kwh_per_hour': 2.8,
            'status': 'online'
        }
        
        response = authenticated_client.post(
            '/api/electric-vehicles/',
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New EV'
        assert ElectricVehicle.objects.filter(user=user, name='New EV').exists()

    def test_update_ev_mode(self, authenticated_client, electric_vehicle):
        """Test updating EV mode."""
        data = {
            'name': electric_vehicle.name,
            'capacity_kwh': electric_vehicle.capacity_kwh,
            'current_charge_kwh': electric_vehicle.current_charge_kwh,
            'max_charge_rate_kw': electric_vehicle.max_charge_rate_kw,
            'max_discharge_rate_kw': electric_vehicle.max_discharge_rate_kw,
            'mode': 'discharging',
            'driving_efficiency_kwh_per_hour': electric_vehicle.driving_efficiency_kwh_per_hour,
            'status': 'online'
        }
        
        response = authenticated_client.put(
            f'/api/electric-vehicles/{electric_vehicle.id}/',
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['mode'] == 'discharging'


@pytest.mark.django_db
class TestSolarPanelEndpoints:
    """Test solar panel-specific API endpoints."""

    def test_list_solar_panels(self, authenticated_client, solar_panel):
        """Test listing solar panels."""
        response = authenticated_client.get('/api/solar-panels/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_create_solar_panel(self, authenticated_client, user):
        """Test creating a solar panel."""
        data = {
            'name': 'New Solar Panel',
            'panel_area_m2': 30.0,
            'efficiency': 0.22,
            'max_capacity_w': 6600.0,
            'latitude': 34.05,
            'longitude': -118.25,
            'status': 'online'
        }
        
        response = authenticated_client.post(
            '/api/solar-panels/',
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Solar Panel'


@pytest.mark.django_db
class TestGeneratorEndpoints:
    """Test generator-specific API endpoints."""

    def test_list_generators(self, authenticated_client, generator):
        """Test listing generators."""
        response = authenticated_client.get('/api/generators/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_create_generator(self, authenticated_client, user):
        """Test creating a generator."""
        data = {
            'name': 'New Generator',
            'rated_output_w': 7500.0,
            'status': 'online'
        }
        
        response = authenticated_client.post(
            '/api/generators/',
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Generator'


@pytest.mark.django_db
class TestConsumptionDeviceEndpoints:
    """Test air conditioner and heater endpoints."""

    def test_list_air_conditioners(self, authenticated_client, air_conditioner):
        """Test listing air conditioners."""
        response = authenticated_client.get('/api/air-conditioners/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_create_air_conditioner(self, authenticated_client, user):
        """Test creating an air conditioner."""
        data = {
            'name': 'New AC',
            'rated_power_w': 4000.0,
            'min_power_w': 2000.0,
            'max_power_w': 5000.0,
            'status': 'online'
        }
        
        response = authenticated_client.post(
            '/api/air-conditioners/',
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New AC'

    def test_list_heaters(self, authenticated_client, heater):
        """Test listing heaters."""
        response = authenticated_client.get('/api/heaters/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_create_heater(self, authenticated_client, user):
        """Test creating a heater."""
        data = {
            'name': 'New Heater',
            'rated_power_w': 2500.0,
            'min_power_w': 1000.0,
            'max_power_w': 3000.0,
            'status': 'online'
        }
        
        response = authenticated_client.post(
            '/api/heaters/',
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Heater'


@pytest.mark.django_db
class TestPermissions:
    """Test API permission checks."""

    def test_non_staff_cannot_see_other_user_devices(
        self, authenticated_client, another_user
    ):
        """Test non-staff users only see their own devices."""
        # Create device for another user
        other_battery = Battery.objects.create(
            user=another_user,
            name='Other Battery',
            capacity_kwh=10.0,
            current_charge_kwh=5.0,
            max_charge_rate_kw=5.0,
            max_discharge_rate_kw=5.0
        )
        
        # Try to access the device list
        response = authenticated_client.get('/api/batteries/')
        assert response.status_code == status.HTTP_200_OK
        
        # Should not see other user's device
        device_ids = [d['id'] for d in response.data['results']]
        assert other_battery.id not in device_ids

    def test_non_staff_cannot_update_other_user_device(
        self, authenticated_client, another_user
    ):
        """Test non-staff users cannot update other user's devices."""
        other_battery = Battery.objects.create(
            user=another_user,
            name='Other Battery',
            capacity_kwh=10.0,
            current_charge_kwh=5.0,
            max_charge_rate_kw=5.0,
            max_discharge_rate_kw=5.0
        )
        
        data = {'name': 'Hacked Battery'}
        response = authenticated_client.patch(
            f'/api/batteries/{other_battery.id}/',
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_non_staff_cannot_delete_other_user_device(
        self, authenticated_client, another_user
    ):
        """Test non-staff users cannot delete other user's devices."""
        other_battery = Battery.objects.create(
            user=another_user,
            name='Other Battery',
            capacity_kwh=10.0,
            current_charge_kwh=5.0,
            max_charge_rate_kw=5.0,
            max_discharge_rate_kw=5.0
        )
        
        response = authenticated_client.delete(
            f'/api/batteries/{other_battery.id}/'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Battery.objects.filter(id=other_battery.id).exists()


@pytest.mark.django_db
class TestValidation:
    """Test API input validation."""

    def test_create_battery_with_invalid_data(self, authenticated_client):
        """Test creating battery with invalid data."""
        data = {
            'name': 'Invalid Battery',
            'capacity_kwh': -10.0,  # Invalid: negative
            'current_charge_kwh': 5.0,
            'max_charge_rate_kw': 5.0,
            'max_discharge_rate_kw': 5.0
        }
        
        response = authenticated_client.post(
            '/api/batteries/',
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_battery_missing_required_field(self, authenticated_client):
        """Test creating battery with missing required field."""
        data = {
            'name': 'Incomplete Battery',
            # Missing capacity_kwh
            'current_charge_kwh': 5.0,
            'max_charge_rate_kw': 5.0
        }
        
        response = authenticated_client.post(
            '/api/batteries/',
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
