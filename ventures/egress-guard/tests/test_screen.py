"""Screening semantics, ported from RegLineage's tests/unit/test_egress.py."""

from __future__ import annotations

import json
from itertools import product
from typing import ClassVar

import pytest

from egresswall import (
    DEFAULT_GOVERNANCE_TOKENS,
    DENIED_FIELD_PATH,
    EMBEDDED_DOCUMENT_UNPARSEABLE,
    FORBIDDEN_KEY,
    FORBIDDEN_VALUE,
    JOIN_TOKEN,
    MAX_DENIED_PATH_CHARS,
    MAX_FORBIDDEN_VALUES,
    PAYLOAD_TOO_DEEP,
    PAYLOAD_TOO_LARGE,
    RAW_IDENTIFIER,
    SECRET_MATERIAL,
    EgressViolation,
    Policy,
    Violation,
    check,
    screen,
)

EMAIL = "member-88231@northgate-clinic.test"
OPEN = Policy(forbidden_keys=frozenset())


class TestShapeRules:
    """Some shapes are never releasable, whatever the policy says."""

    def test_raw_email_is_blocked_anywhere_in_the_payload(self) -> None:
        payload = {"a": [{"b": {"c": f"contact {EMAIL} now"}}]}
        with pytest.raises(EgressViolation) as caught:
            screen(payload, OPEN)
        assert caught.value.reason == RAW_IDENTIFIER
        assert caught.value.path == "response.a[0].b.c"

    def test_join_token_is_blocked(self) -> None:
        # Built by concatenation and bound to a name that is not
        # `token`/`secret`/`api_key`-shaped, so the repo's pre-push secret scan
        # reads this fixture as the test data it is.
        join_key = "hmac-" + "sha256:" + "ab" * 32
        with pytest.raises(EgressViolation) as caught:
            screen({"cohort": join_key}, OPEN)
        assert caught.value.reason == JOIN_TOKEN

    def test_governed_aggregate_passes(self) -> None:
        payload = {
            "cohort": "HIGH/LOW/PREMIUM/ELEVATED",
            "cohort_size": 25,
            "week_2_abandonment_rate": "0.7200",
        }
        assert screen(payload, OPEN) is payload

    def test_empty_and_null_values_pass(self) -> None:
        assert check({"a": None, "b": "", "c": [], "d": {}, "e": False}, OPEN) == []

    def test_a_number_that_looks_like_an_ssn_is_screened_as_text(self) -> None:
        assert check({"n": 4128}, OPEN) == []
        assert [item.code for item in check({"n": "412-88-7690"}, OPEN)] == [RAW_IDENTIFIER]

    @pytest.mark.parametrize("wrap", [bytes, bytearray, memoryview])
    def test_binary_text_is_decoded_and_screened(self, wrap) -> None:
        """bytearray is a Sequence and memoryview is neither: both used to walk past."""
        found = check({"b": wrap(EMAIL.encode())}, OPEN)
        assert [item.code for item in found] == [RAW_IDENTIFIER], wrap

    def test_the_where_argument_names_the_root_of_every_path(self) -> None:
        found = check({"x": EMAIL}, OPEN, where="tools/call.result")
        assert found[0].path == "tools/call.result.x"


class TestForbiddenKeys:
    """Ported from RegLineage's mcp_runtime._screen key-name rules."""

    @pytest.mark.parametrize(
        "key", ["api_key", "raw_rows", "rows", "sql", "ssn", "password", "secrets", "user_id"]
    )
    def test_a_default_forbidden_key_blocks_on_the_name_alone(self, key: str) -> None:
        found = check({key: []})
        assert [item.code for item in found] == [FORBIDDEN_KEY]

    @pytest.mark.parametrize(
        "key", ["aws_credentials", "user_password", "reviewer_override_note", "client_secret"]
    )
    def test_substring_rules_catch_unlisted_names(self, key: str) -> None:
        assert [item.code for item in check({key: 1})] == [FORBIDDEN_KEY]

    def test_the_token_suffix_rule_catches_unlisted_names(self) -> None:
        assert [item.code for item in check({"refresh_token": 1})] == [FORBIDDEN_KEY]

    def test_key_matching_is_case_insensitive(self) -> None:
        assert [item.code for item in check({"API_KEY": 1})] == [FORBIDDEN_KEY]

    def test_a_forbidden_name_as_a_value_is_not_a_violation(self) -> None:
        assert check({"denied_fields": ["api_key", "ssn"]}) == []

    def test_an_emptied_forbidden_key_set_disables_the_rule(self) -> None:
        assert check({"api_key": 1}, Policy(forbidden_keys=frozenset())) == []


