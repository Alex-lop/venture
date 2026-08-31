"""Reading a repository. Nothing here writes, executes repository code, or opens a socket.

The only subprocess this module starts is ``git``, and only with read-only
plumbing (``ls-files``, ``rev-parse``, ``log``). Every other fact comes from
``os.scandir`` and from opening a named file for reading.
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

__all__ = [
    "CATEGORIES",
    "CODEOWNERS_BONUS",
    "HEURISTIC_BASE",
    "HISTORY_COMMITS",
    "HISTORY_PATHS",
    "MAX_READ_BYTES",
    "READ_ONLY_GIT",
    "READ_ONLY_GIT_CONFIG",
    "REGRESSION_WEIGHT",
    "SKIP_DIRECTORIES",
    "SNIFF_BYTES",
    "Candidate",
    "Finding",
    "Repair",
    "Scan",
    "scan",
]

#: How many bytes of a named file this tool will read. A configuration file
#: larger than this is reported as skipped rather than parsed, so one enormous
#: checked-in JSON cannot decide how long a checkup takes.
MAX_READ_BYTES = 1_048_576

#: How much of a file is sniffed for a NUL byte before it is called binary.
SNIFF_BYTES = 8_192

#: How far back the history heuristic looks. Ranking asks which paths have
#: already been broken, and a repository with more history than this answers
#: that question from its most recent commits.
HISTORY_COMMITS = 2000

#: How many path entries the history walk will consume before it stops. The
#: commit cap alone does not bound the work: one vendor-refresh commit can name
#: a hundred thousand files. When this is reached the report says the history
#: was sampled rather than reading a monorepo's whole log into memory.
HISTORY_PATHS = 200_000

#: The score a candidate gets for the path heuristic alone, and what CODEOWNERS
#: and a regression-test repair add. §3 of the report states this arithmetic and
#: tests/test_scan.py checks a constructed repository against it.
HEURISTIC_BASE = 1
CODEOWNERS_BONUS = 2
REGRESSION_WEIGHT = 2

#: The git subcommands this tool runs. Every one is read-only; the tuple is
#: asserted by tests/test_readonly.py, which also fails on any other
#: subprocess in the package.
READ_ONLY_GIT = ("ls-files", "rev-parse", "log")

#: The configuration every git call overrides on the command line. The
#: inspected repository's own `.git/config` is data, not instructions, and both
#: of these keys name a program git would otherwise execute on our behalf:
#: `core.fsmonitor` runs on `ls-files`, `core.hooksPath` on anything that fires
#: a hook. A `-c` on the command line outranks the repository's file, so a
#: hostile checkout cannot put its own program back.
READ_ONLY_GIT_CONFIG = ("core.fsmonitor=false", "core.hooksPath=/dev/null")

#: What the directory walk skips when the path is not a git repository and
#: there is therefore no .gitignore engine to ask.
SKIP_DIRECTORIES = (
    ".git", ".hg", ".svn", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", ".venv",
    "__pycache__", "build", "dist", "node_modules", "venv",
)  # fmt: skip

#: Lockfile names, used twice: as an inventory fact and as a path candidate.
LOCKFILES = (
    "Cargo.lock", "Gemfile.lock", "Pipfile.lock", "composer.lock", "go.sum",
    "package-lock.json", "pnpm-lock.yaml", "poetry.lock", "uv.lock", "yarn.lock",
)  # fmt: skip

#: The places a junior would be stopped, in the runbook's words. Each entry is
#: a slug, the noun that goes in the rule sentence, and the path needles that
#: identify it. A needle ending in "/" matches a directory component; any other
#: needle matches anywhere in the path.
CATEGORIES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "db",
        "the schema and query layer",
        ("db/", "database/", "migrations/", "migrate/", "alembic/", "prisma/", "schema/"),
    ),
    ("auth", "authentication and session handling", ("auth/", "authn/", "authz/", "session/", "identity/")),
    ("payments", "money", ("payments/", "billing/", "pricing/", "invoice", "stripe", "checkout")),
    (
        "deploy",
        "deployment and infrastructure",
        ("deploy/", "infra/", "terraform/", "kubernetes/", "k8s/", "helm/", "ansible/", ".github/workflows/"),
    ),
    ("secrets", "secret material", ("secrets/", "credentials", "keys/", ".env")),
    (
        "generated",
        "generated and vendored files",
        ("generated/", "vendor/", "vendored/", "third_party/", "_pb2.py", ".pb.go", ".generated."),
    ),
    ("lockfiles", "the dependency lockfiles", LOCKFILES),
)

#: A commit subject that says the change was a repair. The history heuristic
#: counts a path once per matching commit that touched it.
REPAIR_SUBJECT = re.compile(r"(?i)\b(fix|fixes|fixed|revert|reverts|hotfix|regression|bugfix)\b")

#: A test path named for a regression. A repair commit that also touches one of
#: these is the strongest evidence the runbook asks for, and counts twice.
REGRESSION_TEST = re.compile(r"(?i)(^|/)(tests?|spec)/.*(regress|issue|_bug|/bug|bug_|bugfix)")

_AGENT_FILES = (
    "CLAUDE.md",
    "AGENTS.md",
    ".cursorrules",
    ".cursor/rules",
    ".github/copilot-instructions.md",
    "GEMINI.md",
)

#: A line in an agent-facing file that forbids something *and* names a path.
_FORBIDS = re.compile(r"(?i)\b(never|do not|don't|must not|forbidden|off[- ]limits|no touching|read[- ]only)\b")
_PATHISH = re.compile(r"[\w.-]+/|\*\*|\*\.\w+|\.env\b")

_TEST_RUNNER = re.compile(
    r"(?i)\b(pytest|unittest|tox|nox|npm (run )?test|yarn test|pnpm test|jest|vitest|"
    r"go test|cargo test|mvn test|gradle test|make test|rspec|phpunit)\b"
)
_SECRET_SCANNER = re.compile(r"(?i)\b(gitleaks|trufflehog|detect-secrets|ggshield|git-secrets)\b")
_SCREEN_IN_COMMAND = re.compile(r"(?i)(egresswall|mcp-scan|mcp-gateway|guardrail|proxy)")

#: Everything that could make a string in the report read as something other
#: than itself: the C0 and C1 controls (a newline ends a table row), the bidi
#: overrides (a filename can be made to render backwards) and the zero-width
#: marks (two different paths can be made to look identical).
_INVISIBLE = re.compile("[\\x00-\\x1f\\x7f-\\x9f\\u061c\\u200b-\\u200f\\u202a-\\u202e\\u2066-\\u2069\\ufeff]")

#: The markdown syntax a repository-controlled string may not carry into the
#: report: a code span, a link, an HTML tag. `|` is escaped by the renderer's
#: own _cell, which every table cell goes through.
_MARKDOWN = str.maketrans({"`": "\\`", "[": "\\[", "]": "\\]", "<": "\\<", ">": "\\>"})

#: How much of any one repository-controlled string reaches the report.
QUOTED_WIDTH = 200


def visible(text: str) -> str:
    """One repository-controlled string with nothing invisible left in it."""

    return _INVISIBLE.sub(lambda hit: f"\\u{ord(hit.group()):04x}", text)


def quoted(text: str) -> str:
    """A repository string, safe to put in a markdown cell or bullet, and bounded.

    Paths keep their punctuation -- `src/[id].tsx` is a real filename and the
    report must name it as it is -- so only the values read out of a
    repository's JSON, its commit subjects and its CODEOWNERS lines come
    through here.
    """

    out = visible(text).translate(_MARKDOWN)
    return out if len(out) <= QUOTED_WIDTH else out[: QUOTED_WIDTH - 1] + "…"


@dataclass(frozen=True)
class Finding:
    """One inventory fact, where it came from, and what it lets an agent do."""

    fact: str
    where: str
    consequence: str


@dataclass(frozen=True)
class Candidate:
    """A place a junior would be stopped. A candidate, never a conclusion."""

    slug: str
    rule: str
    paths: tuple[str, ...]
    prefixes: tuple[str, ...]
    evidence: tuple[str, ...]
    score: int


@dataclass
class Scan:
    """Everything read off one repository. The report renders this and nothing else."""

    given_path: str
    root: Path
    head: str | None
    files: list[str]
    total_files: int
    truncated: bool
    max_files: int
    is_git: bool
    languages: list[tuple[str, int]]
    total_bytes: int
    read: list[str] = field(default_factory=list)
    unread: list[str] = field(default_factory=list)
    owned: tuple[str, ...] = ()
    findings: list[Finding] = field(default_factory=list)
    candidates: list[Candidate] = field(default_factory=list)
    mcp_config: tuple[str, dict] | None = None
    repairs: int = 0
    #: Whether the history walk stopped at HISTORY_PATHS rather than reading
    #: every path the log names.
    history_sampled: bool = False
    #: The directories repair commits actually touched -- the churn hot-spots
    #: the starter policy grants writes in.
    churn: tuple[str, ...] = ()


# --- listing -----------------------------------------------------------------


def _argv(root: Path, *args: str) -> list[str]:
    """The whole command line for one git call, hardened against the checkout.

    The user's own configuration is left alone -- nulling it would also disable
    their `safe.directory` protection -- and only the keys that would make git
    run a program are overridden here.
    """

    assert args[0] in READ_ONLY_GIT, args[0]
    overrides = [item for setting in READ_ONLY_GIT_CONFIG for item in ("-c", setting)]
    return ["git", "-C", str(root), *overrides, "--no-optional-locks", *args]


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(_argv(root, *args), capture_output=True, check=False)


def _walk(root: Path) -> list[str]:
    out: list[str] = []
    for parent, directories, names in os.walk(root):
        directories[:] = sorted(item for item in directories if item not in SKIP_DIRECTORIES)
        for name in names:
            out.append(os.path.relpath(os.path.join(parent, name), root).replace(os.sep, "/"))
    return out


def list_files(root: Path, max_files: int) -> tuple[list[str], int, bool, bool]:
    """Every path this checkup considers, plus how many there were in total.

    In a git repository the list is git's own: tracked files plus untracked
    files that .gitignore does not exclude. Anywhere else it is a directory
    walk that skips SKIP_DIRECTORIES, because there is no .gitignore engine in
    the standard library and guessing one would report paths as read that were
    not.
    """

    done = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    is_git = done.returncode == 0
    if is_git:
        text = done.stdout.decode("utf-8", "surrogateescape")
        names = [item for item in text.split("\0") if item]
    else:
        names = _walk(root)
    # One representation for a path, decided here and not at either renderer: a
    # byte sequence that is not UTF-8 becomes U+FFFD and anything invisible
    # becomes a visible escape, so the markdown, the JSON and the emitted policy
    # all name the same thing.
    names = [visible(item.encode("utf-8", "surrogateescape").decode("utf-8", "replace")) for item in names]
    names.sort()
    return names[:max_files], len(names), len(names) > max_files, is_git


def _inside(root: Path, path: Path) -> bool:
    """True when `path` resolves to something at or under `root`."""

    try:
        target = path.resolve()
    except OSError:  # pragma: no cover - a resolve loop or a vanished path
        return False
    return target == root or root in target.parents


def _escapes(root: Path, relative: str) -> bool:
    """A listed path that is a symlink pointing out of the repository."""

    path = root / relative
    try:
        return path.is_symlink() and not _inside(root, path)
    except OSError:  # pragma: no cover - a path that cannot be stat'ed
        return False


def _read(root: Path, relative: str) -> str | None:
    """The text of one named file, or None if it is absent, binary, or too big.

    A symlink whose target is outside the repository is not read: this tool
    reports on one repository, and `CLAUDE.md -> /etc/passwd` would otherwise
    put a file from the reader's own machine into a report they hand over.
    """

    path = root / relative
    try:
        if not path.is_file() or path.stat().st_size > MAX_READ_BYTES:
            return None
        if not _inside(root, path):
            return None
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\0" in raw[:SNIFF_BYTES]:
        return None
    return raw.decode("utf-8", "replace")


def _line_of(text: str, needle: str) -> int:
    for number, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return number
    return 1


def _where(relative: str, text: str, needle: str) -> str:
    return f"{relative}:{_line_of(text, needle)}"


# --- guardrail inventory ------------------------------------------------------


#: A CODEOWNERS owner: a @user, a @org/team, or an email address.
_OWNER = re.compile(r"@[\w.-]+(/[\w.-]+)?|[^@\s]+@[^@\s]+\.[^@\s]+")


def _codeowners(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The patterns that name an owner, and the patterns that do not.

    A pattern with no owner is valid CODEOWNERS and does the opposite of
    requiring a reviewer: it clears the ownership an earlier line gave. Only an
    owned pattern is evidence, so only an owned pattern reaches the ranking.
    """

    owned, unowned = [], []
    for line in text.splitlines():
        fields = line.split("#", 1)[0].split()
        if not fields:
            continue
        (owned if any(_OWNER.fullmatch(item) for item in fields[1:]) else unowned).append(quoted(fields[0]))
    return tuple(owned), tuple(unowned)


