"""docs/comparison.md may not say anything the checked-in evidence does not support."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from conftest import evidence_corpus, flatten, unquoted

EVIDENCE = Path(__file__).resolve().parent.parent / "docs" / "evidence"
#: A run of digits that is not part of a word, with thousands separators folded.
NUMBER = re.compile(r"(?<![\w.])\d+(?:,\d{3})*(?:\.\d+)?")

#: Every figure on the page, and the field of the repository metadata it comes
#: from. A figure with no entry here fails the test below.
FIGURES = {
    "kenryu42__cc-safety-net.txt": {
        "1,517": "stargazers_count",
        "75": "forks_count",
        "0": "open_issues_count",
        "2026-08-31": "pushed_at",
    },
    "microsoft__agentrc.txt": {
        "1,037": "stargazers_count",
        "93": "forks_count",
        "56": "open_issues_count",
        "2026-08-26": "pushed_at",
    },
}


@pytest.fixture(scope="session")
def comparison(repo_root: Path) -> str:
    return (repo_root / "docs" / "comparison.md").read_text(encoding="utf-8")


def test_every_quotation_on_the_page_is_in_a_checked_in_source(comparison: str) -> None:
    assert unquoted(comparison) == []


@pytest.mark.parametrize("slug", sorted(FIGURES))
def test_every_figure_on_the_page_is_the_value_in_the_fetched_metadata(comparison: str, slug: str) -> None:
    body = (EVIDENCE / slug).read_text(encoding="utf-8")
    payload = json.loads(body[body.index("{") :])
    for literal, field in FIGURES[slug].items():
        value = str(payload[field])
        assert literal.replace(",", "") in value, (slug, field, literal, value)
        assert literal in comparison, literal


def test_every_number_on_the_page_is_a_figure_this_test_knows(comparison: str) -> None:
    """The page states no number the code decides; every one is an incumbent's."""

    declared = {"2026-08-31", "2026", "08", "31", "26", "2", "3", "1", "2.0"} | {
        literal for figures in FIGURES.values() for literal in figures
    }
    for number in NUMBER.findall(flatten(comparison)):
        assert number in declared, number


def test_the_page_names_every_incumbent_the_evidence_covers(comparison: str) -> None:
    corpus = evidence_corpus()
    for name in ("kenryu42/cc-safety-net", "microsoft/agentrc"):
        assert name in comparison
        assert name in corpus


def test_the_page_says_the_incumbents_are_worth_installing(comparison: str) -> None:
    """The honest-comparison rule: the page recommends the free floor, not against it."""

    assert "Install the incumbents." in comparison
    assert "install the first two anyway" in (Path(EVIDENCE).parent.parent / "README.md").read_text(encoding="utf-8")


def test_the_page_records_the_date_and_the_refresh_command(comparison: str) -> None:
    assert "2026-08-31" in comparison
    assert "python3 scripts/refresh_evidence.py" in comparison
    assert (Path(EVIDENCE).parent.parent / "scripts" / "refresh_evidence.py").exists()


def test_every_evidence_file_records_its_source_and_its_date() -> None:
    files = sorted(EVIDENCE.glob("*.txt"))
    assert len(files) >= 4
    for path in files:
        head = path.read_text(encoding="utf-8").splitlines()[:3]
        assert head[0].startswith("# source: "), path.name
        assert re.fullmatch(r"# (fetched|command): .+", head[1]), path.name
