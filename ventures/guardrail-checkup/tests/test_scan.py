"""Reading a repository: the listing, the inventory, the history, the ranking."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
from conftest import GIT_ENV, build_repo, git

from guardrail_checkup import CODEOWNERS_BONUS, HEURISTIC_BASE, REGRESSION_WEIGHT, SKIP_DIRECTORIES, scan
from guardrail_checkup._scan import _argv, candidates, history, list_files


def facts(result) -> str:
    return "\n".join(f"{item.fact} | {item.where} | {item.consequence}" for item in result.findings)


# --- listing ------------------------------------------------------------------


def test_a_git_repository_is_listed_by_git_and_gitignore_is_respected(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".gitignore").write_text("ignored/\n")
    (repository / "ignored").mkdir()
    (repository / "ignored" / "secret.py").write_text("x = 1\n")
    result = scan(str(repository), 20_000)
    assert result.is_git
    assert "ignored/secret.py" not in result.files
    assert ".gitignore" in result.files


def test_a_plain_directory_is_walked_and_the_report_says_gitignore_was_not_applied(tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    (plain / "node_modules" / "left-pad").mkdir(parents=True)
    (plain / "node_modules" / "left-pad" / "index.js").write_text("//\n")
    (plain / "app.py").write_text("x = 1\n")
    result = scan(str(plain), 20_000)
    assert not result.is_git
    assert result.head is None
    assert result.files == ["app.py"], result.files
    assert "node_modules" in SKIP_DIRECTORIES


def test_the_listing_is_capped_and_the_cap_is_reported(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    files, total, truncated, _ = list_files(repository, 3)
    assert len(files) == 3
    assert total > 3
    assert truncated
    result = scan(str(repository), 3)
    assert result.truncated and result.max_files == 3


def test_a_file_list_is_sorted_so_two_runs_agree(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    assert scan(str(repository), 20_000).files == sorted(scan(str(repository), 20_000).files)


def test_a_binary_file_is_listed_and_not_read(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / "CLAUDE.md").write_bytes(b"# notes\x00\x00 never touch db/\n")
    result = scan(str(repository), 20_000)
    assert "CLAUDE.md: present, not read" in facts(result)


# --- inventory ----------------------------------------------------------------


def test_the_fixture_repository_has_the_gaps_the_demo_claims(fixture_repo: Path) -> None:
    text = facts(scan(str(fixture_repo), 20_000))
    assert "CLAUDE.md: 300 bytes, 8 lines, no line both forbids something and names a path" in text
    assert ".claude/settings.json: absent" in text
    assert "CODEOWNERS: absent" in text
    assert "secret scanning: not configured" in text
    assert "lockfiles: none found" in text
    assert ".github/workflows: absent" in text


def test_an_instruction_file_that_forbids_a_path_is_reported_as_such(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / "AGENTS.md").write_text("# rules\n\nNever edit db/migrations/ yourself.\n")
    text = facts(scan(str(repository), 20_000))
    assert "1 line(s) forbid something and name a path" in text
    assert "AGENTS.md:3" in text


def test_a_hook_that_matches_a_write_tool_is_distinguished_from_one_that_does_not(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".claude").mkdir()
    (repository / ".claude" / "settings.json").write_text(
        '{\n  "hooks": {\n    "PreToolUse": [\n'
        '      {"matcher": "Bash", "hooks": [{"type": "command", "command": "x"}]}\n    ]\n  }\n}\n'
    )
    text = facts(scan(str(repository), 20_000))
    assert "none matches a write tool" in text
    assert "no write tool is inspected by this event" in text
    assert "no PostToolUse hook" in text

    (repository / ".claude" / "settings.json").write_text(
        '{"hooks": {"PreToolUse": [{"matcher": "Write|Edit", "hooks": []}]}}'
    )
    text = facts(scan(str(repository), 20_000))
    assert "a write to any path is inspected" in text


def test_an_mcp_server_with_a_screen_in_its_command_line_is_told_apart(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    text = facts(scan(str(repository), 20_000))
    assert "no screen in the command line" in text
    assert "reaches the agent's context unscreened" in text

    (repository / ".mcp.json").write_text(
        '{"mcpServers": {"support-tools": {"command": "egresswall", '
        '"args": ["proxy", "--policy", "p.json", "--", "python", "-m", "support_tools"]}}}'
    )
    text = facts(scan(str(repository), 20_000))
    assert "tool output is screened before the agent sees it" in text


def test_a_workflow_is_judged_on_running_tests_and_on_pull_requests(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".github" / "workflows").mkdir(parents=True)
    workflow = repository / ".github" / "workflows" / "ci.yml"
    workflow.write_text("on:\n  push:\njobs:\n  t:\n    steps:\n      - run: pytest -q\n")
    text = facts(scan(str(repository), 20_000))
    assert "tests run, does not run on pull requests" in text
    assert "can reach review without this workflow having judged it" in text


def test_a_secret_scanner_in_ci_is_found_with_its_line(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".github" / "workflows").mkdir(parents=True)
    workflow = repository / ".github" / "workflows" / "scan.yml"
    workflow.write_text("jobs:\n  s:\n    steps:\n      - uses: gitleaks/gitleaks-action@v2\n")
    text = facts(scan(str(repository), 20_000))
    assert "secret scanning: configured" in text
    assert ".github/workflows/scan.yml:4" in text


def test_installed_git_hooks_are_told_apart_from_samples(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    assert "no installed hook (samples only)" in facts(scan(str(repository), 20_000))
    (repository / ".git" / "hooks" / "pre-commit").write_text("#!/bin/sh\nexit 0\n")
    assert ".git/hooks: pre-commit" in facts(scan(str(repository), 20_000))


def test_every_finding_carries_a_place_and_a_consequence(fixture_repo: Path) -> None:
    for finding in scan(str(fixture_repo), 20_000).findings:
        assert finding.fact and finding.where and finding.consequence
        assert finding.where == "-" or re.fullmatch(r"[^\s:]+:\d+", finding.where), finding.where


# --- history and ranking ------------------------------------------------------


def test_only_repair_commits_count_towards_the_history_evidence(fixture_repo: Path) -> None:
    repairs, churn, truncated = history(fixture_repo)
    assert len(repairs) == 3, [item.subject for item in repairs]
    assert all(any(word in item.subject.lower() for word in ("fix", "revert")) for item in repairs)
    assert not truncated
    assert "db/**" in churn
    assert any("db" in item.categories for item in repairs)


def test_a_repair_that_also_touches_a_regression_test_counts_double(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / "tests" / "test_regression_orders.py").write_text("def test_x():\n    assert True\n")
    (repository / "db" / "queries.py").write_text((repository / "db" / "queries.py").read_text() + "# y\n")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "fix: orders regression")
    repairs, _, _ = history(repository)
    latest = repairs[0]
    assert latest.subject == "fix: orders regression"
    assert latest.weight == REGRESSION_WEIGHT == 2
    assert all(item.weight == 1 for item in repairs[1:])


def test_the_score_is_the_arithmetic_the_report_states_not_the_files_touched(tmp_path: Path) -> None:
    """One repair commit over three db/ files is one commit of evidence, not three."""

    repository = tmp_path / "one-commit"
    (repository / "db").mkdir(parents=True)
    for name in ("a.py", "b.py", "c.py"):
        (repository / "db" / name).write_text("x = 1\n")
    git(repository, "init", "-q", "-b", "main")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "fix: one repair touching three db files")
    result = scan(str(repository), 20_000)
    candidate = next(item for item in result.candidates if item.slug == "db")
    assert candidate.score == HEURISTIC_BASE + 1 == 2
    assert result.repairs == 1
    assert "git history: 1 repair commit(s)" in " ".join(candidate.evidence)


def test_the_history_walk_stops_at_its_path_cap_and_says_so(fixture_repo: Path) -> None:
    """The commit cap bounds how far back; this one bounds what one commit can cost."""

    repairs, _, truncated = history(fixture_repo, max_paths=1)
    assert truncated
    assert len(repairs) < 3
    assert not any(hasattr(item, "paths") for item in repairs)


def test_candidates_are_ranked_by_evidence_and_the_db_layer_wins_here(fixture_repo: Path) -> None:
    result = scan(str(fixture_repo), 20_000)
    assert [item.slug for item in result.candidates][:1] == ["db"]
    assert result.candidates[0].score > result.candidates[-1].score
    assert result.candidates == sorted(result.candidates, key=lambda item: (-item.score, -len(item.paths), item.slug))


def test_codeowners_adds_two_to_the_score(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    before = {item.slug: item.score for item in scan(str(repository), 20_000).candidates}
    (repository / "CODEOWNERS").write_text("db/ @platform\n")
    after = scan(str(repository), 20_000)
    assert after.candidates[0].slug == "db"
    assert after.candidates[0].score == before["db"] + CODEOWNERS_BONUS == before["db"] + 2
    assert any("CODEOWNERS" in item for item in after.candidates[0].evidence)


def test_a_codeowners_pattern_with_no_owner_requires_nobody_and_scores_nothing(tmp_path: Path) -> None:
    """`*` on its own line clears ownership; counting it as a reviewer is a false positive."""

    repository = build_repo(tmp_path / "repo")
    before = {item.slug: item.score for item in scan(str(repository), 20_000).candidates}
    (repository / "CODEOWNERS").write_text("# comment\n*\n/db/\n")
    result = scan(str(repository), 20_000)
    text = facts(result)
    assert "CODEOWNERS: 0 pattern(s) with a required reviewer, 2 that name no owner" in text
    assert "no pattern here names an owner" in text
    assert result.owned == ()
    assert {item.slug: item.score for item in result.candidates} == before


def test_a_repository_with_no_candidate_paths_reports_none(tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    (plain / "main.c").write_text("int main(void){return 0;}\n")
    assert scan(str(plain), 20_000).candidates == []
    assert candidates([], [], ()) == []


def test_the_churn_is_the_directories_repairs_touched(fixture_repo: Path) -> None:
    result = scan(str(fixture_repo), 20_000)
    assert "db/**" in result.churn
    assert "db/migrations/**" in result.churn


def test_scanning_the_same_commit_twice_gives_the_same_answer(fixture_repo: Path) -> None:
    first, second = scan(str(fixture_repo), 20_000), scan(str(fixture_repo), 20_000)
    assert facts(first) == facts(second)
    assert first.candidates == second.candidates


def test_the_scan_never_writes_into_the_repository_it_reads(fixture_repo: Path) -> None:
    before = subprocess.run(
        ["git", "-C", str(fixture_repo), "status", "--porcelain"],
        capture_output=True,
        text=True,
        env={**GIT_ENV},
        check=True,
    ).stdout
    scan(str(fixture_repo), 20_000)
    after = subprocess.run(
        ["git", "-C", str(fixture_repo), "status", "--porcelain"],
        capture_output=True,
        text=True,
        env={**GIT_ENV},
        check=True,
    ).stdout
    assert before == after == ""


# --- a repository is untrusted input ------------------------------------------


def test_a_repository_config_cannot_make_git_run_a_program(tmp_path: Path) -> None:
    """core.fsmonitor in the checkout's own .git/config is executed by `git ls-files`."""

    repository = build_repo(tmp_path / "repo")
    sentinel = tmp_path / "pwned"
    hostile = tmp_path / "fsmonitor.sh"
    hostile.write_text(f'#!/bin/sh\ntouch "{sentinel}"\necho ""\n')
    hostile.chmod(0o755)
    git(repository, "config", "core.fsmonitor", str(hostile))

    result = scan(str(repository), 20_000)

    assert not sentinel.exists(), "the inspected repository ran a program on this machine"
    assert result.files, result.files


