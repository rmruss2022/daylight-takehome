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
        """Check if user is authenticated via JWT or Django session."""
        context = info.context
        
        # In Strawberry Django, context is the request object
        # Handle both cases: context as request directly or context.request
        request = context if hasattr(context, 'user') else getattr(context, 'request', None)
        if request is None:
            return False
        
        # Check if user is authenticated via Django session
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Ensure user is set in context for resolver access
            if not hasattr(context, 'user'):
                context.user = request.user
            return True
        
        # Fall back to JWT authentication from Authorization header
        auth_header = getattr(request, 'headers', {}).get('Authorization', '') or request.META.get('HTTP_AUTHORIZATION', '')
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
            
            # Attach user to context for resolver access
            context.user = user
            return True
            
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return False
