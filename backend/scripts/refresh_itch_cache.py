"""Refresh itch metadata cache entries."""

import argparse
import logging

from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine
from app.services.itch_cache import refresh_all_stale

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Refresh all approved games, not only stale entries",
    )
    args = parser.parse_args()
    force = args.force or settings.ITCH_REFRESH_ON_DEPLOY

    with Session(engine) as session:
        count = refresh_all_stale(session, force=force)

    if count:
        logger.info("Refreshed %s game(s)", count)
    else:
        logger.info("No itch cache entries needed refresh")


if __name__ == "__main__":
    main()
