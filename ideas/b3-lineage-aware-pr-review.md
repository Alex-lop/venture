# Lineage-aware PR review for SQL and dbt

**Slug:** b3-lineage-aware-pr-review  |  **Track:** B  |  **Researched:** 2026-08-30  |  **Status:** researched

## One-line pitch
A free GitHub App that reads the SQL/dbt diff on every PR and comments with the exact blast radius — which downstream models, which BI dashboards, and which columns actually break — for small teams who run dbt Core in GitHub Actions and cannot afford an enterprise catalog.

## Specific buyer
**Title:** Analytics Engineer / Data Engineer / "the one data person", often the person who owns both the dbt repo and the BI instance. Sometimes a Head of Data at a 30-200 person company.

**Company size:** 2-20 person data team, dbt Core (not dbt Platform Enterprise), GitHub Actions for CI, Snowflake/BigQuery/Postgres/Databricks, Metabase / Looker / Lightdash / Mode / Power BI on top.

**Where they hang out online:**
- r/dataengineering — ~200K members (per [PainOnSocial's 2026 subreddit roundup](https://painonsocial.com/subreddits/data-engineers)). **Note: Reddit is not machine-fetchable for this research — see Research log.**
- dbt Community Slack — "over 100,000 members" per [getdbt.com/community](https://www.getdbt.com/community). Channels `#dbt-core-development`, `#tools-and-integrations`, `#advice-dbt-for-*`. Strict anti-promo norms.
- dbt Discourse — https://discourse.getdbt.com (public, indexable, low traffic now).
- GitHub issue threads on `dbt-labs/dbt-core` — the highest-signal complaint venue found (see Pain evidence; dbt Labs staff write the complaints for their users).
- Hacker News — every launch in this space gets a Show HN / Launch HN (Datafold 189 pts, Metaplane 163 pts, Nao Labs 158 pts, Grai 101 pts, Zingle 9 pts).
- Locally Optimistic Slack (analytics leadership community), DataTalks.Club Slack.
- LinkedIn: "Analytics Engineering" and "Modern Data Stack" groups; dbt Labs' own content orbit.

**Where they hang out offline / Boston:**
- [Data Engineering Boston](https://www.meetup.com/data-engineering-boston/) and [Boston Data and AI](https://www.meetup.com/boston-data-and-ai/) (1,526 members) on Meetup.
- [Analytics.Club Boston](https://www.meetup.com/ac-bos/).
- Databricks Boston User Group (meets in the Seaport, per community.databricks.com).
- Snowflake Boston User Group; Data Council (the Nao founders demoed there — HN comment 43940458).
- Boston is dense in the exact ICP: Toast, Klaviyo, Wayfair, HubSpot, Drift, CarGurus, Flywire, Chewy Boston, plus hundreds of Series A/B SaaS companies with a 3-8 person data team. Alex can physically attend the above meetups at $0 and demo on a laptop.

## Pain evidence (verbatim, >= 5)

1. ⚠️ VERIFIER: date_wrong - > "There are many scenarios where executing `dbt list --select state:modified` over or under selects the appropriate resources. This leads to: - confusion "why are these models selected as `state:modified`, I haven't changed them" - performance concerns "why am I running 60 models when I only changed 2" - potentially bad code sneaking it's way into production "i checked my changes using a Slim CI job, but these models weren't run, now production is broken""
   — dbt-core GitHub, [Epic] state:modified should Actually (only) select the modified resources, https://github.com/dbt-labs/dbt-core/issues/9562, posted 2024-02-13. Written by `graciegoheen`, a **dbt Labs product manager**, summarizing user reports. Still open as of 2026-08-30.

2. > "This worked great until the project grew in complexity and the `@` operator started creating enormous graphs. Our CI checks started to run hundreds of models on small changes. Even though the queries were processing 0 rows the checks were taking ~10 minutes in total. ... This worked as advertised but the problem was that even if our CI check went from running 300 models to 20 -- the tables in prod now had millions of records in them so the run time of the actual models increased. Also we are using snowflake so this would represent an unreasonable use of our Snowflake credits."
   — dbt-core GitHub, [Feature] "Slim CI" but with `LIMIT 0`, https://github.com/dbt-labs/dbt-core/issues/4201, posted 2021-11-03. Written by `jsnb-devoted`, a practitioner at Devoted Health building their own dbt CI. Same issue closes with: > "Most of what we hope to check with CI is "column level lineage" -- namely that you can't delete a field from a model that is being referenced 10 levels downstream"

3. > "Job runtime goes from minutes to hours; we cancel before completion ... Offline comparison of defer baseline vs current-run manifest shows **0 model checksum diffs**, **0 seed checksum diffs**, and **0 new nodes** — yet all 5 seeds and a large downstream graph still run."
   — dbt-core GitHub, [v2 Bug] state:modified+ false positives ... (dbt Cloud), https://github.com/dbt-labs/dbt-core/issues/15231, posted 2026-06-10. Written by `ajmatison`, a paying dbt Cloud (Fusion Stable, Snowflake) customer running a ~409-model project. **This is 11 weeks old — the pain is current, not historical.**

4. > "In the context of running slim CI Job build with deferral enabled and `state:modified+` selector, the job will consider all the models modified when models are materialized to different `database` compared to the deferred environment. ... Development CI Job starts and build **all** the models since database (and schema) is considered to be modified"
   — dbt-core GitHub, [BUG] State modified is not ignoring database config in CI Jobs, https://github.com/dbt-labs/dbt-core/issues/14235, posted 2026-02-09. Written by `leevilehtonen`, running dbt Fusion `2.0.0-preview.108` on dbt Cloud.

5. > "A variant of **Slim CI to the max:** being able to do an impact analysis at _development time_ when you're changing a source / model's column name. After all, the fact that a column changes _does not necessarily mean_ that the column also **used** in any dependent models. For that, you really need column level lineage."
   — dbt-core GitHub, Column level lineage, https://github.com/dbt-labs/dbt-core/issues/3226#issuecomment-826807137, posted 2021-04-26 by `bashyroger`, a practitioner. The dbt Labs response in the same thread (jtcohen6, 2021-04-08) names the same use case: > "**Slim CI to the max:** If you've only changed one column across a few models, rather than running the changed models and _all_ their children, you'd only need to run + test downstream models that use the affected column." **Five years later this is still Enterprise-only in dbt (see WTP table).**

6. > "Most of us are still juggling multiple tools: writing code in Cursor, checking results in the warehouse console, troubleshooting with an observability tool, and verifying in BI tool no dashboard broke."
   — Launch HN: Nao Labs (YC X25) – Cursor for Data, https://news.ycombinator.com/item?id=43938607, posted 2025-05-09 by ClaireGz, co-founder. 158 points. The manual "go check the BI tool" step is stated as the default workflow.

7. > "Senior data engineers had very limited time to review PRs, and with AI-assisted coding the amount of code being written each day grew a lot. This left teams choosing between two costly outcomes: let PRs through with minimal review and risk warehouse cost spikes or broken pipelines, or slow everything down with long review cycles. ... we shipped a PR that triggered repeated full refreshes on a large model and it turned into a $50k Snowflake bill."
   — Show HN: Zingle – an AI code reviewer for data teams (SQL/dbt/Airflow/Spark), https://news.ycombinator.com/item?id=45931748, posted 2025-11-14 by UvrajSB, co-founder, describing 60+ dbt PRs/week at an enterprise client. **Only 9 points; getzingle.com today (fetched 2026-08-30) no longer sells PR review — it sells "AI agents that build production-grade data pipelines." They pivoted off this exact wedge within ~9 months.** That is negative evidence and it matters.

8. > "Early in my career, as an on-call data engineer at Lyft, I accidentally introduced a breaking code change while attempting to ship a hotfix at 4AM to a SQL job that computed tables for core business analytics. A seemingly small change in filtering logic ended up corrupting data for [core business analytics]"
   — Launch HN: Datafold (YC S20) – Diff Tool for SQL Databases, https://news.ycombinator.com/item?id=24071955, posted 2020-08-06 by hichkaker (Gleb Mezhanskiy, founder/ex-Lyft). 189 points.

9. > "Analysts with 1-2 years experience in SQL are often writing ETL. Responsible Data Engineers can't be there every time they deploy to production. ... Yes, you can write your own tools for SQL QA. Making a standard tool that the entire company can and does use is another story."
   — HN comment, https://news.ycombinator.com/item?id=24074176, posted 2020-08-06 by `forrestb`. Describes exactly the 2-20 person team dynamic (junior analysts merging SQL, no senior gate).

## Willingness-to-pay evidence (>= 3)

| Competitor / substitute | Pricing (exact, URL, date seen) | Who it serves | Gap vs. this idea |
|---|---|---|---|
| **dbt platform (dbt Labs)** | Developer **$0** (1 seat, 3,000 models/mo, 1 project); Starter **$100 per user/month** (5 seats, 15,000 models/mo, 1 project); Enterprise & Enterprise+ custom. https://www.getdbt.com/pricing, seen 2026-08-30. **Column-level lineage: "dbt platform \| Enterprise, Enterprise+" — "CLL is available to all dbt Enterprise plans that can use Catalog."** https://docs.getdbt.com/docs/collaborate/column-level-lineage, seen 2026-08-30. | Everyone on dbt. | CLL and Catalog are Enterprise-gated. A 5-person team on Starter ($500/mo) still cannot get column-level blast radius, and gets **zero** BI-tool lineage. This is the single clearest gap. |
| **Recce (RecceHQ)** — *the direct competitor* | Free **$0** (10 preset checks, 100 agent reviews/mo, automated CI validation & PR comments, LLM insights); Team **$250/month** annual / **$300/month** regular (unlimited preset checks, 1,000 agent reviews/mo, **unlimited seats**); Enterprise contact us. https://reccehq.com/pricing, seen 2026-08-30. OSS: https://github.com/DataRecce/recce, 476 stars, last push 2026-08-28. | dbt teams doing PR review. Tagline is literally "the data-validation toolkit for enhanced dbt PR review." | **This is the idea, already shipped, already free at the entry tier, already flat-priced at unlimited seats.** Recce is data-diff-first (needs a dev warehouse env + credentials); a purely static, credential-free parse is the only differentiation left, and it is thin. |
| **Datafold** | Public pricing **removed** — /pricing redirects to /contact-us as of 2026-08-30. Wayback 2025-05-17 snapshot: "Datafold's customized pricing is based on the number of users and tables being monitored and tested, and is generally purchased by data teams as a comprehensive platform." http://web.archive.org/web/20250517100331/https://www.datafold.com/pricing. Historical anchor: an HN commenter in the 2020 Launch HN quoted **"$90/m/user is a lot"** — https://news.ycombinator.com/item?id=24075891, 2020-08-06. Ships CI data diff, downstream impact analysis, column-level lineage into Tableau/Looker/Power BI/Mode/Hightouch. | Mid-market → enterprise. Sales-led. | Proves the WTP number ($90/user/mo, 6 years ago) **and** proves the segment abandonment: they moved from public pricing to "call us." Nobody self-serve is left except Recce. |
| **Paradime** | Code IDE: SPARK **$20/user/mo**, FLOW **$44/user/mo**, VIBE **$84/user/mo**; Bolt (deploy) **starts at $180/user/mo**; Radar (FinOps) **starts at $899/month**. https://www.paradime.io/pricing, seen 2026-08-30. | dbt teams that find dbt Cloud too expensive. | Validates that **$20/seat/month is a real, live price point for a dbt-adjacent developer tool sold to this exact buyer.** This is the strongest direct support for the brief's $20/seat wedge. |
| **Metaplane (now Datadog)** | Free **$0** (10 monitored tables, 4 users); Pro **usage-based, pay per monitored table** (12 users, unlimited viewers) — includes "Column-level Lineage" and **"Data CI/CD — Prevent data quality issues in PRs"**; Enterprise custom. https://www.metaplane.dev/pricing, seen 2026-08-30. Banner: "Metaplane and Datadog join forces." | SMB → mid-market data teams. | Ships the PR impact comment already, has a free tier, and now has Datadog's distribution and balance sheet behind it. |
| **Euno** | "REQUEST PRICING" / "BOOK A DEMO" at every tier; priced per *resource* (up to 150K / 1.5M / any scale), **unlimited users**. Feature matrix explicitly lists **"Impact analysis (CI integration): Automatically detect and/or block changes that could affect downstream dependencies before merge."** https://www.euno.ai/pricing, seen 2026-08-30. | Mid-market/enterprise with Looker/Tableau. | Exact feature parity on the core promise; sales-led, so leaves the self-serve floor open — but also signals the floor may not be worth much. |
| **Elementary** | Every tier is **"Talk to us."** Scale (≤10 editor seats, ≤1K tables), Enterprise (≤20 editors, ≤40 viewers, ≤3K tables), Unlimited. Column-level lineage listed in all tiers. https://www.elementary-data.com/pricing, seen 2026-08-30. OSS: 2,402 stars. | dbt-native observability, SMB→enterprise. | Started OSS/self-serve, now fully sales-led. Same abandonment pattern as Datafold. |
| **Sifflet / Atlan (free GitHub Actions)** | The **action** is free on GitHub Marketplace; it calls the vendor's lineage API, so it requires a paid Sifflet/Atlan catalog. https://github.com/marketplace/actions/sifflet-dbt-impact-analysis-action and https://github.com/atlanhq/atlan-action, seen 2026-08-30. | Enterprise catalog customers. | The PR-comment UX is already commoditized and given away as a loss leader by catalog vendors. |
| **Free OSS substitutes** | dbt-checkpoint (764 stars, pre-commit hooks for dbt quality, https://github.com/dbt-labs/dbt-checkpoint... actually dbt-checkpoint/dbt-checkpoint, last push 2026-08-17); SQLMesh (3,260 stars, ships column-level lineage + plan/diff natively, https://github.com/SQLMesh/sqlmesh); DBT-Metabase Lineage VS Code extension (free, https://marketplace.visualstudio.com/items?itemName=TraceData.dbt-metabase-lineage). | Everyone, $0. | The floor is genuinely $0 and well-populated. |
| **Manual cost being paid today** | Analytics Engineer average total pay **$156,418/yr** (Glassdoor, 2026, https://www.glassdoor.com/Salaries/analytics-engineer-salary-SRCH_KO0,18.htm, seen 2026-08-30). At 2,080 hrs and a 1.3x fully-loaded multiplier ≈ **$98/hr**. Assume 1.5 hrs/week per engineer spent tracing "what does this touch?" plus one broken-dashboard fire drill per month at 3 hrs: ≈ 114 hrs/yr ≈ **$11,200/yr per analytics engineer**. A 5-person team ≈ **$56K/yr** of the pain. Plus the Zingle-quoted **$50K Snowflake bill** tail risk. | — | The pain is worth 100x a $20/seat price. **The problem is not value, it is that eight vendors already offer to capture it and two of them offer it free.** |

## Reachability (50 qualified buyers in 30 days, $0)

| Channel | Evidence of buyer presence | Play |
|---|---|---|
| GitHub code search for public dbt repos | `path:dbt_project.yml` returns tens of thousands of public repos; many are company repos with real CI. | Install-free "audit": run the parser offline against a public repo, open **nothing** (no PR, no issue — per ethics), and DM/email the maintainer via their public contact with a link to a hosted report. Realistically 100+ qualified targets identified in a week. |
| Hacker News Show HN | Direct comps: Datafold 189 pts, Metaplane 163, Nao 158, Grai 101, SQLMesh 29, Zingle 9. Median for a working data-tooling Show HN is ~20-150 pts. | One Show HN with a live public-repo demo. Historically converts to 10-40 signups for tools in this niche. Free, one shot, non-repeatable. |
| r/dataengineering (~200K members) | See buyer section. Note: could not be verified first-hand — Reddit blocks this agent's fetcher. | A "I parsed 500 public dbt repos and here's how many PRs would have broken a dashboard" data post. Genuinely reachable but the sub is hostile to launches; lead with the dataset, not the product. |
| dbt Community Slack (100K+) | https://www.getdbt.com/community, seen 2026-08-30. | Answer questions in `#advice-*` channels for 3 weeks first. Direct promo is against norms and will get the account removed — treat as a listening post plus warm-DM source, not a launch channel. |
| dbt-core GitHub issue threads | Issues #3226, #4201, #9562 have engaged practitioners who self-identified with this exact pain. | Public, on-topic technical replies (not ads) on open issues where an OSS tool is a legitimate answer. ~30 named, self-selected people across those threads. |
| **Boston, in person** | Data Engineering Boston, Boston Data and AI (1,526 members), Analytics.Club Boston, Databricks Boston User Group (Seaport). | Attend 3-4 meetups in 30 days, 10-20 conversations each. This is Alex's strongest asymmetric channel and costs $0 + a T ride. Boston's SaaS density (Toast, Klaviyo, HubSpot, CarGurus, Flywire, Drift) means the ICP is physically in the room. |

**Verdict on reachability:** 50 qualified buyers in 30 days at $0 is realistic. 50 *installs* is plausible with a genuinely free OSS tier. 50 *paying* is not.

## Wedge
**The smallest thing one buyer pays for this month:**

A GitHub App, free for public repos and for one private repo, that on every PR touching `models/**/*.sql`:
1. Parses the diff with `sqlglot` (no warehouse credentials, no dbt run, no data access — this is the differentiator vs. Recce/Datafold, both of which need a dev warehouse env),
2. Resolves `ref()`/`source()` against the repo to build the model DAG **and** does column-level resolution on the changed models,
3. Reads the **Metabase / Lightdash / Looker** API (read-only, user-supplied token) to map each affected column to the specific saved questions and dashboards that select it,
4. Comments: *"This PR drops `orders.total_conversions`. 7 downstream models and 3 Metabase dashboards reference it: [Exec Weekly — card 412], [Growth — card 88], [Finance MRR — card 201]. Suggested `dbt test` additions: …"*

**What one buyer pays for THIS month:** the private-repo tier at **$29/repo/month** flat (not per seat — Recce and Euno have both proven flat/unlimited-seat is the norm here, and a 5-person team will not do seat math for a bot). The paid feature that unlocks the wallet is **the BI half** — the model-to-model half is free in dbt Core's manifest and free in Recce; "which *dashboard* breaks" is the part that no free tool gives a Metabase/Lightdash shop.

## Build estimate
**~8-12 agent-days to a sellable MVP.**

Components:
- GitHub App: webhook receiver, PR checkout, check-run + comment API. (~1 day; well-trodden, Probot or raw FastAPI.)
- dbt project parser: read `dbt_project.yml`, `models/**`, `manifest.json` if committed; resolve `ref()`/`source()` graph. (~1 day — `dbt-core`'s own parse or hand-rolled Jinja regex; the manifest, when present, does this for free.)
- Column-level resolution with `sqlglot` (`sqlglot.lineage`, Apache-2.0, handles ~25 dialects). This is the hard part and the accuracy risk: Jinja macros, `select *`, dynamic column lists, incremental logic. (~3-4 days for something that is right ~85% of the time.)
- BI connectors: Metabase `/api/card` (`dataset_query` contains table + field refs) ~1 day; Lightdash ~1 day; Looker (`lookml_model_explore`) ~2 days. Ship Metabase first — it is the modal BI tool at this company size and nobody serves it.
- Comment rendering, dedupe on force-push, "advisory only, never block" default (an HN commenter on the Zingle thread specifically asked for this: > "I don't love tools that block PRs automatically. Can this run in advisory mode only?" — https://news.ycombinator.com/item?id=45937229, 2025-11-15). (~1 day.)
- Billing: Stripe Checkout + a `repo_id → plan` table. (~0.5 day.)

**Reusable assets: Graphene ui/dag_render.py for impact rendering; Graft blast-radius design as reference; sqlglot (OSS) for lineage.**

## Unit economics
- **Price:** $29/repo/month flat (free tier: public repos + 1 private repo).
- **Model/API cost per customer per month:** The core parse is **deterministic — $0 LLM cost.** Only the optional "suggested tests" blurb calls a model. Assume 60 PRs/month/repo × ~4K input + 600 output tokens on a small model ≈ 240K in / 36K out ≈ **$0.35/month/repo** at Haiku-class pricing. Even at Sonnet-class it is under $3.
- **Compute:** each PR is a shallow clone + a parse. ~10 CPU-seconds. 60 PRs × 50 repos = 3,000 runs/mo ≈ 8 CPU-hours. **Fly.io shared-cpu-1x, $5/mo**, or Cloudflare Workers free tier for the webhook + a $5 worker for the parse.
- **Hosting total:** ~$5-12/mo (app + Postgres on Neon/Supabase free tier + a domain). **Comfortably inside the $40/mo burn cap.**
- **Gross margin at 10 paying repos ($290 MRR):** ~$290 − $12 hosting − $4 LLM − ~$12 Stripe fees ≈ **$262, ~90%.**
- **Break-even: 1 paying repo.** That is the one genuinely attractive number in this dossier.

## Risks

**1. Incumbent saturation — the dominant risk.** At least nine shipping products deliver "PR comment with downstream impact" today: Recce (free tier + $250/mo, OSS, 476 stars, pushed 2026-08-28), Metaplane ("Data CI/CD — Prevent data quality issues in PRs," free tier, now Datadog), Euno ("Impact analysis (CI integration): Automatically detect and/or block changes that could affect downstream dependencies before merge"), Datafold ("Downstream impact analysis," "Automatically run a data diff when a PR opens"), Sifflet and Atlan (free GitHub Actions on paid catalogs), Foundational, Select Star, SQLMesh (native CLL, free, 3,260 stars). **Recce alone is a near-exact substitute with a free tier.**

**2. Platform dependency on dbt Labs — and the Fusion squeeze.** dbt Core v2 shipped 2026-06 on a Rust engine; the roadmap states "advanced SQL comprehension, linting, and column-level lineage" are "(available in Fusion only)" (https://github.com/dbt-labs/dbt-core/blob/main/docs/roadmap/2026-06-announcing-v2.md). Fusion is free-with-`dbt login`. dbt Labs is one product decision away from putting CLL-in-CI in the free tier and vaporizing the wedge — and they have been publicly planning it since 2021 ("Slim CI to the max", jtcohen6, issue #3226). Also note dbt Labs merged with Fivetran (Oct 2025, https://news.ycombinator.com/item?id=45570948), which increases, not decreases, their incentive to bundle.

**3. Negative precedent: someone tried this exact pitch and left.** Zingle launched "an AI code reviewer for data teams" on HN 2025-11-14 with a lineage graph engine, downstream dashboard tracing, and a free tier. It got 9 points. By 2026-08-30 getzingle.com sells "AI agents that build production-grade data pipelines" — the PR-review framing is gone from their homepage. Either the wedge did not monetize or it did not differentiate.

**4. Accuracy liability.** A blast-radius comment that says "safe to merge" and is wrong is worse than no comment. `sqlglot` lineage breaks on `select *`, Jinja macros, dynamic SQL, and warehouse-specific functions. dbt Labs' own PM wrote of the analogous failure: > "i checked my changes using a Slim CI job, but these models weren't run, now production is broken" (issue #9562). Mitigation: advisory-only, never block, always say "N columns unresolved" rather than implying completeness. This limits liability but also limits perceived value.

**5. Security / trust for a solo student vendor.** The product needs a GitHub App with repo read and a read-only BI API token. A 5-person data team at a Series B company will ask for SOC 2. Datafold, Elementary, and Foundational all lead with "SOC 2 Type II" / "no access to your data from the Cloud." Mitigation: **run entirely as a GitHub Action inside the customer's own CI** (no code leaves their infra) and sell the hosted dashboard as the upsell. This is also the honest answer to why a student can compete here at all.

**6. Legal:** Low. Reading a customer's own repo under an installed GitHub App and their own BI API with their own token is unambiguously consented. `sqlglot` is Apache-2.0. No scraping, no third-party data. Public-repo demo reports use only public data.

## Kill criteria
Pick one lane and hold the number:

- **By 2026-11-15 (10 weeks):** **100 GitHub App installs OR 250 GitHub stars on the OSS core.** If under 40 installs, the free tier is not differentiated from Recce and the OSS distribution thesis is dead — stop.
- **By 2026-12-15 (~15 weeks):** **5 paying repos at $29/mo ($145 MRR).** If under 3, kill.
- **Earliest signal, by 2026-09-30 (30 days):** **15 replies from 60 outreach conversations** (meetups + public-repo maintainer emails + HN) that say "yes, we manually check the BI tool before merging and we don't pay for a tool that does it." If under 8, kill before writing the parser.

## Incumbents and adjacent players
- **Recce / RecceHQ** — "the data-validation toolkit for enhanced dbt PR review"; OSS 476★; Free / $250-300 per month, unlimited seats. https://reccehq.com/pricing, https://github.com/DataRecce/recce — **the direct competitor.**
- **dbt platform (dbt Labs)** — CI jobs, Slim CI / `state:modified`, dbt Catalog, column-level lineage (Enterprise only). $0 / $100 per user/mo / custom. https://www.getdbt.com/pricing
- **dbt Fusion engine / dbt Core v2** — Rust engine, full SQL comprehension, CLL in Fusion. Free with login, Apache-2.0 core. https://www.getdbt.com/product/fusion
- **Datafold** — CI data diff, downstream impact analysis, column-level lineage into Tableau/Looker/Power BI/Mode. Call-us pricing. https://www.datafold.com/
- **SQLMesh / Tobiko Data** — OSS 3,260★, native column-level lineage and plan/diff; dbt-compatible. Tobiko Cloud pricing page 404s as of 2026-08-30. https://github.com/SQLMesh/sqlmesh
- **Elementary** — dbt-native observability, OSS 2,402★, Cloud all "Talk to us." https://www.elementary-data.com/pricing
- **Metaplane (Datadog)** — "Data CI/CD — Prevent data quality issues in PRs," free tier, usage-based Pro. https://www.metaplane.dev/pricing
- **Euno** — column-level lineage, "Impact analysis (CI integration)" that can block merges; per-resource pricing, unlimited users, request-pricing. https://www.euno.ai/pricing
- **Foundational** — cross-platform lineage, impact analysis, "secure automated code review and validation process"; form-gated pricing. https://www.foundational.io/pricing
- **Select Star** — catalog + column-level lineage + MCP server; no public pricing. https://www.selectstar.com/pricing
- **Sifflet** — free GitHub Action posting downstream impact as a PR comment, backed by paid Sifflet lineage API. https://github.com/marketplace/actions/sifflet-dbt-impact-analysis-action
- **Atlan** — `atlanhq/atlan-action`, free Action, downstream lineage impact in PRs, backed by paid Atlan catalog. https://github.com/atlanhq/atlan-action
- **Nao Labs (YC X25)** — AI code editor for data with column lineage and downstream-impact suggestions in the IDE. 158 pts on HN. https://getnao.io/
- **Zingle** — launched as "AI code reviewer for data teams (SQL/dbt/Airflow/Spark)" 2025-11; homepage now sells pipeline-building agents. https://getzingle.com
- **Paradime** — dbt IDE + deploy, $20/$44/$84 per user/mo. Price anchor for this buyer. https://www.paradime.io/pricing
- **dbt-checkpoint** — free pre-commit hooks for dbt project quality, 764★. https://github.com/dbt-checkpoint/dbt-checkpoint
- **Lightdash** — dbt-native BI; Cloud Pro **$3,000/month**, no per-seat. A potential *integration partner*, not a competitor. https://www.lightdash.com/pricing
- **DBT-Metabase Lineage** — free VS Code extension mapping dbt columns to Metabase cards. The Metabase gap is smaller than it looks. https://marketplace.visualstudio.com/items?itemName=TraceData.dbt-metabase-lineage
- **Grai** — OSS data observability / lineage, 101 pts HN 2023. https://news.ycombinator.com/item?id=36758122

## Score

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Time to first dollar | ×3 | **2** | The category's free floor is well populated (Recce free tier, Metaplane free tier, Atlan/Sifflet free Actions, dbt-checkpoint, SQLMesh) so a paid tier must clear a high "why not the free one" bar; data tooling also requires a security conversation before a private-repo install, and no self-serve comp in this space converts in under ~6 weeks. |
| Reachability by a student | ×3 | **4** | ~200K in r/dataengineering, 100K+ in dbt Slack, a live Show HN channel with 100-190pt precedents, self-identified complainers in three public dbt-core issue threads, plus four Boston meetups (Data Engineering Boston, Boston Data and AI at 1,526 members, Analytics.Club Boston, Databricks Boston User Group) that Alex can attend for free — 50 qualified conversations in 30 days is genuinely achievable. |
| Pain × frequency | ×2 | **5** | dbt Labs' own PM documents users saying "now production is broken" (issue #9562, still open), the false-positive `state:modified` bug is 11 weeks old and current (#15231, 2026-06-10), and the pain fires on **every single PR** — Zingle's client shipped 60 dbt PRs/week. |
| WTP evidence | ×2 | **3** | Real prices exist for this exact buyer (Paradime $20-84/user/mo, Recce $250-300/mo, dbt Starter $100/user/mo, Datafold historically $90/user/mo) and the manual cost is ~$11K/yr per analytics engineer — but the 2-20 person segment is precisely the one Datafold and Elementary abandoned for "call us," and an HN commenter on the Datafold launch said outright "outside of enterprise I just can't see anyone paying that." |
| **Fit with assets and strengths** | ×2 | **TBD** | Filled by the main agent from the Phase 0 asset inventory. |
| Compounding | ×2 | **3** | Dialect coverage, BI-connector coverage, and GitHub stars all compound, and a public-repo lineage corpus would be a real moat — but there is no data network effect (every customer's graph is private) and no community lock-in that Recce and SQLMesh have not already built with 476 and 3,260 stars. |
| Risk (5 = low) | ×2 | **2** | Nine shipping competitors including a free-tier near-clone (Recce), a platform owner (dbt Labs/Fivetran) that has publicly wanted "Slim CI to the max" since 2021 and now has a Rust engine that does full SQL comprehension, an acquirer with distribution (Datadog/Metaplane), and a documented case (Zingle) of a funded team pivoting off this exact pitch inside 9 months. |
| Ceiling | ×1 | **3** | The category supports real revenue (Datafold, Metaplane, Elementary all VC-scale), but the *self-serve small-team slice* that is actually open is worth maybe $5-20K MRR solo before the enterprise motion — which Alex cannot run — becomes the only way up. |
| Build cost (5 = cheap) | ×1 | **4** | `sqlglot` (Apache-2.0) does dialect-aware column lineage for free, dbt's `manifest.json` supplies the model DAG, Metabase's `/api/card` exposes field refs, and the GitHub App shell is a day — ~8-12 agent-days total, with the only genuinely hard part being Jinja/`select *` resolution accuracy. |

**Subtotal excluding Fit: 51 / 80.**
(TTFD 6 + Reach 12 + Pain 10 + WTP 6 + Compounding 6 + Risk 4 + Ceiling 3 + Build 4.)
With Fit at 5/5 the total would be 61/90; with Fit at 3/5, 57/90.

## Verdict
The pain is real, current, and expensive — better documented than almost anything else a student could research, because dbt Labs' own product managers write the complaints down in public GitHub issues and leave them open for five years. A 5-person team on dbt Core genuinely cannot get column-level blast radius without paying dbt Enterprise or a catalog vendor, and they genuinely do open Metabase by hand before merging. The build is cheap (~8-12 agent-days), the LLM cost is near zero because the core is a deterministic parse, and hosting fits in $12/month, so break-even is one customer. But the market is the most crowded of any idea in this plan: Recce ships this exact product with a free tier and $250/mo unlimited seats, Metaplane ships it inside Datadog, Euno and Datafold and Foundational and Select Star all ship it upmarket, Atlan and Sifflet give the PR comment away free as catalog loss-leaders, SQLMesh does column-level lineage natively for free, and dbt Labs' Fusion engine now does full SQL comprehension in a Rust runtime with a roadmap entry that has wanted "Slim CI to the max" since 2021. Most damning: Zingle launched precisely this pitch on HN in November 2025 with a lineage engine and a free tier, got 9 points, and had pivoted to selling pipeline-building agents within nine months. The only genuinely open crack is the **BI half for cheap BI tools** — nobody serves "which *Metabase* question breaks" to a team that will not buy a catalog — and that crack is narrow enough that it may be a feature, not a company. **Recommendation: do not build this as a business. Consider it only as a 3-4 agent-day free OSS GitHub Action, published to build career capital and a data-community audience, with the 30-day kill gate at 15 replies from 60 conversations — and if those replies come back strong and specifically about Metabase/Lightdash, revisit.** Alex's scarce resource is hours, and this idea asks him to spend them out-competing nine funded teams on their home turf.

## Research log
**Time spent:** ~75 agent-minutes.

**Queries run**
- HN Algolia API: `dbt CI`, `broke downstream dashboard`, `dbt slim ci`, `column level lineage`, `datafold`. Full-thread pulls on items 45931748 (Zingle), 43938607 (Nao Labs), 24071955 (Datafold Launch HN), 34603050 (Ask HN: How do you test SQL?).
- `gh api search/issues` on `dbt-labs/dbt-core` for `"slim ci"`; full bodies + comments on issues 9562, 15231, 14235, 4201, 3226, 10002, 9548, 10138.
- `gh api repos/*` for star counts and last-push dates on DataRecce/recce, elementary-data/elementary, SQLMesh/sqlmesh, datafold/data-diff, dbt-checkpoint/dbt-checkpoint, sqlfluff/sqlfluff, tconbeer/sqlfmt.
- Pricing pages fetched live 2026-08-30: getdbt.com/pricing, reccehq.com/pricing (via 301 from datarecce.io/pricing), datafold.com/pricing (redirects to /contact-us), elementary-data.com/pricing, paradime.io/pricing, metaplane.dev/pricing, euno.ai/pricing, foundational.io/pricing, selectstar.com/pricing, lightdash.com/pricing, tobikodata.com/pricing (**404**).
- Wayback via `curl`: `archive.org/wayback/available` + `web/20250517100331/datafold.com/pricing` and `web/20230601000000/datafold.com/pricing`.
- WebSearch: dbt Fusion CLL licensing; dbt CLL plan availability (docs.getdbt.com); GitHub Marketplace dbt PR impact actions; Metabase↔dbt lineage tools; analytics engineer salary (Glassdoor 2026); Boston data meetups; r/dataengineering and dbt Slack sizes.
- AWS Marketplace dbt Platform review pages (G2 + PeerSpot syndicated), page 14 — 10 full reviews read.

**Sources that were most useful**
1. `dbt-labs/dbt-core` GitHub issues — by far the best complaint source in this niche. Verbatim, dated, attributable, and dbt Labs staff summarize user pain in their own words. Issues #9562 and #4201 are the two load-bearing citations.
2. HN Algolia item API (`/api/v1/items/<id>`) returns full comment trees as JSON — much better than fetching HN pages. Yielded the Datafold $90/user/mo price anchor and the Zingle $50K-Snowflake-bill story.
3. Live pricing pages via `curl` + a 20-line HTML stripper. Faster and more complete than WebFetch for marketing sites.
4. Wayback via raw `curl` (WebFetch is blocked on web.archive.org, `curl` is not).

**Dead ends**
- **Reddit is completely unavailable to this agent.** `curl` to `reddit.com/r/*/search.json` and `old.reddit.com` both return the HTML shell, not JSON. WebFetch returns "Claude Code is unable to fetch from www.reddit.com." WebSearch with `allowed_domains: reddit.com` returns HTTP 400 ("domains are not accessible to our user agent"). Pushshift returns 307. **No r/dataengineering quote in this dossier is first-hand, so none is included** — the member count is cited from a third-party roundup and flagged as unverified. This is a real gap in the pain evidence and the main agent should treat r/dataengineering sentiment as unconfirmed.
- G2 (`g2.com/products/datafold/reviews`) returns HTTP 403. Worked around partially via AWS Marketplace, which syndicates G2 and PeerSpot reviews for dbt — but those reviews are 4.7★ average and contain almost no CI/lineage complaints (the top gripes are UI clutter and YAML verbosity), so they were low-yield.
- dbt Discourse search returned only 2 results for "slim ci slow," both from 2021. The forum appears largely superseded by the Slack and by GitHub issues.
- `tobikodata.com/pricing` and `/pricing.html` both 404 — Tobiko Cloud has no public price as of 2026-08-30.
- Generic GitHub issue search for `"broke downstream" dbt` returned recency-sorted noise (auto-generated repos), not complaints. Repo-scoped search on `dbt-labs/dbt-core` was the productive form.

## Verification (2026-08-30, adversarial pass)
- Quotes: 17 checked, 16 verified, 0 unfetchable, 1 not found/altered (1 date_wrong: Pain #1 quote text is verbatim, but the attribution line's "Still open as of 2026-08-30" is false — dbt-core #9562 was closed 2024-11-25T17:54:06Z per `api.github.com/repos/dbt-labs/dbt-core/issues/9562`. That "still open" framing is reused in the Pain×frequency score justification.)
- Claims:
  - **Recce pricing/OSS** — CONFIRMED exactly. Free $0 / Team $300 monthly, $250 annual / unlimited seats / Enterprise contact us; 476★, pushed 2026-08-28, Apache-2.0. https://reccehq.com/pricing + api.github.com/repos/DataRecce/recce
  - **dbt pricing + CLL Enterprise-gating** — CONFIRMED verbatim, both quoted strings ("dbt platform | Enterprise, Enterprise+", "CLL is available to all dbt Enterprise plans that can use Catalog"). https://www.getdbt.com/pricing, https://docs.getdbt.com/docs/collaborate/column-level-lineage
  - **dbt-core v2 roadmap "(available in Fusion only) like advanced SQL comprehension, linting, and column-level lineage"** — CONFIRMED verbatim, line 116. https://raw.githubusercontent.com/dbt-labs/dbt-core/main/docs/roadmap/2026-06-announcing-v2.md
  - **Paradime $20/$44/$84, Bolt $180, Radar $899** — CONFIRMED, but the dossier's read is wrong. Bolt's own feature list says "Column-level lineage diff for every pull request" and "Cross-platform lineage between dbt™ models and Looker, Tableau, or ThoughtSpot". Paradime is a **competitor on the exact wedge**, not merely a "$20/seat price anchor". https://www.paradime.io/pricing
  - **Star counts (SQLMesh 3,260 / Elementary 2,402 / dbt-checkpoint 764)** — CONFIRMED, all three exact. GitHub API.
  - **`sqlglot` is Apache-2.0** — REFUTED. sqlglot is **MIT** ("MIT License, Copyright (c) 2026 Toby Mao"). Stated three times, including inside the Legal risk. Practically harmless (both permissive) but it is a legal-section factual error. https://raw.githubusercontent.com/tobymao/sqlglot/main/LICENSE
  - **r/dataengineering "~200K members" per PainOnSocial** — REFUTED by the dossier's own cited source, which says **174K**. https://painonsocial.com/subreddits/data-engineers
  - **Zingle pivot** — CONFIRMED. Homepage now reads "AI agents for analysts to build production-grade data pipelines," backed by Accel and Nexus. https://getzingle.com
  - **Datafold pricing removed / Elementary all "Talk to us" / Euno "Impact analysis (CI integration)…before merge" / Metaplane free-4-users + Pro CLL + Data CI/CD / Lightdash Cloud Pro $3,000 / tobikodata.com/pricing 404** — ALL CONFIRMED, Euno string verbatim. Respective /pricing pages.
  - **Glassdoor Analytics Engineer $156,418** — CONFIRMED (page reads $156,436 today; Glassdoor drifts daily).
  - **"dbt Labs merged with Fivetran (Oct 2025), news.ycombinator.com/item?id=45570948"** — PARTLY. The merger is real and now **closed** (dbt Labs' own v2 roadmap links "Fivetran and dbt are one company now"), which strengthens Risk 2 — but item 45570948 is a *comment*, not the story. The story is 45568842 (117 pts, 2025-10-13).
  - **"Boston Data and AI (1,526 members)"** — PARTLY: 1,653 members today. https://www.meetup.com/boston-data-and-ai/
- Score challenges:
  - **Reachability 4 → 3.** Three of the four Boston channels do not do what's claimed. Data Engineering Boston's last event was **2024-12-04** (dormant ~21 months). Analytics.Club Boston's entire 2026 calendar is *global virtual* networking/job events, not Boston in-person. Only Boston Data and AI is live, and its 2026 topics are RAG/agents/lakehouse, not dbt or analytics engineering. Add the 174K-vs-200K subreddit inflation and the "asymmetric Boston advantage" is one meetup with an off-ICP agenda.
  - **Risk 2 → 1.** The dossier names its own sole differentiator: "a purely static, credential-free parse is the only differentiation left." That product already ships free. **`Fszta/parrant`** (MIT, 78★, pushed 2026-08-28, `pip install parrant`, ships `action.yml`): "reads only your dbt artifacts… parses the compiled SQL statically with sqlglot… never connects to your warehouse and never runs dbt," and posts a column-level blast-radius verdict comment on every PR. Add Paradime Bolt shipping "column-level lineage diff for every pull request" plus dbt→Looker/Tableau lineage. The count is not nine competitors, it is eleven, and one of them is the MVP.
  - **WTP 3 → 2.** Paradime is called "the strongest direct support for the brief's $20/seat wedge," but $20/user buys an AI IDE; the PR-lineage feature sits in **Bolt at $180/user/mo**. It is not evidence anyone pays $20 for a lineage bot. Meanwhile the one shipped product doing the dossier's exact paid differentiator — DBT-Metabase Lineage, dbt columns → Metabase cards — has **100 installs**. The dossier read that as "the Metabase gap is smaller than it looks"; the sharper read is that the BI half has measured near-zero demand.
  - **Compounding 3 → 2.** The free static-CLL lane is already occupied (parrant MIT, `b-ned/dbt-colibri` 293★), and the free catalog lane the dossier never mentions is enormous: **DataHub 12,617★** and **OpenMetadata 15,030★**, both Apache-2.0, both self-hostable, both with dbt *and* Metabase/Looker connectors. There is no star-count or corpus advantage left to accrete.
  - **Pain 5 → 4.** Pain is real, but two of the five dbt-core citations are resolved (#9562 closed 2024-11-25, #14235 closed 2026-03-13), and the two genuinely current ones (#15231, #14235) are **dbt Cloud / Fusion deferral** bugs hitting paying dbt Cloud customers — not the "dbt Core in GitHub Actions, cannot afford enterprise" ICP the dossier targets. The evidence is strong but partly aimed at a different buyer.
  - **Kill criteria — one is unmeasurable.** "100 installs **OR** 250 GitHub stars" mixes an orthogonal, game-able vanity metric into a revenue gate, and the fail line ("under 40 installs") leaves the entire 40–99 band with no defined action. The 30-day gate is also a leading question ("yes, we manually check the BI tool…") that will over-collect agreement. The $145-MRR gate is the only clean one.
- Missing:
  - **`Fszta/parrant`** (MIT, 78★, active) — the dossier's MVP, already built and free, with a GitHub Action. Not mentioned anywhere. This alone should have changed the Wedge section.
  - **`b-ned/dbt-colibri`** (293★) — free Python column-level-lineage extractor for dbt from `manifest.json`.
  - **DataHub (12,617★)** and **OpenMetadata (15,030★)** — the two largest free OSS catalogs, both with dbt + Metabase/Looker lineage. The dossier's "free OSS substitutes" row lists three minor tools and misses the two obvious ones.
  - **Paradime as competitor, not anchor** — Bolt ships per-PR column-level lineage diff and cross-platform BI lineage.
  - **`AltimateAI/altimate-code`** (803★, MIT, created 2026-02) — fast-growing OSS agentic dbt harness in the adjacent lane.
  - **The Metabase-lineage demand signal (100 installs)** — read as a demand fact rather than a competitive one, this is the strongest single argument against the paid wedge and the dossier under-weights it.
  - Reddit remains unverified (correctly flagged), but the dossier's own source contradicts its member count.
- Overall: **mostly-trustworthy** — quotes are near-perfectly verbatim and every price checked reproduced exactly, but the dossier carries one false status claim that feeds a score (#9562 "still open"), an inflated subreddit figure contradicted by its own citation, a license error in the legal section, and it missed the free MIT tool that already is its wedge — all of which push in the same direction as its own "do not build" verdict, only harder.


## Final score (main agent, 2026-08-30)
- Fit with assets and strengths: **3/5** ×2 — Graph/lineage thinking and GitHub-check plumbing are familiar (Graphene, Graft fluency); SQL/dbt parsing is new.
- Reusable assets: Graphene ui/dag_render.py for impact rendering; Graft blast-radius design as reference; sqlglot (OSS) for lineage.
- Subtotal as researched: 51/80 · after adversarial verification: **40/80** (risk 2→1, reach 4→3, wtp 3→2, comp 3→2, pain 5→4)
- **Total: 46/90**
