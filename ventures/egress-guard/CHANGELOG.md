# Changelog

All notable changes to this project are documented here.
This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-30

The first release. Everything below is what it contains; there is no earlier
version to have changed from, so "Changed" and "Fixed" describe what was
corrected in the code this package was extracted from and during its review.

### Changed
- Renamed from `egress-guard` to `egresswall` before any release. The install
  instruction, the distribution name, the import name and `[project.urls]` all
  name `egresswall`, and a doc-truth test fails if any of them ever disagrees.
  (The registry lookups behind the rename are not checked in, so this entry does
  not describe them.)
- The proxy screens **every** server message whole, batches included, whether or
  not it saw the request that asked for it: results, errors, notifications,
  server requests, elements of a batch that are not objects, and messages that
  carry no member JSON-RPC defines. It used to screen a selected member of a
  recognised shape, so six shapes crossed the boundary unscreened. A violating
  message is replaced by a JSON-RPC error only on an id the client actually
  sent; anything else that violates is dropped with the reason on the proxy's
  stderr.
- Field **names** are screened like values. A tool that returns a table keyed by
  an email address or an SSN -- what a lookup tool returns -- used to be reported
  CLEAN with every detector active.
- A field name, a dotted path or a method name that carries a value is reported
  by position (`<key#3>`), never by its text, so no path, detail, JSON-RPC error
  or log line can carry a value out inside the report that blocked it.
- One folding for every name comparison, in `_fold`: NFKD, then combining marks
  stripped, then casefold, applied to field names, denied field paths and
  `allow_domains`. That is what makes fullwidth `ＡＰＩ＿ＫＥＹ` the listed
  `api_key`, which NFC could not do. An allowed domain spelled with
  a capital letter used to be a dead entry, and a confusable spelling of a
  listed field name (U+1E9E LATIN CAPITAL LETTER SHARP S, which casefolds to
  `ss`, spelling `ssn`) used to slip past the list.
- `hook` exits 2 on any input it could not parse, not only on input that nests
  too deep. Unparseable input is input that was not screened, and exit 1 is the
  code Claude Code treats as a non-blocking error.
- Install is `pip install egresswall`, with
  `uv pip install git+https://github.com/Alex-lop/egresswall` from source. The
  README named a clone-and-build route before the name was published.
- Field names are matched with case and separators removed, so `apiKey`,
  `api-key` and `API_KEY` are all the listed `api_key`. `access_key`, `auth`,
  `authorization`, `private_key`, `session_id` and `x_api_key` joined the
  defaults.
- A denied field path is a violation whenever the field is present: `0`,
  `false`, `""`, `[]` and `{}` now count. Only `null` and the governance-
  vocabulary exemption pass. Empty containers used to pass and falsy scalars
  did not.
- `max_depth` over 500 is refused when the policy is built, so `check()` cannot
  reach CPython's recursion limit and break its "never raises" contract.
- `denied_field_paths` are matched with case and separators removed on both
  sides, like forbidden field names: `patient.mrn` now catches `Patient.MRN`.
  It used to be an exact string comparison that any capitalisation bypassed.
- `forbidden_key_suffixes` is matched after normalization, so the default is
  spelled `token` rather than `_token` -- the rule it always implemented.
  `nextToken` and `pageToken` are refused by default, which is wrong for a
  paginated backend: set `forbidden_key_suffixes` to `[]` there. The protocol's
  own names are exempt in the proxy, so this does not reach `progressToken`.
- The `openai_key` detector requires 40 or more characters carrying a digit and
  an uppercase letter, so a hyphenated `sk-`-prefixed product slug such as
  `sk-widget-blue-large-2026-edition` is no longer reported as a key.

### Fixed
- Core: the invisible-prefix bypass below re-opened through code points the
  categories do not reach. Stripping Unicode categories C, Z and M still leaves
  a Hangul filler in front of a document a reader sees unchanged, because a
  filler is in none of them: `U+115F`, `U+1160`, `U+3164` and `U+FFA0` are general
  category `Lo`, and `U+2800` and `U+1D159` are `So`. One of them prefixed to a
  serialized `content[].text` payload turned `forbidden_keys` and
  `denied_field_paths` off for the whole of it again, with nothing reported and
  nothing logged. What is stripped from both ends is now the union of three
  sets: the categories, every code point with Unicode's
  `Default_Ignorable_Code_Point` property -- transcribed by hand into
  `_DEFAULT_IGNORABLE` from `DerivedCoreProperties.txt` for Unicode 15.1.0, with
  the URL and the merged ranges recorded beside it -- and the two blank-by-glyph
  code points `U+2800` and `U+1D159`. The regex is compared against a second,
  independent transcription of the same block in the test file, so a typo in
  either fails; all 4176 stripped code points are swept at both ends and at
  both ends at once; and the four fillers are asserted to be the only
  `Default_Ignorable` code points outside C, Z and M, which is why the property
  is stripped and not just the categories.
