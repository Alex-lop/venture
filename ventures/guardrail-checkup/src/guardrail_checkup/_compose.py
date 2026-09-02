"""What the two sibling packages contribute, and the files this tool offers to write.

Nothing here is ever written into the repository under inspection. Every draft
goes to the directory the user names with ``--emit-dir``.
"""

from __future__ import annotations

import json
import re
import shlex
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from ._scan import Scan, _read, _record, _screened, servers_of


def _siblings() -> tuple:
    """The two sibling packages, imported in the one function that uses them.

    At module scope a partial environment turns `import guardrail_checkup`
    itself into a two-level traceback and the console script into exit 1 -- the
    one status this tool promises never to return, and the one a reader would
    read as "it gated my change". Imported here, a missing sibling is an
    `ImportError` the CLI turns into one line and exit 2.
    """

    try:
        from agent_plan_lint import DocumentError, load_plan, load_policy, validate_plan
        from egresswall import Policy, check
    except ImportError as error:  # pragma: no cover - only reachable in a --no-deps install
        raise ImportError(
            "needs agent-plan-lint and egresswall, both declared dependencies: pip install guardrail-checkup"
        ) from error
    return DocumentError, load_plan, load_policy, validate_plan, Policy, check


__all__ = [
    "CANDIDATE_LIMIT",
    "EXCLUSION_GLOBS",
    "FIXTURE_SAMPLE",
    "SIGNATURE_SCAN_BYTES",
    "SIGNATURE_SCAN_FILES",
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

#: How many invariant candidates a report names and drafts a hook for, at most.
#: Three is the in-person session's number: a reader acts on three and skims a
#: longer list. §3 says how many it actually had.
CANDIDATE_LIMIT = 3

#: How many candidate path globs the starter policy can exclude. The report
#: names the cut because this cap changes what the emitted policy permits.
EXCLUSION_GLOBS = 64

#: How many checked-in JSON fixtures are screened. A sample, not a sweep: this
#: section exists to show what egresswall would say, not to audit a corpus.
FIXTURE_SAMPLE = 5

#: How many bytes of checked-in JSON the agent-plan-lint signature scan reads
#: before it stops. The sweep deliberately reads the whole listing rather than
#: the `--max-files` slice, so that "no document was found" is a statement about
#: the repository -- but nothing then bounded the work, and 20,000 JSON files of
#: 1 MiB apiece cost 18 seconds whatever `--max-files` said. The budget bounds
#: the work without bounding the truth: when it is spent §2 says how many files
#: were listed and not read, instead of reporting an absence it did not check.
SIGNATURE_SCAN_BYTES = 64 * 2**20

#: How many checked-in `.json` files the same sweep opens before it stops. The
#: byte budget bounds what is read out of a file and not what it costs to open
#: one: a repository of tiny checked-in JSON never spends 64 MiB, and 100,000
#: of them is eight seconds of `open` against the two tests/test_limits.py
#: holds one step to. Ten thousand is under a second here, and §2 counts the
#: rest into the same "listed and not read" clause the byte budget fills.
SIGNATURE_SCAN_FILES = 10_000

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
    #: The MCP servers `egresswall proxy` was put in front of; the ones it could
    #: not be, each with the reason; and the ones already running a screen, which
    #: would come back double-proxied if they were wrapped again.
    wrapped: tuple[str, ...] = ()
    unwrapped: tuple[tuple[str, str], ...] = ()
    already: tuple[str, ...] = ()
    #: Paths left out of the starter policy because agent-plan-lint refuses
    #: them as globs. Its own type decides, not a copy of its rules here.
    unpoliceable: tuple[str, ...] = ()
    #: How many checked-in `.json` files the signature scan listed and did not
    #: read, because SIGNATURE_SCAN_BYTES or SIGNATURE_SCAN_FILES was spent. §2
    #: says so instead of reporting that no policy document exists.
    signature_skipped: int = 0
    #: Candidate path globs omitted from the starter policy at EXCLUSION_GLOBS.
    exclusions_cut: int = 0
    #: What the emitted MCP suggestion names as egresswall's policy file. The
    #: report's §4 quotes it and says it is a placeholder, because running the
    #: emitted configuration before writing that policy fails.
    policy_path: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "policies": [{"path": path, "status": status} for path, status in self.policies],
            "plans": [{"path": path, "status": status} for path, status in self.plans],
            "validations": self.validations,
            "screened": [{"path": path, "violations": items} for path, items in self.screened],
            "drafts": sorted(self.drafts),
            "mcp": {
                "wrapped": list(self.wrapped),
                "unwrapped": [{"server": name, "reason": reason} for name, reason in self.unwrapped],
                "already_screened": list(self.already),
            },
            "unpoliceable": list(self.unpoliceable),
            "signature_scan_skipped": self.signature_skipped,
            "candidate_exclusions_cut": self.exclusions_cut,
        }


