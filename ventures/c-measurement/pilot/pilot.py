#!/usr/bin/env python3
"""Base-snapshot buildability pilot for the Track M corpus.

For each candidate repo: check out the base commit of its first sample PR inside a
container, install *from the lockfile only*, then `pytest --collect-only` and a real
`pytest` run with the network off. One results.csv row per repo.

Untrusted repo code never runs on the host: every phase is a `docker run`, the work
tree lives in a per-repo docker volume, and no host path is ever mounted.

Usage:  python3 pilot.py --csv <candidates.csv> [--jobs 3] [--limit N] [--repo O/R]
        python3 pilot.py --selfcheck      # no docker, no network
"""
from __future__ import annotations

import argparse
import csv
import fcntl
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results.csv"
LOGDIR = HERE / "logs"

COLUMNS = [
    "repo", "base_sha", "python", "lock_kind", "install_ok", "collect_ok",
    "collected_count", "run_ok", "passed", "failed", "errored", "duration_s",
    "failure_class", "notes",
]

IMAGES = ["3.9", "3.10", "3.11", "3.12", "3.13", "3.14"]
DEFAULT_PY = "3.12"
# newest is not safest: prefer the version most third-party wheels exist for
PY_PREFERENCE = ["3.12", "3.13", "3.11", "3.10", "3.14", "3.9"]
IMG = "pilot-py:{}"
UV_CACHE_VOL = "pilot-uvcache"
PIP_CACHE_VOL = "pilot-pipcache"

CAP_INSTALL = 600   # 10 min
CAP_COLLECT = 300   # 5 min
CAP_RUN = 900       # 15 min
MEM = os.environ.get("PILOT_MEM", "2500m")   # docker VM has 8 GB; 3 x 4g overcommits it
CPUS = os.environ.get("PILOT_CPUS", "2")
LOG_CAP = 200 * 1024  # 200 KB per log file

_write_lock_path = HERE / ".results.lock"


# ---------------------------------------------------------------- python choice

def _cmp(a: tuple[int, int], b: tuple[int, int]) -> int:
    return (a > b) - (a < b)


def spec_allows(spec: str, ver: str) -> bool:
    """Does a PEP 440 `requires-python` string admit this X.Y? (major.minor only)."""
    v = tuple(int(x) for x in ver.split("."))
    for raw in spec.split(","):
        s = raw.strip()
        if not s:
            continue
        m = re.match(r"^(==|!=|>=|<=|~=|>|<)?\s*v?(\d+)(?:\.(\d+|\*))?", s)
        if not m:
            continue
        op = m.group(1) or "=="
        major = int(m.group(2))
        minor_raw = m.group(3)
        if minor_raw in (None, "*"):
            # bare major bound, e.g. "<4" or "==3.*": compare on major only
            if op in (">=", "==", "~=") and v[0] < major:
                return False
            if op == "<" and v[0] >= major:
                return False
            if op == "<=" and v[0] > major:
                return False
            if op == ">" and v[0] <= major:
                return False
            continue
        b = (major, int(minor_raw))
        c = _cmp(v, b)
        if op == ">=" and c < 0:
            return False
        if op == ">" and c <= 0:
            return False
        if op == "<=" and c > 0:
            return False
        if op == "<" and c >= 0:
            return False
        if op in ("==", "~=") and c != 0:
            # ~=3.10 means >=3.10,<4 ; == on X.Y.Z pins the minor
            if op == "~=" and c > 0 and v[0] == b[0]:
                continue
            return False
        if op == "!=" and c == 0:
            return False
    return True


def pick_python(requires: str, dotpythonversion: str) -> tuple[str, str]:
    """Return (X.Y, note). `.python-version` wins when we have an image for it."""
    dpv = (dotpythonversion or "").strip().splitlines()
    if dpv:
        m = re.match(r"^\s*v?(\d+\.\d+)", dpv[0].strip())
        if m and m.group(1) in IMAGES:
            return m.group(1), ".python-version"
    spec = (requires or "").strip()
    if not spec:
        return DEFAULT_PY, "default"
    order = PY_PREFERENCE
    for v in order:
        if spec_allows(spec, v):
            return v, "requires-python"
    return DEFAULT_PY, "requires-python-unsatisfiable"


