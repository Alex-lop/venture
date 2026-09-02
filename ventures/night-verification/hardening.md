# N4 — property and mutation hardening — 2026-09-02

No runtime or test dependency was added. Both mutation tools ran ephemerally via
`uvx`; deterministic property-style assertions use only the standard library.

## agent-plan-lint

Target: `src/agent_plan_lint/validation.py`, with `tests/test_validation.py` as
the runner. Mutmut 2.4.5 generated 462 mutants.

- Before: 371 killed, 91 survived.
- After: 384 killed, 78 survived — 13 additional decision mutants killed.
- The 78 remaining are documented as acceptable for this targeted campaign:
  61 alter diagnostic/schema presentation rather than acceptance outcomes; 10
  are fail-closed or validity-redundant (`184,209,271,306,312,334,343,353,399,420`);
  four alter synthetic glob strings (`139,145,152,166`); `344` is a sentinel
  collision; and `461–462` are equivalent JSON-mode mutations.

The added assertions exhaust the authorization/finalization mode product and
cover retry limits, dependency/criterion reachability, strict human gates and
root-glob lease conflicts. They are folded into existing tests, so the public
collection remains 488 (437 pass / 51 version-gated skips on Python 3.11).

## egresswall

Targeted mutmut 3.7.0 campaign over the aggregate budget, email, forbidden-value,
path-normalization and budget-state seams: 65 selected, 62 killed, two equivalent
survivors, one timeout, zero untested.

- `_normalize_path__mutmut_1` changes `> 128` to `>= 128`; at exactly 128 the
  result is identical and only cached versus uncached execution changes.
- `_Budget.__init____mutmut_5` changes `False` to `None`; both are falsey until
  every stop path assigns `True`.
- `_forbidden_value__mutmut_12` changes a state-loop `and` to `or` and loops
  forever at state zero. The timeout is a detected behavioral failure, not an
  accepted survivor.

Properties cover all two-letter TLD shapes, a small exhaustive forbidden-value
differential, exact/over text and node budgets, unrenderable keys and long
flattened paths. The full collection remains 675 and passes.
