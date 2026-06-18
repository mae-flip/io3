"""Rename is_superuser to is_owner

Revision ID: l2a3b4c5d6e7
Revises: k1f2a3b4c5d6
Create Date: 2026-06-18

"""

from alembic import op

revision = "l2a3b4c5d6e7"
down_revision = "k1f2a3b4c5d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("user", "is_superuser", new_column_name="is_owner")


def downgrade() -> None:
    op.alter_column("user", "is_owner", new_column_name="is_superuser")
