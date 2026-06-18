import re
from urllib.parse import urlparse, urlunparse

from app.models import LinkPlatform

ITCH_HOSTS = {"itch.io", "www.itch.io"}


def detect_platform(url: str) -> LinkPlatform:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    if host == "itch.io" or host.endswith(".itch.io"):
        return LinkPlatform.itch
    if host in {"store.steampowered.com", "steampowered.com"}:
        return LinkPlatform.steam
    return LinkPlatform.website


def itch_profile_url_from_game_url(url: str) -> str | None:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.")
    if host.endswith(".itch.io") and host != "itch.io":
        subdomain = host.removesuffix(".itch.io")
        if subdomain:
            return f"https://{subdomain}.itch.io"
    return None


def normalize_itch_url(url: str) -> str | None:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.")
    if host not in ITCH_HOSTS and not host.endswith(".itch.io"):
        return None

    path = parsed.path.rstrip("/")
    if not path or path == "/":
        return None

    clean = urlunparse(("https", parsed.netloc.lower(), path, "", "", ""))
    return clean


def normalize_url(url: str, platform: LinkPlatform) -> str:
    if platform == LinkPlatform.itch:
        normalized = normalize_itch_url(url)
        if normalized:
            return normalized
    parsed = urlparse(url.strip())
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme or "https", parsed.netloc.lower(), path, "", "", ""))


def is_allowed_submission_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    if not parsed.netloc:
        return False
    host = parsed.netloc.lower().removeprefix("www.")
    if host in ITCH_HOSTS or host.endswith(".itch.io"):
        return True
    if host in {"store.steampowered.com", "steampowered.com"}:
        return True
    return bool(re.match(r"^https?://", url.strip()))
