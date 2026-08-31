"""The command line, driven as a subprocess, plus the demo compared byte for byte."""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

import pytest
from conftest import FENCE, GIT_ENV, build_repo, git

from guardrail_checkup import NAME, SECTIONS, __version__
from guardrail_checkup._cli import DEFAULT_MAX_FILES, build_parser, main

#: An inline code span, however wide its fence -- the same expression
#: tests/test_scan.py uses.
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)*?\1", re.S)


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


@pytest.mark.parametrize("sink", ["true", "head -1"])
def test_a_reader_that_closes_the_pipe_is_still_exit_zero_with_the_report_written(
    sink: str, fixture_repo: Path, tmp_path: Path, shell_env: dict[str, str]
) -> None:
    """`guardrail-checkup run . --out R.md | head` exited 120 on a run that worked.

    The summary line is buffered, so the write survived `main` and failed in
    CPython's shutdown flush -- past every guard in `_cli`, printing a
    `BrokenPipeError` traceback to stderr and exiting 120. The report was on
    disk each time. A CI step that pipes this tool into anything that reads a
    few lines then failed on a run whose report was written, which is the one
    thing the documented exit status promises cannot happen.
    """

    out = tmp_path / f"r{abs(hash(sink))}.md"
    command = (
        f"{shlex.quote(sys.executable)} -m guardrail_checkup run {shlex.quote(str(fixture_repo))} "
        f"--out {shlex.quote(str(out))} | {sink}"
    )
    done = subprocess.run(
        ["bash", "-o", "pipefail", "-c", command], capture_output=True, text=True, timeout=300, env=shell_env
    )

    assert done.returncode == 0, (done.returncode, done.stderr)
    assert done.stderr == "", done.stderr
    assert out.read_text(encoding="utf-8").startswith("# Agent guardrail checkup")


def test_the_report_is_written_and_the_status_is_zero_with_stdout_closed(
    fixture_repo: Path, tmp_path: Path, shell_env: dict[str, str]
) -> None:
    """The same contract with no stdout at all, which is the other way to lose it."""

    out = tmp_path / "closed.md"
    command = (
        f"{shlex.quote(sys.executable)} -m guardrail_checkup run {shlex.quote(str(fixture_repo))} "
        f"--out {shlex.quote(str(out))} 1>&-"
    )
    done = subprocess.run(["bash", "-c", command], capture_output=True, text=True, timeout=300, env=shell_env)

    assert done.returncode == 0, (done.returncode, done.stderr)
    assert done.stderr == "", done.stderr
    assert out.read_text(encoding="utf-8").startswith("# Agent guardrail checkup")


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
    """The constant, the parser's default and the help text the README quotes."""

    run = next(iter(build_parser()._subparsers._group_actions)).choices["run"]  # type: ignore[union-attr]
    assert DEFAULT_MAX_FILES == 20_000
    assert run.get_default("max_files") == DEFAULT_MAX_FILES
    assert str(DEFAULT_MAX_FILES) in run.format_help()


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
    # Outside a code span: the command line is rendered *inside* one, where a
    # `](http` is inert, and a `<img>` and a `##` are too.
    outside = CODE_SPAN.sub("", FENCE.sub("", body))
    assert re.search(r"(?<!\\)\]\(http", outside) is None, "a link the repository wrote would be clickable"
    assert "[Details](https://evil.example)" in body, "it is reported, inert, in the cell it belongs to"
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

    # §5 may not single one out either: it is the section that says what this
    # file does not know, and naming a candidate there is a judgement about which
    # one matters. The sentence used to index the list by its length.
    section = body.split(f"## {SECTIONS[4]}")[1].split("## ")[0]
    assert re.search(r"(?i)candidate \d", section) is None, section
    if shape == "none":
        assert "no candidate to rank" in body
    else:
        assert "bare path match" in body


