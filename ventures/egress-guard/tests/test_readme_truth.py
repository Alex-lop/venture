"""The README is executed, not trusted. These tests fail when it overclaims."""

from __future__ import annotations

import ast
import dataclasses
import inspect
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
from conftest import flatten, fullwidth, quotations, unquoted

import egresswall
from egresswall import Policy, _cli, check

RUNNABLE = re.compile(r"<!-- runnable -->\n```console\n(.*?)```", re.DOTALL)
TABLE_CODE = re.compile(r"^\| `([A-Z_]+)` \|", re.MULTILINE)
COLLECTED = re.compile(r"(\d+) tests? collected")
#: The README spells small counts out; these are the words it may use. Written
#: out, a count is invisible to the digit regex in tests/test_doc_numbers.py, so
#: every one of them is pinned to the code here instead.
WORDS = {"three": 3, "four": 4, "six": 6, "seven": 7, "nine": 9, "ten": 10, "eleven": 11}
WORDS_BY_COUNT = {count: word for word, count in WORDS.items()}
PER_FILE = re.compile(r"^\S+\.py: (\d+)$", re.MULTILINE)


@pytest.fixture(scope="session")
def readme(repo_root: Path) -> str:
    return (repo_root / "README.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def shell_env(tmp_path_factory, repo_root: Path) -> dict[str, str]:
    """A PATH on which `egresswall` is this checkout, however tests were started."""
    bin_dir = tmp_path_factory.mktemp("bin")
    script = bin_dir / egresswall.NAME
    script.write_text(f'#!/bin/sh\nexec "{sys.executable}" -m egresswall._cli "$@"\n')
    script.chmod(0o755)
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    env["PYTHONPATH"] = str(repo_root / "src")
    return env


def blocks(readme: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for block in RUNNABLE.findall(readme):
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


def normalize(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def test_the_readme_has_runnable_blocks(readme: str) -> None:
    assert len(blocks(readme)) >= 5


def test_every_runnable_readme_command_prints_what_the_readme_shows(
    readme: str, repo_root: Path, shell_env: dict[str, str]
) -> None:
    for command, expected in blocks(readme):
        done = subprocess.run(
            command,
            shell=True,
            cwd=repo_root,
            env=shell_env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert normalize(done.stdout + done.stderr) == normalize(expected), command


def test_the_reason_codes_in_the_readme_are_exactly_the_codes_in_the_code(
    readme: str,
) -> None:
    assert set(TABLE_CODE.findall(readme)) == set(egresswall.VIOLATION_CODES)


def test_every_reason_code_constant_is_exported_and_documented() -> None:
    for code in egresswall.VIOLATION_CODES:
        assert getattr(egresswall, code) == code
        assert egresswall.VIOLATION_CODES[code].strip()


def test_the_readme_detector_count_matches_the_code(readme: str) -> None:
    assert "**It does not recognise names, addresses or free-text PII.** Ten regular" in readme
    assert len(egresswall.DETECTORS) == 10


@pytest.mark.parametrize("flag", ["--redact", "--mask", "--fix", "--http", "--sse", "--url"])
def test_a_documented_non_feature_has_no_cli_flag(flag: str) -> None:
    """The 'What it does not do' list is asserted against the argument parser."""
    parser = _cli.build_parser()
    actions = list(parser._actions)
    for action in parser._subparsers._group_actions:  # type: ignore[union-attr]
        for sub in action.choices.values():  # type: ignore[attr-defined]
            actions.extend(sub._actions)
    assert flag not in {option for item in actions for option in item.option_strings}


def test_the_hook_screens_the_tool_response_and_nothing_else() -> None:
    source = inspect.getsource(_cli._cmd_hook)
    assert "tool_response" in source
    assert "tool_input" not in source


def test_the_readme_version_matches_the_package(readme: str, repo_root: Path) -> None:
    version = egresswall.__version__
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["name"] == egresswall.NAME
    assert f"Status: {version}." in readme
    assert f"## [{version}]" in (repo_root / "CHANGELOG.md").read_text(encoding="utf-8")


#: The two routes a reader may take, and the only two the README may name.
INSTALL = ("pip install egresswall\n", "uv pip install git+https://github.com/Alex-lop/egresswall")
#: Every installer whose invocation would read as an install route on this page.
INSTALLERS = re.compile(r"(?:uv pip|uvx|pipx|conda|poetry|pdm|brew|pip)\s+install[^\n`]*")


def test_the_readme_names_the_two_install_routes_and_no_others(readme: str) -> None:
    """One published name, one source URL: a third route would be one nobody tested.

    Asserted as an equality rather than as a denylist of routes that were once
    true: a `pipx install` block nobody had run could be added under a denylist
    and the suite stayed green.
    """
    found = {match.group(0).strip() for match in INSTALLERS.finditer(readme)}
    assert found == {route.strip() for route in INSTALL}, found
    assert INSTALL[0].strip().endswith(egresswall.NAME)


def test_both_install_routes_name_what_the_packaging_metadata_names(
    readme: str, repo_root: Path
) -> None:
    """Offline, the checkable claim is that the README and pyproject agree.

    `pip install <name>` must be the distribution name hatchling builds, and the
    from-source URL must be the repository `[project.urls]` points at -- so the
    README and the metadata PyPI renders cannot name two different projects.
    """
    project = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert INSTALL[0].split()[-1].strip() == project["name"] == egresswall.NAME
    source = project["urls"]["Source"]
    assert INSTALL[1].endswith(source), (INSTALL[1], source)
    for url in project["urls"].values():
        assert url.startswith(f"https://github.com/Alex-lop/{egresswall.NAME}"), url
        assert "/ventures/" not in url, url
    assert source in readme


def test_the_readme_pathological_input_count_matches_the_suite(
    readme: str, repo_root: Path
) -> None:
    """The count of hostile strings the README claims is the count the suite runs."""
    stated = re.search(r"(\w+) pathological inputs are", flatten(readme))
    assert stated is not None, "the README must state how many pathological inputs it runs"
    tree = ast.parse((repo_root / "tests" / "test_detectors.py").read_text(encoding="utf-8"))
    cases = [
        len(node.decorator_list[0].args[1].elts)
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_pathological_input_does_not_blow_up_the_matcher"
    ]
    assert cases == [WORDS[stated.group(1)]]


def test_the_readme_conversation_length_matches_the_suite(readme: str, repo_root: Path) -> None:
    stated = re.search(r"a (\d+)-call conversation", readme)
    assert stated is not None, "the README must state how long the deadlock test runs"
    source = (repo_root / "tests" / "test_proxy.py").read_text(encoding="utf-8")
    assert f"for index in range({stated.group(1)}):" in source


def test_the_readme_hostile_server_count_matches_the_suite(readme: str, repo_root: Path) -> None:
    """Each hostile server is one test; the README's number is that count."""
    stated = re.search(r"plus (\d+) hand-written hostile servers", flatten(readme))
    assert stated is not None, "the README must state how many hostile servers it is driven by"
    tree = ast.parse((repo_root / "tests" / "test_proxy.py").read_text(encoding="utf-8"))
    servers = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and any(
            isinstance(call, ast.Call) and getattr(call.func, "id", "") == "drive_script"
            for call in ast.walk(node)
        )
    ]
    assert len(servers) == int(stated.group(1))


def test_the_readme_screening_bound_is_the_one_the_suite_measures(
    readme: str, repo_root: Path
) -> None:
    """The stated bound, the stated cap and the stated number of shapes are the suite's."""
    claim = (
        r"the most text a policy allows, max_total_length, (\d+) MiB by default, screens in "
        r"under a second in each of the (\w+) shapes the suite measures"
    )
    stated = re.search(claim, flatten(readme))
    assert stated is not None, "the README must state the payload and the time it is measured at"
    assert int(stated.group(1)) == Policy().max_total_length // 2**20
    source = (repo_root / "tests" / "test_detectors.py").read_text(encoding="utf-8")
    assert "assert elapsed < 1.0" in source
    shapes = re.search(r"^SHAPES = \[(.*?)\]", source, re.MULTILINE | re.DOTALL)
    assert shapes is not None
    named = [item.strip() for item in shapes.group(1).split(",") if item.strip()]
    assert WORDS[stated.group(2)] == len(named), named


def test_the_readme_describes_how_field_names_are_screened(readme: str) -> None:
    """A key is a value: the claim, and the placeholder that keeps it out of the report."""
    assert "Field names are screened as strings too" in flatten(readme)
    found = check({"contacts": {"member-88231@northgate-clinic.test": "vip"}}, Policy())
    assert [item.code for item in found] == [egresswall.RAW_IDENTIFIER]
    assert "`<key#3>`" in readme
    named = check({"a": 1, "b": 2, "c": 3, "member-88231@northgate-clinic.test": 4}, Policy())
    assert named[0].path == "response.<key#3>"


def test_the_readme_says_which_identifiers_need_a_separator(readme: str) -> None:
    assert "Both want a separator, so 123456789 and 6175550142 pass." in flatten(readme)
    only = Policy(forbidden_keys=frozenset(), detectors=frozenset({"ssn", "phone"}))
    assert check({"a": "123456789", "b": "6175550142"}, only) == []
    assert check({"a": "123-45-6789"}, only)


def test_the_readme_does_not_generalise_over_the_projects_it_compares(readme: str) -> None:
    """Guardrails and the Claude Code built-ins do not rewrite; no claim may say they do."""
    flat = flatten(readme)
    assert "The short version is that most of them detect and then rewrite" in flat
    assert "The short version is that they detect and then rewrite" not in flat


def test_the_readme_policy_block_shows_the_real_defaults(readme: str) -> None:
    block = re.search(r"```json\n(\{[^`]*?\"max_string_length\"[^`]*?\})\n```", readme)
    assert block is not None, "the README must show a policy file with the size limits"
    shown = json.loads(block.group(1))
    defaults = Policy()
    assert "Every key the policy has is in that example." in readme
    assert set(shown) == {item.name for item in dataclasses.fields(Policy)}
    for field in ("max_depth", "max_nodes", "max_string_length", "max_total_length"):
        assert shown[field] == getattr(defaults, field), field
    assert f"{defaults.max_depth + 1} levels with `max_depth: {defaults.max_depth}`" in readme
    assert f"a {defaults.max_string_length // 2**20 * 2} MiB string with the " in readme
    assert f"{defaults.max_string_length // 2**20} MiB default" in readme


def test_the_readme_dependency_claims_match_pyproject(readme: str, repo_root: Path) -> None:
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    assert "Zero runtime dependencies" in readme
    assert pyproject["project"]["dependencies"] == []
    assert "two development ones (`pytest`, `ruff`)" in readme
    dev = pyproject["dependency-groups"]["dev"]
    assert {re.split(r"[><=~!\[]", item)[0] for item in dev} == {"pytest", "ruff"}


def test_the_readme_test_matrix_matches_the_ci_workflow(readme: str, repo_root: Path) -> None:
    workflow = (repo_root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    versions = re.findall(r'"(3\.\d+)"', re.search(r"python: \[(.*?)\]", workflow).group(1))
    systems = re.search(r"os: \[(.*?)\]", workflow).group(1).replace(" ", "").split(",")
    stated = re.search(r"on CPython ([^,]+(?:, [^,]+)*) and (3\.\d+), on (\S+) and (\S+)\.", readme)
    assert stated is not None, "the README must state the versions and runners CI uses"
    assert [item.strip() for item in stated.group(1).split(",")] + [stated.group(2)] == versions
    assert [stated.group(3), stated.group(4)] == systems


def test_the_readme_test_count_matches_the_suite(readme: str, repo_root: Path) -> None:
    stated = re.search(r"\*\*(\d+) tests\*\*", readme)
    assert stated is not None, "the README must state a test count"
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=300,
    )
    total = COLLECTED.search(done.stdout)
    counted = (
        int(total.group(1)) if total else sum(int(item) for item in PER_FILE.findall(done.stdout))
    )
    assert counted > 0, done.stdout[-2000:]
    assert int(stated.group(1)) == counted


def ci_steps(repo_root: Path) -> list[str]:
    """Every single-line `- run:` step of ci.yml's test job, interpreter pin removed.

    CI pins an interpreter per matrix entry and the script uses the project's;
    that is the only difference the two are allowed to have. The wheel-install
    step is a `- name:` block with a `run: |` body, so it is not one of these --
    which is exactly what "before it installs the built wheel" means.
    """
    workflow = (repo_root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    job = workflow.split("\n  test:")[1].split("\n  docs-truth:")[0]
    steps = [
        line.strip()[len("- run: ") :]
        for line in job.splitlines()
        if line.strip().startswith("- run: ")
    ]
    return [step.replace(" --python ${{ matrix.python }}", "") for step in steps]


def script_lines(repo_root: Path) -> list[str]:
    script = (repo_root / "scripts" / "check.sh").read_text(encoding="utf-8")
    return [
        line for line in script.splitlines() if line and not line.startswith(("#", "set ", "cd "))
    ]


def test_the_check_script_is_every_step_ci_runs_before_it_installs_the_wheel(
    readme: str, repo_root: Path
) -> None:
    """A subset check stayed green while CI grew a step the script did not have.

    An equality is the only version of this claim that cannot rot: add a step to
    CI, or drop one from the script, and this fails.
    """
    ci = ci_steps(repo_root)
    lines = script_lines(repo_root)
    assert lines == ci, (lines, ci)
    stated = "runs the checks CI runs before it installs the built wheel:"
    assert stated in readme
    block = re.search(re.escape(stated) + r"\n\n```\n(.*?)```", readme, re.DOTALL)
    assert block is not None, "the README must show the block it claims the script runs"
    assert block.group(1).strip().splitlines() == lines


def test_the_demo_script_still_prints_what_output_txt_records(
    repo_root: Path, shell_env: dict[str, str]
) -> None:
    done = subprocess.run(
        ["./demo/demo.sh"],
        cwd=repo_root,
        env=shell_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=180,
    )
    recorded = (repo_root / "demo" / "OUTPUT.txt").read_text(encoding="utf-8")
    assert normalize(done.stdout) == normalize(recorded)


def test_every_quotation_in_the_readme_is_in_the_checked_in_sources(readme: str) -> None:
    """A sentence attributed to a source has to be in the copy of it under docs/evidence/."""
    assert len(quotations(readme)) >= 2
    assert unquoted(readme) == []


#: "It does not keep state, phone home or write files": the network and the
#: filesystem are not in the package at all, and this is what says so.
NO_NETWORK = frozenset({"socket", "ssl", "urllib", "http", "requests", "httpx", "smtplib"})


def test_no_module_in_the_package_can_reach_the_network(repo_root: Path) -> None:
    for source in sorted((repo_root / "src" / egresswall.NAME).glob("*.py")):
        for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names = {alias.name for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {node.module or ""}
            else:
                continue
            found = {name.split(".")[0] for name in names} & NO_NETWORK
            assert not found, f"{source.name} imports {found}"


def test_a_check_run_writes_no_file(tmp_path: Path, shell_env: dict[str, str]) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text('{"contact": "member-88231@northgate-clinic.test"}', encoding="utf-8")
    before = sorted(item.name for item in tmp_path.iterdir())
    done = subprocess.run(
        [egresswall.NAME, "check", "payload.json"],
        cwd=tmp_path,
        env=shell_env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert done.returncode == 1, done.stderr
    assert sorted(item.name for item in tmp_path.iterdir()) == before


def test_the_readme_states_the_suffix_rule_the_code_implements(readme: str) -> None:
    """The rule is 'ends in token once normalized', which refuses pagination cursors."""
    assert "`nextToken` and `pageToken` are refused by default" in readme
    assert Policy().forbids_key("nextToken") and Policy().forbids_key("pageToken")
    assert not Policy(forbidden_key_suffixes=frozenset()).forbids_key("nextToken")


def test_the_readme_states_the_join_token_shapes_the_detector_matches(readme: str) -> None:
    assert "`hmac-sha256:` or `hmac-sha512:` prefix followed by 64 to 128 hex characters" in readme
    only = Policy(forbidden_keys=frozenset(), detectors=frozenset({"join_token"}))
    for token in ("hmac-sha256:" + "ab" * 32, "hmac-sha512:" + "cd" * 64):
        assert check({"v": token}, only), token


def test_the_readme_states_how_denied_paths_are_matched(readme: str) -> None:
    assert "with case and separators removed on both sides" in readme
    policy = Policy(forbidden_keys=frozenset(), denied_field_paths=frozenset({"patient.mrn"}))
    assert check({"Patient": {"MRN": "NG-88231"}}, policy)


def test_the_readme_counts_the_surfaces_the_demo_exercises(readme: str, repo_root: Path) -> None:
    script = (repo_root / "demo" / "demo.sh").read_text(encoding="utf-8")
    words = {3: "three", 4: "four"}
    scenarios = len(re.findall(r'^echo "== \d+\.', script, re.MULTILINE))
    surfaces = sum(f"{egresswall.NAME} {word}" in script for word in ("check", "hook", "proxy"))
    assert (
        f"exercises all {words[surfaces]} surfaces end to end ({words[scenarios]} scenarios)"
        in readme
    )


#: "It does not persist state": nothing in the package may open a store, and the
#: proxy's only state is a dict that dies with the process.
NO_PERSISTENCE = frozenset({"sqlite3", "shelve", "dbm", "pickle", "marshal"})


def test_the_only_state_the_package_keeps_dies_with_the_process(repo_root: Path) -> None:
    source = (repo_root / "src" / egresswall.NAME / "_proxy.py").read_text(encoding="utf-8")
    run_proxy = next(
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name == "run_proxy"
    )
    assert "pending: dict[str, str] = {}" in ast.get_source_segment(source, run_proxy)
    for path in sorted((repo_root / "src" / egresswall.NAME).glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names = {alias.name for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {node.module or ""}
            else:
                continue
            found = {name.split(".")[0] for name in names} & NO_PERSISTENCE
            assert not found, f"{path.name} imports {found}"


# --- fix pass 4: the claims added for what the code now does ------------------


def test_the_readme_report_bounds_are_the_ones_the_cli_enforces(readme: str) -> None:
    """A report is bounded because a path is a name the other side chose."""
    flat = flatten(readme)
    stated = re.search(r"A report lists at most (\d+) violations and (\d+) characters", flat)
    assert stated is not None, "the README must state how much of a report it will print"
    assert int(stated.group(1)) == _cli.MAX_REPORTED
    assert int(stated.group(2)) == _cli.MAX_REPORT_CHARS
    assert "its path and its detail are truncated" in flatten(readme)
    assert "The reason code is never truncated." in flatten(readme)
    share = re.search(r"one violation's share is (\d+) characters", flatten(readme))
    assert share is not None, "the README must state the per-violation share"
    assert int(share.group(1)) == _cli.MAX_VIOLATION_CHARS
    deep = _cli.Violation("FORBIDDEN_KEY", "response." + "a.b.c." * 400, "field name is forbidden")
    listed, _ = _cli._listed([deep] * (_cli.MAX_REPORTED + 5))
    assert len(listed) == _cli.MAX_REPORTED
    assert all(len(str(item)) <= _cli.MAX_VIOLATION_CHARS for item in listed)
    assert sum(len(str(item)) for item in listed) <= _cli.MAX_REPORT_CHARS
    assert listed[0].path.endswith("...")
    wordy = _cli.Violation("DENIED_FIELD_PATH", "response.a", "denied field " + "x" * 900)
    trimmed = _cli._listed([wordy])[0][0]
    assert trimmed.code == "DENIED_FIELD_PATH"
    assert trimmed.detail.endswith("...") and len(str(trimmed)) <= _cli.MAX_VIOLATION_CHARS


def test_the_readme_states_that_a_duplicate_key_is_refused(readme: str) -> None:
    flat = flatten(readme)
    assert "spells the same key twice is refused rather than screened" in flat
    assert "check and hook exit 2; the proxy answers the client with a JSON-RPC parse error" in flat
    with pytest.raises(ValueError, match="duplicate object key"):
        egresswall._core.loads('{"v": "one", "v": "two"}')


def test_the_readme_forbidden_value_bound_is_the_one_the_policy_enforces(readme: str) -> None:
    stated = re.search(r"forbidden_values holds at most (\d+) entries", flatten(readme))
    assert stated is not None, "the README must state the denylist bound"
    assert int(stated.group(1)) == egresswall.MAX_FORBIDDEN_VALUES
    over = frozenset(f"v{index}" for index in range(egresswall.MAX_FORBIDDEN_VALUES + 1))
    with pytest.raises(ValueError, match="forbidden_values holds at most"):
        Policy(forbidden_values=over)


def test_the_readme_says_a_homoglyph_field_name_is_not_the_listed_name(readme: str) -> None:
    """The docstring on _fold used to claim the opposite; the README is the source of truth."""
    flat = flatten(readme)
    assert "it does not fold one script into another" in flat
    assert "spelled with a Cyrillic" in flat
    assert Policy().forbids_key("API_KEY") and Policy().forbids_key(
        "\uff21\uff30\uff29\uff3f\uff2b\uff25\uff39"
    )
    assert not Policy().forbids_key("\u0430pi_key")
    found = check({"\u0430pi_key": "AKIAIOSFODNN7EXAMPLE"}, Policy())
    assert [item.code for item in found] == [egresswall.SECRET_MATERIAL]


def test_the_readme_lists_exactly_the_protocol_names_the_proxy_exempts(readme: str) -> None:
    from egresswall._proxy import PROTOCOL_KEYS

    listed = set(
        re.findall(
            r"`([A-Za-z_][A-Za-z]*)`",
            readme.split("Two sets of field names")[1].split("is exempt, because")[0],
        )
    )
    assert listed == PROTOCOL_KEYS, listed ^ PROTOCOL_KEYS
    for name in PROTOCOL_KEYS:
        assert not Policy(exempt_keys=PROTOCOL_KEYS).forbids_key(name), name
    assert f"Those {WORDS_BY_COUNT[len(PROTOCOL_KEYS)]} names are matched" in readme


def test_the_readme_says_the_protocol_names_are_matched_the_way_forbidden_names_are(
    readme: str,
) -> None:
    """The exemption is by normalized name, not by exact name; the page used to say exact.

    So a data field genuinely called `progress_token` or `next_cursor` is exempt
    too, and the page has to say so or the code has to stop doing it. This is
    the assertion the old test was missing: that the exemption is *not* exact.
    """
    from egresswall._proxy import PROTOCOL_KEYS

    flat = flatten(readme)
    assert "matched the way forbidden names are \u2014 case and separators removed" in flat
    assert "exempt wherever they appear in a server message" in flat
    exempting = Policy(exempt_keys=PROTOCOL_KEYS)
    for spelling in ("progress_token", "PROGRESS-TOKEN", "Progresstoken"):
        assert Policy().forbids_key(spelling), spelling
        assert not exempting.forbids_key(spelling), spelling
    for spelling in ("next_cursor", "M_E_T_A", "Cursor"):
        assert not exempting.forbids_key(spelling), spelling
    # The value under an exempt name is still screened by every rule.
    found = check({"progress_token": "member-88231@northgate-clinic.test"}, exempting)
    assert [item.code for item in found] == [egresswall.RAW_IDENTIFIER]


def test_the_readme_lists_exactly_the_schema_names_the_proxy_exempts(readme: str) -> None:
    from egresswall._core import SCHEMA_KEYS
    from egresswall._proxy import SCHEMA_METHODS

    section = readme.split("And in a ")[1].split("message, the parameter names")[0]
    assert set(re.findall(r"`([a-z/]+)`", section)) == SCHEMA_METHODS
    declared = readme.split("the parameter names declared under ")[1].split(" are exempt")[0]
    assert set(re.findall(r"`(\w+)`", declared)) == SCHEMA_KEYS


def test_the_readme_examples_that_no_other_test_pins_are_true(readme: str, repo_root: Path) -> None:
    """The small specifics a reader will copy: the false positive, the confusables, the bound."""
    phone_only = Policy(forbidden_keys=frozenset(), detectors=frozenset({"phone"}))
    assert "320.451.9977" in readme
    assert check({"v": "320.451.9977"}, phone_only), "the README's phone false positive"
    # Written as escapes: the point is that these are not the ASCII characters.
    confusables = ("member-88231\u2024northgate\uff20clinic.test", "bWVtYmVyQGV4LnRlc3Q=")
    for confusable in confusables:
        assert check({"v": confusable}, Policy(forbidden_keys=frozenset())) == [], confusable
    for point in ("U+2024", "U+FF20", "U+2011"):
        assert f"`{point}`" in readme, point
    source = (repo_root / "tests" / "test_detectors.py").read_text(encoding="utf-8")
    assert "each asserting that matching finishes in under a second" in flatten(readme)
    assert "assert time.monotonic() - started < 1.0" in source


# --- fix pass 5: the page itself, not only the code behind it -----------------

#: Every promise in "What it does not do", exactly as the README spells it, and
#: the test in this file that asserts the code side of it. Each of those tests
#: read the code and never the page, so the list could be inverted into an
#: overclaim -- "It screens tool inputs as well as responses" -- with a green
#: suite. This is the other half of every one of them.
NON_FEATURES = {
    "**It does not redact, mask or rewrite.**": "test_a_documented_non_feature_has_no_cli_flag",
    "**It does not screen tool inputs.**": (
        "test_the_hook_screens_the_tool_response_and_nothing_else"
    ),
    "**It does not recognise names, addresses or free-text PII.**": (
        "test_the_readme_detector_count_matches_the_code"
    ),
    "**It does not speak HTTP or SSE.**": "test_a_documented_non_feature_has_no_cli_flag",
    "**It does not stop a Claude Code tool call.**": (
        "test_the_hook_reports_rather_than_substituting_an_output"
    ),
    "**It does not fold the case of a `forbidden_values` entry.**": (
        "test_the_readme_says_a_forbidden_value_is_matched_literally"
    ),
    "**It does not exempt documented placeholders.**": (
        "test_allow_domains_exempts_exactly_the_listed_domain"
    ),
    "**It does not persist state, phone home or write files.**": (
        "test_no_module_in_the_package_can_reach_the_network"
    ),
    "**It does not defeat obfuscation.**": (
        "test_the_readme_says_a_homoglyph_field_name_is_not_the_listed_name"
    ),
    "**It does not answer every message it refuses.**": (
        "test_an_oversized_line_never_echoes_an_id_the_client_did_not_send"
    ),
    "**It does not screen the server's own stderr.**": (
        "test_the_servers_own_stderr_reaches_the_operator_unscreened"
    ),
    "**It does not fall back to string-only screening for a document it cannot parse.**": (
        "test_a_serialized_document_that_spells_a_field_twice_is_refused"
    ),
}


def test_the_does_not_do_list_is_exactly_these_promises(readme: str, repo_root: Path) -> None:
    """Delete a promise, invert one, or add one nothing backs, and this fails."""
    from test_doc_numbers import suite_test_names

    section = readme.split("## What it does not do")[1].split("\n## ")[0]
    listed = re.findall(r"^- (\*\*.+?\.\*\*)", section, re.MULTILINE)
    assert set(listed) == set(NON_FEATURES), set(listed) ^ set(NON_FEATURES)
    names = suite_test_names(repo_root)
    for sentence, test in NON_FEATURES.items():
        assert test in names, (sentence, test)


def test_the_readme_says_the_proxy_screens_every_server_message(readme: str) -> None:
    """The word "most" and the word "every" are a whole different promise."""
    flat = flatten(readme)
    assert "screens every server message whole before it reaches the client" in flat
    assert "screens most server message" not in flat


def test_the_hook_reports_rather_than_substituting_an_output() -> None:
    """It does not stop a Claude Code tool call: the hook never writes a decision."""
    source = inspect.getsource(_cli._cmd_hook)
    assert "updatedToolOutput" not in source
    assert "hookSpecificOutput" not in source
    assert "PostToolUse" in inspect.getsource(_cli.build_parser)


def test_the_readme_says_a_forbidden_value_is_matched_literally(readme: str) -> None:
    """The one rule with no folding, and the only doc that says so is this bullet."""
    flat = flatten(readme)
    assert "It does not fold the case of a forbidden_values entry." in flat
    policy = Policy(forbidden_values=frozenset({"ACME-INTERNAL-CASE-9931"}), detectors=frozenset())
    assert check({"n": "x ACME-INTERNAL-CASE-9931 y"}, policy)
    assert check({"n": "x acme-internal-case-9931 y"}, policy) == []
    accented = Policy(forbidden_values=frozenset({"café-9931"}), detectors=frozenset())
    assert check({"n": "café-9931"}, accented)
    assert check({"n": "café-9931"}, accented) == []
    # The field-name rules do fold, which is the asymmetry the bullet exists for.
    assert Policy().forbids_key("API-KEY")


def test_the_readme_licence_is_the_one_the_package_ships(readme: str, repo_root: Path) -> None:
    """A licence line nothing checks can be changed to any other licence, and was."""
    project = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    licence = project["license"]
    assert f"{licence}. See [LICENSE](LICENSE)." in readme
    assert licence == "Apache-2.0"
    head = " ".join((repo_root / "LICENSE").read_text(encoding="utf-8").split())
    assert head.startswith("Apache License Version 2.0"), head[:60]
    # A licence for someone else's repository needs evidence this package does
    # not check in, so the page states none.
    where = readme.split("## Where it came from")[1].split("\n## ")[0]
    assert "Apache" not in where and "MIT" not in where, where


# Counts written as words are pinned for every document, not only this one, in
# tests/test_doc_numbers.py: WORD_PINS maps each spelled-out count on a page to
# the code expression that decides it, and the *set* of number-words on the page
# is asserted so a new one cannot arrive unchecked. This file used to hold a
# README-only version of that and it is gone rather than duplicated.


def test_every_fetched_date_in_the_readme_is_the_date_its_evidence_carries(
    readme: str, repo_root: Path
) -> None:
    """The README cites a page by URL and date; the checked-in copy carries both."""
    cited = re.findall(r"\((https?://\S+?), fetched (\d{4}-\d{2}-\d{2})\)", readme)
    assert cited, "the README must cite the page it quotes with a URL and a date"
    sources = {}
    for path in sorted((repo_root / "docs" / "evidence").glob("*.txt")):
        head = path.read_text(encoding="utf-8").splitlines()[:2]
        sources[head[0].split(": ", 1)[1]] = head[1].split(": ", 1)[1]
    for url, date in cited:
        assert url in sources, url
        assert sources[url] == date, (url, date, sources[url])


# --- fix pass 6: the prose a whitelist could not see --------------------------


def test_the_readme_exit_status_is_the_one_the_command_returns(
    readme: str, repo_root: Path, shell_env: dict[str, str]
) -> None:
    """The runnable test compared output and never the status, so the number was free.

    Changing "the exit status is 1" to 0 left the whole doc-truth suite green.
    """
    stated = re.search(
        r"the whole payload is refused and the exit status is (\d+)", flatten(readme)
    )
    assert stated is not None, "the README must state the status a refused payload exits with"
    command = blocks(readme)[0][0]
    done = subprocess.run(
        command,
        shell=True,
        cwd=repo_root,
        env=shell_env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert done.returncode == int(stated.group(1)), command


#: A `--flag` in these documents that belongs to another tool, and whose it is.
FOREIGN_FLAGS = {
    "--check": "uv lock --check and ruff --check",
    "--collect-only": "pytest",
    "--group": "uv sync --group dev",
}
FLAG = re.compile(r"--[a-z][a-z0-9-]*")


@pytest.mark.parametrize("document", ["README.md", "docs/comparison.md", "CHANGELOG.md"])
def test_every_flag_the_docs_name_is_one_the_parser_has(document: str, repo_root: Path) -> None:
    """Inverting "There is no `--redact` flag" left the suite green; this is why not.

    A flag named on either page is either an option the argument parser really
    has, a flag of another tool declared above, or spelled out as one that does
    not exist -- which is a polarity check, not a mention check: inverting "There
    is no `--redact` flag" into "There is a `--redact` flag" has to fail here.
    """
    text = (repo_root / document).read_text(encoding="utf-8")
    parser = _cli.build_parser()
    actions = list(parser._actions)
    for action in parser._subparsers._group_actions:  # type: ignore[union-attr]
        for sub in action.choices.values():  # type: ignore[attr-defined]
            actions.extend(sub._actions)
    real = {option for item in actions for option in item.option_strings}
    for flag in FLAG.findall(text):
        if flag in real or flag in FOREIGN_FLAGS:
            continue
        assert f"no `{flag}` flag" in text, (document, flag)


#: "the `email`, `ssn` and `phone` detectors" and every run like it.
DETECTOR_RUN = re.compile(r"the ((?:`\w+`(?:, | and )?)+) detectors?")


def test_the_detector_names_in_the_readme_are_exactly_the_detectors_in_the_code(
    readme: str,
) -> None:
    """A `passport` detector invented in the table survived the whole doc-truth suite."""
    section = readme.split("## What it catches")[1].split("\n## ")[0]
    named: set[str] = set()
    for run in DETECTOR_RUN.findall(section):
        named |= set(re.findall(r"`(\w+)`", run))
    assert named == set(egresswall.DETECTORS), named ^ set(egresswall.DETECTORS)


def test_the_spec_coverage_claim_is_the_set_of_messages_the_suite_drives(
    readme: str, repo_root: Path
) -> None:
    """The claim said "every"; the suite was three server notifications short."""
    from test_proxy import SERVER_TO_CLIENT, SPEC_MESSAGES

    flat = flatten(readme)
    stated = re.search(
        r"Every server-to-client request and notification the MCP specification defines "
        r"— (\w+) requests and (\w+) notifications — is driven through the proxy",
        flat,
    )
    assert stated is not None, "the README must scope and count what the suite drives"
    driven = {item["method"] for item in SPEC_MESSAGES.values() if "method" in item}
    assert driven == SERVER_TO_CLIENT
    requests = {name for name in driven if not name.startswith("notifications/")}
    assert WORDS[stated.group(1)] == len(requests), requests
    assert WORDS[stated.group(2)] == len(driven) - len(requests)


def test_the_readme_describes_the_serialized_payload_rule_the_code_implements(
    readme: str,
) -> None:
    """The two rules an operator configures did not fire on an MCP content[].text at all."""
    flat = flatten(readme)
    assert "Serialized payloads are unwrapped." in flat
    assert "whose first visible character is { or [ is parsed and screened again" in flat
    policy = Policy(denied_field_paths=frozenset({"patient.mrn"}))
    wrapped = {"content": [{"type": "text", "text": '{"patient": {"mrn": "NG-88231"}}'}]}
    found = check(wrapped, policy)
    assert [item.code for item in found] == [egresswall.DENIED_FIELD_PATH]
    assert found[0].path == "response.content[0].text→patient.mrn"


# --- fix pass 7: the table cells, not only the reason codes in them -----------

#: Reason code -> (the row's right-hand cell verbatim, a payload, the policy).
#: The codes down the left were pinned and the cells beside them were not, so a
#: row could describe a rule the code does not implement -- "matched only when
#: it is the whole string" against a matcher that matches substrings. Every
#: example here is both pinned as text and screened: it has to trip its own row.
CATCH_EXAMPLES: dict[str, tuple[str, object, Policy]] = {
    "RAW_IDENTIFIER": (
        '`"contact": "member-88231@northgate-clinic.test"`',
        {"contact": "member-88231@northgate-clinic.test"},
        Policy(),
    ),
    "JOIN_TOKEN": (
        '`"cohort": "hmac-sha256:abab…"`',
        {"cohort": "hmac-sha256:" + "ab" * 32},
        Policy(),
    ),
    "SECRET_MATERIAL": ('`"AKIAIOSFODNN7EXAMPLE"`', {"v": "AKIAIOSFODNN7EXAMPLE"}, Policy()),
    "FORBIDDEN_KEY": (
        '`{"apiKey": ""}` — the name alone is enough',
        {"apiKey": ""},
        Policy(),
    ),
    "DENIED_FIELD_PATH": (
        '`{"patient": {"mrn": "NG-88231"}}`',
        {"patient": {"mrn": "NG-88231"}},
        Policy(denied_field_paths=frozenset({"patient.mrn"})),
    ),
    "FORBIDDEN_VALUE": (
        '`"escalated per ACME-INTERNAL-CASE-9931"`',
        {"note": "escalated per ACME-INTERNAL-CASE-9931"},
        Policy(forbidden_values=frozenset({"ACME-INTERNAL-CASE-9931"})),
    ),
    "PAYLOAD_TOO_DEEP": ("33 levels with `max_depth: 32`", None, Policy()),
    "PAYLOAD_TOO_LARGE": (
        "a 2 MiB string with the 1 MiB default",
        {"v": "a" * (2 * 2**20)},
        Policy(),
    ),
    "EMBEDDED_DOCUMENT_UNPARSEABLE": (
        '`{"total": 1, "total": 2}` — the same field twice',
        {"t": '{"total": 1, "total": 2}'},
        Policy(),
    ),
}

CATCH_ROW = re.compile(r"^\| `([A-Z_]+)` \| (.+?) \| (.+?) \|$", re.MULTILINE)


def nested(levels: int) -> dict:
    payload: dict = {}
    node = payload
    for _ in range(levels):
        child: dict = {}
        node["k"] = child
        node = child
    return payload


def test_the_what_it_catches_examples_are_pinned_and_trip_their_own_row(readme: str) -> None:
    """Every example in the right-hand column is screened, not just printed."""
    section = readme.split("## What it catches")[1].split("\n## ")[0]
    rows = {code: example for code, _, example in CATCH_ROW.findall(section)}
    assert set(rows) == set(egresswall.VIOLATION_CODES), set(rows) ^ set(egresswall.VIOLATION_CODES)
    assert rows == {code: cell for code, (cell, _, _) in CATCH_EXAMPLES.items()}
    for code, (_, payload, policy) in CATCH_EXAMPLES.items():
        if payload is None:  # the depth row: its example is a shape, not a literal
            depth = Policy().max_depth
            assert f"{depth + 1} levels with `max_depth: {depth}`" in section
            payload = nested(depth + 1)
        assert code in {item.code for item in check(payload, policy)}, code


# --- fix pass 8: the blocks a reader copies, and the cells beside the codes ---


def test_the_python_api_block_imports_only_names_the_package_exports(readme: str) -> None:
    """The API block was printed and never read.

    Adding `redact` to its import line -- the one entry point this package
    promises never to grow -- left the whole doc-truth suite green.
    """
    block = re.search(r"```python\n(.*?)```", readme, re.DOTALL)
    assert block is not None, "the README must show the Python API"
    tree = ast.parse(block.group(1))
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == egresswall.NAME
        for alias in node.names
    }
    assert imported, "the block must import from the package"
    assert imported <= set(egresswall.__all__), imported - set(egresswall.__all__)


def test_the_client_config_block_names_the_console_script_the_wheel_installs(
    readme: str, repo_root: Path
) -> None:
    """`"command": "egresswall-proxy"` in the copy-paste block shipped green."""
    block = re.search(r'```json\n(\{[^`]*?"mcpServers"[^`]*?\})\n```', readme, re.DOTALL)
    assert block is not None, "the README must show an MCP client config"
    server = next(iter(json.loads(block.group(1))["mcpServers"].values()))
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    assert server["command"] == egresswall.NAME
    assert egresswall.NAME in pyproject["project"]["scripts"]
    assert server["args"][0] == "proxy"
    assert "--" in server["args"]


def test_the_hook_config_block_names_the_stage_the_hook_reads(readme: str) -> None:
    """`_cmd_hook` reads `tool_response`, which only a PostToolUse hook is given.

    The block said PostToolUse and nothing tied it to the code, so changing it to
    PreToolUse -- a hook that would screen nothing -- left the suite green.
    """
    block = re.search(r'```json\n(\{\n  "hooks"[^`]*?\})\n```', readme, re.DOTALL)
    assert block is not None, "the README must show a Claude Code hook config"
    hooks = json.loads(block.group(1))["hooks"]
    assert set(hooks) == {"PostToolUse"}, set(hooks)
    command = hooks["PostToolUse"][0]["hooks"][0]["command"]
    assert command.startswith(f"{egresswall.NAME} hook ")
    assert "tool_response" in inspect.getsource(_cli._cmd_hook)


def test_the_what_it_catches_trigger_cells_state_the_rule_the_code_implements(
    readme: str,
) -> None:
    """The middle column was prose nothing read: inverting the FORBIDDEN_KEY cell
    to "with case and separators preserved" left the suite green."""
    section = readme.split("## What it catches")[1].split("\n## ")[0]
    triggers = {code: trigger for code, trigger, _ in CATCH_ROW.findall(section)}
    assert "case and separators removed" in triggers["FORBIDDEN_KEY"]
    assert "case and separators removed on both sides" in triggers["DENIED_FIELD_PATH"]
    # The cells say the rule; these are the rule.
    for spelling in ("apiKey", "api-key", "API_KEY", fullwidth("API_KEY")):
        assert egresswall.FORBIDDEN_KEY in {
            item.code for item in check({spelling: ""}, Policy())
        }, spelling
    denied = Policy(denied_field_paths=frozenset({"patient.mrn"}))
    assert egresswall.DENIED_FIELD_PATH in {
        item.code for item in check({"Patient": {"MRN": "NG-88231"}}, denied)
    }
    assert "first visible character" in triggers["EMBEDDED_DOCUMENT_UNPARSEABLE"]
    assert "refused by default" in triggers["EMBEDDED_DOCUMENT_UNPARSEABLE"]


# --- fix pass 9: the code points the page names are the ones the code strips --


def test_the_readme_names_the_code_points_the_strip_set_covers(readme: str) -> None:
    """The page names six code points by number; each is in the set that decides
    them, and each is one Unicode category C, Z and M does not reach -- which is
    the whole reason the strip set is a property and two literals rather than
    three category letters."""
    import unicodedata

    from egresswall._core import _BLANK_BY_GLYPH, _DEFAULT_IGNORABLE, _document_candidate

    for point in (0x115F, 0x1160, 0x3164, 0xFFA0):
        assert f"U+{point:04X}" in readme
        assert _DEFAULT_IGNORABLE.match(chr(point)), hex(point)
    for point in (0x2800, 0x1D159):
        assert f"U+{point:04X}" in readme
        assert chr(point) in _BLANK_BY_GLYPH, hex(point)
    for point in (0x115F, 0x1160, 0x3164, 0xFFA0, 0x2800, 0x1D159):
        assert unicodedata.category(chr(point))[0] not in "CZM", hex(point)
        assert _document_candidate(chr(point) + '{"a": 1}') == '{"a": 1}', hex(point)
