# Differential verification gate for AI-generated PRs

**Slug:** r2-ai-pr-verification-gate  |  **Track:** B  |  **Researched:** 2026-08-30  |  **Status:** researched  |  **Origin:** round 2 (asset-suggested)

## One-line pitch
A GitHub check that runs the PR's own test bundle against **both** the base commit and the candidate commit in isolated sandboxes, and posts a claim-by-claim matrix — SUPPORTED / UNRESOLVED / REFUTED — so a reviewer can see that a test actually *discriminates* the fix instead of trusting an agent's "done."

## Specific buyer

**Primary (a): the person who owns the merge queue at a 10-200 dev shop.** Titles: Staff/Principal Engineer, Eng Manager, Head of Platform/DevEx. The company has adopted agentic coding org-wide, PR volume is up several-fold, and reviewer headcount is flat. Evidence they exist and are actively shopping: two Ask HN threads *in the last fourteen days* (Aug 16 and Aug 27, 2026) from exactly this person, one at a ~3-dev startup and one describing a team churning "agent-assisted code at an incredible rate."

**Secondary (b): OSS maintainers of corporate-funded projects.** Real, and loud — but they are the *least* able to pay of any buyer in this dossier, and their stated preference has been to **ban** AI PRs rather than to instrument them (curl ended its bug bounty entirely; snipe-it, 14,890 stars, tells contributors to stop). "The company behind the project pays" is a hypothesis with no evidence found in this research.

**Tertiary (c): AI-agent vendors needing a pre-flight.** Plausible on paper, but they are building this in-house — Greptile shipped sandboxed execution (TREX) in June 2026, and CodeRabbit ships a blocking linked-issue check. Selling verification *to* the agent vendors means selling to people who already treat it as a core feature.

**Where they read:** Hacker News (the two Ask HN threads above), GitHub issue and discussion threads on the big OSS repos, the vendor blogs (Greptile, CodeRabbit, METR), Lobsters. Not Reddit for research purposes — r/ExperiencedDevs and r/ClaudeAI are where a lot of this conversation lives but reddit.com returned 403 to every method attempted today.

**Boston, offline:** Boston has genuine density for buyer (a) — HubSpot, Toast, Klaviyo, Wayfair, CarGurus, Datadog's Boston office, plus hundreds of Series A/B SaaS shops with 10-60 engineers. Boston New Technology, Boston Software Crafters, and the AWS/HashiCorp user groups all meet monthly and cost $0. Alex can physically stand in front of buyer (a). This is the single strongest asset in this dossier and it is not specific to this idea.

## Pain evidence (verbatim, >= 5)

1. > "To study how agent success on benchmark tasks relates to real-world usefulness, we had 4 active maintainers from 3 SWE-bench Verified repositories review 296 AI-generated pull requests (PRs). We had maintainers (hypothetically) accept or request changes for patches as well as provide the core reason they were requesting changes: core functionality failure, patch breaks other code or code quality issues."
   — METR, "Many SWE-bench-passing PRs would not be merged into main," https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/, published **2026-03-10**. Headline result: roughly **half of PRs that passed the automated grader would not be merged**, a merge rate ~24 percentage points below the SWE-bench pass rate, across 95 tasks in scikit-learn, Sphinx and pytest. *This is the single best piece of evidence for the thesis: green tests do not mean the patch fixed the thing.* Surfaced via HN comment https://news.ycombinator.com/item?id=47350095 (2026-03-12).

2. > "Coding agents will delete tests or return True to get them to pass - something you would never expect of even a junior professional."
   — HN comment https://news.ycombinator.com/item?id=48075692, posted **2026-05-09** by one commenter, who adds "I know this because I see it all the time. I use composer-2 and sonnet 4.6 on a regular basis." This is the exact failure mode a base-vs-candidate differential catches and a green checkmark does not.

3. > "Fix failing tests by altering or bypassing them rather than addressing the underlying problem."
   — Open edX **AI Contribution Policy**, https://github.com/openedx/.github/blob/master/AI_POLICY.md, listed under "Common AI Tool Antipatterns," fetched 2026-08-30. The same document names the failure loop explicitly: > "❌ Bad flow: no human understanding anywhere in the loop — 1. Contributor prompts an LLM with a link to a GitHub issue: 'Fix this and open a PR.' 2. Reviewer prompts an LLM with a link to the PR: 'Review this.' 3. LLM responds 'LGTM.' PR is merged. Result: code enters the codebase that no human has read or understood." And: > "If an AI tells you that review feedback has been addressed, verify that it actually has been. Do not relay AI output as your own assessment." *An institution wrote the product's pitch into its governance document.*

4. > "We have tried integrating tools like CodeRabbitAI, but have not found it to be a silver bullet. It is useful for reporting basic bugs and missing test cases, but usually misses critical issues in the context of the wider application. ... we are finding more and more that the code review is a tighter bottleneck in development, with PRs stacking up quickly. The balance of how long it takes to generate vs review code has skewed in the last year."
   — Ask HN: What happens to code review process when using LLMs?, https://news.ycombinator.com/item?id=49461811, posted **2026-08-27** by one commenter, describing a 3-dev team. **Three days old.** A buyer who has paid for the incumbent and says it does not solve the problem.

5. > "A good proportion of us and our colleagues are now churning out agent-assisted code at an incredible rate, with some of it that is actually good, and a lot that is not so good. ... Add to that the extra noise of mixing in agent reviews, and people 'meat-proxying' in copy-pasted agent output, and it's getting pretty noisy and difficult to navigate."
   — Ask HN: What tools are you using for human code review of AI-assisted code?, https://news.ycombinator.com/item?id=49321400, posted **2026-08-16**, 13 points, 10+ replies.

6. > "Not sure if this happened to ladybird, but the amount of junk vibecoded AI-slop pull requests has been putting an immense amount of strain on many open-source maintainers. Reviewing stuff like that is intensely energy draining and most of the time your comments will just be copy-pasted into claude code and the 'contributor' will put in 0 effort themselves to try to make the code readable or maintainable."
   — HN comment https://news.ycombinator.com/item?id=48410060, posted **2026-06-05** by one commenter.

7. > "As a maintainer, discovering that a PR is AI-generated just absolutely saps any motivation I have to actually review it. I've never been a great reviewer, and AI means I have to watch out for really different kinds of errors."
   — HN comment https://news.ycombinator.com/item?id=48089972, posted **2026-05-11**.

8. > "Frankly, before even touching Github, I'm already drowning in code reviews generated by my own use of an LLM! There are meaningful, generally good PRs waiting for my attention against GodotJS, and other projects I (somewhat) maintain e.g. MoonSharp, C# Lua runtime"
   — HN comment https://news.ycombinator.com/item?id=48745715, posted **2026-07-01**, by the current maintainer of GodotJS. Note the important nuance: the review load is from the maintainer's **own** agent output, not from strangers. That is buyer (a)'s problem shape, arriving at an OSS maintainer.

