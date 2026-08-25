# Privacy notice: template for review

**Status: DRAFT for Snowflake legal / privacy / marketing review. Not approved.**

I am not a lawyer and this is not legal advice. This is a starting point drafted
against what the activation actually collects, so the review conversation can be
about wording rather than about fact-finding. **Nothing here should go on a stand
until someone who owns privacy at Snowflake has signed it off**, and they may well
replace it with a standard event-capture notice that already exists — ask first,
because Snowflake runs events constantly and a corporate template almost
certainly exists for exactly this.

## What is actually collected (verified against the code, 2026-08-24)

Personal data, typed by the visitor:

| Field | Where | Column |
|---|---|---|
| First name | The letter | `SESSIONS.FIRST_NAME` |
| Employer | The letter ("Where you work") | `SESSIONS.COMPANY` |
| Their business problem, free text, 400 chars | The letter | `SESSIONS.PROBLEM_STATEMENT` |
| Their MVP description, free text | The workshop | `TURNS.VISITOR_INPUT` |
| Anything typed into an "Other" box | Library, marketplace | `TURNS.VISITOR_INPUT` |

Not personal data, but stored alongside it: industry, data types held, platforms,
marketplace selections, resolved archetype, features, readiness score, timings,
token counts, and the presigned URL of their document.

**No email address is collected.** It was removed on 2026-08-24. **No surname, no
phone number, no job title, no photograph.** Nothing is collected without the
visitor typing it.

Free text is the risk. A visitor describing their business problem may type
anything, including a customer name, a patient context or a colleague's name. We
do not control that, we cannot filter it reliably in five minutes, and we store it
verbatim because its verbatim-ness is the point — it is the only place the visitor
says *why*, and the only thing an SDR can quote back.

## Where it goes and for how long

- A Snowflake account controlled by Snowflake (`LOCO4COCO.BOOTH.SESSIONS` and
  `TURNS`).
- A document on an internal Snowflake stage, handed to the visitor as a QR code.
  The presigned link expires after **7 days**.
- Nothing is sent to a third party. No analytics, no tracking pixel, no cookies —
  the client is one HTML file served from localhost.
- The booth laptop holds a local `state.json` for the current visitor only, reset
  between visitors, plus a local `cost.jsonl` of timings and token counts.

**Retention is currently unbounded, and that is a gap.** There is no automatic
deletion. A retention period needs to be decided and implemented — a storage
lifecycle policy or a scheduled task on `SESSIONS` and `TURNS` would do it.

## Draft on-stand notice (short form)

Intended to sit under the letter, one tap from the first screen. Deliberately
short: a visitor on a five-minute clock will not read a page of terms, and a
notice nobody reads protects nobody.

> **What we do with this**
>
> We keep your first name, where you work, and what you type about your problem,
> so a Snowflake colleague can follow up about what you built here. We store it in
> Snowflake's own systems. We do not share it with anyone else, and we do not use
> cookies or tracking.
>
> Your document link works for 7 days. Please do not type anything confidential,
> or anyone else's personal details.
>
> Want it deleted, or want to see it? Ask anyone on the stand, or email
> [PRIVACY CONTACT]. Full detail: [LINK TO SNOWFLAKE PRIVACY NOTICE].

## Questions the reviewer needs to answer

These are the decisions I cannot make:

1. **Lawful basis.** Legitimate interest (business development at a trade event)
   or consent? If consent, it must be recorded per visitor — there is currently
   nowhere to store it, so that is a schema change, not just copy.
2. **Retention period**, and who implements the deletion.
3. **Is this a marketing capture?** If the intent is SDR follow-up, this may fall
   under the same rules as any other event lead capture, in which case Snowflake's
   existing event process should be reused rather than reinvented.
4. **How is follow-up actually done** now that no email is collected? A visitor
   who wants contact has to give their details some other way — probably the
   normal stand lead-capture mechanism, which has its own notice.
5. **The wording of the "do not type anything confidential" line.** It is doing a
   lot of work and needs to be phrasing the reviewer is happy with.
6. **Where the notice must appear**: on the stand as printed signage, on screen,
   or both.
7. **Paris.** A French-language version, and any France-specific requirement.

## What is implemented, and what is not

Implemented: no email collection; presigned links expire in 7 days; nothing shared
with third parties; no cookies or analytics; state reset between visitors.

**Not implemented, pending the review above:** the on-screen notice itself, a
consent record, an automatic retention/deletion policy, and a documented
subject-access or erasure route.