def _matches_write(matcher: str) -> bool:
    """Whether a hook matcher catches a tool that writes.

    docs/evidence/claude-code-hooks.txt: "If you omit the matcher or use "*",
    the group activates on every occurrence of the event." So the strictest
    configuration there is -- a group that fires on every tool call -- is the
    one a naive substring test reads as matching nothing. `edit` covers
    `MultiEdit` and `NotebookEdit`; tests/test_hooks.py pins both.
    """

    return matcher.strip() in ("", "*") or bool(re.search(r"(?i)write|edit", matcher))


def _matches(path: str, needles: tuple[str, ...]) -> bool:
    for needle in needles:
        if needle.endswith("/"):
            if path.startswith(needle) or f"/{needle}" in path:
                return True
        elif needle in path:
            return True
    return False


def inventory(root: Path, files: list[str], scan_out: Scan) -> list[Finding]:
    """Which agent-facing artifacts exist, and what each one does or does not enforce."""

    present = set(files)
    found: list[Finding] = []

    def read(relative: str) -> str | None:
        text = _read(root, relative)
        (scan_out.read if text is not None else scan_out.unread).append(relative)
        return text

    # 1. Instruction files.
    for name in _AGENT_FILES:
        candidates = sorted(item for item in present if item == name or item.startswith(f"{name}/"))
        if not candidates:
            found.append(
                Finding(
                    f"{name}: absent",
                    "-",
                    "nothing written down here for an agent to follow, so every rule is folklore",
                )
            )
            continue
        for relative in candidates:
            text = read(relative)
            if text is None:
                found.append(Finding(f"{name}: present, not read", relative, "unreadable, too large, or binary"))
                continue
            forbidding = [
                (number, line)
                for number, line in enumerate(text.splitlines(), start=1)
                if _FORBIDS.search(line) and _PATHISH.search(line)
            ]
            if forbidding:
                number, _ = forbidding[0]
                found.append(
                    Finding(
                        f"{relative}: {len(text):,} bytes, {len(text.splitlines())} lines, "
                        f"{len(forbidding)} line(s) forbid something and name a path",
                        f"{relative}:{number}",
                        "prose an agent may follow; nothing here blocks a write, so it is guidance, not a guardrail",
                    )
                )
            else:
                found.append(
                    Finding(
                        f"{relative}: {len(text):,} bytes, {len(text.splitlines())} lines, "
                        "no line both forbids something and names a path",
                        f"{relative}:1",
                        "an agent reading this learns no path is off limits, and writes wherever the task leads",
                    )
                )

    # 2. Claude Code hooks.
    settings = ".claude/settings.json"
    text = read(settings) if settings in present else None
    if text is None:
        found.append(
            Finding(
                f"{settings}: absent",
                "-",
                "no PreToolUse or PostToolUse hook runs, so nothing inspects a tool call before it happens",
            )
        )
    else:
        parsed: object = None
        try:
            parsed = json.loads(text)
        except ValueError:
            found.append(Finding(f"{settings}: not valid JSON", f"{settings}:1", "the hook block cannot be read"))
        malformed = None
        if parsed is not None and not isinstance(parsed, dict):
            malformed = "not a JSON object"
        elif isinstance(parsed, dict) and "hooks" in parsed and not isinstance(parsed["hooks"], dict):
            malformed = "the hooks block is not a JSON object"
        if malformed is not None:
            found.append(
                Finding(
                    f"{settings}: {malformed}",
                    f"{settings}:1",
                    "the hook block cannot be read, so what it configures here is unknown",
                )
            )
        block = parsed.get("hooks") if isinstance(parsed, dict) else None
        hooks = block if isinstance(block, dict) else {}
        for event in ("PreToolUse", "PostToolUse"):
            listed = hooks.get(event)
            if listed is not None and not isinstance(listed, list):
                found.append(
                    Finding(
                        f"{settings}: the {event} block is not a list",
                        f"{settings}:1",
                        "the hook block cannot be read, so what it configures here is unknown",
                    )
                )
                listed = None
            entries = [item for item in (listed or []) if isinstance(item, dict)]
            if not entries:
                found.append(
                    Finding(
                        f"{settings}: no {event} hook",
                        f"{settings}:{_line_of(text, 'hooks')}",
                        "a tool call of this kind runs with nothing in front of it",
                    )
                )
                continue
            matchers = [quoted(str(item.get("matcher", ""))) for item in entries]
            writes = [item for item in matchers if _matches_write(item)]
            found.append(
                Finding(
                    f"{settings}: {len(entries)} {event} entr{'y' if len(entries) == 1 else 'ies'}, "
                    f"matcher(s) {', '.join(repr(item) for item in matchers) or 'unset'}"
                    + ("" if writes else "; none matches a write tool"),
                    _where(relative=settings, text=text, needle=event),
                    "a write to any path is inspected; whether this hook blocks is not checked, because "
                    "nothing here was executed"
                    if writes
                    else "no write tool is inspected by this event",
                )
            )

    # 3. MCP servers.
    for relative in (".mcp.json", "claude_desktop_config.json", ".claude/mcp.json"):
        if relative not in present:
            continue
        text = read(relative)
        if text is None:
            continue
        try:
            config = json.loads(text)
        except ValueError:
            found.append(Finding(f"{relative}: not valid JSON", f"{relative}:1", "the server list cannot be read"))
            continue
        if not isinstance(config, dict):
            found.append(Finding(f"{relative}: not a JSON object", f"{relative}:1", "the server list cannot be read"))
            continue
        servers = config.get("mcpServers") or config.get("servers") or {}
        if not isinstance(servers, dict):
            found.append(
                Finding(
                    f"{relative}: the server list is not a JSON object",
                    f"{relative}:1",
                    "the server list cannot be read",
                )
            )
            servers = {}
        if scan_out.mcp_config is None and servers:
            scan_out.mcp_config = (relative, config)
        for name, entry in sorted(servers.items()):
            where = _where(relative, text, f'"{name}"')
            label = f"{relative}: MCP server {quoted(str(name))!r}"
            if not isinstance(entry, dict):
                found.append(
                    Finding(f"{label} is not a JSON object", where, "this entry configures nothing that can be read")
                )
                continue
            if "command" not in entry:
                target = quoted(str(entry.get("url") or entry.get("type") or "no command and no url"))
                found.append(
                    Finding(
                        f"{label} is remote — {target}",
                        where,
                        "whatever this server returns reaches the agent's context unscreened, and a proxy in "
                        "front of a command cannot screen it",
                    )
                )
                continue
            arguments = entry.get("args") if isinstance(entry.get("args"), list) else []
            command = quoted(" ".join([str(entry["command"])] + [str(item) for item in arguments]))
            screened = bool(_SCREEN_IN_COMMAND.search(command))
            found.append(
                Finding(
                    f"{label} runs `{command.strip()}`" + ("" if screened else "; no screen in the command line"),
                    where,
                    "tool output is screened before the agent sees it"
                    if screened
                    else "whatever this server returns reaches the agent's context unscreened",
                )
            )
    if not any("MCP server" in item.fact for item in found):
        found.append(
            Finding(
                "no MCP server configuration found (.mcp.json, claude_desktop_config.json, .claude/mcp.json)",
                "-",
                "no tool servers are configured in this repository, so none can be screened here",
            )
        )

    # 4. pre-commit and git hooks.
    pre_commit = ".pre-commit-config.yaml"
    if pre_commit in present:
        text = read(pre_commit) or ""
        ids = len(re.findall(r"^\s*- id:", text, re.M))
        found.append(
            Finding(
                f"{pre_commit}: present, {ids} hook id(s)",
                f"{pre_commit}:1",
                "these run on commit, only for a contributor who installed the framework",
            )
        )
    else:
        found.append(Finding(f"{pre_commit}: absent", "-", "no commit-time check runs on a contributor's machine"))
    live = (
        sorted(
            item.name
            for item in (root / ".git" / "hooks").iterdir()
            if item.is_file() and not item.name.endswith(".sample")
        )
        if (root / ".git" / "hooks").is_dir()
        else []
    )
    found.append(
        Finding(
            f".git/hooks: {', '.join(live) if live else 'no installed hook (samples only)'}",
            ".git/hooks:1",
            "a commit is checked locally before it is made" if live else "nothing is checked at commit time",
        )
    )

    # 5. CODEOWNERS.
    owners_path = next(
        (item for item in ("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS") if item in present), None
    )
    if owners_path is None:
        found.append(
            Finding("CODEOWNERS: absent", "-", "no path requires a named reviewer, so any path can be merged by anyone")
        )
        scan_out.owned = ()
    else:
        text = read(owners_path) or ""
        owned, unowned = _codeowners(text)
        scan_out.owned = owned
        found.append(
            Finding(
                f"{owners_path}: {len(owned)} pattern(s) with a required reviewer"
                + (f", {len(unowned)} that name no owner" if unowned else ""),
                f"{owners_path}:1",
                "changes under an owned path need a named human, on the host, on a pull request; a pattern "
                "with no owner clears the ownership an earlier line gave"
                if owned
                else "no pattern here names an owner, so this file requires no reviewer anywhere",
            )
        )

    # 6. CI workflows.
    workflows = sorted(
        item for item in present if item.startswith(".github/workflows/") and item.endswith((".yml", ".yaml"))
    )
    if not workflows:
        found.append(Finding(".github/workflows: absent", "-", "no automated check runs on a change at all"))
    for relative in workflows:
        text = read(relative) or ""
        runs_tests = _TEST_RUNNER.search(text)
        on_pr = "pull_request" in text
        found.append(
            Finding(
                f"{relative}: tests {'run' if runs_tests else 'not found'}, "
                f"{'runs on pull requests' if on_pr else 'does not run on pull requests'}",
                _where(relative, text, runs_tests.group(0) if runs_tests else "on"),
                "a change is tested before review"
                if runs_tests and on_pr
                else "a change can reach review without this workflow having judged it",
            )
        )

    # 7. Secret scanning.
    scanners: list[str] = []
    for relative in [*workflows, pre_commit, ".gitleaks.toml", ".secrets.baseline"]:
        if relative not in present:
            continue
        text = _read(root, relative)
        if text and _SECRET_SCANNER.search(text):
            scanners.append(_where(relative, text, _SECRET_SCANNER.search(text).group(0)))
    found.append(
        Finding(
            f"secret scanning: {'configured' if scanners else 'not configured'}"
            + (f" ({len(scanners)} reference(s))" if scanners else " (no gitleaks, trufflehog or detect-secrets)"),
            scanners[0] if scanners else "-",
            "a committed credential is caught by a check"
            if scanners
            else "a credential an agent pastes into a file is committed with everything else",
        )
    )

    # 8. Lockfiles.
    locks = sorted(item for item in present if item.rsplit("/", 1)[-1] in LOCKFILES)
    found.append(
        Finding(
            f"lockfiles: {', '.join(locks) if locks else 'none found'}",
            f"{locks[0]}:1" if locks else "-",
            "a test run resolves the same dependencies twice"
            if locks
            else "no pinned dependency set, so a hook or a test run is not reproducible",
        )
    )

    # 9. Symlinks that leave the repository.
    escaping = sorted(item for item in files if _escapes(root, item))
    if escaping:
        found.append(
            Finding(
                f"symlinks out of this repository: {len(escaping)} — {', '.join(escaping[:4])}",
                f"{escaping[0]}:1",
                "the target is on this machine and not in this repository; it was listed and not read",
            )
        )

    # 10. Test layout.
    tests = [
        item
        for item in present
        if re.search(r"(^|/)(tests?|spec)/|(^|/)test_[^/]+$|_test\.[a-z]+$|\.(test|spec)\.[jt]sx?$", item)
    ]
    found.append(
        Finding(
            f"tests: {len(tests)} file(s) in a test path",
            f"{sorted(tests)[0]}:1" if tests else "-",
            "there is a suite a hook or a CI gate can call"
            if tests
            else "nothing to run, so no invariant can be enforced by a test",
        )
    )
    return found


