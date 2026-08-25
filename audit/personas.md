# Personas — one per industry track

Authored for `demolish-audit`. Each industry track is a different demo: a
different letter, a different set of library options, a different Marketplace
stall, and a different archetype at the workshop. So each needs its own persona,
its own journey, and its own acceptance criteria.

Three lenses per persona, per demolish-audit:

- **end-user** — the person at the booth who plays it
- **economic buyer** — the person back at the office who pays for Snowflake
- **champion** — the Snowflake SE on the stand who has to defend the output

The gate rule: a story marked **KEY** is gate-blocking. **ADV** is advisory —
reported, does not block.

---

## Cross-cutting stories (apply to every persona)

| ID | Lens | Story | Acceptance criterion | Rank |
|---|---|---|---|---|
| X1 | end-user | The letter asks me only what it needs | The letter form has exactly 4 controls and **no email field** | KEY |
| X2 | end-user | The library offers data that sounds like MY world | The 6 data-source labels match this industry's `data_sources`, not the generic set | KEY |
| X3 | end-user | The stall offers data I could actually attach | 6 Marketplace picks, every one `Free`, none `by request` | KEY |
| X4 | champion | I can defend every pick as relevant | No pick is off-geography for a UK stand; weather is at most 1 unless weather is core to the industry | KEY |
| X5 | end-user | I am not asked to contradict myself | "Already in Snowflake" / "Not sure yet" cannot be combined with a named platform | KEY |
| X6 | end-user | I can see where my data lives without hunting | The platform chips are in the viewport once revealed, and CONFIRM is reachable | KEY |
| X7 | buyer | I leave with something concrete | The blueprint names a real Snowflake feature and a guide to fork | KEY |
| X8 | buyer | The route into Snowflake is spelled out | The blueprint names an ingestion route for each platform picked | KEY |
| X9 | champion | The document is never self-contradictory | Blueprint never says "Nothing to move" alongside move instructions | KEY |
| X10 | end-user | Nothing looks broken | No clipped text, no dark-on-dark, interior is a room not a letterbox strip | KEY |
| X11 | champion | The same taps produce the same document | Two identical runs produce the same Marketplace set and route order | ADV |

---

## 1. Healthcare & Life Sciences

**end-user — Dr Amara Okafor, Clinical Informatics Lead, Royal Free London NHS FT**
Has 11 years of discharge summaries and referral letters in a Trust EPR. Cannot
answer "which patients waited longest and why" without a data team ticket.

- **Pain:** free-text clinical correspondence is unqueryable
- **Buyer:** Trust CIO — funds it if it cuts the elective backlog
- **Champion:** SE must not appear to give clinical or IG advice

| ID | Story | Acceptance criterion | Rank |
|---|---|---|---|
| H1 | Library speaks clinical | Options include "Patient records" and "Clinical notes & letters" | KEY |
| H2 | Stall offers health-relevant UK data | At least 2 picks are UK population/health (Census, Acorn, UK Health Facts) | KEY |
| H3 | Free-text problem drives the archetype | Blueprint archetype is document/search-shaped, not forecasting | ADV |

## 2. Financial Services

**end-user — Tom Whitfield, Head of Data, mid-tier UK retail bank**
Transaction history in Oracle, risk models in spreadsheets. Wants to explain
fraud alerts to a regulator.

- **Pain:** cannot join transactions to external reference data
- **Buyer:** CDO — funds it for regulatory defensibility
- **Champion:** must not imply a compliance guarantee

| ID | Story | Acceptance criterion | Rank |
|---|---|---|---|
| F1 | Library speaks banking | Options include "Transaction history" and "Positions & trades" | KEY |
| F2 | Oracle route is CDC, not a nightly dump | Blueprint names Openflow Oracle CDC when Oracle is picked | KEY |
| F3 | No weather in the stall | 0 Met Office picks | KEY |

## 3. Retail & Consumer Goods

**end-user — Priya Raman, Trading Analyst, UK grocery chain**
Till transactions and loyalty data. Wants to know why a store underperforms.

- **Pain:** no external context for catchment or demand
- **Buyer:** Commercial Director — funds it for margin
- **Champion:** weather IS legitimate here (demand driver)

| ID | Story | Acceptance criterion | Rank |
|---|---|---|---|
| R1 | Library speaks retail | Options include "Sales & till transactions" and "Loyalty & customer data" | KEY |
| R2 | Stall is UK-catchment shaped | Picks include UK income/geodemographic data (PayCheck, Acorn) | KEY |
| R3 | Weather is allowed but not dominant | Met Office picks <= 2 | ADV |

## 4. Public Sector & Government

**end-user — Sam Booth, Head of Digital, Leeds City Council**
Planning applications and case records. Wants to cut determination times.

- **Pain:** case data not joined to address or boundary reference data
- **Buyer:** Director of Resources — funds it against a statutory target
- **Champion:** **this is the track that failed.** Three of six picks were Met
  Office weather and one was *India Economic Monitor* on a UK stand.

| ID | Story | Acceptance criterion | Rank |
|---|---|---|---|
| P1 | Library speaks local government | Options include "Case management records" and "Policy & guidance documents" | KEY |
| P2 | Stall is UK public-sector reference data | >= 4 picks are UK geography/population (Census, OS Boundary Line, Address Spine, Acorn, CARTO) | KEY |
| P3 | **No off-geography picks** | 0 picks naming a non-UK country or "International" | KEY |
| P4 | **Weather does not dominate** | Met Office picks <= 1 | KEY |
| P5 | Ordnance Survey survives the region filter | OS Boundary Line (`regions = ALL`) is present | KEY |

