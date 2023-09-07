# noqa: WPS462
import json
import uuid
from typing import Dict, List

import openai
from loguru import logger

from fia_api.db.models.conversation_model import (
    ConversationElementModel,
    ConversationElementRole,
)
from fia_api.db.models.token_usage_model import TokenUsageModel
from fia_api.db.models.user_conversation_model import UserConversationModel
from fia_api.db.models.user_model import UserModel
from fia_api.settings import settings
from fia_api.web.api.teacher.schema import ConversationResponse, TeacherResponse
from fia_api.web.api.user.utils import format_conversation_for_response

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


# Ignoring type as I don't really know what the OpenAI API returns...
async def get_openai_response(conversation_id: str):  # type: ignore
    """
    Wraps the OpenAI API call. Mostly to make mocking easier.

    :param conversation_id: String conversation_id
    :return: OpenAI Chat Response object
    """
    return openai.ChatCompletion.create(
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


async def get_response(conversation_id: str, message: str) -> ConversationResponse:
    """
    Converse with OpenAI.

    Given the conversation ID, and a new message to add to it, store the
    message, get the response, store that, and return it.

    :param conversation_id: String ID representing the conversation.
    :param message: String message the user wants to send.
    :return: ConversationResponse
    """
    await ConversationElementModel.create(
        conversation_id=uuid.UUID(conversation_id),
        role=ConversationElementRole.USER,
        content=message,
    )

    chat_response = await get_openai_response(conversation_id)
    logger.warning("-------------------------")
    logger.warning(chat_response)
    logger.warning("-------------------------")

    # Do this JSON dance to have it serialize correctly.
    teacher_response = json.dumps(
        json.loads(
            chat_response.choices[0].message.function_call.arguments,  # noqa: WPS219
        ),
    )

    await ConversationElementModel.create(
        conversation_id=uuid.UUID(conversation_id),
        role=ConversationElementRole.SYSTEM,
        content=teacher_response,
    )

    token_usage_model = await TokenUsageModel.get(
        conversation_id=uuid.UUID(conversation_id),
    )
    token_usage_model.prompt_token_usage += chat_response.usage["prompt_tokens"]
    token_usage_model.completion_token_usage += chat_response.usage["completion_tokens"]
    await token_usage_model.save()

    return await format_conversation_for_response(
        conversation_id,
        last=True,
    )


async def initialize_conversation(
    user: UserModel,
    message: str,
) -> ConversationResponse:
    """
    Starts the conversation.

    Set up the DB with the initial conversation prompt and return the new
    conversation ID, along with the first response from the model.

    :param user: The user initiating the conversation.
    :param message: The message to start the conversation with.
    :returns: ConversationResponse of the teacher's first reply.
    """
    conversation_id = uuid.uuid4()

    await ConversationElementModel.create(
        conversation_id=conversation_id,
        role=ConversationElementRole.SYSTEM,
        content=settings.prompts["p2"],
    )

    await UserConversationModel.create(
        user=user,
        conversation_id=conversation_id,
    )

    await TokenUsageModel.create(conversation_id=conversation_id)

    return await get_response(str(conversation_id), message)
