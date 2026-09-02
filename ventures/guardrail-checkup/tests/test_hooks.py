"""The emitted hook is executed. A hook that has never run does not go on a stranger's screen."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from guardrail_checkup import checkup, emit, hook_script, one_line_test, settings_snippet
from guardrail_checkup._scan import _matches_write

EVIDENCE = Path(__file__).resolve().parent.parent / "docs" / "evidence" / "claude-code-hooks.txt"


@pytest.fixture(scope="module")
def emitted(fixture_repo: Path, tmp_path_factory) -> Path:
    _, composed = checkup(str(fixture_repo))
    directory = tmp_path_factory.mktemp("drafts")
    emit(composed.drafts, directory)
    return directory


def run_hook(script: Path, event: dict) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script)], input=json.dumps(event), capture_output=True, text=True, timeout=30
    )


def test_the_emitted_hook_blocks_a_write_under_the_protected_path(emitted: Path) -> None:
    done = run_hook(
        emitted / "hooks" / "protect-db.py",
        {"cwd": "/repo", "tool_name": "Write", "tool_input": {"file_path": "/repo/db/queries.py"}},
    )
    assert done.returncode == 2, done
    assert "BLOCKED: db/queries.py" in done.stderr
    assert done.stdout == ""


@pytest.mark.parametrize(
    "event",
    [
        {"cwd": "/repo", "tool_name": "Write", "tool_input": {"file_path": "/repo/app/handlers.py"}},
        {"cwd": "/repo", "tool_name": "Bash", "tool_input": {"command": "rm -rf ./build"}},
        {"cwd": "/repo", "tool_name": "Read", "tool_input": {"file_path": "/repo/db/queries.py"}},
        {"cwd": "/repo", "tool_name": "Edit", "tool_input": {}},
    ],
)
def test_the_emitted_hook_allows_everything_else(emitted: Path, event: dict) -> None:
    done = run_hook(emitted / "hooks" / "protect-db.py", event)
    assert done.returncode == 0, done.stderr


def test_the_emitted_hook_is_executable_and_starts_with_a_shebang(emitted: Path) -> None:
    script = emitted / "hooks" / "protect-db.py"
    assert script.stat().st_mode & 0o111
    assert script.read_text().startswith("#!/usr/bin/env python3\n")


def test_the_settings_snippet_is_the_shape_the_documentation_gives(emitted: Path) -> None:
    """Every key in the snippet is one the fetched hooks page names."""

    snippet = json.loads((emitted / "hooks" / "settings-db.json").read_text())
    assert snippet == settings_snippet("db")
    entry = snippet["hooks"]["PreToolUse"][0]
    assert entry["matcher"] == "Write|Edit|MultiEdit"
    assert entry["hooks"][0]["type"] == "command"
    assert entry["hooks"][0]["command"].startswith("${CLAUDE_PROJECT_DIR}/.claude/hooks/")
    page = EVIDENCE.read_text(encoding="utf-8")
    for key in ("PreToolUse", "matcher", "CLAUDE_PROJECT_DIR", "tool_name", "tool_input", "cwd"):
        assert key in page, key


def test_the_documented_exit_code_for_blocking_is_the_one_the_hook_uses() -> None:
    page = EVIDENCE.read_text(encoding="utf-8")
    assert "Blocks the tool call" in page
    assert "sys.exit(2)" in hook_script("db", ("db/",))


def test_the_hook_script_names_every_prefix_it_was_given() -> None:
    body = hook_script("payments", ("billing/", "payments/"))
    assert "PROTECTED = ('billing/', 'payments/')" in body


def test_the_one_line_test_fails_on_a_staged_violation_and_passes_on_a_clean_index(
    fixture_repo: Path, tmp_path: Path
) -> None:
    """The test line in the report is run, on a real index, in both directions."""

    from conftest import GIT_ENV, build_repo, git

    repository = build_repo(tmp_path / "repo")
    line = one_line_test(("db/",))
    assert re.search(r"^! git diff --cached --name-only \| grep -qE '\^\(db/\)'$", line)

    import os

    env = {**os.environ, **GIT_ENV}
    clean = subprocess.run(line, shell=True, cwd=repository, capture_output=True, env=env)
    assert clean.returncode == 0

    (repository / "db" / "queries.py").write_text("# staged change\n")
    git(repository, "add", "db/queries.py")
    dirty = subprocess.run(line, shell=True, cwd=repository, capture_output=True, env=env)
    assert dirty.returncode != 0


def test_the_catch_all_matcher_means_what_the_fetched_page_says_it_means() -> None:
    """The semantics and the source, in one place, so they cannot drift apart."""

    page = " ".join(EVIDENCE.read_text(encoding="utf-8").split())
    assert 'If you omit the matcher or use "*" , the group activates on every occurrence of the event.' in page
    for matcher in ("", "*", " * ", "Write", "Edit|Bash", "MultiEdit", "NotebookEdit"):
        assert _matches_write(matcher), matcher
    for matcher in ("Bash", "Read", "WebFetch", "Task"):
        assert not _matches_write(matcher), matcher


#: One matcher per evaluation mode the fetched page names, and the verdict each
#: one must get. The substring test this replaced was wrong in both directions:
#: `.*`, `^Notebook` and `Bash|.*` all catch a write tool and were reported as
#: catching none -- the false negative that tells a reader nothing inspects a
#: write when something does -- while `WriteLog` and `mcp__notes__write_note`
#: are exact matchers naming one tool that is not a write tool and were reported
#: as inspecting a write to any path.
MATCHERS = [
    ("*", True, "match all"),
    ("", True, "match all"),
    ("   ", True, "match all"),
    ("Edit", True, "exact"),
    ("Edit|Write", True, "exact list, | separated"),
    ("Edit, Write", True, "exact list, comma separated"),
    ("Bash", False, "exact, not a write tool"),
    ("WriteLog", False, "exact, not a write tool"),
    ("mcp__notes__write_note", False, "exact, not a write tool"),
    ("code-reviewer", False, "exact, an agent type"),
    (".*", True, "regular expression, matches every name"),
    ("^Notebook", True, "regular expression, matches NotebookEdit"),
    ("Bash|.*", True, "regular expression, the alternation matches every name"),
    ("^Bash$", False, "regular expression, anchored on a tool that does not write"),
    ("mcp__memory__.*", False, "regular expression, matches no core write tool"),
    # JavaScript spells a named group `(?<x>...)`; Python spells it `(?P<x>...)`
    # and rejects the other. `(?<x>Write)` does catch `Write`, and answering
    # "no write tool is inspected" about it is the false negative that tells a
    # reader nothing stops a write when something does.
    ("(?<x>Write)", True, "regular expression, a JavaScript named group"),
    ("(?<!Not)Write", True, "regular expression, a lookbehind both dialects share"),
    ("[unclosed", None, "not a regular expression this tool can evaluate"),
]


@pytest.mark.parametrize("matcher,expected,mode", MATCHERS, ids=[item[2] + " " + item[0][:14] for item in MATCHERS])
def test_a_matcher_is_evaluated_the_three_ways_the_fetched_page_names(matcher: str, expected: bool, mode: str) -> None:
    """The three modes, cited: docs/evidence/claude-code-hooks.txt:145-146."""

    page = " ".join(EVIDENCE.read_text(encoding="utf-8").split())
    assert "Only letters, digits, _ , - , spaces, , , and | Exact string, or list of exact strings" in page
    assert "Contains any other character JavaScript regular expression, unanchored" in page
    assert _matches_write(matcher) is expected, (matcher, mode)


def test_a_matcher_that_catches_a_write_tool_is_reported_as_inspecting_a_write(tmp_path: Path) -> None:
    """The row a reader acts on, over the two matchers the substring test got backwards."""

    from conftest import build_repo

    from guardrail_checkup import scan

    def rows(matcher: str) -> str:
        repository = build_repo(tmp_path / matcher.replace("*", "star").replace(".", "dot"))
        (repository / ".claude").mkdir()
        (repository / ".claude" / "settings.json").write_text(
            json.dumps({"hooks": {"PreToolUse": [{"matcher": matcher, "hooks": []}]}})
        )
        return "\n".join(item.fact + " | " + item.consequence for item in scan(str(repository), 20_000).findings)

    caught = rows(".*")
    assert "none matches a write tool" not in caught
    assert "a write to any path is inspected by a hook this repository checks in" in caught

    missed = rows("WriteLog")
    assert "none matches a write tool" in missed
    assert "a write to any path is inspected by a hook this repository checks in" not in missed


#: Path text that is shell syntax. `re.escape` makes a filename safe for grep
#: and does nothing about `sh`, which is the question that matters: the report
#: offers the one-liner to a reader to paste into a shell.
HOSTILE_PREFIXES = (
    "stripe';id>SENTINEL;echo'.py",
    "db/$(id>SENTINEL)/",
    "db/`id>SENTINEL`/",
    "db/;id>SENTINEL;x/",
    'db/"$(id>SENTINEL)"/',
)


@pytest.mark.parametrize("prefix", HOSTILE_PREFIXES)
def test_the_one_line_test_runs_no_command_a_filename_smuggled_into_it(prefix: str, tmp_path: Path) -> None:
    """A hostile checkout may not get code execution on the reviewer's machine."""

    import os

    from conftest import GIT_ENV, build_repo

    repository = build_repo(tmp_path / "repo")
    sentinel = tmp_path / "SENTINEL"
    line = one_line_test((prefix.replace("SENTINEL", str(sentinel)),))
    done = subprocess.run(line, shell=True, cwd=repository, capture_output=True, env={**os.environ, **GIT_ENV})

    assert not sentinel.exists(), f"the emitted line ran a command from a filename: {line}"
    assert done.returncode == 0, done.stderr  # nothing staged matches, so the test passes
    assert done.stderr == b"", done.stderr


