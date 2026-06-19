from typing import Any

from fastapi import APIRouter
from pydantic import HttpUrl, TypeAdapter

from app.api.deps import CurrentUser, SessionDep
from app.models import UserProfileLink, UserProfileLinksUpdate, UserPublic
from app.services.user_profile import (
    MAX_CUSTOM_PROFILE_LINKS,
    is_default_itch_profile_link,
    user_to_public,
)

router = APIRouter(prefix="/users", tags=["users"])

_http_url_adapter = TypeAdapter(HttpUrl)


def _normalize_custom_profile_links(
    links: list[UserProfileLink], *, username: str | None
) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for link in links:
        if link.managed_by_itch or is_default_itch_profile_link(link.url, username):
            continue
        normalized.append(
            {
                "label": link.label.strip(),
                "url": str(_http_url_adapter.validate_python(link.url.strip())),
            }
        )
        if len(normalized) >= MAX_CUSTOM_PROFILE_LINKS:
            break
    return normalized


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return user_to_public(current_user)


@router.patch("/me/profile-links", response_model=UserPublic)
def update_user_profile_links(
    session: SessionDep,
    current_user: CurrentUser,
    body: UserProfileLinksUpdate,
) -> Any:
    """
    Update custom profile links. The itch.io profile link is always included
    automatically and cannot be removed.
    """
    current_user.profile_links = _normalize_custom_profile_links(
        body.links, username=current_user.itch_username
    )
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return user_to_public(current_user)
