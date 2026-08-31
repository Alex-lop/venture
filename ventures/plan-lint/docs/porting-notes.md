# Porting notes

`agent-plan-lint` is the plan admission gate from
[Graphene](https://github.com/Alex-lop/Graphene) (Apache-2.0), extracted so it can
be used without adopting Graphene's runtime. The engine
(`backend/graphene/orchestration/validation.py`), the models it needs
(`orchestration/mission_models.py`, `core_models.py`), the canonical hash
(`hashing.py`) and the test suite
(`tests/unit/orchestration/test_validation.py`) were ported. This page lists every
place where the port is not a copy. <!-- claim: test_the_porting_notes_match_what_was_actually_dropped_and_added -->

## Dropped, because it means nothing outside Graphene

| Dropped | Why |
| --- | --- |
| `Task.evidence_adapter` and the `legacy_adapter_unavailable` code | The field chose between Graphene's `generic_v1` evidence contract and a demo-fixture `legacy_auth_v2` adapter. Outside that runtime there is no adapter registry to be unavailable, so both the field and its issue code are gone. Its ported test went with it. |
| `ProjectPolicy.retention` (`retain_days`, `retain_failed_attempts`) | A retention window for Graphene's event store. The validator never read it, and this package has no store, so requiring it would have made every policy carry a meaningless field. |
| Graphene's event-payload safety machinery (`_safe_payload_key`, the forbidden-key lists) | It guards mission *events*, which this package does not have. The value-level secret scan it shares is kept and narrowed: a task's `title`, `contract` or `blocker`, and a criterion's `description`, are refused when they carry one of the credential shapes listed in `docs/schema.md`, because those strings get quoted into logs and tickets. Graphene's broader rule -- any sentence containing `password:` or a home-directory path -- was dropped, because it refuses the security tickets this package's users write. |
<!-- claim: test_the_porting_notes_match_what_was_actually_dropped_and_added -->

## Added

| Added | Why |
| --- | --- |
| `agent_plan_lint.globs.full_match` | Graphene runs on Python 3.13 and calls `PurePosixPath.full_match`, which does not exist on 3.11 or 3.12. This package supports 3.11+, so the matcher is reimplemented and used on every version -- identical behaviour everywhere, rather than only on the newest interpreter. It is checked against a table captured from CPython 3.13, and re-derived from the standard library whenever the suite runs on 3.13 (`tests/test_globs.py`). |
| `--strict` and `criterion_human_gate` | Graphene accepts a criterion discharged by a named human gate. Some operators want the stronger rule -- every criterion machine-checkable -- so `validate_plan(..., strict=True)` adds that one issue code. Nothing else changes between the two modes. |
| `load_plan` / `load_policy`, and the CLI | Graphene loads plans through its mission store and its `plan_yaml` codec. A standalone linter needs a file in and an exit code out. The YAML codec's strictness is kept: duplicate keys and anchors/aliases are refused, because last-key-wins would silently drop half of an edited plan. |
| JSON as the native format | Graphene's editable projection is YAML. Here PyYAML is an optional extra (`pip install 'agent-plan-lint[yaml]'`) and JSON needs no dependency at all, which keeps the runtime dependency list at exactly one entry. |
<!-- claim: test_the_optional_extra_sentence_is_the_extra_the_metadata_declares, test_human_gate_criterion_passes_by_default_and_fails_under_strict -->

## What the test suite does not cover on every version

`tests/test_globs.py` checks the matcher against a table captured from CPython
3.13 on 3.11, 3.12 and 3.13, and re-derives that table from
`PurePosixPath.full_match` only on 3.13, where that method exists. So `pytest -q`
reports 488 passed on 3.13 and 437 passed, 51 skipped on 3.11 and 3.12: the 51
are the differential checks against the standard library, not missing coverage,
and a green 3.11-only run has not compared the matcher with an independent
oracle. The hand-written table runs on every version. <!-- claim: test_the_documented_test_counts_are_the_counts_pytest_reports -->

## Kept, deliberately

- Every other issue code, with Graphene's exact wording and semantics. <!-- claim: test_every_emitted_code_is_documented_and_every_documented_code_is_emitted -->
- The shape rules that look Graphene-specific but are the reason the gate is
  decidable: exactly one assembly task, exactly one verification task, the
  verification consuming exactly the assembly's candidate, and exactly one
  acceptance check per task. A plan that does not have a single merge point and a
  single verification point cannot be checked for "does every criterion have a
  verifier downstream of every producer", which is the question the gate exists to
  answer. <!-- claim: test_final_stage_shape_matches_runtime_protocol -->
- `evaluate_plan_policy` and `PlanPolicyDecisionV1`: the digest that binds a
  validated plan to the policy, the base commit and the resulting authorization
  mode. It is what makes "this plan was approved" a checkable statement rather than
  a memory.
- Determinism: issues come back sorted by `(code, task_id, detail)`, so two runs
  over the same documents produce the same bytes.

## Hardening before the first release

Adversarial reviews ran against this package before anything was published.
None of what they found ever reached a user, so none of it is in `CHANGELOG.md`;
it is here because the reasoning is worth keeping and the code carries the tests.

- **Documents.** A document is refused rather than misread: duplicate keys in JSON
  as well as YAML, YAML anchors and aliases refused in the composer where they are
  produced (the loader claimed to refuse them and did not), CPython's non-JSON
  `NaN` / `Infinity` literals, an integer literal past CPython's 4300-digit
  conversion limit, nesting deeper than the parser's stack, a read bounded by
  `MAX_DOCUMENT_BYTES` rather than by the size of the file behind it, and only ever
  a regular file -- a validator pointed at a FIFO used to block until the writer
  closed. Neither parse branch names the exception types it has to predict, so a
  failure inside a tag constructor -- `!!timestamp "not-a-time"`, `!!bool "x"`,
  `!!int ""` -- is a refusal like any other rather than a traceback out of
  `load_plan`. Every one of them is exit 2, in the format the caller asked for. <!-- claim: test_a_complex_yaml_mapping_key_is_a_document_error, test_a_number_the_interpreter_refuses_is_a_document_error, test_an_endless_source_is_refused_by_name_rather_than_read, test_a_tag_whose_value_cannot_be_converted_is_a_document_error, test_no_tagged_scalar_leaves_the_loader_as_anything_but_a_document_error -->
- **Paths and text.** Path and text fields refuse control characters *and*
  bidirectional formatting characters, at the parse boundary rather than in the
  report, so a library consumer that formats findings itself gets the guard too.
  The CLI escapes the same set on the way out for text that never went through a
  model. <!-- claim: test_control_characters_are_refused_in_paths_and_in_public_text, test_a_character_that_hides_text_is_refused_wherever_u200b_is -->
- **Comparisons.** Every path comparison goes through one normalisation, so a path
  cannot mean one thing to one check and another to the next. An exclusion covers
  what is inside it and the path its subtree hangs off. A published output is
  checked against the policy's write globs, not only against the task's own lease.
  Write leases are compared between every pair of tasks, not work tasks only, and
  a lease on a directory collides with a lease on anything inside it. The
  assembly's merge exemption is per path, not per task pair. <!-- claim: test_an_exclusion_holds_against_a_respelled_path, test_an_output_path_the_policy_never_granted_is_refused, test_a_directory_lease_and_a_file_lease_inside_it_conflict -->
- **Read scopes.** A wildcard scope is granted when a policy glob provably covers
  it, so a task asking for less than it was granted is admitted; and it is refused
  when it could reach an exclusion, because comparing the scope's *spelling*
  against the exclusion let `read_paths: ["app/secr*/**"]` walk into
  `exclusions: ["app/secrets/**"]`.
- **Work bounds.** Glob matching is a dynamic program carried in one integer, a bit
  per path offset, with the ends compared one segment at a time before the loop
  runs and each component's mask computed once per path. Successive reviews each
  found a document inside the caps that ran far past the budget; the caps in
  `docs/schema.md` -- 16 segments, 64 globs per list, 32 distinct wildcard
  components, 2048 paths -- are where they are because they are what makes the
  worst document those bounds allow finish well inside the budget
  `tests/test_performance.py` pins.
- **Text that is not a secret.** The entropy heuristic measured a run before
  breaking it, so `feature/AB-1234-refactor-user-profile-service` and
  `src/main/java/com/example/App2024Service.java` were refused as credentials --
  a load failure, exit 2, on a plan whose only sin was naming a file. `/`, `_` and
  `-` now break a run before it is measured; the prefixed shapes still catch every
  prefixed credential, and what stays refused -- an unbroken CamelCase run past the
  threshold carrying three digits -- is written down in `docs/schema.md`. The zero-width non-joiner and joiner came out of the
  unprintable class for the same reason: they are orthography in Persian, Urdu
  and Devanagari and the spelling of a multi-part emoji, not a way to forge a
  line of output. <!-- claim: test_ordinary_prose_about_secrets_is_not_a_credential, test_a_snake_case_name_is_a_name_rather_than_a_credential, test_an_unbroken_camel_case_run_with_three_digits_is_still_refused -->
- **A refusal that quoted the document.** `MarkedYAMLError.__str__` embeds a
  snippet of the offending source line, so an unparseable plan printed its own
  content -- an AWS key id included -- to stderr and into `--format json`. The
  YAML branch now reports the problem and its line and column and never
  interpolates the parser's own string. <!-- claim: test_a_yaml_refusal_never_echoes_the_line_that_failed -->
- **Windows path spellings.** `_path_key` folded case because Windows and macOS
  do; Windows also strips a trailing dot or space off a component, so
  `app/token.env.` walked past an exclusion on `app/token.env` and `app/api.py.`
  raced `app/api.py` without a conflict. Both spellings are refused at the parse
  boundary rather than folded, because on Linux they are two real files.
- **The pages themselves.** A doc-truth test that asserts a fixed list of phrases
  cannot see a *new* claim, so fabricated sentences were added to these pages
  and the suite stayed green. Every number in the prose of `README.md`,
  `CHANGELOG.md`, this page and `docs/schema.md` is now swept and has to be
  accounted for by a constant, by the metadata, by the CI matrix or by an explicit
  set a reviewer edits -- in words as well as in digits, inside an inline code
  span as well as outside one, and on
  `docs/comparison.md` and `CONTRIBUTING.md` too; a sentence that says the
  package *catches*, *checks*, *refuses*, *rejects*, *validates*, *verifies*,
  *detects*, *enforces*, *blocks*, *ensures*, *guarantees*, *supports*, *ships*
  or *reports* something, or says *never*, *always* or *every*, has to carry a
  marker naming the test that backs it;
  the README's `##` sections and every whole
  bullet of its disclaimer list and of the changelog are pinned as tuples; the wheel metadata's
  `description` may not use a verb the disclaimer list disclaims; the supported
  Python versions are the CI matrix and nothing else; and every quotation on
  `docs/comparison.md` is checked against `docs/comparison-quotes.txt`, which
  `scripts/refresh-comparison.sh` writes out of the pages it fetched, so a
  fabricated quotation fails CI offline instead of waiting for a release. Each
  quotation is bound to the page its own row cites, and each row of each table is
  bound to a tool-and-URL pair the manifest records, because a fabricated row and
  a real sentence moved into a neighbouring row are both untrue statements about
  a named third party. `CONTRIBUTING.md` lists what the suite still misses, and
  that list is pinned by a test of its own. <!-- claim: test_no_number_in_the_prose_of_a_page_is_unaccounted_for, test_every_block_that_makes_a_claim_names_the_test_that_backs_it, test_every_quotation_is_one_the_refresh_script_found_on_a_page_the_page_cites -->
- **The command line's own failures.** A YAML mapping key that is a list or a
  map reached the duplicate-key guard's hash before PyYAML could refuse it, so
  an unhashable key left the loader as a `TypeError`: a traceback on stderr and
  exit 1, which tells a CI gate reading the exit contract that the plan was
  merely out of policy. Such a key is now refused by name, `TypeError` joined
  the loader's except tuple, and every entry point wraps its work in one safety
  net: an unexpected exception is the documented exit 2 and one line, with a
  hidden `--traceback` for debugging this package rather than using it. <!-- claim: test_a_complex_yaml_mapping_key_is_a_document_error, test_an_unexpected_failure_is_the_documented_error_exit_and_one_line, test_both_entry_points_go_through_the_same_safety_net -->
- **Names that are not keys.** The entropy heuristic broke a run on `/` and `-`
  but not on `_`, so an underscore-joined migration or test name carrying a year
  was refused as a credential. `_` breaks a run too, and the run length is far
  above any identifier a person types. Two invisible-character gaps closed with
  it: the unprintable class now covers every character that renders as nothing
  rather than only the zero-width space, and `_path_key` folds case the way a
  filesystem does rather than with full folding, which had made `gruß.py` and
  `gruss.py` one lease. <!-- claim: test_a_snake_case_name_is_a_name_rather_than_a_credential, test_a_character_that_hides_text_is_refused_wherever_u200b_is, test_a_write_lease_is_not_folded_by_a_case_fold_no_filesystem_performs -->
- **Invisible characters in a path, and names that are not values.** The
  zero-width joiners were kept legal because they are orthography, and the same
  expression guarded a path: `app/secrets<U+200C>/key.pem` renders like
  `app/secrets/key.pem`, walked past an exclusion on that subtree, and made the
  two spellings of one lease two leases. A path now goes through a Unicode
  category rule instead -- no C, Z or M category, nothing in
  `Default_Ignorable_Code_Point`, no blank Braille cell, and the ASCII space the
  one exception -- because `str.isprintable`, which the first fix used, is only
  the C and Z half of that and still admitted every variation selector and the
  combining grapheme joiner. The text fields keep the joiners. The credential scan lost the other half of the
  same confusion: the value written after `secret=` had only to be a short run of
  identifier characters, so `secret = AWS_SECRET_ACCESS_KEY_V2` and
  `token = settings.OAUTH2_TOKEN` failed to load at all. The value is now
  measured the way a token run is -- a provider prefix, a PEM header, or 32
  characters mixing case with three digits -- and the separators do not break
  it, because what follows `secret=` is one field. <!-- claim: test_an_invisible_character_is_refused_in_a_path_though_it_is_legal_in_text, test_a_zero_width_joiner_cannot_walk_past_an_exclusion_or_a_write_lease, test_an_environment_variable_name_is_not_the_secret_it_names, test_a_secret_name_assigned_a_real_secret_is_still_refused, test_the_264_code_points_str_isprintable_admitted_are_refused_in_a_path, test_a_combining_grapheme_joiner_cannot_walk_past_an_exclusion_or_a_write_lease -->
- **Reports.** An issue detail names at most 8 ids and is truncated to the 512
  characters the model allows; at most 32 findings are listed per issue code; and
  one contested write path is one finding rather than one per pair of tasks, which
  is what turned a wide plan's report from a body no hook could read into a bounded
  one. Those three numbers are the constants in `validation.py` and
  `tests/test_docs.py` fails when this line and the code disagree. <!-- claim: test_the_schema_doc_states_the_report_bounds_the_validator_enforces, test_a_code_that_fires_on_every_task_is_reported_up_to_a_bound_and_then_counted -->
