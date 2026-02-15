from datetime import datetime
from typing import Annotated, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, model_validator
from sqlalchemy import Row

from app.services.postgresql.sqlalchemy import SQLAlchemyBase


__all__ = ["OrmModel", "UUIDModel", "DateTimeSerialized", "UUIDSerialized", "LifeCycleMixin"]


DateTimeSerialized = Annotated[
    datetime, PlainSerializer(lambda dt: int(dt.timestamp()), return_type=int, when_used="json")
]

UUIDSerialized = Annotated[UUID, PlainSerializer(lambda uuid: str(uuid), return_type=str, when_used="always")]


class OrmModel(BaseModel):
    """ORM model with SQLAlchemy (both ORM and Core) query result mapping
    to Pydantic model via `.model_validate()`."""

    model_config = ConfigDict(from_attributes=True, revalidate_instances="subclass-instances")

    @model_validator(mode="before")
    @classmethod
    def load_object(cls, obj: SQLAlchemyBase | Row | BaseModel | dict) -> dict[str, Any]:
        """Prepare object for valid Pydantic attributes mapping via `.model_validate()`.

        Args:
            obj (SQLAlchemyBase | Row | BaseModel | dict): object to load in Pydantic model.
                1. SQLAlchemyBase - if object is SqlAlchemy ORM model
                2. Row - if object is SqlAlchemy Core query result
                3. BaseModel - if model is created from another Pydantic model.
                4. Dict - if model is created in a usual way via attributes.

        Returns:
            dict[str, Any]: prepared dict to load into Pydantic model
        """
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        parsed: dict[str, Any] = {}
        if isinstance(obj, SQLAlchemyBase):
            parsed.update(obj.__dict__)
            return parsed
        for field, value in obj._asdict().items():
            if isinstance(value, SQLAlchemyBase):
                parsed.update(value.__dict__)
            else:
                parsed[field] = value
        return parsed


class UUIDModel(OrmModel):
    """ORM model with automatic UUID generator for `id` field."""

    id: UUIDSerialized = Field(default_factory=uuid4, examples=["02080e33-b2de-4a63-aad0-c0001bccf62d"])


class LifeCycleMixin(BaseModel):
    created_at: datetime
    updated_at: datetime | None = None
