# Agent guardrail checkup — Graphene

Run 2026-09-02 · read-only · `assets/Graphene` · HEAD `30c9271a4daa`
Produced by `guardrail-checkup`, a deterministic offline reader. No model was called for anything below; every judgement in §3 is yours to make.

## 1. Scope

- **Repository:** `assets/Graphene`, as given on the command line
- **HEAD:** `30c9271a4daa917de8015a5665b9bc26d7f1a201`
- **Size:** 545 file(s) considered, 8,852,293 bytes (apparent size)
- **File list:** `git ls-files` — tracked files plus untracked files `.gitignore` does not exclude
- **Language mix** (by file extension), the 10 most common of 28:
  - `.py` — 275
  - `.json` — 73
  - `.txt` — 70
  - `.md` — 58
  - `.ndjson` — 15
  - `.mjs` — 12
  - `.sh` — 6
  - `.png` — 5
  - `(no extension)` — 3
  - `.css` — 3
- **Read:** the named guardrail artifacts listed in §2, `pyproject.toml`, `setup.cfg`, `package.json` (for the linter falsifier), every checked-in `.json` file the signature scan reached before its 64 MiB and 10,000 file budgets were spent, and up to 4 JSON fixture(s) screened in §2. A file over 1 MiB, or one whose first 8 KiB contains a NUL byte, is listed and not read.
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
| .claude/settings.json: absent | `-` | no PreToolUse or PostToolUse hook is configured here; this tool reads the two settings files in the checkout and nothing on the machine outside it |
| .claude/settings.local.json: absent | `-` | no PreToolUse or PostToolUse hook is configured here; this tool reads the two settings files in the checkout and nothing on the machine outside it |
| .mcp.json: MCP server 'graphene' runs `uv run --frozen graphene-mcp`; no screen in the command line | `.mcp.json:3` | whatever this server returns reaches the agent's context unscreened |
| .pre-commit-config.yaml: absent | `-` | no commit-time check runs on a contributor's machine |
| .git/hooks: no installed hook (samples only) | `.git/hooks:1` | nothing is checked at commit time |
| CODEOWNERS: absent | `-` | no path in this repository names a required reviewer; branch protection on the host was not read |
| .github/workflows/ci.yml: a test runner is named in a run: step, runs on pull requests | `.github/workflows/ci.yml:47` | a test runner is named here and this workflow runs on pull requests; whether it ran, and on what, was not checked, because nothing here was executed |
| secret scanning: not configured (no gitleaks, trufflehog or detect-secrets) | `-` | a credential an agent pastes into a file is committed with everything else |
| lockfiles: uv.lock | `uv.lock:1` | a test run resolves the same dependencies twice |
| tests: 148 file(s) in a test path | `demo/fixture/tests/test_rate_limit.py:1` | there is a suite a hook or a CI gate can call |

### agent-plan-lint

- `demo/north_star/policy.template.json` — refused: policy is invalid: policy\_id: String should match pattern '^\[A-Za-z0-9\]\[A-Za-z0-9.\_:-\]{0,127}$'
- `backend/graphene/orchestration/static/mission-replay.json` — refused: plan is invalid: mission\_id: Field required
- `evidence/north_star/2026-08-23-mission1/mission_start_5291caad50a8ee7a222a9221.graphene-capsule/plan/revision-1.json` — refused: plan is invalid: revision: Field required
- `evidence/north_star/2026-08-23-mission1/plan_show.json` — refused: plan is invalid: revision: Field required
- `evidence/north_star/2026-08-23-mission1/status_final.json` — refused: plan is invalid: mission\_id: Field required
- `evidence/north_star/2026-08-23-mission4-failure-lab/mission_start_38129f17add65609de1c3388.graphene-capsule/plan/revision-1.json` — refused: plan is invalid: revision: Field required
- `evidence/north_star/2026-08-23-mission4-failure-lab/status_final.json` — refused: plan is invalid: mission\_id: Field required
- `evidence/north_star/2026-08-23-trigger-demo/plan_show.json` — refused: plan is invalid: revision: Field required
- `evidence/north_star/2026-08-23-trigger-demo/status_final.json` — refused: plan is invalid: mission\_id: Field required