# --- history and candidates ---------------------------------------------------


class Repair(NamedTuple):
    """One repair commit: what it is called, what it is worth, what it touched.

    The paths themselves are not kept. A monorepo's log names millions of them
    and the report uses at most three subjects, so each commit carries only the
    category slugs its paths matched.
    """

    sha: str
    subject: str
    weight: int
    categories: frozenset[str]


def history(
    root: Path, limit: int = HISTORY_COMMITS, max_paths: int = HISTORY_PATHS
) -> tuple[list[Repair], tuple[str, ...], bool]:
    """The repair commits, the directories they touched, and whether the walk was cut short.

    `git log --name-only` is read a line at a time and stopped at `max_paths`
    path entries: the commit cap bounds how far back this looks, and this one
    bounds how much any single commit can cost.
    """

    repairs: list[Repair] = []
    churn: set[str] = set()
    seen = 0
    sha = subject = ""
    weight, categories, repairing = 1, set(), False

    def close() -> None:
        if repairing:
            repairs.append(Repair(sha, quoted(subject), weight, frozenset(categories)))

    with subprocess.Popen(
        _argv(root, "log", "--no-merges", f"-n{limit}", "--name-only", "--format=%x00%h%x1f%s"),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    ) as process:
        assert process.stdout is not None
        truncated = False
        for raw in process.stdout:
            line = raw.decode("utf-8", "replace").rstrip("\n")
            if line.startswith("\0"):
                close()
                sha, _, subject = line[1:].partition("\x1f")
                weight, categories = 1, set()
                repairing = bool(REPAIR_SUBJECT.search(subject))
                continue
            if not line.strip():
                continue
            seen += 1
            if seen > max_paths:
                truncated = True
                break
            if not repairing:
                continue
            path = visible(line)
            if REGRESSION_TEST.search(path):
                weight = REGRESSION_WEIGHT
            categories |= {slug for slug, _, needles in CATEGORIES if _matches(path, needles)}
            if len(churn) < 4096:
                churn.add(f"{path.rsplit('/', 1)[0]}/**" if "/" in path else path)
        close()
        if truncated:  # the log is longer than the cap; stop git rather than read the rest
            process.stdout.close()
            process.kill()
        if process.wait() != 0 and not truncated:
            return [], (), False
    return repairs, tuple(sorted(churn)), truncated


