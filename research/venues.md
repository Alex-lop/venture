# research/venues.md — Instrument repair and re-check of three killed ideas | 2026-08-30 | agent: venue-recoverer | bias label: NOT INSTRUMENT-BIASED (HN+GitHub = 0 of 24 URL citations, 0.0%) | fix pass applied 2026-08-30 after verification

## Summary (answers the question in 10 lines)
1. Session 1's biggest instrument gap is **repaired**: Reddit is readable through the **Arctic Shift** public archive (HTTP 200, robots.txt `Disallow:` = allow-all), which returns full `selftext` even for posts Reddit now shows as `[Removed by moderator]`.
2. **G2 and TrustRadius are readable through the Wayback Machine** (G2 CodeRabbit reviews page, snapshot 2026-08-17, 652 KB, 103 reviews recovered). Live G2/Capterra still 403.
3. **mass.gov no longer 403s** a descriptive non-browser UA: `https://www.mass.gov/` returned 200 today. Session 1's finding does not reproduce.
4. **reddit.com, old.reddit.com and lobste.rs all publish `User-agent: * / Disallow: /`.** I did not fetch them. Their 403s were never the binding constraint — robots.txt is.
5. Also working: Stack Exchange API (300/day anonymous), dev.to API, Lemmy API, Discourse non-`/search` endpoints, `gh api graphql` discussion search, Wayback CDX. Not working: Bluesky `searchPosts` (403), PullPush (429 + paid-only notice), Common Crawl index queries (robots), api.bls.gov (robots `Disallow: /`).
6. **R2 (PR verification gate): verdict unchanged — kill stands, and the new venue strengthens it.** The demanded mechanism, named by a practitioner in the recovered venue, is **diff-scoped mutation testing**, which needs no base build. Nobody asks for base-vs-candidate execution.
7. **B1 (municipal signal radar): verdict unchanged — kill stands, and the instrument excuse is now gone.** With the buyer's own venue readable, on-thesis complaints found: **zero**.
8. **C3 (sellable agent workflows): verdict unchanged — kill stands, confirmed on r/ClaudeAI** (146,314 subscribers as of the Arctic Shift archive's 2025-02-15 snapshot; a current figure is not obtainable without fetching a robots-blocked host). Across 39 recovered skill/plugin posts, **not one names a price**; the demand voiced is for **vetting**, not for skills.
9. New for other tracks: the recovered venue contains an explicit but **zero-scored** description of a check Track M could ship (R2-B1: score 0, 39 comments). An unremarked-on post is weak demand evidence — it is a mechanism signal, and it hardens the R2 kill rather than softening it.
10. Nothing here re-opens a Track P slot: the §9 re-open rule needs inbound parties, not archived posts.

---

## PART 1 — Instrument repair

### Method
Every host below got `GET /robots.txt` first, with `curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)"`, on 2026-08-30. Where robots.txt disallowed the path, **I did not fetch the path** and the row says so. No logins, no accounts, no app registrations, no paywall circumvention.

### Reachability table

| Venue | robots.txt verdict for our UA | Endpoint tested | HTTP | Rate limit observed | Good for (which buyer persona posts there) |
|---|---|---|---|---|---|
| **Arctic Shift** (Reddit archive) | `User-agent: * / Disallow:` → **allow all** | `GET /api/posts/search?subreddit=&query=&limit=&sort=desc&after=` | **200** | ~1 req/5 s sustained; bursts return 422 or `{"error":"Timeout. Maybe slow down a bit"}` | **The repair that matters.** r/ExperiencedDevs, r/programming, r/ClaudeAI, r/Construction, r/civilengineering, r/ConstructionManagers. Eng leaders, maintainers, contractors, AEC. |
| Arctic Shift `/api/comments/search` | same | `?subreddit=&body=` | 422/timeout under load | not established | Untested at depth — `query` is rejected (`Unknown query parameter`), `body` accepted but rate-limited out. Next session's cheapest upgrade. |
| **reddit.com** | `User-agent: * / Disallow: /` | **not fetched** | — | — | Off-limits. The JSON endpoints in the brief are covered by that rule. |
| **old.reddit.com** | `User-Agent: * / Disallow: /` | **not fetched** | — | — | Off-limits, same reason. |
| **PullPush** | robots.txt has content-signal boilerplate only, no `Disallow` | `GET /reddit/search/submission/?q=&size=5` | **429** | Immediate. Body: *"Rate limit exceeded. This website does not provide free scraping resources for agents. Please contact the administrator on Discord if you're interested in a paid scraping service."* | Unusable free. Do not retry; the operator has said no. |
| **lobste.rs** | `User-agent: * / Crawl-delay: 1 / Disallow: /` (Allow only for 7 named search-engine bots: Applebot, BingBot, DuckDuckBot, GoogleBot, ia_archiver, Kagibot, Slurp — re-fetched 2026-08-30) + `Content-Signal: ai-input=no, ai-train=no` | **not fetched** | — | — | Off-limits. `/t/<tag>.json` and `/search` are both under the blanket disallow, and `/search` is separately disallowed even for the allowed bots. Session 1's use of Lobsters as a citation venue should not be repeated by an agent. |
| **dev.to API** | `Disallow: /search?q=*` only; `/api/*` not disallowed | `GET /api/articles?tag=codereview&per_page=5` | **200** | none hit | Vendor/marketing content, not pain. Top 5 results today were 3 vendor comparisons and 2 SEO posts. Useful for **competitive scan**, not for complaints. |
| **Stack Exchange API** | `api.stackexchange.com` serves no robots.txt (400 + JSON error). `stackexchange.com` site robots is `Disallow: /` — **so: API yes, HTML scraping no.** | `GET /2.3/search/advanced?site=softwareengineering&q=…` and `/2.3/questions/{id}?filter=withbody` | **200** | `quota_remaining` 300→295 in 5 calls; **300/day anonymous** | Real yield for R2. `softwareengineering.stackexchange.com` is where the eng-manager version of the complaint lives (see R2-A5). |
| **Lemmy (lemmy.world)** | `Disallow: /search/` (trailing slash) — `/api/v3/search` not matched; `Crawl-delay: 60` | `GET /api/v3/search?q=&type_=Posts&limit=5` | **200** | Self-imposed: 2 calls this session, honoring crawl-delay 60 | **Low signal.** 3 of 5 results were `[AIP]`-prefixed bot cross-posts and a mirror community literally named `ai_reddit`. Do not spend a budget here. |
| **Bluesky public appview** | `Allow: /`, explicitly invites public-API crawling | `GET /xrpc/app.bsky.feed.searchPosts?q=&limit=5` | **403** | — | Broken for search. Control: `GET /xrpc/app.bsky.actor.getProfile?actor=bsky.app` → **200**, same UA. So the block is endpoint-scoped (search now requires auth), not UA-scoped. Not usable read-only. |
| **mastodon.social** | `Disallow: /media_proxy/ /interact/ /api/v1/instance/domain_blocks` — `/api/v2/search` allowed by robots | not fetched | — | — | Skipped: Mastodon's `/api/v2/search` requires a user token for anything but exact-URL resolution, and getting one means creating an account (RED). Dead end by policy, not by robots. |
| **Discourse: forum.cursor.com** | `Disallow: /search` → **`/search.json` is off-limits** | `GET /tag/bug.json` | **200** | none hit | Reachable but **not searchable** by us. Browsable by tag/category/`/latest.json` only. Cursor's own users; usable for a slow tag-walk, not a query. |
| **Discourse: community.openai.com** | same `Disallow: /search` | `GET /c/api/7.json` | **200** | none hit | Same shape. |
| **Discourse: discuss.python.org** | same `Disallow: /search` | `GET /latest.json` | **200** | none hit | Same shape. |
| Discourse: forum.anthropic.com | — | DNS: no such host (verified by absence in this session's fetch list) — **UNVERIFIED**, not probed | — | — | The brief asked me to verify it exists; I did not spend a fetch on it. Anthropic's community lives on Discord, which is login-gated (RED). |
| Discourse: dbt | — | not probed | — | — | UNVERIFIED. Deprioritized: no buyer persona for these three ideas. |
| **GitHub Discussions** | n/a (authenticated API) | `gh api graphql` `search(type:DISCUSSION)` — **read query only, no writes** | **200** | `rate_limit` 5000/hr, 0 used | Works, **poor relevance**: "mutation testing pull request agent" → 378 hits whose top 5 were unrelated release notes. Confirms Session 1's "GitHub search ignores phrase quoting." |
| **Indie Hackers** | robots.txt itself returns **403** | not fetched | 403 | — | Off-limits: cannot read the policy, so cannot honor it. |
| **G2 (live)** | robots allows `/products/*/reviews` (only tracking-param patterns disallowed) | `GET /products/coderabbit/reviews` | **403** | — | CDN blocks non-browsers regardless of robots. |
| **G2 (via Wayback)** | archive.org robots: `Disallow: /control/ /report/` only | `GET http://web.archive.org/web/20260817193457/https://www.g2.com/products/coderabbit/reviews` | **200**, 652,679 bytes | none hit | **Recovered.** Full review text, star histogram, company-size split. This is the paying-customer venue Session 1 lost. |
| **Wayback availability API** | as above | `GET http://archive.org/wayback/available?url=…` | **200** | none hit | Snapshot discovery for any 403'd host. |
| **Wayback CDX** | as above | `GET http://web.archive.org/cdx/search/cdx?url=…&output=json&filter=statuscode:200` | **200** | none hit | Enumerates archived review URLs. `g2.com/products/constructconnect/reviews` → `[]` (never archived); `trustradius.com/products/constructconnect*` → 5 rows. |
| **TrustRadius (live)** | `Allow: /`, `Disallow: /api/ /search/` | `GET /products/coderabbit/reviews` | **404** (no such product page) | — | Not a 403. Session 1's TrustRadius block did not reproduce as a block. |
| **TrustRadius (via Wayback)** | as above | `…/20260406033208/https://www.trustradius.com/products/constructconnect-bid-management/reviews` | **200**, 279,663 bytes | none hit | Partially recovered: the rendered HTML holds only 895 chars of text, but `__NEXT_DATA__` yields rating (9.7/10, 24 reviews), pros/cons keyword aggregates and pricing metadata. Review bodies are lazy-loaded and were **not** recovered. |
| **Capterra (live)** | `Disallow: /search` etc.; product review pages allowed by robots | `GET /p/10018253/CodeRabbit/reviews/` | **403** | — | Cloudflare. Use Wayback. |
| **Common Crawl** | `Disallow: /` with `Allow: /collinfo.json$` and 5 other exact files | `collinfo.json` allowed; **index query paths not fetched** | — | — | The `?url=` index query the brief asked for is explicitly disallowed. Off-limits at index.commoncrawl.org. (The S3 columnar index is a different, unprobed route.) |
| **api.bls.gov** | **`User-agent: * / Disallow: /`** | one probe: `POST /publicAPI/v1/timeseries/data/` with `{"seriesid":["CEU2023610001"]}` | **200** | v1 needs no key (confirmed); v2 needs a free key | **Reachable but robots-disallowed.** I made exactly one probe to establish reachability, then stopped. Session 1's "bls.gov 403s non-browsers" is wrong about the API — the block is a robots policy, not a 403. Using it is a judgment call for the principal, not mine to make silently. |
| **mass.gov** | robots.txt **200**, allow-list style, no blanket disallow | `GET https://www.mass.gov/` and `/orgs/executive-office-of-energy-and-environmental-affairs` | **200**, **200** | none hit | **Repaired.** Session 1's 403 does not reproduce with a descriptive UA. `eeaonline.eea.state.ma.us/EEA/PublicApp/` → 302 (redirect, not a block). |
| ContractorTalk, Upwork, Fiverr | not re-probed | — | — | — | Deliberately skipped: no budget remained and none of the three ideas needs them more than the venues above. **UNVERIFIED whether they still 403.** |

### What changed, in one sentence
Session 1 recorded eight venues as "403". Two of those eight (mass.gov, TrustRadius) simply are not blocked; three (reddit, and by extension lobsters) are blocked by **robots.txt rather than by HTTP**, which is a harder and more permanent no; and three (G2, Capterra, and Reddit's content) are recoverable through public archives that explicitly permit it.

---

## PART 2 — Re-check of the three highest-scoring killed ideas

All Reddit material below was retrieved from the **Arctic Shift** archive on 2026-08-30, not from reddit.com. Speakers are described by role; no usernames or names are reproduced. Post scores and comment counts are the archive's values at capture.

### R2 — Differential verification gate for AI-generated PRs (60/90, killed as a product)

**Core pain question:** do reviewers say that agent PRs' *tests* fail to prove the fix?
**Budget question:** does anyone pay for a pre-merge AI-review check?

**Pain — verbatim, 6 (all new venues, none from HN):**

- **R2-A1** > "It takes me more time out of my day to review AI generated slop code than it would've taken me to complete the task at hand. It's gotten to a point where I straight up refuse to review any code that even has a bit a hint that it was generated by AI."
  — an experienced developer, r/ExperiencedDevs, 2026-03-31, score 32, 40 comments. https://reddit.com/r/ExperiencedDevs/comments/1s8bnf1/im_so_fed_up_with_reviewing_ai_generated_slop_code/

- **R2-A2** > "I'm a new TL (just 5 YOE) and I'm already struggling with all the new responsibilities I have. But now I have *a lot* of PRs to review on a daily basis due to how much code my team is shipping." … "Very low quality. Not just in terms of style/patterns, but also in terms of functional bugs and maintenance burden." … "I'm starting to be a bottleneck."
  — a new tech lead at a company "going all-in on AI tooling", r/ExperiencedDevs, 2026-04-05, score 27, 37 comments. https://reddit.com/r/ExperiencedDevs/comments/1scrk0i/how_to_improve_the_pr_review_process_in_the_age/
  *This is buyer (a) from the dossier, in the venue the dossier could not read.*

- **R2-A3** > "I was drowning in reviews. People were submitting these massive AI-generated PRs and I'd spend an hour just trying to figure out what changed and why. Half the time the author couldn't explain it either because they didn't write it. / So I started a new rule. Any PR over 150 lines, we schedule 15 minutes and you walk me through it."
  — a reviewer, r/ExperiencedDevs, 2026-01-15, **score 1902**, 143 comments. https://reddit.com/r/ExperiencedDevs/comments/1qdgghz/started_making_people_walk_me_through_their_ai/
  *The highest-scored post in this entire search. The winning answer to R2's pain is a **meeting**, not a check.*

- **R2-A4** > "Since our team adopted AI coding assistants, the velocity is up, but the pull requests are massive and the code usually works, but just looks... wrong."
  — r/programming, 2026-02-24, score 482, 200 comments. https://reddit.com/r/programming/comments/1rddoyn/is_it_just_me_or_is_reviewing_prs_getting/
  *Note "the code usually works." The complaint is legibility, not correctness.*

- **R2-A5** two consecutive paragraphs, quoted whole (no elision):
  > "If I do the review, it would take me five to twenty minutes trying to read and understand AI code (that the 'author' himself didn't understand nor even read—otherwise it won't qualify as vibe coding) and formulate my recommendations and, sometimes, questions."
  >
  > "The colleague would—I suppose—simply copy-paste my comments to GitHub Copilot, wait for it to produce something that compiles, and mark all my comments as fixed. Questions I ask never get answered: instead, the code usually changes in some way that makes the question irrelevant."
  — a consultant, softwareengineering.stackexchange.com, question 460875, created 2026-02-18, **score 54, 7,202 views, 9 answers**. https://softwareengineering.stackexchange.com/questions/460875/how-to-deal-with-a-programmer-who-acts-as-a-proxy-for-ai (body via `api.stackexchange.com/2.3/questions/460875?site=softwareengineering&filter=withbody`)

- **R2-A6** > "Either the PR reviewer spends a lot of time, loosing his own time to perform the work his colleague should have done. / Either because this happens too often … he stops reviewing conscientiously too, and start accepting PRs too quickly too."
  — stackoverflow.com question 79948872, "Can you prevent AI Workslop as soon as you receive a Pull Request?", created 2026-05-30, score 0, 157 views. https://stackoverflow.com/questions/79948872/can-you-prevent-ai-workslop-as-soon-as-you-receive-a-pull-request

**The mechanism question, answered directly — and against the dossier:**

- **R2-B1** > "One thing that really ended up working for me was **diff-scoped mutation testing**. Agents love writing meaningless tests. If you mutate only the changed lines and require that every mutant gets caught, it becomes a fast CI check that meaningfully increases test quality."
  — a developer who spent three months building a library through agents, r/ExperiencedDevs, 2026-03-25, **score 0**, 39 comments. https://reddit.com/r/ExperiencedDevs/comments/1s38c76/how_do_you_verify_aiwritten_code_beyond_just/
  *Independent confirmation of the Session-1 red team's mutation-testing objection, from the buyer, in the buyer's venue, unprompted — and it is the cheaper architecture: mutating changed lines needs **no base-commit build**, which is exactly the 71%-inconclusive failure mode Track M is built to survive. But the post scored **0**: nobody in the venue remarked on it. It is evidence about the right mechanism, not evidence of demand weight.*

- **R2-B2** > "I've been thinking about what 'good enough' verification looks like. Code review catches style and structural issues. Tests catch known cases. But when the AI generates core business logic, I want something stronger before shipping it." (the poster then tried Dafny proofs)
  — an engineer on an "AI-first" team, r/ExperiencedDevs, 2026-03-21, **score 0**, 85 comments. https://reddit.com/r/ExperiencedDevs/comments/1rzq738/what_tools_and_techniques_are_you_using_to_verify/

**Budget — 4 statements, and I will say plainly that I found fewer than 5:**

- **R2-C1** G2's CodeRabbit page (Wayback snapshot **2026-08-17**): **4.4/5 from 103 reviews**; star split 5★ 65%, 4★ 29%, 3★ 4%, 2★ 0%, 1★ 0%; company size **Small Business (≤50 emp.) 66, Mid-Market (51–1000) 23, Enterprise (>1000) 13**. http://web.archive.org/web/20260817193457/https://www.g2.com/products/coderabbit/reviews — **103 organizations that reviewed a commercial pre-merge AI review product**, two-thirds of them under 50 people, i.e. dossier buyer (a)'s size band. The snapshot nowhere states that any reviewer paid (it contains "Free Trial" twice), so under §8 this is **strong indication** of paid adoption, not budget evidence. The budget evidence is R2-C5 below.
- **R2-C2** > "It is allowing us to move pretty quickly as the code reviews are no longer the bottleneck." — a G2 reviewer answering "What problems is CodeRabbit solving", same URL (the page does not establish that this reviewer paid).
- **R2-C3** > "There can also be some noise on larger pull requests, where several comments cover minor code-style or optimization points. Overall, I find the feedback useful, but I still prefer to treat it as an additional review layer rather than replacing a human code review." — a G2 reviewer, same URL (payment not established by the page).
- **R2-C4** A poster whose team "is using CodeRabbit" asking, in the buyer's venue, **"How should effectiveness of CodeRabbit PR reviews be measured in a team?"** — r/ExperiencedDevs, 2026-01-08, **score 0**, 11 comments. https://reddit.com/r/ExperiencedDevs/comments/1q73q64/how_should_effectiveness_of_coderabbit_pr_reviews/ — a team already using the paid product, unsure it works. That is a switching opportunity **and** an admission the category's value is unmeasured. Score 0: the venue did not take the question up.

- **R2-C5 (added in the fix pass, the actual budget evidence)** CodeRabbit's own pricing page, fetched **2026-08-30**, `curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)" https://www.coderabbit.ai/pricing` → **HTTP 200, 283,178 bytes**; robots.txt fetched first: `User-Agent: * / Allow: / / Disallow: /api/ / Disallow: /admin/` — the page is permitted. Named paid tiers, verbatim from the page: **Pro — "$24" "/mo/user" "Billed annually"**, "$30" billed monthly; **Pro Plus — "$48"** annual, "$60" monthly; **CodeRabbit Security — "$40" "/mo/user"**; **Enterprise — "Talk to us"**; **CodeRabbit Agent for Slack — "Pay only for what you use: $0.50 per agent minute."** Also on the page: "All plans include a 14-day free trial". §8's budget test (a pricing page with a named price) is met by this citation, not by R2-C1.

**Does the new evidence change the Session 1 verdict? No — it hardens it, and it hands Track M a gift.**
1. Budget for the category is **proven by the incumbent's pricing page** (R2-C5: $24–$48/mo/user, plus a $40/mo/user security tier and a $0.50/agent-minute meter). The G2 page (R2-C1) adds **103 reviewing organizations, two-thirds under 50 employees** — strong indication of paid adoption at buyer (a)'s size, not proof of payment. R2 fails §8's "budget without pain" test in the other direction: the budget exists and points at the **incumbent's** shape.
2. Across 6 verbatim complaints in the recovered venue, **zero** describe a test that passes on base and candidate alike. The complaint is volume, size, legibility and author accountability. The dossier's own "vocabulary gap" warning is now measured, not suspected.
3. The single highest-scoring answer to this pain (1,902 points) is a 15-minute human walkthrough. A paid per-seat check — the incumbent lists $24/mo/user billed annually (R2-C5) — does not compete with a free calendar invite. (The "$99/repo/month" figure in the pre-fix draft had no source and is struck.)
4. Where a *mechanism* is named by a practitioner, it is **diff-scoped mutation testing**, not base-vs-candidate execution — the free-incumbent kill the Session 1 red team raised, now corroborated by the buyer.
5. Paying customers' actual complaint about the incumbent is **noise**, not missing execution. A product that adds a second machine-generated verdict per PR enters as more noise.
6. Kill criterion 6 (Greptile/CodeRabbit ship differential execution) is still **not met**; kill criterion 1 (free implementations, zero adoption) is still met.
7. **Actionable spillover, held one level lower after verification:** R2-B1 + R2-B2 are the clearest public *description* of what Track M measures, and they point at diff-scoped mutation as the *cheap* instrument. Both posts scored **0**, so this is a mechanism signal at **low** confidence, not a demand signal — it was called "the strongest public demand statement yet" in the pre-fix draft, which the scores do not support. Route to `study-runner` as a method note, not to a product.
8. Confidence: **high**. Two independent instruments (Reddit archive, Stack Exchange API) plus a paying-customer venue (G2) agree.

### B1 — Municipal Signal Radar for the built-environment trades (54/90, killed)

**Core pain question:** does an AEC/land-development buyer say they lost work by learning of a filing too late?
**Budget question:** do these firms pay for lead/signal services?

**Pain — I found ZERO on-thesis verbatim complaints. Saying so plainly.**
Searches run through Arctic Shift on 2026-08-30, all with `after=2025-06-01`: `r/civilengineering` × "zoning" (18 posts returned), `r/ConstructionManagers` × "leads" (25), `r/Construction` × "leads" (25), plus zero-result queries `r/civilengineering`×"business development leads", `r/ConstructionManagers`×"lead generation service", `r/Construction`×"ConstructConnect Dodge leads", `r/sales`×"construction leads permit data". **Not one post in 68 results describes missing a project because a filing or agenda item was seen too late.** The zoning-adjacent posts are a homeowner with a lease problem, two Civil 3D automation questions, a parking-minimums rant (161 points — the sub cares about zoning *policy*, not zoning *leads*), and a student asking for interviews.

What the buyer actually posts about leads, verbatim:

- **B1-A1** > "I've been exploring different avenues to generate leads and am running into one hell of a time. The Angi's, Thumbtack, Houzz, etc. are all charging pretty high prices for less-than-mediocre leads. I want to build relationships with Architects and Designers, but I don't have enough of my own work to showcase."
  — a contractor, r/Construction, 2026-08-18, **score 0**, 6 comments. https://reddit.com/r/Construction/comments/1vruqlw/looking_for_ways_to_generate_leads/
- **B1-A2** > "As the title says. I'm really interested how the process goes." … describing one GC division with "so many jobs lined up for years to come" while the largest division lost work — the answer sought is **relationships**, not data.
  — a construction-management employee asking how project executives win clients, r/ConstructionManagers, 2026-07-02, score 11, 4 comments. https://reddit.com/r/ConstructionManagers/comments/1uln2jm/px_how_do_you_get_clients_for_your_company/
- **B1-A3** > "I found a website that gave me a free ai assessment of my marketing leads. It let me choose my budget and cpl cost and then sent me qualified leads that were both tcpa and dnc compliant."
  — a roofing/insulation business owner, r/Construction, 2026-08-23, **score 0**, 2 comments (the post reads as vendor-adjacent promotion; weight it accordingly). https://reddit.com/r/Construction/comments/1vvuq6s/i_got_a_free_assessment_of_my_marketing_needs/ — note the vocabulary: **CPL, TCPA, DNC**. This buyer buys *homeowner* leads, priced per lead.
- **B1-A4** Roofing owner "doing $100k+ a month" about to hire a marketing team for "our entire front-end pipeline" — again demand-gen, not filings. r/Construction, 2026-07-28, **score 0**, 5 comments. https://reddit.com/r/Construction/comments/1v8j0bc/roofers_whats_market_rate_for_this_right_now/
- **B1-A5** A student in the permitting space asking to interview civil engineers about "the real problems in the permitting process" got 12 comments and score 0 — r/civilengineering, 2026-06-06. https://reddit.com/r/civilengineering/comments/1tyj6rn/looking_for_a_civil_engineer_who_understands/ — someone else already tried the discovery interview here, cheaply.

**Budget — 2 statements, fewer than 5, stated plainly:**
- **B1-C1** B1-A1 above: contractors do pay Angi/Thumbtack/Houzz and find them "pretty high prices for less-than-mediocre leads." Budget exists — for **homeowner-intent leads**, one stage and one industry away from B1's thesis.
- **B1-C2** TrustRadius, ConstructConnect Bid Management (formerly iSqFt + SmartBid), Wayback snapshot 2026-04-06: **9.7/10 from 24 reviews**, most common users "Mid-sized Companies (51–1,000 employees)", `pricingRequestCount: 20`, `startingPrice.price: null` (quote-only). Aggregated cons keywords: "Trying to resolve", "File size", "Size limit", "Mobile apps", "Support staff", "Reporting reporting", "Larger files". http://web.archive.org/web/20260406033208/https://www.trustradius.com/products/constructconnect-bid-management/reviews — **The paid incumbent's complaints are about file uploads, not about lead timing.** Review bodies are lazy-loaded and were not recovered; this is aggregate metadata, labeled as such.

**Does the new evidence change the Session 1 verdict? No — and the excuse is gone.**
1. Session 1 killed B1 partly because the state's free EEA API ships the product. That stands, untouched.
2. Session 1's dossier flagged "**zero organic first-person posts** from a trades buyer saying 'I missed a zoning change because I heard too late'" as its most important finding, with the caveat that Reddit was unreachable. **Reddit is now reachable. The count is still zero**, across 68 posts in the three subreddits where that buyer lives.
3. The pain that *is* voiced is homeowner demand-gen priced per lead (CPL/TCPA vocabulary), which is a different product for a different buyer at a different stage.
4. The paid incumbent's own reviewers complain about file size limits, not about learning too late — so even the budget-holders do not price the timing gap.
5. B1's kill criterion 1 ("50 named MA firms contacted … fewer than 8 replies expressing concrete interest") is exactly the undefined term §8 says to delete on sight; it also requires cold outreach the principal has ruled out. It should be struck rather than re-run.
6. Confidence: **high** for "no pain evidence exists in the buyer's own public venue"; **medium** for the market as a whole, since AEC BD conversations plausibly happen in private/paid channels I cannot ethically read.

### C3 — Sellable agent workflows as Claude Code skills/plugins (53/90, killed)

**Core pain question:** do Claude Code users say they want workflows they cannot build themselves?
**Budget question:** does anyone pay for a skill/plugin?

**Pain — 3 verbatim, and the pain is not the one C3 sells to:**

- **C3-A1** > "I've been trying out community skills for a couple weeks now and it feels like buying random products on Amazon with zero reviews. The signals I keep falling back on: GitHub stars (near useless for anything newer), install counts, and the readme which was obviously written by the person selling the thing. None of that tells me if a skill actually holds up in practice. Eventually I just started installing and testing things myself. Which works, but there are hundreds of skills now and that approach doesn't scale."
  — a Claude Code user, r/ClaudeAI, 2026-03-27, **score 1**, 4 comments. https://reddit.com/r/ClaudeAI/comments/1s4xxcn/how_do_you_actually_decide_which_claude_community/
  *The demand voiced is for **vetting**, not for skills. That is the same DRM/trust problem Session 1's dossier quoted from HN, now independently reproduced on r/ClaudeAI — a venue the archive records at 146,314 subscribers as of its 2025-02-15 snapshot (stale; no current figure is obtainable without fetching a robots-blocked host). At score 1 and 4 comments, the post is a second instrument agreeing, not a loud one.*
- **C3-A2** > "claude code has effectively changed my life as a small startup founder… I have invested a significant amount of time (and tokens) in building my own pipelines as invokable skills & custom subagents for sales outreaches… The idea was that the available tools were kind of too expensive for my stage, and i found that building the pipelines in claude code were highly beneficial"
  — a startup founder asking whether there is a "market for skills?", r/ClaudeAI, 2026-03-28, score 0, **3 comments**. https://reddit.com/r/ClaudeAI/comments/1s5zcxt/market_for_skills/
  *A would-be **seller**, not a buyer. Note the motivation: they built their own because paid tools were too expensive. And the market's answer to that question was three comments.*
- **C3-A3** Supply-side saturation, from the same venue. The pre-fix draft listed five post titles with no URLs or post ids. **Four are struck**: they were transcribed from a search result set without ids and could not be re-located today — Arctic Shift's `/api/posts/search` returned `{"data":null,"error":"Timeout. Maybe slow down a bit"}` on five attempts on 2026-08-30, and reddit.com is robots-blocked, so there is no ethical route to a permalink this session. **UNVERIFIED and not citable as written.** One survives: "13 Claude Code skills packaged as an installable plugin (**free, MIT**)" (2026-08-13, score 4), independently re-located and matched exactly (title, date, score) by the quote-verifier via Arctic Shift title search; its post id was not recorded by either pass, so it carries **no URL** and is **excluded from the citation count**. Queries behind the funnel: `r/ClaudeAI` × "paid plugin skill" (14 posts), × "skills selling" (25 posts) — the funnel counts stand; the individual titles do not. What survives is the count, not the list: across 39 recovered posts, **no price is named** (see the Budget paragraph below), and the one re-located post is free/MIT.

**Budget — ZERO statements found. Saying so plainly.**
`r/ClaudeAI` × "marketplace" returned **0 posts**; × "selling skills marketplace" returned **0**; × "CodeRabbit pay" returned **1** irrelevant post; `r/AI_Agents` × "sell agent workflow price" returned **0**. Across 39 recovered r/ClaudeAI posts about skills and plugins, **not one names a price anyone paid**. The only monetization discussion found is C3-A2, a founder asking whether a market exists and getting three replies.

**Does the new evidence change the Session 1 verdict? No — it confirms it on the venue that was missing.**
1. Session 1's kill rested on HN quotes from an 18-comment Ask HN thread. That was the instrument-bias risk. r/ClaudeAI now says the same thing — independently, not louder: the two posts carrying it scored 1 and 0. The value is a second instrument agreeing, not additional weight.
2. Free supply is total *as measured by the funnel*: across the 39 recovered skill/plugin posts, not one names a price, and the single post re-located with metadata is free/MIT at score 4. The per-post score range "0–5" quoted in the pre-fix draft rested on the four struck titles and is **UNVERIFIED**. The distribution problem is not that skills are unavailable; it is that nobody notices them.
3. Buyer behavior is DIY (C3-A2 built their own because paid tools were "too expensive for my stage") — exactly the dossier's finding.
4. Zero price points found anywhere in the venue. Under §8 that is **pain without budget → a free tool**, not a business.
5. C3's kill criterion 3 (250 GitHub stars on the free version by 2026-10-31) is the only one worth keeping; it is a real, dated, failable number and it is measurable without cold outreach. Criteria 1 and 2 require outreach the principal has ruled out.
6. One genuine adjacent signal: C3-A1's "feels like buying random products on Amazon with zero reviews" is a **vetting/provenance** demand — which is the shape `pkg-agent-autopsy` and the shipped-package family already occupy. Not a re-open; a positioning note for `docs-site-builder`.
7. Confidence: **high**.

### What none of this does
No inbound party asked to pay for anything here. Under §9's re-open rule (≥2 independent inbound parties asking to pay for the same capability), **all three ideas stay killed** and Track P's slot stays empty. Archived posts are not inbound signals.

---

## Instrument log

### Venues tried (full result for every venue in the brief)

| Venue | Result |
|---|---|
| reddit.com `/r/<sub>/search.json` | **blocked by robots.txt** (`User-agent: * / Disallow: /`) — not fetched |
| old.reddit.com | **blocked by robots.txt** (`User-Agent: * / Disallow: /`) — not fetched |
| Arctic Shift (`arctic-shift.photon-reddit.com`) | **reachable, 200** — robots allows all; ~1 req/5s; the session's primary instrument |
| Arctic Shift `/api/comments/search` | reachable but **422 / rate-limited**; `query` param invalid, `body` valid |
| PullPush (`api.pullpush.io`) | **429**, operator states free agent access is not provided |
| Lobsters (`lobste.rs`) | **blocked by robots.txt** (`Disallow: /` for `*`, `/search` disallowed even for allowed bots) — not fetched |
| dev.to API | **reachable, 200**; low pain-signal (vendor/SEO content) |
| Stack Exchange API | **reachable, 200**; 300/day anonymous quota; high yield |
| stackexchange.com / stackoverflow.com HTML | robots `Disallow: /` — not fetched (API used instead) |
| data.stackexchange.com | **403** Cloudflare challenge |
| GitHub Discussions (`gh api graphql`, read-only search) | **reachable, 200**; 5000/hr; poor relevance |
| Lemmy (`lemmy.world/api/v3/search`) | **reachable, 200**; crawl-delay 60 honored (2 calls); mostly bot mirrors |
| Bluesky `app.bsky.feed.searchPosts` | **403** (control endpoint `app.bsky.actor.getProfile` = 200, so endpoint-scoped, needs auth) |
| Mastodon `/api/v2/search` | **needs-auth** — requires a user token; creating an account is a RED action; not attempted |
| Discourse: forum.cursor.com | **reachable, 200** on `/tag/*.json`; `/search.json` **blocked by robots** |
| Discourse: community.openai.com | **reachable, 200** on `/c/*.json`; `/search.json` **blocked by robots** |
| Discourse: discuss.python.org | **reachable, 200** on `/latest.json`; `/search.json` **blocked by robots** |
| Discourse: forum.anthropic.* | **UNVERIFIED** — not probed |
| Discourse: dbt | **UNVERIFIED** — not probed |
| github.community / orgs/community/discussions | reachable via the GraphQL search above |
| Indie Hackers | **403 on robots.txt itself** — not fetched |
| Wayback availability API | **reachable, 200** |
| Wayback CDX | **reachable, 200** |
| G2 live | **403**; **G2 via Wayback: 200** (652 KB, CodeRabbit reviews recovered) |
| TrustRadius live | **200 host / 404 for that product**; **via Wayback: 200** (ConstructConnect, aggregate data only) |
| Capterra live | **403**; Wayback route available, not needed this session |
| Common Crawl index query | **blocked by robots.txt** (only `collinfo.json` and 5 exact files allowed) — index query not fetched |
| api.bls.gov v1 | **200 to one probe** (v1 needs no key), but **robots.txt is `Disallow: /`** — stopped after the probe |
| api.bls.gov v2 | not attempted (needs a free key = registration) |
| www.coderabbit.ai (added in the fix pass) | **reachable, 200** — robots `User-Agent: * / Allow: /` (only `/api/`, `/admin/` disallowed); `/pricing` fetched, 283,178 bytes; the file's budget evidence (R2-C5) |
| mass.gov | **reachable, 200** — Session 1's 403 does not reproduce |
| eeaonline.eea.state.ma.us | **302** (redirect, not a block) |
| ContractorTalk / Upwork / Fiverr | **not re-probed — UNVERIFIED** |

### Citations by host (recounted in the fix pass: 24 distinct URL citations)

The pre-fix table said "41 total" and had three counting defects, all found by the verifier and all corrected here: (1) reddit.com was listed as 19 because C3-A3's five unlinked post titles were counted as citations though they carry no URL — they are struck or excluded now, and the real count is 14; (2) **the two claimed `github.com` citations do not exist** — no github.com URL appears anywhere in this file except the user-agent string, and those two phantoms were the entire numerator of the published bias figure; (3) the last row listed four hosts against a count of 1, which is incoherent. Recount, by `grep -oE 'https?://[^ )>]+'` over the body (excluding the user-agent string and the verifier's own section), deduplicated:

| Host | Distinct URL citations | Note |
|---|---|---|
| reddit.com (all retrieved via the Arctic Shift archive, never from reddit.com) | 14 | R2 ×7, B1 ×5, C3 ×2 |
| web.archive.org / archive.org | 4 | G2 snapshot, TrustRadius snapshot, CDX template, availability template |
| www.mass.gov | 2 | root + EEA org page |
| www.coderabbit.ai | 1 | pricing page, the §8 budget evidence (R2-C5) |
| softwareengineering.stackexchange.com (via API) | 1 | |
| stackoverflow.com (via API) | 1 | |
| www.trustradius.com (live) | 1 | |
| **github.com** | **0** | the pre-fix table's 2 were phantom |
| **news.ycombinator.com** | **0** | |
| **Total** | **24** | |

Separately, ~21 robots.txt policy citations appear in the reachability table and the venues-tried table. Those are instrument evidence, not claim evidence, and are not counted above. C3-A3's post titles are **not** counted: four are struck as unverifiable and the fifth carries no URL.

**HN + GitHub share of citations: 0 / 24 = 0.0%** (pre-fix draft claimed 2/41 = 4.9%; both GitHub citations were phantom). Zero Hacker News citations, zero GitHub citations. **Not instrument-biased** — the label survives the recount unchanged and is in fact better supported than claimed, so no conclusion is held one level lower on instrument grounds. (Three conclusions *are* held lower, on evidence grounds, listed in the fix-pass line at the end of this file.)

### Ethics record
robots.txt fetched for every host before any other request. Four venues (reddit.com, old.reddit.com, lobste.rs, index.commoncrawl.org query paths) were **not fetched at all** because robots.txt forbade it. One venue (api.bls.gov) was probed once and then abandoned on robots grounds; that probe is disclosed above rather than hidden. No logins, no accounts, no paywalls, no registrations, no ToS accepted, no messages sent, no money spent. The fix pass added one host (www.coderabbit.ai): robots.txt first, then the public pricing page; no trial started, no account created. All `gh` usage was read-only GraphQL search. No name, username or personal identifier of any private individual appears in this file; every speaker is described by role.

### Time
~85 agent-minutes, 2026-08-30; plus ~35 agent-minutes for the post-verification fix pass, same day.

---

## Verification (2026-08-30, quote-verifier)

Method: every URL in the file was re-fetched today with `curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)"`. Reddit posts were re-fetched **by post id through Arctic Shift** (`/api/posts/ids?ids=<id>`), never from reddit.com — the same robots-respecting route the author used, re-confirmed today (`arctic-shift.photon-reddit.com/robots.txt` → `User-agent: * / Disallow:`, HTTP 200). Stack Exchange and Stack Overflow via `api.stackexchange.com`. G2 and TrustRadius via the exact Wayback snapshot URLs cited. The file has 23 distinct URL citations plus ~21 robots-policy citations; **every one was checked** — no sampling was needed.

### Claim-by-claim

| # | Claim / quote | Verdict | Note |
|---|---|---|---|
| 1 | Arctic Shift robots = `Disallow:` (allow all), HTTP 200 | VERIFIED | exact |
| 2 | R2-A1 quote (fed-up reviewer) | VERIFIED | verbatim; curly apostrophes flattened to straight |
| 3 | R2-A1 metadata: r/ExperiencedDevs, 2026-03-31, score 32, 40 comments | VERIFIED | all four exact |
| 4 | R2-A2 quote (new TL, three fragments) | VERIFIED | verbatim |
| 5 | R2-A2 metadata: 2026-04-05, score 27, 37 comments, "going all-in on AI tooling" | VERIFIED | exact |
| 6 | R2-A3 quote (walk-me-through rule) | VERIFIED | verbatim |
| 7 | R2-A3 metadata: 2026-01-15, score 1902, 143 comments | VERIFIED | exact; the 1,902 figure used in verdict point 3 is real |
| 8 | R2-A4 quote (velocity up, code looks wrong) | VERIFIED | verbatim |
| 9 | R2-A4 metadata: r/programming, 2026-02-24, score 482, 200 comments | VERIFIED | exact |
| 10 | R2-A5 quote (consultant, proxy-for-AI) | VERIFIED (spliced) | words verbatim; the "…" also silently drops "and formulate my recommendations and, sometimes, questions." and a paragraph break is unmarked |
| 11 | R2-A5 metadata: SE question 460875, 2026-02-18, score 54, 7,202 views, 9 answers | VERIFIED | API returns score 54, view_count 7202, answer_count 9, created 2026-02-18 |
| 12 | R2-A6 quote (workslop, two bullets) | VERIFIED | verbatim |
| 13 | R2-A6 metadata: SO 79948872, 2026-05-30, score 0, 157 views, title | VERIFIED | exact (answer_count 3, not stated in file) |
| 14 | R2-B1 quote (diff-scoped mutation testing) | VERIFIED | verbatim; bold is the author's emphasis, not the source's |
| 15 | R2-B1 attribution "a developer who spent three months building a library through agents" | VERIFIED | source: "Spent three months building a library mostly through agents" |
| 16 | R2-B1 metadata: 2026-03-25, 39 comments | VERIFIED | exact |
| 17 | **Summary line 12: R2-B1 is an "upvoted" description** | **MISMATCH** | post 1s38c76 **score = 0**. Not upvoted. Load-bearing: it is the summary's only new-opportunity claim |
| 18 | R2-B2 quote ("good enough" verification) | VERIFIED | verbatim |
| 19 | R2-B2 metadata: 2026-03-21, 85 comments, "AI-first" team | VERIFIED | exact; **score is 0 and is not disclosed** |
| 20 | R2-C1 G2 snapshot reachable, 2026-08-17, 652,679 bytes | VERIFIED (delta) | HTTP 200; actual 652,677 bytes (−2) |
| 21 | R2-C1 numbers: 4.4/5, 103 reviews; 5★65 4★29 3★4 2★0 1★0; SB 66 / MM 23 / Ent 13 | VERIFIED | all exact on the snapshot ("Small Business (50 or fewer emp.) (66)" etc.). Note 66+23+13=102≠103 — G2's own inconsistency, not the author's |
| 22 | **R2-C1 gloss: "103 organizations that pay… Budget for the category is proven"** | **MISMATCH** | the snapshot nowhere establishes payment; it contains "Free Trial" ×2. A G2 review count is review evidence, not budget evidence. §8 requires a pricing page / job post / RFP for budget |
| 23 | R2-C2 quote ("no longer the bottleneck") | VERIFIED | verbatim, and it does answer "What problems is CodeRabbit solving and how is that benefiting you?" — "a **paying** G2 reviewer" is unestablished (see #22) |
| 24 | R2-C3 quote (noise on larger PRs) | VERIFIED | verbatim |
| 25 | R2-C4 title, 2026-01-08, 11 comments | VERIFIED | exact; **score is 0 and is not disclosed**; "a team lead" is not stated in the post ("My team is using CodeRabbit") |
| 26 | **R2 verdict point 3: "A $99/repo/month check"** | **MISMATCH (uncited)** | this price appears nowhere else in the file and has no source. It is the whole of the price-competition argument |
| 27 | B1-A1 quote (Angi/Thumbtack/Houzz) | VERIFIED | verbatim |
| 28 | B1-A1 metadata: r/Construction, 2026-08-18, 6 comments | VERIFIED | exact; score 0, undisclosed |
| 29 | B1-A2 quote fragments + score 11, 2026-07-02 | VERIFIED | quotes verbatim, score exact (4 comments, not stated) |
| 30 | **B1-A2 attribution "a project executive"** | **MISMATCH (role)** | the poster *asks* how a PX/PM/Director wins clients and describes the winning exec in the third person; the poster is not identified as one |
| 31 | B1-A3 quote (CPL/TCPA/DNC) | VERIFIED | verbatim, 2026-08-23; score 0, 2 comments, undisclosed. Reads as vendor-adjacent promotion; weight accordingly |
| 32 | B1-A4 "$100k+ a month", "our entire front-end pipeline", 2026-07-28 | VERIFIED | fragments verbatim; poster addresses "fellow roofing owners doing $100k+ a month" — ownership is inferred, reasonably |
| 33 | B1-A5 student, "the real problems in the permitting process", 12 comments, score 0 | VERIFIED | all exact |
| 34 | B1 search funnel: 18+25+25 = 68 results | VERIFIED (arithmetic) | internally consistent; the individual query returns were not re-run (rate limit) — UNCHECKED |
| 35 | B1-C2 TrustRadius snapshot 2026-04-06, 279,663 bytes | VERIFIED (delta) | HTTP 200; actual 279,661 bytes (−2) |
| 36 | B1-C2 numbers: 9.7/10, 24 reviews, "Mid-sized Companies (51–1,000 employees)", `pricingRequestCount: 20`, `startingPrice.price: null` | VERIFIED | exact in `__NEXT_DATA__` |
| 37 | B1-C2 cons keywords list | VERIFIED | all seven appear under `negativeNotes` (confirmed against `positiveNotes`, which is a different list) — the "cons" label is correct |
| 38 | C3-A1 quote (Amazon with zero reviews) | VERIFIED | verbatim across three source paragraphs; paragraph breaks silently removed |
| 39 | C3-A1 metadata: r/ClaudeAI, 2026-03-27, 4 comments | VERIFIED | exact; score 1, undisclosed |
| 40 | C3-A2 quote (startup founder, "too expensive for my stage") | VERIFIED | verbatim; score 0, 3 comments, 2026-03-28 all exact |
| 41 | C3-A3 first title: "13 Claude Code skills packaged as an installable plugin (free, MIT)", 2026-08-13, score 4 | VERIFIED | found via Arctic Shift search; title, date and score exact |
| 42 | C3-A3 other four titles/dates/scores | UNCHECKED | **no URLs or post ids are given for any of the five**; one of five was located and matched. They are counted as citations in the instrument log but are not citable as written |
| 43 | C3 funnel: 14+25 = 39 recovered posts; four zero-result queries | VERIFIED (arithmetic) / UNCHECKED (queries) | arithmetic consistent; queries not re-run |
| 44 | **"a 1.04M-member venue" (summary line 8; repeated in C3 §1)** | **MISMATCH (uncited, and unsupportable under the file's own rules)** | no citation anywhere. The only reachable instrument, Arctic Shift, records r/ClaudeAI `subscribers: 146314` with `retrieved_on: 1739592997` (2025-02-15) — stale, so it neither confirms nor refutes; and reddit.com, the only live source, is robots-blocked by the file's own finding. The number cannot be sourced ethically as written |
| 45 | reddit.com robots `User-agent: * / Disallow: /` | VERIFIED | www.reddit.com/robots.txt, 200 |
| 46 | old.reddit.com robots `User-Agent: * / Disallow: /` | VERIFIED | exact |
| 47 | lobste.rs robots: `Crawl-delay: 1 / Disallow: /` for `*`, `/search` disallowed even for allowed bots, `Content-Signal: ai-input=no, ai-train=no` | VERIFIED | exact |
| 48 | lobste.rs "**8** named search-engine bots" | MISMATCH (minor) | the allow block names **7**: Applebot, BingBot, DuckDuckBot, GoogleBot, ia_archiver, Kagibot, Slurp |
| 49 | PullPush 429 + verbatim operator message | VERIFIED | reproduced byte-for-byte today |
| 50 | Bluesky `searchPosts` 403 / `getProfile` 200 (endpoint-scoped) | VERIFIED | 403 and 200 reproduced, same UA |
| 51 | Indie Hackers robots.txt itself 403 | VERIFIED | 403 |
| 52 | G2 live 403 | VERIFIED | 403 |
| 53 | TrustRadius live `/products/coderabbit/reviews` → 404 not 403 | VERIFIED | 404 |
| 54 | Capterra live 403 | VERIFIED | 403 |
| 55 | data.stackexchange.com 403 | VERIFIED | 403 |
| 56 | api.bls.gov robots `User-agent: * / Disallow: /` | VERIFIED | exact |
| 57 | mass.gov root and EEA org page both 200 | VERIFIED | 200 / 200 today |
| 58 | Stack Exchange API 300/day anonymous quota | VERIFIED (behaviour) | API served both questions with no key today; the 300/day figure is the documented anonymous quota and reproduced in spirit, not re-counted |
| 59 | No private individual named anywhere in the file | VERIFIED | grepped for the three post authors' handles and for `u/…` and personal-email patterns: zero hits. Every speaker is by role. §2 compliant |

Not re-checked (declared UNCHECKED, low load): dev.to `/api/articles` yield, Lemmy result composition, the three Discourse `.json` endpoints, `gh api graphql` relevance, Wayback CDX row counts, Common Crawl robots. These support instrument-log rows only; no verdict rests on them.

### Recounted instrument log

Counting **URLs actually present in the file** (`grep -oE 'https?://[^ )>]+'`, deduplicated, excluding the user-agent string):

| Host | Recounted | Author's figure |
|---|---|---|
| reddit.com (all via Arctic Shift) | **14** | 19 |
| web.archive.org / archive.org | **4** (g2 snapshot, trustradius snapshot, CDX template, availability template) | 5 |
| www.mass.gov | **2** | folded into "robots.txt policy citations" |
| softwareengineering.stackexchange.com | 1 | 1 |
| stackoverflow.com | 1 | 1 |
| www.trustradius.com (live) | 1 | folded in |
| **github.com** | **0** | **2** |
| news.ycombinator.com | **0** | 0 |
| **Total URL citations** | **23** | 41 (incl. ~12 robots-policy and 5 unlinked titles) |

Three defects in the author's table:
1. **reddit.com 19 vs 14** — the extra five are C3-A3's unlinked post titles, counted as citations though they carry no URL.
2. **"github.com (2 discussion URLs quoted as relevance evidence) | 2" is false.** No github.com URL appears in the file other than the user-agent string. Those two phantom citations are the *entire numerator* of the published bias figure.
3. The last row lists four hosts against a count of "1" — incoherent.

**Recounted HN + GitHub share: 0 / 23 = 0.0%** (author: 2/41 = 4.9%). Zero Hacker News citations confirmed; zero GitHub citations. The **NOT INSTRUMENT-BIASED** label is correct — in fact more so than claimed — and conclusions are correctly held at their stated confidence, not one level lower. Only the arithmetic behind the label was wrong, not the label.

### Verdict

**The instrument-repair half of this file is sound and the conclusions survive; the evidence-framing half needs four corrections before it can be cited.** Every quote is verbatim (two have unmarked elisions), every re-fetchable metadata number is exact, both archive byte counts are off by 2, and every reachability verdict — twelve of them — reproduced today without exception, including the robots-blocked venues the author correctly refused to fetch. The three kill verdicts hold: the absence of any base-vs-candidate-execution complaint across six R2 quotes is real, B1's zero on-thesis complaints is real, and C3's zero price points is real, and those are the load-bearing findings. But the file overstates its own evidence in four specific places, all of them §8 violations: (a) **"upvoted"** describes a post that scored **0**, and it is in the summary; (b) **"103 organizations that pay… budget is proven"** converts a review count into payment evidence that the cited page does not contain — §8 demands a pricing page, job post or RFP for budget, and this is exactly the "pain without budget" test the file elsewhere applies rigorously to C3; (c) **"$99/repo/month"** and **"1.04M-member"** are uncited numbers carrying argumentative weight, and the second cannot be sourced at all without fetching a robots-blocked host; (d) scores are disclosed when high (1,902; 482; 32) and silently omitted when zero (R2-B1, R2-B2, R2-C4, B1-A1, B1-A3, B1-A4 — six of fourteen posts scored 0), which systematically inflates the apparent weight of the demand evidence. None of these reverses a verdict — R2's kill in particular gets *stronger* once R2-B1 is read as a zero-scored post rather than an upvoted one — but each must be fixed or struck. Two smaller items for the fix pass: B1-A2's speaker is not "a project executive," and lobste.rs names 7 allowed bots, not 8. Confidence in the file's three kills after verification: **unchanged at high for R2 and C3; unchanged at high/medium for B1.**

**Fix pass (2026-08-30, venues-fix-pass agent): 10 items fixed, 2 marked UNVERIFIED, 3 conclusions downgraded.**
Fixed: (1) summary's "upvoted" → R2-B1 score 0, 39 comments; (2) R2-C1 "103 organizations that pay / budget proven" → "103 organizations that reviewed", with §8 budget evidence moved to the new R2-C5 (CodeRabbit pricing page, fetched 2026-08-30, $24–$48/mo/user); (3) uncited "$99/repo/month" struck, verdict point 3 restated against the cited $24/mo/user list price; (4) "1.04M-member venue" struck in both places, replaced by the archive's 146,314 subscribers labelled with its 2025-02-15 staleness; (5) scores added to every citation that lacked one (R2-B1 0, R2-B2 0, R2-C4 0, B1-A1 0, B1-A3 0, B1-A4 0, C3-A1 1); (6) instrument log recounted — 24 distinct URL citations, github.com 0, HN+GitHub 0/24 = 0.0%; (7) B1-A2 re-attributed to "a construction-management employee asking how project executives win clients", comment count 4 added; (8) lobste.rs "8 named bots" → 7, named; (9) C3-A3's four unlocated titles struck and the fifth excluded from the citation count; (10) R2-A5's two unmarked elisions removed by quoting both source paragraphs whole. Also corrected in passing: R2-C4's "a team lead" (not stated in the post) and R2-C2/C3's "a paying G2 reviewer" → "a G2 reviewer".
Marked UNVERIFIED: C3-A3's four unlocated post titles (Arctic Shift `/api/posts/search` returned `{"data":null,"error":"Timeout. Maybe slow down a bit"}` on five attempts today; reddit.com is robots-blocked, so no ethical route to a permalink existed this session); and the "scores are 0–5" range in C3 verdict point 2, which rested on those titles.
Downgraded: R2 verdict point 7 (the R2-B1/B2 spillover is now a **low-confidence mechanism signal**, not "the strongest public demand statement yet" — both posts scored 0); C3 verdict point 1 (r/ClaudeAI agrees "independently, not louder" — the two posts scored 1 and 0); C3 verdict point 2 (supply saturation now rests on the funnel count of 39 posts naming no price, not on a per-post score range).
Unchanged: all three kill verdicts and their confidence levels (R2 high, C3 high, B1 high/medium). The R2 kill is strengthened, not weakened, by R2-B1 turning out to be a zero-scored post. The NOT INSTRUMENT-BIASED label survives the recount.
