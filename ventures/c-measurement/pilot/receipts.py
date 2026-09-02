#!/usr/bin/env python3
"""Publish safe per-repo pilot evidence without publishing untrusted log text."""

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path

from pilot import COLUMNS, LOG_CAP

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results.csv"
LOGS = HERE / "logs"
OUT = HERE / "receipts"
PHASES = ("install.log", "collect.log", "run.log")
FAILURES = {
    "",
    "build-backend",
    "collection-error",
    "env-var/secret required",
    "lock-unresolvable",
    "native-deps",
    "network-at-test-time",
    "no-lock",
    "other",
    "python-version",
    "tests-failed-at-base",
    "timeout",
}
PYTHONS = {"", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14"}
COMPONENT = re.compile(r"[A-Za-z0-9_.-]+")
SHA = re.compile(r"[0-9a-f]{40}")
MAX_LOG = LOG_CAP + len(b"\n\n...[truncated to 200 KB by pilot.py]...\n\n")


def read_csv(path: Path) -> tuple[list[str] | None, list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return reader.fieldnames, list(reader)


def integer(value: str, field: str) -> int:
    assert re.fullmatch(r"0|[1-9][0-9]*", value), (field, value)
    return int(value)


def flag(value: str, field: str) -> bool:
    assert value in {"0", "1"}, (field, value)
    return value == "1"


def receipt_path(repo: str) -> Path:
    parts = repo.split("/")
    assert len(parts) == 2
    assert all(COMPONENT.fullmatch(part) and part not in {".", ".."} for part in parts)
    return Path(parts[0]) / f"{parts[1]}.json"


def log_record(path: Path) -> dict[str, int | str]:
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    assert len(data) <= MAX_LOG, path
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def build(candidate_csv: Path) -> dict[Path, bytes]:
    candidate_header, candidates = read_csv(candidate_csv)
    assert candidate_header and {
        "repo",
        "base_sha_of_first_sample_pr",
        "lock_kind",
    } <= set(candidate_header)
    by_candidate = {row["repo"]: row for row in candidates}
    assert len(candidates) == len(by_candidate) == 100

    header, rows = read_csv(RESULTS)
    assert header == COLUMNS
    by_repo = {row["repo"]: row for row in rows}
    assert len(rows) == len(by_repo) == 100
    assert set(by_repo) == set(by_candidate)

    expected_logs: set[Path] = set()
    rendered: dict[Path, bytes] = {}
    for repo in sorted(by_repo):
        row, candidate = by_repo[repo], by_candidate[repo]
        relative = receipt_path(repo)
        assert SHA.fullmatch(row["base_sha"])
        assert row["base_sha"] == candidate["base_sha_of_first_sample_pr"]
        assert row["lock_kind"] == candidate["lock_kind"]
        assert COMPONENT.fullmatch(row["lock_kind"])
        assert row["python"] in PYTHONS
        assert row["failure_class"] in FAILURES

        install = flag(row["install_ok"], "install_ok")
        collect = flag(row["collect_ok"], "collect_ok")
        run = flag(row["run_ok"], "run_ok")
        assert not collect or install
        assert not run or collect
        duration = float(row["duration_s"])
        assert math.isfinite(duration) and duration >= 0

        needed = {"install.log"}
        if install:
            needed.add("collect.log")
        if collect:
            needed.add("run.log")
        logs: dict[str, dict[str, int | str] | None] = {}
        slug = repo.replace("/", "__")
        for phase in PHASES:
            path = LOGS / slug / phase
            logs[phase] = log_record(path) if phase in needed else None
            if phase in needed:
                expected_logs.add(path)
            else:
                assert not path.exists(), path

        receipt = {
            "base_sha": row["base_sha"],
            "logs": logs,
            "repo": repo,
            "result": {
                "collect_ok": collect,
                "collected_count": integer(row["collected_count"], "collected_count"),
                "duration_s": duration,
                "errored": integer(row["errored"], "errored"),
                "failed": integer(row["failed"], "failed"),
                "failure_class": row["failure_class"] or None,
                "install_ok": install,
                "lock_kind": row["lock_kind"],
                "passed": integer(row["passed"], "passed"),
                "python": row["python"],
                "run_ok": run,
            },
            "schema": 1,
        }
        rendered[relative] = (
            json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False)
            + "\n"
        ).encode()

    assert set(LOGS.rglob("*.log")) == expected_logs
    return rendered


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--csv",
        type=Path,
        default=HERE.parent / "corpus" / "candidates-pilot-100.csv",
    )
    args = parser.parse_args()
    expected = build(args.csv.resolve())
    if args.check:
        actual = {
            path.relative_to(OUT): path.read_bytes() for path in OUT.rglob("*.json")
        }
        assert actual == expected
    else:
        for relative, data in expected.items():
            path = OUT / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        assert {path.relative_to(OUT) for path in OUT.rglob("*.json")} == set(expected)
    print(f"PASS receipts: {len(expected)}")


if __name__ == "__main__":
    main()
