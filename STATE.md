# STATE — resume point

session: 4
status: RUNNING
started: 2026-09-02 00:11 EDT
brief: `codex-night-run-prompt.md` over `CLAUDE.md` v2
principal_file: `private/PRINCIPAL.md`
standing_approvals: repos=yes, pypi=yes, oss-prs=yes, track-h=yes
last_verified_remote_head: `001a0ffc1092e171fe10e66778b6b2d2298bc822`
remote_at_last_check: `origin/main...HEAD = 0/0`
next_file: `PRINCIPAL_TODO.md` (13 minutes)

## Night-run claims

| rung | task | owner | status | artifact |
|---|---|---|---|---|
| N1 | hostile clean-room and doc-truth verification of both source releases | codex/orchestrator | CLAIMED | `ventures/night-verification/packages.md` |
| N4 | property and mutation hardening of both shipped package working copies | codex/test-hardener | CLAIMED | tests plus `ventures/night-verification/hardening.md` |
| N5 | supported-Python compatibility audit and fixes | codex/compatibility | CLAIMED | `ventures/night-verification/compatibility.md` |
| N6 | guardrail-checkup dogfood across every public Alex-lop repository | codex/autopsy-dogfood | CLAIMED | `ventures/guardrail-checkup/docs/dogfood/` |

N2 is complete at 100/100. N3 is already above its target with 3,633 screened repos;
both will be mechanically rechecked during the close rather than reclaimed.

## Day-run ladder

| rung | status | evidence |
|---|---|---|
| L0 hygiene | DONE | redaction commit `f4e68d4` was already on `origin/main`; pre-push secret, denylist, identity and path checks pass on every session-3 push |
| L1 agent-plan-lint | SOURCE COMPLETE / PYPI BLOCKED | `Alex-lop/agent-plan-lint`, tag `v0.1.0`, CI green, docs live; PyPI endpoints 404. The Keychain credential reached PyPI but `uv publish` returned HTTP 403 invalid/expired and accepted no artifact (ASK-015) |
| L2 buildability pilot | DONE | v3 search: 110 qualifying repos; fixed manifest/results: 100/100 exact. install 79, collect 56, run verdict 50, strict buildable **43/100**, fully green 19, 267,558 collected. The 30% falsifier did not fire. Commit `b070fad` tracks 100 sanitized per-repo receipts; raw third-party logs stay local |
| L3 egresswall | SOURCE COMPLETE / PYPI BLOCKED | `Alex-lop/egresswall`, tag `v0.1.0`, CI green, docs live, `mcp-name:` present; same ASK-015 PyPI blocker |
| L4 guardrail-checkup | DONE, NOT RELEASED | round-9 blockers fixed; 483 passed / 2 skipped, Ruff/build/clean installs passed. Real deterministic Graphene report: 16 findings, 3 invariant candidates; Graphene HEAD/status unchanged. Commit `3952fdc`. Release stays held because its sibling dependencies are absent from PyPI and local source overrides remain |
| L5 close loop | DONE | concise operative DECISION v4 + evidence appendices; source-ready launch drafts; live signal gates/forecasts; principal handoff; commits `436c53a`, `1d0de98`, `033c1de` |
| L6 extra research | SKIPPED | higher rungs consumed the window |

## Ground truth at close

- Two tagged source releases exist; GitHub Release API objects: 0; PyPI distributions: 0.
- `https://alex-lop.github.io/guardposts/` and `/study.html` are live.
- The published differential study remains frozen and reproducible at 107 PR rows over
  the original v2 cohort's 25 strict-buildable repos. The expanded pilot is reported
  separately; no post-hoc rows were added to the published study.
- Eight ASK-012 PRs are open, mergeable/clean and green; branches must not be deleted.
- ASK-013/014 defaults applied 2026-09-02: Apache-2.0 and the recorded names remain.
- Cash spent: $0. Codex/client usage was not reported.

## Resume order

1. Alex repairs PyPI authentication (ASK-015): replace the invalid Keychain token or
   configure trusted publishing. Do not retry the current credential.
2. After auth works, publish the exact `v0.1.0` tag artifacts for `agent-plan-lint` and
   `egresswall`, verify JSON/Simple endpoints plus a clean install, then update the
   guardposts `RELEASED` flags/install lines and replace `{PYPI_URL}` in the launch kit.
   Note: agent-plan-lint `main` is one comment-only commit past its tag; do not publish
   untagged `main` bytes as the already-tagged version.
3. Re-lock `guardrail-checkup` against the published siblings, remove only its local
   dependency overrides, repeat the release verification, then create/tag/publish it.
4. Alex merges the eight ASK-012 PRs without deleting branches and sends ASK-002's notice.
5. On 2026-09-06, apply ASK-010/011 defaults if no answer: run payroll and business in
   parallel; do not rewrite public history.

Resume mechanically: read `CLAUDE.md`, `private/PRINCIPAL.md`, this file, then run
`git fetch origin && git status --short && git log origin/main --oneline -20`. Never
force-push, delete a public branch, or publish a package whose tag bytes were not verified.
