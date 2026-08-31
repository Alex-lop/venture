#!/usr/bin/env bash
# A 60-second demo of guardrail-checkup. Requires guardrail-checkup on PATH and git.
#
# It builds a throwaway git repository from demo/fixture (a service with a db/
# directory, a migration, an .mcp.json, no hooks, and a CLAUDE.md that forbids
# nothing), gives it a history with three repairs, and runs the checkup over it.
# The fixture is copied, never git-initialised in place; the checkout under
# demo/fixture is not touched, and neither is the repository under inspection.
#
# Pass a directory to keep the report and the drafts; otherwise they are removed.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
keep="${1:-}"
work="$(mktemp -d)"
trap 'rm -rf "${work}"' EXIT

cp -R "${here}/fixture" "${work}/shipfast"

# A fixed identity, fixed dates and no user configuration, so the commit SHAs in
# the report below are the same on every machine.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME="Demo Author" GIT_AUTHOR_EMAIL="demo@example.invalid"
export GIT_COMMITTER_NAME="Demo Author" GIT_COMMITTER_EMAIL="demo@example.invalid"
export SOURCE_DATE_EPOCH=1788134400   # 2026-08-31T00:00:00Z, so the report's date is fixed too

commit() {
  GIT_AUTHOR_DATE="$2" GIT_COMMITTER_DATE="$2" git -C "${work}/shipfast" commit -q -m "$1"
}
git -C "${work}/shipfast" init -q -b main
git -C "${work}/shipfast" add -A
commit "orders service: handlers, queries, first migration" "2026-08-03T09:00:00+00:00"
printf '\n\ndef refund(conn, order_id):\n    conn.execute("UPDATE orders SET state = %%s WHERE id = %%s", ("refunded", order_id))\n' \
  >> "${work}/shipfast/db/queries.py"
git -C "${work}/shipfast" add -A
commit "fix: refund left the order marked paid" "2026-08-11T14:20:00+00:00"
printf 'ALTER TABLE orders ADD COLUMN refunded_cents BIGINT NOT NULL DEFAULT 0;\n' \
  >> "${work}/shipfast/db/migrations/0001_orders.sql"
git -C "${work}/shipfast" add -A
commit "hotfix: migration ran twice in staging" "2026-08-19T08:05:00+00:00"
printf '\n\n# charge before mark_paid; see the revert\n' >> "${work}/shipfast/app/checkout.py"
git -C "${work}/shipfast" add -A
commit "revert: back out the checkout retry change" "2026-08-25T17:40:00+00:00"

cd "${work}"

echo "== 1. The repository under inspection =="
echo "\$ git -C shipfast log --oneline"
git -C shipfast log --oneline
echo

echo "== 2. One command, one report, nothing written into the repository =="
echo "\$ guardrail-checkup run shipfast --out REPORT.md --emit-dir drafts"
guardrail-checkup run shipfast --out REPORT.md --emit-dir drafts
echo "\$ git -C shipfast status --porcelain | wc -l"
git -C shipfast status --porcelain | wc -l | tr -d ' '
echo

echo "== 3. What it drafted, outside the repository =="
echo "\$ find drafts -type f | sort"
find drafts -type f | sort
echo

echo "== 4. The emitted hook, run against three tool calls =="
echo "\$ echo '{\"cwd\":\"/repo\",\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"/repo/db/queries.py\"}}' | drafts/hooks/protect-db.py"
set +e
echo '{"cwd":"/repo","tool_name":"Write","tool_input":{"file_path":"/repo/db/queries.py"}}' | drafts/hooks/protect-db.py
echo "exit status: $?"
echo '{"cwd":"/repo","tool_name":"Write","tool_input":{"file_path":"/repo/app/checkout.py"}}' | drafts/hooks/protect-db.py
echo "app/checkout.py -> exit status: $?"
echo '{"cwd":"/repo","tool_name":"Bash","tool_input":{"command":"ls"}}' | drafts/hooks/protect-db.py
echo "Bash -> exit status: $?"
set -e
echo

echo "== 5. The report =="
cat REPORT.md

if [ -n "${keep}" ]; then
  mkdir -p "${keep}"
  cp REPORT.md "${keep}/OUTPUT.md"
  cp -R drafts "${keep}/drafts"
fi
