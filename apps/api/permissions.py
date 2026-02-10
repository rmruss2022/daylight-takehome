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
        
        # Get the actual request object from Strawberry context
        # Strawberry Django wraps the request in a context object
        if hasattr(context, 'request'):
            request = context.request
        elif hasattr(context, '_request'):
            request = context._request
        else:
            # Context IS the request in some cases
            request = context
        
        if request is None:
            return False
        
        # Check if user is authenticated via Django session
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Ensure user is set in context for resolver access
            context.user = request.user
            return True
        
        # Fall back to JWT authentication from Authorization header
        # Try to get header from multiple possible locations
        auth_header = ''
        if hasattr(request, 'headers') and 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization', '')
        elif hasattr(request, 'META'):
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
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
