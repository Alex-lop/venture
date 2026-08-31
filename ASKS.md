# ASKS — approval queue for RED actions and things only Alex can answer

Newest on top. Each ASK: what, why, cost, deadline, what happens if declined. Reply inline (`APPROVED` / `DECLINED` / edits) and the agent picks it up next session. Nothing here has been done.

---

## Session 2 batch — 2026-08-30 (each ASK has a default and the date it applies; nothing waits)

## ASK-015 — Publish to PyPI: one command per package (the agent's publish step was declined by the harness permission layer) — **no default; the upload is yours**
- **What:** `agent-plan-lint` 0.1.0 is released on GitHub — [https://github.com/Alex-lop/agent-plan-lint](https://github.com/Alex-lop/agent-plan-lint), tag `v0.1.0`, 437 passed / 51 skipped on its pinned 3.11, 488 collected — but not on PyPI: the agent's session declined the publish step (the keychain-token read + `uv publish`), and no other session may route around that decline. From a clone of the repository at `v0.1.0`:
  `uv build && UV_PUBLISH_TOKEN="$(security find-generic-password -s pypi-token -w)" uv publish dist/*`
  The same one-liner applies to `egresswall` and `guardrail-checkup` when their repositories exist; the agent lists each here as its repo and tag go live. The standing approval for PyPI is already yes — the block is the tool, not the policy.
- **After the upload:** the agent adds the site's `RELEASED` flag and install line, the `pip install` sentence on Graphene #14, and `{PYPI_URL}` in `outreach/queue.md` §A, and the launch order in queue.md §C can start.
- **Cost:** $0. **If not done:** the package is installable from source only (`uv pip install git+https://github.com/Alex-lop/agent-plan-lint`) and none of the launch drafts can be posted.

## ASK-014 — Veto window: package and family names (default applies 2026-09-02)
- **What:** `agent-plan-lint` (was plan-lint — PyPI name taken by an abandoned 2025 project), `egresswall` (was egress-guard — PyPI name taken 2026-08-29 by an adjacent project), `guardrail-checkup` (was agent-autopsy — "Autopsy" is a registered forensic-tool trademark), `readonly-gateway` and `change-receipt` unchanged, docs-site family `guardposts`. Evidence and runners-up: `research/naming.md` §3.
- **Cost:** $0. **If vetoed:** the runner-up in naming.md is used; nothing has been published under any name yet.

## ASK-013 — Veto window: graphene-site LICENSE = Apache-2.0 (default applies 2026-09-02)
- **What:** https://github.com/Alex-lop/graphene-site/pull/1 adds Apache-2.0 (matches the product it markets; the site's scripts are code). Alternative: CC BY for the page copy and images. **Cost:** $0.

## ASK-012 — Merge eight verified PRs on your own repos (one click each)
- **What:** LICENSE copyright lines — Graphene #12, RegLineage #9, Nemisis #1 (CI green), graphene-site #1 (no CI); deployment images build + `procps` — Graphene #13 `fix/deploy-image-procps` (two adversarial verification passes; both images build and run `process_control` in a container); customer-voice READMEs — Graphene #14, RegLineage #10, Nemisis #2 (each audited to zero blockers/majors; a one-line RELEASE-LINK commit follows the package release). (GitHub Pages for `Alex-lop/guardposts` is already enabled and built: https://alex-lop.github.io/guardposts/.) These are GREEN under CLAUDE.md §2, but the harness's permission layer declined the agent's merge action, so the clicks are yours. Do **not** delete the branches (RED).
- **Cost:** $0. **If declined:** branches stay open; the customer-voice README PRs later in Track I will stack on them.
- **Update 2026-08-31 04:50:** Nemisis #2 had become CONFLICTING (your 12 commits to Nemisis main on 08-30 evening landed after the branch was cut) with CI failing on a hard-coded bundle digest in the README's pasted console block. main was merged into the branch (merge commit ec0336e — no force-push), 54 README claims re-verified against the merged tree and 11 corrected, 270 tests + ruff + mypy + CI green; the PR is MERGEABLE again. All eight PRs are clickable.

## ASK-011 — Rewrite the public history of `Alex-lop/venture` to purge third-party names? (RED: history rewrite) — default **NO**, applies 2026-09-06
- **What:** the session-1 commits still contain the original wording (a person's name, account handle, school, and the leaked-file list). This session's redaction commit fixes the tree going forward; history is untouched. Option (a) leave it — the default; option (b) `git filter-repo` + force-push, which rewrites every SHA and breaks any existing clone. **Cost:** $0. **Recommendation:** (a) unless the third party asks; send ASK-002's message either way.

## ASK-010 — Job/co-op search in parallel with the swarm? — default **run both**, applies 2026-09-06 (`DECISION.md` v4 §5)
- **What:** `research/demand.md` finds payroll is the only shape with dated dollar transactions in this category (Boston bands $130k–$340k, reqs named). The agent prepares req lists and application drafts under `private/outreach/` and contacts nobody; ~6 h/week of yours. **If declined:** the hours stay on Tracks H and I.

## ASK-007 — **RESOLVED 2026-08-30** (`private/PRINCIPAL.md` filled: US resident, TA grader, 12 h/week, standing approvals yes ×4, Track H yes). Original text kept for the record — Fill in §0 of `CLAUDE.md`, above all your visa/co-op status (10 minutes)
- **What:** Answer the blanks the agent could not infer: how to address you; skills you consider strengths / would rather not lean on; things you refuse to build; accounts you already have and are willing to use (Vercel, Stripe, registrar, Cloudflare, Railway/Fly…); your **citizenship/visa status** (F-1/J-1 changes everything — see `CLAUDE.md` §0); whether you have a **co-op signed or upcoming** and whether its agreement has an invention-assignment clause; whether you hold any paid NU position (TA/RA/grader).
- **Why:** The red team showed 10 of the plan's 11 weekly hours sit on tracks whose legality depends on this answer (consulting income and SaaS revenue are exactly what an F-1 without CPT/OPT cannot do; DHS: a DSO who knows must terminate the SEVIS record). The policy research also found a co-op invention-assignment agreement and Massachusetts SaaS sales tax are the two things that can actually hurt you. All three depend on facts only you have.
- **Cost:** $0. **Deadline:** before DECISION.md sign-off. **If declined:** the agent continues on inferred strengths and treats visa/co-op as unknown risks in every plan.

## ASK-009 — Approve outreach batch #1 (you send; nothing is sent by the agent)
- **What:** `outreach/queue.md` holds the 20-second Venture Café opener and a follow-up email offering a **free, unpriced 60-minute agent autopsy** to 12 named Boston/Cambridge companies whose own job posts name Claude Code/Cursor/Codex (Hi Marley, CloudZero, Reprise, Suno, Lumafield, Kodex, Tulip, Jellyfish, Fairmarkit, Lila Sciences, EverQuote, ClearGov — each with a published role email or contact form and the exact job-post quote to personalize with). All contact channels are the firms' own published business channels; no individuals were scraped. Approve all, some, or edit the copy inline. *(The six Track B practitioner calls that were in this batch are **withdrawn**: B was killed by the EEA-portal finding before anything was sent; the drafts stay in the queue as a record.)*
- **Why:** These are the first real-world signals the plan can get, and every one is RED (contacting a human). No price is named, by design (DECISION.md v3).
- **Cost:** $0. Your time: ~90 min to send 12 messages after Venture Café. **Deadline:** follow-ups within 24 h of Thu 2026-09-03; cold ones by 2026-09-08. **If declined:** nothing is sent; A stalls at zero signal and C continues.

- **Update 2026-08-30:** the named contacts moved to `private/outreach/named-targets.md`; the Session-1 opener and follow-up are superseded by `outreach/track-h/` (verified runbook, opener, follow-ups). Still yours to send; nothing has been sent.
## ASK-008 — Before any paid engagement: three legal items (all $0 to start)
- **What:** (a) Book the **Community Business Clinic** (ASK-005c) to review a one-page fixed-price engagement letter the agent will draft (scope, fees-paid liability cap, no-warranty language, data handling for repo access); (b) confirm you are engaging as an independent contractor under **M.G.L. c.149 §148B** (the three-prong ABC test — the clinic can advise); (c) decide on **E&O / professional-liability insurance** for production-repo access — likely unaffordable under the $1,000 cap, which argues for keeping engagements #1–2 small, scoped, and read-only where possible. None of this is legal advice; it is the list the red team said v1 omitted.
- **Cost:** $0 now. **Deadline (re-set by `DECISION.md` v4):** items (a)+(b) closed by 2026-10-01; the first engagement ≥ $750 is gated on them by 2026-10-31. **If declined:** the agent will not draft an engagement letter and A stays a free experiment.

## ASK-006 — Choose a legal business address (not a dorm, not a PO box)
- **What:** Decide what address you can use for Stripe onboarding and, later, a Boston DBA. NU housing policy bars business use of a residence hall/mailbox; Boston City Clerk and Stripe both reject PO boxes.
- **Why:** This small logistical fact gates payments. **Cost:** $0 (a family address works). **Deadline:** before the first invoice. **If declined:** no Stripe, no first dollar.

## ASK-005 — Northeastern free resources (three emails/forms; agent will draft each)
- **What:** (a) Register for the **IDEA "Ready" stage** orientation (free; pipeline to up to $30,000 non-dilutive Gap Fund + mentors) — https://damore-mckim.northeastern.edu/idea/ ; (b) apply to **IP CO-LAB** (free trademark/IP clinic, any NU student) once a product name exists — https://law.northeastern.edu/experience/clinics/ip-clinic ; (c) contact the **Community Business Clinic** before signing any customer contract or co-op agreement — https://law.northeastern.edu/experience/clinics/community-business/ .
- **Why:** Free money and free counsel worth more than the $1,000 cap. **Cost:** $0. **Deadline:** IDEA cohorts run per semester — check the fall deadline this week. **If declined:** nothing breaks; you pay for what could be free.

## ASK-004 — Confirm IP cleanliness of the three hackathon repos (5 minutes)
- **What:** Confirm in writing here that **no hackathon/sponsor terms** (AllThingsAgentic, DataHub, NVIDIA×Nexius) grant sponsors rights over Graphene, RegLineage, or Nemisis; and that the stray first commit in RegLineage — made by a different GitHub account at repo creation (identifying details in `private/THIRD-PARTY.md`) — is a template/scaffold with no authorship claim. Then let the agent fill the `Copyright [yyyy] [name]` lines in all three LICENSE files and add a LICENSE to `graphene-site` (GREEN once you confirm).
- **Why:** The readers could not find sponsor terms in any repo, which is not the same as none existing. **Cost:** $0. **Deadline:** before any of that code ships to a customer. **If declined:** the agent treats all three as encumbered and builds only from scratch.

- **Update 2026-08-30:** the copyright lines were filled under CLAUDE.md v2 §2 (decide-with-default; PRs in ASK-012). The sponsor-terms / stray-commit confirmation is still yours.
## ASK-003 — Delete the public branch `AC-Washing-Well@commit-changes`
- **What:** `git push origin --delete commit-changes` on `Alex-lop/AC-Washing-Well`. The branch holds 51 blobs: Northeastern CS2800 coursework solutions and ~2.7 MB of IMC Prosperity competition CSVs, publicly visible.
- **Why:** Academic-integrity exposure for you, and the brief forbids touching anything university-related without approval. Destructive (branch deletion), so the agent will not do it unapproved. **Cost:** $0. **Deadline:** today. **If declined:** it stays public.

## ASK-002 — Tell the owner of the other GitHub account about a secret leaked in their public repo — **OPEN**
- **What:** A non-expiring API **client secret** (and client id) is committed in plaintext in several files of a **public** repository belonging to a different person — the account that was the `gh` login on this machine. The exact account, repository and file list are in **`private/THIRD-PARTY.md`** and are deliberately in no tracked file. Only the account owner can fix it: rotate the secret at the provider, delete the scratch scripts, and purge them from git history (a plain `git rm` leaves the secret in history).
- **Why:** Contacting a human is RED. The agent did not contact anyone, and will not.
- **Also note — this is the part that still needs your decision:** the redaction passes clean the **working tree only**. Earlier commits already pushed to the public `Alex-lop/venture` still carry the pre-redaction wording of several tracked files, and `outreach/crm.csv` is still present at those commits. The full inventory of what remains readable, and the options for dealing with it, are in **`private/THIRD-PARTY.md`** and are in no tracked file. Scrubbing published history is a rewrite on a public repo — RED under `CLAUDE.md` §2 — so it needs your written approval; the alternative is deleting/recreating the public repo, which is also RED. Nothing here is reversible by the agent alone.
- **Cost:** $0. **Deadline:** today. **If declined:** the secret stays live.

## ASK-001 — Re-authenticate `gh` as `Alex-lop` — **RESOLVED 2026-08-30**
- **What it was:** this machine's `gh` CLI was logged in as a different person's GitHub account, not yours, so any GitHub write from here would have been attributed to someone else. The agent made no GitHub write action while that was true.
- **Resolution, verified today:** `gh api user --jq '.login'` → `Alex-lop`; `gh auth status` shows `Alex-lop` as the active account. GitHub writes are unblocked. *(Housekeeping, optional: the other account is still in the keyring as inactive — `gh auth logout` removes it. Identifying details are in `private/THIRD-PARTY.md`.)*
- **Cost:** $0. **Nothing further is needed from you on this ASK.**

---

## Pending (will be written after DECISION.md is signed off)
- Domain purchase for the chosen venture (first approved spend, ≤ $15/yr).
- Stripe Individual/Sole-Proprietor account (free; needs SSN + address; get a free IRS EIN first so clients never see your SSN on a W-9).
- MassTaxConnect sales-tax registration **before the first SaaS sale** (MA taxes prewritten software accessed remotely at 6.25%; consulting/custom work is generally not taxed — verify with DOR; not legal/tax advice).
- ~~Outreach batch #1~~ → now ASK-009.
