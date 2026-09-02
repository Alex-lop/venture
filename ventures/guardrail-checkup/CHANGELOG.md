# Changelog

All notable changes to this project are documented here.
This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-31

The first release. There is no earlier version to have changed from, so this
entry describes what the release contains and what was decided during its
review.

### Added

- `guardrail-checkup run PATH --out REPORT.md` writes a six-section report over
  one repository: Scope, Tool results and what they got wrong, Invariant
  candidates, Monday list, What this did not cover, Provenance. The sections and
  their order are the ones the in-person session works through. No section
  states a conclusion: §3 is headed *candidates* because the tool never claims
  to have found the invariants.
- A guardrail inventory over `CLAUDE.md`, `AGENTS.md`, `.cursorrules`,
  `.cursor/rules`, `.github/copilot-instructions.md`, `GEMINI.md`,
  `.claude/settings.json` and `.claude/settings.local.json` hooks,
  `.mcp.json` / `claude_desktop_config.json` /
  `.claude/mcp.json` servers, `.pre-commit-config.yaml`, installed `.git/hooks`,
  `CODEOWNERS`, `.github/workflows/`, secret-scanning configuration, lockfiles
  and test layout. Every row that cites a file carries its `file:line`, a row
  stating an absence carries `-` because the listing is what establishes it, and
  every row carries one line explaining why it matters or what remains unknown.
- Up to three ranked invariant candidates from path heuristics, from repair
  commits in `git log`, and from `CODEOWNERS`, each with a `PreToolUse` hook
  that blocks writes to the path and a one-line test. The report labels them
  candidates; when fewer than three categories match anything it says so rather
  than inventing a third; and it names, in those words, every candidate whose
  only evidence is a bare path match.
- Composition with the sibling packages: `agent-plan-lint` validates any
  checked-in policy or plan document and drafts a starter policy when no JSON
  file carries the policy signature keys; `egresswall` screens a sample of checked-in JSON fixtures and the MCP
  configuration is rewritten with `egresswall proxy` in front of each server
  that runs a command line, as a suggestion. A server that names a URL instead
  is reached over the network, cannot be wrapped by a proxy in front of a
  command, and is reported as unchanged with both counts stated.
- `--emit-dir` for the drafted policy, hooks and MCP suggestion; `--format json`
  for the same facts as a document — the scope, the inventory, the siblings'
  results, the falsifiers, the candidates and the Monday list, without §3's
  per-candidate snippet, script and test line; `--max-files` for the listing cap,
  which bounds the ranking, language mix and symlink inspection but not the
  inventory's name-based lookups or the agent-plan-lint signature scan, and which §3 names in the
  report when it bit.

### Decided during the build

- **The tool never writes into the repository it reads.** `--out` and
  `--emit-dir` are refused with exit 2 if either resolves inside `PATH`. The
  only subprocess in the package is `git`, restricted to `ls-files`,
  `rev-parse` and `log` by an assertion in the wrapper; `tests/test_readonly.py`
  asserts that over the AST of every shipped module, along with the absence of
  any import that could reach the network or a model provider.
- **Exit status is 0 whenever the report was written, and 2 on a usage or IO
  error. It is never 1.** This tool reports; it does not gate. The sibling
  packages exit 1 on a finding because they are gates.
- **No readiness score, no grade, no percentage for the repository.** Section 3
  is a judgement about the reader's code, and a number would launder it into
  something it is not. The number section 3 prints beside each candidate is the
  evidence tally that section defines — repair commits, `CODEOWNERS`, the path
  heuristic — and `tests/test_cli.py` fails if a rendered report ever carries a
  percentage outside a quoted scorer claim, or the word *grade* at all.
- **The report is deterministic.** The same commit, with `SOURCE_DATE_EPOCH`
  set, produces the same bytes; without it the date line moves and nothing else
  does. The path is printed as given rather than resolved, so a report can be
  diffed and a demo can be checked in.
- **Section 2 does not run the tools it names.** It emits the falsifier list —
  the claims a generic readiness scorer makes, next to what is true in this
  repository and the command that shows it — because running `npx` would break
  the offline promise and because the falsifiers are what the reader needs.
- The history heuristic weighs a repair commit double when the same commit
  touched a test path named for a regression. The first draft matched
  `\bregress` with a word boundary, which never fired on `test_regression_x.py`;
  the boundary is gone and `tests/test_scan.py` covers it.
- **A commit is one point, however many files it touched.** The score §3 states
  is the number of repair commits, so a single commit over three files under
  `db/` counts once. An earlier draft summed weighted path touches, which the
  documented formula did not describe.
