from fastapi import APIRouter, Depends, UploadFile

from fia_api.db.models.user_model import UserModel
from fia_api.web.api.teacher.schema import ConverseResponse, TeacherConverseRequest
from fia_api.web.api.teacher.utils import (
    get_response,
    get_text_from_audio,
    initialize_conversation,
)
from fia_api.web.api.user.schema import AuthenticatedUser
from fia_api.web.api.user.utils import get_current_user

router = APIRouter()


@router.post("/converse", response_model=ConverseResponse)
async def converse(
    converse_request: TeacherConverseRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> ConverseResponse:
    """
    Starts or continues a conversation with the Teacher.

    :param converse_request: The request object.
    :param user: The AuthenticatedUser making the request.
    :returns: ConverseResponse of mistakes and conversation.
    """
    if converse_request.conversation_id == "new":
        return await initialize_conversation(
            await UserModel.get(username=user.username),
            converse_request.message,
        )

    return await get_response(
        converse_request.conversation_id,
        converse_request.message,
        await UserModel.get(username=user.username),
    )


@router.post("/converse-with-audio", response_model=ConverseResponse)
async def converse_with_audio(
    conversation_id: str,
    audio_file: UploadFile,
    user: AuthenticatedUser = Depends(get_current_user),
) -> ConverseResponse:
    """
    Starts or continues a conversation with the Teacher with audio.

    :param conversation_id: The conversation ID being discussed.
    :param audio_file: The file of the recorded audio.
    :param user: The AuthenticatedUser making the request.
    :returns: ConverseResponse of mistakes and conversation.
    """
    message = await get_text_from_audio(audio_file)

    if conversation_id == "new":
        return await initialize_conversation(
            await UserModel.get(username=user.username),
            message,
        )

    return await get_response(
        conversation_id,
        message,
        await UserModel.get(username=user.username),
    )
