#!/usr/bin/env bash
# Sixty seconds: one plan the gate rejects, one it admits.
# Set PLAN_LINT to point at a specific interpreter's console script.
set -u
cd "$(dirname "$0")"
PLAN_LINT="${PLAN_LINT:-agent-plan-lint}"

echo '$ agent-plan-lint check plan-bad.json --policy policy.json'
"$PLAN_LINT" check plan-bad.json --policy policy.json
echo "exit status: $?"
echo
echo '$ agent-plan-lint check plan-good.json --policy policy.json'
"$PLAN_LINT" check plan-good.json --policy policy.json
echo "exit status: $?"
