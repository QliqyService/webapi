from pydantic import BaseModel, EmailStr, Field

from app.schemas.base import UUIDModel
from app.schemas.validators import make_lowercase_validator, make_password_validator, make_strip_validator


class PostUserRegisterRequest(BaseModel):
    email: EmailStr = Field(min_length=5, max_length=100)
    first_name: str = Field(examples=["John"], min_length=2, max_length=20)
    last_name: str | None = Field(examples=["Doe"], default=None, min_length=2, max_length=20)
    password: str = Field(examples=["password123"], min_length=6, max_length=50)

    _strip = make_strip_validator("email", "first_name", "last_name")
    _lowercase_email = make_lowercase_validator("email")
    _password = make_password_validator("password", forbid_email=True)


class PostUserRegisterResponse(UUIDModel):
    pass


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class RequestVerifyTokenSchema(BaseModel):
    email: EmailStr = Field(min_length=5, max_length=100)

    _strip = make_strip_validator("email")
    _lowercase = make_lowercase_validator("email")


class VerifyTokenSchema(BaseModel):
    token: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr = Field(min_length=5, max_length=100)

    _strip = make_strip_validator("email")
    _lowercase = make_lowercase_validator("email")


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str = Field(min_length=6, max_length=50)

    _password = make_password_validator("new_password")
