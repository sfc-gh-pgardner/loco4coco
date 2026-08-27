# Loco 4 CoCo - the booth decision tree

_Generated from the live `config.json`, `archetypes.md` and `server.py`. Every option below is what a visitor is actually offered. Regenerate with `python3 game/decision_tree.py` after changing config._

## Why this document exists

A home stage and five screens shape the blueprint. All but one are precomputed by us; only the archetype is decided at runtime, and it matters which is which - only the precomputed ones can be improved by editing config.

| Step | What the visitor does | Where the options come from | Tunable? |
|---|---|---|---|
| 0. The home stage | Answers where their data lives (platforms), which country they are in, and where their data and AI may run (residency) | `config.platforms`, `config.country`, `config.residency`, `config.sovereignty` | **Yes - fully precomputed** |
| 1. The letter | Types name, company, industry, **and the problem in two sentences** | Industry list in `config.industries` | Yes - the list |
| 2. The library | Ticks the data they hold | `industries.<key>.data_sources` | **Yes - fully precomputed** |
| 3. The marketplace | Ticks data to join | `marketplace-index.md`, 6 verified listings per industry | **Yes - fully precomputed** |
| 4. The workshop | Types one line describing the MVP | Free text | No - but the archetype it maps to is |
| 5. The postbox | Posts it | - | - |

With `discovery: manual` there is now only ONE runtime decision: which of the 9 archetypes the visitor is routed to. Even that is no longer purely the model's - `game/context.py` resolves it deterministically from the visitor's own words scored against each archetype's pain text, and the model chooses from that shortlist. Everything else on this page is ours to set.

## The tree, top to bottom

```
HOME STAGE   (precomputed; CoCo reacts to each with a pre-written line)
  platform  ->  9 universal chips -> integration path in the blueprint
  country   ->  8 options -> region logic
  residency ->  4 options (sovereignty-framed) -> blueprint sovereignty section
        |
LETTER
  industry  ->  one of 8
  problem   ->  free text, 400 chars, threaded into every later prompt
        |
LIBRARY   (precomputed per industry)
  data held ->  6 options per industry + "something else"
        |
MARKETPLACE
  6-6 curated, region-verified options per industry  (discovery: manual)
  every one is checked is_ready_for_import, so a visitor can attach it
        |
WORKSHOP
  one line  ->  model picks 1 of 9 archetypes
             ->  features + first step come from archetypes.md, no inference
        |
POSTBOX   ->  QA review, then blueprint (.docx) + QR. No email, no local record.
```

## Per industry

For each industry: what the library offers, and the six curated Marketplace listings it offers. Every listing is verified importable in the event region, so nothing here is a dead end. The live-search keywords are listed too, but they only bite if `locations.marketplace.discovery` is set back to `live`.

### Healthcare & Life Sciences

`healthcare` - 6 data sources, 6 curated joins, 16 live-search keywords, 0 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Patient records | Structured clinical records in a PAS or EPR system |
| Clinical notes & letters | Free text - discharge summaries, referrals, correspondence |
| Referral & waiting list data | Pathways, breaches, appointment scheduling |
| Clinical trial data | Protocols, recruitment, outcomes |
| Imaging & diagnostics | Scan metadata and reports |
| Estates & operations | Beds, theatres, staffing rotas, supplies |

**Marketplace - the six curated joins offered, all verified importable**

| Listing | Provider | Access |
|---|---|---|
| UK (England and Wales only) Census 2021 - Trial | Jaywing | Free |
| Acorn - Geodemographic Segmentation in the UK | CACI Ltd | Free |
| Postcode Sector Weather Forecasts | Met Office | Free 14-day trial |
| PubMed Biomedical Research Corpus | Snowflake | Free |
| UK Health Facts and Dimensions Sample | Facts and Dimensions Ltd | Free |
| Household Acorn - geodemographic segmentation at household level SAMPLE DATA | CACI Ltd | Free |

**Live-search keywords** (16): clinical, patient, nhs, health, disease, epidemiolog, population health, prescrib, wellbeing, mortality, hospital, medic, pharma, drug, life science, biotech

### Financial Services

