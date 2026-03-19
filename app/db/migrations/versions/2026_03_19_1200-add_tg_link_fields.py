"""add tg link fields

Revision ID: 9f8a2f7d10aa
Revises: a1fb10af1d4e
Create Date: 2026-03-19 12:00:00.000000+00:00

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "9f8a2f7d10aa"
down_revision = "a1fb10af1d4e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("tg_username", sa.String(length=255), nullable=True))
    op.add_column(
        "users",
        sa.Column("tg_notify_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "tg_notify_enabled", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "tg_notify_enabled")
    op.drop_column("users", "tg_username")
