# research/adoption.md — Incumbent adoption, measured — 2026-08-30 — `adoption-analyst` (Wave 1, fix pass 2026-08-30) — **INSTRUMENT-BIASED (GitHub = 88.6% of citations counted per fetched URL, 310 of 350; 67.2% counted per repo — over the 70% threshold on the unit CLAUDE.md §8 plainly reads, see Instrument log. The one-level confidence discount is therefore mandatory, not discretionary: every conclusion below is held one level lower, and the verdicts that rest on a GitHub-search zero-result are marked WEAK)**

**Summary (answers the question in 10 lines).**
1. **76 repos measured today by API.** 62 of them are Session-1 kill-incumbents (Table 1); under the numeric rule stated above Table 1 they classify as **20 dominant, 14 active-small, 12 abandoned, 5 dormant, 11 zero-adoption**. A further 14 kill-incumbents are commercial with no public repo (Table 1b, now sourced to Session 1 file+line) — 76 killers in total, against the brief's expected 25–45.
2. Session 1's rule "a free incumbent exists → kill" does not survive measurement in **27 of 62 cases** (12 abandoned + 4 dormant + 11 zero-adoption). One further repo, `Aider-AI/aider`, is dormant by the rule (0 commits in 90 days) but retains **64 distinct non-owner people** opening issues in 90 days at 48,613★ — it has stopped shipping and is *not* a re-openable category; it is excluded from the 27. **16 of the named killers have zero commits on their default branch in 90 days**, five of them for over a year.
3. One genuine correction to Session 1's numbers: `IBM/mcp-context-forge` is **4,389★**, where `ideas/r2-agent-guardrails-per-repo.md:228` cites only "73 HN points". (`denoland/clawpatrol` is **not** a correction — Session 1's own red-team already fixed it at `ideas/r2-agent-guardrails-per-repo.md:316`, "**`denoland/clawpatrol` has 1,034 GitHub stars**, not just \"112 HN points\" as listed"; today it is 1,033, i.e. one *fewer*.) Owner/status changes since Session 1: `invariantlabs-ai/mcp-scan` now redirects to **`snyk/agent-scan`** (acquired and renamed); `protectai/llm-guard` is **archived**; `microsoft/presidio` moved to `data-privacy-stack`; `NanoNets/Graft` moved to `trailhq`.
4. **plan-lint: no dominant incumbent.** The one exact-shape repo, `cirbuk/plan-lint` (13★, "Static analysis toolkit for LLM agent plans"), last pushed **2025-08-09** — abandoned, and it owns the PyPI name. Category open on a **gap**: nothing lints an *agent plan* as a schema+policy artifact; the maintained policy linters (`StyraInc/regal`, `conftest`) lint Rego, not plans.
5. **egress-guard: no dominant incumbent for the exact shape, and the name is gone.** PyPI `egress-guard` 1.0.0 was published **2026-08-29 — yesterday** (`AnyEvalOrg/egress-guard`, **0★**). The adopted tools sit on either side of the gap: `presidio-analyzer` 6.53M downloads/mo detects PII but is not an MCP hook; `mcp-scan` scans *server descriptions*, not response *values*. Open on a **gap**.
6. **agent-autopsy: a dominant adjacent incumbent exists — `kenryu42/cc-safety-net`** (1,518★, 100 commits/90d, 18 non-owner issues from 13 people) — but it *enforces*, it does not *report*. `microsoft/agentrc` (1,036★) is a config format with **5 distinct non-owner authors**. Open on **distribution**, not capability.
7. **readonly-gateway: DOMINANT INCUMBENT — build a contribution, not a package.** `modelcontextprotocol/servers` (89,977★, 64 c90, 64 distinct non-owner authors, pushed today) is the only repo in that table that clears the dominant rule, and its PyPI package `mcp-server-sqlite` pulls **60,015 downloads/month**. `motherduckdb/mcp-server-motherduck` is **active-small** under the rule (513★, c90 8, auth 7) despite 33,286 dl/mo and a company behind it. Every independent read-only SQLite gateway found is abandoned.
8. **change-receipt: DOMINANT INCUMBENTS — build a contribution, not a package.** Two of the four clear the dominant rule outright — `slsa-framework/slsa` (1,920★, c90 25, auth 10) and `sigstore/gitsign` (1,121★, c90 18, auth 13). `in-toto/attestation` (369★, 23,464 dl/mo) and `actions/attest-build-provenance` (1,027★, c90 7, 851 forks) miss it and are **active-small**, but the ecosystem's usage sits in `securesystemslib` at **1,009,281 dl/mo**. PyPI `jittest` 0.3.4 (2026-08-20) already ships Ed25519-signed receipts for agent-authored pull requests — at 0 stars.
9. **Net effect on §5's release order:** plan-lint, egress-guard and agent-autopsy stay packages; **readonly-gateway and change-receipt convert to contribution PRs** (named in §"Verdict" below).
10. **The pattern that matters more than any single verdict:** for the three packages that stay packages — plan-lint, egress-guard and agent-autopsy — *every* exact-shape competitor found is at **0–13 stars**, and every dominant repo is one layer away from the shape. (Across all five the range is **0–107 stars** — `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` at 107★ and `centralmind/gateway` at 546★ are exact-shape entries in the readonly-gateway table — but both are abandoned, 13 months without a push.) That is the distribution problem Session 1 diagnosed, confirmed with numbers.

---

## Method and its limits

Every row was produced today, 2026-08-30 (UTC 2026-08-31T00:5x), by these commands:

- metadata: `gh api repos/O/R --jq '[.stargazers_count,.forks_count,.created_at,.pushed_at,.owner.login,.archived]|@tsv'`
- commits: `gh api "repos/O/R/commits?since=2026-06-01T00:00:00Z&per_page=100" --jq length` (**caps at 100**; "100" below means ≥100)
- issues+PRs opened since 2026-06-01 and their authors: `gh api "repos/O/R/issues?state=all&sort=created&direction=desc&per_page=100"` piped to `jq` filtering `.created_at>="2026-06-01"` and `.user.login != owner`. This endpoint returns issues **and** PRs. It reads the 100 most recently created items, so a row marked `cap` means the true 90-day count is ≥100 and the non-owner count is a floor, not a total.
- releases: `gh api repos/O/R/releases/latest --jq .published_at`
- downloads: `curl https://pypistats.org/api/packages/<pkg>/recent` and `curl https://api.npmjs.org/downloads/point/last-month/<pkg>`
- lifetime star velocity = stars ÷ months since `created_at`, arithmetic shown per row (e.g. cc-safety-net: 1518 ÷ 8.2 months = 186/mo).

**Two instrument failures, both material, both worked around:**
1. **`gh api repos/O/R/stargazers` with `Accept: application/vnd.github.star+json` returns HTTP 404 for every repo with this token, and 401 unauthenticated.** The brief's preferred method for a 90-day star delta is therefore unavailable to me.
2. **Wayback replay is offline today.** `http://archive.org/wayback/available?...` answers correctly (snapshots exist for 9 of 10 repos probed) but `http://web.archive.org/web/<ts>/https://github.com/O/R` returns `<title>Internet Archive: Temporarily Offline</title>` (11,832 bytes, no repo HTML).

**Consequence: "stars gained in the last 90 days" is UNVERIFIED for every repo in this file.** I substitute three things that *are* verifiable and that the classification rule actually needs: lifetime star velocity, default-branch commits in the last 90 days, and the count of **distinct non-owner people** who opened an issue or PR in the last 90 days. The last of these is the strongest signal in the file — it is the one number a project cannot manufacture by pushing commits to itself.

**Owner-exclusion caveat:** `-author:<owner>` is meaningless when the owner is an org (an org never authors an issue), so for org-owned repos `non-owner = total`. Rows are still reported honestly; read the *distinct authors* column instead.

---

## The classification rule (stated before it is used)

Session 1 used the four labels informally. They are the load-bearing terms in this file — the class split, the "27 of 62" headline and both contribute-instead-of-ship verdicts all rest on them — so here is the numeric rule, evaluated **top-down, first match wins**, on the columns of Table 1 as measured on 2026-08-30. Nothing in this file uses any other definition.

| # | Class | Rule |
|---|---|---|
| 1 | **abandoned** | `archived == true` **OR** (`c90 == 0` **AND** last push ≥ 180 days ago, i.e. on or before 2026-03-03) |
| 2 | **dormant** | `c90 == 0` **AND** last push after 2026-03-03 |
| 3 | **zero-adoption** | `auth ≤ 3` **AND** `★ < 100` **AND** (no download figure **OR** downloads < 10,000/mo) |
| 4 | **dominant** | `c90 ≥ 10` **AND** `auth ≥ 10` **AND** last push ≤ 30 days ago (on or after 2026-07-31) **AND** (`★ ≥ 1,000` **OR** downloads ≥ 25,000/mo) |
| 5 | **active-small** | everything else (alive, some outside participation, below the dominant bar) |

Why this precedence and these numbers. Maintenance is tested **before** adoption because an unmaintained repo cannot be a killer however many stars it has — that is the whole point of CLAUDE.md §8's "existence is not a kill." `auth` (distinct non-owner people who opened an issue or PR in 90 days) is the axis that carries the most weight because it is the one number a project cannot manufacture by pushing commits to itself. The download floor of 25,000/mo is 50× the brief's own §9 package-success gate of 500/mo. `auth ≥ 10` is the smallest count at which "a community" is not one team.

**Rows the rule reclassifies against the labels this file originally carried (5 in Table 1, 1 in a package table), all reported, none re-tuned to preserve a verdict:**

