from app.models import User, UserProfileLink, UserPublic

ITCH_PROFILE_LINK_LABEL = "itch.io"
MAX_CUSTOM_PROFILE_LINKS = 7


def itch_profile_url(username: str) -> str:
    return f"https://{username}.itch.io"


def is_default_itch_profile_link(url: str, username: str | None) -> bool:
    if not username:
        return False
    return url.rstrip("/") == itch_profile_url(username).rstrip("/")


def default_itch_profile_link(username: str) -> UserProfileLink:
    return UserProfileLink(
        label=ITCH_PROFILE_LINK_LABEL,
        url=itch_profile_url(username),
        managed_by_itch=True,
    )


def custom_profile_links_raw(
    links: list[dict[str, str]], *, username: str | None
) -> list[dict[str, str]]:
    return [
        link
        for link in links
        if not is_default_itch_profile_link(link.get("url", ""), username)
    ]


def resolved_profile_links(user: User) -> list[UserProfileLink]:
    links: list[UserProfileLink] = []
    if user.itch_username:
        links.append(default_itch_profile_link(user.itch_username))
    for raw in custom_profile_links_raw(user.profile_links, username=user.itch_username):
        links.append(
            UserProfileLink(
                label=raw["label"],
                url=raw["url"],
                managed_by_itch=False,
            )
        )
    return links


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
