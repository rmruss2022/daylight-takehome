"""Authentication mutations."""

import jwt
import strawberry
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.conf import settings
from apps.api.types.user_types import AuthPayload, UserType


def generate_jwt_token(user) -> str:
    """Generate JWT token for user."""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS),
        'iat': datetime.utcnow()
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return token


@strawberry.type
class AuthMutation:
    @strawberry.mutation
    def login_user(self, username: str, password: str) -> AuthPayload:
        """Authenticate user and return JWT token."""
        user = authenticate(username=username, password=password)

        if user is None:
            raise Exception("Invalid credentials")

        token = generate_jwt_token(user)

        return AuthPayload(
            token=token,
            user=UserType(
                id=user.id,
                username=user.username,
                email=user.email
            )
        )
