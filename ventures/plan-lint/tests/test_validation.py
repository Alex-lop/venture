"""The validation suite ported from Graphene's tests/unit/orchestration/test_validation.py."""

from __future__ import annotations

import ast
import unicodedata
from pathlib import Path

import pytest
from pydantic import ValidationError

import agent_plan_lint
from agent_plan_lint import (
    ISSUE_CODES,
    ArtifactContract,
    ArtifactRequirement,
    AuthorizationMode,
    CommandTemplate,
    CriterionVerificationKind,
    FinalizationMode,
    Plan,
    PlanValidationError,
    ProjectPolicy,
    Task,
    TaskKind,
    canonical_json_sha256,
    evaluate_plan_policy,
    require_valid_plan,
    validate_plan,
)
from conftest import plan as _plan
from conftest import policy as _policy
from conftest import replace, replace_criterion
from conftest import task as _task


def codes(*arguments: object, **keywords: object) -> set[str]:
    return {item.code for item in validate_plan(*arguments, **keywords).issues}


def test_valid_plan_is_pure_deterministic_and_topological() -> None:
    policy, plan = _policy(), _plan()
    before = canonical_json_sha256(plan.model_dump(mode="json"))

    first = validate_plan(policy, plan)
    second = require_valid_plan(policy, plan)

    assert first == second
    assert first.valid
    assert first.topological_order == ("work-a", "work-b", "assemble", "verify")
    assert canonical_json_sha256(plan.model_dump(mode="json")) == before


@pytest.mark.parametrize(
    ("changed", "code"),
    (
        (
            lambda plan: replace(plan, "assemble", dependencies=("ghost", "work-a", "work-b")),
            "missing_dependency",
        ),
        (
            lambda plan: replace(
                plan,
                "assemble",
                inputs=(
                    ArtifactRequirement(producer_task_id="work-a", name="wrong", kind="patch"),
                    ArtifactRequirement(producer_task_id="work-b", name="patch-b", kind="patch"),
                ),
            ),
            "missing_artifact_contract",
        ),
        (
            lambda plan: replace(
                plan,
                "work-b",
                write_paths=("app/a.py",),
                expected_outputs=(ArtifactContract(name="patch-b", kind="patch", paths=("app/a.py",)),),
            ),
            "parallel_write_conflict",
        ),
    ),
)
def test_plan_validator_reports_structured_failures(changed, code: str) -> None:
    result = validate_plan(_policy(), changed(_plan()))

    assert not result.valid
    assert code in {item.code for item in result.issues}
    with pytest.raises(PlanValidationError):
        require_valid_plan(_policy(), changed(_plan()))


def test_plan_validator_rejects_cycles() -> None:
    cyclic = replace(
        _plan(),
        "work-a",
        dependencies=("verify",),
        inputs=(ArtifactRequirement(producer_task_id="verify", name="verification", kind="test-receipt"),),
    )

    result = validate_plan(_policy(), cyclic)

    assert not result.valid
    assert result.topological_order == ()
    assert "cycle" in {item.code for item in result.issues}


def test_plan_rejects_checks_the_completion_receipt_cannot_prove() -> None:
    plan = replace(_plan(), "work-a", acceptance_checks=("check", "edit"))

    assert "acceptance_check_count_unsupported" in codes(_policy(), plan)


def test_write_leases_are_exact_and_policy_globs_use_full_path_matching() -> None:
    with pytest.raises(ValidationError, match="must be exact"):
        Task.model_validate(
            {
                **_plan().tasks[-1].model_dump(mode="json"),
                "write_paths": ("app/**",),
                "expected_outputs": (ArtifactContract(name="patch-a", kind="patch", paths=("app/**",)),),
            }
        )

    policy = ProjectPolicy.model_validate(
        {
            **_policy().model_dump(mode="json"),
            "allowed_write_globs": ("app/*", "out/**", "tests/**"),
        }
    )
    nested = replace(
        _plan(),
        "work-a",
        write_paths=("app/nested/a.py",),
        expected_outputs=(ArtifactContract(name="patch-a", kind="patch", paths=("app/nested/a.py",)),),
    )

    assert "write_path_not_allowed" in codes(policy, nested)


def test_a_wildcard_read_scope_must_be_provably_inside_a_granted_glob() -> None:
    """A scope narrower than the grant is allowed; one the grant cannot cover is not."""

    narrow_policy = ProjectPolicy.model_validate(
        {
            **_policy().model_dump(mode="json"),
            "allowed_read_globs": ("app/*", "out/**", "tests/**"),
        }
    )
    broad_read = replace(_plan(), "work-a", read_paths=("app/**",))

    assert "read_path_not_allowed" in codes(narrow_policy, broad_read)
    assert "read_path_not_allowed" in codes(_policy(), replace(_plan(), "work-a", read_paths=("other/**",)))
    for narrower in ("app/*", "app/sub/**", "app/**/*.py"):
        assert "read_path_not_allowed" not in codes(_policy(), replace(_plan(), "work-a", read_paths=(narrower,)))


def test_plan_requires_global_budget_for_declared_retry_limits() -> None:
    policy = _policy()
    policy = ProjectPolicy.model_validate(
        {
            **policy.model_dump(mode="json"),
            "resource_budget": {
                **policy.resource_budget.model_dump(mode="json"),
                "max_attempts": 7,
            },
        }
    )

    assert "attempt_budget_too_small" in codes(policy, _plan())


@pytest.mark.parametrize(
    ("changed", "code"),
    (
        (lambda plan: plan.model_copy(update={"criteria": ()}), "criterion_uncovered"),
        (
            lambda plan: replace_criterion(plan, verifier_task_id=None, verifier_id=None),
            "criterion_no_verifier",
        ),
        (
            lambda plan: replace_criterion(
                plan,
                verification_kind=CriterionVerificationKind.MODEL_ASSERTION,
                verifier_task_id=None,
                verifier_id=None,
            ),
            "criterion_model_assertion",
        ),
        (
            lambda plan: replace_criterion(plan, producer_task_ids=("verify",)),
            "criterion_self_verification",
        ),
    ),
)
def test_plan_rejects_unverifiable_criterion_coverage(changed, code: str) -> None:
    assert code in codes(_policy(), changed(_plan()))


def test_assembly_frontier_must_name_transitive_leaf_outputs() -> None:
    chained = replace(
        _plan(),
        "work-b",
        dependencies=("work-a",),
        inputs=(ArtifactRequirement(producer_task_id="work-a", name="patch-a", kind="patch"),),
    )
    chained = replace(
        chained,
        "assemble",
        dependencies=("work-b",),
        inputs=(ArtifactRequirement(producer_task_id="work-b", name="patch-b", kind="patch"),),
    )

    assert "artifact_frontier_missing" in codes(_policy(), chained)


