---
name: poc-archetypes
description: "The ten POC shapes Loco4CoCo routes a visitor to. Each carries a plain-English visitor framing, the Snowflake features it uses, the guide to fork, doc topics, and a kick-off prompt skeleton. This is the spine of the quiz — Round 1 and Round 2 answers resolve to exactly one archetype."
---

# POC archetypes

Ten shapes. Every visitor leaves mapped to exactly one, chosen by their Round 1 and Round 2 answers. The archetype determines the guide to fork, the features named in the blueprint, and the kick-off prompt.

## How resolution works

**Q2 (the pain) wins by default. Q3 (the dream) shapes the deliverable, it does not usually replace the archetype.**

This precedence is deliberate and was corrected after dry-running: treating Q3 as a blunt override throws away the pain signal, which is the more reliable of the two. A visitor who says "too much comes in to sort by hand" and then "show me a picture I can act on" wants a *triage view* — they do not want the classification silently dropped in favour of a generic dashboard. The pain is what they came to the stand about; the dream is how they picture the fix.

Apply in this order:

1. **Resolve from Q2.** It maps near one-to-one onto an archetype.
2. **Check whether that archetype already delivers the Q3 dream.** Usually it does — most primary forks already include a UI, and several already answer in plain English. If so, **keep the Q2 archetype** and let Q3 choose the fork variant and shape the deliverable sentence.
3. **Only override when genuinely incompatible** — when the Q2 archetype cannot produce the Q3 dream at all. In practice this is narrow:

| Q2 archetype | Q3 answer | Verdict |
|---|---|---|
| any | "Do the whole task, not just tell me about it" | **Override** to `an-agent-that-acts` — no other archetype acts |
| any | "Let me share it safely with others" | **Override** to `share-without-copying` — a distinct outcome |
| `talk-to-my-data` / `ask-my-documents` | "Warn me before it goes wrong" | **Override** to `predict-what-happens-next` — asking is not forecasting |
| `triage-and-classify` | "Show me a picture I can act on" | **Keep** — its primary fork is already a dashboard |
| `join-the-silos` | "Answer questions in plain English" | **Keep** — unify first; note the semantic view as the obvious phase two |
| `watch-it-live` | "Warn me before it goes wrong" | **Keep** — alerting is already the point |
| `extract-from-paperwork` | "Show me a picture I can act on" | **Keep** — add a summary view to the deliverable |

4. **Round 2 tunes, never re-routes.** Data on hand and audience set scope, choose between the primary and an alternate fork, and feed the readiness score.

When two archetypes remain genuinely tied, prefer the one whose **primary feature matches the data they actually have**. A POC they can start beats a more impressive one they cannot.

When you keep the Q2 archetype but Q3 pointed elsewhere, **say so in the reveal** — "we'll get you the picture too, but the win is sorting it first". This shows you listened rather than silently discarding their answer.

Never show the archetype ID to the visitor. Show the friendly name and their own words back.

---

## 1. talk-to-my-data
**ID** `talk-to-my-data` · **Friendly** "Just ask your data"

- **Visitor pain:** "I wait days for someone to run a query for me." / "I can't write SQL." / "Every question becomes a ticket."
- **What gets built:** a semantic view over their tables, queried in plain English.
- **Features:** Cortex Analyst, semantic views, Snowflake CoWork
- **Doc topics:** `cortex analyst semantic view`, `semantic views overview`
- **Fork:** `snowflake-semantic-view-business-ready-queries`
- **Needs from them:** at least one table with a few numeric columns and a date.
- **Prompt skeleton:** build a semantic view over `<their tables>` covering `<their metrics>`, then ask it `<their question>`.

## 2. ask-my-documents
**ID** `ask-my-documents` · **Friendly** "Ask your documents"

- **Visitor pain:** "The answer is in a 200-page PDF nobody reads." / "Our policies/guidance are unsearchable."
- **What gets built:** a RAG assistant over their documents with a chat front end.
- **Features:** Cortex Search, AI_PARSE_DOCUMENT, Streamlit
- **Doc topics:** `cortex search overview`, `ai_parse_document`
- **Fork:** `ask-questions-to-your-own-documents-with-snowflake-cortex-search`
- **Needs from them:** a folder of PDFs, Word docs or web pages.
- **Prompt skeleton:** load `<their docs>` into a Cortex Search service and give me a Streamlit chat app that answers `<their question>` with citations.

## 3. extract-from-paperwork
**ID** `extract-from-paperwork` · **Friendly** "Stop retyping paperwork"

- **Visitor pain:** "Someone retypes invoices/forms/claims into a spreadsheet." / "We key in the same fields all day."
- **What gets built:** a pipeline turning a stage of documents into a clean table.
- **Features:** AI_EXTRACT, Document AI, dynamic tables
- **Doc topics:** `ai_extract`, `document ai`
- **Fork:** `create-a-document-processing-pipeline-with-ai-extract`
- **Needs from them:** a sample of the form, ideally 10+ of the same layout.
- **Prompt skeleton:** extract `<their fields>` from the documents in my stage into a table, and keep it current as new files land.

## 4. triage-and-classify
**ID** `triage-and-classify` · **Friendly** "Sort the inbound"

