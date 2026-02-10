"""GraphQL types for users."""

import strawberry


@strawberry.type
class UserType:
    """User type."""
    id: int
    username: str
    email: str


@strawberry.type
class AuthPayload:
    """Authentication response payload."""
    token: str
    user: UserType
