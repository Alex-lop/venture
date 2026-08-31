# Naming: availability + confusability for the Wave-2 packages

**Agent:** `naming-checker` · **Date of all checks: 2026-08-30** (UTC probes ran 2026-08-31T00:55Z–01:20Z)
**Nothing was registered, published, or reserved.** Every row below is a read-only probe.

## Method (reproducible)

| Surface | Command |
|---|---|
| PyPI | `curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)" -o /dev/null -w '%{http_code}' https://pypi.org/pypi/<name>/json` — 404 = free, 200 = taken |
| PyPI normalization | Every hyphenated name probed a second time in underscore form. **Confirmed PEP 503 equivalence:** `plan-lint` → 200 and `plan_lint` → 200 (same project); `planlint` → 404. Hyphen/underscore/dot/case collapse to one name; `planlint` is a *different* name from `plan-lint`. |
| npm | `curl ... https://registry.npmjs.org/<name>` — 404 = free. npm does **not** normalize separators: `agent-autopsy` → 200 but `agent_autopsy` → 404. |
| GitHub (principal) | `gh api repos/Alex-lop/<name>` — 404 = free |
| GitHub (confusables) | `gh api "search/repositories?q=<name>+in:name&sort=stars&order=desc&per_page=3"` |
| PATH collision | `command -v <name>` |
| Adoption of incumbents | `curl https://pypistats.org/api/packages/<name>/recent` |

`gh auth status` on this machine: active account **`Alex-lop`** (token scopes `gist, read:org, repo`). All repo-existence checks below are therefore authoritative for the principal's namespace.

**Instrument note (§8):** availability is a registry fact, not a web-search finding — 0% of the availability rows come from HN/GitHub prose. The confusability and trademark rows are GitHub- and vendor-site-shaped; those are labeled where they carry judgment rather than a status code.

---

## 1. Full results table

`—` = not probed. **Bold** = the recommendation.

### Package 1 — static validator for agent plans/policies

| Candidate | PyPI | GitHub `Alex-lop/` | GitHub confusables (`in:name`) | npm | Verdict |
|---|---|---|---|---|---|
| `plan-lint` | **200 TAKEN** | free | 13 repos; `cirbuk/plan-lint` ★13 | 404 free | **DEAD** — see §2.1 |
| `plan_lint` | 200 TAKEN (= `plan-lint`) | — | — | 404 free | DEAD, same project |
| `planlint` | 404 free | free | 5 repos, all ★0; `donbeave/planlint` = "Rust plan-contract compiler … deterministic AI-agent verification" | 404 free | **REJECT** — typosquat-shaped near-miss on a live same-category PyPI name |
| **`agent-plan-lint`** | **404 free** | **free** | **total=0** | **404 free** | **AVAILABLE — recommended** |
| `agent_plan_lint` | 404 free (= above) | — | — | 404 free | same name on PyPI |
| `planguard` | **200 TAKEN** | free | — | 404 free | DEAD — `DBArkimetrix/planguard` v0.7.6, 11 releases, last upload 2026-04-30, adjacent purpose ("Make AI-assisted development safer, auditable") |
| `plancheck` | 404 free | free | 198 repos; `LDClark/PlanCheck` ★58 (radiotherapy), `stephendotcarter/planchecker` ★20 | 200 TAKEN (placeholder, 0 versions, 2018) | REJECT — generic, npm name held, medical-physics meaning dominates the term |
| `planfence` | 404 free | free | total=0 | 404 free | AVAILABLE — clean fallback (§2.1) |
| `plangate` | 404 free | free | 8 repos, ★2/★1/★0, all agent-workflow gating | AVAILABLE but crowding fast in exactly our category |
| `policy-lint` | 404 free | free | 30 repos; `Azure/azure-policy-linter` ★7, `Amara-ops/agent-guardrails-policy-linter` ★2 | 404 free | AVAILABLE, weaker — "policy lint" already means Azure/OPA policy |
| `plan-assert` | 404 free | free | — | 404 free | AVAILABLE, unshopped |

### Package 2 — value-level PII/secret egress firewall for MCP tool responses

