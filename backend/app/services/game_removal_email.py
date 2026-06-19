import logging

from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import Game, User
from app.utils import generate_game_removed_email, send_email

logger = logging.getLogger(__name__)


def _game_title(game: Game) -> str:
    if game.itch_cache and game.itch_cache.title:
        return game.itch_cache.title
    return "Untitled"


def notify_submitter_of_game_removal(*, session: Session, game: Game) -> None:
    if not settings.emails_enabled:
        logger.info(
            "Skipping game removal email for game %s: SMTP is not configured",
            game.id,
        )
        return

    submitter = session.get(User, game.submitter_id)
    if not submitter or not crud.user_has_contact_email(submitter):
        logger.info(
            "Skipping game removal email for game %s: submitter has no contact email",
            game.id,
        )
        return

    removal_reason = (game.removal_reason or "").strip()
    if not removal_reason:
        logger.info(
            "Skipping game removal email for game %s: no removal reason recorded",
            game.id,
        )
        return

    session.refresh(game, attribute_names=["itch_cache"])
    game_title = _game_title(game)
    email_data = generate_game_removed_email(
        email_to=submitter.email,
        game_title=game_title,
        removal_reason=removal_reason,
    )

    try:
        send_email(
            email_to=submitter.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    except Exception:
        logger.exception(
            "Failed to send game removal email for game %s to %s",
            game.id,
            submitter.email,
        )
