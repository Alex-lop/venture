"""docs/comparison.md may not say anything the checked-in evidence does not support.

Five mechanisms, the same discipline as `tests/test_readme_truth.py`:

* every quotation is in a file under `docs/evidence/`;
* every figure equals the field of the fetched metadata, **in its own row**;
* every row of the comparison table is the declared one, cell by cell, with the
  adoption cell -- licence included -- built from that repository's metadata, so
  a fabricated row, a swapped licence and an invented adoption claim all fail;
* every comparative sentence about an incumbent is bound to the phrase in the
  fetched source that supports it;
* every `every`/`all` claim is on a closed list, and every capability list is
  the length declared here.

`test_the_page_fails_on_each_injected_falsehood` replays the falsehoods an audit
shipped past the earlier version of this file.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest
from conftest import evidence_corpus, flatten, list_items, unquoted

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

#: The adoption cell of a repository's row, built from that repository's fetched
#: metadata. The licence is part of it, so swapping two projects' licences is a
#: cell that stops matching -- checking only that "MIT" appears somewhere on a
#: page where both projects are MIT proves nothing.
ADOPTION = (
    "{stargazers_count:,} stars, {forks_count} forks, {open_issues_count} open issues, last push {pushed}, {licence}"
)

#: Every row of the comparison table, cell by cell. The table is the page's one
#: factual claim about somebody else's project; a fabricated fourth row, an
#: invented adoption boast and a characterisation the page says it will not make
#: are all a row that stops matching. `None` for the adoption cell means "build
#: it from that repository's metadata".
ROWS: dict[str, tuple[str | None, str | None, str]] = {
    "**Claude Code `/doctor`**": (
        '"Run a setup checkup that diagnoses issues and can fix them. Checks installation health, including '
        'duplicate or leftover installs, PATH problems, and unparseable settings files." Further down its own '
        'list, it also "trims checked-in CLAUDE.md files by cutting content Claude could derive from the '
        'codebase". From the terminal, `claude doctor` "prints read-only installation diagnostics without '
        'starting a session."',
        "Bundled with Claude Code",
        "Diagnoses the *installation*. It does not read your `db/` directory or your git history, and it does "
        "not know which of your paths an agent should never write.",
    ),
    "**`kenryu42/cc-safety-net`**": (
        '"A pre-execution guard for AI coding agents. It blocks destructive Git and file system commands, plus '
        'common attempts to access sensitive files, before a tool call runs."',
        None,
        "Blocks a *generic* set of dangerous commands. A generic tool has two settings — allow and block — "
        "because it has never read your repository. The setting that is right for your build cache is wrong "
        "for your fixtures.",
    ),
    "**`microsoft/agentrc`**": (
        '"Get your repo ready for AI." — its own description, and all this page will say about it: the only '
        "source checked in for it is the repository metadata below, and that says what it is for, not what it "
        "emits.",
        None,
        "Not characterised here. Read its README before you decide between them; this page does not describe a "
        "tool it has not fetched a source for.",
    ),
}

#: Which fetched metadata file each repository row's figures come from.
ROW_SOURCE = {
    "**`kenryu42/cc-safety-net`**": "kenryu42__cc-safety-net.txt",
    "**`microsoft/agentrc`**": "microsoft__agentrc.txt",
}

#: Every comparative sentence the page makes about an incumbent, and the phrase
#: in the fetched source that has to still be there for it to be true. A claim
#: about what somebody else's tool does *not* do is only as good as the source
#: list it was read off -- and the page's own evidence said `/doctor` reads
#: checked-in `CLAUDE.md` files, which an earlier draft of the sentence denied.
CLAIMS = {
    "/doctor diagnoses the installation and offers to trim your CLAUDE.md.": (
        "claude-code-commands.txt",
        "trims checked-in CLAUDE.md files by cutting content Claude could derive from the codebase",
    ),
    "cc-safety-net blocks a generic list of destructive commands before a tool call runs.": (
        "kenryu42__cc-safety-net.txt",
        "It blocks destructive Git and file system commands",
    ),
    "Diagnoses the installation. It does not read your db/ directory or your git history": (
        "claude-code-commands.txt",
        "prints read-only installation diagnostics without starting a session",
    ),
    "/doctor ships with the agent and prints read-only installation diagnostics.": (
        "claude-code-commands.txt",
        "prints read-only installation diagnostics without starting a session",
    ),
    "cc-safety-net blocks destructive Git and file system commands before a tool call runs.": (
        "kenryu42__cc-safety-net.txt",
        "It blocks destructive Git and file system commands, plus common attempts to access sensitive "
        "files, before a tool call runs",
    ),
    "Each is better than anything this package would write for you at the thing it does, and the second "
    "of them enforces.": (
        "kenryu42__cc-safety-net.txt",
        "It blocks destructive Git and file system commands",
    ),
}

#: The README's one comparative paragraph, bound the same way. It named three
#: incumbents in a sentence characterising two of them, and `microsoft/agentrc`
#: -- which this page promises not to characterise -- picked up "diagnose an
#: installation" and "block a generic command list" for free.
README_CLAIMS = {
    "/doctor diagnoses the installation and cc-safety-net blocks a generic list of destructive commands "
    "before a tool call runs.": (
        "kenryu42__cc-safety-net.txt",
        "before a tool call runs",
    ),
    "microsoft/agentrc is not characterised, here or there: the only source checked in for it is its "
    "repository metadata, and that says what it is for rather than what it emits.": (
        "microsoft__agentrc.txt",
        "Get your repo ready for AI",
    ),
}

#: Sentences the page states about itself rather than about an incumbent, held
#: verbatim. An audit replaced "`cc-safety-net` could add a `--report` flag in an
#: afternoon" with "already ships a `--report` flag that prints the same
#: inventory" and the suite passed: the sentence carried no digit and no figure,
#: and it was a capability claim no fetched source supported.
#: The phrase in a fetched source behind the one adoption cell that is not built
#: from repository metadata. Every other claim about an incumbent on this page is
#: bound to a fetched file; this cell was hardcoded in the test instead.
DOCTOR_ADOPTION = ("claude-code-commands.txt", "including built-in commands and bundled skills")

#: The fetched source behind each of the three one-line facts §5 of every report
#: states -- `guardrail_checkup._report.NOT_REPLACED`. The report is the artifact
#: the page says is honest about these three, so its sentences about somebody
#: else's project are bound the way the page's own are.
#: Every `##` heading on the page, in order. A whole invented section is the one
#: shape none of the mechanisms above reads: an audit shipped a *## Telemetry*
#: section into `README.md` green, and this page had the same hole.
HEADINGS = [
    "The three you will meet first",
    "The one-line difference",
    "What this one deliberately does not do",
    "Where it sits with the sibling packages",
]

REPORT_SOURCES = {
    "Claude Code's `/doctor`": ("claude-code-commands.txt", "/doctor"),
    "`kenryu42/cc-safety-net`": ("kenryu42__cc-safety-net.txt", "kenryu42/cc-safety-net"),
    "`microsoft/agentrc`": ("microsoft__agentrc.txt", "microsoft/agentrc"),
}

PAGE_SENTENCES = (
    "That difference is thin. This package is not defended by capability; it is defended by being the "
    "artifact you run first, and by being honest about the other three in the report it writes.",
    # The sibling paragraph. Its three sentences are capability claims about
    # this package and the two it is built on, and an audit reversed two of them
    # -- "rewrites your plan to fit the policy", "applies them for you" --
    # inside prose no closed list held.
    "This package instead reads your git history and `CODEOWNERS` and hands back what is enforced today, what a "
    "generic scorer will get wrong about you specifically, and up to three ranked places a hook may pay for itself.",
    "`agent-plan-lint` validates a plan against a policy. `egresswall` screens what a tool hands back. "
    "`guardrail-checkup` is the thing you run before you have either: when their signature keys are absent it "
    "drafts a starter policy, when an MCP configuration exists it drafts a screened copy, and it applies neither.",
    # The three sentences an audit reversed in prose no closed list held: the
    # page's own no-enforcement promise, twice, and a capability invented for a
    # shipped script.
    "That is what this one does, and it enforces none of it.",
    "Each is better than anything this package would write for you at the thing it does, and the second of "
    "them enforces. This one reports, and the report is what you read before deciding what to enforce.",
    "Re-fetch with `python3 scripts/refresh_evidence.py`, which exits non-zero if a source stopped saying "
    "what this page says it says.",
)

#: The page's own capability list, whole. Held by its length alone, an audit
#: rewrote the body of a bullet -- "It writes a hook and installs it into
#: `.claude/hooks/` for you" -- and the count did not move.
PAGE_ITEMS = {
    "What this one deliberately does not do": [
        "- **No readiness score, no grade, no percentage for your repository.** §3 of the report is a "
        "judgement about your code and a number would launder it into something it is not. The report heads "
        "§3 *Invariant candidates*, says a human confirms or replaces them, and names the ones whose only "
        "evidence is a path match. The number §3 prints beside each candidate is the evidence tally that "
        "section defines, not a rating.",
        "- **No enforcement.** It writes a hook; it never installs one. It writes a policy; it never applies "
        "one. Every draft goes to the directory you name with `--emit-dir`, and the tool refuses to write "
        "anywhere inside the repository it read.",
        "- **No model call, no network.** The report is deterministic: the same commit, with "
        "`SOURCE_DATE_EPOCH` set, produces the same bytes apart from the command line the report records. "
        "Without `SOURCE_DATE_EPOCH` the date line moves and nothing else does. That is also why §3 cannot "
        "read your architecture, and the report says so.",
        "- **It does not run the tools it names.** §2 of the report is the falsifier list to have ready when "
        "*you* run them, built from your own files, with the command that disproves each claim. "
        "`guardrail-checkup` starts no `npx` and opens no socket.",
    ],
}

#: Every `every`/`all` claim on the page, and what makes it true. Closed, like
#: README.md's and CHANGELOG.md's.
DECLARED_ABSOLUTES = {
    "every quotation and number on this page is checked": "test_every_quotation_on_the_page_is_in_a_checked_in_source",
    "all this page will say about it": "test_every_row_of_the_table_is_the_declared_one",
    "Every draft goes to the directory you name": "test_writing_inside_the_repository_under_inspection_is_refused",
}

#: How many items each list on the page carries. A fabricated comparison row is
#: a new item here.
LIST_LENGTHS = {
    "The three you will meet first": 4,  # the header row plus three projects
    "What this one deliberately does not do": 4,
}


@pytest.fixture(scope="session")
def comparison(repo_root: Path) -> str:
    return (repo_root / "docs" / "comparison.md").read_text(encoding="utf-8")


def metadata(slug: str) -> dict:
    body = (EVIDENCE / slug).read_text(encoding="utf-8")
    return json.loads(body[body.index("{") :])


def adoption_cell(slug: str) -> str:
    payload = metadata(slug)
    return ADOPTION.format(**payload, pushed=payload["pushed_at"][:10], licence=(payload["license"] or {})["spdx_id"])


def rows(comparison: str) -> dict[str, tuple[str, ...]]:
    """The comparison table, keyed by its first cell."""

    out = {}
    for line in list_items(comparison, "The three you will meet first"):
        cells = tuple(item.strip() for item in line.strip().strip("|").split(" | "))
        out[cells[0]] = cells[1:]
    return out


def check_page(comparison: str) -> None:
    """Every mechanism this file has, over the page given. The injection hook."""

    assert unquoted(comparison) == []
    check_rows(comparison)
    check_claims(comparison)
    check_page_sentences(comparison)
    check_page_items(comparison)
    check_absolutes(comparison)
    check_lists(comparison)
    check_numbers(comparison)
    check_fetched_date(comparison)
    check_determinism(comparison)
    check_headings(comparison)


def check_headings(comparison: str) -> None:
    """The page's `##` headings, in order: an invented section is a heading nothing reads."""

    found = [line[3:].strip() for line in comparison.splitlines() if line.startswith("## ")]
    assert found == HEADINGS, found


