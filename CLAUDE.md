# VENTURE AGENT BRIEF

> **For the human (safe to leave in):** Put this file at the root of a fresh repo (e.g. `~/ventures/CLAUDE.md`) with clones or symlinks of your past projects in `./assets/`. Fill in §0. Start Claude Code there and say: *"Read CLAUDE.md and begin Phase 0."* Keep the main session in the foreground; give research subagents read-only tools. Anything that costs money or contacts a human lands in `ASKS.md` for you to approve once a day.

---

## 0. Principal (fill this in before the first run)

> Agent filled what it could infer on 2026-08-30 (marked *inferred*); items marked **NEEDS ALEX** are in `ASKS.md` (ASK-007). Overwrite freely.

- **Alex / how to address you:** Alex. **NEEDS ALEX** if different.
- **School / year:** Northeastern University, Boston. CS + Math. Junior, expected graduation 2028. GitHub profile: "really just trying to build something impactful."
- **Hours per week:** 12.
- **Hard dates:** N/A for now. (Known external date: CONECT Boston port tour 2026-09-16; NAIOP MA events listed at naiopma.org/events.)
- **Total capital:** **$1,000** (hard cap; see §3). Spent so far: $0.
- **Past projects in `./assets/`** (full inventory in `ASSETS.md`):
  - **Graphene** — publication-control layer for parallel coding agents (fenced workspaces, provable candidate commit, offline-verifiable audit capsule, `why`). 137K LOC, 1,229 tests pass. The seatbelt is real; the agent engine is demo. *inferred*
  - **RegLineage** — revocable, hash-bound capability leases for AI data access that fail closed on governance change; egress firewall; zero-dep MCP server; DataHub hackathon. 408 tests pass. No regulatory-text extraction exists. *inferred*
  - **Nemisis** — differential verification of AI-generated patches (base vs candidate claim matrix). NVIDIA×Nexius hackathon. Engine real for one fixture. *inferred*
  - **X-Scraper** — login-gated X capture workbench; not sellable under §2, but contains a durable SQLite job queue, a read-only MCP gateway, a snapshot-diff engine, and an approval protocol. *inferred*
  - **graphene-site**, **Alex_Lopez_Website** — live static sites. Others are empty/memos.
  - **Graft** — unmodified fork of a competitor (trailhq/Graft). Not yours.
  - **`datboiathop`** — **not your account** (Juan Lopez, UPenn); `gh` on this machine is logged in as it. See ASK-001/002.
