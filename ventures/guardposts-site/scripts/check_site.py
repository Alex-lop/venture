#!/usr/bin/env python3
"""Doc-truth test for the guardposts site. Stdlib only.

1. Every number on study.md appears in `python3 analysis.py` output or in SUMMARY.md, AND
   every "A ... = P%" on a study.md table row is bound to its claim: A and its denominator
   must be the A/B = P% that analysis.py prints. Membership alone would let a real number
   sit on the wrong row.
2. Every count on a package page is recomputed from that package's suite (collected tests,
   hostile servers) rather than trusted.
3. Every relative link resolves to a file; every github.com / *.github.io URL is Alex-lop's;
   every path inside Alex-lop/venture resolves against `git ls-files` in the monorepo, so a
   link to something that has not been pushed fails instead of 404ing in public.
4. No page claims a package can be installed until RELEASED names it -- and vice versa.
5. No email address, and no string from private/DENYLIST.txt (whole-word, case-insensitive).

Usage: python3 scripts/check_site.py [--study PATH] [--denylist PATH] [--skip-analysis]
                                     [--skip-packages]
"""
import ast
import re
import subprocess
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
PACKAGES = ("agent-plan-lint", "egresswall", "guardrail-checkup")
# The one sentence allowed to say "PyPI" while nothing is released. Stripped before the
# install-claim scan, so any other PyPI claim fails.
STATUS = "release in progress; install lines appear here when the PyPI upload lands"
INSTALL_MARKERS = ("pip install", "uv pip install", "pypi")
# Third-party repos the comparison pages cite. Anything else on github.com must be
# Alex-lop's, so a link cannot quietly point at an account that is not the principal's.
CITED = ("open-policy-agent/conftest", "open-policy-agent/regal", "microsoft/agentrc",
         "cirbuk/plan-lint", "data-privacy-stack/presidio", "protectai/llm-guard",
         "snyk/agent-scan", "lasso-security/mcp-gateway", "guardrails-ai/guardrails")
# Counts on a package page, and how to recompute each from the package itself. The page is
# checked against the suite, never against the package's own README, so a stale README
# cannot certify a stale page.
PKG_COUNTS = {
    "packages/agent-plan-lint.md": [("plan-lint", r"(\d[\d,]*) collected tests", "tests")],
    "packages/egresswall.md": [("egress-guard", r"(\d[\d,]*) collected tests", "tests"),
                               ("egress-guard", r"(\d[\d,]*) hand-written hostile servers",
                                "hostile")],
}
MONOREPO = SITE.parent.parent
REPO_URL = re.compile(r"https?://github\.com/Alex-lop/venture/(?:tree|blob)/[^/]+/([^)\s#]+)", re.I)
COLLECTED = re.compile(r"(\d+) tests? collected")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
LINK = re.compile(r"\[[^\]]*\]\(\s*([^)\s]+)")
URL = re.compile(r"https?://\S+")
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")

fails = []


def check(name, bad, detail=""):
    if bad:
        fails.append(name)
        print(f"FAIL {name}: {len(bad)} problem(s)")
        for b in bad[:20]:
            print(f"    {b}")
        if len(bad) > 20:
            print(f"    ... and {len(bad) - 20} more")
    else:
        print(f"PASS {name}: {detail}")


def pages():
    return sorted(p for p in SITE.rglob("*.md"))


def site_pages():
    """The .md files Jekyll renders: the ones with front matter. README.md is not one."""
    return [p for p in pages() if p.read_text().startswith("---\n")]


def rel(p):
    return str(p.relative_to(SITE))


def tracked():
    """Files pushed to Alex-lop/venture, as `git ls-files` sees them. Returns None on error."""
    run = subprocess.run(["git", "ls-files"], cwd=MONOREPO, capture_output=True, text=True)
    return set(run.stdout.split()) if run.returncode == 0 else None


def collected_tests(pkg: Path):
    """Number of tests the package's own suite collects. `-o addopts=` so a package that
    puts -q in its addopts still prints the total."""
    run = subprocess.run(["uv", "run", "--offline", "pytest", "-o", "addopts=",
                          "--collect-only", "-q"], cwd=pkg, capture_output=True, text=True)
    found = COLLECTED.search(run.stdout)
    if run.returncode != 0 or not found:
        return None, (run.stdout + run.stderr)[-400:]
    return int(found.group(1)), ""


