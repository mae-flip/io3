#!/usr/bin/env bash
# Restore Postgres from a pg_dump .sql file. Overwrites current DB contents.
# Usage: ./backend/scripts/restore-db.sh backups/app-20260101-120000.sql

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <path-to.sql>" >&2
  exit 1
fi

DUMP="$1"
if [ ! -f "$DUMP" ]; then
  echo "File not found: ${DUMP}" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

COMPOSE_FILE="${COMPOSE_FILE:-compose.yml}"
STACK_NAME="${STACK_NAME:-}"

COMPOSE_ARGS=(-f "$COMPOSE_FILE")
if [ -n "$STACK_NAME" ]; then
  COMPOSE_ARGS+=(--project-name "$STACK_NAME")
fi

echo "Restoring from ${DUMP} — this replaces data in the running database."
read -r -p "Type the dump filename to confirm: " CONFIRM
if [ "$CONFIRM" != "$(basename "$DUMP")" ]; then
  echo "Aborted." >&2
  exit 1
fi

docker compose "${COMPOSE_ARGS[@]}" exec -T db \
  sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1' \
  < "$DUMP"

echo "Restore finished."
