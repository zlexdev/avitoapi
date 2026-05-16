#!/usr/bin/env bash
# Run the echo bot. Idempotent — safe to call from systemd ExecStart.
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  set -a; source .env; set +a
fi

exec python -m echo_bot "$@"
