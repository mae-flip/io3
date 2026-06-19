import re

from pydantic import HttpUrl, TypeAdapter, ValidationError

from app.models import User, UserProfileLink, UserPublic

MAX_CUSTOM_PROFILE_LINKS = 7
_http_url_adapter = TypeAdapter(HttpUrl)


def itch_profile_url(username: str) -> str:
    return f"https://{username}.itch.io"


class InvalidProfileLinkUrlError(ValueError):
    pass


def normalize_profile_link_url(raw_url: str) -> str:
    stripped = raw_url.strip()
    if not stripped:
        raise InvalidProfileLinkUrlError("Link URL is required")
    if not re.match(r"^https?://", stripped, re.IGNORECASE):
        stripped = f"https://{stripped}"
    try:
        return str(_http_url_adapter.validate_python(stripped))
    except ValidationError as exc:
        raise InvalidProfileLinkUrlError(
            "Each link URL must be a valid web address"
        ) from exc


def is_default_itch_profile_link(url: str, username: str | None) -> bool:
    if not username:
        return False
    return url.rstrip("/") == itch_profile_url(username).rstrip("/")


def default_itch_profile_link(username: str) -> UserProfileLink:
    return UserProfileLink(
        url=itch_profile_url(username),
        managed_by_itch=True,
    )


def profile_link_url(raw: dict[str, str] | str) -> str:
    if isinstance(raw, str):
        return raw
    return raw.get("url", "")


def custom_profile_links_raw(
    links: list[dict[str, str] | str], *, username: str | None
) -> list[str]:
    urls: list[str] = []
    for link in links:
        url = profile_link_url(link)
        if not url or is_default_itch_profile_link(url, username):
            continue
        urls.append(url)
    return urls


def resolved_profile_links(user: User) -> list[UserProfileLink]:
    links: list[UserProfileLink] = []
    if user.itch_username:
        links.append(default_itch_profile_link(user.itch_username))
    for url in custom_profile_links_raw(user.profile_links, username=user.itch_username):
        links.append(
            UserProfileLink(
                url=url,
                managed_by_itch=False,
            )
        )
    return links


def author_matches_submitter(
    *,
    author_url: str | None,
    author_name: str | None,
    submitter: User,
) -> bool:
    if not submitter.itch_username:
        return False
    submitter_profile = itch_profile_url(submitter.itch_username)
    if author_url:
        return author_url.rstrip("/").lower() == submitter_profile.rstrip("/").lower()
    if author_name:
        return author_name.lower() == submitter.itch_username.lower()
    return False


def profile_links_for_displayed_author(
    *,
    author_url: str | None,
    author_name: str | None,
    submitter: User | None,
) -> list[UserProfileLink]:
    if submitter is None:
        return []
    if not author_matches_submitter(
        author_url=author_url,
        author_name=author_name,
        submitter=submitter,
    ):
        return []
    return resolved_profile_links(submitter)


def user_to_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        itch_username=user.itch_username,
        display_name=user.display_name,
        is_owner=user.is_owner,
        is_moderator=user.is_moderator,
        created_at=user.created_at,
        profile_links=resolved_profile_links(user),
    )
