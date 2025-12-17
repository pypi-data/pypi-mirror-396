#!/usr/bin/env bash
# Run unit tests with coverage
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Running unit tests..."
uv run pytest tests/ --cov=artificer --cov-report=term-missing "$@"
