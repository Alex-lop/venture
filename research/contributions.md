# research/contributions.md — Contribution targets for packages 4 and 5, verified 2026-08-30/31 — `contribution-scout`

**INSTRUMENT-BIASED (≈97% of citations are GitHub: `api.github.com`, `raw.githubusercontent.com`; 1 of ~34 sources is `pypi.org`).** Per CLAUDE.md §8 every conclusion here is held one level lower than stated. Mitigating note, not an excuse: the claims in this file are *about GitHub repositories* — their archive status, their CONTRIBUTING text, their merge history — so GitHub is the primary source rather than a proxy for one. The bias that remains is real: I cannot see maintainer intent expressed on Discord, in meetings, or in email, and two verdicts below turn on maintainer intent.

All `gh api` calls made as `Alex-lop`, read-only (GET), 2026-08-30/31 UTC. Individuals are described by role per CLAUDE.md §2; org and repo names are used as-is.

---

## 0. Headline: adoption.md's package-4 target does not exist

`research/adoption.md:230` puts **`modelcontextprotocol/servers` (`src/sqlite`)** in the DOMINANT row and derives the whole "contribute" verdict from it. Verified today:

```
gh api repos/modelcontextprotocol/servers/contents/src --jq '.[].name'
 -> everything fetch filesystem git memory sequentialthinking time      # no sqlite
gh api repos/modelcontextprotocol/servers-archived --jq '.archived, .pushed_at'
 -> true, 2025-05-28T17:57:12Z
gh api repos/modelcontextprotocol/servers-archived/contents/src --jq '.[].name'
 -> ... postgres redis sentry slack sqlite
```

A repo MEMBER closed the SQLite read-only request (`servers#1945`, `state_reason: not_planned`, 2025-05-29): *"This server has been moved to the archived repository at https://github.com/modelcontextprotocol/servers-archived to reduce maintenance overhead… no longer actively maintained."* PyPI confirms the package is frozen: `curl -s https://pypi.org/pypi/mcp-server-sqlite/json` → version `2025.4.25`, last upload `2025-04-25T08:27:29`, 16 months stale.

**So adoption.md's own table contained the same artifact in two rows with opposite classes** — `src/sqlite` as DOMINANT and `servers-archived` as "abandoned (ARCHIVED)". Under adoption.md's rule #1 (`archived == true` → abandoned, evaluated first), the SQLite server is **abandoned**. The 60,015 downloads/month are real, and they are downloads of a dead package. `modelcontextprotocol/servers` is still dominant as a *repo*; it is no longer an incumbent in the *category* `readonly-gateway` competes in.

---

## 1. `modelcontextprotocol/servers` — status, policy, merge behaviour

**Status:** active. `archived:false`, 89,978★, 11,539 forks, `pushed_at 2026-08-30T21:43:38Z`, 512 open issues, license NOASSERTION (`gh api repos/modelcontextprotocol/servers`).

**Policy** (`CONTRIBUTING.md`, fetched today). Accepts: bug fixes; usability improvements; enhancements that demonstrate under-used MCP protocol features (Resources, Prompts, Roots). *"We're more selective about: **Other new features** — especially if they're not crucial to the server's core purpose or are highly opinionated."* Does not accept new server implementations. The in-repo `CLAUDE.md:82` **paraphrases rather than quotes** it — *"**Selective:** New features outside a server's core purpose or highly opinionated additions."* (`curl -sL raw.githubusercontent.com/modelcontextprotocol/servers/main/CLAUDE.md`, 2026-08-31). **No AI-contribution or generated-code policy exists** in `CONTRIBUTING.md`, in-repo `CLAUDE.md`, the PR template, or the org-level `modelcontextprotocol/.github/CONTRIBUTING.md` — so no disclosure line is *required*; there is a `claude-review` label in use. **No CODEOWNERS** at `/`, `/.github`, or `/docs` (all 404). `SECURITY.md`: *"This repository is **not** eligible for security vulnerability reporting"* — reference implementations, not production software. That single line reprices any "hardening" pitch here.

**PR template** requires: server named, motivation, "How Has This Been Tested?" (with an LLM client), breaking-change note, README updated, tests pass.

**Labels/triage:** per-server labels (`server-filesystem`, `server-git`, …), plus `bug enhancement documentation duplicate "good first issue" "help wanted" "waiting for submitter" waiting-on-sdk wontfix v2`. `good first issue` currently has **zero** open issues; `help wanted` also returns none — the triage vocabulary exists but is not being used to recruit.

**Last 20 merged external PRs** (`state=closed`, filtered `merged_at != null`, `author_association ∈ {NONE, CONTRIBUTOR, FIRST_TIME_CONTRIBUTOR}`, bots removed): **median time-to-merge 17.16 days** (min 0.62 d, max 431.38 d). Shape is unmistakable — **14 of 20** are titled `fix(<server>): <one specific bug>`, and **9 of those are `fix(filesystem)`** (counted off the same 20-PR set that produces the median above). Measured diffs of the nine most recent: 2–3 files, **+13/-0 to +157/-1** — additions span 13–157, deletions never exceed 27 (`gh api repos/modelcontextprotocol/servers/pulls/<n> --jq '{changed_files,additions,deletions}'`, 2026-08-31). Examples: `#4704 fix(filesystem): reject Windows paths on POSIX` (2.70 d, +13/-0); `#4642 fix(memory): write the knowledge graph atomically` (13.55 d, +157/-1); `#4630 fix(filesystem): make move_file fail instead of silently overwriting` (17.23 d, +45/-1).

### 1a. The gap in the surviving reference server (filesystem)

`src/filesystem/index.ts` (786 lines, fetched today from `raw.githubusercontent.com/modelcontextprotocol/servers/main/`):
- **line 33** — `const args = process.argv.slice(2);` is parsed *only* as a list of allowed directories. There is no `--read-only` flag and no env var.
- **lines 358, 384, 413, 616** — `write_file`, `edit_file`, `create_directory`, `move_file` are registered **unconditionally**: no flag, no env var, no branch gates any of them. All four are annotated `readOnlyHint: false`; **three of the four are `destructiveHint: true`** (`:371`, `:401`, `:630`) and **`create_directory` (`:426`) is `destructiveHint: false`**. Unconditional registration, not the hint values, is the load-bearing fact here.
- The only read-only concept in the server is the `readOnlyHint` **annotation** (lines 221, 244, 278, …), which is advisory metadata a client may ignore. Nothing enforces it.

Two open issues name this: `servers#1160` "Support read-only paths in filesystem MCP with npx" (open since 2025-03-31, **0 comments in 17 months**) and `servers#3505` — which is an **open PR**, not an issue: `--read-only` flag + `mode-utils.ts` + 261 lines of enforcement tests, 6 files, **+598/-125**, opened **2026-03-09**, `merged:false`, `review_comments: 0`, **175 days with no maintainer review of any kind** (its only comment is an unsolicited third-party review that ends in a crypto wallet address).

### 1b. Where read-only hardening could otherwise land

