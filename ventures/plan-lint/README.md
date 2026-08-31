# agent-plan-lint

**Reject an agent's plan before anything runs.** Your agent proposes a plan; your
project has a policy. `agent-plan-lint` decides, statically, whether the plan fits inside
the policy — dependency cycles, writes outside the allowed paths, two parallel tasks
writing the same file, success criteria the agent would grade itself on, attempt
budgets that do not add up — and exits non-zero with a typed code per finding.

```
pip install agent-plan-lint
```

Or from source:

```
uv pip install git+https://github.com/Alex-lop/agent-plan-lint
```

## 60 seconds

A plan with a cycle, a write outside the policy's paths, two tasks fighting over one
file, and a criterion the model marks for itself:

```console
$ agent-plan-lint check demo/plan-bad.json --policy demo/policy.json
invalid: 4 issues in demo/plan-bad.json
  criterion_model_assertion [criterion-checkout-works]: a model assertion cannot verify a success criterion
  cycle: task dependency graph contains a cycle
  parallel_write_conflict: tasks work-api, work-models overlap write scope: app/api.py
  write_path_not_allowed [work-tests]: write path is forbidden: docs/guide.md
```

The same mission, repaired:

```console
$ agent-plan-lint check demo/plan-good.json --policy demo/policy.json
ok: demo/plan-good.json is within demo/policy.json
order: work-api -> work-models -> work-tests -> assemble -> verify
```

Exit status is `0` when the plan is within policy, `1` when it is not, and `2` when a
document cannot be loaded, the command line is wrong, or the tool itself fails
unexpectedly — so it drops into CI or an admission hook as-is. Add
`--format json` for the machine-readable result, and `--strict` to also reject
criteria that a human, rather than a check, would sign off.

In Python:

```python
from agent_plan_lint import load_plan, load_policy, require_valid_plan

require_valid_plan(load_policy("policy.json"), load_plan("plan.json"))
```

## What it catches

Every finding is one of these codes; `agent-plan-lint codes` prints them with their meanings. <!-- claim: test_the_readme_lists_exactly_the_codes_the_validator_can_emit -->

```console
$ agent-plan-lint codes | wc -l
36
```

| What goes wrong | Codes |
| --- | --- |
| The task graph is not a DAG | `cycle`, `missing_dependency` |
| Two tasks write the same path — the assembly excepted, over the outputs it merges | `parallel_write_conflict`, `ordered_write_conflict` |
| A task steps outside the policy's paths | `read_path_not_allowed`, `write_path_not_allowed`, `output_outside_write_scope` |
| The plan spends more than the policy grants | `concurrency_exceeds_policy`, `attempt_budget_too_small`, `attempt_limit_exceeds_policy` |
| A task uses a command or role the policy never granted | `command_not_allowed`, `role_not_allowed` |
| A success criterion proves nothing | `criterion_model_assertion`, `criterion_self_verification`, `criterion_no_verifier`, `criterion_uncovered`, `criterion_missing_producer`, `criterion_verifier_not_downstream`, `criterion_human_gate` |
| Artifacts between tasks do not line up | `missing_artifact_contract`, `input_without_dependency`, `dependency_without_artifact`, `duplicate_output_name`, `artifact_frontier_missing`, `artifact_frontier_ambiguous` |
| The merge and verification stages are not a shape a runtime can execute | `assembly_count`, `assembly_not_reachable`, `assembly_output_shape_unsupported`, `assembly_output_kind_unsupported`, `verification_count`, `verification_not_bound`, `verification_input_shape_unsupported`, `verification_output_shape_unsupported`, `verification_output_kind_unsupported`, `acceptance_check_count_unsupported` |
| A task is not in the state a fresh plan starts in | `non_initial_task_state` |
<!-- claim: test_the_catches_table_says_what_a_reviewer_listed_and_nothing_else, test_the_readme_lists_exactly_the_codes_the_validator_can_emit, test_every_emitted_code_is_documented_and_every_documented_code_is_emitted -->

`docs/schema.md` describes every field of a plan and a policy; `agent-plan-lint schema`
prints the JSON Schema for both. <!-- claim: test_every_field_of_every_document_model_is_documented, test_the_schema_doc_documents_no_field_that_does_not_exist -->

## What it does not do

- It does not execute, spawn, or sandbox anything. There is no subprocess in the package.
- It does not open a socket. There is no network client in the package.
- It does not read the files your plan names — only the plan and policy documents you point it at.
- It does not rewrite or repair a plan. There is no `--fix`.
- It does not watch a directory or run as a daemon. There is no `--watch`.
- It has no plugin system and no config file. There is no `--config`; the policy document is the configuration.
- It does not carve a hole in a scope. A wildcard read scope that could reach an
  excluded path is refused rather than narrowed, because nothing downstream of this
  gate enforces the hole — so `exclusions: ["app/secrets/**"]` refuses
  `read_paths: ["app/**"]`, and a task asks for `app/src/**` instead. <!-- claim: test_the_exclusion_example_in_the_disclaimer_list_is_what_the_validator_decides -->