def test_every_git_call_carries_the_overrides_that_make_it_read_only(tmp_path: Path) -> None:
    """The list is short and auditable on purpose: read it next to READ_ONLY_GIT."""

    argv = _argv(tmp_path, "ls-files")
    assert argv[:3] == ["git", "-C", str(tmp_path)]
    assert argv[3:] == [
        "-c",
        "core.fsmonitor=false",
        "-c",
        "core.hooksPath=/dev/null",
        "--no-optional-locks",
        "ls-files",
    ]
    assert "GIT_CONFIG_GLOBAL" not in Path("src/guardrail_checkup/_scan.py").read_text(encoding="utf-8")


def test_a_symlink_out_of_the_repository_is_listed_and_never_read(tmp_path: Path) -> None:
    outside = tmp_path / "secret.txt"
    outside.write_text("PRIVATE" * 20_000 + "\n")
    repository = build_repo(tmp_path / "repo")
    (repository / "CLAUDE.md").unlink()
    (repository / "CLAUDE.md").symlink_to(outside)
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "fix: point the instructions elsewhere")

    result = scan(str(repository), 20_000)
    text = facts(result)

    assert "CLAUDE.md: present, not read" in text
    assert "symlinks out of this repository: 1 — CLAUDE.md" in text
    assert "PRIVATE" not in text
    assert str(len(outside.read_text())) not in text
    assert result.total_bytes < 10_000 < len(outside.read_text())


