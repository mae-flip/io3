import re
from urllib.parse import urlparse

from sqlmodel import Session, select

from app.models import Game


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "game"


def slug_from_itch_url(url: str) -> str:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.strip("/")
    parts: list[str] = []
    if host.endswith(".itch.io") and host != "itch.io":
        subdomain = host.removesuffix(".itch.io")
        if subdomain:
            parts.append(subdomain)
    if path:
        parts.append(path.split("/")[-1])
    return slugify("-".join(parts) if parts else "game")


def unique_game_slug(session: Session, title: str) -> str:
    base = slugify(title)
    slug = base
    counter = 2
    while session.exec(select(Game).where(Game.slug == slug)).first():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def unique_game_slug_from_url(session: Session, url: str) -> str:
    base = slug_from_itch_url(url)
    slug = base
    counter = 2
    while session.exec(select(Game).where(Game.slug == slug)).first():
        slug = f"{base}-{counter}"
        counter += 1
    return slug
