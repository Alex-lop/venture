"""One positive and one negative case per detector, plus ReDoS resistance."""

from __future__ import annotations

import sys
import time

import pytest

from egresswall import (
    DETECTORS,
    JOIN_TOKEN,
    MAX_ALLOWED_DEPTH,
    MAX_FORBIDDEN_VALUES,
    RAW_IDENTIFIER,
    SECRET_MATERIAL,
    Policy,
    check,
)

OPEN = Policy(forbidden_keys=frozenset())

POSITIVE = {
    "email": "reach member-88231@northgate-clinic.test today",
    "ssn": "ssn on file 412-88-7690 verified",
    "phone": "call (617) 555-0142 back",
    "join_token": "cohort hmac-sha256:" + "ab" * 32,
    "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIE...",
    "aws_access_key": "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
    "github_token": "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8",
    "anthropic_key": "sk-ant-api03-" + "Xq7" * 12,
    "openai_key": "sk-proj-" + "Zk4Qb7Xm2R" * 5,
    "bearer_token": "Authorization: Bearer " + "eyJhbGciOiJIUzI1NiJ9.abcdefghij",
}

NEGATIVE = {
    "email": "the at sign @ alone, and northgate-clinic.test, are not addresses",
    "ssn": "order 412-88-769 and 4128876901234 are not SSNs",
    "phone": "version 1.555.0142 and 100-555-0142 are not phone numbers",
    "join_token": "hmac-sha256:deadbeef is too short to be a join key",
    "private_key": "-----BEGIN PUBLIC KEY----- and -----BEGIN CERTIFICATE-----",
    "aws_access_key": "AKIA is a prefix; AKIASHORT is not a key id",
    "github_token": "ghp_short and github_pat_x are not tokens",
    "anthropic_key": "sk-ant-1234 is too short",
    "openai_key": (
        "sk-1234 is too short, sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx is not OpenAI's, and "
        "sk-widget-blue-large-2026-edition-with-more-words is a product slug"
    ),
    "bearer_token": "bearer with nothing after it, and Bearer short",
}


@pytest.mark.parametrize("name", sorted(DETECTORS))
def test_every_detector_has_a_positive_and_a_negative_case(name: str) -> None:
    assert name in POSITIVE and name in NEGATIVE


@pytest.mark.parametrize("name", sorted(DETECTORS))
def test_detector_fires_on_its_positive_case(name: str) -> None:
    only = Policy(forbidden_keys=frozenset(), detectors=frozenset({name}))
    found = check({"v": POSITIVE[name]}, only)
    assert [item.code for item in found] == [DETECTORS[name][1]], name


@pytest.mark.parametrize("name", sorted(DETECTORS))
def test_detector_stays_quiet_on_its_negative_case(name: str) -> None:
    only = Policy(forbidden_keys=frozenset(), detectors=frozenset({name}))
    assert check({"v": NEGATIVE[name]}, only) == [], name


def test_a_placeholder_email_is_still_a_violation_by_default() -> None:
    assert [item.code for item in check({"v": "user@example.com"}, OPEN)] == [RAW_IDENTIFIER]

    only = Policy(forbidden_keys=frozenset(), detectors=frozenset({"email"}))
    for first in "abcdefghijklmnopqrstuvwxyz":
        for second in "abcdefghijklmnopqrstuvwxyz":
            address = f"member@clinic.{first}{second}"
            assert [item.code for item in check(address, only)] == [RAW_IDENTIFIER], address


def test_allow_domains_exempts_exactly_the_listed_domain() -> None:
    policy = Policy(forbidden_keys=frozenset(), allow_domains=frozenset({"example.com"}))
    assert check({"v": "user@example.com"}, policy) == []
    assert check({"v": "USER@Example.COM"}, policy) == []
    assert [item.code for item in check({"v": "user@mail.example.com"}, policy)] == [RAW_IDENTIFIER]


def test_an_anthropic_key_is_not_reported_as_an_openai_key() -> None:
    policy = Policy(forbidden_keys=frozenset(), detectors=frozenset({"openai_key"}))
    assert check({"v": POSITIVE["anthropic_key"]}, policy) == []


def test_secret_detectors_share_one_reason_code() -> None:
    secrets = {
        "private_key",
        "aws_access_key",
        "github_token",
        "anthropic_key",
        "openai_key",
        "bearer_token",
    }
    assert {DETECTORS[name][1] for name in secrets} == {SECRET_MATERIAL}


@pytest.mark.parametrize(
    "hostile",
    [
        "a" * 40000 + "@" + "b" * 40000,
        "a" * 40000 + "@" + "b." * 20000,
        ("a." * 20000) + "@b",
        "hmac-sha256:" + "a" * 60000,
        "Bearer " + "-" * 60000,
        "sk-proj-" + "-" * 60000,
        "-----BEGIN " + "A" * 60000,
        "1" * 60000,
        "(617)" + " " * 60000,
    ],
)
def test_pathological_input_does_not_blow_up_the_matcher(hostile: str) -> None:
    started = time.monotonic()
    check({"v": hostile}, OPEN)
    assert time.monotonic() - started < 1.0, "a detector backtracked badly"


