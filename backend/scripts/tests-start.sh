#!/usr/bin/env bash
set -e
set -x

export POSTGRES_DB=app_test
export IO3_TEST_DB_PREPARED=1

PYTHONPATH=. python app/ensure_test_database.py
PYTHONPATH=. alembic upgrade head

python app/tests_pre_start.py

bash scripts/test.sh "$@"
