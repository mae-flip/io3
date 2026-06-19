from datetime import timedelta
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import Session

from app import crud
from app.api.deps import OptionalKudosVisitor, SessionDep
from app.core import security
from app.core.config import settings
from app.models import (
    ItchAuthCallback,
    ItchAuthResponse,
    ItchAuthorizeResponse,
    ItchGamePublic,
    UserPublic,
)
from app.services.itch_api import (
    ItchApiError,
    build_itch_authorize_url,
    fetch_itch_games,
    fetch_itch_profile,
    normalize_itch_game_url,
)
from app.services.itch_oauth_state import create_oauth_state, verify_oauth_state
from app.services.itch_public import public_viewability_for_games
from app.services.itch_search import listing_status_for_games

router = APIRouter(prefix="/auth/itch", tags=["itch-auth"])


def _require_oauth_config() -> None:
    if not settings.ITCH_OAUTH_CLIENT_ID:
        raise HTTPException(
            status_code=503,
            detail="itch.io OAuth is not configured on this server",
        )


async def _itch_games_public(
    session: Session, games: list
) -> list[ItchGamePublic]:
    filtered = [game for game in games if game.classification == "game"]
    game_refs = [(game.url, game.title) for game in filtered]
    listing_status = await listing_status_for_games(game_refs)
    viewability_status = await public_viewability_for_games(game_refs)

    public_games: list[ItchGamePublic] = []
    for game in filtered:
        normalized = normalize_itch_game_url(game.url)
        already_indexed = False
        if normalized:
            already_indexed = crud.find_game_by_itch_url(
                session=session, normalized_url=normalized
            ) is not None
        itch_search_listed = bool(normalized and listing_status.get(normalized, False))
        publicly_viewable = bool(normalized and viewability_status.get(normalized, False))
        public_games.append(
            ItchGamePublic(
                id=game.id,
                title=game.title,
                url=game.url,
                cover_url=game.cover_url,
                short_text=game.short_text,
                published=game.published,
                classification=game.classification,
                normalized_url=normalized,
                already_indexed=already_indexed,
                itch_search_listed=itch_search_listed,
                publicly_viewable=publicly_viewable,
            )
        )
    return public_games


@router.get("/authorize", response_model=ItchAuthorizeResponse)
def itch_authorize() -> Any:
    _require_oauth_config()
    state = create_oauth_state()
    authorize_url = build_itch_authorize_url(
        client_id=settings.ITCH_OAUTH_CLIENT_ID,
        redirect_uri=settings.itch_oauth_redirect_uri,
        state=state,
    )
    return ItchAuthorizeResponse(authorize_url=authorize_url, state=state)


@router.post("/callback", response_model=ItchAuthResponse)
async def itch_callback(
    session: SessionDep,
    body: ItchAuthCallback,
    kudos_visitor_id: OptionalKudosVisitor,
) -> Any:
    _require_oauth_config()
    if not verify_oauth_state(body.state):
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    try:
        profile = await fetch_itch_profile(body.access_token)
        itch_games = await fetch_itch_games(body.access_token)
    except ItchApiError as exc:
        raise HTTPException(
            status_code=401,
            detail="Could not verify itch.io credentials",
        ) from exc

    user = crud.get_or_create_itch_user(
        session=session,
        itch_user_id=profile.id,
        itch_username=profile.username,
        display_name=profile.display_name,
    )

    if kudos_visitor_id:
        user = crud.claim_anonymous_kudos_for_user(
            session=session, user=user, visitor_id=kudos_visitor_id
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    io3_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )

    games = await _itch_games_public(session, itch_games)
    user_public = UserPublic.model_validate(user)

    return ItchAuthResponse(
        access_token=io3_token,
        user=user_public,
        games=games,
        itch_username=profile.username,
    )