# ---------------------------------------------------------------- log handling

def write_log(path: Path, text: str) -> None:
    b = text.encode("utf-8", "replace")
    if len(b) > LOG_CAP:
        half = LOG_CAP // 2
        b = b[:half] + b"\n\n...[truncated to 200 KB by pilot.py]...\n\n" + b[-half:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b)


# ---------------------------------------------------------------- classification

NATIVE = [
    "gcc: command not found", "cc1: ", "command 'gcc' failed", "command 'cc' failed",
    "fatal error: Python.h", "unable to execute 'gcc'", "no such file or directory: 'cc'",
    "error: command 'g++' failed", "ld: cannot find", "clang: error",
    "Microsoft Visual C++", ".h: No such file or directory", "Cargo, the Rust package manager",
    "cargo metadata", "CMake must be installed", "meson-python", "Failed building wheel",
    "Failed to build installable wheels", "error: linker", "libc-dev", "build-essential",
]
BACKEND = [
    "Getting requirements to build wheel", "BackendUnavailable",
    "No module named 'setuptools'", "hatchling", "setuptools_scm", "poetry.core",
    "flit_core", "maturin", "scikit-build", "Failed to build", "build backend",
]
LOCKBAD = [
    "needs to be updated", "lockfile", "lock file", "No solution found", "is not consistent",
    "does not match", "Failed to parse", "not found in the package registry",
    "was not found in the package index", "pyproject.toml changed significantly",
    "run `uv lock`", "poetry lock", "THESE PACKAGES DO NOT MATCH THE HASHES",
    "Distribution not found", "No matching distribution",
]
PYVER = [
    "requires Python", "Requires-Python", "python_requires", "requires-python",
    "The Python request", "no interpreter found", "is not supported by",
    "SyntaxError", "unsupported operand", "requires a different Python",
]
NETWORK = [
    "Temporary failure in name resolution", "Name or service not known",
    "Max retries exceeded", "NewConnectionError", "gaierror", "urlopen error",
    "Connection refused", "Failed to establish a new connection", "nodename nor servname",
    "ConnectTimeout", "network is unreachable", "Network is unreachable",
    "getaddrinfo", "SSLError", "ProxyError",
]
SECRET = [
    "API_KEY", "API key", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "environment variable",
    "credentials", "not authenticated", "AuthenticationError", "token is required",
    "KeyError: 'OPENAI", "Missing required", "GITHUB_TOKEN",
]


def _hits(text: str, needles: list[str]) -> str | None:
    for n in needles:
        if n in text:
            return n
    return None


def classify(phase: str, exit_code: int, install_log: str, collect_log: str,
             run_log: str) -> tuple[str, str]:
    """(failure_class, evidence) for the first phase that failed. phase in
    clone|install|collect|run|none."""
    if phase == "none":
        return "", ""
    if exit_code == 124:
        return "timeout", f"{phase} exceeded its cap"
    if phase == "clone":
        return "other", "clone/checkout failed"
    text = {"install": install_log, "collect": collect_log, "run": run_log}[phase]
    tail = text[-40000:]
    if phase == "install":
        if "===UNPINNED===" in text:
            return "no-lock", "requirements file is not fully pinned"
        if "===NOLOCK===" in text:
            return "no-lock", "declared lockfile absent at the base commit"
        for cls, needles in (("python-version", PYVER), ("lock-unresolvable", LOCKBAD),
                             ("native-deps", NATIVE), ("build-backend", BACKEND)):
            h = _hits(tail, needles)
            if h:
                return cls, h
        h = _hits(tail, NETWORK)
        if h:
            return "other", f"network failure during install: {h}"
        return "other", "install failed, no known signature"
    # collect / run
    h = _hits(tail, NETWORK)
    if h:
        return "network-at-test-time", h
    h = _hits(tail, SECRET)
    if h:
        return "env-var/secret required", h
    if phase == "collect":
        return "collection-error", "pytest --collect-only did not succeed"
    if "ERROR collecting" in tail or "errors during collection" in tail:
        return "collection-error", "collection errors in the run phase"
    h = _hits(tail, NATIVE)
    if h:
        return "native-deps", h
    h = _hits(tail, PYVER)
    if h:
        return "python-version", h
    return "other", "test run reached no verdict"