@pytest.mark.parametrize(
    "body,expected",
    [
        ('{"hooks": "none"}', "the hooks block is not a JSON object"),
        ('{"hooks": ["none"]}', "the hooks block is not a JSON object"),
        ('{"hooks": null}', "the hooks block is not a JSON object"),
        ('["not", "an", "object"]', "not a JSON object"),
        ('{"hooks": {"PreToolUse": "one"}}', "the PreToolUse block is not a list"),
        ('{"hooks": {"PreToolUse": [7]}}', "no PreToolUse hook"),
        ("{oops", "not valid JSON"),
    ],
)
def test_a_settings_file_that_is_not_the_expected_shape_is_a_finding_not_a_crash(
    tmp_path: Path, body: str, expected: str
) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".claude").mkdir()
    (repository / ".claude" / "settings.json").write_text(body)
    assert expected in facts(scan(str(repository), 20_000))


@pytest.mark.parametrize(
    "body,expected",
    [
        ('{"mcpServers": {"a": "just-a-string"}}', "MCP server 'a' is not a JSON object"),
        ('{"mcpServers": {"a": 7}}', "MCP server 'a' is not a JSON object"),
        ("[1,2,3]", ".mcp.json: not a JSON object"),
        ('{"mcpServers": ["a"]}', "the server list is not a JSON object"),
        ('{"mcpServers": {"a": {"command": "node", "args": "oops"}}}', "MCP server 'a' runs `node`"),
        ('{"mcpServers": {"a": {"type": "http", "url": "https://x.invalid/mcp"}}}', "MCP server 'a' is remote"),
    ],
)
def test_an_mcp_file_that_is_not_the_expected_shape_is_a_finding_not_a_crash(
    tmp_path: Path, body: str, expected: str
) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".mcp.json").write_text(body)
    assert expected in facts(scan(str(repository), 20_000))


