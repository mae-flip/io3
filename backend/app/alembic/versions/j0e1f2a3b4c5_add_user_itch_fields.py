"""Add itch OAuth fields to user

Revision ID: j0e1f2a3b4c5
Revises: i9d0e1f2a3b4
Create Date: 2026-06-17

"""

from alembic import op
import sqlalchemy as sa

revision = "j0e1f2a3b4c5"
down_revision = "i9d0e1f2a3b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("itch_user_id", sa.Integer(), nullable=True))
    op.add_column(
        "user", sa.Column("itch_username", sa.String(length=255), nullable=True)
    )
    op.create_index(
        op.f("ix_user_itch_user_id"), "user", ["itch_user_id"], unique=True
    )
    op.create_index(
        op.f("ix_user_itch_username"), "user", ["itch_username"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_itch_username"), table_name="user")
    op.drop_index(op.f("ix_user_itch_user_id"), table_name="user")
    op.drop_column("user", "itch_username")
    op.drop_column("user", "itch_user_id")
