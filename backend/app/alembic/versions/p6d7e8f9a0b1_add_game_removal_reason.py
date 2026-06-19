"""Add removal_reason to game

Revision ID: p6d7e8f9a0b1
Revises: o5c6d7e8f9a0
Create Date: 2026-06-18

"""

import sqlalchemy as sa
from alembic import op

revision = "p6d7e8f9a0b1"
down_revision = "o5c6d7e8f9a0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "game",
        sa.Column("removal_reason", sa.String(length=1000), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("game", "removal_reason")
