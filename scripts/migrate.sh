#!/bin/bash
# Script to apply database migrations

cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Apply migrations
alembic upgrade head

echo "Migrations applied successfully!"
