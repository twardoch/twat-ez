#!/usr/bin/env bash
# install.sh — Install twat-ez locally
# Easy and convenient utilities for the twat ecosystem
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Installing twat-ez..."
uv pip install -e . 2>/dev/null || pip install -e .
echo "Done."
