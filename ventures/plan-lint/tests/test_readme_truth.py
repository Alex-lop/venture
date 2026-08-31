"""The README may not outrun the code.

Every code the README lists, every command it shows, every number it prints and
every capability it disclaims is checked against the package here. A claim that
cannot be backed is deleted from the README, not softened.

The tests above the sweep pin the claims these pages make today. The sweep at the
bottom is what makes a *new* claim expensive: every number in the prose of
README.md, CHANGELOG.md and docs/porting-notes.md, every `##` section of the
README and every bullet of its disclaimer list has to be accounted for -- either
produced by a constant in the package or written into an explicit set a reviewer
had to edit. A sentence nobody accounted for fails the suite.
"""

from __future__ import annotations

import functools
import inspect
import os
import re
import subprocess
import sys
import tomllib
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

import agent_plan_lint
from agent_plan_lint import ISSUE_CODES

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
CHANGELOG = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
SOURCE = {path.name: path.read_text(encoding="utf-8") for path in (ROOT / "src" / "agent_plan_lint").glob("*.py")}


def section(title: str) -> str:
    match = re.search(rf"^## {re.escape(title)}$(.*?)(?=^## |\Z)", README, re.M | re.S)
    assert match is not None, f"README has no '## {title}' section"
    return match.group(1)


def normalize(text: str) -> str:
    return "\n".join(" ".join(line.split()) for line in text.strip().splitlines())


@pytest.fixture(scope="module")
def console_environment(tmp_path_factory) -> dict[str, str]:
    """A PATH where `agent-plan-lint` is this checkout and `python` is this interpreter."""

    directory = tmp_path_factory.mktemp("bin")
    shim = directory / "agent-plan-lint"
    shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" -m agent_plan_lint.cli "$@"\n')
    shim.chmod(0o755)
    return {
        "PATH": os.pathsep.join([str(directory), str(Path(sys.executable).parent), "/usr/bin", "/bin"]),
        "HOME": os.environ.get("HOME", str(directory)),
        "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
        "COLUMNS": "80",
    }


def console_commands() -> list[tuple[str, str]]:
    """Every `$ command` plus its expected output from the README's console blocks."""

    pairs: list[tuple[str, str]] = []
    for block in re.findall(r"^```console$(.*?)^```$", README, re.M | re.S):
        command: str | None = None
        expected: list[str] = []
        for line in block.strip("\n").splitlines():
            if line.startswith("$ "):
                if command is not None:
                    pairs.append((command, "\n".join(expected)))
                command, expected = line[2:], []
            else:
                expected.append(line)
        assert command is not None, "console block without a command"
        pairs.append((command, "\n".join(expected)))
    assert pairs, "README has no runnable console blocks"
    return pairs


@pytest.mark.parametrize(("command", "expected"), console_commands())
def test_every_console_block_prints_what_the_readme_shows(
    command: str, expected: str, console_environment: dict[str, str]
) -> None:
    result = subprocess.run(
        ["sh", "-c", command],
        cwd=ROOT,
        env=console_environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert normalize(result.stdout) == normalize(expected), result.stderr


def test_the_readme_lists_exactly_the_codes_the_validator_can_emit() -> None:
    listed = set(re.findall(r"`([a-z][a-z0-9_]*)`", section("What it catches")))

    assert listed == set(ISSUE_CODES)
    assert f"{len(ISSUE_CODES)} typed issue codes" in CHANGELOG


#: The left-hand column of the "What it catches" table: what each row says goes
#: wrong. The right-hand column is pinned to `ISSUE_CODES` above, which cannot
#: see a cell rewritten into a capability the package does not have.
CATCHES_ROWS = (
    "The task graph is not a DAG",
    "Two tasks write the same path — the assembly excepted, over the outputs it merges",
    "A task steps outside the policy's paths",
    "The plan spends more than the policy grants",
    "A task uses a command or role the policy never granted",
    "A success criterion proves nothing",
    "Artifacts between tasks do not line up",
    "The merge and verification stages are not a shape a runtime can execute",
    "A task is not in the state a fresh plan starts in",
)


def test_the_catches_table_says_what_a_reviewer_listed_and_nothing_else() -> None:
    """A row rewritten into a claim -- "every scope is auto-narrowed" -- fails here."""

    rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in section("What it catches").splitlines()
        if line.startswith("|")
    ]
    body = [row for row in rows if row[0] not in {"What goes wrong"} and set("".join(row)) - set("-: ")]

    assert tuple(row[0] for row in body) == CATCHES_ROWS
    assert {code for row in body for code in re.findall(r"`([a-z_]+)`", row[1])} == set(ISSUE_CODES)


