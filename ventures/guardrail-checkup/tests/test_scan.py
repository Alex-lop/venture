"""Reading a repository: the listing, the inventory, the history, the ranking."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
from conftest import FENCE, GIT_ENV, build_repo, git

from guardrail_checkup import (
    CODEOWNERS_BONUS,
    HEURISTIC_BASE,
    REGRESSION_WEIGHT,
    SETTINGS_FILES,
    SKIP_DIRECTORIES,
    checkup,
    compose,
    md,
    render_json,
    render_markdown,
    scan,
    servers_of,
)
from guardrail_checkup._report import EXAMPLES, NOT_REPLACED
from guardrail_checkup._scan import (
    AGENT_FILE_LIMIT,
    LANGUAGE_ROWS,
    SERVER_ROWS,
    WORKFLOW_LIMIT,
    _argv,
    candidates,
    history,
    list_files,
)

VERSIONS = {"guardrail-checkup": "0.1.0", "agent-plan-lint": "0.1.0", "egresswall": "0.1.0"}

#: An inline code span, however wide its fence: what the report puts a
#: repository-controlled path inside, and what a markdown reader will not
#: read as a link, a tag or a heading.
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)*?\1", re.S)


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
    files, all_files, truncated, _ = list_files(repository, 3)
    assert len(files) == 3
    assert len(all_files) > 3
    assert files == all_files[:3]
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
    assert "the command it runs is one of the known screens" in text
    assert "no screen in the command line" not in text


def test_a_workflow_is_judged_on_running_tests_and_on_pull_requests(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".github" / "workflows").mkdir(parents=True)
    workflow = repository / ".github" / "workflows" / "ci.yml"
    workflow.write_text("on:\n  push:\njobs:\n  t:\n    steps:\n      - run: pytest -q\n")
    text = facts(scan(str(repository), 20_000))
    assert "a test runner is named in a run: step, does not run on pull requests" in text
    assert "can reach review without this workflow having judged it" in text


def test_pull_request_is_read_in_the_trigger_block_and_nowhere_else(tmp_path: Path) -> None:
    """A substring search over the whole file made a job name decide the trigger."""

    repository = build_repo(tmp_path / "repo")
    (repository / ".github" / "workflows").mkdir(parents=True)
    named = repository / ".github" / "workflows" / "named.yml"
    named.write_text("on: push\njobs:\n  pull_request_notes:\n    steps:\n      - run: pytest\n")
    assert "named.yml: a test runner is named in a run: step, does not run on pull requests" in facts(
        scan(str(repository), 20_000)
    )

    for trigger in ("on: pull_request\n", "on: [push, pull_request]\n", "on:\n  pull_request:\n    branches: [main]\n"):
        named.write_text(trigger + "jobs:\n  t:\n    steps:\n      - run: pytest\n")
        assert "named.yml: a test runner is named in a run: step, runs on pull requests" in facts(
            scan(str(repository), 20_000)
        ), trigger


def test_a_secret_scanner_in_ci_is_found_with_its_line(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".github" / "workflows").mkdir(parents=True)
    workflow = repository / ".github" / "workflows" / "scan.yml"
    workflow.write_text("jobs:\n  s:\n    steps:\n      - uses: gitleaks/gitleaks-action@v2\n")
    text = facts(scan(str(repository), 20_000))
    assert "secret scanning: named in 1 place(s)" in text
    assert ".github/workflows/scan.yml:4" in text


def test_a_scanner_named_in_a_job_id_or_a_guard_is_not_reported_as_a_configured_control(tmp_path: Path) -> None:
    """The fact column may not assert a control this repository does not have.

    Unlike the test-runner row, this detector is a word search over the whole
    uncommented file, so a job id, a step `name:`, an `if:` guard and an `env:`
    value all reach it -- the three places the sibling detector at
    `_run_steps` was hardened against. "secret scanning: configured" over
    `gitleaks-job:` and `name: gitleaks is not used here` states a control that
    is not there, and the row's own consequence cell contradicts it.
    """

    repository = tmp_path / "named"
    (repository / ".github" / "workflows").mkdir(parents=True)
    (repository / ".github" / "workflows" / "ci.yml").write_text(
        "on: push\njobs:\n"
        "  gitleaks-job:\n"
        "    steps:\n"
        "      - name: gitleaks and pytest are not used here\n"
        "        if: gitleaks\n"
        "        env:\n"
        "          NOTE: we removed gitleaks\n"
        "        run: echo hi\n"
    )
    text = facts(scan(str(repository), 20_000))
    assert "secret scanning: named in 1 place(s)" in text
    assert "secret scanning: configured" not in text
    row = next(item for item in scan(str(repository), 20_000).findings if item.fact.startswith("secret scanning:"))
    assert "whether it runs, and on what, was not checked" in row.consequence


def test_the_workflow_rows_are_capped_and_the_row_says_how_many_there_were(tmp_path: Path) -> None:
    """The number of workflows is the repository's choice, so it is bounded here.

    Each one is read at up to MAX_READ_BYTES and walked line by line, and the
    listing had no cap at all: 1,000 workflows of 1 MiB apiece took 44 seconds
    and produced 1,015 rows. The remainder row is the one `.cursor/rules`
    already gets, so no cell states a negative about a workflow nobody opened.
    """

    repository = tmp_path / "workflows"
    (repository / ".github" / "workflows").mkdir(parents=True)
    for number in range(WORKFLOW_LIMIT + 5):
        path = repository / ".github" / "workflows" / f"w{number:03d}.yml"
        path.write_text("on: push\njobs:\n  a:\n    steps: []\n")
    # The scanner is named only in a workflow that sorts past the cap.
    (repository / ".github" / "workflows" / "zz-last.yml").write_text(
        "on: push\njobs:\n  s:\n    steps:\n      - run: gitleaks detect\n"
    )

    result = scan(str(repository), 20_000)
    text = facts(result)

    assert f".github/workflows: {WORKFLOW_LIMIT + 6:,} file(s); the first {WORKFLOW_LIMIT} in sorted order" in text
    assert "6 more file(s) were listed and not read" in text
    assert len([item for item in result.findings if item.fact.startswith(".github/workflows/w")]) == WORKFLOW_LIMIT
    # And nothing then says the repository has no scanner, because six of the
    # files one would be named in were never opened.
    assert "secret scanning: not configured" not in text
    assert "secret scanning: not named in the files that were read; 6 file(s) here were present and not read" in text


def test_installed_git_hooks_are_told_apart_from_samples(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    assert "no installed hook (samples only)" in facts(scan(str(repository), 20_000))
    hook = repository / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/bin/sh\nexit 0\n")
    hook.chmod(0o755)
    assert ".git/hooks: pre-commit" in facts(scan(str(repository), 20_000))


def test_a_hook_git_will_not_run_is_not_reported_as_one_that_checks_a_commit(tmp_path: Path) -> None:
    """git refuses a hook without the execute bit and makes the commit anyway.

    "hint: The '.git/hooks/pre-commit' hook was ignored because it's not set as
    executable" -- and the commit lands. Counting the file as installed put "a
    commit is checked locally before it is made" in the report about a commit
    nothing checked.
    """

    repository = build_repo(tmp_path / "repo")
    hook = repository / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o644)

    text = facts(scan(str(repository), 20_000))

    assert ".git/hooks: no executable hook" in text
    assert "a commit is checked locally before it is made" not in text
    assert ".git/hooks: pre-commit — present, not executable" in text
    assert "git ignores a hook file without the execute bit" in text
    # And git agrees: the commit goes through with the hook sitting there.
    (repository / "b.py").write_text("x\n")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "second")

    hook.chmod(0o755)
    executable = facts(scan(str(repository), 20_000))
    assert ".git/hooks: pre-commit" in executable
    assert "a commit is checked locally before it is made" in executable
    assert "present, not executable" not in executable


def test_the_files_under_one_agent_file_prefix_are_capped_and_the_row_says_so(tmp_path: Path) -> None:
    """`.cursor/rules/` fans out over a directory, and the fan-out was unbounded."""

    repository = tmp_path / "rules"
    (repository / ".cursor" / "rules").mkdir(parents=True)
    for number in range(AGENT_FILE_LIMIT + 5):
        (repository / ".cursor" / "rules" / f"r{number:03d}.md").write_text("never edit db/ here\n")

    text = facts(scan(str(repository), 20_000))

    assert f"the first {AGENT_FILE_LIMIT} in sorted order were read" in text
    assert "5 more file(s) under this path were listed and not read" in text
    rows = [line for line in text.splitlines() if line.startswith(".cursor/rules/r")]
    assert len(rows) == AGENT_FILE_LIMIT


def test_a_handful_of_rule_files_is_still_reported_in_full(tmp_path: Path) -> None:
    repository = tmp_path / "few"
    (repository / ".cursor" / "rules").mkdir(parents=True)
    for name in ("a.md", "b.md", "c.md"):
        (repository / ".cursor" / "rules" / name).write_text("never edit db/ here\n")

    text = facts(scan(str(repository), 20_000))

    assert "in sorted order were read" not in text
    for name in ("a.md", "b.md", "c.md"):
        assert f".cursor/rules/{name}" in text


def test_the_mcp_server_rows_are_capped_and_the_row_says_how_many_there_were(tmp_path: Path) -> None:
    repository = tmp_path / "many"
    repository.mkdir()
    (repository / ".mcp.json").write_text(
        json.dumps({"mcpServers": {f"s{i:05d}": {"url": f"https://x{i}.example/"} for i in range(SERVER_ROWS + 7)}})
    )

    text = facts(scan(str(repository), 20_000))

    assert f"{SERVER_ROWS + 7:,} server(s) configured; the first {SERVER_ROWS} in sorted order have a row below" in text
    assert "7 more server(s) are configured here" in text
    assert text.count("MCP server") == SERVER_ROWS


def test_symlink_stats_stop_at_the_listing_cap(tmp_path: Path, monkeypatch) -> None:
    """Finding 9 must not lstat every ordinary file in an unbounded listing."""

    import guardrail_checkup._scan as scan_module

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("x\n")
    repository = tmp_path / "capped"
    repository.mkdir()
    for number in range(5):
        (repository / f"a{number}.txt").write_text("x\n")
    (repository / "zz-escape.txt").symlink_to(outside / "secret.txt")

    checked: list[str] = []
    real = scan_module._escapes

    def counted(root: Path, relative: str) -> bool:
        checked.append(relative)
        return real(root, relative)

    monkeypatch.setattr(scan_module, "_escapes", counted)
    result = scan(str(repository), 3)

    assert result.truncated
    assert "zz-escape.txt" not in result.files
    assert checked == result.files
    assert "symlinks out of this repository" not in facts(result)


def test_every_file_this_tool_opens_is_named_in_the_scope_it_prints(tmp_path: Path) -> None:
    """§1 promises "exactly what was and was not read", so every `_read` is accounted.

    The linter falsifier opened `pyproject.toml` with `_read` directly, so a
    repository whose only linter evidence is `[tool.ruff]` produced the row with
    `scope.read` empty.
    """

    import guardrail_checkup._compose as compose_module
    import guardrail_checkup._report as report_module
    import guardrail_checkup._scan as scan_module

    repository = build_repo(tmp_path / "repo")
    (repository / "pyproject.toml").write_text("[tool.ruff]\nline-length = 120\n")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "add a linter configuration")

    opened: list[str] = []
    real = scan_module._read

    def spy(root, relative):
        opened.append(relative)
        return real(root, relative)

    for module in (scan_module, compose_module, report_module):
        module._read = spy  # type: ignore[attr-defined]
    try:
        result = scan(str(repository), 20_000)
        composed = compose(result, "p.json")
        document = json.loads(
            __import__("guardrail_checkup", fromlist=["render_json"]).render_json(
                result, composed, "cmd", VERSIONS, None, "2026-08-31"
            )
        )
    finally:
        for module in (scan_module, compose_module, report_module):
            module._read = real  # type: ignore[attr-defined]

    accounted = set(document["scope"]["read"]) | set(document["scope"]["unread"])
    assert opened, "nothing was read at all"
    assert set(opened) <= accounted, sorted(set(opened) - accounted)
    assert "pyproject.toml" in document["scope"]["read"]


def test_the_absent_rows_say_nothing_about_the_host(tmp_path: Path) -> None:
    """§5 says branch protection and the host were never asked, so §2 may not answer.

    *CODEOWNERS: absent* claimed any path can be merged by anyone and
    *.github/workflows: absent* claimed no automated check runs at all — both
    false under branch protection with required reviewers, or under any CI that
    is not GitHub Actions.
    """

    repository = build_repo(tmp_path / "repo")
    text = facts(scan(str(repository), 20_000))

    assert "CODEOWNERS: absent" in text and ".github/workflows: absent" in text
    assert "no path in this repository names a required reviewer; branch protection on the host was not read" in text
    assert "no GitHub Actions workflow is checked in here; CI configured elsewhere was not read" in text
    assert "any path can be merged by anyone" not in text
    assert "no automated check runs on a change at all" not in text


def test_every_finding_carries_a_place_and_a_consequence(fixture_repo: Path) -> None:
    """The claim three documents make: every row that cites a file carries its `file:line`.

    The assertion opened `finding.where == "-" or ...`, which exempted the whole
    counterexample: an absence row renders `-`, nine of the seventeen rows of
    the shipped `demo/OUTPUT.md` are absence rows, and the documents said every
    row carried the `file:line` it came from. The blanket exemption pinned the
    false absolute in place. Scoped now -- a row may carry `-` only when it
    cites no file this scan opened, because what establishes an absence is the
    listing and not a line of a file.
    """

    result = scan(str(fixture_repo), 20_000)
    opened = result.read + result.unread
    assert result.findings
    for finding in result.findings:
        assert finding.fact and finding.where and finding.consequence
        if finding.where == "-":
            assert not [item for item in opened if item in finding.fact], finding.fact
        else:
            assert re.fullmatch(r"[^\s:]+:\d+", finding.where), finding.where


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
    # Not `sorted(..., key=<the code's own key>)`, which is the code restating
    # itself and cannot fail. The scores are read off the list and the order is
    # checked against them.
    scores = [item.score for item in result.candidates]
    assert scores == sorted(scores, reverse=True), scores


def test_equal_scores_are_ordered_by_the_number_of_matching_files(tmp_path: Path) -> None:
    """The README and §3 both say "the number of matching files", so it is all of them.

    `paths` is capped at eight examples and was the tie-break, so a category of
    twenty files lost to one of nine and the report stated the opposite of the
    order it had produced.
    """

    repository = tmp_path / "tie"
    for folder, count in (("db", 20), ("auth", 9)):
        (repository / folder).mkdir(parents=True)
        for number in range(count):
            (repository / folder / f"f{number:02d}.py").write_text("x = 1\n")

    result = scan(str(repository), 20_000)

    assert {item.slug: item.score for item in result.candidates} == {"db": HEURISTIC_BASE, "auth": HEURISTIC_BASE}
    assert [item.slug for item in result.candidates] == ["db", "auth"]
    assert [item.matched for item in result.candidates] == [20, 9]
    assert [len(item.paths) for item in result.candidates] == [8, 8], "the examples are capped and cannot rank"


def test_codeowners_adds_two_to_the_score(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    before = {item.slug: item.score for item in scan(str(repository), 20_000).candidates}
    (repository / "CODEOWNERS").write_text("db/ @platform\n")
    after = scan(str(repository), 20_000)
    assert after.candidates[0].slug == "db"
    assert after.candidates[0].score == before["db"] + CODEOWNERS_BONUS == before["db"] + 2
    assert any("CODEOWNERS" in item for item in after.candidates[0].evidence)


def test_the_codeowners_evidence_line_states_the_total_before_its_examples(tmp_path: Path) -> None:
    """It named three patterns and no total, in a report whose caps announce themselves.

    The repair-commit line two statements above it prints the count and then the
    first three; twelve owned patterns pointing at a candidate's files showed
    three, and the reader could not tell the list had been cut.
    """

    repository = build_repo(tmp_path / "repo")
    for number in range(12):
        (repository / "db" / f"f{number:02d}.py").write_text("x = 1\n")
    (repository / "CODEOWNERS").write_text("".join(f"/db/f{number:02d}.py @platform\n" for number in range(12)))

    result = scan(str(repository), 20_000)
    line = next(item for item in result.candidates[0].evidence if item.startswith("CODEOWNERS:"))

    assert line.startswith("CODEOWNERS: 12 pattern(s) already require a named reviewer — ")
    assert line.count(",") == 2, "the count, then three examples"


def test_the_language_mix_says_how_many_extensions_it_left_out(tmp_path: Path) -> None:
    """§1 promises exactly what was and was not read, and cut the list at ten in silence."""

    repository = tmp_path / "polyglot"
    repository.mkdir()
    for number in range(15):
        (repository / f"f{number:02d}.e{number:02d}").write_text("x\n")

    result = scan(str(repository), 20_000)
    body = render_markdown(result, compose(result, "p.json"), "cmd", VERSIONS, None, "2026-08-31")

    assert len(result.languages) == LANGUAGE_ROWS == 10
    assert result.extensions == 15
    assert f"- **Language mix** (by file extension), the {LANGUAGE_ROWS} most common of 15:" in body


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


def test_every_git_call_carries_the_overrides_that_make_it_read_only(tmp_path: Path, repo_root: Path) -> None:
    """The list is short and auditable on purpose: read it next to READ_ONLY_GIT."""

    argv = _argv(tmp_path, "ls-files")
    assert argv[:3] == ["git", "-C", str(tmp_path)]
    assert argv[3:] == [
        "-c",
        "core.fsmonitor=false",
        "-c",
        "core.hooksPath=/dev/null",
        "-c",
        "core.quotePath=false",
        "--no-optional-locks",
        "ls-files",
    ]
    assert "GIT_CONFIG_GLOBAL" not in (repo_root / "src" / "guardrail_checkup" / "_scan.py").read_text("utf-8")


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
    """`git ls-files` succeeded, so the report may not say this is not a repository."""

    repository = tmp_path / "empty"
    repository.mkdir()
    git(repository, "init", "-q", "-b", "main")
    result = scan(str(repository), 20_000)
    assert result.is_git
    assert result.head is None
    assert result.repairs == 0

    body = render_markdown(result, compose(result, "p.json"), "cmd", VERSIONS, None, "2026-08-31")
    assert body.count("git repository with no commits yet") == 3  # the header, §1 and §6
    assert "not a git repository" not in body
    assert "`git ls-files`" in body


def test_a_sampled_history_says_so_in_the_report(fixture_repo: Path) -> None:
    result = scan(str(fixture_repo), 20_000)
    repairs, _, truncated = history(fixture_repo, max_paths=1)
    result.repairs, result.history_sampled = len(repairs), truncated
    body = render_markdown(result, compose(result, "p.json"), "cmd", VERSIONS, None, "2026-08-31")
    assert "The history was sampled: the walk stopped after 100,000 path entries" in body


# --- what the listing, the hooks directory and the detectors get wrong --------


def test_a_symlink_cycle_does_not_stop_the_report_being_written(tmp_path: Path) -> None:
    """Path.resolve raises RuntimeError, not OSError, on ELOOP. It killed the whole run."""

    loops = tmp_path / "loops"
    loops.mkdir()
    (loops / "loopa").symlink_to("loopb")
    (loops / "loopb").symlink_to("loopa")
    result = scan(str(loops), 20_000)
    assert sorted(result.files) == ["loopa", "loopb"]
    body = render_markdown(result, compose(result, "p.json"), "cmd", VERSIONS, None, "2026-08-31")
    assert "## 1. Scope" in body


def test_a_directory_symlink_out_of_the_repository_is_listed_and_reported(tmp_path: Path) -> None:
    """A link to a whole tree is the dangerous case; os.walk never puts one in `names`."""

    outside = tmp_path / "outside"
    (outside / "nested").mkdir(parents=True)
    (outside / "nested" / "secret.txt").write_text("PRIVATE\n")
    plain = tmp_path / "plain"
    plain.mkdir()
    (plain / "escape.txt").symlink_to(outside / "nested" / "secret.txt")
    (plain / "escapedir").symlink_to(outside)

    result = scan(str(plain), 20_000)

    assert sorted(result.files) == ["escape.txt", "escapedir"], result.files
    assert "escapedir/nested/secret.txt" not in result.files, "the walk descended into the link"
    assert "symlinks out of this repository: 2 — escape.txt, escapedir" in facts(result)


def test_an_installed_hook_is_found_when_core_hookspath_moves_the_directory(tmp_path: Path) -> None:
    """The configuration a blocking hook is most likely to live in. The row said the opposite."""

    repository = build_repo(tmp_path / "repo")
    (repository / ".githooks").mkdir()
    (repository / ".githooks" / "pre-commit").write_text("#!/bin/sh\nexit 1\n")
    (repository / ".githooks" / "pre-commit").chmod(0o755)
    git(repository, "config", "core.hooksPath", ".githooks")

    text = facts(scan(str(repository), 20_000))

    assert ".githooks: pre-commit" in text
    assert "no installed hook (samples only)" not in text
    assert "a commit is checked locally before it is made" in text


def test_an_installed_hook_is_found_from_inside_a_worktree(tmp_path: Path) -> None:
    """A linked worktree's `.git` is a file, so `<root>/.git/hooks` does not exist."""

    repository = build_repo(tmp_path / "repo")
    (repository / ".git" / "hooks" / "pre-commit").write_text("#!/bin/sh\nexit 1\n")
    (repository / ".git" / "hooks" / "pre-commit").chmod(0o755)
    worktree = tmp_path / "wt"
    git(repository, "worktree", "add", "-q", str(worktree), "-b", "side")

    text = facts(scan(str(worktree), 20_000))

    assert "pre-commit" in text
    assert "no installed hook (samples only)" not in text
    assert str(repository) not in text, "an absolute path off this machine may not reach the report"


