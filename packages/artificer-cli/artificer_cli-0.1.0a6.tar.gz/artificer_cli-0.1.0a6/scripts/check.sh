#!/usr/bin/env bash
# Run all checks: format, lint, test, typecheck
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Format ==="
./scripts/format.sh

echo ""
echo "=== Lint ==="
./scripts/lint.sh

echo ""
echo "=== Test ==="
./scripts/test.sh

echo ""
echo "=== Typecheck ==="
./scripts/typecheck.sh

echo ""
echo "All checks passed!"