`financial` - 6 data sources, 6 curated joins, 12 live-search keywords, 0 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Transaction history | Card, payment and account movement |
| Customer & account master | KYC records, product holdings, segments |
| Positions & trades | Holdings, orders, execution history |
| Risk & capital models | Exposures, limits, stress test inputs |
| Customer communications | Call transcripts, complaints, chat logs |
| Regulatory reporting | Submissions and the reconciliations behind them |

**Marketplace - the six curated joins offered, all verified importable**

| Listing | Provider | Access |
|---|---|---|
| Snowflake Public Data: Foreign Exchange Rates | Snowflake Public Data Products | Free 60-day trial |
| Inflation Forecasting - Headline & Core CPI by Country | Turnleaf Analytics | Free |
| Company Data UK (incl. Guernsey) - XL Dataset | North Data GmbH | Free 7-day trial |
| Industry Classification Systems (NAICS, ANZSIC, ISIC, UK-SIC, etc.) | IBISWorld | Free |
| CSRHub ESG (Environment, Social, Governance) Fast Start | CSRHub LLC | Free 30-day trial |
| Banking Analytics Bundle | InSights | Free |

**Live-search keywords** (12): foreign exchange, inflation, credit, risk, equity, market, macro, payments, fraud, interest rate, economic, commodit

### Retail & Consumer Goods

`retail` - 6 data sources, 6 curated joins, 11 live-search keywords, 2 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Sales & till transactions | Basket-level sales by store and channel |
| Inventory & stock positions | Availability, shrink, replenishment |
| Loyalty & customer data | Membership, spend history, segments |
| Web & app clickstream | Browse, search and cart behaviour |
| Supplier & logistics data | Purchase orders, lead times, delivery performance |
| Reviews & customer service | Free text feedback, returns reasons, contact logs |

**Marketplace - the six curated joins offered, all verified importable**

| Listing | Provider | Access |
|---|---|---|
| Postcode Sector Weather Forecasts | Met Office | Free 14-day trial |
| Acorn - Geodemographic Segmentation in the UK | CACI Ltd | Free |
| PayCheck - UK household income estimates at postcode level - SAMPLE data | CACI Ltd | Free |
| UK (England and Wales only) Census 2021 - Trial | Jaywing | Free |
| Industry Classification Systems (NAICS, ANZSIC, ISIC, UK-SIC, etc.) | IBISWorld | Free |
| Spatial Features (GBR, Quadgrid 15 and H3 Res. 8) | CARTO | Free |

**Live-search keywords** (11): consumer, footfall, spend, household income, demographic, acorn, basket, weather, postcode, segmentation, price

**Pinned listings**: GZTDZJKVCY, GZSVZAJO3

### Public Sector & Government

`public` - 6 data sources, 6 curated joins, 11 live-search keywords, 3 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Case management records | Casework across service lines |
| Policy & guidance documents | Years of PDFs, circulars and statutory guidance |
| Citizen contact & correspondence | Calls, emails, webforms, complaints |
| Assets & estates | Property, highways, fleet, maintenance |
| Finance & procurement | Budgets, spend over threshold, contracts |
| Performance & statutory returns | KPIs and central government reporting |

**Marketplace - the six curated joins offered, all verified importable**

| Listing | Provider | Access |
|---|---|---|
| UK (England and Wales only) Census 2021 - Trial | Jaywing | Free |
| Address Spine - UK address level property information - Sample Data | CACI Ltd | Free |
| CARTO Boundaries | CARTO | Free |
| Acorn - Geodemographic Segmentation in the UK | CACI Ltd | Free |
| National Severe Weather Warning Service | Met Office | Free |
| Administrative boundaries - Great Britain: Boundary Line - Open | Ordnance Survey | Free |

**Live-search keywords** (11): census, postcode, deprivation, boundary, population, geospatial, planning, crime, education, transport, uprn

**Pinned listings**: GZSVZAJO3, GZ1MOZBWYYT, GZSVZ1K7UQ

### Manufacturing & Industrial

`manufacturing` - 6 data sources, 6 curated joins, 20 live-search keywords, 0 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Machine & sensor telemetry | High frequency readings off the line |
| Quality & defect records | Inspection results, scrap, rework |
| Maintenance logs | Work orders and engineer free text |
| ERP & production planning | Orders, BOMs, schedules, yields |
| Supplier & inbound logistics | Component lead times and quality by supplier |
| Energy consumption | Meter data by line and site |

**Marketplace - the six curated joins offered, all verified importable**

