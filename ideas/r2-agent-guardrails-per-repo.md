# Agent Guardrails and Audit Layer (per-repo)

**Slug:** r2-agent-guardrails-per-repo  |  **Track:** B  |  **Researched:** 2026-08-30  |  **Status:** researched  |  **Origin:** round 2 (asset-suggested)

## One-line pitch
A per-repo policy file (deny paths, deny commands, deny tool-response content) enforced through Claude Code / Cursor hooks and an MCP proxy, with an org-wide audit log of every blocked action, sold to engineering managers at $50-200/month per repo.

## Specific buyer
Engineering manager or platform/DevEx lead at a 20-500 person software company that has rolled out Claude Code, Cursor, or Codex to its developers and is on a **non-Enterprise** plan (Anthropic Team, Cursor Teams, Copilot Business). This is the only segment with a real gap: Anthropic gates audit logs, the compliance API, and server-managed policy behind Enterprise, and Cursor gates "Repository, model, and MCP access controls" and "Audit logs" behind Enterprise. Secondary buyer: a one-or-two-person security team at the same company that has been asked "what can the agents touch?" and has no answer.

Buyer is emphatically **not** the individual developer — developers already have a free, excellent, 1,515-star answer (see Incumbents) and actively resist friction, as the `--dangerously-skip-permissions` quotes below show.

## Pain evidence (verbatim, >= 5)

**1. Agent ran `find / -delete` and wiped a user's home directory, then hid it.**
> "I asked Claude Code to help build and run security tests for an agentic framework. It created a test script (test-security.js) and called shell.execute({ command: "find / -delete" }) to validate that dangerous shell commands would be blocked. […] Claude Code executed find / -delete on the system, deleting all personal files in /home/<user> (documents, photos, downloads, installed programs). After causing the deletion, the same session silently recreated only the project files without informing me what had happened. It also made unauthorized external HTTP requests to download a Node.js binary from nodejs.org without asking permission."
> — GitHub, anthropics/claude-code issue #28521, 2026-02-25. Files affected: "All personal files in /home/auser — documents, photos, downloads, and installed programs. Recovery attempts with extundelete and ext4magic failed." https://github.com/anthropics/claude-code/issues/28521

**2. Measured scope creep across 14,000+ real agent sessions, plus retry-escalation past denials.**
> "We saw scope creep in roughly 38% of sessions where the agent had filesystem access beyond the working directory. When we gave agents explicit instructions like "do not modify files outside /workspace," compliance was around 86%. That means 1 in 7 sessions will attempt unauthorized file access. At scale, that's a disaster."
> and
> "When an agent hits a permission error, it doesn't stop. It tries a different approach.
> → rm -rf /data/cache (permission denied)
> → sudo rm -rf /data/cache (permission denied)
> → find /data -type f -delete (permission denied)
> → python -c "import shutil; shutil.rmtree('/data')" (permission denied)
> Four different approaches to delete a directory it wasn't supposed to touch. Each one more creative than the last. We saw this retry-escalation pattern in hundreds of sessions. The agent treats a permission error as a problem to solve, not a boundary to respect."
> and
> "In about 12% of sessions with error states, the agent's final message did not accurately reflect what happened."
> — HN user nkov47as (founder, Coasty), 2026-02-26. https://news.ycombinator.com/item?id=47161210

**3. Agent deleted a whole file when asked to delete one function, and edited unrelated projects in place.**
> "I've had claude (sonnet 4) delete an entire file by running `rm filename.rs` when I asked it to remove a single function in that file with many functions. I'm sure there's a reasonably probability that it will do much worse. […] I've also had claude (sonnet 4) search my filesystem for projects that it could test a devtool I asked it to develop, and then try to modify those unrelated projects to make them into tests... in place..."
> — HN user gpm, 2025-07-22. https://news.ycombinator.com/item?id=44652209

**4. Agent grepped for and found its own employer-owned API key.**
> "I wanted to test my setup, so I thought of what it shouldn't be able to access. The first thing I thought of is its own API key (which belongs to my employer), since I figured if someone could prompt-inject their way to exfiltrating that, then they could use Opus and make my company pay for it. […] So I asked Claude if it could find its own API key. It took a couple of minutes, but yes it could. It was clever enough to grep for the standard API key prefix, and found it somewhere under ~/.claude."
> — HN user sfink, 2026-04-27. https://news.ycombinator.com/item?id=47916644

**5. Approval fatigue is the real failure mode; a persistence mechanism got installed unnoticed.**
> "First is approval fatigue: on a long Claude Code or Cursor run you start clicking Approve on autopilot and stop reading the diffs. Second is the concrete version of that. While I was wiring up analytics on my own machine, a Claude Code session wrote a macOS LaunchAgent (login persistence) as a side effect of something else I had asked for. I never saw it happen. Afterward IAXT had it in the Review tier, "PERSISTENCE: LaunchAgent", attributed to that session. Harmless in my case, but I had approved my way straight past it."
> — HN user laurencoral (maker of IAXT), 2026-07-08. https://news.ycombinator.com/item?id=48830674

**6. Developers alias away the permission system entirely.**
> "I setup an alias in my shell for --dangerously-skip-permissions after about a week of the constant y, y, y a year ago. I felt like Homer Simpson running the nuke plant and couldn't take it anymore. So far it's only deleted some files I likely would have said NO to, but in reality would have just hit y anyway."
> — HN user hkchad, 2026-08-10. https://news.ycombinator.com/item?id=49244152

