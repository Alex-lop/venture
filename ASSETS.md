# ASSETS — Phase 0 inventory

**Inventoried:** 2026-08-30 · **Method:** one read-only reader agent per repo (two for Graphene), each ran the repo's own test suite, checked authorship via the GitHub API, and wrote a full narrative report (kept in the session scratchpad; the numbers below are from those reports). Nothing was edited, pushed, or contacted.

## Summary table

| Asset | What it is | LOC (code / tests) | Tests run today | License | Authorship | Sellable state |
|---|---|---|---|---|---|---|
| **Graphene** | Publication-control layer for parallel coding agents: fenced workspaces, plan validation, isolated git refs, offline-verifiable audit capsule, `why` provenance query, MCP server, TUI | 75.2K backend / 56.6K tests (137K total) | **1,229 passed**, 5 skipped, 617 s; ruff clean; 5-job CI green | Apache-2.0 (copyright line unfilled) | Solo (208 commits + 1 image bot) | Control plane is real; agent engine is demo/replay. **The seatbelt is the asset.** |
| **RegLineage** | Capability-lease runtime: hash-bound, expiring, narrowly scoped "leases" for AI data access that fail closed when governance context changes; egress firewall; zero-dep MCP server; review→approve→publish→readback workflow | 33.5K src / 16.1K tests | **408 passed** offline (228 unit + 36 capability + monitoring/mcp/integration suites) | Apache-2.0 (copyright line unfilled) | Solo (92 commits; 1 stray scaffold commit by another GitHub account at repo creation — resolve, see hygiene) | Runtime + firewall + MCP server are real. "Regulatory change" extraction does not exist. |
| **Nemisis** | Adversarial differential verification of AI-generated patches: ticket + diff → typed executable claims → same test bundle on base and candidate in isolated worlds → SUPPORTED / REFUTED / UNRESOLVED matrix with tamper-evident manifest | 4.3K (1.7K generic / 1.4K vendor-tied) | Local hero run reproduced exactly; strict mypy over 25 files; CI tests the built wheel | Apache-2.0 (copyright line unfilled) | Solo (6 commits, all 2026-08-30) | Engine is real for one packaged fixture; runs exactly one repo; Nemotron/ConTree paths never hit a live provider. |
| **X-Scraper** | Local "feed-to-snapshot" workbench for X: Playwright capture behind a *logged-in* session → SQLite snapshots → diff/search/export → read-only MCP access; durable job queue; approval protocol | 26K (11.9K tests) | **238 passed**, ruff clean, 6/6 JS | MIT | Solo (60 commits) | **Not commercializable as-is** (X ToS: scraping behind login). Four generic sub-assets are. |
| **graphene-site** | Dependency-free static marketing site for Graphene, live on GitHub Pages | 1.9K | 2 headless suites pass | **None** (all rights reserved by default) | Solo | Live. The deleted `refresh.py` "claims bound to evidence" build step is the idea worth keeping. |
| **Alex_Lopez_Website** | Personal portfolio site, live on Pages | 1.8K | red test suite | MIT | Solo | Career capital only. |
| **AXFold, AC-Washing-Well, AgenticCinemaFramework, The-Greater-Stake, Alex-lop** | Empty repo / accidental push / two research memos / profile README | ~0 | — | mixed | Solo | Nothing to reuse. See hygiene. |
| **Graft** (fork) | Unmodified fork of `trailhq/Graft` (npm `@nanonets/graft`), an open-source code-context graph for coding agents — **a competitor/substrate, not Alex's IP** | 37.8K TS | 836/836 pass, 27 s | MIT (theirs) | 0 commits by Alex; 63 behind upstream | Worth $0 as owned IP; worth a lot as a free dependency (see B4 notes). |
| **Two repos cloned from a different person's GitHub account** | **Not Alex's account.** They belong to a different person, whose account was the active `gh` login on this machine; specifics in `private/THIRD-PARTY.md` | — | — | none | **Not the principal** | Removed from `assets/`. See ASKS. |

---

## 1. Graphene — `Alex-lop/Graphene`

