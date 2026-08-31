# LOG — daily: done / learned / next (newest on top)

## 2026-08-31 — session 2b (04:21–05:40 EDT): a second orchestrator on the same checkout — checkpoints, site truth, the Nemisis README PR repaired

**Done (files, not chat; one commit per artifact)**
- **Two orchestrators, one checkout.** `ListAgents` showed session 2a alive and mid-round on the package trees; the split was agreed by message — 2a: fix → verify → release for the three packages; 2b: everything else — with the shared-index protocol written into `STATE.md` §Concurrency.
- **Working copies on the remote.** `ventures/plan-lint` (e8a95c3) and `ventures/guardrail-checkup` (dfdf07f) were untracked — nothing of either was on origin — and are now labelled checkpoints; `scripts/check-launch-cites.py` (0bb451f). egresswall stays untracked until 2a renames one fixture local whose shape the pre-push secret regex matches.
- **Clean-clone verification of the checkpoints** (git-archive exports; nothing run in the live trees): agent-plan-lint GREEN — 437 passed / 0 failed, wheel installs in a fresh 3.12 venv, demo byte-identical; guardrail-checkup RED — 4 of 168 (stale demo outputs, README count 128 vs 168, a packaging-test scrape), handed to 2a's builder.
- **Site truth.** The guardposts pages said the working copies were not pushed and that guardrail-checkup had no code; both false after the checkpoint. Fixed on venture (e045dfe) and `Alex-lop/guardposts` (b43434e); Pages rebuilt; `check_site.py --skip-packages` passes.
- **Nemisis README PR #2 repaired.** It was CONFLICTING with CI failing: Alex pushed 12 commits to main on 08-30 21:39–22:17 EDT after the branch was cut. main was merged into the branch (merge commit ec0336e — no force-push), README/PROOF/STATUS conflicts resolved, 54 claims re-verified against the merged tree and 11 corrected where main had made them false (the CI failure itself was a hard-coded bundle digest in the pasted console block; now elided, the claim that it prints one kept). 270 tests + ruff + mypy green locally, CI green, PR MERGEABLE/CLEAN; an independent verifier passed it with two non-blocking notes (`docs/STATUS.md`'s "267 tests" escapes the new staleness regex; three external-literature figures are unverifiable offline and attributed as such).
- **Signals interim:** 3 non-fork stars, 0 stranger issues (the one non-owner item since 08-24 is imgbot), nothing released, nothing inbound.

**Not done, and why**
- **No package published, no package repo created.** 2a's round-8 red team found real blockers (path guard passes Default_Ignorable code points; YAML loader lets three exception types escape; egresswall's embedded-document check bypassed by a leading format character; three CHANGELOG sentences describe code that is not shipped). Publishing that tree would put a false CHANGELOG under Alex's name (CLAUDE.md §2). Round 9 returns ~05:45–06:00 EDT, after this window; the fallback the sprint order names — checkpoint + reason in `STATE.md` — is what landed.
- **egresswall is on no remote** until the fixture rename; 2a owns that and will commit it labelled as a mid-round checkpoint.

