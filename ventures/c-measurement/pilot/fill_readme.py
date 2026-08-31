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
START, END = "<!--SUMMARY-->", "<!--/SUMMARY-->"

md = subprocess.run([sys.executable, str(HERE / "pilot.py"), "--summary", "--md"],
                    capture_output=True, text=True, check=True).stdout
rows = list(csv.DictReader(open(HERE / "results.csv", newline="")))
total = sum(1 for _ in csv.DictReader(open(HERE.parent / "corpus" / "candidates-v2.csv",
                                           newline="")))
running = subprocess.run(["pgrep", "-f", "pilot.py --csv"], capture_output=True,
                         text=True).stdout.split()
block = f"""{START}
## Interim results

**The run is not finished.** Rows in `results.csv`: **{len(rows)} of {total}** repos in
`candidates-v2.csv`; the remaining {total - len(rows)} are queued or in flight
({'the job is still running, pid ' + running[0] if running else 'the job is not running'}).
Every number below is regenerated from `results.csv` by `fill_readme.py` — none of it is
typed by hand. **Do not quote these against the 30% gate:** the finished set is what the
gate is about, and the corpus is ordered so the first rows are the largest repos.

{md.strip()}
{END}"""
text = README.read_text()
if START in text and END in text:
    text = re.sub(re.escape(START) + r".*?" + re.escape(END), block, text, flags=re.S)
else:
    text = text.replace(START, block)
README.write_text(text)
print(f"README.md updated: {len(rows)}/{total} rows")
