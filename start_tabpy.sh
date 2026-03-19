#!/usr/bin/env bash

set -euo pipefail

PORT=9004
STATUS_URL="http://localhost:${PORT}/status"

if curl -fsS "$STATUS_URL" >/dev/null 2>&1; then
  echo "TabPy is already running on port ${PORT}."
  echo "Status:"
  curl -fsS "$STATUS_URL"
  exit 0
fi

if lsof -iTCP:"$PORT" -sTCP:LISTEN -n -P >/dev/null 2>&1; then
  echo "Port ${PORT} is already in use by another process."
  echo "Stop the existing process or free the port, then try again."
  exit 1
fi

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

exec tabpy
