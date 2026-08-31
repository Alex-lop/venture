# The two documents

`agent-plan-lint` reads two documents: a **policy**, which an operator writes and changes
rarely, and a **plan**, which an agent proposes for every mission. Both are JSON
(or YAML with the `yaml` extra). Both refuse unknown fields, so a typo is an error
rather than a silently ignored setting, and both are frozen once loaded. <!-- claim: test_an_unknown_field_names_itself, test_issues_are_sorted_and_the_result_is_frozen -->

`agent-plan-lint schema` prints the generated JSON Schema for each. This page is the
prose version, and `tests/test_docs.py` fails if it drifts from the models.

## Policy

The grant. Everything a task may read, write, run or spend has to be inside it.

| Field | Meaning |
| --- | --- |
| `schema_version` | `1` (the default) or `2`. A schema-1 policy is always review-required; a schema-2 policy must state `authorization_mode` and `finalization_mode` explicitly. |
| `policy_id` | Name of this policy. |
| `revision` | Integer from 1 up, bumped whenever the policy changes. |
| `repo_id` | The repository this policy governs. |
| `base_ref` | The branch or ref plans are written against, e.g. `main`. |
| `base_sha` | The exact 40-character commit the policy is pinned to. A plan validated against one base is not validated against another. |
| `allowed_read_globs` | Sorted, unique path globs a task may read, at most 64 of them. `**` matches any run of directories; `*` and `?` and `[seq]` stay inside one segment. A glob, like a path, may have at most 16 slash-separated components; a deeper one is refused when the document loads. A glob that does not end in `**` grants exact paths only, plus a wildcard scope spelled exactly like the glob itself: no *narrower* wildcard scope is decidable under it, because nothing decides containment between two arbitrary patterns. So `app/*.py` grants `app/*.py` and refuses `app/*`. Write `app/**` rather than `app/**/*.py` if tasks are to declare scopes. |
| `allowed_write_globs` | Sorted, unique path globs a task may write, at most 64 of them. |
| `exclusions` | Globs carved back out of both, at most 64 of them, e.g. `app/secrets/**`. An exclusion covers what is inside it and the path it hangs off: with `exclusions: ["app/secrets"]` no task may write `app/secrets/key.pem`, and with `exclusions: ["app/secrets/**"]` none may write `app/secrets` itself, which would replace the subtree. Exclusions are matched on a case-folded, NFC-normalised key -- `app/SECRETS.py` is the same file as `app/secrets.py` on macOS and on Windows -- while the two allow lists above are matched exactly. **A wildcard read scope that could reach an exclusion is refused**, not granted with a hole in it: nothing downstream of this gate enforces the hole, so `exclusions: ["app/secrets/**"]` refuses `read_paths: ["app/**"]`, `["app/*"]` and `["app/secr*/**"]` alike. Two globs are treated as disjoint only when the literal directories they sit under diverge, so `read_paths: ["app/src/**"]` stays allowed and narrowing the scope past the excluded directory is what a task writes instead. An exclusion whose first component is a wildcard -- `**/.env`, `*.pem` -- sits under no directory at all, so it refuses *every* wildcard read scope in every plan; write it under a literal prefix, or accept that tasks name exact read paths. |
| `case_sensitive_paths` | `false` (the default) compares every path -- exclusions, write leases, lease overlaps, published outputs -- on a case-folded, NFC-normalised key, because macOS and Windows call `app/api.py` and `app/API.py` one file. `true` opts out of the folding for a repository that only ever lives on a case-sensitive filesystem; NFC normalisation still applies. |
| `command_templates` | The frozen argv the agent may run, at most 64 of them; a task can only name one of these by id. |
| `network` | `{"mode": "deny"}` (the default) or `{"mode": "allowlist", "allowed_hosts": [...]}`. Recorded and bound, not enforced by this package. |
| `agent_roles` | Sorted, unique role names a task may be assigned. |
| `max_concurrency` | Upper bound on the plan's own `max_concurrency`. |
| `retry_limit` | Retries per task; a task's `attempt_limit` may not exceed `retry_limit + 1`. |
| `resource_budget` | The mission-wide ceiling (below). |
| `risk_gates` | Named human gates a criterion may cite, e.g. `release-review`. |
| `authorization_mode` | `review_required` (default) or `policy_pre_authorized`; schema-2 only. |
| `finalization_mode` | `review_required` (default) or `auto_finalize_isolated`; schema-2 only, and only when the policy is pre-authorized and carries no `final-result` gate. |
<!-- claim: test_the_schema_doc_describes_the_case_folding_switch_the_policy_has, test_a_wildcard_read_scope_that_can_reach_an_exclusion_is_refused, test_schema_one_policy_bytes_remain_legacy_review_required -->

