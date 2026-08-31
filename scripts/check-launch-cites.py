#!/usr/bin/env python3
"""Check the README anchors in outreach/queue.md, section '## Package launches'.

Every cite there is `PL §Heading` or `(EW §Heading: "quoted phrase")` — section
anchors, never line numbers, because the READMEs move under the drafts. This asserts
each heading still exists and each quoted phrase is still on one line of that README.
Run it before the principal posts (queue.md §C row 0b). Exits non-zero on any miss.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
READMES = {"PL": ROOT / "ventures/plan-lint/README.md",
           "EW": ROOT / "ventures/egress-guard/README.md"}
SECTION = re.compile(r"^## Package launches.*?^## Track M", re.S | re.M)
HEADING = re.compile(r'\b(PL|EW) §([^:,;()"*\n]+)')
PHRASE = re.compile(r'\((PL|EW)[^()]*?:\s*((?:"[^"]*",?\s*)+)\)')

draft = SECTION.search((ROOT / "outreach/queue.md").read_text(encoding="utf-8")).group(0)
text = {tag: path.read_text(encoding="utf-8") for tag, path in READMES.items()}
headings = HEADING.findall(draft)
phrases = [(tag, p) for tag, group in PHRASE.findall(draft)
           for p in re.findall(r'"([^"]+)"', group)]
bad = []

if len(headings) < 20 or len(phrases) < 8:
    bad.append("%d headings / %d phrases matched - the cite grammar changed and this "
               "check has gone vacuous" % (len(headings), len(phrases)))

# a backticked EW:284 is this file's own prose about the scheme that was replaced
for stale in re.findall(r"\b(?:PL|EW):\d+", re.sub(r"`[^`]*`", "", draft)):
    bad.append("line-number cite survives: %s" % stale)

for tag, heading in headings:
    heading = heading.strip().rstrip(".")
    if heading != "opening" and ("## " + heading) not in text[tag]:
        bad.append("%s: no section '## %s'" % (tag, heading))

for tag, phrase in phrases:
    if not any(phrase in line for line in text[tag].splitlines()):
        bad.append("%s: phrase is not on any single line: %r" % (tag, phrase))

print("%d headings, %d quoted phrases checked against %s and %s"
      % (len(headings), len(phrases), *[p.relative_to(ROOT) for p in READMES.values()]))
print("\n".join(sorted(set(bad))) if bad else "all anchors resolve")
sys.exit(1 if bad else 0)
