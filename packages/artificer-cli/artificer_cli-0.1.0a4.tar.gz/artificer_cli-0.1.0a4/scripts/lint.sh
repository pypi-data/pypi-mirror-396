#!/usr/bin/env bash
# Run ruff linter
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Running ruff check..."
uv run ruff check artificer tests "$@"
