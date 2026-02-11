"""GraphQL types for devices."""

import strawberry
from typing import Optional
from datetime import datetime
from enum import Enum


@strawberry.enum
class DeviceStatusEnum(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


@strawberry.enum
class EVModeEnum(Enum):
    CHARGING = "charging"
    DISCHARGING = "discharging"
    OFFLINE = "offline"


@strawberry.type
class DeviceInterface:
    """Base interface for all devices."""
    id: int
    name: str
    status: DeviceStatusEnum
    device_type: str
    created_at: datetime
    updated_at: datetime


@strawberry.type
class SolarPanelType(DeviceInterface):
    """Solar panel device type."""
    panel_area_m2: float
    efficiency: float
    max_capacity_w: float
    latitude: float
    longitude: float


@strawberry.type
class GeneratorType(DeviceInterface):
    """Generator device type."""
    rated_output_w: float


@strawberry.type
class BatteryType(DeviceInterface):
    """Battery device type."""
    capacity_kwh: float
    current_charge_kwh: float
    max_charge_rate_kw: float
    max_discharge_rate_kw: float
    charge_percentage: float
    current_flow_w: float  # Current power flow: positive = charging, negative = discharging


@strawberry.type
class ElectricVehicleType(DeviceInterface):
    """Electric vehicle device type."""
    capacity_kwh: float
    current_charge_kwh: float
    max_charge_rate_kw: float
    max_discharge_rate_kw: float
    mode: EVModeEnum
    last_seen_at: Optional[datetime]
    driving_efficiency_kwh_per_hour: float
    charge_percentage: float
    current_flow_w: float  # Current power flow: positive = charging, negative = discharging


@strawberry.type
class AirConditionerType(DeviceInterface):
    """Air conditioner device type."""
    rated_power_w: float
    min_power_w: float
    max_power_w: float


@strawberry.type
class HeaterType(DeviceInterface):
    """Heater device type."""
    rated_power_w: float
    min_power_w: float
    max_power_w: float


# Union type for polymorphic device queries
DeviceUnion = strawberry.union(
    "DeviceUnion",
    (SolarPanelType, GeneratorType, BatteryType, ElectricVehicleType, AirConditionerType, HeaterType)
)
