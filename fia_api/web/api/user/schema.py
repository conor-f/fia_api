from typing import List, Union

from pydantic import BaseModel

from fia_api.web.api.teacher.schema import TeacherResponse


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

    # If str, then this is just a user response.
    line: Union[TeacherResponse, str]


class UserConversationElement(BaseModel):
    """The user part of the conversation."""

    role: str = "user"
    message: str


class TeacherConversationElement(BaseModel):
    """The teacher response."""

    role: str = "teacher"
    response: TeacherResponse


class ConversationElement(BaseModel):
    """A single part of a conversation. Either from the user or system."""

    conversation_element: Union[TeacherConversationElement, UserConversationElement]


class ConversationResponse(BaseModel):
    """A conversation a user had."""

    conversation_id: str
    conversation: List[ConversationElement]
