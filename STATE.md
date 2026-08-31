# STATE — resume point (machine-readable; update at every checkpoint)

session: 2
started: 2026-08-30
brief: CLAUDE.md v2 (installed this session; v1 kept at private/CLAUDE-v1.md)
principal_file: private/PRINCIPAL.md (merged; US resident; standing approvals: repos=yes pypi=yes oss-prs=yes track-h=yes)
current_wave: 2 (ship) + 3 (measure: study-runner) — waves 0, 1, DECISION v4, Track H prep complete
push_rule: the redaction commit lands on origin before any other session-2 commit (done in this checkpoint)

## Waves
| wave | status | evidence |
|---|---|---|
| 0 hygiene | DONE | redaction: 5 passes + 5 adversarial verifications, 325-entry denylist, prepush.sh (whole-word denylist, secret regexes, identity, paths) installed as .git/hooks/pre-push; private/IDENTITY.md; LICENSE PRs Graphene #12, RegLineage #9, Nemisis #1, graphene-site #1 (CI green; merge = ASK-012); Graphene deploy PR #13 (images build + procps; verified twice) |
| 1 instrument | DONE | research/{adoption,demand,venues,channels,precedents,naming,contributions,a1-weekly-screen}.md — each quote-verified (re-fetched) and fixed; adoption.md is INSTRUMENT-BIASED (88.6% GitHub) and carries a corrections section |
| 2 ship | RUNNING | ventures/plan-lint and ventures/egress-guard built to the release bar; clean-clone + claims-vs-code + red-team rounds with fix passes in flight (workflow wf_f3e2111a-317). Release names per research/naming.md: agent-plan-lint, egresswall (ASK-014 veto window to 2026-09-02). Release = orchestrator: rename → own repo under Alex-lop → PyPI (token in keychain) |
| 3 measure | pilot DONE; study-runner RUNNING | pilot n=60: install 80% / collect 57% / run 48% / buildable 25/60 = 42% / green-at-base 11/60 = 18% (ventures/c-measurement/pilot/results.csv). study-runner (per-PR base-vs-candidate with the PR's own tests) building + method review + background run (workflow wf_d52eb08e-743) → ventures/c-measurement/study/ |
| 4 inbound | PARTIAL | outreach/track-h/ (runbook, opener, follow-ups; verified 3 rounds); SIGNALS.md week-0 baseline. Pending: launch-kit-writer (after release), readme-rewriter ×3 (after release, so links are true), docs-site-builder (guardposts; after ≥1 release) |
| 5 verify | CONTINUOUS | every artifact above carries its verification appendix or verdict |
| DECISION v4 | DONE | appended + 3-lens red team + revision + 2 verification passes; orchestrator applied the last 4 fixes (n=60 pilot numbers; instrument gate replaces the pre-satisfied buildability gate; preamble disclosure; P read date) |

## Standing items (this session)
- a1-weekly-screen: 0 of 14 pass (research/a1-weekly-screen.md); next 2026-09-06
- signal-watcher: baseline in SIGNALS.md; next weekly entry 2026-09-06
- inbound-triager: nothing inbound
- ledger-keeper: $0 spent; LEDGER.md session-usage line at end of session
- commit-chunker: one commit per artifact enforced by the orchestrator (see git log)

## Open tasks (ordered)
1. Wave 2 workflow returns → rename plan-lint → agent-plan-lint, egress-guard → egresswall (pyproject name, console script, import name, README) → re-run scripts/check.sh → create public repos under Alex-lop → push → tag v0.1.0 → `uv build` + `uv publish` (UV_PUBLISH_TOKEN from keychain) → verify `pip install` from PyPI in a fresh venv → add `mcp-name:` README token first if the package ships an MCP surface (research/channels.md:175).
2. study-runner returns → read ventures/c-measurement/study/results-prs.csv progress; commit the instrument + METHOD.md; the background run continues across sessions (resume command in study/README.md).
3. pkg-guardrail-checkup (third package) builder — composes agent-plan-lint + egresswall; report shape = outreach/track-h/runbook.md §3 (six sections).
4. Wave 4: launch-kit-writer (Show HN needs a runnable artifact — research/channels.md:87; MCP registry; PyCoder's), readme-rewriter ×3 (PRs on Graphene/RegLineage/Nemisis), docs-site-builder (guardposts on GitHub Pages).
5. Contribution PR to motherduckdb/mcp-server-motherduck (hardened read-only `--secure` mode; research/contributions.md) — gated 2026-09-15 in DECISION v4.
6. End of session: LOG.md entry, WEEKLY.md (Sunday), LEDGER.md usage line, this file; push.

## Agents (this session) — role → artifact observed
| role | artifact |
|---|---|
| redactor (5 passes) + redaction-verifier (5) | 27 tracked files rewritten; private/{THIRD-PARTY.md,DENYLIST.txt,REDACTION-LOG.md,outreach/*,ma-filing-feed/} |
| identity-auditor | private/IDENTITY.md |
| secrets-scanner | scripts/prepush.sh, private/SCAN-REPORT.md, private/prepush.log |
| graphene-deploy-fixer ×2 + pr-verifier ×2 | Graphene PR #13 |
| license-fixer + pr-verifier | PRs Graphene #12, RegLineage #9, Nemisis #1, graphene-site #1 |
| naming-checker | research/naming.md |
| a1-weekly-screen | research/a1-weekly-screen.md |
| signal-watcher | SIGNALS.md |
| adoption-analyst / demand-side-scout / venue-recoverer / inbound-channel-mapper / study-precedent-scout + quote-verifier ×5 + fix ×5 | research/{adoption,demand,venues,channels,precedents}.md |
| contribution-scout + quote-verifier + fix | research/contributions.md |
| track-h-preparer ×3 + track-h-verifier ×3 | outreach/track-h/{runbook,opener,followups}.md |
| decision-v4-writer, red-team ×3, reviser, verifier ×2, fix | DECISION.md v4 + "Red-team pass (v4)" |
| corpus-widener | ventures/c-measurement/corpus/{candidates-v2.csv,FUNNEL-v2.md,scripts/} |
| base-build-pilot | ventures/c-measurement/pilot/{results.csv,METHOD.md,pilot.py,run.sh} |
| pkg-plan-lint, pkg-egress-guard + verifiers | ventures/plan-lint, ventures/egress-guard (in verification) |
| study-runner + method-reviewer | ventures/c-measurement/study/ (in flight) |

## Workflow run ids (this session)
wave0 wf_5cca3c1f-7fd · wave0-round2 wf_83fa9bf7-75d · wave1 wf_ea0d9c52-0e1 · wave2+3 wf_f3e2111a-317 · track-h wf_91f13d1b-b44 + wf_24177761-860 · decision-v4 wf_9c18a3bc-0d8 · contributions wf_92735dd2-731 · study-runner wf_d52eb08e-743

## Resume instructions
On restart: read CLAUDE.md, private/PRINCIPAL.md, this file. `git status` and `git log --oneline -30` show which artifacts landed (liveness = files + commits, never notifications). Continue from the first open task whose artifact is missing. Never `gh auth switch`. Never delete a branch on a public repo.
