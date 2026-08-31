#!/usr/bin/env bash
# A 60-second demo of egresswall. Requires only egresswall on PATH.
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-python3}"

run() {
  echo "\$ $*"
  set +e
  "$@"
  local status=$?
  set -e
  echo "exit status: $status"
  echo
}

echo "== 1. A governed aggregate leaves the boundary =="
run egresswall check demo/clean.json --policy demo/policy.json

echo "== 2. The same tool, one bad row: blocked whole, never redacted =="
run egresswall check demo/leaky.json --policy demo/policy.json

echo "== 3. In front of a live MCP server, the client gets an error, not the value =="
echo "\$ egresswall proxy --policy demo/policy.json -- python3 demo/fake_mcp_server.py"
{
  echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"cohort_summary"}}'
  echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"lookup_customer"}}'
} | egresswall proxy --policy demo/policy.json -- "$PYTHON" demo/fake_mcp_server.py
echo
echo "== 4. As a Claude Code PostToolUse hook =="
echo "\$ echo '<hook event>' | egresswall hook --policy demo/policy.json"
set +e
echo '{"hook_event_name":"PostToolUse","tool_name":"mcp__support__lookup_customer","tool_input":{"ticket":"SUP-4417"},"tool_response":{"contact_email":"member-88231@northgate-clinic.test"}}' \
  | egresswall hook --policy demo/policy.json
echo "exit status: $?"
set -e
