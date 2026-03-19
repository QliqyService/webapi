from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Path, Query, Request
from loguru import logger as LOGGER
from sqlalchemy import select

from app.db import Database
from app.db.models import UserForm
from app.dependencies.http.exceptions import (
    PermissionDeniedException,
    RequestedDataNotFoundException,
    UnauthorizedUserException,
)
from app.managers import Managers
from app.schemas.users.users import UserSchema
from app.services import Services


OptionalAccessTokenDepends = Annotated[Optional[str], Depends(Services.auth.oauth2_schema)]


def get_access_token(request: Request, access_token: OptionalAccessTokenDepends = None) -> str:
    """
    1) Swagger / curl: берет Bearer токен из Authorization (oauth2_schema)
    2) Browser: если заголовка нет — берет токен из cookie 'access_token'
    """
    if access_token:
        return access_token

    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    raise UnauthorizedUserException("Access token is missing")


AccessTokenDepends = Annotated[str, Depends(get_access_token)]
InvitationID = Annotated[UUID, Path(description="Invitation ID")]
InvitationIDQuery = Annotated[Optional[UUID], Query(description="Invitation ID", alias="invitation_id")]


async def get_current_user_id_by_access_token(access_token: str) -> UUID:
    """Get user id by access token.

    Args:
        access_token (str): access token

    Raises:
        UnauthorizedUserException: if access token is invalid

    Returns:
        UUID: user id
    """
    response = await Services.auth_proxy.get_me(access_token=access_token)
    return response["id"]


async def get_current_user_id(access_token: OptionalAccessTokenDepends) -> Optional[UUID]:
    """Get user id by access token.

    Args:
        access_token (str): access token

    Raises:
        UnauthorizedUserException: if access token is invalid

    Returns:
        UUID: user id
    """
    if access_token is not None:
        try:
            return await get_current_user_id_by_access_token(access_token=access_token)
        except HTTPException:
            return None

    return None


UserID = Annotated[UUID, Depends(get_current_user_id)]


class UserDepends:
    def __init__(self, is_superuser: bool = False):
        self.is_superuser = is_superuser

    async def __call__(self, user_id: UserID, access_token: AccessTokenDepends) -> UserSchema:
        """Get user model.

        Args:
            user_id (Annotated[UUID, Depends): user id (via access token)

        Raises:
            UnauthorizedUserException: if user was not found by its email

        Returns:
            UserSchema: user model
        """
        if not user_id:
            raise UnauthorizedUserException()

        user = await Database.users.get_by_pk(pk=user_id)
        if not user:
            LOGGER.debug("User not found locally, syncing from auth")

            auth_user = await Managers.auth.get_me(access_token=access_token)

            user = await Database.users.create(
                UserSchema(
                    id=auth_user.id,
                    email=auth_user.email,
                    phone=None,
                    first_name=auth_user.first_name,
                    last_name=auth_user.last_name,
                    tg_account=None,
                    tg_username=None,
                    tg_notify_enabled=False,
                    is_superuser=auth_user.is_superuser,
                    is_verified=auth_user.is_verified,
                    notify_email_enabled=False,
                )
            )

        if self.is_superuser and not user.is_superuser:
            raise PermissionDeniedException("User is not a superuser")

        LOGGER.debug("User authenticated: {}", user.email)
        return user


ActiveUserDepends = Annotated[UserSchema, Depends(UserDepends())]


async def get_current_user(access_token: AccessTokenDepends) -> UserSchema:
    return await Managers.auth.get_me(access_token=access_token)


CurrentUserDepends = Annotated[UserSchema, Depends(get_current_user)]


async def get_current_form_by_user_id(
    form_id: UUID,
    current_user: CurrentUserDepends,
) -> UserForm:
    async with Services.database.session() as session:
        result = await session.execute(
            select(UserForm).where(UserForm.id == form_id, UserForm.user_id == current_user.id, UserForm.is_enabled)
        )

        form_db = result.scalar_one_or_none()

    if not form_db:
        raise RequestedDataNotFoundException("Form not found")

    return form_db


CurrentFormDepends = Annotated[UserForm, Depends(get_current_form_by_user_id)]


async def get_public_form(form_id: UUID) -> UserForm:
    async with Services.database.session() as session:
        result = await session.execute(select(UserForm).where(UserForm.id == form_id, UserForm.is_enabled))
        form_db = result.scalar_one_or_none()

    if not form_db:
        raise RequestedDataNotFoundException("Form not found")

    return form_db


PublicFormDepends = Annotated[UserForm, Depends(get_public_form)]
