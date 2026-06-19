import secrets
from datetime import timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import crud
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User
from tests.utils.utils import random_lower_string


def create_itch_user(
    db: Session,
    *,
    itch_user_id: int | None = None,
    itch_username: str | None = None,
    contact_email: str | None = None,
    is_owner: bool = False,
    is_moderator: bool = False,
) -> User:
    itch_id = itch_user_id or abs(hash(random_lower_string())) % 10_000_000
    username = itch_username or f"user_{random_lower_string()[:8]}"
    user = User(
        email=contact_email or crud.itch_user_email(itch_id),
        hashed_password=get_password_hash(secrets.token_urlsafe(32)),
        itch_user_id=itch_id,
        itch_username=username,
        display_name=username,
        can_submit=True,
        is_owner=is_owner,
        is_moderator=is_moderator,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_random_user(db: Session) -> User:
    return create_itch_user(db)


def authentication_token_for_user(*, user: User) -> dict[str, str]:
    token = security.create_access_token(
        user.id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {token}"}


def owner_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    del client
    user = db.exec(
        select(User).where(User.itch_username == settings.ITCH_OWNER_USERNAME)
    ).first()
    if user is None:
        user = create_itch_user(
            db, itch_username=settings.ITCH_OWNER_USERNAME, is_owner=True
        )
    elif not user.is_owner:
        user.is_owner = True
        db.add(user)
        db.commit()
        db.refresh(user)
    return authentication_token_for_user(user=user)


def moderator_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    del client
    user = create_itch_user(db, is_moderator=True)
    return authentication_token_for_user(user=user)


def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    del client
    user = create_itch_user(
        db, contact_email=f"submit-{random_lower_string()[:8]}@example.com"
    )
    return authentication_token_for_user(user=user)