def _identifier(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._:-]", "-", text).lstrip("-.:")[:128]
    return cleaned if cleaned and cleaned[0].isalnum() else "repo"


def _glob_check() -> Callable[[str], bool]:
    """agent-plan-lint's own answer to "is this a legal write glob?".

    Not a second implementation of its rules. The first one was a regular
    expression covering a backslash, the control and bidi characters and a
    leading `./`, and it missed two whole classes the sibling refuses -- a path
    component ending in a dot or a space (Windows strips both, so `token.env.`
    and `token.env` are one file there) and U+00A0 with the rest of the
    invisible, combining and non-printable set. The emitted policy was then
    invalid and `unpoliceable` was empty, so §2 said nothing had been left out.
    This reads the annotated type off the policy model instead, so the two
    cannot drift again.
    """

    from agent_plan_lint import ProjectPolicy
    from pydantic import TypeAdapter  # agent-plan-lint's own dependency, not a new one

    adapter = TypeAdapter(ProjectPolicy.model_fields["allowed_write_globs"].annotation)

    def policeable(item: str) -> bool:
        try:
            adapter.validate_python((item,))
        except Exception:
            return False
        return True

    return policeable


def policy_globs(items: list[str]) -> tuple[list[str], list[str]]:
    """Split path globs into the ones a policy can carry and the ones it cannot."""

    policeable = _glob_check()
    kept = [item for item in items if policeable(item)]
    return kept, [item for item in items if not policeable(item)]


def policy_paths(result: Scan) -> tuple[list[str], list[str], list[str], int]:
    """The starter policy's write globs, capped candidate exclusions, omitted invalid paths, and cut count.

    Write globs are the churn: the directories repair commits actually touched.
    Exclusions carve the candidates back out of them. With no history to read,
    every top-level directory stands in for the churn.
    """

    # `[:CANDIDATE_LIMIT]`, because §3 and §4 both call these "the §3
    # candidates": built from every ranked candidate, a repository matching more
    # than three categories got a policy excluding paths no section named.
    all_exclusions = sorted(
        {
            f"{prefix.rstrip('/')}/**" if prefix.endswith("/") else prefix
            for candidate in result.candidates[:CANDIDATE_LIMIT]
            for prefix in candidate.prefixes
        }
    )
    exclusions = all_exclusions[:EXCLUSION_GLOBS]
    tops = sorted({f"{item.split('/', 1)[0]}/**" for item in result.files if "/" in item})
    writes, dropped_writes = policy_globs(list(result.churn) or tops)
    kept_exclusions, dropped_exclusions = policy_globs(exclusions)
    return (
        writes,
        kept_exclusions,
        sorted(set(dropped_writes) | set(dropped_exclusions)),
        len(all_exclusions) - len(exclusions),
    )


def starter_policy(result: Scan) -> dict:
    """A valid policy: write globs are the churn, exclusions up to EXCLUSION_GLOBS candidate paths.

    Valid is the claim, and tests/test_compose.py enforces it by loading every
    policy this function emits with ``agent_plan_lint.load_policy``, over
    repositories built from a hostile path alphabet as well as ordinary ones.
    """

    writes, exclusions, _, _ = policy_paths(result)
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


def wrapped_mcp(
    config: dict, policy_path: str
) -> tuple[dict, tuple[str, ...], tuple[tuple[str, str], ...], tuple[str, ...]]:
    """The MCP configuration with `egresswall proxy` in front of each server it can wrap.

    Returns the configuration, the servers that were wrapped, the servers that
    were not with the reason for each, and the servers that already run a
    screen. Four things stop a rewrite: a server that names a URL rather than a
    command line is reached over the network and a proxy that wraps a command
    cannot screen it; a server naming neither a command nor a URL configures
    nothing, so there is no command line to put a proxy in front of; a server
    whose command or `args` are not all strings cannot have its command line
    rebuilt without inventing one, and `str()` on a JSON object writes a Python
    repr into a shell argument; and a server already running `egresswall`,
    `mcp-gateway` or `mcp-scan` comes back double-proxied if it is wrapped
    again, while §2 reports it as screened. The report states
    every count rather than saying "every server".
    """

    key, listed = servers_of(config)
    servers = dict(listed) if isinstance(listed, dict) else {}
    wrapped: list[str] = []
    unwrapped: list[tuple[str, str]] = []
    already: list[str] = []
    for name, entry in sorted(servers.items()):
        if not isinstance(entry, dict) or "command" not in entry:
            # Only the entries that name a URL are reached over the network. An
            # entry naming neither a command nor a URL configures nothing, and
            # the inventory's own row says exactly that -- one report described
            # the same server two ways.
            remote = isinstance(entry, dict) and bool(entry.get("url"))
            unwrapped.append(
                (
                    str(name),
                    "reached over the network, and a proxy in front of a command cannot screen it"
                    if remote
                    else "this entry configures no command to wrap",
                )
            )
            continue
        arguments = entry.get("args") if isinstance(entry.get("args"), list) else []
        if not isinstance(entry["command"], str) or any(not isinstance(item, str) for item in arguments):
            unwrapped.append((str(name), "its command line is not all strings, so this tool will not rebuild it"))
            continue
        if _screened(entry["command"], arguments):
            already.append(str(name))
            continue
        servers[name] = {
            **entry,
            "command": "egresswall",
            "args": ["proxy", "--policy", policy_path, "--", entry["command"], *arguments],
        }
        wrapped.append(str(name))
    return {**config, key: servers}, tuple(wrapped), tuple(unwrapped), tuple(already)


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
    """A shell one-liner that exits non-zero when a staged commit touches the paths.

    The prefixes are filenames out of the repository under inspection, and the
    report offers this line to a reader to paste into a shell. `re.escape` makes
    a path safe for `grep`; it does not make it safe for `sh`, which is a
    different question and the dangerous one -- a file named
    ``stripe';id>PWNED;echo'.py`` closes the quote and appends a command. The
    whole pattern is one `shlex.quote`d token, so nothing in a filename is shell
    syntax.
    """

    pattern = "^(" + "|".join(re.escape(item) for item in prefixes) + ")"
    return f"! git diff --cached --name-only | grep -qE {shlex.quote(pattern)}"


