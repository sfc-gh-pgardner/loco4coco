# Loco for CoCo

https://github.com/sfc-gh-pgardner/loco4coco/raw/main/assets/Loco4Coco.mp4

A five-minute Cortex Code activation for **Snowflake World Tour**. A visitor drives a penguin
round an arctic map, answers a few light questions, and leaves with the scaffolding for a POC:
their idea in their own words, the Snowflake developer guide to fork, the
features with doc links, and a kick-off prompt to paste into Cortex Code
on a free trial. They take it away by **scanning a QR code** with their own phone.

> **Read [CONSTRAINTS.md](CONSTRAINTS.md) before designing or changing any feature.**
> It states what the event is, who the visitor is, and the six venue properties
> every change is checked against. They are properties of the stand, not
> preferences, and they have been broken before.

It uses **real** Cortex Code and real Snowflake Marketplace listings. It runs on a laptop:
a Python standard-library server plus a browser canvas. No npm, no build step, nothing hosted.

## Setting it up

New laptop, new account, never run this before: **[SETUP.md](SETUP.md)**.

Already set up:

```bash
cd game
python3 server.py          # then open http://127.0.0.1:4747/
```

## Running an event

`SETUP.md` also covers the operational side: the pre-flight before doors open,
the cost guardrails, and resetting between visitors.

## How it is put together

| Path | What it is |
|---|---|
| `game/server.py` | The booth server. Prompts CoCo, streams reasoning, logs to Snowflake. |
| `game/index.html` | The whole front end: procedural pixel-art canvas and the panels. |
| `game/config.json` | Everything tunable: copy, locations, transports, models, guardrails. |
| `game/smoke_test.py` | End-to-end proof. Run it after any change. |
| `game/bench.py`, `game/bench2.py` | Latency benchmarks (agentic path, and direct inference). |
| `deploy/verify_context.py` | **Pre-flight gate.** Closed lists, doc links, live listings. Exits with the failure count. |
| `deploy/load_context.py` | Loads the reference markdown into the shared Snowflake context tables. |
| `game/context.py` | The closed lists, their three-layer fallback, and deterministic keyword retrieval. |
| `game/agent_pool.py` | The warm Cortex Code agent. One in-flight call, always. |
| `audit/` | Chromium persona suite (`npx playwright test`), 35 stories over 8 industries. |
| `game/state_cli.py` | Reset between visitors, purge rows. |
| `deploy/` | DCM project that builds the Snowflake objects on any account. |
| `skills/loco4coco/references/` | The closed lists the game may name - listings, guides, features, archetypes - plus their committed offline bundle. |

## Two speeds, on purpose

Turns that only reflect back what the visitor just said (Library, Marketplace) call Cortex
inference directly and return in ~2s. Turns where CoCo must exercise judgement or actually
do something (Workshop, and the optional "Ask CoCo one thing") run real agentic Cortex Code
with tools, and take 35 to 40s.

The reasoning tray appears **only** for the agentic turns, because only they have real
reasoning to show. Making the cheap turns instant is what earns attention for the one
moment where CoCo genuinely thinks.

Total CoCo wait is about 58s of the 300s budget, down from 144.5s before tuning.

## A few hard-won notes

- **Python does not hot-reload.** Restart the server after editing `server.py` or
  `config.json`. HTML and CSS are served from disk.
- **Claude is not available via `CORTEX.COMPLETE` in every region.** The fast path uses
  `mistral-large2`; it falls back to the agentic path automatically if inference fails.
- **Delivery is a QR to a presigned stage document, not an email.** The booth keeps
  nothing on the laptop and sends no email; the visitor scans the QR on screen and the
  document lands on their own phone.
- **The server stops itself after 45 minutes idle**, so a forgotten laptop cannot run all night.
