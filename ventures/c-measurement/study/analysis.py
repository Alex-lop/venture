#!/usr/bin/env python3
"""Every number in WRITEUP.md / SUMMARY.md, recomputed from the four published CSVs.

    python3 analysis.py            # the whole write-up's arithmetic
    python3 analysis.py --selfcheck  # the interval math, against closed forms

Reads only:  results-prs.csv, results-tests.csv, ../pilot/results.csv,
             ../corpus/candidates-v2.csv, ../corpus/funnel-v2.csv.
Writes nothing.  No network, no docker.
"""
import csv, sys, collections
from math import sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRS = HERE / "results-prs.csv"
TESTS = HERE / "results-tests.csv"
PILOT = HERE.parent / "pilot" / "results.csv"
CORPUS = HERE.parent / "corpus" / "candidates-v2.csv"
FUNNEL = HERE.parent / "corpus" / "funnel-v2.csv"


def wilson(k, n, z=1.959963985):
    """Wilson score interval, the one to quote for a proportion at 0 or 1."""
    if not n:
        return (0.0, 1.0)
    p, d = k / n, 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - h) / d), min(1.0, (c + h) / d))


def clopper_pearson(k, n, alpha=0.05):
    """Exact interval by bisection on the Beta CDF via the regularized incomplete
    beta function's continued fraction — no scipy, and correct at k=0 and k=n."""
    if not n:
        return (0.0, 1.0)
    lo = 0.0 if k == 0 else _beta_inv(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else _beta_inv(1 - alpha / 2, k + 1, n - k)
    return (lo, hi)


def _betainc(a, b, x):
    """Regularized incomplete beta I_x(a,b), Lentz's continued fraction (NR 6.4)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    from math import lgamma, exp, log
    lbeta = lgamma(a) + lgamma(b) - lgamma(a + b)
    front = exp(log(x) * a + log(1 - x) * b - lbeta) / a
    if x > (a + 1) / (a + b + 2):
        return 1.0 - _betainc(b, a, 1 - x)
    f, c, d = 1.0, 1.0, 0.0
    for i in range(0, 300):
        m = i // 2
        if i == 0:
            num = 1.0
        elif i % 2 == 0:
            num = m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m))
        else:
            num = -((a + m) * (a + b + m) * x) / ((a + 2 * m) * (a + 2 * m + 1))
        d = 1.0 + num * d
        d = 1e-30 if abs(d) < 1e-30 else d
        d = 1.0 / d
        c = 1.0 + num / c
        c = 1e-30 if abs(c) < 1e-30 else c
        f *= c * d
        if abs(1.0 - c * d) < 1e-12:
            break
    return front * (f - 1.0)


def _beta_inv(p, a, b):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _betainc(a, b, mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def pct(x):
    return f"{100 * x:.1f}%"


def ci(k, n):
    w, c = wilson(k, n), clopper_pearson(k, n)
    return (f"{k}/{n} = {pct(k / n) if n else 'n/a'}  "
            f"Wilson95 [{pct(w[0])}, {pct(w[1])}]  CP95 [{pct(c[0])}, {pct(c[1])}]")


def main():
    prs = list(csv.DictReader(open(PRS, newline="")))
    tests = list(csv.DictReader(open(TESTS, newline="")))
    pilot = list(csv.DictReader(open(PILOT, newline="")))
    corpus = list(csv.DictReader(open(CORPUS, newline="")))
    funnel = list(csv.DictReader(open(FUNNEL, newline="")))

    # ---- funnel -----------------------------------------------------------
    buildable = [r for r in pilot
                 if r["install_ok"] == "1" and r["collect_ok"] == "1"
                 and r["run_ok"] == "1" and r["errored"] == "0"
                 and int(r["passed"]) + int(r["failed"]) >= 1]
    sample_prs = sum(len([x for x in r["sample_pr_numbers"].split(";") if x])
                     for r in corpus)
    print("== FUNNEL ==")
    # ../corpus/funnel-v2.csv: one row per repo, emitted by corpus/scripts/funnel_csv.py
    # from widen.py's append-only checkpoint log, last row per repo (2,015 rows/1,908 repos).
    fk = ["examined", "no_test_path", "no_verbatim_trailer", "too_large", "no_source_path"]
    ft = collections.Counter()
    for r in funnel:
        ft.update({k: int(r[k]) for k in fk})
    fv = collections.Counter(r["verdict"] for r in funnel)
    print(f"stage-1 repos                {len(funnel)}")
    print(f"repo gate / lock+pytest gate "
          f"{len(funnel) - sum(v for k, v in fv.items() if k in {'under_stars', 'fork', 'not_python', 'archived', 'stale'})}"
          f" / {fv['QUALIFIED'] + fv['too_few_qualifying_prs']}")
    print(f"PRs examined at stage 4      {ft['examined']}")
    print(f"  dropped no_test_path       {ci(ft['no_test_path'], ft['examined'])}")
    print("  dropped other              "
          + ", ".join(f"{k} {ft[k]}" for k in fk[2:]))
    print(f"qualifying repos             {fv['QUALIFIED']}")
    print(f"funnel sample PRs            "
          f"{sum(int(r['sample_prs']) for r in funnel if r['verdict'] == 'QUALIFIED')}")
    print(f"corpus repos                 {len(corpus)}")
    print(f"corpus sample PRs            {sample_prs}")
    print(f"pilot repos attempted        {len(pilot)}")
    print(f"pilot buildable              {ci(len(buildable), len(pilot))}")
    print(f"study PRs attempted          {len(prs)}")
    print(f"study repos with >=1 PR row  {len(set(r['repo'] for r in prs))}")

    build_names = set(r["repo"] for r in buildable)
    in_build = [r for r in corpus if r["repo"] in build_names]
    print(f"sample PRs in buildable repos "
          f"{sum(len([x for x in r['sample_pr_numbers'].split(';') if x]) for r in in_build)}")
    st = sorted(int(r["stars"]) for r in in_build)
    print(f"buildable-repo stars         min {st[0]} median {st[len(st) // 2]} max {st[-1]}  "
          f"under 50 stars: {sum(x < 50 for x in st)}/{len(st)}")
    print(f"resolved PRs span repos      "
          f"{len(set(r['repo'] for r in prs if r['pr_verdict'] != 'UNRESOLVED'))}")

    ms = sorted(r["merged_at"] for r in prs if r["merged_at"])
    dur = [float(r["duration_s"]) for r in prs if r["duration_s"]]
    print(f"merged_at window             {ms[0][:10]} .. {ms[-1][:10]}")
    print(f"container time               {sum(dur) / 3600:.1f} h  "
          f"mean {sum(dur) / len(dur):.0f}s  max {max(dur):.0f}s")

    # ---- per-PR: the pre-registered quantity ------------------------------
    v = collections.Counter(r["pr_verdict"] for r in prs)
    disc = [r for r in prs if r["pr_verdict"] == "DISCRIMINATING"]
    nond = [r for r in prs if r["pr_verdict"] == "NON_DISCRIMINATING"]
    part = [r for r in prs if r["unresolved_reason"].startswith("partial evidence")]
    resolved = len(disc) + len(nond)
    print("\n== PER-PR, pre-registered: zero FAIL_TO_PASS ==")
    print(f"attempted {len(prs)}  DISCRIMINATING {v['DISCRIMINATING']}  "
          f"NON_DISCRIMINATING {v['NON_DISCRIMINATING']}  UNRESOLVED {v['UNRESOLVED']}")
    print(f"unresolved share             {ci(v['UNRESOLVED'], len(prs))}")
    print(f"strict  (resolved only)      {ci(len(nond), resolved)}")
    print(f"permissive (+partial ev.)    {ci(len(nond) + len(part), resolved + len(part))}")
    for name, sub in (("cc_type=fix", [r for r in prs if r["cc_type"] == "fix"]),
                      ("base==merge^1", [r for r in prs
                                         if r["base_is_merge_first_parent"] == "1"])):
        d = sum(r["pr_verdict"] == "DISCRIMINATING" for r in sub)
        n = sum(r["pr_verdict"] == "NON_DISCRIMINATING" for r in sub)
        print(f"{name:28} n={len(sub)}  strict {ci(n, d + n)}")

    # ---- per-test ---------------------------------------------------------
    tv = collections.Counter(r["verdict"] for r in tests)
    tres = tv["FAIL_TO_PASS"] + tv["PASS_TO_PASS"]
    f2p = [r for r in tests if r["verdict"] == "FAIL_TO_PASS"]
    by_base = collections.Counter(r["base_outcome"] for r in f2p)
    print("\n== PER-TEST ==")
    print(f"PR-touched test rows         {len(tests)}")
    print(f"  PASS_TO_PASS               {tv['PASS_TO_PASS']}")
    print(f"  FAIL_TO_PASS               {tv['FAIL_TO_PASS']}")
    print(f"  UNRESOLVED                 {tv['UNRESOLVED']}")
    print(f"P2P share of resolved rows   {ci(tv['PASS_TO_PASS'], tres)}")
    print(f"P2P share of all rows        {ci(tv['PASS_TO_PASS'], len(tests))}")
    print(f"F2P via base error (import/collection) "
          f"{ci(by_base['error'], len(f2p))}")
    print(f"F2P via base assertion failure         "
          f"{ci(by_base['failed'], len(f2p))}")
    print("pre_patch_outcome            " +
          "  ".join(f"{k}={n}" for k, n in
                    collections.Counter(r["pre_patch_outcome"]
                                        for r in tests).most_common()))
    print("base_outcome                 " +
          "  ".join(f"{k}={n}" for k, n in
                    collections.Counter(r["base_outcome"]
                                        for r in tests).most_common()))
    print("candidate_outcome            " +
          "  ".join(f"{k}={n}" for k, n in
                    collections.Counter(r["candidate_outcome"]
                                        for r in tests).most_common()))
    flaky = sum(r["base_outcome"] == "flaky" for r in tests) + \
        sum(r["candidate_outcome"] == "flaky" for r in tests)
    print(f"flaky observations (either side)       {flaky} of {2 * len(tests)} side-obs")

    # ---- the stricter per-PR bar -----------------------------------------
    assertion = collections.defaultdict(int)
    anyf2p = collections.defaultdict(int)
    for r in f2p:
        k = (r["repo"], r["pr"])
        anyf2p[k] += 1
        if r["base_outcome"] == "failed":
            assertion[k] += 1
    res = [r for r in prs if r["pr_verdict"] in ("DISCRIMINATING", "NON_DISCRIMINATING")]
    no_assert = [r for r in res if not assertion[(r["repo"], r["pr"])]]
    only_err = [r for r in res
                if anyf2p[(r["repo"], r["pr"])] and not assertion[(r["repo"], r["pr"])]]
    both = [r for r in res
            if assertion[(r["repo"], r["pr"])]
            and anyf2p[(r["repo"], r["pr"])] > assertion[(r["repo"], r["pr"])]]
    print("\n== PER-PR, stricter: zero ASSERTION-LEVEL FAIL_TO_PASS ==")
    print(f"resolved PRs                 {len(res)}")
    print(f"no assertion-level F2P       {ci(len(no_assert), len(res))}")
    print(f"  of which F2P is import/collection error only  {len(only_err)}")
    print(f"  PRs mixing both kinds of F2P                  {len(both)}")
    fixres = [r for r in res if r["cc_type"] == "fix"]
    print(f"fix PRs, no assertion F2P    "
          f"{ci(sum(not assertion[(r['repo'], r['pr'])] for r in fixres), len(fixres))}")


    # ---- clustering and weighting ----------------------------------------
    print("\n== CLUSTERING AND WEIGHTING ==")
    per_repo = collections.Counter(r["repo"] for r in prs)
    c = sorted(per_repo.values())
    print(f"repos with >=1 PR row        {len(per_repo)}  "
          f"PRs/repo min {c[0]} median {c[len(c) // 2]} max {c[-1]}")
    print("largest 3 repos by PR count  " +
          "  ".join(f"{k}={n}" for k, n in per_repo.most_common(3)))
    trows = collections.Counter(r["repo"] for r in tests)
    print(f"test rows: top repo {trows.most_common(1)[0][1]}/{len(tests)} = "
          f"{pct(trows.most_common(1)[0][1] / len(tests))} ({trows.most_common(1)[0][0]})")
    tpr = collections.Counter((r["repo"], r["pr"]) for r in tests)
    tv2 = sorted(tpr.values())
    print(f"test rows/PR min {tv2[0]} median {tv2[len(tv2) // 2]} max {tv2[-1]}")
    shares = []
    for r in res:
        k = (r["repo"], r["pr"])
        d = int(r["n_f2p"]) + int(r["n_p2p"])
        if d:
            shares.append(int(r["n_p2p"]) / d)
    shares.sort()
    print(f"per-PR P2P share of resolved rows: median "
          f"{pct(shares[len(shares) // 2])}  "
          f"(unweighted over {len(shares)} resolved PRs with >=1 resolved row)")
    print(f"resolved PRs with zero P2P   "
          f"{sum(s == 0 for s in shares)}/{len(shares)}")
    newtest = sum(int(r["test_files_new"]) > 0 for r in res)
    print(f"resolved PRs adding a new test file  {newtest}/{len(res)}")
    print(f"  of the {len(no_assert)} with no assertion-level F2P, adding a new test file: "
          f"{sum(int(r['test_files_new']) > 0 for r in no_assert)}")

    # ---- unresolved -------------------------------------------------------
    print("\n== UNRESOLVED ==")
    for k, n in collections.Counter(
            r["unresolved_reason"] for r in prs
            if r["pr_verdict"] == "UNRESOLVED").most_common():
        print(f"  {n:3d}  {k}")

    # ---- strata -----------------------------------------------------------
    print("\n== STRATA (n, DISCRIMINATING, NON_DISCRIMINATING, UNRESOLVED) ==")
    for col in ("cc_type", "pr_trailer_kinds"):
        print(f"-- {col}")
        for k, n in collections.Counter(r[col] or "(none)" for r in prs).most_common():
            sub = [r for r in prs if (r[col] or "(none)") == k]
            c = collections.Counter(r["pr_verdict"] for r in sub)
            print(f"  {k:34} n={n:3d}  D={c['DISCRIMINATING']:3d} "
                  f"N={c['NON_DISCRIMINATING']:3d} U={c['UNRESOLVED']:3d}")

    # ---- selection covariates --------------------------------------------
    print("\n== SELECTION ==")
    print(f"corpus repos 10-49 stars     "
          f"{sum(int(r['stars']) < 50 for r in corpus)}/{len(corpus)}")
    lines = sorted(int(r["changed_lines"]) for r in prs if r["changed_lines"])
    print(f"changed_lines median         {lines[len(lines) // 2]}  "
          f"min {lines[0]}  max {lines[-1]}")
    print(f"PRs adding >=1 new test file "
          f"{sum(int(r['test_files_new']) > 0 for r in prs)}/{len(prs)}")
    print(f"PRs with infra_changed=1     "
          f"{sum(r['infra_changed'] == '1' for r in prs)}/{len(prs)}")
    print(f"path-rule miss bound         "
          f"{sum(int(r['unmatched_testish_files'] or 0) > 0 for r in nond)}"
          f"/{len(nond)} NON_DISCRIMINATING PRs have unmatched_testish_files>0; "
          f"{sum(int(r['unmatched_testish_files'] or 0) > 0 for r in prs)}/{len(prs)} "
          f"over all PRs")
    redteam(prs, tests, pilot, corpus)
    return 0


def selfcheck() -> int:
    """The only hand-rolled maths here is the incomplete beta behind Clopper-Pearson.
    Check it against the closed forms, and both intervals against k=0, the case the
    headline actually uses."""
    for x in (0.1, 0.5, 0.9):
        assert abs(_betainc(1, 1, x) - x) < 1e-9                     # I_x(1,1) = x
        assert abs(_betainc(2, 1, x) - x * x) < 1e-9                 # I_x(2,1) = x^2
        assert abs(_betainc(1, 2, x) - (2 * x - x * x)) < 1e-9       # I_x(1,2) = 2x - x^2
    for n in (41, 77, 99):
        lo, hi = clopper_pearson(0, n)
        assert lo == 0.0 and abs(hi - (1 - 0.025 ** (1 / n))) < 1e-6, (n, hi)
        lo, hi = clopper_pearson(n, n)
        assert hi == 1.0 and abs(lo - 0.025 ** (1 / n)) < 1e-6, (n, lo)
    assert abs(clopper_pearson(1, 100)[1] - 0.054459) < 1e-4         # the permissive end
    w = wilson(0, 99)
    assert w[0] == 0.0 and abs(w[1] - 0.037353) < 1e-5, w
    assert wilson(50, 100)[0] < 0.5 < wilson(50, 100)[1]
    assert wilson(0, 0) == (0.0, 1.0) and clopper_pearson(0, 0) == (0.0, 1.0)
    print("selfcheck OK")
    return 0




def redteam(prs, tests, pilot, corpus):
    """== RED-TEAM PASS (2026-08-31) == every number added or corrected by the
    three red-team reviews.  Deterministic: the cluster bootstrap is seeded."""
    import random
    print("\n== RED-TEAM PASS (2026-08-31) ==")
    res = {(r["repo"], r["pr"]) for r in prs if r["pr_verdict"] != "UNRESOLVED"}
    resolved = [r for r in tests if r["verdict"] != "UNRESOLVED"]
    f2p = [r for r in tests if r["verdict"] == "FAIL_TO_PASS"]

    # --- O-A2: what FAIL_TO_PASS is actually made of --------------------------
    x = collections.Counter((r["base_outcome"], r["pre_patch_outcome"]) for r in f2p)
    print("[A2] FAIL_TO_PASS crosstab base_outcome x pre_patch_outcome:")
    for k, v in x.most_common():
        print(f"       {k[0]:>6} @ base / {k[1]:>7} pre-patch  {v:>5}  {pct(v / len(f2p))}")
    print(f"     total F2P {len(f2p)};  new-module-with-its-test ('error','absent') "
          f"{x[('error','absent')]} = {pct(x[('error','absent')] / len(f2p))};  "
          f"collateral ('error','passed') {x[('error','passed')]} = "
          f"{pct(x[('error','passed')] / len(f2p))}")

    # re-score the per-PR headline with the collateral rows deleted
    keep = collections.Counter()
    for r in f2p:
        if not (r["base_outcome"] == "error" and r["pre_patch_outcome"] == "passed"):
            keep[(r["repo"], r["pr"])] += 1
    print(f"[A2] per-PR headline re-scored with collateral rows dropped: "
          f"{sum(keep[k] == 0 for k in res)}/{len(res)} PRs left with zero F2P")

    # --- O-A1 / O-C4: clustering ---------------------------------------------
    ev = collections.Counter((r["repo"], r["pr"], r["test_id"].split("::")[0])
                             for r in f2p if r["base_outcome"] == "error")
    top2 = sum(v for _, v in ev.most_common(2))
    print(f"[A1] {sum(ev.values())} error-at-base F2P rows come from {len(ev)} module-level "
          f"collection events; the two largest are {top2}/{len(f2p)} = "
          f"{pct(top2 / len(f2p))} of ALL F2P rows")
    print(f"[A1]   the three largest single events: "
          + "; ".join(f"{k[0]}#{k[1]} {k[2]} = {v} rows" for k, v in ev.most_common(3)))
    drop = {(k[0], k[1]) for k, _ in ev.most_common(2)}
    r2 = [r for r in resolved if (r["repo"], r["pr"]) not in drop]
    p2 = sum(r["verdict"] == "PASS_TO_PASS" for r in r2)
    fe2 = sum(r["verdict"] == "FAIL_TO_PASS" and r["base_outcome"] == "error" for r in r2)
    print(f"[A1] dropping those two PRs ({sorted(drop)}): P2P {pct(p2 / len(r2))}, "
          f"import-error share of F2P {pct(fe2 / (len(r2) - p2))}")

    by = collections.defaultdict(lambda: [0, 0, 0, 0])   # p2p, n, err_f2p, f2p
    for r in resolved:
        c = by[r["repo"]]
        c[1] += 1
        if r["verdict"] == "PASS_TO_PASS":
            c[0] += 1
        else:
            c[3] += 1
            if r["base_outcome"] == "error":
                c[2] += 1
    names = sorted(by)
    rng, A, B = random.Random(0), [], []
    for _ in range(20000):
        s = [by[rng.choice(names)] for _ in names]
        A.append(sum(c[0] for c in s) / sum(c[1] for c in s))
        d = sum(c[3] for c in s)
        if d:
            B.append(sum(c[2] for c in s) / d)
    A.sort(); B.sort()
    q = lambda v, p: v[int(p * len(v))]
    print(f"[A1] cluster bootstrap over {len(names)} repos, 20,000 draws, seed 0: "
          f"P2P 95% [{pct(q(A,.025))}, {pct(q(A,.975))}]  "
          f"import-error 95% [{pct(q(B,.025))}, {pct(q(B,.975))}]")
    lo = [(sum(by[m][0] for m in names if m != n) / sum(by[m][1] for m in names if m != n),
           sum(by[m][2] for m in names if m != n) / sum(by[m][3] for m in names if m != n))
          for n in names]
    print(f"[A1] leave-one-repo-out: P2P {pct(min(a for a, _ in lo))}..{pct(max(a for a, _ in lo))}  "
          f"import-error {pct(min(b for _, b in lo))}..{pct(max(b for _, b in lo))}")
    sh = sorted(by[n][0] / by[n][1] for n in names)
    mean = sum(sh) / len(sh)
    sd = sqrt(sum((v - mean) ** 2 for v in sh) / (len(sh) - 1))
    print(f"[A1] per-repo P2P share: min {pct(sh[0])} median {pct(sh[len(sh)//2])} "
          f"max {pct(sh[-1])} mean {pct(mean)} sd {pct(sd)}")
    nd_repos = len({r["repo"] for r in prs if r["pr_verdict"] == "NON_DISCRIMINATING"})
    print(f"[C4] per-PR headline with the repo as the unit: {ci(nd_repos, len(names))}")

    # --- O-A5: the bracket the strict/permissive pair does not give -----------
    print(f"[A5] worst case, every unresolved PR non-discriminating: "
          f"{ci(len(prs) - len(res), len(prs))}")

    # --- O-A3 / O-A4: strata, and how many repos each is ----------------------
    print("[A4] repos behind each stratum (resolved PRs only):")
    for key, lab in (("cc_type", "cc_type"), ("pr_trailer_kinds", "trailer")):
        for v, _ in collections.Counter(r[key] for r in prs
                                        if r["pr_verdict"] != "UNRESOLVED").most_common():
            g = [r for r in prs if r[key] == v and r["pr_verdict"] != "UNRESOLVED"]
            print(f"       {lab}={v or '(none)':<26} {len(g):>3} PRs / "
                  f"{len({r['repo'] for r in g}):>2} repos")
    fixrepos = len({r["repo"] for r in prs
                    if r["cc_type"] == "fix" and r["pr_verdict"] != "UNRESOLVED"})
    print(f"[A4] fix stratum with the repo as the unit: {ci(0, fixrepos)}")

    # --- O-B4 / O-C2: the pre-registered quantity, newly-added test ids only --
    new = [r for r in tests if r["pre_patch_outcome"] == "absent"]
    newres = [r for r in new if r["verdict"] != "UNRESOLVED"]
    np_ = sum(r["verdict"] == "PASS_TO_PASS" for r in newres)
    print(f"[B4] newly-added test ids (pre_patch_outcome=absent): {len(new)} of {len(tests)}; "
          f"{len(newres)} resolved")
    print(f"[B4] PASS_TO_PASS share of newly-added resolved ids: {ci(np_, len(newres))}   "
          f"(all PR-touched ids, for contrast: "
          f"{ci(sum(r['verdict']=='PASS_TO_PASS' for r in resolved), len(resolved))})")
    pp = collections.Counter(r["pre_patch_outcome"] for r in resolved
                             if r["verdict"] == "PASS_TO_PASS")
    print(f"[C2] of the {sum(pp.values())} PASS_TO_PASS rows, {pp['passed']} = "
          f"{pct(pp['passed'] / sum(pp.values()))} already passed on the UNPATCHED base; "
          f"pre-existing ids are {len(resolved) - len([r for r in resolved if r['pre_patch_outcome']=='absent'])}"
          f"/{len(resolved)} = "
          f"{pct(1 - len([r for r in resolved if r['pre_patch_outcome']=='absent']) / len(resolved))} "
          f"of all resolved rows")
    nf = collections.Counter(r["base_outcome"] for r in newres
                             if r["verdict"] == "FAIL_TO_PASS")
    print(f"[B4] newly-added ids that are FAIL_TO_PASS: {sum(nf.values())} of {len(newres)} "
          f"resolved ({pct(sum(nf.values()) / len(newres))}); UNRESOLVED "
          f"{len(new) - len(newres)}")
    print(f"[B4] newly-added F2P by base outcome: assertion(failed) {nf['failed']} = "
          f"{pct(nf['failed'] / sum(nf.values()))}, import/collection(error) {nf['error']} = "
          f"{pct(nf['error'] / sum(nf.values()))}")
    cnew = collections.Counter()
    anew = collections.Counter()
    for r in new:
        anew[(r["repo"], r["pr"])] += 1
        if r["verdict"] == "FAIL_TO_PASS":
            cnew[(r["repo"], r["pr"])] += 1
    have = [k for k in res if anew[k] > 0]
    nd = [k for k in have if cnew[k] == 0]
    print(f"[B4] PER-PR, newly-added ids only — the quantity precedents.md defines: "
          f"{ci(len(nd), len(have))}  ({len(res) - len(have)} resolved PRs have no new id)")
    print(f"[B4]   the exception is {sorted(nd)}; repos with >=1 such PR: "
          f"{ci(len({k[0] for k in nd}), len(names))}")
    fixres = {(r["repo"], r["pr"]) for r in prs
              if r["cc_type"] == "fix" and r["pr_verdict"] != "UNRESOLVED"}
    hf = [k for k in have if k in fixres]
    print(f"[B4]   fix stratum, newly-added ids only: {ci(len([k for k in hf if cnew[k]==0]), len(hf))}")

    # --- O-A6: the merge^1 sensitivity check ---------------------------------
    fp = {(r["repo"], r["pr"]): r["base_is_merge_first_parent"] for r in prs}
    print("[A6] per-test FAIL_TO_PASS rate by base_is_merge_first_parent:")
    for rows, lab in ((resolved, "all"), (r2, "two dominant PRs dropped")):
        for flag in ("1", "0"):
            g = [r for r in rows if fp[(r["repo"], r["pr"])] == flag]
            print(f"       {lab:<26} flag={flag}  "
                  f"{sum(r['verdict']=='FAIL_TO_PASS' for r in g)}/{len(g)} = "
                  f"{pct(sum(r['verdict']=='FAIL_TO_PASS' for r in g) / len(g))}")

    # --- O-A7: flakiness at the level that matters ---------------------------
    fl = [r for r in tests if "flaky" in (r["base_outcome"], r["candidate_outcome"])]
    print(f"[A7] flaky rows {len(fl)} in "
          f"{len({(r['repo'], r['pr'], r['test_id'].split('::')[0]) for r in fl})} module(s); "
          f"the base side holds {len(ev)} module-level collection events, each one "
          f"import decision replicated to every id in its module")

    # --- O-A8 / O-A10: bounds that were vacuous or mis-stated -----------------
    strict = {k for k in res} - {(r["repo"], r["pr"]) for r in f2p
                                 if r["base_outcome"] == "failed"}
    sx = collections.Counter((r["base_outcome"], r["pre_patch_outcome"]) for r in f2p
                             if (r["repo"], r["pr"]) in strict)
    print(f"[A2b] the {len(strict)} stricter-bar PRs' own FAIL_TO_PASS rows: "
          + ", ".join(f"({k[0]},{k[1]}) {v}" for k, v in sx.most_common())
          + f" — collateral is {sx[('error','passed')]}/{sum(sx.values())} = "
          f"{pct(sx[('error','passed')] / sum(sx.values()))} of their evidence")
    um = [r for r in prs if int(r["unmatched_testish_files"] or 0) > 0]
    print(f"[A8] PRs with >=1 file the wider auditor rule calls a test and the strict rule "
          f"does not: {len(um)}/{len(prs)}; of those, in the stricter-bar set: "
          f"{sorted((r['repo'], r['pr']) for r in um if (r['repo'], r['pr']) in strict)}")
    n = collections.Counter((r["repo"], r["pr"]) for r in tests)
    a = sorted(n[(r["repo"], r["pr"])] for r in prs)
    nz = [v for v in a if v]
    print(f"[A10] test rows per PR over all {len(a)} PRs: {a[0]} .. {a[-1]} "
          f"(median {a[len(a)//2]}); {len(a) - len(nz)} PRs produced no test row; over the "
          f"{len(nz)} that did: {nz[0]} .. {nz[-1]} (median {nz[len(nz)//2]})")

    # --- O-C1: built vs unbuilt covariates -----------------------------------
    build = {r["repo"] for r in pilot
             if r["install_ok"] == "1" and r["collect_ok"] == "1" and r["run_ok"] == "1"
             and r["errored"] == "0" and int(r["passed"]) + int(r["failed"]) >= 1}
    print("[C1] built vs unbuilt corpus repos, on covariates observable for both:")
    for lab, g in (("built", [r for r in corpus if r["repo"] in build]),
                   ("unbuilt", [r for r in corpus if r["repo"] not in build])):
        s = sorted(int(r["stars"]) for r in g)
        ap = sorted(int(r["agent_pr_count_90d"]) for r in g)
        lk = collections.Counter(r["lock_kind"] for r in g)
        print(f"       {lab:<8} n={len(g):>2}  stars min {s[0]} median {s[len(s)//2]} "
              f"max {s[-1]}  agent_pr_90d median {ap[len(ap)//2]}  "
              f"uv.lock {lk['uv.lock']}/{len(g)}")
    return 0


if __name__ == "__main__":
    sys.exit(selfcheck() if "--selfcheck" in sys.argv else main())