- **`modelcontextprotocol/servers-archived`** — archived; PRs cannot be opened. Dead end.
- **`modelcontextprotocol/registry`** (7,203★, pushed 2026-08-26) and **`modelcontextprotocol/modelcontextprotocol`** (9,085★, pushed 2026-08-30) are alive, and `CONTRIBUTING.md` explicitly routes new servers to the registry. A *published server* in the registry is distribution without a merge queue — this is the escape hatch for a standalone package, not a contribution target.
- **`crystaldba/postgres-mcp`** — 3,241★, pushed 2026-08-17, 89 open issues; 59 merged external PRs, last-20 median **0.77 d**, but the newest merge is 2026-08-16 and adoption.md measured **1 commit in 90 days**. Fast historically, quiet now. Wrong engine (Postgres) anyway.
- `ktanaka101/mcp-server-duckdb` (178★, pushed **2025-05-05**) and `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` (107★, pushed **2025-07-18**) re-verified today: still abandoned, 13–16 months.

---

## 2. `motherduckdb/mcp-server-motherduck` — the live target

**Status:** active, company-backed. `archived:false`, 513★, 86 forks, `pushed_at 2026-08-19T17:04:10Z`, **6 open issues** (only 2 are non-PR issues) — a maintainer keeping the queue empty. MIT.

**Policy:** **no CONTRIBUTING.md, no PR template, no CODEOWNERS, no AI policy** (all six paths 404 via `gh api .../contents/`). Nothing to disclose against; the disclosure line is therefore a courtesy, not a requirement — see §5.

**Last 14 merged external PRs** (the full external history): **median 5.31 d**, min 0.03 d, max 47.45 d. The decisive precedent: **`#20 "Add read-only mode support for DuckDB connections"` — an external contributor, merged in 18.57 days.** Also `#83 "fix: redact motherduck_token from switch_database_connection response"` (8.32 d) — a security fix from outside, merged in a week.

### The exact gap, in the target's own words

`README.md` §"Securing for Production", fetched today:

> *"When giving third parties access to a self-hosted MCP server, **read-only mode alone is not sufficient** — it still allows access to the local filesystem, changing DuckDB settings, and other potentially sensitive operations."*
> *"**Self-hosting DuckDB MCP:** Use `--init-sql` to apply security settings. See the [Securing DuckDB guide]…"*

The code confirms it. `src/mcp_server_motherduck/database.py`:
- **five `duckdb.connect` sites, not four.** `:104-107`, `:214-217`, `:318-321`, `:433-436` pass `read_only=<flag>`, which is the only read-only enforcement anywhere in the file. The fifth, **`:128` — `duckdb.connect(":memory:")` — passes no `read_only` argument at all**, so it is read-write unconditionally. That omission strengthens the argument below rather than weakening it.
- `:212` — `read_only_flag = self._read_only if self.db_type == "motherduck" else False`; for the **default** `--db-path :memory:` the flag is `False`.
- `src/.../tools/execute_query.py:21` is the whole tool: `return db_client.query(sql)`. Arbitrary SQL, no statement inspection, no allowlist.

DuckDB's `read_only=True` stops writes *to the attached database*. It does not stop `COPY (SELECT …) TO '/tmp/x'`, `read_csv('/etc/passwd')`, `INSTALL`/`LOAD`, or `SET`. Proof that the fix is absent: `search/code?q=repo:motherduckdb/mcp-server-motherduck+<term>` returns **`total_count: 0`** for all four of `enable_external_access`, `disabled_filesystems`, `lock_configuration`, `allow_community_extensions`.

### Contribution design — `--secure` preset (22 lines)

```
Files touched (4):
  src/mcp_server_motherduck/database.py   +~35   apply hardening pragmas after connect
  src/mcp_server_motherduck/configs.py    +~4    SECURE_SETTINGS tuple (data, not code)
  src/mcp_server_motherduck/__init__.py   +~8    --secure CLI flag, env MOTHERDUCK_SECURE
  tests/test_secure_mode.py               +~120  new
  README.md                               +~12   fold into "Securing for Production"
API surface: one flag, --secure (default OFF). Applies, in one transaction, the
  settings the README already tells users to apply by hand via --init-sql:
    SET enable_external_access=false; SET allow_community_extensions=false;
    SET disabled_filesystems='LocalFileSystem'; SET lock_configuration=true;
  Order matters: lock_configuration LAST, else the rest can be unset.
  Runs after --init-sql so an operator's own settings still apply.
Tests (the point of the PR — this is the X-Scraper _ReadOnlyStorage test set
  translated from SQLite to DuckDB): each asserts a DuckDBError, not a silent pass —
  COPY (SELECT 1) TO '<tmp>'; read_csv('<tmp>'); INSTALL/LOAD a community extension;
  ATTACH '<other.duckdb>' AS x; SET enable_external_access=true (re-enable attempt);
  plus one positive test that ordinary SELECT/DESCRIBE still work.
Backward compatibility: total. Flag defaults OFF; no existing path changes; no
  new dependency (all four are stock DuckDB settings).
AI disclosure: not required (no policy exists). Include anyway, one line in the PR
  body: "Drafted with AI assistance; every line manually reviewed and tested by me."
  Cost is zero and it matches the norm the adjacent ecosystem (gittuf) now enforces.
```

**Effort:** **3 agent-days** (1 to reproduce each escape against a scratch `.duckdb` and pin exact DuckDB error types, 1 to write, 1 for CI/`pre-commit`/review turns). **Principal-hours: ~1.5** — one 20-min read of the diff before it opens, then ~2 review replies at the observed 5.31 d median.

**Rejection risk: MEDIUM (~35%).** Evidence for: the README states the gap itself, so the PR closes a documented hole rather than proposing a new idea; `#20` proves a read-only-mode PR from outside merges; `#83` proves security fixes merge in ~8 days; only 2 open non-PR issues means someone is actually reading. Evidence against, and it is specific: the same README section answers this exact problem with *"we recommend **MotherDuck Remote MCP** — hosted by MotherDuck"* and *"Fork this repo and customize."* A flag that makes self-hosting safe removes a reason to buy the hosted product. Expect the counter-offer "put it in `--init-sql` docs instead"; the pre-agreed fallback is to accept a docs-only merge and keep the test file, which is the durable half.

---

## 3. Package 5 targets — measured, then repriced

| Target | Status today | Merged external PRs (sampling window — see Method notes) | Median time-to-merge | AI policy |
|---|---|---|---|---|
| `in-toto/attestation` | active, 369★, pushed 2026-08-24, 72 open issues | 45 | **11.42 d** | none; **DCO sign-off required** (in-toto/community CONTRIBUTING) |
| `gittuf/gittuf` | active, 655★, pushed 2026-08-26, 103 open issues | **115 since 2026-06-09** | **7.89 d** | **explicit, permissive, enforced by PR template** |
| `slsa-framework/slsa` | active, 1,920★, pushed 2026-08-29 | 13 in the page-1 sample; **118 at 3 pages** (90 excl. `renovate-bot`) | 2.62 d (page-1) / **2.64 d** over all 118 | none found |
| `sigstore/gitsign` | active, 1,121★, pushed 2026-08-24 | 6 in the page-1 sample; **12 at 3 pages**, back to 2024-06-28 | 31.79 d (page-1) / **4.62 d** over all 12 | none found |
| `actions/attest-build-provenance` | active, 1,027★, pushed 2026-08-21, 10 open issues | 4 in the page-1 sample; **13 = complete history** (399 closed PRs, exhausted) | 0.39 d (page-1) / **0.63 d** over all 13 | none found |

