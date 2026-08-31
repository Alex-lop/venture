# Track H — the 20-second opener (v2)

**Truth rule (CLAUDE.md §2): every claim here must be true on the day it is said.**
As of 2026-08-30 **nothing is published on PyPI and the study is not published.** So the credential
today is *the code that exists and passes tests on GitHub* plus *a measurement in progress* — not
"shipped packages". Each block below marks the swap-in line to use **once** those are true.

---

## The default opener (Venture Café / AI Native Dev Boston)

> I'm Alex, CS + Math at Northeastern. I've spent the summer building the guardrail layer around
> coding agents — fenced workspaces, plan validators, egress firewalls, a differential PR verifier.
> About 220K lines, all public, and the guardrail suites are green: 1,229 tests on the control plane
> and 408 on the lease runtime. Right now I'm measuring something nobody's published: across public
> Python repos with green test suites and merged agent-written PRs, how often the PR's own tests pass
> on the *old* code too — the test that proves nothing.
>
> While that runs I'm doing free 60-minute agent autopsies for a handful of engineering leads. You
> pick a repo, read-only clone is fine. I run Microsoft's free readiness scorer and Claude Code's
> `claude doctor` live, install `cc-safety-net` if you want it — and then the part no free tool does: I've
> read your codebase for an hour beforehand and I bring the three places in *your* repo where an
> agent will do something you'd never let a junior do. No pitch, no price. I'm collecting what breaks.
> Want one?

**Swap-in once a package is on PyPI:** replace *"About 220K lines, all public"* with
*"Two of those are pip-installable now — `{package}` and `{package}`."* Keep the test counts.

**Why counts and not "all tested":** `ASSETS.md` records a red suite on the portfolio site, ~45% of
Nemisis's `src/` tested only against fakes, and `benchmarks/` in Graphene with no benchmark. Two named
passing numbers are true, checkable, and survive a hostile reader with `ASSETS.md` open — `ASSETS.md:9`
→ **1,229 passed** on Graphene, `ASSETS.md:10` → **408 passed** offline on RegLineage. "All tested"
does not.

**Why two and not three.** An earlier draft added *"238 on the read-only data boundary."* Drop it and
never restore it. `ASSETS.md:12` attributes those 238 tests to **X-Scraper as a whole** — a local
feed-to-snapshot workbench for X that captures behind a *logged-in* session — not to the read-only
data boundary, which is one file inside it (`mcp_server.py` `_ReadOnlyStorage`, `ASSETS.md:89`).
`ASSETS.md` flags that repo **not commercializable as-is (X ToS)**, and a login-scraping tool collides
with CLAUDE.md §2's "never behind a login" in the middle of a trust pitch. The repo is public, so a
prospect can and will look. If asked *"which repo is that?"*, answer before they find it:
> "A local snapshot workbench for X I built before I'd read their terms properly — it can't ship, and
> I say so in its own docs. The reusable piece is the read-only SQLite gateway inside it, which is the
> thing I described."

**Where 220K comes from** — `ASSETS.md`'s own per-repo LOC, added up: Graphene 137K + RegLineage 49.6K
(33.5K src + 16.1K tests) + X-Scraper 26K + Nemisis 4.3K + the two sites 3.7K ≈ 220K. It excludes the
Graft fork, which is someone else's repo with 0 commits by the principal. If any of those numbers move,
recompute or drop the figure — never round it upward.

**Swap-in once the study is published:** *"Right now I'm measuring"* → *"I published the number for"*
and add the one-line result. Not before.

**Timing:** the credential is the first 8 seconds. If they lean in, the ask is the last 5. If they
don't, stop after the test counts and ask what they're running.

---

## Variation — platform / dev-productivity lead (they own the tooling budget and the pain)

> I build the seatbelt layer for coding agents — the part that decides which agent-proposed change is
> allowed to become a commit. Fences, plan validation, an audit trail you can verify offline. What I
> keep finding is that the generic tools are all *harness*-shaped, not *repo*-shaped: they'll tell a
> tested Python repo it has no tests. I'm doing free 60-minute autopsies — I read a repo beforehand
> and bring the three architectural invariants that are worth an actual hook, the "nothing outside
> `db/` writes raw SQL" kind, not the "don't `rm -rf`" kind. That part's judgment; it's why it's free
> and why nobody ships it in a box.

## Variation — CTO of a ~30-person company (wears every hat; sell one hour, not a program)

> Your engineers are running Claude Code or Cursor and you've probably got a `CLAUDE.md` somebody
> wrote once. I do a free 60-minute session: three free tools live on a read-only clone, and then the
> three places in your codebase where an agent will confidently do the wrong plausible thing — with
> the hook that stops each one. You get a one-page writeup the next day and you keep it. It's one
> hour, I don't need production access, and there's nothing to buy at the end. I'm doing them because
> I'm collecting what actually breaks across teams, and I don't have enough of them yet.

## Variation — data-platform lead (agents near the data layer; lead with egress and read-only)

> My background is agents touching governed data — capability leases that expire, a value-level
> egress firewall that raises instead of quietly redacting when a tool response carries a field the
> agent was never granted, a read-only MCP gateway over a local SQLite file — opened `mode=ro` with
> `PRAGMA query_only`, allowlisted, question-shaped tools. So when I do these free 60-minute
> autopsies, for a data platform the three invariants usually land on your access layer: what an agent
> may join, what may leave a tool response, which migrations it must never author. Read-only clone,
> one hour, one page back the next day. Interested?

---

## "So what do you sell?" — the two-sentence answer

> Nothing yet. The autopsy is free and there's no version of it I'm charging for today — what I have
> is the study I'm running and the guardrail code on GitHub, and I'm doing these sessions to find out
> what teams would actually want built.

**If pushed a second time** ("come on, what would this cost?"):
> Honestly, I don't have a number — I'd be making one up, and you'd know it. Ask me again after I've
> done a few more of these and I'll have a real answer.

**Never** name a figure, a range, a "typically", or an anchor of any kind. This is RED
(CLAUDE.md §2); the principal names prices, and only after the gates in `DECISION.md`.

## Two objections that will come up

- **"We already run `cc-safety-net`."** *"Good — I'd have installed it for you in minute 25. Watch
  what it tells you about itself: at the standard preset it allows `rm -rf ./build` and prints the
  reason, `rm.recursive-force-paranoid — off via preset`. Flip to paranoid and it blocks — and it
  blocks your fixtures directory too. Two settings, allow-everything and block-everything, because
  it has never read your repo. The setting that's right for your build cache is wrong for your
  fixtures. That gap is what the hour is for."* (Do not claim the tool has no rule for this — it
  has one, off by default, and it says so on screen. See `runbook.md` §2, 25–35.)
  (If two separate teams say cc-safety-net is *sufficient*, that is the dossier's own kill criterion —
  log it verbatim in `SIGNALS.md`.)
- **"We'll just run agentrc."** *"Let's run it right now, it takes two minutes."* On a non-JS repo the
  counter-demo makes itself (`runbook.md` §2). On a JS repo, say so and move to the invariants.
