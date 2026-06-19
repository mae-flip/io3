#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python app/initial_data.py

# Re-fetch itch metadata for approved games so new cache fields populate on deploy.
if [ "${ITCH_REFRESH_ON_DEPLOY:-false}" = "true" ]; then
  python scripts/refresh_itch_cache.py --force
fi
