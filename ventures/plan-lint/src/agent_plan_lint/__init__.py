"""agent-plan-lint: static validation of an agent's plan against a project policy.

from agent_plan_lint import load_plan, load_policy, validate_plan

result = validate_plan(load_policy("policy.json"), load_plan("plan.json"))
print(result.valid, [issue.code for issue in result.issues])
"""

from __future__ import annotations

from importlib import metadata

from .globs import full_match
from .loading import DocumentError, load_plan, load_policy
from .models import (
    ArtifactContract,
    ArtifactRequirement,
    AuthorizationMode,
    CommandTemplate,
    Criterion,
    CriterionVerificationKind,
    FinalizationMode,
    NetworkMode,
    NetworkPolicy,
    Plan,
    PlanPolicyDecisionV1,
    ProjectPolicy,
    ResourceBudget,
    Task,
    TaskKind,
    TaskState,
    canonical_json_sha256,
)
from .validation import (
    ISSUE_CODES,
    PlanValidationError,
    PlanValidationIssue,
    PlanValidationResult,
    evaluate_plan_policy,
    require_valid_plan,
    validate_plan,
)

#: The distribution name, derived from this package's import name.
NAME = __name__.replace("_", "-")

try:
    __version__ = metadata.version(NAME)
except metadata.PackageNotFoundError:  # pragma: no cover - source tree without install
    __version__ = "0+unknown"

__all__ = [
    "ISSUE_CODES",
    "NAME",
    "ArtifactContract",
    "ArtifactRequirement",
    "AuthorizationMode",
    "CommandTemplate",
    "Criterion",
    "CriterionVerificationKind",
    "DocumentError",
    "FinalizationMode",
    "NetworkMode",
    "NetworkPolicy",
    "Plan",
    "PlanPolicyDecisionV1",
    "PlanValidationError",
    "PlanValidationIssue",
    "PlanValidationResult",
    "ProjectPolicy",
    "ResourceBudget",
    "Task",
    "TaskKind",
    "TaskState",
    "__version__",
    "canonical_json_sha256",
    "evaluate_plan_policy",
    "full_match",
    "load_plan",
    "load_policy",
    "require_valid_plan",
    "validate_plan",
]
