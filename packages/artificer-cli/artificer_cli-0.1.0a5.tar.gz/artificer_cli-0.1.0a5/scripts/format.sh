#!/usr/bin/env bash
# Run ruff formatter
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Running ruff format..."
uv run ruff format artificer tests
