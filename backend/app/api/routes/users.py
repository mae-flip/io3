from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import UserProfileLinkUpdate, UserProfileLinksUpdate, UserPublic
from app.services.user_profile import (
    InvalidProfileLinkUrlError,
    MAX_CUSTOM_PROFILE_LINKS,
    is_default_itch_profile_link,
    normalize_profile_link_url,
    user_to_public,
)

router = APIRouter(prefix="/users", tags=["users"])


def _normalize_custom_profile_links(
    links: list[UserProfileLinkUpdate], *, username: str | None
) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for link in links:
        if is_default_itch_profile_link(link.url, username):
            continue
        try:
            url = normalize_profile_link_url(link.url)
        except InvalidProfileLinkUrlError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        normalized.append({"url": url})
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
