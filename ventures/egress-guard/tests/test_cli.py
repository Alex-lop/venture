"""The CLI is the product surface, so it is tested through subprocess."""

from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from egresswall import _cli

CLI = [sys.executable, "-m", "egresswall._cli"]

HOOK_EVENT = {
    "session_id": "0199e0b1-0000-7000-8000-000000000000",
    "transcript_path": "/tmp/transcript.jsonl",
    "cwd": "/srv/app",
    "hook_event_name": "PostToolUse",
    "tool_name": "mcp__support__lookup_customer",
    "tool_input": {"ticket": "SUP-4417"},
    "tool_response": {"ticket": "SUP-4417", "status": "ESCALATED"},
    "tool_use_id": "toolu_01",
}


def run(args: list[str], stdin: str = "", cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        CLI + args, input=stdin, capture_output=True, text=True, cwd=cwd, timeout=60
    )


def test_help_names_all_three_surfaces(repo_root: Path) -> None:
    done = run(["--help"], cwd=repo_root)
    assert done.returncode == 0
    for word in ("check", "hook", "proxy"):
        assert word in done.stdout


def test_version_prints_the_package_name_and_version(repo_root: Path) -> None:
    import egresswall

    done = run(["--version"], cwd=repo_root)
    assert done.stdout.strip() == f"{egresswall.NAME} {egresswall.__version__}"


def test_check_on_a_clean_file_exits_zero(repo_root: Path) -> None:
    done = run(["check", "demo/clean.json", "--policy", "demo/policy.json"], cwd=repo_root)
    assert done.returncode == 0
    assert done.stdout == "CLEAN: demo/clean.json\n"


def test_check_on_a_leaky_file_exits_one_and_names_every_reason(repo_root: Path) -> None:
    done = run(["check", "demo/leaky.json", "--policy", "demo/policy.json"], cwd=repo_root)
    assert done.returncode == 1
    assert done.stdout.startswith("BLOCKED: demo/leaky.json\n")
    assert done.stdout.rstrip().endswith("6 violations")
    assert "member-88231@northgate-clinic.test" not in done.stdout


def test_check_json_format_is_machine_readable(repo_root: Path) -> None:
    done = run(
        ["check", "demo/leaky.json", "--policy", "demo/policy.json", "--format", "json"],
        cwd=repo_root,
    )
    assert done.returncode == 1
    report = json.loads(done.stdout)
    assert report["blocked"] is True
    assert {item["code"] for item in report["violations"]} == {
        "RAW_IDENTIFIER",
        "DENIED_FIELD_PATH",
        "FORBIDDEN_KEY",
        "SECRET_MATERIAL",
        "FORBIDDEN_VALUE",
    }


def test_check_reads_stdin(repo_root: Path) -> None:
    done = run(["check", "-"], stdin='{"api_key": "x"}', cwd=repo_root)
    assert done.returncode == 1
    assert "FORBIDDEN_KEY" in done.stdout


def test_check_reports_an_unreadable_file_without_a_traceback(repo_root: Path) -> None:
    done = run(["check", "no-such-file.json"], cwd=repo_root)
    assert done.returncode == 2
    assert "Traceback" not in done.stderr
    assert "cannot read" in done.stderr


def test_a_bad_policy_file_fails_closed_without_a_traceback(
    repo_root: Path, tmp_path: Path
) -> None:
    bad = tmp_path / "policy.json"
    bad.write_text('{"redact": true}')
    done = run(["check", "demo/clean.json", "--policy", str(bad)], cwd=repo_root)
    assert done.returncode == 2
    assert "unknown policy keys: redact" in done.stderr
    assert "Traceback" not in done.stderr


def test_a_policy_that_is_not_a_json_object_fails_closed_in_every_mode(
    repo_root: Path, tmp_path: Path
) -> None:
    """`hook` must exit 2 (blocking) and never 1, which Claude Code treats as non-blocking."""
    event = dict(HOOK_EVENT, tool_response={"ssn": "412-88-7690"})
    for index, body in enumerate(["null", "true", "123", '["denied_field_paths"]', '"text"']):
        bad = tmp_path / f"policy{index}.json"
        bad.write_text(body)
        for args, stdin in ((["check", "demo/leaky.json"], ""), (["hook"], json.dumps(event))):
            done = run([*args, "--policy", str(bad)], stdin=stdin, cwd=repo_root)
            assert done.returncode == 2, (body, args, done.stderr)
            assert "policy must be a JSON object" in done.stderr, body
            assert "Traceback" not in done.stderr, body


