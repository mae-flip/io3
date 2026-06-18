"""Live itch URL-only games with metadata cache

Revision ID: i9d0e1f2a3b4
Revises: h8c9d0e1f2a3
Create Date: 2026-06-17

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "i9d0e1f2a3b4"
down_revision = "h8c9d0e1f2a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("game", sa.Column("itch_url", sa.String(length=2048), nullable=True))

    op.create_table(
        "game_itch_cache",
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.String(length=500), nullable=True),
        sa.Column("cover_image_url", sa.String(length=2048), nullable=True),
        sa.Column("author_name", sa.String(length=255), nullable=True),
        sa.Column("author_url", sa.String(length=2048), nullable=True),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "platforms",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fetch_error", sa.String(length=1000), nullable=True),
        sa.ForeignKeyConstraint(["game_id"], ["game.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("game_id"),
    )
    op.create_index(
        "ix_game_itch_cache_tags_gin",
        "game_itch_cache",
        ["tags"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_game_itch_cache_platforms_gin",
        "game_itch_cache",
        ["platforms"],
        postgresql_using="gin",
    )

    op.execute(
        """
        UPDATE game g SET itch_url = sub.normalized_url
        FROM (
            SELECT DISTINCT ON (gl.game_id)
                gl.game_id,
                gl.normalized_url
            FROM gamelink gl
            ORDER BY gl.game_id, gl.is_primary DESC, gl.id
        ) sub
        WHERE sub.game_id = g.id
        """
    )
    op.execute(
        """
        UPDATE game
        SET itch_url = 'https://unknown.itch.io/missing-' || id::text
        WHERE itch_url IS NULL
        """
    )

    op.execute(
        """
        INSERT INTO game_itch_cache (
            game_id, title, summary, cover_image_url,
            author_name, author_url, tags, platforms, fetched_at
        )
        SELECT
            g.id,
            g.title,
            g.summary,
            g.cover_image_url,
            g.author_name,
            g.author_url,
            COALESCE((
                SELECT jsonb_agg(
                    jsonb_build_object(
                        'slug', t.slug,
                        'name', t.name,
                        'itch_url', t.itch_url,
                        'is_genre', gt.is_genre
                    )
                    ORDER BY gt.is_genre DESC, lower(t.name)
                )
                FROM gametag gt
                JOIN tag t ON t.id = gt.tag_id
                WHERE gt.game_id = g.id
            ), '[]'::jsonb),
            COALESCE((
                SELECT jsonb_agg(gp.platform::text ORDER BY gp.platform)
                FROM gameosplatform gp
                WHERE gp.game_id = g.id
            ), '[]'::jsonb),
            NOW()
        FROM game g
        """
    )

    op.drop_column("game", "title")
    op.drop_column("game", "summary")
    op.drop_column("game", "description")
    op.drop_column("game", "cover_image_url")
    op.drop_column("game", "author_name")
    op.drop_column("game", "author_url")

    op.drop_table("gametag")
    op.drop_table("gameosplatform")
    op.drop_table("gamelink")
    op.drop_table("tag")

    op.alter_column("game", "itch_url", nullable=False)
    op.create_index("ix_game_itch_url", "game", ["itch_url"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_game_itch_url", table_name="game")
    op.add_column("game", sa.Column("title", sa.String(length=255), nullable=True))
    op.add_column("game", sa.Column("summary", sa.String(length=500), nullable=True))
    op.add_column(
        "game", sa.Column("description", sa.String(length=10000), nullable=True)
    )
    op.add_column(
        "game", sa.Column("cover_image_url", sa.String(length=2048), nullable=True)
    )
    op.add_column("game", sa.Column("author_name", sa.String(length=255), nullable=True))
    op.add_column("game", sa.Column("author_url", sa.String(length=2048), nullable=True))

    op.execute(
        """
        UPDATE game g SET
            title = COALESCE(c.title, g.slug),
            summary = c.summary,
            cover_image_url = c.cover_image_url,
            author_name = c.author_name,
            author_url = c.author_url
        FROM game_itch_cache c
        WHERE c.game_id = g.id
        """
    )
    op.execute("UPDATE game SET title = slug WHERE title IS NULL")
    op.alter_column("game", "title", nullable=False)

    op.create_table(
        "tag",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("itch_url", sa.String(length=2048), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tag_slug", "tag", ["slug"], unique=True)

    op.create_table(
        "gamelink",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column(
            "platform",
            postgresql.ENUM(
                "itch", "steam", "website", "other", name="linkplatform", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column("normalized_url", sa.String(length=2048), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["game.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gamelink_normalized_url", "gamelink", ["normalized_url"], unique=True)

    op.create_table(
        "gametag",
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.Column("is_genre", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["game.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("game_id", "tag_id"),
    )

    op.create_table(
        "gameosplatform",
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column(
            "platform",
            postgresql.ENUM(
                "android",
                "windows",
                "apple",
                "linux",
                "web",
                name="osplatform",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["game_id"], ["game.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("game_id", "platform"),
    )

    op.execute(
        """
        INSERT INTO gamelink (id, url, platform, is_primary, game_id, normalized_url)
        SELECT gen_random_uuid(), itch_url, 'itch', true, id, itch_url
        FROM game
        """
    )

    op.drop_index("ix_game_itch_cache_platforms_gin", table_name="game_itch_cache")
    op.drop_index("ix_game_itch_cache_tags_gin", table_name="game_itch_cache")
    op.drop_table("game_itch_cache")
    op.drop_column("game", "itch_url")