COLLECTED_RE = [
    re.compile(r"^(\d+)\s+tests? collected", re.M),
    re.compile(r"collected (\d+) items", re.M),
    re.compile(r"^(\d+)/(\d+) tests collected", re.M),
]


def parse_collected(text: str) -> int:
    best = 0
    for rx in COLLECTED_RE:
        for m in rx.finditer(text):
            best = max(best, int(m.group(1)))
    return best


def parse_verdict(text: str) -> tuple[int, int, int, bool]:
    """(passed, failed, errored, saw_summary) from the pytest summary line."""
    tail = text[-8000:]
    counts = {}
    saw = False
    for m in re.finditer(r"(\d+) (passed|failed|error|errors|xfailed|xpassed|skipped|deselected)",
                         tail):
        n, word = int(m.group(1)), m.group(2)
        if word in ("error", "errors"):
            word = "errored"
        counts[word] = max(counts.get(word, 0), n)
        saw = True
    if not saw and re.search(r"no tests ran", tail):
        saw = True
    return counts.get("passed", 0), counts.get("failed", 0), counts.get("errored", 0), saw


# ---------------------------------------------------------------- docker plumbing

def sh(cmd: list[str], timeout: int | None = None, stdin: str | None = None
       ) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, input=stdin, capture_output=True, text=True,
                           timeout=timeout, errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"") if isinstance(e.stdout, bytes) else (e.stdout or "")
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        return 124, out + "\n[pilot.py] host-side timeout\n"


def docker_run(image: str, volume: str, script: str, cap: int, network: bool,
               extra: list[str] | None = None) -> tuple[int, str]:
    cmd = [
        "docker", "run", "--rm", "-i",
        "--memory", MEM, "--cpus", CPUS, "--pids-limit", "2048",
        "-v", f"{volume}:/w",
        "-v", f"{UV_CACHE_VOL}:/uvcache",
        "-v", f"{PIP_CACHE_VOL}:/pipcache",
        "-e", "HOME=/root", "-e", "PYTHONUNBUFFERED=1",
        "-e", "GIT_TERMINAL_PROMPT=0",
    ]
    if not network:
        cmd += ["--network", "none"]
    cmd += (extra or []) + [image, "timeout", "-k", "10", str(cap), "bash", "-s"]
    rc, out = sh(cmd, timeout=cap + 120, stdin=script)
    return rc, out


CLONE_SH = r"""
set -u
cd /w
rm -rf repo
git clone --filter=blob:none --quiet https://github.com/{repo}.git repo 2>&1 || exit 20
cd repo
git checkout --quiet --force {sha} 2>&1 || exit 21
echo "===PYVER==="
cat .python-version 2>/dev/null || true
echo "===REQPY==="
grep -m1 -E '^\s*requires-python' pyproject.toml 2>/dev/null || true
grep -m1 -E '^\s*python_requires' setup.cfg 2>/dev/null || true
echo "===LOCKS==="
ls -1 uv.lock poetry.lock pdm.lock Pipfile.lock requirements*.txt 2>/dev/null || true
echo "===CLONE_OK==="
"""

