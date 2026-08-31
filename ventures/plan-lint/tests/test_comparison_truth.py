"""docs/comparison.md is the page that makes the most externally checkable claims.

`scripts/refresh-comparison.sh` re-fetches the sources before a release; what it
found is checked in, so the same checks run offline here. The page cites no page
that was never captured, its fetch date is real, every star count names the
repository it came from, and every quotation it prints is one the script found on
the page it cites and wrote into `docs/comparison-quotes.txt`.
"""

from __future__ import annotations

import re
import tomllib
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
COMPARISON = (ROOT / "docs" / "comparison.md").read_text(encoding="utf-8")
SOURCES = (ROOT / "docs" / "comparison-sources.txt").read_text(encoding="utf-8")
QUOTES = (ROOT / "docs" / "comparison-quotes.txt").read_text(encoding="utf-8")
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
SLUG = r"`[A-Za-z0-9][\w.-]*/[A-Za-z0-9][\w.-]*`"


def star_cells() -> list[str]:
    """The `Stars` cell of every body row of every table that has one."""

    cells: list[str] = []
    columns: int | None = None
    for line in COMPARISON.splitlines():
        if not line.startswith("|"):
            columns = None
            continue
        row = [cell.strip() for cell in line.strip("|").split("|")]
        if columns is None:
            columns = row.index("Stars") if "Stars" in row else -1
        elif columns >= 0 and set("".join(row)) - set("-: "):
            cells.append(row[columns])
    return cells


def first_cells() -> list[str]:
    """The first cell of every body row of every comparison table."""

    cells: list[str] = []
    heading = False
    for line in COMPARISON.splitlines():
        if not line.startswith("|"):
            heading = False
            continue
        row = [cell.strip() for cell in line.strip("|").split("|")]
        if not heading:
            heading = True
        elif set("".join(row)) - set("-: "):
            cells.append(row[0])
    return cells


def test_the_page_still_has_rows_to_check() -> None:
    assert len(first_cells()) >= 9


@pytest.mark.parametrize("cell", first_cells())
def test_every_comparison_row_is_a_tool_and_a_page_the_manifest_recorded(cell: str) -> None:
    """A row is a public claim about someone else's project, under the author's name.

    A wholly fabricated row -- a tool that does not exist, citing a URL already in
    the manifest -- passed every other check on this page: the third table has no
    `Stars` column, and the page's disclosure covers unquoted *negative*
    judgements, not invented positive ones. So the row itself is bound to the
    manifest by tool name and cited URL together.
    """

    links = re.findall(r"\[([^\]]+)\]\((https://[^)]+)\)", cell)

    assert links, f"a comparison row that cites nothing: {cell}"
    for name, url in links:
        assert f"\nrow: {name} {url}\n" in SOURCES, f"row: {name} {url}"


def test_every_row_the_manifest_records_is_still_on_the_page() -> None:
    """The other direction: a row deleted from the page leaves no evidence behind."""

    recorded = re.findall(r"^row: (.+) (https://\S+)$", SOURCES, re.M)
    printed = {
        (name, url) for cell in first_cells() for name, url in re.findall(r"\[([^\]]+)\]\((https://[^)]+)\)", cell)
    }

    assert len(recorded) >= 9
    assert set(recorded) == printed


def test_a_row_the_manifest_never_recorded_would_fail_the_check() -> None:
    """The guard's own failure mode, pinned rather than assumed."""

    fabricated = "[Kyverno for agents](https://kyverno.io/docs/introduction/)"
    name, url = re.findall(r"\[([^\]]+)\]\((https://[^)]+)\)", fabricated)[0]

    assert url in SOURCES, "the fabricated row cites a URL the manifest already has"
    assert f"\nrow: {name} {url}\n" not in SOURCES


def test_the_page_still_has_star_counts_to_check() -> None:
    assert len(star_cells()) >= 4


