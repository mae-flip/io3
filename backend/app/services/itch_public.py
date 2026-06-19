import asyncio
import re

import httpx

from app.core.config import settings
from app.services.itch import ITCH_USER_AGENT, _fetch_itch_html
from app.services.urls import normalize_itch_url

GATED_PAGE_MARKERS = (
    "game_password_page",
    "game_not_published_error_page",
    'name="game_password"',
    "A password is required to view this page",
    "You do not have access to this page",
    "has been restricted by the author",
)

NOT_PUBLIC_DETAIL = (
    "Game is not publicly viewable on itch.io "
    "(restricted access or password-protected)"
)


def is_itch_page_publicly_viewable(content: str) -> bool:
    """True when an anonymous visitor can view the full itch.io game page."""
    if not content:
        return False
    if any(marker in content for marker in GATED_PAGE_MARKERS):
        return False
    if re.search(r'property="og:title"\s+content="itch\.io"', content, re.IGNORECASE):
        return False
    return bool(re.search(r'<meta\s+name="itch:path"\s+content="games/', content))


def check_public_viewability_sync(url: str) -> bool:
    normalized = normalize_itch_url(url)
    if not normalized:
        return False
    content = _fetch_itch_html(normalized)
    return is_itch_page_publicly_viewable(content or "")


async def is_publicly_viewable(url: str) -> bool:
    normalized = normalize_itch_url(url)
    if not normalized:
        return False
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(
                normalized,
                headers={"User-Agent": ITCH_USER_AGENT},
            )
            if response.status_code >= 400:
                return False
            return is_itch_page_publicly_viewable(response.text)
    except httpx.HTTPError:
        return False


async def public_viewability_for_games(
    games: list[tuple[str, str]],
) -> dict[str, bool]:
    """Map normalized itch URL to whether the page is publicly viewable."""
    semaphore = asyncio.Semaphore(settings.ITCH_FETCH_CONCURRENCY)

    async def check_one(url: str, _title: str) -> tuple[str, bool]:
        normalized = normalize_itch_url(url)
        if not normalized:
            return url, False
        async with semaphore:
            viewable = await is_publicly_viewable(url)
        return normalized, viewable

    results = await asyncio.gather(*(check_one(url, title) for url, title in games))
    return dict(results)
