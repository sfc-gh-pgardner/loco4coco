---
name: agentic-marketplace-enhancement
description: "Proposed enhancement to the Marketplace stage using Agentic search on the Snowflake Marketplace (PrPr). Drafted for review, not yet merged into the decision tree Google Doc — that doc is currently with a colleague."
status: draft, awaiting sign-off
---

# Agentic Marketplace (PrPr) — proposed enhancement to THE MARKETPLACE stage

This is a staging file. Nothing here has been merged into the decision-tree
Google Doc
(`1vyAFvNr83nTKP4eJ-jsNN7LV528XZLEO4FwQtqVMXRs`) — it is under colleague review.
Once a path below is picked and (if applicable) built, this section is what
gets pasted into that doc.

## Where this fits in the existing tree

THE MARKETPLACE stage (`game/server.py::listings_for()`) is currently a two-tier
chain:

```
MARKETPLACE
  Tier 1 live    - SHOW AVAILABLE LISTINGS, region-filtered, cached (TTL)
  Tier 2 curated - marketplace-index.md, per-industry, offline-safe fallback
```

Both tiers are sub-second for the visitor because the expensive part (the SQL
call) already happened out-of-band and is served from memory — "the stall
stays instant." This matters for everything below: any agentic addition has to
preserve that property, not trade it away.

## What was tested

`cortex exec` can call the same `marketplace-search` skill that powers
Snowsight's Discover-tab agentic search, from the command line:

```bash
cortex exec "Use the marketplace-search skill to find weather data listings
for North America..." --format json -c PG_LONDON --bypass
```

Confirmed working on `PG_LONDON` (2026-08-23): returned 12 real, well-formed
listings with provider names and descriptions. Measured cost: **~55 seconds**
and **~250K tokens** (mostly cached skill/tool instructions) for one query.

## Path A — call it live, per visitor

At Step 3, `server.py` shells out to `cortex exec` synchronously while the
visitor waits, and shows the agentic result instead of / alongside Tier 1.

**Rejected.** 55 seconds of dead air breaks the booth's pace (every other step
responds in 1-3s). It's also non-deterministic — wording and even which
listings come back can vary call to call, which is a problem for an SE running
a rehearsed demo. And it's real LLM spend per visitor with no caching benefit,
since each visitor's problem statement differs.

## Path B — don't use it (status quo)

Tier 1 → Tier 2 stays exactly as it is today. Zero risk, zero new cost, zero
new latency. This is the permanent safety net underneath whichever of C/D
below gets built — it doesn't go away either way.

## Path C — recommended code change: precomputed agentic cache

Treat the agentic call exactly like the existing live-listings cache: compute
it rarely, in the background, and serve visitors only from memory.

```
MARKETPLACE
  Tier 0 agentic - cortex exec, run per-industry on a long TTL (event-day /
                    manual refresh), never inline in a visitor's turn
  Tier 1 live    - unchanged
  Tier 2 curated - unchanged
```

- One `cortex exec` call per industry (8 total, ~55s × 8 ≈ 7-8 minutes),
  triggered by the SE before doors open or on a scheduled refresh — never
  during a visitor's turn.
- Parsed into the same shape Tier 1/2 already use (`title`, `provider`, `url`,
  ...) and cached in memory (mirrors `_live_cache` / `refresh_live_listings()`
  in `game/server.py`).
- `listings_for()` tries the agentic cache first if it's fresh and has
  ≥ `marketplace.min_live_results`; otherwise falls through to Tier 1, then
  Tier 2 — unchanged behaviour if `cortex exec` isn't installed, times out,
  errors, or the cache is stale/empty.
- Net effect: visitors can get agentic-quality picks, but never wait on an LLM
  agent loop, and the per-event cost is bounded (8 calls per refresh, not one
  per visitor).

**Not yet built** — pending sign-off below.

## Path D — recommended first step: simulate now, offline

Run the same idea without touching runtime code at all. Do it once, this
week, ahead of the next event:

1. For each of the 8 industries in `config.industries`
   (`healthcare`, `financial`, `retail`, `public`, `manufacturing`, `energy`,
   `media`, `other`), run one `cortex exec` call phrased as a realistic
   visitor problem statement for that vertical — reusing the industry framing
   text already in `config.json` (e.g. the `industry_question` /
   `confirm_industry` copy) so the simulated angle matches what a real visitor
   actually types.
2. Read back what the `marketplace-search` skill surfaces per industry.
3. Fold genuinely good matches into `marketplace-index.md`'s existing curated
   tables (Tier 2) under the matching `## <industry>` section, following its
   existing verification rules (region-checked, access terms labelled, no
   unverified provider names — see that file's "What is verified" table).
4. Where the agentic search finds listings today's `industry_keywords` in
   `config.json` miss entirely, consider adding those words to close the gap
   in Tier 1 (live) too.

Example simulation prompts (one per industry, run individually):

| Industry | Simulated visitor angle |
|---|---|
| `healthcare` | "We're a hospital trust wanting to risk-adjust readmissions by catchment area — what population, deprivation, or weather data could we join against patient records?" |
| `financial` | "We're a retail bank wanting to enrich SME lending decisions — what company financials, macroeconomic, or ESG data is available?" |
| `retail` | "We're a retailer wanting to plan store-level demand — what footfall, weather, or demographic data could we join against POS data?" |
| `public` | "We're a local government body wanting to understand deprivation and service demand — what census, geospatial, or benefits data is available?" |
| `manufacturing` | "We're a manufacturer wanting to reduce downtime — what supply chain, commodity pricing, or logistics data is available?" |
| `energy` | "We're a utility wanting to forecast demand — what weather, commodity, or grid data is available?" |
| `media` | "We're a media company wanting to understand audience behaviour — what demographic, social, or advertising data is available?" |
| `other` | "We're a company outside the usual verticals wanting general enrichment — what firmographic or geospatial data is broadly useful?" |

- Zero runtime code changes, zero added latency, zero added per-visitor cost.
- Directly strengthens the fallback path that runs on every visitor today,
  regardless of whether Path C ever gets built.
- Can be run today, independent of the Path C decision.

## Recommendation

Run Path D now (no code, no risk, improves what's already live). Treat Path C
as a separate, optional follow-up once there's appetite for the `server.py`
change and someone can validate the Tier 0 cache/fallback behaviour with
`smoke_test.py`. Path A stays rejected; Path B (the existing fallback) never
changes under any of the above.