**Those population figures are sample sizes, not histories.** 13, 6 and 4 are the yield of the *first page of closed PRs sorted by `updated` desc* — a sampling window, and specifically not a date range: because it orders by **update** time, a five-year-old PR with one recent comment lands inside it while a quiet recent one falls outside. Re-running the same script at more pages on 2026-08-31:

```
prs.sh slsa-framework/slsa 3        -> merged seen=242  external=118  (90 excluding renovate-bot)
                                       median over all 118: 2.64 d;  oldest external merge 2021-09-16
prs.sh sigstore/gitsign 3           -> external=12,  median 4.62 d,   oldest external merge 2024-06-28
prs.sh actions/attest-build-provenance 4  -> external=13, median 0.63 d, back to 2024-02-23
   (399 closed PRs total, so 4 pages IS the complete history for this repo)
prs.sh motherduckdb/mcp-server-motherduck 3 -> external=14, median 5.31 d
   (82 closed PRs total -> page 1 already exhausts it: 14 IS the entire external history here)
```

**So "tiny population" is false for `slsa`** — its real external population is an order of magnitude larger than the table's 13, and its speed is real — but the population is concentrated: **28 of the 118 are `renovate-bot` dependency bumps and 60 come from a single prolific external contributor**, leaving ~30 ordinary outside contributions across five years. `gitsign` doubles to 12 over 26 months and its median falls from 31.79 d (page-1 sample of 6) to 4.62 d. `attest-build-provenance` triples to 13. Only the `motherduck` figure was what the method note claimed it was.

**The "closed to substance" verdict therefore does not rest on population size — it rests on the governance path, which is verified.** SLSA's `CONTRIBUTING.md` routes a change through: *"The proposer finds or creates a GitHub Issue"* → *"The community discusses and refines the idea, **guided by the steering committee**"* → if needed a *"proposal document"* in `slsa-framework/slsa-proposals` → *"Once there is general agreement that the proposal is sound, the proposer submits a pull request implementing the idea."* Issue, then committee, then proposal doc, then PR. That is a governance path, not a Wave-2 artifact — and it is what makes the fast median unreachable for anything of substance.

### 3a. `in-toto/attestation` — the predicate process, and why the queue is the finding

Process, from `docs/new_predicate_guidelines.md` (fetched today): **PR-first, not issue-first.** Open a PR following the `spec/predicates/template/` and ITE-9 formatting; add the predicate to `spec/predicates/README.md`; include a **protobuf definition** so Go/Python/Java/Rust bindings generate; *"maintainers will review the PR at the next maintainers meeting"*; if the `predicateType` URI lives under `in-toto.io`, a second PR to `in-toto/in-toto.io`. Preliminary questions the PR must answer include, verbatim: *"**Why don't existing predicates cover this use case?**"*

Two existing predicates make that question hard for "workspace evidence". `spec/predicates/runtime-trace.md` (v0.1) already exists and is deliberately generic — *"can be used to express a runtime trace of any operation… from an operation spawned by a user using a CLI command"*, and explicitly *"can prove the build was executed in a hermetic environment with no network access."* `scai.md` covers evidence-based assertions about supply-chain attributes. The Graphene workspace-evidence idea (`workspace_audit.py:368 audit_workspace` — base SHA + per-path old/new mode and full-content SHA-256, rejected if `changed_paths ⊄ allowed`, digested into one `patch_sha256`) is a *narrower, sharper* instance of runtime-trace, and a maintainer can reasonably say so.

**The queue is the decisive evidence.** `gh api "repos/in-toto/attestation/pulls?state=open&per_page=50"` — 13 open PRs, **12 from non-members**, of which at least seven are agent/AI predicate proposals: `#591 Add AI Agent Decision predicate` (2026-08-29), `#588 Add AI Agent Action predicate type (v0.1)` (2026-08-19, +1464/-0 over 2 files, **six rounds of third-party comment and no maintainer review** — `review_comments: 0`, `comments: 6`, and its single submitted review is `author_association: NONE`), `#587 PRML`, `#575 eval-result`, `#570 Adversarial Execution Evidence`, `#552 agent-threat-scan`, `#581 source-review-coverage`. Older still: `#502 Define initial baseline predicate` open since **2025-11-20** (9.3 months, 32 review comments — 17 of them MEMBER), `#496 Add Tool Assessment Predicate Type` open since **2025-10-08** (10.7 months, 42 review comments — 18 MEMBER, a "Bumping request for review" in month 2).

**What the maintainers are and are not reading.** The correct claim is narrower than an earlier draft of this file made it, and it matters. Across the **nine 2026 predicate PRs** — `#552 #570 #575 #581 #582 #587 #588 #590 #591` — every comment and every submitted review carries `author_association: NONE`: **zero maintainer comments, zero maintainer reviews, on any of the nine.** Non-members are reviewing each other's predicates. But the two **oldest** predicate PRs are the opposite case and must not be lumped in with them: **`#502` carries 17 MEMBER review comments and 7 MEMBER reviews; `#496` carries 18 MEMBER review comments and 2 MEMBER reviews** — heavy maintainer engagement — and both are *still open*, 9.3 and 10.7 months after opening, last updated 2026-04-07 and 2026-02-25.

```
gh api repos/in-toto/attestation/pulls/{502,496}/comments  --jq '[.[].author_association]|group_by(.)|map({(.[0]):length})|add'
 -> #502 {"MEMBER":17,"NONE":15}          #496 {"CONTRIBUTOR":14,"MEMBER":18,"NONE":10}
gh api repos/in-toto/attestation/pulls/{502,496}/reviews   --jq '...'
 -> #502 {"MEMBER":7,"NONE":12}           #496 {"CONTRIBUTOR":1,"MEMBER":2,"NONE":10}
gh api repos/in-toto/attestation/pulls/<n>/{comments,reviews}, issues/<n>/comments   for n in 552 570 575 581 582 587 588 590 591
 -> every non-empty result: ["NONE"]. No MEMBER anywhere.        (all re-run 2026-08-31)
```

So the finding is **slow, then silent — not absent.** Maintainers do review outside predicate PRs, on a cadence of months, and have not yet touched anything from the 2026 cohort. That is the premise the package-5 verdict rests on; the "zero maintainer response rate" premise is struck. One contributor has an open PR (`#582`, 2026-07-31) whose entire purpose is *"point the vetting process at a meeting a contributor can find"* — the meeting the guidelines route every predicate through is not findable from the repo. Merged predicates, for scale: `#508 Add SPDX 3 Predicate` **50.86 d**, `#470 Create a simple verification attestation` **185.98 d**.

### 3b. `gittuf/gittuf` — warmest maintainer, confirmed, with a caveat that changes the plan

