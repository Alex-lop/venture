"""docs/comparison.md is checked against docs/evidence/, offline.

Every star count, licence, release tag, date and quotation on that page has to
be in a response or an excerpt that was fetched and checked in. A quotation the
source never contained cannot survive this file.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from conftest import flatten, quotations, unquoted

REPOS = {
    "presidio": "data-privacy-stack__presidio.json",
    "llm-guard": "protectai__llm-guard.json",
    "agent-scan": "snyk__agent-scan.json",
    "mcp-gateway": "lasso-security__mcp-gateway.json",
    "guardrails": "guardrails-ai__guardrails.json",
}


@pytest.fixture(scope="session")
def evidence(repo_root: Path) -> Path:
    return repo_root / "docs" / "evidence"


@pytest.fixture(scope="session")
def page(repo_root: Path) -> str:
    return (repo_root / "docs" / "comparison.md").read_text(encoding="utf-8")


def approx_stars(count: int) -> str:
    return f"~{count / 1000:.1f}k" if count >= 1000 else f"~{count // 10 * 10}"


def records(evidence: Path) -> dict[str, dict]:
    return {
        key: json.loads((evidence / name).read_text(encoding="utf-8"))
        for key, name in REPOS.items()
    }


def section(page: str, needle: str) -> str:
    """The chunk of the page that describes one project."""
    parts = page.split("\n## ")
    found = [part for part in parts if needle in part.splitlines()[0]]
    assert found, needle
    return found[0]


def first_bullet(section: str) -> str:
    """The line under the heading that carries the stars, licence, release and dates."""
    bullets = re.split(r"\n- ", section)
    assert len(bullets) > 1, section.splitlines()[0]
    return bullets[1].split("\n\n")[0]


def test_every_project_has_a_checked_in_api_response(evidence: Path) -> None:
    for name in REPOS.values():
        assert (evidence / name).exists(), name


def test_the_page_states_the_fetch_date_the_evidence_carries(page: str, evidence: Path) -> None:
    stated = re.search(r"fetched on \*\*(\d{4}-\d{2}-\d{2})\*\*", page)
    assert stated is not None, "the page must state the date its evidence was fetched"
    for item in evidence.glob("*.json"):
        assert json.loads(item.read_text())["fetched"] == stated.group(1), item.name
    for item in evidence.glob("*.txt"):
        assert f"# fetched: {stated.group(1)}" in item.read_text(encoding="utf-8"), item.name


@pytest.mark.parametrize("key", sorted(REPOS))
def test_the_figures_for_each_project_match_its_api_response(
    key: str, page: str, evidence: Path
) -> None:
    record = records(evidence)[key]
    text = section(page, record["full_name"].split("/")[1])
    assert approx_stars(record["stargazers_count"]) in text, record["stargazers_count"]
    assert record["license"] in text
    if record["archived"]:
        # As an emphasised label in the first bullet, beside the stars and the
        # licence -- not anywhere in the section, and not in passing. The word
        # appears further down in "the GitHub API returns `archived: true`", so
        # a loose check stayed green when the label itself was replaced with
        # "actively maintained by its authors".
        labels = re.findall(r"\*\*(.+?)\*\*", first_bullet(text))
        assert any("archived" in item.lower() for item in labels), (
            "an archived project must carry the label, not a passing mention"
        )
    assert record["pushed_at"][:10] in text
    if record["tag_name"] is None:
        assert "no GitHub release published" in text
    else:
        assert f"`{record['tag_name']}`" in text
        assert record["published_at"][:10] in text


def test_every_quotation_on_the_page_is_in_the_checked_in_sources(page: str) -> None:
    assert len(quotations(page)) >= 12, "the page quotes its sources; this test is why"
    assert unquoted(page) == []


CATEGORIES = re.compile(r"one `categories` object with\s+(\d+) flags . (.+?) . and no class", re.S)


def test_the_summary_does_not_generalise_over_the_whole_table(page: str) -> None:
    """Guardrails raises and Agent Scan only scans, so no claim may cover every row."""
    flat = flatten(page)
    assert "most of the projects in this table detect and then rewrite" in flat
    assert "The short version: the projects in this table detect and then rewrite" not in flat
    assert "Guardrails is the one project here that will also raise rather than repair" in flat
    assert "closest comparison" not in flat, "an unmeasured superlative"


def test_the_claim_that_guardrails_can_refuse_is_in_the_checked_in_readme(evidence: Path) -> None:
    source = (evidence / "guardrails-readme.txt").read_text(encoding="utf-8")
    assert "OnFailAction.EXCEPTION" in source


def test_the_least_recently_pushed_live_project_is_the_one_the_page_names(
    page: str, evidence: Path
) -> None:
    """A superlative that outlives its evidence is a false claim with a green suite."""
    live = {key: item for key, item in records(evidence).items() if not item["archived"]}
    oldest = min(live, key=lambda key: live[key]["pushed_at"])
    phrase = "the longest since its last push"
    assert flatten(page).count(phrase) == 1, phrase
    assert phrase in flatten(section(page, live[oldest]["full_name"].split("/")[1]))


def test_the_moderation_taxonomy_matches_the_checked_in_response(page: str, evidence: Path) -> None:
    # Collapse the wrapping but keep the backticks: the names are code spans.
    stated = CATEGORIES.search(re.sub(r"\s+", " ", page))
    assert stated is not None, "the page must state how many moderation categories there are"
    named = re.findall(r"`([a-z/-]+)`", stated.group(2))
    assert len(named) == int(stated.group(1))
    source = (evidence / "openai-moderation.txt").read_text(encoding="utf-8")
    block = re.search(r'"categories" : \{(.*?)\}', source, re.S)
    assert block is not None, "the checked-in response must carry the categories object"
    assert re.findall(r'"([a-z/-]+)" :', block.group(1)) == named


def test_the_page_claims_no_rename_the_evidence_does_not_record(page: str) -> None:
    """docs/evidence/ records a repository's current identity, never a redirect.

    Two bullets used to say `gh api repos/<old>` "now resolves to" `<new>`, which
    nothing checked in supports: the records carry `full_name` and no request path.
    Either the evidence grows a `requested` field or the page does not say it.
    """
    assert "now resolves to" not in page
    assert "formerly" not in page


def test_every_section_names_the_repository_the_evidence_records(page: str, evidence: Path) -> None:
    for key, record in records(evidence).items():
        heading = section(page, key).splitlines()[0]
        assert f"`{record['full_name']}`" in heading, heading


#: A section on this page that is not one of the repositories under
#: docs/evidence/*.json, and the excerpt it is read from. There is no third
#: kind: a heading that is neither is a project nobody fetched anything about.
NON_REPO_SECTIONS = {
    "Claude Code permissions and hooks": "claude-code-hooks.txt",
    "Provider content filters (OpenAI moderation endpoint)": "openai-moderation.txt",
}

#: The one heading that compares nothing and needs no evidence.
CLOSING_SECTION = "When not to use egresswall"


def test_the_page_has_no_section_no_evidence_file_backs(page: str, evidence: Path) -> None:
    """A whole fabricated competitor section was invisible to every test here.

    The figure, licence, tag and quotation checks all iterate over the evidence
    records, so they see every project that *has* a record and nothing at all
    about a project that does not. This iterates the other way -- over the
    page -- so a section can only exist if something under docs/evidence/ backs
    it, and the two sections that are not repositories cite the excerpt they
    are read from.
    """
    headings = set(re.findall(r"^## (.+)$", page, re.MULTILINE))
    repos = {section(page, key).splitlines()[0] for key in records(evidence)}
    assert headings == repos | set(NON_REPO_SECTIONS) | {CLOSING_SECTION}, headings
    for heading, file in NON_REPO_SECTIONS.items():
        source = (evidence / file).read_text(encoding="utf-8").splitlines()[0]
        assert source.startswith("# source: "), file
        assert source.split(": ", 1)[1] in section(page, heading), (heading, file)


def test_refreshing_writes_nothing_when_a_source_lost_an_anchor(repo_root: Path) -> None:
    """The script's docstring promises a failing diff, not a silent rewrite."""
    source = (repo_root / "scripts" / "refresh_evidence.py").read_text(encoding="utf-8")
    body = source.split("def main()")[1]
    assert body.index("if missing:") < body.index("path.write_text(body")
    assert "write_text" not in body.split("if missing:")[0]


