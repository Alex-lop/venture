# Agent guardrail checkup — venture

Run 2026-09-02 · read-only · `venture` · HEAD `774a531278a2`
Produced by `guardrail-checkup`, a deterministic offline reader. No model was called for anything below; every judgement in §3 is yours to make.

## 1. Scope

- **Repository:** `venture`, as given on the command line
- **HEAD:** `774a531278a235498a09611990d199c2290f59bd`
- **Size:** 329 file(s) considered, 6,989,810 bytes (apparent size)
- **File list:** `git ls-files` — tracked files plus untracked files `.gitignore` does not exclude
- **Language mix** (by file extension), the 10 most common of 15:
  - `.json` — 113
  - `.md` — 86
  - `.py` — 63
  - `.txt` — 17
  - `.sh` — 10
  - `.csv` — 9
  - `.gitignore` — 6
  - `(no extension)` — 5
  - `.yml` — 4
  - `.lock` — 3
- **Read:** the named guardrail artifacts listed in §2, `pyproject.toml`, `setup.cfg`, `package.json` (for the linter falsifier), every checked-in `.json` file the signature scan reached before its 64 MiB and 10,000 file budgets were spent, and up to 5 JSON fixture(s) screened in §2. A file over 1 MiB, or one whose first 8 KiB contains a NUL byte, is listed and not read.
- **Not read:** everything else. No source file was interpreted, no test was run, no command from this repository was executed, and nothing was sent anywhere.

## 2. Tool results — and what they got wrong

### Guardrail inventory — what exists, and what an agent can do because of it

| Fact | Where | What an agent can do |
| --- | --- | --- |
| CLAUDE.md: 27,741 bytes, 256 lines, 18 line(s) forbid something and name a path | `CLAUDE.md:5` | prose an agent may follow; nothing here blocks a write, so it is guidance, not a guardrail |
| AGENTS.md: absent | `-` | nothing written down here for an agent to follow, so every rule is folklore |
| .cursorrules: absent | `-` | nothing written down here for an agent to follow, so every rule is folklore |
| .cursor/rules: absent | `-` | nothing written down here for an agent to follow, so every rule is folklore |
| .github/copilot-instructions.md: absent | `-` | nothing written down here for an agent to follow, so every rule is folklore |
| GEMINI.md: absent | `-` | nothing written down here for an agent to follow, so every rule is folklore |
| .claude/settings.json: absent | `-` | no PreToolUse or PostToolUse hook is configured here; this tool reads the two settings files in the checkout and nothing on the machine outside it |
| .claude/settings.local.json: absent | `-` | no PreToolUse or PostToolUse hook is configured here; this tool reads the two settings files in the checkout and nothing on the machine outside it |
| no MCP server configuration found (.mcp.json, claude_desktop_config.json, .claude/mcp.json) | `-` | no tool servers are configured in this repository, so none can be screened here |
| .pre-commit-config.yaml: absent | `-` | no commit-time check runs on a contributor's machine |
| .git/hooks: no installed hook (samples only) | `.git/hooks:1` | nothing is checked at commit time |
| CODEOWNERS: absent | `-` | no path in this repository names a required reviewer; branch protection on the host was not read |
| .github/workflows: absent | `-` | no GitHub Actions workflow is checked in here; CI configured elsewhere was not read |
| secret scanning: not configured (no gitleaks, trufflehog or detect-secrets) | `-` | a credential an agent pastes into a file is committed with everything else |
| lockfiles: ventures/egress-guard/uv.lock, ventures/guardrail-checkup/uv.lock, ventures/plan-lint/uv.lock | `ventures/egress-guard/uv.lock:1` | a test run resolves the same dependencies twice |
| tests: 31 file(s) in a test path | `ventures/egress-guard/tests/conftest.py:1` | there is a suite a hook or a CI gate can call |

### agent-plan-lint

- `ventures/plan-lint/demo/policy.json` — loads: a valid agent-plan-lint policy
- `ventures/plan-lint/demo/plan-bad.json` — 4 issue(s)
- `ventures/plan-lint/demo/plan-good.json` — within policy
  - `ventures/plan-lint/demo/plan-bad.json: criterion_model_assertion — a model assertion cannot verify a success criterion`
  - `ventures/plan-lint/demo/plan-bad.json: cycle — task dependency graph contains a cycle`
  - `ventures/plan-lint/demo/plan-bad.json: parallel_write_conflict — tasks work-api, work-models overlap write scope: app/api.py`
  - `ventures/plan-lint/demo/plan-bad.json: write_path_not_allowed — write path is forbidden: docs/guide.md`

### egresswall

