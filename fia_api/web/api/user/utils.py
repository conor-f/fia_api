import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from loguru import logger
from passlib.context import CryptContext
from pydantic import ValidationError

from fia_api.db.models.conversation_model import (
    ConversationElementModel,
    ConversationElementRole,
)
from fia_api.db.models.user_model import UserModel
from fia_api.settings import settings
from fia_api.web.api.teacher.schema import TeacherResponse
from fia_api.web.api.user.schema import (
    AuthenticatedUser,
    ConversationElement,
    ConversationResponse,
    TeacherConversationElement,
    TokenPayload,
    UserConversationElement,
)

ACCESS_TOKEN_EXPIRY_MINUTES = 30
REFRESH_TOKEN_EXPIRY_MINUTES = 60 * 24 * 7
ALGORITHM = "HS256"


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/api/user/login",
    scheme_name="JWT",
)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    """
    Hashes the password with bcrypt/passlib.

    :param password: String password to hash
    :returns: String of the hashed password
    """
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """
    Compares two strings to see if the plaintext password hashes to hashed_pass.

    :param password: String password
    :param hashed_pass: String hashed password to compare it to
    :returns: Boolean True if the password matches the hash. False otherwise.
    """
    return password_context.verify(password, hashed_pass)


def create_access_token(subject: Union[str, Any]) -> str:
    """
    Creates the string JWT access token.

    :param subject: Not fully sure?
    :returns: The string access token.
    """
    expires_delta = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRY_MINUTES,
    )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    return jwt.encode(to_encode, settings.jwt_secret_key, ALGORITHM)


def create_refresh_token(subject: Union[str, Any]) -> str:
    """
    Creates the string JWT refresh token.

    :param subject: Not fully sure?
    :returns: The string refresh token.
    """
    expires_delta = datetime.utcnow() + timedelta(
        minutes=REFRESH_TOKEN_EXPIRY_MINUTES,
    )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    return jwt.encode(to_encode, settings.jwt_refresh_secret_key, ALGORITHM)


async def get_current_user(token: str = Depends(reuseable_oauth)) -> AuthenticatedUser:
    """
    Given a JWT token of a logged in user, return the AuthenticatedUser object for them.

    :param token: String JWT token to decode.
    :returns: AuthenticatedUser object
    :raises HTTPException: Whenever the token is expired or the credentials are bad.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[ALGORITHM],
        )
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.warning(f"GOT TOKEN DATA: {token_data}")
    user = await UserModel.get(username=token_data.sub)
    logger.warning(f"USER::::: {user}")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return AuthenticatedUser(username=user.username)


async def format_conversation_element(
    conversation_element: Dict[str, str],
) -> Union[TeacherConversationElement, UserConversationElement]:
    """
    Return the correct object.

    :param conversation_element: A dict of the current conversation element.
    :returns: A sensible representation of the conversation element.
    """
    role = ConversationElementRole[conversation_element["role"].lower()]
    if role == ConversationElementRole.SYSTEM:
        return TeacherConversationElement(
            response=TeacherResponse(
                **json.loads(conversation_element["content"]),
            ),
        )

    return UserConversationElement(message=conversation_element["content"])


async def format_conversation_for_response(
    conversation_id: str,
    last: bool = False,
) -> ConversationResponse:
    """
    Returns the ConversationRespone from a conversation_id string.

    :param conversation_id: String conversation_id.
    :param last: Boolean optional if True only return the most recent element instead
                    of the whole conversation.
    :returns: ConversationResponse
    """
    raw_conversation = await ConversationElementModel.filter(
        conversation_id=uuid.UUID(conversation_id),
    ).values()

    if last:
        raw_conversation = [raw_conversation[-1]]

    return ConversationResponse(
        conversation_id=conversation_id,
        conversation=[
            ConversationElement(
                conversation_element=await format_conversation_element(
                    conversation_element,
                ),
            )
            for conversation_element in raw_conversation
        ],
    )
