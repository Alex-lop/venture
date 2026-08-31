# guardposts — the site

Source for <https://alex-lop.github.io/guardposts/>: the home page for the `guardposts`
family of agent guardrails and for the measurement study that goes with them.

Plain Markdown with Jekyll front matter and a built-in GitHub Pages theme
(`jekyll-theme-cayman`). No build tooling, no JavaScript, no analytics, no external assets,
no `CNAME` — GitHub Pages builds it from `main`. There is deliberately no `.nojekyll`: the
site *is* Jekyll.

```
_config.yml   index.md   study.md   compare.md   about.md
packages/agent-plan-lint.md   packages/egresswall.md   packages/guardrail-checkup.md
scripts/check_site.py         LICENSE
```

## Checking it

`scripts/check_site.py` is the doc-truth test for this site. Stdlib only, no arguments:

```sh
python3 scripts/check_site.py
```

It runs the study's `analysis.py` and asserts that every number on `study.md` appears in
that output or in the study's `SUMMARY.md`; that every relative link resolves to a file that
exists and every absolute GitHub URL points under `Alex-lop/`; that no page claims a package
can be installed until a `RELEASED` file at the site root names it; and that no page carries
an email address or a string from the private denylist. It expects the study
beside it (it reads `../c-measurement/study/`); pass `--study <path>` if it is elsewhere,
and `--skip-analysis` to check everything except the numbers.

## Release flag

`RELEASED` does not exist yet, and while it does not, no page here may say `pip install`,
`uv pip install`, or that a package is on PyPI. Publishing a package means adding its name
on its own line in `RELEASED` and adding the install line to that package's page in the same
commit — `check_site.py` fails if the second half is skipped, and fails the other way if a
name is added to `RELEASED` while nothing installs it.

## Licence

Apache-2.0, Copyright 2026 Alexander Lopez. See `LICENSE`.