def check_determinism(text: str) -> None:
    """Without SOURCE_DATE_EPOCH the date line moves, so the unqualified form is false.

    Run over `README.md` and `CHANGELOG.md` as well as this page: the CHANGELOG
    stated the banned form unchallenged, because this check read one file.
    """

    flat = flatten(text).lower()
    assert "the same commit, with source_date_epoch set, produces the same bytes" in flat
    assert "the report is deterministic: the same commit produces the same bytes." not in flat
    assert "the report is deterministic. the same commit produces the same bytes" not in flat


def check_rows(comparison: str) -> None:
    found = rows(comparison)
    assert set(found) == {"", *ROWS}, sorted(found)  # the header row's first cell is empty
    for name, (does, adoption, denies) in ROWS.items():
        expected = (does, adoption or adoption_cell(ROW_SOURCE[name]), denies)
        assert found[name] == expected, (name, found[name])


def check_claims(text: str, claims: dict[str, tuple[str, str]] | None = None) -> None:
    flat = flatten(text)
    for sentence, (slug, phrase) in (claims or CLAIMS).items():
        assert flatten(sentence) in flat, sentence
        assert flatten(phrase) in flatten((EVIDENCE / slug).read_text(encoding="utf-8")), (slug, phrase)


def check_page_sentences(comparison: str) -> None:
    """The page's own closed sentences, word for word."""

    flat = flatten(comparison)
    for sentence in PAGE_SENTENCES:
        assert flatten(sentence) in flat, sentence


