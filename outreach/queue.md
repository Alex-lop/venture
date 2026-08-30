# Outreach queue

Nothing here is sent by the agent. Every item is a draft for Alex to send (RED action — see ASK-009 once this batch is complete). Each entry: who, channel, why this person, the message. Newest on top. Track sends in `crm.csv`.

**Batch #1 status:** DRAFTED — 12 A-track companies (free-autopsy invitation, no price). **The B-track calls below are WITHDRAWN** (Track B killed 2026-08-30 by the EEA-portal finding — `DECISION.md` v3); they are kept as a record and as a ready list if the B slot ever re-opens on a wetlands signal. Nothing sent. Approval = ASK-009 (A only). Per `DECISION.md` v2: **no price is named anywhere in this batch.**

---

## A — free "agent autopsy" (unpriced experiment; gate: 5 accepted by 2026-09-30)

### In the room (Venture Café Cambridge, Thursdays 4:30–8 pm) — the 20-second version
> I'm Alex, CS at Northeastern. I've spent the summer running parallel coding agents on my own repos with fences and audit trails — about 230K lines of it, all tested. I'm doing free 60-minute "agent autopsies" for a handful of engineering leads: you pick a repo, I run Microsoft's free readiness checker and Claude Code's `/doctor` on it live, and then I show you the three places in *your* codebase where an agent will do something you'd never let a junior do — the invariants worth a hook. No pitch, no price; I'm collecting what breaks. Want one?


### September calendar for A (verified from the organizers' pages, 2026-08-30)
| Date | Event | Why / note |
|---|---|---|
| **Thu 2026-09-03**, 4:30 pm | Venture Café Cambridge — "Uncertainty Principle: AI, Quantum, and the Tools Reshaping Work" (CIC, 1 Broadway) | The right room, five days after the Cursor news. Skip AI Tinkerers the same night (GTM theme). |
| Thu 2026-09-10 | Venture Café — "University of Tsukuba Night" | Low value for this thesis; optional. |
| **Thu 2026-09-17**, 6–8:30 pm | **"AI Native Dev Boston: Inside the Dark Factory"** — AI Security Engineers community, at Snyk, 100 Summer St | Collides with Venture Café; **take the meetup** — it targets teams already shipping with coding agents. Registration via the Luma link on the meetup page. |
| Thu 2026-09-24 | Venture Café — Thursday Gathering | Second Venture Café night (capacity rule: two per month). |
| Thu 2026-10-01 | **Boston AI Week @ Venture Café** | Hold. |

### Follow-up email (send within 24 h of meeting someone) — template
**Subject:** the autopsy — 60 min, your repo, no pitch