@pytest.mark.parametrize("shape", ["absolute", "relative"])
def test_a_hooks_path_outside_the_repository_is_reported_and_never_listed(tmp_path: Path, shape: str) -> None:
    """`core.hooksPath` is the inspected checkout's setting, so the answer is contained.

    Unchecked, it made this tool `iterdir()` any directory on the reader's
    machine the repository named and print its filenames into the report as
    this repository's installed hooks, under "the hooks directory this worktree
    shares with its main checkout".
    """

    secret = tmp_path / "secrets"
    secret.mkdir()
    (secret / "id_rsa").write_text("PRIVATE\n")
    (secret / "company-prod.pem").write_text("PRIVATE\n")
    repository = build_repo(tmp_path / "repo")
    git(repository, "config", "core.hooksPath", str(secret) if shape == "absolute" else "../secrets")

    result = scan(str(repository), 20_000)
    body = render_markdown(result, compose(result, "p.json"), "cmd", VERSIONS, None, "2026-08-31")

    assert "`core.hooksPath` points outside this repository" in facts(result)
    assert "a commit is checked locally before it is made" not in facts(result)
    for name in ("id_rsa", "company-prod.pem", str(secret)):
        assert name not in body, name


def test_a_hooks_path_that_is_not_a_directory_gets_no_row_at_all(tmp_path: Path) -> None:
    """ "no installed hook (samples only)" about a file is a statement about nothing."""

    repository = build_repo(tmp_path / "repo")
    git(repository, "config", "core.hooksPath", "app/checkout.py")
    text = facts(scan(str(repository), 20_000))
    assert "no installed hook (samples only)" not in text
    assert "nothing is checked at commit time" not in text