- `ventures/egress-guard/demo/clean.json` — clean under egresswall's default policy
- `ventures/egress-guard/demo/leaky.json` — **4 violation(s)** under egresswall's default policy:
  - `RAW_IDENTIFIER at response.customer.contact_email: the email detector matched`
  - `RAW_IDENTIFIER at response.customer.national_id: the ssn detector matched`
  - `FORBIDDEN_KEY at response.integration.api_key: field name 'api_key' is forbidden by policy`
  - `SECRET_MATERIAL at response.integration.api_key: the openai_key detector matched`
- `ventures/egress-guard/demo/policy.json` — clean under egresswall's default policy
- `ventures/guardrail-checkup/demo/fixture/.mcp.json` — clean under egresswall's default policy
- `ventures/guardrail-checkup/demo/fixture/tests/fixtures/support_reply.json` — **2 violation(s)** under egresswall's default policy:
  - `RAW_IDENTIFIER at response.customer.contact_email: the email detector matched`
  - `FORBIDDEN_KEY at response.integration.api_key: field name 'api_key' is forbidden by policy`

A violation names a code and a path, never a value. These are checked-in fixtures; the same screen in front of a live MCP server is what stops the real answer.

### What a generic scorer will get wrong here

**guardrail-checkup did not run any of these tools.** It contacts no network and starts no `npx`. This is the falsifier list to have ready when you do run them, built from this repository's own files:

| A generic readiness scorer will say | True here | Command that shows it |
| --- | --- | --- |
| “Missing package manager lockfile” | `ventures/egress-guard/uv.lock` is committed | `wc -l ventures/egress-guard/uv.lock` |
| “Testing: 0/0 (0%)” | 31 file(s) sit in a test path | `git ls-files --cached --others --exclude-standard \| grep -cE '(^\|/)(tests?\|spec)/\|(^\|/)test_[^/]+$\|_test\.[a-z]+$\|\.(test\|spec)\.[jt]sx?$'` |

## 3. Invariant candidates

**Candidates — a human confirms or replaces them.** They are ranked by evidence, not by judgement: score = repair commits in the history that touched these paths (a commit that also touched a regression test counts twice) + 2 if CODEOWNERS names one of them + 1 if the path heuristic matched at all. This tool does not know your architecture and does not claim to.

### Invariant candidate 1 — An agent does not write to deployment and infrastructure without a human deciding first.

- **Governs:** `ventures/egress-guard/.github/workflows/`, `ventures/guardrail-checkup/.github/workflows/`, `ventures/plan-lint/.github/workflows/` — for example `ventures/egress-guard/.github/workflows/ci.yml`, `ventures/guardrail-checkup/.github/workflows/ci.yml`, `ventures/plan-lint/.github/workflows/ci.yml`
- **Evidence (score 4):**
  - path heuristic: 3 file(s) matching ventures/egress-guard/.github/workflows/, ventures/guardrail-checkup/.github/workflows/, ventures/plan-lint/.github/workflows/
  - git history: 3 repair commit(s) touched these paths — 2a233fd ventures/egress-guard: egresswall 0.1.0 release tree — ten verification rounds (clean-clone × claims-vs-code × red team), nine fix passes; 675 tests on 3.11/3.12/3.13; mcp-name registry line (pkg-egr…; dfdf07f ventures: guardrail-checkup working copy checkpoint — builder fix pass still in flight; not a release (orchestrator); e8a95c3 ventures: agent-plan-lint working copy checkpoint — tracked so the tree is on the remote while round-7 fixes land; not a release (orchestrator)
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

PROTECTED = ('ventures/egress-guard/.github/workflows/', 'ventures/guardrail-checkup/.github/workflows/', 'ventures/plan-lint/.github/workflows/')
event = json.load(sys.stdin)
if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)
target = event.get("tool_input", {}).get("file_path", "")
path = os.path.relpath(target, event.get("cwd", ".")) if target else ""
if path.startswith(PROTECTED):
    print(f"BLOCKED: {path} is under deploy, which a human decides. Ask, do not edit.", file=sys.stderr)
    sys.exit(2)
