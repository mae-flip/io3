from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, Field

from app.services.urls import normalize_itch_url

ITCH_API_BASE = "https://api.itch.io"
ITCH_OAUTH_AUTHORIZE_URL = "https://itch.io/user/oauth"
ITCH_OAUTH_SCOPES = "profile:me profile:games"


class ItchApiError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ItchProfileUser(BaseModel):
    id: int
    username: str
    display_name: str | None = None
    url: str | None = None
    cover_url: str | None = None
    developer: bool = False


class ItchProfileResponse(BaseModel):
    user: ItchProfileUser


class ItchGameSummary(BaseModel):
    id: int
    title: str
    url: str
    cover_url: str | None = None
    short_text: str | None = None
    published: bool = True
    classification: str = "game"


class ItchGamesResponse(BaseModel):
    games: list[ItchGameSummary] = Field(default_factory=list)


def build_itch_authorize_url(
    *, client_id: str, redirect_uri: str, state: str
) -> str:
    params = urlencode(
        {
            "client_id": client_id,
            "scope": ITCH_OAUTH_SCOPES,
            "redirect_uri": redirect_uri,
            "response_type": "token",
            "state": state,
        }
    )
    return f"{ITCH_OAUTH_AUTHORIZE_URL}?{params}"


async def _itch_api_get(
    path: str, access_token: str
) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{ITCH_API_BASE}{path}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if response.status_code >= 400:
        raise ItchApiError(
            "itch.io API request failed",
            status_code=response.status_code,
        )
    data = response.json()
    if isinstance(data, dict) and data.get("errors"):
        raise ItchApiError("; ".join(data["errors"]), status_code=response.status_code)
    return data


async def fetch_itch_profile(access_token: str) -> ItchProfileUser:
    data = await _itch_api_get("/profile", access_token)
    return ItchProfileResponse.model_validate(data).user


async def fetch_itch_games(access_token: str) -> list[ItchGameSummary]:
    data = await _itch_api_get("/profile/games", access_token)
    return ItchGamesResponse.model_validate(data).games


def normalize_itch_game_url(url: str) -> str | None:
    return normalize_itch_url(url)


def owned_game_urls(games: list[ItchGameSummary]) -> dict[str, ItchGameSummary]:
    owned: dict[str, ItchGameSummary] = {}
    for game in games:
        normalized = normalize_itch_game_url(game.url)
        if normalized:
            owned[normalized] = game
    return owned
