#!/usr/bin/env bash
# The same steps CI runs, locally. Needs uv; everything else it fetches itself.
set -euo pipefail
cd "$(dirname "$0")/.."

uv lock --check
uv run ruff check .
uv run ruff format --check .
# One environment per interpreter, and `UV_PYTHON` so the `uv` calls the tests
# make themselves agree with the leg they run in. Sharing `.venv` between legs
# lets a nested `uv` rebuild it from `.python-version` mid-run, which fails as a
# missing module or as a wheel installed on the wrong interpreter.
for version in 3.11 3.12 3.13; do
    echo "== pytest on ${version} =="
    UV_PYTHON="${version}" UV_PROJECT_ENVIRONMENT=".venvs/${version}" \
        uv run --python "${version}" pytest -q
done

# A stale wheel from an earlier version would make `dist/*.whl` two files and
# the install below fail on conflicting URLs, so the directory is rebuilt.
rm -rf dist
uv build
fresh="$(mktemp -d)"
trap 'rm -rf "${fresh}"' EXIT
for version in 3.11 3.12 3.13; do
    echo "== wheel on ${version} =="
    # `uv venv` with no `--python` reads .python-version, which would install
    # the wheel on 3.11 three times.
    uv venv --python "${version}" "${fresh}/venv"
    uv pip install --python "${fresh}/venv/bin/python" dist/*.whl
    "${fresh}/venv/bin/agent-plan-lint" --help > /dev/null
    PLAN_LINT="${fresh}/venv/bin/agent-plan-lint" demo/demo.sh | diff - demo/OUTPUT.txt
    rm -rf "${fresh}/venv"
done
echo "all checks passed"
