# noqa: WPS462
import json
import uuid
from typing import Dict, List

import openai

from fia_api.db.models.conversation_model import (
    ConversationElementModel,
    ConversationElementRole,
)
from fia_api.settings import settings
from fia_api.web.api.teacher import PROMPTS
from fia_api.web.api.teacher.schema import TeacherConverseResponse, TeacherResponse

openai.api_key = settings.openai_api_key


async def get_messages_from_conversation_id(
    conversation_id: str,
) -> List[Dict[str, str]]:
    """
    Given a conversation_id, return a list of dicts ready to pass to OpenAI.

    :param conversation_id: str ID of the conversation
    :return: List of dicts of shape {"role": EnumValue, "content": "message"}
    """
    raw_conversation = await ConversationElementModel.filter(
        conversation_id=uuid.UUID(conversation_id),
    ).values()

    return [
        {
            "role": conversation_element["role"].value,
            "content": conversation_element["content"],
        }
        for conversation_element in raw_conversation
    ]


async def get_response(conversation_id: str, message: str) -> TeacherConverseResponse:
    """
    Converse with OpenAI.

    Given the conversation ID, and a new message to add to it, store the
    message, get the response, store that, and return it.

    :param conversation_id: String ID representing the conversation.
    :param message: String message the user wants to send.
    :return: TeacherResponse
    """
    await ConversationElementModel.create(
        conversation_id=uuid.UUID(conversation_id),
        role=ConversationElementRole.USER,
        content=message,
    )

    chat_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=await get_messages_from_conversation_id(conversation_id),
        functions=[
            {
                "name": "get_answer_for_user_query",
                "description": "Get user language learning mistakes and a sentence to continue the conversation",  # noqa: E501
                "parameters": TeacherResponse.schema(),
            },
        ],
        function_call={"name": "get_answer_for_user_query"},
    )

    teacher_response = chat_response.choices[  # noqa: WPS219
        0
    ].message.function_call.arguments

    await ConversationElementModel.create(
        conversation_id=uuid.UUID(conversation_id),
        role=ConversationElementRole.SYSTEM,
        content=teacher_response,
    )

    # TODO: Store the token usage in the DB...

    return TeacherConverseResponse(
        conversation_id=conversation_id,
        response=json.loads(teacher_response),
    )


async def initialize_conversation(message: str) -> TeacherConverseResponse:
    """
    Starts the conversation.

    Set up the DB with the initial conversation prompt and return the new
    conversation ID, along with the first response from the model.

    :param message: The message to start the conversation with.
    :returns: TeacherConverseResponse of the teacher's first reply.
    """
    conversation_id = uuid.uuid4()

    await ConversationElementModel.create(
        conversation_id=conversation_id,
        role=ConversationElementRole.SYSTEM,
        content=PROMPTS["p3"],
    )

    return await get_response(str(conversation_id), message)