**Learned**
- Two sessions on one checkout work only if the index is treated as shared: explicit paths, never `git add -A`, never `stash` or `pull --rebase` (both move the other session's uncommitted edits) — fetch and compare instead.
- The pre-push hook scans the working-tree content of every tracked file, so tracking the package trees means the other session's mid-edit fixtures can block a push; quoting one such line in `STATE.md` tripped it too.
- A README that pins the digest of an artifact whose bytes move with the code fails on the next unrelated commit; elide the digest and keep the sentence that says one is printed.

**Next (session 3)**
- 2a's release sequence (agent-plan-lint → egresswall → guardrail-checkup) once round 9 is clean; then `STATE.md` open task 3 (site RELEASED flag, RELEASE-LINK commits, launch-draft re-sync). egresswall checkpoint. ASK-012: all eight PRs are mergeable again. Weekly `signal-watcher` and the A1 screen on 2026-09-06.

## 2026-08-30 → 2026-08-31 — session 2: brief v2 installed; hygiene, instrument repair, two packages to release bar, the study run and written

**Done (files, not chat; every artifact verified by an adversarial pass before commit; one commit per artifact)**
- **Brief v2 installed** as `CLAUDE.md` (v1 kept privately); `private/PRINCIPAL.md` merged from Alex's answers (US resident, TA grader, 12 h/week, standing approvals yes ×4, Track H yes). `STATE.md` is the resume point.
- **Wave 0 hygiene:** third-party personal data redacted from 27 tracked files in five passes against five adversarial sweeps (325-entry private denylist; named-people lists and the sample digest moved to `private/`); `scripts/prepush.sh` (secret regexes, whole-word denylist, author/remote/gh identity, no private paths) installed as the pre-push hook; `gh` is Alex-lop (ASK-001 closed). LICENSE copyright lines: PRs Graphene #12, RegLineage #9, Nemisis #1, graphene-site #1 (CI green). Graphene deployment images now build and can read process identity: PR #13 (two defects — missing `procps`, and a `.dockerignore` allowlist that omitted every COPY path — verified twice in containers).
- **Wave 1 instrument repair** (`research/`): adoption measured for 62 kill-incumbents — 27 fail the "dominant" bar; distinct non-owner authors in 90 days is the discriminator stars are not; demand — payroll is the only proven transaction ($130k–$340k bands), self-serve band is $24–48/user/month for agent PR review, ten AI-security vendors publish no price; venues — Arctic Shift recovers Reddit and Wayback recovers G2 (Session 1's "403" list was partly a robots.txt policy, not a block); channels — Show HN excludes the study, the MCP Registry needs an `mcp-name:` README token before the PyPI upload, arXiv has an endorsement gate; precedents — Track M's quantity is unpublished (nearest: arXiv 2607.28871 on benchmark tasks; 2606.18168 static oracles); naming — `agent-plan-lint`, `egresswall`, `guardrail-checkup`, family `guardposts`; contributions — the MCP sqlite server is archived, so readonly-gateway re-opens (PR to `motherduckdb/mcp-server-motherduck` first), change-receipt is neither a package nor a PR this quarter. Every file quote-verified by re-fetch and fixed.
- **Wave 2 ship:** `ventures/plan-lint` (agent-plan-lint) and `ventures/egress-guard` (egresswall) built to the release bar and put through seven rounds of clean-clone install × claims-vs-code audit × red team, each round fixing what the last found (glob DoS 45 s → 0.36 s; expected-output paths now under the write grant; MCP-mandated fields allow-listed; JSON-in-text tool results screened structurally). Final round and release: see the line below this entry.
- **Wave 3 measure — done:** corpus widened to 60 repos at ≥10 stars (pool exhausted); 60-repo base-build pilot in Docker — 80% install / 57% collect / 48% ran / **42% buildable** (25 repos), gate cleared; study-runner built, method red-teamed, 107 PRs run: **0 of 99 resolved PRs shipped no FAIL_TO_PASS test** (Wilson [0%, 3.7%]); 78% of PR-touched tests are PASS_TO_PASS; 74% of F2P is import/collection error; 14/99 have no assertion-level F2P. Write-up, dataset card, summary, `analysis.py`; three-lens red team (25 objections dispositioned); 242/246 numbers reproduced by an independent verifier and the rest fixed. Launch drafts in `outreach/queue.md` await a public URL.
- **Wave 4 inbound:** Track H runbook/opener/follow-ups (every tool command verified offline; the agentrc install line in its own README is broken on npm 12 and the runbook carries the working one); customer-voice README PRs Graphene #14, RegLineage #10, Nemisis #2 (each audited to zero majors); `SIGNALS.md` week-0 baseline; guardposts docs site in build.
- **DECISION.md v4** appended and red-teamed (three lenses): dollar gates reinstated, whole-plan gate split so stars alone cannot pass it, ASK-010 (job/co-op in parallel; default "run both"), package 4 retargeted after the archived-sqlite finding, buildability now a finding not a gate, an instrument gate for 2026-09-20 in its place.
- `ASKS.md`: ASK-001/007 resolved; ASK-010..014 with defaults and dates. `LEDGER.md`: $0 spent.

**Learned**
- Redaction converges only with adversarial sweeps and class-level fixes; a denylist grep proves nothing about what is not on the list. Five passes, ~330 strings; the public git history still holds the originals (ASK-011).
- The verify-wave finds real defects every round for the first six rounds; the crash classes that survive longest are malformed-input paths (huge ints, complex YAML keys, escaped quotes in ids) and the "obvious" data shape nobody encoded (tool results as JSON inside `content[].text`).
- "A free incumbent exists" killed 27 of 62 ideas whose incumbents fail the dominant bar today; the number a project cannot manufacture is distinct non-owner authors in 90 days.
- The study's own thesis did not survive: agent PRs in buildable, well-maintained repos ship at least one test that fails on base — mostly because the module arrives with its test (import error at base). The honest headline is two numbers, per-PR 0% and per-test 78% PASS_TO_PASS, with the mechanism named.
- The harness's permission layer declines `gh pr merge` in this mode; merges are the principal's clicks (ASK-012). Session limits can kill background agents mid-run — the journal + files on disk made every restart lossless.

**Next (session 3)**
- Release both packages once round 7 is clean: own repos under Alex-lop → tag v0.1.0 → PyPI (`mcp-name:` first) → fill the RELEASE-LINK placeholders in the three README PRs → launch drafts (Show HN for the runnable packages; regular HN + newsletters + Bluesky for the study).
- Create `Alex-lop/guardposts`, enable Pages, replace `{STUDY_URL}`; then the study is postable.
- `guardrail-checkup` builder (report shape = Track H runbook §3); the motherduck `--secure` PR (gated 2026-09-15); weekly `signal-watcher` and A1 screen on 2026-09-06.
- Alex: merge the eight open PRs (ASK-012), decide ASK-010/011/013/014 (defaults apply on their dates), Thursday 2026-09-03 Venture Café with `outreach/track-h/`.

## 2026-08-30 (Sunday) — session 1: Phase 0 → Phase 2, red-teamed, in one day

**Done (all read-only research, code reading, and drafting; nothing sent, nothing spent, no accounts created)**
- Renamed the brief to `CLAUDE.md`; filled §0 with everything inferable and the Northeastern/MA policy research (primary sources); `assets/` gitignored; 12 public repos cloned.
- **Phase 0** → `ASSETS.md`, `STRENGTHS.md`. Every test suite run (1,229 + 408 + 238 pass). Headline: the seatbelts are real; the engines are demo-ware; no PDF pipeline, no crawler, nothing deployed, no second user ever.
- **Phase 1** → 24 dossiers in `ideas/` (14 from the brief, 9 asset-suggested, 1 red-team-requested), each with verbatim complaints, pricing, reachability, kill criteria and rubric scores; **every dossier adversarially verified** (quotes re-fetched, load-bearing claims checked, scores challenged); 6 competitor deep-dives; ranking in `ideas/README.md`.
- **A1 sweep** → 3 finders, 14 vetters: Algora's public board no longer exists; 14/14 skips; best EV $7/hr. Recorded in the A1 dossier.
- **First customer-facing artifact** → the 2026-W36 Massachusetts filings digest: 320 filings across 30 towns, hand-compiled by 9 collectors with robots.txt respected and homeowners anonymized. Kept as proof of method after B was killed. The rows are held privately (session 2, redactor); the public method record is `ventures/ma-filing-feed/samples/README.md`.
- **Phase 2** → `DECISION.md` v1 → red-teamed by three adversaries → v2 → the two follow-ups they demanded came back and killed B and B′ → **v3 (final for day 1)**.
- **C started** → `ventures/c-measurement/corpus/`: 14,417 agent-trailered merged PRs → 23 qualifying repos; funnel and biases documented.
- **Outreach** → `outreach/queue.md` (12 A-track companies with their own job-post quotes; September calendar), `outreach/crm.csv`; approval queued as ASK-009. **`ASKS.md`: nine ASKs**, ASK-007 (visa/co-op) first.
- `WEEKLY.md` week-0 review; `LEDGER.md` at $0.

**Learned**
- `gh` on this machine was authenticated as **a different person's GitHub account, not Alex's** — no GitHub writes until ASK-001 (**resolved 2026-08-30**: `gh api user` → `Alex-lop`); a secret is committed in plaintext in that account's public repository and only its owner can rotate it (ASK-002; specifics in `private/THIRD-PARTY.md`). `AC-Washing-Well@commit-changes` publishes CS2800 coursework (ASK-003).
- The brief's defaults are dead on the evidence (A1 saturated, B4 free incumbents, C1's analogue shut down). Every asset-derived dev-tool idea has a free implementation shipped in the last eight weeks. What survives verification is either physical/local or paid-on-delivery — and the red team showed even those need a real budget event, not a loud thread.
- **B died to the state's own data**: the EEA portal's free NOI API (applicant, address, resource areas, decision date; one-day lag; 18–55 days before the agenda). The Cursor "budget event" behind A's v1 wedge was refuted by the primary source (shutoff 2026-11-12; `/init` `/import` `/doctor` do the migration free).
- Two independent tests of the provenance thesis failed in opposite directions (r2: pain, no budget; r3: budget, no pain). Stop testing it.
- Research-process limits worth remembering: reddit.com 403s everything; ContractorTalk/G2/TrustRadius/Upwork/Fiverr/bls.gov 403; mass.gov 403s non-browsers (use Wayback or the EEA portal); WebSearch budget exhausts at 200 calls per agent session; Capterra/Trustpilot/Indeed/HN Algolia/GitHub/BBB/PissedConsumer/vendor pricing pages work; GitHub search doesn't honour phrase quoting; CivicClerk's OData pages at 15 rows regardless of `$top`.

**Next (session 2, once Alex answers ASK-001…009)**
- Alex: ASK-007 first; Venture Café Thu 2026-09-03 (opener in `outreach/queue.md`); send the A follow-ups within 24 h.
- Agent: widen the C corpus to ≥10 stars and script the 100-repo base-build pilot (the study's real falsifier); draft the free-autopsy runbook (agentrc + `/doctor` + `cc-safety-net` + the three-invariants read) so each session is repeatable; weekly 10-minute A1 screen; nothing on B unless an autopsied team asks for it.
- Repo hygiene once ASK-004 clears: LICENSE copyright lines, graphene-site LICENSE, the `/bin/ps` deployment defect.