| Row | Repo | Measurement | Was | Rule says | Why |
|---|---|---|---|---|---|
| 34 | `motherduckdb/mcp-server-motherduck` | 513★, c90 8, auth 7, 33,286 dl/mo | dominant *for its slot* | **active-small** | fails `c90 ≥ 10` and `auth ≥ 10`; "dominant for its slot" was a judgement, not a measurement |
| 35 | `DataRecce/recce` | 477★, c90 100, auth 8, 42,749 dl/mo | dominant | **active-small** | fails `auth ≥ 10` by two people |
| 38 | `in-toto/attestation` | 369★, c90 41, auth 15, 23,464 dl/mo | dominant | **active-small** | fails both adoption thresholds (★ < 1,000 and 23,464 < 25,000 dl/mo) |
| 47 | `asteroid-belt/skulto` | 49★, c90 0, auth 1, pushed 2026-08-23 | zero-adoption | **dormant** | maintenance is tested first; both descriptions are true of it |
| 50 | `cfitzgerald-pd/skillcop` | 8★, c90 0, auth 1, pushed 2026-05-29 | zero-adoption | **dormant** | same |
| pkg 5 | `actions/attest-build-provenance` | 1,027★, c90 7, auth 9, 851 forks | dominant | **active-small** | fails `c90 ≥ 10` and `auth ≥ 10` |

`Aider-AI/aider` was previously filed under a one-row category invented for it, *dormant-but-adopted*. The rule has no such class: it is **dormant** (c90 = 0, pushed 2026-05-22). Its 48,613★ and **64 distinct non-owner participants in 90 days** are reported in the row and in summary #2, and it is excluded from the "27 of 62" count for that reason.

**What the reclassifications do to the verdicts** (stated here so a reader does not have to reconstruct it): Package 4's "contribute" verdict is unaffected — `modelcontextprotocol/servers` is the only row in that table that clears the rule, and it clears every clause with room to spare. Package 5's "contribute" verdict narrows from four dominant standards to **two** (`slsa`, `gitsign`), with `in-toto/attestation`, `attest-build-provenance` and `gittuf` as active-small; two maintained dominant standards plus `securesystemslib` at ~1M downloads/month still kill a new competing receipt format, but the claim is thinner than it was and is held accordingly. No "ship" verdict changes.

**Pending CLAUDE.md §2 ruling (blocks push).** Roughly 18 rows below name an individual-owned repository slug. Section 2 forbids tracked-file content about a private individual; a repo slug is also the only checkable identifier a reader has, so a blanket strip would make the file unverifiable. The proportionate default applied here, pending an explicit ruling from the orchestrator: org- and company-owned slugs stay as they are (§2 permits them); for individual-owned repos the slug stays and **every editorial characterisation is deleted** — the row states the measured numbers and the class label and nothing else. If the ruling is stricter, rows 45–58 and their package-table echoes move to `private/` and are referenced by number.

## Table 1 — kill-incumbents with a public repo (measured today)

`★` stars · `vel` lifetime stars/month · `c90` commits since 2026-06-01 (caps at 100) · `i90` issues+PRs created since 2026-06-01 in the 100 most recent (`cap` = ≥100) · `auth` distinct **non-owner** people who opened one · `push` last push.

| # | Repo | Killed (dossier) | ★ | vel | c90 | i90 | auth | push | release | Class |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `modelcontextprotocol/servers` | b4 / readonly-gateway | 89,977 | 4,215 | 64 | cap | 64 | 2026-08-30 | 2026-08-18 | **dominant** |
| 2 | `colbymchenry/codegraph` | b4 repo graph | 68,696 | 9,338 | 100 | cap | 55 | 2026-08-26 | 2026-08-26 | **dominant** |
| 3 | `BerriAI/litellm` | r2 LLM-deprecation | 57,615 | 1,551 | 100 | cap | 40 | 2026-08-31 | 2026-08-23 | **dominant** |
| 4 | `Aider-AI/aider` | c1 flagship | 48,613 | 1,224 | **0** | cap | 64 | 2026-05-22 | 2025-08-09 | **dormant** (64 outside participants — see rule note) |
| 5 | `DeusData/codebase-memory-mcp` | b4 repo graph | 41,309 | 6,727 | 100 | cap | 28 | 2026-08-30 | 2026-08-19 | **dominant** |
| 6 | `continuedev/continue` | c1 flagship | 35,705 | 910 | 24 | cap | 64 | 2026-08-30 | 2026-06-19 | **dominant** |
| 7 | `oraios/serena` | b4 repo graph | 28,657 | 1,662 | 100 | cap | 42 | 2026-08-30 | 2026-08-09 | **dominant** |
| 8 | `microsoft/presidio` (now `data-privacy-stack`) | egress substitutes | 10,682 | 107 | 99 | cap | 43 | 2026-08-30 | 2026-07-22 | **dominant** (6,528,584 dl/mo) |
| 9 | `zilliztech/claude-context` | b4 repo graph | 12,455 | 841 | 7 | 43 | 29 | 2026-07-14 | none | active-small (slowing) |
| 10 | `guardrails-ai/guardrails` | egress substitutes | 7,335 | 170 | 77 | cap | 33 | 2026-08-27 | 2026-08-14 | **dominant** (142,938 dl/mo) |
| 11 | `potpie-ai/potpie` | b4 repo graph | 5,702 | 232 | 100 | cap | 19 | 2026-08-30 | 2026-07-03 | **dominant** |
| 12 | `NanoNets/Graft` (owner now `trailhq`) | b4 repo graph | 5,160 | 2,694 | 100 | cap | 28 | 2026-08-30 | none | **dominant** |
| 13 | `vitali87/code-graph-rag` | b4 repo graph | 4,851 | 335 | 100 | cap | **0** | 2026-08-31 | 2026-08-26 | active-small — see note A |
| 14 | `IBM/mcp-context-forge` | r2 guardrails | 4,389 | 279 | 100 | cap | 32 | 2026-08-28 | 2026-08-18 | **dominant** (corrects dossier) |
| 15 | `dagger/container-use` | c1 flagship | 4,028 | 264 | 8 | 16 | 5 | 2026-08-17 | 2025-08-19 | active-small (decaying) |
| 16 | `SQLMesh/sqlmesh` | b3 lineage | 3,260 | 69 | 91 | cap | 49 | 2026-08-30 | 2026-07-24 | **dominant** (551,041 dl/mo) |
| 17 | `protectai/llm-guard` | egress substitutes | 3,206 | 86 | 1 | 11 | 7 | 2026-07-08 | none | **abandoned (ARCHIVED)** — 186,489 dl/mo of momentum |
| 18 | `stravu/crystal` | c1 flagship | 3,115 | 210 | **0** | 0 | 0 | 2026-02-26 | 2026-02-26 | **abandoned** |
| 19 | `invariantlabs-ai/mcp-scan` (owner now `snyk`) | MCP security | 2,982 | 178 | 100 | cap | 28 | 2026-08-28 | 2026-08-19 | **dominant** (company-backed) |
| 20 | `elementary-data/elementary` | b3 lineage | 2,402 | 40 | 41 | 90 | 24 | 2026-08-30 | 2026-07-08 | **dominant** |
| 21 | `slsa-framework/slsa` | r2 provenance | 1,920 | 29 | 25 | 32 | 10 | 2026-08-29 | none | **dominant** (standard) |
| 22 | `kenryu42/cc-safety-net` | r2 guardrails | 1,518 | 186 | 100 | 45 | **13** | 2026-08-29 | 2026-08-25 | **dominant** |
| 23 | `zzet/gortex` | b4 repo graph | 1,510 | 314 | 100 | cap | 19 | 2026-08-30 | 2026-08-30 | **dominant** |
| 24 | `skillsgate/skillsgate` | c3 workflows | 1,141 | 172 | 12 | 11 | 6 | 2026-08-21 | 2026-06-08 | active-small |
| 25 | `sigstore/gitsign` | r2 provenance | 1,121 | 22 | 18 | 56 | 13 | 2026-08-24 | 2026-08-05 | **dominant** (standard) |
| 26 | `sipyourdrink-ltd/bernstein` | c1 flagship | 1,043 | 197 | 100 | cap | 14 | 2026-08-31 | 2026-08-28 | **dominant** |
| 27 | `microsoft/agentrc` | autopsy substitutes | 1,036 | 148 | 10 | cap | **5** | 2026-08-26 | none | active-small — see note B |
| 28 | `denoland/clawpatrol` | r2 guardrails | 1,033 | 253 | 100 | cap | 15 | 2026-08-19 | 2026-08-19 | **dominant** (corrects dossier) |
| 29 | `dbt-checkpoint/dbt-checkpoint` | b3 lineage | 764 | 11 | 10 | 18 | 10 | 2026-08-17 | 2026-06-18 | active-small |
| 30 | `gittuf/gittuf` | r2 provenance | 655 | 14 | 100 | cap | 17 | 2026-08-26 | 2026-06-30 | active-small (high commit, low star) |
| 31 | `gouline/dbt-metabase` | r2 metabase bot | 610 | 8 | 8 | 10 | 4 | 2026-08-06 | 2026-05-06 | active-small (120,616 dl/mo) |
| 32 | `devflowinc/uzi` | c1 flagship | 582 | 38 | **0** | 2 | 2 | **2025-06-04** | 2025-06-03 | **abandoned (15 months)** |
| 33 | `Shopify/deprecation_toolkit` | b5 watchdog | 538 | 5 | 10 | 15 | 1 | 2026-08-24 | 2026-05-07 | active-small |
| 34 | `motherduckdb/mcp-server-motherduck` | readonly-gateway | 513 | 25 | 8 | 15 | 7 | 2026-08-19 | 2026-08-19 | active-small (33,286 dl/mo, company-backed) |
| 35 | `DataRecce/recce` | b3 lineage | 477 | 14 | 100 | cap | 8 | 2026-08-28 | 2026-08-26 | active-small (42,749 dl/mo, paid tier) |
| 36 | `gtmagents/gtm-agents` | c3 workflows | 393 | 42 | **0** | 1 | 1 | 2026-04-03 | none | dormant (150 days) |
| 37 | `lasso-security/mcp-gateway` | MCP security | 384 | 23 | **0** | 7 | 6 | **2026-01-22** | 2026-01-21 | **abandoned (7 months)** |
| 38 | `in-toto/attestation` | r2 provenance / change-receipt | 369 | 6 | 41 | 35 | 15 | 2026-08-24 | 2026-03-18 | active-small (standard; 23,464 dl/mo) |
| 39 | `wrale/mcp-server-tree-sitter` | b4 repo graph | 310 | 18 | **0** | 0 | 0 | 2026-05-21 | 2026-04-09 | **abandoned (ARCHIVED)** |
| 40 | `Edison-Watch/open-edison` | r2 guardrails | 288 | 22 | **0** | 0 | 0 | **2026-01-22** | none | **abandoned (7 months)** |
| 41 | `eqtylab/cupcake` | r2 guardrails | 287 | 21 | **0** | 6 | 3 | **2026-03-02** | 2025-12-10 | **abandoned (181 days)** |
| 42 | `eqtylab/mcp-guardian` | MCP security | 199 | 11 | **0** | 0 | 0 | **2025-08-08** | 2025-04-08 | **abandoned (12+ months)** |
| 43 | `systempromptio/awesome-ai-agent-governance` | r2 guardrails | 33 | 8 | 53 | 57 | **50** | 2026-08-28 | none | active-small (a curated list; 50 distinct non-owner contributors) |
| 44 | `dwarvesf/claude-guardrails` | r2 guardrails | 33 | 6 | 2 | 5 | 4 | 2026-08-10 | 2026-04-17 | active-small |
| 45 | `varun369/skillfortify` (owner `qualixar`) | c3 workflows | 30 | 5 | 2 | 0 | 0 | 2026-08-05 | 2026-08-05 | **zero-adoption** |
| 46 | `until-dev/plugins` | r2 PR gate | 29 | 29 | 26 | 1 | 1 | 2026-08-27 | none | **zero-adoption** |
| 47 | `asteroid-belt/skulto` | c3 workflows | 49 | 7 | **0** | 1 | 1 | 2026-08-23 | 2026-04-19 | dormant |
| 48 | `clash-sh/clash` | c1 flagship | 63 | 9 | **0** | 2 | 2 | 2026-07-17 | 2026-02-08 | dormant |
| 49 | `Fszta/parrant` | r2 metabase bot | 78 | 4 | 100 | 80 | **0** | 2026-08-28 | 2026-08-27 | **zero-adoption** |
| 50 | `cfitzgerald-pd/skillcop` | c3 workflows | 8 | ~1 | **0** | 1 | 1 | 2026-05-29 | 2026-03-20 | dormant |
| 51 | `DNYoussef/codeguard-action` | r2 PR gate | 6 | 1 | 39 | 37 | **0** | 2026-08-17 | 2026-07-29 | **zero-adoption** |
| 52 | `Open-fab-ai/openfab` | r2 provenance | 6 | 2 | 100 | 38 | 2 | 2026-08-26 | 2026-06-30 | **zero-adoption** (Session 1 recorded 6★ / 0 forks at `ideas/r2-ai-code-provenance-receipts.md:69`) |
| 53 | `atlanhq/atlan-action` | b3 lineage | 5 | ~0 | 8 | 10 | 3 | 2026-08-28 | 2024-10-24 | **zero-adoption** (free front-end to a paid catalog) |
| 54 | `jacquardlabs/gauntlet` | r2 PR gate | 4 | 5 | 70 | 79 | **0** | 2026-08-25 | 2026-08-25 | **zero-adoption** |
| 55 | `Tania-coder/SEISMOGRAPH` | b5 watchdog | 3 | 1 | 100 | 26 | 1 | 2026-08-28 | 2026-07-18 | **zero-adoption** |
| 56 | `thossullivan/model-eol` | r2 LLM-deprecation | **0** | 0 | 85 | 88 | 3 | 2026-08-24 | 2026-08-18 | **zero-adoption** (1,504 npm dl/mo) |
| 57 | `Kartik24Hulmukh/jittest` | r2 PR gate / change-receipt | **0** | 0 | — | — | — | 2026-08-30 | PyPI 0.3.4 2026-08-20 | **zero-adoption** |
| 58 | `AnyEvalOrg/egress-guard` | egress-guard (new) | **0** | 0 | — | — | — | 2026-08-29 | PyPI 1.0.0 2026-08-29 | **zero-adoption** (1 day old) |
| 59 | `cirbuk/plan-lint` | plan-lint | 13 | 1 | **0** | 0 | 0 | **2025-08-09** | 2025-04-27 | **abandoned (12+ months)** |
| 60 | `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` | readonly-gateway | 107 | 5 | **0** | 4 | 3 | **2025-07-18** | none | **abandoned (13 months)** |
| 61 | `centralmind/gateway` | readonly-gateway | 546 | 29 | **0** | 0 | 0 | **2025-07-18** | 2025-07-12 | **abandoned (13 months)** |
| 62 | `modelcontextprotocol/servers-archived` | readonly-gateway | 295 | 20 | **0** | 0 | 0 | 2025-05-28 | none | **abandoned (ARCHIVED)** |