def check_page_items(comparison: str) -> None:
    """The page's closed lists, item by item and whole, not by their length."""

    for heading, expected in PAGE_ITEMS.items():
        found = [" ".join(item.split()) for item in list_items(comparison, heading)]
        assert found == expected, (heading, found)


def fetched_stamps() -> set[str]:
    """The `# fetched:` date on the second line of each fetched evidence file."""

    out = set()
    for path in sorted(EVIDENCE.glob("*.txt")):
        second = path.read_text(encoding="utf-8").splitlines()[1]
        if second.startswith("# fetched: "):
            out.add(second.removeprefix("# fetched: ").strip())
    return out


def check_fetched_date(comparison: str) -> None:
    """The page's own fetched-on date is the stamp inside the evidence files.

    The page's heading says every number on it is checked against a copy of its
    source, and this one was not: `check_numbers` tested membership of a
    hardcoded set, so the date could be swapped for another date that appears
    elsewhere on the page while every evidence file still said 2026-08-31.
    """

    stamps = fetched_stamps()
    assert stamps, "no evidence file carries a fetched date"
    found = re.search(r"Figures fetched \*\*(\d{4}-\d{2}-\d{2})\*\*", comparison)
    assert found is not None, "the page does not record when its figures were fetched"
    assert {found.group(1)} == stamps, (found.group(1), sorted(stamps))


