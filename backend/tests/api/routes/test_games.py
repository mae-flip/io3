from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import GameStatus
from app.services.itch import ItchMetadata, ItchTag
from app.services.itch_api import ItchGameSummary
from tests.utils.game import create_random_game, set_game_cache


def test_read_games_public(client: TestClient, db: Session) -> None:
    create_random_game(db, approved=True)
    response = client.get(f"{settings.API_V1_STR}/games/")
    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 1
    assert len(content["data"]) >= 1


def test_read_game_by_slug(
    client: TestClient, db: Session
) -> None:
    from app.models import GameItchCache

    game = create_random_game(db, approved=True)
    cache_row = db.get(GameItchCache, game.id)
    response = client.get(f"{settings.API_V1_STR}/games/{game.slug}")
    assert response.status_code == 200
    content = response.json()
    assert content["slug"] == game.slug
    assert content["title"] == cache_row.title


def test_read_pending_game_hidden_from_public(
    client: TestClient, db: Session
) -> None:
    game = create_random_game(db, approved=False)
    response = client.get(f"{settings.API_V1_STR}/games/{game.slug}")
    assert response.status_code == 404


def test_create_game(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    metadata = ItchMetadata(
        normalized_url="https://creator.itch.io/new-queer-game",
        title="New Queer Game",
        summary="Short summary",
    )
    with patch(
        "app.crud.fetch_itch_metadata_sync",
        return_value=metadata,
    ):
        response = client.post(
            f"{settings.API_V1_STR}/games/",
            headers=normal_user_token_headers,
            json={"url": "https://creator.itch.io/new-queer-game"},
        )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == "New Queer Game"
    assert content["status"] == "approved"


def test_create_game_duplicate_url(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    game = create_random_game(db)
    response = client.post(
        f"{settings.API_V1_STR}/games/",
        headers=normal_user_token_headers,
        json={"url": game.itch_url},
    )
    assert response.status_code == 400


def test_read_tags(client: TestClient, db: Session) -> None:
    game = create_random_game(db, approved=True)
    set_game_cache(
        db,
        game,
        tags=[
            {
                "slug": "nsfw",
                "name": "NSFW",
                "itch_url": "https://itch.io/games/tag-nsfw",
                "is_genre": False,
            }
        ],
    )
    response = client.get(f"{settings.API_V1_STR}/tags/")
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content["data"], list)
    assert content["count"] >= 1


def test_moderation_approve(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    game = create_random_game(db, approved=False)
    response = client.post(
        f"{settings.API_V1_STR}/moderation/games/{game.id}/approve",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["status"] == "approved"


def test_moderation_reject(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    game = create_random_game(db, approved=False)
    response = client.post(
        f"{settings.API_V1_STR}/moderation/games/{game.id}/reject",
        headers=superuser_token_headers,
        json={"rejection_reason": "Not eligible for indexing"},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["status"] == "rejected"


def test_read_games_author_name(
    client: TestClient, db: Session
) -> None:
    game = create_random_game(db, approved=True)
    set_game_cache(
        db,
        game,
        author_name="MaeFlip",
        author_url="https://maeflip.itch.io",
    )

    response = client.get(f"{settings.API_V1_STR}/games/")
    assert response.status_code == 200
    item = next(row for row in response.json()["data"] if row["id"] == str(game.id))
    assert item["author_name"] == "MaeFlip"
    assert item["author_url"] == "https://maeflip.itch.io"


def test_read_games_sort_title(
    client: TestClient, db: Session
) -> None:
    game_a = create_random_game(db, approved=True)
    game_b = create_random_game(db, approved=True)
    set_game_cache(db, game_a, title="Alpha Game")
    set_game_cache(db, game_b, title="Zulu Game")

    response = client.get(
        f"{settings.API_V1_STR}/games/",
        params={"sort": "title", "limit": 100},
    )
    assert response.status_code == 200
    titles = [row["title"] for row in response.json()["data"]]
    assert titles.index("Alpha Game") < titles.index("Zulu Game")


def test_read_featured_games(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    featured = create_random_game(db, approved=True)
    other = create_random_game(db, approved=True)
    crud.feature_game(session=db, game=featured)

    response = client.get(f"{settings.API_V1_STR}/games/featured")
    assert response.status_code == 200
    slugs = {row["slug"] for row in response.json()["data"]}
    assert featured.slug in slugs
    assert other.slug not in slugs


def test_add_kudos(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    game = create_random_game(db, approved=True)
    response = client.post(
        f"{settings.API_V1_STR}/games/{game.slug}/kudos",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["kudos_count"] == 1
    assert content["has_kudos"] is True

    duplicate = client.post(
        f"{settings.API_V1_STR}/games/{game.slug}/kudos",
        headers=normal_user_token_headers,
    )
    assert duplicate.status_code == 409


def test_add_anonymous_kudos(client: TestClient, db: Session) -> None:
    import uuid

    game = create_random_game(db, approved=True)
    visitor_id = str(uuid.uuid4())
    headers = {"X-Kudos-Visitor-Id": visitor_id}

    missing = client.post(f"{settings.API_V1_STR}/games/{game.slug}/kudos")
    assert missing.status_code == 400

    response = client.post(
        f"{settings.API_V1_STR}/games/{game.slug}/kudos",
        headers=headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["kudos_count"] == 1
    assert content["has_kudos"] is True

    list_response = client.get(
        f"{settings.API_V1_STR}/games/",
        headers=headers,
    )
    assert list_response.status_code == 200
    row = next(item for item in list_response.json()["data"] if item["slug"] == game.slug)
    assert row["has_kudos"] is True

    duplicate = client.post(
        f"{settings.API_V1_STR}/games/{game.slug}/kudos",
        headers=headers,
    )
    assert duplicate.status_code == 409


def test_anonymous_kudos_carries_over_on_login(
    client: TestClient, db: Session
) -> None:
    import uuid

    from app.models import GameAnonymousKudos, GameKudos
    from tests.utils.user import authentication_token_for_user, create_itch_user

    game = create_random_game(db, approved=True)
    visitor_id = str(uuid.uuid4())
    visitor_headers = {"X-Kudos-Visitor-Id": visitor_id}

    anon = client.post(
        f"{settings.API_V1_STR}/games/{game.slug}/kudos",
        headers=visitor_headers,
    )
    assert anon.status_code == 200
    assert anon.json()["kudos_count"] == 1

    user = create_itch_user(db)
    user = crud.claim_anonymous_kudos_for_user(
        session=db, user=user, visitor_id=visitor_id
    )

    assert user.kudos_visitor_id == visitor_id
    assert db.get(GameAnonymousKudos, (visitor_id, game.id)) is None
    assert db.get(GameKudos, (user.id, game.id)) is not None

    db.refresh(game)
    assert game.kudos_count == 1

    auth_headers = {
        **visitor_headers,
        **authentication_token_for_user(user=user),
    }
    duplicate = client.post(
        f"{settings.API_V1_STR}/games/{game.slug}/kudos",
        headers=auth_headers,
    )
    assert duplicate.status_code == 409

    list_response = client.get(
        f"{settings.API_V1_STR}/games/",
        headers=auth_headers,
    )
    row = next(item for item in list_response.json()["data"] if item["slug"] == game.slug)
    assert row["has_kudos"] is True


def test_logged_in_kudos_shows_after_logout(
    client: TestClient, db: Session
) -> None:
    import uuid

    from tests.utils.user import authentication_token_for_user, create_itch_user

    game = create_random_game(db, approved=True)
    visitor_id = str(uuid.uuid4())
    user = create_itch_user(db)

    auth_headers = {
        "X-Kudos-Visitor-Id": visitor_id,
        **authentication_token_for_user(user=user),
    }
    response = client.post(
        f"{settings.API_V1_STR}/games/{game.slug}/kudos",
        headers=auth_headers,
    )
    assert response.status_code == 200

    db.refresh(user)
    assert user.kudos_visitor_id == visitor_id

    logged_out = client.get(
        f"{settings.API_V1_STR}/games/",
        headers={"X-Kudos-Visitor-Id": visitor_id},
    )
    assert logged_out.status_code == 200
    row = next(item for item in logged_out.json()["data"] if item["slug"] == game.slug)
    assert row["has_kudos"] is True


def test_logged_in_kudos_blocks_anonymous_duplicate(
    client: TestClient, db: Session
) -> None:
    import uuid

    from tests.utils.user import authentication_token_for_user, create_itch_user

    game = create_random_game(db, approved=True)
    visitor_id = str(uuid.uuid4())
    user = create_itch_user(db)
    user.kudos_visitor_id = visitor_id
    db.add(user)
    db.commit()
    db.refresh(user)

    auth_headers = {
        "X-Kudos-Visitor-Id": visitor_id,
        **authentication_token_for_user(user=user),
    }
    logged_in = client.post(
        f"{settings.API_V1_STR}/games/{game.slug}/kudos",
        headers=auth_headers,
    )
    assert logged_in.status_code == 200

    anon = client.post(
        f"{settings.API_V1_STR}/games/{game.slug}/kudos",
        headers={"X-Kudos-Visitor-Id": visitor_id},
    )
    assert anon.status_code == 409


def test_read_games_search_by_tag(
    client: TestClient, db: Session
) -> None:
    game = create_random_game(db, approved=True)
    other = create_random_game(db, approved=True)
    set_game_cache(
        db,
        game,
        tags=[
            {
                "slug": "nsfw",
                "name": "NSFW",
                "itch_url": "https://itch.io/games/tag-nsfw",
                "is_genre": False,
            }
        ],
    )

    response = client.get(
        f"{settings.API_V1_STR}/games/",
        params={"search": "nsfw", "limit": 100},
    )
    assert response.status_code == 200
    ids = {row["id"] for row in response.json()["data"]}
    assert str(game.id) in ids
    assert str(other.id) not in ids


def test_read_games_search_by_genre_name(
    client: TestClient, db: Session
) -> None:
    game = create_random_game(db, approved=True)
    set_game_cache(
        db,
        game,
        tags=[
            {
                "slug": "genre-action",
                "name": "Action",
                "itch_url": "https://itch.io/games/genre-action",
                "is_genre": True,
            }
        ],
    )

    response = client.get(
        f"{settings.API_V1_STR}/games/",
        params={"search": "action", "limit": 100},
    )
    assert response.status_code == 200
    assert any(row["id"] == str(game.id) for row in response.json()["data"])


def test_moderation_feature(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    game = create_random_game(db, approved=True)
    response = client.post(
        f"{settings.API_V1_STR}/moderation/games/{game.id}/feature",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["featured_at"] is not None


def test_submit_batch_owned_game(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    metadata = ItchMetadata(
        normalized_url="https://creator.itch.io/batch-game",
        title="Batch Game",
        summary="Short summary",
    )
    itch_games = [
        ItchGameSummary(
            id=1,
            title="Batch Game",
            url="https://creator.itch.io/batch-game",
            published=True,
            classification="game",
        )
    ]
    with (
        patch(
            "app.api.routes.games.fetch_itch_games",
            new_callable=AsyncMock,
            return_value=itch_games,
        ),
        patch(
            "app.api.routes.games.is_listed_in_itch_search",
            new_callable=AsyncMock,
            return_value=False,
        ),
        patch(
            "app.crud.fetch_itch_metadata_sync",
            return_value=metadata,
        ),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/games/submit-batch",
            headers=normal_user_token_headers,
            json={
                "urls": ["https://creator.itch.io/batch-game"],
                "itch_access_token": "itch-token",
            },
        )
    assert response.status_code == 200
    content = response.json()
    assert content["submitted_count"] == 1
    assert content["results"][0]["status"] == "submitted"
    assert content["results"][0]["game"]["status"] == "approved"


def test_submit_batch_not_owned(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    with patch(
        "app.api.routes.games.fetch_itch_games",
        new_callable=AsyncMock,
        return_value=[],
    ):
        response = client.post(
            f"{settings.API_V1_STR}/games/submit-batch",
            headers=normal_user_token_headers,
            json={
                "urls": ["https://someone.itch.io/not-mine"],
                "itch_access_token": "itch-token",
            },
        )
    assert response.status_code == 200
    content = response.json()
    assert content["submitted_count"] == 0
    assert content["results"][0]["status"] == "not_owned"


def test_submit_batch_duplicate(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    game = create_random_game(db)
    itch_games = [
        ItchGameSummary(
            id=2,
            title="Existing",
            url=game.itch_url,
            published=True,
            classification="game",
        )
    ]
    with patch(
        "app.api.routes.games.fetch_itch_games",
        new_callable=AsyncMock,
        return_value=itch_games,
    ):
        response = client.post(
            f"{settings.API_V1_STR}/games/submit-batch",
            headers=normal_user_token_headers,
            json={
                "urls": [game.itch_url],
                "itch_access_token": "itch-token",
            },
        )
    assert response.status_code == 200
    content = response.json()
    assert content["submitted_count"] == 0
    assert content["results"][0]["status"] == "duplicate"


def test_submit_batch_still_listed(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    itch_games = [
        ItchGameSummary(
            id=3,
            title="Listed Game",
            url="https://creator.itch.io/listed-game",
            published=True,
            classification="game",
        )
    ]
    with (
        patch(
            "app.api.routes.games.fetch_itch_games",
            new_callable=AsyncMock,
            return_value=itch_games,
        ),
        patch(
            "app.api.routes.games.is_listed_in_itch_search",
            new_callable=AsyncMock,
            return_value=True,
        ),
    ):
        response = client.post(
            f"{settings.API_V1_STR}/games/submit-batch",
            headers=normal_user_token_headers,
            json={
                "urls": ["https://creator.itch.io/listed-game"],
                "itch_access_token": "itch-token",
            },
        )
    assert response.status_code == 200
    content = response.json()
    assert content["submitted_count"] == 0
    assert content["results"][0]["status"] == "still_listed"
