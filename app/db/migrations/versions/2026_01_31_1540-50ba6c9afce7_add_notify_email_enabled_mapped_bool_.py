"""add notify_email_enabled

Revision ID: 50ba6c9afce7
Revises: 0bb0912895d2
Create Date: 2026-01-31 15:40:00.000000

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "50ba6c9afce7"
down_revision = "0bb0912895d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "notify_email_enabled",
            sa.Boolean(),
            nullable=True,
            server_default=sa.text("false"),
        ),
    )

    op.execute("UPDATE users SET notify_email_enabled = false WHERE notify_email_enabled IS NULL")

    op.alter_column("users", "notify_email_enabled", nullable=False)

    # опционально — убираем дефолт на уровне БД
    op.alter_column("users", "notify_email_enabled", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "notify_email_enabled")