def test_a_path_that_is_not_a_git_repository_gets_no_hooks_row_at_all(tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    (plain / "main.c").write_text("int main(void){return 0;}\n")
    text = facts(scan(str(plain), 20_000))
    assert "hooks" not in text
    assert "nothing is checked at commit time" not in text


def test_an_artifact_that_sorts_past_the_listing_cap_is_still_found(tmp_path: Path) -> None:
    """The inventory reads the whole listing: `none found` off a truncated one is false."""

    repository = tmp_path / "big"
    (repository / "aaa").mkdir(parents=True)
    for number in range(40):
        (repository / "aaa" / f"{number:03d}.py").write_text("x = 1\n")
    (repository / "requirements.lock").write_text("package==1.0\n")
    (repository / "CODEOWNERS").write_text("db/ @platform\n")
    git(repository, "init", "-q", "-b", "main")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "initial import")

    result = scan(str(repository), 10)
    text = facts(result)

    assert result.truncated and len(result.files) == 10
    assert "lockfiles: requirements.lock" in text, text
    assert "lockfiles: none found" not in text
    assert "CODEOWNERS: absent" not in text


def test_a_workflow_that_says_it_does_not_use_a_scanner_is_not_reported_as_having_one(tmp_path: Path) -> None:
    """A comment is what a file says about itself, not what it runs."""

    repository = tmp_path / "commented"
    (repository / ".github" / "workflows").mkdir(parents=True)
    (repository / ".github" / "workflows" / "ci.yml").write_text("# we do NOT use gitleaks or pytest here\non: push\n")
    text = facts(scan(str(repository), 20_000))
    assert "secret scanning: not configured" in text
    assert "secret scanning: configured" not in text
    assert "no test runner in a run: step" in text


