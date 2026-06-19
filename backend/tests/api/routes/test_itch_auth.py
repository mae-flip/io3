from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.services.itch_api import ItchGameSummary, ItchProfileUser
from app.services.itch_oauth_state import create_oauth_state


def test_itch_authorize_not_configured(client: TestClient) -> None:
    with patch.object(settings, "ITCH_OAUTH_CLIENT_ID", ""):
        response = client.get(f"{settings.API_V1_STR}/auth/itch/authorize")
    assert response.status_code == 503


def test_itch_authorize_returns_url(client: TestClient) -> None:
    with patch.object(settings, "ITCH_OAUTH_CLIENT_ID", "test-client-id"):
        response = client.get(f"{settings.API_V1_STR}/auth/itch/authorize")
    assert response.status_code == 200
    content = response.json()
    assert "authorize_url" in content
    assert "state" in content
    assert "test-client-id" in content["authorize_url"]


def test_itch_callback_invalid_state(client: TestClient) -> None:
    with patch.object(settings, "ITCH_OAUTH_CLIENT_ID", "test-client-id"):
        response = client.post(
            f"{settings.API_V1_STR}/auth/itch/callback",
            json={"access_token": "itch-token", "state": "invalid"},
        )
    assert response.status_code == 400


def test_itch_callback_creates_shadow_user(client: TestClient, db: Session) -> None:
    profile = ItchProfileUser(
        id=4242,
        username="queerdev",
        display_name="Queer Dev",
        url="https://queerdev.itch.io",
    )
    games = [
        ItchGameSummary(
            id=99,
            title="My Game",
            url="https://queerdev.itch.io/my-game",
            published=True,
            classification="game",
        ),
        ItchGameSummary(
            id=100,
            title="Draft Tool",
            url="https://queerdev.itch.io/tool",
            published=False,
            classification="tool",
        ),
    ]
    state = create_oauth_state()

    with (
        patch.object(settings, "ITCH_OAUTH_CLIENT_ID", "test-client-id"),
        patch(
            "app.api.routes.itch_auth.fetch_itch_profile",
            new_callable=AsyncMock,
            return_value=profile,
        ),
        patch(
            "app.api.routes.itch_auth.fetch_itch_games",
            new_callable=AsyncMock,
            return_value=games,
        ),
        patch(
            "app.api.routes.itch_auth.listing_status_for_games",
            new_callable=AsyncMock,
            return_value={"https://queerdev.itch.io/my-game": False},
        ),
        patch(
            "app.api.routes.itch_auth.public_viewability_for_games",
            new_callable=AsyncMock,
            return_value={"https://queerdev.itch.io/my-game": True},
        ),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/auth/itch/callback",
            json={"access_token": "itch-token", "state": state},
        )

    assert response.status_code == 200
    content = response.json()
    assert content["itch_username"] == "queerdev"
    assert content["access_token"]
    assert content["user"]["itch_username"] == "queerdev"
    assert len(content["games"]) == 1
    assert content["games"][0]["title"] == "My Game"

    from app import crud

    user = crud.get_user_by_itch_user_id(session=db, itch_user_id=4242)
    assert user is not None
    assert user.can_submit is True


def test_itch_callback_marks_moderator_removed_games(
    client: TestClient, db: Session
) -> None:
    from tests.utils.game import create_random_game

    game = create_random_game(db, approved=True)
    crud.remove_game_from_index(
        session=db, db_game=game, removal_reason="Not eligible for io3"
    )

    profile = ItchProfileUser(
        id=5252,
        username="removeddev",
        display_name="Removed Dev",
        url="https://removeddev.itch.io",
    )
    games = [
        ItchGameSummary(
            id=101,
            title="Removed Game",
            url=game.itch_url,
            published=True,
            classification="game",
        ),
    ]
    state = create_oauth_state()

    with (
        patch.object(settings, "ITCH_OAUTH_CLIENT_ID", "test-client-id"),
        patch(
            "app.api.routes.itch_auth.fetch_itch_profile",
            new_callable=AsyncMock,
            return_value=profile,
        ),
        patch(
            "app.api.routes.itch_auth.fetch_itch_games",
            new_callable=AsyncMock,
            return_value=games,
        ),
        patch(
            "app.api.routes.itch_auth.listing_status_for_games",
            new_callable=AsyncMock,
            return_value={game.itch_url: False},
        ),
        patch(
            "app.api.routes.itch_auth.public_viewability_for_games",
            new_callable=AsyncMock,
            return_value={game.itch_url: True},
        ),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/auth/itch/callback",
            json={"access_token": "itch-token", "state": state},
        )

    assert response.status_code == 200
    content = response.json()
    assert len(content["games"]) == 1
    assert content["games"][0]["removed_by_moderator"] is True
    assert content["games"][0]["already_indexed"] is False
    assert content["games"][0]["removal_reason"] == "Not eligible for io3"


