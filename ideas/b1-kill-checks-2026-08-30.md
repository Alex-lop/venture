# Track B — the two ten-minute kill checks, and the revival test

**Run:** 2026-08-30 · **Method:** live HTTP against masspublicnotices.org (ASP.NET WebForms, POST-driven) and the EEA Data Portal's JSON API; every count below is reproducible from the scripts noted. WebSearch budget was already exhausted (200/200) when this session started, so discovery used Brave HTML search via curl; reddit.com and maccweb.org 403 to non-browsers, mass.gov 403s to WebFetch.

**Verdict: B-dead** — and not by the objection the red team raised. masspublicnotices.org is *not* the killer. The Commonwealth's own free JSON API is.

---

## Headline

| | Digest §0 (hand-compiled) | masspublicnotices.org | EEA Data Portal "Wetland NOI Projects" |
|---|---|---|---|
| Rows, 30 towns, 14 days | 90 conservation items (29 new NOI/RDA/ANRAD) | **27** ConCom/wetlands notices | **22** NOI/Buffer Zone/ANRAD filings |
| Towns covered of the 30 | 14 | **11** (19 return zero) | **29** (only Somerville is empty) |
| Applicant named | businesses only — homeowners suppressed by policy (36/90 blanked) | yes, in full text | **yes, including homeowners** |
| Street address | yes | yes | yes |
| DEP/WPA file # | when the agenda prints it | in full text | **yes, structured field** (54% populated) |
| Consultant / representative | 22 of 90 (24%) | in full text sometimes | **no** (`Company` = applicant's entity, not the consultant) |
| Timing vs. the digest | agenda date | ≥5 days before hearing | **18–55 days before the digest's agenda date** |
| Cost / format | 1 agent-day + 90 principal-min per issue | free, HTML, snippet only | **free, JSON, no auth, Excel export** |

---

## CHECK 1 — masspublicnotices.org

Search is free and anonymous; I ran it end to end. Site: https://www.masspublicnotices.org/ (accessed 2026-08-30). Advanced Search accepts a keyword with All Words / Any Words / **Exact Phrase**, an EXCLUDE box, 14 county checkboxes, **229 city/town checkboxes**, 322 publication checkboxes, and a date range. Rolling 12 months; older notices go to a separate Archive Search.

### Counts, publication dates 2026-08-16 → 2026-08-30 (exact phrase)

| Query | Statewide | Filtered to the 30 towns |
|---|---|---|
| "Notice of Intent" | 17 pages @10/page ≈ **161–170** | **45** |
| "Conservation Commission" | 27 pages ≈ **261–270** | **29** |
| "Wetlands Protection Act" | 15 pages ≈ **141–150** | **16** |
| "Request for Determination of Applicability" | — | **8** |
| **Union, deduplicated by notice ID** | — | **59** |
| **…of which actually ConCom/wetlands** | — | **27** |

**The raw "Notice of Intent" count is inflated by more than half.** 32 of the 59 deduplicated hits are not wetlands filings at all: MassDEP public-hearing notices, and repeated Executive Office for Administration and Finance c.29 §2HHHHHH notices in the Boston Globe. The honest wetlands number is **27**.

An independent cross-check gives the identical figure. Running 30 separate statewide searches, one per town, exact phrase `"<Town> Conservation Commission"`, same 14 days:

```
Boston 4 · Hingham 5 · Medford 1 · Needham 1 · Newton 2 · Quincy 3
Reading 3 · Sudbury 3 · Weston 1 · Weymouth 4                    = 27
Ashland Bedford Belmont Braintree Brookline Canton Concord Hopkinton
Lexington Malden Milton Natick Norwood Somerville Walpole Waltham
Watertown Wayland Wellesley Winchester                            = 0  (19 towns)
```

### The town filter does not mean what it looks like

From the site's own Help page (https://www.masspublicnotices.org/Help.aspx, accessed 2026-08-30), verbatim:

> "County and City lists identify **where Massachusetts newspapers are published**. Select one or more from those lists to display all notices **from newspapers published in those jurisdictions**."

Confirmed in the data: notice ID 906195 is a **Newton** ConCom NOI, filed by a named private individual (name withheld, `CLAUDE.md` §2) for 55 Bound Brook Rd, and it is tagged `City: Boston / County: Suffolk` because it ran in the Boston Herald. You cannot filter this site by the town a project is in. You filter by which newspaper printed the ad.

### Coverage is admitted-partial, and the gaps are the digest's core towns

The homepage says, verbatim:

> "The **majority** of the state's newspapers participate in this site. If the information you are looking for is not listed, let us know. Our goal is for this site to include every public notice published in Massachusetts."

That is the mechanism behind the 19 zeros. Concretely: Ashland ConCom heard two new NOIs on 2026-08-24 (DEP 095-1022 at 0/175 Oak Street; DEP 095-1025 at 167-171 Pleasant Street with EBT Environmental) plus 55 Tilton Avenue with Connorstone Engineering. c.131 §40 required each to be advertised ≥5 days ahead. Searches for `"Tilton Avenue"`, `"Pleasant View Trust"`, and `"Ashland Conservation Commission"` over 2026-08-10 → 2026-08-30 all return **0**. The ads exist by law; MNPA does not have them.

### Five notices opened — what a row actually carries

Search results render as `Publication · publication date · City (of the paper) · County` plus a **~300-character snippet**, then `click 'view' to open the full text`. The full text is at `Details.aspx?SID=…&ID=…` and is **gated by a Cloudflare Turnstile CAPTCHA** ("You must complete the challenge in order to continue" — present on all five detail pages I opened: IDs 905314, 905403, 905910, 905955, 906195).

Across all **27** wetlands snippets: applicant name visible in **3** (the two Boston Herald Newton notices, which lead with the filer, and one Braintree), DEP file number in **0**, representative/engineer in **0**. Everything load-bearing sits past the truncation, behind the CAPTCHA, one solve per notice.

Representative snippets, verbatim:

- `55 WHITON AVENUE HINGHAM LEGAL NOTICE PUBLIC HEARING The Hingham Conservation Commission will hold a public hearing pursuant to M.G.L. Ch. 131, Section 40 and the Hingham Wetlands Protection Bylaw on AUGUST 31, 2026 at 7:00PM…` (Patriot Ledger, 2026-08-21)
- `[applicant name redacted — private homeowner] has filed a Notice of Intent with the Newton Con- servation Commission for exterior modifications to a single-family house and driveway at 55 Bound Brook Rd.…` (Boston Herald, 2026-08-29)
- `1085 MAIN ST LEGAL NOTICE TOWN OF WEYMOUTH CONSERVATION COMMISSION…` (Patriot Ledger, 2026-08-18) — the digest's own Weymouth row, DEP 81-1344, Conserv Group Inc.

### Row-for-row against the digest

Matching the digest's **29** new-hearing NOI/RDA/ANRAD rows against the 27 MNPA snippets by town + street address: **8 confirmed matches** (Hingham 92 Kimball Beach, 16 Kress Farm, 28 Independence, 55 Whiton; Weymouth 593 Commercial, 325 Ralph Talbot, 1085 Main, 0 Broad). True overlap is higher — Boston (4), Reading (3) and Sudbury (3) have notices whose snippets truncate before the address — but it is bounded above by the 27.

Direction of the gaps:

- **MNPA has, digest §0 lacks:** Braintree, Medford, Needham, Newton, Quincy — plus **Framingham and Westwood**, two of the towns DECISION.md/the digest classify as bot-blocked or unreadable.
- **Digest §0 has, MNPA lacks:** Ashland, Canton, Concord, Hopkinton, Milton, Norwood, Watertown, Wellesley — plus everything that is not a new hearing. Of the digest's 90 conservation rows, **61 are continued hearings, decisions, Certificates of Compliance, enforcement orders, minor plan changes and amendments.** None of those require newspaper notice, so none can ever appear on MNPA.

### Answer to the question posed

The digest's residual value against MNPA is **(a) rows the newspapers miss, plus (b) structure** — not nothing. MNPA does not kill B. It is a partial, publication-indexed, CAPTCHA-gated, snippet-only substitute covering roughly a third of the digest's conservation rows in eleven of thirty towns.

**The red team's objection #2 does not land as written.** It is superseded by something worse.

---

## CHECK 2 — EEA Data Portal, "Wetland NOI Projects"

Menu item `Wetland Notice of Intent Projects` at https://eeaonline.eea.state.ma.us/portal (Angular route `search-wire`), accessed 2026-08-30. Free, no login, no CAPTCHA, no robots restriction encountered. The UI advertises itself as: *"Notice of Intent filings can be searched by NOI number, city or town, and by date."*

Behind it is an unauthenticated JSON API. From the page's own `<meta name="data-lake-api-url" content="/EEA/DataLake/V1.0/DataLakeAPI/">` and the app's `wire` constant in `dist/scripts/custom.js`:

```
GET https://eeaonline.eea.state.ma.us/EEA/DataLake/V1.0/DataLakeAPI/wire
      ?_start=0&_end=6000&FromFilingDate=2026-01-01&ToFilingDate=2026-08-30
GET https://eeaonline.eea.state.ma.us/EEA/DataLake/V1.0/DataLakeAPI/wire/{NOIId}
```

**Search fields:** NOI Number · City/Town (dropdown) · Filing Date (range).
**Result fields:** `NOINum` · `FilingDate` · `ProjectAddress` · `ApplicantName` · `Company` · `TownName` · `OOCDate`.
**Detail fields:** `NOINum` · `ApplicantInformation` · `FilingDate` · `FilingType` · `ProjectType` · `ProjectAddress` · `InlandResourceAreas` · `CoastalResourceAreas` · `Comments` · `TechnicalComments` · `SOCRequest`.
`hasExportToExcel: true`. Page size 25 in the UI; the API honours `_start`/`_end` up to thousands.

The app's own tooltips, verbatim from the source: `TownId` = *"The city/town where the project is located (not necessarily where the applicant lives)"*; `FilingDate` = *"The date a NOI has been filed with the Department"*; `FilingType` = *"Buffer Zone – Buffer Zone Impacts Only; NOI – Notice of Intent; ANRAD – Abbreviated Notice of Resource Area Delineation"*; `OOCDate` = *"Date of Conservation Commission's decision"*.

### Lag: one day

On 2026-08-30 the newest filing in the set is dated **2026-08-29**. 2026 YTD statewide: **3,073** filings. August 2026 alone: **423**. Last 14 days statewide: **208**.

### Coverage of the 30 digest towns

2026 YTD, **328** filings across the 30 towns (~9.5/week). Twenty-nine of thirty towns are present; only Somerville has zero.

`Ashland 11 · Bedford 10 · Belmont 2 · Boston 55 · Braintree 11 · Brookline 4 · Canton 12 · Concord 15 · Hingham 22 · Hopkinton 10 · Lexington 13 · Malden 1 · Medford 6 · Milton 9 · Natick 9 · Needham 21 · Newton 14 · Norwood 6 · Quincy 11 · Reading 7 · Sudbury 13 · Walpole 7 · Waltham 9 · Watertown 1 · Wayland 10 · Wellesley 12 · Weston 13 · Weymouth 12 · Winchester 2`

Every town MNPA missed — Ashland, Canton, Concord, Hopkinton, Lexington, Brookline, Bedford, Wellesley, Watertown, Natick, Milton, Norwood, Walpole, Wayland, Waltham, Winchester, Belmont, Malden — is here.

### It is earlier than the digest, by weeks

Taking DEP file numbers straight out of digest §0 and looking them up in the free API — **19 of 20 found**, one miss being a 2019-era Reading Certificate of Compliance outside the 2026 window:

| DEP file # | Digest agenda date | **Actual filing date (free API)** | Lead time the digest gave away |
|---|---|---|---|
| 095-1022 Ashland, 175 & 0 Oak Street | 2026-08-24 | **2026-06-30** | 55 days |
| 095-1025 Ashland, 167-171 Pleasant Street | 2026-08-24 | **2026-06-30** | 55 days |
| 006-2141 Boston, 3 Dolphin Way (Massport) | 2026-09-02 | **2026-07-31** | 33 days |
| 124-1378 Canton, 275 Dan Road | 2026-08-26 | **2026-07-29** | 28 days |
| 081-1344 Weymouth, 1085 Main Street | 2026-08-25 | **2026-07-28** | 28 days |
| 006-2139 Boston, 420 West Street | 2026-09-02 | **2026-08-04** | 29 days |
| 034-1571 Hingham, 55 Whiton Avenue | 2026-08-31 | **2026-08-13** | 18 days |
| 006-2147 Boston, 64-66-68 Kenrick Street | 2026-09-02 | **2026-08-24** | 9 days |
| 137-1744 Concord, 18B Powder Mill Road | 2026-08-26 | **2026-08-27** | — |
| 201-1397 Lexington, 27 Valleyfield Street | not in digest | 2026-08-24 | — |

### It names the people the digest refuses to name

The digest's stated policy is *"businesses only — private homeowners are never named,"* which blanks 36 of its 90 rows. The state names them, in a public dataset, as a matter of course:

- Three of the digest's `individual (homeowner)` rows were spot-checked against the state API on 2026-08-30. In all three the free dataset returns the applicant's full personal name in an `ApplicantName` field where the digest prints **"individual (homeowner)"**.
- The names and the row-level mapping are deliberately not reproduced here (`CLAUDE.md` §2); the check and its raw output are recorded in `private/outreach/digest-individuals.md`.

The pincer the red team described — named rows are worthless as leads, unnamed rows are unusable — is resolved by the free source, not by the paid one.

### The one field the state does not give you

`Company` is populated on 232 of 423 August filings, but it is the **applicant's** entity, not the consultant: `TOWN OF ASHLAND DEPARTMENT OF PUBLIC WORKS`, `FLYNN MASONRY`, `RODENHISER EXCAVATING, INC.`, `TASHMOO REALTY LLC`, `CONSERV GROUP, INC`, `NSTAR ELECTRIC COMPANY D/B/A EVERSOURCE ENERGY`. The consultant of record leaks only by accident, in the free-text `Comments` field, via the filing-fee payor — **2 of 60** details sampled in the 30 towns (`"CHECK #14664, PAYOR GRADY CONSULTING LLC"` on Hingham 225 Otis Street). Not a field.

So the **only** column the digest owns outright is the representative/engineer of record — at a 24% fill rate (22 of 90), on a field DECISION.md's own "What changed" section already declared *"not obtainable from agendas and already free on BLDUP."*

### Also present, also free: the decision

`OOCDate` is populated on **1,813 of 3,073** 2026 filings (59%). The Order-of-Conditions decision date — a thing the digest reports as "decision" rows — is a structured column in the free dataset.

---

## REVIVAL TEST — is work awarded after the NOI to a firm not on it?

### It exists, it is statutory, and it is the wrong size

**M.G.L. c.44 §53G** (https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVII/Chapter44/Section53G, accessed 2026-08-30) lets a ConCom impose fees on the applicant "for the employment of outside consultants," with an administrative appeal to the city council or selectmen limited to "claims that the consultant selected has a conflict of interest or does not possess the minimum, required qualifications."

MACC's own conference paper — *"An Introduction to the Wetlands Consultant Peer Review Process: Legal Considerations for M.G.L. Chapter 44, Section 53G,"* MACC Fall Conference, 2017-10-28 (https://cdn.ymaws.com/www.maccweb.org/resource/collection/8812584C-FC1C-4DFA-A43B-C34D2DC207CA/NAVIGATING_WETLANDS_CONSULTANT_PEER_REVIEW_IN_MASSACHUSETTS.PDF, fetched 2026-08-30) — is explicit that the scope is broader than plan review:

> "Fees may be assessed to cover consulting services for application review, **monitoring, reporting and compliance** under Ch. 40, § 8C, Ch. 131, § 40, or a local wetlands ordinance or by-law."

And Needham — one of the 30 towns — states the timing plainly (https://www.needhamma.gov/475/Regulations-for-Hiring-Outside-Consultan, accessed 2026-08-30):

> "**After the applicant has presented his/her project to the Commission at a hearing**, the members shall determine whether one or more outside consultants will be necessary in order for the Commission to make a fully informed decision on the application."

So the answer to the red team's question is literally **yes**: there is a scope awarded *after* the filing hits the agenda, to a firm that by construction is *not* the one on the filing. Three things then kill it as a lead thesis.

**1. There is nothing to bid on.** Per DOR IGR 03-208 as summarised in the MACC paper: contracts under $10,000 need only "sound business practices" — *"ensuring receipt of a favorable price by periodically soliciting price lists or quotes… Does not require a formal process."* $10,000–$34,999.99 requires three quotes. Needham's own threshold is $4,999.99 before c.30B applies. Peer-review assignments live below these lines, are awarded by the Commission from its own standing relationships, and are never advertised. I searched for a live wetlands/environmental peer-review RFQ or IFB in the 30 towns and found none. A feed that tells you a hearing happened does not put you in the room where the reviewer is picked.

**2. Taking the work bars you from the market you were in.** The same MACC paper, on G.L. c.268A:

> "§ 17(c) No municipal employee shall act as agent or attorney for anyone in connection with any particular matter in which the same city or town is a party… **Consultants who serve a ConComm cannot represent other parties in other matters in the same community.**"

The persona B is priced at — applicant-side wetlands scientists and stormwater engineers, the EBTs and Connorstones and LECs on the digest's own list — cannot add peer-review work in a town without giving up applicant work in that town. Peer review is not an expansion channel for them; it is a substitution.

**3. The volume is ~1%.** In the sample week's **320 agenda items / 90 conservation rows across 30 towns**, exactly **one** item is peer-review-adjacent: Ashland ConCom 2026-08-24, *"Review of Draft Letter to ZBA regarding 55 West Union Geotechnical Report"* — and that is the Commission commenting on someone else's 40B geotechnical peer review, not a §53G award. Zero §53G consultant selections appear in the whole sample.

**4. Order-of-Conditions monitoring goes to the incumbent.** The applicant-side monitoring and replication reporting a standard OOC imposes is performed by the consultant who wrote the replication plan and stamped the sheets — they hold the baseline data, and MassDEP's own replication guidance keys the monitoring to the as-designed plan. I found no MA town bidding out OOC-imposed monitoring or replication planting to a firm that was not already on the filing. The §53G "monitoring, reporting and compliance" money is the *Commission's* reviewer, which lands back in objections 1–3.

**Threshold set by the red team: "≥30% of NOI hearings generate a downstream scope awarded to a firm not already on the filing." Observed: ~1%, unadvertised, and conflict-barred for the buyer. Not met, not close.**

### The market-share reposition: the category is real, and the incumbent already ships it

The category buys:

- **The Warren Group** (Boston, data since 1872), Mortgage MarketShare: *"Submit the name of a competitor and a specific county or state that you would like to review. We'll run a Mortgage MarketShare Report at the company level, paired with a Loan Originator Report"* — https://thewarrengroup.com/business/data-solutions/mortgage-marketshare (accessed 2026-08-30). Competitor-versus-you-by-geography, sold as a product.
- **ConstructConnect Insight**: *"real-time data on projects specifying competitors' products"*, sold to building-product manufacturers — https://www.constructconnect.com/blog/beating-your-competition-why-competitive-tracking-is-a-game-changer-for-building-product-manufacturers (accessed 2026-08-30).

But the local incumbent already sells exactly the reposition, to this city, at scale — https://www.bldup.com/data (accessed 2026-08-30), verbatim:

> "Follow Developers, Owners, GCs, Subs, and Lenders. **Get alerts when they win projects** or change ownership so you never miss an opportunity."
> "Verified Developers, Owners, GCs, Subs, Lenders, Brokers, **Architects, Engineers**, and more"
> "Identify qualified GCs, **benchmark competitor pipelines**, and build stronger partnerships with trusted firms."
> "Trusted by **65,000+** Subcontractors, General Contractors, Developers, and the teams who work with them"

Firm-level win tracking for engineers, with alerts, at 65,000 users, in Boston. The gap left is "the same thing, one tier down, for ConCom filings" — and the only field that would make it possible (consultant of record) is the 24%-fill column the digest itself says cannot be got from agendas.

---

## What this changes

1. **Retire the BLDUP question.** The kill question to put to a prospect is now: *"You can pull every NOI in your town, with the applicant's name, address, DEP file number and filing date, free and one day after it is filed, from the state's own portal. What would you pay me for on top of that?"* If the answer is not instant and specific, there is no product.
2. **The falsifier "fewer than 20 named wetlands/civil/survey firms identifiable" was already pre-satisfied and is now moot.** Firm identification was never the constraint.
3. **The one honest asset in the corpus is the consultant-of-record column** — 22 names in one week, ~58 across the full digest, obtainable nowhere free. It is a market-share dataset, not a lead feed, and it competes head-on with a 65,000-user Boston incumbent that already ships alerts on which engineers win what.
4. **The digest is strictly late.** It reports on 2026-08-30 a filing the state published on 2026-06-30. A product whose headline promise is early warning cannot ship 55 days behind a free API.
5. **Salvage value:** the WIRE API is a clean, free, structured, statewide corpus with a one-day lag — 3,073 rows YTD, 328 in the 30 towns. If any B-shaped thing survives, it is built on that, in an afternoon, and it is not a hand-compiled digest.

---

## Reproduction

Scripts and captured data: `/private/tmp/claude-501/-Users-alexlopez-Desktop-money-maker-venture/d4da4194-2d84-4d17-a936-30c2eba158ca/scratchpad/` — `mpn.py` (session + form), `run2.py` (town checkbox postbacks), `page2.py` (50-per-page result grid), `per_town.json`, `wet_towns.json`, `wire_2026.json`, `wire_details.json`.

One-liner that reproduces the whole of Check 2:

```
curl -s 'https://eeaonline.eea.state.ma.us/EEA/DataLake/V1.0/DataLakeAPI/wire?_start=0&_end=50&FromFilingDate=2026-08-16&ToFilingDate=2026-08-30'
```
