"""Every number in README.md and CHANGELOG.md is accounted for.

The rest of the doc-truth suite is a whitelist: it checks the claims it was told
about, which is why a figure with no test -- the memory numbers this pass
deleted -- could sit in the CHANGELOG for a release. This is the complement. The
*set* of numbers each document contains is asserted, so a new figure cannot
arrive unchecked; each number is either one the code decides (asserted against
the code, so either side changing fails), one another test in this suite pins
(the test is named, and asserted to exist), or declared prose -- a date, a
version, a Unicode code point, an example value -- with the reason recorded.
"""

from __future__ import annotations

import ast
import functools
import re
import tomllib
from pathlib import Path

import pytest
from conftest import flatten, fullwidth

from egresswall import (
    MAX_ALLOWED_DEPTH,
    MAX_DENIED_PATH_CHARS,
    MAX_FORBIDDEN_VALUES,
    Policy,
    _cli,
)
from egresswall._proxy import BLOCKED_CODE, MAX_LINE_BYTES

#: A run of digits that is not part of a word: 3.11 and 320.451.9977 are one
#: number each, and the 32001 of -32001 is the number in it.
NUMBER = re.compile(r"(?<![\w.])\d+(?:\.\d+)*")


def numbers(text: str) -> set[str]:
    return {match.group(0) for match in NUMBER.finditer(text)}


#: Every document this package ships that states a figure. docs/comparison.md is
#: here because its own test is a whitelist too: it checks the figures it knows
#: to look for, so the set of numbers on the page needs this to be constrained.
DOCUMENTS = ["README.md", "CHANGELOG.md", "docs/comparison.md"]


def code() -> dict[str, dict[str, object]]:
    """Doc literal -> the value the code has, per document."""
    policy = Policy()
    shared = {
        "20": _cli.MAX_REPORTED,
        "4000": _cli.MAX_REPORT_CHARS,
        "10000": MAX_FORBIDDEN_VALUES,
        "128": 128,  # the join_token detector's upper hex bound, below
        "64": 64,  # and its lower one
    }
    return {
        "README.md": shared
        | {
            "32": policy.max_depth,
            "33": policy.max_depth + 1,
            "100000": policy.max_nodes,
            "1048576": policy.max_string_length,
            "2097152": policy.max_total_length,
            "1": policy.max_string_length // 2**20,
            "2": policy.max_string_length // 2**20 * 2,
            "8": MAX_LINE_BYTES // 2**20,
            "32001": -BLOCKED_CODE,
            "512": MAX_DENIED_PATH_CHARS,
        },
        "CHANGELOG.md": shared
        | {
            "4176": stripped_set_size(),
            "500": MAX_ALLOWED_DEPTH,
            "512": MAX_DENIED_PATH_CHARS,
            "40": 40,  # the openai_key detector's minimum body length, below
        },
        # The comparison page states no figure the code decides: every number on
        # it is an incumbent's, and every one of those is pinned to the response
        # under docs/evidence/ that carries it.
        "docs/comparison.md": {},
    }


#: How many code points `_document_candidate` strips from the ends of a string
#: before it decides whether the string is a document -- the whole
#: `Default_Ignorable_Code_Point` set plus the two drawn blank without being in
#: it. Swept once: the CHANGELOG states this number.
@functools.cache
def stripped_set_size() -> int:
    from egresswall._core import _BLANK_BY_GLYPH, _DEFAULT_IGNORABLE

    return len(
        {point for point in range(0x110000) if _DEFAULT_IGNORABLE.match(chr(point))}
        | {ord(char) for char in _BLANK_BY_GLYPH}
    )


def test_the_changelog_names_the_strip_set_the_code_has(repo_root: Path) -> None:
    """The code points and the Unicode version this file cites are the code's.

    `_DEFAULT_IGNORABLE` says which revision of DerivedCoreProperties.txt it was
    transcribed from; a bullet naming a different one is a bullet nobody can
    check the transcription against.
    """
    from egresswall import _core

    text = (repo_root / "CHANGELOG.md").read_text(encoding="utf-8")
    source = Path(_core.__file__).read_text(encoding="utf-8")
    version = re.search(r"unicode\.org/Public/([\d.]+)/ucd/", source).group(1)
    assert version == "15.1.0" and version in text
    for point in (0x115F, 0x1160, 0x3164, 0xFFA0):
        assert f"U+{point:04X}" in text
        assert _core._DEFAULT_IGNORABLE.match(chr(point)), hex(point)
    for point in (0x2800, 0x1D159):
        assert f"U+{point:04X}" in text
        assert chr(point) in _core._BLANK_BY_GLYPH, hex(point)


