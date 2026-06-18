import asyncio
import re
from urllib.parse import quote_plus, urlparse

import httpx

from app.core.config import settings
from app.services.itch import ITCH_USER_AGENT
from app.services.urls import normalize_itch_url

ITCH_SEARCH_URL = "https://itch.io/search"

NON_GAME_ITCH_HOSTS = frozenset(
    {"itch.io", "www.itch.io", "static.itch.io", "img.itch.io"}
)

GAME_LINK_PATTERN = re.compile(
    r'href="(https://[a-z0-9-]+\.itch\.io/[^"?#]+)"',
    re.IGNORECASE,
)


def extract_game_urls_from_search_html(html: str) -> set[str]:
    urls: set[str] = set()
    for match in GAME_LINK_PATTERN.finditer(html):
        raw_url = match.group(1)
        host = urlparse(raw_url).netloc.lower().removeprefix("www.")
        if host in NON_GAME_ITCH_HOSTS:
            continue
        normalized = normalize_itch_url(raw_url)
        if normalized:
            urls.add(normalized)
    return urls


def search_query_for_game(*, url: str, title: str) -> str:
    cleaned_title = title.strip()
    if cleaned_title:
        return cleaned_title
    parsed = urlparse(url.strip())
    path = parsed.path.strip("/")
    if path:
        return path.split("/")[-1].replace("-", " ")
    host = parsed.netloc.lower().removeprefix("www.")
    if host.endswith(".itch.io") and host != "itch.io":
        return host.removesuffix(".itch.io")
    return url


async def _fetch_search_page(query: str, *, page: int = 1) -> str:
    page_suffix = f"&page={page}" if page > 1 else ""
    search_url = f"{ITCH_SEARCH_URL}?q={quote_plus(query)}{page_suffix}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            search_url,
            headers={"User-Agent": ITCH_USER_AGENT},
            follow_redirects=True,
        )
    response.raise_for_status()
    return response.text


async def is_listed_in_itch_search(
    *,
    url: str,
    title: str,
    max_pages: int = 3,
) -> bool:
    """True when the game URL appears in itch.io search results (still listed)."""
    normalized = normalize_itch_url(url)
    if not normalized:
        return False

    query = search_query_for_game(url=url, title=title)
    for page in range(1, max_pages + 1):
        html = await _fetch_search_page(query, page=page)
        if normalized in extract_game_urls_from_search_html(html):
            return True
        if page == 1 and "game_cell" not in html and "game_link" not in html:
            break
    return False


async def listing_status_for_games(
    games: list[tuple[str, str]],
) -> dict[str, bool]:
    """Map normalized itch URL to whether it still appears in itch search."""
    semaphore = asyncio.Semaphore(settings.ITCH_FETCH_CONCURRENCY)

    async def check_one(url: str, title: str) -> tuple[str, bool]:
        normalized = normalize_itch_url(url)
        if not normalized:
            return url, False
        async with semaphore:
            listed = await is_listed_in_itch_search(url=url, title=title)
        return normalized, listed

    results = await asyncio.gather(*(check_one(url, title) for url, title in games))
    return dict(results)
