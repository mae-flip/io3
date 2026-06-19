"""Add itch price fields to game cache

Revision ID: o5c6d7e8f9a0
Revises: n4b5c6d7e8f9
Create Date: 2026-06-18

"""

import sqlalchemy as sa
from alembic import op

revision = "o5c6d7e8f9a0"
down_revision = "n4b5c6d7e8f9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "game_itch_cache",
        sa.Column("price_cents", sa.Integer(), nullable=True),
    )
    op.add_column(
        "game_itch_cache",
        sa.Column("price_currency", sa.String(length=3), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("game_itch_cache", "price_currency")
    op.drop_column("game_itch_cache", "price_cents")
