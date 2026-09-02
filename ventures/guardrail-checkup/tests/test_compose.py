"""What the two sibling packages contribute, and what this tool drafts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from agent_plan_lint import DocumentError, PlanValidationIssue, load_policy
from conftest import build_repo, git

from guardrail_checkup import (
    CANDIDATE_LIMIT,
    CHURN_GLOBS,
    EXCLUSION_GLOBS,
    checkup,
    compose,
    emit,
    render_markdown,
    scan,
    starter_policy,
    wrapped_mcp,
)
from guardrail_checkup._cli import main
from guardrail_checkup._compose import PLAN_KEYS, POLICY_KEYS

PLACEHOLDER = "/etc/egresswall/policy.json"
VERSIONS = {"guardrail-checkup": "0.1.0", "agent-plan-lint": "0.1.0", "egresswall": "0.1.0"}


def _task(task_id: str, kind: str, role: str, dependencies, writes, outputs, inputs=()) -> dict:
    return {
        "task_id": task_id,
        "title": f"Task {task_id}",
        "contract": f"Do {task_id}.",
        "kind": kind,
        "dependencies": list(dependencies),
        "assigned_role": role,
        "read_paths": ["app/api.py"],
        "write_paths": list(writes),
        "allowed_commands": ["pytest"] if kind == "verification" else ["edit"],
        "inputs": list(inputs),
        "expected_outputs": outputs,
        "acceptance_checks": ["pytest"],
        "priority": 1,
        "attempt_limit": 2,
    }


def documents_that_validate_with_issues() -> tuple[dict, dict]:
    """A policy and a plan that load and then fail validation.

    `compose` renders `issue.code` and one field off every issue, and the only
    plan any test carried was `{"mission_id": "m", "tasks": []}`, which is
    refused at load and never validated -- so the whole `validations` path, and
    §2's renderer for it, were never executed by the suite at all.
    """

    policy = {
        "schema_version": 1,
        "policy_id": "p",
        "revision": 1,
        "repo_id": "p",
        "base_ref": "main",
        "base_sha": "0" * 40,
        "allowed_read_globs": ["**"],
        "allowed_write_globs": ["app/**", "db/**", "out/**"],
        "exclusions": ["db/**"],
        "command_templates": [
            {"template_id": "edit", "argv": ["python", "-m", "x"], "timeout_seconds": 300},
            {"template_id": "pytest", "argv": ["pytest", "-q"], "timeout_seconds": 600},
        ],
        "network": {"mode": "deny"},
        "agent_roles": ["assembler", "verifier", "worker"],
        "max_concurrency": 4,
        "retry_limit": 1,
        "resource_budget": {"max_worker_seconds": 1800, "max_attempts": 12, "max_artifact_bytes": 1000000},
        "risk_gates": [],
    }
    plan = {
        "schema_version": 1,
        "mission_id": "m",
        "revision": 1,
        "max_concurrency": 2,
        "criteria": [],
        "tasks": [
            _task(
                "a-assemble",
                "assembly",
                "assembler",
                ["c-work"],
                ["out/candidate.patch"],
                [{"name": "candidate", "kind": "patch", "paths": ["out/candidate.patch"]}],
                [{"producer_task_id": "c-work", "name": "patch-db", "kind": "patch"}],
            ),
            _task(
                "b-verify",
                "verification",
                "verifier",
                ["a-assemble"],
                ["out/verification.json"],
                [{"name": "verification", "kind": "test-receipt", "paths": ["out/verification.json"]}],
                [{"producer_task_id": "a-assemble", "name": "candidate", "kind": "patch"}],
            ),
            # The forbidden write: `db/**` is an exclusion, so this is one issue.
            _task(
                "c-work",
                "work",
                "worker",
                [],
                ["db/queries.py"],
                [{"name": "patch-db", "kind": "patch", "paths": ["db/queries.py"]}],
            ),
        ],
    }
    return policy, plan


def repository_with_a_plan_that_fails(root: Path) -> Path:
    repository = build_repo(root)
    policy, plan = documents_that_validate_with_issues()
    (repository / "policy.json").write_text(json.dumps(policy))
    (repository / "plan.json").write_text(json.dumps(plan))
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "add a policy and a plan")
    return repository


def test_the_issue_fields_this_tool_renders_are_the_fields_the_sibling_declares() -> None:
    """`issue.message` does not exist. Every run over a plan with an issue raised."""

    assert set(PlanValidationIssue.model_fields) == {"code", "task_id", "detail"}


def test_a_plan_with_issues_is_validated_and_every_line_names_its_code(tmp_path: Path) -> None:
    repository = repository_with_a_plan_that_fails(tmp_path / "repo")

    result, composed = checkup(str(repository))

    assert composed.validations, "the validation path is dead code if this is empty"
    codes = {line.split(" — ")[0].split(": ")[-1] for line in composed.validations}
    assert "write_path_not_allowed" in codes, composed.validations
    for line in composed.validations:
        assert line.startswith("plan.json: ")
        assert " — " in line and line.rsplit(" — ", 1)[1]
    body = render_markdown(
        result,
        composed,
        "cmd",
        {"guardrail-checkup": "0", "agent-plan-lint": "0", "egresswall": "0"},
        None,
        "2026-08-31",
    )
    assert "write_path_not_allowed" in body


def test_the_cli_writes_a_report_for_a_repository_whose_plan_has_issues(tmp_path: Path) -> None:
    """The same repository through the console script: exit 0 and a report on disk."""

    repository = repository_with_a_plan_that_fails(tmp_path / "repo")
    out = tmp_path / "checkup.md"

    assert main(["run", str(repository), "--out", str(out)]) == 0
    assert "write_path_not_allowed" in out.read_text(encoding="utf-8")


# --- agent-plan-lint ----------------------------------------------------------


def test_the_drafted_starter_policy_is_a_valid_agent_plan_lint_policy(fixture_repo: Path, tmp_path: Path) -> None:
    result, composed = checkup(str(fixture_repo))
    target = tmp_path / "starter-policy.json"
    target.write_text(composed.drafts["starter-policy.json"])
    policy = load_policy(target)
    assert policy.policy_id == "shipfast"
    assert policy.base_sha == result.head


@pytest.mark.parametrize("shape", ["git", "plain", "empty", "deep"])
def test_every_starter_policy_this_tool_emits_loads(shape: str, tmp_path: Path) -> None:
    """`valid` is the claim on the tin, so it is checked on four shapes of repository."""

    root = tmp_path / shape
    if shape == "git":
        build_repo(root)
    elif shape == "plain":
        (root / "db").mkdir(parents=True)
        (root / "db" / "q.py").write_text("x = 1\n")
    elif shape == "empty":
        root.mkdir()
    else:
        deep = root / "a" / "b" / "c" / "payments" / "d"
        deep.mkdir(parents=True)
        (deep / "charge.py").write_text("x = 1\n")
    result = scan(str(root), 20_000)
    target = tmp_path / f"{shape}.json"
    target.write_text(json.dumps(starter_policy(result)))
    assert load_policy(target).schema_version == 1


def test_the_starter_policy_excludes_the_candidates_and_grants_the_churn(fixture_repo: Path) -> None:
    result = scan(str(fixture_repo), 20_000)
    policy = starter_policy(result)
    assert "db/**" in policy["exclusions"]
    assert policy["allowed_write_globs"] == list(result.churn)


def test_the_starter_policy_excludes_exactly_the_candidates_section_three_names(tmp_path: Path) -> None:
    """More categories match than §3 renders, and both documents say "the §3 candidates".

    Built from `result.candidates` rather than the first `CANDIDATE_LIMIT`, a
    repository matching seven categories got a policy excluding four paths no
    section of the report named.
    """

    repository = tmp_path / "many"
    for relative in (
        "db/queries.py",
        "auth/session.py",
        "payments/charge.py",
        "deploy/main.tf",
        "secrets/keys.py",
        "vendor/lib.py",
    ):
        (repository / relative).parent.mkdir(parents=True, exist_ok=True)
        (repository / relative).write_text("x = 1\n")
    (repository / "uv.lock").write_text("# lock\n")

    result = scan(str(repository), 20_000)
    policy = starter_policy(result)

    assert len(result.candidates) > CANDIDATE_LIMIT, [item.slug for item in result.candidates]
    named = {
        f"{prefix.rstrip('/')}/**" if prefix.endswith("/") else prefix
        for candidate in result.candidates[:CANDIDATE_LIMIT]
        for prefix in candidate.prefixes
    }
    assert set(policy["exclusions"]) == named
    outside = {
        f"{prefix.rstrip('/')}/**" if prefix.endswith("/") else prefix
        for candidate in result.candidates[CANDIDATE_LIMIT:]
        for prefix in candidate.prefixes
    }
    assert outside and not (outside & set(policy["exclusions"])), outside


def test_the_starter_policy_reports_candidate_exclusions_cut_at_its_cap(tmp_path: Path) -> None:
    repository = tmp_path / "many-db-paths"
    for number in range(EXCLUSION_GLOBS + 3):
        path = repository / f"area{number:03d}" / "db" / "query.py"
        path.parent.mkdir(parents=True)
        path.write_text("x = 1\n")

    result = scan(str(repository), 20_000)
    composed = compose(result, PLACEHOLDER)
    policy = json.loads(composed.drafts["starter-policy.json"])
    body = render_markdown(result, composed, "run .", VERSIONS, "drafts", "2026-08-31")

    assert len(policy["exclusions"]) == EXCLUSION_GLOBS
    assert composed.exclusions_cut == 3
    assert composed.to_dict()["candidate_exclusions_cut"] == 3
    assert f"first {EXCLUSION_GLOBS} candidate path globs in sorted order (3 more were cut)" in body


def test_the_starter_policy_falls_back_to_every_top_level_directory_with_no_repair_history(tmp_path: Path) -> None:
    """The README's own showcased run is this case: 0 repair commits, so no churn to grant."""

    repository = tmp_path / "fresh"
    for folder in ("src", "docs", "db"):
        (repository / folder).mkdir(parents=True)
        (repository / folder / "f.py").write_text("x = 1\n")
    git(repository, "init", "-q", "-b", "main")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "initial import")

    result = scan(str(repository), 20_000)

    assert result.repairs == 0 and result.churn == ()
    assert starter_policy(result)["allowed_write_globs"] == ["db/**", "docs/**", "src/**"]


