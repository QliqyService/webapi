from typing import Literal

from pydantic import BaseModel, EmailStr, Field
from app.schemas.base import UUIDModel
from app.schemas.mixins import CreateUpdateAt
from app.schemas.validators import make_phone_length_validator, make_strip_validator


MAX_PHONE_NUMBER_LENGTH = 15


class UserSchema(UUIDModel, CreateUpdateAt):
    email: EmailStr
    phone: int | None = Field(examples=["9876543210"], default=None)
    first_name: str | None = Field(examples=["John"], default=None)
    last_name: str | None = Field(examples=["Doe"], default=None)
    tg_account: str | None = Field(examples=["@telegram"], default=None)
    is_superuser: bool = False
    is_verified: bool = False
    usercode: str | None = Field(examples=["It will be generated"], default=None)
    avatar_key: str | None = None


    # ✅ настройки уведомлений
    notify_email_enabled: bool = False
    notify_email: EmailStr | None = None


class UserPasswordResetSchema(UUIDModel):
    password: str = Field(examples=["password123"])


class UserCreateSchema(BaseModel):
    email: EmailStr
    first_name: str | None = Field(examples=["John"], default=None)
    last_name: str | None = Field(examples=["Doe"], default=None)
    phone: int | None = Field(examples=["9876543210"], default=None)
    tg_account: str | None = Field(examples=["@telegram"], default=None)

    notify_email_enabled: bool = False
    notify_email: EmailStr | None = None

    validate_correct_phone_number = make_phone_length_validator(
        "phone",
        MAX_PHONE_NUMBER_LENGTH,
    )


class UserUpdateSchema(BaseModel):
    email: EmailStr | None = Field(default=None, min_length=5, max_length=100)
    phone: int | None = Field(examples=["9876543210"], default=None)
    first_name: str | None = Field(examples=["John"], default=None, min_length=2, max_length=64)
    last_name: str | None = Field(examples=["Doe"], default=None, min_length=2, max_length=64)
    tg_account: str | None = Field(examples=["@telegram"], default=None)
    avatar_key: str | None = None

    notify_email_enabled: bool | None = None
    notify_email: EmailStr | None = None

    validate_correct_phone_number = make_phone_length_validator(
        "phone",
        MAX_PHONE_NUMBER_LENGTH,
    )
    strip_names = make_strip_validator("first_name", "last_name")


class ProxyCreateUserSchema(UserSchema):
    pass


class CreateUserResponse(UserSchema):
    password: str = Field(examples=["password123"])


class GetByEmailResponse(BaseModel):
    state: Literal["not_found", "exists", "free"] = "not_found"
    user: UserSchema | None = None
