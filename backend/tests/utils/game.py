from datetime import datetime, timezone

from sqlmodel import Session

from app.models import Game, GameItchCache, GameStatus, User
from app.services.slug import unique_game_slug_from_url
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_game(
    db: Session, *, approved: bool = False, submitter: User | None = None
) -> Game:
    user = submitter or create_random_user(db)
    path = random_lower_string()
    itch_url = f"https://example.itch.io/{path}"
    title = random_lower_string()
    slug = unique_game_slug_from_url(db, itch_url)
    game = Game(
        itch_url=itch_url,
        slug=slug,
        submitter_id=user.id,
        status=GameStatus.pending,
    )
    db.add(game)
    db.flush()
    cache = GameItchCache(
        game_id=game.id,
        title=title,
        summary="A queer indie game for the index",
        author_name="Example Author",
        author_url="https://example.itch.io",
        tags=[],
        platforms=["web"],
        fetched_at=datetime.now(timezone.utc),
    )
    db.add(cache)
    db.commit()
    db.refresh(game)
    if approved:
        game.status = GameStatus.approved
        db.add(game)
        db.commit()
        db.refresh(game)
    return game


def set_game_cache(
    db: Session,
    game: Game,
    *,
    title: str | None = None,
    author_name: str | None = None,
    author_url: str | None = None,
    tags: list[dict] | None = None,
) -> GameItchCache:
    cache = db.get(GameItchCache, game.id)
    if not cache:
        cache = GameItchCache(
            game_id=game.id,
            tags=[],
            platforms=[],
            fetched_at=datetime.now(timezone.utc),
        )
    if title is not None:
        cache.title = title
    if author_name is not None:
        cache.author_name = author_name
    if author_url is not None:
        cache.author_url = author_url
    if tags is not None:
        cache.tags = tags
    cache.fetched_at = datetime.now(timezone.utc)
    db.add(cache)
    db.commit()
    db.refresh(cache)
    return cache
