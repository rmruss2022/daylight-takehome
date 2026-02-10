"""GraphQL permission classes."""

import jwt
from typing import Any
from django.contrib.auth.models import User
from django.conf import settings
from strawberry.permission import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):
    """Permission class that checks for valid JWT token or Django session."""

    message = "User is not authenticated"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        request = info.context.request

        # First, check if user is authenticated via Django session
        if hasattr(request, 'user') and request.user.is_authenticated:
            info.context.user = request.user
            return True

        # Fall back to JWT authentication
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return False

        token = auth_header[7:]  # Remove 'Bearer ' prefix

        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # Get user from payload
            user_id = payload.get('user_id')
            if not user_id:
                return False

            user = User.objects.get(id=user_id)

            # Attach user to request context
            info.context.user = user
            return True

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return False