def test_a_package_merely_named_proxy_is_not_reported_as_a_screen(tmp_path: Path) -> None:
    """The one row that asserts a control is in force may not be decided by a substring."""

    repository = build_repo(tmp_path / "repo")
    (repository / ".mcp.json").write_text('{"mcpServers":{"s":{"command":"npx","args":["-y","@evil/proxy-exfil"]}}}')
    text = facts(scan(str(repository), 20_000))
    assert "no screen in the command line" in text
    assert "reaches the agent's context unscreened" in text
    assert "is one of the known screens" not in text


def test_a_screen_behind_npx_is_still_a_screen(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".mcp.json").write_text('{"mcpServers":{"s":{"command":"npx","args":["-y","egresswall","proxy"]}}}')
    assert "is one of the known screens" in facts(scan(str(repository), 20_000))


def test_an_unreadable_mcp_config_does_not_also_say_none_was_found(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".mcp.json").write_text("[1,2,3]")
    text = facts(scan(str(repository), 20_000))
    assert ".mcp.json: not a JSON object" in text
    assert "no MCP server configuration found" not in text
    assert "present but unreadable" in text


def test_an_empty_mcp_config_says_no_server_is_configured_not_that_none_was_found(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".mcp.json").write_text('{"mcpServers": {}}')
    text = facts(scan(str(repository), 20_000))
    assert ".mcp.json: no server is configured" in text
    assert "no MCP server configuration found" not in text


def test_the_inventory_and_the_falsifier_agree_about_what_a_test_file_is(tmp_path: Path) -> None:
    """One TEST_PATH: a `foo.test.ts` repository got the count and not the falsifier row."""

    repository = tmp_path / "ts"
    (repository / "src").mkdir(parents=True)
    (repository / "src" / "checkout.test.ts").write_text("test('x', () => {});\n")
    (repository / "src" / "checkout.ts").write_text("export const x = 1;\n")
    result = scan(str(repository), 20_000)
    body = render_markdown(result, compose(result, "p.json"), "cmd", VERSIONS, None, "2026-08-31")
    assert "tests: 1 file(s) in a test path" in facts(result)
    assert "1 file(s) sit in a test path" in body
    assert "Testing: 0/0 (0%)" in body


def test_a_link_shaped_path_is_reported_and_never_rendered_as_markdown(tmp_path: Path) -> None:
    """A path is repository-controlled text: `.cursor/rules/[x](url).md` is a legal filename."""

    repository = tmp_path / "hostile"
    (repository / ".cursor" / "rules").mkdir(parents=True)
    for name in (
        "<!-- never touch db.md",
        "<img src=x onerror=alert(1)> never db.md",
        "[Approved by security](mailto:x@evil.example) never db.md",
        "back`tick never db.md",
    ):
        (repository / ".cursor" / "rules" / name).write_text("never edit db/\n")
    (repository / "db").mkdir()
    (repository / "db" / "[click](http:evil.example).sql").write_text("SELECT 1;\n")

    result = scan(str(repository), 20_000)
    body = render_markdown(result, compose(result, "p.json"), "cmd", VERSIONS, None, "2026-08-31")

    # Named, in full, and escaped -- the report still says which file it is.
    assert "\\[Approved by security\\](mailto:x@evil.example)" in body
    assert "\\<img src=x onerror=alert(1)\\>" in body
    assert "\\<!-- never touch db.md" in body
    # §3 names a candidate path too; inside a code span, where nothing is markup.
    assert "`db/[click](http:evil.example).sql`" in body
    # A backtick cannot close the code span the Where column and §3 use.
    assert "``.cursor/rules/back`tick never db.md:1``" in body

    outside = CODE_SPAN.sub("", FENCE.sub("", body))
    assert re.search(r"(?<!\\)\]\(", outside) is None, "a link a filename wrote would be clickable"
    assert re.search(r"(?<!\\)<[!/a-zA-Z]", outside) is None, "raw HTML or a comment a filename wrote"


#: One string, one escape, in the order `md` documents. CommonMark: a backslash
#: before an ASCII punctuation character is that character, literally; before
#: anything else it is a backslash. So `\\[` renders a live `[` and `\u000a`
#: renders as itself.
ESCAPES = [
    ("[x](https://evil.example)", "\\[x\\](https://evil.example)"),
    ("](https://evil.example)", "\\](https://evil.example)"),
    ("back\\slash", "back\\\\slash"),
    ("<img src=x>", "\\<img src=x\\>"),
    ("a`b", "a\\`b"),
    ("*bold* _em_", "\\*bold\\* \\_em\\_"),
    ("a|b", "a\\|b"),
    ("one\ntwo", "one\\u000atwo"),
    ("gp\u202egnp", "gp\\u202egnp"),
]


@pytest.mark.parametrize("raw,escaped", ESCAPES, ids=[item[0][:12] for item in ESCAPES])
def test_one_escaper_escapes_the_backslash_first_and_everything_else_after(raw: str, escaped: str) -> None:
    """The order is the whole fix: `md` after `md` turns `\\[` into a live `[`."""

    assert md(raw) == escaped


def test_the_escaper_cuts_before_it_escapes_so_a_cut_never_leaves_half_an_escape() -> None:
    out = md("[" * 300, width=10)
    assert out == "\\[" * 9 + "…"


