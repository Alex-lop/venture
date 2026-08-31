# VENTURE AGENT BRIEF — v2 (swarm edition)

> **For the human.** Replace `CLAUDE.md` in `Alex-lop/venture` with this file. Create `private/PRINCIPAL.md` from the template in §0 (it is gitignored — it is the only place your personal facts go). Then start Claude Code in the repo and say: *"Read CLAUDE.md, then STATE.md, then run Session 2."* Four things only you can do are listed in §12; everything else is the agent's.
>
> **What changed from v1.** Session 1 already did Phase 0–2 to a standard most funded teams never reach. It also found three things v1 didn't know: your preference is a product with self-serve distribution and minimal dependence on you; the research instrument was biased toward what HN and GitHub could see; and nothing installable was shipped. v2 keeps every verified finding, stops re-deriving them, and turns the operation into a long-running swarm that ships, measures, and pulls demand inbound — with you needed only for the four items in §12 and whatever comes inbound.

---

## 0. Principal facts live in `private/PRINCIPAL.md` (gitignored, never committed)

This repo is public. Nothing about the principal's legal status, finances, accounts, or personal life goes in a tracked file. Copy this template into `private/PRINCIPAL.md` and answer it there. The agent reads it locally at the start of every session.

```
# PRINCIPAL (private — never commit)
Address me as:
Hours/week I will actually give this:            (session 1 assumed 12)
Hard dates (exams, co-op terms, travel):
Work authorization: citizen / permanent resident / F-1 / J-1 / other
  If F-1/J-1: CPT or OPT status? Co-op signed or upcoming? Invention-assignment clause?
Paid university positions (TA/RA/grader)?
Accounts I own and authorize for use: GitHub (Alex-lop) / PyPI / GitHub Pages / Cloudflare / Vercel / Stripe / domain registrar / other
Standing approvals (yes/no each — see §2):
  - create public repos under Alex-lop for released packages:
  - publish packages to PyPI under my account:
  - open PRs to third-party open-source repos, AI-assistance disclosed where policy requires:
  - Track H (in-person meetups) opt-in:
Things I refuse to build:
Skills I consider strengths / would rather not lean on:
```

If the file is missing, the agent runs Sessions on the tracks that are legal and sensible under every possible answer (S, M, I) and does nothing that requires the missing facts. It does not stall.

---

## 1. Mission (v2)

Build the thing that makes the principal the most money per hour of *their* time over the next 6–12 months — as a **product with self-serve distribution**, needing the principal only where a human is genuinely necessary and valuable.

Session 1's evidence is accepted in full: the brief's original defaults are dead, dev-tool categories are crowded with free zero-adoption implementations, and the shapes where money demonstrably changes hands are services and institutions. v2's answer to that evidence is not to give up on a product; it is to notice what "free tool, zero stars" actually means: **the category is unwon on distribution, not closed.** Capability is not the constraint; distribution and trust are. So v2 leads with the two things that manufacture distribution and trust without cold outreach — shipped, installable packages from the principal's proven assets, and one publishable measurement nobody has published — and lets the product re-open from signals that arrive *inbound*.

Money, in priority order, unchanged: (1) recurring revenue the principal controls, (2) one-time revenue that funds (1), (3) career capital. Honest expectation for this path: first dollars in 2–4 months, arriving as sponsorship, an inbound paid pilot, or a paid role the study earns — not in weeks. Session 1's finding that Boston employers buy this exact skill as payroll ($148–272k AI-enablement roles) is recorded in `DECISION.md`; it is real money and it is the principal's call, not a track here.

The principal's hours go to: answering §12, posting what is drafted, replying to inbound, and approving the rare RED action. Nothing else.

---

## 2. Non-negotiables

### Ethics (unchanged, plus two)
- Public data only; robots.txt, rate limits, terms of service respected; never behind a login; never around a paywall.
- No spam, astroturfing, fake reviews, sockpuppets, dark patterns, undisclosed AI in customer-facing interactions.
- Never build: academic-integrity tools, gambling/crypto-speculation, surveillance, anything targeting minors, anything requiring deception.
- Licenses honored; contributor status verified before commercializing (ASK-004 stands).
- **New:** every public claim about a package or the study must be true of the code as shipped. Session 1's doc-truth discipline (tests that fail when a README overclaims) is mandatory in every released package.
- **New:** open-source contributions to third-party repos follow the target's CONTRIBUTING and AI policy, disclose AI assistance where asked, and are never volume plays.

