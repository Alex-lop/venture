from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

FENCE = re.compile(r"```.*?```", re.S)
CODE = re.compile(r"`[^`\n]*`")
#: An editorial insertion such as "discover[s]" is the quoter's, not the source's.
INSERTION = re.compile(r"\[[^\]]{0,3}\]")

#: A hermetic git: the user's own configuration cannot change what a test sees.
GIT_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_AUTHOR_NAME": "Test Author",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "Test Author",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, env={**os.environ, **GIT_ENV})


def build_repo(destination: Path, source: Path | None = None) -> Path:
    """A git repository from demo/fixture with the history demo.sh gives it.

    The SHAs are not pinned here -- demo/OUTPUT.txt pins those. What matters to
    these tests is that four commits exist and that three of them are repairs.
    """

    shutil.copytree(source or (ROOT / "demo" / "fixture"), destination)
    git(destination, "init", "-q", "-b", "main")
    git(destination, "add", "-A")
    git(destination, "commit", "-q", "-m", "orders service: handlers, queries, first migration")
    (destination / "db" / "queries.py").write_text(
        (destination / "db" / "queries.py").read_text() + "\n\ndef refund(conn, order_id):\n    pass\n"
    )
    git(destination, "add", "-A")
    git(destination, "commit", "-q", "-m", "fix: refund left the order marked paid")
    (destination / "db" / "migrations" / "0001_orders.sql").write_text(
        (destination / "db" / "migrations" / "0001_orders.sql").read_text() + "ALTER TABLE orders ADD COLUMN x INT;\n"
    )
    git(destination, "add", "-A")
    git(destination, "commit", "-q", "-m", "hotfix: migration ran twice in staging")
    (destination / "app" / "checkout.py").write_text((destination / "app" / "checkout.py").read_text() + "\n# note\n")
    git(destination, "add", "-A")
    git(destination, "commit", "-q", "-m", "revert: back out the checkout retry change")
    return destination


@pytest.fixture(scope="session")
def fixture_repo(tmp_path_factory) -> Path:
    return build_repo(tmp_path_factory.mktemp("repos") / "shipfast")


@pytest.fixture(scope="session")
def shell_env(tmp_path_factory) -> dict[str, str]:
    """A PATH on which `guardrail-checkup` is this checkout, however tests were started."""

    bin_dir = tmp_path_factory.mktemp("bin")
    script = bin_dir / "guardrail-checkup"
    script.write_text(f'#!/bin/sh\nexec "{sys.executable}" -m guardrail_checkup "$@"\n')
    script.chmod(0o755)
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    env["PYTHONPATH"] = str(ROOT / "src")
    return env


@pytest.fixture(scope="session")
def demo_output(tmp_path_factory, shell_env: dict[str, str]) -> tuple[str, Path]:
    """demo/demo.sh run once, with its artifacts kept."""

    keep = tmp_path_factory.mktemp("demo-keep")
    done = subprocess.run(
        [str(ROOT / "demo" / "demo.sh"), str(keep)],
        cwd=ROOT,
        env=shell_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=300,
    )
    assert done.returncode == 0, done.stdout
    return done.stdout, keep


def flatten(text: str) -> str:
    """Compare on words, not typography: curly quotes, emphasis and breaks are noise."""

    for curly, plain in zip("\u2019\u2018\u201c\u201d", "''\"\"", strict=True):
        text = text.replace(curly, plain)
    return INSERTION.sub("", re.sub(r"\s+", " ", text.replace("*", "").replace("`", "")))


def quotations(markdown: str) -> list[str]:
    """Every double-quoted span outside code, paired left to right."""

    spans = flatten(CODE.sub("", FENCE.sub("", markdown))).split('"')
    assert len(spans) % 2 == 1, "unbalanced quotation marks"
    return [item for item in spans[1::2] if len(item) >= 12]


def evidence_corpus() -> str:
    """Every source excerpt checked in under docs/evidence/, as one flat string."""

    files = sorted((ROOT / "docs" / "evidence").glob("*.txt"))
    return flatten("\n".join(item.read_text(encoding="utf-8") for item in files))


def unquoted(markdown: str) -> list[str]:
    """The quotations in `markdown` that no checked-in source contains."""

    corpus = evidence_corpus()
    return [quote for quote in quotations(markdown) if quote.strip(". ") not in corpus]
