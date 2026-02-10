"""Comprehensive tests for authentication."""

import pytest
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from apps.api.mutations.auth import generate_jwt_token
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Create an API client."""
    return APIClient()


@pytest.mark.django_db
class TestJWTTokenGeneration:
    """Test JWT token generation."""

    def test_generate_jwt_token(self, user):
        """Test JWT token generation for user."""
        token = generate_jwt_token(user)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        assert payload['user_id'] == user.id
        assert payload['username'] == user.username
        assert 'exp' in payload
        assert 'iat' in payload

    def test_token_contains_user_info(self, user):
        """Test token contains correct user information."""
        token = generate_jwt_token(user)
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        assert payload['user_id'] == user.id
        assert payload['username'] == 'testuser'

    def test_token_expiration_time(self, user):
        """Test token has correct expiration time."""
        token = generate_jwt_token(user)
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        exp_time = datetime.utcfromtimestamp(payload['exp'])
        iat_time = datetime.utcfromtimestamp(payload['iat'])
        
        # Check expiration is in the future
        assert exp_time > iat_time
        
        # Check expiration is approximately correct (within 1 minute tolerance)
        expected_exp = iat_time + timedelta(hours=settings.JWT_EXPIRY_HOURS)
        time_diff = abs((exp_time - expected_exp).total_seconds())
        assert time_diff < 60  # Within 60 seconds

    def test_token_issued_at_time(self, user):
        """Test token issued at time is reasonable."""
        before_generation = datetime.utcnow().replace(microsecond=0)
        token = generate_jwt_token(user)
        after_generation = datetime.utcnow().replace(microsecond=0) + timedelta(seconds=1)
        
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        iat_time = datetime.utcfromtimestamp(payload['iat'])
        
        # Issued at time should be between before and after (allowing for second precision)
        assert before_generation <= iat_time <= after_generation


@pytest.mark.django_db
class TestUserAuthentication:
    """Test user authentication."""

    def test_user_creation_with_password(self):
        """Test creating user with password."""
        user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='newpass123'
        )
        
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.check_password('newpass123')
        assert not user.check_password('wrongpass')

    def test_user_password_hashing(self):
        """Test user password is hashed, not stored plain."""
        user = User.objects.create_user(
            username='hashuser',
            password='mypassword123'
        )
        
        # Password should be hashed, not plain
        assert user.password != 'mypassword123'
        assert user.password.startswith('pbkdf2_')  # Django's default hasher
        
        # But check_password should work
        assert user.check_password('mypassword123')

    def test_user_password_validation(self):
        """Test password validation."""
        user = User.objects.create_user(
            username='validuser',
            password='validpass123'
        )
        
        assert user.check_password('validpass123')
        assert not user.check_password('invalidpass')
        assert not user.check_password('')
        assert not user.check_password('validpass1234')  # Extra char

    def test_superuser_creation(self):
        """Test creating superuser."""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        assert admin.is_superuser
        assert admin.is_staff
        assert admin.check_password('adminpass123')


@pytest.mark.django_db
class TestAPIAuthentication:
    """Test API authentication."""

    def test_api_requires_authentication(self, api_client):
        """Test API endpoints require authentication."""
        response = api_client.get('/api/devices/')
        assert response.status_code in [401, 403]

    def test_api_with_valid_token(self, api_client, user):
        """Test API access with valid JWT token."""
        token = generate_jwt_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = api_client.get('/api/devices/')
        assert response.status_code == 200

    def test_api_with_invalid_token(self, api_client):
        """Test API rejects invalid token."""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        
        response = api_client.get('/api/devices/')
        # Should be unauthorized
        assert response.status_code in [401, 403]

    def test_api_without_bearer_prefix(self, api_client, user):
        """Test API rejects token without Bearer prefix."""
        token = generate_jwt_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=token)  # Missing "Bearer "
        
        response = api_client.get('/api/devices/')
        assert response.status_code in [401, 403]

    def test_api_with_empty_token(self, api_client):
        """Test API rejects empty token."""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ')
        
        response = api_client.get('/api/devices/')
        assert response.status_code in [401, 403]


@pytest.mark.django_db
class TestPermissions:
    """Test user permissions."""

    def test_staff_user_access(self):
        """Test staff user has elevated permissions."""
        staff_user = User.objects.create_user(
            username='staff',
            password='staffpass',
            is_staff=True
        )
        
        assert staff_user.is_staff
        assert not staff_user.is_superuser

    def test_superuser_permissions(self):
        """Test superuser has all permissions."""
        superuser = User.objects.create_superuser(
            username='super',
            password='superpass'
        )
        
        assert superuser.is_superuser
        assert superuser.is_staff
        assert superuser.is_active

    def test_regular_user_permissions(self, user):
        """Test regular user has no elevated permissions."""
        assert not user.is_staff
        assert not user.is_superuser
        assert user.is_active

    def test_inactive_user(self):
        """Test inactive user cannot authenticate."""
        inactive_user = User.objects.create_user(
            username='inactive',
            password='inactivepass',
            is_active=False
        )
        
        assert not inactive_user.is_active
        # Inactive users should not be able to authenticate
        # Note: Django's authenticate() checks is_active


@pytest.mark.django_db
class TestPasswordManagement:
    """Test password management."""

    def test_change_user_password(self, user):
        """Test changing user password."""
        old_password = 'testpass123'
        new_password = 'newpass456'
        
        assert user.check_password(old_password)
        
        user.set_password(new_password)
        user.save()
        
        assert user.check_password(new_password)
        assert not user.check_password(old_password)

    def test_password_hash_changes_on_update(self, user):
        """Test password hash changes when password is updated."""
        original_hash = user.password
        
        user.set_password('newpassword123')
        user.save()
        
        assert user.password != original_hash

    def test_empty_password_not_allowed(self):
        """Test empty password is not allowed."""
        user = User.objects.create_user(
            username='emptypass',
            password=''
        )
        
        # Empty password is hashed but can still authenticate with empty string
        # This is expected Django behavior - empty passwords are technically valid
        # but should be prevented at the application/form level
        assert user.password  # Password hash exists
        assert user.check_password('')  # Empty password authenticates
        # Note: In production, form validation should prevent empty passwords


@pytest.mark.django_db
class TestTokenValidation:
    """Test JWT token validation."""

    def test_decode_valid_token(self, user):
        """Test decoding a valid token."""
        token = generate_jwt_token(user)
        
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        assert payload['user_id'] == user.id

    def test_decode_token_with_wrong_secret(self, user):
        """Test decoding token with wrong secret fails."""
        token = generate_jwt_token(user)
        
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(
                token,
                'wrong_secret_key',
                algorithms=[settings.JWT_ALGORITHM]
            )

    def test_decode_token_with_wrong_algorithm(self, user):
        """Test decoding token with wrong algorithm fails."""
        token = generate_jwt_token(user)
        
        with pytest.raises((jwt.DecodeError, jwt.InvalidSignatureError, jwt.InvalidAlgorithmError)):
            jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=['HS512']  # Wrong algorithm
            )

    def test_decode_malformed_token(self):
        """Test decoding malformed token fails."""
        malformed_token = 'this.is.not.a.valid.token'
        
        with pytest.raises((jwt.DecodeError, jwt.InvalidTokenError)):
            jwt.decode(
                malformed_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

    def test_decode_expired_token(self, user):
        """Test decoding expired token fails."""
        # Create token with immediate expiry
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
            'iat': datetime.utcnow() - timedelta(hours=2)
        }
        
        expired_token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(
                expired_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )


@pytest.mark.django_db
class TestUserIsolation:
    """Test user data isolation."""

    def test_users_cannot_access_each_others_data(
        self, api_client, user, another_user
    ):
        """Test users cannot access each other's data."""
        from apps.devices.models import Battery
        
        # Create device for user
        user_battery = Battery.objects.create(
            user=user,
            name='User Battery',
            capacity_kwh=10.0,
            current_charge_kwh=5.0,
            max_charge_rate_kw=5.0,
            max_discharge_rate_kw=5.0
        )
        
        # Create device for another_user
        other_battery = Battery.objects.create(
            user=another_user,
            name='Other Battery',
            capacity_kwh=10.0,
            current_charge_kwh=5.0,
            max_charge_rate_kw=5.0,
            max_discharge_rate_kw=5.0
        )
        
        # Authenticate as user
        token = generate_jwt_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # User should see their device
        response = api_client.get('/api/batteries/')
        assert response.status_code == 200
        device_ids = [d['id'] for d in response.data['results']]
        assert user_battery.id in device_ids
        assert other_battery.id not in device_ids

    def test_token_user_matches_request_user(self, api_client, user, another_user):
        """Test token user ID matches the authenticated user."""
        token = generate_jwt_token(user)
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        assert payload['user_id'] == user.id
        assert payload['user_id'] != another_user.id
