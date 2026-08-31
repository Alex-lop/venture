# Outreach queue

Nothing here is sent by the agent. Every item is a draft for Alex to send (RED action — see ASK-009 once this batch is complete). Each entry: the company, its own published channel, why this company, the message. No individual is named here — per-company contacts live in `private/outreach/named-targets.md`. Newest on top. Track sends in `private/outreach/crm.csv` (moved out of the tracked tree: it is a list of named people).

**Batch #1 status:** DRAFTED — 12 A-track companies (free-autopsy invitation, no price). **The B-track calls below are WITHDRAWN** (Track B killed 2026-08-30 by the EEA-portal finding — `DECISION.md` v3); they are kept as a record and as a ready list if the B slot ever re-opens on a wetlands signal. Nothing sent. Approval = ASK-009 (A only). Per `DECISION.md` v2: **no price is named anywhere in this batch.**

---

## Track M study — launch drafts (2026-08-31, **revised after the red-team pass**)

**Status:** DRAFTED. Nothing sent. The principal posts every item below; the agent posts
nothing (`CLAUDE.md` §2 RED). **No price and no pitch appears anywhere in this section** —
Changelog News rejects commercial products outright ("🚫 Commercial products/services.
Sponsorship is your path.", `research/channels.md` §1), and the study is not a product.

**What is being launched:** the Track M study — `ventures/c-measurement/study/WRITEUP.md`,
`SUMMARY.md`, `DATASET-CARD.md`, the two result CSVs and the instrument (`runner.py`,
`analysis.py`). **Blocked on one thing:** a public URL. Every `{STUDY_URL}` below is a
placeholder; nothing here can be posted until the study is live somewhere linkable.

**Revised 2026-08-31.** Three red teams reviewed the write-up; `WRITEUP.md` §Red-team pass
lists every objection and its disposition. Four things changed in these drafts and **must not
be reverted**: (1) the headline is now the **pre-registered** quantity — the PR's own
*newly-added* tests, 1 of 99 — with the all-touched-tests number as context; (2) the
"well-maintained tail / the selection biases toward 0" line is **withdrawn** (the built repos
have *fewer* stars than the unbuilt ones); (3) the 74.0% is no longer described as "the PR
added the module too" (that is 15.4%; 58.6% is collateral breakage of pre-existing tests);
(4) nothing claims a property is **specific to agents** — there is no human-PR control arm.

**The four numbers every draft must keep together** (from `python3 analysis.py`): **1 of 99**
resolved PRs added tests that all already pass on base (Wilson 95% [0.2%, 5.5%]; 0 of 41 on
`fix` PRs); **0 of 99** ship an entirely non-discriminating test file set, which is **0 of 25
repositories, [0.0%, 13.3%]** once clustering is respected; **10.5%** of the tests these PRs
*add* are `PASS_TO_PASS` against **78.0%** of all tests in the files they touch; and **58.6%**
of the `FAIL_TO_PASS` evidence is a pre-existing test collaterally broken by the patch, not a
new module. A draft that quotes one without the others is dishonest in one direction or the
other and must not be posted.

**Sequencing.** SRE Weekly and Changelog News both prefer published-first, no embargo
(`research/channels.md` §1). Post to HN, then submit to the newsletters the same day; arXiv
is on its own clock (see the endorsement gate below).

### 1. Hacker News — **regular submission, not a Show HN**

Show HN excludes reading material — "Off topic: blog posts, sign-up pages, newsletters,
lists, and other reading material. Those can't be tried out, so can't be Show HNs. Make a
regular submission instead." (`research/channels.md:87`). So: normal submit form, no "Show
HN:" prefix. `news.ycombinator.com/robots.txt` sets `Crawl-delay: 30`; the principal is
posting by hand, so it does not apply, but nothing automated touches HN either way.

**Title (79 characters, HN's cap is 80):**

> We ran 107 merged AI-agent PRs' own tests against the commit they branched from

*Alternate (72 chars), if a number reads better:* `1 of 99 merged AI-agent PRs added only
tests that already passed on base`

*(The pre-revision title — "0 of 99 merged AI-agent PRs had every test pass on base; 78% of
tests did" — is withdrawn: it led with the non-pre-registered bar and paired it with a
number computed on a different denominator.)*

**First comment (post immediately after submitting, then stay for the comment window —
`DECISION.md` §4 budgets +4 h for a launch's comments):**

> Author here. The question was narrow: when a coding agent opens a PR and the PR gets
> merged, do the tests it added actually distinguish the code before the change from the code
> after it? SWE-bench answers that during dataset construction and throws the answer away, so
> I ran it as the measurement instead. It is BSG-VA's replay (arXiv:2607.28871) applied to
> merged real-world PRs rather than benchmark rollouts.
>
> Method: take each merged PR's own test files, apply only those files to the PR's base
> commit, install from the repo's lockfile, run them twice on base and twice on the merge
> commit in a container with the network off, and classify every test id as FAIL_TO_PASS /
> PASS_TO_PASS / UNRESOLVED. 107 PRs, 25 Python repos, 99 reached a verdict.
>
> The number I pre-registered was about the tests each PR *adds*. 1 of the 99 added only
> tests that already passed at its base commit — Wilson 95% [0.2%, 5.5%], and 0 of 41 on
> fix-titled PRs. Under a looser bar (zero discriminating tests anywhere in the files the PR
> touched, new or pre-existing) it is 0 of 99 — but those 99 PRs sit in 25 repos, and with
> the repo as the unit that is 0 of 25, [0.0%, 13.3%]. Quote the wider one.
>
> The interesting part is what the tests are made of. 78.0% of all the test ids in the files
> these PRs touch pass on base and candidate alike — but 90.9% of those ids are pre-existing
> tests being re-run. Restricted to the tests the PRs actually added, only 10.5% pass on both
> sides. And of the evidence that does discriminate, only 15.4% is "the PR added the module,
> so the test could not import at base"; 58.6% is a pre-existing *passing* test that the PR's
> own test patch broke by adding an import. I had that backwards in an earlier draft; the
> crosstab that catches it is in the write-up and in the published CSVs.
>
> What it is not: a population estimate. The 25 repos are the ones whose base commit installs
> from a lockfile and runs its suite offline — 25 of 60. I originally called that "the
> well-maintained tail" and claimed the selection biased the result toward zero. That claim
> is withdrawn: the repos that built have a median 64 stars against 351 for the ones that
> did not, identical agent-PR volume, and a near-identical lock-kind mix. The filter selects
> small single-lockfile projects, and I cannot tell you which way the residual bias runs.
>
> It is also **not** a claim about agents specifically — there is no human-PR control arm
> here. The nearest published one (arXiv:2601.21194) finds human and human-agent PRs include
> tests at comparable rates, 40.0% vs 42.9%. And 92 of 107 PRs carry one trailer family, so
> it is not a per-agent comparison either. A trailer proves an agent was involved, not that
> the agent wrote the tests that landed.
>
> It does not contradict "All Smoke, No Alarm" (arXiv:2606.18168), which found 80.2% of agent
> test patches have weak or no explicit oracle signals *statically*. Different axis, and
> different denominator — the number to put beside 80.2% is my 10.5%, not my 78.0%.
>
> Instrument, both CSVs, the method with every known limit, and a script that reprints every
> number are in the repo, including a section that lists all 25 red-team objections against
> this write-up with what I fixed, what I acknowledged, and the one I rejected. The dataset
> carries no author, login, email, PR title or PR body — only repo, PR number, SHAs, test ids
> and outcomes.
>
> Disclosure: built and written with heavy AI assistance; I designed the method, reviewed the
> instrument, and I am accountable for every number. I also keep two commercial concepts in
> the same repo that a *positive* finding would have helped; the finding went the other way.
> Happy to be told what is wrong with it.

### 2. Bluesky thread (6 posts, each ≤300 characters)

Post 1/6 carries the link; the rest are replies in order. Measured lengths with a 36-character
URL substituted for `{STUDY_URL}`: 268, 246, 254, 251, 243, 264. Bluesky counts a link as its
full text, so a URL longer than ~70 characters breaks post 1 — shorten it or move it to 6/6.

> **1/6** I ran the tests from 107 merged AI-agent pull requests against the commit each PR
> branched from, to ask whether they could have caught anything. 25 Python repos, 99 reached a
> verdict. Not a comparison to human PRs — no control arm. {STUDY_URL}

> **2/6** The pre-registered number is about the tests each PR *adds*: 1 of 99 added only
> tests that already passed at its base commit. Wilson 95% [0.2%, 5.5%]. On fix-titled PRs,
> 0 of 41. The strong form of "agents write tests that can't fail" fails here.

> **3/6** Looser bar — zero discriminating tests anywhere in the files the PR touched — is
> 0 of 99. But those PRs sit in 25 repos, and two PRs of one repo supply 50.5% of the discriminating rows.
> With the repo as the unit it's 0 of 25, [0.0%, 13.3%]. Use that one.

> **4/6** The other direction: 78.0% of all test ids in the touched files pass on both sides
> — but 90.9% of those ids are pre-existing tests being re-run. Restricted to the tests these
> PRs actually *added*, only 10.5% pass on both. That's the honest comparison.

> **5/6** And I had the mechanism backwards in a draft. Only 15.4% of the discriminating
> evidence is "the PR added the module so the test couldn't import at base." 58.6% is a
> pre-existing *passing* test broken by an import the PR's own test patch added.

> **6/6** Caveats: 25 repos, chosen because their base installs from a lockfile and runs
> offline. I called that the well-maintained tail; withdrawn — they have *fewer* stars than
> the ones that failed to build. Method, CSVs, red-team log: {STUDY_URL}

### 3. PyCoder's Weekly and Changelog News — submission blurb

Both take the same text. PyCoder's: https://pycoders.com/submissions → "Submit Your Link »"
($0, "we want to hear from you about projects you are working on … and articles you want to
share"). Changelog News: https://changelog.com/news/submit ($0, free account; "Submitting
your own work is also encouraged"; no how-tos, no commercial products). Both are weekly and
notify only on publication. **Title:** *Do merged AI-agent PRs ship tests that could have
caught anything?* **URL:** `{STUDY_URL}`

> A differential-execution study of 107 merged, agent-trailered pull requests across 25 public
> Python repositories: each PR's own test files are applied to the PR's base commit, run twice
> there and twice on the merge commit in an offline container, and classified in SWE-bench's
> FAIL_TO_PASS / PASS_TO_PASS vocabulary. Of the 99 PRs that reached a verdict, exactly one
> added tests that all already passed at its base commit (Wilson 95% [0.2%, 5.5%]); under the
> looser bar of "no discriminating test anywhere in the touched files" it is 0 of 99, or 0 of
> 25 repositories once clustering is respected. But only 10.5% of the tests these PRs *add*
> pass on both sides, against 78.0% of every test in the files they touch — and 58.6% of the
> discriminating evidence turns out to be a pre-existing passing test broken by an import the
> PR's own test patch added, not a newly-arrived module. Open dataset, open instrument, every
> published number reproducible by one script, and a section listing all 25 objections three
> red teams raised against the write-up with each one's disposition. Written with AI
> assistance, disclosed in the post.

### 4. arXiv cs.SE — abstract, and the gate in front of it

**The gate, verbatim from `research/channels.md:135`:** "arXiv requires that users be
endorsed before submitting their first paper to arXiv or a new category." Endorsement needs
either a claimed co-authored paper *plus* an institutional address, or a personal endorsement
from an established arXiv author — and "**A .edu address alone does not clear the gate for a
first-time author with no claimed paper.**" arXiv also warns that "it is inappropriate to
email large numbers of potential endorsers at once."

**Consequences already recorded, not re-argued here:** `DECISION.md` §3 dates the endorsement
request at **2026-09-19** and declares the arXiv path dead if no endorser has replied in
writing by **2026-09-26**; §1.7 puts the endorser **outside Northeastern**, because
university contact is RED (`CLAUDE.md` §2). **Nothing in this section asks the agent to
contact anyone.** If the gate does not clear, the study still ships as an open dataset
release and the HN, Bluesky and newsletter drafts above are unaffected.

**Abstract (one paragraph, 262 words, 1,681 characters — under arXiv's 1,920 limit):**

> Coding agents now open a large share of pull requests on public repositories, and roughly
> half of those that touch code under test also change tests (49.6%, arXiv:2607.18057;
> 42.9% include tests at all, arXiv:2601.21194). Whether those tests could have caught
> anything has been measured statically, or dynamically on benchmark rollouts, or discarded
> as a by-product of benchmark construction. We apply BSG-VA's base/candidate replay to
> merged real-world pull requests. For 107 merged PRs carrying a verbatim coding-agent
> trailer, across 25 public Python repositories whose base commit installs from its lockfile
> and runs its suite offline, we apply each PR's own test files to the PR's base commit and
> execute them twice on base and twice on the merge commit, classifying every PR-touched test
> id as FAIL_TO_PASS, PASS_TO_PASS, or UNRESOLVED. Ninety-nine PRs reach a verdict. One added
> only tests that already pass at its base commit (1/99, Wilson 95% CI [0.2%, 5.5%]; 0/41 on
> fix-titled PRs); under the looser criterion of no discriminating test anywhere in the
> touched files, 0/99, which is 0 of 25 repositories, [0.0%, 13.3%], with the repository as
> the unit. The tests these PRs add are mostly discriminating (10.5% PASS_TO_PASS) while the
> files they touch are mostly not (78.0%), and 58.6% of FAIL_TO_PASS evidence is a
> pre-existing passing test collaterally broken by the patch. We release the instrument, both
> datasets, and the funnel, and we report the selection's covariates rather than assuming its
> direction. To our knowledge no prior work reports this rate with its denominator on merged
> agent PRs; our absence search is arXiv-metadata-dominant and we state its limits.

### Not in this section (deliberately)

- **No Show HN.** `research/channels.md:87` excludes reading material; a study is reading
  material even though the instrument is runnable.
- **No Reddit or Lobsters draft.** Both are robots-excluded, so their rules could not be read
  today and are UNVERIFIED (`research/channels.md` §0). Drafting for rules we could not fetch
  is how a submission gets removed.
- **No price, no service, no hosted anything.** Changelog News bars it and the study is not
  for sale.
- **No individual named anywhere**, including no endorser candidate — the arXiv item names a
  gate and a date, not a person.
- **No claim that any of this is specific to agents.** There is no human-PR control arm in
  the study, so no draft may say or imply one.

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

### Named A targets — 12 Boston/Cambridge companies whose own job posts name Claude Code / Cursor / Codex as internal tooling (read-only research; contacts are the companies' own published role emails or contact forms only — no individual is named; the per-company people the research found are in `private/outreach/named-targets.md`)

| # | Company | Area · size | Published channel | Why now (their own job post) | Evidence | Fit |
|---|---|---|---|---|---|---|
| 1 | **Hi Marley** | Boston, MA · ~100 employees; ~30-40 engineers; all 11 | https://www.himarley.com/contact-us/ | Clearest org-wide adopter found in Boston. Principal AI Product Engineer req: 'You live in Claude Code, Codex, and Cursor.' Sr. IT Systems Engineer req: 'Provision and manage access to Claude, ChatGPT, and Cursor; support colleagues who are building and runnin | [post](https://www.himarley.com/job-openings?gh_jid=7773714003) | 5 |
| 2 | **CloudZero** | Boston, MA · ~150 employees; ~50 engineers; 8 of 15 o | https://www.cloudzero.com/contact/ | Double exposure. Internally: Senior IT Operations Engineer (Boston) req says 'You reach for Claude Code, Claude Desktop, or ChatGPT before problem-solving manually'; Senior CloudOps Engineer (Boston) wants 'an appetite for frontier AI models such as Claude, Co | [post](https://jobs.ashbyhq.com/cloudzero/4ad891a4-8e60-4bc9-9dfd-a0a7a895a865) | 5 |
| 3 | **Reprise** | Boston, MA · ~80 employees; ~30 engineers | https://www.reprise.com/contact | Most explicit public statement of pipeline-level agent adoption found in Boston, in their own job post: 'We have aggressively used AI to change our entire build pipeline to use agent-driven recursive development cycles and we are starting to do the same on our | [post](https://jobs.ashbyhq.com/reprise/4d6b5343-170f-4ed0-8488-440acac01f32) | 4 |
| 4 | **Suno** | Cambridge, MA (Harvard Square HQ) · ~150 employees; ~50 engineers; 12 of 62  | https://jobs.ashbyhq.com/suno | They have stood up a named internal function for exactly this decision. Senior/Staff SWE, AI Engineering: 'One, AI Leverage, empowers engineers and other teams to move faster at scale with agentic tools.' Staff/Senior SWE Platform: 'Build shared infrastructure | [post](https://jobs.ashbyhq.com/suno/9e6da9b6-8562-4d9e-ae8e-c3319f76bdba) | 4 |
| 5 | **Lumafield** | Cambridge / Boston, MA (plus Everett, MA · ~200 employees; ~60 engineers; 8 of 16 o | info@lumafield.com | Agentic coding tools are a stated hiring bar even for customer-facing engineers: 'Comfortable using agentic coding tools (Claude Code, Cursor, or similar) to build tools and automations. You don't need to be a software engineer, but you should be someone who r | [post](https://jobs.lever.co/lumafield/181866d7-ffa5-4e12-b25c-aa4f1fd0bb11) | 4 |
| 6 | **Kodex** | Boston, MA (YC S21 · 30 employees per YC directory; ~15 engin | https://www.kodexglobal.com/contact | Only YC Boston company (2021+ batches) that cleared the evidence bar. Their engineering req states both the practice and the guardrail: 'We leverage AI-assisted, agentic development. We use these tools to move faster, but never ship code we can't explain, test | [post](https://jobs.ashbyhq.com/kodex/31e53827-080b-4266-945c-950005486081) | 4 |
| 7 | **Tulip Interfaces** | Somerville, MA · ~250 employees; Somerville engineering ~ | hello@tulip.co | Actively hiring a dedicated developer-experience function for agents: 'AI Enablement Engineer - Developer Experience' and 'Developer Experience Engineer' reqs both in Somerville, plus a Budapest twin. Their embedded SWE req names the tools directly - 'Experien | [post](https://tulip.co/careers/job-posting/?gh_jid=7820441003) | 4 |
| 8 | **Jellyfish** | Boston, MA (HQ · ~180 employees; ~55 engineers | hello@jellyfish.co | Two reasons. Internally, their Staff Data Engineer req calls for someone to 'spearhead development of internal tooling and agentic workflows that meaningfully accelerate engineering velocity across the org.' Commercially, they ship Jellyfish AI Impact, the pro | [post](https://jobs.ashbyhq.com/jellyfish/255c6eee-7ab8-431b-a007-4b637dccee40) | 3 |
| 9 | **Fairmarkit** | Boston, MA · ~100 employees; ~30 engineers; 4 of 7 op | https://www.fairmarkit.com/careers | Standing up a greenfield agent team in Boston right now: 'Agentic AI Engineer (Boston, Hybrid)' - 'Fairmarkit is building a brand new AI and Agentic business line from scratch, and we're assembling a small, elite founding team around it. This is one of the fir | [post](https://job-boards.greenhouse.io/fairmarkit/jobs/6111188004) | 3 |
| 10 | **Lila Sciences** | Cambridge, MA · Cambridge software + data platform group | https://job-boards.greenhouse.io/lilasciences | Names the exact tools as a hiring requirement: Staff Engineer, Data Platform - 'Proficiency with AI-assisted development tools (Cursor, Claude Code, or similar) and ability to incorporate them effectively into day-to-day engineering work.' They also have a Cam | [post](https://job-boards.greenhouse.io/lilasciences/jobs/4222065009) | 3 |
| 11 | **EverQuote** | Cambridge, MA · ~350 employees - engineering is ABOVE th | https://careers.everquote.com | Two Cambridge engineering reqs name the stack explicitly. Senior Full Stack Engineer II: 'proficiency in using AI coding tools (e.g., Claude Code, Copilot) in the full software development lifecycle, including designing, generating code, testing, monitoring an | [post](https://careers.everquote.com/job/?gh_jid=7670496003) | 3 |
| 12 | **ClearGov** | Boston area (Wellesley, MA HQ) - but pla · ~120 employees; ~35 engineers | info@cleargov.com | The most complete tool list of any board surveyed: Sr. Software Engineer - Platform asks for 'Experience using AI-assisted development tools such as Cursor, Windsurf, Claude Code, GitHub Copilot, CodeRabbit, Greptile, or similar.' A team that lists six tools h | [post](https://job-boards.greenhouse.io/cleargov/jobs/4371916009) | 2 |

**Personalization line per company:** quote their own job post — e.g. *"your Principal AI Product Engineer req says 'you live in Claude Code, Codex, and Cursor' — that's the setup I autopsy."* Do **not** reference the HN Cursor thread: it is pseudonymous and names no Boston company (verified).

**Caveats from the research:** WebSearch was exhausted, so this list comes from Greenhouse/Ashby/Lever job-board APIs across ~66 Boston boards; the YC Boston 2021+ directory does NOT support the thesis (51 active companies, mostly biotech/hardware; ~11 software firms in band, only Kodex cleared the evidence bar). EverQuote and Tulip are above the 5–50 band; ClearGov's platform team is in Calgary. Cold email to a CTO is the weakest channel here — the plan is to meet people at Venture Café first and use these as the follow-up/warm list.


---

## B — practitioner calls — **WITHDRAWN 2026-08-30** (B killed before sending; kept as a record)

**One question, asked of firms already named in this week's sample digest:** *"Does a material share of your work arrive after a Notice of Intent is already on a Conservation Commission agenda — from a party not already on the filing? Or are you always the one who filed it?"* Secondary: *"Do you use BLDUP, masspublicnotices.org, or a town's Notify Me emails today, and what do they miss?"*

### Email — template (Alex sends; no attachment; the sample is offered, not pushed)
**Subject:** quick question from a Northeastern student about how wetlands work gets awarded

> Hi {first name},
>
> I'm a CS student at Northeastern doing a small research project on Massachusetts conservation-commission filings. This week I compiled every ConCom and planning-board agenda item across 30 Greater Boston towns — {firm} shows up on {N} of them ({town}, {date}, {address}), which is why I'm writing to you rather than to a directory.
>
> I have one honest question and it decides whether the project is useful to anyone or just interesting to me: **when a Notice of Intent hits an agenda, is the wetlands scientist / engineer already hired — or does work still get awarded after that point (peer review, replication, monitoring, a consultant swap)?**
>
> Fifteen minutes on the phone would answer it. In return I'll send you the full 30-town compilation for this week, free, whatever you say. {slot 1} or {slot 2}?
>
> Alex Lopez
> Northeastern University, CS + Math '28

### Named B targets — 15 firms from read-only research (firms only; contact = the firm's own published business channel; no individual is named here — the per-firm people are in `private/outreach/named-targets.md`; no social-network scraping)

**Call first (the kill/revive test — pick three, answers decide B on 2026-09-15):**

| # | Firm | Town | Type | Published channel | Size | Named this week | Evidence | Why this firm |
|---|---|---|---|---|---|---|---|---|
| 1 | **Environmental Consulting & Restoration, LLC (ECR)** (fit 5) | Plymouth | wetlands + restoration | https://ecrwetlands.com/contact-us/ (form; site 403s non-browsers — verify live) | 4–6 | Named on the agenda as the representative of record ("Representative: (individual), ECR") — NOI, 1 Sycamore Lane, DEP 034-1569, Hingham ConCom 2026-08-31 | [agenda](https://www.hingham-ma.gov/AgendaCenter/ViewFile/Agenda/_08312026-11227) | Four-person shop that says on its own team page it partners with engineering/survey firms to win work; restoration + delineation + permitting is exactly the digest's section 0 |
| 2 | **Goddard Consulting LLC** (fit 5) | Northborough | wetlands | info@goddardconsultingllc.com (site footer) / contact form | 8–15 | Wetlands consultant of record, NOI, 281 Main Street, Reading — continued hearing, Reading ConCom 2026-08-26 | [agenda](https://www.readingma.gov/DocumentCenter/View/24619/2026-08-26-Conservation-Commission-Agenda) | Pure-play wetlands consultancy, four MA offices, no product of its own; every NOI in the digest is one of their jobs or a competitor's |
| 3 | **EBT Environmental Consultants, Inc.** (fit 5) | North Oxford | wetlands | no company-level channel published — the only published contact is a personal address (withheld; see `private/outreach/named-targets.md`) | 1–3 | Environmental consultant of record — "Pleasant View Trust c/o EBT Environmental Consultants, DEP 95-1025", NOI, 167-171 Pleasant St, Ashland ConCom 2026-08-24 | [agenda](https://www.ashlandmass.com/AgendaCenter/ViewFile/Agenda/_08242026-7950) | Est. 1986, one or two people, works "as a subcontractor to engineering, survey and architectural firms" (their words) — the persona the B thesis needs, and the one most likely to say the vendor is always already on the filing |
| 4 | **Chongris Engineering LLC** (fit 5) | Andover | septic / stormwater civil | https://chongrisengineering.com/contact/ (form; the other published address is a personal one, withheld) | 1–5 | Civil engineer of record (base survey), Brookline 2026-08-26; and Wellesley Design Review Board, 15 Lathrop Road Large House Review, 2026-09-02 | [agenda](https://wellesleyma.gov/AgendaCenter/ViewFile/Agenda/_09022026-9582) | Headline is "Fast Permitting. Short Lead Times." — a firm that sells on permit velocity is the one most likely to value permit visibility |
| 5 | **Reed Land Surveying, Inc.** (fit 5) | Lakeville | survey | no company-level channel published — the only published address is a personal one (withheld) | 4–8 | Surveyor of record on a Reading conservation item, 2026-08-26 | [agenda](https://www.readingma.gov/DocumentCenter/View/24619/2026-08-26-Conservation-Commission-Agenda) | Their site names their buyers — civil engineers, developers, GCs, site contractors — i.e. the applicants in this digest; an Order of Conditions today is a stakeout job in six weeks (the post-filing scope question, in their own business) |
| 6 | **Continental Land Survey, LLC (C&L)** (fit 5) | Franklin / Needham | survey | survey@clsurveyma.com (printed on the agenda itself) | 1–2 | Land surveyor of record, Wellesley Design Review Board, 15 Lathrop Road (LHR-26-06), 2026-09-02 | [agenda](https://wellesleyma.gov/AgendaCenter/ViewFile/Agenda/_09022026-9582) | One-surveyor shop whose listed service area (~50 MetroWest/South Shore towns) nearly matches the digest's coverage |

**Hold (send only if B survives the first three calls):**

| # | Firm | Town | Type | Published channel | Size | Named this week | Evidence | Why this firm |
|---|---|---|---|---|---|---|---|---|
| 7 | **LEC Environmental Consultants, Inc.** (fit 4) | Wakefield / Plymouth | wetlands | northlec@lecenvironmental.com; marketing@lecenvironmental.com (published; site is http-only) | 20–30 | Named of record in the sample (see digest §5) | see digest §5 | Mid-size wetlands firm with a published marketing address — the least cold of the wetlands set |
| 8 | **Merrill Engineers and Land Surveyors** (fit 4) | Hanover | civil + survey | https://merrillinc.com/contact/ (form has a "Service(s) I can provide Merrill" option) | 40–60 | Named of record in the sample | see digest §5 | Vendor-inbound path exists on their own site |
| 9 | **Highpoint Engineering, Inc.** (fit 4) | Dedham | civil / stormwater | https://highpointeng.com/contact/ | 15–20 | Named of record in the sample (Needham ×2) | see digest §5 | Sells Permit Expediting and Stormwater Inspections as service lines — already monetises permit navigation; fastest possible sale or the clearest "we already track this" |
| 10 | **Water & Wetland** (fit 4) | South Grafton | aquatic / wetland restoration | no company-level channel published — the only published address is a personal one (withheld) | 10–20 | — | — | Restoration contractor: the persona most likely to be hired AFTER an Order of Conditions (replication/monitoring) — a direct test of the post-filing-scope question |
| 11 | **Field Resources, Inc.** (fit 4) | Needham | survey | office@fieldresources.net (published; http-only) | 5–15 | Named of record in the sample | see digest §5 | Needham-based; sample density is high there |
| 12 | **Green Seal Environmental, LLC** (fit 4) | Canton (project) | environmental engineering | in person — Canton Planning Board 2026-09-02 (the only public evidence is the agenda itself) | unknown | Named on Canton PB agenda 2026-09-02 | see digest | Meet at the hearing, not by email |
| 13 | **Beals and Thomas, Inc.** (fit 3) | Southborough | civil / survey / wetland science | mail@bealsandthomas.com | 50–70 | Named of record in the sample (Needham) | see digest §5 | Larger; likely already served — useful as a "what do you use today" call |
| 14 | **Activitas, Inc.** (fit 3) | Dedham | landscape + civil | admin@activitas.com | ~13 | Named of record in the sample (Reading) | see digest §5 | Adjacent persona |
| 15 | **Horsley Witten Group, Inc.** (fit 3) | Sandwich | stormwater / environmental | hwinfo@horsleywitten.com | 80–100 | — | — | Too large for the wedge; a good "what do you use today" reference call |

**Personalization line per firm** (drops into the `{firm} shows up on {N} of them` sentence): use the "Named this week" cell verbatim, with the agenda link.

**Research notes:** none of the 15 shows any BLDUP/Dodge/ConstructConnect reference on its site; Highpoint sells permit expediting; Merrill's contact form has a vendor-inbound option; ECR's site 403s non-browser clients (re-check live); EBT publishes no company-level mailbox — its only published contact is a personal ISP address, so it has no usable public channel for this purpose. Excluded: firms with no usable web presence (McCarty, Choubah, Connorstone) and national firms already served (VHB, Weston & Sampson, CDM Smith, Kimley-Horn, TRC, Foth, Wright-Pierce, Epsilon, Control Point).

---

## Not in this batch (deliberately)
- No sales email to the 45 firms in `private/outreach/crm.csv` — the red team showed the lead-feed thesis is unproven and the sample was still advertising a price and a field it can't deliver (both fixed). Nothing goes to them until the three calls come back.
- No message to BLDUP — but see `DECISION.md` open questions: an informational interview there is worth more than a crawler.
