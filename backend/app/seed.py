from sqlmodel import Session, select

from app.core.config import settings
from app.models import Game


def seed_sample_games(session: Session) -> None:
    if settings.ENVIRONMENT != "local":
        return
    if session.exec(select(Game)).first():
        return
