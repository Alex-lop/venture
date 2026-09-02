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
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

__all__ = [
    "AGENT_FILE_LIMIT",
    "CATEGORIES",
    "CHURN_GLOBS",
    "CODEOWNERS_BONUS",
    "HEURISTIC_BASE",
    "HISTORY_COMMITS",
    "HISTORY_PATHS",
    "HOOKS_PATH_CONFIG",
    "LANGUAGE_ROWS",
    "LINE_BUDGET",
    "MAX_READ_BYTES",
    "OWNER_LIMIT",
    "READ_ONLY_GIT",
    "READ_ONLY_GIT_CONFIG",
    "REGRESSION_WEIGHT",
    "SCREENS",
    "SERVER_ROWS",
    "SETTINGS_FILES",
    "SKIP_DIRECTORIES",
    "SNIFF_BYTES",
    "TEST_PATH",
    "WORKFLOW_LIMIT",
    "WRITE_TOOLS",
    "Candidate",
    "Finding",
    "Repair",
    "Scan",
    "md",
    "scan",
    "servers_of",
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

#: How many distinct directories the churn counter keeps. The starter policy
#: carries the CHURN_GLOBS most-churned of them; this only stops a monorepo's
#: log from filling memory with the rest.
CHURN_LIMIT = 4096

#: How many churn directories the drafted starter policy carries as write
#: globs: the most-churned first, ties broken by name. The cut was silent, and
#: it is the one place in this package where a cap decides what an emitted file
#: *grants* rather than what a row says -- a repository whose repair commits
#: touched a hundred directories was handed a policy denying writes in
#: thirty-six of them, with no clause anywhere saying so. §2 now names both
#: numbers.
CHURN_GLOBS = 64

#: How many path entries the history walk will consume before it stops. The
#: commit cap alone does not bound the work: one vendor-refresh commit can name
#: a hundred thousand files. When this is reached the report says the history
#: was sampled rather than reading a monorepo's whole log into memory. Every
#: path in a repair commit is matched against the seven categories, which is
#: about five microseconds of it, so the number is chosen the way WORKFLOW_LIMIT
#: was: 200,000 was 1.1 seconds at the cap and this is 0.6, against the two
#: seconds tests/test_limits.py holds one step to. The paths are what this
#: bounds; `--no-renames` on the log is what bounds the seconds, and
#: tests/test_limits.py now times this cap and the commit cap.
HISTORY_PATHS = 100_000

#: How many files one prefix entry of `_AGENT_FILES` -- `.cursor/rules` is the
#: only one today -- is read and rowed for. Every other axis in this tool is
#: capped and this one was not: 2,000 rule files of 1 MiB each are read at up to
#: MAX_READ_BYTES, split into lines and run past two regexes apiece, which is
#: files x lines with no bound on either factor and 50 seconds of it. The row
#: says how many were read when the cap bit.
AGENT_FILE_LIMIT = 64

#: How many lines one fan-out step will walk. Each step -- the `.cursor/rules`
#: read and the workflow read -- gets this budget separately, and a step that
#: spends it stops opening files and says so in the row that already counts the
#: ones it did not read.
#:
#: The file caps bound the files; they do not bound the work, because the cost
#: here is per *line* and MAX_READ_BYTES lets one file carry half a million
#: two-byte ones. Measured at the caps, on files of 1 MiB apiece: 64 rule files
#: of lines that match `_FORBIDS` and not `_PATHISH`, so both regexes run on
#: every line, is 8.4 million lines and 2.8 seconds; 32 workflows that are half
#: `run: |` block scalar and half top-level `on:` block, so `_run_steps` and
#: `_triggers` both copy most of the file, is 5.9 million lines and 2.8
#: seconds. Both are over the two seconds tests/test_limits.py holds one step
#: to, on a repository well inside every documented cap. A million lines is
#: half a second of the more expensive of the two, and 32 workflows of the
#: ordinary kind are three thousand lines in total, so nothing an honest
#: repository checks in ever reaches it. tests/test_limits.py times both steps
#: at the caps with the worst line shape each one has.
LINE_BUDGET = 1_000_000

#: How many extensions §1's language mix names. The eleventh onward used to
#: vanish out of a section that promises to say exactly what was and was not
#: read; §1 now says how many it left out.
LANGUAGE_ROWS = 10

#: How many MCP servers get a row of their own in §2. A `.mcp.json` naming
#: 17,000 servers produced 17,000 rows and a 3.6 MB report -- unreadable well
#: before it was slow. The remainder is one row that says how many there were.
SERVER_ROWS = 64

#: How many `.github/workflows` files are read and rowed. This was the one axis
#: with no cap: how many workflows a repository checks in is its own choice,
#: each one is read at up to MAX_READ_BYTES and walked line by line, and 1,000
#: of 1 MiB apiece took 44 seconds -- 22x the budget tests/test_limits.py holds
#: every other step to -- and produced 1,015 rows. The remainder is one row
#: saying how many were listed and not read, so no cell states a negative about
#: a workflow nobody opened. Half the other caps, because the worst case here is
#: 1 MiB of YAML apiece walked line by line: 64 of those was 2.2 seconds, over
#: the budget tests/test_limits.py holds one step to, and 32 is 0.6. The file
#: count is not the cost driver, so LINE_BUDGET bounds this step as well.
WORKFLOW_LIMIT = 32

#: How many distinct CODEOWNERS patterns the ranking will test against a
#: category's files. One pattern costs one substring search over a string built
#: once per category, so the work is O(patterns + files) rather than the product
#: -- but CODEOWNERS is read up to MAX_READ_BYTES, which is room for about
#: 150,000 patterns, and 150,000 searches is a minute of nothing. Past this the
#: CODEOWNERS row says how many were tested.
OWNER_LIMIT = 2000

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
#: `core.quotePath=false` is the third: with it on, git renders a path that is
#: not pure ASCII as a C-quoted literal (`"caf\303\251/db"`), and that literal
#: -- not the path -- became the starter policy's write glob, so the emitted
#: policy silently lost every directory whose name is not ASCII.
READ_ONLY_GIT_CONFIG = ("core.fsmonitor=false", "core.hooksPath=/dev/null", "core.quotePath=false")

#: The overrides for the single call that asks git where this checkout's hooks
#: live. `core.hooksPath=/dev/null` *is* the answer to that question, so it
#: would make every repository that moves its hooks look like one that installed
#: none. `rev-parse` fires no hook, so nothing from the checkout runs either
#: way; the `core.fsmonitor` override, which `rev-parse` would run, stays.
HOOKS_PATH_CONFIG = ("core.fsmonitor=false", "core.quotePath=false")

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

#: The settings files this tool reads for a hook, both repository-local. Claude
#: Code's own `/hooks` menu labels five hook sources
#: (docs/evidence/claude-code-hooks.txt:388-392):
#: User Settings : from ~/.claude/settings.json
#: Project Settings : from .claude/settings.json
#: Local Settings : from .claude/settings.local.json
#: Plugin Hooks : from a plugin's hooks/hooks.json
#: Session Hooks : registered in memory for the current session
#: Two of those five are these files. The other three are not in the checkout.
#: Neither is the "Managed policy settings" tier the same page's location
#: table adds at line 125 -- which is the enterprise policy §5 of every report
#: already names. So §5 says the hook sources outside this checkout were not
#: read, and every consequence below is scoped to this repository's checked-in
#: configuration. The second file is gitignored by Claude Code, so it is looked
#: for on disk as well as in the listing. tests/test_hooks.py counts the five
#: against the evidence file.
SETTINGS_FILES = (".claude/settings.json", ".claude/settings.local.json")

#: A line in an agent-facing file that forbids something *and* names a path.
_FORBIDS = re.compile(r"(?i)\b(never|do not|don't|must not|forbidden|off[- ]limits|no touching|read[- ]only)\b")
_PATHISH = re.compile(r"[\w.-]+/|\*\*|\*\.\w+|\.env\b")

#: A path that holds tests. One expression, used by the inventory's test-layout
#: row and by the report's "Testing: 0/0 (0%)" falsifier, so the two counts in
#: one report cannot disagree about what a test file is.
TEST_PATH = re.compile(r"(^|/)(tests?|spec)/|(^|/)test_[^/]+$|_test\.[a-z]+$|\.(test|spec)\.[jt]sx?$")

_TEST_RUNNER = re.compile(
    r"(?i)\b(pytest|unittest|tox|nox|npm (run )?test|yarn test|pnpm test|jest|vitest|"
    r"go test|cargo test|mvn test|gradle test|make test|rspec|phpunit)\b"
)
_SECRET_SCANNER = re.compile(r"(?i)\b(gitleaks|trufflehog|detect-secrets|ggshield|git-secrets)\b")

#: The executables whose presence at the head of an MCP server's command line
#: means the server's output passes a screen before the agent sees it. Matched
#: against the executable name and nothing else: a substring test over the whole
#: command line reports `@evil/proxy-exfil` as screened because its name
#: contains "proxy", and this is the one row in the report that asserts a
#: control is in force.
SCREENS = ("egresswall", "mcp-gateway", "mcp-scan")

#: Command names that run another command rather than being one. The screen, if
#: there is one, is the name after them.
_RUNNERS = ("bunx", "npx", "pnpm", "uvx", "yarn")

#: Everything that could make a string in the report read as something other
#: than itself: the C0 and C1 controls (a newline ends a table row), the bidi
#: overrides (a filename can be made to render backwards) and the zero-width
#: marks (two different paths can be made to look identical).
_INVISIBLE = re.compile("[\\x00-\\x1f\\x7f-\\x9f\\u061c\\u200b-\\u200f\\u202a-\\u202e\\u2066-\\u2069\\ufeff]")

#: The characters a repository-controlled string may not carry into the report
#: as themselves, in the order they are escaped. The backslash is first and the
#: order is load-bearing: escaping it after the others would double the
#: backslash they add, and CommonMark reads `\\[` as a literal backslash
#: followed by a *live* `[`. Then the characters that open a link, an HTML tag,
#: a code span or emphasis, and the pipe, which is the table's own delimiter.
_ESCAPE = "\\[]<>`*_|"

#: How much of any one repository-controlled string reaches the report.
QUOTED_WIDTH = 200

#: A double-quoted token in a line of JSON. `_quoted_lines` reads every one of
#: them in a single pass so a per-server line lookup is a dict hit.
_QUOTED_TOKEN = re.compile(r'"((?:[^"\\]|\\.)*)"')


def visible(text: str) -> str:
    """One repository-controlled string with nothing invisible left in it."""

    return _INVISIBLE.sub(lambda hit: f"\\u{ord(hit.group()):04x}", text)


def md(text: str, width: int = 0) -> str:
    """One repository-controlled string, rendered as itself and as nothing else.

    The single escaper. Every string a repository controls -- a path, an MCP
    server name, a hook matcher, a CODEOWNERS pattern, a commit subject --
    passes through this once, where it is interpolated into a fact, and through
    nothing afterwards. Escaping an already-escaped string is the defect this
    replaced: a second pass turns `\\[` into a literal backslash and a *live*
    `[`, so `.mcp.json` naming a server `[Approved by security](https://…)` put
    a working link in the report a reader hands to someone else.

    `width` cuts the text before it is escaped, so a cut can never leave half an
    escape behind. A control character, a bidi override and a zero-width mark
    become a visible `\\uXXXX`: a newline would otherwise end the table row and
    an override would render the name backwards.

    Inside a code span nothing here applies -- a backslash is literal there --
    so the renderer's `_code` widens the fence instead. That is the one place
    this function is not what runs.
    """

    if width and len(text) > width:
        text = text[: width - 1] + "…"
    for character in _ESCAPE:
        text = text.replace(character, "\\" + character)
    return _INVISIBLE.sub(lambda hit: f"\\u{ord(hit.group()):04x}", text)


def _code(text: str) -> str:
    """One inline code span that nothing in `text` can close or escape out of.

    Not the escaper, and the one place `md` does not run: a backslash is
    literal inside a code span, so `md` would render its own backslashes.
    CommonMark's answer to a backtick is a longer fence, and a leading or
    trailing backtick needs one space of padding; `visible` is what keeps a
    control character in a filename from ending the row. Repository-controlled
    text -- a path, a command built from one -- is rendered through this
    everywhere it sits in a code span, and through `md` everywhere else.

    It lives here, beside `md`, because a fact built in this module needs it
    too: the MCP command line was escaped with `md` and then put inside a
    hand-built single-backtick span, where a backtick in the command closed the
    span early and every backslash `md` added rendered as itself.
    """

    text = visible(text)
    fence = "`" * (max((len(run) for run in re.findall(r"`+", text)), default=0) + 1)
    pad = " " if text.startswith("`") or text.endswith("`") else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def _bar(text: str) -> str:
    """The pipe escape a code span needs inside a table, and only there.

    `md` escapes the pipe in every repository-controlled string it renders as
    text, so a fact and a consequence arrive already escaped and must not be
    escaped again. A code span is the one place `md` does not run, and GFM still
    ends the cell on a bare `|`.
    """

    return text.replace("|", "\\|")


def _text(raw: bytes) -> str:
    """One name out of git's output, as the one representation this tool uses.

    `surrogateescape` first, so nothing is lost between git's bytes and the
    normalisation, then the round trip that decides the representation once and
    not at either renderer: a byte sequence that is not UTF-8 becomes U+FFFD and
    anything invisible becomes a visible escape, so the markdown, the JSON and
    the emitted policy all name the same thing.
    """

    return visible(_decode(raw))


def _decode(raw: bytes) -> str:
    """git's bytes as one string, losing nothing on the way and no surrogate at the end."""

    return raw.decode("utf-8", "surrogateescape").encode("utf-8", "surrogateescape").decode("utf-8", "replace")


def _records(stream: object) -> Iterator[bytes]:
    """git's `-z` output, one NUL-separated record at a time and never all at once."""

    buffer = b""
    for chunk in iter(lambda: stream.read(65_536), b""):
        buffer += chunk
        *records, buffer = buffer.split(b"\0")
        yield from records
    if buffer:
        yield buffer


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
    #: Up to eight of the matching paths, as examples for the report.
    paths: tuple[str, ...]
    #: How many files matched -- the tie-break §3 and the README both state.
    #: `len(paths)` was the tie-break and it is capped at eight, so a category
    #: of twenty files lost to one of nine.
    matched: int
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
    #: Every path the listing found, before `--max-files` cut it. The inventory
    #: asks this one whether a named artifact exists, because answering "none
    #: found" off the truncated list is a false statement rather than a gap.
    all_files: list[str]
    total_files: int
    truncated: bool
    max_files: int
    is_git: bool
    languages: list[tuple[str, int]]
    #: How many distinct extensions the capped listing held, before
    #: `languages` was cut to the ten most common. §1 says how many it left out.
    extensions: int
    total_bytes: int
    read: list[str] = field(default_factory=list)
    unread: list[str] = field(default_factory=list)
    #: A shadow set over the two lists above, and the only thing `_record`
    #: tests membership against. The lists stay because §1 and the JSON
    #: document's `scope.read` are ordered; the membership test over them was
    #: linear, one `_record` call is made per file opened, and the signature
    #: scan opens every checked-in `.json` file the listing names -- so the
    #: recorder was O(files²) and cost 100 seconds of a 126-second run over a
    #: repository of 200,000 tiny JSON files. tests/test_limits.py times it.
    recorded: set[str] = field(default_factory=set)
    owned: tuple[str, ...] = ()
    findings: list[Finding] = field(default_factory=list)
    candidates: list[Candidate] = field(default_factory=list)
    mcp_config: tuple[str, dict] | None = None
    repairs: int = 0
    #: Whether the history walk stopped at HISTORY_PATHS rather than reading
    #: every path the log names.
    history_sampled: bool = False
    #: The most-churned directories repair commits touched -- the hot-spots the
    #: starter policy grants writes in, at most CHURN_GLOBS of them.
    churn: tuple[str, ...] = ()
    #: How many more churned directories there were, which the starter policy
    #: does not grant writes in. §2 says so when it is not zero.
    churn_cut: int = 0


# --- listing -----------------------------------------------------------------


def _argv(root: Path, *args: str, config: tuple[str, ...] = READ_ONLY_GIT_CONFIG) -> list[str]:
    """The whole command line for one git call, hardened against the checkout.

    The user's own configuration is left alone -- nulling it would also disable
    their `safe.directory` protection -- and only the keys that would make git
    run a program are overridden here. `config` is `READ_ONLY_GIT_CONFIG` for
    every call but the two that ask where this checkout's hooks live and which
    git directory a linked worktree shares; see `HOOKS_PATH_CONFIG`.
    """

    assert args[0] in READ_ONLY_GIT, args[0]
    overrides = [item for setting in config for item in ("-c", setting)]
    return ["git", "-C", str(root), *overrides, "--no-optional-locks", *args]


def _git(root: Path, *args: str, config: tuple[str, ...] = READ_ONLY_GIT_CONFIG) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(_argv(root, *args, config=config), capture_output=True, check=False)


def _walk(root: Path) -> list[str]:
    def relative(full: str) -> str:
        return os.path.relpath(full, root).replace(os.sep, "/")

    out: list[str] = []
    for parent, directories, names in os.walk(root):
        keep: list[str] = []
        for item in sorted(directories):
            if item in SKIP_DIRECTORIES:
                continue
            # A symlink to a directory is a leaf, not a branch: os.walk hands it
            # over in `directories` and never descends into it, so listing it
            # here is the only way a link to a whole tree outside the repository
            # reaches finding 9 -- the dangerous case the README's guarantee is
            # about.
            if os.path.islink(os.path.join(parent, item)):
                out.append(relative(os.path.join(parent, item)))
            else:
                keep.append(item)
        directories[:] = keep
        out.extend(relative(os.path.join(parent, name)) for name in names)
    return out


def list_files(root: Path, max_files: int) -> tuple[list[str], list[str], bool, bool]:
    """The paths this checkup considers, and every path the listing found.

    In a git repository the list is git's own: tracked files plus untracked
    files that .gitignore does not exclude. Anywhere else it is a directory
    walk that skips SKIP_DIRECTORIES, because there is no .gitignore engine in
    the standard library and guessing one would report paths as read that were
    not.

    Two lists come back because `--max-files` bounds the work, not the truth:
    the ranking and the language mix read the capped list, and the inventory
    reads the whole one so that "lockfiles: none found" is never said about a
    repository whose lockfile sorted past the cap.
    """

    done = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    is_git = done.returncode == 0
    if is_git:
        names = [_text(item) for item in done.stdout.split(b"\0") if item]
    else:
        names = [_text(item.encode("utf-8", "surrogateescape")) for item in _walk(root)]
    names.sort()
    return names[:max_files], names, len(names) > max_files, is_git


def _inside(root: Path, path: Path) -> bool:
    """True when `path` resolves to something at or under `root`.

    `os.path.realpath`, not `Path.resolve`: two symlinks pointing at each other
    make `resolve` raise `RuntimeError` on CPython 3.11+, which killed the whole
    run and produced no report at all. `realpath` returns the unresolved path on
    a loop, which is not inside `root`, which is the answer this needs.
    """

    try:
        target = Path(os.path.realpath(path))
    except (OSError, ValueError):  # pragma: no cover - a path that cannot be read at all
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


def _record(result: Scan, relative: str, text: str | None) -> str | None:
    """Record one `_read` against §1's own list, once, and hand the text back.

    §1 promises "exactly what was and was not read" and the JSON document
    renders `scope.read` and `scope.unread` from these two lists, so every call
    to `_read` anywhere in the package goes through here. The falsifier list's
    linter lookup did not, and a repository whose only linter evidence is
    `[tool.ruff]` in `pyproject.toml` produced the row with `scope.read` empty.
    Idempotent, because one scan may be rendered or composed more than once --
    and the idempotence is a set lookup, not a scan of the two lists it guards.
    """

    if relative not in result.recorded:
        result.recorded.add(relative)
        (result.read if text is not None else result.unread).append(relative)
    return text


def _line_of(lines: list[str], needle: str) -> int:
    """The line one needle first appears on, off the file's own line list.

    The list is split once per file by the caller: this lookup, the comment
    stripper and the two YAML readers all walked the same text apart, which was
    four passes over a megabyte for one row.
    """

    for number, line in enumerate(lines, start=1):
        if needle in line:
            return number
    return 1


def _quoted_lines(text: str) -> dict[str, int]:
    """Every double-quoted token in one file, and the line it first appears on.

    Built once per file, before the loop that needs it. Scanning the whole text
    once per MCP server instead is O(servers x lines), and both grow together
    inside MAX_READ_BYTES: a two-file repository whose `.mcp.json` names 17,000
    servers spent 25 seconds here and nowhere else.
    """

    index: dict[str, int] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        for token in _QUOTED_TOKEN.findall(line):
            index.setdefault(token, number)
    return index


def _where(relative: str, lines: dict[str, int], needle: str) -> str:
    """`file:line` for one JSON key, off the index built once for that file."""

    return f"{relative}:{lines.get(needle, 1)}"


def _at(relative: str, lines: list[str], needle: str) -> str:
    """`file:line` for the files this tool looks something up in exactly once."""

    return f"{relative}:{_line_of(lines, needle)}"


# --- guardrail inventory ------------------------------------------------------


#: A CODEOWNERS owner: a @user, a @org/team, or an email address.
_OWNER = re.compile(r"@[\w.-]+(/[\w.-]+)?|[^@\s]+@[^@\s]+\.[^@\s]+")


def _codeowners(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The patterns that name an owner, and the patterns that do not.

    A pattern with no owner is valid CODEOWNERS and does the opposite of
    requiring a reviewer: it clears the ownership an earlier line gave. Only an
    owned pattern is evidence, so only an owned pattern reaches the ranking.

    The patterns come back as the file wrote them. They are matched against real
    paths before they are rendered, and an escaped pattern matches nothing.
    """

    owned, unowned = [], []
    for line in text.splitlines():
        fields = line.split("#", 1)[0].split()
        if not fields:
            continue
        (owned if any(_OWNER.fullmatch(item) for item in fields[1:]) else unowned).append(fields[0])
    return tuple(owned), tuple(unowned)


#: The core tools that write a file. A matcher is tested against these names
#: and nothing else, so `WriteLog` -- an exact matcher naming one tool that is
#: not a write tool -- no longer reads as "a write to any path is inspected".
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")

#: The character set that keeps a matcher on the exact-match path
#: (docs/evidence/claude-code-hooks.txt:145-146). Anything else in it makes the
#: matcher an unanchored regular expression.
_EXACT_MATCHER = re.compile(r"[A-Za-z0-9_\- ,|]*")


#: A JavaScript named capture group. Claude Code's matchers are JavaScript
#: regular expressions and `(?<name>...)` is the syntax JavaScript spells it
#: with; Python spells the same thing `(?P<name>...)` and rejects the other,
#: which sent `(?<x>Write)` -- a matcher that does catch `Write` -- down the
#: "no write tool is inspected" branch. The lookbehinds `(?<=` and `(?<!` are
#: valid in both and are left alone.
_JS_GROUP = re.compile(r"\(\?<(?![=!])")


def _matches_write(matcher: str) -> bool | None:
    """Whether a hook matcher catches a tool that writes, or None when unknown.

    The three modes docs/evidence/claude-code-hooks.txt:145-146 names, in its
    order. `"*"`, `""` or an omitted matcher fires on every occurrence of the
    event -- so the strictest configuration there is is the one a naive
    substring test reads as matching nothing. A matcher of only letters,
    digits, `_`, `-`, spaces, `,` and `|` is an exact string, or a `|`/`,`
    separated list of them. Anything else is an unanchored regular expression,
    tested against each write tool's name the way `RegExp.prototype.test` would.

    Both directions of the substring test this replaced were wrong. `.*`,
    `^Notebook` and `Bash|.*` all match a write tool and were reported as
    matching none -- the false negative that tells a reader nothing inspects a
    write when something does; `WriteLog` and `mcp__notes__write_note` match no
    write tool and were reported as inspecting every path.
    """

    matcher = matcher.strip()
    if matcher in ("", "*"):
        return True
    if _EXACT_MATCHER.fullmatch(matcher):
        names = {item.strip() for token in matcher.split("|") for item in token.split(",")}
        return bool(names & set(WRITE_TOOLS))
    try:
        pattern = re.compile(_JS_GROUP.sub("(?P<", matcher))
    except re.error:
        # Not a regular expression this tool can evaluate. Saying "no write tool
        # is inspected" about it is a negative fact about a matcher that was
        # never run, and it is the direction that costs the reader, so the
        # caller hedges the row instead.
        return None
    return any(pattern.search(name) for name in WRITE_TOOLS)


def _screened(command: str, arguments: list[object]) -> bool:
    """Whether the executable this MCP server runs is one of the known screens.

    Decided on the executable name alone. A substring test over the joined
    command line reports `npx -y @evil/proxy-exfil` as screened because the
    package name contains "proxy", and the consequence column then states an
    unhedged safety fact about it.
    """

    words = [str(command), *(str(item) for item in arguments)]
    while words and _names(words[0], _RUNNERS):
        words = [item for item in words[1:] if not item.startswith("-")]
    return bool(words) and _names(words[0], SCREENS)


def _names(token: str, allowed: tuple[str, ...]) -> bool:
    """Whether one command-line token names one of `allowed`.

    A bare name is resolved on PATH and an absolute path is the file it names.
    Anything else -- `@evil/egresswall`, `./egresswall`, `bin/egresswall` -- is
    a package someone else publishes or a binary the checkout itself ships, and
    the npm scope is exactly where a package's identity lives. Taking the last
    path segment threw that away, so `npx -y @evil/egresswall` was reported as
    screened. This is the one row in the report that asserts a control is in
    force.
    """

    return token in allowed or (token.startswith("/") and token.rsplit("/", 1)[-1] in allowed)


#: A `run:` key, and a `#` comment that is not inside a word. Both are matched
#: once per line of every workflow, so both are compiled once here.
_RUN_STEP = re.compile(r"^(\s*)(-\s+)?run\s*:\s*(.*)$")
_COMMENT = re.compile(r"(?<!\S)#.*$")


def _run_steps(body: list[str]) -> str:
    """Every `run:` value in a workflow, and nothing else in it.

    The test-runner detector was a word search over the whole file, so a step
    named `why we dropped pytest` made the row state that this workflow tests a
    change before review, for a workflow that runs `echo hi`. Only a `run:`
    value is a command the workflow executes; a `name:`, an `if:` guard, an
    `env:` value and a job id are not. A block scalar (`run: |`) carries its
    command on the lines indented past the `run:` key, which are collected too.
    """

    out: list[str] = []
    block: int | None = None
    for line in body:
        if block is not None:
            if not line.strip() or len(line) - len(line.lstrip()) > block:
                out.append(line)
                continue
            block = None
        match = _RUN_STEP.match(line)
        if match:
            if match.group(3).strip().rstrip("+-") in ("|", ">"):
                block = len(match.group(1)) + len(match.group(2) or "")
            else:
                out.append(match.group(3))
    return "\n".join(out)


def _triggers(body: list[str]) -> str:
    """A workflow's top-level `on:` block: from `on:` to the next key at column 0.

    Whether a workflow runs on pull requests was a substring search over the
    whole file, so a job named `pull_request_notes` in an `on: push` workflow
    made the consequence column state, unhedged, that a change is tested before
    review. Covers `on: pull_request`, `on: [push, pull_request]` and the block
    form; a workflow that names the trigger anywhere else is not one that runs
    on it.
    """

    out: list[str] = []
    inside = False
    for line in body:
        if re.match(r"""^["']?on["']?\s*:""", line):
            inside, out = True, [line]
        elif inside and (not line.strip() or line[:1].isspace()):
            out.append(line)
        elif inside:
            break
    return "\n".join(out)


def _uncommented(lines: list[str]) -> list[str]:
    """The same lines with `#` comments removed, for the detectors that grep them.

    `# we do NOT use gitleaks here` is a workflow saying the opposite of what a
    bare substring search reads off it, and the row it produces asserts that a
    committed credential is caught.
    """

    # Compiled once and skipped outright on a line with no `#`: this is the
    # hottest loop in the scan -- one call per line of every workflow -- and
    # `re.sub` with a pattern string looks the compiled form up every time.
    return [_COMMENT.sub("", line) if "#" in line else line for line in lines]


def _common_dir(root: Path) -> Path:
    """The git directory this checkout shares with its main one, resolved.

    A linked worktree's hooks live under the main checkout's `.git`, which is the
    one legitimate answer outside `root`. Anything else `core.hooksPath` names is
    a directory on the reader's machine that this repository chose.
    """

    done = _git(root, "rev-parse", "--git-common-dir", config=HOOKS_PATH_CONFIG)
    answer = done.stdout.decode("utf-8", "replace").strip() if done.returncode == 0 else ""
    return Path(os.path.realpath(root / answer)) if answer else root


def _hooks_dir(root: Path) -> tuple[Path | None, str | None]:
    """Where git looks for this checkout's hooks, and the answer this tool refused.

    `core.hooksPath` moves the directory and a linked worktree's `.git` is a
    file, so `<root>/.git/hooks` is the wrong place to look in exactly the two
    configurations an installed, blocking hook is most likely to live in --
    and the row would then state the opposite as fact.

    The answer is contained, because `core.hooksPath` is the *inspected*
    repository's setting and the whole tool treats that checkout as untrusted
    input. Unchecked, `core.hooksPath = ~/.ssh` made this a directory listing of
    the reader's private files, printed into a report they hand to someone else
    under the heading "the hooks directory this worktree shares with its main
    checkout". A path at or under `root`, or under the git directory a linked
    worktree shares with its main checkout, is read; anything else comes back as
    the refused answer, which is itself worth a row.
    """

    done = _git(root, "rev-parse", "--git-path", "hooks", config=HOOKS_PATH_CONFIG)
    if done.returncode != 0:
        return None, None
    answer = done.stdout.decode("utf-8", "replace").strip()
    if not answer:
        return None, None
    candidate = root / answer
    if _inside(root, candidate) or _inside(_common_dir(root), candidate):
        return candidate, None
    return None, answer


def servers_of(config: dict) -> tuple[str, object]:
    """The key an MCP configuration lists its servers under, and what is there.

    One reader for both callers. The inventory took `mcpServers or servers` and
    the emitted suggestion took `mcpServers if present else servers`, so a
    configuration carrying an empty `mcpServers` beside a populated `servers`
    made the report state a count its own table contradicted and hardened
    nothing. Whatever is there comes back as it is, dict or not, because the
    caller reports a server list that is not an object rather than dropping it.
    """

    chosen = config.get("mcpServers") or config.get("servers")
    key = "mcpServers" if config.get("mcpServers") else "servers"
    return key, {} if chosen is None else chosen


def _matches(path: str, needles: tuple[str, ...]) -> bool:
    for needle in needles:
        if needle.endswith("/"):
            if path.startswith(needle) or f"/{needle}" in path:
                return True
        elif needle in path:
            return True
    return False


def _unread_row(relative: str) -> Finding:
    """The one row for a named artifact that is present and could not be read.

    Every branch that reads a named artifact ends here instead of coercing the
    missing text to `""`. A file over MAX_READ_BYTES, or one holding a NUL in
    its first SNIFF_BYTES, was never opened, and "0 pattern(s) with a required
    reviewer" or "tests not found" about it is a negative fact this tool cannot
    know. The same run's own `scope.unread` already names the path, so the two
    halves of one report contradicted each other.
    """

    return Finding(
        f"{md(relative)}: present, not read",
        f"{relative}:1",
        "unreadable, too large, or binary, so what it configures here is unknown",
    )


def _gitignored_row(relative: str) -> Finding:
    """The row for a config file that is on disk and not in the listing.

    `.mcp.json` and `.claude/settings.local.json` carry per-machine server and
    hook configuration and are commonly gitignored. Looking for them in the git
    listing alone made the report state an absolute -- "no tool servers are
    configured in this repository" -- about a file sitting in the checkout that
    the agent actually loads. They are read from disk, and the report says
    where they came from.
    """

    return Finding(
        f"{md(relative)}: present on disk, not checked in",
        f"{relative}:1",
        "the agent reads this file here and it is not in the listing, so what it configures is real on this "
        "machine and travels with nobody else",
    )


def inventory(root: Path, files: list[str], scan_out: Scan) -> list[Finding]:
    """Which agent-facing artifacts exist, and what each one does or does not enforce.

    The lookups run over `scan_out.all_files`, not over the `--max-files` slice:
    "CODEOWNERS: absent" read off a truncated listing is a false statement about
    a repository that has one, and §1's truncation note does not say the
    inventory may be wrong.
    """

    present = set(scan_out.all_files or files)
    found: list[Finding] = []

    def read(relative: str) -> str | None:
        return _record(scan_out, relative, _read(root, relative))

    # 1. Instruction files.
    #
    # Two bounds, because two things run away here: how many files one prefix
    # entry fans out over, and how many lines those files carry. AGENT_FILE_LIMIT
    # is the first; LINE_BUDGET is the second, spent across the whole step, and
    # the row below counts what was actually read rather than what the file cap
    # allowed.
    budget = LINE_BUDGET
    for name in _AGENT_FILES:
        matching = sorted(item for item in present if item == name or item.startswith(f"{name}/"))
        candidates = matching[:AGENT_FILE_LIMIT]
        opened: list[str] = []
        rows: list[Finding] = []
        for relative in candidates:
            if budget <= 0:
                break
            opened.append(relative)
            text = read(relative)
            shown = md(relative)
            if text is None:
                rows.append(_unread_row(relative))
                continue
            # Split once: the comprehension and both counts below walked the
            # same megabyte apart, which was three passes for one row.
            lines = text.splitlines()
            budget -= len(lines)
            forbidding = [
                number for number, line in enumerate(lines, start=1) if _FORBIDS.search(line) and _PATHISH.search(line)
            ]
            if forbidding:
                rows.append(
                    Finding(
                        f"{shown}: {len(text):,} bytes, {len(lines)} lines, "
                        f"{len(forbidding)} line(s) forbid something and name a path",
                        f"{relative}:{forbidding[0]}",
                        "prose an agent may follow; nothing here blocks a write, so it is guidance, not a guardrail",
                    )
                )
            else:
                rows.append(
                    Finding(
                        f"{shown}: {len(text):,} bytes, {len(lines)} lines, "
                        "no line both forbids something and names a path",
                        f"{relative}:1",
                        "an agent reading this learns no path is off limits, and writes wherever the task leads",
                    )
                )
        over = len(matching) - len(opened)
        if over > 0:
            found.append(
                Finding(
                    f"{md(name)}: {len(matching):,} file(s); the first {len(opened)} in sorted order were read",
                    f"{matching[0]}:1",
                    f"{over:,} more file(s) under this path were listed and not read, so what they forbid is unknown",
                )
            )
        if not matching:
            found.append(
                Finding(
                    f"{name}: absent",
                    "-",
                    "nothing written down here for an agent to follow, so every rule is folklore",
                )
            )
        found.extend(rows)

    # 2. Claude Code hooks, as this repository checks them in.
    #
    # Both files: Claude Code reads `settings.local.json` too and gitignores it,
    # so a repository whose blocking PreToolUse hook lives there was reported as
    # having no hook at all -- the false negative that matters, a report telling
    # a reader nothing stops a write when something does.
    for settings in SETTINGS_FILES:
        exists = settings in present or (root / settings).is_file()
        if exists and settings not in present:
            found.append(_gitignored_row(settings))
        text = read(settings) if exists else None
        if not exists:
            found.append(
                Finding(
                    f"{settings}: absent",
                    "-",
                    "no PreToolUse or PostToolUse hook is configured here; this tool reads the two settings "
                    "files in the checkout and nothing on the machine outside it",
                )
            )
            continue
        if text is None:
            found.append(_unread_row(settings))
            continue
        lines = _quoted_lines(text)
        parsed: object = None
        try:
            parsed = json.loads(text)
        except ValueError:
            # `continue`, because the rows below state what the file configures.
            # Without it a typo in `settings.json` produced "not valid JSON"
            # and then "no PreToolUse hook" about the same unparsed file.
            found.append(
                Finding(
                    f"{settings}: not valid JSON",
                    f"{settings}:1",
                    "the hook block cannot be read, so what it configures here is unknown",
                )
            )
            continue
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
            block_list = hooks.get(event)
            if block_list is not None and not isinstance(block_list, list):
                found.append(
                    Finding(
                        f"{settings}: the {event} block is not a list",
                        f"{settings}:1",
                        "the hook block cannot be read, so what it configures here is unknown",
                    )
                )
                block_list = None
            entries = [item for item in (block_list or []) if isinstance(item, dict)]
            if not entries:
                found.append(
                    Finding(
                        f"{settings}: no {event} hook",
                        _where(settings, lines, "hooks"),
                        "a tool call of this kind runs with nothing in front of it that this repository checks in",
                    )
                )
                continue
            # Matched on the matcher the file wrote, escaped only for display:
            # `md` turns `*` into `\*`, and a catch-all matcher read through the
            # escaper matches nothing.
            matchers = [str(item.get("matcher", "")) for item in entries]
            verdicts = [_matches_write(item) for item in matchers]
            writes = [item is True for item in verdicts if item is True]
            unknown = any(item is None for item in verdicts)
            # Quoted here rather than with `repr`, which escapes the backslash
            # `md` just added and hands a live `[` back to the reader.
            listed = ", ".join("'" + md(item, QUOTED_WIDTH) + "'" for item in matchers) or "unset"
            found.append(
                Finding(
                    f"{settings}: {len(entries)} {event} entr{'y' if len(entries) == 1 else 'ies'}, "
                    f"matcher(s) {listed}"
                    + (
                        ""
                        if writes
                        else "; one is not a regular expression this tool can evaluate"
                        if unknown
                        else "; none matches a write tool"
                    ),
                    _where(settings, lines, event),
                    "a write to any path is inspected by a hook this repository checks in; whether this hook "
                    "blocks is not checked, because nothing here was executed"
                    if writes
                    else "whether a write tool is inspected by this event was not checked, because this tool "
                    "could not evaluate the matcher"
                    if unknown
                    else "no write tool is inspected by this event in this repository's checked-in configuration",
                )
            )

    # 3. MCP servers.
    mcp_paths = (".mcp.json", "claude_desktop_config.json", ".claude/mcp.json")
    # `or ... .is_file()`, the same test the settings branch above uses: these
    # files carry per-machine server configuration and are commonly gitignored,
    # and one that is not in the listing is still the file the agent loads.
    mcp_present = [item for item in mcp_paths if item in present or (root / item).is_file()]
    mcp_unreadable: list[str] = []
    for relative in mcp_present:
        if relative not in present:
            found.append(_gitignored_row(relative))
        text = read(relative)
        if text is None:
            mcp_unreadable.append(relative)
            continue
        try:
            config = json.loads(text)
        except ValueError:
            mcp_unreadable.append(relative)
            found.append(Finding(f"{relative}: not valid JSON", f"{relative}:1", "the server list cannot be read"))
            continue
        if not isinstance(config, dict):
            mcp_unreadable.append(relative)
            found.append(Finding(f"{relative}: not a JSON object", f"{relative}:1", "the server list cannot be read"))
            continue
        _, servers = servers_of(config)
        if not isinstance(servers, dict):
            mcp_unreadable.append(relative)
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
        # Once per file, not once per server: see `_quoted_lines`.
        lines = _quoted_lines(text)
        listed_servers = sorted(servers.items())
        if len(listed_servers) > SERVER_ROWS:
            found.append(
                Finding(
                    f"{md(relative)}: {len(listed_servers):,} server(s) configured; the first {SERVER_ROWS} in "
                    "sorted order have a row below",
                    f"{relative}:1",
                    f"{len(listed_servers) - SERVER_ROWS:,} more server(s) are configured here and are not "
                    "described row by row",
                )
            )
            listed_servers = listed_servers[:SERVER_ROWS]
        for name, entry in listed_servers:
            where = _where(relative, lines, str(name))
            label = f"{relative}: MCP server '{md(str(name), QUOTED_WIDTH)}'"
            if not isinstance(entry, dict):
                found.append(
                    Finding(f"{label} is not a JSON object", where, "this entry configures nothing that can be read")
                )
                continue
            if "command" not in entry:
                target = md(str(entry.get("url") or entry.get("type") or "no command and no url"), QUOTED_WIDTH)
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
            line = " ".join([str(entry["command"])] + [str(item) for item in arguments]).strip()
            if len(line) > QUOTED_WIDTH:
                line = line[: QUOTED_WIDTH - 1] + "…"
            # `_code`, not `md` inside a hand-built span: a backslash is literal
            # inside a code span and a backtick closes it, so an `md`-escaped
            # command line broke the span and swallowed the rest of the row.
            command = _bar(_code(line))
            screened = _screened(entry["command"], arguments)
            found.append(
                Finding(
                    f"{label} runs {command}" + ("" if screened else "; no screen in the command line"),
                    where,
                    "the command it runs is one of the known screens (" + ", ".join(SCREENS) + "), so tool "
                    "output passes it before the agent sees it; whether it screens this server was not "
                    "checked, because nothing here was executed"
                    if screened
                    else "whatever this server returns reaches the agent's context unscreened",
                )
            )
    if not any("MCP server" in item.fact for item in found):
        if mcp_unreadable:
            found.append(
                Finding(
                    f"{', '.join(mcp_unreadable)}: present but unreadable, so whether any server is "
                    "configured here is unknown",
                    f"{mcp_unreadable[0]}:1",
                    "nothing here says what is configured, so nothing here says what is or is not screened",
                )
            )
        elif mcp_present:
            found.append(
                Finding(
                    f"{', '.join(mcp_present)}: no server is configured",
                    f"{mcp_present[0]}:1",
                    "no tool servers are configured in this repository, so none can be screened here",
                )
            )
        else:
            found.append(
                Finding(
                    f"no MCP server configuration found ({', '.join(mcp_paths)})",
                    "-",
                    "no tool servers are configured in this repository, so none can be screened here",
                )
            )

    # 4. pre-commit and git hooks.
    pre_commit = ".pre-commit-config.yaml"
    pre_commit_text = read(pre_commit) if pre_commit in present else None
    if pre_commit in present and pre_commit_text is None:
        found.append(_unread_row(pre_commit))
    elif pre_commit in present:
        ids = len(re.findall(r"^\s*- id:", pre_commit_text, re.M))
        found.append(
            Finding(
                f"{pre_commit}: present, {ids} hook id(s)",
                f"{pre_commit}:1",
                "these run on commit, only for a contributor who installed the framework",
            )
        )
    else:
        found.append(Finding(f"{pre_commit}: absent", "-", "no commit-time check runs on a contributor's machine"))
    # No row at all when this is not a git repository: "no installed hook
    # (samples only)" about a directory that does not exist, cited as
    # `.git/hooks:1`, is a statement about nothing.
    hooks_dir, escaped = _hooks_dir(root) if scan_out.is_git else (None, None)
    if escaped is not None:
        found.append(
            Finding(
                # The value is deliberately not printed. It is this checkout's
                # own `.git/config`, which is not checked in, so it can hold a
                # path out of the reader's home directory -- and this report is
                # a document they hand to someone else.
                "git hooks directory: `core.hooksPath` points outside this repository",
                "-",
                "the directory was not read, because it is on this machine and not in this repository; what runs "
                "at commit time here is unknown",
            )
        )
    elif hooks_dir is not None and hooks_dir.is_dir():
        # Installed means present *and* executable. git refuses to run a hook
        # without the execute bit -- "hook was ignored because it's not set as
        # executable" -- and the commit goes through, so counting one as
        # installed put "a commit is checked locally before it is made" in the
        # report about a commit nothing checked.
        live: list[str] = []
        inert: list[str] = []
        with contextlib.suppress(OSError):
            for item in sorted(hooks_dir.iterdir(), key=lambda entry: entry.name):
                if not item.is_file() or item.name.endswith(".sample"):
                    continue
                (live if os.access(item, os.X_OK) else inert).append(item.name)
        try:  # a linked worktree's hooks live in the main checkout, off this path
            label, where = str(hooks_dir.relative_to(root)), f"{hooks_dir.relative_to(root)}:1"
        except ValueError:
            label, where = "the hooks directory this worktree shares with its main checkout", "-"
        found.append(
            Finding(
                f"{md(label)}: "
                + (
                    ", ".join(md(item) for item in live)
                    if live
                    else "no executable hook"
                    if inert
                    else "no installed hook (samples only)"
                ),
                where,
                "a commit is checked locally before it is made" if live else "nothing is checked at commit time",
            )
        )
        if inert:
            found.append(
                Finding(
                    f"{md(label)}: {', '.join(md(item) for item in inert)} — present, not executable",
                    where,
                    "git ignores a hook file without the execute bit and makes the commit anyway, so this file "
                    "checks nothing",
                )
            )

    # 5. CODEOWNERS.
    owners_path = next(
        (item for item in ("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS") if item in present), None
    )
    if owners_path is None:
        found.append(
            Finding(
                "CODEOWNERS: absent",
                "-",
                "no path in this repository names a required reviewer; branch protection on the host was not read",
            )
        )
        scan_out.owned = ()
    elif (text := read(owners_path)) is None:
        found.append(_unread_row(owners_path))
        scan_out.owned = ()
    else:
        owned, unowned = _codeowners(text)
        # Deduped and capped here, once, rather than in the ranking: the file is
        # read up to MAX_READ_BYTES and every pattern costs a search per
        # category. The row says how many were tested when the cap bit.
        distinct = list(dict.fromkeys(owned))
        scan_out.owned = tuple(distinct[:OWNER_LIMIT])
        found.append(
            Finding(
                f"{owners_path}: {len(owned)} pattern(s) with a required reviewer"
                + (f", {len(unowned)} that name no owner" if unowned else "")
                + (
                    f"; the ranking tested the first {OWNER_LIMIT:,} distinct pattern(s)"
                    if len(distinct) > OWNER_LIMIT
                    else ""
                ),
                f"{owners_path}:1",
                "changes under an owned path need a named human, on the host, on a pull request; a pattern "
                "with no owner clears the ownership an earlier line gave"
                if owned
                else "no pattern here names an owner, so this file requires no reviewer anywhere",
            )
        )

    # 6. CI workflows.
    listed = sorted(
        item for item in present if item.startswith(".github/workflows/") and item.endswith((".yml", ".yaml"))
    )
    # Capped like the rule directory and the MCP table, and for the same reason:
    # files x lines with no bound on either factor. Both factors are bounded --
    # WORKFLOW_LIMIT files and LINE_BUDGET lines across them -- and the
    # remainder gets the row `.cursor/rules` already gets, so step 7 below never
    # says "not configured" about a workflow it did not open.
    capped = listed[:WORKFLOW_LIMIT]
    workflows: list[str] = []
    #: `_uncommented` once per workflow: step 6 and step 7 both want it, and it
    #: is the hottest loop in the scan (one `re.sub` per line per pass).
    uncommented: dict[str, list[str]] = {}
    rows: list[Finding] = []
    budget = LINE_BUDGET
    for relative in capped:
        if budget <= 0:
            break
        workflows.append(relative)
        text = read(relative)
        if text is None:
            rows.append(_unread_row(relative))
            continue
        # Split once, here: the comment stripper, the two YAML readers and the
        # line lookup below each split the same megabyte again.
        lines = text.splitlines()
        budget -= len(lines)
        # A comment is what a file says about itself, not what it runs:
        # "# we do NOT use pytest here" is not a workflow that runs tests.
        body = uncommented[relative] = _uncommented(lines)
        # And a `run:` value is the only thing in a workflow that is a command:
        # a step `name:`, an `if:` guard and an `env:` value are not.
        runs_tests = _TEST_RUNNER.search(_run_steps(body))
        on_pr = "pull_request" in _triggers(body)
        rows.append(
            Finding(
                f"{md(relative)}: "
                + ("a test runner is named in a run: step" if runs_tests else "no test runner in a run: step")
                + f", {'runs on pull requests' if on_pr else 'does not run on pull requests'}",
                _at(relative, lines, runs_tests.group(0) if runs_tests else "on"),
                # Hedged the way the secret-scanning row below is hedged, and
                # for the same reason: nothing here was executed, so a `run:`
                # step behind `if: false` reads exactly like one that runs.
                "a test runner is named here and this workflow runs on pull requests; whether it ran, and on "
                "what, was not checked, because nothing here was executed"
                if runs_tests and on_pr
                else "a change can reach review without this workflow having judged it",
            )
        )
    over = len(listed) - len(workflows)
    if over > 0:
        found.append(
            Finding(
                f".github/workflows: {len(listed):,} file(s); the first {len(workflows)} in sorted order were read",
                f"{listed[0]}:1",
                f"{over:,} more file(s) were listed and not read, so what they run is unknown",
            )
        )
    if not listed:
        found.append(
            Finding(
                ".github/workflows: absent",
                "-",
                "no GitHub Actions workflow is checked in here; CI configured elsewhere was not read",
            )
        )
    found.extend(rows)

    # 7. Secret scanning.
    scanners: list[str] = []
    # `read`, not `_read`: this loop opened two files -- `.gitleaks.toml` and
    # `.secrets.baseline` -- outside the one recorder, so §1's read list and the
    # JSON document's `scope.read` did not name a file the report cites.
    # The workflows past either workflow cap were listed and not read, so they
    # belong here rather than in a silence: a scanner named only in one of them
    # must not come out as "not configured".
    unscanned: list[str] = [item for item in listed if item not in set(workflows)]
    for relative in [*workflows, pre_commit, ".gitleaks.toml", ".secrets.baseline"]:
        if relative not in present:
            continue
        text = read(relative)
        if text is None:
            unscanned.append(relative)
            continue
        lines = uncommented.get(relative) or _uncommented(text.splitlines())
        hit = _SECRET_SCANNER.search("\n".join(lines))
        if hit:
            scanners.append(_at(relative, lines, hit.group(0)))
    unread_note = f"; {len(unscanned)} file(s) here were present and not read" if unscanned else ""
    if scanners:
        # "named in", not "configured": unlike step 6's test-runner row this is
        # a word search over the whole uncommented file, so a job id, a step
        # `name:`, an `if:` guard and an `env:` value all count. The fact column
        # says what was found; asserting a control from it is the reader's call,
        # and the consequence column says so.
        fact = f"secret scanning: named in {len(scanners)} place(s){unread_note}"
        consequence = (
            "a scanner is named in these files; whether it runs, and on what, was not checked, "
            "because nothing here was executed"
        )
    elif unscanned:
        fact = f"secret scanning: not named in the files that were read{unread_note}"
        consequence = (
            "one of the files a scanner would be named in was not read, so whether one is configured here is unknown"
        )
    else:
        fact = "secret scanning: not configured (no gitleaks, trufflehog or detect-secrets)"
        consequence = "a credential an agent pastes into a file is committed with everything else"
    found.append(Finding(fact, scanners[0] if scanners else "-", consequence))

    # 8. Lockfiles.
    locks = sorted(item for item in present if item.rsplit("/", 1)[-1] in LOCKFILES)
    found.append(
        Finding(
            "lockfiles: " + (", ".join(md(item) for item in locks) if locks else "none found"),
            f"{locks[0]}:1" if locks else "-",
            "a test run resolves the same dependencies twice"
            if locks
            else "no pinned dependency set, so a hook or a test run is not reproducible",
        )
    )

    # 9. Symlinks that leave the repository.
    # Symlink checks call lstat. Keep that sweep under the caller's listing cap;
    # a checkout with millions of ordinary files must not buy millions of
    # syscalls for this one finding.
    escaping = sorted(item for item in files if _escapes(root, item))
    if escaping:
        found.append(
            Finding(
                f"symlinks out of this repository: {len(escaping)} — " + ", ".join(md(item) for item in escaping[:4]),
                f"{escaping[0]}:1",
                "the target is on this machine and not in this repository; it was listed and not read",
            )
        )

    # 10. Test layout.
    tests = [item for item in present if TEST_PATH.search(item)]
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

    The directories come back most-churned first -- the count is how many paths
    in repair commits fell in each one -- because `scan` keeps only the first
    CHURN_GLOBS of them for the starter policy's write globs, and a cut in
    alphabetical order drops directories for their names.

    `git log --name-only -z` is read a record at a time and stopped at
    `max_paths` path entries: the commit cap bounds how far back this looks, and
    this one bounds how much any single commit can cost.

    `--no-renames` is what bounds the wall clock. Rename detection runs before
    git emits a commit's first byte, so neither the path cap nor killing the
    process can stop work git has already paid for: one commit renaming a
    hundred thousand files costs 18.6 seconds of `git log` with detection on and
    0.14 without, and the cap bit in both. It is also the more useful answer here, because this walk
    wants the paths a repair touched: a detected rename names only the new path,
    and without detection the churn set gets the old one too.

    `-z`, with `core.quotePath=false` on every git call, is what makes the paths
    here the same strings `git ls-files -z` gave the listing. Without it git
    C-quotes anything that is not pure ASCII, `caf\303\251/db/queries.py`
    became the starter policy's write glob, and the policy then dropped it as
    unpoliceable -- one emitted file carrying two spellings of one directory.
    """

    repairs: list[Repair] = []
    #: Counted, not collected: the starter policy carries the CHURN_GLOBS
    #: most-churned directories, and a set could only be cut alphabetically.
    churn: Counter[str] = Counter()
    seen = 0
    sha = subject = ""
    weight, categories, repairing = 1, set(), False

    def close() -> None:
        if repairing:
            repairs.append(Repair(sha, md(subject, QUOTED_WIDTH), weight, frozenset(categories)))

    with subprocess.Popen(
        # `%x01` marks a commit record: with `-z` the NUL is the separator, so it
        # cannot also be the marker.
        _argv(root, "log", "--no-merges", f"-n{limit}", "--no-renames", "--name-only", "-z", "--format=%x01%h%x1f%s"),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    ) as process:
        assert process.stdout is not None
        truncated = False
        for record in _records(process.stdout):
            if record.startswith(b"\x01"):
                close()
                head, _, rest = record[1:].partition(b"\x1f")
                sha, subject = head.decode("ascii", "replace"), _decode(rest)
                weight, categories = 1, set()
                repairing = bool(REPAIR_SUBJECT.search(subject))
                continue
            # git separates the commit record from the first path with a
            # newline that `-z` does not replace.
            name = record.lstrip(b"\n")
            if not name.strip():
                continue
            seen += 1
            if seen > max_paths:
                truncated = True
                break
            if not repairing:
                continue
            path = _text(name)
            if REGRESSION_TEST.search(path):
                weight = REGRESSION_WEIGHT
            categories |= {slug for slug, _, needles in CATEGORIES if _matches(path, needles)}
            glob = f"{path.rsplit('/', 1)[0]}/**" if "/" in path else path
            if len(churn) < CHURN_LIMIT or glob in churn:
                churn[glob] += 1
        close()
        if truncated:  # the log is longer than the cap; stop git rather than read the rest
            process.stdout.close()
            process.kill()
        if process.wait() != 0 and not truncated:
            return [], (), False
    # Most-churned first, ties broken by name: the cut that follows in `scan`
    # drops the directories repair commits touched least, not the ones whose
    # names sort last.
    return repairs, tuple(item for item, _ in sorted(churn.items(), key=lambda pair: (-pair[1], pair[0]))), truncated


def candidates(files: list[str], repairs: list[Repair], owned: tuple[str, ...]) -> list[Candidate]:
    """The invariant candidates, ranked. Candidates: a human confirms or replaces them.

    Score = the repair commits that touched these paths (a commit that also
    touched a regression test counts twice) + 2 if CODEOWNERS names one of them
    + 1 if the path heuristic matched at all. Ties break on the number of
    matching files -- all of them, not the eight `paths` carries as examples --
    then on the slug.
    """

    out: list[Candidate] = []
    for slug, noun, needles in CATEGORIES:
        matched = [item for item in files if _matches(item, needles)]
        if not matched:
            continue
        prefixes = sorted({_prefix(item, needles) for item in matched})
        evidence: list[str] = [
            f"path heuristic: {len(matched)} file(s) matching "
            + ", ".join(md(item) for item in prefixes)  # a path is repository-controlled text
        ]
        score = HEURISTIC_BASE
        touched = [item for item in repairs if slug in item.categories]
        if touched:
            score += sum(item.weight for item in touched)
            named = [f"{item.sha} {item.subject}" for item in touched]
            evidence.append(f"git history: {len(named)} repair commit(s) touched these paths — {'; '.join(named[:3])}")
        owns = _owned_here(owned, matched)
        if owns:
            score += CODEOWNERS_BONUS
            # The count and then the examples, the way the repair-commit line
            # above does it: three of twelve owned patterns read as all of them.
            evidence.append(
                f"CODEOWNERS: {len(owns)} pattern(s) already require a named reviewer — "
                + ", ".join(md(item, QUOTED_WIDTH) for item in owns[:3])
            )
        out.append(
            Candidate(
                slug=slug,
                rule=f"An agent does not write to {noun} without a human deciding first.",
                paths=tuple(sorted(matched)[:8]),
                matched=len(matched),
                prefixes=tuple(prefixes),
                evidence=tuple(evidence),
                score=score,
            )
        )
    out.sort(key=lambda item: (-item.score, -item.matched, item.slug))
    return out


def _owned_here(owned: tuple[str, ...], matched: list[str]) -> list[str]:
    """The CODEOWNERS patterns that name one of `matched`, in O(patterns + files).

    Two strings are built once per category and every pattern is one substring
    search over one of them. The loop this replaces asked `_matches` for every
    (pattern, file) pair, and a pattern that matches nothing -- the normal case
    -- paid the whole product: a 5,001-file repository with a 1 MiB CODEOWNERS
    took 92 seconds, and that comprehension was the entire runtime.

    A needle ending in `/` matches a run of whole path components, so it can
    only ever match inside the directory part; searching the distinct
    directories, each wrapped in slashes, is the same answer over a much smaller
    string. Any other needle matches anywhere in a path, so it searches the
    paths. Neither needle can contain a newline -- CODEOWNERS fields are split
    on whitespace -- so nothing matches across two entries.
    """

    paths = "\n".join(matched)
    directories = "\n".join(sorted({f"/{item.rsplit('/', 1)[0]}/" for item in matched if "/" in item}))
    out = []
    for pattern in owned:
        needle = pattern.lstrip("/").rstrip("*") or "/"
        here = f"/{needle}" in directories if needle.endswith("/") else needle in paths
        if here:
            out.append(pattern)
    return sorted(dict.fromkeys(out))


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
    files, all_files, truncated, is_git = list_files(root, max_files)
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
        all_files=all_files,
        total_files=len(all_files),
        truncated=truncated,
        max_files=max_files,
        is_git=is_git,
        languages=sorted(extensions.items(), key=lambda pair: (-pair[1], pair[0]))[:LANGUAGE_ROWS],
        extensions=len(extensions),
        total_bytes=total_bytes,
    )
    result.findings = inventory(root, files, result)
    repairs, churn, sampled = history(root)
    result.repairs = len(repairs)
    result.history_sampled = sampled
    result.churn = churn[:CHURN_GLOBS]
    result.churn_cut = len(churn) - len(result.churn)
    result.candidates = candidates(files, repairs, result.owned)
    return result