def hostile_servers(pkg: Path):
    """One hostile server per test function that calls drive_script -- the count the
    package's own tests/test_readme_truth.py asserts against its README."""
    src = pkg / "tests" / "test_proxy.py"
    if not src.is_file():
        return None, f"{src} not found"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    return sum(isinstance(n, ast.FunctionDef) and any(
        isinstance(c, ast.Call) and getattr(c.func, "id", "") == "drive_script"
        for c in ast.walk(n)) for n in tree.body), ""


def bound_ratios(study_md: str, analysis: str):
    """Each "A ... = P%" on a table row, with A's denominator taken from the numbers before
    it on that row, must be a ratio analysis.py actually printed. Intervals ([0.0%, 5.5%])
    are dropped first; percentages never serve as a numerator or denominator."""
    hay = " ".join(analysis.split())
    bad = []
    for i, line in enumerate(study_md.splitlines(), 1):
        if not line.lstrip().startswith("|"):
            continue
        row = re.sub(r"\[[^\]]*\]", " ", line)
        plain = []
        for m in re.finditer(r"(\d[\d,]*(?:\.\d+)?)(%?)", row):
            value = m.group(1).replace(",", "")
            if not m.group(2):
                plain.append(value)
            elif row[:m.start()].rstrip().endswith("=") and len(plain) >= 2:
                a, b = plain[-2], plain[-1]
                pair = ((a, b), (b, a))
                if not any(f"{x}/{y} = {value}%" in hay for x, y in pair):
                    bad.append(f"study.md:{i}: '= {value}%' is not analysis.py's "
                               f"{b}/{a} or {a}/{b}")
    return bad


