# noqa: WPS462
import json
import uuid
from typing import Any, Dict, List

import openai
from loguru import logger

from fia_api.db.models.conversation_model import (
    ConversationElementModel,
    ConversationElementRole,
)
from fia_api.db.models.learning_moment_model import LearningMomentModel
from fia_api.db.models.token_usage_model import TokenUsageModel
from fia_api.db.models.user_conversation_model import UserConversationModel
from fia_api.db.models.user_model import UserModel
from fia_api.settings import settings
from fia_api.web.api.flashcards.utils import create_flashcard
from fia_api.web.api.teacher.schema import (
    ConversationContinuation,
    ConverseResponse,
    LearningMoments,
    Mistake,
    Translation,
)

openai.api_key = settings.openai_api_key


async def store_token_usage(
    conversation_id: str,
    openai_response: Any,
) -> None:  # type: ignore
    """
    Store the token usage for an OpenAI request.

    :param conversation_id: String to store the usage under
    :param openai_response: The messy openAI datatype
    """
    token_usage_model = await TokenUsageModel.get(
        conversation_id=uuid.UUID(conversation_id),
    )

    token_usage_model.prompt_token_usage += openai_response.usage["prompt_tokens"]
    token_usage_model.completion_token_usage += openai_response.usage[
        "completion_tokens"
    ]

    await token_usage_model.save()


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


async def get_learning_moments_from_message(
    message: str,
    conversation_id: str,
) -> LearningMoments:
    """
    Get LearningMoments from a user message.

    :param message: String message from the user to look for mistakes in.
    :param conversation_id: Store the token usage in the conversation.
    :returns: LearningMoments
    """
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {
                "role": "assistant",
                "content": settings.get_learning_moments_prompt,
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        functions=[
            {
                "name": "get_learning_moments",
                "description": "List all of the mistakes in the user's message and any words in the user message that they would like translated.",  # noqa: E501
                "parameters": LearningMoments.schema(),
            },
        ],
        function_call={"name": "get_learning_moments"},
    )

    await store_token_usage(conversation_id, openai_response)

    return LearningMoments(
        **json.loads(
            openai_response.choices[0].message.function_call.arguments,  # noqa: WPS219
        ),
    )


async def get_conversation_continuation(
    conversation_id: str,
) -> ConversationContinuation:
    """
    Continue the conversation with the user based on the context.

    The conversation in the DB must be updated with the most recent user
    message.

    :param conversation_id: String conversation to continue on.
    :returns: ConversationContinuation
    """
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=await get_messages_from_conversation_id(conversation_id),
        functions=[
            {
                "name": "get_conversation_response",
                "description": "Get the conversational response to the user's message.",
                "parameters": ConversationContinuation.schema(),
            },
        ],
        function_call={"name": "get_conversation_response"},
    )

    await store_token_usage(conversation_id, openai_response)

    return ConversationContinuation(
        **json.loads(
            openai_response.choices[0].message.function_call.arguments,  # noqa: WPS219
        ),
    )


async def create_flashcards_from_learning_moments(
    learning_moments: LearningMoments,
    user: UserModel,
    conversation_id: str,
) -> None:
    """
    Store each learning moment as a flashcard.

    :param learning_moments: LearningMoments to store as flashcards.
    :param user: UserModel to associate with the flashcards.
    :param conversation_id: String conversation ID for context.
    """
    for learning_moment in learning_moments.learning_moments:
        parsed_learning_moment = learning_moment.moment

        if isinstance(parsed_learning_moment, Mistake):
            await create_flashcard(
                user.username,
                parsed_learning_moment.incorrect_section,
                parsed_learning_moment.corrected_section,
                conversation_id,
                explanation=parsed_learning_moment.explanation,
            )
        elif isinstance(parsed_learning_moment, Translation):
            await create_flashcard(
                user.username,
                parsed_learning_moment.phrase,
                parsed_learning_moment.translated_phrase,
                conversation_id,
                both_sides=True,
            )
        else:
            logger.error("Some weirdness going on....")
            logger.error(learning_moment)


async def store_learning_moments(
    user_conversation_element: ConversationElementModel,
    learning_moments: LearningMoments,
) -> None:
    """
    Store learning moments in the DB.

    :param user_conversation_element: ConversationElement these moments are
                                      related to.
    :param learning_moments: The LearningMoments to store in the DB.
    """
    # TODO: These saves can't all be necessary...
    for learning_moment in learning_moments.learning_moments:
        learning_moment_model = LearningMomentModel(
            learning_moment=learning_moment.model_dump_json(),
        )
        await learning_moment_model.save()
        await user_conversation_element.learning_moments.add(learning_moment_model)
        await user_conversation_element.save()


async def get_response(
    conversation_id: str,
    message: str,
    user: UserModel,
) -> ConverseResponse:
    """
    Converse with OpenAI.

    Given the conversation ID, and a new message to add to it, store the
    message, get the response, store that, and return it.

    :param conversation_id: String ID representing the conversation.
    :param message: String message the user wants to send.
    :param user: UserModel, needed to store flashcards.
    :return: ConverseResponse
    """
    user_conversation_element = await ConversationElementModel.create(
        conversation_id=uuid.UUID(conversation_id),
        role=ConversationElementRole.USER,
        content=message,
    )
    await user_conversation_element.save()

    learning_moments = await get_learning_moments_from_message(
        message,
        conversation_id,
    )

    await store_learning_moments(user_conversation_element, learning_moments)

    await create_flashcards_from_learning_moments(
        learning_moments,
        user,
        conversation_id,
    )
    conversation_continuation = await get_conversation_continuation(conversation_id)

    # TODO: Store the learning moments.
    logger.info(learning_moments)

    await ConversationElementModel.create(
        conversation_id=uuid.UUID(conversation_id),
        role=ConversationElementRole.SYSTEM,
        content=conversation_continuation.message,
    )

    return ConverseResponse(
        conversation_id=conversation_id,
        learning_moments=learning_moments,
        conversation_response=conversation_continuation.message,
    )


async def initialize_conversation(
    user: UserModel,
    message: str,
) -> ConverseResponse:
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
        role=ConversationElementRole.ASSISTANT,
        content=settings.conversation_continuation_prompt,
    )

    await UserConversationModel.create(
        user=user,
        conversation_id=conversation_id,
    )

    await TokenUsageModel.create(conversation_id=conversation_id)

    return await get_response(str(conversation_id), message, user)