adoption.md called gittuf the warmest maintainer. That reproduces and then some: **115 merged external PRs between 2026-06-09 and 2026-08-26** (≈11 weeks), last-20 **median 7.89 d**, max 24.03 d — no long tail at all, which none of the other four targets can say.

It is also the only target with a written AI policy, and it is permissive. `CONTRIBUTING.md` §"AI-based Contributions Policy": *"AI-based contributions to gittuf are allowed, but must be of good quality… **All** content submitted to gittuf is manually reviewed by the contributor… The contributor fully understands the content they are submitting… Low-quality contributions or outright 'AI slop'… will be closed without further review."* `.github/pull_request_template.md` makes it a checkbox with a free-text box:

> `- [ ] I **did** use generative AI in some form in making the content of this pull request. I have described my use of AI below.`

Plus DCO sign-off on every commit, tests required, and CoC agreement.

**The caveat.** A new attestation type is a change to the design document, which `CONTRIBUTING.md` routes through a **GAP**. `docs/gaps/README.md` lists GAPs 1–6, and **every one is `Implemented: No`** — including `GAP 3 Authentication Evidence Attestations` and `GAP 6 Code Review Tool Attestations`, the two nearest neighbours of workspace evidence. The 7.89-day median belongs to code and test PRs (`test: add SSH signer/verifier error-path coverage`, `rsl, tuf: stricter validation for entry and metadata fields`, `pkg/gitinterface: remove os.Chdir`), not to design proposals. gittuf's existing surface is `internal/attestations/authorizations/v02/v02.go:19` — `PredicateType = "https://gittuf.dev/reference-authorization/v0.2"`, whose predicate is three fields (`targetRef`, `fromID`, `targetID`). It records *that a change was authorized*, never *what the author could touch*. The gap is real; the fast lane does not lead to it.

### Contribution design — package 5, staged (19 lines)

```
Stage A (do this, or nothing):  one in-scope gittuf code PR, ~2 agent-days.
  Files: internal/attestations/authorizations/v02/*_test.go or pkg/gitinterface/*
  Pick from the shape that actually merges: error-path test coverage or a fuzz
  target (precedents #1555, #1513, #1526 — **0.68 to 1.59 d each**: 0.74 / 1.59 / 0.68 d;
  the 0.30 d figure quoted earlier was the last-20 minimum across all gittuf external PRs).
  Purpose is standing, not the idea. Costs 2 days, buys a maintainer who knows the name.
  Disclosure: tick the "I did use generative AI" box; one sentence describing how.
  DCO: every commit signed off (`git commit -s`). Tests mandatory.
Stage B (only if Stage A merges):  GAP draft for workspace-evidence attestation.
  Files: docs/gaps/7/README.md (follow docs/gaps/template.md; needs a sponsor)
  Content: the audit_workspace model — baseline (base_sha + git-admin digest),
  per-path {status, old/new mode, old/new sha256}, allowlist containment as a
  verification rule, one canonical patch_sha256. Reference verifier in Go.
  Backward compatibility: additive; no existing predicate or ref changes.
NOT recommended: an in-toto/attestation predicate PR as the first move. It joins a
  queue of 7+ agent predicates that no maintainer has commented on or reviewed yet
  (all nine 2026 predicate PRs: zero MEMBER comments, zero MEMBER reviews), queued
  behind two 2025 predicates that DID get heavy maintainer review and are still open
  at 9.3 and 10.7 months, and it must first answer "why doesn't runtime-trace cover
  this?". The block is maintainer bandwidth measured in quarters, not indifference.
```

**Effort:** Stage A **2 agent-days**, ~0.5 principal-hours. Stage B **6–9 agent-days** for the GAP alone (spec + reference verifier + prior-art section against `runtime-trace`, `scai`, GAP 3 and GAP 6), **principal-hours unbounded** — GAP review is a discussion over months, and 0 of 6 GAPs have shipped. The in-toto predicate path, if ever taken, is **8–12 agent-days** (spec + protobuf + bindings + two PRs) against a 50–186 day merge history.

**Rejection risk:** Stage A **LOW (~15%)** — 115 merged external PRs in 11 weeks, and the AI policy names the acceptance condition explicitly. Stage B **HIGH (~70%)** on the operative meaning of "accepted" — not that a GAP is refused, but that the observed outcome for all six existing GAPs is *merged as a document, implemented never*. The in-toto path is **HIGH (~75%)**, and the reason is **latency, not silence**: the stated scope question has a ready answer that is not ours (`runtime-trace` v0.1); no maintainer has commented on or reviewed any of the nine 2026 predicate PRs; the two 2025 predicates that *were* reviewed heavily are still open at 9.3 and 10.7 months; and merged predicates took **50.86 d** and **185.98 d**. Every one of those clocks is longer than Wave 2.

---

## 4. Recommendation

**First: `motherduckdb/mcp-server-motherduck`, the `--secure` PR.** 3 agent-days, ~1.5 principal-hours, 5.31 d median, an exact precedent (`#20`), a gap the target's own README states in the second person, and a test suite that is `_ReadOnlyStorage`'s escape list translated to DuckDB. It is the cheapest high-trust artifact available to Wave 2 and the only package-4 target where a maintainer is demonstrably reading.

**Do not open `#3505`'s PR again at `modelcontextprotocol/servers`.** A functionally identical `--read-only` flag PR (+598/-125, with 261 lines of enforcement tests) has sat 175 days with `review_comments: 0`. `CONTRIBUTING.md` files new flags under "more selective… highly opinionated", and `SECURITY.md` says the repo is *"not eligible for security vulnerability reporting"* because these are teaching examples. If that repo is wanted for its 89,978★ of distribution, the entry ticket is the shape that merges: one `fix(filesystem): …` PR, 2–3 files, +13 to +157 lines, against a real defect. That is a separate, cheap errand (~1 agent-day) — not the readonly-gateway artifact.

**Package 5: do not build it in Wave 2.** Spend 2 agent-days on the gittuf Stage-A PR to buy standing, and stop. adoption.md's kill of a *competing receipt format* stands (`slsa` and `gitsign` both clear the dominant rule and were re-verified active today). What this file adds is that the *contribution* substitute is also unaffordable on Wave-2's clock: the in-toto queue is 7+ agent predicates deep with zero maintainer comments or reviews on any of the nine 2026 ones, the two 2025 predicates that *did* draw heavy maintainer review are still open at 9.3 and 10.7 months, merged predicates take 50–186 days, and gittuf's design-change path has produced six documents and zero implementations. Deferring costs nothing, because §5's release order already frees these two builds.

**Should either stay a standalone package?** Applying adoption.md's own rule, top-down, first match wins:

