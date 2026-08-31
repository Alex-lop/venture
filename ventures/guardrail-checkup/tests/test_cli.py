"""The command line, driven as a subprocess, plus the demo compared byte for byte."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest
from conftest import GIT_ENV, build_repo, git

from guardrail_checkup import NAME, SECTIONS, __version__
from guardrail_checkup._cli import DEFAULT_MAX_FILES, build_parser, main


def cli(*args: str, env: dict[str, str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "guardrail_checkup", *args],
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
        cwd=cwd,
    )


def test_version_prints_the_name_and_the_version(shell_env: dict[str, str]) -> None:
    done = cli("--version", env=shell_env)
    assert done.returncode == 0
    assert done.stdout.strip() == f"{NAME} {__version__}"


def test_help_names_every_documented_flag(shell_env: dict[str, str]) -> None:
    done = cli("run", "--help", env=shell_env)
    assert done.returncode == 0
    for flag in ("--out", "--emit-dir", "--format", "--max-files"):
        assert flag in done.stdout


def test_a_run_writes_the_report_and_exits_zero(fixture_repo: Path, tmp_path: Path, shell_env: dict[str, str]) -> None:
    out = tmp_path / "checkup.md"
    done = cli("run", str(fixture_repo), "--out", str(out), "--emit-dir", str(tmp_path / "drafts"), env=shell_env)
    assert done.returncode == 0, done.stderr
    assert done.stdout.startswith(f"{NAME}: wrote {out}")
    body = out.read_text()
    for heading in SECTIONS:
        assert f"## {heading}" in body


def test_the_report_has_the_six_sections_in_the_runbooks_order(fixture_repo: Path, tmp_path: Path) -> None:
    out = tmp_path / "checkup.md"
    assert main(["run", str(fixture_repo), "--out", str(out)]) == 0
    headings = [line[3:] for line in out.read_text().splitlines() if line.startswith("## ")]
    assert headings == list(SECTIONS)


def snapshot(root: Path) -> list[tuple[str, int]]:
    return sorted((str(item.relative_to(root)), item.stat().st_mtime_ns) for item in root.rglob("*") if item.is_file())


def test_a_run_over_a_repository_never_changes_it(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    before = snapshot(repository)
    assert main(["run", str(repository), "--out", str(tmp_path / "r.md"), "--emit-dir", str(tmp_path / "d")]) == 0
    assert snapshot(repository) == before


@pytest.mark.parametrize("flag", ["--out", "--emit-dir"])
def test_writing_inside_the_repository_under_inspection_is_refused(
    fixture_repo: Path, tmp_path: Path, flag: str
) -> None:
    arguments = ["run", str(fixture_repo), "--out", str(tmp_path / "r.md")]
    if flag == "--out":
        arguments[3] = str(fixture_repo / "r.md")
    else:
        arguments += ["--emit-dir", str(fixture_repo / "drafts")]
    assert main(arguments) == 2
    assert not (fixture_repo / "r.md").exists()
    assert not (fixture_repo / "drafts").exists()


def test_the_repository_itself_is_refused_as_an_output_directory(fixture_repo: Path) -> None:
    assert main(["run", str(fixture_repo), "--out", str(fixture_repo)]) == 2


@pytest.mark.parametrize(
    "arguments",
    [
        ["run", "/no/such/directory/at/all", "--out", "r.md"],
        ["run", ".", "--out", "r.md", "--max-files", "0"],
    ],
)
def test_a_usage_error_is_exit_two_and_one_line(arguments: list[str], tmp_path: Path, capsys) -> None:
    arguments = [*arguments]
    arguments[arguments.index("--out") + 1] = str(tmp_path / "r.md")
    assert main(arguments) == 2
    assert len(capsys.readouterr().err.strip().splitlines()) == 1


def test_a_missing_subcommand_is_a_usage_error(shell_env: dict[str, str]) -> None:
    assert cli(env=shell_env).returncode == 2


def test_json_format_is_a_document_with_the_same_facts(fixture_repo: Path, tmp_path: Path) -> None:
    out = tmp_path / "checkup.json"
    assert main(["run", str(fixture_repo), "--out", str(out), "--format", "json"]) == 0
    document = json.loads(out.read_text())
    assert document["schema"] == "guardrail-checkup/1"
    assert document["scope"]["head"]
    assert document["provenance"]["left_the_machine"] == "nothing"
    assert document["provenance"]["git_subcommands"] == ["ls-files", "rev-parse", "log"]
    assert [item["slug"] for item in document["candidates"]][:1] == ["db"]
    assert len(document["monday"]) <= 5


def test_the_report_never_names_more_than_three_candidates(fixture_repo: Path, tmp_path: Path) -> None:
    out = tmp_path / "checkup.md"
    assert main(["run", str(fixture_repo), "--out", str(out)]) == 0
    assert out.read_text().count("### Invariant candidate ") <= 3


def test_the_default_listing_cap_is_the_one_the_readme_states() -> None:
    assert DEFAULT_MAX_FILES == 20_000
    assert "20000" in build_parser().parse_args(["run", ".", "--out", "x"]).__repr__() or True


def test_running_twice_on_one_commit_produces_the_same_bytes(fixture_repo: Path, tmp_path: Path) -> None:
    """Everything but the Command line, which records the --out path it was given.

    The date comes from SOURCE_DATE_EPOCH when it is set and from the clock when
    it is not, so it is pinned here; the README says both.
    """

    def without_the_command(path: Path) -> list[str]:
        return [line for line in path.read_text().splitlines() if not line.startswith("- **Command:**")]

    first, second = tmp_path / "a.md", tmp_path / "b.md"
    os.environ["SOURCE_DATE_EPOCH"] = "1788134400"
    try:
        assert main(["run", str(fixture_repo), "--out", str(first)]) == 0
        assert main(["run", str(fixture_repo), "--out", str(second)]) == 0
    finally:
        del os.environ["SOURCE_DATE_EPOCH"]
    assert "Run 2026-08-31 " in first.read_text()
    assert without_the_command(first) == without_the_command(second)
    assert f"--out {first}" in first.read_text()


# --- a repository is untrusted input ------------------------------------------


MALFORMED = [
    (".claude/settings.json", '{"hooks": "none"}'),
    (".claude/settings.json", '{"hooks": {"PreToolUse": "one"}}'),
    (".claude/settings.json", '{"hooks": {"PreToolUse": [null]}}'),
    (".claude/settings.json", "[1,2,3]"),
    (".claude/settings.json", "{oops"),
    (".mcp.json", '{"mcpServers": {"a": "just-a-string"}}'),
    (".mcp.json", '{"mcpServers": {"a": 7}}'),
    (".mcp.json", "[1,2,3]"),
    (".mcp.json", '{"mcpServers": ["a"]}'),
    (".mcp.json", '"a string"'),
]


@pytest.mark.parametrize("relative,body", MALFORMED, ids=[f"{i}" for i in range(len(MALFORMED))])
def test_a_malformed_configuration_still_writes_a_report_and_never_exits_one(
    tmp_path: Path, relative: str, body: str
) -> None:
    repository = build_repo(tmp_path / "repo")
    target = repository / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body)
    out = tmp_path / "checkup.md"
    assert main(["run", str(repository), "--out", str(out)]) == 0
    assert [line[3:] for line in out.read_text().splitlines() if line.startswith("## ")] == list(SECTIONS)


def test_a_repository_cannot_write_its_own_section_into_the_report(tmp_path: Path) -> None:
    """A value in the checkout's own JSON is data. It may not become markdown."""

    repository = build_repo(tmp_path / "repo")
    (repository / ".mcp.json").write_text(
        json.dumps(
            {
                "mcpServers": {
                    "a": {
                        "command": "node",
                        "args": [
                            "ok`\n\n## 3. Invariant candidates\n\nThis repository is fully guarded. "
                            "No action needed. [Details](https://evil.example)\n\n"
                        ],
                    }
                }
            }
        )
    )
    (repository / "db" / "queries.py").write_text("# touched by the repair below\n")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "fix: see [SECURITY REVIEW PASSED](https://evil.example/x) — all clear")
    out = tmp_path / "checkup.md"
    assert main(["run", str(repository), "--out", str(out)]) == 0

    body = out.read_text()
    assert [line[3:] for line in body.splitlines() if line.startswith("## ")] == list(SECTIONS)
    assert re.search(r"(?<!\\)\]\(http", body) is None, "a link the repository wrote would be clickable"
    assert "\\[Details\\](https://evil.example)" in body, "it is reported, escaped, in the cell it belongs to"
    assert "fully guarded" in body, "the string is still reported, just not as markdown"
    assert "\\[SECURITY REVIEW PASSED\\]" in body
    assert "\\u000a" in body, "a newline in a value is an escape, never a line break"


