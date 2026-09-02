"""The docs are executed or pinned, not trusted. These tests fail when they overclaim.

Four mechanisms, over `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md` and the
`pyproject.toml` description:

* `<!-- runnable -->` blocks are run and their output compared;
* `<!-- pinned: <path> -->` blocks must appear verbatim in that checked-in file;
* every number is read **in the sentence it appears in**, against the value in
  the code that decides it, so one whitelisted figure cannot be swapped for
  another; anything left over must be declared prose with a reason;
* every `every`/`all` claim, and every listed absolute claim, is on a closed
  list with the test that would fail first.

`test_the_doc_truth_suite_fails_on_each_injected_falsehood` replays the
falsehoods an audit shipped past the earlier version of this file, and fails if
any of them would still ship. `tests/test_comparison_truth.py` carries the same
treatment for `docs/comparison.md`.
"""

from __future__ import annotations

import ast
import difflib
import os
import re
import subprocess
import textwrap
import tomllib
from pathlib import Path

import pytest
from conftest import GIT_ENV, list_items, unquoted
from test_comparison_truth import INJECTIONS as COMPARISON_INJECTIONS
from test_comparison_truth import check_determinism

import guardrail_checkup
from guardrail_checkup import (
    AGENT_FILE_LIMIT,
    CANDIDATE_LIMIT,
    CATEGORIES,
    CODEOWNERS_BONUS,
    EXCLUSION_GLOBS,
    FIXTURE_SAMPLE,
    HEURISTIC_BASE,
    HISTORY_COMMITS,
    MAX_READ_BYTES,
    MONDAY_LIMIT,
    NAME,
    OWNER_LIMIT,
    REGRESSION_WEIGHT,
    SECTIONS,
    SERVER_ROWS,
    SIGNATURE_SCAN_BYTES,
    SIGNATURE_SCAN_FILES,
    SKIP_DIRECTORIES,
    SNIFF_BYTES,
    __version__,
    hook_script,
)
from guardrail_checkup._cli import DEFAULT_MAX_FILES, build_parser
from guardrail_checkup._scan import REPAIR_SUBJECT, SCREENS, WORKFLOW_LIMIT

RUNNABLE = re.compile(r"<!-- runnable -->\n```console\n(.*?)```", re.DOTALL)
PINNED = re.compile(r"<!-- pinned: ([^ ]+) -->\n```[a-z]*\n(.*?)```", re.DOTALL)
#: A run of digits that is not part of a word: 3.11 and 0.1.0 are one number each.
NUMBER = re.compile(r"(?<![\w.])\d+(?:\.\d+)*")
#: The documents spell small counts out; every one of them is pinned to the code.
WORDS = {"one": 1, "two": 2, "three": 3, "five": 5, "six": 6, "seven": 7, "nine": 9, "ten": 10}
#: How a repeated weight is written in prose.
TIMES = {2: "double", 3: "triple"}


def word(value: int) -> str:
    """The number-word the documents use for a value the code decides."""

    return next(name for name, number in WORDS.items() if number == value)


def never(returns: list[int]) -> int:
    """The exit status the CLI never returns. Both documents say which."""

    return next(item for item in (0, 1, 2) if item not in returns)


def exit_statuses(repo_root: Path) -> set[int]:
    """Every integer the CLI returns. `return None` is control flow, not a status."""

    tree = ast.parse((repo_root / "src" / "guardrail_checkup" / "_cli.py").read_text(encoding="utf-8"))
    return {
        node.value.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, int)
    }


def flat(text: str) -> str:
    """One line, so a claim that wraps is still one string to match against."""

    return " ".join(text.split())


@pytest.fixture(scope="session")
def documents(repo_root: Path) -> dict[str, str]:
    meta = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    return {
        "README.md": (repo_root / "README.md").read_text(encoding="utf-8"),
        "CHANGELOG.md": (repo_root / "CHANGELOG.md").read_text(encoding="utf-8"),
        "CONTRIBUTING.md": (repo_root / "CONTRIBUTING.md").read_text(encoding="utf-8"),
        "pyproject description": meta["description"],
        # PyPI renders the keywords and nothing else in the suite reads one, so
        # "score" and "grading" could be added to them unchallenged.
        "pyproject keywords": " ".join(meta["keywords"]),
        # PyPI renders a classifier as a fact about the package: an audit added
        # `License :: OSI Approved :: MIT License` beside `license = "Apache-2.0"`
        # and the whole suite passed.
        "pyproject classifiers": "\n".join(meta["classifiers"]),
        # A comment is a declarative claim. "The two sibling packages and
        # nothing else" became "plus PyYAML" unchallenged.
        "pyproject comments": "\n".join(
            line
            for line in (repo_root / "pyproject.toml").read_text(encoding="utf-8").splitlines()
            if line.lstrip().startswith("#")
        ),
        # PyPI renders these in the sidebar. An audit repointed one at a
        # different repository and the whole suite passed.
        "pyproject urls": "\n".join(f"{key} = {value}" for key, value in meta["urls"].items()),
    }


@pytest.fixture(scope="session")
def readme(documents: dict[str, str]) -> str:
    return documents["README.md"]


