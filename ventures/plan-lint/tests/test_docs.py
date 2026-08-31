"""docs/schema.md and docs/porting-notes.md are checked against the models."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from agent_plan_lint import (
    ISSUE_CODES,
    ArtifactContract,
    ArtifactRequirement,
    CommandTemplate,
    Criterion,
    NetworkPolicy,
    Plan,
    ProjectPolicy,
    ResourceBudget,
    Task,
    load_plan,
    load_policy,
    validate_plan,
)
from agent_plan_lint.globs import MAX_PATH_SEGMENTS, MAX_POLICY_WILDCARDS
from agent_plan_lint.loading import MAX_DOCUMENT_BYTES
from agent_plan_lint.models import MAX_PLAN_PATHS, MAX_POLICY_GLOBS

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DOC = (ROOT / "docs" / "schema.md").read_text(encoding="utf-8")
CHANGELOG = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
PORTING_DOC = (ROOT / "docs" / "porting-notes.md").read_text(encoding="utf-8")
MODELS = (
    ArtifactContract,
    ArtifactRequirement,
    CommandTemplate,
    Criterion,
    NetworkPolicy,
    Plan,
    ProjectPolicy,
    ResourceBudget,
    Task,
)
DOCUMENTED = set(re.findall(r"^\| `([a-z_]+)` \|", SCHEMA_DOC, re.M))


@pytest.mark.parametrize("model", MODELS, ids=lambda model: model.__name__)
def test_every_field_of_every_document_model_is_documented(model) -> None:
    assert set(model.model_fields) <= DOCUMENTED


def test_the_schema_doc_documents_no_field_that_does_not_exist() -> None:
    real = {name for model in MODELS for name in model.model_fields}

    assert real >= DOCUMENTED


def test_the_minimal_example_in_the_schema_doc_is_valid() -> None:
    examples = re.findall(r"^```json$(.*?)^```$", SCHEMA_DOC, re.M | re.S)

    assert len(examples) == 2
    policy, plan = (json.loads(example) for example in examples)
    result = validate_plan(load_policy(policy), load_plan(plan))

    assert result.valid, [issue.code for issue in result.issues]
    assert result.topological_order == ("edit", "assemble", "verify")


def test_the_porting_notes_match_what_was_actually_dropped_and_added() -> None:
    assert "legacy_adapter_unavailable" in PORTING_DOC
    assert "legacy_adapter_unavailable" not in ISSUE_CODES
    assert "evidence_adapter" not in Task.model_fields
    assert "retention" not in ProjectPolicy.model_fields
    assert "criterion_human_gate" in PORTING_DOC
    assert "criterion_human_gate" in ISSUE_CODES


def _bound(model, field: str, attribute: str):
    """One `Field` constraint, read off the model rather than restated here."""

    for item in model.model_fields[field].metadata:
        if hasattr(item, attribute):
            return getattr(item, attribute)
    raise AssertionError(f"{model.__name__}.{field} has no {attribute}")


def test_the_schema_doc_states_the_bounds_the_models_enforce() -> None:
    """Every number on the schema page, read off the code it describes."""

    assert f"at most {MAX_PATH_SEGMENTS} slash-separated components" in SCHEMA_DOC
    assert f"At most {MAX_PATH_SEGMENTS} slash-separated segments each" in SCHEMA_DOC
    assert f"may name at most {MAX_PLAN_PATHS} paths" in SCHEMA_DOC
    for field in ("allowed_read_globs", "allowed_write_globs", "exclusions", "command_templates"):
        assert _bound(ProjectPolicy, field, "max_length") == MAX_POLICY_GLOBS
    assert SCHEMA_DOC.count(f"at most {MAX_POLICY_GLOBS} of them") == 4
    assert f"at most {MAX_POLICY_GLOBS} of them; a task can only name one" in SCHEMA_DOC
    assert f"nor `*` nor `**` | {MAX_POLICY_WILDCARDS} |" in SCHEMA_DOC
    assert f"| Bytes read from one document | {MAX_DOCUMENT_BYTES} |" in SCHEMA_DOC
    assert f"| Segments in one path or components in one pattern | {MAX_PATH_SEGMENTS} |" in SCHEMA_DOC
    assert f"| Globs in each of a policy's three path lists | {MAX_POLICY_GLOBS} |" in SCHEMA_DOC
    assert f"| Paths one plan may name in total | {MAX_PLAN_PATHS} |" in SCHEMA_DOC


def test_the_schema_doc_states_the_field_ranges_the_models_enforce() -> None:
    """The ranges the tables print, each read off the `Field` that enforces it."""

    assert f"1 to {_bound(CommandTemplate, 'timeout_seconds', 'le')} seconds" in SCHEMA_DOC
    assert f"{_bound(Plan, 'tasks', 'min_length')} to {_bound(Plan, 'tasks', 'max_length')} tasks" in SCHEMA_DOC
    assert f"1 to {_bound(Task, 'attempt_limit', 'le')}, and at most the policy" in SCHEMA_DOC
    assert f"{_bound(Task, 'priority', 'ge')} to {_bound(Task, 'priority', 'le')}; scheduling hint" in SCHEMA_DOC
    digits = int(re.search(r"\{(\d+)\}\$$", ProjectPolicy.model_fields["base_sha"].metadata[0].pattern).group(1))
    assert f"The exact {digits}-character commit" in SCHEMA_DOC


def test_the_schema_doc_states_the_report_bounds_the_validator_enforces() -> None:
    """The report is bounded too, and the page says by how much."""

    from agent_plan_lint.validation import _DETAIL_LIMIT, _ISSUES_PER_CODE, _LISTING_LIMIT

    assert f"at most {_ISSUES_PER_CODE}\nfindings are listed per issue code" in SCHEMA_DOC
    assert f"names at most {_LISTING_LIMIT} items and is truncated to {_DETAIL_LIMIT} characters" in SCHEMA_DOC
    # docs/porting-notes.md restates all three in one bullet.
    flat = " ".join(PORTING_DOC.split())
    assert f"An issue detail names at most {_LISTING_LIMIT} ids and is truncated to the {_DETAIL_LIMIT}" in flat
    assert f"at most {_ISSUES_PER_CODE} findings are listed per issue code" in flat


def test_the_schema_doc_states_the_credential_thresholds_the_models_enforce() -> None:
    from agent_plan_lint.models import (
        _PROVIDER_KEY,
        _RUN_SEPARATOR,
        MIN_BEARER_CHARACTERS,
        MIN_TOKEN_CHARACTERS,
        MIN_TOKEN_DIGITS,
        _high_entropy,
    )

    # What breaks a run is the difference between refusing a key and refusing a
    # branch name, so the page names the separators the code splits on.
    separators = _RUN_SEPARATOR.pattern.strip("[]")
    assert set(separators) == {"/", "_", "-"}
    spelled = ", by ".join(f"`{character}`" for character in separators[:-1])
    assert f"A run is broken by {spelled} and by `{separators[-1]}` before it is measured" in SCHEMA_DOC
    assert not _high_entropy("Merge branch feature/AB-1234-refactor-user-profile-service")
    assert not _high_entropy("run_MigrationV2_2024_backfill_Step3_final")
    # The limit the same paragraph states: no separator at all and it is refused.
    assert _high_entropy("FeatureFlagRolloutStage2Cohort3Batch4")
    assert "Break such a\nname with `/`, `_` or `-` and it loads." in SCHEMA_DOC
    # The shape a user actually hits: a long CamelCase class name with a year in
    # it crosses the same threshold, and the page has to say so where the ceiling
    # is stated rather than leave it to be discovered in CI.
    assert "`CheckoutSessionTokenRefresher2026Service`" in SCHEMA_DOC
    assert _high_entropy("Refactor CheckoutSessionTokenRefresher2026Service into two classes.")

    # Every prefix the table lists is a prefix the expression actually matches.
    # `xox-` was in the table and is not one: the Slack family needs the letter.
    row = re.search(r"^\| A provider key prefix \|(.+)\|$", SCHEMA_DOC, re.M)

    assert row is not None, "the schema doc no longer has a provider-key row"
    prefixes = re.findall(r"`([^`]+)`", row.group(1))
    assert prefixes
    for prefix in prefixes:
        assert _PROVIDER_KEY.search(f"{prefix}A1B2C3D4E5F6G7H8I9J0K1L2"), prefix
    assert not _PROVIDER_KEY.search("xox-A1B2C3D4E5F6G7H8I9J0K1L2")

    # The assigned-value shape has its own floor, and the same two constants set it.
    assert (
        f"a provider key prefix, a PEM header, or {MIN_TOKEN_CHARACTERS} characters or more "
        f"mixing case with at least {MIN_TOKEN_DIGITS} digits"
    ) in " ".join(SCHEMA_DOC.split())
    assert f"A bearer token of {MIN_BEARER_CHARACTERS} characters or more" in SCHEMA_DOC
    assert (
        f"{MIN_TOKEN_CHARACTERS} characters or more, unbroken, with upper case, "
        f"lower case and at least {MIN_TOKEN_DIGITS} digits"
    ) in SCHEMA_DOC


def test_the_schema_doc_lists_the_shell_basenames_the_models_refuse() -> None:
    """A table of names in prose drifts the first time a name is added to the code."""

    from agent_plan_lint.models import _SHELL_COMMANDS

    row = re.search(r"^\| `argv` \|(.+)$", SCHEMA_DOC, re.M)

    assert row is not None, "the schema doc no longer has an `argv` row"
    assert sorted(re.findall(r"`([a-z]+)`", row.group(1).split("--")[1])) == sorted(_SHELL_COMMANDS)


def test_the_docs_truth_job_runs_the_test_that_reproduces_the_published_transcript() -> None:
    """`demo/OUTPUT.txt` is a page of output; the docs-truth job has to cover it."""

    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "tests/test_cli.py::test_demo_script_reproduces_the_captured_output" in workflow


def test_the_schema_doc_describes_the_case_folding_switch_the_policy_has() -> None:
    assert "case_sensitive_paths" in ProjectPolicy.model_fields
    assert ProjectPolicy.model_fields["case_sensitive_paths"].default is False
    assert "`false` (the default) compares every path" in SCHEMA_DOC


def accepted_prose_examples() -> list[str]:
    """The quoted task titles the schema page promises the validator still accepts."""

    paragraph = re.search(r"^Prose is not a shape.*?\n\n", SCHEMA_DOC, re.M | re.S)

    assert paragraph is not None, "the schema doc has no accepted-prose paragraph"
    return re.findall(r'"([^"\n]{12,})"', " ".join(paragraph.group().split()))


def test_every_accepted_prose_example_is_a_sentence_the_validator_test_accepts() -> None:
    """The page says `tests/test_validation.py` holds these sentences; this is that check."""

    source = " ".join((ROOT / "tests" / "test_validation.py").read_text(encoding="utf-8").replace("`", "").split())
    examples = accepted_prose_examples()

    assert len(examples) >= 5
    assert "`tests/test_validation.py` holds every one of those sentences" in " ".join(SCHEMA_DOC.split())
    for example in examples:
        assert " ".join(example.replace("`", "").split()) in source, example


def test_no_number_in_the_prose_of_the_schema_doc_is_unaccounted_for() -> None:
    """The README's sweep, applied to the page that states the bounds themselves.

    Every number here comes off a model bound, a validator constant, or a quoted
    example sentence that `tests/test_validation.py` also holds -- so a new number
    cannot arrive without a reviewer putting it somewhere the code can move it.
    """

    from agent_plan_lint.models import (
        BLANK_BY_GLYPH,
        MIN_BEARER_CHARACTERS,
        MIN_TOKEN_CHARACTERS,
        MIN_TOKEN_DIGITS,
    )
    from agent_plan_lint.validation import _DETAIL_LIMIT, _ISSUES_PER_CODE, _LISTING_LIMIT
    from test_readme_truth import numbers_in, page_prose

    digits = re.search(r"\{(\d+)\}\$$", ProjectPolicy.model_fields["base_sha"].metadata[0].pattern).group(1)
    accounted = {
        str(value)
        for value in (
            MAX_PATH_SEGMENTS,
            MAX_POLICY_GLOBS,
            MAX_POLICY_WILDCARDS,
            MAX_PLAN_PATHS,
            MAX_DOCUMENT_BYTES,
            MIN_BEARER_CHARACTERS,
            MIN_TOKEN_CHARACTERS,
            MIN_TOKEN_DIGITS,
            _DETAIL_LIMIT,
            _ISSUES_PER_CODE,
            _LISTING_LIMIT,
            digits,
            _bound(CommandTemplate, "timeout_seconds", "le"),
            _bound(Plan, "tasks", "min_length"),
            _bound(Plan, "tasks", "max_length"),
            _bound(Task, "attempt_limit", "le"),
            abs(_bound(Task, "priority", "ge")),
            _bound(Task, "priority", "le"),
            # The two `schema_version` values the page documents.
            1,
            2,
            # `attempt_count` is `0` in a new plan; the page states the default.
            Task.model_fields["attempt_count"].default,
        )
    }
    accounted |= {number for example in accepted_prose_examples() for number in numbers_in(example)}
    # The one code point the page spells in digits, read off the constant that
    # refuses it rather than typed into the page by hand.
    accounted |= {f"{ord(BLANK_BY_GLYPH):04X}"}
    unaccounted = sorted(numbers_in(page_prose("docs/schema.md")) - accounted)

    assert unaccounted == [], f"docs/schema.md states numbers nothing accounts for: {unaccounted}"


def test_the_changelog_states_the_bounds_and_the_budget_the_tests_enforce() -> None:
    """Every number the changelog prints; each moves if the code or the test moves."""

    from agent_plan_lint.models import MIN_TOKEN_CHARACTERS, MIN_TOKEN_DIGITS
    from agent_plan_lint.validation import _ISSUES_PER_CODE
    from test_performance import BUDGET_SECONDS

    flat = " ".join(CHANGELOG.split())

    assert (
        f"it runs to {MIN_TOKEN_CHARACTERS} characters or more mixing case and "
        f"carrying at least {MIN_TOKEN_DIGITS} digits"
    ) in flat

    assert f"at most {MAX_PATH_SEGMENTS} slash-separated segments" in flat
    assert f"at most {MAX_POLICY_GLOBS} globs in each of a policy's three path lists" in flat
    assert f"at most {MAX_POLICY_WILDCARDS} distinct wildcard path components" in flat
    assert f"at most {MAX_PLAN_PATHS} paths named by one plan" in flat
    assert f"at {_ISSUES_PER_CODE} findings per issue code" in flat
    assert BUDGET_SECONDS == 2.0
    assert "to a two-second budget" in flat
    assert f"{len(ISSUE_CODES)} typed issue codes" in flat
