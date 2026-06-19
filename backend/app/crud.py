import secrets
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func as sa_func
from sqlalchemy import text as sa_text
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, func, or_, select

from app.core.config import settings
from app.core.security import get_password_hash
from app.models import (
    AdminGamePublic,
    AdminGamesPublic,
    DuplicateCheckResult,
    Game,
    GameAnonymousKudos,
    GameCreate,
    GameItchCache,
    GameKudos,
    GameSort,
    GameStatus,
    GameUpdate,
    ModeratorUserPublic,
    ModeratorUsersPublic,
    NewsletterSubscriber,
    OsPlatform,
    PlatformPublic,
    TagPublic,
    User,
)
from app.services.itch_cache import (
    tag_id_from_slug,
    upsert_from_metadata,
)
from app.services.itch import fetch_itch_metadata_sync
from app.services.itch_public import NOT_PUBLIC_DETAIL, check_public_viewability_sync
from app.services.platforms import PLATFORM_DISPLAY_ORDER, platform_label
from app.services.slug import unique_game_slug_from_url
from app.services.urls import normalize_itch_url


def user_can_submit(user: User) -> bool:
    return user.is_owner or user.is_moderator or user.can_submit


def _sync_owner_flag(user: User, itch_username: str) -> None:
    if itch_username.lower() == settings.ITCH_OWNER_USERNAME.lower():
        user.is_owner = True


def itch_user_email(itch_user_id: int) -> str:
    return f"itch-{itch_user_id}@example.com"


def user_has_contact_email(user: User) -> bool:
    if user.itch_user_id is None:
        return True
    return user.email != itch_user_email(user.itch_user_id)


def set_user_contact_email(*, session: Session, user: User, email: str) -> User:
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing and existing.id != user.id:
        raise ValueError("This email address is already in use")
    user.email = email
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_itch_user_id(*, session: Session, itch_user_id: int) -> User | None:
    statement = select(User).where(User.itch_user_id == itch_user_id)
    return session.exec(statement).first()


def get_or_create_itch_user(
    *,
    session: Session,
    itch_user_id: int,
    itch_username: str,
    display_name: str | None,
) -> User:
    user = get_user_by_itch_user_id(session=session, itch_user_id=itch_user_id)
    if user:
        user.itch_username = itch_username
        user.display_name = display_name or itch_username
        user.can_submit = True
        _sync_owner_flag(user, itch_username)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    user = User(
        email=itch_user_email(itch_user_id),
        hashed_password=get_password_hash(secrets.token_urlsafe(32)),
        itch_user_id=itch_user_id,
        itch_username=itch_username,
        display_name=display_name or itch_username,
        can_submit=True,
        is_active=True,
    )
    _sync_owner_flag(user, itch_username)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def list_itch_users(
    *, session: Session, skip: int = 0, limit: int = 100
) -> ModeratorUsersPublic:
    count = session.exec(
        select(func.count()).select_from(User).where(col(User.itch_user_id).is_not(None))
    ).one()
    users = session.exec(
        select(User)
        .where(col(User.itch_user_id).is_not(None))
        .order_by(col(User.created_at).desc())
        .offset(skip)
        .limit(limit)
    ).all()
    return ModeratorUsersPublic(
        data=[ModeratorUserPublic.model_validate(user) for user in users],
        count=count,
    )


def update_moderator_status(
    *, session: Session, db_user: User, is_moderator: bool
) -> User:
    db_user.is_moderator = is_moderator
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def find_similar_titles(*, session: Session, title: str) -> list[str]:
    pattern = f"%{title.strip()}%"
    statement = (
        select(GameItchCache.title)
        .where(col(GameItchCache.title).ilike(pattern))
        .limit(5)
    )
    return [row for row in session.exec(statement).all() if row]


def find_game_by_itch_url(*, session: Session, normalized_url: str) -> Game | None:
    statement = select(Game).where(Game.itch_url == normalized_url)
    return session.exec(statement).first()


def tags_public_from_cache(cache: GameItchCache | None) -> list[TagPublic]:
    if not cache:
        return []
    tags = [
        TagPublic(
            id=tag_id_from_slug(tag["slug"]),
            name=tag["name"],
            slug=tag["slug"],
            itch_url=tag.get("itch_url"),
            is_genre=bool(tag.get("is_genre")),
        )
        for tag in cache.tags
    ]
    tags.sort(key=lambda item: (not item.is_genre, item.name.lower()))
    return tags


