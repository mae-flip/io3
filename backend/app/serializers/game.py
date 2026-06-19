import uuid

from sqlmodel import Session

from app import crud
from app.models import Game, GameItchCache, GameLinkPublic, GamePublic, GamesPublic, LinkPlatform, TagPublic, User
from app.services.itch_cache import ensure_fresh, ensure_fresh_many, get_cache, link_id_from_url
from app.services.user_profile import profile_links_for_displayed_author


def _synthetic_link(game: Game) -> GameLinkPublic:
    return GameLinkPublic(
        id=link_id_from_url(game.itch_url),
        url=game.itch_url,
        platform=LinkPlatform.itch,
        is_primary=True,
        normalized_url=game.itch_url,
    )


def game_to_public(
    game: Game,
    *,
    cache: GameItchCache | None = None,
    has_kudos: bool = False,
    tags: list[TagPublic] | None = None,
    platforms: list | None = None,
) -> GamePublic:
    tag_data = tags if tags is not None else crud.tags_public_from_cache(cache)
    platform_data = platforms if platforms is not None else crud.platforms_public_from_cache(cache)
    author_name = cache.author_name if cache else None
    author_url = cache.author_url if cache else None
    submitter_itch_username: str | None = None
    submitter_profile_links = []
    if game.submitter:
        if game.submitter.itch_username:
            submitter_itch_username = game.submitter.itch_username
        submitter_profile_links = profile_links_for_displayed_author(
            author_url=author_url,
            author_name=author_name,
            submitter=game.submitter,
        )
    return GamePublic(
        id=game.id,
        slug=game.slug,
        title=cache.title if cache else None,
        summary=cache.summary if cache else None,
        description=None,
        cover_image_url=cache.cover_image_url if cache else None,
        status=game.status,
        submitter_id=game.submitter_id,
        submitter_itch_username=submitter_itch_username,
        submitter_profile_links=submitter_profile_links,
        reviewed_at=game.reviewed_at,
        rejection_reason=game.rejection_reason,
        duplicate_title_warning=game.duplicate_title_warning,
        kudos_count=game.kudos_count,
        featured_at=game.featured_at,
        author_name=author_name,
        author_url=author_url,
        has_kudos=has_kudos,
        created_at=game.created_at,
        updated_at=game.updated_at,
        links=[_synthetic_link(game)],
        tags=tag_data,
        platforms=platform_data,
        price_cents=cache.price_cents if cache else None,
        price_currency=cache.price_currency if cache else None,
    )


def game_to_public_from_session(
    session: Session,
    game: Game,
    *,
    has_kudos: bool = False,
) -> GamePublic:
    cache = ensure_fresh(session, game)
    session.commit()
    session.refresh(game, attribute_names=["itch_cache", "submitter"])
    return game_to_public(game, cache=cache or game.itch_cache, has_kudos=has_kudos)


def games_public(
    session: Session,
    games: list[Game],
    count: int,
    *,
    current_user: User | None = None,
    kudos_visitor_id: str | None = None,
) -> GamesPublic:
    ensure_fresh_many(session, games)
    session.commit()

    for game in games:
        session.refresh(game, attribute_names=["itch_cache"])

    kudos_ids: set[uuid.UUID] = set()
    if games and (current_user or kudos_visitor_id):
        kudos_ids = crud.get_kudos_game_ids(
            session=session,
            game_ids=[game.id for game in games],
            user_id=current_user.id if current_user else None,
            visitor_id=kudos_visitor_id,
        )

    return GamesPublic(
        data=[
            game_to_public(
                game,
                cache=game.itch_cache or get_cache(session, game.id),
                has_kudos=game.id in kudos_ids,
            )
            for game in games
        ],
        count=count,
    )
