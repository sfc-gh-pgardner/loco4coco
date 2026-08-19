# Loco 4 CoCo - the booth decision tree

_Generated from the live `config.json`, `archetypes.md` and `server.py`. Every option below is what a visitor is actually offered. Regenerate with `python3 game/decision_tree.py` after changing config._

## Why this document exists

Five choices decide the whole blueprint. Three of them are precomputed by us and two are decided at runtime, and it matters which is which - only the precomputed ones can be improved by editing config.

| Step | What the visitor does | Where the options come from | Tunable? |
|---|---|---|---|
| 1. The letter | Types name, company, industry, **and the problem in two sentences** | Industry list in `config.industries` | Yes - the list |
| 2. The library | Ticks data they hold, then taps the platforms it sits on | `industries.<key>.data_sources` + `config.platforms` | **Yes - fully precomputed** |
| 3. The marketplace | Ticks data to join | `industries.<key>.marketplace` as the fallback, but **live listings first** | Partly - see below |
| 4. The workshop | Types one line describing the MVP | Free text | No - but the archetype it maps to is |
| 5. The postbox | Posts it | - | - |

The two runtime decisions are: which live Marketplace listings match the industry keywords, and which of the ten archetypes the model picks from the visitor's one-line description. Everything else is ours to set.

## The tree, top to bottom

```
LETTER
  industry  ->  one of 8
  problem   ->  free text, 400 chars, threaded into every later prompt
        |
LIBRARY   (precomputed per industry)
  data held ->  6 options per industry + "something else"
  platform  ->  9 universal chips -> integration path in the blueprint
        |
MARKETPLACE
  live listings matched on industry keywords  (min 3 results)
  falls back to 5-5 curated options per industry
        |
WORKSHOP
  one line  ->  model picks 1 of 10 archetypes
             ->  features + first step come from archetypes.md, no inference
        |
POSTBOX   ->  blueprint (.docx today, HTML alongside it) + QR + email
```

## Per industry

For each industry: what the library offers, what the marketplace offers as the curated fallback, and the keywords used to find live listings. The keywords are the lever on live results - a thin keyword list is why an industry falls back to the curated list.

### Healthcare & Life Sciences

`healthcare` - 6 data sources, 5 curated joins, 16 live-search keywords, 0 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Patient records | Structured clinical records in a PAS or EPR system |
| Clinical notes & letters | Free text - discharge summaries, referrals, correspondence |
| Referral & waiting list data | Pathways, breaches, appointment scheduling |
| Clinical trial data | Protocols, recruitment, outcomes |
| Imaging & diagnostics | Scan metadata and reports |
| Estates & operations | Beds, theatres, staffing rotas, supplies |

**Marketplace - curated joins (the fallback when live search is thin)**

| Option | Note shown under it |
|---|---|
| Population & demographics | Census and small-area statistics to risk-adjust by catchment |
| Deprivation & social determinants | Index of Multiple Deprivation to explain outcome variation |
| Geospatial & travel time | Boundaries and drive times for access and coverage analysis |
| Weather & air quality | Correlate respiratory admissions with pollution and cold snaps |
| Drug & medical reference data | Coding systems and terminologies for normalising records |

**Live-search keywords** (16): clinical, patient, nhs, health, disease, epidemiolog, population health, prescrib, wellbeing, mortality, hospital, medic, pharma, drug, life science, biotech

### Financial Services

`financial` - 6 data sources, 5 curated joins, 12 live-search keywords, 0 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Transaction history | Card, payment and account movement |
| Customer & account master | KYC records, product holdings, segments |
| Positions & trades | Holdings, orders, execution history |
| Risk & capital models | Exposures, limits, stress test inputs |
| Customer communications | Call transcripts, complaints, chat logs |
| Regulatory reporting | Submissions and the reconciliations behind them |

**Marketplace - curated joins (the fallback when live search is thin)**

| Option | Note shown under it |
|---|---|
| Market & pricing data | Prices and reference data to value positions |
| Company financials & firmographics | Counterparty and SME lending enrichment |
| Macroeconomic indicators | Rates, inflation and employment for scenario modelling |
| ESG & climate risk | Physical and transition risk against a loan book |
| Sanctions & adverse media | Screening and enhanced due diligence signals |

