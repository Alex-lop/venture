"""Every scan step is bounded, and the bounds are timed rather than asserted in prose.

A repository is untrusted input, and so is its size: a checked-in CODEOWNERS, a
`.mcp.json` and a monorepo's file list are all things a stranger controls. Each
test here builds the worst case a bound allows -- or, where a step has two
bounds, the case that isolates the one it is about -- and asserts the run is
still quick, so a quadratic step reintroduced later fails on the clock rather
than on somebody's afternoon.

The worst case is a shape, not a size: a fixture of 1 MiB files whose lines are
33 bytes long looked like it held the workflow cap and was three times cheaper
than the same megabyte in two-byte lines, which is why two of these tests build
the line shape rather than the file count.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

from conftest import GIT_ENV, git

from guardrail_checkup import (
    AGENT_FILE_LIMIT,
    HISTORY_COMMITS,
    HISTORY_PATHS,
    LINE_BUDGET,
    MAX_READ_BYTES,
    OWNER_LIMIT,
    SERVER_ROWS,
    SIGNATURE_SCAN_BYTES,
    SIGNATURE_SCAN_FILES,
    WORKFLOW_LIMIT,
    Scan,
    compose,
    render_markdown,
    scan,
)
from guardrail_checkup._cli import main
from guardrail_checkup._scan import _record, history

#: The wall-clock budget for one bounded step, and for a whole run over a
#: synthetic repository of 5,000 files. Generous by an order of magnitude
#: against the measurements: the point is to fail on a quadratic step, not on a
#: slow machine.
STEP_SECONDS = 2.0
RUN_SECONDS = 30.0

#: 149,796 x 7 bytes = 1,048,572, one line under MAX_READ_BYTES: the largest
#: CODEOWNERS this tool will read, which is where the worst case lives.
BIGGEST_CODEOWNERS = 149_796


def _history(root: Path, records: list[str]) -> Path:
    """A synthetic history with no working tree, written by `git fast-import`.

    Both history caps are counted in thousands -- 2,000 commits and 100,000 path
    entries -- and `git commit` cannot build either inside a test. Nothing is
    checked out because `history()` reads the log and never the working tree.
    """

    root.mkdir(parents=True)
    git(root, "init", "-q", "-b", "main")
    done = subprocess.run(
        ["git", "-C", str(root), "fast-import", "--quiet"],
        input="".join(records).encode(),
        capture_output=True,
        env={**os.environ, **GIT_ENV},
    )
    assert done.returncode == 0, done.stderr
    return root


def _commit(mark: int, subject: str, parent: int | None) -> str:
    return (
        f"commit refs/heads/main\nmark :{mark}\n"
        f"committer Test Author <test@example.invalid> {1700000000 + mark} +0000\n"
        f"data {len(subject)}\n{subject}\n" + (f"from :{parent}\ndeleteall\n" if parent else "")
    )


def _files(root: Path, count: int, folder: str = "db") -> Path:
    (root / folder).mkdir(parents=True)
    for number in range(count):
        (root / folder / f"f{number:05d}.py").write_text("x = 1\n")
    return root


def test_the_largest_codeowners_this_tool_reads_does_not_decide_how_long_a_checkup_takes(
    tmp_path: Path,
) -> None:
    """The ranking asked `_matches` for every (pattern, file) pair.

    A pattern that matches nothing is the normal case and paid the whole
    product: 5,000 files under `db/` and a 1 MiB CODEOWNERS of one non-matching
    pattern took 92 seconds, and that one comprehension was the entire runtime.
    """

    repository = _files(tmp_path / "owners", 5_000)
    (repository / "CODEOWNERS").write_text("/zz @o\n" * BIGGEST_CODEOWNERS)

    started = time.monotonic()
    result = scan(str(repository), 20_000)
    elapsed = time.monotonic() - started

    assert elapsed < STEP_SECONDS, elapsed
    assert [item.slug for item in result.candidates] == ["db"]
    assert not any("CODEOWNERS" in line for line in result.candidates[0].evidence)


def test_the_largest_codeowners_of_distinct_matching_patterns_is_capped_and_says_so(tmp_path: Path) -> None:
    """The cap is documented, and the row says when it bit."""

    repository = _files(tmp_path / "distinct", 500)
    (repository / "CODEOWNERS").write_text("".join(f"/db/f{number:05d}.py @o\n" for number in range(5_000)))

    started = time.monotonic()
    result = scan(str(repository), 20_000)
    elapsed = time.monotonic() - started

    assert elapsed < STEP_SECONDS, elapsed
    assert len(result.owned) == OWNER_LIMIT
    row = next(item for item in result.findings if item.fact.startswith("CODEOWNERS:"))
    assert f"the ranking tested the first {OWNER_LIMIT:,} distinct pattern(s)" in row.fact


def test_a_dense_mcp_configuration_does_not_decide_how_long_a_checkup_takes(tmp_path: Path) -> None:
    """`_line_of` ran once per server over the whole file: O(servers x lines)."""

    repository = tmp_path / "servers"
    repository.mkdir()
    (repository / "a.py").write_text("x = 1\n")
    (repository / ".mcp.json").write_text(
        json.dumps({"mcpServers": {f"s{i:05d}": {"url": f"https://x{i}.example/"} for i in range(5_000)}}, indent=1)
    )

    started = time.monotonic()
    result = scan(str(repository), 20_000)
    elapsed = time.monotonic() - started

    assert elapsed < STEP_SECONDS, elapsed
    rows = [item for item in result.findings if "MCP server" in item.fact]
    assert len(rows) == SERVER_ROWS
    assert f"5,000 server(s) configured; the first {SERVER_ROWS} in sorted order have a row below" in "\n".join(
        item.fact for item in result.findings
    )
    # The line number is the one in the file, not a constant: the index is real.
    assert len({item.where for item in rows}) > 1


def test_a_directory_of_rule_files_does_not_decide_how_long_a_checkup_takes(tmp_path: Path) -> None:
    """`.cursor/rules/` was read whole: files x lines, with no bound on either.

    2,000 files of 1 MiB apiece took 50 seconds and produced 2,015 rows -- over
    the demo's own budget, and unreadable long before that.
    """

    repository = tmp_path / "rules"
    (repository / ".cursor" / "rules").mkdir(parents=True)
    blob = "never edit db/ path here\n" * 4_000  # ~100 KiB each, 500 of them
    for number in range(500):
        (repository / ".cursor" / "rules" / f"r{number:05d}.md").write_text(blob)

    started = time.monotonic()
    result = scan(str(repository), 20_000)
    elapsed = time.monotonic() - started

    assert elapsed < STEP_SECONDS, elapsed
    facts = "\n".join(item.fact for item in result.findings)
    assert f"the first {AGENT_FILE_LIMIT} in sorted order were read" in facts
    assert len([item for item in result.findings if item.fact.startswith(".cursor/rules/r")]) == AGENT_FILE_LIMIT


def test_a_repository_of_workflows_does_not_decide_how_long_a_checkup_takes(tmp_path: Path) -> None:
    """`.github/workflows/` had no cap at all, and it is the repository's choice.

    Every workflow is read at up to MAX_READ_BYTES and walked line by line by
    `_uncommented`, `_run_steps` and `_triggers`, and `_uncommented` was walked
    twice -- once for step 6 and again for step 7. 1,000 workflows of 1 MiB was
    44 seconds of scan, 22x this budget, and 1,015 rows. This holds the file
    cap: the files are sized at half of what LINE_BUDGET allows each of them, so
    the budget cannot bite here and the row below is about WORKFLOW_LIMIT. The
    test after this one holds the line budget, at the worst line shape.
    """

    repository = tmp_path / "workflows"
    (repository / ".github" / "workflows").mkdir(parents=True)
    filler = "a: filler line, no comment in it\n" * (LINE_BUDGET // (WORKFLOW_LIMIT * 2))
    blob = "on: [push]\njobs:\n  t:\n    steps:\n      - run: echo hi\n" + filler
    assert len(blob) < MAX_READ_BYTES, len(blob)
    for number in range(WORKFLOW_LIMIT + 200):
        (repository / ".github" / "workflows" / f"w{number:05d}.yml").write_text(blob)

    started = time.monotonic()
    result = scan(str(repository), 20_000)
    elapsed = time.monotonic() - started

    assert elapsed < STEP_SECONDS, elapsed
    assert len([item for item in result.findings if item.fact.startswith(".github/workflows/w")]) == WORKFLOW_LIMIT
    assert f"the first {WORKFLOW_LIMIT} in sorted order were read" in "\n".join(item.fact for item in result.findings)


def test_a_repository_of_checked_in_json_does_not_decide_how_long_the_signature_scan_takes(tmp_path: Path) -> None:
    """The agent-plan-lint signature sweep reads the whole listing, by design.

    `--max-files` was deliberately removed as its bound, to stop "no policy
    found" being said about a repository whose policy sorted past the cap, and
    nothing was put in its place: 20,000 JSON files of 1 MiB took 18.7 seconds
    of compose with `--max-files 1`. SIGNATURE_SCAN_BYTES bounds the bytes
    instead, and §2 says how many files were left unread.
    """

    repository = tmp_path / "json"
    (repository / "data").mkdir(parents=True)
    blob = '{"pad": "' + "x" * 1_000_000 + '"}'
    for number in range(SIGNATURE_SCAN_BYTES // len(blob) + 30):
        (repository / "data" / f"j{number:05d}.json").write_text(blob)

    result = scan(str(repository), 20_000)
    started = time.monotonic()
    composed = compose(result, "/etc/egresswall/policy.json")
    elapsed = time.monotonic() - started

    assert elapsed < STEP_SECONDS, elapsed
    assert composed.signature_skipped >= 20, composed.signature_skipped
    assert len(result.read) * 1_000_000 < SIGNATURE_SCAN_BYTES + 2_000_000, len(result.read)
    # And the report says so, rather than reporting an absence it did not check.
    versions = {"guardrail-checkup": "0", "agent-plan-lint": "0", "egresswall": "0", "python": "3"}
    body = render_markdown(result, composed, "run .", versions, None, "2026-08-31")
    assert f"{composed.signature_skipped:,} more were listed and not read" in body


def _worst_case_files(directory: Path, count: int, line: str, suffix: str, header: str = "") -> None:
    """`count` files just under MAX_READ_BYTES, each one `line` repeated.

    The size the read cap allows, in the line shape that costs the most: the
    file caps bound the files and the work is per line, so a fixture of a few
    long lines is not the worst case a documented bound allows -- it is the
    shape that made the cap look like it held. Just under the cap, because a
    file one byte over it is not read at all, which is the cheapest case there
    is rather than the worst.
    """

    directory.mkdir(parents=True)
    body = header + line * ((MAX_READ_BYTES - len(header) - 1) // len(line))
    assert len(body) < MAX_READ_BYTES, len(body)
    for number in range(count):
        (directory / f"f{number:05d}{suffix}").write_text(body)


def test_the_worst_line_shape_a_rule_directory_allows_is_still_one_step(tmp_path: Path) -> None:
    """AGENT_FILE_LIMIT counts files; `_FORBIDS` and `_PATHISH` cost per line.

    64 files at the read cap, each of the shortest line that matches `_FORBIDS`
    and not `_PATHISH` -- so both regexes run on every one of 8.4 million lines
    -- was 2.8 seconds against this budget, on a repository inside every
    documented cap. The suite's other fixture is 500 files of ~100 KiB, which is
    0.2 seconds and never touched the axis that ran away. LINE_BUDGET bounds it
    now, and the row says how many files were actually read.
    """

    repository = tmp_path / "rules-worst"
    _worst_case_files(repository / ".cursor" / "rules", AGENT_FILE_LIMIT + 5, "never a\n", ".md")

    started = time.monotonic()
    result = scan(str(repository), 20_000)
    elapsed = time.monotonic() - started

    assert elapsed < STEP_SECONDS, elapsed
    row = next(item for item in result.findings if item.fact.startswith(".cursor/rules:"))
    read = len([item for item in result.findings if " lines, " in item.fact])
    assert 0 < read < AGENT_FILE_LIMIT, "the line budget bit before the file cap did"
    assert f"the first {read} in sorted order were read" in row.fact
    assert f"{AGENT_FILE_LIMIT + 5 - read:,} more file(s)" in row.consequence


def test_the_worst_line_shape_a_workflow_directory_allows_is_still_one_step(tmp_path: Path) -> None:
    """WORKFLOW_LIMIT counts files; `_run_steps` and `_triggers` cost per line.

    32 workflows at the read cap, every line of them inside a `run: |` block
    scalar, so the block collector copies the whole file: 5.9 million lines and
    2.8 seconds against this budget. The suite's other fixture is 33-byte filler
    lines, which is 0.9 seconds, so the cap looked like it held.
    """

    repository = tmp_path / "workflows-worst"
    _worst_case_files(
        repository / ".github" / "workflows",
        WORKFLOW_LIMIT + 5,
        "        x\n",
        ".yml",
        header="on: [push]\njobs:\n  t:\n    steps:\n      - run: |\n",
    )

    started = time.monotonic()
    result = scan(str(repository), 20_000)
    elapsed = time.monotonic() - started

    assert elapsed < STEP_SECONDS, elapsed
    row = next(item for item in result.findings if item.fact.startswith(".github/workflows:"))
    read = len([item for item in result.findings if "run: step" in item.fact])
    assert 0 < read < WORKFLOW_LIMIT, "the line budget bit before the file cap did"
    assert f"the first {read} in sorted order were read" in row.fact
    # And the secret-scanning row counts the unread ones rather than calling a
    # scanner absent over files nobody opened.
    scanning = next(item for item in result.findings if item.fact.startswith("secret scanning:"))
    assert f"{WORKFLOW_LIMIT + 5 - read} file(s) here were present and not read" in scanning.fact


def test_neither_line_budget_bites_on_workflows_and_rules_of_the_ordinary_size(tmp_path: Path) -> None:
    """The budget is for the pathological case, not for a repository anyone has."""

    repository = tmp_path / "ordinary"
    (repository / ".github" / "workflows").mkdir(parents=True)
    (repository / ".cursor" / "rules").mkdir(parents=True)
    for number in range(WORKFLOW_LIMIT):
        (repository / ".github" / "workflows" / f"w{number}.yml").write_text(
            "on: [pull_request]\njobs:\n  t:\n    steps:\n      - run: pytest\n"
        )
    for number in range(AGENT_FILE_LIMIT):
        (repository / ".cursor" / "rules" / f"r{number}.md").write_text("never edit db/\n" * 200)

    result = scan(str(repository), 20_000)

    assert len([item for item in result.findings if item.fact.startswith(".github/workflows/w")]) == WORKFLOW_LIMIT
    assert len([item for item in result.findings if item.fact.startswith(".cursor/rules/r")]) == AGENT_FILE_LIMIT
    assert not [item for item in result.findings if "in sorted order were read" in item.fact]


def test_a_hundred_thousand_files_through_the_recorder_do_not_decide_how_long_a_checkup_takes() -> None:
    """`_record` de-duplicated against two lists, which is O(files²).

    Every `_read` in the package goes through it, and the signature scan opens
    every checked-in `.json` file the listing names, so the cost of recording
    the reads overtook the cost of the reads: 200,000 files was 100 seconds of
    `_record` inside a 126-second run, and the step crossed this budget at about
    18,000 files -- inside the default `--max-files`, which does not bound that
    sweep by design. The lists are still the ordered ones §1 and `scope.read`
    render; the membership test is a set.
    """

    result = Scan(
        given_path=".",
        root=Path("."),
        head=None,
        files=[],
        all_files=[],
        total_files=0,
        truncated=False,
        max_files=20_000,
        is_git=False,
        languages=[],
        extensions=0,
        total_bytes=0,
    )
    names = [f"d{number // 1000:03d}/f{number:06d}.json" for number in range(100_000)]

    started = time.monotonic()
    for number, relative in enumerate(names):
        _record(result, relative, "{}" if number % 2 else None)
    elapsed = time.monotonic() - started

    assert elapsed < STEP_SECONDS, elapsed
    assert len(result.read) + len(result.unread) == len(names)
    # Still idempotent, and still ordered: the sets are shadows of the lists.
    _record(result, names[0], "{}")
    assert result.unread[:2] == names[:1] + names[2:3]
    assert len(result.read) + len(result.unread) == len(names)


def test_a_repository_of_tiny_checked_in_json_does_not_decide_how_long_the_signature_scan_takes(
    tmp_path: Path,
) -> None:
    """The byte budget bounds what a file costs to read, not what it costs to open.

    A repository of tiny checked-in JSON never spends 64 MiB, so the sweep read
    every one of them: 100,000 files is eight seconds of `open` alone.
    SIGNATURE_SCAN_FILES bounds the opens, and the remainder goes into the same
    clause §2 already carries for the byte budget.
    """

    repository = tmp_path / "tiny"
    (repository / "data").mkdir(parents=True)
    for number in range(SIGNATURE_SCAN_FILES + 30):
        (repository / "data" / f"j{number:06d}.json").write_text('{"a": 1}')

    result = scan(str(repository), 20_000)
    started = time.monotonic()
    composed = compose(result, "/etc/egresswall/policy.json")
    elapsed = time.monotonic() - started

    assert elapsed < STEP_SECONDS, elapsed
    assert composed.signature_skipped == 30, composed.signature_skipped
    versions = {"guardrail-checkup": "0", "agent-plan-lint": "0", "egresswall": "0", "python": "3"}
    body = render_markdown(result, composed, "run .", versions, None, "2026-08-31")
    assert "30 more were listed and not read" in body


def test_a_whole_run_over_five_thousand_files_finishes_well_inside_the_demo_budget(tmp_path: Path) -> None:
    """Listing, inventory, history, ranking, composition and rendering, end to end."""

    repository = _files(tmp_path / "big", 5_000)
    (repository / "CODEOWNERS").write_text("/db/ @platform\n")
    git(repository, "init", "-q", "-b", "main")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "fix: the first repair")

    started = time.monotonic()
    code = main(["run", str(repository), "--out", str(tmp_path / "r.md"), "--emit-dir", str(tmp_path / "d")])
    elapsed = time.monotonic() - started

    assert code == 0
    assert elapsed < RUN_SECONDS, elapsed
    assert (tmp_path / "r.md").read_text().startswith("# Agent guardrail checkup — big")


def test_a_vendor_refresh_at_the_path_cap_does_not_decide_how_long_a_checkup_takes(tmp_path: Path) -> None:
    """The one step with a documented cap and no timing behind it.

    `git log --name-only` ran rename detection before it emitted a byte, so
    neither `HISTORY_PATHS` nor killing the process could bound the wall clock:
    26 commits renaming 30,000 files apiece cost 12 seconds, and one repair
    commit renaming 200,000 files cost 4. The cap bounds the paths and
    `--no-renames` bounds the seconds; both are needed, and this is the shape
    the cap was written for -- a repair commit that names a hundred thousand
    files, then another that moves all of them.
    """

    blob = ["blob\nmark :1\ndata 6\nx = 1\n"]
    for number, parent in ((10, None), (11, 10)):
        blob.append(_commit(number, f"fix: vendor refresh {number}", parent))
        # Spread over directories: one tree of 100,000 entries is quadratic in
        # `fast-import`, and the walk's cost is the same either way.
        blob.extend(f"M 100644 :1 v{number}/db/d{n // 100:04d}/f{n % 100:02d}.py\n" for n in range(100_000))
    repository = _history(tmp_path / "vendor", blob)

    started = time.monotonic()
    repairs, churn, truncated = history(repository)
    elapsed = time.monotonic() - started

    assert elapsed < STEP_SECONDS, elapsed
    assert truncated, "200,000 path entries against a 100,000 cap"
    assert [item.categories for item in repairs] == [frozenset({"db"})]
    assert churn


def test_fifty_thousand_commits_do_not_decide_how_long_a_checkup_takes(tmp_path: Path) -> None:
    """The commit cap: `-n2000` is on the log, so git stops rather than this reader."""

    blob = []
    for number in range(50_000):
        body = str(number)
        blob.append(f"blob\nmark :{number + 1}\ndata {len(body)}\n{body}\n")
        blob.append(_commit(1_000_000 + number, f"fix: repair {number}", None))
        blob.append(f"from :{1_000_000 + number - 1}\n" if number else "")
        blob.append(f"M 100644 :{number + 1} db/f{number % 50:03d}.py\n")
    repository = _history(tmp_path / "many", blob)

    started = time.monotonic()
    repairs, _, truncated = history(repository)
    elapsed = time.monotonic() - started

    assert elapsed < STEP_SECONDS, elapsed
    assert len(repairs) == HISTORY_COMMITS
    assert not truncated, f"{HISTORY_COMMITS} commits of one path apiece is under {HISTORY_PATHS:,}"