- **Visitor pain:** "Too much comes in to sort by hand." / "We read every complaint to find the urgent ones."
- **What gets built:** classification and sentiment over a backlog, with a triage view.
- **Features:** AI_CLASSIFY, AI_SENTIMENT, AI_FILTER
- **Doc topics:** `ai_classify`, `ai_sentiment`
- **Fork:** `avalanche-customer-review-data-analytics`
- **Needs from them:** a table with a free-text column.
- **Prompt skeleton:** classify `<their text column>` into `<their categories>`, score sentiment, and surface the ones needing attention first.

## 5. an-agent-that-acts
**ID** `an-agent-that-acts` · **Friendly** "An agent that does the work"

- **Visitor pain:** "I don't want an answer, I want the task done." / "It's six systems and a checklist every time."
- **What gets built:** a Cortex Agent with tools that completes a multi-step task.
- **Features:** Cortex Agents, Cortex Analyst, Cortex Search, MCP
- **Doc topics:** `cortex agents`, `snowflake mcp server`
- **Fork:** `getting-started-with-cortex-agents-with-coco`
- **Needs from them:** a described process with a clear trigger and outcome.
- **Prompt skeleton:** build a Cortex Agent that, given `<their trigger>`, does `<their steps>` and returns `<their outcome>`.

## 6. predict-what-happens-next
**ID** `predict-what-happens-next` · **Friendly** "See it coming"

- **Visitor pain:** "We react instead of planning." / "We find out after it's gone wrong."
- **What gets built:** a forecast or anomaly detector on their history.
- **Features:** ML forecasting, anomaly detection, Snowflake ML
- **Doc topics:** `ml functions forecasting`, `anomaly detection`
- **Fork:** `ml-forecasting-ad`
- **Needs from them:** a time series — a date column and a value column, ideally 12+ months.
- **Prompt skeleton:** forecast `<their measure>` for the next `<horizon>` from `<their table>` and flag anything anomalous.

## 7. join-the-silos
**ID** `join-the-silos` · **Friendly** "Join up the silos"

- **Visitor pain:** "Our data is in five systems." / "Someone rebuilds the same spreadsheet every month."
- **What gets built:** an incremental pipeline unifying sources into one modelled table.
- **Features:** dynamic tables, Snowflake Notebooks, ingestion
- **Doc topics:** `dynamic tables`, `data loading overview`
- **Fork:** `create-declarative-data-pipelines-with-dynamic-tables`
- **Needs from them:** two or more sources that share a key.
- **Prompt skeleton:** combine `<their sources>` into one table keyed on `<their key>`, refreshing automatically.

## 8. share-without-copying
**ID** `share-without-copying` · **Friendly** "Share without sending files"

- **Visitor pain:** "Partners email us CSVs." / "We can't share without copying data out."
- **What gets built:** a governed live share or internal marketplace listing.
- **Features:** Secure Data Sharing, internal marketplace, listings
- **Doc topics:** `secure data sharing`, `internal marketplace`
- **Fork:** `internal-marketplace-intra-org-sharing`
- **Needs from them:** a dataset and someone to share it with.
- **Prompt skeleton:** publish `<their dataset>` as a governed share for `<their audience>` without copying it.

## 9. watch-it-live
**ID** `watch-it-live` · **Friendly** "Watch it live"

- **Visitor pain:** "We find out too late." / "Reporting is yesterday's news."
- **What gets built:** a streaming feed with alerting on a threshold.
- **Features:** Snowpipe Streaming, alerts, event tables
- **Doc topics:** `snowpipe streaming`, `alerts`
- **Fork:** `getting-started-with-snowpipe-streaming-v2`
- **Needs from them:** a source that produces events continuously.
- **Prompt skeleton:** stream `<their source>` into Snowflake and alert me when `<their condition>`.

---

## Readiness score (out of 5)

Award one point each. Show the score, and name the weakest point as "the thing to firm up" — this is the diagnostic that makes the blueprint useful rather than flattering.

**Score strictly.** Dry-running three realistic personas against a looser rubric produced two 5s and a 3, which is useless: if almost everyone scores full marks the number carries no information, the visitor gets no next step, and the SE gets no opening. Typical should be **3**. A 5 should be rare and mean the person could genuinely start on Monday. When in doubt, withhold the point — an honest 3 with a clear "firm this up" beats a flattering 5.

| Point | Award only when | Do NOT award when |
|---|---|---|
| Data on hand | They named data they can **access themselves today**, without raising a request | "Not sure yet", or it needs someone else's permission or an export |
| Clear user | They named a **specific** person or team who feels the pain | "The whole organisation", "everyone", or the user is themselves in the abstract |
| Measurable outcome | They can point to a number that **exists today** and would move — a volume, a delay, a cost | The benefit is real but unquantified ("it'd save loads of time") |
| Feature fit | The archetype's primary feature works on the **shape** of data they described | They have tables but the archetype needs documents, or vice versa |
| Realistic scope | Achievable on a free trial in about a fortnight | Multiple source systems, org-wide rollout, or anything needing procurement |

Expected distribution across a booth day: mostly 2–3, some 4, a 5 occasionally. If a session is producing 5s routinely, the scoring has drifted — re-read the "do NOT award" column.

A low score is not a failure and must never be presented as one. Frame it as "here's what to nail down first" — that framing is the honest, useful version, it gives the visitor a genuine next step, and it is the SE's opening for a follow-up conversation.
