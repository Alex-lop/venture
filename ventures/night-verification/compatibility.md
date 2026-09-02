# N5 — supported-Python compatibility — 2026-09-02

Fresh public-tag clones were tested with uv-managed CPython 3.11, 3.12 and 3.13.
Declared classifiers, `requires-python` and the CI axes agree for both packages.

| Package | 3.11 | 3.12 | 3.13 | Build/install/demo |
|---|---:|---:|---:|---|
| `agent-plan-lint` | 437 pass / 51 intentional skips | 437 / 51 | 488 / 0 | wheel+sdist, fresh wheel import/CLI and demo pass on all three |
| `egresswall` | 675 / 0 | 675 / 0 | 675 / 0 | wheel+sdist, fresh wheel import/CLI and demo pass on all three |

Totals: 1,362 plan-lint tests plus 2,025 egresswall tests, zero failures.
Plan-lint's three wheels were byte-identical at
`704d7a4c5afb9f937a1d009b8c6bdd3f34173d95ffff4056fad937107f5c2607`.
Both public tag commits also have all seven GitHub CI jobs green (six OS/Python
matrix cells plus doc truth). No supported-version defect was found.

The local matrix exercised macOS; GitHub CI supplies the matching Ubuntu cells.
Python 3.14 is not claimed by the classifiers or CI and was not added overnight.
