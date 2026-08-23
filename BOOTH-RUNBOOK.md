# Loco for CoCo - booth runbook

Snowflake World Tour. London first (English), Paris second (French).

The activation: a visitor answers five light questions in under five minutes and leaves with an emailed POC blueprint - their idea in their own words, the Snowflake developer guide to fork, the features with doc links, a readiness score, and a kick-off prompt to paste into CoCo on a free trial.

## What is built and verified

| Component | State |
|---|---|
| `loco4coco` skill - the five-minute visitor flow | Written |
| `loco4coco-ops` skill - setup, pre-flight, analytics | Written |
| 10 POC archetypes with resolution rules and scoring | Written, corrected after dry runs |
| 44 curated developer guides, archetype-tagged | **All verified HTTP 200 on 2026-08-05** |
| Guides verifier script | **Tested** - reports 44 curated, 0 failing, 0 redirecting |
| English copy deck | Written |
| `LOCO4COCO.BOOTH.SESSIONS` | **Created and write-tested** (apostrophes, accents, arrays) |
| `LOCO4COCO_WH` + `LOCO4COCO_RM` | **Created and verified** - X-Small, 60s suspend, quota 20, notify 75%/90%, suspend 100%, `notify_users` non-empty |
| Booth analytics queries | **Run against dry-run data** |
| Email delivery via Gmail MCP | **NOT VERIFIED - blocking** |
| Wall-clock timing | **NOT VERIFIED - needs a human** |
| French copy deck | Not started, by design |

## Two things must happen before London

### 1. Prove the email path

The single blocking item. Verified on 2026-08-05, by direct test:

- Google Drive sharing to **any** external address is blocked by Snowflake Workspace policy: *"an item cannot be shared outside of Snowflake Inc."* This also fails with notification off, so it is permission creation that is blocked, and it cannot be fixed without Workspace admin rights.
- `SYSTEM$SEND_EMAIL` reaches only verified email addresses of users in the same account. Visitors are impossible.
- Snowflake presigned stage URLs are genuinely public and need no login, but always serve `application/octet-stream`, so a browser downloads rather than renders. (Also: `curl -I` returns 403 because the signature is method-specific - test with GET.)

So the **Natoma Gmail MCP** is the only route to a visitor's inbox. It was registered during this build but never exercised, because HTTP MCPs need OAuth on first connect and a fresh session before their tools load.

Test it in a fresh session, and test it properly:

- Send to a **real external non-Snowflake address you control**. A colleague on `@snowflake.com` would pass while the real case fails.
- Confirm it arrives, is not in spam, and that the prompt block **copies cleanly on a phone**.

If it cannot be made to work, the booth still runs: drop the email field, show the blueprint on screen, invite a photo. Say so in the opening rather than collecting an address you cannot deliver to.

### 2. Time it with real people

Three personas were traced end to end - an operations manager, a data engineer and a public sector governance officer. That exercise found and fixed three real defects (see below). It did **not** establish timing: the durations in the session table are my estimates, not measurements. No human has run this.

Before London, run it with three people who have never seen it, stopwatch running, and record actual `duration_seconds`. Two things to watch:

- Reading the fortune and the reveal aloud takes longer than reading it silently.
- A visitor who thinks about `R1.Q2` rather than skimming it will take 30 seconds on that question alone.

If sessions land over five minutes, cut a beat - do not relax the clock. The five-minute promise is in the brief and in the opening line.

## Defects found by the dry runs

Recorded because they show the flow was wrong in ways that were not obvious on paper:

1. **Q3 overrode Q2, discarding the pain.** "Too much comes in to sort by hand" plus "show me a picture" routed to a generic dashboard, throwing away the classification that was the actual problem - and the triage fork is already a dashboard. Fixed: Q2 wins by default, Q3 shapes the deliverable, override only when genuinely incompatible.
2. **The readiness rubric was too generous.** Two of three personas scored 5/5. A score almost everyone aces is flattering, not diagnostic. Fixed with explicit "do NOT award" conditions; the same three personas now score 3, 2 and 4.
3. **No copy existed for a 5/5.** `REVEAL.SCORE` interpolates a weakest point that does not exist at full marks, so it would have rendered a dangling sentence. Added `REVEAL.SCORE_PERFECT`.

