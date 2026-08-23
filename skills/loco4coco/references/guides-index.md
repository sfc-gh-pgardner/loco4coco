---
name: guides-index
description: "Curated index of Snowflake developer guides, archetype-tagged, for the Loco4CoCo prior-art step. Bundled so it resolves instantly and survives poor venue wifi. Every URL verified HTTP 200 on 2026-08-05. Rebuild with scripts/build_guides_index.py before each event."
---

# Curated developer guides index

**Verified:** 2026-08-05 - all 44 URLs returned HTTP 200 on that date.
**Base:** `https://www.snowflake.com/en/developers/guides/<slug>/`
**Corpus:** harvested 565 of the 653 guides the site reported (86%); the shortfall is landing/industry pages and cards without a parseable heading. The curation below is a deliberate subset, not the whole corpus.

## Why bundled

demolish's prior-art step hands ranked keywords to a human who eyeballs the guides page. That is the right trade for an SE with time. It is the wrong trade for a booth: 653 guides across 55 client-side-paginated pages, a non-technical visitor, and a five-minute clock. So the agent resolves the fork-base itself from this index, and only reaches the network for **feature doc links** via `snowflake_product_docs`.

## Rules for using this index

- Pick the **primary** fork for the resolved archetype. Offer an alternate only if the visitor's Round 2 answers clearly favour it.
- Never invent a slug. If a needed guide is not here, say "no direct guide - build from scratch" and name the features instead. A recorded negative is honest; a fabricated URL is a defect.
- Do not deep-link to sections. Slug-level only, which is what was verified.
- `CoCo` in the notes column means the guide explicitly features Cortex Code or CoWork - prefer these, because the visitor's takeaway is a CoCo prompt.

---

## 1. talk-to-my-data

| Guide | Slug | Notes |
|---|---|---|
| Build Business-Ready Queries with Snowflake Semantic Views | `snowflake-semantic-view-business-ready-queries` | **Primary fork** |
| Build Semantic Views and Connect to Tableau with Snowflake | `snowflake-semantic-view-autopilot` | If they mention BI tools |
| Building AI Applications with Snowflake Cortex: RAG, Text-to-SQL & CoCo | `accelerate-app-dev-coco` | CoCo |
| Getting Started with Snowflake CoCo for Data Analysis | `getting-started-with-coco-for-data-analysis` | CoCo · gentlest start |

## 2. ask-my-documents

| Guide | Slug | Notes |
|---|---|---|
| Build a RAG-based LLM assistant using Streamlit and Cortex Search | `ask-questions-to-your-own-documents-with-snowflake-cortex-search` | **Primary fork** |
| Build a RAG App with Streamlit and Snowflake Cortex | `build-rag-app-with-streamlit-and-snowflake-cortex` | Simpler alternate |
| Multi-Index Cortex Search: Build a Retail Catalog Search App | `multi-index-cortex-search-build-a-retail-catalog-search-app` | Multiple doc sets |
| Getting Started with Snowflake CoWork and Cortex Knowledge Extensions | `getting-started-with-cowork-and-cke` | CoCo |

## 3. extract-from-paperwork

| Guide | Slug | Notes |
|---|---|---|
| Create a Document Processing Pipeline with AI_EXTRACT | `create-a-document-processing-pipeline-with-ai-extract` | **Primary fork** · modern |
| Automating Document Processing Workflows With Document AI | `automating-document-processing-workflows-with-document-ai` | Higher volume |
| Document AI Invoice Reconciliation | `doc-ai-invoice-reconciliation` | If they say invoices |
| Extracting Insights from Unstructured Data with Document AI | `tasty-bytes-extracting-insights-with-docai` | Sample data included |

## 4. triage-and-classify

| Guide | Slug | Notes |
|---|---|---|
| Build a Customer Review Analytics Dashboard with Cortex and Streamlit | `avalanche-customer-review-data-analytics` | **Primary fork** |
| Customer Reviews Analytics using Snowflake Cortex | `customer-reviews-analytics-using-snowflake-cortex` | No-UI alternate |
| Lead Scoring with ML-Powered Classification | `lead-scoring-with-ml-powered-classification` | Scoring/ranking framing |

## 5. an-agent-that-acts

