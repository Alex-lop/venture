# Agent guardrail checkup — Graft

Run 2026-08-21 · read-only · `Graft` · HEAD `65a76e5edd40`
Produced by `guardrail-checkup`, a deterministic offline reader. No model was called for anything below; every judgement in §3 is yours to make.

## 1. Scope

- **Repository:** `Graft`, as given on the command line
- **HEAD:** `65a76e5edd4098e0c7f4749d1e87f15ed741d069`
- **Size:** 255 file(s) considered, 43,657,873 bytes (apparent size)
- **File list:** `git ls-files` — tracked files plus untracked files `.gitignore` does not exclude
- **Language mix** (by file extension), the 10 most common of 16:
  - `.ts` — 199
  - `.scm` — 13
  - `.yml` — 8
  - `.json` — 6
  - `.md` — 6
  - `.gif` — 5
  - `.mjs` — 5
  - `.png` — 4
  - `.cjs` — 2
  - `(no extension)` — 1
- **Read:** the named guardrail artifacts listed in §2, `pyproject.toml`, `setup.cfg`, `package.json` (for the linter falsifier), every checked-in `.json` file the signature scan reached before its 64 MiB and 10,000 file budgets were spent, and up to 0 JSON fixture(s) screened in §2. A file over 1 MiB, or one whose first 8 KiB contains a NUL byte, is listed and not read.
- **Not read:** everything else. No source file was interpreted, no test was run, no command from this repository was executed, and nothing was sent anywhere.

## 2. Tool results — and what they got wrong

### Guardrail inventory — what exists, and what an agent can do because of it

| Fact | Where | What an agent can do |
| --- | --- | --- |
| CLAUDE.md: absent | `-` | nothing written down here for an agent to follow, so every rule is folklore |
| AGENTS.md: absent | `-` | nothing written down here for an agent to follow, so every rule is folklore |
| .cursorrules: absent | `-` | nothing written down here for an agent to follow, so every rule is folklore |
| .cursor/rules: absent | `-` | nothing written down here for an agent to follow, so every rule is folklore |
| .github/copilot-instructions.md: absent | `-` | nothing written down here for an agent to follow, so every rule is folklore |
| GEMINI.md: absent | `-` | nothing written down here for an agent to follow, so every rule is folklore |
| .claude/settings.json: no PreToolUse hook | `.claude/settings.json:13` | a tool call of this kind runs with nothing in front of it that this repository checks in |
| .claude/settings.json: 2 PostToolUse entries, matcher(s) 'Write\|Edit\|MultiEdit', 'Bash\|mcp\_\_graft\_\_' | `.claude/settings.json:14` | a write to any path is inspected by a hook this repository checks in; whether this hook blocks is not checked, because nothing here was executed |
| .claude/settings.local.json: absent | `-` | no PreToolUse or PostToolUse hook is configured here; this tool reads the two settings files in the checkout and nothing on the machine outside it |
| no MCP server configuration found (.mcp.json, claude_desktop_config.json, .claude/mcp.json) | `-` | no tool servers are configured in this repository, so none can be screened here |
| .pre-commit-config.yaml: absent | `-` | no commit-time check runs on a contributor's machine |
| .git/hooks: no installed hook (samples only) | `.git/hooks:1` | nothing is checked at commit time |
| CODEOWNERS: absent | `-` | no path in this repository names a required reviewer; branch protection on the host was not read |
| .github/workflows/blast-cache.yml: no test runner in a run: step, does not run on pull requests | `.github/workflows/blast-cache.yml:5` | a change can reach review without this workflow having judged it |
| .github/workflows/blast-pages.yml: no test runner in a run: step, runs on pull requests | `.github/workflows/blast-pages.yml:7` | a change can reach review without this workflow having judged it |
| .github/workflows/blast.yml: no test runner in a run: step, runs on pull requests | `.github/workflows/blast.yml:3` | a change can reach review without this workflow having judged it |
| .github/workflows/ci.yml: a test runner is named in a run: step, runs on pull requests | `.github/workflows/ci.yml:43` | a test runner is named here and this workflow runs on pull requests; whether it ran, and on what, was not checked, because nothing here was executed |
| .github/workflows/codeql.yml: no test runner in a run: step, runs on pull requests | `.github/workflows/codeql.yml:3` | a change can reach review without this workflow having judged it |
| .github/workflows/scorecard.yml: no test runner in a run: step, does not run on pull requests | `.github/workflows/scorecard.yml:2` | a change can reach review without this workflow having judged it |
| secret scanning: not configured (no gitleaks, trufflehog or detect-secrets) | `-` | a credential an agent pastes into a file is committed with everything else |
| lockfiles: package-lock.json | `package-lock.json:1` | a test run resolves the same dependencies twice |
| tests: 90 file(s) in a test path | `test/ask-fusion.test.ts:1` | there is a suite a hook or a CI gate can call |

