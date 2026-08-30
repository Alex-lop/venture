# ASKS — approval queue for RED actions and things only Alex can answer

Newest on top. Each ASK: what, why, cost, deadline, what happens if declined. Reply inline (`APPROVED` / `DECLINED` / edits) and the agent picks it up next session. Nothing here has been done.

---

## ASK-007 — **FIRST.** Fill in §0 of `CLAUDE.md`, above all your visa/co-op status (10 minutes)
- **What:** Answer the blanks the agent could not infer: how to address you; skills you consider strengths / would rather not lean on; things you refuse to build; accounts you already have and are willing to use (Vercel, Stripe, registrar, Cloudflare, Railway/Fly…); your **citizenship/visa status** (F-1/J-1 changes everything — see `CLAUDE.md` §0); whether you have a **co-op signed or upcoming** and whether its agreement has an invention-assignment clause; whether you hold any paid NU position (TA/RA/grader).
- **Why:** The red team showed 10 of the plan's 11 weekly hours sit on tracks whose legality depends on this answer (consulting income and SaaS revenue are exactly what an F-1 without CPT/OPT cannot do; DHS: a DSO who knows must terminate the SEVIS record). The policy research also found a co-op invention-assignment agreement and Massachusetts SaaS sales tax are the two things that can actually hurt you. All three depend on facts only you have.
- **Cost:** $0. **Deadline:** before DECISION.md sign-off. **If declined:** the agent continues on inferred strengths and treats visa/co-op as unknown risks in every plan.

## ASK-009 — Approve outreach batch #1 (you send; nothing is sent by the agent)
- **What:** `outreach/queue.md` holds the 20-second Venture Café opener and a follow-up email offering a **free, unpriced 60-minute agent autopsy** to 12 named Boston/Cambridge companies whose own job posts name Claude Code/Cursor/Codex (Hi Marley, CloudZero, Reprise, Suno, Lumafield, Kodex, Tulip, Jellyfish, Fairmarkit, Lila Sciences, EverQuote, ClearGov — each with a published role email or contact form and the exact job-post quote to personalize with). All contact channels are the firms' own published business channels; no individuals were scraped. Approve all, some, or edit the copy inline. *(The six Track B practitioner calls that were in this batch are **withdrawn**: B was killed by the EEA-portal finding before anything was sent; the drafts stay in the queue as a record.)*
- **Why:** These are the first real-world signals the plan can get, and every one is RED (contacting a human). No price is named, by design (DECISION.md v3).
- **Cost:** $0. Your time: ~90 min to send 12 messages after Venture Café. **Deadline:** follow-ups within 24 h of Thu 2026-09-03; cold ones by 2026-09-08. **If declined:** nothing is sent; A stalls at zero signal and C continues.

## ASK-008 — Before any paid engagement: three legal items (all $0 to start)
- **What:** (a) Book the **Community Business Clinic** (ASK-005c) to review a one-page fixed-price engagement letter the agent will draft (scope, fees-paid liability cap, no-warranty language, data handling for repo access); (b) confirm you are engaging as an independent contractor under **M.G.L. c.149 §148B** (the three-prong ABC test — the clinic can advise); (c) decide on **E&O / professional-liability insurance** for production-repo access — likely unaffordable under the $1,000 cap, which argues for keeping engagements #1–2 small, scoped, and read-only where possible. None of this is legal advice; it is the list the red team said v1 omitted.
- **Cost:** $0 now. **Deadline:** before the first invoice (earliest 2026-10-15). **If declined:** the agent will not draft an engagement letter and A stays a free experiment.

## ASK-006 — Choose a legal business address (not a dorm, not a PO box)
- **What:** Decide what address you can use for Stripe onboarding and, later, a Boston DBA. NU housing policy bars business use of a residence hall/mailbox; Boston City Clerk and Stripe both reject PO boxes.
- **Why:** This small logistical fact gates payments. **Cost:** $0 (a family address works). **Deadline:** before the first invoice. **If declined:** no Stripe, no first dollar.