- **The repository under inspection is untrusted input.** Its `.git/config` is
  overridden on every git command line (`core.fsmonitor`, `core.hooksPath`,
  `core.quotePath`), because git would otherwise run a program the checkout
  names or hand back a C-quoted literal instead of a path; the user's own
  configuration is left alone so `safe.directory` still protects them. The two
  exceptions are the `rev-parse` queries that ask where this checkout's hooks
  live and which git directory a linked worktree shares, which drop the
  `core.hooksPath` override because that override *is* the answer to the first
  question — and which fire no hook. Every
  string the repository controls — a command line in `.mcp.json`, a commit
  subject, a `CODEOWNERS` pattern, a path — is escaped before it reaches the
  report, so a checkout cannot write its own heading, its own link or an
  invisible character into the report it is the subject of. A path renders
  through `path_cell` outside a code span and through a widened fence inside
  one, because a backslash is literal in a code span; and every
  repository-derived token in a shell line the report offers the reader —
  §3's one-line test, §2's falsifier commands — is `shlex.quote`d, because
  `re.escape` makes a filename safe for `grep` and not for `sh`. A configuration
  file that parses but is not the expected shape is a finding, not a traceback,
  and one `except` in `main` keeps any future shape from producing exit 1.
- **A symlink out of the repository is not read.** One inside the listing cap is
  also reported; checking the full listing would make this single finding an
  uncapped `lstat` sweep. `CLAUDE.md -> /etc/passwd` cannot put a file from the
  reader's own machine into a report they hand to someone else.
- **A hook matcher of `*`, or none at all, matches every tool.** The fetched
  hooks page says so, and `tests/test_hooks.py` quotes the sentence next to the
  code that implements it; the first draft read the strictest configuration as
  matching nothing.
- **Only a `CODEOWNERS` pattern that names an owner requires a reviewer.** A
  pattern with no owner clears ownership, so it is reported separately and adds
  nothing to the ranking.
- **The history walk is bounded twice.** `HISTORY_COMMITS` bounds how far back
  it looks and `HISTORY_PATHS` bounds how much one commit can cost; the log is
  read one NUL-separated record at a time, no path lists are retained, and §6 says when the walk
  was cut short. Neither cap bounds the wall clock by itself — `--no-renames`
  does, for the reason the seventh pass below records.
- **The sdist ships everything the suite reads**, `.python-version` included,
  so the suite in an unpacked source distribution fails on no file that was
  never packaged; the one check that needs a git checkout skips itself there.
  `tests/test_packaging.py` derives the list from the suite itself.
- **The doc-truth suite reads numbers in context.** Each figure is matched
  inside its own sentence against the value in the code, `CHANGELOG.md`,
  `CONTRIBUTING.md` and the package description are covered too, every
  `every`/`all` claim in the README is on a closed list, and a set of injected
  falsehoods is replayed as a test.

### Fixed before release, from the second review pass

- **A filename cannot run a command on the reviewer's machine.** §3's one-line
  test built a `grep` pattern out of repository paths inside a single-quoted
  shell string; `re.escape` does not escape `'`, so a file named
  ``stripe';id>PWNED;echo'.py`` closed the quote and appended a command to a line
  the report invites you to paste into a shell. §2's `wc -l` and `grep -n`
  falsifier commands had the same shape. Every repository-derived token is now
  one `shlex.quote`d argument, and `tests/test_hooks.py` runs both through `sh`
  over a repository of shell metacharacters and asserts no extra command ran.
- **A filename cannot write markdown into the report.** Paths deliberately
  skipped the escaper, so `.cursor/rules/[Approved by security](mailto:…) never
  db.md` rendered as a live link and `<!-- …` commented out every row after it.
  Paths now render through `path_cell` outside a code span and through a fence
  wider than any backtick in them inside one.
- **A symlink loop no longer kills the run.** `Path.resolve` raises
  `RuntimeError`, not `OSError`, on ELOOP, so two symlinks pointing at each other
  produced no report at all. The check is `os.path.realpath`, which returns the
  unresolved path instead of raising.
- **A directory symlink out of the repository is listed.** `os.walk` hands one
  over in its directory list and never in its file list, so a link to a whole
  tree — the dangerous case — was invisible to the symlink finding.
- **The inventory's name-based lookups read the whole listing.** `--max-files` truncated the list the
  inventory looked names up in, so a repository above the cap was told its
  committed lockfile did not exist. The cap still bounds the ranking, the
  language mix and the byte total.
