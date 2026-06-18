import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import col, select

from app import crud
from app.api.deps import (
    CurrentUser,
    KUDOS_VISITOR_HEADER,
    OptionalKudosVisitor,
    OptionalUser,
    SessionDep,
)
from app.models import (
    DuplicateCheckResult,
    Game,
    GameCreate,
    GamePublic,
    GameSubmitBatch,
    GamesPublic,
    GameSort,
    GameStatus,
    GameUpdate,
    ItchMetadataPreview,
    OsPlatform,
    SubmitBatchItemStatus,
    SubmitBatchResponse,
    SubmitBatchResultItem,
)
from app.serializers.game import game_to_public_from_session, games_public
from app.services.itch import fetch_itch_metadata
from app.services.itch_api import ItchApiError, fetch_itch_games, owned_game_urls
from app.services.itch_search import is_listed_in_itch_search
from app.services.urls import normalize_itch_url

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/", response_model=GamesPublic)
def read_games(
    session: SessionDep,
    current_user: OptionalUser,
    kudos_visitor_id: OptionalKudosVisitor,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    sort: GameSort = GameSort.latest,
    tag_slugs: list[str] = Query(default=[]),
    platforms: list[OsPlatform] = Query(default=[]),
) -> Any:
    games, count = crud.search_games_query(
        session=session,
        status=GameStatus.approved,
        tag_slugs=tag_slugs or None,
        platforms=platforms or None,
        search=search,
        sort=sort,
        skip=skip,
        limit=limit,
    )
    return games_public(
        session,
        games,
        count,
        current_user=current_user,
        kudos_visitor_id=kudos_visitor_id,
    )


@router.get("/featured", response_model=GamesPublic)
def read_featured_games(
    session: SessionDep,
    current_user: OptionalUser,
    kudos_visitor_id: OptionalKudosVisitor,
    limit: int = 3,
) -> Any:
    games = crud.featured_games_query(session=session, limit=limit)
    return games_public(
        session,
        games,
        len(games),
        current_user=current_user,
        kudos_visitor_id=kudos_visitor_id,
    )


