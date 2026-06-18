"""Add anonymous kudos table

Revision ID: k1f2a3b4c5d6
Revises: j0e1f2a3b4c5
Create Date: 2026-06-18

"""

from alembic import op
import sqlalchemy as sa

revision = "k1f2a3b4c5d6"
down_revision = "j0e1f2a3b4c5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "game_anonymous_kudos",
        sa.Column("visitor_id", sa.String(length=36), nullable=False),
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["game.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("visitor_id", "game_id"),
    )
    op.create_index(
        op.f("ix_game_anonymous_kudos_game_id"),
        "game_anonymous_kudos",
        ["game_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_game_anonymous_kudos_game_id"), table_name="game_anonymous_kudos"
    )
    op.drop_table("game_anonymous_kudos")