def test_hook_exits_zero_on_a_clean_tool_response(repo_root: Path) -> None:
    done = run(["hook"], stdin=json.dumps(HOOK_EVENT), cwd=repo_root)
    assert done.returncode == 0
    assert done.stderr == ""


def test_hook_exits_two_and_explains_on_a_violating_tool_response(repo_root: Path) -> None:
    event = dict(HOOK_EVENT, tool_response={"contact": "member-88231@northgate-clinic.test"})
    done = run(["hook"], stdin=json.dumps(event), cwd=repo_root)
    assert done.returncode == 2
    assert "mcp__support__lookup_customer" in done.stderr
    assert "RAW_IDENTIFIER at tool_response.contact" in done.stderr
    assert "member-88231@northgate-clinic.test" not in done.stderr


def test_hook_ignores_an_event_without_a_tool_response(repo_root: Path) -> None:
    event = {k: v for k, v in HOOK_EVENT.items() if k != "tool_response"}
    done = run(["hook"], stdin=json.dumps(event), cwd=repo_root)
    assert done.returncode == 0


def test_hook_does_not_screen_the_tool_input(repo_root: Path) -> None:
    event = dict(HOOK_EVENT, tool_input={"api_key": "sk-proj-" + "Zk4Qb7Xm2R" * 5})
    done = run(["hook"], stdin=json.dumps(event), cwd=repo_root)
    assert done.returncode == 0


def test_hook_on_broken_stdin_does_not_traceback(repo_root: Path) -> None:
    done = run(["hook"], stdin="not json", cwd=repo_root)
    assert done.returncode == 2
    assert "Traceback" not in done.stderr


def test_proxy_without_a_command_explains_itself(repo_root: Path) -> None:
    done = run(["proxy"], cwd=repo_root)
    assert done.returncode == 2
    assert "needs a server command" in done.stderr


# --- regressions found by the red team ---------------------------------------

DEEP = "[" * 10000 + "]" * 10000


def test_the_hook_refuses_a_payload_it_cannot_parse(repo_root: Path) -> None:
    """RecursionError is not a JSONDecodeError; exit 1 would be a silent fail-open."""
    done = run(["hook"], stdin='{"tool_name":"x","tool_response":' + DEEP + "}", cwd=repo_root)
    assert done.returncode == 2, done.stderr
    assert "PAYLOAD_TOO_DEEP" in done.stderr
    assert "Traceback" not in done.stderr


def test_check_refuses_a_file_it_cannot_parse(repo_root: Path, tmp_path: Path) -> None:
    deep = tmp_path / "deep.json"
    deep.write_text(DEEP)
    done = run(["check", str(deep), "--format", "json"], cwd=repo_root)
    assert done.returncode == 2, done.stdout
    assert done.stdout == ""
    assert "nests too deep" in done.stderr
    assert "Traceback" not in done.stderr


def test_check_names_the_file_that_is_not_utf8(repo_root: Path, tmp_path: Path) -> None:
    bad = tmp_path / "nonutf8.json"
    bad.write_bytes(b"\xff\xfe\x00bad")
    done = run(["check", str(bad)], cwd=repo_root)
    assert done.returncode == 2
    assert done.stderr.startswith(f"egresswall: cannot read {bad}: ")


def test_the_hook_refuses_stdin_it_cannot_parse_at_all(repo_root: Path) -> None:
    """Unparseable input is content the hook could not screen: exit 2, never 1."""
    for stdin in ("not json", '{"tool_response":'):
        done = run(["hook"], stdin=stdin, cwd=repo_root)
        assert done.returncode == 2, (stdin, done.stderr)
        assert "was not screened" in done.stderr
        assert "Traceback" not in done.stderr