| Candidate | PyPI | GitHub `Alex-lop/` | GitHub confusables | npm | Verdict |
|---|---|---|---|---|---|
| `egress-guard` | **200 TAKEN** | free | — | 404 free | **DEAD** — see §2.2 |
| `egress_guard` | 200 TAKEN (= above) | — | — | 404 free | DEAD, same project |
| `egressguard` | 404 free | free | 4 repos; `Hipepper/EgressGuard` ★6, `Erythrites/EgressGuard` = "Build AI Egress Guard", `0x7f9/EgressGuard` = "Default-deny outbound firewall" | 404 free | **REJECT** — near-miss on the live `egress-guard` PyPI name *and* three same-name GitHub repos |
| `mcp-egress-guard` | **200 TAKEN** | free | `goutamadwant/mcp-egress-guard` ★0 | 404 free | **DEAD** — see §2.2 |
| `mcp-egress` | 404 free | free | 4 repos, top ★1 unrelated (mTLS); #2 is `mcp-egress-guard` itself | 404 free | REJECT — one word short of a live package that does our exact job |
| `toolguard` | **200 TAKEN** | free | — | 404 free | **DEAD** — v0.2.21, 40 releases, **133,248 downloads/month**, "Policy adherence code generation for guarding AI agent tools." Only genuinely *dominant* incumbent in the whole sweep |
| `egress-firewall` | 404 free | free | 20 repos; `Azure/azure-firewall-egress-controller` ★14, `github-early-access/actions-native-egress-firewall` ★11 | 404 free | REJECT — term is owned by *network-layer* egress control; our product is value-level, so the name misdescribes the product |
| **`egresswall`** | **404 free** | **free** | **total=0** | **404 free** | **AVAILABLE — recommended** |
| `valuewall` | 404 free | free | 5 repos, all ★0 `valuewallet` typos | 404 free | AVAILABLE — runner-up; names the actual differentiator (value-level, not connection-level) |
| `leakstop` | 404 free | free | 8 repos, all ★0, no description | 404 free | AVAILABLE, plainer |
| `mcp-redact` | 404 free | free | 25 repos; `gs-mcp-proxy-pii-redactor` ★7, `redact-mcp` ★6, `pg-redact-mcp` ★4 | 404 free | AVAILABLE but the crowded end of the category |
| `tool-dlp` | 404 free | free | 72 repos, all noise (`yt-dlp`, `DL_POLY`, `DLPan`) — the `dlp` token is unsearchable | 404 free | REJECT — search-hostile |

### Package 3 — run it on your repo → missing-guardrails report (the inbound magnet)

| Candidate | PyPI | GitHub `Alex-lop/` | GitHub confusables | npm | Verdict |
|---|---|---|---|---|---|
| `agent-autopsy` | 404 free | free | 27 repos; `Abhisekhpatel/AgentAutopsy` ★11, `navanchauhan/agent-autopsy` ★9, `MenokoOG/agent-autopsy` ★1 | **200 TAKEN** (v0.1.2, created 2026-07-09, "Autopsy your coding-agent sessions") | **DEAD** — trademark + npm + crowded, see §2.3 |
| `repo-autopsy` | 404 free | free | 24 repos, top ★0 but three separate `repo-autopsy` projects exist | **200 TAKEN** (v0.0.3, created 2026-07-15) | DEAD — same trademark issue, npm taken |
| `autopsy` | **200 TAKEN** | free | `sleuthkit/autopsy` **★3301**, pushed 2026-06-20 | **200 TAKEN** (2015, 22 versions) | **DEAD** — registered trademark, see §2.3 |
| `agent-checkup` | 404 free | free | 5 repos; **exact-name** `ryuichiyamaguchi/agent-checkup` ★0 | 404 free | AVAILABLE, minor exact-name GitHub clash |
| `repo-checkup` | 404 free | free | 20 repos; `i-am-noamg/fast-repo-checkup` ★4 | 404 free | AVAILABLE, generic |
| **`guardrail-checkup`** | **404 free** | **free** | **total=0** | **404 free** | **AVAILABLE — recommended** |
| `guardrail-scan` | 404 free | free | 8 repos, all ★0, but "guardrail scanner" there means *LLM red-teaming*, not repo static analysis | 404 free | REJECT — misdescribes |
| `guardrail-audit` | 404 free | free | 40 repos; `…guardrail-auditor-skill` ★9 | 404 free | AVAILABLE, weaker than `-checkup` |
| `agentcheckup` | 404 free | free | — | 404 free | AVAILABLE, unshopped |

