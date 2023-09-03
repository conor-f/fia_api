from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from fia_api.db.models.user_details_model import UserDetailsModel
from fia_api.db.models.user_model import UserModel
from fia_api.web.api.user.schema import (
    AuthenticatedUser,
    CreateUserRequest,
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

    user_details_model = await UserDetailsModel.create()

    await UserModel.create(
        username=new_user_request.username,
        password_hash=get_hashed_password(new_user_request.password),
        user_details=user_details_model,
    )


@router.post("/delete", status_code=200)  # noqa: WPS432
async def delete_user(user: AuthenticatedUser = Depends(get_current_user)) -> None:
    """
    Delete user model in the database.

    :param user: The authenticated user to delete.
    """
    user_model = await UserModel.get(username=user.username)
    await user_model.delete()


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

    user_details = await user.user_details.get()
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
    user_details = await user_model.user_details.get()

    return UserDetails(
        username=user_model.username,
        times_logged_in=user_details.times_logged_in,
    )
