from typing import Annotated

from fastapi import Form, status
from pydantic import EmailStr

from app.dependencies.http import AccessTokenDepends
from app.managers import Managers
from app.routers.api.base import Router
from app.schemas.auth import (
    ForgotPasswordSchema,
    LoginResponse,
    PostUserRegisterRequest,
    PostUserRegisterResponse,
    RequestVerifyTokenSchema,
    ResetPasswordSchema,
    VerifyTokenSchema,
)
from app.schemas.users.users import UserSchema


router = Router(
    name="Authentication",
    description="""
All results, except `shared` endpoints and logging in, require a [JWT](https://en.wikipedia.org/wiki/JSON_Web_Token)
token to be provided in the `AUTHORIZATION` header.
This token can be retrieved via the next authentication methods.

> WARNING: This token has the authorization info of the concrete user.
By sharing your token you automatically grant access to the data you possess in the platform.
We highly recommend you neither to share your authorization token nor to provide your credentials!
""",
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=PostUserRegisterResponse,
)
async def register_user(
    data: PostUserRegisterRequest,
):
    """
    Register a new user.

    ### Input
    - **email** [Length from 5 to 100]: user email
    - **first_name** [Length from 2 to 20]: user first name
    - **last_name** [Length from 2 to 20] (Optional): user last name
    - **password** [Length from 6 to 50]: user password.
        Password must not contain email.
        It must be at least 6 alphanumeric characters or following symbols: !@#$%^&*()_+

    ### Output
    - **id** user ID
    - **email**: user email
    - **first_name**: user first name
    - **last_name**: user last name
    """
    return await Managers.auth.register(data=data)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def login(
    username: Annotated[EmailStr, Form(description="User email", min_length=5, max_length=100)],
    password: Annotated[str, Form(description="User password", min_length=6, max_length=50)],
):
    """
    Login by user credentials.

    ### Input
    - **username** [Length from 5 to 100]: user email
    - **password** [Length from 6 to 50]: user password

    ### Output
    - **access_token**: access token
    - **token_type**: token type
    """
    return await Managers.auth.login(
        email=username.lower(),
        password=password,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    access_token: AccessTokenDepends,
):
    """
    Logout from the system.
    """
    return await Managers.auth.logout(access_token=access_token)


@router.post(
    "/request_verify_token",
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_verify_token(
    data: RequestVerifyTokenSchema,
):
    """
    Request a verification token.

    ### Input
    - **email** [Length from 5 to 100]: user email
    """
    return await Managers.auth.request_verify_token(
        email=data.email,
    )


@router.post(
    "/verify_token",
    status_code=status.HTTP_200_OK,
    response_model=UserSchema,
)
async def verify_token(
    data: VerifyTokenSchema,
):
    """
    Verify a user by a token.

    ### Input
    - **token**: verification token
    """
    return await Managers.auth.verify_token(
        token=data.token,
    )


@router.post(
    "/forgot_password",
    status_code=status.HTTP_202_ACCEPTED,
)
async def forgot_password(
    data: ForgotPasswordSchema,
):
    """
    Request a password reset token.

    ### Input
    - **email** [Length from 5 to 100]: user email
    """
    return await Managers.auth.forgot_password(
        email=data.email,
    )


@router.post(
    "/reset_password",
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    data: ResetPasswordSchema,
):
    """
    Reset a user password.

    ### Input
    - **token**: password reset token
    - **new_password** [Length from 6 to 50]: new user password.
        It must be at least 6 alphanumeric characters or following symbols: !@#$%^&*()_+
    """
    return await Managers.auth.reset_password(
        token=data.token,
        new_password=data.new_password,
    )
