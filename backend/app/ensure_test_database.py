import logging
import re

import psycopg
from psycopg import sql

from app.core.config import settings

logger = logging.getLogger(__name__)

_VALID_TEST_DB = re.compile(r"^[a-z][a-z0-9_]*_test$")


def ensure_test_database() -> None:
    db_name = settings.POSTGRES_DB
    if not _VALID_TEST_DB.match(db_name):
        return

    conninfo = (
        f"host={settings.POSTGRES_SERVER} "
        f"port={settings.POSTGRES_PORT} "
        f"user={settings.POSTGRES_USER} "
        f"password={settings.POSTGRES_PASSWORD} "
        f"dbname=postgres"
    )
    with psycopg.connect(conninfo, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (db_name,),
            )
            if cur.fetchone():
                return
            logger.info("Creating test database %s", db_name)
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    ensure_test_database()


if __name__ == "__main__":
    main()