#: The first sentence of every top-level bullet of the changelog's release
#: section. A fabricated capability -- "Plans are cached between runs" -- is a
#: new bullet, and a new bullet is a reviewer edit here.
CHANGELOG_BULLETS = (
    "`validate_plan`, `require_valid_plan` and `evaluate_plan_policy`: the plan admission gate extracted from"
    " [Graphene](https://github.com/Alex-lop/Graphene), with 36 typed issue codes covering dependency cycles,"
    " out-of-scope reads and writes, parallel write-path conflicts, unverifiable or self-asserted success criteria,"
    " artifact contracts and attempt budgets.",
    "`load_plan` / `load_policy`: JSON documents natively, YAML through the optional `yaml` extra. A document that"
    " cannot be read is a refusal naming the reason and never a traceback -- neither parse branch names the"
    " exception types it has to predict, so a failure inside a tag constructor is a refusal like any other -- and"
    " never the document's own text: a YAML"
    " parse failure reports the problem with its line and column, not the source line PyYAML quotes, which would"
    " copy a credential straight into the log. Those reasons include duplicate keys, a non-string mapping key, YAML"
    " anchors and aliases, CPython's non-JSON `NaN` and `Infinity`, a number the interpreter itself will not"
    " convert, nesting deeper than the parser's stack, anything that is not a regular file, and anything over"
    " `MAX_DOCUMENT_BYTES`.",
    "`agent-plan-lint check|codes|schema` command line, exiting 0 within policy, 1 with issues, 2 on a document"
    " that cannot be loaded or the command line is wrong. `--format json` prints JSON on exit 0, on exit 1 and on a"
    " load failure's exit 2; a usage error is argparse's own message on stderr and the safety net below is one line"
    " there, and neither is JSON. An unexpected failure inside the tool is that same exit 2 and one line on stderr"
    " rather than a traceback and exit 1, which would have told a CI gate the plan was merely out of policy. `python"
    " -m agent_plan_lint` is the same entry point as the console script, so both go through that one safety net.",
    "`agent_plan_lint.globs.full_match`, a `PurePosixPath.full_match` equivalent for the canonical patterns a"
    " document can contain -- no empty component, at most 16 of them -- used on every supported version, checked"
    " against the standard library's behaviour on 3.13. An empty component and a pattern past the bound are the two"
    " documented divergences, and a document carrying either is refused when it loads.",
    "No path component may end in a dot or a space. Windows strips both, so `app/token.env.` and `app/token.env`"
    " are one file there while every comparison here would call them two, which turned a trailing dot into an escape"
    " from an exclusion and from the write-conflict check. Both spellings are refused when the document loads.",
    "No path may contain an invisible character. The rule is a Unicode category test rather than `str.isprintable`:"
    " a code point in a path may not be in the C, Z or M general categories -- the ASCII space excepted -- nor in"
    " Unicode's `Default_Ignorable_Code_Point` set, nor the blank Braille cell. `str.isprintable` is only the C and"
    " Z half of that, so it admitted every combining mark in the set, the variation selectors included; a read scope"
    " or a write lease carrying one renders character for character like the path without it -- so it walked past an"
    " exclusion on that subtree, and two tasks leasing the two spellings of `app/api.py` were two leases rather than"
    " one conflict. The zero-width joiners stay legal in a `title`, a `contract` and a `blocker`, where they are"
    " orthography rather than a file name, and the command line escapes the same set on the way out. What the M half"
    " costs is the decomposed spelling of an accented path name, and a path in a script whose vowel signs are"
    " separate code points.",
    "Exclusions, write leases, lease overlaps and published outputs compare through one case-folded,"
    " NFC-normalised key, because macOS and Windows call `app/api.py` and `app/API.py` one file; a policy that"
    " only ever lives on a case-sensitive filesystem sets `case_sensitive_paths: true`. The fold is the"
    " length-preserving one those filesystems perform, so `app/gruß.py` and `app/gruss.py` stay the two files"
    " they are everywhere. The policy's read and write grant globs match the path as the plan spells it, so a"
    " grant written `app/**` does not admit `App/api.py` -- the write is refused as `write_path_not_allowed`,"
    " not folded into the grant.",
    "A policy exclusion binds wildcard read scopes: a scope that could reach an excluded path is refused rather"
    " than granted with a hole in it, because nothing downstream of this gate enforces the hole. `docs/schema.md`"
    " says what a task writes instead.",
    "Text a plan publishes -- a task's `title`, `contract` or `blocker`, a criterion's `description` -- is refused"
    " when it carries a credential *shape*, and the refusal names the field and the shape without echoing the value."
    " Prose about secrets is not a shape, and neither is a name: a run of characters is broken by `/`, by `_` and by"
    " `-` before its entropy is measured, so a branch name, a source path, an ADR filename, a release tag and a"
    " snake_case migration name are short words rather than one long token, and the security tickets this tool's"
    " users write still load. A value assigned after `secret`, `token`, `password` or `api_key` is measured the same"
    " way: it is a credential when it carries a provider key prefix or a PEM header, or when it runs to 32"
    " characters or more mixing case and carrying at least 3 digits, and a shorter one is the *name* of a secret"
    " rather than a secret -- so `secret = AWS_SECRET_ACCESS_KEY_V2` and `SECRET_KEY=change-me-in-prod` both load.",
    "Bounds that keep a document inside `MAX_DOCUMENT_BYTES` bounded in work as well as in bytes: at most 16"
    " slash-separated segments in a path or a pattern, at most 64 globs in each of a policy's three path lists, at"
    " most 32 distinct wildcard path components across a whole policy, and at most 2048 paths named by one plan."
    " Crossing any of them is a refusal that says which. The report is bounded too, at 32 findings per issue code,"
    " and one contested write path is one finding naming every task racing for it. `tests/test_performance.py`"
    " builds the worst document those bounds allow and pins it to a two-second budget.",
    "Supported on CPython 3.11, 3.12 and 3.13. One runtime dependency, `pydantic>=2.7`.",
)


def changelog_bullets() -> tuple[str, ...]:
    body = re.search(r"^## [\d.]+ - \S+$(.*)", CHANGELOG, re.M | re.S)

    assert body is not None
    return tuple(
        " ".join(CLAIM_MARKER.sub("", bullet).split())
        for bullet in re.findall(r"^- (.+?)(?=\n- |\n\n|\Z)", body.group(1), re.M | re.S)
    )