| Listing | Provider | Access |
|---|---|---|
| CEIC Commodities Data | CEIC Data | Free |
| Company Data UK (incl. Guernsey) - XL Dataset | North Data GmbH | Free 7-day trial |
| Overture Maps - Transportation | CARTO | Free |
| FactSet Supply Chain Relationships (sample) | FactSet | Free |
| D&B Shipping Insights Sample | Dun & Bradstreet | Free |
| Solid United Nations Codes for Trade and Transport Locations | Solid Data LLC | Free 30-day trial |

**Live-search keywords** (20): supply chain, logistics, commodit, shipping, freight, industrial, manufactur, materials, energy price, trade, tariff, production, inventory, supplier, port, vessel, steel, metal, company data, economic

### Energy & Utilities

`energy` - 6 data sources, 6 curated joins, 11 live-search keywords, 3 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Smart meter readings | Interval consumption at premise level |
| Network & asset data | Substations, pipes, cables, condition |
| Outage & fault records | Interruptions, causes, restoration times |
| Generation & dispatch | Output, availability, curtailment |
| Customer & billing | Accounts, tariffs, arrears, vulnerability flags |
| Field engineer reports | Free text inspection and repair notes |

**Marketplace - the six curated joins offered, all verified importable**

| Listing | Provider | Access |
|---|---|---|
| Postcode Sector Weather Forecasts | Met Office | Free 14-day trial |
| National Severe Weather Warning Service | Met Office | Free |
| Yes Energy - Sample Data | Yes Energy | Free |
| Sample of GasMarketCube - Global Gas Supply, Demand and Trade | Rystad Energy | Free |
| Wind Power Forecast, Day-ahead - Sample | Weather Solutions | Free |
| Crude oil price data | General Index | Free Trial |

**Live-search keywords** (11): weather, climate, emission, carbon, grid, renewable, solar, wind, temperature, energy, net zero

**Pinned listings**: GZTDZJKVCM, GZTDZJKVCU, GZTDZJKVCY

### Media, Telco & Entertainment

`media` - 6 data sources, 6 curated joins, 10 live-search keywords, 0 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Viewing & listening events | Play, pause, completion by title and device |
| Subscriber & account data | Plans, churn, lifetime value |
| Content catalogue & metadata | Titles, rights, genres, availability windows |
| Network performance | Throughput, latency, coverage, faults |
| Advertising & campaign data | Impressions, fill rate, yield |
| Customer support interactions | Call transcripts and chat logs |

**Marketplace - the six curated joins offered, all verified importable**

| Listing | Provider | Access |
|---|---|---|
| Acorn - Geodemographic Segmentation in the UK | CACI Ltd | Free |
| UK (England and Wales only) Census 2021 - Trial | Jaywing | Free |
| CARTO Boundaries | CARTO | Free |
| Spatial Features (GBR, Quadgrid 15 and H3 Res. 8) | CARTO | Free |
| GLP-1 Social Conversations Sample Dataset | Socialgist | Free |
| American Community Survey, 2016 | data.world, Inc | Free |

**Live-search keywords** (10): audience, media, broadband, mobile, advertising, viewership, telco, subscriber, content, social

### Something else

`other` - 6 data sources, 6 curated joins, 6 live-search keywords, 1 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Core operational records | Whatever your main system of record holds |
| Documents & PDFs | Years of unstructured files nobody can query |
| Customer or member data | Who you serve and what they have done |
| Finance & billing | Revenue, spend, invoices |
| Emails, calls & tickets | Free text interactions |
| Device or sensor data | Anything machine-generated and high volume |

**Marketplace - the six curated joins offered, all verified importable**

| Listing | Provider | Access |
|---|---|---|
| UK (England and Wales only) Census 2021 - Trial | Jaywing | Free |
| Company Data UK (incl. Guernsey) - XL Dataset | North Data GmbH | Free 7-day trial |
| CARTO Boundaries | CARTO | Free |
| Snowflake Public Data: Foreign Exchange Rates | Snowflake Public Data Products | Free 60-day trial |
| CARTO Analytics Toolbox | CARTO | Free |
| Acorn - Geodemographic Segmentation in the UK | CACI Ltd | Free |

**Live-search keywords** (6): weather, census, demographic, postcode, economic, geospatial

**Pinned listings**: GZTDZJKVCY

## The platform question, and what it produces

