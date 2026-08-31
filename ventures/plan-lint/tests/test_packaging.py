"""The built wheel installs into a fresh environment and runs."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import agent_plan_lint

ROOT = Path(__file__).resolve().parent.parent

pytestmark = [
    pytest.mark.skipif(shutil.which("uv") is None, reason="packaging is checked with uv"),
    pytest.mark.skipif(sys.platform == "win32", reason="POSIX venv layout"),
]


def uv(*arguments: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["uv", *arguments], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    return result


@pytest.fixture(scope="module")
def wheel(tmp_path_factory) -> Path:
    output = tmp_path_factory.mktemp("dist")
    uv("build", "--out-dir", str(output))
    wheels = list(output.glob("*.whl"))
    sdists = list(output.glob("*.tar.gz"))

    assert len(wheels) == 1 and len(sdists) == 1
    return wheels[0]


def test_the_wheel_installs_and_the_console_script_runs(wheel: Path, tmp_path) -> None:
    environment = tmp_path / "venv"
    # `uv venv` with no `--python` reads `.python-version` from ROOT, so the
    # wheel would be installed on 3.11 even when the suite is running on 3.13.
    uv("venv", "--python", sys.executable, str(environment))
    python = environment / "bin" / "python"
    uv("pip", "install", "--python", str(python), str(wheel))

    imported = subprocess.run(
        [str(python), "-c", "import agent_plan_lint; print(agent_plan_lint.__version__)"],
        capture_output=True,
        text=True,
        check=True,
    )
    helped = subprocess.run(
        [str(environment / "bin" / "agent-plan-lint"), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert imported.stdout.strip() == agent_plan_lint.__version__
    assert "check" in helped.stdout


def test_the_demo_runs_from_the_installed_wheel(wheel: Path, tmp_path) -> None:
    environment = tmp_path / "venv"
    uv("venv", "--python", sys.executable, str(environment))
    uv("pip", "install", "--python", str(environment / "bin" / "python"), str(wheel))

    demo = subprocess.run(
        ["sh", str(ROOT / "demo" / "demo.sh")],
        capture_output=True,
        text=True,
        check=True,
        env={"PATH": "/usr/bin:/bin", "PLAN_LINT": str(environment / "bin" / "agent-plan-lint")},
    )

    assert demo.stdout == (ROOT / "demo" / "OUTPUT.txt").read_text()


def test_the_wheel_environment_is_the_interpreter_running_the_tests(wheel: Path, tmp_path) -> None:
    """Otherwise `pytest -q` on 3.12 and 3.13 both prove only that the wheel runs on 3.11."""

    environment = tmp_path / "venv"
    uv("venv", "--python", sys.executable, str(environment))
    reported = subprocess.run(
        [str(environment / "bin" / "python"), "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert reported.stdout.strip() == f"{sys.version_info.major}.{sys.version_info.minor}"
