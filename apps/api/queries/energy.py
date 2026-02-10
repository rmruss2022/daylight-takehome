"""Energy statistics queries."""

import strawberry
from strawberry.types import Info
from apps.api.types.energy_stats import EnergyStatsType, CurrentStorageType
from apps.api.permissions import IsAuthenticated
from apps.simulation.redis_client import RedisClient


@strawberry.type
class EnergyQuery:
    @strawberry.field(permission_classes=[IsAuthenticated])
    def energy_stats(self, info: Info) -> EnergyStatsType:
        """Get current energy statistics for the authenticated user."""
        user = info.context.user
        redis_client = RedisClient()

        # Get aggregated stats from Redis
        stats = redis_client.get_user_stats(user.id)

        if not stats:
            # Return zero stats if no data available yet
            return EnergyStatsType(
                current_production=0.0,
                current_consumption=0.0,
                current_storage=CurrentStorageType(
                    total_capacity_wh=0.0,
                    current_level_wh=0.0,
                    percentage=0.0
                ),
                current_storage_flow=0.0,
                net_grid_flow=0.0
            )

        return EnergyStatsType(
            current_production=stats['current_production'],
            current_consumption=stats['current_consumption'],
            current_storage=CurrentStorageType(
                total_capacity_wh=stats['current_storage']['total_capacity_wh'],
                current_level_wh=stats['current_storage']['current_level_wh'],
                percentage=stats['current_storage']['percentage']
            ),
            current_storage_flow=stats['current_storage_flow'],
            net_grid_flow=stats['net_grid_flow']
        )