### agent-plan-lint

- No document in agent-plan-lint's schema was found (no `.json` file carries both `policy_id` and `allowed_write_globs`, or both `mission_id` and `tasks`).
- A starter policy was drafted instead; see §4. It was **not** written into your repository.

### egresswall

- No checked-in JSON fixture was found to screen.

### What a generic scorer will get wrong here

**guardrail-checkup did not run any of these tools.** It contacts no network and starts no `npx`. This is the falsifier list to have ready when you do run them, built from this repository's own files:

| A generic readiness scorer will say | True here | Command that shows it |
| --- | --- | --- |
| “Missing package manager lockfile” | `package-lock.json` is committed | `wc -l package-lock.json` |
| “Testing: 0/0 (0%)” | 90 file(s) sit in a test path | `git ls-files --cached --others --exclude-standard \| grep -cE '(^\|/)(tests?\|spec)/\|(^\|/)test_[^/]+$\|_test\.[a-z]+$\|\.(test\|spec)\.[jt]sx?$'` |

## 3. Invariant candidates

**Candidates — a human confirms or replaces them.** They are ranked by evidence, not by judgement: score = repair commits in the history that touched these paths (a commit that also touched a regression test counts twice) + 2 if CODEOWNERS names one of them + 1 if the path heuristic matched at all. This tool does not know your architecture and does not claim to.

1 of these is a bare path match at score 1: the path heuristic matched and nothing else did — no repair commit and no CODEOWNERS entry points at them. Equal scores are ordered by the number of matching files, then by name; that ordering is not evidence.

### Invariant candidate 1 — An agent does not write to the dependency lockfiles without a human deciding first.

- **Governs:** `package-lock.json`
- **Evidence (score 5):**
  - path heuristic: 1 file(s) matching package-lock.json
  - git history: 4 repair commit(s) touched these paths — 9c4a2e0 fix: put the tokens-saved line on top of tool output; 7d74ecd Retrieval + steering fixes: staleness, test de-rank, known-target/refactor guidance, callers --depth all; cdec18e feat(ask): graph-rank + IDF + body indexing, and fix silent 32KB parse drop
- **An agent breaks it by:** reading two files nearby, inferring the pattern, and writing the change here rather than asking — which is the correct move everywhere else in this repository.
- **Hook** — `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-lockfiles.py"
          }
        ]
      }
    ]
  }
}
```

  and `.claude/hooks/protect-lockfiles.py` (emitted; exit 2 blocks the call):

```python
#!/usr/bin/env python3
"""Block an agent write under a protected path. Drafted by guardrail-checkup; a human confirms it."""
import json, os, sys

PROTECTED = ('package-lock.json',)
event = json.load(sys.stdin)
if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)
target = event.get("tool_input", {}).get("file_path", "")
path = os.path.relpath(target, event.get("cwd", ".")) if target else ""
if path.startswith(PROTECTED):
    print(f"BLOCKED: {path} is under lockfiles, which a human decides. Ask, do not edit.", file=sys.stderr)
    sys.exit(2)
```

- **Test** (exits non-zero when a staged commit violates it): `! git diff --cached --name-only | grep -qE '^(package\-lock\.json)'`

### Invariant candidate 2 — An agent does not write to deployment and infrastructure without a human deciding first.

