import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings

STATE_ALGORITHM = "HS256"
STATE_EXPIRE_MINUTES = 10


def create_oauth_state() -> str:
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(minutes=STATE_EXPIRE_MINUTES),
        "nonce": secrets.token_urlsafe(16),
        "purpose": "itch_oauth",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=STATE_ALGORITHM)


def verify_oauth_state(state: str) -> bool:
    try:
        payload = jwt.decode(state, settings.SECRET_KEY, algorithms=[STATE_ALGORITHM])
    except jwt.InvalidTokenError:
        return False
    return payload.get("purpose") == "itch_oauth"