class TestDeniedFieldPaths:
    def test_a_denied_bare_name_blocks_at_any_depth(self) -> None:
        policy = Policy(forbidden_keys=frozenset(), denied_field_paths=frozenset({"mrn"}))
        found = check({"records": [{"mrn": "NG-88231"}]}, policy)
        assert found == [
            Violation(
                DENIED_FIELD_PATH,
                "response.records[0].mrn",
                "denied field 'records.mrn' carries a value",
            )
        ]

    @pytest.mark.parametrize("payload", [{"patient": {"MRN": "x"}}, {"Patient": {"mrn": "x"}}])
    def test_a_denied_path_is_matched_like_a_field_name(self, payload: dict) -> None:
        """Case and separators are removed on both sides, as they are for forbidden keys."""
        policy = Policy(forbidden_keys=frozenset(), denied_field_paths=frozenset({"patient.mrn"}))
        assert [item.code for item in check(payload, policy)] == [DENIED_FIELD_PATH], payload

    def test_a_denied_dotted_path_blocks_only_under_its_parent(self) -> None:
        policy = Policy(forbidden_keys=frozenset(), denied_field_paths=frozenset({"patient.mrn"}))
        assert [item.code for item in check({"patient": {"mrn": "NG-88231"}}, policy)] == [
            DENIED_FIELD_PATH
        ]
        assert check({"study": {"mrn": "NG-88231"}}, policy) == []

    def test_a_denied_field_carrying_a_container_is_blocked(self) -> None:
        policy = Policy(forbidden_keys=frozenset(), denied_field_paths=frozenset({"mrn"}))
        assert [item.code for item in check({"mrn": ["NG-88231"]}, policy)] == [DENIED_FIELD_PATH]

    @pytest.mark.parametrize("value", [0, False, "", [], {}, "NG-88231", " "])
    def test_a_denied_field_that_exists_at_all_is_blocked(self, value: object) -> None:
        """One rule: present is enough. Only None and governance vocabulary pass."""
        policy = Policy(forbidden_keys=frozenset(), denied_field_paths=frozenset({"mrn"}))
        assert [item.code for item in check({"mrn": value}, policy)] == [DENIED_FIELD_PATH], value

    @pytest.mark.parametrize("value", [None, "DENY", "MODEL_CONTEXT_DENIED"])
    def test_a_denied_field_passes_only_when_absent_or_governance_vocabulary(
        self, value: object
    ) -> None:
        policy = Policy(forbidden_keys=frozenset(), denied_field_paths=frozenset({"mrn"}))
        assert check({"mrn": value}, policy) == [], value

    def test_governance_text_may_name_a_denied_field(self) -> None:
        """Explaining a denial is not the same as leaking a value."""
        policy = Policy(
            forbidden_keys=frozenset(), denied_field_paths=frozenset({"resting_heart_rate"})
        )
        assert (
            check(
                {
                    "field_path": "resting_heart_rate",
                    "capability": "MODEL_CONTEXT",
                    "decision": "DENY",
                    "reason_codes": ["MODEL_CONTEXT_DENIED_BIOMETRIC"],
                    "resting_heart_rate": "DENY",
                },
                policy,
            )
            == []
        )

    def test_an_uppercase_value_with_digits_is_data_not_vocabulary(self) -> None:
        policy = Policy(forbidden_keys=frozenset(), denied_field_paths=frozenset({"mrn"}))
        assert [item.code for item in check({"mrn": "NG-88231"}, policy)] == [DENIED_FIELD_PATH]

    def test_allow_tokens_extends_the_governance_vocabulary(self) -> None:
        policy = Policy(
            forbidden_keys=frozenset(),
            denied_field_paths=frozenset({"mrn"}),
            allow_tokens=frozenset({"withheld"}),
        )
        assert check({"mrn": "withheld"}, policy) == []


class TestForbiddenValues:
    def test_a_forbidden_literal_is_blocked_as_a_substring(self) -> None:
        policy = Policy(forbidden_keys=frozenset(), forbidden_values=frozenset({"HIGH"}))
        found = check({"note": "cohort HIGH performed worst"}, policy)
        assert [item.code for item in found] == [FORBIDDEN_VALUE]

    def test_a_forbidden_literal_is_case_sensitive(self) -> None:
        policy = Policy(forbidden_keys=frozenset(), forbidden_values=frozenset({"HIGH"}))
        assert check({"note": "cohort high performed worst"}, policy) == []

        texts = ["".join(chars) for size in range(5) for chars in product("abx", repeat=size)]
        for size in range(1, 4):
            for chars in product("ab", repeat=size):
                value = "".join(chars)
                policy = Policy(
                    forbidden_keys=frozenset(),
                    forbidden_values=frozenset({value}),
                    detectors=frozenset(),
                )
                for text in texts:
                    found = check(text, policy)
                    assert bool(found) is (value in text), (value, text)

    @pytest.mark.parametrize(
        "text", ["HIGHland", "the HIGH", "a HIGH note", "HIGH", "HHIGH", "\u00e9HIGH"]
    )
    def test_a_forbidden_literal_is_found_wherever_it_sits(self, text: str) -> None:
        """The matcher scans by candidate offset, so every offset has to be one."""
        policy = Policy(forbidden_keys=frozenset(), forbidden_values=frozenset({"HIGH"}))
        assert [item.code for item in check({"n": text}, policy)] == [FORBIDDEN_VALUE]

    @pytest.mark.parametrize("text", ["HIG", "HI GH", "hIGH", "HIGx", "HH"])
    def test_a_near_miss_is_not_a_forbidden_literal(self, text: str) -> None:
        policy = Policy(forbidden_keys=frozenset(), forbidden_values=frozenset({"HIGH"}))
        assert check({"n": text}, policy) == []

    def test_entries_of_different_lengths_are_all_matched(self) -> None:
        """The matcher keys on the shortest entry's width; longer ones must still fire."""
        values = frozenset({"AB", "ABCDEFGH", "ZZZZZZ"})
        policy = Policy(forbidden_keys=frozenset(), forbidden_values=values)
        for text in ("xxABxx", "xxABCDEFGHxx", "xxZZZZZZxx"):
            assert [item.code for item in check({"n": text}, policy)] == [FORBIDDEN_VALUE], text
        assert check({"n": "xxZZZZZxx"}, policy) == []

    def test_a_regex_metacharacter_in_an_entry_is_a_literal(self) -> None:
        values = frozenset({"a.c", "[x]", "^y$"})
        policy = Policy(forbidden_keys=frozenset(), forbidden_values=values)
        assert [item.code for item in check({"n": "1 [x] 2"}, policy)] == [FORBIDDEN_VALUE]
        assert check({"n": "abc"}, policy) == []

    @pytest.mark.parametrize(
        "field", ["forbidden_values", "forbidden_key_substrings", "forbidden_key_suffixes"]
    )
    def test_an_empty_entry_is_refused_rather_than_matching_everything(self, field: str) -> None:
        """A trailing comma in a policy file would otherwise refuse every payload."""
        with pytest.raises(ValueError, match=f"{field} may not hold an empty string"):
            Policy.from_dict({field: [""]})

    def test_the_largest_denylist_a_policy_may_hold_still_matches(self) -> None:
        values = frozenset(f"zq{index:05d}wv" for index in range(MAX_FORBIDDEN_VALUES))
        policy = Policy(forbidden_keys=frozenset(), forbidden_values=values)
        assert [item.code for item in check({"n": "see zq09999wv now"}, policy)] == [
            FORBIDDEN_VALUE
        ]
        assert check({"n": "see zq10000wv now"}, policy) == []

    def test_a_denylist_over_the_bound_is_refused_when_the_policy_is_built(self) -> None:
        over = frozenset(f"v{index}" for index in range(MAX_FORBIDDEN_VALUES + 1))
        with pytest.raises(ValueError, match="forbidden_values holds at most"):
            Policy(forbidden_values=over)


