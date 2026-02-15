import re
from typing import Any

from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo


PASSWORD_REGEX = re.compile(r"[\w!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_{|}~`]{6,}")


def make_strip_validator(*field_names: str):
    """
    - обрезает пробелы у строк (strip)
    Работает для одного или нескольких полей.
    """

    @field_validator(*field_names, mode="before", check_fields=False)
    @classmethod
    def _strip_strings(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    return _strip_strings


def make_lowercase_validator(*field_names: str):
    """
    Приводит строки к lowercase (email и т.п.)
    """

    @field_validator(*field_names)
    @classmethod
    def _lowercase(cls, v: str) -> str:
        return v.lower()

    return _lowercase


def make_password_validator(
    field_name: str,
    *,
    forbid_email: bool = False,
):
    """
    Валидатор пароля:
    - минимум 6 символов
    - допустимые символы
    - опционально: запрет на вхождение email
    """

    @field_validator(field_name)
    @classmethod
    def _validate_password(cls, v: str, info: ValidationInfo) -> str:
        if not PASSWORD_REGEX.match(v):
            raise ValueError("Password should be at least 6 characters and contain only allowed symbols")

        if forbid_email and "email" in info.data:
            if info.data["email"] in v:
                raise ValueError("Password should not contain email")

        return v

    return _validate_password


def make_phone_length_validator(field_name: str, max_length: int):
    """
    Валидатор длины номера телефона.
    """

    @field_validator(field_name, check_fields=False)
    @classmethod
    def _validate_phone(cls, v: int | None) -> int | None:
        if v and len(str(v)) > max_length:
            raise ValueError("Invalid phone number!")
        return v

    return _validate_phone