- Core: the schema exemption silently switched off `denied_field_paths`. The
  entry below exempted a declared schema's parameter *names* from the
  field-name rule; the walk gated the field-**path** rule behind the same
  branch, so an operator's `denied_field_paths` did not run under
  `inputSchema`, `outputSchema` or `requestedSchema` in any of the five methods
  that carry them -- and `elicitation/create` is server-originated, so the
  untrusted side named the exempt method itself and chose the exemption for a
  subtree of its own naming. Only `forbids_key` is gated now. A denied path
  names a field of the operator's own boundary rather than a schema keyword, so
  it runs everywhere, and the README's "Nothing else is exempt" is true again.
  A catalogue and an elicitation carrying a denied path are refused, a schema
  declaring a forbidden *name* is still forwarded, and both halves are tests.
- Core: `_extend_path` pruned the accumulated dotted path on the **raw** field
  name's length against a limit measured after separators were removed, so a
  parent name padded with separators -- `____patient____` -- was replaced by
  the too-long marker while `patient.mrn` still described what it carried, and
  the denied path failed open on a name the other side of the boundary chooses.
  The bound is checked on the normalized child only. A segment that normalizes
  to nothing is no segment either, so `patient.` and `patient` build the same
  path rather than `patient..mrn` and `patient.mrn`.
- Docs: the README described the `forbidden_key_suffixes` matcher as compiled
  "the same way" as the Aho-Corasick automaton behind `forbidden_values`, where
  this file correctly calls it a reversed prefix tree. The two pages name the
  same structure now.
- Docs: the README's `PAYLOAD_TOO_LARGE` row listed three of the six things
  that raise it. It names the numbers this interpreter cannot render or re-emit
  and the messages the proxy refuses before screening them as well.
- Tests: two fixtures were shaped like checked-in credentials -- `token = "..."`
  and `secret = "..."` -- so a package whose subject is credential material
  tripped the repository's own pre-push secret scan. Both are built by
  concatenation and bound to names that are not credential-shaped, and a test
  greps every text file in the package for that shape so the next one cannot
  arrive unnoticed.
- Core: the fail-closed embedded-document walk was reachable again one level up.
  The candidate test was the regex `\s*[{\[]`, and `\s` is neither a byte-order
  mark, a zero-width space, a soft hyphen nor a combining mark -- so a server
  turned `forbidden_keys` and `denied_field_paths` off for its whole
  `content[].text` payload by prefixing the serialized document with one
  invisible code point: the string stopped being a candidate, `_walk_embedded`
  never ran, and the message was forwarded whole with nothing reported and
  nothing logged. `_document_candidate` stripped every code point whose Unicode
  category is C, Z or M from both ends and used the stripped text both for
  the `{`/`[` test and for `json.loads`, so a document behind U+FEFF is screened
  as a document. That set is **superseded** by the entry below it: three
  categories are not the whole of what carries no glyph. The repro plus every prefix in that class -- the byte-order
  mark, the zero-width and bidi format characters, the soft hyphen, the
  combining grapheme joiner, the invisible operators, ASCII and Unicode
  whitespace, and combining marks -- is a test, in the library and through the
  proxy. A document behind a *printable* prologue is still not a candidate, and
  the README says so.
- Docs: this file described three mechanisms the code does not have. Name
  folding was "NFC then casefold" when `_fold` does NFKD, strips combining marks
  and casefolds -- NFC cannot fold fullwidth `ＡＰＩ＿ＫＥＹ` to the listed
  `api_key`, which the README claims it does. The shipped `forbidden_values`
  matcher was described as a prefilter and a fixed-width lookup when
  `_value_matcher` builds an Aho-Corasick automaton. And an unparseable embedded
  document "is screened as a string only" when the shipped default refuses it as
  `EMBEDDED_DOCUMENT_UNPARSEABLE`. All three sentences are corrected, the
  superseded bullets are marked as superseded, and a test now pins each
  mechanism to the code that decides it: the normalisation form named here and
  in the README has to be the one `_fold`'s docstring names, the matcher named
  on both pages has to be the one `_value_matcher`'s docstring names, and the
  embedded-document default named on both pages has to be
  `Policy().refuse_unparseable_embedded`.
