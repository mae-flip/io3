from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from sqlmodel import Session

from app.core.config import settings
from app.models import Game, GameItchCache, GameStatus
from app.services.itch import ItchMetadata, ItchTag
from app.services.itch_cache import (
    _is_stale,
    ensure_fresh,
    get_cache,
    upsert_from_metadata,
)
from tests.utils.game import create_random_game
from tests.utils.user import create_random_user


def test_is_stale_when_missing() -> None:
    assert _is_stale(None) is True


def test_is_stale_when_fresh(db: Session) -> None:
    game = create_random_game(db)
    cache = db.get(GameItchCache, game.id)
    assert cache is not None
    assert _is_stale(cache) is False


def test_is_stale_when_expired(db: Session) -> None:
    game = create_random_game(db)
    cache = db.get(GameItchCache, game.id)
    assert cache is not None
    cache.fetched_at = datetime.now(timezone.utc) - timedelta(
        seconds=settings.ITCH_CACHE_TTL_SECONDS + 1
    )
    db.add(cache)
    db.commit()
    assert _is_stale(cache) is True


def test_upsert_from_metadata(db: Session) -> None:
    user = create_random_user(db)
    game = Game(
        slug="test-game",
        itch_url="https://example.itch.io/test-game",
        submitter_id=user.id,
        status=GameStatus.pending,
    )
    db.add(game)
    db.commit()
    db.refresh(game)

    metadata = ItchMetadata(
        normalized_url=game.itch_url,
        title="Test Game",
        summary="Summary",
        tags=[ItchTag(name="NSFW", slug="nsfw", itch_url="https://itch.io/games/tag-nsfw")],
    )
    cache = upsert_from_metadata(session=db, game_id=game.id, metadata=metadata)
    assert cache.title == "Test Game"
    assert cache.tags[0]["slug"] == "nsfw"


def test_ensure_fresh_skips_live_fetch_when_fresh(db: Session) -> None:
    game = create_random_game(db)
    with patch("app.services.itch_cache.refresh_game_cache") as refresh:
        cache = ensure_fresh(db, game)
    refresh.assert_not_called()
    assert cache is not None


def test_ensure_fresh_fetches_when_stale(db: Session) -> None:
    game = create_random_game(db)
    cache = db.get(GameItchCache, game.id)
    assert cache is not None
    cache.fetched_at = datetime.now(timezone.utc) - timedelta(
        seconds=settings.ITCH_CACHE_TTL_SECONDS + 1
    )
    db.add(cache)
    db.commit()

    metadata = ItchMetadata(
        normalized_url=game.itch_url,
        title="Updated Title",
    )
    with patch(
        "app.services.itch_cache.refresh_game_cache",
        return_value=upsert_from_metadata(
            session=db, game_id=game.id, metadata=metadata
        ),
    ):
        result = ensure_fresh(db, game)
    assert result is not None
    assert get_cache(db, game.id) is not None