**What it does.** Sits *after* an agent runtime and decides which agent-proposed changes may become a commit. Operator declares a deny-by-default policy (read/write globs, frozen argv command allowlist, network deny, budgets). A plan is statically validated (455-LOC engine, ~30 typed issue codes: cycles, parallel write-path conflicts, out-of-scope paths, unverified criteria, self-asserted criteria), bound to a base SHA and its own digest. Parallel workers get private workspaces plus fencing tokens; every write re-asserts a 10-tuple binding inside one SQLite transaction, so a stale worker physically cannot publish. Assembly merges accepted artifacts into one exact candidate patch; verification runs a frozen check inside a macOS Seatbelt sandbox; `workspace_audit.py` independently measures what changed on disk. After policy pre-authorization or TTY-attested approval it creates exactly one commit under `refs/graphene/results/<hash>` via compare-and-swap `update-ref` — never pushes, merges, or touches the supplied checkout. Two read surfaces: `graphene why <path>` (causal chain file → publication → attempt → inputs → assembly → verification → approval) and `graphene mission capsule` (portable, redacted, offline-verifiable bundle). Nine-tool MCP stdio server.

**Verified today.** Full scripted mission end to end on a scratch repo (init → start → approve-plan → 7 attempts incl. a retry → assemble → verify → approve → isolated ref), confirmed with plain `git` that the checkout is untouched and exactly one commit lands on the result ref; capsule export + cold verify from a clean clone; wheel/sdist install outside the checkout; Firestore emulator and Docker executor suites.

**Reusable (high).**
- `orchestration/validation.py` — plan admission gate (cycles, conflicts, scope, unverified criteria). Standalone; depends only on models + hashing.
- `orchestration/workspace_audit.py` — independent "what actually changed" audit vs. declared write lease; Unicode case-collision and Windows reserved-name checks.
- `orchestration/local_result.py` + `lineage/local_commit.py` — isolated git-ref creation: flock, `worktree add --detach`, re-derived patch digest must equal candidate digest, CAS `update-ref`; hermetic git env (strip `GIT_*`, `GIT_CONFIG_GLOBAL=/dev/null`, alternate `GIT_INDEX_FILE`).
- `orchestration/capsule.py` — offline-verifiable audit capsule (hash-chained events, per-attempt evidence, receipts).
- `orchestration/process_control.py` — PID-reuse-safe owned-process registry (Linux boot_id + starttime; macOS libproc birth token).
- `execution/adapter.py:344` + `orchestration/sandbox.py` — macOS Seatbelt profile generator and Docker executor for untrusted code.
- `ui/dag_render.py` — pure-function terminal DAG renderer.
- `hashing.py` — canonical JSON + domain-separated, length-prefixed tree digest.
- `tests/unit/test_readme_contract.py`, `test_documentation_truth.py`, `scripts/verify_installed_artifacts.py`, parity scripts — "docs cannot outrun the code" release discipline.
- (medium) MCP server hardening (`reject_forged_arguments`), `adk_planner.py` "constrain the model to judgment, compile the boilerplate" pattern, event-sourced SQLite store, GCP least-privilege runbook.

**Domain knowledge embedded.** Seatbelt SBPL authoring for untrusted tests; python.org framework-build launcher exec-in-place breaking process identity; SQLite `LIKE` on BLOB behaving differently between macOS 3.51 and slim-image 3.46; `python:3.13-slim` lacks `procps`; Vertex regional model availability; Firestore 1 MiB sharding; three distinct meanings of "agents ran in parallel".

**Quality.** Top decile for a solo project. Locked deps, CI on two OSes + Firestore emulator, 1,268 automated checks, doc-truth tests. **Two defects found:** (1) all three deployment images pin `python:3.13-slim`, which has no `/bin/ps`, so `process_control.py:139` raises unconditionally — **the deployment image cannot run the product** (`scripts/linux_parity_check.sh` already reports `LINUX PARITY: FAILED`); (2) `macos_parity_check.sh` can report a false FAILED on a stale venv. Docs are dense and self-auditing — superb for a judge, hostile to a customer.

