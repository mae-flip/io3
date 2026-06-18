import asyncio
from unittest.mock import AsyncMock, patch

from app.services.itch_api import (
    ItchApiError,
    ItchGameSummary,
    build_itch_authorize_url,
    fetch_itch_games,
    fetch_itch_profile,
    owned_game_urls,
)


def test_build_itch_authorize_url() -> None:
    url = build_itch_authorize_url(
        client_id="test-client",
        redirect_uri="http://localhost:5173/submit/callback",
        state="abc123",
    )
    assert url.startswith("https://itch.io/user/oauth?")
    assert "client_id=test-client" in url
    assert "response_type=token" in url
    assert "state=abc123" in url
    assert "profile%3Ame+profile%3Agames" in url


def test_fetch_itch_profile() -> None:
    profile_data = {
        "user": {
            "id": 29789,
            "username": "fasterthanlime",
            "display_name": "Amos",
            "url": "https://fasterthanlime.itch.io",
        }
    }
    with patch(
        "app.services.itch_api._itch_api_get",
        new_callable=AsyncMock,
        return_value=profile_data,
    ):
        profile = asyncio.run(fetch_itch_profile("token"))
    assert profile.id == 29789
    assert profile.username == "fasterthanlime"


def test_fetch_itch_games() -> None:
    games_data = {
        "games": [
            {
                "id": 3,
                "title": "X-Moon",
                "url": "http://leafo.itch.io/x-moon",
                "published": True,
                "classification": "game",
            }
        ]
    }
    with patch(
        "app.services.itch_api._itch_api_get",
        new_callable=AsyncMock,
        return_value=games_data,
    ):
        games = asyncio.run(fetch_itch_games("token"))
    assert len(games) == 1
    assert games[0].title == "X-Moon"


def test_fetch_itch_profile_api_error() -> None:
    with patch(
        "app.services.itch_api._itch_api_get",
        new_callable=AsyncMock,
        side_effect=ItchApiError("bad token", status_code=401),
    ):
        try:
            asyncio.run(fetch_itch_profile("bad"))
            assert False, "expected ItchApiError"
        except ItchApiError:
            pass


def test_owned_game_urls_normalizes() -> None:
    games = [
        ItchGameSummary(
            id=1,
            title="Game",
            url="https://creator.itch.io/my-game/",
            published=True,
            classification="game",
        )
    ]
    owned = owned_game_urls(games)
    assert "https://creator.itch.io/my-game" in owned
