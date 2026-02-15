from enum import StrEnum
from typing import Any, Literal, NoReturn, Optional, TypedDict
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from loguru import logger as LOGGER

from app.dependencies.exceptions import raise_http_exception
from app.dependencies.exceptions.enums import AuthExceptionCode, UsersExceptionCode


LOGIN_RESPONSE_TYPE = TypedDict(
    "LOGIN_RESPONSE_TYPE",
    {
        "access_token": str,
        "token_type": str,
    },
)
REGISTER_RESPONSE_TYPE = TypedDict(
    "REGISTER_RESPONSE_TYPE",
    {
        "id": UUID,
        "email": str,
        "is_active": bool,
        "is_superuser": bool,
        "is_verified": bool,
    },
)
GET_ME_RESPONSE_TYPE = TypedDict(
    "GET_ME_RESPONSE_TYPE",
    {
        "id": UUID,
        "email": str,
        "is_active": bool,
        "is_superuser": bool,
        "is_verified": bool,
    },
)

PATCH_ME_REQUEST_TYPE = TypedDict(
    "PATCH_ME_REQUEST_TYPE",
    {
        "email": str,
        "password": Optional[str],
    },
)


class AuthProxyErrorCode(StrEnum):
    REGISTER_INVALID_PASSWORD = "REGISTER_INVALID_PASSWORD"
    REGISTER_USER_ALREADY_EXISTS = "REGISTER_USER_ALREADY_EXISTS"
    OAUTH_NOT_AVAILABLE_EMAIL = "OAUTH_NOT_AVAILABLE_EMAIL"
    OAUTH_USER_ALREADY_EXISTS = "OAUTH_USER_ALREADY_EXISTS"
    LOGIN_BAD_CREDENTIALS = "LOGIN_BAD_CREDENTIALS"
    LOGIN_USER_NOT_VERIFIED = "LOGIN_USER_NOT_VERIFIED"
    RESET_PASSWORD_BAD_TOKEN = "RESET_PASSWORD_BAD_TOKEN"
    RESET_PASSWORD_INVALID_PASSWORD = "RESET_PASSWORD_INVALID_PASSWORD"
    VERIFY_USER_BAD_TOKEN = "VERIFY_USER_BAD_TOKEN"
    VERIFY_USER_ALREADY_VERIFIED = "VERIFY_USER_ALREADY_VERIFIED"
    UPDATE_USER_EMAIL_ALREADY_EXISTS = "UPDATE_USER_EMAIL_ALREADY_EXISTS"
    UPDATE_USER_INVALID_PASSWORD = "UPDATE_USER_INVALID_PASSWORD"


