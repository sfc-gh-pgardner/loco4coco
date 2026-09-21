# Loco for CoCo: Setup Guide

**In a hurry?** There is a one-page TL;DR version of this guide: [Loco4CoCo — TL;DR setup](https://docs.google.com/document/d/1TwRR5uurF8NHGTbQBiBQBs0fHV9lqqUZ7357WxY5e_E/edit). This document is the long form, with the reasoning behind each choice.

For someone who has never run this, on a fresh laptop, against a brand new Snowflake account.

Last updated 2026-09-21.

> **Before you change anything, read [CONSTRAINTS.md](CONSTRAINTS.md).** It states
> what the event is (Snowflake World Tour, a booth stand, five minutes, one
> visitor at a time, who is not a developer) and the six venue properties every
> change is checked against. Setting the thing up does not require it; changing
> it does.

## TL;DR — the whole setup is three things

You do two of them. Cortex Code does the third.

**1. Get an account.** Register at <https://go.dataops.live/emea-swt/register>. Once per
event — London, Paris and Berlin each get their own. The account name is random and you
never need it.

**2. Connect to it.**

```bash
snow connection add                  # name it e.g. MYBOOTH
snow connection test -c MYBOOTH
cortex exec "Reply with the single word: ready." --no-mcp -c MYBOOTH
```

All three must answer. If the last one says `No models available`, Cortex Code is not
authenticated — fix that before going on.

**3. Paste the prompt in the next section into Cortex Code.** It clones the repo, deploys,
loads the datasets, sets your venue and name, starts the server and proves it with a smoke
test. Then it tells you the four numbers you need to check.

That is it. Nothing to translate, no region to set, no deploy target to add, no marketplace
to re-verify, no account identifier to paste anywhere.

If you would rather drive it yourself, Steps 1–8 below are the same steps in longhand.

## Let Cortex Code do it

This is the expected route and the repo is written for it. Open Cortex Code in a terminal,
replace the three bracketed values, and paste:

```
Set up the Loco for CoCo booth game on this laptop.

Clone https://github.com/sfc-gh-pgardner/loco4coco into ~/Desktop/Loco4CoCo and
symlink it to ~/.snowflake/cortex/plugins/loco4coco. Then read SETUP.md in that
repo and follow it end to end for the SWT <London|Paris|Berlin> event.

My Snowflake connection is called <MYBOOTH>. I have already registered at
go.dataops.live/emea-swt/register and added the connection.

Do all of it: install the Python packages, run deploy/bootstrap.py, run
deploy/load_context.py, run deploy/verify_context.py --all, set event.venue and
event.operator ("<Your Name> / Stand <N>"), start game/server.py, and run
game/smoke_test.py against it.

Then tell me four things: the venue, how many datasets loaded for that city,
whether the lists are being read from snowflake, and the smoke test result. Stop
and tell me if any step fails rather than working around it.
```

It will ask before anything destructive.

**One prompt you may see, and one you should never see:**

- Cortex Code asking permission to run a command. Normal; approve it.
- **macOS asking for your keychain password ("Python wants to access key
  `com.snowflake.connector.python`").** If you see this, stop and run the key-pair step in
  Step 2. A DataOps event account uses OAuth by default, which caches its token in the
  keychain and raises that dialog once per process — **312 times over a 100-visitor day**,
  including mid-visit. `python3 scripts/setup_keypair.py --connection <your-connection>`
  removes it permanently. "Always Allow" does not.


## What you end up with

A local booth game. A visitor drives a penguin round an arctic map, answers a few light
questions in under five minutes, and leaves with a POC blueprint: their idea in
their own words, the Snowflake developer guide to fork, the features with doc links, and
a kick-off prompt to paste into Cortex Code on a free trial.

It runs entirely on the laptop (a small Python server plus a browser canvas). Nothing is
hosted. The only thing it reaches out to is your Snowflake account: Cortex inference,
session logging, and the presigned stage document the visitor scans at the end.

**Budget:** about 58s of the five minutes is CoCo thinking, leaving roughly four minutes
for the human. The optional "Ask CoCo one thing" stop adds about 35s.

## Step 1: install the tools

macOS or Linux, **Python 3.11+**, plus the Snowflake CLI and Cortex Code. Then:

```bash
pip3 install snowflake-connector-python python-docx PyYAML segno
```

Check all three answer, and you are done with prerequisites:

```bash
python3 --version && snow --version && cortex --version
```

Everything else is Python standard library. No npm, no build step. After you clone
(Step 3) you can reinstall from the pinned `requirements.txt` instead, which is the
more reliable route.

`cortex` is optional but strongly recommended: it powers the Workshop and the 7th
marketplace option. Without it both fall back silently and the game still runs.

## Step 2: get your event account, then create a connection

**Register at <https://go.dataops.live/emea-swt/register>.** You will be assigned a
Snowflake account from a pool. **Do this once per event** - London, Paris and Berlin
each get their own account.

The account name is random (`NDL_HACKATHON_WEHBMG` and similar) and you will not know
it in advance. That is fine: **nothing in this setup asks you for the account's name or
its region.** Whichever account you are given, the steps below are identical.

The game never stores credentials. It refers to a **named connection** in your own
`~/.snowflake/connections.toml`, and Snowflake's tooling resolves it.

```bash
snow connection add                     # name it e.g. MYBOOTH
snow connection test -c MYBOOTH
cortex exec "Reply with the single word: ready." --no-mcp -c MYBOOTH
```

All three must succeed before you go further. If that last command returns
`No models available`, Cortex Code is not authenticated for this connection. Fix it
now - without it the Workshop and the 7th marketplace option quietly fall back to
COMPLETE, and you will not find out until a visitor is standing in front of you.

### Then swap to key-pair auth, as soon as you have cloned the repo

`snow connection add` gives you OAuth against a DataOps account, which caches its token in
the macOS keychain and raises a password dialog **once per process** — 10 during setup, then
3 per visitor, 312 over a 100-visitor day. One of those can land mid-visit and the stand
stops until somebody types a password. "Always Allow" does not fix it: the grant is per
binary and is lost when the token refreshes.

Key-pair auth has no token to cache, so it never touches the keychain at all. The script
lives in the repo, so run this **immediately after Step 3**:

```bash
python3 scripts/setup_keypair.py --connection MYBOOTH
```

Use the same connection name you created in Step 0. It generates an RSA key under
`~/.snowflake/keys/` (0600), registers the public half on your event user, and rewrites that
connection to use `SNOWFLAKE_JWT` — **in place, keeping the name**. `connections.toml` is
backed up first, so it is reversible.

Converting in place rather than creating a second connection is deliberate. Cortex Code's
connection picker holds its own selection, and a new connection name would leave your
original one still selected and still on OAuth — so the browser prompts would carry on.
Keeping the name means the picker, `game/config.json` and every `-c` you have already typed
all keep working.

You may still see two or three prompts before the swap. That is expected and harmless —
what matters is that none of them can happen once the doors open.


## Step 3: get the code

It is a Cortex Code plugin, so it lives in the plugins directory:

```bash
git clone https://github.com/sfc-gh-pgardner/loco4coco.git ~/.snowflake/cortex/plugins/loco4coco
cd ~/.snowflake/cortex/plugins/loco4coco
```

That is the simplest arrangement and the one the rest of this guide assumes.
If you would rather keep the checkout somewhere you actually look at, such as
`~/Desktop/Loco4CoCo`, clone it there and symlink the plugin path at it
instead. Cortex Code follows the symlink, so the plugin still loads and you
only have one copy of the code:

```bash
git clone https://github.com/sfc-gh-pgardner/loco4coco.git ~/Desktop/Loco4CoCo
ln -s ~/Desktop/Loco4CoCo ~/.snowflake/cortex/plugins/loco4coco
```

Whichever you pick, keep exactly one checkout. Two copies drift, and the
`git status` you are reading will not be the code that is running.

## Step 4: there is no deploy target to add

**Skip this - there is nothing to edit.** The default `EVENT` target in
`deploy/manifest.yml` deliberately pins no account and deploys wherever your
connection points. Pasting a pool-assigned account ID into a tracked file would be
pure friction, and invites committing someone else's account identifier.

## Step 5: deploy the Snowflake objects

One command builds the database, schema, `SESSIONS` and `TURNS` tables, stage, warehouse
and resource monitor. Look before you leap:

```bash
python3 deploy/bootstrap.py -c MYBOOTH --plan-only
python3 deploy/bootstrap.py -c MYBOOTH
```

It also patches `game/config.json` to point at your account and runs the smoke test, so
the account is proven rather than assumed.

The resource monitor is created with a **quota of 25 credits and a suspend trigger**.

> **An empty notify list is expected here, and the monitor is a ceiling rather than a
> guard.** A pool-assigned account's user usually has no email address at all, so
> `NOTIFY_USERS` cannot be set — it fails outright with "User ... does not have an
> associated email address" — and the post-hook falls back to a monitor with no
> recipients. There is deliberately **no suspend trigger**, so nothing will ever
> interrupt a visitor.
>
> Be clear-eyed about what that means: the monitor will not warn you and will not stop
> anything. It is a recorded quota, nothing more. In practice it does not matter —
> measured on an event account, the booth warehouse used **0.78 credits in 14 days**
> against **64 credits for Cortex Code Desktop** over the same period, so a 100-credit
> warehouse quota is far beyond anything a booth can reach. Real cost visibility is
> `game/cost.jsonl` and `SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY`, and the line that
> actually moves is Cortex Code Desktop during setup, not the booth.

## Step 6: load this city's datasets

**Do not skip this. It is the step whose absence is invisible.**

```bash
python3 deploy/load_context.py --connection MYBOOTH
python3 deploy/verify_context.py --all --connection MYBOOTH
```

This pushes the curated dataset lists — all three cities — into the account. Until it
runs, the account has nothing to serve, and the game silently falls back to a copy
committed in the repo. If that copy is older than the last curation, **a Paris booth
serves London's datasets with a full stall, eight industries and nothing in the log.**
That has happened. It is why Step 8 has you check a number.

You only re-run it if the curation changes. If it does, three artefacts have to be
refreshed in order, because each feeds the next:

```bash
python3 scripts/build_marketplace_json.py --mirror   # json  -> marketplace-index.md
python3 game/context.py --bundle                    # md    -> context-bundle.json
python3 deploy/load_context.py --connection MYBOOTH  # md    -> Snowflake tables
```

## Step 7: point the game at your event

Start the server (Step 8), then open **<http://127.0.0.1:4747/admin>**. Pick your venue,
type your name and stand, press Apply. That is the whole configuration.

| Venue | City | Language | Marketplace region (recommendations) | Dataset profile |
|---|---|---|---|---|
| `london` | London | en | AWS_EU_WEST_2 | uk |
| `paris` | Paris | fr | AWS_EU_WEST_3 | fr |
| `berlin` | Berlin | de | AWS_EU_CENTRAL_1 | de |

**Applying a venue does not need a restart.** The config is re-read on every request,
and Apply flushes the dataset cache, so the change lands on the next visitor.

**Operator** is written to `SESSIONS.SE_OPERATOR` for every visitor and **cannot be
reconstructed after the event**. Format it `Your Name / Stand 2`. If you leave it blank,
"which stand produced the best conversations" is unanswerable afterwards.

You can still set `event.venue` and `event.operator` by hand in `game/config.json` if
you prefer; `/admin` writes the same two keys.

### When you *do* need the restart button

`/admin` has one, and it is not for config changes. Use it when **replies stop coming
back** — a cancelled in-flight call can wedge the warm agent pool, and no amount of
config reloading fixes that — or when you have edited `server.py`, which Python does not
hot-reload. It re-execs the process, takes a couple of seconds, and the first reply
afterwards is slow again.

Between visitors use **Clear visitor** instead, which wipes the session and recycles the
agent without dropping the process.

### Two regions, and they are not the same thing

This is the one thing worth reading twice, because getting it backwards used to empty
the marketplace stall.

- **The event's region** is in the table above. It decides which Marketplace datasets
  are *preferred* in the recommendations, because that is where your visitors live.
  It is set for you by `event.venue`.
- **The account's region** is whatever the DataOps pool assigned you. It decides only
  where `SESSIONS`, `TURNS` and blueprints are written. **It must never filter
  recommendations, and you never need to know what it is.**

Keeping these apart is exactly what makes a random pool assignment safe. All three
event regions were verified answering correctly from a single AWS Frankfurt account,
because the Marketplace catalogue is global.

### One account per event

**Each event runs on its own account**, so `LOCO4COCO.BOOTH` in that account *is* the
per-event separation and there are deliberately no per-event schemas. Sessions still
carry `EVENT_CITY` so the rows are labelled.

> **Do not re-verify the curated listings against your own account, and do not drop a
> listing because your account cannot import it.** The visitor never imports anything
> at the booth - they leave with links and open them later from their own account. A
> pick is judged on whether it is relevant to the event's city, not on what the booth
> can attach. Measured: only 28 of the 48 curated UK picks are importable in
> `AWS_EU_WEST_2`, and deleting the other 20 would throw away four of the best UK
> datasets on the list.

### Several people setting up their own laptops

The app holds no account details of its own, so this is the whole flow per person:

```bash
snow connection add                  # their own account
python3 deploy/bootstrap.py -c <THEIRS>
# then set event.venue in game/config.json for the event they are running
```

`bootstrap.py` patches `game/config.json` to point at their connection. Everything else
(models, prompts, marketplace profiles) is identical from the clone.

Other keys you may still set directly:

| Key | What it does |
|---|---|
| `event.venue` | **Primary toggle** (above). Overwrites city/language/region and sets the marketplace profile. Leave unset to hand-configure the three fields below. |
| `event.city`, `event.language`, `event.marketplace_region` | Only used directly if `event.venue` is unset or unknown. A venue overwrites them. |
| `snowflake.connection_name` | Your connection (bootstrap normally sets this) |

**Note the models are region-specific, in availability and in speed.** The default
`coco.complete_model` and `qa.model` are both **`claude-4-sonnet`**, measured at 5.1s
median on an eu-central-1 event account. It replaced `llama3.3-70b`, which measured a
**69.5s median and ranged 33.7-111.4s** in the same region and could eat a third of the
visit on one stall. `mistral-large2` is fast (3.7s) but recommended the wrong Snowflake
feature on the test prompt. The **first** COMPLETE call on a cold warehouse takes around
56s and later ones around 4s, so run one throwaway visitor through before doors open.

**How the marketplace stall is filled.** The six picks per industry are
precomputed per city and committed in
`skills/loco4coco/references/marketplace.json`. Choosing the venue selects the
right set. There is nothing to re-run on the day, and no live catalogue call on
the visitor's critical path.

**The 7th option.** Anything the visitor *types* into the "something else" box
triggers agentic Marketplace discovery via `cortex search marketplace`, filtered
to the event's region. It runs in the **background** and its results are merged
into the takeaway document at the postbox, so a slow call can never hold up the
stall and the six curated picks are never waited on.

This replaced an earlier free-form agent prompt, which was measured and
abandoned: it took 110-237s and returned out-of-region results 78 times out of
91. The filtered search is **6.2-6.4s measured** (timed against both eu-west-2 and
eu-central-1 filters on an event account) and is in-region by construction.

There is deliberately no call cap. Watch spend in `game/cost.jsonl`
(`kind: marketplace_agentic`) and set `marketplace.agentic.enabled: false` to
turn it off. Spend is watched **per account** - its own resource monitor plus the
`cost.jsonl` on that laptop - and there is deliberately no cross-booth rollup:
combine the per-account figures by hand if you want an event-wide total.

## Step 8: run it and prove it

```bash
cd game
python3 server.py
```

Open <http://127.0.0.1:4747/>. Then in a second terminal, against the running server:

```bash
python3 smoke_test.py
```

You want `PASS, all invariants hold`, **one session row and four turn rows**. That means
the account is wired end to end.

### Before doors open, every day, at every stand

Open <http://127.0.0.1:4747/admin> and read four lines:

| Line | Must say |
|---|---|
| Venue / City | the event you are actually at |
| Datasets loaded | **90–96**. `0` means Step 6 never ran and you will serve the wrong city's data |
| Lists read from | **snowflake**. `bundle` or `markdown` means the account read failed and you are on a committed copy |
| Operator | your name and stand — it cannot be recovered afterwards |

Then run **one throwaway visitor all the way through**. The first inference call on a cold
warehouse takes around 56s against roughly 4s afterwards, and you do not want a stranger
to be the one who discovers that.

## Running four stands

The game holds **one visitor at a time** (a single state file), so four simultaneous
stands means **four independent servers**. Simplest and cheapest: one laptop per stand.

Give each stand its **own account and connection** if you can. Not for cost (tokens cost
the same either way) but so four stands' requests do not queue behind one another, and one
stand cannot affect another. Two accounts with two stands each is fine.

**Do not deploy this to SPCS to make it faster.** Model inference already runs server-side
inside Snowflake, so adding compute behind the game does not speed up replies. It adds
cost, and the single-session design would still need one service per stand.

**Pre-warm each stand** before doors open: start the server and click through one throwaway
visitor. The first Cortex call in a fresh process takes 5 to 9s (it includes connection
setup); after that it settles to 2 to 3.5s.

## Cost guardrails

- The resource monitor from Step 5 has a 100-credit quota and notifies at 75%, 90% and
  100%. It does **not** suspend the warehouse - it only warns, so a busy booth is never cut
  off mid-visit. Watch the notifications and `game/cost.jsonl`.
- `game/cost.jsonl` records every model call locally: turn, transport, model, duration and
  token counts. This is how you see spend per visitor.
- The warehouse is X-Small with 60s auto-suspend. It only does logging, so it is near free.
- The server stops itself after **45 minutes idle**, so a forgotten laptop cannot run all
  night. Change `server.idle_shutdown_minutes`, or set `0` for a long event.

## Delivery: how the visitor actually gets their blueprint

There are two independent routes, so a failure in one does not send a visitor away
empty-handed. **Email was removed: nothing is sent, and no visitor content is kept on
the laptop.**

**The QR code on screen - the primary handover.**
When the visitor presses SEND, the game builds a real Word document, uploads it to
`@LOCO4COCO.BOOTH.BLUEPRINTS` and presigns it for seven days. The confirmation card
shows that link as a QR code plus a tappable link. They scan it and leave with the
document. This path needs no email, no MCP, and no operator - only the Snowflake
connection the game already has.

**The durable record, for after the event.**
The document sits in the Snowflake stage and the row in `BOOTH.SESSIONS` carries
`DOCUMENT_URL` and `DELIVERY_STATUS`, so leads can be reconciled and re-presented in
bulk later even if the laptop is wiped. Note the presigned URL expires after seven days;
re-presign from the stage if you need it after that.

### Preflight: run this at every stand before doors open

```bash
curl -s http://127.0.0.1:4747/api/delivery/check | python3 -m json.tool
```

It checks, in order: `python-docx` importable, the stage configured, the stage
reachable, and - the one that matters - a real file staged and
presigned end to end. `"ok": true` means the QR handover works, which means no visitor
can leave with nothing. If `presign_works` fails, the stand is not ready: check the
connection name in `game/config.json` and that the deploy created the stage.

If `segno` is not installed the QR degrades to a plain link rather than breaking, but
install it - a link nobody can type is not a handover.

## Between visitors, and end of day

```bash
python3 state_cli.py reset --level all --yes
```

Add `--purge-rows` to also clear the Snowflake rows. Use that when **testing**, not at a
live event, or you will delete your leads.

## SDR handover: export the leads before the account is torn down

**This is not optional and there is no second chance.** The account you were assigned
from the pool is temporary. Every lead the booth captured lives in `SESSIONS` on *that*
account, and because there is one account per event this has to be done three times -
once per city, on the last day of that event.

Run the handover query and save the result off the laptop:

```sql
SELECT SESSION_TS, EVENT_CITY, SE_OPERATOR,
       FIRST_NAME, COMPANY, INDUSTRY,
       PROBLEM_STATEMENT,
       POC_NAME, POC_SUMMARY, GUIDE_FORKED, FIRST_STEP,
       PLATFORMS, DATA_HELD, MARKETPLACE_JOINED,
       COMPANY_COUNTRY, RESIDENCY,
       DELIVERY_STATUS, DOCUMENT_URL
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE PROBLEM_STATEMENT IS NOT NULL AND PROBLEM_STATEMENT <> ''
ORDER BY SESSION_TS DESC;
```

`PROBLEM_STATEMENT` is the one to quote back - it is the visitor's own words.

**The document links expire after 7 days**, independently of the account. If you export
later than that the links are dead, and you re-mint them from the stage:

```sql
LIST @LOCO4COCO.BOOTH.BLUEPRINTS;
SELECT GET_PRESIGNED_URL(@LOCO4COCO.BOOTH.BLUEPRINTS, '<filename>', 604800);
```

**The same person may visit more than one stand.** Deduplicate on first name and
company before handing anything over, or one visitor reads as several unrelated leads.

**Do not circulate the raw table.** It holds a first name, an employer and free text the
visitor typed. For anything going wider than the SDR doing the follow-up, drop
`FIRST_NAME` and `COMPANY` and keep industry, problem statement, POC and features.

An aggregated per-event view, a durable export and an `--anonymise` mode are scoped but
not built. Until they exist, the query above *is* the handover.

## Troubleshooting: what actually goes wrong

1. **Edited `config.json` and nothing changed.** Config *is* re-read on every request, so
   venue and operator changes land immediately — use `/admin` and press Apply. Only
   `server.py` edits need the restart button. HTML and CSS are served fresh from disk.
2. **A Library or Marketplace reply is slow.** Those use direct Cortex inference and
   **models are region-specific, in availability and in speed.** The default is
   `claude-4-sonnet`. Measured on an eu-central-1 event account, 3 reps each:
   `claude-4-sonnet` 5.1s, `openai-gpt-5-mini` 3.1s, `llama3.1-70b` 3.5s,
   `mistral-large2` 3.7s, and `llama3.3-70b` **69.5s median, ranging 33.7–111.4s** —
   it was the previous default and is a booth hazard. Not available in eu-central-1 at
   all: `claude-4-5-sonnet`, `claude-3-7-sonnet`, `llama4-maverick`, `llama4-scout`,
   `openai-gpt-4.1`, `deepseek-r1`. If you move region, re-measure before the event
   with a one-line `SELECT SNOWFLAKE.CORTEX.COMPLETE(...)` — do not assume.
3. **Marketplace stall shows the wrong city's datasets, or `/admin` says 0 loaded.**
   `deploy/load_context.py` has not been run against this account (Step 6), so the game
   is falling back to the copy committed in the repo. Check `/admin`: **lists read from**
   should say `snowflake`, not `bundle` or `markdown`, and **datasets loaded** should be
   90–96. This failure is otherwise completely silent.
4. **Marketplace stall is genuinely empty.** `event.marketplace_region` is unset — pick a
   venue in `/admin`.
5. **First visitor felt slow.** Cold warehouse: the first inference call takes around 56s
   against roughly 4s afterwards. Pre-warm with a throwaway visitor.
6. **`No models available`.** Cortex Code is not authenticated for that connection (Step 2).
7. **macOS keeps asking for your keychain password: "Python wants to access key
   `com.snowflake.connector.python`".** Fix this properly in Step 2; do not try to live
   with it.

   The cause is the auth mode, not the booth. A DataOps event account is handed out with
   `authenticator = oauth_authorization_code` and `client_store_temporary_credential = true`.
   That caches the OAuth token in the macOS keychain, and macOS asks permission once per
   *process* that reads it. The booth is process-heavy by design, so the count is:

   | when | authenticating processes |
   | --- | --- |
   | setup, once per event account | 10 |
   | server start | 2 |
   | **per visitor** | **3** (stage copy, presign, LIST) |
   | a 100-visitor day | **312** |

   Run `python3 scripts/count_auth_calls.py` to reproduce that count. The per-visitor number
   is the one that matters: a modal password dialog can land in the middle of someone's
   visit, and the stand stops until you type a password.

   **"Always Allow" is not a reliable fix.** The grant is scoped to one binary path, so
   `snow`, `cortex` and the framework Python each need their own, and the grant is lost
   whenever the token is rewritten on refresh. It also does nothing about the token expiring
   during a long day, where the recovery path is a browser window opening mid-visit.

   **The fix is key-pair auth, which has no token to cache and so never touches the keychain
   at all.** One command, once per event account:

   ```bash
   python3 scripts/setup_keypair.py --connection <your-connection>
   ```

   That generates an unencrypted RSA key under `~/.snowflake/keys/` (0600), registers the
   public half on your event user with `ALTER USER`, and rewrites that connection to
   `SNOWFLAKE_JWT` in place, dropping `client_store_temporary_credential`.
   `connections.toml` is backed up first. The key is unencrypted deliberately — a passphrase
   would just reintroduce a prompt, and the booth has to run unattended.

   The connection keeps its name, so nothing downstream changes: the same `-c` works, the
   Cortex Code picker keeps its selection, and `game/config.json` already holds that name.
   Restart Cortex Code afterwards so it rereads the file. Verified: five consecutive fresh
   `snow sql` subprocesses, zero prompts, and 1.4–2.2s each against ~3.4s under OAuth.

   Do **not** instead set `client_store_temporary_credential = false`. That stops the caching,
   so the connector falls back to the full OAuth browser flow — a browser window opening
   mid-visitor is worse than the dialog you were trying to remove.

6. **The server vanished.** It idled out after 45 minutes.
7. **Nobody got a monitor warning.** `monitor_notify_user` was empty, or the user has no
   email address. On hands-on-lab / event accounts the login user often has no email, so
   `NOTIFY_USERS` cannot be set - the deploy no longer aborts (the post-hook creates the
   monitor without a notify list and prints a warning), but nobody is warned. For an
   unattended event account, add a `DO SUSPEND` trigger by hand if you want a hard cap.

## If you change the fast model

The two fast turns use `claude-4-sonnet` by default. Open-weight models need more prompt
discipline than Claude: `mistral-large2` (a previous default) greeted the visitor by name on
*every* turn and named vague capabilities such as "the ability to handle large datasets".
Both are fixed in the prompts. If you change `coco.complete_model`, read a couple of Library
and Marketplace replies and check for exactly those two failures before trusting it at a booth.

And check the **feature it recommends is real and appropriate**, not merely plausible. On
the manufacturing test prompt `mistral-large2` recommended Time Travel for predicting
supplier delays and both llama models recommended Materialized Views, where the right
answer was Dynamic Tables. A fast wrong answer is worse at a booth than a slow right one.

## How the two speeds work

Turns that only reflect back what the visitor just told you (Library, Marketplace) call
Cortex inference directly and return in about 2s. Turns where CoCo must exercise judgement
or actually do something (the Workshop, and the optional Ask CoCo stop) run real Cortex
Code with tools and take 35 to 40s.

The reasoning tray is shown **only** for the agentic turns, because only they have real
reasoning to show. That is deliberate: making the cheap turns instant is what earns the
attention for the one moment where CoCo genuinely thinks.
