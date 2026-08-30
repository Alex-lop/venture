# Third-party API Change Watchdog Mapped to Your Code

**Slug:** b5-api-change-watchdog  |  **Track:** B  |  **Researched:** 2026-08-30  |  **Status:** researched

## One-line pitch
Watch the changelogs, OpenAPI specs and deprecation notices of the external APIs a team depends on, then tell them the one thing every existing tool refuses to tell them: which files and lines in *their* repo break, and open the upgrade PR.

## Specific buyer
**Title:** Founding engineer / lead backend engineer / CTO at a 3-30 person product company whose product is mostly glue between external APIs — Stripe + Shopify + Twilio + Plaid + an LLM provider + a shipping carrier. Also: Shopify/Amazon-marketplace app vendors, whose apps get delisted if they fall behind a version (Shopify delists apps still on unsupported APIs on 2026-04-01, per https://shopify.dev/docs/api/usage/versioning).

**Where they are online:**
- Hacker News (`Ask HN`/`Show HN`), lobste.rs
- Shopify Developer Community Forums — https://community.shopify.dev (active daily; the deprecation threads cited below are from there)
- OpenAI Developer Community — https://community.openai.com/c/api/34 (the 2026 model-shutdown thread ran April to August 2026)
- GitHub issue trackers of vendor SDKs: `Shopify/shopify-app-js`, `amzn/selling-partner-api-models`, `stripe/stripe-node`, `google-gemini/*`
- r/ExperiencedDevs, r/webdev, r/shopifyDev, r/SaaS — **note:** Reddit disabled unauthenticated `.json` endpoints in 2026, both `curl` and WebFetch returned 403/blocked during this research, so Reddit is now a read-with-a-browser-only channel and not automatable within ToS-friendly limits.
- Indie Hackers, dev.to (`#api` tag — the competing `APIWatch` newsletter markets there)
- Vendor Slack/Discords: Shopify Partners, Stripe Developers, Plaid, Vercel, Supabase

**Offline / Boston:**
- Boston New Technology (BNT) monthly demo nights, https://www.bostonnewtechnology.com
- Startup Boston Week (September, free/cheap tickets), https://www.startupbostonweek.com
- Boston API/Backend and Boston Software Crafters meetups on Meetup.com
- MassChallenge and Cambridge Innovation Center (One Broadway, Kendall) — dense concentration of 5-30 person SaaS teams, 20 minutes from Northeastern on the Red/Orange line
- Northeastern's own co-op employer network: hundreds of Boston SaaS companies who already hire NEU students and will take a meeting from one

## Pain evidence (verbatim, >= 5)

1. > "Recently worked on a project where our team used 10+ third-party APIs. Twice this year we got hit by silent breaking changes and found out only when users complained."
   — Ask HN: "How do you handle breaking changes from third-party APIs in production?", user `kriish2205`, https://news.ycombinator.com/item?id=47538731, posted 2026-03-27. Developer on a team integrating 10+ APIs. **Note the signal cuts both ways: the post scored 1 point and received 0 replies.**

2. > "For approximately one month (late January through February 27), our AI features ran without any grounding. Every part recommendation, every spec search — generated purely from the model's pre-trained knowledge. The corrupted data accumulated in our database and was served to B2B customers. We had no idea."
   > "On February 27, I noticed recommendations weren't matching real datasheets. What followed was 16 hours of debugging — 63 Git commits, 13 different approaches. I rewrote prompts, rebuilt the search pipeline, changed configurations, adjusted timeouts, switched between parallel and sequential calls. Nothing worked, because the problem was never in my code."
   — `takibboinz`, "Gemini-flash-latest silently broke Search grounding for 1 month", https://news.ycombinator.com/item?id=47271099, posted 2026-03-06. Founder of PartsplanAI, a B2B electronic-components marketplace (small team). Same post: *"The changelog entry for January 21 reads only: 'gemini-flash-latest alias now points to gemini-3-flash-preview'. No mention of grounding regression. No compatibility warning."*

3. > "The anonymized buyer email (`xxxxx@marketplace.amazon.com`) was previously returned by default in the Orders API v0 `getOrders` and `getOrder` responses without requiring a Restricted Data Token (RDT) or any restricted roles. This field has been silently removed from the response with no deprecation notice."
   — GitHub issue `amzn/selling-partner-api-models` #5131, https://github.com/amzn/selling-partner-api-models/issues/5131, opened 2026-02-12. Amazon marketplace-app integrator; issue is still open and assigned to an Amazon engineer.

4. > "I'm facing an issue where the deprecation alert persists, even though I migrated to version 2024-04 several weeks ago. The alert consistently appears at 12:00 AM, and I cannot identify where the deprecated API call is being made."
   — `BigVan`, Shopify Developer Community Forums, "Deprecated API calls", https://community.shopify.dev/t/deprecated-api-calls/6169, posted 2025-01-27, 8:37am. Shopify app developer. **This is the single most on-thesis quote found: the vendor's own alert fired and the developer still could not find the call site. That gap is exactly the product.**

5. > "we don't make any API calls to the products or variants endpoints anywhere in our app."
   — `kartik-stoq`, Shopify Developer Community Forums, "Sudden API deprecation warning for old version", https://community.shopify.dev/t/sudden-api-deprecation-warning-for-old-version/23827, posted 2025-10-13, 4:07pm. Engineer at Stoq (Shopify app vendor). Same thread, `sandy-stoq`, 2025-10-13, 3:13pm: *"Can anyone from Shopify take a look at this? We're seeing a 2024-07 API deprecation warning banner for one of our apps, but we're already on 2025-04."*

6. > "This is terrible news. I strongly urge you not to shut down these legacy models, especially the finetuned ones that many of us spent disproportionate amounts of time tweaking to our needs."
   — `MarkusAntonuis`, OpenAI Developer Community, "Deprecation notice: upcoming model shutdowns in 2026", https://community.openai.com/t/deprecation-notice-upcoming-model-shutdowns-in-2026/1379553, posted 2026-04-23, 3:06am.

7. > "This is a ridiculous list of models and super fast. Seems to me this will make me move to Mistral, Chinese or OS stable models first than doing finetuning again with OpenAI."
   — `nikola.k`, same OpenAI thread, https://community.openai.com/t/deprecation-notice-upcoming-model-shutdowns-in-2026/1379553, posted 2026-04-23, 6:04am.

8. > "gpt-4o-mini-tts-2025-03-20 was supposesdly depreciated on July 23rd but it's still works."
   — `ltnew007`, same OpenAI thread, posted 2026-08-01, 7:08pm. Illustrates the inverse failure: vendors' own published dates are unreliable in both directions.

9. > "All node.js examples in the Documentation are still showing client.query()"
   — `Kevin-Hamilton`, GitHub issue `Shopify/shopify-app-js` #2928 ("graphql query method throws FeatureDeprecatedError exception"), https://github.com/Shopify/shopify-app-js/issues/2928, comment posted 2026-07-16 (issue opened 2025-11-12). The issue body asks that *"Deprecation of graphql client.query should be extended OR error message should be more helpful AND documentation should be updated."* A Shopify staffer replied 2025-11-18: *"Sorry that this mislead you."* Nine months later the docs were still wrong.

10. > "Many (most?) APIs don't provide RSS feeds, sometimes they provide RSS that they block from fetching (yes, this happens!), or provide API updates on JavaScript-heavy pages, and so many other crazy things. So, I had to use other ways to track changelogs and documentation updates."
    — `kull`, "Show HN: API Changelog Tracker" (apipulse.app), https://news.ycombinator.com/item?id=47766479, posted 2026-04-14. Founder/solo dev. Direct evidence that the *ingestion* half is genuinely hard and therefore a real moat — and evidence that a competitor already solved it.

11. > "Built this because I kept finding API changes after something had already broken."
    — `skyatday`, Show HN for Varen (varen.dev), https://news.ycombinator.com/item?id=47604426, posted 2026-04-01. Solo founder; covers "100+ APIs".

12. > "The problem was always the same: remove or change an endpoint, deploy, and a few hours later customers email saying their integrations broke."
    — `PeterDS`, "Show HN: API Impact Tracker", https://news.ycombinator.com/item?id=46579637, posted 2026-01-11. This is the *producer* side of the same pain (your API breaking your clients) and is a distinct, possibly better-monetized market.

**Counter-evidence I am obliged to report:** every one of the 2026 posts in this exact space died on arrival. HN 47538731 (Ask HN, 2026-03-27): 1 point, 0 comments. HN 47766479 (apiPulse, 2026-04-14): 2 points, 0 comments. HN 47271099 (Gemini grounding, 2026-03-06): 2 points, 0 comments. HN 48339989 (API drift guide, 2026-05-30): 4 points, 0 comments. HN 48773957 (Seismograph, 2026-07-03): 1 point, 0 comments. HN 42843790 (Shopify deprecation strategy, 2025-01-27): 2 points, 1 comment. The dev.to "Every Major API Deprecation in February 2026" post has 0 comments. Developers experience this pain but do not gather around it, do not upvote it, and do not evangelize solutions to it.

## Willingness-to-pay evidence (>= 3)

| Competitor / substitute | Pricing (exact, URL, date seen) | Who it serves | Gap vs. this idea |
|---|---|---|---|
| **FlareCanary** | Free $0 (5 endpoints, daily); **Starter $19/mo** (25 endpoints, hourly); **Pro $49/mo** (100 endpoints, 15-min); **Startup $199/mo** (250); **Enterprise $499/mo** (500). https://www.flarecanary.com/ seen 2026-08-30 | Teams depending on third-party services and AI-agent dependencies; also monitors MCP server tool definitions | Polls live endpoints and diffs schemas against a learned baseline. **Already occupies the exact $49/month price point in the brief.** Does not read your repo, does not name call sites, does not open PRs. |
| **apiPulse** (apipulse.app) | Basic **Free** (5 API subscriptions, daily); **PRO $4.20/mo** (20 subscriptions, instant); Enterprise custom. 1-month free trial, no card. https://apipulse.app/ seen 2026-08-30 | Solo devs and small teams tracking Stripe, Shopify, Twilio, Claude, HubSpot, Amazon SP-API, FedEx/UPS, TikTok Shop, etc. | **This is the brutal price anchor.** The changelog-watching half of the brief retails for $4.20/month today. Anything Alex charges above that has to be justified entirely by the code-mapping half. |
| **ApiNotes** (apinotes.io) | Starter **$0/mo**; Developer **$6.99/mo**. https://apinotes.io/ seen 2026-08-30. Tagline: *"Your API changelog writes itself"* | API producers (docs, mock servers, validator) — but it also publishes a **free** directory of 50+ public API changelogs rebuilt daily from vendor OpenAPI specs | Gives the consumer-side changelog corpus away for free as a marketing asset. Competes with the wedge at a price of zero. |
| **Bump.sh** | From **$149/mo**; Business **$700/mo**; free Basic tier. https://bump.sh/ , pricing per G2/PricingSaaS listings seen 2026-08-30 | API **producers** publishing docs and detecting breaking changes in their own spec before release | Producer-side. Proves teams pay real money for breaking-change detection — but for the API they own, not the ones they consume. |
| **Visualping** | Free $0 (150 checks / 5 pages); Personal $14 / $35 / $70 per mo; Business $140-$350/mo (200-500 pages). https://visualping.io/pricing seen 2026-08-30 | Anyone monitoring web pages; explicitly markets "API changelog monitoring for technology partners" | Generic pixel/text diff. No API semantics, no breaking-vs-safe classification, no code mapping. The dumb substitute most teams actually reach for. |
| **apichangelog.com** | Originally a paid product (Show HN 2014-06-29, https://news.ycombinator.com/item?id=7960990, 4 points). As of 2026-08-30 the domain **301-redirects to a free Substack newsletter** (`apichangelog.substack.com`); last Wayback snapshot of the product site is 2018-08-28 | Devs | **Pricing archaeology result: the original paid product in this exact category died and its carcass is now a free newsletter.** A twelve-year-old warning. |
| **APIWatch** | Free newsletter (apiwatch-landing.pages.dev), promoted via dev.to content marketing, https://dev.to/atomicsoftware/every-major-api-deprecation-in-february-2026-breaking-changes-you-cant-miss-2k9a, 2026-02 | Devs | Free. Another zero-price competitor for the alerting half. |

**Manual cost being paid today (computed):** BLS median annual wage for software developers was **$135,980 as of May 2025** (https://www.bls.gov/ooh/computer-and-information-technology/software-developers.htm). That is ~$65/hr direct, ~$95/hr fully loaded at a 1.45x multiplier. The PartsplanAI incident above cost **16 hours of debugging (~$1,040-$1,520)** plus a month of corrupted data served to B2B customers — from a single unannounced alias change. A team hit twice a year at that scale is burning **$2,000-$3,000/year** in pure incident-response time, which supports a $49/month ($588/yr) price on paper. Note the gap between "supports on paper" and "someone signs up": the $4.20/month competitor exists because the *felt* value is far below the *computed* value.

## Reachability (50 qualified buyers in 30 days, $0)

Realistic, ethical, and free channels, with evidence of buyer presence:

1. **GitHub public-repo mining (highest yield, fully public data).** `gh api search/code` / dependency-graph queries for repos whose manifests contain 4+ of `stripe`, `shopify-api`, `twilio`, `plaid`, `@aws-sdk/client-*`, `openai`, `@anthropic-ai/sdk`, `easypost`. That query returns thousands of public repos; a hundred-plus are maintained by small companies with a public contact address. Free, public, and within ToS. **This is also the product's own qualification list.** Ethics constraint: this yields *identification*, not permission to bulk-mail; use it to find teams whose maintainers already invite contact (README contact, "we're hiring", public Discord).
2. **Shopify Developer Community Forums** — https://community.shopify.dev. The deprecation subforum has continuous 2025-2026 traffic (threads cited above span Jan 2025 to Jul 2026, with Shopify staff replying within hours). Participating honestly as a developer who publishes free tooling is legitimate; posting product links is not.
3. **OpenAI Developer Community "Deprecations" category** — https://community.openai.com. The single 2026 shutdown thread ran from April to August 2026 with named, self-identified developers publicly stating what will break for them.
4. **Hacker News Show HN with an open-source CLI.** Realistic expectation, calibrated by the evidence above: **1-4 points and 0 comments.** Do not plan on HN.
5. **dev.to / lobste.rs technical writing.** The incumbent (`flarecanary`) runs exactly this play with multi-post SEO series. Free, slow, and the competitor is already 6+ posts ahead.
6. **Open-source distribution is the only credible PLG path here:** ship the code-mapping half as a free MIT CLI + GitHub Action (this is exactly what `API Impact Tracker` and `Seismograph` did), monetize the hosted vendor-changelog corpus. Installs are countable; that is the kill metric.
7. **Boston, in person.** Northeastern is 2 stops from the Kendall/CIC cluster. Boston New Technology demo nights, Startup Boston Week (September, i.e. next month), and Boston backend meetups each put 30-150 engineers from 5-50 person companies in one room. Alex can qualify 10-15 people per event in conversation — "how many external APIs do you call, and when did one last break you?" — and that is a real, unfair, non-scalable advantage over the seven remote solo founders already in this space. **Three events in 30 days is a plausible 30-45 qualified conversations; GitHub mining covers the rest.**

## Wedge
**A one-time, paid "deprecation call-site audit" for one specific vendor deadline — starting with Shopify's 2026-04-01-style delisting deadlines and the OpenAI/Anthropic/Google model shutdown lists.**

Concretely: the buyer points the CLI at their repo. It (a) reads the vendor's published deprecation list, (b) greps + AST-matches every call site in the repo that touches a deprecated endpoint, field, model ID, or parameter, (c) emits a ranked file:line report and a draft PR for the mechanical ones. One vendor. One deadline. One repo.

This is the smallest thing someone pays for **this month**, and it is the exact thing `BigVan` asked for in evidence item 4: *"I cannot identify where the deprecated API call is being made."* Sell it as $199-$499 one-time (fits money priority #2), and convert to $49/month monitoring afterward. Do **not** lead with the monitoring subscription — that half retails for $4.20.

## Build estimate
**Agent-days to a sellable MVP: 6-9.**

- Vendor deprecation ingestion for 3 vendors only (Shopify version/deprecation docs, OpenAI deprecations page + `.md` endpoint, Stripe API changelog). Hand-written adapters, no generic scraper. **1.5 days.**
- Deprecated-symbol extraction: turn each vendor notice into a machine-readable list of (endpoint, field, model-id, param) tokens. LLM-assisted with human review; the review is the product's accuracy. **1 day.**
- Call-site matcher: ripgrep for the cheap 80%, then tree-sitter AST match for JS/TS and Python only, then one LLM confirmation pass per candidate to kill false positives. **2-3 days.** *This is the whole differentiator and the whole risk.*
- Report + draft-PR generation (GitHub App or plain `gh pr create`). **1 day.**
- CLI packaging, GitHub Action, landing page, Stripe checkout for the one-time audit. **1.5 days.**
- Daily re-check scheduler + email/Slack alert (only needed to convert to subscription). **1 day.**

Deliberately skipped in v1: more than 2 languages, generic changelog scraping across 100 vendors (apiPulse and Varen already won that race), auto-merge, OpenAPI spec diffing (ApiNotes gives it away free).

**Reusable assets: X-Scraper snapshot-diff engine for changelog monitoring; Graphene workspace_audit for call-site mapping.**

## Unit economics
- **Price:** $299 one-time audit (wedge) → $49/month per repo monitoring (expansion). Assume 10 monitoring customers.
- **LLM cost — shared corpus (not per-customer):** ~40 vendors x 1 fetch/day; only ~5 produce a diff worth summarizing. 10 calls/day at ~8k in / 1k out on a Haiku-class model (~$1/MTok in, ~$5/MTok out) = ~$0.13/day = **~$4/month total, amortized across all customers.**
- **LLM cost — per customer:** one full repo scan/month, ~200 candidate call sites confirmed at 3k in / 500 out = ~$1.10; plus ~2 draft PRs/month on a Sonnet-class model (~$3/$15 per MTok) at 30k in / 6k out = ~$0.36. **~$1.50-2.50/customer/month.** One-time audits cost ~$3-5 each in tokens.
- **Hosting:** Fly.io or Railway hobby container + managed Postgres, **$5-12/month**. Domain ~$1.20/month amortized. Resend free tier for email (3k/mo). **Total fixed burn: under $15/month — comfortably inside the $40 ceiling** and it stays there until roughly 15 paying customers.
- **Gross margin at 10 customers ($490 MRR):** COGS ~$15 fixed + ~$20 variable = $35. **~93% gross margin.**
- **Break-even on burn: 1 customer.** That part is genuinely good.

## Risks
- **Accuracy liability (highest).** A false negative — "no breaking changes affect you" when one does — is worse than no product, because the customer stops checking. The PartsplanAI incident shows the failure mode is *silent*, which is precisely the class this tool would be trusted to catch and would sometimes miss. Evidence: the Gemini alias change produced HTTP 200, valid JSON, `finish_reason: STOP`, and no error (HN 47271099) — no spec diff and no changelog line would have caught the grounding regression. **A meaningful share of the pain this product promises to solve is structurally undetectable by this product.**
- **Price ceiling set by competitors, not by value.** apiPulse charges $4.20/month for the alerting half; ApiNotes and APIWatch give it away; apichangelog.com's paid product decayed into a free Substack. The $49/month in the brief is already taken by FlareCanary's Pro tier for a broader feature set.
- **Crowded field, zero demand signal.** At least eight distinct products/newsletters shipped into this exact category between Jan and Jul 2026 (API Impact Tracker, Varen, apiPulse, ApiNotes, FlareCanary, APIGuard, Seismograph, APIWatch). Every launch scored 1-4 HN points with 0 comments. Supply is racing ahead of demand.
- **Platform dependency and ToS.** The corpus depends on fetching vendor changelog pages. `kull` reported (HN 47766479, 2026-04-14) that some vendors *"provide RSS that they block from fetching"*. Respecting robots.txt is non-negotiable and will silently shrink coverage. Reddit's 2026 shutdown of unauthenticated `.json` endpoints (which blocked this very research) is the template for how fast a source can vanish.
- **Repo access is a security review.** The differentiating feature requires reading customer source code. A 3-30 person company will ask a solo undergraduate for a security questionnaire, and rightly. Mitigation: local-first CLI that never uploads code (the design `PeterDS` chose: *"Runs locally (SQLite) - no data leaves your infrastructure"*), which in turn makes the recurring-revenue story harder.
- **Incumbent response is cheap.** Shopify, Stripe and OpenAI all already publish deprecation dashboards and email notices; GitHub could add this to Dependabot as a semantics layer at any time. Dependabot and Renovate do not cover API semantics today — that gap is the opening, and also the reason it may close.

## Kill criteria
- **By 2026-09-30:** 3 paid one-time audits at $199+ from GitHub-mined or Boston-met teams. Fewer than 3 → kill.
- **By 2026-09-30:** 25 installs of the free CLI/GitHub Action. Fewer than 10 → kill (no PLG path exists and outbound is barred by ethics).
- **By 2026-10-15:** 2 of those audit customers converted to $49/month. Zero → the recurring-revenue thesis is dead; at most keep it as a one-time service (money priority #2), never as a SaaS.
- **Immediate kill:** if in the first 3 real audits the call-site matcher produces more false positives than true positives on a real repo, stop — the only differentiator does not work.

## Incumbents and adjacent players
**Consumer-side (direct competitors):**
- FlareCanary — schema-drift and endpoint monitoring for third-party APIs, $0/$19/$49/$199/$499 per month. https://www.flarecanary.com/
- apiPulse — changelog/doc-update subscriptions for 20+ named APIs, $4.20/month PRO. https://apipulse.app/
- Varen — "monitors API changelogs, release notes, and OpenAPI specs", 100+ APIs, Show HN 2026-04-01. https://varen.dev/ (returned 403 to automated fetch, 2026-08-30)
- ApiNotes — free daily-rebuilt changelog directory for 50+ public APIs from vendor OpenAPI specs; paid tier $6.99/mo is producer-side. https://apinotes.io/
- APIGuard — API drift detection, content-marketing play. https://apiguard.co/blog/api-drift-detection-guide
- Seismograph — open-source early warning for silent LLM API drift. https://github.com/Tania-coder/SEISMOGRAPH
- APIWatch — free curated API-change newsletter. https://dev.to/atomicsoftware/every-major-api-deprecation-in-february-2026-breaking-changes-you-cant-miss-2k9a
- apichangelog.com — the 2013/2014 original; now redirects to a free Substack. https://apichangelog.substack.com/
- Visualping — generic page-change monitoring marketed for changelog watching, $14-$350/month. https://visualping.io/pricing
- PageCrawl.io — page/API monitoring, from ~$80/year. https://pagecrawl.io/blog/api-monitoring-track-changes-alerts
- Apify actors — "Changelog Radar for SaaS", $0.01 per check. https://apify.com/seeb/changelog-radar-for-saas/api

**Producer-side (adjacent, larger budgets, different buyer):**
- Bump.sh — breaking-change detection + changelog for your own API, from $149/month. https://bump.sh/
- API Impact Tracker — open-source: "which of my real clients breaks if I ship this?", local SQLite, MIT. https://news.ycombinator.com/item?id=46579637
- Optic — OpenAPI diff and breaking-change CI gate. https://www.useoptic.com/
- Speakeasy / Stainless / liblab — SDK generation from OpenAPI for API vendors. https://www.speakeasy.com/ , https://www.stainless.com/ , https://liblab.com/
- Zuplo / Kong — API gateways with deprecation and versioning controls. https://zuplo.com/ , https://konghq.com/
- Treblle / Moesif — API observability and usage analytics for API owners. https://treblle.com/ , https://www.moesif.com/
- Postman (acquired Akita) — API platform with contract testing and monitors. https://www.postman.com/

**Dependency tooling (does NOT cover API semantics — the stated gap):**
- Dependabot / Renovate — package-version bumps only; they see `package.json`, never a vendor's REST field rename. https://github.com/dependabot , https://docs.renovatebot.com/
- Snyk / Socket — security and supply-chain risk in dependencies, not external API contracts. https://snyk.io/ , https://socket.dev/
- Infield — tracks *runtime* deprecation warnings (Ruby only), Show HN 2024-12-19. https://docs.infield.ai/docs/monitor-deprecation-warnings
- Shopify `deprecation_toolkit` — catches deprecation warnings in CI, Ruby only. https://github.com/Shopify/deprecation_toolkit

## Score

| Criterion | Weight | Score | Justification |
|---|---:|---:|---|
| Time to first dollar | x3 | 3 | The one-time audit wedge is genuinely sellable within 2-3 weeks of building, but there is no self-serve demand pull — every 2026 launch in this space got 0 comments, so first dollar comes from hand-sold Boston conversations, not from shipping. |
| Reachability by a student | x3 | 3 | GitHub dependency mining gives a free, public, perfectly-qualified list of thousands of repos, and Boston's CIC/Startup Boston Week density lets Alex have 30-45 face-to-face qualifying conversations in 30 days — but Reddit is now closed (403), HN is dead for this topic, and there is no association or trade show for "teams that call a lot of APIs." |
| Pain x frequency | x2 | 3 | Documented, dated, real, and recurring (Gemini alias 2026-01, Amazon SP-API field removal 2026-02, Shopify delisting deadline 2026-04, OpenAI shutdowns Apr-Aug 2026), with one incident costing 16 engineer-hours plus a month of corrupted B2B data — but the Ask HN asking exactly this question got 1 point and 0 replies, which is a chronic-ache signature, not a hair-on-fire one. |
| Willingness-to-pay evidence | x2 | 2 | FlareCanary *lists* $49/month and Bump.sh *lists* $149/month, but I found no evidence of anyone actually paying for consumer-side change watching, while apiPulse prices it at $4.20/month, ApiNotes and APIWatch give it away, and the original apichangelog.com paid product decayed into a free Substack. |
| Fit with assets and strengths | ×2 | **3** | Repo tooling and snapshot-diff fit; changelog parsing is new. |
| Compounding | x2 | 4 | The vendor-adapter corpus genuinely compounds (kull's testimony that vendors block RSS and hide changes behind JS makes ingestion a real accumulating moat), each new vendor adapter serves every customer, and the deprecated-symbol-to-call-site rule library gets more accurate with every audit run. |
| Risk (5 = low) | x2 | 2 | Accuracy liability is severe and partly unfixable — the Gemini failure was HTTP 200 with valid JSON, invisible to any spec diff — compounded by eight live competitors, a price ceiling set at $4.20 by a rival, and the need for source-code access from security-conscious buyers who will not lightly grant it to a solo undergraduate. |
| Ceiling | x1 | 2 | The buyer segment (5-30 person API-glue companies) is small, the price is capped near $49 by an incumbent already there, larger teams build this internally, and the closest historical comparable in this exact category went to zero. |
| Build cost (5 = cheap) | x1 | 3 | Changelog ingestion for 3 vendors is a weekend, but the only differentiating component — multi-language AST call-site matching with acceptable false-positive rates — is 2-3 focused agent-days and is the part most likely to need a second and third pass. |

**Subtotal excluding Fit: 45 / 80.**
(9 + 9 + 6 + 4 + 8 + 4 + 2 + 3 = 45. With Fit scored 1-5 the total lands between 47 and 55 out of 90.)

## Verdict
The pain is real, dated, and expensive — I can name the incident, the vendor, the developer, and the hour count — but this is a market where eight people have already shown up with the same idea in eight months and nobody in the audience clapped. The decisive evidence is not any single complaint; it is the pattern: an Ask HN asking precisely this question scored 1 point with 0 replies, five Show HNs for this exact product scored 1-4 points with 0 comments each, the incumbent charges $4.20/month for the half of the product that is easy, and the original 2013 entrant's paid product has decayed into a free newsletter. Developers absorb this pain the way they absorb flaky CI — irritating, expensive, and never quite worth a purchase order. The one asset in this dossier that the eight competitors do not have is `BigVan`'s sentence: *"I cannot identify where the deprecated API call is being made."* Every existing tool tells you a change happened; none tells you where in your code it lands. That gap is worth a two-week probe — build only the call-site matcher, sell it as a fixed-price audit against a specific vendor deadline, and let Alex's Boston access do the selling that HN demonstrably will not do. But do not build this as a $49/month SaaS: the recurring-revenue half of the thesis is directly contradicted by every price point in the willingness-to-pay table, and the honest expected outcome is a modest one-time-revenue service, not the compounding subscription the plan hoped for. If three audits do not sell by 2026-09-30, this is a well-researched no.

## Research log
**Time spent:** roughly 70 agent-minutes.

**Queries run (Hacker News Algolia API, https://hn.algolia.com/api/v1/search):** `API deprecation broke`; `"breaking change" third-party API`; `Shopify API deprecation`; `Stripe API version upgrade pain`; `"deprecation email" missed`; `API changelog monitor`; `"found out when customers" API`; `"silently changed" API response`; `"didn't get the deprecation"`; `vendor API changed without notice`; `"no warning" API breaking change production`; `model deprecation OpenAI broke our app`; `"silently broke" API`; `Google Maps API deprecation surprise`; `"we only found out" API change`; `maintaining integrations third party APIs break constantly`; `"integration broke" API change customer`; `keeping up with API changes painful`; `"API drift"`; `monitor third-party API changes Show HN`; `"OpenAPI diff" breaking changes tool`; `Plaid API deprecation`; `Twilio API deprecation broke`. Full item trees pulled for HN 47538731, 47604426, 47766479, 46579637, 42843790, 42465705, 47271099, 48773957, 48339989, 48260848, 7960990.

**GitHub (read-only `gh api search/issues`):** `"breaking change" "no deprecation notice" in:body is:issue` (136 results); `"deprecated without warning" API is:issue` (825 results); `org:Shopify deprecation "no notice"` (458 results); `repo:stripe/* repo:twilio/* repo:plaid/* breaking deprecat` (0 results — vendor SDK repos are clean, the complaints live in vendor forums instead). Issue bodies and comments fetched for `amzn/selling-partner-api-models#5131` and `Shopify/shopify-app-js#2928`.

**Pages fetched (WebFetch):** community.shopify.dev threads 6169 and 23827; community.openai.com thread 1379553; apipulse.app; apinotes.io and its blog post; flarecanary.com; visualping.io/pricing; dev.to/atomicsoftware February-2026 deprecation roundup.

**Liveness checks (`curl -I -L`, 2026-08-30):** apichangelog.com → 301 to apichangelog.substack.com (200); varen.dev 200 (but 403 to automated fetch); apipulse.app 200; apinotes.io 200; flarecanary.com 200; getvaren.com 200 but it is an unrelated personal-finance product, not the HN "Varen".

**Wayback:** `archive.org/wayback/available?url=apichangelog.com` → closest snapshot 2018-08-28 (the product site stopped being archived after 2018). Direct fetch of web.archive.org was blocked by the fetch tool, so the snapshot content itself is unverified; only the snapshot date and the live 301 are asserted.

**Dead ends:**
- **Reddit is effectively closed.** `https://www.reddit.com/r/webdev/search.json` returned HTTP 403 with an HTML body; `old.reddit.com` and `www.reddit.com` are both blocked to WebFetch. Corroborated by reporting that Reddit disabled unauthenticated `.json` endpoints on 2026-05-30. **No Reddit quotes appear in this dossier because none could be verified.**
- lobste.rs `search.json` returned `{"error":"400 Unpermitted query or form parameter"}`.
- bls.gov returned 403 to WebFetch; the $135,980 median wage figure comes from the BLS OOH page as surfaced in search results and should be spot-checked in a browser before it goes in any customer-facing material.
- apiguard.co refused the connection (ECONNREFUSED) on direct fetch.
- HN comment mining for the buyer-side complaint shape ("our integration broke because a vendor changed something") was almost entirely dry across eight phrasings. Nearly every HN hit for "API deprecation" is about *language and OS* APIs (Python, Apple, Android, GTK), not third-party SaaS APIs. That asymmetry is itself a finding: the SaaS-API version of this pain does not get discussed on HN, it gets discussed in vendor forums and GitHub issues.
- A KushoAI statistic ("41% of APIs experience undocumented schema changes within 30 days, 63% within 90 days") surfaced in search results but the primary source could not be fetched, so **it is deliberately excluded** from the evidence sections above.

## Verification (2026-08-30, adversarial pass)
- Quotes: 12 checked, 12 verified, 0 unfetchable, 0 not found/altered. Every verbatim quote in "Pain evidence" appears on the cited page with the cited author and date. HN 1/2/10/11/12 confirmed via `hn.algolia.com/api/v1/items/{id}` (text, author, timestamp, and the 1-4 point / 0-comment scores all match). Quotes 4/5 confirmed via `community.shopify.dev/t/...json`; 6/7/8 via `community.openai.com/t/1379553.json` (authors `MarkusAntonuis` 03:06Z, `nikola.k` 06:04Z, `ltnew007` 2026-08-01 19:08Z — all exact, typo `supposesdly` included); 3 via GitHub API on `amzn/selling-partner-api-models#5131`; 9 via GitHub API on `Shopify/shopify-app-js#2928` (comment 2026-07-16T08:33Z, staffer `lizkenyon` 2025-11-18 "Sorry that this mislead you"). Sourcing discipline on quotes is the strongest part of this dossier.
- Claims:
  - **REFUTED — "Shopify delists apps still on unsupported APIs on 2026-04-01."** The versioning page's table reads `2026-04 | April 1, 2026 | April 16, 2027 15:00 UTC`. 2026-04-01 is a *release* date, not a deadline, and it is five months in the past. The real next hard date is **2026-10-16 15:00 UTC** (version 2025-10 becomes inaccessible), then 2027-01-16. The delisting policy itself is real and quoted correctly. https://shopify.dev/docs/api/usage/versioning
  - **REFUTED — Bump.sh "From $149/mo; Business $700/mo; free Basic tier."** The vendor's own page lists **Basic $50/month, Pro $250/month, Custom**, and no free tier. No $149 or $700 appears anywhere in the HTML. The dossier sourced this from G2/PricingSaaS aggregators instead of the vendor and says so — that shortcut produced the only wrong prices in the table. https://bump.sh/pricing
  - **CONFIRMED — FlareCanary $0 / $19 / $49 / $199 / $499.** Endpoint counts and check frequencies (5/daily, 25/hourly, 100/15-min, 250, 500) all match, as does "does not access customer repositories." https://www.flarecanary.com/
  - **CONFIRMED — apiPulse Basic free (5 subs, daily) / PRO $4.20/mo (20 subs, instant) / Enterprise custom.** The $4.20 price anchor is real. https://apipulse.app/
  - **CONFIRMED — ApiNotes $0 / $6.99, tagline "Your API changelog writes itself", free directory of 50+ changelogs "rebuilt every day from each vendor's official OpenAPI specification."** https://apinotes.io/ , https://apinotes.io/changelogs
  - **CONFIRMED — Visualping $0 (150 checks/5 pages), $14/$35/$70, Business $140–$350 (200–500 pages).** Exact. The "explicitly markets API changelog monitoring" sub-claim is not on the pricing page. https://visualping.io/pricing
  - **CONFIRMED — BLS median annual wage for software developers $135,980, May 2025.** The dossier flagged this as unverified (bls.gov 403s). It is correct: verified against the 2026-08-28 Wayback snapshot of the OOH page. Remove the caveat. http://web.archive.org/web/20260828021418/https://www.bls.gov/ooh/computer-and-information-technology/software-developers.htm
  - **CONFIRMED — apichangelog.com 301-redirects to apichangelog.substack.com**, and Show HN 7960990 (2014-06-29, `bpedro`, 4 points) is real. Pricing archaeology stands.
  - **CONFIRMED — Reddit is closed to automated access.** `www.reddit.com/.../search.json` and `old.reddit.com/.../search.json` both return HTTP 403 with an HTML body, with a browser User-Agent. The specific date "2026-05-30" for the shutdown is **unverifiable** (WebSearch budget exhausted; no primary source located) — drop the date, keep the fact.
  - **PARTLY — "every 2026 launch got 1–4 points, 0 comments."** Point counts check out, but the two Show HN links cited are *comment* IDs. Their parent stories are `47604425` (Varen, score 1, 1 descendant) and `46579636` (API Impact Tracker, score 1, 3 descendants). Also: Varen returned HTTP 200 to plain curl today, not 403.
  - **PARTLY — evidence items 4 and 5 are vendor false alarms, not breaking changes.** In thread 23827 Shopify staff (`Alan_G`, 2025-10-16) wrote "We are looking into this further as a possible issue on our end" and the banner cleared with **no code change**. In thread 6169 `BigVan` replies to the "just grep for /api/products" advice with "I already did that and the problem persists," and three more developers (`Tchinkatchuk`, `chunrong_xu`, `wissem`) report the same. The flagship quote of the whole dossier is therefore a case where a repo-scanning call-site matcher would have returned **zero hits and been useless** — the exact false-negative failure mode listed as risk #1. Meanwhile `santechsoftware` solved his version with a plain text search for `/api/products`, free, in minutes.
  - **PARTLY — "Nine months later the docs were still wrong" (item 9).** 2025-11-12 → 2026-07-16 is eight months.
- Score challenges:
  - **Compounding 4 → 2.** ApiNotes publishes 50+ vendor changelogs free, rebuilt daily from official OpenAPI specs; Varen covers 100+. A corpus a competitor gives away is not an accumulating moat. Worse for the second half of the justification: **Smartsheet shipped `smartsheet-deprecation-scanner` on 2026-06-08** — a free Apache-2.0 Claude Code skill that "scans a codebase for usage of deprecated Smartsheet API endpoints, query parameters, request/response fields… outputs a structured markdown report with **file paths, line numbers, code snippets, and migration guidance**," across Python, TypeScript, Java, C#, Go, Ruby and PHP, checking the vendor changelog first. The rule library compounds for the *vendor*, who has the deprecation list already and no reason to charge.
  - **Risk (5 = low) 2 → 1.** The researcher weighted accuracy liability and competitor count but never checked whether the differentiator itself is commodity. It is: `ast-grep` (15.7k stars, tree-sitter, MIT) and `semgrep` (16.4k) are the "2–3 agent-day" matcher off the shelf; `openrewrite/rewrite` (3.7k stars, pushed today) does automated mass API migration; and **GraphQL Inspector** (MIT, 1.76k stars) already validates a repo's own operations against a schema and returns "a list of errors found in documents. A second list with every deprecated usage" — and Shopify's Admin API, the wedge vendor, is GraphQL. The differentiator has a free incumbent in the wedge's own first market.
  - **Pain × frequency 3 → 2.** Over-weighted the Shopify forum threads. Two of twelve pain items are vendor-side alerting bugs with no call site to find, and the dossier's own strongest incident (Gemini grounding) is conceded to be structurally undetectable by this product. What survives as genuine, in-scope, code-locatable pain is thin: the SP-API `buyerEmail` removal and the OpenAI model-shutdown list. That is a chronic ache with a free workaround (grep), not a purchase order.
  - **Time to first dollar 3 → 2.** The wedge sells against a vendor deadline, and the named deadline does not exist. The one real Shopify deadline in range is 2026-10-16 — which lands **after** the 2026-09-30 kill date. The plan's urgency and its go/no-go are out of phase by two weeks.
  - **Build cost (5 = cheap) 3 → 4.** Under-weighted how cheap this now is: Smartsheet's 7-language scanner has a two-day repo history (created 2026-06-08, last push 2026-06-10) and contains no custom AST code. That is good news for the build estimate and terrible news for the thesis — cheap to build is cheap to copy, by the vendor, for free.
  - **Kill criteria are mostly sound but have three defects.** (a) The install criterion states two thresholds — "25 installs… Fewer than 10 → kill" — leaving 10–24 undefined. (b) "More false positives than true positives" names no adjudicator, no definition of a true positive, and n=3. (c) There is no kill trigger for the scenario that already happened once: a vendor ships the call-site scanner free as an agent skill.
- Missing:
  - `smartsheet/smartsheet-deprecation-scanner` (2026-06-08, Apache-2.0) — an API **vendor** giving away the exact differentiator, with file paths and line numbers, in 7 languages. Not in the dossier at any point. This is the single most important omission.
  - GraphQL Inspector (MIT) — free, does the code-mapping half for GraphQL, and Shopify Admin is GraphQL.
  - `ast-grep`, `semgrep`, OpenRewrite/Moderne — the "whole differentiator" as free dependencies and, in Moderne's case, a funded company in the adjacent seat. None appear under "Incumbents and adjacent players."
  - Shopify's own **API health report** (https://shopify.dev/docs/api/usage/versioning/api-health) — free, in the Dev Dashboard, lists deprecated calls from the past 14 days with "information about what you need to do to update your app." The dossier gestures at "vendor dashboards" in Risks but never names or prices the free substitute sitting inside the wedge's first vendor.
  - The corrected Shopify deadline table (next: 2026-10-16, then 2027-01-16). The wedge needs re-anchoring to a date that exists.
  - `API Impact Tracker` is dead: `aj9704845-code/api-impact-tracker`, 1 star, last push 2026-01-10 — the day after launch — and GitHub reports the license as NOASSERTION, not the MIT the author claimed on HN. The dossier cites its design as the model to copy and lists it as a live adjacent player.
  - No evidence was sought that **anyone pays** any of the eight competitors. Listed prices were verified; a single paying customer was not. That is the question the whole WTP section turns on.
  - ToS/copyright on republishing vendor changelog text — the core corpus asset — was never examined beyond robots.txt.
- Overall: **mostly-trustworthy** — the quote work is exemplary (12/12 verbatim, correctly attributed and dated) and the counter-evidence is honestly reported, but the wedge rests on a Shopify deadline that does not exist, on a flagship quote whose thread shows the code had no call site to find, and on a "nobody else does code mapping" premise that an API vendor publicly refuted for free in June 2026.


## Final score (main agent, 2026-08-30)
- Fit with assets and strengths: **3/5** ×2 — Repo tooling and snapshot-diff fit; changelog parsing is new.
- Reusable assets: X-Scraper snapshot-diff engine for changelog monitoring; Graphene workspace_audit for call-site mapping.
- Subtotal as researched: 45/80 · after adversarial verification: **35/80** (comp 4→2, risk 2→1, pain 3→2, ttfd 3→2, build 3→4)
- **Total: 41/90**