def test_the_join_token_bounds_in_the_docs_are_the_regex_bounds() -> None:
    """The 64 and 128 both documents state are the quantifier in the pattern."""
    from egresswall._core import _JOIN_TOKEN, _OPENAI_KEY

    assert re.search(r"\[0-9a-f\]\{(\d+),(\d+)\}", _JOIN_TOKEN.pattern).groups() == ("64", "128")
    assert re.search(r"\{(\d+),\}", _OPENAI_KEY.pattern).group(1) == "40"


#: Every star count, licence, release tag and per-project date on the comparison
#: page is read back out of docs/evidence/ by this one test.
FIGURES = "test_the_figures_for_each_project_match_its_api_response"

#: The four Hangul fillers, the Braille blank and the musical null notehead the
#: README names by code point are read back out of the code by this one test.
#: `U+115F` and `U+1D159` reach the digit regex as "115" and "1", so the fillers
#: are pinned by the three literals that survive it plus the Braille blank.
STRIP_POINTS = "test_the_readme_names_the_code_points_the_strip_set_covers"

#: The same code points on the page PyPI links as Changelog, plus the revision
#: of DerivedCoreProperties.txt the transcription cites.
CHANGELOG_STRIP_POINTS = "test_the_changelog_names_the_strip_set_the_code_has"

#: Doc literal -> the test in this suite that pins it. The test has to exist.
PINNED = {
    "README.md": {
        "675": "test_the_readme_test_count_matches_the_suite",
        "49": "test_the_readme_hostile_server_count_matches_the_suite",
        "200": "test_the_readme_conversation_length_matches_the_suite",
        "9": "test_the_readme_pathological_input_count_matches_the_suite",
        "3.11": "test_the_readme_test_matrix_matches_the_ci_workflow",
        "3.12": "test_the_readme_test_matrix_matches_the_ci_workflow",
        "3.13": "test_the_readme_test_matrix_matches_the_ci_workflow",
        "2.0": "test_every_runnable_readme_command_prints_what_the_readme_shows",
        "6": "test_every_runnable_readme_command_prints_what_the_readme_shows",
        "0.1.0": "test_the_readme_version_matches_the_package",
        "6789": "test_the_readme_says_which_identifiers_need_a_separator",
        "123456789": "test_the_readme_says_which_identifiers_need_a_separator",
        "6175550142": "test_the_readme_says_which_identifiers_need_a_separator",
        "3": "test_the_readme_counts_the_surfaces_the_demo_exercises",
        "115": STRIP_POINTS,
        "1160": STRIP_POINTS,
        "3164": STRIP_POINTS,
        "2800": STRIP_POINTS,
    },
    "CHANGELOG.md": {
        "0.1.0": "test_the_readme_version_matches_the_package",
        "13": "test_the_moderation_taxonomy_matches_the_checked_in_response",
        "123456789": "test_the_readme_says_which_identifiers_need_a_separator",
        "6175550142": "test_the_readme_says_which_identifiers_need_a_separator",
        "65": "test_the_join_token_detector_covers_every_shape_the_readme_lists",
        "115": CHANGELOG_STRIP_POINTS,
        "1160": CHANGELOG_STRIP_POINTS,
        "3164": CHANGELOG_STRIP_POINTS,
        "2800": CHANGELOG_STRIP_POINTS,
        "15.1.0": CHANGELOG_STRIP_POINTS,
    },
    # An incumbent's star count, licence, release tag or date is a claim about
    # someone else's project, so every one of them names the test that reads it
    # back out of docs/evidence/. Without this entry the *set* of numbers on the
    # page was unconstrained: a whole dated numeric claim about a competitor
    # could be added and the suite stayed green.
    "docs/comparison.md": {
        "10.7": FIGURES,
        "3.2": FIGURES,
        "7.3": FIGURES,
        "3.0": FIGURES,
        "380": FIGURES,
        "2.2.364": FIGURES,
        "2.0": FIGURES,
        "01": FIGURES,
        "07": FIGURES,
        "08": FIGURES,
        "14": FIGURES,
        "19": FIGURES,
        "21": FIGURES,
        "22": FIGURES,
        "27": FIGURES,
        "28": FIGURES,
        "30": FIGURES,
        "2026": "test_the_page_states_the_fetch_date_the_evidence_carries",
        "13": "test_the_moderation_taxonomy_matches_the_checked_in_response",
        "25": "test_every_quotation_on_the_page_is_in_the_checked_in_sources",
    },
}

