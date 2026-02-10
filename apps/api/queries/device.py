"""Device queries."""

import strawberry
from typing import List
from strawberry.types import Info
from apps.devices.models import Device
from apps.api.types.device_types import DeviceUnion
from apps.api.mutations.device import convert_device_to_graphql
from apps.api.permissions import IsAuthenticated


@strawberry.type
class DeviceQuery:
    @strawberry.field(permission_classes=[IsAuthenticated])
    def all_devices(self, info: Info) -> List[DeviceUnion]:
        """Get all devices for the authenticated user."""
        user = info.context.user
        devices = Device.objects.filter(user=user).select_related(
            'solarpanel', 'generator', 'battery', 'electricvehicle',
            'airconditioner', 'heater'
        )

        return [convert_device_to_graphql(device) for device in devices]
