"""GraphQL types for energy statistics."""

import strawberry
from typing import List


@strawberry.type
class CurrentStorageType:
    """Current storage state across all batteries and EVs."""
    total_capacity_wh: float
    current_level_wh: float
    percentage: float


@strawberry.type
class EnergyStatsType:
    """Real-time energy statistics for a user."""
    current_production: float  # Total watts being produced
    current_consumption: float  # Total watts being consumed
    current_storage: CurrentStorageType  # Storage state
    current_storage_flow: float  # Watts flowing to/from storage (+ charging, - discharging)
    net_grid_flow: float  # Watts to/from grid (+ importing, - exporting)