def unfence(span: str) -> str:
    """The text inside an inline code span, whatever the width of its fence."""

    span = span.strip()
    fence = re.match(r"`+", span).group(0)
    # `_cell` escapes the table delimiter; GFM renders `\|` as `|`.
    return span[len(fence) : -len(fence)].strip().replace("\\|", "|")


def shell_lines(body: str) -> list[str]:
    """Every command the report offers the reader to paste into a shell."""

    tests = [unfence(line.split("): ", 1)[1]) for line in body.splitlines() if line.startswith("- **Test** (")]
    falsifiers = [
        unfence(line.strip("| ").split(" | ")[-1]) for line in body.splitlines() if line.startswith("| \u201c")
    ]
    return tests + falsifiers


def test_every_repository_derived_token_in_the_reports_shell_lines_is_quoted(tmp_path: Path) -> None:
    """\u00a72's falsifier commands and \u00a73's test line, over a repository of shell metacharacters."""

    import os

    from conftest import GIT_ENV

    from guardrail_checkup import compose, render_markdown, scan

    repository = tmp_path / "hostile"
    sentinel = repository / "SENTINEL"  # relative: the shell lines run with cwd=repository
    # The metacharacters are *inside* the repository, which is where a path the
    # report interpolates comes from.
    vendor = repository / "a;id>SENTINEL;x"
    (vendor / "db").mkdir(parents=True)
    (vendor / "db" / "queries.py").write_text("x = 1\n")
    (vendor / "uv.lock").write_text("# lock\n")
    (vendor / "pyproject.toml").write_text("[tool.ruff]\n")
    (vendor / "tests").mkdir()
    (vendor / "tests" / "test_x.py").write_text("def test_x():\n    assert True\n")

    result = scan(str(repository), 20_000)
    body = render_markdown(
        result,
        compose(result, "p.json"),
        "cmd",
        {"guardrail-checkup": "0", "agent-plan-lint": "0", "egresswall": "0"},
        None,
        "2026-08-31",
    )

    lines = shell_lines(body)
    assert len(lines) >= 3, lines
    assert any("uv.lock" in item for item in lines), lines
    for line in lines:
        subprocess.run(line, shell=True, cwd=repository, capture_output=True, env={**os.environ, **GIT_ENV})
        assert not sentinel.exists(), line


