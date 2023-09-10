import uuid
from loguru import logger
from dataclasses import dataclass
from typing import Dict, List

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture


@dataclass
class OpenAIAPIFunctionCall:
    """Mock class for OpenAI Chat Completion."""

    name: str
    arguments: str


@dataclass
class OpenAIAPIMessage:
    """Mock class for OpenAI Chat Completion."""

    role: str
    function_call: OpenAIAPIFunctionCall


@dataclass
class OpenAIAPIChoices:
    """Mock class for OpenAI Chat Completion."""

    message: OpenAIAPIMessage


@dataclass
class OpenAIAPIResponse:
    """Mock class for OpenAI Chat Completion."""

    choices: List[OpenAIAPIChoices]
    usage: Dict[str, int]


async def get_access_token(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> str:
    """
    Helper method to get an access token for a user.

    :param fastapi_app: current application.
    :param client: client for the app.
    :return: String access token.
    """
    create_url = fastapi_app.url_path_for("create_user")
    login_url = fastapi_app.url_path_for("login")

    username = str(uuid.uuid4())
    password = str(uuid.uuid4())

    # Create User:
    await client.post(
        create_url,
        json={
            "username": username,
            "password": password,
        },
    )

    # Login:
    response = await client.post(
        login_url,
        data={
            "username": username,
            "password": password,
        },
        headers={
            "content-type": "application/x-www-form-urlencoded",
        },
    )

    return response.json()["access_token"]


@pytest.mark.anyio
async def test_conversations(
    fastapi_app: FastAPI,
    client: AsyncClient,
    mocker: MockerFixture,
) -> None:
    """
    Tests that conversation routes work.

    :param fastapi_app: current application.
    :param client: client for the app.
    :param mocker: Automatically supplied by pytest to mock objects.
    """
    access_token = await get_access_token(fastapi_app, client)
    auth_headers = {
        "Authorization": f"Bearer {access_token}",
    }

    list_conversations_url = fastapi_app.url_path_for("list_user_conversations")
    get_conversation_url = fastapi_app.url_path_for("get_user_conversation")
    converse_url = fastapi_app.url_path_for("converse")

    # No conversations by default:
    response = await client.get(
        list_conversations_url,
        headers=auth_headers,
    )
    assert not response.json()["conversations"]

    def get_mocked_openai_response(*args, **kwargs):
        learning_moments_api_response = OpenAIAPIResponse(
            choices=[
                OpenAIAPIChoices(
                    message=OpenAIAPIMessage(
                        role="assistant",
                        function_call=OpenAIAPIFunctionCall(
                            name="get_learning_moments",
                            arguments="{\n  \"learning_moments\": [\n    {\n      \"moment\": {\n        \"incorrect_section\": \"Hallo\",\n        \"corrected_section\": \"Hallo,\",\n        \"explanation\": \"In German, a comma is often used after greetings like 'Hallo' or 'Guten Tag'.\"\n      }\n    },\n    {\n      \"moment\": {\n        \"incorrect_section\": \"Wie Geht's?\",\n        \"corrected_section\": \"Wie geht es dir?\",\n        \"explanation\": \"The correct way to ask 'How are you?' in German is 'Wie geht es dir?'\"\n      }\n    }\n  ]\n}",  # noqa: E501
                        ),
                    ),
                ),
            ],
            usage={
                "prompt_tokens": 181,
                "completion_tokens": 114,
                "total_tokens": 295,
            },
        )
        chat_continuation_api_response = OpenAIAPIResponse(
            choices=[
                OpenAIAPIChoices(
                    message=OpenAIAPIMessage(
                        role="assistant",
                        function_call=OpenAIAPIFunctionCall(
                            name="get_conversation_response",
                            arguments="{\n\"message\": \"Mir geht es gut, danke!  Wie geht es dir?\"\n}",  # noqa: E501
                        ),
                    ),
                ),
            ],
            usage={
                "prompt_tokens": 181,
                "completion_tokens": 114,
                "total_tokens": 295,
            },
        )

        if kwargs["functions"][0]["name"] == "get_learning_moments":
            return learning_moments_api_response
        else:
            return chat_continuation_api_response

    # Begin conversation:
    if True:
        mocker.patch(
            "fia_api.web.api.teacher.utils.openai.ChatCompletion.create",
            side_effect=get_mocked_openai_response
        )
    response = await client.post(
        converse_url,
        headers=auth_headers,
        json={
            "conversation_id": "new",
            "message": "Hallo, Wie Geht's?",
        },
    )

    print(response)
    print(response.json())
    conversation_id = response.json()["conversation_id"]
    conversation = response.json()["conversation"]

    assert conversation_id != "new"
    assert len(conversation) == 1
    assert conversation[0]["role"] == "system"

    # Now one conversation
    response = await client.get(
        list_conversations_url,
        headers=auth_headers,
    )
    assert len(response.json()["conversations"]) == 1
    assert response.json()["conversations"][0]["conversation_id"] == conversation_id

    # Continue conversation:
    response = await client.post(
        converse_url,
        headers=auth_headers,
        json={
            "conversation_id": conversation_id,
            "message": "Es geht mir auch gut",
        },
    )

    assert conversation_id == response.json()["conversation_id"]
    assert len(conversation) == 1
    assert conversation[0]["role"] == "system"

    # Now get conversation:
    response = await client.get(
        get_conversation_url,
        headers=auth_headers,
        params={
            "conversation_id": conversation_id,
        },
    )
    logger.error(response.json())
    assert len(response.json()["conversation"]) == 4
