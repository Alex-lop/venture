# Agent guardrail checkup — egresswall

Run 2026-08-31 · read-only · `egresswall` · HEAD `45917d4d7d42`
Produced by `guardrail-checkup`, a deterministic offline reader. No model was called for anything below; every judgement in §3 is yours to make.

## 1. Scope

- **Repository:** `egresswall`, as given on the command line
- **HEAD:** `45917d4d7d42b31c56dd0d73284b1e6623eaf63a`
- **Size:** 45 file(s) considered, 454,636 bytes (apparent size)
- **File list:** `git ls-files` — tracked files plus untracked files `.gitignore` does not exclude
- **Language mix** (by file extension), the 10 most common of 12:
  - `.py` — 16
  - `.json` — 8
  - `.txt` — 8
  - `.md` — 4
  - `.sh` — 2
  - `(no extension)` — 1
  - `.gitignore` — 1
  - `.lock` — 1
  - `.python-version` — 1
  - `.toml` — 1
- **Read:** the named guardrail artifacts listed in §2, `pyproject.toml`, `setup.cfg`, `package.json` (for the linter falsifier), every checked-in `.json` file the signature scan reached before its 64 MiB and 10,000 file budgets were spent, and up to 3 JSON fixture(s) screened in §2. A file over 1 MiB, or one whose first 8 KiB contains a NUL byte, is listed and not read.
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
| no MCP server configuration found (.mcp.json, claude_desktop_config.json, .claude/mcp.json) | `-` | no tool servers are configured in this repository, so none can be screened here |
| .pre-commit-config.yaml: absent | `-` | no commit-time check runs on a contributor's machine |
| .git/hooks: no installed hook (samples only) | `.git/hooks:1` | nothing is checked at commit time |
| CODEOWNERS: absent | `-` | no path in this repository names a required reviewer; branch protection on the host was not read |
| .github/workflows/ci.yml: a test runner is named in a run: step, runs on pull requests | `.github/workflows/ci.yml:29` | a test runner is named here and this workflow runs on pull requests; whether it ran, and on what, was not checked, because nothing here was executed |
| secret scanning: not configured (no gitleaks, trufflehog or detect-secrets) | `-` | a credential an agent pastes into a file is committed with everything else |
| lockfiles: uv.lock | `uv.lock:1` | a test run resolves the same dependencies twice |
| tests: 9 file(s) in a test path | `tests/conftest.py:1` | there is a suite a hook or a CI gate can call |

### agent-plan-lint

- No document in agent-plan-lint's schema was found (no `.json` file carries both `policy_id` and `allowed_write_globs`, or both `mission_id` and `tasks`).
- A starter policy was drafted instead; see §4. It was **not** written into your repository.

### egresswall

- `demo/clean.json` — clean under egresswall's default policy
- `demo/leaky.json` — **4 violation(s)** under egresswall's default policy:
  - `RAW_IDENTIFIER at response.customer.contact_email: the email detector matched`
  - `RAW_IDENTIFIER at response.customer.national_id: the ssn detector matched`
  - `FORBIDDEN_KEY at response.integration.api_key: field name 'api_key' is forbidden by policy`
  - `SECRET_MATERIAL at response.integration.api_key: the openai_key detector matched`
- `demo/policy.json` — clean under egresswall's default policy

A violation names a code and a path, never a value. These are checked-in fixtures; the same screen in front of a live MCP server is what stops the real answer.

### What a generic scorer will get wrong here

**guardrail-checkup did not run any of these tools.** It contacts no network and starts no `npx`. This is the falsifier list to have ready when you do run them, built from this repository's own files:

| A generic readiness scorer will say | True here | Command that shows it |
| --- | --- | --- |
| “Missing package manager lockfile” | `uv.lock` is committed | `wc -l uv.lock` |
| “Missing linter configuration” | a linter is configured at `pyproject.toml:50` | `grep -n -iE 'ruff\|eslint\|biome\|flake8\|prettier' pyproject.toml` |
| “Testing: 0/0 (0%)” | 9 file(s) sit in a test path | `git ls-files --cached --others --exclude-standard \| grep -cE '(^\|/)(tests?\|spec)/\|(^\|/)test_[^/]+$\|_test\.[a-z]+$\|\.(test\|spec)\.[jt]sx?$'` |

## 3. Invariant candidates

**Candidates — a human confirms or replaces them.** They are ranked by evidence, not by judgement: score = repair commits in the history that touched these paths (a commit that also touched a regression test counts twice) + 2 if CODEOWNERS names one of them + 1 if the path heuristic matched at all. This tool does not know your architecture and does not claim to.

Only 2 of the categories this tool knows matched a path here, so it names 2 candidate(s) and not three. The runbook's rule applies: do not invent a third.

All 2 of these are a bare path match at score 1: the path heuristic matched and nothing else did — no repair commit and no CODEOWNERS entry points at them. Equal scores are ordered by the number of matching files, then by name; that ordering is not evidence.

### Invariant candidate 1 — An agent does not write to deployment and infrastructure without a human deciding first.

- **Governs:** `.github/workflows/` — for example `.github/workflows/ci.yml`
- **Evidence (score 1):**
  - path heuristic: 1 file(s) matching .github/workflows/
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

### Invariant candidate 2 — An agent does not write to the dependency lockfiles without a human deciding first.

- **Governs:** `uv.lock`
- **Evidence (score 1):**
  - path heuristic: 1 file(s) matching uv.lock
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

PROTECTED = ('uv.lock',)
event = json.load(sys.stdin)
if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)
target = event.get("tool_input", {}).get("file_path", "")
path = os.path.relpath(target, event.get("cwd", ".")) if target else ""
if path.startswith(PROTECTED):
    print(f"BLOCKED: {path} is under lockfiles, which a human decides. Ask, do not edit.", file=sys.stderr)
    sys.exit(2)
```

- **Test** (exits non-zero when a staged commit violates it): `! git diff --cached --name-only | grep -qE '^(uv\.lock)'`

## 4. Monday list

1. Read invariant candidate 1 (deploy) in §3 and decide whether it is right. If it is, copy `DIR/hooks/protect-deploy.py` into `.claude/hooks/`, `chmod +x` it, and merge `DIR/hooks/settings-deploy.json` into `.claude/settings.json`. Re-run with `--emit-dir DIR` to write it; this run wrote no draft.
2. Create `.claude/settings.json` with the hooks block from §3. Neither settings file exists in this repository today, so every candidate in §3 has nowhere to live.
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
- **Command:** `guardrail-checkup run egresswall --out dogfood/egresswall.md`
- **Repository commit:** `45917d4d7d42b31c56dd0d73284b1e6623eaf63a`
- **Repair commits examined:** 0, from the last 2000 non-merge commits
- **What left this machine: nothing.** This tool opens no socket and makes no model call. The git subcommands it runs are `ls-files`, `rev-parse` and `log`, all read-only. It wrote no file inside the repository it read.
- **Built on:** `agent-plan-lint` 0.1.0 (policy and plan validation), `egresswall` 0.1.0 (fixture screening, MCP proxy suggestion).
- **Lineage:** the plan gate comes from Graphene's admission validator and the screen from RegLineage's egress firewall, both the author's own prior work, extracted and re-tested as packages.
- **AI assistance:** this tool was written with AI assistance. **This report was not** — it is deterministic output from the files listed in §1, and re-running the command above on the same commit produces it again byte for byte.
- **No guarantee** is made about anything not listed in §1. The third-party tools named in §2 and §5 are unaffiliated with this one.
