"""Path-glob matching with the semantics of `PurePosixPath.full_match`.

`PurePosixPath.full_match` landed in Python 3.13; this package supports 3.11+,
so the matcher is implemented here and used on every version, which keeps the
behaviour identical across interpreters instead of only on the newest one.

Semantics (matched against the whole path, anchored at both ends):

* `**` matches any run of path segments. As the last component of a pattern it
  must match at least one segment, which is what `a/**` not matching `a` means
  in the standard library.
* every other component matches exactly one segment, with `*`, `?` and `[seq]`
  handled by `fnmatch` -- a segment never contains `/`, so `fnmatch`'s
  separator-blind `*` cannot leak across segments here.

The equivalence holds for *canonical* patterns: no empty component (`**/`,
`*//*a*`), and at most `MAX_PATH_SEGMENTS` components. `pathlib` normalises an
empty component away and this matcher does not, so `full_match("a/b", "**/")`
is False here and True there; a pattern past the bound is a `ValueError` here
and a bool there. `models.RepoPath` refuses both spellings when a document
loads, so no document can reach either case; a direct caller of this module
gets the divergence documented above rather than a silent difference.

The match is a dynamic program over the segments carried in one integer, one
bit per offset into the path, so a component costs a few machine-word
operations rather than one `fnmatch` call per (component, segment) cell, and no
regular expression backtracks over a run of `**`.

Three bounds, each documented in `docs/schema.md`, are what keep the work of
matching a whole plan against a whole policy finite, and they are the reason
the caps are where they are rather than at whatever the byte cap allows:

* `MAX_PATH_SEGMENTS` -- how deep one path or pattern goes;
* `MAX_POLICY_WILDCARDS` -- how many *distinct* components a policy may use
  that are neither a literal name nor `*` nor `**`. Only those cost a scan of
  the path's segments; every other component is a dictionary lookup or a
  constant. Real policies use a handful (`*.py`, `test_*.py`); a document that
  uses thousands is what turns matching into a denial of service;
* `models.MAX_PLAN_PATHS` -- how many paths one plan may name at all.

`matches_any` is the entry point a policy is matched through, and it does the
per-path work once for the whole pattern list: the segment index, the mask of
each wildcard component, and an index of the patterns whose first component is
a literal, so a path is only tried against the patterns that could accept its
first segment.

`tests/test_globs.py` holds a table of cases captured from CPython 3.13 and
re-checks it against `PurePosixPath.full_match` whenever the tests run on 3.13.
`tests/test_performance.py` pins the work bound.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from fnmatch import translate
from functools import lru_cache

__all__ = ["MAX_PATH_SEGMENTS", "MAX_POLICY_WILDCARDS", "full_match", "matches_any", "wildcard_components"]

#: Most segments a path, or components a pattern, may have. A repository path
#: 15 directories deep is already pathological, and the bound is what makes the
#: cost of one match a bounded number of steps rather than one that grows with
#: the deepest path a document happens to name. `models.RepoPath` enforces it
#: when a document loads, so this module only has to defend a direct caller.
MAX_PATH_SEGMENTS = 16

#: Most *distinct* wildcard components one policy may spend across its read
#: globs, write globs and exclusions. A wildcard component is the only kind
#: whose mask costs a scan of the path, so this is the bound that keeps a
#: policy from making every (path, pattern) pair pay for one.
MAX_POLICY_WILDCARDS = 32

_WILDCARD = "*?["

# What a component costs to turn into a mask, decided once per pattern.
_ANY_RUN = 0  # `**`
_ANY_SEGMENT = 1  # `*`
_LITERAL = 2  # a name: one dictionary lookup
_PATTERN = 3  # anything else: one scan of the path's distinct segments

#: How many wildcard masks one path keeps before the cache for it is dropped.
#: A single policy cannot exceed `MAX_POLICY_WILDCARDS`; the slack is for a
#: long-lived process that validates against several policies in turn.
_MASKS_PER_PATH = 4 * MAX_POLICY_WILDCARDS


@lru_cache(maxsize=4096)
def _components(pattern: str) -> tuple[str, ...]:
    """Pattern components with runs of `**` collapsed -- `**/**` matches what `**` does."""

    parts = pattern.split("/")
    return tuple(part for index, part in enumerate(parts) if part != "**" or index == 0 or parts[index - 1] != "**")


def _kind(component: str) -> int:
    if component == "**":
        return _ANY_RUN
    if component == "*":
        return _ANY_SEGMENT
    return _PATTERN if any(character in component for character in _WILDCARD) else _LITERAL


def wildcard_components(patterns: Iterable[str]) -> set[str]:
    """The components of `patterns` whose mask costs a scan of the path.

    `MAX_POLICY_WILDCARDS` is counted over this set, so `**`, `*` and literal
    directory names are free: a policy may use as many of them as it likes.
    """

    return {component for pattern in patterns for component in _components(pattern) if _kind(component) == _PATTERN}


@lru_cache(maxsize=8192)
def _index(path: str) -> tuple[int, dict[str, int], str, str]:
    """Segment count, the offsets each distinct segment sits at, and the two ends.

    The ends are carried here so the alignment checks in `_match` can ask about
    one segment instead of building the whole mask of a component that is about
    to be rejected.
    """

    segments = path.split("/")
    positions: dict[str, int] = {}
    for offset, segment in enumerate(segments):
        positions[segment] = positions.get(segment, 0) | (1 << offset)
    return len(segments), positions, segments[0], segments[-1]


@lru_cache(maxsize=8192)
def _matcher(component: str):
    """`component` compiled once, so a mask is a C-level match per segment."""

    return re.compile(translate(component)).match


@lru_cache(maxsize=2048)
def _masks(path: str) -> dict[str, int]:
    """The wildcard masks computed for one path, shared by every pattern list it meets."""

    return {}


@lru_cache(maxsize=4096)
def _shape(pattern: str) -> tuple[tuple[tuple[int, str], ...], int, int]:
    """The pattern's components with their kinds, its fewest segments, and its exact length.

    The exact length is `-1` unless the pattern has no `**`, in which case a
    path of any other length is rejected before the dynamic program runs.
    """

    components = _components(pattern)
    star_star = "**" in components
    required = sum(1 for component in components if component != "**") + (1 if components[-1] == "**" else 0)
    steps = tuple((_kind(component), component) for component in components)
    return steps, required, -1 if star_star else len(components)


def _segment_match(kind: int, component: str, segment: str) -> bool:
    """Does one component match one segment? The cheap question a mask answers 32 times."""

    if kind == _ANY_SEGMENT:
        return True
    if kind == _LITERAL:
        return component == segment
    return _matcher(component)(segment) is not None


def _match(path: str, pattern: str, index: tuple[int, dict[str, int], str, str], masks: dict[str, int]) -> bool:
    """`full_match`, with the per-path work already done by the caller."""

    count, positions, first, last = index
    steps, required, exact = _shape(pattern)
    if count > MAX_PATH_SEGMENTS or len(steps) > MAX_PATH_SEGMENTS:
        raise ValueError(f"a path and a pattern may have at most {MAX_PATH_SEGMENTS} segments")
    if count < required or (exact >= 0 and count != exact):
        return False
    # Two cheap necessary conditions before the loop: the ends have to line up.
    # They reject the common miss with one segment comparison rather than a
    # sweep of every component, which is what keeps a policy full of globs that
    # nearly match off the hot path.
    if steps[0][0] != _ANY_RUN and not _segment_match(*steps[0], first):
        return False
    if steps[-1][0] != _ANY_RUN and not _segment_match(*steps[-1], last):
        return False

    # Bit `offset` of `reachable` is set when the components consumed so far
    # can end at that offset into the path. `**` sets every bit from the
    # earliest reachable offset up, which is a negative int in Python -- an
    # infinite run of ones -- and that is exactly the value wanted here.
    final = len(steps) - 1
    reachable = 1
    previous = mask = None
    for position, (kind, component) in enumerate(steps):
        if kind == _ANY_RUN:
            lowest = (reachable & -reachable).bit_length() - 1
            # A trailing `**` translates to `.*` after a separator, so it needs
            # at least one segment: `a/**` does not match `a`.
            reachable = -1 << (lowest + (1 if position == final else 0))
            continue
        # A pattern repeats a component far more often than not (`*/*/*/...`),
        # and a component's mask does not depend on where it sits, so the
        # lookup is skipped when it would repeat.
        if component != previous:
            previous = component
            if kind == _ANY_SEGMENT:
                mask = (1 << count) - 1
            elif kind == _LITERAL:
                mask = positions.get(component, 0)
            else:
                mask = masks.get(component, -1)
                if mask < 0:
                    if len(masks) >= _MASKS_PER_PATH:
                        masks.clear()
                    matcher = _matcher(component)
                    mask = 0
                    for segment, offsets in positions.items():
                        if matcher(segment):
                            mask |= offsets
                    masks[component] = mask
        reachable = (reachable & mask) << 1
        if not reachable:
            return False
    return bool(reachable >> count & 1)


def full_match(path: str, pattern: str) -> bool:
    """Return True when `path` matches the glob `pattern` in full.

    `PurePosixPath.full_match` semantics for canonical patterns: no empty
    component and at most `MAX_PATH_SEGMENTS` of them. An empty component, which
    `pathlib` normalises away and this does not, is the one shape where the two
    disagree; a path or pattern past the bound raises `ValueError` where the
    standard library returns a bool. See the module docstring.
    """

    return _match(path, pattern, _index(path), _masks(path))


@lru_cache(maxsize=4096)
def _by_first_segment(patterns: tuple[str, ...]) -> tuple[dict[str, tuple[str, ...]], tuple[str, ...]]:
    """Patterns grouped by the literal first component they require, plus the rest.

    A policy's globs are matched against every path in a plan. Most of them open
    with a literal directory, so a path only has to be tried against the globs
    that could accept its first segment; the ones opening with `**` or a
    wildcard have to be tried against everything.
    """

    literal: dict[str, list[str]] = {}
    wildcard: list[str] = []
    for pattern in patterns:
        head = _components(pattern)[0]
        if _kind(head) in (_ANY_RUN, _ANY_SEGMENT, _PATTERN):
            wildcard.append(pattern)
        else:
            literal.setdefault(head, []).append(pattern)
    return {head: tuple(group) for head, group in literal.items()}, tuple(wildcard)


def matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    """True when `path` fully matches at least one of `patterns`."""

    literal, wildcard = _by_first_segment(patterns)
    candidates = literal.get(path.partition("/")[0], ()) + wildcard
    if not candidates:
        return False
    index, masks = _index(path), _masks(path)
    return any(_match(path, pattern, index, masks) for pattern in candidates)