**Note A — `vitali87/code-graph-rag` (instrument caveat, not a judgement):** 4,851★. Of the 100 most recently created issues/PRs, all 100 were created since 2026-06-01, so the 100-item window does not reach back far enough to see any non-owner author. `auth = 0` here is a **floor artefact of the window**, not a measurement of outside interest, and the row is classed **active-small** on that basis rather than zero-adoption (★ ≥ 100 excludes it from the zero-adoption rule regardless).

**Note B — `microsoft/agentrc`:** 1,036★, ≥100 issues/PRs in 90 days, but only **5 distinct non-owner people** opened any of them. Compare `kenryu42/cc-safety-net` at 45 items from **13** people, or `punkpeye/awesome-mcp-servers` at ≥100 from **88**. Microsoft's stars are corporate reach; the participation is thin. This is the single most useful number in the file for `agent-autopsy`.

## Table 1b — kill-incumbents with no public repo (not re-measured; Session 1 verified these on 2026-08-30)

These killed ideas on *pricing*, not on adoption, so a star count would not have changed the call. I did not re-fetch them (CLAUDE.md §5: "Never re-run Session 1's research") and I make no claim about them beyond what the dossiers already verified — but §8 requires every claim to carry evidence, and §5 forbids *re-deriving* Session 1's work, not *citing* it. Each row therefore carries the dossier file and line a reader can check without a fetch. Line numbers are as of 2026-08-30.

