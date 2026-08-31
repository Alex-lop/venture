# A1. Bounty and micro-contract engine

**Slug:** a1-bounty-engine  |  **Track:** A  |  **Researched:** 2026-08-30  |  **Status:** researched

## One-line pitch
A daily sweep of paid open-source bounties and small fixed-scope gigs, ranked by expected dollars-per-hour, that an AI agent implements and the principal reviews and submits — a thesis that the evidence below substantially refutes as a revenue engine, while pointing hard at a better adjacent business.

## Specific buyer
Two distinct buyers, and neither is well served by this product:

**Buyer 1 — the bounty poster.** Founder or lead maintainer of a commercial open-source (COSS) company, typically 3–30 people, seed to Series A. Examples found funding real bounties: tscircuit (EDA tooling), Tenstorrent (AI silicon, $200–$3,000 per bounty), Coolify, Ziverge ($143K distributed), Teamhanko, Twenty (YC S23, $2,500 bounty), Archestra. They hang out on: Hacker News (`Show HN`, `Ask HN: Freelancer?` monthly threads), r/opensource, r/rust, r/elixir, the Algora and Opire dashboards, their own project Discords, and X. Offline they cluster at FOSDEM (Brussels, February), Open Source Summit North America, All Things Open (Raleigh, October), and — locally for the principal — the Boston-area open-source and startup scene: Boston New Technology, Boston Python, Boston Software Crafters, the MIT/Harvard startup orbit, Cambridge Innovation Center, and Northeastern's own entrepreneurship and OSS clubs.

**Buyer 2 — the small-company gig client** wanting a scraper, integration, LLM feature, or automation. Reachable through Upwork, Contra, the HN monthly freelancer thread, and local Boston networks.

Critically: **the principal's single biggest structural asset — being physically in Boston and able to walk into a room — is worth exactly zero to this idea.** Bounties are won by whoever's PR lands first on a public GitHub issue, from anywhere on earth. This idea puts the principal into global, anonymous, latency-based competition and discards his only unfair advantage.

## Pain evidence (verbatim, >= 5)

1. > "Meanwhile, several companies are no longer offering bounties. It's becoming tedious to sift through all the AI-generated submissions, many of which are false positives."
   — HN user, https://news.ycombinator.com/item?id=48164705, posted 2026-05-16. Commenting on the "I tried to make Claude make me money on open-source bounties" thread. This is the *supply of bounties itself* shrinking in response to AI submissions.

2. > "Better models are better.But smaller and cheaper models which produce more junk are cheaper.The cost is with the project maintainer, not with the bounty hunter."
   — HN user, https://news.ycombinator.com/item?id=48164853, posted 2026-05-16. Names the externality that makes maintainers hostile to exactly the workflow this idea proposes.

3. > "This avalanche is going to make maintainer overload even worse. Some projects will have a hard time to handle this kind of backlog expansion without any added maintainers to help."
   — the lead maintainer of curl, on the project maintainer's own blog, https://daniel.haxx.se/blog/2026/04/22/high-quality-chaos/, posted 2026-04-22. The single most-cited maintainer voice on AI contribution volume. The same post reports report frequency **doubled vs 2025**.

4. > "From by my own experience, you'll have to review/test the boring task from a one-time contributor, which is also not fun. You don't need to do that as often if the contributor is going to stay, but you're not attracting this sort of contributions with bounties."
   — HN user, https://news.ycombinator.com/item?id=37543455, posted 2023-09-17, on the "Bounties Damage Open Source Projects" thread (105 comments). A maintainer describing why bounty-sourced work is a net cost to the project.

5. > "Note that competition is fierce for the "easy" tasks on Algora and many Algora regulars will open a PR (pull request) within minutes of a bounty being available publicly."
   — HN user, https://news.ycombinator.com/item?id=38334627, posted 2023-11-19. Notable because this was true *three years before* the AI agents arrived. The race predates the agent wave; agents only compressed it.

6. > "Every legitimate $50 to $1,000 bounty had between **8 and 158 attempts** within hours of being posted, and 8 to 10 open PRs already in flight." … "You are not waiting on demand. You are *the eleventh PR* into a queue that the maintainer has been ignoring for a week."
   — Author of `algora-scout2`, https://github.com/iotqowrop/algora-scout2/blob/main/POST.md, published 2026-05-16 (discussed on HN 2026-05-16). This is a direct, documented replication of the exact workflow in this brief: Algora board sweep, Claude implements, human reviews before submit, $20 token budget. **Result after 48 hours and 80 scanned bounties: $0.**

7. > "Maintainer review is the bottleneck, not solution quality. Even a perfect PR submitted ninth probably loses to a mediocre PR submitted first."
   — Same source and date as (6). This is the sentence that kills the brief's "prefer bounties with fewer competing claimants / niche stacks beat popular ones" strategy, because the same author found $50 issues on niche repos attracting 20+ attempts in a single day.

8. > "Why would you burn money on $17 - $50 bounties? In the hopes that you'd collect $30 at $5.68 spend? You can literally offer your services to carry boxes for a higher hourly rate."
   — HN user, https://news.ycombinator.com/item?id=48165009, posted 2026-05-17. The unit-economics objection, stated by a working developer.

