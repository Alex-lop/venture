#!/usr/bin/env bash
# The release gate for what CI cannot check offline: every page docs/comparison.md
# cites is re-fetched, every quotation on the page is re-found on a page that
# quotation's own row cites -- not merely somewhere -- and written into
# docs/comparison-quotes.txt with every page it was found on, so CI can re-check
# both the wording and the attribution offline,
# every star count is re-read with `gh api` and compared against what the page
# prints, and both release targets are resolved -- the tagged source archive
# and the PyPI project, the second of which turns green the moment
# the release is uploaded. Run it before a release; it needs the network and an
# authenticated `gh`, which is why CI does not run it.
set -uo pipefail
cd "$(dirname "$0")/.."

agent='agent-plan-lint/0.1.0 (+https://github.com/Alex-lop/agent-plan-lint)'
source_install="$(sed -n 's/^pip install git+//p' README.md)"
source_repo="${source_install%@*}"
source_tag="${source_install##*@}"
distribution="$(python3 -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["name"])')"
pypi_url="https://pypi.org/pypi/${distribution}/json"

print_install_targets() {
    printf '%s\n' "${source_repo}/archive/refs/tags/${source_tag}.tar.gz" "${pypi_url}"
}

pypi_copy_is_current() {
    [ "$1" != "200" ] || ! grep -q 'PyPI publication is pending' README.md
}

if [ "${1-}" = "--print-install-targets" ]; then
    print_install_targets
    exit 0
fi
if [ "${1-}" = "--check-pypi-copy" ]; then
    pypi_copy_is_current "${2-}"
    exit
fi

pages="$(mktemp -d)"
trap 'rm -rf "${pages}"' EXIT

while read -r url; do
    case "${url}" in https://*) ;; *) continue ;; esac
    code="$(curl -sS -A "${agent}" -L --max-time 60 -o "${pages}/$(printf '%s' "${url}" | tr -c 'A-Za-z0-9' '_')" -w '%{http_code}' "${url}")"
    printf '%s  %s\n' "${code}" "${url}"
    sleep 1
done < docs/comparison-sources.txt

status=0
python3 - "${pages}" <<'PY' || status=1
import html
import pathlib
import re
import sys
import unicodedata


def flat(text: str) -> str:
    """One lower-case line of words, with markup and typography normalised away."""

    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    text = unicodedata.normalize("NFKC", text)
    for fancy, plain in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'), ("\u2014", "--")):
        text = text.replace(fancy, plain)
    return " ".join(text.split()).lower()


sources = pathlib.Path("docs/comparison-sources.txt").read_text("utf-8")
urls = re.findall(r"^https://\S+$", sources, re.M)
fetched = re.search(r"^# fetched: (\S+ UTC)$", sources, re.M).group(1)
# The same name the shell loop above wrote each page under.
bodies = {}
for url in urls:
    body = pathlib.Path(sys.argv[1], re.sub(r"[^A-Za-z0-9]", "_", url))
    bodies[url] = flat(body.read_text("utf-8", "replace")) if body.exists() else ""
page = pathlib.Path("docs/comparison.md").read_text("utf-8")
units: list[str] = []
paragraph: list[str] = []
for line in page.splitlines():
    # A table row is its own unit; a stray quote in one row must not pair with
    # the next row's. Prose is joined so a quotation may wrap across lines.
    if line.startswith("|") or not line.strip():
        if paragraph:
            units.append(" ".join(paragraph))
            paragraph = []
        if line.startswith("|"):
            units.append(line)
    else:
        paragraph.append(line.strip())
units.append(" ".join(paragraph))
# Each quotation with the URLs the unit printing it cites: a quotation has to be
# on a page its own row links to, or it is attributed to the wrong project. Eight
# characters is the floor here and in tests/test_comparison_truth.py, which pins
# this constant so the two cannot drift apart.
quotations = [
    (quotation, re.findall(r"https://[^\s)]+", unit))
    for unit in units
    for quotation in re.findall(r'"([^"\n]{8,})"', unit)
]
# The archive is the offline half of this check: a quotation nobody fetched
# cannot be added to it without running this script, and
# tests/test_comparison_truth.py fails when the page prints one that is not here.
archive = [
    "# Every quotation docs/comparison.md prints, with the page it was found on.",
    "# Written by scripts/refresh-comparison.sh from the pages it fetched; do not",
    "# edit by hand. tests/test_comparison_truth.py fails when the page prints a",
    "# quotation that is not recorded here, which is how a fabricated quotation",
    "# fails CI offline rather than only at the next release.",
    "#",
    f"# fetched: {fetched}",
]
missing = []
for quotation, cited in quotations:
    found = [url for url, body in bodies.items() if flat(quotation) in body]
    if not found:
        missing.append(quotation)
        print(f"NOT ON ANY FETCHED PAGE: {quotation!r}")
        continue
    if not set(found) & set(cited):
        missing.append(quotation)
        print(f"ON A PAGE THE ROW DOES NOT CITE: {quotation!r} is on {found}, the row cites {cited}")
        continue
    # Every page it was found on, so the offline check can see the attribution.
    for url in found:
        archive.append(f"#\n# {url}\nquote: {quotation}")