def test_the_starter_policy_says_how_many_churned_directories_it_left_out(tmp_path: Path) -> None:
    """The one cap that decides what an emitted file grants, not what a row says.

    A repository whose repair commits touched a hundred directories was handed a
    policy with CHURN_GLOBS write globs -- so writes in the other thirty-six are
    denied by it -- and no row of the report, no clause in §2 or §4 and nothing
    in the policy said any had been dropped. The globs are the most-churned ones
    now, and §2 states both numbers.
    """

    repository = tmp_path / "churn"
    for number in range(CHURN_GLOBS + 36):
        (repository / f"d{number:03d}").mkdir(parents=True)
        (repository / f"d{number:03d}" / "a.py").write_text("x = 1\n")
    git(repository, "init", "-q", "-b", "main")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "fix: one repair over a hundred directories")

    result = scan(str(repository), 20_000)
    composed = compose(result, PLACEHOLDER)
    policy = json.loads(composed.drafts["starter-policy.json"])
    body = render_markdown(result, composed, "run .", VERSIONS, "drafts", "2026-08-31")

    assert len(policy["allowed_write_globs"]) == CHURN_GLOBS == len(result.churn)
    assert result.churn_cut == 36
    assert f"Its write globs come from the {CHURN_GLOBS} most-churned directories (36 more were cut)." in body
    # And the emitted policy is still one agent-plan-lint loads.
    (tmp_path / "starter-policy.json").write_text(composed.drafts["starter-policy.json"])
    assert load_policy(tmp_path / "starter-policy.json")