**Honest split.** Real: the control plane (store, fencing, validation, envelopes, audit, sandbox, isolated ref, `why`, capsule, TUI, MCP, CLI). Demo: the *agent* half — the only credential-free path replays hardcoded fixture bytes; live Gemini path has five `NOT PROVEN` rows; `google-adk` is a hard runtime dependency; Firestore/Cloud Run never deployed; `lineage/` + `viewer/` (~11.8K LOC) is a superseded protocol tour; `benchmarks/` is a 122-line justification with no benchmark. 0 stars, 0 issues, no second user ever.

**License / collaborators.** Apache-2.0; solo. Repo was `AllThingsAgenticHackathon` until recently — **hackathon/sponsor IP terms not found in the repo; confirm none apply** (ASK-004). Copyright line in LICENSE still boilerplate.

**Days to a first paying customer** (agent estimates): ~13 focused days for a *single local technical buyer* (fix `/bin/ps`, one live credentialed run captured as a capsule, delete the legacy third, provider-agnostic worker adapter, PyPI, onboarding); ~18–26 days for "wrap your existing coding agent: fenced workspace + provable candidate + audit receipt". A *team* product is a different order of magnitude.

**Commercial angles.** (1) **Sell the seatbelt, not the engine** — bounded workspace + provable candidate wrapping any coding agent; buyer: platform lead at 150–800 eng companies. (2) **AI-change provenance receipts** — capsule as a compliance deliverable for SOC 2 / ISO 27001 change-management; buyer: SDLC governance owner at regulated 50–300 person companies. (3) **Plan/policy validator as a package** — "lint your agent's plan before it runs"; buyer: internal agent-platform owners. (4) Open-core isolation primitives (owned processes, sandbox, hermetic git) for agent-runtime startups. (5) Release-truth tooling (doc-truth tests, installed-artifact probe) for Python devtool teams.

## 2. RegLineage — `Alex-lop/RegLineage`

**What it does.** A capability-lease runtime for AI data access: an agent gets a narrowly scoped, hash-bound, expiring lease to run one registered analysis over one field set; a poller watches a governance catalog (DataHub) for changes; on a relevant change only the intersecting lease fails closed; a fixed repair is proposed, separately approved, written back, re-read with matching hashes, and only then does a replacement lease activate. Two demo domains (NYC taxi on DuckDB; synthetic fitness retention with per-field ACCESS/COMPUTE/MODEL_CONTEXT/DESCRIBE/PUBLISH grants, HMAC tokenization, k-anonymity). DataHub hackathon entry (3 stars).

**Reusable (high).** `canonical.py` (74 LOC canonical JSON+SHA-256, stdlib only); `runtime/models.py` self-verifying hash-bound records; `runtime/store.py` transactional SQLite lease store with a 6-state machine, fencing epochs, idempotency keys, hash-chained audit, and the scope-intersection impact assessor (`_build_assessment`, the genuinely novel idea); **`agent/egress.py` value-level egress firewall** (denied fields, email/SSN/phone regexes, join tokens — raises rather than redacts); **`mcp_runtime/server.py` zero-dependency MCP JSON-RPC stdio server** (modern + 3 legacy handshakes, schema-validated args, recursive `_screen()` over 25 forbidden keys + substring rules); `mcp_runtime/contracts.py` uniform `GovernedResponse` envelope; **`validation/citations.py` structured citation validator** (10 stable failure codes — "did the model actually quote the source?"); `validation/graph_paths.py` (catches hallucinated lineage shortcuts); `workflow/` 12-state review→approve→publish→readback with approval hashes that ignore cosmetic edits; `models/workflow.py` `ImpactClaim` that **bans "compliant/violation/unlawful" in code**; `evaluation/` — a real 16-page CPPA Delete Act regulation (SHA-pinned), three synthetic policies, and a hand-authored 13-finding gold answer key.

**DataHub coupling.** Confined to `datahub/` + 8 `urn:li:` assertions; every external boundary is a `Protocol` with an in-memory twin, which is why 408 tests pass offline and why the code is salvageable.

**Honest split.** Real: runtime, hashing discipline, both egress firewalls, MCP server, impact assessor, snapshot differ, validators, CI (incl. Docker build + health smoke), eval corpus. Demo: **PDF-to-structured-records is essentially absent** (70 lines of `str.find` against two literals); the obligation extractor does not exist (one hand-written JSON); the "drafting agent" injects known defects on purpose; the compiler emits one hardcoded SQL string; ~11% of `src/` is presentation. **No authentication anywhere** — reviewer identity is an unvalidated string.

