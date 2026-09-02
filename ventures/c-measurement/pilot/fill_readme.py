#!/usr/bin/env python3
"""Regenerate README.md's interim-results block from results.csv, so the numbers in the
prose are never typed by hand. Idempotent: run it again whenever results.csv grows."""
import csv
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
README = HERE / "README.md"
MANIFEST = HERE.parent / "corpus" / "candidates-pilot-100.csv"
START, END = "<!--SUMMARY-->", "<!--/SUMMARY-->"

md = subprocess.run([sys.executable, str(HERE / "pilot.py"), "--summary", "--md"],
                    capture_output=True, text=True, check=True).stdout
rows = list(csv.DictReader(open(HERE / "results.csv", newline="")))
manifest = list(csv.DictReader(open(MANIFEST, newline="")))
total = len(manifest)
running = subprocess.run(["pgrep", "-f", "pilot.py --csv"], capture_output=True,
                         text=True).stdout.split()
done = len(rows) == total and {r["repo"] for r in rows} == {r["repo"] for r in manifest}
head = (f"## Results\n\n**The run is complete:** all **{total}** repos in "
        f"`candidates-pilot-100.csv` have a row in `results.csv`."
        if done else
        f"## Interim results\n\n**The run is not finished.** Rows in `results.csv`: "
        f"**{len(rows)} of {total}** repos in `candidates-pilot-100.csv`; the remaining "
        f"{total - len(rows)} are queued or in flight "
        f"({'the job is still running, pid ' + running[0] if running else 'the job is not running'}).")
gate = ("" if done else
        " **Do not quote these against the 30% gate:** the finished set is what the gate is"
        " about, and the corpus is ordered so the first rows are the largest repos.")
block = f"""{START}
{head}
Every number below is regenerated from `results.csv` by `fill_readme.py` — none of it is
typed by hand.{gate}

{md.strip()}
{END}"""
text = README.read_text()
if START in text and END in text:
    text = re.sub(re.escape(START) + r".*?" + re.escape(END), block, text, flags=re.S)
else:
    text = text.replace(START, block)
README.write_text(text)
print(f"README.md updated: {len(rows)}/{total} rows")
