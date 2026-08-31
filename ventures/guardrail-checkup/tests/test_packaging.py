"""Build the wheel, install it into a throwaway venv, run the console script."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tarfile
import tomllib
import zipfile
from pathlib import Path

import pytest

import guardrail_checkup

pytestmark = pytest.mark.skipif(shutil.which("uv") is None, reason="uv is not installed")


@pytest.fixture(scope="module")
def built(tmp_path_factory, repo_root: Path) -> Path:
    out = tmp_path_factory.mktemp("dist")
    subprocess.run(["uv", "build", "--out-dir", str(out)], cwd=repo_root, check=True, capture_output=True)
    return out


def project(repo_root: Path) -> dict:
    return tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))["project"]


def test_uv_build_produces_a_wheel_and_an_sdist(built: Path) -> None:
    names = sorted(item.name for item in built.iterdir())
    version = guardrail_checkup.__version__
    assert f"guardrail_checkup-{version}-py3-none-any.whl" in names
    assert f"guardrail_checkup-{version}.tar.gz" in names


def siblings(repo_root: Path) -> list[str]:
    """The two dependencies, from the working copies, until they are on PyPI.

    After the release this list is empty and the install below is the plain
    `uv pip install <wheel>` a user runs; see CHANGELOG.md 0.1.0.
    """

    present = [repo_root.parent / name for name in ("plan-lint", "egress-guard")]
    return [str(item) for item in present if (item / "pyproject.toml").exists()]


def test_the_wheel_installs_into_a_fresh_venv_and_the_console_script_runs(
    built: Path, tmp_path: Path, repo_root: Path
) -> None:
    venv = tmp_path / "venv"
    subprocess.run(["uv", "venv", "-p", sys.executable, str(venv)], check=True, capture_output=True)
    python = venv / "bin" / "python"
    done = subprocess.run(
        ["uv", "pip", "install", "--python", str(python), str(next(built.glob("*.whl"))), *siblings(repo_root)],
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stderr
    script = venv / "bin" / guardrail_checkup.NAME
    assert script.exists(), f"the console script must be named {guardrail_checkup.NAME}"
    done = subprocess.run([str(script), "--version"], capture_output=True, text=True, check=True)
    assert done.stdout.strip() == f"{guardrail_checkup.NAME} {guardrail_checkup.__version__}"
    module = subprocess.run(
        [str(python), "-m", "guardrail_checkup", "--version"], capture_output=True, text=True, check=True
    )
    assert module.stdout.strip() == done.stdout.strip()


def test_the_console_script_without_the_siblings_is_one_line_and_exit_two(built: Path, tmp_path: Path) -> None:
    """The real partial environment: the wheel installed with --no-deps, in its own venv.

    The promise is exit 2 and one line for every error a user can reach. A
    module-level sibling import made this a two-level traceback and exit 1.
    """

    venv = tmp_path / "bare"
    subprocess.run(["uv", "venv", "-p", sys.executable, str(venv)], check=True, capture_output=True)
    python = venv / "bin" / "python"
    subprocess.run(
        ["uv", "pip", "install", "--python", str(python), "--no-deps", str(next(built.glob("*.whl")))],
        check=True,
        capture_output=True,
    )
    (tmp_path / "repo").mkdir()
    done = subprocess.run(
        [str(venv / "bin" / guardrail_checkup.NAME), "run", str(tmp_path / "repo"), "--out", str(tmp_path / "r.md")],
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert done.returncode == 2, (done.returncode, done.stderr)
    assert "Traceback" not in done.stderr
    assert len(done.stderr.strip().splitlines()) == 1, done.stderr
    assert "pip install guardrail-checkup" in done.stderr


def test_the_installed_package_carries_its_type_marker(built: Path) -> None:
    with zipfile.ZipFile(next(built.glob("*.whl"))) as wheel:
        assert "guardrail_checkup/py.typed" in wheel.namelist()


def test_the_sdist_ships_exactly_one_package(built: Path) -> None:
    """A second, divergent copy of the implementation must not ride along in a release."""

    with tarfile.open(next(built.glob("*.tar.gz"))) as sdist:
        packages = {
            name.split("/")[2] for name in sdist.getnames() if name.count("/") >= 3 and name.split("/")[1] == "src"
        }
    assert packages == {"guardrail_checkup"}


def test_the_sdist_ships_the_demo_the_docs_and_the_tests(built: Path) -> None:
    """Everything the suite in the sdist reads, or the suite in the sdist fails."""

    with tarfile.open(next(built.glob("*.tar.gz"))) as sdist:
        names = {name.split("/", 1)[1] for name in sdist.getnames() if "/" in name}
    required = (
        "demo/demo.sh",
        "demo/OUTPUT.txt",
        "demo/OUTPUT.md",
        "docs/comparison.md",
        "tests/conftest.py",
        ".python-version",
        ".github/workflows/ci.yml",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
    )
    for item in required:
        assert item in names, item
    read_by_the_suite = {
        found
        for path in sorted(Path(__file__).parent.glob("*.py"))
        if path.name != Path(__file__).name  # this file names the pattern itself
        for found in re.findall(r'repo_root / "([^"]+)"', path.read_text(encoding="utf-8"))
    }
    shipped = set(names) | {"pyproject.toml"}
    for item in sorted(read_by_the_suite):
        assert item in shipped or any(name.startswith(f"{item}/") for name in names), item


def test_the_wheel_ships_the_package_and_nothing_else(built: Path) -> None:
    """CONTRIBUTING says the installed package contacts no network. This is its boundary."""

    with zipfile.ZipFile(next(built.glob("*.whl"))) as wheel:
        tops = {name.split("/")[0] for name in wheel.namelist()}
    assert tops == {"guardrail_checkup", f"guardrail_checkup-{guardrail_checkup.__version__}.dist-info"}, tops


def test_the_name_the_console_script_and_the_module_constant_agree(repo_root: Path) -> None:
    meta = project(repo_root)
    assert meta["name"] == guardrail_checkup.NAME
    assert meta["scripts"] == {guardrail_checkup.NAME: "guardrail_checkup._cli:main"}


def test_the_only_runtime_dependencies_are_the_two_sibling_packages(repo_root: Path) -> None:
    dependencies = project(repo_root)["dependencies"]
    assert sorted(item.split(">")[0] for item in dependencies) == ["agent-plan-lint", "egresswall"]


def test_the_python_classifiers_are_the_versions_ci_runs(repo_root: Path) -> None:
    """A classifier is a promise PyPI renders; nothing else in the suite reads one."""

    workflow = (repo_root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    tested = re.findall(r'"(3\.\d+)"', re.search(r"python: \[(.*?)\]", workflow).group(1))
    meta = project(repo_root)
    claimed = [
        item.split(" :: ")[-1]
        for item in meta["classifiers"]
        if item.startswith("Programming Language :: Python :: 3.")
    ]
    assert claimed == tested == ["3.11", "3.12", "3.13"], (claimed, tested)
    floor = meta["requires-python"].lstrip(">=")
    assert floor == (repo_root / ".python-version").read_text().strip() == "3.11"


def test_the_ci_matrix_runs_both_operating_systems(repo_root: Path) -> None:
    workflow = (repo_root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert re.search(r"os: \[ubuntu-latest, macos-latest\]", workflow)


def test_check_sh_runs_the_steps_ci_runs_before_it_builds(repo_root: Path) -> None:
    """A step CI grows and this script lacks would ship an untested claim."""

    script = (repo_root / "scripts" / "check.sh").read_text(encoding="utf-8")
    workflow = (repo_root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    matrix_job = workflow[: workflow.index("  docs-truth:")]
    steps = [line.strip()[len("- run: ") :] for line in matrix_job.splitlines() if line.strip().startswith("- run: uv")]
    scripted = [line.strip() for line in script.splitlines() if line.startswith("uv ")]
    normalised = [re.sub(r" --python \$\{\{ matrix\.python \}\}", "", item) for item in steps]
    assert scripted == normalised, (scripted, normalised)


def test_the_release_maturity_classifier_is_the_one_this_release_intends(repo_root: Path) -> None:
    statuses = [item for item in project(repo_root)["classifiers"] if item.startswith("Development Status")]
    assert statuses == ["Development Status :: 4 - Beta"]


def test_no_url_in_the_shipped_source_names_another_repository(repo_root: Path) -> None:
    """The sdist ships scripts/, so a stray URL in it is published with the package."""

    source = project(repo_root)["urls"]["Source"]
    for folder in ("src", "scripts"):
        for path in sorted((repo_root / folder).rglob("*.py")):
            for url in re.findall(r"https?://[^\s\"'()]+", path.read_text(encoding="utf-8")):
                if "github.com/Alex-lop" not in url:
                    continue  # a third party's URL is evidence, not this package's identity
                assert url.startswith(source), (path.name, url)


def test_every_test_file_on_disk_is_tracked_by_git(repo_root: Path) -> None:
    """A clean clone has to collect the count the README's runnable block asserts.

    `tests/test_limits.py` was the one file in the package git did not track and
    was not gitignored either: `pytest --collect-only` reported 318 here and 314
    from a clone, and `CHANGELOG.md` named a file that was not in the repository.
    """

    inside = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--is-inside-work-tree"], capture_output=True, check=False
    )
    if inside.returncode != 0:
        # An unpacked sdist is not a git work tree, and the sdist ships this
        # suite. The check applies to a clone; there it is `CalledProcessError`.
        pytest.skip("not a git checkout; the tracked-file check only applies to a clone")
    done = subprocess.run(["git", "-C", str(repo_root), "ls-files", "-z", "tests"], capture_output=True, check=True)
    tracked = {item for item in done.stdout.decode("utf-8", "replace").split("\0") if item}
    on_disk = {f"tests/{path.name}" for path in sorted((repo_root / "tests").glob("test_*.py"))}
    assert on_disk <= tracked, sorted(on_disk - tracked)


def test_every_project_url_names_this_packages_own_repository(repo_root: Path) -> None:
    """A URL repointed at another repository is a claim PyPI renders in the sidebar."""

    urls = project(repo_root)["urls"]
    source = urls["Source"]
    assert source == "https://github.com/Alex-lop/guardrail-checkup"
    assert urls["Homepage"] == source
    for name, url in urls.items():
        assert url.startswith(source), (name, url)


def test_the_changelog_records_that_the_path_sources_flip_at_release(repo_root: Path) -> None:
    """[tool.uv.sources] is pre-release scaffolding; the CHANGELOG has to say so."""

    pyproject = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    changelog = (repo_root / "CHANGELOG.md").read_text(encoding="utf-8")
    if "[tool.uv.sources]" in pyproject:
        assert "tool.uv.sources" in changelog
        assert "PyPI" in changelog
