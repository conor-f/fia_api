import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from fia_api.db.models.user_details_model import UserDetailsModel
from fia_api.db.models.user_model import UserModel


# noqa: WPS432
@pytest.mark.anyio
async def test_create_user(fastapi_app: FastAPI, client: AsyncClient) -> None:
    """
    Tests that create user route works.

    :param fastapi_app: current application.
    :param client: client for the app.
    """
    url = fastapi_app.url_path_for("create_user")

    username = str(uuid.uuid4())
    password = str(uuid.uuid4())

    response = await client.post(
        url,
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 201
    created_user = await UserModel.filter(username=username)
    assert len(created_user) == 1
    assert created_user[0].password_hash == password
    assert created_user[0].is_fully_registered is False

    user_details = await UserDetailsModel.filter(user_id=created_user[0])
    assert len(user_details) == 1
    assert user_details[0].times_logged_in == 0
