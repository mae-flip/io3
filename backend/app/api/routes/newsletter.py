from typing import Any

from fastapi import APIRouter

from app import crud
from app.api.deps import SessionDep
from app.models import Message, NewsletterSubscribe

router = APIRouter(prefix="/newsletter", tags=["newsletter"])


@router.post("/subscribe", response_model=Message, status_code=201)
def subscribe_to_newsletter(
    *, session: SessionDep, body: NewsletterSubscribe
) -> Any:
    crud.subscribe_newsletter(session=session, email=body.email)
    return Message(
        message="You're on the list! We'll email you when new weekly features drop."
    )
