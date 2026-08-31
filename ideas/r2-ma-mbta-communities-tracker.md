# MBTA Communities Act (Section 3A) Rezoning Tracker for Massachusetts

**Slug:** r2-ma-mbta-communities-tracker  |  **Track:** C  |  **Researched:** 2026-08-30  |  **Status:** researched  |  **Origin:** round 2 (asset-suggested)

## One-line pitch
A free public tracker of MBTA Communities Act (M.G.L. c.40A §3A) compliance status, district maps, deadlines and upcoming town votes for the 177 statutorily named Massachusetts municipalities, monetized by a $49–149/month alert feed for developers and land-use attorneys — an idea that is **already fully shipped, for free, by the Commonwealth itself**, roughly eight months after the last statutory deadline passed.

## Specific buyer
Intended: multifamily land-acquisition staff at Boston-area developers, land-use attorneys at MA firms (Bowditch & Dewey, Goulston & Storrs), housing advocacy orgs (Abundant Housing MA, CHAPA), MAPC and regional planning staff, journalists at Banker & Tradesman / CommonWealth Beacon.

Actual, after research: **there is no buyer left.** Every one of those parties is already served free and authoritatively by EOHLC's own published data suite, and the compliance event they would have been tracking has essentially concluded. As of 2026-07-22, EOHLC reports **153 of 177 municipalities fully compliant**; as of 2026-01-16, only **12** remained noncompliant (Carver, Dracut, East Bridgewater, Freetown, Halifax, Holden, Marblehead, Middleton, Rehoboth, Tewksbury, Wilmington, Winthrop), and news coverage through August 2026 shows Marblehead (May), Rehoboth (June), Tewksbury (June) and Dracut (re-voting August) working through that remainder. The tracked universe is ~12 towns and shrinking to zero.

## Pain evidence (verbatim, >= 5)

All quotes copy-pasted from pages fetched 2026-08-30. **Read the framing note after the quotes — it is the decisive finding.**

1. Boston Indicators, "The Surprising Lack of Good Permitting Data and What to Do about It," Boston Indicators, **October 31, 2025** — https://www.bostonindicators.org/upzone_update/bad-permit-data
   > "Homes in the construction pipeline should be readily countable, unlike, for example, grains of sand in Salisbury Beach. But go try and figure out how many homes, exactly, Massachusetts municipalities permitted last year, and last decade. The numbers slip through your fingers like sand."

2. Same source, same date:
   > "We don't have a system in place to count them thoroughly. We lack concrete numbers on most dimensions of residential projects that are under permit review or under construction statewide."

3. Same source, same date:
   > "The problem lies, first, in a system of self-reporting by city and town governments; some numbers get lost in their digital and paper files. Data reporting is a lift, so the ask has been left light, which is the second problem. The result is data with too many holes and too little detail."

4. Same source, same date — the manual-labor tell:
   > "Back in 2018, I called and emailed municipal planners and building inspectors across 100 cities and towns of Greater Boston, asking for their multifamily permit tallies, covering the years 2015 through 2017."

5. Same source, same date — on MAPC's existing free MassBuilds map:
   > "The map's data for the inner-core communities are in the best shape; entries get patchier further out from Boston."

6. An MBTA Communities engagement manager at CHAPA, quoted in "'It was too effing complicated': A pro-housing reckoning over MBTA Communities law," CommonWealth Beacon, **September 18, 2025** — https://commonwealthbeacon.org/government/state-government/it-was-too-effing-complicated-a-pro-housing-reckoning-over-mbta-communities-law/
   > "And many of them did, but it took so much effort, so much time, that I don't think we could realistically do it again for any other zoning reform. We've eaten up that political capital."

7. The executive director of Abundant Housing Massachusetts, same article, same date:
   > "We crafted this law in a way that we thought was responding to the unique aspect of local control, local decision making, Town Meeting form of government we have in Massachusetts, but that made it incredibly difficult"

   and, on the 177 municipalities having to vote in compliant zoning, that it "opens up a whole bunch of headaches".

8. A program manager for the MBTA Communities technical assistance program at the Massachusetts Housing Partnership, same article, same date:
   > "But the MBTA Communities model isn't ideal, she said, because of how much work it took to tailor each municipality's plan, even as organizations streamlined the process"

