# Track H — the free 60-minute agent autopsy (runbook)

**Status:** Track H opt-in = yes (`private/PRINCIPAL.md`). Two Thursdays a month, capacity ≤ 4.5 h/week
(`DECISION.md`). Gate: **≥5 accepted autopsies by 2026-09-30**. Calendar and in-room opener: `outreach/queue.md` §A.

**Report shape is fixed** (§3): those six sections are the spec `pkg-agent-autopsy` (CLAUDE.md §5) will
emit — **UNVERIFIED: that package does not exist yet**; the shape is intent, not an observed fact.
**Every command below was run on 2026-08-30** on the principal's own repos or a copy of them; output is
quoted verbatim, trimmed blocks marked *abridged*. Every version is pinned: the published agentrc
install command does not work as written, and `cc-safety-net` shipped four releases in two days.

---
## 1. Before — 30–60 min prep, agent-assisted

### What the principal asks for (in the follow-up email, `followups.md`)
1. **A repo.** A read-only clone, a public repo, or a tarball. Read-only is enough and is the ask —
   it removes the "20-year-old wants production access" objection before it is raised.
2. **One sentence:** *"one thing your agents keep getting wrong."*
3. **Nothing else.** No credentials, no VPN, no CI, no prod anything.
4. **Consent to the AI-assisted read — in that same email, before anything is cloned.** Coding agents do
   the prep, so file contents from the clone are sent to a third-party model provider's API and handled
   under that provider's terms. Offer the alternative in the same breath: the principal reads it alone
   with no agent involved, or the autopsy stays on a public repo. **No clone is read until they answer.**
   A security-conscious buyer finds this out eventually; only the version where they heard it first survives.
### Pre-read checklist (30 min, run by the swarm on the clone)
| # | Look at | Question it answers |
|---|---|---|
| 1 | `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, `.github/copilot-instructions.md` | What have they already written down? Is it bloated? (Never rewrite it — see §4.) |
| 2 | `.github/workflows/`, pre-commit config, `Makefile`/`justfile` | What is *enforced* vs. merely *documented*? The gap is the product. |
| 3 | Test layout: where tests live, what one test run costs, is there a lockfile | Whether a hook can even run cheaply |
| 4 | Dependency + package manifests | Stack, so the agentrc counter-demo can be predicted before the room |
| 5 | **Where a junior would be stopped:** DB/query layers, auth & session code, migrations, money/pricing/billing, deploy & infra scripts, generated or vendored files, public API surfaces | The candidate invariants |
| 6 | `git log` on those paths: revert commits, hotfixes, "fix: don't" commit messages | Which invariant has *already* been violated — the strongest candidate |

### Producing the three candidate invariants
Repo-specific and architectural, never generic safety — generic safety is free (§2, step 3). The
deliverable is the layer above it: **the fence that knows this repo has a `PaymentService`.** Produce
**three**, each with: the rule in one sentence · the paths it governs · the hook that enforces it · a
one-line test that fails today if broken. Rank "has this already bitten them" (`git log`) over elegance.

### The prompt the principal pastes to prepare
```
Read this repo (read-only; do not modify, do not run anything that writes outside /tmp).
Produce exactly 3 candidate architectural invariants for a 60-minute agent autopsy.

Method:
1. Read CONTRIBUTING.md, AGENTS.md, CLAUDE.md, .cursor/rules, .github/copilot-instructions.md. Note
   what is written down but NOT enforced anywhere in CI or hooks.
2. Map the enforcement surface: .github/workflows/, .pre-commit-config.yaml, Makefile/justfile,
   package scripts. What is actually blocked today?
3. Find where a new hire would be stopped in review: DB/query access layers, auth and session
   handling, migrations, money/pricing/billing, deploy and infra scripts, generated/vendored files,
   public API surfaces.
4. Per candidate, `git log --oneline -- <paths>`: reverts, hotfixes, "fix: don't ..." messages.
   Prior violation outranks elegance.

For each of the 3, output:
  - RULE: one sentence, in their vocabulary, naming their own types/modules
  - PATHS: the exact globs it governs
  - WHY AN AGENT BREAKS IT: the specific wrong-but-plausible thing an agent does here
  - EVIDENCE: file:line, or a commit SHA where it already happened; "none found" if none
  - HOOK: the concrete PreToolUse/pre-commit check, as a runnable snippet
  - TEST: one line that exits non-zero if the rule is violated