- **Installed git hooks are found where git looks for them.** `<root>/.git/hooks`
  is the wrong directory under `core.hooksPath` and inside a linked worktree —
  the two configurations a blocking hook is most likely to live in — and the row
  then stated the opposite as fact. It asks `git rev-parse --git-path hooks`, and
  emits no row at all when the path is not a git repository.
- **An MCP server is screened when the command it runs is a screen**, matched on
  the executable name against `egresswall`, `mcp-gateway` and `mcp-scan`. A
  substring search over the whole command line reported `npx -y @evil/proxy-exfil`
  as screened, in the one row of the report that asserts a control is in force.
- **A comment is not a configuration.** The secret-scanner and test-runner
  detectors read `# we do NOT use gitleaks or pytest here` as both, and the
  scanner row's consequence is now hedged the way the hook row's is.
- **Section 5 names no candidate.** It said "is candidate *N* the right one",
  with `N` the length of the list, so it always singled out the lowest-ranked
  one — a judgement, inside the section that says what the report does not know.
- **One `TEST_PATH`.** The report's falsifier regex was a copy of the inventory's
  with one alternative missing, so a `*.test.ts` repository got the count and not
  the falsifier row.
- Three smaller things: `.mcp.json` present but unreadable no longer produces
  two rows that contradict each other; §1 says *apparent size*, because
  `st_size` on a sparse file is not bytes on disk; and §4 says that the
  `--policy` path in the emitted MCP suggestion is a placeholder.

### Fixed before release, from the third review pass

- **A large `CODEOWNERS` no longer decides how long a checkup takes.** The
  ranking asked whether each owned pattern matched each candidate file, and a
  pattern that matches nothing — the normal case — paid the whole product: a
  repository of five thousand files with a 1 MiB `CODEOWNERS` took a minute and
  a half. The patterns
  are deduped and capped at `OWNER_LIMIT`, the row says when the cap bit, and
  each pattern is now one substring search over two strings built once per
  category. `tests/test_limits.py` builds the largest `CODEOWNERS` this tool
  will read and fails on the clock.
- **One escaper, and it runs once.** `md` escapes the backslash first and then
  the characters that open a link, a tag, a code span, emphasis or a table
  cell. It replaced `quoted`, `path_cell` and the renderer's `_cell`, which
  between them escaped some strings twice: `repr()` doubled the backslash the
  escaper had just added, so `\[` became a literal backslash and a *live* `[`
  and an MCP server named `[Approved by security](https://…)` put a working
  link in the report. A code span is the one place it does not run, because a
  backslash is literal there.
- **git's paths are read raw.** `git log --name-only` C-quotes anything that is
  not ASCII, so an accented directory arrived as a backslash-escaped literal,
  became the starter policy's write glob, and was then dropped as unpoliceable —
  one emitted policy carrying two spellings of one directory. Each git call carries
  `-c core.quotePath=false`, the log walk reads `-z` records, and bytes are
  decoded with `surrogateescape` before the one normalisation the listing
  already used.
- **Both settings files are read, and no row claims anything about the
  machine.** A repository whose blocking `PreToolUse` hook lives in
  `.claude/settings.local.json` — which Claude Code reads and gitignores — was
  reported as configuring no hook. Both files are read, the local one from
  disk as well as from the listing, each consequence says what this
  repository checks in rather than what runs on the machine, and section 5 names
  the hook sources that are outside the checkout.
- **The Monday list names `PostToolUse` only when a `PostToolUse` hook
  exists.** The branch fired whenever no `PreToolUse` hook was found and then
  asserted that one was wired, contradicting the inventory table two sections
  above it.
- **A line number is computed once per file.** `_line_of` scanned the whole
  configuration once per MCP server, so a two-file repository whose `.mcp.json`
  named thousands of them spent half a minute there. The quoted tokens are indexed in
  one pass and the lookup is a dict hit.
- **A missing sibling is one line and exit 2.** The two sibling imports were at
  module scope, so a partial environment turned `import guardrail_checkup` into
  a two-level traceback and the console script into exit 1 — the one status
  this tool promises never to return. They moved into the function that uses
  them, and `tests/test_packaging.py` installs the wheel with `--no-deps` and
  checks both.
- **A hard link is refused like a path inside the repository.** The guard
  compared resolved paths, and a hard link resolves to itself, so a second name
  for a file in the repository was outside it by any path test and the same
  bytes on disk. The symlink half of the same hole was closed in the fourth
  pass below.