- It does not accept an unbounded document. A path or a glob may be 16 segments deep,
  a policy may list 64 globs in each of its three path lists and spend 32 distinct
  wildcard path components, a plan may name 2048 paths, and a document may be 1 MiB;
  `docs/schema.md` has the table and every refusal names the bound it crossed. <!-- claim: test_the_readme_states_the_bounds_the_code_enforces, test_a_policy_over_the_wildcard_budget_is_refused_by_name -->
- It does not enforce anything. The verdict is an exit status and a report; what
  stops a run is the hook, the CI job or the person that reads it. <!-- claim: test_the_package_never_executes_anything_or_opens_a_socket, test_the_readme_names_the_exit_statuses_the_cli_actually_uses -->
- It does not know whether the work is a good idea. It checks the plan against the policy, nothing else. <!-- claim: test_every_bullet_of_the_disclaimer_list_still_disclaims_something, test_the_package_never_executes_anything_or_opens_a_socket -->

## How it is tested

```console
$ python -m pytest --collect-only -q | grep -c ::
488
```

Those tests run on CPython 3.11, 3.12 and 3.13, on Ubuntu and macOS, in the CI
matrix in `.github/workflows/ci.yml`; `scripts/check.sh` runs the same steps
locally. 51 of them re-derive the glob table from the standard library and run
only on 3.13, where `PurePosixPath.full_match` exists; on 3.11 and 3.12 the same
table is checked as a captured fixture, so those runs report 51 skips. They
include:

- the validator suite ported from the source repository, adapted to this schema
  (`tests/test_validation.py`);
- the CLI, driven as a subprocess, including the demo script's output compared byte
  for byte with `demo/OUTPUT.txt` (`tests/test_cli.py`);
- `agent_plan_lint.globs.full_match`, which stands in for `PurePosixPath.full_match`
  (new in 3.13) and is used on every supported version, so the matching is identical on
  3.11, 3.12 and 3.13; checked against a table captured from CPython 3.13 on every
  version and re-derived from the standard library itself when the suite runs on 3.13
  (`tests/test_globs.py`). It implements those semantics for the patterns a document
  can contain -- no empty component, at most 16 of them; an empty component such as
  `**/` is the one shape where the two disagree, and a pattern past the bound raises
  where the standard library returns a bool, both of which `docs/schema.md` refuses at
  load; <!-- claim: test_the_matcher_claim_states_the_divergence_the_glob_tests_pin, test_no_document_can_carry_a_pattern_the_two_disagree_on -->
- this README, `CHANGELOG.md` and the two pages in `docs/`: the codes above, the
  commands and their output, the "does not do" list, and the version, all asserted
  against the code -- and every number in their prose swept, so a number, a section
  or a disclaimer bullet that nothing in the package accounts for fails the suite
  (`tests/test_readme_truth.py`, `tests/test_docs.py`); <!-- claim: test_no_number_in_the_prose_of_a_page_is_unaccounted_for, test_every_block_that_makes_a_claim_names_the_test_that_backs_it, test_the_readme_has_exactly_the_sections_this_file_checks -->
- `docs/comparison.md`: every page it cites is listed in `docs/comparison-sources.txt`,
  every star count names the repository it was read from, and every quotation it
  prints is in `docs/comparison-quotes.txt`, the archive
  `scripts/refresh-comparison.sh` writes from the pages it fetched
  (`tests/test_comparison_truth.py`); that script re-fetches those pages before a
  release and re-checks every quotation, every star count against `gh api`,
  and both install targets above; <!-- claim: test_every_page_the_comparison_cites_was_captured, test_every_star_count_names_the_repository_it_was_read_from, test_every_quotation_is_one_the_refresh_script_found_on_a_page_the_page_cites -->
- the built wheel, installed into a fresh virtual environment and run
  (`tests/test_packaging.py`).

The only runtime dependency is `pydantic>=2.7`. YAML plans need the optional `yaml`
extra; JSON needs nothing.

```console
$ agent-plan-lint --version
agent-plan-lint 0.1.0
```

## Where it came from

This is the plan admission gate from
[Graphene](https://github.com/Alex-lop/Graphene) (Apache-2.0), a publication-control
layer for parallel coding agents, where it sits between a model-proposed plan and a
fenced, parallel execution: no plan runs until it validates against the project
policy. The engine, its issue codes, and its test suite are ported here; what was
specific to Graphene's runtime was dropped and is listed in `docs/porting-notes.md`. <!-- claim: test_the_provenance_of_the_port_carries_dated_evidence -->

Graphene's release rule is inherited with it: a claim in a README that no test can
back is deleted rather than softened. `tests/test_readme_truth.py` is that rule
applied to this file.

## Comparison

`docs/comparison.md` — what the policy engines, agent frameworks and tool-call
guardrails on that page do that this does not, and the other way round.

## License

Apache-2.0. Copyright 2026 Alexander Lopez.