def test_the_most_churned_directory_is_the_one_the_policy_keeps(tmp_path: Path) -> None:
    """Cut alphabetically, the policy dropped directories for their names.

    `zz/` touched by every repair commit sorts last, so a set cut at CHURN_GLOBS
    threw away the hottest path in the repository and kept sixty-four cold ones.
    """

    repository = tmp_path / "ranked"
    for number in range(CHURN_GLOBS + 10):
        (repository / f"d{number:03d}").mkdir(parents=True)
        (repository / f"d{number:03d}" / "a.py").write_text("x = 1\n")
    (repository / "zz").mkdir()
    (repository / "zz" / "hot.py").write_text("x = 1\n")
    git(repository, "init", "-q", "-b", "main")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "fix: the first repair")
    for number in range(3):
        (repository / "zz" / "hot.py").write_text(f"x = {number}\n")
        git(repository, "add", "-A")
        git(repository, "commit", "-q", "-m", f"fix: repair {number} in the hot directory")

    result = scan(str(repository), 20_000)

    assert result.churn[0] == "zz/**", result.churn[:3]
    assert result.churn_cut == 11, "seventy-five churned directories, sixty-four globs"


def test_a_checked_in_policy_is_loaded_and_reported_instead_of_drafted(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    result = scan(str(repository), 20_000)
    (repository / "policy.json").write_text(json.dumps(starter_policy(result)))
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "add the policy")
    composed = compose(scan(str(repository), 20_000), PLACEHOLDER)
    assert composed.policies == [("policy.json", "loads: a valid agent-plan-lint policy")]
    assert "starter-policy.json" not in composed.drafts