Asked once on the home stage, one tap, universal across industries. Each chip writes a concrete route into the blueprint, so this is the section that turns "we have the data somewhere" into a first task.

| Chip | Route the blueprint prints |
|---|---|
| Microsoft / Azure | Openflow has a first-party connector for Azure Blob Storage and SQL Server. For Fabric or OneLake, register the Iceberg tables through a catalog integration and query them in place - no copy. |
| AWS | Point an external stage at the S3 bucket with a storage integration, then Snowpipe for continuous load. If the data is already Iceberg in Glue, use a catalog integration and leave it where it is. |
| Google Cloud | A storage integration over the GCS bucket plus an external stage. BigQuery data moves cleanly as Parquet exported to GCS, or through Openflow if you need it on a schedule. |
| Oracle | Openflow's Oracle connector does change data capture, so you get an ongoing replica rather than a nightly dump. Start with the handful of tables the proof of concept actually reads. |
| SAP | Either the SAP connector for Snowflake, or SAP Business Data Cloud sharing the data as Iceberg that Snowflake reads without a copy. The second route is usually faster to stand up. |
| On-premise / our own servers | Openflow can run inside your network and push out, so nothing has to be exposed inbound. For a first proof of concept, a one-off bulk load of a representative extract is usually enough. |
| SaaS apps (Salesforce, Workday, etc.) | Openflow has connectors for the common SaaS sources, and the Marketplace carries some of them as ready-made shares. Check the Marketplace first - it is the cheaper answer when it exists. |
| Already in Snowflake | Nothing to move. Point the proof of concept at the existing tables and spend the saved time on the model and the interface instead. |
| Not sure yet | Worth ten minutes with whoever owns the source before you build. The answer changes the effort more than any other decision here. |

### Combinations, and the guardrails on them

The chips are multi-select, so most visitors tap more than one. Before the guardrails, **16 of the 36 possible pairs produced a self-contradicting document** and **10 printed "Openflow" twice**. Both are fixed, and both are enforced twice - in the browser on tap, and again on the server when the blueprint is built - so a bypassed or mis-clicked UI still cannot produce a contradictory hand-out.

| Selection | What the blueprint prints | Why |
|---|---|---|
| One cloud, e.g. **AWS** | That one route | The simple case |
| **Azure + AWS** | Both routes, Azure first | Genuinely different routes; config order decides which is printed first, so it is the same document every time regardless of tap order |
| **Already in Snowflake** alone | Its own line, no route | A legitimate answer on its own |
| **Already in Snowflake** + any named source | The named source only; "Already in Snowflake" is dropped | A named source is actionable, so it wins - printing both said "nothing to move" and "here is how to move it" in the same document |
| **Not sure yet** alone | Its own line, no route | A legitimate answer on its own |
| **Not sure yet** + any named source | The named source only; "Not sure yet" is dropped | A named source is actionable, so it wins - printing both said "nothing to move" and "here is how to move it" in the same document |
| More than 4 chips | The first 4 in config order | Caps the ingestion section so it reads as a plan, not a checklist. All 9 chips used to print 9 route paragraphs |

Verified by exhausting every single, pair and triple combination: **0 contradictions and 0 cap overruns**, worst case bounded at 4 routes.

## The 9 archetypes

The workshop is free text, but it resolves to exactly one of these. Features and the first step are precomputed, so they are instant and always correct; only the summary and the considerations need the model.

| Archetype | Features | Considerations in pool |
|---|---|---|
| talk-to-my-data | Cortex Analyst, Semantic Views, Snowflake Intelligence | 5 |
| ask-my-documents | Cortex Search, AI_PARSE_DOCUMENT, Cortex Agents | 5 |
| extract-from-paperwork | AI_EXTRACT, AI_PARSE_DOCUMENT, Dynamic Tables | 5 |
| triage-and-classify | AI_CLASSIFY, Dynamic Tables, Streams | 5 |
| an-agent-that-acts | Cortex Agents, Snowflake Intelligence, Semantic Views | 5 |
| predict-what-happens-next | ML Forecasting, ML Anomaly Detection, Snowflake Notebooks | 5 |
| join-the-silos | Dynamic Tables, Snowflake Marketplace, Semantic Views | 5 |
| share-without-copying | Secure Data Sharing, Snowflake Marketplace, Dynamic Tables | 5 |
| watch-it-live | Snowpipe Streaming, Dynamic Tables, Streams | 5 |

