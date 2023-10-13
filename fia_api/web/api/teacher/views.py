from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse

from fia_api.db.models.user_model import UserModel
from fia_api.web.api.teacher.schema import (
    ConverseResponse,
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
    # TODO: Should be the same endpoint as above.
    # TODO: For some reason POST vars and File uploads are a mess. Fix all of
    # this nonsense.
    #   This is because the conversation_id is passed as a str, not a model.
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


@router.post("/get-audio")
def get_audio(
    audio_request: GetAudioRequest,
    language_code: str,
    user: AuthenticatedUser = Depends(get_current_user),
) -> StreamingResponse:
    """
    Given some text and metadata, return the mp3.

    :param audio_request: The details of the request.
    :param language_code: The language to get the audio in.
    :param user: The AuthenticatedUser making the request.
    :returns: GetAudioResponse.
    """
    audio_stream = get_audio_stream_from_text(audio_request.text, language_code)

    return StreamingResponse(
        audio_stream,
        media_type="audio/mpeg",
    )
