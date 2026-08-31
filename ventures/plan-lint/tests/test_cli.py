"""The command line, exercised as a subprocess exactly as a user runs it."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import agent_plan_lint
from agent_plan_lint import ISSUE_CODES, CriterionVerificationKind, ProjectPolicy, validate_plan
from conftest import plan as _plan
from conftest import policy as _policy
from conftest import replace, replace_criterion

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "demo"


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "agent_plan_lint.cli", *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


def test_check_reports_the_demo_issues_and_exits_one() -> None:
    result = run("check", str(DEMO / "plan-bad.json"), "--policy", str(DEMO / "policy.json"))

    assert result.returncode == 1
    assert "invalid: 4 issues" in result.stdout
    reported = [line.split()[0].rstrip(":") for line in result.stdout.splitlines()[1:]]
    assert reported == [
        "criterion_model_assertion",
        "cycle",
        "parallel_write_conflict",
        "write_path_not_allowed",
    ]


def test_check_exits_zero_on_a_plan_within_policy() -> None:
    result = run("check", str(DEMO / "plan-good.json"), "--policy", str(DEMO / "policy.json"))

    assert result.returncode == 0
    assert result.stdout.startswith("ok: ")
    assert "order: work-api -> work-models -> work-tests -> assemble -> verify" in result.stdout


def test_json_format_is_the_validation_result() -> None:
    result = run(
        "check",
        str(DEMO / "plan-bad.json"),
        "--policy",
        str(DEMO / "policy.json"),
        "--format",
        "json",
    )
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["valid"] is False
    assert payload["topological_order"] == []
    assert {issue["code"] for issue in payload["issues"]} == {
        "criterion_model_assertion",
        "cycle",
        "parallel_write_conflict",
        "write_path_not_allowed",
    }
    assert all(set(issue) == {"code", "task_id", "detail"} for issue in payload["issues"])


def test_strict_rejects_a_human_gate_that_the_default_admits(tmp_path) -> None:
    policy = ProjectPolicy.model_validate({**_policy().model_dump(mode="json"), "risk_gates": ["release-review"]})
    plan = replace_criterion(
        _plan(),
        verification_kind=CriterionVerificationKind.HUMAN_GATE,
        verifier_task_id=None,
        verifier_id="release-review",
    )
    policy_path = tmp_path / "policy.json"
    plan_path = tmp_path / "plan.json"
    policy_path.write_text(json.dumps(policy.model_dump(mode="json")))
    plan_path.write_text(json.dumps(plan.model_dump(mode="json")))

    relaxed = run("check", str(plan_path), "--policy", str(policy_path))
    strict = run("check", str(plan_path), "--policy", str(policy_path), "--strict")

    assert relaxed.returncode == 0
    assert strict.returncode == 1
    assert "criterion_human_gate" in strict.stdout


@pytest.mark.parametrize(
    ("plan_name", "text", "expected"),
    (
        ("absent.json", None, "cannot read"),
        ("broken.json", "{", "not valid JSON"),
        ("empty.json", "{}", "plan is invalid"),
    ),
)
def test_a_document_that_cannot_be_loaded_exits_two(tmp_path, plan_name, text, expected) -> None:
    path = tmp_path / plan_name
    if text is not None:
        path.write_text(text)

    result = run("check", str(path), "--policy", str(DEMO / "policy.json"))

    assert result.returncode == 2
    assert expected in result.stderr
    assert result.stdout == ""


def test_codes_lists_every_issue_code_with_its_meaning() -> None:
    result = run("codes")
    listed = {line.split()[0]: line.split(maxsplit=1)[1].strip() for line in result.stdout.splitlines()}

    assert result.returncode == 0
    assert listed == dict(ISSUE_CODES)


def test_schema_prints_the_json_schema_of_both_documents() -> None:
    result = run("schema")
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["plan"]["title"] == "Plan"
    assert payload["policy"]["title"] == "ProjectPolicy"
    assert "tasks" in payload["plan"]["properties"]
    assert "allowed_write_globs" in payload["policy"]["properties"]


def test_version_prints_the_installed_version() -> None:
    result = run("--version")

    assert result.returncode == 0
    assert result.stdout.strip() == f"agent-plan-lint {agent_plan_lint.__version__}"


def test_help_names_every_subcommand() -> None:
    result = run("--help")

    assert result.returncode == 0
    for command in ("check", "codes", "schema"):
        assert command in result.stdout


def test_no_subcommand_is_a_usage_error() -> None:
    result = run()

    assert result.returncode == 2
    assert "usage: agent-plan-lint" in result.stderr


@pytest.mark.skipif(sys.platform == "win32", reason="demo.sh is a POSIX shell script")
def test_demo_script_reproduces_the_captured_output(tmp_path) -> None:
    shim = tmp_path / "agent-plan-lint"
    shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" -m agent_plan_lint.cli "$@"\n')
    shim.chmod(0o755)

    result = subprocess.run(
        ["sh", str(DEMO / "demo.sh")],
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": "/usr/bin:/bin", "PLAN_LINT": str(shim)},
    )

    assert result.stdout == (DEMO / "OUTPUT.txt").read_text()


def test_a_document_that_cannot_be_loaded_is_json_when_json_was_asked_for(tmp_path) -> None:
    """`--format json` is JSON on all three exit codes, not only on a verdict."""

    path = tmp_path / "deep.json"
    path.write_text('{"a":' * 10_000 + "1" + "}" * 10_000)

    result = run("check", str(path), "--policy", str(DEMO / "policy.json"), "--format", "json")
    payload = json.loads(result.stdout)

    assert result.returncode == 2
    assert payload["document"] == str(path)
    assert "nested too deeply" in payload["error"]


def test_a_deeply_nested_document_exits_two_without_a_traceback(tmp_path) -> None:
    path = tmp_path / "deep.json"
    path.write_text('{"a":' * 10_000 + "1" + "}" * 10_000)

    result = run("check", str(path), "--policy", str(DEMO / "policy.json"))

    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert result.stderr.strip() == f"agent-plan-lint: {path} is nested too deeply to load"


def test_the_text_report_is_one_verdict_line_plus_one_line_per_issue(tmp_path) -> None:
    """Neither a document nor its file name can forge a line of this tool's own output.

    A bidirectional override inside a document is refused when it loads, so
    what still has to be escaped here is the name the caller typed.
    """

    outside = "docs/guide.md"
    plan = replace(
        _plan(),
        "work-a",
        write_paths=(outside,),
        expected_outputs=[{"name": "patch-a", "kind": "patch", "paths": [outside]}],
    )
    policy_path = tmp_path / "policy.json"
    plan_path = tmp_path / "pl‮an.json"
    policy_path.write_text(json.dumps(_policy().model_dump(mode="json")))
    plan_path.write_text(json.dumps(plan.model_dump(mode="json")))
    expected = validate_plan(_policy(), plan)

    result = run("check", str(plan_path), "--policy", str(policy_path))

    assert result.returncode == 1
    assert expected.issues and len(result.stdout.splitlines()) == 1 + len(expected.issues)
    assert "‮" not in result.stdout
    assert "\\u202e" in result.stdout


def test_the_module_form_is_the_console_script() -> None:
    """`python -m agent_plan_lint` is what a hook reaches for when the script is not on PATH."""

    module = subprocess.run(
        [
            sys.executable,
            "-m",
            "agent_plan_lint",
            "check",
            str(DEMO / "plan-good.json"),
            "--policy",
            str(DEMO / "policy.json"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    script = run("check", str(DEMO / "plan-good.json"), "--policy", str(DEMO / "policy.json"))

    assert module.returncode == script.returncode == 0
    assert module.stdout == script.stdout


def test_the_readme_names_the_exit_statuses_the_cli_actually_uses() -> None:
    """The three numbers the tests above assert are the three the README prints."""

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    sentence = re.search(r"Exit status is (.+?)so it drops", readme, re.S)

    assert sentence is not None
    assert [int(number) for number in re.findall(r"`(\d+)`", sentence.group(1))] == [0, 1, 2]


@pytest.mark.parametrize("output_format", ("text", "json"))
def test_an_over_long_integer_literal_exits_two_in_the_format_asked_for(tmp_path, output_format: str) -> None:
    """A document that cannot be loaded is exit 2 on every format, never a traceback."""

    path = tmp_path / "bigint.json"
    path.write_text('{"schema_version": ' + "9" * 4_301 + "}")

    result = run("check", str(path), "--policy", str(DEMO / "policy.json"), "--format", output_format)

    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    if output_format == "json":
        assert json.loads(result.stdout)["document"] == str(path)
    else:
        assert "is not valid JSON" in result.stderr


def test_a_document_with_a_complex_yaml_key_exits_two_with_json_on_stdout(tmp_path) -> None:
    """The exit contract holds for the shape that used to escape as a `TypeError`."""

    path = tmp_path / "complex.yaml"
    path.write_text("? [1, 2]\n: v\n")
    result = run("check", str(path), "--policy", str(DEMO / "policy.json"), "--format", "json")

    assert result.returncode == 2
    assert json.loads(result.stdout)["document"] == str(path)
    assert "Traceback" not in result.stderr


def _with_a_fault(*arguments: str) -> subprocess.CompletedProcess[str]:
    """Run `main` with `validate_plan` replaced by a fault nothing in the CLI expects."""

    program = (
        "import sys\n"
        "import agent_plan_lint.validation as validation\n"
        "def _boom(*arguments, **keywords):\n"
        "    raise RuntimeError('injected fault')\n"
        "validation.validate_plan = _boom\n"
        "from agent_plan_lint.cli import main\n"
        "sys.exit(main(sys.argv[1:]))\n"
    )
    return subprocess.run(
        [sys.executable, "-c", program, *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


def test_an_unexpected_failure_is_the_documented_error_exit_and_one_line() -> None:
    """A fault nobody predicted is a refusal with a reason, never a traceback at the user."""

    arguments = ("check", str(DEMO / "plan-good.json"), "--policy", str(DEMO / "policy.json"))
    result = _with_a_fault(*arguments)
    with_traceback = _with_a_fault(*arguments, "--traceback")

    assert result.returncode == 2
    assert result.stderr.splitlines() == ["agent-plan-lint: internal error: RuntimeError: injected fault"]
    assert "Traceback" not in result.stderr
    # The hidden flag is for debugging, so it does the opposite: the real traceback.
    assert with_traceback.returncode != 0
    assert "Traceback (most recent call last)" in with_traceback.stderr
    assert "RuntimeError: injected fault" in with_traceback.stderr


def test_both_entry_points_go_through_the_same_safety_net() -> None:
    """`python -m agent_plan_lint` is `main()` and nothing else, so it cannot drift."""

    source = (ROOT / "src" / "agent_plan_lint" / "__main__.py").read_text(encoding="utf-8")

    assert "raise SystemExit(main())" in source
    assert source.count("def ") == 0


def test_the_traceback_flag_is_hidden_from_the_help_text() -> None:
    """A debugging flag is not part of the interface the README documents."""

    for arguments in (("--help",), ("check", "--help")):
        assert "--traceback" not in run(*arguments).stdout


def test_a_usage_error_is_still_a_usage_error_rather_than_an_internal_one() -> None:
    """`SystemExit` from argparse may not be swallowed by the safety net."""

    result = run("check", "--policy", str(DEMO / "policy.json"))

    assert result.returncode == 2
    assert "internal error" not in result.stderr


def test_a_tag_that_cannot_be_converted_exits_two_with_json_on_stdout(tmp_path) -> None:
    """The shape that used to reach `main`'s safety net: exit 2 and no JSON at all.

    `--format json` is documented as JSON on the load failure, and an
    `AttributeError` out of PyYAML's timestamp constructor printed
    `internal error:` on stderr with an empty stdout instead.
    """

    path = tmp_path / "plan.yaml"
    path.write_text('a: !!timestamp "not-a-time"\n')

    result = run("check", str(path), "--policy", str(DEMO / "policy.json"), "--format", "json")

    assert result.returncode == 2
    assert json.loads(result.stdout)["document"] == str(path)
    assert "internal error" not in result.stderr
    assert "Traceback" not in result.stderr


def test_a_hidden_code_point_in_a_file_name_is_escaped_in_the_output() -> None:
    """The command line is the one text a model never saw, so the CLI escapes it itself.

    A variation selector is invisible: without the escape the refusal names a
    file the reader cannot tell from a different one.
    """

    result = run("check", "demo/plan️.json", "--policy", str(DEMO / "policy.json"))

    assert result.returncode == 2
    assert "️" not in result.stderr
    assert "\\ufe0f" in result.stderr