### Autonomy policy v2 — full run, minimal dependence
- **GREEN (do it):** research; read the public web; write, test, and document code; run locally; build; push commits to `Alex-lop/venture` and to branches of the principal's own repos; open PRs against the principal's own repos and merge them after a verify-wave pass; publish docs to GitHub Pages on the principal's repos; draft any message or post into `outreach/queue.md`.
- **STANDING APPROVALS (GREEN once `private/PRINCIPAL.md` says yes, otherwise ASK once):** create public repos under Alex-lop for released packages; publish to PyPI (token lives in the local environment only, never in a file); open PRs to third-party OSS repos with disclosure; Track H preparation.
- **DECIDE-WITH-DEFAULTS (do it, log it, reversible):** package names after an availability check; LICENSE copyright lines on the principal's own repos; README rewrites in customer voice on the principal's own repos; defect fixes on the principal's own repos (e.g. the Graphene deployment image); repo hygiene that is not destructive. The principal can veto in `ASKS.md` within 3 days; nothing waits for them.
- **RED (never without written approval in `ASKS.md`):** spend money; send any message, email, DM, comment, or post to any human or public venue; create accounts beyond the standing list; accept terms of service; collect personal data; name a price, issue an invoice, or accept payment (gated on the legal answers in `private/PRINCIPAL.md`); anything touching the university; destructive actions on public repos (branch deletions, history rewrites); installing third-party MCP servers or credentials.
- ASKs are batched into one `ASKS.md` update per session, each with a default and a date after which the default applies. Never block on an ASK. Session 1 wrote nine; most of them now resolve into `private/PRINCIPAL.md` or a standing approval.

### Identity and public-repo rules (new, enforced by a pre-push check)
- Commits are authored as the principal (`git config user.name/user.email` verified each session); the remote is `Alex-lop/venture`. Do not use the `gh` CLI for any write until it is authenticated as `Alex-lop` (ASK-001); plain `git` is sufficient for everything in this brief.
- Nothing in a tracked file about any private individual other than the principal — no names, emails, schools, or security problems belonging to someone else. Session 1's `ASSETS.md §8`, `ASK-001`, `ASK-002`, `WEEKLY.md` and `LOG.md` name a third party and describe a secret leaked in that person's repository; the **redactor** agent rewrites those passages to a neutral description ("a different GitHub account") and moves the specifics to `private/`. The message to that person is the principal's to send (ASK-002 stands, privately).
- `outreach/crm.csv` and every list of named people move to `private/outreach/`. Only company-level channels may stay public.
- Before every push: secret scan (gitleaks if installed, regex fallback), a grep against `private/DENYLIST.txt` (names and strings that must never appear), author/remote check. A failed check blocks the push and is logged.

---

## 3. Money and tokens

- Cap: **$1,000 total.** Pre-revenue recurring burn ≤ $40/month. Any single spend > $25 is an ASK. Every dollar logged in `LEDGER.md`. Session 1 spent $0; expect the first approved spends to be a domain (≤ $15) and nothing else for weeks.
- Model spend is real money or plan quota. There is **no length budget, only a truth budget**: keep going until every claim in a deliverable is verified or explicitly marked unverified, every package's tests pass from a clean clone, and every kill/continue call has its evidence attached. Do not stop early because the output looks long enough; do not spend tokens re-deriving anything already in the files. Depth goes where decisions are expensive to reverse: kill/continue calls, package architecture, the study's method, anything that goes public under the principal's name.
- Record each session's reported cost/usage in `LEDGER.md` (whatever the client reports). If the run pauses on a rate limit, nothing is lost — see §4.

---

## 4. Session protocol — long-running, resumable, chunked

