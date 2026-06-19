from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.services.itch import ItchMetadata
from tests.utils.game import create_random_game
from tests.utils.user import create_itch_user


def test_read_admin_games_requires_auth(client: TestClient, db: Session) -> None:
    create_random_game(db, approved=True)
    response = client.get(f"{settings.API_V1_STR}/admin/games")
    assert response.status_code == 401


def test_read_admin_games(client: TestClient, db: Session, moderator_token_headers: dict[str, str]) -> None:
    create_random_game(db, approved=True)
    response = client.get(
        f"{settings.API_V1_STR}/admin/games", headers=moderator_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 1
    assert "itch_url" in content["data"][0]


def test_read_admin_games_pagination(
    client: TestClient, db: Session, moderator_token_headers: dict[str, str]
) -> None:
    from tests.utils.game import set_game_cache

    for index in range(3):
        game = create_random_game(db, approved=True)
        set_game_cache(db, game, title=f"Paginated Game {index}")

    page_one = client.get(
        f"{settings.API_V1_STR}/admin/games",
        headers=moderator_token_headers,
        params={"skip": 0, "limit": 2},
    )
    assert page_one.status_code == 200
    content = page_one.json()
    assert content["count"] >= 3
    assert len(content["data"]) == 2

    page_two = client.get(
        f"{settings.API_V1_STR}/admin/games",
        headers=moderator_token_headers,
        params={"skip": 2, "limit": 2},
    )
    assert page_two.status_code == 200
    page_one_ids = {item["id"] for item in content["data"]}
    page_two_ids = {item["id"] for item in page_two.json()["data"]}
    assert page_one_ids.isdisjoint(page_two_ids)


def test_read_admin_games_search(
    client: TestClient, db: Session, moderator_token_headers: dict[str, str]
) -> None:
    from tests.utils.game import set_game_cache

    matching = create_random_game(db, approved=True)
    other = create_random_game(db, approved=True)
    set_game_cache(db, matching, title="Unique Admin Search Target")
    set_game_cache(db, other, title="Something Else")

    response = client.get(
        f"{settings.API_V1_STR}/admin/games",
        headers=moderator_token_headers,
        params={"search": "Unique Admin Search"},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    assert content["data"][0]["id"] == str(matching.id)


def test_create_admin_game(client: TestClient, moderator_token_headers: dict[str, str]) -> None:
    from unittest.mock import patch

    metadata = ItchMetadata(
        normalized_url="https://creator.itch.io/admin-added-game",
        title="Admin Added Game",
        summary="Short summary",
    )
    with (
        patch(
            "app.crud.fetch_itch_metadata_sync",
            return_value=metadata,
        ),
        patch(
            "app.crud.check_public_viewability_sync",
            return_value=True,
        ),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/admin/games",
            json={"url": "https://creator.itch.io/admin-added-game"},
            headers=moderator_token_headers,
        )
    assert response.status_code == 200
    content = response.json()
    assert content["itch_url"] == "https://creator.itch.io/admin-added-game"
    assert content["status"] == "approved"
    assert content["title"] == "Admin Added Game"


def test_delete_admin_game(
    client: TestClient, db: Session, moderator_token_headers: dict[str, str]
) -> None:
    game = create_random_game(db, approved=True)
    response = client.request(
        "DELETE",
        f"{settings.API_V1_STR}/admin/games/{game.id}",
        headers=moderator_token_headers,
        json={"removal_reason": "Does not meet indexing guidelines"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Game removed from the index"

    list_response = client.get(
        f"{settings.API_V1_STR}/admin/games", headers=moderator_token_headers
    )
    ids = [item["id"] for item in list_response.json()["data"]]
    assert str(game.id) not in ids

    removed_response = client.get(
        f"{settings.API_V1_STR}/admin/games/removed",
        headers=moderator_token_headers,
    )
    assert removed_response.status_code == 200
    removed_ids = [item["id"] for item in removed_response.json()["data"]]
    assert str(game.id) in removed_ids
    removed_game = next(
        item for item in removed_response.json()["data"] if item["id"] == str(game.id)
    )
    assert removed_game["status"] == "archived"
    assert removed_game["removal_reason"] == "Does not meet indexing guidelines"


def test_delete_admin_game_sends_removal_email(
    client: TestClient, db: Session, moderator_token_headers: dict[str, str]
) -> None:
    submitter = create_itch_user(db, contact_email="author@example.com")
    game = create_random_game(db, approved=True, submitter=submitter)

    with (
        patch.object(settings, "SMTP_HOST", "smtp.example.com"),
        patch.object(settings, "EMAILS_FROM_EMAIL", "staff@example.com"),
        patch("app.services.game_removal_email.send_email") as send_email,
    ):
        response = client.request(
            "DELETE",
            f"{settings.API_V1_STR}/admin/games/{game.id}",
            headers=moderator_token_headers,
            json={"removal_reason": "Does not meet indexing guidelines"},
        )

    assert response.status_code == 200
    send_email.assert_called_once()
    call_kwargs = send_email.call_args.kwargs
    assert call_kwargs["email_to"] == "author@example.com"
    assert "Does not meet indexing guidelines" in call_kwargs["html_content"]
    assert "author@example.com" not in call_kwargs["subject"]


def test_delete_admin_game_skips_email_without_contact_email(
    client: TestClient, db: Session, moderator_token_headers: dict[str, str]
) -> None:
    game = create_random_game(db, approved=True)

    with (
        patch.object(settings, "SMTP_HOST", "smtp.example.com"),
        patch.object(settings, "EMAILS_FROM_EMAIL", "staff@example.com"),
        patch("app.services.game_removal_email.send_email") as send_email,
    ):
        response = client.request(
            "DELETE",
            f"{settings.API_V1_STR}/admin/games/{game.id}",
            headers=moderator_token_headers,
            json={"removal_reason": "Does not meet indexing guidelines"},
        )

    assert response.status_code == 200
    send_email.assert_not_called()


def test_restore_admin_game(
    client: TestClient, db: Session, moderator_token_headers: dict[str, str]
) -> None:
    game = create_random_game(db, approved=True)
    client.request(
        "DELETE",
        f"{settings.API_V1_STR}/admin/games/{game.id}",
        headers=moderator_token_headers,
        json={"removal_reason": "Removed for testing restore"},
    )

    response = client.post(
        f"{settings.API_V1_STR}/admin/games/{game.id}/restore",
        headers=moderator_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"

    list_response = client.get(
        f"{settings.API_V1_STR}/admin/games", headers=moderator_token_headers
    )
    ids = [item["id"] for item in list_response.json()["data"]]
    assert str(game.id) in ids

    removed_response = client.get(
        f"{settings.API_V1_STR}/admin/games/removed",
        headers=moderator_token_headers,
    )
    removed_ids = [item["id"] for item in removed_response.json()["data"]]
    assert str(game.id) not in removed_ids


def test_restore_admin_game_not_removed(
    client: TestClient, db: Session, moderator_token_headers: dict[str, str]
) -> None:
    game = create_random_game(db, approved=True)
    response = client.post(
        f"{settings.API_V1_STR}/admin/games/{game.id}/restore",
        headers=moderator_token_headers,
    )
    assert response.status_code == 400


def test_feature_admin_game(
    client: TestClient, db: Session, moderator_token_headers: dict[str, str]
) -> None:
    game = create_random_game(db, approved=True)
    response = client.post(
        f"{settings.API_V1_STR}/admin/games/{game.id}/feature",
        headers=moderator_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["featured_at"] is not None


def test_unfeature_admin_game(
    client: TestClient, db: Session, moderator_token_headers: dict[str, str]
) -> None:
    game = create_random_game(db, approved=True)
    client.post(
        f"{settings.API_V1_STR}/admin/games/{game.id}/feature",
        headers=moderator_token_headers,
    )
    response = client.post(
        f"{settings.API_V1_STR}/admin/games/{game.id}/unfeature",
        headers=moderator_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["featured_at"] is None


def test_read_admin_users_requires_owner(
    client: TestClient, db: Session, moderator_token_headers: dict[str, str]
) -> None:
    create_itch_user(db)
    response = client.get(
        f"{settings.API_V1_STR}/admin/users", headers=moderator_token_headers
    )
    assert response.status_code == 403


def test_read_admin_users(
    client: TestClient, db: Session, owner_token_headers: dict[str, str]
) -> None:
    create_itch_user(db, itch_username="mod-candidate")
    response = client.get(
        f"{settings.API_V1_STR}/admin/users", headers=owner_token_headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 1
    assert "itch_username" in content["data"][0]


def test_update_admin_user_moderator_status(
    client: TestClient, db: Session, owner_token_headers: dict[str, str]
) -> None:
    user = create_itch_user(db, itch_username="future-mod")
    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{user.id}",
        json={"is_moderator": True},
        headers=owner_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_moderator"] is True

    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{user.id}",
        json={"is_moderator": False},
        headers=owner_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_moderator"] is False


def test_read_newsletter_subscribers_requires_owner(
    client: TestClient, db: Session, moderator_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/admin/newsletter/subscribers",
        headers=moderator_token_headers,
    )
    assert response.status_code == 403


def test_read_newsletter_subscribers(
    client: TestClient, db: Session, owner_token_headers: dict[str, str]
) -> None:
    from app import crud

    crud.subscribe_newsletter(session=db, email="one@example.com")
    crud.subscribe_newsletter(session=db, email="two@example.com")

    response = client.get(
        f"{settings.API_V1_STR}/admin/newsletter/subscribers",
        headers=owner_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["count"] == 2


def test_download_newsletter_subscribers_csv(
    client: TestClient, db: Session, owner_token_headers: dict[str, str]
) -> None:
    from app import crud

    crud.subscribe_newsletter(session=db, email="alpha@example.com")
    crud.subscribe_newsletter(session=db, email="beta@example.com")

    response = client.get(
        f"{settings.API_V1_STR}/admin/newsletter/subscribers.csv",
        headers=owner_token_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    lines = response.text.strip().splitlines()
    assert lines[0] == "email"
    assert "alpha@example.com" in lines
    assert "beta@example.com" in lines