def test_no_repository_controlled_string_reaches_the_report_as_markdown(tmp_path: Path) -> None:
    """A server name, a hook matcher, a CODEOWNERS pattern and a commit subject.

    The path case has its own test above; these four went through `repr()` or
    were interpolated raw, and `repr()` doubled the backslash `quoted` had just
    added -- so the escape did not merely fail, it inverted, and the report a
    reader hands to someone else carried a live link out of the checkout.
    """

    repository = build_repo(tmp_path / "hostile")
    (repository / ".mcp.json").write_text(
        json.dumps(
            {
                "mcpServers": {
                    "[Approved by security](https://evil.example/pwn)": {"command": "node", "args": ["s.js"]},
                    "](https://evil.example/two)": {"command": "node", "args": ["s.js"]},
                    "x`code`y": {"command": "node", "args": ["s.js"]},
                }
            }
        )
    )
    (repository / ".claude").mkdir()
    (repository / ".claude" / "settings.json").write_text(
        json.dumps({"hooks": {"PreToolUse": [{"matcher": "Write|[click here](https://evil.example)", "hooks": []}]}})
    )
    (repository / "CODEOWNERS").write_text("[db](https://evil.example)/ @platform\ndb/ @platform\n")
    (repository / "db" / "queries.py").write_text("# touched\n")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "fix: [SECURITY REVIEW PASSED](https://evil.example/x) <b>all clear</b>")

    result = scan(str(repository), 20_000)
    body = render_markdown(result, compose(result, "p.json"), "cmd", VERSIONS, None, "2026-08-31")

    assert "\\[Approved by security\\](https://evil.example/pwn)" in body
    assert "\\](https://evil.example/two)" in body
    assert "\\[SECURITY REVIEW PASSED\\]" in body
    assert "\\[click here\\]" in body
    outside = CODE_SPAN.sub("", FENCE.sub("", body))
    assert re.search(r"(?<!\\)\]\(", outside) is None, "a link a repository string wrote would be clickable"
    assert re.search(r"(?<!\\)<[!/a-zA-Z]", outside) is None, "raw HTML a repository string wrote"
    assert re.search(r"(?<!\\)`", outside) is None, "a backtick that would open a code span"
    # Every table row is still one row: nothing closed the table.
    for line in body.splitlines():
        if line.startswith("|"):
            assert line.endswith("|"), line


def test_a_repair_commit_over_a_non_ascii_path_spells_it_the_way_the_listing_does(tmp_path: Path) -> None:
    """`git log --name-only` C-quotes anything that is not ASCII unless told not to.

    The quoted literal became the starter policy's write glob, `policy_globs`
    then called the backslash unpoliceable and dropped it, and the emitted
    policy carried two spellings of one directory -- the report blaming
    agent-plan-lint for a mangling this tool did itself.
    """

    repository = tmp_path / "accents"
    (repository / "caf\u00e9" / "db").mkdir(parents=True)
    (repository / "na\u00efve").mkdir()
    (repository / "caf\u00e9" / "db" / "queries.py").write_text("x = 1\n")
    (repository / "na\u00efve" / "pay.py").write_text("x = 1\n")
    (repository / "plain.py").write_text("x = 1\n")
    git(repository, "init", "-q", "-b", "main")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "fix: regression in caf\u00e9/db")

    result = scan(str(repository), 20_000)
    _, composed = checkup(str(repository))
    policy = json.loads(composed.drafts["starter-policy.json"])

    assert "caf\u00e9/db/**" in result.churn, result.churn
    assert "na\u00efve" in " ".join(result.churn)
    assert "caf\u00e9/db/**" in policy["allowed_write_globs"], policy["allowed_write_globs"]
    assert not any("\\" in item for item in policy["allowed_write_globs"]), policy["allowed_write_globs"]
    assert composed.unpoliceable == ()
    # The exclusions come from ls-files and the write globs from the log; one
    # spelling, or the emitted policy contradicts itself.
    assert set(policy["exclusions"]) <= set(policy["allowed_write_globs"]) | {"caf\u00e9/db/**"}


def test_a_repair_commit_over_a_path_that_is_not_utf8_does_not_stop_the_history(tmp_path: Path) -> None:
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
    git(repository, "commit", "-q", "-m", "fix: the byte that is not utf-8")

    result = scan(str(repository), 20_000)

    assert "db/ba\ufffdd.sql" in result.files
    assert "db/**" in result.churn
    assert all(item.isprintable() for item in result.churn), result.churn
    assert result.repairs == 4


def test_a_hook_in_the_local_settings_file_is_not_reported_as_no_hook_at_all(tmp_path: Path) -> None:
    """Claude Code reads settings.local.json and gitignores it, so ls-files never lists it.

    The row said `.claude/settings.json: absent` and the consequence stated an
    absolute -- nothing inspects a tool call -- about a repository whose
    blocking PreToolUse hook was one file over.
    """

    repository = build_repo(tmp_path / "repo")
    (repository / ".claude").mkdir()
    (repository / ".gitignore").write_text(".claude/settings.local.json\n")
    (repository / ".claude" / "settings.local.json").write_text(
        '{"hooks": {"PreToolUse": [{"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "b.py"}]}]}}'
    )
    text = facts(scan(str(repository), 20_000))

    assert ".claude/settings.local.json: 1 PreToolUse entry" in text
    assert "a write to any path is inspected by a hook this repository checks in" in text
    # And the absent row for the other file no longer states an absolute about
    # the machine.
    assert ".claude/settings.json: absent" in text
    assert "no PreToolUse or PostToolUse hook runs, so nothing inspects a tool call" not in text
    assert "this tool reads the two settings files in the checkout" in text