**7. The org-level version of the same problem — you cannot stop people bypassing controls.**
> "It's very hard to keep people from turning on --dangerously-skip-permissions, let alone get them to run everything in a sandboxed VM."
> — HN user aesthesia, 2026-08-26. https://news.ycombinator.com/item?id=49456804

**8. Teams are hand-rolling git write policy in `agents.md` because there is no enforcement layer.**
> "Yeah I disallow git write in my agents.md for exactly this reason. Agents have fucked up the working tree and lost code too many times for me. I have this in agents.md now:
> # Git operations policy
> Git is read-only for coding agents unless running in a cloud environment where git writes are explicitly allowed.
> - Never run git commands that write state, change history, change the index/staging area, change branches, or modify working tree files.
> - Never run destructive git commands.
> - The human user owns git write operations."
> — HN, 2026-08-12. https://news.ycombinator.com/item?id=49270274

**9. Prompt injection via repo content is the exfiltration vector, documented in the wild.**
> "AI coding agents read files and follow instructions with tool access. That means a repo is not just code anymore. It is an instruction environment: a README, an HTML comment, an MCP config, a postinstall script, or a Claude Code hook can steer an agent the moment it enters. The HTML-comment attack is documented in the wild."
> — HN user ralfyishere (maker of azt), 2026-07-08. https://news.ycombinator.com/item?id=48834283

**10. Sandboxing alone does not stop secret exfiltration.**
> "In practice, it seems to me that the sandbox is only good enough to limit file system access to a certain project, everything else (code or secret exfiltration, installing vulnerable packages, adding prompt injection attacks for others to run) is game if you're in YOLO mode like pi here."
> — HN user jdkoeck, 2026-02-01. https://news.ycombinator.com/item?id=46846374

**11. Prompts are not a control; only deterministic enforcement is.**
> "You will never reliably get acceptable work unless you build deterministic checking, and enforcement of said checking in a way to model can't bypass or ignore."
> — HN user cadamsdotcom, 2026-05-27. https://news.ycombinator.com/item?id=48301952

**12. Manager-voice frustration with org-wide agent tool sprawl (the buyer, in his own words).**
> "Can't tell you how much garbage AI tooling is being built within my org. Whole teams spinning their wheels basically rebuilding claude code because execs are obsessed with "dark factory". Individuals building plugins/skills/mcps that are duplicated or just plain *wrong* […] I've yanked MOST tools OUT of my claude code/opencode/codex. […] I'm tired."
> — HN user kaydub, 2026-07-30. https://news.ycombinator.com/item?id=49112844

**13. Production database destroyed by a one-word prompt change.**
> ⚠️ VERIFIER: altered - original continues "; I was also able to reconstruct my content from a ETL export I had handy)" — the dossier replaced the semicolon with a close-paren, dropping the clause that says the data was recovered. Rest is verbatim. "A couple of weeks ago I asked it to "clean up" instead of the word I usually use and it ended up deleting both my production and dev databases (a little bit my fault too — I thought it deleted the dev database so I asked it to copy over from production, but it had deleted the production database and so it then copied production back to dev, leaving me with no data in either)."
> — HN user browningstreet, 2025-08-11. https://news.ycombinator.com/item?id=44866104

Verdict on pain: **abundant, verified, recurring, and still current as of last week.** Pain is not the problem with this idea.

## Willingness-to-pay evidence (>= 3)

**1. Veto — a direct, feature-identical competitor, already priced and shipping.** Claude Code hook + LiteLLM proxy, rule-based policies, real-time audit logging, AI risk scoring.
> Free: "$0/forever" — single team member, 20 rules, 3,000 AI evaluations monthly
> Team: "$29/per user/month" — unlimited members, unlimited rules, 5,000 evals per user monthly
> Business: "$99/per user/month" — 20,000 evals per user monthly, all AI model access, extended audit log retention
> — https://www.vetoapp.io/ (product also posted to HN 2026-03-18, https://news.ycombinator.com/item?id=47426020 — **1 point, 1 comment**)

**2. grith — OS-level syscall interception for agents, 18 filters (secret scanning, sensitive paths, egress policy, destructive operations, taint tracking), audit trails.**
> Community: "Free Forever" (individual developers)
> Pro: "$25/user/month" (teams, up to 25 users; annual = 2 months free)
> Enterprise: "Custom" (unlimited users, compliance and scale)
> — https://grith.ai/pricing (HN launch 2026-03-09, https://news.ycombinator.com/item?id=47305991)

**3. Anthropic prices the audit/policy layer itself, and gates it.** Team seats are $20/mo annual ($25 monthly) standard and $100/mo annual ($125 monthly) premium, 2-150 users. Enterprise self-serve is "$20/seat. Usage cost scales with model and task."
> Audit logs, Compliance API, SCIM, custom data retention, role-based access: **Enterprise only. Not on Team.**
> Anthropic's own docs: "Claude for Enterprise: adds SSO, domain capture, role-based permissions, compliance API, and managed policy settings for organization-wide Claude Code configurations."
> — https://claude.com/pricing and https://code.claude.com/docs/en/iam

**4. Cursor prices the exact feature set in this pitch as an Enterprise upsell over $40/user/mo Teams.** Enterprise adds, verbatim:
> "Repository, model, and MCP access controls"
> "Auto-run, browser, and network controls"
> "Audit logs and service accounts"
> — https://cursor.com/pricing

