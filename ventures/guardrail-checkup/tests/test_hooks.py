"""The emitted hook is executed. A hook that has never run does not go on a stranger's screen."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from guardrail_checkup import checkup, emit, hook_script, one_line_test, settings_snippet

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