def test_a_long_string_is_blocked_rather_than_scanned() -> None:
    policy = Policy(forbidden_keys=frozenset(), max_string_length=1000)
    started = time.monotonic()
    found = check({"v": "a" * 500000 + "@" + "b" * 500000}, policy)
    assert [item.code for item in found] == ["PAYLOAD_TOO_LARGE"]
    assert time.monotonic() - started < 1.0


def test_the_join_token_detector_covers_every_shape_the_readme_lists() -> None:
    """The regex takes sha512 and 65-128 hex digits, not only sha256 and 64."""
    only = Policy(forbidden_keys=frozenset(), detectors=frozenset({"join_token"}))
    shapes = ("hmac-sha256:" + "ab" * 32, "hmac-sha512:" + "cd" * 64, "hmac-sha256:" + "e" * 65)
    for token in shapes:
        assert [item.code for item in check({"v": token}, only)] == [JOIN_TOKEN], token


def test_an_sk_prefixed_product_slug_is_not_an_openai_key() -> None:
    """A real key is 40+ high-entropy characters; a catalogue SKU is not one."""
    only = Policy(forbidden_keys=frozenset(), detectors=frozenset({"openai_key"}))
    assert check({"sku": "sk-widget-blue-large-2026-edition"}, only) == []
    assert check({"sku": "sk-widget-blue-large-2026-edition-with-more-words"}, only) == []
    assert [item.code for item in check({"v": POSITIVE["openai_key"]}, only)] == [SECRET_MATERIAL]


#: The most text one payload may carry: the bound the timings below measure.
CAP = Policy().max_total_length
#: The largest denylists a policy may hold, which is what makes them worth timing.
VALUES = frozenset(f"zq{index:05d}wv" for index in range(MAX_FORBIDDEN_VALUES))
PATHS = frozenset(f"a{index:05d}.b{index:05d}" for index in range(10_000))