9. > "No autonomous AI agent use or vibe coding. This already leads to an auto-ban from our GitHub repository." … "No use of AI to generate substantial pieces of code. We require all code to be human authored."
   — Godot Engine official contribution policy, https://godotengine.org/article/contribution-policy-2026/, published 2026-06-30. Account-level consequence, not just PR rejection.

10. > "**SecureBananaLabs/bug-bounty** — 21 auto-generated "bug" issues, all closed without merge. The repo exists purely to waste developers' time." … "**90% of "Bounties" Are Fake**"
    — one commenter, https://dev.to/zeroknowledge0x/i-let-an-ai-agent-hunt-open-source-bounties-for-48-hours-heres-what-i-learned-about-the-future-5131, published 2026-05-29. Of 200+ bounties scanned, this author found **12 legitimate** (6%).

11. > "frequently you will need to cleanup bounty PRs. I.e. change from inline styles to tailwind, use middleware instead of inline controls on functions, etc." … "It is much easier to get bounty hunters when your project uses beginner friendly pieces like React/Astro. We have a lot of regret for going with SolidJS."
    — HN user, https://news.ycombinator.com/item?id=37770006, posted 2023-10-04, self-described as "a bootstrapped founding team" — i.e. an actual paying bounty poster. Note the second sentence directly contradicts the brief's "niche stacks beat popular ones" thesis from the *buyer's* side: niche stacks get fewer hunters because they're harder, not because they're underpriced.

### Independent verification of saturation (primary data, collected 2026-08-30)
I did not take the writeup's numbers on faith. Querying the public GitHub REST API for `/attempt` comments on the issues it named:

| Issue | Total comments | Comments containing `/attempt` |
|---|---|---|
| `tscircuit/dsn-converter#54` ($170) | 256 | **204** |
| `tscircuit/schematic-trace-solver#29` ($100) | 130 | **76** |
| `rohitdash08/FinMind#121` ($500, still open, labels include `💎 Bounty` `$500`) | 112 | **45** |

Saturation is real and has grown roughly 30% since the May 2026 writeup (158 → 204 on the same issue). `tscircuit` is a niche electronic-design-automation project — precisely the "niche stack" the brief hoped would be less contested.