- **Package 4 — yes, the SQLite half re-opens.** The row that produced its "contribute" verdict is `archived == true` → **abandoned** under rule #1, which is evaluated before adoption precisely so that download counts cannot rescue a dead repo. Re-classifying the package-4 table with `src/sqlite` removed leaves: `motherduck` active-small, `postgres-mcp` active-small, four abandoned, one zero-adoption — **no dominant incumbent**, so under CLAUDE.md §8 the category is open, and the dossier must say on which axis. It is open on a **gap**: no maintained SQLite MCP server enforces read-only at the statement level, and the one that advertised the exact shape (107★, "safe, read-only access to SQLite") has been dead 13 months. Two cautions kept in front: four abandoned servers in this category is also evidence that people build these and stop, and the merged `--secure` PR is worth more than the package would be. So the sequence is **PR first, package only if the PR lands** — the merged PR becomes the README's first line and the registry listing (`modelcontextprotocol/registry`, 7,203★, is the distribution channel `CONTRIBUTING.md` itself points new servers at), which is the distribution the standalone package was always missing.
- **Package 5 — no.** Two dominant, maintained standards (`slsa`, `gitsign`) plus `securesystemslib` at ~1M downloads/month kill a competing format under rule #4, and nothing measured today moves any of them. It is neither a package nor, on this timeline, a PR.

**Open items I could not settle.** (a) Whether the motherduck maintainer treats `--secure` as competing with the hosted product — that is maintainer intent, and my instrument cannot see it; the 35% risk figure is a judgement, marked **UNVERIFIED**. (b) Whether in-toto's maintainers meeting is active — `#582` says a contributor could not find it from the repo, and I did not fetch a non-GitHub meeting calendar. **UNVERIFIED.** (c) Whether `runtime-trace` v0.1 has any producer implementation; if it has none, the overlap objection is weaker than I priced it. **UNVERIFIED.**

---

## Instrument log

**Reachable today (2026-08-30/31 UTC), all read-only GET:**

| Venue / API | Method | Result |
|---|---|---|
| `api.github.com` repos / contents / issues / pulls / labels | `gh api` as `Alex-lop` | **reachable** — ~90 calls, core limit 5,000/hr, never below 4,900 remaining |
| `api.github.com` `search/issues` | `gh api` | **reachable** — 2 queries, no secondary rate limit hit (adoption.md hit one at ~37 calls; I stayed well under) |
| `api.github.com` `search/code` | `gh api` | **reachable but tiny budget** — limit **10/min**; 7 queries used at 3s spacing |
| `api.github.com` `search/repositories` | `gh api` | **reachable, low value** — 1 query; `sort=updated` returns near-pure noise (20 results, 18 irrelevant), reproducing Session 1's "GitHub search ignores phrase quoting" finding |
| `raw.githubusercontent.com` | `curl -sL` | **reachable** — 5 files (in-toto/community CONTRIBUTING, slsa CONTRIBUTING, gittuf SECURITY + v02.go + gaps README, MCP org CONTRIBUTING, filesystem index.ts) |
| `pypi.org/pypi/<pkg>/json` | `curl -s` | **reachable** — 1 package (`mcp-server-sqlite`), no rate limiting at this volume |

**Not tried, and it matters:** in-toto and MCP maintainer meetings, Discords, mailing lists, CNCF/OpenSSF slack. Two of this file's three UNVERIFIED items live there. Verdicts about *maintainer intent* (motherduck's hosted-product conflict; in-toto's meeting cadence) are the weakest claims here and are labeled as such rather than smoothed over.

**Citation count by venue:** GitHub (`api.github.com` + `raw.githubusercontent.com`) ≈33 of ≈34; PyPI 1. **≈97% — far over CLAUDE.md §8's 70% threshold.** File is labeled instrument-biased; every conclusion above is held one confidence level lower than written.

**Method notes.** "External" = `author_association ∈ {NONE, CONTRIBUTOR, FIRST_TIME_CONTRIBUTOR}` with `dependabot`/`*[bot]` authors removed; time-to-merge = `merged_at − created_at` (so it includes contributor turnaround, not just maintainer latency — the real number a contributor experiences). **Sampling — stated honestly.** `prs.sh` fetches `repos/<R>/pulls?state=closed&per_page=100&sort=updated&direction=desc` for N pages, so its population is *the N×100 most recently **updated** closed PRs*. That is a **sampling window, not a date range and not a history**: it is ordered by update time, so an old PR with a recent comment is inside it and a quiet recent PR is outside it, and the count moves between runs of the identical command. Populations here: last-20 for `servers`, `in-toto/attestation` and `gittuf`; page-1 yields of **14, 13, 6 and 4** for `motherduck`, `slsa`, `gitsign` and `attest-build-provenance`. Of those four, only **`motherduck`'s 14 is a complete external history** — that repo has 82 closed PRs total, so one page exhausts it (verified: `page=2 -> length 0`). The other three are samples; at 3–4 pages they return **118, 12 and 13**, and `attest-build-provenance`'s 13 is complete (399 closed PRs, pagination exhausted at page 4). A "median" over 4 or 6 PRs is reported because it is what the window held, not because it is stable — see §3, where two of those medians moved once the window widened. Script: `/private/tmp/claude-501/-Users-alexlopez-Desktop-money-maker/4c5de4fd-4aa2-42f0-93ec-addeeb47e2a6/scratchpad/prs.sh <owner/repo> <pages>`.

---

## Verification (2026-08-30, quote-verifier)

Adversarial re-verification of every claim above. Method: every `gh api` call re-run as `Alex-lop` (read-only GET), every `raw.githubusercontent.com` file re-fetched with `curl -sL`, every quote diffed against the fetched bytes, and the merged-PR statistics re-run with the scout's own script (`scratchpad/prs.sh`, still present and inspected — filter confirmed as documented: `merged_at != null`, `author_association ∈ {NONE, CONTRIBUTOR, FIRST_TIME_CONTRIBUTOR, FIRST_TIMER}`, `*[bot]`/`dependabot` removed, dedup by number, `merged_at − created_at`). Independent re-implementation used for cross-checks. 61 claims checked.

**Verdict: SOUND WITH ONE MATERIAL CORRECTION.** Every number in the file reproduces exactly — medians, mins, maxes, populations, star counts, dates, line numbers, diff sizes. Two claims do not survive: an in-toto maintainer-silence claim that is contradicted by 35 MEMBER review comments on the two PRs it names, and a method note that describes page-1 samples as entire merge histories. Nine smaller mismatches are listed. The **package-4 recommendation (motherduck `--secure` PR first) is unaffected and fully verified**; the **package-5 recommendation (gittuf Stage A only, defer the rest) survives**, but its stated *reason* for the in-toto path must be restated — see MF-1.

### Archived / active status (`gh api repos/O/R --jq .archived`) — 13/13 confirmed

| Repo | archived | ★ | pushed_at | open issues | Matches file |
|---|---|---|---|---|---|
| `modelcontextprotocol/servers` | false | 89,978 | 2026-08-30T21:43:38Z | 512 | ✅ exact |
| `modelcontextprotocol/servers-archived` | **true** | 295 | 2025-05-28T17:57:12Z | 0 | ✅ exact |
| `motherduckdb/mcp-server-motherduck` | false | 513 | 2026-08-19T17:04:10Z | 6 (2 non-PR) | ✅ exact |
| `in-toto/attestation` | false | 369 | 2026-08-24 | 72 | ✅ exact |
| `gittuf/gittuf` | false | 655 | 2026-08-26 | 103 | ✅ exact |
| `slsa-framework/slsa` | false | 1,920 | 2026-08-29 | 174 | ✅ exact |
| `sigstore/gitsign` | false | 1,121 | 2026-08-24 | 49 | ✅ exact |
| `actions/attest-build-provenance` | false | 1,027 | 2026-08-21 | 10 | ✅ exact |
| `modelcontextprotocol/registry` | false | 7,203 | 2026-08-26 | 157 | ✅ exact |
| `modelcontextprotocol/modelcontextprotocol` | false | 9,085 | 2026-08-30 | 137 | ✅ exact |
| `crystaldba/postgres-mcp` | false | 3,241 | 2026-08-17 | 89 | ✅ exact |
| `ktanaka101/mcp-server-duckdb` | false | 178 | **2025-05-05** | 6 | ✅ still dead |
| `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` | false | 107 | **2025-07-18** | 8 | ✅ still dead |