@router.get("/me", response_model=GamesPublic)
def read_my_games(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    statement = (
        select(Game)
        .where(Game.submitter_id == current_user.id)
        .options(*crud._game_load_options())
        .order_by(col(Game.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    games = list(session.exec(statement).all())
    count = len(
        session.exec(
            select(Game).where(Game.submitter_id == current_user.id)
        ).all()
    )
    return games_public(session, games, count, current_user=current_user)


@router.get("/prefill-itch", response_model=ItchMetadataPreview)
async def prefill_itch_metadata(url: str) -> Any:
    return await fetch_itch_metadata(url)


@router.get("/check-duplicate", response_model=DuplicateCheckResult)
def check_duplicate(
    session: SessionDep,
    url: str,
    title: str | None = None,
) -> Any:
    return crud.check_duplicate_games(session=session, url=url, title=title)


@router.post("/submit-batch", response_model=SubmitBatchResponse)
async def submit_games_batch(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    body: GameSubmitBatch,
) -> Any:
    if not crud.user_can_submit(current_user):
        raise HTTPException(
            status_code=403,
            detail="Your account is not yet eligible to submit games",
        )

    try:
        itch_games = await fetch_itch_games(body.itch_access_token)
    except ItchApiError as exc:
        raise HTTPException(
            status_code=401,
            detail="itch.io session expired. Please log in again.",
        ) from exc

    owned = owned_game_urls(itch_games)
    results: list[SubmitBatchResultItem] = []
    submitted_count = 0
    skipped_count = 0

    for raw_url in body.urls:
        normalized = normalize_itch_url(raw_url)
        if not normalized or normalized not in owned:
            skipped_count += 1
            results.append(
                SubmitBatchResultItem(
                    url=raw_url,
                    status=SubmitBatchItemStatus.not_owned,
                    detail="Game is not in your itch.io library",
                )
            )
            continue

        if crud.find_game_by_itch_url(session=session, normalized_url=normalized):
            skipped_count += 1
            results.append(
                SubmitBatchResultItem(
                    url=raw_url,
                    status=SubmitBatchItemStatus.duplicate,
                    detail="Game is already indexed",
                )
            )
            continue

        owned_game = owned.get(normalized)
        if owned_game and await is_listed_in_itch_search(
            url=raw_url, title=owned_game.title
        ):
            skipped_count += 1
            results.append(
                SubmitBatchResultItem(
                    url=raw_url,
                    status=SubmitBatchItemStatus.still_listed,
                    detail="Game still appears in itch.io search and cannot be indexed here",
                )
            )
            continue

        try:
            game = crud.create_game(
                session=session,
                game_in=GameCreate(url=raw_url),
                submitter_id=current_user.id,
            )
            loaded = crud.load_game(session, game.id)
            assert loaded
            game_public = game_to_public_from_session(session, loaded)
            submitted_count += 1
            results.append(
                SubmitBatchResultItem(
                    url=raw_url,
                    status=SubmitBatchItemStatus.submitted,
                    game=game_public,
                )
            )
        except ValueError as exc:
            skipped_count += 1
            results.append(
                SubmitBatchResultItem(
                    url=raw_url,
                    status=SubmitBatchItemStatus.error,
                    detail=str(exc),
                )
            )

    return SubmitBatchResponse(
        results=results,
        submitted_count=submitted_count,
        skipped_count=skipped_count,
    )


@router.get("/{slug}", response_model=GamePublic)
def read_game(
    session: SessionDep,
    slug: str,
    current_user: OptionalUser,
    kudos_visitor_id: OptionalKudosVisitor,
) -> Any:
    game = crud.load_game_by_slug(session, slug)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status != GameStatus.approved:
        is_owner = current_user and game.submitter_id == current_user.id
        is_mod = current_user and (
            current_user.is_moderator or current_user.is_owner
        )
        if not is_owner and not is_mod:
            raise HTTPException(status_code=404, detail="Game not found")
    kudos_ids = crud.get_kudos_game_ids(
        session=session,
        game_ids=[game.id],
        user_id=current_user.id if current_user else None,
        visitor_id=kudos_visitor_id,
    )
    has_kudos = game.id in kudos_ids
    return game_to_public_from_session(session, game, has_kudos=has_kudos)


@router.post("/{slug}/kudos", response_model=GamePublic)
def add_kudos(
    session: SessionDep,
    slug: str,
    current_user: OptionalUser,
    kudos_visitor_id: OptionalKudosVisitor,
) -> Any:
    if not current_user and not kudos_visitor_id:
        raise HTTPException(
            status_code=400,
            detail=f"Anonymous kudos require the {KUDOS_VISITOR_HEADER} header",
        )
    game = crud.load_game_by_slug(session, slug)
    if not game or game.status != GameStatus.approved:
        raise HTTPException(status_code=404, detail="Game not found")
    try:
        if current_user:
            crud.add_game_kudos(
                session=session,
                game=game,
                user_id=current_user.id,
                visitor_id=kudos_visitor_id,
            )
        else:
            assert kudos_visitor_id
            crud.add_anonymous_game_kudos(
                session=session, game=game, visitor_id=kudos_visitor_id
            )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    loaded = crud.load_game_by_slug(session, slug)
    assert loaded
    return game_to_public_from_session(session, loaded, has_kudos=True)


@router.post("/", response_model=GamePublic)
def create_game(
    *, session: SessionDep, current_user: CurrentUser, game_in: GameCreate
) -> Any:
    if not crud.user_can_submit(current_user):
        raise HTTPException(
            status_code=403,
            detail="Your account is not yet eligible to submit games",
        )

    try:
        game = crud.create_game(
            session=session, game_in=game_in, submitter_id=current_user.id
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    loaded = crud.load_game(session, game.id)
    assert loaded
    return game_to_public_from_session(session, loaded)


@router.patch("/{id}", response_model=GamePublic)
def update_game(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    game_in: GameUpdate,
) -> Any:
    game = crud.load_game(session, id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.submitter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if game.status != GameStatus.pending:
        raise HTTPException(
            status_code=400, detail="Only pending submissions can be edited"
        )

    try:
        updated = crud.update_game(session=session, db_game=game, game_in=game_in)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    loaded = crud.load_game(session, updated.id)
    assert loaded
    return game_to_public_from_session(session, loaded)
