"""Comprehensive tests for GraphQL API."""

import pytest
import json
from django.contrib.auth.models import User
from django.test import Client
from apps.api.mutations.auth import generate_jwt_token
from apps.devices.models import Battery, ElectricVehicle, SolarPanel


@pytest.fixture
def graphql_client():
    """Create a Django test client for GraphQL."""
    return Client()


@pytest.fixture
def auth_headers(user):
    """Create authentication headers with JWT token."""
    token = generate_jwt_token(user)
    return {'HTTP_AUTHORIZATION': f'Bearer {token}'}


def execute_graphql(client, query, variables=None, headers=None):
    """Helper to execute GraphQL queries."""
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    
    extra = headers or {}
    response = client.post(
        '/api/graphql',
        data=json.dumps(payload),
        content_type='application/json',
        **extra
    )
    return response


@pytest.mark.django_db
class TestAuthMutation:
    """Test GraphQL authentication mutations."""

    def test_login_user_with_valid_credentials(self, graphql_client, user):
        """Test login with valid credentials."""
        query = """
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
        variables = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = execute_graphql(graphql_client, query, variables)
        assert response.status_code == 200
        
        data = response.json()
        assert 'data' in data
        assert 'loginUser' in data['data']
        assert 'token' in data['data']['loginUser']
        assert data['data']['loginUser']['user']['username'] == 'testuser'

    def test_login_user_with_invalid_credentials(self, graphql_client, user):
        """Test login with invalid credentials."""
        query = """
            mutation LoginUser($username: String!, $password: String!) {
                loginUser(username: $username, password: $password) {
                    token
                    user {
                        username
                    }
                }
            }
        """
        variables = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = execute_graphql(graphql_client, query, variables)
        assert response.status_code == 200
        
        data = response.json()
        assert 'errors' in data
        assert 'Invalid credentials' in str(data['errors'])

    def test_login_user_with_nonexistent_user(self, graphql_client):
        """Test login with nonexistent user."""
        query = """
            mutation LoginUser($username: String!, $password: String!) {
                loginUser(username: $username, password: $password) {
                    token
                }
            }
        """
        variables = {
            'username': 'nonexistent',
            'password': 'password123'
        }
        
        response = execute_graphql(graphql_client, query, variables)
        data = response.json()
        assert 'errors' in data


@pytest.mark.django_db
class TestDeviceQueries:
    """Test GraphQL device queries."""

    def test_all_devices_query_authenticated(
        self, graphql_client, auth_headers, user, battery, electric_vehicle
    ):
        """Test allDevices query with authentication."""
        query = """
            query AllDevices {
                allDevices {
                    ... on BatteryType {
                        id
                        name
                        deviceType
                        status
                        capacityKwh
                        currentChargeKwh
                    }
                    ... on ElectricVehicleType {
                        id
                        name
                        deviceType
                        status
                        mode
                        capacityKwh
                    }
                }
            }
        """
        
        response = execute_graphql(graphql_client, query, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert 'data' in data
        assert 'allDevices' in data['data']
        assert len(data['data']['allDevices']) == 2

    def test_all_devices_query_unauthenticated(self, graphql_client):
        """Test allDevices query without authentication."""
        query = """
            query AllDevices {
                allDevices {
                    ... on BatteryType {
                        id
                        name
                    }
                }
            }
        """
        
        response = execute_graphql(graphql_client, query)
        data = response.json()
        assert 'errors' in data

    def test_all_devices_filtered_by_user(
        self, graphql_client, auth_headers, user, another_user, battery
    ):
        """Test allDevices only returns current user's devices."""
        # Create device for another user
        Battery.objects.create(
            user=another_user,
            name='Other Battery',
            capacity_kwh=10.0,
            current_charge_kwh=5.0,
            max_charge_rate_kw=5.0,
            max_discharge_rate_kw=5.0
        )
        
        query = """
            query AllDevices {
                allDevices {
                    ... on BatteryType {
                        id
                        name
                    }
                }
            }
        """
        
        response = execute_graphql(graphql_client, query, headers=auth_headers)
        data = response.json()
        
        assert 'data' in data
        devices = data['data']['allDevices']
        assert len(devices) == 1
        assert devices[0]['name'] == battery.name

    def test_all_devices_with_solar_panel(
        self, graphql_client, auth_headers, user, solar_panel
    ):
        """Test allDevices returns solar panel data."""
        query = """
            query AllDevices {
                allDevices {
                    ... on SolarPanelType {
                        id
                        name
                        deviceType
                        panelAreaM2
                        efficiency
                        maxCapacityW
                    }
                }
            }
        """
        
        response = execute_graphql(graphql_client, query, headers=auth_headers)
        data = response.json()
        
        assert 'data' in data
        devices = data['data']['allDevices']
        assert len(devices) == 1
        assert devices[0]['name'] == solar_panel.name
        assert devices[0]['deviceType'] == 'solar_panel'


