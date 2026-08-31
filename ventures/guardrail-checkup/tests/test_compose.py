"""What the two sibling packages contribute, and what this tool drafts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from agent_plan_lint import DocumentError, load_policy
from conftest import build_repo, git

from guardrail_checkup import checkup, compose, emit, render_markdown, scan, starter_policy, wrapped_mcp
from guardrail_checkup._compose import PLAN_KEYS, POLICY_KEYS

PLACEHOLDER = "/etc/egresswall/policy.json"


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
    suggestion, wrapped, unwrapped = wrapped_mcp(config, PLACEHOLDER)
    assert suggestion["mcpServers"]["remote"] == config["mcpServers"]["remote"]
    assert suggestion["mcpServers"]["local"]["command"] == "egresswall"
    assert (wrapped, unwrapped) == (("local",), ("remote",))


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
    assert all("\\" in item or item.startswith("./") for item in composed.unpoliceable), composed.unpoliceable
