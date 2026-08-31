# Paid demand in agent governance — who pays, how much, for which shape | 2026-08-30 | demand-side-scout (Wave 1) | NOT instrument-biased (HN+GitHub = 13/56 citations = 23.2%)

## Summary (answers the question)

1. **Payroll is the only shape with observed, dated, dollar-denominated transactions.** Coder staffs a standing "AI Governance team"; LaunchDarkly staffs "AgentControl" at **$145,500–$263,670**; Notion pays **$270,000–$340,000** for guardrails-and-provenance work; Tulip pays **$130,000–$180,000** for it in Somerville, MA; Klaviyo pays **$148,000–$222,000** and **$160,000–$240,000**, Hi Marley **$152,000–$283,000**, all Boston.
2. **The AI-security vendor category has no public price at all.** Six of the ten AI-security vendors checked 404 their `/pricing` path outright (Lasso, Prompt Security, Zenity, HiddenLayer, Noma, Guardrails AI); the other four (Lakera, Invariant Labs, WhyLabs, MintMCP) serve a page with no price on it. Ten for ten, no public price exists. It is 100% contact-sales — an enterprise sales motion the principal cannot run.
3. **The one adjacent category with self-serve prices is agent PR review**: CodeRabbit **$24–48/user/mo** (+ **$40/user/mo** security tier, **$143M** raised), Greptile **$30/seat/mo**, Graphite **$20–40/user/mo**, Datadog Test Optimization **$8/committer/mo**.
4. **Federal procurement has bought none of it.** USAspending FY2025–2026-08-30: "AI governance", "AI code review", "generative AI guardrails", "AI guardrails", "prompt injection", "GitHub Copilot" → **0 awards each**; the same query returns $105k–$250k awards for SonarQube/Checkmarx. Category not yet in procurement language.
5. **Sponsorship pays ~nothing here.** gitleaks' and bandit's Open Collectives hold **$0**; the gitleaks maintainer has **9** GitHub sponsors. Sponsorship is not a revenue line for a security devtool.
6. **Regulation does not force it yet.** EU AI Act Arts. 12/14 apply from **2 Aug 2026** but only to *high-risk* systems; an internal coding agent is not one. The live forcing function is **SOC 2 CC8.1**, and it is a review-record demand, not a product demand.
7. **Closest to money of the five Wave-2 packages: `pkg-change-receipt`, then `pkg-egress-guard`.** Both have a named, funded, shipping buyer-side analogue; both are last and second in the release order.
8. **`pkg-plan-lint` is the weakest** — two priced competitors already sit at $25–29/user with ~zero traction; shipping it first is a distribution bet, not a demand bet.
9. **The honest read:** every dollar found flows to a salary or to a funded vendor. Nobody pays a solo maintainer for this shape. This is a second, independent instrument (ATS JSON, not Indeed) confirming DECISION.md §7's payroll finding.
10. **Implication for Track M:** the study is the only artifact here that a hiring manager at Coder/LaunchDarkly/Datadog would read, and those are the people with the budget.

---

*Note on job-post quotes: descriptions are served as HTML by the ATS APIs. Quotes below are the text after tag-stripping and whitespace normalisation; wording is unaltered. The raw JSON is reproducible with the curl commands in the instrument log.*

## 1. Job posts — hiring humans to do the manual thing

Method: `curl` against `boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true`, `api.ashbyhq.com/posting-api/job-board/<slug>`, `api.lever.co/v0/postings/<slug>?mode=json` for **114 slug/board combinations**, 2026-08-30. **44 boards resolved with ≥1 posting** (see instrument log); **6,244 postings retrieved**, then read for the governance reqs quoted below. (An earlier draft reported two keyword-filter counts here — title matches and body matches. This file publishes neither the phrase list nor the filter, so those counts are not reproducible from it and are **withdrawn as UNVERIFIED**. Nothing below depends on them: every posting cited in §1 is quoted from its own re-fetched JSON.)

### 1a. The single best-matched post: a vendor staffing a governance team around exactly `pkg-egress-guard`

**Coder — Staff Software Engineer (AI Governance)** — United States — published **2026-08-11** — no band published — https://jobs.ashbyhq.com/coder/b2779e7d-e280-420c-9fc1-eeb27900134a

> "This role sits on our AI Governance team, which builds and maintains two enterprise-grade components of Coder's AI governance stack. AI Gateway is a centralized LLM gateway that sits between coding agents and providers such as OpenAI or Anthropic, providing organizations with audit trails, token tracking, cost control, and centralized authentication. Agent Firewall wraps those agents with default-deny network policies, controlling which domains and methods they can reach inside workspaces."

> "Day to day, you'll be shipping features, hardening security boundaries, collaborating with enterprise customers on real-world policy needs, and contributing to Coder's open-source ecosystem."

Why this matters: "default-deny network policies … which domains and methods they can reach" is `pkg-egress-guard`'s spec, being built by a funded vendor with *enterprise customers with real-world policy needs*, staffed as a whole team, and priced at contact-sales (§2). Coder also runs four more "Agentic Engineering" reqs on the same board.

### 1b. A product line named for the category, with published bands

**LaunchDarkly — Engineering Manager, AgentControl** — Remote US — updated **2026-08-26** — **$163,000–$224,070 / $172,600–$237,270 / $191,800–$263,670** (three pay zones) — https://job-boards.greenhouse.io/launchdarkly/jobs/7977701003

> "LaunchDarkly's AgentControl team is on a mission to manage the complete software development lifecycle for shipping agents to production, from configuring to benchmarking to observing and beyond. … These systems enable customers to control, monitor, and optimize their agent's functionality."

**LaunchDarkly — Full Stack Engineer, AgentControl** — Remote US — updated **2026-08-14** — **$145,500–$200,090 / $154,100–$211,860 / $171,200–$235,400** — https://job-boards.greenhouse.io/launchdarkly/jobs/7750116003

### 1c. The `pkg-change-receipt` job description, written by someone else

**Datadog — Senior Platform Product Manager, AI SDLC Trusted Throughput** — New York, NY — https://careers.datadoghq.com/detail/7947683/?gh_jid=7947683

> "Drive systems that monitor and validate AI-generated or AI-attributed changes to ensure correctness, compliance, and trust"

> "Partner with engineering, infrastructure, security, and developer experience teams to build automated validation, auditability, and risk-scoring capabilities into deployment workflows"

> "As AI accelerates development velocity and system complexity, you will help evolve SDLC systems from human-supervised workflows to platforms with built-in safety, observability, and correctness guarantees."

This is the clearest statement found anywhere that a large buyer treats "validate AI-attributed changes" as a funded platform programme. It is being built **internally**, by a PM plus a platform team, not bought.

### 1d. Provenance named as a deliverable (twice, by the model vendors)

**Anthropic — Staff+ Software Engineer, Safeguards** — SF / NYC — updated **2026-08-21** — https://job-boards.greenhouse.io/anthropic/jobs/4951844008

> "We develop sandboxed agent architectures, brokered and audited data access, and provenance guarantees that keep humans firmly in control as model capabilities grow."