def check_absolutes(comparison: str) -> None:
    rest = flatten(comparison)
    for phrase in DECLARED_ABSOLUTES:
        rest = rest.replace(flatten(phrase), " ")
    assert re.findall(r"(?i).{40}\b(?:every|all)\b.{40}", rest) == []


def check_lists(comparison: str) -> None:
    for heading, count in LIST_LENGTHS.items():
        found = list_items(comparison, heading)
        assert len(found) == count, (heading, len(found), found)


def check_numbers(comparison: str) -> None:
    declared = {"2026-08-31", "2026", "08", "31", "26", "2", "3", "1", "2.0"} | {
        literal for figures in FIGURES.values() for literal in figures
    }
    for number in NUMBER.findall(flatten(comparison)):
        assert number in declared, number


def test_every_quotation_on_the_page_is_in_a_checked_in_source(comparison: str) -> None:
    assert unquoted(comparison) == []


@pytest.mark.parametrize("slug", sorted(FIGURES))
def test_every_figure_on_the_page_is_the_value_in_the_fetched_metadata(comparison: str, slug: str) -> None:
    """Each figure equals its own repository's metadata, in its own row of the table.

    Checking only that a figure appears somewhere on the page passes when two
    repositories' figures are swapped, which would credit one project's
    adoption to the other under a heading that says every figure is checked.
    """

    payload = metadata(slug)
    name = payload["full_name"]
    found = [line for line in comparison.splitlines() if f"`{name}`" in line and line.startswith("|")]
    assert len(found) == 1, (name, found)
    for literal, field in FIGURES[slug].items():
        value = str(payload[field])
        expected = value[:10] if field == "pushed_at" else value
        assert literal.replace(",", "") == expected, (slug, field, literal, value)
        assert literal in found[0], (name, literal, found[0])