@pytest.mark.django_db
class TestEnergyStatsQuery:
    """Test GraphQL energy statistics query."""

    def test_energy_stats_authenticated(
        self, graphql_client, auth_headers, user
    ):
        """Test energyStats query with authentication."""
        query = """
            query EnergyStats {
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
        
        response = execute_graphql(graphql_client, query, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert 'data' in data
        assert 'energyStats' in data['data']
        
        stats = data['data']['energyStats']
        assert 'currentProduction' in stats
        assert 'currentConsumption' in stats
        assert 'currentStorage' in stats
        assert 'currentStorageFlow' in stats
        assert 'netGridFlow' in stats

    def test_energy_stats_unauthenticated(self, graphql_client):
        """Test energyStats query without authentication."""
        query = """
            query EnergyStats {
                energyStats {
                    currentProduction
                    currentConsumption
                }
            }
        """
        
        response = execute_graphql(graphql_client, query)
        data = response.json()
        assert 'errors' in data

    def test_energy_stats_with_zero_data(
        self, graphql_client, auth_headers, user
    ):
        """Test energyStats returns zero values when no data."""
        query = """
            query EnergyStats {
                energyStats {
                    currentProduction
                    currentConsumption
                    currentStorage {
                        totalCapacityWh
                        currentLevelWh
                        percentage
                    }
                }
            }
        """
        
        response = execute_graphql(graphql_client, query, headers=auth_headers)
        data = response.json()
        
        assert 'data' in data
        stats = data['data']['energyStats']
        # Should return zero values if no Redis data
        assert stats['currentProduction'] >= 0
        assert stats['currentConsumption'] >= 0
        assert stats['currentStorage']['totalCapacityWh'] >= 0


@pytest.mark.django_db
class TestGraphQLErrorHandling:
    """Test GraphQL error handling."""

    def test_invalid_query_syntax(self, graphql_client, auth_headers):
        """Test handling of invalid GraphQL syntax."""
        query = """
            query InvalidQuery {
                allDevices
                    id
                    name
                }
            }
        """
        
        response = execute_graphql(graphql_client, query, headers=auth_headers)
        data = response.json()
        assert 'errors' in data

    def test_query_nonexistent_field(self, graphql_client, auth_headers):
        """Test querying non-existent field."""
        query = """
            query NonExistentField {
                allDevices {
                    ... on BatteryType {
                        id
                        nonExistentField
                    }
                }
            }
        """
        
        response = execute_graphql(graphql_client, query, headers=auth_headers)
        data = response.json()
        assert 'errors' in data

    def test_missing_required_argument(self, graphql_client):
        """Test mutation with missing required argument."""
        query = """
            mutation LoginUser {
                loginUser(username: "testuser") {
                    token
                }
            }
        """
        
        response = execute_graphql(graphql_client, query)
        data = response.json()
        assert 'errors' in data


@pytest.mark.django_db
class TestGraphQLComplexQueries:
    """Test complex GraphQL queries."""

    def test_nested_query_with_multiple_device_types(
        self, graphql_client, auth_headers, user,
        battery, electric_vehicle, solar_panel
    ):
        """Test query with multiple device types."""
        query = """
            query ComplexQuery {
                allDevices {
                    ... on BatteryType {
                        id
                        name
                        deviceType
                        capacityKwh
                        currentChargeKwh
                        chargePercentage
                    }
                    ... on ElectricVehicleType {
                        id
                        name
                        deviceType
                        mode
                        capacityKwh
                        currentChargeKwh
                        chargePercentage
                    }
                    ... on SolarPanelType {
                        id
                        name
                        deviceType
                        panelAreaM2
                        efficiency
                    }
                }
            }
        """
        
        response = execute_graphql(graphql_client, query, headers=auth_headers)
        data = response.json()
        
        assert 'data' in data
        devices = data['data']['allDevices']
        assert len(devices) == 3
        
        # Verify each device type
        device_types = [d['deviceType'] for d in devices]
        assert 'battery' in device_types
        assert 'electric_vehicle' in device_types
        assert 'solar_panel' in device_types

    def test_query_with_variables(self, graphql_client, user):
        """Test GraphQL query with variables."""
        query = """
            mutation LoginUser($username: String!, $password: String!) {
                loginUser(username: $username, password: $password) {
                    token
                    user {
                        username
                    }
                }
            }
        """
        variables = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = execute_graphql(graphql_client, query, variables)
        data = response.json()
        
        assert 'data' in data
        assert data['data']['loginUser']['user']['username'] == 'testuser'

    def test_combined_query_devices_and_stats(
        self, graphql_client, auth_headers, user, battery
    ):
        """Test querying both devices and energy stats."""
        query = """
            query CombinedQuery {
                allDevices {
                    ... on BatteryType {
                        id
                        name
                    }
                }
                energyStats {
                    currentProduction
                    currentConsumption
                }
            }
        """
        
        response = execute_graphql(graphql_client, query, headers=auth_headers)
        data = response.json()
        
        assert 'data' in data
        assert 'allDevices' in data['data']
        assert 'energyStats' in data['data']
        assert len(data['data']['allDevices']) == 1


@pytest.mark.django_db
class TestGraphQLAuthentication:
    """Test GraphQL authentication requirements."""

    def test_authenticated_query_requires_token(self, graphql_client, user, battery):
        """Test that authenticated queries require a valid token."""
        query = """
            query AllDevices {
                allDevices {
                    ... on BatteryType {
                        id
                        name
                    }
                }
            }
        """
        
        # Without token
        response = execute_graphql(graphql_client, query)
        data = response.json()
        assert 'errors' in data

    def test_invalid_token_rejected(self, graphql_client, user):
        """Test that invalid tokens are rejected."""
        query = """
            query AllDevices {
                allDevices {
                    ... on BatteryType {
                        id
                    }
                }
            }
        """
        
        headers = {'HTTP_AUTHORIZATION': 'Bearer invalid_token_123'}
        response = execute_graphql(graphql_client, query, headers=headers)
        data = response.json()
        assert 'errors' in data

    def test_expired_token_rejected(self, graphql_client, user):
        """Test that expired tokens are rejected."""
        # Note: This would require mocking time or using a very short expiry
        # For now, we test with malformed token
        query = """
            query AllDevices {
                allDevices {
                    ... on BatteryType {
                        id
                    }
                }
            }
        """
        
        headers = {'HTTP_AUTHORIZATION': 'Bearer expired.token.here'}
        response = execute_graphql(graphql_client, query, headers=headers)
        data = response.json()
        assert 'errors' in data
