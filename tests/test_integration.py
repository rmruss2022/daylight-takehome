"""Comprehensive integration tests for end-to-end flows."""

import pytest
import json
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.test import Client
from apps.api.mutations.auth import generate_jwt_token
from apps.devices.models import (
    Battery, ElectricVehicle, SolarPanel, Generator,
    AirConditioner, Heater, DeviceStatus
)


@pytest.fixture
def api_client():
    """Create an API client."""
    return APIClient()


@pytest.fixture
def graphql_client():
    """Create a GraphQL client."""
    return Client()


@pytest.mark.django_db
class TestUserRegistrationAndLogin:
    """Test complete user registration and login flow."""

    def test_user_registration_and_login_flow(self, graphql_client):
        """Test complete flow: create user, login, access protected resource."""
        # 1. Create user
        user = User.objects.create_user(
            username='integrationuser',
            email='integration@example.com',
            password='integration123'
        )
        assert user.id is not None
        
        # 2. Login via GraphQL
        login_query = """
            mutation LoginUser($username: String!, $password: String!) {
                loginUser(username: $username, password: $password) {
                    token
                    user {
                        id
                        username
                        email
                    }
                }
            }
        """
        login_variables = {
            'username': 'integrationuser',
            'password': 'integration123'
        }
        
        login_response = graphql_client.post(
            '/graphql/',
            data=json.dumps({
                'query': login_query,
                'variables': login_variables
            }),
            content_type='application/json'
        )
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert 'data' in login_data
        token = login_data['data']['loginUser']['token']
        assert token is not None
        
        # 3. Use token to access protected resource
        devices_query = """
            query AllDevices {
                allDevices {
                    ... on BatteryType {
                        id
                        name
                    }
                }
            }
        """
        
        devices_response = graphql_client.post(
            '/graphql/',
            data=json.dumps({'query': devices_query}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        assert devices_response.status_code == 200
        devices_data = devices_response.json()
        assert 'data' in devices_data
        assert 'allDevices' in devices_data['data']


@pytest.mark.django_db
class TestDeviceCreationAndRetrieval:
    """Test end-to-end device creation and retrieval."""

    def test_create_and_retrieve_battery_rest(self, api_client, user):
        """Test creating and retrieving a battery via REST API."""
        # Authenticate
        token = generate_jwt_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # 1. Create battery
        battery_data = {
            'name': 'Integration Battery',
            'capacity_kwh': 13.5,
            'current_charge_kwh': 6.75,
            'max_charge_rate_kw': 5.0,
            'max_discharge_rate_kw': 5.0,
            'status': 'online'
        }
        
        create_response = api_client.post(
            '/api/batteries/',
            data=battery_data,
            format='json'
        )
        
        assert create_response.status_code == 201
        battery_id = create_response.data['id']
        
        # 2. Retrieve battery
        retrieve_response = api_client.get(f'/api/batteries/{battery_id}/')
        assert retrieve_response.status_code == 200
        assert retrieve_response.data['name'] == 'Integration Battery'
        assert retrieve_response.data['capacity_kwh'] == 13.5
        
        # 3. List all batteries
        list_response = api_client.get('/api/batteries/')
        assert list_response.status_code == 200
        assert any(b['id'] == battery_id for b in list_response.data['results'])
        
        # 4. Update battery
        update_data = {
            'name': 'Updated Integration Battery',
            'capacity_kwh': 13.5,
            'current_charge_kwh': 10.0,
            'max_charge_rate_kw': 5.0,
            'max_discharge_rate_kw': 5.0,
            'status': 'online'
        }
        
        update_response = api_client.put(
            f'/api/batteries/{battery_id}/',
            data=update_data,
            format='json'
        )
        assert update_response.status_code == 200
        assert update_response.data['name'] == 'Updated Integration Battery'
        assert update_response.data['current_charge_kwh'] == 10.0
        
        # 5. Delete battery
        delete_response = api_client.delete(f'/api/batteries/{battery_id}/')
        assert delete_response.status_code == 204
        
        # 6. Verify deletion
        verify_response = api_client.get(f'/api/batteries/{battery_id}/')
        assert verify_response.status_code == 404

    def test_create_multiple_device_types(self, api_client, user):
        """Test creating multiple device types and listing them."""
        token = generate_jwt_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Create battery
        battery_response = api_client.post(
            '/api/batteries/',
            data={
                'name': 'Test Battery',
                'capacity_kwh': 10.0,
                'current_charge_kwh': 5.0,
                'max_charge_rate_kw': 5.0,
                'max_discharge_rate_kw': 5.0,
                'status': 'online'
            },
            format='json'
        )
        assert battery_response.status_code == 201
        
        # Create EV
        ev_response = api_client.post(
            '/api/electric-vehicles/',
            data={
                'name': 'Test EV',
                'capacity_kwh': 75.0,
                'current_charge_kwh': 50.0,
                'max_charge_rate_kw': 11.0,
                'max_discharge_rate_kw': 7.0,
                'mode': 'charging',
                'driving_efficiency_kwh_per_hour': 3.0,
                'status': 'online'
            },
            format='json'
        )
        assert ev_response.status_code == 201
        
        # Create solar panel
        solar_response = api_client.post(
            '/api/solar-panels/',
            data={
                'name': 'Test Solar',
                'panel_area_m2': 20.0,
                'efficiency': 0.20,
                'max_capacity_w': 4000.0,
                'status': 'online'
            },
            format='json'
        )
        assert solar_response.status_code == 201
        
        # List all devices
        devices_response = api_client.get('/api/devices/')
        assert devices_response.status_code == 200
        assert len(devices_response.data['results']) == 3


@pytest.mark.django_db
class TestDashboardDataFlow:
    """Test dashboard data flow end-to-end."""

    def test_dashboard_energy_stats_flow(self, graphql_client, user):
        """Test complete dashboard data flow."""
        # 1. Create devices
        Battery.objects.create(
            user=user,
            name='Dashboard Battery',
            capacity_kwh=10.0,
            current_charge_kwh=5.0,
            max_charge_rate_kw=5.0,
            max_discharge_rate_kw=5.0,
            status=DeviceStatus.ONLINE
        )
        
        SolarPanel.objects.create(
            user=user,
            name='Dashboard Solar',
            panel_area_m2=20.0,
            efficiency=0.20,
            max_capacity_w=4000.0,
            status=DeviceStatus.ONLINE
        )
        
        # 2. Login and get token
        token = generate_jwt_token(user)
        
        # 3. Query devices
        devices_query = """
            query DashboardDevices {
                allDevices {
                    ... on BatteryType {
                        id
                        name
                        deviceType
                        status
                        capacityKwh
                        currentChargeKwh
                        chargePercentage
                    }
                    ... on SolarPanelType {
                        id
                        name
                        deviceType
                        status
                        panelAreaM2
                        efficiency
                    }
                }
            }
        """
        
        devices_response = graphql_client.post(
            '/graphql/',
            data=json.dumps({'query': devices_query}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        assert devices_response.status_code == 200
        devices_data = devices_response.json()
        assert len(devices_data['data']['allDevices']) == 2
        
        # 4. Query energy stats
        stats_query = """
            query DashboardStats {
                energyStats {
                    currentProduction
                    currentConsumption
                    currentStorage {
                        totalCapacityWh
                        currentLevelWh
                        percentage
                    }
                    currentStorageFlow
                    netGridFlow
                }
            }
        """
        
        stats_response = graphql_client.post(
            '/graphql/',
            data=json.dumps({'query': stats_query}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        assert 'energyStats' in stats_data['data']


@pytest.mark.django_db
class TestEnergyCalculations:
    """Test energy calculations across the system."""

    def test_battery_charge_percentage_calculation(self, api_client, user):
        """Test battery charge percentage is calculated correctly."""
        token = generate_jwt_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Create battery with 50% charge
        response = api_client.post(
            '/api/batteries/',
            data={
                'name': 'Calc Battery',
                'capacity_kwh': 10.0,
                'current_charge_kwh': 5.0,
                'max_charge_rate_kw': 5.0,
                'max_discharge_rate_kw': 5.0,
                'status': 'online'
            },
            format='json'
        )
        
        battery_id = response.data['id']
        
        # Retrieve and verify percentage
        retrieve_response = api_client.get(f'/api/batteries/{battery_id}/')
        
        # Calculate expected percentage (from model)
        battery = Battery.objects.get(id=battery_id)
        assert battery.charge_percentage == 50.0

    def test_ev_charge_percentage_calculation(self, api_client, user):
        """Test EV charge percentage is calculated correctly."""
        token = generate_jwt_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Create EV with 75% charge
        response = api_client.post(
            '/api/electric-vehicles/',
            data={
                'name': 'Calc EV',
                'capacity_kwh': 80.0,
                'current_charge_kwh': 60.0,
                'max_charge_rate_kw': 11.0,
                'max_discharge_rate_kw': 7.0,
                'mode': 'charging',
                'driving_efficiency_kwh_per_hour': 3.0,
                'status': 'online'
            },
            format='json'
        )
        
        ev_id = response.data['id']
        
        # Verify percentage
        ev = ElectricVehicle.objects.get(id=ev_id)
        assert ev.charge_percentage == 75.0


@pytest.mark.django_db
class TestUserIsolationIntegration:
    """Test user data isolation in real scenarios."""

    def test_complete_user_isolation_flow(self, api_client):
        """Test complete user isolation across REST and GraphQL."""
        # Create two users
        user1 = User.objects.create_user(
            username='user1',
            password='pass1'
        )
        user2 = User.objects.create_user(
            username='user2',
            password='pass2'
        )
        
        # User 1 creates a battery
        token1 = generate_jwt_token(user1)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
        
        battery1_response = api_client.post(
            '/api/batteries/',
            data={
                'name': 'User 1 Battery',
                'capacity_kwh': 10.0,
                'current_charge_kwh': 5.0,
                'max_charge_rate_kw': 5.0,
                'max_discharge_rate_kw': 5.0,
                'status': 'online'
            },
            format='json'
        )
        battery1_id = battery1_response.data['id']
        
        # User 2 creates a battery
        token2 = generate_jwt_token(user2)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        
        battery2_response = api_client.post(
            '/api/batteries/',
            data={
                'name': 'User 2 Battery',
                'capacity_kwh': 15.0,
                'current_charge_kwh': 7.5,
                'max_charge_rate_kw': 7.0,
                'max_discharge_rate_kw': 7.0,
                'status': 'online'
            },
            format='json'
        )
        battery2_id = battery2_response.data['id']
        
        # User 1 should only see their battery
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
        user1_list = api_client.get('/api/batteries/')
        user1_ids = [b['id'] for b in user1_list.data['results']]
        assert battery1_id in user1_ids
        assert battery2_id not in user1_ids
        
        # User 2 should only see their battery
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        user2_list = api_client.get('/api/batteries/')
        user2_ids = [b['id'] for b in user2_list.data['results']]
        assert battery2_id in user2_ids
        assert battery1_id not in user2_ids
        
        # User 1 cannot access User 2's battery
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
        unauthorized_response = api_client.get(f'/api/batteries/{battery2_id}/')
        assert unauthorized_response.status_code == 404


@pytest.mark.django_db
class TestDeviceStatusTransitions:
    """Test device status transitions through API."""

    def test_device_status_lifecycle(self, api_client, user):
        """Test complete device status lifecycle."""
        token = generate_jwt_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Create device (online by default)
        create_response = api_client.post(
            '/api/batteries/',
            data={
                'name': 'Status Test Battery',
                'capacity_kwh': 10.0,
                'current_charge_kwh': 5.0,
                'max_charge_rate_kw': 5.0,
                'max_discharge_rate_kw': 5.0,
                'status': 'online'
            },
            format='json'
        )
        battery_id = create_response.data['id']
        assert create_response.data['status'] == 'online'
        
        # Transition to offline
        api_client.patch(
            f'/api/batteries/{battery_id}/',
            data={'status': 'offline'},
            format='json'
        )
        offline_response = api_client.get(f'/api/batteries/{battery_id}/')
        assert offline_response.data['status'] == 'offline'
        
        # Transition to error
        api_client.patch(
            f'/api/batteries/{battery_id}/',
            data={'status': 'error'},
            format='json'
        )
        error_response = api_client.get(f'/api/batteries/{battery_id}/')
        assert error_response.data['status'] == 'error'
        
        # Back to online
        api_client.patch(
            f'/api/batteries/{battery_id}/',
            data={'status': 'online'},
            format='json'
        )
        online_response = api_client.get(f'/api/batteries/{battery_id}/')
        assert online_response.data['status'] == 'online'