def test_both_settings_files_are_read_and_neither_is_claimed_about_the_machine(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    text = facts(scan(str(repository), 20_000))
    for name in SETTINGS_FILES:
        assert f"{name}: absent" in text
    assert "nothing on the machine outside it" in text


def test_one_reader_decides_which_key_an_mcp_configuration_lists_its_servers_under(tmp_path: Path) -> None:
    """An empty `mcpServers` beside a populated `servers` made two readers disagree."""

    assert servers_of({"mcpServers": {}, "servers": {"leaky": {"command": "node"}}}) == (
        "servers",
        {"leaky": {"command": "node"}},
    )
    repository = build_repo(tmp_path / "repo")
    (repository / ".mcp.json").write_text(
        json.dumps({"mcpServers": {}, "servers": {"leaky": {"command": "node", "args": ["s.js"]}}})
    )
    result = scan(str(repository), 20_000)
    body = render_markdown(result, compose(result, "p.json"), "cmd", VERSIONS, None, "2026-08-31")

    assert "MCP server 'leaky' runs `node s.js`" in facts(result)
    assert "in front of 1 of 1 server(s)" in body


def test_the_two_hooks_path_queries_are_the_only_calls_that_relax_an_override(repo_root: Path) -> None:
    """`core.hooksPath=/dev/null` is the answer to `--git-path hooks`, so those two calls drop it.

    Two, not one: `--git-path hooks` asks where the hooks are and
    `--git-common-dir` asks which git directory a linked worktree shares, which
    is what contains the first answer. Both documents said "one" while this
    assertion said two.
    """

    from guardrail_checkup._scan import HOOKS_PATH_CONFIG

    argv = _argv(Path("/tmp"), "rev-parse", "--git-path", "hooks", config=HOOKS_PATH_CONFIG)
    assert argv[3:] == [
        "-c",
        "core.fsmonitor=false",
        "-c",
        "core.quotePath=false",
        "--no-optional-locks",
        "rev-parse",
        "--git-path",
        "hooks",
    ]
    source = (repo_root / "src" / "guardrail_checkup" / "_scan.py").read_text(encoding="utf-8")
    # Two calls, both parts of the same question: where the hooks are, and which
    # git directory a linked worktree shares -- the one legitimate answer
    # outside the root, and the containment check needs it.
    assert source.count("config=HOOKS_PATH_CONFIG") == 2, "only the hooks-directory queries may relax an override"
    assert '_git(root, "rev-parse", "--git-path", "hooks", config=HOOKS_PATH_CONFIG)' in source
    assert '_git(root, "rev-parse", "--git-common-dir", config=HOOKS_PATH_CONFIG)' in source


# --- present, and not read ------------------------------------------------------


def oversized(path: Path) -> None:
    """A file past MAX_READ_BYTES. `_read` refuses it before it opens it."""

    path.write_text("# pad\n" * 200_000)


def with_a_nul(path: Path) -> None:
    """A file whose first SNIFF_BYTES hold a NUL. `_read` calls it binary."""

    path.write_bytes(b"/db/ @security-team\n" + b"\x00\x00binary\n")


def unreadable(path: Path) -> None:
    """A file the owner cannot open. `_read` catches the OSError."""

    path.write_text("/db/ @security-team\n")
    path.chmod(0o000)


#: One "present but never opened" shape per guardrail file that has a branch of
#: its own, and the row each branch has to print instead of the negative fact it
#: used to. Every negative below was an absence asserted about a file the same
#: run's `scope.unread` says was never read.
UNREADABLE = [
    ("CODEOWNERS", oversized, "pattern(s) with a required reviewer", "CODEOWNERS: present, not read"),
    ("CODEOWNERS", with_a_nul, "pattern(s) with a required reviewer", "CODEOWNERS: present, not read"),
    ("CODEOWNERS", unreadable, "pattern(s) with a required reviewer", "CODEOWNERS: present, not read"),
    (
        ".github/workflows/ci.yml",
        oversized,
        "no test runner in a run: step",
        ".github/workflows/ci.yml: present, not read",
    ),
    (
        ".github/workflows/ci.yml",
        with_a_nul,
        "no test runner in a run: step",
        ".github/workflows/ci.yml: present, not read",
    ),
    (
        ".github/workflows/ci.yml",
        unreadable,
        "no test runner in a run: step",
        ".github/workflows/ci.yml: present, not read",
    ),
    (".pre-commit-config.yaml", oversized, "present, 0 hook id(s)", ".pre-commit-config.yaml: present, not read"),
    (".pre-commit-config.yaml", with_a_nul, "present, 0 hook id(s)", ".pre-commit-config.yaml: present, not read"),
    (".pre-commit-config.yaml", unreadable, "present, 0 hook id(s)", ".pre-commit-config.yaml: present, not read"),
    (".claude/settings.json", oversized, "no PreToolUse hook", ".claude/settings.json: present, not read"),
    (".claude/settings.json", with_a_nul, "no PreToolUse hook", ".claude/settings.json: present, not read"),
    (".claude/settings.json", unreadable, "no PreToolUse hook", ".claude/settings.json: present, not read"),
    (".mcp.json", oversized, "no server is configured", "present but unreadable"),
    (".mcp.json", with_a_nul, "no server is configured", "present but unreadable"),
    (".mcp.json", unreadable, "no server is configured", "present but unreadable"),
    (".gitleaks.toml", oversized, "not configured (no gitleaks", "1 file(s) here were present and not read"),
    (".gitleaks.toml", with_a_nul, "not configured (no gitleaks", "1 file(s) here were present and not read"),
    (".gitleaks.toml", unreadable, "not configured (no gitleaks", "1 file(s) here were present and not read"),
    (".secrets.baseline", oversized, "not configured (no gitleaks", "1 file(s) here were present and not read"),
]


@pytest.mark.parametrize(
    "relative,make,negative,expected", UNREADABLE, ids=[f"{item[0]} {item[1].__name__}" for item in UNREADABLE]
)
def test_a_file_that_is_present_and_not_read_never_produces_a_negative_fact(
    tmp_path: Path, relative: str, make, negative: str, expected: str
) -> None:
    """The report may not answer a question about a file it never opened.

    One run printed "CODEOWNERS: 0 pattern(s) with a required reviewer", "tests
    not found", "secret scanning: not configured" and "no PreToolUse hook" about
    four files its own `scope.unread` listed as never read: `read(...) or ""`
    coerced the absence to an empty file and every detector then measured that.
    """

    if make is unreadable and os.geteuid() == 0:
        pytest.skip("root reads a file with mode 000")
    repository = tmp_path / "unread"
    path = repository / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    make(path)
    (repository / "app").mkdir()
    (repository / "app" / "main.py").write_text("x = 1\n")

    result = scan(str(repository), 20_000)
    text = facts(result)

    assert relative in result.unread, (relative, result.read, result.unread)
    assert relative not in result.read
    assert negative not in text, text
    assert expected in text, text


def test_a_settings_file_that_does_not_parse_says_nothing_about_the_hooks_in_it(tmp_path: Path) -> None:
    """The realistic one: a typo in `settings.json`, and two rows about what it configures.

    "not valid JSON" was followed by "no PreToolUse hook" and "no PostToolUse
    hook" about the same file. The file could not be parsed; nothing here knows
    what it configures.
    """

    repository = tmp_path / "typo"
    (repository / ".claude").mkdir(parents=True)
    (repository / ".claude" / "settings.json").write_text('{"hooks": {"PreToolUse": [ }\n')
    (repository / "app.py").write_text("x = 1\n")

    text = facts(scan(str(repository), 20_000))

    assert ".claude/settings.json: not valid JSON" in text
    assert "so what it configures here is unknown" in text
    assert "no PreToolUse hook" not in text
    assert "no PostToolUse hook" not in text


def test_a_matcher_this_tool_cannot_evaluate_is_not_a_matcher_that_inspects_nothing(tmp_path: Path) -> None:
    """`(?<x>Write)` is a JavaScript named group, and it does catch `Write`."""

    repository = tmp_path / "jsre"
    (repository / ".claude").mkdir(parents=True)
    (repository / ".claude" / "settings.json").write_text(
        json.dumps(
            {"hooks": {"PreToolUse": [{"matcher": "(?<x>Write)", "hooks": [{"type": "command", "command": "x"}]}]}}
        )
    )
    (repository / "app.py").write_text("x = 1\n")

    text = facts(scan(str(repository), 20_000))

    assert "a write to any path is inspected by a hook this repository checks in" in text
    assert "none matches a write tool" not in text
    assert "no write tool is inspected by this event" not in text


def test_a_matcher_that_is_no_regular_expression_at_all_is_reported_as_unchecked(tmp_path: Path) -> None:
    repository = tmp_path / "badre"
    (repository / ".claude").mkdir(parents=True)
    (repository / ".claude" / "settings.json").write_text(
        json.dumps(
            {"hooks": {"PreToolUse": [{"matcher": "[unclosed", "hooks": [{"type": "command", "command": "x"}]}]}}
        )
    )
    (repository / "app.py").write_text("x = 1\n")

    text = facts(scan(str(repository), 20_000))

    assert "one is not a regular expression this tool can evaluate" in text
    assert "whether a write tool is inspected by this event was not checked" in text
    assert "no write tool is inspected by this event" not in text


# --- per-machine configuration this repository gitignores -----------------------


def test_a_gitignored_mcp_configuration_is_read_from_disk_and_said_to_be(tmp_path: Path) -> None:
    """`.mcp.json` carries per-machine server config and is commonly gitignored.

    Looked for in the git listing alone, the report stated an absolute -- "no
    tool servers are configured in this repository, so none can be screened
    here" -- about the file the agent actually loads, sitting in the checkout.
    """

    repository = tmp_path / "ignored"
    (repository / "db").mkdir(parents=True)
    (repository / "db" / "queries.py").write_text("x = 1\n")
    (repository / ".gitignore").write_text(".mcp.json\n")
    git(repository.parent, "init", "-q", "-b", "main", str(repository))
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "first")
    (repository / ".mcp.json").write_text(json.dumps({"mcpServers": {"s": {"command": "node", "args": ["s.js"]}}}))

    result = scan(str(repository), 20_000)
    text = facts(result)

    assert ".mcp.json" not in result.files, "the fixture has to be gitignored for this to mean anything"
    assert ".mcp.json: present on disk, not checked in" in text
    assert ".mcp.json: MCP server 's' runs `node s.js`" in text
    assert "no MCP server configuration found" not in text
    assert ".mcp.json" in result.read
    assert "mcp-wrapped.json" in compose(result, "p.json").drafts


