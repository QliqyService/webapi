from datetime import datetime
from typing import Optional
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


__all__ = ["SQLAlchemyBase", "LifeCycleMixin"]


class SQLAlchemyBase(DeclarativeBase):
    __abstract__ = True

    id: Mapped[sa.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)

    def __repr__(self):
        return f"<{self.__class__.__name__}: #{self.id}>"

    def to_dict(self, obj: Optional["SQLAlchemyBase"] = None):
        dict_ = {}
        exclude_keys = ("_sa_instance_state",)
        for k, v in (obj or self).__dict__.items():
            if k not in exclude_keys:
                if isinstance(v, SQLAlchemyBase):
                    v = self.to_dict(v)
                dict_[k] = v
        return dict_


class LifeCycleMixin:
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