def test_the_hook_never_logs_a_tool_name_that_carries_a_value(repo_root: Path) -> None:
    """A server names its own tools, so a tool named after a row is a leak too."""
    event = dict(
        HOOK_EVENT,
        tool_name="mcp__support__member-88231@northgate-clinic.test",
        tool_response={"ssn": "412-88-7690"},
    )
    done = run(["hook"], stdin=json.dumps(event), cwd=repo_root)
    assert done.returncode == 2
    assert "member-88231@northgate-clinic.test" not in done.stderr
    assert "<tool>" in done.stderr


# --- fix pass 4: a report is bounded, and ambiguous input is refused ---------


def amplifying_event(chains: int = 300, depth: int = 30) -> str:
    """A tool response whose every field name is forbidden, at depth.

    Every violation carries a path, every path segment is a name the server
    chose, so an uncapped report multiplies a payload into the operator's log
    and -- through the hook's stderr -- into the model's context.
    """
    name = "b" * 59 + "token"

    def chain() -> dict:
        top: dict = {}
        node = top
        for _ in range(depth):
            child: dict = {}
            node[name] = child
            node = child
        node[name] = ""
        return top

    payload = {f"c{index:05d}": chain() for index in range(chains)}
    return json.dumps({"tool_name": "t", "tool_response": payload})


def test_the_hook_report_is_bounded_however_many_violations_there_are(repo_root: Path) -> None:
    done = run(["hook"], stdin=amplifying_event(), cwd=repo_root)
    assert done.returncode == 2
    assert len(done.stderr) < 8192, len(done.stderr)
    assert "(+" in done.stderr and " more)" in done.stderr


def test_the_check_report_is_bounded_and_says_how_much_it_did_not_list(
    repo_root: Path, tmp_path: Path
) -> None:
    payload = tmp_path / "many.json"
    payload.write_text(json.dumps(json.loads(amplifying_event())["tool_response"]))
    done = run(["check", str(payload), "--format", "json"], cwd=repo_root)
    assert done.returncode == 1
    report = json.loads(done.stdout)
    assert 0 < len(report["violations"]) <= 20
    assert report["truncated"] > 0
    text = run(["check", str(payload)], cwd=repo_root)
    assert len(text.stdout) < 8192, len(text.stdout)
    assert f"(+{report['truncated']} more)" in text.stdout


DUPLICATE = '{"v": "member-88231@northgate-clinic.test", "v": "clean"}'


def test_a_duplicate_object_key_is_refused_rather_than_screened_last_wins(
    repo_root: Path,
) -> None:
    """Last-wins is a fail-open: a first-wins reader downstream sees the value."""
    done = run(["check", "-"], stdin=DUPLICATE, cwd=repo_root)
    assert done.returncode == 2, done.stdout
    assert "duplicate object key" in done.stderr
    assert "member-88231@northgate-clinic.test" not in done.stderr
    assert "Traceback" not in done.stderr


def test_the_hook_refuses_a_duplicate_object_key_too(repo_root: Path) -> None:
    event = '{"tool_name":"t","tool_response":' + DUPLICATE + "}"
    done = run(["hook"], stdin=event, cwd=repo_root)
    assert done.returncode == 2, done.stderr
    assert "was not screened" in done.stderr


# --- fix pass 4: every parse failure is the documented refusal, not a traceback


#: The exception classes a parse or load path may raise. UnicodeError is a
#: ValueError, OverflowError is not, and RecursionError is neither -- catching
#: only json's own JSONDecodeError left three ways to exit on a traceback.
PARSE_FAILURES = [ValueError, OverflowError, RecursionError, UnicodeError]


@pytest.mark.parametrize("failure", PARSE_FAILURES)
def test_any_parse_failure_exits_two_on_every_surface(failure, monkeypatch) -> None:
    """Input that could not be parsed is input that was not screened: exit 2."""

    def explode(text: str) -> object:
        raise failure("refused")

    monkeypatch.setattr(_cli, "loads", explode)

    monkeypatch.setattr("sys.stdin", io.StringIO("{}"))
    err = io.StringIO()
    args = argparse.Namespace(file="-", policy=None, format="text")
    assert _cli._cmd_check(args, io.StringIO(), err) == 2
    assert err.getvalue().startswith(f"{_cli.NAME}: cannot read -")

    monkeypatch.setattr("sys.stdin", io.StringIO("{}"))
    hook_err = io.StringIO()
    hook_args = argparse.Namespace(policy=None)
    assert _cli._cmd_hook(hook_args, io.StringIO(), hook_err) == 2
    assert "was not screened" in hook_err.getvalue()


