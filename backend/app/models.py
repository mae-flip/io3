import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import EmailStr
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class GameStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    archived = "archived"


class GameSort(str, enum.Enum):
    latest = "latest"
    title = "title"
    author = "author"
    kudos = "kudos"


class LinkPlatform(str, enum.Enum):
    itch = "itch"
    steam = "steam"
    website = "website"
    other = "other"


class OsPlatform(str, enum.Enum):
    android = "android"
    windows = "windows"
    apple = "apple"
    linux = "linux"
    web = "web"


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    is_active: bool = True
    is_owner: bool = False
    is_moderator: bool = False
    display_name: str | None = Field(default=None, max_length=255)
    itch_user_id: int | None = Field(default=None, unique=True, index=True)
    itch_username: str | None = Field(default=None, unique=True, max_length=255)
    kudos_visitor_id: str | None = Field(default=None, max_length=36, index=True)
    can_submit: bool = False
    submission_eligible_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    profile_links: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="[]"),
    )
    games: list["Game"] = Relationship(
        back_populates="submitter",
        sa_relationship_kwargs={"foreign_keys": "[Game.submitter_id]"},
    )


class UserPublic(SQLModel):
    id: uuid.UUID
    itch_username: str | None = None
    display_name: str | None = None
    is_owner: bool = False
    is_moderator: bool = False
    has_contact_email: bool = False
    contact_email: str | None = None
    created_at: datetime | None = None
    profile_links: list["UserProfileLink"] = Field(default_factory=list)


class UserContactEmailUpdate(SQLModel):
    email: EmailStr = Field(max_length=255)


class UserProfileLink(SQLModel):
    url: str = Field(min_length=1, max_length=2048)
    managed_by_itch: bool = False


class UserProfileLinkUpdate(SQLModel):
    url: str = Field(min_length=1, max_length=2048)


class UserProfileLinksUpdate(SQLModel):
    links: list[UserProfileLinkUpdate] = Field(default_factory=list, max_length=7)


class ModeratorUserPublic(SQLModel):
    id: uuid.UUID
    itch_username: str | None = None
    display_name: str | None = None
    is_moderator: bool = False
    is_owner: bool = False
    created_at: datetime | None = None


class ModeratorUsersPublic(SQLModel):
    data: list[ModeratorUserPublic]
    count: int


class ModeratorUserUpdate(SQLModel):
    is_moderator: bool


class TagPublic(SQLModel):
    id: uuid.UUID
    name: str
    slug: str
    itch_url: str | None = None
    is_genre: bool = False


class PlatformPublic(SQLModel):
    platform: OsPlatform
    name: str


class TagsPublic(SQLModel):
    data: list[TagPublic]
    count: int