class TestLimits:
    def test_depth_beyond_max_depth_blocks_rather_than_recursing(self) -> None:
        payload: dict = {}
        node = payload
        for _ in range(60):
            node["next"] = {}
            node = node["next"]
        found = check(payload, Policy(max_depth=8))
        assert [item.code for item in found] == [PAYLOAD_TOO_DEEP]

    def test_more_nodes_than_max_nodes_blocks(self) -> None:
        found = check({"items": list(range(100))}, Policy(max_nodes=10))
        assert [item.code for item in found] == [PAYLOAD_TOO_LARGE]

        policy = Policy(forbidden_keys=frozenset(), max_nodes=3)
        assert check([1, 2], policy) == []
        assert [item.code for item in check([1, 2, 3], policy)] == [PAYLOAD_TOO_LARGE]

    def test_a_string_longer_than_the_limit_is_blocked_not_skipped(self) -> None:
        policy = Policy(forbidden_keys=frozenset(), max_string_length=100)
        found = check({"blob": "x" * 101}, policy)
        assert [item.code for item in found] == [PAYLOAD_TOO_LARGE]

        shaped = memoryview(b"x" * 80).cast("B", shape=[1, 80])
        policy = Policy(
            forbidden_keys=frozenset(),
            detectors=frozenset(),
            max_string_length=1000,
            max_total_length=1,
        )
        assert [item.code for item in check(shaped, policy)] == [PAYLOAD_TOO_LARGE]

        released = memoryview(b"x")
        released.release()
        assert [item.code for item in check(released, policy)] == [PAYLOAD_TOO_LARGE]

    def test_limits_must_be_positive(self) -> None:
        with pytest.raises(ValueError, match="max_depth"):
            Policy(max_depth=0)


class TestNoValueEverLeaks:
    def test_no_violation_message_contains_the_value(self) -> None:
        # AWS's own documentation example, concatenated and bound to a
        # non-credential-shaped name for the same pre-push scan.
        access_id = "AKIA" + "IOSFODNN7EXAMPLE"
        payload = {"customer": {"contact": EMAIL, "creds": access_id}}
        found = check(payload, Policy(forbidden_keys=frozenset()))
        assert found
        for item in found:
            rendered = str(item) + repr(item.to_dict())
            assert EMAIL not in rendered
            assert access_id not in rendered

    def test_the_exception_message_does_not_contain_the_value(self) -> None:
        with pytest.raises(EgressViolation) as caught:
            screen({"a": EMAIL}, OPEN)
        assert EMAIL not in str(caught.value)


class TestPolicyFile:
    def test_round_trips_through_json(self, tmp_path) -> None:
        import json

        policy = Policy(
            denied_field_paths=frozenset({"patient.mrn"}),
            forbidden_values=frozenset({"ACME"}),
            max_depth=4,
        )
        path = tmp_path / "policy.json"
        path.write_text(json.dumps(policy.to_dict()))
        assert Policy.from_file(path) == policy

    def test_an_unknown_policy_key_is_an_error(self) -> None:
        with pytest.raises(ValueError, match="unknown policy keys: redact"):
            Policy.from_dict({"redact": True})

    def test_an_unknown_detector_is_an_error(self) -> None:
        with pytest.raises(ValueError, match="unknown detectors: passport"):
            Policy(detectors=frozenset({"passport"}))

    def test_a_wrongly_typed_policy_value_is_an_error(self) -> None:
        with pytest.raises(ValueError, match="max_depth must be an integer"):
            Policy.from_dict({"max_depth": "8"})
        with pytest.raises(ValueError, match="must be a list of strings"):
            Policy.from_dict({"denied_field_paths": "mrn"})

    def test_selecting_a_subset_of_detectors_turns_the_rest_off(self) -> None:
        policy = Policy(forbidden_keys=frozenset(), detectors=frozenset({"ssn"}))
        assert check({"a": EMAIL}, policy) == []
        assert [item.code for item in check({"a": "412-88-7690"}, policy)] == [RAW_IDENTIFIER]


class TestForbiddenKeySpellings:
    """A field name is matched on its normalized form, so casing and separators
    cannot smuggle a known-bad name past the list."""

    @pytest.mark.parametrize(
        "key",
        [
            "api_key",
            "apiKey",
            "api-key",
            "API-KEY",
            "apikey",
            "x-api-key",
            "authorization",
            "Authorization",
            "access_key",
            "accessKey",
            "private_key",
            "session_id",
            "sessionId",
            "refresh-token",
            "bearerToken",
            "auth_token",
            "client_secret",
            "clientSecret",
        ],
    )
    def test_a_forbidden_field_name_is_caught_however_it_is_spelled(self, key: str) -> None:
        found = check({key: "zzzzzzzzzzzzzzzz"}, Policy(detectors=frozenset()))
        assert [item.code for item in found] == [FORBIDDEN_KEY], key

    @pytest.mark.parametrize("key", ["author", "keys", "api_documentation_url", "tokenizer"])
    def test_a_neighbouring_name_is_not_caught(self, key: str) -> None:
        assert check({key: "ordinary"}, Policy(detectors=frozenset())) == [], key


class TestCheckNeverRaises:
    """check() documents that it never raises. Every input that could break that is here."""

    def test_an_integer_past_the_digit_limit_is_a_violation_not_an_exception(self) -> None:
        """`str(10**5000)` raises before any detector runs, and json.dumps(10**5000) does not.

        A caller screening a dict their own tool assembled -- rather than one
        they parsed -- would otherwise get an uncaught ValueError out of the
        function documented as the one that cannot raise.
        """
        found = check({"n": 10**5000})
        assert [item.code for item in found] == [PAYLOAD_TOO_LARGE]
        assert "could not be rendered" in found[0].detail
        with pytest.raises(EgressViolation):
            screen({"n": 10**5000})

        found = check({10**5000: "safe"})
        assert [item.code for item in found] == [PAYLOAD_TOO_LARGE]
        assert "could not be rendered" in found[0].detail

        class HostileText(str):
            def __str__(self) -> str:
                return self

            def __len__(self) -> int:
                raise RuntimeError("must not escape")

            def __hash__(self) -> int:
                raise RuntimeError("must not escape")

        class HostileKey:
            def __str__(self) -> str:
                return HostileText("safe")

        assert check({HostileKey(): "safe"}) == []

    def test_a_policy_deeper_than_the_walk_can_recurse_is_refused(self) -> None:
        with pytest.raises(ValueError, match="max_depth must be <= 500"):
            Policy.from_dict({"max_depth": 10**9})

    def test_a_payload_deeper_than_the_recursion_limit_is_refused_not_raised(self) -> None:
        payload: dict = {}
        cursor = payload
        for _ in range(2000):
            cursor["a"] = {}
            cursor = cursor["a"]
        cursor["email"] = "member-88231@northgate-clinic.test"
        found = check(payload, Policy.from_dict({"max_depth": 500}))
        assert [item.code for item in found] == [PAYLOAD_TOO_DEEP]


