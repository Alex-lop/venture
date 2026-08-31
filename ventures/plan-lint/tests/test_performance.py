"""MAX_DOCUMENT_BYTES has to bound the work, not only the bytes.

A policy's globs and exclusions are matched against every path a plan names,
pair by pair, so a document well inside the size cap can name hundreds of
thousands of pairs. Four bounds keep that finite, and the shapes below sit on
all of them at once:

* `MAX_PLAN_PATHS` -- how many paths one plan may name at all;
* `MAX_POLICY_GLOBS` -- how many globs a policy may list in each of its three
  path lists, so a path is matched a bounded number of times;
* `MAX_PATH_SEGMENTS` -- how deep one path or pattern goes, which is how many
  steps one match costs;
* `MAX_POLICY_WILDCARDS` -- how many *distinct* components a policy may use
  that are neither a literal name nor `*` nor `**`, which is the only kind
  whose mask costs a scan of the path.

The last shape is the expensive one: it spends the whole wildcard budget on
components that match every segment of every path, arranges them so no two
neighbours repeat, and puts the component that fails at the far end, so every
pair pays for the full dynamic program before it is rejected. It also fills
the exclusion list to its cap, so every path is matched twice over.

The budget is deliberately loose: it is a work bound, not a benchmark, and it
has to hold on the slowest runner in the matrix. `docs/schema.md` states every
bound above; `tests/test_docs.py` checks that it still states the right ones.
"""

from __future__ import annotations

import itertools
import json
import random
import time

import pytest

from agent_plan_lint import DocumentError, Plan, ProjectPolicy, load_plan, load_policy, validate_plan
from agent_plan_lint.globs import MAX_PATH_SEGMENTS, MAX_POLICY_WILDCARDS
from agent_plan_lint.loading import MAX_DOCUMENT_BYTES
from agent_plan_lint.models import MAX_PLAN_PATHS, MAX_POLICY_GLOBS
from conftest import plan as _plan
from conftest import policy as _policy
from conftest import replace
from conftest import task as _task

BUDGET_SECONDS = 2.0
_DEPTH = MAX_PATH_SEGMENTS - 1


def _universal(count: int) -> list[str]:
    """Distinct components that match every segment the shapes below name."""

    letters = "bcdefghijklmnopqrstuvwxy"
    return ["[az" + "".join(pair) + "]*" for pair in itertools.permutations(letters, 2)][:count]


def _spread(pool: list[str], width: int, count: int, tail: str) -> list[str]:
    """`count` distinct globs, each `width` components from `pool`, none repeating a neighbour."""

    generator = random.Random(7)
    chosen: set[str] = set()
    while len(chosen) < count:
        chosen.add("/".join(generator.sample(pool, width)) + tail)
    return sorted(chosen)


def _distinct_wildcards() -> tuple[list[str], list[str], object]:
    """The whole wildcard budget spent on components that match everything."""

    pool = _universal(MAX_POLICY_WILDCARDS - 2)
    width = MAX_PATH_SEGMENTS - 2
    globs = _spread(pool, width, MAX_POLICY_GLOBS, "/z*/[az]*")
    exclusions = _spread(pool, width, MAX_POLICY_GLOBS, "/[az]*/z*")
    return (
        globs,
        exclusions,
        lambda task, index: (
            "/".join(f"a{task}{index:03d}{part:02d}" for part in range(_DEPTH)) + f"/z{task}{index:03d}"
        ),
    )