### egresswall

- `demo/north_star/goal.json` — clean under egresswall's default policy
- `demo/north_star/policy.template.json` — clean under egresswall's default policy
- `demo/taskmaster/scenario.json` — clean under egresswall's default policy
- `tests/fixtures/viewer_replay_source.json` — **4 violation(s)** under egresswall's default policy:
  - `FORBIDDEN_KEY at response.runs.consumer.events[2].session_id: field name 'session_id' is forbidden by policy`
  - `FORBIDDEN_KEY at response.runs.consumer.events[3].session_id: field name 'session_id' is forbidden by policy`
  - `FORBIDDEN_KEY at response.runs.consumer.events[4].session_id: field name 'session_id' is forbidden by policy`
  - `FORBIDDEN_KEY at response.runs.consumer.events[5].session_id: field name 'session_id' is forbidden by policy`

A violation names a code and a path, never a value. These are checked-in fixtures; the same screen in front of a live MCP server is what stops the real answer.
- Your MCP configuration (`.mcp.json`) was rewritten as a **suggestion** with `egresswall proxy` in front of 1 of 1 server(s). It was not applied; see §4.

### What a generic scorer will get wrong here

**guardrail-checkup did not run any of these tools.** It contacts no network and starts no `npx`. This is the falsifier list to have ready when you do run them, built from this repository's own files:

| A generic readiness scorer will say | True here | Command that shows it |
| --- | --- | --- |
| “Missing package manager lockfile” | `uv.lock` is committed | `wc -l uv.lock` |
| “Missing linter configuration” | a linter is configured at `pyproject.toml:30` | `grep -n -iE 'ruff\|eslint\|biome\|flake8\|prettier' pyproject.toml` |
| “Testing: 0/0 (0%)” | 148 file(s) sit in a test path | `git ls-files --cached --others --exclude-standard \| grep -cE '(^\|/)(tests?\|spec)/\|(^\|/)test_[^/]+$\|_test\.[a-z]+$\|\.(test\|spec)\.[jt]sx?$'` |

## 3. Invariant candidates

**Candidates — a human confirms or replaces them.** They are ranked by evidence, not by judgement: score = repair commits in the history that touched these paths (a commit that also touched a regression test counts twice) + 2 if CODEOWNERS names one of them + 1 if the path heuristic matched at all. This tool does not know your architecture and does not claim to.

All 3 of these are a bare path match at score 1: the path heuristic matched and nothing else did — no repair commit and no CODEOWNERS entry points at them. Equal scores are ordered by the number of matching files, then by name; that ordering is not evidence.

### Invariant candidate 1 — An agent does not write to deployment and infrastructure without a human deciding first.

- **Governs:** `.github/workflows/`, `deploy/` — for example `.github/workflows/ci.yml`, `deploy/cloudrun/Dockerfile`, `deploy/cloudrun/README.md`, `deploy/cloudrun/cloudbuild.yaml`
- **Evidence (score 1):**
  - path heuristic: 6 file(s) matching .github/workflows/, deploy/
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

PROTECTED = ('.github/workflows/', 'deploy/')
event = json.load(sys.stdin)
if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)
target = event.get("tool_input", {}).get("file_path", "")
path = os.path.relpath(target, event.get("cwd", ".")) if target else ""
if path.startswith(PROTECTED):
    print(f"BLOCKED: {path} is under deploy, which a human decides. Ask, do not edit.", file=sys.stderr)
    sys.exit(2)
```

- **Test** (exits non-zero when a staged commit violates it): `! git diff --cached --name-only | grep -qE '^(\.github/workflows/|deploy/)'`

### Invariant candidate 2 — An agent does not write to generated and vendored files without a human deciding first.

- **Governs:** `backend/graphene/viewer/static/vendor/` — for example `backend/graphene/viewer/static/vendor/CYTOSCAPE_LICENSE.txt`, `backend/graphene/viewer/static/vendor/README.txt`, `backend/graphene/viewer/static/vendor/cytoscape.esm.min.mjs`
- **Evidence (score 1):**
  - path heuristic: 3 file(s) matching backend/graphene/viewer/static/vendor/
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
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-generated.py"
          }
        ]
      }
    ]
  }
}
```

  and `.claude/hooks/protect-generated.py` (emitted; exit 2 blocks the call):

