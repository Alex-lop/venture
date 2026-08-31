#!/usr/bin/env python3
"""Emit the tracked per-repo funnel CSV from widen.py's gitignored checkpoint log.

`raw/repo_results.jsonl` is append-only and resumable, so a repo that was re-processed
appears more than once: 2,015 rows for 1,908 repos. **Dedupe rule: last row per repo
wins.** Reading the log without that rule gives 981 examined / 302 no_test_path instead
of the published 937 / 288.

    python3 scripts/funnel_csv.py        # writes funnel-v2.csv, asserts the totals

The raw log is gitignored (it carries PR-author logins); `funnel-v2.csv` carries repo
names, stage/verdict and counts only, and is the tracked source for the funnel.
"""
import collections, csv, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent.parent
DROPS = ["ok", "no_test_path", "no_verbatim_trailer", "too_large", "no_source_path"]
COLS = ["repo", "stage", "verdict", "examined", "qualifying", "sample_prs"] + DROPS


def rows():
    last = {}
    for line in (HERE / "raw" / "repo_results.jsonl").open():
        d = json.loads(line)
        last[d["repo"]] = d           # last row per repo wins
    for r in sorted(last.values(), key=lambda d: d["repo"]):
        d = r.get("drop_reasons") or {}
        yield dict(repo=r["repo"], stage=r["stage"], verdict=r["verdict"],
                   examined=r.get("examined") or 0, qualifying=r.get("qualifying") or 0,
                   sample_prs=len(r.get("sample") or []),
                   **{k: d.get(k, 0) for k in DROPS})


def main():
    out = list(rows())
    total = collections.Counter()
    for r in out:
        total.update({k: r[k] for k in ["examined", "qualifying", "sample_prs"] + DROPS})
    verdicts = collections.Counter(r["verdict"] for r in out)
    # the published funnel: WRITEUP.md §Corpus and funnel, FUNNEL-v2.md stage table
    assert len(out) == 1908, len(out)
    assert total["examined"] == 937 and total["no_test_path"] == 288, total
    assert (total["no_verbatim_trailer"], total["too_large"], total["no_source_path"]) \
        == (101, 69, 62), total
    assert verdicts["QUALIFIED"] == 60, verdicts
    assert sum(r["sample_prs"] for r in out if r["verdict"] == "QUALIFIED") == 265
    with (HERE / "funnel-v2.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, COLS)
        w.writeheader()
        w.writerows(out)
    print(f"funnel-v2.csv: {len(out)} repos, {total['examined']} PRs examined, "
          f"{total['no_test_path']} no_test_path, {verdicts['QUALIFIED']} QUALIFIED, "
          f"{sum(r['sample_prs'] for r in out if r['verdict'] == 'QUALIFIED')} sample PRs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