#: Doc literal -> why it is prose rather than a claim about the code.
PROSE = {
    "README.md": {
        "0": "the exit status of a clean run, and the [0] of a JSON path",
        "45": "an example SSN's middle group",
        "60": "the '60 seconds' heading",
        "88231": "the example member id in the fixtures",
        "9931": "the example internal case id",
        "123": "an example SSN's first group",
        "320.451.9977": "the example build string that trips the phone detector",
        "2011": "U+2011, a Unicode code point",
        "2024": "U+2024, a Unicode code point",
        "2026": "the year the hooks page was fetched",
        "08": "the month the hooks page was fetched",
        "30": "the day the hooks page was fetched",
    },
    "docs/comparison.md": {
        "2": "the exit code the hook uses",
        "9931": "the example internal case id",
    },
    "CHANGELOG.md": {
        "0": "the 0 of a falsy value a denied path still refuses",
        "1": "the exit code Claude Code treats as non-blocking",
        "2": "the exit code the hook uses instead",
        "3": "a heading level and the count of surfaces",
        "7": "the example request id echoed as a string",
        "8": "the 8 MiB line limit and the UTF-8 in 'not valid UTF-8'",
        "88231": "the example member id in the fixtures",
        "123": "an example non-object policy",
        "128": "the join_token upper bound",
        "200": "the 200-call conversation, in a sentence about the README's counts",
        "2026": "the release year",
        "30": "the release day",
        "08": "the release month",
    },
}


