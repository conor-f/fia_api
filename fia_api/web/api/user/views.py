from fastapi import APIRouter
from loguru import logger

from fia_api.db.models.user_details_model import UserDetailsModel
from fia_api.db.models.user_model import UserModel
from fia_api.web.api.user.schema import CreateUserRequest

router = APIRouter()


@router.post("/create", status_code=201)  # noqa: WPS432
async def create_user(new_user_request: CreateUserRequest) -> None:
    """
    Creates user model in the database.

    :param new_user_request: new user.
    """
    logger.warning(f"GOT REQUEST: {new_user_request}")
    user_model = await UserModel.create(
        username=new_user_request.username,
        # TODO: Obviously hash this.
        password_hash=new_user_request.password,
    )

    logger.warning(f"CREATED USER {user_model}")

    user_details_model = await UserDetailsModel.create(user_id=user_model)
    logger.warning(f"CREATED DETAILS {user_details_model}")