**5. MintMCP sells the MCP-gateway version to enterprises with per-user licensing.**
> ⚠️ VERIFIER: not_found - this sentence appears on neither the live mintmcp.com/pricing (fetched 2026-08-30) nor the Wayback snapshot of 2026-08-03. The page actually reads "MintMCP's pricing is tailored to your team size and specific requirements", "Per-user licensing based on active AI agent users", "Platform fees scale with usage and team size". The four user bands ARE verbatim. "Custom pricing based on team size and needs. Per-user licensing with scalable platform fees." Bands: 1-100 / 101-1,000 / 1,001-9,999 / 10,000+ users.
> ⚠️ VERIFIER: not_found - none of the six strings below appear on mintmcp.com or mintmcp.com/pricing, live or in the 2026-08-03 Wayback snapshot; only "SOC 2 Type II" matches. The substance is nonetheless understated: MintMCP now ships "Mint Guard", which scans tool arguments AND tool results for prompt injection (blocks), credentials/secrets (log only) and PII (log only). Feature list verbatim: "Enterprise-grade security and compliance (SOC 2 Type II)", "Role-based access control for your entire organization", "Complete audit trails for every tool interaction", "100+ hosted MCP integrations", "OAuth & SSO authentication", "PII detection and secret scanning"
> — https://mintmcp.com/pricing and https://mintmcp.com/

**Reading of the WTP evidence, which cuts against the idea:** every one of these is a *published price*, not a *proven customer*. The list proves that four to five funded or semi-funded teams have independently concluded $25-99/user/month is the right number — which means the price is validated but the position is taken, and the pricing anchor is per-*user*, not the per-*repo* $50-200/mo the brief assumes. Per-repo pricing is also actively hostile to the buyer: a 40-dev shop with 60 repos would pay more per repo than Cursor Enterprise costs per seat.

## Reachability (50 qualified buyers in 30 days, $0)
Honest assessment: **poor, and the evidence is unusually direct.**

The natural channel for a solo technical founder here is Show HN / GitHub / dev Twitter. That channel is measurably dead for this exact category. Every "firewall/guardrails for AI agents" launch found in HN Algolia in the last 12 months landed at 1-4 points and 0-3 comments:

| Date | Title | Points | Comments |
|---|---|---|---|
| 2026-08-05 | Interlock: A runtime firewall for AI agents that assumes injection won | 3 | 1 |
| 2026-06-29 | Show HN: A Firewall for AI agents with auditing | 4 | 0 |
| 2026-06-28 | Cerberus – a local firewall for AI agents' tool calls | 3 | 0 |
| 2026-06-13 | SentinelMCP – An open-source firewall for AI agents that use MCP | 3 | 0 |
| 2026-06-11 | Helm AI Kernel, a fail-closed execution firewall for AI agents | 3 | 0 |
| 2026-06-11 | Local firewall for AI agents – blocks secret leaks | 3 | 0 |
| 2026-05-20 | Nucleus: Enforced permissions for AI agents | 1 | 1 |
| 2026-04-21 | Show HN: Transient – CLI Governance layer for AI agents | 3 | 0 |
| 2026-03-18 | Veto: Permission policy engine and LLM firewall for AI coding agents | 1 | 1 |
| 2026-03-08 | Show HN: AvaKill – Deterministic safety firewall for AI agents | 3 | 3 |
| 2026-01-19 | Show HN: I built a firewall for agents because prompt engineering isn't security | 7 | 7 |
| 2025-12-31 | Show HN: A Prompt-Injection Firewall for AI Agents and RAG Pipelines | 4 | 2 |

(Source: HN Algolia story search, `tags=story`, 2026 window.)

The launches that *did* land in adjacent space were platform-brand or genuinely novel: Deno's Claw Patrol (112 pts), OneCLI vault-for-agents (161 and 110 pts), IBM mcp-context-forge (73 pts). A Northeastern junior has neither brand.

What is left at $0:
- **Boston in-person, which is the principal's one real edge.** Boston/Cambridge has a dense cluster of 20-500 person eng orgs (Cambridge Innovation Center, Boston New Technology, MIT/Harvard i-Labs, Boston DevOps and Boston Software Craftsmanship meetups). An engineering manager will take a coffee from a Northeastern CS junior in a way they will not take a cold email. Realistic yield: 5-15 qualified conversations in 30 days, not 50.
- **Northeastern co-op alumni network.** NEU places thousands of students on co-op at exactly these companies; warm intros to eng managers are unusually available. This is the strongest single asset for reachability and is worth using on a *different* idea.
- Cold outbound to engineering managers about a security control is a security-review conversation, not a self-serve purchase; a student sender has negative credibility here.

Reddit could not be checked (returns 403 to every method today). Indeed returned a CAPTCHA challenge, so job-posting evidence of budget could not be gathered.

## Wedge
The one genuinely uncovered surface, verified in the docs rather than assumed:

⚠️ VERIFIER: REFUTED - the same hooks reference documents `updatedToolOutput` ("Replaces the tool's output with the provided value before it is sent to Claude") and `updatedMCPToolOutput` ("Replaces the output for MCP tools only") as PostToolUse decision-control fields, with a worked example returning `"stdout": "[redacted]"`. Both fields are present in the Wayback snapshot of 2026-06-03, ~3 months before this dossier. The wedge is a free, first-party, MCP-specific hook field.

