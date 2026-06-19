from fastapi.testclient import TestClient
from sqlmodel import Session

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
    assert content["has_contact_email"] is True
    assert content["contact_email"] is not None
    assert len(content["profile_links"]) == 1
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
                {"url": "https://bsky.app/profile/example"},
                {"url": "https://ko-fi.com/example"},
            ]
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["profile_links"]) == 3
    assert content["profile_links"][0]["managed_by_itch"] is True
    assert content["profile_links"][0]["url"] == itch_profile_url(itch_username)
    assert content["profile_links"][1]["url"] == "https://bsky.app/profile/example"
    assert content["profile_links"][2]["url"] == "https://ko-fi.com/example"

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
                {"url": itch_profile_url(itch_username)},
                {"url": "https://bsky.app/profile/example"},
            ]
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["profile_links"]) == 2
    assert content["profile_links"][0]["managed_by_itch"] is True
    assert content["profile_links"][1]["url"] == "https://bsky.app/profile/example"


def test_update_user_profile_links_rejects_invalid_url(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/profile-links",
        headers=normal_user_token_headers,
        json={"links": [{"url": "not a url"}]},
    )
    assert response.status_code == 422


def test_update_user_profile_links_accepts_url_without_scheme(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/profile-links",
        headers=normal_user_token_headers,
        json={
            "links": [
                {
                    "url": "www.tumblr.com/pineappical",
                }
            ]
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content["profile_links"][-1]["url"] == "https://www.tumblr.com/pineappical"


def test_read_user_me_without_contact_email(db, client: TestClient) -> None:
    from tests.utils.user import authentication_token_for_user, create_itch_user

    user = create_itch_user(db)
    headers = authentication_token_for_user(user=user)
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["has_contact_email"] is False
    assert response.json()["contact_email"] is None


def test_update_user_contact_email(
    client: TestClient, db: Session
) -> None:
    from tests.utils.user import authentication_token_for_user, create_itch_user

    user = create_itch_user(db)
    headers = authentication_token_for_user(user=user)
    email = "creator@example.com"

    response = client.patch(
        f"{settings.API_V1_STR}/users/me/contact-email",
        headers=headers,
        json={"email": email},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["has_contact_email"] is True
    assert content["contact_email"] == email

    db.refresh(user)
    assert user.email == email


def test_update_user_contact_email_rejects_duplicate(
    client: TestClient, db: Session
) -> None:
    from tests.utils.user import authentication_token_for_user, create_itch_user

    create_itch_user(db, contact_email="taken@example.com")
    user = create_itch_user(db)
    headers = authentication_token_for_user(user=user)

    response = client.patch(
        f"{settings.API_V1_STR}/users/me/contact-email",
        headers=headers,
        json={"email": "taken@example.com"},
    )
    assert response.status_code == 409


def test_submit_batch_requires_contact_email(
    client: TestClient, db: Session
) -> None:
    from tests.utils.user import authentication_token_for_user, create_itch_user

    user = create_itch_user(db)
    headers = authentication_token_for_user(user=user)

    response = client.post(
        f"{settings.API_V1_STR}/games/submit-batch",
        headers=headers,
        json={
            "urls": ["https://creator.itch.io/batch-game"],
            "itch_access_token": "itch-token",
        },
    )
    assert response.status_code == 403
    assert "contact email" in response.json()["detail"].lower()
