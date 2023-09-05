from fastapi import APIRouter, Depends

from fia_api.db.models.user_model import UserModel
from fia_api.web.api.teacher.schema import (
    TeacherConverseRequest,
    TeacherConverseResponse,
)
from fia_api.web.api.teacher.utils import get_response, initialize_conversation
from fia_api.web.api.user.schema import AuthenticatedUser
from fia_api.web.api.user.utils import get_current_user

router = APIRouter()


@router.post("/converse", response_model=TeacherConverseResponse)
async def converse(
    converse_request: TeacherConverseRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> TeacherConverseResponse:
    """
    Starts or continues a conversation with the Teacher.

    :param converse_request: The request object.
    :param user: The AuthenticatedUser making the request.
    :returns: TeacherConverseResponse of mistakes and conversation.
    """
    if converse_request.conversation_id == "new":
        return await initialize_conversation(
            await UserModel.get(username=user.username),
            converse_request.message,
        )

    return await get_response(
        converse_request.conversation_id,
        converse_request.message,
    )
