#!/usr/bin/env bash
# Dump Postgres to backups/<db>-<timestamp>.sql
# Run from repo root. Requires the db service to be up.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

COMPOSE_FILE="${COMPOSE_FILE:-compose.yml}"
STACK_NAME="${STACK_NAME:-}"
BACKUP_DIR="${BACKUP_DIR:-backups}"

mkdir -p "$BACKUP_DIR"

COMPOSE_ARGS=(-f "$COMPOSE_FILE")
if [ -n "$STACK_NAME" ]; then
  COMPOSE_ARGS+=(--project-name "$STACK_NAME")
fi

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

# POSTGRES_DB is set inside the db container via compose / .env
DB_NAME="$(docker compose "${COMPOSE_ARGS[@]}" exec -T db printenv POSTGRES_DB)"
OUT="${BACKUP_DIR}/${DB_NAME}-${TIMESTAMP}.sql"

docker compose "${COMPOSE_ARGS[@]}" exec -T db \
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-acl' \
  > "$OUT"

echo "Wrote ${OUT}"