```

- **Test** (exits non-zero when a staged commit violates it): `! git diff --cached --name-only | grep -qE '^(ventures/egress\-guard/\.github/workflows/|ventures/guardrail\-checkup/\.github/workflows/|ventures/plan\-lint/\.github/workflows/)'`

### Invariant candidate 2 — An agent does not write to the dependency lockfiles without a human deciding first.

- **Governs:** `ventures/egress-guard/uv.lock`, `ventures/guardrail-checkup/uv.lock`, `ventures/plan-lint/uv.lock`
- **Evidence (score 4):**
  - path heuristic: 3 file(s) matching ventures/egress-guard/uv.lock, ventures/guardrail-checkup/uv.lock, ventures/plan-lint/uv.lock
  - git history: 3 repair commit(s) touched these paths — 2a233fd ventures/egress-guard: egresswall 0.1.0 release tree — ten verification rounds (clean-clone × claims-vs-code × red team), nine fix passes; 675 tests on 3.11/3.12/3.13; mcp-name registry line (pkg-egr…; dfdf07f ventures: guardrail-checkup working copy checkpoint — builder fix pass still in flight; not a release (orchestrator); e8a95c3 ventures: agent-plan-lint working copy checkpoint — tracked so the tree is on the remote while round-7 fixes land; not a release (orchestrator)
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

PROTECTED = ('ventures/egress-guard/uv.lock', 'ventures/guardrail-checkup/uv.lock', 'ventures/plan-lint/uv.lock')
event = json.load(sys.stdin)
if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)
target = event.get("tool_input", {}).get("file_path", "")
path = os.path.relpath(target, event.get("cwd", ".")) if target else ""
if path.startswith(PROTECTED):
    print(f"BLOCKED: {path} is under lockfiles, which a human decides. Ask, do not edit.", file=sys.stderr)
    sys.exit(2)
```

- **Test** (exits non-zero when a staged commit violates it): `! git diff --cached --name-only | grep -qE '^(ventures/egress\-guard/uv\.lock|ventures/guardrail\-checkup/uv\.lock|ventures/plan\-lint/uv\.lock)'`

### Invariant candidate 3 — An agent does not write to the schema and query layer without a human deciding first.

- **Governs:** `ventures/guardrail-checkup/demo/fixture/db/` — for example `ventures/guardrail-checkup/demo/fixture/db/migrations/0001_orders.sql`, `ventures/guardrail-checkup/demo/fixture/db/queries.py`
- **Evidence (score 2):**
  - path heuristic: 2 file(s) matching ventures/guardrail-checkup/demo/fixture/db/
  - git history: 1 repair commit(s) touched these paths — dfdf07f ventures: guardrail-checkup working copy checkpoint — builder fix pass still in flight; not a release (orchestrator)
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
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-db.py"
          }
        ]
      }
    ]
  }
}
```

  and `.claude/hooks/protect-db.py` (emitted; exit 2 blocks the call):

```python
#!/usr/bin/env python3
"""Block an agent write under a protected path. Drafted by guardrail-checkup; a human confirms it."""
import json, os, sys

PROTECTED = ('ventures/guardrail-checkup/demo/fixture/db/',)
event = json.load(sys.stdin)
if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)
target = event.get("tool_input", {}).get("file_path", "")
path = os.path.relpath(target, event.get("cwd", ".")) if target else ""
if path.startswith(PROTECTED):
    print(f"BLOCKED: {path} is under db, which a human decides. Ask, do not edit.", file=sys.stderr)
    sys.exit(2)
```

- **Test** (exits non-zero when a staged commit violates it): `! git diff --cached --name-only | grep -qE '^(ventures/guardrail\-checkup/demo/fixture/db/)'`

## 4. Monday list

1. Read invariant candidate 1 (deploy) in §3 and decide whether it is right. If it is, copy `DIR/hooks/protect-deploy.py` into `.claude/hooks/`, `chmod +x` it, and merge `DIR/hooks/settings-deploy.json` into `.claude/settings.json`. Re-run with `--emit-dir DIR` to write it; this run wrote no draft.
2. Create `.claude/settings.json` with the hooks block from §3. Neither settings file exists in this repository today, so every candidate in §3 has nowhere to live.
3. Add gitleaks or detect-secrets to CI or to `.pre-commit-config.yaml`. §5 explains why this tool cannot do it for you.

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
- **Command:** `guardrail-checkup run venture --out docs/dogfood/venture.md`
- **Repository commit:** `774a531278a235498a09611990d199c2290f59bd`
- **Repair commits examined:** 7, from the last 2000 non-merge commits
- **What left this machine: nothing.** This tool opens no socket and makes no model call. The git subcommands it runs are `ls-files`, `rev-parse` and `log`, all read-only. It wrote no file inside the repository it read.
- **Built on:** `agent-plan-lint` 0.1.0 (policy and plan validation), `egresswall` 0.1.0 (fixture screening, MCP proxy suggestion).
- **Lineage:** the plan gate comes from Graphene's admission validator and the screen from RegLineage's egress firewall, both the author's own prior work, extracted and re-tested as packages.
- **AI assistance:** this tool was written with AI assistance. **This report was not** — it is deterministic output from the files listed in §1, and re-running the command above on the same commit produces it again byte for byte.
- **No guarantee** is made about anything not listed in §1. The third-party tools named in §2 and §5 are unaffiliated with this one.