def main():
    argv = sys.argv[1:]
    skip_analysis = "--skip-analysis" in argv
    skip_packages = "--skip-packages" in argv
    study_dir = SITE.parent / "c-measurement" / "study"
    if "--study" in argv:
        study_dir = Path(argv[argv.index("--study") + 1]).resolve()

    # ---- 1. numbers on study.md -------------------------------------------------
    haystack = ""
    summary = study_dir / "SUMMARY.md"
    if summary.is_file():
        haystack += summary.read_text()
    if skip_analysis:
        print(f"SKIP numbers: --skip-analysis (haystack: {'SUMMARY.md' if haystack else 'nothing'})")
    elif not (study_dir / "analysis.py").is_file():
        fails.append("numbers")
        print(f"FAIL numbers: {study_dir}/analysis.py not found (pass --study or --skip-analysis)")
    else:
        run = subprocess.run([sys.executable, "analysis.py"], cwd=study_dir,
                             capture_output=True, text=True)
        if run.returncode != 0:
            fails.append("numbers")
            print(f"FAIL numbers: analysis.py exited {run.returncode}\n{run.stderr[-2000:]}")
        else:
            haystack += run.stdout
            # Whole-token comparison, not substring: "1.7" must not be satisfied by "41.7".
            hay = {n.replace(",", "") for n in NUM.findall(haystack)}
            body = URL.sub(" ", (SITE / "study.md").read_text().split("---", 2)[-1])
            missing = sorted({n for n in NUM.findall(body) if n.replace(",", "") not in hay})
            whole = URL.sub(" ", (SITE / "study.md").read_text())  # line numbers as edited
            bound = bound_ratios(whole, run.stdout)
            rows = sum(1 for l in whole.splitlines() if l.lstrip().startswith("|"))
            check("numbers", missing + bound,
                  f"every number on study.md is in analysis.py output or SUMMARY.md, and "
                  f"every '= N%' across {rows} table rows is a ratio analysis.py printed "
                  f"({len(run.stdout.splitlines())} lines of analysis)")

    # ---- 2. counts on the package pages, recomputed from the suites ------------
    if skip_packages:
        print("SKIP package-counts: --skip-packages")
    else:
        counts, checked = [], 0
        for page, wanted in PKG_COUNTS.items():
            text = (SITE / page).read_text()
            for pkg_name, pattern, kind in wanted:
                pkg = SITE.parent / pkg_name
                stated = re.search(pattern, text)
                if stated is None:
                    counts.append(f"{page}: no number matching /{pattern}/ on the page")
                    continue
                actual, why = (collected_tests(pkg) if kind == "tests"
                               else hostile_servers(pkg))
                if actual is None:
                    counts.append(f"{page}: cannot recount {kind} in {pkg}: {why}")
                elif int(stated.group(1).replace(",", "")) != actual:
                    counts.append(f"{page}: says {stated.group(0)!r}; {pkg_name} has {actual}")
                else:
                    checked += 1
        check("package-counts", counts,
              f"{checked} count(s) on the package pages recomputed from the packages")

    # ---- 3. links ---------------------------------------------------------------
    bad_links = []
    files = tracked()
    if files is None:
        bad_links.append(f"git ls-files failed in {MONOREPO}: monorepo links cannot be checked")
    for p in pages():
        for target in LINK.findall(p.read_text()):
            if target.startswith("http"):
                host = target.split("/")[2].lower()
                if host in ("github.com", "raw.githubusercontent.com"):
                    slug = "/".join(target.split("/")[3:5]).lower()
                    if not (slug.startswith("alex-lop/") or slug in CITED):
                        bad_links.append(f"{rel(p)}: neither Alex-lop's nor a cited "
                                         f"source -> {target}")
                    inside = REPO_URL.match(target)
                    if inside and files is not None:
                        path = inside.group(1).rstrip("/")
                        if not (path in files or any(f.startswith(path + "/") for f in files)):
                            bad_links.append(f"{rel(p)}: not pushed to Alex-lop/venture "
                                             f"(no tracked file at {path}) -> {target}")
                elif host.endswith("github.io") and not host.startswith("alex-lop."):
                    bad_links.append(f"{rel(p)}: not Alex-lop's pages site -> {target}")
                continue
            if target.startswith(("mailto:", "#")):
                bad_links.append(f"{rel(p)}: {target}")
                continue
            if not (p.parent / target.split("#")[0]).exists():
                bad_links.append(f"{rel(p)}: dangling -> {target}")
    check("links", bad_links,
          f"{len(pages())} pages; every relative link resolves and every Alex-lop/venture "
          f"path is one of {len(files or ())} tracked files")

    # ---- 4. install claims vs the RELEASED flag file ----------------------------
    flag = SITE / "RELEASED"
    released = set(flag.read_text().split()) if flag.is_file() else set()
    unknown = released - set(PACKAGES)
    claims, claimed = [], set()
    for p in site_pages():
        for i, line in enumerate(p.read_text().replace(STATUS, "").splitlines(), 1):
            low = line.lower()
            if not any(m in low for m in INSTALL_MARKERS):
                continue
            named = {n for n in PACKAGES if n in low}
            claimed |= named & released
            if not named & released:
                claims.append(f"{rel(p)}:{i}: {line.strip()[:90]}")
    check("install-claims", claims + sorted(f"RELEASED names {n}, but no page installs it"
                                            for n in released - claimed)
          + sorted(f"RELEASED names unknown package {n}" for n in unknown),
          f"RELEASED = {sorted(released) or 'absent (no package may claim an install)'}")

    # ---- 5. emails and the denylist ---------------------------------------------
    emails = [f"{rel(p)}: {m}" for p in pages() for m in EMAIL.findall(p.read_text())]
    check("no-email", emails, "no address on any page; GitHub issues are the only channel")

    denylist = SITE.parent.parent / "private" / "DENYLIST.txt"
    if "--denylist" in argv:
        denylist = Path(argv[argv.index("--denylist") + 1]).resolve()
    if not denylist.is_file():
        print(f"SKIP denylist: {denylist} not present")
    else:
        terms = [t for t in (l.strip() for l in denylist.read_text().splitlines()) if t]
        pat = re.compile("|".join(rf"(?<!\w){re.escape(t)}(?!\w)" for t in terms), re.I)
        hits = []
        for p in pages():
            for i, line in enumerate(p.read_text().splitlines(), 1):
                for m in pat.finditer(line):
                    hits.append(f"{rel(p)}:{i}: {m.group(0)!r}")
        check("denylist", hits, f"{len(terms)} denied strings, none present")

    print("\n" + ("FAILED: " + ", ".join(fails) if fails else "OK -- all checks passed"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
