"""Root GraphQL schema."""

import strawberry
from apps.api.mutations.auth import AuthMutation
from apps.api.mutations.device import DeviceMutation
from apps.api.queries.device import DeviceQuery
from apps.api.queries.energy import EnergyQuery


@strawberry.type
class Query(DeviceQuery, EnergyQuery):
    """Root query type combining all queries."""
    pass


@strawberry.type
class Mutation(AuthMutation, DeviceMutation):
    """Root mutation type combining all mutations."""
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