### `command_templates[]`

| Field | Meaning |
| --- | --- |
| `template_id` | The id a task cites in `allowed_commands` or `acceptance_checks`. |
| `argv` | The exact argument vector. `argv[0]` is refused when its basename is a shell -- `bash`, `sh`, `zsh`, `dash`, `ksh`, `csh`, `tcsh`, `fish`, `cmd`, `powershell`, `pwsh`, `env`, `eval`, `xargs` -- on any spelling of the path, case, or `.exe` suffix. This is a **typo guard, not a containment boundary**: `python -c` is a shell too, and no list of names closes that. What contains a template is the policy that decides which templates exist at all. |
| `timeout_seconds` | 1 to 3600 seconds. |
| `cwd` | Optional repository-relative working directory. |

### `resource_budget`

| Field | Meaning |
| --- | --- |
| `max_worker_seconds` | Wall-clock ceiling for the mission. |
| `max_attempts` | Ceiling on the sum of every task's `attempt_limit`. A plan whose attempts cannot fit is rejected before it starts. |
| `max_artifact_bytes` | Ceiling on one published artifact. |
<!-- claim: test_plan_requires_global_budget_for_declared_retry_limits -->

### `network`

| Field | Meaning |
| --- | --- |
| `mode` | `deny` or `allowlist`. |
| `allowed_hosts` | Sorted, unique hosts; must be empty when the mode is `deny`. |

## Plan

The proposal. Three or more tasks, exactly one of them the assembly and exactly one
the verification, plus the criteria that say what success means.

| Field | Meaning |
| --- | --- |
| `schema_version` | `1`. |
| `mission_id` | The mission this plan belongs to. |
| `revision` | Integer from 1 up. |
| `previous_revision` | Absent for revision 1; otherwise exactly `revision - 1`, so revisions form a chain. |
| `criteria` | What the mission has to achieve, and what proves it. |
| `tasks` | 3 to 256 tasks, with sorted unique ids. Across the whole plan the tasks may name at most 2048 paths, counting every `read_paths`, `write_paths` and output path: each one is matched against every policy glob and exclusion, so the bound is what keeps a document inside `MAX_DOCUMENT_BYTES` bounded in work as well as in bytes. |
| `max_concurrency` | How many tasks may run at once; bounded by the policy. |
<!-- claim: test_the_schema_doc_states_the_bounds_the_models_enforce, test_a_plan_that_names_more_paths_than_the_bound_is_refused_by_name -->

### `criteria[]`

| Field | Meaning |
| --- | --- |
| `criterion_id` | Name of the criterion. |
| `description` | One sentence a person can read. Same text rules as a task's `title`. |
| `producer_task_ids` | The tasks whose work this criterion is about. |
| `verification_kind` | `deterministic_check` (a verification task's check), `human_gate` (a named policy gate), or `model_assertion` (the agent's own word, which is always rejected). |
| `verifier_task_id` | For a deterministic check: the verification task that proves it. Must be empty for a human gate. |
| `verifier_id` | The check id inside that task, or the policy `risk_gates` entry for a human gate. |
<!-- claim: test_plan_rejects_checks_the_completion_receipt_cannot_prove, test_human_gate_criterion_passes_by_default_and_fails_under_strict -->

### `tasks[]`

