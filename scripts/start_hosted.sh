#!/bin/sh
# Container start: bring the database up to date, build the manual assistant's library in the background when it is
# switched on and has a key (the host keeps no disk, so this runs after every restart, about two minutes), then serve.
set -eu
alembic upgrade head
INDEX="car mechanic assistant/$CHROMA_PERSIST_DIRECTORY"
if [ "${AI_TOOLS_ENABLED:-false}" = "true" ] && [ -n "${GEMINI_API_KEY:-}" ] && [ ! -e "$INDEX" ]; then
  # A separate process with a 10-minute limit, so a slow or failing build never holds up the workshop or /health.
  (cd "car mechanic assistant" && echo "Manual assistant library build started" \
    && timeout 600 python -m src.vector_store --output "$CHROMA_PERSIST_DIRECTORY" \
    || echo "Manual assistant library build failed; the assistant page will keep saying it is preparing") &
fi
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers --forwarded-allow-ips='*'
