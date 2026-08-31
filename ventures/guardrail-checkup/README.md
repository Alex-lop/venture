# guardrail-checkup

**Run it on your own repository and get back the report a consultant would hand you after an
hour: what your agents are actually stopped from doing today, which claims a generic scorer
will get wrong about *this* repository, and up to three ranked places a hook would pay for
itself.**

```
pip install guardrail-checkup
```

Deterministic, offline, read-only. It opens no socket, calls no model, runs nothing from the
repository it reads, and writes nothing inside it — every draft goes to a directory you name.
*Status: 0.1.0. From source: `uv pip install git+https://github.com/Alex-lop/guardrail-checkup`.*

The judgement stays with you. This tool ranks candidates by evidence and says so in the
report; it does not tell you what your architecture means. Deterministic means what it says:
the same commit, with `SOURCE_DATE_EPOCH` set, produces the same bytes apart from the command
line the report records, so two reports can be diffed. Without `SOURCE_DATE_EPOCH` the only
other thing that moves is the date.

## 60 seconds

<!-- pinned: demo/OUTPUT.txt -->
```console
$ guardrail-checkup run shipfast --out REPORT.md --emit-dir drafts
guardrail-checkup: wrote REPORT.md — 17 inventory finding(s), 2 invariant candidate(s), 6 draft(s) in drafts
```

`demo/demo.sh` builds a throwaway repository from `demo/fixture` (a service with a `db/`
directory, a migration, an `.mcp.json`, no hooks, and a `CLAUDE.md` that forbids nothing),
gives it a history with three repairs, and runs the checkup over it. `demo/OUTPUT.md` is the
report it produced; `demo/OUTPUT.txt` is the whole transcript. Both are compared byte for byte
in CI.

## The six sections

The report has the same six sections, in the same order, as the in-person session this
package stands in for:

1. **Scope** — the path, HEAD, size, language mix by file extension, and exactly what was and
   was not read.
2. **Tool results — and what they got wrong** — the guardrail inventory (every row that cites
   a file carries its `file:line`, and one line of *what an agent can do because of this*), what
   `agent-plan-lint` and `egresswall` found, and the falsifier list for the generic scorers.
3. **Invariant candidates** — up to three ranked candidates, each with the paths it governs,
   the evidence, a `PreToolUse` hook that blocks writes there, and a one-line test.
4. **Monday list** — at most five actions, each naming a file this tool emitted or a file to edit.
5. **What this did not cover** — branch protection, production, secrets in history, runtime,
   hooks configured outside this checkout, anything needing a model, and the three tools this
   one does not replace, named with one line each from a checked-in source.
6. **Provenance** — versions, the exact command, what left the machine (nothing), and the
   AI-assistance disclosure.

## What it looks at

| Artifact | What the report says about it |
|---|---|
| `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules`, `.github/copilot-instructions.md`, `GEMINI.md` | present or absent; bytes and lines; how many lines both forbid something and name a path. A directory entry such as `.cursor/rules` fans out over the files in it, up to 64 of them and until this step's line budget is spent, and the row says how many were read when either bound bit |
| `.claude/settings.json`, `.claude/settings.local.json` | per file: whether a `PreToolUse` or `PostToolUse` hook exists, its matchers, and whether any of them matches a write tool — an omitted matcher and `*` match every tool, a matcher of only letters, digits, `_`, `-`, spaces, `,` and `\|` is an exact list, and anything else is an unanchored regular expression — one this tool cannot evaluate is reported as unchecked, not as matching nothing. Both are repository-local; the second is read from disk as well as from the listing, and the report says *present on disk, not checked in*, because Claude Code gitignores it |
| `.mcp.json`, `claude_desktop_config.json`, `.claude/mcp.json` | each server, its command line, and whether the command it runs is one of three known screens (`egresswall`, `mcp-gateway`, `mcp-scan`), read off the executable name rather than a substring of the line — and only when that name is bare or an absolute path, because an npm scope is where a package's identity lives. The first 64 servers get a row each; past that one row says how many there were. These are read from disk as well as from the listing, for the reason above |
| `.pre-commit-config.yaml`, git hooks | how many hook ids the framework file declares; which git hooks are installed — present, not a sample, and executable, because git ignores a hook without the execute bit and makes the commit anyway, so the ones without it get a row of their own — in the directory `git rev-parse --git-path hooks` names, so `core.hooksPath` and a linked worktree are not read as an empty one — and when that directory is outside the repository, a finding says so and it is not read |
| `CODEOWNERS` | how many patterns name an owner, how many name none and so require no reviewer, and — when the file holds more than 2000 distinct owned patterns — how many of them the ranking tested |
| `.github/workflows/*.yml`, `*.yaml` | per workflow: whether a test runner is named in one of its `run:` steps — a step `name:`, an `if:` guard, an `env:` value and a job id are not commands — and whether it runs on pull requests. The first 32 in sorted order are read, and fewer when this step's line budget is spent first; one row then says how many were read and how many were listed and not read, and no later row says a scanner is absent |
| gitleaks / trufflehog / detect-secrets / ggshield / git-secrets | whether any is named outside a comment in CI, pre-commit, or a config of its own; whether it runs is not checked |
| lockfiles, test layout | which lockfiles are committed; how many files sit in a test path |
| any of the above that is present and cannot be read | one row saying *present, not read* and why — over 1 MiB, a NUL byte in the first 8 KiB, or the file would not open. No row then states what that file does or does not configure |

