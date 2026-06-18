from collections.abc import Generator
import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import Game, GameAnonymousKudos, GameItchCache, GameKudos, NewsletterSubscriber, User
from tests.utils import user as user_utils


def _is_allowed_test_database() -> bool:
    if settings.POSTGRES_DB.endswith("_test"):
        return True
    allowed = os.environ.get("IO3_ALLOW_TEST_DB")
    return allowed == settings.POSTGRES_DB


def pytest_configure(config: pytest.Config) -> None:
    if settings.ENVIRONMENT in ("production", "staging"):
        pytest.exit(
            f"Refusing to run tests with ENVIRONMENT={settings.ENVIRONMENT!r}",
            returncode=1,
        )
    if not _is_allowed_test_database():
        pytest.exit(
            f"Refusing to run tests against POSTGRES_DB={settings.POSTGRES_DB!r}. "
            "Use a database whose name ends with '_test' (run "
            "`bash scripts/test-local.sh pytest` from backend/), or set "
            "IO3_ALLOW_TEST_DB to that database name for disposable CI databases.",
            returncode=1,
        )


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        session.exec(delete(GameKudos))
        session.exec(delete(GameAnonymousKudos))
        session.exec(delete(GameItchCache))
        session.exec(delete(Game))
        session.exec(delete(NewsletterSubscriber))
        session.exec(delete(User))
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def owner_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return user_utils.owner_token_headers(client, db)


@pytest.fixture(scope="module")
def moderator_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return user_utils.moderator_token_headers(client, db)


@pytest.fixture(scope="module")
def superuser_token_headers(moderator_token_headers: dict[str, str]) -> dict[str, str]:
    return moderator_token_headers


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return user_utils.normal_user_token_headers(client, db)
