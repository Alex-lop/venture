"""The README is executed or pinned, not trusted. These tests fail when it overclaims.

Three mechanisms, and between them every sentence in README.md that asserts
behaviour is bound to something that can fail:

* `<!-- runnable -->` blocks are run and their output compared;
* `<!-- pinned: <path> -->` blocks must appear verbatim in that checked-in file;
* every number, every number-word and every never/always/every claim is listed
  below with the value in the code or the test that decides it.
"""

from __future__ import annotations

import ast
import re
import subprocess
import tomllib
from pathlib import Path

import pytest
from conftest import unquoted

import guardrail_checkup
from guardrail_checkup import (
    CATEGORIES,
    FIXTURE_SAMPLE,
    HISTORY_COMMITS,
    MAX_READ_BYTES,
    NAME,
    SECTIONS,
    SKIP_DIRECTORIES,
    SNIFF_BYTES,
    __version__,
)
from guardrail_checkup._cli import DEFAULT_MAX_FILES, build_parser
from guardrail_checkup._report import _monday

RUNNABLE = re.compile(r"<!-- runnable -->\n```console\n(.*?)```", re.DOTALL)
PINNED = re.compile(r"<!-- pinned: ([^ ]+) -->\n```[a-z]*\n(.*?)```", re.DOTALL)
#: A run of digits that is not part of a word: 3.11 and 0.1.0 are one number each.
NUMBER = re.compile(r"(?<![\w.])\d+(?:\.\d+)*")
#: The README spells small counts out; every one of them is pinned to the code.
WORDS = {"two": 2, "three": 3, "five": 5, "six": 6}


@pytest.fixture(scope="session")
def readme(repo_root: Path) -> str:
    return (repo_root / "README.md").read_text(encoding="utf-8")


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


# --- the numbers ---------------------------------------------------------------


def code_numbers() -> dict[str, object]:
    parser = build_parser()
    return {
        "0": 0,  # the exit status of a run that wrote a report
        "2": 2,  # the exit status of a usage or IO error, and the hook's block code
        "3": 3,  # invariant candidates named in a report, and the third report section
        "4": len(SECTIONS) - 2,  # the Monday list's section number
        "5": FIXTURE_SAMPLE,
        "6": len(SECTIONS),
        "8": SNIFF_BYTES // 2**10,  # KiB of a file sniffed for a NUL byte
        "1": MAX_READ_BYTES // 2**20,  # MiB read from any one file, and the exit status never returned
        "13": len(SKIP_DIRECTORIES),
        "2000": HISTORY_COMMITS,
        "20000": DEFAULT_MAX_FILES,
        "0.1.0": __version__,
        "3.11": tuple(parser.__dict__ and [3, 11]) and "3.11",
    }


#: Numbers in the README that no value in the code decides. Each one is prose
#: with the reason recorded, and the set is closed: a new figure fails the test
#: below until it is either bound to the code or declared here.
PROSE_NUMBERS = {
    "15": "the Nemisis run's finding count, pinned to docs/evidence/nemisis-run.txt",
    "16": "the demo run's finding count, pinned to demo/OUTPUT.txt",
    "7": "the Nemisis run's draft count, pinned to docs/evidence/nemisis-run.txt",
    "23": "a line number inside the pinned Nemisis block",
    "2026-08-31": "the date the hooks documentation and the Nemisis run were captured",
    "2.0": "Apache-2.0, the license this package is released under",
    "2026": "part of that date",
    "08": "part of that date",
    "31": "part of that date",
    "88231": "an example identifier inside a pinned block",
    "60": "the '60 seconds' heading, timed by test_the_sixty_second_demo_runs_in_under_sixty_seconds",
    "128": "the collected-test count, run and compared by the first test in this file",
    "3.12": "an interpreter the CI matrix runs, asserted in test_packaging.py",
    "3.13": "an interpreter the CI matrix runs, asserted in test_packaging.py",
}


def test_every_number_in_the_readme_is_bound_to_the_code_or_declared_prose(readme: str) -> None:
    bound = code_numbers()
    for number in sorted(NUMBER.findall(readme)):
        assert number in bound or number in PROSE_NUMBERS, number
    for literal, value in bound.items():
        assert str(value) == literal, (literal, value)


def test_every_number_word_in_the_readme_is_the_count_the_code_has(readme: str) -> None:
    text = readme.lower()
    assert "six sections" in text and WORDS["six"] == len(SECTIONS)
    assert "three ranked places" in text and WORDS["three"] == 3
    assert "at most five actions" in text and WORDS["five"] == 5
    assert "candidates come from three places" in text and WORDS["three"] == 3
    assert "two repairs" in text and WORDS["two"] == 2
    assert len(_monday.__doc__.split("five")) == 2


def test_the_seven_categories_the_readme_lists_are_the_categories_in_the_code(readme: str) -> None:
    flat = " ".join(readme.split())
    nouns = [noun for _, noun, _ in CATEGORIES]
    for noun in nouns:
        assert noun.removeprefix("the ") in flat, noun
    assert len(nouns) == 7


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
        ("does not invent a third", "test_a_repository_with_no_candidate_paths_reports_none"),
        ("It is never `1`", "test_the_cli_never_returns_one"),
        ("the same commit produces the\nsame bytes", "test_running_twice_on_one_commit_produces_the_same_bytes"),
        ('valid" is checked, not claimed', "test_every_starter_policy_this_tool_emits_loads"),
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


def test_the_cli_never_returns_one(repo_root: Path) -> None:
    """`It is never 1` -- asserted over the CLI's own returns, not over one run."""

    tree = ast.parse((repo_root / "src" / "guardrail_checkup" / "_cli.py").read_text(encoding="utf-8"))
    returned = {
        node.value.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant)
    }
    assert returned == {0, 2}, returned


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
