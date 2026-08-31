"""What the two sibling packages contribute, and the files this tool offers to write.

Nothing here is ever written into the repository under inspection. Every draft
goes to the directory the user names with ``--emit-dir``.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from agent_plan_lint import DocumentError, load_plan, load_policy, validate_plan
from egresswall import Policy, check

from ._scan import Scan, _read

__all__ = [
    "FIXTURE_SAMPLE",
    "Composition",
    "compose",
    "emit",
    "hook_script",
    "one_line_test",
    "policy_globs",
    "settings_snippet",
    "starter_policy",
    "wrapped_mcp",
]

#: How many checked-in JSON fixtures are screened. A sample, not a sweep: this
#: section exists to show what egresswall would say, not to audit a corpus.
FIXTURE_SAMPLE = 5

#: Where a fixture may live for this tool to sample it.
_FIXTURE_PATH = re.compile(r"(^|/)(fixtures?|testdata|test_data|tests?|spec|demo|examples?)(/|$)")

#: The keys that identify a document as agent-plan-lint's rather than anyone
#: else's. Both are required, so a JSON file that happens to have "tasks" is
#: not mistaken for a plan.
POLICY_KEYS = ("policy_id", "allowed_write_globs")
PLAN_KEYS = ("mission_id", "tasks")


@dataclass
class Composition:
    """Everything the siblings produced, plus the drafts the CLI may emit."""

    policies: list[tuple[str, str]] = field(default_factory=list)
    plans: list[tuple[str, str]] = field(default_factory=list)
    validations: list[str] = field(default_factory=list)
    screened: list[tuple[str, list[str]]] = field(default_factory=list)
    drafts: dict[str, str] = field(default_factory=dict)
    #: The MCP servers `egresswall proxy` was put in front of, and the ones it
    #: could not be: a server that names a URL rather than a command is not
    #: reachable through a proxy that wraps a command line.
    wrapped: tuple[str, ...] = ()
    unwrapped: tuple[str, ...] = ()
    #: Paths left out of the starter policy because agent-plan-lint refuses
    #: them as globs (a backslash, a control or bidi character, a leading `./`).
    unpoliceable: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "policies": [{"path": path, "status": status} for path, status in self.policies],
            "plans": [{"path": path, "status": status} for path, status in self.plans],
            "validations": self.validations,
            "screened": [{"path": path, "violations": items} for path, items in self.screened],
            "drafts": sorted(self.drafts),
            "mcp": {"wrapped": list(self.wrapped), "unwrapped": list(self.unwrapped)},
            "unpoliceable": list(self.unpoliceable),
        }


def _identifier(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._:-]", "-", text).lstrip("-.:")[:128]
    return cleaned if cleaned and cleaned[0].isalnum() else "repo"


#: A path agent-plan-lint will not accept as a glob: it requires a canonical,
#: relative path and refuses a backslash, a control or bidi character, and a
#: leading `./`. A repository is free to contain such a path; a policy is not.
_UNPOLICEABLE = re.compile(
    "[\\\\\\x00-\\x1f\\x7f-\\x9f\\u061c\\u200b-\\u200f\\u202a-\\u202e\\u2066-\\u2069]|^\\.{1,2}/"
)


def policy_globs(items: list[str]) -> tuple[list[str], list[str]]:
    """Split path globs into the ones a policy can carry and the ones it cannot."""

    kept = [item for item in items if not _UNPOLICEABLE.search(item)]
    return kept, [item for item in items if _UNPOLICEABLE.search(item)]


def policy_paths(result: Scan) -> tuple[list[str], list[str], list[str]]:
    """The starter policy's write globs and exclusions, and what was left out of both.

    Write globs are the churn: the directories repair commits actually touched.
    Exclusions carve the candidates back out of them. With no history to read,
    every top-level directory stands in for the churn.
    """

    exclusions = sorted(
        {
            f"{prefix.rstrip('/')}/**" if prefix.endswith("/") else prefix
            for candidate in result.candidates
            for prefix in candidate.prefixes
        }
    )[:64]
    tops = sorted({f"{item.split('/', 1)[0]}/**" for item in result.files if "/" in item})
    writes, dropped_writes = policy_globs(list(result.churn) or tops)
    kept_exclusions, dropped_exclusions = policy_globs(exclusions)
    return writes, kept_exclusions, sorted(set(dropped_writes) | set(dropped_exclusions))


def starter_policy(result: Scan) -> dict:
    """A valid agent-plan-lint policy: write globs are the churn, exclusions the candidates.

    Valid is the claim, and tests/test_compose.py enforces it by loading every
    policy this function emits with ``agent_plan_lint.load_policy``, over
    repositories built from a hostile path alphabet as well as ordinary ones.
    """

    writes, exclusions, _ = policy_paths(result)
    return {
        "schema_version": 1,
        "policy_id": _identifier(result.root.name),
        "revision": 1,
        "repo_id": _identifier(result.root.name),
        "base_ref": "HEAD",
        "base_sha": result.head or "0" * 40,
        "allowed_read_globs": ["**"],
        "allowed_write_globs": writes or ["**"],
        "exclusions": exclusions,
        "command_templates": [{"template_id": "tests", "argv": ["make", "test"], "timeout_seconds": 600}],
        "network": {"mode": "deny"},
        "agent_roles": ["assembler", "verifier", "worker"],
        "max_concurrency": 4,
        "retry_limit": 1,
        "resource_budget": {"max_worker_seconds": 1800, "max_attempts": 12, "max_artifact_bytes": 1000000},
        "risk_gates": [],
    }


def wrapped_mcp(config: dict, policy_path: str) -> tuple[dict, tuple[str, ...], tuple[str, ...]]:
    """The MCP configuration with `egresswall proxy` in front of each server it can wrap.

    Returns the configuration, the servers that were wrapped, and the servers
    that were not: a server that names a URL rather than a command line is
    reached over the network, and a proxy that wraps a command cannot screen
    it. The report states both counts rather than saying "every server".
    """

    key = "mcpServers" if "mcpServers" in config else "servers"
    servers = dict(config.get(key) or {}) if isinstance(config.get(key), dict) else {}
    wrapped, unwrapped = [], []
    for name, entry in sorted(servers.items()):
        if not isinstance(entry, dict) or "command" not in entry:
            unwrapped.append(str(name))
            continue
        arguments = entry.get("args") if isinstance(entry.get("args"), list) else []
        inner = [str(entry["command"]), *[str(item) for item in arguments]]
        servers[name] = {
            **entry,
            "command": "egresswall",
            "args": ["proxy", "--policy", policy_path, "--", *inner],
        }
        wrapped.append(str(name))
    return {**config, key: servers}, tuple(wrapped), tuple(unwrapped)


def settings_snippet(slug: str) -> dict:
    """The .claude/settings.json block that wires a PreToolUse hook to a script.

    The shape is Claude Code's, verified against https://code.claude.com/docs/en/hooks
    on 2026-08-31; the fetched page is checked in at docs/evidence/claude-code-hooks.txt,
    which carries the date it was fetched on its second line.
    """

    return {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Write|Edit|MultiEdit",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-" + slug + ".py",
                        }
                    ],
                }
            ]
        }
    }


def hook_script(slug: str, prefixes: tuple[str, ...]) -> str:
    """A PreToolUse hook that blocks a write under `prefixes`. Exit 2 blocks the call."""

    listed = repr(tuple(prefixes))
    return f'''#!/usr/bin/env python3
"""Block an agent write under a protected path. Drafted by guardrail-checkup; a human confirms it."""
import json, os, sys

PROTECTED = {listed}
event = json.load(sys.stdin)
if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)
target = event.get("tool_input", {{}}).get("file_path", "")
path = os.path.relpath(target, event.get("cwd", ".")) if target else ""
if path.startswith(PROTECTED):
    print(f"BLOCKED: {{path}} is under {slug}, which a human decides. Ask, do not edit.", file=sys.stderr)
    sys.exit(2)
'''


def one_line_test(prefixes: tuple[str, ...]) -> str:
    """A shell one-liner that exits non-zero when a staged commit touches the paths."""

    pattern = "|".join(re.escape(item) for item in prefixes)
    return f"! git diff --cached --name-only | grep -qE '^({pattern})'"


def _documents(result: Scan) -> tuple[list[str], list[str]]:
    policies, plans = [], []
    for relative in result.files:
        if not relative.endswith(".json"):
            continue
        text = _read(result.root, relative)
        if text is None:
            continue
        if all(f'"{key}"' in text for key in POLICY_KEYS):
            policies.append(relative)
        elif all(f'"{key}"' in text for key in PLAN_KEYS):
            plans.append(relative)
    return policies, plans


def compose(result: Scan, policy_path: str) -> Composition:
    """Run the siblings over what the scan found, and draft what it did not."""

    out = Composition()
    policy_names, plan_names = _documents(result)
    loaded_policy = None
    for relative in policy_names:
        try:
            document = load_policy(result.root / relative)
            loaded_policy = loaded_policy or document
            out.policies.append((relative, "loads: a valid agent-plan-lint policy"))
        except DocumentError as error:
            out.policies.append((relative, f"refused: {error}"))
    for relative in plan_names:
        try:
            plan = load_plan(result.root / relative)
        except DocumentError as error:
            out.plans.append((relative, f"refused: {error}"))
            continue
        if loaded_policy is None:
            out.plans.append((relative, "loads: a valid agent-plan-lint plan; no policy found to validate it against"))
            continue
        validated = validate_plan(loaded_policy, plan)
        out.plans.append((relative, "within policy" if validated.valid else f"{len(validated.issues)} issue(s)"))
        out.validations.extend(f"{relative}: {issue.code} — {issue.message}" for issue in validated.issues)

    if not policy_names:
        out.drafts["starter-policy.json"] = json.dumps(starter_policy(result), indent=2) + "\n"
        out.unpoliceable = tuple(policy_paths(result)[2])

    if result.mcp_config is not None:
        _, config = result.mcp_config
        suggestion, out.wrapped, out.unwrapped = wrapped_mcp(config, policy_path)
        out.drafts["mcp-wrapped.json"] = json.dumps(suggestion, indent=2) + "\n"

    fixtures = [item for item in result.files if item.endswith(".json") and _FIXTURE_PATH.search(item)]
    for relative in fixtures[:FIXTURE_SAMPLE]:
        text = _read(result.root, relative)
        if text is None:
            continue
        try:
            payload = json.loads(text)
        except ValueError:
            continue
        out.screened.append((relative, [str(item) for item in check(payload, Policy())]))

    for candidate in result.candidates[:3]:
        out.drafts[f"hooks/protect-{candidate.slug}.py"] = hook_script(candidate.slug, candidate.prefixes)
        out.drafts[f"hooks/settings-{candidate.slug}.json"] = (
            json.dumps(settings_snippet(candidate.slug), indent=2) + "\n"
        )
    return out


def emit(drafts: dict[str, str], directory: Path) -> list[Path]:
    """Write every draft under `directory`. The only files this package creates."""

    written = []
    for name, body in sorted(drafts.items()):
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        if name.endswith(".py"):
            target.chmod(0o755)
        written.append(target)
    return written