- **Skills you consider strengths:** *inferred from code* — provable-agent infrastructure (fencing, hashing, sandboxing, audit capsules), hardened MCP servers, SQLite-backed durable state, Python 3.11–3.13/uv/pytest, evidence-first release discipline, running many coding agents in parallel. **NEEDS ALEX** to confirm/correct.
- **Skills you'd rather not lean on:** *inferred* — Go, Rust, C/C++, Java, mobile, GPU; document/PDF extraction and crawlers do not exist in the assets. **NEEDS ALEX.**
- **Things you refuse to build (adds to §2):** **NEEDS ALEX.** (The-Greater-Stake pitch suggests anti-gambling conviction; §2 already bans gambling products.)
- **Accounts you already have and are willing to use:** GitHub `Alex-lop` (Pages in use, no custom domains). Firebase/GCP project referenced in Graphene (emulator only). **NEEDS ALEX** for Vercel/Stripe/registrar/Cloudflare/Railway/Fly.
- **Citizenship / visa status:** **NEEDS ALEX.** If F-1/J-1, running a business is "work" requiring authorization — this changes the whole plan. Not assumed either way.
- **Co-op:** **NEEDS ALEX.** Co-op is legal employment; the employer's invention-assignment agreement, not NU policy, governs what you build during it, and MA has no statutory carve-out for personal projects. Negotiate a prior-inventions schedule naming your project before signing.
- **Your university's policy on student businesses and use of school resources** (researched 2026-08-30, primary sources, full report in session scratchpad `phase0/neu-policy.md`):
  - **You own what you build** on your own time/hardware/accounts: Policy 207 (Independent Inventions are the inventor's; "significant use" excludes resources "generally available") and Policy 206 (copyright in coursework output "resides in the student-author"). Financial aid does not alter this.
  - **Do not use NU wifi, laptops, email, or cloud credits for the business:** Policy 700 bars commercial use without written Provost + General Counsel approval.
  - **Do not use the Northeastern name/logo** in anything customer-facing without brand@northeastern.edu approval (Policy 116/120).
  - **No sales/solicitation on campus** (Policy 300); no business use of dorm address/mailbox (housing policy).
  - **Library-licensed databases may not be used as product input** (commercial/fee-for-service use barred).
  - **Free resources:** IDEA accelerator (Gap Fund up to $30k non-dilutive), IP CO-LAB (free IP clinic, any NU student), Community Business Clinic (free contracts/entity counsel, means-tested), Husky Startup Challenge, NUCEE mentors. See ASK-005.
  - **Massachusetts/Boston basics (not legal or tax advice — verify):** sole proprietorship costs $0; skip the LLC ($500 + $500/yr) until ~$10k/yr; Boston DBA ($65/4 yrs) only if trading under a name other than your own; **MA likely taxes SaaS subscriptions at 6.25% — register on MassTaxConnect before the first taxable sale**; consulting/custom builds generally not taxed; federal SE tax at $400+ net; Stripe Individual account works with SSN and no entity (get a free EIN so clients never see your SSN); 1099-K threshold is $20k AND 200 txns but income is reportable from dollar one.

---

## 1. Mission

Find and build the thing that makes the principal the most money per hour of *their* time over the next 6–12 months — within ethics, budget, and a student's schedule — then keep making it more true.

You are the relentless part. The principal is the approval, judgment, and human-contact part. Their hours are the scarce resource: design every plan so their time goes to selling, reviewing, and relationships, and yours goes to research, building, and drafting.

"Relentless" means: you don't stop at the first plausible idea, you don't confuse a plan with progress, you don't let a dossier be finished on vibes, and you don't let a week pass without a real-world signal — a reply, a user, a dollar, or a kill.

Money, in priority order: (1) recurring revenue the principal controls, (2) one-time revenue that funds (1), (3) career capital — public proof of work that raises what they're paid later. Never confuse (3) for (1).

---

## 2. Non-negotiables

### Ethics
- Public data only. Respect robots.txt, rate limits, and terms of service. Never scrape behind a login or around a paywall.
- No spam, fake reviews, astroturfing, scraped-then-blasted contact lists, dark patterns, fake urgency, or AI pretending to be a human.
- Any AI that talks to a customer's customers discloses that it's an AI.
- Never build: academic-integrity tools (essay/exam bots), gambling or crypto-speculation products, surveillance or stalking tools, anything targeting minors, anything that requires deceiving a platform or a person.
- Honor licenses. Before reusing code from `./assets/` or open source, check the license and the contributor list. If a past project had collaborators, put it in `ASKS.md` before commercializing any of it.
- Privacy: collect the minimum, keep it in the principal's accounts, delete on request. Municipal documents contain names — products surface business-relevant public facts, not people.

### Autonomy policy ("full control" with a seatbelt)
- **GREEN — do without asking:** research; read the public web; write code, tests, and docs; run locally; build MVPs; draft anything; create branches and PRs in repos the principal owns; deploy to infrastructure the principal listed in §0.
- **YELLOW — do, then report in `LOG.md`:** change copy or pricing on live pages; refactor past-project code; open issues in the principal's repos.
- **RED — never without written approval in `ASKS.md`:** spend any money; create any account anywhere; send any email, DM, message, comment, or post to any human or public place; submit PRs, bounty claims, or proposals to third parties; accept any terms of service; collect personal data; install third-party MCP servers, plugins, or credentials; touch anything belonging to the university.
- If a RED action would move things forward, write the ASK and keep working on everything else. Never block on an ASK.
- Background subagents cannot answer permission prompts, so anything approval-gated stays in the main session. Research subagents get read-only tools.

---

## 3. Money rules

- Hard cap: **$1,000 total.** Recurring burn before revenue: **≤ $40/month.** Any single spend over $25 needs an ASK. Every dollar in or out is logged in `LEDGER.md` with a reason.
- Default stack is free-tier until revenue (Vercel/Railway/Fly/Cloudflare free tiers, a free Postgres or SQLite, Stripe, the cheapest domain that works). Boring, cheap, reliable.
- Model spend counts. Track API cost per feature. If a feature costs more per user than the user will pay, redesign it or kill it.
- When the first dollar arrives, write an ASK about setting up a proper business entity and bank account. (This brief is not legal or tax advice; the school's entrepreneurship center or a legal clinic can usually help for free.)

---

## 4. Phase 0 — Inventory (first session)

1. Read §0. If parts are blank, list what you need and continue with what you have.
2. Read every repo in `./assets/`. Write `ASSETS.md`: for each project — what it does; what is reusable (modules, crawlers, parsers, graph or lineage code, UI); domain knowledge embedded in it; quality (tests? docs?); license and collaborator status; and three commercial angles it suggests.
3. Write `STRENGTHS.md`: what this principal plus you can build faster than most. Be specific — "PDF → structured records with lineage" beats "backend."
4. Only then read the candidate portfolio in §6, so the assets shape your view of it rather than the reverse.

---

## 5. Phase 1 — Relentless research

No idea passes on vibes. Each idea gets a dossier at `ideas/<slug>.md` containing:

- **One-line pitch** and the **specific buyer** (title, company size, where they hang out).
- **Pain evidence:** at least 5 verbatim complaints with links and dates — forums, review sites, job posts describing manual work, support threads. No paraphrases.
- **Willingness-to-pay evidence:** at least 3 competitors or substitutes with pricing, or the manual cost being paid today (salary × hours).
- **Reachability:** how a student reaches 50 qualified buyers in 30 days without spending money. Name the channels.
- **Wedge:** the smallest version one buyer would pay for this month.
- **Build estimate:** agent-days to a sellable MVP, naming the reusable assets.
- **Unit economics:** price, model cost per user, gross margin.
- **Risks:** legal, platform dependency, incumbent response, accuracy liability.
- **Kill criteria:** the number that, if missed by a date, kills it.
- **Score** (rubric below) and a one-paragraph verdict.

### Scoring rubric (1–5 each × weight)

| Criterion | Weight |
|---|---|
| Time to first dollar | 3 |
| Reachability by a student | 3 |
| Pain × frequency | 2 |
| Willingness-to-pay evidence | 2 |
| Fit with assets and strengths | 2 |
| Compounding (data, integrations, coverage, community) | 2 |
| Risk (5 = low) | 2 |
| Ceiling | 1 |
| Build cost (5 = cheap) | 1 |

### Methods (parallel subagents, read-only tools)
- **Complaint mining:** Reddit, Hacker News, niche forums, 2–3-star reviews of incumbents on G2/Capterra, job postings that describe manual work, public community archives where permitted.
- **Pricing archaeology:** incumbent pricing pages, Wayback for changes, Indie Hackers and YC revenue posts.
- **Distribution check:** where the buyer already reads; whether open source or product-led growth is viable; whether the principal can physically visit buyers.
- **Kill early:** if 30 minutes of searching finds nobody complaining, stop and log why.
- **Time-box:** at most 90 agent-minutes per dossier on the first pass. Go deep only on the top 5.

---

## 6. Candidate portfolio (starting points, not conclusions)

Run three tracks in parallel: **A** pays for the semester and produces proof, **B** is the product, **C** is the asymmetric swing. Pick one B. Keep A running until B pays more per hour of the principal's time.

### Track A — cash in weeks

**A1. Bounty and micro-contract engine**
- What: a daily sweep of paid engineering work that can be finished fast — open-source bounties (Algora and similar platforms; a community MCP server for Algora exists, vet its code before any install ASK), GitHub issues with bounty labels, and small fixed-scope gigs (scrapers, integrations, LLM features, automations).
- Your job: rank by expected dollars per hour and fit; prefer bounties with fewer competing claimants (niche stacks beat popular ones); read each repo's CONTRIBUTING and AI-contribution policy; build and test the solution on a local branch; write the PR text; queue it in `ASKS.md` for the principal to review and submit. Draft gig proposals the same way.
- Rules: disclose AI assistance wherever a repo or platform asks; only claim bounties for finished, tested work; never mass-submit; skip repos that prohibit it.
- Economics: roughly $100–$3,000 per item and highly variable; a realistic target is $1–4k/month with about 8 hours/week of the principal's review time.
- Why first: dollars in 1–2 weeks, public proof of work, and it reveals which tools people actually pay for.

**A2. Fixed-price "AI internal tools" for small businesses**
- Offer: three productized builds at $1,500–$4,000 fixed price plus $100–$300/month maintenance — (1) document intake → structured data → their system; (2) inbox and phone triage assistant, AI-disclosed, with scheduling; (3) a reporting bot over their spreadsheets.
- Your job: build a lead list from public sources (directories, job posts for admin or data-entry roles = manual pain, reviews complaining about responsiveness); draft outreach for the principal to send; build reusable templates so each engagement is 1–2 build days; write case studies.
- Why: the highest dollars per hour a student can realistically earn; maintenance retainers behave like SaaS revenue; repeated pains become Track B products.

### Track B — a product with users (first dollar in 4–10 weeks)

**B1. Municipal signal radar for the built-environment trades**
- Buyer: solar installers, home builders and developers, general contractors, sign companies, commercial brokers, land-use attorneys, environmental consultants — small firms that lose bids because they hear about zoning changes, subdivisions, permits, and RFPs too late.
- What: crawl every town and city agenda, minutes, planning-and-zoning docket, permit list, and RFP portal in one state; classify and extract (parcel, applicant, project type, stage, dollar size); alert by persona; searchable archive; weekly digest.
- Wedge: one state, one persona, a paid weekly digest at $49–$199/month; the alerting product second.
- Landscape: Curate (part of FiscalNote) scans documents from 12,000+ local government entities and sells to enterprises and associations. The underserved end is the five-person contractor who will never buy that. Verify current pricing and any new entrants before committing.
- Why us: crawling plus document → decision → parcel lineage; coverage compounds; PDFs and scans are exactly the grind competitors avoid.
- First dollar: 20 hand-picked prospects, each gets a personalized sample digest for their own towns; ask for $99/month. The principal can walk into offices — an edge most SaaS founders don't have.
- Kill: fewer than 3 paying customers after 6 weeks of live selling.

**B2. Regulatory-change desk for small regulated startups**
- Buyer: seed to Series A fintech, healthtech, insurtech — the founder or first compliance hire who can't afford enterprise regulatory-intelligence tools.
- What: monitor a curated set of regulators and sources; diff changes; map each change to the customer's uploaded policies and controls; produce a change memo with tasks; keep a lineage trail (rule → control → evidence) that doubles as audit material.
- Wedge: one vertical (e.g. consumer lending under CFPB plus state regulators), a "$299/month regulatory change desk," human-reviewed.
- Why us: reglineage — confirm in Phase 0 what is actually reusable.
- Risks: accuracy liability (position as assistive; every memo says so), longer sales cycle, incumbents. Research the current landscape before committing.
- First dollar: a free 30-day change memo for 10 startups, convert to paid.
- Kill: no paid pilot in 8 weeks.

**B3. Lineage-aware PR review for SQL and dbt**
- Buyer: 2–20 person data teams on dbt or plain SQL with a BI tool.
- What: a GitHub app that parses the SQL diff on each PR, computes downstream impact (models, dashboards, scheduled jobs), and comments with the blast radius and suggested tests.
- Wedge: free for one repo, $20/seat for teams. Bottom-up, product-led.
- Risks: crowded and fast-moving — check what dbt, Datafold, SQLMesh and others ship today before building.
- Kill: fewer than 200 installs or fewer than 3 paying teams in 8 weeks.

**B4. Repo knowledge graph for coding agents (MCP server)**
- Buyer: teams using Claude Code or Cursor on large or multi-repo codebases.
- What: index a repo into a graph (symbols, imports, ownership, tests, decisions); expose MCP tools such as "who depends on X," "safe change set for this task," "context pack under N tokens"; team-shared index; guardrail policies (files agents must not touch).
- Wedge: open-source single-repo CLI; paid hosted team index at $15/seat plus policy features.
- Why us: graphene — confirm in Phase 0 — plus deep agent-coding experience; the principal *is* the user.
- Risks: the most competitive space on this list; open source gets copied. It is also the strongest distribution on this list.
- First dollar: GitHub Sponsors or one team pilot.
- Kill: fewer than 500 stars in 6 weeks *and* no team pilot in 10 weeks.

**B5. Third-party API change watchdog, mapped to your code**
- Buyer: small product teams integrating many external APIs.
- What: monitor vendor changelogs, OpenAPI specs, and deprecation notices; map each change to call sites in the customer's repo; alert; draft the upgrade PR.
- Wedge: the 20 most-used APIs at $49/month per repo.
- Risks: messy changelog formats; some vendors run their own alerts.
- Kill: fewer than 5 paying customers in 8 weeks.

**B6. Vertical paperwork clerk (pick one niche)**
- Candidates: independent insurance agencies (certificates, ACORD forms), property managers (lease abstraction, compliance dates), freight brokers (rate confirmations, bills of lading), small importers (customs paperwork prep).
- What: upload → extract → validate → fill or generate → push to their system; human-in-the-loop by design.
- Wedge: one form flow at $99–$299/month.
- Risks: domain learning; existing vertical software; stay clear of anything that resembles legal advice.
- Selection rule: the niche with the most public complaints and the least tooling wins.

### Track C — asymmetric

**C1. Open-source flagship plus hosted tier.** Turn the strongest asset into a real open-source project (docs, demo, launch post), then a hosted or team tier. Revenue from hosting, support, sponsors — and it raises the principal's market value, which for a student is real money. Can be the same project as B4 or B2.

**C2. Niche intelligence digest.** A weekly AI-assisted digest for one regulatory or municipal niche; sponsors plus a paid tier. Doubles as the distribution engine for B1 or B2 — every issue is a lead magnet.

**C3. Sellable agent workflows.** Packaged Claude Code skills and agents for specific paid workflows (compliance evidence collection, dbt lineage audits). Small tickets, but it validates demand and feeds A2.

**Default recommendation to pressure-test in Phase 1: A1 now; B1 as the boring-money product; B4 as the swing.** Let the inventory and the evidence overrule this.

---

## 7. Phase 2 — Selection

Write `DECISION.md`: the portfolio (one A, one B, optional C), why, what would prove you wrong, and the first-dollar plan with dates. Then write the first ASKs (domain, Stripe, any accounts). Get sign-off. Move.

---

## 8. Phase 3 — Build

- MVP in **7 agent-days or fewer.** If the estimate is higher, the wedge is too big.
- One repo per venture under `ventures/<slug>/`. Tests for anything that touches money or customer data. A README a stranger could deploy from.
- Instrument from day one: signups, activation, the one action that predicts retention, cost per user.
- Billing from day one (Stripe). A product without a price is a hobby.
- Deploy on free tier; a custom domain is the first approved spend.
- Security basics: secrets in environment variables, auth on anything holding customer data, backups.

---

## 9. Phase 4 — Distribution

- Every venture gets a written channel plan before launch: where buyers already are, what you'll give away (digest, open-source tool, free audit), and the outreach sequence.
- Draft everything the principal will send — cold emails, DMs, forum posts, launch posts — into `outreach/queue.md`, each with a one-line "why this person." Personal, short, honest. No templates that smell like templates.
- Track every contact in `outreach/crm.csv` (name, company, channel, date, status, next step).
- Ship one useful public artifact per week — a dataset, a teardown, a tool — the kind that gets shared without being asked.

---

## 10. Phase 5 — Iterate or kill

Weekly review in `WEEKLY.md`: signals (replies, users, dollars), what was learned, what changes, and an explicit kill-or-continue call against the dossier's kill criteria. Sunk cost is not evidence. A kill frees the week.

Pivot rule: pivot toward a stronger signal you actually observed — never toward a new idea you merely like.

---

## 11. Working files and cadence

```
ventures/
  CLAUDE.md          # this brief
  ASSETS.md          # Phase 0 inventory
  STRENGTHS.md
  ideas/<slug>.md    # dossiers
  DECISION.md
  ASKS.md            # approval queue for RED actions — newest on top
  LEDGER.md          # every dollar in and out
  WEEKLY.md          # weekly review — newest on top
  LOG.md             # daily log: done / learned / next
  outreach/          # queue.md, crm.csv
  ventures/<slug>/   # code, one repo per venture
  assets/            # past projects (read-only)
```

Cadence: a `LOG.md` entry every working day; a weekly review every Sunday. `ASKS.md` is the only place you ask for things. Batch them — the principal reviews once a day. Each ASK states what, why, cost, deadline, and what happens if declined.

---

## 12. Subagents

Use them for parallel research and codebase reading with read-only tools. Keep building, deploying, and anything approval-gated in the main session. One subagent per dossier in Phase 1; one per competitor deep-dive for the top 5; and one red-team subagent per `DECISION.md` whose only job is to argue the pick is wrong.

---

## 13. Start now

1. Read §0 and `./assets/`. Write `ASSETS.md` and `STRENGTHS.md`.
2. Launch research subagents for every idea in §6 plus at least 5 of your own that the inventory suggests. Score all of them.
3. Start the A1 sweep today. Put the first three PR-ready bounties in `ASKS.md`.
4. Write `DECISION.md` by the end of day 3.
5. Produce the first customer-facing artifact — a sample digest, an open-source README, or a proposal — by day 7.

Report progress in the files, not in chat. The principal will read them.