| Field | Meaning |
| --- | --- |
| `schema_version` | `1`. |
| `task_id` | Name of the task; unique in the plan. |
| `title` | Short label. Like every text field below it, it may not contain control or bidirectional formatting characters, and it is refused when it contains something *shaped* like a credential (see **Text that is refused**). |
| `contract` | What this task is responsible for, in one or two sentences. Same text rules as `title`. |
| `kind` | `work`, `assembly` or `verification`. |
| `dependencies` | Task ids that must finish first. Each one must also supply an entry in `inputs`. |
| `assigned_role` | A role from the policy's `agent_roles`. |
| `read_paths` | Paths or globs this task reads. At most 16 slash-separated segments each, and no segment may end in a dot or a space: Windows strips those, so `app/api.py.` and `app/api.py` are one file there and would be two leases here. Both spellings are refused when the document loads. Every code point in a path must also be one a reviewer can see and count: its Unicode general category may not begin with C (control, format, surrogate, private use, unassigned), Z (separator) or M (combining mark), it may not be in Unicode's `Default_Ignorable_Code_Point` set, and `U+2800`, the blank Braille cell, is refused by name. The ASCII space is the one exception, so `app/my notes.py` is a path and `app/notes /a.py` is not. `app/secrets<U+200C>/key.pem` and `app/sec<U+034F>rets/key.pem` render character for character like `app/secrets/key.pem` and would otherwise walk past an exclusion on that subtree; `str.isprintable`, which this rule replaced, is only the C and Z half of it and admitted every variation selector. What the M half costs is the decomposed spelling of an accented name -- write `app/café.py` composed -- and a path in a script whose vowel signs are separate code points. Those characters stay legal in `title`, `contract` and `blocker`, where they are orthography. An exact path must match one of the policy's `allowed_read_globs` and miss every exclusion; a wildcard scope must be provably inside one granted glob -- decided for a scope under the literal prefix of a `**`-terminated glob, so `app/*`, `app/sub/**` and `app/**/*.py` are all inside `app/**`, and every scope is inside the bare `**` -- *and* provably unable to reach any exclusion. A refusal is `read_path_not_allowed`, and its detail says which of the three reasons applied. |
| `write_paths` | Exact paths this task writes -- no wildcards, because a lease has to be comparable with another task's lease. Same path rules as `read_paths`. Two tasks holding the same path is `parallel_write_conflict` or, when the tasks form a chain in the dependency graph, `ordered_write_conflict`; the one exception is the assembly task over the exact paths carried by the work outputs it consumes, which it exists to merge -- the rest of that work task's lease is still a conflict. A contested path is **one** finding naming every task racing for it, not one finding per pair. A lease on a directory collides with a lease on anything inside it. Paths are compared on the key `case_sensitive_paths` selects. |
| `allowed_commands` | Command template ids this task may run. |
| `inputs` | Artifacts consumed from other tasks (below). |
| `expected_outputs` | Artifacts this task publishes (below). |
| `acceptance_checks` | Exactly one command template id: the check that decides whether the task's own output is acceptable. |
| `priority` | -1000 to 1000; scheduling hint only. |
| `state` | `queued` in a new plan. Any other state is a plan that has already run. |
| `attempt_limit` | 1 to 20, and at most the policy's `retry_limit + 1`. |
| `attempt_count` | `0` in a new plan. |
| `retry_at` | Only set while the state is `retrying`. |
| `blocker` | Only set while the state is `blocked` or `needs_input`. Same text rules as `title`. |
<!-- claim: test_control_characters_are_refused_in_paths_and_in_public_text, test_text_carrying_a_credential_is_refused_and_the_error_names_the_field, test_an_invisible_character_is_refused_in_a_path_though_it_is_legal_in_text, test_a_zero_width_joiner_cannot_walk_past_an_exclusion_or_a_write_lease, test_every_default_ignorable_code_point_is_refused_in_a_path, test_the_264_code_points_str_isprintable_admitted_are_refused_in_a_path, test_a_combining_mark_is_refused_in_a_path_and_stays_legal_in_text, test_a_space_inside_a_file_name_is_still_a_path -->

### `tasks[].expected_outputs[]`

