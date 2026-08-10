---
name: session-log
description: "The Snowflake row written per booth visitor: table contract, insert rules, consent wording status, and the queries that turn the booth's own output into a second live demo. Verified against LOCO4COCO.BOOTH.SESSIONS on 2026-08-05."
---

# Session log

One row per visitor in `LOCO4COCO.BOOTH.SESSIONS` (account `SFSEEUROPE-PG_LONDON`). It serves two purposes: the lead list for SE follow-up, and a dataset the booth generates about itself — which makes *"CoCo, which POC idea was most popular today?"* a legitimate second demo, run on data the audience just created.

## Table

Created and write-tested 2026-08-05. Columns:

| Column | Type | Notes |
|---|---|---|
| `session_id` | STRING | defaults `UUID_STRING()` |
| `session_ts` | TIMESTAMP_LTZ | defaults `CURRENT_TIMESTAMP()` |
| `event_city` | STRING | `London` / `Paris` |
| `language_code` | STRING | `en` / `fr` — which copy deck ran |
| `first_name` | STRING | as given |
| `role_stated` | STRING | their words, not a bucket |
| `email` | STRING | null when not provided |
| `consent_given` | BOOLEAN | must be TRUE for `email` to be non-null |
| `email_provided` | BOOLEAN | |
| `email_sent` | BOOLEAN | truthful — never record a send that failed |
| `sector` | STRING | R1.Q1 |
| `pain_chosen` | STRING | R1.Q2 |
| `dream_chosen` | STRING | R1.Q3 |
| `data_on_hand` | STRING | R2.Q1 |
| `audience` | STRING | R2.Q2 |
| `poc_archetype` | STRING | archetype ID |
| `poc_name` | STRING | the name shown to them |
| `guide_forked` | STRING | slug, or `none-from-scratch` |
| `features` | ARRAY | feature names |
| `readiness_score` | NUMBER(1,0) | 0–5 |
| `weakest_point` | STRING | what to firm up |
| `duration_seconds` | NUMBER(5,0) | measured, not estimated |
| `se_operator` | STRING | who ran the booth |
| `notes` | STRING | free text |

## Insert rules

- **Always insert, even on failure.** A visitor who abandoned halfway is useful signal. Write what you have and note it.
- **`email_sent` must be truthful.** If the Gmail send failed, `FALSE`. A lead list that overstates delivery is worse than none.
- **No email without consent.** If `consent_given` is FALSE, store `email` as NULL. Do not keep it "just in case".
- **`duration_seconds` is measured** from first message to handoff. This is the evidence the five-minute claim is real, so do not estimate it.
- **Escape apostrophes** by doubling them. Verified necessary: `Children''s Services Analyst` and `The answer''s buried...` are realistic values, and an unescaped apostrophe breaks the insert. Test values with accents too — `Chloé` round-trips correctly.
- Use `LOCO4COCO_WH` (X-Small, `AUTO_SUSPEND = 60`, bound to `LOCO4COCO_RM`). Do not let it fall back to the account default, or spend lands on the wrong monitor.

## Consent

**Not yet drafted. Do not invent final wording.** Capturing name, role and email at a public event needs events/marketing and privacy sign-off. `OPEN.CONSENT` is a placeholder until that lands.

What it must cover: what is stored, why, who follows up, how to opt out, and that the blueprint email is the immediate purpose. Until approved, the booth can still run consent-free by skipping the email field and letting visitors photograph the on-screen blueprint — the activation degrades gracefully.

## Booth demo queries

Run these live on the booth screen. They work on a handful of rows, which matters at 10am on day one.

Most popular POC shapes:
```sql
SELECT poc_archetype, COUNT(*) AS visitors,
       ROUND(AVG(readiness_score), 1) AS avg_readiness
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE session_ts::DATE = CURRENT_DATE()
GROUP BY poc_archetype
ORDER BY visitors DESC;
```

Are we actually under five minutes?
```sql
SELECT COUNT(*) AS sessions,
       ROUND(AVG(duration_seconds)) AS avg_seconds,
       MAX(duration_seconds) AS worst_seconds,
       SUM(IFF(duration_seconds > 300, 1, 0)) AS over_five_min
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE session_ts::DATE = CURRENT_DATE();
```

What blocks people most (the genuinely interesting finding):
```sql
SELECT weakest_point, COUNT(*) AS n
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE weakest_point IS NOT NULL
GROUP BY weakest_point
ORDER BY n DESC;
```

Which sectors bring which pains:
```sql
SELECT sector, pain_chosen, COUNT(*) AS n
FROM LOCO4COCO.BOOTH.SESSIONS
GROUP BY sector, pain_chosen
HAVING COUNT(*) > 1
ORDER BY n DESC;
```

Follow-up list for the SE team:
```sql
SELECT session_ts::DATE AS day, first_name, role_stated, email,
       poc_name, poc_archetype, readiness_score, weakest_point
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE consent_given AND email IS NOT NULL
ORDER BY readiness_score DESC, session_ts;
```

Ordering by readiness descending puts the warmest leads first — someone scoring 5/5 has data, a user and an outcome, and is worth calling this week.
