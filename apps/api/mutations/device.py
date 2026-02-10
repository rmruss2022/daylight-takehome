"""Device mutations."""

import strawberry
from typing import Optional
from enum import Enum
from strawberry.types import Info
from apps.devices.models import (
    SolarPanel, Generator, Battery, ElectricVehicle,
    AirConditioner, Heater, Device, DeviceStatus, EVMode
)
from apps.api.types.device_types import (
    DeviceUnion, SolarPanelType, GeneratorType, BatteryType,
    ElectricVehicleType, AirConditionerType, HeaterType,
    DeviceStatusEnum, EVModeEnum
)
from apps.api.permissions import IsAuthenticated
from apps.simulation.redis_client import RedisClient


@strawberry.enum
class DeviceTypeEnum(Enum):
    SOLAR_PANEL = "solar_panel"
    GENERATOR = "generator"
    BATTERY = "battery"
    ELECTRIC_VEHICLE = "electric_vehicle"
    AIR_CONDITIONER = "air_conditioner"
    HEATER = "heater"


@strawberry.input
class CreateDeviceInput:
    """Input for creating a new device."""
    name: str
    device_type: DeviceTypeEnum

    # Solar Panel fields
    panel_area_m2: Optional[float] = None
    efficiency: Optional[float] = None
    max_capacity_w: Optional[float] = None
    latitude: Optional[float] = 37.77
    longitude: Optional[float] = -122.42

    # Generator fields
    rated_output_w: Optional[float] = None

    # Battery fields
    capacity_kwh: Optional[float] = None
    current_charge_kwh: Optional[float] = 0.0
    max_charge_rate_kw: Optional[float] = None
    max_discharge_rate_kw: Optional[float] = None

    # EV specific fields
    mode: Optional[EVModeEnum] = EVModeEnum.CHARGING
    driving_efficiency_kwh_per_hour: Optional[float] = 3.0

    # Consumption device fields
    min_power_w: Optional[float] = None
    max_power_w: Optional[float] = None


@strawberry.input
class UpdateDeviceInput:
    """Input for updating an existing device."""
    name: Optional[str] = None
    status: Optional[DeviceStatusEnum] = None

    # Device-specific fields can be updated here
    current_charge_kwh: Optional[float] = None
    mode: Optional[EVModeEnum] = None


def convert_device_to_graphql(device):
    """Convert Django model to GraphQL type."""
    device_type = device.get_device_type()
    specific_device = device.get_specific_device()
    
    # Get current status from Redis (simulation state)
    redis_client = RedisClient()
    current_status = device.status  # Default to DB status
    
    # Check Redis for real-time simulation status
    if device_type in ['battery', 'electric_vehicle']:
        redis_data = redis_client.get_device_storage(device.id)
    else:
        redis_data = redis_client.get_device_data(device.id)
    
    if redis_data and 'status' in redis_data:
        current_status = redis_data['status']

    if device_type == 'solar_panel':
        return SolarPanelType(
            id=device.id,
            name=device.name,
            status=DeviceStatusEnum[current_status.upper()],
            device_type=device_type,
            created_at=device.created_at,
            updated_at=device.updated_at,
            panel_area_m2=specific_device.panel_area_m2,
            efficiency=specific_device.efficiency,
            max_capacity_w=specific_device.max_capacity_w,
            latitude=specific_device.latitude,
            longitude=specific_device.longitude,
        )
    elif device_type == 'generator':
        return GeneratorType(
            id=device.id,
            name=device.name,
            status=DeviceStatusEnum[current_status.upper()],
            device_type=device_type,
            created_at=device.created_at,
            updated_at=device.updated_at,
            rated_output_w=specific_device.rated_output_w,
        )
    elif device_type == 'battery':
        return BatteryType(
            id=device.id,
            name=device.name,
            status=DeviceStatusEnum[current_status.upper()],
            device_type=device_type,
            created_at=device.created_at,
            updated_at=device.updated_at,
            capacity_kwh=specific_device.capacity_kwh,
            current_charge_kwh=specific_device.current_charge_kwh,
            max_charge_rate_kw=specific_device.max_charge_rate_kw,
            max_discharge_rate_kw=specific_device.max_discharge_rate_kw,
            charge_percentage=specific_device.charge_percentage,
        )
    elif device_type == 'electric_vehicle':
        return ElectricVehicleType(
            id=device.id,
            name=device.name,
            status=DeviceStatusEnum[current_status.upper()],
            device_type=device_type,
            created_at=device.created_at,
            updated_at=device.updated_at,
            capacity_kwh=specific_device.capacity_kwh,
            current_charge_kwh=specific_device.current_charge_kwh,
            max_charge_rate_kw=specific_device.max_charge_rate_kw,
            max_discharge_rate_kw=specific_device.max_discharge_rate_kw,
            mode=EVModeEnum[specific_device.mode.upper()],
            last_seen_at=specific_device.last_seen_at,
            driving_efficiency_kwh_per_hour=specific_device.driving_efficiency_kwh_per_hour,
            charge_percentage=specific_device.charge_percentage,
        )
    elif device_type == 'air_conditioner':
        return AirConditionerType(
            id=device.id,
            name=device.name,
            status=DeviceStatusEnum[current_status.upper()],
            device_type=device_type,
            created_at=device.created_at,
            updated_at=device.updated_at,
            rated_power_w=specific_device.rated_power_w,
            min_power_w=specific_device.min_power_w,
            max_power_w=specific_device.max_power_w,
        )
    elif device_type == 'heater':
        return HeaterType(
            id=device.id,
            name=device.name,
            status=DeviceStatusEnum[current_status.upper()],
            device_type=device_type,
            created_at=device.created_at,
            updated_at=device.updated_at,
            rated_power_w=specific_device.rated_power_w,
            min_power_w=specific_device.min_power_w,
            max_power_w=specific_device.max_power_w,
        )


