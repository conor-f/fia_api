from typing import List

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