9. Outside counsel for the Town of Marshfield, at SJC oral argument, reported in "Were MBTA Communities costs unfair, or a self-imposed expense?", CommonWealth Beacon, **March 4, 2026** — https://commonwealthbeacon.org/housing/were-mbta-communities-costs-unfair-or-a-self-imposed-expense/
   > "Marshfield was forced to employ a person to develop zoning modeling, [counsel name redacted] told the court, and the town 'incurred expense associated with' navigating the 22 pages of compliance regulations."

**Framing note — why these quotes do not support the product.** Every complaint above is about the *work of complying* with §3A (writing zoning, running town meetings, hiring modelers) or about the *quality of statewide permit data*. **Not one person, anywhere I could reach, complains that they cannot find out which towns are compliant, where the 3A districts are, or when the votes are.** That is the thing this product sells, and the silence around it is total: zero Hacker News discussion of MBTA Communities zoning data (HN Algolia returns only 2014 transit-visualization comments), and GitHub search returns exactly **one** repository (`busebusee27/mbta_communities_zoning`, **0 stars**, last pushed 2025-05-30) across `MBTA communities zoning`, `mbta communities 3A`, and `massachusetts zoning tracker`. Reddit was unreachable (403 to every method, per prior runs today), so that channel is unverified — but a demand signal this absent everywhere else would be surprising to find only there.

## Willingness-to-pay evidence (>= 3)

