# Loco for CoCo: Setup Guide

For someone who has never run this, on a fresh laptop, against a brand new Snowflake account.

Last updated 2026-08-10.

## What you end up with

A local booth game. A visitor drives a penguin round an arctic map, answers a few light
questions in under five minutes, and leaves with an emailed POC blueprint: their idea in
their own words, the Snowflake developer guide to fork, the features with doc links, a
readiness score, and a kick-off prompt to paste into Cortex Code on a free trial.

It runs entirely on the laptop (a small Python server plus a browser canvas). Nothing is
hosted. The only things it reaches out to are your Snowflake account (Cortex inference and
session logging) and, at the end, your own Gmail to post the blueprint.

**Budget:** about 58s of the five minutes is CoCo thinking, leaving roughly four minutes
for the human. The optional "Ask CoCo one thing" stop adds about 35s.

## Before you start

1. A laptop, macOS or Linux, with **Python 3.11+**.
2. A Snowflake account where you can create a database, warehouse and resource monitor.
   ACCOUNTADMIN is simplest. **Cortex must be enabled.**
3. Your **account region**, e.g. `AWS_EU_WEST_2`. Write it down.
4. A Google account for sending blueprints (your own Gmail).

## Step 1: install the tools

Install the Snowflake CLI and Cortex Code, then the three Python packages:

```bash
pip3 install snowflake-connector-python python-docx PyYAML segno
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
git clone https://github.com/snow-paddy/loco4coco.git ~/.snowflake/cortex/plugins/loco4coco
cd ~/.snowflake/cortex/plugins/loco4coco
```

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

- The resource monitor from Step 5 has a credit quota, notifies at 75% and 90%, suspends at 100%.
- `game/cost.jsonl` records every model call locally: turn, transport, model, duration and
  token counts. This is how you see spend per visitor.
- The warehouse is X-Small with 60s auto-suspend. It only does logging, so it is near free.
- The server stops itself after **45 minutes idle**, so a forgotten laptop cannot run all
  night. Change `server.idle_shutdown_minutes`, or set `0` for a long event.

## Delivery: how the visitor actually gets their blueprint

There are three independent tiers. Each one is sufficient on its own, so a failure in
one does not send a visitor away empty-handed.

**Tier 1 - the QR code on screen. This is the primary handover at an event.**
When the visitor presses SEND, the game builds a real Word document, uploads it to
`@LOCO4COCO.BOOTH.BLUEPRINTS` and presigns it for seven days. The confirmation card
shows that link as a QR code plus a tappable link. They scan it and leave with the
document. This path needs no email, no MCP, and no operator - only the Snowflake
connection the game already has.

**Tier 2 - the queued email, drained by an operator.**
The game writes a fully composed email to `game/outbox/` as a durable record, and an
operator drains it from an **interactive** Cortex Code session using the Gmail tools.
This is deliberate, not a shortcut: Gmail MCP tools do not load under `cortex exec`,
only in an interactive session; the MCP exposes `create_draft` only, with no send tool
and no attachment parameter; and `snowflake.com` publishes DMARC `p=reject`, so a
third-party sender is rejected outright. See the `loco4coco-ops` skill for the drain.

**Tier 3 - the durable record, for after the event.**
The document sits in the Snowflake stage and the row in `BOOTH.SESSIONS` carries
`DOCUMENT_URL` and `DELIVERY_STATUS`, so leads can be reconciled and re-sent in bulk
later even if the laptop is wiped. Note the presigned URL expires after seven days;
re-presign from the stage if you need it after that.

Nothing in the game ever claims an email was sent when it was not. The card says
"queued", and points at the QR.

### Preflight: run this at every stand before doors open

```bash
curl -s http://127.0.0.1:4747/api/delivery/check | python3 -m json.tool
```

It checks, in order: `python-docx` importable, the stage configured, the stage
reachable, `outbox/` writable, and - the one that matters - a real file staged and
presigned end to end. `"ok": true` means Tier 1 works, which means no visitor can
leave with nothing. If `presign_works` fails, the stand is not ready: check the
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