def blocks(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for block in RUNNABLE.findall(text):
        command: str | None = None
        expected: list[str] = []
        for line in block.splitlines():
            if line.startswith("$ "):
                if command is not None:
                    pairs.append((command, "\n".join(expected)))
                command, expected = line[2:], []
            elif command is not None:
                expected.append(line)
        if command is not None:
            pairs.append((command, "\n".join(expected)))
    return pairs


# --- the blocks ---------------------------------------------------------------


def test_the_collect_count_the_readme_states_is_the_count_pytest_reports(
    readme: str, repo_root: Path, shell_env: dict[str, str]
) -> None:
    """The one runnable block: the README's own test count, from pytest itself."""

    commands = blocks(readme)
    assert len(commands) == 1, commands
    command, expected = commands[0]
    done = subprocess.run(
        command, shell=True, cwd=repo_root, env=shell_env, capture_output=True, text=True, timeout=300
    )
    count = int(done.stdout.strip())
    assert int(expected.strip()) == count, (expected, count)


def test_every_pinned_block_appears_in_the_file_it_names(readme: str, repo_root: Path) -> None:
    found = PINNED.findall(readme)
    assert len(found) == 5, found
    for relative, body in found:
        source = (repo_root / relative).read_text(encoding="utf-8")
        for line in body.strip().splitlines():
            assert line in source, (relative, line)


def test_the_settings_snippet_in_the_readme_is_the_one_the_code_emits(readme: str) -> None:
    import json

    snippet = json.dumps(guardrail_checkup.settings_snippet("db"), indent=2)
    assert snippet in readme


# --- every number, in the sentence it is in ------------------------------------


def bindings(repo_root: Path) -> list[tuple[str, str, str]]:
    """(document, pattern, what decides it) — every pattern built from the code.

    A pattern is the claim *and* its number, so replacing one whitelisted figure
    with another whitelisted figure fails here even though both are declared.
    """

    workflow = (repo_root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    pythons = re.findall(r'"(3\.\d+)"', re.search(r"python: \[(.*?)\]", workflow).group(1))
    systems = [
        {"ubuntu": "Ubuntu", "macos": "macOS", "windows": "Windows"}[item.split("-")[0]]
        for item in re.search(r"os: \[(.*?)\]", workflow).group(1).split(", ")
    ]
    demo = (repo_root / "demo" / "demo.sh").read_text(encoding="utf-8")
    repairs = [item for item in re.findall(r'^commit "([^"]+)"', demo, re.M) if REPAIR_SUBJECT.search(item)]
    scan_source = (repo_root / "src" / "guardrail_checkup" / "_scan.py").read_text(encoding="utf-8")
    evidence_sources = scan_source.count("evidence.append(") + 1  # the path heuristic is always the first
    returns = sorted(exit_statuses(repo_root))
    ok, bad = returns[0], returns[-1]
    # the last exit in the script is the one under the BLOCKED message
    blocks_with = int(re.findall(r"sys\.exit\((\d)\)", hook_script("db", ("db/",)))[-1])
    meta = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    floor = meta["requires-python"].lstrip(">=")
    licence = meta["license"]
    # `run` takes one repository and no more; the documents say "one repository".
    subparser = next(
        action
        for action in build_parser()._subparsers._group_actions  # type: ignore[union-attr]
    ).choices["run"]
    positionals = [item for item in subparser._actions if not item.option_strings]

    return [
        ("README.md", rf"Status: {re.escape(__version__)}\b", "guardrail_checkup.__version__"),
        ("README.md", rf"the same {word(len(SECTIONS))} sections", "len(SECTIONS)"),
        (
            "README.md",
            rf"3\. \*\*{re.escape(SECTIONS[2].split('. ', 1)[1])}\*\*",
            "SECTIONS[2], the heading the report renders",
        ),
        ("README.md", rf"up to {word(CANDIDATE_LIMIT)} ranked places", "CANDIDATE_LIMIT"),
        ("README.md", rf"up to {word(CANDIDATE_LIMIT)} ranked candidates", "CANDIDATE_LIMIT"),
        ("README.md", rf"at most {word(MONDAY_LIMIT)} actions", "MONDAY_LIMIT"),
        (
            "README.md",
            rf"the {word(len(CATEGORIES))} places a junior would be stopped: "
            + re.escape(", ".join(noun for _, noun, _ in CATEGORIES[:-1]) + ", and " + CATEGORIES[-1][1]),
            "the nouns in CATEGORIES, in order",
        ),
        (
            "README.md",
            rf"one of {word(len(SCREENS))} known screens "
            + re.escape("(" + ", ".join(f"`{item}`" for item in SCREENS) + ")"),
            "SCREENS",
        ),
        (
            "README.md",
            rf"more than {OWNER_LIMIT} distinct owned patterns",
            "OWNER_LIMIT",
        ),
        ("README.md", rf"Candidates come from {word(evidence_sources)} places", "the evidence lines candidates() adds"),
        ("README.md", rf"over the last {HISTORY_COMMITS} non-merge commits", "HISTORY_COMMITS"),
        ("README.md", rf"a history with {word(len(repairs))} repairs", "the repair commits demo/demo.sh makes"),
        (
            "README.md",
            rf"\+ {CODEOWNERS_BONUS} if `CODEOWNERS` names one of them, \+ {HEURISTIC_BASE} if the path heuristic",
            "CODEOWNERS_BONUS and HEURISTIC_BASE",
        ),
        ("README.md", rf"up to {FIXTURE_SAMPLE} checked-in JSON fixtures", "FIXTURE_SAMPLE"),
        ("README.md", rf"fans out over the files in it, up to {AGENT_FILE_LIMIT} of them", "AGENT_FILE_LIMIT"),
        (
            "README.md",
            rf"exclusions are drawn from the first {EXCLUSION_GLOBS} §3-candidate path globs",
            "EXCLUSION_GLOBS",
        ),
        ("README.md", rf"The first {SERVER_ROWS} servers get a row each", "SERVER_ROWS"),
        ("README.md", rf"A candidate at score {HEURISTIC_BASE} is a bare path match", "HEURISTIC_BASE"),
        (
            "README.md",
            rf"replays {len(INJECTIONS) + len(COMPARISON_INJECTIONS)} injected falsehoods",
            "the two INJECTIONS lists the suite replays",
        ),
        ("README.md", rf"weighted {TIMES[REGRESSION_WEIGHT]} when the same commit", "REGRESSION_WEIGHT"),
        (
            "README.md",
            rf"when fewer than {word(CANDIDATE_LIMIT)} categories match anything",
            "CANDIDATE_LIMIT",
        ),
        ("README.md", rf"## License {re.escape(licence)}\. Built on", "the license in pyproject.toml"),
        ("README.md", rf"which exits {blocks_with} to block the call", "the sys.exit in hook_script"),
        (
            "README.md",
            rf"Exit status is `{ok}` whenever the report was written, and `{bad}` on a usage or IO error",
            "the constants _cli.main returns",
        ),
        ("README.md", rf"It is never `{never(returns)}`", "the same returns"),
        ("README.md", rf"skips {len(SKIP_DIRECTORIES)} well-known directories", "len(SKIP_DIRECTORIES)"),
        ("README.md", rf"`--max-files` \(default {DEFAULT_MAX_FILES}\)", "DEFAULT_MAX_FILES"),
        ("README.md", rf"up to {MAX_READ_BYTES // 2**20} MiB each", "MAX_READ_BYTES"),
        ("README.md", rf"NUL byte in its first {SNIFF_BYTES // 2**10} KiB", "SNIFF_BYTES"),
        (
            "README.md",
            rf"run on CPython {', '.join(pythons[:-1])} and {pythons[-1]}, on {' and '.join(systems)},",
            "the CI matrix in .github/workflows/ci.yml",
        ),
        ("CHANGELOG.md", rf"refused with exit {bad} if either resolves inside", "the constants _cli.main returns"),
        (
            "CHANGELOG.md",
            rf"Exit status is {ok} whenever the report was written, and {bad} on a usage or IO error\. "
            rf"It is never {never(returns)}",
            "the same returns",
        ),
        ("CHANGELOG.md", rf"weighs a repair commit {TIMES[REGRESSION_WEIGHT]}", "REGRESSION_WEIGHT"),
        (
            "CHANGELOG.md",
            rf"six-section report over {word(len(positionals))} repository",
            "the run subcommand's positional arguments",
        ),
        ("CHANGELOG.md", rf"Section {SECTIONS.index('3. Invariant candidates') + 1} is a judgement", "SECTIONS"),
        ("CHANGELOG.md", rf"Up to {word(CANDIDATE_LIMIT)} ranked invariant candidates", "CANDIDATE_LIMIT"),
        ("CONTRIBUTING.md", rf"`\.python-version` pins {re.escape(floor)},", "requires-python in pyproject.toml"),
        (
            "CONTRIBUTING.md",
            rf"passes on {', '.join(pythons[:-1])} and {pythons[-1]}\.",
            "the CI matrix in .github/workflows/ci.yml",
        ),
        (
            "CONTRIBUTING.md",
            rf"replay {len(INJECTIONS) + len(COMPARISON_INJECTIONS)} injected falsehoods",
            "the two INJECTIONS lists the suite replays",
        ),
        (
            "README.md",
            rf"The first {WORKFLOW_LIMIT} in sorted order are read, and fewer when this step's line budget "
            r"is spent first",
            "WORKFLOW_LIMIT",
        ),
        (
            "README.md",
            rf"the signature scan reaches before its {SIGNATURE_SCAN_BYTES // 2**20} MiB and "
            rf"{SIGNATURE_SCAN_FILES} file budgets are spent",
            "SIGNATURE_SCAN_BYTES and SIGNATURE_SCAN_FILES",
        ),
        ("pyproject description", rf"up to {word(CANDIDATE_LIMIT)} invariant candidates", "CANDIDATE_LIMIT"),
    ]


@pytest.fixture(scope="session")
def bound(repo_root: Path) -> list[tuple[str, str, str]]:
    return bindings(repo_root)


def code_numbers(repo_root: Path) -> dict[str, object]:
    floor = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["requires-python"]
    return {
        "0": 0,  # the exit status of a run that wrote a report
        "2": 2,  # the exit status of a usage or IO error, and the hook's block code
        "3": CANDIDATE_LIMIT,  # invariant candidates named in a report, and the third report section
        "4": len(SECTIONS) - 2,  # the Monday list's section number
        "5": FIXTURE_SAMPLE,
        "6": len(SECTIONS),
        "8": SNIFF_BYTES // 2**10,  # KiB of a file sniffed for a NUL byte
        "1": MAX_READ_BYTES // 2**20,  # MiB read from any one file, and the exit status never returned
        "13": len(SKIP_DIRECTORIES),
        "2000": HISTORY_COMMITS,  # and OWNER_LIMIT, which is the same figure
        "32": WORKFLOW_LIMIT,
        "64": AGENT_FILE_LIMIT,  # and SERVER_ROWS, CHURN_GLOBS and SIGNATURE_SCAN_BYTES in MiB, one figure
        "10000": SIGNATURE_SCAN_FILES,
        "101": len(INJECTIONS) + len(COMPARISON_INJECTIONS),  # the falsehoods the suite replays
        "20000": DEFAULT_MAX_FILES,
        "0.1.0": __version__,
        "3.11": floor.lstrip(">="),  # the interpreter floor the package declares
    }


#: The repository this package is published from. Every `[project.urls]` entry
#: has to start with it: an audit repointed one at a different repository of the
#: author's and the whole suite passed.
PROJECT_SOURCE = "https://github.com/Alex-lop/guardrail-checkup"

#: Numbers in the documents that no value in the code decides. Each entry is the
#: digit run, the pattern that has to match the sentence it appears in, and the
#: reason it is prose. The set is closed *and* anchored: membership alone let an
#: audit swap the README's `## 60 seconds` heading for `## 16 seconds` -- one
#: declared prose figure for another declared prose figure in the same document
#: -- and the whole suite passed.
PROSE_NUMBERS: dict[str, dict[str, tuple[str, str]]] = {
    "README.md": {
        "7": (r"7 draft\(s\) in gcnem/drafts", "the Nemisis run's draft count, pinned to its transcript"),
        "16": (r"— 16 inventory finding\(s\)", "the Nemisis run's finding count, pinned to its transcript"),
        "17": (r"— 17 inventory finding\(s\)", "the demo run's finding count, pinned to demo/OUTPUT.txt"),
        "23": (r"ci\.yml:23", "a line number inside the pinned Nemisis block"),
        "2026-08-31": (r"docs/en/hooks> on 2026-08-31", "the date the hooks documentation was captured"),
        "2.0": (r"Apache-2\.0\. Built on", "Apache-2.0, the license this package is released under"),
        "2026": (r"2026-08-31", "part of that date"),
        "08": (r"2026-08-31", "part of that date"),
        "31": (r"2026-08-31", "part of that date"),
        "60": (r"## 60 seconds", "the demo budget, timed by test_the_sixty_second_demo_runs_in_under_sixty_seconds"),
        "485": (r"grep -c :: 485", "the collected-test count, run and compared by the first test in this file"),
        "3.12": (r"CPython 3\.11, 3\.12 and 3\.13", "an interpreter the CI matrix runs"),
        "3.13": (r"CPython 3\.11, 3\.12 and 3\.13", "an interpreter the CI matrix runs"),
    },
    "CHANGELOG.md": {
        "0.1": (r"agent-plan-lint>=0\.1,<1", "the lower bound of the sibling packages' declared version ranges"),
        "0.1.0": (r"## \[0\.1\.0\] - 2026-08-31", "this release"),
        "1": (r"It is never 1", "the exit status this tool never returns, and the siblings' gate status"),
        "2026": (r"\[0\.1\.0\] - 2026-08-31", "the release date"),
        "08": (r"\[0\.1\.0\] - 2026-08-31", "part of that date"),
        "31": (r"\[0\.1\.0\] - 2026-08-31", "part of that date"),
        "120": (
            r"--out R\.md \| head` exited \*\*120\*\*",
            "the status CPython's own shutdown flush produced on a broken pipe, before the fix below it",
        ),
    },
    "CONTRIBUTING.md": {
        "0": (r"exits 0 \(no cited source has moved\)", "the exit status of a check that passed"),
        "1": (r"1\. `\./scripts/check\.sh` must pass", "a numbered step, and the upper bound of the version ranges"),
        "2": (r"2\. New behaviour needs a test", "a numbered step, and the shell's stderr redirection"),
        "3": (r"3\. No new runtime dependencies", "a numbered step, and the section that carries the judgement"),
        "4": (r"4\. Quoting a source", "a numbered step"),
        "5": (r"5\. Regenerate the demo", "a numbered step"),
        "0.1": (r"`agent-plan-lint>=0\.1,<1`", "the lower bound of the sibling packages' declared version ranges"),
        "200": (r"returns 200", "the HTTP status every project URL must return before a release"),
        "3.11": (r"`\.python-version` pins 3\.11", "the interpreter floor, asserted in test_packaging.py"),
        "3.12": (r"passes on 3\.11, 3\.12 and 3\.13", "an interpreter the CI matrix runs"),
        "3.13": (r"passes on 3\.11, 3\.12 and 3\.13", "an interpreter the CI matrix runs"),
        "60": (r"\*60 seconds\*", "the README heading this file names as prose it does not read"),
    },
    "pyproject description": {},
    "pyproject keywords": {},
    "pyproject urls": {},
    "pyproject classifiers": {
        "4": (r"Development Status :: 4 - Beta", "the Development Status classifier's own number"),
        "3": (r"Programming Language :: Python :: 3", "the Python major version each interpreter classifier names"),
        "3.12": (r"Programming Language :: Python :: 3\.12", "an interpreter the CI matrix runs"),
        "3.13": (r"Programming Language :: Python :: 3\.13", "an interpreter the CI matrix runs"),
    },
    "pyproject comments": {
        "0.1.0": (r"CHANGELOG\.md 0\.1\.0", "the CHANGELOG entry the release checklist points at"),
        "200": (r"must return 200 before a publish", "the HTTP status every project URL must return"),
    },
}

#: Every `every`/`all` claim in the documents, and what makes it true. The set
#: is closed per document: a new absolute claim — the shape an invented
#: capability takes when it carries no digit — fails the test below until it is
#: listed here. `docs/comparison.md` gets the same treatment in
#: tests/test_comparison_truth.py.
DECLARED_ABSOLUTES: dict[str, dict[str, str]] = {}
DECLARED_ABSOLUTES["README.md"] = {
    "every draft goes to a directory you name": "test_writing_inside_the_repository_under_inspection_is_refused",
    "every row that cites a file carries its `file:line`, and one line explaining": (
        "test_every_finding_carries_a_place_and_a_consequence"
    ),
    "an omitted matcher and `*` match every tool": (
        "test_the_catch_all_matcher_means_what_the_fetched_page_says_it_means"
    ),
    "The first 64 servers get a row each": "test_the_mcp_server_rows_are_capped_and_the_row_says_how_many_there_were",
    "Every row is a fact plus one sentence explaining why it matters or what remains unknown.": (
        "test_every_finding_carries_a_place_and_a_consequence"
    ),
    "Every row that cites a file carries its `file:line`; a row that states an absence carries `-`": (
        "test_every_finding_carries_a_place_and_a_consequence"
    ),
    "if the path heuristic matched at all": "test_the_score_is_the_arithmetic_the_report_states_not_the_files_touched",
    "loads every policy this tool emits": "test_every_starter_policy_loads_even_over_a_repository_of_hostile_paths",
    "in front of every server that runs a command line": (
        "test_a_remote_server_is_carried_through_untouched_and_counted_as_unwrapped"
    ),
    "It does not read every file": "test_a_binary_file_is_listed_and_not_read",
    "every checked-in `.json` the signature scan reaches": "test_a_json_file_that_is_neither_shape_is_left_alone",
    "§5 of every report says it": "test_the_report_has_the_six_sections_in_the_runbooks_order",
    "overridden on every git command line": "test_every_git_call_carries_the_overrides_that_make_it_read_only",
    "every emitted starter policy loaded by": "test_every_starter_policy_this_tool_emits_loads",
    "it fails on any `every`/`all` sentence in any of those documents that is not on that list": "this test",
    "all of them whole, not by their opening": "test_every_closed_list_is_the_text_the_suite_declares",
    "it binds every quotation to a file": "test_every_quotation_in_the_readme_is_in_a_checked_in_source",
    "dated evidence for every figure": "test_every_figure_on_the_page_is_the_value_in_the_fetched_metadata",
    "or every top-level directory, when the history holds": (
        "test_the_starter_policy_falls_back_to_every_top_level_directory_with_no_repair_history"
    ),
    "`core.hooksPath` is overridden too, on every call but the two": (
        "test_the_two_hooks_path_queries_are_the_only_calls_that_relax_an_override"
    ),
    "it holds the length of each capability list": "test_every_capability_list_is_the_length_the_suite_declares",
}
DECLARED_ABSOLUTES["CHANGELOG.md"] = {
    "capped like every other axis": "test_a_repository_of_workflows_does_not_decide_how_long_a_checkup_takes",
    "Every row that cites a file carries its `file:line`, a row stating an absence carries `-`": (
        "test_every_finding_carries_a_place_and_a_consequence"
    ),
    "every row carries one line explaining why it matters or what remains unknown": (
        "test_every_finding_carries_a_place_and_a_consequence"
    ),
    "it names, in those words, every candidate whose only evidence": (
        "test_the_report_never_points_at_a_candidate_it_did_not_render"
    ),
    "over the AST of every shipped module": "test_no_shipped_module_imports_anything_that_can_reach_the_network",
    "or the word *grade* at all": "test_no_rendered_report_carries_a_readiness_score_a_grade_or_a_percentage",
    "overridden on every git command line": "test_every_git_call_carries_the_overrides_that_make_it_read_only",
    "Every string the repository controls": "test_a_repository_cannot_write_its_own_section_into_the_report",
    "Every branch that reads a named artifact ends at one row": (
        "test_a_file_that_is_present_and_not_read_never_produces_a_negative_fact"
    ),
    "every repository-derived token in a shell line the report offers the reader": (
        "test_every_repository_derived_token_in_the_reports_shell_lines_is_quoted"
    ),
    "Every repository-derived token is now one `shlex.quote`d argument": (
        "test_the_one_line_test_runs_no_command_a_filename_smuggled_into_it"
    ),
    "or none at all, matches every tool": "test_the_catch_all_matcher_means_what_the_fetched_page_says_it_means",
    "every `every`/`all` claim in the README is on a closed list": (
        "test_every_absolute_claim_in_the_documents_is_on_the_declared_list"
    ),
    "commented out every row after it": "test_a_link_shaped_path_is_reported_and_never_rendered_as_markdown",
    "pointing at each other produced no report at all": ("test_a_symlink_cycle_does_not_stop_the_report_being_written"),
    "emits no row at all when the path is not a git repository": (
        "test_a_path_that_is_not_a_git_repository_gets_no_hooks_row_at_all"
    ),
    "Every target — `--out`, `--emit-dir` and each emitted draft — is compared by `os.path.realpath` now": (
        "test_a_symlink_into_the_repository_is_refused_like_a_path_inside_it"
    ),
    "so every repository carrying a policy and a plan that fails validation ended in": (
        "test_a_plan_with_issues_is_validated_and_every_line_names_its_code"
    ),
    "exit 2 with no report at all": "test_the_cli_writes_a_report_for_a_repository_whose_plan_has_issues",
    "while `WriteLog` was reported as inspecting every path": (
        "test_a_matcher_that_catches_a_write_tool_is_reported_as_inspecting_a_write"
    ),
    "All of them: the sort read `len(paths)`": "test_equal_scores_are_ordered_by_the_number_of_matching_files",
    "built from every ranked candidate while §3 renders the first three": (
        "test_the_starter_policy_excludes_exactly_the_candidates_section_three_names"
    ),
    "**Every file this tool opens is named in §1.**": (
        "test_every_file_this_tool_opens_is_named_in_the_scope_it_prints"
    ),
    "Every `_read` in the package goes through one recorder now": (
        "test_every_file_this_tool_opens_is_named_in_the_scope_it_prints"
    ),
    "fanned out over every file under it at up to `MAX_READ_BYTES` apiece": (
        "test_the_files_under_one_agent_file_prefix_are_capped_and_the_row_says_so"
    ),
    "said no automated check runs at all": "test_the_absent_rows_say_nothing_about_the_host",
    "while every other item names a path": "test_the_last_monday_item_names_the_instruction_file",
    "every declared prose number carries the sentence it must appear in": (
        "test_every_number_in_the_documents_is_bound_to_the_code_or_declared_prose"
    ),
}
DECLARED_ABSOLUTES["pyproject comments"] = {
    "so renaming the package means changing all three": (
        "test_the_name_the_console_script_and_the_module_constant_agree"
    ),
}


DECLARED_ABSOLUTES["CONTRIBUTING.md"] = {
    "over the AST of every module in the installed package": (
        "test_no_shipped_module_imports_anything_that_can_reach_the_network"
    ),
    "the behavioural sentences and the `every`/`all` claims": (
        "test_every_absolute_claim_in_the_documents_is_on_the_declared_list"
    ),
    "the stamp inside every evidence file": "test_the_pages_fetched_date_is_the_stamp_in_every_evidence_file",
    "a flag or an `every`/`all`": "test_every_absolute_claim_in_the_documents_is_on_the_declared_list",
    "no flag and no `every`/`all`, will ship": ("test_every_absolute_claim_in_the_documents_is_on_the_declared_list"),
    "Pass `--python` to **every** `uv run`": "test_the_python_classifiers_are_the_versions_ci_runs",
    "Every URL in `[project.urls]` returns 200": "test_every_project_url_names_this_packages_own_repository",
}


#: How many bullets, numbered items and table rows each capability list carries.
#: An invented capability is a new bullet or a new table row; a deleted promise
#: is a missing one. The counts are closed, so either fails here.
LIST_LENGTHS = {
    ("README.md", "The six sections"): 6,
    ("README.md", "What it looks at"): 10,
    ("README.md", "The invariant candidates"): 3,
    ("README.md", "What it composes"): 2,
    ("README.md", "What it does not do"): 13,
    ("CHANGELOG.md", "Added"): 5,
    ("CHANGELOG.md", "Decided during the build"): 14,
    ("CHANGELOG.md", "Fixed before release, from the second review pass"): 11,
    ("CHANGELOG.md", "Fixed before release, from the third review pass"): 13,
    ("CHANGELOG.md", "Fixed before release, from the fourth review pass"): 14,
    ("CHANGELOG.md", "Fixed before release, from the fifth review pass"): 15,
    ("CHANGELOG.md", "Fixed before release, from the sixth review pass"): 9,
    ("CHANGELOG.md", "Fixed before release, from the seventh review pass"): 9,
    ("CHANGELOG.md", "Fixed before release, from the eighth review pass"): 7,
    ("CHANGELOG.md", "Pre-release scaffolding"): 1,
    ("CONTRIBUTING.md", "The three rules this package will not bend"): 3,
    ("CONTRIBUTING.md", "What the doc-truth suite does not catch"): 9,
}

CLOSED_ITEMS: dict[tuple[str, str], list[str]] = {
    ("README.md", "The six sections"): [
        "1. **Scope** — the path, HEAD, size, language mix by file extension, and exactly what was and was not read.",
        (
            "2. **Tool results — and what they got wrong** — the guardrail inventory (every row that cites a "
            "file carries its `file:line`, and one line explaining why it matters or what remains unknown), what "
            "`agent-plan-lint` and "
            "`egresswall` found, and the falsifier list for the generic scorers."
        ),
        (
            "3. **Invariant candidates** — up to three ranked candidates, each with the paths it governs, the "
            "evidence, a `PreToolUse` hook that blocks writes there, and a one-line test."
        ),
        "4. **Monday list** — at most five actions, each naming a file this tool emitted or a file to edit.",
        (
            "5. **What this did not cover** — branch protection, production, secrets in history, runtime, hooks "
            "configured outside this checkout, anything needing a model, and the three tools this one does not "
            "replace, named with one line each from a checked-in source."
        ),
        (
            "6. **Provenance** — versions, the exact command, what left the machine (nothing), and the AI-assistance "
            "disclosure."
        ),
    ],
    ("README.md", "The invariant candidates"): [
        (
            "- **path heuristics** — the seven places a junior would be stopped: the schema and query layer, "
            "authentication and session handling, money, deployment and infrastructure, secret material, generated "
            "and vendored files, and the dependency lockfiles;"
        ),
        (
            "- **git history** — the paths that repair commits (`fix`, `revert`, `hotfix`, `regression`, `bugfix`) "
            "touched, over the last 2000 non-merge commits, weighted double when the same commit also touched a test "
            "named for a regression;"
        ),
        (
            "- **`CODEOWNERS`** — the paths that already require a named human. They are ranked on evidence, not "
            "elegance: score = repair commits that touched these paths, + 2 if `CODEOWNERS` names one of them, + 1 if "
            "the path heuristic matched at all. One repair commit is worth one point however many files it touched. A "
            "candidate at score 1 is a bare path match — the heuristic matched and nothing else did — and the report "
            "says so, in those words, rather than presenting it as evidence; among equal scores the order is the "
            "number of matching files, then the name. The report labels them *candidates — a human confirms or "
            "replaces them*, and when fewer than three categories match anything it says so and does not invent a "
            "third. Each one comes with the hook that would enforce it, in Claude Code's documented `settings.json` "
            "shape (verified against <https://code.claude.com/docs/en/hooks> on 2026-08-31; the fetched page is "
            "`docs/evidence/claude-code-hooks.txt`):"
        ),
    ],
    ("README.md", "What it composes"): [
        (
            "- **`agent-plan-lint`** — if any checked-in `.json` file carries both `policy_id` and "
            "`allowed_write_globs`, or both `mission_id` and `tasks`, it is loaded and validated and the issues go in "
            "§2. If no checked-in JSON file carries either pair of signature keys, a **starter policy** is drafted "
            "instead: a valid `agent-plan-lint` policy whose write "
            "globs are the most-churned directories repair commits touched, capped at 64 with §2 naming the count "
            "and the cut — or every top-level directory, when the history holds no repair commit to read — and "
            f"whose exclusions are drawn from the first {EXCLUSION_GLOBS} §3-candidate path globs in sorted order, "
            "with §2 naming any cut or path the sibling refuses. A test loads every "
            'policy this tool emits with `agent_plan_lint.load_policy`, so "valid" is checked, not claimed.'
        ),
        (
            "- **`egresswall`** — up to 5 checked-in JSON fixtures are screened with egresswall's default policy, and "
            "the report names the reason code and the path, never the value. If an MCP configuration exists, the same "
            "configuration is rewritten with `egresswall proxy` in front of each server it can wrap and written to "
            "`--emit-dir` as a **suggestion**. The servers it does not rewrite are counted and named in §2, with "
            "the reason for each: one that names a URL is reached over the network and a proxy in front of a "
            "command cannot screen it; one whose command line is not made of strings would need one invented; one "
            "that configures neither a command nor a URL has no command to wrap; and one already running a known "
            "screen would come back double-proxied. Nothing is applied."
        ),
    ],
    ("CHANGELOG.md", "Added"): [
        (
            "- `guardrail-checkup run PATH --out REPORT.md` writes a six-section report over one repository: Scope, "
            "Tool results and what they got wrong, Invariant candidates, Monday list, What this did not cover, "
            "Provenance. The sections and their order are the ones the in-person session works through. No section "
            "states a conclusion: §3 is headed *candidates* because the tool never claims to have found the "
            "invariants."
        ),
        (
            "- A guardrail inventory over `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules`, "
            "`.github/copilot-instructions.md`, `GEMINI.md`, `.claude/settings.json` and "
            "`.claude/settings.local.json` hooks, `.mcp.json` / `claude_desktop_config.json` / `.claude/mcp.json` "
            "servers, `.pre-commit-config.yaml`, installed `.git/hooks`, `CODEOWNERS`, `.github/workflows/`, "
            "secret-scanning configuration, lockfiles and test layout. Every row that cites a file carries its "
            "`file:line`, a row stating an absence carries `-` because the listing is what establishes it, and "
            "every row carries one line explaining why it matters or what remains unknown."
        ),
        (
            "- Up to three ranked invariant candidates from path heuristics, from repair commits in `git log`, and "
            "from `CODEOWNERS`, each with a `PreToolUse` hook that blocks writes to the path and a one-line test. The "
            "report labels them candidates; when fewer than three categories match anything it says so rather than "
            "inventing a third; and it names, in those words, every candidate whose only evidence is a bare path "
            "match."
        ),
        (
            "- Composition with the sibling packages: `agent-plan-lint` validates any checked-in policy or plan "
            "document and drafts a starter policy when no JSON file carries the policy signature keys; `egresswall` "
            "screens a sample of checked-in "
            "JSON fixtures and the MCP configuration is rewritten with `egresswall proxy` in front of each server "
            "that runs a command line, as a suggestion. A server that names a URL instead is reached over the "
            "network, cannot be wrapped by a proxy in front of a command, and is reported as unchanged with both "
            "counts stated."
        ),
        (
            "- `--emit-dir` for the drafted policy, hooks and MCP suggestion; `--format json` for the same facts as a "
            "document — the scope, the inventory, the siblings' results, the falsifiers, the candidates and the "
            "Monday list, without §3's per-candidate snippet, script and test line; `--max-files` for the listing "
            "cap, which bounds the ranking, language mix and symlink inspection but not the inventory's name-based "
            "lookups or the agent-plan-lint signature scan, and which §3 names in the report when it bit."
        ),
    ],
    ("CHANGELOG.md", "Pre-release scaffolding"): [
        (
            "- `[tool.uv.sources]` in `pyproject.toml` resolves `agent-plan-lint` and `egresswall` from the sibling "
            "working copies, because neither is on PyPI yet. **The release deletes that table and re-locks**, so the "
            "declared PyPI ranges `agent-plan-lint>=0.1,<1` and `egresswall>=0.1,<1` are what a user resolves. "
            "`tests/test_packaging.py` fails if the table is present and this note is not."
        ),
    ],
    ("CHANGELOG.md", "Fixed before release, from the sixth review pass"): [
        (
            "- **The workflow list is capped like every other axis.** How many workflows a repository checks in "
            "was the one axis with no bound: each is read at up to `MAX_READ_BYTES` and walked line by line three "
            "times, and `_uncommented` was walked twice more because the workflow step and the secret-scanning "
            "step each computed it. A thousand workflows of a megabyte apiece was forty-four seconds of scan — "
            "well over the whole-run budget — and a thousand and fifteen rows. `WORKFLOW_LIMIT` is 32, the "
            "remainder gets the row the rule directory already gets, and the secret scan counts the unread ones "
            "rather than calling them absent."
        ),
        (
            "- **The agent-plan-lint signature scan has a byte budget.** Removing `--max-files` as its bound "
            "stopped it reporting a policy absent, and put nothing in its place: twenty thousand checked-in JSON "
            "files of a megabyte apiece cost eighteen seconds whatever `--max-files` said. The sweep still reads "
            "the whole listing, so no absence is claimed off a truncated one, but it stops after "
            "`SIGNATURE_SCAN_BYTES` and §2 then says how many files were listed and not read."
        ),
        (
            "- **The secret-scanning row says where a scanner was named, not that one is configured.** Unlike the "
            "test-runner row beside it, this detector is a word search over the whole uncommented file, so a job "
            "id, a step `name:`, an `if:` guard and an `env:` value reach it too. The fact column read "
            "*configured* while its own consequence column hedged; it reads *named in N place(s)* now."
        ),
        (
            "- **§1's own figures are the capped slice, and the README says which.** The README named §3's "
            "ranking as the one section the `--max-files` slice decides; the file count, the byte total and the "
            "language mix §1 prints are computed from the same slice. The sentence says so, and a test runs the "
            "tool twice, capped and not, to hold it."
        ),
        (
            "- **`CONTRIBUTING.md`'s residual list is the nine classes it still misses.** Two documents stated "
            "different counts — this file said eleven where that one said ten — and neither figure was bound, so "
            "an audit swapped one for *four* with the whole suite green. The list lost the closed preamble class "
            "and the AI-assistance survivor, and one binding now holds the spelled count in both documents "
            "against the number of bullets."
        ),
        (
            "- **The AI-assistance disclosure is a bound sentence in both documents.** The one sentence "
            "discharging it was held by no test: an audit replaced it with its reverse and the whole suite "
            "passed. Both it and the README's line are in `SENTENCES` now, against the §6 line the renderer "
            "emits."
        ),
        (
            "- **§3's no-candidate paragraph ends before the next heading.** It was the one branch in the "
            "renderer that added no trailing blank line, so the report ran *…and no other.* straight into `## 4. "
            "Monday list`."
        ),
        (
            "- **Three README sentences that outran the code.** The workflow table row was keyed `*.yml` while "
            "the scan also reads `*.yaml`; the egresswall bullet presented three unwrapped-server cases where the "
            "code produces four; and the path is printed in the header line under the title, not in the title, "
            "which prints the resolved directory's name. §1 accounts for the files it opened — the JSON document "
            "is what lists them one by one."
        ),
        (
            "- **`scripts/refresh_evidence.py`'s docstring names the test that reads it.** It named "
            "`tests/test_readme_truth.py`; the test that counts its hosts is in `tests/test_comparison_truth.py`. "
            "The script ships in the sdist, so the false sentence was published; that test now asserts the "
            "docstring names it."
        ),
    ],
    ("CHANGELOG.md", "Fixed before release, from the seventh review pass"): [
        (
            "- **The history walk is bounded in seconds, not only in paths.** `git log --name-only` runs rename "
            "detection before it emits its first byte, so neither `HISTORY_PATHS` nor killing git could bound the "
            "wall clock: one commit renaming a hundred thousand files cost eighteen seconds of `git log` against "
            "a two-second budget, and the path cap bit either way. `--no-renames` makes the same walk half a "
            "second, and it is the better answer for a walk that wants the paths a repair touched, because a "
            "detected rename reports only the new path where this one wants both. The caps are `HISTORY_COMMITS` "
            "2000 non-merge commits and `HISTORY_PATHS` a hundred thousand path entries, the second chosen the "
            "way `WORKFLOW_LIMIT` was — a path in a repair commit is matched against the seven categories, so two "
            "hundred thousand was over a second at the cap and a hundred thousand is half of that — and "
            "`tests/test_limits.py` times both: a vendor refresh at the path cap and fifty thousand commits at "
            "the commit cap, each against the two seconds the other steps are held to."
        ),
        (
            "- **§5 of the report names the three tools this one does not replace.** `docs/comparison.md` said "
            "this package is defended by being honest about the other three *in the report it writes*, and no "
            "rendered report named one of them: the honesty was on that page, and the doc-truth suite held the "
            "sentence word for word, so it pinned a false claim in place. §5 now carries one line each for Claude "
            "Code's `/doctor`, `kenryu42/cc-safety-net` and `microsoft/agentrc`, quoting the source checked in "
            "under `docs/evidence/` for each; §6's unaffiliation line names §5 beside §2; and two tests hold it, "
            "one grepping a rendered report for the three phrases and one binding each phrase to the fetched file "
            "it came from."
        ),
        (
            "- **`CONTRIBUTING.md` says which decision bullets are held whole.** Its residual list said the "
            "bolded lead of each decision under *Decided during the build* and the *Fixed before release* "
            "sections is held word for word and the body is not; the sixth pass is held item by item, and an "
            "audit's rewrite of a body there was caught by the mechanism that sentence said would miss it. The "
            "sentence names the second through fifth passes now, and this pass and the sixth are held whole."
        ),
        (
            "- **The falsifier command prints the figure printed beside it.** §2's testing row offered `find . "
            "-path ./.git -prune -o -name 'test_*' -print | wc -l`, which prunes the literal `./.git` and nothing "
            "else and counts files *named* `test_*` rather than files *in a test path*: on the checkout the "
            "pinned transcript records it printed five times the figure in the cell beside it, because it walked "
            "`.venv/` and counted by name. A report sells that column as the command that disproves the claim, so "
            "both halves come from one place now — the listing §1 names and `TEST_PATH` itself, as `git ls-files` "
            "in a checkout and as a `find` pruning `SKIP_DIRECTORIES` outside one — and a test runs it in both "
            "shapes and compares what it prints with the cell."
        ),
        (
            "- **The two example lists in §2's egresswall paragraph say when they were cut.** Four of five "
            "thousand copied-through servers were named and the sentence ended in a full stop: the one truncation "
            "in the report that did not announce itself, where the caps beside it say how many they left out."
        ),
        (
            "- **`CONTRIBUTING.md` says what the path dependencies stop, which is CI itself.** It scoped them to "
            "the wheel-install step; in a checkout without the sibling working copies beside it, `uv lock "
            "--check` and `uv sync` both fail to resolve them before a step runs, so no step of the matrix runs "
            "there today. The release step that deletes `[tool.uv.sources]` removes the condition."
        ),
        (
            "- **`README.md`'s *License* section and `CHANGELOG.md`'s release preamble are held whole.** Both "
            "were prose no closed list read, and an audit shipped a false packaging claim through one and an "
            "invented security sign-off through the other, green through the suite. They are held the way "
            "`README.md`'s preamble already was."
        ),
        (
            "- **A `##` heading no document declares fails the suite.** An entire invented section — a "
            "*Telemetry* heading claiming each run records an anonymous summary of its finding counts — shipped "
            "green: it contradicted the offline promise, and no closed list, no held sentence and no length check "
            "knew about a heading that was not there before. The `##` headings of `README.md`, `CHANGELOG.md`, "
            "`CONTRIBUTING.md` and `docs/comparison.md` are a closed list now."
        ),
        (
            "- **Two source docstrings stated counts the code contradicts.** `wrapped_mcp`'s said three things "
            "stop a rewrite and listed three where the code emits four unwrapped reasons — the fourth is the case "
            "the sixth pass corrected the README for — and `_argv`'s scoped the read-only git configuration to "
            "one exception where the code has two. Both ship in the sdist, and a docstring in `src/` is read by "
            "no test: the eighth class `CONTRIBUTING.md` declares."
        ),
    ],
    ("CHANGELOG.md", "Fixed before release, from the eighth review pass"): [
        (
            "- **The read recorder de-duplicates against a set.** Each `_read` in the package goes through "
            "`_record`, whose idempotence was a membership test over the two ordered lists §1 and `scope.read` "
            "render — so recording the reads cost more than the reads: a hundred seconds of a two-minute run over "
            "a repository of two hundred thousand tiny checked-in JSON files, and the step crossed the two-second "
            "budget at about eighteen thousand of them, inside the default `--max-files`, which by design does "
            "not bound that sweep. The lists are still the ordered ones the report renders; a shadow set answers "
            "the question. `tests/test_limits.py` times a hundred thousand files through the recorder."
        ),
        (
            "- **The signature scan has a file budget as well as a byte budget.** `SIGNATURE_SCAN_BYTES` bounds "
            "what a file costs to read and nothing bounded what one costs to open, and a repository of tiny JSON "
            "never spends sixty-four mebibytes: a hundred thousand files is eight seconds of `open` alone. "
            "`SIGNATURE_SCAN_FILES` is 10000, and the remainder goes into the *listed and not read* clause §2 "
            "already carries, so no absence is claimed over a file nobody opened."
        ),
        (
            "- **The workflow and rule-file caps bound the work, not the file count.** Both capped files where "
            "the cost is per line, and `MAX_READ_BYTES` lets one file carry half a million two-byte ones: "
            "sixty-four rule files of lines matching `_FORBIDS` was nearly three seconds, and 32 workflows of "
            "`run: |` block scalar was nearly three seconds, against the two seconds `tests/test_limits.py` holds "
            "one step to — on a repository inside the documented caps, while the fixtures meant to hold those "
            "caps used line shapes an order of magnitude cheaper. `LINE_BUDGET` is a million lines per step, each "
            "file's text is split once rather than three or four times, and the row that already counted the "
            "files nobody opened now counts these too. Both steps are timed at their caps in the worst line shape "
            "each one allows."
        ),
        (
            "- **The starter policy says how many churned directories it left out.** The churn set was cut at 64 "
            "alphabetically, before the policy was drafted: a repository whose repair commits touched a hundred "
            "directories was handed a policy that denies writes in thirty-six of them, and no row, no clause and "
            "nothing in the emitted file said so — the one cap here that decides what an emitted file *grants* "
            "rather than what a row says. The globs are the most-churned directories now, `CHURN_GLOBS` is 64, "
            "and §2 states both figures. The emitted policy carries no note of its own: `agent-plan-lint`'s "
            "policy model forbids unknown fields and its loader is strict JSON, which has no comments."
        ),
        (
            "- **The inventory's row claim says what the rows do.** Three sentences promised the `file:line` for "
            "rows that carry none: an absence row carries `-`, which is nine of the seventeen rows in the shipped "
            'demo report, and the assertion bound to those sentences opened `where == "-" or ...` — so the '
            "binding exempted the counterexample and pinned a false absolute in place. The sentences are scoped "
            "to a row that cites a file now, and the assertion allows `-` only on a row naming no file the scan "
            "opened."
        ),
        (
            "- **The summary line cannot lose a run that succeeded.** With the report on disk, `guardrail-checkup "
            "run . --out R.md | head` exited **120**: the line is buffered, so it failed in CPython's shutdown "
            "flush, after `main` returned and past the guards in `_cli`. It is flushed inside the guarded path "
            "now, a reader that closed the pipe — or a caller that gives it no stdout — is exit 0 with a silent "
            "stderr, and two tests drive it through both."
        ),
        (
            "- **Three cuts that did not announce themselves now do.** The comment beside `SETTINGS_FILES` said "
            "Claude Code reads four hook sources where its own `/hooks` menu lists five, and a test counts them "
            "against the evidence file; §3's `CODEOWNERS` evidence line named three patterns and no total, the "
            "way the repair-commit line beside it already did; and §1's language mix, the ten most common "
            "extensions, says how many there were."
        ),
    ],
    ("CONTRIBUTING.md", "What the doc-truth suite does not catch"): [
        (
            "- **A spelled-out number in a sentence no binding names.** The number scanner matches digits. *six "
            "known screens*, *one of the three below* and this section's own count are caught because a binding "
            "was written for each; a spelled number somewhere else is prose to this suite."
        ),
        (
            "- **The body of a `CHANGELOG.md` decision bullet.** Under *Decided during the build* and the second "
            "through fifth *Fixed before release* passes, the bolded lead of each decision is held word for word "
            "and the paragraph under it is not, so a sentence rewritten inside one ships unless it carries a "
            "digit, a quotation mark, a flag or an `every`/`all`. The sixth, seventh and eighth passes are held "
            "item by item and whole, and a body rewritten in one of those fails."
        ),
        (
            "- **Prose in a `README.md` section with no closed list.** *60 seconds*, *Observed on a real "
            "repository*, *Command line*, *How it is tested* and *Comparison* are prose. One sentence in each is "
            "held in `SENTENCES`; another added beside it, carrying no digit, no quotation mark, no flag and no "
            "`every`/`all`, will ship."
        ),
        (
            "- **Non-bullet prose under a heading whose closed list holds only its bullets.** `CLOSED_ITEMS` "
            "compares bullets, numbered items and table rows. A paragraph beside them — the line introducing *The "
            "six sections*, for instance — is not an item, and an invented appendix added to it shipped."
        ),
        (
            "- **A sentence of this file that `SENTENCES` does not hold.** One sentence of each section here is "
            "held word for word and the whole file is scanned for digits, for flags and for absolutes; the intro "
            "above the first `##` has no held sentence of its own. A sentence added beside a held one ships, and "
            "so does the rest of a section's prose."
        ),
        (
            "- **Prose on `docs/comparison.md` outside its closed lists.** `PAGE_ITEMS` holds *What this one "
            "deliberately does not do* whole and `PAGE_SENTENCES` holds five sentences elsewhere. Any other "
            "sentence on that page — including its table's own surrounding prose — is read only for quotations, "
            "figures, flags and absolutes."
        ),
        (
            "- **A checked-in evidence transcript outside the lines `README.md` pins.** Pinning is "
            "one-directional: a quoted block has to appear in the file it names, and nothing reads the rest of "
            "the file. `docs/evidence/nemisis-run.txt` is the exception, and only on a machine that has the "
            "checkout it records, where a test re-runs the command and diffs the whole transcript."
        ),
        (
            "- **A declarative comment or module docstring in a source file.** `pyproject.toml`'s comments are "
            "scanned for digits and for absolutes. A comment or docstring in `src/`, `tests/`, `demo/` or "
            "`scripts/` is read by no test, apart from the two host names in `scripts/refresh_evidence.py`'s "
            "docstring, which one test asserts against the URLs the script fetches."
        ),
        (
            "- **A `pyproject.toml` comment beyond the blocks asserted literally.** The dependency comment, the "
            "classifier list and the project URLs are compared word for word in `tests/test_readme_truth.py` and "
            "`tests/test_packaging.py`. Any other comment there is prose with the digit and absolute scanners "
            "over it."
        ),
    ],
    ("CONTRIBUTING.md", "The three rules this package will not bend"): [
        (
            "- **It never writes into the repository it reads.** `--out` and `--emit-dir` are refused if either "
            "resolves inside `PATH`. Anything that would need to write there is out of scope."
        ),
        (
            "- **It contacts no network and calls no model.** `tests/test_readonly.py` asserts that over the AST of "
            "every module in the installed package (`src/guardrail_checkup`): no `socket`, no `urllib`, no provider "
            "SDK, and two `subprocess` calls that both build their argv with `_argv`, restricted to `git ls-files`, "
            "`git rev-parse` and `git log`. The wheel carries that package and nothing else, which "
            "`tests/test_packaging.py` checks; the *sdist* also ships `scripts/refresh_evidence.py`, which does fetch "
            "two named hosts, and is a maintainer's tool that nothing in the package imports. A feature that needs "
            "any of those is a different package."
        ),
        (
            "- **It reports; it does not rate and it does not enforce.** No readiness score for the repository, no "
            "percentage, no grade, no `--apply`, no `--fix`. Section 3 of the report is a judgement about the "
            "reader's code, and this tool's job is to hand them the evidence for it. The number section 3 prints "
            "beside each candidate is the evidence tally that section defines."
        ),
    ],
}


#: Every row of README.md's *What it looks at* table, cell by cell. The list is
#: closed: an invented row, a deleted one and a reworded one all fail here. An
#: audit shipped three claims through this table -- that the workflow row checks
#: review-before-merge, that an ownerless CODEOWNERS pattern requires a second
#: reviewer, that the test-layout row checks whether the tests are green -- and
#: none of them carried a digit, a flag or an `every`.
LOOKS_AT = [
    "| Artifact | What the report says about it |",
    (
        "| `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules`, `.github/copilot-instructions.md`, "
        "`GEMINI.md` | present or absent; bytes and lines; how many lines both forbid something and name a "
        "path. A directory entry such as `.cursor/rules` fans out over the files in it, up to 64 of them "
        "and until this step's line budget is spent, and the row says how many were read when either "
        "bound bit |"
    ),
    (
        "| `.claude/settings.json`, `.claude/settings.local.json` | per file: whether a `PreToolUse` or "
        "`PostToolUse` hook exists, its matchers, and whether any of them matches a write tool — an omitted "
        "matcher and `*` match every tool, a matcher of only letters, digits, `_`, `-`, spaces, `,` and "
        "`\\|` is an exact list, and anything else is an unanchored regular expression — one this tool "
        "cannot evaluate is reported as unchecked, not as matching nothing. Both are repository-local; the "
        "second is read from disk as well as from the listing, and the report says *present on disk, not "
        "checked in*, because Claude Code gitignores it |"
    ),
    (
        "| `.mcp.json`, `claude_desktop_config.json`, `.claude/mcp.json` | each server, its command line, "
        "and whether the command it runs is one of three known screens (`egresswall`, `mcp-gateway`, "
        "`mcp-scan`), read off the executable name rather than a substring of the line — and only when that "
        "name is bare or an absolute path, because an npm scope is where a package's identity lives. The "
        "first 64 servers get a row each; past that one row says how many there were. These are read from "
        "disk as well as from the listing, for the reason above |"
    ),
    (
        "| `.pre-commit-config.yaml`, git hooks | how many hook ids the framework file declares; which git "
        "hooks are installed — present, not a sample, and executable, because git ignores a hook without "
        "the execute bit and makes the commit anyway, so the ones without it get a row of their own — in "
        "the directory `git rev-parse --git-path hooks` names, so `core.hooksPath` and a linked worktree "
        "are not read as an empty one — and when that directory is outside the repository, a finding says "
        "so and it is not read |"
    ),
    (
        "| `CODEOWNERS` | how many patterns name an owner, how many name none and so require no reviewer, and "
        "— when the file holds more than 2000 distinct owned patterns — how many of them the ranking tested |"
    ),
    (
        "| `.github/workflows/*.yml`, `*.yaml` | per workflow: whether a test runner is named in one of its "
        "`run:` steps — a step `name:`, an `if:` guard, an `env:` value and a job id are not commands — and "
        "whether it runs on pull requests. The first 32 in sorted order are read, and fewer when this "
        "step's line budget is spent first; one row then says how many were read and how many were listed "
        "and not read, and no later row says a scanner is absent |"
    ),
    (
        "| gitleaks / trufflehog / detect-secrets / ggshield / git-secrets | whether any is named outside a "
        "comment in CI, pre-commit, or a config of its own; whether it runs is not checked |"
    ),
    "| lockfiles, test layout | which lockfiles are committed; how many files sit in a test path |",
    (
        "| any of the above that is present and cannot be read | one row saying *present, not read* and why "
        "— over 1 MiB, a NUL byte in the first 8 KiB, or the file would not open. No row then states what "
        "that file does or does not configure |"
    ),
]

#: Behavioural sentences that carry no digit, no flag and no `every`, next to
#: the test that fails first when each stops being true. Closed and verbatim: an
#: audit reversed six of these inside an existing bullet -- an invented tie-break
#: rule, "tracked files only", a fourth hook-test case, fabricated exit-2
#: causes, a demo fixture that forbids writes, a `CHANGELOG.md` bound named
#: wrong -- and every one of them shipped green.
SENTENCES = [
    (
        "README.md",
        "among equal scores the order is the number of matching files, then the name",
        "test_equal_scores_are_ordered_by_the_number_of_matching_files",
    ),
    (
        "README.md",
        "timings at the `CODEOWNERS` bound, at a dense MCP configuration, at the rule-file and workflow "
        "caps in the worst line shape each allows, at the signature scan's byte and file budgets, at a "
        "hundred thousand files through the read recorder, at both history caps and over a whole run of "
        "five thousand files",
        "test_a_vendor_refresh_at_the_path_cap_does_not_decide_how_long_a_checkup_takes",
    ),
    (
        "README.md",
        "injected falsehoods and fails if any of them would have shipped",
        "test_the_doc_truth_suite_fails_on_each_injected_falsehood",
    ),
    (
        "CONTRIBUTING.md",
        "**It never writes into the repository it reads.**",
        "test_writing_inside_the_repository_under_inspection_is_refused",
    ),
    (
        "CONTRIBUTING.md",
        "**It contacts no network and calls no model.**",
        "test_no_shipped_module_imports_anything_that_can_reach_the_network",
    ),
    (
        "CONTRIBUTING.md",
        "**It reports; it does not rate and it does not enforce.**",
        "test_no_rendered_report_carries_a_readiness_score_a_grade_or_a_percentage",
    ),
    (
        "README.md",
        "In a git repository the file list is `git ls-files` (tracked files plus untracked files "
        "`.gitignore` does not exclude)",
        "test_a_git_repository_is_listed_by_git_and_gitignore_is_respected",
    ),
    (
        "README.md",
        "The emitted hook is executed by the test suite against a blocked path, an allowed path and a non-write tool",
        "test_the_emitted_hook_blocks_a_write_under_the_protected_path",
    ),
    (
        "README.md",
        "and `2` on a usage or IO error — a bad path, a `--out` inside the repository, an unwritable directory",
        "test_a_usage_error_is_exit_two_and_one_line",
    ),
    (
        "README.md",
        "(a service with a `db/` directory, a migration, an `.mcp.json`, no hooks, and a `CLAUDE.md` that "
        "forbids nothing)",
        "test_the_fixture_repository_has_the_gaps_the_demo_claims",
    ),
    (
        "README.md",
        "the same commit, with `SOURCE_DATE_EPOCH` set, produces the same bytes apart from the command line "
        "the report records",
        "test_running_twice_on_one_commit_produces_the_same_bytes",
    ),
    (
        "CHANGELOG.md",
        "`egresswall` screens a sample of checked-in JSON fixtures",
        "test_a_checked_in_fixture_is_screened_and_the_report_never_carries_the_value",
    ),
    (
        "CHANGELOG.md",
        "`HISTORY_COMMITS` bounds how far back it looks and `HISTORY_PATHS` bounds how much one commit can cost",
        "test_the_history_walk_stops_at_its_path_cap_and_says_so",
    ),
    (
        "CHANGELOG.md",
        "The only subprocess in the package is `git`, restricted to `ls-files`, `rev-parse` and `log` by an "
        "assertion in the wrapper",
        "test_the_git_wrapper_refuses_a_subcommand_that_is_not_on_the_list",
    ),
    # The heading-less preamble, which belongs to no section and which
    # `list_items` therefore never sees. An invented capability sentence added
    # here -- "It also installs the drafted hook into `.claude/hooks/` once you
    # confirm it." -- shipped through the whole suite.
    (
        "README.md",
        "Deterministic, offline, read-only. It opens no socket, calls no model, runs nothing from the "
        "repository it reads, and writes nothing inside it — every draft goes to a directory you name.",
        "test_a_run_over_a_repository_never_changes_it",
    ),
    (
        "README.md",
        "The judgement stays with you. This tool ranks candidates by evidence and says so in the report; it "
        "does not tell you what your architecture means.",
        "test_the_report_never_points_at_a_candidate_it_did_not_render",
    ),
    # Non-bullet prose under a heading whose closed list holds only its bullets:
    # a false tail on this paragraph -- "the suite installs it into the fixture
    # repository to confirm it blocks there too" -- shipped for the same reason.
    (
        "README.md",
        "The emitted hook is executed by the test suite against a blocked path, an allowed path and a "
        "non-write tool, so it is a script that has run before it reaches anyone's screen.",
        "test_the_emitted_hook_blocks_a_write_under_the_protected_path",
    ),
    # One sentence per section of CONTRIBUTING.md that the gap list does not
    # name. Each of these was reversed and shipped: the Scope guarantee about
    # executing repository code, the pre-release note about the registry, the
    # interpreter warning, and step 2's own rule.
    (
        "CONTRIBUTING.md",
        "any check that would have to execute code from the repository under inspection",
        "test_the_only_subprocess_is_git_and_only_read_only_plumbing",
    ),
    (
        "CONTRIBUTING.md",
        "Until that happens, a checkout without those sibling working copies beside it cannot run CI: "
        "`uv lock --check` and `uv sync` both fail to resolve the two path dependencies before any step runs.",
        "test_the_changelog_records_that_the_path_sources_flip_at_release",
    ),
    (
        "CONTRIBUTING.md",
        "`.python-version` pins 3.11, and `uv run` re-resolves the interpreter from it",
        "test_the_python_classifiers_are_the_versions_ci_runs",
    ),
    (
        "CONTRIBUTING.md",
        "New README claims need a test in `tests/test_readme_truth.py`: the README is executed or pinned, not trusted.",
        "test_every_documented_number_is_the_value_the_code_decides",
    ),
    (
        "CONTRIBUTING.md",
        "`docs/evidence/nemisis-run.txt` is the run this build produces.",
        "test_the_checked_in_run_is_the_run_this_build_produces",
    ),
    # The AI-assistance disclosure the brief requires. It was held by no test:
    # an audit replaced it with "This package was written by hand; only its
    # tests were drafted with AI assistance." and the whole suite passed.
    (
        "CONTRIBUTING.md",
        "This package was written with AI assistance.",
        "test_section_six_discloses_that_the_tool_was_written_with_ai_assistance",
    ),
    (
        "README.md",
        "Written with AI assistance; see `CONTRIBUTING.md`.",
        "test_section_six_discloses_that_the_tool_was_written_with_ai_assistance",
    ),
    # §3 is not the only section the `--max-files` slice decides: §1's own
    # figures are the slice too, and the README said otherwise.
    (
        "README.md",
        "§3's ranking reads the capped listing, and it says so in the "
        "report when the cap bit; §1's file count, byte total and language mix are the capped slice too, and "
        "§1 names both totals.",
        "test_section_one_reports_the_capped_slice_and_names_both_totals",
    ),
    (
        "README.md",
        "The path is printed exactly as you type it — in the header line under the title, in §1 and in §6",
        "test_the_report_prints_the_path_exactly_as_it_was_given",
    ),
]

#: The flags this package does not have and never will. They may be named only
#: inside one of the sentences below, which deny them: `--fix only ever writes
#: inside --emit-dir` is a behaviour claim about a flag that does not exist, and
#: it shipped past a test that checked only the parser.
NON_FEATURES = ("--apply", "--fix", "--install", "--config", "--score", "--model")
NON_FEATURE_PHRASES = (
    "There is no `--apply` and no `--fix`.",
    "no `--apply`, no `--fix`.",
    "an `--apply` or `--install` mode",
)

#: Every other `--flag` the documents name, and whose it is. Closed, like
#: PROSE_NUMBERS: a flag with no entry here and none in the parser fails.
OTHER_FLAGS = {
    "--check": "uv lock, in the note about what the path dependencies stop",
    "--collect-only": "pytest, in the one runnable block",
    "--flag": "the placeholder this file's own rule is written with",
    "--git-path": "git, in the sentence about where hooks live",
    "--name-only": "git, in the sentence about the history walk",
    "--no-renames": "git log, in the decision that bounded the history walk's wall clock",
    "--no-deps": "uv pip, in the sentence about the partial-environment test",
    "--policy": "egresswall proxy and agent-plan-lint check, in the emitted suggestion",
    "--porcelain": "git, in the pinned Nemisis transcript",
    "--python": "uv run, in the note about checking another interpreter",
    "--report": "a flag `cc-safety-net` does not have, named in the decision that removed the claim",
}

#: Every bullet of README.md's "What it does not do" list, in order and *whole*,
#: next to the test that fails first when it stops being true. Held opening-only,
#: an audit reversed the read-only guarantee inside the body of a bullet whose
#: first sentence still read correctly, and it shipped.
DOES_NOT_DO: list[tuple[str, str]] = [
    (
        (
            "- It does not modify the repository it reads. `--out`, `--emit-dir` and each file it would emit are "
            "refused with exit 2 if any of them resolves inside it, symlinks followed; and so is any output path that "
            "is a hard link to a file that already exists — a second name for a file in the repository resolves to "
            "itself, so no path comparison can see it."
        ),
        "test_writing_inside_the_repository_under_inspection_is_refused",
    ),
    (
        "- It does not install, apply, or enable anything. There is no `--apply` and no `--fix`.",
        "test_a_documented_non_feature_has_no_command_line_flag",
    ),
    (
        (
            "- It does not open a socket. There is no network client in the installed package; the one script that "
            "fetches anything, `scripts/refresh_evidence.py`, ships only in the sdist, is never imported by the "
            "package, and is run by hand."
        ),
        "test_no_shipped_module_imports_anything_that_can_reach_the_network",
    ),
    (
        "- It does not call a model. There is no provider, no API key, and no prompt in the package.",
        "test_the_package_has_no_prompt_and_no_provider",
    ),
    (
        "- It does not run the tools it names in §2. It starts no `npx` and no agent CLI.",
        "test_the_only_subprocess_is_git_and_only_read_only_plumbing",
    ),
    (
        (
            "- It does not execute anything from the repository it reads. The only subprocess it starts is `git`, and "
            "only `ls-files`, `rev-parse` and `log`."
        ),
        "test_the_git_wrapper_refuses_a_subcommand_that_is_not_on_the_list",
    ),
    (
        (
            "- It does not give the repository a readiness score, a grade, or a percentage. A number over a judgement "
            "launders it. The per-candidate number in §3 is the evidence tally that section defines — repair commits, "
            "`CODEOWNERS`, path heuristic — not a rating of anything."
        ),
        "test_no_rendered_report_carries_a_readiness_score_a_grade_or_a_percentage",
    ),
    (
        (
            "- It does not read every file. It reads the named guardrail artifacts, `pyproject.toml`, `setup.cfg` and "
            "`package.json` (for the linter falsifier), every checked-in `.json` the signature scan reaches before "
            "its 64 MiB and 10000 file budgets are spent, and the fixture sample — up to 1 MiB each, skipping "
            "anything with a NUL "
            "byte in its first 8 KiB. §1 accounts for each one — the JSON document lists them file by file as "
            "`scope.read` — and nothing this tool opens is missing. A named file it could not read is reported as "
            "present and not read, and no row then answers a question about it; when either budget is spent, §2 says "
            "how many `.json` files were listed and not read rather than reporting that no policy exists."
        ),
        "test_a_binary_file_is_listed_and_not_read",
    ),
    (
        "- It does not know your architecture. §3 is a ranked list of places, and the report says so.",
        "test_the_report_never_points_at_a_candidate_it_did_not_render",
    ),
    (
        (
            "- It does not check what a hook that exists actually does. A `PreToolUse` entry that only appends to a "
            "log reads exactly like one that blocks: presence is checked, behaviour is not, and §5 of every report "
            "says it."
        ),
        "test_a_catch_all_matcher_inspects_every_write",
    ),
    (
        (
            "- It does not follow a symlink out of the repository. One in the `--max-files` slice is reported as a "
            "finding, and any file it points at is not read."
        ),
        "test_a_symlink_out_of_the_repository_is_listed_and_never_read",
    ),
    (
        (
            "- It does not run on a repository's terms. Its own `.git/config` is overridden on every git command "
            "line, because `core.fsmonitor` there would otherwise run a program from the checkout. `core.hooksPath` "
            "is overridden too, on every call but the two `rev-parse` queries that ask where this checkout's hooks "
            "live and which git directory a linked worktree shares — that override is the answer to the first "
            "question, and `rev-parse` fires no hook. That answer is then "
            "contained: a hooks directory outside the repository, and outside the git directory a linked worktree "
            "shares with its main checkout, is reported and never listed."
        ),
        "test_a_repository_config_cannot_make_git_run_a_program",
    ),
    (
        "- It has no config file and no plugin system. The command line is the configuration.",
        "test_a_documented_non_feature_has_no_command_line_flag",
    ),
]


#: The bolded lead of every decision CHANGELOG.md records, in order. A decision
#: reversed in prose -- "the tool writes the drafted hook files into the
#: repository it reads" -- is a lead that stops matching.
BOLD_LEADS = {
    "Decided during the build": [
        "The tool never writes into the repository it reads.",
        "Exit status is 0 whenever the report was written, and 2 on a usage or IO error. It is never 1.",
        "No readiness score, no grade, no percentage for the repository.",
        "The report is deterministic.",
        "Section 2 does not run the tools it names.",
        "A commit is one point, however many files it touched.",
        "The repository under inspection is untrusted input.",
        "A symlink out of the repository is not read.",
        "A hook matcher of `*`, or none at all, matches every tool.",
        "Only a `CODEOWNERS` pattern that names an owner requires a reviewer.",
        "The history walk is bounded twice.",
        "The sdist ships everything the suite reads",
        "The doc-truth suite reads numbers in context.",
    ],
    "Fixed before release, from the second review pass": [
        "A filename cannot run a command on the reviewer's machine.",
        "A filename cannot write markdown into the report.",
        "A symlink loop no longer kills the run.",
        "A directory symlink out of the repository is listed.",
        "The inventory's name-based lookups read the whole listing.",
        "Installed git hooks are found where git looks for them.",
        "An MCP server is screened when the command it runs is a screen",
        "A comment is not a configuration.",
        "Section 5 names no candidate.",
        "One `TEST_PATH`.",
    ],
    "Fixed before release, from the third review pass": [
        "A large `CODEOWNERS` no longer decides how long a checkup takes.",
        "One escaper, and it runs once.",
        "git's paths are read raw.",
        "Both settings files are read, and no row claims anything about the machine.",
        "The Monday list names `PostToolUse` only when a `PostToolUse` hook exists.",
        "A line number is computed once per file.",
        "A missing sibling is one line and exit 2.",
        "A hard link is refused like a path inside the repository.",
        "One reader decides which key an MCP configuration lists its servers under.",
        "The emitted MCP suggestion wraps what it can and says what it did not.",
        "The Monday list names a path, not a phrase.",
        "The doc-truth suite closes more lists.",
        "The comparison page says only what a fetched source says.",
    ],
    "Fixed before release, from the fifth review pass": [
        "A file that is present and cannot be read never produces a negative fact.",
        "A settings file that does not parse says nothing about the hooks in it.",
        "Every string the repository controls now goes through one of the two doors.",
        "An installed git hook is one git will run.",
        "A gitignored `.mcp.json` is read from disk.",
        "A test runner is read off a workflow's `run:` steps.",
        "The secret-scanning sweep goes through the one recorder.",
        "`--max-files` no longer bounds the agent-plan-lint signature scan.",
        "The MCP command line is rendered as a code span rather than escaped into one.",
        "A known screen is a bare name or an absolute path.",
        "A matcher this tool cannot evaluate is reported as unchecked.",
        "The checked-in Nemisis transcript is regenerated and diffed.",
        "`CONTRIBUTING.md` names each class the doc-truth suite still misses.",
        "The tracked-file check skips where there is no git checkout.",
        "`markdown-it-py` joins the development dependencies.",
    ],
    "Fixed before release, from the sixth review pass": [
        "The workflow list is capped like every other axis.",
        "The agent-plan-lint signature scan has a byte budget.",
        "The secret-scanning row says where a scanner was named, not that one is configured.",
        "§1's own figures are the capped slice, and the README says which.",
        "`CONTRIBUTING.md`'s residual list is the nine classes it still misses.",
        "The AI-assistance disclosure is a bound sentence in both documents.",
        "§3's no-candidate paragraph ends before the next heading.",
        "Three README sentences that outran the code.",
        "`scripts/refresh_evidence.py`'s docstring names the test that reads it.",
    ],
    "Fixed before release, from the fourth review pass": [
        "A symlink is refused like a hard link.",
        "A plan with a validation issue no longer raises.",
        "`core.hooksPath` cannot point this tool out of the repository.",
        "A hook matcher is evaluated the three ways the documentation names.",
        "The starter policy's filter is agent-plan-lint's own path type.",
        "The tie-break is the number of matching files.",
        "The starter policy excludes the candidates §3 names.",
        "Every file this tool opens is named in §1.",
        "The rule directory and the MCP table are bounded like everything else.",
        "A job name no longer decides whether a workflow runs on pull requests.",
        "Two consequence cells stopped stating facts about the host.",
        "The Monday list names the instruction file.",
        "The doc-truth suite holds its closed lists whole.",
        "`tests/test_limits.py` is tracked.",
    ],
}

#: README.md's heading-less preamble, whole. It belongs to no section, so
#: `list_items` never sees it and `SENTENCES` only catches a sentence that is
#: reversed or deleted -- an invented capability sentence *added* beside them
#: ("It also installs the drafted hook into `.claude/hooks/` once you confirm
#: it.") shipped through the whole suite. Held like a closed list instead.
PREAMBLE = """**Run it on your own repository and get back the report a consultant would hand you after an
hour: what your agents are actually stopped from doing today, which claims a generic scorer
will get wrong about *this* repository, and up to three ranked places a hook would pay for
itself.**

```
pip install guardrail-checkup
```

Deterministic, offline, read-only. It opens no socket, calls no model, runs nothing from the
repository it reads, and writes nothing inside it — every draft goes to a directory you name.
*Status: 0.1.0. From source: `uv pip install git+https://github.com/Alex-lop/guardrail-checkup`.*

The judgement stays with you. This tool ranks candidates by evidence and says so in the
report; it does not tell you what your architecture means. Deterministic means what it says:
the same commit, with `SOURCE_DATE_EPOCH` set, produces the same bytes apart from the command
line the report records, so two reports can be diffed. Without `SOURCE_DATE_EPOCH` the only
other thing that moves is the date."""


#: Every `##` heading of each document, in order. An entire invented section --
#: *## Telemetry / Each run records an anonymous summary of its finding counts,
#: and nothing else, for the author's own tally* -- shipped green through the
#: whole suite: no closed list, no held sentence and no length check knew about
#: a heading that was not there before. `docs/comparison.md` gets the same
#: treatment in tests/test_comparison_truth.py.
HEADINGS = {
    "README.md": [
        "60 seconds",
        "The six sections",
        "What it looks at",
        "The invariant candidates",
        "What it composes",
        "Observed on a real repository",
        "What it does not do",
        "Command line",
        "How it is tested",
        "Comparison",
        "License",
    ],
    "CHANGELOG.md": [
        "[0.1.0] - 2026-08-31",
    ],
    "CONTRIBUTING.md": [
        "Before you open a PR",
        "The three rules this package will not bend",
        "What the doc-truth suite does not catch",
        "Before the release: the two path dependencies",
        "Checking another Python version",
        "Release checklist",
        "AI assistance",
        "Scope",
    ],
}

#: Prose that belongs to no closed list, held whole under the heading it sits
#: under. `README.md`'s heading-less preamble was the first of these; an audit
#: then appended "Both sibling packages are vendored into the wheel, so a user
#: resolves nothing from the registry" to *License* and "An external security
#: reviewer signed off on the read-only guarantees" to the release preamble, and
#: both shipped green -- a false packaging claim and an invented sign-off, in
#: the two sections nothing read.
HELD_PROSE = {
    (
        "README.md",
        "## License",
    ): """Apache-2.0. Built on [`agent-plan-lint`](https://github.com/Alex-lop/agent-plan-lint) and
[`egresswall`](https://github.com/Alex-lop/egresswall), and on the plan gate and egress
firewall they were extracted from. Written with AI assistance; see `CONTRIBUTING.md`.""",
    (
        "CHANGELOG.md",
        "## [0.1.0] - 2026-08-31",
    ): """The first release. There is no earlier version to have changed from, so this
entry describes what the release contains and what was decided during its
review.""",
}


def prose_under(text: str, heading: str) -> str:
    """The lines under one heading, up to the next heading of any level."""

    return re.split(r"\n#{1,6} ", text.split(f"\n{heading}\n", 1)[1], maxsplit=1)[0].strip()


def check_headings(documents: dict[str, str]) -> None:
    for name, expected in HEADINGS.items():
        found = [line[3:].strip() for line in documents[name].splitlines() if line.startswith("## ")]
        assert found == expected, (name, found)


def check_held_prose(documents: dict[str, str]) -> None:
    for (name, heading), expected in HELD_PROSE.items():
        assert flat(prose_under(documents[name], heading)) == flat(expected), (name, heading)


def check_preamble(readme: str) -> None:
    """The paragraphs above the first `##`, word for word."""

    found = readme.split("\n## ", 1)[0].split("\n", 1)[1]
    assert flat(found) == flat(PREAMBLE), found


def check_class_count(contributing: str, changelog: str) -> None:
    """The spelled count of residual classes, in both documents that state it.

    Two shipped documents stated different counts -- `CONTRIBUTING.md` said ten
    and `CHANGELOG.md`'s fifth-pass bullet said eleven -- and neither figure was
    bound, because a spelled number in a decision bullet is prose to the number
    scanner. An audit swapped one of them for "four" and the whole suite passed.
    Both are the bullet count now, so the two cannot drift again.
    """

    found = list_items(contributing, "What the doc-truth suite does not catch")
    assert f"{word(len(found)).capitalize()} classes still get through." in contributing, len(found)
    assert f"the {word(len(found))} classes it still misses" in flat(changelog), len(found)
    # Spelled, not in digits: the digit form would be read by the number scanner
    # and this binding would be doing nothing.
    assert not re.search(rf"(?<![\w.]){len(found)}(?![\w.]) classes", flat(contributing) + " " + flat(changelog))


#: The package description and its keywords, exactly. PyPI renders both, no test
#: elsewhere reads either, and an invented capability appended to the
#: description is a sentence with no digit and no `every` in it.
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Quality Assurance",
    "Typing :: Typed",
]

#: The comment in `pyproject.toml` that states a fact about the code, whole.
#: Only its first sentence was asserted, so its second -- "Both are the author's
#: own; the report's Provenance section names their installed versions" -- was
#: reversed and shipped.
DEPENDENCY_COMMENT = (
    "# The two sibling packages and nothing else. Both are the author's own; the\n"
    "# report's Provenance section names their installed versions."
)

PYPROJECT_DESCRIPTION = (
    "Run it on your own repository and get the six-section agent-guardrail report: what is enforced, "
    "what a generic scorer gets wrong here, and up to three invariant candidates worth a hook."
)
KEYWORDS = ["agents", "ai-agents", "guardrails", "claude-code", "mcp", "hooks", "audit", "report"]


def check_lists(documents: dict[str, str]) -> None:
    """Every capability list is the length the suite declares."""

    for (name, heading), count in LIST_LENGTHS.items():
        found = list_items(documents[name], heading)
        assert len(found) == count, (name, heading, len(found), count, found)


def check_python_block(readme: str) -> None:
    """The README's Python block is the example the package's own docstring gives.

    Executed against the demo fixture by its own test; compared here so an
    injected attribute -- `result.score` -- fails inside the injection replay too.
    """

    found = re.findall(r"```python\n(.*?)```", readme, re.DOTALL)
    assert len(found) == 1, found
    docstring = textwrap.dedent(guardrail_checkup.__doc__.split("\n\n", 1)[1].split("\n\nDeterministic")[0])
    assert flat(found[0]) == flat(docstring), (found[0], docstring)


def check_table(readme: str) -> None:
    """README's *What it looks at* is the closed table declared above, cell by cell."""

    assert list_items(readme, "What it looks at") == LOOKS_AT


def check_sentences(documents: dict[str, str]) -> None:
    """Every behavioural sentence on the closed list is still there, word for word."""

    for name, sentence, _ in SENTENCES:
        assert flat(sentence) in flat(documents[name]), (name, sentence)


def check_flags(documents: dict[str, str]) -> None:
    """No document names a `--flag` the parser does not have.

    A non-feature may appear only inside a sentence that denies it, so
    "`--fix` only ever writes inside `--emit-dir`" fails where "There is no
    `--apply` and no `--fix`." passes.
    """

    parser = build_parser()
    actions = list(parser._actions)
    for action in parser._subparsers._group_actions:  # type: ignore[union-attr]
        for sub_parser in action.choices.values():  # type: ignore[attr-defined]
            actions.extend(sub_parser._actions)
    known = {option for item in actions for option in item.option_strings} | set(OTHER_FLAGS)
    for name, text in documents.items():
        rest = flat(text)
        for phrase in NON_FEATURE_PHRASES:
            rest = rest.replace(flat(phrase), " ")
        for flag in re.findall(r"(?<![\w-])--[a-z][a-z0-9-]*", rest):
            assert flag in known, (name, flag)
            assert flag not in NON_FEATURES, (name, flag)


def check_denials(readme: str) -> None:
    """README's "What it does not do" is the closed, ordered list declared above.

    Whole bullets, not their openings: an audit reversed the read-only guarantee
    inside the body of a bullet whose first sentence still read correctly.
    """

    found = [flat(item) for item in list_items(readme, "What it does not do") if item.startswith("- ")]
    assert found == [text for text, _ in DOES_NOT_DO], found


def check_closed_items(documents: dict[str, str]) -> None:
    """Every closed list is the text the suite declares, item by item, in order."""

    for (name, heading), expected in CLOSED_ITEMS.items():
        found = [flat(item) for item in list_items(documents[name], heading)]
        assert found == expected, (name, heading, found)


def check_urls(documents: dict[str, str]) -> None:
    """Every `[project.urls]` entry names this package's own repository."""

    entries = dict(line.split(" = ", 1) for line in documents["pyproject urls"].splitlines())
    assert entries["Source"] == PROJECT_SOURCE, entries["Source"]
    for name, url in entries.items():
        assert url.startswith(PROJECT_SOURCE), (name, url)


def check_leads(changelog: str) -> None:
    """Every decision the CHANGELOG records, by its bolded lead, in order."""

    for heading, leads in BOLD_LEADS.items():
        body = "\n".join(list_items(changelog, heading))
        found = [
            match.group(1)
            for match in (
                re.match(r"- \*\*(.+?)\*\*", flat(item)) for item in re.split(r"\n(?=- )", body) if item.strip()
            )
            if match
        ]
        assert found == leads, (heading, found)


def check_numbers(documents: dict[str, str], repo_root: Path) -> None:
    bound = code_numbers(repo_root)
    for name, text in documents.items():
        declared = PROSE_NUMBERS[name]
        for number in sorted(set(NUMBER.findall(text))):
            assert number in bound or number in declared, (name, number)
        # And each declared figure still has to appear in the sentence it was
        # declared for, so one whitelisted figure cannot stand in for another.
        for number, (pattern, why) in declared.items():
            assert re.search(pattern, flat(text)), (name, number, pattern, why)
    for literal, value in bound.items():
        assert str(value) == literal, (literal, value)


def check_absolutes(documents: dict[str, str]) -> None:
    """No `every`/`all` sentence in any scanned document is off the declared list.

    Over `documents`, not over `DECLARED_ABSOLUTES`: keyed off the declaration,
    a document with no entry -- `CONTRIBUTING.md`, the package description, its
    keywords, its classifiers, its comments -- was never scanned at all, and an
    audit rewrote this file's own contribution rules with two absolutes in them.
    """

    for name, text in documents.items():
        rest = flat(text)
        for phrase in DECLARED_ABSOLUTES.get(name, {}):
            rest = rest.replace(flat(phrase), " ")
        left = re.findall(r"(?i).{40}\b(?:every|all)\b.{40}", rest)
        assert left == [], (name, left)


def check_documents(documents: dict[str, str], bound: list[tuple[str, str, str]], repo_root: Path) -> None:
    """Every mechanism this file has, over the documents given. The injection hook."""

    for name, pattern, why in bound:
        assert re.search(pattern, flat(documents[name])), (name, pattern, why)
    check_numbers(documents, repo_root)
    check_absolutes(documents)
    check_lists(documents)
    check_closed_items(documents)
    check_urls(documents)
    check_table(documents["README.md"])
    check_sentences(documents)
    check_flags(documents)
    check_denials(documents["README.md"])
    check_leads(documents["CHANGELOG.md"])
    # The comparison page's rule, over the two documents that state the same
    # claim: without SOURCE_DATE_EPOCH the date line moves, so the unqualified
    # form is false wherever it is written.
    check_determinism(documents["README.md"])
    check_determinism(documents["CHANGELOG.md"])
    assert documents["pyproject description"] == PYPROJECT_DESCRIPTION
    assert documents["pyproject keywords"] == " ".join(KEYWORDS)
    assert documents["pyproject classifiers"] == "\n".join(CLASSIFIERS)
    assert not [item for item in CLASSIFIERS if item.startswith("License ::")], "the SPDX field is the licence"
    assert DEPENDENCY_COMMENT in documents["pyproject comments"]
    check_python_block(documents["README.md"])
    check_preamble(documents["README.md"])
    check_headings(documents)
    check_held_prose(documents)
    check_class_count(documents["CONTRIBUTING.md"], documents["CHANGELOG.md"])
    assert not re.search(r"(?i)\b(scores?|graded?|percentage)\b", documents["pyproject description"])


def test_every_documented_number_is_the_value_the_code_decides(
    documents: dict[str, str], bound: list[tuple[str, str, str]], repo_root: Path
) -> None:
    check_documents(documents, bound, repo_root)


def test_every_number_in_the_documents_is_bound_to_the_code_or_declared_prose(
    documents: dict[str, str], repo_root: Path
) -> None:
    check_numbers(documents, repo_root)


def test_every_absolute_claim_in_the_documents_is_on_the_declared_list(documents: dict[str, str]) -> None:
    """An invented capability carries no digit. It does carry `every` or `all`."""

    check_absolutes(documents)


def test_every_capability_list_is_the_length_the_suite_declares(documents: dict[str, str]) -> None:
    check_lists(documents)


def test_every_closed_list_is_the_text_the_suite_declares(documents: dict[str, str]) -> None:
    """Whole items, in order: a reversal inside one is what an opening cannot see."""

    check_closed_items(documents)


def test_every_project_url_names_this_packages_own_repository_in_the_documents(documents: dict[str, str]) -> None:
    check_urls(documents)


def test_every_row_of_the_what_it_looks_at_table_is_the_declared_one(readme: str) -> None:
    check_table(readme)


def test_every_behavioural_sentence_on_the_closed_list_names_a_test_that_exists(
    documents: dict[str, str], repo_root: Path
) -> None:
    check_sentences(documents)
    names = set()
    for path in sorted((repo_root / "tests").glob("test_*.py")):
        names |= {
            node.name for node in ast.walk(ast.parse(path.read_text("utf-8"))) if isinstance(node, ast.FunctionDef)
        }
    for _, sentence, test_name in SENTENCES:
        assert test_name in names, (sentence, test_name)


def test_no_document_names_a_flag_this_package_does_not_have(documents: dict[str, str]) -> None:
    check_flags(documents)


def test_the_determinism_claim_carries_its_qualifier_in_both_documents(documents: dict[str, str]) -> None:
    check_determinism(documents["README.md"])
    check_determinism(documents["CHANGELOG.md"])


def test_the_readme_denies_exactly_the_things_the_suite_has_a_test_for(
    readme: str, documents: dict[str, str], repo_root: Path
) -> None:
    check_denials(readme)
    names = set()
    for path in sorted((repo_root / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text("utf-8"))
        names |= {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    for opening, test_name in DOES_NOT_DO:
        assert test_name in names, (opening, test_name)


def test_every_decision_the_changelog_records_is_the_one_the_code_made(documents: dict[str, str]) -> None:
    check_leads(documents["CHANGELOG.md"])


def test_the_package_description_and_keywords_are_the_declared_ones(repo_root: Path) -> None:
    """PyPI renders both; nothing else in the suite reads a keyword."""

    meta = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert meta["description"] == PYPROJECT_DESCRIPTION
    assert meta["keywords"] == KEYWORDS
    assert not re.search(r"(?i)\b(scores?|graded?|grading|percentage)\b", " ".join(KEYWORDS))


def test_the_package_description_promises_no_score(documents: dict[str, str]) -> None:
    assert not re.search(r"(?i)\b(scores?|graded?|percentage)\b", documents["pyproject description"])
    assert "scorer" in documents["pyproject description"], "it says what a scorer gets wrong, not that it scores"


def test_the_seven_categories_the_readme_lists_are_the_categories_in_the_code(readme: str) -> None:
    """The list, in order, and nothing beside it: an eighth category is a new noun."""

    nouns = [noun for _, noun, _ in CATEGORIES]
    assert len(nouns) == 7
    listed = ", ".join(nouns[:-1]) + ", and " + nouns[-1]
    assert f"the seven places a junior would be stopped: {listed};" in flat(readme)


def test_the_python_block_in_the_readme_is_code_that_runs(readme: str, fixture_repo: Path) -> None:
    """The one block the suite executes rather than pins: an invented attribute fails here."""

    blocks_found = re.findall(r"```python\n(.*?)```", readme, re.DOTALL)
    assert len(blocks_found) == 1, blocks_found
    source = blocks_found[0].replace('"/path/to/repo"', repr(str(fixture_repo)))
    namespace: dict[str, object] = {}
    exec(compile(source, "README.md", "exec"), namespace)
    assert namespace["result"].head


# --- the injected falsehoods -----------------------------------------------------


#: The falsehoods an audit injected one at a time into the earlier version of
#: these documents. Every one of them shipped green then. Each entry is
#: (case, document, the true text, the false text), and the test below fails if
#: any of them would ship now. The comparison page's three swaps are the same
#: exercise in tests/test_comparison_truth.py.
INJECTIONS = [
    ("I01 the read cap", "README.md", "up to 1 MiB each", "up to 4 MiB each"),
    ("I02 the skip list", "README.md", "skips 13 well-known directories", "skips 5 well-known directories"),
    ("I03 the history depth", "README.md", "last 2000 non-merge commits", "last 20000 non-merge commits"),
    ("I04 the listing cap", "README.md", "`--max-files` (default 20000)", "`--max-files` (default 2000)"),
    ("I05 the fixture sample", "README.md", "up to 5 checked-in JSON", "up to 3 checked-in JSON"),
    ("I06 the sniff window", "README.md", "NUL byte in its first 8 KiB", "NUL byte in its first 2 KiB"),
    ("I07 the categories", "README.md", "the seven places a junior", "the nine places a junior"),
    (
        "I08 an invented capability",
        "README.md",
        "## What it does not do",
        "## What it does not do\n\nIt flags every hard-coded credential it finds and rewrites your `.gitignore` "
        "in place.\n",
    ),
    (
        "I12 the exit statuses",
        "README.md",
        "Exit status is `0` whenever the report was written, and `2` on a usage or IO error",
        "Exit status is `2` whenever the report was written, and `0` on a usage or IO error",
    ),
    ("I13 the hook's block code", "README.md", "which exits 2 to block the call", "which exits 0 to block the call"),
    (
        "I14 the scoring weights",
        "README.md",
        "+ 2 if `CODEOWNERS` names one of them, + 1 if the path heuristic",
        "+ 3 if `CODEOWNERS` names one of them, + 2 if the path heuristic",
    ),
    ("I15 the CI matrix", "README.md", "on Ubuntu and macOS,", "on Ubuntu, macOS and Windows,"),
    ("I16 the regression weight", "CHANGELOG.md", "weighs a repair commit double", "weighs a repair commit triple"),
    (
        "I17 a score in the description",
        "pyproject description",
        "what a generic scorer gets wrong here",
        "a 0-100 readiness score",
    ),
    ("C1 the Monday cap", "README.md", "at most five actions", "at most four actions"),
    ("C2 the demo's repairs", "README.md", "a history with three repairs", "a history with two repairs"),
    # The second audit: twenty falsehoods that shipped green through the whole
    # suite. Each one is here next to the mechanism that now catches it.
    ("A01 the bare-match score", "README.md", "at score 1 is a bare", "at score 2 is a bare"),
    ("A02 the regression weight in prose", "README.md", "weighted double when", "weighted triple when"),
    ("A03 the third-candidate rule", "README.md", "fewer than three categories", "fewer than six categories"),
    (
        "A06 an invented artifact row",
        "README.md",
        "| lockfiles, test layout |",
        "| `.gitleaks.toml` | the rules it configures, and which of them this tool re-implements |\n"
        "| lockfiles, test layout |",
    ),
    (
        "A07 a score and a grade",
        "README.md",
        "- **`egresswall`** —",
        "- It scores the repository and grades it against a baseline.\n- **`egresswall`** —",
    ),
    (
        "A08 an --apply mode",
        "README.md",
        "- **`CODEOWNERS`** — the paths",
        "- It can install the hook it drafts for you when you pass `--apply`;\n- **`CODEOWNERS`** — the paths",
    ),
    (
        "A09 a source of evidence it does not read",
        "README.md",
        "- **`CODEOWNERS`** — the paths",
        "- **CI logs** — it reads your CI logs to rank the candidates;\n- **`CODEOWNERS`** — the paths",
    ),
    ("A27 the licence", "README.md", "Apache-2.0. Built on", "MIT. Built on"),
    (
        "A15 an --apply mode in the changelog",
        "CHANGELOG.md",
        "- `--emit-dir` for the drafted policy",
        "- `--apply` installs the drafted hook into `.claude/hooks/` for you.\n- `--emit-dir` for the drafted policy",
    ),
    ("A16 how many repositories one run reads", "CHANGELOG.md", "one repository:", "two repositories:"),
    (
        "A28 a reversed decision",
        "CHANGELOG.md",
        "**The tool never writes into the repository it reads.**",
        "**The tool writes the drafted hook files into the repository it reads.**",
    ),
    (
        "A17 an invented capability in the description",
        "pyproject description",
        "worth a hook.",
        "worth a hook, and installs them for you.",
    ),
    ("A18 a score in the keywords", "pyproject keywords", "audit report", "audit report score grading"),
    # The third audit: twenty-three falsehoods that shipped green through the
    # whole suite, each next to the mechanism that now catches it.
    ("X01 the screen count", "README.md", "one of three known screens", "one of six known screens"),
    (
        "X02 a fabricated screen",
        "README.md",
        "`mcp-gateway`, `mcp-scan`), read off",
        "`mcp-gateway`, `mcp-scan`, `snyk-mcp`), read off",
    ),
    (
        "X03 a capability invented in a table row",
        "README.md",
        "are not commands — and whether it runs on pull requests. The first",
        "are not commands, whether it runs on pull requests, whether review before merge is required. The first",
    ),
    (
        "X04 a table row reversed",
        "README.md",
        "how many name none and so require no reviewer",
        "how many name none and so require a second reviewer",
    ),
    (
        "X05 an eighth path category",
        "README.md",
        "and the dependency lockfiles;",
        "the dependency lockfiles, and the CI workflow definitions;",
    ),
    (
        "X06 an invented tie-break rule",
        "README.md",
        "among equal scores the order is the number of\nmatching files, then the name",
        "among equal scores the order is the most recently touched, then the name",
    ),
    (
        "X07 a fourth hook-test case",
        "README.md",
        "against a blocked path, an allowed path and a\nnon-write tool",
        "against a blocked path, an allowed path, a non-write tool and a symlinked path",
    ),
    (
        "X08 a listing rule reversed",
        "README.md",
        "(tracked files\nplus untracked files `.gitignore` does not exclude)",
        "(tracked files only; an untracked file is never listed)",
    ),
    (
        "X09 fabricated exit-2 causes",
        "README.md",
        "a bad\npath, a `--out` inside the repository, an unwritable directory",
        "a bad path, a malformed `.mcp.json`, a repository with no commits",
    ),
    (
        "X10 a flag this package does not have",
        "README.md",
        "`python -m guardrail_checkup` is the same CLI",
        "`python -m guardrail_checkup` is the same CLI plus `--quiet`",
    ),
    (
        "X11 a Python API that does not exist",
        "README.md",
        "print(result.head, [item.slug for item in result.candidates])",
        "print(result.score, [item.slug for item in result.candidates])",
    ),
    (
        "X12 the determinism qualifier removed",
        "README.md",
        "the same commit, with `SOURCE_DATE_EPOCH` set, produces the same bytes apart from the command\n"
        "line the report records",
        "the same commit produces the same bytes",
    ),
    (
        "X13 a demo fixture that forbids writes",
        "README.md",
        "no hooks, and a `CLAUDE.md` that forbids nothing)",
        "no hooks, and a `CLAUDE.md` that forbids writes under `db/`)",
    ),
    (
        "X14 a behaviour given to a non-feature",
        "README.md",
        "There is no `--apply` and no `--fix`.",
        "There is no `--apply`; `--fix` only ever writes inside `--emit-dir`.",
    ),
    (
        "X15 a subcommand added to the git allowlist",
        "CHANGELOG.md",
        "restricted to `ls-files`,\n  `rev-parse` and `log` by an assertion in the wrapper",
        "restricted to `ls-files`, `rev-parse`, `diff` and `log` by an assertion in the wrapper",
    ),
    (
        "X16 a screen pointed at something it never sees",
        "CHANGELOG.md",
        "`egresswall` screens a sample of checked-in JSON fixtures",
        "`egresswall` screens the live MCP servers",
    ),
    (
        "X17 the wrong constant named as a bound",
        "CHANGELOG.md",
        "`HISTORY_COMMITS` bounds how far back\n  it looks and `HISTORY_PATHS` bounds how much one commit can cost",
        "`HISTORY_COMMITS` bounds how far back it looks and `MAX_READ_BYTES` bounds how much one commit can cost",
    ),
    (
        "X18 a licence classifier the SPDX field contradicts",
        "pyproject classifiers",
        "Typing :: Typed",
        "License :: OSI Approved :: MIT License\nTyping :: Typed",
    ),
    (
        "X19 a third dependency in a comment",
        "pyproject comments",
        "# The two sibling packages and nothing else.",
        "# The two sibling packages plus PyYAML.",
    ),
    (
        "X25 a table row that claims it runs the tests",
        "README.md",
        "how many files sit in a test path |",
        "how many files sit in a test path, and whether they are green |",
    ),
    # The fourth audit: falsehoods that shipped green through the previous
    # version because a closed list held only the opening of each item, because
    # CONTRIBUTING.md was in `documents` and in no scan, and because a declared
    # prose figure was checked for membership rather than for its sentence.
    (
        "J02 a reversed rule in CONTRIBUTING's own three",
        "CONTRIBUTING.md",
        "- **It never writes into the repository it reads.**",
        "- **It writes the drafted hook files into the repository it reads.**",
    ),
    (
        "J09 an invented fourth rule",
        "CONTRIBUTING.md",
        "\n## What the doc-truth suite does not catch",
        "- **It uploads a record of each run to the author.** The record names the\n  repository and the "
        "findings.\n\n## What the doc-truth suite does not catch",
    ),
    (
        "J03 a reversed CHANGELOG Added bullet",
        "CHANGELOG.md",
        "which bounds the ranking, language mix and symlink inspection but not the\n  inventory's name-based "
        "lookups or the agent-plan-lint signature scan",
        "which bounds the ranking, language mix, symlink inspection and every inventory lookup",
    ),
    (
        "J11 a reversed pre-release note",
        "CHANGELOG.md",
        "**The release deletes that table and re-locks**",
        "**The release keeps that table**",
    ),
    (
        "J12 a denial reversed inside a bullet whose opening is held",
        "README.md",
        "It starts no `npx` and no agent CLI.",
        "It runs each of them and folds their output into §2.",
    ),
    (
        "J05 a rewritten item of The six sections",
        "README.md",
        "5. **What this did not cover** — branch protection, production, secrets in history, runtime,",
        "5. **What this did not cover** — a short note; the report reads the host's branch protection,",
    ),
    (
        "J06 a rewritten item of What it composes",
        "README.md",
        "the report names the reason code and the path, never the value",
        "the report names the reason code, the path and the value it found",
    ),
    (
        "J07 one declared prose figure swapped for another",
        "README.md",
        "## 60 seconds",
        "## 16 seconds",
    ),
    (
        "J20 the suite's own behaviour softened",
        "README.md",
        "and fails if any of them would have shipped",
        "and reports which of them would have shipped",
    ),
    (
        "J23 absolutes in a document nothing scanned",
        "CONTRIBUTING.md",
        "2. New behaviour needs a test. New README claims need a test in",
        "2. Every new behaviour is covered by a test, and all README claims are executed or pinned in",
    ),
    # The fifth audit: eleven of the seventeen falsehoods that shipped green
    # through the previous version, each next to the binding that now holds it.
    # The other six fell in classes CONTRIBUTING.md already declared.
    (
        "N01 an invented capability in the preamble",
        "README.md",
        "The judgement stays with you.",
        "It also installs the drafted hook into `.claude/hooks/` once you confirm it. The judgement stays with you.",
    ),
    (
        "N02 a false tail on prose no closed list holds",
        "README.md",
        "so it is a script that has run before it reaches anyone's screen.",
        "so it is a script that has run before it reaches anyone's screen, and the suite installs it into "
        "the fixture repository to confirm it blocks there too.",
    ),
    (
        "N03 the Scope guarantee reversed",
        "CONTRIBUTING.md",
        "any check that would have to execute code from the repository under\ninspection",
        "any check that cannot execute code from the repository under inspection",
    ),
    (
        "N04 the pre-release note reversed",
        "CONTRIBUTING.md",
        "cannot run CI: `uv lock --check` and `uv sync` both fail to resolve the\ntwo path dependencies",
        "cannot run CI's wheel-install step, which resolves the two path dependencies",
    ),
    (
        "N05 the interpreter warning reversed",
        "CONTRIBUTING.md",
        "`.python-version` pins 3.11, and `uv run` re-resolves the interpreter from it",
        "`.python-version` pins 3.11, and `uv run` ignores it once `--python` has been passed once",
    ),
    (
        "N06 the body of a gap bullet rewritten",
        "CONTRIBUTING.md",
        "comment or docstring in `src/`, `tests/`, `demo/` or `scripts/` is read by no\n  test,",
        "comment or docstring anywhere in this repository is read by a test,",
    ),
    (
        "N10 the residual-class count",
        "CONTRIBUTING.md",
        "Nine classes still get through.",
        "Four classes still get through.",
    ),
    (
        "N11 a fifth-pass decision reversed",
        "CHANGELOG.md",
        "**An installed git hook is one git will run.**",
        "**An installed git hook is any file in the hooks directory.**",
    ),
    (
        "N12 a table row that claims it reads what a workflow mentions",
        "README.md",
        "whether a test runner is named in one of its `run:` steps",
        "whether a test runner is named anywhere in it",
    ),
    (
        "N18 the second sentence of the dependency comment",
        "pyproject comments",
        "Both are the author's own; the\n# report's Provenance section names their installed versions.",
        "Neither is the author's own; the\n# report's Provenance section omits their installed versions.",
    ),
    (
        "K01 the section the listing cap decides",
        "README.md",
        "§3's ranking reads the capped listing",
        "§3's ranking reads the whole listing",
    ),
    (
        "K02 where the given path is printed",
        "README.md",
        "in the header line under the title, in §1 and in §6",
        "in the title line, in §1 and in §6",
    ),
    (
        "K03 the AI-assistance disclosure",
        "CONTRIBUTING.md",
        "This package was written with AI assistance.",
        "This package was written by hand; only its tests were drafted with AI assistance.",
    ),
    (
        "K04 the residual-class count in the CHANGELOG",
        "CHANGELOG.md",
        "the nine classes it still misses",
        "the four classes it still misses",
    ),
    ("K06 the workflow cap", "README.md", "The first 32 in sorted order", "The first 320 in sorted order"),
    (
        "K07 the signature scan's budget",
        "README.md",
        "before its 64 MiB and 10000 file budgets are spent",
        "before its 640 MiB and 10000 file budgets are spent",
    ),
    (
        "J16 a project URL repointed at another repository",
        "pyproject urls",
        "Changelog = https://github.com/Alex-lop/guardrail-checkup/blob/main/CHANGELOG.md",
        "Changelog = https://github.com/Alex-lop/Nemisis/blob/main/CHANGELOG.md",
    ),
    # The seventh audit: three survivors, each in a class no list named. The
    # first is the highest-value falsehood any sweep has shipped -- a whole
    # invented capability, contradicting the offline promise, under a heading
    # nothing read.
    (
        "P01 an invented section beside the declared ones",
        "README.md",
        "## License",
        "## Telemetry\n\nEach run records an anonymous summary of its finding counts, and nothing else, for the "
        "author's own tally.\n\n## License",
    ),
    (
        "P02 a sign-off invented in the release preamble",
        "CHANGELOG.md",
        "entry describes what the release contains and what was decided during its\nreview.",
        "entry describes what the release contains and what was decided during its\nreview. An external security "
        "reviewer signed off on the read-only guarantees.",
    ),
    (
        "P03 a packaging claim in the License section",
        "README.md",
        "Written with AI assistance; see `CONTRIBUTING.md`.",
        "Written with AI assistance; see `CONTRIBUTING.md`. Both sibling packages are vendored into the wheel, "
        "so a user resolves nothing from the registry.",
    ),
    # The eighth audit: the two shipped sentences it found false, put back.
    (
        "Q01 the starter policy's write globs, uncapped",
        "README.md",
        "touched, capped at 64 with §2 naming the count and the cut",
        "touched, all of them",
    ),
    (
        "Q02 the inventory row claim, unscoped",
        "README.md",
        "that cites a file carries its `file:line`; a row that states an absence carries `-`",
        "carries the `file:line` it came from, absence rows included",
    ),
    (
        "Q03 the workflow row's line budget",
        "README.md",
        "The first 32 in sorted order are read, and fewer when this step's line budget is spent first",
        "The first 32 in sorted order are read",
    ),
]


@pytest.mark.parametrize("case", INJECTIONS, ids=[item[0] for item in INJECTIONS])
def test_the_doc_truth_suite_fails_on_each_injected_falsehood(
    documents: dict[str, str], bound: list[tuple[str, str, str]], repo_root: Path, case: tuple[str, str, str, str]
) -> None:
    _, name, true, false = case
    assert true in documents[name], (name, true)
    mutated = dict(documents)
    mutated[name] = documents[name].replace(true, false, 1)
    with pytest.raises(AssertionError):
        check_documents(mutated, bound, repo_root)


# --- the absolute claims --------------------------------------------------------


@pytest.mark.parametrize(
    "sentence,test_name",
    [
        ("It opens no socket", "test_no_shipped_module_imports_anything_that_can_reach_the_network"),
        ("calls no model", "test_the_package_has_no_prompt_and_no_provider"),
        ("runs nothing from the\nrepository it reads", "test_the_only_subprocess_is_git_and_only_read_only_plumbing"),
        ("writes nothing inside it", "test_a_run_over_a_repository_never_changes_it"),
        ("does not modify the repository it reads", "test_writing_inside_the_repository_under_inspection_is_refused"),
        ("It does not open a socket", "test_no_shipped_module_imports_anything_that_can_reach_the_network"),
        ("It does not call a model", "test_the_package_has_no_prompt_and_no_provider"),
        ("It does not run the tools it names", "test_the_only_subprocess_is_git_and_only_read_only_plumbing"),
        ("only `ls-files`, `rev-parse` and `log`", "test_the_git_wrapper_refuses_a_subcommand_that_is_not_on_the_list"),
        ("never the value", "test_a_checked_in_fixture_is_screened_and_the_report_never_carries_the_value"),
        ("Nothing is applied", "test_the_wrapped_mcp_configuration_puts_the_proxy_in_front_of_every_server"),
        ("does not invent a third", "test_the_report_never_points_at_a_candidate_it_did_not_render"),
        ("It is never `1`", "test_the_cli_never_returns_one"),
        (
            "the same commit, with `SOURCE_DATE_EPOCH` set, produces the same bytes",
            "test_running_twice_on_one_commit_produces_the_same_bytes",
        ),
        ('valid" is checked, not claimed', "test_every_starter_policy_this_tool_emits_loads"),
        (
            "It does not follow a symlink out of the repository",
            "test_a_symlink_out_of_the_repository_is_listed_and_never_read",
        ),
        (
            "Its own `.git/config` is overridden on every git command line",
            "test_a_repository_config_cannot_make_git_run_a_program",
        ),
        (
            "It does not check what a hook that exists actually does",
            "test_a_catch_all_matcher_inspects_every_write",
        ),
        (
            "There is no network client in the installed package",
            "test_no_script_outside_the_installed_package_reaches_the_network_except_the_documented_one",
        ),
        (
            "is never imported by the package",
            "test_nothing_in_the_installed_package_imports_the_one_script_that_fetches",
        ),
        (
            "It does not give the repository a readiness score, a grade, or a percentage",
            "test_no_rendered_report_carries_a_readiness_score_a_grade_or_a_percentage",
        ),
        (
            "`--format json` writes the same facts as a JSON document",
            "test_json_format_is_a_document_with_the_same_facts",
        ),
        (
            "§2's name-based\ninventory lookups and the signature scan still ask the whole listing",
            "test_an_artifact_that_sorts_past_the_listing_cap_is_still_found",
        ),
        (
            "The path is printed exactly as you type it",
            "test_the_report_prints_the_path_exactly_as_it_was_given",
        ),
        (
            "in the directory `git rev-parse --git-path hooks` names",
            "test_an_installed_hook_is_found_when_core_hookspath_moves_the_directory",
        ),
        (
            "read off the executable name rather than a substring of the line",
            "test_a_package_merely_named_proxy_is_not_reported_as_a_screen",
        ),
        (
            "whether any is named outside a comment",
            "test_a_workflow_that_says_it_does_not_use_a_scanner_is_not_reported_as_having_one",
        ),
    ],
)
def test_each_absolute_claim_names_a_test_that_exists(
    readme: str, sentence: str, test_name: str, repo_root: Path
) -> None:
    assert " ".join(sentence.split()) in " ".join(readme.split()), sentence
    names = set()
    for path in sorted((repo_root / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names |= {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    assert test_name in names, test_name


def test_every_heading_in_the_documents_is_one_the_suite_declares(documents: dict[str, str]) -> None:
    """A whole invented section is a heading no list knows: *## Telemetry* shipped green."""

    check_headings(documents)


def test_the_prose_no_closed_list_reads_is_held_whole(documents: dict[str, str]) -> None:
    """README's *License* and CHANGELOG's release preamble, word for word."""

    check_held_prose(documents)


def test_the_number_of_residual_classes_contributing_states_is_the_number_it_lists(
    documents: dict[str, str],
) -> None:
    """The count sentence is prose to the number scanner, so it gets a binding of its own.

    "Four classes still get through." was false by thirteen when an audit
    counted: seventeen of twenty-three injections shipped, eleven of them in
    classes the list did not name. `CHANGELOG.md` then stated a different count
    from this file's, and an audit swapped that one for "four" green.
    """

    check_class_count(documents["CONTRIBUTING.md"], documents["CHANGELOG.md"])


def test_the_cli_never_returns_one(repo_root: Path) -> None:
    """`It is never 1` -- asserted over the CLI's own returns, not over one run."""

    assert exit_statuses(repo_root) == {0, 2}


@pytest.mark.parametrize("flag", ["--apply", "--fix", "--install", "--config", "--score", "--model"])
def test_a_documented_non_feature_has_no_command_line_flag(flag: str) -> None:
    parser = build_parser()
    actions = list(parser._actions)
    for action in parser._subparsers._group_actions:  # type: ignore[union-attr]
        for sub in action.choices.values():  # type: ignore[attr-defined]
            actions.extend(sub._actions)
    assert flag not in {option for item in actions for option in item.option_strings}


# --- identity and quotation ------------------------------------------------------


def test_the_install_route_names_this_distribution(readme: str, repo_root: Path) -> None:
    meta = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert f"pip install {NAME}" in readme
    assert meta["name"] == NAME == guardrail_checkup.NAME
    assert meta["scripts"] == {NAME: "guardrail_checkup._cli:main"}
    assert f"uv pip install git+{meta['urls']['Source']}" in readme


def test_no_url_in_the_readme_names_another_repository_of_the_authors(readme: str, repo_root: Path) -> None:
    source = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["urls"]["Source"]
    siblings = ("agent-plan-lint", "egresswall", "Nemisis")
    for url in re.findall(r"https?://[^\s\"'()<>]+", readme):
        if "github.com/Alex-lop" not in url:
            continue
        assert url.startswith(source) or any(url.endswith(item) for item in siblings), url


def test_every_quotation_in_the_readme_is_in_a_checked_in_source(readme: str) -> None:
    assert unquoted(readme) == []


# --- the checked-in run over a real repository ------------------------------------

#: The evidence transcript README's *Observed on a real repository* pins, and
#: everything needed to produce it again. The checkout is the author's own
#: working copy beside this package; CI does not have it, so the test below
#: skips there rather than pretending. It ran once against a stale transcript --
#: a pre-fix run mislabelled as the shipped version, whose §1 and CODEOWNERS
#: rows the shipped build no longer produces -- and nothing failed, because the
#: only thing bound was the three blocks README quotes.
NEMISIS = {
    "path": "assets/Nemisis",
    "head": "1491f7ca1d674114c6e09f92abdb1301cb25a158",
    "epoch": "1788134400",
    "out": "gcnem/REPORT.md",
    "emit": "gcnem/drafts",
    "evidence": "docs/evidence/nemisis-run.txt",
}


def nemisis_command() -> str:
    return f"guardrail-checkup run {NEMISIS['path']} --out {NEMISIS['out']} --emit-dir {NEMISIS['emit']}"


def nemisis_transcript(checkout: Path, work: Path, env: dict[str, str], stamp: str) -> str:
    """The transcript again, from the code in this tree, byte for byte.

    Run from a directory that is not the checkout and is not this package, with
    `assets/Nemisis` a symlink to the checkout: that is what makes the pinned
    command line relative, so the transcript demonstrates the advice the README
    gives instead of carrying two absolute paths through a shipped document.
    """

    (work / "assets").mkdir(parents=True, exist_ok=True)
    (work / "assets" / "Nemisis").symlink_to(checkout)
    run = {**env, **GIT_ENV, "SOURCE_DATE_EPOCH": NEMISIS["epoch"]}
    done = subprocess.run(nemisis_command(), shell=True, cwd=work, env=run, capture_output=True, text=True, timeout=300)
    assert done.returncode == 0, done.stderr
    status = subprocess.run(
        f"git -C {NEMISIS['path']} status --porcelain | wc -l",
        shell=True,
        cwd=work,
        env=run,
        capture_output=True,
        text=True,
        timeout=300,
    )
    body = [
        f"# source: guardrail-checkup {__version__} run over a local read-only checkout of github.com/Alex-lop/Nemisis",
        f"# command: SOURCE_DATE_EPOCH={NEMISIS['epoch']} {nemisis_command()}",
        f"# run from: a directory outside the checkout, with {NEMISIS['path']} a symlink to it",
        f"# commit: {NEMISIS['head']}",
        f"# fetched: {stamp}",
        "",
        f"$ {nemisis_command()}",
        done.stdout.strip(),
        f"$ git -C {NEMISIS['path']} status --porcelain | wc -l",
        status.stdout.strip(),
        "",
        "--- REPORT.md ---",
        (work / NEMISIS["out"]).read_text(encoding="utf-8").rstrip("\n"),
        "",
    ]
    return "\n".join(body)


def test_the_checked_in_run_is_the_run_this_build_produces(
    repo_root: Path, tmp_path: Path, shell_env: dict[str, str]
) -> None:
    """Re-run the pinned session and diff the whole transcript, not the three quoted blocks.

    Set GUARDRAIL_CHECKUP_REGENERATE_EVIDENCE=1 to rewrite the file instead of
    comparing it; that is how it is regenerated, and CONTRIBUTING.md says so.
    """

    checkout = repo_root.parent.parent / "assets" / "Nemisis"
    if not (checkout / ".git").exists():
        pytest.skip(f"{checkout} is not a checkout on this machine")
    head = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    if head.stdout.strip() != NEMISIS["head"]:
        pytest.skip(f"{checkout} is at {head.stdout.strip()[:12]}, not the commit this transcript records")

    evidence = repo_root / NEMISIS["evidence"]
    checked_in = evidence.read_text(encoding="utf-8")
    stamp = next(line.split(": ", 1)[1] for line in checked_in.splitlines() if line.startswith("# fetched: "))
    produced = nemisis_transcript(checkout, tmp_path / "nemisis", shell_env, stamp)

    if os.environ.get("GUARDRAIL_CHECKUP_REGENERATE_EVIDENCE") == "1":  # pragma: no cover - a maintainer's switch
        evidence.write_text(produced, encoding="utf-8")
        pytest.skip("regenerated")
    assert produced == checked_in, "\n".join(
        difflib.unified_diff(checked_in.splitlines(), produced.splitlines(), "checked in", "this build", lineterm="")
    )
    # And the run left the checkout exactly as it found it.
    after = subprocess.run(
        ["git", "-C", str(checkout), "status", "--porcelain"], capture_output=True, text=True, check=False
    )
    assert after.stdout == "", after.stdout