def test_a_broken_policy_is_reported_by_its_reason_and_not_by_a_traceback(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / "policy.json").write_text('{"policy_id": "x", "allowed_write_globs": ["app/**"]}')
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "add a broken policy")
    composed = compose(scan(str(repository), 20_000), PLACEHOLDER)
    path, status = composed.policies[0]
    assert path == "policy.json"
    assert status.startswith("refused: ")
    with pytest.raises(DocumentError):
        load_policy(repository / "policy.json")


def test_a_plan_without_a_policy_says_so_rather_than_validating_nothing(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / "plan.json").write_text('{"mission_id": "m", "tasks": [], "revision": 1, "max_concurrency": 1}')
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "add a plan")
    composed = compose(scan(str(repository), 20_000), PLACEHOLDER)
    assert composed.plans
    assert "no policy found" in composed.plans[0][1] or "refused" in composed.plans[0][1]


def test_a_json_file_that_is_neither_shape_is_left_alone(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    composed = compose(scan(str(repository), 20_000), PLACEHOLDER)
    assert composed.policies == [] and composed.plans == []
    assert all(key in ("policy_id", "allowed_write_globs") for key in POLICY_KEYS)
    assert all(key in ("mission_id", "tasks") for key in PLAN_KEYS)


# --- egresswall ---------------------------------------------------------------


def test_a_checked_in_fixture_is_screened_and_the_report_never_carries_the_value(fixture_repo: Path) -> None:
    _, composed = checkup(str(fixture_repo))
    path, violations = composed.screened[0]
    assert path == "tests/fixtures/support_reply.json"
    assert any(item.startswith("RAW_IDENTIFIER") for item in violations)
    assert any(item.startswith("FORBIDDEN_KEY") for item in violations)
    blob = " ".join(violations)
    assert "member-88231@northgate-clinic.test" not in blob
    assert "sk-proj-EXAMPLE" not in blob


def test_the_wrapped_mcp_configuration_puts_the_proxy_in_front_of_every_server(fixture_repo: Path) -> None:
    _, composed = checkup(str(fixture_repo))
    wrapped = json.loads(composed.drafts["mcp-wrapped.json"])
    servers = wrapped["mcpServers"]
    assert composed.wrapped == ("support-tools", "warehouse")
    assert composed.unwrapped == ()
    assert set(servers) == {"support-tools", "warehouse"}
    for entry in servers.values():
        assert entry["command"] == "egresswall"
        assert entry["args"][:3] == ["proxy", "--policy", PLACEHOLDER]
        assert "--" in entry["args"]
    assert servers["support-tools"]["args"][-3:] == ["python", "-m", "support_tools"]


def test_a_remote_server_is_carried_through_untouched_and_counted_as_unwrapped() -> None:
    """A stdio proxy cannot screen a server the agent reaches over the network."""

    config = {
        "mcpServers": {
            "remote": {"type": "http", "url": "https://example.invalid/mcp"},
            "local": {"command": "node", "args": ["s.js"]},
        }
    }
    suggestion, wrapped, unwrapped, already = wrapped_mcp(config, PLACEHOLDER)
    assert suggestion["mcpServers"]["remote"] == config["mcpServers"]["remote"]
    assert suggestion["mcpServers"]["local"]["command"] == "egresswall"
    assert wrapped == ("local",)
    assert already == ()
    assert [name for name, _ in unwrapped] == ["remote"]
    assert "over the network" in unwrapped[0][1]


def test_an_entry_with_no_command_and_no_url_is_not_called_a_network_server() -> None:
    """The inventory row prints "no command and no url"; the suggestion said "network"."""

    config = {"mcpServers": {"empty": {"type": "stdio"}, "remote": {"url": "https://example.invalid/mcp"}}}
    _, wrapped, unwrapped, _ = wrapped_mcp(config, PLACEHOLDER)

    assert wrapped == ()
    reasons = dict(unwrapped)
    assert reasons["empty"] == "this entry configures no command to wrap"
    assert "over the network" in reasons["remote"]


def test_a_server_already_running_a_screen_is_not_wrapped_a_second_time() -> None:
    """§2 reports it as screened; the suggestion put a second proxy in front of it."""

    config = {
        "mcpServers": {
            "screened": {"command": "egresswall", "args": ["proxy", "--", "node", "s.js"]},
            "bare": {"command": "node", "args": ["s.js"]},
        }
    }
    suggestion, wrapped, unwrapped, already = wrapped_mcp(config, PLACEHOLDER)

    assert (wrapped, unwrapped, already) == (("bare",), (), ("screened",))
    assert suggestion["mcpServers"]["screened"] == config["mcpServers"]["screened"]
    assert suggestion["mcpServers"]["screened"]["args"].count("proxy") == 1


def test_a_server_whose_command_line_is_not_all_strings_is_not_rebuilt() -> None:
    """`str()` on a JSON object writes a Python repr into a shell argument."""

    config = {"mcpServers": {"odd": {"command": "node", "args": [1, {"a": 1}]}}}
    suggestion, wrapped, unwrapped, already = wrapped_mcp(config, PLACEHOLDER)

    assert (wrapped, already) == ((), ())
    assert [name for name, _ in unwrapped] == ["odd"]
    assert "not all strings" in unwrapped[0][1]
    assert suggestion["mcpServers"]["odd"] == config["mcpServers"]["odd"]
    assert "{'a': 1}" not in json.dumps(suggestion)


def test_the_report_says_how_many_servers_could_not_be_wrapped(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".mcp.json").write_text(
        '{"mcpServers": {"remote": {"type": "http", "url": "https://mcp.example.invalid/sse"},'
        ' "local": {"command": "node", "args": ["s.js"]}}}'
    )
    result, composed = checkup(str(repository))
    body = render_markdown(
        result,
        composed,
        "cmd",
        {"guardrail-checkup": "0", "agent-plan-lint": "0", "egresswall": "0"},
        None,
        "2026-08-31",
    )
    assert "in front of 1 of 2 server(s)" in body
    assert "`remote`" in body
    assert "in front of each server" not in body


def test_a_repository_with_no_mcp_configuration_gets_no_suggestion(tmp_path: Path) -> None:
    repository = build_repo(tmp_path / "repo")
    (repository / ".mcp.json").unlink()
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "drop the mcp config")
    _, composed = checkup(str(repository))
    assert "mcp-wrapped.json" not in composed.drafts