INSTALL_SH = r"""
set -u
cd /w/repo
export UV_CACHE_DIR=/uvcache PIP_CACHE_DIR=/pipcache UV_LINK_MODE=copy
export UV_PYTHON_DOWNLOADS=never
export POETRY_VIRTUALENVS_IN_PROJECT=true PIPENV_VENV_IN_PROJECT=1
export PIPENV_IGNORE_VIRTUALENVS=1 PIPENV_NOSPIN=1 PATH="/root/.local/bin:$PATH"
echo "===PHASE=install kind={kind} file={lockfile} python=$(python3 -V)==="
case "{kind}" in
  uv.lock)
    # Everything below installs *from the lock* (--frozen). Extras and groups are resolved
    # in uv.lock, so syncing them is not a resolution -- but a default `uv sync` installs
    # neither, and then the test dependencies are simply absent. Ladder, widest first:
    # Each rung gets its own inner timeout: without one, a slow widest rung would eat the
    # whole 10-minute install cap and the fallbacks would never run.
    if timeout 300 uv sync --frozen --all-extras --all-groups --no-progress 2>&1; then :
    elif echo "===NOTE=== --all-extras --all-groups failed or timed out; retrying --all-groups" && \
         timeout 160 uv sync --frozen --all-groups --no-progress 2>&1; then :
    elif echo "===NOTE=== --all-groups failed or timed out; retrying the default sync" && \
         timeout 120 uv sync --frozen --no-progress 2>&1; then :
    else exit 30; fi
    ;;
  poetry.lock)
    uv tool install poetry 2>&1 || exit 32
    timeout 300 poetry install --no-interaction --no-ansi --all-extras 2>&1 || \
      timeout 200 poetry install --no-interaction --no-ansi 2>&1 || exit 30
    ;;
  Pipfile.lock)
    uv tool install pipenv 2>&1 || exit 32
    timeout 300 pipenv sync --dev 2>&1 || \
      timeout 200 pipenv sync 2>&1 || exit 30
    ;;
  pinned-requirements)
    if [ ! -f "{lockfile}" ]; then echo "===NOLOCK=== {lockfile} absent at this commit"; exit 42; fi
    python3 -c "
import sys
ls=[l.split('#')[0].strip() for l in open(sys.argv[1],errors='replace')]
bad=[s for s in ls if s and not s.startswith('-') and '==' not in s and '@' not in s]
print('===UNPINNED===',len(bad),bad[:8]) if bad else print('all requirement lines pinned')
sys.exit(1 if bad else 0)
" "{lockfile}" 2>&1 || exit 40
    uv venv .venv 2>&1 || exit 31
    uv pip install --python .venv/bin/python -r "{lockfile}" 2>&1 || exit 30
    if [ -f pyproject.toml ] || [ -f setup.py ]; then
      echo "===NOTE=== installing project with --no-deps (no resolution)"
      uv pip install --python .venv/bin/python --no-deps -e . 2>&1 || \
        echo "===NOTE=== editable --no-deps install of the project failed"
    fi
    ;;
  *)
    echo "unsupported lock kind: {kind}"; exit 39
    ;;
esac
test -x .venv/bin/python || exit 33
if ! .venv/bin/python -c "import pytest" 2>/dev/null; then
  echo "===NOTE=== pytest absent after lockfile install; installing pytest"
  uv pip install --python .venv/bin/python pytest 2>&1 || exit 34
fi
if .venv/bin/python -c "import pytest_timeout" 2>/dev/null; then
  touch /w/HAS_TIMEOUT
else
  echo "===NOTE=== pytest-timeout absent; installing it into the venv"
  if uv pip install --python .venv/bin/python pytest-timeout 2>&1; then
    touch /w/HAS_TIMEOUT
  else
    echo "===NOTE=== pytest-timeout install failed; running without --timeout"
  fi
fi
.venv/bin/python -m pytest --version 2>&1 | head -2
echo "===INSTALL_OK==="
"""

COLLECT_SH = r"""
set -u
cd /w/repo
.venv/bin/python -m pytest --collect-only -q 2>&1
rc=$?
echo "===COLLECT_RC=$rc==="
exit $rc
"""

RUN_SH = r"""
set -u
cd /w/repo
TO=""
[ -f /w/HAS_TIMEOUT ] && TO="--timeout=600"
echo "===CMD=pytest -q -x $TO -p no:cacheprovider==="
.venv/bin/python -m pytest -q -x $TO -p no:cacheprovider 2>&1
rc=$?
echo "===RUN_RC=$rc==="
exit $rc
"""


def vol_name(repo: str) -> str:
    return "pilot-" + re.sub(r"[^a-zA-Z0-9_.-]", "-", repo.replace("/", "__")).lower()


# ---------------------------------------------------------------- one repo

