# Track H — follow-up drafts

Three emails, in order. All `{placeholders}`. **The principal sends them; the agent never does**
(CLAUDE.md §2, RED). No names, no personal email addresses, and no prices anywhere in this file.
Person-shaped details for a live thread go in `private/outreach/`, never here.

Rules for all three: plain text, no attachment, no tracking pixel, no link-gate, no calendar tool.
Every claim must be true on the day it is sent (see `opener.md`).

---

## 1 · Within 24 h of meeting them
*(Session 1 template from `outreach/queue.md`, updated for v2: read-only clone is the ask, the
install command is corrected, and the study is described as in progress.)*

**Subject:** the autopsy — 60 min, your repo, no pitch

> Hi {first name},
>
> Good to meet you at {event} on Thursday. As promised: a free 60-minute agent autopsy on
> {repo or team}.
>
> What happens: on a call, on a read-only clone you control, I run `@microsoft/agentrc` (Microsoft's
> free readiness scorer — its own README calls it experimental, which is fair and isn't my point; the
> point is that on my own tested, locked, linted Python repo it reported zero tests, no lockfile, and
> told me to install Prettier, and nothing generic can know your stack), Claude Code's `claude doctor`,
> and `cc-safety-net` if you want it. Then the part no tool does: I read your codebase for an hour
> beforehand and bring the three repo-specific invariants I'd put a hook on — the "nothing outside
> `db/` writes raw SQL" kind, not the "don't `rm -rf`" kind. You get a one-page writeup the next day
> and you keep it. If nothing's useful you've lost an hour and I've learned something.
>
> I don't need production access, credentials, or CI — a read-only clone or a public repo is enough,
> and I delete it the same day.
>
> One thing up front, because you'd want to know before you send anything: the prep is AI-assisted.
> Coding agents read the clone, so file contents from it go to a third-party model provider's API and
> are handled under that provider's terms. If you'd rather they didn't, say so — I'll read it myself
> with no agent involved, or we keep the whole thing to a public repo. Either way you get the same
> hour and the same one-pager. I won't clone anything until you've answered that.
>
> Two slots next week: {slot 1}, {slot 2}. Reply with a repo and one thing your agents keep getting
> wrong.
>
> Alex
> _(CS + Math at Northeastern · {github link} — the fenced-agent control plane and the
> patch-verification engine are both there, with the tests)_

*Optional personalization line, one sentence, from their own public job post — e.g. "your {role} req
says {short quote}; that's exactly the setup I autopsy." Quote the post, never a person, and never
reference a pseudonymous forum thread.*

---

## 2 · Within 24 h of the autopsy — "here is your report"

**Subject:** your agent autopsy — {repo}, one page

> Hi {first name},
>
> Thanks for the hour. The one-pager is below — it's yours, no strings, forward it to whoever should
> see it.
>
> Two things worth doing this week regardless of anything else I said:
> 1. `npx -y cc-safety-net@2.2.2 install --{their agent cli}` — free, MIT. Footprint, so you can check
>    it: it edits `~/.claude/settings.json` (adds `extraKnownMarketplaces` and `enabledPlugins`),
>    clones a third-party community marketplace repository — not Anthropic, not a vendor — into
>    `~/.claude/plugins/`, plus a ~10 MB cache and two bookkeeping JSON files, and touches
>    `~/.claude.json` after backing it up to `~/.claude/backups/`. Don't take that repo's URL from me:
>    after install, the exact `owner/repo` is written into your own `~/.claude/settings.json` under
>    `extraKnownMarketplaces.cc-marketplace.source.repo` — read it there and decide. Install needs
>    network, because of that clone.
>
>    `npx -y cc-safety-net@2.2.2 uninstall --{their agent cli}` removes the integration and the
>    marketplace clone. Two things it leaves, if you want them gone:
>    `rm -rf ~/.claude/plugins/cache/cc-marketplace` (the ~10 MB cache) and, optionally, the single
>    `~/.claude/backups/.claude.json.backup.<epoch-ms>` file it created. **Please don't `rm -rf`
>    `~/.claude/plugins/` itself** — that directory is the shared root for every Claude Code plugin and
>    marketplace you have, and `known_marketplaces.json` / `installed_plugins.json` in it are shared
>    bookkeeping for all of them, so leave both files alone. Verified on an isolated home directory:
>    after uninstall those two paths are the only leftovers worth deleting — the rest is those two
>    shared JSONs and a small sweep marker, which should stay.
> 2. `/doctor` inside a Claude Code session — it audits the instruction file you already have and its
>    headline move is *deleting* lines, not adding them.
>
> The clone is deleted. Nothing of yours is in my notes except {the one thing you asked me to
> remember}, and that is company-level and unattributed.
>
> ---
>
> {THE REPORT — paste the six sections from runbook.md §3 inline: Scope · Tool results and what they
> got wrong · The three invariants · Monday list · What this did not cover · Provenance.}
>
> ---
>
> Two notes on the report. First, the prep was AI-assisted, and here is exactly what that means: a
> coding-agent swarm read the clone, so file contents from your repo were sent to a third-party model
> provider's API and handled under that provider's terms — the thing I flagged before you sent it, and
> the no-agent alternative is still open for any future one. I checked every invariant candidate by
> hand against your repo before it went in here. The clone is deleted and nothing of yours is retained
> on my machine or in any repo of mine, except de-identified company-level notes (sector, rough team
> size, stack, which tool claims were false, which invariant you corrected) with no name and no quotation
> of your source; that is a statement about my side only, and I'm not going to claim anything about the
> provider's side beyond their published terms.
> Second, {invariant N} is the one *you* corrected in the room — I kept your version.
>
> If any of the three hooks turns out to be wrong once it meets a real branch, tell me. That's the
> most useful thing I could get from this.
>
> Alex

**Never** add a "next steps", a scope, a proposal, or a number. The report is the end of the
transaction. Log the outcome company-level in `SIGNALS.md`; person-shaped notes go in
`private/outreach/`.

---

## 3 · Two weeks later — one check-in, then stop

**Subject:** did the {invariant 1 short name} hook survive?

> Hi {first name},
>
> Two weeks on — curious whether the {invariant 1 short name} hook is still in place or whether
> someone turned it off in week one. Either answer is useful to me; "we deleted it on day three" is
> the more useful one.
>
> {If they named something in the room: You mentioned {the thing they said they'd want}. Still on your
> list, or did it solve itself?}
>
> No ask — I'm building a picture of which fences actually hold across teams, and yours is one of
> {n}.
>
> Alex

**Stop rule:** if there is no reply to this, there is no fourth email. Ever. A team that goes quiet is
data, not a lead.

**If they reply asking what a paid version would cost:** do not answer with a number. Reply:
> Honestly, I don't have one yet — you'd be the {ordinal} team to ask, and I'd rather come back with a
> real answer than invent one. Can I ask what you'd want it to cover?

Then log the request **verbatim** in `SIGNALS.md` (company-level, no name). Two independent teams
asking to pay for the *same* capability is the Track P re-open rule (CLAUDE.md §7); one is a data point.
Pricing is the principal's call, after the gates in `DECISION.md`.
