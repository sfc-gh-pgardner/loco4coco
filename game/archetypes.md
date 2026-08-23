# Archetype catalogue

Precomputed per-archetype defaults, so the forge's blocking model call only has
to choose an archetype and speak. Everything in here is available instantly and
needs no inference.

Two jobs:

1. **Defaults** — features, and a concrete first step. If the background stage
   fails entirely, a blueprint assembled from these alone is still complete and
   correct, just less tailored.
2. **A considerations pool** — numbered candidate considerations per archetype.
   The background stage returns *indices* rather than four sentences of prose,
   which is where most of the output tokens went.

Feature names must appear verbatim in `feature-docs.md`, or they are dropped when
the blueprint is linked. Keep them in sync.

## talk-to-my-data

| field | value |
|---|---|
| features | Cortex Analyst, Semantic Views, Snowflake Intelligence |
| first_step | Write down the three questions people ask most, then model just the tables those need. |

1. Plain-English questions only work if your column names mean something - budget time for a semantic layer.
2. Decide who is allowed to see which rows before you open it up, not after.
3. Agree what each metric means with the team who owns it, or two people will get two answers.
4. Start with one subject area. A semantic view over everything is a six month project, not a POC.
5. Check whether your numbers are already reconciled somewhere - if not, the POC will surface the discrepancy.

## ask-my-documents

| field | value |
|---|---|
| features | Cortex Search, AI_PARSE_DOCUMENT, Cortex Agents |
| first_step | Put fifty representative documents on a stage and see what the parser returns before building anything. |

1. Scanned documents and clean PDFs behave very differently - check which you actually have.
2. Decide what a good answer looks like, and keep twenty questions aside to test against.
3. Citations matter more than fluency here. Insist the answer points at the source page.
4. Work out who is allowed to see which documents, because search will happily cross that line.
5. Old versions of the same document will contradict each other. Decide which one wins.

## extract-from-paperwork

| field | value |
|---|---|
| features | AI_EXTRACT, AI_PARSE_DOCUMENT, Dynamic Tables |
| first_step | List the fields you actually need, then test extraction on your ugliest ten documents rather than your cleanest. |

1. Define the fields precisely, including what an empty one means.
2. Decide your accuracy bar per field - a wrong total is not the same as a wrong date.
3. Plan the human check for low-confidence extractions before you go near production.
4. Layout drift breaks extraction quietly. Keep a sample set to re-test against.
5. Work out where the extracted data lands, and what happens when the same document arrives twice.

## triage-and-classify

| field | value |
|---|---|
| features | AI_CLASSIFY, Dynamic Tables, Streams |
| first_step | Agree the categories with the people who act on them, then hand-label two hundred examples as your yardstick. |

1. If two of your categories overlap, the model will look wrong when it is not. Tighten them first.
2. Decide what happens to the "not sure" bucket, because there will be one.
3. Measure against hand-labelled examples, not against a feeling.
4. Volumes spike. Check the cost at peak, not at average.
5. Someone needs to own the categories over time, or they drift out of date.

## an-agent-that-acts

| field | value |
|---|---|
| features | Cortex Agents, Snowflake Intelligence, Semantic Views |
| first_step | Pick one action worth automating, and write down exactly what the agent must never do. |

1. Draw the line between what it can do alone and what needs a human to approve.
2. Log every action it takes. You will need to explain one of them.
3. Give it the narrowest permissions that work, then stop.
4. Decide how it fails safely when a downstream system is down.
5. Start read-only. Earn the write.

## predict-what-happens-next

| field | value |
|---|---|
| features | ML Forecasting, ML Anomaly Detection, Snowflake Notebooks |
| first_step | Check you have enough history for the thing you want to predict before modelling anything. |

1. Forecasting needs history. Confirm how far back your data genuinely goes.
2. Decide what accuracy is good enough to act on, in the units of the business.
3. Work out what you would do differently if the prediction were right. If nothing, pick another target.
4. Watch for gaps and outliers - a pandemic, a system migration, a bad month of collection.
5. Plan how you will know when the model has gone stale.

## join-the-silos

| field | value |
|---|---|
| features | Dynamic Tables, Snowflake Marketplace, Semantic Views |
| first_step | Find the one key that links your two most important systems, and check how often it is missing. |

1. Agree the join key early. Missing or mismatched keys are where these projects die.
2. Decide which system wins when two disagree about the same record.
3. Different systems mean different update frequencies. Decide what "current" means.
4. Keep the raw data alongside the joined view, so you can prove where a number came from.
5. Check for duplicate records before you join, not after the totals look wrong.

## share-without-copying

| field | value |
|---|---|
| features | Secure Data Sharing, Snowflake Marketplace, Dynamic Tables |
| first_step | Pick one dataset and one partner, and write down exactly which columns they may see. |

1. Decide precisely which columns and rows leave your account.
2. Agree who is accountable for the data once it is shared.
3. Mask or aggregate anything personal before it goes out, not as a follow-up.
4. Sharing is live, so a schema change on your side is their outage. Version it.
5. Work out how you would revoke access quickly if you needed to.

## watch-it-live

| field | value |
|---|---|
| features | Snowpipe Streaming, Dynamic Tables, Streams |
| first_step | Define the one event worth reacting to, and how quickly someone must know about it. |

1. Be honest about how fresh the data needs to be - minutes is far cheaper than seconds.
2. Decide who gets alerted, and what they are expected to do.
3. Late and out-of-order events will arrive. Decide how they are handled.
4. Set the alert threshold carefully. An ignored alert is worse than none.
5. Check the cost of always-on ingestion against the value of the faster answer.