def platforms_public_from_cache(cache: GameItchCache | None) -> list[PlatformPublic]:
    if not cache:
        return []
    order = {platform: index for index, platform in enumerate(PLATFORM_DISPLAY_ORDER)}
    platforms = [
        PlatformPublic(platform=OsPlatform(value), name=platform_label(OsPlatform(value)))
        for value in cache.platforms
    ]
    platforms.sort(key=lambda item: order.get(item.platform, 99))
    return platforms


def create_game(
    *, session: Session, game_in: GameCreate, submitter_id: uuid.UUID
) -> Game:
    normalized = normalize_itch_url(game_in.url)
    if not normalized:
        raise ValueError("URL must be a valid itch.io game page")

    if find_game_by_itch_url(session=session, normalized_url=normalized):
        raise ValueError(f"Duplicate URL already indexed: {game_in.url}")

    if not check_public_viewability_sync(normalized):
        raise ValueError(NOT_PUBLIC_DETAIL)

    metadata = fetch_itch_metadata_sync(normalized)
    slug = unique_game_slug_from_url(session, normalized)
    duplicate_warning = False
    if metadata.title:
        duplicate_warning = len(
            find_similar_titles(session=session, title=metadata.title)
        ) > 0

    now = datetime.now(timezone.utc)
    db_game = Game(
        slug=slug,
        itch_url=normalized,
        submitter_id=submitter_id,
        status=GameStatus.approved,
        reviewed_by_id=submitter_id,
        reviewed_at=now,
        duplicate_title_warning=duplicate_warning,
    )
    session.add(db_game)
    session.commit()
    session.refresh(db_game)

    upsert_from_metadata(session=session, game_id=db_game.id, metadata=metadata)
    session.commit()
    session.refresh(db_game)
    return db_game


def create_admin_game(
    *, session: Session, game_in: GameCreate, submitter_id: uuid.UUID
) -> Game:
    normalized = normalize_itch_url(game_in.url)
    if not normalized:
        raise ValueError("URL must be a valid itch.io game page")

    if find_game_by_itch_url(session=session, normalized_url=normalized):
        raise ValueError(f"Duplicate URL already indexed: {game_in.url}")

    if not check_public_viewability_sync(normalized):
        raise ValueError(NOT_PUBLIC_DETAIL)

    metadata = fetch_itch_metadata_sync(normalized)
    slug = unique_game_slug_from_url(session, normalized)
    duplicate_warning = False
    if metadata.title:
        duplicate_warning = len(
            find_similar_titles(session=session, title=metadata.title)
        ) > 0

    now = datetime.now(timezone.utc)
    db_game = Game(
        slug=slug,
        itch_url=normalized,
        submitter_id=submitter_id,
        status=GameStatus.approved,
        reviewed_by_id=submitter_id,
        reviewed_at=now,
        duplicate_title_warning=duplicate_warning,
    )
    session.add(db_game)
    session.commit()
    session.refresh(db_game)

    upsert_from_metadata(session=session, game_id=db_game.id, metadata=metadata)
    session.commit()
    session.refresh(db_game)
    return db_game


def remove_game_from_index(
    *, session: Session, db_game: Game, removal_reason: str
) -> Game:
    db_game.status = GameStatus.archived
    db_game.removal_reason = removal_reason.strip()
    db_game.featured_at = None
    db_game.updated_at = datetime.now(timezone.utc)
    session.add(db_game)
    session.commit()
    session.refresh(db_game)
    return db_game


def restore_game_to_index(*, session: Session, db_game: Game) -> Game:
    if db_game.status != GameStatus.archived:
        raise ValueError("Game is not removed from the index")
    db_game.status = GameStatus.approved
    db_game.removal_reason = None
    db_game.updated_at = datetime.now(timezone.utc)
    session.add(db_game)
    session.commit()
    session.refresh(db_game)
    return db_game


def admin_games_public(
    session: Session, games: list[Game], count: int
) -> AdminGamesPublic:
    for game in games:
        session.refresh(game, attribute_names=["itch_cache"])

    return AdminGamesPublic(
        data=[
            AdminGamePublic(
                id=game.id,
                itch_url=game.itch_url,
                title=game.itch_cache.title if game.itch_cache else None,
                status=game.status,
                featured_at=game.featured_at,
                removal_reason=game.removal_reason,
                created_at=game.created_at,
                updated_at=game.updated_at,
            )
            for game in games
        ],
        count=count,
    )


def _admin_games_status_filter(*, removed: bool):
    if removed:
        return col(Game.status) == GameStatus.archived
    return col(Game.status) != GameStatus.archived