| Incumbent | Killed | Session 1's evidence | Source (Session 1 dossier, file:line) |
|---|---|---|---|
| CodeRabbit | r2 PR gate, c1 | Pro **$24/user/mo**, Pro Plus **$48**, Security **$40**, Slack agent $0.50/agent-minute; **$1.5B valuation** ($143M Series C) — **commercial, dominant**. The "~$40M ARR" this file previously carried is **struck: UNVERIFIED** — Session 1 explicitly could not confirm it | `ideas/r2-ai-pr-verification-gate.md:67` (prices, from coderabbit.ai/pricing); `:252` ($1.5B, HN 49274706); `:237` ("CodeRabbit's '$40M ARR' … **could not be independently verified in this session**") |
| Greptile | r2 PR gate, b4 | Starter free (1 dev, 50 credits/mo); Pro **$30/seat/mo** (50 credits/seat, **$1/extra credit** — this file previously wrote "$1/review", corrected); TREX runtime validation shipped 2026-06-15 — **commercial, dominant** | `ideas/r2-ai-pr-verification-gate.md:68`; `:177` |
| Metabase Pro | r2 metabase bot | **$575/month** ($12/user/mo, first 10 included); Starter $100/mo; Dependency graph and Dependency diagnostics are footnoted "Available on Pro and Enterprise plans" — **commercial, dominant** | `ideas/r2-metabase-dbt-impact-bot.md:69` |
| Recce Cloud | b3 | Free $0 (10 preset checks, 100 agent reviews/mo); Team **$250/mo annual / $300/mo regular, unlimited seats** — commercial, active (OSS side measured at #35) | `ideas/b3-lineage-aware-pr-review.md:63`; `:140` |
| dbt platform (dbt Labs) | b3 | Developer **$0** (1 seat); Starter **$100 per user/month**; column-level lineage is Enterprise/Enterprise+ only — **commercial, dominant** | `ideas/b3-lineage-aware-pr-review.md:62` |
| Veto (vetoapp.io) | r2 guardrails | **$0 / $29 / $99 per user/mo**, feature-identical to the pitch (Claude Code hook + LiteLLM proxy + audit log) — commercial | `ideas/r2-agent-guardrails-per-repo.md:211`; confirmed verbatim by Session 1's own verifier at `:300` |
| grith (grith.ai) | r2 guardrails | **$0 / $25 per user/mo** / Enterprise; OS-level syscall interception, 18 filters — commercial | `ideas/r2-agent-guardrails-per-repo.md:212`; `:95` (grith.ai/pricing, HN 47305991) |
| MintMCP | r2 guardrails, c3 | enterprise MCP gateway, SOC 2 Type II, custom per-user pricing in four user bands — commercial. **Caveat carried forward:** Session 1's verifier marked the pricing *sentence* `not_found` on the live page; the four bands and the SOC 2 claim are verbatim | `ideas/r2-agent-guardrails-per-repo.md:213`; verifier caveat at `:109`–`:110` |
| Certificial | b6 insurance | free to insureds; **Applied Systems licenses the Epic/CSR24 integration free** — the incumbent answer ships at $0 inside the dominant AMS — **commercial, dominant** | `ideas/b6-insurance-agency-clerk.md:243`; `:118` |
| HappyRobot | b6 freight | **~$61–62M raised** ($44M Series B, Sept 2025), **~$500M valuation**; DHL, Ryder, Werner — **commercial, dominant** | `ideas/b6-freight-broker-clerk.md:143`; `:126` |
| Avalara Tariff Classification | b6 importer | **quote-only, no public dollar figure**; Automated / Self-Serve / Managed tiers, **260+ human classifiers, 180+ countries** — **commercial, dominant** | `ideas/b6-small-importer-clerk.md:76`; `:153` |
| MassLandlords | b6 property | free forms library; **2,593 members statewide**, Boston events — also the distribution channel — free, dominant in MA | `ideas/b6-property-manager-clerk.md:76` |
| CodeDD / Sema / Black Duck / Crosslake | r3 diligence | CodeDD **€4,490 flat to 1M LoC** + €79/user/mo add-on; Sema **$82.50/dev/mo** list (**still a pre-order 31 months on**); Black Duck "thousands of M&A deals"; Crosslake no published price, 6,000 prior transactions — **commercial, dominant** | `ideas/r3-ai-code-diligence.md:60` (CodeDD); `:61` (Sema); `:20` (Black Duck); `:63` (Crosslake) |
| Claude Code native (permissions, hooks, `managed-settings.json`, `/doctor`) | r2 guardrails, autopsy | free, bundled; `anthropics/claude-code` **measured by me today** at 143,476★, 94 c90, 71 distinct non-owner authors/90d — **dominant** by the rule, and the floor every package must clear | `ideas/r2-agent-guardrails-per-repo.md:182`; confirmed verbatim by Session 1's verifier at `:299`. Repo row measured today, not from Session 1 |

**Count:** 62 measured repos + 14 unmeasured commercial = **76 kill-incumbents**, against the brief's expected 25–45. Session 1 named more killers than it counted.

---

## Package 1 — `plan-lint` (static validator for agent plans and policies; Graphene `validation.py`)

| Substitute | What it is | ★ | c90 | i90 / non-owner authors | last push | downloads | Class |
|---|---|---|---|---|---|---|---|
| `cirbuk/plan-lint` | **"Static analysis toolkit for LLM agent plans"** — the exact shape | 13 | **0** | 0 / 0 | **2025-08-09** | PyPI `plan-lint` 0.0.3, last release **2025-04-29** | **abandoned** |
| a zero-star personal repo (owner and slug in `private/THIRD-PARTY.md`) | "Local-first linter for reusable agent skill instructions" | **0** | 64 | 15 / **0** | 2026-08-26 | — | **zero-adoption** |
| `StyraInc/regal` (owner `open-policy-agent`) | Rego linter — lints *policy*, not plans | 402 | 43 | 65 / 12 | 2026-08-25 | — | active-small, well-maintained |
| `open-policy-agent/conftest` | Tests structured config against Rego | 3,256 | 51 | 72 / 23 | 2026-08-25 | — | **dominant** (different shape) |
| `open-policy-agent/opa` | The policy engine itself | 12,180 | 100 | ≥100 / 18 | 2026-08-28 | — | **dominant** (different shape) |
| `eqtylab/cupcake` | GitHub description, verbatim: "A native policy enforcement layer for AI coding agents. Built on OPA/Rego." — enforces at runtime | 287 | **0** | 6 / 3 | **2026-03-02** | — | **abandoned** |
| `mbeacom/adrkit` | Machine-readable ADRs + governance | 11 | 100 | — | 2026-08-30 | — | **zero-adoption** |
| `gh api search/repositories?q=agent+plan+validator+lint+policy` | — | — | — | — | — | — | **`TOTAL=0`** |

**Verdict: NO dominant incumbent for this exact shape. The category is open on a GAP.**
X = **nothing validates an agent's *plan object* — the pre-execution list of steps, tools and targets — against a declarative policy, statically, before the agent runs.** The maintained tools (`opa`, `conftest`, `regal`) are a policy *engine* and its linter: they require you to already have written Rego and to already have a JSON document to test. The one project that named the plan itself as the artifact, `cirbuk/plan-lint`, has been dead for **12 months** and never exceeded 13 stars.
**Ship the package.** Two operational consequences for the builder: (a) **the PyPI name `plan-lint` is taken** by the abandoned project (0.0.3, 2025-04-29) — hand this to `naming-checker`; (b) the honest comparison page writes itself: "the OPA family lints your policy, this lints the plan your policy has to judge."
*Confidence: held one level lower per the bias label. The `TOTAL=0` search is weak evidence — CLAUDE.md §6 records that GitHub search ignores phrase quoting and ANDs terms, so a zero there means "no repo whose name/description contains all five words," not "nothing exists." The abandoned-incumbent finding does not depend on it.*

## Package 2 — `egress-guard` (value-level PII/secret egress firewall for MCP tool responses)

| Substitute | What it is | ★ | c90 | i90 / non-owner authors | last push | downloads/mo | Class |
|---|---|---|---|---|---|---|---|
| `AnyEvalOrg/egress-guard` | **"Deterministic, dependency-free detection of sandbox escape and undeclared external-host contact in agent traces"** — PyPI 1.0.0 published **2026-08-29** | **0** | — | — | 2026-08-29 | PyPI, 1 day old | **zero-adoption** |
| `microsoft/presidio` (`data-privacy-stack`) | PII detection + anonymization engine | 10,682 | 99 | ≥100 / 43 | 2026-08-30 | **6,528,584** (`presidio-analyzer`) | **dominant** (not an MCP hook) |
| `guardrails-ai/guardrails` | LLM I/O validation framework | 7,335 | 77 | ≥100 / 33 | 2026-08-27 | **142,938** | **dominant** (not MCP-response-scoped) |
| `protectai/llm-guard` | Input/output scanners incl. secrets, PII | 3,206 | 1 | 11 / 7 | 2026-07-08 | 186,489 | **abandoned (ARCHIVED)** |
| `invariantlabs-ai/mcp-scan` (owner `snyk`) | Scans MCP **servers/tool descriptions** for poisoning | 2,982 | 100 | ≥100 / 28 | 2026-08-28 | PyPI 5,350 · npm 1,976 | **dominant** (scans descriptions, not values) |
| `IBM/mcp-context-forge` | MCP gateway/registry | 4,389 | 100 | ≥100 / 32 | 2026-08-28 | — | **dominant** (gateway, not a value filter) |
| `lasso-security/mcp-gateway` | MCP gateway with guardrails | 384 | **0** | 7 / 6 | **2026-01-22** | — | **abandoned (7 months)** |
| `eqtylab/mcp-guardian` | MCP proxy/approval GUI | 199 | **0** | 0 / 0 | **2025-08-08** | — | **abandoned (12+ months)** |
| `Edison-Watch/open-edison` | GitHub description, verbatim: "🔐 Firewall Your Data, Control Agents. Prevent agent data exfiltration…"; README line 14, verbatim: "OpenEdison helps address the [lethal trifecta problem](…)" | 288 | **0** | 0 / 0 | **2026-01-22** | — | **abandoned (7 months)** |
| `gh api search/repositories?q=MCP+egress+firewall+PII+redaction` | — | — | — | — | — | — | **`TOTAL=0`** |
| `gh api search/repositories?q=MCP+tool+output+redaction+secrets+scanning` | — | — | — | — | — | — | **`TOTAL=0`** |

**Verdict: NO dominant incumbent for this exact shape. Open on a GAP — with a distribution warning.**
X = **screening the *values inside an MCP tool response* before they reach the model, as a library the server owner installs.** The dominant tools bracket this without covering it: `presidio` has the detectors but no MCP integration point; `mcp-scan` has the MCP integration point but inspects tool *descriptions* at scan time, not response *payloads* at call time; the three MCP gateways that sat exactly here (`lasso-security/mcp-gateway`, `eqtylab/mcp-guardian`, `Edison-Watch/open-edison`) are all abandoned — 7, 12 and 7 months dead respectively, with a combined 871 stars they stopped defending.
**Ship the package.** Two operational consequences: (a) **the PyPI name `egress-guard` was taken yesterday**, 2026-08-29, by a 0-star project describing a genuinely adjacent product (egress detection in agent *traces*, post-hoc, vs. this one's *response values*, in-line) — `naming-checker` must pick a different name, and the comparison page should name it rather than pretend it isn't there; (b) the strongest honest claim is not "nobody built this" but "three funded-looking gateways built it and all three stopped."
*Confidence: held one level lower. The two `TOTAL=0` searches are WEAK for the reason given above.*

## Package 3 — `agent-autopsy` (run-on-your-own-repo report of missing guardrails + three invariants worth a hook)

| Substitute | What it is | ★ | c90 | i90 / **distinct non-owner authors** | last push | Class |
|---|---|---|---|---|---|---|
| `anthropics/claude-code` `/doctor`, hooks, `managed-settings.json` | Free, bundled, first-party | 143,476 | 94 | ≥100 / **71** | 2026-08-28 | **dominant** — the floor |
| `kenryu42/cc-safety-net` | Blocks destructive commands, 134 secret rules, 13 agent CLIs, `npx` install | 1,518 | 100 | 45 / **13** | 2026-08-29 | **dominant** — *enforces*, does not *report* |
| `microsoft/agentrc` | Machine-readable agent config standard | 1,036 | 10 | ≥100 / **5** | 2026-08-26 | active-small (corporate stars, thin participation) |
| `denoland/clawpatrol` | "Security firewall for agents" | 1,033 | 100 | ≥100 / **15** | 2026-08-19 | **dominant** — enforces |
| `punkpeye/awesome-mcp-servers` | The marketplace/list layer | 93,322 | 100 | ≥100 / **88** | 2026-08-29 | **dominant** (a directory) |
| `wong2/awesome-mcp-servers` | Same | 4,283 | 10 | 0 / 0 | 2026-07-13 | active-small |
| `systempromptio/awesome-ai-agent-governance` | Curated list of *this exact category* | 33 | 53 | 57 / **50** | 2026-08-28 | active-small (50 distinct non-owner contributors to a list in this category) |
| `dwarvesf/claude-guardrails` | Hook pack | 33 | 2 | 5 / 4 | 2026-08-10 | active-small |
| `varun369/skillfortify`, `cfitzgerald-pd/skillcop`, `asteroid-belt/skulto` | Skill security scanners | 30 / 8 / 49 | 2 / 0 / 0 | 0 / 1 / 1 | 2026-08-05 / 2026-05-29 / 2026-08-23 | **zero-adoption / dormant / dormant** |
| `gh api search/repositories?q=claude+code+guardrails+audit+repo+report` | — | — | — | — | — | **`TOTAL=0`** |
| `gh api search/repositories?q=agent+guardrails+hooks+invariants+repo+scanner` | — | — | — | — | — | **`TOTAL=0`** |

**Verdict: NO dominant incumbent for this exact shape. Open on DISTRIBUTION, not on a gap.**
Every dominant tool here is an *enforcer* you install and configure; none is a *reporter* you run once against a repo you already have and that tells you what is missing. That distinction is thin — thin enough that `cc-safety-net` could add a `--report` flag in an afternoon — so the defensible position is not capability, it is being the artifact people run first. That is exactly what §5 says this package is for ("the inbound magnet").
The one number that makes this worth shipping rather than contributing: **`microsoft/agentrc` has 1,036 stars and 5 distinct non-owner participants in 90 days.** A Microsoft-branded standard in this category is being starred and not used. Nobody has won this on distribution; Microsoft's reach did not do it.
**Ship the package**, and treat the honest comparison page as the product: name `cc-safety-net` as the thing to install *after* the autopsy, not as a competitor.
*Confidence: held one level lower. The two `TOTAL=0` searches are WEAK; the agentrc participation number is strong and is not search-derived.*

## Package 4 — `readonly-gateway` (read-only MCP gateway over SQLite/DuckDB)

| Substitute | What it is | ★ | c90 | i90 / non-owner authors | last push | downloads/mo | Class |
|---|---|---|---|---|---|---|---|
| `modelcontextprotocol/servers` (`src/sqlite`) | The reference server set | **89,977** | 64 | ≥100 / **64** | 2026-08-30 | PyPI `mcp-server-sqlite` **60,015** | **DOMINANT** |
| `motherduckdb/mcp-server-motherduck` | DuckDB + MotherDuck MCP server | 513 | 8 | 15 / 7 | 2026-08-19 | PyPI **33,286** | active-small (company-backed; fails `c90 ≥ 10` and `auth ≥ 10`) |
| `crystaldba/postgres-mcp` | Postgres MCP with restricted/read-only mode | 3,240 | 1 | 37 / **24** | 2026-08-17 | — | active-small (24 outside people, 1 commit) |
| `designcomputer/mysql_mcp_server` | MySQL MCP, read-oriented | 1,374 | 26 | 3 / 3 | 2026-08-02 | — | active-small |
| `runekaagaard/mcp-alchemy` | SQLAlchemy-generic DB MCP | 418 | 4 | 2 / 2 | 2026-07-31 | — | active-small |
| `centralmind/gateway` | "Universal MCP-Server for your Databases" | 546 | **0** | 0 / 0 | **2025-07-18** | — | **abandoned (13 months)** |
| `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` | "safe, **read-only** access to SQLite databases" — the exact shape | 107 | **0** | 4 / 3 | **2025-07-18** | — | **abandoned (13 months)** |
| `executeautomation/mcp-database-server` | Multi-DB MCP incl. SQLite | 379 | **0** | 0 / 0 | **2025-08-27** | — | **abandoned (12 months)** |
| `ktanaka101/mcp-server-duckdb` | DuckDB MCP server | 178 | **0** | 2 / 2 | **2025-05-05** | PyPI `mcp-server-duckdb` (not read) | **abandoned (16 months)** |
| `modelcontextprotocol/servers-archived` | Where the old reference servers went | 295 | **0** | 0 / 0 | 2025-05-28 | — | **abandoned (ARCHIVED)** |
| PyPI `duckdb-mcp-server` | third-party | — | — | — | — | **334** | zero-adoption |

**Verdict: YES — a dominant, well-maintained incumbent exists. `modelcontextprotocol/servers`.**
89,977 stars, 64 commits and **64 distinct outside contributors in 90 days**, and its SQLite server pulls **60,015 PyPI downloads a month** — it clears every clause of the dominant rule with room to spare, and it is the only row in this table that does. `motherduckdb/mcp-server-motherduck` is **active-small** under the rule (c90 8, auth 7), so the DuckDB half is *held*, not *owned* — by a company-backed server at 33,286 downloads/month with a thin maintainer bench. There is no distribution to win here: the reference implementation ships in the protocol's own repo and is what every tutorial installs.
**Per CLAUDE.md §5, `pkg-readonly-gateway`'s artifact becomes a contribution PR.** The specific contribution, from X-Scraper `_ReadOnlyStorage`: **a hardened read-only mode for the SQLite MCP server — statement-level allowlisting (not regex on the query string), a connection opened with SQLite's `file:...?mode=ro` URI plus `PRAGMA query_only`, and a test suite proving the write paths that a naive read-only check misses (`ATTACH`, `PRAGMA writable_schema`, `CREATE TEMP`, recursive-CTE resource exhaustion).** That is a real gap in a dominant repo, it is a subset of code the principal has already tested, and it is the highest-trust artifact in the whole Wave-2 list — a merged PR in `modelcontextprotocol/servers` is worth more as distribution than a package nobody installs. Target the same work at `motherduckdb/mcp-server-motherduck` second (8 commits/90d, 7 outside people — a maintainer with room for help).
*Confidence: high, and it survives the one-level discount. This verdict rests on download counts and contributor counts, not on a search.*

## Package 5 — `change-receipt` (offline-verifiable receipt for an AI-authored change)

| Substitute | What it is | ★ | c90 | i90 / non-owner authors | last push | downloads/mo | Class |
|---|---|---|---|---|---|---|---|
| `sigstore/gitsign` | Keyless signed commits, Sigstore | 1,121 | 18 | 56 / **13** | 2026-08-24 | — | **DOMINANT** (standard) |
| `slsa-framework/slsa` | Provenance framework | 1,920 | 25 | 32 / **10** | 2026-08-29 | — | **DOMINANT** (standard) |
| `in-toto/attestation` | The attestation format itself | 369 | 41 | 35 / **15** | 2026-08-24 | PyPI `in-toto` **23,464**; `securesystemslib` **1,009,281** | active-small (standard; 369★ and 23,464 dl/mo both miss the dominant bar) |
| `actions/attest-build-provenance` | GitHub artifact attestations | 1,027 | 7 | 14 / 9 | 2026-08-21 | — | active-small (851 forks = in production, but c90 7 and auth 9 miss the bar) |
| `gittuf/gittuf` | Git-native policy + verifiable history | 655 | **100** | ≥100 / **17** | 2026-08-26 | — | active-small, heavily maintained |
| `Open-fab-ai/openfab` | The Apache-2.0 in-toto predicate Session 1 recorded at 6★ / 0 forks | **6** | 100 | 38 / **2** | 2026-08-26 | — | **zero-adoption** |
| `Kartik24Hulmukh/jittest` | PyPI summary, verbatim: "Differential test-execution gate for agent-authored pull requests with Ed25519-signed receipts." (GitHub description differs: "…for agent-authored pull requests. Emits Ed25519-signed receipts you can re-verify without trusting the tool.") | **0** | — | — | 2026-08-30 | PyPI 0.3.4, 2026-08-20, 6 releases | **zero-adoption** |
| `gh api search/repositories?q=AI+code+provenance+attestation+receipt+verify` | — | — | — | — | — | — | **`TOTAL=0`** |

**Verdict: YES — dominant, well-maintained incumbents exist. The in-toto / Sigstore / SLSA stack. (Narrowed by the classification rule — read the next paragraph before quoting this one.)**
Under the rule, **two** of these clear `dominant`: `slsa-framework/slsa` (1,920★, c90 25, auth 10) and `sigstore/gitsign` (1,121★, c90 18, auth 13). `in-toto/attestation`, `actions/attest-build-provenance` and `gittuf/gittuf` are **active-small** — maintained and real, but below the bar. What still kills a new competing receipt format is the combination: two dominant maintained standards, a signing library at **1,009,281 downloads/month**, GitHub's own action at 851 forks, and 10–17 distinct outside participants across the set. A new offline-verifiable receipt format competes with a signature ecosystem that already has adoption, tooling, and a CNCF-shaped governance story. The verdict holds on a narrower base than it originally claimed, and is held one level lower for that as well as for the bias label.

**Session 1's OpenFab evidence reproduces and its reasoning stands.** `Open-fab-ai/openfab` measures 6★, 0 forks, 100 commits/90d and **2 distinct non-owner participants in 90 days** — which is exactly what Session 1 recorded (`ideas/r2-ai-code-provenance-receipts.md:69`: "Apache-2.0, created 2026-06-10, **6 stars**, last pushed 2026-08-26"; `ideas/r2-ai-pr-verification-gate.md:318`: "openfab has **6 stars and 0 forks**", scored "as a credential, not a channel" *because* of that). Session 1 killed r2-provenance on the published in-toto predicate spec plus the live OpenSSF TAC thread (`ossf/tac#628`), **never on OpenFab's star count** — so its reasoning was specification overlap, not adoption, and it is correct. The kill is additionally reinforced by in-toto / Sigstore / SLSA adoption, which Session 1 did not measure. **An earlier draft of this file proposed a `WEEKLY.md` correction on this point; it is withdrawn — it corrected nothing and would have replaced an accurate record with a false premise.**

**Per §5, `pkg-change-receipt`'s artifact becomes a contribution PR.** The specific contribution, from Graphene `capsule.py` + `local_result.py` + `workspace_audit.py`: **an in-toto predicate (or a `gittuf` attestation type) for *workspace evidence* — the fenced-workspace hash chain that proves which files an agent could read and did write during a change — submitted to `in-toto/attestation` as a predicate spec with a reference verifier.** This is the one piece the existing stack genuinely lacks: SLSA and GitHub artifact attestations both establish *where and how software was built*, not *what the agent was allowed to touch while authoring it*. `gittuf` (100 commits/90d, 17 outside people) is the warmest maintainer to approach.
*Confidence: medium-high. It was "high, survives the discount" before the classification rule was written down; the rule narrows the dominant base from four standards to two (`slsa`, `gitsign`), so the verdict is held one level lower than that on top of the file-wide bias discount. It still rests on download and participant counts, not on a search.*

---

## What this changes for Wave 2

| Package | Verdict | Action |
|---|---|---|
| 1 `plan-lint` | no dominant incumbent; open on a **gap** (nothing lints the plan object) | **ship** — rename (PyPI `plan-lint` taken by an abandoned 13★ project) |
| 2 `egress-guard` | no dominant incumbent; open on a **gap** (value-level MCP response screening); 3 abandoned gateways | **ship** — rename (PyPI `egress-guard` taken 2026-08-29) |
| 3 `agent-autopsy` | no dominant incumbent; open on **distribution** (all incumbents enforce, none reports) | **ship** — this is the inbound magnet, as §5 says |
| 4 `readonly-gateway` | **dominant: `modelcontextprotocol/servers`** (89,977★, c90 64, 64 outside contributors/90d, 60,015 dl/mo — the only row in its table that clears the rule) | **contribute** — hardened read-only mode + write-path test suite |
| 5 `change-receipt` | **dominant: `slsa-framework/slsa` + `sigstore/gitsign`** (2 of 4 clear the rule; `in-toto/attestation` and `actions/attest-build-provenance` are active-small), plus `securesystemslib` at 1,009,281 dl/mo | **contribute** — workspace-evidence predicate to `in-toto/attestation`, via `gittuf` |

Release order in §5 was plan-lint → egress-guard → agent-autopsy → readonly-gateway → change-receipt. Packages 4 and 5 leave the queue as packages and enter it as PRs, which frees the largest two builds (8–12 and 10–15 agent-days) — the effort moves forward, exactly as §5 prescribes.

**No correction to `WEEKLY.md` is proposed.** An earlier draft of this file proposed one, on the grounds that `WEEKLY.md`'s R2 line was "wrong about OpenFab." It is not: Session 1 recorded OpenFab at 6★/0 forks in two dossiers and killed r2-provenance on the published in-toto predicate spec and the OpenSSF TAC thread, not on OpenFab's adoption. That measurement reproduces today (6★, 0 forks, 2 distinct non-owner participants in 90d) and the reasoning stands. The proposed edit is **withdrawn**. What this file adds to the standing record is not a correction but a reinforcement: the in-toto / Sigstore / SLSA adoption numbers, which Session 1 did not measure.

---

## Instrument log

**Venues and APIs tried today (2026-08-30 / UTC 2026-08-31):**

| Venue / API | Method | Result |
|---|---|---|
| `api.github.com` repos/commits/issues/releases | `gh api` (authenticated as `Alex-lop`) | **reachable** — 76 repos measured, core limit 5,000/hr, never exhausted |
| `api.github.com` `search/repositories` | `gh api` | **reachable but throttled** — **6** queries completed at 12s spacing. (An earlier draft of this log said 9. Only 6 appear anywhere in the file, so a reader could not check the other three; they are removed from the count rather than asserted.) |
| `api.github.com` `search/issues` | `gh api` | **blocked by secondary rate limit** after ~37 calls even at 3s spacing ("You have exceeded a secondary rate limit", request ID logged). Abandoned; replaced with the core `repos/O/R/issues` endpoint, which is strictly better (one call returns counts *and* author identities) |
| `api.github.com` `repos/O/R/stargazers` + `vnd.github.star+json` | `gh api` and `curl` | **needs-auth / 404** — HTTP 404 with a valid token on every repo tried, HTTP 401 unauthenticated. **The brief's preferred 90-day star-delta method is unavailable.** |
| `archive.org/wayback/available` | `curl` | **reachable** — 10 probes, 9 snapshots found near 20260601 |
| `web.archive.org/web/<ts>/…` (replay) | `curl -L` | **intermittent** — returned `Internet Archive: Temporarily Offline` (11,832-byte placeholder, HTTP 503) on every attempt I made. The verifier reproduced that byte-exact on one repo but got HTTP 200 and 442,339 bytes of real repo HTML on another minutes earlier, so the defensible wording is **unreliable today**, not down. **The brief's fallback 90-day star-delta method was unusable for me either way.** |
| `pypistats.org/api/packages/<pkg>/recent` | `curl` | **reachable but heavily rate-limited** — 429 at 9s spacing, succeeded at 22s. **12** packages read (an earlier draft said 11; the file cites 12 distinct successful figures), 5 not read (`elementary-data`, `jittest`, `dbt-checkpoint`, `parrant`, `mcp-server-duckdb` — **UNVERIFIED**) |
| `pypi.org/pypi/<pkg>/json` | `curl` | **reachable** — 6 name checks, no throttling |
| `api.npmjs.org/downloads/point/last-month/<pkg>` | `curl` | **reachable** — 4 queries, 2 packages resolved (`model-eol` 1,504; `mcp-scan` 1,976), 2 not found |
| `robots.txt` | — | not applicable: every fetch above is a documented public JSON API queried with its own client, not a crawl of HTML pages. No HTML page was scraped. |

All non-`gh` requests sent `-A "venture-research/2 (+https://github.com/Alex-lop/venture)"`. No login was used anywhere, no paywall was crossed, nothing was written to any third-party service, nothing was spent.

**Citations by host.** The file cites command templates rather than per-claim URLs (§8 permits "a command and its output"), so the count depends on the unit. Both defensible units are given; the label is the same under either, and under the unit §8 plainly reads — a fetched URL — the file is well over the threshold.

| Host | Per repo (1 repo = 1 citation) | Per fetched URL |
|---|---|---|
| `api.github.com` | **82** (76 repo measurements + 6 repository searches) | **310** (76 repos × 4 endpoints — metadata, commits, issues, releases — + 6 searches) |
| `pypistats.org` | 17 (12 successful, 5 unread) | 17 |
| `archive.org` + `web.archive.org` | 11 | 11 |
| `pypi.org` | 8 | 8 |
| `api.npmjs.org` | 4 | 4 |
| Hacker News | 0 | 0 |
| **Total** | **122** | **350** |

**HN + GitHub share: 310 / 350 = 88.6% per fetched URL; 82 / 122 = 67.2% per repo.** Arithmetic: 76 × 4 = 304, + 6 searches = 310; 310 + 17 + 11 + 8 + 4 = 350; 310 ÷ 350 = 0.8857. (The quote-verifier's recount gave 313 / 353 = 88.7%, which included the three `search/repositories` queries the file never showed; those are removed above. The × 4 endpoint model is an upper bound — rows 57 and 58 got metadata only — but the conclusion is not close enough to the line for that to matter.)

An earlier draft of this log reported 68.5%, kept the INSTRUMENT-BIASED label on judgement, and argued the arithmetic under-reported the bias. The arithmetic now carries the label on its own: **88.6% > 70%**, so the one-level confidence discount is **mandatory, not discretionary**, and every conclusion in this file is held one level lower on that basis.

What the label means in practice, beyond the number: the *question* was GitHub-shaped ("measure stars, forks, commits"), so the instrument was chosen for me, and this file cannot see any incumbent that is adopted without being on GitHub. Table 1b is the visible edge of that blind spot — 14 commercial killers I could count but not measure. Three specific things this file cannot tell you: whether any dominant-looking repo has *paying* users; whether an abandoned repo was abandoned because it was acquired or because it failed; and whether a package with high downloads has human users or CI robots. `demand-side-scout` and `venue-recoverer` are the agents that can see those.

**Marked UNVERIFIED in this file:** stars gained in the last 90 days (all repos — both prescribed methods unavailable to me); PyPI downloads for `elementary-data`, `jittest`, `dbt-checkpoint`, `parrant`, `mcp-server-duckdb`; the commercial incumbents in Table 1b (Session 1's, not re-fetched per §5 — now each carrying a dossier file:line a reader can check without a fetch); and **CodeRabbit's "~$40M ARR"**, which this file previously stated flatly and which Session 1 itself recorded as "could not be independently verified" (`ideas/r2-ai-pr-verification-gate.md:237`) — struck from Table 1b.

---

## Verification (2026-08-30, quote-verifier)

Method: every Table-1 row re-fetched with the author's own commands (`gh api repos/O/R`, `.../commits?since=2026-06-01T00:00:00Z&per_page=100`, `.../issues?state=all&sort=created&direction=desc&per_page=100` filtered to `created_at>="2026-06-01"` with `.user.login != owner`, `.../releases/latest`); all PyPI figures re-read from `pypistats.org/api/packages/<pkg>/recent` and `pypi.org/pypi/<pkg>/json`; npm from `api.npmjs.org`; all six `search/repositories` queries re-run; every quoted string re-read from the live `description` or README. All non-`gh` requests sent `-A "venture-research/2 (+https://github.com/Alex-lop/venture)"`. No sampling was needed for Table 1 — all 62 rows were re-fetched, not 20.

**155 claims checked — 135 VERIFIED, 7 MISMATCH, 0 UNREACHABLE, 13 UNCHECKED.**

| # | Claim | Verdict |
|---|---|---|
| V1 | Table 1, all 62 rows: `★`, `c90`, `i90`, `auth`, `push`, `release` | **VERIFIED (62/62 exact)**. `c90` reproduced digit-for-digit on all 62; `i90`/`auth` reproduced on all 62; every `release` date and every `none` reproduced. Star drift ≤ +3 (`colbymchenry/codegraph` 68,696→68,699; `DeusData/codebase-memory-mcp` 41,309→41,310; `oraios/serena` 28,657→28,658) |
| V2 | 14 package-table repos not in Table 1 (`claude-code`, `skill-plan-lint`, `regal`, `conftest`, `opa`, `adrkit`, `punkpeye/…`, `wong2/…`, `postgres-mcp`, `mysql_mcp_server`, `mcp-alchemy`, `executeautomation/…`, `mcp-server-duckdb`, `attest-build-provenance`) | **VERIFIED (14/14)**. Only drift: `anthropics/claude-code` 143,476→143,478★; `punkpeye/awesome-mcp-servers` 93,322→93,325★ and its Note-B author count 88→**91** (rolling 100-item window) |
| V3 | 12 PyPI download figures + 2 npm | **VERIFIED (14/14)**. npm exact (`model-eol` 1,504; `mcp-scan` 1,976). PyPI all drifted −1.2% to −3.5% in one direction, consistent with a 30-day rolling window read one day later: `mcp-server-sqlite` 60,015→59,228 · `mcp-server-motherduck` 33,286→32,381 · `securesystemslib` 1,009,281→997,380 · `presidio-analyzer` 6,528,584→6,355,035 · `sqlmesh` 551,041→544,272 · `guardrails-ai` 142,938→138,908 · `llm-guard` 186,489→181,308 (3 × HTTP 429 before succeeding) · `in-toto` 23,464→23,190 · `recce` 42,749→41,256 · `dbt-metabase` 120,616→118,375 · `mcp-scan` 5,350→5,284 · `duckdb-mcp-server` 334→313 |
| V4 | PyPI name/release facts: `plan-lint` 0.0.3 last release 2025-04-29; `egress-guard` 1.0.0 published 2026-08-29; `jittest` 0.3.4 2026-08-20, 6 releases | **VERIFIED (3/3 exact)** |
| V5 | Six `gh api search/repositories` queries return `TOTAL=0` | **VERIFIED (6/6)**, and the author's own WEAK label on them is correct |
| V6 | Owner/status changes: `presidio`→`data-privacy-stack`, `Graft`→`trailhq`, `mcp-scan`→`snyk`, `llm-guard` archived, `skillfortify`→`qualixar`, `regal`→`open-policy-agent`, `mcp-server-tree-sitter` archived, `servers-archived` archived | **VERIFIED (8/8)**. Addendum: the `mcp-scan` redirect target is `snyk/**agent-scan**` — the repo was renamed, not just re-owned. `DNYoussef/codeguard-action` now redirects to `DNYoussef/guardspine-code-action` (unrecorded, not load-bearing) |
| V7 | Quote — `cirbuk/plan-lint` "Static analysis toolkit for LLM agent plans" | **VERIFIED verbatim** |
| V8 | Quote — `skill-plan-lint`, `AnyEvalOrg/egress-guard`, `hannesrudolph/…` ("safe, **read-only** access to SQLite databases"), `centralmind/gateway`, `denoland/clawpatrol`, `jittest` PyPI summary fragment "Ed25519-signed receipts" | **VERIFIED (6/6 verbatim substrings)** |
| V9 | Quote — `eqtylab/cupcake` "policy enforcement layer for AI coding agents, built on OPA/Rego" | **MISMATCH.** Actual: `A native policy enforcement layer for AI coding agents. Built on OPA/Rego.` A sentence break was silently converted to a comma inside quote marks |
| V10 | Quote — `Edison-Watch/open-edison` "MCP Gateway to block the lethal trifecta" | **MISMATCH.** Not verbatim anywhere. Description: `🔐 Firewall Your Data, Control Agents. Prevent agent data exfiltration…`; README line 14: `OpenEdison helps address the [lethal trifecta problem](…)`. The quoted sentence is the author's paraphrase |
| V11 | Quote — `jittest` "Differential test-execution gate for agent-authored PRs with **Ed25519-signed receipts**" | **MISMATCH (minor).** PyPI summary reads `…for agent-authored pull requests with Ed25519-signed receipts.`; the GitHub description reads `…pull requests. Emits Ed25519-signed receipts you can re-verify without trusting the tool.` "PRs" was substituted inside the quote |
| V12 | Derived: 23 dominant / 11 active-small / 15 abandoned-or-dormant / 13 zero-adoption = 62 | **VERIFIED** — recounted from the Class column, tallies exactly |
| V13 | Derived: "16 of the named killers have zero commits on their default branch in 90 days" | **VERIFIED** — recounted `c90 == 0` across Table 1: exactly 16 |
| V14 | Derived: lifetime star velocity arithmetic | **VERIFIED** on 20 rows spot-checked against `created_at`; all within rounding (e.g. `cc-safety-net` 1518 ÷ 8.2 = 185.1, filed as 186) |
| V15 | Summary #2: "does not survive measurement in **28 of 62 cases**" | **MISMATCH.** The 28 includes `Aider-AI/aider` under the one-row category *dormant-but-adopted* — a repo at 48,613★ with **64 distinct non-owner people** opening issues in 90 days. A repo with 64 outside participants is not a case where "an incumbent exists → kill" failed. Honest figure: **27 of 62** |
| V16 | Summary #10: "*every* exact-shape competitor found is at 0–13 stars" | **MISMATCH**, contradicted by the file's own Package-4 table, which labels `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` (**107★**) "the exact shape"; `centralmind/gateway` (546★) is also an exact-shape entry |
| V17 | Summary #3: `denoland/clawpatrol` is 1,033★ (Session 1 "cited as HN points") | **MISMATCH.** `ideas/r2-agent-guardrails-per-repo.md:316` already states: "**`denoland/clawpatrol` has 1,034 GitHub stars**, not just \"112 HN points\" as listed." Session 1's own red-team caught this; it is not new drift, and the count has gone *down* by 1 |
| V18 | Summary #3: `IBM/mcp-context-forge` 4,389★ vs dossier's 73 HN points | **VERIFIED** — `ideas/r2-agent-guardrails-per-repo.md:228`: "`IBM/mcp-context-forge` — MCP Gateway and Registry, 73 HN points" |
| V19 | §Package 5 + §"One correction to the standing record": Session 1 cited OpenFab as the killer and "the kill was right, but not for the reason recorded"; `WEEKLY.md` is "wrong about OpenFab" | **MISMATCH.** Session 1 already recorded OpenFab's adoption: `ideas/r2-ai-code-provenance-receipts.md:69` — "Apache-2.0, created 2026-06-10, **6 stars**, last pushed 2026-08-26"; `ideas/r2-ai-pr-verification-gate.md:318` — "openfab has **6 stars and 0 forks**", and scores it "as a credential, not a channel" *because* of that. Session 1 killed on the published predicate spec + the live OpenSSF TAC thread, never on OpenFab's adoption. The proposed `WEEKLY.md` correction corrects nothing |
| V20 | Quote of `WEEKLY.md` line 33 | **VERIFIED** — ellipsis elides only "; PR-gate engine becomes C's instrument" |
| V21 | Instrument log: `stargazers` + `vnd.github.star+json` → 404 authenticated, 401 unauthenticated | **VERIFIED** — reproduced exactly on `kenryu42/cc-safety-net` |
| V22 | Instrument log: Wayback replay returns `Internet Archive: Temporarily Offline`, 11,832 bytes | **VERIFIED with nuance** — reproduced byte-exact (HTTP 503, 11,832 bytes) on `microsoft/agentrc`, but a probe of `kenryu42/cc-safety-net` minutes earlier returned **HTTP 200, 442,339 bytes of real repo HTML**. Replay is *intermittent*, not down. "Also unavailable" overstates it; "unreliable today" is the defensible wording |
| V23 | Instrument log: `archive.org/wayback/available` reachable, snapshots for 9 of 10 repos "near 20260601" | **PARTIAL** — endpoint reachable (VERIFIED), but on my 5-repo re-probe only 3 returned a snapshot (`modelcontextprotocol/servers` and `cc-safety-net` returned `"archived_snapshots": {}`), and `cirbuk/plan-lint`'s closest is **20250506** — 13 months from 20260601. "Near" is undefined |
| V24 | Instrument log: pypistats 429s, npm 4 queries / 2 resolved | **VERIFIED** — I hit 429 five times at 22s spacing and needed up to 75s |
| V25 | Instrument log: `pypistats.org` 16 citations (11 successful); Total 124; HN+GitHub 85/124 = 68.5% | **MISMATCH (arithmetic).** The file cites **12** distinct successful pypistats figures, not 11 (`presidio-analyzer`, `guardrails-ai`, `llm-guard`, `sqlmesh`, `recce`, `dbt-metabase`, `mcp-scan`, `in-toto`, `securesystemslib`, `mcp-server-sqlite`, `mcp-server-motherduck`, `duckdb-mcp-server`). 12 + 5 declared-unread = 17 attempts, total 125, share 85/125 = **68.0%**. See the recount below |
| V26 | Table 1b, 14 commercial rows (prices, ARR, valuations, raise amounts) | **13 UNCHECKED** — the file supplies no URL, no fetch date and no file/line pointer for any of them, and declares them out of scope per §5. Not re-fetched here for the same reason. `anthropics/claude-code` (143,476★ / 94 c90 / 71 authors) is the one measured row: **VERIFIED** (now 143,478★) |

### Instrument log, recounted

The file has **no per-claim URLs**; it cites command templates, which §8 permits ("a command and its output"). A recount therefore has to fix a unit. Two defensible units, both recounted:

| Unit | api.github.com | pypistats | archive.org | pypi.org | npmjs | HN | Total | HN+GitHub share |
|---|---|---|---|---|---|---|---|---|
| Author's unit (1 repo = 1 citation) | 85 (76 repos + 9 searches) | **17** (12 ok, 5 unread) | 11 | 8 | 4 | 0 | **125** | **68.0%** (author: 68.5%) |
| Per fetched URL (§8's plain reading) | **313** (76 repos × 4 endpoints — metadata, commits, issues, releases — + 9 searches) | 17 | 11 | 8 | 4 | 0 | **353** | **88.7%** |

Two further notes on the log. (a) Only **6** `search/repositories` queries appear anywhere in the file; the log claims 9 — three are counted as citations but never shown, so a reader cannot check them. (b) `Hacker News: 0` is correct: the file's two references to HN points are quotations *of Session 1's dossier*, not fetches.

**The label is right and the reason given for it is not needed.** The author kept the INSTRUMENT-BIASED label while reporting 68.5%, arguing on judgement that the arithmetic under-reports the bias. The arithmetic under a per-URL count agrees: **88.7%**, comfortably over the 70% line. The one-level confidence discount is mandatory, not discretionary, and the file's self-deprecating "this is a bad reason to pass a bias test" can be replaced with the number.

### Verdict

**The measurement layer is clean and the two structural verdicts hold; the framing around them does not.** Every one of the 62 Table-1 rows reproduced exactly — 62/62 on commits, 62/62 on issue and distinct-author counts, 62/62 on release dates, stars within +3 — and all 14 download figures reproduced with a uniform −1% to −3.5% one-day rolling-window drift. Nothing in this file was invented; that is an unusual result for a file of this size and it is worth saying plainly. The two verdicts that change Wave 2 — **`readonly-gateway` → contribute** (rests on `modelcontextprotocol/servers` at 89,977★ / 64 commits / 64 distinct outside authors and `mcp-server-sqlite` at 59,228 dl/mo) and **`change-receipt` → contribute** (rests on `securesystemslib` at 997,380 dl/mo, three maintained standards at 10–17 outside participants each, 851 forks on `actions/attest-build-provenance`) — rest entirely on numbers I re-fetched and confirmed, not on searches, and they survive the discount. The three "ship" verdicts also survive, though `plan-lint` and `egress-guard` rest partly on `TOTAL=0` searches the author correctly labels WEAK. What does **not** hold is the rhetorical layer: summary #10's "every exact-shape competitor is at 0–13 stars" is refuted by the file's own 107★ row; summary #2's "28 of 62" is inflated by filing a 48,613★ project with 64 outside participants under "dormant"; and two of the three "Session 1 got this wrong" corrections (clawpatrol, OpenFab) are things Session 1 already had right in `ideas/`, so the proposed `WEEKLY.md` edit should be withdrawn. Above all, the classification rule is never stated: "dominant", "active-small", "abandoned" and "zero-adoption" carry the entire file — the 23/11/15/13 split, the 28-of-62 headline, and both contribute-instead-of-ship calls — and no numeric threshold for any of them appears anywhere, which is exactly the undefined-term §8 deletes on sight. **Hold the two contribute verdicts at high confidence discounted one level to medium-high (they are download- and contributor-count-driven); hold the three ship verdicts at medium; treat summary lines #2, #3 and #10 and the `WEEKLY.md` correction as not established until the author's fix pass addresses the must-fix list.**

### Fix pass (2026-08-30, `adoption-analyst`, responding to the 9 must-fix items above)

| # | Must-fix | What changed |
|---|---|---|
| 1 | Four class labels undefined | New section **"The classification rule (stated before it is used)"** inserted before Table 1: numeric thresholds on `c90`, `auth`, push recency, `★` and downloads, evaluated top-down. The Class column was re-derived mechanically from the rule. **6 rows reclassify** (#34 `mcp-server-motherduck`, #35 `recce`, #38 `in-toto/attestation`, and pkg-5 `attest-build-provenance`: dominant → active-small; #47 `skulto`, #50 `skillcop`: zero-adoption → dormant), all listed in that section. Split changes from 23/11/15/13 to **20 dominant, 14 active-small, 12 abandoned, 5 dormant, 11 zero-adoption**. `Aider-AI/aider`'s invented one-row class *dormant-but-adopted* is gone; it is **dormant** |
| 2 | Summary #10 "every exact-shape competitor at 0–13 stars" | Restricted to the three shipped packages, with the 0–107 range for all five stated alongside (`hannesrudolph/…` 107★, `centralmind/gateway` 546★, both abandoned 13 months) |
| 3 | Summary #2 "28 of 62" | Now **27 of 62**, with `aider` split out explicitly as dormant-with-64-outside-participants and excluded |
| 4 | `WEEKLY.md` correction about OpenFab | **Withdrawn.** Replaced with Session 1's reproduced evidence (6★, 0 forks, 2 non-owner participants/90d) and the record that Session 1 killed on the in-toto predicate spec + `ossf/tac#628`, not on adoption. Package-5 verdict paragraph rewritten to match |
| 5 | Summary #3 `clawpatrol` drift | Removed from the drift list, replaced with Session 1's own red-team finding at `ideas/r2-agent-guardrails-per-repo.md:316` (1,034★ then, 1,033★ today — *down* one). `IBM/mcp-context-forge` stays as the one genuine correction |
| 6 | Three paraphrases inside quote marks | All three replaced with strings I re-fetched today (`gh api repos/O/R --jq .description`; `raw.githubusercontent.com/…/README.md`; `pypi.org/pypi/jittest/json`), each labelled with the surface it came from, elisions marked with `…` |
| 7 | Instrument-log arithmetic | pypistats row → **12 successful of 17**; three unshown `search/repositories` queries **removed** from the count (6, not 9); both counting units tabulated with the arithmetic shown; **310/350 = 88.6% per fetched URL**; the "bad reason to pass a bias test" judgement paragraph deleted and replaced by the number; header bias label updated |
| 8 | Table 1b unsourced | Source column added: every one of the 14 rows now points at a Session 1 dossier file and line. Two corrections surfaced by doing it — CodeRabbit's "~$40M ARR" **struck as UNVERIFIED** (Session 1 said so at `:237`), and Greptile's "$1/review" corrected to "$1/extra credit" |
| 9 | ~18 individual handles + pejorative characterisations | Proportionate default applied and **flagged as pending an explicit orchestrator ruling** (noted in the rule section, blocks push): org/company slugs unchanged; individual-owned rows keep the slug and lose every editorial clause — "all by the owner" (#49), "0 stars" (#56), "the saturation signal" (#43), and Note A's "a self-driven tracker" / "I do not claim zero outside interest," which is rewritten as a pure window artefact |

**Conclusions downgraded (5):** (a) the file-wide one-level confidence discount is now **mandatory**, carried by 88.6% arithmetic rather than by judgement; (b) Package 5's "contribute" verdict narrows from four dominant standards to **two**, and its confidence line drops from "high, survives the discount" to **medium-high**; (c) Package 4's DuckDB half drops from `mcp-server-motherduck` *owning* it to *holding* it (active-small); (d) summary #10's scope narrows from five packages to three; (e) summary #2 drops from 28 to 27. **Verdicts unchanged:** all three "ship" calls, and both "contribute" calls — Package 4 on `modelcontextprotocol/servers` alone, Package 5 on `slsa` + `gitsign` + `securesystemslib`.

**Still open, not fixable by me:** the CLAUDE.md §2 ruling in item 9. The proportionate default is applied; if the orchestrator rules stricter, rows 45–58 and their package-table echoes move to `private/` and are referenced by number.

Fix pass: 9 items fixed, 1 marked UNVERIFIED, 5 conclusions downgraded.


## Corrections (2026-08-30, orchestrator, after research/contributions.md and DECISION.md v4)
- **Package 4 (readonly-gateway) — the "dominant" verdict is void.** The row `modelcontextprotocol/servers (src/sqlite)` and the row `modelcontextprotocol/servers-archived` are the same artifact: the SQLite server was moved to the archived repository (`archived: true`, pushed 2025-05-28; `contents/src` of `servers@main` lists no `sqlite`, fetched 2026-08-30 — see `research/contributions.md`). The 60,015 dl/mo for `mcp-server-sqlite` is legacy traffic to a package last uploaded 2025-04-25. Under this file's own rule (archived ⇒ abandoned, evaluated first), the slot has no dominant row; the category is **open on a gap**. Sequencing per `DECISION.md` v4 §1.3: a hardened read-only-mode PR to `motherduckdb/mcp-server-motherduck` (active-small) first, gated 2026-09-15; the standalone package returns if that fails.
- **Package 5 (change-receipt).** `research/contributions.md` finds `in-toto/attestation`'s predicate queue unanswered (13 open outside PRs) and recommends neither a package nor a PR this quarter; `DECISION.md` v4 keeps an issue-first path with a 2026-10-15 gate. The dominant classification of the SLSA/Sigstore stack stands.