## 5. Manufacturing & Industrial

**end-user — Greg Nowak, Plant Systems Manager, Midlands automotive tier-1**
Machine telemetry on-premise, ERP in SAP. Wants to predict defects.

- **Pain:** high-volume sensor data stuck on the shop floor
- **Buyer:** Ops Director — funds it against scrap rate
- **Champion:** on-prem route must not require inbound exposure

| ID | Story | Acceptance criterion | Rank |
|---|---|---|---|
| M1 | Library speaks the factory | Options include "Machine & sensor telemetry" and "Quality & defect records" | KEY |
| M2 | On-prem route is outbound-only | Blueprint says Openflow runs inside the network and pushes out | KEY |
| M3 | SAP route offers the Iceberg option | Blueprint names SAP BDC / Iceberg when SAP is picked | ADV |

## 6. Energy & Utilities

**end-user — Fiona Hargreaves, Network Data Manager, UK DNO**
Smart meter reads and outage records. Wants to forecast constraint.

- **Pain:** meter volume vs network asset data
- **Buyer:** Network Director — funds it against Ofgem targets
- **Champion:** weather is core here — 2 picks defensible

| ID | Story | Acceptance criterion | Rank |
|---|---|---|---|
| E1 | Library speaks utilities | Options include "Smart meter readings" and "Outage & fault records" | KEY |
| E2 | Weather is justified, not padding | Met Office picks <= 2 AND at least 3 non-weather picks | KEY |

## 7. Media, Telco & Entertainment

**end-user — Dan Mercer, Audience Insight Lead, UK broadcaster**
Viewing data and subscriber records. Wants to cut churn.

- **Pain:** viewing behaviour not joined to audience context
- **Buyer:** CMO — funds it against churn
- **Champion:** must be UK audience data, not US

| ID | Story | Acceptance criterion | Rank |
|---|---|---|---|
| T1 | Library speaks media | Options include "Viewing & listening events" and "Subscriber & account data" | KEY |
| T2 | Stall is UK audience shaped | >= 2 UK-signal picks | KEY |

## 8. Something else (the fallback)

**end-user — Alex Deniz, Ops Manager, an SMB the taxonomy does not cover**
Picked "Something else" or let CoCo guess.

- **Pain:** the generic path must still feel bespoke
- **Buyer:** MD — funds it if the output is not obviously templated
- **Champion:** must never look like a fallback

| ID | Story | Acceptance criterion | Rank |
|---|---|---|---|
| O1 | Generic library is broad but purposeful | 6 options, generic set, each with a note | KEY |
| O2 | Stall still fills and is still free | 6 picks, all Free | KEY |
| O3 | Never says "other" or "fallback" to the visitor | No visitor-facing string contains "fallback"/"other industry" | ADV |

---

## Persona coverage matrix

| Industry | Chromium flow | Library asserted | Stall asserted | Guardrail asserted | Blueprint asserted |
|---|---|---|---|---|---|
| Healthcare | full | yes | yes | yes | yes |
| Financial | full | yes | yes | yes | yes |
| Retail | flow to stall | yes | yes | yes | - |
| Public sector | full | yes | yes | yes | yes |
| Manufacturing | flow to stall | yes | yes | yes | - |
| Energy | flow to stall | yes | yes | yes | - |
| Media | flow to stall | yes | yes | yes | - |
| Something else | flow to stall | yes | yes | yes | - |

Full flow (through workshop + postbox, which costs a model call per stop) runs
for three tracks; the rest assert everything up to and including the stall and
the guardrail. Rationale: the library, stall and guardrail are where the
industry branching actually lives, and they are deterministic — the workshop is
the same code path for every industry with a different prompt.

---

## Audit verdict — demolish-audit gate

**Run:** real Chromium (Playwright), viewport 1512x800, serial single worker.
**Result: 35 / 35 PASS. Gate: SHIP.**

Re-run any time with the server up:

```
npx --no-install playwright test --config audit/playwright.config.js
```

Serial by design: the server holds one visitor in `state.json` per process, so
parallel tracks would overwrite each other's industry.

### Defects this audit found that the agentic browser had missed

| Defect | Detail |
|---|---|
| **Interiors were stretched ~30%** | `syncSceneBuffer()` floored the pixel buffer at 300px while the box was 288px tall at 1512x800, giving a buffer ratio of 0.284 against a CSS ratio of 0.218. Only reproducible at a real booth viewport height - the earlier pass ran at 890-1203px where the clamp never bit. Floor removed. |
| **Public sector stall was off-brief** | 3 of 6 picks were Met Office weather and one was *India Economic Monitor* on a UK stand. |
| **Ordnance Survey silently dropped** | `regions = ALL` was substring-matched like a region list, so it matched nothing. Public sector shipped 5 picks instead of 6 and lost OS Boundary Line. |

### Coverage

- 8 industry tracks, each with its own persona, letter, library, stall and journey
- 4 checks per track (letter, library + visual, guardrail + reachability, stall)
- 3 tracks additionally driven through workshop and blueprint (healthcare,
  financial, public sector)