```python
#!/usr/bin/env python3
"""Block an agent write under a protected path. Drafted by guardrail-checkup; a human confirms it."""
import json, os, sys

PROTECTED = ('backend/graphene/viewer/static/vendor/',)
event = json.load(sys.stdin)
if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)
target = event.get("tool_input", {}).get("file_path", "")
path = os.path.relpath(target, event.get("cwd", ".")) if target else ""
if path.startswith(PROTECTED):
    print(f"BLOCKED: {path} is under generated, which a human decides. Ask, do not edit.", file=sys.stderr)
    sys.exit(2)
```

- **Test** (exits non-zero when a staged commit violates it): `! git diff --cached --name-only | grep -qE '^(backend/graphene/viewer/static/vendor/)'`

### Invariant candidate 3 — An agent does not write to authentication and session handling without a human deciding first.

- **Governs:** `demo/fixture/app/auth/` — for example `demo/fixture/app/auth/__init__.py`, `demo/fixture/app/auth/limiter.py`
- **Evidence (score 1):**
  - path heuristic: 2 file(s) matching demo/fixture/app/auth/
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
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-auth.py"
          }
        ]
      }
    ]
  }
}
```

  and `.claude/hooks/protect-auth.py` (emitted; exit 2 blocks the call):

```python
#!/usr/bin/env python3
"""Block an agent write under a protected path. Drafted by guardrail-checkup; a human confirms it."""
import json, os, sys

PROTECTED = ('demo/fixture/app/auth/',)
event = json.load(sys.stdin)
if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)
target = event.get("tool_input", {}).get("file_path", "")
path = os.path.relpath(target, event.get("cwd", ".")) if target else ""
if path.startswith(PROTECTED):
    print(f"BLOCKED: {path} is under auth, which a human decides. Ask, do not edit.", file=sys.stderr)
    sys.exit(2)
```

- **Test** (exits non-zero when a staged commit violates it): `! git diff --cached --name-only | grep -qE '^(demo/fixture/app/auth/)'`

## 4. Monday list

1. Read invariant candidate 1 (deploy) in §3 and decide whether it is right. If it is, copy `DIR/hooks/protect-deploy.py` into `.claude/hooks/`, `chmod +x` it, and merge `DIR/hooks/settings-deploy.json` into `.claude/settings.json`. Re-run with `--emit-dir DIR` to write it; this run wrote no draft.
2. Create `.claude/settings.json` with the hooks block from §3. Neither settings file exists in this repository today, so every candidate in §3 has nowhere to live.
3. Compare `DIR/mcp-wrapped.json` with your own MCP configuration. It is the same servers with `egresswall proxy` in front of the 1 it could wrap; nothing was applied. Its `--policy` names `/etc/egresswall/policy.json`, a placeholder — point it at an egresswall policy you write, because this tool writes none. Re-run with `--emit-dir DIR` to write it; this run wrote no draft.
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
- **Command:** `guardrail-checkup run assets/Graphene --out ventures/guardrail-checkup/docs/evidence/graphene-report.md`
- **Repository commit:** `30c9271a4daa917de8015a5665b9bc26d7f1a201`
- **Repair commits examined:** 0, from the last 2000 non-merge commits
- **What left this machine: nothing.** This tool opens no socket and makes no model call. The git subcommands it runs are `ls-files`, `rev-parse` and `log`, all read-only. It wrote no file inside the repository it read.
- **Built on:** `agent-plan-lint` 0.1.0 (policy and plan validation), `egresswall` 0.1.0 (fixture screening, MCP proxy suggestion).
- **Lineage:** the plan gate comes from Graphene's admission validator and the screen from RegLineage's egress firewall, both the author's own prior work, extracted and re-tested as packages.
- **AI assistance:** this tool was written with AI assistance. **This report was not** — it is deterministic output from the files listed in §1, and re-running the command above on the same commit produces it again byte for byte.
- **No guarantee** is made about anything not listed in §1. The third-party tools named in §2 and §5 are unaffiliated with this one.
