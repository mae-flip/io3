from fastapi.testclient import TestClient

from app.core.config import settings


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
