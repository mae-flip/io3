import csv
import io
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app import crud
from app.api.deps import CurrentModerator, CurrentOwner, SessionDep
from app.models import (
    AdminGamePublic,
    AdminGamesPublic,
    Game,
    GameCreate,
    GameStatus,
    Message,
    ModeratorUserPublic,
    ModeratorUserUpdate,
    ModeratorUsersPublic,
    NewsletterSubscribersPublic,
    User,
)

router = APIRouter(prefix="/admin", tags=["admin"])


def _admin_game_public(game: Game) -> AdminGamePublic:
    cache = game.itch_cache
    return AdminGamePublic(
        id=game.id,
        itch_url=game.itch_url,
        title=cache.title if cache else None,
        status=game.status,
        featured_at=game.featured_at,
        created_at=game.created_at,
    )


@router.get("/games", response_model=AdminGamesPublic)
def read_admin_games(
    session: SessionDep,
    current_user: CurrentModerator,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
) -> Any:
    games, count = crud.admin_games_query(
        session=session, search=search, skip=skip, limit=limit
    )
    return crud.admin_games_public(session, games, count)


@router.post("/games", response_model=AdminGamePublic)
def create_admin_game(
    *,
    session: SessionDep,
    current_user: CurrentModerator,
    game_in: GameCreate,
) -> Any:
    try:
        game = crud.create_admin_game(
            session=session,
            game_in=game_in,
            submitter_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    loaded = crud.load_game(session, game.id)
    assert loaded
    return _admin_game_public(loaded)


@router.post("/games/{id}/feature", response_model=AdminGamePublic)
def feature_admin_game(
    session: SessionDep, current_user: CurrentModerator, id: uuid.UUID
) -> Any:
    game = crud.load_game(session, id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status != GameStatus.approved:
        raise HTTPException(
            status_code=400, detail="Only approved games can be featured"
        )
    updated = crud.feature_game(session=session, game=game)
    loaded = crud.load_game(session, updated.id)
    assert loaded
    return _admin_game_public(loaded)


@router.post("/games/{id}/unfeature", response_model=AdminGamePublic)
def unfeature_admin_game(
    session: SessionDep, current_user: CurrentModerator, id: uuid.UUID
) -> Any:
    game = crud.load_game(session, id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    updated = crud.unfeature_game(session=session, game=game)
    loaded = crud.load_game(session, updated.id)
    assert loaded
    return _admin_game_public(loaded)


@router.delete("/games/{id}", response_model=Message)
def delete_admin_game(
    session: SessionDep, current_user: CurrentModerator, id: uuid.UUID
) -> Any:
    game = crud.load_game(session, id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    crud.delete_game(session=session, db_game=game)
    return Message(message="Game deleted successfully")


@router.get("/users", response_model=ModeratorUsersPublic)
def read_admin_users(
    session: SessionDep,
    current_user: CurrentOwner,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return crud.list_itch_users(session=session, skip=skip, limit=limit)


@router.patch("/users/{user_id}", response_model=ModeratorUserPublic)
def update_admin_user(
    *,
    session: SessionDep,
    current_user: CurrentOwner,
    user_id: uuid.UUID,
    user_in: ModeratorUserUpdate,
) -> Any:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.is_owner:
        raise HTTPException(
            status_code=400, detail="Cannot change moderator status of the owner"
        )
    if db_user.id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Cannot change your own moderator status"
        )
    if db_user.itch_user_id is None:
        raise HTTPException(status_code=400, detail="User is not an itch.io account")

    updated = crud.update_moderator_status(
        session=session, db_user=db_user, is_moderator=user_in.is_moderator
    )
    return ModeratorUserPublic.model_validate(updated)


@router.get("/newsletter/subscribers", response_model=NewsletterSubscribersPublic)
def read_newsletter_subscribers(
    session: SessionDep,
    current_user: CurrentOwner,
) -> Any:
    count = crud.count_newsletter_subscribers(session=session)
    return NewsletterSubscribersPublic(count=count)


@router.get("/newsletter/subscribers.csv")
def download_newsletter_subscribers_csv(
    session: SessionDep,
    current_user: CurrentOwner,
) -> Response:
    emails = crud.list_newsletter_subscriber_emails(session=session)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["email"])
    for email in emails:
        writer.writerow([email])
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="newsletter-subscribers.csv"'
        },
    )
