# Contributing

Please open an issue, or a small and focused pull request.

1. `scripts/check.sh` runs the same steps locally: `uv lock --check`, `ruff check`,
   `ruff format --check`, `pytest` on 3.11, 3.12 and 3.13, `uv build`, and the built
   wheel installed into a fresh environment on each of those three interpreters,
   running the demo. Please make it pass before opening a pull request. CI runs
   those steps again on Ubuntu and macOS, and adds a second job that runs the
   doc-truth tests on their own. <!-- claim: test_the_contributing_check_script_claim_is_what_the_script_runs -->
2. Every behaviour change needs a test. Every README or `docs/` claim needs a test
   that fails when the claim stops being true -- `tests/test_readme_truth.py`,
   `tests/test_docs.py` and `tests/test_comparison_truth.py` are where those live.
   A sentence that says the package *always*, *blocks*, *catches*, *checks*,
   *detects*, *enforces*, *ensures*, *every*, *guarantees*, *never*, *refuses*,
   *rejects*, *reports*, *ships*, *supports*, *validates* or *verifies*
   something has to name the test that backs it:
   end the paragraph, list item or table row with a marker comment, <!-- claim: test_every_block_that_makes_a_claim_names_the_test_that_backs_it, test_the_marker_convention_is_written_down_where_a_contributor_reads_it -->

   ```
   <!-- claim: test_the_readme_lists_exactly_the_codes_the_validator_can_emit -->
   ```

   naming one or more `def test_...` functions under `tests/`. The marker covers
   every claim sentence in the block it ends, it is invisible in rendered
   Markdown, and `tests/test_readme_truth.py` fails when a block makes a claim
   without one or names a test that does not exist. Say something weaker, or write
   the test.
   `docs/comparison.md` quotes other projects' documentation: before a release run
   `scripts/refresh-comparison.sh`, which re-fetches every page in
   `docs/comparison-sources.txt` and fails on a quotation that is no longer there.
   Adding a claim about another tool means adding its URL to that manifest. <!-- claim: test_every_claim_marker_names_a_test_that_exists, test_every_page_the_comparison_cites_was_captured -->
3. `.python-version` pins 3.11, and it wins over anything `uv sync` did earlier. To
   test a different interpreter, pass `--python` on **every** `uv run`, not only on
   `uv sync` -- otherwise `uv run --frozen pytest` silently rebuilds the environment
   on 3.11 and you have run the same version twice. `scripts/check.sh` and CI both
   pass it per command. <!-- claim: test_the_check_script_passes_an_interpreter_to_every_uv_run -->
4. Keep the public API small. A new flag, a new module or a new dependency needs a
   reason that a test can state.

## AI assistance

If a pull request was prepared with AI assistance -- a coding agent, an autocomplete
model, a chat session that wrote the patch -- say so in the pull request description.
It does not disqualify anything; it tells the reviewer what to check. You are still
responsible for each line you submit, and for the claim that you have the right to
contribute it.

## What the doc-truth suite does not catch

The suite is a guard, not a proof, and a guard whose holes are undocumented gets
trusted for more than it does. These are the holes as of `0.1.0`, each one found
by injecting a false claim into a copy of the tree and watching the suite stay
green. Closing any of them is a welcome pull request. <!-- claim: test_the_documented_gaps_in_the_doc_truth_suite_are_the_ones_a_reviewer_listed -->

- A claim built from a verb outside the marker list in step 2 above carries no
  marker and needs no test.
- An adoption or usage number that happens to equal a constant the package
  produces passes the number sweep, which matches values and not what they count.
- A number spelled as a hyphenated compound is read as its last word, so it
  passes whenever that word's value is one the sweep already accounts for.
- A number inside a fenced code block is not swept; such a block is pinned only
  where some test runs it and compares the output.
- The wheel's `description` is held against a list of words a reviewer wrote out,
  rather than against any capability the package lacks.
- The provenance of the port is presence-only: the manifest records that each
  ported path existed on the fetch date, not what was in it, so a claim about
  Graphene's own wording cannot be re-derived offline.
- A quoted span shorter than the eight-character floor is collected by neither
  the offline check nor the refresh script.
- Star counts and dated figures are re-read from the world only by
  `scripts/refresh-comparison.sh` at release time; offline, the tests hold the
  page to the manifest and the manifest to nothing.
- The unquoted judgements on `docs/comparison.md` are one person's reading on the
  fetch date and no script can re-derive them; the page says so in its opening
  paragraph.
