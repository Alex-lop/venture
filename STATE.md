# STATE — resume point (machine-readable; update at every checkpoint)

session: 2 — two orchestrators on one checkout since 2026-08-31 04:21 EDT (see "Concurrency")
started: 2026-08-30
brief: CLAUDE.md v2 (installed this session; v1 kept at private/CLAUDE-v1.md)
principal_file: private/PRINCIPAL.md (merged; US resident; standing approvals: repos=yes pypi=yes oss-prs=yes track-h=yes)
current_wave: 2 (ship: agent-plan-lint and egresswall released to GitHub, PyPI = ASK-015; guardrail-checkup in verification) + 4 (inbound wiring) — waves 0, 1, 3, DECISION v4, Track H prep, README rewrites, docs site complete
push_rule: the redaction commit lands on origin before any other session-2 commit (done: f4e68d4)
last_checkpoint: 2026-08-31 ~05:50 EDT (session 2a; 2b has closed)

## Concurrency (2026-08-31, from 04:21 EDT)
- **Session 2a** (`money-maker-9a`, started 2026-08-30 20:42 EDT) owns `ventures/plan-lint`, `ventures/egress-guard`, `ventures/guardrail-checkup`: fix → verify → release. Running: `wf_b255ee0e-ece` = round 9 (agent-plan-lint + egresswall; red team + claims re-verify; started ~04:15, ETA 05:45–06:00 EDT); `wf_955ab038-512` = guardrail-checkup build + up to two verify/fix rounds (started ~03:35, ETA 06:30–07:30 EDT). `wf_e071a665-382` (round 8) finished.
- **Session 2b** (`money-maker-29`, 04:21–05:40 EDT window) owns everything else: checkpoint commits, the docs site, STATE/LOG/SIGNALS/LEDGER, README-PR repair.
- Shared-checkout protocol (agreed by message): stage+commit atomically with explicit paths, never `git add -A`; message the other session before any `git add` under the three package trees and before every commit to `main`; `git pull --rebase` before push; the pre-push hook on every push; no force-push ever; no `check.sh`/`pytest` inside the three trees from 2b (they write `.venvs/`, `dist/`).
- **No publish, no package repo, no merge from 2b** — 2a's round-8 red team found real blockers (below), and CLAUDE.md §2 forbids shipping a CHANGELOG that describes code other than what is shipped. The in-window fallback is the checkpoint commit + this file.
- **2b final state (05:13 EDT):** venture main 13f2c18 (LOG addendum) on top of 6c7fe93 (wiring); Alex-lop/guardposts 8a4dea1 (Pages rebuilt from it); Graphene #14 head a159860 — MERGEABLE, all 6 checks SUCCESS (recorded 05:45 EDT by 2a); previously: wheel+sdist, Linux 3.13, Firestore, Node 22, CodeRabbit all pass, `Python 3.13 / macOS sandbox` still pending at 05:12 (a docs-only change; 2a or the next session records its conclusion). Nothing else from 2b is in flight.
- Resume rule for any later session: run `ListAgents` first. If a peer session is alive and busy on the package trees, leave them to it and take the rest.