- Docs: four things a reader copies or relies on were printed and never read.
  The Python API block's import line was not checked against `__all__`, so the
  README could advertise a `redact` entry point this package promises never to
  grow; the MCP client-config block's `command` was not tied to the console
  script the wheel installs; the Claude Code block's hook stage was not tied to
  the field `_cmd_hook` reads, so a `PreToolUse` block that screens nothing read
  as correct; and the middle column of "What it catches" -- the cell that states
  the rule -- was unchecked while the example beside it was pinned. Each is a
  test now, and each fails on the mutation that used to ship green.
- Docs: the README stated the fail-closed default's cost as a parenthesis. It
  states it as the design decision it is now, in "What it catches" and in "What
  it does not do": a template string such as `{{name}}`, a bracketed log line
  and a Markdown link at the start of a string are candidates that do not parse,
  so the default policy refuses them and blocks the whole tool result, and
  `refuse_unparseable_embedded: false` is the opt-out for a server whose text is
  templates and logs. Both modes are tested.
- Core: the embedded-document walk failed **open**. A string that opened like a
  serialized document and then would not parse was screened as a string and
  forwarded, so the untrusted side turned `forbidden_keys` and
  `denied_field_paths` off for its whole `content[].text` payload by appending
  one token -- a field spelled twice, an integer past this interpreter's digit
  limit, an array nested past the parser's own recursion -- with nothing
  reported and nothing logged. The same inputs at the envelope are refusals, so
  a server chose which rules applied to it. A candidate document that was not
  screened as a document is now the violation
  `EMBEDDED_DOCUMENT_UNPARSEABLE`, on the surface the README calls the only one
  that stops a value. A string whose first visible character is neither `{` nor
  `[` is not a candidate and is screened as a string exactly as before; the
  cost is a false positive on a string that merely starts like a document, and
  `refuse_unparseable_embedded: false` in the policy is the operator's opt-out
  back to the old walk.
- Core: `max_total_length` is documented as the bound that is measured, and a
  JSON number was screened as the text `str` renders it without being charged
  to it -- so a payload of long integers made the walk read an unbounded amount
  of text under a documented cap. A rendered number costs the budget its own
  length now, and a timing shape of max-digit integers is one of the seven the
  suite measures at that cap.
- Docs: this file claimed "a test that screens the largest message the proxy
  accepts in under two seconds" and no such test existed -- the only timing
  assertions were over `max_total_length` in `tests/test_detectors.py`, which is
  a different payload and a different bound. A test drives a line of exactly the
  largest size the proxy accepts through the proxy and asserts it.
- Docs: this file stated a timing-shape count the suite never ran, and
  contradicted the README about it twice in the same release. Every spelled-out
  shape count is pinned to `len(SHAPES)` now, here as well as in the README.
- Docs: counts written as words were pinned in `README.md` and nowhere else, so
  a spelled-out count here or on the comparison page could be changed to any
  other one with a green suite -- including counts that contradict an exported
  constant. Every document is scanned for number-words, each is either pinned to
  the code expression that decides it or declared prose, and the *set* of them
  is asserted so a new one cannot arrive unchecked.
- Docs: the capability bullets under "Added" were checked by nothing, so the
  file PyPI links as Changelog could advertise a subcommand, a flag or a hook
  stage the code does not have. Each bullet's first sentence is pinned, and the
  flag-name check that ran over `README.md` and `docs/comparison.md` runs over
  this file too.
- Docs: `docs/comparison.md` was checked project by project from the evidence
  records, so a whole fabricated section -- a competitor with no checked-in
  response behind it -- was invisible. The set of `##` headings on the page is
  asserted against the evidence records plus a declared list of non-repository
  sections, each bound to the excerpt it cites.
- Docs: the README's "What it catches" table had its reason codes pinned and its
  cells unchecked, so a row could describe a rule the code does not implement.
  Every example in the right-hand column is pinned verbatim and screened, and
  the code it reports has to be the code on its row.
