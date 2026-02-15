from typing import TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.services.postgresql import LifeCycleMixin, SQLAlchemyBase


if TYPE_CHECKING:
    from .user_forms import UserForm


class Comment(SQLAlchemyBase, LifeCycleMixin):
    __tablename__ = "comments"
    first_name: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    last_name: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    phone: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True)
    title: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    description: Mapped[str] = mapped_column(sa.String(1024), nullable=False)
    user_form_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        sa.ForeignKey("user_form.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_form: Mapped["UserForm"] = relationship(
        "UserForm",
        back_populates="comments",
    )