def suite_test_names(repo_root: Path) -> set[str]:
    names: set[str] = set()
    for path in sorted((repo_root / "tests").glob("test_*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                names.add(node.name)
    return names


@pytest.mark.parametrize("document", DOCUMENTS)
def test_every_number_in_the_document_is_pinned_or_declared(document: str, repo_root: Path) -> None:
    text = (repo_root / document).read_text(encoding="utf-8")
    accounted = set(code()[document]) | set(PINNED[document]) | set(PROSE[document])
    found = numbers(text)
    assert found - accounted == set(), f"{document} states a number nothing accounts for"
    assert accounted - found == set(), f"{document} no longer states a number declared here"


@pytest.mark.parametrize("document", DOCUMENTS)
def test_every_number_the_code_decides_is_the_number_the_document_states(
    document: str, repo_root: Path
) -> None:
    """Change the code or change the document and this fails; they move together."""
    text = (repo_root / document).read_text(encoding="utf-8")
    for literal, value in code()[document].items():
        assert str(value) == literal, (document, literal, value)
        assert literal in numbers(text), (document, literal)


@pytest.mark.parametrize("document", DOCUMENTS)
def test_every_number_said_to_have_a_test_has_that_test(document: str, repo_root: Path) -> None:
    names = suite_test_names(repo_root)
    for literal, test in PINNED[document].items():
        assert test in names, (document, literal, test)


def test_the_python_floor_in_the_readme_is_the_one_pyproject_requires(repo_root: Path) -> None:
    """3.11 is a version, so the number test treats it as pinned; this is the pin."""
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    floor = pyproject["project"]["requires-python"].lstrip(">=")
    assert f"Python {floor}+" in (repo_root / "README.md").read_text(encoding="utf-8")


#: The one line PyPI renders under the package name, and the terms it is filed
#: under. A superlative denylist was the only guard on the first and there was
#: none at all on the second, so the description could be rewritten into
#: "blocks or redacts ... with sub-millisecond screening" -- an inversion of the
#: promise plus an unmeasured latency claim -- and `hipaa`, `gdpr-compliant` and
#: `soc2` could be filed as keywords, with a green suite. Both are verbatim now.
DESCRIPTION = (
    "A value-level egress firewall for agent tool responses: blocks identifiers, "
    "secrets and denied fields instead of redacting them."
)
KEYWORDS = ["mcp", "agent", "security", "dlp", "egress", "guardrails", "claude-code", "pii"]


def test_the_package_description_and_keywords_are_the_pinned_ones(repo_root: Path) -> None:
    """The metadata PyPI renders, pinned the way a README sentence is."""
    project = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["description"] == DESCRIPTION
    assert project["keywords"] == KEYWORDS


def test_the_package_description_makes_no_superlative_claim(repo_root: Path) -> None:
    """The one-line pitch PyPI renders is not covered by any other doc-truth test."""
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    description = pyproject["project"]["description"].lower()
    for word in ("fastest", "most complete", "trusted by", "best", "leading", "enterprise"):
        assert word not in description, word
    # A speed claim needs a measurement this package publishes nowhere, so the
    # vocabulary for one is not available here either. ("redact" is: the line
    # says the package blocks *instead of* redacting, and the pin above is what
    # keeps that polarity.)
    for word in ("millisecond", "microsecond", "latency", "throughput"):
        assert word not in description, word


# --- fix pass 7: the counts these documents spell out ------------------------
#
# A count written as a word is invisible to NUMBER above, and the pin for one
# lived in tests/test_readme_truth.py and read README.md only -- so "one of the
# six" became "one of the eleven" in the CHANGELOG, and "Ten detectors" became
# "Twelve detectors" beside an exported constant that says ten, with the whole
# suite green. This is the digit machinery again, over words, over every
# document: each spelled-out count names the code expression that decides it,
# and the *set* of number-words on the page is asserted so a new one cannot
# arrive unchecked.

WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}
WORD = re.compile(r"(?<!\w)(" + "|".join(WORDS) + r")(?!\w)", re.IGNORECASE)


def word_counts() -> dict[str, int]:
    """Every count in the code that one of these documents spells out."""
    from test_detectors import SHAPES
    from test_proxy import PROXY_SECONDS, SPEC_MESSAGES

    from egresswall import DETECTORS, SECRET_MATERIAL, VIOLATION_CODES
    from egresswall._proxy import PROTOCOL_KEYS

    script = (Path(__file__).resolve().parent.parent / "demo" / "demo.sh").read_text(
        encoding="utf-8"
    )
    driven = {item["method"] for item in SPEC_MESSAGES.values() if "method" in item}
    notifications = {name for name in driven if name.startswith("notifications/")}
    tree = ast.parse((Path(__file__).resolve().parent / "test_detectors.py").read_text("utf-8"))
    hostile = [
        len(node.decorator_list[0].args[1].elts)
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_pathological_input_does_not_blow_up_the_matcher"
    ]
    return {
        "surfaces": sum(f"egresswall {word}" in script for word in ("check", "hook", "proxy")),
        "scenarios": len(re.findall(r'^echo "== \d+\.', script, re.MULTILINE)),
        "detectors": len(DETECTORS),
        "secret_detectors": sum(code == SECRET_MATERIAL for _, code in DETECTORS.values()),
        "violation_codes": len(VIOLATION_CODES),
        "protocol_keys": len(PROTOCOL_KEYS),
        "shapes": len(SHAPES),
        "spec_requests": len(driven) - len(notifications),
        "spec_notifications": len(notifications),
        "pathological": hostile[0],
        "proxy_seconds": int(PROXY_SECONDS),
    }


def word_pins() -> dict[str, tuple[tuple[str, tuple[int, ...]], ...]]:
    """Document -> (pattern naming a spelled-out count, the counts the code decides).

    Every group in the pattern is one count. The pattern has to match, every
    match of it has to spell the same counts, and those have to be the code's.
    """
    n = word_counts()
    refusers = ("(\\w+) of them can refuse instead", (2,))
    return {
        "README.md": (
            ("one screening core and (\\w+) places to put it", (n["surfaces"],)),
            (
                r"exercises all (\w+) surfaces end to end \((\w+) scenarios\)",
                (n["surfaces"], n["scenarios"]),
            ),
            ("A policy means the same thing on all (\\w+) surfaces", (n["surfaces"],)),
            ("adds (\\w+) secret detectors", (n["secret_detectors"],)),
            ("(\\w+) regular expressions, all listed above", (n["detectors"],)),
            ("The (\\w+) regexes match ASCII literals", (n["detectors"],)),
            ("The (\\w+) detectors and forbidden_values do read", (n["detectors"],)),
            ("Those (\\w+) names are matched", (n["protocol_keys"],)),
            ("in each of the (\\w+) shapes the suite measures", (n["shapes"],)),
            ("(\\w+) pathological inputs are", (n["pathological"],)),
            (
                "(\\w+) requests and (\\w+) notifications",
                (n["spec_requests"], n["spec_notifications"]),
            ),
            ("answering it in under (\\w+) seconds", (n["proxy_seconds"],)),
            # A claim about the page next door: R3 changed this count alone and
            # left docs/comparison.md saying something else in the same release.
            ("the (\\w+) that can refuse", (2,)),
        ),
        "CHANGELOG.md": (
            (
                "-- (\\w+) surfaces, (\\w+) secret detectors, (\\w+) regex detectors, "
                "(\\w+) protocol names",
                (
                    n["surfaces"],
                    n["secret_detectors"],
                    n["detectors"],
                    n["protocol_keys"],
                ),
            ),
            ("(\\w+) violation codes, exported as constants", (n["violation_codes"],)),
            ("(\\w+) detectors: email,", (n["detectors"],)),
            ("means the same thing on all (\\w+) surfaces", (n["surfaces"],)),
            (
                r"there are (\w+) surfaces and (\w+)\s+scenarios",
                (n["surfaces"], n["scenarios"]),
            ),
            ("(\\w+) pathological inputs, a 200-call conversation", (n["pathological"],)),
            ("one of the (\\w+) the suite measures at that cap", (n["shapes"],)),
            ("one of the (\\w+) the suite times under a second", (n["shapes"],)),
            (r"One of the (\w+) timing shapes measures them", (n["shapes"],)),
            ("the timing test\\s+measures (\\w+) shapes at exactly that cap", (n["shapes"],)),
            ("in each of the\\s+(\\w+) shapes the suite times", (n["shapes"],)),
            ("finishes in under (\\w+) seconds", (n["proxy_seconds"],)),
            ("accepts in under (\\w+) seconds", (n["proxy_seconds"],)),
        ),
        "docs/comparison.md": (
            ("(\\w+) regex detectors are not an NER model", (n["detectors"],)),
            refusers,
        ),
    }


#: Document -> the number-word it spells for a reason no code expression decides.
WORD_PROSE = {
    "README.md": {
        "one": "one core, one violation's share, one call, a one-off -- never a count of anything",
        "two": "two development dependencies, two boundaries in RegLineage, two sets of names",
        "four": "the four scenarios of the demo, pinned above",
    },
    "CHANGELOG.md": {
        "one": "one folding, one bucket, one token -- never a count of anything",
        "two": "the two install routes, the two surfaces that only report, the two lists",
        "five": "the five MCP field names that entry adds to the exemption, listed in it",
        "six": "six message shapes crossed the boundary before this release; history",
        "four": 'the quoted false claim "all four surfaces" this release fixed',
        "eleven": "the eleven protocol field names, counted in the pinned run above",
    },
    "docs/comparison.md": {
        "one": "'a blocked one', 'the one project here that will also raise' -- not a count",
        "two": "the projects that can refuse, pinned above",
    },
}


@pytest.mark.parametrize("document", DOCUMENTS)
def test_every_count_written_as_a_word_is_the_count_in_the_code(
    document: str, repo_root: Path
) -> None:
    """Change the code or change the document and this fails; they move together."""
    text = flatten((repo_root / document).read_text(encoding="utf-8"))
    for pattern, expected in word_pins()[document]:
        found = list(re.finditer(pattern, text))
        assert found, (document, pattern)
        for match in found:
            spelled = tuple(WORDS[group.lower()] for group in match.groups())
            assert spelled == expected, (document, pattern, match.group(0))


@pytest.mark.parametrize("document", DOCUMENTS)
def test_every_number_word_in_the_document_is_pinned_or_declared(
    document: str, repo_root: Path
) -> None:
    """The set, not the listing: a new spelled-out count cannot arrive unchecked."""
    text = flatten((repo_root / document).read_text(encoding="utf-8"))
    pinned = {
        group.lower()
        for pattern, _ in word_pins()[document]
        for match in re.finditer(pattern, text)
        for group in match.groups()
    }
    accounted = pinned | set(WORD_PROSE[document])
    found = {match.group(1).lower() for match in WORD.finditer(text)}
    assert found - accounted == set(), f"{document} spells a count nothing accounts for"
    assert accounted - found == set(), f"{document} no longer spells a count declared here"


# --- fix pass 7: the capability bullets PyPI links as Changelog ---------------
#
# The "Added" bullets are the surface listing a reader sees on the page PyPI
# links as Changelog, and nothing read them: a bullet advertising a subcommand
# the parser does not have, a flag this package refuses to grow, or the wrong
# hook stage all shipped green. Each bullet's first sentence is pinned here, so
# a capability claim moves only when someone changes this tuple beside it.

CHANGELOG_BULLETS = (
    "egresswall.screen(payload, policy, where=...) raises EgressViolation; "
    "egresswall.check(payload, policy) returns a list of Violation.",
    "egresswall.Policy: denied field paths, forbidden field names (with substring and suffix "
    "rules), forbidden literal values, per-class detectors, allowlisted governance tokens and "
    "email domains, exempt_keys for a name the field-name rules must skip, "
    "refuse_unparseable_embedded for whether a string that opens like a serialized document "
    "and will not parse is refused, and max_depth / max_nodes / max_string_length / "
    "max_total_length limits that fail closed.",
    "Ten detectors: email, ssn, phone, join_token, private_key, aws_access_key, github_token, "
    "anthropic_key, openai_key, bearer_token.",
    "Nine violation codes, exported as constants and as VIOLATION_CODES.",
    "egresswall check FILE.json (--policy, --format text|json, exit 1 on violations).",
    "egresswall hook: a Claude Code PostToolUse hook that screens tool_response and exits 2 "
    "with the reason on stderr.",
    "egresswall proxy -- <server command>: an MCP stdio proxy that replaces a violating result "
    "with a JSON-RPC error.",
    "docs/evidence/: the API responses and source excerpts behind every figure and quotation "
    "in README.md and docs/comparison.md, refreshed by scripts/refresh_evidence.py "
    "(deliberately not run in CI) and enforced by tests/test_comparison_truth.py.",
    "Doc-truth tests for the default limits, the dependency claims, the CI matrix and every "
    'quotation, for the "does not keep state, phone home or write files" claim (no module '
    "imports socket, ssl, urllib, http or requests, and a check run leaves its working "
    "directory as it found it), and for the sdist, which must ship exactly one package.",
)


def added_bullets(repo_root: Path) -> list[str]:
    """Every bullet under `### Added`, flattened, first sentence only."""
    text = (repo_root / "CHANGELOG.md").read_text(encoding="utf-8")
    section = text.split("### Added\n")[1].split("\n### ")[0]
    out = []
    for bullet in re.split(r"\n- ", "\n" + section.strip()):
        if bullet.strip():
            out.append(re.split(r"(?<=\.)\s", flatten(bullet.strip()), maxsplit=1)[0])
    return out


def test_every_capability_bullet_in_the_changelog_is_the_pinned_one(repo_root: Path) -> None:
    """Add a bullet, delete one, or invert one, and this fails."""
    assert tuple(added_bullets(repo_root)) == CHANGELOG_BULLETS


def test_every_subcommand_the_changelog_advertises_is_one_the_parser_defines(
    repo_root: Path,
) -> None:
    """A bullet advertising `egresswall check --redact FILE.json` shipped green."""
    parser = _cli.build_parser()
    defined = set(parser._subparsers._group_actions[0].choices)  # type: ignore[union-attr]
    for bullet in added_bullets(repo_root):
        named = set(re.findall(r"(?<!\.)\begresswall (\w+)", bullet))
        assert named <= defined, (bullet, named - defined)


# --- fix pass 7: the honest list of what none of this catches ----------------

#: The first clause of every gap CONTRIBUTING.md admits to, in order. The
#: section exists so a reader knows what the suite is *not* telling them, which
#: makes it exactly the kind of list that rots quietly: closing a gap and
#: leaving the line, or deleting a line without closing the gap, both read the
#: same on the page. Pinned, neither is silent.
UNCAUGHT = (
    "A new prose sentence anywhere on a page that carries no number, no number-word, no "
    "quotation, no flag and no listed superlative",
    'The body of a "What it does not do" bullet',
    'The CHANGELOG\'s "Changed" and "Fixed" bullets',
    'The comparison page\'s "What X does that egresswall does not" paragraphs',
    "The list of tools the README's comparison paragraph names is not tied to the sections on "
    "docs/comparison.md, so it can name a project the page does not cover.",
    'A count in a historical sentence ("six shapes crossed the boundary") names no live code '
    "expression",
    "The timing bounds are wall clock on whatever machine runs the suite.",
    "A rule the code has and no document mentions",
    "CONTRIBUTING.md itself is outside the number, word, quotation and flag checks; only this "
    "section is pinned.",
)


def test_contributing_lists_exactly_the_gaps_this_suite_still_has(repo_root: Path) -> None:
    """Add a gap, close one, or reword one, and this fails until the tuple moves."""
    text = (repo_root / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "## What the doc-truth suite does not catch" in text
    section = text.split("## What the doc-truth suite does not catch")[1].split("\n## ")[0]
    listed = [
        flatten(item) for item in re.findall(r"^- (.+?)(?=\n- |\n\n|\Z)", section, re.S | re.M)
    ]
    assert len(listed) == len(UNCAUGHT), listed
    for said, pinned in zip(listed, UNCAUGHT, strict=True):
        assert said.startswith(pinned), (said, pinned)


# --- fix pass 8: the mechanism sentences, pinned to the mechanism -------------
#
# A number on the page is pinned to the expression that decides it, and a
# capability bullet is pinned as text -- but a sentence naming *how* something
# works was checked by nothing. Three shipped and were false: name folding was
# "NFC then casefold" against a `_fold` that does NFKD and strips combining
# marks, the `forbidden_values` matcher was "a prefilter and a fixed-width
# lookup" against a `_value_matcher` that builds an Aho-Corasick automaton, and
# an unparseable embedded document "is screened as a string only" against a
# default that refuses it. Each mechanism is named in the code, and every
# document that describes it has to use the same name.

#: Mechanism -> (the word, the code object whose docstring is the source of
#: truth for it, the documents that must name it).
MECHANISMS: tuple[tuple[str, str, object, tuple[str, ...]], ...] = (
    ("name folding", "NFKD", None, ("README.md", "CHANGELOG.md")),
    ("the forbidden_values matcher", "Aho-Corasick", None, ("README.md", "CHANGELOG.md")),
    ("the embedded-document candidate test", "C, Z or M", None, ("README.md", "CHANGELOG.md")),
    # fix pass 9: the categories are not the whole strip set, and the property
    # that is the rest of it has to be named by the same name everywhere.
    (
        "the embedded-document strip set",
        "Default_Ignorable",
        None,
        ("README.md", "CHANGELOG.md"),
    ),
)


def mechanism_sources() -> dict[str, object]:
    from egresswall import _core

    return {
        "NFKD": _core._fold,
        "Aho-Corasick": _core._value_matcher,
        "C, Z or M": _core._document_candidate,
        "Default_Ignorable": _core._document_candidate,
    }


@pytest.mark.parametrize(("mechanism", "word", "_unused", "documents"), MECHANISMS)
def test_every_document_names_the_mechanism_the_code_names(
    mechanism: str, word: str, _unused: object, documents: tuple[str, ...], repo_root: Path
) -> None:
    """Rename the mechanism in the code without renaming it on the page, or the
    reverse, and this fails."""
    source = mechanism_sources()[word]
    doc = source.__doc__ or ""
    assert word in flatten(doc), (mechanism, source.__name__)
    for document in documents:
        text = flatten((repo_root / document).read_text(encoding="utf-8"))
        assert word in text, (mechanism, document)


def test_no_document_calls_the_folding_nfc() -> None:
    """The word that was wrong, and the behaviour that proves it was wrong."""
    import unicodedata

    from egresswall._core import normalize_key

    spelled = fullwidth("API_KEY")
    assert normalize_key(spelled) == "apikey"
    assert unicodedata.normalize("NFC", spelled).casefold() != "apikey"


@pytest.mark.parametrize("document", ["README.md", "CHANGELOG.md"])
def test_nfc_is_only_ever_named_beside_the_form_the_code_uses(
    document: str, repo_root: Path
) -> None:
    """ "NFC then casefold" is the sentence that shipped. A paragraph may say what
    NFC could not do; none may describe the folding as NFC."""
    text = (repo_root / document).read_text(encoding="utf-8")
    for quoted in re.finditer(r"(.?)NFC then casefold(.?)", text):
        assert quoted.group(1) == '"' and quoted.group(2) == '"', (
            f"{document} states the old sentence as its own rather than quoting it"
        )
    for paragraph in re.split(r"\n\s*\n|\n- ", text):
        if "NFC" in paragraph:
            assert "NFKD" in paragraph, (document, flatten(paragraph)[:200])


def test_the_matcher_the_documents_name_is_the_one_the_code_builds() -> None:
    """Aho-Corasick is a claim with a behaviour: a failure link finds the second
    entry inside a run that started as the first."""
    from egresswall._core import _forbidden_value, _value_matcher

    matcher = _value_matcher(frozenset({"abc", "bcd"}))
    assert matcher is not None
    _first, goto, fail, hit = matcher
    assert len(goto) == len(fail) == len(hit)
    assert any(link for link in fail), "an automaton with no failure links is a trie"
    assert _forbidden_value("abcd", frozenset({"abcd"[1:], "zzz"}))
    assert _forbidden_value("xxabcdxx", frozenset({"bcd"}))


def test_the_entry_bound_the_documents_state_is_the_one_the_suite_times(repo_root: Path) -> None:
    """The "10000 entries, the length of the string" claim, and the two timing
    shapes that are the whole of its evidence."""
    from test_detectors import SHAPES

    assert MAX_FORBIDDEN_VALUES == 10_000
    named = {shape.__name__ for shape in SHAPES}
    assert {"full_forbidden_value_list", "colliding_forbidden_value_list"} <= named
    source = (repo_root / "tests" / "test_detectors.py").read_text(encoding="utf-8")
    assert "assert elapsed < 1.0" in source


@pytest.mark.parametrize("document", ["README.md", "CHANGELOG.md"])
def test_the_embedded_document_default_on_the_page_is_the_shipped_default(
    document: str, repo_root: Path
) -> None:
    """Refuse-unparseable is the default, so every page has to name the code and
    the flag rather than the behaviour it replaced."""
    from egresswall import EMBEDDED_DOCUMENT_UNPARSEABLE, check

    assert Policy().refuse_unparseable_embedded is True
    assert [item.code for item in check({"t": "{{name}}"}, Policy())] == [
        EMBEDDED_DOCUMENT_UNPARSEABLE
    ]
    text = flatten((repo_root / document).read_text(encoding="utf-8"))
    assert EMBEDDED_DOCUMENT_UNPARSEABLE in text, document
    assert "refuse_unparseable_embedded" in text, document


#: A bullet in this file describing a mechanism a later bullet replaced. Each is
#: a sentence a reader meets in the present tense on the page PyPI links as
#: Changelog, so each has to say it was replaced.
SUPERSEDED = (
    "A denylist was precomputed once per policy into a prefilter and a fixed-width lookup",
    "was screened as a string only at this point",
)


@pytest.mark.parametrize("sentence", SUPERSEDED)
def test_a_superseded_mechanism_bullet_says_it_was_superseded(
    sentence: str, repo_root: Path
) -> None:
    """Delete the marker and the file describes two mechanisms as if both ship."""
    text = (repo_root / "CHANGELOG.md").read_text(encoding="utf-8")
    bullets = [flatten(bullet) for bullet in re.split(r"\n- ", text)]
    holding = [bullet for bullet in bullets if sentence in bullet]
    assert len(holding) == 1, sentence
    assert "supersede" in holding[0].lower(), holding[0]