def admin_games_query(
    *,
    session: Session,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
    removed: bool = False,
) -> tuple[list[Game], int]:
    status_filter = _admin_games_status_filter(removed=removed)
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        statement = _cache_joined_statement().where(status_filter)
        count_statement = (
            select(func.count())
            .select_from(Game)
            .join(GameItchCache, GameItchCache.game_id == Game.id)
            .where(status_filter)
        )
        search_filter = or_(
            col(GameItchCache.title).ilike(pattern),
            col(Game.itch_url).ilike(pattern),
            col(GameItchCache.author_name).ilike(pattern),
        )
        statement = statement.where(search_filter)
        count_statement = count_statement.where(search_filter)
    else:
        statement = select(Game).where(status_filter)
        count_statement = (
            select(func.count()).select_from(Game).where(status_filter)
        )

    count = session.exec(count_statement).one()
    order_column = col(Game.updated_at).desc() if removed else col(Game.created_at).desc()
    games = session.exec(
        statement.options(*_game_load_options())
        .order_by(order_column)
        .offset(skip)
        .limit(limit)
    ).all()
    return list(games), count


def update_game(
    *, session: Session, db_game: Game, game_in: GameUpdate
) -> Game:
    if game_in.url is None:
        return db_game

    normalized = normalize_itch_url(game_in.url)
    if not normalized:
        raise ValueError("URL must be a valid itch.io game page")

    if normalized != db_game.itch_url:
        existing = find_game_by_itch_url(session=session, normalized_url=normalized)
        if existing and existing.id != db_game.id:
            raise ValueError(f"Duplicate URL already indexed: {game_in.url}")
        if not check_public_viewability_sync(normalized):
            raise ValueError(NOT_PUBLIC_DETAIL)
        metadata = fetch_itch_metadata_sync(normalized)
        db_game.itch_url = normalized
        upsert_from_metadata(session=session, game_id=db_game.id, metadata=metadata)

    db_game.updated_at = datetime.now(timezone.utc)
    session.add(db_game)
    session.commit()
    session.refresh(db_game)
    return db_game


def _author_name_expr():
    return sa_func.coalesce(GameItchCache.author_name, "")


def _game_load_options():
    return (
        selectinload(Game.itch_cache),  # type: ignore[arg-type]
        selectinload(Game.submitter),  # type: ignore[arg-type]
    )


def load_game(session: Session, game_id: uuid.UUID) -> Game | None:
    statement = (
        select(Game)
        .where(Game.id == game_id)
        .options(*_game_load_options())
    )
    return session.exec(statement).first()


def load_game_by_slug(session: Session, slug: str) -> Game | None:
    statement = (
        select(Game)
        .where(Game.slug == slug)
        .options(*_game_load_options())
    )
    return session.exec(statement).first()


def check_duplicate_games(
    session: Session,
    url: str,
    title: str | None = None,
) -> DuplicateCheckResult:
    result = DuplicateCheckResult()
    normalized = normalize_itch_url(url)
    if normalized:
        existing = find_game_by_itch_url(session=session, normalized_url=normalized)
        if existing:
            result.url_exists = True
            result.existing_game_slug = existing.slug
    if title:
        result.similar_titles = find_similar_titles(session=session, title=title)
    return result


def get_kudos_game_ids_for_user(
    *, session: Session, user_id: uuid.UUID, game_ids: list[uuid.UUID]
) -> set[uuid.UUID]:
    if not game_ids:
        return set()
    rows = session.exec(
        select(GameKudos.game_id).where(
            GameKudos.user_id == user_id,
            col(GameKudos.game_id).in_(game_ids),
        )
    ).all()
    return set(rows)


def get_user_by_kudos_visitor_id(
    *, session: Session, visitor_id: str
) -> User | None:
    statement = select(User).where(User.kudos_visitor_id == visitor_id)
    return session.exec(statement).first()


def get_kudos_game_ids_for_visitor(
    *, session: Session, visitor_id: str, game_ids: list[uuid.UUID]
) -> set[uuid.UUID]:
    if not game_ids:
        return set()
    kudos_ids: set[uuid.UUID] = set()
    rows = session.exec(
        select(GameAnonymousKudos.game_id).where(
            GameAnonymousKudos.visitor_id == visitor_id,
            col(GameAnonymousKudos.game_id).in_(game_ids),
        )
    ).all()
    kudos_ids |= set(rows)
    linked_user = get_user_by_kudos_visitor_id(session=session, visitor_id=visitor_id)
    if linked_user:
        kudos_ids |= get_kudos_game_ids_for_user(
            session=session, user_id=linked_user.id, game_ids=game_ids
        )
    return kudos_ids