def test_every_changelog_bullet_is_one_a_reviewer_listed() -> None:
    """A capability nobody shipped is a bullet nobody listed."""

    assert changelog_bullets() == CHANGELOG_BULLETS


def test_a_sentence_appended_to_a_pinned_bullet_fails_the_pin() -> None:
    """The pins are whole bullets, so a second sentence is not free text.

    Pinning `bullet.split(". ")[0]` left everything after the first sentence
    unchecked: "Windows wheels are published with each release." appended to the
    CPython-support bullet, and "It reports the minimal edit that would make the
    plan valid." appended to the `--fix` disclaimer, both shipped green.
    """

    for pinned, bullets in ((DISCLAIMERS, disclaimer_bullets()), (CHANGELOG_BULLETS, changelog_bullets())):
        assert bullets == pinned
        assert any(". " in bullet for bullet in pinned), "nothing here has a second sentence to protect"
        appended = (pinned[0] + " Windows wheels are published with each release.", *pinned[1:])
        assert appended != pinned


def test_the_readme_version_is_the_packaged_version() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]

    assert agent_plan_lint.__version__ == version
    assert f"agent-plan-lint {version}" in README
    assert pyproject["project"]["dependencies"] == ["pydantic>=2.7"]
    assert "The only runtime dependency is `pydantic>=2.7`" in README
    assert "One runtime dependency, `pydantic>=2.7`" in CHANGELOG
    heading = re.search(r"^## ([\d.]+) - (\S+)$", CHANGELOG, re.M)
    assert heading is not None, "the changelog has no `## <version> - <status>` heading"
    assert heading.group(1) == version
    assert heading.group(2) == "unreleased" or date.fromisoformat(heading.group(2)) <= datetime.now(UTC).date()


#: Every bullet of the disclaimer list, whole. Reversing one into a capability
#: claim ("It rewrites and repairs a plan with `--fix`"), adding a new one, or
#: appending a second sentence to an existing one ("It reports the minimal edit
#: that would make the plan valid.") all fail here, which is the half extracting
#: `--flag` tokens cannot see.
DISCLAIMERS = (
    "It does not execute, spawn, or sandbox anything. There is no subprocess in the package.",
    "It does not open a socket. There is no network client in the package.",
    "It does not read the files your plan names — only the plan and policy documents you point it at.",
    "It does not rewrite or repair a plan. There is no `--fix`.",
    "It does not watch a directory or run as a daemon. There is no `--watch`.",
    "It has no plugin system and no config file. There is no `--config`; the policy document is the configuration.",
    "It does not carve a hole in a scope. A wildcard read scope that could reach an excluded path is refused rather"
    ' than narrowed, because nothing downstream of this gate enforces the hole — so `exclusions: ["app/secrets/**"]`'
    ' refuses `read_paths: ["app/**"]`, and a task asks for `app/src/**` instead.',
    "It does not accept an unbounded document. A path or a glob may be 16 segments deep, a policy may list 64 globs"
    " in each of its three path lists and spend 32 distinct wildcard path components, a plan may name 2048 paths,"
    " and a document may be 1 MiB; `docs/schema.md` has the table and every refusal names the bound it crossed.",
    "It does not enforce anything. The verdict is an exit status and a report; what stops a run is the hook, the CI"
    " job or the person that reads it.",
    "It does not know whether the work is a good idea. It checks the plan against the policy, nothing else.",
)


def disclaimer_bullets() -> tuple[str, ...]:
    section_text = section("What it does not do").strip()
    return tuple(
        " ".join(CLAIM_MARKER.sub("", bullet).split())
        for bullet in re.findall(r"^- (.+?)(?=\n- |\Z)", section_text, re.M | re.S)
    )


def test_every_bullet_of_the_disclaimer_list_still_disclaims_something() -> None:
    """A bullet that stopped starting with "It does not" stopped being a disclaimer."""

    bullets = disclaimer_bullets()

    assert bullets == DISCLAIMERS
    for bullet in bullets:
        assert re.match(r"It (does not|has no) ", bullet), bullet


