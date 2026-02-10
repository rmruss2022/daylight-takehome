"""Tests for authentication."""

import pytest
import jwt
from django.conf import settings
from apps.api.mutations.auth import generate_jwt_token


@pytest.mark.django_db
class TestAuthentication:
    """Test authentication functionality."""

    def test_generate_jwt_token(self, user):
        """Test JWT token generation."""
        token = generate_jwt_token(user)

        # Decode token
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
