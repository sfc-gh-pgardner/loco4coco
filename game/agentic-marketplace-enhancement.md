---
name: agentic-marketplace-enhancement
description: "Enhancement to the Marketplace stage using Agentic search on the Snowflake Marketplace (PrPr). Drafted for review, not yet merged into the decision tree Google Doc - the marketplace-specific sections of that doc were updated directly on 2026-08-23 with the user's explicit go-ahead; other sections stay untouched while a colleague reviews."
status: Tier 0 built, tested, then disabled for latency; Path D executed instead - 6 free-weighted picks per industry now live
---

# Agentic Marketplace (PrPr) - enhancement to THE MARKETPLACE stage

## Where this landed

**Tier 0 (live, per-visitor) is built and disabled.** It worked end-to-end on
`PG_LONDON`, but measured latency (70-110s+, 2 of 3 real runs timed out even
at 120s) was judged too high and too variable to trust against THE LIBRARY's
unmeasured dwell time. `marketplace.agentic.enabled: false` in `config.json`
turns it off; the code stays in place, dormant, for later.

**Path D (offline precompute) is what actually shipped.** The same PrPr
access, run once per industry with zero latency risk, to add a verified 6th,
free-weighted pick to `marketplace-index.md` (Tier 2). Every industry is now
at 6 listings, and **every single one is Free** (was 39 Free + 1 Paid across
40 slots; the one Paid listing turned out not even importable, see below).

## Where this fits in the existing tree

THE MARKETPLACE stage (`game/server.py::listings_for()`) is a three-tier
chain:

```
MARKETPLACE
  Tier 0 agentic - cortex exec, per-visitor, DISABLED (marketplace.agentic.enabled=false)
  Tier 1 live    - SHOW AVAILABLE LISTINGS, region-filtered, cached (TTL)
  Tier 2 curated - marketplace-index.md, per-industry, 6 listings, all Free
```

Tier 1 and Tier 2 are sub-second for the visitor - "the stall stays instant."
With Tier 0 off, this is the real, active chain every visitor uses today.

## What was tested (live Tier 0)

`cortex exec` can call the same `marketplace-search` skill that powers
Snowsight's Discover-tab agentic search, from the command line. Confirmed
working on `PG_LONDON` (2026-08-23). Measured cost across the session:
**one sample at ~55s, then 70s/100s+(timeout)/92s(success) once wired into
`run_agentic_search()`** - call it 90-110s+ realistically, not 55s. ~250K
tokens per call (mostly cached skill/tool instructions).

## Path A - call it live, per visitor

**Rejected.** 90-110s+ of dead air breaks the booth's pace (every other step
responds in 1-3s). Non-deterministic wording/results, and real LLM spend per
visitor with no caching benefit since each problem statement differs.

## Path B - don't use it (status quo)

Tier 1 → Tier 2. Always the permanent safety net underneath whichever of
Tier 0 / Path D is active - never changes.

## Path C - built, then disabled: per-visitor Tier 0 at THE LETTER

Fired from `_intake()` on a daemon thread the instant industry + problem are
known, racing THE LIBRARY. Confirmed end-to-end via `smoke_test.py` and a
live `PG_LONDON` run: the trigger fires, the visitor's Letter response is
never delayed, and when the call succeeds `/api/options` picks it up
automatically on the next fetch.

**Why it's off:** real visitor dwell time on THE LIBRARY has never been
measured (see `BOOTH-RUNBOOK.md`), and 90-110s+ is long enough that it's a
real risk Tier 0 usually loses its race and just spends money in the
background for a screen the visitor's already left. No cap by design (the
user's explicit call: "we only need monitors") - if re-enabled, watch spend
in `game/cost.jsonl` (`kind: marketplace_agentic`).

Implemented in `game/server.py`: `run_agentic_search()`,
`start_agentic_search()`, `listings_agentic()`, and the extended
`listings_for(cfg, industry, session_id)` tier chain. Left in place, dormant.

## Path D - executed: offline precompute, free-weighted

Ran 8 `cortex exec` calls (one per industry, in parallel, ~4 minutes total
wall time), each phrased as a realistic visitor problem statement and
explicitly asked to prioritise Free/free-trial listings. Every candidate was
verified the same way `marketplace-index.md`'s existing entries are:
`SHOW AVAILABLE LISTINGS` (region, by-request, discover-only) **plus one
check that was missing from `build_marketplace_index.py` until today -
`is_ready_for_import`**. A listing can pass every other check and still be
genuinely unattachable if this is false.

That check caught real, pre-existing drift, not just new candidates: **five
already-curated listings turned out not importable** - "Snowflake Public
Data: Core Weather Data" (used in 3 industries, and already flagged as
drifted by `verify_marketplace_index.py`'s own header comment), "Carbon
Footprint Data" (2 industries), "Coal Global Data", the OTT Market Analysis
listing, and - notably - **healthcare's one Paid listing, Element Data
HCPCS, which was not just expensive but not actually attachable either.**
All five were dropped and replaced with verified, importable, Free
alternatives (provider + access terms confirmed via a real rendered browser
page for every new entry, matching the file's existing rigor).

**Result:** all 8 industries now offer 6 curated listings, **100% Free**,
zero Paid. `scripts/build_marketplace_index.py --write` regenerated
`marketplace-index.md`; `python3 decision_tree.py` regenerated
`decision_tree.md` (which had its own bug fixed in the same pass - it was
counting a dead `config.json` field instead of parsing the real file, so
"5 curated joins" never reflected what visitors actually saw).

One known, separate finding from this work, **not fixed** (out of this
task's scope): `server.py`'s Tier 1 live SQL (`refresh_live_listings()`)
filters `WHERE "regions" LIKE '%eu-west-2%'`, which does not match the
literal string `"ALL"` that Snowflake returns for universally-available
listings - so any listing available in every region is silently invisible
to Tier 1, account-wide, not just for these industries. Six of the new Tier 2
picks are region=`"ALL"` and are unaffected (Tier 2 is a static file, not
re-queried via that SQL), but Tier 1 itself would benefit from the same
one-line fix already made in `build_marketplace_index.py`'s `available_in()`.

## Recommendation

Current state is booth-ready: Tier 1 → Tier 2 (now 6-for-6 free per
industry) is the live chain, unaffected by any of the above. Re-enable Tier 0
only once real Library-stage dwell time is measured. Consider fixing the
`server.py` Tier 1 "ALL"-region gap separately - small, safe, and would let
some of today's Tier 2-only picks surface live too.

