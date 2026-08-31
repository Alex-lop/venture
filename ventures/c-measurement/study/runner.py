#!/usr/bin/env python3
"""Track M differential verifier: run each agent-PR's own tests on base and candidate.

For every qualifying merged agent-trailered PR in a *buildable* repo (the pilot's
run_ok set), check out the PR's base commit in a container, install from the lockfile,
run the PR's test files that already exist there (-> pre_patch_outcome), apply ONLY the
PR's test-path changes, run exactly the PR's test files twice, then check out the merge
commit, re-install, run the same files twice again, and classify every test with
SWE-bench's vocabulary (FAIL_TO_PASS / PASS_TO_PASS / UNRESOLVED).

Two observations per side: an id whose observations disagree is `flaky` and resolves to
nothing. A fatal run on either side is UNRESOLVED for the PR *and* for every one of its
test rows. Zero FAIL_TO_PASS is NON_DISCRIMINATING only when no row was left unresolved.

Everything untrusted runs in docker: the build/install/run logic, the image, the
python-version choice, the caps and the volume cleanup are imported verbatim from
../pilot/pilot.py.  No host path is ever mounted into a container.

Usage:  python3 runner.py [--jobs 3] [--smoke 2] [--repo O/R[,O/R]] [--limit N]
        python3 runner.py --selfcheck     # no docker, no network
        python3 runner.py --summary [--md]
"""
from __future__ import annotations

import argparse
import csv
import fcntl
import json
import os
import re
import shlex
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from xml.etree import ElementTree

HERE = Path(__file__).resolve().parent
PILOT = HERE.parent / "pilot"
CORPUS = HERE.parent / "corpus"

# The brief's container budget. pilot.py reads these at import time.
os.environ.setdefault("PILOT_MEM", "4g")
os.environ.setdefault("PILOT_CPUS", "2")
sys.path.insert(0, str(PILOT))
import pilot  # noqa: E402  (path must be set first)

PR_CSV = HERE / "results-prs.csv"
TEST_CSV = HERE / "results-tests.csv"
LOGDIR = HERE / "logs"
RAWDIR = HERE / "raw"
LOCK = HERE / ".results.lock"

PR_COLUMNS = [
    "repo", "pr", "base_sha", "merge_sha", "merged_at", "n_tests", "n_f2p", "n_p2p",
    "n_unresolved", "pr_verdict", "unresolved_reason", "cc_type", "pr_trailer_kinds",
    "base_is_merge_first_parent", "unmatched_testish_files", "changed_lines",
    "test_files_new", "test_files_modified", "infra_changed", "repo_trailer_kinds",
    "duration_s",
]
TEST_COLUMNS = ["repo", "pr", "test_id", "pre_patch_outcome", "base_outcome",
                "candidate_outcome", "verdict"]

CAP_CLONE = 900     # clone + fetch + diff + apply, network on
CAP_RUN = 900       # 15 minutes per pytest invocation (the brief's cap)
MAX_JUNIT_BYTES = 512_000   # nemisis/junit.py's cap, kept identical
CACHE_CAP_MB = int(os.environ.get("STUDY_CACHE_CAP_MB", "8000"))


# ---------------------------------------------------------------- PR file rules

def is_test_path(path: str) -> bool:
    """The corpus README's test-path rule, verbatim: tests/, test_*.py, *_test.py,
    conftest.py."""
    parts = path.split("/")
    if "tests" in parts[:-1]:
        return True
    base = parts[-1]
    return bool(re.match(r"^test_.*\.py$", base) or re.match(r"^.*_test\.py$", base)
                or base == "conftest.py")


def is_runnable_test_module(path: str) -> bool:
    """A path we can hand to pytest as an argument. conftest.py and data files under
    tests/ are patched but never run directly."""
    base = path.split("/")[-1]
    return bool(re.match(r"^test_.*\.py$", base) or re.match(r"^.*_test\.py$", base))


def is_infra(path: str) -> bool:
    """Test-infrastructure change: applied with the tests, and flagged, because it
    moves the goalposts of the base run."""
    parts = path.split("/")
    return parts[-1] in ("conftest.py", "pytest.ini", "tox.ini", "setup.cfg") \
        or "fixtures" in parts[:-1]


def is_testish_path(path: str) -> bool:
    """The *auditor* rule: deliberately wider than `is_test_path`, and never used to
    select anything to run. Every miss of the strict path rule pushes a PR toward
    NON_DISCRIMINATING, so `unmatched_testish_files` (testish and not test) is the
    published upper bound on that error: `test/` singular, Django `tests.py`,
    `spec_*.py`, `check_*.py`, `testing/`, `src/**/mytest.py`."""
    if not path.endswith((".py", ".pyi")):
        return False
    base = path.split("/")[-1]
    return "test" in path.lower() or bool(re.match(r"^(spec|check)_.*\.pyi?$", base))


CC_TYPES = {"fix", "feat", "refactor", "docs", "test", "chore", "perf", "build", "ci",
            "style", "revert"}
CC_RE = re.compile(r"^\s*([a-zA-Z]{2,10})(\([^)]*\))?!?:")