def test_the_monday_list_names_posttooluse_only_when_a_posttooluse_hook_exists(tmp_path: Path) -> None:
    """The branch fired on "no PreToolUse hook" and asserted a fact it never checked.

    A permissions-only settings file -- the common case -- was told that today
    only `PostToolUse` is wired, contradicted by the inventory table two
    sections above it in the same report.
    """

    repository = build_repo(tmp_path / "repo")
    (repository / ".claude").mkdir()
    (repository / ".claude" / "settings.json").write_text('{"permissions": {"allow": ["Bash(ls:*)"]}}')
    out = tmp_path / "none.md"
    assert main(["run", str(repository), "--out", str(out)]) == 0
    body = out.read_text()

    assert "no PreToolUse hook" in body and "no PostToolUse hook" in body
    assert "PostToolUse" not in body.split(f"## {SECTIONS[3]}")[1].split("## ")[0]
    assert "wires no hook of either kind" in body

    (repository / ".claude" / "settings.json").write_text(
        '{"hooks": {"PostToolUse": [{"matcher": "Write", "hooks": [{"type": "command", "command": "log.py"}]}]}}'
    )
    assert main(["run", str(repository), "--out", str(out)]) == 0
    monday = out.read_text().split(f"## {SECTIONS[3]}")[1].split("## ")[0]
    assert "is a `PostToolUse` one, and it runs after the write" in monday


def test_the_monday_list_without_an_emit_dir_names_a_path_and_not_a_phrase(fixture_repo: Path, tmp_path: Path) -> None:
    """The fallback used to be concatenated into a path inside a code span."""

    out = tmp_path / "checkup.md"
    assert main(["run", str(fixture_repo), "--out", str(out)]) == 0
    monday = out.read_text().split(f"## {SECTIONS[3]}")[1].split("## ")[0]

    assert "the directory you pass to --emit-dir/hooks" not in monday
    assert "`DIR/hooks/protect-db.py`" in monday
    assert "Re-run with `--emit-dir DIR` to write it; this run wrote no draft." in monday

    assert main(["run", str(fixture_repo), "--out", str(out), "--emit-dir", str(tmp_path / "d")]) == 0
    monday = out.read_text().split(f"## {SECTIONS[3]}")[1].split("## ")[0]
    assert f"`{tmp_path / 'd'}/hooks/protect-db.py`" in monday
    assert "Re-run with" not in monday


@pytest.mark.parametrize("flag", ["--out", "--emit-dir"])
def test_a_hard_link_into_the_repository_is_refused_like_a_path_inside_it(
    fixture_repo: Path, tmp_path: Path, flag: str
) -> None:
    """`_outside` compared resolved paths, and a hard link resolves to itself.

    A second name for a file in the repository is outside it by every path test
    and is the same bytes, so the tool overwrote a file inside the repository it
    had promised to leave alone.
    """

    keep = fixture_repo / "app" / "checkout.py"
    before = keep.read_text()
    outside = tmp_path / "out"
    outside.mkdir()
    target = outside / ("report.md" if flag == "--out" else "starter-policy.json")
    os.link(keep, target)

    arguments = ["run", str(fixture_repo), "--out", str(outside / "r.md")]
    if flag == "--out":
        arguments[3] = str(target)
    else:
        arguments += ["--emit-dir", str(outside)]

    assert main(arguments) == 2
    assert keep.read_text() == before


def test_the_last_monday_item_names_the_instruction_file(tmp_path: Path) -> None:
    """Every Monday item names a file; this one said "your agent instruction file"."""

    repository = tmp_path / "repo"
    (repository / "db").mkdir(parents=True)
    (repository / "db" / "queries.py").write_text("x = 1\n")
    (repository / "CLAUDE.md").write_text("Write good code. Ask when you are unsure.\n")
    out = tmp_path / "checkup.md"

    assert main(["run", str(repository), "--out", str(out)]) == 0
    monday = out.read_text().split(f"## {SECTIONS[3]}")[1].split("## ")[0]

    assert "your agent instruction file" not in monday
    assert "Add one line to `CLAUDE.md` naming the paths in §3" in monday