def flat_rows() -> tuple[dict, Policy]:
    """Many small strings: the cheapest shape, and the one to beat."""
    return {f"row_{index}": {"note": "n" * 4083} for index in range(CAP // 4096)}, OPEN


def deep_with_long_names() -> tuple[dict, Policy]:
    """The deepest a policy may nest, with field names long enough to hurt.

    Re-normalizing the accumulated dotted path at every node made this shape
    quadratic in the depth rather than linear in the payload.
    """
    payload: dict = {}
    node = payload
    for index in range(MAX_ALLOWED_DEPTH):
        child: dict = {}
        node[f"k{index:04d}" + "a" * (CAP // MAX_ALLOWED_DEPTH - 5)] = child
        node = child
    node["end"] = 1
    policy = Policy(
        forbidden_keys=frozenset(),
        max_depth=MAX_ALLOWED_DEPTH,
        denied_field_paths=PATHS,
    )
    return payload, policy


def full_forbidden_value_list() -> tuple[dict, Policy]:
    """A full denylist over text that is nothing but candidate positions for it.

    Every character starts a value in the list, so the matcher's fast path never
    fires. Scanning once per entry instead made this shape O(entries x bytes).
    """
    payload = {f"row_{index}": {"note": "z" * 4083} for index in range(CAP // 4096)}
    return payload, Policy(forbidden_keys=frozenset(), forbidden_values=VALUES)


def colliding_forbidden_value_list() -> tuple[dict, Policy]:
    """A denylist whose entries all share a head, over text made of that head.

    This is the shape the shape above misses. Entries of one length give every
    bucket of a head index exactly one candidate, so an index that degenerates
    when entries collide measures fast anyway. Here one short entry sets the
    index width and every other entry shares that width's prefix, and the text
    is that prefix repeated: 201 such entries took five seconds over this
    payload before the matcher became an automaton. Nothing in it matches, so
    the cost measured is the search and not an early exit.
    """
    payload = {f"row_{index}": {"note": "NG" * 2041} for index in range(CAP // 4096)}
    values = frozenset({"QA"} | {f"NG-{index:06d}" for index in range(MAX_FORBIDDEN_VALUES - 1)})
    return payload, Policy(forbidden_keys=frozenset(), forbidden_values=values)


def full_denied_path_list() -> tuple[dict, Policy]:
    """A denied-path list of ten thousand entries is one set lookup per node."""
    payload = {f"row_{index}": {"note": "n" * 4083} for index in range(CAP // 4096)}
    return payload, Policy(forbidden_keys=frozenset(), denied_field_paths=PATHS)


def full_key_name_lists() -> tuple[dict, Policy]:
    """A payload of nothing but field names, against full substring and suffix lists.

    `MAX_FORBIDDEN_VALUES` bounds `forbidden_values` and nothing bounded these
    two, which were re-scanned per field name: ten thousand substrings cost ten
    seconds over this payload before both became precomputed matchers.
    """
    payload = {f"k{index:06d}" + "a" * 20: "n" * 30 for index in range(CAP // 60)}
    policy = Policy(
        forbidden_keys=frozenset(),
        forbidden_key_substrings=frozenset(f"zqsub{index:05d}" for index in range(10_000)),
        forbidden_key_suffixes=frozenset(f"zqsuf{index:05d}" for index in range(10_000)),
    )
    return payload, policy


def max_digit_numbers() -> tuple[dict, Policy]:
    """A payload of the longest integers this interpreter renders.

    A JSON number is screened as the text `str` renders it, and that text used
    to cost the budget nothing: 8.6 MB of digits screened in 1.27 s with
    `max_total_length` reporting 0 text spent, so the documented bound was not a
    bound on numbers at all. Charging the rendered length is what puts this
    shape under the same cap as the others.
    """
    digits = sys.get_int_max_str_digits()
    value = int("9" * digits)
    payload = {f"n{index:05d}": value for index in range(CAP // digits)}
    return payload, OPEN


SHAPES = [
    flat_rows,
    deep_with_long_names,
    full_forbidden_value_list,
    colliding_forbidden_value_list,
    full_denied_path_list,
    full_key_name_lists,
    max_digit_numbers,
]


@pytest.mark.parametrize("shape", SHAPES)
def test_the_most_text_a_policy_allows_screens_in_under_a_second(shape) -> None:
    """Every input inside the documented caps screens in about a tool call's time.

    Not only the cheap shape: depth, long field names and a full denylist are the
    inputs that used to blow the bound while a flat-rows test passed.
    """
    payload, policy = shape()
    started = time.monotonic()
    found = check(payload, policy)
    elapsed = time.monotonic() - started
    assert elapsed < 1.0, f"{shape.__name__} took {elapsed:.2f}s"
    # No rule matches in any shape, so what is timed is the search over the
    # whole payload rather than a first violation the walk stopped at. Only the
    # deepest shape reports anything, and only because it is one node deeper
    # than the policy allows -- which it reaches after walking all of it.
    assert {item.code for item in found} <= {"PAYLOAD_TOO_DEEP"}, found[:1]


def test_a_payload_over_the_text_budget_is_refused_rather_than_screened() -> None:
    """The budget is what makes the timing above a bound and not a sample."""
    payload, _ = flat_rows()
    over = {"a": payload, "b": payload, "c": payload, "d": payload}
    started = time.monotonic()
    found = check(over, OPEN)
    assert [item.code for item in found] == ["PAYLOAD_TOO_LARGE"]
    assert time.monotonic() - started < 1.0

    policy = Policy(forbidden_keys=frozenset(), max_total_length=10)
    for lengths in ((10,), (5, 5), (1, 9)):
        assert check(["x" * length for length in lengths], policy) == [], lengths
    detail = "payload carries more text than max_total_length=10 and was not fully screened"
    for lengths, index in (((11,), 0), ((6, 5), 1), ((4, 4, 3), 2)):
        found = check(["x" * length for length in lengths], policy)
        assert [item.code for item in found] == ["PAYLOAD_TOO_LARGE"], lengths
        assert (found[0].path, found[0].detail) == (f"response[{index}]", detail)


def test_a_field_name_counts_against_the_text_budget_like_a_value() -> None:
    """A payload of nothing but long field names is text too, and is bounded too."""
    policy = Policy(forbidden_keys=frozenset(), max_total_length=1000)
    assert check({"n" * 400: 1, "m" * 400: 2}, policy) == []
    found = check({"n" * 400: 1, "m" * 400: 2, "o" * 400: 3}, policy)
    assert [item.code for item in found] == ["PAYLOAD_TOO_LARGE"]


def test_a_rendered_number_counts_against_the_text_budget_like_a_string() -> None:
    """A number is screened as the text `str` renders it, so it costs that text.

    Uncharged, a payload of long integers screened an unbounded amount of text
    under a documented cap: the walk read every digit with all ten detectors
    while `max_total_length` was still reporting nothing spent.
    """
    big = int("9" * 400)
    policy = Policy(forbidden_keys=frozenset(), max_total_length=1000)
    assert check({"a": big, "b": big}, policy) == []
    # A number is charged after it is rendered, so the walk overruns by at most
    # one node's worth of text before the next node refuses the payload -- the
    # same one-node slack the string branch has.
    found = check({"a": big, "b": big, "c": big, "d": big}, policy)
    assert [item.code for item in found] == ["PAYLOAD_TOO_LARGE"]