# --- fix pass 5: what the page says about itself ------------------------------


def test_the_page_states_the_detector_count_the_code_has(page: str) -> None:
    """ "ten regex detectors" is a word, so the digit test never saw it."""
    from egresswall import DETECTORS

    words = {3: "three", 6: "six", 10: "ten"}
    assert f"{words[len(DETECTORS)]} regex detectors are not an NER model" in flatten(page)


def test_the_page_says_only_what_its_own_test_checks(page: str) -> None:
    """The sentence naming this file's guarantees has to be true of this file."""
    flat = flatten(page)
    assert (
        "tests/test_comparison_truth.py fails if a figure, a licence, a release tag or a "
        "quotation on this page is not in them" in flat
    )
    # "a figure" is true because tests/test_doc_numbers.py runs over this page
    # too: the set of numbers on it is asserted, not only the ones this file
    # knows to look for.
    from test_doc_numbers import DOCUMENTS

    assert "docs/comparison.md" in DOCUMENTS


#: Claims no evidence under docs/evidence/ could settle. The pyproject
#: description had this guard and the two documents a reader actually reads did
#: not, so a superlative could be written straight into the comparison page.
SUPERLATIVES = (
    "fastest",
    "most complete",
    "trusted by",
    "best",
    "leading",
    "enterprise",
    # Comparative forms: an injected "faster than Presidio on every payload" and
    # "detection is exhaustive for the classes listed" both survived the suite.
    "faster than",
    "more complete than",
    "exhaustive",
)


@pytest.mark.parametrize("document", ["README.md", "docs/comparison.md"])
def test_no_document_makes_a_superlative_claim(document: str, repo_root: Path) -> None:
    text = (repo_root / document).read_text(encoding="utf-8").lower()
    for word in SUPERLATIVES:
        assert word not in text, (document, word)


def test_the_page_promises_no_more_evidence_than_is_checked_in(page: str) -> None:
    """The guarantee used to be "every claim", and the feature paragraphs are not one.

    Each project's "what it does that egresswall does not" paragraph names
    features that appear in no checked-in excerpt -- re-asking, a server mode,
    tracing, NER. They are a reading of the linked docs, and the page has to say
    so rather than promise evidence it does not carry.
    """
    flat = flatten(page)
    assert (
        "Every figure, licence, release tag, date and quotation below comes from a page or "
        "API response fetched on 2026-08-30" in flat
    )
    assert "Every claim below comes from" not in flat
    assert (
        "are the author's reading of each project's own documentation on that date, "
        "not quotations, and nothing under evidence/ backs them" in flat
    )