## Daily operation

Every morning, run `loco4coco-ops` pre-flight - eight checks, each of which must *prove* a capability rather than observe that something exists. That distinction is the whole lesson of this build: three delivery routes looked available and were blocked by policy.

Between visitors, start a **fresh session**. Do not carry context: the previous visitor's sector and pain will bias the next resolution, and their details must not leak into someone else's blueprint.

At the end of each day, export leads (ordered by readiness descending, so the warmest surface first) and check `failed_sends` and `over_five_min`. Then suspend the warehouse:

```sql
ALTER WAREHOUSE LOCO4COCO_WH SUSPEND;
```

## Cost

Default posture off. Warehouse is X-Small, created suspended, 60-second auto-suspend, bound to a 20-credit monitor that notifies at 75% and 90% and suspends at 100%.

Expected Snowflake spend across the event is a few credits - one INSERT per visitor. The real exposure is an idle warehouse across a conference day, which the suspend kills. Note the warehouse is Gen2, billing about 1.35 credits/hour rather than 1.0, so do not be alarmed by a figure above a naive X-Small estimate.

**The material cost is CoCo tokens, not Snowflake credits.** Each session is a multi-turn agent conversation, and a busy booth might run 100+. Measure token spend during the timed dry runs and multiply by expected footfall before the event.

## Paris

The copy deck is the seam. Every visitor-facing string lives in `references/copy-en.md` behind an ID; the skill references IDs and never hardcodes text. Paris needs `copy-fr.md` with the same IDs - nothing else changes, and `language_code` on the session row records which deck ran.

**No French deck has been written, deliberately.** This is customer-facing copy with jokes, a fortune-teller conceit and deliberate register choices; machine translation would produce something subtly off in a way that undermines the whole light touch. It needs a French speaker.

What the translator needs to know:

- The fortune-teller framing is a **wink, not a bit** - warm, not zany. This is the hardest thing to carry across.
- `R1.Q2` options are the archetype routing keys. Meaning must be preserved exactly; phrasing is free.
- Never translate feature names (`Cortex Search`, `AI_EXTRACT`) or guide titles - guides are English-only.
- The kick-off prompt should stay **English**, because it is pasted into CoCo and the guides it references are English. Confirm this with the Paris team; it is a judgement call, not an obvious one.
- Keep strings short. A booth is loud and French runs longer than English - roughly 15 - 20% more characters for the same meaning, which matters on a screen.

Also confirm before Paris: whether the guides listing's French locale (`/fr/developers/guides/`, which exists) has enough coverage to be worth pointing at, or whether English guides remain the better fork-base.

## Open questions for others

1. **Consent wording** - capturing name, role and email at a public event needs events/marketing and privacy sign-off. `OPEN.CONSENT` is a placeholder. The activation can run consent-free (no email, photograph the screen) until it lands.
2. **Signup UTM** - wanted so free-trial signups are attributable to the activation. Not supplied. Ship the bare `signup.snowflake.com` URL until it is; do not invent parameters.
3. **Whose Google account** the booth runs under. The Gmail MCP is bound to an individual identity. If the booth laptop is not Paddy's, it needs authenticating in advance.
4. **Retention** - how long visitor rows are kept, and who deletes them.

## Reviewer steps - do these by hand

Not verifiable by me:

- [ ] Send a blueprint to your own **non-Snowflake** address; confirm arrival, not-spam, and that the prompt copies cleanly **on a phone**
- [ ] Run three timed sessions with people who have not seen it; record real `duration_seconds`
- [ ] Read `FORTUNE.*` and `REVEAL.*` **aloud** - they are performed, not read, and stilted lines will show immediately
- [ ] Paste one generated prompt into a genuine free trial and confirm CoCo does something sensible on first contact
- [ ] Sanity-check three or four guide links on a phone over venue-grade wifi
- [ ] Confirm the readiness score feels fair to a real visitor and not like a mark out of five
- [ ] Decide whether the booth screen shows the blueprint, the conversation, or both
