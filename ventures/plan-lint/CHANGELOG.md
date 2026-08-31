# Changelog

All notable changes to this project are documented here. This project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 - unreleased

The first release.

- `validate_plan`, `require_valid_plan` and `evaluate_plan_policy`: the plan
  admission gate extracted from [Graphene](https://github.com/Alex-lop/Graphene),
  with 36 typed issue codes covering dependency cycles, out-of-scope reads and
  writes, parallel write-path conflicts, unverifiable or self-asserted success
  criteria, artifact contracts and attempt budgets.
- `load_plan` / `load_policy`: JSON documents natively, YAML through the optional
  `yaml` extra. A document that cannot be read is a refusal naming the reason and
  never a traceback -- neither parse branch names the exception types it has to
  predict, so a failure inside a tag constructor is a refusal like any other -- and
  never the document's own text: a YAML parse failure reports
  the problem with its line and column, not the source line PyYAML quotes, which
  would copy a credential straight into the log. Those reasons include duplicate
  keys, a non-string mapping key, YAML anchors and aliases, CPython's non-JSON
  `NaN` and `Infinity`, a number the interpreter itself will not convert, nesting
  deeper than the parser's stack, anything that is not a regular file, and anything
  over `MAX_DOCUMENT_BYTES`. <!-- claim: test_a_complex_yaml_mapping_key_is_a_document_error, test_a_yaml_refusal_never_echoes_the_line_that_failed, test_a_number_the_interpreter_refuses_is_a_document_error -->
- `agent-plan-lint check|codes|schema` command line, exiting 0 within policy, 1 with
  issues, 2 on a document that cannot be loaded or the command line is wrong.
  `--format json` prints JSON on exit 0, on exit 1 and on a load failure's exit 2;
  a usage error is argparse's own message on stderr and the safety net below is
  one line there, and neither is JSON. An unexpected failure inside the tool is that same exit 2 and one line
  on stderr rather than a traceback and exit 1, which would have told a CI gate
  the plan was merely out of policy. `python -m agent_plan_lint` is the same entry
  point as the console script, so both go through that one safety net.
- `agent_plan_lint.globs.full_match`, a `PurePosixPath.full_match` equivalent for the
  canonical patterns a document can contain -- no empty component, at most 16 of them
  -- used on every supported version, checked against the standard library's behaviour
  on 3.13. An empty component and a pattern past the bound are the two documented
  divergences, and a document carrying either is refused when it loads. <!-- claim: test_the_matcher_claim_states_the_divergence_the_glob_tests_pin, test_no_document_can_carry_a_pattern_the_two_disagree_on -->
- No path component may end in a dot or a space. Windows strips both, so
  `app/token.env.` and `app/token.env` are one file there while every comparison
  here would call them two, which turned a trailing dot into an escape from an
  exclusion and from the write-conflict check. Both spellings are refused when the
  document loads. <!-- claim: test_a_path_component_ending_in_a_dot_or_a_space_is_refused_when_the_document_loads, test_a_trailing_dot_cannot_walk_past_an_exclusion_or_a_write_lease -->
- No path may contain an invisible character. The rule is a Unicode category test
  rather than `str.isprintable`: a code point in a path may not be in the C, Z or M
  general categories -- the ASCII space excepted -- nor in Unicode's
  `Default_Ignorable_Code_Point` set, nor the blank Braille cell. `str.isprintable`
  is only the C and Z half of that, so it admitted every combining mark in the set,
  the variation selectors included; a read scope or a write lease carrying one
  renders character for character like the path without it -- so it walked past an
  exclusion on that subtree, and two tasks leasing the two spellings of `app/api.py`
  were two leases rather than one conflict. The zero-width joiners stay legal in a
  `title`, a `contract` and a `blocker`, where they are orthography rather than a
  file name, and the command line escapes the same set on the way out. What the M
  half costs is the decomposed spelling of an accented path name, and a path in a
  script whose vowel signs are separate code points. <!-- claim: test_an_invisible_character_is_refused_in_a_path_though_it_is_legal_in_text, test_a_zero_width_joiner_cannot_walk_past_an_exclusion_or_a_write_lease, test_a_zero_width_joiner_is_orthography_rather_than_a_forged_line -->
- Exclusions, write leases, lease overlaps and published outputs compare through one
  case-folded, NFC-normalised key, because macOS and Windows call `app/api.py` and `app/API.py` one file; a policy that only
  ever lives on a case-sensitive filesystem sets `case_sensitive_paths: true`. The
  fold is the length-preserving one those filesystems perform, so `app/gruß.py` and
  `app/gruss.py` stay the two files they are everywhere. The policy's read and write grant
  globs match the path as the plan spells it, so a grant written `app/**` does not admit
  `App/api.py` -- the write is refused as `write_path_not_allowed`, not folded into the grant. <!-- claim: test_two_tasks_writing_one_file_under_different_spellings_conflict, test_a_case_sensitive_policy_opts_out_of_the_folding, test_a_write_lease_is_not_folded_by_a_case_fold_no_filesystem_performs -->
- A policy exclusion binds wildcard read scopes: a scope that could reach an
  excluded path is refused rather than granted with a hole in it, because nothing
  downstream of this gate enforces the hole. `docs/schema.md` says what a task
  writes instead. <!-- claim: test_a_wildcard_read_scope_that_can_reach_an_exclusion_is_refused, test_a_wildcard_read_scope_disjoint_from_every_exclusion_is_admitted, test_the_exclusion_example_in_the_disclaimer_list_is_what_the_validator_decides -->
- Text a plan publishes -- a task's `title`, `contract` or `blocker`, a criterion's
  `description` -- is refused when it carries a credential *shape*, and the refusal
  names the field and the shape without echoing the value. Prose about secrets is
  not a shape, and neither is a name: a run of characters is broken by `/`, by
  `_` and by `-` before its entropy is measured, so a branch name, a source path,
  an ADR filename, a release tag and a snake_case migration name are short words
  rather than one long token, and the security tickets this tool's users write
  still load. A value assigned after `secret`, `token`, `password` or `api_key` is
  measured the same way: it is a credential when it carries a provider key prefix
  or a PEM header, or when it runs to 32 characters or more mixing case and
  carrying at least 3 digits, and a shorter one is the *name* of a secret rather
  than a secret -- so `secret = AWS_SECRET_ACCESS_KEY_V2` and
  `SECRET_KEY=change-me-in-prod` both load. <!-- claim: test_text_carrying_a_credential_is_refused_and_the_error_names_the_field, test_ordinary_prose_about_secrets_is_not_a_credential, test_a_secret_name_assigned_a_real_secret_is_still_refused, test_an_environment_variable_name_is_not_the_secret_it_names -->
- Bounds that keep a document inside `MAX_DOCUMENT_BYTES` bounded in work as well as
  in bytes: at most 16 slash-separated segments in a path or a pattern, at most 64
  globs in each of a policy's three path lists, at most 32 distinct wildcard path
  components across a whole policy, and at most 2048 paths named by one plan.
  Crossing any of them is a refusal that says which. The report is bounded too, at
  32 findings per issue code, and one contested write path is one finding naming
  every task racing for it. `tests/test_performance.py` builds the worst document
  those bounds allow and pins it to a two-second budget. <!-- claim: test_every_changelog_bullet_is_one_a_reviewer_listed, test_the_changelog_states_the_bounds_and_the_budget_the_tests_enforce, test_a_worst_case_legal_document_still_validates_inside_a_work_budget -->
- Supported on CPython 3.11, 3.12 and 3.13. One runtime dependency, `pydantic>=2.7`.

Adversarial reviews ran against this package before it was released. What they
found and what changed is recorded in `docs/porting-notes.md` rather than here:
none of it ever reached a user, so none of it is a change to anything.
