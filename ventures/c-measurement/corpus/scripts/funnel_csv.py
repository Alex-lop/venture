#!/usr/bin/env python3
"""Emit the tracked per-repo funnel CSV from widen.py's gitignored checkpoint log.

`raw/repo_results.jsonl` is append-only and resumable, so a repo may appear more than
once. **Dedupe rule: last row per repo wins.**

    python3 scripts/funnel_csv.py        # writes funnel-v3.csv, asserts the totals

The raw log is gitignored (it carries PR-author logins); `funnel-v3.csv` carries repo
names, stage/verdict and counts only, and is the tracked source for the funnel.
"""
import collections, csv, hashlib, json, pathlib, sys

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
        repo = r["repo"]
        if hashlib.sha256(repo.encode()).hexdigest() == (
            "c6da23a97540747e97c28f0f6246384376f1cf862a4fd14f72537efe8a794adb"
        ):
            repo = "redacted/repo-2064"
        yield dict(repo=repo, stage=r["stage"], verdict=r["verdict"],
                   examined=r.get("examined") or 0, qualifying=r.get("qualifying") or 0,
                   sample_prs=len(r.get("sample") or []),
                   **{k: d.get(k, 0) for k in DROPS})


def main():
    out = list(rows())
    total = collections.Counter()
    for r in out:
        total.update({k: r[k] for k in ["examined", "qualifying", "sample_prs"] + DROPS})
    verdicts = collections.Counter(r["verdict"] for r in out)
    # The completed funnel; v2 stays frozen for the published 60-repo study.
    assert len(out) == 3633, len(out)
    assert total["examined"] == 1614 and total["no_test_path"] == 502, total
    assert (total["no_verbatim_trailer"], total["too_large"], total["no_source_path"]) \
        == (143, 121, 121), total
    assert verdicts["QUALIFIED"] == 110, verdicts
    assert sum(r["sample_prs"] for r in out if r["verdict"] == "QUALIFIED") == 484
    with (HERE / "funnel-v3.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print(f"funnel-v3.csv: {len(out)} repos, {total['examined']} PRs examined, "
          f"{total['no_test_path']} no_test_path, {verdicts['QUALIFIED']} QUALIFIED, "
          f"{sum(r['sample_prs'] for r in out if r['verdict'] == 'QUALIFIED')} sample PRs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
