import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

import httpx

from app.models import ItchMetadataPreview, ItchTagPreview, OsPlatform
from app.services.platforms import itch_platform_from_link, platform_label
from app.services.urls import itch_profile_url_from_game_url, normalize_itch_url

ITCH_USER_AGENT = "io3-indexer/1.0 (+metadata-prefill)"


@dataclass
class ItchTag:
    name: str
    slug: str
    itch_url: str
    is_genre: bool = False


@dataclass
class ItchMetadata:
    title: str | None = None
    summary: str | None = None
    cover_image_url: str | None = None
    author_name: str | None = None
    author_url: str | None = None
    tags: list[ItchTag] = field(default_factory=list)
    platforms: list[OsPlatform] = field(default_factory=list)
    normalized_url: str | None = None
    price_cents: int | None = None
    price_currency: str | None = None


def itch_tag_slug_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    if "/tag-" in path:
        return path.rsplit("/tag-", 1)[-1]
    segment = path.rsplit("/", 1)[-1]
    if segment.startswith("tag-"):
        return segment[4:]
    return segment.lower()


def _extract_meta(content: str, property_name: str) -> str | None:
    pattern = rf'<meta\s+property="{property_name}"\s+content="([^"]*)"'
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        return match.group(1)
    pattern = rf'<meta\s+content="([^"]*)"\s+property="{property_name}"'
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _extract_meta_name(content: str, name: str) -> str | None:
    pattern = rf'<meta\s+content="([^"]*)"\s+name="{name}"'
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        return match.group(1)
    pattern = rf'<meta\s+name="{name}"\s+content="([^"]*)"'
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _extract_title_tag(content: str) -> str | None:
    match = re.search(r"<title[^>]*>([^<]+)</title>", content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _parse_author_from_title(title: str | None) -> str | None:
    if not title or " by " not in title:
        return None
    author = title.rsplit(" by ", 1)[-1].strip()
    return author or None


def _parse_game_title_from_title(title: str | None) -> str | None:
    if not title:
        return None
    if " by " in title:
        game_title = title.rsplit(" by ", 1)[0].strip()
        return game_title or None
    return title.strip() or None


def _extract_itch_profile_url(content: str) -> str | None:
    match = re.search(r'href="(https://itch\.io/profile/[^"]+)"', content)
    if match:
        return match.group(1)
    match = re.search(
        r'href="(https://[\w-]+\.itch\.io)"(?:\s|/")',
        content,
    )
    if match:
        return match.group(1)
    return None


def _author_name_from_subdomain(url: str) -> str | None:
    profile_url = itch_profile_url_from_game_url(url)
    if not profile_url:
        return None
    subdomain = profile_url.removeprefix("https://").split(".", 1)[0]
    if not subdomain:
        return None
    return subdomain.replace("-", " ").title()


def _extract_itch_info_links(content: str, label: str) -> list[tuple[str, str]]:
    pattern = rf"<tr><td>{label}</td><td>(.*?)</td></tr>"
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    if not match:
        return []
    cell = match.group(1)
    return [
        (name.strip(), url.strip())
        for url, name in re.findall(r'href="([^"]+)">([^<]+)</a>', cell)
        if name.strip()
    ]


def _extract_itch_platforms(content: str) -> list[OsPlatform]:
    platforms: list[OsPlatform] = []
    seen: set[OsPlatform] = set()

    for name, url in _extract_itch_info_links(content, "Platforms"):
        platform = itch_platform_from_link(name, url)
        if platform and platform not in seen:
            seen.add(platform)
            platforms.append(platform)

    return platforms


def _extract_itch_price(content: str) -> tuple[int | None, str | None]:
    match = re.search(r'"actual_price"\s*:\s*(\d+)', content)
    if match:
        currency_match = re.search(r'"priceCurrency"\s*:\s*"([A-Z]+)"', content)
        currency = currency_match.group(1) if currency_match else "USD"
        return int(match.group(1)), currency

    match = re.search(
        r'"offers"\s*:\s*\{[^}]*"price"\s*:\s*"([0-9.]+)"',
        content,
    )
    if match:
        cents = round(float(match.group(1)) * 100)
        currency_match = re.search(r'"priceCurrency"\s*:\s*"([A-Z]+)"', content)
        currency = currency_match.group(1) if currency_match else "USD"
        return cents, currency

    if re.search(r'href="https://itch\.io/games/free"', content):
        return 0, "USD"

    return None, None


def _extract_itch_tags(content: str) -> list[ItchTag]:
    tags: list[ItchTag] = []
    seen: set[str] = set()

    def add(name: str, url: str, *, is_genre: bool) -> None:
        slug = itch_tag_slug_from_url(url)
        if not slug:
            return
        if slug in seen:
            if is_genre:
                for tag in tags:
                    if tag.slug == slug:
                        tag.is_genre = True
            return
        seen.add(slug)
        tags.append(ItchTag(name=name, slug=slug, itch_url=url, is_genre=is_genre))

    for name, url in _extract_itch_info_links(content, "Genre"):
        add(name, url, is_genre=True)
    for name, url in _extract_itch_info_links(content, "Tags"):
        add(name, url, is_genre=False)

    return tags


def parse_itch_metadata_from_html(content: str, *, url: str) -> ItchMetadata:
    normalized = normalize_itch_url(url)
    metadata = ItchMetadata(normalized_url=normalized)

    page_title = _extract_title_tag(content)
    twitter_title = _extract_meta_name(content, "twitter:title")

    metadata.title = (
        _extract_meta(content, "og:title")
        or _parse_game_title_from_title(twitter_title)
        or _parse_game_title_from_title(page_title)
    )
    metadata.summary = _extract_meta(content, "og:description")
    metadata.cover_image_url = _extract_meta(content, "og:image")
    metadata.author_name = (
        _parse_author_from_title(twitter_title)
        or _parse_author_from_title(page_title)
    )
    metadata.author_url = (
        itch_profile_url_from_game_url(url) or _extract_itch_profile_url(content)
    )
    if not metadata.author_name:
        metadata.author_name = _author_name_from_subdomain(url)
    metadata.tags = _extract_itch_tags(content)
    metadata.platforms = _extract_itch_platforms(content)
    metadata.price_cents, metadata.price_currency = _extract_itch_price(content)

    return metadata


def _fetch_itch_html(url: str) -> str | None:
    normalized = normalize_itch_url(url)
    if not normalized:
        return None
    try:
        with httpx.Client(follow_redirects=True, timeout=10.0) as client:
            response = client.get(
                normalized,
                headers={"User-Agent": ITCH_USER_AGENT},
            )
            response.raise_for_status()
            return response.text
    except httpx.HTTPError:
        return None


def fetch_itch_metadata_sync(url: str) -> ItchMetadata:
    normalized = normalize_itch_url(url)
    metadata = ItchMetadata(normalized_url=normalized)
    if not normalized:
        return metadata

    content = _fetch_itch_html(url)
    if content:
        return parse_itch_metadata_from_html(content, url=url)

    metadata.author_url = itch_profile_url_from_game_url(url)
    metadata.author_name = _author_name_from_subdomain(url)
    return metadata


def _metadata_to_preview(url: str, metadata: ItchMetadata) -> ItchMetadataPreview:
    return ItchMetadataPreview(
        url=url,
        title=metadata.title,
        summary=metadata.summary,
        cover_image_url=metadata.cover_image_url,
        author_name=metadata.author_name,
        author_url=metadata.author_url,
        tags=[
            ItchTagPreview(
                name=tag.name,
                slug=tag.slug,
                itch_url=tag.itch_url,
                is_genre=tag.is_genre,
            )
            for tag in metadata.tags
        ],
        normalized_url=metadata.normalized_url,
    )


async def fetch_itch_metadata(url: str) -> ItchMetadataPreview:
    normalized = normalize_itch_url(url)
    if not normalized:
        return ItchMetadataPreview(url=url, normalized_url=normalized)

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(
                normalized,
                headers={"User-Agent": ITCH_USER_AGENT},
            )
            response.raise_for_status()
            content = response.text
    except httpx.HTTPError:
        metadata = fetch_itch_metadata_sync(url)
        return _metadata_to_preview(url, metadata)

    metadata = parse_itch_metadata_from_html(content, url=url)
    return _metadata_to_preview(url, metadata)
