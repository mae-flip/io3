"""Remove unused iOS platform rows

Revision ID: h8c9d0e1f2a3
Revises: g7b8c9d0e1f2
Create Date: 2026-06-17

"""

from alembic import op


revision = "h8c9d0e1f2a3"
down_revision = "g7b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM gameosplatform WHERE platform = 'ios'")


def downgrade() -> None:
    pass
