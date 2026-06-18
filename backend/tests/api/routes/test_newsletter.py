from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models import NewsletterSubscriber


def test_subscribe_to_newsletter(client: TestClient, db: Session) -> None:
    email = "weekly@example.com"
    response = client.post(
        f"{settings.API_V1_STR}/newsletter/subscribe",
        json={"email": email},
    )
    assert response.status_code == 201
    assert "on the list" in response.json()["message"].lower()

    subscriber = db.exec(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
    ).first()
    assert subscriber is not None


def test_subscribe_to_newsletter_is_idempotent(
    client: TestClient, db: Session
) -> None:
    email = "weekly-idempotent@example.com"
    first = client.post(
        f"{settings.API_V1_STR}/newsletter/subscribe",
        json={"email": email},
    )
    second = client.post(
        f"{settings.API_V1_STR}/newsletter/subscribe",
        json={"email": email},
    )
    assert first.status_code == 201
    assert second.status_code == 201

    subscribers = db.exec(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
    ).all()
    assert len(subscribers) == 1
