import uuid

import pytest
from dateutil.parser import parse as dateutil_parse
from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture

from fia_api.web.api.flashcards.utils import create_flashcard

username = str(uuid.uuid4())


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
    global username  # noqa: WPS420

    create_url = fastapi_app.url_path_for("create_user")
    login_url = fastapi_app.url_path_for("login")

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
async def test_flashcards(
    fastapi_app: FastAPI,
    client: AsyncClient,
    mocker: MockerFixture,
) -> None:
    """
    Tests that flashcards routes work.

    :param fastapi_app: current application.
    :param client: client for the app.
    :param mocker: Automatically supplied by pytest to mock objects.
    """
    global username  # noqa: WPS420
    access_token = await get_access_token(fastapi_app, client)
    auth_headers = {
        "Authorization": f"Bearer {access_token}",
    }

    get_flashcards_url = fastapi_app.url_path_for("get_flashcards")
    update_flashcard_url = fastapi_app.url_path_for("update_flashcard")

    # No flashcards by default:
    response = await client.get(
        get_flashcards_url,
        headers=auth_headers,
    )
    assert not response.json()["flashcards"]

    # Create flashcard:
    await create_flashcard(
        username,
        "front of card",
        "back of card",
        str(uuid.uuid4()),
        explanation="Explainer",
    )

    # Now one flashcard
    response = await client.get(
        get_flashcards_url,
        headers=auth_headers,
    )
    assert len(response.json()["flashcards"]) == 1
    assert response.json()["flashcards"][0]["front"] == "front of card"
    assert response.json()["flashcards"][0]["explanation"] == "Explainer"

    original_details = response.json()["flashcards"][0]
    flashcard_id = original_details["id"]

    # Update flashcard:
    response = await client.post(
        update_flashcard_url,
        headers=auth_headers,
        json={
            "id": flashcard_id,
            "ease": 3,
        },
    )
    response = await client.get(
        get_flashcards_url,
        headers=auth_headers,
    )
    new_details = response.json()["flashcards"][0]

    assert dateutil_parse(original_details["next_review_date"]) < dateutil_parse(
        new_details["next_review_date"],
    )

    # Add two more flashcards:
    await create_flashcard(
        username,
        "front 2",
        "back 2",
        str(uuid.uuid4()),
        both_sides=True,
    )

    # Now there are three flashcards:
    response = await client.get(
        get_flashcards_url,
        headers=auth_headers,
    )
    assert len(response.json()["flashcards"]) == 3