- Docs: the one-line description PyPI renders under the package name was guarded
  only by a superlative denylist, and the keywords by nothing at all. Both are
  pinned verbatim.
- Proxy: every dotted `denied_field_paths` entry was a silent no-op. `check` and
  `hook` root the dotted path at the tool payload; the proxy screened the whole
  JSON-RPC envelope, so the accumulated path gained a `result.` prefix and never
  equalled the operator's entry. The same policy and the same body gave opposite
  verdicts on the two surfaces that only report and the one that actually stops
  a value, and the shipped `demo/policy.json` was one of the policies that did
  not enforce. Each payload member -- `result`, `params`, `error.data` -- is now
  screened as its own document, so `patient.mrn` means the same thing on all
  three surfaces; the reported path still reads `tools/call.result.patient.mrn`.
  Only bare-name entries fired before, which is why the demo looked right.
- Core: `forbidden_values` matching still scaled with the denylist. Entries were
  bucketed by a fixed-width head whose width was the shortest entry, so one short
  entry collapsed the index and every entry sharing that width's prefix landed in
  one bucket, walked in full at every matching offset -- and the text is chosen by
  the server. A plausible denylist of internal case ids took seconds per message
  over the documented text budget, and the timing test missed it because its
  10000 entries were all one length, which gives every bucket one candidate. The
  denylist is compiled into an Aho-Corasick automaton now, which reads each
  character a bounded number of times whatever the list holds; a
  colliding-denylist shape is one of the seven the suite times under a second.
- Core: `forbidden_key_substrings` and `forbidden_key_suffixes` had no cap and
  were re-scanned per field name, so a full-size substring list cost seconds over
  the same text budget. Substrings reuse the automaton and suffixes are matched
  through a reversed prefix tree, so both cost the length of the field name
  whatever the list holds. One of the seven timing shapes measures them under a
  second.
- Proxy: `elicitation/create` got no schema exemption, so a spec-compliant server
  asking the user for a `phone`, a `user_id` or anything ending in `token`
  declared it in `requestedSchema.properties` and had the whole request dropped.
  It carries an id, so the server then waited forever for an answer the client
  was never told to send. `requestedSchema` joins `inputSchema`/`outputSchema`,
  and every server-to-client request and notification the MCP specification
  defines now has a test asserting it is forwarded under the default policy.
- Proxy: the response pump parsed with `json.loads`, so a server object spelling
  the same field twice was screened last-wins and forwarded -- the leak `check`
  and `hook` refuse with exit 2. It parses with the duplicate-key refusal now and
  answers the client with a JSON-RPC parse error.
- Proxy: the JSON-RPC error and the drop log embedded the violation path
  untruncated, so a deep payload of long server-chosen field names produced an
  error far past the per-violation share the README documents. Both are trimmed
  like the CLI's report, which is where the bound now lives.
- Proxy: an empty server batch was swallowed with no forwarded message and no log
  line, the one shape that was neither answered nor logged. It is logged.
- Core: `check()` documents "never raises" and raised on an integer past
  CPython's int-to-string digit limit, which `str(value)` hits before any
  detector runs. A value that cannot be rendered has not been screened, so it is
  a `PAYLOAD_TOO_LARGE` violation instead.
- Core: an empty string in `forbidden_values`, `forbidden_key_substrings` or
  `forbidden_key_suffixes` matched everything. It is refused when the policy is
  built, like an unknown key, rather than deciding the whole payload silently.
- CLI: `hook` exited 0 on input that parsed to a shape it did not recognise, so a
  payload plainly carrying a `tool_response` was passed through unscreened when
  it arrived wrapped in an array. A non-object event exits 2 like unparseable
  input; a real event with no `tool_response` still exits 0.
- Packaging: `python -m egresswall` died with an import error rather than running
  the CLI, which is what a CI job or an editor-launched venv reaches for when the
  console script is not on PATH.
- Scripts: `scripts/refresh_evidence.py` sent a User-Agent naming a repository
  other than this package's, and the sdist ships `scripts/`. A test asserts every
  URL under `src/` and `scripts/` that names this account names this repository.
