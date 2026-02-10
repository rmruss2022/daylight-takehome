from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .rest_views import (
    UserViewSet, DeviceViewSet, BatteryViewSet,
    ElectricVehicleViewSet, SolarPanelViewSet, GeneratorViewSet,
    AirConditionerViewSet, HeaterViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'batteries', BatteryViewSet, basename='battery')
router.register(r'electric-vehicles', ElectricVehicleViewSet, basename='electricvehicle')
router.register(r'solar-panels', SolarPanelViewSet, basename='solarpanel')
router.register(r'generators', GeneratorViewSet, basename='generator')
router.register(r'air-conditioners', AirConditionerViewSet, basename='airconditioner')
router.register(r'heaters', HeaterViewSet, basename='heater')

urlpatterns = [
    # JWT Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # REST API endpoints
    path('', include(router.urls)),
]
