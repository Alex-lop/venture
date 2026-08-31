"""`agent_plan_lint.globs.full_match` must behave exactly like `PurePosixPath.full_match`.

`PurePosixPath.full_match` only exists on Python 3.13+, and this package supports
3.11+, so the matcher is our own on every version. CASES below was captured from
CPython 3.13.9 and is re-derived from the standard library whenever the suite runs
on 3.13 or newer -- so a divergence fails the build on the newest interpreter and
the frozen expectations keep 3.11 and 3.12 honest.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import PurePosixPath

import pytest

from agent_plan_lint.globs import MAX_PATH_SEGMENTS, full_match, matches_any

CASES = (
    ("app/a.py", "app/**", True),
    ("app", "app/**", False),
    ("app/nested/a.py", "app/**", True),
    ("app/nested/a.py", "app/*", False),
    ("app/a.py", "app/*", True),
    ("app/a.py", "*", False),
    ("a", "**", True),
    ("a/b/c", "**", True),
    ("a/b/c", "**/c", True),
    ("c", "**/c", True),
    ("a/b/c", "a/**/c", True),
    ("a/c", "a/**/c", True),
    ("a/b/x/c", "a/**/c", True),
    ("app/a.py", "**/*.py", True),
    ("a.py", "**/*.py", True),
    ("app/a.txt", "**/*.py", False),
    ("app/a.py", "*.py", False),
    ("a.py", "*.py", True),
    ("src/app/a.py", "app/**", False),
    ("tests/unit/test_x.py", "tests/**", True),
    ("app/.hidden.py", "app/*", True),
    (".hidden", "*", True),
    ("app/.git/config", "app/**", True),
    ("app/a.py", "app/[ab].py", True),
    ("app/c.py", "app/[ab].py", False),
    ("app/a.py", "app/[!a].py", False),
    ("app/b.py", "app/[!a].py", True),
    ("app/a-b.py", "app/[a-c]-b.py", True),
    ("app/d-b.py", "app/[a-c]-b.py", False),
    ("app/ab.py", "app/?b.py", True),
    ("app/b.py", "app/?b.py", False),
    ("app/sub/a.py", "app/?/a.py", False),
    ("app/s/a.py", "app/?/a.py", True),
    ("out/candidate.patch", "out/**", True),
    ("out", "out/**", False),
    ("app/secrets/key.txt", "app/secrets/**", True),
    ("app/secrets/key.txt", "app/**", True),
    ("a/b", "a/b", True),
    ("a/b", "a/b/c", False),
    ("a/b/c", "a/b", False),
    ("app/a.py", "**/**", True),
    ("a", "**/**", True),
    ("a/b", "**/*", True),
    ("app/a.py", "app/**/*.py", True),
    ("app/x/y/a.py", "app/**/*.py", True),
    ("a", "a/**/b", False),
    ("a/b", "a/**/b", True),
    ("a/x/b", "a/**/b", True),
)

# Every pattern component and path segment worth crossing with the others.
_COMPONENTS = ("a", "b", "*", "**", "?", "*.py", "[ab]", "[!a]", "a*", "x")
_SEGMENTS = ("a", "b", "x", "a.py", "b.py", "ab")


@pytest.mark.parametrize(("path", "pattern", "expected"), CASES)
def test_matches_the_captured_standard_library_behaviour(path: str, pattern: str, expected: bool) -> None:
    assert full_match(path, pattern) is expected


# Skipped on 3.11 and 3.12: these two are the only checks against an independent
# oracle, so a green run there has compared the matcher with the captured table
# only. See docs/porting-notes.md.
@pytest.mark.skipif(sys.version_info < (3, 13), reason="PurePosixPath.full_match needs 3.13")
@pytest.mark.parametrize(("path", "pattern", "expected"), CASES)
def test_captured_behaviour_still_matches_this_interpreter(path: str, pattern: str, expected: bool) -> None:
    assert PurePosixPath(path).full_match(pattern) is expected


@pytest.mark.skipif(sys.version_info < (3, 13), reason="PurePosixPath.full_match needs 3.13")
def test_exhaustive_agreement_with_the_standard_library() -> None:
    paths = ["/".join(segments) for length in (1, 2, 3) for segments in itertools.product(_SEGMENTS, repeat=length)]
    patterns = [
        "/".join(components) for length in (1, 2, 3) for components in itertools.product(_COMPONENTS, repeat=length)
    ]
    mismatches = [
        (path, pattern)
        for pattern in patterns
        for path in paths
        if full_match(path, pattern) != PurePosixPath(path).full_match(pattern)
    ]

    assert len(paths) * len(patterns) > 250_000
    assert mismatches == []


@pytest.mark.parametrize(
    ("path", "pattern"),
    (
        ("a/" * MAX_PATH_SEGMENTS + "f", "**"),
        ("f", "a/" * MAX_PATH_SEGMENTS + "f"),
    ),
)
def test_a_path_or_pattern_past_the_bound_is_refused_rather_than_matched(path: str, pattern: str) -> None:
    """`models.RepoPath` refuses these when a document loads; a direct caller gets this."""

    assert full_match("a/" * (MAX_PATH_SEGMENTS - 1) + "f", "**") is True
    with pytest.raises(ValueError, match=f"at most {MAX_PATH_SEGMENTS} segments"):
        full_match(path, pattern)


#: The two shapes where this matcher and `PurePosixPath.full_match` disagree.
#: `pathlib` normalises an empty pattern component away and this does not. The
#: module docstring, README.md and CHANGELOG.md all state the divergence, so it
#: is pinned here in both directions: a fix on either side has to move the prose.
DIVERGENCES = (("a/b", "**/"), ("aa/ab", "*//*a*"))


@pytest.mark.parametrize(("path", "pattern"), DIVERGENCES)
def test_an_empty_pattern_component_is_the_documented_divergence(path: str, pattern: str) -> None:
    assert full_match(path, pattern) is False


@pytest.mark.skipif(sys.version_info < (3, 13), reason="PurePosixPath.full_match needs 3.13")
@pytest.mark.parametrize(("path", "pattern"), DIVERGENCES)
def test_the_standard_library_answers_the_other_way_on_the_documented_divergence(path: str, pattern: str) -> None:
    assert PurePosixPath(path).full_match(pattern) is True


def test_no_document_can_carry_a_pattern_the_two_disagree_on() -> None:
    """Which is why documenting the divergence is enough: the validator cannot reach it."""

    from pydantic import TypeAdapter, ValidationError

    from agent_plan_lint.models import RepoPath

    adapter = TypeAdapter(RepoPath)
    for _, pattern in DIVERGENCES:
        with pytest.raises(ValidationError):
            adapter.validate_python(pattern)
    with pytest.raises(ValidationError):
        adapter.validate_python("/".join(["*"] * (MAX_PATH_SEGMENTS + 1)))


def test_matches_any_answers_what_the_patterns_answer_one_by_one() -> None:
    """The first-segment index is an optimisation; it may not change an answer."""

    patterns = ("app/**", "lib/*.py", "**/*.md", "*.py", "?/x", "[ab]/**")
    pool = (*_SEGMENTS, "app", "lib")
    paths = ["/".join(segments) for length in (1, 2, 3) for segments in itertools.product(pool, repeat=length)]
    disagreements = [
        path for path in paths if matches_any(path, patterns) != any(full_match(path, item) for item in patterns)
    ]

    assert len(paths) > 500
    assert any(matches_any(path, patterns) for path in paths)
    assert disagreements == []
