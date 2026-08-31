# Metabase-only downstream-impact bot for dbt pull requests

**Slug:** r2-metabase-dbt-impact-bot  |  **Track:** B  |  **Researched:** 2026-08-30  |  **Status:** researched  |  **Origin:** round 2 (asset-suggested)

## One-line pitch
A GitHub bot that reads the SQL diff on a dbt pull request, calls the Metabase API to find every saved question and dashboard that reads the changed columns, and comments "this PR breaks 14 questions on 3 dashboards" — for the 2-20 person data teams on OSS/Starter Metabase who cannot reach Metabase's own dependency graph behind the $575/month Pro tier.

**Verdict up front: DO NOT BUILD.** The exact product — sqlglot column lineage over `manifest.json`, joined to the Metabase API, cards resolved to dashboards, posted as a sticky PR comment with a policy gate — already exists as **[parrant](https://github.com/Fszta/parrant)**, MIT-licensed, free, 78 stars, last pushed **2026-08-28 (two days ago)**, with a first-class `parrant/metabase/` module and a docs page literally titled "Cross-boundary impact (Metabase)". Metabase itself ships both halves natively on Pro. See **Incumbents** and **Verdict**.

## Specific buyer
**Title:** Analytics Engineer / "the one data person" / Head of Data who owns both the dbt repo and the Metabase instance.

**Company size:** 2-20 person data team. dbt Core in GitHub Actions, Snowflake/BigQuery/Postgres, self-hosted OSS Metabase or Metabase Cloud **Starter** ($100/mo). The defining trait: they are *below* the Metabase Pro line ($575/mo), which is where Metabase's own Dependency graph and Dependency diagnostics live.

**Population sizing (quantified):**
- Metabase homepage claim, fetched 2026-08-30: **"Trusted by 100,000+ companies"**. GitHub: **48,992 stars**, 6,777 forks, pushed 2026-08-30 (https://api.github.com/repos/metabase/metabase).
- The dbt ∩ Metabase intersection has a hard proxy: **`dbt-metabase` (gouline) did 120,616 PyPI downloads in the last 30 days** (2,074 last day, 24,267 last week — https://pypistats.org/api/packages/dbt-metabase/recent, fetched 2026-08-30). 610 GitHub stars, last pushed 2026-08-06.
- For scale calibration: `recce` (the funded dbt-PR-review incumbent) did **42,749/month** over the same window; `dbt-core` did **82,400,735/month**. So the dbt+Metabase population is real and roughly **3x the Recce user base by download proxy** — this is *not* a "nobody is there" market. The market exists. It is already served.

**Where they are online:** Metabase Discourse (https://discourse.metabase.com, public, indexable, JSON search API works); `metabase/metabase` GitHub issues (4,453 open); dbt Community Slack (100K+, `#tools-and-integrations`); r/dataengineering (**not verifiable — Reddit 403s every method, see Research log**); HN. **Note: HN is a dead channel for this specific pain** — HN Algolia returns `nbHits: 2` for "metabase dbt lineage" (both are "Ask HN: Who wants to be hired") and `nbHits: 1` for "metabase broke dashboard". All real complaints live on Metabase Discourse and GitHub.

**Boston:** unchanged from b3 — Data Engineering Boston, Boston Data and AI (1,526 members), Analytics.Club Boston are all reachable by T for $0.

## Pain evidence (verbatim, >= 5)

All 12 quotes below were copy-pasted from pages fetched 2026-08-30 via the Discourse JSON API and the GitHub REST API.

1. > "I have a table which is used in a number of questions. **I wish to remove a column from this table in the underlying database. How can I get a complete list of all questions that use this table?** Is there a way to do it using the built in Metabase analytics or can it still only be done using a direct connection to the Metabase DB"
   — Metabase Discourse, "How can I discover which questions a specific table is used in?", https://discourse.metabase.com/t/how-can-i-discover-which-questions-a-specific-table-is-used-in/160110, posted **2024-09-26** by one commenter (Metabase v1.49.22). This is the product's exact use case, stated by the buyer, unprompted. The only answer given was: go query the application database, or use a third-party Neo4j tool.

2. > "My org is looking to retrieve questions contain certain columns. **We have over 4k questions so doing this manually would not be possible.**"
   — Metabase Discourse, "Using Metabase API to find certain columns in questions", https://discourse.metabase.com/t/using-metabase-api-to-find-certain-columns-in-questions/149583, posted **2024-08-22** by one commenter. The community answer (one commenter, 2024-08-25): > "Not really no, I mean you can programatically fetch each card metadata then do the search programatically but **thats gonna be a lot of work**"

3. > "**I have this same problem. I would like to find references to particular columns in questions.** Is the Metabase application db only accessible for self-hosted deployments, or can I access it through the cloud-hosted version?"
   — Same thread, posted **2025-05-13** by one commenter. This is the strongest *segment* signal in the dossier: the app-DB workaround that everyone recommends **does not work on Metabase Cloud**, which is exactly where the paying Starter-tier buyer sits.

4. > "Each question or dashboard should have an available dependency graph, visible in the Metabase GUI. This should include both upstream and downstream dependencies. **Ideally, if there are any dependencies, the UI could warn me before I save any changes.** E.g., 'Are you sure you want to save changes? Updating this question will impact the X dashboard.' **Currently I mitigate this by grouping related questions and dashboards in the same collection** ... so I know that if I update something in a collection, it could impact the others (so I better manually double check them!)"
   — Metabase Discourse, "Dependency graph between datasources <> questions/dashboards", https://discourse.metabase.com/t/dependency-graph-between-datasources-questions-dashboards/15260, posted **2021-06-15** by one commenter. A named manual workaround (folder conventions + manual double-checking) is the cleanest possible statement of the pain.

5. > "The use case is: **identify the impact on a data source we need to change and/or migrate.** Propagate the changes to questions/dashboards."
   — Same thread, posted **2021-06-14** by one commenter. Metabase staff (a Metabase staffer) replied: > "You would have to look in the metadata. **It can get quite complicated to find all tables used.**"

6. > "We use dbt Cloud and Metabase at my company, and while Metabase is great (really love it), we've always had this annoying problem: **it's really hard to know which columns are actually being used in production. This got even worse once we started doing more self-serve analytics.** ... Now we actually know which columns we need to maintain and when we should be careful making changes."
   — Metabase Discourse, "DBT-Metabase Lineage VS Code extension", https://discourse.metabase.com/t/dbt-metabase-lineage-vs-code-extension/290098, posted **2026-01-25** by one commenter. **This person felt the pain badly enough to build and ship the product. See Incumbents — that extension has 100 installs.**

7. ⚠️ VERIFIER: misattributed - the quote, the P1 label, the open state and the 2026-06-30 date are all verbatim-correct, and a Metabase staffer IS Metabase staff (Discourse `admin: true`; 331 PRs to metabase/metabase). But the real name "Metabase staff" is unsupported: the GitHub profile name is "da" and the Discourse profile name is "Dragons Ahead". a second Metabase account is a separate account.
   > "If you make a model, make questions out of it and then modify the model, **you don't get a warning if you're going to break questions that will use the model/field that you modify** ... We should tell the user that it's going to break downstream dependencies (as we track these)"
   — GitHub, `metabase/metabase` issue #76708, "No warning before modifying a model that will break downstream dependencies", https://github.com/metabase/metabase/issues/76708, posted **2026-06-30** by a Metabase staffer (Metabase staff, **Metabase staff**). Labeled `Type:Bug`, **`Priority:P1`**, still **open** on 2026-08-30. Metabase's own staff filed this as a P1 nine weeks ago. Note the parenthetical — *"as we track these"* — Metabase already has the dependency data; only the warning is missing.

8. > "I have a table I need to replace with a different table in all saved queries. **Is there any way to query or search for the queries that reference this table?**"
   — Metabase Discourse, "Finding queries that utilize a specific table", https://discourse.metabase.com/t/finding-queries-that-utilize-a-specific-table/20586, posted **2022-06-14** by one commenter. Staff answer: use the GUI reference section for GUI questions, and for SQL questions > "you would either have to use the search, or **look in the Metabase application database table `report_card`**". A user in the same thread, **2023-04-21** (one commenter): > "Can we make the report_card accessible from within the UI for read-only?" — answered "It's tentatively coming in 47", then **2023-07-21**: > "**It's not coming in v47, might come later**".

9. > "it used to be possible to search for the tables used in SQL questions using the search feature, however **it seems not to be possible anymore.** Is it a bug?"
   — Same thread, posted **2023-10-12** by one commenter. The answer was a link to a third-party Neo4j tool (`paoliniluis/metagraph`).

10. > "When you have a lot of questions **it's easy to lose track where they were referred in, so after doing updates you can forget to check if questions referring to it still works.**"
    — GitHub, `metabase/metabase` issue #13139, "See list of questions where selected question is referred to", https://github.com/metabase/metabase/issues/13139, posted **2020-08-19** by one commenter. **28 reactions, still open after six years.** Sibling issue #13975 ("Show dashboards linked to a question") drew **123 reactions** before Metabase closed it by shipping.

11. > "I need to identify **any tables that aren't currently used by any questions.** ... Problem is that this only returns the tables that are explicitly used in the queries. I also need to identify anything used in the filters or groups. Has anyone managed to do this? **It's all in there somewhere, it's just more work than I expected.**"
    — Metabase Discourse, "Query for tables used in questions", https://discourse.metabase.com/t/query-for-tables-used-in-questions/25022, posted **2023-05-03** by one commenter. This is verbatim demand for the **reverse product** (dead-question / unused-model detection).

12. > "I am working on Housekeeping Project for Metabase which includes **Deleting Dashboard/Charts** ... I realized that deleting the data from repository **might causes of the issue later since it might have a lot of dependency table.**"
    — Metabase Discourse, "Housekeeping process and automation for unused resources", https://discourse.metabase.com/t/housekeeping-process-and-automation-for-unused-resources/153081, posted **2024-09-03** by one commenter. Metabase staff reply, **2024-09-11**: > "**we'll be shipping a cleanup feature very soon**, but in the meantime, try clearing up the entities just going to the application database". They shipped it — see Incumbents.

**Assessment of the pain:** genuinely real, six years continuous (2020→2026), stated by users *and* by Metabase's own staff in a P1 bug. This is not a hallucinated market. The problem is not demand. **The problem is entirely on the supply side.**

## Willingness-to-pay evidence (>= 3)

1. **Metabase prices this exact capability at $575/month.** Metabase Pro is **"$575 / month"** ("$12 per user / month", first 10 users included); Starter is **"$100 / month"** ("$6 per user / month", first 5 included); Open Source is **Free**; Enterprise **"Price starts at $20,000 / year"** (https://www.metabase.com/pricing, fetched 2026-08-30). In the Data Studio docs, **Dependency graph**, **Dependency diagnostics**, **Replace data sources**, **Schema viewer** and **Library** all carry an asterisk footnoted verbatim as: > "\* Available on [Pro and Enterprise plans](https://www.metabase.com/pricing/)." (https://raw.githubusercontent.com/metabase/metabase/master/docs/data-studio/overview.md, fetched 2026-08-30). **The gap between Starter and Pro is $475/month, and dependency tooling is one of the things you cross it for.** That is a large, real, vendor-set price umbrella — the single best WTP number in this dossier.

2. **Adjacent dbt-PR-impact tools sustain $250-300/month at this team size.** Recce: Free **$0** (10 preset checks, 100 agent reviews/mo); Team **$250/month** annual, **$300/month** monthly (unlimited checks, 1,000 agent reviews); Enterprise custom (https://reccehq.com/pricing, fetched 2026-08-30). Paradime sells dbt-adjacent dev tooling at **$20/user/mo** (SPARK) to **$84/user/mo** (VIBE) (https://www.paradime.io/pricing, per b3, 2026-08-30). Datafold's historical anchor is an HN commenter quoting **"$90/m/user is a lot"** (https://news.ycombinator.com/item?id=24075891, 2020-08-06). A $29-49/mo flat price sits far under all of these.

3. **The catalog vendors charge real money and do cover Metabase.** Secoda: three tiers (Core / Premium / Enterprise), **all "contact sales"**, and its integration list reads verbatim > "Secoda integrations with Tableau, Looker, Metabase, Redash, Mode, Sigma, Power BI and Google Data Studio" with > "Secoda automates column and table level data lineage" and > "Secoda works with both dbt Cloud and Core" (https://www.secoda.co/pricing, fetched 2026-08-30). So the *paid* answer for Metabase lineage already exists; it is just sold as a catalog, not a PR bot.

4. **Counter-evidence that must be weighed against all of the above — the self-serve floor for this specific product is $0, and has been tested.** The TraceData "DBT-Metabase Lineage" VS Code extension is **Free**, does exactly this ("Track and visualize how your dbt model columns are used in Metabase dashboards and questions. **Instantly see the impact of schema changes on your BI layer.**"), and has **100 installs** and 2 reviews (https://marketplace.visualstudio.com/items?itemName=TraceData.dbt-metabase-lineage, fetched 2026-08-30) after being announced on Metabase Discourse on 2026-01-25. **A free, exact-fit tool announced to the exact audience seven months ago reached 100 installs.** And `parrant` — the strictly better CI-native version — has done **618 PyPI downloads in 30 days** (https://pypistats.org/api/packages/parrant/recent). Both numbers are an order of magnitude below what a viable paid funnel needs.

**Net WTP read:** the *value* is proven at $475/month of price umbrella. The *price realized by anyone shipping this specific product* is $0, twice, publicly, in 2026.

## Reachability (50 qualified buyers in 30 days, $0)

| Channel | Evidence buyer is there | Play | Realistic yield |
|---|---|---|---|
| **Metabase Discourse** | The 8 threads quoted above; JSON search API is public and works. Threads are low-volume (2-6 posts) but every poster is a self-identified qualified buyer. | Read-only mining to build a named list; answer on-topic technical questions. **Ethics: no product drops in old threads.** | ~30 named individuals identifiable from the threads above alone |
| **`metabase/metabase` GitHub issues** | #13139 (28 reactions, open 6 yrs), #13975 (123 reactions), #5222 (21 reactions), #76708 (P1, open). Reaction lists are public. | Legitimate technical replies where an OSS tool is a real answer. | ~50-150 reaction-identified users across those four issues |
| **dbt Community Slack (100K+)** | `#tools-and-integrations`. | Listening post + warm DMs only; direct promo violates norms. | ~10 warm conversations/month |
| **`dbt-metabase` download base** | 120,616 downloads/month proves the population. But downloads are anonymous — **there is no way to reach these people directly.** | Contribute upstream to `dbt-metabase`; get a README link. | Indirect, slow |
| **Hacker News** | **Weak.** `nbHits: 2` for "metabase dbt lineage", `nbHits: 1` for "metabase broke dashboard". No Show HN in this niche has landed. | One Show HN. | Low confidence; this niche has no HN presence |
| **r/dataengineering** | Cannot verify — Reddit 403s. | — | Unknown |
| **Boston meetups** | Data Engineering Boston, Boston Data and AI (1,526 members), Analytics.Club Boston. | Attend 3-4 in 30 days. | 10-20 conversations, some fraction on Metabase |

**Verdict on reachability: this is the one genuinely strong score in the dossier.** 50 qualified, *named* buyers in 30 days at $0 is clearly achievable — the Discourse threads and GitHub reaction lists alone get most of the way there, and the population is quantified at 120K downloads/month. Reachability is not the reason to kill this.

## Wedge
**The wedge as designed is sound and is exactly what someone else already shipped.** Stating it for the record so the main agent can see how completely it is occupied:

*Free for one repo; $29/month per additional private repo. On every PR touching `models/**/*.sql`: parse the diff with sqlglot, resolve `ref()`/`source()` against `manifest.json` to get column-level lineage, hit the Metabase API to resolve every card down to `schema.table.column`, attach the dashboards each card appears on, and post a sticky PR comment naming the broken questions and dashboards. Reverse product: flag Metabase questions nobody has opened in a year that pin models you cannot delete.*

Compare, verbatim, to `parrant`'s own docs page `docs/decision-engine/metabase.md` (fetched 2026-08-30):

> "dbt lineage stops at dbt's edge. But the question a reviewer actually cares about is one hop further out: **Will this column change break *that dashboard*?** The cross-boundary feature follows impact **past dbt's edge into your BI layer** — from a changed dbt column, through the BI cards that read it, to the dashboards those cards live on ... **Metabase is the first supported BI connector.**"

And its `metabase-extract` CLI:

```
parrant metabase-extract --metabase-url ... --metabase-api-key "$METABASE_API_KEY" \
  --database-id 2 --manifest target/manifest.json --output metabase_lineage.json
parrant impact --metabase metabase_lineage.json --ci     # posts the sticky PR comment
```

This is not a similar product. It is the same product, including the same architectural decisions the brief proposed (sqlglot, `manifest.json`, Metabase API, cards→dashboards, PR comment), plus ones the brief did not (offline zero-credential gate step, MBQL parser, policy gating, incremental snapshots, coverage/staleness honesty). **MIT license. Free. Zero paid tier.**

## Build estimate
**~8-12 agent-days to a sellable MVP** — unchanged from b3, and *not* the constraint here.

Components:
- GitHub App (webhook, checkout, check-run + sticky comment) — ~1 day
- dbt manifest/DAG parse — ~1 day (manifest.json does most of it free)
- sqlglot column-level lineage across Jinja/`select *`/incremental — **~3-4 days for ~85% accuracy** (the hard part)
- Metabase connector: `/api/card` → `dataset_query`, MBQL resolution, native-SQL resolution, card→dashboard join — ~1-2 days
- Comment rendering, force-push dedupe, advisory-only default — ~1 day
- Stripe Checkout + `repo_id → plan` — ~0.5 day

**Technical feasibility is confirmed and unblocked:** Metabase **API keys are available on all plans including Open Source** — only *config-file* key creation is Pro/Enterprise-gated (https://raw.githubusercontent.com/metabase/metabase/master/docs/people-and-groups/api-keys.md, fetched 2026-08-30). Serialization *is* Pro-gated, but this product does not need it. So the build is genuinely possible against free Metabase. That is not the problem.

**Reusable assets: Graphene dag_render; Graft blast-radius design.**

## Unit economics
- **Price:** $29/repo/month flat; free for one repo.
- **LLM cost:** the parse is **deterministic, $0**. Optional summary blurb ≈ **$0.35/repo/month** at Haiku-class pricing.
- **Compute:** shallow clone + parse ≈ 10 CPU-sec/PR; 60 PRs × 50 repos ≈ 8 CPU-hours/month. Fly.io shared-cpu-1x **$5/mo** + Neon/Supabase free tier + domain.
- **Total burn: ~$5-12/month — comfortably inside the $40/month cap.**
- **Gross margin at 10 paying repos ($290 MRR):** ≈ $262, ~90%.
- **Break-even: 1 paying repo.**

The economics are excellent and completely irrelevant, because the denominator is "customers who pay for something available free under MIT."

## Risks

**1. The product already exists, free, MIT-licensed, and shipped 2 days ago. (Fatal.)** `parrant` — https://github.com/Fszta/parrant, 78 stars, created 2025-03-04, **last pushed 2026-08-28**, MIT — contains a first-class `parrant/metabase/` package (`client.py`, `extract.py`, `pmbql.py`, `reach.py`, `resolvers.py`, `warehouse_meta.py`, `join.py`), a dedicated `.github/workflows/metabase-live.yml` CI job, live integration tests (`tests/live/test_metabase_live.py`), and a docs page devoted to Metabase cross-boundary impact. Its own README comparison table reads verbatim: > "**Reaches your BI layer** | dbt docs/DAG: ❌ | **Parrant: ✅ follows impact into Metabase dashboards & cards**". There is no paid tier to undercut and no gap to fill.

**2. Metabase ships both halves natively.** Not "might ship" — shipped, documented, in `master`:
   - **Dependency graph** (Data Studio): > "A visual map of how your content connects, **so you can understand the impact of changes before you make them.**" Tracks Questions, Models, Snippets, Transforms, Metrics, Dashboards, Documents, plus source tables.
   - **Dependency diagnostics** → **Broken dependencies** tab: > "lists items that other content depends on, where a dependent item references a column or field the item no longer provides. **This can happen when a column is removed or renamed**" — showing "**Problems**: Missing columns detected for this item" and "**Broken dependents**: Downstream items that break because they reference those missing columns."
   - **Dependency diagnostics** → **Unreferenced entities** tab: **this is the "dead question detection" reverse product, verbatim** — > "content that nothing else references."
   (https://raw.githubusercontent.com/metabase/metabase/master/docs/monitor/dependency-diagnostics.md and .../docs/data-studio/dependencies/graph.md, both fetched 2026-08-30.)

**3. Metabase is actively closing the last technical gap.** The one thing Metabase's graph does not yet parse is native SQL (issue #71997, open 2026-04-03: "Metabase cannot trace Native SQL dependencies in Data Studio Dependency Graph"). But `metabase/metabase` PR **#68977 "Implement SQLGlot returned-columns via lineage analysis"** (merged, 2026-02-02) and PR **#68752 "[WIP] Use Sqlglot in dependencies"** (2026-01-27) show **Metabase is adopting the identical sqlglot approach in-product, this year.** The remaining differentiator has a visible expiry date.

**4. Metabase is moving into dbt's territory, not away from it.** Metabase now ships **Transforms** — priced on the *Starter* tier at "1,000 included runs" then "$0.01" per run (https://www.metabase.com/pricing, 2026-08-30) — writing query results back to the database and reusing them as sources. Metabase Discourse already has transform-DAG threads (e.g. "Downstream dependent transforms do not wait for upstream transforms to ANALYZE", 2026-05-20). For a 2-20 person team, Metabase Transforms is a credible reason to need *less* dbt, which erodes the intersection this product depends on.

**5. Demand for the free version is already measured and it is small.** The two people who shipped this got **100 VS Code installs** and **618 PyPI downloads/month**. If a free tool cannot pull four figures of users out of a 120K-downloads/month population, a paid one will not pull dozens of paying teams.

**6. Buyer is structurally the cheapest segment in data tooling.** The target is defined as "cannot pay Metabase $575/mo" and "runs dbt Core not dbt Cloud." Selecting for price sensitivity twice, then asking for $29/mo against a free MIT alternative, is adverse selection.

**7. Mild ToS flag (not the reason to kill).** Metabase Cloud hosting terms prohibit using the service or its output > "to train, calibrate, or validate, in whole or in part any other systems, programs or platforms, or for benchmarking, **software-development**, or other competitive purposes" (https://www.metabase.com/license/hosting, fetched 2026-08-30). A customer pointing a tool at their own instance with their own API key is almost certainly fine, and `parrant` operates this way openly. But a commercial product built *on top of* a competitor's API, competing with that competitor's own Pro-tier feature, is not a comfortable place to build a business.

## Kill criteria
These were the tests. **Three of the four failed before any code was written:**

1. ❌ **"Nobody covers Metabase."** — **FALSE.** `parrant` covers Metabase specifically and names it as its first BI connector. Secoda covers Metabase in a paid catalog. The VS Code extension covers it. *(The narrower claim from b3 does survive: Recce's pricing page mentions no BI integration at all, and Euno's mentions only Looker. The dbt-PR-vendors genuinely don't cover Metabase. It just doesn't matter, because an OSS project does.)*
2. ❌ **"Metabase itself does not ship lineage/impact."** — **FALSE.** Dependency graph + Dependency diagnostics (broken *and* unreferenced) ship today on Pro/Enterprise, and sqlglot-based native-SQL parsing is being merged in 2026.
3. ❌ **"The reverse product (dead-question detection) is open."** — **FALSE.** Metabase's "Unreferenced entities" tab is exactly this.
4. ✅ **"The pain is real and recent."** — **TRUE.** Twelve verbatim complaints, 2020-2026, including an open P1 filed by Metabase staff nine weeks ago. This is the only test that passed.

**Additional kill criterion, had it been built:** fewer than 3 paying repos within 60 days of a Show HN. Given 100 installs and 618 downloads for the free versions, this would have been hit.

## Incumbents and adjacent players

| Player | What it is | Price | Covers Metabase? | Verdict |
|---|---|---|---|---|
| **parrant** (Fszta) | **The exact product.** sqlglot column lineage over dbt artifacts → Metabase API → cards → dashboards → sticky PR comment + policy gate. `parrant/metabase/` module, live Metabase CI tests, dedicated docs page. 78 stars, created 2025-03-04, pushed **2026-08-28**. https://github.com/Fszta/parrant | **$0, MIT, no paid tier** | **Yes — first-class, by name** | **Fatal. This is the idea, already built and free.** |
| **Metabase Dependency graph** | Data Studio. "understand the impact of changes before you make them." Questions/Models/Snippets/Transforms/Metrics/Dashboards/Documents + source tables. | **Pro $575/mo+** | Native | Owns the segment above the wedge; expanding down |
| **Metabase Dependency diagnostics** | "Broken dependencies" (missing columns → broken dependents) + **"Unreferenced entities"** | **Pro $575/mo+** | Native | **Ships both the forward and the reverse product** |
| **Metabase sqlglot work** | PR #68977 (merged 2026-02-02), PR #68752 (2026-01-27), issue #71997 (open) | Included | Native | Closing the last native-SQL gap in-product |
| **TraceData VS Code ext** | "Track and visualize how your dbt model columns are used in Metabase dashboards and questions." | **Free** | Yes | **100 installs** — the demand test, already run |
| **dbt-metabase (gouline)** | Syncs dbt→Metabase metadata; extracts Metabase cards/dashboards as **dbt exposures** (`depends_on: ref('orders')`) | **Free, OSS** | Yes | 610 stars, **120,616 downloads/mo**. Feeds parrant. |
| **metagraph (paoliniluis)** | "Insert Metabase entities into Neo4j to analyze dependencies" — the tool Metabase staff link when users ask | **Free, OSS** | Yes | The pre-existing community workaround |
| **Secoda** | Catalog; column-level lineage; dbt Core+Cloud | Contact sales | **Yes, explicitly listed** | The paid answer, sold as a catalog |
| **Recce** | dbt PR review / data diff | Free $0; Team **$250/mo** ann., **$300/mo** monthly | **No BI integration on pricing page** | Adjacent; the b3 gap is real but moot |
| **Euno** | dbt impact analysis + CI | All tiers "request pricing" | **Looker only** | Adjacent, sales-led |
| **Datafold / Metaplane (Datadog) / Elementary / dbt Cloud CLL / SQLMesh** | Per b3, 2026-08-30 | $0 → enterprise | Tableau/Looker/PowerBI/Mode | Adjacent; none serve Metabase; none needs to |

## Score

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Time to first dollar | ×3 | **2** | Code ships in ~2 weeks, but the first dollar requires convincing someone to pay $29/mo for what `parrant` gives away under MIT and what Metabase Pro includes — the two free implementations that already exist got 100 installs and 618 downloads/mo. |
| Reachability by a student | ×3 | **4** | 12 named complainers pulled from public Discourse/GitHub in one session, 100K+ Metabase companies, 120,616 dbt-metabase downloads/month, plus Boston meetups at $0 — 50 qualified named buyers in 30 days is clearly achievable. |
| Pain × frequency | ×2 | **3** | Real and continuous 2020→2026 with an open **P1** filed by Metabase staff (#76708, 2026-06-30) — but episodic (fires on schema changes, not daily) and the Discourse threads are thin (2-6 posts each), which is why free tools satisfy it. |
| WTP evidence | ×2 | **2** | Metabase's own $475/mo Starter→Pro gap proves the *value*; but the realized price for this exact product is **$0 twice publicly in 2026** (parrant MIT, TraceData free), and no one has ever charged for it. |
| Fit with assets and strengths | ×2 | **3** | Graph thinking fits; sqlglot/Metabase API are new. |
| Compounding | ×2 | **2** | A Metabase lineage snapshot is a mild asset, but there is no data network effect, no proprietary corpus, and the OSS competitor already accumulated the same asset with a two-day-old commit. |
| Risk (5 = low) | ×2 | **1** | Highest-risk profile in the round: exact free MIT competitor active this week, the platform vendor ships both halves natively and is merging the same sqlglot approach in-product, and Metabase Transforms is eating the dbt dependency the whole idea rests on. |
| Ceiling | ×1 | **2** | TAM is "dbt Core + OSS/Starter Metabase teams of 2-20 who will pay for what is free" — at $29-49/mo that is low four-figure MRR at absolute best, and the natural upgrade path is *away* to Metabase Pro. |
| Build cost (5 = cheap) | ×1 | **4** | ~8-12 agent-days, $5-12/mo burn, deterministic (near-zero LLM cost), break-even at 1 repo — and `parrant` is MIT, so the hard sqlglot/MBQL work is readable. |

**Subtotal excluding Fit: 40 / 80.**
(TTFD 6 + Reach 12 + Pain 6 + WTP 4 + Compounding 4 + Risk 2 + Ceiling 2 + Build 4)

## Verdict

**KILL. Do not build.**

This idea failed in the most useful possible way: the market research came back *positive* and the competitive research came back *fatal*. The pain is documented across six years and twelve verbatim complaints, including an open P1 bug written by a Metabase employee nine weeks ago. The population is quantified at 120,616 `dbt-metabase` downloads per month. Metabase itself prices the fix at a $475/month tier jump. Every premise in the brief about *demand* held up.

The premise about *supply* did not. The brief's core bet — "every incumbent covers Tableau/Looker/PowerBI/Mode; nobody covers Metabase" — is true of the funded vendors (Recce lists no BI integration; Euno lists only Looker) and irrelevant, because someone reached the identical conclusion first and shipped **parrant**: MIT, free, a dedicated `parrant/metabase/` package with an MBQL parser and live Metabase integration tests, a docs page titled "Cross-boundary impact (Metabase)", and a README table whose "Reaches your BI layer" row reads *"✅ follows impact into Metabase dashboards & cards."* Last commit two days before this research. There is no paid tier to undercut, no missing feature to add, and no pricing wedge to slide into. Meanwhile Metabase Pro ships the forward product (Broken dependencies) *and* the reverse product (Unreferenced entities), and is merging sqlglot into its own dependency engine.

The decisive number is not competitive, though — it is demand-side. Two people built this exact tool for free and gave it to exactly this audience: 100 VS Code installs and 618 PyPI downloads a month. A population of 120K monthly downloads produced a three-figure response to a free, exact-fit solution. That is a pain people complain about on a forum and then work around with a folder-naming convention. It is not a pain they open a wallet for.

**What to carry forward, since the research was not wasted:**
1. **Metabase Discourse is an excellent, under-mined, machine-readable complaint corpus.** `https://discourse.metabase.com/search.json?q=...` works with no auth, returns dated posts with usernames, and produced 9 of the 12 quotes here in minutes. Reusable for any future BI-adjacent idea. Same for the GitHub issues API with `sort=reactions` (issue #13975 at 123 reactions is a demand thermometer nobody is reading).
2. **The "check whether the platform vendor already ships it" step should run before the complaint mining, not after.** Reading `docs/data-studio/overview.md` in the vendor's own GitHub repo — where the tier asterisks are footnoted in plain markdown — took 90 seconds and would have killed this idea at minute five.
3. **`parrant` itself is worth watching, not competing with.** MIT, one maintainer, no commercial tier, a clean architecture, and an explicitly BI-agnostic extractor interface ("adding another BI tool means a new *extractor* that writes the same shape of snapshot"). If Alex wants career capital in this space, contributing a Lightdash or Superset extractor is a far better use of 12 hrs/week than competing with it — visible OSS work on a live tool, zero market risk, and it is the single cheapest way to find out whether anyone in this niche would ever pay for anything.

## Research log

**Method:** read-only. Discourse JSON search + topic APIs, GitHub REST search/issues/contents/raw, PyPI stats API, vendor pricing pages via WebFetch, HN Algolia. No posting, signup, DM, or authenticated access. All quotes copy-pasted from fetched responses. Time spent ≈ 40 agent-minutes.

**Constraints hit:**
- **WebSearch budget exhausted at 200/200 calls at the very start of this task** (session-wide limit, consumed by earlier round-2 agents). All research below was done via direct API/fetch only. This turned out not to matter — the Discourse and GitHub APIs are higher-signal than search for this question — but it is worth flagging for the orchestrator that later agents in a round inherit an empty search budget.
- **reddit.com** — not attempted; 403s every method per the standing brief. r/dataengineering claims are therefore unverified.
- **Indeed** — returned **HTTP 403** to this agent (contradicting the brief's note that Indeed works). No job-posting population sizing was possible; substituted PyPI download counts, which are a better proxy anyway.
- **GitHub code search API** — requires authentication (401 unauthenticated). Substituted the git trees API (`/git/trees/main?recursive=1`) to enumerate `parrant`'s file layout, which is how the `parrant/metabase/` module was found.
- **G2/TrustRadius** — not attempted per standing brief.

**Queries run:**
- HN Algolia: `metabase dbt` (673 hits, all incidental — Who-is-hiring threads); `metabase dbt lineage` (**2 hits**); `metabase broke dashboard` (**1 hit**); `dbt BI impact analysis` (**0 hits**). Conclusion: HN is not a channel for this pain.
- Metabase Discourse `search.json`: `lineage`, `which questions use this table`, `dependencies`, `impact analysis`, `unused questions cleanup`, `broken question column removed`, `find questions using column`, `delete unused dashboards`. Then full topic fetches of ids 20586, 160110, 15260, 25022, 290098, 153081, 149583.
- dbt Discourse `search.json`: `metabase`, `BI dashboard broke`, `exposures metabase` — **essentially empty**; the dbt community does not discuss Metabase impact.
- GitHub issues API on `metabase/metabase`: `lineage in:title` (17), `dependencies in:title` (210, sorted by reactions), `broken questions column` (146), `unused questions in:title` (0). Direct fetches of #76708, #71997, #44310, #13139 (+ comments), #13975, #5222.
- GitHub repos API: `metabase/metabase` (48,992★), `gouline/dbt-metabase` (610★), `Fszta/parrant` (78★, MIT, pushed 2026-08-28). Repo search `metabase dbt lineage` — **this is how parrant was found.**
- Raw GitHub docs: `docs/data-studio/overview.md`, `docs/data-studio/dependencies/graph.md`, `docs/monitor/dependency-diagnostics.md`, `docs/people-and-groups/api-keys.md`, `docs/installation-and-operation/serialization.md`; `Fszta/parrant` README + `docs/decision-engine/metabase.md` + recursive file tree; `gouline/dbt-metabase` README.
- PyPI stats: `dbt-metabase` (120,616/mo), `recce` (42,749/mo), `parrant` (618/mo), `dbt-core` (82,400,735/mo).
- Pricing pages fetched 2026-08-30: metabase.com/pricing, metabase.com (homepage), metabase.com/license/hosting, reccehq.com/pricing, euno.ai/pricing, secoda.co/pricing, marketplace.visualstudio.com (TraceData extension). datafold.com/integrations and docs.datafold.com/integrations/bi both returned **404**.

**Sequence that produced the kill:** GitHub repo search for `metabase dbt lineage` surfaced `Fszta/parrant` (78★) in the same result set as unrelated student projects. Its README comparison table claimed "follows impact into Metabase dashboards & cards," which could have meant dbt-exposure-based coverage. The recursive git tree then showed a full `parrant/metabase/` package including `pmbql.py` and `client.py`, plus `.github/workflows/metabase-live.yml` — proving direct Metabase API integration, not exposures. `docs/decision-engine/metabase.md` confirmed the complete two-step architecture. Independently, `docs/data-studio/overview.md` in Metabase's own repo showed Dependency graph and Dependency diagnostics footnoted "\* Available on Pro and Enterprise plans," and `dependency-diagnostics.md` showed the "Unreferenced entities" tab — killing the reverse product too.

**Not verified / open questions:** r/dataengineering sentiment (Reddit blocked). Whether `parrant` has any paying users or commercial intent (no pricing page, no sponsor link, MIT). Whether the TraceData VS Code extension's 100 installs reflect low demand or low distribution effort. Exact Metabase OSS-vs-Cloud split among dbt users (the 100K+ company figure is not broken down by tier).

## Verification (2026-08-30, adversarial pass)
- Quotes: 34 checked, 33 verified, 0 unfetchable, 1 misattributed (quote 7's "Metabase staff" real-name attribution; the quote text, P1 label, open state, date and "Metabase staff" are all correct)
- Claims:
  - **parrant exists as described** — CONFIRMED. `https://api.github.com/repos/Fszta/parrant`: 78★, 7 forks, MIT, created 2025-03-04, pushed 2026-08-28. Git tree confirms `parrant/metabase/{client,extract,pmbql,reach,resolvers,warehouse_meta,join,artifact,cli}.py`, `.github/workflows/metabase-live.yml`, `tests/live/test_metabase_live.py`, `docs/decision-engine/metabase.md`. README lines 87/96/117 confirm `--ci` posts a **sticky PR comment**, and `action.yml` exists (HTTP 200). The dossier's docs quote is verbatim.
  - **…but parrant's Metabase connector is SEVEN DAYS OLD** — the dossier omits this. Every commit touching the Metabase code is 2026-08-23→2026-08-27; the first is `feat: cross-boundary impact into BI dashboards (Metabase connector)`, 2026-08-23T09:57:24Z (`/commits?path=dbt_column_lineage/metabase`, n=2; `?path=parrant/metabase`, n=11). Solo maintainer (1 contributor, 410 commits), v0.19.0, 3 watchers, no FUNDING.yml. It has **zero distribution to this audience**: `discourse.metabase.com/search.json?q=parrant` → 0 topics, 0 posts; no HN post.
  - **"parrant: 618 PyPI downloads in 30 days" (Risk 5, WTP 4, Verdict)** — REFUTED as a demand test. `https://pypistats.org/api/packages/parrant/recent` returns `last_week: 618, last_month: 618` — identical, because the package was renamed from `dbt_column_lineage` on 2026-08-23 and its first release under the name `parrant` is v0.17.1, 2026-08-23T18:54:29 (`pypi.org/pypi/parrant/json`, 5 releases, all 2026-08-23→08-27). It is 7 days of downloads for a week-old package name, not a 30-day demand measurement. (The old name `dbt-column-lineage` does 310/mo.)
  - **"TraceData VS Code extension = a free, exact-fit tool announced to the exact audience"** — REFUTED for the target segment. Its own author states on the quoted Discourse thread (topic 290098, 2026-01-25, full post): > "For Metabase, you'll need **the serialization API enabled**". Serialization is Pro/Enterprise-gated (`docs/installation-and-operation/serialization.md` carries `{% include plans-blockquote.html feature="Serialization" %}`) — a fact the dossier itself states in Build estimate but never connects. So the 100 installs measure demand among **Pro/Enterprise** customers who already have Dependency graph, not among the OSS/Starter buyer the dossier defines. Extension metadata otherwise confirmed: 100 installs, 2 reviews, v0.5.6, updated 2026-08-18, description verbatim. Also closed-source ("The source code of the extension is not open source unfortunately.").
  - **Metabase pricing** — CONFIRMED (metabase.com/pricing, fetched 2026-08-30): OSS Free; Starter "$100 … $6 per user / month"; Pro "$575 … $12 per user / month"; Enterprise "Price starts at $20,000 / year". Transforms: "You get 1,000 included runs on Starter and Pro. After 1,000, each run costs $0.01". (A promo strikethrough of $90 / $517.50 is live today; list prices as quoted.)
  - **Metabase ships both halves, Pro-gated** — CONFIRMED but narrower than stated. `docs/data-studio/overview.md` L25/L30 verbatim; `docs/monitor/dependency-diagnostics.md` "Broken dependencies" verbatim; `docs/data-studio/dependencies/graph.md` entity list exact. All of it is Pro/Enterprise ($575/mo) — i.e. **it does not ship to the buyer this dossier defines**.
  - **Kill criterion 3 ("reverse product is closed")** — REFUTED. The dossier's own reverse product is *"questions **nobody has opened in a year**"* (usage-based). Metabase's Unreferenced entities is reference-based only: > "shows items that aren't used by any other non-archived content" and > "An unreferenced item isn't broken and isn't automatically safe to delete… Check [Usage analytics] for view activity before you archive or delete an item." And Usage analytics is *itself* Pro/Enterprise-gated (`usage-and-performance-tools/usage-analytics.md`, plans-blockquote). Not "exactly this", and not available below Pro.
  - **GitHub issue set** — CONFIRMED via `gh api`: #76708 open, `Priority:P1`, 2026-06-30, body verbatim; #13139 open, 28 reactions, 2020-08-19, body verbatim; #13975 **closed 2026-06-09**, 123 reactions; #5222 open since 2017-05-30, 21 reactions; #71997 open 2026-04-03; PR #68977 **merged 2026-02-03**; PR #68752 **closed unmerged**. Repo: 48,992★, 6,777 forks, pushed 2026-08-30 (open issues 4,452, dossier said 4,453 — moving number).
  - **All 12 pain quotes** — CONFIRMED verbatim against `discourse.metabase.com/t/{id}.json` and the GitHub issues API, including usernames and dates. Recce ($0 / $250 annual / $300 monthly, no BI integration named), Secoda (3 tiers, all contact-sales, Metabase named), Metabase homepage "Trusted by 100,000+ companies", the hosting-terms restriction clause, and the Datafold HN comment ("$90/m/user is a *lot*", GordonS, 2020-08-06) all verified verbatim. `dbt-metabase` 120,616/mo, `recce` 42,749/mo, `dbt-core` 82,400,735/mo all confirmed. The research log's own claim that the WebSearch budget was exhausted at 200/200 is confirmed — it is still exhausted.
- Score challenges:
  - **WTP evidence 2 → 3.** Both pillars of the "$0 realized price, twice, publicly" argument are broken: TraceData requires a Pro-only API so it never reached the target segment, and parrant's 618 is one week of a renamed package. No one has actually run a demand test on OSS/Starter Metabase teams. The $475/mo Starter→Pro umbrella is still the real number, and it is now the *only* number.
  - **Risk (5 = low) 1 → 2.** "Exact free MIT competitor active this week" is true but the connector is 7 days old, pre-1.0, one contributor, 78★, 3 watchers, never announced to Metabase Discourse or HN. That is a project to watch, not an incumbent that has taken the segment. The genuinely fatal element — MIT and free, so there is no price to charge — survives untouched and is enough on its own; the "already lost the market" framing is not supported.
  - **Kill criterion 2 is unmeasurable as written.** "Metabase itself does not ship lineage/impact" cannot test a wedge whose entire premise is *below the Pro line* — it fires on a feature the defined buyer cannot buy. It should have read "…ships it on OSS or Starter."
  - **Kill criterion 1 is binary on existence, not on price or distribution.** It fires on any GitHub repo. The criterion that actually mattered — "someone offers this free under a permissive license" — is the one that fired, and it deserves to be stated that way.
  - **Kill criterion 3 flips ❌ → ✅** per the Unreferenced-entities evidence above. Two of four, not three of four, genuinely failed.
- Missing:
  - **DataHub (Apache-2.0) and OpenMetadata both ship free Metabase ingestion connectors** and are absent from the incumbent table. DataHub's own source README: "It also captures **table-level** lineage" — i.e. not column-level, so it does not strengthen the kill, but a free catalog with a Metabase connector belongs in the table.
  - **Usage analytics is Pro-gated** — never checked, and it is the half of the reverse product Metabase does *not* fold into Unreferenced entities.
  - **dbt v2 / Fusion is not mentioned once.** docs.getdbt.com: "dbt Core 2.x: dbt Core 2.0, the free, fully open-source (Apache 2.0) distribution of the new Rust-based dbt engine." TraceData already advertises "Works with dbt Core, Fusion, and Cloud." The build plan's hard part ("sqlglot column-level lineage … ~3-4 days for ~85% accuracy") is estimated as if the dbt engine of 2026 were static.
  - **parrant's CI action needs `catalog.json` for both base and head branches** (`action.yml` inputs `catalog` + `base-catalog`), i.e. `dbt docs generate` against the warehouse on two branches. The dossier praises the "offline, zero-credential" gate without noting the artifact-production cost that precedes it — a real adoption gap, though not a business.
  - **The ToS flag applies only to Metabase Cloud.** metabase.com/license/hosting governs the hosted Subscription Services; self-hosted OSS Metabase — most of the defined segment — is not bound by it. The dossier treats the risk as segment-wide.
  - **#5222 ("Archiving a question removes it from all dashboards without notifying the user", 21 reactions) is still open since 2017-05-30** while #13975 was closed 2026-06-09. The still-open vein is the *silent-breakage-on-archive* one, not the dashboards-list one.
- Overall: **mostly-trustworthy** - every quote and every price is verbatim-accurate and the KILL is correct, but it is correct for exactly one reason (a free MIT tool means there is no price to charge), and the three supporting pillars the dossier stacks on top of it — "the demand test has already been run", "Metabase ships both halves", "the reverse product is closed" — are each materially overstated once you check that TraceData needs a Pro-only API, that parrant's 618 downloads are seven days old, and that Unreferenced entities is reference-based and Pro-gated.


## Final score (main agent, 2026-08-30)
- Fit with assets and strengths: **3/5** ×2 — Graph thinking fits; sqlglot/Metabase API are new.
- Reusable assets: Graphene dag_render; Graft blast-radius design.
- Subtotal as researched: 40/80 · after adversarial verification: **44/80** (wtp 2→3, risk 1→2)
- **Total: 50/90**
