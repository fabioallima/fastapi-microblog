#!/usr/bin/bash

# Start environment with docker compose
MICROBLOG_DB=microblog_test docker compose up -d

# wait 5 seconds
sleep 5

# Ensure database is clean
docker compose exec api microblog reset-db -f
docker compose exec api alembic stamp base

# run migrations
docker compose exec api alembic upgrade head

# run tests
docker compose exec api pytest -v -l --tb=short --maxfail=1 tests/

# Stop environment
docker compose down