**Relevance to a regulatory-change product.** You have the *back half* (verification, approval, audit trail, readback) and an eval set. You do **not** have a regulator fetcher/differ, a PDF→obligation extractor, or a rule→control mapper. Agent estimate: 60–90 focused days, mostly new work. Ship-the-lease-runtime as "revocable data leases for AI agents": ~15–20 days. Ship the egress firewall / MCP guardrail as a pip package: **~5–8 days** (smallest surface, weakest moat).

**License / collaborators.** Apache-2.0, copyright line unfilled. One stray commit at repo creation by another GitHub account — likely template/scaffold; **confirm and document before commercializing** (ASK-004). Hackathon/sponsor terms not present in repo — confirm.

**Commercial angles.** (1) **MCP egress firewall** — pip-installable guard in front of any MCP server's tool responses; buyer: internal AI-platform owner at 200–2,000 person companies. (2) **Revocable data leases for AI agents**; buyer: data-governance heads at regulated enterprises (long sales cycle). (3) **Citation-integrity verification for AI-drafted compliance/legal work** — API/CLI that checks a claim + citation against the source; buyer: compliance directors, legal ops.

## 3. Nemisis — `Alex-lop/Nemisis`

**What it does.** "Don't ask whether the agent says it's done; make the patch prove each claim." Ticket + candidate diff → typed executable claims (INVARIANT / CHANGE_WITNESS) → one immutable verification bundle run against base and candidate snapshots in separate temp worlds → per-claim verdict matrix (SUPPORTED / REGRESSION / NON_DISCRIMINATING / UNRESOLVED …) → JSON manifest + static HTML report, cross-validated by a 200-line fail-closed `validate_manifest()`. The packaged fixture is an inventory-reservation patch that passes existing tests but double-decrements on crash-then-retry — and the matrix catches it as UNRESOLVED. NVIDIA × Nexius hackathon.

