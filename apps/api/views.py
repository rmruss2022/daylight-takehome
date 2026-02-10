"""Custom GraphQL view with proper CSRF handling."""
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from strawberry.django.views import GraphQLView as BaseGraphQLView


@method_decorator(csrf_exempt, name='dispatch')
class GraphQLView(BaseGraphQLView):
    """
    Custom GraphQL view that:
    - Exempts CSRF (uses JWT authentication with Authorization header)
    - Properly sets up context with user for permission checks
    """

    def get_context(self, request, response=None):
        """
        Override get_context to ensure user is available in the context.
        This is critical for the IsAuthenticated permission class to work
        with both session and JWT authentication.
        """
        context = super().get_context(request, response)
        # Ensure user is set in context from the request
        if hasattr(request, 'user'):
            context.user = request.user
        return context