### The one apparent counter-example, and why it does not apply
one commenter reported a follow-up 96-hour run (https://dev.to/zeroknowledge0x/i-let-an-ai-agent-hunt-open-source-bounties-for-96-hours-heres-the-brutal-truth-about-what-42p3, published 2026-06-01): **240 PRs submitted, 72 merged, "$500-800" earned.** Three reasons this is not a template for the principal:
- It required submitting 240 PRs in 4 days from an unsupervised agent with "No supervision. No approval gates." That is mass-submission — explicitly forbidden by the principal's own rules and by the ethics constraints in this brief.
- 100% of merges came from 7 repos, headed by `ritesh-1918/HELPDESK.AI` (28) and `Aigen-Protocol/aigen-protocol` (22) — obscure projects, not the COSS companies with real budgets.
- Earnings are reported as a $300-wide range and are commingled with dev.to article revenue. Merges are not payouts.

## Willingness-to-pay evidence (>= 3)

| Competitor / substitute | Pricing (exact, URL, date seen) | Who it serves | Gap vs. this idea |
|---|---|---|---|
| **Algora** | ⚠️ VERIFIER: misattributed - Historically "23% fee over your rewarded bounties (20% Algora fee + 3% Stripe fee)" — quoted from Algora's docs by HN user, https://news.ycombinator.com/item?id=35829168, 2023-05-05. Founder one commenter corroborates "a take rate of about 25% for each bounty" (https://news.ycombinator.com/item?id=40726661, 2024-06-19). As of 2026-08-30 the algora.io homepage headline is **"Open source tech recruiting"** / "Connecting the most prolific open source maintainers & contributors with their next jobs" — the bounty board is now a secondary surface. | COSS companies funding GitHub issues; increasingly, companies hiring OSS contributors | The platform this brief is built on has repositioned toward recruiting. A "daily Algora sweep" is a sweep of a de-prioritized surface. The 23% take also cuts a $100 bounty to $77 before token cost. |
| **Opire** | "4% Opire fees" + Stripe "5.25% + $0.85" on bounties; "10% of the tip amount" on tips. Org plans: Starter **$16.67/mo**, Pro **$33.33/mo**, Enterprise **$166.67/mo** (annual billing). https://opire.dev/home, seen 2026-08-30. | Smaller OSS orgs wanting cheaper bounty infrastructure than Algora | Confirms real WTP for bounty *infrastructure*, and confirms the take-rate compression (23% → 4%). Nothing here creates a defensible position for a *solver*. |
| **Human freelance contractors (the true substitute)** | Live rates from `Ask HN: Freelancer?` threads: **$75/hour** — 14-person agency, https://news.ycombinator.com/item?id=49263751, 2026-08-11; **$100/hour** — solo senior engineer, Madison WI, https://news.ycombinator.com/item?id=48358866, 2026-06-01; **$110/hour** — 20-year full-stack/AI engineer, https://news.ycombinator.com/item?id=48360454, 2026-06-01. | Startups and SMBs needing scoped dev work | **This is the key pricing insight.** A task a $100/hr contractor bills at $300–$1,000 is posted as a $50–$500 bounty. Bounty posters are deliberately buying below market, and the discount is paid for by the losing entrants' unpaid labor. The principal would be entering the market on the losing side of that transfer. |
| **Proven large bounties (upper bound of WTP)** | Tenstorrent $200–$3,000 per issue; microG single $10,000 bounty; Prettier pooled bounty reached **$22,500** (Wasmer plus one individual sponsor added $12,500); `BasedHardware/omi` React Native bounty up to **$20,000**. Sourced from HN one commenter https://news.ycombinator.com/item?id=45278787 (2025-09-17) and https://news.ycombinator.com/item?id=43365943 (2025-03-14), and an open-source founder https://news.ycombinator.com/item?id=38252861 (2023-11-13). | Well-funded infra companies | Real money exists at the top of the market — but these are 2–3 month engagements requiring deep domain expertise (silicon toolchains, formatter internals), not 12-hrs/week fast-finish items. They are not the market this brief describes. |
| **Upwork (the gig half of the idea)** | AI & ML subcategory reply rate **7.21%** vs platform mean 7.45%; 3,535 proposals in the Dec 2025–Feb 2026 window in AI/ML vs ~37,000 in Web Dev; Upwork's active client base **shrank 6% in 2025**, flat-to-down in Q1 2026. https://gigradar.io/blog/upwork-market-report-2026, seen 2026-08-30. | Freelance developers bidding on fixed-scope work | A 7.21% reply rate means ~14 proposals per single conversation, before you win anything. This is a customer-acquisition cost paid in the principal's scarcest resource: his own hours. |

### The manual cost being paid today
A maintainer choosing between (a) doing a 6-hour feature themselves and (b) posting a bounty is comparing their own time against $50–$500. At the market contractor rate of $100/hr (one commenter, 2026-06-01), that 6 hours is worth **$600**. The bounty is priced at 8–83% of the honest contract price. That spread is the entire business model of bounty boards, and it accrues to the *poster*, not the solver. There is no version of this where the solver captures the surplus.

## Reachability (50 qualified buyers in 30 days, $0)
Reachability is, ironically, this idea's one genuine strength — the work is public and permissionless. The problem is that it is equally reachable by everyone else on earth.

- **GitHub label search** — `gh search issues --label "💎 Bounty"` returns the entire live pool at zero cost, instantly, with no gatekeeper. 50 "buyers" (bounty-posting repos) can be enumerated in about 10 minutes. Verified working (rate-limited during this research at 5,000 req/hr shared).
- **Algora board** (https://algora.io) and **Opire** (https://opire.dev) — public, no login required to browse.
- **HN `Ask HN: Freelancer? Seeking freelancer?`** — monthly, first business day. **This channel is dead on the demand side.** I counted top-level posts across the last three threads: August 2026 (https://news.ycombinator.com/item?id=49157021): 15 posts, **15 SEEKING WORK, 0 SEEKING FREELANCER**. July 2026 (id=48749020): 20 posts, **19 SEEKING WORK, 0 SEEKING FREELANCER**. June 2026 (id=48358236): 31 posts, **28 SEEKING WORK, 1 SEEKING FREELANCER**. That is **62 sellers to 1 buyer** over three months.
- **r/opensource, r/forhire, r/rust, r/elixir** — Reddit's public JSON search endpoint returned HTML rather than JSON during this research (blocked), so I could not verify member counts or post frequency first-hand and will not assert them.
- **Boston, in person** — Boston New Technology, Boston Python, Boston Software Crafters, CIC Cambridge, MIT/Harvard startup events, Northeastern's OSS and entrepreneurship clubs. **These are all real and all irrelevant to this idea**: no Boston founder awards a GitHub bounty because you shook their hand. The in-person advantage is entirely stranded here, which is itself an argument for spending the principal's 12 hours elsewhere.

## Wedge
The smallest honest version that could earn a dollar this month: **pick exactly one niche, paying repo with a documented merge history and a stack most hunters avoid** — Tenstorrent (`tt-metal`, $200–$3,000, C++/hardware), the Elixir ecosystem, or a Zig/Rust infra project — **become a real, known contributor with 2–3 unpaid merged PRs first**, then take bounties as an already-trusted contributor. This is the "What I'd do differently" conclusion of the person who ran the experiment: *"Pick one repo and become a contributor first. Maintainers ship bounties to people they trust."*

That wedge is genuinely viable. But note what it actually is: **it is not a product, it is a job.** It produces one-time labor income, it takes weeks of unpaid work before the first dollar, and it stops the moment the principal stops. Under the principal's stated money priority — recurring revenue he controls first, one-time revenue that *funds* recurring second — this ranks as a weak third: career capital with a small cash kicker.

## Build estimate
**0.5 agent-days to a sellable MVP** — and the MVP already exists and is MIT-licensed. `scout.py` (https://github.com/iotqowrop/algora-scout2) is "a couple hundred lines" and already does: enumerate bounty-labeled issues, filter junk/reserved/out-of-range, count `/attempt` comments, find linked PRs, measure staleness, diff against prior scans, flag `RIPE` candidates.

Components required: `gh` CLI + GitHub REST (free, 5,000 req/hr), a JSON state file, a ranking heuristic, a cron entry, and an agent loop for implementation. There is no hard engineering here. **The build cost being near-zero is precisely the problem: anyone can build it, and roughly 200 people per issue already have.**

Reusable assets: X-Scraper durable job queue for the daily sweep; the gh-api harness written today.

## Unit economics
- **Price:** not set by the principal. Bounty amounts are posted by the buyer, $50–$500 typical, $1 spam at the bottom, $2,500+ rare.
- **Take rate against him:** 23% on Algora historically (a $100 bounty nets $77); ~4% + Stripe 5.25% + $0.85 on Opire (a $100 bounty nets ~$89.90).
- **Model/API cost:** The documented single win in this space cost ~$16 in tokens to earn $16.88 — a **1.05x gross multiple before any human time**. Assumptions: Claude-class model, one repo clone + test cycle per attempt, ~1–3M tokens per serious attempt. On a flat-rate subscription within the principal's $40/mo cap, marginal token cost is near zero, but so is throughput — the "$506 run-rate" figures circulating come from 30 parallel agents on flat-rate, not from a single reviewed pipeline.
- **Hosting:** $0. A cron job on the principal's own machine.
- **Recurring burn:** ~$20/mo (one AI coding subscription), comfortably under the $40 cap.
- **Gross margin — the real number:** margin per *attempt* is negative for every attempt that loses, and the observed loss rate for honest single-submission play is at or near 100%. The direct replication ran 3 scans over 2 days across 80 bounties and found **zero** viable candidates and **zero** dollars. Break-even at $20/mo requires one winning $50 bounty per month net of fees ($38.50 on Algora); the evidence does not establish that even that is reliably achievable when you are the 11th PR.
- **Recurring revenue: $0.** Every dollar is one-time. Month 13 starts at zero exactly like month 1.

## Risks
- **Legal / ToS:** Low-moderate. Reading public GitHub issues via the documented API is fine. But GitHub's secondary rate limits explicitly invoke the ToS scraping clause (I triggered one during this research), so a high-frequency sweep needs care.
- **Account ban — this is the sharp one.** Godot's policy auto-bans for autonomous agent use (2026-06-30, quoted above). A maintainer on another bounty-funded project publicly banned a contributor over a bounty dispute (the account and the maintainer's stated reason are deliberately not reproduced here, `CLAUDE.md` §2). A GitHub account is the principal's permanent professional identity as a 2028 grad; risking it for $50 items is a catastrophically bad trade of career capital.
- **Platform dependency:** Total, and deteriorating. Algora — the platform this brief names first — now leads with "Open source tech recruiting." Its public tRPC bounty-list endpoint returned an empty item list when I queried it on 2026-08-30, though I could not confirm the correct parameter shape, so I treat that as inconclusive rather than as proof the board is empty.
- **Incumbent response:** Not a competitor problem — a *commons* problem. Bounty supply is actively contracting in response to AI submissions ("several companies are no longer offering bounties"). The principal would be entering a market that is shrinking because of people doing exactly what this idea proposes.
- **Counterparty / payment risk:** Documented non-payment. 90% of searched bounties were assessed as fake by one researcher; honeypot repos (`SecureBananaLabs/bug-bounty`, `UnsafeLabs/Bounty-Hunters`) exist specifically to harvest free labor; "merged PRs but zero payment" is a reported pattern. There is no contract and no recourse.
- **Reputational / ethical:** The only strategy shown to produce meaningful revenue (240 PRs in 96 hours) is the one the principal's ethics forbid. Playing honestly means playing the strategy that demonstrably returns $0.
- **Accuracy liability:** Low in dollar terms — a bad PR gets closed, not sued — but each bad PR is a permanent public artifact attached to the principal's name.

## Kill criteria
This idea should be killed unless, by **2026-09-30** (30 days), the principal has:
- **≥ 1 bounty actually paid out, net ≥ $150**, from ≤ 8 total hours of his own review time, submitted honestly (single submission, AI disclosed, no mass-submit); **and**
- **≥ 3 distinct bounties** identified where the `/attempt` count at time of discovery was **≤ 3** and the repo has a verified history of merging external PRs.

If either is missed, stop. Given that a direct replication of this exact workflow returned $0 across 80 bounties, and that live verification on 2026-08-30 shows 204/76/45 `/attempt` comments on the sample issues, **my prior is that both criteria fail.** I would not spend the 30 days.

## Incumbents and adjacent players
- **Algora** — https://algora.io — the reference bounty platform; ~23% historical take rate; as of 2026-08-30 leads with "Open source tech recruiting," bounties now secondary.
- **Opire** — https://opire.dev/home — direct Algora competitor; 4% + Stripe; org plans $16.67–$166.67/mo.
- **Polar** — https://polar.sh — OSS monetization / merchant-of-record; 5% + 50¢ standard as of 2026 (4% + 40¢ grandfathered pre-2026-05-27).
- **BountyHub** — https://alternativeto.net/software/bountyhub/about — works on repos without a bot installed, dedicated UI (per HN one commenter, 2025-01-05).
- **bountyboard.dev** — https://bountyboard.dev/bounties — smaller aggregator.
- **TaskBounty** — https://www.task-bounty.com/for-oss-maintainers — "turn your GitHub issue backlog into funded bounties."
- **Bountysource** — defunct; documented as having taken at least $21,000 from OSS developers (https://boehs.org/node/bountysource). The cautionary tale of the category.
- **octobounty** — https://github.com/shanepadgett/octobounty — open-source bounty tooling.
- **`algora-scout2`** — https://github.com/iotqowrop/algora-scout2 — MIT-licensed scanner that is functionally the MVP this brief proposes building. Already free.
- **HackerOne / Bugcrowd** — private security programs; paused parts of the Internet Bug Bounty in 2026 because remediation, not discovery, became the bottleneck.
- **Upwork / Contra** — the gig half; 7.21% reply rate in AI/ML, shrinking client base.

## Score

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Time to first dollar | ×3 | **2** | The payment *mechanism* is fast (autopay 1–3 business days on merge, no sales cycle), but the direct replication of this exact workflow produced $0 across 80 bounties in 48 hours, and the honest wedge requires weeks of unpaid contribution before the first paid bounty. |
| Reachability by a student | ×3 | **5** | Genuinely excellent and the idea's one real strength: the entire buyer pool is public, permissionless, and enumerable in ten minutes via `gh search issues --label "💎 Bounty"` at zero cost — no gatekeeper, no credential, no introduction needed. |
| Pain × frequency | ×2 | **2** | Maintainer pain is real and frequent, but it has *inverted*: they are drowning in PRs to review ("The cost is with the project maintainer"; curl's "avalanche"), not starving for code. This idea supplies more of what already hurts them. |
| WTP evidence | ×2 | **4** | Money demonstrably changes hands — Ziverge $143K distributed, Prettier's $22,500 pooled bounty, Tenstorrent $200–$3,000, Twenty's $2,500 — so willingness to pay is proven; it is the principal's *probability of capturing it* that is unproven. |
| Fit with assets and strengths | ×2 | **3** | Repo tooling and test discipline fit; but the channel is dead, so fit is moot. |
| Compounding | ×2 | **1** | Effectively zero — no data moat, no integrations, no coverage advantage, no customer list, no recurring contract; every bounty is a fresh race from zero, and `scout.py` is already MIT-licensed and free to all competitors. |
| Risk (5 = low) | ×2 | **2** | GitHub account bans are a live consequence (Godot auto-bans for agent use; Archestra publicly banned a hunter), non-payment is documented, ~90% of listed bounties were assessed as fake, and the named platform has pivoted away from bounties. |
| Ceiling | ×1 | **1** | Hard-capped by the principal's own review hours and never becomes an asset — at 8 hrs/week even a fantasy $100/hr effective rate tops out near $3,200/mo, it stops the day he stops, and it can never be sold. |
| Build cost (5 = cheap) | ×1 | **5** | Near-free: the MVP already exists as a couple hundred lines of MIT-licensed Python, needing only `gh`, a JSON state file, and a cron entry — which is also precisely why it confers no advantage. |

**Subtotal excluding Fit: 45 / 80.**
(6 + 15 + 4 + 8 + 2 + 4 + 1 + 5 = 45. With Fit scored later, max total is 90.)

That 45 is flattered by a single 5×3 = 15 from Reachability. Strip that one criterion and the idea scores 30/65 — and the reachability score is itself the problem in disguise: perfectly reachable by the principal means perfectly reachable by 204 other claimants on the same issue.

## Verdict
**Do not build this.** Not because nobody is in pain — the pain is abundant and well documented — but because the pain has inverted relative to the brief's premise, and because someone already ran this exact experiment and published the negative result. In May 2026 a developer swept the Algora board, had Claude implement, kept a human review gate, capped spend at $20, and earned **$0** across 80 bounties; every legitimate $50–$1,000 item had 8–158 claimants within *hours*. I verified that independently on 2026-08-30 against the live GitHub API and found saturation had grown roughly 30% since (204 `/attempt` comments on a single $170 issue, on a niche EDA repo — exactly the "niche stack" the brief hoped would be quieter). The brief's claimed economics of $1–4k/month for ~8 hrs/week are not supported by any evidence I could find; the only run that produced real money required 240 unsupervised PRs in 96 hours, which the principal's own ethics rules forbid, and even that yielded a vague "$500-800" concentrated in seven obscure repos. Meanwhile the structural facts are all adverse: Algora — the platform named first in the brief — now leads with "Open source tech recruiting"; Godot auto-bans accounts for agent contributions and 37 of 120 surveyed projects ban AI code outright; bounty supply is *contracting* because of AI submissions; posters deliberately price at $50–$500 for work a $100/hr contractor bills at $600; and the HN freelancer channel ran 62 sellers to 1 buyer over the last three months. Most damning against the principal's own stated priorities: this generates **zero recurring revenue, zero compounding assets, and strands his Boston in-person advantage completely** — it is a lottery ticket denominated in his single scarcest resource. The honest wedge (become a trusted contributor to one niche paying repo like Tenstorrent, then take bounties as an insider) is real and I would not talk him out of it *as a career-capital play worth a few hours a month* — but it is a job, not a business, and it should not be Track A's engine. The genuinely valuable finding from this research is that every source points at the same unserved buyer from the opposite direction: **maintainers are drowning in AI-generated PRs and will pay to triage them.** That is the business hiding inside this dossier, and it is recurring.

## Research log
**Time spent:** ~70 agent-minutes.

**Queries run:**
- WebSearch: "Algora bounties how much money developers earn open source bounty payouts"; "Hacker News open source bounties don't work maintainers experience"; "repository policy 'no AI-generated' pull requests ban CONTRIBUTING 2026 maintainers"; "reddit bounty hunting open source 'waste of time' competition PR rejected not paid"; "Upwork 2026 developers 'race to the bottom' AI agents flooding proposals freelance market saturated"; "maintainer 'we posted a bounty' nobody solved it…"; "Opire OR Polar bounty platform fee percentage pricing 2026"; "'Algora' 2026 bounties board declining pivot recruiting".
- HN Algolia API: full comment trees for items 48164229 ("I tried to make Claude make me money on open-source bounties") and 37541994 ("Bounties Damage Open Source Projects", 105 comments); comment search for "algora bounty" (30 hits); story search for "Freelancer Seeking freelancer"; full item trees for the Aug/Jul/Jun 2026 freelancer threads with a script classifying top-level posts as SEEKING WORK vs SEEKING FREELANCER.
- GitHub REST API (read-only, `gh api`): comment counts and `/attempt`-matching comment counts for `tscircuit/dsn-converter#54`, `tscircuit/schematic-trace-solver#29`, `rohitdash08/FinMind#121`.
- dev.to public API: `body_markdown` for both of that author's bounty-hunting articles.
- Direct fetch: raw `POST.md` from `iotqowrop/algora-scout2`.
- WebFetch: godotengine.org contribution policy; daniel.haxx.se "high quality chaos"; opire.dev/home; algora.io homepage; gigs.sh/p/algora; blog.jakelee.co.uk BountyHour post-mortem.
- Probed `api.algora.io`, `console.algora.io/api/bounties`, and `algora.io/api/trpc/bounty.list` for a live open-bounty count.

**Most useful sources:** the `algora-scout2` POST.md (a direct, honest, negative replication of this precise workflow, with a data table); the live GitHub API verification of `/attempt` counts, which upgraded that writeup from anecdote to confirmed-and-worsening; the HN freelancer-thread supply/demand count (62:1), which independently kills the micro-gig half of the idea; and Godot's 2026 policy for the account-ban risk.

**Dead ends:** Reddit's public JSON search (`reddit.com` and `old.reddit.com`, several User-Agents) returned HTML instead of JSON — blocked — so no Reddit quotes are used and no Reddit member counts are asserted. `web.archive.org` was unreachable from this tool, so I could not do the intended pricing archaeology on Algora's historical homepage and fee page; the 23% figure therefore rests on an HN comment quoting the docs verbatim in 2023 plus a founder's "about 25%" corroboration in 2024, and is labeled historical rather than current. `docs.algora.io/bounties/payments` 301s to a 404. `algora.io/bounties` and `opire.dev/pricing` 404 via WebFetch (client-rendered). theregister.com and darkreading.com returned 404/403. The Algora tRPC endpoint returned an empty item list but I could not confirm the parameter shape, so I recorded it as inconclusive rather than as evidence. I hit a GitHub secondary rate limit partway through, which capped live bounty-pool sampling to the three issues above.

## Verification (2026-08-30, adversarial pass)
- Quotes: 22 checked, 21 verified, 0 unfetchable, 1 misattributed
- Claims:
  - **REFUTED — "Take rate against him: 23% on Algora (a $100 bounty nets $77)" / "$38.50 net on a $50 bounty".** Algora's own docs state the opposite: *"Contributors always get 100% of the bounty. Algora charges a % fee over your awarded bounty when you complete your payment."* The fee is charged to the **poster**, on top of the reward, not deducted from the solver. https://web.archive.org/web/2024/https://docs.algora.io/bounties/payments — the one commenter quote is verbatim but the dossier misreads its incidence. Affects three places: WTP table, Unit economics, Kill criterion 1.
  - **REFUTED — "~4% + Stripe 5.25% + $0.85 on Opire (a $100 bounty nets ~$89.90)."** Opire: *"Developers receive 100% of the bounty they earn, with no deductions or hidden fees taken from their payout. All associated fees are covered by the bounty creator"* and *"4% for bounties … on top of the bounty/tip amount."* A $100 Opire bounty nets the solver **$100**. https://opire.dev/home
  - **REFUTED (misattribution) — "Founder one commenter corroborates."** one commenter is not an Algora founder. That account's own 2025-04-10 HN comment tells a *different* user *"you should add a clear disclaimer that you are one of Algora's founders"*; the Show HN: Algora submitter is an Algora founder; that commenter's profile lists only a Twitter link. The 25% figure is a bystander's estimate, not founder corroboration. (source: the commenter's HN comment history, searched via the HN Algolia API for `query=algora&tags=comment` on 2026-08-30; the account handle is withheld here)
  - **REFUTED — "Earnings … are commingled with dev.to article revenue."** The 96-hour article separates them and says the opposite: *"the direct earnings from articles are minimal (Dev.to doesn't pay per view)."* Its table reports bounty earnings as a standalone `$500-800`. https://dev.to/api/articles/zeroknowledge0x/i-let-an-ai-agent-hunt-open-source-bounties-for-96-hours-heres-the-brutal-truth-about-what-42p3
  - **PARTLY — "204 other claimants on the same issue."** Re-ran the API: `tscircuit/dsn-converter#54` = 256 comments / 204 `/attempt` comments ✓, but only **105 distinct authors**. Saturation confirmed; the claimant count is ~2× overstated. Both tscircuit issues are also now **closed** and `#54` has had its bounty label removed. FinMind#121 open at 45 ✓.
  - **CONFIRMED — HN freelancer supply/demand.** Independently recounted all three threads: Aug 2026 15/15/0, Jul 2026 20/19/0, Jun 2026 31/28/1. Matches exactly. https://hn.algolia.com/api/v1/items/49157021
  - **CONFIRMED — Upwork/GigRadar figures** (7.21% vs 7.45%, 3,535 vs ~37,000, 832k→785k = 6%, Q1 2026 784k). https://gigradar.io/blog/upwork-market-report-2026
  - **CONFIRMED — Polar 5% + 50¢ / Early Member 4% + 40¢ for orgs created before May 27, 2026.** https://polar.sh/docs/merchant-of-record/fees
  - **CONFIRMED — Godot policy, the curl maintainer’s "avalanche" post, Prettier $22,500, Tenstorrent $200–$3,000, microG $10,000, omi $20,000, all six HN quotes, both dev.to articles, POST.md ($16 tokens/$16.88, "$506 run-rate").** Caveat on that post: it is about AI-assisted **security reports** to curl's bug-bounty program, not PRs on bounty-labeled issues — it is weaker support for "maintainers drowning in AI PRs" than the dossier implies.
  - **UNVERIFIABLE — "Ziverge $143K distributed" and "Twenty (YC S23, $2,500 bounty)."** Cited nowhere in the dossier and I could not source either; HN search for "143K"/"143,000" bounties returns 0 hits, and `algora.io/ziverge` and `/twentyhq` now serve the recruiting SPA shell rather than org bounty totals. Both are load-bearing for the WTP score of 4.
  - **UNVERIFIABLE — "37 of 120 surveyed projects ban AI code outright"** (Verdict). No source given anywhere in the dossier; no matching survey found.
- Score challenges:
  - **Reachability ×3: dossier 5 → 3.** The justification ("50 bounty-posting repos enumerable in about 10 minutes") does not survive execution. Full paginated scan of `label:"💎 Bounty" is:issue is:open` on 2026-08-30: **558 open issues across 71 repos, but 413 of 558 (74%) come from three documented honeypots** — `ClankerNation/OpenAgents` (201), `UnsafeLabs/Bounty-Hunters` (182), `SecureBananaLabs/bug-bounty` (30), all three named as scams by the dossier's own dev.to source. Strip obvious spam repos and 118 issues / 61 repos remain, of which the largest clusters are dead: `tscircuit/docs-old` is **archived** (last push 2025-01-22, no `$` labels) and `rohitdash08/FinMind` has not been pushed since **2026-02-21**. Enumerating 50 *qualified* buyers this way is not a ten-minute job. This is the criterion carrying 15 of the dossier's 45 points.
  - **WTP evidence ×2: dossier 4 → 3.** Half the exemplars in the justification (Ziverge $143K, Twenty $2,500) are uncited and unverifiable; the two that verify (Prettier, Tenstorrent) are, by the dossier's own admission in the same table, 2–3 month expert engagements outside this market.
  - **Risk ×2: dossier 2 → 1.** Counterparty risk is worse than described. `rohitdash08/FinMind` — the dossier's own sample repo — has **18 merged PRs against 290 closed-unmerged** (5.8% merge rate) and has been unmaintained for six months while still advertising $500/$250/$1k bounty labels that have accumulated 45/26/11 `/attempt` claims. That is a live, verifiable free-labor trap, stronger evidence than the secondhand "90% fake".
  - *(Note: the two fee corrections above cut in the dossier's disfavour on rigor but in the idea's favour on economics — the solver keeps 100% on both platforms. The verdict is unaffected; saturation, not take rate, is what kills it.)*
  - **Kill criteria — criterion 2 is measurable but not discriminating.** "≥ 3 distinct bounties where `/attempt` ≤ 3 and the repo has a verified history of merging external PRs" is satisfiable in ten minutes today by **14 issues on `tscircuit/docs-old`** — an archived repo whose issues carry no dollar label and have sat since 2024–2025. It needs a live dollar amount, a repo-activity/recency filter, and a definition of "verified history" (how many merges, in what window). Criterion 1's "≤ 8 total hours of his own review time" specifies no measurement method, and "net ≥ $150" is now ambiguous given contributors receive 100% on both platforms — net of what?
- Missing:
  - **The recommended pivot already has a free incumbent.** The dossier's closing "business hiding inside this dossier" — maintainers paying to triage AI-generated PRs — is CodeRabbit's existing product, and it is **free forever for public repositories** (*"install CodeRabbit on a public repository, and receive free reviews forever for public repositories"*; paid tiers $24–$48/mo/user). https://www.coderabbit.ai/pricing. The exact buyer named gets the exact product at $0.
  - **The evidence for that was in a document the dossier already read.** The 96-hour dev.to article — cited twice — describes its agent "*Monitors review feedback and responds to automated bots (CodeRabbit, Cubic)*" and "*Addressed automated reviews (CodeRabbit, Cubic, GitGuardian)*". Three AI review bots were already deployed on bounty repos in May 2026. The dossier's one constructive recommendation is aimed at a market its own source shows is contested.
  - **Single-source dependency not disclosed.** The dossier's spine is `iotqowrop/algora-scout2` POST.md, cited for quotes 6 and 7, the build estimate, the unit economics and the verdict. That repo has **0 stars, was created 2026-05-20 and last pushed nine minutes later**, is by an anonymous account, and its HN thread drew 37 points / 26 comments. Its own headline says "60 fresh issues" while its body says 80 — an internal inconsistency the dossier propagates without noting. Its conclusions replicated well against my independent checks, but the dossier presents an anonymous abandoned gist as settled fact.
  - **Not checked: whether any 2026 platform actually gates or de-duplicates attempts.** The whole saturation thesis assumes the `/attempt` free-for-all is permanent. Opire's assignment model, Algora's "Reserved for" labels and maintainer-assignment flow (visible in `archestra-ai/archestra#3859`) are mechanisms that could change the race dynamics; none were evaluated.
- Overall: **mostly-trustworthy** — every verbatim quote checked out and the two hardest original datasets (the 62:1 freelancer count and the `/attempt` saturation counts) reproduced exactly under independent re-execution, but the fee incidence is wrong on both platforms, a bystander was promoted to "founder" to prop up a pricing figure, two WTP exemplars and one verdict statistic have no source at all, the top-scoring criterion does not survive running its own command, and the recommended pivot has a free funded incumbent the dossier's own source names.

## Live sweep results (2026-08-30, 3 finders + 14 vetters, all read-only)

**Method.** Algora's public bounty index no longer exists (`algora.io/bounties` and `console.algora.io/bounties` → 404; the tRPC `bounty.list` endpoint returns `{"items":[]}`; the homepage now sells "open source tech recruiting"). The only working global index is GitHub search: `is:open is:issue commenter:algora-pbc[bot]` (401 results), the legacy `commenter:algora-pbc` user account (38), and self-applied `label:"💎 Bounty"` (241, mostly agent farms). Funding truth requires the org board (`algora.io/<org>/bounties`) **and** the issue still being open — boards are stale in both directions (tscircuit lists closed issues; daytonaio lists 16 bounties on a deleted repo). Replit Bounties is gone (301 → a Contra marketing page). Ubiquity's `Price: N USD` ecosystem rejects every outsider `/start` ("You must be a core team member"). `commenter:polar-sh[bot]` / IssueHunt / Opire bot queries return 0.

**Funnel.** 401 bot-commented open issues → 287 after dropping `💰 Rewarded` → 162 with amount ≥ $50 and not awarded → 32 in credible non-archived repos → ~12 with board-confirmed live funding → ~6 that fit Python/TypeScript. **Total realistically winnable, well-fit money: under $500.**

**Vetted (14 candidates, every one `skip`).** Highest expected value found: **$7 per principal-hour** (daydreamsai $1,000 — 246 PRs opened, 0 merged, crypto payout). Representative failures: warpspeed-bounties $750–960 (116 PRs, 0 ever merged, owner account created the day the bounties were posted); microG $14,999 RCS (maintainer applies an "AI slop" label to 77 PRs and states LLM code "must be presumed to be tainted"); coolify $1,000 (bounty expired; "Core Team Only"); gitea #4898 $300 (the finder's "0 attempts" was wrong — 9 claims, an active +1183-line PR the maintainer told everyone to rally behind, issue locked for `/attempt` spam); drizzle-orm set $360 ($200 withdrawn by its funder in 2025 — the pinned bot comment keeps the board rendering it; 19 open PRs implement the same one-condition fix for #1603, zero reviewed; the org has paid one external bounty ever, $40, to its own maintainer; thread comment 2026-08-25: "STOP SENDING SLOP GUYS … ALGORA DOESN'T EVEN DO BOUNTIES ANYMORE"); comet-ml/opik #1010 (bounty closed to new attempts 2026-02-20, a competing PR is CI-green awaiting approval); gyroflow #45 $500 (Rust, research-grade, blocked on two upstream repos).

**The four 60-second screens the vetters converged on** (run before reading any code): (1) fetch the board's `?status=completed` view — if lifetime payouts are ~$0 or only maintainers were paid, stop; (2) `gh api "search/issues?q=repo:OWNER/REPO+type:pr+<issue>"` — more than ~3 open attempts, walk away; (3) external-vs-core share of the last 30 merged PRs — under ~30% external, your PR is decoration; (4) grep the thread for the funder withdrawing the bounty or a maintainer announcing a rewrite of the subsystem.

**Conclusion.** The brief's instruction to "put the first three PR-ready bounties in ASKS.md" cannot be honestly satisfied today: there are no three bounties worth building. The daily-sweep harness (`q.sh`, `d.sh`, `qs.sh` and the query list in the session scratchpad) is cheap to re-run weekly, so A1 survives only as a **weekly 10-minute screen with the four gates above**, not as an income line. Score unchanged (45/80 excl. fit); verdict unchanged: do not build.


## Final score (main agent, 2026-08-30)
- Fit with assets and strengths: **3/5** ×2 — Repo tooling and test discipline fit; but the channel is dead, so fit is moot.
- Reusable assets: X-Scraper durable job queue for the daily sweep; the gh-api harness written today.
- Subtotal as researched: 45/80 · after adversarial verification: **32/80** (reach 5→3, wtp 4→3, risk 2→1, ttfd 2→1)
- **Total: 38/90**
