#!/usr/bin/env bash

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export POSTGRES_DB=app_test
export IO3_TEST_DB_PREPARED=1

if docker compose -f "$ROOT/compose.yml" ps db --status running 2>/dev/null | grep -q running; then
  docker compose -f "$ROOT/compose.yml" exec -T db psql -U "${POSTGRES_USER:-postgres}" -tc \
    "SELECT 1 FROM pg_database WHERE datname = 'app_test'" | grep -q 1 \
    || docker compose -f "$ROOT/compose.yml" exec -T db psql -U "${POSTGRES_USER:-postgres}" \
      -c "CREATE DATABASE app_test;"
fi

cd "$BACKEND"
PYTHONPATH=. python3 app/ensure_test_database.py
PYTHONPATH=. alembic upgrade head

exec "$@"