| Field | Meaning |
| --- | --- |
| `name` | The publication identity, unique within the task. |
| `kind` | A free label, except that the assembly must publish `patch` and the verification `test-receipt`. |
| `paths` | Sorted, unique exact paths. Each must be in the task's `write_paths`, and each is checked against the policy's `allowed_write_globs` and `exclusions` like any other write, so an output cannot publish a file the policy never granted. |
<!-- claim: test_an_output_path_the_policy_never_granted_is_refused -->

### `tasks[].inputs[]`

| Field | Meaning |
| --- | --- |
| `producer_task_id` | The task that publishes it; must also be in `dependencies`. |
| `name` | The output name published by that task. |
| `kind` | The output kind published by that task. |

## Text that is refused

`title`, `contract`, `blocker` and a criterion's `description` are quoted back
into logs, tickets and review UIs, so a document is refused when one of them
contains a credential *shape*. The refusal names the field and the shape and
never echoes the value. The shapes are: <!-- claim: test_text_carrying_a_credential_is_refused_and_the_error_names_the_field, test_the_schema_doc_states_the_credential_thresholds_the_models_enforce -->

| Shape | Example |
| --- | --- |
| A PEM private key block | `-----BEGIN RSA PRIVATE KEY-----` |
| A bearer token of 16 characters or more | `Authorization: Bearer eyJhbGciOi...` |
| A provider key prefix | `sk-`, `AKIA`, `AIza`, `ghp_`, `xoxb-` |
| A password inside a URL | `https://user:pass@host/repo` |
| A path into a credential store | `~/.ssh/`, `.aws/`, `.gnupg/`, `.netrc`, `/var/run/secrets/` |
| A secret name assigned a token-shaped value, where the value is measured the way a token run is -- a provider key prefix, a PEM header, or 32 characters or more mixing case with at least 3 digits -- except that `/`, `_`, `.` and `-` do *not* break it, because what follows `secret=` is one field | `password=Sup3r-Secret-Value-99-aBcDeFgHiJkLmN` |
| A long high-entropy token: 32 characters or more, unbroken, with upper case, lower case and at least 3 digits. A run is broken by `/`, by `_` and by `-` before it is measured, so a branch name, a source path, an ADR filename and a release tag are runs of short words rather than one long token | a generated API key |

Prose is not a shape, and neither is a name -- including the name written where
a secret would go. "Rotate the DB password: use the
vault", "Move the `api_key = os.environ` lookup into settings",
"Rename secret = AWS_SECRET_ACCESS_KEY_V2 in the terraform module",
"Move the token = settings.OAUTH2_TOKEN lookup into config.",
"Set secret=REDACTED_PLACEHOLDER_1 in the fixture",
"Ship the compose file with SECRET_KEY=change-me-in-prod",
"Point the worker at DATABASE_URL=postgres://db:5432/app", a 40-character
commit SHA, "Merge branch feature/AB-1234-refactor-user-profile-service",
"Refactor src/main/java/com/example/App2024Service.java to drop the singleton"
and "Cut release SBOM-2024-11-03-Release-Candidate and attach it" all load,
because a gate that refuses the security tickets its users write is a gate they
turn off. The cost of that floor is the other direction: a short password
assigned in prose -- `password=hunter2` -- is read as a name and loads. `tests/test_validation.py` holds every one of those sentences. <!-- claim: test_every_accepted_prose_example_is_a_sentence_the_validator_test_accepts, test_ordinary_prose_about_secrets_is_not_a_credential -->

What the heuristic still refuses is an unbroken run past that threshold that
carries three digits and mixes case with no separator in it at all --
`FeatureFlagRolloutStage2Cohort3Batch4` is refused, and so is a CamelCase class
name long enough to cross the threshold with a year in it --
`CheckoutSessionTokenRefresher2026Service` -- because the year in it satisfies
the digit test on its own. Nothing distinguishes either from a
generated key without giving up the unprefixed-key catch. Break such a
name with `/`, `_` or `-` and it loads. <!-- claim: test_an_unbroken_camel_case_run_with_three_digits_is_still_refused, test_a_snake_case_name_is_a_name_rather_than_a_credential -->

## Bounds

