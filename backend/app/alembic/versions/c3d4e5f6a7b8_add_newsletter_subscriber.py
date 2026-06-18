"""Add newsletter subscriber table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-16

"""

from alembic import op
import sqlalchemy as sa


revision = "c3d4e5f6a7b8"  # manually assigned during initial io3 migration
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "newslettersubscriber",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_newslettersubscriber_email", "newslettersubscriber", ["email"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_newslettersubscriber_email", table_name="newslettersubscriber")
    op.drop_table("newslettersubscriber")
