"""Replace item with io3 game index models

Revision ID: a1b2c3d4e5f6
Revises: fe56fa70289e
Create Date: 2026-06-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

revision = "a1b2c3d4e5f6"  # manually assigned during initial io3 migration
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None

GAME_STATUS = postgresql.ENUM(
    "pending",
    "approved",
    "rejected",
    "archived",
    name="gamestatus",
    create_type=False,
)
LINK_PLATFORM = postgresql.ENUM(
    "itch",
    "steam",
    "website",
    "other",
    name="linkplatform",
    create_type=False,
)


def upgrade():
    bind = op.get_bind()
    postgresql.ENUM(
        "pending", "approved", "rejected", "archived", name="gamestatus"
    ).create(bind, checkfirst=True)
    postgresql.ENUM("itch", "steam", "website", "other", name="linkplatform").create(
        bind, checkfirst=True
    )

    op.add_column(
        "user",
        sa.Column("is_moderator", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "user",
        sa.Column("display_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    )
    op.add_column(
        "user",
        sa.Column("can_submit", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "user",
        sa.Column("submission_eligible_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "tagcategory",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("slug", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tagcategory_slug"), "tagcategory", ["slug"], unique=True)

    op.create_table(
        "tag",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("slug", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["tagcategory.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tag_slug"), "tag", ["slug"], unique=True)

    op.create_table(
        "game",
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("summary", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=10000), nullable=True),
        sa.Column("cover_image_url", sqlmodel.sql.sqltypes.AutoString(length=2048), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("status", GAME_STATUS, nullable=False),
        sa.Column("submitter_id", sa.Uuid(), nullable=False),
        sa.Column("reviewed_by_id", sa.Uuid(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column("duplicate_title_warning", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("kudos_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["user.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["submitter_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_game_slug"), "game", ["slug"], unique=True)

    op.create_table(
        "gamelink",
        sa.Column("url", sqlmodel.sql.sqltypes.AutoString(length=2048), nullable=False),
        sa.Column("platform", LINK_PLATFORM, nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column("normalized_url", sqlmodel.sql.sqltypes.AutoString(length=2048), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["game.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_gamelink_normalized_url"), "gamelink", ["normalized_url"], unique=True)

    op.create_table(
        "gametag",
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["game.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("game_id", "tag_id"),
    )

    op.drop_table("item")

    op.alter_column("user", "is_moderator", server_default=None)
    op.alter_column("user", "can_submit", server_default=None)
    op.alter_column("game", "duplicate_title_warning", server_default=None)
    op.alter_column("game", "kudos_count", server_default=None)


def downgrade():
    bind = op.get_bind()
    op.create_table(
        "item",
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.drop_table("gametag")
    op.drop_index(op.f("ix_gamelink_normalized_url"), table_name="gamelink")
    op.drop_table("gamelink")
    op.drop_index(op.f("ix_game_slug"), table_name="game")
    op.drop_table("game")
    op.drop_index(op.f("ix_tag_slug"), table_name="tag")
    op.drop_table("tag")
    op.drop_index(op.f("ix_tagcategory_slug"), table_name="tagcategory")
    op.drop_table("tagcategory")

    op.drop_column("user", "submission_eligible_at")
    op.drop_column("user", "can_submit")
    op.drop_column("user", "display_name")
    op.drop_column("user", "is_moderator")

    postgresql.ENUM(name="linkplatform").drop(bind, checkfirst=True)
    postgresql.ENUM(name="gamestatus").drop(bind, checkfirst=True)