class TestPolicyShape:
    """A policy file is a trust boundary: no JSON shape may escape as a traceback."""

    @pytest.mark.parametrize("data", [None, True, 123, "text", ["denied_field_paths"]])
    def test_a_policy_that_is_not_a_json_object_is_a_policy_error(self, data: object) -> None:
        with pytest.raises(ValueError, match="policy must be a JSON object"):
            Policy.from_dict(data)  # type: ignore[arg-type]


class TestSuffixRuleSemantics:
    """The suffix is matched after normalization, which is what the README says."""

    @pytest.mark.parametrize("key", ["refresh_token", "refreshToken", "nextToken", "next_token"])
    def test_the_suffix_rule_matches_the_normalized_name(self, key: str) -> None:
        assert [item.code for item in check({key: 1})] == [FORBIDDEN_KEY], key

    def test_dropping_the_suffix_lets_a_pagination_cursor_through(self) -> None:
        policy = Policy(forbidden_key_suffixes=frozenset())
        assert check({"nextToken": "abc"}, policy) == []


class TestFieldNamesAreScreenedLikeValues:
    """A lookup table keyed by an identifier is the shape a lookup tool returns."""

    def test_an_identifier_used_as_a_field_name_is_a_violation(self) -> None:
        found = check({"contacts": {EMAIL: "vip"}}, OPEN)
        assert [item.code for item in found] == [RAW_IDENTIFIER]

    def test_an_ssn_used_as_a_field_name_is_a_violation(self) -> None:
        found = check({"balances": {"412-88-7690": 10}}, OPEN)
        assert [item.code for item in found] == [RAW_IDENTIFIER]

    def test_a_secret_used_as_a_field_name_is_a_violation(self) -> None:
        found = check({"AKIAIOSFODNN7EXAMPLE": 1}, OPEN)
        assert [item.code for item in found] == [SECRET_MATERIAL]

    def test_a_forbidden_literal_used_as_a_field_name_is_a_violation(self) -> None:
        policy = Policy(forbidden_keys=frozenset(), forbidden_values=frozenset({"ACME"}))
        assert [item.code for item in check({"ACME-CASE": 1}, policy)] == [FORBIDDEN_VALUE]

    def test_a_field_name_that_carries_a_value_is_not_echoed_in_the_report(self) -> None:
        """The name is the value here, so the report may not repeat it."""
        found = check({EMAIL: {"api_key": "x"}}, Policy())
        assert found
        rendered = " ".join(str(item) + repr(item.to_dict()) for item in found)
        assert EMAIL not in rendered
        assert "<key#0>" in rendered

    def test_a_denied_path_detail_never_echoes_an_identifier_field_name(self) -> None:
        policy = Policy(forbidden_keys=frozenset(), denied_field_paths=frozenset({"mrn"}))
        found = check({EMAIL: {"mrn": "NG-88231"}}, policy)
        rendered = " ".join(str(item) for item in found)
        assert EMAIL not in rendered
        assert "denied field '<key#0>.mrn' carries a value" in rendered

    def test_an_ordinary_field_name_is_still_named_in_the_report(self) -> None:
        found = check({"integration": {"api_key": "x"}}, Policy())
        assert [item.path for item in found] == ["response.integration.api_key"]

    def test_a_denied_path_under_an_unnamed_key_is_still_matched(self) -> None:
        """Sanitising the report may not disarm the policy: matching uses the real name."""
        policy = Policy(
            forbidden_keys=frozenset(), denied_field_paths=frozenset({"weird name.mrn"})
        )
        assert [item.code for item in check({"weird name": {"mrn": "x"}}, policy)] == [
            DENIED_FIELD_PATH
        ]


class TestOneNormalisationForEveryNameComparison:
    def test_an_uppercase_allowed_domain_still_allows_the_domain(self) -> None:
        policy = Policy(
            forbidden_keys=frozenset(), allow_domains=frozenset({"Support.ACME-Corp.example"})
        )
        assert check({"x": "a@support.acme-corp.example"}, policy) == []

    def test_the_folding_does_exactly_what_its_docstring_says(self) -> None:
        """Every example _fold's docstring gives, including the one it rules out."""
        from egresswall._core import _fold, normalize_key

        assert _fold("\u1e9e") == "ss"
        assert _fold("\u212a") == "k"
        assert _fold("\u015b") == "s"
        assert normalize_key("\uff21\uff30\uff29") == "api"
        assert _fold("\u0430") != "a"
        assert not Policy().forbids_key("\u0430pi_key")

    def test_a_unicode_confusable_in_a_field_name_does_not_disable_the_key_rule(self) -> None:
        """One folding for every name: casefold maps \u1e9e to ss, so \u1e9en is ssn."""
        assert [item.code for item in check({"\u1e9eN": 1}, Policy(detectors=frozenset()))] == [
            FORBIDDEN_KEY
        ]


def test_a_long_field_name_is_screened_but_never_cached() -> None:
    """A key is chosen by the other side, so caching it would be a memory hazard."""
    from egresswall import _core

    def cached() -> int:
        return (
            _core._normalize_cached.cache_info().currsize
            + _core._screen_key_cached.cache_info().currsize
            + _core._normalize_path_cached.cache_info().currsize
        )

    before = cached()
    huge = "x" * 200_000
    assert [item.code for item in check({huge: 1}, Policy(max_string_length=1000))] == [
        PAYLOAD_TOO_LARGE
    ]
    assert cached() == before


# --- fix pass 6 ---------------------------------------------------------------


