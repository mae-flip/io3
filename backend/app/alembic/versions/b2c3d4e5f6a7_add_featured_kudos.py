"""Add featured_at to game and game_kudos table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-16

"""

from alembic import op
import sqlalchemy as sa


revision = "b2c3d4e5f6a7"  # manually assigned during initial io3 migration
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "game",
        sa.Column("featured_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_game_featured_at", "game", ["featured_at"])

    op.create_table(
        "gamekudos",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["game.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "game_id"),
    )


def downgrade() -> None:
    op.drop_table("gamekudos")
    op.drop_index("ix_game_featured_at", table_name="game")
    op.drop_column("game", "featured_at")