# --- emitting -----------------------------------------------------------------


def test_emit_writes_every_draft_and_makes_the_hooks_executable(fixture_repo: Path, tmp_path: Path) -> None:
    _, composed = checkup(str(fixture_repo))
    written = emit(composed.drafts, tmp_path / "drafts")
    assert {item.name for item in written} == {Path(name).name for name in composed.drafts}
    for item in written:
        assert item.exists()
        if item.suffix == ".py":
            assert item.stat().st_mode & 0o111


# --- a policy over hostile paths ------------------------------------------------


#: Path components a repository may legally contain and a policy glob may not,
#: next to ones it may: agent-plan-lint refuses a backslash, a control or bidi
#: character and a leading `./`, and accepts every glob metacharacter.
HOSTILE = (
    "back\\slash",
    "a\nb",
    "gp\u202egnp",
    "zero\u200bwidth",
    "sp ace",
    "q?mark",
    "[bracket",
    "**star",
    "!neg",
    "..x",
    # The three shapes the hand-written filter missed. agent-plan-lint refuses a
    # component ending in a dot or a space -- Windows strips both, so
    # `token.env.` and `token.env` are one file there -- and U+00A0 with the
    # rest of the invisible set. The emitted policy was invalid and §2 said
    # nothing had been left out.
    "dot.",
    "trailing ",
    "n\u00a0bsp",
)