def test_every_row_of_the_table_is_the_declared_one(comparison: str) -> None:
    """Row count, and every cell of every row -- the adoption cell from the metadata."""

    check_rows(comparison)


def test_every_comparative_sentence_is_backed_by_a_phrase_in_its_source(comparison: str) -> None:
    check_claims(comparison)
    check_page_sentences(comparison)


def test_the_readmes_comparison_paragraph_is_backed_by_a_phrase_in_its_source(repo_root: Path) -> None:
    """The README states the same comparison in one sentence, and it went unread."""

    check_claims((repo_root / "README.md").read_text(encoding="utf-8"), README_CLAIMS)


def test_every_absolute_claim_on_the_page_is_on_the_declared_list(comparison: str) -> None:
    check_absolutes(comparison)


def test_every_list_on_the_page_is_the_length_the_suite_declares(comparison: str) -> None:
    check_lists(comparison)


def test_every_number_on_the_page_is_a_figure_this_test_knows(comparison: str) -> None:
    """The page states no number the code decides; every one is an incumbent's."""

    check_numbers(comparison)


def test_the_doctor_adoption_cell_is_backed_by_a_phrase_in_its_source(comparison: str) -> None:
    """The one incumbent statement on the page with no fetched phrase behind it.

    Every figure in the other two adoption cells is read off that repository's
    fetched metadata; this one was a string in this file and nowhere else.
    """

    name, phrase = DOCTOR_ADOPTION
    cell = ROWS["**Claude Code `/doctor`**"][1]
    assert cell is not None and cell in comparison
    source = flatten((EVIDENCE / name).read_text(encoding="utf-8"))
    assert flatten(phrase) in source, phrase
    assert "/doctor" in source


def test_the_report_says_about_the_other_three_only_what_a_fetched_source_says(comparison: str) -> None:
    """The page's claim that the report is honest about the other three, made true.

    "It is defended by being honest about the other three in the report it
    writes" is held word for word in PAGE_SENTENCES, and no rendered report
    named one of them: the suite pinned a false sentence in place. §5 names them
    now, and every phrase it quotes is bound here to the file it came from --
    the same discipline the page itself is held to, because a report handed to a
    stranger states these facts about somebody else's project.
    """

    from guardrail_checkup._report import NOT_REPLACED

    assert "honest about the other three in the report it" in flatten(comparison)
    assert len(NOT_REPLACED) == len(REPORT_SOURCES) == 3
    for name, fact in NOT_REPLACED:
        file_name, identifier = REPORT_SOURCES[name]
        source = flatten((EVIDENCE / file_name).read_text(encoding="utf-8"))
        assert flatten(fact) in source, fact
        assert identifier in source, identifier


def test_every_heading_on_the_page_is_one_the_suite_declares(comparison: str) -> None:
    check_headings(comparison)


def test_the_page_names_every_incumbent_the_evidence_covers(comparison: str) -> None:
    corpus = evidence_corpus()
    for name in ("kenryu42/cc-safety-net", "microsoft/agentrc"):
        assert name in comparison
        assert name in corpus