def test_a_number_too_long_to_convert_is_refused_cleanly(repo_root: Path, tmp_path: Path) -> None:
    """Valid JSON this interpreter will not convert is still refused, not crashed on."""
    big = tmp_path / "big.json"
    big.write_text('{"n": ' + "9" * 100000 + "}")
    done = run(["check", str(big)], cwd=repo_root)
    assert done.returncode == 2, done.stdout
    assert done.stdout == ""
    assert "Traceback" not in done.stderr
    assert done.stderr.startswith(f"egresswall: cannot read {big}: ")


# --- fix pass 5: the only silent allow the CLI had ---------------------------


@pytest.mark.parametrize(
    "stdin",
    [
        "null",
        "[]",
        '"a string"',
        '[{"tool_response": {"e": "member-88231@northgate-clinic.test"}}]',
    ],
)
def test_the_hook_refuses_input_that_parses_to_a_shape_it_does_not_recognise(
    repo_root: Path, stdin: str
) -> None:
    """A PostToolUse event is an object; anything else was not screened.

    The array case is the one that mattered: a payload plainly carrying a
    `tool_response` was passed through unscreened because it arrived wrapped.
    """
    done = run(["hook"], stdin=stdin, cwd=repo_root)
    assert done.returncode == 2, done.stdout
    assert "not a JSON object and was not screened" in done.stderr
    assert "member-88231@northgate-clinic.test" not in done.stderr


def test_the_hook_still_passes_a_real_event_with_no_tool_response(repo_root: Path) -> None:
    """A PreToolUse event legitimately has none, and must not be refused."""
    event = dict(HOOK_EVENT)
    del event["tool_response"]
    done = run(["hook"], stdin=json.dumps(event), cwd=repo_root)
    assert done.returncode == 0, done.stderr


# --- fix pass 6: nothing this CLI does ends in a traceback --------------------

#: Replace a function every subcommand reaches with one that raises something
#: `main` never listed, then run the real entry point.
FAULT = (
    "import sys\n"
    "from egresswall import _cli\n"
    "def boom(path):\n"
    "    raise RuntimeError('injected fault')\n"
    "_cli._load_policy = boom\n"
    "sys.exit(_cli.main(sys.argv[1:]))\n"
)


def run_faulty(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", FAULT, *args], capture_output=True, text=True, cwd=cwd, timeout=60
    )


@pytest.mark.parametrize("args", [["check", "demo/clean.json"], ["proxy", "--", "true"]])
def test_an_unexpected_failure_is_one_line_and_the_documented_exit(
    repo_root: Path, args: list[str]
) -> None:
    """A traceback in an MCP server log carries the payload's own field names."""
    done = run_faulty(args, cwd=repo_root)
    assert done.returncode == 2, done.stderr
    assert done.stdout == ""
    assert done.stderr == "egresswall: injected fault\n"
    assert "Traceback" not in done.stderr


def test_the_hidden_traceback_flag_puts_the_real_traceback_back(repo_root: Path) -> None:
    done = run_faulty(["--traceback", "check", "demo/clean.json"], cwd=repo_root)
    assert done.returncode == 1
    assert "Traceback" in done.stderr
    assert "RuntimeError: injected fault" in done.stderr


def test_the_traceback_flag_is_hidden_from_help(repo_root: Path) -> None:
    done = run(["--help"], cwd=repo_root)
    assert "--traceback" not in done.stdout


def test_both_entry_points_go_through_the_same_guard(repo_root: Path) -> None:
    """One safety net covers the console script and `python -m egresswall`."""
    import tomllib

    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["scripts"]["egresswall"] == "egresswall._cli:main"
    main_module = (repo_root / "src" / "egresswall" / "__main__.py").read_text(encoding="utf-8")
    assert "from ._cli import main" in main_module and "main()" in main_module