@pytest.mark.parametrize("cell", star_cells())
def test_every_star_count_names_the_repository_it_was_read_from(cell: str) -> None:
    assert re.fullmatch(rf"{SLUG} [\d,]+(?: · {SLUG} [\d,]+)*", cell), cell


def test_a_star_count_written_in_prose_also_names_its_repository() -> None:
    for line in COMPARISON.splitlines():
        if line.startswith("|") or not re.search(r"\d[\d,]*\s+stars\b", line):
            continue
        assert re.search(SLUG, line), line


@pytest.mark.parametrize("url", sorted(set(re.findall(r"https://[^\s)]+", COMPARISON))))
def test_every_page_the_comparison_cites_was_captured(url: str) -> None:
    """A URL that is not in the manifest is a claim from a page nobody fetched."""

    assert url in SOURCES, url


def test_the_fetch_date_is_real_and_is_not_in_the_future() -> None:
    stated = re.search(r"fetched on \*\*(\d{4}-\d{2}-\d{2}) UTC\*\*", COMPARISON)
    captured = re.search(r"^# fetched: (\d{4}-\d{2}-\d{2}) UTC$", SOURCES, re.M)

    assert stated is not None and captured is not None
    fetched = date.fromisoformat(stated.group(1))
    assert fetched == date.fromisoformat(captured.group(1))
    assert fetched <= datetime.now(UTC).date()


def test_the_page_states_a_tolerance_the_refresh_script_enforces() -> None:
    """A number on the page that no check can fail on is a number nobody re-reads."""

    script = (ROOT / "scripts" / "refresh-comparison.sh").read_text(encoding="utf-8")

    assert "more than 2 per cent, or by more than five" in COMPARISON
    assert "max(5, round(live * 0.02))" in script
    assert "gh api" in script


def test_every_figure_the_page_states_is_one_the_manifest_recorded() -> None:
    """A number about someone else's project needs a command that read it, and a date."""

    flat = " ".join(COMPARISON.split())
    figures = re.findall(r"^figure: (.+)$", SOURCES, re.M)
    stated = re.findall(r"last (?:pushed|released) \d{4}-\d{2}-\d{2}(?: \(v[\d.]+\))?", flat)

    assert figures and stated
    for figure in figures:
        assert figure in flat, figure
    assert len(figures) >= 12
    for phrase in stated:
        assert any(phrase in figure for figure in figures), phrase


def test_every_star_count_on_the_page_is_one_the_manifest_recorded() -> None:
    """Mutating a count on the page has to fail offline, not only at release time."""

    flat = " ".join(COMPARISON.split())
    figures = re.findall(r"^figure: (.+)$", SOURCES, re.M)
    counts = re.findall(rf"({SLUG}) ([\d,]+)", flat)

    assert len(counts) >= 9
    for slug, count in counts:
        assert any(f"{slug} {count}" == figure for figure in figures), f"{slug} {count}"


def test_the_console_script_claim_carries_dated_evidence() -> None:
    """A claim about someone else's package needs the command that read it."""

    assert "the `plan-lint` console script" in " ".join(COMPARISON.split())
    assert "figure: the `plan-lint` console script" in SOURCES
    assert "entry_points.txt" in SOURCES


def test_no_date_on_the_page_is_unaccounted_for() -> None:
    """Every date is either the fetch date or one of the recorded figures."""

    accounted = re.findall(r"\d{4}-\d{2}-\d{2}", SOURCES)

    for date_text in re.findall(r"\d{4}-\d{2}-\d{2}", COMPARISON):
        assert date_text in accounted, date_text


def test_every_file_the_page_names_exists_inside_the_package() -> None:
    """A citation to a path outside the released tree is a citation to nothing."""

    named = set(re.findall(r"`([\w./-]+\.(?:md|txt|py|toml|json|sh|yml))`", COMPARISON))

    assert named
    for relative in named:
        assert (ROOT / relative).exists() or (ROOT / "docs" / relative).exists(), relative


