import uuid
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

    # Begin conversation:
    api_response = OpenAIAPIResponse(
        choices=[
            OpenAIAPIChoices(
                message=OpenAIAPIMessage(
                    role="assistant",
                    function_call=OpenAIAPIFunctionCall(
                        name="get_answer_for_user_query",
                        arguments='{\n  "translated_words": [\n    {\n "word": "Hallo",\n      "translated_word": "Hello"\n },\n    {\n      "word": "Wie",\n      "translated_word": "How"\n    },\n    {\n      "word": "Geht",\n "translated_word": "is going"\n    },\n    {\n "word": "s",\n "translated_word": "it"\n }\n  ],\n  "mistakes": [],\n "conversation_response": "Mir geht es gut, danke. Wie kann ich Ihnen helfen?"\n}',  # noqa: E501
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
    if False:
        mocker.patch(
            "fia_api.web.api.teacher.utils.get_openai_response",
            return_value=api_response,
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
    assert conversation[0]["conversation_element"]["role"] == "teacher"

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
    assert conversation[0]["conversation_element"]["role"] == "teacher"

    # Now get conversation:
    response = await client.get(
        get_conversation_url,
        headers=auth_headers,
        params={
            "conversation_id": conversation_id,
        },
    )
    assert len(response.json()["conversation"]) == 4