### Package 4 — read-only MCP gateway over SQLite/DuckDB

| Candidate | PyPI | GitHub `Alex-lop/` | GitHub confusables | npm | Verdict |
|---|---|---|---|---|---|
| **`readonly-gateway`** | **404 free** | **free** | **total=1** — `mlasch/smart-garden-gateway-yocto-meta-readonly-rootfs-overlay` ★0, unrelated | **404 free** | **AVAILABLE — recommended, cleanest name in the entire sweep** |
| `readonly_gateway` | 404 free (= above) | — | — | 404 free | same name on PyPI |
| `ro-gateway` | 404 free | free | 780 repos — `ro` is a substring token, matches every `…routing-gateway`, `…rocketchat-push-gateway` ★47 | 404 free | REJECT — `ro-` is not a legible abbreviation and destroys searchability |
| `readonly-mcp` | 404 free | free | 153 repos; `paulomac1000/ha-mcp-readonly` ★42, `kubernetes-readonly-mcp` ★6, `readonly-filesystem-mcp` ★6 | 404 free | AVAILABLE but a busy naming pattern — "readonly-X-mcp" is a genre |
| `mcp-readonly` | 404 free | free | same 153-repo result set | 404 free | same as above |
| `sqlite-readonly-mcp` | 404 free | free | 2 repos, both ★0, incl. exact-name `dochaocn/sqlite-readonly-mcp` | 404 free | AVAILABLE but **excludes DuckDB**, which the product supports — do not paint the name into SQLite |

### Package 5 — offline-verifiable receipt for an AI-authored change

| Candidate | PyPI | GitHub `Alex-lop/` | GitHub confusables | npm | Verdict |
|---|---|---|---|---|---|
| **`change-receipt`** | **404 free** | **free** | **total=4**, all ★0, none a Python package | **404 free** | **AVAILABLE — recommended** |
| `change_receipt` | 404 free (= above) | — | — | 404 free | same name on PyPI |
| `changereceipt` | 404 free | free | total=0 | 404 free | AVAILABLE, but unreadable run-together |
| `git-receipt` | 404 free | free | 92 repos; `aschmelyun/github-receipts` **★201** = "GitHub issues receipt printer" | **200 TAKEN** ("Print your git activity as a thermal receipt — tech debt tax") | **REJECT** — npm taken and the whole `git-receipt` / `github-receipt` neighborhood is *novelty thermal-printer toys*. Catastrophic connotation for a verifiable-provenance product |
| `ai-change-receipt` | 404 free | free | total=0 | 404 free | AVAILABLE, but the `ai-` prefix ages badly and adds nothing |

### Family / docs-site name

| Candidate | PyPI | GitHub `Alex-lop/` | GitHub confusables | npm | Verdict |
|---|---|---|---|---|---|
| `seatbelts` | 404 free | free | 63 repos, all Garry's Mod / student projects | **200 TAKEN** (reserved 2016, 0 versions) | **DEAD** — see §2.4 |
| `agent-seatbelts` | 404 free | free | 1 repo: `ban10yuu/awesome-agent-seatbelts` ★0 = "Curated safety, audit, context, and verification tools for AI coding agents" — *someone already uses this phrase for our exact category* | 404 free | **DEAD** — GhostPack collision, see §2.4 |
| `provable` | **200 TAKEN** | free | — | **200 TAKEN** (2017) | **DEAD** — PyPI `provable` v0.9.0 (provable.ml, "certified discovery for tree ensembles", uploaded 2026-08-07); npm `provable` = blockchain fair-random |
| `boundedagents` | 404 free | free | **total=0** | 404 free | AVAILABLE, clunky |
| `bounded-agents` | 404 free | free | total=0 | 404 free | AVAILABLE, vague — describes a research posture, not a product family |
| `graphene-tools` | 404 free | free | 1 repo: `NateScarlet/graphene-django-tools` ★7 | 404 free | **DEAD** — see §2.5. Registry-free, category-fatal |
| `graphene_tools` | 404 free (= above) | — | — | 404 free | same |
| `handrail` *(own)* | 404 free | free | 80 repos; `brekk/handrail` ★5 = "add safety to your pipes" — same *metaphor*, same *concept* | **200 TAKEN** (2017, 27 versions, "safety for your functional pipelines") | REJECT — npm taken by a same-metaphor safety library |
| `holdfast` *(own)* | **200 TAKEN** | free | — | **200 TAKEN** | **DEAD** — PyPI `holdfast` v0.5.1 = "Governed evolution for prompts and skills … stay within contracts" (uploaded 2026-04-17). Same category, 7 releases |
| `agentproof` *(own)* | **200 TAKEN** | free | — | **200 TAKEN** | **DEAD** — PyPI = "pytest-based behavioral testing framework for AI agents"; npm = agent-service trust scores. Both same category |
| **`guardposts`** *(own)* | **404 free** | **free** | **total=0** | **404 free** | **AVAILABLE — recommended** |

