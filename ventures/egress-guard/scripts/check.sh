#!/usr/bin/env bash
# The checks CI runs before it installs the built wheel, in the order CI runs them.
# tests/test_readme_truth.py asserts this list equals ci.yml's, so a step CI grows
# and this script lacks fails the suite rather than shipping a false claim.
set -euo pipefail
cd "$(dirname "$0")/.."

uv lock --check
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv build
