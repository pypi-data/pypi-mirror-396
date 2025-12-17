#!/usr/bin/env bash
# Run mypy type checking on the codebase
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Running mypy type checks..."
uv run mypy artificer tests