def test_the_page_says_the_incumbents_are_worth_installing(comparison: str, repo_root: Path) -> None:
    """The honest-comparison rule: the page recommends the free floor, not against it."""

    assert "Install the incumbents." in comparison
    assert "Install the first two anyway." in (repo_root / "README.md").read_text(encoding="utf-8")


def test_the_determinism_claim_carries_the_qualifier_the_readme_carries(comparison: str) -> None:
    check_determinism(comparison)


def test_the_page_records_the_date_and_the_refresh_command(comparison: str, repo_root: Path) -> None:
    assert "python3 scripts/refresh_evidence.py" in comparison
    assert (repo_root / "scripts" / "refresh_evidence.py").exists()


def test_the_pages_fetched_date_is_the_stamp_in_every_evidence_file(comparison: str) -> None:
    check_fetched_date(comparison)


def test_every_list_on_the_page_is_the_text_the_suite_declares(comparison: str) -> None:
    check_page_items(comparison)


def test_the_script_fetches_the_hosts_its_docstring_names(repo_root: Path) -> None:
    """CONTRIBUTING states a host count; the script's own docstring has to name them."""

    from urllib.parse import urlsplit

    path = repo_root / "scripts" / "refresh_evidence.py"
    spec = importlib.util.spec_from_file_location("refresh_evidence_hosts", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    hosts = {urlsplit(url).netloc for url in module.urls()}

    assert len(hosts) == 2, sorted(hosts)
    for host in hosts:
        assert f"`{host}`" in module.__doc__, host
    # And it names the file this assertion lives in. The docstring said
    # tests/test_readme_truth.py, which reads nothing in that script; the sdist
    # ships scripts/, so the false sentence was published with the package.
    assert f"tests/{Path(__file__).name}" in module.__doc__, module.__doc__
    contributing = (repo_root / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert f"which does fetch {('one', 'two', 'three')[len(hosts) - 1]} named hosts" in " ".join(contributing.split())


def test_every_sentence_the_page_quotes_is_an_anchor_a_refresh_would_fail_on(comparison: str, repo_root: Path) -> None:
    """CONTRIBUTING: quoting a source means adding it to scripts/refresh_evidence.py.

    Without this, a refresh exits 0 while the page keeps quoting text the source
    no longer contains, and the release checklist's step proves nothing.
    """

    path = repo_root / "scripts" / "refresh_evidence.py"
    spec = importlib.util.spec_from_file_location("refresh_evidence", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    anchors = [item for _, phrases in module.PAGES.values() for item in phrases]
    anchors += [item for phrases in module.REPOS.values() for item in phrases]
    corpus = flatten(" ".join(anchors))
    for quote in re.findall(r'"([^"]{12,})"', flatten(comparison)):
        assert quote.strip(". ") in corpus, quote


def test_every_evidence_file_records_its_source_and_its_date() -> None:
    files = sorted(EVIDENCE.glob("*.txt"))
    assert len(files) >= 4
    for path in files:
        head = path.read_text(encoding="utf-8").splitlines()[:3]
        assert head[0].startswith("# source: "), path.name
        assert re.fullmatch(r"# (fetched|command): .+", head[1]), path.name


# --- the injected falsehoods ------------------------------------------------------


#: The falsehoods an audit injected one at a time into the earlier version of
#: this page. Every one of them shipped green then.
INJECTIONS = [
    (
        "A10 a swapped licence",
        "last push 2026-08-31, MIT",
        "last push 2026-08-31, Apache-2.0",
    ),
    (
        "A11 a fabricated fourth row",
        "\n\n## The one-line difference",
        '\n| **`acme/agent-warden`** | "Guardrails for coding agents." | 4,201 stars, 310 forks, 2 open issues, '
        "last push 2026-08-31, MIT | Nothing this one does. |\n\n## The one-line difference",
    ),
    (
        "A12 a characterisation the page says it will not make",
        "Not characterised here.",
        "Generates a repo-wide agent configuration and enforces it on every commit.",
    ),
    (
        "A13 an invented adoption boast",
        "1,517 stars, 75 forks",
        "the most widely installed of the three — 1,517 stars, 75 forks",
    ),
    (
        "A14 a reversed capability claim",
        "Blocks a *generic* set of dangerous commands.",
        "Blocks nothing until you write a policy for it.",
    ),
    (
        "A23 another reversed capability claim",
        "because it has never read your repository",
        "because it has already read your repository",
    ),
    (
        "A25 a comparative claim the evidence contradicts",
        "This package instead\nreads your git history and `CODEOWNERS`",
        "This package instead\nguesses from filenames and ignores git history and `CODEOWNERS`",
    ),
    (
        "A30 the unqualified determinism claim",
        "the same commit, with\n  `SOURCE_DATE_EPOCH` set, produces the same bytes apart from the command line the "
        "report\n  records. Without `SOURCE_DATE_EPOCH` the date line moves and nothing else does.",
        "the same commit produces the same bytes.",
    ),
    (
        "A31 a score for the repository",
        "**No readiness score, no grade, no percentage for your repository.**",
        "**A readiness score out of 100, and a grade.**",
    ),
    # The third audit: three more that shipped green, each next to the mechanism
    # that now catches it.
    (
        "X20 a count of the incumbents nothing decides",
        "Each is better than anything this package would write for you at the thing it does",
        "One of the three below is better than anything this package would write for you",
    ),
    (
        "X21 a capability claim no fetched source supports",
        "That difference is thin. This package is not defended by capability",
        "That difference is thin: `cc-safety-net` already ships a `--report` flag that prints the same "
        "inventory. This package is not defended by capability",
    ),
    (
        "X22 a characterisation of /doctor the evidence does not carry",
        "`/doctor` ships with the agent and prints read-only installation\ndiagnostics.",
        "`/doctor` ships with the agent and rewrites your `CODEOWNERS`.",
    ),
    # The fourth audit: four more that shipped green, each next to the mechanism
    # that now catches it.
    (
        "J04 a sibling package given a capability it does not have",
        "`agent-plan-lint` validates a plan against a policy.",
        "`agent-plan-lint` rewrites your plan to fit the policy.",
    ),
    (
        "J10 an enforcement claim inside a length-closed bullet",
        "It writes a hook; it never installs one.",
        "It writes a hook and installs it into `.claude/hooks/` for you.",
    ),
    (
        "J18 this package given a capability it denies",
        "drafts a\nscreened copy, and it applies neither.",
        "drafts a screened copy, and applies it for you.",
    ),
    (
        "N07 the page's own no-enforcement promise reversed",
        "That is what this one does, and it\nenforces none of it.",
        "That is what this one does, and it enforces the first of them for you.",
    ),
    (
        "N08 the same promise reversed in the opening paragraph",
        "This one reports, and the report is what you read before deciding\nwhat to enforce.",
        "This one reports and then enforces what you approve.",
    ),
    (
        "N22 a capability invented for a shipped script",
        "`python3 scripts/refresh_evidence.py`, which exits non-zero if a source stopped saying what\nthis "
        "page says it says.",
        "`python3 scripts/refresh_evidence.py`, which rewrites this page in place whenever a source has moved.",
    ),
    (
        "J24 the fetched-on date swapped for another date on the page",
        "Figures fetched **2026-08-31**",
        "Figures fetched **2026-08-26**",
    ),
]


@pytest.mark.parametrize("case", INJECTIONS, ids=[item[0] for item in INJECTIONS])
def test_the_page_fails_on_each_injected_falsehood(comparison: str, case: tuple[str, str, str]) -> None:
    _, true, false = case
    assert true in comparison, true
    with pytest.raises(AssertionError):
        check_page(comparison.replace(true, false, 1))


def test_the_page_as_checked_in_passes_every_mechanism(comparison: str) -> None:
    check_page(comparison)