def get_kudos_game_ids(
    *,
    session: Session,
    game_ids: list[uuid.UUID],
    user_id: uuid.UUID | None = None,
    visitor_id: str | None = None,
) -> set[uuid.UUID]:
    kudos_ids: set[uuid.UUID] = set()
    visitor_ids: set[str] = set()
    if visitor_id:
        visitor_ids.add(visitor_id)
    if user_id:
        kudos_ids |= get_kudos_game_ids_for_user(
            session=session, user_id=user_id, game_ids=game_ids
        )
        user = session.get(User, user_id)
        if user and user.kudos_visitor_id:
            visitor_ids.add(user.kudos_visitor_id)
    for vid in visitor_ids:
        kudos_ids |= get_kudos_game_ids_for_visitor(
            session=session, visitor_id=vid, game_ids=game_ids
        )
    return kudos_ids


def ensure_kudos_visitor_id(
    *, session: Session, user: User, visitor_id: str
) -> User:
    if user.kudos_visitor_id is None:
        user.kudos_visitor_id = visitor_id
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def claim_anonymous_kudos_for_user(
    *, session: Session, user: User, visitor_id: str
) -> User:
    user = ensure_kudos_visitor_id(session=session, user=user, visitor_id=visitor_id)

    anonymous_rows = session.exec(
        select(GameAnonymousKudos).where(GameAnonymousKudos.visitor_id == visitor_id)
    ).all()
    for row in anonymous_rows:
        existing = session.get(GameKudos, (user.id, row.game_id))
        if not existing:
            session.add(
                GameKudos(
                    user_id=user.id,
                    game_id=row.game_id,
                    created_at=row.created_at,
                )
            )
        session.delete(row)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _cache_joined_statement():
    return select(Game).join(GameItchCache, GameItchCache.game_id == Game.id)


def search_games_query(
    *,
    session: Session,
    status: GameStatus | None = GameStatus.approved,
    tag_slugs: list[str] | None = None,
    platforms: list[OsPlatform] | None = None,
    search: str | None = None,
    sort: GameSort = GameSort.latest,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Game], int]:
    needs_cache = bool(
        search or tag_slugs or platforms or sort in {GameSort.title, GameSort.author}
    )
    if needs_cache:
        statement = _cache_joined_statement()
        count_statement = (
            select(func.count())
            .select_from(Game)
            .join(GameItchCache, GameItchCache.game_id == Game.id)
        )
    else:
        statement = select(Game)
        count_statement = select(func.count()).select_from(Game)

    if status is not None:
        statement = statement.where(Game.status == status)
        count_statement = count_statement.where(Game.status == status)

    if search:
        pattern = f"%{search.strip()}%"
        tag_search = sa_text(
            """
            EXISTS (
                SELECT 1 FROM jsonb_array_elements(game_itch_cache.tags) AS tag
                WHERE tag->>'name' ILIKE :pattern OR tag->>'slug' ILIKE :pattern
            )
            """
        ).bindparams(pattern=pattern)
        search_filter = or_(
            col(GameItchCache.title).ilike(pattern),
            col(GameItchCache.summary).ilike(pattern),
            col(GameItchCache.author_name).ilike(pattern),
            tag_search,
        )
        statement = statement.where(search_filter)
        count_statement = count_statement.where(search_filter)

    if tag_slugs:
        for slug in tag_slugs:
            slug_filter = sa_text(
                """
                EXISTS (
                    SELECT 1 FROM jsonb_array_elements(game_itch_cache.tags) AS tag
                    WHERE tag->>'slug' = :slug
                )
                """
            ).bindparams(slug=slug)
            statement = statement.where(slug_filter)
            count_statement = count_statement.where(slug_filter)

    if platforms:
        platform_values = [platform.value for platform in platforms]
        platform_filter = sa_text(
            "game_itch_cache.platforms ?| :platform_values"
        ).bindparams(platform_values=platform_values)
        statement = statement.where(platform_filter)
        count_statement = count_statement.where(platform_filter)

    if sort == GameSort.latest:
        order = col(Game.created_at).desc()
    elif sort == GameSort.title:
        order = col(GameItchCache.title).asc()
    elif sort == GameSort.author:
        order = _author_name_expr().asc()
    else:
        order = col(Game.kudos_count).desc()

    count = session.exec(count_statement).one()
    games = session.exec(
        statement.options(*_game_load_options())
        .order_by(order)
        .offset(skip)
        .limit(limit)
    ).all()
    return list(games), count


