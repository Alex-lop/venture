# guardrail-checkup

**Run it on your own repository and get back the report a consultant would hand you after an
hour: what your agents are actually stopped from doing today, which claims a generic scorer
will get wrong about *this* repository, and three ranked places a hook would pay for itself.**

```
pip install guardrail-checkup
```

Deterministic, offline, read-only. It opens no socket, calls no model, runs nothing from the
repository it reads, and writes nothing inside it — every draft goes to a directory you name.
*Status: 0.1.0. From source: `uv pip install git+https://github.com/Alex-lop/guardrail-checkup`.*

The judgement stays with you. This tool ranks candidates by evidence and says so in the
report; it does not tell you what your architecture means. Deterministic means what it says:
the same commit produces the same bytes, so two reports can be diffed.

## 60 seconds

<!-- pinned: demo/OUTPUT.txt -->
```console
$ guardrail-checkup run shipfast --out REPORT.md --emit-dir drafts
guardrail-checkup: wrote REPORT.md — 16 inventory finding(s), 2 invariant candidate(s), 6 draft(s) in drafts
```

`demo/demo.sh` builds a throwaway repository from `demo/fixture` (a service with a `db/`
directory, a migration, an `.mcp.json`, no hooks, and a `CLAUDE.md` that forbids nothing),
gives it a history with two repairs, and runs the checkup over it. `demo/OUTPUT.md` is the
report it produced; `demo/OUTPUT.txt` is the whole transcript. Both are compared byte for byte
in CI.

## The six sections

The report has the same six sections, in the same order, as the in-person session this
package replaces — so the two are interchangeable as a deliverable:

1. **Scope** — the path, HEAD, size, language mix by file extension, and exactly what was and
   was not read.
2. **Tool results — and what they got wrong** — the guardrail inventory (every fact with the
   `file:line` it came from and one line of *what an agent can do because of this*), what
   `agent-plan-lint` and `egresswall` found, and the falsifier list for the generic scorers.
3. **The three invariants** — ranked candidates, each with the paths it governs, the evidence,
   a `PreToolUse` hook that blocks writes there, and a one-line test.
4. **Monday list** — at most five actions, each naming a file this tool emitted or a file to edit.
5. **What this did not cover** — branch protection, production, secrets in history, runtime,
   anything needing a model.
6. **Provenance** — versions, the exact command, what left the machine (nothing), and the
   AI-assistance disclosure.

## What it looks at

| Artifact | What the report says about it |
|---|---|
| `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules`, `.github/copilot-instructions.md`, `GEMINI.md` | present or absent; bytes and lines; how many lines both forbid something and name a path |
| `.claude/settings.json` | whether a `PreToolUse` or `PostToolUse` hook exists, its matchers, and whether any of them matches a write tool |
| `.mcp.json`, `claude_desktop_config.json`, `.claude/mcp.json` | every server, its command line, and whether anything in that command line screens what the server returns |
| `.pre-commit-config.yaml`, `.git/hooks` | the framework's hook ids; which git hooks are actually installed rather than samples |
| `CODEOWNERS` | how many patterns require a named reviewer |
| `.github/workflows/*.yml` | per workflow: whether a test runner appears in it, and whether it runs on pull requests |
| gitleaks / trufflehog / detect-secrets / ggshield / git-secrets | whether any is referenced in CI, pre-commit, or a config of its own |
| lockfiles, test layout | which lockfiles are committed; how many files sit in a test path |

Every row is a fact plus the `file:line` it came from plus one sentence naming what an agent
can do because of it.

## The three invariant candidates

Candidates come from three places, exactly as the in-person method does:

- **path heuristics** — the seven places a junior would be stopped: the schema and query
  layer, authentication and session handling, money, deployment and infrastructure, secret
  material, generated and vendored files, and the dependency lockfiles;
- **git history** — the paths that repair commits (`fix`, `revert`, `hotfix`, `regression`,
  `bugfix`) touched, over the last 2000 non-merge commits, weighted double when the same
  commit also touched a test named for a regression;
- **`CODEOWNERS`** — the paths that already require a named human.