def cc_type(title: str) -> str:
    """The conventional-commit type of the PR title, or "" when it carries none.
    precedents.md Objection 3: the headline is restricted to `fix` PRs, because a
    refactor / docs / coverage PR *should* ship tests that pass on both sides. Only the
    leading type token is read; no other part of the title is stored."""
    m = CC_RE.match(title or "")
    t = (m.group(1).lower() if m else "")
    return t if t in CC_TYPES else ""


# The corpus's ten agent trailers, regexes verbatim from ../corpus/scripts/widen.py.
# Only the *key* ("copilot") ever reaches a tracked file — never the trailer line, which
# carries an author login and email.
VERBATIM = {
    "claude-coauthor": re.compile(r"co-authored-by:\s*claude", re.I),
    "claude-code-gen": re.compile(r"generated with \[?claude code", re.I),
    "codex": re.compile(r"co-authored-by:\s*codex", re.I),
    "cursor": re.compile(r"co-authored-by:\s*cursor", re.I),
    "copilot": re.compile(r"co-authored-by:\s*copilot", re.I),
    "devin": re.compile(r"co-authored-by:\s*devin-ai-integration", re.I),
    "openhands": re.compile(r"co-authored-by:\s*openhands", re.I),
    "sweep": re.compile(r"co-authored-by:\s*sweep", re.I),
    "aider": re.compile(r"\[aider\]", re.I),
    "robot-gen": re.compile("\U0001F916 generated with", re.I),
}


def trailers_in(text: str) -> set[str]:
    return {k for k, rx in VERBATIM.items() if rx.search(text or "")}


# ---------------------------------------------------------------- junit parsing