@strawberry.type
class DeviceMutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_device(self, info: Info, input: CreateDeviceInput) -> DeviceUnion:
        """Create a new device."""
        user = info.context.user

        # Create device based on type
        if input.device_type == DeviceTypeEnum.SOLAR_PANEL:
            device = SolarPanel.objects.create(
                user=user,
                name=input.name,
                panel_area_m2=input.panel_area_m2,
                efficiency=input.efficiency,
                max_capacity_w=input.max_capacity_w,
                latitude=input.latitude,
                longitude=input.longitude,
            )
        elif input.device_type == DeviceTypeEnum.GENERATOR:
            device = Generator.objects.create(
                user=user,
                name=input.name,
                rated_output_w=input.rated_output_w,
            )
        elif input.device_type == DeviceTypeEnum.BATTERY:
            device = Battery.objects.create(
                user=user,
                name=input.name,
                capacity_kwh=input.capacity_kwh,
                current_charge_kwh=input.current_charge_kwh,
                max_charge_rate_kw=input.max_charge_rate_kw,
                max_discharge_rate_kw=input.max_discharge_rate_kw,
            )
        elif input.device_type == DeviceTypeEnum.ELECTRIC_VEHICLE:
            device = ElectricVehicle.objects.create(
                user=user,
                name=input.name,
                capacity_kwh=input.capacity_kwh,
                current_charge_kwh=input.current_charge_kwh,
                max_charge_rate_kw=input.max_charge_rate_kw,
                max_discharge_rate_kw=input.max_discharge_rate_kw,
                mode=input.mode.value,
                driving_efficiency_kwh_per_hour=input.driving_efficiency_kwh_per_hour,
            )
        elif input.device_type == DeviceTypeEnum.AIR_CONDITIONER:
            device = AirConditioner.objects.create(
                user=user,
                name=input.name,
                rated_power_w=input.rated_output_w,
                min_power_w=input.min_power_w,
                max_power_w=input.max_power_w,
            )
        elif input.device_type == DeviceTypeEnum.HEATER:
            device = Heater.objects.create(
                user=user,
                name=input.name,
                rated_power_w=input.rated_output_w,
                min_power_w=input.min_power_w,
                max_power_w=input.max_power_w,
            )
        else:
            raise Exception(f"Unknown device type: {input.device_type}")

        return convert_device_to_graphql(device)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_device(self, info: Info, id: int, input: UpdateDeviceInput) -> DeviceUnion:
        """Update an existing device."""
        user = info.context.user

        try:
            device = Device.objects.get(id=id, user=user)
        except Device.DoesNotExist:
            raise Exception("Device not found or you don't have permission to update it")

        # Update common fields
        if input.name is not None:
            device.name = input.name
        if input.status is not None:
            device.status = input.status.value

        device.save()

        # Update device-specific fields
        specific_device = device.get_specific_device()

        if input.current_charge_kwh is not None:
            if hasattr(specific_device, 'current_charge_kwh'):
                specific_device.current_charge_kwh = input.current_charge_kwh
                specific_device.save()

        if input.mode is not None:
            if hasattr(specific_device, 'mode'):
                specific_device.mode = input.mode.value
                specific_device.save()

        return convert_device_to_graphql(device)
