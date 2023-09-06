import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient


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
) -> None:
    """
    Tests that conversation routes work.

    :param fastapi_app: current application.
    :param client: client for the app.
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
    response = await client.post(
        converse_url,
        headers=auth_headers,
        json={
            "conversation_id": "new",
            "message": "Hallo, Wie Geht's?",
        },
    )

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