def test_itch_callback_sets_owner_for_configured_username(
    client: TestClient, db: Session
) -> None:
    owner_username = "configured-owner"
    profile = ItchProfileUser(
        id=7777,
        username=owner_username,
        display_name="Site Owner",
        url="https://owner.itch.io",
    )
    state = create_oauth_state()

    with (
        patch.object(settings, "ITCH_OAUTH_CLIENT_ID", "test-client-id"),
        patch.object(settings, "ITCH_OWNER_USERNAME", owner_username),
        patch(
            "app.api.routes.itch_auth.fetch_itch_profile",
            new_callable=AsyncMock,
            return_value=profile,
        ),
        patch(
            "app.api.routes.itch_auth.fetch_itch_games",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "app.api.routes.itch_auth.listing_status_for_games",
            new_callable=AsyncMock,
            return_value={},
        ),
        patch(
            "app.api.routes.itch_auth.public_viewability_for_games",
            new_callable=AsyncMock,
            return_value={},
        ),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/auth/itch/callback",
            json={"access_token": "itch-token", "state": state},
        )

    assert response.status_code == 200
    assert response.json()["user"]["is_owner"] is True

    from app import crud

    user = crud.get_user_by_itch_user_id(session=db, itch_user_id=7777)
    assert user is not None
    assert user.is_owner is True


def test_itch_callback_claims_anonymous_kudos(
    client: TestClient, db: Session
) -> None:
    import uuid

    from app.models import GameAnonymousKudos, GameKudos
    from app.services.itch_api import ItchProfileUser
    from tests.utils.game import create_random_game

    game = create_random_game(db, approved=True)
    visitor_id = str(uuid.uuid4())
    crud.add_anonymous_game_kudos(session=db, game=game, visitor_id=visitor_id)
    db.refresh(game)
    assert game.kudos_count == 1

    profile = ItchProfileUser(
        id=8888,
        username="kudosfan",
        display_name="Kudos Fan",
        url="https://kudosfan.itch.io",
    )
    state = create_oauth_state()

    with (
        patch.object(settings, "ITCH_OAUTH_CLIENT_ID", "test-client-id"),
        patch(
            "app.api.routes.itch_auth.fetch_itch_profile",
            new_callable=AsyncMock,
            return_value=profile,
        ),
        patch(
            "app.api.routes.itch_auth.fetch_itch_games",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "app.api.routes.itch_auth.listing_status_for_games",
            new_callable=AsyncMock,
            return_value={},
        ),
        patch(
            "app.api.routes.itch_auth.public_viewability_for_games",
            new_callable=AsyncMock,
            return_value={},
        ),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/auth/itch/callback",
            json={"access_token": "itch-token", "state": state},
            headers={"X-Kudos-Visitor-Id": visitor_id},
        )

    assert response.status_code == 200

    user = crud.get_user_by_itch_user_id(session=db, itch_user_id=8888)
    assert user is not None
    assert user.kudos_visitor_id == visitor_id
    assert db.get(GameAnonymousKudos, (visitor_id, game.id)) is None
    assert db.get(GameKudos, (user.id, game.id)) is not None

    db.refresh(game)
    assert game.kudos_count == 1
