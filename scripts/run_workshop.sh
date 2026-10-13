#!/bin/sh
# Start the workshop app on this computer: bring the database up to date, then serve until Ctrl-C.
# Usage: scripts/run_workshop.sh path/to/server.env [port]
set -eu
ENV_FILE="${1:?Give the settings file, for example: scripts/run_workshop.sh \"car mechanic assistant/runtime/workshop-live/server.env\"}"
PORT="${2:-18041}"
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-python}"
# The settings file is plain KEY=value lines; values may contain spaces, so read it line by line.
while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in ''|\#*) continue ;; esac
  export "$line"
done < "$ENV_FILE"
"$PYTHON" -m alembic upgrade head
exec "$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT"