> Hi {first name},
>
> Good to meet you at Venture Café on Thursday. As promised: a free 60-minute agent autopsy on {repo or team}.
>
> What happens: on a call, on a throwaway clone you control, I run `microsoft/agentrc` (free, Microsoft's readiness scorer — it will tell you your Python repo has no linter, which is the fun part), Claude Code's `/doctor` on your `CLAUDE.md`/`AGENTS.md` if you have one, and `cc-safety-net`. Then the part no tool does: I read your codebase for an hour beforehand and bring the three repo-specific invariants I'd put a hook on — the "never write raw SQL outside `db/`" kind, not the "don't `rm -rf`" kind. You keep the notes. If nothing's useful, you've lost an hour and I've learned something.
>
> Two slots next week: {slot 1}, {slot 2}. Reply with a repo (read-only is fine) and one thing your agents keep getting wrong.
>
> Alex
> _(CS+Math, Northeastern '28 · {github link} — the fenced-agent control plane and the patch-verification engine are both there, with the tests)_

**Why this works:** every claim is demonstrable in the meeting; the free tools are named honestly (the red team's point); the deliverable named is the one thing no free tool ships. **Why this person:** filled per target below.

### Named A targets — 12 Boston/Cambridge companies whose own job posts name Claude Code / Cursor / Codex as internal tooling (read-only research; contacts are published role emails or contact forms only)

| # | Company | Area · size | Eng lead (published) | Published channel | Why now (their own job post) | Evidence | Fit |
|---|---|---|---|---|---|---|---|
| 1 | **Hi Marley** | Boston, MA · ~100 employees; ~30-40 engineers; all 11 | Jonathan Tushman (CTO and Chief AI Officer) | https://www.himarley.com/contact-us/ | Clearest org-wide adopter found in Boston. Principal AI Product Engineer req: 'You live in Claude Code, Codex, and Cursor.' Sr. IT Systems Engineer req: 'Provision and manage access to Claude, ChatGPT, and Cursor; support colleagues who are building and runnin | [post](https://www.himarley.com/job-openings?gh_jid=7773714003) | 5 |
| 2 | **CloudZero** | Boston, MA · ~150 employees; ~50 engineers; 8 of 15 o | Erik Peterson (Co-founder & CTO) | https://www.cloudzero.com/contact/ | Double exposure. Internally: Senior IT Operations Engineer (Boston) req says 'You reach for Claude Code, Claude Desktop, or ChatGPT before problem-solving manually'; Senior CloudOps Engineer (Boston) wants 'an appetite for frontier AI models such as Claude, Co | [post](https://jobs.ashbyhq.com/cloudzero/4ad891a4-8e60-4bc9-9dfd-a0a7a895a865) | 5 |
| 3 | **Reprise** | Boston, MA · ~80 employees; ~30 engineers | Erez Segall (Vice President, Engineering) | https://www.reprise.com/contact | Most explicit public statement of pipeline-level agent adoption found in Boston, in their own job post: 'We have aggressively used AI to change our entire build pipeline to use agent-driven recursive development cycles and we are starting to do the same on our | [post](https://jobs.ashbyhq.com/reprise/4d6b5343-170f-4ed0-8488-440acac01f32) | 4 |
| 4 | **Suno** | Cambridge, MA (Harvard Square HQ) · ~150 employees; ~50 engineers; 12 of 62  | Mikey Shulman (Co-Founder & CEO (no CTO or VP Eng is publish) | https://jobs.ashbyhq.com/suno | They have stood up a named internal function for exactly this decision. Senior/Staff SWE, AI Engineering: 'One, AI Leverage, empowers engineers and other teams to move faster at scale with agentic tools.' Staff/Senior SWE Platform: 'Build shared infrastructure | [post](https://jobs.ashbyhq.com/suno/9e6da9b6-8562-4d9e-ae8e-c3319f76bdba) | 4 |
| 5 | **Lumafield** | Cambridge / Boston, MA (plus Everett, MA · ~200 employees; ~60 engineers; 8 of 16 o | Andreas Bastian (CTO (Ryan Buck is Head of Engineering, also n) | info@lumafield.com | Agentic coding tools are a stated hiring bar even for customer-facing engineers: 'Comfortable using agentic coding tools (Claude Code, Cursor, or similar) to build tools and automations. You don't need to be a software engineer, but you should be someone who r | [post](https://jobs.lever.co/lumafield/181866d7-ffa5-4e12-b25c-aa4f1fd0bb11) | 4 |
| 6 | **Kodex** | Boston, MA (YC S21 · 30 employees per YC directory; ~15 engin | Danny Mendoza (CTO / Co-founder) | https://www.kodexglobal.com/contact | Only YC Boston company (2021+ batches) that cleared the evidence bar. Their engineering req states both the practice and the guardrail: 'We leverage AI-assisted, agentic development. We use these tools to move faster, but never ship code we can't explain, test | [post](https://jobs.ashbyhq.com/kodex/31e53827-080b-4266-945c-950005486081) | 4 |
| 7 | **Tulip Interfaces** | Somerville, MA · ~250 employees; Somerville engineering ~ | Not published - no engineering executive (Owning role is the open AI Enablement Enginee) | hello@tulip.co | Actively hiring a dedicated developer-experience function for agents: 'AI Enablement Engineer - Developer Experience' and 'Developer Experience Engineer' reqs both in Somerville, plus a Budapest twin. Their embedded SWE req names the tools directly - 'Experien | [post](https://tulip.co/careers/job-posting/?gh_jid=7820441003) | 4 |
| 8 | **Jellyfish** | Boston, MA (HQ · ~180 employees; ~55 engineers | Not published by full name - their About (Co-founder (R&D leadership); no exec titles p) | hello@jellyfish.co | Two reasons. Internally, their Staff Data Engineer req calls for someone to 'spearhead development of internal tooling and agentic workflows that meaningfully accelerate engineering velocity across the org.' Commercially, they ship Jellyfish AI Impact, the pro | [post](https://jobs.ashbyhq.com/jellyfish/255c6eee-7ab8-431b-a007-4b637dccee40) | 3 |
| 9 | **Fairmarkit** | Boston, MA · ~100 employees; ~30 engineers; 4 of 7 op | Victor Kushch (Chief Technology Officer & Cofounder) | https://www.fairmarkit.com/careers | Standing up a greenfield agent team in Boston right now: 'Agentic AI Engineer (Boston, Hybrid)' - 'Fairmarkit is building a brand new AI and Agentic business line from scratch, and we're assembling a small, elite founding team around it. This is one of the fir | [post](https://job-boards.greenhouse.io/fairmarkit/jobs/6111188004) | 3 |
| 10 | **Lila Sciences** | Cambridge, MA · Cambridge software + data platform group | Not published - no engineering executive (Head of Software Product (open req)) | https://job-boards.greenhouse.io/lilasciences | Names the exact tools as a hiring requirement: Staff Engineer, Data Platform - 'Proficiency with AI-assisted development tools (Cursor, Claude Code, or similar) and ability to incorporate them effectively into day-to-day engineering work.' They also have a Cam | [post](https://job-boards.greenhouse.io/lilasciences/jobs/4222065009) | 3 |
| 11 | **EverQuote** | Cambridge, MA · ~350 employees - engineering is ABOVE th | Tomas Revesz (Co-founder & Chief Technology Officer) | https://careers.everquote.com | Two Cambridge engineering reqs name the stack explicitly. Senior Full Stack Engineer II: 'proficiency in using AI coding tools (e.g., Claude Code, Copilot) in the full software development lifecycle, including designing, generating code, testing, monitoring an | [post](https://careers.everquote.com/job/?gh_jid=7670496003) | 3 |
| 12 | **ClearGov** | Boston area (Wellesley, MA HQ) - but pla · ~120 employees; ~35 engineers | Clarence Pong (Chief Technology Officer) | info@cleargov.com | The most complete tool list of any board surveyed: Sr. Software Engineer - Platform asks for 'Experience using AI-assisted development tools such as Cursor, Windsurf, Claude Code, GitHub Copilot, CodeRabbit, Greptile, or similar.' A team that lists six tools h | [post](https://job-boards.greenhouse.io/cleargov/jobs/4371916009) | 2 |

**Personalization line per company:** quote their own job post — e.g. *"your Principal AI Product Engineer req says 'you live in Claude Code, Codex, and Cursor' — that's the setup I autopsy."* Do **not** reference the HN Cursor thread: it is pseudonymous and names no Boston company (verified).

**Caveats from the research:** WebSearch was exhausted, so this list comes from Greenhouse/Ashby/Lever job-board APIs across ~66 Boston boards; the YC Boston 2021+ directory does NOT support the thesis (51 active companies, mostly biotech/hardware; ~11 software firms in band, only Kodex cleared the evidence bar). EverQuote and Tulip are above the 5–50 band; ClearGov's platform team is in Calgary. Cold email to a CTO is the weakest channel here — the plan is to meet people at Venture Café first and use these as the follow-up/warm list.


---

## B — practitioner calls — **WITHDRAWN 2026-08-30** (B killed before sending; kept as a record)

**One question, asked of firms already named in this week's sample digest:** *"Does a material share of your work arrive after a Notice of Intent is already on a Conservation Commission agenda — from a party not already on the filing? Or are you always the one who filed it?"* Secondary: *"Do you use BLDUP, masspublicnotices.org, or a town's Notify Me emails today, and what do they miss?"*

### Email — template (Alex sends; no attachment; the sample is offered, not pushed)
**Subject:** quick question from a Northeastern student about how wetlands work gets awarded

> Hi {name},
>
> I'm a CS student at Northeastern doing a small research project on Massachusetts conservation-commission filings. This week I compiled every ConCom and planning-board agenda item across 30 Greater Boston towns — {firm} shows up on {N} of them ({town}, {date}, {address}), which is why I'm writing to you rather than to a directory.
>
> I have one honest question and it decides whether the project is useful to anyone or just interesting to me: **when a Notice of Intent hits an agenda, is the wetlands scientist / engineer already hired — or does work still get awarded after that point (peer review, replication, monitoring, a consultant swap)?**
>
> Fifteen minutes on the phone would answer it. In return I'll send you the full 30-town compilation for this week, free, whatever you say. {slot 1} or {slot 2}?
>
> Alex Lopez
> Northeastern University, CS + Math '28

### Named B targets — 15 firms from read-only research (firms, not individuals; contact = the firm's own published business channel; no social-network scraping)

**Call first (the kill/revive test — pick three, answers decide B on 2026-09-15):**

| # | Firm | Town | Type | Named principal | Published channel | Size | Named this week | Evidence | Why this firm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Environmental Consulting & Restoration, LLC (ECR)** (fit 5) | Plymouth | wetlands + restoration | Brad Holmes, Founder | https://ecrwetlands.com/contact-us/ (form; site 403s non-browsers — verify live) | 4–6 | Named by name on the agenda — "Representative: Brad Holmes, ECR" — NOI, 1 Sycamore Lane, DEP 034-1569, Hingham ConCom 2026-08-31 | [agenda](https://www.hingham-ma.gov/AgendaCenter/ViewFile/Agenda/_08312026-11227) | Four-person shop that says on its own team page it partners with engineering/survey firms to win work; restoration + delineation + permitting is exactly the digest's section 0 |
| 2 | **Goddard Consulting LLC** (fit 5) | Northborough | wetlands | Scott Goddard, Founder (PWS) | info@goddardconsultingllc.com (site footer) / contact form | 8–15 | Wetlands consultant of record, NOI, 281 Main Street, Reading — continued hearing, Reading ConCom 2026-08-26 | [agenda](https://www.readingma.gov/DocumentCenter/View/24619/2026-08-26-Conservation-Commission-Agenda) | Pure-play wetlands consultancy, four MA offices, no product of its own; every NOI in the digest is one of their jobs or a competitor's |
| 3 | **EBT Environmental Consultants, Inc.** (fit 5) | North Oxford | wetlands | Glenn Krevosky (the firm's published contact) | glenn.krevosky@charter.net (published as the firm contact in the site header/footer) | 1–3 | Environmental consultant of record — "Pleasant View Trust c/o EBT Environmental Consultants, DEP 95-1025", NOI, 167-171 Pleasant St, Ashland ConCom 2026-08-24 | [agenda](https://www.ashlandmass.com/AgendaCenter/ViewFile/Agenda/_08242026-7950) | Est. 1986, one or two people, works "as a subcontractor to engineering, survey and architectural firms" (their words) — the persona the B thesis needs, and the one most likely to say the vendor is always already on the filing |
| 4 | **Chongris Engineering LLC** (fit 5) | Andover | septic / stormwater civil | Alek Chongris | alek@chongrisengineering.com (published firm contact) / /contact/ | 1–5 | Civil engineer of record (base survey), Brookline 2026-08-26; and Wellesley Design Review Board, 15 Lathrop Road Large House Review, 2026-09-02 | [agenda](https://wellesleyma.gov/AgendaCenter/ViewFile/Agenda/_09022026-9582) | Headline is "Fast Permitting. Short Lead Times." — a firm that sells on permit velocity is the one most likely to value permit visibility |
| 5 | **Reed Land Surveying, Inc.** (fit 5) | Lakeville | survey | Glen D. Reed, PLS, President | glen@reedlandsurveying.com (published) | 4–8 | Surveyor of record on a Reading conservation item, 2026-08-26 | [agenda](https://www.readingma.gov/DocumentCenter/View/24619/2026-08-26-Conservation-Commission-Agenda) | Their site names their buyers — civil engineers, developers, GCs, site contractors — i.e. the applicants in this digest; an Order of Conditions today is a stakeout job in six weeks (the post-filing scope question, in their own business) |
| 6 | **Continental Land Survey, LLC (C&L)** (fit 5) | Franklin / Needham | survey | Christopher C. Charlton, PLS, owner | survey@clsurveyma.com (printed on the agenda itself) | 1–2 | Land surveyor of record, Wellesley Design Review Board, 15 Lathrop Road (LHR-26-06), 2026-09-02 | [agenda](https://wellesleyma.gov/AgendaCenter/ViewFile/Agenda/_09022026-9582) | One-surveyor shop whose listed service area (~50 MetroWest/South Shore towns) nearly matches the digest's coverage |

**Hold (send only if B survives the first three calls):**

| # | Firm | Town | Type | Named principal | Published channel | Size | Named this week | Evidence | Why this firm |
|---|---|---|---|---|---|---|---|---|---|
| 7 | **LEC Environmental Consultants, Inc.** (fit 4) | Wakefield / Plymouth | wetlands | Ann M. Marton, President | northlec@lecenvironmental.com; marketing@lecenvironmental.com (published; site is http-only) | 20–30 | Named of record in the sample (see crm.csv) | see digest §5 | Mid-size wetlands firm with a published marketing address — the least cold of the wetlands set |
| 8 | **Merrill Engineers and Land Surveyors** (fit 4) | Hanover | civil + survey | Joshua M. Bows, PE, President | https://merrillinc.com/contact/ (form has a "Service(s) I can provide Merrill" option) | 40–60 | Named of record in the sample | see digest §5 | Vendor-inbound path exists on their own site |
| 9 | **Highpoint Engineering, Inc.** (fit 4) | Dedham | civil / stormwater | Douglas Hartnett, PE, President | https://highpointeng.com/contact/ | 15–20 | Named of record in the sample (Needham ×2) | see digest §5 | Sells Permit Expediting and Stormwater Inspections as service lines — already monetises permit navigation; fastest possible sale or the clearest "we already track this" |
| 10 | **Water & Wetland** (fit 4) | South Grafton | aquatic / wetland restoration | Joe Onorato, Co-Founder | Joe@waterandwetland.com (published) | 10–20 | — | — | Restoration contractor: the persona most likely to be hired AFTER an Order of Conditions (replication/monitoring) — a direct test of the post-filing-scope question |
| 11 | **Field Resources, Inc.** (fit 4) | Needham | survey | (none published) | office@fieldresources.net (published; http-only) | 5–15 | Named of record in the sample | see digest §5 | Needham-based; sample density is high there |
| 12 | **Green Seal Environmental, LLC** (fit 4) | Canton (project) | environmental engineering | Stuart Clark, PE, VP Engineering Services | in person — Canton Planning Board 2026-09-02 (the only public evidence is the agenda itself) | unknown | Named on Canton PB agenda 2026-09-02 | see digest | Meet at the hearing, not by email |
| 13 | **Beals and Thomas, Inc.** (fit 3) | Southborough | civil / survey / wetland science | Stacy Minihane, PWS, Principal | mail@bealsandthomas.com | 50–70 | Named of record in the sample (Needham) | see digest §5 | Larger; likely already served — useful as a "what do you use today" call |
| 14 | **Activitas, Inc.** (fit 3) | Dedham | landscape + civil | Patrick Maguire, RLA, Managing Principal | admin@activitas.com | ~13 | Named of record in the sample (Reading) | see digest §5 | Adjacent persona |
| 15 | **Horsley Witten Group, Inc.** (fit 3) | Sandwich | stormwater / environmental | Rich Claytor, PE, Principal | hwinfo@horsleywitten.com | 80–100 | — | — | Too large for the wedge; a good "what do you use today" reference call |

**Personalization line per firm** (drops into the `{firm} shows up on {N} of them` sentence): use the "Named this week" cell verbatim, with the agenda link.

**Research notes:** none of the 15 shows any BLDUP/Dodge/ConstructConnect reference on its site; Highpoint sells permit expediting; Merrill's contact form has a vendor-inbound option; ECR's site 403s non-browser clients (re-check live); EBT's published contact is a charter.net address used as the firm's business contact. Excluded: firms with no usable web presence (McCarty, Choubah, Connorstone) and national firms already served (VHB, Weston & Sampson, CDM Smith, Kimley-Horn, TRC, Foth, Wright-Pierce, Epsilon, Control Point).

---

## Not in this batch (deliberately)
- No sales email to the 45 firms in `crm.csv` — the red team showed the lead-feed thesis is unproven and the sample was still advertising a price and a field it can't deliver (both fixed). Nothing goes to them until the three calls come back.
- No message to BLDUP — but see `DECISION.md` open questions: an informational interview there is worth more than a crawler.