class TestSerializedJsonInsideAString:
    """MCP carries a tool's whole payload as JSON text inside `content[].text`.

    Screened as one string, the field-name and field-path rules -- the two an
    operator configures -- never saw a field at all. A string that opens with
    `{` or `[` is screened as a document as well.
    """

    ROW: ClassVar[dict] = {
        "patient": {"mrn": "NG-88231"},
        "rows": [{"user_id": 7}],
        "api_key": "",
    }
    POLICY = Policy(denied_field_paths=frozenset({"patient.mrn"}))

    def result(self) -> dict:
        return {"content": [{"type": "text", "text": json.dumps(self.ROW, sort_keys=True)}]}

    def test_the_name_rules_fire_inside_the_serialized_payload(self) -> None:
        found = {(item.code, item.path) for item in check(self.result(), self.POLICY)}
        assert (
            DENIED_FIELD_PATH,
            "response.content[0].text→patient.mrn",
        ) in found
        assert (FORBIDDEN_KEY, "response.content[0].text→rows") in found
        assert (FORBIDDEN_KEY, "response.content[0].text→api_key") in found

    def test_a_policy_means_the_same_thing_wrapped_as_it_does_unwrapped(self) -> None:
        """The whole point of the dotted root: `patient.mrn` on every surface."""
        loose = {item.code for item in check(self.ROW, self.POLICY)}
        wrapped = {item.code for item in check(self.result(), self.POLICY)}
        assert loose == wrapped

    def test_a_benign_serialized_payload_screens_clean(self) -> None:
        clean = {"content": [{"type": "text", "text": '{"cohort_size": 25}'}]}
        assert check(clean, self.POLICY) == []

    def test_a_string_that_is_not_a_document_at_all_is_screened_as_a_string(self) -> None:
        """Prose that never opens like a document is not a candidate and is not refused."""
        payload = {"note": "this is not json, and " + EMAIL + " is in it"}
        assert [item.code for item in check(payload, OPEN)] == [RAW_IDENTIFIER]

    def test_a_string_that_opens_like_a_document_and_is_not_one_is_refused(self) -> None:
        """Fail closed: the name rules could not run, so the scalar is a violation.

        The detectors still read every character of it first, so both codes are
        reported -- the string was screened as a string and refused as a document.
        """
        payload = {"note": "{ this is not json, and " + EMAIL + " is in it"}
        assert [item.code for item in check(payload, OPEN)] == [
            RAW_IDENTIFIER,
            EMBEDDED_DOCUMENT_UNPARSEABLE,
        ]

    def test_a_serialized_document_that_spells_a_field_twice_is_refused(self) -> None:
        """Ambiguous text has not been screened, so it does not cross.

        Python keeps the last spelling; a first-wins reader keeps the other one.
        `check` and `hook` already refuse such a document at the envelope, and
        this is the same rule one level in.
        """
        text = '{"api_key": "", "api_key": ""}'
        assert [
            item.code
            for item in check({"content": [{"text": text}]}, Policy(detectors=frozenset()))
        ] == [EMBEDDED_DOCUMENT_UNPARSEABLE]

    #: The red team's repro: an honest document, and the same document with one
    #: token appended that no parser resolves the way the next one does. Every
    #: one of these used to turn `forbidden_keys` and `denied_field_paths` off
    #: for the whole payload, silently, at the server's discretion.
    HONEST: ClassVar[str] = '{"patient":{"mrn":"NG-88231"},"api_key":"s3cr3t"}'
    SWITCHES: ClassVar[dict[str, str]] = {
        "duplicate-key": '"patient":{"mrn":"clean"}',
        "over-limit-integer": '"n":' + "9" * 5000,
        "over-deep-array": '"d":' + "[" * 200_000 + "]" * 200_000,
    }

    def switched(self, name: str) -> str:
        return self.HONEST[:-1] + "," + self.SWITCHES[name] + "}"

    def test_the_honest_document_is_refused_on_both_name_rules(self) -> None:
        found = check({"content": [{"text": self.HONEST}]}, self.POLICY)
        assert {item.code for item in found} == {DENIED_FIELD_PATH, FORBIDDEN_KEY}

    @pytest.mark.parametrize("name", sorted(SWITCHES))
    def test_one_appended_token_cannot_turn_the_name_rules_off(self, name: str) -> None:
        found = check({"content": [{"text": self.switched(name)}]}, self.POLICY)
        assert [item.code for item in found] == [EMBEDDED_DOCUMENT_UNPARSEABLE], name

    @pytest.mark.parametrize("name", sorted(SWITCHES))
    def test_the_operator_can_opt_out_and_get_the_old_fail_open_walk(self, name: str) -> None:
        """One flag, documented, off by default: a policy chooses to fail open."""
        loose = Policy(
            denied_field_paths=frozenset({"patient.mrn"}), refuse_unparseable_embedded=False
        )
        assert check({"content": [{"text": self.switched(name)}]}, loose) == [], name

    def test_the_embedded_document_is_bounded_by_the_same_budget(self) -> None:
        text = json.dumps([1] * 200)
        tight = Policy(forbidden_keys=frozenset(), max_nodes=50)
        assert [item.code for item in check({"t": text}, tight)] == [PAYLOAD_TOO_LARGE]

    def test_a_string_too_long_to_screen_is_never_parsed(self) -> None:
        """Refused twice over: too long to screen as a string, never screened as a document."""
        text = json.dumps({"api_key": "x" * 5000})
        tight = Policy(max_string_length=100)
        assert [item.code for item in check({"t": text}, tight)] == [
            PAYLOAD_TOO_LARGE,
            EMBEDDED_DOCUMENT_UNPARSEABLE,
        ]


class TestGovernanceVocabulary:
    POLICY = Policy(forbidden_keys=frozenset(), denied_field_paths=frozenset({"mrn"}))

    @pytest.mark.parametrize("value", ["SMITH", "ABCDEF", "NG", "MRN"])
    def test_an_upper_cased_value_is_data_not_vocabulary(self, value: str) -> None:
        """It was `[A-Z][A-Z_]*`, so an upper-cased surname was governance vocabulary."""
        assert [item.code for item in check({"mrn": value}, self.POLICY)] == [DENIED_FIELD_PATH], (
            value
        )

    @pytest.mark.parametrize("value", sorted(DEFAULT_GOVERNANCE_TOKENS))
    def test_every_default_governance_word_passes(self, value: str) -> None:
        assert check({"mrn": value}, self.POLICY) == [], value

    def test_allow_tokens_is_the_only_way_to_widen_the_list(self) -> None:
        widened = Policy(
            forbidden_keys=frozenset(),
            denied_field_paths=frozenset({"mrn"}),
            allow_tokens=frozenset({"SMITH"}),
        )
        assert check({"mrn": "SMITH"}, widened) == []


def test_a_denied_field_path_longer_than_the_cap_is_refused() -> None:
    """Unbounded, one long entry buys back the per-node path cost the walk bounds."""
    with pytest.raises(ValueError, match="denied_field_paths entry holds at most"):
        Policy(denied_field_paths=frozenset({"z" * (MAX_DENIED_PATH_CHARS + 1)}))
    Policy(denied_field_paths=frozenset({"z" * MAX_DENIED_PATH_CHARS}))


