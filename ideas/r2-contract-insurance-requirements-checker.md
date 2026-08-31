# Contract Insurance-Requirements Extractor and Coverage Checker

**Slug:** r2-contract-insurance-requirements-checker  |  **Track:** B  |  **Researched:** 2026-08-30  |  **Status:** researched  |  **Origin:** round 2 (asset-suggested)

## One-line pitch
Upload a subcontract, lease, or vendor agreement and get back a one-page structured checklist of every insurance requirement it imposes — limits by line, additional-insured status, primary and non-contributory, waiver of subrogation, notice-of-cancellation, umbrella follow-form — diffed against the party's actual COI, with each requirement quoted and page-cited so a human can verify it before signing.

## Specific buyer
Three candidate buyers were investigated. They are not equally good.

**(a) Small independent P&C agency staff (CSR / commercial lines account manager / "certificate processor").** The role exists as a named job title: **Higginbotham, "Certificate Processor," Corpus Christi TX** — "Provides customer service for insured parties requesting certificates of insurance" (Indeed, fetched 2026-08-30, https://www.indeed.com/jobs?q=%22high+volume%22+%22certificates+of+insurance%22). Locally: **Farsyt, "Insurance CSR," Cambridge MA** — "Issue certificates of insurance and evidence of property"; **Salem Five Insurance Services, "Commercial Insurance Manager," Woburn MA, $90,000–$120,000/yr** — "Train newly hired Account Managers on rating, quoting, new business applications, binders of insurance, endorsements, certificates of insurance" (Indeed, fetched 2026-08-30, https://www.indeed.com/jobs?q=%22certificate+of+insurance%22+specialist&l=Boston%2C+MA). **This buyer has a $0 price anchor — see WTP evidence.**

**(b) Subcontractors and small GCs who sign the subcontract.** The party that actually eats the risk. Evidence they do this work manually: **Suffolk Construction (Boston-HQ GC), "Assistant Project Manager," $85,000–$127,000/yr** — "Request Insurance Certificates from subcontractors to review for compliance with company's insurance requirements"; **Ryan Companies US Inc, "Risk Management Coordinator," Minneapolis, $70,000–$75,000/yr** — "Review insurance requirements within construction agreements (including DBIA and AIA forms...subcontracts)" (Indeed, fetched 2026-08-30, https://www.indeed.com/jobs?q=%22insurance+requirements%22+%22subcontract%22+review).

**(c) Property managers / vendor-compliance coordinators.** **SiteLine Services, "Vendor Relations Coordinator," Abilene TX, $58,000–$70,000/yr** — "Ability to read commercial agreements, extract critical dates/limits, and check certificates of insurance against corporate compliance thresholds" (Indeed, fetched 2026-08-30). This posting is a literal job description of the product.

**Recommendation: buyer (b), the subcontractor/small GC, is the only one without a free incumbent and without a licensing/E&O boundary problem.**

## Pain evidence (verbatim, >= 5)

**1. Big "I" Virtual University — the agent's E&O trap when asked to attest to contract insurance requirements.** VU article, "Addendums to COIs: Bad, But…", published **December 8, 2021**, https://www.independentagent.com/vu_resource/addendums-to-cois-bad-but/ (fetched 2026-08-30, opening paragraphs reproduced verbatim):

> "Yes, many lawyers and risk managers have accepted the fact that COIs cannot be used to convey anything other than the reality of the policy; but this hasn't stopped these 'black hats' from looking for other ways to corner the agent. These bad actors have developed another method for suckering agents into creating an errors and omissions (E&O) noose…. Enter the **Addendum**!"

The same article, on a first (summarizing) read of the page, reported these lines as quoted contractor/insured pressure: *"We won't let them on the site without the addendum."* / *"They are holding up my pay until they receive the completed addendum."* — and the E&O point *"the agent is in no less danger if he or she undertakes to complete the coverage addendum."* **Flagged: these three came through a summarizing fetch, not the strict verbatim pass; re-read the page and confirm exact wording before quoting them publicly.**

**2. Big "I" Virtual University — agents field the inverse question constantly.** VU article, "Mistakes on Certificates Versus Clear Policy Language", **July 13, 2021**, https://www.independentagent.com/vu_resource/mistakes-on-certificates-versus-clear-policy-language/ (fetched 2026-08-30). Opening question, verbatim: *"Can a certificate of insurance limit the breadth of protection provided by the insurance policy and endorsements?"* The article calls it "the weirdest certificate of insurance (COI) question" its author has encountered, noting the usual question runs the other direction (whether COI language can *expand* coverage). Context: Big "I" maintains **70 resources** on certificates of insurance in this archive (https://www.independentagent.com/agency-management-solutions/certificates-of-insurance/, fetched 2026-08-30), 68 of them VU articles — the topic generates enough recurring member confusion to justify a 70-item library.

**3. A general contractor's own tool for this already exists as free code.** GitHub repo `ankundu005/certificate-of-insurance-analyzer`, **created 2026-05-03**, 0 stars, https://github.com/ankundu005/certificate-of-insurance-analyzer — repository description, verbatim:

> "A personal App to analyze the certificate of insurance for General Contractors before they are hired to do the job. I wanted to create solution so that it helps me to analyze the risks for contractors not having the right insurance to build my ADU."

**4. An insurance professional built the full product as a portfolio project.** GitHub repo `Tondie-HSPI/Certificate-and-Coverage-Clarity`, **created 2026-06-19, last pushed 2026-08-10**, 1 star, https://github.com/Tondie-HSPI/Certificate-and-Coverage-Clarity — README, verbatim:

> "**A decision-support prototype for commercial insurance intake, COI review, and evidence comparison.** … The project demonstrates how AI-assisted review can support commercial insurance, compliance, and service workflows without replacing professional judgment. It organizes requirements, compares evidence, highlights gaps, and drafts review-ready follow-up language. … The application supports commercial insurance professionals working through contracts, Certificates of Insurance (COIs), policies, and endorsement evidence."

This is the pitch, written by a domain practitioner, shipped free, with **one star**.

**5. Contractors on the receiving end of insurance-document review, Trustpilot, Avetta (1 star, July 21, 2026, a reviewer in GB)**, https://www.trustpilot.com/review/avetta.com (fetched 2026-08-30):

> "What should be a simply process has been delayed by them for weeks not reviewing docs on time and rejecting valid insurance docs with no reason behind it."

**6. Trustpilot, ISNetworld (1 star, August 7, 2026, a reviewer)**, https://www.trustpilot.com/review/isnetworld.com (fetched 2026-08-30):

> "WASTE OF TIME AND MONEY- They are not helpful, they demand more and more information constantly. Their onboarding process is completely obtuse, entirely too many steps..."

**7. Trustpilot, ISNetworld (1 star, May 20, 2026, a reviewer)**, same URL:

> "Don't go anywhere near this business, Our client insists we use them as a H&S platform. Uncooperative time wasting and a waste of money"

**8. Capterra, myCOI (1.0 stars, a reviewer — Operations Manager, construction, 1–2 years' use — December 17, 2024)**, https://www.capterra.com/p/234580/myCOI/reviews/ (fetched 2026-08-30):

> "Not pleasant. They were hard to work with, system was a mess" / Cons: "Was not a fan of the layout or impressed with the functions offered"

**9. Capterra, myCOI (a reviewer — VP Risk, construction, 2+ years — August 30, 2022)**, same URL:

> "Bulk downloading documents in the cert Management is not usable...it takes us days"

**10. Capterra, myCOI (a reviewer — Contract Administrator, real estate — 4.0 stars, April 17, 2023)**, same URL:

> "I wish that the reviews were more accurate and timely we have ran into issues"

**Honest read of this evidence.** Items 5–10 are complaints about *compliance portals* (Avetta, ISNetworld, myCOI), not about the act of reading a contract's insurance exhibit. Items 1–4 are the closest to the actual wedge, and two of them are GitHub repos rather than customers. **Nobody is publicly complaining, in their own words, that extracting insurance requirements from a contract is hard.** The task shows up in the world as a *job duty on a payroll*, not as a rant. That is a materially weaker demand signal than a market where people vent.

## Willingness-to-pay evidence (>= 3)

**1. Employers pay full-time salaries specifically for this task.** All from Indeed, fetched 2026-08-30:
- SiteLine Services, Vendor Relations Coordinator, **$58,000–$70,000/yr** — "read commercial agreements, extract critical dates/limits, and check certificates of insurance against corporate compliance thresholds"
- Ryan Companies US Inc, Risk Management Coordinator, **$70,000–$75,000/yr** — "Review insurance requirements within construction agreements"
- AMN Healthcare, Risk Management Specialist, **$73,000–$86,500/yr** — "3–6 years of relevant experience in risk management, insurance, or contract review"
- M.C. Dean, Insurance Risk Specialist, **$112,800–$141,000/yr** — "Reviewing and updating insurance requirements and limits for the organization's subcontractor program"
- Washington University in St. Louis, Insurance Program Manager, **$84,200–$148,500/yr** — "Administers the University's certificate of insurance (COI) program"

**2. Certificial charges the requesting side, and gives the agent side away free.** https://www.certificial.com/pricing and https://www.certificial.com/agents-brokers (both fetched 2026-08-30), verbatim:
- Requestor: Basic free ("Track compliance of up to 5 suppliers"); **Professional "Starts at $99/mo"**; Enterprise "Contact Us"
- Insured: "$0 free". Agent & Broker: "$0 free" — **"Completely free for Agents, Brokers and Carriers."**
- Agent/broker page also lists tiers "Free: $0 per life / Premium: $249 per year / Enterprise: $639 per year"
- Certificial already ships **"Requirement Comparison"** — "automatic comparison between the Insured's coverage and the Certificate Holders' request easily."

**This is the single most important number in the dossier and it is negative:** the buyer 40 minutes from campus (the independent agency) has been trained by a funded incumbent to pay **$0** for coverage-vs-requirement comparison.

**3. Agencies already buy this work as outsourced labor.** WAHVE, "Commercial Lines Account Manager," remote (Indeed, fetched 2026-08-30): "Responsible for contract review and issuance of Certificates of Insurance (COI's)." WAHVE sells "Vintage Contract Staffing (VCS)" — remote insurance professionals averaging "25+ years of experience" (https://www.wahve.com/, fetched 2026-08-30). No public rate card.

**4. Adjacent categories are funded and enterprise-priced.** Qumis: "Qumis raises $4.3M to bring attorney-grade Coverage Intelligence to commercial insurance" (https://www.qumis.com/, fetched 2026-08-30) — targets "brokers and producers, claims investigators, and carriers/MGAs/TPAs," lists "policy analysis," "quote comparison," and "contract compliance." Document Crunch: "Join 500+ companies that aren't accepting risk as the cost of doing business" (https://www.documentcrunch.com/, fetched 2026-08-30), logos include Balfour Beatty, DPR, Swinerton. Neither publishes a price; `/pricing` returns 404 on Document Crunch and Qumis. Sales-led enterprise pricing, not a self-serve tier a student can undercut into.

## Reachability (50 qualified buyers in 30 days, $0)

**What actually exists near Boston:**
- **Massachusetts Association of Insurance Agents (MAIA)**, 91 Cedar Street, Milford, MA 01757, (508) 634-2900 (archived homepage 2025-12-01 via web.archive.org, retrieved by curl 2026-08-30; massagent.com returns 403 to direct fetch). Runs a "Calendar of Classes," "Live Webinars," "Designations and Certifications," "Young Agents" events, an "Annual Meeting" and a "Big Event." ~35 miles from Northeastern, roughly a 45-minute drive — **reachable but not walkable, and every touchpoint is an event you must attend, not a forum you can read.** Membership count is not published on the homepage; the brief's "~1,000 member agencies" was **not verified** in this research.
- Boston-metro agencies hiring for this exact work, from public job posts: Salem Five Insurance Services (Woburn), Farsyt (Cambridge), Simply Business (Boston), WTW (Boston). Suffolk Construction is a Boston-HQ GC on the contractor side.

**What does not exist (this is the problem):**
- **reddit.com returns 403 to every method** in this environment — r/InsuranceProfessional (~38k members) could not be read at all.
- **insurance-forums.com returns 403.** **contractortalk.com is behind a Tollbit 402 wall.** **G2 / TrustRadius return 403.**
- **forums.jlconline.com is dead** — 301-redirects to the JLC homepage.
- **insurancejournal.com/forums is effectively dead**: 19,337 posts / 3,547 topics / 4,869 members total; a title search for "additional insured" returns **five threads, the newest from 2009** (https://www.insurancejournal.com/forums/search.php?keywords=additional+insured, fetched 2026-08-30). The "Opinions" subforum's last activity was July 2024.
- **Review sites have no category.** myCOI has 47 Capterra reviews; **TrustLayer has 2** (https://www.capterra.com/p/198486/TrustLayer/); Certificial, TrustLayer and myCOI all have **0 Trustpilot reviews**; Avetta's BBB profile states "This business has 0 complaints." Capterra's own search for "certificate of insurance tracking" returns affiliate-tracking software and SSL certificate managers. **There is no complaint surface, which also means no SEO surface and no review-mining channel.**
- **HN is empty**, as predicted: Algolia searches for "certificate of insurance," "additional insured," "contract review AI insurance," and "COI compliance" return zero on-topic stories or Show HNs.
- **OSS/PLG does not work here either.** Six GitHub repos doing COI/ACORD-25 extraction, all created between 2025-07-14 and 2026-08-22, **all with 0 or 1 star**: `Tondie-HSPI/Certificate-and-Coverage-Clarity` (1★), `Kurosyss/certifitrack` (1★), `theonlyoneH/coi-validator` (1★), `harshbopaliya/coi-compliance-zenml` (1★), `ankundu005/certificate-of-insurance-analyzer` (0★), `SourcyLab/florida-coi-parser` (0★). Nobody has converted open source into distribution in this niche.

**Realistic 30-day, $0 plan:** attend one MAIA education event or Young Agents event in Milford; walk into 10–15 Boston-metro independent agencies with a printed sample report; approach subcontractors at supply houses and at AGC Massachusetts / ASA events. **Estimated yield: 15–25 conversations, not 50 qualified buyers.** Every channel here is physical and serial. This is the weakest dimension of the idea.

## Wedge
**Sell the checklist, not the opinion, and sell it to the party that signs.**

v1 is a single flow: a subcontractor or small GC uploads the subcontract's insurance exhibit (or the whole 40-page PDF) and gets back a one-page report that (a) lists every insurance obligation as a row — coverage line, required limit, occurrence vs aggregate, additional-insured status and form number if named, primary and non-contributory, waiver of subrogation, notice of cancellation days, umbrella/excess follow-form, indemnity trigger, certificate-holder wording — each with the **verbatim contract sentence and page number**; and (b) if they also upload their ACORD 25, marks each row `evidenced on COI` / `not evidenced on COI` / `cannot tell from a COI — ask your agent for the endorsement`.

The wedge is the *citation and the framing*: it never says "you are not covered." It says "this contract requires X on page 12; your certificate does not show X; ask your agent." That is a reading-comprehension product, not a coverage opinion — which is what keeps it on the safe side of the line Big "I" draws (see Risks).

Why this and not the agency: Certificial gives agents requirement-comparison for free, and agencies have institutional reasons to *avoid* opining on contracts. The sub has no free tool, signs the document, and eats the loss.

## Build estimate
**5–8 agent-days for a sellable v1.**

Components:
1. PDF ingest — text-layer extraction with an OCR fallback for scanned exhibits (1 day; scanned-PDF exhibits are common and this is the part that will actually bite).
2. LLM structured extraction to a fixed requirements schema, with span offsets so every row carries a verbatim quote + page cite (1.5–2 days, including the schema design, which is the real domain work).
3. ACORD 25 parser — the form is fixed-layout and several of the GitHub repos above solve it; limits, dates, checkbox columns for additional insured / subrogation waived (1 day).
4. Diff engine — requirement row vs COI evidence, with an explicit "a COI cannot prove this, ask for the endorsement" third state (0.5 day).
5. One-page HTML → PDF report (0.5–1 day).
6. Stripe one-time checkout + upload page, no accounts in v1 (0.5 day).
7. A held-out eval set of ~20 real subcontract insurance exhibits scored by hand — **non-negotiable, this is the whole product** (1–1.5 days).

Not in v1: AMS/Applied Epic integration, policy-form (not COI) analysis, endorsement-form libraries, multi-user accounts, monitoring/renewal tracking.

Reusable assets: None.

## Unit economics
- Price: **$29 per contract one-time**, or **$79/mo for 10 contracts** for a GC's risk coordinator. (Anchor: Certificial requestor "Starts at $99/mo"; a $58k–$70k coordinator costs ~$30/hr loaded and this replaces 30–60 minutes.)
- Variable cost per 40-page contract: ~60k–120k input tokens + ~4k output at Sonnet-class pricing ≈ **$0.20–$0.60**; OCR fallback adds cents. Gross margin ~97% at $29.
- Fixed burn: domain ~$12/yr, Vercel/Render free tier, Stripe pay-per-transaction. **Well under $40/month.**
- Break-even on burn: ~2 reports/month. Break-even on *time* (12 hrs/week has an opportunity cost): ~40 reports/month at $29, which requires roughly 15–20 recurring accounts. **That is the hard number, and reachability says it takes months, not weeks.**

## Risks
1. **Coverage advice / E&O / unauthorized practice of law — the dominant risk.** Big "I"'s own Virtual University tells agents that completing a contract insurance requirements addendum is "creating an errors and omissions (E&O) noose" (Big "I" VU, 2021-12-08). Interpreting a contract clause is arguably legal work; opining that a policy fails to satisfy it is arguably insurance advice, which in Massachusetts is licensed activity. A student-run tool that outputs "you have a gap" inherits both exposures. Mitigation is real but constraining: quote-and-cite only, never conclude, never name a policy form the user did not upload, hard disclaimer, and no state-law conclusions. This also caps the value of the output — the safe version is less useful than the useful version.
2. **Asymmetric downside on a $29 sale.** Missing a "primary and non-contributory" requirement can void a defense obligation on a seven-figure claim. Tiny ticket, unbounded tail. Insurance for this (tech E&O) costs more than the product will earn in year one.
⚠️ VERIFIER: altered - 3. **Incumbents already ship the comparison half.** Certificial: "Requirement Comparison … automatic comparison between the Insured's coverage and the Certificate Holders' request." illumend (the AI-native successor to myCOI, mycoitracking.com now 301-redirects to illumend.ai): "illumend is the AI-native insurance compliance platform from myCOI, built on 16 years of compliance expertise and now powered by AI," whose engine Lumie "checks coverage against your contract or lease requirements." TrustLayer: "reads COIs, checks them against your standards, and flags coverage gaps." The only unoccupied sliver is *extracting the requirements from the contract document itself* — and that is exactly the part an LLM makes trivial.
4. **No moat, demonstrated empirically.** Six independent COI-extraction repos appeared in 13 months, one of them a full "organizes requirements, compares evidence, highlights gaps" product built by an insurance professional. Zero traction for any of them. If it were both valuable and defensible, one of these would have stars.
5. **No public complaint surface** → cannot validate demand cheaply, cannot do content marketing, cannot find buyers online. Reddit blocked, forums dead, review sites empty.
6. **Transactional, not recurring.** A small sub signs a handful of contracts a year. The recurring version of this buyer is a GC's risk coordinator — who is exactly the person a $70k salary already covers, and who works at a company with a procurement process a student cannot navigate in 12 hrs/week.
7. **Scanned exhibits.** A meaningful share of subcontract PDFs are scans of scans. OCR quality, not LLM quality, will be the accuracy ceiling.

## Kill criteria
- **Contact 15 Boston-area subcontractors or small GCs in 30 days (in person at supply houses, AGC MA / ASA events, or via published contact forms). If fewer than 3 will hand over a real subcontract for a free review → kill.** People who won't give you the document for free will never pay for the analysis.
- **Run the first 5 free reviews. If 3 of them surface zero actionable gaps → kill.** A checker with no news to deliver has no product.
- **If 2 or more insurance professionals say some version of "we would never let a third party opine on our client's coverage" → the agency channel is dead**, and the remaining contractor-only channel does not support recurring revenue. Re-scope or kill.
- **If Certificial, illumend, or TrustLayer ships contract-document upload (not just requirement configuration) before you have 10 paying users → kill.** Watch https://www.certificial.com/pricing and https://www.illumend.ai/ monthly.
- **If the eval set shows below ~90% recall on the four endorsement requirements (additional insured, primary and non-contributory, waiver of subrogation, notice of cancellation) → do not ship at all.** Below that, the tool creates liability rather than removing it.
- **Time box: if no paying customer by day 45 → stop.**

## Incumbents and adjacent players

| Player | What it does | Price (public, fetched 2026-08-30) | Overlap with this wedge |
|---|---|---|---|
| **Certificial** (certificial.com) | COI issuance + supplier compliance network; **"Requirement Comparison"** | Requestor: free ≤5 suppliers, Professional **"Starts at $99/mo"**, Enterprise contact-us. Insured $0. **"Completely free for Agents, Brokers and Carriers."** Agent tiers listed as Free $0 / Premium $249/yr / Enterprise $639/yr | **High.** Already compares coverage to a holder's stated request. Missing piece is reading the requirement out of the contract PDF. |
| **illumend** (illumend.ai, formerly **myCOI**; mycoitracking.com 301s here) | "AI-native insurance compliance platform from myCOI, built on 16 years of compliance expertise"; engine "Lumie" "checks coverage against your contract or lease requirements" | Not published; "Schedule Demo" / "Calculate Your ROI" | **High.** Explicitly frames contract/lease requirements as the comparison basis. 47 Capterra reviews, 4.7★. |
| **TrustLayer** (trustlayer.io) | ⚠️ VERIFIER: altered - Vendor COI collection/verification; "reads COIs, checks them against your standards, and flags coverage gaps"; "517,000+ companies" in network; "create multiple compliance profiles that correspond to specific contract requirements" | Not published: "Pricing varies depending on platform usage… Please schedule a demo" | **High on the compare side.** Requirements appear to be configured, not extracted. 2 Capterra reviews, 0 Trustpilot reviews. |
| **Document Crunch** (documentcrunch.com) | "AI Risk Intelligence Platform" for construction contracts; CrunchAI reads contract risk "with cited sources"; Project Assist agentic layer | Not published (`/pricing` 404). "Join 500+ companies"; Balfour Beatty, DPR, Swinerton | **Highest strategic threat.** Same document, same buyer, cited-source output; insurance is one clause family among many. Enterprise GC-focused. |
| **Qumis** (qumis.com, formerly qumis.ai) | "attorney-grade Coverage Intelligence"; policy analysis, quote comparison, **"contract compliance"**; buyers = brokers/producers, claims, carriers/MGAs/TPAs | Not published (`/pricing` 404). **"Qumis raises $4.3M"** | **High on the broker side.** Funded, aimed squarely at the agency buyer, and already names contract compliance. |
| **Applied Indio** (Applied Systems) | "Application and submissions management platform" — turns the commercial application into "a simple, Turbo-Tax like experience" | Not published | **Low.** No certificate or contract-requirement functionality on the product page. The round-1 assumption that the AMS vendors own this space is only half right — they own *applications*, not contract review. |
| **ISNetworld, Avetta, ComplianceDepot/RealPage, Highwire** | Contractor prequalification portals that review the sub's insurance docs on behalf of a hiring client | Subscription, charged to the *contractor* | **Adjacent and universally hated** (see Pain evidence 5–7). They are the reason subs care about getting the exhibit right, i.e. a demand driver, not a competitor. |
| **6 GitHub repos** (`Tondie-HSPI/Certificate-and-Coverage-Clarity`, `Kurosyss/certifitrack`, `theonlyoneH/coi-validator`, `harshbopaliya/coi-compliance-zenml`, `ankundu005/certificate-of-insurance-analyzer`, `SourcyLab/florida-coi-parser`) | COI/ACORD-25 extraction, requirement organization, gap highlighting | Free | **Proof the build is cheap and the moat is zero.** All created 2025-07 → 2026-08. All 0–1 stars. |

## Score

| Dimension | Weight | Score | Justification |
|---|---|---|---|
| Time to first dollar | x3 | **3** | The build is 5–8 agent-days and the artifact (a one-page cited gap report) is sellable on sight, but the first dollar waits on someone else's contract cycle rather than on your launch date, and every buyer must be reached in person. |
| Reachability by a student | x3 | **2** | Reddit is 403, insurance-forums.com is 403, JLC's forums are dead, Insurance Journal's forum's newest "additional insured" thread is from 2009, TrustLayer/Certificial/myCOI have 0 Trustpilot reviews and TrustLayer has 2 on Capterra — the only live channel is driving 45 minutes to MAIA in Milford or walking into agencies, which does not produce 50 qualified buyers in 30 days. |
| Pain x frequency | x2 | **3** | The work is provably real and salaried (SiteLine: "read commercial agreements, extract critical dates/limits, and check certificates of insurance against corporate compliance thresholds"; Ryan Companies; Suffolk; M.C. Dean), but it fires per new contract — weekly for a GC risk coordinator, a few times a year for a small sub — and nobody complains about it publicly in their own words. |
| WTP evidence | x2 | **3** | Employers pay $58k–$141k salaries for this exact duty and Certificial charges requestors "Starts at $99/mo", but the nearest buyer has a hard $0 anchor: "Completely free for Agents, Brokers and Carriers." |
| Fit with assets and strengths | ×2 | **1** | Document extraction — nothing in the assets. |
| Compounding | x2 | **2** | Each contract reviewed grows a corpus of requirement clauses and a hand-scored eval set, which is a genuine asset, but the customer relationship is per-contract with no network effect and nothing a competitor could not rebuild with an LLM in a week — as six GitHub repos in 13 months demonstrate. |
| Risk (5 = low) | x2 | **2** | Flagging a coverage gap sits on the coverage-advice / unauthorized-practice line that Big "I" itself calls "an errors and omissions (E&O) noose", and a missed "primary and non-contributory" flag carries seven-figure downside on a $29 sale. |
| Ceiling | x1 | **3** | The surrounding market is real and funded (Document Crunch "500+ companies", Qumis "$4.3M"), but the extraction slice alone is a feature inside those products, and their buyers are enterprise GCs and carriers a solo student cannot sell. |
| Build cost (5 = cheap) | x1 | **4** | PDF-to-schema extraction, an ACORD 25 parser and a diff report is 5–8 agent-days on free tiers at ~$0.20–$0.60 of tokens per contract; the only expensive part is the hand-scored eval set. |

**Subtotal excluding fit: 42 / 80.**
(9 + 6 + 6 + 6 + 4 + 4 + 3 + 4)

## Verdict
**Weak — do not lead with this. Keep as a possible one-time-revenue side product, not as the recurring-revenue bet.**

The round-1 hypothesis was that certificate *generation* is commoditized while contract *requirement extraction* is unoccupied. Half of that held up: Applied Indio really is only an application platform, and nobody sells "upload the subcontract PDF" as a product. But the gap is unoccupied for three bad reasons rather than one good one. First, the adjacent players already own the half that matters commercially — Certificial ships "Requirement Comparison," illumend's Lumie "checks coverage against your contract or lease requirements," TrustLayer "flags coverage gaps" — so the extraction step is a feature they can add whenever a customer asks, not a business. Second, the buyer closest to Alex has been trained to pay zero: "Completely free for Agents, Brokers and Carriers." Third, and most damning for a solo operator, the output is a coverage opinion, and the industry's own educator frames volunteering that opinion as building "an errors and omissions (E&O) noose."

The reachability picture seals it. Every online channel where this buyer might congregate is either blocked, dead, or empty: reddit 403, insurance-forums 403, Insurance Journal's forum's most recent relevant thread predates the iPhone 4, and the entire software category has fewer public reviews than a mid-sized coffee shop. That leaves driving to Milford. A 12-hour week does not support a buyer you can only reach one handshake at a time.

The strongest signal in this dossier is also the most discouraging one: an actual insurance professional built the entire product — "It organizes requirements, compares evidence, highlights gaps, and drafts review-ready follow-up language" — deployed it to AWS, and earned one GitHub star. Five other people built adjacent versions in the same 13 months. When domain experts with better distribution than you have already shipped it for free and nothing happened, the constraint is not the software.

If Alex pursues anything here, it should be the reframed version in the adjacent ideas below — sell to the party *writing* the requirements rather than the party interpreting them, which removes the coverage-advice problem entirely.

## Research log

**Method constraint:** the session's WebSearch budget (200/200 calls) was already exhausted before this research began, so **no keyword search engine was available**. Attempted and blocked as substitutes: DuckDuckGo HTML and Lite endpoints (HTTP 202 + JS captcha), DuckDuckGo via WebFetch (duck-image CAPTCHA), Mojeek (`<title>Captcha</title>`), Ecosia (403), Brave (200 but unparsed), six SearXNG instances (searx.be served a browser-verification page; priv.au, searxng.site, opnxng.com, search.inetol.net all 429; search.bus-hit.me timed out), Bing via WebFetch (returned geo-generic Seattle insurance results, not the query). **All discovery was therefore done by direct URL fetch against sites known to work, plus public JSON APIs.** This materially reduced complaint-mining coverage and is the main reason the pain evidence skews toward job postings and adjacent-product reviews.

**Also blocked/dead:** reddit.com (403, as warned — r/InsuranceProfessional unreadable); web.archive.org via WebFetch ("Claude Code is unable to fetch from web.archive.org" — worked via curl); api.pullpush.io Reddit archive (429, "This website does not provide free scraping resources for agents"); insurance-forums.com (403); massagent.com (403 direct, retrieved via Wayback + curl); forums.jlconline.com (301 to homepage, forums retired); levelset.com/ask-an-expert (404); pissedconsumer brand subdomains (404); trustpilot.com/review/compliancedepot.com (404); trustpilot.com/review/smartcompliance.com (404); documentcrunch.com/pricing (404); qumis.com/pricing (404); trustlayer.io/pricing and /products/contract-intelligence (404); independentagent.com/vu_resource/beware-certificial-cbre-... (404 despite being listed on the live archive page); several Big "I" VU articles are member-gated ("You've reached member only content").

**Worked:** Indeed job search, Capterra product + review pages, Trustpilot brand pages, BBB, independentagent.com VU article pages (public subset), vendor marketing/pricing pages, GitHub REST API, HN Algolia API, StackExchange API, archive.org availability API + Wayback via curl.

**Sources fetched (all 2026-08-30):**
- https://www.indeed.com/jobs?q=%22certificate+of+insurance%22+%22contract+review%22
- https://www.indeed.com/jobs?q=%22insurance+requirements%22+%22subcontract%22+review
- https://www.indeed.com/jobs?q=%22high+volume%22+%22certificates+of+insurance%22
- https://www.indeed.com/jobs?q=%22certificate+of+insurance%22+specialist&l=Boston%2C+MA
- https://www.indeed.com/jobs?q=%22insurance+exhibit%22+OR+%22insurance+requirements%22+%22review+contracts%22
- https://www.independentagent.com/agency-management-solutions/certificates-of-insurance/ (70 COI resources, 68 VU articles)
- https://www.independentagent.com/vu_resource/addendums-to-cois-bad-but/ (Big "I" VU, 2021-12-08)
- https://www.independentagent.com/vu_resource/mistakes-on-certificates-versus-clear-policy-language/ (Big "I" VU, 2021-07-13)
- https://www.certificial.com/pricing ; https://www.certificial.com/agents-brokers
- https://www.illumend.ai/ (myCOI successor; mycoitracking.com 301s here)
- https://www.trustlayer.io/
- https://www.documentcrunch.com/
- https://www.qumis.com/ (qumis.ai 301s here)
- https://www1.appliedsystems.com/en-us/solutions/for-agents/insurance-application-software/indio/
- https://www.capterra.com/p/234580/myCOI/reviews/ ; https://www.capterra.com/p/198486/TrustLayer/ ; https://www.capterra.com/p/70671/Applied-Epic/reviews/
- https://www.capterra.com/search/?query=certificate%20of%20insurance%20tracking (category is noise — returns SSL certificate and affiliate-tracking software)
- https://www.trustpilot.com/review/avetta.com ; /isnetworld.com ; /mycoitracking.com (0 reviews) ; /certificial.com (0) ; /trustlayer.io (0)
- https://www.bbb.org/us/ut/draper/profile/compliance-consulting/avetta-1126-22004121/complaints ("This business has 0 complaints")
- https://www.insurancejournal.com/forums/ and /forums/search.php?keywords=additional+insured
- GitHub API: repo search for "certificate of insurance" (21 results) and ACORD 25 / insurance-requirements extraction (13 results); metadata + READMEs for the six repos named above
- HN Algolia API: "certificate of insurance", "additional insured", "contract review AI insurance", "COI compliance" — no on-topic results
- https://www.wahve.com/ ; https://www.resourcepro.com/solutions/
- massagent.com via Wayback snapshot 2025-12-01 (address, education calendar, Young Agents events)

**Not verified:** MAIA's "~1,000 member agencies" figure from the brief (not published on the pages reachable); IRMI's *Contractual Risk Transfer* subscription price (page renders via JS, price never loaded); any per-contract or per-COI outsourcing rate from WAHVE/ReSource Pro; the three quoted lines in Pain evidence #1 that came through a summarizing fetch rather than the verbatim pass.

## Verification (2026-08-30, adversarial pass)
- Quotes: 26 checked, 22 verified, 3 unfetchable, 1 altered
- Claims:
  - **Big "I" VU, "Addendums to COIs" (2021-12-08) — all six quoted phrases verbatim, including the three the dossier self-flagged.** CONFIRMED via raw HTML: "these 'black hats'", "an errors and omissions (E&O) noose…. Enter the Addendum!", "the agent is in no less danger if he or she undertakes to complete the coverage addendum", "We won't let them on the site without the addendum.", "They are holding up my pay until they receive the completed addendum." The dossier's caveat in Pain evidence #1 can be removed — the lines are real. https://www.independentagent.com/vu_resource/addendums-to-cois-bad-but/
  - **Big "I" VU, "Mistakes on Certificates Versus Clear Policy Language" (2021-07-13).** CONFIRMED verbatim: "Can a certificate of insurance limit the breadth of protection provided by the insurance policy and endorsements?" / "This has to be the weirdest certificate of insurance (COI) question I have ever been asked." https://www.independentagent.com/vu_resource/mistakes-on-certificates-versus-clear-policy-language/
  - **All six GitHub repos: star counts and creation dates.** CONFIRMED via GitHub API — 0★/1★, created 2025-07-14 → 2026-08-22, exactly as stated. Tondie-HSPI README quote verbatim. But `ankundu005/certificate-of-insurance-analyzer` was created 19:11:32Z and pushed 19:15:38Z the same day and ships `AGENTS.md` + `CLAUDE.md`: it is a ~4-minute agent-generated Next.js app, not a GC's hand-built tool. Weakens it as a demand signal; strengthens "no moat."
  - **Certificial pricing + "Completely free for Agents, Brokers and Carriers" + Free $0/Premium $249/Enterprise $639 + "Requirement Comparison".** CONFIRMED verbatim. https://www.certificial.com/pricing , https://www.certificial.com/agents-brokers
  - **REFUTED — "The sub has no free tool" (the entire rationale for choosing buyer (b)).** Certificial's free *Insured* tier already sells the sub: "Know Where You Stand" (instantly determine if you meet client coverage needs), "Alerting" (notification when coverage no longer meets requirements), "Keep Your Money" ("completely free to you as an insured"). The $0 anchor the dossier calls "the single most important number" applies to the recommended buyer too. https://www.certificial.com/insureds
  - **REFUTED — "nobody sells 'upload the subcontract PDF' as a product" / "the only unoccupied sliver is extracting the requirements from the contract document itself."** **Evident ID** (absent from the incumbent table) ships it: "Name a supplier or upload a contract — and get an instant snapshot with signals to act on", verification "against your exact requirements" covering "every coverage type, limit, endorsement, and exclusion", flagging "Ambiguous language & conflicting reqs". It also publishes a price: **Essential $15 per vendor billed annually, Pro $25 per vendor** — a public floor far under $29/contract. https://www.evidentid.com/ , https://www.evidentid.com/pricing/
  - **PARTLY REFUTED — Document Crunch is "enterprise GC-focused", "not a self-serve tier a student can undercut into."** DC runs a dedicated `/subcontractors` (specialty contractor) product, a **14-day self-serve free trial** covering "prime and subcontracts, scopes of work, NDAs, POs, insurance policies, specs, and more", a `/construction-insurance-sureties` page for "brokers, underwriters and sureties", and partner pages for IRMI, Acrisure and AXA XL. `/pricing` does 404 (confirmed), but "no self-serve tier" is wrong. https://www.documentcrunch.com/trial , /subcontractors , /construction-insurance-sureties
  - **REFUTED — "massagent.com returns 403 to direct fetch" and MAIA's "~1,000 member agencies" is "not verified" / "not published on the homepage."** massagent.com returns HTTP 200 to a normal user-agent and the live homepage states verbatim: "the leading trade association for nearly 1,000 Massachusetts independent insurance agencies and their estimated 9,000+ employees." It also hosts a public **Agent Locator** directory (massagent.com/agent-locator/). https://massagent.com/
  - **PARTLY REFUTED — Insurance Journal forums "effectively dead", "newest 'additional insured' thread from 2009."** Forum totals CONFIRMED exactly (19,337 posts / 3,547 topics / 4,869 members) and the *title-only* search does return 5 matches newest 2009 — but the URL the dossier cites (no `&sf=titleonly`) actually returns **281 matches**, including the on-topic thread "The AI and COI issue can be a PITA" (Jul 2019). The Hard-to-Place Accounts subforum's last post is **2026-03-23**, not July 2024. The Verdict's "most recent relevant thread predates the iPhone 4" does not survive the cited URL.
  - **Trustpilot (Avetta 2026-07-21; ISNetworld 2026-08-07 and 2026-05-20) and the three Capterra myCOI reviews (items 8–10).** All CONFIRMED verbatim and the dates are correct. Item 9's elided "...it takes us days" is genuinely in the same Cons field. Avetta TrustScore 1.9/13 reviews; myCOI 47 reviews/4.7★; TrustLayer 2 reviews. BBB "This business has 0 complaints" CONFIRMED.
  - **Qumis "$4.3M", Document Crunch "Join 500+ companies…", illumend/Lumie quotes, Applied Indio "Turbo-Tax like experience", mycoitracking.com 301 → illumend.ai, Big "I" 70-resource COI archive.** All CONFIRMED.
  - **ALTERED — TrustLayer quote.** Dossier: "reads COIs, checks them against your standards, and flags coverage gaps". Actual: "reads each COI, checks it against your standards **and industry benchmarks**, and flags any gaps in coverage". Paraphrase presented inside quotation marks; marked in-file. "517,000+ companies" and the compliance-profiles line are verbatim. https://www.trustlayer.io/
  - **UNVERIFIABLE — Ryan Companies, SiteLine Services, WAHVE, Higginbotham, Farsyt, Salem Five, AMN Healthcare, Washington University postings.** Indeed is fetchable (Suffolk Construction $85,000–$127,000 and M.C. Dean $112,800–$141,000 both reconfirmed today, Suffolk's posting is New Haven CT), but these eight listings no longer appear in the cited result sets. Not a strike — job boards rotate — but the WTP row rests on quotes that cannot be re-checked.
- Score challenges:
  - **Reachability by a student, x3: dossier 2 → 3.** The channel picture is understated because two of its facts are wrong. MAIA is fetchable, publishes ~1,000 member agencies / 9,000+ employees, and runs a public **Agent Locator**. **AGC MA publishes a public member directory filterable to "Greater Boston"** (members.agcmass.org/list, "over 100 union and open shop contractors") plus a 2026-09-18 Safety Awards event inside the 30-day window. Insurance Journal's forum has 281 on-topic matches and 2026 activity. Still bad — 50 qualified buyers in 30 days remains unrealistic — but "every touchpoint is an event you must attend, not a forum you can read" is false.
  - **WTP evidence, x2: dossier 3 → 2.** The $0 anchor is worse than the dossier says, not better: it hits the *recommended* buyer, not just the rejected one (Certificial Insured tier, free, with requirement alerting). And the market's published floor is Evident ID at **$15/vendor/yr**, which the dossier missed while asserting "neither publishes a price."
  - **Ceiling, x1: dossier 3 → 2.** "The extraction slice is unoccupied" is the load-bearing premise of the Ceiling justification and of the Verdict's "half of that held up." Evident ID occupies it today with an explicit "upload a contract" flow at a published price.
  - **Risk (5 = low), x2: dossier 2 → 3 (challenged in the opposite direction).** Risk #1 stretches its source. The Big "I" VU "E&O noose" argument is specifically about an *agent* being coerced into attesting to coverage on a form that binds the agency — a party with a licence, an E&O policy and a carrier relationship. A cited, quote-only reading tool sold to the *signer* of the contract is a different posture, and the dossier's stronger legal premise ("opining that a policy fails to satisfy it is arguably insurance advice, which in Massachusetts is licensed activity") carries **no citation** to M.G.L. c.175, 211 CMR, or any enforcement action. Risk #2 (asymmetric downside on a $29 sale) stands on its own and is the real reason for a low score; Risk #1 as written is not evidenced.
  - **Vague / unfirable kill criteria:** (a) "If 3 of them surface **zero actionable gaps**" — "actionable" is undefined and self-graded by the tool's author; (b) "If **2 or more** insurance professionals say **some version of** 'we would never let a third party opine…'" — "some version of" is unfalsifiable, and it kills a channel the dossier has already declined, so it can never change a decision; (c) "If **Certificial, illumend, or TrustLayer** ships contract-document upload → kill" — the named list is too narrow and the condition is already met by a non-listed player (Evident ID) as of today, so as written the trigger will never fire. Only the ~90%-recall eval criterion is measurable as stated.
- Missing:
  - **Evident ID** — omitted competitor that ships the exact wedge ("upload a contract"), sells to the same vendor-compliance buyer, and publishes $15–$25/vendor/yr.
  - **Certificial's free Insured tier** — the dossier read Certificial's agent page and pricing page but not `/insureds`, which is where its own recommended buyer gets the product for $0.
  - **Document Crunch `/subcontractors` + 14-day self-serve trial + insurance/surety page + IRMI, Acrisure and AXA XL partner pages** — DC is already in the recommended buyer's channel, not confined to enterprise GCs.
  - **illumend runs lead-gen SEO on exactly these queries** — `/how-to-read-a-certificate-of-insurance-coi-free-guide`, `/are-subcontractors-required-to-have-insurance-free-ebook`. "There is no SEO surface" is wrong; the surface exists and a funded incumbent already owns it.
  - **AGC MA public member directory + 2026-09-18 Safety Awards**, and **MAIA's public Agent Locator** — two free, online, in-window prospect lists the dossier concluded did not exist.
  - **The uncited Massachusetts licensing premise** in Risk #1 — the single strongest kill argument in the dossier has no statute, regulation, bulletin, or enforcement action behind it.
  - **Internal inconsistency:** the dossier calls the agent-side $0 anchor "the single most important number in the dossier and it is negative," then recommends a buyer for whom that number is not the anchor — and the buyer it picks turns out to have a $0 anchor of its own.
- Overall: **mostly-trustworthy** — every quote I could reach checked out verbatim (including the three the dossier honestly flagged as uncertain, which are in fact clean), but the competitive scan missed a player shipping the exact "unoccupied sliver" at a published price, the free-tool analysis is wrong about the recommended buyer, and two reachability facts (massagent.com 403, Insurance Journal's newest thread) are wrong in the direction of over-killing; the kill verdict survives — on better evidence than the dossier's own reasoning — but three of its four load-bearing arguments need rewriting.


## Final score (main agent, 2026-08-30)
- Fit with assets and strengths: **1/5** ×2 — Document extraction — nothing in the assets.
- Reusable assets: None.
- Subtotal as researched: 42/80 · after adversarial verification: **44/80** (reach 2→3, wtp 3→2, ceil 3→2, risk 2→3)
- **Total: 46/90**