class GameKudos(SQLModel, table=True):
    user_id: uuid.UUID = Field(
        foreign_key="user.id", primary_key=True, ondelete="CASCADE"
    )
    game_id: uuid.UUID = Field(
        foreign_key="game.id", primary_key=True, ondelete="CASCADE"
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class GameAnonymousKudos(SQLModel, table=True):
    __tablename__ = "game_anonymous_kudos"

    visitor_id: str = Field(primary_key=True, max_length=36)
    game_id: uuid.UUID = Field(
        foreign_key="game.id", primary_key=True, ondelete="CASCADE"
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class GameItchCache(SQLModel, table=True):
    __tablename__ = "game_itch_cache"

    game_id: uuid.UUID = Field(
        foreign_key="game.id", primary_key=True, ondelete="CASCADE"
    )
    title: str | None = Field(default=None, max_length=255)
    summary: str | None = Field(default=None, max_length=500)
    cover_image_url: str | None = Field(default=None, max_length=2048)
    author_name: str | None = Field(default=None, max_length=255)
    author_url: str | None = Field(default=None, max_length=2048)
    tags: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="[]"),
    )
    platforms: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default="[]"),
    )
    price_cents: int | None = Field(default=None)
    price_currency: str | None = Field(default=None, max_length=3)
    fetched_at: datetime = Field(
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    fetch_error: str | None = Field(default=None, max_length=1000)
    game: "Game" = Relationship(back_populates="itch_cache")


class GameLinkPublic(SQLModel):
    id: uuid.UUID
    url: str
    platform: LinkPlatform = LinkPlatform.itch
    is_primary: bool = True
    normalized_url: str


class GameCreate(SQLModel):
    url: str = Field(min_length=1, max_length=2048)


class GameUpdate(SQLModel):
    url: str | None = Field(default=None, min_length=1, max_length=2048)


class Game(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    slug: str = Field(min_length=1, max_length=255, unique=True, index=True)
    itch_url: str = Field(max_length=2048, unique=True, index=True)
    status: GameStatus = Field(default=GameStatus.pending)
    submitter_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    reviewed_by_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", nullable=True, ondelete="SET NULL"
    )
    reviewed_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    rejection_reason: str | None = Field(default=None, max_length=1000)
    removal_reason: str | None = Field(default=None, max_length=1000)
    duplicate_title_warning: bool = False
    kudos_count: int = 0
    featured_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
        index=True,
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    submitter: User | None = Relationship(
        back_populates="games",
        sa_relationship_kwargs={"foreign_keys": "[Game.submitter_id]"},
    )
    itch_cache: "GameItchCache" = Relationship(
        back_populates="game",
        sa_relationship_kwargs={"uselist": False},
        cascade_delete=True,
    )


class SubmitBatchItemStatus(str, enum.Enum):
    submitted = "submitted"
    duplicate = "duplicate"
    not_owned = "not_owned"
    still_listed = "still_listed"
    not_public = "not_public"
    removed_by_moderator = "removed_by_moderator"
    error = "error"


class GameSubmitBatch(SQLModel):
    urls: list[str] = Field(min_length=1, max_length=50)
    itch_access_token: str = Field(min_length=1, max_length=2048)


class SubmitBatchResultItem(SQLModel):
    url: str
    status: SubmitBatchItemStatus
    game: "GamePublic | None" = None
    detail: str | None = None


class SubmitBatchResponse(SQLModel):
    results: list[SubmitBatchResultItem]
    submitted_count: int
    skipped_count: int


class ItchGamePublic(SQLModel):
    id: int
    title: str
    url: str
    cover_url: str | None = None
    short_text: str | None = None
    published: bool = True
    classification: str = "game"
    normalized_url: str | None = None
    already_indexed: bool = False
    removed_by_moderator: bool = False
    removal_reason: str | None = None
    itch_search_listed: bool = False
    publicly_viewable: bool = True


class ItchAuthorizeResponse(SQLModel):
    authorize_url: str
    state: str


class ItchAuthCallback(SQLModel):
    access_token: str = Field(min_length=1, max_length=2048)
    state: str = Field(min_length=1, max_length=512)


class ItchAuthResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
    games: list[ItchGamePublic]
    itch_username: str


class GamePublic(SQLModel):
    id: uuid.UUID
    slug: str
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    cover_image_url: str | None = None
    status: GameStatus
    submitter_id: uuid.UUID
    submitter_itch_username: str | None = None
    submitter_profile_links: list["UserProfileLink"] = Field(default_factory=list)
    reviewed_at: datetime | None = None
    rejection_reason: str | None = None
    duplicate_title_warning: bool = False
    kudos_count: int = 0
    featured_at: datetime | None = None
    author_name: str | None = None
    author_url: str | None = None
    has_kudos: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    links: list[GameLinkPublic] = []
    tags: list[TagPublic] = []
    platforms: list[PlatformPublic] = []
    price_cents: int | None = None
    price_currency: str | None = None


class GamesPublic(SQLModel):
    data: list[GamePublic]
    count: int


class AdminGamePublic(SQLModel):
    id: uuid.UUID
    itch_url: str
    title: str | None = None
    status: GameStatus
    featured_at: datetime | None = None
    removal_reason: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AdminGamesPublic(SQLModel):
    data: list[AdminGamePublic]
    count: int


class GameReject(SQLModel):
    rejection_reason: str = Field(min_length=1, max_length=1000)


class GameRemove(SQLModel):
    removal_reason: str = Field(min_length=1, max_length=1000)


class ItchTagPreview(SQLModel):
    name: str
    slug: str
    itch_url: str
    is_genre: bool = False


class ItchMetadataPreview(SQLModel):
    url: str
    title: str | None = None
    summary: str | None = None
    cover_image_url: str | None = None
    author_name: str | None = None
    author_url: str | None = None
    tags: list[ItchTagPreview] = []
    normalized_url: str | None = None


class DuplicateCheckResult(SQLModel):
    url_exists: bool = False
    existing_game_slug: str | None = None
    similar_titles: list[str] = []


class Message(SQLModel):
    message: str


class NewsletterSubscribe(SQLModel):
    email: EmailStr = Field(max_length=255)


class NewsletterSubscriber(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class NewsletterSubscribersPublic(SQLModel):
    count: int


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


