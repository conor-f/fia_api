from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    """Request object for calls to the create user endpoint."""

    username: str
    password: str
    is_fully_registered: bool | None = None