def test_the_page_says_the_unquoted_judgements_are_not_machine_checked() -> None:
    """The half no script can enforce has to be disclosed, not implied."""

    assert "no\ncheck can re-derive it" in COMPARISON


def test_the_refresh_script_resolves_both_install_targets_the_readme_shows() -> None:
    """Two install commands, two things that have to exist on release day."""

    script = (ROOT / "scripts" / "refresh-comparison.sh").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "sed -n 's/^pip install //p' README.md" in script
    assert "sed -n 's/^uv pip install git+//p' README.md" in script
    assert "https://pypi.org/pypi/${distribution}/json" in script
    assert "both install targets above" in readme


def test_the_refresh_script_identifies_itself_as_this_package() -> None:
    """The script ships in the sdist, so its User-Agent is this package's public face."""

    script = (ROOT / "scripts" / "refresh-comparison.sh").read_text(encoding="utf-8")
    expected = f"agent='{PROJECT['name']}/{PROJECT['version']} (+{PROJECT['urls']['Source']})'"

    assert expected in script, expected


#: The shortest quoted span the page and the refresh script both collect. Eight
#: characters is enough to put a false self-description in a competitor's mouth
#: -- Cedar 'calls itself "a linter"' -- and the constant has to move in the
#: script at the same time, which
#: `test_the_quotation_floor_is_the_one_the_refresh_script_collects` pins.
MIN_QUOTATION_CHARACTERS = 8


def units() -> list[str]:
    """The page split the way `scripts/refresh-comparison.sh` splits it.

    A table row is its own unit so a stray quote in one row cannot pair with the
    next row's; prose is joined so a quotation may wrap across lines.
    """

    collected: list[str] = []
    paragraph: list[str] = []
    for line in COMPARISON.splitlines():
        if line.startswith("|") or not line.strip():
            if paragraph:
                collected.append(" ".join(paragraph))
                paragraph = []
            if line.startswith("|"):
                collected.append(line)
        else:
            paragraph.append(line.strip())
    collected.append(" ".join(paragraph))
    return collected


def quotations() -> list[tuple[str, tuple[str, ...]]]:
    """Every quotation on the page, with the URLs the unit printing it cites."""

    return [
        (quotation, tuple(re.findall(r"https://[^\s)]+", unit)))
        for unit in units()
        for quotation in re.findall(rf'"([^"\n]{{{MIN_QUOTATION_CHARACTERS},}})"', unit)
    ]


def archived_quotations() -> dict[str, set[str]]:
    """Each recorded quotation, and every page `refresh-comparison.sh` found it on."""

    archive: dict[str, set[str]] = {}
    url = ""
    for line in QUOTES.splitlines():
        if line.startswith("# https://"):
            url = line[2:]
        elif line.startswith("quote: "):
            archive.setdefault(line.removeprefix("quote: "), set()).add(url)
    return archive


def test_the_page_still_has_quotations_to_check() -> None:
    assert len(quotations()) >= 11


def test_the_quotation_floor_is_the_one_the_refresh_script_collects() -> None:
    """Two collectors, one constant: a quotation the script never fetched must fail here."""

    script = (ROOT / "scripts" / "refresh-comparison.sh").read_text(encoding="utf-8")

    assert f"{{{MIN_QUOTATION_CHARACTERS},}}" in script, script
    assert MIN_QUOTATION_CHARACTERS <= 8


@pytest.mark.parametrize(("quotation", "cited"), quotations())
def test_every_quotation_is_one_the_refresh_script_found_on_a_page_the_page_cites(
    quotation: str, cited: tuple[str, ...]
) -> None:
    """A fabricated quotation fails here, offline, rather than at the next release.

    The archive is only ever written by `scripts/refresh-comparison.sh` out of
    pages it fetched, so a quotation cannot be added to it without re-fetching --
    and it records which page each one came off, so a real quotation moved into
    another tool's row fails too. Misquoting a named third party is a factual
    defect, not a formatting one.
    """

    found = archived_quotations().get(quotation)

    assert found is not None, quotation
    assert found & set(cited), f"{quotation!r} was found on {sorted(found)}, not on {list(cited)}"