pathlib.Path("docs/comparison-quotes.txt").write_text("\n".join(archive) + "\n", "utf-8")
print(f"{len(quotations) - len(missing)}/{len(quotations)} quotations found verbatim")
sys.exit(1 if missing else 0)
PY

# Star counts: the page states a tolerance, and this is the check behind it.
python3 - <<'STARS' || status=1
import pathlib
import re
import subprocess
import sys

page = pathlib.Path("docs/comparison.md").read_text("utf-8")
counted = sorted(set(re.findall(r"`([A-Za-z0-9][\w.-]*/[A-Za-z0-9][\w.-]*)` ([\d,]+)", page)))
drifted = []
for slug, printed in counted:
    read = subprocess.run(
        ["gh", "api", f"repos/{slug}", "-q", ".stargazers_count"],
        capture_output=True,
        text=True,
        check=False,
    )
    if read.returncode != 0:
        print(f"UNREADABLE  {slug}: {read.stderr.strip()}")
        drifted.append(slug)
        continue
    live, stated = int(read.stdout), int(printed.replace(",", ""))
    tolerance = max(5, round(live * 0.02))
    verdict = "ok" if abs(live - stated) <= tolerance else "OUT OF TOLERANCE"
    print(f"{verdict}  {slug}: page {stated:,}, live {live:,}, tolerance {tolerance:,}")
    if verdict != "ok":
        drifted.append(slug)
print(f"{len(counted) - len(drifted)}/{len(counted)} star counts within tolerance")
sys.exit(1 if drifted else 0)
STARS

# Every recorded figure has to still be what the manifest says it is: the page
# is pinned to the manifest offline by tests/test_comparison_truth.py, and this
# is the half that needs the network.
python3 - <<'FIGURES' || status=1
import io
import json
import pathlib
import re
import sys
import urllib.request
import zipfile

sources = pathlib.Path("docs/comparison-sources.txt").read_text("utf-8")
figures = set(re.findall(r"^figure: (.+)$", sources, re.M))
wrong = []
with urllib.request.urlopen("https://pypi.org/pypi/plan-lint/json", timeout=60) as response:
    project = json.load(response)
version = project["info"]["version"]
released = min(item["upload_time_iso_8601"] for item in project["releases"][version])[:10]
if f"last released {released} (v{version})" not in figures:
    wrong.append(f"plan-lint is now {version} released {released}")
wheel = next(item for item in project["releases"][version] if item["filename"].endswith(".whl"))
with urllib.request.urlopen(wheel["url"], timeout=60) as response:
    archive = zipfile.ZipFile(io.BytesIO(response.read()))
entry_points = next(
    archive.read(name).decode() for name in archive.namelist() if name.endswith("entry_points.txt")
)
if "plan-lint = " not in entry_points:
    wrong.append(f"plan-lint no longer installs a `plan-lint` console script: {entry_points!r}")
for line in wrong:
    print(f"FIGURE HAS MOVED: {line}")
print(f"{2 - len(wrong)}/2 published-package figures still hold")
sys.exit(1 if wrong else 0)
FIGURES

# The tagged source install and the PyPI project both have to resolve before release.
while IFS= read -r install; do
    code="$(curl -sS -A "${agent}" -L --max-time 60 -o /dev/null -w '%{http_code}' "${install}")"
    printf '%s  %s\n' "${code}" "${install}"
    if [ "${code}" != "200" ]; then
        echo "INSTALL TARGET DOES NOT RESOLVE: ${install}"
        status=1
    fi
    if [ "${install}" = "${pypi_url}" ] && ! pypi_copy_is_current "${code}"; then
        echo "README STILL SAYS PYPI PUBLICATION IS PENDING"
        status=1
    fi
done < <(print_install_targets)

exit "${status}"