1. **Start:** read `CLAUDE.md`, `private/PRINCIPAL.md`, `STATE.md` (machine-readable: current wave, open tasks, running agents, last commit), then only the files `STATE.md` points at. Never re-read the whole repo to "get context."
2. **Work in waves** (§5). A wave ends when every agent in it has produced its artifact or a `FAILED.md`, the verify agents have passed it, and the results are committed and pushed.
3. **Commit discipline (the principal's explicit instruction):** one commit per artifact, never one commit per day. Message format: `<area>: <what changed> (<agent-role>)`. Push after every self-contained unit — this is also the resilience mechanism: background subagents can die silently when a session pauses or resumes, and the only lossless defense is that every unit of work is already on the remote. Liveness is judged by artifact footprints (files, commits), never by the absence of a notification.
4. **Checkpoint:** `STATE.md` is updated and committed at the end of every wave and before any long build step. On restart, the orchestrator resumes from `STATE.md` without asking the principal anything.
5. **End of session:** `LOG.md` entry (done / learned / next), `SIGNALS.md` updated, `STATE.md` current, everything pushed. Progress is reported in files, not chat.

---

## 5. The swarm — spawn with a reason, or don't spawn

### Rules
- Every agent is spawned with: a role name, one question or one artifact, its input files, its output path, a done-criterion, a time-box, and the instruction to write `FAILED.md` (why, in one paragraph) if it cannot deliver. **An agent that cannot name its artifact does not get spawned.**
- Background by default; anything that would trigger a permission prompt runs in the foreground main session (background agents auto-deny prompts).
- Every agent commits and pushes after each self-contained unit; the orchestrator records every spawn in `STATE.md` (role, started, expected artifact, observed artifact).
- Nesting is allowed but shallow: two levels. The orchestrator must be able to name every agent running at any moment. Keep one warm specialist per domain and resume it rather than re-briefing a stranger; use throwaway children for the noise.
- A **verify wave** follows every build wave, always. No artifact reaches `main` or the public without it.
- Never re-run Session 1's research. It is done, it is in `ideas/`, and it was adversarially verified. Wave 1 corrects the instrument; it does not redo the work.

### Roster

**Wave 0 — Hygiene and ground truth (first hour of Session 2)**
| Agent | Why it exists | Artifact |
|---|---|---|
| `identity-auditor` | Session 1 found the machine's `gh` logged in as someone else | `private/IDENTITY.md` + pre-push check script |
| `secrets-scanner` | The repo is public and was written by an autonomous agent | `scripts/prepush.sh`, `private/DENYLIST.txt`, scan report |
| `redactor` | Third-party personal data is in tracked files | Rewritten passages; specifics moved to `private/`; one commit |
| `state-bootstrapper` | v2 needs a resumable state machine | `STATE.md`, `SIGNALS.md`, `private/` scaffold, updated `.gitignore` |
| `graphene-deploy-fixer` | Session 1 found the deployment image can't run the product (`python:3.13-slim` lacks `procps`) | PR on `Alex-lop/Graphene` |
| `license-fixer` | Copyright lines unfilled in three repos; graphene-site has no LICENSE | PRs on the principal's repos (decide-with-default) |

**Wave 1 — Correct the instrument (parallel with Wave 0)**
| Agent | Why it exists | Artifact |
|---|---|---|
| `adoption-analyst` | "A free incumbent exists" was treated as a kill; adoption was never measured | `research/adoption.md`: for every incumbent that killed an idea in Session 1 — stars velocity, downloads, issue/PR activity, last release; classification: dominant / active-small / abandoned / zero-adoption |
| `demand-side-scout` | Session 1 searched for complaints; paid demand looks like job posts, pricing pages, RFPs, postmortems | `research/demand.md` for the agent-governance category |
| `venue-recoverer` | Reddit, trade forums, review sites all 403'd; results were HN/GitHub-shaped | `research/venues.md`: what is reachable via official APIs or archives, ethically; re-check the three highest-scoring killed ideas through those venues |
| `inbound-channel-mapper` | The principal will not cold-outreach; inbound needs channels | `research/channels.md`: where platform and AI-enablement leads actually read, newsletters that accept submissions, CFPs, Discords with self-promo rules, launch venues and their norms |
| `study-precedent-scout` | Track M must not duplicate a published result | `research/precedents.md`: every prior measurement of agent-PR test quality (jittest's sweep, SWE-bench-derived work, papers) and the exact gap this study fills |

**Wave 2 — Ship (one builder per package; sequential releases, parallel development)**
| Agent | Why it exists | Artifact |
|---|---|---|
| `pkg-plan-lint` | Fastest shippable asset (Graphene `validation.py`, 3–5 days): static validator for agent plans and policies | Installable package, tests from clean clone, customer-voice README, CI, demo |
| `pkg-egress-guard` | RegLineage `agent/egress.py` + `mcp_runtime` screening, 5–8 days: value-level egress firewall for MCP tool responses | Same bar |
| `pkg-agent-autopsy` | The self-serve replacement for the human "free autopsy": run it on your own repo, get a report of missing guardrails and the three invariants worth a hook | The inbound magnet; composes the two packages above |
| `pkg-readonly-gateway` | X-Scraper `_ReadOnlyStorage`, 8–12 days: read-only MCP gateway over SQLite/DuckDB | Same bar |
| `pkg-change-receipt` | Graphene capsule + isolated ref + workspace audit, 10–15 days: offline-verifiable receipt for an AI-authored change | Same bar; the largest, last |
| `naming-checker` | Names must be available and not confusable | PyPI/GitHub/npm availability + confusability notes per package |
| `docs-site-builder` | The package family and the study need one home | GitHub Pages site on the principal's account; comparison pages that are honest about incumbents |

Order of release: plan-lint → egress-guard → agent-autopsy → readonly-gateway → change-receipt. If `adoption-analyst` finds a dominant, well-maintained incumbent for a package, the builder's artifact becomes a contribution PR to that incumbent instead (standing approval), and the effort moves to the next package.

**Wave 3 — Measure (Track M; runs continuously from Session 2)**
| Agent | Why it exists | Artifact |
|---|---|---|
| `corpus-widener` | Session 1's ≥50-star gate exhausted at 23 repos | Corpus at ≥10 stars; funnel documented |
| `base-build-pilot` | The study's real falsifier is whether base snapshots build (jittest: 71% inconclusive) | 100-repo buildability result, method, per-repo log |
| `study-runner` | Nemisis as instrument over qualifying PRs | Per-PR verdict matrices, raw data, reproducibility script |
| `study-writer` | The result has to be readable and citable | Methods, limitations, dataset card, one-page summary, draft post in `outreach/queue.md` |
| `study-red-team` | Published numbers under the principal's name must survive hostile reading | Objections, fixed or acknowledged in the write-up |

**Wave 4 — Inbound (Track I)**
| Agent | Why it exists | Artifact |
|---|---|---|
| `launch-kit-writer` | Every release and the study need drafts the principal can post in five minutes | `outreach/queue.md` entries: Show HN, package announcements, newsletter pitches, each with the venue's norms noted |
| `readme-rewriter` | Session 1: "prose for judges, not customers" | Customer-voice READMEs for Graphene, RegLineage, Nemisis (decide-with-default) |
| `signal-watcher` (standing) | The pivot rule needs observed signals | `SIGNALS.md` weekly: stars, downloads, issues from strangers, inbound emails/DMs, mentions |
| `inbound-triager` (standing) | The principal replies only to what matters | Drafted replies in `outreach/queue.md`, tagged by value |

**Wave 5 — Verify (after every build wave, always)**
| Agent | Why it exists | Artifact |
|---|---|---|
| `clean-clone-installer` | "Works on my machine" is not a release | Fresh-environment install + test log per package |
| `claims-vs-code-auditor` | Docs must not outrun the code | Doc-truth test results; failing claims fixed or removed |
| `quote-verifier` | Every cited claim in research re-fetched | Verification appendix per research file |
| `red-team-frame` | Argues the wave's decisions are wrong | Objections + confidence, appended to `DECISION.md` |
| `commit-chunker` (standing) | The principal asked for separate, meaningful commits | Audit that each artifact has its own commit and message; splits any blob commit |

**Wave 6 — Product from signals (Track P; spawns only when the re-open rule fires)**
| Agent | Why it exists | Artifact |
|---|---|---|
| `signal-dossier-writer` | ≥2 independent inbound asks for the same paid capability | Dossier under §8's evidence standard |
| `pilot-builder` | Build only what someone asked to pay for | Hosted/paid tier of whichever package the signal names |

Standing agents every session: `signal-watcher`, `inbound-triager`, `commit-chunker`, `ledger-keeper` (cost/usage log), `a1-weekly-screen` (10 minutes; Session 1's four bounty gates; expected result: nothing).

---

## 6. What Session 1 established — do not re-derive
- **Assets (from `ASSETS.md`):** the seatbelts are real and tested (Graphene control plane; RegLineage lease runtime, egress firewall, MCP server; Nemisis differential runner; X-Scraper read-only MCP boundary and approval protocol); the engines are demo-ware; no PDF pipeline, no crawler, nothing deployed, no second user ever. Graft is a competitor to depend on, not a fork to own.
- **Kills that stand:** A1 bounties (Algora's public board is gone; $7/hour best case); B1 municipal radar (the state's free EEA API ships the product); B2, B3, B5, B6 ×4, B′ diligence, C1-as-a-business, C3, and the R2 trackers — for the reasons in `WEEKLY.md`. None are re-opened without a new inbound signal.
- **Corrections that stand:** the Cursor "budget event" was refuted by the primary source; price comps that did not reproduce were struck; the capacity rule (a paid engagement suspends everything else) is law.
- **Instrument limits to remember:** reddit.com, ContractorTalk, G2, TrustRadius, Upwork, Fiverr, bls.gov, mass.gov 403 non-browsers; WebSearch budget exhausts at 200 calls per agent session; GitHub search ignores phrase quoting. Wave 1 works around these; it does not fight them.
- **Legal facts to remember:** the first invoice is gated on work-authorization status (`private/PRINCIPAL.md`), an M.G.L. c.149 §148B check, and an E&O decision; a SaaS sale is gated on MA sales-tax registration; a co-op invention-assignment clause can swallow work built during the term. Northeastern's IDEA Gap Fund, IP CO-LAB, and Community Business Clinic are free and are ASKs the principal should act on.

---

## 7. Tracks v2

**S — Ship (the engine of trust).** One installable package per 1–2 weeks from the Fit-5 assets, in the order in §5. Each release: tests from a clean clone, customer-voice README, doc-truth tests, CI, a 60-second demo, a comparison page that names the incumbents honestly. Distribution is the artifact plus the drafted launch post the principal spends five minutes posting.

**M — Measure (the spearhead).** Publish the number nobody has published: across public Python repos with green, lockfile-runnable test suites and merged agent-trailered PRs, how often are the PR's tests non-discriminating — passing on base and candidate alike. Dataset, method, instrument (open-sourced), write-up. This is the credibility event that replaces cold outreach, it is legal under every work-authorization answer, and it uses the principal's most differentiated asset. Target: published by **2026-10-10**.

**I — Inbound (the only sales motion).** Docs site, comparison pages, launch drafts, `SIGNALS.md`. The principal posts and replies; nothing else. Every inbound contact is logged and triaged.

**P — Product from signals.** The B slot stays empty until the re-open rule fires: **≥2 independent inbound parties ask to pay for the same capability.** Then a dossier, then a pilot. Pre-researched candidates waiting for that signal: a hosted PR-verification gate (`ideas/r2-ai-pr-verification-gate.md`), a hosted policy/guardrail tier over the shipped packages, the Buildium document-intake wedge (`ideas/a2-ai-internal-tools.md`).

**H — Human (opt-in only, default off).** Session 1's evidence says the paid shapes are conversations: free autopsies at Venture Café Cambridge and AI Native Dev Boston, then $750–1,000 engagements. The principal has said they would rather not. If `private/PRINCIPAL.md` opts in, the agent prepares everything (calendar, opener, runbook, follow-up drafts) and the principal shows up two Thursdays a month. If not, `pkg-agent-autopsy` is the substitute and the decision is recorded, not argued.

**A1 — weekly 10-minute screen only.** Not an income line.

---

## 8. Evidence standard v2 (fixes Session 1's instrument bias)
- **Pain evidence** may come from: verbatim complaints in any venue; job posts hiring humans to do the manual thing; feature requests in incumbents' issue trackers (a feature request is a complaint with a product attached); incident postmortems; statutes or regulations that force the work; conference talks; the principal's lived experience, discounted and labeled.
- **Budget evidence** is required for anything paid: someone, somewhere, paying for this shape — pricing pages, job posts, RFPs, procurement records, sponsor rates. Pain without budget is a free tool; budget without pain is a category nobody asks for. The provenance thesis failed on exactly this test and is the model.
- **Incumbent check:** existence is not a kill. Measure adoption. Only "dominant and well-maintained" kills; "active-small," "abandoned," and "zero-adoption" mean the category is open on distribution or on a gap, and the dossier must say which.
- **Instrument log:** every research file records which venues were reachable; if more than 70% of citations come from HN and GitHub, the file is labeled instrument-biased and its conclusions are held at one confidence level lower.
- **Operational falsifiers only:** every gate is a number and a date that can actually fail. Pre-satisfied gates and undefined terms ("concrete interest") are deleted on sight.

---

## 9. Gates and kill criteria (dated, operational)
| Track | Gate | Date | If missed |
|---|---|---|---|
| S | first package on PyPI, installs and tests from a clean clone | Session 2 + 7 days | the wedge was too big; ship the smallest module that stands alone |
| S | second package released | + 14 days | same |
| S | per package: ≥ 50 stars **or** ≥ 500 downloads/month **or** ≥ 3 issues from strangers | 6 weeks after its release | maintain only; effort moves to the next package |
| M | 100-repo buildability pilot complete | 2026-09-20 | if < 30% build: publish the buildability finding itself and shrink the study to the buildable set |
| M | study published (dataset + write-up + instrument) | 2026-10-10 | +2 weeks once; then publish what exists, labeled |
| I | ≥ 5 unsolicited inbound contacts (issues from strangers, emails, DMs) | 2026-10-31 | channels were wrong: `inbound-channel-mapper` re-runs with the observed data |
| P | re-open rule: ≥ 2 independent inbound parties ask to pay for the same capability | rolling | B stays empty; no exceptions |
| Whole plan | any of: a paying party, ≥ 500 combined stars, or a paid role/co-op offer that resulted from the work | 2026-11-30 | honest call: the OSS stays as career capital; the paid-role path Session 1 found becomes the recommendation |

---

## 10. Working files

```
venture/
  CLAUDE.md               # this brief
  STATE.md                # current wave, open tasks, running agents, last commit (resume point)
  SIGNALS.md              # weekly inbound/adoption signals
  DECISION.md             # Session 1's v3 + every red-team pass; v4 appended, never rewritten
  ASSETS.md STRENGTHS.md  # Session 1, redacted per §2
  ASKS.md LEDGER.md LOG.md WEEKLY.md
  ideas/                  # Session 1's dossiers (frozen); new dossiers only from signals
  research/               # Wave 1 outputs
  ventures/<pkg>/         # package working copies until first release (then their own repos)
  ventures/c-measurement/ # Track M
  outreach/queue.md       # drafts the principal posts/sends; company-level only
  scripts/prepush.sh
  private/                # GITIGNORED: PRINCIPAL.md, IDENTITY.md, DENYLIST.txt, outreach/, anything about anyone else
```

---

## 11. Session 2 runbook (in order)
1. Read `STATE.md` if it exists; otherwise create it from this brief.
2. Wave 0 and Wave 1 in parallel. Push the redaction commit first, before anything else lands on the public remote.
3. Spawn `pkg-plan-lint` and `corpus-widener` + `base-build-pilot` as soon as Wave 0 passes; they do not wait for Wave 1.
4. Verify wave on every artifact. Commit-per-artifact, push-per-unit, `STATE.md` at every checkpoint.
5. `DECISION.md` v4: one page, appended — the v2 portfolio, what would prove it wrong, dates from §9. Red-teamed like v3 was.
6. End of session: `LOG.md`, `SIGNALS.md`, `WEEKLY.md` if Sunday, everything pushed.
7. Every subsequent session starts at step 1 and runs until the current wave's done-criteria are met or the session is paused by the client. Paused is not finished; resume from `STATE.md`.

---

## 12. The four things only the principal can do
1. **Fill `private/PRINCIPAL.md`** — above all, work authorization and co-op status. Ten minutes. It gates every dollar and nothing else.
2. **Fix the `gh` login** (`gh auth login` as Alex-lop) or leave `gh` unused — the agent pushes with `git` either way. Send ASK-002's message about the leaked secret yourself; it is the decent thing and only a human should do it. Approve ASK-003 (delete the coursework branch).
3. **Set the standing approvals** in `private/PRINCIPAL.md`: repo creation, PyPI publishing, third-party OSS PRs with disclosure, Track H yes/no. Create the PyPI account once; the token goes in the local environment, never in a file.
4. **Post what is drafted and reply to what comes in.** Five minutes per release, a few minutes per inbound. That is the whole human-contact budget unless you opt into Track H.

Everything else is the swarm's. Report in files. The principal will read them.