def candidates(files: list[str], repairs: list[Repair], owned: tuple[str, ...]) -> list[Candidate]:
    """The invariant candidates, ranked. Candidates: a human confirms or replaces them.

    Score = the repair commits that touched these paths (a commit that also
    touched a regression test counts twice) + 2 if CODEOWNERS names one of them
    + 1 if the path heuristic matched at all. Ties break on the number of
    matching files, then on the slug.
    """

    out: list[Candidate] = []
    for slug, noun, needles in CATEGORIES:
        matched = [item for item in files if _matches(item, needles)]
        if not matched:
            continue
        prefixes = sorted({_prefix(item, needles) for item in matched})
        evidence: list[str] = [f"path heuristic: {len(matched)} file(s) matching {', '.join(prefixes)}"]
        score = HEURISTIC_BASE
        touched = [item for item in repairs if slug in item.categories]
        if touched:
            score += sum(item.weight for item in touched)
            named = [f"{item.sha} {item.subject}" for item in touched]
            evidence.append(f"git history: {len(named)} repair commit(s) touched these paths — {'; '.join(named[:3])}")
        owns = [
            pattern
            for pattern in owned
            if any(_matches(item, (pattern.lstrip("/").rstrip("*") or "/",)) for item in matched)
        ]
        if owns:
            score += CODEOWNERS_BONUS
            evidence.append(f"CODEOWNERS: {', '.join(sorted(set(owns))[:3])} already requires a named reviewer")
        out.append(
            Candidate(
                slug=slug,
                rule=f"An agent does not write to {noun} without a human deciding first.",
                paths=tuple(sorted(matched)[:8]),
                prefixes=tuple(prefixes),
                evidence=tuple(evidence),
                score=score,
            )
        )
    out.sort(key=lambda item: (-item.score, -len(item.paths), item.slug))
    return out