# --- fix pass 8: a document behind an invisible character ---------------------

#: Every code point the red team could hide a serialized document behind: the
#: byte-order mark, the zero-width and bidi format characters, a soft hyphen,
#: a combining grapheme joiner, a Mongolian vowel separator, the word joiner
#: and the four invisible operators, ASCII whitespace, the non-breaking, line
#: and paragraph separators, and three shapes of combining mark. Every one of
#: them is Unicode category C, Z or M -- and `\s`, the test the candidate check
#: used to use, covers only part of that set, so prefixing a payload with one
#: turned `forbidden_keys` and `denied_field_paths` off for the whole of it
#: with nothing reported and nothing logged.
INVISIBLE_PREFIXES = [
    chr(0xFEFF),  # byte-order mark
    *[chr(point) for point in range(0x200B, 0x2010)],  # ZWSP, ZWNJ, ZWJ, LRM, RLM
    *[chr(point) for point in range(0x2060, 0x2065)],  # word joiner, invisible operators
    chr(0x00AD),  # soft hyphen
    chr(0x034F),  # combining grapheme joiner
    chr(0x180E),  # Mongolian vowel separator
    "\t",
    "\n",
    "\r",
    "\v",
    "\f",
    "\x00",
    " ",
    chr(0x00A0),  # no-break space
    chr(0x2003),  # em space
    chr(0x2028),  # line separator
    chr(0x2029),  # paragraph separator
    chr(0x3000),  # ideographic space
    chr(0x061C),  # Arabic letter mark
    *[chr(point) for point in range(0x202A, 0x202F)],  # LRE, RLE, PDF, LRO, RLO
    *[chr(point) for point in range(0x2066, 0x206A)],  # LRI, RLI, FSI, PDI
    chr(0x0301),  # combining acute accent (Mn)
    chr(0x0489),  # combining cyrillic millions sign (Me)
    chr(0x0903),  # devanagari sign visarga (Mc)
    chr(0xFEFF) + chr(0x200B) + "\t" + chr(0x202E),  # a run of them, which is what is sent
]


class TestADocumentBehindAnInvisibleCharacter:
    """The round-7 fail-closed walk was reachable again one level up.

    The candidate test was `\\s*[{\\[]`, so one U+FEFF in front of the
    serialized document meant the string was never a candidate: `_walk_embedded`
    was never called, the two rules an operator configures never ran, and the
    message was forwarded whole with nothing on stderr. The candidate test and
    `json.loads` both run on the text stripped of category C, Z and M code
    points at either end now, so the document behind the prefix is screened as
    a document.
    """

    #: The red team's exact repro, and the policy it used: the package's own
    #: `demo/policy.json` denies `patient.mrn`.
    HONEST: ClassVar[str] = '{"patient":{"mrn":"NG-88231"},"api_key":"s3cr3t"}'
    POLICY = Policy(denied_field_paths=frozenset({"patient.mrn"}))

    def wrapped(self, text: str) -> dict:
        return {"content": [{"type": "text", "text": text}]}

    def test_every_generated_prefix_is_a_category_the_fix_strips(self) -> None:
        """The list is the class, not a handful of literals someone remembered."""
        import unicodedata

        assert len(INVISIBLE_PREFIXES) >= 30
        for prefix in INVISIBLE_PREFIXES:
            for char in prefix:
                assert unicodedata.category(char)[0] in "CZM", (hex(ord(char)),)

    def test_the_repro_document_is_refused_on_both_name_rules(self) -> None:
        found = check(self.wrapped(self.HONEST), self.POLICY)
        assert {item.code for item in found} == {DENIED_FIELD_PATH, FORBIDDEN_KEY}

    @pytest.mark.parametrize("prefix", INVISIBLE_PREFIXES)
    def test_a_leading_invisible_character_cannot_turn_the_name_rules_off(
        self, prefix: str
    ) -> None:
        found = check(self.wrapped(prefix + self.HONEST), self.POLICY)
        assert {item.code for item in found} == {DENIED_FIELD_PATH, FORBIDDEN_KEY}, hex(
            ord(prefix[0])
        )

    @pytest.mark.parametrize("prefix", INVISIBLE_PREFIXES)
    def test_a_trailing_invisible_character_cannot_turn_the_name_rules_off(
        self, prefix: str
    ) -> None:
        found = check(self.wrapped(self.HONEST + prefix), self.POLICY)
        assert {item.code for item in found} == {DENIED_FIELD_PATH, FORBIDDEN_KEY}, hex(
            ord(prefix[0])
        )

    @pytest.mark.parametrize("prefix", INVISIBLE_PREFIXES)
    def test_an_invisible_character_at_both_ends_cannot_turn_the_name_rules_off(
        self, prefix: str
    ) -> None:
        found = check(self.wrapped(prefix + self.HONEST + prefix), self.POLICY)
        assert {item.code for item in found} == {DENIED_FIELD_PATH, FORBIDDEN_KEY}, hex(
            ord(prefix[0])
        )

    @pytest.mark.parametrize("prefix", INVISIBLE_PREFIXES)
    def test_a_prefix_does_not_reopen_the_fail_open_walk_either(self, prefix: str) -> None:
        """A candidate behind a prefix that will not parse is still refused."""
        broken = self.HONEST[:-1] + ',"patient":{"mrn":"clean"}}'
        found = check(self.wrapped(prefix + broken), self.POLICY)
        assert [item.code for item in found] == [EMBEDDED_DOCUMENT_UNPARSEABLE], hex(ord(prefix[0]))

    def test_a_printable_prologue_is_not_a_candidate_and_the_readme_says_so(self) -> None:
        """The boundary of the fix, stated where a reader can find it.

        Stripping is defined on invisible code points. A document behind a
        printable prologue -- XSSI's `)]}'`, a log prefix -- is not a candidate
        and is screened as a string only, which is what any other prose is.
        """
        found = check(self.wrapped(")]}'\n" + self.HONEST), self.POLICY)
        assert found == []

    def test_stripping_the_whole_text_budget_stays_inside_the_timing_bound(self) -> None:
        """The strip is a Python loop, so its worst case is measured, not assumed.

        A payload whose every character is a leading zero-width space is the
        most stripping `max_total_length` can buy, and it is refused for its
        size like any other payload that large.
        """
        import time

        document = '{"x": 1}'
        pad = chr(0x200B) * (1024 * 1024 - len(document))
        payload = {"a": pad + document, "b": chr(0x200B) * (1024 * 1024)}
        started = time.monotonic()
        found = check(payload, Policy(forbidden_keys=frozenset()))
        assert time.monotonic() - started < 1.0
        assert [item.code for item in found] == [PAYLOAD_TOO_LARGE]