@pytest.mark.parametrize("flag", ["--out", "--emit-dir"])
def test_a_symlink_into_the_repository_is_refused_like_a_path_inside_it(
    fixture_repo: Path, tmp_path: Path, flag: str
) -> None:
    """The sibling hole to the hard link, and the one `write_text` follows.

    `_refuse` compared the joined path lexically, so `--emit-dir drafts` with
    `drafts/starter-policy.json` a symlink to `<repo>/CLAUDE.md` was outside the
    repository by every comparison, exited 0, and left the checkout modified
    while §6 still said "It wrote no file inside the repository it read."
    """

    keep = fixture_repo / "CLAUDE.md"
    before = keep.read_text()
    outside = tmp_path / "out"
    outside.mkdir()
    target = outside / ("report.md" if flag == "--out" else "starter-policy.json")
    target.symlink_to(keep)

    arguments = ["run", str(fixture_repo), "--out", str(outside / "r.md")]
    if flag == "--out":
        arguments[3] = str(target)
    else:
        arguments += ["--emit-dir", str(outside)]

    assert main(arguments) == 2
    assert keep.read_text() == before


def test_a_symlinked_emit_directory_that_lands_in_the_repository_is_refused(fixture_repo: Path, tmp_path: Path) -> None:
    """The nested draft: `drafts/hooks` a link to the checkout is the same hole."""

    outside = tmp_path / "out"
    outside.mkdir()
    (outside / "hooks").symlink_to(fixture_repo / "db", target_is_directory=True)
    before = sorted(item.name for item in (fixture_repo / "db").iterdir())

    assert main(["run", str(fixture_repo), "--out", str(tmp_path / "r.md"), "--emit-dir", str(outside)]) == 2
    assert sorted(item.name for item in (fixture_repo / "db").iterdir()) == before


def test_a_directory_name_cannot_write_its_own_heading_into_the_report(tmp_path: Path) -> None:
    """A newline in a directory name is legal, and a hostile archive creates one."""

    repository = tmp_path / "evil\n## Approved by security ` "
    (repository / "db").mkdir(parents=True)
    (repository / "db" / "a.py").write_text("x = 1\n")
    out = tmp_path / "checkup.md"
    assert main(["run", str(repository), "--out", str(out)]) == 0
    body = out.read_text()

    assert [line[3:] for line in body.splitlines() if line.startswith("## ")] == list(SECTIONS)
    assert "\n## Approved by security" not in body
    assert "\\u000a" in body.splitlines()[0], body.splitlines()[0]
    assert "\\u000a" in body.splitlines()[2], body.splitlines()[2]


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


def test_no_rendered_report_carries_a_readiness_score_a_grade_or_a_percentage(
    fixture_repo: Path, tmp_path: Path
) -> None:
    """What the README, CHANGELOG and comparison page all promise about the output.

    The per-candidate number §3 prints is an evidence tally that section defines;
    a percentage may appear only inside a quoted claim the report attributes to a
    generic scorer, in the falsifier table, which is the point of that table.
    """

    out = tmp_path / "checkup.md"
    assert main(["run", str(fixture_repo), "--out", str(out)]) == 0
    body = out.read_text()

    for line in body.splitlines():
        if re.search(r"\d\s*%", line):
            assert line.startswith("| “"), line
    assert re.search(r"(?i)\bgrade[sd]?\b|\bgrading\b", body) is None, body
    assert re.search(r"(?i)\b(readiness|overall|repository) score\b", body) is None, body
    assert "**Evidence (score " in body, "the per-candidate tally is still there, and §3 defines it"


def test_the_report_prints_the_path_exactly_as_it_was_given(fixture_repo: Path, tmp_path: Path) -> None:
    """Determinism, and the reason the README tells you to `cd` in and pass `.`.

    The path lands in the header line under the title, in §1 and in §6, so an
    absolute one puts the operator's home directory into a document meant to be
    handed over. The title itself prints the resolved directory's name.
    """

    out = tmp_path / "checkup.md"
    assert main(["run", str(fixture_repo), "--out", str(out)]) == 0
    absolute = out.read_text()
    assert absolute.count(str(fixture_repo)) >= 3

    done = subprocess.run(
        [sys.executable, "-m", "guardrail_checkup", "run", ".", "--out", str(out)],
        cwd=fixture_repo,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parent.parent / "src")},
    )
    assert done.returncode == 0, done.stderr
    relative = out.read_text()
    assert "read-only · `.` · " in relative
    assert "- **Repository:** `.`, as given on the command line" in relative
    assert str(fixture_repo) not in relative