Rules: no generic safety rules (rm -rf, secrets, force-push) — cc-safety-net covers those free. No
rule requiring a new CLAUDE.md. No rule you cannot show evidence for. If only 2 have evidence, say
so; do not invent a third.
```

Time-box prep at 60 min. Two candidates with evidence beats three with one invented — bring two and say so.

---

## 2. During — 60 minutes, minute by minute

### Pre-flight — the morning of, on real Wi-Fi
Node 18+ per `cc-safety-net`'s declared `engines` (`npm view cc-safety-net engines` → `{ node: '>=18' }`);
`@microsoft/agentrc` declares no `engines` field at all. Verified on v26.7.0 / npm 12.0.2. Re-verify the
pins (`npm view cc-safety-net version`, `npm view @microsoft/agentrc version`) and re-run the traces
below if either moved — the quoted output is the claim, so a version bump invalidates it.

**Conference Wi-Fi is the single most likely failure of this hour, and warming the npm cache *does* fix
it.** Run the two pins once online in the morning; every in-room command below then carries `--offline`:
```sh
npx -y cc-safety-net@2.2.2 explain "rm -rf ./build" >/dev/null   # warm the cache
npx --yes @microsoft/agentrc@2.0.1-0 --version >/dev/null        # warm the cache
```
Verified 2026-08-30 on a copy of Nemisis: under `--offline`, all three `explain` traces and the full
`readiness` report reproduced the output quoted below. `--offline` fails closed rather than quietly
reaching the network — an uncached pin gives `npm error code ENOTCACHED ... cache mode is
'only-if-cached'`. Expect two `npm notice run …` lines above each trace; name them, move on.
**The one exception is `cc-safety-net install`** — it clones a marketplace repo and no cache warms that.
If Wi-Fi is down, skip the install, put it in the follow-up email, and nothing else in the hour is lost.

### 0–5 · Frame
*"Before anything else: the prep was agent-assisted, exactly as I said before you sent the clone — file
contents went to a third-party model provider's API, and everything in the report I re-checked by hand.
Three free tools on this repo, then the back half on what the free tools can't do. They will get
things wrong; that's the useful part."*

### 5–15 · microsoft/agentrc — the counter-demo

> **The published install command does not work on current npm.** The README says `npx
> github:microsoft/agentrc`. On npm 12.0.2 that fails:
> ```
> npm error code EALLOWGIT
> npm error Fetching packages of type "git" have been disabled
> npm error Refusing to fetch "github:microsoft/agentrc"
> ```
> Cause: `allow-git = "none"` is npm 12's built-in default (`npm config ls -l`). Verified 2026-08-30.

**Use the registry build instead** — npm `@microsoft/agentrc`, latest `2.0.1-0`, **published
2026-03-14** (2026-07-16 is the package's registry-wide `modified` timestamp, not this version's publish
date; it is the publish date that goes in the report's Provenance line). The `next` tag is `2.0.1-91`,
2026-06-15 — newer than `latest`, so say so before a prospect opens npm and spots it. Repo tip
`8d0c05c` 2026-06-18; MIT. From `npm view … time --json` / `dist-tags` + the GitHub API, 2026-08-30.

```sh
npx --yes --offline @microsoft/agentrc@2.0.1-0 readiness
```

**Say the experimental banner out loud before criticizing anything.** The README's own header reads
verbatim `> [!WARNING]` / `> **Experimental** — Under active development. Expect breaking changes.`
(re-verified 2026-08-30). Lead with it — *"their own README calls this experimental, and that is not my
criticism; a prototype is allowed to be rough"* — or the strongest ten minutes of the hour reads as a
straw man to anyone who opens the repo afterwards. The criticism that survives is the one below, and it
is true of the shipped 1.0 of every generic scorer: nothing generic can know your stack.

**Observed on a copy of `Alex-lop/Nemisis` (Python, uv, pytest), 2026-08-30, exit 0, re-run under
`--offline`** — *abridged*: the `- Repo:` path line, six of the eight Repo Health rows, and ten of the twelve "Fix first" items cut (the list runs long on a real repo); full log kept.

```
Readiness report
- Monorepo: no
- Level: 0 (Functional)

