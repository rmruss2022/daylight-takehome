from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from apps.devices.models.base import Device
from apps.devices.models.storage import Battery, ElectricVehicle
from apps.devices.models.production import SolarPanel, Generator
from apps.devices.models.consumption import AirConditioner, Heater
from .serializers import (
    UserSerializer, DeviceSerializer, BatterySerializer,
    ElectricVehicleSerializer, SolarPanelSerializer, GeneratorSerializer,
    AirConditionerSerializer, HeaterSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model.
    Allows CRUD operations on users (admin only).
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user info."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class DeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for base Device model.
    Lists all devices with their types.
    """
    queryset = Device.objects.all().select_related('user')
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter devices by user if not admin."""
        if self.request.user.is_staff:
            return Device.objects.all().select_related('user')
        return Device.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get device statistics."""
        queryset = self.get_queryset()
        total = queryset.count()
        online = queryset.filter(status='online').count()
        offline = queryset.filter(status='offline').count()
        error = queryset.filter(status='error').count()
        
        return Response({
            'total': total,
            'online': online,
            'offline': offline,
            'error': error
        })


class BatteryViewSet(viewsets.ModelViewSet):
    """ViewSet for Battery devices."""
    queryset = Battery.objects.all().select_related('user')
    serializer_class = BatterySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Battery.objects.all().select_related('user')
        return Battery.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ElectricVehicleViewSet(viewsets.ModelViewSet):
    """ViewSet for Electric Vehicle devices."""
    queryset = ElectricVehicle.objects.all().select_related('user')
    serializer_class = ElectricVehicleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return ElectricVehicle.objects.all().select_related('user')
        return ElectricVehicle.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SolarPanelViewSet(viewsets.ModelViewSet):
    """ViewSet for Solar Panel devices."""
    queryset = SolarPanel.objects.all().select_related('user')
    serializer_class = SolarPanelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return SolarPanel.objects.all().select_related('user')
        return SolarPanel.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GeneratorViewSet(viewsets.ModelViewSet):
    """ViewSet for Generator devices."""
    queryset = Generator.objects.all().select_related('user')
    serializer_class = GeneratorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Generator.objects.all().select_related('user')
        return Generator.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AirConditionerViewSet(viewsets.ModelViewSet):
    """ViewSet for Air Conditioner devices."""
    queryset = AirConditioner.objects.all().select_related('user')
    serializer_class = AirConditionerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return AirConditioner.objects.all().select_related('user')
        return AirConditioner.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HeaterViewSet(viewsets.ModelViewSet):
    """ViewSet for Heater devices."""
    queryset = Heater.objects.all().select_related('user')
    serializer_class = HeaterSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Heater.objects.all().select_related('user')
        return Heater.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
