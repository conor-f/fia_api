from typing import List

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


class ConversationSnippet(BaseModel):
    """A simple preview of a conversation."""

    conversation_id: str
    conversation_intro: str


class UserConversationList(BaseModel):
    """A list of a user's conversations with the conversation ID and details."""

    conversations: List[ConversationSnippet]


class ConversationLine(BaseModel):
    """A single line of a conversation."""

    role: str
    content: str


class UserConversationResponse(BaseModel):
    """A conversation a user had."""

    conversation: List[ConversationLine]