Repo Health
● Testing: 0/0 (0%)                 ● Code Quality: 0/1 (0%)

AI Setup
● AI Tooling: 0/4 (0%)

Fix first
- High impact / Low effort • Linting configured [repo]
  Missing ESLint/Biome/Prettier configuration.
- High impact / Low effort • Lockfile present [repo]
  Missing package manager lockfile.
```

**The counter-demo, three claims, each falsified from the repo in front of you:**

| agentrc says | Ground truth in that repo | Show it |
|---|---|---|
| `Testing: 0/0 (0%)` | 9 `test_*.py` files, a full pytest suite that passes | `uv run --offline pytest -q` → `113 passed in 2.90s` (and `find tests -name 'test_*.py' \| wc -l` → `9`) |
| `Missing package manager lockfile` | `uv.lock`, 605 lines, committed | `wc -l uv.lock` → `605 uv.lock` |
| `Missing ESLint/Biome/Prettier configuration` | ruff pinned and configured | `grep -n 'ruff' pyproject.toml` → `"ruff>=0.12,<1"`, `[tool.ruff]`, `[tool.ruff.lint]` |

**The line:** *"It scored a tested, locked, linted Python repo at Level 0 and told it to install
Prettier. It's a JS-shaped scorer. That is not a knock on Microsoft — it's the shape of every generic
readiness tool. Nothing generic knows your stack, and nothing generic knows your architecture."*

Then run it on **their** repo, live. If their repo is JS/TS the scorer behaves better — say so out loud;
the honesty is the credibility, and the argument does not depend on it failing.

### 15–25 · Claude Code `/doctor`
Verified in current docs 2026-08-30: **https://code.claude.com/docs/en/commands**
(`https://docs.claude.com/en/docs/claude-code/slash-commands` now 301s to `code.claude.com/docs/en/...`).
Documented verbatim as: *"Run a setup checkup that diagnoses issues and can fix them… Deduplicates local
`CLAUDE.md` files against checked-in ones, trims checked-in `CLAUDE.md` files by cutting content Claude
could derive from the codebase… Reports findings first and asks for confirmation before changing
anything. From the terminal, `claude doctor` prints read-only installation diagnostics without starting a
session. Alias: `/checkup`."*

**In the room, run the terminal form — it cannot change anything on their machine:**
```sh
claude doctor
```
Observed on Claude Code 2.1.251, 2026-08-30, exit 0 — *abridged*: the version/path boilerplate is cut,
the two lines that matter are verbatim:
```
Claude Code doctor

Running: native (2.1.251)
Platform: darwin-arm64
Auto-updates: enabled
Last update attempt: success → 2.1.251 (2026-08-30)
Managed settings (remote): not fetched — requires an Enterprise or Team subscription

Remote Control
Control this session from claude.ai/code or the Claude mobile app

No installation issues found.
```
**Two of those lines are not diagnostics** — the subscription-tier line and the Remote Control promo.
Name them in one breath (*"those two are product lines, not findings"*); do not discover them live.
Offer the in-session `/doctor` only if they ask, only on their keyboard, pointing at the confirmation
prompt first. The `CLAUDE.md` **trim** check needs v2.1.206+; if they are older, the context-diet
finding is yours to make by hand from the pre-read.

**The line:** *"This one pays for itself in five minutes — it audits the file you already wrote, and its
headline move is deleting instructions, not adding them."*
### 25–35 · cc-safety-net — install the free floor, then show its ceiling
npm `cc-safety-net`, **v2.2.2**, MIT, published 2026-08-25 and still latest on 2026-08-30; docs
https://ccsafetynet.com/docs; 13 agent CLIs (Claude Code, Codex, Cursor, Gemini CLI, Copilot CLI, …).
**Pin it in every command:** 2.1.1 → 2.2.0 → 2.2.1 → 2.2.2 all shipped inside 2026-08-24/25, `@latest`
can move between prep and the room, and the quoted traces below are the claim.

**Zero-footprint demo first** — `explain` writes nothing, so run it before asking to install anything.
**From inside their repo, never `$HOME`:** in a home directory `rm -rf ./build` matches a different rule
("rm -rf in home directory is dangerous") and the whole demo inverts.