**OpenAI — Product Manager, Codex Security Controls & Partner Interfaces** — US Remote — published **2026-07-13** — https://jobs.ashbyhq.com/openai/97681dd5-65ad-4eb5-b692-e6d192871c38

> "This role focuses on securing Codex itself: how identity, permissions, tools, MCP servers, repositories, secrets, networks, and high-impact actions are governed across Codex products."

> "Audit trails, provenance, stop conditions, revocation, and rollback."

> "Evaluate risks such as permission bypass, prompt injection, malicious tools, secret exposure, cross-tenant access, stale authorization, partner outages, conflicting decisions, and incomplete audit evidence."

Note the direction of travel: **provenance and audit trails are becoming features of the agent vendors' own products.** That is the same erasure risk DECISION.md recorded for the B′ provenance thesis, arriving from the vendor side instead of the trailer side.

### 1e. Guardrails as a paid band

**Notion — Software Engineer, AI Security** — San Francisco — published **2026-06-09** — **$270,000–$340,000** — https://jobs.ashbyhq.com/notion/def3f337-5593-491c-b34d-e0b53f2a5cac

> "You'll turn product risks into clear architecture, reusable guardrails, automated tests, and production systems that help teams ship new features safely."

> "Define and build security architecture for product surfaces that operate across customer workspace content, including tool execution, content writes, retrieval, permission checks, provenance, and auditability."

### 1f. Boston / Massachusetts (relevant to the principal's geography)

| Company | Title | Location | Band | Date | URL |
|---|---|---|---|---|---|
| Tulip | AI Enablement Engineer – Developer Experience | **Somerville, MA** (hybrid 3+ days) | **$130,000–$180,000** | updated 2026-08-06 | https://tulip.co/careers/job-posting/?gh_jid=7820441003 |
| Fairmarkit | Agentic AI Engineer (Boston, Hybrid) | Boston | **"$336,000 -$350,000"** (verbatim; likely total comp — flagged) | updated 2026-07-13 | https://job-boards.greenhouse.io/fairmarkit/jobs/6111188004 |
| Klaviyo | Sr. Software Engineer, AI Enablement | Boston, MA | **$148,000–$222,000** ("Base Pay Range For US Locations", in the Greenhouse `content` payload) | updated 2026-08-26 | https://www.klaviyo.com/careers/jobs/7688416003 |
| Klaviyo | AI Enablement Program Manager | Boston, MA | **$160,000–$240,000** ("Base Pay Range For US Locations", in the Greenhouse `content` payload) | updated 2026-08-26 | https://www.klaviyo.com/careers/jobs/7801432003 |
| Hi Marley | Principal AI Platform Engineer | Hybrid – Boston, MA | **$152,000–$283,000** ("annual base salary", in the Greenhouse `content` payload) | updated 2026-08-25 | https://www.himarley.com/job-openings?gh_jid=7773706003 |

Tulip, verbatim: *"Build and maintain the internal agentic AI platform engineers rely on daily: skills, plugins, MCP servers, and integrations across our tech stack (source control, CI/CD, observability, ticketing, and more)"*.