def test_a_gitignored_local_settings_file_is_said_to_be_on_disk_and_not_checked_in(tmp_path: Path) -> None:
    repository = tmp_path / "ignored-settings"
    (repository / ".claude").mkdir(parents=True)
    (repository / ".gitignore").write_text(".claude/settings.local.json\n")
    (repository / "app.py").write_text("x = 1\n")
    git(repository.parent, "init", "-q", "-b", "main", str(repository))
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "first")
    (repository / ".claude" / "settings.local.json").write_text(
        json.dumps({"hooks": {"PreToolUse": [{"matcher": "Write", "hooks": [{"type": "command", "command": "x"}]}]}})
    )

    text = facts(scan(str(repository), 20_000))

    assert ".claude/settings.local.json: present on disk, not checked in" in text
    assert "a write to any path is inspected by a hook this repository checks in" in text


# --- what a workflow runs, as opposed to what it mentions ------------------------


#: A workflow that names a test runner somewhere that is not a command. Each of
#: these made the report state that a change is tested before review, for a
#: workflow whose only command is `echo hi`.
NOT_A_COMMAND = [
    (
        "name",
        "on: [pull_request]\njobs:\n  a:\n    steps:\n      - name: why we dropped pytest\n        run: echo hi\n",
    ),
    (
        "if",
        "on: [pull_request]\njobs:\n  a:\n    steps:\n      - if: contains(github.head_ref, 'pytest')\n"
        "        run: echo hi\n",
    ),
    (
        "env",
        "on: [pull_request]\njobs:\n  a:\n    env:\n      NOTE: pytest is not used here\n"
        "    steps:\n      - run: echo hi\n",
    ),
    ("job id", "on: [pull_request]\njobs:\n  pytest:\n    steps:\n      - run: echo hi\n"),
    ("uses", "on: [pull_request]\njobs:\n  a:\n    steps:\n      - uses: acme/cargo test@v1\n"),
]


@pytest.mark.parametrize("where,body", NOT_A_COMMAND, ids=[item[0] for item in NOT_A_COMMAND])
def test_a_test_runner_that_is_not_a_command_is_not_a_workflow_that_runs_tests(
    tmp_path: Path, where: str, body: str
) -> None:
    repository = tmp_path / f"wf-{where.replace(' ', '-')}"
    (repository / ".github" / "workflows").mkdir(parents=True)
    (repository / ".github" / "workflows" / "ci.yml").write_text(body)

    text = facts(scan(str(repository), 20_000))

    assert "no test runner in a run: step" in text, text
    assert "a test runner is named here and this workflow runs on pull requests" not in text
    assert "a change can reach review without this workflow having judged it" in text


@pytest.mark.parametrize(
    "body",
    [
        "on: [pull_request]\njobs:\n  a:\n    steps:\n      - run: pytest -q\n",
        "on: [pull_request]\njobs:\n  a:\n    steps:\n      - run: |\n          uv sync\n          pytest -q\n",
        "on: [pull_request]\njobs:\n  a:\n    steps:\n      - name: tests\n        run: >\n          npm test\n",
    ],
    ids=["inline", "block scalar", "folded scalar after a name"],
)
def test_a_test_runner_in_a_run_step_is_found_however_the_step_is_written(tmp_path: Path, body: str) -> None:
    repository = tmp_path / "wfrun"
    (repository / ".github" / "workflows").mkdir(parents=True)
    (repository / ".github" / "workflows" / "ci.yml").write_text(body)

    text = facts(scan(str(repository), 20_000))

    assert "a test runner is named in a run: step, runs on pull requests" in text
    assert "whether it ran, and on what, was not checked, because nothing here was executed" in text


# --- what counts as a known screen -----------------------------------------------


#: The command lines that must not be reported as running a known screen. The
#: check took the last path segment, which is exactly where an npm scope stops
#: being part of the name.
NOT_A_SCREEN = [
    ("npm scope", {"command": "npx", "args": ["-y", "@evil/egresswall"]}),
    ("a binary the checkout ships", {"command": "./egresswall"}),
    ("a relative path", {"command": "bin/egresswall"}),
    ("a scoped runner", {"command": "@evil/npx", "args": ["egresswall"]}),
]


@pytest.mark.parametrize("case,entry", NOT_A_SCREEN, ids=[item[0] for item in NOT_A_SCREEN])
def test_only_a_bare_name_or_an_absolute_path_counts_as_a_known_screen(tmp_path: Path, case: str, entry: dict) -> None:
    repository = tmp_path / f"screen-{case.replace(' ', '-')}"
    repository.mkdir()
    (repository / ".mcp.json").write_text(json.dumps({"mcpServers": {"s": entry}}))

    text = facts(scan(str(repository), 20_000))

    assert "no screen in the command line" in text, text
    assert "the command it runs is one of the known screens" not in text


@pytest.mark.parametrize("command", ["egresswall", "/usr/local/bin/egresswall"], ids=["on PATH", "absolute"])
def test_a_screen_named_bare_or_by_absolute_path_is_still_a_screen(tmp_path: Path, command: str) -> None:
    repository = tmp_path / f"ok-{command.count('/')}"
    repository.mkdir()
    (repository / ".mcp.json").write_text(json.dumps({"mcpServers": {"s": {"command": command, "args": ["proxy"]}}}))

    assert "the command it runs is one of the known screens" in facts(scan(str(repository), 20_000))


def test_a_backtick_in_an_mcp_command_line_cannot_close_the_span_it_is_rendered_in(tmp_path: Path) -> None:
    """`md` is the escaper for markdown text, and a code span is where it does not run."""

    repository = tmp_path / "tick"
    repository.mkdir()
    (repository / ".mcp.json").write_text(
        json.dumps({"mcpServers": {"s": {"command": "node", "args": ["a`b", "```", "x|y"]}}})
    )

    result = scan(str(repository), 20_000)
    body = render_markdown(result, compose(result, "p.json"), "cmd", VERSIONS, None, "2026-08-31")
    row = next(line for line in body.splitlines() if "MCP server" in line)

    assert "; no screen in the command line" in row, row
    assert row.endswith("|") and row.count("|") - row.count("\\|") == 4, row
    assert "\\`" not in row, "a backslash is literal inside a code span"
    assert row.count("`") % 2 == 0, row


# --- one recorder, one rendered report -------------------------------------------


def test_every_file_opened_under_the_repository_is_named_in_the_scope_it_prints(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """§1's promise, asserted at the syscall rather than at one function.

    `test_every_file_this_tool_opens_is_named_in_the_scope_it_prints` spies on
    `_read`, so a branch that opens a file some other way is invisible to it --
    and one did: the secret-scanning sweep called `_read` directly, past the
    recorder, and a report cited `.gitleaks.toml:3` while `scope.read` did not
    name the file. This one watches `open` and `Path.read_bytes` instead, which
    is every way this package or its siblings can read a byte.
    """

    repository = build_repo(tmp_path / "repo")
    (repository / ".gitleaks.toml").write_text("[extend]\nuseDefault = true\n")
    (repository / ".secrets.baseline").write_text('{"results": {}}\n')
    (repository / "CODEOWNERS").write_text("/db/ @platform\n")
    (repository / ".pre-commit-config.yaml").write_text("repos:\n  - repo: x\n    hooks:\n      - id: gitleaks\n")
    (repository / ".github" / "workflows").mkdir(parents=True)
    (repository / ".github" / "workflows" / "ci.yml").write_text(
        "on: [pull_request]\njobs:\n  t:\n    steps:\n      - run: pytest\n"
    )
    (repository / "pyproject.toml").write_text("[tool.ruff]\nline-length = 120\n")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "add the guardrail files this tool reads")

    root = Path(os.path.realpath(repository))
    opened: list[str] = []
    real_open, real_read_bytes = open, Path.read_bytes

    def spy_open(file, *args, **kwargs):
        opened.append(os.fspath(file))
        return real_open(file, *args, **kwargs)

    def spy_read_bytes(self):
        opened.append(os.fspath(self))
        return real_read_bytes(self)

    monkeypatch.setattr("builtins.open", spy_open)
    monkeypatch.setattr(Path, "read_bytes", spy_read_bytes)
    result = scan(str(repository), 20_000)
    composed = compose(result, "p.json")
    document = json.loads(render_json(result, composed, "cmd", VERSIONS, None, "2026-08-31"))
    monkeypatch.undo()

    accounted = set(document["scope"]["read"]) | set(document["scope"]["unread"])
    inside = {
        os.path.relpath(os.path.realpath(item), root).replace(os.sep, "/")
        for item in opened
        if os.path.realpath(item).startswith(f"{root}{os.sep}")
    }
    inside = {item for item in inside if not item.startswith(".git/")}
    assert inside, "nothing under the repository was opened at all"
    assert inside <= accounted, sorted(inside - accounted)
    for named in (".gitleaks.toml", ".secrets.baseline", "CODEOWNERS", "pyproject.toml"):
        assert named in document["scope"]["read"], (named, document["scope"]["read"])