def _prefix(path: str, needles: tuple[str, ...]) -> str:
    """The needle that matched, as a path prefix a hook can compare against."""

    for needle in needles:
        if needle.endswith("/"):
            if path.startswith(needle):
                return needle
            if f"/{needle}" in path:
                return path[: path.index(f"/{needle}") + len(needle) + 1]
        elif needle in path:
            return path
    return path


# --- the whole scan -----------------------------------------------------------


def scan(given_path: str, max_files: int) -> Scan:
    root = Path(given_path).resolve()
    files, total, truncated, is_git = list_files(root, max_files)
    head = None
    if is_git:
        done = _git(root, "rev-parse", "HEAD")
        head = done.stdout.decode().strip() or None if done.returncode == 0 else None
    extensions = Counter(
        ("." + item.rsplit(".", 1)[1] if "." in item.rsplit("/", 1)[-1] else "(no extension)") for item in files
    )
    total_bytes = 0
    for item in files:
        with contextlib.suppress(OSError):
            # lstat, not stat: a symlink is worth its own size here, so a link
            # to a file outside the repository cannot inflate the total either.
            total_bytes += (root / item).lstat().st_size
    result = Scan(
        given_path=given_path,
        root=root,
        head=head,
        files=files,
        total_files=total,
        truncated=truncated,
        max_files=max_files,
        is_git=is_git,
        languages=sorted(extensions.items(), key=lambda pair: (-pair[1], pair[0]))[:10],
        total_bytes=total_bytes,
    )
    result.findings = inventory(root, files, result)
    repairs, churn, sampled = history(root)
    result.repairs = len(repairs)
    result.history_sampled = sampled
    result.churn = churn[:64]
    result.candidates = candidates(files, repairs, result.owned)
    return result