**First steps**

- **talk-to-my-data** - Write down the three questions people ask most, then model just the tables those need.
- **ask-my-documents** - Put fifty representative documents on a stage and see what the parser returns before building anything.
- **extract-from-paperwork** - List the fields you actually need, then test extraction on your ugliest ten documents rather than your cleanest.
- **triage-and-classify** - Agree the categories with the people who act on them, then hand-label two hundred examples as your yardstick.
- **an-agent-that-acts** - Pick one action worth automating, and write down exactly what the agent must never do.
- **predict-what-happens-next** - Check you have enough history for the thing you want to predict before modelling anything.
- **join-the-silos** - Find the one key that links your two most important systems, and check how often it is missing.
- **share-without-copying** - Pick one dataset and one partner, and write down exactly which columns they may see.
- **watch-it-live** - Define the one event worth reacting to, and how quickly someone must know about it.

## Where the precomputed suggestions are weakest

Computed, not editorial - these are the counts that stand out.

- **Healthcare & Life Sciences** has no pinned listings, so if live search returns nothing recognisable there is no guaranteed good result.
- **Financial Services** has no pinned listings, so if live search returns nothing recognisable there is no guaranteed good result.
- **Manufacturing & Industrial** has no pinned listings, so if live search returns nothing recognisable there is no guaranteed good result.
- **Media, Telco & Entertainment** has no pinned listings, so if live search returns nothing recognisable there is no guaranteed good result.
- **Something else** has only 6 live-search keywords, so it will fall back to the curated list more often than the others.

Two structural gaps worth a decision rather than a count:

- **No industry biases the archetype choice.** A hospital and a bank get the same 9 archetypes with the same weighting. A per-industry ordering, or two or three likely archetypes per industry, would make the forge both faster and more plausible.
- **The data held does not narrow the marketplace suggestion.** Someone who ticked "clinical notes" is offered the same joins as someone who ticked "estates and operations". A held-to-join mapping is the highest-value precompute still missing.

## Where the visitor's time goes

A stop is only as good as the wait in front of it, so the transport each one uses is part of the decision tree, not an implementation detail.

| Stop | Transport asked for | Ceiling |
|---|---|---|
| The Data Library | `complete` | 60s |
| The Marketplace | `complete` | 60s |
| The Workshop | `exec` | 60s |
| The Postbox | `exec` | 60s |

**Measured before any of this was built** (5 visits, `game/cost.jsonl`): the Workshop stop was 75% of all model wait at a 26.0s median, because it was the only stop running a real `cortex exec`.

`cortex exec` is a one-shot CI/CD entry point with no `--resume`, no `--session` and no `--daemon`, so every call is a cold process. Timed on a trivial prompt: 22.7s default, 19.4s with `--no-mcp`, 18.1s with every flag that helps. **About 18 seconds of that is startup, not thinking.**

So the booth now leads with a warm `cortex mcp serve` process, which is the same binary in server mode, held open between visitors:

| | cold `cortex exec` | warm agent |
|---|---|---|
| startup | ~18s, every call | 1.3s, once |
| a turn | ~26s | **~3.4s** |

### Four layers, because a stand is not a laptop at a desk

1. **warm agent** - `cortex mcp serve`, ~3.4s.
2. **`cortex exec`** - a cold one-shot. Not started unless 20s of budget remain.
3. **`COMPLETE`** - `SNOWFLAKE.CORTEX.COMPLETE`. Fast, non-agentic.
4. **precomputed** - the archetype defaults in this document. No model at all.

Layer 4 is why this document matters operationally: on a flat venue network with a suspended warehouse, what a visitor leaves with is exactly the precomputed content listed above. It is the floor, so it has to read well on its own.

### Two constraints that are not negotiable

- **One in-flight agent call at a time.** Two calls were issued on one warm process without waiting: one asked for ALPHA, one asked for BRAVO, and both received ALPHA. Concurrent calls mis-correlate, which on a stand means one visitor's content in another visitor's document with no error raised. The pool holds a mutex; a second caller waits.
- **Every turn has a wall-clock ceiling** (60s by default). The Library has been measured at a 127.3s outlier against a 2.2s median. Past the ceiling the visitor is better served by layer 4 than by a better sentence.

