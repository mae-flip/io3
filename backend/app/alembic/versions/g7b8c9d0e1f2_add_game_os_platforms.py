"""Add game OS platform associations

Revision ID: g7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-06-17

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "g7b8c9d0e1f2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None

OS_PLATFORM = postgresql.ENUM(
    "android",
    "windows",
    "apple",
    "linux",
    "ios",
    "web",
    name="osplatform",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(
        "android",
        "windows",
        "apple",
        "linux",
        "ios",
        "web",
        name="osplatform",
    ).create(bind, checkfirst=True)
    op.create_table(
        "gameosplatform",
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column("platform", OS_PLATFORM, nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["game.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("game_id", "platform"),
    )


def downgrade() -> None:
    op.drop_table("gameosplatform")
    bind = op.get_bind()
    postgresql.ENUM(name="osplatform").drop(bind, checkfirst=True)
