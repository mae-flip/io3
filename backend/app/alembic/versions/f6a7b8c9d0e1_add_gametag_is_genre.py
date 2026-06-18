"""Add is_genre flag to game-tag associations

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-06-16

"""

from alembic import op
import sqlalchemy as sa


revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "gametag",
        sa.Column("is_genre", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.alter_column("gametag", "is_genre", server_default=None)


def downgrade() -> None:
    op.drop_column("gametag", "is_genre")