**Reusable (high).** `matrix.py` (verdict truth table), `evidence.py` (manifest validator, proven against five tamper classes), `patches.py` (conservative diff validation + fixed-argv apply + post-apply file-set check), `junit.py` (fail-closed parser trusting only a co-shipped pytest plugin's annotations), `safety.py`, `hashing.py`, `bundle.py`, `models.py` (24 frozen strict Pydantic contracts). ~700 LOC of provider-free, tested library.

**Domain knowledge.** A test that ERRORs is *absence* of evidence, not failure; a CHANGE_WITNESS test passing on both base and candidate indicts the test (NON_DISCRIMINATING); candidate-supplied tests can never be acceptance evidence; pytest JUnit XML alone cannot separate assertion failure from error; runner hardening against a candidate repo injecting plugins/config.

**Honest split.** Real execution layer (real subprocesses, real `git apply`, real pytest, deterministic digests reproduced across machines). Never executed against reality: Nemotron path (515 LOC) and ConTree sandbox path (474 LOC) — ~45% of `src/` tested only against fakes, honestly labelled `MOCKED_TEST_ONLY` / `BLOCKED`. Runs exactly one repository; no dependency-install step; local mode is not sandboxed.

**Days to a customer.** 20–32 focused days for a one-customer GitHub check (arbitrary-repo intake, dependency installation inside a world, live sandbox, delivery surface, red/flaky base suites). **3–5 days to publish the library** (`patches`+`safety`+`bundle`+`junit`+`matrix`+`evidence`).

**License / collaborators.** Apache-2.0, solo, copyright line unfilled; no sponsor terms in repo — confirm (ASK-004).

**Commercial angles.** (1) **Merge gate for AI-generated PRs** — a check that posts the claim-by-claim evidence matrix; buyer: VP Eng / platform at 150–800 person companies rolling out agents. (2) **Bug-fix proof-of-work** for teams billing fix work or running SLAs. (3) **Tamper-evident audit trail for AI-authored changes** in regulated software. (4) ~~OSS library for safely applying and verifying LLM-written diffs~~ — **killed by the C-track deep-dive:** Codex, Aider and OpenHands each solved patch-apply in-tree; SWE-agent's applier is five lines and will not import; `unidiff`/`patch-ng` cover the parse/apply halves. What remains is the *measurement* (see `DECISION.md`, Track C).

## 4. X-Scraper — `Alex-lop/X-Scraper`

**What it does.** Human-approved bounded capture of X (Playwright against a *saved logged-in session*) → durable SQLite snapshots with provenance → diff/search/export → read-only MCP tools → Flask loopback API → Textual TUI. `RECOVERY_POSTMORTEM.md` documents the author falsifying his own benchmark claim and forbidding multi-account "rescue".

**Decisive constraint.** Capture requires a logged-in session and X's terms prohibit scraping; the repo's own `docs/responsible-use.md` says so. **Under the brief's ethics rules the X product cannot be sold.** Live X capture has, in any case, never been run.

**Reusable (high) — the four ideas trapped inside a product that can't ship.** (1) `jobs.py` + queue half of `storage.py` — durable single-process SQLite job queue (idempotent admission, priority + FIFO + source-fair round-robin, leases, retries, resource probe). (2) `mcp_server.py` `_ReadOnlyStorage` — bounded read-only MCP server over a local SQLite file (`mode=ro` + `PRAGMA query_only`, allowlists, question-shaped tools). (3) `read_service.compare_snapshots` + FTS5 evidence search — snapshot-and-diff-with-citations engine. (4) `api.py` preview → canonical manifest → signed digest → exact-match confirm — a human-in-the-loop **agent action approval protocol** with a priced cost preview. Tax on all of them: `storage.py` is 3,064 lines in one class.

**Quality.** 238 tests, ruff clean, real Chromium integration, real MCP SDK. Well-engineered offline; unproven where it matters.

**License / collaborators.** MIT, solo. Fork `Scweet` (upstream lib) is not Alex's.

**Commercial angles.** (1) "Safe agent reads over your own data" — read-only MCP gateway over a customer's SQLite/DuckDB (8–12 days). (2) Durable embedded job queue library for Python (10–15 days). (3) "What changed on this page" monitoring for *authorized* targets (20–30 days). (4) Agent action-approval protocol as a small library for agents that spend money. (5) Paid "evidence audit" of AI-built codebases (the postmortem is the credential).

## 5. graphene-site, Alex_Lopez_Website, and the placeholders

- **graphene-site** — 1.9K LOC, zero dependencies, live at `https://alex-lop.github.io/graphene-site/`, no custom domain, **no LICENSE** (the site advertises an Apache-2.0 product while being all-rights-reserved). Two headless invariant suites pass, including *negative* assertions ("mission narrative must not autoplay"). The home copy at `~/graphene-site` uniquely holds two deleted-but-tracked scripts: `scripts/refresh.py` (192 LOC) regenerates only marker-delimited regions of `index.html` from a pinned product checkout, binding every proof-table claim to a JSON path in `contracts/product_proof.json`; `plan_digest.py` (72 LOC). **"A marketing page that cannot outrun its evidence" is the one differentiated idea here** (agent estimate 8–12 days to a GitHub Action + hosted check).
- **Alex_Lopez_Website** — live on Pages, MIT, red test suite, loads Three.js from jsDelivr at runtime (vendor it).
- **AC-Washing-Well** — `main` is empty, but branch `commit-changes` holds 51 blobs: **Northeastern CS2800 coursework solutions and ~2.7 MB of IMC Prosperity CSVs pushed to a public repo.** Delete the branch (ASK-003).
- **AgenticCinemaFramework** (research memo; documents a hackathon whose rules restrict AI-model usage to Google Cloud + one partner), **The-Greater-Stake** (an anti-online-betting pitch, no code), **AXFold** (LICENSE only), **Alex-lop** (profile README).

## 6. Desktop Graphene variants (read-only glance)

`GrapheneFinalRelease-20260828` — `diff -rq` against the GitHub clone's `backend/` returns **zero differences** (de-git'd snapshot). `graphene-lanes` (714 MB, four experiment lanes, Aug 25) and the five `graphene-nightwatch*` trees (Aug 24; `-b`, `-c`, `-d` are byte-identical copies of the same commit) are older, superseded lanes. `AllThingsAgenticHackathon` (1.1 GB, branch `codex/runtime-recovery-20260827-verified`) is ~17 h older than `main` but holds **14 untracked files** (`HANDOFF.md`, `ULTRA_AUDIT_REPORT.md`, `GRAPHENE_META_PROMPT_*.md`, `evidence/ultra-check/`) — the only genuinely unsaved content; preserve those before deleting anything. ~2.8 GB of the Desktop is redundant copies.