**Live-search keywords** (12): foreign exchange, inflation, credit, risk, equity, market, macro, payments, fraud, interest rate, economic, commodit

### Retail & Consumer Goods

`retail` - 6 data sources, 5 curated joins, 11 live-search keywords, 2 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Sales & till transactions | Basket-level sales by store and channel |
| Inventory & stock positions | Availability, shrink, replenishment |
| Loyalty & customer data | Membership, spend history, segments |
| Web & app clickstream | Browse, search and cart behaviour |
| Supplier & logistics data | Purchase orders, lead times, delivery performance |
| Reviews & customer service | Free text feedback, returns reasons, contact logs |

**Marketplace - curated joins (the fallback when live search is thin)**

| Option | Note shown under it |
|---|---|
| Weather observations & forecast | The single biggest driver of short-term demand |
| Population & demographics | Catchment profiling for store and range decisions |
| Mobility & footfall | High street and retail park movement patterns |
| Competitor & commodity prices | Price positioning and input cost exposure |
| Holidays & events calendars | Bank holidays and fixtures that move demand |

**Live-search keywords** (11): consumer, footfall, spend, household income, demographic, acorn, basket, weather, postcode, segmentation, price

**Pinned listings**: GZTDZJKVCY, GZSVZAJO3

### Public Sector & Government

`public` - 6 data sources, 5 curated joins, 11 live-search keywords, 3 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Case management records | Casework across service lines |
| Policy & guidance documents | Years of PDFs, circulars and statutory guidance |
| Citizen contact & correspondence | Calls, emails, webforms, complaints |
| Assets & estates | Property, highways, fleet, maintenance |
| Finance & procurement | Budgets, spend over threshold, contracts |
| Performance & statutory returns | KPIs and central government reporting |

**Marketplace - curated joins (the fallback when live search is thin)**

| Option | Note shown under it |
|---|---|
| Census & population statistics | Small-area demographics for needs assessment |
| Deprivation indices | Target interventions where need is greatest |
| Boundaries & geospatial reference | Wards, LSOAs, postcodes and lookups |
| Weather & flood risk | Resilience planning and winter pressures |
| Transport & accessibility | Public transport access to services |

**Live-search keywords** (11): census, postcode, deprivation, boundary, population, geospatial, planning, crime, education, transport, uprn

**Pinned listings**: GZTDZJKVCU, GZTDZJKVCY, GZSVZAJO3

### Manufacturing & Industrial

`manufacturing` - 6 data sources, 5 curated joins, 20 live-search keywords, 0 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Machine & sensor telemetry | High frequency readings off the line |
| Quality & defect records | Inspection results, scrap, rework |
| Maintenance logs | Work orders and engineer free text |
| ERP & production planning | Orders, BOMs, schedules, yields |
| Supplier & inbound logistics | Component lead times and quality by supplier |
| Energy consumption | Meter data by line and site |

**Marketplace - curated joins (the fallback when live search is thin)**

| Option | Note shown under it |
|---|---|
| Commodity & input prices | Raw material cost exposure |
| Weather observations | Ambient conditions against yield and energy use |
| Freight & shipping data | Port congestion and route disruption |
| Supplier firmographics & risk | Financial health of the supply base |
| Emissions & ESG factors | Scope 3 reporting and carbon intensity |

**Live-search keywords** (20): supply chain, logistics, commodit, shipping, freight, industrial, manufactur, materials, energy price, trade, tariff, production, inventory, supplier, port, vessel, steel, metal, company data, economic

### Energy & Utilities

`energy` - 6 data sources, 5 curated joins, 11 live-search keywords, 3 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Smart meter readings | Interval consumption at premise level |
| Network & asset data | Substations, pipes, cables, condition |
| Outage & fault records | Interruptions, causes, restoration times |
| Generation & dispatch | Output, availability, curtailment |
| Customer & billing | Accounts, tariffs, arrears, vulnerability flags |
| Field engineer reports | Free text inspection and repair notes |

**Marketplace - curated joins (the fallback when live search is thin)**

