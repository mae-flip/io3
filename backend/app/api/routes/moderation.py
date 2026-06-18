import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app import crud
from app.api.deps import CurrentModerator, SessionDep
from app.models import (
    DuplicateCheckResult,
    Game,
    GamePublic,
    GamesPublic,
    GameReject,
    GameStatus,
)
from app.serializers.game import game_to_public_from_session, games_public

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.get("/queue", response_model=GamesPublic)
def read_moderation_queue(
    session: SessionDep, current_user: CurrentModerator, skip: int = 0, limit: int = 100
) -> Any:
    count_statement = (
        select(func.count()).select_from(Game).where(Game.status == GameStatus.pending)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Game)
        .where(Game.status == GameStatus.pending)
        .options(*crud._game_load_options())
        .order_by(col(Game.created_at).asc())
        .offset(skip)
        .limit(limit)
    )
    games = session.exec(statement).all()
    return games_public(session, list(games), count)


@router.post("/games/{id}/approve", response_model=GamePublic)
def approve_game(
    session: SessionDep, current_user: CurrentModerator, id: uuid.UUID
) -> Any:
    game = crud.load_game(session, id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status != GameStatus.pending:
        raise HTTPException(status_code=400, detail="Game is not pending review")

    game.status = GameStatus.approved
    game.reviewed_by_id = current_user.id
    game.reviewed_at = datetime.now(timezone.utc)
    game.rejection_reason = None
    game.updated_at = datetime.now(timezone.utc)
    session.add(game)
    session.commit()
    session.refresh(game)
    return game_to_public_from_session(session, game)


@router.post("/games/{id}/feature", response_model=GamePublic)
def feature_game(
    session: SessionDep, current_user: CurrentModerator, id: uuid.UUID
) -> Any:
    game = crud.load_game(session, id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status != GameStatus.approved:
        raise HTTPException(status_code=400, detail="Only approved games can be featured")

    updated = crud.feature_game(session=session, game=game)
    loaded = crud.load_game(session, updated.id)
    assert loaded
    return game_to_public_from_session(session, loaded)


@router.post("/games/{id}/reject", response_model=GamePublic)
def reject_game(
    session: SessionDep,
    current_user: CurrentModerator,
    id: uuid.UUID,
    body: GameReject,
) -> Any:
    game = crud.load_game(session, id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status != GameStatus.pending:
        raise HTTPException(status_code=400, detail="Game is not pending review")

    game.status = GameStatus.rejected
    game.reviewed_by_id = current_user.id
    game.reviewed_at = datetime.now(timezone.utc)
    game.rejection_reason = body.rejection_reason
    game.updated_at = datetime.now(timezone.utc)
    session.add(game)
    session.commit()
    session.refresh(game)
    return game_to_public_from_session(session, game)


@router.get("/duplicates", response_model=DuplicateCheckResult)
def check_duplicates(
    session: SessionDep, current_user: CurrentModerator, url: str
) -> Any:
    return crud.check_duplicate_games(session=session, url=url)
