from sqlmodel import Session, create_engine

from app.core.config import settings
from app.seed import seed_sample_games

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    seed_sample_games(session)