They are ranked on evidence, not elegance: score = repair commits that touched these paths,
+ 2 if `CODEOWNERS` names one of them, + 1 if the path heuristic matched at all. The report
labels them *candidates — a human confirms or replaces them*, and when fewer than three have
evidence it says so and does not invent a third.

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
  `agent-plan-lint` policy whose write globs are the directories repair commits actually
  touched and whose exclusions are the §3 candidates. A test loads every policy this tool
  emits with `agent_plan_lint.load_policy`, so "valid" is checked, not claimed.
- **`egresswall`** — up to 5 checked-in JSON fixtures are screened with egresswall's default
  policy, and the report names the reason code and the path, never the value. If an MCP
  configuration exists, the same configuration is rewritten with `egresswall proxy` in front
  of every server and written to `--emit-dir` as a **suggestion**. Nothing is applied.

## Observed on a real repository

A run over a read-only checkout of [`Alex-lop/Nemisis`](https://github.com/Alex-lop/Nemisis),
2026-08-31. Not re-run by CI — it needs that checkout — so the block below is pinned to
`docs/evidence/nemisis-run.txt`, which is the whole session, and a doc-truth test fails if
the two ever disagree:

<!-- pinned: docs/evidence/nemisis-run.txt -->
```console
$ guardrail-checkup run assets/Nemisis --out REPORT.md --emit-dir drafts
guardrail-checkup: wrote REPORT.md — 15 inventory finding(s), 3 invariant candidate(s), 7 draft(s) in drafts
$ git -C assets/Nemisis status --porcelain | wc -l
0
```

Two lines of §2 from that report, and they are the point of §2:

<!-- pinned: docs/evidence/nemisis-run.txt -->
```
| .github/workflows/ci.yml: tests run, runs on pull requests | `.github/workflows/ci.yml:23` | a change is tested before review |
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

- It does not modify the repository it reads. `--out` and `--emit-dir` are refused with exit 2
  if either resolves inside it.
- It does not install, apply, or enable anything. There is no `--apply` and no `--fix`.
- It does not open a socket. There is no network client in the package.
- It does not call a model. There is no provider, no API key, and no prompt in the package.
- It does not run the tools it names in §2. It starts no `npx` and no agent CLI.
- It does not execute anything from the repository it reads. The only subprocess it starts is
  `git`, and only `ls-files`, `rev-parse` and `log`.
- It does not score, grade, or give a percentage. A number over a judgement launders it.
- It does not read every file. It reads the named guardrail artifacts, every checked-in
  `.json` (for the signature keys), and the fixture sample — up to 1 MiB each, skipping
  anything with a NUL byte in its first 8 KiB. §1 says which.
- It does not know your architecture. §3 is a ranked list of places, and the report says so.
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
`--max-files` (default 20000) the listing is truncated and §1 names the cap.

`--format json` writes the same report as a JSON document for a dashboard. `python -m
guardrail_checkup` is the same CLI, for when the console script is not on PATH.

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
128
```

Those tests run on CPython 3.11, 3.12 and 3.13, on Ubuntu and macOS, in the matrix in
`.github/workflows/ci.yml`; `scripts/check.sh` runs the same steps locally. They include the
demo compared byte for byte with `demo/OUTPUT.txt` and `demo/OUTPUT.md`, the emitted hook run
as a subprocess, every emitted starter policy loaded by `agent_plan_lint.load_policy`, and a
doc-truth suite that fails when this README overclaims: every number and number-word in it is
bound to a value the code decides or declared as prose with a reason, a named list of absolute
claims is bound one-to-one to the tests that would fail first, and every quotation is bound to
a file under `docs/evidence/`. `CONTRIBUTING.md` says what that suite still cannot see.

## Comparison

`docs/comparison.md` puts this next to Claude Code's `/doctor`, `kenryu42/cc-safety-net` and
`microsoft/agentrc`, with dated evidence for every figure. The short version: all three
enforce or score, none of them reports, and you should install the first two anyway.

## License

Apache-2.0. Built on [`agent-plan-lint`](https://github.com/Alex-lop/agent-plan-lint) and
[`egresswall`](https://github.com/Alex-lop/egresswall), and on the plan gate and egress
firewall they were extracted from. Written with AI assistance; see `CONTRIBUTING.md`.