def run_repo(row: dict) -> dict:
    repo = row["repo"]
    sha = row["base_sha_of_first_sample_pr"]
    kind = row["lock_kind"]
    lockfile = row.get("lockfile_type", "")
    lockfile = lockfile.split(":", 1)[1] if lockfile.startswith("pinned:") else ""
    slug = repo.replace("/", "__")
    logs = LOGDIR / slug
    vol = vol_name(repo)
    notes: list[str] = []
    t0 = time.time()
    res = dict.fromkeys(COLUMNS, "")
    res.update(repo=repo, base_sha=sha, lock_kind=kind, python="", install_ok=0,
               collect_ok=0, collected_count=0, run_ok=0, passed=0, failed=0, errored=0)

    sh(["docker", "volume", "create", vol])
    try:
        rc, clone_out = docker_run(IMG.format(DEFAULT_PY), vol,
                                   CLONE_SH.format(repo=repo, sha=sha),
                                   CAP_INSTALL, network=True)
        if rc != 0 or "===CLONE_OK===" not in clone_out:
            write_log(logs / "install.log", clone_out)
            cls, ev = classify("clone", rc, clone_out, "", "")
            res.update(failure_class=cls, notes=f"clone/checkout rc={rc}; {ev}",
                       duration_s=round(time.time() - t0, 1), python="")
            return res

        dpv = clone_out.split("===PYVER===", 1)[1].split("===REQPY===", 1)[0].strip()
        reqpy_raw = clone_out.split("===REQPY===", 1)[1].split("===LOCKS===", 1)[0]
        m = re.search(r'["\']([^"\']+)["\']', reqpy_raw) or re.search(r"=\s*(.+)", reqpy_raw)
        reqpy = (m.group(1).strip() if m else "") or row.get("python_requires", "")
        py, why = pick_python(reqpy, dpv)
        res["python"] = py
        notes.append(f"py from {why}")
        if why == "requires-python-unsatisfiable":
            notes.append(f"requires-python={reqpy!r} matched no available image")

        if kind == "pinned-requirements" and not lockfile:
            lockfile = "requirements.txt"
        rc, install_out = docker_run(
            IMG.format(py), vol,
            INSTALL_SH.replace("{kind}", kind).replace("{lockfile}", lockfile),
            CAP_INSTALL, network=True)
        install_out = clone_out + "\n" + install_out
        write_log(logs / "install.log", install_out)
        for n in re.findall(r"===NOTE=== (.+)", install_out):
            notes.append(n.strip())
        if rc != 0 or "===INSTALL_OK===" not in install_out:
            cls, ev = classify("install", rc, install_out, "", "")
            res.update(failure_class=cls, notes="; ".join(notes + [f"install rc={rc}: {ev}"]),
                       duration_s=round(time.time() - t0, 1))
            return res
        res["install_ok"] = 1

        rc, collect_out = docker_run(IMG.format(py), vol, COLLECT_SH, CAP_COLLECT,
                                     network=False)
        write_log(logs / "collect.log", collect_out)
        res["collected_count"] = parse_collected(collect_out)
        if rc != 0:
            cls, ev = classify("collect", rc, install_out, collect_out, "")
            res.update(failure_class=cls,
                       notes="; ".join(notes + [f"collect rc={rc}: {ev}"]),
                       duration_s=round(time.time() - t0, 1))
            return res
        res["collect_ok"] = 1

        rc, run_out = docker_run(IMG.format(py), vol, RUN_SH, CAP_RUN, network=False)
        write_log(logs / "run.log", run_out)
        p, f, e, saw = parse_verdict(run_out)
        res.update(passed=p, failed=f, errored=e)
        if rc in (0, 1) and saw:
            res["run_ok"] = 1
            res["failure_class"] = "" if rc == 0 else "tests-failed-at-base"
        else:
            cls, ev = classify("run", rc, install_out, collect_out, run_out)
            res["failure_class"] = cls
            notes.append(f"run rc={rc}: {ev}")
        res.update(notes="; ".join(notes), duration_s=round(time.time() - t0, 1))
        return res
    finally:
        sh(["docker", "volume", "rm", "-f", vol], timeout=120)


# ---------------------------------------------------------------- driver