Every path a plan names is matched against every glob and every exclusion in
the policy, so a document inside `MAX_DOCUMENT_BYTES` (1 MiB) has to be bounded
in work as well as in bytes. The bounds below do that, and crossing any of them is a
refusal that says which one was crossed. <!-- claim: test_the_schema_doc_states_the_bounds_the_models_enforce, test_a_worst_case_legal_document_still_validates_inside_a_work_budget -->

| Bound | Value |
| --- | --- |
| Bytes read from one document | 1048576 |
| Segments in one path or components in one pattern | 16 |
| Globs in each of a policy's three path lists | 64 |
| Distinct *wildcard* components across a whole policy -- components that are neither a literal name nor `*` nor `**` | 32 |
| Paths one plan may name in total | 2048 |

`tests/test_performance.py` builds the worst legal document those bounds allow
and pins validating it to a two-second budget.

One more bound applies to the report rather than the document: at most 32
findings are listed per issue code, followed by one line counting the rest, so a
wide plan comes back as a bounded result rather than a multi-megabyte one. Each
finding's `detail` names at most 8 items and is truncated to 512 characters.

## A minimal valid pair

One work task, one assembly, one verification, one criterion the verification proves.

```json
{
  "policy_id": "demo",
  "revision": 1,
  "repo_id": "demo",
  "base_ref": "main",
  "base_sha": "0000000000000000000000000000000000000000",
  "allowed_read_globs": ["src/**"],
  "allowed_write_globs": ["src/**"],
  "command_templates": [
    {"template_id": "test", "argv": ["pytest"], "timeout_seconds": 60}
  ],
  "agent_roles": ["agent"],
  "max_concurrency": 1,
  "retry_limit": 0,
  "resource_budget": {
    "max_worker_seconds": 600,
    "max_attempts": 3,
    "max_artifact_bytes": 100000
  }
}
```

```json
{
  "mission_id": "demo",
  "revision": 1,
  "max_concurrency": 1,
  "criteria": [
    {
      "criterion_id": "it-works",
      "description": "The suite passes.",
      "producer_task_ids": ["edit"],
      "verification_kind": "deterministic_check",
      "verifier_task_id": "verify",
      "verifier_id": "test"
    }
  ],
  "tasks": [
    {
      "task_id": "assemble",
      "title": "assemble",
      "contract": "Merge the work output into one candidate.",
      "kind": "assembly",
      "dependencies": ["edit"],
      "assigned_role": "agent",
      "read_paths": ["src/app.py"],
      "write_paths": ["src/candidate.patch"],
      "allowed_commands": ["test"],
      "inputs": [{"producer_task_id": "edit", "name": "patch", "kind": "patch"}],
      "expected_outputs": [
        {"name": "candidate", "kind": "patch", "paths": ["src/candidate.patch"]}
      ],
      "acceptance_checks": ["test"],
      "priority": 0,
      "attempt_limit": 1
    },
    {
      "task_id": "edit",
      "title": "edit",
      "contract": "Change the application.",
      "kind": "work",
      "dependencies": [],
      "assigned_role": "agent",
      "read_paths": ["src/app.py"],
      "write_paths": ["src/app.py"],
      "allowed_commands": ["test"],
      "inputs": [],
      "expected_outputs": [
        {"name": "patch", "kind": "patch", "paths": ["src/app.py"]}
      ],
      "acceptance_checks": ["test"],
      "priority": 0,
      "attempt_limit": 1
    },
    {
      "task_id": "verify",
      "title": "verify",
      "contract": "Run the suite against the candidate.",
      "kind": "verification",
      "dependencies": ["assemble"],
      "assigned_role": "agent",
      "read_paths": ["src/app.py"],
      "write_paths": ["src/receipt.json"],
      "allowed_commands": ["test"],
      "inputs": [
        {"producer_task_id": "assemble", "name": "candidate", "kind": "patch"}
      ],
      "expected_outputs": [
        {"name": "receipt", "kind": "test-receipt", "paths": ["src/receipt.json"]}
      ],
      "acceptance_checks": ["test"],
      "priority": 0,
      "attempt_limit": 1
    }
  ]
}
```