class TestATemplateStringUnderTheDefaultPolicy:
    """The documented cost of the fail-closed default, pinned in both modes.

    A candidate is any string that opens with `{` or `[`, so a template string
    is a candidate that does not parse and is refused. That is the design
    decision, not an accident: the alternative -- deciding a candidate is only
    a string that also *ends* in the matching bracket -- hands the untrusted
    side a one-character way to make a document stop being one. The README says
    so under "What it catches" and under "What it does not do", with the flag.
    """

    TEMPLATES: ClassVar[list[str]] = [
        "{{name}}",
        "{{ order.total }} is substituted at render time",
        "[INFO] 2026-08-30 09:14:02 request handled in 12ms",
        "[see the runbook](https://example.com/runbook) for the rollback steps",
        "{'status': 'ok', 'rows': 0}",
    ]

    @pytest.mark.parametrize("text", TEMPLATES)
    def test_a_template_string_is_refused_by_default(self, text: str) -> None:
        assert [item.code for item in check({"note": text}, OPEN)] == [
            EMBEDDED_DOCUMENT_UNPARSEABLE
        ], text

    @pytest.mark.parametrize("text", TEMPLATES)
    def test_the_documented_flag_is_the_opt_out_for_exactly_that(self, text: str) -> None:
        loose = Policy(forbidden_keys=frozenset(), refuse_unparseable_embedded=False)
        assert check({"note": text}, loose) == [], text


# --- fix pass 9: blank where the categories are not ---------------------------

#: The code points the round-9 red team hid a serialized document behind. Each
#: renders as nothing or as blank width, and not one of them is Unicode general
#: category C, Z or M -- so the round-8 fix, which stripped exactly those
#: categories, forwarded a `content[].text` payload prefixed with one of them
#: with `forbidden_keys` and `denied_field_paths` never run, nothing reported
#: and nothing logged. Four are Hangul fillers, category Lo, and are in
#: Unicode's `Default_Ignorable_Code_Point` set; the other two are category So
#: and are drawn blank by every font that has them.
BLANK_OUTSIDE_THE_CATEGORIES = [
    "ᅟ",  # HANGUL CHOSEONG FILLER (Lo, Default_Ignorable)
    "ᅠ",  # HANGUL JUNGSEONG FILLER (Lo, Default_Ignorable)
    "ㅤ",  # HANGUL FILLER (Lo, Default_Ignorable)
    "ﾠ",  # HALFWIDTH HANGUL FILLER (Lo, Default_Ignorable)
    "⠀",  # BRAILLE PATTERN BLANK (So)
    "\U0001d159",  # MUSICAL SYMBOL NULL NOTEHEAD (So)
]

#: `DerivedCoreProperties.txt`, the `# Default_Ignorable_Code_Point` block,
#: transcribed a second time here -- line by line, unmerged, as the file writes
#: it -- from https://www.unicode.org/Public/15.1.0/ucd/DerivedCoreProperties.txt.
#: `_core._DEFAULT_IGNORABLE` is the same data written as a regex with adjacent
#: lines merged, and the test below asserts the two agree code point for code
#: point, so a typo in either transcription fails rather than ships.
DEFAULT_IGNORABLE_LINES = [
    (0x00AD, 0x00AD),
    (0x034F, 0x034F),
    (0x061C, 0x061C),
    (0x115F, 0x1160),
    (0x17B4, 0x17B5),
    (0x180B, 0x180D),
    (0x180E, 0x180E),
    (0x180F, 0x180F),
    (0x200B, 0x200F),
    (0x202A, 0x202E),
    (0x2060, 0x2064),
    (0x2065, 0x2065),
    (0x2066, 0x206F),
    (0x3164, 0x3164),
    (0xFE00, 0xFE0F),
    (0xFEFF, 0xFEFF),
    (0xFFA0, 0xFFA0),
    (0xFFF0, 0xFFF8),
    (0x1BCA0, 0x1BCA3),
    (0x1D173, 0x1D17A),
    (0xE0000, 0xE0000),
    (0xE0001, 0xE0001),
    (0xE0002, 0xE001F),
    (0xE0020, 0xE007F),
    (0xE0080, 0xE00FF),
    (0xE0100, 0xE01EF),
    (0xE01F0, 0xE0FFF),
]


