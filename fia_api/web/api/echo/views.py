from fastapi import APIRouter

from fia_api.web.api.echo.schema import Message

router = APIRouter()


@router.post("/", response_model=Message)
async def send_echo_message(
    incoming_message: Message,
) -> Message:
    """
    Sends echo back to user.

    :param incoming_message: incoming message.
    :returns: message same as the incoming.
    """
    response_message = incoming_message
    response_message.message = f"Response: {incoming_message.message}"

    return response_message