- Docs: the README said the eleven protocol field names were exempt "by exact
  name". They are matched the way forbidden names are -- case and separators
  removed -- and are exempt wherever they appear in a server message, not only
  where the specification puts them. The page says both, with a test that fails
  under the exact-name reading.
- Docs: the README claimed duplicate-key refusal and the report bounds for every
  surface while both were true of `check` and `hook` only. The proxy does both
  now, so the claim is true rather than narrowed.
- Docs: `forbidden_values` is the one rule with no case or Unicode folding, which
  no document said. "What it does not do" says it, with a test asserting both
  halves.
- Docs: `docs/comparison.md` claimed a test failed on "a figure" while nothing
  constrained the *set* of numbers on the page, so a dated numeric claim about a
  competitor could be added unchecked. `tests/test_doc_numbers.py` runs over the
  comparison page as a third document.
- Docs: the counts written as words -- three surfaces, six secret detectors, ten
  regex detectors, eleven protocol names -- were invisible to the digit test and
  pinned by nothing. Each is asserted against the code.
- Docs: the "What it does not do" list, the two install routes, the licence line
  and the `Programming Language :: Python` classifiers were asserted against the
  code and never against the page, so a promise could be deleted or inverted, a
  third install route added, the licence changed or a classifier promoted with a
  green suite. Each is pinned now, install routes by exclusivity rather than by a
  denylist of stale spellings.
- Docs: the RegLineage attribution carried a licence for a repository nothing
  under `docs/evidence/` records. The parenthetical is gone.
- Docs: the README's own `fetched <date>` citations were never compared with the
  `# fetched:` header of the evidence file they cite, and the archived label on
  the comparison page was satisfied by an incidental later mention of the word.
  Both are pinned, and the superlative word list runs over `README.md` and
  `docs/comparison.md` as well as the packaging description.
- Proxy: a server message that *is* JSON `null`, or a batch containing one, took
  the whole MCP session down with an uncaught `IndexError`: `screen_message`
  returned `None` both for "this screened clean" and for "drop this", and `null`
  is a value that screens clean. It returns what to forward and why it was not,
  so the two answers are no longer the same value.
- Proxy: `progressToken`, `_meta`, `cursor`, `nextCursor` and `requestId` are
  names the JSON-RPC and MCP specifications mandate, not data a tool chose.
  `progressToken` normalizes to a name ending in the default forbidden suffix
  `token`, so every `notifications/progress` a compliant server sent was dropped
  and progress reporting was silently dead behind the proxy. All five are exempt
  from the field-name rules now, matched the way forbidden names are -- case and
  separators removed -- and one test each says so. The values under them are
  screened exactly as before.
- Proxy: the field-name rules ran over `tools/list` as if a tool's declared
  parameters were data, so a server offering a tool that takes a `phone` or
  `rows` argument could not be listed at all -- and a client that cannot list
  tools cannot use the server. Inside a discovery result the names declared
  under `inputSchema` and `outputSchema` are exempt; nothing else in the message
  is, and every value in it is still screened.
- Core: `Policy.denies_path` re-normalized the whole accumulated dotted path at
  every node, and did it even when `denied_field_paths` was empty, so screening
  was quadratic in the depth rather than linear in the payload. The normalized
  path is carried down the walk one field name at a time.
- Core: `forbidden_values` was scanned once per entry per string, which made
  screening O(entries x bytes) -- seconds per message for a denylist of internal
  case ids. A denylist was precomputed once per policy into a prefilter and a
  fixed-width lookup at this point, and the bound rose from 64 entries to 10000.
  That lookup still scaled with the denylist and is **superseded** by the
  Aho-Corasick entry above, which is what ships.
- Core: nothing bounded how much text one payload could make the walk screen.
  `max_nodes` x `max_string_length` is not a bound anyone can wait for, so
  `max_total_length` (2 MiB by default) is the one that is measured: the walk
  refuses a payload once it has screened that much text, and the timing test
  measures seven shapes at exactly that cap.
- CLI: nothing bounded how many violations a report could name. Every violation
  carries a path built from field names the other side chose, so a verbose tool
  response amplified into the hook's stderr -- which Claude Code puts in the
  model's context. A report lists at most 20 violations and 4000 characters of
  them -- one violation's share is 200 characters, past which its path and its
  detail are truncated -- and then says how many it did not list. The count of
  violations is still exact.
