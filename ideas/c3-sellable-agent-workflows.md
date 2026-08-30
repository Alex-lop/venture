# C3. Sellable agent workflows (Claude Code skills and agents)

**Slug:** c3-sellable-agent-workflows  |  **Track:** C  |  **Researched:** 2026-08-30  |  **Status:** researched

## One-line pitch
Package specific paid workflows (compliance evidence collection, dbt lineage audits, document intake) as installable Claude Code skills/plugins and sell them to teams already running Claude Code — a market that, on the evidence below, currently transacts in $2-$60 impulse tickets against an enormous free substitute pool.

## Specific buyer
Two distinct buyers, and the evidence says they behave very differently.

**Buyer A (the one the plan names): staff/senior engineer or eng manager at a 10-200 person software company already using Claude Code.**
- Online: r/ClaudeAI (1,043,382 members as of Aug 2026, growing ~2,425/day — [redditli.st](https://redditli.st/subreddit/ClaudeAI)), Hacker News (the "Ask HN: I still don't understand why AI agents need 'skills'" thread ran 17 pts / 18 comments on 2026-08-02), GitHub (this buyer stars skill repos by the hundred thousand — `nextlevelbuilder/ui-ux-pro-max-skill` at 123,039 stars, `hesreallyhim/awesome-claude-code` at 53,207), X/Twitter, and the Anthropic Discord.
- Offline (Boston): Meetup lists ODSC AI Boston, Boston Enterprise AI, New England Artificial Intelligence, Platform Engineers Boston, AI Security Engineers - Boston MA ([meetup.com search](https://www.meetup.com/find/?keywords=AI%20engineering&location=us--ma--Boston)) — but the listed events show 1-19 attendees each, so these are coffee-table sized, not lead firehoses. Boston tech employers within reach of Northeastern: HubSpot, Toast, Wayfair, Klaviyo, DraftKings (excluded on ethics grounds), CIC Cambridge tenants.
- **This buyer's dominant behavior is DIY.** See pain evidence #1, #3, #4.

**Buyer B (the one the evidence actually supports): a small consultancy / agency / fractional-CTO shop that resells implementation.**
- They buy time, not markdown. They hang out in the same places plus Ask HN: Freelancer? threads. This buyer will pay 3-4 figures for a delivered, installed, working workflow. There is no marketplace listing evidence for this buyer because the transaction is an invoice, not a checkout.

## Pain evidence (verbatim, >= 5)

1. > "I'd also go even further and say that you likely should never install ANY skill that you didn't create yourself (i mean, guided claude to create it for you works too), or "forked" an existing one and pulled only what you need. Everyone's workflow is different and nobody knows which workflow is the right one. If you turn your harness into a junk drawer of random skills that get auto updated, you introduce yet another layer of nondeterminism into it, and also blow up your context window. The only skill you should probably install instead of maintaining it yourself is playwright-cli, but that's pretty much it."
   — Hacker News, user `gck1`, comment on "Anatomy of the .claude/ folder", https://news.ycombinator.com/item?id=47545794, posted 2026-03-27. Practitioner-level Claude Code user. **This is the single most important quote in the dossier: it is the target buyer explaining, unprompted, why he will not buy your product.**

2. > "how much do you make selling skills on marketplace, just curious? It seems like it'd be impossible to vet a skill without reading it, so the entire concept mystifies me just a little bit."
   — Hacker News, user `kian`, https://news.ycombinator.com/item?id=49140987, posted 2026-08-02, in "Ask HN: I still don't understand why AI agents need 'skills'". Replying directly to a self-described skill seller. The vetting problem: a skill you can read is a skill you can copy; a skill you can't read is a skill you can't trust.

3. > "How do you sell them - do you give a preview or how else do you protect it from just being copy/pasted?"
   — Hacker News, user `kzzzznot`, https://news.ycombinator.com/item?id=49147258, posted 2026-08-02. **The seller never answered.** This is the DRM problem stated in one line: the product is a markdown file.

4. > ⚠️ VERIFIER: misattributed - "Skills are exactly that, well structured markdown documents." … "It is just marketing speak to evoke some similarity to Sci-fi movies show AI robots learning stuff by quickly going books. Nothing of the sort happens here though... So you are not missing anything. What you think is exactly what it is. Just some prefix for preloading the LLM context with.."
   — Hacker News, users `infotainment` (https://news.ycombinator.com/item?id=49139888) and `qsera` (https://news.ycombinator.com/item?id=49142248), both 2026-08-02, in "Ask HN: I still don't understand why AI agents need 'skills'" (https://news.ycombinator.com/item?id=49139845). Commoditization risk stated by the buyer population itself.

5. > "Usually only charge a few bucks because honestly, anyone can make them but those that buy get them because they don't want to spend the time on making them. You can sell them for $10 or $15, maybe more depending on the skill. Not always a lot but if you have a ton of them, you can make some serious cash."
   — Hacker News, user `getstowly` (a **seller** of skills), https://news.ycombinator.com/item?id=49141032, posted 2026-08-02. A practitioner's own price ceiling: $10-$15, "not always a lot", and the strategy is volume. He declined to name where he sells when asked (https://news.ycombinator.com/item?id=49141448).

6. > "Started building this after getting nervous about installing random SKILL.md files from GitHub. Scans for prompt injection in markdown/references and suspicious patterns in scripts/."
   — Hacker News, user `adamos486` describing Skulto in "Ask HN: What are you working on? (February 2026)", https://news.ycombinator.com/item?id=46940316, posted 2026-02-09. Independent developer. Third-party skills are a perceived attack surface, not a perceived convenience.

7. > "Cisco's AI security research team tested a third-party OpenClaw skill and found it performed data exfiltration and prompt injection without user awareness, noting that the skill repository lacked adequate vetting to prevent malicious submissions."
   — Hacker News, user `c22`, https://news.ycombinator.com/item?id=47083701, posted 2026-02-20, quoting Wikipedia's OpenClaw article. Corroborated by PromptArmor, "Hijacking Claude Code via Injected Marketplace Plugins" (https://promptarmor.substack.com/p/hijacking-claude-code-via-injected, 2025-10-16): *"A plugin can: (1) Bypass human-in-the-loop protections (2) Exfiltrate a user's files via indirect prompt injection"*. The category is being actively poisoned for an unknown solo seller.

8. > "I love vercel, but I think the 'collect a bunch of random skills' approach just isn't it. You need versioning, linking between skills, an easy install client...basically a full package manager, which this is not."
   — Hacker News, user `theahura`, https://news.ycombinator.com/item?id=46722059, posted 2026-01-22, on "Show HN: Agent Skills Leaderboard". Team lead who shipped a curated set. Real pain — but the pain is *curation and infrastructure*, and his answer was to give it away free at noriskillsets.dev.

9. **Demand-side pain that IS real (buyer B / enterprise):**
   > "Engineering managers invite their teammates and Promptster analyzes the engineers work with ai coding tools (claude code, codex, cursor, copilot). The manager receives a team-aggregate dashboard where they can roll-out certain practices / skill to their whole team."
   — Hacker News, user `Paarthmj`, https://news.ycombinator.com/item?id=48897402, posted 2026-07-13. A founder describing the actual budgeted problem: managers want to *roll out* standard practices across a team. Note that the money is going to a dashboard/SaaS, not to a skill pack.
   > "MintMCP helps enterprises safely roll out agents to the entire organization (e.g, governance around MCP tools and agents like Claude Code / Codex / Cowork)."
   — Hacker News, user `vrv`, Ask HN: Who is hiring? (May 2026), https://news.ycombinator.com/item?id=47982567, posted 2026-05-02. Funded startup hiring founding engineers for exactly this. The enterprise pain is **governance and safe rollout**, not "we need more skills."

## Willingness-to-pay evidence (>= 3)

I pulled the embedded product JSON (`ratings.count`, `price_cents`) from live Gumroad pages on 2026-08-30. Gumroad rating rates on digital products run roughly 2-10% of buyers, so ratings are a floor-indicator of sales, not a count — but a **0** is close to dispositive.

| Competitor / substitute | Pricing (exact, URL, date seen) | Who it serves | Gap vs. this idea |
|---|---|---|---|
| **Claude Code for Designers** (aidesignlab) | **$69.99**, **42 ratings, 4.9 avg** — https://aidesignlab.gumroad.com/l/claude-code-for-designers, seen 2026-08-30 | Designers learning to ship apps | The one product in this dataset with real traction is a **course**, not a skill pack. Education sells; markdown doesn't. |
| **MY PREMIUM CLAUDE SKILLS COLLECTION** (usamaakrm) | **$60.00**, **12 ratings, 5.0 avg** — https://usamaakrm.gumroad.com/l/premium-claude-skills, seen 2026-08-30 | Marketing/content generalists | Best-selling actual *skill pack* found. ~12 ratings ≈ maybe 120-600 lifetime sales ≈ $7k-$36k gross, over months. Not a technical buyer. |
| **Claude Skills Pack** (thinkaiprompt), 30 skills | **$39.00**, **5 ratings, 4.4 avg** — https://thinkaiprompt.gumroad.com/l/claude-skills, seen 2026-08-30 | Business generalists | Note the 4.4 avg — the lowest in the set. Pack buyers are the least satisfied. |
| **Master Marketing Skills Bundle — 167 Claude AI Skills** (inflectual) | **$167.00**, **0 ratings** — https://inflectual.gumroad.com/l/master-marketing-claude-skills-bundle, seen 2026-08-30 | Marketers | 167 skills, zero ratings. Bundle-size does not create willingness to pay. |
| **The Complete Claude Code Playbook** (getflowmate) | **$27.00**, **0 ratings** — https://getflowmate.gumroad.com/l/dxnjk, seen 2026-08-30 | Claude Code users | Top organic search result for "claude code skill" commerce. Zero ratings. |
| **Claude Code Skills 101** (youssefhosni) | **$20.00**, **0 ratings** — https://youssefhosni.gumroad.com/l/pdtedw, seen 2026-08-30 | Devs learning to build skills | Even the meta-product (teaching people to sell skills) shows no traction. |
| **Agensi** — curated SKILL.md marketplace | Skills **$5-$75** ($9.99 "Award Winning Design", $49 "Comp Planning"); **"Flat 30% platform fee on every sale"**, creators "Keep 70%". Homepage: **"4,500+ Skills · 5,500+ Users · 400+ Creators"** — https://www.agensi.io/ and https://www.agensi.io/skills, seen 2026-08-30 | Skill creators + AI-tool users | **More skills listed than users on the platform.** Individual paid skills show 1-3 reviews. This is a supply glut, not a market. 30% take rate on a $10 ticket = $7 to you. |
| **Ref** (paid MCP server, search-over-docs) | **$9/month for 1,000 credits**, $0.009/search, 200 free credits; ⚠️ VERIFIER: altered - *"hundreds of paying subscribers with continuing growth"* after 3 months — https://www.pulsemcp.com/posts/pricing-the-unknown-a-paid-mcp-server, published 2025-09-10 | Developers using coding agents | **The only credible paid-agent-artifact revenue I found.** It works because it is a *metered hosted service* with real marginal cost, not a file. This is the adjacent idea. |
| **Agent37** (hosted skills w/ paywall + entitlements) | "hosting starts at **$3.99/mo**", cloud "about **$4 a month**", $1 starter credit — https://www.agent37.com/blog/monetize-claude-code-skills, published 2025-12-26 | Skill creators who want DRM | Infrastructure for a market that hasn't shown up. Article cites **zero** actual sales figures or named sellers. |
| **Vanta** (the incumbent for "compliance evidence collection") | **$10,000-$50,000/year**; 50-200 employees on SOC 2 only ≈ **$15,000-$35,000 ACV**; 1-20 employees: $14,000 Essentials / $21,500 Plus / $23,000 Professional — https://costbench.com/software/compliance-management/vanta/ and https://soc2auditors.org/insights/vanta-pricing/, seen 2026-08-30 | Startups pursuing SOC 2 | **The budget for "compliance evidence collection" is five figures a year — and it goes to a platform with auditor relationships and a trust page, not to a $29 skill.** |
| **Claude Code plugin marketplaces (Anthropic's own channel)** | **$0.** No payment, billing, licensing, entitlement, or usage-tracking mechanism exists — marketplaces are git repos with a `.claude-plugin/marketplace.json`, installed via `/plugin marketplace add owner/repo` — https://code.claude.com/docs/en/plugin-marketplaces, seen 2026-08-30 | Everyone | **The native distribution channel is free by construction.** Any paywall you build is out-of-band and bypassable by anyone who has the files. |
| **Free substitutes** | $0 — `nextlevelbuilder/ui-ux-pro-max-skill` (123,039 stars, MIT, no FUNDING.yml), `hesreallyhim/awesome-claude-code` (53,207 stars, no FUNDING.yml), `JuliusBrussee/caveman` (101,791 stars, has `github: JuliusBrussee` sponsors), `affaan-m/ECC` (244,382 stars, sponsors + ecc.tools), `skillsgate` ("indexed 45k+ AI agent skills", https://github.com/skillsgate/skillsgate), Smithery (**17,446+ MCPs**, https://smithery.ai/, now "part of Arcade.dev") — all seen 2026-08-30 | Everyone | Two of the three most-starred skill repos in the ecosystem have **no funding file at all**. The free tier of this market has six-figure star counts and zero monetization. |

**Manual cost being paid today (for the wedge, not for the pack):** a US compliance/security analyst gathering SOC 2 evidence manually. Using a conservative $110,000 fully-loaded salary ÷ 2,080 h = **$53/hour**; a quarterly evidence pull across 15 systems is commonly a 20-40 hour job = **$1,060-$2,120 per cycle, $4,240-$8,480/year**. That is why Vanta can charge $15k-$35k. It is also why a *delivered, installed* evidence-collection workflow can be invoiced at $1,500 and look cheap — and why the same thing sold as a $29 download looks like a toy.

## Reachability (50 qualified buyers in 30 days, $0)

Reachable, yes. Reachable *as buyers*, much less clear.

- **r/ClaudeAI — 1,043,382 members (Aug 2026), +72,740 in 30 days** ([redditli.st](https://redditli.st/subreddit/ClaudeAI)). Enormous and free. Caveat: self-promotion rules make direct selling here a fast ban, and Reddit's JSON/search endpoints were fully blocked from this research environment (both `curl` and WebFetch returned 403/shell HTML), so I could **not** verify post-level demand signals there. Treat r/ClaudeAI as an unverified channel until Alex checks it manually.
- **GitHub, as the primary channel.** This is the one channel with hard evidence: a genuinely useful free skill repo reaches 50k-250k stars in this ecosystem (5 examples above, all created within the last 14 months). Publishing the workflow free, with a `.claude-plugin/marketplace.json` so it installs in one command, is the highest-leverage $0 distribution available and costs nothing but agent-hours.
- **Hacker News Show HN — with a strong warning.** I enumerated the skill-marketplace Show HNs of Feb-Apr 2026: Skly (1 pt, 1 comment, 2026-02-10), ClawsMarket (1 pt, 0 comments), Moltplace (1 pt, 0), ClawHQ (1 pt, 0), SkillSandbox (1 pt, 0), skillsgate (1 pt, 0), AgentLink (1 pt, 0), SkillFortify (2 pts, 0), Skillcop (2 pts, 0), Agensi (1 pt, 0, 2026-04-21). **Ten launches, a combined ~12 points and 1 comment.** HN is saturated on this category. A Show HN of a *specific working workflow with a before/after* still lands (Ask HN threads on skills get 17+ pts and real discussion); a Show HN of "a marketplace" is dead on arrival.
- **In person, Boston.** ODSC AI Boston, Boston Enterprise AI, New England Artificial Intelligence, Platform Engineers Boston, AI Security Engineers - Boston MA, Boston AI/ML/Computer Vision, Analytics.Club Boston ([meetup.com](https://www.meetup.com/find/?keywords=AI%20engineering&location=us--ma--Boston), seen 2026-08-30). Honest read: listed event attendance is **1-19 people**, so this is 5-15 real conversations per month, not 50. But they are the *right* 5-15 for buyer B, and Alex can physically attend. Add Northeastern's own co-op employer network (HubSpot, Toast, Wayfair, Klaviyo all take NEU co-ops) — a warm intro to an eng manager at a co-op employer is worth more than 10,000 Reddit impressions.
- **Verdict on reachability:** 50 people who will *look* in 30 days is easy via GitHub. 50 *qualified buyers* is not, because the qualification test ("will you pay for markdown you could generate yourself") fails for most of them.

## Wedge
**Not a pack. A paid install.**

Smallest thing one buyer pays for this month: pick **one** narrow, evidence-heavy workflow — SOC 2 evidence collection is the best of the three named, because the budget already exists ($15k-$35k/yr to Vanta) and the manual alternative costs $1,000-$2,000 a quarter. Then:

1. Build it as a private Claude Code plugin (skill + agent + scripts + a `marketplace.json` the buyer hosts in *their own* git org, per https://code.claude.com/docs/en/plugin-marketplaces).
2. Sell it to **one** Boston-area 20-80 person company as a **fixed-fee $1,000-$1,500 "installed and working in your repo" engagement**, not a download. The deliverable is a repo they own, a 30-minute handoff call, and 30 days of fixes.
3. Publish a stripped-down version free on GitHub as the lead magnet. The free repo is the marketing; the install is the revenue.

Why this ordering: every piece of evidence says the *artifact* is worth $10 and the *delivery* is worth $1,000. Selling the artifact makes 400 sales necessary; selling the delivery makes 1 sale sufficient.

## Build estimate
**2-4 agent-days to a sellable v1 of one workflow.** Components:
- One skill directory (SKILL.md + reference material — the DEV writeup's "the skill prompt is about 20% of the value, reference material is the other 80%" is directionally right and matches what the 42-rating course sells).
- 2-4 deterministic scripts the skill shells out to (evidence pull from GitHub/AWS/Okta APIs, output normalization, an evidence manifest).
- A `.claude-plugin/marketplace.json` + install README so `/plugin marketplace add` works in one command.
- A before/after artifact: the actual evidence bundle produced, with timings. This is the sales asset and it is the part most sellers skip.
- Gumroad or LemonSqueezy listing (30 min) *only* if pursuing the low-ticket path — note Agensi takes **30%**, Gumroad ~10%+$0.50, and neither prevents redistribution.

**Reusable assets: Graphene MCP server + policy files, Nemisis verification bundle, RegLineage egress firewall as sellable skills.**

## Unit economics

**Path 1 — low-ticket pack (the plan's version):**
- Price: $29 one-time.
- Platform fee: Gumroad ~10% + $0.50 → **$25.60 net**; on Agensi's flat 30% → **$20.30 net**.
- Model/API cost: **$0/user/month** — the buyer runs it on their own Claude Code subscription. This is the one genuinely good property of this business.
- Hosting: **$0** (Gumroad/GitHub free). Fits the <$40/mo burn cap with room to spare.
- Gross margin: **~88%** on Gumroad, ~70% on Agensi.
- **The problem is not margin, it is volume.** Evidence-anchored realistic outcome: the median Claude-skill Gumroad product in my sample has **0-5 ratings**. At a 5% rating rate that's 0-100 lifetime sales = **$0-$2,560 gross, spread over months**. To hit $500 MRR you need ~20 new sales *every month, forever*, against a free substitute pool with 500,000+ combined GitHub stars.

**Path 2 — the wedge (paid install):**
- Price: $1,250 fixed fee per engagement.
- Cost: ~8 of Alex's hours + ~$10-20 of API spend during build (well inside the $40/mo cap; Claude Code subscription is likely already sunk).
- Gross margin: **>95%**, and one sale ≈ 49 pack sales.
- Not recurring. Rated by the principal's own priority list this is #2 money (one-time revenue that funds #1) — which is exactly what the brief said C3 was for.

## Risks

- **Platform dependency — severe.** Anthropic's own distribution channel has **no payment mechanism at all** (https://code.claude.com/docs/en/plugin-marketplaces, seen 2026-08-30). Anthropic ships first-party skills and plugins continuously and for free; anything narrow and popular enough to sell is a candidate for absorption into the product. Smithery — 17,446+ MCP servers — was absorbed into Arcade.dev.
- **Zero enforceable DRM.** The product is markdown. `kzzzznot` asked a seller point-blank how he stops copy/paste (https://news.ycombinator.com/item?id=49147258, 2026-08-02) and **got no answer**. Agent37 exists ($3.99/mo hosting) precisely because this is unsolved, and its own marketing article cites no seller revenue.
- **Category is being poisoned by security incidents.** PromptArmor documented plugin-based file exfiltration and human-in-the-loop bypass (2025-10-16); Cisco found a third-party skill performing data exfiltration and prompt injection "without user awareness" (via https://news.ycombinator.com/item?id=47083701, 2026-02-20). An unknown solo seller asking a team to install executable content is on the wrong side of that trend, and it gets worse, not better.
- **Commoditization by the tool itself.** `gck1`: *"you likely should never install ANY skill that you didn't create yourself (i mean, guided claude to create it for you works too)"* — Claude Code will write the buyer's skill for free in 20 minutes. The buyer *is* the competitor.
- **Accuracy liability — real for compliance specifically.** A skill that produces SOC 2 evidence that an auditor later rejects is a client-facing failure. Mitigation: sell it as an evidence *collector and organizer* that a human signs off on, never as an assurance product; put that in writing in the engagement scope. Do not market it as "SOC 2 compliant" or imply auditor endorsement.
- **Legal — low.** Selling your own markdown and scripts is clean. Two things to keep clean: (a) don't repackage MIT/Apache repos' content into a paid bundle without honoring the license and attribution — several of the highest-star skill repos are MIT (`ui-ux-pro-max-skill`, `affaan-m/ECC`) and one is NOASSERTION (`caveman`, `awesome-claude-code`), meaning **no license granted at all**; (b) a compliance-workflow skill that touches a client's AWS/Okta/GitHub needs a scoped, read-only credential and a written data-handling note.
- **Marketplace risk is not incumbent response — it's incumbent irrelevance.** No incumbent will bother responding. Ten skill marketplaces launched on HN in ten weeks and collected ~12 points between them.

## Kill criteria
Sequenced, wedge-first. Each is a hard number and date.

1. **By 2026-09-30:** 10 substantive replies from Boston-area eng/compliance leads to a specific "I'll build and install your SOC 2 evidence-collection agent, fixed fee" offer (in-person at the 3 named meetups + NEU co-op network + warm intros). **<3 replies → kill the wedge, do not build the pack.**
2. **By 2026-10-31:** **1 paying customer at >= $750** for a delivered install. **0 → kill C3 entirely and move the hours to a Track A idea.**
3. **Free-repo distribution check, by 2026-10-31:** the free version of the workflow on GitHub reaches **250 stars** (against an ecosystem where useful skills reach 50,000+). **<50 stars → the workflow isn't interesting enough to anyone, kill.**
4. **Only if 1-3 pass, then test the pack. By 2026-11-30:** **15 paid downloads at $29** (~$385 net). **<5 → confirm the low-ticket path is dead and never revisit it; keep the services line only.**
5. **Standing kill:** if at any point Anthropic ships a first-party paid-plugin/entitlement mechanism, re-open; if Anthropic ships a first-party version of the chosen workflow, kill that workflow same week.

## Incumbents and adjacent players
- **Anthropic Claude Code plugin marketplaces** — git-repo + JSON catalog, no payments, no licensing. https://code.claude.com/docs/en/plugin-marketplaces
- **Agensi** — curated SKILL.md marketplace, 30% flat fee, "4,500+ Skills · 5,500+ Users · 400+ Creators", skills $5-$75, 1-3 reviews each. https://www.agensi.io/
- **Skly** — "marketplace where you can buy and sell skills for AI agents", Show HN 2026-02-10, 1 point, 1 comment. https://skly.ai
- **Agent37** — hosted skill runtime with paywalls/entitlements, hosting from $3.99/mo; also the loudest content marketer in the category. https://www.agent37.com/
- **skillsgate** — "indexed 45k+ AI agent skills into an open source marketplace", free. https://github.com/skillsgate/skillsgate
- **MCP Market** — agent skills directory for Claude/ChatGPT/Codex. https://mcpmarket.com/tools/skills
- **agentskill.club** — "Free Agent Skills Library". https://www.agentskill.club/
- **claudeskillsmarket.com** — marketplace. https://www.claudeskillsmarket.com/
- **noriskillsets.dev** — hand-battle-tested curated skill set, free (via https://news.ycombinator.com/item?id=46722059)
- **aitmpl.com** — Claude Code plugins/marketplace collections directory, free. https://www.aitmpl.com/plugins/
- **GTM Agents** — 67-plugin Claude Code marketplace for revenue teams, open. https://github.com/gtmagents/gtm-agents
- **Smithery** — 17,446+ MCP servers; now "part of Arcade.dev". https://smithery.ai/
- **Ref** — paid MCP server, $9/mo, hundreds of paying subscribers. https://ref.tools (via https://www.pulsemcp.com/posts/pricing-the-unknown-a-paid-mcp-server)
- **PulseMCP** — MCP directory + the best writing on MCP pricing. https://www.pulsemcp.com/
- **MintMCP** — enterprise MCP gateway / safe agent rollout, VC-backed, hiring. (via https://news.ycombinator.com/item?id=47982567)
- **Promptster** — team AI-fluency dashboard, managers roll skills out to teams. https://www.promptster.ai
- **Skulto** — offline-first package manager for agent skills with injection scanning. https://github.com/asteroid-belt/skulto
- **Skillcop / SkillFortify / AgentGuard / skill-security-scan** — skill security scanners, all free/OSS. https://github.com/cfitzgerald-pd/skillcop, https://github.com/varun369/skillfortify
- **Vanta / Drata / Comp AI** — the actual incumbents for "compliance evidence collection", $10k-$80k/yr. https://costbench.com/software/compliance-management/vanta/, https://www.trycomp.ai/vanta-pricing
- **Gumroad / LemonSqueezy** — the actual checkout most sellers use; ~10% + $0.50.
- **Top free substitutes** (all seen 2026-08-30): affaan-m/ECC 244,382★; multica-ai/andrej-karpathy-skills 208,734★; nextlevelbuilder/ui-ux-pro-max-skill 123,039★; JuliusBrussee/caveman 101,791★; thedotmack/claude-mem 92,606★; hesreallyhim/awesome-claude-code 53,207★.

## Score

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Time to first dollar | x3 | **4** | A Gumroad listing can be live in a day and multiple $19-$60 Claude-skill products show non-zero ratings (2, 3, 5, 12, 42), so a first dollar in ~2 weeks is realistic; the wedge (a $1,250 install) plausibly closes inside 60 days given the local meetup and co-op networks. |
| Reachability by a student | x3 | **3** | The audience is trivially findable and huge (r/ClaudeAI 1,043,382 members; skill repos hitting 123k stars), but HN is saturated (10 skill-marketplace Show HNs → ~12 points total), Reddit self-promo is bannable, Boston meetups show 1-19 attendees, and I could not verify Reddit demand at all because Reddit was blocked from this environment. |
| Pain x frequency | x2 | **2** | Nobody is complaining that they lack skills — they are complaining that they can't trust the ones that exist (`gck1`: *"never install ANY skill that you didn't create yourself"*; Cisco/PromptArmor exfiltration findings), and the buyer's default fix is to have Claude write one in 20 minutes. |
| Willingness-to-pay evidence | x2 | **2** | Real but tiny and mostly non-technical: the best-selling actual skill pack found has 12 ratings at $60, three products have literally 0 ratings ($27, $20, $167), and the only high-traction product in the sample ($69.99, 42 ratings) is a **course**, not a workflow. |
| Fit with assets and strengths | ×2 | **4** | Packaging agent workflows is exactly what the principal does daily; the assets are the demo material. |
| Compounding | x2 | **2** | Audience and reputation compound a little, but the artifact does not: markdown is copyable with no DRM (a seller was asked how he prevents copy/paste and did not answer), the native channel is free git repos with no entitlement layer, and the two most-starred skill repos in the ecosystem have no funding file at all. |
| Risk (5 = low) | x2 | **2** | Total platform dependency on a vendor whose own distribution channel has zero payment mechanism and who ships competing first-party skills for free; plus an active security-incident narrative (PromptArmor 2025-10-16, Cisco via HN 2026-02-20) that specifically discredits installing a stranger's executable content. |
| Ceiling | x1 | **2** | Extrapolating the observed data — $10-$60 tickets, 0-12 ratings per pack, 30% platform take — the pack path tops out as side income; the services path has a higher per-sale ceiling but is capped hard by Alex's 12 hrs/week and is not recurring. |
| Build cost (5 = cheap) | x1 | **5** | A skill is markdown plus a few scripts plus a `marketplace.json`; $0 hosting, $0 per-user API cost (the buyer pays for their own inference), 2-4 agent-days — comfortably inside $1,000 capital and $40/mo burn. |

**Subtotal excluding Fit: 44 / 80.**
(4×3=12, 3×3=9, 2×2=4, 2×2=4, 2×2=4, 2×2=4, 2×1=2, 5×1=5)
**Total with Fit = 44 + (Fit × 2), max 90.**

## Verdict

Selling Claude Code skills as *products* is a market with real sellers, real listings, real infrastructure, and almost no real money — and the evidence for that is unusually clean. I pulled live sales-proxy data from eight Gumroad listings: three have **zero** ratings including a $167 bundle of 167 skills; the best-performing genuine skill pack has 12; the only product with meaningful traction is a $69.99 **course** about Claude Code, aimed at designers. The most credible seller I found describes his own ceiling as *"$10 or $15, maybe more"* and admits *"anyone can make them."* Agensi lists 4,500+ skills against 5,500 users — more inventory than customers — and takes 30%. Ten skill-marketplace Show HNs launched between Feb and Apr 2026 and collected roughly twelve points and one comment between them. Meanwhile Anthropic's own plugin marketplace spec contains no payment, licensing, or entitlement mechanism whatsoever, the free substitute pool has half a million GitHub stars, and the loudest voices in the buyer population are actively arguing that you should never install a skill you didn't write yourself — a position that security research (PromptArmor, Cisco) keeps validating. The product is a markdown file, the buyer's agent will write one for free, and there is no way to stop redistribution; a seller asked exactly that question on HN and received no answer.

That said, this idea should not be deleted — it should be **re-pointed**. The signal that *is* real is that the pain lives one layer up: managers want to roll standard practices out to a team (Promptster), enterprises want to adopt agents safely (MintMCP, funded and hiring), and the budget for something like "compliance evidence collection" is $15,000-$35,000 a year and currently goes to Vanta. Alex should not sell a $29 pack; he should sell **one installed workflow to one Boston company for $1,000-$1,500**, publish the stripped-down version free on GitHub as marketing, and treat the whole thing exactly as the brief framed it — a fast validation and cash line that funds a recurring product, not a recurring product itself. Under that framing it earns a slot as a **secondary, time-boxed track**: if the September/October kill gates in this dossier aren't cleared, the hours belong in Track A. Do not spend twelve weekly hours building a catalog of skills to list on a marketplace; the data says the catalog is where this idea goes to die quietly at 1 point and 0 comments.

## Research log

**Time spent:** ~70 agent-minutes.

**Queries run**
- WebSearch: paid Claude Code skills marketplace 2026; selling Claude Code plugins Gumroad revenue; gumroad.com/l claude code skill pack; site:reddit.com Claude Code skills "would pay"; Vanta pricing 2026 SOC 2; r/ClaudeAI subreddit members 2026; indie hacker MRR selling Claude Code skills. (WebSearch budget exhausted at 200 calls mid-session; final Boston-meetup check done via WebFetch instead.)
- HN Algolia API: `claude code skills marketplace`, `paid MCP server`, `prompt pack`, `sell skills`, `monetize skills`, `third-party skills security`, `skills slop`, `install random skill`, `claude code team rollout`, `agent workflows for our team`, `AI agent consulting rate`, `SEEKING FREELANCER claude code agent`, `marketplace AI agent skills`, `Show HN skills marketplace`, plus full-thread pulls on items 49139845, 49139979, 49104808, 46961475, 47545794, 46722059, 46541614, 46828302, 47982567, 48897402.
- GitHub REST API: repo search `claude+code+skills`, `claude+code+agents`, `claude+skills` sorted by stars; per-repo metadata and `.github/FUNDING.yml` checks on ECC, caveman, ui-ux-pro-max-skill, awesome-claude-code, claude-mem.
- Live scrape of embedded product JSON (`price_cents`, `ratings.count`) on 8 Gumroad Claude-skill listings.
- WebFetch: code.claude.com plugin-marketplaces docs; agensi.io home + /skills; smithery.ai + /pricing; agent37.com monetize article; pulsemcp.com paid-MCP pricing post; promptarmor.substack.com plugin hijacking; meetup.com Boston AI search.

**Most useful sources**
1. Gumroad embedded JSON — the single best evidence in the dossier. Ratings counts are unfakeable and they say 0-12 for skill packs.
2. https://code.claude.com/docs/en/plugin-marketplaces — settles the structural question: the native channel has no payment layer.
3. The Show HN graveyard of skill marketplaces (Feb-Apr 2026), all 0-2 points.
4. https://news.ycombinator.com/item?id=47545794 (`gck1`) — the buyer explaining why he won't buy.
5. https://www.pulsemcp.com/posts/pricing-the-unknown-a-paid-mcp-server — the one credible paid-agent-artifact revenue story, and it's a metered service.

**Dead ends**
- **Reddit was completely inaccessible** from this environment: `reddit.com/*.json` returned the HTML shell for every user-agent tried, `old.reddit.com` likewise, and WebFetch returned "unable to fetch from www.reddit.com". Subreddit size came from a third-party stats mirror (redditli.st). **No Reddit complaint quote in this dossier — that is a real gap and Alex should spend 20 minutes checking r/ClaudeAI and r/ClaudeCode manually before acting.**
- Gumroad's `/discover` search and `discover_search` endpoints are JS-rendered / 404 for anonymous requests; had to find product URLs via WebSearch then scrape individual pages.
- Smithery's pricing page returned only chrome (and revealed the Arcade.dev acquisition); no author-monetization details obtainable.
- SEO content farms (agent37.com, agensi.io/learn, claudeskillsmarket.com, agentskill.club) dominate every search for this topic and contain **zero** verifiable sales numbers. The volume of "how to monetize skills" content vastly exceeds the evidence that anyone is monetizing skills — itself a market signal.
- No public GitHub Sponsors dollar amounts are exposed via the REST API; I could only confirm presence/absence of `FUNDING.yml`.

## Verification (2026-08-30, adversarial pass)

- **Quotes: 17 checked, 15 verified, 0 unfetchable, 2 not found/altered.**
  - Verified verbatim against the HN Firebase API (`hacker-news.firebaseio.com/v0/item/<id>.json`), which returns raw comment text and Unix timestamps: `gck1` 47545794 (2026-03-27, story confirmed as "Anatomy of the .claude/ folder", id 47543139, 627 pts); `kian` 49140987; `kzzzznot` 49147258 (**no `kids` field — "the seller never answered" is confirmed structurally**); `qsera` 49142248; `getstowly` 49141032 (and 49141448 has no replies — "declined to name where he sells" confirmed); `adamos486` 46940316; `c22` 47083701; `theahura` 46722059 (story 46697908 "Show HN: Agent Skills Leaderboard" confirmed); `Paarthmj` 48897402; `vrv` 47982567 (story 47975571 "Ask HN: Who is hiring? (May 2026)" confirmed). All ten dates in the dossier match the epoch timestamps exactly.
  - PromptArmor quote and 2025-10-16 date: **verified** verbatim.
  - Agensi "Flat 30% platform fee on every sale" / "Keep 70%" / "4,500+ Skills · 5,500+ Users · 400+ Creators": **verified** verbatim.
  - Agent37 "$3.99/mo" / "about $4 a month" / "$1 starter credit", published 2025-12-26, zero named sellers or revenue figures: **verified**.
  - skillsgate "indexed 45k+ AI agent skills": **verified** (HN 47310285, Show HN title, 2026-03-09).
  - **FAILURE 1 — misattributed (pain evidence #4).** *"Skills are exactly that, well structured markdown documents."* is **not** `infotainment` at 49139888. It is **`getstowly` at 49139979**. `infotainment`'s actual words were *"'Well-organized markdown docs' are exactly what skills are."* This matters beyond attribution: `getstowly` is the **skill seller** from pain evidence #5, and in that same comment he continues *"I sell skills on marketplace because sometimes, crafting the perfect prompt can be hard... They're great."* The dossier presents the line as "commoditization risk stated by the buyer population itself"; the actual speaker was arguing the opposite. (Verified via HN Algolia: the phrase returns exactly 1 hit ecosystem-wide, objectID 49139979.)
  - **FAILURE 2 — altered (WTP table, Ref row).** The dossier presents *"hundreds of paying subscribers with continuing growth"* in quotes and italics. The source says: **"Ref has thousands of weekly users and hundreds of subscribers with more signing up and subscribing everyday."** Paraphrase presented as verbatim. The substance survives (and "thousands of weekly users" is a detail the dossier dropped that would have *helped* its argument).
  - Reddit inaccessibility independently reproduced: `reddit.com/r/ClaudeAI/about.json`, `old.reddit.com/.../about.json`, and `search.json` all returned the SPA shell under a descriptive User-Agent. The dossier's dead-end note is honest, not lazy.

- **Claims:**
  - **Gumroad prices + rating counts (all six) — CONFIRMED to the digit** by re-scraping embedded product JSON on 2026-08-30: $69.99/42/4.9; $60.00/12/5.0; $39.00/5/4.4; $167.00/0; $27.00/0; $20.00/0. This is the dossier's best evidence and it holds exactly. (URLs as cited in the WTP table.)
  - **GitHub star counts — CONFIRMED** (drift of 1–10 stars in six hours, i.e. live data): ECC 244,392; karpathy-skills 208,740; ui-ux-pro-max 123,045; caveman 101,795; claude-mem 92,606; awesome-claude-code 53,207. License claims also confirmed (MIT / MIT / MIT / NOASSERTION / Apache-2.0 / NOASSERTION). https://api.github.com/repos/affaan-m/ECC etc.
  - **FUNDING.yml claims — CONFIRMED exactly.** `ui-ux-pro-max-skill` and `awesome-claude-code` return 404 on `.github/FUNDING.yml`; `caveman` contains `github: JuliusBrussee`; `ECC` contains `github: affaan-m` + `custom: ['https://ecc.tools']`.
  - **"No payment mechanism in Claude Code plugin marketplaces" — CONFIRMED.** https://code.claude.com/docs/en/plugin-marketplaces. The only occurrence of "entitlement" is in a free-form `metadata` object described as *"Claude Code doesn't read it"* — which strengthens the dossier's point rather than weakening it.
  - **Ten marketplace Show HNs, ~12 points combined — CONFIRMED.** Skly 46961474 (1 pt/1c, 2026-02-10), ClawsMarket 46878646 (1/0), Moltplace 46902251 (1/0), ClawHQ 47024332 (1/0), SkillSandbox 47027734 (1/0), skillsgate 47310285 (1/0), AgentLink 46917375 (1/0), SkillFortify 47168723 (2/2), Skillcop 47457995 (2/0), Agensi 47846681 (1/0). (Dossier's research log cites Skly as 46961475; actual id is 46961474 — typo only.)
  - **Vanta pricing — PARTLY confirmed.** The 1–20 employee AWS Marketplace figures ($14,000 Essentials / $21,500 Plus / $23,000 Professional) are exact per https://soc2auditors.org/insights/vanta-pricing/. But that source explicitly states it has **no** 50–200 employee band, and https://costbench.com/software/compliance-management/vanta/ gives $10k–**$80k**/yr (not $10k–$50k as the WTP table says; the dossier's own incumbents list says $80k, so it contradicts itself) with "~$14,000/yr for 25–50 employees, SOC 2 only" and "~$30,000/yr for 100–200 employees, multiple frameworks". The dossier's headline "$15,000–$35,000 ACV for 50–200 on SOC 2 only" is an **interpolation, not a sourced figure**, and it is on the high side: costbench's own SOC-2-only datapoint is $14k.
  - **Ref pricing — CONFIRMED** ($9/mo for 1,000 credits, $0.009/search, 200 free credits, published 2025-09-10). Quote wording altered, see above.
  - **Smithery "17,446+ MCPs", now part of Arcade.dev — CONFIRMED** (homepage now reads "Browse 17,447+ MCPs"; banner: "Smithery is now a part of Arcade.dev").
  - **Agensi $5–$75 range — CONFIRMED** (catalog prices observed: 5, 7, 9.99, 10, 12, 15, 19, 75). **But see Missing** — the browse page's own facet count says "300 skills found", not 4,500+.
  - **Unit-economics arithmetic — CONFIRMED.** $110k/2,080 = $52.88; 20–40h × $53 = $1,060–$2,120; $29 − 10% − $0.50 = $25.60 (88.3% margin); $29 × 0.70 = $20.30; 15 × $25.60 = $384. Score subtotal 44/80 and the weighted line under it are both arithmetically correct.

- **Score challenges:**
  - **Time to first dollar: dossier 4 → verifier 3 (x3, −3 pts).** The 4 is scored against the pack path the dossier itself concludes is dead. Three of six sampled listings have literally **zero** lifetime ratings, so "a Gumroad listing live in a day" is a listing, not a dollar. The path the dossier actually recommends is a cold $1,250 fixed-fee consulting engagement sold by a student into 20–80-person companies via meetups with 1–19 listed attendees — that is a 60–120 day sales cycle, not two weeks. Scoring the easy-but-worthless path at the highest weight (x3) inflates the total by 3.
  - **Reachability: dossier 3 → verifier 4 (x3, +3 pts).** The dossier enumerated only *marketplace* Show HNs and concluded "HN is saturated on this category." Broader Algolia queries show HN in 2026 rewards **specific single skills** heavily: "Agent Skill to Force Docs in ASD-STE100" **363 pts / 122 comments** (2026-07-30, HN 49114639); "My Agent Skill for Test-Driven Development" **251 / 109** (2026-06-04, 48398925); "Show HN: Claude Code skills that build complete Godot games" **337 / 205** (2026-03-16, 47400868); "You're probably using Agent Skills wrong" **74 / 25**; "Agent skills that bring team coding standards to Claude Code and Codex" **75 / 38** (2026-08-04). The dossier anchored on a 17-point Ask HN when 250–360-point precedents exist for exactly the artifact it recommends building. That is a live, free, repeatable top-of-funnel, and it was under-weighted.
  - **Compounding: dossier 2 → verifier 3 (x2, +2 pts).** The dossier is right that the *artifact* doesn't compound. But it under-weights that the free-repo channel demonstrably does: five repos created inside 14 months at 92k–244k stars, and the dossier's own wedge plan uses the free repo as the lead magnet. Audience built this way is the input to every later idea, not just this one.
  - **Build cost: dossier 5 → verifier 4 (x1, −1 pt).** "2–4 agent-days, markdown plus a few scripts" prices the *pack*, not the thing being sold. The recommended deliverable reads live AWS, Okta and GitHub, normalizes output, emits an auditor-facing manifest, and carries 30 days of fixes plus a scoped-credential data-handling agreement. Dollar cost really is ~$0 (which is what the criterion mostly measures), so 4 not 3.
  - Pain × frequency (2), WTP (2), Risk (2), Ceiling (2): **no challenge** — verified evidence supports each, and the 2026 findings below make the pain and risk scores *more* defensible, not less.
  - **Net effect: +1 point (45/80 excluding Fit).** The individual scores move but the verdict does not, which is itself a point in the dossier's favour.
  - **Kill criteria — two are unmeasurable as written.**
    - #1: "10 substantive replies... **<3** → kill" leaves the **3–9 band with no defined action**, and "substantive" is undefined (is a "sounds interesting, send info" a substantive reply?). Same structural gap in #3: "250 stars... **<50** → kill" leaves **50–249 undefined**, and GitHub stars are trivially inflatable and a poor proxy for purchase intent in an ecosystem where the dossier's own comparables are 100k+.
    - #5 is not a kill criterion at all in its first half ("if Anthropic ships a paid-plugin mechanism, **re-open**"), and its second half — "if Anthropic ships a first-party version of the chosen workflow" — is undefined: would an Anthropic-published *example* skill count, or only a shipped product feature?
    - **Missing entirely: no gate tests the wedge's core assumption** — that a buyer will pay for SOC 2 evidence collection when Vanta, Drata and Comp AI already automate it. #1 measures replies to an offer; it does not measure whether the offer beats the incumbent. Suggested addition: *by 2026-09-30, 3 of 5 buyer conversations must state that their existing compliance tool does not already cover the workflow — otherwise the wedge is mis-aimed regardless of reply count.*
    - #2 and #4 are clean, hard, dated numbers. Credit where due.

- **Missing:**
  - **The biggest story in this category is absent from the dossier.** "Top downloaded skill in ClawHub contains malware" (1Password) — **334 points, 151 comments, 2026-02-05**, https://news.ycombinator.com/item?id=46898615 — plus "Malicious AI 'Skills' on OpenClaw's ClawHub Marketplace Bypass Scanners" (2026-06-24, 48662618) and trent.ai's analysis of **2,354 popular ClawHub skills** (2026-04-15, 47778839). The dossier's security thesis is correct but is built on a 2-point comment and a Substack post when a 334-point front-page story on exactly this exists.
  - **ClawHub (https://clawhub.ai/) is not in the incumbents list.** HN 46963691, 50 pts / 41 comments, 2026-02-10. By download volume it appears to be the largest skill marketplace in the evidence set and it is the one the malware research keeps targeting.
  - **Comp AI is fully open source and pulls SOC 2 evidence from 580+ integrations, with audit + pen test bundled** (https://www.trycomp.ai/vanta-pricing). This is the most serious analytical gap in the dossier. The wedge argument is "the budget exists ($15k–$35k/yr to Vanta), so a $1,250 install looks cheap." But a $1,250 one-time evidence collector is not competing with Vanta's price — it competes with a **free, open-source, 580-integration product that already does exactly that job**, and with the fact that a buyer already paying Vanta has *already bought* automated evidence collection. The dossier lists Comp AI in a single incumbents line without checking what it does.
  - **Tessl** (https://tessl.io/, Show HN 2026-02-05, 46900933) — "a package manager for agent skills with built-in evals," a funded company attacking precisely the curation/infrastructure pain the dossier identifies through `theahura`. Absent.
  - **Skrun** (https://github.com/skrun-dev/skrun, HN 47689319, **62 pts**, 2026-04-08) — "Deploy any agent skill as an API." This is the *exact* metered-hosted-service shape the dossier names as the only credible monetization path (via Ref), it already exists, and it is open source. That materially weakens "this is the adjacent idea."
  - **The free version of the re-pointed thesis already shipped.** "Agent skills that bring team coding standards to Claude Code and Codex" — 75 pts / 38 comments, 2026-08-04 (49169640) — is the manager-rollout pain the dossier pivots toward, served free.
  - **skills.sh (Vercel's Agent Skills Leaderboard)**, 135 pts / 44 comments, 2026-01-19, is cited only as the *thread* `theahura` commented in; it is never listed as the free substitute it is.
  - **Agensi's own catalog contradicts its marketing.** The browse page facet reads **"300 skills found"** / "Categories All 300" (https://www.agensi.io/skills, seen 2026-08-30) against the homepage's "4,500+ Skills." The dossier's "more skills listed than users" line rests on the marketing number. The real number is worse for Agensi but weaker as evidence for the dossier's specific claim.
  - **No treatment of Anthropic's Usage Policy / Commercial Terms** as they bear on reselling agent configurations, or on whether a client's own Claude Code seat permits a third party operating inside their repo. The Legal section covers OSS licensing and credential scoping only.
  - **Reddit remains a genuine hole** — independently reproduced as unfetchable, so not a strike, but the dossier's own recommendation (Alex spends 20 minutes on r/ClaudeAI and r/ClaudeCode manually) should be treated as a blocking prerequisite, not a footnote, since Reddit is the single largest claimed channel and carries a x3-weighted score.

- **Overall: mostly-trustworthy** — every checkable number in the dossier (six Gumroad price/rating pairs, six star counts, four FUNDING.yml checks, ten Show HN scores, Agensi/Smithery/Ref/Agent37/Vanta figures, and all the arithmetic) reproduced exactly or within live-data drift, and 15 of 17 quotes are verbatim with correct dates and attributions; the two defects are one paraphrase-as-quote and one misattribution that inverts the speaker's intent, and the two real analytical gaps are an under-weighted HN channel and an unchecked free open-source incumbent sitting directly on the recommended wedge.


## Final score (main agent, 2026-08-30)
- Fit with assets and strengths: **4/5** ×2 — Packaging agent workflows is exactly what the principal does daily; the assets are the demo material.
- Reusable assets: Graphene MCP server + policy files, Nemisis verification bundle, RegLineage egress firewall as sellable skills.
- Subtotal as researched: 44/80 · after adversarial verification: **45/80** (ttfd 4→3, reach 3→4, comp 2→3, build 5→4)
- **Total: 53/90**