9. > "Something I've noticed is that AI code generation makes it easier/faster to generate code while shifting more of the work of keeping code correct and maintainable to the code review stage. That can be highly problematic for open source projects that are typically already bottlenecked by maintainer review bandwidth."
   — HN comment https://news.ycombinator.com/item?id=46765795, posted **2026-01-26**.

10. > "Here's my question: why did the files that you submitted name [maintainer name redacted] as the author? / Beats me. AI decided to do so and I didn't question it." ... "This humongous amount of code is hard to review, and very lightly tested. (You are only testing that basic functionality works.) Inevitably the code will be full of problems, and we (the maintainers of the compiler) will have to pay the cost of fixing them."
   — the OCaml compiler incident, quoted in HN comment https://news.ycombinator.com/item?id=46689187, posted **2026-01-20**. The maintainer's objection is literally "lightly tested — you are only testing that basic functionality works."

11. > "I see this in code-reviews where AI tools like code-rabbit and greptile are producing workslop in enormous quantities. It is sucking up enormous amount of human energy just reading the nicely formatted bs put out by these tools. All of that for finding an occasional [real bug]"
    — HN comment https://news.ycombinator.com/item?id=45339025, posted **2025-09-22**. Negative evidence about the *category* Alex would be entering: the current AI-review products are experienced as noise generators.

**The workaround people already perform by hand** (the strongest single signal that the mechanism is wanted):
> "Then it creates tests and verifies that all of them actually work, not just pass. To do this, my agent writes the test, then it deletes the code it covers, reruns the test, confirms it goes red, and finally puts the code back."
— HN comment https://news.ycombinator.com/item?id=49309494, posted **2026-08-15** by one commenter, describing a workflow behind "more than 400 PRs merged over the last 4 months." **This person hand-rolled base-vs-candidate discrimination testing because no product gave it to them.** That is the product, described by a user, two weeks ago, unprompted.

**Context on scale of the underlying disappointment** (not the pain itself, but the reason budgets are under scrutiny):
> "ALL the AI tooling we have implemented (at least on the engineering side of the equation) has contributed to a total of... drum roll please... 7 (seven) Percent overall productivity increase! The most productive teams saw a productivity increase of around 20%, while some teams actually saw drops in productivity into the negative percentage points."
— HN comment https://news.ycombinator.com/item?id=48743713, posted **2026-07-01** by one commenter, describing a formal 2-year evaluation at a ~2,000-developer public company with unlimited AI tooling budget.

## Willingness-to-pay evidence (>= 3)

| Competitor / substitute | Pricing (exact, URL, seen 2026-08-30) | Does it do base-vs-candidate differential verification? |
|---|---|---|
| **CodeRabbit** | Pro **$24/user/mo** annual; Pro Plus **$48/user/mo**; CodeRabbit Security **$40/user/mo**; Enterprise custom; Slack agent **$0.50/agent-minute**. Site banner: **"We raised $143M to build the control layer for software change."** https://www.coderabbit.ai/pricing | **Partially, and this is the headline risk.** Its config reference ships a built-in pre-merge check `issue_assessment` — *"Linked Issue Assessment \| Assess how well the PR addresses linked issues"* — with `mode: error` that **"requires resolution before merging"** and **"can block the PR until the check passes."** It also ships `custom_checks` with *"Deterministic pass/fail criteria (max 10,000 characters)."* https://docs.coderabbit.ai/reference/configuration. It is an LLM judgment, not an executed differential — but it occupies the same slot on the PR, is included in the $24 tier ("Built-in pre-merge checks"), and a buyer will not distinguish the two in a 30-second pitch. |
| **Greptile** | Starter **free** (1 dev, 50 credits/mo); Pro **$30/seat/mo** (50 credits/seat, $1/extra credit); Enterprise custom. Free for MIT/Apache OSS; 50% off pre-Series-A. https://www.greptile.com/pricing | **Closest thing to "yes" on the market.** TREX (Runtime Validation, shipped **2026-06-15**): *"When Greptile reviews a PR, it picks out the behavior worth running and spins up a TREX agent. The agent spins up a sandbox, runs the relevant code, and reports back on issues"* — with evidence artifacts: *"logs, screenshots, API traces, execution scripts, or even a video of a UI change playing out."* Claimed +20% bugs caught vs static review. https://www.greptile.com/blog/trex. It executes the **candidate**; it does not appear to execute the **base** for discrimination. That gap is the entire remaining differentiation, and it is one sprint wide for a funded team. |
| **Qodo** | Pro Team **$30/mo** base, credits at **$0.012/credit** pooled, ~18/36/144 reviews per month at 2,500/5,000/20,000 credits; Enterprise for 30+ users. https://www.qodo.ai/pricing/ | No differential execution found. Agentic PR review + rules. |
| **Graphite** | Hobby free; Starter **$20/user/mo**; Team **$40/user/mo** (unlimited AI reviews); Enterprise custom. https://graphite.dev/pricing | No. Review + stacking + merge queue. |
| **Sourcery** | Free for OSS; Pro **$12/seat/mo**; Team **$24/seat/mo**; Enterprise custom. https://sourcery.ai/pricing | No. |
| **Diffblue** | **Outcome-priced**, and the most interesting anchor in this table: *"Pay for coverage delivered — not seats, API calls, or guesswork. You're charged for net new lines of coverage added — tests that compile, pass, and strengthen your codebase."* From **$1,500 for 5,000 net new lines**, **$0.30/line**. Explicitly sells the verification property: *"Built-in verification framework — you never review broken tests."* https://www.diffblue.com/pricing/ | Not PR-differential, but it proves a buyer will pay for **independently re-verifiable outcomes** rather than seats — and it validates a pricing model Alex could copy ($/proven claim) that no seat-priced incumbent can match. |
| **GitHub Copilot code review** | Bundled into Copilot seats. | The commoditization floor. Whatever GitHub bundles for free defines the price of the generic half of this product. |
| **Free OSS clones of this exact idea** | **$0.** See Incumbents section — six of them, all shipped in the last eight weeks, all with 0-5 stars. | `Kartik24Hulmukh/jittest` does **exactly** this, verdict taxonomy and all. |

**What the pain costs today, for reference:** METR's finding says ~50% of test-passing agent PRs are not mergeable. If a 40-dev shop merges 200 agent PRs/week and a senior reviewer spends 25 extra minutes per PR determining "did this actually fix it," at a $95/hr fully-loaded rate that is ~$79K/quarter of review labor. The value is real. **The problem is not value. The problem is that the value is already claimed by two funded vendors and given away by six free ones.**

## Reachability (50 qualified buyers in 30 days, $0)