- CLI: duplicate object keys were last-wins, so a payload whose first spelling of
  a field carried a value and whose second was clean was reported CLEAN and would
  leak wherever it is read first-wins. Input whose meaning depends on the parser
  is refused with exit 2 instead.
- CLI and proxy: `OverflowError` is not a `ValueError` and was caught nowhere on
  the parse paths; every one of them now answers with the documented refusal code
  for `ValueError`, `UnicodeError`, `OverflowError` and `RecursionError` alike.
- Proxy: an integer literal past this interpreter's digit limit is valid JSON
  CPython will not convert, and it was reported to the client as "the server sent
  invalid JSON". It is reported as the size limit it is, so an operator chasing it
  looks at the interpreter rather than at their server.
- Docs: `_fold`'s docstring claimed a confusable spelling of a listed field name
  could not disable the rule. Separator stripping deletes non-ASCII characters
  outright, so `аpi_key` spelled with a Cyrillic `а` is not the listed name.
  The docstring says what the code does and the README's "does not do" list says
  it too, with a test.
- Docs: the README claimed screening is "linear in the nodes and the bytes a
  payload carries", an asymptotic claim backed by one measured point. It states
  the measured bound instead -- the most text a policy allows, in each of the
  seven shapes the suite times.
- Proxy: a message carrying both a `result` and an `error` had the `error`
  forwarded unscreened, because screening stopped at the first member present.
- Proxy: a bare JSON string, a message with a non-string `method`, a message
  with no `result`/`error`/`method` member, a clean `result` beside a violating
  extra member, and a batch element that is not an object were all forwarded
  byte-for-byte.
- Proxy: the id of a violating message was echoed to the client unvalidated, so
  a server could put a value in `id` and have the error that blocked the payload
  carry it out. Only an id the client is waiting on is answered; the rest are
  dropped with the reason logged.
- Proxy: the drop log printed a violation whose path was built from
  server-controlled field names, and a server-chosen method name became the root
  of that path. Both are bounded now.
- Hook: the tool name in the stderr report is chosen by the server, so a tool
  named after a row put the row in the transcript. It is bounded like a method
  name and replaced by `<tool>` when it is not a plain name.
- Core: field names are memoized only while they are short. Screening a name
  caches it, and a name is chosen by whatever is on the other side of the
  boundary, so a server sending one large distinct key per message could have
  grown the caches without bound.
- Core: `Policy.allow_domains` was compared against a lowercased domain without
  being lowercased itself, so `Support.ACME-Corp.example` silently allowed
  nothing.
- Docs: the README and `docs/comparison.md` said the projects compared "detect
  and then rewrite", which the comparison page's own Guardrails section
  contradicts and which is untrue of Snyk Agent Scan and the Claude Code
  built-ins. Both now say most of them rewrite and name the two that refuse, and
  a doc-truth test fails if the generalisation comes back.
- Docs: the README claimed no state was kept (the proxy keeps in-flight ids in
  memory), stated a work bound (`max_nodes` x `max_string_length`) that ignored
  the per-detector factor and that no test measured, and left the counts in "How
  it is tested" -- nine pathological inputs, a 200-call conversation, the
  hostile servers -- unpinned. The bound is now the measured one: one test
  drives a line of exactly the largest size the proxy accepts through the proxy
  and asserts the exchange finishes in under two seconds, and every count is
  asserted against the suite.
- Docs: `docs/comparison.md` called MCP Gateway "the closest comparison", an
  unmeasured superlative, and pinned neither the "longest since its last push"
  superlative nor the 13 moderation categories to its evidence. The superlative
  and the taxonomy now have doc-truth tests, and `scripts/refresh_evidence.py`
  fails if the taxonomy changes.
- Docs: `ssn` and `phone` need a separator, so `123456789` and `6175550142` pass
  the screen. Said in the table rather than left to be discovered.
- Proxy: a server message that reused a live request id (a `ping`, a
  `sampling/createMessage`) consumed the pending entry, and the real result was
  then forwarded unscreened.
- Proxy: a JSON-RPC batch — a top-level array — was forwarded with no screening
  at all.
- Proxy: a server that echoed the request id with a different JSON type (`7` as
  `"7"`) had its result forwarded unscreened.
- Proxy: a `NaN` in a result, or a byte that is not valid UTF-8, crashed the
  proxy mid-session and left the real MCP server running as an orphan. The
  child is now always terminated, and a non-UTF-8 byte is screened as U+FFFD.