### Claims table

| # | Claim (§) | Re-verification | Verdict |
|---|---|---|---|
| 1 | `servers/contents/src` has no `sqlite` (§0) | `everything fetch filesystem git memory sequentialthinking time` | ✅ |
| 2 | `servers-archived/contents/src` has `sqlite` (§0) | present (13 dirs incl. postgres, redis, sentry, slack, sqlite) | ✅ |
| 3 | `servers#1945` closed `not_planned` by a MEMBER, 2025-05-29 (§0) | `closed / not_planned / 2025-05-29T16:22:40Z`; sole comment `author_association: MEMBER` | ✅ |
| 4 | The #1945 quote (§0) | Verbatim, but the `…` silently joins two paragraphs; "no longer actively maintained" is the opening of the second. Substance intact | ✅ (see m-2) |
| 5 | PyPI `mcp-server-sqlite` `2025.4.25`, upload `2025-04-25T08:27:29`, 16 months stale (§0) | wheel 08:27:27, sdist 08:27:29; version and staleness exact | ✅ |
| 6 | adoption.md:230 puts `src/sqlite` in DOMINANT; :136 puts `servers-archived` in abandoned; rule #1 (`archived==true`) at :44 evaluated first (§0) | All three lines read locally; contradiction is real and the re-classification follows | ✅ |
| 7 | `servers` CONTRIBUTING "more selective about… Other new features" quote (§1) | Verbatim except the file lowercases the source's "Especially" | ✅ (m-1) |
| 8 | "Does not accept new server implementations" (§1) | CONTRIBUTING:24 routes them to the registry | ✅ |
| 9 | "in-repo `CLAUDE.md` restates this **verbatim**" (§1) | CLAUDE.md:82 is a *paraphrase*: "**Selective:** New features outside a server's core purpose or highly opinionated additions." | ❌ **MF-6** |
| 10 | No AI policy in CONTRIBUTING / CLAUDE.md / PR template / org `.github` (§1) | Zero hits for AI/generative/LLM-generated in all four | ✅ |
| 11 | `claude-review` label in use (§1) | Present in the label list | ✅ |
| 12 | No CODEOWNERS at `/`, `/.github`, `/docs` (§1) | All three 404 | ✅ |
| 13 | SECURITY.md "not eligible for security vulnerability reporting" (§1) | Verbatim, SECURITY.md:11 | ✅ |
| 14 | PR template requires server, motivation, "How Has This Been Tested?" with an LLM client, breaking change, README, tests (§1) | All present | ✅ |
| 15 | Label vocabulary list (§1) | All named labels present | ✅ |
| 16 | `good first issue` = 0 open, `help wanted` = 0 open (§1) | `search/issues` → `total_count: 0` for both | ✅ |
| 17 | Last-20 merged external: median **17.16 d**, min 0.62, max 431.38 (§1) | Scout script, 3 pages: `median 17.16 d min 0.62 d max 431.38 d`, n=20 of 31 external | ✅ exact |
| 18 | "13 of 20 titled `fix(<server>):`, **11 of those** `fix(filesystem)`" (§1) | 14 match `^fix(<server>):`; only **9** are `fix(filesystem)` | ❌ **MF-4** |
| 19 | Nine most recent: 2–3 files, **+13/-0 to +161/-18** (§1) | Files 2–3 ✅. Observed additions 13…157, deletions 0…27. No PR is +161/-18 | ❌ **MF-5** |
| 20 | `#4704` 2.70 d +13/-0; `#4642` 13.55 d +157/-1; `#4630` 17.23 d +45/-1 (§1) | 2.70/+13/-0; 13.56/+157/-1; 17.23/+45/-1 | ✅ |
| 21 | `index.ts` is 786 lines; `:33` = `const args = process.argv.slice(2);` (§1a) | Exact | ✅ |
| 22 | No `--read-only` flag, no env var (§1a) | No `process.env` anywhere; argv parsed only into allowed dirs | ✅ |
| 23 | `:358 :384 :413 :616` register `write_file`, `edit_file`, `create_directory`, `move_file` unconditionally (§1a) | All four exact, all unconditional | ✅ |
| 24 | "each annotated `readOnlyHint: false, destructiveHint: true`" (§1a) | `:371` ✅ `:401` ✅ `:630` ✅; **`:426` (`create_directory`) is `destructiveHint: false`** | ❌ **MF-3** |
| 25 | `readOnlyHint` at :221 :244 :278 is advisory only (§1a) | Exact lines; nothing consumes them | ✅ |
| 26 | `servers#1160` open since 2025-03-31, 0 comments (§1a) | `open / 2025-03-31T09:45:50Z / comments: 0` | ✅ |
| 27 | `servers#3505` open PR, `--read-only` + `mode-utils.ts` + 261 test lines, 6 files, +598/-125, opened 2026-03-09, `review_comments: 0`, ~175 d, only comment a third-party review (§1a) | All exact. `readonly-enforcement.test.ts` = +261. One review exists but `author_association: NONE` — "no maintainer review" holds | ✅ |
| 28 | `registry` 7,203★ / `modelcontextprotocol` 9,085★ alive; CONTRIBUTING routes new servers to the registry (§1b) | Exact; CONTRIBUTING:20,24 and the PR template both route there | ✅ |
| 29 | `postgres-mcp` 3,241★, 89 open, 59 merged external, last-20 median **0.77 d**, newest merge 2026-08-16 (§1b) | Scout script: `external=59`, `median 0.77 d`, newest `2026-08-16T05:33:37Z` | ✅ exact |
| 30 | motherduck has no CONTRIBUTING, PR template, or CODEOWNERS (§2) | All six paths 404 | ✅ |
| 31 | Motherduck last-14 merged external: median **5.31 d**, min 0.03, max 47.45 (§2) | `external=14`, `median 5.31 d min 0.03 d max 47.45 d` | ✅ exact |
| 32 | `#20` "Add read-only mode support for DuckDB connections", external, merged **18.57 d** (§2) | `CONTRIBUTOR`, 2025-05-01T17:40:35 → 2025-05-20T07:24:50 = 18.57 d | ✅ |
| 33 | `#83` token-redaction fix merged **8.32 d** (§2) | 2026-04-20T02:44:45 → 2026-04-28T10:18:53 = 8.32 d | ✅ |
| 34 | README "read-only mode alone is not sufficient…" quote (§2) | Verbatim, README:207 | ✅ |
| 35 | README "Self-hosting DuckDB MCP: Use `--init-sql`…" quote (§2) | Verbatim, README:213 | ✅ |
| 36 | README recommends hosted Remote MCP; "Fork this repo and customize." (§2, §2 risk) | :209 verbatim (elided "zero-setup, read-write capable, and"); :211 truncates "…and customize **as needed**" | ✅ (m-3) |
| 37 | `database.py` `:104-107 :214-217 :318-321 :433-436` are the connect sites, read-only only via `duckdb.connect(read_only=…)` (§2) | All four line ranges exact | ✅ |
| 38 | "**all four** connect sites" (§2) | There are **five** `duckdb.connect` calls; `:128` is `duckdb.connect(":memory:")` with no `read_only` at all | ❌ **MF-7** (strengthens the argument) |
| 39 | `:212 read_only_flag = self._read_only if self.db_type == "motherduck" else False` (§2) | Exact | ✅ |
| 40 | `execute_query.py:21` is `return db_client.query(sql)` (§2) | Exact; whole function body | ✅ |
| 41 | `search/code` `total_count: 0` for `enable_external_access`, `disabled_filesystems`, `lock_configuration`, `allow_community_extensions` (§2) | All four re-run at 7 s spacing → `0` | ✅ |
| 42 | in-toto 45 merged external, last-20 median **11.42 d**, DCO required, no AI policy (§3) | Scout script pages=2 → `external=45`, `median 11.42 d`; DCO + Signed-off-by in in-toto/community CONTRIBUTING; 0 AI hits | ✅ exact |
| 43 | gittuf **115 merged external 2026-06-09 → 2026-08-26**, last-20 median **7.89 d**, max 24.03 (§3, §3b) | Independent count over that window = **115**, first 2026-06-09T10:05:53Z, last 2026-08-26T16:37:01Z; script `median 7.89 d min 0.30 d max 24.03 d` | ✅ exact |
| 44 | slsa 13 / 2.62 d; gitsign 6 / 31.79 d; abp 4 / 0.39 d, windows 2022-10 / 2026-01 / 2024-02 (§3) | All six numbers and all three window dates reproduce **exactly** under the scout's script at `pages=1` | ✅ (but see MF-2) |
| 45 | "13, 6 and 4 are the **entire** external merge histories" (method note) | False for slsa and gitsign: at `pages=3` slsa has **148** merged external (116 excluding `renovate-bot`) reaching back only to **2024-10-16**; gitsign has **12** back to 2024-06-28 | ❌ **MF-2** |
| 46 | slsa external PRs are "mostly dependency bumps, typo fixes and doc lines" (§3) | Holds — 32 of the top-148 are `renovate-bot` version bumps, the rest largely `impl: Update …` / spelling | ✅ |
| 47 | SLSA CONTRIBUTING: issue first → community discussion "guided by the steering committee" → optional proposal doc in `slsa-proposals` → PR (§3) | CONTRIBUTING:30–45, verbatim structure | ✅ |
| 48 | `new_predicate_guidelines.md` is PR-first; predicate template, `spec/predicates/README.md`, protobuf definition, "maintainers will review the PR at the next maintainers meeting", second PR to `in-toto.io` (§3a) | Lines 52–66, all five steps verbatim | ✅ |
| 49 | "Why don't existing predicates cover this use case?" verbatim (§3a) | Line 13, modulo the source's curly apostrophe and `[link]` markup | ✅ |
| 50 | `runtime-trace` v0.1 quotes (§3a) | "express a runtime trace of any operation" ✅; "from an operation spawned by a user using a CLI command" ✅; the hermetic quote stitches across "invoked via a script, **that** the build" without an ellipsis — substance intact | ✅ (m-4) |
| 51 | `scai.md` covers evidence-based supply-chain assertions (§3a) | Fair paraphrase of the document | ✅ |
| 52 | 13 open PRs, **12 from non-members**; `#591 #588 #587 #575 #570 #552 #581` are agent/AI predicate proposals (§3a) | Exactly 13 open, exactly 12 non-member (`#532` is MEMBER); all seven numbers, titles and dates exact | ✅ |
| 53 | `#502` open since 2025-11-20, 32 review comments; `#496` open since 2025-10-08, 42 review comments (§3a) | `#502`: 2025-11-20, `review_comments: 32`. `#496`: 2025-10-08, `review_comments: 42` | ✅ |
| 54 | "I read every thread on #588 #591 #582 #502 #496. **Every substantive review comment carries `author_association: NONE`… no maintainer comment appears on any of them**" (§3a) | **FALSE.** `#502` review comments = **17 MEMBER** + 15 NONE, plus **7 MEMBER reviews**. `#496` = **18 MEMBER** + 14 CONTRIBUTOR + 10 NONE, plus 2 MEMBER reviews | ❌ **MF-1** |
| 55 | "maintainer response rate to outside predicate PRs, over 13 open PRs, is **zero**" (§3) / "no maintainer has commented on any pending predicate" (§4) | Same falsification. True only of the eight **2026** agent/AI predicate PRs (`#591 #590 #588 #587 #582 #581 #575 #570 #552` — all comments `NONE`, zero maintainer reviews) | ❌ **MF-1** |
| 56 | `#588` +1464/-0, "six rounds of review" (§3a) | +1464/-0 ✅ over 2 files. The "six rounds" are **6 issue comments, all `NONE`**, plus 1 `NONE` review — no maintainer round | ❌ **MF-9** |
| 57 | Merged predicates `#508` **50.86 d**, `#470` **185.98 d** (§3a) | 2025-12-02T21:37:55→2026-01-22T18:22:28 = 50.86 d; 2025-07-03T20:06:22→2026-01-05T19:38:26 = 185.98 d | ✅ |
| 58 | gittuf AI policy quote and PR-template checkbox (§3b) | Verbatim, CONTRIBUTING:32–45 and `.github/pull_request_template.md`; DCO, tests and CoC boxes all present | ✅ |
| 59 | `docs/gaps/README.md` lists GAPs 1–6, **every one `Implemented: No`**, incl. GAP 3 "Authentication Evidence Attestations" and GAP 6 "Code Review Tool Attestations"; CONTRIBUTING routes design changes through a GAP; `docs/gaps/template.md` exists (§3b) | All exact; template.md returns 200 | ✅ |
| 60 | `v02.go:19 PredicateType = "https://gittuf.dev/reference-authorization/v0.2"`, predicate is `targetRef`/`fromID`/`targetID` (§3b) | Exact, line 19; struct has exactly those three fields | ✅ |
| 61 | Stage-A precedents `#1555 #1513 #1526` merged "**0.30 to 1.59 d** each" (§3, Stage A) | Actual: 0.74 d, 1.59 d, 0.68 d. **0.30 d is the last-20 minimum, not one of these three** | ❌ **MF-8** |