## Waves
| wave | status | evidence |
|---|---|---|
| 0 hygiene | DONE | redaction: 5 passes + 5 adversarial verifications, 325-entry denylist, prepush.sh (whole-word denylist, secret regexes, identity, paths) installed as .git/hooks/pre-push; private/IDENTITY.md; LICENSE PRs Graphene #12, RegLineage #9, Nemisis #1, graphene-site #1 (CI green; merge = ASK-012); Graphene deploy PR #13 (images build + procps; verified twice) |
| 1 instrument | DONE | research/{adoption,demand,venues,channels,precedents,naming,contributions,a1-weekly-screen}.md — each quote-verified (re-fetched) and fixed; adoption.md is INSTRUMENT-BIASED (88.6% GitHub) and carries a corrections section |
| 2 ship | RUNNING | **agent-plan-lint**: repo + v0.1.0 tag live (https://github.com/Alex-lop/agent-plan-lint; main 7408ee7 adds a docstring correction after the tag; build from main), nine verification rounds. **egresswall**: repo + v0.1.0 tag live (https://github.com/Alex-lop/egresswall), ten verification rounds, round 10 red team 0/0 and claims 0 false sentences, 675 tests, `mcp-name:` line in README. **PyPI upload for both = ASK-015** (2a's harness declines the token/publish step). **guardrail-checkup**: build + verify/fix rounds in flight (wf_955ab038-512). Wiring done: Graphene #14 and RegLineage #10 RELEASE-LINKs filled (plain pushes), site pages say source released / index pending, queue §A/§B repo URLs and counts filled; {PYPI_URL} stays a placeholder until the upload |
| 2 checkpoint | PARTIAL (2b) | working copies on origin/main so the work exists if the window closes: **e8a95c3** `ventures/plan-lint` (agent-plan-lint), **dfdf07f** `ventures/guardrail-checkup`, **0bb451f** `scripts/check-launch-cites.py`. Both labelled "working copy checkpoint; not a release". **egresswall not on any remote:** round-9 fix pass still running in the tree; hook false-positive rename pending — `ventures/egress-guard/tests/test_screen.py:45` assigns a quoted `hmac-sha256:…` fixture string to a local named `token`, which prepush.sh's generic secret regex (`token = "<12+ chars>"`) matches; 2a renames the local (e.g. `value`) when the tree is quiet (~05:45–06:00 EDT), then the tree is committed labelled "working-copy checkpoint mid-round-9; not the release tree". Clean-clone verification of both from `git archive` exports in scratchpad (never in the live trees), `wf_0aa192e8-13c`: **agent-plan-lint @ e8a95c3 GREEN** — `uv lock --check` ok, `uv sync --frozen`, 437 passed / 51 skipped (3.13-only glob tests on a 3.11 interpreter) / 0 failed, ruff lint+format clean, `uv build`, wheel installs into a fresh 3.12 venv, `agent-plan-lint --help` and `codes` (36 lines) run, `demo/demo.sh` output byte-identical to `demo/OUTPUT.txt` — so the sprint bar "installs from a clean clone, tests green" holds on the checkpoint; what blocks publishing is the round-8 red-team list, not the suite. **guardrail-checkup @ dfdf07f RED** (expected mid-build) — lock ok, sync ok, ruff clean, wheel + `--help` ok, but 4 of 168 tests fail: `demo/OUTPUT.txt` and `demo/OUTPUT.md` are stale against the code (22 diff lines), README says 128 collected tests vs 168, and `test_packaging.py::test_the_sdist_ships_the_demo_the_docs_and_the_tests` scrapes non-file tokens; 2a's builder rounds own these. Site note: `packages/egresswall.md` states 413 collected tests / 44 hostile servers while the mid-round-10 tree collects 630 / 46 — the page is re-synced (and `check_site.py` run without `--skip-packages`) at egresswall's checkpoint, not before |
| 3 measure | DONE | pilot n=60: install 80% / collect 57% / run 48% / buildable 25/60 = 42% / green-at-base 11/60 = 18% (ventures/c-measurement/pilot/results.csv). study complete: 107 PRs over 25 repos — 0/99 resolved PRs without a FAIL_TO_PASS test (Wilson [0%, 3.7%]); 78% of PR-touched tests PASS_TO_PASS; 74% of F2P via import/collection error; 14/99 have no assertion-level F2P. WRITEUP.md, SUMMARY.md, DATASET-CARD.md, analysis.py — red-teamed (3 lenses, 25 objections) and number-verified (242/246 + fixes). Study live at https://alex-lop.github.io/guardposts/study.html; launch drafts in outreach/queue.md carry that URL |
| 4 inbound | RUNNING | outreach/track-h/ done; SIGNALS.md baseline; README PRs open: Graphene #14, RegLineage #10 (MERGEABLE, checks SUCCESS), **Nemisis #2 repaired** (was CONFLICTING + CI failing after Alex's 12 commits to main on 08-30 21:39–22:17 EDT): main merged into `docs/customer-readme` as merge commit **ec0336e** (no force-push), README/PROOF/STATUS conflicts resolved, 54 claims re-verified and 11 corrected on the merged tree, CI failure (hard-coded bundle digest in the pasted console block) removed; 270 tests + ruff + mypy green, CI SUCCESS ×2, MERGEABLE/CLEAN; independent verifier PASS (`wf_c999a078-485`; two non-blocking notes in LOG.md). Guardposts site LIVE at https://alex-lop.github.io/guardposts/ (repo Alex-lop/guardposts; source at ventures/guardposts-site/); **e045dfe / guardposts b43434e**: pages now link the two pushed working copies and say "in verification, not released"; check_site.py `--skip-packages` passes (the package-count re-check runs `uv run` inside the trees, so it waits for a quiet tree). LICENSE/deploy PRs: all OPEN, MERGEABLE, checks SUCCESS (Nemisis #1 mergeable=UNKNOWN at query time) |
| 5 verify | CONTINUOUS | every artifact above carries its verification appendix or verdict |
| DECISION v4 | DONE | appended + 3-lens red team + revision + 2 verification passes; orchestrator applied the last 4 fixes (n=60 pilot numbers; instrument gate replaces the pre-satisfied buildability gate; preamble disclosure; P read date) |

## Standing items (this session)
- a1-weekly-screen: 0 of 14 pass (research/a1-weekly-screen.md); next 2026-09-06
- signal-watcher: baseline in SIGNALS.md; interim 2026-08-31 04:35 EDT: 3 non-fork stars total, 11 open issues (owner/agent), 0 stranger issues — the one non-owner item since 08-24 is imgbot[bot] on Graphene #6 (bot; does not count); nothing released, so no download signal exists; next weekly entry 2026-09-06
- inbound-triager: nothing inbound
- ledger-keeper: $0 spent; LEDGER.md session-usage line at end of session
- commit-chunker: one commit per artifact enforced by both orchestrators (see git log)

## Open tasks (ordered)
1. (2a) Round 9 returns → fix pass → if clean, release in order agent-plan-lint → egresswall → guardrail-checkup exactly as the wave-2 row says; message 2b (or record here) each package name the moment `uv pip install <name>==0.1.0` from PyPI verifies. If not clean when 2a's window ends: commit the trees labelled as checkpoints and write the blocker list here.
2. DONE: egresswall release tree committed to venture main and released to GitHub (v0.1.0).
3. DONE for the source release (2b): site page + index link https://github.com/Alex-lop/agent-plan-lint and say the index upload is pending (check_site.py full run), Graphene #14 links the repo, queue.md §A has `{REPO_URL}`/`{PL_TESTS}`=488. **At each PyPI upload**, in the same commit: add the name to `ventures/guardposts-site/RELEASED` + the install line on its package page (+ replace the "working copy … not a release" sentences), run `scripts/check_site.py` without `--skip-packages`, push to venture and to Alex-lop/guardposts. Then the RELEASE-LINK one-line commits: Graphene #14 branch `docs/customer-readme` line 49 (agent-plan-lint), RegLineage #10 line 42 (egresswall), Nemisis #2 line 107 (`<package-name>` — decide at release; guardrail-checkup is the candidate since Nemisis is the study's instrument, not a source of either package). Then the package launch drafts: re-sync per the header of outreach/queue.md §Package launches and run `scripts/check-launch-cites.py`.
4. DONE (2b): Nemisis #2 repaired and verified — ec0336e, MERGEABLE/CLEAN, CI green. Non-blocking follow-up for whoever next touches Nemisis: `docs/STATUS.md:50` says "267 tests" (tree collects 270) and the README-truth regex `(\d+)[- ]tests? (?:suite|passed)` does not catch that phrasing.
5. Contribution PR to motherduckdb/mcp-server-motherduck (hardened read-only `--secure` mode; research/contributions.md) — gated 2026-09-15 in DECISION v4.
6. End of each session: LOG.md entry, WEEKLY.md (Sunday), LEDGER.md usage line, this file; push.

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
| pkg-plan-lint, pkg-egress-guard + verifiers ×8 rounds (2a) | ventures/plan-lint, ventures/egress-guard (round 9 in flight) |
| pkg-guardrail-checkup + verifiers (2a) | ventures/guardrail-checkup (verify rounds in flight) |
| study-runner + method-reviewer + study-writer + red-team + verifier | ventures/c-measurement/study/ |
| readme-rewriter ×3 + auditors | PRs Graphene #14, RegLineage #10, Nemisis #2 |
| launch-kit-writer | outreach/queue.md §Package launches; scripts/check-launch-cites.py |
| docs-site-builder | ventures/guardposts-site/, Alex-lop/guardposts (Pages live) |
| orchestrator (2b) | checkpoints e8a95c3, dfdf07f, 0bb451f; site e045dfe + guardposts b43434e; this file |
| clean-clone-installer ×2 (2b) | `wf_0aa192e8-13c`: agent-plan-lint @ e8a95c3 GREEN (437/0), guardrail-checkup @ dfdf07f RED (4/168 stale demo + count) — details in the wave-2 checkpoint row |
| readme-pr-repairer + pr-verifier (2b) | Nemisis #2 — merge commit ec0336e, 54 claims checked / 11 fixed, CI green, verifier PASS (`wf_c999a078-485`) |

## Workflow run ids
2a: wave0 wf_5cca3c1f-7fd · wave0-round2 wf_83fa9bf7-75d · wave1 wf_ea0d9c52-0e1 · wave2+3 wf_f3e2111a-317 · track-h wf_91f13d1b-b44 + wf_24177761-860 · decision-v4 wf_9c18a3bc-0d8 · contributions wf_92735dd2-731 · study-runner wf_d52eb08e-743 · wave2-round3 wf_8f68ca8f-88a · wave2-round5 wf_8f35ead4-fdd · readme wf_de43755e-5b6 + wf_cca0787f-f2b + wf_66ec413f-2db · study-writeup wf_3b47bb2d-80f · round8 wf_e071a665-382 (done) · round9 wf_b255ee0e-ece (running) · guardrail-checkup wf_955ab038-512 (running)
2b: checkpoint-verify wf_0aa192e8-13c · nemisis-pr-repair wf_c999a078-485

## Resume instructions
On restart: read CLAUDE.md, private/PRINCIPAL.md, this file. `ListAgents` — if a peer session is alive, message it before touching anything it owns (Concurrency, above). `git status` and `git log --oneline -30` show which artifacts landed (liveness = files + commits, never notifications). Continue from the first open task whose artifact is missing. Never `gh auth switch`. Never delete a branch on a public repo. Never force-push. Never publish a package whose CHANGELOG/README describe code other than what is in the tree.
