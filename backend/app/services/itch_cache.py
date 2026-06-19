import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from sqlmodel import Session, select

from app.core.config import settings
from app.models import Game, GameItchCache, OsPlatform
from app.services.itch import ITCH_USER_AGENT, ItchMetadata, ItchTag, parse_itch_metadata_from_html
from app.services.urls import normalize_itch_url

TAG_ID_NAMESPACE = uuid.UUID("a3b2c1d0-e5f4-3210-abcd-ef1234567890")
LINK_ID_NAMESPACE = uuid.UUID("b4c3d2e1-f6a5-4321-bcde-f12345678901")


def tag_id_from_slug(slug: str) -> uuid.UUID:
    return uuid.uuid5(TAG_ID_NAMESPACE, f"itch-tag:{slug}")


def link_id_from_url(url: str) -> uuid.UUID:
    return uuid.uuid5(LINK_ID_NAMESPACE, url)


def _tags_to_json(tags: list[ItchTag]) -> list[dict[str, Any]]:
    return [
        {
            "slug": tag.slug,
            "name": tag.name,
            "itch_url": tag.itch_url,
            "is_genre": tag.is_genre,
        }
        for tag in tags
    ]


def _platforms_to_json(platforms: list[OsPlatform]) -> list[str]:
    return [platform.value for platform in platforms]


def get_cache(session: Session, game_id: uuid.UUID) -> GameItchCache | None:
    return session.get(GameItchCache, game_id)


def _is_stale(cache: GameItchCache | None) -> bool:
    if cache is None:
        return True
    ttl = timedelta(seconds=settings.ITCH_CACHE_TTL_SECONDS)
    fetched_at = cache.fetched_at
    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - fetched_at >= ttl


def upsert_from_metadata(
    *,
    session: Session,
    game_id: uuid.UUID,
    metadata: ItchMetadata,
    fetch_error: str | None = None,
) -> GameItchCache:
    now = datetime.now(timezone.utc)
    existing = session.get(GameItchCache, game_id)
    payload = {
        "title": metadata.title,
        "summary": metadata.summary,
        "cover_image_url": metadata.cover_image_url,
        "author_name": metadata.author_name,
        "author_url": metadata.author_url,
        "tags": _tags_to_json(metadata.tags),
        "platforms": _platforms_to_json(metadata.platforms),
        "price_cents": metadata.price_cents,
        "price_currency": metadata.price_currency,
        "fetched_at": now,
        "fetch_error": fetch_error,
    }
    if existing:
        existing.sqlmodel_update(payload)
        session.add(existing)
        session.flush()
        return existing

    cache = GameItchCache(game_id=game_id, **payload)
    session.add(cache)
    session.flush()
    return cache


async def _fetch_html_async(client: httpx.AsyncClient, url: str) -> str | None:
    try:
        response = await client.get(
            url,
            headers={"User-Agent": ITCH_USER_AGENT},
        )
        response.raise_for_status()
        return response.text
    except httpx.HTTPError:
        return None


async def _fetch_metadata_async(url: str) -> tuple[ItchMetadata, str | None]:
    normalized = normalize_itch_url(url)
    metadata = ItchMetadata(normalized_url=normalized)
    if not normalized:
        return metadata, "Invalid itch URL"

    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        content = await _fetch_html_async(client, normalized)

    if content:
        return parse_itch_metadata_from_html(content, url=url), None

    from app.services.itch import fetch_itch_metadata_sync

    fallback = fetch_itch_metadata_sync(url)
    return fallback, "Failed to fetch itch page"


def refresh_game_cache(*, session: Session, game: Game) -> GameItchCache | None:
    metadata, error = asyncio.run(_fetch_metadata_async(game.itch_url))
    if error and not metadata.title and not metadata.tags:
        existing = session.get(GameItchCache, game.id)
        if existing:
            existing.fetch_error = error
            existing.fetched_at = datetime.now(timezone.utc)
            session.add(existing)
            session.flush()
            return existing
    return upsert_from_metadata(
        session=session,
        game_id=game.id,
        metadata=metadata,
        fetch_error=error,
    )


def ensure_fresh(session: Session, game: Game) -> GameItchCache | None:
    cache = get_cache(session, game.id)
    if not _is_stale(cache):
        return cache
    return refresh_game_cache(session=session, game=game)


async def _refresh_games_async(games: list[Game]) -> list[tuple[Game, ItchMetadata, str | None]]:
    semaphore = asyncio.Semaphore(settings.ITCH_FETCH_CONCURRENCY)

    async def fetch_one(game: Game) -> tuple[Game, ItchMetadata, str | None]:
        async with semaphore:
            metadata, error = await _fetch_metadata_async(game.itch_url)
            return game, metadata, error

    return await asyncio.gather(*[fetch_one(game) for game in games])


def ensure_fresh_many(session: Session, games: list[Game]) -> None:
    stale_games: list[Game] = []
    for game in games:
        cache = get_cache(session, game.id)
        if _is_stale(cache):
            stale_games.append(game)

    if not stale_games:
        return

    def apply_result(
        game: Game, metadata: ItchMetadata, error: str | None
    ) -> None:
        if error and not metadata.title and not metadata.tags:
            existing = session.get(GameItchCache, game.id)
            if existing:
                existing.fetch_error = error
                existing.fetched_at = datetime.now(timezone.utc)
                session.add(existing)
                return
        upsert_from_metadata(
            session=session,
            game_id=game.id,
            metadata=metadata,
            fetch_error=error,
        )

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        results = asyncio.run(_refresh_games_async(stale_games))
        for game, metadata, error in results:
            apply_result(game, metadata, error)
    else:
        for game in stale_games:
            metadata, error = asyncio.run(_fetch_metadata_async(game.itch_url))
            apply_result(game, metadata, error)

    session.flush()


def refresh_all_stale(session: Session, *, force: bool = False) -> int:
    from app.models import GameStatus

    statement = select(Game).where(Game.status == GameStatus.approved)
    games = list(session.exec(statement).all())
    if force:
        stale = games
    else:
        stale = [game for game in games if _is_stale(get_cache(session, game.id))]

    if not stale:
        return 0

    ensure_fresh_many(session, stale)
    session.commit()
    return len(stale)
