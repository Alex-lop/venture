"""The three promises on the tin, asserted against the source itself.

The README says this package opens no socket, calls no model, executes nothing
from the repository it reads, and writes only where you tell it to. Those are
sentences no behavioural test can falsify on its own -- a socket opened on a
path no test takes is still a socket -- so they are checked over the AST of
every shipped module.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from guardrail_checkup import READ_ONLY_GIT, READ_ONLY_GIT_CONFIG

SOURCE = Path(__file__).resolve().parent.parent / "src" / "guardrail_checkup"

#: Anything that could reach the network or a model provider.
FORBIDDEN_IMPORTS = {
    "aiohttp",
    "anthropic",
    "asyncio",
    "http",
    "httpx",
    "openai",
    "requests",
    "socket",
    "ssl",
    "telnetlib",
    "urllib",
    "webbrowser",
}

#: The only module allowed to create a file, and the only function in it.
WRITER = ("_compose.py", "emit")


def modules() -> list[tuple[str, ast.Module]]:
    return [(path.name, ast.parse(path.read_text(encoding="utf-8"))) for path in sorted(SOURCE.glob("*.py"))]


@pytest.mark.parametrize("name,tree", modules(), ids=lambda item: item if isinstance(item, str) else "")
def test_no_shipped_module_imports_anything_that_can_reach_the_network(name: str, tree: ast.Module) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found = {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            found = {(node.module or "").split(".")[0]}
        else:
            continue
        assert not (found & FORBIDDEN_IMPORTS), (name, sorted(found & FORBIDDEN_IMPORTS))


def test_the_only_subprocess_is_git_and_only_read_only_plumbing() -> None:
    """Both subprocess calls in the package build their argv with `_argv`, and only git."""

    calls = []
    for name, tree in modules():
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in ("run", "Popen", "call", "check_output", "system"):
                calls.append((name, node.attr))
    assert sorted(calls) == [("_scan.py", "Popen"), ("_scan.py", "run")], calls
    assert READ_ONLY_GIT == ("ls-files", "rev-parse", "log")
    assert READ_ONLY_GIT_CONFIG == ("core.fsmonitor=false", "core.hooksPath=/dev/null", "core.quotePath=false")
    source = (SOURCE / "_scan.py").read_text(encoding="utf-8")
    assert source.count('"git"') == 1, "every git call goes through _argv"


def test_the_git_wrapper_refuses_a_subcommand_that_is_not_on_the_list(tmp_path: Path) -> None:
    from guardrail_checkup._scan import _git

    with pytest.raises(AssertionError):
        _git(tmp_path, "commit", "-m", "no")


def test_only_the_emit_function_creates_a_file() -> None:
    """`write_text`, `mkdir` and `chmod` appear in exactly one place outside the CLI."""

    writers: list[tuple[str, str, str]] = []
    for name, tree in modules():
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for inner in ast.walk(node):
                if isinstance(inner, ast.Attribute) and inner.attr in ("write_text", "write_bytes", "mkdir", "chmod"):
                    writers.append((name, node.name, inner.attr))
    for name, function, attribute in writers:
        assert (name, function) in ((WRITER[0], WRITER[1]), ("_cli.py", "main")), (name, function, attribute)


def test_nothing_in_the_package_opens_a_file_for_writing() -> None:
    for name, tree in modules():
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
                pytest.fail(f"{name} calls open() directly")


def test_the_package_has_no_prompt_and_no_provider(fixture_repo: Path) -> None:
    blob = "\n".join(path.read_text(encoding="utf-8") for path in sorted(SOURCE.glob("*.py"))).lower()
    for token in ("api_key", "api key", "completion(", "chat.completions", "messages.create", "bearer "):
        assert token not in blob, token


# --- the sdist ships more than the installed package -----------------------------


SCRIPTS = SOURCE.parent.parent / "scripts"

#: An import hook that hides the two siblings, so a partial environment can be
#: reproduced without building one.
BLOCKER = (
    "import sys\n"
    "from importlib.abc import MetaPathFinder\n"
    "class Block(MetaPathFinder):\n"
    "    def find_spec(self, name, path=None, target=None):\n"
    "        if name.split('.')[0] in ('agent_plan_lint', 'egresswall'):\n"
    "            raise ModuleNotFoundError(f'No module named {name!r}', name=name)\n"
    "        return None\n"
    "sys.meta_path.insert(0, Block())\n"
)

#: The one file in this repository that may import a network client. It is not
#: in the wheel, nothing in the package imports it, and it is run by hand;
#: README.md's "no network client in the installed package" is measured against
#: exactly this exception, and the set is closed.
NETWORK_EXCEPTIONS = {"refresh_evidence.py"}


def test_no_script_outside_the_installed_package_reaches_the_network_except_the_documented_one() -> None:
    """`SOURCE.glob("*.py")` never reaches scripts/, and the sdist ships scripts/."""

    fetching = set()
    for path in sorted(SCRIPTS.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        found: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                found |= {(node.module or "").split(".")[0]}
        if found & FORBIDDEN_IMPORTS:
            fetching.add(path.name)
    assert fetching == NETWORK_EXCEPTIONS, fetching


def test_nothing_in_the_installed_package_imports_the_one_script_that_fetches() -> None:
    blob = "\n".join(path.read_text(encoding="utf-8") for path in sorted(SOURCE.glob("*.py")))
    for name in NETWORK_EXCEPTIONS:
        assert name.removesuffix(".py") not in blob, name


def test_importing_the_package_without_its_siblings_still_imports(tmp_path: Path) -> None:
    """The siblings are imported in the function that uses them, not at module scope.

    At module scope a partial environment made `import guardrail_checkup` a
    two-level traceback and the console script exit 1 -- the one status this
    tool promises never to return.
    """

    import subprocess
    import sys

    script = tmp_path / "blocked.py"
    script.write_text(
        BLOCKER + "import guardrail_checkup\n" + "print('imported', guardrail_checkup.__version__)\n",
        encoding="utf-8",
    )
    done = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=120)

    assert done.returncode == 0, done.stderr
    assert done.stdout.startswith("imported ")
    assert "Traceback" not in done.stderr


def test_the_cli_without_its_siblings_is_one_line_and_exit_two(tmp_path: Path) -> None:
    """A bare ModuleNotFoundError does not say what is missing or how to get it."""

    import subprocess
    import sys

    (tmp_path / "repo").mkdir()
    script = tmp_path / "blocked_cli.py"
    script.write_text(
        BLOCKER
        + "from guardrail_checkup._cli import main\n"
        + f"raise SystemExit(main(['run', {str(tmp_path / 'repo')!r}, '--out', {str(tmp_path / 'r.md')!r}]))\n",
        encoding="utf-8",
    )
    done = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=120)

    assert done.returncode == 2, (done.returncode, done.stderr)
    assert "Traceback" not in done.stderr
    assert len(done.stderr.strip().splitlines()) == 1, done.stderr
    assert "agent-plan-lint" in done.stderr and "egresswall" in done.stderr
    assert "pip install guardrail-checkup" in done.stderr
    assert not (tmp_path / "r.md").exists()


# --- nothing reaches the report unescaped ----------------------------------------

#: The functions that make a repository-controlled string safe to interpolate.
#: `md` escapes it as markdown text, `_code` seals it in a code span `visible`
#: has already emptied of control characters, `_bar` protects the table cell,
#: and `shlex.quote` protects a shell line the reader is invited to paste.
ESCAPERS = ("md(", "_code(", "_bar(", "visible(", "shlex.quote(")

#: Every f-string interpolation in the two rendering modules that is *not*
#: wrapped in one of those, and why it is safe anyway. The list is closed: an
#: interpolation with no entry here and no escaper around it fails the test
#: below. `composed.validations` was exactly such an interpolation -- a path out
#: of the checkout, straight into a markdown bullet -- and it shipped because
#: nothing read the renderer for this shape.
UNESCAPED: dict[str, str] = {
    # Counts, constants and the report's own vocabulary.
    "'All ' if len(bare) == len(shown) else ''": "the module's own words",
    "'is' if len(bare) == 1 else 'are'": "the module's own words",
    "'twice' if REGRESSION_WEIGHT == 2 else f'{REGRESSION_WEIGHT} times'": "a constant in this package",
    "CODEOWNERS_BONUS": "a constant in this package",
    "HEURISTIC_BASE": "a constant in this package",
    "HISTORY_COMMITS": "a constant in this package",
    "HISTORY_PATHS": "a constant in this package",
    "MAX_READ_BYTES // 2 ** 20": "a constant in this package",
    "REGRESSION_WEIGHT": "a constant in this package",
    "SIGNATURE_SCAN_BYTES // 2 ** 20": "a constant in this package",
    "SIGNATURE_SCAN_FILES": "a constant in this package",
    "SNIFF_BYTES // 2 ** 10": "a constant in this package",
    "composed.signature_skipped": "an integer this package counted",
    **{f"SECTIONS[{number}]": "a constant in this package" for number in range(6)},
    "candidate.rule": "built in _scan from CATEGORIES, which is a constant in this package",
    "candidate.score": "an integer",
    "candidate.slug": "a slug from CATEGORIES, a constant in this package",
    "claim": "the falsifier list's own claim text, written in this module",
    "count": "an integer",
    "date": "the run date, from SOURCE_DATE_EPOCH or the clock",
    "fence": "a run of backticks this module counted",
    "first.slug": "a slug from CATEGORIES, a constant in this package",
    "governs": "already built out of _code",
    "len(bare)": "an integer",
    "len(composed.already)": "an integer",
    "len(composed.screened)": "an integer",
    "len(composed.unpoliceable)": "an integer",
    "len(composed.unwrapped)": "an integer",
    "len(composed.wrapped)": "an integer",
    "len(result.candidates)": "an integer",
    "len(result.churn)": "an integer",
    "len(result.languages)": "an integer",
    "len(result.files)": "an integer",
    "len(tests)": "an integer",
    "len(validated.issues)": "an integer",
    "len(violations)": "an integer",
    "number": "an integer",
    "pattern": "TEST_PATH's own source, a constant in this package, through shlex.quote",
    "prune": "SKIP_DIRECTORIES, a constant in this package, each name through shlex.quote",
    "total - EXAMPLES": "an integer",
    **{f"NOT_REPLACED[{number}][{half}]": "a constant in this package" for number in range(3) for half in (0, 1)},
    "result.max_files": "an integer off the command line",
    "result.churn_cut": "an integer",
    "result.extensions": "an integer",
    "result.repairs": "an integer",
    "result.total_bytes": "an integer",
    "result.total_files": "an integer",
    "result.total_files - result.max_files": "an integer",
    "total": "an integer",
    "versions['agent-plan-lint']": "an installed distribution's version",
    "versions['egresswall']": "an installed distribution's version",
    "versions['guardrail-checkup']": "this package's own version",
    "key": "the MCP configuration's server key, one of two names servers_of picks between",
    "slug": "a slug from CATEGORIES, a constant in this package",
    # Strings this package built, already escaped where they were built.
    "finding.fact": "built in _scan, where every repository string in it went through md or _code",
    "finding.consequence": "a sentence written in _scan; no repository string reaches it",
    "item": "an evidence line or a Monday action, each built out of md or _code",
    "reason": "one of three sentences written in _compose",
    "error": "a sibling's message for a document it refused; §2 renders that status through md",
    "issue.code": "a sibling's own issue code; §2 renders the line it goes in through _code",
    "issue.detail": "a sibling's own issue detail; §2 renders the line it goes in through _code",
    "where": "the --emit-dir the user typed, or the literal DIR; every use of it is inside _code",
    "relative": "one of LINTER_MANIFESTS, a constant in this package",
    "composed.policy_path": "_cli.POLICY_PLACEHOLDER, a constant in this package",
    "_no_head(result)": "one of two sentences written in this module",
    "result.head": "git's own object name for HEAD, hexadecimal",
    "result.head[:12]": "git's own object name for HEAD, hexadecimal",
    # _compose's own drafts, which are files rather than report prose.
    "item.split('/', 1)[0]": "a path in a drafted policy, which agent-plan-lint's own type validates",
    "prefix.rstrip('/')": "a path in a drafted policy, which agent-plan-lint's own type validates",
    "listed": "a repr of the drafted hook's path tuple, inside a Python source file",
}


@pytest.mark.parametrize("name", ["_report.py", "_compose.py"])
def test_no_f_string_in_the_renderer_interpolates_a_scan_result_unescaped(name: str) -> None:
    """The renderer, read for the shape the audit found rather than for the string it found.

    A path, an MCP server name, a hook matcher, a policy issue's detail: every
    one of them is text the inspected repository wrote, and every one of them
    reaches this report. `md` and `_code` are the two doors; this asserts there
    is no third.
    """

    tree = ast.parse((SOURCE / name).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.JoinedStr):
            continue
        for part in node.values:
            if not isinstance(part, ast.FormattedValue):
                continue
            expression = ast.unparse(part.value)
            if any(escaper in expression for escaper in ESCAPERS):
                continue
            assert expression in UNESCAPED, (name, expression)
