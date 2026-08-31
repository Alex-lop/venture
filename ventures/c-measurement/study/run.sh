#!/usr/bin/env bash
# Track M differential verifier. Resumable: PRs already in results-prs.csv are skipped.
#
#   ./run.sh                       # every sample PR of every buildable repo, 3 at a time
#   ./run.sh --smoke 2             # only the two buildable repos with the smallest suites
#   ./run.sh --repo O/R --limit 1  # one PR
#   JOBS=2 ./run.sh
#
# Everything untrusted runs in docker (image, install and caps come from ../pilot).
# Requires: docker running, gh authenticated read-only, python3 on the host.
set -euo pipefail
cd "$(dirname "$0")"

JOBS="${JOBS:-3}"

command -v docker >/dev/null || { echo "docker not found"; exit 1; }
docker info >/dev/null 2>&1 || { echo "docker daemon not running"; exit 1; }
command -v gh >/dev/null || { echo "gh not found"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "gh not authenticated"; exit 1; }
python3 runner.py --selfcheck

docker volume create pilot-uvcache >/dev/null
docker volume create pilot-pipcache >/dev/null

exec python3 runner.py --jobs "$JOBS" "$@"
