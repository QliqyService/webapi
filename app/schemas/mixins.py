from datetime import datetime

from pydantic import BaseModel

from app.schemas.validators import make_phone_length_validator, make_strip_validator


MAX_PHONE_NUMBER_LENGTH = 15


class StripTitleDescriptionMixin(BaseModel):
    strip_strings = make_strip_validator("title", "description")


class PhoneLengthMixin(BaseModel):
    validate_correct_phone_number = make_phone_length_validator(
        "phone",
        MAX_PHONE_NUMBER_LENGTH,
    )


class CreateUpdateAt(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None
