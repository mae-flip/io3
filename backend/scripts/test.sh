#!/usr/bin/env bash

set -e
set -x

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "${IO3_TEST_DB_PREPARED:-}" != "1" ]; then
  exec bash "$SCRIPT_DIR/test-local.sh" bash "$SCRIPT_DIR/test.sh" "$@"
fi

coverage run -m pytest tests/ "$@"
coverage report
coverage html --title "${@-coverage}"
