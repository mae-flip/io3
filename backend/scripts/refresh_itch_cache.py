"""Refresh stale itch metadata cache entries."""

from sqlmodel import Session

from app.core.db import engine
from app.services.itch_cache import refresh_all_stale


def main() -> None:
    with Session(engine) as session:
        count = refresh_all_stale(session)
    print(f"Refreshed {count} game(s)")


if __name__ == "__main__":
    main()