def test_every_starter_policy_loads_even_over_a_repository_of_hostile_paths(tmp_path: Path) -> None:
    """The README says a test loads every policy this tool emits. This is the hard half."""

    root = tmp_path / "hostile"
    (root / "db").mkdir(parents=True)
    (root / "db" / "queries.py").write_text("x = 1\n")
    for name in HOSTILE:
        (root / name).mkdir()
        (root / name / "f.py").write_text("x = 1\n")
    _, composed = checkup(str(root))
    target = tmp_path / "policy.json"
    target.write_text(composed.drafts["starter-policy.json"])
    policy = load_policy(target)
    assert policy.schema_version == 1
    assert any("star" in item for item in policy.allowed_write_globs), policy.allowed_write_globs
    assert composed.unpoliceable, "the paths a policy cannot carry are reported, not silently dropped"
    # Every shape above that a policy cannot carry is named, including the three
    # a regular expression over backslashes and control characters never saw.
    for name in ("dot.", "trailing ", "n\u00a0bsp", "back\\slash"):
        assert any(item.startswith(name) for item in composed.unpoliceable), (name, composed.unpoliceable)
    # And the ones it can are still granted.
    assert not any(item.startswith(("q?mark", "[bracket", "!neg", "..x")) for item in composed.unpoliceable)


def test_a_policy_that_sorts_past_the_listing_cap_is_still_found(tmp_path: Path) -> None:
    """`--max-files` bounds the work, not the truth -- the rule the inventory already follows.

    The signature scan read the `--max-files` slice, so a repository whose only
    checked-in policy sorted past the cap was told "No document in
    agent-plan-lint's schema was found" as a fact about the repository, and a
    starter policy was drafted over the top of the one it has.
    """

    policy, _ = documents_that_validate_with_issues()
    repository = tmp_path / "capped"
    repository.mkdir()
    (repository / "aaa.json").write_text("{}\n")
    (repository / "zz-policy.json").write_text(json.dumps(policy))

    result = scan(str(repository), 1)
    composed = compose(result, PLACEHOLDER)

    assert result.truncated
    assert [path for path, _ in composed.policies] == ["zz-policy.json"]
    assert "starter-policy.json" not in composed.drafts
    body = render_markdown(result, composed, "cmd", VERSIONS, None, "2026-08-31")
    assert "No document in agent-plan-lint's schema was found" not in body


def test_a_ranking_off_a_capped_listing_says_the_listing_was_capped(tmp_path: Path) -> None:
    """§3 is the one section that reads the `--max-files` slice, so it says so."""

    repository = tmp_path / "capped-rank"
    (repository / "db").mkdir(parents=True)
    (repository / "aaa.txt").write_text("x\n")
    (repository / "db" / "queries.py").write_text("x\n")

    result = scan(str(repository), 1)
    body = render_markdown(result, compose(result, PLACEHOLDER), "cmd", VERSIONS, None, "2026-08-31")

    assert result.truncated
    assert "Listing capped at 1; 1 file(s) were not scanned for a candidate path" in body
