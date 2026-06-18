import asyncio
from unittest.mock import AsyncMock, patch

from app.services.itch_search import (
    extract_game_urls_from_search_html,
    is_listed_in_itch_search,
    search_query_for_game,
)


def test_extract_game_urls_from_search_html() -> None:
    html = """
    <a href="https://creator.itch.io/my-game">Game</a>
    <a href="https://static.itch.io/foo">Static</a>
    <a href="https://other.itch.io/another-game/">Other</a>
    """
    urls = extract_game_urls_from_search_html(html)
    assert "https://creator.itch.io/my-game" in urls
    assert "https://other.itch.io/another-game" in urls
    assert not any("static.itch.io" in url for url in urls)


def test_search_query_for_game_prefers_title() -> None:
    assert (
        search_query_for_game(
            url="https://creator.itch.io/my-game",
            title="My Queer Game",
        )
        == "My Queer Game"
    )


def test_search_query_for_game_falls_back_to_slug() -> None:
    assert search_query_for_game(
        url="https://creator.itch.io/my-game",
        title="",
    ) == "my game"


def test_is_listed_in_itch_search_true() -> None:
    html = '<a href="https://creator.itch.io/target-game">Target</a>'
    with patch(
        "app.services.itch_search._fetch_search_page",
        new_callable=AsyncMock,
        return_value=html,
    ):
        listed = asyncio.run(
            is_listed_in_itch_search(
                url="https://creator.itch.io/target-game",
                title="Target Game",
            )
        )
    assert listed is True


def test_is_listed_in_itch_search_false() -> None:
    html = '<a href="https://creator.itch.io/other-game">Other</a>'
    with patch(
        "app.services.itch_search._fetch_search_page",
        new_callable=AsyncMock,
        return_value=html,
    ):
        listed = asyncio.run(
            is_listed_in_itch_search(
                url="https://creator.itch.io/target-game",
                title="Target Game",
            )
        )
    assert listed is False