def test_ordered_tasks_cannot_share_a_base_relative_write_scope() -> None:
    ordered = replace(
        _plan(),
        "work-b",
        dependencies=("work-a",),
        inputs=(ArtifactRequirement(producer_task_id="work-a", name="patch-a", kind="patch"),),
        write_paths=("app/a.py",),
        expected_outputs=(ArtifactContract(name="patch-b", kind="patch", paths=("app/a.py",)),),
    )

    assert "ordered_write_conflict" in codes(_policy(), ordered)


def test_assembly_merge_workspace_may_cover_work_output_paths() -> None:
    merged = replace(
        _plan(),
        "assemble",
        write_paths=("app/a.py", "app/b.py"),
        expected_outputs=(ArtifactContract(name="candidate", kind="patch", paths=("app/a.py", "app/b.py")),),
    )

    assert not codes(_policy(), merged) & {"ordered_write_conflict", "parallel_write_conflict"}


def test_a_task_that_is_not_merging_may_not_clobber_a_work_lease() -> None:
    """The merge exemption is the assembly over what it consumes, and nothing else."""

    verification = replace(_plan(), "verify", write_paths=("app/a.py", "out/verification.json"))
    detached = replace(
        _plan(),
        "assemble",
        write_paths=("app/a.py", "out/candidate.patch"),
        dependencies=("work-b",),
        inputs=[{"producer_task_id": "work-b", "name": "patch-b", "kind": "patch"}],
    )

    assert "ordered_write_conflict" in codes(_policy(), verification)
    assert "parallel_write_conflict" in codes(_policy(), detached)


def test_a_wide_plan_comes_back_as_a_result_rather_than_raising() -> None:
    """A 40-task plan lists more ids than `detail` holds; it is still a finding."""

    work = tuple(
        _task(f"work-task-number-{index:03d}", f"patch-{index:03d}", "patch", f"app/file{index:03d}.py")
        for index in range(40)
    )
    assembly = _task(
        "assemble",
        "candidate",
        "patch",
        "out/candidate.patch",
        kind=TaskKind.ASSEMBLY,
        role="assembler",
        dependencies=tuple(item.task_id for item in work),
    )
    verify = _task(
        "verify",
        "verification",
        "test-receipt",
        "out/verification.json",
        kind=TaskKind.VERIFICATION,
        role="verifier",
        dependencies=("assemble",),
        inputs=(ArtifactRequirement(producer_task_id="assemble", name="candidate", kind="patch"),),
    )
    plan = Plan.model_validate(
        {
            **_plan().model_dump(mode="json"),
            "tasks": [
                item.model_dump(mode="json")
                for item in sorted((*work, assembly, verify), key=lambda item: item.task_id)
            ],
        }
    )

    result = validate_plan(_policy(), plan)
    details = {item.code: item.detail for item in result.issues}

    assert "artifact_frontier_missing" in details
    assert details["artifact_frontier_missing"].endswith("(+32 more)")
    assert all(len(detail) <= 512 for detail in details.values())


@pytest.mark.parametrize(
    ("changed", "code"),
    (
        (
            lambda plan: replace(
                plan,
                "assemble",
                write_paths=("out/candidate.patch", "out/manifest.json"),
                expected_outputs=(
                    ArtifactContract(name="candidate", kind="patch", paths=("out/candidate.patch",)),
                    ArtifactContract(name="manifest", kind="report", paths=("out/manifest.json",)),
                ),
            ),
            "assembly_output_shape_unsupported",
        ),
        (
            lambda plan: replace(
                plan,
                "assemble",
                expected_outputs=(ArtifactContract(name="candidate", kind="snapshot", paths=("out/candidate.patch",)),),
            ),
            "assembly_output_kind_unsupported",
        ),
        (
            lambda plan: replace(
                plan,
                "verify",
                dependencies=("assemble", "work-a"),
                inputs=(
                    ArtifactRequirement(producer_task_id="assemble", name="candidate", kind="patch"),
                    ArtifactRequirement(producer_task_id="work-a", name="patch-a", kind="patch"),
                ),
            ),
            "verification_input_shape_unsupported",
        ),
        (
            lambda plan: replace(
                plan,
                "verify",
                expected_outputs=(
                    ArtifactContract(
                        name="verification",
                        kind="model-review",
                        paths=("out/verification.json",),
                    ),
                ),
            ),
            "verification_output_kind_unsupported",
        ),
    ),
)
def test_final_stage_shape_matches_runtime_protocol(changed, code: str) -> None:
    assert code in codes(_policy(), changed(_plan()))


def test_output_name_is_the_publication_identity() -> None:
    duplicate = replace(
        _plan(),
        "work-a",
        expected_outputs=(
            ArtifactContract(name="patch-a", kind="patch", paths=("app/a.py",)),
            ArtifactContract(name="patch-a", kind="report", paths=("app/a.py",)),
        ),
    )

    assert "duplicate_output_name" in codes(_policy(), duplicate)


def test_schema_one_policy_bytes_remain_legacy_review_required() -> None:
    policy = _policy()

    assert policy.authorization_mode == AuthorizationMode.REVIEW_REQUIRED
    assert policy.finalization_mode == FinalizationMode.REVIEW_REQUIRED
    assert "authorization_mode" not in policy.model_dump(mode="json")
    assert "finalization_mode" not in policy.model_dump(mode="json")


def test_policy_evaluation_binds_exact_valid_plan_and_modes() -> None:
    policy = ProjectPolicy.model_validate(
        {
            **_policy().model_dump(mode="json"),
            "schema_version": 2,
            "authorization_mode": AuthorizationMode.POLICY_PRE_AUTHORIZED,
            "finalization_mode": FinalizationMode.AUTO_FINALIZE_ISOLATED,
        }
    )
    plan = _plan()

    decision = evaluate_plan_policy(
        policy,
        plan,
        goal_request_id="goal-request-0001",
        requested_mode=AuthorizationMode.POLICY_PRE_AUTHORIZED,
    )

    assert decision.effective_mode == AuthorizationMode.POLICY_PRE_AUTHORIZED
    assert decision.finalization_mode == FinalizationMode.AUTO_FINALIZE_ISOLATED
    assert decision.policy_sha256 == canonical_json_sha256(policy.model_dump(mode="json"))
    assert decision.plan_sha256 == canonical_json_sha256(plan.model_dump(mode="json"))