- Proxy: an oversized (>8 MiB) or unparseable server line was dropped silently,
  leaving the client waiting on an id that would never be answered. Both are
  now answered with a JSON-RPC error whenever the head of the line names a call
  the client is actually waiting on, and dropped with the reason on stderr when
  it does not.
- CLI: `json.loads` raises `RecursionError`, which is not a `ValueError` and was
  caught nowhere. `hook` exited 1 on deeply nested input — the code Claude Code
  treats as a non-blocking error — so the hook silently failed open; it now
  exits 2. `check` printed a traceback; it now exits 2 with a readable message.
- CLI: `check` on a file that is not UTF-8 now names the file it could not read.
- Docs: removed a sentence presented as a quotation from the Claude Code hooks
  page that the page does not contain, and corrected the claim that
  `PostToolUse` has no decision control — it has `updatedToolOutput`, which this
  package deliberately does not use, because substituting a value is a rewrite.

- Proxy: a JSON-RPC `error` object was forwarded byte-for-byte, so a server
  that put a row into `error.message` or `error.data` handed the client the
  email, the SSN and the API key inside the surface meant to stop them.
- Proxy: server-to-client notifications were forwarded unscreened, so a server
  that logged a row it had just fetched through `notifications/message` -- the
  standard MCP logging channel -- leaked it past the screen.
- Proxy: the id of an oversized or unparseable line was scraped with a regex
  and echoed back unvalidated, so a payload-internal field named `id` crossed
  the boundary inside the error that blocked the payload. Only an id the client
  is waiting on is echoed now.
- Proxy: the 8 MiB line limit was checked only after the whole line had been
  read into memory, so one very long server line drove the proxy's memory
  without bound. Lines are read bounded and abandoned as they arrive, so memory
  no longer grows with the length of a line the proxy is going to refuse.
- CLI: a policy file whose top-level JSON is not an object (`null`, `true`,
  `123`, an array) raised `TypeError` and printed a traceback, and `hook` then
  exited 1 -- the code Claude Code treats as non-blocking -- so a real
  violation was never reported. It is a policy error and exit 2 in every mode.
- Core: `bytearray` and `memoryview` values walked past every detector (a
  `bytearray` is a `Sequence`, so it was iterated as integers). Both are now
  decoded and screened like `bytes`.
- Docs: `docs/comparison.md` presented `protectai/llm-guard` as a live
  alternative without saying the repository is archived. The evidence records
  carry `archived` now and a doc-truth test fails if an archived project is not
  named as one; the "least recently maintained" superlative became the measured
  statement it can defend.
- Docs: the README said the demo runs "all four surfaces" (there are three
  surfaces and four scenarios), understated `join_token` (`hmac-sha512:` and 65
  to 128 hex digits also match), described the suffix rule as `_token` when the
  code matches the normalized name, and did not say how denied paths are
  matched. It now also states that the detectors are ASCII-literal, that a
  Unicode-confusable or base64-wrapped value passes, and that a refused server
  line is not always answerable.
- Core: MCP's `CallToolResult` carries the tool's whole payload as serialized
  JSON inside `content[].text`, and that was one string to the screen -- so
  `forbidden_keys` and `denied_field_paths`, the two rules an operator
  configures, silently never fired behind the proxy and only the value
  detectors ran. A screened string that opens a JSON object or array is parsed
  and screened again as a document under the same node, depth and text budget,
  with its own dotted root, and violations in it are reported at
  `content[0].text→<path>`. The candidate test was `\s*[{\[]` at this point and
  is `_document_candidate` in what ships -- the invisible-code-point entry above
  **supersedes** that half. A payload that is not JSON, or that spells a field
  twice, was screened as a string only at this point; the
  `EMBEDDED_DOCUMENT_UNPARSEABLE` entry above **supersedes** that and is what
  ships.
- Proxy: `_recover_id` called `json.loads` on a raw regex slice of a line that
  had **not** parsed, so a server id carrying an escaped quote (`"a\"b"`) raised
  out of the response pump: the proxy exited 2 and every call the client had in
  flight was lost. A fragment that will not parse is not a candidate id; the
  loop keeps scanning. The same crash arrived by the oversized-line path.
