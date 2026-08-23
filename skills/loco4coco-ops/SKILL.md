---
name: loco4coco-ops
description: "Booth operator skill for Loco for CoCo: one-time setup, the pre-flight check before doors open, resetting between visitors, end-of-day lead export, live booth analytics, and refreshing the guides index. Triggers: booth setup, preflight, pre-flight, is the booth ready, loco4coco setup, export leads, booth analytics, reset the booth, refresh guides index, booth costs."
---

# Loco for CoCo - booth ops

**Why this skill:** The visitor-facing skill assumes a working environment. This one creates it, proves it before doors open, and gets the leads out afterwards. Run pre-flight every morning of the event - the failure modes are boring and entirely avoidable.

**Not for:** Running a session. That is `loco4coco`.

## Pre-flight (run every morning, before doors)

Each check must **prove** the capability, not merely observe that something exists. The single hardest lesson from building this: three delivery routes looked available and were blocked by policy.

| # | Check | How | If it fails |
|---|---|---|---|
| 1 | Snowflake connection | `SELECT CURRENT_ACCOUNT(), CURRENT_WAREHOUSE()` | Fix the connection; nothing works without it |
| 2 | Table reachable | `SELECT COUNT(*) FROM LOCO4COCO.BOOTH.SESSIONS` | Re-run setup |
| 3 | Warehouse + monitor | `SHOW WAREHOUSES LIKE 'LOCO4COCO_WH'` - confirm `X-Small`, `auto_suspend 60`, `resource_monitor LOCO4COCO_RM` | Re-bind the monitor |
| 4 | Monitor has quota **and** notify_users | `SHOW RESOURCE MONITORS LIKE 'LOCO4COCO_RM'` - `notify_at` must show `75%,90%`, `suspend_at 100%`, and `notify_users` must be **non-empty** | A monitor with empty `notify_users` is silent. Re-create it |
| 5 | **Gmail send works end to end** | Send one real blueprint to a **genuinely external, non-Snowflake** address and confirm arrival | See below - this is the highest-risk check |
| 6 | Guides index valid | `python3 scripts/build_guides_index.py` - expect `0 failing, 0 redirecting` | Fix slugs before any visitor sees one |
| 7 | Docs lookup | One `snowflake_product_docs` query | Venue network. Degrade to naming features without links |
| 8 | Write path | Insert a row with an apostrophe and an accent, read it back, delete it | Escaping regression |
| 9 | **Delivery, automated** | `curl -s http://127.0.0.1:4747/api/delivery/check \| python3 -m json.tool` - expect `"ok": true` | See below. This one check covers checks 1-2 of delivery and is the fastest way to clear a stand |

### Check 9 in detail: the automated delivery preflight

One call proves every leg of the handover on that laptop, in order: `python-docx`
importable, stage configured, stage reachable, `outbox/` writable, and a real file
staged and **presigned end to end**. Run it per stand.

```bash
curl -s http://127.0.0.1:4747/api/delivery/check | python3 -m json.tool
```

`"ok": true` means the QR handover works, which means **no visitor can leave with
nothing** even if email never works all day. Treat that as the bar for opening a
stand, and check 5 (real Gmail arrival) as the upgrade rather than the gate.

If `presign_works` fails, the stand is not ready: check `snowflake.connection_name`
in `game/config.json` and that the deploy actually created
`@LOCO4COCO.BOOTH.BLUEPRINTS`. If `word_library` fails, `pip3 install python-docx`.
If the QR renders as a plain link only, `pip3 install segno`.

### Check 5 in detail

Verified 2026-08-05: Google Drive sharing to any external address is **blocked by Snowflake Workspace policy**, `SYSTEM$SEND_EMAIL` reaches only verified in-account users, and presigned stage URLs download rather than render. The **Natoma Gmail MCP** (`Gmail` in `~/.snowflake/cortex/mcp.json`) is the only route to a visitor's inbox, and as of that date it was registered but **never exercised**.

So:

- Test with a **real external address you control** - a personal Outlook or Gmail. A colleague on `@snowflake.com` would pass while the real case fails.
- Confirm the mail **arrives**, that the prompt block **copies cleanly on a phone**, and that it did not land in spam.
- HTTP MCPs need OAuth on first connect **and a fresh session** before their tools appear. If the Gmail tools are missing, restart CoCo before concluding anything is broken.
- If it cannot be made to work, the booth still runs: skip the email field, show the blueprint on screen, let visitors photograph it. Say so in the opening rather than collecting an address you cannot deliver to.

## One-time setup

Already applied to `SFSEEUROPE-PG_LONDON` on 2026-08-05:

- `LOCO4COCO` database, `BOOTH` schema
- `LOCO4COCO.BOOTH.SESSIONS` table (see `../loco4coco/references/session-log.md`)
- `LOCO4COCO.BOOTH.BLUEPRINTS` stage - `SNOWFLAKE_SSE`, directory enabled. Created during the delivery spike; **currently unused** since delivery is email. Keep it: it is the archive location if blueprints ever need retaining, and it is the only verified route to a public no-login URL should a QR ever be wanted.
- `LOCO4COCO_WH` - X-Small, `AUTO_SUSPEND = 60`, initially suspended
- `LOCO4COCO_RM` - 20 credit quota, notify at 75% and 90%, suspend at 100%, suspend-immediate at 110%, notifying `PGARDNER`

For Paris, re-run against the account being used and change `event_city`.

## Cost

Default posture is **off**. `LOCO4COCO_WH` is created suspended with a 60-second auto-suspend.

The booth workload is trivial - one INSERT per visitor plus the occasional analytics query. The genuine exposure is **an idle warehouse left running across a conference day**, which the 60-second suspend kills. Note `LOCO4COCO_WH` is Gen2, which bills around 1.35 credits/hour rather than 1.0, so do not be alarmed if credits exceed a naive X-Small estimate.

The 20-credit quota is deliberately generous against an expected spend of a few credits across the event. If it trips, something is wrong - investigate rather than raising it.

**The real cost is CoCo tokens, not Snowflake credits.** Each session is a multi-turn agent conversation. Measure token spend across the dry runs, multiply by expected footfall, and confirm the number before the event. Snowflake compute will not be the expensive part.

## Between visitors

Start a fresh session per visitor. Do not carry context over - the previous visitor's sector and pain will bias the next resolution, and their details must not leak into someone else's blueprint.

Quick reset: confirm the last row landed (`SELECT MAX(session_ts) ...`), then start a new conversation.

## Deploying to a new account

Every Snowflake object is defined as code in `deploy/`, as a DCM project. Nothing
is hand-created any more - the tracking table silently drifted away from the app
once already because it was.

```bash
# 1. Add a target to deploy/manifest.yml (account_identifier, project_name,
#    project_owner, templating_config). Set monitor_notify_user for that
#    account - the username differs per account and is deliberately NOT
#    defaulted, because a monitor pointed at a non-existent user fails.
# 2. Dry run first. Nothing is applied.
python3 deploy/bootstrap.py --target <NAME> -c <CONNECTION> --plan-only
# 3. Deploy for real.
python3 deploy/bootstrap.py --target <NAME> -c <CONNECTION>
```

`bootstrap.py` refuses to run if the connection is not actually on the account
the target names - deploying booth objects to the wrong account is not something
to discover afterwards. It then creates the project schema, archives any pre-v2
`SESSIONS`, plans, deploys, creates the resource monitor, repoints
`game/config.json`, and runs `smoke_test.py` so the account is **proven, not
assumed**.

Proven on two accounts and two regions: `SFSEEUROPE-PG_LONDON` (AWS eu-west-2)
and `SFSEEUROPE-US_WEST_DEMO_PG` (AWS us-west-2).

Two things DCM cannot do, both handled:

- **Resource monitors are not a supported `DEFINE` entity.** `LOCO4COCO_RM` is
  created by `deploy/hooks/post_hook.sql`, which bootstrap runs and then
  verifies `notify_users` is non-empty. A monitor with no notify users cannot
  warn anyone, and that has happened here before.