def test_policy_evaluation_downgrades_legacy_policy_to_review() -> None:
    decision = evaluate_plan_policy(
        _policy(),
        _plan(),
        goal_request_id="goal-request-0001",
        requested_mode=AuthorizationMode.POLICY_PRE_AUTHORIZED,
    )

    assert decision.effective_mode == AuthorizationMode.REVIEW_REQUIRED
    assert decision.finalization_mode == FinalizationMode.REVIEW_REQUIRED
    assert "policy_requires_review" in decision.reason_codes


def test_automatic_finalization_rejects_a_final_result_gate() -> None:
    with pytest.raises(ValidationError, match="no final-result gate"):
        ProjectPolicy.model_validate(
            {
                **_policy().model_dump(mode="json"),
                "schema_version": 2,
                "risk_gates": ["final-result"],
                "authorization_mode": AuthorizationMode.POLICY_PRE_AUTHORIZED,
                "finalization_mode": FinalizationMode.AUTO_FINALIZE_ISOLATED,
            }
        )


# --- added here, not ported ------------------------------------------------


def test_human_gate_criterion_passes_by_default_and_fails_under_strict() -> None:
    policy = ProjectPolicy.model_validate({**_policy().model_dump(mode="json"), "risk_gates": ["release-review"]})
    gated = replace_criterion(
        _plan(),
        verification_kind=CriterionVerificationKind.HUMAN_GATE,
        verifier_task_id=None,
        verifier_id="release-review",
    )

    assert validate_plan(policy, gated).valid
    assert codes(policy, gated, strict=True) == {"criterion_human_gate"}
    with pytest.raises(PlanValidationError):
        require_valid_plan(policy, gated, strict=True)


def test_human_gate_without_a_policy_gate_has_no_verifier() -> None:
    gated = replace_criterion(
        _plan(),
        verification_kind=CriterionVerificationKind.HUMAN_GATE,
        verifier_task_id=None,
        verifier_id="release-review",
    )

    assert "criterion_no_verifier" in codes(_policy(), gated)


def test_every_emitted_code_is_documented_and_every_documented_code_is_emitted() -> None:
    source = Path(agent_plan_lint.validation.__file__).read_text(encoding="utf-8")
    emitted = {
        constant.value
        for call in ast.walk(ast.parse(source))
        if isinstance(call, ast.Call) and getattr(call.func, "id", None) == "issue"
        for constant in ast.walk(call.args[0])
        if isinstance(constant, ast.Constant) and isinstance(constant.value, str)
    }

    assert emitted == set(ISSUE_CODES)
    assert all(meaning and meaning[0].islower() for meaning in ISSUE_CODES.values())
    assert list(ISSUE_CODES) == sorted(ISSUE_CODES)


def test_issue_codes_mapping_is_read_only() -> None:
    with pytest.raises(TypeError):
        ISSUE_CODES["nope"] = "nope"  # type: ignore[index]


def _task_with(**fields: str) -> Task:
    return Task.model_validate({**_plan().tasks[-1].model_dump(mode="json"), **fields})


@pytest.mark.parametrize(
    ("field", "text", "reason"),
    (
        ("contract", "use api_key=sk-live-0123456789abcdef when calling the API", "provider key prefix"),
        ("title", "Ship ghp_0123456789abcdefghijklmnopqrstuvwx", "provider key prefix"),
        ("contract", "Send Authorization: Bearer eyJhbGciOiJIUzI1NiJ9abcdef", "bearer token"),
        ("contract", "Paste -----BEGIN RSA PRIVATE KEY----- into the store", "PEM private key block"),
        ("contract", "Clone from https://user:hunter2@example.invalid/repo", "password inside a URL"),
        ("contract", "Copy ~/.ssh/id_rsa onto the runner", "path into a credential store"),
        ("contract", "Set password=Sup3r-Secret-Value-99-aBcDeFgHiJkLmN in the env", "token-shaped value"),
        ("contract", "Rotate to aB3dEfGh1jKlMnOpQrStUvWxYz012345 today", "high-entropy token"),
    ),
)
def test_text_carrying_a_credential_is_refused_and_the_error_names_the_field(field, text, reason) -> None:
    """The refusal has to be actionable without echoing the value back into a log."""

    with pytest.raises(ValidationError) as raised:
        _task_with(**{field: text})

    message = str(raised.value)
    assert f"{field} looks like it contains a credential" in message
    assert reason in message
    assert text not in message.split("input_value=")[0]


@pytest.mark.parametrize(
    "text",
    (
        "Rotate the DB password: use the vault.",
        "Move the api_key = os.environ lookup into settings.",
        "Read /Users/ci/checkout and fix the path handling.",
        "Store the secret: never in git.",
        "Rebase onto 4d1c2f0e9a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d before merging.",
        "Refactor TheVeryLongCamelCaseHttpClient2Builder into two files.",
        "Document how token rotation works for the access_token endpoint.",
        # A name assigned after `secret`/`token`/`password` is still a name: the
        # value has to look like a secret, not merely sit where one would go.
        "Rename secret = AWS_SECRET_ACCESS_KEY_V2 in the terraform module",
        "Move the token = settings.OAUTH2_TOKEN lookup into config.",
        "Document that access_token: refresh_token_rotation_v2 is the new flow",
        "Set secret=REDACTED_PLACEHOLDER_1 in the fixture",
        "Point the worker at DATABASE_URL=postgres://db:5432/app",
        "Ship the compose file with SECRET_KEY=change-me-in-prod",
        "Read API_TOKEN: ${{ secrets.API_TOKEN }} from the workflow",
        # The documented cost of the floor: a short password in prose is a name.
        "Set password=hunter2 in the fixture",
        # A run is broken by `/` and `-` before its entropy is measured: each of
        # these is 32+ characters of mixed case with three digits when the
        # separators are ignored, and every one of them is a name, not a key.
        "Merge branch feature/AB-1234-refactor-user-profile-service",
        "Refactor src/main/java/com/example/App2024Service.java to drop the singleton",
        "Cut release SBOM-2024-11-03-Release-Candidate and attach it",
        "Update docs/adr/0007-Adopt-OpenTelemetry-1.29-Tracing.md",
    ),
)
def test_ordinary_prose_about_secrets_is_not_a_credential(text: str) -> None:
    """The buyers of a guardrail write security tickets; refusing them makes the gate unusable."""

    assert _task_with(title=text, contract=text).title == text