- **One reader decides which key an MCP configuration lists its servers
  under.** The inventory took `mcpServers or servers` and the emitted
  suggestion took `mcpServers if present else servers`, so a configuration with
  an empty `mcpServers` beside a populated `servers` made the report state a
  count its own table contradicted.
- **The emitted MCP suggestion wraps what it can and says what it did not.** A
  server already running a known screen came back double-proxied, and a server
  whose `args` were not made of strings had a Python repr written into its
  command line. Each is counted and named instead.
- **The Monday list names a path, not a phrase.** With no `--emit-dir` the
  fallback words were concatenated into a path inside a code span, producing
  text that was not a path and could not be copied.
- **The doc-truth suite closes more lists.** An audit shipped twenty-three falsehoods
  through the previous version: an invented table row, a reversed row, a
  spelled number the digit scanner never saw, a flag that does not exist, a
  wrong Python example, a false licence classifier. The rows of *What it looks
  at*, a list of behavioural sentences, the classifiers, the `--flag` tokens
  and the Python block are read now, and the injections are replayed as
  tests. `CONTRIBUTING.md` lists the classes that still get through.
- **The comparison page says only what a fetched source says.** *They enforce*
  and *`cc-safety-net` could add a `--report` flag in an afternoon* were
  characterisations no checked-in evidence supported, and the README's short
  version attributed two capabilities to `microsoft/agentrc`, which the page
  itself promises not to characterise.

### Fixed before release, from the fourth review pass

- **A symlink is refused like a hard link.** `--emit-dir` joined each draft name
  onto the directory without resolving it, and `write_text` follows a symlink,
  so `drafts/starter-policy.json` pointing at a file in the checkout exited 0,
  edited the repository, and left §6 saying it had written no file inside it.
  Every target — `--out`, `--emit-dir` and each emitted draft — is compared by
  `os.path.realpath` now.
- **A plan with a validation issue no longer raises.** The renderer read
  `issue.message`, which `agent_plan_lint.PlanValidationIssue` does not have, so
  every repository carrying a policy and a plan that fails validation ended in
  `AttributeError` and exit 2 with no report at all. It is `issue.detail`, the
  fields are pinned against the sibling's model, and the whole path now runs in
  a test over a plan that produces issues.
- **`core.hooksPath` cannot point this tool out of the repository.** The
  inspected checkout's own configuration chose the directory whose filenames the
  report printed as this repository's installed hooks; `core.hooksPath = ~/.ssh`
  made the report a listing of the reader's private files, labelled as a
  worktree fact. The answer is contained to the repository, or to the git
  directory a linked worktree shares with its main checkout, and anything else
  is a finding that says so and is not read.
- **A hook matcher is evaluated the three ways the documentation names.** The
  test was `write` or `edit` anywhere in the matcher, wrong in both directions:
  `.*`, `^Notebook` and `Bash|.*` catch a write tool and were reported as
  catching none — the false negative that tells a reader nothing inspects a
  write when something does — while `WriteLog` was reported as inspecting every
  path. The three modes are evaluated in the order the fetched page names them,
  and the docstring cites the two lines it names them on.
- **The starter policy's filter is agent-plan-lint's own path type.** A hand
  written regular expression stood in for the sibling's rules and missed two
  classes it refuses: a path component ending in a dot or a space, and the
  non-breaking space with the rest of the invisible set. The emitted policy was invalid and §2 said
  nothing had been left out of it. The annotated type is read off the policy
  model instead, so the two cannot drift.
- **The tie-break is the number of matching files.** All of them: the sort read
  `len(paths)`, which is capped at eight examples, so a category of twenty files
  ranked below one of nine — the opposite of what the README and §3 both state.
- **The starter policy excludes the candidates §3 names.** Its exclusions were
  built from every ranked candidate while §3 renders the first three, so a
  repository matching seven categories got a policy excluding four paths no
  section of the report mentioned.
- **Every file this tool opens is named in §1.** The linter falsifier read
  `pyproject.toml`, `setup.cfg` and `package.json` outside the inventory's own
  accounting, so §1 promised "exactly what was and was not read" while the JSON
  document's `scope.read` was empty. Every `_read` in the package goes through
  one recorder now, and a test asserts it.
- **The rule directory and the MCP table are bounded like everything else.** A
  prefix entry of the agent-file list fanned out over every file under it at up
  to `MAX_READ_BYTES` apiece — files times lines, with no bound on either — and
  a `.mcp.json` naming thousands of servers produced one row each. Both are
  capped, the row says when the cap bit, and `tests/test_limits.py` times both.
