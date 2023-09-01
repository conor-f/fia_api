from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from fia_api.db.models.user_details_model import UserDetailsModel
from fia_api.db.models.user_model import UserModel
from fia_api.web.api.user.schema import (
    AuthenticatedUser,
    CreateUserRequest,
    DeleteUserRequest,
    TokenSchema,
    UserDetails,
)
from fia_api.web.api.user.utils import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_hashed_password,
    verify_password,
)

router = APIRouter()


@router.post("/create", status_code=201)  # noqa: WPS432
async def create_user(new_user_request: CreateUserRequest) -> None:
    """
    Creates user model in the database.

    :param new_user_request: new user.
    :raises HTTPException: When a username already exists
    """
    if await UserModel.exists(username=new_user_request.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already exists",
        )

    user_model = await UserModel.create(
        username=new_user_request.username,
        password_hash=get_hashed_password(new_user_request.password),
    )

    await UserDetailsModel.create(user_id=user_model)


@router.post("/delete", status_code=200)  # noqa: WPS432
async def delete_user(delete_user_request: DeleteUserRequest) -> None:
    """
    Delete user model in the database.

    :param delete_user_request: The user to delete.
    """
    user = await UserModel.get(username=delete_user_request.username)
    await user.delete()


@router.post("/login", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenSchema:
    """
    Handles login.

    :param form_data: x-www-form-urlencoded username + password
    :returns: TokenSchema
    :raises HTTPException: For incorrect username/password
    """
    user = await UserModel.get(username=form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    user_details = await UserDetailsModel.get(user_id=user.id)
    user_details.times_logged_in += 1
    await user_details.save()

    return TokenSchema(
        access_token=create_access_token(user.username),
        refresh_token=create_refresh_token(user.username),
    )


@router.get(
    "/view-details",
    summary="Get details of currently logged in user",
    response_model=UserDetails,
)
async def get_user_details(
    user: AuthenticatedUser = Depends(get_current_user),
) -> UserDetails:
    """
    Returns the logged in user's details.

    :param user: AuthenticatedUser
    :returns: UserDetails
    """
    user_model = await UserModel.get(username=user.username)
    user_details = await UserDetailsModel.get(user_id=user_model.id)

    return UserDetails(
        username=user.username,
        times_logged_in=user_details.times_logged_in,
    )