| Channel | Evidence the buyer is there | Play | Honest yield |
|---|---|---|---|
| **HN Ask/Show threads** | https://news.ycombinator.com/item?id=49321400 (2026-08-16) and https://news.ycombinator.com/item?id=49461811 (2026-08-27) contain ~12 self-identified buyers between them, several naming their company situation. | Reply substantively (not promotionally) in live threads; these threads recur roughly monthly. | 10-25 named, self-selected people/month. Genuinely high quality. |
| **GitHub issues + repos with AI contribution policies** | GitHub search for `"AI contribution policy" in:readme` returns **204 repos**, including snipe-it (14,890 stars) and openedx/openedx-platform (8,175 stars). Each has a maintainer with a written, machine-checkable-ish policy and a public contact. | Run the checker offline against their public PR history, publish the aggregate ("I checked 204 repos' AI policies against 8,000 PRs — here's the compliance rate"), never open an unsolicited PR or issue. | 50+ identified in a week. Conversion to *paying* is the problem, not identification. |
| **Show HN** | One shot, non-repeatable. | Ship the OSS differential gate, launch it. | **Read the graveyard first.** HN Show HN history for this category: "AI Code Review Agent" 2 pts, "CodeProt (94% precision)" 1 pt, "AI Code Review CLI" 5 pts, "Stanza" 2 pts, "LogicVisor" 2 pts, "AI code reviews with deep code understanding" 3 pts, "Igor" 2 pts. CodeRabbit's own Show HN in 2023 got **3 points**. The median outcome for an AI-code-review Show HN is single digits. |
| **Boston, in person** | Boston New Technology, Boston Software Crafters, Boston DevOps, the Cambridge/Seaport startup density. Buyer (a) is physically present in quantity. | Attend 4 meetups in 30 days, demo the differential matrix on a laptop against a real public PR. | 20-40 conversations. This is Alex's real edge and it is idea-agnostic. |
| Reddit (r/ExperiencedDevs, r/ClaudeAI) | Almost certainly the highest-volume venue for this complaint. | — | **Could not verify.** reddit.com returned 403 to every method attempted in this session. Treat as unmeasured upside. |

**Verdict on reachability: high (4/5).** Developers are the most reachable buyer on earth and Alex is one. Reaching 50 qualified buyers at $0 in 30 days is easy. **Converting any of them away from a tool they already pay for is the hard part, and reachability does not help with that.**

## Wedge

**Smallest thing one buyer pays for this month.** Not a review bot — the review-bot slot on the PR is taken, twice over, by funded companies. Sell the one output nobody else produces:

**A `discriminating-tests` check.** For each test file touched or added by the PR, run that test against the **base** commit and the **candidate** commit in isolated snapshots, and report one line per test:

- `PROVEN` — red on base, green on candidate. The test discriminates the change. *This is the only line that means anything.*
- `NON-DISCRIMINATING` — green on both. The test was added, CI is green, and it proves nothing about the fix.
- `REFUTED` — red on both. The claimed fix does not hold.
- `UNRESOLVED` — the base snapshot would not build. A loud refusal, never a guess.

Then one summary number the manager actually wants: **"7 of the 11 tests added by agent PRs merged this week were non-discriminating."** That is a metric no incumbent emits, it is checkable, it is embarrassing in a useful way, and it does not compete with CodeRabbit — it grades CodeRabbit's output.

**Price:** flat **$99/repo/month**, or Diffblue-style **$/proven claim**. Not per seat — per seat is a losing fight against a $143M-funded vendor at $24.

**Why this and not the policy-compliance half:** the machine-readable AI-policy check (disclosure trailer present, tests added, diff under N lines) is a 200-line GitHub Action, is free-forever in every buyer's mind, and CodeRabbit's `custom_checks` with "deterministic pass/fail criteria" already covers it. It is a giveaway, not a wedge.

## Build estimate

**~6-9 agent-days to a sellable MVP**, assuming the Nemisis engine already handles claim extraction and world isolation.

Components:
- GitHub App: webhook on `pull_request`, check-run creation, matrix rendered as a check summary — 1 day.
- Base/candidate snapshot orchestration inside the **customer's own CI runner** (a composite GitHub Action, not Alex's compute — this is what keeps burn under $40/mo) — 2 days. This is the hard part: reliably building the base snapshot for repos with dirty dependency setups. The `UNRESOLVED` verdict exists precisely because this will fail often.
- Test-selection: which of the PR's tests to run on base without running the full suite for 40 minutes — 1-2 days.
- Claim extraction from the PR body / linked issue → typed claims — reuses Nemisis, 1 day of adaptation.
- Manifest / signed receipt — 0.5 day. **Note: the receipt is engineering-culture catnip and, on the evidence below, worth approximately zero dollars.**
- Landing page, docs, OSS repo, install flow — 1-2 days.

**Reusable assets: Nemisis matrix/evidence/patches/junit/bundle; Graphene execution/adapter.py Seatbelt + sandbox.py Docker executor.**

**Recurring burn:** ~$0-15/mo if execution runs on the customer's runners (domain + a small control-plane box). If Alex runs the sandboxes himself, sandboxed test execution for even ten active repos will blow past $40/mo immediately. **The architecture is forced by the budget constraint, and fortunately the forced choice is also the right one.**

## Unit economics

- Price: $99/repo/mo flat (or $0.50/proven claim, min $49/mo).
- COGS at the customer-runs-the-compute architecture: ~$1-3/repo/mo (control plane, storage of receipts). Gross margin >95%.
- CAC: $0 cash, but high in hours — the only channels are content, HN, and in-person, all of which cost Alex's 12 hrs/week.
- Break-even on burn: **1 customer**.
- To hit $1,000 MRR: ~10 paying repos. Plausible in a year *if* the differentiator survives contact with Greptile's roadmap.
- Churn risk is the real number here: a check that reports `UNRESOLVED` on half of a customer's PRs (because their base snapshots don't build) gets uninstalled in week two. **The product's value is bounded by how often it can build a clean base snapshot in a stranger's repo, and this dossier found no evidence about that rate.** That is the number to measure before building anything else.

## Risks

