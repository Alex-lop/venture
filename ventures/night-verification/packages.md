# N1 — hostile release verification — 2026-09-02

Scope: fresh clones of the public `v0.1.0` tags, official GitHub/PyPI endpoints,
clean builds and installs, the shipped demos, doc-truth suites, and adversarial API
inputs. No tag was moved or rewritten.

| Package | Public tag | Clean result | Hostile result |
|---|---|---|---|
| `agent-plan-lint` | object `a5f62df` → commit `2b13942` | 488 tests on 3.13; wheel/sdist and source install pass; 10/10 adversarial cases pass | PyPI JSON and a clean index install return 404 / no distribution |
| `egresswall` | object `26213d3` → commit `45917d4` | 675 tests; wheel/sdist, demo and 17 hostile cases otherwise pass | PyPI is 404; the tag lets a terminal leaf cross `max_total_length`, and `check()` raises while rendering an adversarial mapping key |

The current source trees close every actionable finding:

- Both READMEs now say PyPI publication is pending and install the exact public
  source tag. The plan-lint network release gate still deliberately fails until
  PyPI exists, but it now parses the one truthful install command correctly.
- Egresswall checks the aggregate text budget immediately after every charge,
  stops parent walks after a child exhausts it, and converts an unrenderable key
  into one sanitized `PAYLOAD_TOO_LARGE` finding instead of raising.
- Focused regressions cover exact-cap partitions, final-leaf overruns, parent-loop
  termination, rendered scalars and hostile mapping keys. The full suite remains
  675 tests.

PyPI publication remains externally blocked by ASK-015's rejected credential.
The immutable `v0.1.0` tag documentation therefore remains historical evidence;
the fixed source should receive a new tag only after the index release path works.
