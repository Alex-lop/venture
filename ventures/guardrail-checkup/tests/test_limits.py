"""Every scan step is bounded, and the bounds are timed rather than asserted in prose.

A repository is untrusted input, and so is its size: a checked-in CODEOWNERS, a
`.mcp.json` and a monorepo's file list are all things a stranger controls. Each
test here builds the worst case a bound allows and asserts the run is still
quick, so a quadratic step reintroduced later fails on the clock rather than on
somebody's afternoon.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from conftest import git

from guardrail_checkup import AGENT_FILE_LIMIT, OWNER_LIMIT, SERVER_ROWS, scan
from guardrail_checkup._cli import main

#: The wall-clock budget for one bounded step, and for a whole run over a
#: synthetic repository of 5,000 files. Generous by an order of magnitude
#: against the measurements: the point is to fail on a quadratic step, not on a
#: slow machine.
STEP_SECONDS = 2.0
RUN_SECONDS = 30.0

#: 149,796 x 7 bytes = 1,048,572, one line under MAX_READ_BYTES: the largest
#: CODEOWNERS this tool will read, which is where the worst case lives.
BIGGEST_CODEOWNERS = 149_796


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
