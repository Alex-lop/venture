# Repo knowledge graph for coding agents (MCP server)

**Slug:** b4-repo-knowledge-graph-mcp  |  **Track:** B  |  **Researched:** 2026-08-30  |  **Status:** researched

## One-line pitch
Index a repo into a symbol/import/ownership/decision graph and expose it to Claude Code and Cursor so agents stop re-discovering the codebase every session — sold as a free single-repo CLI with a paid team-shared index and guardrail policies.

## Specific buyer
**Title:** Staff/principal engineer or eng manager owning a >250k-LOC monorepo or a multi-repo microservice estate, at a 20-300 person software company where the team already pays for Claude Code Max or Cursor Business seats. Secondary buyer: platform/DevEx team lead with a tooling budget.

**Where they hang out online:**
- Hacker News (`news.ycombinator.com`) — this is the single dominant channel; every competitor in this space launched via Show HN or Launch HN (Graft 39 pts, Nia 131 pts, Hyper 79 pts).
- GitHub Trending / `r/ClaudeAI`, `r/cursor`, `r/LocalLLaMA` (Reddit blocked both `WebFetch` and public-JSON `curl` with HTTP 403 during this research — see Research log; Reddit presence is asserted secondhand by the Graft author, "got a lot of praise for it on reddit", HN id 49301741, and is NOT independently verified here).
- Cursor Community Forum (`forum.cursor.com`) — active bug-report subforum with monorepo indexing threads.
- `anthropics/claude-code` GitHub issue tracker.
- Discord: several competitors run their own (e.g. gortex, https://discord.gg/39MFHu3J5d).

**Offline / Boston (verifiable, principal can physically attend):**
- **AI Tinkerers Boston** — https://boston.aitinkerers.org/ ; part of a 253-city, 124,000+ member network; next listed event "Back from Summer: AI GTM Builders", 2026-09-03.
- **Boston AI Week 2026**, 2026-09-24 to 2026-10-02, https://aiweek.boston/schedule — advertised as 120+ AI events in Massachusetts.
- **AICamp Boston** — https://www.aicamp.ai/ ; sponsor page cites "8,000+ AI developers in Boston".
- **Boston Generative AI Meetup** — https://www.meetup.com/boston-generative-ai-meetup/ ; a core event of Boston AI Week.
- Northeastern's own Khoury co-op employer network (Alex is a Northeastern junior; co-op partner companies in Boston are the exact 20-300 person software shops described above).

## Pain evidence (verbatim, >= 5)

1. > "Hi HN I'm Tirth. I built code-review-graph because I got tired of watching Claude Code re-read my entire codebase on every single task."
   — Hacker News, https://news.ycombinator.com/item?id=47314091 , posted 2026-03-09. Written by an indie developer shipping their own OSS fix for the problem.

2. > "I kept hitting Claude Code's rate limits. The usual workaround is feeding file contents into the conversation to help the agent find what it needs — but you hit the ceiling faster, and the repo starts accumulating context files that exist purely to compensate for bad search."
   — Hacker News, https://news.ycombinator.com/item?id=47664736 , posted 2026-04-06. Author of "An experiment – replacing Claude Code's context-stuffing with semantic grep"; a working developer hitting paid-plan quota ceilings.

3. > "The context problem with coding agents is real. We've been coordinating multiple agents on builds - they often re-scan the same files or miss cross-file dependencies."
   — Hacker News, https://news.ycombinator.com/item?id=46195303 , posted 2025-12-08, in the Launch HN thread for Nia (YC S25). Written by a practitioner running multi-agent builds — i.e. exactly the "agent breaks what it didn't know about" failure.

4. > "This looks neat, we certainly need more ideas and solutions on this space, I work with large codebases daily and the limits on agentic contexts are constantly evident."
   — Hacker News, https://news.ycombinator.com/item?id=46195319 , posted 2025-12-08. Self-described daily large-codebase engineer; in the same thread they ask specifically how the index survives a large local refactor.

5. > "Coding agents kept reworking decisions we'd already settled - reviving an approach we ruled out in an ADR, redoing something a requirement already pinned. The context was in the repo; the agent had no current view of it."
   — Hacker News, https://news.ycombinator.com/item?id=48715032 , posted 2026-06-29. Author of "Lore", a team-decisions layer for coding agents; describes a team ("decisions we'd made"), not a solo dev.

6. > "My project is being developed in a monorepo environment exclusively for the frontend. When I open the workspace in Cursor, codebase indexing runs indefinitely, and the moment it finishes, it immediately starts again. Are you currently working on a solution to address this problem?"
   — Cursor Community Forum, a user, https://forum.cursor.com/t/when-using-cursor-in-a-monorepo-codebase-indexing-goes-into-an-infinite-loop/71739 , posted 2025-03-28. Frontend monorepo developer; thread auto-closed 2025-04-27 with **no fix from Cursor**.

7. > "In large codebase, the best code is the one that matches the codebase own voice and conventions, because that's the mental model of the team. Ingesting a full codebase explicit/implict patterns in an agent windows to make them match the codebase doesnt work: too much context, hallucinations, ..."
   — Hacker News, https://news.ycombinator.com/item?id=49154714 , posted 2026-08-03, "Show HN: Argot, a Rust AI guardrail based on your codebase AST patterns". The author shipped that fix as free open source.

8. > "biggest limitation is that it doesn't have workspaces where you can get context from several repos for building your application."
   — Hacker News, https://news.ycombinator.com/item?id=44945939 , posted 2025-08-18. Enterprise-tool user (Warp.dev) describing the multi-repo context gap directly.

9. > "One concern I have is that right now each session gets fresh 'eyes' on the problem. Right now I find I get a lot of mileage out of a combination of long-running sessions and fresh ones. I worry with a single generated concept graph that gets only incremental refreshes will become stale slowly, and in subtle ways that are hard to detect."
   — Hacker News, https://news.ycombinator.com/item?id=49301360 , posted 2026-08-14, in the Graft Show HN. This is the *buyer objection* to the product, stated unprompted by a would-be user.

10. > "We've been building p0 because we kept hitting the same wall: AI coding tools are great at generating code from scratch, but can fall flat when shipping complex features into multi-repo codebases with real architecture, real standards, and real constrain[ts]"
    — Hacker News, https://news.ycombinator.com/item?id=47247672 , posted 2026-03-04. Founder of a startup built entirely on this pain.

### Two quotes that specifically damage the *MCP* framing in the brief
11. > ⚠️ VERIFIER: misattributed - "Same is true for any other cli tools, claude never actually uses them as it's trained to use grep. but for graft as we set the directive to use graft at the start of the session and before the turn, claude just knows graft exists"
    — the Graft author, Hacker News, https://news.ycombinator.com/item?id=49301695 , posted 2026-08-14. The same author shipped a whole Show HN titled "Claude Code kept ignoring our MCP tools, so we used hooks instead" (2026-08-12, https://news.ycombinator.com/item?id=49275395).

12. > "We do this because MCP is inherently unreliable -- you are at the whim of the calling agent to recognize the connection between the tool call description and the user's query. Hooks let you reliably run side effects as part of the lifecycle."
    — a Hyper (YC P26) cofounder, Hacker News, https://news.ycombinator.com/item?id=48403931 , posted 2026-06-04.

**Verdict on pain: overwhelming and daily.** This is one of the most validated pains on the whole idea list. That is precisely the problem — see below.

## Willingness-to-pay evidence (>= 3)

| Competitor / substitute | Pricing (exact, URL, date seen) | Who it serves | Gap vs. this idea |
|---|---|---|---|
| **Unblocked — Platform tier** | "$29/user/month (annual) or $35/user/month (monthly)"; feature bullet: "Connect context to Claude, Cursor, Copilot, and more (via MCP)". Code Review tier "$19/user/month (annual) or $23/user/month (monthly)". https://getunblocked.com/pricing/ , fetched 2026-08-30 | Dev teams wanting codebase + Slack + docs context piped to agents | **This is literally the paid product in the brief, already shipped and priced at $29/seat by a funded company.** They add Slack/Jira/Confluence history, which a repo-only graph cannot. |
| **Greptile — Pro** | "$30/seat/month", "50 credits included per seat", "$1 per additional credit", "1 credit = 1 standard review". Starter free for 1 active dev. https://www.greptile.com/pricing , fetched 2026-08-30 | Teams buying AI code review grounded in whole-repo context | Proves teams pay ~$30/seat for repo-context-derived *outcomes* (a review), not for the index itself. Greptile moved to per-review metering in Mar 2026 — evidence the flat seat model under-monetized. |
| **Sourcegraph** | ⚠️ VERIFIER: not_found - Enterprise Starter "$19 per user per month" (≤50 devs, ≤100 repos, 5GB); Amp Enterprise "$59 per user per month"; self-hosted enterprise deals reported "$50,000–$75,000/yr" minimum. https://sourcegraph.com/pricing , via search 2026-08-30 | Enterprise code search + agents | Sets the price ceiling ($19–59/seat) and shows the incumbent already owns the enterprise version of "who depends on X". |
| **Augment Code** | ⚠️ VERIFIER: not_found (Context Engine free-MCP/GA claim) - Cheapest plan "Business at $100/mo flat (up to 50 seats, with $100 of usage included)"; company reported "$252M in funding and $20M in revenue". Context Engine **unbundled as a free MCP server any coding agent can call, GA 2026-02-06** (https://www.augmentcode.com/context-engine , via search 2026-08-30) | Mid-market/enterprise eng orgs | A $252M-funded incumbent gave away the exact MCP context-engine wedge for free six months ago. |
| **Potpie** ("Context Graph for AI Native SDLC", 5,703 GitHub stars) | **No public price.** "Potpie's pricing model depends on a few factors specific to your team. Licenses are priced per user. There is a platform fee based on the number of users supported." https://potpie.ai/pricing , fetched 2026-08-30 | Teams | A 5.7k-star OSS repo-graph company that pulled self-serve pricing and went sales-led — a negative signal for $15/seat PLG in this category. |
| **codegraph (colbymchenry)** — the market leader | **$0. MIT license, 100% local, 68,633 stars** (created 2026-01-18; `gh api repos/colbymchenry/codegraph`, 2026-08-30). Hosted product is a *waitlist with no published price*: "The CodeGraph platform is coming... Get early beta access · getcodegraph.com" | Every Claude Code / Cursor / Codex / Copilot user | **The direct competitor's free tier is 68k stars and its paid tier does not exist yet.** |
| **codebase-memory-mcp (DeusData)** | **$0. MIT, 41,169 stars**, no paid tier, no hosted service: "All processing happens 100% locally; your code never leaves your machine." Claims "~3,400 tokens ... versus ~412,000 tokens via file-by-file grep exploration—a 99.2% reduction." https://github.com/DeusData/codebase-memory-mcp , fetched 2026-08-30 | Same buyer | Free, single static binary, 158 languages, zero deps. |

**Manual cost being paid today (computed).** The wasted resource is model tokens and engineer wall-clock, not salary hours for a manual task. Two independent measured claims: codegraph's benchmark, "62% fewer tokens · 44% cheaper" median across seven repos (README, fetched 2026-08-30); Graft's headline, "cut grep tokens by 42%" (HN 49299985, 2026-08-14). A dev on a $200/mo Claude Max plan who is quota-limited (see complaint #2) is therefore losing on the order of $40–90/mo of usable capacity, plus latency. Fully-loaded US senior SWE at ~$180k ≈ $86/hr; two hours/week lost to agent re-discovery and rework ≈ **$745/dev/month** of theoretical value. **But that entire $745 is already recoverable for $0** by installing a 68k-star MIT binary — which is why the price of this capability has collapsed to zero.

## Reachability (50 qualified buyers in 30 days, $0)

Reaching 50 *users* is easy; reaching 50 *qualified buyers* (someone with a seat budget) is not. Channels with evidence of buyer presence:

- **Hacker News Show HN / Launch HN.** Every player here used it. Evidence of buyer presence in-thread: Graft's Show HN drew 44 comments including two enterprise-shaped questions ("How mergeable is it?", "what about java projects?"). *Realistic outcome for a new entrant in Aug 2026: Graft's earlier attempts got 6 pts (2026-07-30) and 3 pts (2026-08-06) before the fourth post hit 39.* Expect ~3 attempts for one hit.
- **GitHub Trending.** A secondary source states "three independent implementations appeared on GitHub Trending in the same week" (https://agentconn.com/blog/codegraph-pre-indexed-knowledge-graph-multi-agent-claude-code-codex-2026/). Star velocity is achievable — Graft went 0→5,115 stars in ~4 weeks — but stars are not buyers.
- **Cursor Community Forum.** Confirmed live monorepo-indexing bug threads with no vendor fix (evidence #6). Read-only mining is fine; posting would violate the no-outreach rule until the principal chooses to.
- **`anthropics/claude-code` issues.** (GitHub search API returned secondary-rate-limit errors during this session; not verified.)
- **Boston, in person, $0:** AI Tinkerers Boston (event 2026-09-03), Boston AI Week 2026-09-24→10-02 with 120+ events, AICamp Boston (8,000+ AI devs claimed), Boston Generative AI Meetup, DevFest Boston. A junior at Northeastern can walk into all of these and demo a laptop. This is the one channel where Alex has a genuine, non-commoditized edge: **face-to-face with a Boston eng lead, watching their own monorepo get indexed live.** Realistic: 4 events × ~10 real conversations = 40 conversations in 30 days; maybe 8-12 are qualified buyers.

**Honest read: 50 qualified buyers in 30 days at $0 is achievable on volume but the conversion is the problem, not the reach.** Every one of those 50 can install a free 68k-star alternative in the same conversation.

## Wedge
The smallest thing one buyer would pay for *this month* is **not the graph**. The graph is free.

The narrowest defensible wedge from the evidence: **a Claude Code / Codex hook that enforces a written policy about what agents may touch, and produces an audit trail of what agents read and changed** — installed on a team's repo, priced per repo not per seat. Rationale: (a) two independent founders (Graft, Hyper) state on the record that MCP tools get ignored and hooks are the only reliable surface; (b) the free 41k-star leader explicitly has **no** access controls, policy enforcement, or guardrail mechanisms; (c) the buyer for guardrails is a manager/compliance owner with budget, not a developer with a `brew install`.

Caveat, stated plainly: even this wedge has prior art (Cranot/roam-code, 510 stars, "change-safety gates, audit evidence"; GlitterKill/sdl-mcp, 467 stars, "policy-centered context budget layer"; Brain0, 340 stars, "DLP audit of what agents read"), and the one pure-play Show HN for it (Vectimus, Cedar policy enforcement for AI coding agents, 2026-03-26) got **3 points and 2 comments** — https://news.ycombinator.com/item?id=47525283 . The guardrail buyer exists but does not read Hacker News.

## Build estimate
**Agent-days to a sellable MVP: 8-12.** Components:
- Tree-sitter parse → symbol/import/call graph → SQLite (well-trodden; ~2 days with an agent).
- Claude Code `SessionStart` / `PreToolUse` / `PostToolUse` hook harness + Codex equivalent (~1 day).
- Incremental re-index on file change + git-pull sync (the hard part; staleness is the #1 stated objection — evidence #9) (~2-3 days).
- Policy file (`.agentpolicy`) + deny/allow enforcement + audit log (~2 days).
- Hosted team index: auth, per-repo storage, seat billing via Stripe (~3 days).
- Benchmark harness that is *actually reproducible* (see Notable findings — the Graft thread shows unreproducible benchmarks get publicly dismantled) (~1-2 days).

**Reusable assets: Graft as a pinned dependency (not a fork); Graphene policy validator for guardrail rules.**

The build is not the risk. Nothing here is hard. Being the 25th entrant is the risk.

## Unit economics
- **Price:** $15/seat/month (brief's number) or $49/repo/month for the policy+audit wedge.
- **Model/API cost:** Near zero if the design is deterministic (tree-sitter + SQLite, no embeddings) — this is what the free leaders do ("zero API keys", roam-code). If embeddings are used: a 500k-LOC repo ≈ ~25M tokens ≈ $0.65 one-time at $0.026/M for a small embedding model, plus ~5% re-embed/month ≈ **$0.10-1.00/repo/month**. Assumption: embeddings only, no generation in the hot path.
- **Hosting:** A team-shared index for 20 repos fits in a $5/mo Hetzner/Fly box + $0 SQLite/Litestream to R2. **Under the $40/mo burn ceiling comfortably** — this idea passes the capital constraint easily.
- **Gross margin:** ~95%+. Margin is not the problem.
- **Break-even on burn:** 3 seats at $15. The economics are fine; the demand at any price above $0 is what is unproven.

## Risks
- **Commoditization (fatal, and already realized).** Verified star counts as of 2026-08-30 via `gh api`: colbymchenry/codegraph **68,633**; DeusData/codebase-memory-mcp **41,169**; oraios/serena **28,631**; zilliztech/claude-context **12,455**; potpie-ai/potpie **5,703**; NanoNets/Graft **5,115** (created ~2026-07); vitali87/code-graph-rag **4,848**; plus zzet/gortex 1,504; harshkedia177/axon 807; CodeBendKit/codeseek 765; aovestdipaperino/tokensave 604; 0xK3vin/MegaMemory 513; Cranot/roam-code 510; ooples/token-optimizer-mcp 500; GlitterKill/sdl-mcp 467; syncable-dev/memtrace 467; Muvon/octocode 460 — **the overwhelming majority created in 2026, nearly all MIT and free.**
- **Incumbent response (already happened).** ⚠️ VERIFIER: not_found - Augment Code — $252M raised — unbundled its context engine as a free MCP server, GA 2026-02-06. Sourcegraph, Unblocked, Greptile, Potpie, Nia (YC S25, $6M raised), Hyper (YC P26), p0 all sell adjacent versions.
- **Platform dependency (high).** The product only works via Claude Code hooks / Cursor internals. Anthropic and Cursor can absorb this in a release. A commenter on the Nia launch put the risk exactly: > "I am not sure how you get traction without being 10x better than what Cursor can produce *tomorrow*. If you are successful the coding agents will copy your idea and then people being lazy and using what works have no inventive to switch." — https://news.ycombinator.com/item?id=46197185 , 2025-12-08.
- **Technical premise may be wrong.** A February 2026 Amazon Science paper is reported to find that "keyword search via agentic tool use achieves over 90% of RAG-level performance without a vector database, and for code specifically, exact-match search outperforms semantic retrieval on stable, well-named codebases" (via https://vadim.blog/claude-code-no-indexing/ , seen 2026-08-30 — secondary source, not the paper itself). If true, the ceiling on the value-add is thin.
- **Accuracy liability / staleness.** The single most-repeated buyer objection (evidence #9; also another commenter on the Hyper thread, 2026-06-25: "context that's right on Monday is quietly wrong by Friday, and nobody notices until a decision gets made on it"). A wrong "safe change set" is worse than no answer.
- **Distribution/trust risk specific to hooks.** Hyper installed hooks and was publicly called out: > "turns out that when you run the app it installs a hook to run every time you start a session, submit a prompt, or agent ends a turn on all your coding agents / platforms. Zero notice was given, pretty shady." — https://news.ycombinator.com/item?id=48390705 , 2026-06-03. The reliable surface is also the surface that burns trust if mishandled.
- **Legal:** Low. Reading a customer's own repo under their instruction; MIT-licensed tree-sitter grammars; no scraping. The real legal surface is a hosted index holding customer source — SOC2 pressure arrives at the first 50-person buyer (see the Terretta exchange on the Hyper thread, https://news.ycombinator.com/item?id=48398113 ).

## Kill criteria
Given the field, the bar must be brutal and early:
- **By 2026-10-15 (6 weeks):** if the free CLI does not reach **500 GitHub stars** and **25 unique installs from outside Alex's network**, stop. (Reference: Graft did 5,115 stars in ~4 weeks with a NanoNets-sized megaphone; a solo student clearing 10% of that is the minimum sign of pull.)
- **By 2026-11-15 (11 weeks):** if **3 paying teams** (any price ≥ $49/mo) have not converted, stop. Not 3 trials — 3 charged cards.
- **Pre-build gate, by 2026-09-15:** at Boston AI Tinkerers (2026-09-03) and Boston AI Week (09-24→10-02), if fewer than **5 of 20** eng leads asked "would you pay for a team-shared index with policy enforcement" say yes *and* name a budget owner, do not write the code at all. This gate costs ~6 hours and is the highest-value 6 hours in the plan.

## Incumbents and adjacent players
Free / open source (all verified via `gh api`, 2026-08-30 unless noted):
- **colbymchenry/codegraph** — 68,633★, MIT, local, "62% fewer tokens · 44% cheaper", hosted platform on waitlist. https://github.com/colbymchenry/codegraph
- **DeusData/codebase-memory-mcp** — 41,169★, MIT, 158 languages, single static binary, "99.2% reduction". https://github.com/DeusData/codebase-memory-mcp
- **oraios/serena** — 28,631★, "MCP toolkit ... semantic retrieval and editing". https://github.com/oraios/serena
- **zilliztech/claude-context** — 12,455★, semantic code search MCP. https://github.com/zilliztech/claude-context
- **potpie-ai/potpie** — 5,703★, "Context Graph for AI Native SDLC"; pricing now gated. https://github.com/potpie-ai/potpie
- **NanoNets/Graft** — 5,115★ in ~1 month; hooks-not-MCP; SWE-Bench claims publicly disputed on HN. https://github.com/NanoNets/Graft
- **vitali87/code-graph-rag** — 4,848★, "ultimate RAG for your monorepo". https://github.com/vitali87/code-graph-rag
- **zzet/gortex** — 1,504★, 257 languages, "cutting token usage up to 50x". https://github.com/zzet/gortex
- **harshkedia177/axon** — 807★. **CodeBendKit/codeseek** — 765★. **aovestdipaperino/tokensave** — 604★, "40+ tools, 30+ languages". **0xK3vin/MegaMemory** — 513★. **Cranot/roam-code** — 510★, *has change-safety gates + audit evidence*. **ooples/token-optimizer-mcp** — 500★. **GlitterKill/sdl-mcp** — 467★, *policy-centered context budget layer*. **syncable-dev/memtrace** — 467★. **Muvon/octocode** — 460★. **JudiniLabs/mcp-code-graph** — 402★. **Brain0-ai/brain0** — 340★, *audit of what agents read, provenance attestations*. **ozgurcd/gograph** — 212★. **qcri/codebadger** — 162★ (Joern CPGs).
- **Aider** (48,594★) ships a repo-map; **Continue** (35,696★) is a full OSS agent; **getzep/graphiti** (30,408★) is the general-purpose graph memory layer.
- **wrale/mcp-server-tree-sitter** — 310★ (named in the brief; effectively inactive relative to the field).

Commercial:
- **Unblocked** — $19–29/user/mo, MCP context for Claude/Cursor/Copilot. https://getunblocked.com/pricing/
- **Greptile** — $30/seat/mo + $1/review overage. https://www.greptile.com/pricing
- **Sourcegraph / Amp** — ⚠️ VERIFIER: not_found - $19/user/mo Enterprise Starter, $59/user/mo Amp Enterprise. https://sourcegraph.com/pricing
- **Augment Code** — ⚠️ VERIFIER: not_found - $100/mo Business floor; context engine unbundled free as MCP, GA 2026-02-06; $252M raised, ~$20M revenue. https://www.augmentcode.com/context-engine
- **Nia (YC S25)** — $6M raised, "context layer for AI coding agents". https://trynia.ai — Launch HN https://news.ycombinator.com/item?id=46194828
- **Hyper (YC P26)** — "company brain", hooks-based, Postgres graph. https://heyhyper.ai — Launch HN https://news.ycombinator.com/item?id=48387095
- **p0** — multi-repo feature shipping. https://news.ycombinator.com/item?id=47247672
- **Greplica** — "context layer ... architecture, decisions, nuances". https://news.ycombinator.com/item?id=48785488
- **Lore** — team decisions/ADRs served to agents. https://news.ycombinator.com/item?id=48715032
- **CodeRabbit**, **Bloop** (9,498★, code search), **Moderne**, **Glean** (enterprise KG), **Vectimus** (Cedar policy for agents; 3 HN pts), **Argot** (free AST guardrail), **CodeSee** — adjacent; CodeSee status not re-verified this session.

## Score

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Time to first dollar | ×3 | **2** | The category price is $0: the two leaders (68.6k and 41.2k★) are MIT and free, and the leader's own hosted paid tier is still an unpriced waitlist as of 2026-08-30 — nobody has demonstrated a first self-serve dollar for a repo graph. |
| Reachability by a student | ×3 | **3** | Channels are genuinely free and open (HN Show HN, GitHub Trending, plus verified Boston venues: AI Tinkerers 2026-09-03, Boston AI Week 2026-09-24→10-02, AICamp's claimed 8,000+ Boston AI devs), but the same feed is being flooded by 20+ 2026-vintage competitors and Graft needed four HN posts to land one. |
| Pain × frequency | ×2 | **5** | Daily, universal, and independently verified 12 ways — 68,633★ and 41,169★ on free fixes, four funded startups, and complaints #1-#10 all describing the same re-discovery tax. |
| WTP evidence | ×2 | **2** | Teams demonstrably pay $19-59/seat for *outcomes* built on repo context (Unblocked $29, Greptile $30, Amp $59) but the graph layer itself is priced at $0 by the top three OSS players and was given away free by a $252M-funded incumbent (Augment, 2026-02-06). |
| Fit with assets and strengths | ×2 | **4** | Deep agent-context expertise and a working read of Graft; but the free incumbents make it moot. |
| Compounding | ×2 | **2** | The index is per-repo and private, so there is no cross-customer data network effect; the asset a competitor cannot regenerate with tree-sitter in milliseconds is *decisions/ownership/policy history*, which is a small slice of the proposed product. |
| Risk (5 = low) | ×2 | **1** | Platform-dependent on Claude Code/Cursor hook APIs, the MCP surface is called unreliable on the record by two independent founders, incumbents already shipped the wedge free, and a Feb-2026 Amazon Science result reportedly says keyword search gets >90% of RAG performance on code. |
| Ceiling | ×1 | **4** | Real: Augment at ~$20M revenue and Sourcegraph's $50-75k/yr enterprise floor prove seat-based context tooling supports a large business — if you can hold a position. |
| Build cost (5 = cheap) | ×1 | **3** | An MVP is 8-12 agent-days of well-trodden tree-sitter + SQLite + hooks work, but reaching parity with a 68k-star, 158-language incumbent is not cheap. |

**Subtotal excluding Fit: 42 / 80.**  (6 + 9 + 10 + 4 + 4 + 2 + 4 + 3)
Total with Fit: 42 + (Fit × 2), max 90.

## Verdict
The pain is real, enormous, and daily — and that is exactly why this is a bad business for a solo student in August 2026. Between January and August 2026 the market answered this question in public: **colbymchenry/codegraph reached 68,633 stars and DeusData/codebase-memory-mcp reached 41,169 stars, both MIT, both free, both 100% local**, joined by at least eighteen other free implementations, four venture-funded startups (Nia $6M, Hyper, Potpie, p0), and a $252M-funded incumbent that unbundled its context engine as a *free* MCP server in February. The market leader with 68k stars has a hosted paid tier that is still a waitlist with no published price — meaning even the winner has not proven anyone will pay for this. The brief's specific framing is also wrong on the mechanics: the Graft and Hyper founders both state on the record that coding agents ignore MCP tools and hooks are the only reliable surface, so "MCP server" is the wrong noun. What survives is narrow: the *decisions, ownership and policy* layer — the part of a repo graph that tree-sitter cannot regenerate — sold to a manager who buys guardrails and audit trails, priced per repo, not to a developer who buys speed and can `brew install` a free competitor. But even that has 500-star prior art and its one pure-play Show HN drew 3 points. **Recommendation: do not build the product. Spend six hours instead on the pre-build gate at Boston AI Tinkerers on 2026-09-03 and Boston AI Week; if fewer than 5 of 20 eng leads name a budget owner for agent guardrails, kill it entirely and take the adjacent ideas below.** The one genuinely non-commoditized thing this research surfaced is that nobody in the field can produce a credible benchmark — that is a smaller, cheaper, and more defensible opening than the graph itself.

## Research log
**Time spent:** ~60 agent-minutes.

**Queries run (HN Algolia API, `hn.algolia.com/api/v1/search`):** "coding agent repo context"; "coding agent broke something it didn't know about"; "AI agent context window cost codebase"; "Claude Code doesn't understand my codebase"; "agent guardrails files should not touch"; "agent broke other code depends on"; "coding agent impact analysis dependencies"; "claude code token cost exploring repo"; "agents editing files they should not"; "AI agent changed a shared library other teams"; "codebase too large for agent context team"; "Graft Claude Code hooks"; "nanonets graft".

**Full HN threads pulled via `/api/v1/items/`:** 49299985 (Graft Show HN, 39pts/44c), 48387095 (Launch HN: Hyper, YC P26, 79pts), 46194828 (Launch HN: Nia, YC S25, 131pts), 47525283 (Vectimus, 3pts).

**GitHub (`gh api`, read-only):** direct `repos/{owner}/{name}` lookups for 21 repos; `search/repositories?q=code+graph+mcp+agent`. Star counts and creation dates in this dossier are from those calls on 2026-08-30.

**Pages fetched (WebFetch):** getunblocked.com/pricing, greptile.com/pricing, potpie.ai/pricing, github.com/colbymchenry/codegraph, github.com/DeusData/codebase-memory-mcp, forum.cursor.com/t/…/71739.

**Web searches:** Greptile pricing; Unblocked pricing; Augment Code context engine 2026; "code graph" MCP servers 2026; Cursor monorepo indexing complaints; Sourcegraph Amp pricing; OSS MCP monetization/MRR; Claude Code native indexing; Boston AI meetups.

**Dead ends and gaps (stated honestly):**
- **Reddit was completely inaccessible.** `www.reddit.com/…/search.json` and `api.reddit.com` returned **HTTP 403** under four different User-Agents, and WebFetch refused both `www.reddit.com` and `old.reddit.com` ("Claude Code is unable to fetch from…"). **No Reddit quote appears in this dossier**, so r/ClaudeAI and r/cursor sentiment is unverified here and should be re-checked before any decision that hinges on it.
- **GitHub search API hit a secondary rate limit** mid-session, so `anthropics/claude-code` issue mining did not complete.
- **trynia.ai/pricing returned HTTP 429**; Nia's exact seat price is not in this dossier.
- No G2/Capterra 2-3 star reviews were successfully pulled for the OSS players (they have none — that is itself the finding: the competition is free software, which has no review pages, only star counts).
- The Amazon Science "keyword search ≥90% of RAG" claim comes from a secondary blog summary, not the paper; flagged as such in Risks.

## Verification (2026-08-30, adversarial pass)
- **Quotes: 26 checked, 24 verified, 0 unfetchable, 2 not found/altered.** All 12 "Pain evidence" quotes reproduce **exactly** on the cited HN item IDs and the Cursor forum thread (checked via `hn.algolia.com/api/v1/items/` and `forum.cursor.com/t/...71739.json`), including authors and dates. The three Risks quotes also verify (46197185, 48390705, 48398113), as does the un-URL'd one commenter "right on Monday ... wrong by Friday" line (it is HN id **48669080**, 2026-06-25 — URL should be added). The two failures are both pricing/competitor cells, flagged in place: Sourcegraph's "$19 / $59 per user per month" and Augment's "Context Engine unbundled as a free MCP server, GA 2026-02-06".
- Claims:
  - **Star counts (all 21 repos) — CONFIRMED.** `gh api` re-run 2026-08-30: codegraph 68,634 (MIT, created 2026-01-18); codebase-memory-mcp 41,176 (MIT); serena 28,634; claude-context 12,455; potpie 5,703; Graft 5,116; code-graph-rag 4,848; gortex 1,505; roam-code 510; sdl-mcp 467; brain0 340; mcp-server-tree-sitter 310; aider 48,594; continue 35,696; graphiti 30,408. Descriptions quoted in the dossier are verbatim.
  - **"Graft went 0→5,115 stars in ~4 weeks" / "5,115★ in ~1 month" — REFUTED.** `NanoNets/Graft` was created **2026-07-03** (`gh api repos/NanoNets/Graft`), so 5,116 stars took **~8 weeks**, not 4. The 6-week / 500-star kill criterion is calibrated against a benchmark that is 2× too fast.
  - **"Expect ~3 attempts for one hit" (Graft's HN history) — CONFIRMED and then some.** Algolia shows **four** prior submissions of `github.com/NanoNets/Graft` before the 39-pt hit: 48658849 (2026-06-24, 2 pts), 49107075 (2026-07-30, 6 pts), 49197687 (2026-08-06, 3 pts), 49275395 (2026-08-12, 3 pts). The dossier's "6 pts / 3 pts" figures are exact.
  - **Unblocked $29/$35 and $19/$23, "Connect context to Claude, Cursor, Copilot, and more (via MCP)" — CONFIRMED.** https://getunblocked.com/pricing/
  - **Greptile $30/seat/mo, 50 credits/seat, $1/extra credit, "1 credit = 1 standard review", free Starter for 1 active dev — CONFIRMED.** https://www.greptile.com/pricing (the *added* claim that Greptile "moved to per-review metering in Mar 2026" is unverifiable — no dated source).
  - **Sourcegraph "$19 per user per month" Enterprise Starter and Amp Enterprise "$59 per user per month" — REFUTED.** https://sourcegraph.com/pricing today lists exactly one plan: "**Starting at $16K** — Includes credits for AI features; scales with team size · Contact sales". No per-seat tier exists. https://ampcode.com/pricing lists Megawatt **$20/month** and Gigawatt **$200/month** plus "Unconstrained" usage billing — no $59/user tier. The dossier's "$19–59/seat price ceiling" is therefore unsupported, and the real published enterprise floor is **higher**, not lower.
  - **Augment "Context Engine unbundled as a free MCP server any coding agent can call, GA 2026-02-06" — REFUTED by the dossier's own cited URL.** https://www.augmentcode.com/context-engine is a sales page ("Talk to our experts", "33% Lower Spend · 32% Fewer Tokens"); no free tier, no MCP server, no GA date anywhere on it. https://www.augmentcode.com/pricing lists "Context Engine" and "MCP & Native Tools" as **paid-plan features** of Business ($100/mo flat, up to 50 seats — this part CONFIRMED) and Enterprise. The changelog (Mar–Aug 2026) shows no such release. "$252M in funding and $20M in revenue" — unverifiable (no primary source reachable; web search budget exhausted).
  - **Potpie has no public price — CONFIRMED verbatim.** https://potpie.ai/pricing: "Potpie's pricing model depends on a few factors specific to your team. Licenses are priced per user. There is a platform fee based on the number of users supported."
  - **codegraph's hosted tier is still an unpriced waitlist — CONFIRMED.** https://getcodegraph.com renders only "Join the waitlist for early beta access"; README line 42/44 matches. README benchmark line is verbatim: "**88% fewer tool calls · 53% faster · 62% fewer tokens · 44% cheaper**".
  - **codebase-memory-mcp "~3,400 tokens vs ~412,000 ... 99.2% reduction" and "All processing happens 100% locally" — CONFIRMED verbatim** in README (lines 36, 290, 23).
  - **Amazon Science paper — PARTLY.** The paper is **real**: arXiv **2602.23368**, "Keyword search is all you need: Achieving RAG-Level Performance without vector databases using agentic tool use", Subramanian et al. (AWS). But it was **submitted 19 Dec 2025**, not "February 2026", and the dossier's second clause ("for code specifically, exact-match search outperforms semantic retrieval on stable, well-named codebases") is the **blogger's own extrapolation** — vadim.blog states plainly that "the benchmark focused on document Q&A rather than code navigation specifically". The dossier correctly flags the source as secondary; the date and the code-specific clause should be corrected. (Blog post is dated 2026-03-03.)
  - **Nia "$6M raised" — PARTLY.** The only source is an HN *commenter* saying "you have raised $6M" in the Launch HN (46194828, 131 pts / 87 comments — both confirmed). The founder never states a figure. He *does* answer the pricing gap the dossier left open: "Nia is a paid product but we have a free tier", plus "a self-serve paid plan for heavier individual use, and organization plans with higher limits, SOC 2, seat based billing".
  - **Boston venues — CONFIRMED with minor drift.** boston.aitinkerers.org: "Back from Summer: AI GTM Builders", **2026-09-03**, "part of a 253-city global network with **125,000+** members" (dossier says 124,000+). aiweek.boston/schedule: "September 16 – October 28, 2026" with "Core festival week · September 24 – October 2, 2026" and "**135 approved events**" (dossier says 120+). Both under-stated, not over-stated.
- Score challenges:
  - **WTP evidence: dossier 2 → verifier 3.** Two of the three facts holding this score down are wrong. Augment did **not** give the context engine away — it is a gated feature of a $100/mo-floor paid plan. Sourcegraph does not sell at $19/seat — it sells "MCP: Code graph knowledge for agents" and "Full MCP Server, API, and CLI access" as headline **enterprise** features starting at **$16K/yr**. Nia's founder confirms a self-serve paid plan and seat-based org billing. Corrected, the picture is "the graph layer is free at the bottom and expensive at the top, with nothing in the middle" — a positioning problem, not an absence of willingness to pay. The researcher over-weighted a free-unbundling event that did not happen.
  - **Reachability by a student: dossier 3 → verifier 2.** The dossier's own reference case is worse than reported: Graft needed **four** HN submissions over seven weeks, not three, and the payoff was 39 points. Meanwhile the category's actual HN ceiling is **445 points / 151 comments** (Semble, 2026-05-17) and belongs to an established ML lab with a pre-existing audience and its own embedding model — a solo student is competing for attention against that, not against 39-point posts. The Boston in-person channel is verified and genuinely differentiated, which is why this is a 2 and not a 1.
  - **Kill criteria — one of the three is unmeasurable.** "25 unique installs from outside Alex's network" has **no instrument**: a local-first MIT CLI cannot count installs without telemetry, and "100% local, no telemetry" is the exact positioning every competitor in the dossier's own list uses to win. Either the metric or the product promise has to go. The "500 stars in 6 weeks" bar is measurable but mis-calibrated (see the ~8-weeks correction above). The pre-build gate is the strongest of the three, but the one named September event is an **"AI GTM Builders"** (go-to-market) night — not an obvious place to find 20 engineering leads with tooling budget; the gate needs a different room.
- Missing:
  - **Claude Code already ships the free first-party substitute, and the dossier never mentions it.** `anthropics/claude-code` CHANGELOG **v2.0.74**: "Added LSP (Language Server Protocol) tool for code intelligence features like **go-to-definition, find references, and hover documentation**", extended by v2.1.162 to `workspaceSymbol` search, with LSP plugins, gitignore-aware `findReferences`, and diagnostics. The word "LSP" appears **zero times** in this dossier. "Anthropic and Cursor can absorb this in a release" is not a forward-looking risk — the symbol-graph half shipped, free, in-product, months ago.
  - **Users say the free substitute is sufficient.** On the Semble thread: "I just put something in my global CLAUDE.md (under ~/.Claude) asking it to use the LSP instead of grep and **have never had this issue since**" and "My q would have been this. Lsp solved this no?" (HN 48169874). That is a buyer, unprompted, describing a $0 zero-install fix.
  - **Semble is absent from the competitor list and is the biggest thing in the category.** `MinishLab/semble` — **5,968★**, MIT, created 2026-04-06, "Uses 99% fewer tokens than grep+read", static Model2Vec embeddings + BM25, no API keys. Its Show HN (48169874, 2026-05-17) did **445 points / 151 comments** — ~11× Graft's thread and larger than every thread the dossier cites combined. It also took **three** submissions to land (7 pts → 8 pts → 445 pts).
  - **A stronger objection than "MCP is unreliable": the models are RL'd on grep.** From the same thread, stated by a *user* rather than a competing founder: "models are **so heavily RL'd with grep that they do not trust results in other forms** and will continually retry or reread, and **all token savings are lost** because the model does not trust the results of the other tools." The Semble author confirms it varies by model ("Sonnet 4.6 seems to trust semble but Opus 4.7 less so"). This damages the dossier's *proposed hook wedge* too, not just the MCP framing — hooks can inject context but cannot stop the model re-grepping.
  - **The category's headline benchmark numbers are already publicly distrusted.** Multiple users on that thread describe RTK (a widely-installed free token-reduction CLI the dossier never mentions) as "over-reporting token savings", "always reports ~100% savings for me because rtk obviously doesn't know about the head/tail the agent pipes into", and "got stuck in a loop with a faulty RTK command". The dossier repeats 42% / 62% / 99.2% / 120× as evidence of value; buyers now discount those on sight. This *strengthens* the dossier's own closing insight (that credible benchmarking is the real opening) but it belongs in Risks, not the verdict's last line.
  - **The 68k-star leader is monetizing the dossier's own wedge.** getcodegraph.com, verbatim: "**change-impact intelligence for AI-written code** ... For every PR, know within seconds exactly **what to test, what could break, which flows are affected**, and whether business logic is compromised ... what it affects · what to test · what could break · **who signed off**". The proposed "policy + audit + change-safety" wedge is precisely what the free leader is building its paid tier on, with 68k stars of distribution already in place.
  - **Reddit remains unverified — independently reproduced.** `old.reddit.com/...search.json` and `www.reddit.com/...search.json` both returned non-JSON/blocked responses in this session under a browser UA. The "r/ClaudeAI, r/cursor, r/LocalLLaMA" line in *Where they hang out* still rests on one secondhand HN comment; the dossier is honest about this and the failure is not a strike.
- Overall: **mostly-trustworthy** — the quote hygiene is exceptional (24/26 verbatim-exact, including all 12 pain quotes and their authors and dates) and the central negative finding survives every check, but two of the four pillars of the verdict (Augment's "free unbundling" and a "$19–59/seat ceiling") are contradicted by the primary sources the dossier itself cites, and the single strongest kill-argument available in August 2026 — Claude Code's own free, shipped LSP tool, which users on HN say already solves this — is missing entirely.


## Final score (main agent, 2026-08-30)
- Fit with assets and strengths: **4/5** ×2 — Deep agent-context expertise and a working read of Graft; but the free incumbents make it moot.
- Reusable assets: Graft as a pinned dependency (not a fork); Graphene policy validator for guardrail rules.
- Subtotal as researched: 42/80 · after adversarial verification: **41/80** (wtp 2→3, reach 3→2)
- **Total: 49/90**
