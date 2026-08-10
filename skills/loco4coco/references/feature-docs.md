---
name: feature-docs
description: "Closed list of Snowflake features the Workshop may name, each with a verified docs.snowflake.com URL. Bundled so blueprints resolve instantly and cannot contain a fabricated link. Rebuild with scripts/build_feature_docs.py before each event."
---

# Feature documentation map

**Verified:** 2026-08-06 — every URL returned HTTP 200 on that date.
**Count:** 53 features.

## Why a closed list

Features used to arrive as free text from the model, so there was nothing reliable to link. The Workshop prompt now selects **only** from the names below, which means every feature in a blueprint has a working link by construction. A name outside this list is dropped rather than rendered bare — silently omitting one is better than shipping a guess.

Match on the exact name in the first column.

## Cortex AI services

| Feature | Documentation |
|---|---|
| Cortex Agents | https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents |
| Cortex Analyst | https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst |
| Cortex Fine-tuning | https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-finetuning |
| Cortex Playground | https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-playground |
| Cortex Search | https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview |
| Document AI | https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-documents |
| Snowflake Intelligence | https://docs.snowflake.com/en/user-guide/snowflake-cortex/snowflake-cowork |

## AISQL functions

| Feature | Documentation |
|---|---|
| AISQL functions | https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql |
| AI_AGG | https://docs.snowflake.com/en/sql-reference/functions/ai_agg |
| AI_CLASSIFY | https://docs.snowflake.com/en/sql-reference/functions/ai_classify |
| AI_COMPLETE | https://docs.snowflake.com/en/sql-reference/functions/ai_complete |
| AI_EMBED | https://docs.snowflake.com/en/sql-reference/functions/ai_embed |
| AI_EXTRACT | https://docs.snowflake.com/en/sql-reference/functions/ai_extract |
| AI_FILTER | https://docs.snowflake.com/en/sql-reference/functions/ai_filter |
| AI_PARSE_DOCUMENT | https://docs.snowflake.com/en/sql-reference/functions/ai_parse_document |
| AI_REDACT | https://docs.snowflake.com/en/sql-reference/functions/ai_redact |
| AI_SENTIMENT | https://docs.snowflake.com/en/sql-reference/functions/ai_sentiment |
| AI_SIMILARITY | https://docs.snowflake.com/en/sql-reference/functions/ai_similarity |
| AI_SUMMARIZE_AGG | https://docs.snowflake.com/en/sql-reference/functions/ai_summarize_agg |
| AI_TRANSCRIBE | https://docs.snowflake.com/en/sql-reference/functions/ai_transcribe |
| AI_TRANSLATE | https://docs.snowflake.com/en/sql-reference/functions/ai_translate |

## Modelling and semantics

| Feature | Documentation |
|---|---|
| Dynamic Tables | https://docs.snowflake.com/en/user-guide/dynamic-tables/overview |
| External Tables | https://docs.snowflake.com/en/user-guide/tables-external-intro |
| Hybrid Tables | https://docs.snowflake.com/en/user-guide/tables-hybrid |
| Iceberg Tables | https://docs.snowflake.com/en/user-guide/tables-iceberg |
| Materialized Views | https://docs.snowflake.com/en/user-guide/views-materialized |
| Semantic Views | https://docs.snowflake.com/en/user-guide/views-semantic/overview |

## Apps and interfaces

| Feature | Documentation |
|---|---|
| Snowflake Notebooks | https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks |
| Snowpark Python | https://docs.snowflake.com/en/developer-guide/snowpark/python/index |
| Streamlit in Snowflake | https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit |

## Pipelines and ingestion

| Feature | Documentation |
|---|---|
| Alerts | https://docs.snowflake.com/en/user-guide/alerts |
| Openflow | https://docs.snowflake.com/en/user-guide/data-integration/openflow/about |
| Snowpipe | https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro |
| Snowpipe Streaming | https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-overview |
| Streams | https://docs.snowflake.com/en/user-guide/streams-intro |
| Tasks | https://docs.snowflake.com/en/user-guide/tasks-intro |

## Machine learning

| Feature | Documentation |
|---|---|
| ML Anomaly Detection | https://docs.snowflake.com/en/user-guide/ml-functions/anomaly-detection |
| ML Classification | https://docs.snowflake.com/en/user-guide/ml-functions/classification |
| ML Forecasting | https://docs.snowflake.com/en/user-guide/ml-functions/forecasting |
| ML Top Insights | https://docs.snowflake.com/en/user-guide/ml-functions/top-insights |
| Snowflake Feature Store | https://docs.snowflake.com/en/developer-guide/snowflake-ml/feature-store/overview |
| Snowflake Model Registry | https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/overview |

## Sharing and collaboration

| Feature | Documentation |
|---|---|
| Data Clean Rooms | https://docs.snowflake.com/en/user-guide/cleanrooms/overview |
| Secure Data Sharing | https://docs.snowflake.com/en/user-guide/data-sharing-intro |
| Snowflake Marketplace | https://docs.snowflake.com/en/collaboration/collaboration-listings-about |

## Governance and quality

| Feature | Documentation |
|---|---|
| Access History | https://docs.snowflake.com/en/user-guide/access-history |
| Data Classification | https://docs.snowflake.com/en/user-guide/classify-intro |
| Data Metric Functions | https://docs.snowflake.com/en/user-guide/data-quality-intro |
| Masking Policies | https://docs.snowflake.com/en/user-guide/security-column-ddm-intro |
| Object Tagging | https://docs.snowflake.com/en/user-guide/object-tagging/introduction |
| Row Access Policies | https://docs.snowflake.com/en/user-guide/security-row-intro |
| Search Optimization Service | https://docs.snowflake.com/en/user-guide/search-optimization-service |
| Time Travel | https://docs.snowflake.com/en/user-guide/data-time-travel |