def _tag(el: ElementTree.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def _outcome(case: ElementTree.Element) -> str:
    """nemisis/junit.py's _outcome, minus the nemisis marker property: an ERROR is
    absence of evidence, and it wins over every other child."""
    children = {_tag(c) for c in case}
    if "error" in children:
        return "error"
    if "skipped" in children:
        return "skipped"
    if "failure" in children:
        return "failed"
    return "passed"


def parse_junit(xml_text: str, rc: int, timed_out: bool
                ) -> tuple[dict[str, str], set[str], str]:
    """(outcomes by test_id, modules that failed to collect, fatal reason or "").

    Fail-closed, per nemisis/junit.py: a timeout, a pytest exit code that means the
    session itself broke (2 interrupted, 3 internal, 4 usage, 5 nothing collected),
    an absent/oversized/unparseable report, or a duplicate test id is *absence of
    evidence*, not a result.
    """
    if timed_out:
        return {}, set(), "timeout"
    if rc in (2, 3, 4):
        return {}, set(), f"pytest exit {rc}"
    if rc == 5:
        return {}, set(), "no tests collected"
    body = xml_text.strip()
    if not body:
        return {}, set(), "no junit xml"
    if len(body.encode("utf-8", "replace")) > MAX_JUNIT_BYTES:
        return {}, set(), "junit xml over 512 KB"
    try:
        root = ElementTree.fromstring(body)
    except ElementTree.ParseError:
        return {}, set(), "junit xml unparseable"

    outcomes: dict[str, str] = {}
    err_modules: set[str] = set()
    for case in (e for e in root.iter() if _tag(e) == "testcase"):
        cls = case.get("classname") or ""
        name = case.get("name") or ""
        if not cls:
            # pytest emits a classname-less <testcase name="dotted.module"> carrying a
            # <error message="collection failure"> when a module will not import.
            if _outcome(case) == "error":
                err_modules.add(name)
            continue
        tid = f"{cls}::{name}"
        if tid in outcomes:
            outcomes[tid] = "error"     # duplicate ids are untrusted structure
            continue
        outcomes[tid] = _outcome(case)
    return outcomes, err_modules, ""


def side_outcome(tid: str, outcomes: dict[str, str], err_modules: set[str],
                 fatal: str) -> str:
    if fatal:
        return "error"
    if tid in outcomes:
        return outcomes[tid]
    module = tid.split("::", 1)[0]
    if any(module == m or module.startswith(m + ".") for m in err_modules):
        return "error"      # the whole module failed to collect on this side
    return "missing"


Obs = tuple  # (outcomes, err_modules, fatal) — one pytest observation of one side


def side2(tid: str, o1: Obs, o2: Obs) -> str:
    """One side, observed twice (precedents.md Objection 4 / Meta TestGen-LLM's 18-point
    built-vs-reliable gap). Two observations that disagree are `flaky`, which no cell of
    the verdict table resolves."""
    a, b = side_outcome(tid, *o1), side_outcome(tid, *o2)
    return a if a == b else "flaky"


def verdict(base: str, cand: str) -> str:
    """SWE-bench vocabulary over nemisis semantics. Everything that is not one of the
    two resolved cells is UNRESOLVED; the (base, candidate) pair in the same row is
    the reason."""
    if base in ("failed", "error") and cand == "passed":
        return "FAIL_TO_PASS"
    if base == "passed" and cand == "passed":
        return "PASS_TO_PASS"
    return "UNRESOLVED"


def build_rows(repo: str, num: str, b1: Obs, b2: Obs, c1: Obs, c2: Obs, pre: Obs
               ) -> list[dict]:
    """Every test row for one PR. A fatal side is absence of evidence for *every* id in
    the run, so those rows say UNRESOLVED too: `results-tests.csv` must never be able to
    state something `results-prs.csv` contradicts, and no test-level aggregate may count
    a broken environment as discriminating evidence."""
    fatal = b1[2] or b2[2] or c1[2] or c2[2]
    rows = []
    for tid in sorted(set(b1[0]) | set(b2[0]) | set(c1[0]) | set(c2[0])):
        b, c = side2(tid, b1, b2), side2(tid, c1, c2)
        p = side_outcome(tid, *pre)
        rows.append({"repo": repo, "pr": num, "test_id": tid,
                     "pre_patch_outcome": "absent" if p == "missing" else p,
                     "base_outcome": b, "candidate_outcome": c,
                     "verdict": "UNRESOLVED" if fatal else verdict(b, c)})
    return rows


def pr_verdict_of(n_f2p: int, n_p2p: int, n_unres: int, b_fatal: str, c_fatal: str
                  ) -> tuple[str, str]:
    """(pr_verdict, unresolved_reason). Zero FAIL_TO_PASS is evidence *of*
    non-discrimination only when every row resolved — 1 PASS_TO_PASS beside 40
    no-evidence rows is not the headline verdict, it is partial evidence."""
    if b_fatal or c_fatal:
        return "UNRESOLVED", (f"base_run: {b_fatal}" if b_fatal
                              else f"candidate_run: {c_fatal}")
    if n_f2p:
        return "DISCRIMINATING", ""
    if n_p2p and not n_unres:
        return "NON_DISCRIMINATING", ""
    if n_p2p:
        return "UNRESOLVED", f"partial evidence: {n_unres} unresolved rows"
    return "UNRESOLVED", "no test resolved on both sides"


# ---------------------------------------------------------------- github metadata

def gh_json(path: str, cache: Path, jsonlines: bool = False, jq: str = "") -> object:
    """`gh api` GET, cached on disk. Raw dumps live under study/raw/ (gitignored)
    because PR payloads carry author logins."""
    if cache.exists() and cache.stat().st_size:
        text = cache.read_text()
    else:
        cmd = ["gh", "api", path]
        if jq:
            cmd += ["--paginate", "--jq", jq]
        rc, text = pilot.sh(cmd, timeout=180)
        if rc != 0:
            raise RuntimeError(f"gh api {path} rc={rc}: {text[-300:]}")
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(text)
    if jsonlines:
        return [json.loads(x) for x in text.splitlines() if x.strip()]
    return json.loads(text)


def pr_metadata(repo: str, num: str) -> dict:
    slug = repo.replace("/", "__")
    pr = gh_json(f"repos/{repo}/pulls/{num}", RAWDIR / slug / f"pr{num}.json")
    files = gh_json(
        f"repos/{repo}/pulls/{num}/files?per_page=100",
        RAWDIR / slug / f"pr{num}-files.jsonl", jsonlines=True,
        jq=".[] | {filename, previous_filename, status, additions, deletions}")
    kinds = trailers_in(pr.get("body") or "")
    if not kinds:
        # The corpus accepted a trailer in the body *or* in a commit message; only the
        # body is in the PR payload, so the commit messages are fetched when it is not
        # there. Only `.commit.message` is requested, so no author email is ever stored.
        try:
            msgs = gh_json(f"repos/{repo}/pulls/{num}/commits?per_page=100",
                           RAWDIR / slug / f"pr{num}-commits.jsonl", jsonlines=True,
                           jq=".[] | {message: .commit.message}")
            kinds = trailers_in("\n".join(m.get("message") or "" for m in msgs))
        except Exception:
            kinds = set()       # an unavailable commit list is "" (unknown), not a PR loss
    return {
        "base_sha": pr["base"]["sha"],
        "merge_sha": pr.get("merge_commit_sha") or "",
        "merged_at": pr.get("merged_at") or "",
        "changed_lines": int(pr.get("additions", 0)) + int(pr.get("deletions", 0)),
        "cc_type": cc_type(pr.get("title") or ""),
        "pr_trailer_kinds": ";".join(sorted(kinds)),
        "files": files,
    }


# ---------------------------------------------------------------- container steps

CLONE_SH = r"""
set -u
cd /w
rm -rf repo
git clone --filter=blob:none --quiet https://github.com/{repo}.git repo 2>&1 || exit 20
cd repo
git fetch --quiet origin {base} {merge} 2>&1 || true
git checkout --quiet --force {base} 2>&1 || exit 21
echo "===PYVER==="
cat .python-version 2>/dev/null || true
echo "===REQPY==="
grep -m1 -E '^\s*requires-python' pyproject.toml 2>/dev/null || true
grep -m1 -E '^\s*python_requires' setup.cfg 2>/dev/null || true
echo "===FIRSTPARENT==="
git rev-parse --verify --quiet {merge}^1 || true
echo "===BASEFILES==="
for f in {files}; do [ -f "$f" ] && echo "$f"; done
echo "===DIFF==="
git diff {base} {merge} -- {paths} > /w/test.patch 2>&1 || exit 22
echo "patch bytes: $(wc -c < /w/test.patch)"
echo "===CLONE_OK==="
"""

# Applied *after* the pre-patch base run, so the base's own greenness is observed on the
# tree the maintainers actually had. Network is on because `git apply --3way` may have to
# fetch a blob the --filter=blob:none clone left behind; no untrusted code runs here.
APPLY_SH = r"""
set -u
cd /w/repo
if [ -s /w/test.patch ]; then
  git apply --whitespace=nowarn /w/test.patch 2>&1 \
    || { echo "===NOTE=== plain git apply failed; retrying --3way"; \
         git apply --3way --whitespace=nowarn /w/test.patch 2>&1; } \
    || exit 23
else
  echo "===NOTE=== empty test patch: base and merge agree on every PR test path"
fi
echo "===APPLY_OK==="
"""

CAND_SH = r"""
set -u
cd /w/repo
git checkout --quiet --force {merge} 2>&1 || exit 24
git clean -xffdq 2>&1 || true
test -e .venv && exit 25
echo "===CAND_OK==="
"""

RUN_SH = r"""
set -u
cd /w/repo
TO=""
[ -f /w/HAS_TIMEOUT ] && TO="--timeout=600"
rm -f /w/{tag}.xml
echo "===CMD=pytest {files} -q $TO -p no:cacheprovider --continue-on-collection-errors==="
.venv/bin/python -m pytest {files} -q $TO -p no:cacheprovider \
  --continue-on-collection-errors --junitxml=/w/{tag}.xml -o junit_family=xunit2 2>&1 \
  | tail -c 30000
rc=${PIPESTATUS[0]}
echo "===RUN_RC=$rc==="
echo "===JUNIT_BEGIN==="
head -c 512001 /w/{tag}.xml 2>/dev/null || true
echo ""
echo "===JUNIT_END==="
"""


def extract(text: str, begin: str, end: str) -> str:
    if begin not in text or end not in text:
        return ""
    return text.split(begin)[-1].split(end)[0]


def run_rc(text: str, docker_rc: int) -> int:
    m = re.findall(r"===RUN_RC=(-?\d+)===", text)
    return int(m[-1]) if m else docker_rc


def pytest_phase(img: str, vol: str, tag: str, files: list[str], log: Path
                 ) -> tuple[dict[str, str], set[str], str]:
    script = RUN_SH.replace("{tag}", tag).replace(
        "{files}", " ".join(shlex.quote(f) for f in files))
    rc, out = pilot.docker_run(img, vol, script, CAP_RUN, network=False)
    xml = extract(out, "===JUNIT_BEGIN===", "===JUNIT_END===")
    pilot.write_log(log, out.replace(xml, f"\n[{len(xml)} bytes of junit xml elided]\n")
                    if xml else out)
    return parse_junit(xml, run_rc(out, rc), timed_out=(rc == 124))


def pytest_twice(img: str, vol: str, tag: str, files: list[str], logs: Path
                 ) -> tuple[Obs, Obs]:
    """Two observations of one side. Objection 4's remedy: the pair is compared per test
    id in `side2`, and disagreement is UNRESOLVED rather than a pass."""
    return (pytest_phase(img, vol, tag, files, logs / f"run-{tag}.log"),
            pytest_phase(img, vol, tag + "2", files, logs / f"run-{tag}2.log"))


# ---------------------------------------------------------------- one PR

def blank_pr(repo: str, num: str) -> dict:
    row = dict.fromkeys(PR_COLUMNS, "")
    row.update(repo=repo, pr=num, n_tests=0, n_f2p=0, n_p2p=0, n_unresolved=0,
               infra_changed=0, test_files_new=0, test_files_modified=0,
               changed_lines=0, unmatched_testish_files=0, pr_verdict="UNRESOLVED")
    return row


def run_pr(repo_row: dict, num: str) -> tuple[dict, list[dict]]:
    repo = repo_row["repo"]
    py = repo_row["python"] or pilot.DEFAULT_PY
    kind = repo_row["lock_kind"]
    lockfile = repo_row.get("lockfile_type", "")
    lockfile = lockfile.split(":", 1)[1] if lockfile.startswith("pinned:") else ""
    if kind == "pinned-requirements" and not lockfile:
        lockfile = "requirements.txt"
    slug = repo.replace("/", "__")
    logs = LOGDIR / f"{slug}__pr{num}"
    vol = f"{pilot.vol_name(repo)}-pr{num}"
    img = pilot.IMG.format(py)
    t0 = time.time()
    res = blank_pr(repo, num)
    res["repo_trailer_kinds"] = repo_row.get("trailer_kinds", "")

    def done(reason: str = "", vd: str = "UNRESOLVED") -> tuple[dict, list[dict]]:
        res.update(pr_verdict=vd, unresolved_reason=reason,
                   duration_s=round(time.time() - t0, 1))
        return res, []

    try:
        meta = pr_metadata(repo, num)
    except Exception as exc:
        return done(f"api_error: {type(exc).__name__}")
    res.update(base_sha=meta["base_sha"], merge_sha=meta["merge_sha"],
               merged_at=meta["merged_at"], changed_lines=meta["changed_lines"],
               cc_type=meta["cc_type"], pr_trailer_kinds=meta["pr_trailer_kinds"])
    if not meta["merge_sha"]:
        return done("no merge_commit_sha")

    patch_paths, run_files = [], []
    for f in meta["files"]:
        name = f["filename"]
        if not is_test_path(name):
            if is_infra(name):
                res["infra_changed"] = 1
            if is_testish_path(name) and f["status"] != "removed":
                res["unmatched_testish_files"] += 1
            continue
        if is_infra(name):
            res["infra_changed"] = 1
        if f["status"] == "removed":
            continue
        patch_paths.append(name)
        if f.get("previous_filename"):
            patch_paths.append(f["previous_filename"])
        if is_runnable_test_module(name):
            run_files.append(name)
            if f["status"] == "added":
                res["test_files_new"] += 1
            else:
                res["test_files_modified"] += 1
    if not run_files:
        return done("no runnable test file (test paths were conftest/fixtures only)")

    pilot.sh(["docker", "volume", "create", vol])
    try:
        script = (CLONE_SH.replace("{repo}", repo).replace("{base}", meta["base_sha"])
                  .replace("{merge}", meta["merge_sha"])
                  .replace("{files}", " ".join(shlex.quote(f) for f in run_files))
                  .replace("{paths}", " ".join(shlex.quote(p) for p in patch_paths)))
        rc, out = pilot.docker_run(img, vol, script, CAP_CLONE, network=True)
        pilot.write_log(logs / "clone.log", out)
        if rc != 0 or "===CLONE_OK===" not in out:
            reason = {20: "clone_failed", 21: "base_checkout_failed",
                      22: "diff_failed", 124: "clone_timeout"}.get(rc, f"clone_rc_{rc}")
            return done(reason)
        # The counterfactual Track M wants is the target branch immediately before the PR
        # landed = merge_commit_sha^1. base.sha is the base ref as of the PR's last sync;
        # where they differ, every intervening commit's effect is attributed to this PR.
        fp = extract(out, "===FIRSTPARENT===", "===BASEFILES===").strip()
        res["base_is_merge_first_parent"] = int(fp == meta["base_sha"]) if fp else ""
        want = set(run_files)
        pre_files = [f for f in (ln.strip() for ln in
                                 extract(out, "===BASEFILES===", "===DIFF===").splitlines())
                     if f in want]

        install = pilot.INSTALL_SH.replace("{kind}", kind).replace("{lockfile}", lockfile)
        rc, out = pilot.docker_run(img, vol, install, pilot.CAP_INSTALL, network=True)
        pilot.write_log(logs / "install-base.log", out)
        if rc != 0 or "===INSTALL_OK===" not in out:
            return done("install_failed_base" if rc != 124 else "install_timeout_base")

        # Objection 1's admission criterion, recorded rather than enforced: how each test
        # id behaved at the unpatched base, before the PR's test patch was applied.
        pre: Obs = ({}, set(), "") if not pre_files else pytest_phase(
            img, vol, "pre", pre_files, logs / "run-pre.log")
        if pre[2] == "no tests collected":
            # Fail-closed is right for the two sides being compared, but here pytest exit
            # 5 means the file existed at base and held no test yet -- that is `absent`,
            # not a broken base. Mislabelling it `error` would make a reader filtering on
            # base greenness discard legitimate FAIL_TO_PASS rows.
            pre = ({}, set(), "")

        rc, out = pilot.docker_run(img, vol, APPLY_SH, CAP_CLONE, network=True)
        pilot.write_log(logs / "apply.log", out)
        if rc != 0 or "===APPLY_OK===" not in out:
            return done("apply_failed" if rc != 124 else "apply_timeout")

        b1, b2 = pytest_twice(img, vol, "base", run_files, logs)

        rc, out = pilot.docker_run(img, vol, CAND_SH.replace("{merge}", meta["merge_sha"]),
                                   CAP_CLONE, network=True)
        pilot.write_log(logs / "candidate.log", out)
        if rc != 0 or "===CAND_OK===" not in out:
            return done("candidate_checkout_failed" if rc != 124 else "candidate_timeout")

        rc, out = pilot.docker_run(img, vol, install, pilot.CAP_INSTALL, network=True)
        pilot.write_log(logs / "install-candidate.log", out)
        if rc != 0 or "===INSTALL_OK===" not in out:
            return done("install_failed_candidate" if rc != 124
                        else "install_timeout_candidate")

        c1, c2 = pytest_twice(img, vol, "cand", run_files, logs)
    except Exception as exc:
        return done(f"harness_exception: {type(exc).__name__}")
    finally:
        pilot.sh(["docker", "volume", "rm", "-f", vol], timeout=180)

    rows = build_rows(repo, num, b1, b2, c1, c2, pre)
    res["n_tests"] = len(rows)
    res["n_f2p"] = sum(r["verdict"] == "FAIL_TO_PASS" for r in rows)
    res["n_p2p"] = sum(r["verdict"] == "PASS_TO_PASS" for r in rows)
    res["n_unresolved"] = sum(r["verdict"] == "UNRESOLVED" for r in rows)
    res["duration_s"] = round(time.time() - t0, 1)
    res["pr_verdict"], res["unresolved_reason"] = pr_verdict_of(
        res["n_f2p"], res["n_p2p"], res["n_unresolved"],
        b1[2] or b2[2], c1[2] or c2[2])
    return res, rows


# ---------------------------------------------------------------- driver

def append(writes: list[tuple[Path, list[str], list[dict]]]) -> None:
    """Both CSVs under one flock: the PR row is the resume key, so it must never land
    without the test rows it summarises."""
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        for path, columns, rows in writes:
            if not rows:
                continue
            fresh = not path.exists() or path.stat().st_size == 0
            with open(path, "a", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
                if fresh:
                    w.writeheader()
                w.writerows(rows)
                fh.flush()
                os.fsync(fh.fileno())
        fcntl.flock(lk, fcntl.LOCK_UN)


def done_prs() -> set[tuple[str, str]]:
    if not PR_CSV.exists():
        return set()
    with open(PR_CSV, newline="") as fh:
        return {(r["repo"], r["pr"]) for r in csv.DictReader(fh) if r.get("repo")}


def buildable() -> list[dict]:
    """The pilot's buildable set, joined to the corpus row. Ordered by suite size, so
    --smoke N is the N cheapest repos."""
    with open(CORPUS / "candidates-v2.csv", newline="") as fh:
        corpus = {r["repo"]: r for r in csv.DictReader(fh)}
    out = []
    with open(PILOT / "results.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            ok = (r["install_ok"] == "1" and r["collect_ok"] == "1" and r["run_ok"] == "1"
                  and int(r["errored"] or 0) == 0
                  and int(r["passed"] or 0) + int(r["failed"] or 0) >= 1)
            if ok and r["repo"] in corpus:
                row = dict(corpus[r["repo"]])
                row.update(python=r["python"], lock_kind=r["lock_kind"],
                           collected_count=int(r["collected_count"] or 0))
                out.append(row)
    return sorted(out, key=lambda r: r["collected_count"])


def cache_guard() -> None:
    """Per-PR work volumes are removed in `finally`; the shared uv cache is not, and it
    grows without bound (the pilot's 60-repo run left 40 GB in it). The brief's budget is
    20 GB of disk total and the six images are ~6 GB of that, so wipe the cache between
    runs when it is over the cap. Costs one re-download; never runs mid-pool."""
    img = pilot.IMG.format(pilot.DEFAULT_PY)
    mount = f"{pilot.UV_CACHE_VOL}:/uvcache"
    rc, out = pilot.sh(["docker", "run", "--rm", "-v", mount, img, "du", "-sm", "/uvcache"],
                       timeout=600)
    m = re.match(r"\s*(\d+)", out)
    mb = int(m.group(1)) if rc == 0 and m else 0
    print(f"[study] uv cache {mb} MB (cap {CACHE_CAP_MB} MB)", flush=True)
    if mb > CACHE_CAP_MB:
        pilot.sh(["docker", "run", "--rm", "-v", mount, img, "bash", "-c",
                  "rm -rf /uvcache/* /uvcache/.[!.]* 2>/dev/null; true"], timeout=900)
        print("[study] uv cache cleared", flush=True)


def selfcheck() -> int:
    assert is_test_path("tests/test_a.py") and is_test_path("src/pkg/tests/helper.py")
    assert is_test_path("test_top.py") and is_test_path("a/b_test.py")
    assert is_test_path("conftest.py") and is_test_path("tests/conftest.py")
    assert not is_test_path("src/app.py") and not is_test_path("testing/util.py")
    assert not is_test_path("tests.py")
    # the auditor rule catches exactly what the strict rule misses, and nothing to run
    for p in ("tests.py", "test/thing.py", "spec_parser.py", "check_api.py",
              "testing/util.py", "src/pkg/mytest.py"):
        assert is_testish_path(p) and not is_test_path(p), p
    assert not is_testish_path("src/app.py") and not is_testish_path("tests/data.json")
    assert is_testish_path("tests/test_a.py")     # testish is a superset, never a filter

    assert cc_type("fix: crash on empty input") == "fix"
    assert cc_type("feat(api)!: drop v1") == "feat"
    assert cc_type("Refactor: tidy") == "refactor"
    assert cc_type("bump deps") == "" and cc_type("wip: whatever") == ""
    assert cc_type("") == "" and cc_type("http://x: y") == ""
    assert trailers_in("Co-Authored-By: Claude <x@y>") == {"claude-coauthor"}
    assert trailers_in("\U0001F916 Generated with [Claude Code](u)") == {
        "claude-code-gen", "robot-gen"}
    assert trailers_in("no trailer here") == set()
    assert is_runnable_test_module("tests/test_a.py")
    assert not is_runnable_test_module("tests/conftest.py")
    assert not is_runnable_test_module("tests/data/fixture.json")
    assert is_infra("tests/conftest.py") and is_infra("setup.cfg")
    assert is_infra("tests/fixtures/x.json") and not is_infra("tests/test_a.py")

    xml = ('<testsuites><testsuite>'
           '<testcase classname="tests.test_ok" name="test_pass"/>'
           '<testcase classname="tests.test_ok" name="test_fail"><failure/></testcase>'
           '<testcase classname="tests.test_ok" name="test_err"><error/></testcase>'
           '<testcase classname="tests.test_ok" name="test_skip"><skipped/></testcase>'
           '<testcase classname="tests.test_ok.TestK" name="test_m"/>'
           '<testcase classname="" name="tests.test_broken">'
           '<error message="collection failure"/></testcase>'
           '</testsuite></testsuites>')
    o, em, fatal = parse_junit(xml, 1, False)
    assert not fatal and em == {"tests.test_broken"}, (em, fatal)
    assert o == {"tests.test_ok::test_pass": "passed", "tests.test_ok::test_fail": "failed",
                 "tests.test_ok::test_err": "error", "tests.test_ok::test_skip": "skipped",
                 "tests.test_ok.TestK::test_m": "passed"}, o
    # a <failure> that also carries an <error> is an error: nemisis's precedence
    o2, _, _ = parse_junit('<testsuite><testcase classname="m" name="t">'
                           '<failure/><error/></testcase></testsuite>', 1, False)
    assert o2 == {"m::t": "error"}, o2
    dup = ('<testsuite><testcase classname="m" name="t"/>'
           '<testcase classname="m" name="t"/></testsuite>')
    assert parse_junit(dup, 0, False)[0] == {"m::t": "error"}
    for bad_rc in (2, 3, 4, 5):
        assert parse_junit(xml, bad_rc, False)[2], bad_rc
    assert parse_junit(xml, 0, True)[2] == "timeout"
    assert parse_junit("", 0, False)[2] == "no junit xml"
    assert parse_junit("<not xml", 0, False)[2] == "junit xml unparseable"
    assert parse_junit("<a/>" + "x" * MAX_JUNIT_BYTES, 0, False)[2].startswith("junit xml over")

    # a module that would not collect on one side is an error there, not "missing"
    assert side_outcome("tests.test_broken::test_x", o, em, "") == "error"
    assert side_outcome("tests.test_broken.TestC::t", o, em, "") == "error"
    assert side_outcome("tests.test_other::t", o, em, "") == "missing"
    assert side_outcome("tests.test_ok::test_pass", o, em, "timeout") == "error"

    assert verdict("failed", "passed") == "FAIL_TO_PASS"
    assert verdict("error", "passed") == "FAIL_TO_PASS"
    assert verdict("passed", "passed") == "PASS_TO_PASS"
    for pair in (("passed", "failed"), ("failed", "failed"), ("passed", "error"),
                 ("missing", "passed"), ("passed", "missing"), ("skipped", "passed"),
                 ("passed", "skipped"), ("error", "error")):
        assert verdict(*pair) == "UNRESOLVED", pair
    # two observations of a side: disagreement is `flaky`, and no cell resolves it
    ok = ({"m::t": "passed"}, set(), "")
    bad = ({"m::t": "failed"}, set(), "")
    assert side2("m::t", ok, ok) == "passed" and side2("m::t", ok, bad) == "flaky"
    assert verdict("flaky", "passed") == "UNRESOLVED"
    assert verdict("passed", "flaky") == "UNRESOLVED"

    # a fatal side stamps UNRESOLVED on every *test row*, not only on the PR row
    none: Obs = ({}, set(), "")
    fat = ({}, set(), "timeout")
    r = build_rows("o/r", "1", fat, fat, ok, ok, none)
    assert [x["verdict"] for x in r] == ["UNRESOLVED"], r
    assert r[0]["base_outcome"] == "error" and r[0]["pre_patch_outcome"] == "absent"
    r2 = build_rows("o/r", "1", bad, bad, ok, ok, ({"m::t": "passed"}, set(), ""))
    assert r2[0]["verdict"] == "FAIL_TO_PASS" and r2[0]["pre_patch_outcome"] == "passed"

    assert pr_verdict_of(0, 3, 0, "", "") == ("NON_DISCRIMINATING", "")
    assert pr_verdict_of(1, 3, 40, "", "")[0] == "DISCRIMINATING"
    v40 = pr_verdict_of(0, 1, 40, "", "")     # the blocker: 1 P2P beside 40 no-evidence
    assert v40 == ("UNRESOLVED", "partial evidence: 40 unresolved rows"), v40
    assert pr_verdict_of(0, 0, 2, "", "") == ("UNRESOLVED", "no test resolved on both sides")
    assert pr_verdict_of(9, 9, 0, "timeout", "") == ("UNRESOLVED", "base_run: timeout")
    assert pr_verdict_of(9, 9, 0, "", "pytest exit 4")[1] == "candidate_run: pytest exit 4"

    assert extract("a===B===xml===E===b", "===B===", "===E===") == "xml"
    assert run_rc("noise\n===RUN_RC=1===\n", 0) == 1 and run_rc("", 124) == 124
    assert "{files}" in CLONE_SH and "===APPLY_OK===" in APPLY_SH
    print("selfcheck OK")
    return 0


def interval(rows: list[dict]) -> str:
    """The headline as an interval, never as one permissively computed number.
    strict = NON_DISCRIMINATING / (DISC + NON_DISC), every row of those PRs resolved.
    permissive = the same, counting `partial evidence` PRs (zero F2P, some no-evidence
    rows) as non-discriminating. The truth is between them."""
    d = sum(r["pr_verdict"] == "DISCRIMINATING" for r in rows)
    n = sum(r["pr_verdict"] == "NON_DISCRIMINATING" for r in rows)
    p = sum(r["unresolved_reason"].startswith("partial evidence") for r in rows)
    if not d + n + p:
        return "n/a (no resolved PR in this stratum)"
    lo = f"{n / (d + n):.0%}" if d + n else "n/a"
    hi = f"{(n + p) / (d + n + p):.0%}"
    return f"[{lo} .. {hi}]  (strict {n}/{d + n}, permissive {n + p}/{d + n + p})"


def summary(md: bool = False) -> int:
    import collections
    rows = list(csv.DictReader(open(PR_CSV, newline=""))) if PR_CSV.exists() else []
    if not rows:
        print("no results yet")
        return 0
    v = collections.Counter(r["pr_verdict"] for r in rows)
    resolved = v["DISCRIMINATING"] + v["NON_DISCRIMINATING"]
    reasons = collections.Counter(r["unresolved_reason"] for r in rows
                                  if r["pr_verdict"] == "UNRESOLVED")
    fix = [r for r in rows if r.get("cc_type") == "fix"]
    fp = [r for r in rows if r.get("base_is_merge_first_parent") == "1"]
    nd = [r for r in rows if r["pr_verdict"] == "NON_DISCRIMINATING"]
    audit = sum(int(r.get("unmatched_testish_files") or 0) > 0 for r in nd)
    if md:
        print("| PR verdict | n | share of attempted |\n|---|---:|---:|")
        for k in ("DISCRIMINATING", "NON_DISCRIMINATING", "UNRESOLVED"):
            print(f"| `{k}` | {v[k]} | {v[k]/len(rows):.0%} |")
        print(f"\nNon-discriminating share, `fix` PRs only (the headline): "
              f"**{interval(fix)}**, n={len(fix)}.\n")
        print(f"All PR types: {interval(rows)}. "
              f"base == merge^1 only: {interval(fp)}, n={len(fp)}.\n")
        print("| unresolved_reason | n |\n|---|---:|")
        for k, n in reasons.most_common():
            print(f"| `{k}` | {n} |")
        print("\n| cc_type | n | non-discriminating share |\n|---|---:|---|")
        for k, n in collections.Counter(r.get("cc_type") or "(none)" for r in rows).most_common():
            print(f"| `{k}` | {n} | {interval([r for r in rows if (r.get('cc_type') or '(none)') == k])} |")
        print("\n| pr_trailer_kinds | n | non-discriminating share |\n|---|---:|---|")
        for k, n in collections.Counter(r.get("pr_trailer_kinds") or "(none)"
                                        for r in rows).most_common():
            print(f"| `{k}` | {n} | {interval([r for r in rows if (r.get('pr_trailer_kinds') or '(none)') == k])} |")
        print(f"\nUpper bound on path-rule misses: {audit} of {len(nd)} NON_DISCRIMINATING "
              f"PRs also changed a file the wider auditor rule calls a test.")
        return 0
    print(f"attempted {len(rows)}  discriminating {v['DISCRIMINATING']}  "
          f"non-discriminating {v['NON_DISCRIMINATING']}  unresolved {v['UNRESOLVED']}")
    print(f"  headline (cc_type=fix, n={len(fix)}): {interval(fix)}")
    print(f"  all types (n={len(rows)}):            {interval(rows)}")
    print(f"  base==merge^1 (n={len(fp)}):          {interval(fp)}")
    print(f"  path-rule miss bound: {audit}/{len(nd)} NON_DISCRIMINATING PRs have "
          f"unmatched_testish_files>0")
    if resolved:
        print(f"  non-discriminating share of resolved (strict): "
              f"{v['NON_DISCRIMINATING']/resolved:.0%} ({v['NON_DISCRIMINATING']}/{resolved})")
    for k, n in reasons.most_common():
        print(f"  {n:3d}  {k}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--smoke", type=int, default=0,
                    help="only the N buildable repos with the smallest suites")
    ap.add_argument("--repo", default="", help="comma-separated O/R filter")
    ap.add_argument("--limit", type=int, default=0, help="max PRs this run")
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        return selfcheck()
    if a.summary:
        return summary(a.md)

    repos = buildable()
    if a.smoke:
        repos = repos[:a.smoke]
    if a.repo:
        want = set(a.repo.split(","))
        repos = [r for r in repos if r["repo"] in want]
    already = done_prs()
    todo = [(r, n) for r in repos for n in r["sample_pr_numbers"].split(";") if n
            and (r["repo"], n) not in already]
    if a.limit:
        todo = todo[:a.limit]
    print(f"[study] {len(repos)} buildable repos, {len(already)} PRs already done, "
          f"{len(todo)} to run, jobs={a.jobs}", flush=True)
    if not todo:
        return 0
    pilot.build_images({r["python"] or pilot.DEFAULT_PY for r in repos})
    cache_guard()

    def one(item: tuple[dict, str]) -> None:
        repo_row, num = item
        print(f"[study] START {repo_row['repo']}#{num}", flush=True)
        try:
            res, rows = run_pr(repo_row, num)
        except Exception as exc:   # never lose a PR
            res, rows = blank_pr(repo_row["repo"], num), []
            res.update(unresolved_reason=f"harness_exception: {type(exc).__name__}: {exc}"[:200],
                       repo_trailer_kinds=repo_row.get("trailer_kinds", ""))
        append([(TEST_CSV, TEST_COLUMNS, rows), (PR_CSV, PR_COLUMNS, [res])])
        print(f"[study] DONE  {res['repo']}#{res['pr']} {res['pr_verdict']} "
              f"tests={res['n_tests']} f2p={res['n_f2p']} p2p={res['n_p2p']} "
              f"unres={res['n_unresolved']} {res['unresolved_reason']} "
              f"{res['duration_s']}s", flush=True)

    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        list(ex.map(one, todo))
    print("[study] all done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