def append_result(res: dict) -> None:
    with open(_write_lock_path, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        new = not RESULTS.exists() or RESULTS.stat().st_size == 0
        with open(RESULTS, "a", newline="") as fh:
            w = csv.DictWriter(
                fh, fieldnames=COLUMNS, extrasaction="ignore", lineterminator="\n"
            )
            if new:
                w.writeheader()
            w.writerow(res)
            fh.flush()
            os.fsync(fh.fileno())
        fcntl.flock(lk, fcntl.LOCK_UN)


def done_repos() -> set[str]:
    if not RESULTS.exists():
        return set()
    with open(RESULTS, newline="") as fh:
        return {r["repo"] for r in csv.DictReader(fh) if r.get("repo")}


def build_images(needed: set[str]) -> None:
    def build(v: str) -> None:
        tag = IMG.format(v)
        if sh(["docker", "image", "inspect", tag])[0] == 0:
            return
        rc, out = sh(["docker", "build", "--build-arg", f"PYVER={v}", "-t", tag,
                      str(HERE)], timeout=1200)
        print(f"[pilot] built {tag}" if rc == 0
              else f"[pilot] WARNING: {tag} failed to build\n{out[-800:]}", flush=True)
    with ThreadPoolExecutor(max_workers=len(needed) or 1) as ex:
        list(ex.map(build, sorted(needed)))


def selfcheck() -> int:
    assert spec_allows(">=3.10,<3.14", "3.12")
    assert not spec_allows(">=3.10,<3.14", "3.14")
    assert not spec_allows(">=3.12", "3.11")
    assert spec_allows("==3.11.*", "3.11") and not spec_allows("==3.11.*", "3.12")
    assert spec_allows(">=3.10,<4.0", "3.13")
    assert spec_allows("==3.13.13", "3.13") and not spec_allows("==3.13.13", "3.12")
    assert pick_python(">=3.10,<3.14", "")[0] == "3.12"
    assert pick_python(">=3.13", "")[0] == "3.13", pick_python(">=3.13", "")
    assert pick_python(">=3.14.2", "")[0] == "3.14"
    assert pick_python("", "")[0] == "3.12"
    assert pick_python(">=3.9", "3.10\n")[0] == "3.10"
    assert pick_python(">=3.9", "3.13.1")[0] == "3.13"
    assert parse_collected("collected 41 items\n41 tests collected in 0.5s") == 41
    assert parse_verdict("== 3 failed, 12 passed, 1 error in 2s ==") == (12, 3, 1, True)
    assert parse_verdict("== 5 passed in 1s ==")[:3] == (5, 0, 0)
    assert classify("install", 124, "", "", "")[0] == "timeout"
    assert classify("install", 30, "fatal error: Python.h missing", "", "")[0] == "native-deps"
    assert classify("install", 30, "x\n===UNPINNED=== 3", "", "")[0] == "no-lock"
    assert classify("install", 30, "uv.lock needs to be updated", "", "")[0] == "lock-unresolvable"
    assert classify("run", 2, "", "", "Max retries exceeded")[0] == "network-at-test-time"
    assert classify("run", 2, "", "", "KeyError: 'OPENAI_API_KEY'")[0] == "env-var/secret required"
    assert classify("collect", 2, "", "ERROR collecting tests/x.py", "")[0] == "collection-error"
    assert classify("none", 0, "", "", "") == ("", "")
    assert vol_name("Foo/Bar_Baz") == "pilot-foo__bar_baz"
    print("selfcheck OK")
    return 0


def summary(md: bool = False) -> int:
    """Funnel counts over whatever results.csv holds right now. --md emits markdown,
    so the numbers in README.md are generated from the data, never typed."""
    import collections
    rows = list(csv.DictReader(open(RESULTS, newline=""))) if RESULTS.exists() else []
    n = len(rows)
    if not n:
        print("no results yet")
        return 0
    i = sum(int(r["install_ok"]) for r in rows)
    c = sum(int(r["collect_ok"]) for r in rows)
    ru = sum(int(r["run_ok"]) for r in rows)
    b = sum(
        int(r["install_ok"])
        and int(r["collect_ok"])
        and int(r["run_ok"])
        and int(r["errored"]) == 0
        and int(r["passed"]) + int(r["failed"]) >= 1
        for r in rows
    )
    g = sum(
        int(r["install_ok"])
        and int(r["collect_ok"])
        and int(r["run_ok"])
        and int(r["errored"]) == 0
        and int(r["failed"]) == 0
        and int(r["passed"]) >= 1
        for r in rows
    )
    cls_counts = collections.Counter(r["failure_class"] or "clean-pass" for r in rows)
    kinds = sorted({r["lock_kind"] for r in rows})
    by = collections.Counter((r["lock_kind"], int(r["run_ok"])) for r in rows)
    tests = sum(int(r["collected_count"] or 0) for r in rows)
    if not md:
        print(f"attempted {n}  install_ok {i} ({i/n:.0%})  collect_ok {c} ({c/n:.0%})  "
              f"run_ok {ru} ({ru/n:.0%})  buildable {b} ({b/n:.0%})  "
              f"green {g} ({g/n:.0%})  tests collected {tests}")
        for cl, k in cls_counts.most_common():
            print(f"  {k:3d}  {cl}")
        for kind in kinds:
            tot = sum(v for (k, _), v in by.items() if k == kind)
            print(f"  lock_kind {kind}: {by[(kind, 1)]}/{tot} reached a verdict")
        return 0
    print(f"| step | n | share of attempted |\n|---|---:|---:|")
    print(f"| attempted | {n} | — |")
    print(f"| `install_ok` | {i} | {i/n:.0%} |")
    print(f"| `collect_ok` | {c} | {c/n:.0%} |")
    print(f"| **`run_ok` (reached a verdict)** | **{ru}** | **{ru/n:.0%}** |")
    print(f"| **strict buildable** | **{b}** | **{b/n:.0%}** |")
    print(f"| fully green with ≥1 executed test | {g} | {g/n:.0%} |")
    result = "did not fire" if b / n >= 0.30 else "fired"
    print(f"\n**Verdict:** strict buildability is **{b}/{n} ({b/n:.0%})**; the 30% "
          f"falsifier **{result}**.")
    print(f"\nTests collected in total, including partial collections that then "
          f"errored: **{tests}**.\n")
    print("| failure_class | n |\n|---|---:|")
    for cl, k in cls_counts.most_common():
        print(f"| `{cl}` | {k} |")
    print("\n| lock_kind | reached a verdict | attempted |\n|---|---:|---:|")
    for kind in kinds:
        tot = sum(v for (k, _), v in by.items() if k == kind)
        print(f"| `{kind}` | {by[(kind, 1)]} | {tot} |")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--csv", default=str(HERE.parent / "corpus" / "candidates-pilot-100.csv")
    )
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--repo", default="")
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        return selfcheck()
    if a.summary:
        return summary(a.md)

    with open(a.csv, newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("repo")]
    if a.repo:
        rows = [r for r in rows if r["repo"] == a.repo]
    already = done_repos()
    todo = [r for r in rows if r["repo"] not in already]
    if a.limit:
        todo = todo[:a.limit]
    print(f"[pilot] {len(rows)} candidates, {len(already)} already done, "
          f"{len(todo)} to run, jobs={a.jobs}", flush=True)
    if not todo:
        return 0
    build_images(set(IMAGES))   # .python-version can name a version the CSV does not

    def one(r: dict) -> None:
        t = time.time()
        print(f"[pilot] START {r['repo']}", flush=True)
        try:
            res = run_repo(r)
        except Exception as exc:  # never lose a row
            res = dict.fromkeys(COLUMNS, "")
            res.update(repo=r["repo"], base_sha=r["base_sha_of_first_sample_pr"],
                       lock_kind=r["lock_kind"], install_ok=0, collect_ok=0,
                       collected_count=0, run_ok=0, passed=0, failed=0, errored=0,
                       duration_s=round(time.time() - t, 1), failure_class="other",
                       notes=f"harness exception: {type(exc).__name__}: {exc}"[:300])
        append_result(res)
        print(f"[pilot] DONE  {res['repo']} install={res['install_ok']} "
              f"collect={res['collect_ok']} run={res['run_ok']} "
              f"class={res['failure_class']} {res['duration_s']}s", flush=True)

    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        list(ex.map(one, todo))
    print("[pilot] all done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