### Must-fix

**MF-1 (material — changes a stated reason, not the recommendation).** §3a's "Every substantive review comment carries `author_association: NONE`… no maintainer comment appears on any of them", §3's "the empirical maintainer response rate to outside predicate PRs, over 13 open PRs, is zero", and §4's "in a repo where no maintainer has commented on any pending predicate" are **contradicted by the API**: `in-toto/attestation#502` carries 17 MEMBER review comments and 7 MEMBER reviews; `#496` carries 18 MEMBER review comments and 2 MEMBER reviews. Both are named in the very sentence that claims otherwise. Replace with the claim that *is* true and still supports the verdict: **no maintainer has commented on or reviewed any of the nine 2026 predicate PRs (`#552 #570 #575 #581 #582 #587 #588 #590 #591`) — every comment on them is `author_association: NONE`** — while the two oldest predicate PRs received heavy maintainer review and are still open after 9–10.5 months. The corrected reading is *slower*, not *absent*, maintainer attention; the HIGH (~75%) in-toto rejection risk survives on the merge-latency evidence (50.86 d and 185.98 d) and the 9-month-open queue, but the "zero response rate" premise must go.

**MF-2 (material — a population claim, not a number).** The method note's "**14, 13, 6 and 4** are the *entire* external merge histories" is false for slsa and gitsign. Those figures are the yield of **one page of the 100 most-recently-*updated* closed PRs** — a sampling window, not a date range. Re-run at 3 pages, `slsa-framework/slsa` has **148 merged external PRs (116 excluding `renovate-bot`) reaching back only to 2024-10-16**, and `sigstore/gitsign` has **12 back to 2024-06-28**. §3's inference "fast *medians* over tiny *populations* … effectively closed to substance" therefore does not hold for slsa. Fix: state the sampling method honestly ("first page of closed PRs sorted by `updated` desc"), report slsa as ≥116 merged external PRs at a 2.62 d median dominated by dependency bumps, and rest the "closed to substance" verdict on the CONTRIBUTING governance path (issue → steering committee → proposal doc → PR), which *is* verified. The package-5 recommendation is unchanged.