### Retrieval is deterministic on purpose

The closed lists reach the model as **content in the prompt**, not as a tool: `cortex exec` takes no tools except through MCP, and MCP is not guaranteed on a borrowed booth laptop. The corpus is ~150 rows, so `game/context.py` scores it in process and injects only the slice that matches the visitor's own words (~220 tokens).

No search service, deliberately. At a Snowflake-branded event the same input must give the same document, and a visitor's pain language is bridged to our feature names through the archetype **pain** text - "we retype invoices all day" shares no token with `AI_EXTRACT`, but plenty with the pain line.

## Pre-prepared scripts (for marketing review)

Every fixed line a visitor sees or hears, in running order, straight from `config.json`. **These are pre-written and identical for every visitor.** The one-line replies CoCo speaks at the Library, Marketplace and Workshop are NOT listed here: they are generated per visit by the model (SNOWFLAKE.CORTEX.COMPLETE, `mistral-large2`), reflecting back what the visitor just picked. The model PICKS from closed lists and REFLECTS; it never writes the copy below, and it cannot invent a feature, guide or listing that is not in the curated lists.

Placeholders in braces - `{country}`, `{platform}`, `{region}`, `{first_name}` - are filled from the visitor's own answers at runtime.

### Intro card

- **Title:** Loco for CoCo
- **Button:** START
- This is a fun way to experience the power of Cortex Code (CoCo) through the medium of an arcade game.
- You have 5 minutes to explore the key aspects of building out a Proof of Concept on Snowflake with CoCo as your tour guide on our features, marketplace datasets and how enterprise-grade AI can bring your ideas to life.
- After 5 minutes you will have a personalised action plan (scan it and keep it) to building out a project on Snowflake - be daring! This is a fun, flexible process with a very real and useful outcome!
- Anything you type stays private - it is shared only with you and Snowflake, and never sold on or shared with anyone else.

### Home stage - CoCo's narrative

The penguin arrives, reads a letter, and walks the visitor to the questions. Every line is fixed:

- **arctic:** Somewhere in the Arctic...
- **arctic_sub:** (Yes, penguins live in Antarctica, but CoCo is special!)
- **greeting:** Hey CoCo,
- **body:** It's your friend {first_name}! I've heard you and the Cortex Crew have been cooking up some amazing products recently. Me and my team at {company} wanted to learn more. We're particularly interested in {industry} and wanted to understand what an MVP/POC would look like for this on Snowflake. Could you help us out?
- **signoff:** Signed {first_name}
- **button:** THAT'S BETTER
- **line1:** A letter, from my friend {first_name}! Better get to work...
- **line2:** Anyway, let's go and get this show on the road.
- **map_line:** First stop is my Data Library. That's where I keep all the unstructured, semi-structured and structured data that would be useful for {first_name} and {company}.
- **bubble:** Wow, a letter from my friend! Shame I can't make out some of these words... (Please fill this in with your details)

### Home stage - the three questions

**Where does your data live today?**

- _Hint:_ Tap every platform it sits on. This is what decides how we get it into Snowflake.
- Microsoft / Azure
- AWS
- Google Cloud
- Oracle
- SAP
- On-premise / our own servers
- SaaS apps (Salesforce, Workday, etc.)
- Already in Snowflake
- Not sure yet

**And where is your company based?**

- _Hint:_ One tap. It helps me keep your data where your rules need it.
- United Kingdom
- Ireland
- France
- Germany
- Netherlands
- Nordics
- Rest of EU
- Somewhere else

**Where are your data and AI models allowed to run?**

- _Hint:_ This shapes the region we build in. One tap.
- {country} only
- Anywhere in the EU is fine
- The US is fine too
- Not sure yet

### Sovereignty - CoCo's reactions and blueprint pillars

CoCo answers each home-stage choice with a fixed reassurance (`react`); the four `pillars` are reused verbatim in the blueprint's sovereignty section.

Reactions:
- **platform_already:** Perfect - it's already in Snowflake, so we skip the plumbing and go straight to building.
- **platform_unsure:** No problem - we'll work the plumbing out together, it's usually the easy part.
- **platform_named:** Good - I know exactly how to get data out of {platform} and into Snowflake, in region and without copying it around.
- **country:** {country}, lovely. I'll keep everything where {country}'s rules need it.
- **residency_country_only:** Understood - everything stays in {country}. Your data, the AI models, all of it.
- **residency_eu:** Great - we'll keep it inside the EU. Data and models both, no border crossings.
- **residency_us_ok:** Plenty of room to work with, then - and it still stays wherever you choose.
- **residency_unsure:** We'll keep it close to home by default - you can always widen it later.