def test_the_settings_comment_counts_the_hook_sources_the_evidence_file_lists() -> None:
    """The comment beside SETTINGS_FILES said Claude Code reads four sources.

    Both places it cited list five. `/hooks` labels every hook with one of five
    sources, and the same page's location table adds a managed-policy tier the
    comment did not mention either -- while §5 of every rendered report already
    named the enterprise policy. A comment in `src/` is read by no test, which
    is the eighth class `CONTRIBUTING.md` declares uncovered; this closes the
    one that decides which two of those sources this tool can read at all.
    """

    source = (Path(__file__).resolve().parent.parent / "src" / "guardrail_checkup" / "_scan.py").read_text(
        encoding="utf-8"
    )
    comment = source.split("\nSETTINGS_FILES = ", 1)[0].rsplit("\n\n", 1)[1]
    lines = EVIDENCE.read_text(encoding="utf-8").splitlines()
    # The five source labels the menu lists, off the file rather than off a copy
    # of it: the count in the comment is the length of this list.
    listed = [item.strip() for item in lines[387:392]]

    assert len(listed) == 5
    assert "`/hooks` menu labels five hook sources" in comment.replace("\n#:", "").replace("#:", "")
    # The page's apostrophe is U+2019 and the comment's is an ASCII one, which
    # is the only difference a quotation of these five lines is allowed to have.
    curly = "\u2019"
    flat = " ".join(item.strip("#: ") for item in comment.splitlines()).replace(curly, "'")
    for item in listed:
        assert item.replace(curly, "'") in flat, item
    assert "Managed policy settings" in lines[124]
    assert "line 125" in flat