**MF-3.** §1a: "each annotated `readOnlyHint: false, destructiveHint: true`" — `create_directory` (`index.ts:426`) is `destructiveHint: **false**`. Say "three of the four; `create_directory` is `destructiveHint: false`."

**MF-4.** §1: "13 of 20 … and **11 of those are `fix(filesystem)`**" — actual counts on the identical PR set are **14** matching `fix(<server>):` and **9** `fix(filesystem)`.

**MF-5.** §1: the diff range "+13/-0 to **+161/-18**" has no referent. Across the nine most recent merged external PRs the observed range is **+13/-0 … +157/-1**, with the largest deletion count being `#4104` at +19/-27. Restate as "+13/-0 to +157/-1".

**MF-6.** §1: "in-repo `CLAUDE.md` restates this **verbatim**" — it paraphrases (`CLAUDE.md:82`: "**Selective:** New features outside a server's core purpose or highly opinionated additions."). Drop "verbatim" or quote line 82.

**MF-7.** §2: "all **four** connect sites" — `database.py` has **five** `duckdb.connect` calls; the fifth, `:128 duckdb.connect(":memory:")`, passes no `read_only` argument at all. This strengthens the §2 argument and should be cited rather than omitted.

**MF-8.** §3 Stage A: precedents `#1555 #1513 #1526` are "0.30 to 1.59 d each" — actual 0.74 d, 1.59 d, 0.68 d. The 0.30 d is the last-20 minimum across all gittuf external PRs. Restate as "0.68 to 1.59 d each".

**MF-9.** §3a: `#588`'s "six rounds of review" is six issue comments plus one review, **all `author_association: NONE`** — no maintainer round. Word it as "six rounds of third-party comment".

### Notes not requiring a fix

- **m-1** §1's CONTRIBUTING quote lowercases the source's "Especially" after the em dash.
- **m-2** The `#1945` quote's `…` joins two paragraphs; both fragments are verbatim and the meaning is preserved.
- **m-3** "Fork this repo and customize." truncates "…and customize **as needed**"; add the ellipsis.
- **m-4** The `runtime-trace` hermetic quote stitches across "invoked via a script, **that** the build"; add an ellipsis.
- **Private-individual check: clean.** No maintainer is named as a person anywhere in the file — every actor appears by role ("a repo MEMBER", "an external contributor", "one contributor", "a maintainer"). No `@handles`, emails, or personal details. Two GitHub *account-owned repository slugs* appear (`ktanaka101/mcp-server-duckdb`, `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`); CLAUDE.md §2 permits repository names as-is, and neither is used to describe a person. **No redaction required.**
- **Instrument-bias label is correct and, if anything, understated.** The verifier's own instrument was ~98% GitHub. The two verdicts turning on maintainer intent (motherduck's hosted-product conflict; in-toto's meeting cadence) remain **UNVERIFIED** — I did not reach any non-GitHub venue either. The file's third UNVERIFIED item (whether `runtime-trace` v0.1 has a producer implementation) also remains open; `search/code` was not spent on it.
- **§0, §2 and §4's package-4 recommendation are fully verified** — including the cross-file contradiction in `adoption.md` (line 230 DOMINANT vs line 136 abandoned, under the rule at line 44), which reproduces exactly.

**Reproduction:** all commands above re-run 2026-08-30/31 UTC as `Alex-lop`, read-only. The scout's `prs.sh` was executed unmodified; an independent `jq` re-implementation of the same filter produced identical medians on all seven repos, which is why every statistic in the table above is marked exact rather than approximate.
---

**Fix pass: 9 items fixed.** (2026-08-31, `contribution-scout`.) MF-1 through MF-9 were applied to the body above; this Verification section is left as written so the record of what was wrong survives the correction. Every replacement figure was independently re-measured before it was written in, not copied from the finding: `gh api .../pulls/{502,496}/{comments,reviews}` and the same three endpoints for all nine 2026 predicate PRs (MF-1); `prs.sh` re-run at 3–4 pages on slsa, gitsign, attest-build-provenance and motherduck, plus a `page=N --jq length` probe to establish which histories are actually exhausted (MF-2); `fs_index.ts:371/401/426/630` (MF-3); a re-count of the identical 20-PR set (MF-4); nine `pulls/<n>` diff reads (MF-5); `CLAUDE.md:82` re-fetched (MF-6); `grep -n duckdb.connect database.py` (MF-7); three `pulls/<n>` timestamp reads on gittuf (MF-8); `pulls/588` counts (MF-9). Two figures came out differently from the finding's own re-run and the measured values were used: slsa returns **118** external merged PRs at `pages=3` (90 excluding `renovate-bot`), not 148/116, and its window reaches back to a **2021-09-16** merge rather than 2024-10-16 — which is itself evidence for MF-2's point, since the window is ordered by *update* time and therefore is not a date range and does not reproduce between runs. Two knock-on corrections were made that no finding named, because leaving them would have created fresh mismatches: `gitsign`'s median falls from 31.79 d (page-1 sample of 6) to **4.62 d** over all 12, and `attest-build-provenance`'s from 0.39 d to **0.63 d** over its complete 13 — both now reported with the sample they belong to. Neither recommendation moved: package 4 is still the motherduck `--secure` PR, package 5 is still gittuf Stage A only.