Every row is a fact plus one sentence naming what an agent can do because of it. Every row
that cites a file carries its `file:line`; a row that states an absence carries `-`, because
what establishes an absence is the listing and not a line of a file.

## The invariant candidates

Candidates come from three places, exactly as the in-person method does:

- **path heuristics** — the seven places a junior would be stopped: the schema and query
  layer, authentication and session handling, money, deployment and infrastructure, secret
  material, generated and vendored files, and the dependency lockfiles;
- **git history** — the paths that repair commits (`fix`, `revert`, `hotfix`, `regression`,
  `bugfix`) touched, over the last 2000 non-merge commits, weighted double when the same
  commit also touched a test named for a regression;
- **`CODEOWNERS`** — the paths that already require a named human.

They are ranked on evidence, not elegance: score = repair commits that touched these paths,
+ 2 if `CODEOWNERS` names one of them, + 1 if the path heuristic matched at all. One repair
commit is worth one point however many files it touched. A candidate at score 1 is a bare
path match — the heuristic matched and nothing else did — and the report says so, in those
words, rather than presenting it as evidence; among equal scores the order is the number of
matching files, then the name. The report labels them *candidates — a human confirms or
replaces them*, and when fewer than three categories match anything it says so and does not
invent a third.

Each one comes with the hook that would enforce it, in Claude Code's documented
`settings.json` shape (verified against <https://code.claude.com/docs/en/hooks> on
2026-08-31; the fetched page is `docs/evidence/claude-code-hooks.txt`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-db.py"
          }
        ]
      }
    ]
  }
}
```

and the script it points at, emitted into `--emit-dir`, which exits 2 to block the call:

<!-- pinned: demo/OUTPUT.txt -->
```console
$ echo '{"cwd":"/repo","tool_name":"Write","tool_input":{"file_path":"/repo/db/queries.py"}}' | drafts/hooks/protect-db.py
BLOCKED: db/queries.py is under db, which a human decides. Ask, do not edit.
exit status: 2
```

The emitted hook is executed by the test suite against a blocked path, an allowed path and a
non-write tool, so it is a script that has run before it reaches anyone's screen.

## What it composes

- **`agent-plan-lint`** — if any checked-in `.json` file carries both `policy_id` and
  `allowed_write_globs`, or both `mission_id` and `tasks`, it is loaded and validated and the
  issues go in §2. If none does, a **starter policy** is drafted instead: a valid
  `agent-plan-lint` policy whose write globs are the most-churned directories repair commits
  touched, capped at 64 with §2 naming the count and the cut — or every top-level directory,
  when the history holds no repair commit to read — and whose exclusions are the §3 candidates. A test loads every policy this tool
  emits with `agent_plan_lint.load_policy`, so "valid" is checked, not claimed.
- **`egresswall`** — up to 5 checked-in JSON fixtures are screened with egresswall's default
  policy, and the report names the reason code and the path, never the value. If an MCP
  configuration exists, the same configuration is rewritten with `egresswall proxy` in front
  of each server it can wrap and written to `--emit-dir` as a **suggestion**. The servers it
  does not rewrite are counted and named in §2, with the reason for each: one that names a URL
  is reached over the network and a proxy in front of a command cannot screen it; one whose
  command line is not made of strings would need one invented; one that configures neither a
  command nor a URL has no command to wrap; and one already running a known screen would come
  back double-proxied. Nothing is applied.

## Observed on a real repository

A run over a read-only checkout of [`Alex-lop/Nemisis`](https://github.com/Alex-lop/Nemisis),
2026-08-31. Not re-run by CI — it needs that checkout — so the block below is pinned to
`docs/evidence/nemisis-run.txt`, which is the whole session. A doc-truth test re-runs that command
against that commit and diffs the whole transcript, so a stale one fails rather than shipping; it
skips where the checkout is absent, which is everywhere but the author's machine:

<!-- pinned: docs/evidence/nemisis-run.txt -->
```console
$ guardrail-checkup run assets/Nemisis --out gcnem/REPORT.md --emit-dir gcnem/drafts
guardrail-checkup: wrote gcnem/REPORT.md — 16 inventory finding(s), 3 invariant candidate(s), 7 draft(s) in gcnem/drafts
$ git -C assets/Nemisis status --porcelain | wc -l
0
```

That repository has no repair commits under any candidate path and no `CODEOWNERS`, so §3 of
that report says what it should: the candidates it names are bare path matches, and it says so
in the report rather than presenting them as evidence.

Two lines of §2 from that report, and they are the point of §2:

<!-- pinned: docs/evidence/nemisis-run.txt -->
```
| .github/workflows/ci.yml: a test runner is named in a run: step, runs on pull requests | `.github/workflows/ci.yml:23` | a test runner is named here and this workflow runs on pull requests; whether it ran, and on what, was not checked, because nothing here was executed |
| lockfiles: uv.lock | `uv.lock:1` | a test run resolves the same dependencies twice |
```

That repository has a lockfile, a linter and a test path — the three things a generic
readiness scorer most often reports as missing. §2 hands you the command that disproves each,
before you are in the room:

<!-- pinned: docs/evidence/nemisis-run.txt -->
```
| “Missing package manager lockfile” | `uv.lock` is committed | `wc -l uv.lock` |
```

## What it does not do

- It does not modify the repository it reads. `--out`, `--emit-dir` and each file it would
  emit are refused with exit 2 if any of them resolves inside it, symlinks followed; and so is
  any output path that is a hard link to a file that already exists — a second name for a file
  in the repository resolves to itself, so no path comparison can see it.
- It does not install, apply, or enable anything. There is no `--apply` and no `--fix`.
- It does not open a socket. There is no network client in the installed package; the one
  script that fetches anything, `scripts/refresh_evidence.py`, ships only in the sdist, is
  never imported by the package, and is run by hand.
- It does not call a model. There is no provider, no API key, and no prompt in the package.
- It does not run the tools it names in §2. It starts no `npx` and no agent CLI.
- It does not execute anything from the repository it reads. The only subprocess it starts is
  `git`, and only `ls-files`, `rev-parse` and `log`.
- It does not give the repository a readiness score, a grade, or a percentage. A number over
  a judgement launders it. The per-candidate number in §3 is the evidence tally that section
  defines — repair commits, `CODEOWNERS`, path heuristic — not a rating of anything.
- It does not read every file. It reads the named guardrail artifacts, `pyproject.toml`,
  `setup.cfg` and `package.json` (for the linter falsifier), every checked-in `.json` the
  signature scan reaches before its 64 MiB and 10000 file budgets are spent, and the fixture sample —
  up to 1 MiB each, skipping anything with a NUL byte in its first 8 KiB. §1 accounts for
  each one —
  the JSON document lists them file by file as `scope.read` — and nothing this tool opens is
  missing. A named file it could not read is reported as present and not read, and no
  row then answers a question about it; when either budget is spent, §2 says how many `.json`
  files were listed and not read rather than reporting that no policy exists.
- It does not know your architecture. §3 is a ranked list of places, and the report says so.
- It does not check what a hook that exists actually does. A `PreToolUse` entry that only
  appends to a log reads exactly like one that blocks: presence is checked, behaviour is not,
  and §5 of every report says it.
- It does not follow a symlink out of the repository. One is reported as a finding, and the
  file it points at is not read.
- It does not run on a repository's terms. Its own `.git/config` is overridden on every git
  command line, because `core.fsmonitor` there would otherwise run a program from the
  checkout. `core.hooksPath` is overridden too, on every call but the two `rev-parse` queries that ask
  where this checkout's hooks live and which git directory a linked worktree shares — that
  override is the answer to the first question, and `rev-parse` fires no hook. That answer is then contained: a hooks directory outside the
  repository, and outside the git directory a linked worktree shares with its main checkout,
  is reported and never listed.
- It has no config file and no plugin system. The command line is the configuration.

## Command line

```
guardrail-checkup run PATH --out REPORT.md [--emit-dir DIR] [--format md|json] [--max-files N]
guardrail-checkup --version
```

Exit status is `0` whenever the report was written, and `2` on a usage or IO error — a bad
path, a `--out` inside the repository, an unwritable directory. It is never `1`: this tool
reports, it does not gate. In a git repository the file list is `git ls-files` (tracked files
plus untracked files `.gitignore` does not exclude); anywhere else it is a directory walk that
skips 13 well-known directories and says in §1 that `.gitignore` was not applied. Past
`--max-files` (default 20000) the listing is truncated and §1 names the cap; the §2 inventory and
the signature scan still ask the whole listing, so a lockfile or a policy past the cap is never
reported as absent. §3's ranking is the one section whose conclusions read the capped listing, and
it says so in the report when the cap bit; §1's file count, byte total and language mix are the
capped slice too, and §1 names both totals.
The path is printed exactly as you type it — in the header line under the title, in §1 and in §6
— so `cd` into the repository and pass `.` when the report is going to someone else.

`--format json` writes the same facts as a JSON document for a dashboard: the scope, the
inventory, what the siblings found, the falsifiers, the ranked candidates and the Monday list.
It does not carry §3's per-candidate settings snippet, hook script or one-line test; those are
in the markdown. `python -m guardrail_checkup` is the same CLI, for when the console script is
not on PATH.

In Python:

```python
from guardrail_checkup import checkup