def test_a_quotation_printed_under_another_tools_url_would_fail_the_check() -> None:
    """A real quotation moved into a neighbouring row left the whole suite green.

    The archive records the page each quotation came off, so the check can tell a
    LangGraph sentence printed in the CrewAI row from one printed in LangGraph's.
    """

    archive = archived_quotations()
    pages = {url for urls in archive.values() for url in urls}

    assert len(pages) >= 5
    for quotation, cited in quotations():
        elsewhere = pages - archive[quotation]
        assert elsewhere, f"{quotation!r} is on every cited page; the check cannot discriminate"
        assert not archive[quotation] & elsewhere
        assert archive[quotation] & set(cited)


def test_the_quotation_archive_belongs_to_the_fetch_the_manifest_records() -> None:
    """An archive from another day is evidence for another version of those pages."""

    archived = re.search(r"^# fetched: (\d{4}-\d{2}-\d{2}) UTC$", QUOTES, re.M)
    captured = re.search(r"^# fetched: (\d{4}-\d{2}-\d{2}) UTC$", SOURCES, re.M)

    assert archived is not None and captured is not None
    assert archived.group(1) == captured.group(1)
    cited = re.findall(r"^# (https://\S+)$", QUOTES, re.M)
    assert cited
    for url in cited:
        assert url in SOURCES, url


def test_the_predecessor_ordering_is_the_one_the_recorded_dates_imply() -> None:
    """ "Published first" is a comparative claim; both dates are checked in."""

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    incumbent = re.search(r"^figure: last released (\d{4}-\d{2}-\d{2})", SOURCES, re.M)
    ours = re.search(r"^## [\d.]+ - (\S+)$", changelog, re.M)

    assert incumbent is not None and ours is not None
    first = ours.group(1) == "unreleased" or date.fromisoformat(incumbent.group(1)) < date.fromisoformat(ours.group(1))

    assert first, "the incumbent no longer published first; the page says it did"
    assert "is the same idea, published first" in " ".join(COMPARISON.split())


def test_the_provenance_of_the_port_carries_dated_evidence() -> None:
    """The licence and the five ported paths are claims about another repository."""

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    porting = (ROOT / "docs" / "porting-notes.md").read_text(encoding="utf-8")
    recorded = re.findall(r"^provenance: (.+)$", SOURCES, re.M)
    licences = [item.removeprefix("Graphene LICENSE ") for item in recorded if item.startswith("Graphene LICENSE ")]
    paths = [item.removeprefix("ported path ") for item in recorded if item.startswith("ported path ")]

    assert len(licences) == 1
    assert len(paths) == 5
    for page in (readme, porting):
        assert f"[Graphene](https://github.com/Alex-lop/Graphene) ({licences[0]})" in " ".join(page.split())
    for spelling in paths:
        assert spelling in porting, spelling


def test_the_readme_comparison_line_names_the_categories_the_page_has() -> None:
    """The README used to enumerate seven tools for a page that covers eleven.

    An enumeration goes stale silently every time a row is added, so the line
    names the page's own section categories instead, and each of those has to be
    a heading on the page.
    """

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    line = re.search(r"^`docs/comparison\.md` — (.+?)\.$", readme, re.M | re.S)
    headings = " ".join(re.findall(r"^## (.+)$", COMPARISON, re.M)).lower()

    assert line is not None, "the README no longer points at the comparison page"
    named = re.findall(r"(policy engines|agent frameworks|guardrails)", " ".join(line.group(1).split()))
    assert len(named) == 3, line.group(1)
    for category in named:
        assert category in headings, category
    # And no tool is named in that line, which is what went stale.
    for slug in re.findall(SLUG, COMPARISON):
        assert slug.strip("`").split("/")[-1] not in line.group(1)