---

## 2. The five findings that actually change the plan

### 2.1 `plan-lint` is taken *by the same product idea*, and its console script is `plan-lint`

`cirbuk/plan-lint` on PyPI: v0.0.3, summary **"plan-linter is a static analysis toolkit for LLM agent plans"** (`curl https://pypi.org/pypi/plan-lint/json`, 2026-08-30). This is not a name clash — it is the Wave-2 `pkg-plan-lint` one-liner, already shipped.

Its `pyproject.toml`, read via `gh api repos/cirbuk/plan-lint/contents/pyproject.toml`, declares:

```
[project.scripts]
plan-lint = "plan_lint.cli:app"
```

**So `plan-lint` is an occupied console-script name on PATH, not just an occupied PyPI name.** Shipping a binary called `plan-lint` would collide for any user who has both installed — whichever wheel installs second silently wins. Do not use `plan-lint` as an entry point under any package name.

Adoption, per §8's incumbent rule (`pypistats.org/api/packages/plan-lint/recent`, 2026-08-30): **15 downloads/month, 3 last week, 0 yesterday**; ★13; last release 2025-04-29; last push 2025-08-09. Classification: **zero-adoption**. The *category* is open — the *name* is not. Take the category, leave the name.

### 2.2 `egress-guard` was published on PyPI **yesterday**, and `mcp-egress-guard` is already our product

- `egress-guard` v1.0.0, uploaded **2026-08-29T20:13:31Z** — one day before this check. `AnyEvalOrg/egress-guard` ★0, pushed 2026-08-29. 111 downloads in its first day.
- `mcp-egress-guard` v1.0.1, last upload 2026-08-15, 149 downloads/month. Summary: **"Local-first MCP reverse proxy that blocks sensitive, destructive, or policy-violating tool calls before execution using deterministic rules, DLP matchers, and A[…]"**

That second one is the Wave-2 `pkg-egress-guard` brief almost word for word. Neither has adoption (both effectively zero-adoption, so §8 says the category stays open), but the entire `egress-*guard` name neighborhood is now occupied by two live packages doing our job. Any near-miss we pick (`egressguard`, `mcp-egress`) reads as a clone and competes for the same search results while being a different install. Move one word sideways: **`egresswall`**.

Separately, `toolguard` is the one **dominant** incumbent found anywhere in this sweep — **133,248 downloads/month**, 40 releases, "Policy adherence code generation for guarding AI agent tools." Per §5's release rule, `toolguard` is not just an unavailable name; it is a candidate for the "contribute instead of compete" branch. Flagging for `adoption-analyst` / the orchestrator, not resolving it here.

### 2.3 `Autopsy` is a registered trademark in our own category

