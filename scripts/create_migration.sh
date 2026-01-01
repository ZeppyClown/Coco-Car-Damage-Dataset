#!/bin/bash
# Script to create a new Alembic migration

cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create migration
alembic revision --autogenerate -m "${1:-auto migration}"

echo "Migration created successfully!"
