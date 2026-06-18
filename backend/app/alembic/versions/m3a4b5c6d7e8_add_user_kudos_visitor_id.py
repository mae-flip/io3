"""Add user kudos visitor id

Revision ID: m3a4b5c6d7e8
Revises: l2a3b4c5d6e7
Create Date: 2026-06-18

"""

from alembic import op
import sqlalchemy as sa

revision = "m3a4b5c6d7e8"
down_revision = "l2a3b4c5d6e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("kudos_visitor_id", sa.String(length=36), nullable=True),
    )
    op.create_index(
        op.f("ix_user_kudos_visitor_id"),
        "user",
        ["kudos_visitor_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_kudos_visitor_id"), table_name="user")
    op.drop_column("user", "kudos_visitor_id")