Pillars:
- **data:** Your data never leaves {region}: it stays in your own Snowflake account, in region, not copied out to be processed.
- **models:** Cortex runs the AI models where your data already lives, so nothing crosses a border to be understood.
- **marketplace:** Marketplace data is shared live rather than copied, and you are only ever offered listings available in {region}.
- **governance:** One set of controls - role-based access, masking, row-level policies - governs all of it, in one place.

### The letter - what the visitor types

- **Prompt:** Please enter your details:
- **Your first name** (`first_name`) - e.g. Priya
- **Where you work** (`company`) - e.g. NHS Trust, Barclays, Tesco
- Industry is picked from the 8-item list; the problem is free text (threaded into every later prompt and into the document).
- **Library synthetic-data hint:** CoCo can mimic any shelf as synthetic data so a POC can start before the real feed exists. Generate it in Snowflake with GENERATOR and RANDOM, or let Cortex fabricate realistic rows from a description.

### The workshop - the one line we ask for

- **heading:** Ask CoCo one thing
- **hint:** Optional. One question about your POC and CoCo will look it up properly.
- **placeholder:** e.g. what would we need before we could trust the predictions?
- **button:** ASK COCO
- **skip:** SKIP THIS

### The postbox - delivery lines

CoCo speaks one of these when the visitor presses send (`{first_name}` is filled in if given):

- **On success:** Wrapped and labelled, {first_name}. Scan the code on screen and it is yours - the link works for seven days.
- **If staging fails:** I could not wrap it up this time - grab a Snowflake person and we will sort it.

### The model prompts

The one-line replies above are generated, not scripted - so for full transparency, every prompt the booth actually sends to Cortex (the shared preamble, the Library, Marketplace and Workshop turns, the background fill and the QA relevance check) is rendered verbatim against an example visitor in `skills/loco4coco/references/model-prompts.md`. Regenerate it with `python3 scripts/build_model_prompts.py`. The rule that governs all of them: the model only ever PICKS from our closed lists and REFLECTS them back - it is never asked to invent a feature, a listing or a fact, and the same visitor input yields the same document.

## Flagged for review

Decisions for a human, not code changes. None of these stop the booth running.

- **Geo weighting is London-only.** The curated picks are scored with 19 UK preference terms and 20 non-UK demotion terms (`marketplace.geo`). Re-weight before Paris, or a French room is offered UK postcode data.
- **11 of the 48 curated slots are time-limited trials** rather than perpetual Free. Everything is free to acquire and nothing is Paid, but some expire before a visitor is likely to act on it.
- **The curated set repeats across industries.** 48 slots are filled by only 30 distinct listings. Most reused: UK (England and Wales only) Census 2021 - Trial (5 industries); Acorn - Geodemographic Segmentation in the UK (5 industries); Postcode Sector Weather Forecasts (3 industries); Company Data UK (incl. Guernsey) - XL Dataset (3 industries). This is the "why am I being offered the same thing again" problem, and it is content curation work rather than a bug.
- **`is_ready_for_import` is the flag that decides whether a visitor can actually attach a listing**, and it is stricter than it looks. Measured on the London account: of 4,347 visible listings only 671 are importable. Every one of those is also not-by-request. The trap is the middle group - 2,594 listings are NOT by-request and still NOT importable, so they look freely available and cannot be mounted. Checking only region and by-request passes listings a visitor cannot use; that is how five unattachable entries once sat in the curated index undetected. `deploy/verify_context.py --listings` now checks the flag directly, and all 30 distinct curated listings pass it.
- **The agentic marketplace tier stays disabled.** Re-timed 2026-08-24 at **117.1s** for one search - slower than the 70-110s originally measured, and far slower than a visitor walking one stall. It does return better matches (a "poor data quality" problem returned Ataccama Data Quality and Semarchy xDM rather than an industry keyword guess), but it does NOT verify region or `is_ready_for_import`, so its suggestions can be dead ends. Warming does not rescue it: the 117s is inference and tool time, not the ~18s of process startup.