- **A job name no longer decides whether a workflow runs on pull requests.** The
  trigger was a substring search over the whole file, so a job called
  `pull_request_notes` in an `on: push` workflow made the consequence column
  state that a change is tested before review. Only the top-level `on:` block is
  read.
- **Two consequence cells stopped stating facts about the host.** *CODEOWNERS:
  absent* said any path can be merged by anyone and *.github/workflows: absent*
  said no automated check runs at all — both false under branch protection or a
  CI that is not GitHub Actions, and both contradicted by §5 of the same report.
  Each is scoped to the checkout now.
- **The Monday list names the instruction file.** Its last item said "your agent
  instruction file" while every other item names a path; the row that produced
  the branch already knew which file it was.
- **The doc-truth suite holds its closed lists whole.** An audit reversed a rule
  inside `CONTRIBUTING.md`'s own three rules, reversed the read-only guarantee
  inside the body of a bullet whose opening was held, rewrote items of two
  length-closed lists, repointed a project URL, and swapped one declared prose
  figure for another — twenty-two of twenty-six injections shipped green. Items
  are held whole rather than by their opening, every declared prose number
  carries the sentence it must appear in, `CONTRIBUTING.md` and the project URLs
  are scanned like the rest, and the replayed injections are what the README and
  `CONTRIBUTING.md` now count.
- **`tests/test_limits.py` is tracked.** It was the one file in the package git
  did not track and did not ignore, so a clean clone collected four tests fewer
  than the README's runnable block asserts. `tests/test_packaging.py` fails now
  when a test file on disk is untracked.

### Fixed before release, from the fifth review pass

- **A file that is present and cannot be read never produces a negative fact.**
  `read(...) or ""` coerced an unopened file to an empty one, and each detector
  then measured that: one run printed *CODEOWNERS: 0 pattern(s) with a required
  reviewer*, *tests not found*, *secret scanning: not configured* and *no
  PreToolUse hook* about four files the same run's own `scope.unread` listed as
  never read. Every branch that reads a named artifact ends at one row —
  *present, not read* — and a table-driven test covers each branch against a
  file over the cap, one holding a NUL and one the owner cannot open.
- **A settings file that does not parse says nothing about the hooks in it.** A
  typo in `.claude/settings.json` produced *not valid JSON* and then two rows
  asserting what the unparsed file configures.
- **Every string the repository controls now goes through one of the two doors.**
  `composed.validations` was the last that went through neither, so a plan file
  named `[click](evil.example) <img src=x onerror=…> plan.json` put a live link
  and a live image into §2 of a document the reader hands to someone else. It is
  rendered in a code span now; a test renders a hostile repository's whole report
  with a CommonMark parser and asserts no link, image or HTML tag survives
  outside one, and another reads the renderer's own f-strings for an
  interpolation that passes neither `md` nor `_code`.
- **An installed git hook is one git will run.** A hook file without the execute
  bit was counted as installed, and the row then said *a commit is checked
  locally before it is made* — while git prints "hook was ignored because it's
  not set as executable" and makes the commit. Executable is part of the test
  now, and the non-executable files get a row of their own.
- **A gitignored `.mcp.json` is read from disk.** MCP configuration was looked
  for in the git listing alone, so the common setup — the file carries
  per-machine server config and is gitignored — produced *no tool servers are
  configured in this repository* about the file the agent actually loads. It is
  read the way `.claude/settings.local.json` already was, and the report says
  *present on disk, not checked in*.
- **A test runner is read off a workflow's `run:` steps.** The detector was a
  word search over the whole file, so a step named *why we dropped pytest* made
  the report state that a change is tested before review for a workflow that runs
  `echo hi`. Only a `run:` value is a command; the consequence is hedged the way
  the secret-scanning row is, because nothing here was executed.
- **The secret-scanning sweep goes through the one recorder.** It opened
  `.gitleaks.toml` and `.secrets.baseline` with `_read` directly, so §1 and
  `scope.read` did not name a file the report cites by line. A test now spies on
  `open` and `Path.read_bytes` rather than on one function, so a branch that
  reads a file some other way fails it.
- **`--max-files` no longer bounds the agent-plan-lint signature scan.** A
  repository whose checked-in policy sorted past the cap was told no document in
  the schema was found, and a starter policy was drafted over the top of the one
  it has. The scan reads the whole listing, like the inventory; §3's ranking is
  the one section that still reads the capped slice, and it says so.
- **The MCP command line is rendered as a code span rather than escaped into
  one.** `md` is the escaper for markdown text and a backslash is literal inside
  a code span, so a backtick in a command closed the span early and swallowed the
  rest of the row.
