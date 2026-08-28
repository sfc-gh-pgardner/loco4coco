# Loco for CoCo: Setup Guide

For someone who has never run this, on a fresh laptop, against a brand new Snowflake account.

Last updated 2026-08-10.

> **Before you change anything, read [CONSTRAINTS.md](CONSTRAINTS.md).** It states
> what the event is (Snowflake World Tour, a booth stand, five minutes, one
> visitor at a time, who is not a developer) and the six venue properties every
> change is checked against. Setting the thing up does not require it; changing
> it does.

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

## Before you start

1. A laptop, macOS or Linux, with **Python 3.11+**.
2. A Snowflake account where you can create a database, warehouse and resource monitor.
   ACCOUNTADMIN is simplest. **Cortex must be enabled.**
3. Your **account region**, e.g. `AWS_EU_WEST_2`. Write it down.
4. *(Optional, recommended)* `cortex` CLI on the booth laptop and reachable - this is what powers Tier 0 (agentic marketplace search, see Step 6). Not
   required for the booth app to run: Tier 0 degrades silently to Tier 1/2 if
   `cortex` is missing, times out, or `marketplace.agentic.enabled` is false.
   "Agentic search on the Snowflake Marketplace" (PrPr) in Snowsight's
   Discover tab is the same underlying skill, useful for ad-hoc research, and
   needs `SNOWFLAKE.COPILOT_USER` plus `SNOWFLAKE.CORTEX_USER` or
   `SNOWFLAKE.CORTEX_AGENT_USER` - but that account flag is not what Tier 0
   depends on.

## Step 1: install the tools

Install the Snowflake CLI and Cortex Code, then the four Python packages:

```bash
pip3 install snowflake-connector-python python-docx PyYAML segno
```

Once you have cloned the repo (Step 3) you can install the same four from the
pinned list instead, which is the more reliable route:

```bash
pip3 install -r requirements.txt
```

Check all three answer:

```bash
python3 --version
snow --version
cortex --version
```

Everything else is Python standard library. No npm, no build step.

## Step 2: create a Snowflake connection

The game never stores credentials. It refers to a **named connection** in your own
`~/.snowflake/connections.toml`, and Snowflake's tooling resolves it.

```bash
snow connection add                     # name it e.g. MYBOOTH
snow connection test -c MYBOOTH
cortex exec "Reply with the single word: ready." --no-mcp -c MYBOOTH
```

If that last command returns `No models available`, Cortex Code is not authenticated for
this connection. Fix it now; the whole game depends on it.

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

## Step 4: add your account as a deploy target

Open `deploy/manifest.yml`. It ships with `LONDON` and `US_WEST_DEMO`. Copy one block and
edit it for your account, naming it e.g. `MYBOOTH`.

## Step 5: deploy the Snowflake objects

One command builds the database, schema, `SESSIONS` and `TURNS` tables, stage, warehouse
and resource monitor. Look before you leap:

```bash
python3 deploy/bootstrap.py --target MYBOOTH --connection MYBOOTH --plan-only
python3 deploy/bootstrap.py --target MYBOOTH --connection MYBOOTH
```

It also patches `game/config.json` to point at your account and runs the smoke test, so
the account is proven rather than assumed.

> Get this right: the resource monitor needs `monitor_notify_user` set to a **real user in
> your account**. A monitor with an empty notify list cannot warn anybody, and that has
> silently happened before.

## Step 6: point the game at your event

Edit `game/config.json`:

| Key | What it does |
|---|---|
| `event.city`, `event.language` | What the visitor sees |
| `event.region` | **Must match your account region.** Filters the Marketplace stall to listings the visitor can actually attach. Wrong value = empty stall. |
| `snowflake.connection_name` | Your connection (bootstrap normally sets this) |

**About the Marketplace preview:** the game now uses three tiers, in order.
Tier 0 is agentic: `cortex exec` calls the `marketplace-search` skill - the same skill behind Snowsight's Discover-tab "Agentic search on the
Snowflake Marketplace" (PrPr) - fired the moment a visitor submits THE
LETTER, personalised to their actual problem statement, racing THE LIBRARY
for time to finish. **It ships disabled** (`marketplace.agentic.enabled:
false`): measured on `PG_LONDON` it took 70-110s and timed out on 2 of 3
runs, which is too slow to reliably beat a visitor walking one stall. The
code is left dormant - re-enable it only once someone has actually timed
real visitors through THE LIBRARY.

So the live chain is Tier 1 (live `SHOW AVAILABLE LISTINGS`,
region-filtered, cached) then Tier 2 (curated `marketplace-index.md`, six
verified listings per industry, all currently Free) as the offline-safe net.
That chain runs exactly as it always has and needs nothing from Tier 0. If
Tier 0 is ever re-enabled there is deliberately no call cap: watch spend in
`game/cost.jsonl` (`kind: marketplace_agentic`) and flip it off by hand. Spend
is watched **per account** - its own resource monitor plus the `cost.jsonl` on
that laptop - and there is deliberately no cross-booth rollup in the app:
combine the per-account figures by hand if you want an event-wide total.

Known and unfixed: the Tier 1 query filters `regions LIKE '%<region>%'`,
which never matches the literal `ALL` Snowflake returns for
universally-available listings, so those are invisible to live search
account-wide. Tier 2 is unaffected.

## Step 7: run it and prove it

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

## Troubleshooting: what actually goes wrong

1. **Edited `config.json` or `server.py` and nothing changed.** Python does not hot-reload.
   Restart the server. HTML and CSS are served fresh from disk and need no restart.
2. **A Library or Marketplace reply fails or is slow.** Those use direct Cortex inference.
   Claude models are **not available through `CORTEX.COMPLETE` in every region** (error
   512513 on AWS_EU_WEST_2). Set `coco.complete_model` to `mistral-large2` or
   `llama3.3-70b`. The game already falls back to the slower agentic path automatically.
3. **Marketplace stall is empty.** `event.region` does not match your account region.
4. **First visitor felt slow.** Connection setup. Pre-warm.
5. **`No models available`.** Cortex Code is not authenticated for that connection (Step 2).
6. **The server vanished.** It idled out after 45 minutes.
7. **Nobody got a monitor warning.** `monitor_notify_user` was empty (Step 5).

## If you change the fast model

The two fast turns use `mistral-large2`, which needs more prompt discipline than Claude.
When first switched on it greeted the visitor by name on *every* turn and named vague
capabilities such as "the ability to handle large datasets". Both are fixed in the prompts.
If you change `coco.complete_model`, read a couple of Library and Marketplace replies and
check for exactly those two failures before trusting it at a booth.

## How the two speeds work

Turns that only reflect back what the visitor just told you (Library, Marketplace) call
Cortex inference directly and return in about 2s. Turns where CoCo must exercise judgement
or actually do something (the Workshop, and the optional Ask CoCo stop) run real Cortex
Code with tools and take 35 to 40s.

The reasoning tray is shown **only** for the agentic turns, because only they have real
reasoning to show. That is deliberate: making the cheap turns instant is what earns the
attention for the one moment where CoCo genuinely thinks.