def featured_games_query(
    *, session: Session, limit: int = 3
) -> list[Game]:
    statement = (
        select(Game)
        .where(Game.status == GameStatus.approved)
        .where(col(Game.featured_at).is_not(None))
        .options(*_game_load_options())
        .order_by(col(Game.featured_at).desc())
        .limit(limit)
    )
    return list(session.exec(statement).all())


def list_distinct_tags(session: Session) -> list[TagPublic]:
    rows = session.exec(
        sa_text(
            """
            SELECT slug, name, itch_url, is_genre
            FROM (
                SELECT DISTINCT
                    tag->>'slug' AS slug,
                    tag->>'name' AS name,
                    tag->>'itch_url' AS itch_url,
                    COALESCE((tag->>'is_genre')::boolean, false) AS is_genre
                FROM game_itch_cache c
                JOIN game g ON g.id = c.game_id
                CROSS JOIN LATERAL jsonb_array_elements(c.tags) AS tag
                WHERE g.status = 'approved'
            ) AS distinct_tags
            ORDER BY is_genre DESC, lower(name)
            """
        )
    ).all()
    return [
        TagPublic(
            id=tag_id_from_slug(row.slug),
            name=row.name,
            slug=row.slug,
            itch_url=row.itch_url,
            is_genre=row.is_genre,
        )
        for row in rows
    ]


def tag_exists(session: Session, slug: str) -> bool:
    rows = session.exec(
        sa_text(
            """
            SELECT 1
            FROM game_itch_cache c
            JOIN game g ON g.id = c.game_id
            CROSS JOIN LATERAL jsonb_array_elements(c.tags) AS tag
            WHERE g.status = 'approved' AND tag->>'slug' = :slug
            LIMIT 1
            """
        ).bindparams(slug=slug)
    ).first()
    return rows is not None


def add_game_kudos(
    *,
    session: Session,
    game: Game,
    user_id: uuid.UUID,
    visitor_id: str | None = None,
) -> Game:
    existing = session.get(GameKudos, (user_id, game.id))
    if existing:
        raise ValueError("Already gave kudos")

    user = session.get(User, user_id)
    if user and visitor_id:
        user = ensure_kudos_visitor_id(session=session, user=user, visitor_id=visitor_id)

    visitor_ids: set[str] = set()
    if visitor_id:
        visitor_ids.add(visitor_id)
    if user and user.kudos_visitor_id:
        visitor_ids.add(user.kudos_visitor_id)
    for vid in visitor_ids:
        if session.get(GameAnonymousKudos, (vid, game.id)):
            raise ValueError("Already gave kudos")

    session.add(GameKudos(user_id=user_id, game_id=game.id))
    game.kudos_count += 1
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


def add_anonymous_game_kudos(
    *, session: Session, game: Game, visitor_id: str
) -> Game:
    existing = session.get(GameAnonymousKudos, (visitor_id, game.id))
    if existing:
        raise ValueError("Already gave kudos")

    linked_user = get_user_by_kudos_visitor_id(session=session, visitor_id=visitor_id)
    if linked_user and session.get(GameKudos, (linked_user.id, game.id)):
        raise ValueError("Already gave kudos")

    session.add(GameAnonymousKudos(visitor_id=visitor_id, game_id=game.id))
    game.kudos_count += 1
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


def feature_game(*, session: Session, game: Game) -> Game:
    game.featured_at = datetime.now(timezone.utc)
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


def unfeature_game(*, session: Session, game: Game) -> Game:
    game.featured_at = None
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


def get_newsletter_subscriber_by_email(
    *, session: Session, email: str
) -> NewsletterSubscriber | None:
    statement = select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
    return session.exec(statement).first()


def subscribe_newsletter(*, session: Session, email: str) -> NewsletterSubscriber:
    existing = get_newsletter_subscriber_by_email(session=session, email=email)
    if existing:
        return existing
    subscriber = NewsletterSubscriber(email=email)
    session.add(subscriber)
    session.commit()
    session.refresh(subscriber)
    return subscriber


def count_newsletter_subscribers(*, session: Session) -> int:
    return session.exec(
        select(func.count()).select_from(NewsletterSubscriber)
    ).one()


def list_newsletter_subscriber_emails(*, session: Session) -> list[str]:
    rows = session.exec(
        select(NewsletterSubscriber.email).order_by(col(NewsletterSubscriber.created_at))
    ).all()
    return list(rows)