```sh
npx -y --offline cc-safety-net@2.2.2 explain "git checkout -- ."
npx -y --offline cc-safety-net@2.2.2 explain "rm -rf ./build"
CC_SAFETY_NET_LEVEL=paranoid npx -y --offline cc-safety-net@2.2.2 explain "rm -rf ./build"
```

Observed 2026-08-30 from inside a git repo, exit 0 each time, cache warmed that morning and the pins run
`--offline`. Full output, nothing trimmed:

```
INPUT
  git checkout -- .

STEP 1 - Split shell commands
  Segment 1: ["git","checkout","--","."]

STEP 2 - Match rules
  Rule:   git:analyzeGitMatch()
  Result: MATCHED

RESULT
  Status: BLOCKED
  Reason: git checkout -- discards uncommitted changes permanently. Use 'git
          stash' first.
```
```
INPUT
  rm -rf ./build

STEP 2 - Match rules
  Rule:   analyzer/rm.ts:analyzeRmMatch()
  Result: No match

RESULT
  Status: ALLOWED

CONFIG
  Safety preset: standard
  Effective capabilities: standard
  Rule activation: rm.recursive-force-paranoid — off via preset
```
```
INPUT
  rm -rf ./build          # CC_SAFETY_NET_LEVEL=paranoid

STEP 2 - Match rules
  Rule:   analyzer/rm.ts:analyzeRmMatch()
  Result: MATCHED

RESULT
  Status: BLOCKED
  Reason: rm -rf for non-temporary paths is blocked by the active safety policy.
          Retry deleting only explicit paths inside the current directory;
          escalate for anything outside it.

CONFIG
  Safety preset: standard
  Effective capabilities: paranoid
  Rule activation: rm.recursive-force-paranoid — on via environment
```
*(Abridged: all three omit the `+== Command Analysis ==+` banner npx prints above them and the constant
`Path: none` / `Rule customizations: 0` config lines; traces 2–3 also omit their `STEP 1` line, identical
to each other, and trace 1's `CONFIG` block is `standard` throughout with no `Rule activation` line.
Everything else is verbatim; the full logs are kept.)*

**This is the hinge of the hour, and the last line of the trace is the argument.** The tool ships a rule
for exactly this case — `rm.recursive-force-paranoid` — and prints that it is off. Never say "it has no
rule for this": anyone reading the screen you are projecting will correct you and the hinge collapses at
minute 30 with 25 minutes left. Show both presets, then say:

> "Install this today — free, MIT, better than anything I'd write for you in an hour. Now look at what
> it's telling you. Standard lets `rm -rf ./build` through and names the rule it turned off. Paranoid
> blocks it — and also blocks your fixtures directory, your `dist/`, and the temp tree your integration
> suite rebuilds on every run. A generic tool only ever has two settings, allow-everything and
> block-everything, because it has never read your repo. The setting that's right for your build cache
> is wrong for your fixtures. That gap is judgment. It's the next 25 minutes."

If someone says *"so just set paranoid"* — good, they read the screen; that is the demo landing, not a
counter to it. Ask which of their own directories they would have to except by hand and write the list
down: that list is the invariant conversation starting ten minutes early.

**Install only if they want it, on their machine, on their keyboard. `install` needs network** (it clones
a marketplace repo), so if Wi-Fi is down, skip it and put it in the follow-up email.
```sh
npx -y cc-safety-net@2.2.2 install --claude-code    # or --cursor, --codex, --gemini-cli, ...
npx -y cc-safety-net@2.2.2 uninstall --claude-code
```

