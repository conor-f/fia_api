from typing import List, Union

from pydantic import BaseModel


# OpenAI Related Response Models:
class Mistake(BaseModel):
    """Represents a "Mistake" that the model found in the user input."""

    mistake_text: str
    fixed_text: str
    explanation: str


class TranslatedWords(BaseModel):
    """Represents a "Translation" that the model was requested to make."""

    word: str
    translated_word: str


class TeacherResponse(BaseModel):
    """Represents the entire response from the "Teacher"."""

    translated_words: List[TranslatedWords]
    mistakes: List[Mistake]
    conversation_response: str


class TeacherConverseRequest(BaseModel):
    """Request object for calls to the Teacher to continue a conversation."""

    # If conversation_id is "new", then start a new conversation.
    conversation_id: str
    message: str


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