## 7. Graft (fork) — competitor intelligence, not an asset

Unmodified fork (`ahead_by: 0`, 63 behind) of `trailhq/Graft` — 5,115 stars, 9,305 npm downloads/week, 836/836 tests pass, two Nanonets employees shipping 25–30 commits/day; `latest` on npm currently uninstallable; MIT. It does: cross-language symbol/edge extraction (7 full-fidelity + WASM tree-sitter breadth tier), graph.json with a four-level edge-confidence ladder, personalized-PageRank retrieval, six MCP tools, a diff→blast-radius engine, nine-agent instruction-file integration, local viewer. It does **not** do: ownership/review routing, architectural guardrails, history×structure coupling, team-shared hosted index, policy enforcement. **Do not fork it; depend on it** (pin the version). Its founders state on the record that agents ignore MCP tools and hooks are the only reliable surface — relevant to any "MCP server" plan.

## 8. Provenance error — two repos belonging to someone else

Two of the repos cloned into `assets/` in Phase 0 are not the principal's: they belong to **a different person, whose GitHub account was the active `gh` login on this machine**. The GitHub API and the commit metadata both confirm a different owner (checked 2026-08-30). Consequences: (a) both repos were removed from `assets/`; (b) no GitHub write action (PRs, issues, comments) could happen from this machine until the `gh` login was redone as `Alex-lop` — **done and verified 2026-08-30** (`gh api user` → `Alex-lop`), so ASK-001 is resolved; (c) **a secret is committed in plaintext in that account's public repository** — only the account owner can rotate it and purge the history, so it stays an ASK (ASK-002). Every specific — the account, the person, the school, the repository names and the leaked-file list — is in `private/THIRD-PARTY.md` and in no tracked file.

## 9. Repo hygiene to fix before anything is shown to a customer

1. Fill the `Copyright [yyyy] [name]` line in `LICENSE` for Graphene, RegLineage, Nemisis. Add a LICENSE to graphene-site.
2. Fix the `python:3.13-slim` / `procps` deployment defect in Graphene (0.5 day) — or stop shipping Dockerfiles that can't run.
3. Delete `AC-Washing-Well@commit-changes` (coursework + competition data on a public repo).
4. Confirm the stray scaffold commit by another GitHub account in RegLineage and the absence of hackathon/sponsor IP terms for Graphene, RegLineage, Nemisis.
5. Preserve the 14 untracked files in `~/Desktop/AllThingsAgenticHackathon`, then reclaim ~2.8 GB of duplicate trees.
6. Rewrite top-of-funnel prose (Graphene README/site) for a customer, not a judge. Keep the rigor; lose the epistemology lecture.

## 10. What the inventory says, in one paragraph

Everything Alex has built in the last seven weeks is the same idea from four angles: **make an AI agent's actions provable, bounded, and revocable** — a fenced workspace and provable candidate commit (Graphene), a differential proof that a patch does what it claims (Nemisis), a hash-bound revocable data lease and an egress firewall (RegLineage), and a preview→digest→confirm approval protocol with a read-only MCP boundary (X-Scraper). The engines around those ideas are demo-ware; the *seatbelts* are real and tested; per the readers, Graphene's fenced-workspace/capsule combination has no exact open-source equivalent, while Nemisis's differential idea does (SWE-bench's harness grades FAIL_TO_PASS/PASS_TO_PASS by construction; `jittest` on PyPI is the same product with zero adoption) — see the C-track deep-dive. There is **no** working PDF/document-extraction pipeline, **no** crawler beyond a login-gated Playwright harness, and **no** deployed cloud service anywhere. Fit scores in `ideas/` are set accordingly.