@pytest.mark.parametrize(
    "text",
    (
        "Set password=Sup3r-Secret-Value-99-aBcDeFgHiJkLmN in the env",
        "Put secret: aG9tZS9hbGV4/L3NlY3JldDEy-MzQ1Njc4OQ== in the fixture",
        "Use api_key = Xk29/pQ4+Lm81nZr/Ty63wBv/Hd05Ns7 for staging",
    ),
)
def test_a_secret_name_assigned_a_real_secret_is_still_refused(text: str) -> None:
    """The narrowing may not cost the shape: a separator does not break an assigned value.

    `_high_entropy` splits a run on `/`, `_` and `-` before measuring it, so none
    of these fires there. Written after `secret=` the value is one field, and 32+
    characters of mixed case with three digits is a key however it is punctuated.
    """

    from agent_plan_lint.models import _high_entropy

    assert not _high_entropy(text)
    with pytest.raises(ValidationError, match="token-shaped value"):
        _task_with(contract=text)


def test_an_environment_variable_name_is_not_the_secret_it_names() -> None:
    """The rotation ticket this gate's own buyers write, refused at exit 2 before.

    `secret = AWS_SECRET_ACCESS_KEY_V2` is a name; the value only has to be long
    enough, and mixed enough, to be a key rather than a name for the shape to
    fire. `docs/schema.md` states the same floor.
    """

    from agent_plan_lint.models import MIN_TOKEN_CHARACTERS, _is_secret_value

    assert not _is_secret_value("AWS_SECRET_ACCESS_KEY_V2")
    assert not _is_secret_value("settings.OAUTH2_TOKEN")
    assert not _is_secret_value("change-me-in-prod")
    assert not _is_secret_value("postgres://db:5432/app")
    assert _is_secret_value("sk-live-0123456789abcdef")
    assert not _is_secret_value("aB3" * ((MIN_TOKEN_CHARACTERS - 1) // 3))


def test_a_generated_key_is_still_refused_when_a_separator_stops_breaking_runs() -> None:
    """The separator split may not cost the shape it exists to catch: one unbroken blob."""

    with pytest.raises(ValidationError, match="high-entropy token"):
        _task_with(title="Set it to zK3vQm8XpLd2RtYw9BnJfHs4UeCa7Gio now")


def test_a_plan_the_policy_forbids_by_role_and_command_is_reported_per_task() -> None:
    plan = replace(_plan(), "work-a", assigned_role="ghost", allowed_commands=("deploy",))

    result = validate_plan(_policy(), plan)
    per_task = {(item.code, item.task_id) for item in result.issues}

    assert ("role_not_allowed", "work-a") in per_task
    assert ("command_not_allowed", "work-a") in per_task


def test_concurrency_and_state_are_checked_against_the_policy() -> None:
    plan = _plan().model_copy(update={"max_concurrency": 8})

    assert "concurrency_exceeds_policy" in codes(_policy(), plan)
    assert "non_initial_task_state" in codes(_policy(), replace(_plan(), "work-a", state="running"))


def test_issues_are_sorted_and_the_result_is_frozen() -> None:
    plan = replace(_plan(), "work-a", assigned_role="ghost", allowed_commands=("deploy",))
    result = validate_plan(_policy(), plan)

    assert list(result.issues) == sorted(result.issues, key=lambda item: (item.code, item.task_id or "", item.detail))
    with pytest.raises(ValidationError):
        result.issues[0].code = "other"  # type: ignore[misc]


def _writing(left: str, right: str):
    """The shared plan, with the two independent work tasks writing these paths."""

    plan = replace(
        _plan(),
        "work-a",
        write_paths=(left,),
        expected_outputs=[{"name": "patch-a", "kind": "patch", "paths": [left]}],
    )
    return replace(
        plan,
        "work-b",
        write_paths=(right,),
        expected_outputs=[{"name": "patch-b", "kind": "patch", "paths": [right]}],
    )


@pytest.mark.parametrize(
    ("left", "right"),
    (
        ("app/api.py", "app/API.py"),
        ("app/\u212bngstrom.py", "app/\u00c5ngstrom.py"),
    ),
)
def test_two_tasks_writing_one_file_under_different_spellings_conflict(left: str, right: str) -> None:
    """macOS and Windows resolve these pairs to one file, so the race is real.

    The second pair is what NFC still decides now that a path may not carry a
    combining mark: the angstrom sign and the letter it is canonically
    equivalent to are one file, and neither spelling is a mark.
    """

    result = validate_plan(_policy(), _writing(left, right))
    conflicts = [item for item in result.issues if item.code == "parallel_write_conflict"]

    assert [item.code for item in result.issues] == ["parallel_write_conflict"]
    assert left in conflicts[0].detail and right in conflicts[0].detail


def test_identical_write_paths_still_conflict_and_name_the_path() -> None:
    result = validate_plan(_policy(), _writing("app/api.py", "app/api.py"))

    assert [item.code for item in result.issues] == ["parallel_write_conflict"]
    assert result.issues[0].detail.endswith("overlap write scope: app/api.py")


def _with_exclusions(*exclusions: str) -> ProjectPolicy:
    return ProjectPolicy.model_validate({**_policy().model_dump(mode="json"), "exclusions": list(exclusions)})


def test_writing_the_root_of_an_excluded_subtree_is_refused() -> None:
    """`app/secrets/**` does not match `app/secrets`, but writing it replaces the subtree."""

    policy = _with_exclusions("app/secrets/**")
    root = replace(
        _plan(),
        "work-a",
        write_paths=("app/secrets",),
        expected_outputs=[{"name": "patch-a", "kind": "patch", "paths": ["app/secrets"]}],
    )
    inside = replace(
        _plan(),
        "work-a",
        write_paths=("app/secrets/key.env",),
        expected_outputs=[{"name": "patch-a", "kind": "patch", "paths": ["app/secrets/key.env"]}],
    )

    assert "write_path_not_allowed" in codes(policy, root)
    assert "write_path_not_allowed" in codes(policy, inside)
    assert "write_path_not_allowed" not in codes(policy, _plan())


def test_reading_the_root_of_an_excluded_subtree_is_refused() -> None:
    policy = _with_exclusions("app/secrets/**")
    plan = replace(_plan(), "work-a", read_paths=("app/secrets",))

    assert "read_path_not_allowed" in codes(policy, plan)


def test_a_wildcard_read_scope_that_can_reach_an_exclusion_is_refused() -> None:
    """A hole inside a granted scope is a hole nothing downstream of this gate enforces.

    `app/secr*/**` is the shape that motivates the rule: it is written to reach
    into the excluded directory and nothing else, and comparing the scope's
    spelling against the exclusion admitted it.
    """

    for scope in ("app/**", "app/secr*/**", "app/*", "app/**/*.py", "app/secrets/**"):
        plan = replace(_plan(), "work-a", read_paths=(scope,))
        assert "read_path_not_allowed" in codes(_with_exclusions("app/secrets/**"), plan), scope
    for exclusion in ("**/.env", "*.pem", "app/secrets.py", "app/secrets"):
        # A wildcard exclusion sits under no directory at all, so every
        # wildcard scope can reach it.
        assert "read_path_not_allowed" in codes(
            _with_exclusions(exclusion), replace(_plan(), "work-a", read_paths=("app/**",))
        ), exclusion


def test_a_wildcard_read_scope_disjoint_from_every_exclusion_is_admitted() -> None:
    """Narrowing the scope past the excluded directory is what an operator writes instead."""

    policy = _with_exclusions("app/secrets/**")

    for scope in ("tests/**", "app/src/**", "app/src/*", "app/secretsauce/**", "app/SRC/**"):
        plan = replace(_plan(), "work-a", read_paths=(scope,))
        assert "read_path_not_allowed" not in codes(policy, plan), scope


def test_a_refused_read_path_says_which_of_the_reasons_applied() -> None:
    """Three refusals wear one code, so the detail has to tell them apart."""

    def detail(policy, scope):
        plan = replace(_plan(), "work-a", read_paths=(scope,))
        found = [item for item in validate_plan(policy, plan).issues if item.code == "read_path_not_allowed"]
        assert found, scope
        return found[0].detail

    assert "matches no policy glob" in detail(_policy(), "other/x.py")
    assert "no policy glob provably covers" in detail(_policy(), "other/**")
    assert "can reach the exclusion" in detail(_with_exclusions("app/secrets/**"), "app/**")
    assert "an exclusion covers the path" in detail(_with_exclusions("app/secrets.py"), "app/secrets.py")


def test_a_read_scope_wholly_inside_an_exclusion_is_refused() -> None:
    for exclusion, scope in (
        ("app/secrets/**", "app/secrets/**"),
        ("app/secrets/**", "app/secrets/keys/**"),
        ("app/secrets", "app/secrets/keys/**"),
        ("app/**", "app/*"),
    ):
        plan = replace(_plan(), "work-a", read_paths=(scope,))
        assert "read_path_not_allowed" in codes(_with_exclusions(exclusion), plan), (exclusion, scope)


def test_an_exclusion_holds_against_a_respelled_path() -> None:
    """macOS and Windows call these the same file, so the exclusion has to."""

    for path in ("app/SECRETS.py", "app/Secrets.py", "app/secrets.py"):
        plan = replace(_plan(), "work-a", read_paths=(path,))
        assert "read_path_not_allowed" in codes(_with_exclusions("app/secrets.py"), plan), path
    singleton = replace(_plan(), "work-a", read_paths=("app/\u212bngstrom.py",))
    assert "read_path_not_allowed" in codes(_with_exclusions("app/\u00c5ngstrom.py"), singleton)
    inside = replace(
        _plan(),
        "work-a",
        write_paths=("app/SECRETS/key.pem",),
        expected_outputs=[{"name": "patch-a", "kind": "patch", "paths": ["app/SECRETS/key.pem"]}],
    )
    assert "write_path_not_allowed" in codes(_with_exclusions("app/secrets/**"), inside)


def test_a_bare_directory_exclusion_covers_what_is_inside_it() -> None:
    """`exclusions: ["app/secrets"]` is what an operator writes, and it has to hold."""

    plan = replace(
        _plan(),
        "work-a",
        write_paths=("app/secrets/key.pem",),
        expected_outputs=[{"name": "patch-a", "kind": "patch", "paths": ["app/secrets/key.pem"]}],
    )

    assert "write_path_not_allowed" in codes(_with_exclusions("app/secrets"), plan)
    assert "write_path_not_allowed" not in codes(_with_exclusions("app/secretsauce"), plan)


@pytest.mark.parametrize(
    "argv0",
    ("bash", "/bin/bash", "/bin/sh", "Bash", "bash.exe", "env", "xargs", "C:\\Windows\\System32\\cmd.exe", "pwsh"),
)
def test_a_shell_template_is_refused_however_it_is_spelled(argv0: str) -> None:
    with pytest.raises(ValidationError, match="shell command templates"):
        CommandTemplate(template_id="edit", argv=(argv0, "-c", "true"), timeout_seconds=60)


@pytest.mark.parametrize("argv0", ("pytest", "python", "/usr/bin/python3", "ruff"))
def test_a_direct_command_template_is_accepted(argv0: str) -> None:
    """The guard is a typo guard, not containment: `python -c` is a shell and is allowed."""

    assert CommandTemplate(template_id="edit", argv=(argv0, "x"), timeout_seconds=60).argv[0] == argv0


@pytest.mark.parametrize("value", ("a\nb", "a\rb", "a\tb", "a\x00b", "a\x7fb"))
def test_control_characters_are_refused_in_paths_and_in_public_text(value: str) -> None:
    with pytest.raises(ValidationError):
        replace(_plan(), "work-a", read_paths=(value,))
    with pytest.raises(ValidationError):
        replace(_plan(), "work-a", title=value)


def test_an_output_path_the_policy_never_granted_is_refused() -> None:
    """A published path is a written path: the write grant and the exclusions apply to it.

    Comparing an output only against the task's own lease let a respelling --
    one file on macOS, two on Linux -- publish a path the policy never named.
    """

    published = replace(
        _plan(),
        "work-a",
        write_paths=("app/a.py",),
        expected_outputs=[{"name": "patch-a", "kind": "patch", "paths": ["app/A.py"]}],
    )
    narrow = ProjectPolicy.model_validate(
        {**_policy().model_dump(mode="json"), "allowed_write_globs": ("app/a.py", "out/**")}
    )

    for policy in (narrow, _with_exclusions("app/A.py")):
        refused = [
            item
            for item in validate_plan(policy, published).issues
            if item.code == "write_path_not_allowed" and item.task_id == "work-a"
        ]
        assert refused, [item.code for item in validate_plan(policy, published).issues]
        assert refused[0].detail.endswith("app/A.py")
    assert "write_path_not_allowed" not in codes(_policy(), _plan())


def test_a_directory_lease_and_a_file_lease_inside_it_conflict() -> None:
    """Whichever writes the directory last destroys the other task's file."""

    plan = replace(
        _plan(),
        "work-a",
        write_paths=("app/pkg",),
        expected_outputs=[{"name": "patch-a", "kind": "patch", "paths": ["app/pkg"]}],
    )
    plan = replace(
        plan,
        "work-b",
        write_paths=("app/pkg/x.py",),
        expected_outputs=[{"name": "patch-b", "kind": "patch", "paths": ["app/pkg/x.py"]}],
    )
    result = validate_plan(_policy(), plan)
    conflicts = [item for item in result.issues if item.code == "parallel_write_conflict"]

    assert conflicts, [item.code for item in result.issues]
    # The listing names the containing path, which is the one that has to move.
    assert conflicts[0].detail.endswith("overlap write scope: app/pkg")
    assert "parallel_write_conflict" not in codes(_policy(), _plan())
    assert "parallel_write_conflict" not in codes(
        _policy(),
        replace(
            _plan(),
            "work-b",
            write_paths=("app/pkgsuffix.py",),
            expected_outputs=[{"name": "patch-b", "kind": "patch", "paths": ["app/pkgsuffix.py"]}],
        ),
    )


def test_the_merge_exemption_covers_only_the_paths_the_assembly_merges() -> None:
    """Consuming one artifact is not a licence over the rest of the producer's lease."""

    plan = replace(
        _plan(),
        "work-a",
        write_paths=("app/a.py", "app/notes.md"),
        expected_outputs=[{"name": "patch-a", "kind": "patch", "paths": ["app/a.py"]}],
    )
    plan = replace(
        plan,
        "assemble",
        write_paths=("app/a.py", "app/notes.md", "out/candidate.patch"),
        expected_outputs=[{"name": "candidate", "kind": "patch", "paths": ["out/candidate.patch"]}],
    )
    result = validate_plan(_policy(), plan)
    conflicts = [item for item in result.issues if item.code == "ordered_write_conflict"]

    assert conflicts, [item.code for item in result.issues]
    assert "app/notes.md" in conflicts[0].detail
    assert "app/a.py" not in conflicts[0].detail


def test_a_policy_granting_everything_admits_every_wildcard_read_scope() -> None:
    """`**` is the broadest grant the schema can express; it cannot be the one that misfires."""

    policy = ProjectPolicy.model_validate(
        {**_policy().model_dump(mode="json"), "allowed_read_globs": ("**",), "allowed_write_globs": ("**",)}
    )

    for scope in ("app/*", "app/**", "app/**/*.py", "**", "**/*.py"):
        assert "read_path_not_allowed" not in codes(policy, replace(_plan(), "work-a", read_paths=(scope,))), scope
    assert "read_path_not_allowed" not in codes(policy, replace(_plan(), "work-a", read_paths=("app/exact.py",)))
    assert "read_path_not_allowed" in codes(
        ProjectPolicy.model_validate({**policy.model_dump(mode="json"), "exclusions": ("app/**",)}),
        replace(_plan(), "work-a", read_paths=("app/*",)),
    )


def test_a_case_sensitive_policy_opts_out_of_the_folding() -> None:
    """One filesystem's opinion is a policy setting, and it moves every comparison at once."""

    sensitive = ProjectPolicy.model_validate({**_policy().model_dump(mode="json"), "case_sensitive_paths": True})
    respelled = _writing("app/api.py", "app/API.py")

    assert "parallel_write_conflict" in codes(_policy(), respelled)
    assert "parallel_write_conflict" not in codes(sensitive, respelled)
    excluding = {**_policy().model_dump(mode="json"), "exclusions": ("app/secrets.py",)}
    shouted = replace(_plan(), "work-a", read_paths=("app/SECRETS.py",))
    assert "read_path_not_allowed" in codes(ProjectPolicy.model_validate(excluding), shouted)
    assert "read_path_not_allowed" not in codes(
        ProjectPolicy.model_validate({**excluding, "case_sensitive_paths": True}), shouted
    )


def _crowd(count: int, **task_fields: object) -> Plan:
    """The base plan plus `count` extra work tasks, all shaped the same way."""

    base = _plan().model_dump(mode="json")
    extra = [
        {
            **_task(f"work-c{index:03d}", f"patch-c{index:03d}", "patch", "app/api.py").model_dump(mode="json"),
            **task_fields,
        }
        for index in range(count)
    ]
    return Plan.model_validate({**base, "tasks": sorted(base["tasks"] + extra, key=lambda item: item["task_id"])})


def test_one_contested_path_is_one_finding_however_many_tasks_race_for_it() -> None:
    """A path leased by k tasks is one race, not k(k-1)/2 restatements of it."""

    import json

    result = validate_plan(_policy(), _crowd(60))
    conflicts = [item for item in result.issues if item.code == "parallel_write_conflict"]

    assert len(conflicts) == 1
    assert "app/api.py" in conflicts[0].detail
    assert "work-c000" in conflicts[0].detail
    assert len(json.dumps(result.model_dump(mode="json"))) < 100_000


def test_a_code_that_fires_on_every_task_is_reported_up_to_a_bound_and_then_counted() -> None:
    """A wide plan comes back as a bounded report, and the report says what it left out."""

    from agent_plan_lint.validation import _ISSUES_PER_CODE

    result = validate_plan(_policy(), _crowd(_ISSUES_PER_CODE + 8, assigned_role="ghost"))
    refusals = [item for item in result.issues if item.code == "role_not_allowed"]

    assert len(refusals) == _ISSUES_PER_CODE + 1
    assert refusals[-1].detail == "and 8 more findings under this code, not listed"
    assert not result.valid


@pytest.mark.parametrize("text", ("docs/\u202eok.py", "docs/a\u200bb.py", "docs/a\u2066b.py"))
def test_a_bidirectional_override_in_a_path_is_refused_when_the_document_loads(text: str) -> None:
    """The model is the public API: a library consumer formats findings itself."""

    with pytest.raises(ValidationError, match="bidirectional formatting"):
        replace(_plan(), "work-a", read_paths=(text,))


@pytest.mark.parametrize(
    "text",
    (
        "\u0645\u06cc\u200c\u062e\u0648\u0627\u0647\u0645 refactor the parser",
        "\u0915\u094d\u200c\u0937 module rename",
        "Ship the \U0001f469\u200d\U0001f4bb onboarding page",
    ),
)
def test_a_zero_width_joiner_is_orthography_rather_than_a_forged_line(text: str) -> None:
    """U+200C and U+200D neither move the cursor nor hide text; refusing them refuses Persian."""

    assert _task_with(title=text).title == text


@pytest.mark.parametrize("character", ("\u200c", "\u200d", "\u00a0", "\u2000"))
def test_an_invisible_character_is_refused_in_a_path_though_it_is_legal_in_text(character: str) -> None:
    """A joiner is orthography in a title and a second file in a path.

    `app/secrets<ZWJ>/key.pem` renders character for character like
    `app/secrets/key.pem`, so it walks past an exclusion on that subtree, and two
    tasks leasing `app/api.py` and `app/api<ZWJ>.py` are one lease to the
    reviewer approving the plan. The whole Cf class is refused in a path, by
    name, and stays legal in `title`, `contract` and `blocker`.
    """

    hidden = f"app/secrets{character}/key.pem"

    assert _task_with(title=f"Ship the a{character}b page").title == f"Ship the a{character}b page"
    for field in ("read_paths", "write_paths"):
        with pytest.raises(ValidationError, match=r"may not contain U\+"):
            _task_with(**{field: [hidden]})
    with pytest.raises(ValidationError, match=r"may not contain U\+"):
        ProjectPolicy.model_validate(
            {**_policy().model_dump(mode="json"), "exclusions": [f"app/secrets{character}/**"]}
        )


def test_a_zero_width_joiner_cannot_walk_past_an_exclusion_or_a_write_lease() -> None:
    """The two properties the README leads with, against the three-byte escape.

    Before the path class was split from the text class, the leased path below
    passed a policy excluding `app/secrets/**` and printed `ok:`, and the two
    spellings of `app/api.py` were two leases rather than a
    `parallel_write_conflict`.
    """

    excluded = "app/secrets/key.pem"
    disguised = "app/secrets\u200d/key.pem"
    policy = _with_exclusions("app/secrets/**")
    plan = replace(
        _plan(),
        "work-a",
        write_paths=(excluded,),
        expected_outputs=[{"name": "patch-a", "kind": "patch", "paths": [excluded]}],
    )

    assert "write_path_not_allowed" in codes(policy, plan)
    with pytest.raises(ValidationError, match=r"may not contain U\+"):
        replace(
            _plan(),
            "work-a",
            write_paths=(disguised,),
            expected_outputs=[{"name": "patch-a", "kind": "patch", "paths": [disguised]}],
        )


def test_a_direction_override_is_still_refused_alongside_the_joiners() -> None:
    """The narrowing may not cost what the class exists for."""

    with pytest.raises(ValidationError, match="bidirectional formatting"):
        _task_with(title="Ship the \u202ereversed title")


@pytest.mark.parametrize("text", ("app/api.py.", "app/api.py ", "app/dir./file.py", "app/dir /file.py"))
def test_a_path_component_ending_in_a_dot_or_a_space_is_refused_when_the_document_loads(text: str) -> None:
    """Windows strips both, so these are `app/api.py` there and a second lease here."""

    with pytest.raises(ValidationError, match="dot or a space"):
        replace(_plan(), "work-a", read_paths=(text,))


def test_a_trailing_dot_cannot_walk_past_an_exclusion_or_a_write_lease() -> None:
    """The two properties the README leads with, against the one-character escape."""

    policy = _policy().model_copy(update={"exclusions": ("app/token.env",)})

    with pytest.raises(ValidationError, match="dot or a space"):
        replace(_plan(), "work-a", write_paths=("app/token.env.",), expected_outputs=())
    with pytest.raises(ValidationError, match="dot or a space"):
        replace(_plan(), "work-b", write_paths=("app/a.py.",), expected_outputs=())
    assert policy.exclusions == ("app/token.env",)


@pytest.mark.parametrize(
    "text",
    (
        "run_MigrationV2_2024_backfill_Step3_final",
        "rotate_db_password_helper",
        "rotate_db_password_helper_for_Stage2_2024_Rollout3",
        "Rename test_checkout_idempotency_Retry2024_Case3_variant",
        "Bump the open_telemetry_Collector0_Dot98_Release3 chart",
    ),
)
def test_a_snake_case_name_is_a_name_rather_than_a_credential(text: str) -> None:
    """`_` is the dominant word separator in Python, and it did not break a run.

    An underscore-joined migration, test or feature-flag name that happens to
    mix case and carry a year was refused at the parse boundary as "a long
    high-entropy token", which rejected the whole document with exit 2.
    """

    assert _task_with(title=text, contract=text).title == text


@pytest.mark.parametrize(
    "text",
    (
        "Update the FeatureFlagRolloutStage2Cohort3Batch4 rollout",
        "Rename testCheckoutIdempotencyRetry2024Case3Variant",
    ),
)
def test_an_unbroken_camel_case_run_with_three_digits_is_still_refused(text: str) -> None:
    """The documented limit of the heuristic, pinned so the page cannot drift off it.

    Nothing separates a 32-character CamelCase name carrying three digits from a
    generated key without giving up the unprefixed-key catch, so the run is
    refused and `docs/schema.md` says to break it with `/`, `_` or `-`.
    """

    with pytest.raises(ValidationError, match="high-entropy token"):
        _task_with(title=text)


def test_the_entropy_rule_never_fires_on_a_short_identifier() -> None:
    """A run has to be long before mixed case means "generated", and 24 characters is short."""

    from agent_plan_lint.models import MIN_TOKEN_CHARACTERS, _high_entropy

    assert MIN_TOKEN_CHARACTERS >= 24
    for length in range(1, 24):
        identifier = ("aB3" * 8)[:length]
        assert not _high_entropy(identifier), identifier
        assert not _high_entropy(f"Ship {identifier} today"), identifier


def test_a_write_lease_is_not_folded_by_a_case_fold_no_filesystem_performs() -> None:
    """`str.casefold` is *full* folding: it maps `ss`, `fi`, `s`.

    macOS and Windows fold case simply, so `app/gru.py` and `app/gruss.py` are
    two files that coexist and a plan writing both is not a conflict.
    """

    from agent_plan_lint.validation import _path_key

    assert _path_key("a/ß.py") != _path_key("a/ss.py")
    assert _path_key("a/ﬁle.py") != _path_key("a/file.py")
    assert _path_key("a/API.py") == _path_key("a/api.py")
    assert _path_key("a/\u212bngstrom.py") == _path_key("a/\u00c5ngstrom.py")
    assert _path_key("a/CAFÉ.py") == _path_key("a/café.py")

    result = validate_plan(_policy(), _writing("app/gruß.py", "app/gruss.py"))

    assert [item.code for item in result.issues] == []


@pytest.mark.parametrize(
    "character",
    ("­", "᠎", "⁠", "⁡", "⁢", "⁣", "⁤", "﻿", "ᅟ", "ᅠ", "ㅤ"),
)
def test_a_character_that_hides_text_is_refused_wherever_u200b_is(character: str) -> None:
    """The class exists because two leases that render identically are one lease to a reviewer.

    U+200B is refused on the stated ground that it hides text; every character
    here hides text the same way, so a plan could hold two files a human
    approving it sees as one.
    """

    with pytest.raises(ValidationError, match="bidirectional formatting"):
        replace(_plan(), "work-a", read_paths=(f"docs/a{character}b.py",))
    with pytest.raises(ValidationError, match="bidirectional formatting"):
        _task_with(title=f"Ship a{character}b today")


# ---------------------------------------------------------------------------
# The path character rule: a category test, not `str.isprintable`.
# ---------------------------------------------------------------------------

#: `Default_Ignorable_Code_Point`, transcribed a second time from
#: https://www.unicode.org/Public/15.1.0/ucd/DerivedCoreProperties.txt so the
#: expression in `models` is checked against a copy of the property rather than
#: against itself. Ranges adjacent in the file are kept apart here on purpose.
DEFAULT_IGNORABLE_RANGES = (
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
    (0xE0000, 0xE0001),
    (0xE0002, 0xE001F),
    (0xE0020, 0xE007F),
    (0xE0080, 0xE00FF),
    (0xE0100, 0xE01EF),
    (0xE01F0, 0xE0FFF),
)


def _default_ignorable() -> tuple[str, ...]:
    return tuple(chr(point) for first, last in DEFAULT_IGNORABLE_RANGES for point in range(first, last + 1))


def _the_264_str_isprintable_admitted() -> tuple[str, ...]:
    """Every hidden code point the previous guard called printable.

    Generated, not listed: the combining-mark half of the property, read out of
    `unicodedata` at run time so a Unicode version that moves one shows up here,
    plus U+2800, which is not in the property and is drawn blank by every font.
    """

    marks = tuple(character for character in _default_ignorable() if unicodedata.category(character).startswith("M"))
    return (*marks, "\u2800")


def test_the_default_ignorable_expression_is_the_property_it_claims_to_be() -> None:
    """A typo in one range would admit a whole block of hidden characters in silence."""

    from agent_plan_lint.models import DEFAULT_IGNORABLE

    matched = {point for point in range(0x110000) if DEFAULT_IGNORABLE.match(chr(point))}

    assert matched == {ord(character) for character in _default_ignorable()}


def test_every_default_ignorable_code_point_is_refused_in_a_path() -> None:
    """The guard is the Unicode property, not a list of the characters someone thought of.

    `_relative_posix_path` is the one validator behind every path field, so the
    sweep runs against it directly; the test below runs one representative
    through each of the fields that use it.
    """

    from agent_plan_lint.models import _relative_posix_path

    admitted = []
    for character in (*_default_ignorable(), "\u2800"):
        try:
            _relative_posix_path(f"app/sec{character}rets/key.pem")
        except ValueError:
            continue
        admitted.append(f"U+{ord(character):04X}")

    assert admitted == []


def test_the_264_code_points_str_isprintable_admitted_are_refused_in_a_path() -> None:
    """The exact class the previous guard let through, back through a model.

    `str.isprintable` is false only for the C and Z categories, so all 264 of
    these -- the combining grapheme joiner, the Khmer inherent vowels, the
    Mongolian free variation selectors, the 256 variation selectors and the
    blank Braille cell -- loaded in every path field, and
    `app/sec<U+034F>rets/key.pem` walked past an exclusion on `app/secrets/**`.
    """

    hidden = _the_264_str_isprintable_admitted()

    assert len(hidden) == 264
    assert all(character.isprintable() for character in hidden)
    for character in hidden:
        with pytest.raises(ValidationError, match=r"may not contain U\+"):
            _task_with(read_paths=[f"app/sec{character}rets/key.pem"])


def test_a_hidden_code_point_is_refused_in_every_field_that_holds_a_path() -> None:
    """One validator behind seven fields, so the rule cannot hold in only some of them."""

    hidden = "app/sec\u034frets/key.pem"
    expected = r"may not contain U\+034F"

    for field in ("read_paths", "write_paths"):
        with pytest.raises(ValidationError, match=expected):
            _task_with(**{field: [hidden]})
    with pytest.raises(ValidationError, match=expected):
        _task_with(expected_outputs=[{"name": "patch-a", "kind": "patch", "paths": [hidden]}])
    for field in ("allowed_read_globs", "allowed_write_globs", "exclusions"):
        with pytest.raises(ValidationError, match=expected):
            ProjectPolicy.model_validate({**_policy().model_dump(mode="json"), field: [hidden]})
    with pytest.raises(ValidationError, match=expected):
        CommandTemplate(template_id="edit", argv=("python",), timeout_seconds=60, cwd=hidden)


def test_a_combining_grapheme_joiner_cannot_walk_past_an_exclusion_or_a_write_lease() -> None:
    """The two headline properties, against the escape `str.isprintable` left open.

    `check` printed `ok:` for a plan reading `app/sec<U+034F>rets/key.pem` under
    `exclusions: ["app/secrets/**"]`, and two tasks leasing `app/a.py` and
    `app/a<U+034F>.py` were two leases rather than a `parallel_write_conflict`.
    """

    policy = _with_exclusions("app/secrets/**")

    assert "read_path_not_allowed" in codes(policy, replace(_plan(), "work-a", read_paths=("app/secrets/key.pem",)))
    with pytest.raises(ValidationError, match=r"may not contain U\+034F"):
        replace(_plan(), "work-a", read_paths=("app/sec\u034frets/key.pem",))
    with pytest.raises(ValidationError, match=r"may not contain U\+034F"):
        _writing("app/a.py", "app/a\u034f.py")


def test_a_combining_mark_is_refused_in_a_path_and_stays_legal_in_text() -> None:
    """What the M clause costs, pinned: the decomposed spelling of an accented name.

    The composed spelling is a path; the decomposed one is refused rather than
    folded, because folding it would make a path a policy granted stop matching
    itself on a case-sensitive filesystem. `docs/schema.md` states the trade.
    """

    assert _task_with(read_paths=["app/caf\u00e9.py"]).read_paths == ("app/caf\u00e9.py",)
    with pytest.raises(ValidationError, match=r"may not contain U\+0301"):
        _task_with(read_paths=["app/cafe\u0301.py"])
    assert _task_with(title="Rename cafe\u0301.py").title == "Rename cafe\u0301.py"


def test_a_space_inside_a_file_name_is_still_a_path() -> None:
    """U+0020 is the one separator a path may carry, and only inside a component."""

    assert _task_with(read_paths=["app/my notes.py"]).read_paths == ("app/my notes.py",)
    with pytest.raises(ValidationError, match="dot or a space"):
        _task_with(read_paths=["app/notes /a.py"])
    with pytest.raises(ValidationError, match=r"may not contain U\+00A0"):
        _task_with(read_paths=["app/my\u00a0notes.py"])