Klaviyo Sr. SWE AI Enablement, verbatim: *"Act as a subject matter expert for AI-driven engineering tools, mentoring other engineers and championing a culture of AI-first development."* — **this reproduces, from Greenhouse JSON, the exact sentence Session 1 captured from Indeed** (`ideas/r2-agent-readiness-service.md` WTP table). The role is still open on 2026-08-30. **Session 1's $148,000–$222,000 figure IS re-confirmed today, from the Greenhouse `content` payload — a second instrument, not Indeed.** The band lives in the posting's description HTML: `Base Pay Range For US Locations: $148,000 — $222,000 USD`. (Greenhouse's separate structured `pay_input_ranges` field is empty, which is what an earlier draft of this file mistook for no band being published.) Re-fetched today from `boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true`, job `7688416003`, `updated_at 2026-08-26T11:10:55-04:00`.

Klaviyo AI Enablement Program Manager, verbatim: *"This role is based in our Boston office — and it's one of the most visible things we're building right now."* Band, same payload, job `7801432003`: `Base Pay Range For US Locations: $160,000 — $240,000 USD`. Hi Marley's Principal AI Platform Engineer (job `7773706003`, `boards-api.greenhouse.io/v1/boards/himarley/jobs?content=true`, `updated_at 2026-08-25T16:27:31-04:00`) publishes *"The annual base salary for this role is expected to fall within the range of [$152,000–$283,000]"*. **Four Boston-area bands, all re-fetched today** — the Massachusetts payroll evidence behind summary claims 1 and 9 is four posts deep, not one.

### 1g. Consultancy-shaped roles are being hired *by the vendors*, not bought from outsiders

**GitLab — Forward Deployed Engineer, AI and Agentic SDLC** — Remote US — https://job-boards.greenhouse.io/gitlab/jobs/8517171002

> "Engagements may range from a focused technical consultation to a long-running design partnership."

**Replit — Field Engineer** — Foster City, CA — published **2025-07-26**, six days after Replit's production-database incident (§4) — https://jobs.ashbyhq.com/replit/2c1463ab-05a4-482a-a605-013403a41e80

> "Enterprise Governance: You own the 'Guardrails' mission. You configure workspace policies and AI governance templates that solve for data safety, compliance, and CISO approval."

> "Context & Connectivity (MCP): You write and deploy Model Context Protocol (MCP) servers to securely connect Replit Agents to customer-specific data, making Replit the central hub for their internal development."

This is the incident→control→hire chain in one document, and the control was **built and staffed, not purchased**.

### 1h. HN "Who is hiring?" — a real negative

`hn.algolia.com/api/v1/search_by_date?tags=comment,story_49156683&hitsPerPage=1000`, fetched 2026-08-30. Story: "Ask HN: Who is hiring? (August 2026)", https://news.ycombinator.com/item?id=49156683, 2026-08-03, 386 comments.

Keyword census over all 386 comments: `agent` 59, `compliance` 16, `mcp` 5, `guardrail` 3, `soc 2` 3, `code review` 2, `ai governance` 1, **`provenance` 0, `prompt injection` 0, `ai security` 0**.

Startups hiring on HN are not hiring for agent governance. The demand is concentrated in mid/large platform vendors whose reqs live on ATS boards. The only priced engagement-shaped comment in the thread is a company hiring contractors:

> "CONTRACT, PROJECT-BASED ($50-$150/hr). For people who already have the domain. A scoped first project, typically three to six weeks."
> — Arcforma AI's own hiring comment, https://news.ycombinator.com/item?id=49248055, 2026-08-10

$50–150/hr for scoped 3–6 week AI-build projects is the observed market rate for the *service* shape — meaningfully below the $2,000/two-weeks the `r2-agent-readiness-service` dossier hypothesised, once hours are counted.

---

## 2. Pricing pages, verbatim (all fetched 2026-08-30 by `curl -A "venture-research/2 …"`)

### 2a. AI-security vendors: no public price exists

| Vendor | `/pricing` | Result |
|---|---|---|
| Lasso Security | https://www.lasso.security/pricing | **HTTP 404** |
| Prompt Security | https://www.prompt.security/pricing | **HTTP 404** |
| Zenity | https://zenity.io/pricing | **HTTP 404** |
| HiddenLayer | https://hiddenlayer.com/pricing | **HTTP 404** |
| Noma Security | https://noma.security/pricing | **HTTP 404** |
| Guardrails AI | https://www.guardrailsai.com/pricing | **HTTP 404** |
| Lakera | https://www.lakera.ai/pricing | 200, 3,635-byte stub, no price strings |
| Invariant Labs | https://invariantlabs.ai/pricing | 200, no price strings |
| WhyLabs | https://whylabs.ai/pricing | 200, no price strings |
| MintMCP | https://mintmcp.com/pricing | 200, no price strings (matches the verifier note in `ideas/r2-agent-guardrails-per-repo.md`) |

Six of the ten AI-security vendors checked 404 their `/pricing` path outright; the other four serve a page with no price on it. **Ten for ten, no public price exists** — and that is the finding: **this category does not sell self-serve.** "Contact sales" is a data point, and the data point says the buying motion is a procurement cycle with a security team, a SOC 2 questionnaire and a DPA — not something an unincorporated solo maintainer can transact.

### 2b. Agent PR review / code-change control — self-serve prices exist here

**CodeRabbit** — https://www.coderabbit.ai/pricing
> "We raised $143M to build the control layer for software change"
> "Pro Pull Request Reviews & Insights $24 /mo/user Billed annually"
> "$48 /mo/user Billed annually All Pro plan features Multi-repo analysis Custom pre-merge checks"
> "CodeRabbit Security $40 /mo/user Continuous security monitoring of your repositories Security review of each PR"
> "CodeRabbit Agent for Slack Pay only for what you use: $0.50 per agent minute"

**Greptile** — https://www.greptile.com/pricing
> "Pro is $30 per seat per month and includes 50 credits per seat."
> "One standard review uses 1 credit, one TREX review uses 3 credits, and additional credits are $1 each"
> "Enterprise Best for organizations at scale Custom pricing"
> "50% off for early-stage startups Pre-Series A startups with under $2M revenue in the past 12 months get 50% off"

Greptile's own nav names two products in this dossier's category: **"TREX: Runtime Validation Beta"** and **"Agent Independence Security Review"**.

**Graphite** — https://graphite.dev/pricing — "$ 20 … Per user/month, billed annually"; "$ 40 … Per user/month, billed annually"

**Datadog** — https://www.datadoghq.com/pricing/?product=llm-observability — Test Optimization: "Starting At $ 8 Per committer, per month*"; "*Billed annually or $ 12 on-demand". (Datadog's LLM Observability per-span rate could not be isolated from the shared JS pricing table — **UNVERIFIED**.)

**Snyk** — https://snyk.io/plans/ — "$0 / month per contributing developer"; "Starting at $25 / month per contributing developer"; "Ignite … Starting at $1,260 / year per contributing developer"; top tier "Contact Sales for pricing".

### 2c. Policy / audit / network control sold as an enterprise upsell

**Coder** — https://coder.com/pricing — the page names **"AI Gateway"** and **"Agent Firewall"** as features and carries no dollar figure:
> "Coder Premium offers enhanced security, scalability, and governance features"
> "Get pricing or request a demo to get started."

**Cursor** — https://cursor.com/pricing — "Teams $40 / user / mo"; Enterprise = "Contact Sales", listing "audit logs and service accounts" and an "AI code tracking API". (Reproduces Session 1's capture.)

**GitHub** — https://github.com/pricing — Enterprise "Starting at $ 21 USD per user/month". Copilot plans (https://github.com/features/copilot/plans): "Pro $10 per month", "Pro+ $39 per month", "Max $100 per month", "1 AI credit = $0.01 USD".

**LaunchDarkly** — https://launchdarkly.com/pricing/ — the AgentControl meter is published:
> "Add-on AI Run blocks — $5 / 1000"
> "$5 per additional 1k runs"
> "$10 per Service Connection / mo"

**grith** — https://grith.ai/pricing — "Pro $25 /user/month For teams that need centralised control, project analytics, and verifiable evid[ence]"; "Enterprise Custom Contact us For organisations with compliance and scale requirements"; "Air-gapped deployment (planned)". The phrase *"verifiable evidence"* in a $25/user tier is the closest priced analogue to `pkg-change-receipt` found anywhere.

**Anthropic / Claude** (https://claude.com/pricing) and **Veto** (https://www.vetoapp.io/) render prices via JS and did not yield strings to `curl`; Session 1's captures in `ideas/r2-agent-guardrails-per-repo.md` stand and are not re-derived here.

**Price-shape conclusion:** every observed price in this category is **per user or per seat, $20–48/month**, or **usage-metered** ($0.50/agent-minute, $5/1,000 runs, $1/credit). **No vendor prices per repo.** The per-repo $50–200/mo assumption in `r2-agent-guardrails-per-repo` has no market precedent and one strong counter-argument (that file's own closing paragraph).

---

## 3. RFPs and procurement

**SAM.gov: unusable, ethically and technically.** `https://sam.gov/robots.txt` (fetched 2026-08-30) contains `Disallow: /search/`, which is exactly the public-search path the task named. The keyless API endpoint `https://api.sam.gov/prod/opportunities/v2/search?…` returns **HTTP 404**; the documented endpoint requires an API key, which requires an account — a RED action. **SAM.gov is therefore recorded as blocked-by-robots + needs-auth and was not scraped.**

**USAspending.gov is public, keyless, and answers the question.** `POST https://api.usaspending.gov/api/v2/search/spending_by_award/`, award types A/B/C/D, `time_period` 2025-01-01 → 2026-08-30, fetched 2026-08-30:

| Keyword | Awards returned |
|---|---|
| "artificial intelligence governance" | **0** |
| "AI code review" | **0** |
| "generative AI guardrails" | **0** |
| "AI guardrails" | **0** |
| "prompt injection" | **0** |
| "large language model security" | **0** |
| "GitHub Copilot" | **0** |

Control queries against the same endpoint and window prove the instrument works and show what the adjacent category *does* buy:

- "artificial intelligence" → ECS Federal, **$120,575,059.35**, "RESEARCH AND DEVELOPMENT EFFORT TO DESIGN AND DEVELOP PROTOTYPES TO ARTIFICIAL INTELLIGENCE/MACHINE …"
- "static application security testing" → ResolveSoft, **$249,987.25**, "SONARQUBE-STATIC APPLICATION SECURITY TESTING (SAST) TOOL, DESIGNED TO ANALYZE SOURCE CODE TO FIND S…"; ThunderCat, **$168,273.71**, Checkmarx renewal for NOAA/NCEI; AccessAgility, **$105,419.00**, SonarQube
- "GitHub Enterprise" → 4 Star Technologies, **$228,516.84**, "GITHUB ENTERPRISE SOFTWARE LICENSE"

**Reading:** government buys *named, established commercial products* in the code-scanning line at **$105k–$250k per award**. It has not yet written a single award description containing the words this category uses. A federal or state RFP is not a 2026 revenue path for this product; it is a 2028 one, and only for a vendor with FedRAMP-shaped compliance.

State/university RFPs: not searched — the two general RFP aggregators are login-walled and the state portals 403 non-browsers per `CLAUDE.md` §6. Recorded as **not attempted** rather than "none found".

---

## 4. Incident postmortems — and whether a control was *bought*

| Incident | Date | Source (fetched 2026-08-30) | Control added, verbatim | Bought? |
|---|---|---|---|---|
| Replit agent deletes a production database during a code freeze | 2025-07-20 | https://news.ycombinator.com/item?id=44625119 (143 pts); https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/ (via https://news.ycombinator.com/item?id=44632575) | Replit's CEO: *"Replit agent in development deleted data from the production database. Unacceptable and should never be possible…We heard the 'code freeze' pain loud and clear. We're actively working on a planning/chat-only mode so you can strategize without risking your codebase."* — https://fortune.com/2025/07/23/ai-coding-tool-replit-wiped-database-called-it-a-catastrophic-failure/, 2025-07-23. Fortune paraphrases the rest: *"updates included the rollout of automatic separation between development and production databases, improvements to rollback systems, and the development of a new 'planning-only' mode."* | **No.** Vendor built it free, and hired a Field Engineer to "own the 'Guardrails' mission" six days later (§1g). |
| Gemini CLI hallucinates and deletes a user's files | 2025-07-22 | https://news.ycombinator.com/item?id=44651485 (304 pts), linking the affected user's own writeup | Not verified in this pass — **UNVERIFIED** | Unknown |
| Google Antigravity deletes the contents of a drive | 2025-11-30 / 2025-12-01 | https://news.ycombinator.com/item?id=46103532 (544 pts), https://news.ycombinator.com/item?id=46103811 (44 pts) | Not verified in this pass — **UNVERIFIED**; the linked venues (reddit, mastodon) 403 non-browsers per §6 | Unknown |

**The pattern is the finding.** In the one case traced end to end, a high-profile agent incident produced (a) free product controls shipped by the vendor and (b) a salaried headcount at the vendor. It produced no purchase order. Three Show HN launches of exactly the paid control — *"Vectimus – Cedar policy enforcement for AI coding agents"* (https://news.ycombinator.com/item?id=47525283, 2026-03-26, **3 points**), *"Trollbridge – let your agent run YOLO but without the whole internet"* (https://news.ycombinator.com/item?id=48850008, 2026-07-09, **1 point**), *"Do-over, undo for AI agent shell commands"* (https://news.ycombinator.com/item?id=49371211, 2026-08-20, **2 points**) — show **no launch traction observed on HN** for exactly the paid control this dossier is about. HN points measure launch attention, not adoption: §8's incumbent test asks for stars velocity, downloads, issue/PR activity and last release, none of which this file measured, and `research/adoption.md` carries no entry for these three projects. **The zero-adoption classification is therefore not made here — it is handed to `adoption-analyst`.** What this file's own evidence supports is narrower and still holds: nobody has converted the incident anger into a purchase.

---

## 5. Regulation and standards

**EU AI Act (Regulation (EU) 2024/1689), fetched today from the primary source:** https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689

Article 12 (Record-keeping), verbatim:
> "High-risk AI systems shall technically allow for the automatic recording of events (logs) over the lifetime of the system."

Article 14 (Human oversight), verbatim:
> "High-risk AI systems shall be designed and developed in such a way, including with appropriate human-machine interface tools, that they can be effectively overseen by natural persons during the period in which they are in use."

Article 113 (Entry into force and application), verbatim:
> "It shall apply from 2 August 2026. However: (a) Chapters I and II shall apply from 2 February 2025; (b) Chapter III Section 4, Chapter V, Chapter VII and Chapter XII and Article 78 shall apply from 2 August 2025, with the exception of Article 101; (c) Article 6(1) and the corresponding obligations in this Regulation shall apply from 2 August 2027."

**Operative limit, stated plainly:** both articles begin "High-risk AI systems shall…". An internal coding agent writing application code is not an Annex III high-risk use. **The EU AI Act does not, today, force logging or oversight on a coding agent.** Anyone selling `pkg-change-receipt` on an AI-Act compliance story would be overclaiming, and `CLAUDE.md` §2 forbids that. (Whether the Digital Omnibus moves the 2026-08-02 date for Annex III is **UNVERIFIED** — not checked in this pass.)

**SOC 2 CC8.1 is the live forcing function, and it is a review-record demand.** The most on-point statement found is a consultancy playbook page — *not* auditor guidance, and labelled as such: https://thebrightbyte.com/playbook/expertise/ai-coding-agents-soc2, published 2026-04-27, publisher The BrightByte:

> "A human who is not the change author has to approve the merge."

The same page's auditor checklist: *"Pull a sample of 10 production commits and identify which were AI-assisted"* and *"Show the review record for each AI-assisted commit, including reviewer identity."* It recommends a commit trailer of the form `AI-Assisted: Cursor 0.45 / claude-3.7-sonnet`.

**What that means for the product:** the demand SOC 2 creates is satisfiable by a CODEOWNERS file, a PR template and a branch-protection rule — all free, all already shipped by GitHub. It creates demand for *evidence*, not for a *runtime guard*. And a trailer-based signal is erasable, which is precisely the objection that killed B′ (`DECISION.md` §7). **Do not re-open the provenance thesis on this evidence.**

**NIST AI RMF / Generative AI Profile (NIST AI 600-1) and ISO/IEC 42001: not fetched in this pass — recorded as not attempted**, because on the evidence above they would change the conclusion only if a buyer were citing them in a purchase, and no such purchase was found in §3.

---

## 6. What sponsorship pays in this category

Open Collective public JSON (`https://opencollective.com/<slug>.json`, fetched 2026-08-30; `balance`/`yearlyIncome` are in **cents**):

| Collective | Balance | Yearly income | Backers |
|---|---|---|---|
| **gitleaks** | **$0.00** | **$0.00** | **0** |
| **bandit** | **$0.00** | **$0.00** | **0** |
| semgrep, pip-audit, ruff, litellm, pyup | — | — | "Not found" (no collective) |
| babel | $197,209.67 | $259,978.49 | 1,258 |
| webpack | $89,805.91 | $184,470.31 | 2,772 |
| vuejs | $43,152.34 | $189,938.00 | 871 |

GitHub Sponsors, via `gh api graphql` (read-only), 2026-08-30 — sponsor **counts** are public, income is not (`monthlyEstimatedSponsorsIncomeInCents` returns 0 for every account queried, i.e. owner-only):

| Account (role) | Sponsors | Listing? |
|---|---|---|
| the solo maintainer of gitleaks | **9** | yes |
| a very widely-followed solo Python/devtool maintainer | 487 | yes |
| the solo maintainer of FastAPI | 119 | yes |
| pydantic (org) | 12 | yes |
| astral-sh, guardrails-ai, invariantlabs-ai, NVIDIA | 0 | **no sponsors listing at all** |

**Conclusion:** the two closest comparables — a widely-deployed solo-maintained secret scanner and a widely-deployed Python security linter — raise **$0/year** through Open Collective, and the gitleaks maintainer has **nine** sponsors. Six-figure OSS income requires framework-scale adoption (Babel, webpack, Vue), which is two orders of magnitude beyond anything the Wave-2 packages can reach by 2026-11-30. **Sponsorship should be modelled at $0 and treated as a signal channel, not a revenue line.** This does not kill Track S — it kills sponsorship as Track S's *money* story, leaving inbound and career capital.

---

## 7. Budget map

**Confidence key:** **H** = a dated dollar figure re-fetched today from a primary source; **M** = a named buyer with no published price; **L** = inference from adjacent evidence only.

| Shape | Who pays | Price / salary evidence (URL, 2026-08-30) | Conf. |
|---|---|---|---|
| Agent network/egress control (`pkg-egress-guard`) | Platform vendors, as **payroll**; their enterprise customers, at contact-sales | Coder staffs an AI Governance team building "Agent Firewall … default-deny network policies" (jobs.ashbyhq.com/coder/b2779e7d…); coder.com/pricing has **no number**, "request a demo"; grith Pro **$25/user/mo**; Cursor Enterprise "Auto-run, browser, and network controls" = contact sales | **H** for payroll; **L** for self-serve |
| Verification / receipts for AI-authored changes (`pkg-change-receipt`) | Large eng orgs, as **payroll**; SMB teams, via **PR-review seats** | Datadog PM req: "monitor and validate AI-generated or AI-attributed changes" (careers.datadoghq.com/detail/7947683); CodeRabbit **$24–48/user/mo** + **$40/user/mo** security, **$143M raised** (coderabbit.ai/pricing); Greptile **$30/seat/mo**; Datadog Test Optimization **$8/committer/mo**; grith Pro **$25/user/mo** for "verifiable evid[ence]" | **H** |
| Agent PR review as a seat | Eng teams, self-serve, today | Four vendors with published seat prices, $8–48/user/mo, one with $143M behind it | **H** |
| Policy/plan static validation (`pkg-plan-lint`) | Nobody observed paying separately | Veto **$29–99/user/mo** and grith **$25/user/mo** both bundle it; both HN launches scored 1 point (Session 1's captures) | **L** |
| Read-only MCP gateway (`pkg-readonly-gateway`) | Enterprises, contact-sales only | MintMCP: per-user licensing, **no published number** (mintmcp.com/pricing); Coder "AI Gateway" inside Premium, no number | **M** |
| Agent-readiness report (`pkg-agent-autopsy`) | Nobody, as a product; adjacent services bill hourly | Arcforma AI: **"$50-$150/hr"**, 3–6 week scoped projects (news.ycombinator.com/item?id=49248055); GitLab and Replit hire this as FDE/Field Engineer payroll | **L** as product, **M** as lead magnet |
| The whole capability, as a salary | Coder, LaunchDarkly, Notion, Datadog, Anthropic, OpenAI, Tulip, Klaviyo, Hi Marley, Fairmarkit | **$130,000–$180,000** (Tulip, Somerville MA); **$148,000–$222,000** (Klaviyo Sr. SWE AI Enablement, Boston); **$160,000–$240,000** (Klaviyo AI Enablement PM, Boston); **$152,000–$283,000** (Hi Marley Principal AI Platform Engineer, Boston); **$145,500–$263,670** (LaunchDarkly AgentControl); **$270,000–$340,000** (Notion AI Security); **"$336,000 -$350,000"** (Fairmarkit, Boston) | **H** |
| The capability, as a federal contract | Nobody, yet | 7/7 category keywords return **0 awards** on USAspending FY2025→2026-08-30; SAST comparators run $105k–$250k | **H** (as a negative) |
| The capability, as sponsorship | Nobody | gitleaks & bandit collectives: **$0**; 9 sponsors on the gitleaks maintainer | **H** (as a negative) |

---

## 8. Implications

### For each Wave-2 package

- **`pkg-plan-lint` (shipping first).** Weakest budget evidence of the five. Two priced competitors bundle it at $25–29/user and neither has traction. Keep it first — it is the fastest asset and the release-cadence proof — but **do not attach a revenue story to it.** Its gate stays the §9 adoption gate (50 stars / 500 downloads / 3 stranger issues), which is the right gate for a package with no observed buyer.
- **`pkg-egress-guard`.** The strongest *named-competitor* signal: Coder ships "Agent Firewall … default-deny network policies" and staffs a team for it, published 19 days ago. Under §8's incumbent test that is **active-small and well-funded, but enterprise-only and unpriced** — the category is open at the self-serve end, which is exactly where an installable package lives. Concrete recommendation: the README's comparison page must name Coder Agent Firewall, grith and Cursor Enterprise's network controls honestly, and position on *"works in your CI, no gateway to run, no seat to buy."*
- **`pkg-agent-autopsy`.** No budget as a product; strong as the inbound instrument, which is what §5 already calls it. The only observed price for the service it replaces is **$50–150/hr contract work**, not $1,500–3,000 fixed-price — one more nail in `r2-agent-readiness-service`'s pricing hypothesis, from a new instrument.
- **`pkg-readonly-gateway`.** Real buyers (MintMCP has enterprise customers), zero public price, per-user licensing. Medium confidence, and a long build. No reason to move it earlier.
- **`pkg-change-receipt`.** **Closest of the five to money.** A named PM at Datadog is funded to "monitor and validate AI-generated or AI-attributed changes"; grith already charges $25/user/mo for "verifiable evidence"; the SOC 2 CC8.1 evidence demand is real and dated. But it is last in the order and the largest build, and its buyer is an enterprise with an auditor. **Recommendation: do not reorder the releases** (the §9 cadence gate matters more), but write `pkg-change-receipt`'s README against the CC8.1 evidence question — *"show the review record for each AI-assisted commit"* — rather than against an EU AI Act story that Article 12's own first six words defeat.

### For the study (Track M)

The people with budget in this category are the hiring managers behind the Coder, LaunchDarkly, Datadog, Notion and OpenAI reqs quoted above. A published measurement of *how often agent-PR tests are non-discriminating* is directly addressed to them, is citable in the exact language their reqs use ("validate AI-generated or AI-attributed changes", "correctness, compliance, and trust"), and is the one artifact here that neither payroll nor a funded vendor already owns. **Track M's audience is now evidenced, not assumed.** Its distribution list, when `launch-kit-writer` builds one, should include the vendors named in §1 rather than only HN.

### For the plan as a whole

Three independent instruments now say the same thing. Session 1's Indeed search, `DECISION.md` §7's red team, and today's ATS-JSON sweep all find the market buying this capability as **salary** and not as a **service or a package**. §3 and §6 close the two remaining escape hatches: no procurement money, no sponsorship money. That is not an argument to stop shipping — the packages are the credential that makes the payroll route real, and the §9 gates already treat them that way. It is an argument to stop looking for a paid *product* buyer before the re-open rule fires, exactly as `CLAUDE.md` §7's Track P specifies.

---

## Instrument log

**Venues and APIs tried, 2026-08-30. Identified as `curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)"` throughout.**

| Venue / API | Result |
|---|---|
| `boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true` (55 probes) | **reachable**; **24** resolved with jobs: anthropic 571, vercel 91, datadog 454, stripe 575, klaviyo 143, toast 312, cargurus 54, tulip 75, himarley 11, fairmarkit 7, everquote 12, cleargov 7, gitlab 220, databricks 856, figma 163, brex 294, airtable 16, netlify 2, grafanalabs 134, elastic 340, circleci 4, launchdarkly 51, jfrog 44, chainguard 86. hubspot 200/0 jobs. 404: openai, cursor, anysphere, cognition, replit, sourcegraph, github, snyk, shopify, wayfair, chewy, draftkings, rapid7, suno, jellyfish, cloudzero, reprise, kodex, lumafield, notion, linear, ramp, plaid, retool, render, hashicorp, docker, sentry, harness, wiz |
| `api.ashbyhq.com/posting-api/job-board/<slug>` (41 slugs) | **reachable**; **19** resolved: openai 754, cursor 121, cognition 89, replit 71, suno 62, jellyfish 6, cloudzero 15, reprise 1, kodex 5, notion 133, linear 29, ramp 139, plaid 102, render 33, sentry 42, coder 26, graphite 7, greptile 18, coderabbit 53. snyk & wiz 200/0. 404: anysphere, sourcegraph, shopify, wayfair, chewy, draftkings, rapid7, lumafield, retool, harness, windsurf, codeium, lakera, zenity, hiddenlayer, noma, promptsecurity, protectai, galileo, arize |
| `api.lever.co/v0/postings/<slug>?mode=json` (18 slugs) | **reachable**; **1** resolved (lumafield 16). 17× 404 |
| `hn.algolia.com/api/v1/search`, `/search_by_date` | **reachable**; whoishiring stories + 386-comment and 428-comment trees pulled in full |
| `api.usaspending.gov/api/v2/search/spending_by_award/` (POST, 10 queries) | **reachable**, keyless; 7 category keywords → 0 awards, 3 control keywords → results |
| `sam.gov/robots.txt` | reachable; **`Disallow: /search/`** — the public search path is **blocked by robots** and was not fetched |
| `api.sam.gov/prod/opportunities/v2/search` (keyless) | **404 / needs-auth** (API key requires an account = RED). Not pursued |
| `eur-lex.europa.eu` (Reg. (EU) 2024/1689 full HTML) | **reachable**, 1.26 MB |
| `artificialintelligenceact.eu` articles 12/14/timeline | reachable but **unusable** — inline glossary tooltips are interleaved into the article text, corrupting any quote. Superseded by EUR-Lex |
| `opencollective.com/<slug>.json` (10 slugs) | **reachable**; 5 resolved, 5 "Not found" |
| `gh api graphql` (sponsors, read-only, authenticated as Alex-lop) | **reachable**; sponsor counts public, `monthlyEstimatedSponsorsIncomeInCents` returns 0 for all (owner-only field) |
| Pricing pages via `curl` (23 URLs) | 17× 200, **6× 404** (lasso.security, prompt.security, zenity.io, hiddenlayer.com, noma.security, guardrailsai.com). JS-only (200 but no price strings): lakera.ai, invariantlabs.ai, whylabs.ai, mintmcp.com, claude.com, vetoapp.io, coder.com |
| WebSearch | 2 calls (SOC 2 CC8.1 + AI code; Replit CEO response). 198 of ~200 budget unspent |
| WebFetch | 2 calls (fortune.com; thebrightbyte.com) |
| LinkedIn | **not attempted** — login-walled, off-limits per the task |
| Indeed | **not attempted** this pass; Session 1's captures cited as Session-1 evidence, not re-derived |
| reddit.com, G2, TrustRadius, state RFP portals | **not attempted** — 403 to non-browsers per `CLAUDE.md` §6 |
| NIST AI RMF / GenAI Profile, ISO/IEC 42001, SEC/FTC guidance | **not attempted** — time-boxed out; see §5 for why the conclusion does not turn on them |

**Citations by host.** Machine-counted from this file: `grep -oE 'https?://[^ )|`"]+' demand.md | sort -u` → **56 distinct URLs**, of which one is the User-Agent string `+https://github.com/Alex-lop/venture` and not a citation → **55 cited URLs**, plus one API cited without a scheme (`hn.algolia.com/api/v1/...`) = **56**.

| Host | Count |
|---|---|
| news.ycombinator.com | 10 |
| hn.algolia.com (cited without scheme) | 1 |
| job-boards.greenhouse.io | 5 |
| jobs.ashbyhq.com | 4 |
| github.com (citations only; the UA string excluded) | 2 |
| www.klaviyo.com | 2 |
| careers.datadoghq.com, tulip.co, www.himarley.com | 3 |
| www.coderabbit.ai, www.greptile.com, graphite.dev, coder.com, launchdarkly.com, cursor.com, snyk.io, www.datadoghq.com, grith.ai, mintmcp.com, claude.com, www.vetoapp.io | 12 |
| www.lasso.security, www.prompt.security, zenity.io, hiddenlayer.com, noma.security, www.guardrailsai.com, www.lakera.ai, invariantlabs.ai, whylabs.ai (404 or JS-empty) | 9 |
| eur-lex.europa.eu | 1 |
| thebrightbyte.com | 1 |
| api.usaspending.gov | 1 |
| sam.gov, api.sam.gov | 2 |
| fortune.com | 1 |
| www.theregister.com | 1 |
| opencollective.com | 1 |

**HN + GitHub share: (10 + 1) + 2 = 13 / 56 = 23.2%.** Well below the 70% threshold. **This file is NOT instrument-biased**, and its conclusions are held at their stated confidence. The dominant instrument here is ATS job-board JSON (6 hosts, 15 citations, 26.8%) — ahead of HN, and the instrument Session 1 lacked entirely.

**Not verified / open:** Datadog LLM Observability per-span price; whether the EU Digital Omnibus moves the 2026-08-02 Annex III date; the controls added after the Gemini CLI and Antigravity incidents; whether Fairmarkit's "$336,000 -$350,000" is base or total compensation; §1's two withdrawn keyword-match counts (**UNVERIFIED** — not reproducible without re-running the 6,244-posting sweep; nothing depends on them); whether the three Show HN projects in §4 have any adoption at all (`adoption-analyst`'s call, not this file's).

---

## Verification (2026-08-30, quote-verifier)

Method: every URL in the body re-fetched today with `curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)"`; every `gh api` claim re-run read-only; every USAspending query re-POSTed with the same filters; every verbatim string tested with an exact `in` match against the tag-stripped, whitespace-normalised source. Quote characters (`'` vs `’`, `"` vs `“`) were normalised before matching and a difference in those alone is **not** counted a mismatch — a difference in *words* is. The file has 90 discrete checkable assertions; **all were checked** (no sampling needed under the 60-citation rule for load-bearing items, and the sub-60 URL count let me do the rest too), except one noted UNCHECKED below.

**Totals: 90 checked — 83 VERIFIED, 6 MISMATCH, 0 UNREACHABLE, 1 UNCHECKED.**

### Mismatches (the only things that need fixing)

| # | Claim in the body | Actual, re-fetched 2026-08-30 | Verdict |
|---|---|---|---|
| M1 | §1f table: Klaviyo *Sr. Software Engineer, AI Enablement* band "not in the Greenhouse JSON" | `boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true`, job `7688416003`, `content` field: `Base Pay Range For US Locations: $148,000 — $222,000 USD`. Updated `2026-08-26T11:10:55-04:00` | **MISMATCH** |
| M2 | §1f narrative: "Session 1's $148,000–$222,000 figure is *not* re-confirmed here: the Greenhouse payload carries no compensation field." | It **is** re-confirmed. The band is inside the posting's `content` HTML (Greenhouse's structured `pay_input_ranges` is separate and empty; the author appears to have checked only the structured field). Session 1's number reproduces **exactly** from a second instrument | **MISMATCH — and it strengthens the file** |
| M3 | §1f table: Klaviyo *AI Enablement Program Manager* band "not in the Greenhouse JSON" | Job `7801432003` `content`: `Base Pay Range For US Locations: $160,000 — $240,000 USD`. Updated `2026-08-26T11:10:55-04:00` | **MISMATCH** |
| M4 | §1f table: Hi Marley *Principal AI Platform Engineer* band "not published", date "—" | Job `7773706003` `content`: "The annual base salary for this role is expected to fall within the range of [$152,000–$283,000]". Updated `2026-08-25T16:27:31-04:00` | **MISMATCH** |
| M5 | §2b, presented as a verbatim blockquote: *"Greptile Pro is $30 per seat per month and includes 50 credits per seat"* | The page's FAQ reads: **"Pro is $30 per seat per month and includes 50 credits per seat."** The word *Greptile* is not in the sentence. The **number is right**; the quote is not verbatim | **MISMATCH (paraphrase as quote)** |
| M6 | Instrument log: "**56 distinct URLs** … = **57**"; "HN + GitHub share: 14 / 57 = **24.6%**" | 56 distinct URLs reproduce, but one of the three `github.com` hits is the **User-Agent string** `+https://github.com/Alex-lop/venture`, not a citation. Corrected: **55 cited URLs + 1 schemeless (`hn.algolia.com`) = 56**; HN + GitHub = 10 + 1 + 2 = **13 / 56 = 23.2%** | **MISMATCH (immaterial)** |

Also flagged, not counted as mismatches: the Fairmarkit source says the band is "(including a bonus)", which upgrades the file's "likely total comp — flagged" from a guess to a fact; Datadog's actual title is "Senior Platform Product Manager **-** AI SDLC Trusted Throughput" (hyphen, not comma); Tulip's is "AI Enablement Engineer**-** Developer Experience"; the Coder line *"Get pricing or request a demo to get started."* is the page's `<meta name="description">`, not body copy; Cursor's page capitalises *"Audit logs and service accounts"*; the Replit source uses double quotes around **"Guardrails"** where the body renders single.

### The other 84 assertions — all VERIFIED today

- **Job posts.** Coder `b2779e7d…` — title *Staff Software Engineer (AI Governance)*, United States, `publishedAt 2026-08-11`, **both blockquotes exact**; and the board carries **exactly four** further "(Agentic Engineering)" reqs, as claimed. LaunchDarkly EM `7977701003` → **$163,000 / $172,600 / $191,800 – $224,070 / $237,270 / $263,670**; FSE `7750116003` → **$145,500 / $154,100 / $171,200 – $200,090 / $211,860 / $235,400**; both AgentControl sentences exact. Datadog `7947683` — **all three bullets exact**. Anthropic Safeguards, OpenAI Codex PM (`publishedAt 2026-07-13`, all three quotes), Notion AI Security (`publishedAt 2026-06-09`, band **$270,000–$340,000** present in the description, both quotes), Tulip (**$130,000–$180,000**, Somerville MA, updated 2026-08-06, quote exact), Klaviyo SWE + PM quotes, GitLab FDE quote, Replit Field Engineer (`publishedAt 2025-07-26`, both quotes) — **exact**. The "six days after" arithmetic (2025-07-20 → 2025-07-26) checks.
- **HN.** Story `49156683` = *Ask HN: Who is hiring? (August 2026)*, 2026-08-03, **386 descendants**. The 10-term keyword census re-ran over all 386 comments from the same Algolia endpoint and reproduced **every count exactly**: agent 59, compliance 16, mcp 5, guardrail 3, soc 2 3, code review 2, ai governance 1, provenance 0, prompt injection 0, ai security 0. The contract-rate quote is **verbatim**, and item `49248055`'s `parent` is `49156683`, confirming it sits in that thread. Show HN scores today: **3 / 1 / 2**. Incident stories: **143 / 304 / 544 / 44** points — all exact.
- **Pricing.** **6/6 404s reproduce** (lasso.security, prompt.security, zenity.io, hiddenlayer.com, noma.security, guardrailsai.com). Lakera returns **200 at exactly 3,635 bytes** with no `$` string; invariantlabs.ai, whylabs.ai and mintmcp.com return 200 with **zero** price-like strings (MintMCP's "Per-user licensing based on active AI agent users" is present, with no number). CodeRabbit's five strings, Greptile's other four, Graphite's `$ 20`/`$ 40`, Datadog's `$ 8` committer + `$ 12` on-demand, Snyk's four tiers, Coder's Premium line and its "AI Gateway"/"Agent Firewall" feature names, Cursor's `$40` Teams + "AI code tracking API" + "Auto-run, browser, and network controls", GitHub's `$ 21`, Copilot's `$10/$39/$100` + `1 AI credit = $0.01 USD`, LaunchDarkly's three AgentControl meters, and grith's four strings — **all found verbatim**.
- **Procurement.** `sam.gov/robots.txt` line 55 is `Disallow: /search/`. `api.sam.gov/prod/opportunities/v2/search` → **404**. All **seven** category keywords return **0 results** on `spending_by_award` for A/B/C/D over 2025-01-01→2026-08-30. Controls reproduce to the cent: ECS Federal **$120,575,059.35**; ResolveSoft **$249,987.25** (SonarQube SAST); ThunderCat **$168,273.71** (description confirms *"RENEWAL OF CHECKMARX CXSAST"* for NCEI); AccessAgility **$105,419.00** (SonarQube); 4 Star Technologies **$228,516.84** *"GITHUB ENTERPRISE SOFTWARE LICENSE"*. The $105k–$250k band is the correct read of the full result set.
- **Regulation.** EUR-Lex returns **1,264,454 bytes**; the Article 12, Article 14 and Article 113 quotes are **verbatim**, and the surrounding text confirms the article numbers are attributed correctly (each quote is the first sentence under its own "Article 12 Record-keeping" / "Article 14 Human oversight" heading). The BrightByte page's `datePublished` is **2026-04-27** and all three of its quoted lines are exact.
- **Sponsorship.** Open Collective JSON: gitleaks and bandit both `balance 0, yearlyIncome 0, backersCount 0`; semgrep/pip-audit/ruff/litellm/pyup all return `Not found`; babel `19720967`/`25997849`/1258, webpack `8980591`/`18447031`/2772, vuejs `4315234`/`18993800`/871 cents — **the cents→dollars arithmetic in the table is correct in all six figures**. `gh api graphql` today returns sponsor counts **9, 487, 119, 12** and **0 with `hasSponsorsListing: false`** for all four orgs — exact.
- **Fortune / Register.** Both fetch 200. The CEO block quote is verbatim (curly quotes in source), and Fortune's own sentence "Masad said updates included the rollout of automatic separation between development and production databases, improvements to rollback systems, and the development of a new 'planning-only' mode…" confirms the file's paraphrase and its labelling of it as a paraphrase.

### Instrument log, recounted independently

`grep -oE 'https?://[^ )|`"]+' demand.md | sed 's/[.,;:]*$//' | sort -u` → **56** distinct URLs, matching the author. Removing the User-Agent URL leaves **55 citations**; adding the schemeless `hn.algolia.com` API gives **56**.

| Host group | Count |
|---|---|
| news.ycombinator.com | 10 |
| hn.algolia.com (schemeless) | 1 |
| github.com (citations only, UA excluded) | 2 |
| job-boards.greenhouse.io / jobs.ashbyhq.com / careers.datadoghq.com / tulip.co / www.klaviyo.com / www.himarley.com (ATS + careers) | 15 |
| vendor pricing hosts (21 distinct) | 21 |
| eur-lex.europa.eu, thebrightbyte.com, api.usaspending.gov, sam.gov, api.sam.gov, fortune.com, www.theregister.com, opencollective.com | 8 (approx., 1 each) |

**Corrected HN + GitHub share: 13 / 56 = 23.2%** (author: 24.6%). Both are far below the 70% threshold; the **NOT instrument-biased** header label stands and no confidence downgrade is triggered. I also independently re-derived the log's own arithmetic: 55 + 41 + 18 = **114** probes ✓; 24 + 19 + 1 = **44** boards resolved ✓; the 44 listed per-board posting counts sum to exactly **6,244** ✓. I re-fetched **20 of those 44** board counts live (greenhouse: anthropic 571, datadog 454, gitlab 220, launchdarkly 51, fairmarkit 7, tulip 75, klaviyo 143, himarley 11, hubspot 0; ashby: openai 754, notion 133, replit 71, coder 26, cursor 121, greptile 18, coderabbit 53, graphite 7, snyk 0, wiz 0; lever: lumafield 16) — **every one matched exactly** — and spot-checked ten of the claimed 404s (greenhouse openai/cursor/notion/github/snyk, ashby anysphere/sourcegraph/lakera/zenity/retool), all **404** as claimed.

**UNCHECKED (1):** §1's "**159** matched a governance keyword in the title; **70** carried ≥2 of the governance phrases in the body." The file does not publish the keyword list or the matching script, so these two numbers are not reproducible from the file as written. They are not load-bearing for any conclusion. *Fix: either publish the phrase list and the one-liner, or drop the two numbers.*

### Section 8 sin check

- **Private individuals:** **clean.** No name, handle or personal email of anyone but the principal appears. Speakers are described by role throughout ("Replit's CEO", "the solo maintainer of gitleaks"). Note for the author: "the solo maintainer of FastAPI" and "the solo maintainer of gitleaks" are role descriptions that identify one specific person each — within the letter of the rule, but consider "a widely-deployed Python web-framework's solo maintainer" if this text is ever quoted outward.
- **"Incumbent exists = kill":** **not committed.** The file measures instead of killing, and explicitly classifies (`active-small and well-funded, but enterprise-only and unpriced`).
- **Pain without budget:** **not committed** — the file's whole spine is the budget test, and it closes both escape hatches (§3, §6) with negatives rather than hope.
- **Pre-satisfied gates / undefined terms:** no new gate is asserted (it defers to §9's dated ones). One small lapse: the §7 **"Conf." H/M/L** column is never defined. *Fix: one line saying what H, M and L mean in terms of evidence.*
- **Paraphrase as quote:** one instance, **M5** above.
- **Overreach to flag (not a sin, but the weakest inference in the file):** §4 says three low-scoring Show HN launches "confirm … the category is **zero-adoption**". Three HN point counts measure *launch attention*, not adoption; §8's incumbent test asks for stars/downloads/issue activity. *Fix: either cite `research/adoption.md`'s numbers for those three projects or soften to "no launch traction observed".* Similarly, §8's "MintMCP has enterprise customers" rests on the pricing page advertising "Enterprise SLAs … available", not on a named customer.
- **Internal inconsistency to flag:** the summary's line 2 and §2a's "**Six 404s out of six** named AI-security vendors" sit above a table that lists **ten** AI-security vendors, four of which returned 200. *Fix: "six of the ten AI-security vendors checked 404 their /pricing path; the other four return a page with no price on it" — which is a stronger sentence anyway, since it makes the "no public price at all" claim 10-for-10.*

### Verdict

**The file's conclusions hold at their stated confidence, and one of them holds harder than the author claimed.** Of 90 checkable assertions, 83 reproduce exactly against the live sources today, 0 were unreachable, and 1 is unreproducible only because the file omits its method. The six mismatches are all of the same benign kind — none reverses a finding. Four of them (M1–M4) are the author *under*-reporting: the Klaviyo and Hi Marley bands **are** in the Greenhouse payload today, which means Session 1's $148,000–$222,000 figure is now independently re-confirmed from a second instrument rather than left standing on Indeed, and the §7 "capability as a salary" row can add **$152,000–$283,000 (Hi Marley, Boston)** and **$160,000–$240,000 (Klaviyo PM, Boston)** to the Massachusetts evidence — strengthening summary claims 1 and 9 and the "For the plan as a whole" argument. M5 is a one-word insertion into an otherwise correct quote; M6 moves the bias share from 24.6% to 23.2% and changes nothing. Everything that actually carries a verdict — the 6/6 pricing 404s, the seven zero-award procurement queries with their working controls, the $0 Open Collective balances and nine sponsors, the three EU AI Act articles' "High-risk AI systems shall…" framing, the four self-serve seat prices, and the Coder/Datadog/LaunchDarkly reqs that anchor `pkg-egress-guard` and `pkg-change-receipt` — is **verbatim and current as of 2026-08-30**. The one place the reasoning outruns the evidence is the §4 leap from three Show HN point scores to a "zero-adoption" classification, which is `adoption.md`'s call to make, not this file's; that sentence should be sourced or softened, and it is the only edit that touches an argument rather than a fact.

**Fix pass: 8 items fixed, 1 marked UNVERIFIED, 1 conclusion downgraded.** (demand-side-scout, 2026-08-30. Fixed: the three Massachusetts bands and the Klaviyo narrative — all four re-fetched independently today from `boards-api.greenhouse.io` and matching the verifier exactly; the Greptile quote; the six-of-six → ten-for-ten pricing statement in summary line 2 and §2a; the §7 H/M/L confidence key; the citation recount to 13/56 = 23.2% in the header and the instrument log; the §7 salary row. UNVERIFIED: §1's title/body keyword-match counts, withdrawn from the text as unreproducible from this file. Downgraded: §4 no longer classifies the category **zero-adoption** — it claims only "no launch traction observed on HN" and hands the classification to `adoption-analyst`. The **NOT instrument-biased** label and every other confidence level stand unchanged.)