#: Each shape defeats one shortcut: no `**` run collapses, no first component is
#: a literal the matcher can index on, every component is a wildcard that has to
#: be matched against every segment, or -- the last -- no component's mask can
#: be reused from its neighbour.
SHAPES = {
    "runs of **": (
        [("**/x*/" * (_DEPTH // 2)) + f"z{index:03d}" for index in range(MAX_POLICY_GLOBS)],
        [("**/y*/" * (_DEPTH // 2)) + f"w{index:03d}" for index in range(MAX_POLICY_GLOBS)],
        lambda task, index: "a/" * _DEPTH + f"f{task:02d}{index:03d}",
    ),
    "every component a *": (
        ["*/" * _DEPTH + f"z{index:03d}" for index in range(MAX_POLICY_GLOBS)],
        ["*/" * _DEPTH + f"w{index:03d}" for index in range(MAX_POLICY_GLOBS)],
        lambda task, index: (
            "/".join(f"g{task}{index}{part:02d}" for part in range(_DEPTH)) + f"/f{task:02d}{index:03d}"
        ),
    ),
    "character classes": (
        [("[a-z]*/" * _DEPTH) + f"z{index:03d}" for index in range(MAX_POLICY_GLOBS)],
        [("[a-z]*/" * _DEPTH) + f"w{index:03d}" for index in range(MAX_POLICY_GLOBS)],
        lambda task, index: (
            "/".join(f"s{task}{index}{part:02d}" for part in range(_DEPTH)) + f"/f{task:02d}{index:03d}"
        ),
    ),
    "distinct wildcards": _distinct_wildcards(),
}


def _worst_case(globs: list[str], exclusions: list[str], path) -> tuple[ProjectPolicy, Plan]:
    """A policy at every list bound, and a plan at the path bound that reads nothing twice."""

    policy = ProjectPolicy.model_validate(
        {
            **_policy().model_dump(mode="json"),
            "allowed_read_globs": tuple(sorted(globs)),
            "allowed_write_globs": tuple(sorted(globs)),
            "exclusions": tuple(sorted(exclusions)),
        }
    )
    base = _plan().model_dump(mode="json")
    extra = [
        _task(f"work-x{index:02d}", f"patch-x{index:02d}", "patch", f"app/x{index:02d}.py").model_dump(mode="json")
        for index in range(4)
    ]
    plan = Plan.model_validate({**base, "tasks": sorted(base["tasks"] + extra, key=lambda item: item["task_id"])})
    for task, item in enumerate(plan.tasks):
        plan = replace(plan, item.task_id, read_paths=tuple(sorted(path(task, index) for index in range(253))))
    return policy, plan


@pytest.mark.parametrize("shape", sorted(SHAPES), ids=lambda name: name.replace(" ", "-"))
def test_a_worst_case_legal_document_still_validates_inside_a_work_budget(shape: str) -> None:
    policy, plan = _worst_case(*SHAPES[shape])
    named = sum(
        len(task.read_paths) + len(task.write_paths) + sum(len(item.paths) for item in task.expected_outputs)
        for task in plan.tasks
    )
    documents = (
        len(json.dumps(policy.model_dump(mode="json"))),
        len(json.dumps(plan.model_dump(mode="json"))),
    )

    started = time.perf_counter()
    result = validate_plan(policy, plan)
    elapsed = time.perf_counter() - started

    assert all(size < MAX_DOCUMENT_BYTES for size in documents), documents
    assert named > MAX_PLAN_PATHS - 16, named
    assert max(len(item.split("/")) for item in plan.tasks[0].read_paths) == MAX_PATH_SEGMENTS
    assert not result.valid
    assert elapsed < BUDGET_SECONDS, f"{elapsed:.1f}s for documents of {documents} bytes naming {named} paths"


def test_the_worst_shape_spends_the_whole_wildcard_budget() -> None:
    """The shape above is only worst-case while it sits on the bound it is testing."""

    from agent_plan_lint.globs import wildcard_components

    globs, exclusions, _ = SHAPES["distinct wildcards"]

    assert len(globs) == len(exclusions) == MAX_POLICY_GLOBS
    assert len(wildcard_components(tuple(globs) + tuple(exclusions))) == MAX_POLICY_WILDCARDS


def test_a_policy_over_the_wildcard_budget_is_refused_by_name() -> None:
    """One more distinct wildcard component than the bound, and the policy will not load."""

    document = _policy().model_dump(mode="json")
    document["allowed_read_globs"] = sorted({f"app/w{index:03d}*/x.py" for index in range(MAX_POLICY_WILDCARDS + 1)})

    assert len(json.dumps(document)) < MAX_DOCUMENT_BYTES
    with pytest.raises(DocumentError, match=f"at most {MAX_POLICY_WILDCARDS} distinct wildcard"):
        load_policy(document)


def test_a_policy_at_the_wildcard_budget_still_loads() -> None:
    document = _policy().model_dump(mode="json")
    document["allowed_read_globs"] = sorted({f"app/w{index:03d}*/x.py" for index in range(MAX_POLICY_WILDCARDS)})

    assert load_policy(document).allowed_read_globs


def test_a_plan_that_names_more_paths_than_the_bound_is_refused_by_name() -> None:
    """The bound is what the budget above rests on, so crossing it is a clean refusal."""

    base = _plan().model_dump(mode="json")
    wide = [
        _task(f"work-y{index:02d}", f"patch-y{index:02d}", "patch", f"app/y{index:02d}.py").model_dump(mode="json")
        for index in range(9)
    ]
    for task, item in enumerate(wide):
        item["read_paths"] = sorted(f"app/f{task:02d}{index:03d}.py" for index in range(256))
    document = {**base, "tasks": sorted(base["tasks"] + wide, key=lambda item: item["task_id"])}

    assert len(json.dumps(document)) < MAX_DOCUMENT_BYTES
    with pytest.raises(DocumentError, match=f"at most {MAX_PLAN_PATHS} paths"):
        load_plan(document)


def test_a_path_deeper_than_the_bound_is_refused_by_name() -> None:
    document = _plan().model_dump(mode="json")
    document["tasks"][0]["read_paths"] = ["a/" * MAX_PATH_SEGMENTS + "f.py"]

    with pytest.raises(DocumentError, match=f"more than {MAX_PATH_SEGMENTS} segments"):
        load_plan(document)


def test_a_policy_that_lists_more_globs_than_the_bound_is_refused() -> None:
    """The second factor in the budget: how many patterns each path is matched against."""

    document = _policy().model_dump(mode="json")
    document["allowed_read_globs"] = sorted(f"app/d{index:03d}/**" for index in range(MAX_POLICY_GLOBS + 1))

    with pytest.raises(DocumentError, match="at most 64 items"):
        load_policy(document)