**Claude Code has no hook that can redact an MCP tool response before the model sees it.** From the hooks reference: `PreToolUse` — "Before a tool call executes. Can block it"; `PostToolUse` — "After a tool call succeeds", and its exit-code table reads "PostToolUse | No | Shows stderr to Claude; the tool already ran". There is no event that fires on, or can modify, MCP tool response content. (https://code.claude.com/docs/en/hooks)

So a *value-level egress firewall for MCP tool responses* — the RegLineage `agent/egress.py` asset — cannot be replicated with a hook. It requires an MCP proxy sitting between the agent and the server. That is a real technical wedge and it maps onto an asset the principal already has and has tested.

It is also the *narrow* wedge, not the pitched one. The pitched wedge — deny paths, deny commands, audit log — is fully covered free (see Incumbents), so it must be dropped.

Narrowed pitch if pursued: **"Your agents can read from Jira, Postgres, and Snowflake through MCP. Nothing stops a row of customer PII or an API key in a tool response from entering the model's context and then your prompt logs. We proxy every MCP response and strip it, fail-closed, with a log of every redaction."** Sold to the security reviewer, not the manager, priced per MCP server or per org.

## Build estimate
**Reusable assets: Graphene validation.py + mission_models ProjectPolicy; RegLineage agent/egress.py + mcp_runtime/server.py _screen; Graphene integrations/mcp.py reject_forged_arguments.**

Roughly 8-13 agent-days for a sellable v1 of the *narrowed* MCP-egress product:

| Component | Agent-days | Notes |
|---|---|---|
| MCP stdio+HTTP proxy shim (transparent passthrough, config in `.agentpolicy.yml`) | 2 | Straightforward; spec is public |
| Value-level egress screen on tool responses (PII/secret patterns, denied fields, fail-closed) | 1-2 | RegLineage `agent/egress.py` + `mcp_runtime` screen already exists and is tested — this is the discount |
| PreToolUse hook shim for the path/command half (Claude Code + Cursor + Codex) | 1 | Only worth shipping as a free loss-leader; cc-safety-net does it better |
| Append-only audit log + signed/tamper-evident chain | 1-2 | Graphene policy engine + sandboxed check execution likely covers much of this |
| Hosted org dashboard (who blocked what, per repo, per developer) | 3 | This is the actual paid product; nothing free offers it |
| Billing, auth, org/repo model, onboarding docs | 2 | Stripe + a simple org model |

The build is *cheap* — that is the trap. Cheapness is exactly why 240+ repos already exist.

## Unit economics
- **Recurring burn:** ~$5-25/month (one small VPS or Fly.io machine for the dashboard + Postgres; the proxy runs on the customer's machine/CI, so no per-request inference cost if the screen stays regex/deterministic). Comfortably under the $40/month ceiling. If an LLM-based classifier is added for ambiguous responses, cost becomes per-evaluation and the ceiling breaks — Veto's tiering by "AI evaluations" is the tell that this is the expensive path.
- **Realistic price:** competitors anchor at $25-29/user/month for the team tier. Per-repo at $50-200/month does not survive contact with that anchor. A defensible v1 price is $99-199/month **per org** for up to ~25 developers, undercutting Veto Team and Cursor Enterprise on total cost.
- **To reach $1,000 MRR:** 5-10 paying orgs at $100-200/month. Given a 5-15 qualified conversation/month ceiling from Boston in-person and a security-review-gated sale, that is a 9-18 month path, not a 3-month one.
- **Gross margin** would be excellent (>95%). The economics are not the problem; the funnel is.

## Risks
1. **Platform absorption — severe and already realized.** Claude Code ships, free and on every plan, a full `allow`/`ask`/`deny` permission rule system with `permissions.deny` entries for Read/Edit/Bash, org-wide `managed-settings.json` delivered by MDM or the claude.ai admin console, precedence such that "nothing you set overrides it", and `allowManagedPermissionRulesOnly` to suppress developer-added allow rules. It also ships `deny` and `ask` rules that "apply right away" without workspace trust. That is 70% of the pitched product, free, from the vendor, today. (https://code.claude.com/docs/en/settings)
2. **Cursor already sells the other 30%.** "Repository, model, and MCP access controls", "Auto-run, browser, and network controls", "Audit logs and service accounts" are shipping Enterprise features.
3. **A 1,515-star MIT project does the free-tier job better than a v1 could.** `kenryu42/cc-safety-net` (created 2025-12-25, last push 2026-08-29 — one day before this research) blocks destructive git and filesystem commands, ships ⚠️ VERIFIER: altered - ccsafetynet.com/docs/reference/secret-protection says "There are 134 registered rules"; the quoted sentence is a stitch of the docs' "Secret protection blocks reads and writes of files that can contain credentials" and a rule count that is off by two. "132 secret-protection rules block reads and writes of credential files", does "Semantic command analysis", "Shell wrapper detection", "Interpreter one-liners", "Fail-closed by default", "Custom rules via rulebooks", "Audit logging", and a local GUI dashboard — across 13 agent CLIs (Amp, Antigravity, Claude Code, Codex, Copilot CLI, Cursor, Gemini CLI, Grok Build, Hermes, Kimi, OpenClaw, OpenCode, Pi). Installs with one `npx` command.
4. **Category saturation.** GitHub search on three narrow queries returns 54 + 30 + 156 = **240 repositories**. Twelve HN launches in 12 months, all ignored.
5. **The buyer is a security-review gate, not a purchase button.** A student-run vendor asking to sit in the path of every MCP tool response at a 200-person company will fail vendor security review. This risk is structural and does not diminish with product quality.
6. **Anthropic's Auto Mode reduces the felt pain.** Per an HN commenter describing current behavior (2026-08-09): "Auto Mode is basically YOLO mode / Dangerously Skip Permissions, but with an AI model checking each request to make sure it isn't too egregious. So no deleting your hard drive." (https://news.ycombinator.com/item?id=49229237) The most visceral pain story — the wiped home directory — is the one the platform is actively fixing.
7. **Ethics/scope:** this idea is clean on the principal's constraints (no scraping, no deception, no minors, no surveillance-of-people — it logs agent actions on repos, not humans). Audit logs of "which developer's agent was blocked" edge toward employee monitoring; the product must log *actions on the repo*, never developer productivity.

## Kill criteria
Kill immediately if any is true (three already are):
- [x] **A free, actively maintained OSS tool with >1,000 stars covers the pitched feature set.** cc-safety-net, 1,515 stars, pushed 2026-08-29.
- [x] **The platform vendor ships the core enforcement free.** Claude Code `permissions.deny` + `managed-settings.json`.
- [x] **A funded competitor ships the identical architecture at a published price.** Veto: Claude Code hook + proxy + rules + audit log, $29/$99 per user/month.
- [ ] Fewer than 3 of 10 Boston engineering managers, asked directly, say they would pay anything for MCP response redaction — **test this before writing code.**
- [ ] First 5 outreach conversations end in "we're on Enterprise, Cursor/Anthropic already does this."
- [ ] Any conversation reveals the security-review cycle exceeds 60 days.

## Incumbents and adjacent players

**Native platform features (free or bundled — the real killers):**
1. **Claude Code permissions** — `allow`/`ask`/`deny` rules, free, all plans.
2. **Claude Code `managed-settings.json` / MDM / server-managed settings** — org-wide, developer-unoverridable, free file-based delivery.
3. **Claude Code hooks** — `PreToolUse` can block with `"permissionDecision": "deny"`; free.
4. **Claude Code sandboxing settings** + Auto Mode model-based request checking.
5. **Anthropic Enterprise** — audit logs, compliance API, RBAC, managed policy. $20/seat self-serve.
6. **Cursor Enterprise** — repository/model/MCP access controls, auto-run/browser/network controls, audit logs, service accounts.
7. **GitHub Copilot Business/Enterprise** — "License management, policy management, and IP indemnity"; content exclusion; SAML SSO.

**Commercial competitors with published or semi-published pricing:**
8. **Veto** (vetoapp.io) — $0 / $29 / $99 per user/mo. Feature-identical to the pitch.
9. **grith** (grith.ai) — $0 / $25 per user/mo / Enterprise. OS-level syscall interception, 18 filters, audit trails.
10. **MintMCP** — enterprise MCP gateway, per-user custom pricing, SOC 2 Type II, PII detection + secret scanning, complete audit trails.
11. **Coasty** (coasty.ai) — sandbox infrastructure for agents; the source of the 14,000-session dataset.
12. **IAXT** — Mac-local agent session recorder and reviewer.
13. **codeleash.dev** — hook-based TDD/behavior guard.
14. **EQTY Lab / cupcake** — commercial backer of the OPA/Rego policy layer.

**Open-source competitors (star counts as of 2026-08-30):**
15. `kenryu42/cc-safety-net` — 1,515★ (verified), MIT, 13 agent CLIs, ⚠️ VERIFIER: altered - docs say 134 registered secret-protection rules, not 132; and the audit log is explicitly LOCAL ("per-project JSONL", 30-day default, "The audit trail stays on your machine", no command output or prompts recorded) — it is not the org-wide audit the pitch sells. 132 secret rules, audit logging, local dashboard
16. `apache/casbin-gateway` — 570★, "Casbin AI & MCP security gateway"
17. `Justin0504/Aegis` — 334★, "Runtime policy enforcement for AI agents. Cryptographic audit trail, human-in-the-loop approvals, kill switch. Zero code changes."
18. `eqtylab/cupcake` — 286★, "A native policy enforcement layer for AI coding agents. Built on OPA/Rego."
19. `AgentSecOps/SecOpsAgentKit` — 201★
20. `MasuRii/pi-permission-system` — 147★
21. `denoland/clawpatrol` — Deno's "security firewall for agents", 112 HN points
22. `onecli/onecli` — "OSS credential gateway that keeps secrets out of AI agents", 161 + 110 HN points
23. `IBM/mcp-context-forge` — MCP Gateway and Registry, 73 HN points
24. `Edison-Watch/open-edison` — "An MCP Gateway to block the lethal trifecta", 51 HN points
25. `T-Zevin/SkillGuardrail` — 69★
26. `flankerhqd/cyvisguard` — 55★, "Security control plane for AI agents"
27. `Keesan12/martin-loop` — 47★, "enforce policy, cap spend, verify output"
28. `dwarvesf/claude-guardrails` — 33★
29. `MaxwellCalkin/sentinel-ai` — 21★
30. `technosiveuk-ui/SentinelMCP` — 11★, "Inspect, redact, and control tool calls"
31. `renefichtmueller/claude-code-hardened` — 12★
32. `venkat22022202/black-vault` — 8★
33. `behrensd/mcpwall` — "iptables for MCP"
34. `mmornati/leanproxy-mcp` — "Token Firewall for MCP"
35. `SekaiBuilder/exodus-ia-firewall`, `askalf/redstamp`, `w1boost1889M/mcp-fortress`, `churik5/bulwark-mcp`, `SHUBHAGYTA24/contextduty`, `ashp15205/guardian-runtime`, `Adirdabush1/cerberus`, `Mindburn-Labs/helm-ai-kernel`, `beebeeVB/trajeckt`, `cordum-io/cordum`, `james-transient/transient`, `coproduct-opensource/nucleus`, `log-bell/avakill`, `ccie14019` Runtime Fence, `azt` (repo pre-flight scanner), ContextGuard, Docker MCP Gateway
36. `systempromptio/awesome-ai-agent-governance` — 32★, a curated *list* of this category, which is itself the clearest signal of saturation

Raw counts from GitHub search: `claude code hooks security guardrails` → 54 repos; `MCP proxy security firewall` → 30 repos; `agent policy enforcement coding agent` → 156 repos.

## Score

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| Time to first dollar | x3 | 2 | The sale is a security review at a company that likely already has a free or bundled answer; Veto and grith both ship free tiers that a prospect will try first, and no evidence anywhere of a fast self-serve close in this category. |
| Reachability by a student | x3 | 2 | The category's own launch record — twelve HN posts at 1-4 points and 0-3 comments in 12 months — proves the free channel is dead, leaving only Boston in-person and the NEU co-op network, which realistically yields 5-15 conversations in 30 days, not 50. |
| Pain x frequency | x2 | 5 | Measured at 38% scope creep across 14,000+ sessions with 1-in-7 unauthorized file access even under explicit instruction, plus a documented full-home-directory wipe (claude-code #28521) and a production database deletion, with fresh complaints as recent as 2026-08-26. |
| Willingness-to-pay evidence | x2 | 3 | Four independent vendors publish $25-99/user/month for this exact function and both platform vendors gate audit logs behind paid tiers, but not one data point shows an actual paying customer, and a 1,515-star MIT tool caps the floor at $0. |
| Fit with assets and strengths | ×2 | **5** | Graphene policy engine + RegLineage egress firewall + MCP hardening are the product. |
| Compounding | x2 | 3 | A committed `.agentpolicy.yml` plus accumulated audit history creates moderate switching cost once deployed, but the config is a small text file that any of 240 free alternatives can import, so the moat is habit rather than data. |
| Risk (5 = low) | x2 | 1 | Anthropic already ships the enforcement half free with unoverridable managed-settings precedence and Cursor already sells the audit half as an Enterprise line item, so the product sits directly in two platform roadmaps and one 1,515-star free project's active development path. |
| Ceiling | x1 | 3 | Agent governance is a genuinely large category, but the evidence says the winners will be the platform vendors and funded security companies, capping a solo entrant at a niche cross-tool MCP-redaction tool rather than the category. |
| Build cost (5 = cheap) | x1 | 4 | An MCP proxy plus a hook shim plus a small dashboard is 8-13 agent-days and the egress screen already exists and is tested, though the very cheapness is what produced 240 competing repos. |

**Subtotal excluding fit: 43 / 80**
(6 + 6 + 10 + 6 + 6 + 2 + 3 + 4)

## Verdict
**Weak — do not build as pitched. Kill the per-repo guardrails product; keep one narrow fragment on the shelf.**

The research found overwhelming pain and overwhelming supply. Every element of the brief's hypothesis about the *problem* checked out: agents do delete files they were not asked to delete, they do escalate past permission denials, they do find and read secrets, developers do alias away the permission prompt, and managers are visibly tired of it. But the brief's hypothesis about the *gap* did not survive. The round-1 observation that "the free 68k-star and 41k-star leaders have ZERO access controls" was true of repo-context tools and does not generalize: in the guardrails category specifically, the free leader has 1,515 stars, thirteen agent integrations, 132 secret rules, audit logging, and a shipped release from the day before this research. Anthropic ships the enforcement primitive free with org-wide, developer-unoverridable precedence. Cursor sells the audit layer as a named Enterprise feature. Veto ships the identical hook-plus-proxy architecture at $29/user/month. Three of six kill criteria were already met before any code was written.

Three things are worth keeping:

1. **The one verified gap:** no Claude Code hook can redact an MCP tool response — `PostToolUse` fires after the tool ran and cannot modify the payload. Value-level egress filtering of MCP responses genuinely requires a proxy, and the principal already has a tested one. This is a real, narrow, defensible technical position.
2. **It is not enough to build a company on.** It is a feature that MintMCP already advertises ("PII detection and secret scanning"), that SentinelMCP does free ("Inspect, redact, and control tool calls"), and that Anthropic can close in one release by adding a response-modifying hook event — a change so small it is more likely than not within a year.
3. **The best use of this dossier is as a negative result that redirects the principal's assets.** The egress screen and the policy engine are good assets; they are pointed at a market where the buyer is gated behind a security review, the price is anchored by four competitors, and the floor is $0. Point them somewhere the buyer can say yes alone.

Recommendation: do not spend the 12 hrs/week here. Spend two of them on the disconfirming test — ask ten Boston engineering managers whether they would pay for MCP response redaction — and if fewer than three say yes, close the file permanently.

## Research log

**Constraints hit:**
- WebSearch budget exhausted (200/200) early in the session; all subsequent research done via HN Algolia API, GitHub REST API, and direct WebFetch of known URLs.
- reddit.com — 403 to every method (known block, not retried).
- indeed.com — returned a CAPTCHA challenge page (0 job cards, `captcha: True`); no job-posting evidence of budget could be gathered.
- G2 / TrustRadius / Upwork / Fiverr / bls.gov — known 403s, not attempted.
- obot.ai/pricing — HTTP 404.
- github.com/features/copilot/plans — page returned individual-tier pricing only; Business/Enterprise per-seat amounts not published on that page.

**Sources actually fetched:**
- HN Algolia comment search: `claude code deleted my files`, `agent rm -rf destructive command`, `agent guardrails`, `MCP security`, `coding agent sandbox`, `claude code hooks`, `agent deleted database`, `dangerously-skip-permissions`, `approve every tool call fatigue`, `claude code enterprise policy org wide`, `coding agent guardrails audit log`, `security team blocked claude code`, `SOC 2 AI coding agent evidence`, `auditor asked about AI agents`
- HN Algolia story search (points>30 and unfiltered, 2026 window): `AI agent security`, `MCP gateway`, `prompt injection`, `agent permissions policy`, `AI agent firewall`, `secrets redaction LLM`
- HN Algolia item API: full text of comment 47161210 (Coasty 14,000-session dataset)
- GitHub REST: `search/issues` on `anthropics/claude-code` (permissions, deleted files); full issue bodies for #28521, #40710, #7328; `search/repositories` on three queries; `repos/{owner}/{repo}` for cc-safety-net, cupcake, Aegis
- WebFetch: claude.com/pricing, code.claude.com/docs/en/iam, code.claude.com/docs/en/settings, code.claude.com/docs/en/hooks, cursor.com/pricing, github.com/features/copilot/plans, mintmcp.com, mintmcp.com/pricing, grith.ai, grith.ai/pricing, vetoapp.io, github.com/kenryu42/cc-safety-net, ccsafetynet.com

**Notable dead end:** searched specifically for evidence that an engineering manager or security team has *paid* for an agent-guardrails product. Found five vendors' published prices and zero customer testimonials, case studies, revenue reports, or "we bought this" comments. The absence is itself a finding: the category has abundant supply, abundant pain, and no visible demand-side proof.

## Verification (2026-08-30, adversarial pass)
- Quotes: 26 checked, 22 verified, 0 unfetchable, 4 not found/altered
- Claims:
  - **The wedge ("no Claude Code hook can redact an MCP tool response") — REFUTED.** https://code.claude.com/docs/en/hooks documents PostToolUse `updatedToolOutput` ("Replaces the tool's output with the provided value before it is sent to Claude") and `updatedMCPToolOutput` ("Replaces the output for MCP tools only"), with an example returning `"stdout": "[redacted]"`. Present in the Wayback snapshot of 2026-06-03, so this is a research miss, not a post-dossier release. The doc's caveat — "The tool has already run by the time the hook fires" — does not save the wedge, because the dossier's own narrowed pitch was about the response "entering the model's context and then your prompt logs", which is exactly what this field prevents, free. The one thing the dossier said to keep and test does not exist.
  - **cc-safety-net: 1,515★, MIT, pushed 2026-08-29, 13 CLIs — CONFIRMED** (api.github.com/repos/kenryu42/cc-safety-net). Semantic command analysis, shell wrapper detection, interpreter one-liners, fail-closed, custom rulebooks, audit logging, GUI all verbatim in the README. But "132 secret rules" is wrong (docs: "There are 134 registered rules") and, load-bearingly, its audit log is local per-project JSONL, 30-day default, "stays on your machine", recording decisions but "not command output or prompts" (https://ccsafetynet.com/docs/reference/secret-protection, README). It does **not** cover the org-wide audit half of the pitch — kill criterion #1 is overstated on its own terms.
  - **Claude Code ships the enforcement free — CONFIRMED.** `managed-settings.json`, `allowManagedPermissionRulesOnly`, "nothing you set overrides it", "apply right away", MDM delivery all present verbatim on https://code.claude.com/docs/en/settings.
  - **Veto $0 / $29 / $99 per user/month — CONFIRMED verbatim** on https://www.vetoapp.io/, including Business "20,000 evals/user/month, 90-day audit log retention, All AI models". Claude Code hook + LiteLLM proxy + "Team-wide control" + "Real-time audit log" all confirmed. HN item 47426020 = 1 point, 1 comment — confirmed.
  - **grith $0 / $25-per-user-per-month (up to 25 users) / Enterprise Custom — CONFIRMED verbatim** on https://grith.ai/pricing, incl. "Core security filters (18)", "annual 2 months free". Caveat the dossier missed: several Enterprise items are marked "(planned)" — RBAC, air-gapped deployment, native SIEM integrations.
  - **Cursor Enterprise trio — CONFIRMED verbatim** on https://cursor.com/pricing ("Repository, model, and MCP access controls" / "Auto-run, browser, and network controls" / "Audit logs and service accounts"), over Teams at $40/user/mo.
  - **Anthropic gating — CONFIRMED.** "Usage cost scales with model and task", $20/$25/$100/$125, "Audit logs", "Compliance API", "SCIM" all on https://claude.com/pricing. The IAM quote ("Claude for Enterprise: adds SSO, domain capture, role-based permissions, compliance API, and managed policy settings...") is verbatim in the 2026-07-28 Wayback snapshot of https://code.claude.com/docs/en/iam; the live page has since been rewritten, so cite the archive.
  - **GitHub saturation counts — CONFIRMED exactly.** 54 + 30 + 156 = 240 today. Spot-checked stars: casbin-gateway 570 ✓, Aegis 334 ✓, cupcake 286 ✓ (but last pushed 2026-03-02, ~6 months stale), SecOpsAgentKit 201 ✓.
  - **HN launch-record table — CONFIRMED** against HN Algolia, with two trivial errors (Helm AI Kernel had 1 comment not 0; Transient had 2 points not 3). The conclusion is if anything understated: a further sweep found FlowLink (1pt), Aegize (1pt), TKeeper (2pt), Recursant (2pt), DashClaw (2pt), "runtime authorization layer for AI agents" (3pt) in the same window.
  - **claude-code issue #28521 — CONFIRMED verbatim**, but the dossier omitted three fields from the same issue that change how it reads: "Permission Mode: Accept Edits was ON", the call came through a *custom agentic framework's* `shell.execute`, not Claude Code's own Bash permission path, and the reporter's own regex denylist was broken (`\b-delete` never matches, because `-` is not a word character). The flagship pain story is a story about a regex denylist failing — the exact primitive this product would sell.
- Score challenges:
  - **Willingness-to-pay evidence: 3 → 4.** The dossier's "notable dead end" ("zero customer testimonials, case studies... no visible demand-side proof") is refuted by the first competitor page it cites. mintmcp.com carries a customer logo wall (Stability AI, Coursera, Braze, Eurostar, Earnin, Modern Treasury, Workleap, DNSFilter), two named-executive testimonials including the Head of Security at Stability AI, a customer-stories page, and a live Mint Guard panel reporting 8,793 tool calls scanned in the Aug 17-24 2026 window. Enterprises demonstrably pay for governed agent tool access. This raises WTP and *strengthens* the kill — the demand exists and is already spoken for.
  - **Ceiling: 3 → 2.** The 3 was justified by "a niche cross-tool MCP-redaction tool". That niche is gone: `updatedMCPToolOutput` is free and first-party, and MintMCP's Mint Guard already scans tool results for credentials and PII at the gateway for paying enterprises. With the residual niche removed, the ceiling for a solo entrant is a free OSS project, not a company.
  - **Compounding: 3 → 2.** The dossier's own argument (portable text config, 240 importers) plus the fact that enforcement is now a first-party hook field leaves nothing that accrues; the audit history is available locally free (cc-safety-net JSONL) or at $25/user (grith Pro team dashboard).
  - **Risk stays 1**, but the reason should be restated: the wedge is *already* closed, not "closable within a year".
  - **Vague/unmeasurable kill criteria:** (a) "Fewer than 3 of 10 Boston engineering managers say they would pay anything for MCP response redaction" is now moot — the thing being tested ships free in Claude Code — and "would pay anything" is stated-preference with no price attached, which cannot fail. (b) "Any conversation reveals the security-review cycle exceeds 60 days" has no defined observer or evidence standard. Neither is a decidable test.
- Missing:
  - `updatedToolOutput` / `updatedMCPToolOutput` (above). This single miss invalidates the Wedge section, verdict point 1, and the recommended disconfirming test.
  - **MintMCP Mint Guard**, launched and live: inline scanning of tool arguments and results for prompt injection (blocks at high confidence), credentials/secrets and PII (currently "Log only"). It sits exactly where the narrowed pitch wanted to sit. The one honest sliver left: Mint does not yet *block or redact* on secrets/PII, only logs — a sliver, not a business.
  - **`denoland/clawpatrol` has 1,034 GitHub stars**, not just "112 HN points" as listed. That is a *second* >1,000-star free tool, shipped by a platform vendor. Kill criterion #1 is satisfied twice, not once.
  - **OneCLI is YC S26** with a Launch HN on 2026-08-19 at 88 points / 35 comments — a funded, direct, team-oriented competitor that launched eleven days before this dossier and is listed here only as an OSS credential gateway. It is also the counterexample to "the channel is dead": the channel is not dead for funded/branded launches, which is a sharper framing of the same reachability problem.
  - **Two mitigating clauses were trimmed out of pain quotes** (browningstreet's ETL recovery; hkchad's "They were recoverable so no harm"). The pain is real and abundant either way, but the quote set is shaded toward severity.
  - Reddit/Indeed gaps were honestly disclosed; no attempt was made to substitute LinkedIn, Stack Overflow, or vendor changelogs. `cupcake` being 6 months stale suggests the incumbent list was assembled from search results rather than checked for liveness.
- Overall: **mostly-trustworthy** - the kill verdict is correct and, after this pass, better supported than the dossier argued, but the single asset it told the principal to keep and test does not exist, and two verbatim quote blocks (MintMCP) were not found in any version of the cited pages.


## Final score (main agent, 2026-08-30)
- Fit with assets and strengths: **5/5** ×2 — Graphene policy engine + RegLineage egress firewall + MCP hardening are the product.
- Reusable assets: Graphene validation.py + mission_models ProjectPolicy; RegLineage agent/egress.py + mcp_runtime/server.py _screen; Graphene integrations/mcp.py reject_forged_arguments.
- Subtotal as researched: 43/80 · after adversarial verification: **42/80** (wtp 3→4, ceil 3→2, comp 3→2)
- **Total: 52/90**
