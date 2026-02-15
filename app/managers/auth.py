from uuid import UUID

from fastapi import status
from loguru import logger as LOGGER

from app.db import Database, UsersDb
from app.dependencies.exceptions import raise_http_exception
from app.dependencies.exceptions.enums import AuthExceptionCode, UsersExceptionCode
from app.schemas.auth import LoginResponse, PostUserRegisterRequest, PostUserRegisterResponse
from app.schemas.users.users import UserSchema
from app.services import Services


class AuthManager:
    """Authorization manager"""

    @staticmethod
    async def login(email: str, password: str) -> LoginResponse:
        """Logic of endpoint POST `/auth/login`

        Args:
            email (str): user email
            password (str): user password
        Returns:
            LoginResponse: access token
        """

        response = await Services.auth_proxy.login(username=email, password=password)
        LOGGER.debug("User authenticated: {}", email)
        return LoginResponse.model_validate(response)

    @staticmethod
    async def logout(access_token: str) -> None:
        """Logic of endpoint POST `/auth/logout`

        Args:
            access_token (str): access token
        """

        await Services.auth_proxy.logout(access_token=access_token)

    @staticmethod
    async def register(data: PostUserRegisterRequest) -> PostUserRegisterResponse:
        """Logic of endpoint POST `/auth/register`
        Register a new user.
            1. Creates the user in the external Auth service,
               which returns the generated user ID.
            2. Creates a local user record in the WebAPI database using the same ID
               to keep internal relations.
        """

        is_verified = False

        response = await Services.auth_proxy.register(
            email=data.email,
            password=data.password,
            is_auto_verify=is_verified,
        )
        user_id = UUID(response["id"])

        user_for_webapi = UserSchema(
            id=user_id,
            email=data.email,
            phone=None,
            first_name=getattr(data, "first_name", None),
            last_name=getattr(data, "last_name", None),
            is_superuser=False,
            is_verified=is_verified,
        )

        await UsersDb().create(user=user_for_webapi)
        return PostUserRegisterResponse(id=user_id)

    @staticmethod
    async def request_verify_token(email: str) -> None:
        """Logic of endpoint POST `/auth/request_verify_token`

        Args:
            email (str): user email
        """

        user_db = await Database.users.get_by_email(email=email)
        if not user_db:
            raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                code=UsersExceptionCode.NOT_FOUND,
                reason="User not found",
            )
        if user_db.is_verified:
            raise_http_exception(
                status_code=status.HTTP_400_BAD_REQUEST,
                code=AuthExceptionCode.USER_ALREADY_VERIFIED,
                reason="User already verified",
            )

        await Services.auth_proxy.request_verify_token(email=email)
        LOGGER.debug("Verification email sent: {}", email)

    @staticmethod
    async def verify_token(token: str) -> UserSchema:
        """Logic of endpoint POST `/auth/verify_token`

        Args:
            token (str): verification token
        Returns:
            UserSchema: verified user
        """

        response = await Services.auth_proxy.verify_token(token=token)

        user = await Database.users.update_verified(user_id=response["id"], is_verified=True)
        LOGGER.debug("User verified: {}", user.email)
        return user

    @staticmethod
    async def forgot_password(email: str) -> None:
        """Logic of endpoint POST `/auth/forgot_password`

        Args:
            email (str): user email
        """

        user_db = await Database.users.get_by_email(email=email)
        if not user_db:
            raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                code=UsersExceptionCode.NOT_FOUND,
                reason="User not found",
            )

        await Services.auth_proxy.forgot_password(email=email)
        LOGGER.debug("Forgot password email sent: {}", email)

    @staticmethod
    async def reset_password(token: str, new_password: str) -> None:
        """Logic of endpoint POST `/auth/reset_password`

        Args:
            token (str): verification token
            new_password (str): new password
        """

        await Services.auth_proxy.reset_password(token=token, password=new_password)
        LOGGER.debug("Password reset: {}", token)

    @staticmethod
    async def get_me(access_token: str) -> UserSchema:
        """Получить текущего пользователя по access_token через auth-сервис"""

        response = await Services.auth_proxy.get_me(access_token=access_token)
        return UserSchema.model_validate(response)