- **A known screen is a bare name or an absolute path.** The check took the last
  path segment, which is where an npm scope stops being part of a package's
  name, so `npx -y @evil/egresswall` and a `./egresswall` the checkout itself
  ships were reported as screening the server.
- **A matcher this tool cannot evaluate is reported as unchecked.** Claude Code's
  matchers are JavaScript regular expressions; `(?<x>Write)` is a valid named
  group there and Python rejects it, and the row then said no write tool is
  inspected. The JavaScript spelling is rewritten to Python's, and whatever still
  fails to compile gets the hedge the hook and screen rows already use.
- **The checked-in Nemisis transcript is regenerated and diffed.** It was a
  pre-fix run labelled with the shipped version, and only the three blocks the
  README quotes were bound. A test re-runs the recorded command against the
  recorded commit and diffs the whole file, skipping where that checkout is
  absent; the transcript records the command, the commit and the
  `SOURCE_DATE_EPOCH` it was produced with, and its paths are relative.
- **`CONTRIBUTING.md` names each class the doc-truth suite still misses.** It
  said four; an audit shipped seventeen of twenty-three injected falsehoods, and
  eleven of those fell in classes the list did not name. The list was then the
  eleven classes those injections demonstrated, its length and its text held
  by the suite, and the sentences the audit reversed are each pinned and replayed.
- **The tracked-file check skips where there is no git checkout.** It ran `git
  ls-files` unconditionally, so the suite in an unpacked sdist ended in
  `CalledProcessError` rather than in the skip its own precondition asks for.
- **`markdown-it-py` joins the development dependencies.** The report's escaping
  is now asserted against a CommonMark parser rather than against a regular
  expression over the markdown. It is a `[dependency-groups] dev` entry; the two
  runtime dependencies are unchanged.

### Fixed before release, from the sixth review pass

- **The workflow list is capped like every other axis.** How many workflows a
  repository checks in was the one axis with no bound: each is read at up to
  `MAX_READ_BYTES` and walked line by line three times, and `_uncommented` was
  walked twice more because the workflow step and the secret-scanning step
  each computed it. A thousand
  workflows of a megabyte apiece was forty-four seconds of scan — well over the
  whole-run budget — and a thousand and fifteen rows. `WORKFLOW_LIMIT` is 32,
  the remainder gets the row the rule directory already gets, and the secret
  scan counts the unread ones rather than calling them absent.
- **The agent-plan-lint signature scan has a byte budget.** Removing
  `--max-files` as its bound stopped it reporting a policy absent, and put
  nothing in its place: twenty thousand checked-in JSON files of a megabyte
  apiece cost eighteen seconds whatever `--max-files` said. The sweep still
  reads the whole listing, so no absence is claimed off a truncated one, but it
  stops after `SIGNATURE_SCAN_BYTES` and §2 then says how many files were listed
  and not read.
- **The secret-scanning row says where a scanner was named, not that one is
  configured.** Unlike the test-runner row beside it, this detector is a word
  search over the whole uncommented file, so a job id, a step `name:`, an `if:`
  guard and an `env:` value reach it too. The fact column read *configured*
  while its own consequence column hedged; it reads *named in N place(s)* now.
- **§1's own figures are the capped slice, and the README says which.** The
  README named §3's ranking as the one section the `--max-files` slice decides;
  the file count, the byte total and the language mix §1 prints are computed
  from the same slice. The sentence says so, and a test runs the tool twice,
  capped and not, to hold it.
- **`CONTRIBUTING.md`'s residual list is the nine classes it still misses.** Two
  documents stated different counts — this file said eleven where that one said
  ten — and neither figure was bound, so an audit swapped one for *four* with
  the whole suite green. The list lost the closed preamble class and the
  AI-assistance survivor, and one binding now holds the spelled count in both
  documents against the number of bullets.
- **The AI-assistance disclosure is a bound sentence in both documents.** The
  one sentence discharging it was held by no test: an audit replaced it with its
  reverse and the whole suite passed. Both it and the README's line are in
  `SENTENCES` now, against the §6 line the renderer emits.
- **§3's no-candidate paragraph ends before the next heading.** It was the one
  branch in the renderer that added no trailing blank line, so the report ran
  *…and no other.* straight into `## 4. Monday list`.