result, composed = checkup("/path/to/repo")
print(result.head, [item.slug for item in result.candidates])
```

## How it is tested

<!-- runnable -->
```console
$ python -m pytest --collect-only -q -o addopts='' | grep -c ::
483
```

Those tests run on CPython 3.11, 3.12 and 3.13, on Ubuntu and macOS, in the matrix in
`.github/workflows/ci.yml`; `scripts/check.sh` runs the same steps locally. They include the
demo compared byte for byte with `demo/OUTPUT.txt` and `demo/OUTPUT.md`, the emitted hook run
as a subprocess, the Python block above executed against the demo fixture, timings at the
`CODEOWNERS` bound, at a dense MCP configuration, at the rule-file and workflow caps in the
worst line shape each allows, at the signature scan's byte and file budgets, at a hundred
thousand files through the read recorder, at both history caps and over a whole run of
five thousand files, every emitted starter policy loaded by `agent_plan_lint.load_policy`
— including policies emitted over paths with backslashes, newlines and bidi marks in them —
and a doc-truth suite that fails when this README, `CHANGELOG.md`, `CONTRIBUTING.md`, the
comparison page or the package description, its keywords and its classifiers overclaim. That
suite reads each digit *in its sentence*, against the value in the code, so swapping one
whitelisted figure for another fails, and a digit it does not bind that way is declared prose
with its reason; it holds a named list of absolute claims bound one-to-one to the tests
that would fail first; it fails on any `every`/`all` sentence in any of those documents that is
not on that list; it holds the length of each capability list, each row of the *What it looks
at* table, each *What it does not do* bullet, each *The six sections*, *The invariant
candidates* and *What it composes* item, each `Added` and `Pre-release scaffolding` bullet of
`CHANGELOG.md`, each of `CONTRIBUTING.md`'s three rules — all of them whole, not by their
opening — the lead of each recorded decision and a closed list of behavioural sentences, so an
invented capability and a reversed one both fail on a list rather than on the prose; it fails
on a `--flag` that is neither in this package's parser nor on the declared non-feature list; it
binds each row of the comparison table, adoption cell and licence included, to the fetched
metadata, each comparative sentence about an incumbent to the phrase in the fetched source that
supports it, and that page's fetched-on date to the stamp inside the evidence files; and it
binds every quotation to a file under `docs/evidence/`. It also replays 101 injected falsehoods
and fails if any of them would have shipped. `CONTRIBUTING.md` says what it still does not
catch.

## Comparison

`docs/comparison.md` puts this next to Claude Code's `/doctor`, `kenryu42/cc-safety-net` and
`microsoft/agentrc`, with dated evidence for every figure, each figure checked against the row
it sits in. The short version: `/doctor` diagnoses the installation and `cc-safety-net` blocks a
generic list of destructive commands before a tool call runs; neither reads your repository's
own history to say which of *your* paths is worth a hook. `microsoft/agentrc` is not
characterised, here or there: the only source checked in for it is its repository metadata, and
that says what it is for rather than what it emits. Install the first two anyway.

## License

Apache-2.0. Built on [`agent-plan-lint`](https://github.com/Alex-lop/agent-plan-lint) and
[`egresswall`](https://github.com/Alex-lop/egresswall), and on the plan gate and egress
firewall they were extracted from. Written with AI assistance; see `CONTRIBUTING.md`.
