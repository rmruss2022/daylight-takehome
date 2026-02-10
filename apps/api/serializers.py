from rest_framework import serializers
from django.contrib.auth.models import User
from apps.devices.models.base import Device
from apps.devices.models.storage import Battery, ElectricVehicle
from apps.devices.models.production import SolarPanel, Generator
from apps.devices.models.consumption import AirConditioner, Heater


class UserSerializer(serializers.ModelSerializer):
    device_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_active', 'is_staff', 'date_joined', 'device_count']
        read_only_fields = ['id', 'date_joined', 'device_count']
    
    def get_device_count(self, obj):
        return obj.devices.count()


class DeviceSerializer(serializers.ModelSerializer):
    device_type = serializers.CharField(source='get_device_type', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Device
        fields = ['id', 'user', 'user_username', 'name', 'status', 
                  'device_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'device_type']


class BatterySerializer(serializers.ModelSerializer):
    device_type = serializers.CharField(source='get_device_type', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    charge_percentage = serializers.FloatField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Battery
        fields = ['id', 'user', 'user_username', 'name', 'status', 'device_type',
                  'capacity_kwh', 'current_charge_kwh', 'charge_percentage',
                  'max_charge_rate_kw', 'max_discharge_rate_kw',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'device_type', 'charge_percentage']


class ElectricVehicleSerializer(serializers.ModelSerializer):
    device_type = serializers.CharField(source='get_device_type', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    charge_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = ElectricVehicle
        fields = ['id', 'user', 'user_username', 'name', 'status', 'device_type',
                  'capacity_kwh', 'current_charge_kwh', 'charge_percentage',
                  'max_charge_rate_kw', 'max_discharge_rate_kw', 'mode',
                  'last_seen_at', 'driving_efficiency_kwh_per_hour',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'device_type', 'charge_percentage']


class SolarPanelSerializer(serializers.ModelSerializer):
    device_type = serializers.CharField(source='get_device_type', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = SolarPanel
        fields = ['id', 'user', 'user_username', 'name', 'status', 'device_type',
                  'panel_area_m2', 'efficiency', 'max_capacity_w',
                  'latitude', 'longitude', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'device_type']


class GeneratorSerializer(serializers.ModelSerializer):
    device_type = serializers.CharField(source='get_device_type', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Generator
        fields = ['id', 'user', 'user_username', 'name', 'status', 'device_type',
                  'rated_output_w', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'device_type']


class AirConditionerSerializer(serializers.ModelSerializer):
    device_type = serializers.CharField(source='get_device_type', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = AirConditioner
        fields = ['id', 'user', 'user_username', 'name', 'status', 'device_type',
                  'rated_power_w', 'min_power_w', 'max_power_w',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'device_type']


class HeaterSerializer(serializers.ModelSerializer):
    device_type = serializers.CharField(source='get_device_type', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Heater
        fields = ['id', 'user', 'user_username', 'name', 'status', 'device_type',
                  'rated_power_w', 'min_power_w', 'max_power_w',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'device_type']