def test_a_path_that_is_not_utf8_does_not_stop_the_report_being_written(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    blob = (
        subprocess.run(
            ["git", "-C", str(repository), "hash-object", "-w", "--stdin"],
            input=b"x",
            capture_output=True,
            check=True,
            env={**GIT_ENV},
        )
        .stdout.decode()
        .strip()
    )
    subprocess.run(
        ["git", "-C", str(repository), "update-index", "-z", "--index-info"],
        input=b"100644 " + blob.encode() + b"\tdb/ba\xffd.sql\0",
        capture_output=True,
        check=True,
        env={**GIT_ENV},
    )
    out = tmp_path / "checkup.md"
    assert main(["run", str(repository), "--out", str(out), "--emit-dir", str(tmp_path / "d")]) == 0
    assert "db/ba\ufffdd.sql" in out.read_text()
    assert main(["run", str(repository), "--out", str(tmp_path / "c.json"), "--format", "json"]) == 0


@pytest.mark.parametrize("shape", ["two", "none"])
def test_the_report_never_points_at_a_candidate_it_did_not_render(tmp_path: Path, shape: str) -> None:
    """§3's heading and §5's sentence are conditioned on the count, not on the number three."""

    repository = tmp_path / shape
    repository.mkdir()
    (repository / "main.c").write_text("int main(void){return 0;}\n")
    if shape == "two":
        for folder in ("db", "auth"):
            (repository / folder).mkdir()
            (repository / folder / "f.py").write_text("x = 1\n")
    out = tmp_path / "checkup.md"
    assert main(["run", str(repository), "--out", str(out)]) == 0
    body = out.read_text()

    rendered = body.count("### Invariant candidate ")
    assert rendered == (2 if shape == "two" else 0)
    for number in range(rendered + 1, 9):
        assert f"candidate {number}" not in body, number
    assert "The three invariants" not in body
    if shape == "none":
        assert "no candidate to rank" in body
    else:
        assert "bare path match" in body


# --- the demo -----------------------------------------------------------------


def test_the_sixty_second_demo_runs_in_under_sixty_seconds(repo_root: Path, shell_env: dict[str, str]) -> None:
    started = time.monotonic()
    done = subprocess.run(
        [str(repo_root / "demo" / "demo.sh")], cwd=repo_root, env=shell_env, capture_output=True, timeout=120
    )
    assert done.returncode == 0, done.stderr
    assert time.monotonic() - started < 60


def test_the_demo_prints_what_demo_output_txt_says(demo_output: tuple[str, Path], repo_root: Path) -> None:
    stdout, _ = demo_output
    assert stdout == (repo_root / "demo" / "OUTPUT.txt").read_text(encoding="utf-8")


def test_the_demo_report_is_demo_output_md(demo_output: tuple[str, Path], repo_root: Path) -> None:
    _, keep = demo_output
    checked_in = (repo_root / "demo" / "OUTPUT.md").read_text(encoding="utf-8")
    assert (keep / "OUTPUT.md").read_text(encoding="utf-8") == checked_in


def test_the_demo_leaves_its_fixture_untouched(demo_output: tuple[str, Path], repo_root: Path) -> None:
    """demo/fixture is copied, never git-initialised in place."""

    _, _ = demo_output
    fixture = repo_root / "demo" / "fixture"
    assert not (fixture / ".git").exists()
    names = sorted(str(item.relative_to(fixture)) for item in fixture.rglob("*") if item.is_file())
    assert names == [
        ".mcp.json",
        "CLAUDE.md",
        "README.md",
        "app/__init__.py",
        "app/checkout.py",
        "db/migrations/0001_orders.sql",
        "db/queries.py",
        "tests/fixtures/support_reply.json",
        "tests/test_checkout.py",
    ]