class AuthProxyClient:
    base_url: str
    timeout: int

    @staticmethod
    def _raise_http_exception(status_code: int, detail: str) -> NoReturn:
        """Raise http exception."""

        if detail not in AuthProxyErrorCode.__members__:
            raise_http_exception(
                status_code=status_code,
                code=AuthExceptionCode.UNKNOWN,
                reason=detail,
            )

        match detail:
            case AuthProxyErrorCode.REGISTER_INVALID_PASSWORD | AuthProxyErrorCode.UPDATE_USER_INVALID_PASSWORD:
                # Password should be at least 3 characters
                raise_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code=AuthExceptionCode.INVALID_PASSWORD,
                    reason="Password validation failed.",
                )
            case AuthProxyErrorCode.REGISTER_USER_ALREADY_EXISTS | AuthProxyErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS:
                # A user with this email already exists.
                raise_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code=UsersExceptionCode.EMAIL_ALREADY_EXISTS,
                    reason="A user with this email already exists.",
                )
            case AuthProxyErrorCode.LOGIN_BAD_CREDENTIALS:
                # Bad credentials
                raise_http_exception(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    code=AuthExceptionCode.BAD_CREDENTIALS,
                    reason="Bad credentials.",
                )
            case AuthProxyErrorCode.RESET_PASSWORD_BAD_TOKEN:
                # Reset password bad token
                raise_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code=AuthExceptionCode.RESET_PASSWORD_BAD_TOKEN,
                    reason="Reset password bad token.",
                )
            case AuthProxyErrorCode.RESET_PASSWORD_INVALID_PASSWORD:
                # Reset password invalid password
                raise_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code=AuthExceptionCode.RESET_PASSWORD_INVALID_PASSWORD,
                    reason="Reset password invalid password.",
                )
            case AuthProxyErrorCode.VERIFY_USER_BAD_TOKEN:
                # Verify user bad token
                raise_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code=AuthExceptionCode.VERIFY_USER_BAD_TOKEN,
                    reason="Verify user bad token.",
                )
            case AuthProxyErrorCode.VERIFY_USER_ALREADY_VERIFIED:
                # Verify user already verified
                raise_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code=AuthExceptionCode.USER_ALREADY_VERIFIED,
                    reason="Verify user already verified.",
                )

    def __init__(self, url: str, timeout: int = 30):
        self.base_url = url
        self.timeout = timeout

    async def _make_request(
        self,
        method: Literal["POST", "GET", "PATCH"],
        path: str,
        headers: Optional[dict] = None,
        query_params: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> tuple[int, dict[str, Any]]:
        """Make request to the API.

        Args:
            method (Literal["POST"]): request method
            path (str): request path
            headers (Optional[dict], optional): request headers. Defaults to None.
            query_params (Optional[dict], optional): request query params. Defaults to None.
            data (Optional[dict], optional): request data. Defaults to None.
            json (Optional[dict], optional): request json. Defaults to None.
        Returns:
            tuple[int, dict[str, Any]]: status code and response
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = self.base_url + path
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=query_params,
                    data=data,
                    json=json,
                )
                if response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
                    LOGGER.warning(
                        f"AuthProxyClient: Status code: {response.status_code}. Details: {response.text}. "
                        "Failed to make request."
                    )
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=response.text,
                    )

                return response.status_code, response.json()
        except httpx.ConnectError as e:
            LOGGER.error("AuthProxyClient: Failed to connect to auth service")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth service is unavailable",
            ) from e
        except httpx.TimeoutException as e:
            LOGGER.error("AuthProxyClient: Request timeout")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth service request timeout",
            ) from e
        except Exception as e:
            LOGGER.exception(f"AuthProxyClient: Unexpected error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth service error",
            ) from e

    async def login(
        self,
        username: str,
        password: str,
        grant_type: Literal["password"] = "password",
        scope: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> LOGIN_RESPONSE_TYPE:
        """Login by user credentials.

        Args:
            username (str): user email
            password (str): user password
            grant_type (Literal["password"], optional): grant type. Defaults to "password".
            scope (Optional[str], optional): scope. Defaults to None.
            client_id (Optional[str], optional): client ID. Defaults to None.
            client_secret (Optional[str], optional): client secret. Defaults to None.
        Returns:
            dict: access token
        """
        path = "/api/v1/auth/login"
        data = dict(
            username=username,
            password=password,
            grant_type=grant_type,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        status_code, response = await self._make_request(
            method="POST",
            path=path,
            headers=headers,
            data=data,
        )

        if status_code == status.HTTP_200_OK:
            return dict(
                access_token=response["access_token"],
                token_type=response["token_type"],
            )

        self._raise_http_exception(
            status_code=status_code,
            detail=response["detail"],
        )

    async def logout(
        self,
        access_token: str,
    ) -> None:
        """Logout user.

        Args:
            access_token (str): access token
        Returns:
            None
        """
        path = "/api/v1/auth/logout"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        await self._make_request(
            method="POST",
            path=path,
            headers=headers,
        )

    async def register(
        self,
        email: str,
        password: str,
        is_auto_verify: bool = False,
    ) -> REGISTER_RESPONSE_TYPE:
        """Register a new user.

        Args:
            email (str): user email
            password (str): user password
            is_auto_verify (bool): auto verify user
        Returns:
            dict: registered user
        """
        path = "/api/v1/auth/register"
        data = dict(
            email=email,
            password=password,
        )
        query_params = {
            "is_auto_verify": is_auto_verify,
        }
        headers = {
            "Content-Type": "application/json",
        }

        status_code, response = await self._make_request(
            method="POST",
            path=path,
            headers=headers,
            query_params=query_params,
            json=data,
        )

        if status_code == status.HTTP_201_CREATED:
            return dict(
                id=response["id"],
                email=response["email"],
                is_active=response["is_active"],
                is_superuser=response["is_superuser"],
                is_verified=is_auto_verify,
            )

        self._raise_http_exception(
            status_code=status_code,
            detail=response["detail"],
        )

    async def request_verify_token(
        self,
        email: str,
    ) -> None:
        """Register a new user.

        Args:
            email (str): user email
        Returns:
            dict: registered user
        """
        path = "/api/v1/auth/request-verify-token"
        data = dict(
            email=email,
        )
        headers = {
            "Content-Type": "application/json",
        }

        status_code, response = await self._make_request(
            method="POST",
            path=path,
            headers=headers,
            json=data,
        )

        if status_code != status.HTTP_202_ACCEPTED:
            self._raise_http_exception(
                status_code=status_code,
                detail=response["detail"],
            )

    async def verify_token(
        self,
        token: str,
    ) -> GET_ME_RESPONSE_TYPE:
        """Verify token.

        Args:
            token (str): token
        Returns:
            dict: user data
        """
        path = "/api/v1/auth/verify"
        data = dict(
            token=token,
        )
        headers = {
            "Content-Type": "application/json",
        }

        status_code, response = await self._make_request(
            method="POST",
            path=path,
            headers=headers,
            json=data,
        )

        if status_code == status.HTTP_200_OK:
            return dict(
                id=response["id"],
                email=response["email"],
                is_active=response["is_active"],
                is_superuser=response["is_superuser"],
                is_verified=response["is_verified"],
            )

        self._raise_http_exception(
            status_code=status_code,
            detail=response["detail"],
        )

    async def forgot_password(
        self,
        email: str,
    ) -> None:
        """Forgot password.

        Args:
            email (str): user email
        Returns:
            None
        """
        path = "/api/v1/auth/forgot-password"
        data = dict(
            email=email,
        )
        headers = {
            "Content-Type": "application/json",
        }

        status_code, response = await self._make_request(
            method="POST",
            path=path,
            headers=headers,
            json=data,
        )

        if status_code != status.HTTP_202_ACCEPTED:
            self._raise_http_exception(
                status_code=status_code,
                detail=response["detail"],
            )

    async def reset_password(
        self,
        token: str,
        password: str,
    ) -> None:
        """Reset password.

        Args:
            token (str): token
            password (str): new password
        Returns:
            None
        """
        path = "/api/v1/auth/reset-password"
        data = dict(
            token=token,
            password=password,
        )
        headers = {
            "Content-Type": "application/json",
        }

        status_code, response = await self._make_request(
            method="POST",
            path=path,
            headers=headers,
            json=data,
        )

        if status_code != status.HTTP_200_OK:
            self._raise_http_exception(
                status_code=status_code,
                detail=response["detail"],
            )

    async def get_me(
        self,
        access_token: str,
    ) -> GET_ME_RESPONSE_TYPE:
        """Get user data.

        Args:
            access_token (str): access token
        Returns:
            dict: user data
        """
        path = "/api/v1/users/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        status_code, response = await self._make_request(
            method="GET",
            path=path,
            headers=headers,
        )

        if status_code == status.HTTP_200_OK:
            return dict(
                id=response["id"],
                email=response["email"],
                is_active=response["is_active"],
                is_superuser=response["is_superuser"],
                is_verified=response["is_verified"],
            )

        self._raise_http_exception(
            status_code=status_code,
            detail=response["detail"],
        )

    async def patch_me(
        self,
        access_token: str,
        data: PATCH_ME_REQUEST_TYPE,
    ) -> GET_ME_RESPONSE_TYPE:
        """Patch user data.

        Args:
            access_token (str): access token
            data (PATCH_ME_REQUEST_TYPE): user data
        Returns:
            dict: user data
        """
        path = "/api/v1/users/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        status_code, response = await self._make_request(
            method="PATCH",
            path=path,
            headers=headers,
            json=data,
        )

        if status_code == status.HTTP_200_OK:
            return dict(
                id=response["id"],
                email=response["email"],
                is_active=response["is_active"],
                is_superuser=response["is_superuser"],
                is_verified=response["is_verified"],
            )

        self._raise_http_exception(
            status_code=status_code,
            detail=response["detail"],
        )

    async def patch_user(
        self,
        access_token: str,
        user_id: UUID,
        data: PATCH_ME_REQUEST_TYPE,
    ) -> GET_ME_RESPONSE_TYPE:
        """Patch user data.

        Args:
            access_token (str): access token
            user_id (UUID): user ID
            data (PATCH_ME_REQUEST_TYPE): user data
        Returns:
            dict: user data
        """
        path = f"/api/v1/users/{user_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        status_code, response = await self._make_request(
            method="PATCH",
            path=path,
            headers=headers,
            json=data,
        )

        if status_code == status.HTTP_200_OK:
            return dict(
                id=response["id"],
                email=response["email"],
                is_active=response["is_active"],
                is_superuser=response["is_superuser"],
                is_verified=response["is_verified"],
            )

        self._raise_http_exception(
            status_code=status_code,
            detail=response["detail"],
        )

    async def perpetual_token_generation(self, user_id: UUID) -> Optional[str]:
        """Generate a perpetual token for the user.

        Args:
            user_id (UUID): User ID for whom the token is generated.

        Returns:
            Optional[str]: The generated perpetual token or None if the request fails.
        """
        path = f"/api/v1/auth/users/{user_id}/perpetual_token_generation"
        headers = {
            "Content-Type": "application/json",
        }

        status_code, response = await self._make_request(
            method="POST",
            path=path,
            headers=headers,
        )

        if status_code == status.HTTP_200_OK:
            return response.get("access_token")

        self._raise_http_exception(
            status_code=status_code,
            detail=response["detail"],
        )