**Recite the footprint before they press enter.** Measured 2026-08-30, v2.2.2, into an isolated empty
`HOME` (the principal's own `~/.claude` was never touched). `install` prints
`Installed Claude Code integration` and:

- **edits `~/.claude/settings.json`** — adds `extraKnownMarketplaces` and
  `enabledPlugins: {"cc-safety-net@cc-marketplace": true}`
- **creates `~/.claude/plugins/`** — a git clone of a third-party community marketplace repository
  (not Anthropic, not a vendor). **Do not read its URL off a slide or an email — the exact `owner/repo`
  is written into `~/.claude/settings.json` under `extraKnownMarketplaces.cc-marketplace.source.repo`;
  tell them to read that value and decide.** Plus `cache/cc-marketplace` (~9.9 MB),
  `known_marketplaces.json`, `installed_plugins.json`, `.last_inuse_sweep`
- **touches `~/.claude.json`** — outside `~/.claude/` entirely — after backing it up to
  `~/.claude/backups/.claude.json.backup.<epoch-ms>`

`uninstall` prints `Uninstalled Claude Code integration`, empties both settings keys — leaving them
present as `"enabledPlugins": {}` / `"extraKnownMarketplaces": {}` rather than restoring them to
absent — and removes the marketplace clone (`plugins/marketplaces/cc-marketplace` is gone). **It leaves
behind** the ~9.9 MB plugin cache, both bookkeeping JSONs, the sweep marker, and the `.claude.json`
backup. Exactly two lines finish it, and nothing wider:
```sh
rm -rf ~/.claude/plugins/cache/cc-marketplace            # the 9.9 MB clone cache
rm -f ~/.claude/backups/.claude.json.backup.<epoch-ms>   # optional; `ls ~/.claude/backups/` names it
```
**Never say `rm -rf ~/.claude/plugins/`, and say why not.** That is the shared plugin root for *every*
Claude Code plugin and marketplace on the machine, and `known_marketplaces.json` /
`installed_plugins.json` are shared bookkeeping for all of them — **leave both JSONs alone**; deleting
them breaks installs unrelated to this tool. Recommending an over-broad `rm -rf` in the hour whose whole
thesis is *agents do destructive, plausible-looking things* is the one mistake that cannot be walked
back. Verified 2026-08-30 in an isolated `HOME`: `.claude/` is 9.9 MB after uninstall, 16 KB after the
two lines above. Never install anything on someone's laptop whose footprint you cannot recite.

### 35–55 · The three invariants (the deliverable)
Twenty minutes, roughly seven each. For each one, on screen, in their repo:
1. **The rule**, in their vocabulary, naming their own module. *"Nothing outside `db/` constructs raw SQL."*
2. **Where it already broke** — commit or file:line from prep. If none, say "prophylactic" and rank it third.
3. **Why an agent breaks it:** it reads three files, sees a plausible pattern, and reinvents the thing
   two directories over. Not a model defect — missing context no `AGENTS.md` sentence reliably supplies,
   which is why it goes in a hook, not in prose.
4. **The hook**, on screen, ~10 lines. Worked example below — bring it filled in for *their* repo.
5. **The one-line test** that exits non-zero today if violated.

#### The worked example — carry this shape into every session
Rule: *"Nothing outside `db/` constructs raw SQL."* Two fences, catching it at two moments: the PreToolUse
hook stops the agent mid-edit, the git hook stops whatever the agent talked a human into committing.

**(a) `.claude/settings.json`** — the matcher block. Without this entry the script never runs, and a
PreToolUse hook is not guessable, so show the wiring, not just the script.
```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Write|Edit|MultiEdit",
        "hooks": [ { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/no-raw-sql.py" } ] }
    ]
  }
}
```

**(b) `.claude/hooks/no-raw-sql.py`** — the script. Claude Code delivers the event as JSON on **stdin**
(`tool_name`, `tool_input`, `cwd`); **exit 2 blocks the call and shows stderr to the agent**, exit 0 allows
it. Both at https://code.claude.com/docs/en/hooks (verified 2026-08-30).
```python
#!/usr/bin/env python3
import json, os, re, sys
e = json.load(sys.stdin)
if e.get("tool_name") not in ("Write", "Edit", "MultiEdit"): sys.exit(0)
ti = e.get("tool_input", {})
path = os.path.relpath(ti.get("file_path", ""), e.get("cwd", "."))
body = ti.get("content") or ti.get("new_string") or json.dumps(ti.get("edits", ""))
if path.startswith("db/") or not path.endswith(".py"): sys.exit(0)
if re.search(r"(?i)\b(select\s+.+\bfrom\b|insert\s+into\b|update\s+\w+\s+set\b|delete\s+from\b)", body):
    print(f"BLOCKED: {path} constructs raw SQL. Raw SQL lives in db/ only — use db.queries.", file=sys.stderr)
    sys.exit(2)
```
Ten lines, `chmod +x`, no dependencies. **Run it before the room** — a hook that has never executed does
not go on a stranger's screen. Four cases, 2026-08-30, all as expected:
```sh
echo '{"cwd":"/repo","tool_name":"Write","tool_input":{"file_path":"/repo/services/billing.py",
  "content":"conn.execute(\"SELECT id FROM invoices\")"}}' | .claude/hooks/no-raw-sql.py; echo $?
# BLOCKED: services/billing.py constructs raw SQL. Raw SQL lives in db/ only — use db.queries.  → 2
# same payload with file_path=/repo/db/queries.py  → 0 · no SQL in the body → 0 · tool_name=Bash → 0
```

**(c) The git hook** — `.git/hooks/pre-commit`, `chmod +x`. A plain shell hook, not the `pre-commit`
framework: zero dependencies, and it is the same one-line test from the prep prompt.
```sh
#!/bin/sh
! git grep --cached -nEi '(select .+ from|insert into|update [a-z_]+ set|delete from)' -- '*.py' ':!db/' \
  || { echo "blocked: raw SQL outside db/ (above)"; exit 1; }
```
Two details to say on screen. **`--cached` searches the index, not the worktree** — a pre-commit hook
must judge what is being committed; drop it and `git add -p` breaks the gate in both directions. And the
`!`: bare `git grep` exits **0** on a hit, backwards for a gate. Verified end to end 2026-08-30, five
cases: staged violation → prints the `file:line` then `blocked: raw SQL outside db/ (above)`, commit
exits 1; violation staged **then edited away in the worktree** → still blocked (the worktree form lets it
through); clean index → 0; an **unstaged** violation in another tracked file → commit succeeds (the
worktree form blocks that innocent commit); raw SQL staged inside `db/` → allowed.

**(d) The CI one-liner** — the same predicate with no hook and **no `--cached`**: in CI the checkout *is*
the worktree, so the plain form is the right one there. `! git grep -nEi '(select .+ from|insert into|update [a-z_]+ set|delete from)' -- '*.py' ':!db/'`

Swap the path prefix, extension and regex per invariant; the three-part shape (matcher + stdin/exit-2
script, git hook, CI one-liner) does not change. A rule that cannot be reduced to a path glob plus a
predicate over the new text is not hookable — say so and rank it last. Then ask, and shut up: **"Is that
the right third one?"** Their correction is the highest-value minute of the hour, the thing the package
cannot get, and it goes verbatim into `SIGNALS.md`.

### 55–60 · What to do Monday
Hand them three things and stop talking: the two commands (`cc-safety-net install`, `claude doctor`), the
three hook snippets, and *"you'll have the one-pager in 24 hours."* No ask, no next step, no calendar
invite unless **they** propose one.

---

## 3. After — the deliverable, the cadence, the log

### The one-page report (six sections — the shape `pkg-agent-autopsy` is specced to emit; UNVERIFIED, not built)
```markdown
# Agent autopsy — {repo}
Run {date} · read-only clone {sha} · tools: agentrc {ver}, Claude Code {ver}, cc-safety-net {ver}
Prepared with AI assistance (a coding-agent swarm read the clone); every finding below was
re-checked by hand against the repo.

## 1. Scope
What was read, what was NOT read (no prod, no CI, no data), how long, who was in the room.

## 2. Tool results — and what they got wrong
{agentrc verbatim block} → {the claims that are false for this repo, with the command that disproves each}
{claude doctor verbatim block} → {findings worth acting on}
{cc-safety-net explain traces} → {the floor it gives you, and the specific gap above it}

## 3. The three invariants
### Invariant 1 — {rule in one sentence}
- Governs: {paths} · An agent breaks it by: {specific wrong-but-plausible move}
- Already happened: {commit/file:line, or "no prior violation found"}
- Hook: ```{snippet}``` · Test: `{one line that exits non-zero if violated}`
### Invariant 2 — … ### Invariant 3 — … {their correction to the third, in their words}

## 4. Monday list — ordered, each ≤ 30 minutes, free things first.
## 5. What this did not cover — no runtime, no CI, one hour, one pair of eyes.

## 6. Provenance
Tool versions and dates; the tools are third-party and unaffiliated; this report makes no guarantee
about anything not run in the room. Prep was AI-assisted, concretely: coding agents read your read-only
clone, so file contents from it were transmitted to a third-party model provider's API and handled
under that provider's terms. You were told that and agreed before the clone was handed over, with the
no-AI alternative on the table. The clone was deleted on {date} and nothing of yours was retained on my
machine or in any repo of mine after that date, except the de-identified, company-level notes described
in §1 — sector, rough team size, stack, which tool claims were false here, which invariant you corrected —
kept without your name or any quotation of your source. A claim about my side only; I make no retention
claim on the provider's behalf beyond their published terms.
```

**Editor's note — not part of the report; never paste it into the email.** `plan-lint` and
`egress-guard` are **not yet published**: do not name or link either in a report until it is on PyPI.
`followups.md` §2 says paste the six sections inline — paste the fenced block above, nothing below it.

### Follow-up cadence (drafts in `followups.md`)
Three emails, ever. ≤24 h after the room: the offer, two concrete slots, no price. ≤24 h after the
autopsy: the report inline in the body — no attachment, no link-gate, no tracking pixel. +2 weeks: one
check-in on whether the hooks survived contact. No reply to that one means stop; there is no fourth.

### What to log
**`SIGNALS.md` (public, tracked) — company-level only, no names, no personal emails:** autopsy count vs.
the 5-by-09-30 gate · sector and rough eng-team size · stack · which agentrc claims were false on their
repo · which invariant they corrected · **verbatim what they asked to pay for, if anything** (Track P
re-opens only on ≥2 independent parties naming the *same* capability) · whether they said
"cc-safety-net is enough" (the dossier's own kill criterion).

**`private/outreach/` (gitignored):** who, contact, slots, thread state — everything person-shaped.

---

## 4. Rules in the room (non-negotiable)

1. **No price.** Not a number, not a range, not "usually around". If asked: *"Nothing yet — I'm doing
   these free to learn what breaks. If there's a paid version later I'll know what it is because of
   sessions like this."* Naming a price is RED (CLAUDE.md §2) and gated on `DECISION.md`.
2. **No pitch.** No deck, no follow-on scope, no calendar invite unless they propose it.
3. **Disclose the AI assistance**, unprompted, in the room and in the report — a swarm read their clone,
   and rule 5 says exactly what that means for their data. Saying it first is the credential, not the
   liability.
4. **Never touch a production system.** No credentials, no VPN, no CI, no deploy, no live DB. Read-only
   clone or nothing. `/doctor`'s fixing mode and any install runs on *their* keyboard.
5. **Never keep their code — and say where it travels *before* it arrives.** Clone into `/tmp`, delete it
   same day, say so in §6. Because coding agents do the prep, file contents leave the machine for a
   third-party model provider's API under that provider's terms: say that in the §1 email, offer the
   no-AI alternative (the principal reads it alone, or a public repo only), and get an answer before
   cloning. "Deleted" is a claim about local disk and this repo — never let it stretch into a
   data-handling guarantee about the provider. Nothing of theirs enters this repo; `SIGNALS.md` findings
   are company-level, de-identified, and never quote their source.
6. **Every claim demonstrable in the room.** If a tool is not on screen, it is not in the report.
7. **Never rewrite their `CLAUDE.md` as the deliverable.** That artifact is free and the public narrative
   on it soured in Aug 2026. Subtraction (`/doctor`'s trim) is a finding; generation is not a product.
8. **No names of individuals in any tracked file.** Company-level only — **a third party's GitHub handle
   is a name.** Describe the repository, tell them where the machine prints the real value (above), and
   keep the literal `owner/repo` in `private/`, never here (CLAUDE.md §2).
9. **The Northeastern line is a personal fact and nothing more.** One wording everywhere — *"CS + Math
   at Northeastern"* (`opener.md`, `followups.md`, kept identical); claim nothing beyond it. No NU email,
   wifi, hardware, or campus solicitation, and nothing implying the university is involved or endorsing.
   `private/CLAUDE-v1.md` §0 records Policy 116/120 (name and logo need brand approval for
   customer-facing use) and Policy 700 (no business use of NU resources), and CLAUDE.md §2 makes
   "anything touching the university" RED — so keeping the affiliation in a pitch for something meant to
   become paid is the principal's deliberate call, recorded here rather than drifting in by default.
