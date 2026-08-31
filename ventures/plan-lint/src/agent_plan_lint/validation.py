"""The admission gate: does this plan fit inside this policy?

Pure functions over frozen models. Nothing here reads the filesystem, the
network, or the clock, and nothing here mutates its arguments.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Callable
from types import MappingProxyType

from pydantic import Field

from .globs import _components, matches_any
from .models import (
    AuthorizationMode,
    CriterionVerificationKind,
    FinalizationMode,
    FrozenModel,
    Plan,
    PlanPolicyDecisionV1,
    ProjectPolicy,
    Task,
    TaskKind,
    TaskState,
    canonical_json_sha256,
)

__all__ = [
    "ISSUE_CODES",
    "PlanValidationError",
    "PlanValidationIssue",
    "PlanValidationResult",
    "evaluate_plan_policy",
    "require_valid_plan",
    "validate_plan",
]

#: Every issue code this validator can emit, mapped to its one-line meaning.
ISSUE_CODES = MappingProxyType(
    {
        "acceptance_check_count_unsupported": "a task declares more or fewer than one acceptance check",
        "artifact_frontier_ambiguous": "the assembly task consumes an input no work task publishes",
        "artifact_frontier_missing": "the assembly task omits a work task's output",
        "assembly_count": "the plan does not contain exactly one assembly task",
        "assembly_not_reachable": "the assembly task is not downstream of every work task",
        "assembly_output_kind_unsupported": "the assembly task's output kind is not 'patch'",
        "assembly_output_shape_unsupported": "the assembly task does not publish exactly one output",
        "attempt_budget_too_small": "the summed task attempt limits exceed the policy attempt budget",
        "attempt_limit_exceeds_policy": "a task's attempt limit exceeds the policy retry limit plus one",
        "command_not_allowed": "a task names a command template the policy does not define",
        "concurrency_exceeds_policy": "the plan's max_concurrency exceeds the policy's",
        "criterion_human_gate": "a criterion is verified by a human gate (--strict only)",
        "criterion_missing_producer": "a criterion names a producing task the plan does not contain",
        "criterion_model_assertion": "a criterion is verified by a model assertion, which proves nothing",
        "criterion_no_verifier": "a criterion has no verification task check or policy gate behind it",
        "criterion_self_verification": "a criterion is verified by one of its own producing tasks",
        "criterion_uncovered": "the plan declares no criteria, or a criterion has no producing task",
        "criterion_verifier_not_downstream": "a criterion's verifier is not downstream of every producer",
        "cycle": "the task dependency graph contains a cycle",
        "dependency_without_artifact": "a task depends on another without consuming any of its artifacts",
        "duplicate_output_name": "a task publishes two outputs under one name",
        "input_without_dependency": "a task consumes an artifact from a task it does not depend on",
        "missing_artifact_contract": "a task consumes an artifact its producer does not publish",
        "missing_dependency": "a task depends on a task the plan does not contain",
        "non_initial_task_state": "a task is not queued with zero attempts",
        "ordered_write_conflict": "two ordered tasks write the same path",
        "output_outside_write_scope": "a task's output names a path outside its own write lease",
        "parallel_write_conflict": "two independent tasks write the same path",
        "read_path_not_allowed": "a task reads a path the policy does not allow",
        "role_not_allowed": "a task is assigned a role the policy does not allowlist",
        "verification_count": "the plan does not contain exactly one verification task",
        "verification_input_shape_unsupported": "the verification task consumes more than the assembly candidate",
        "verification_not_bound": "the verification task is not downstream of the assembly task",
        "verification_output_kind_unsupported": "the verification task's output kind is not 'test-receipt'",
        "verification_output_shape_unsupported": "the verification task does not publish exactly one output",
        "write_path_not_allowed": "a task writes a path the policy does not allow",
    }
)


class PlanValidationIssue(FrozenModel):
    code: str = Field(pattern=r"^[a-z][a-z0-9_]{1,63}$")
    task_id: str | None = None
    detail: str = Field(min_length=1, max_length=512)


class PlanValidationResult(FrozenModel):
    valid: bool
    topological_order: tuple[str, ...]
    issues: tuple[PlanValidationIssue, ...]


class PlanValidationError(ValueError):
    def __init__(self, result: PlanValidationResult) -> None:
        self.result = result
        super().__init__("; ".join(item.code for item in result.issues))


#: The `detail` field's own bound, so a long listing is truncated once, here.
_DETAIL_LIMIT = 512
#: How many items a listing spells out before it counts the rest.
_LISTING_LIMIT = 8
#: How many findings one code reports before the rest are counted in one line.
#: A wide plan is a bounded report -- at most 33 lines per code -- rather than a
#: multi-megabyte one piped into a hook's `json.loads`. `docs/schema.md` says so.
_ISSUES_PER_CODE = 32


def _listing(items: list[str]) -> str:
    """Name the first few items and count the rest, so a detail stays readable."""

    if len(items) <= _LISTING_LIMIT:
        return ", ".join(items)
    return ", ".join(items[:_LISTING_LIMIT]) + f" (+{len(items) - _LISTING_LIMIT} more)"


def _bounded(detail: str) -> str:
    return detail if len(detail) <= _DETAIL_LIMIT else detail[: _DETAIL_LIMIT - 3] + "..."


def _capped(issues: list[PlanValidationIssue]) -> tuple[PlanValidationIssue, ...]:
    """The first `_ISSUES_PER_CODE` findings of each code, plus one line counting the rest.

    The count is what a caller acts on; the thousandth restatement of it is
    output volume. `issues` arrives in canonical order, so the kept ones are
    the same on every run.
    """

    seen: dict[str, int] = {}
    for item in issues:
        seen[item.code] = seen.get(item.code, 0) + 1
    kept: list[PlanValidationIssue] = []
    shown: dict[str, int] = {}
    for item in issues:
        shown[item.code] = count = shown.get(item.code, 0) + 1
        if count <= _ISSUES_PER_CODE:
            kept.append(item)
        elif count == _ISSUES_PER_CODE + 1:
            rest = seen[item.code] - _ISSUES_PER_CODE
            kept.append(
                PlanValidationIssue(code=item.code, detail=f"and {rest} more findings under this code, not listed")
            )
    return tuple(kept)


def _path_key(path: str, *, case_sensitive: bool = False) -> str:
    """The one normalisation every path comparison in this package goes through.

    Exclusions, write leases, lease overlaps and a task's expected outputs are
    all compared on this key, so a path cannot mean one thing to one check and
    another to the next.

    macOS (APFS, case-insensitive by default) and Windows treat `app/api.py`
    and `app/API.py` as the same file, and APFS treats the NFC and NFD
    spellings of an accented name as the same file, so the default folds case
    after normalising to NFC. A policy that sets `case_sensitive_paths: true`
    -- a repository that only ever lives on a case-sensitive filesystem --
    opts out of the folding; NFC still applies, because the two spellings of
    an accented name are one name rather than one filesystem's opinion.
    """

    key = unicodedata.normalize("NFC", path)
    if case_sensitive:
        return key
    # `str.casefold` is *full* case folding, which expands: it maps `ß` to `ss`
    # and `ﬁ` to `fi`. No filesystem does that -- macOS and Windows fold
    # simply -- so full folding collapsed `gruß.py` and `gruss.py`, two files
    # that coexist everywhere, into one lease. Keeping only the folds that
    # preserve length is simple case folding in practice.
    return "".join(folded if len(folded := character.casefold()) == 1 else character.lower() for character in key)


def _contains(outer: str, inner: str) -> bool:
    """True when `inner` sits strictly inside the subtree `outer` names."""

    return inner.startswith(f"{outer}/")


def _ancestors_of(key: str) -> list[str]:
    """Every directory `key` hangs off, as keys: `a/b/c` -> `a`, `a/b`."""

    parts = key.split("/")
    return ["/".join(parts[:index]) for index in range(1, len(parts))]


def _excluded(key: str, exclusions: tuple[str, ...]) -> bool:
    """True when an exclusion covers the key `key`, in either direction of containment.

    An exclusion covers what is under it -- `app/secrets` covers
    `app/secrets/key.pem`, which is what excluding a directory by name means --
    and the path its own subtree hangs off, because writing `app/secrets`
    replaces the subtree `app/secrets/**` is protecting. Both sides arrive
    already through `_path_key`, so an exclusion cannot be escaped by respelling
    a path in another case or normalisation that macOS and Windows call the
    same file.
    """

    return matches_any(key, exclusions) or any(_contains(key, item) or _contains(item, key) for item in exclusions)


def _covers(pattern: str, scope: str) -> bool:
    """True when every path `scope` can match also matches `pattern`.

    Containment between two patterns is decided only for the shapes policies
    are written in: `pattern` itself, and anything spelled under the literal
    prefix of a `**`-terminated pattern. So `app/**` covers `app/*` and
    `app/sub/**`, and the bare `**` -- whose literal prefix is empty, so every
    scope is under it -- covers everything. Nothing here decides a pattern
    whose prefix opens with a wildcard.
    """

    if pattern == scope:
        return True
    components = _components(pattern)
    if components[-1] != "**":
        return False
    prefix = "/".join(components[:-1])
    return not any(character in prefix for character in "*?[") and (not prefix or scope.startswith(f"{prefix}/"))


def _literal_prefix(pattern: str) -> str:
    """The directory every match of `pattern` sits under: its components before the first wildcard.

    `app/secrets/**` sits under `app/secrets`; `app/secr*/**` sits under `app`;
    `**/.env` and `*.pem` sit under nothing at all, so they can be reached from
    anywhere.
    """

    prefix: list[str] = []
    for component in _components(pattern):
        if any(character in component for character in "*?["):
            break
        prefix.append(component)
    return "/".join(prefix)


def _may_reach(scope: str, exclusion: str) -> bool:
    """True unless no path can be under both globs.

    Deciding glob-against-glob intersection in general is not worth its cost
    here, and guessing the wrong way would grant access. One shape proves
    disjointness outright -- the literal prefixes the two sit under diverge, so
    nothing is under both -- and everything else is treated as reachable.
    """

    left, right = _literal_prefix(scope), _literal_prefix(exclusion)
    if not left or not right:
        return True
    return left == right or left.startswith(f"{right}/") or right.startswith(f"{left}/")


def _read_scope_refusal(
    scope: str,
    allowed_globs: tuple[str, ...],
    exclusions: tuple[str, ...],
    *,
    case_sensitive: bool,
) -> str | None:
    """Why the policy refuses this read scope, or None when it grants it.

    An exact path has to match a granted glob and miss every exclusion. A
    wildcard scope has to be provably inside one granted glob *and* provably
    unable to reach any exclusion: a scope that can reach excluded content is
    refused rather than granted with a hole in it, because nothing downstream
    of this gate enforces the hole. `docs/schema.md` states the rule and what
    an operator writes instead.
    """

    key = _path_key(scope, case_sensitive=case_sensitive)
    if any(character in scope for character in "*?["):
        if not any(_covers(glob, scope) for glob in allowed_globs):
            return "no policy glob provably covers this wildcard scope"
        reached = [item for item in exclusions if _may_reach(key, item)]
        return f"the scope can reach the exclusion {reached[0]}" if reached else None
    if not matches_any(scope, allowed_globs):
        return "the path matches no policy glob"
    return "an exclusion covers the path" if _excluded(key, exclusions) else None


def _merges(assembly: Task, producer: Task) -> bool:
    """True when `assembly` is the merge stage for `producer`'s output.

    An assembly re-writes what it merges, so its lease overlapping a work task
    whose artifact it consumes is the shape this schema asks for. Every other
    overlapping pair is a conflict, including an assembly against a work task
    it does not consume, and a verification task against anything.
    """

    return (
        assembly.kind == TaskKind.ASSEMBLY
        and producer.kind == TaskKind.WORK
        and producer.task_id in {item.producer_task_id for item in assembly.inputs}
    )


def _merge_exemptions(plan: Plan, key: Callable[[str], str]) -> dict[tuple[str, str], set[str]]:
    """`(assembly id, path key)` -> the producers whose merge into that path excuses it.

    The exemption is per path, not per pair: an assembly that consumes one
    artifact from a work task has no licence over the rest of that task's
    lease, only over the paths carried by the outputs it actually merges.
    """

    exemptions: dict[tuple[str, str], set[str]] = {}
    for assembly in plan.tasks:
        consumed = {(item.producer_task_id, item.name, item.kind) for item in assembly.inputs}
        for producer in plan.tasks:
            if not _merges(assembly, producer):
                continue
            for output in producer.expected_outputs:
                if (producer.task_id, output.name, output.kind) not in consumed:
                    continue
                for path in output.paths:
                    exemptions.setdefault((assembly.task_id, key(path)), set()).add(producer.task_id)
    return exemptions


def _topological(tasks: dict[str, Task]) -> tuple[tuple[str, ...], bool]:
    indegree = {task_id: 0 for task_id in tasks}
    consumers: dict[str, list[str]] = {task_id: [] for task_id in tasks}
    for task in tasks.values():
        for dependency in task.dependencies:
            if dependency in tasks:
                indegree[task.task_id] += 1
                consumers[dependency].append(task.task_id)
    ready = sorted(task_id for task_id, count in indegree.items() if count == 0)
    ordered: list[str] = []
    while ready:
        task_id = ready.pop(0)
        ordered.append(task_id)
        for consumer in sorted(consumers[task_id]):
            indegree[consumer] -= 1
            if indegree[consumer] == 0:
                ready.append(consumer)
                ready.sort()
    return tuple(ordered), len(ordered) != len(tasks)


def _ancestors(tasks: dict[str, Task]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}

    def visit(task_id: str, pending: set[str]) -> set[str]:
        if task_id in result:
            return result[task_id]
        if task_id in pending:
            return set()
        found: set[str] = set()
        for dependency in tasks[task_id].dependencies:
            if dependency not in tasks:
                continue
            found.add(dependency)
            found.update(visit(dependency, pending | {task_id}))
        result[task_id] = found
        return found

    for task_id in tasks:
        visit(task_id, set())
    return result


def validate_plan(policy: ProjectPolicy, plan: Plan, *, strict: bool = False) -> PlanValidationResult:
    """Validate a proposed plan against a policy, without running anything.

    `strict=True` adds one rule: a success criterion may not be discharged by a
    human gate, so every criterion has to be machine-checkable.
    """

    issues: list[PlanValidationIssue] = []
    tasks = {task.task_id: task for task in plan.tasks}
    templates = {item.template_id for item in policy.command_templates}

    def key(path: str) -> str:
        return _path_key(path, case_sensitive=policy.case_sensitive_paths)

    exclusions = tuple(sorted({key(item) for item in policy.exclusions}))

    def issue(code: str, detail: str, task_id: str | None = None) -> None:
        # A plan may name hundreds of tasks and paths, and `detail` is bounded
        # at 512 characters: bound it here, so a large plan is a result rather
        # than a `ValidationError` raised from inside the validator.
        issues.append(PlanValidationIssue(code=code, task_id=task_id, detail=_bounded(detail)))

    if plan.max_concurrency > policy.max_concurrency:
        issue("concurrency_exceeds_policy", "plan concurrency exceeds project policy")
    if sum(task.attempt_limit for task in plan.tasks) > policy.resource_budget.max_attempts:
        issue(
            "attempt_budget_too_small",
            "mission attempt budget cannot cover every declared task attempt",
        )

    for task in plan.tasks:
        missing = sorted(set(task.dependencies) - set(tasks))
        if missing:
            issue(
                "missing_dependency",
                f"dependencies are absent: {_listing(missing)}",
                task.task_id,
            )
        if task.state != TaskState.QUEUED or task.attempt_count != 0:
            issue("non_initial_task_state", "new plan tasks must be queued", task.task_id)
        if task.attempt_limit > policy.retry_limit + 1:
            issue(
                "attempt_limit_exceeds_policy",
                "attempt limit exceeds policy",
                task.task_id,
            )
        if task.assigned_role not in policy.agent_roles:
            issue("role_not_allowed", "assigned role is not allowlisted", task.task_id)
        if len(task.acceptance_checks) != 1:
            issue(
                "acceptance_check_count_unsupported",
                "this evidence contract requires exactly one acceptance check",
                task.task_id,
            )
        unknown_commands = sorted((set(task.allowed_commands) | set(task.acceptance_checks)) - templates)
        if unknown_commands:
            issue(
                "command_not_allowed",
                f"command templates are absent: {_listing(unknown_commands)}",
                task.task_id,
            )
        for path in task.read_paths:
            refusal = _read_scope_refusal(
                path,
                policy.allowed_read_globs,
                exclusions,
                case_sensitive=policy.case_sensitive_paths,
            )
            if refusal is not None:
                issue(
                    "read_path_not_allowed",
                    f"read path is forbidden: {path} -- {refusal}",
                    task.task_id,
                )
        # A path a task publishes is a path it writes, so it is checked against
        # the policy's write grant and its exclusions like any other write --
        # `write_paths` alone would let an output name a file the policy never
        # granted.
        published = {path for output in task.expected_outputs for path in output.paths}
        for path in sorted(published | set(task.write_paths)):
            if not matches_any(path, policy.allowed_write_globs) or _excluded(key(path), exclusions):
                issue(
                    "write_path_not_allowed",
                    f"write path is forbidden: {path}",
                    task.task_id,
                )
        lease = {key(path) for path in task.write_paths}
        for output in task.expected_outputs:
            if any(key(path) not in lease for path in output.paths):
                issue(
                    "output_outside_write_scope",
                    f"output {output.name} contains a path outside the task lease",
                    task.task_id,
                )
        output_names = tuple(item.name for item in task.expected_outputs)
        if len(output_names) != len(set(output_names)):
            issue(
                "duplicate_output_name",
                "task output names must identify one publication each",
                task.task_id,
            )
        for requirement in task.inputs:
            if requirement.producer_task_id not in task.dependencies:
                issue(
                    "input_without_dependency",
                    f"input producer {requirement.producer_task_id} is not a dependency",
                    task.task_id,
                )
                continue
            producer = tasks.get(requirement.producer_task_id)
            if producer is not None and not any(
                output.name == requirement.name and output.kind == requirement.kind
                for output in producer.expected_outputs
            ):
                issue(
                    "missing_artifact_contract",
                    f"dependency {requirement.producer_task_id} does not publish {requirement.name}",
                    task.task_id,
                )
        input_producers = {item.producer_task_id for item in task.inputs}
        for dependency in task.dependencies:
            if dependency in tasks and dependency not in input_producers:
                issue(
                    "dependency_without_artifact",
                    f"dependency {dependency} has no declared input artifact",
                    task.task_id,
                )

    order, cyclic = _topological(tasks)
    if cyclic:
        issue("cycle", "task dependency graph contains a cycle")
    ancestors = _ancestors(tasks)

    # Every task holds a write lease, not only the work tasks: an assembly that
    # writes a file a work task is writing clobbers that task's lease too. A
    # lease on a directory and a lease on a file inside it are the same race,
    # so a task also *covers* every directory its paths hang off.
    #
    # The report is one finding per contested path rather than one per pair of
    # tasks: a path leased by k tasks is one race, not k(k-1)/2 of them, and a
    # 253-task plan all writing one file used to produce 31,881 findings of the
    # same thing.
    holders: dict[str, dict[str, str]] = {}
    coverers: dict[str, set[str]] = {}
    for task in plan.tasks:
        lease = {key(path): path for path in task.write_paths}
        for item, spelling in lease.items():
            holders.setdefault(item, {})[task.task_id] = spelling
        for item in set(lease) | {ancestor for path in lease for ancestor in _ancestors_of(path)}:
            coverers.setdefault(item, set()).add(task.task_id)
    merged = _merge_exemptions(plan, key)
    position = {task_id: index for index, task_id in enumerate(order)}
    for item, spellings in sorted(holders.items()):
        participants = coverers[item]
        # An assembly is exempt on a path only while every other task racing
        # for it is a producer whose output it merges there. A third task on
        # the same path is a race the assembly is part of again.
        active = {
            task_id for task_id in participants if not merged.get((task_id, item), set()) >= participants - {task_id}
        }
        if len(active) < 2 or not spellings.keys() & active:
            continue
        # Ordered when the tasks form a chain: the ancestor sets are already
        # transitive, so consecutive pairs in topological order decide it.
        chain = sorted(participants, key=lambda task_id: position.get(task_id, len(position)))
        ordered = all(chain[step] in ancestors.get(chain[step + 1], set()) for step in range(len(chain) - 1))
        issue(
            "ordered_write_conflict" if ordered else "parallel_write_conflict",
            f"tasks {_listing(sorted(participants))} overlap write scope: {_listing(sorted(set(spellings.values())))}",
        )

    if not plan.criteria:
        issue("criterion_uncovered", "plan declares no success-criterion coverage")
    for criterion in plan.criteria:
        producers = set(criterion.producer_task_ids)
        if not producers:
            issue(
                "criterion_uncovered",
                "criterion has no producing task",
                criterion.criterion_id,
            )
        missing_producers = sorted(producers - set(tasks))
        if missing_producers:
            issue(
                "criterion_missing_producer",
                f"criterion producers are absent: {_listing(missing_producers)}",
                criterion.criterion_id,
            )
        if criterion.verification_kind == CriterionVerificationKind.MODEL_ASSERTION:
            issue(
                "criterion_model_assertion",
                "a model assertion cannot verify a success criterion",
                criterion.criterion_id,
            )
            continue
        if criterion.verification_kind == CriterionVerificationKind.HUMAN_GATE:
            if strict:
                issue(
                    "criterion_human_gate",
                    "strict mode requires a machine-checkable criterion",
                    criterion.criterion_id,
                )
            if criterion.verifier_task_id is not None or criterion.verifier_id not in policy.risk_gates:
                issue(
                    "criterion_no_verifier",
                    "human verification requires a typed policy gate",
                    criterion.criterion_id,
                )
            continue
        verifier = tasks.get(criterion.verifier_task_id or "")
        if (
            verifier is None
            or verifier.kind != TaskKind.VERIFICATION
            or criterion.verifier_id not in verifier.acceptance_checks
        ):
            issue(
                "criterion_no_verifier",
                "deterministic verification requires a verification task check",
                criterion.criterion_id,
            )
            continue
        if verifier.task_id in producers:
            issue(
                "criterion_self_verification",
                "a producing task cannot verify its own criterion",
                criterion.criterion_id,
            )
        elif any(
            producer in tasks and producer not in ancestors.get(verifier.task_id, set()) for producer in producers
        ):
            issue(
                "criterion_verifier_not_downstream",
                "criterion verifier is not downstream of every producer",
                criterion.criterion_id,
            )

    assemblies = [task for task in plan.tasks if task.kind == TaskKind.ASSEMBLY]
    verifiers = [task for task in plan.tasks if task.kind == TaskKind.VERIFICATION]
    if len(assemblies) != 1:
        issue("assembly_count", "plan requires exactly one assembly task")
    if len(verifiers) != 1:
        issue("verification_count", "plan requires exactly one verification task")
    if len(assemblies) == len(verifiers) == 1:
        assembly, verifier = assemblies[0], verifiers[0]
        required = {task.task_id for task in plan.tasks if task.kind == TaskKind.WORK}
        if not required <= ancestors.get(assembly.task_id, set()):
            issue("assembly_not_reachable", "assembly does not consume every work task")
        if assembly.task_id not in ancestors.get(verifier.task_id, set()):
            issue("verification_not_bound", "verification is not downstream of assembly")
        work_outputs = {
            (task.task_id, output.name, output.kind)
            for task in plan.tasks
            if task.kind == TaskKind.WORK
            for output in task.expected_outputs
        }
        frontier = {(item.producer_task_id, item.name, item.kind) for item in assembly.inputs}
        missing_frontier = sorted(work_outputs - frontier)
        if missing_frontier:
            issue(
                "artifact_frontier_missing",
                "assembly omits work outputs: "
                + _listing([f"{task_id}/{name}" for task_id, name, _ in missing_frontier]),
                assembly.task_id,
            )
        extra_frontier = sorted(frontier - work_outputs)
        if extra_frontier:
            issue(
                "artifact_frontier_ambiguous",
                "assembly contains unsupported frontier inputs",
                assembly.task_id,
            )

        if len(assembly.expected_outputs) != 1:
            issue(
                "assembly_output_shape_unsupported",
                "assembly must publish exactly one candidate patch",
                assembly.task_id,
            )
        elif assembly.expected_outputs[0].kind != "patch":
            issue(
                "assembly_output_kind_unsupported",
                "assembly candidate kind must be patch",
                assembly.task_id,
            )

        expected_candidate = (
            None
            if len(assembly.expected_outputs) != 1
            else (
                assembly.task_id,
                assembly.expected_outputs[0].name,
                assembly.expected_outputs[0].kind,
            )
        )
        verifier_inputs = tuple((item.producer_task_id, item.name, item.kind) for item in verifier.inputs)
        if (
            expected_candidate is None
            or verifier.dependencies != (assembly.task_id,)
            or verifier_inputs != (expected_candidate,)
        ):
            issue(
                "verification_input_shape_unsupported",
                "verification must consume only the exact assembly candidate",
                verifier.task_id,
            )
        if len(verifier.expected_outputs) != 1:
            issue(
                "verification_output_shape_unsupported",
                "verification must publish exactly one receipt",
                verifier.task_id,
            )
        elif verifier.expected_outputs[0].kind != "test-receipt":
            issue(
                "verification_output_kind_unsupported",
                "verification output kind must be test-receipt",
                verifier.task_id,
            )

    canonical_issues = _capped(sorted(issues, key=lambda item: (item.code, item.task_id or "", item.detail)))
    return PlanValidationResult(
        valid=not canonical_issues,
        topological_order=order if not cyclic else (),
        issues=canonical_issues,
    )


def require_valid_plan(policy: ProjectPolicy, plan: Plan, *, strict: bool = False) -> PlanValidationResult:
    """Return the validation result, or raise `PlanValidationError`."""

    result = validate_plan(policy, plan, strict=strict)
    if not result.valid:
        raise PlanValidationError(result)
    return result


def evaluate_plan_policy(
    policy: ProjectPolicy,
    plan: Plan,
    *,
    goal_request_id: str,
    requested_mode: AuthorizationMode,
    requested_finalization_mode: FinalizationMode | None = None,
) -> PlanPolicyDecisionV1:
    """Bind a valid plan to the narrowest effective authorization and result mode."""

    require_valid_plan(policy, plan)
    pre_authorized = (
        requested_mode == AuthorizationMode.POLICY_PRE_AUTHORIZED
        and policy.authorization_mode == AuthorizationMode.POLICY_PRE_AUTHORIZED
    )
    effective_mode = AuthorizationMode.POLICY_PRE_AUTHORIZED if pre_authorized else AuthorizationMode.REVIEW_REQUIRED
    requested_finalization = requested_finalization_mode or policy.finalization_mode
    finalization_mode = (
        FinalizationMode.AUTO_FINALIZE_ISOLATED
        if pre_authorized
        and requested_finalization == FinalizationMode.AUTO_FINALIZE_ISOLATED
        and policy.finalization_mode == FinalizationMode.AUTO_FINALIZE_ISOLATED
        else FinalizationMode.REVIEW_REQUIRED
    )
    reasons = ["plan_within_policy"]
    if requested_mode == AuthorizationMode.REVIEW_REQUIRED:
        reasons.append("review_requested")
    elif not pre_authorized:
        reasons.append("policy_requires_review")
    if finalization_mode == FinalizationMode.AUTO_FINALIZE_ISOLATED:
        reasons.append("isolated_result_pre_authorized")
    elif pre_authorized:
        reasons.append("final_review_required")
    return PlanPolicyDecisionV1.create(
        goal_request_id=goal_request_id,
        requested_mode=requested_mode,
        effective_mode=effective_mode,
        finalization_mode=finalization_mode,
        policy_id=policy.policy_id,
        policy_revision=policy.revision,
        policy_sha256=canonical_json_sha256(policy.model_dump(mode="json")),
        base_sha=policy.base_sha,
        plan_revision=plan.revision,
        plan_sha256=canonical_json_sha256(plan.model_dump(mode="json")),
        reason_codes=tuple(sorted(reasons)),
    )
