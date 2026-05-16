#!/usr/bin/env bash
# Probe the running bot's /healthz endpoint. Exit 0 on 200, non-zero otherwise.
set -euo pipefail

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8080}"
URL="http://${HOST}:${PORT}/healthz"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl not installed" >&2
  exit 127
fi

status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$URL" || true)
if [[ "$status" == "200" ]]; then
  echo "healthz ok: $URL"
  exit 0
fi
echo "healthz failed: $URL (status=$status)" >&2
exit 1