> "Autopsy® is a digital forensics platform and graphical interface to The Sleuth Kit®" — sleuthkit/autopsy, **★3301**, pushed 2026-06-20 (`gh api repos/sleuthkit/autopsy`). The vendor states Autopsy and The Sleuth Kit are **registered trademarks held by the tool’s author, an individual rather than a company** (https://www.sleuthkit.org/autopsy/, https://www.autopsy.com/, retrieved 2026-08-30).

Trademark protection is category-scoped, and that is precisely the problem: Autopsy is a **security/forensics analysis tool** and `agent-autopsy` would be a **security analysis tool**. This is the same class of goods, not a distant homonym. It is also the package explicitly designated as *the inbound magnet* — the one name that will be typed into search engines and said aloud at meetups. A name that returns a 3,301-star forensics platform is a distribution bug before it is a legal one.

Independently, the name is gone anyway: **npm `agent-autopsy` is taken** (v0.1.2, created 2026-07-09, "Autopsy your coding-agent sessions — see every tool call, token, and dollar"), **npm `repo-autopsy` is taken** (created 2026-07-15), and GitHub has 27 `agent-autopsy` repos including `AgentAutopsy` ★11 ("Replay any AI failure exactly as it happened"). Three separate parties reached this metaphor in the last two months.

**Not a legal opinion.** Whether use would actually infringe is a lawyer's call and is UNVERIFIED here. The recommendation stands on availability and distribution alone, which is enough.

### 2.4 `seatbelt` is a 4,689-star security tool

`GhostPack/Seatbelt` — **★4689** (`gh api repos/GhostPack/Seatbelt`) — "a C# project that performs a number of security oriented host-survey 'safety checks'" (https://github.com/GhostPack/Seatbelt, https://docs.specterops.io/ghostpack-docs/Seatbelt-mdx/overview, retrieved 2026-08-30). Every security engineer in the target audience knows this tool. A family called "seatbelts" reads as GhostPack tooling.

npm `seatbelts` is also held as a 0-version reservation since 2016 — free on PyPI, but the family name needs the whole surface.

And the phrase is already spoken for in our category: `ban10yuu/awesome-agent-seatbelts` = "Curated safety, audit, context, and verification tools for AI coding agents."

### 2.5 `graphene-tools` is the hardest kill in the sweep — and no registry would have caught it

`graphene-tools` is **free on PyPI, free on npm, free under `Alex-lop`**. Every status code says yes. It is still unusable:

`graphene` on PyPI is the **GraphQL Framework for Python** (v3.4.3, graphql-python/graphene) with **39,567,514 downloads per month** (`pypistats.org/api/packages/graphene/recent`, 2026-08-30). `graphene-*` is an established third-party plugin namespace — `graphene-django`, `graphene-sqlalchemy`, and `NateScarlet/graphene-django-tools` ★7 sits directly on the candidate name.

`pip install graphene-tools` would be read by essentially the entire Python audience as a GraphQL utility package. The principal's own repo being named Graphene is not a defense; it is the source of the error. **Do not use `graphene-` as a family prefix for anything public.** This is also the standing argument for checking meaning, not only availability.

---

## 3. Recommendations

One name per package. All five are free on PyPI (both spellings), free on npm, free under `Alex-lop`, and clear on `command -v` on this machine as of 2026-08-30.

| # | Package | **Recommended name** | Console script | Import name | Why |
|---|---|---|---|---|---|
| 1 | plan/policy validator | **`agent-plan-lint`** | `agent-plan-lint` | `agent_plan_lint` | Only free name that keeps the descriptive "plan lint" phrase. GitHub `in:name` **total=0**. The `agent-` prefix is honest (it *is* for agent plans) and it avoids the occupied `plan-lint` console script. |
| 2 | MCP egress firewall | **`egresswall`** | `egresswall` | `egresswall` | Free on all four surfaces, GitHub **total=0**, no PATH collision. Keeps "egress" for search while stepping clear of the two live `egress-*guard` packages. |
| 3 | repo guardrail report | **`guardrail-checkup`** | `guardrail-checkup` | `guardrail_checkup` | Free everywhere, GitHub **total=0**. Says what the tool does ("run it, get a report") with zero trademark exposure. Replaces `agent-autopsy` entirely. |
| 4 | read-only MCP gateway | **`readonly-gateway`** | `readonly-gateway` | `readonly_gateway` | Cleanest name in the sweep: 1 unrelated GitHub hit, free on every surface. Stays engine-neutral (SQLite *and* DuckDB), unlike `sqlite-readonly-mcp`. **Use as briefed.** |
| 5 | AI-change receipt | **`change-receipt`** | `change-receipt` | `change_receipt` | Free everywhere; 4 GitHub hits, all ★0, none a Python package. **Use as briefed.** Avoid `git-receipt` — novelty-printer connotation and npm taken. |
| — | Family / docs site | **`guardposts`** | n/a | n/a | Free on PyPI, npm, and `Alex-lop`; GitHub `in:name` **total=0**. Keeps the guard metaphor the packages share without colliding with GhostPack Seatbelt, `graphene-*`, or `provable`. |

**Runners-up, if any recommendation is vetoed:** ① `planfence` (all-clear, total=0, but opaque) · ② `valuewall` (all-clear; names the value-level differentiator) · ③ `repo-checkup` or `agentcheckup` · ④ `readonly-mcp` (freer discovery, busier neighborhood) · ⑤ `changereceipt` · family `bounded-agents` (all-clear, vaguer).

### Naming rules this sweep produced

1. **Never ship a console script named after someone else's console script.** `plan-lint` is taken on PATH by `cirbuk/plan-lint`. Check `[project.scripts]` of any same-category incumbent, not just the distribution name.
2. **Reject near-misses harder than collisions.** `planlint`/`plan-lint` and `egressguard`/`egress-guard` are *available* and *worse than unavailable* — they read as typosquats of live packages doing the same job, and split search traffic while installing something different.
3. **A free name can still be a dead name.** `graphene-tools` passed every registry and fails on meaning (§2.5).
4. **PyPI normalizes, npm does not.** One PyPI check covers `-`/`_`/case. npm needs the literal string — `agent-autopsy` is taken there while `agent_autopsy` is free.

### Registration state

**Nothing was registered.** No PyPI upload, no npm publish, no repo creation, no domain purchase, no account created. Registering names is a `DECIDE-WITH-DEFAULTS` action for the repos (§2) and a `RED`/standing-approval action for PyPI; both belong to the orchestrator and `private/PRINCIPAL.md`, not to this agent.

**Domains: UNVERIFIED.** `dig +short A/NS` returned nothing for `guardposts.dev`, `guardposts.io`, `boundedagents.dev`, `egresswall.dev`, `egresswall.com` (2026-08-30) — absence of DNS is *not* proof a domain is unregistered, and local `whois` on this machine resolved only to the IANA `.dev` record, so registrar availability was not established. This does not block anything: §5's `docs-site-builder` artifact is a **GitHub Pages site on the principal's account**, so `alex-lop.github.io/guardposts` needs no domain and no spend.

---

## 4. Verification appendix

Every status code in this file came from one of these, run 2026-08-30 (UTC 2026-08-31T00:55Z–01:20Z):

```
curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)" -o /dev/null -w '%{http_code}' https://pypi.org/pypi/<name>/json
curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)" -o /dev/null -w '%{http_code}' https://registry.npmjs.org/<name>
gh api repos/Alex-lop/<name>
gh api "search/repositories?q=<name>+in:name&sort=stars&order=desc&per_page=3"
command -v <name>
curl -sS https://pypistats.org/api/packages/<name>/recent
dig +short <domain> A ; dig +short <domain> NS
```

Raw probe outputs (49 names × PyPI+npm, then 22 replacement candidates) are reproducible by re-running the loops above; the name lists are in this file's tables.

**Web sources retrieved 2026-08-30** (used only for the two trademark/well-known-product flags):
- https://www.sleuthkit.org/autopsy/ and https://www.autopsy.com/ — Autopsy® / The Sleuth Kit® registered trademarks held by the tool’s author (an individual, not a company)
- https://github.com/sleuthkit/autopsy — ★3301
- https://github.com/GhostPack/Seatbelt and https://docs.specterops.io/ghostpack-docs/Seatbelt-mdx/overview — Seatbelt, ★4689

**Marked UNVERIFIED:** domain registrability (§3); whether use of any rejected name would legally infringe (§2.3) — that is a lawyer's question, and the recommendations do not depend on the answer.

**No private individual other than the principal is named in this file.** GitHub organization and account names appear only as owners of *public packages and repositories* that constitute the availability evidence.
