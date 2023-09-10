from datetime import datetime
from typing import List

from pydantic import BaseModel


class Flashcard(BaseModel):
    """Represents a "Flashcard"."""

    id: int
    conversation_id: str
    next_review_date: datetime
    front: str
    back: str
    last_reviewed_date: datetime


class UpdateFlashcardRequest(BaseModel):
    """Request object for updating a flashcard."""

    id: int
    ease: int
    # TODO: Add time taken to answer or other metrics.


class GetFlashcardsResponse(BaseModel):
    """The resposne from the API when Flashcards are gotten."""

    flashcards: List[Flashcard]