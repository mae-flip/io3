from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.user_profile import itch_profile_url


def test_read_user_me(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert "itch_username" in content
    assert content["is_owner"] is False
    assert content["is_moderator"] is False
    assert len(content["profile_links"]) == 1
    assert content["profile_links"][0]["label"] == "itch.io"
    assert content["profile_links"][0]["managed_by_itch"] is True
    assert content["profile_links"][0]["url"] == itch_profile_url(
        content["itch_username"]
    )


def test_read_user_me_owner(
    client: TestClient, owner_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/users/me", headers=owner_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["is_owner"] is True
    assert content["itch_username"] == settings.ITCH_OWNER_USERNAME


def test_read_user_me_unauthorized(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 401


def test_update_user_profile_links(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    me_response = client.get(
        f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers
    )
    itch_username = me_response.json()["itch_username"]

    response = client.patch(
        f"{settings.API_V1_STR}/users/me/profile-links",
        headers=normal_user_token_headers,
        json={
            "links": [
                {"label": "Bluesky", "url": "https://bsky.app/profile/example"},
                {"label": "Ko-fi", "url": "https://ko-fi.com/example"},
            ]
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["profile_links"]) == 3
    assert content["profile_links"][0]["label"] == "itch.io"
    assert content["profile_links"][0]["managed_by_itch"] is True
    assert content["profile_links"][0]["url"] == itch_profile_url(itch_username)
    assert content["profile_links"][1]["label"] == "Bluesky"
    assert content["profile_links"][2]["label"] == "Ko-fi"

    me_response = client.get(
        f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers
    )
    assert me_response.json()["profile_links"] == content["profile_links"]


def test_update_user_profile_links_strips_itch_link(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    me_response = client.get(
        f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers
    )
    itch_username = me_response.json()["itch_username"]

    response = client.patch(
        f"{settings.API_V1_STR}/users/me/profile-links",
        headers=normal_user_token_headers,
        json={
            "links": [
                {
                    "label": "itch.io",
                    "url": itch_profile_url(itch_username),
                    "managed_by_itch": True,
                },
                {"label": "Bluesky", "url": "https://bsky.app/profile/example"},
            ]
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["profile_links"]) == 2
    assert content["profile_links"][0]["managed_by_itch"] is True
    assert content["profile_links"][1]["label"] == "Bluesky"


def test_update_user_profile_links_rejects_invalid_url(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/profile-links",
        headers=normal_user_token_headers,
        json={"links": [{"label": "Bad", "url": "not-a-url"}]},
    )
    assert response.status_code == 422
