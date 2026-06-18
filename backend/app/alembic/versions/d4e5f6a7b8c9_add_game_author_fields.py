"""Add game author fields from itch metadata

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-16

"""

from alembic import op
import sqlalchemy as sa


revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("game", sa.Column("author_name", sa.String(length=255), nullable=True))
    op.add_column("game", sa.Column("author_url", sa.String(length=2048), nullable=True))


def downgrade() -> None:
    op.drop_column("game", "author_url")
    op.drop_column("game", "author_name")
