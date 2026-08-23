# Loco4CoCo game v2 - persona audit report

**Date:** 2026-08-06 · **Harness:** `http://127.0.0.1:4747/` (`python3 server.py`)
**Method:** two agentic-browser passes walking the app as a visitor, plus an
API-level smoke test (`game/smoke_test.py`). Playwright was not installed and
the game is a single static page with no npm project, so the skill's
agentic-browser fallback was used rather than introducing a JS toolchain.

## Persona lenses

| Lens | Instantiated as | What a pass proves |
|---|---|---|
| End-user | The booth visitor - a data or service lead with five minutes and no Snowflake account | They reach a named POC and leave with something usable, without typing much |
| Economic buyer | The visitor's own director, who reads the email later | The blueprint is credible, specific to their sector, and honest about gaps |
| Champion | The SE running the booth | Nothing on screen embarrasses them; the reasoning stream is a feature, not a leak |
| Author/owner | Paddy | The app matches the brief and never presents a queued email as a sent one |

## Result

**Gate: PASS**, with two items carried (below).

### Pass 1 findings, all fixed

| Defect | Severity | Fix |
|---|---|---|
| Reset leaked visitor 1's name, employer and email to visitor 2 | **Blocker** | `NEW VISITOR` control + `write_state(replace=True)` |
| `write_state` merged `poc: {}` instead of replacing, so reset never cleared the POC | **Blocker** | `replace` flag; proven zero residue for `dave`/`camden`/`policy` |
| Reasoning tray broke character - "the user wants me to respond as CoCo the Snowflake penguin" - and named internal tools | High | `_TRAY_BLOCK` filter; 0 leaks across four sectors |
| The blueprint was built but never shown to the visitor | High | `/api/blueprint` + on-screen reveal at the postbox |
| Panel clipped ~40% at small windows, `CONFIRM` unreachable | High | Overlay fixed to viewport, card `max-height: 88vh` |
| Canvas sized once at load, wrong after any resize | Medium | `fitCanvas()` on `resize` |
| 5:00 countdown expired in silence | Medium | Reads `OVER` and CoCo nudges once; play continues |
| Workshop returned no archetype, so every POC got the same wrong guide | High | Archetype enumerated in the prompt; now resolves correctly across inputs |
| `email_sent` reported true when the Gmail tool was missing | **Blocker** | Verdict JSON, fail closed; `email_sent` tracks a confirmed draft only |
| "a case or EPR system" | Low | "a PAS or EPR system" |

### Verified working

- Industry inference: NHS Trust → healthcare, Barclays → financial, Camden Council → public, Lloyds → financial, Acme Ltd → other.
- Archetype resolution varies correctly with input: complaints backlog → `ask-my-documents` (Cortex Search RAG guide); missed-payment prediction → `predict-what-happens-next` (ML Functions forecasting guide).
- Reasoning tray streams genuine `thinking` blocks with a live elapsed counter, and never duplicates the reply that lands in the bubble.
- No blinking caret anywhere: one `@keyframes pulse` in the whole stylesheet, on the tray's live dot.
- Document chain end to end: `python-docx` → `snow stage copy` → `GET_PRESIGNED_URL` → public GET returns `Microsoft OOXML`, 37 KB, opens cleanly.
- Gmail `create_draft` proven from an interactive session: `labelIds: ["DRAFT"]`.
- Honest state at the postbox: `queued: true`, `draft_created: false`, `email_sent: false`.

### Measured timing

CoCo wait totals **126s of the 300s budget** (library 26s, marketplace 18s,
workshop 32s, postbox 50s), leaving ~174s for reading, choosing and walking.
Feasible but tight - the postbox is the longest wait and lands last.

## Carried items

1. **No email has actually been sent to an external recipient.** The draft is
   proven; pressing Send is not. Until someone does that once, delivery is
   unproven.
2. **No human-timed run.** The 126s above is machine-measured CoCo latency, not
   three real people walking the map. The five-minute claim stays an estimate
   until it is observed.

## Known and accepted

- `/api/state` is unauthenticated on loopback and exposes visitor PII plus a
  live presigned URL. Acceptable for a booth laptop; do not bind to `0.0.0.0`.
- The send depends on an operator draining `outbox/`. Documented in the
  loco4coco-ops skill. If nobody drains it, nobody gets an email.
- CoCo's thinking occasionally refers to the visitor in the third person and so
  infers gender from a first name. Low impact, in the tray only.

## Marketplace curation audit (2026-08-07)

Verifies the Marketplace is curated per industry and region-filtered, not fixed.

**Curation matrix (deterministic, all 8 industries via `listings_for`).** Each
industry returns 5 listings valid in the event region `AWS_EU_WEST_2`. The
distinctness check found **no two industries with an identical listing set**.
Every returned listing includes `AWS_EU_WEST_2` in its regions or a truncated
`+N` list (region filter working). Spot examples:
- financial: FX Rates, Inflation Forecasting, UK Company Data, IBISWorld SIC, CSRHub ESG
- public: UK Census 2021, CACI Address Spine, CARTO Boundaries, Acorn, Met Office Severe Weather
- healthcare: UK Census, Acorn, Postcode Weather, PubMed, HCPCS (Paid, labelled)
- energy: Postcode Weather, Severe Weather Warning, Yes Energy, Coal Global, Carbon Footprint

**Live end-to-end flows (real `cortex exec`, per industry).**
- **Healthcare (NHS Foundation Trust):** library offered clinical items; stall
  offered Census/Acorn/PubMed/HCPCS; CoCo joined Census+Acorn to patient records
  and framed it as surfacing health inequalities / unmet need. Turns 28s + 28s.
- **Energy (National Grid):** library offered smart-meter/network data; stall
  offered weather + severe-weather + Yes Energy; CoCo joined the weather feeds to
  predict localised demand spikes and pre-position crews before storms. 30s + 26s.

Both stalls were distinct, region-valid, and industry-appropriate, and CoCo's
live reply was tailored to the sector. Combined with the earlier full Financial
walkthrough, curation is confirmed working across use cases.

**Not exhaustively browser-tested:** retail, public, manufacturing, media, other
were verified at the curation layer (matrix above) but not driven end-to-end;
the two live flows plus the Financial walkthrough are taken as representative.
