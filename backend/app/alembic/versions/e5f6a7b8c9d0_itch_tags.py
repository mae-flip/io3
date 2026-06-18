"""Replace taxonomy tags with itch-sourced tags

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-16

"""

from alembic import op
import sqlalchemy as sa


revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM gametag")
    op.execute("DELETE FROM tag")
    op.drop_constraint("tag_category_id_fkey", "tag", type_="foreignkey")
    op.drop_column("tag", "category_id")
    op.drop_column("tag", "is_active")
    op.drop_column("tag", "description")
    op.add_column("tag", sa.Column("itch_url", sa.String(length=2048), nullable=True))
    op.drop_index("ix_tagcategory_slug", table_name="tagcategory")
    op.drop_table("tagcategory")


def downgrade() -> None:
    op.create_table(
        "tagcategory",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tagcategory_slug", "tagcategory", ["slug"], unique=True)
    op.drop_column("tag", "itch_url")
    op.add_column("tag", sa.Column("description", sa.String(length=500), nullable=True))
    op.add_column(
        "tag",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.add_column("tag", sa.Column("category_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "tag_category_id_fkey", "tag", "tagcategory", ["category_id"], ["id"]
    )