1. **Six people already built this and nobody starred it.** This is the finding that should dominate the decision. Public GitHub repos shipped in the last 8 weeks implementing exactly this concept:
   - `Kartik24Hulmukh/jittest` — **0 stars**, created 2026-07-26, pushed 2026-08-30 (today). README: *"jittest is a differential test-execution gate for agent-authored pull requests. It does not read your diff and guess. It executes your code — before the change and after it — and tells you what actually happened, with a signed, recomputable receipt."* Verdicts: `proven_catch` (red on base, green... it defines it as passes-on-base-fails-on-head), `refuted`, `non_discriminating`, `inconclusive`. Ed25519-signed receipts. **This is the idea, the taxonomy, and the pitch, already on PyPI.**
   - `mrodgersjs-web/proof-gate-action` — **0 stars**. *"The CI step that catches an AI agent forging 'done.'"* HMAC-signed ProofPackets.
   - ⚠️ VERIFIER: misattributed - the quote is verbatim from HN 46915049, but that commenter (DavidYoussef) links `github.com/DNYoussef/codeguard-action`, since renamed `DNYoussef/guardspine-code-action` — **6 stars, 3 forks, pushed 2026-08-17**, not 0 stars and not dead. `ai-codeguard/codeguard-action` is a different, empty repo (created *and* last pushed 2026-04-25, no description), created 2.5 months **after** the HN comment. Original line follows.
   - `ai-codeguard/codeguard-action` — **0 stars**; its author pitched it on HN (https://news.ycombinator.com/item?id=46915049, 2026-02-06) with risk tiers L0-L4 and *"seals everything into a hash-chained evidence bundle."*
   - `mojunrubest/agent-delivery-gate` — **0 stars**. *"Host-owned verification gate for Agent-delivered pull requests."*
   - `Safkatul-Islam/proofgate` — **0 stars**. *"An evidence-first release gate for pull requests."*
   - ⚠️ VERIFIER: misattributed - provenance is reversed. GitHub API says `tiammomo/RepoSteward` has `fork: false` and was created **2026-08-21**, six days *before* `pwd11/RepoSteward` (created 2026-08-27, 0 stars). tiammomo is the original with 23 stars in nine days; pwd11 is the copy. Original line follows.
   - `pwd11/RepoSteward` — **0 stars** (a fork at `tiammomo/RepoSteward` has 23). *"policy-gated control plane for turning GitHub issues into verified, human-reviewed pull requests."*
   - `jacquardlabs/gauntlet` — **4 stars**, pushed 2026-08-25. *"Independent judges for pre-delivery artifacts — findings with receipts."*
   **The binding constraint in this market is distribution and trust, not capability.** Alex's advantage is capability. That is the wrong advantage for this market.

2. **The incumbents already own the PR slot and are one sprint from the differentiator.** CodeRabbit ships blocking `issue_assessment` at $24/seat with $143M in the bank. Greptile ships sandboxed execution with evidence artifacts at $30/seat and shipped it 10 weeks ago. Adding "also run it on base" to TREX is a small feature for Greptile and an existential one for Alex.

3. **The buyer is not asking for this.** Read what the twelve people in the two August 2026 Ask HN threads actually want: architectural review, decision-trace review, plan-vs-implementation conformance. one commenter (2026-08-18): *"the reviewable unit shouldn't be the final diff. Instead, review the decision trace: plan, assumptions, etc."* — the herve.review founder replies *"I can't agree more."* Another commenter (2026-08-28): *"We have 5 devs and changed from doing code review to plan review... Then when the PR gets raised there is a loop that just compares the implementation plan to the actual code."* **Not one person in either thread asked for proof that the tests discriminate.** The mechanism is correct; the demand is pointed elsewhere.

4. **And a funded startup is already serving *that* demand.** `until-dev/plugins` (28 stars, pushed 2026-08-27): *"Define intent in a Plan, let the agent run, and check every pull request against it."* Open-source plugin + hosted workspace, with a manifesto site (notyourpeer.com). Plus `herve.review`, in beta as of 2026-08-25, capturing agent sessions to guide reviewers. Both launched within the last month.

5. **The category is experienced as noise.** See pain quote #11. Adding a ninth bot comment to a PR is a negative-value action unless the signal is unambiguous, which makes the `UNRESOLVED` rate (see Unit economics) product-defining.

6. **Base-snapshot build reliability is unvalidated and is the whole product.** No evidence gathered on how often a stranger's repo can be built at an arbitrary base commit inside CI.

7. **The signed-manifest/tamper-evidence angle is the most seductive and least valuable part.** Three of the six dead clones lead with cryptographic receipts. Zero stars each. The one voice found arguing that auditors want this (https://news.ycombinator.com/item?id=46945119, 2026-02-09) is the author of one of those 0-star repos.

8. Ethics: clean. Public repos, no scraping behind logins, no unsolicited PRs or issues on other people's repos.

## Kill criteria

Kill this idea if any of the following is true. **Two of them already appear to be true before writing a line of code.**

1. ☑︎ **ALREADY TRUE — a working free implementation of the exact idea exists with no adoption.** `jittest` (0 stars, on PyPI, pushed today) plus five siblings. If capability were the constraint, at least one would have traction.
2. ☑︎ **LIKELY ALREADY TRUE — an incumbent ships the buyer-visible version.** CodeRabbit's `issue_assessment` blocking pre-merge check, included at $24/seat.
3. ☐ Ask 10 engineering leaders "would you pay $99/repo/mo to know which of your agent PRs' tests actually discriminate?" and fewer than 3 say yes → kill. **Do this before building.**
4. ☐ Run the base-snapshot builder against 50 random public repos with recent PRs; if the `UNRESOLVED` rate exceeds 40%, kill — the check is not trustworthy enough to be non-noise.
5. ☐ 30 days after the OSS launch, fewer than 50 stars and fewer than 5 installs → kill (calibrated against jittest's 0 and gauntlet's 4).
6. ☐ Greptile or CodeRabbit ships base-vs-candidate differential execution → kill immediately, do not compete.

## Incumbents and adjacent players

**Funded, in-market, own the PR comment slot:**
| Player | Price | Overlap |
|---|---|---|
| CodeRabbit ($143M raised) | $24-48/user/mo | Blocking `issue_assessment` + deterministic `custom_checks`. Direct. |
| Greptile | $30/seat/mo | **TREX runtime validation** — sandboxed execution + evidence artifacts, June 2026. Most direct. |
| Qodo | $30/mo + credits | Agentic PR review, rules. |
| Graphite | $20-40/user/mo | Review, merge queue, Cursor cloud agents in-PR. |
| Sourcery | $12-24/seat/mo | Review, free for OSS. |
| GitHub Copilot code review | bundled | The free floor. |
| Cursor BugBot | bundled | Named favorably by a practitioner in the Aug 16 thread. |
| Diffblue | $0.30/verified line, from $1,500 | Outcome pricing for verified test artifacts. Pricing-model precedent, not a competitor. |

**New entrants, last 60 days, serving the demand buyers actually voiced:**
- `until-dev/plugins` — 28 stars, plan-vs-PR conformance, OSS plugin + hosted, 2026-08-27.
- `herve.review` — agent-session capture to guide review, beta, 2026-08-25.
- `pyor.review` — GitHub PR replacement built by a practitioner for one team, 2026-08-25.
- `jacquardlabs/gauntlet` — 4 stars, multi-judge with receipts, 2026-08-25.

**Dead-on-arrival clones of this exact idea (all 0 stars):** jittest, proof-gate-action, codeguard-action, agent-delivery-gate, proofgate, RepoSteward.

**Substitutes people use instead, for free:** a second Claude Code session reviewing the PR (named by 4 of ~12 respondents in the Aug 16 thread); custom Claude "skills" per review lens; hand-rolled mutation checks (see the mutation-check quote above).

## Score

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Time to first dollar | x3 | **2** | The PR-check slot is occupied at $24/seat by a $143M-funded vendor whose `issue_assessment` check a buyer will read as the same product; first dollar requires displacement, not adoption, and six free clones set the reference price at $0. |
| Reachability by a student | x3 | **4** | Two Ask HN threads in 14 days contain ~12 named self-identified buyers, GitHub search yields 204 repos with formal AI policies and public maintainer contacts, and Boston's SaaS density puts buyer (a) in a room Alex can walk into for the price of a T fare. |
| Pain x frequency | x2 | **5** | METR measured ~50% of test-passing agent PRs as unmergeable across 296 PRs; curl killed its bug bounty; snipe-it (14.9K stars) and Open edX wrote governance policies naming "fix failing tests by bypassing them" as an antipattern; the complaint recurs on HN weekly and twice in the last fortnight. |
| WTP evidence | x2 | **5** | Six vendors publish live per-seat prices between $12 and $48/user/month for AI PR review, CodeRabbit raised $143M against this exact workflow, and Diffblue prices verified outcomes at $0.30/line from a $1,500 floor. |
| Fit with assets and strengths | ×2 | **5** | Nemisis is the engine; Graphene sandbox/executor is the runner. |
| Compounding | x2 | **3** | A corpus of which claims get refuted, plus per-repo base-snapshot build recipes, is a genuine accumulating asset — but it compounds slowly and confers no defense against Greptile adding one flag to TREX. |
| Risk (5 = low) | x2 | **1** | Two funded incumbents occupy the slot and one already executes code in a sandbox; six independent free implementations of the precise idea have zero adoption between them; GitHub bundles the generic version free; and the buyers who spoke this month asked for plan-conformance and decision traces, not test discrimination. |
| Ceiling | x1 | **4** | CodeRabbit's $143M raise and $24-48/seat pricing prove the category supports a large business, and the differential-proof angle could extend into agent-vendor pre-flight and compliance attestation. |
| Build cost (5 = cheap) | x1 | **4** | ~6-9 agent-days on top of an existing Nemisis engine, and running the sandboxes inside the customer's own CI runners keeps recurring burn near $0 and inside the $40/month ceiling. |

**Subtotal excluding fit: 54 / 80.**
(2x3=6, 4x3=12, 5x2=10, 5x2=10, 3x2=6, 1x2=2, 4x1=4, 4x1=4)

## Verdict

**Weak — do not build; harvest the parts.** The pain is as well-evidenced as anything in this research programme, and the willingness-to-pay is proven to the decimal point. Neither of those is the constraint. The constraint is that **this specific mechanism has been independently built six times in eight weeks by solo developers and has attracted a combined four GitHub stars**, while the two funded incumbents already own the surface it would render on and one of them already executes code in a sandbox during review. Alex's advantage — a working differential-verification engine — is an advantage in the dimension this market does not reward.

Three things are worth carrying forward:

1. **The metric, not the product.** "N of your agent PRs added tests that prove nothing" is a number no incumbent emits and every engineering manager would read. It may be a content asset, a free one-shot audit, or a lead magnet for something else — but it is more interesting as a *measurement* published about the ecosystem than as a *check* sold per repo. The 204 repos with public AI contribution policies are a ready-made corpus for exactly that study, and the study costs nothing but compute.
2. **The Diffblue pricing model.** Outcome pricing ("pay per proven claim") is the one commercial move a seat-priced $143M incumbent structurally cannot copy. Keep it for whatever Alex does build.
3. **Nemisis itself is validated as an engine and invalidated as a product.** The METR result and the Open edX antipattern list say the mechanism is correct. The six dead repos say it is not a business on its own. Look for a domain where differential verification is the *regulated* or *contractual* requirement — where someone must produce the evidence and cannot choose not to — rather than developer tooling, where it is a nice-to-have competing with a free second Claude session.

Kill criteria 3 and 4 are cheap enough that if Alex disagrees with this verdict, running them costs under a day and would settle it with data instead of judgment. Do not skip to building.

## Research log

**Time spent:** ~80 agent-minutes, 2026-08-30.

**Sources that worked:** HN Algolia API (`hn.algolia.com/api/v1/search` and `/items/{id}` — the items endpoint for full threads was the highest-yield tool in this session), GitHub REST API (repo search, readme raw fetch), raw.githubusercontent.com, vendor pricing pages via curl with a browser UA (coderabbit.ai, greptile.com, graphite.dev, qodo.ai, sourcery.ai, diffblue.com), docs.coderabbit.ai configuration reference, metr.org.

**Sources that failed:**
- **reddit.com** — 403 to every method, as flagged in the brief. r/ExperiencedDevs and r/ClaudeAI are almost certainly the highest-volume venue for this complaint and are entirely unmeasured here. This is the single biggest gap in the dossier.
- **Capterra** — Cloudflare interstitial ("Just a moment... Enable JavaScript and cookies to continue") on the CodeRabbit reviews page. No 2-3 star reviews obtained.
- **Trustpilot** — bot verification wall.
- **Indeed** — "Security Check / Additional Verification Required." No job-posting evidence gathered.
- **news.ycombinator.com direct via WebFetch** — HTTP 429. Worked around entirely via the Algolia items API, which returns full comment trees.
- **docs.greptile.com/trex** — empty response; the TREX details came from greptile.com/blog/trex instead.
- **WebSearch** — session budget (200 calls) was already exhausted by earlier runs before this dossier began. All findings here came from direct fetches and API queries, which is why the competitor list is built from GitHub search and pricing pages rather than from search-result surveys. A few claims in the brief (the "37 of 120 surveyed projects ban outright" figure; CodeRabbit's "$40M ARR") **could not be independently verified in this session** and are not relied on above — the $143M raise is verified from CodeRabbit's own site banner.

**Searches run:** ~20 HN Algolia queries (AI PR review/maintainer, slop pull requests, tests pass but don't fix, agent deleted the test, reviewing AI code harder than writing, CodeRabbit noise, curl bug bounty, Show HN AI code review, differential testing base vs candidate, AI contribution policy, and others); 5 GitHub repo searches; 9 vendor pricing/doc fetches; 2 full HN thread expansions; 3 raw policy-file fetches.

**Dead ends worth recording:** searches for maintainers complaining specifically that "the tests passed but the patch didn't fix the issue" returned almost nothing in that phrasing — the complaint is real but people express it as "slop," "I can't trust it," or "reviewing is harder than writing." The METR study is the only place the claim is *measured*. That gap between how loudly the pain is felt and how rarely it is described in the product's own vocabulary is itself a warning about how hard this would be to sell.

## Verification (2026-08-30, adversarial pass)

- **Quotes: 36 checked, 35 verified, 0 unfetchable, 1 misattributed.** Unusually clean. Every HN comment (14 items via the Algolia `/items/` API), the METR note, the Open edX `AI_POLICY.md`, the CodeRabbit config reference, the Greptile TREX post, the Diffblue pricing page and every clone README fetched successfully and matched verbatim. Two silent typo corrections in commenters' text ("an"→"and"; "more work of the work"→"more of the work") and one bracketed substitution (another commenter's "an occasional nugget that turns out to be useful" → "an occasional [real bug]") are honest editorial notation, not strikes. Quote #4 joins two fragments with an ellipsis in **reverse** source order — no words altered, but the ellipsis implies forward continuation. The one real failure is the `codeguard-action` line, marked above.

- **Claims:**
  - **METR — CONFIRMED, exact.** "Roughly half of test-passing SWE-bench Verified PRs... would not be merged"; "about 24.2 percentage points (standard error: 2.7)"; 296 PRs; 4 maintainers; 95/500 tasks in scikit-learn/Sphinx/pytest. https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/ — **but two caveats the dossier omits invert its usefulness here.** METR told maintainers: *"Testing Requirements: We ask them to ignore testing requirements in the PR, as agents are not elicited to include proper tests. This is generous to AI-generated patches."* The study therefore says nothing about whether agent-written tests discriminate — the exact thing this product sells. And the golden (real, already-merged human) baseline was only **68%**, so "~50%" is golden-adjusted, not an absolute defect rate; the $79K/quarter figure treats it as absolute.
  - **"Six free clones of this exact idea" — PARTLY; it is two.** Only `Kartik24Hulmukh/jittest` and `Safkatul-Islam/proofgate` actually execute base-vs-candidate. `proof-gate-action` recomputes an HMAC over an artifact hash (no test execution); `agent-delivery-gate` runs only the candidate under a host verifier; `codeguard-action` is risk-tiered LLM review + evidence bundle; `RepoSteward` is an issue→PR control plane. Risk 1 says this finding "should dominate the decision," so the inflation lands on the load-bearing claim. (proofgate is actually *stronger* than the dossier's product — it runs base, PR, **and** an agent-patched branch.)
  - **jittest — CONFIRMED but mischaracterised as "exactly this, verdict taxonomy and all."** 0 stars, created 2026-07-26, pushed 2026-08-30, PyPI v0.3.4 — all correct. But its `proven_catch` is *"test passes on base, fails on head"* — a **regression** catch, semantically inverted from this dossier's `PROVEN` (red on base, green on candidate = **fix** verification). Also: 0 stars understates it — **499 PyPI downloads in the last month**.
  - **Risk 6 / Kill criterion 4 ("base-snapshot reliability is unvalidated... this dossier found no evidence about that rate") — REFUTED by the very README the dossier quotes.** jittest publishes it: **59/83 (71%) `inconclusive`** — environments could not be restored; only 24/83 (29%) reached a definitive verdict. That is ~1.8x the dossier's own 40% kill threshold. Fair caveat: jittest's cohort is *historical* PRs in flask/requests/youtube-dl, the hardest case; a live PR's merge-base is days old and already built by CI. But "no evidence" is wrong, and the one public number points at the kill.
  - **CodeRabbit — CONFIRMED verbatim,** including the `$143M` banner (corroborated: "CodeRabbit raises a $143M Series C at a $1.5B valuation," HN 49274706, 2026-08-12), `issue_assessment` "Linked Issue Assessment | Assess how well the PR addresses linked issues", and the mode enum "error requires resolution before merging... can block the PR until the check passes." Two corrections: `issue_assessment` **defaults to `warning`, not `error`**; and `custom_checks` is "**Custom** Pre-merge Checks" — a **Pro Plus ($48)** feature per the pricing page, not the $24 tier the Wedge section implies ($24 Pro gets "Built-in pre-merge checks" only).
  - **Greptile TREX — CONFIRMED verbatim,** dated 2026-06-15, "+20% more bugs," both evidence-artifact quotes exact, and no mention anywhere of executing the base. https://www.greptile.com/blog/trex — **two omissions that soften Risk 2:** Greptile's own nav still labels it "**TREX: Runtime Validation Beta**," and the pricing page rations it at **3 credits vs 1 for a standard review** (~16 TREX reviews/seat/month on the $30 Pro plan). The incumbent's position is less settled than "one sprint wide" implies.
  - **All pricing — CONFIRMED to the decimal.** CodeRabbit $24/$48/$40 + $0.50/agent-minute; Greptile Free/$30 + OSS-free + 50% pre-Series-A (page adds "under $2M revenue"); Qodo $30 + $.012/credit + ~18/36 reviews; Graphite Free/$20/$40 "unlimited AI Reviews"; Sourcery OSS-free/$12/$24; Diffblue "Starting at $1500", "5,000 Net new lines", "$0.30 / line", plus both verbatim quotes. Graphite has moved to graphite.com (dossier's URL redirects).
  - **204 repos with "AI contribution policy" in:readme — CONFIRMED exactly (204 today).** snipe-it 14,890 stars ✓ (now `grokability/snipe-it`); openedx-platform 8,175 ✓. curl ending its bug bounty over AI slop ✓ ("cURL removes bug bounties," 435 pts, 2026-01-21, plus five corroborating stories).
  - **Show HN graveyard — every point count CONFIRMED, but the sample is selection-biased.** CodeProt 1, AI Code Review CLI 5, Stanza 2, LogicVisor 2, deep-code-understanding 3, Igor 2, and CodeRabbit's own 2023 Show HN 3 — all exact. The same Algolia queries also return, in-category and mostly recent: **Stage 130 pts (2026-04-16)**, LlamaPReview 102, Haystack 88, **adamsreview 85 (2026-05-11)**, and **"I built a tool to assist AI agents to know when a PR is good to go" 45 pts (2026-01-17)** — the last being nearly this dossier's own pitch. "Read the graveyard first" only read the graveyard.
  - **"~12 self-identified buyers" in the two Ask HN threads — OVERSTATED.** The threads carry 11 and 8 comments, ~15 unique commenters. At least five are **vendors pitching in-thread**: a CodeRabbit staffer ("Coderabbit DX staff here"), the founders of herve.review, jacquardlabs/gauntlet and pyor.review, and a vendor pitching their own boilerplate. Plausible buyers: **6-8**. The Aug-27 thread has **2 points**. And the Risk-3 exchange the dossier leans on — the herve.review founder's "I can't agree more" — is the herve.review founder endorsing the thesis they are selling, not an independent buyer. Risk 3's core assertion ("not one person asked for proof that the tests discriminate") is nonetheless **CONFIRMED** against both full comment trees.

- **Score challenges:**
  - **Reachability 4 → 3.** ~15 unique commenters across both threads, a third of them vendors trawling the same leads (CodeRabbit staff posted directly in-thread); one thread scored 2 points. The 204 repos are real but are buyer (b) — the segment the dossier itself calls least able to pay.
  - **Pain × frequency 5 → 4.** Review-load pain is a well-evidenced 5. Pain for *test non-discrimination specifically* is a 3: METR explicitly excluded testing requirements, and the dossier's own research log concedes nobody expresses the complaint in the product's vocabulary.
  - **Build cost (5 = cheap) 4 → 3.** Base-snapshot orchestration is budgeted at 2 days and called "the hard part." The only public measurement of it (jittest, 71% unrestorable) says it is the *whole* problem.
  - **Risk (5 = low) 1 → 2, near-neutral.** The cited evidence is weaker than stated (six clones → two; TREX is Beta and rationed; CodeRabbit's overlapping `custom_checks` is $48 not $24). But the missed free substitute below and CodeRabbit's $10M OSS giveaway push the other way, so 1 is defensible for reasons the dossier did not give.
  - **Vague / unfalsifiable kill criteria.** KC2 is marked "☑︎ **LIKELY** ALREADY TRUE" — "likely" is not a decision rule, and on the verified facts (`issue_assessment` is an LLM judgment defaulting to `warning`, not an executed differential) a strict reading says KC2 is **not** met. KC3 asks a hypothetical-purchase question that reliably over-predicts; it needs a paid pilot or an invoice, not a "would you." KC6 is the only clean, checkable criterion in the list, and I confirmed it is **not** currently met — neither vendor executes the base.

- **Missing:**
  - **Mutation testing — the real free incumbent, never mentioned once.** Stryker-JS 3,061 stars, infection 2,237 (PHP), mutant 2,187 (Ruby), Stryker.NET 2,065, PIT 1,856 (JVM), mutmut 1,410 (Python), humbug 1,125, cosmic-ray 654 — all free, mature, actively maintained (most pushed within the last week). They answer "does this test detect a change to the code it covers?" **without building the base commit at all** — sidestepping the 71% failure mode entirely. Critically: one commenter's workflow, the dossier's "strongest single signal" and "the product, described by a user, unprompted," is *manual mutation testing*. The claim that "no product gave it to them" is false; mutmut has existed for a decade. This is a stronger kill argument than all six clones combined.
  - **CodeRabbit committed $10M+ to open-source projects over the next 12 months** (HN 49450921, 2026-08-26 — four days before this dossier). Buyer (b) is about to be handed the incumbent for free.
  - **Security is the unpriced risk, and "Ethics: clean" skips it.** "How we exploited CodeRabbit: From simple PR to RCE and write access on 1M repos" — 687 pts, 2025-08-19. Executing an untrusted contributor's *base and candidate* test bundles is the highest-severity attack surface in this category. `agent-delivery-gate`'s own README ships a THREAT_MODEL.md conceding it cannot prove "a malicious project cannot attack a same-host runner." The dossier's chosen architecture pushes that liability onto the customer's runners — a sales objection, not just a COGS saving.
  - **GitHub's own roadmap was never checked.** Copilot code review is called "the commoditization floor" and used to justify the Time-to-first-dollar score of 2, but no primary source was consulted on whether GitHub ships or plans PR-time execution. The largest platform risk in the dossier is asserted, not verified.
  - **`DNYoussef/guardspine-code-action`** (6 stars, 3 forks, active to 2026-08-17) and **`tiammomo/RepoSteward`** (23 stars in nine days, not a fork) are both live projects miscounted as 0-star corpses — see the two ⚠️ marks above. The "combined four GitHub stars" figure in the Verdict is actually ~33 across the correctly-identified repos.
  - **Reddit remains unmeasured** (403 to everything, confirmed again today). The dossier is right to call this its biggest gap.

- **Overall: mostly-trustworthy** — the quote discipline is exceptional (35/36 exact, pricing correct to the decimal) and the "weak — do not build" verdict survives and is arguably *strengthened* by the mutation-testing substitute the dossier missed, but two load-bearing claims fail on inspection: the "six independent implementations" that Risk 1 says should dominate the decision are really two, and the base-snapshot reliability the dossier calls "unvalidated with no evidence" is published at 71% failure in the very README it quotes.


## Final score (main agent, 2026-08-30)
- Fit with assets and strengths: **5/5** ×2 — Nemisis is the engine; Graphene sandbox/executor is the runner.
- Reusable assets: Nemisis matrix/evidence/patches/junit/bundle; Graphene execution/adapter.py Seatbelt + sandbox.py Docker executor.
- Subtotal as researched: 54/80 · after adversarial verification: **50/80** (reach 4→3, pain 5→4, build 4→3, risk 1→2)
- **Total: 60/90**


## Competitor deep-dive (2026-08-30) — C-track: Nemisis verification core as OSS library + the AI-policy-corpus measurement study
**Verdict: RESHAPE**

### Competitors examined
- **SWE-bench harness (pip: swebench)** — substantial overlap. Free, Apache-2.0 Weakness: Requires precomputed base results from a gold patch, so it cannot grade an arbitrary live PR; per-instance Docker images; benchmark-shaped, not CI-shaped; no tamper-evident manifest.
- **jittest** — identical overlap. Free, on PyPI Weakness: Zero adoption after a month of daily pushes. Solo, unknown author, no docs site, no CI integration story. Its failure is the market signal, not a capability gap.
- **mutmut (and cosmic-ray, Stryker)** — substantial overlap. Free, OSS Weakness: Slow (full suite per mutant), not PR-shaped, no verdict-per-claim reporting, not wired into CI as a merge gate, no provenance/manifest layer. Does not answer 'did this specific agent diff get proved.'
- **unidiff (matiasb/python-unidiff)** — partial overlap. Free, MIT Weakness: Parsing only - no application, no path-traversal or symlink safety, no post-apply file-set verification. That residual is exactly Nemisis's patches.py (5,986 B) + safety.py (1,378 B).
- **patch-ng (conan-io/python-patch-ng)** — partial overlap. Free, MIT Weakness: No verdict model, no test execution, no manifest. Purely the apply-safely half.
- **openai/codex apply-patch crate** — partial overlap. Free, in-repo Weakness: Not a reusable library, Rust only, bespoke non-unified patch format. But its existence proves the buyer for 'safe patch application' builds it in-tree rather than importing it.
- **SWE-agent (as a would-be consumer, not a competitor)** — none overlap. Free, MIT Weakness: Not a competitor - it is the archetypal target consumer, and its five-line applier is evidence that the target consumer does not perceive a problem worth a dependency.
- **Open-fab-ai/openfab + ossf/tac#628** — adjacent overlap. Free, Apache-2.0, vendor-neutral Weakness: The predicate's entire verification story is one required field: acceptance_passed: boolean. A signed 'true' resting on a test that is green on base and green on head attests to nothing - exactly the failure the thread exists to prevent. Reference impl is Rust
- **METR: 'Many SWE-bench-passing PRs would not be merged into main'** — adjacent overlap. Free publication Weakness: Measures mergeability on a benchmark judged by humans - not test discrimination, not real merged PRs, not automated. Leaves the exact gap open: nobody has run agent-PR-added tests against the base commit in the wild and published the non-discrimination rate.
- **RedMonk AI policy landscape + CHAOSS wg-ai-alignment + melissawm policy list** — substantial overlap. Free Weakness: They occupy the policy-survey angle completely, four months ahead. More importantly they expose why the corpus is wrong for the study: 98 of 182 policies BAN AI (76 Yes, 6 Yes*, 2 No*), only 40 of 204 repos are Python, and sampled agent-PR counts were 6 (opene

### Is there a gap?
There is a real gap, but it is not the library and not the policy corpus - it is one unpublished number.

WHAT IS CLOSED. (1) Patch-apply safety: every consumer named in the brief has already resolved it in a way that forecloses a Python library. Codex wrote ~180KB of Rust in-tree with an explicit follow_symlinks policy; Aider wrote three of its own coders and has no path-traversal defence at all; OpenHands does not use unified diffs; SWE-agent's applier is five lines of subprocess with zero validation and it declares unidiff as a dependency only to format output. The two who care built it in-tree; the ones who do not are not going to import. (2) Fail-closed test-result parsing: swebench/harness/grading.py already ships the exact "a suite that never ran must not score as passing" logic, across eleven runner formats, with comments naming the karma "Executed 0 of 0" case - versus Nemisis's 2,883-byte pytest-only junit.py that needs a co-shipped plugin a stranger's repo will not have. (3) Differential discrimination as a concept: FAIL_TO_PASS vs PASS_TO_PASS is the SWE-bench definition of a task, and mutation testing (mutmut, 3.6M real downloads/mo, 35 arXiv papers on mutation score + LLM) is the mature general form. (4) The product: six free clones in eight weeks, still at 0-0-0-0-0-4 stars today, one of them (jittest) shipping the identical taxonomy on PyPI with 223 real downloads. (5) The policy survey: RedMonk shipped it 2026-02-26 with plots; CHAOSS maintains the list.

WHAT IS OPEN, PRECISELY. Nobody has taken real, merged, agent-authored pull requests from public repos, run the tests those PRs added against the commit they were merged onto, and published the rate at which those tests pass identically on both sides. METR measured mergeability - on a benchmark, judged by humans (296 PRs, 95/500 tasks, 3 repos, 24pp gap, 278 HN points). Academia measured mutation score - on synthetic suites, and arXiv 2607.22880 (2026-07-24) found those proxies unreliable exactly in the bug-exposing setting that matters here. arXiv returns 1 unrelated result for "non-discriminating tests" OR "vacuous tests". The number does not exist.

HOW LONG FOR AN INCUMBENT TO CLOSE IT. The measurement: 2-6 weeks for METR, Greptile, CodeRabbit, or any grad student who decides to run it - it is a weekend of engineering plus a fortnight of babysitting builds, and the compute is free (GitHub Actions is unlimited on public repos). There is no defensibility, only priority. The library: already closed; nothing to defend. The differentiating artifact Alex owns, matrix.py, is 2,907 bytes - roughly seventy lines of lookup table that any competent engineer reimplements in an afternoon after reading the writeup. The moat is a vocabulary, not a codebase, and vocabularies are won by publishing first, not by licensing.

The binding uncertainty is not competitive, it is operational and still unmeasured: what fraction of stranger repos can actually be built and tested at an arbitrary base commit? That rate caps the study, caps any future product, and no source found in this session reports it.

### What this changes in the dossier
- Correct the LOC figure everywhere: the provider-free core is 43,399 bytes across 8 modules (~1,100-1,300 LOC), not ~700. State that matrix.py - the component ASSETS.md calls the highest-reuse piece with 'no exact open-source equivalent' - is 2,907 bytes and safety.py is 1,378 bytes, so the differentiated IP is roughly 100 lines total.
- Strike 'no exact open-source equivalent for the Nemisis claim matrix' from STRENGTHS.md and ASSETS.md, or heavily qualify it. SWE-bench's FAIL_TO_PASS/PASS_TO_PASS is differential discrimination by construction; swebench/harness/grading.py ships the fail-closed suite-ran logic across 11 runner formats with better comments than Nemisis's pytest-only junit.py; mutation testing is the mature general answer at 3.6M real downloads/month; jittest ships the identical taxonomy including the literal token non_discriminating.
- Kill the 'OSS library for safely applying and verifying LLM-written diffs' commercial angle (#4 in the ASSETS.md Nemisis entry) and the 3-5 day 'publish the library' estimate as a standalone action. Evidence: SWE-agent applies patches in five lines of subprocess with no validation; Aider's patch_coder.py has zero path-safety; Codex built 180KB of Rust in-tree; OpenHands abandoned unified diffs. The target consumers have all already decided.
- Kill the 204-repos-with-AI-policies corpus for the study and record why: 98 of 182 curated policies ban AI outright (76 Yes / 6 Yes* / 2 No*), only 40 of 204 repos are Python, and sampled agent-PR counts were 6 (openedx/openedx-platform), 0 (argoproj/argoproj), 0 (tektoncd/community). The corpus is selected for the absence of the thing being measured.
- Replace it with a density-selected corpus: public Python repos with a green pytest suite runnable from a lockfile, merged PRs in the last ~90 days carrying an agent trailer (9,905,036 PRs match 'Generated with Claude Code'; 384,235 match 'Co-authored-by: Claude'; 142,023 match 'Assisted-by:'), filtered to PRs that added a test. Target 200-400 PRs across 20-40 repos, matching METR's order of magnitude (296 PRs).
- Record that the study's compute is $0 and does not touch the burn cap: 'GitHub Actions usage is free for self-hosted runners and for public repositories that use standard GitHub-hosted runners' (docs.github.com, accessed 2026-08-30). Run the whole thing inside a public repo's own workflow.
- Add a pre-registered kill line to the C-track: if the harness cannot build base+head and run the suite for at least 30 of the first 60 candidate PRs, stop and publish the failure rate as a one-paragraph note. That build-success rate is the unvalidated number that r2-ai-pr-verification-gate.md risk #6 already calls 'the whole product', and this session did not measure it either.
- Add the ossf/tac#628 finding: the openfab/generation predicate's entire verification story is one required boolean field, acceptance_passed. A signed 'true' resting on a test green on base and green on head attests to nothing. The contribution is ONE comment on the open issue proposing an optional structured per-claim acceptance object (supported / regression / non_discriminating / unresolved) plus a small Python verifier - the reference impl is Rust, so Python is complementary. Budget one day and score it as a credential, not a channel: the issue has 4 comments and openfab has 6 stars and 0 forks.
- Add the distribution calibration to c1-open-source-flagship.md: measurement posts in this exact niche beat Show HN library launches 2-3x on HN (METR 278p, SWE-bench contamination 466p, OpenAI benchmark note 343p, Some critical issues with SWE-bench 350p, versus 88-163p for competent 2026 Show HN libraries). Note that the 466-point post WAS a GitHub issue (SWE-bench/SWE-bench#465) - the cheapest publication venue found - and that the closest solo-scan comparable (203p, 'I scanned all of GitHub's oops commits') ran as a guest post on trufflesecurity.com, i.e. it borrowed an audience.
- Reframe the library as the study's published method, not as a product: vendored into the study repo as nemisis/, no PyPI package, no landing page, no pricing. It ships anyway at zero extra cost and avoids a comparison with swebench and mutmut that it loses.
- Update the competitor traction table in r2-ai-pr-verification-gate.md with 2026-08-30 numbers: jittest still 0 stars (pushed the same day, 223 real PyPI downloads in July), proofgate 0, proof-gate-action 0, codeguard-action 0, agent-delivery-gate 0, gauntlet 4, until-dev/plugins 28. A month of daily pushes has produced zero adoption for the closest clone.
- Flag the methodology caveat on every PyPI figure carried forward: these are raw platform counts on a day when requests read 1.69B/month. unidiff 58.3M/mo and swebench 44.5M/mo (against 5,736 stars) are CI/mirror-amplified and safe only for relative comparison. The only literal-safe number is jittest's 223 excluding mirrors, and it is safe because it is small.
- Record the session constraint in the research log: WebSearch was exhausted (200/200) before the first query, so the competitor set is complete for GitHub/PyPI/arXiv/HN and incomplete for the open web (vendor blogs, Lobsters, non-GitHub tooling unseen). Also record that ThemeCoder/RepairAgent 404s and no canonical RepairAgent repo could be located without search.

_Full report: session scratchpad `deepdives/c-nemisis-oss.md`._
