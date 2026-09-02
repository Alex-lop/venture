# STATE — resume point

session: 4
status: CLOSED
started: 2026-09-02 00:11 EDT
closed: 2026-09-02 00:52 EDT
brief: `codex-night-run-prompt.md` over `CLAUDE.md` v2
principal_file: `private/PRINCIPAL.md`
standing_approvals: repos=yes, pypi=yes, oss-prs=yes, track-h=yes
last_verified_remote_head_before_close: `eaddd5437d9497f40e4aa3cfdbfb5c9bc7f20944`
remote_at_last_check: `origin/main...HEAD = 0/0`
next_file: `PRINCIPAL_TODO.md` (16 minutes)

## Night-run claims

Every claim is complete and released; no agent remains live.

| rung | task | owner | status | artifact |
|---|---|---|---|---|
| N1 | hostile clean-room and doc-truth verification of both source releases | — | COMPLETE / RELEASED | `ventures/night-verification/packages.md`; public fixes `agent-plan-lint@031295e`, `egresswall@8f99308` |
| N4 | property and mutation hardening of both shipped package working copies | — | COMPLETE / RELEASED | tests plus `ventures/night-verification/hardening.md` |
| N5 | supported-Python compatibility audit | — | COMPLETE / RELEASED | `ventures/night-verification/compatibility.md` |
| N6 | guardrail-checkup dogfood across every public Alex-lop repository | — | COMPLETE / RELEASED | `ventures/guardrail-checkup/docs/dogfood/` |

N2 mechanically rechecked at 100/100 exact receipts. N3 mechanically rechecked at 3,633
screened repos, 1,614 PRs, 502 no-test-path rows and 110 qualifying repos. N7 was skipped because
the higher verification rungs consumed the run.

## Night close ground truth

- `agent-plan-lint` public main is `031295e`; its 488-test collection, full 437-pass/51-skip suite,
  build and fresh installs pass. GitHub Actions run 33592316007 is green. The immutable `v0.1.0`
  code remains publishable after ASK-015, though main contains later release-truth tests/docs.
- `egresswall` public main is `8f99308`; 675 tests, Ruff/format, builds and fresh installs pass on
  supported Pythons. GitHub Actions run 33592352952 is green. **Never publish immutable `v0.1.0`:**
  hostile verification proved aggregate-length and exception-safety failures. Release fixed main
  under a bumped version and new verified tag after ASK-015.
- Compatibility totals: agent-plan-lint 1,362 passes plus 102 expected skips across 3.11–3.13;
  egresswall 2,025 passes. Plan wheels were byte-identical across interpreters.
- Mutation runs: agent-plan-lint killed 384/462 mutants, with 78 survivors categorized;
  egresswall killed 62/65 selected mutants, with two equivalent survivors and one meaningful
  timeout documented. No dependency was added.
- Guardrail dogfood produced deterministic six-section reports for all 20 public repositories.
  One scanner defect was fixed at the shared lockfile detector (`requirements.lock` now counts),
  and guardrail-checkup is green at 485 tests plus Ruff/format/build.
- The dogfood run removed one tracked credential from `Final_test` current main at `3c207b0` and
  ignored its path without exposing the value. It remains in public history; rotation is ASK-016.
  No history was rewritten.
- Exactly one public defect justified a ticket: Alex_Lopez_Website issue #3, a reproducible failing
  contact-obfuscation invariant. The agent-authored issue does not count as stranger adoption.
- Two source tags exist; GitHub Release API objects: 0; PyPI distributions: 0. No tag moved.
- Eight ASK-012 PRs remain for Alex to merge without deleting branches. Cash spent: $0.

## Resume order

1. Alex revokes/rotates the removed `Final_test` credential (ASK-016). Default to no destructive
   history rewrite unless Alex explicitly approves one after rotation.
2. Alex repairs PyPI authentication (ASK-015). Do not retry the invalid credential.
3. After auth works, publish and clean-install verify agent-plan-lint's exact `v0.1.0` artifact.
   For egresswall, bump from 0.1.0, tag fixed main (normally `v0.1.1`), repeat release verification,
   then publish. Never upload the old egresswall tag.
4. Re-lock guardrail-checkup against published siblings, remove only its local dependency
   overrides, repeat release verification, then create/tag/publish it.
5. Alex merges ASK-012 without deleting branches, sends ASK-002's notice and decides ASK-003.
6. On 2026-09-06 apply ASK-010/011 defaults if unanswered: run payroll and business in parallel;
   do not rewrite public history.

Resume mechanically: read `CLAUDE.md`, `private/PRINCIPAL.md`, this file, then run
`git fetch origin && git status --short && git log origin/main --oneline -20`. Never force-push,
delete a public branch, or publish package bytes that did not pass clean release verification.
