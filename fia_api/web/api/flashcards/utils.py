import uuid
from typing import Any, Dict, List

from fia_api.db.models.flashcard_model import FlashcardModel
from fia_api.db.models.user_model import UserModel
from fia_api.web.api.flashcards.schema import Flashcard, GetFlashcardsResponse


async def create_flashcard(
    username: str,
    front: str,
    back: str,
    conversation_id: str,
    both_sides: bool = False,
) -> None:
    """
    Create a flashcard given the params.

    :param username: String username the card belongs to.
    :param front: String front of the card.
    :param back: String back of the card.
    :param conversation_id: String conversation_id of the context.
    :param both_sides: Optional boolean, if True create a card front:back and
                        back:front.
    """
    await FlashcardModel.create(
        user=await UserModel.get(username=username),
        front=front,
        back=back,
        conversation_id=uuid.UUID(conversation_id),
    )

    if both_sides:
        await FlashcardModel.create(
            user=await UserModel.get(username=username),
            front=back,
            back=front,
            conversation_id=uuid.UUID(conversation_id),
        )


def format_flashcards_for_response(
    raw_flashcards: List[Dict[str, Any]],
) -> GetFlashcardsResponse:
    """
    Formats dicts into a Pydantic response.

    :param raw_flashcards: The dicts to format.
    :return: The formatted response.
    """
    return GetFlashcardsResponse(
        flashcards=[
            Flashcard(
                id=flashcard["id"],
                conversation_id=str(flashcard["conversation_id"]),
                next_review_date=flashcard["next_review_date"],
                front=flashcard["front"],
                back=flashcard["back"],
                last_reviewed_date=flashcard["last_modified"],
            )
            for flashcard in raw_flashcards
        ],
    )