def test_a_catch_all_matcher_inspects_every_write(tmp_path: Path) -> None:
    """The hooks page: omitting the matcher or using "*" activates on every event."""

    repository = build_repo(tmp_path / "repo")
    (repository / ".claude").mkdir()
    for matcher in ('"matcher": "*", ', '"matcher": "", ', ""):
        (repository / ".claude" / "settings.json").write_text(
            '{"hooks": {"PreToolUse": [{' + matcher + '"hooks": [{"type": "command", "command": "x"}]}]}}'
        )
        text = facts(scan(str(repository), 20_000))
        assert "none matches a write tool" not in text, matcher
        assert "a write to any path is inspected" in text, matcher
        assert "whether this hook blocks is not checked" in text, matcher


def test_a_path_that_is_not_utf8_is_reported_as_one_string_and_read_by_nobody(tmp_path: Path) -> None:
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
    result = scan(str(repository), 20_000)
    listed = [item for item in result.files if item.startswith("db/ba")]
    assert listed == ["db/ba\ufffdd.sql"], result.files
    assert all(item.isprintable() for item in result.files)


def test_an_invisible_character_in_a_path_is_escaped_where_it_is_rendered(tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    (plain / "db").mkdir(parents=True)
    (plain / "db" / "gp\u202egnp.sql").write_text("x\n")
    (plain / "db" / "a\u200bb.sql").write_text("x\n")
    result = scan(str(plain), 20_000)
    assert sorted(result.files) == ["db/a\\u200bb.sql", "db/gp\\u202egnp.sql"], result.files


def test_a_git_repository_with_no_commits_is_not_called_a_plain_directory(tmp_path: Path) -> None:
    repository = tmp_path / "empty"
    repository.mkdir()
    git(repository, "init", "-q", "-b", "main")
    result = scan(str(repository), 20_000)
    assert result.is_git
    assert result.head is None
    assert result.repairs == 0