1. **Zoneomics** (https://www.zoneomics.com/pricing, fetched 2026-08-30) — real, published, self-serve prices for zoning intelligence sold to "Brokers, Architects, Urban Planners, and Appraisers," and to "Appraisers, Lenders, Developers, Law Firms":
   - Essentials **$92/Month** — 1 user, 25 searches/month, overage **$4.25/search**, 1 Zoning Brief, "Additional Zoning Brief: $65 each"
   - Advanced **$279/Month** — 150 searches/month, overage **$2.50/search**, 5 Zoning Briefs, additional briefs $55 each
   - Enterprise — custom, 1000+ searches
   - Terms explicitly bar resale: "for internal business and research use only. No republishing, redistribution, or resale is allowed without written authorization. Applies to all plans."
   This proves the *category* has WTP at exactly the $49–149 band the brief guessed — but for parcel-level zoning lookups nationwide, not for a 177-town compliance status list.

2. **Banker & Tradesman** subscription (https://www.bankerandtradesman.com/subscribe/, fetched 2026-08-30) — MA real-estate professionals demonstrably pay for Massachusetts-specific market intelligence:
   - Digital: "$32 one month," "$365 one year," "$625 two years"
   - Digital + Print: "$42 one month," "$420 one year," "$730 two years"
   - New-subscriber offer: "try B&T online for just $9.99 for your first month!"

3. **BLDUP** (https://www.bldup.com/, fetched 2026-08-30) — a Boston-founded, now ten-market construction and property intelligence platform that sells precisely the downstream "pre-application filing feed" the brief names as the funnel destination: "Intent, design phase, and pre-approval data," "Verified decision-makers," "Trusted by 65,000+ Subcontractors." Pricing is demo-gated (no public price page; `/pricing` 404s), i.e. an enterprise sales motion. Its existence proves the adjacent market is real **and already taken in Boston**.

4. **Gridics** (https://www.gridics.com/pricing, fetched 2026-08-30) — sells MuniMap / CodeHUB / ZoneCheck to governments and PropZone / ZoneIQ / "Zoning Data API" to real estate. No public pricing; every path is "Request Demo." Another enterprise-priced incumbent in zoning data.

5. **Counter-evidence, and it is stronger than the above.** Money in this specific niche flowed to *grants and free nonprofit labor*, never to software subscriptions:
   - The MBTA Communities Catalyst Fund gives municipalities "grants ranging from $250,000 to $1 million" (CHAPA, 2024-10-03, https://www.chapa.org/housing-policy/mbta-communities).
   - CHAPA gave the technical assistance away: "From January 2023 until January 2026, CHAPA's MBTA Zoning Technical Assistance provided municipalities with the tools and guidance to navigate new zoning regulations... CHAPA helped 90 communities work on their zoning plans through this program" (https://www.chapa.org/mbta-zoning-ta, fetched 2026-08-30). **Note the past tense and the January 2026 end date.**
   - MAPC, Abundant Housing MA and Boston Indicators all publish their MBTA-C material free.

## Reachability (50 qualified buyers in 30 days, $0)
This is the one genuinely strong column, and it is why the idea is worth killing *carefully* rather than dismissing.

- Every institution named in this dossier is physically in Boston, mostly within a few T stops of Northeastern: CHAPA (One Beacon Street, 5th Floor), Abundant Housing MA (50 Milk Street, 16th Floor), MAPC, Boston Indicators (at The Boston Foundation), EOHLC.
- AHMA runs open public events (e.g. "2026 North Shore YIMBY Summer Social," posted 2026-08-03) and a "Housing Abundance Symposium"; CHAPA runs events and a job board; both list staff pages and staff emails publicly.
- EOHLC publishes a direct contact channel for this exact program: EOHLC3A@mass.gov.
- The EOHLC District Atlas XLSX itself contains a `Letter_Recipient` column of **municipal contact emails** for all compliant towns (a mix of role mailboxes such as `manager@actonma.gov` and name-derived personal mailboxes for individual staff, which are not reproduced here) — 150+ municipal contacts, one download away. (Ethically: that is a legitimate public business contact list, but it is a cold-outreach list, and unsolicited product email to it would be spam under the principal's own rules. Use events and warm intros instead.)
- Town meetings, planning board hearings and Select Board meetings are open, posted, and free to attend.

Verdict on reachability: **50 qualified conversations in 30 days for $0 is genuinely achievable.** The problem is not reaching them; it is that they do not want this.

## Wedge
The intended wedge — "be the free public tracker, then charge for alerts" — **has no opening.** The Commonwealth ships the free tracker, at higher fidelity than a solo student can match, and updates it monthly:

- **MBTA Communities District Atlas** (https://www.mass.gov/info-details/mbta-communities-district-atlas): "153 communities have achieved full compliance with the MBTA Communities Act as of July 22nd, 2026," covering "475 zoning districts in compliant municipalities" and "29,599 parcels in compliant districts."
- **Interactive ArcGIS webmap** of every district: https://massgis.maps.arcgis.com/apps/instant/atlas/index.html?appid=f39b1aba608f4bdfbc55998d89445c26
- **Tabular atlas, 7.4 MB XLSX**, verified downloadable from public S3 on 2026-08-30: `https://s3.dualstack.us-east-1.amazonaws.com/download.massgis.digital.mass.gov/shapefiles/state/MBTACommunitiesAtlas_2026-07-22_WithNotes.xlsx` — seven sheets (`Municipality`, `District`, `Parcel`, `MunicipalityNotes`, `MunicipalityChanges`, `DistrictNotes`, `DataDictionary`) with columns including `Status`, `TransitCat`, `MinMFUC`, `2020HU`, `MFUC`, `Letter_LandArea_Req/Sub/Det`, `Letter_UnitCapacity_Sub/Det`, `Letter_Recipient`, `Letter_DateSent_Month/Day/Year`, `MatchStatus`, `Notes`, `HLCChanges`.
- **Compliance status CSV**, updated monthly: `https://www.mass.gov/files/csv/2026-08/Compliance Status Sheet as of 8-11-26.csv`
- **3A Development Tracker CSV** — the state already runs the development tracker: `https://www.mass.gov/files/csv/2026-07/3A Development Tracker as of 7-30-26.csv`
- Shapefiles / spatial data via MassGIS, plus District Approval Letters, Pre-Adoption Feedback Letters, submitted Action Plans, the compliance model, and the 760 CMR 72 regulations, all as downloadable documents.
- EOHLC has staffed up for this permanently: Boston Indicators reports (2025-10-31) that it hired a former MAPC housing-data lead to run a housing data team for the state agency. *(Paraphrase — the source sentence names the individual, so it is not quoted here.)*

The only residual friction worth naming: those CSVs have **hand-dated filenames with no stable URL, no API, and no changelog**, so nobody can diff month over month. That is a real gap. It is also a ~$0 gap — the answer is a cron job and a git repo, not a $99/month subscription.

## Build estimate
**2–4 agent-days** for a genuinely complete version, which is itself part of the problem: the low build cost is a symptom of the state having done the work.

- Ingest: parse the MassGIS atlas XLSX (7 sheets) + the two EOHLC CSVs + MassGIS shapefiles. ~0.5 day.
- Static site + map: the ArcGIS webmap already exists and can be linked; a Leaflet/MapLibre render of the district shapefiles is ~1 day.
- Monthly diff/changelog job: fetch, hash, diff, publish "what changed" — ~0.5 day. This is the only novel bit.
- Town-vote/hearing calendar: the actual work. Requires monitoring ~12–24 town websites for agendas. Not automatable cleanly (177 different CMSes, many PDF-only), and the payoff shrinks as towns comply. 1–2 days for a partial version, then ongoing manual labor forever.
- **Blocker to check first:** mass.gov returns **HTTP 403 to every automated fetch** — WebFetch and curl, HTML pages and CSV files alike (verified repeatedly on 2026-08-30). Only the MassGIS S3 bucket served automated requests. So the pipeline needs either a manual/browser-assisted download step or MassGIS-only sourcing, and the principal must read mass.gov's terms before automating anything against it.

Reusable assets: X-Scraper snapshot-diff for dataset change detection.

## Unit economics
- Costs: $0 hosting (Cloudflare Pages / GitHub Pages, static), ~$12/yr domain, $0 data (state publishes it). **Well under the $40/month burn cap** — this is not where the idea fails.
- Revenue, generously modeled: the plausible paying universe is MA land-use attorneys and multifamily acquisition staff who care about §3A specifically. Even 20 subscribers at $99/month = $1,980/month, and 20 is not defensible when EOHLC publishes the same facts free with the Commonwealth's authority behind them and Boston Indicators emails the analysis free.
- Realistic revenue: **$0.** The free substitute is better, official, and arrives in the buyer's inbox already.
- The one durable output is non-monetary: a public, well-built civic-data artifact with the principal's name on it.

## Risks
1. **Timing risk — realized, not speculative.** All statutory deadlines have passed (rapid transit 12/31/2023; commuter rail and adjacent 12/31/2024; adjacent small town 12/31/2025; the catch-up deadline 7/14/2025). CHAPA's technical assistance program closed in January 2026. The subject of the tracker is finishing.
2. **Incumbent risk — the incumbent is the state.** EOHLC publishes the map, the parcel data, the status CSV, the development tracker, and the determination letters, and has a dedicated housing data team. You cannot out-authority the agency that issues the determinations.
3. **Free-content risk.** The analysis lane is occupied by Boston Indicators' *Upzone Update* newsletter — expert-authored and funded by The Boston Foundation. It is syndicated onward to StreetsblogMASS. Competing with free, expert, philanthropically funded content as a solo junior is not a fight worth taking.
4. **Thin underlying deal flow.** Coverage from January 2026 reports researchers finding the law's benefits "modest," with figures around 5,200–7,000 homes built or in development statewide. That newsletter's own February 2026 brief on Newton's MRT districts counts "eight MRT adaptive-reuse projects... a potential total of 49 homes—34 of them net new," and concedes "the impact remains limited." Alert feeds need deals to justify their price.
5. **Data-access risk.** mass.gov 403s all automated fetching; the pipeline depends on MassGIS S3 or manual download, and on mass.gov's terms permitting it.
6. **Ethics — clean, and worth noting.** All data is published, downloadable, and license-free; no scraping behind logins, no paywalls, no personal information beyond municipal officials' public business contacts. This idea fails on market, not on ethics.

## Kill criteria
Stated as thresholds; all four were tripped during research, which is why the verdict is a kill rather than a test plan.

1. *Kill if the state or a funded nonprofit already publishes the tracker free.* — **Tripped.** EOHLC publishes the atlas, webmap, parcel XLSX, status CSV, development tracker CSV and shapefiles; MAPC publishes MassBuilds; Boston Indicators publishes Upzone Update.
2. *Kill if the compliance event is more than 80% resolved.* — **Tripped.** 153/177 fully compliant as of 2026-07-22 (86%); 165 of 177 compliant or in progress as of 2026-01-16 (93%).
3. *Kill if no verbatim complaint anywhere describes difficulty tracking §3A status.* — **Tripped.** Nine verbatim complaints found about compliance *work* and permit *data quality*; zero about tracking.
4. *Kill if there is no demand signal in developer/OSS channels.* — **Tripped.** One GitHub repo, zero stars; zero HN discussion.

## Incumbents and adjacent players
| Player | What it does | Price |
|---|---|---|
| **EOHLC / MassGIS (the Commonwealth)** | District Atlas (153 munis, 475 districts, 29,599 parcels), ArcGIS webmap, 7.4 MB parcel-level XLSX, monthly Compliance Status CSV, 3A Development Tracker CSV, shapefiles, approval letters, compliance model | **Free** |
| **MAPC — MassBuilds** (massbuilds.com/map) | Statewide building/pipeline map: addresses, height, parking, status, year completed, dwelling units, affordable units | **Free** |
| **Boston Indicators — *Upzone Update*** (The Boston Foundation) | Ongoing newsletter and briefs analyzing MBTA-C compliance efforts; syndicated to StreetsblogMASS | **Free** |
| **CHAPA — MBTA Zoning TA** | Direct technical assistance to municipalities; helped 90 communities, 97% approval rate | **Free; program ended Jan 2026** |
| **Abundant Housing MA — MBTA Communities Toolkit** | One-pagers, FAQ, glossary, messaging guides, testimony guides, training videos | **Free** |
| **BLDUP** | Boston-founded construction/property intelligence: "Intent, design phase, and pre-approval data," 10 markets, "65,000+ Subcontractors" — occupies the adjacent pre-application-feed idea | Demo-gated |
| **Zoneomics** | National parcel-level zoning search, briefs, API, "Bassett AI" | $92 / $279 per month; $65/brief |
| **Gridics** | Zoning data for governments and real estate (MuniMap, CodeHUB, ZoneCheck, PropZone, ZoneIQ, API) | Demo-gated |
| **Banker & Tradesman** | MA banking + CRE trade press; the incumbent for "what MA real estate pros pay to read" | $365/yr digital |
| **CommonWealth Beacon / Streetsblog MASS** | Free, sustained MBTA-C reporting (Milton, Marshfield SJC, AG suits, town-by-town) | Free |

## Score
Weighted 1–5. Fit is TBD per instructions.

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Time to first dollar | ×3 | **1** | The free tier cannot be a lead magnet when EOHLC's own atlas outranks and out-authorities it, and the paid alert tier has no live deadline to alert against — the last statutory deadline passed 2025-12-31 and CHAPA closed its TA program in January 2026. |
| Reachability by a student | ×3 | **4** | CHAPA (One Beacon St), AHMA (50 Milk St), MAPC, Boston Indicators and EOHLC are all within a short T ride of Northeastern, run open public events, publish staff contacts and a program inbox (EOHLC3A@mass.gov), and town meetings are free to attend — 50 conversations in 30 days at $0 is real. |
| Pain × frequency | ×2 | **2** | Nine verbatim quotes document real pain in *doing* §3A compliance and in MA permit-data quality, but not one describes trouble *tracking* compliance status — and the compliance work that generated the pain is now ~86% finished. |
| WTP evidence | ×2 | **2** | Zoneomics ($92–$279/mo) and Banker & Tradesman ($365/yr) prove the category pays for MA zoning and market intel, but every dollar that moved in this specific niche went to $250k–$1M municipal grants and free CHAPA/MAPC/AHMA labor, and no one pays for §3A tracking today. |
| Fit with assets and strengths | ×2 | **2** | Research/drafting fit; no GIS or crawler assets. |
| Compounding | ×2 | **2** | A single statute in a single state whose enforcement window is closing does not compound; the reusable part is the generic "diff a government dataset on a schedule" pipeline, which belongs to a different idea. |
| Risk (5 = low) | ×2 | **3** | Legal and ethical risk is genuinely low (public, downloadable, license-free data, no scraping behind logins), but market risk is near-total and mass.gov 403s every automated fetch, forcing a manual or MassGIS-only ingest path. |
| Ceiling | ×1 | **1** | The addressable universe is a few hundred MA professionals already served free, against a law credited with only ~5,200–7,000 homes statewide; a realistic best case is a few thousand dollars a year, not a business. |
| Build cost (5 = cheap) | ×1 | **4** | 2–4 agent-days on state-published XLSX/CSV/shapefiles, $0 hosting and ~$12/yr domain, comfortably under the $40/month cap — cheap, but cheap because the state already did the hard part. |

**Subtotal excluding fit: 38 / 80.**
(3 + 12 + 4 + 4 + 4 + 6 + 1 + 4 = 38)

## Verdict
**Kill.** Not because the research came up empty — it came up rich, and every rich finding pointed the same direction.

Three facts, any one of which would be sufficient:

1. **The Commonwealth already ships the product, free, monthly, at parcel grain.** An ArcGIS webmap of all 475 compliant districts, a 7.4 MB seven-sheet XLSX down to 29,599 individual parcels with determination-letter dates, a monthly compliance status CSV, a 3A Development Tracker CSV, and MassGIS shapefiles. EOHLC hired MAPC's housing data lead to keep it that way. There is no free tier to win.
2. **The event being tracked is over.** Every statutory deadline has passed; 153 of 177 towns are fully compliant as of 2026-07-22; the twelve holdouts named in January 2026 are being picked off month by month through 2026. CHAPA's technical assistance program is described on its own site in the past tense, "From January 2023 until January 2026." A tracker whose subject resolves to zero is a wasting asset.
3. **Nobody complains about the thing the product solves.** Nine verbatim complaints across two well-sourced outlets, all about the burden of *complying* or the poverty of statewide *permit* data — none about finding compliance status. One GitHub repo with zero stars. Zero HN discussion.

The idea's one real strength, reachability, is worth banking separately: the principal can meet CHAPA, AHMA, MAPC, Boston Indicators and EOHLC staff in person within a month, for free, and those relationships are the actual asset this research turned up.

Two salvage notes, honestly bounded. First, the EOHLC CSVs really do carry hand-dated filenames with no stable URL and no changelog — a public "diff of Massachusetts housing datasets" repo is a genuine (small) civic contribution and a strong career-capital artifact for a CS+Math junior, at ~1 agent-day and $0. It is not a business; it is a calling card, and it should be scoped as one. Second, the brief's downstream idea — a Massachusetts pre-application filing feed — is where the money in this space actually lives, and BLDUP already occupies it in Boston with "intent, design phase, and pre-approval data" and 65,000+ users. Any move in that direction needs to start from what BLDUP does *not* cover, not from §3A.

## Research log
Web search budget for the session was exhausted before this dossier began (200/200 WebSearch calls), so all research ran through WebFetch, curl, and public APIs.

**Blocked / degraded (verified 2026-08-30):**
- `mass.gov` — HTTP 403 to WebFetch *and* to curl with a browser UA, on both HTML pages and `/files/csv/` downloads. Worked around entirely via the Wayback Machine (snapshot `20260826140428`, four days old) and the public MassGIS S3 bucket, which served requests normally.
- `bing.com` — returns a degraded SERP to anonymous curl: ten identical generic "MBTA" brand results for every query, verified across four unrelated queries. Unusable.
- `duckduckgo.com` (html and lite endpoints) — HTTP 202 challenge page. `searx.be` — antibot captcha. `mojeek.com` — empty result set.
- `indeed.com` — HTTP 403 (contradicting the brief's note that Indeed works; the `/jobs?q=...&l=...` endpoint was refused).
- `reddit.com` — not attempted, per the standing note that it 403s every method today. This is the one channel left unchecked.
- `massbuilds.com/map` — connection timed out; assessed indirectly through that newsletter's description of it.
- `planetizen.com` and `bostonindicators.org` — one 404 (guessed URL) and one 504 respectively; both recovered on retry or via the correct path.

**Worked:** Wayback Machine, MassGIS S3, Google News RSS (`news.google.com/rss/search`, 100 items on the core query), HN Algolia API, GitHub search API, `commonwealthbeacon.org`, `mass.streetsblog.org`, `bostonindicators.org`, `abundanthousingma.org`, `chapa.org`, `mapc.org`, `zoneomics.com`, `gridics.com`, `bldup.com`, `bankerandtradesman.com`.

**Sequence:**
1. HN Algolia for `MBTA Communities` and `zoning data` — nothing relevant; only 2014 transit-visualization comments.
2. mass.gov 403 → Wayback snapshot of the §3A program page. Extracted the full deadline table, the two forms of compliance, and every published artifact link. **This is where the idea died:** the "Submission Statuses" CSV, the District Atlas, and an EOHLC-run "3A Development Tracker" were all already there.
3. Followed the atlas link (also via Wayback) → ArcGIS webmap, MassGIS shapefiles, and the tabular XLSX on public S3. Downloaded the 7.4 MB XLSX and read its sheet names and column headers directly to confirm the data is parcel-level and includes determination-letter metadata.
4. Google News RSS across five queries to establish the 2026 state of play: the twelve holdouts, the AG's January 2026 suit against nine towns, the Marshfield SJC argument, and town-by-town capitulations through August 2026.
5. Fetched CommonWealth Beacon (two articles), StreetsblogMASS (holdouts), and Boston Indicators (two Upzone Update briefs) for verbatim quotes and for the incumbent-content picture.
6. Checked the nonprofit lane: AHMA homepage and MBTA Communities Toolkit, CHAPA's MBTA Communities page and MBTA Zoning TA page (the January 2026 program end date is the sharpest single timing signal in the dossier), MAPC.
7. Pricing archaeology: Zoneomics (public prices), Gridics (demo-gated), BLDUP (demo-gated, adjacent-market incumbent), Banker & Tradesman (public prices).
8. Demand check: GitHub search API across three query variants — one repo, zero stars.

**Not done, and it would not change the verdict:** Reddit (blocked), Capterra/Trustpilot 2–3 star reviews for Zoneomics and Gridics (would sharpen the incumbent picture but not revive a market whose event has concluded), and reading the compliance status CSV itself (blocked by mass.gov's 403; the atlas XLSX and the July 22, 2026 headline figures cover the same ground).

## Verification (2026-08-30, adversarial pass)
- Quotes: 17 checked, 17 verified, 0 unfetchable, 0 not found/altered

**Claims**
- *EOHLC ships the free tracker (atlas, webmap, parcel XLSX, status CSV, dev-tracker CSV, shapefiles).* **Confirmed, and understated.** Atlas page text verified verbatim via Wayback (`https://web.archive.org/web/20260830080158/https://www.mass.gov/info-details/mbta-communities-district-atlas`): "153 communities have achieved full compliance ... as of July 22nd, 2026", "475 zoning districts", "29,599 parcels". XLSX live on S3 (HTTP 200, Last-Modified 2026-07-30). Both CSV links present on the live page as archived 2026-08-26.
- *"no API, no changelog."* **Partly refuted.** EOHLC/MassGIS publish a public, anonymous, queryable ArcGIS REST feature service: `https://services1.arcgis.com/hGdibHYSPO59RG1h/arcgis/rest/services/MBTA_Communities_3A_District_Atlas/FeatureServer` — layers `MBTA 3A Districts` / `MBTA 3A Residensity Parcels` / `Transit Stations Half-Mile Radii`; `?where=1=1&returnCountOnly=true` returns `{"count":475}`. The "no API" gap is real only for the two hand-dated CSVs.
- *CSVs updated "monthly."* **Partly refuted.** Wayback CDX for `mass.gov/files/csv/*` shows irregular cadence — five distinct Compliance Status Sheets in Dec 2024 alone (12-4, 12-12, 12-13, 12-17, 12-18, 12-23), then multi-month gaps. The diff gap is bigger than "monthly" implies.
- *All statutory deadlines have passed.* **Confirmed** from the state's own file: archived `Compliance Status Sheet as of 8-14-25.csv` (177 rows) has a `Compliance Deadlines` column with exactly `12/31/2023` (11), `12/31/2024` (103), `7/14/2025` (28), `12/31/2025` (35).
- *Twelve holdouts as of 2026-01-16.* **Confirmed verbatim**, Streetsblog MASS 2026-01-16 — Carver, Dracut, East Bridgewater, Freetown, Halifax, Holden, Marblehead, Middleton, Rehoboth, Tewksbury, Wilmington, Winthrop.
- *CHAPA TA program ended Jan 2026.* **Confirmed verbatim** at https://chapa.org/mbta-zoning-ta — "From January 2023 until January 2026 ... 97% ... helped 90 communities."
- *mass.gov 403s every automated fetch.* **Confirmed** — 403 to WebFetch and to curl with a browser UA, on both `/info-details/` pages and `/files/csv/` downloads, re-tested 2026-08-30.
- *"GitHub search returns exactly one repository ... 0 stars."* **Refuted as stated.** True only for the three narrow queries used. The obvious query `MBTA Communities` returns **6** repos, including `fdhidalgo/mbta-communities-data-pipeline` (1★, R + DuckDB, "processes 12GB+ of spatial data across 177 Massachusetts municipalities ... to support web visualization") and `duncanburns2013-dot/MBTA-Communities-Act` (created 2026-02-08, live HTML dashboard, "$4.4 billion in unfunded costs"). Direction of the finding survives; the number does not.
- *MassBuilds is a live free incumbent.* **Unverifiable / likely down.** `massbuilds.com` 301s to `www.massbuilds.com`, which resolves (184.72.253.82) but times out; no Wayback capture since 2026-05-20. Never independently verified in the dossier either (it was assessed "indirectly through [that newsletter's] description").
- *Zoneomics $92 / $279, $65 and $55 briefs, resale bar; B&T $32/$365/$625 and $42/$420/$730 and $9.99 intro; BLDUP "Intent, design phase, and pre-approval data" / "Verified decision-makers" / "Trusted by 65,000+"; Gridics demo-gated; CHAPA Catalyst "$250,000 to $1 million"; AHMA 50 Milk St + 2026-08-03 North Shore YIMBY Summer Social; the newsletter's Newton MRT brief "49 homes—34 of them net new" / "the impact remains limited."* **All confirmed verbatim** against the live pages.

**Score challenges**
- **Compounding 2 → 3.** Massachusetts zoning is in an *active* statewide reform cycle, not a closing one (see Missing). A pipeline built on MA zoning-compliance data has a live successor event 65 days out. Still one state, so 3 not 4.
- **Ceiling 1 → 2.** The ceiling was computed against a fixed, shrinking universe (12 holdouts, ~7,000 homes). If Question 7 passes on 2026-11-03 the compliance universe becomes 351 municipalities on a brand-new standard. Still not a business for a solo junior; the "few thousand dollars a year" floor is too low as a *ceiling*.
- **Risk (5 = low) 3 → 4.** The stated data-access risk is largely dissolved by the public ArcGIS FeatureServer plus the MassGIS S3 bucket; mass.gov's 403 blocks two 2 KB CSVs, not the pipeline. Market risk belongs in Time-to-first-dollar and Ceiling, where it is already scored.
- **Vague/unmeasurable kill criteria.** #3 ("no verbatim complaint *anywhere*") is unfalsifiable and was tested against two outlets, HN, and GitHub with Reddit admittedly unchecked. #4 ("no demand signal in developer/OSS channels") was measured with three unnaturally narrow queries and tripped on a count that a fourth, obvious query refutes. Both should have been stated as "in channels X, Y, Z, searched as follows."

**Missing**
- **Massachusetts Question 7 is certified for the November 3, 2026 ballot** — "Require cities and towns to allow single-family homes on residentially zoned lots that meet minimum standards of at least 5,000 square feet in area," with 50 ft frontage and public sewer/water. Nine statewide measures certified as of 2026-08-28 (Ballotpedia). This is a statewide preemption over all 351 municipalities, voted 65 days after this dossier was written, and the dossier does not mention it.
- **The Zoning Act was overhauled in the FY27 budget, six weeks before this dossier.** "Budget bill brings seismic changes to state's Zoning Act" (Mass. Lawyers Weekly, 2026-08-03); "Significant Amendments to Massachusetts Zoning Act" (**Bowditch & Dewey**, 2026-07-15 — one of the dossier's own named buyers wrote the client alert); variance requirements eased (Smart Cities Dive, 2026-07-16).
- **Senate passed duplexes by-right in residential neighborhoods** (AHMA press release, 2026-07-27), pending in the Economic Development bill.
- **The Marshfield SJC case appears still undecided.** Argued 2026-03-04; no decision found in news through 2026-08-30. An open constitutional challenge to the entire law sits over the dataset; the dossier mined the argument for a quote but never asked whether the case had resolved.
- **Compliance is not a monotone counter.** Marblehead voters *overturned* adopted 3A zoning in July 2025; its May 2026 "golf course" compliance drew AG "recourse" talk (2026-05-13); Hopkinton amended its MBTA zoning at May 2026 Town Meeting. The Atlas page itself says it covers only municipalities that "completed HLC's compliance review process" — so the state's flagship map is *not* the tracker for the 24 towns that are conditional, under review, or noncompliant.
- **A "Repeal Multi-Family Zoning Requirements in MBTA Communities" initiative was filed for 2026 and did not make the ballot.** The repeal threat is absent from the dossier entirely.
- **The buyer list is one-sided.** Every named buyer is pro-housing. The anti-3A side is organized, litigating, and building its own free artifacts (the Feb 2026 "follow the money" dashboard). Not obviously monetizable, but unexamined.
- **Still unchecked:** Reddit (403 by rule), Capterra/G2 reviews for Zoneomics and Gridics, and the live 2026 CSVs themselves (no Wayback capture exists for any 2026 Compliance Status Sheet).

**Overall: mostly-trustworthy** — the quote work is exact (17/17 verbatim, correct dates, correct titles) and the kill's load-bearing fact is confirmed and even understated, but two supporting claims are overstated ("exactly one repo", "no API"), one named free incumbent is unverifiable, and the dossier missed a certified statewide zoning ballot question and a July 2026 Zoning Act overhaul that refute its "nothing left to track" framing without rescuing this particular product.


## Final score (main agent, 2026-08-30)
- Fit with assets and strengths: **2/5** ×2 — Research/drafting fit; no GIS or crawler assets.
- Reusable assets: X-Scraper snapshot-diff for dataset change detection.
- Subtotal as researched: 38/80 · after adversarial verification: **43/80** (comp 2→3, ceil 1→2, risk 3→4)
- **Total: 47/90**
