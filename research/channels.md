# Inbound channels — where platform-engineering and AI-enablement leads actually read, and every $0 submission mechanism, verified 2026-08-30 · author: `inbound-channel-mapper` (Wave 1) · bias label: NOT instrument-biased (HN+GitHub = 9 of 52 citations, 17.3%) · fix pass applied 2026-08-30 after quote-verification

**Summary (answers: where do we post, at what cost, under what rules, by when).**
1. **Ranked hypothesis, not a measured finding:** the best-ranked bets for *unsolicited* inbound by 2026-10-31 are a Show HN of a runnable package and MCP-registry auto-indexing (official registry → Glama/PulseMCP mirrors, zero marginal effort per package). Conversion rate for both is **UNVERIFIED** — nothing in this file measures inbound per channel; the §9 gate (≥5 unsolicited contacts by 2026-10-31) is the test that can falsify the ranking.
2. Show HN's rules kill the study and any docs site: "Off topic: blog posts, sign-up pages, newsletters, lists, and other reading material." The study goes to HN as a *regular* submission, never a Show HN.
3. Newsletters with a real $0 submission form and no paywall: Changelog News, PyCoder's Weekly, Awesome Python Weekly (LibHunt), Console.dev (editorial, no form — email), SRE Weekly (reply-to-email, no embargoed content). TLDR/TLDR AI and mcp.so's fast lane are **paid** and are skipped; SRE Weekly sells sponsorship (paid) separately from its $0 reply-to-email editorial path, which is the one we use.
4. Changelog News explicitly bars us if we look commercial: "🚫 Commercial products/services. Sponsorship is your path." — pitch the OSS package and the study, never a hosted tier.
5. The MCP Contributor Discord bars marketing outright ("Service or product marketing — Keep discussions vendor-neutral"); Python Discord bars "unapproved advertising". No Discord is a launch venue; they are support venues.
6. PulseMCP submissions are **paused**; it tells you to publish to the official registry instead, which is the same action that also feeds Glama (80,479 servers indexed as of 2026-08-31).
7. arXiv cs.SE has a first-submission **endorsement gate** that an institutional email alone does not clear (it also requires a claimed co-authored paper) — this is a dated dependency, not a formality: start ≥3 weeks before 2026-10-10.
8. Papers with Code is **gone** — paperswithcode.com now 302s to huggingface.co/papers/trending. HF Papers is the replacement and needs an arXiv ID.
9. Boston, verified from organizers today: Venture Café Thursdays run 09-03, 09-10, 09-17, 09-24, 10-01; **Boston AI Week 2026 is 2026-09-16 → 10-28, core week 09-24 → 10-02** (queue.md's "Thu 2026-10-01 Boston AI Week" is the Venture Café night inside it, not the week).
10. Two queue.md entries did not re-verify: the AI Native Dev Boston meetup slug 404s, and PyData Boston-Cambridge has **no upcoming event** listed. Both are marked UNVERIFIED below with what to check.

---

## 0. What "reachable" meant today

Every fetch below used `curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)"` unless marked WebFetch/WebSearch/`gh api`. robots.txt was fetched first for every host in the instrument log.

**Two hosts are robots-excluded and were therefore NOT crawled:**
- `https://www.reddit.com/robots.txt` and `https://old.reddit.com/robots.txt` (fetched 2026-08-30) both end in `User-agent: *` / `Disallow: /`. Every Reddit rule below is **UNVERIFIED** — quoted rule text could not be obtained without violating the brief.
- `https://lobste.rs/robots.txt`: `User-agent: *` / `Crawl-delay: 1` / `Disallow: /`. Lobsters is also invite-only. **UNVERIFIED, skip.**
- `https://pypi.org/robots.txt` disallows `/pypi/*/json`, so the PyPI JSON API was not used; `pypi.org/classifiers/` is not disallowed and was fetched.

---

## 1. Newsletters — submission mechanism, cost, norms verbatim

| Newsletter | Submission mechanism (URL) | Cost | Norms (verbatim where quoted) | Lead time | Verified |
|---|---|---|---|---|---|
| **Changelog News** | https://changelog.com/news/submit | $0 (free account to submit) | "Submitting other people's work is encouraged. Submitting your own work is also encouraged." · "🚫 How-to's and tutorials." · "🚫 Commercial products/services. Sponsorship is your path." · "🚫 Reader-hostile websites." · "The golden rule: if your fellow devs will find it interesting, submit it. That being said... we get a lot of submissions. Do your best to convince us why something is newsworthy. You'll be notified via email if and when your submission gets published." | Weekly cadence; notified only on publication | 2026-08-30 |
| **PyCoder's Weekly** | https://pycoders.com/submissions → "Submit Your Link »" | $0 | "At PyCoder's Weekly we believe in showcasing the best work available in the Python community. We want to hear from you about projects you are working on, conferences you are running, and articles you want to share." · "And while we cannot guarantee to feature every submitted link in the newsletter, we take everything you send us into consideration." | Weekly (issue #749 dated 2026-08-25); community-submitted projects appear credited "Shared by <submitter>" | 2026-08-30 |
| **Awesome Python Weekly** (LibHunt) | https://python.libhunt.com/contribute | $0, **login required** | "The primary way to contribute is to add a useful library that you use or have used." · "All submitted resources will be considered for inclusion in the weekly newsletter." · "You have to login in order to proceed." · Two submission types: "Package — An open-source library" and "Resource — Blog Post, News, Event, Video, Book" | Weekly | 2026-08-30 |
| **Console.dev** | No public form. Contact is `mailto:hello@console.dev` from https://console.dev/ ; criteria at https://console.dev/selection-criteria | $0 for editorial (https://console.dev/advertise is the paid path — skipped) | "Each week we feature and review 2-3 interesting developer tools" · gates that matter to us: "Is there a self-service signup? A demo or speaking to sales may be an option, but an individual developer should be able to try it themselves without speaking to anyone." · "Is it being actively maintained with regular bug fixes and updates?" · "Does it have good documentation?" · Betas list requires "the release must be pre 1.0 and/or have an appropriate label in the version number e.g. 1.0.0-beta" | Weekly; editorial discretion | 2026-08-30 |
| **SRE Weekly** | Reply to the newsletter email, or the address given on https://sreweekly.com/about/ | $0 (https://sreweekly.com/sponsorship-information/ is paid — skipped) | "I'd love to hear from you if you've seen any articles that I might have missed. Feel free to reply to the email newsletter directly, or email me directly at my first name at this domain. Note that I do not accept embargoed/pre-release content. I prefer to learn about things at the same time that my subscribers do" | Weekly; **no embargo — publish first, then send** | 2026-08-30 |
| **Hacker Newsletter** | None. Auto-curated from HN. https://hackernewsletter.com/ | $0 | "Since 2010, we've hand-curated the best articles from Hacker News into one weekly email." | Mechanism = do well on HN; no separate action | 2026-08-30 |
| **DevOps'ish** | No submission form found; page footers carry "Suggest Changes" (site edits, not submissions). https://devopsish.com/about/ | $0 | "A weekly newsletter assembled by open source leader, DevOps veteran, and Kubernetes Contributor" — one-editor newsletter, "Cloud Native, DevOps, Open Source, AI, tech industry news, culture" | Weekly | 2026-08-30 |
| **Import AI** | The author's own email address, published in the second person on https://importai.substack.com/about ("You can email me at: …" — address withheld here per §2) | $0 | No submission process stated; it is one author's essay newsletter. Treat as a *long-shot single email*, not a channel. | Weekly | 2026-08-30 |
| **TLDR / TLDR AI** | Only https://tldr.tech/advertise found on https://tldr.tech/ ; no free submission mechanism on the site | **Paid (advertise) → SKIP** | Editorial items are summarized by TLDR's own staff from what is already circulating | n/a | 2026-08-30 |
| **Python Weekly** | https://www.pythonweekly.com/ (beehiiv). No submit link in the page's link set; archive-only nav (`/archive`, `/subscribe`, `/authors`) | $0 if a submission path exists — **UNVERIFIED** | Latest issue #760, 2026-08-27, so the newsletter is live and weekly | Weekly | 2026-08-30 |
| **Software Lead Weekly** | https://softwareleadweekly.com/about — no submission form; author curates ("I'm reading 50+ articles every week anyway, so why not pick the very best and send it to my peers?") | $0 | Audience is engineering leadership — the right readers for the study, wrong for a package | Weekly | 2026-08-30 |
| **Programming Digest** | https://programmingdigest.net/ — links are `/newsletters`, `/privacy`, and the publisher https://bonobopress.com/media-kit (paid) | media-kit = **paid**; no free form found | — | — | 2026-08-30 |
| **Data Engineering Weekly**, **Last Week in AI**, **Latent Space**, **AI Engineer newsletter**, **The Batch**, **ByteByteGo** | No submission form found on the fetched pages (dataengineeringweekly.com, lastweekin.ai, latent.space/about, bytebytego.com all 200 but carry no submit/suggest text) | $0 where a reply address exists | **UNVERIFIED** — treat all six as "reply to the author's email after publication", not as submission channels | — | 2026-08-30 |
| **Platform Engineering newsletter** (platformengineering.org) | Site nav has `/join-community`, `/vendor-opportunities`, `/blog` — no editorial submission form. https://platformengineering.org/ | `/vendor-opportunities` reads as paid → SKIP | The free path is the community (Slack) + writing for the blog; **UNVERIFIED** whether the blog takes outside posts | — | 2026-08-30 |
| **MCP-focused newsletters** | The one found with a real mechanism is **PulseMCP** (below, in §4) — its newsletter is fed by its directory. No standalone MCP newsletter with a public submission form was found today. | — | — | — | 2026-08-30 |

---

## 2. CFPs — windows and dates

| Venue | Dates | CFP status today | Cost to speak | Verified |
|---|---|---|---|---|
| **AI Engineer New York 2026** | **2026-10-12 → 10-14**, New York ("AI Engineer New York 2026: Where AI Engineering Meets Wall Street") | Site nav has a "Speak" section; CFP open/closed state **UNVERIFIED** (page is JS-driven). Tickets are paid; speaking is the $0 path | $0 if selected | 2026-08-30 (https://www.ai.engineer/nyc) |
| **AI Engineer Code (SF)** | **2026-11-10 → 11-12**, San Francisco — "By application only." | Application-gated | — | 2026-08-30 (https://www.ai.engineer/) |
| **AI Engineer Europe (London)** | "FEB TBA · LONDON, UK … Dates, venue, speakers, schedule, and tickets will be announced as plans are finalized." | Not open | — | 2026-08-30 |
| **AI Engineer World's Fair 2027** | **2027-06-29 → 07-02**, Moscone West, SF — "targeting over 7,000 AI Engineers, founders, and VPs of AI" | Not open; site offers "Get free talk & workshop videos, CFPs, and early bird discounts" via email list | — | 2026-08-30 |
| **All Things Open 2026** | **2026-10-19 → 10-20**, downtown Raleigh NC | **CLOSED**: "The 2026 call-for-papers (CFP) was open Tuesday, February 17 through Tuesday, March 31." | $0 to submit | 2026-08-30 (https://allthingsopen.org/speak-at-an-ato-event/) |
| **All Things Open — "We ❤️ Open Source"** (article channel, not a CFP) | rolling | **OPEN**: https://allthingsopen.org/contribute-inquiry/ — form fields: "Article topic/Working title", "Briefly outline the key points of your blog post or provide a one paragraph summary" | $0 | 2026-08-30 |
| **FOSDEM 2027** | **2027-01-30 → 01-31**, Brussels | Landing page is a stub (date + address + `info@fosdem.org` only); devroom CFPs are not yet posted. Historically devroom CFPs land Oct–Nov — **watch https://fosdem.org/2027/news/ weekly from 2026-10-01** | $0 | 2026-08-30 (https://fosdem.org/2027/) |
| **PyCon US** | us.pycon.org/**2027**/ returns **404**; the live site is us.pycon.org/2026/ (Long Beach), whose nav carries "Proposal Guidelines / Proposing a Talk / Proposing a Tutorial / Proposing a Poster" | 2027 CFP not open | $0 to submit | 2026-08-30 |
| **PyData Boston-Cambridge** | Meetup group live (3,429 members) but **no upcoming event listed**; most recent events 2026-08-05 and 2026-07-09 | Talk pitches go to the organizers via the Meetup group's Discussions/contact | $0 | 2026-08-30 (https://www.meetup.com/pydata-boston-cambridge/) |
| **Boston Python** | 10,183 members. Upcoming: recurring "Python Over Coffee" Sundays 12:30 pm (Arlington) + **every other Monday, 12:00 pm ET online office hour** ("Every other Monday online at noon Eastern time." — group description; next instances 2026-09-14 and 2026-09-28). **No talk night among the 31 upcoming events the /events/ listing renders** (2026-08-30 → 2027-01-17: 21 × "Python Over Coffee", 9 × "Monday office hour", 1 × "Boston Python + PyLadies + PyData Rooftop Social!" on 2026-09-15 6:00 pm). The response carries `"hasNextPage":true`, so the listing is not exhaustive — the negative claim covers the 31 enumerated events only, not the 40 the group page counts. | Talk pitch via the group's organizers | $0 | 2026-08-30 (https://www.meetup.com/bostonpython/events/ — curl, titles+dateTimes extracted; see instrument log) |
| **Hacktoberfest 2026** | October 2026, "300+ events, In person and online" | **The 2026 program changed shape**: "Under the stewardship of long-time partners Major League Hacking (MLH) and DEV, Hacktoberfest refocuses on high-value, meaningful learning." The site's calls to action are "Apply to Host" and "Host a Fest in your city" — the old four-PRs-for-a-shirt framing is described in past tense ("2015–2025 … maintainers started to face a massive flood of activity and burnout from the rise of low-effort PRs"). **Maintainer opt-in rules for repos: UNVERIFIED** (no maintainer page found at hacktoberfest.com/participation/ — 404 today) | $0 | 2026-08-30 (https://hacktoberfest.com/) |
| **MLOps Community**, **KubeCon NA 2026 co-located AI events**, **Open Source Summit**, **PyData NYC/Global** | Not verified today (mlops.community/code-of-conduct/ 404s; the others were not reached inside the time-box) | **UNVERIFIED** | — | 2026-08-30 |

---

## 3. Discords / Slacks — the self-promo rule, quoted

| Community | Public rule source | Rule verbatim | Verdict |
|---|---|---|---|
| **MCP Contributor Discord** | https://modelcontextprotocol.io/community/communication | Under "Avoid": "MCP user support - Read official documentation and use GitHub Discussions for questions" and "**Service or product marketing - Keep discussions vendor-neutral; mentions of brands are discouraged except as examples relevant to the specification**". Also: "The server is designed for MCP contributors and is not intended for general MCP support." | **Not a launch venue.** The legitimate use is contributing to `#*-sdk-dev` / WG channels and letting the work speak. |
| **Python Discord** | https://www.pythondiscord.com/pages/rules/ | "We have a small but strict set of rules on our server." Rule 6: "**Do not post unapproved advertising.**" Rule 7: "Keep discussions relevant to the channel topic. Each channel's description tells you the topic." Rule 9: "Do not offer or ask for paid work of any kind." Rule 10: "Do not copy and paste answers from ChatGPT or similar AI tools." Escalation: "A public verbal or textual warning … A permanent ban from the server." | A showcase post needs staff approval first (ModMail). The #showcase channel's own rules are inside Discord → **needs-auth, UNVERIFIED**. |
| **DataTalks.Club Slack** | https://datatalks.club/slack.html | Join is an email form: "To join our Slack community, write your email and click on the 'Join' button." · "When participating in discussions, please follow our community guidelines." Channel list is published: `#book-of-the-week`, `#career-questions`, `#datascience`, `#engineering` ("for discussing the engineering aspects of data science: data engineering, ML engineering, MLOps, and so on"), `#events`, `#jobs`, `#memes`, `#random`. **No showcase channel exists** — there is no on-topic place to post a package. | Low value for launches; `#engineering` is a fit for the *study*. |
| **Anthropic Developer Discord, Cursor, Continue.dev, LangChain, CrewAI, Latent Space Discord, MLOps Community Slack** | Rules live inside the server | **needs-auth → UNVERIFIED.** Joining requires an account (RED per §2). | ASK the principal to read and paste the #self-promo / #showcase rule text for each before any post. |

---

## 4. Launch venues and their norms

### 4.1 Show HN — the one that matters
Source: https://news.ycombinator.com/showhn.html (fetched 2026-08-30; `news.ycombinator.com/robots.txt` sets `Crawl-delay: 30`, honored).

> "Show HN is for something you've made that other people can play with."
> "On topic: things people can run on their computers or hold in their hands."
> "**Off topic: blog posts, sign-up pages, newsletters, lists, and other reading material. Those can't be tried out, so can't be Show HNs. Make a regular submission instead.**"
> "The project should be non-trivial. **Don't post quickly-generated one-offs; anybody can do that now.** Share something that is deeply personal and interesting to you. Explain how and why."
> "The project must be something you've worked on personally and which you're around to discuss."
> "Please make it easy for users to try your thing out, ideally without barriers such as signups or emails. You'll get more feedback that way."
> "If your work isn't ready for users to try out, please don't do a Show HN."
> "To post, submit a story whose title begins with 'Show HN'."
> "New features and upgrades ('Foo 1.3.1 is out') generally aren't substantive enough to be Show HNs. A major overhaul is probably ok."
> "**Please don't ask friends to upvote or comment. That's not ok on HN.**"

Operational consequences for us: (a) `pip install X && X --demo` must work with no signup; (b) the study is a **regular** submission, not a Show HN; (c) one Show HN per package, not per release; (d) the principal must be free to answer comments for ~4 hours.

### 4.2 Reddit — UNVERIFIED by construction
r/Python, r/MachineLearning ([P]/[R] tags), r/LocalLLaMA, r/ClaudeAI, r/mcp, r/programming are all plausibly the right rooms, but `reddit.com/robots.txt` is `Disallow: /` for `*`, so **no rule text was fetched and none is quoted here**. Before any post, the principal (a human in a browser, not this agent) must read each subreddit's sidebar rules and wiki. Do not treat any remembered rule ("r/Python allows Showcase Saturday", "r/MachineLearning requires the [P] tag") as verified — it is not.

### 4.3 MCP distribution graph — publish once, appear in many

| Venue | Mechanism | Cost | Norms / requirements | Verified |
|---|---|---|---|---|
| **Official MCP Registry** | `mcp-publisher init` → `mcp-publisher login github` → `mcp-publisher publish` (CLI installed from GitHub releases or `brew install mcp-publisher`) | $0 | For a **PyPI** package: "The MCP Registry verifies ownership of PyPI packages by checking for the existence of an `mcp-name: $SERVER_NAME` string in the package README (which becomes the package description on PyPI). The string may be hidden in a comment, but the `$SERVER_NAME` portion **MUST** match the server name from `server.json`." Server name form: `io.github.username/database-query-mcp`. Registry is "currently in preview. Breaking changes or data resets may occur before general availability." Moderation: "**TL;DR**: The MCP Registry is quite permissive! We only remove illegal content, malware, spam, and completely broken servers" — spam includes "A server that doesn't do anything but provide a fixed response with some marketing copy". | 2026-08-30 (raw.githubusercontent.com/modelcontextprotocol/registry/main/docs/modelcontextprotocol-io/{quickstart,package-types,moderation-policy}.mdx) |
| **PulseMCP** | https://www.pulsemcp.com/submit | $0 | "**Apologies, submissions and changes are temporarily paused**" · "Until mid-August, we are not accepting new MCP server or client submissions, and we are not making changes to existing listings." · "In the meantime, if you have a server to share, publish it to the Official MCP Registry. That is the best first step even when we are not paused, and **we will pick it up automatically once we are back**." | 2026-08-30 |
| **Glama** | https://glama.ai/mcp/servers — "Add Server" button; servers are auto-indexed from GitHub and can then be "Claimed" | $0 | Scale: "80,479 servers" (page timestamp changes by the minute; it read `Updated 2026-08-31 01:08` at verification time and is not quoted here); only 3,292 carry the "Claimed" facet — 3,292 / 80,479 = **4.1%**, so claiming is a cheap differentiator | 2026-08-30 |
| **mcp.so** | https://mcp.so/submit — form takes "Repository URL *", "Name"; the only submit control rendered pre-auth is the paid one | Free lane **UNVERIFIED** — re-fetched 2026-08-30 (`curl -sSL https://mcp.so/submit` → 307 → `?type=server`, HTTP 200): the only submit control rendered pre-auth is "Pay and submit automatically"; a free lane may exist behind sign-in but is not visible on the public submit page, so no $0 path is claimed here. Fast lane is **paid**: "Paid submission $39 one-time publishing fee — Publish immediately without review / Verified badge / Featured and priority placement / Dofollow project link" | Skip the $39. Their own traffic claim: "Unique visitors (12 mo) 2.2M". | 2026-08-30 |
| **Smithery** | https://smithery.ai/new → "Sign in — Continue to your workspace … Continue with GitHub" | $0 but **account required → ASK** | Rules not visible pre-auth | 2026-08-30 |
| **punkpeye/awesome-mcp-servers** | PR against README.md | $0 | "Contributions are welcome and encouraged!" · "**If you are an automated agent, we have a streamlined process for merging agent PRs. Just add `🤖🤖🤖` to the end of the PR title to opt-in. Merging your PR will be fast-tracked.**" · "Alphabetical order: Maintain alphabetical order within each category" · "One server per line" | 2026-08-30 (raw CONTRIBUTING.md) |
| **wong2/awesome-mcp-servers** | **Does not take PRs**: "> [!NOTE] We do not accept PRs. Please submit your MCP on the website: https://mcpservers.org/submit" | $0 | Submit via mcpservers.org/submit | 2026-08-30 (`gh api repos/wong2/awesome-mcp-servers/contents/README.md`) |
| **Cursor directory** | https://cursor.directory/ returned **HTTP 429** (rate-limited) today | — | **UNVERIFIED** — retry off-peak | 2026-08-30 |

### 4.4 Claude Code plugin marketplace
`anthropics/claude-plugins-community` (2,883 stars), README fetched via `gh api` 2026-08-30:
> "A **read-only mirror** of the community plugin marketplace… It is synced nightly from Anthropic's internal review pipeline."
> "Every plugin listed here has been submitted via [claude.ai](https://clau.de/plugin-directory-submission), passed automated security scanning, and been approved for distribution."
> "Submit via **clau.de/plugin-directory-submission**. **Pull requests opened directly against this repo are closed automatically** — all changes flow from the internal review pipeline."
Install path for readers: `claude plugin marketplace add anthropics/claude-plugins-community` then `claude plugin install <name>@claude-community`.
Cost $0; submission needs a Claude account → **ASK**; lead time = nightly sync *after* review, so assume ≥1 week.

### 4.5 Passive discovery: PyPI and GitHub
- PyPI classifiers list (the authoritative set) is at https://pypi.org/classifiers/ (fetched 2026-08-30; note `robots.txt` disallows `/pypi/*/json`, so the JSON API was not used). Classifiers are declared in package metadata; keywords are free text. There is no "submit" step — the taxonomy *is* the channel.
- GitHub topics, measured today with `gh api -X GET search/repositories -f q="topic:<t>"`: `topic:mcp` → **67,930** repos, `topic:claude-code` → **65,988**, `topic:ai-agents` → **81,569**, `topic:mcp-server` → **26,261**, `topic:llm` → **123,173**. `mcp-server` is the only one small enough that a new repo is findable in a "recently updated" sort; the others are noise. Cost $0, lead time zero, effect small but compounding.

### 4.6 Account-gated venues (all $0, all **ASK** — the agent may not create accounts)
Product Hunt (https://www.producthunt.com — `robots.txt` allows crawling but posting needs an account), dev.to, Hashnode, HackerNoon. Lobsters is **invite-only and robots-excluded** → skip.

---

## 5. Where the Track M study goes

| Venue | Mechanism | Cost | Constraint that matters | Verified |
|---|---|---|---|---|
| **arXiv cs.SE** | https://info.arxiv.org/help/endorsement.html | $0 | "**arXiv requires that users be endorsed before submitting their first paper to arXiv or a new category.**" · "Your account may receive endorsement if: you have claimed ownership of a paper submitted by a co-author **and** your email address meets the institutional email criteria" · "Alternatively you can seek personal endorsement from an established arXiv author… A good choice for graduate students would be your thesis advisor or another professor in your department/institution working in your field who is also an active author on arXiv." · Warning: "it is inappropriate to email large numbers of potential endorsers at once". **A .edu address alone does not clear the gate for a first-time author with no claimed paper.** This is an ASK with a date: request endorsement by **2026-09-19** for a 2026-10-10 publication. | 2026-08-30 |
| **Hacker News (regular submission)** | https://news.ycombinator.com/submit | $0 | Not a Show HN (see §4.1). Title = the finding, not the framing. | 2026-08-30 |
| **Hugging Face Papers** | https://huggingface.co/papers/trending | $0, account needed → ASK | **Papers with Code is dead**: `curl -I https://paperswithcode.com/` → `HTTP/2 302` → `location: https://huggingface.co/papers/trending` (2026-08-30). HF Papers indexes by arXiv ID, so it is downstream of the endorsement gate. | 2026-08-30 |
| **Semantic Scholar / Google Scholar** | Automatic, from arXiv | $0 | No submission step; also downstream of arXiv | not separately fetched — **UNVERIFIED** |
| **r/MachineLearning ([P]/[R])**, **r/LocalLLaMA**, **SWE-bench community/Discord** | — | $0 | **UNVERIFIED** (Reddit robots-excluded; SWE-bench Discord needs-auth) | 2026-08-30 |
| **Changelog News** | §1 | $0 | A methods-and-dataset study is exactly what their rules allow (not a tutorial, not a commercial product) | 2026-08-30 |
| **SRE Weekly / Data Engineering Weekly / Software Lead Weekly** | reply-to-email | $0 | SRE Weekly: "I do not accept embargoed/pre-release content" — send *after* publication | 2026-08-30 |
| **Bluesky, LinkedIn, X** | principal's own accounts | $0 | Noted only; the agent posts nothing. | — |

---

## 6. Boston in-person, Sep–Oct 2026 (Track H, opted in)

| Date | Event | Where | Cost | Source · verified 2026-08-30 |
|---|---|---|---|---|
| **Thu 2026-09-03, 4:30 pm** | Venture Café Cambridge — "Uncertainty Principle: AI, Quantum, and the Tools Reshaping Work" | Cambridge (CIC, 1 Broadway) | free, RSVP via GatherUs | venturecafecambridge.org/events (WebFetch — see instrument log) |
| Thu 2026-09-10, 4:30 pm | Venture Café — "University of Tsukuba Night 2026" | same | free | same |
| **Thu 2026-09-17, 4:30 pm** | Venture Café — "**New Frontiers: Space, Health & Global Innovation**" | same | free | same |
| Thu 2026-09-24, 4:30 pm | Venture Café — "Thursday Gathering - September 24, 2026" | same | free | same |
| **Thu 2026-10-01, 4:30 pm** | Venture Café — "**Boston AI Week @ Venture Café!**" | same | free | same |
| Thu 2026-10-29, 4:30 pm | Venture Café — "Chile Innovation Night at Tough Tech Week" | same | free | same |
| **2026-09-16 → 2026-10-28** | **Boston AI Week 2026** — "September 16 – October 28, 2026 · Six weeks across Massachusetts"; "**Core Festival Week: September 24 – October 2**"; "125+ events already approved"; "Mayor Michelle Wu has proclaimed September 24, 2026, to be Boston AI Week in the City of Boston." Site has a **"Host an Event"** path — a $0 way to run a session rather than attend one. | statewide | most events free; per-event | https://aiweek.boston/ and /schedule |
| Thu 2026-09-03 | AI Tinkerers Boston — next event listed as "Back from Summer: AI GTM Builders" | Boston | free/RSVP | https://boston.aitinkerers.org/ (WebSearch snippet corroborated the title; page is JS-heavy) — **partially UNVERIFIED** |
| — | **AI Native Dev Boston (Snyk, 100 Summer St)** — queue.md's Thu 2026-09-17 entry **did not re-verify**: https://www.meetup.com/ai-native-dev-boston/ returns "Group not found. Sorry, the group you're looking for doesn't exist." and a WebSearch for the event found nothing. | — | — | **UNVERIFIED — find the correct Meetup/Luma slug before the principal blocks the evening.** |
| Sundays 12:30 pm (09-06, 09-13, …) | Boston Python — "Python Over Coffee", Caffè Nero, 321 Broadway, Arlington MA | Arlington | free | https://www.meetup.com/bostonpython/ |
| Every other Monday, 12:00 pm ET (next: 2026-09-14, 2026-09-28) | Boston Python — online office hour ("Unstructured Zoom office hour!"); group description reads "Every other Monday online at noon Eastern time." — fortnightly, not weekly | online | free | https://www.meetup.com/bostonpython/events/ |
| Tue 2026-09-15, 6:00 pm | Boston Python + PyLadies + PyData Boston — "Boston Python + PyLadies + PyData  Rooftop Social!" — the only non-recurring Boston Python event in the enumerated upcoming set | Boston area (venue not read) | free | https://www.meetup.com/bostonpython/events/ |
| — | PyData Boston-Cambridge — **no upcoming event**; last listed 2026-08-05 (Kendall Square Roof Garden) and 2026-07-09 (MIT Building E51) | — | free | https://www.meetup.com/pydata-boston-cambridge/ |
| — | MIT/Harvard/Northeastern public talks; HubSpot/Datadog Boston community events | — | — | **not reached inside the time-box — UNVERIFIED** |

Note on `bostonaiweek.com`: it is a stub ("Launching Soon", "Copyright © 2024"). The live 2026 site is **aiweek.boston**. Fix this in `outreach/queue.md`.

---

## 7. RANK

### (a) Top 10 for package launches
| # | Channel | One-line reason | The norms constraint that matters most |
|---|---|---|---|
| 1 | **Show HN** | Best-ranked venue for turning a runnable package into strangers filing issues — the Track I gate's unit. Conversion is **UNVERIFIED** (nothing here measures it); the ranking rests on the venue's own rules matching what we ship | "Please make it easy for users to try your thing out, ideally without barriers such as signups or emails" — and never Show HN a docs page |
| 2 | **Official MCP Registry** (for any package exposing an MCP server) | One `mcp-publisher publish` puts the package into the graph that PulseMCP and Glama re-index for free | The `mcp-name: io.github.<user>/<name>` token must be in the README *before* the PyPI release, or ownership verification fails |
| 3 | **PyPI + GitHub topics** (`mcp-server`, `claude-code`) | Zero lead time, permanent, compounds with every release | `topic:mcp` (67,930) and `topic:llm` (123,173) are noise; `mcp-server` (26,261) is the only findable one |
| 4 | **PyCoder's Weekly** | An explicit, free, self-submission form aimed at "projects you are working on" — the cleanest fit of any newsletter | Python-only; one link per issue; no guarantee of inclusion |
| 5 | **Changelog News** | Free submission, large platform-engineering audience, and self-submission is explicitly welcomed | "🚫 Commercial products/services. Sponsorship is your path." — pitch the OSS, never a paid tier |
| 6 | **punkpeye/awesome-mcp-servers PR** | A maintainer who has *invited* agent-authored PRs; merged listing is durable | Alphabetical order, one server per line, and `🤖🤖🤖` in the PR title if the PR is agent-written (disclosure, per §2) |
| 7 | **Glama** | Auto-indexes from GitHub with no action; "claiming" the listing is a 5-minute differentiator only 3,292 Claimed / 80,479 total = **4.1%** of servers have done | Account to claim → ASK |
| 8 | **Console.dev** | Editorial devtools newsletter whose published criteria we can actually satisfy | "Is there a self-service signup?" — a package with a broken quickstart fails on the first criterion; no form, so a single well-aimed email |
| 9 | **Claude Code plugin marketplace** | The distribution surface for the exact reader we want (teams already running coding agents) | PRs to the mirror repo "are closed automatically"; only clau.de/plugin-directory-submission works, and it needs an account → ASK |
| 10 | **Awesome Python Weekly / LibHunt** | Second Python newsletter with a real submission form, different editor from PyCoder's | Login required; submit as "Package — An open-source library" |

*(Deliberately not in the top 10: mcp.so — no free lane is visible pre-auth (**UNVERIFIED**, §4.3) and the fast lane costs $39; PulseMCP — submissions paused; every Discord — all of them ban unapproved promotion; Reddit — rules unverifiable under robots.)*

### (b) Top 10 for the Track M study
| # | Channel | One-line reason | The norms constraint that matters most |
|---|---|---|---|
| 1 | **HN regular submission** | Highest-variance, zero-cost route to the exact readers, and the study is the kind of primary measurement HN rewards | It is **not** a Show HN; and "Please don't ask friends to upvote" applies to the study too |
| 2 | **arXiv cs.SE** | Makes the result citable and feeds HF Papers, Semantic Scholar and Google Scholar for free | The endorsement gate — a first-time author with an institutional email but no claimed paper still needs a personal endorser; start by **2026-09-19** |
| 3 | **The dataset + instrument repo on GitHub** | The artifact people actually reuse; every reuse is a potential inbound issue | Doc-truth: the README's numbers must be reproducible by the shipped script |
| 4 | **Changelog News** | A methods/dataset study is squarely inside their "newsworthy, non-commercial" rule | "Do your best to convince us why something is newsworthy" — the pitch is the number, not the project |
| 5 | **Hugging Face Papers** | The live successor to Papers with Code (which now 302s there) | Needs an arXiv ID → downstream of #2; account → ASK |
| 6 | **r/MachineLearning [P]/[R]** | Where this genre of measurement gets read and argued | Rules **UNVERIFIED** (robots) — the principal must read the sidebar before posting |
| 7 | **Software Lead Weekly** | Its readers (engineering leaders) are the buyers for everything downstream of the study | No form; a single email to the curator, after publication |
| 8 | **SRE Weekly / Data Engineering Weekly** | Free, reply-to-email, adjacent audiences who care about non-discriminating tests | "I do not accept embargoed/pre-release content" — send only after it is public |
| 9 | **A Boston AI Week talk or PyData Boston talk** | Converts the study into a room of local leads during the 09-16 → 10-28 window; "Host an Event" is $0 | PyData Boston currently has **no scheduled events** — the pitch goes to the organizers, with lead time measured in weeks |
| 10 | **Principal's Bluesky / LinkedIn / X** | The only channels where the principal's own network can amplify without any gatekeeper | The agent drafts; the principal posts (§2 RED) |

### Sequencing against the Track I gate (≥5 unsolicited contacts by 2026-10-31, 62 days from today)
- **By 2026-09-06:** PyPI release #1 with `mcp-name` token, GitHub topics set, registry publish. (Zero-gatekeeper actions.)
- **By 2026-09-13:** Show HN for package #1; same week, PyCoder's + Changelog submissions; awesome-mcp-servers PR.
- **By 2026-09-19:** arXiv endorsement request out (blocking dependency for 2026-10-10).
- **2026-09-24 → 10-02:** Boston AI Week core week + Venture Café 10-01; in-person is the only channel here with a same-day reply loop.
- **By 2026-10-12:** study published → HN regular submission, newsletters, HF Papers.
- Every one of these must carry the same reply address (repo Issues + the principal's public email) or an inbound contact cannot be counted.

---

## Instrument log

**Venues/APIs tried today (2026-08-30; server dates on some responses read 2026-08-31 UTC).**

| Venue / API | Result |
|---|---|
| news.ycombinator.com/showhn.html | reachable (robots: `Crawl-delay: 30`, honored) |
| www.reddit.com, old.reddit.com | **blocked by robots** (`User-agent: *` / `Disallow: /`) — not crawled; all Reddit rules UNVERIFIED |
| lobste.rs | **blocked by robots** (`Disallow: /`) + invite-only — not crawled |
| pypi.org/classifiers/ | reachable (`/pypi/*/json` disallowed → JSON API not used) |
| github.com / raw.githubusercontent.com / `gh api` (read-only GETs) | reachable |
| registry.modelcontextprotocol.io/robots.txt | 404 (docs read from the registry repo instead) |
| modelcontextprotocol.io | reachable |
| console.dev | reachable (`/about/`, `/contact`, `/selection-criteria/` 404; `/selection-criteria` 200) |
| changelog.com/news/submit | reachable |
| pycoders.com (`/suggest` 404 → `/submissions` 200) | reachable |
| pythonweekly.com, softwareleadweekly.com, sreweekly.com, devopsish.com, hackernewsletter.com, programmingdigest.net, tldr.tech, dataengineeringweekly.com, lastweekin.ai, latent.space, bytebytego.com, importai.substack.com, platformengineering.org | reachable |
| python.libhunt.com | reachable |
| www.pythondiscord.com | reachable |
| datatalks.club | reachable |
| mlops.community/code-of-conduct/ | 404 |
| ai.engineer, allthingsopen.org, fosdem.org/2027, hacktoberfest.com, us.pycon.org/2026 | reachable |
| us.pycon.org/2027 | 404 |
| hacktoberfest.com/participation/ | 404 |
| www.meetup.com (bostonpython, pydata-boston-cambridge) | reachable |
| www.meetup.com/bostonpython/events/ (fix pass, 2026-08-30) | reachable — `robots.txt` disallows only the `*/events/{atom,rss,xml}/*` feed variants, not the HTML listing; fetched with `curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)"` → HTTP 200, 218,760 bytes; 31 distinct upcoming events extracted from the embedded `"title"`/`"dateTime"` pairs; response also carries `"hasNextPage":true` |
| www.meetup.com/ai-native-dev-boston | 200 but "Group not found" |
| venturecafecambridge.org | **403 to curl** (robots.txt itself 403) → read via WebFetch |
| aiweek.boston, bostonaiweek.com, boston.aitinkerers.org, aitinkerers.org | reachable |
| info.arxiv.org | reachable (arxiv.org robots `Crawl-delay: 15`, honored) |
| paperswithcode.com | 302 → huggingface.co/papers/trending |
| pulsemcp.com/submit, mcp.so/submit, glama.ai/mcp/servers | reachable |
| smithery.ai/new | reachable but **needs-auth** (sign-in wall) |
| cursor.directory | **429 rate-limited** |
| discord.com (server rules for MCP/Anthropic/Cursor/LangChain/CrewAI/Latent Space) | **needs-auth** — not entered (account creation is RED) |
| WebSearch | 1 call used |
| WebFetch | 1 call used |

**Citations by host** — recount, fix pass 2026-08-30. Rule (reproducible): every `https?://…` in the body above this log, deduplicated by full URL, bucketed by host, excluding the user-agent string `github.com/Alex-lop/venture`. This is a **wider** rule than the author's original table, which mis-allocated three hosts (`fosdem.org`, `tldr.tech`) and omitted three (`bonobopress.com`, `clau.de`, `mcpservers.org`).

| Host | Citations |
|---|---|
| meetup.com | 4 |
| console.dev | 3 |
| ai.engineer | 2 |
| allthingsopen.org | 2 |
| fosdem.org | 2 |
| news.ycombinator.com | 2 |
| pypi.org | 2 |
| sreweekly.com | 2 |
| tldr.tech | 2 |
| aiweek.boston · bonobopress.com · boston.aitinkerers.org · changelog.com · clau.de · cursor.directory · datatalks.club · devopsish.com · glama.ai · hackernewsletter.com · hacktoberfest.com · huggingface.co · importai.substack.com · info.arxiv.org · lobste.rs · mcp.so · mcpservers.org · modelcontextprotocol.io · old.reddit.com · paperswithcode.com · platformengineering.org · producthunt.com · programmingdigest.net · pulsemcp.com · pycoders.com · python.libhunt.com · pythondiscord.com · pythonweekly.com · reddit.com · smithery.ai · softwareleadweekly.com | 1 each (31) |
| **Subtotal, URL-form citations** | **52** |
| GitHub-sourced citations that appear as bare `raw.githubusercontent.com` paths or `gh api` commands rather than full URLs: three registry `.mdx` docs, punkpeye `CONTRIBUTING.md`, `gh api repos/wong2/…/README.md`, `gh api repos/anthropics/claude-plugins-community`, `gh api -X GET search/repositories` (the five §4.5 topic counts) | 7 |

**HN + GitHub share: 9 / 52 = 17.3%** (news.ycombinator.com ×2 + GitHub-sourced ×7; the verifier's recount, adopted — it corrects the author's original "8 / 52 = 15.4%", which omitted the `search/repositories` topic-count query). Under the wider rule of the table above (52 URL-form + 7 non-URL-form = 59 citations) the share is 9 / 59 = 15.3%. Both are far below the 70% threshold, so this file remains **not instrument-biased** and no conclusion is downgraded on that ground. The binding limitation is different and is stated plainly: **Reddit and every Discord are unverifiable by this agent** (robots exclusion and account walls), so four of the venues the brief asked about carry no quoted rules at all. Two further claims are held **UNVERIFIED** after the fix pass and their dependent conclusions are held one level lower: the mcp.so free lane (§4.3 — no free submit control is visible pre-auth, so mcp.so is not counted as a $0 channel anywhere in §7) and the per-channel inbound conversion rate that summary #1 used to rest on (now stated as a ranked hypothesis with the §9 gate as its falsifier).

---

## Verification (2026-08-30, quote-verifier)

Adversarial re-fetch of every citation, number and quoted string in the body above. Method: `curl -sS -A "venture-research/2 (+https://github.com/Alex-lop/venture)"` for every host except venturecafecambridge.org (403 to curl, robots.txt itself 403 → WebFetch, same as the author); `gh api` GETs re-run verbatim. 85 claims checked: **76 VERIFIED, 5 MISMATCH, 0 UNREACHABLE, 4 UNCHECKED.** No sampling was needed — coverage is the whole file, not a subset.

### Claim table

| # | Claim / quote (location) | Verdict |
|---|---|---|
| 1 | reddit.com + old.reddit.com robots.txt end `User-agent: *` / `Disallow: /` (§0) | VERIFIED |
| 2 | lobste.rs robots.txt `User-agent: *` / `Crawl-delay: 1` / `Disallow: /` (§0) | VERIFIED |
| 3 | pypi.org robots.txt disallows `/pypi/*/json` (§0, §4.5) | VERIFIED |
| 4 | news.ycombinator.com robots.txt `Crawl-delay: 30` (§4.1) | VERIFIED |
| 5 | "Show HN is for something you've made that other people can play with." | VERIFIED |
| 6 | "On topic: things people can run on their computers or hold in their hands." | VERIFIED |
| 7 | "Off topic: blog posts, sign-up pages, newsletters, lists, and other reading material…" | VERIFIED |
| 8 | "The project should be non-trivial. Don't post quickly-generated one-offs; anybody can do that now…" | VERIFIED |
| 9 | "The project must be something you've worked on personally and which you're around to discuss." | VERIFIED |
| 10 | "Please make it easy for users to try your thing out, ideally without barriers such as signups or emails…" | VERIFIED |
| 11 | "If your work isn't ready for users to try out, please don't do a Show HN." | VERIFIED |
| 12 | "To post, submit a story whose title begins with 'Show HN'." | VERIFIED |
| 13 | "New features and upgrades ('Foo 1.3.1 is out') generally aren't substantive enough… A major overhaul is probably ok." | VERIFIED |
| 14 | "Please don't ask friends to upvote or comment. That's not ok on HN." | VERIFIED |
| 15 | changelog.com/news/submit reachable; submission needs a free account ("Please sign in / up to submit news.") | VERIFIED |
| 16 | "Submitting other people's work is encouraged. Submitting your own work is also encouraged." | VERIFIED |
| 17 | "🚫 Commercial products/services. Sponsorship is your path." (§1, summary #4, §7a #5) | VERIFIED |
| 18 | "🚫 How-to's and tutorials." · "🚫 Reader-hostile websites." | VERIFIED |
| 19 | "The golden rule: … Do your best to convince us why something is newsworthy. You'll be notified via email if and when your submission gets published." | VERIFIED |
| 20 | pycoders.com/submissions exists; button text "Submit Your Link »" | VERIFIED |
| 21 | "At PyCoder's Weekly we believe in showcasing the best work…" · "And while we cannot guarantee to feature every submitted link…" | VERIFIED |
| 22 | PyCoder's "issue #749 dated 2026-08-25" | UNCHECKED — #749 is confirmed as the latest issue on pycoders.com, but no date is printed on the page fetched; the date is not sourced |
| 23 | python.libhunt.com/contribute: "The primary way to contribute…" · "All submitted resources will be considered…" · "You have to login in order to proceed." · Package/Resource types | VERIFIED |
| 24 | console.dev/selection-criteria: "Each week we feature and review 2-3 interesting developer tools" · "Is there a self-service signup?…" · "Is it being actively maintained…" · "Does it have good documentation?" | VERIFIED |
| 25 | console.dev contact is `hello@console.dev`; /advertise is the paid path | VERIFIED (criteria page: "Email hello@console.dev with the details") |
| 26 | Console betas: "the release must be pre 1.0 and/or have an appropriate label in the version number e.g. 1.0.0-beta" | VERIFIED |
| 27 | SRE Weekly: "I'd love to hear from you if you've seen any articles that I might have missed… Note that I do not accept embargoed/pre-release content. I prefer to learn about things at the same time that my subscribers do" | VERIFIED |
| 28 | sreweekly.com/sponsorship-information/ is the paid path | VERIFIED (page text: "I am currently actively seeking sponsors…send over a copy of my media kit.") |
| 29 | **Summary #6: "TLDR/TLDR AI, SRE Weekly's front page and mcp.so's fast lane are paid and are skipped"** | **MISMATCH** — the sponsorship page names no "front page" product, and §1 of this same file correctly lists SRE Weekly's editorial path as $0. The summary contradicts the body |
| 30 | Hacker Newsletter: "Since 2010, we've hand-curated the best articles from Hacker News into one weekly email." | VERIFIED |
| 31 | DevOps'ish: "A weekly newsletter assembled by open source leader, DevOps veteran, and Kubernetes Contributor" · "Cloud Native, DevOps, Open Source, AI, tech industry news, culture" | VERIFIED (and the quote correctly stops before the editor's name — §2 compliant) |
| 32 | Import AI about page publishes the author's address in the second person; address withheld in the file | VERIFIED — page reads "You can email me at: …"; the file withholds it correctly |
| 33 | tldr.tech exposes only /advertise; no free submission mechanism | VERIFIED (nav: Newsletters · Advertise · Blog) |
| 34 | Python Weekly latest issue #760, 2026-08-27 | VERIFIED ("Aug 27, 2026 Python Weekly (Issue 760 August 27 2026)") |
| 35 | Software Lead Weekly: "I'm reading 50+ articles every week anyway, so why not pick the very best and send it to my peers?" | VERIFIED |
| 36 | Programming Digest links `/newsletters`, `/privacy`, publisher bonobopress.com media kit (paid) | VERIFIED (footer: "© 2013-2026 Bonobo Press · Newsletters · Privacy · Advertise") |
| 37 | platformengineering.org nav has Join Community / Vendor opportunities / blog; no editorial submission form | VERIFIED |
| 38 | AI Engineer New York 2026-10-12 → 10-14; "AI Engineer New York 2026: Where AI Engineering Meets Wall Street"; nav has "Speak" | VERIFIED |
| 39 | AI Engineer Code SF 2026-11-10 → 11-12, "By application only." | VERIFIED |
| 40 | "FEB TBA · LONDON, UK … Dates, venue, speakers, schedule, and tickets will be announced as plans are finalized." | VERIFIED |
| 41 | World's Fair 2027-06-29 → 07-02, Moscone West, "targeting over 7,000 AI Engineers, founders, and VPs of AI"; "Get free talk & workshop videos, CFPs, and early bird discounts" | VERIFIED |
| 42 | All Things Open 2026-10-19 → 10-20, downtown Raleigh NC | VERIFIED |
| 43 | "The 2026 call-for-papers (CFP) was open Tuesday, February 17 through Tuesday, March 31." | VERIFIED |
| 44 | allthingsopen.org/contribute-inquiry/ open; fields "Article topic/Working title", "Briefly outline the key points of your blog post or provide a one paragraph summary" | VERIFIED |
| 45 | FOSDEM 2027 landing page is a stub: "30 & 31 January 2027", Brussels, `info@fosdem.org` | VERIFIED |
| 46 | us.pycon.org/2027/ returns 404 | VERIFIED (HTTP 404) |
| 47 | PyData Boston-Cambridge 3,429 members, no upcoming event, last events 2026-08-05 (Kendall Square Roof Garden) and 2026-07-09 (MIT Building E51) | VERIFIED — page shows only "Past events 71"; no upcoming section exists |
| 48 | Boston Python 10,183 members; "Python Over Coffee" Sundays 12:30 pm, Caffè Nero, 321 Broadway, Arlington MA (09-06, 09-13 listed) | VERIFIED |
| 49 | **Boston Python "Mondays 12:00 pm online office hours" (§2 and §6)** | **MISMATCH** — the group's own text reads "Every other Monday online at noon Eastern time"; listed instances are Aug 31 and Sep 14, i.e. fortnightly, not weekly |
| 50 | Boston Python "no upcoming *talk night* listed for Sep 2026" (§2) | UNCHECKED — the page reports "Upcoming events 40" and renders only the first five; a negative claim over 40 events is not supported by the fetched page |
| 51 | Hacktoberfest 2026: "Under the stewardship of long-time partners Major League Hacking (MLH) and DEV…" · "2015–2025 … burnout from the rise of low-effort PRs" · "Apply to Host" / "Host a Fest in your city" · "300+ events In person and online" | VERIFIED |
| 52 | hacktoberfest.com/participation/ 404 | VERIFIED (HTTP 404) |
| 53 | mlops.community/code-of-conduct/ 404 | VERIFIED (301 → 404 at the un-slashed URL) |
| 54 | MCP Contributor Discord: "Service or product marketing - Keep discussions vendor-neutral; mentions of brands are discouraged except as examples relevant to the specification" · "MCP user support - Read official documentation and use GitHub Discussions for questions" · "The server is designed for MCP contributors and is not intended for general MCP support." | VERIFIED |
| 55 | Python Discord rule numbering 6/7/9/10 and text; escalation "A public verbal or textual warning … A permanent ban from the server." | VERIFIED — enumerated the `<ol>`; rules 6, 7, 9, 10 are exactly as quoted |
| 56 | DataTalks.Club: join-by-email quote, guidelines quote, published channel list, `#engineering` description, no showcase channel | VERIFIED |
| 57 | MCP Registry PyPI ownership: "verifies ownership of PyPI packages by checking for the existence of an `mcp-name: $SERVER_NAME` string in the package README… **MUST** match the server name from `server.json`"; name form `io.github.username/database-query-mcp` | VERIFIED (package-types.mdx L80, L87) |
| 58 | "currently in preview. Breaking changes or data resets may occur before general availability." | VERIFIED |
| 59 | "**TL;DR**: The MCP Registry is quite permissive! We only remove illegal content, malware, spam, and completely broken servers" · spam = "A server that doesn't do anything but provide a fixed response with some marketing copy" | VERIFIED (moderation-policy.mdx L10, L34) |
| 60 | PulseMCP: "Apologies, submissions and changes are temporarily paused" · "Until mid-August, we are not accepting new MCP server or client submissions…" · "publish it to the Official MCP Registry… we will pick it up automatically once we are back" | VERIFIED — still paused today |
| 61 | Glama "80,479 servers"; "Claimed 3,292" | VERIFIED — both figures identical today |
| 62 | **Glama quoted as "80,479 servers. Updated 2026-08-31 01:00"** | **MISMATCH (quote)** — page reads "Updated 2026-08-31 **01:08**". The count is right; the quoted string is not verbatim |
| 63 | "only 4% of servers have done" claiming (§7a #7) | VERIFIED as arithmetic (3,292 ÷ 80,479 = 4.09%) but the file shows no arithmetic — §8 requires derived numbers to show it |
| 64 | mcp.so: "Paid submission $39 one-time publishing fee — Publish immediately without review / Verified badge / Featured and priority placement / Dofollow project link"; "Unique visitors (12 mo) 2.2M"; fields "Repository URL *", "Name" | VERIFIED |
| 65 | mcp.so "Free path $0 (**account = ASK**)" | UNCHECKED — the only submit control rendered pre-auth is "Pay and submit automatically"; no free lane is visible on the fetched page, so "$0 path exists" is not evidenced |
| 66 | Smithery: "Sign in — Continue to your workspace … Continue with GitHub" | VERIFIED |
| 67 | cursor.directory returns HTTP 429 | VERIFIED — reproduced today (429, Vercel Security Checkpoint) |
| 68 | punkpeye/awesome-mcp-servers CONTRIBUTING: "Contributions are welcome and encouraged!" · "If you are an automated agent… add `🤖🤖🤖` to the end of the PR title to opt-in. Merging your PR will be fast-tracked." · "Alphabetical order: Maintain alphabetical order within each category" · "One server per line" | VERIFIED |
| 69 | wong2/awesome-mcp-servers: "> [!NOTE] We do not accept PRs. Please submit your MCP on the website: https://mcpservers.org/submit" | VERIFIED (`gh api repos/wong2/awesome-mcp-servers/contents/README.md`) |
| 70 | anthropics/claude-plugins-community **2,883 stars** | VERIFIED with delta — **2,884** today (+1, immaterial) |
| 71 | Same repo README: "A **read-only mirror** of the community plugin marketplace… synced nightly from Anthropic's internal review pipeline." · "Every plugin listed here has been submitted via claude.ai…" · "Pull requests opened directly against this repo are closed automatically" · install commands | VERIFIED |
| 72 | GitHub topic counts: mcp 67,930 · claude-code 65,988 · ai-agents 81,569 · mcp-server 26,261 · llm 123,173 | VERIFIED with delta — today 67,931 / 65,988 / 81,570 / 26,261 / 123,174 (+1 on three; no order-of-magnitude change, classification "mcp-server is the only findable one" unaffected) |
| 73 | pypi.org/classifiers/ reachable and is the authoritative classifier list | VERIFIED (200) |
| 74 | arXiv: "arXiv requires that users be endorsed before submitting their first paper to arXiv or a new category." · "you have claimed ownership of a paper submitted by a co-author **and** your email address meets the institutional email criteria" · "Alternatively you can seek personal endorsement… A good choice for graduate students would be your thesis advisor…" · "it is inappropriate to email large numbers of potential endorsers at once" | VERIFIED |
| 75 | Interpretation: ".edu address alone does not clear the gate for a first-time author with no claimed paper" (summary #7, §5) | VERIFIED — the page's condition is conjunctive (claimed paper **and** institutional email); the file reads it correctly |
| 76 | `curl -I https://paperswithcode.com/` → `HTTP/2 302` → `location: https://huggingface.co/papers/trending` | VERIFIED — reproduced today, byte for byte |
| 77 | Venture Café Cambridge, six rows: 09-03 "Uncertainty Principle: AI, Quantum, and the Tools Reshaping Work"; 09-10 "University of Tsukuba Night 2026"; 09-17 "New Frontiers: Space, Health & Global Innovation"; 09-24 "Thursday Gathering - September 24, 2026"; 10-01 "Boston AI Week @ Venture Café!"; 10-29 "Chile Innovation Night at Tough Tech Week" — all 4:30 pm, free, RSVP via GatherUs | VERIFIED (titles, dates, times, free-RSVP-via-GatherUs all exact). The venue string "CIC, 1 Broadway" is **UNCHECKED** — no address appears on the events page |
| 78 | aiweek.boston: "September 16 – October 28, 2026 · Six weeks across Massachusetts" · "Core Festival Week: September 24 – October 2" · "125+ events already approved" · "Mayor Michelle Wu has proclaimed September 24, 2026, to be Boston AI Week in the City of Boston." · "Host an Event" path exists | VERIFIED |
| 79 | bostonaiweek.com is a stub: "Launching Soon", "Copyright © 2024" | VERIFIED |
| 80 | AI Tinkerers Boston next event "Back from Summer: AI GTM Builders" — filed as "partially UNVERIFIED" | VERIFIED — **upgrade**: boston.aitinkerers.org renders "SEP 03 Back from Summer: AI GTM Builders 6:00 PM" directly to curl; no WebSearch corroboration needed. (Time is 6:00 PM, which the file does not state) |
| 81 | meetup.com/ai-native-dev-boston: "Group not found. Sorry, the group you're looking for doesn't exist." at HTTP 200 | VERIFIED |
| 82 | producthunt.com robots.txt allows crawling; posting needs an account | VERIFIED (no blanket `Disallow: /`) |
| 83 | **Summary #1: "Only two mechanisms *reliably* produce unsolicited inbound in 62 days"** | **MISMATCH (unsupported)** — nothing in the file measures inbound conversion for any channel. It is a ranking hypothesis stated as a finding; §8 forbids the undefined confidence term |
| 84 | Instrument log total: 52 citations | VERIFIED — independent extraction of the body gives 55 URL occurrences, **52 distinct URLs** |
| 85 | **Instrument log: "HN + GitHub share: 8 / 52 = 15.4%"** | **MISMATCH (arithmetic)** — recount gives **9 / 52 = 17.3%**. Immaterial to the label |

### Recounted instrument log

Extraction: all `https?://…` in the body above §"Instrument log", deduplicated by full URL, bucketed by host.

- **Distinct source URLs: 52** — identical to the author's total.
- **news.ycombinator.com: 2** (`/showhn.html`, `/submit`). `hackernewsletter.com` is a separate host and is correctly excluded from the HN bucket.
- **GitHub-sourced citations: 7** — three `raw.githubusercontent.com/modelcontextprotocol/registry/…mdx` files, `punkpeye/awesome-mcp-servers` raw CONTRIBUTING.md, `gh api repos/wong2/…/README.md`, `gh api repos/anthropics/claude-plugins-community` (stars + README), and `gh api -X GET search/repositories` for the five topic counts in §4.5. The author's table says 6; the topic-count query is the missing seventh. (The single literal `github.com/…` string in the body is the user-agent, not a citation.)
- **HN + GitHub = 9 / 52 = 17.3%** (author: 8 / 52 = 15.4%). Both are far under 70%: the **NOT instrument-biased** label stands and no confidence downgrade is triggered.
- Minor allocation errors in the author's host table, none affecting the total or the share: `fosdem.org` is 2 not 1 (`/2027/` and `/2027/news/`); `tldr.tech` is 2 not 1 (`/` and `/advertise`); `bonobopress.com`, `clau.de` and `mcpservers.org` appear in the body but in no row.

### §8 sins audit

- **Private individuals:** clean. No names, handles or personal emails of private individuals anywhere in the file. The only emails are organizational (`hello@console.dev`, `info@fosdem.org`). The DevOps'ish quote stops immediately before the editor's name; the Import AI address is withheld with a §2 note; the one person named, in a verbatim quote, is a sitting mayor acting in office. This file passes the rule cleanly.
- **Paraphrase presented as quote:** one instance, claim 62 (Glama timestamp `01:00` vs `01:08`). Everything else quoted is verbatim, including punctuation and emoji.
- **Pre-satisfied gates:** none. Every date in §7's sequencing (09-06, 09-13, 09-19, 09-24→10-02, 10-12) is in the future and can fail.
- **Undefined terms:** one, "reliably" in summary #1 (claim 83).
- **Derived numbers without arithmetic:** one, the "4%" of claimed Glama servers (claim 63).
- **"Incumbent exists = kill" / pain-without-budget:** not applicable — this is a channel inventory, and it separates $0 from paid mechanisms correctly throughout, which is the right form of the budget test for a distribution file.

### Verdict

**The file's conclusions hold at their stated confidence.** 76 of 85 claims verified against today's sources, zero unreachable, and every quotation load-bearing on a verdict — Show HN's off-topic rule, Changelog's commercial ban, the MCP Registry's `mcp-name` requirement, PulseMCP's pause, the arXiv endorsement conjunction, the two Discord no-marketing rules, and all six Venture Café listings — is verbatim. The structural findings survive intact: the study is a regular HN submission and not a Show HN; the registry publish is the single action that feeds the directory graph; arXiv endorsement is a dated blocking dependency, not a formality; no Discord is a launch venue; Reddit is genuinely unverifiable under robots and is honestly labeled as such. The five mismatches are all cosmetic or self-inflicted at the summary layer rather than the evidence layer — a wrong minute in one quoted timestamp, a fortnightly meetup described as weekly, a share recomputed from 15.4% to 17.3% that changes no label, and two summary sentences that overstate what the body actually established ("reliably produce inbound", "SRE Weekly's front page is paid", the latter contradicting the file's own §1 row). The two genuine evidence gaps to close are the mcp.so free lane, where no free submit control is visible pre-auth and "$0 path" is therefore unsourced, and Boston Python's "no talk night in September", a negative claim over 40 upcoming events of which the page renders five. Fix those seven items in the author's pass and the file is sound; none of them moves a channel in or out of either top-10 ranking.

**Fix pass: 8 items fixed, 2 marked UNVERIFIED, 1 conclusion downgraded.** (Fixed: summary #1 restated as a hypothesis, summary #6's SRE Weekly clause, the Glama quoted timestamp, Boston Python's fortnightly office hour in §2 and §6, the Boston Python talk-night claim re-sourced from the paginated /events/ listing, the mcp.so free-lane claim, the §7a 4.1% arithmetic shown inline, and the instrument log's host table and 9/52 = 17.3% share. UNVERIFIED: the mcp.so free lane; per-channel inbound conversion. Downgraded: summary #1 from finding to ranked hypothesis; mcp.so is consequently not counted as a $0 channel.)