- **Governs:** `.github/workflows/` — for example `.github/workflows/blast-cache.yml`, `.github/workflows/blast-pages.yml`, `.github/workflows/blast.yml`, `.github/workflows/ci.yml`
- **Evidence (score 3):**
  - path heuristic: 6 file(s) matching .github/workflows/
  - git history: 2 repair commit(s) touched these paths — 73f81e5 fix(blast): rank the hub symbol, and name the areas on the published page (#171); c84515b fix(ci): correct pinned SHAs for scorecard-action and codeql-action
- **An agent breaks it by:** reading two files nearby, inferring the pattern, and writing the change here rather than asking — which is the correct move everywhere else in this repository.
- **Hook** — `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-deploy.py"
          }
        ]
      }
    ]
  }
}
```

  and `.claude/hooks/protect-deploy.py` (emitted; exit 2 blocks the call):

```python
#!/usr/bin/env python3
"""Block an agent write under a protected path. Drafted by guardrail-checkup; a human confirms it."""
import json, os, sys

PROTECTED = ('.github/workflows/',)
event = json.load(sys.stdin)
if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)
target = event.get("tool_input", {}).get("file_path", "")
path = os.path.relpath(target, event.get("cwd", ".")) if target else ""
if path.startswith(PROTECTED):
    print(f"BLOCKED: {path} is under deploy, which a human decides. Ask, do not edit.", file=sys.stderr)
    sys.exit(2)
```

- **Test** (exits non-zero when a staged commit violates it): `! git diff --cached --name-only | grep -qE '^(\.github/workflows/)'`

### Invariant candidate 3 — An agent does not write to secret material without a human deciding first.

- **Governs:** `.env.example`
- **Evidence (score 1):**
  - path heuristic: 1 file(s) matching .env.example
- **An agent breaks it by:** reading two files nearby, inferring the pattern, and writing the change here rather than asking — which is the correct move everywhere else in this repository.
- **Hook** — `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-secrets.py"
          }
        ]
      }
    ]
  }
}
```

  and `.claude/hooks/protect-secrets.py` (emitted; exit 2 blocks the call):

```python
#!/usr/bin/env python3
"""Block an agent write under a protected path. Drafted by guardrail-checkup; a human confirms it."""
import json, os, sys

PROTECTED = ('.env.example',)
event = json.load(sys.stdin)
if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)
target = event.get("tool_input", {}).get("file_path", "")
path = os.path.relpath(target, event.get("cwd", ".")) if target else ""
if path.startswith(PROTECTED):
    print(f"BLOCKED: {path} is under secrets, which a human decides. Ask, do not edit.", file=sys.stderr)
    sys.exit(2)
```

- **Test** (exits non-zero when a staged commit violates it): `! git diff --cached --name-only | grep -qE '^(\.env\.example)'`

## 4. Monday list

1. Read invariant candidate 1 (lockfiles) in §3 and decide whether it is right. If it is, copy `DIR/hooks/protect-lockfiles.py` into `.claude/hooks/`, `chmod +x` it, and merge `DIR/hooks/settings-lockfiles.json` into `.claude/settings.json`. Re-run with `--emit-dir DIR` to write it; this run wrote no draft.
2. Add the §3 `PreToolUse` block to `.claude/settings.json`; the only hook this repository checks in is a `PostToolUse` one, and it runs after the write.
3. Review `DIR/starter-policy.json` — a valid agent-plan-lint policy whose exclusions are the §3 candidates. Fix the write globs to the paths your agents really own, then run `agent-plan-lint check <plan.json> --policy starter-policy.json`. Re-run with `--emit-dir DIR` to write it; this run wrote no draft.
4. Add gitleaks or detect-secrets to CI or to `.pre-commit-config.yaml`. §5 explains why this tool cannot do it for you.

## 5. What this did not cover

- **Branch protection and required reviews.** They live on the host, not in the checkout; this tool never asked one.
- **Production systems.** No credential, no VPN, no CI, no deploy, no live database was touched.
- **Secrets already in history.** This reads the working tree, not every blob. Run `gitleaks detect`, `trufflehog git`, or `detect-secrets scan` for that.
- **Runtime behaviour.** Nothing here was executed. A hook that has never run does not go on anyone's screen — run the emitted one before you trust it.
- **Anything needing a model.** No model was called. §3 is a ranked list of places, not a reading of your architecture, and the judgement — whether these are the right places — is not in this file.
- **Hooks configured outside this checkout.** The inventory reads `.claude/settings.json` and `.claude/settings.local.json`. A hook in `~/.claude/settings.json`, in an enterprise policy, or in an installed plugin is on the machine and not in this repository, and was not read.
- **Whether the rules that exist are followed.** Presence is checked; compliance is not. A hook is reported by its matcher, not by what it does: nothing here was executed, so a `PreToolUse` entry that only writes a log line reads exactly like one that blocks.
- **What the three tools next to this one do.** None of them ran here, and this replaces none of them. Claude Code's `/doctor` “prints read-only installation diagnostics without starting a session”. `kenryu42/cc-safety-net` “blocks destructive Git and file system commands, plus common attempts to access sensitive files, before a tool call runs”. `microsoft/agentrc` says only “Get your repo ready for AI.” — its own description, and this report characterises it no further. The first two are better at those jobs than anything here; install them. This one reports, and the report is what you read before deciding what to enforce.

## 6. Provenance

- **Tool:** `guardrail-checkup` 0.1.0
- **Command:** `guardrail-checkup run Graft --out dogfood/Graft.md`
- **Repository commit:** `65a76e5edd4098e0c7f4749d1e87f15ed741d069`
- **Repair commits examined:** 69, from the last 2000 non-merge commits
- **What left this machine: nothing.** This tool opens no socket and makes no model call. The git subcommands it runs are `ls-files`, `rev-parse` and `log`, all read-only. It wrote no file inside the repository it read.
- **Built on:** `agent-plan-lint` 0.1.0 (policy and plan validation), `egresswall` 0.1.0 (fixture screening, MCP proxy suggestion).
- **Lineage:** the plan gate comes from Graphene's admission validator and the screen from RegLineage's egress firewall, both the author's own prior work, extracted and re-tested as packages.
- **AI assistance:** this tool was written with AI assistance. **This report was not** — it is deterministic output from the files listed in §1, and re-running the command above on the same commit produces it again byte for byte.
- **No guarantee** is made about anything not listed in §1. The third-party tools named in §2 and §5 are unaffiliated with this one.
