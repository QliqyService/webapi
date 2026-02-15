from uuid import UUID

from pydantic import Field

from app.schemas.base import UUIDModel
from app.schemas.comments import CommentsSchema
from app.schemas.mixins import CreateUpdateAt, StripTitleDescriptionMixin
from app.schemas.users.users import UserSchema


class UserFormSchemaWithoutQrcode(UUIDModel, StripTitleDescriptionMixin, CreateUpdateAt):
    """
    Базовая схема формы пользователя для чтения без qrcode (GET).
    """

    title: str = Field(..., max_length=128, examples=["My new form"])
    user_id: UUID
    description: str | None = Field(..., max_length=256, examples=["There's will be your description"])
    is_enabled: bool = Field(default=True)


class UserFormSchemaWithQrcode(UserFormSchemaWithoutQrcode):
    """
    Базовая схема формы пользователя для чтения c qrcode(GET).
    """

    qrcode: bytes | None = None


class UserFormCreateSchema(StripTitleDescriptionMixin):
    """
    Схема для создания формы (POST).
    """

    title: str = Field(..., max_length=128, examples=["My new form"])
    description: str = Field(..., max_length=256, examples=["My new form"])


class UserFormUpdateSchema(StripTitleDescriptionMixin):
    """
    Схема для частичного обновления формы (PATCH).
    """

    title: str | None = Field(
        default=None,
        max_length=128,
        examples=["New Title"],
    )
    description: str | None = Field(default=None, max_length=256, examples=["New description"])


class UserFormFullSchema(UserFormSchemaWithQrcode):
    """
    Расширенная схема: форма + данные пользователя.
    """

    user: UserSchema
    comments: list[CommentsSchema]
