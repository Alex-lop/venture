"""Fixtures shared by the tests: one policy and one plan that satisfies it."""

from __future__ import annotations

from agent_plan_lint import (
    ArtifactContract,
    ArtifactRequirement,
    CommandTemplate,
    Criterion,
    CriterionVerificationKind,
    Plan,
    ProjectPolicy,
    ResourceBudget,
    Task,
    TaskKind,
)


def policy() -> ProjectPolicy:
    return ProjectPolicy(
        policy_id="policy-1",
        revision=1,
        repo_id="repo-1",
        base_ref="main",
        base_sha="a" * 40,
        allowed_read_globs=("app/**", "out/**", "tests/**"),
        allowed_write_globs=("app/**", "out/**", "tests/**"),
        command_templates=(
            CommandTemplate(template_id="check", argv=("pytest",), timeout_seconds=60),
            CommandTemplate(template_id="edit", argv=("python", "edit.py"), timeout_seconds=60),
        ),
        agent_roles=("assembler", "verifier", "worker"),
        max_concurrency=4,
        retry_limit=1,
        resource_budget=ResourceBudget(
            max_worker_seconds=600,
            max_attempts=8,
            max_artifact_bytes=1_000_000,
        ),
    )


def task(
    task_id: str,
    output_name: str,
    output_kind: str,
    output_path: str,
    *,
    kind: TaskKind = TaskKind.WORK,
    role: str = "worker",
    dependencies: tuple[str, ...] = (),
    inputs: tuple[ArtifactRequirement, ...] = (),
) -> Task:
    return Task(
        task_id=task_id,
        title=task_id,
        contract=f"Produce {output_name}.",
        kind=kind,
        dependencies=dependencies,
        assigned_role=role,
        read_paths=("app/source.py",),
        write_paths=(output_path,),
        allowed_commands=("edit",),
        inputs=inputs,
        expected_outputs=(ArtifactContract(name=output_name, kind=output_kind, paths=(output_path,)),),
        acceptance_checks=("check",),
        priority=1,
        attempt_limit=2,
    )


def plan() -> Plan:
    work_a = task("work-a", "patch-a", "patch", "app/a.py")
    work_b = task("work-b", "patch-b", "patch", "app/b.py")
    assembly = task(
        "assemble",
        "candidate",
        "patch",
        "out/candidate.patch",
        kind=TaskKind.ASSEMBLY,
        role="assembler",
        dependencies=("work-a", "work-b"),
        inputs=(
            ArtifactRequirement(producer_task_id="work-a", name="patch-a", kind="patch"),
            ArtifactRequirement(producer_task_id="work-b", name="patch-b", kind="patch"),
        ),
    )
    verify = task(
        "verify",
        "verification",
        "test-receipt",
        "out/verification.json",
        kind=TaskKind.VERIFICATION,
        role="verifier",
        dependencies=("assemble",),
        inputs=(ArtifactRequirement(producer_task_id="assemble", name="candidate", kind="patch"),),
    )
    return Plan(
        mission_id="mission-1",
        revision=1,
        criteria=(
            Criterion(
                criterion_id="criterion-checks",
                description="The bound checks pass.",
                producer_task_ids=("work-a", "work-b"),
                verification_kind=CriterionVerificationKind.DETERMINISTIC_CHECK,
                verifier_task_id="verify",
                verifier_id="check",
            ),
        ),
        tasks=tuple(sorted((assembly, verify, work_a, work_b), key=lambda item: item.task_id)),
        max_concurrency=2,
    )


def replace(source: Plan, task_id: str, **updates: object) -> Plan:
    tasks = []
    for item in source.tasks:
        values = item.model_dump(mode="json")
        tasks.append(Task.model_validate({**values, **updates}) if item.task_id == task_id else item)
    return Plan.model_validate({**source.model_dump(mode="json"), "tasks": tasks})


def replace_criterion(source: Plan, **updates: object) -> Plan:
    criterion = source.criteria[0]
    return Plan.model_validate(
        {
            **source.model_dump(mode="json"),
            "criteria": [{**criterion.model_dump(mode="json"), **updates}],
        }
    )
