#!/usr/bin/env bash
# Base-snapshot buildability pilot. Resumable: repos already in results.csv are skipped.
#
#   ./run.sh                     # the fixed 100-repo pilot manifest, 3 at a time
#   JOBS=2 ./run.sh              # fewer containers at once
#   CSV=../corpus/candidates.csv ./run.sh
#
# Everything untrusted runs in docker. Requires: docker running, python3 on the host.
set -euo pipefail
cd "$(dirname "$0")"

CSV="${CSV:-../corpus/candidates-pilot-100.csv}"
JOBS="${JOBS:-3}"

command -v docker >/dev/null || { echo "docker not found"; exit 1; }
docker info >/dev/null 2>&1 || { echo "docker daemon not running"; exit 1; }
python3 pilot.py --selfcheck

docker volume create pilot-uvcache >/dev/null
docker volume create pilot-pipcache >/dev/null

exec python3 pilot.py --csv "$CSV" --jobs "$JOBS" "$@"
