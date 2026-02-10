"""Custom GraphQL view with proper CSRF handling."""

from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from strawberry.django.views import GraphQLView as BaseGraphQLView


class GraphQLView(BaseGraphQLView):
    """
    Custom GraphQL view that:
    - Exempts CSRF for JWT authentication (Authorization header)
    - Requires CSRF for session authentication
    """

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        # Check if this is JWT authentication (has Authorization header)
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            # JWT auth - exempt from CSRF
            return csrf_exempt(super().dispatch)(request, *args, **kwargs)
        else:
            # Session auth - require CSRF (handled by Django middleware)
            return super().dispatch(request, *args, **kwargs)
