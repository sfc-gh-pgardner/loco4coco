# Weak-fit review — marketplace curation, all three events

Reviewed against `audit/marketplace-se-review.html` (generated 2026-09-20, commit `8726aaa`).
Extraction is reproducible via `scripts/weakfit_review_extract.py`.

## The 97 flags are not 97 decisions

The report flags **97 weak fits**. Splitting them by the table they sit in changes
the size of the job by more than an order of magnitude:

| City | Primary picks | **weak in primary** | Reserve | weak in reserve | Candidates queue |
|---|---|---|---|---|---|
| London | 48 | **0** | 48 | 13 | 10 |
| Paris | 48 | **4** | 48 | 40 | 54 |
| Berlin | 48 | **3** | 47 | 37 | 34 |

90 of the 97 are in **reserves**, which a visitor never sees. They are parked, real,
checked local data — exactly as intended. They need no decision unless something is
promoted out of them.

**Only 7 weak fits are on a stall a visitor is shown.** 6 of the 7 are in
**Manufacturing & Industrial**, which is the starved sector the curation commit
predicted. London is clean at zero.

## Verdicts on the 7

### Paris — Manufacturing & Industrial (3 weak of 6)

Genuine picks: CEIC Shipping, CEIC Commodities, Annual Regional Production of
Renewable Energies in France (defensible as industrial energy input cost).

| Pick | Verdict | Reason |
|---|---|---|
| French National Addresses | **KEEP** | Thin but defensible — supplier and site geocoding is a real logistics use. Least-bad filler. |
| Franciemes IRIS | **REJECT** | IRIS is French census small-area geography. Consumer/demographic, no manufacturing read. |
| French National Health and Social Facilities | **REJECT** | Wrong sector outright. This is the exact defect the last commit set out to fix and it survived into a primary slot. |

Paris reserve offers no on-theme replacement — all six are population, purchasing
power or road casualties.

### Paris — Media, Telco & Entertainment (1 weak of 6)

| Pick | Verdict | Reason |
|---|---|---|
| Annual Regional Production of Renewable Energies in France | **REJECT — replace** | No media read at all. Promote **Shopping center footfall – London and Paris** from reserve: footfall is directly relevant to out-of-home advertising and venue audience, and it is already ✓ in region. |

### Berlin — Manufacturing & Industrial (3 weak of 6)

Genuine picks: CEIC Shipping, CEIC Commodities, Company data.

| Pick | Verdict | Reason |
|---|---|---|
| Germany H3 Travel Matrix | **KEEP** | Freight and distribution routing is a legitimate manufacturing use. |
| Intelligent Event Data: Attended Events, Munich | **REJECT — replace** | Events data has no manufacturing read. Promote **Overture Maps – Transportation** (verified `✓ usable` in the Berlin candidates queue). |
| Purchasing Power for Countries Worldwide | **REJECT — replace** | Consumer spending, and worldwide rather than German. Promote **Industry Classification Systems (NAICS, ANZSIC, ISIC, UK-SIC)** from reserve. |

## The false positive worth fixing in the curator

**Industry Classification Systems** is flagged weak fit in Berlin manufacturing
reserve, but industrial classification is squarely on theme — it is a primary,
unflagged pick in London. The theme list for `manufacturing` matches `industr`,
so the flag is a miss in the ranking rather than the keyword list. Treat the flag
as advisory, not authoritative.

## Paris manufacturing is a genuine regional data gap, not a curation failure

London's manufacturing stall is strong because three on-theme datasets are
available in `AWS_EU_WEST_2`: Overture Maps – Transportation, FactSet Supply Chain
Relationships, and Industry Classification Systems.

Both of the first two are verified **not offered in `AWS_EU_WEST_3`**, and Industry
Classification Systems does not appear in the Paris catalogue at all. So Paris
cannot be brought to London's standard by re-curating — the data is not there.

Accept a Paris manufacturing stall of **four** defensible picks (three genuine plus
French National Addresses) rather than padding it to six with health facilities and
census geography. A visitor in a manufacturing business who is shown hospital
locations learns that we were not really listening.

## Actions

1. Drop 2 picks with no replacement — Paris manufacturing: Franciemes IRIS, French National Health and Social Facilities.
2. Promote 3 replacements — Paris media ← Shopping center footfall; Berlin manufacturing ← Overture Maps – Transportation, Industry Classification Systems.
3. Keep 2 as defensible — Paris French National Addresses, Berlin Germany H3 Travel Matrix.
4. Leave all 90 reserve flags alone.
5. Let Paris manufacturing show four, and do not treat that as a defect to fix.

## Outcome — applied 2026-09-21 (`scripts/apply_weakfit_review.py`)

Weak fits on a stall a visitor sees: **London 0, Paris 1, Berlin 1** (from 0 / 4 / 3).
The two that remain are precisely the two kept deliberately at action 3, so the report
and the review now agree.

Berlin manufacturing is now a genuinely strong stall: CEIC Shipping, CEIC Commodities,
Company data, Germany H3 Travel Matrix, Industry Classification Systems, Overture Maps –
Transportation.

### Reject has to mean removed, not demoted

Demoting the two Paris rejects to reserve **did not remove them from the stall**, and
this is worth knowing before anyone repeats it. The stall is assembled primary-then-reserve
and sliced to six, so reserve doubles as the filler for a short stall. Paris manufacturing
has four on-theme picks, so a demoted row simply reappeared at position five. They are now
deleted from `marketplace.json`; the record of what they were and why they went lives here
and in git.

There is no per-pick exclusion mechanism. `marketplace.industry_avoid` in `config.json`
looks like one but only filters the **live** catalogue search, never curated picks.

### Consequence to accept: Paris manufacturing still pads to six

With the two rejects gone, slots five and six fill from reserve with NIQ-GfK and MBI
purchasing power — off-theme for manufacturing, though far less jarring than hospital
locations. **Showing four would require changing the six-slice for every stall in every
city**, so it was not done unilaterally. If a four-option manufacturing stall is wanted,
that is a deliberate behaviour change to make on purpose.

### Not in scope, but noted

`French National Health and Social Facilities` still sits at position five of the **Paris
media** stall. The curator did not flag it there so it was outside this review, but it is
as questionable for media as it was for manufacturing. Worth a look next pass.
