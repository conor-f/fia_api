from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from fia_api.db.models.flashcard_model import FLASHCARD_EASE, FlashcardModel
from fia_api.db.models.user_model import UserModel
from fia_api.web.api.flashcards.schema import (
    DeleteFlashcardRequest,
    GetFlashcardsResponse,
    UpdateFlashcardRequest,
)
from fia_api.web.api.flashcards.utils import format_flashcards_for_response
from fia_api.web.api.user.schema import AuthenticatedUser
from fia_api.web.api.user.utils import get_current_user

router = APIRouter()


@router.post("/update-flashcard", status_code=200)  # noqa: WPS432
async def update_flashcard(
    flashcard_update_request: UpdateFlashcardRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> None:
    """
    Updates a Flashcard with the user feedback.

    :param flashcard_update_request: The request object.
    :param user: The AuthenticatedUser making the request.
    :raises HTTPException: For no matching flashcard.
    """
    flashcard = await FlashcardModel.get(id=flashcard_update_request.id)

    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="flashcard not found",
        )

    # Time to next review date in seconds.
    time_to_next_review = 60 + (
        flashcard.last_review_interval * FLASHCARD_EASE[flashcard_update_request.ease]
    )

    flashcard.next_review_date = datetime.utcnow() + timedelta(
        seconds=time_to_next_review,
    )
    flashcard.last_review_interval = int(time_to_next_review)
    await flashcard.save()


@router.get("/get-flashcards", response_model=GetFlashcardsResponse)
async def get_flashcards(
    only_due: bool = False,
    limit: int = 0,
    user: AuthenticatedUser = Depends(get_current_user),
) -> GetFlashcardsResponse:
    """
    Gets flashcards associated with a user.

    Optional params let you only return N cards or only due cards.

    :param only_due: If True, only return the flashcards needing review.
    :param limit: The max number of flashcards to return.
    :param user: The AuthenticatedUser making the request.
    :returns: GetFlashcardsResponse of all flashcards requested.
    """
    user_model = await UserModel.get(username=user.username)
    flashcards_qs = FlashcardModel.filter(user=user_model)

    if only_due:
        flashcards_qs = flashcards_qs.filter(next_review_date__lt=datetime.utcnow())

    if limit > 0:
        flashcards_qs = flashcards_qs.limit(limit)

    raw_flashcards = await flashcards_qs.values()

    return format_flashcards_for_response(raw_flashcards)


@router.post("/delete-flashcard", status_code=200)  # noqa: WPS432
async def delete_flashcard(
    delete_flashcard_request: DeleteFlashcardRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> None:
    """
    Delete the flashcard associated with a user.

    TODO: Ensure the flashcard is associated with the user logged in.

    :param delete_flashcard_request: The flashcard ID to delete.
    :param user: The AuthenticatedUser making the request.
    :raises HTTPException: For no matching flashcard.
    """
    flashcard = await FlashcardModel.get(id=delete_flashcard_request.id)

    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="flashcard not found",
        )

    await flashcard.delete()
