from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from apps.api.views import GraphQLView
from apps.api.schema import schema
from apps.devices.views import dashboard, dashboard_demo, login_view, logout_view, test_devices
from apps.devices.admin import admin_site

def health_check(request):
    """Health check endpoint for monitoring."""
    return JsonResponse({'status': 'healthy'})

urlpatterns = [
    # Authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Dashboard
    path('', dashboard, name='dashboard'),
    path('dashboard/', dashboard, name='dashboard_main'),
    path('demo/', dashboard_demo, name='dashboard_demo'),
    path('test-devices/', test_devices, name='test_devices'),

    # Admin
    path('admin/', admin_site.urls),

    # API
    path('graphql/', GraphQLView.as_view(schema=schema)),
    path('health/', health_check),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