class TestBlankCodePointsOutsideTheCategories:
    """The round-8 bypass, re-opened by anything invisible that C/Z/M misses.

    Stripping category C, Z and M covers 966,938 code points and still leaves a
    Hangul filler, a Braille blank and a musical null notehead in front of a
    document a reader sees unchanged. The strip set is now those categories
    plus every `Default_Ignorable_Code_Point` plus the two blank-by-glyph code
    points, and the `{`/`[` test and the parse both run behind it.
    """

    HONEST: ClassVar[str] = '{"patient":{"mrn":"NG-88231"},"api_key":"s3cr3t"}'
    POLICY = Policy(denied_field_paths=frozenset({"patient.mrn"}))

    def wrapped(self, text: str) -> dict:
        return {"content": [{"type": "text", "text": text}]}

    def stripped_set(self) -> list[int]:
        from egresswall._core import _BLANK_BY_GLYPH, _DEFAULT_IGNORABLE

        return sorted(
            {point for point in range(0x110000) if _DEFAULT_IGNORABLE.match(chr(point))}
            | {ord(char) for char in _BLANK_BY_GLYPH}
        )

    def test_none_of_the_red_teams_code_points_is_a_category_the_round_8_fix_stripped(
        self,
    ) -> None:
        """The premise of the finding: the old rule could not have caught these."""
        import unicodedata

        for char in BLANK_OUTSIDE_THE_CATEGORIES:
            assert unicodedata.category(char)[0] not in "CZM", hex(ord(char))

    def test_the_regex_is_the_property_it_says_it_transcribes(self) -> None:
        """Two independent transcriptions of one Unicode data file, compared."""
        from egresswall._core import _DEFAULT_IGNORABLE

        expected = {
            point for first, last in DEFAULT_IGNORABLE_LINES for point in range(first, last + 1)
        }
        matched = {point for point in range(0x110000) if _DEFAULT_IGNORABLE.match(chr(point))}
        assert matched == expected, sorted(hex(point) for point in matched ^ expected)
        assert len(expected) == 4174

    def test_the_only_default_ignorables_outside_czm_are_the_four_hangul_fillers(self) -> None:
        """Why the property is stripped and not just the categories, measured."""
        import unicodedata

        from egresswall._core import _DEFAULT_IGNORABLE

        outside = {
            point
            for point in range(0x110000)
            if _DEFAULT_IGNORABLE.match(chr(point))
            and unicodedata.category(chr(point))[0] not in "CZM"
        }
        assert outside == {0x115F, 0x1160, 0x3164, 0xFFA0}

    @pytest.mark.parametrize("blank", BLANK_OUTSIDE_THE_CATEGORIES)
    def test_a_leading_blank_code_point_cannot_turn_the_name_rules_off(self, blank: str) -> None:
        found = check(self.wrapped(blank + self.HONEST), self.POLICY)
        assert {item.code for item in found} == {DENIED_FIELD_PATH, FORBIDDEN_KEY}, hex(ord(blank))

    @pytest.mark.parametrize("blank", BLANK_OUTSIDE_THE_CATEGORIES)
    def test_a_trailing_blank_code_point_cannot_turn_the_name_rules_off(self, blank: str) -> None:
        found = check(self.wrapped(self.HONEST + blank), self.POLICY)
        assert {item.code for item in found} == {DENIED_FIELD_PATH, FORBIDDEN_KEY}, hex(ord(blank))

    def test_every_code_point_in_the_stripped_set_is_stripped_at_both_ends(self) -> None:
        """The sweep, not a handful of literals: all 4176 of them, each end.

        One `check` per code point per end is the whole point -- the bypass was
        a candidate test that ran before the strip, so only running the screen
        proves the strip is where it has to be.
        """
        points = self.stripped_set()
        assert len(points) == 4176
        expected = {DENIED_FIELD_PATH, FORBIDDEN_KEY}
        for point in points:
            blank = chr(point)
            for text in (blank + self.HONEST, self.HONEST + blank, blank + self.HONEST + blank):
                found = check(self.wrapped(text), self.POLICY)
                assert {item.code for item in found} == expected, hex(point)

    def test_a_blank_code_point_does_not_reopen_the_fail_open_walk_either(self) -> None:
        """A candidate behind a blank prefix that will not parse is still refused."""
        broken = self.HONEST[:-1] + ',"patient":{"mrn":"clean"}}'
        for blank in BLANK_OUTSIDE_THE_CATEGORIES:
            found = check(self.wrapped(blank + broken), self.POLICY)
            assert [item.code for item in found] == [EMBEDDED_DOCUMENT_UNPARSEABLE], hex(ord(blank))

    def test_stripping_the_wider_set_stays_inside_the_timing_bound(self) -> None:
        """The strip is still a Python loop and the widest set is still measured."""
        import time

        document = '{"x": 1}'
        pad = "ㅤ" * (1024 * 1024 - len(document))
        payload = {"a": pad + document, "b": "ㅤ" * (1024 * 1024)}
        started = time.monotonic()
        found = check(payload, Policy(forbidden_keys=frozenset()))
        assert time.monotonic() - started < 2.0
        assert [item.code for item in found] == [PAYLOAD_TOO_LARGE]


# --- fix pass 9: the dotted path is pruned on the normalized length -----------


class TestADeniedPathBehindAnInflatedParentName:
    """`_extend_path` measured the raw name against a normalized limit.

    `denied_field_paths` are matched with case and separators removed on both
    sides, but the walk stopped building the path when the *raw* name was
    longer than the longest denied entry -- so a parent whose separators padded
    it past that length dropped the path and the match never ran. It failed
    open on a name the other side of the boundary chooses.
    """

    POLICY = Policy(forbidden_keys=frozenset(), denied_field_paths=frozenset({"patient.mrn"}))

    def test_the_unpadded_spelling_matches(self) -> None:
        found = check({"patient": {"mrn": "NG-88231"}}, self.POLICY)
        assert [item.code for item in found] == [DENIED_FIELD_PATH]

    @pytest.mark.parametrize("padding", ["____", "_" * 64, "-" * 500, " # " * 40, ". .-_" * 20])
    def test_separators_that_inflate_the_parent_name_do_not_defeat_the_match(
        self, padding: str
    ) -> None:
        name = f"{padding}patient{padding}"
        assert len(name) > len("patient.mrn")
        found = check({name: {"mrn": "NG-88231"}}, self.POLICY)
        assert [item.code for item in found] == [DENIED_FIELD_PATH], name

    @pytest.mark.parametrize(
        "name", ["patient.", ".patient", "patient..", "patient._", "..patient."]
    )
    def test_a_segment_that_is_only_separators_is_no_segment(self, name: str) -> None:
        """The same fail-open one character wide: a trailing dot used to build
        `patient..mrn`, which equals no entry an operator would write."""
        found = check({name: {"mrn": "NG-88231"}}, self.POLICY)
        assert [item.code for item in found] == [DENIED_FIELD_PATH], name

    def test_the_flattened_spelling_still_matches_the_same_entry(self) -> None:
        """ "." stays the segment boundary: a server that flattens its payload is
        screened by the entry the nested spelling is screened by."""
        found = check({"patient.mrn": "NG-88231"}, self.POLICY)
        assert [item.code for item in found] == [DENIED_FIELD_PATH]

        for width in (129, 257):
            padding = "_" * width
            name = f"{padding}patient{padding}.{padding}mrn{padding}"
            found = check({name: "NG-88231"}, self.POLICY)
            assert [item.code for item in found] == [DENIED_FIELD_PATH], width

    def test_the_bound_still_prunes_on_a_genuinely_longer_path(self) -> None:
        """The limit is a real bound, not one the fix removed: a normalized path
        longer than the longest denied entry cannot equal one, and is dropped."""
        from egresswall._core import _PATH_TOO_LONG, _extend_path

        assert _extend_path("", "_" * 40 + "patient", 11) == "patient"
        assert _extend_path("", "p" * 12, 11) == _PATH_TOO_LONG
        assert _extend_path(_PATH_TOO_LONG, "patient", 11) == _PATH_TOO_LONG
        assert check({"p" * 12: {"mrn": "NG-88231"}}, self.POLICY) == []