- **Stage encryption is immutable.** `BLUEPRINTS` must be created
  `SNOWFLAKE_SSE` or `GET_PRESIGNED_URL` will not work. It is pinned in the
  definition rather than left to a default.

Teardown: `EXECUTE DCM PROJECT LOCO4COCO_DEPLOY.PROJECTS.LOCO4COCO_BOOTH PURGE;`
then `DROP DCM PROJECT ...`.

## Resetting the booth

```bash
python3 game/state_cli.py reset                 # between visitors
python3 game/state_cli.py reset --level day     # start of an event day
python3 game/state_cli.py reset --level all --purge-rows   # after a rehearsal
python3 game/state_cli.py show                  # current session at a glance
python3 game/state_cli.py outbox                # what is waiting to be drained
```

The in-browser **NEW VISITOR** button does the same as `--level visitor`. Use it
between visitors: state is server-side and global, so without a reset the next
person sees the previous person's name, employer and email.

`--level day` also rolls the cost log and archives the outbox. It **refuses** if
any outbox record is undrained, listing them, because those are blueprints
nobody has received yet. `--yes` overrides. **Records are always moved to
`outbox/archive/<date>/`, never deleted.**

## What gets tracked

| Table | Grain | Use |
|---|---|---|
| `BOOTH.SESSIONS` | One row per visitor | Lead export, readiness, delivery status |
| `BOOTH.TURNS` | One row per location per visitor | Which beat is slow and what it costs |
| `BOOTH.SESSIONS_V1_ARCHIVE` | The 3 pre-v2 dry-run rows | History only, not written to |

**`READINESS_SCORE` is internal.** It is deliberately never shown to a visitor - no score appears in the email, the `.docx`, or on screen, and the browser payload
strips it. It exists so the lead export can rank warmest-first. What the visitor
sees instead is a **Considerations** section: three or four specific things to
think about, stored in `CONSIDERATIONS`.

Because the score is private, the model is told to be honest rather than kind
when setting it.

`DELIVERY_STATUS` is `QUEUED` on send, `DRAFTED` only if a Gmail draft was
confirmed, and **`SENT` only when the drain actually presses Send** - see below.
The app can never set `SENT` itself, by design.

Measured on a real run, which is why `TURNS` exists:

| Location | Seconds | Share of the wait |
|---|---|---|
| library | 17 | 15% |
| marketplace | 18 | 16% |
| workshop | 30 | 26% |
| postbox | 51 | 44% |

The postbox is the longest wait and it lands last. Input tokens are ~53k per
turn but ~48k of that is cache reads, so the token cost is low; the problem is
latency, not spend.

## Draining the outbox (the email route - no longer the only one)

Since the confirmation card now shows a QR code to the presigned document, a visitor
already has their blueprint before you drain anything. The drain is what turns that
into an email they can find again next week. It is important, not load-bearing.


The game does not send email. It cannot, and the reasons are settled rather than
open questions:

- The Gmail MCP exposes **`create_draft` only** - no send tool, and **no
  attachment parameter**.
- Those Gmail tools **do not load under `cortex exec`**. Verified with
  `--bypass` and persistent tool search: Calendar's tools load, Gmail's never
  do. They work fine in an **interactive** CoCo session.
- `snowflake.com` publishes **DMARC `p=reject`**, so SendGrid, Resend and
  friends sending as a Snowflake address are rejected outright, not
  spam-foldered.

So each visitor's finished email is written to `game/outbox/<stamp>-<name>.json`
holding `to`, `subject`, `body_html`, `document_url` and `document_local`. The
game's own state stays honest about this: `queued` goes true, while
`email_sent` stays **false** until a draft genuinely exists.

**Drain it from an interactive CoCo session** - not from `exec`, which cannot
see the Gmail tools:

1. Read the oldest unsent record in `game/outbox/`.
2. Call the Gmail MCP `create_draft` with `to`, `subject`, `body_html` and
   `isHtml: true`. Pass the body **verbatim**; it is already valid HTML and
   already escaped.
