---
name: prompt-builder
description: "How to compose the kick-off prompt the visitor pastes into CoCo on their free trial. This is the payload of the whole activation — the one artefact that converts a booth conversation into a build. Structure, rules, worked examples, and the anti-patterns that make a prompt fail on first contact."
---

# The kick-off prompt

Everything else in the blueprint is context. **This is the payload.** If the visitor pastes one thing into CoCo in a fortnight's time, it is this, and it has to work on first contact in an account we have never seen.

## Design constraints

The prompt runs in conditions we cannot inspect:

- A **fresh free-trial account** — no data loaded, no warehouses beyond the default, no schemas.
- **Weeks later**, with the booth conversation forgotten.
- Possibly by someone who has **never used CoCo**.
- Against data we have never seen and whose column names we do not know.

So the prompt must be self-contained, must state its own assumptions, and must **tell CoCo to ask before guessing** rather than inventing a schema. A prompt that hallucinates table names fails on line one and the visitor concludes the product does not work.

## Structure

Six parts, in this order. Aim for 150–250 words: long enough to carry intent, short enough to read on a phone.

```
1. ROLE + GOAL      one sentence: who they are, what they want to end up with
2. THE DATA         what they said they have, and an explicit instruction to
                    inspect it and ask rather than assume
3. BUILD THIS       the concrete deliverable, named features
4. START FROM       the guide to fork, by full URL
5. CONSTRAINTS      free trial, small warehouse, suspend when idle, UK English
6. FIRST STEP       one small, verifiable action to take before building
```

Part 6 matters more than it looks. A prompt that says "build me the whole thing" gets a wall of output the visitor cannot verify. A prompt that starts with "first, show me what's in the data and confirm the plan" earns trust and catches wrong assumptions before they compound.

## Rules

- **Second person, imperative.** "Build me…", not "The user would like…".
- **Name real Snowflake features** from the archetype. Not "AI" — `Cortex Search`, `AI_EXTRACT`, `dynamic tables`.
- **Never invent identifiers.** No fabricated database, schema, table or column names. Refer to their data descriptively and instruct CoCo to inspect it.
- **Include the guide URL in full**, from `guides-index.md`. Never a slug alone, never a guessed URL.
- **Never assume data exists.** If Round 2 said "not sure yet", the prompt must open by generating or loading sample data.
- **One deliverable.** A POC that does one thing well beats three half-things.
- **Include the cost line.** It builds trust and is genuinely correct practice.
- **No placeholders in the delivered prompt.** Every `{...}` must be resolved. A blueprint containing `{their_metric}` is a defect.

## Template

```
I'm a {role} at a {sector} organisation and I want to build {poc_name}.

MY DATA
{data_description}. Before you build anything, inspect what's actually there
and tell me what you found — don't assume table or column names, and ask me
if something's ambiguous.

BUILD THIS
{deliverable_sentence}. Use {feature_list}.

START FROM THIS GUIDE
{guide_title}
{guide_url}
Follow its structure but adapt it to my data rather than its sample data.

CONSTRAINTS
This is a Snowflake free trial, so keep it cheap: an X-Small warehouse with
AUTO_SUSPEND set to 60 seconds, and tell me before running anything expensive.
Use UK English in any text you generate.

FIRST STEP
Don't build it all at once. Start by {first_step}, show me the result, and
confirm the plan with me before going further.
```

## Worked example — `ask-my-documents`

Visitor: Sarah, Information Governance Officer, public sector. Pain: "the answer's buried in documents nobody reads." Data: a pile of documents. Audience: a department.

```
I'm an Information Governance Officer at a public sector organisation and I
want to build Policy Answers — a way for my team to ask questions of our
policy documents and get answers with citations.

MY DATA
I have a collection of policy documents as PDFs. Before you build anything,
help me load a few into a stage, inspect what's actually in them, and tell me
what you found — don't assume a structure, and ask me if something's ambiguous.

BUILD THIS
A chat app where someone types a question in plain English and gets an answer
with a citation showing which document and section it came from. Use
AI_PARSE_DOCUMENT to read the PDFs, Cortex Search to index them, and Streamlit
in Snowflake for the interface.

START FROM THIS GUIDE
Build a RAG-based LLM assistant using Streamlit and Snowflake Cortex Search
https://www.snowflake.com/en/developers/guides/ask-questions-to-your-own-documents-with-snowflake-cortex-search/
Follow its structure but adapt it to my documents rather than its sample data.

CONSTRAINTS
This is a Snowflake free trial, so keep it cheap: an X-Small warehouse with
AUTO_SUSPEND set to 60 seconds, and tell me before running anything expensive.
Use UK English in any text you generate.

FIRST STEP
Don't build it all at once. Start by parsing a single PDF and showing me the
extracted text so I can check the quality, then confirm the plan with me
before indexing the rest.
```

## Worked example — no data yet

When `R2.Q1` was "Honestly, not sure yet", the prompt must not pretend otherwise:

```
MY DATA
I don't have a dataset ready yet. Start by creating a small, realistic sample
table I can experiment with — about 200 rows of {domain} data — and show it to
me so I can tell you how it differs from the real thing.
```

Then part 6 becomes: *"Start by building it end to end on that sample, so I can see the shape of it before I bring real data."*

This is honest and it is the version most likely to succeed, because a POC on sample data that works beats a POC on real data that never starts.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| `SELECT * FROM my_table` | Invented identifier; fails on line one and looks broken |
| "Build a complete production-ready platform" | Unverifiable, expensive, never finishes |
| Slug without the full URL | Visitor cannot find it from a phone |
| "Leverage AI to unlock insights" | Names nothing; CoCo cannot act on it |
| Unresolved `{placeholder}` | Visibly broken artefact |
| No cost constraint | Free-trial credits burn on an idle warehouse |
| Assuming data exists when they said it does not | Stalls immediately |

## Self-check before sending

Every one of these must pass:

- [ ] No unresolved `{...}` placeholders anywhere
- [ ] Guide URL is a full `https://www.snowflake.com/en/developers/guides/<slug>/` from `guides-index.md`
- [ ] No invented database, schema, table or column names
- [ ] Named at least two real Snowflake features
- [ ] Cost constraint present
- [ ] A single, small, verifiable first step
- [ ] 150–250 words
- [ ] Reads as the visitor's own words, not Snowflake marketing