- Proxy: each member of a batch got its own size budget, so the documented
  `max_nodes` and `max_total_length` bounded a member rather than the message,
  and a server could multiply the cost by the number of members it put on one
  line. One budget is created per line now; a member that trips it, and every
  member after it, is refused with `PAYLOAD_TOO_LARGE` rather than forwarded.
- Proxy: a JSON number outside this interpreter's float range (`1e999`) was
  parsed to an infinity and re-emitted as the bare token `Infinity`, which is
  not JSON -- the proxy turned a message a strict client could read into one it
  could not. A non-finite number is a `PAYLOAD_TOO_LARGE` violation now, and the
  emitter refuses to write one.
- Core: the governance-vocabulary exemption was the regex `[A-Z][A-Z_]*`
  fullmatched against the value, so *any* all-caps word under a denied field
  path was policy vocabulary rather than data -- an upper-cased surname produced
  no violation. It is the closed list `DEFAULT_GOVERNANCE_TOKENS`, widened by
  `allow_tokens` and by nothing else.
- Core: `denied_field_paths` had no length bound while `forbidden_values` had
  one, so a single very long entry bought back the per-node path cost the walk
  is built to avoid. An entry over 512 characters is refused when the policy is
  built.
- CLI: any exception `main` did not list produced a Python traceback on stderr,
  whose frames carry the payload's own field names. Every failure is one line
  and exit 2 now, with a hidden `--traceback` for bug reports.
- Docs: `docs/comparison.md` opened by promising that every claim on it came
  from a checked-in response, which was wider than what is checked in: the
  per-project feature paragraphs name features no excerpt carries. The sentence
  now promises the figures, licences, tags, dates and quotations -- which are
  the parts the tests enforce -- and labels the feature paragraphs as a reading
  of the linked docs.
- Docs: the README claimed `./scripts/check.sh` runs "exactly what CI runs"
  while CI had a step the script did not. The script runs `uv sync --group dev`
  too, the claim is scoped to the checks CI runs before it installs the built
  wheel, and a doc-truth test now asserts the two lists are *equal* rather than
  overlapping. The proxy's pass-through of the server's own stderr, and the
  exit status the README states for a refused payload, are both stated and
  tested now as well.

### Added
- `egresswall.screen(payload, policy, where=...)` raises `EgressViolation`;
  `egresswall.check(payload, policy)` returns a list of `Violation`.
- `egresswall.Policy`: denied field paths, forbidden field names (with
  substring and suffix rules), forbidden literal values, per-class detectors,
  allowlisted governance tokens and email domains, `exempt_keys` for a name the
  field-name rules must skip, `refuse_unparseable_embedded` for whether a string
  that opens like a serialized document and will not parse is refused, and
  `max_depth` / `max_nodes` / `max_string_length` / `max_total_length` limits
  that fail closed.
- Ten detectors: `email`, `ssn`, `phone`, `join_token`, `private_key`,
  `aws_access_key`, `github_token`, `anthropic_key`, `openai_key`,
  `bearer_token`.
- Nine violation codes, exported as constants and as `VIOLATION_CODES`.
- `egresswall check FILE.json` (`--policy`, `--format text|json`, exit 1 on
  violations).
- `egresswall hook`: a Claude Code `PostToolUse` hook that screens
  `tool_response` and exits 2 with the reason on stderr.
- `egresswall proxy -- <server command>`: an MCP stdio proxy that replaces a
  violating result with a JSON-RPC error.
- `docs/evidence/`: the API responses and source excerpts behind every figure
  and quotation in `README.md` and `docs/comparison.md`, refreshed by
  `scripts/refresh_evidence.py` (deliberately not run in CI) and enforced by
  `tests/test_comparison_truth.py`.
- Doc-truth tests for the default limits, the dependency claims, the CI matrix
  and every quotation, for the "does not keep state, phone home or write files"
  claim (no module imports `socket`, `ssl`, `urllib`, `http` or `requests`, and
  a `check` run leaves its working directory as it found it), and for the
  sdist, which must ship exactly one package.

### Notes
- Extracted from [RegLineage](https://github.com/Alex-lop/RegLineage)
  (`src/reglineage/agent/egress.py` and `src/reglineage/mcp_runtime/server.py`),
  decoupled from that project's plan model and hardened: unambiguous regexes,
  explicit size limits, and a narrower governance-vocabulary exemption
  (`DENY` still passes; `NG-88231` no longer does).
