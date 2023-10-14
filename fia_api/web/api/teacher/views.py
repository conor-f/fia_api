from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from fia_api.db.models.user_model import UserModel
from fia_api.web.api.teacher.schema import (
    ConverseResponse,
    ConverseWithAudioRequest,
    GetAudioRequest,
    TeacherConverseRequest,
)
from fia_api.web.api.teacher.utils import (
    get_audio_stream_from_text,
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
    converse_with_audio_request: ConverseWithAudioRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> ConverseResponse:
    """
    Starts or continues a conversation with the Teacher with audio.

    :param converse_with_audio_request: The request object.
    :param user: The AuthenticatedUser making the request.
    :returns: ConverseResponse of mistakes and conversation.
    """
    # TODO: Should be the same endpoint as above.
    message = await get_text_from_audio(
        converse_with_audio_request.audio_file,
        converse_with_audio_request.language_code,
    )

    if converse_with_audio_request.conversation_id == "new":
        return await initialize_conversation(
            await UserModel.get(username=user.username),
            message,
        )

    return await get_response(
        converse_with_audio_request.conversation_id,
        message,
        await UserModel.get(username=user.username),
    )


@router.post("/get-audio")
def get_audio(
    audio_request: GetAudioRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> StreamingResponse:
    """
    Given some text and metadata, return the mp3.

    :param audio_request: The details of the request.
    :param user: The AuthenticatedUser making the request.
    :returns: GetAudioResponse.
    """
    audio_stream = get_audio_stream_from_text(
        audio_request.text,
        audio_request.language_code,
    )

    return StreamingResponse(
        audio_stream,
        media_type="audio/mpeg",
    )
