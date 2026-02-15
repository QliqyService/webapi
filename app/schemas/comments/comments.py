from pydantic import Field

from app.schemas.base import UUIDModel
from app.schemas.mixins import CreateUpdateAt, PhoneLengthMixin, StripTitleDescriptionMixin


class CommentsSchema(UUIDModel, StripTitleDescriptionMixin, CreateUpdateAt):
    """
    Базовая схема получения комментария на форму (GET).
    """

    first_name: str | None = Field(max_length=32, examples=["My comment"])
    last_name: str | None = Field(max_length=64, examples=["My comment"])
    title: str = Field(..., max_length=128, examples=["My comment"])
    description: str = Field(..., max_length=1024, examples=["My comment"])
    phone: int | None = Field(examples=["9876543210"])


class CommentsCreateSchema(StripTitleDescriptionMixin, PhoneLengthMixin):
    """
    Схема для создания комментария (POST).
    """

    first_name: str | None = Field(max_length=32, examples=["My new comment"])
    last_name: str | None = Field(max_length=64, examples=["My new comment"])
    title: str = Field(..., max_length=128, examples=["My new comment"])
    description: str = Field(..., max_length=1024, examples=["My new comment"])
    phone: int | None = Field(examples=["9876543210"])


class CommentsUpdateSchema(StripTitleDescriptionMixin, PhoneLengthMixin):
    """
    Схема для частичного обновления комментария (PATCH).
    """

    first_name: str | None = Field(max_length=32, examples=["John"], default=None)
    last_name: str | None = Field(max_length=64, examples=["Smith"], default=None)
    title: str | None = Field(max_length=128, examples=["Updated comment"])
    description: str | None = Field(max_length=1024, examples=["Updated comment"])
    phone: int | None = Field(examples=["9876543210"], default=None)