3. Confirm the response carries `labelIds: ["DRAFT"]`.
4. Open Gmail and press **Send**. Creating a draft is not sending - never tell
   a visitor their present is on its way until you have actually sent it.
5. Set `"sent": true` in the record so it is not drafted twice.
6. Mark it in Snowflake, so the record reflects what actually reached the
   visitor rather than what the game hoped would:

   ```sql
   UPDATE LOCO4COCO.BOOTH.SESSIONS
     SET DELIVERY_STATUS = 'SENT'
     WHERE EMAIL = '<recipient>' AND DELIVERY_STATUS IN ('QUEUED','DRAFTED');
   ```

   This is the only step permitted to write `SENT`. The app cannot, because the
   app cannot know.

Drain between visitors rather than at end of day, so people receive their
blueprint while the booth is still fresh in mind.

Deliverability is fine on this path: the draft sends from a real Snowflake
mailbox through Google, so SPF and DKIM align and DMARC passes for any
recipient, internal or external.

If a visitor asks when it arrives, the truthful answer is "shortly, once we post
it" - not "it's in your inbox".

## End of day

Lead export - use the follow-up query in `session-log.md`, which orders by readiness descending so the warmest leads surface first.

Then sanity-check the day:

```sql
SELECT COUNT(*) AS sessions,
       SUM(IFF(email_sent, 1, 0)) AS delivered,
       SUM(IFF(email_provided AND NOT email_sent, 1, 0)) AS failed_sends,
       ROUND(AVG(duration_seconds)) AS avg_seconds,
       SUM(IFF(duration_seconds > 300, 1, 0)) AS over_five_min
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE session_ts::DATE = CURRENT_DATE();
```

`failed_sends` above zero on day one means fix the mail path overnight. `over_five_min` above a third of sessions means the flow needs cutting, not the clock relaxing.

Suspend the warehouse when you pack up:

```sql
ALTER WAREHOUSE LOCO4COCO_WH SUSPEND;
```

## Refreshing the bundled indexes

Three bundled reference files keep the booth offline-fast and stop it inventing
anything. Refresh all three before an event:

```bash
python3 scripts/build_feature_docs.py --write        # 53 feature -> docs URLs
python3 scripts/build_marketplace_index.py --write   # curated real listings
python3 scripts/build_guides_index.py                # 44 developer guides
```

Each one **refuses to write if any entry fails verification**, because a dead
link in a document a visitor keeps is worse than no link.

- **`feature-docs.md`** is a *closed list*. The Workshop may only name features
  from it, which is what guarantees every feature in a blueprint has a working
  documentation link. A name outside the list is dropped rather than rendered
  bare.
- **`marketplace-index.md`** holds real listings with real providers. Note that
  **provider names cannot be re-derived by script**: SQL exposes
  `organization_profile_name` for only 137 of 4,256 listings, and the public
  listing page is a client-rendered React app whose raw HTML contains no
  provider at all. They are recorded constants with a verification date; to
  refresh them, load the pages in a real browser.
- Listings are **filtered to `event.region`** at render time. Offering a London
  visitor a us-east-1-only share sends them somewhere they cannot go.
- The industry groupings in the marketplace index are **editorial judgement, not
  verified fact**. Review them.

## Refreshing the guides index

Guides are published constantly, so the curated index has a shelf life. Before each event:

1. `python3 scripts/build_guides_index.py` - verifies every curated slug still returns 200 and reports redirects.
2. For a full corpus refresh, follow the browser harvest procedure documented in that script's docstring. Note the listing's `?page=` parameters are **ignored server-side** - plain HTTP paging returns 15 guides, not 565 - so the harvest genuinely needs a browser. An earlier version of the script did this over HTTP and exited successfully having found 15 of 565.
3. Update `guides-index.md`, re-run the verifier, and only then ship.

Never ship an unverified slug. A broken link in the one artefact a visitor keeps undoes the whole five minutes.