- **Three README sentences that outran the code.** The workflow table row was
  keyed `*.yml` while the scan also reads `*.yaml`; the egresswall bullet
  presented three unwrapped-server cases where the code produces four; and the
  path is printed in the header line under the title, not in the title, which
  prints the resolved directory's name. §1 accounts for the files it opened —
  the JSON document is what lists them one by one.
- **`scripts/refresh_evidence.py`'s docstring names the test that reads it.** It
  named `tests/test_readme_truth.py`; the test that counts its hosts is in
  `tests/test_comparison_truth.py`. The script ships in the sdist, so the false
  sentence was published; that test now asserts the docstring names it.

### Fixed before release, from the seventh review pass

- **The history walk is bounded in seconds, not only in paths.** `git log
  --name-only` runs rename detection before it emits its first byte, so neither
  `HISTORY_PATHS` nor killing git could bound the wall clock: one commit
  renaming a hundred thousand files cost eighteen seconds of `git log` against a
  two-second budget, and the path cap bit either way. `--no-renames` makes the
  same walk half a second, and it is the better answer for a walk that wants the
  paths a repair touched, because a detected rename reports only the new path
  where this one wants both. The caps are `HISTORY_COMMITS` 2000 non-merge
  commits and `HISTORY_PATHS` a hundred thousand path entries, the second
  chosen the way `WORKFLOW_LIMIT` was — a path in a repair commit is matched
  against the seven categories, so two hundred thousand was over a second at the
  cap and a hundred thousand is half of that — and `tests/test_limits.py` times
  both: a vendor refresh at the path cap and fifty thousand commits at the
  commit cap, each against the two seconds the other steps are held to.
- **§5 of the report names the three tools this one does not replace.**
  `docs/comparison.md` said this package is defended by being honest about the
  other three *in the report it writes*, and no rendered report named one of
  them: the honesty was on that page, and the doc-truth suite held the sentence
  word for word, so it pinned a false claim in place. §5 now carries one line
  each for Claude Code's `/doctor`, `kenryu42/cc-safety-net` and
  `microsoft/agentrc`, quoting the source checked in under `docs/evidence/` for
  each; §6's unaffiliation line names §5 beside §2; and two tests hold it, one
  grepping a rendered report for the three phrases and one binding each phrase
  to the fetched file it came from.
- **`CONTRIBUTING.md` says which decision bullets are held whole.** Its residual
  list said the bolded lead of each decision under *Decided during the build*
  and the *Fixed before release* sections is held word for word and the body is
  not; the sixth pass is held item by item, and an audit's rewrite of a body
  there was caught by the mechanism that sentence said would miss it. The
  sentence names the second through fifth passes now, and this pass and the
  sixth are held whole.
- **The falsifier command prints the figure printed beside it.** §2's testing
  row offered `find . -path ./.git -prune -o -name 'test_*' -print | wc -l`,
  which prunes the literal `./.git` and nothing else and counts files *named*
  `test_*` rather than files *in a test path*: on the checkout the pinned
  transcript records it printed five times the figure in the cell beside it,
  because it walked `.venv/` and counted by name. A report sells that column as
  the command that disproves the claim, so both halves come from one place now
  — the listing §1
  names and `TEST_PATH` itself, as `git ls-files` in a checkout and as a `find`
  pruning `SKIP_DIRECTORIES` outside one — and a test runs it in both shapes and
  compares what it prints with the cell.
- **The two example lists in §2's egresswall paragraph say when they were cut.**
  Four of five thousand copied-through servers were named and the sentence ended
  in a full stop: the one truncation in the report that did not announce itself,
  where the caps beside it say how many they left out.
- **`CONTRIBUTING.md` says what the path dependencies stop, which is CI
  itself.** It scoped them to the wheel-install step; in a checkout without the
  sibling working copies beside it, `uv lock --check` and `uv sync` both fail to
  resolve them before a step runs, so no step of the matrix runs there today.
  The release step that deletes `[tool.uv.sources]` removes the condition.
- **`README.md`'s *License* section and `CHANGELOG.md`'s release preamble are
  held whole.** Both were prose no closed list read, and an audit shipped a
  false packaging claim through one and an invented security sign-off through
  the other, green through the suite. They are held the way `README.md`'s
  preamble already was.
- **A `##` heading no document declares fails the suite.** An entire invented
  section — a *Telemetry* heading claiming each run records an anonymous summary
  of its finding counts — shipped green: it contradicted the offline promise,
  and no closed list, no held sentence and no length check knew about a heading
  that was not there before. The `##` headings of `README.md`, `CHANGELOG.md`,
  `CONTRIBUTING.md` and `docs/comparison.md` are a closed list now.