def test_section_one_reports_the_capped_slice_and_names_both_totals(fixture_repo: Path, tmp_path: Path) -> None:
    """§3 is not the only section the `--max-files` slice decides.

    The README said "§3's ranking is the one section that reads the capped
    listing"; `_scan.scan` computes the language mix and the byte total from the
    slice too, and §1 prints both. Two runs, one capped and one not: §1's own
    numbers move, and the truncation line names the full count as well as the
    cap, so nothing in §1 reads as a statement about the whole repository.
    """

    whole, capped = tmp_path / "whole.md", tmp_path / "capped.md"
    assert main(["run", str(fixture_repo), "--out", str(whole)]) == 0
    assert main(["run", str(fixture_repo), "--out", str(capped), "--max-files", "3"]) == 0
    full, cut = whole.read_text(), capped.read_text()

    def size(body: str) -> str:
        return next(line for line in body.splitlines() if line.startswith("- **Size:**"))

    def mix(body: str) -> list[str]:
        return [line for line in body.splitlines() if line.startswith("  - `.")]

    assert size(full) != size(cut), size(cut)
    assert len(mix(cut)) < len(mix(full))
    assert "- **Size:** 3 file(s) considered," in cut
    # §1 names the cap and the full count beside it, so the reader can tell the
    # considered figure from the repository's own.
    assert "- **Listing truncated:**" in cut and "paths were found and the first 3 in" in cut
    assert "- **Listing truncated:**" not in full


def test_a_report_with_no_candidate_ends_that_paragraph_before_the_next_heading(tmp_path: Path) -> None:
    """Every other section boundary in the renderer has a blank line; this one had none.

    CommonMark still parses `## 4. Monday list` on the line straight after the
    paragraph, so nothing broke -- but the shipped artifact was inconsistent
    with the rest of the same file.
    """

    repository = tmp_path / "nothing"
    repository.mkdir()
    (repository / "readme.txt").write_text("no candidate path here\n")
    out = tmp_path / "r.md"
    assert main(["run", str(repository), "--out", str(out)]) == 0

    lines = out.read_text().splitlines()
    heading = next(number for number, line in enumerate(lines) if line.startswith(f"## {SECTIONS[3]}"))
    assert "there is no candidate to rank" in lines[heading - 2]
    assert lines[heading - 1] == ""


def test_section_six_discloses_that_the_tool_was_written_with_ai_assistance(fixture_repo: Path, tmp_path: Path) -> None:
    """The disclosure the README and CONTRIBUTING both promise, in every report.

    Both documents' sentences are bound to this test in `SENTENCES`: an audit
    replaced CONTRIBUTING's with its reverse -- "written by hand; only its tests
    were drafted with AI assistance" -- and all 441 tests passed.
    """

    out = tmp_path / "r.md"
    assert main(["run", str(fixture_repo), "--out", str(out)]) == 0
    body = out.read_text()
    assert "- **AI assistance:** this tool was written with AI assistance." in body

    document = tmp_path / "r.json"
    assert main(["run", str(fixture_repo), "--out", str(document), "--format", "json"]) == 0
    assert "written with AI assistance" in json.dumps(json.loads(document.read_text()))


def test_the_monday_list_says_the_emitted_policy_path_is_a_placeholder(fixture_repo: Path, tmp_path: Path) -> None:
    """Running the emitted MCP configuration as-is fails; the report has to say why."""

    from guardrail_checkup._cli import POLICY_PLACEHOLDER

    out = tmp_path / "checkup.md"
    assert main(["run", str(fixture_repo), "--out", str(out), "--emit-dir", str(tmp_path / "drafts")]) == 0
    body = out.read_text()
    assert f"Its `--policy` names `{POLICY_PLACEHOLDER}`, a placeholder" in body
    assert POLICY_PLACEHOLDER in (tmp_path / "drafts" / "mcp-wrapped.json").read_text()
