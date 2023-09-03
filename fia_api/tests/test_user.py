import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from fia_api.db.models.user_model import UserModel


@pytest.mark.anyio
async def test_create_login_delete_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """
    Tests that create and delete user routes works.

    :param fastapi_app: current application.
    :param client: client for the app.
    """
    create_url = fastapi_app.url_path_for("create_user")
    login_url = fastapi_app.url_path_for("login")
    delete_url = fastapi_app.url_path_for("delete_user")

    username = str(uuid.uuid4())
    password = str(uuid.uuid4())

    response = await client.post(
        create_url,
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 201
    created_user = await UserModel.filter(username=username)
    assert len(created_user) == 1
    assert created_user[0].password_hash != password
    assert created_user[0].is_fully_registered is False

    user_details = await created_user[0].user_details.get()
    assert user_details.times_logged_in == 0

    response = await client.post(
        delete_url,
        json={
            "username": username,
        },
    )
    assert response.status_code == 401

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
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    response = await client.post(
        delete_url,
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    assert response.status_code == 200
    matched_users = await UserModel.filter(username=username)
    assert not matched_users