def _documents(result: Scan) -> tuple[list[str], list[str], int]:
    """The checked-in policy and plan documents, and how many were not read.

    `result.all_files`, not the `--max-files` slice: "No document in
    agent-plan-lint's schema was found" read off a truncated listing is a false
    statement about a repository whose policy sorted past the cap, and §2 states
    it as a fact about the repository. The same rule the inventory follows.

    SIGNATURE_SCAN_BYTES and SIGNATURE_SCAN_FILES bound the reading instead,
    because the listing does not bound itself: the first is what a file costs to
    read, the second what it costs to open. The third value is how many `.json`
    files were left unopened when either budget ran out, and §2 says so rather
    than reporting an absence over files nobody read.
    """

    policies, plans = [], []
    budget, files, skipped = SIGNATURE_SCAN_BYTES, SIGNATURE_SCAN_FILES, 0
    for relative in result.all_files or result.files:
        if not relative.endswith(".json"):
            continue
        if budget <= 0 or files <= 0:
            skipped += 1
            continue
        files -= 1
        text = _record(result, relative, _read(result.root, relative))
        if text is None:
            continue
        budget -= len(text)
        if all(f'"{key}"' in text for key in POLICY_KEYS):
            policies.append(relative)
        elif all(f'"{key}"' in text for key in PLAN_KEYS):
            plans.append(relative)
    return policies, plans, skipped


def compose(result: Scan, policy_path: str) -> Composition:
    """Run the siblings over what the scan found, and draft what it did not."""

    DocumentError, load_plan, load_policy, validate_plan, Policy, check = _siblings()
    out = Composition(policy_path=policy_path)
    policy_names, plan_names, out.signature_skipped = _documents(result)
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
        # Raw here, escaped where it is rendered: this list is also the JSON
        # document's `composition.validations`, which is data and not markdown.
        # `relative` is a filename out of the checkout and `issue.detail` carries
        # the plan's own write paths, so §2's renderer seals both in a code span
        # -- a plan named `[click](evil.example) <img src=x onerror=…>.json` put
        # a live link and a live image into a report a reader hands over.
        out.validations.extend(f"{relative}: {issue.code} — {issue.detail}" for issue in validated.issues)

    if not policy_names:
        out.drafts["starter-policy.json"] = json.dumps(starter_policy(result), indent=2) + "\n"
        _, _, unpoliceable, out.exclusions_cut = policy_paths(result)
        out.unpoliceable = tuple(unpoliceable)

    if result.mcp_config is not None:
        _, config = result.mcp_config
        suggestion, out.wrapped, out.unwrapped, out.already = wrapped_mcp(config, policy_path)
        out.drafts["mcp-wrapped.json"] = json.dumps(suggestion, indent=2) + "\n"

    # The whole listing, for the same reason `_documents` reads it: "No
    # checked-in JSON fixture was found to screen" off a truncated list is a
    # statement about a repository, and FIXTURE_SAMPLE bounds the work anyway.
    listing = result.all_files or result.files
    fixtures = [item for item in listing if item.endswith(".json") and _FIXTURE_PATH.search(item)]
    for relative in fixtures[:FIXTURE_SAMPLE]:
        text = _record(result, relative, _read(result.root, relative))
        if text is None:
            continue
        try:
            payload = json.loads(text)
        except ValueError:
            continue
        out.screened.append((relative, [str(item) for item in check(payload, Policy())]))

    for candidate in result.candidates[:CANDIDATE_LIMIT]:
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
