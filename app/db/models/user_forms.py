from typing import TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.services.postgresql import LifeCycleMixin, SQLAlchemyBase


if TYPE_CHECKING:
    from .comments import Comment
    from .users import User


class UserForm(SQLAlchemyBase, LifeCycleMixin):
    """UserForm ORM model"""

    __tablename__ = "user_form"

    title: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    description: Mapped[str] = mapped_column(sa.String(256), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(sa.Boolean, nullable=True, default=True)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    qrcode: Mapped[bytes | None] = mapped_column(
        sa.LargeBinary,
        nullable=True,
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="user_form",
        cascade="all, delete-orphan",
    )

    user: Mapped["User"] = relationship("User", back_populates="forms")
