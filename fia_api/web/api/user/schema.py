from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    """Request object for calls to the create user endpoint."""

    username: str
    password: str
    is_fully_registered: bool | None = None


class TokenSchema(BaseModel):
    """Token returned from login."""

    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    """Token passed to authenticated routes."""

    sub: str
    exp: float


class LoginRequest(BaseModel):
    """Request object for calls to the login endpoint."""

    username: str
    password: str


class AuthenticatedUser(BaseModel):
    """A user authenticated through the API."""

    username: str


class UserDetails(BaseModel):
    """A user details."""

    username: str
    times_logged_in: int
    current_language_code: str


class SetUserDetailsRequest(BaseModel):
    """A set user details request."""

    language_code: str
