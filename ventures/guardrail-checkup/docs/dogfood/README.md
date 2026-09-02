# Public-repository dogfood — 2026-09-02

`guardrail-checkup` ran read-only and deterministically over all 20 public
repositories owned by `Alex-lop`, including the three forks and one unborn
repository. Each Markdown report records the exact subject commit and command;
reruns were byte-identical and an independent audit found no credential,
fingerprint, temporary path or local workspace path in the tracked output.

The reports are evidence, not twenty automatic tickets. Human triage rejected
path-only heuristics, intentional hostile fixtures, empty/docs-only repositories
and fork findings. One reproducible defect survived triage:
[Alex_Lopez_Website #3](https://github.com/Alex-lop/Alex_Lopez_Website/issues/3)
records its failing contact-obfuscation regression script without publishing the
contact value.

Two findings were fixed immediately instead of issue-posted:

- `Final_test` no longer tracks its local API credential file and now ignores
  the path (`3c207b0`). The old credential still requires human rotation and a
  separately approved history cleanup; details stay in `private/`.
- `requirements.lock` is now recognized by guardrail-checkup's shared lockfile
  inventory. The regenerated `X-Scraper.md` names it and falsifies a generic
  “missing lockfile” score.

The tool intentionally does not scan arbitrary repository contents for secrets;
it reports whether a preventive scanner is configured and tells the reader to
run gitleaks, trufflehog or detect-secrets for working-tree/history coverage.