## ASK-005 — Northeastern free resources (three emails/forms; agent will draft each)
- **What:** (a) Register for the **IDEA "Ready" stage** orientation (free; pipeline to up to $30,000 non-dilutive Gap Fund + mentors) — https://damore-mckim.northeastern.edu/idea/ ; (b) apply to **IP CO-LAB** (free trademark/IP clinic, any NU student) once a product name exists — https://law.northeastern.edu/experience/clinics/ip-clinic ; (c) contact the **Community Business Clinic** before signing any customer contract or co-op agreement — https://law.northeastern.edu/experience/clinics/community-business/ .
- **Why:** Free money and free counsel worth more than the $1,000 cap. **Cost:** $0. **Deadline:** IDEA cohorts run per semester — check the fall deadline this week. **If declined:** nothing breaks; you pay for what could be free.

## ASK-004 — Confirm IP cleanliness of the three hackathon repos (5 minutes)
- **What:** Confirm in writing here that **no hackathon/sponsor terms** (AllThingsAgentic, DataHub, NVIDIA×Nexius) grant sponsors rights over Graphene, RegLineage, or Nemisis; and that the stray first commit in RegLineage by `rasbhalerao-rgb` (2026-07-17, repo creation) is a template/scaffold with no authorship claim. Then let the agent fill the `Copyright [yyyy] [name]` lines in all three LICENSE files and add a LICENSE to `graphene-site` (GREEN once you confirm).
- **Why:** The readers could not find sponsor terms in any repo, which is not the same as none existing. **Cost:** $0. **Deadline:** before any of that code ships to a customer. **If declined:** the agent treats all three as encumbered and builds only from scratch.

## ASK-003 — Delete the public branch `AC-Washing-Well@commit-changes`
- **What:** `git push origin --delete commit-changes` on `Alex-lop/AC-Washing-Well`. The branch holds 51 blobs: Northeastern CS2800 coursework solutions and ~2.7 MB of IMC Prosperity competition CSVs, publicly visible.
- **Why:** Academic-integrity exposure for you, and the brief forbids touching anything university-related without approval. Destructive (branch deletion), so the agent will not do it unapproved. **Cost:** $0. **Deadline:** today. **If declined:** it stays public.

## ASK-002 — Tell Juan about the leaked Spotify secret in `datboiathop/records`
- **What:** A non-expiring Spotify **client secret** (and client id) is committed in plaintext at line 2 of `test-spotify.js`, `test-playlist.js`, `get-postman-token.js`, `test-postman.js`, plus a Firebase project config in `firebase-applet-config.json`, in the **public** repo `datboiathop/records`. The fix is the account owner's: rotate the secret in the Spotify developer dashboard, delete the 12 scratch scripts, and purge them from git history (a plain `git rm` leaves the secret in history).
- **Why:** Contacting a human is RED. The agent did not contact anyone. **Cost:** $0. **Deadline:** today. **If declined:** the secret stays live.

## ASK-001 — Re-authenticate `gh` as `Alex-lop` (2 minutes) — BLOCKS ALL GITHUB WRITES
- **What:** This machine's `gh` CLI is logged in as **`datboiathop`**, which is Juan Lopez's account (UPenn), not yours. Run `gh auth login` (or `gh auth switch`) as `Alex-lop`. Until then the agent will make **no** GitHub write action (no PRs, issues, comments, branch pushes) from this machine, because they would be attributed to someone else.
- **Why:** Every A-track and OSS plan needs PRs under your name. **Cost:** $0. **Deadline:** before any PR. **If declined:** GitHub-facing work is drafted to files only.

---

## Pending (will be written after DECISION.md is signed off)
- Domain purchase for the chosen venture (first approved spend, ≤ $15/yr).
- Stripe Individual/Sole-Proprietor account (free; needs SSN + address; get a free IRS EIN first so clients never see your SSN on a W-9).
- MassTaxConnect sales-tax registration **before the first SaaS sale** (MA taxes prewritten software accessed remotely at 6.25%; consulting/custom work is generally not taxed — verify with DOR; not legal/tax advice).
- ~~Outreach batch #1~~ → now ASK-009.
