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
    assert READ_ONLY_GIT_CONFIG == ("core.fsmonitor=false", "core.hooksPath=/dev/null")
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