| Guide | Slug | Notes |
|---|---|---|
| Getting Started with Cortex Agents with Snowflake CoCo CLI | `getting-started-with-cortex-agents-with-coco` | **Primary fork** · CoCo |
| Build a Cortex Agent from Scratch with Snowflake | `build-a-cortex-agent-from-scratch-with-snowflake` | Ground-up alternate |
| Build Agent-Powered Workflows Using Cortex AI and Managed MCP Servers | `build-agent-powered-workflows` | Needs external tools |
| Multi-Agent Orchestration in Snowflake CoWork | `multi-agent-orchestration-cowork` | CoCo · ambitious |
| Self-Improving Agents with CoCo | `self-improving-agents-with-coco` | CoCo · advanced |

## 6. predict-what-happens-next

| Guide | Slug | Notes |
|---|---|---|
| Getting Started with Snowflake ML Functions: Anomaly Detection & Forecasting | `ml-forecasting-ad` | **Primary fork** |
| Getting Started with Snowflake ML Forecasting and Classification | `getting-started-with-snowflake-cortex-ml-forecasting-and-classification` | Broader alternate |
| Credit card fraud detection using Snowflake ML | `credit-card-fraud-detection-using-snowflake-ml` | Fraud/risk framing |
| Getting Started with CoCo CLI for Data Science ML | `getting-started-with-coco-cli-for-data-science-ml` | CoCo · technical visitor |

## 7. join-the-silos

| Guide | Slug | Notes |
|---|---|---|
| Create Declarative Data Pipelines with Dynamic Tables | `create-declarative-data-pipelines-with-dynamic-tables` | **Primary fork** |
| Accelerate Data Product Delivery with CoCo | `accelerate-data-product-delivery` | CoCo |
| Deploying Pipelines with Snowflake and dbt labs | `data-engineering-deploying-pipelines-with-snowflake-and-dbt-labs` | If they mention dbt |
| Data Engineering using Snowflake Notebooks | `data-engineering-with-notebooks` | Notebook-led |
| Build an End-to-End Application Using CoCo on Snowflake | `sfguide-build-end-to-end-ai-app-on-snowflake` | CoCo · full stack |

## 8. share-without-copying

| Guide | Slug | Notes |
|---|---|---|
| Intra-Company Data Sharing With The Snowflake Internal Marketplace | `internal-marketplace-intra-org-sharing` | **Primary fork** |
| Sharing Data and AI on the Snowflake Internal Marketplace | `sharing-data-and-ai-on-snowflake-internal-marketplace` | Sharing AI assets too |

## 9. watch-it-live

| Guide | Slug | Notes |
|---|---|---|
| Getting Started with Snowpipe Streaming high-performance architecture and CoCo | `getting-started-with-snowpipe-streaming-v2` | **Primary fork** · CoCo |
| Real-Time Analytics with Kafka, Interactive Tables, and Snowpipe Streaming v2 | `kafka-interactive-tables-streaming` | If they say Kafka |
| Getting Started with Event Tables and Alerts | `alert-on-events` | Alerting-only, lightest |
| Real-Time Streaming with Snowpipe Streaming and Interactive Tables | `interactive-tables-snowpipe-streaming-arcade-lab` | Hands-on lab |

---

## CoCo onboarding (always include one)

Every blueprint names one of these regardless of archetype, so the visitor knows how to start CoCo itself.

| Guide | Slug | Use when |
|---|---|---|
| Get Started with Snowflake CoCo Desktop | `getting-started-with-coco-desktop` | **Default** - most visitors |
| Get Started with Snowflake CoCo CLI | `getting-started-with-coco-cli` | Comfortable in a terminal |
| Snowflake CoCo Foundations | `coco-foundations` | Wants the concepts first |
| Build Your First CoCo Skill | `build-a-coco-skill` | Already an engineer, wants to extend |
| Getting Started with Snowflake CoWork | `getting-started-with-cowork` | Asking/analysing rather than building |

## Redirects resolved during verification

Recorded so a future rebuild does not reintroduce them:

- `cortex-code-foundations` → `coco-foundations`
- `getting-started-with-snowflake-intelligence` → `getting-started-with-cowork`
- `credit-card-fraud-detection-with-snowflake-ml-functions` → `credit-card-fraud-detection-using-snowflake-ml`

## Maintenance

Guides are added constantly, so this index is a snapshot with a shelf life. Rebuild before each event via `scripts/build_guides_index.py`, which re-harvests, re-verifies every URL, and reports additions, removals and new redirects. Never ship an unverified slug.