- **Two source docstrings stated counts the code contradicts.** `wrapped_mcp`'s
  said three things stop a rewrite and listed three where the code emits four
  unwrapped reasons — the fourth is the case the sixth pass corrected the README
  for — and `_argv`'s scoped the read-only git configuration to one exception
  where the code has two. Both ship in the sdist, and a docstring in `src/` is
  read by no test: the eighth class `CONTRIBUTING.md` declares.

### Fixed before release, from the eighth review pass

- **The read recorder de-duplicates against a set.** Each `_read` in the package
  goes through `_record`, whose idempotence was a membership test over the two
  ordered lists §1 and `scope.read` render — so recording the reads cost more
  than the reads: a hundred seconds of a two-minute run over a repository of two
  hundred thousand tiny checked-in JSON files, and the step crossed the
  two-second budget at about eighteen thousand of them, inside the default
  `--max-files`, which by design does not bound that sweep. The lists are still
  the ordered ones the report renders; a shadow set answers the question.
  `tests/test_limits.py` times a hundred thousand files through the recorder.
- **The signature scan has a file budget as well as a byte budget.**
  `SIGNATURE_SCAN_BYTES` bounds what a file costs to read and nothing bounded
  what one costs to open, and a repository of tiny JSON never spends sixty-four
  mebibytes: a hundred thousand files is eight seconds of `open` alone.
  `SIGNATURE_SCAN_FILES` is 10000, and the remainder goes into the *listed and
  not read* clause §2 already carries, so no absence is claimed over a file
  nobody opened.
- **The workflow and rule-file caps bound the work, not the file count.** Both
  capped files where the cost is per line, and `MAX_READ_BYTES` lets one file
  carry half a million two-byte ones: sixty-four rule files of lines matching
  `_FORBIDS` was nearly three seconds, and 32 workflows of `run: |` block scalar
  was nearly three seconds, against the two seconds `tests/test_limits.py` holds
  one step to — on a repository inside the documented caps, while the fixtures
  meant to hold those caps used line shapes an order of magnitude cheaper.
  `LINE_BUDGET` is a million lines per step, each file's text is split once
  rather than three or four times, and the row that already counted the files
  nobody opened now counts these too. Both steps are timed at their caps in the
  worst line shape each one allows.
- **The starter policy says how many churned directories it left out.** The
  churn set was cut at 64 alphabetically, before the policy was drafted: a
  repository whose repair commits touched a hundred directories was handed a
  policy that denies writes in thirty-six of them, and no row, no clause and
  nothing in the emitted file said so — the one cap here that decides what an
  emitted file *grants* rather than what a row says. The globs are the
  most-churned directories now, `CHURN_GLOBS` is 64, and §2 states both figures.
  The emitted policy carries no note of its own: `agent-plan-lint`'s policy
  model forbids unknown fields and its loader is strict JSON, which has no
  comments.
- **The inventory's row claim says what the rows do.** Three sentences promised
  the `file:line` for rows that carry none: an absence row carries `-`, which is
  nine of the seventeen rows in the shipped demo report, and the assertion bound
  to those sentences opened `where == "-" or ...` — so the binding exempted the
  counterexample and pinned a false absolute in place. The sentences are scoped
  to a row that cites a file now, and the assertion allows `-` only on a row
  naming no file the scan opened.
- **The summary line cannot lose a run that succeeded.** With the report on
  disk, `guardrail-checkup run . --out R.md | head` exited **120**: the line is
  buffered, so it failed in CPython's shutdown flush, after `main` returned and
  past the guards in `_cli`. It is flushed inside the guarded path now, a reader
  that closed the pipe — or a caller that gives it no stdout — is exit 0 with a
  silent stderr, and two tests drive it through both.
- **Three cuts that did not announce themselves now do.** The comment beside
  `SETTINGS_FILES` said Claude Code reads four hook sources where its own
  `/hooks` menu lists five, and a test counts them against the evidence file;
  §3's `CODEOWNERS` evidence line named three patterns and no total, the way the
  repair-commit line beside it already did; and §1's language mix, the ten most
  common extensions, says how many there were.

### Pre-release scaffolding

- `[tool.uv.sources]` in `pyproject.toml` resolves `agent-plan-lint` and
  `egresswall` from the sibling working copies, because neither is on PyPI yet.
  **The release deletes that table and re-locks**, so the declared PyPI ranges
  `agent-plan-lint>=0.1,<1` and `egresswall>=0.1,<1` are what a user resolves.
  `tests/test_packaging.py` fails if the table is present and this note is not.