def test_the_disclaimed_flags_do_not_exist() -> None:
    disclaimed = set(re.findall(r"`(--[a-z-]+)`", section("What it does not do")))
    help_text = subprocess.run(
        [sys.executable, "-m", "agent_plan_lint.cli", "check", "--help"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout

    assert disclaimed >= {"--fix", "--watch", "--config"}
    assert not [flag for flag in disclaimed if flag in help_text]


def test_the_package_never_executes_anything_or_opens_a_socket() -> None:
    forbidden = ("subprocess", "socket", "urllib", "http.client", "requests", "httpx", "os.system")
    offenders = {
        name: word
        for name, text in SOURCE.items()
        for word in forbidden
        if re.search(rf"^\s*(?:import|from) {re.escape(word)}\b", text, re.M)
    }

    assert offenders == {}
    for sentence in (
        "It does not execute, spawn, or sandbox anything.",
        "It does not open a socket.",
        "There is no subprocess in the package.",
        "There is no network client in the package.",
        "There is no `--fix`.",
        "There is no `--watch`.",
        "There is no `--config`; the policy document is the configuration.",
    ):
        assert sentence in section("What it does not do"), sentence


def test_the_validator_never_touches_the_filesystem() -> None:
    imports = re.findall(r"^(?:import|from) (\S+)", SOURCE["validation.py"], re.M)

    assert set(imports) == {"__future__", "collections.abc", "unicodedata", "types", "pydantic", ".globs", ".models"}
    assert "only the plan and policy documents you point it at" in README


def test_the_readme_test_commands_are_the_commands_ci_runs() -> None:
    check_script = (ROOT / "scripts" / "check.sh").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    for claim in ("scripts/check.sh", ".github/workflows/ci.yml"):
        assert claim in section("How it is tested")
    for step in ("ruff check", "ruff format --check", "pytest", "uv build", "uv lock --check"):
        assert step in check_script, step
        assert step in workflow, step
    for version in ("3.11", "3.12", "3.13"):
        assert version in workflow
        assert version in section("How it is tested")
    for system, spelling in (("ubuntu", "Ubuntu"), ("macos", "macOS")):
        assert system in workflow, system
        assert spelling in section("How it is tested"), spelling


def test_the_check_script_passes_an_interpreter_to_every_uv_run() -> None:
    """`.python-version` wins otherwise, so an unpinned `uv run` is a second 3.11 run.

    `CONTRIBUTING.md` tells a contributor to pass `--python` on every `uv run`;
    the script it points at has to do the same, on the wheel step as well as on
    the test step, or "on 3.11, 3.12 and 3.13" is only true of `pytest`.
    """

    script = (ROOT / "scripts" / "check.sh").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    # ruff is excluded: a linter's answer does not depend on the interpreter, so
    # the script runs it once and the CI matrix runs it on all three anyway.
    unpinned = [
        line
        for line in script.splitlines()
        if re.search(r"^\s*(?:uv run|uv venv)\b", line) and "--python" not in line and "ruff" not in line
    ]

    assert unpinned == [], unpinned
    assert (ROOT / ".python-version").read_text(encoding="utf-8").strip() == matrix_python_versions()[0]
    assert "pass `--python` on **every** `uv run`" in " ".join(contributing.split())


def test_the_contributing_check_script_claim_is_what_the_script_runs() -> None:
    """CONTRIBUTING ships in the sdist, so its one factual paragraph is swept too."""

    script = (ROOT / "scripts" / "check.sh").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    flat = " ".join((ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8").split())

    assert "`scripts/check.sh` runs the same steps locally" in flat
    # Both directions. Asserting only that the reviewer's list appears in the
    # prose let a *sixth* step -- `mypy --strict`, which nothing runs -- be added
    # to the paragraph and ship green.
    sentence = flat.split("runs the same steps locally:")[1].split("Please make it pass")[0]
    listed = set(re.findall(r"`([^`]+)`", sentence))
    for step in ("uv lock --check", "ruff check", "ruff format --check", "pytest", "uv build"):
        assert step in script, step
    assert listed == {"uv lock --check", "ruff check", "ruff format --check", "pytest", "uv build"}
    for version in matrix_python_versions():
        assert script.count(version) >= 2, version
        assert version in flat
    # The two things CI adds and the script cannot: the other platform, and the
    # second job. Both are named rather than implied.
    assert "on Ubuntu and macOS" in flat
    assert "adds a second job that runs the doc-truth tests" in flat
    assert "runs-on: ubuntu-latest" in workflow
    assert workflow.count("- uses: actions/checkout@v4") == 2


def test_the_install_lines_are_the_two_the_metadata_supports() -> None:
    """The README offers exactly two installs, and neither can drift off the metadata."""

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    urls = project["urls"]
    commands = re.findall(r"^(?:pip|uv pip|pipx|python -m pip|poetry|conda) [^\n`]+$", README, re.M)

    assert commands == [f"pip install {project['name']}", f"uv pip install git+{urls['Source']}"]
    for url in urls.values():
        assert url.startswith(urls["Source"]), url


def test_the_optional_extra_sentence_is_the_extra_the_metadata_declares() -> None:
    """The runtime dependency is asserted against pyproject; so is the optional one."""

    extras = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["optional-dependencies"]

    assert set(extras) == {"yaml"}
    assert extras["yaml"] == ["PyYAML>=6"]
    assert f"YAML plans need the optional `{next(iter(extras))}` extra; JSON needs nothing." in " ".join(README.split())


def test_the_exclusion_example_in_the_disclaimer_list_is_what_the_validator_decides() -> None:
    """The one bullet that states a decision rather than an absence, so it is run."""

    from agent_plan_lint import validate_plan
    from conftest import plan as _plan
    from conftest import policy as _policy
    from conftest import replace

    flat = " ".join(section("What it does not do").split())
    schema = " ".join((ROOT / "docs" / "schema.md").read_text(encoding="utf-8").split())
    assert 'so `exclusions: ["app/secrets/**"]` refuses `read_paths: ["app/**"]`' in flat
    assert "a task asks for `app/src/**` instead" in flat
    # The same rule is stated normatively on the schema page, in its own words.
    # The README bullet was the only spelling this ran, so the page's could be
    # rewritten into the opposite claim and stay green.
    assert (
        "**A wildcard read scope that could reach an exclusion is refused**, not granted with a hole in it:"
        ' nothing downstream of this gate enforces the hole, so `exclusions: ["app/secrets/**"]` refuses'
        ' `read_paths: ["app/**"]`, `["app/*"]` and `["app/secr*/**"]` alike'
    ) in schema
    assert "narrowing the scope past the excluded directory is what a task writes instead" in schema

    policy = _policy().model_copy(update={"exclusions": ("app/secrets/**",)})
    narrowed = validate_plan(policy, replace(_plan(), "work-a", read_paths=("app/src/**",)))

    for scope in ("app/**", "app/*", "app/secr*/**"):
        refused = validate_plan(policy, replace(_plan(), "work-a", read_paths=(scope,)))
        assert "read_path_not_allowed" in {issue.code for issue in refused.issues}, scope
    assert "read_path_not_allowed" not in {issue.code for issue in narrowed.issues}


def test_the_documented_test_counts_are_the_counts_pytest_reports() -> None:
    """The README and the porting notes both restate run counts; both are pinned here."""

    porting = (ROOT / "docs" / "porting-notes.md").read_text(encoding="utf-8")
    collected, gated = _collected_counts()

    assert f"{collected} passed on 3.13 and {collected - gated} passed, {gated} skipped" in porting
    assert f"those runs report {gated} skips" in README


def _collect(*arguments: str) -> list[str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return [line for line in result.stdout.splitlines() if "::" in line]


@functools.lru_cache(maxsize=1)
def _collected_counts() -> tuple[int, int]:
    """How many tests the suite collects, and how many of those only run on 3.13."""

    source = (ROOT / "tests" / "test_globs.py").read_text(encoding="utf-8")
    names = re.findall(r"skipif\(sys\.version_info < \(3, 13\).*?\ndef (\w+)", source, re.S)
    gated = [line for line in _collect("tests/test_globs.py") if any(f"::{name}" in line for name in names)]

    assert names and gated
    return len(_collect()), len(gated)


def test_the_readme_says_how_many_tests_only_run_on_the_newest_python() -> None:
    """The collected count is not the passed count on 3.11 and 3.12, and the README says so."""

    _, gated = _collected_counts()

    assert f"{gated} of them re-derive the glob table from the standard library" in README


def test_the_matcher_claim_states_the_divergence_the_glob_tests_pin() -> None:
    """`full_match` is not the standard library for every pattern, and both pages say which."""

    from agent_plan_lint.globs import MAX_PATH_SEGMENTS, full_match
    from test_globs import DIVERGENCES

    for path, pattern in DIVERGENCES:
        assert full_match(path, pattern) is False, (path, pattern)
    for page in (README, CHANGELOG):
        flat = " ".join(page.split())
        assert "no empty component" in flat
        assert f"at most {MAX_PATH_SEGMENTS} of them" in flat


def test_the_named_files_exist() -> None:
    named = set(re.findall(r"`((?:tests|docs|demo|scripts|\.github)/[\w./-]+)`", README))

    assert named
    for relative in named:
        assert (ROOT / relative).exists(), relative


def test_the_python_example_calls_the_api_the_package_exports() -> None:
    """The one README code block no shell can run still has to name real things."""

    blocks = re.findall(r"^```python$(.*?)^```$", README, re.M | re.S)
    assert len(blocks) == 1
    imported = re.search(r"from agent_plan_lint import (.+)", blocks[0])
    assert imported is not None
    names = [name.strip() for name in imported.group(1).split(",")]

    assert names
    for name in names:
        assert name in agent_plan_lint.__all__, name
    signature = inspect.signature(agent_plan_lint.require_valid_plan)
    assert tuple(signature.parameters) == ("policy", "plan", "strict")
    assert "require_valid_plan(load_policy(" in blocks[0]


def test_the_package_declares_no_plugin_group_the_readme_disclaims() -> None:
    """ "No plugin system" is the strongest line in the disclaimer list, so it is pinned too."""

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]

    assert "It has no plugin system and no config file." in section("What it does not do")
    assert "entry-points" not in project and "entry_points" not in project
    assert set(project["scripts"]) == {"agent-plan-lint"}


def test_the_metadata_claims_no_platform_the_ci_matrix_does_not_run() -> None:
    """`OS Independent` is a distribution claim, and nothing here runs on Windows."""

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert not [item for item in project["classifiers"] if item.startswith("Operating System")]
    assert "windows" not in workflow
    assert "on Ubuntu and macOS" in section("How it is tested")


@functools.lru_cache(maxsize=1)
def matrix_python_versions() -> tuple[str, ...]:
    """The CPython versions CI actually runs, read off the matrix."""

    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    match = re.search(r"^\s*python: \[(.+)\]$", workflow, re.M)

    assert match is not None, "the workflow has no python matrix"
    return tuple(item.strip().strip('"') for item in match.group(1).split(","))


def test_the_metadata_claims_no_python_version_the_ci_matrix_does_not_run() -> None:
    """A supported version is a distribution claim, the same as a supported platform."""

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    matrix = matrix_python_versions()
    classified = {
        item.rsplit(" ", 1)[1]
        for item in project["classifiers"]
        if re.fullmatch(r"Programming Language :: Python :: \d+\.\d+", item)
    }
    lowest = min(matrix, key=lambda version: tuple(int(part) for part in version.split(".")))
    named = ", ".join(matrix[:-1]) + f" and {matrix[-1]}"

    assert classified == set(matrix)
    assert project["requires-python"] == f">={lowest}"
    assert f"run on CPython {named}" in section("How it is tested")
    assert f"Supported on CPython {named}." in CHANGELOG


def test_the_pypi_description_claims_nothing_the_readme_disclaims() -> None:
    """`description` is the one sentence every PyPI visitor reads; it ships in the wheel."""

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    forbidden = (
        "repair",
        "rewrite",
        "fix",
        "execute",
        "spawn",
        "sandbox",
        "watch",
        "daemon",
        "plugin",
        "socket",
        # `enforce` walked through the list above: "...and enforce it at runtime"
        # is a runtime claim in the one sentence every PyPI visitor reads.
        "enforce",
    )
    words = set(re.findall(r"[a-z]+", project["description"].lower()))
    statuses = [item for item in project["classifiers"] if item.startswith("Development Status")]

    for word in forbidden:
        assert word in section("What it does not do").lower(), word
    assert not words & set(forbidden), project["description"]
    assert statuses == ["Development Status :: 4 - Beta"]


def test_the_readme_licence_line_is_the_one_in_the_licence_file() -> None:
    """A copyright line is one of the few README sentences with legal weight."""

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    licence = (ROOT / "LICENSE").read_text(encoding="utf-8")
    stated = re.match(r"^(\S+)\. (Copyright \d{4} .+)\.$", section("License").strip())

    assert stated is not None, section("License")
    assert stated.group(1) == project["license"]
    assert stated.group(2) in licence, stated.group(2)


def test_the_readme_states_the_bounds_the_code_enforces() -> None:
    """The one place the README prints numbers about documents; all five come off the code."""

    from agent_plan_lint.globs import MAX_PATH_SEGMENTS, MAX_POLICY_WILDCARDS
    from agent_plan_lint.loading import MAX_DOCUMENT_BYTES
    from agent_plan_lint.models import MAX_PLAN_PATHS, MAX_POLICY_GLOBS

    flat = " ".join(section("What it does not do").split())

    assert f"may be {MAX_PATH_SEGMENTS} segments deep" in flat
    assert f"list {MAX_POLICY_GLOBS} globs in each of its three path lists" in flat
    assert f"spend {MAX_POLICY_WILDCARDS} distinct wildcard path components" in flat
    assert f"may name {MAX_PLAN_PATHS} paths" in flat
    assert f"may be {MAX_DOCUMENT_BYTES // 1024 // 1024} MiB" in flat


# ---------------------------------------------------------------------------
# The sweep: a claim nobody accounted for fails the suite.
# ---------------------------------------------------------------------------

#: The pages whose prose is swept. docs/schema.md has its own number sweep in
#: tests/test_docs.py, against the bounds it documents.
PROSE_PAGES = ("README.md", "CHANGELOG.md", "CONTRIBUTING.md", "docs/porting-notes.md", "docs/comparison.md")

#: Every page whose prose makes claims, swept for claim sentences.
CLAIM_PAGES = (*PROSE_PAGES, "docs/schema.md")

#: A standalone number in prose, in digits or in words. Fenced blocks are not
#: prose -- they are pinned byte for byte by
#: `test_every_console_block_prints_what_the_readme_shows` -- and neither is a
#: URL. An inline code span *is* swept: "takes `12 ms` on a laptop" is the same
#: fabricated figure as "takes 12 ms on a laptop", and backticks used to buy it
#: for nothing. Words are swept too, because "Five adversarial reviews" is the
#: same claim as "5 adversarial reviews".
WORD_NUMBERS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "thirty": "30",
    "forty": "40",
    "fifty": "50",
    "sixty": "60",
    "seventy": "70",
    "eighty": "80",
    "ninety": "90",
    "hundred": "100",
    "thousand": "1000",
}
NUMBER = re.compile(r"(?<![\w./])(?:\d(?:[\d,]*\d)?(?:\.\d+)*|(?i:" + "|".join(WORD_NUMBERS) + r"))(?![\w-])")


def numbers_in(text: str) -> set[str]:
    """Every number the prose states, with a word spelling read as the number it is."""

    return {WORD_NUMBERS.get(token.lower(), token) for token in NUMBER.findall(text)}


#: Numbers no constant in the package produces. A reviewer has to add one here
#: by hand, which is the point: it cannot arrive attached to a new sentence.
EDITORIAL_NUMBERS = {
    "60": "the '## 60 seconds' heading -- how long that section takes to read",
    "1": "'one' as an English quantifier: one question, one file, one runtime dependency",
    "3": "'three' as an English quantifier: the three path lists a policy has, and the "
    "three interpreters the CI matrix names",
}

#: Every `##` section of the README. A new one is a new page of claims, and the
#: tests above only check the sections named here.
README_SECTIONS = (
    "60 seconds",
    "What it catches",
    "What it does not do",
    "How it is tested",
    "Where it came from",
    "Comparison",
    "License",
)


def prose_of(text: str) -> str:
    """Markdown reduced to the sentences a claim can hide in."""

    text = re.sub(r"^```.*?^```", "", text, flags=re.M | re.S)
    text = re.sub(r"<!-- claim: [^>]*-->", "", text)
    # An ordered-list marker is punctuation, not a claim.
    text = re.sub(r"^\s*\d+\.\s", "", text, flags=re.M)
    # The backticks come off, the content stays: a number inside a code span is
    # a number the page states.
    text = re.sub(r"`+", "", text)
    return re.sub(r"https?://\S+", "", text)


def page_prose(name: str) -> str:
    return prose_of((ROOT / name).read_text(encoding="utf-8"))


@functools.lru_cache(maxsize=1)
def accounted_numbers() -> frozenset[str]:
    """Every number a constant, the metadata or the CI matrix produces."""

    from agent_plan_lint.globs import MAX_PATH_SEGMENTS, MAX_POLICY_WILDCARDS
    from agent_plan_lint.loading import MAX_DOCUMENT_BYTES
    from agent_plan_lint.models import MAX_PLAN_PATHS, MAX_POLICY_GLOBS
    from agent_plan_lint.validation import _DETAIL_LIMIT, _ISSUES_PER_CODE, _LISTING_LIMIT

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    collected, gated = _collected_counts()
    cli = (ROOT / "src" / "agent_plan_lint" / "cli.py").read_text(encoding="utf-8")
    licence = (ROOT / "LICENSE").read_text(encoding="utf-8")
    copyright_line = re.search(r"^\s*(Copyright \d{4} .+)$", licence, re.M)

    assert copyright_line is not None
    numbers = {
        str(len(ISSUE_CODES)),
        str(MAX_PATH_SEGMENTS),
        str(MAX_POLICY_GLOBS),
        str(MAX_POLICY_WILDCARDS),
        str(MAX_PLAN_PATHS),
        str(MAX_DOCUMENT_BYTES // 1024 // 1024),
        str(_DETAIL_LIMIT),
        str(_ISSUES_PER_CODE),
        str(_LISTING_LIMIT),
        str(collected),
        str(collected - gated),
        str(gated),
        str(sys.get_int_max_str_digits()),
        project["version"],
    }
    numbers |= set(matrix_python_versions())
    # The three exit statuses the README documents, read off the CLI.
    numbers |= set(re.findall(r"^\s*return (\d+)", cli, re.M))
    numbers |= numbers_in(" ".join(project["dependencies"]))
    numbers |= numbers_in(project["license"])
    numbers |= numbers_in(copyright_line.group(1))
    return frozenset(numbers | set(EDITORIAL_NUMBERS))


@functools.lru_cache(maxsize=1)
def comparison_numbers() -> frozenset[str]:
    """Every figure `docs/comparison.md` may state: one the manifest recorded, or the tolerance.

    The page's numbers are claims about other people's projects, so each one has
    to be a `figure:` line that `scripts/refresh-comparison.sh` wrote out of a
    page it fetched, a date in that manifest, or the drift tolerance the script
    itself enforces.
    """

    sources = (ROOT / "docs" / "comparison-sources.txt").read_text(encoding="utf-8")
    script = (ROOT / "scripts" / "refresh-comparison.sh").read_text(encoding="utf-8")
    tolerance = re.search(r"max\((\d+), round\(live \* 0\.(\d+)\)\)", script)

    assert tolerance is not None, "the refresh script no longer states a drift tolerance"
    numbers = {number for line in sources.splitlines() for number in numbers_in(line)}
    return frozenset(numbers | {tolerance.group(1), str(int(tolerance.group(2)))})


def extra_accounted(name: str) -> frozenset[str]:
    return comparison_numbers() if name == "docs/comparison.md" else frozenset()


@pytest.mark.parametrize("name", PROSE_PAGES)
def test_no_number_in_the_prose_of_a_page_is_unaccounted_for(name: str) -> None:
    """A number nobody added to the accounted set fails, so an injected claim is not free."""

    unaccounted = sorted(numbers_in(page_prose(name)) - accounted_numbers() - extra_accounted(name))

    assert unaccounted == [], f"{name} states numbers nothing accounts for: {unaccounted}"


@pytest.mark.parametrize(
    "injected",
    (
        "Over 500 downloads a month since release.",
        "Eleven adversarial reviews ran before it was released.",
        "Porting them into Rego takes about four hundred lines.",
        # A backtick is not a licence to state a figure: the sweep reads inside
        # an inline code span, which is where a fabricated latency number and a
        # mutated piece of arithmetic both used to sit for free.
        "Validating the largest legal plan takes `12 ms` on a laptop.",
        "A task may make `retry_limit + 7` attempts.",
    ),
)
def test_the_sweep_would_catch_a_number_that_was_slipped_in(injected: str) -> None:
    """The sweep is the guard, so its own failure mode is pinned rather than assumed."""

    unaccounted = numbers_in(prose_of(injected)) - accounted_numbers() - comparison_numbers()

    assert unaccounted, injected


# ---------------------------------------------------------------------------
# The claim sweep: a sentence that says the package does something names a test.
# ---------------------------------------------------------------------------

#: The verbs and quantifiers that turn a sentence into a claim about the code.
#: `CONTRIBUTING.md` documents the marker convention that answers them.
CLAIM_WORD_LIST = (
    "always",
    "blocks",
    "catches",
    "checks",
    "detects",
    "enforces",
    "ensures",
    "every",
    "guarantees",
    "never",
    "refuses",
    "rejects",
    "reports",
    "ships",
    "supports",
    "validates",
    "verifies",
)
CLAIM_WORDS = re.compile(rf"(?<![\w-])(?i:{'|'.join(CLAIM_WORD_LIST)})(?![\w-])")

#: `<!-- claim: test_a, test_b -->`, inline at the end of a block or on its own
#: line after one. Invisible in rendered Markdown; a reviewer has to write it.
CLAIM_MARKER = re.compile(r"<!--\s*claim:\s*([\w,\s]+?)\s*-->")


def prose_blocks(name: str) -> list[str]:
    """The page split into the units a claim lives in: a paragraph, a list item, a table.

    Headings and fenced blocks are not sentences. A whole table is one unit,
    because a marker cannot go inside a row without becoming a cell.
    """

    text = re.sub(r"^```.*?^```", "", (ROOT / name).read_text(encoding="utf-8"), flags=re.M | re.S)
    blocks: list[list[str]] = []
    kind: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            kind = None
            continue
        starts_item = bool(re.match(r"^\s*(?:[-*]\s|\d+\.\s)", line))
        is_row = stripped.startswith("|")
        wanted = "table" if is_row else ("item" if starts_item else "text")
        if kind is None or starts_item or (wanted == "table") != (kind == "table"):
            if CLAIM_MARKER.fullmatch(stripped) and blocks:
                blocks[-1].append(line)
                kind = None
                continue
            blocks.append([])
            kind = wanted
        blocks[-1].append(line)
    return ["\n".join(block) for block in blocks]


@functools.lru_cache(maxsize=1)
def defined_test_names() -> frozenset[str]:
    return frozenset(
        name
        for path in (ROOT / "tests").glob("test_*.py")
        for name in re.findall(r"^def (test_\w+)", path.read_text(encoding="utf-8"), re.M)
    )


@pytest.mark.parametrize("name", CLAIM_PAGES)
def test_every_block_that_makes_a_claim_names_the_test_that_backs_it(name: str) -> None:
    """A claim sentence with no marker is a claim nobody wrote a test for."""

    unbacked = [
        " ".join(block.split())[:90]
        for block in prose_blocks(name)
        if CLAIM_WORDS.search(CLAIM_MARKER.sub("", block)) and not CLAIM_MARKER.search(block)
    ]

    assert unbacked == [], f"{name} claims without a `<!-- claim: test_... -->` marker: {unbacked}"


def test_every_claim_marker_names_a_test_that_exists() -> None:
    """A marker naming nothing is worse than no marker: it looks backed."""

    named = {
        name.strip()
        for page in CLAIM_PAGES
        for block in prose_blocks(page)
        for group in CLAIM_MARKER.findall(block)
        for name in group.split(",")
        if name.strip()
    }

    assert len(named) >= 20
    assert named <= defined_test_names(), sorted(named - defined_test_names())


def test_the_claim_sweep_would_catch_a_capability_that_was_slipped_in() -> None:
    """The guard's own failure mode, pinned rather than assumed."""

    injected = "It always catches a plan OPA and Cedar both admit."

    assert CLAIM_WORDS.search(injected)
    assert not CLAIM_MARKER.search(injected)


#: The holes in the doc-truth suite, written down because an undocumented hole
#: gets trusted for more than it does. Each was found by injecting a false claim
#: into a copy of the tree and watching the suite stay green. Pinned as a tuple
#: so the honest list cannot quietly shrink, and so closing a hole means deleting
#: its line here in the same commit.
DOC_TRUTH_GAPS = (
    "A claim built from a verb outside the marker list in step 2 above carries no marker and needs no test.",
    "A sentence inside a block that already carries a marker can be rewritten into a different claim and keep it:"
    " a marker has to be present and to name a real test, but nothing decides whether that test exercises the"
    " sentence.",
    "An adoption or usage number that happens to equal a constant the package produces passes the number sweep,"
    " which matches values and not what they count.",
    "A number spelled as a hyphenated compound is read as its last word, so it passes whenever that word's value is"
    " one the sweep already accounts for.",
    "A number inside a fenced code block is not swept; such a block is pinned only where some test runs it and"
    " compares the output.",
    "The wheel's `description` is held against a list of words a reviewer wrote out, rather than against any"
    " capability the package lacks.",
    "The provenance of the port is presence-only: the manifest records that each ported path existed on the fetch"
    " date, not what was in it, so a claim about Graphene's own wording cannot be re-derived offline.",
    "A quoted span shorter than the eight-character floor is collected by neither the offline check nor the refresh"
    " script.",
    "Star counts and dated figures are re-read from the world only by `scripts/refresh-comparison.sh` at release"
    " time; offline, the tests hold the page to the manifest and the manifest to nothing.",
    "The unquoted judgements on `docs/comparison.md` are one person's reading on the fetch date and no script can"
    " re-derive them; the page says so in its opening paragraph.",
)


def test_the_documented_gaps_in_the_doc_truth_suite_are_the_ones_a_reviewer_listed() -> None:
    """`CONTRIBUTING.md` says what the guard misses; that section is itself guarded."""

    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    section_text = re.search(r"^## What the doc-truth suite does not catch$(.*?)(?=^## |\Z)", contributing, re.M | re.S)

    assert section_text is not None, "CONTRIBUTING.md no longer lists what the suite misses"
    bullets = tuple(
        " ".join(CLAIM_MARKER.sub("", bullet).split())
        for bullet in re.findall(r"^- (.+?)(?=\n- |\n\n|\Z)", section_text.group(1), re.M | re.S)
    )

    assert bullets == DOC_TRUTH_GAPS


def test_every_page_that_states_anything_is_a_page_the_sweep_reads() -> None:
    """A page nobody added to the sweep lists is a page of claims nobody checks."""

    pages = {"README.md", "CHANGELOG.md", "CONTRIBUTING.md"} | {
        f"docs/{path.name}" for path in (ROOT / "docs").glob("*.md")
    }

    assert set(CLAIM_PAGES) == pages, sorted(pages ^ set(CLAIM_PAGES))
    assert set(PROSE_PAGES) <= set(CLAIM_PAGES)


def test_the_marker_convention_is_written_down_where_a_contributor_reads_it() -> None:
    """Every word that costs a contributor a marker is named where they read it."""

    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "<!-- claim: " in contributing
    for word in CLAIM_WORD_LIST:
        assert f"*{word}*" in contributing, word


def test_the_readme_has_exactly_the_sections_this_file_checks() -> None:
    """A section nobody listed here is a page of claims nobody checked."""

    assert tuple(re.findall(r"^## (.+)$", README, re.M)) == README_SECTIONS