| Option | Note shown under it |
|---|---|
| Weather & forecast data | The primary driver of both demand and renewable output |
| Energy market prices | Wholesale price exposure and settlement |
| Geospatial & terrain | Network planning and vegetation risk |
| Population & property data | Premise characteristics for demand modelling |
| Climate projections | Long-run asset resilience planning |

**Live-search keywords** (11): weather, climate, emission, carbon, grid, renewable, solar, wind, temperature, energy, net zero

**Pinned listings**: GZTDZJKVCM, GZTDZJKVCU, GZTDZJKVCY

### Media, Telco & Entertainment

`media` - 6 data sources, 5 curated joins, 10 live-search keywords, 0 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Viewing & listening events | Play, pause, completion by title and device |
| Subscriber & account data | Plans, churn, lifetime value |
| Content catalogue & metadata | Titles, rights, genres, availability windows |
| Network performance | Throughput, latency, coverage, faults |
| Advertising & campaign data | Impressions, fill rate, yield |
| Customer support interactions | Call transcripts and chat logs |

**Marketplace - curated joins (the fallback when live search is thin)**

| Option | Note shown under it |
|---|---|
| Population & demographics | Audience profiling and coverage gaps |
| Mobility & location | Where demand sits against network build |
| Sports & events calendars | Fixtures that drive traffic and churn |
| Social & sentiment signals | Title buzz ahead of release |
| Weather observations | Weather against viewing and network load |

**Live-search keywords** (10): audience, media, broadband, mobile, advertising, viewership, telco, subscriber, content, social

### Something else

`other` - 6 data sources, 5 curated joins, 6 live-search keywords, 1 pinned listings

**Library - data they already hold**

| Option | Note shown under it |
|---|---|
| Core operational records | Whatever your main system of record holds |
| Documents & PDFs | Years of unstructured files nobody can query |
| Customer or member data | Who you serve and what they have done |
| Finance & billing | Revenue, spend, invoices |
| Emails, calls & tickets | Free text interactions |
| Device or sensor data | Anything machine-generated and high volume |

**Marketplace - curated joins (the fallback when live search is thin)**

| Option | Note shown under it |
|---|---|
| Population & demographics | Context for wherever you operate |
| Weather observations | Surprisingly often the missing variable |
| Company & firmographic data | Enrich anything B2B |
| Geospatial reference | Boundaries, postcodes and lookups |
| Economic indicators | Trend against the wider economy |

**Live-search keywords** (6): weather, census, demographic, postcode, economic, geospatial

**Pinned listings**: GZTDZJKVCY

## The platform question, and what it produces

Asked once in the library, one tap, universal across industries. Each chip writes a concrete route into the blueprint, so this is the section that turns "we have the data somewhere" into a first task.

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

## The ten archetypes

The workshop is free text, but it resolves to exactly one of these. Features and the first step are precomputed, so they are instant and always correct; only the summary and the considerations need the model.

| Archetype | Features | Considerations in pool |
|---|---|---|
| talk-to-my-data | Cortex Analyst, Semantic Views, Snowflake Intelligence | 5 |
| ask-my-documents | Cortex Search, AI_PARSE_DOCUMENT, Cortex Agents | 5 |
| extract-from-paperwork | AI_EXTRACT, AI_PARSE_DOCUMENT, Dynamic Tables | 5 |
| triage-and-classify | AI_CLASSIFY, Dynamic Tables, Streams | 5 |
| an-agent-that-acts | Cortex Agents, Snowflake Intelligence, Semantic Views | 5 |
| dashboard-that-explains-itself | Streamlit in Snowflake, Cortex Analyst, Semantic Views | 5 |
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
- **dashboard-that-explains-itself** - Pick the one decision this dashboard should change, and design backwards from it.
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

- **No industry biases the archetype choice.** A hospital and a bank get the same ten archetypes with the same weighting. A per-industry ordering, or two or three likely archetypes per industry, would make the forge both faster and more plausible.
- **The data held does not narrow the marketplace suggestion.** Someone who ticked "clinical notes" is offered the same joins as someone who ticked "estates and operations". A held-to-join mapping is the highest-value precompute still missing.

