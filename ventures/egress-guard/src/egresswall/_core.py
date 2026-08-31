"""Value-level egress screening: block, never redact.

A redacted payload hides the fact that an unauthorized value was assembled in
the first place, so every rule here fails closed by raising or reporting a
violation that names the reason and the path but never the value.
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import deque
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, fields, replace
from functools import lru_cache
from pathlib import Path
from typing import Any

# --- reason codes -----------------------------------------------------------

RAW_IDENTIFIER = "RAW_IDENTIFIER"
JOIN_TOKEN = "JOIN_TOKEN"
SECRET_MATERIAL = "SECRET_MATERIAL"
FORBIDDEN_KEY = "FORBIDDEN_KEY"
DENIED_FIELD_PATH = "DENIED_FIELD_PATH"
FORBIDDEN_VALUE = "FORBIDDEN_VALUE"
PAYLOAD_TOO_DEEP = "PAYLOAD_TOO_DEEP"
PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
EMBEDDED_DOCUMENT_UNPARSEABLE = "EMBEDDED_DOCUMENT_UNPARSEABLE"

VIOLATION_CODES: dict[str, str] = {
    RAW_IDENTIFIER: "a direct identifier (email, US SSN, US phone number) was assembled",
    JOIN_TOKEN: "a pseudonymous join key that can re-link records was assembled",
    SECRET_MATERIAL: "credential material (API key, token, private key) was assembled",
    FORBIDDEN_KEY: "a field name the policy forbids appeared in the payload",
    DENIED_FIELD_PATH: "a field the policy denies carried a value",
    FORBIDDEN_VALUE: "a literal value the policy forbids appeared in the payload",
    PAYLOAD_TOO_DEEP: "the payload nests deeper than max_depth and was not fully screened",
    PAYLOAD_TOO_LARGE: "the payload exceeds max_nodes or max_string_length and was not screened",
    EMBEDDED_DOCUMENT_UNPARSEABLE: (
        "a string that opens like a serialized document was not screened as one"
    ),
}

# --- detectors --------------------------------------------------------------
#
# Every pattern below is anchored on a literal or a fixed-width run and has no
# nested or ambiguous quantifier, so matching is linear in the input length.
# Strings longer than Policy.max_string_length are blocked rather than scanned,
# which is what bounds the work a hostile payload can cause.

_EMAIL = re.compile(
    r"(?<![A-Za-z0-9_.+%-])[A-Za-z0-9_.+%-]+"
    r"@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)(?![A-Za-z0-9-])"
)
_SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
_PHONE = re.compile(
    r"(?<!\w)(?:\+?1[ .-]?)?(?:\([2-9]\d{2}\)|[2-9]\d{2})[ .-]\d{3}[ .-]\d{4}(?!\w)"
)
_JOIN_TOKEN = re.compile(r"(?<![0-9a-z])hmac-sha(?:256|512):[0-9a-f]{64,128}(?![0-9a-f])")
_AWS_ACCESS_KEY = re.compile(r"(?<![A-Z0-9])(?:AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16}(?![A-Z0-9])")
_GITHUB_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9]{36,251}|github_pat_[A-Za-z0-9_]{62,255})"
    r"(?![A-Za-z0-9])"
)
_PRIVATE_KEY = re.compile(r"-----BEGIN (?:[A-Z][A-Z0-9]* )*PRIVATE KEY-----")
_BEARER_TOKEN = re.compile(r"(?<![A-Za-z])[Bb]earer +[A-Za-z0-9._~+/-]{20,}={0,2}(?![A-Za-z0-9])")
_ANTHROPIC_KEY = re.compile(r"(?<![A-Za-z0-9-])sk-ant-[A-Za-z0-9_-]{24,}(?![A-Za-z0-9_-])")
_OPENAI_KEY = re.compile(
    r"(?<![A-Za-z0-9-])sk-(?!ant-)(?:proj-|svcacct-|admin-)?([A-Za-z0-9_-]{40,})(?![A-Za-z0-9_-])"
)


def _find_email(text: str, policy: Policy) -> bool:
    allowed = _folded(policy.allow_domains)
    for match in _EMAIL.finditer(text):
        domain = _fold(match.group(1))
        tld = domain.rpartition(".")[2]
        if len(tld) >= 2 and tld.isalpha() and domain not in allowed:
            return True
    return False


def _find_openai_key(text: str, policy: Policy) -> bool:
    """A real key is 40+ high-entropy characters; `sk-widget-blue-large` is a slug."""
    return any(
        any(c.isdigit() for c in body) and any(c.isupper() for c in body)
        for body in (match.group(1) for match in _OPENAI_KEY.finditer(text))
    )


def _regex_detector(pattern: re.Pattern[str]) -> Callable[[str, Policy], bool]:
    def detect(text: str, policy: Policy) -> bool:
        return pattern.search(text) is not None

    return detect


#: Detector name -> (matcher, reason code). The order is the reporting order.
DETECTORS: dict[str, tuple[Callable[[str, Policy], bool], str]] = {
    "email": (_find_email, RAW_IDENTIFIER),
    "ssn": (_regex_detector(_SSN), RAW_IDENTIFIER),
    "phone": (_regex_detector(_PHONE), RAW_IDENTIFIER),
    "join_token": (_regex_detector(_JOIN_TOKEN), JOIN_TOKEN),
    "private_key": (_regex_detector(_PRIVATE_KEY), SECRET_MATERIAL),
    "aws_access_key": (_regex_detector(_AWS_ACCESS_KEY), SECRET_MATERIAL),
    "github_token": (_regex_detector(_GITHUB_TOKEN), SECRET_MATERIAL),
    "anthropic_key": (_regex_detector(_ANTHROPIC_KEY), SECRET_MATERIAL),
    "openai_key": (_find_openai_key, SECRET_MATERIAL),
    "bearer_token": (_regex_detector(_BEARER_TOKEN), SECRET_MATERIAL),
}

DEFAULT_DETECTORS: frozenset[str] = frozenset(DETECTORS)

#: Field names that name a shape no tool response should carry outward.
DEFAULT_FORBIDDEN_KEYS: frozenset[str] = frozenset(
    {
        "access_key",
        "api_key",
        "arbitrary_sql",
        "auth",
        "authorization",
        "credentials",
        "customer_id",
        "database_credentials",
        "direct_identifier",
        "direct_identifiers",
        "password",
        "phone",
        "private_key",
        "query_text",
        "raw_rows",
        "reviewer_override",
        "reviewer_overrides",
        "rows",
        "secret",
        "secrets",
        "session_id",
        "sql",
        "ssn",
        "suppressed_value",
        "suppressed_values",
        "token",
        "user_id",
        "x_api_key",
    }
)
DEFAULT_FORBIDDEN_KEY_SUBSTRINGS: frozenset[str] = frozenset(
    {"credential", "password", "reviewer_override", "secret"}
)
#: Matched after normalize_key, so this is "ends in token once case and
#: separators are removed" -- nextToken and pageToken are refused too.
DEFAULT_FORBIDDEN_KEY_SUFFIXES: frozenset[str] = frozenset({"token"})

#: Below a field with one of these names an MCP message declares what a tool
#: takes and returns, or what an elicitation is asking the user for. The names
#: under them are a schema the server is publishing, not data it is answering
#: with, so the field-name rules do not run there -- a tool that declares a
#: parameter called `phone` must not make `tools/list` fail, because a client
#: that cannot list tools cannot use the server at all, and an
#: `elicitation/create` asking for a `phone` must not be dropped, because it
#: carries an id and the server would wait forever for the answer. Every value
#: inside the schema is screened exactly as usual.
SCHEMA_KEYS: frozenset[str] = frozenset({"inputSchema", "outputSchema", "requestedSchema"})

_INT_FIELDS = frozenset({"max_depth", "max_nodes", "max_string_length", "max_total_length"})
_BOOL_FIELDS = frozenset({"refuse_unparseable_embedded"})

#: The walk is recursive, so max_depth is capped well below CPython's recursion
#: limit: a policy that would crash the walk is refused when it is built.
MAX_ALLOWED_DEPTH = 500

#: A denylist is compiled once per policy into the automaton below, which reads
#: each character of a screened string a bounded number of times whatever the
#: list holds. The bound here is therefore on the memory a policy may pin in
#: that automaton, not on screening time: a policy over it is refused when it is
#: built.
MAX_FORBIDDEN_VALUES = 10_000

#: A denied path is matched against the whole path from the root, so the walk
#: carries the accumulated path only while it is no shorter than the longest
#: entry: one long entry buys back the per-node path cost `_PATH_TOO_LONG`
#: exists to bound. A dotted path longer than this is a typo, not a policy, so
#: a policy holding one is refused when it is built.
MAX_DENIED_PATH_CHARS = 512

_SEPARATORS = re.compile(r"[^a-z0-9]")

#: A field name is echoed back in a path or a message only when it is short,
#: plain ASCII and carries nothing a detector recognises. Everything else is
#: reported as <key#n>: a key can be the value (a table keyed by email address),
#: and the report, the log and the JSON-RPC error all leave the boundary.
_SAFE_NAME = re.compile(r"[A-Za-z0-9_-]{1,64}")

#: A label the other side of the boundary chose -- a JSON-RPC method, an MCP
#: tool name -- reaches a log line the same way a field name does, and is
#: bounded the same way. Labels carry "/" and "." that a field name may not.
_SAFE_LABEL = re.compile(r"[A-Za-z0-9_/.-]{1,64}")


def _fold(text: str) -> str:
    """The one case/Unicode normalisation every name comparison goes through.

    ASCII is lowercased directly -- for ASCII that is exactly what casefold
    does, and it is the common case. Anything else is decomposed (NFKD),
    stripped of combining marks and casefolded, so U+1E9E folds to "ss",
    U+212A to "k", "s" with an acute accent to "s", and fullwidth "API" to
    "api". A homoglyph from another script is **not** folded: Cyrillic "a"
    (U+0430) is not Latin "a" here, and a field name spelled with one is not
    the listed name. The README says so under "What it does not do"; this is
    an obfuscation limit, not a spelling limit.
    """
    if text.isascii():
        return text.lower()
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).casefold()


#: Only names this short are cached. A field name is chosen by whatever is on
#: the other side of the boundary, so an unbounded one must not be able to pin
#: megabytes in a cache, one key at a time.
_MAX_CACHED_NAME = 128


def _normalize(key: str) -> str:
    return _SEPARATORS.sub("", _fold(key))


_normalize_cached = lru_cache(maxsize=8192)(_normalize)


def normalize_key(key: str) -> str:
    """Fold a field name and drop separators, so apiKey == api-key == api_key."""
    return _normalize_cached(key) if len(key) <= _MAX_CACHED_NAME else _normalize(key)


@lru_cache(maxsize=64)
def _normalized(names: frozenset[str]) -> frozenset[str]:
    return frozenset(normalize_key(name) for name in names)


@lru_cache(maxsize=64)
def _folded(names: frozenset[str]) -> frozenset[str]:
    return frozenset(_fold(name) for name in names)


def _normalize_path(dotted: str) -> str:
    """Normalize a dotted path segment by segment, so patient.MRN == patient.mrn."""
    if len(dotted) > _MAX_CACHED_NAME:
        return ".".join(normalize_key(part) for part in dotted.split("."))
    return _normalize_path_cached(dotted)


@lru_cache(maxsize=8192)
def _normalize_path_cached(dotted: str) -> str:
    return ".".join(normalize_key(part) for part in dotted.split("."))


@lru_cache(maxsize=64)
def _normalized_paths(paths: frozenset[str]) -> frozenset[str]:
    return frozenset(_normalize_path(path) for path in paths)


@lru_cache(maxsize=64)
def _longest_denied_path(paths: frozenset[str]) -> int:
    """The longest normalized entry, or -1 when there are none to match."""
    return max((len(path) for path in _normalized_paths(paths)), default=-1)


#: A denied field path is matched against the whole path from the root, so a
#: path longer than the longest denied entry can never equal one -- and a path
#: only grows. Past that length the walk stops building the string and carries
#: this marker instead, which is what keeps the walk linear in the payload
#: rather than quadratic in its depth.
_PATH_TOO_LONG = "\x00"


def _extend_path(dotted: str, name: str, limit: int) -> str:
    """The parent's normalized path plus one field name, normalized once.

    The bound is checked on the *normalized* child, never on the raw name. It
    used to short-circuit on `len(name) > limit`, which measures a name before
    its separators are removed against a limit measured after: a parent field
    spelled `____patient____` was dropped as too long while `patient.mrn` still
    matched what it carried, so a denied path failed open on a name a server
    chose. `_normalize_path` costs the name's length, which `_walk` has already
    charged to `budget.text` before calling this.
    """
    if limit < 0 or dotted == _PATH_TOO_LONG:
        return _PATH_TOO_LONG
    # A field name is normalized the way a policy entry is: separators removed
    # inside a segment, "." kept as the boundary between segments, so a server
    # that flattens `{"patient.mrn": ...}` matches the entry the nested
    # spelling matches. A segment that is nothing but separators is no segment,
    # so `patient.` and `patient` build the same path rather than two.
    segments = (part for part in _normalize_path(name).split(".") if part)
    child = ".".join(filter(None, (dotted, *segments)))
    return child if len(child) <= limit else _PATH_TOO_LONG


@lru_cache(maxsize=16)
def _value_matcher(
    values: frozenset[str],
) -> tuple[re.Pattern[str], list[dict[str, int]], list[int], list[bool]] | None:
    """Precompute a denylist once per policy, so a scan costs the text not the list.

    Testing ``value in text`` once per entry made screening O(entries x bytes),
    which is seconds per message for a denylist of internal case ids. An index
    on the entries' heads is not enough either: the text is chosen by whatever
    is on the other side of the boundary, so it can make every offset a
    candidate and every candidate walk a whole bucket, which cost seconds per
    message for a denylist an operator would plausibly write.

    This is Aho-Corasick: a trie of the entries plus the failure links that say
    where to resume when a character does not continue the current one, so each
    character of the text is read a bounded number of times whatever the
    denylist holds and however it is shaped. The character class in front of it
    is the fast path: text that cannot start an entry anywhere is refused by the
    regex engine at C speed, without the automaton running at all.
    """
    real = sorted(value for value in values if value)
    if not real:
        return None
    goto: list[dict[str, int]] = [{}]
    hit: list[bool] = [False]
    for value in real:
        state = 0
        for char in value:
            nxt = goto[state].get(char)
            if nxt is None:
                nxt = len(goto)
                goto[state][char] = nxt
                goto.append({})
                hit.append(False)
            state = nxt
        hit[state] = True
    fail = [0] * len(goto)
    queue = deque(goto[0].values())
    while queue:
        state = queue.popleft()
        for char, nxt in goto[state].items():
            queue.append(nxt)
            back = fail[state]
            while back and char not in goto[back]:
                back = fail[back]
            candidate = goto[back].get(char, 0)
            fail[nxt] = candidate if candidate != nxt else 0
            hit[nxt] = hit[nxt] or hit[fail[nxt]]
    firsts = "".join(re.escape(char) for char in sorted(goto[0]))
    return re.compile(f"[{firsts}]"), goto, fail, hit


def _forbidden_value(text: str, values: frozenset[str]) -> bool:
    """True when any of ``values`` appears in ``text``, in one pass over ``text``."""
    matcher = _value_matcher(values)
    if matcher is None:
        return False
    first, goto, fail, hit = matcher
    start = first.search(text)
    if start is None:
        return False
    state = 0
    # No entry can begin before the first character that begins one, so the run
    # up to there is skipped whole rather than fed through the automaton.
    for char in text[start.start() :]:
        while state and char not in goto[state]:
            state = fail[state]
        state = goto[state].get(char, 0)
        if hit[state]:
            return True
    return False


@lru_cache(maxsize=64)
def _suffix_trie(suffixes: frozenset[str]) -> dict[str, Any] | None:
    """The normalized suffixes as a tree read backwards, once per policy.

    ``any(name.endswith(part) for part in suffixes)`` re-scanned the whole list
    for every field name in every payload, so a large suffix list cost as much
    per message as the payload did. Walking a name backwards through this costs
    the name, whatever the list holds.
    """
    root: dict[str, Any] = {}
    for suffix in _normalized(suffixes):
        if not suffix:
            continue
        node = root
        for char in reversed(suffix):
            node = node.setdefault(char, {})
        node[""] = True
    return root or None


def _ends_with(norm: str, suffixes: frozenset[str]) -> bool:
    """True when the normalized name ``norm`` ends in one of ``suffixes``."""
    node = _suffix_trie(suffixes)
    if node is None:
        return False
    for char in reversed(norm):
        node = node.get(char)
        if node is None:
            return False
        if "" in node:
            return True
    return False


#: The words a denied field may carry instead of a value: saying a field was
#: withheld is not leaking it. This used to be the regex `[A-Z][A-Z_]*`, which
#: made *any* all-caps word vocabulary -- an upper-cased surname under a denied
#: path produced no violation at all. It is a closed list now, widened by
#: `allow_tokens` and by nothing else.
DEFAULT_GOVERNANCE_TOKENS: frozenset[str] = frozenset(
    {
        "DENIED",
        "DENY",
        "MODEL_CONTEXT_DENIED",
        "NOT_AUTHORIZED",
        "REDACTED",
        "SUPPRESSED",
        "WITHHELD",
    }
)


# --- policy -----------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Policy:
    """What one boundary is allowed to let out. All rules fail closed."""

    denied_field_paths: frozenset[str] = frozenset()
    forbidden_keys: frozenset[str] = DEFAULT_FORBIDDEN_KEYS
    forbidden_key_substrings: frozenset[str] = DEFAULT_FORBIDDEN_KEY_SUBSTRINGS
    forbidden_key_suffixes: frozenset[str] = DEFAULT_FORBIDDEN_KEY_SUFFIXES
    forbidden_values: frozenset[str] = frozenset()
    exempt_keys: frozenset[str] = frozenset()
    detectors: frozenset[str] = DEFAULT_DETECTORS
    allow_domains: frozenset[str] = frozenset()
    allow_tokens: frozenset[str] = frozenset()
    max_depth: int = 32
    max_nodes: int = 100_000
    max_string_length: int = 1_048_576
    #: Every string and every field name costs its own length to screen, and
    #: `max_nodes` x `max_string_length` is not a bound anyone can wait for. This
    #: is the one that is measured: the walk stops and refuses the payload once
    #: it has screened this much text. Raising it raises screening time with it.
    max_total_length: int = 2_097_152
    #: A string whose first visible character is `{` or `[` is a candidate
    #: document -- see `_document_candidate`, which strips the code points in
    #: Unicode category C, Z or M from both ends before deciding. When it does
    #: not parse, or is too long to be parsed at all, the
    #: field-name and field-path rules could not run over it -- so it is refused
    #: as EMBEDDED_DOCUMENT_UNPARSEABLE rather than screened as a string and
    #: forwarded. Set this false and such a string is screened as a string only,
    #: which is the fail-open behaviour and is the operator's to choose.
    refuse_unparseable_embedded: bool = True

    def __post_init__(self) -> None:
        unknown = sorted(self.detectors - DEFAULT_DETECTORS)
        if unknown:
            raise ValueError(f"unknown detectors: {', '.join(unknown)}")
        for name in sorted(_INT_FIELDS):
            if getattr(self, name) < 1:
                raise ValueError(f"{name} must be >= 1")
        if self.max_depth > MAX_ALLOWED_DEPTH:
            raise ValueError(f"max_depth must be <= {MAX_ALLOWED_DEPTH} (the walk is recursive)")
        for name in ("forbidden_values", "forbidden_key_substrings", "forbidden_key_suffixes"):
            # An empty entry matches every string and every field name, so a
            # trailing comma in a policy file would refuse the whole payload.
            # The matchers below skip it; refusing it here says so out loud,
            # like the unknown-key error, rather than letting a typo decide.
            if "" in getattr(self, name):
                raise ValueError(f"{name} may not hold an empty string: it matches everything")
        if len(self.forbidden_values) > MAX_FORBIDDEN_VALUES:
            raise ValueError(
                f"forbidden_values holds at most {MAX_FORBIDDEN_VALUES} entries, "
                f"not {len(self.forbidden_values)}: the matcher for it is held in memory"
            )
        if any(len(path) > MAX_DENIED_PATH_CHARS for path in self.denied_field_paths):
            raise ValueError(
                f"a denied_field_paths entry holds at most {MAX_DENIED_PATH_CHARS} characters: "
                "the walk carries a path that long at every node"
            )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Policy:
        """Build a policy from parsed JSON. Unknown keys are an error."""
        if not isinstance(data, Mapping):
            raise ValueError("policy must be a JSON object")
        known = {item.name for item in fields(cls)}
        unknown = sorted(set(data) - known)
        if unknown:
            raise ValueError(f"unknown policy keys: {', '.join(unknown)}")
        kwargs: dict[str, Any] = {}
        for item in fields(cls):
            if item.name not in data:
                continue
            value = data[item.name]
            if item.name in _BOOL_FIELDS:
                if not isinstance(value, bool):
                    raise ValueError(f"{item.name} must be true or false")
                kwargs[item.name] = value
            elif item.name in _INT_FIELDS:
                if not isinstance(value, int) or isinstance(value, bool):
                    raise ValueError(f"{item.name} must be an integer")
                kwargs[item.name] = value
            else:
                if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
                    raise ValueError(f"{item.name} must be a list of strings")
                kwargs[item.name] = frozenset(value)
        return cls(**kwargs)

    @classmethod
    def from_file(cls, path: str | Path) -> Policy:
        return cls.from_dict(loads(Path(path).read_text(encoding="utf-8")))

    def to_dict(self) -> dict[str, Any]:
        return {
            item.name: (
                getattr(self, item.name)
                if item.name in _INT_FIELDS or item.name in _BOOL_FIELDS
                else sorted(getattr(self, item.name))
            )
            for item in fields(self)
        }

    def forbids_key(self, key: str) -> bool:
        """Match on the normalized name, so apiKey, api-key and API_KEY all match.

        A name in ``exempt_keys`` is never matched by these rules. That is how
        the proxy keeps the protocol's own field names -- ``progressToken`` ends
        in the default forbidden suffix ``token`` -- from making a spec-
        compliant server unusable. It exempts the name, never the value under
        it: everything below an exempt name is screened like anything else.
        """
        norm = normalize_key(key)
        if norm in _normalized(self.exempt_keys):
            return False
        return (
            norm in _normalized(self.forbidden_keys)
            or _forbidden_value(norm, _normalized(self.forbidden_key_substrings))
            or _ends_with(norm, self.forbidden_key_suffixes)
        )

    def denies_path(self, key: str, dotted: str) -> bool:
        """Match like forbids_key: case and separators are removed on both sides.

        ``dotted`` arrives already normalized, one field name at a time, from
        the walk: re-normalizing the whole accumulated path at every node made
        screening quadratic in the depth rather than linear in the payload.
        """
        if not self.denied_field_paths:
            return False
        paths = _normalized_paths(self.denied_field_paths)
        return dotted in paths or normalize_key(key) in paths

    def active_detectors(self) -> tuple[tuple[str, Callable[[str, Policy], bool], str], ...]:
        return tuple((name, *DETECTORS[name]) for name in DETECTORS if name in self.detectors)


# --- violations -------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Violation:
    """One reason a payload may not cross the boundary. Never carries the value."""

    code: str
    path: str
    detail: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.detail}"

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "detail": self.detail}


#: How many violations one report may name, and how many characters of them.
#: Every violation carries a path, a path is as long as the payload is deep,
#: and every segment in it is a field name the server chose -- so an unbounded
#: report is an unbounded server-controlled write into the operator's log and,
#: through the hook's stderr, into the model's context. The number of
#: violations is always reported in full; only the listing is bounded.
MAX_REPORTED = 20
MAX_REPORT_CHARS = 4000
#: Each violation's equal share of that, so one deep path cannot spend the whole
#: listing: past it the path is truncated, and the report stays under
#: MAX_REPORT_CHARS whatever the payload was shaped like. It is also the bound
#: on a violation reported one at a time -- the proxy's JSON-RPC error and its
#: drop log -- where there is no listing but the path is chosen the same way.
MAX_VIOLATION_CHARS = MAX_REPORT_CHARS // MAX_REPORTED


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: max(limit - 3, 0)] + "..."


def _trimmed(item: Violation) -> Violation:
    """A violation as a report, a log line or a JSON-RPC error may carry it.

    Both the path and the detail are built from names the other side chose, and
    both grow with the depth of the payload, so both get half of what one line
    may spend. The reason code is never trimmed: it is the part alerting reads.
    """
    room = max(MAX_VIOLATION_CHARS - (len(str(item)) - len(item.path) - len(item.detail)), 0)
    return replace(
        item, path=_clip(item.path, room // 2), detail=_clip(item.detail, room - room // 2)
    )


class EgressViolation(RuntimeError):
    """A payload would carry a value the policy does not release."""

    def __init__(self, reason: str, path: str, detail: str) -> None:
        super().__init__(f"{reason} at {path}: {detail}")
        self.reason = reason
        self.path = path
        self.detail = detail

    @property
    def violation(self) -> Violation:
        return Violation(self.reason, self.path, self.detail)


# --- the walk ---------------------------------------------------------------


class _Budget:
    __slots__ = ("nodes", "stopped", "text")

    def __init__(self) -> None:
        self.nodes = 0
        self.text = 0
        self.stopped = False


def _carries_data(value: Any, policy: Policy) -> bool:
    """True when a value looks like data rather than governance vocabulary.

    Explaining a denial ({"ssn": "DENY"}) is not the same as leaking a value.
    Shape detectors still run over such strings; only the field-path rule
    makes this exception. Everything else that is present counts, including 0,
    false and an empty list: a denied field that exists at all is a violation.
    """
    if isinstance(value, (bool, int, float)):
        return True
    if isinstance(value, str):
        stripped = value.strip()
        return stripped not in DEFAULT_GOVERNANCE_TOKENS and stripped not in policy.allow_tokens
    return value is not None


def _screen_key(name: str, policy: Policy) -> tuple[tuple[str, str], ...]:
    return tuple(
        (item.code, f"{item.detail} (field name)") for item in _screen_scalar(name, policy, "")
    )


_screen_key_cached = lru_cache(maxsize=8192)(_screen_key)


def _key_findings(name: str, policy: Policy) -> tuple[tuple[str, str], ...]:
    """What a field *name* carries, screened like any other string.

    A tool that returns a table keyed by email address or SSN puts the value in
    the key, so every detector runs over field names too. Short names are cached
    because a payload of records repeats them on every row; long ones are
    screened without being retained.
    """
    if len(name) > _MAX_CACHED_NAME:
        return _screen_key(name, policy)
    return _screen_key_cached(name, policy)


def _safe_label(name: str, policy: Policy, placeholder: str = "<name>") -> str:
    """A method or tool name as it may be logged, or a placeholder for it."""
    return name if _SAFE_LABEL.fullmatch(name) and not _key_findings(name, policy) else placeholder


def _walk(
    value: Any,
    policy: Policy,
    path: str,
    dotted: str,
    shown: str,
    depth: int,
    budget: _Budget,
    schema_keys: frozenset[str] = frozenset(),
    in_schema: bool = False,
) -> Iterator[Violation]:
    if budget.stopped:
        return
    budget.nodes += 1
    if budget.nodes > policy.max_nodes:
        budget.stopped = True
        yield Violation(
            PAYLOAD_TOO_LARGE, path, f"payload has more than max_nodes={policy.max_nodes} nodes"
        )
        return
    if budget.text > policy.max_total_length:
        # Charged as each string and field name is reached and checked here, so
        # a payload overruns the budget by at most one node's worth of text.
        budget.stopped = True
        yield Violation(
            PAYLOAD_TOO_LARGE,
            path,
            f"payload carries more text than max_total_length={policy.max_total_length} "
            "and was not fully screened",
        )
        return
    if depth > policy.max_depth:
        budget.stopped = True
        yield Violation(
            PAYLOAD_TOO_DEEP, path, f"payload nests deeper than max_depth={policy.max_depth}"
        )
        return
    if isinstance(value, Mapping):
        limit = _longest_denied_path(policy.denied_field_paths)
        # The arrow is already the separator between a string and the document
        # serialized inside it, so the root of an embedded document does not
        # take a dot as well: `content[0].text→rows`, not `→.rows`.
        joiner = "" if path.endswith(_EMBEDDED) else "."
        for index, (key, item) in enumerate(value.items()):
            name = str(key)
            budget.text += len(name)
            findings = _key_findings(name, policy)
            # Matching uses the real name; only what is reported is sanitized,
            # so sanitizing can never disarm a rule.
            safe = name if not findings and _SAFE_NAME.fullmatch(name) else f"<key#{index}>"
            child = f"{path}{joiner}{safe}"
            child_dotted = _extend_path(dotted, name, limit)
            child_shown = f"{shown}.{safe}" if shown else safe
            # A name declared inside a schema is not a field carrying a value.
            child_schema = in_schema or (
                bool(schema_keys) and normalize_key(name) in _normalized(schema_keys)
            )
            # Only the field-*name* rule steps aside inside a declared schema: a
            # tool may legitimately take a parameter called `phone`. A denied
            # path names a field of the operator's own boundary rather than a
            # schema keyword, so it runs everywhere, and the values under a
            # schema are screened by every rule either way. Gating it here too
            # switched `denied_field_paths` off for every catalogue and every
            # elicitation, silently, at the untrusted side's choosing.
            if not in_schema and policy.forbids_key(name):
                yield Violation(FORBIDDEN_KEY, child, f"field name {safe!r} is forbidden by policy")
            if policy.denies_path(name, child_dotted) and _carries_data(item, policy):
                yield Violation(
                    DENIED_FIELD_PATH, child, f"denied field {child_shown!r} carries a value"
                )
            for code, detail in findings:
                yield Violation(code, child, detail)
            yield from _walk(
                item,
                policy,
                child,
                child_dotted,
                child_shown,
                depth + 1,
                budget,
                schema_keys,
                child_schema,
            )
        return
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        budget.text += len(value)
        yield from _screen_scalar(value, policy, path)
        if isinstance(value, str):
            document = _document_candidate(value)
            if document is not None:
                yield from _walk_embedded(
                    document, policy, path, depth, budget, schema_keys, in_schema
                )
        return
    if isinstance(value, Sequence):
        for index, item in enumerate(value):
            yield from _walk(
                item,
                policy,
                f"{path}[{index}]",
                dotted,
                shown,
                depth + 1,
                budget,
                schema_keys,
                in_schema,
            )
        return
    # A number is screened as the text `str` renders it, so it costs the budget
    # what that text costs. Uncharged, a payload of long integers screened an
    # unbounded amount of text under a documented cap of `max_total_length`.
    yield from _screen_scalar(value, policy, path, budget)


#: The Unicode general categories of a code point that carries no glyph where
#: it sits: control and format characters (C, where U+FEFF, U+200B, U+00AD and
#: the bidi marks live), separators (Z, ordinary whitespace and U+00A0) and
#: combining marks (M). A serialized document is still one behind any run of
#: these, and `\s` covers only part of the set. It is not the whole of what
#: carries no glyph either -- see the two sets below.
_INVISIBLE_CATEGORIES = "CZM"

#: Unicode's `Default_Ignorable_Code_Point` property, transcribed by hand from
#: DerivedCoreProperties.txt --
#: https://www.unicode.org/Public/15.1.0/ucd/DerivedCoreProperties.txt, the
#: `# Default_Ignorable_Code_Point` block. The ranges are the file's, with its
#: adjacent lines merged (`180B..180D` + `180E` + `180F`, `2060..2064` +
#: `2065` + `2066..206F`, and the whole tag and variation-selector plane
#: `E0000..E0FFF`, which is where the 240 selectors `E0100..E01EF` live); they
#: are identical in Unicode 14.0, which CPython 3.11 ships, and in 16.0.
#:
#: A conforming renderer draws every one of them as nothing when it has no
#: glyph for it, which is exactly the property that decides whether a reader of
#: the payload sees the document unchanged. Category C, Z or M is not that
#: property: most of this set is in those categories, but the four Hangul
#: fillers (U+115F, U+1160, U+3164, U+FFA0) are category Lo, and prefixing a
#: serialized `content[].text` payload with one of them turned `forbidden_keys`
#: and `denied_field_paths` off for the whole payload.
_DEFAULT_IGNORABLE = re.compile(
    r"[\u00ad\u034f\u061c\u115f\u1160\u17b4\u17b5\u180b-\u180f"
    r"\u200b-\u200f\u202a-\u202e\u2060-\u206f\u3164\ufe00-\ufe0f\ufeff"
    r"\uffa0\ufff0-\ufff8\U0001bca0-\U0001bca3\U0001d173-\U0001d17a"
    r"\U000e0000-\U000e0fff]"
)

#: In no C, Z or M category and not `Default_Ignorable`, but both are drawn
#: blank by every font that has them, so they hide a document exactly the way
#: the set above does: the empty cell of the Braille block and the musical null
#: notehead. Both are category So, and both are refused here by name.
_BLANK_BY_GLYPH = frozenset("\u2800\U0001d159")


def _carries_no_glyph(char: str) -> bool:
    """Whether `char` renders as nothing where it sits, by any of the three rules."""
    return (
        unicodedata.category(char)[0] in _INVISIBLE_CATEGORIES
        or char in _BLANK_BY_GLYPH
        or _DEFAULT_IGNORABLE.match(char) is not None
    )


def _strip_invisible(text: str) -> str:
    """`text` with the invisible code points removed from both of its ends."""
    start, end = 0, len(text)
    while start < end and _carries_no_glyph(text[start]):
        start += 1
    while end > start and _carries_no_glyph(text[end - 1]):
        end -= 1
    return text[start:end]


def _document_candidate(text: str) -> str | None:
    r"""The serialized document a string carries, or None when it carries none.

    MCP's CallToolResult carries the tool's whole payload as serialized JSON
    inside `content[].text`, so a string whose first visible character opens a
    JSON object or array is a candidate document and not just a string --
    without that, the field-name and field-path rules, the two an operator
    configures, silently never fired behind the proxy and only the value
    detectors ran.

    Every code point at either end that carries no glyph is stripped first, and
    both the `{`/`[` test and `json.loads` run on the stripped text. Three sets
    say what that means: a Unicode general category of C, Z or M -- a control
    or format character, a separator, a combining mark -- every
    `Default_Ignorable_Code_Point`, which is where the Hangul fillers live, and
    the two code points every font draws blank, U+2800 and U+1D159. The test
    used to be `\s*[{\[]`, which let the untrusted side turn `forbidden_keys`
    and `denied_field_paths` off for a whole payload again by prefixing the
    document with one U+FEFF, U+200B or U+00AD; the categories alone, which
    replaced it, left the same bypass open behind one U+3164.

    A string whose first visible character is anything else -- prose, or a
    document behind a printable prologue such as XSSI's `)]}'` -- is not a
    candidate and is screened as a string only. The README says so.
    """
    stripped = _strip_invisible(text)
    return stripped if stripped[:1] in ("{", "[") else None


#: What separates a string from the document serialized inside it, in a
#: reported path: `content[0].text→rows`.
_EMBEDDED = "→"


def _walk_embedded(
    text: str,
    policy: Policy,
    path: str,
    depth: int,
    budget: _Budget,
    schema_keys: frozenset[str],
    in_schema: bool,
) -> Iterator[Violation]:
    """Screen serialized JSON carried inside a string with the full rules.

    `text` is what `_document_candidate` returned: the carrying string with the
    invisible code points stripped from both of its ends, which is what has to
    be parsed and what its length here is measured on.

    The document is screened under its own dotted root, so a policy's
    `patient.mrn` means the same thing inside a `content[].text` payload as it
    does in the file `egresswall check` reads. Node, depth and text costs are
    charged to the caller's budget, so an embedded document is bounded exactly
    like the one that carried it.

    A candidate that is not screened as a document is a violation, not a pass.
    This used to return quietly, so the untrusted side turned `forbidden_keys`
    and `denied_field_paths` off for its whole payload by appending one token a
    parser chokes on -- a duplicate key, an integer past this interpreter's
    digit limit, an array nested past the parser's recursion. The envelope
    already fails closed on exactly those inputs; this is the same rule one
    level in. `refuse_unparseable_embedded=False` restores the old walk.
    """
    if len(text) > policy.max_string_length:
        # Never parsed: too long to screen as a string is also too long to
        # screen as a document, and the string that carried it was refused for
        # its own length above.
        if policy.refuse_unparseable_embedded:
            yield Violation(
                EMBEDDED_DOCUMENT_UNPARSEABLE,
                path,
                "a serialized document longer than max_string_length was not screened as one",
            )
        return
    try:
        parsed = loads(text)
    except (ValueError, OverflowError, RecursionError):
        if policy.refuse_unparseable_embedded:
            yield Violation(
                EMBEDDED_DOCUMENT_UNPARSEABLE,
                path,
                "a serialized document could not be parsed and was not screened as one",
            )
        return
    yield from _walk(
        parsed, policy, path + _EMBEDDED, "", "", depth + 1, budget, schema_keys, in_schema
    )


def _screen_scalar(
    value: Any, policy: Policy, path: str, budget: _Budget | None = None
) -> Iterator[Violation]:
    if isinstance(value, (bytes, bytearray, memoryview)):
        text = bytes(value).decode("utf-8", errors="replace")
    elif isinstance(value, str):
        text = value
    elif value is None or isinstance(value, bool):
        return
    elif isinstance(value, float) and not math.isfinite(value):
        # `json.loads` maps 1e999 to an infinity and `json.dumps` writes that
        # back as the bare token `Infinity`, which is not JSON: forwarding it
        # would turn a message a strict client can read into one it cannot.
        # A value that cannot be re-emitted is a value that does not cross.
        yield Violation(
            PAYLOAD_TOO_LARGE, path, "a number outside the range this interpreter represents"
        )
        return
    else:
        try:
            text = str(value)
        except Exception:
            # An integer past CPython's int-to-string digit limit is ordinary
            # JSON that `str` refuses to render. Rendering is how a scalar is
            # screened, so a value that cannot be rendered has not been
            # screened: fail closed with a violation rather than raise out of
            # `check`, which is documented never to.
            yield Violation(PAYLOAD_TOO_LARGE, path, "a value could not be rendered for screening")
            return
        if budget is not None:
            budget.text += len(text)
    if not text:
        return
    if len(text) > policy.max_string_length:
        yield Violation(
            PAYLOAD_TOO_LARGE,
            path,
            f"string is longer than max_string_length={policy.max_string_length} "
            "and was not screened",
        )
        return
    for name, detect, code in policy.active_detectors():
        if detect(text, policy):
            yield Violation(code, path, f"the {name} detector matched")
    if _forbidden_value(text, policy.forbidden_values):
        yield Violation(FORBIDDEN_VALUE, path, "a forbidden literal value was assembled")


def check(
    payload: Any, policy: Policy | None = None, *, where: str = "response"
) -> list[Violation]:
    """Return every reason ``payload`` may not cross the boundary. Never raises."""
    return list(_walk(payload, policy or Policy(), where, "", "", 0, _Budget()))


def _first(
    payload: Any,
    policy: Policy,
    *,
    where: str = "response",
    schema_keys: frozenset[str] = frozenset(),
    budget: _Budget | None = None,
) -> Violation | None:
    """The first reason ``payload`` may not cross, or None. Never raises.

    Where only one reason is ever reported -- the proxy's JSON-RPC error, the
    drop log -- this is what stops a hostile payload from materialising tens of
    thousands of Violation objects to name one of them.

    ``schema_keys`` names the fields below which the payload declares a schema
    rather than answering with data; the field-name rules step aside there. It is
    the proxy's knob for a discovery result and is empty everywhere else.

    ``budget`` is passed in when one message is screened as several documents --
    the proxy screens each JSON-RPC member under its own dotted root -- so the
    size limits stay a bound on the message and not on each member of it.
    """
    return next(
        _walk(payload, policy, where, "", "", 0, budget or _Budget(), schema_keys),
        None,
    )


def screen(payload: Any, policy: Policy | None = None, *, where: str = "response") -> Any:
    """Raise :class:`EgressViolation` on the first violation; else return ``payload``."""
    violation = _first(payload, policy or Policy(), where=where)
    if violation is not None:
        raise EgressViolation(violation.code, violation.path, violation.detail)
    return payload


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            # The key is chosen by whatever wrote the document, so the message
            # counts the field rather than naming it.
            raise ValueError(f"duplicate object key at field {len(seen) + 1}")
        seen[key] = value
    return seen


def loads(text: str) -> Any:
    """``json.loads``, refusing an object that spells the same key twice.

    Python keeps the last spelling. A document whose first spelling of a field
    carries a value and whose second is clean would screen clean here and leak
    wherever it is read first-wins, so ambiguous input is refused instead:
    input that cannot be screened unambiguously has not been screened.
    """
    return json.loads(text, object_pairs_hook=_no_duplicate_keys)
