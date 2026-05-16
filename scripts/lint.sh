#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if command -v uv >/dev/null 2>&1; then
    uv run ruff check avitoapi/ tests/
    uv run mypy --strict avitoapi/
else
    python -m ruff check avitoapi/ tests/
    python -m mypy --strict avitoapi/
fi