def test_no_repository_string_renders_as_a_link_an_image_or_html_under_a_commonmark_parser(
    tmp_path: Path,
) -> None:
    """The whole report through a real parser, not a regular expression over it.

    `composed.validations` was the one repository-controlled string that passed
    neither `md` nor `_code`, so a plan file named `[click](evil.example) <img
    src=x onerror=…> plan.json` put a live link and a live image into §2 of the
    document the reader hands to someone else. The suite's own fixtures never
    reached that renderer, because it only runs when a policy loads *and* a plan
    validates with issues.
    """

    from markdown_it import MarkdownIt
    from test_compose import documents_that_validate_with_issues

    policy, plan = documents_that_validate_with_issues()
    repository = build_repo(tmp_path / "hostile")
    (repository / "policy.json").write_text(json.dumps(policy))
    (repository / "[click](evil.example) <img src=x onerror=alert(1)> plan.json").write_text(json.dumps(plan))
    (repository / ".mcp.json").write_text(
        json.dumps({"mcpServers": {"[a](evil.example)": {"command": "node", "args": ["a`b", "<img src=x>"]}}})
    )
    (repository / "CODEOWNERS").write_text("[db](https://evil.example)/ @platform\ndb/ @platform\n")
    (repository / ".cursor" / "rules").mkdir(parents=True)
    (repository / ".cursor" / "rules" / "<script>alert(1) never db.md").write_text("never edit db/\n")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "fix: [SECURITY REVIEW PASSED](https://evil.example) <b>all clear</b>")

    result = scan(str(repository), 20_000)
    composed = compose(result, "p.json")
    body = render_markdown(result, composed, "cmd", VERSIONS, None, "2026-08-31")

    assert composed.validations, "the validations renderer has to run for this to mean anything"
    html = MarkdownIt("commonmark", {"html": True}).render(body)
    inert = re.sub(r"<pre>.*?</pre>", "", html, flags=re.S)
    inert = re.sub(r"<code[^>]*>.*?</code>", "", inert, flags=re.S)
    for tag in ("<a ", "<a>", "<img", "<script", "<iframe", "<b>", "<!--"):
        assert tag not in inert, (tag, [line for line in inert.splitlines() if tag in line])
    # And the hostile text is still *there*, inside the span: a report that
    # dropped the name would hide which file the issue is about.
    assert "[click](evil.example) <img src=x onerror=alert(1)> plan.json: criterion_uncovered" in body


def test_the_falsifier_command_prints_the_figure_printed_beside_it(tmp_path: Path) -> None:
    """A report sells §2's third column as the command that disproves the claim.

    The shipped command pruned `./.git` and nothing else and counted files
    *named* `test_*`: on the recorded Nemisis run it printed 605 beside a cell
    that said 148, because it walked `.venv/` and `__pycache__/` and because a
    file in a test path is not a file named `test_*`. Both halves come from the
    listing §1 names now, and this runs the command to prove it -- in a
    checkout, where the listing is `git ls-files`, and in a plain directory,
    where it is `os.walk` minus SKIP_DIRECTORIES.
    """

    for name, is_git in (("checkout", True), ("plain", False)):
        repository = tmp_path / name
        (repository / "tests").mkdir(parents=True)
        (repository / "tests" / "test_orders.py").write_text("def test_x():\n    assert True\n")
        (repository / "src").mkdir()
        (repository / "src" / "checkout.test.ts").write_text("test('x', () => {});\n")
        (repository / "src" / "app.py").write_text("x = 1\n")
        # The two directories the shipped command walked into: a vendored suite
        # is not this repository's test layout, and neither list counts it.
        (repository / ".venv" / "lib" / "tests").mkdir(parents=True)
        (repository / ".venv" / "lib" / "tests" / "test_vendored.py").write_text("x = 1\n")
        (repository / "__pycache__").mkdir()
        (repository / "__pycache__" / "test_cached.py").write_text("x = 1\n")
        if is_git:
            git(repository, "init", "-q", "-b", "main")
            (repository / ".gitignore").write_text(".venv/\n__pycache__/\n")
            git(repository, "add", "-A")
            git(repository, "commit", "-q", "-m", "first")

        result = scan(str(repository), 20_000)
        assert result.is_git is is_git
        body = render_markdown(result, compose(result, "p.json"), "cmd", VERSIONS, None, "2026-08-31")
        row = next(line for line in body.splitlines() if line.startswith("| \u201cTesting: 0/0"))
        figure, command = row.strip("| ").split(" | ")[1:]
        # Out of its code span, and with the table's `|` escapes undone.
        command = command.strip().strip("`").replace("\\|", "|")
        printed = subprocess.run(
            command,
            shell=True,
            cwd=repository,
            capture_output=True,
            text=True,
            env={**os.environ, **GIT_ENV},
        )
        assert figure == "2 file(s) sit in a test path", figure
        assert printed.stdout.strip() == "2", (name, printed.stdout, printed.stderr)


def test_section_five_names_the_three_tools_this_one_does_not_replace(fixture_repo: Path) -> None:
    """docs/comparison.md says the report is honest about the other three; here it is.

    The page claimed this package is "defended by being honest about the other
    three in the report it writes" while no rendered report named one of them.
    Each phrase here is in a file under `docs/evidence/`, which
    tests/test_comparison_truth.py holds it against.
    """

    result = scan(str(fixture_repo), 20_000)
    body = render_markdown(result, compose(result, "p.json"), "cmd", VERSIONS, None, "2026-08-31")
    section = body.split("## 5. What this did not cover")[1].split("## 6.")[0]
    for name, fact in NOT_REPLACED:
        assert name in section, name
        assert fact in section, fact
    assert "replaces none of them" in section
    assert "The third-party tools named in \u00a72 and \u00a75 are unaffiliated" in body


def test_a_cut_example_list_in_the_egresswall_paragraph_says_it_was_cut(tmp_path: Path) -> None:
    """The one truncation in the report that did not announce itself.

    Four of five thousand servers were named and the sentence ended in a full
    stop, so it read as the whole set. Every other cap in the report says how
    many it left out.
    """

    repository = tmp_path / "servers"
    repository.mkdir()
    (repository / "a.py").write_text("x = 1\n")
    (repository / ".mcp.json").write_text(
        json.dumps({"mcpServers": {f"s{i:03d}": {"url": f"https://x{i}.example/"} for i in range(200)}})
    )
    result = scan(str(repository), 20_000)
    composed = compose(result, "p.json")
    body = render_markdown(result, composed, "cmd", VERSIONS, None, "2026-08-31")

    assert len(composed.unwrapped) == 200
    assert f"and {200 - EXAMPLES} more" in body
    assert body.count("`s004`") == 0, "EXAMPLES names four, and the fifth is behind the count"
