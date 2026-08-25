# Brand and marketing review checklist

Loco 4 CoCo is a booth activation that runs on a Snowflake-branded stand and
hands visitors a document they keep. Everything below is visitor-facing, so it
needs a decision from Snowflake marketing, brand or legal before the first
event. Nothing here is a known violation; it is the list of things only those
teams can sign off.

Every row names the file so a reviewer can see the real thing rather than a
description of it. Run the game locally (`python3 game/server.py`) to see any
item in context.

**Status key:** `NEEDS DECISION` - cannot ship without an answer.
`NEEDS CHECK` - probably fine, confirm it. `FYI` - disclosure, no action expected.

---

## 1. Name, mascot and persona

| # | Item | Where | Status |
|---|---|---|---|
| 1.1 | The name **"Loco 4 CoCo" / "Loco for CoCo"**. Reads as "crazy for CoCo". Approved for a Snowflake-branded stand? | `game/config.json` -> `event.title`, `intro.title`; attract banner `index.html` `#b-title` | NEEDS DECISION |
| 1.2 | **"CoCo" as a nickname for Cortex Code.** Used throughout, including in the visitor's document. Is this an approved abbreviation, or must it be "Cortex Code" on every mention? | everywhere; `intro.body[0]` says "Cortex Code (CoCo)" | NEEDS DECISION |
| 1.3 | **Cortex Code personified as a penguin** with a home, a workshop and a personality, who writes the visitor a letter. Anthropomorphising a product is a brand-level call. | opening sequence, all four interiors | NEEDS DECISION |
| 1.4 | The **Antarctica joke**: "(Yes, penguins live in Antarctica, but CoCo is special!)" | `intake.letter.arctic_sub` | NEEDS CHECK |
| 1.5 | **"the Cortex Crew"** as a collective name for the product family. Invented for this game. | `intake.letter.body` | NEEDS CHECK |
| 1.6 | Personal byline **"by Paddy Gardner"** on the attract screen of a Snowflake-branded booth. | `event.byline`, `index.html` `#b-by` | NEEDS DECISION |

## 2. Logo and mark usage

| # | Item | Where | Status |
|---|---|---|---|
| 2.1 | **The Snowflake mark redrawn as pixel art on a canvas.** The wall logo in CoCo's house is rendered into a pixelated canvas at small size. Brand guidelines normally prohibit redrawing, distorting or rasterising the mark. This is the single most likely objection in this document. | `index.html` `drawScene('house')`, "Snowflake logo on the wall" | NEEDS DECISION |
| 2.2 | Mark and wordmark shipped as PNG and scaled by the browser. Confirm these are the current approved files and that we have the right sizes. | `game/assets/snowflake-mark.png`, `snowflake-wordmark.png` | NEEDS CHECK |
| 2.3 | Mark used **twice flanking the word "DONE"** on the completion screen, as decoration either side of a word. | `index.html` `#ov-done` | NEEDS CHECK |
| 2.4 | Minimum size and clear space. The mark renders at 36x36 px on the done screen and smaller in-scene. | `#ov-done`, house interior | NEEDS CHECK |
| 2.5 | Logo lock-up in the generated **Word document** the visitor keeps. Confirm placement, size and whether a footer or legal line is required. | `game/server.py` `blueprint_docx()` | NEEDS DECISION |

## 3. Colour and type

| # | Item | Where | Status |
|---|---|---|---|
| 3.1 | Primary blue **#29B5E8**. Confirm this is the current Snowflake blue. | `index.html` CSS `--edge` | NEEDS CHECK |
| 3.2 | **Orange #E8863C** on every primary button, including the START button a visitor sees first. Confirm it is an approved accent and approved for primary actions. | `--warm`; `#t-go`, `#bp-send` | NEEDS DECISION |
| 3.3 | Whole UI is **monospace** (SF Mono / Menlo / Consolas) for the arcade feel, not the Snowflake brand typeface. Deliberate; needs a blessing. | `index.html` `body` font stack | NEEDS DECISION |
| 3.4 | Dark-only theme. No light variant exists. | throughout | FYI |

## 4. Claims and copy

The intro card is the first and most-read screen. Its full text is in
`config.json` -> `intro.body`.

| # | Item | Where | Status |
|---|---|---|---|
| 4.1 | **"how enterprise-grade AI can bring your ideas to life"** - a product claim. | `intro.body[1]` | NEEDS CHECK |
| 4.2 | **"You have 5 minutes"** and **"After 5 minutes you will have a personalised action plan"** - a deliverable promise on a timer. | `intro.body[1]`, `intro.body[2]` | NEEDS CHECK |
| 4.3 | **"Five minutes to your next data product"** (subtitle). | `event.subtitle` | NEEDS CHECK |
| 4.4 | **"a very real and useful outcome"** and **"be daring!"** - tone check. | `intro.body[2]` | NEEDS CHECK |
| 4.5 | The document is titled a **"blueprint"** and contains a **readiness score out of 5**. A numeric score on Snowflake-branded paper may read as a formal assessment rather than a conversation starter. | `server.py` `blueprint_html()`, `poc.readiness` | NEEDS DECISION |
| 4.6 | The document names **specific next steps and features** for the visitor's own business. Confirm wording that keeps this a suggestion, not advice or a commitment. A disclaimer line may be required. | `blueprint_html()`, `blueprint_docx()` | NEEDS DECISION |
| 4.7 | CTA to **signup.snowflake.com** (free trial) in the document. Confirm this is the campaign URL marketing wants, or supply a tracked one. | `delivery.signup_url` | NEEDS DECISION |

## 5. Product names in visitor-facing output

The document names real products. Any misnaming ships on paper the visitor keeps.
A product marketing reviewer should check this list against current naming.

| # | Item | Where | Status |
|---|---|---|---|
| 5.1 | Feature names the model is instructed to use: **Cortex Analyst, Cortex Search, Snowpark, Dynamic Tables, ML Classification, Snowflake Marketplace**. | `config.json` library/workshop `prompt` | NEEDS CHECK |
| 5.2 | Ingestion names in the route section: **Openflow** (and its Oracle, Azure Blob, SQL Server and SaaS connectors), **Snowpipe**, **external stage**, **storage integration**, **catalog integration**, **Iceberg**, **SAP Business Data Cloud**. | `server.py` `INTEGRATION_PATHS` | NEEDS CHECK |
| 5.3 | Claims about **first-party connectors** existing for named third-party products (Azure Blob, SQL Server, Oracle CDC, Salesforce, Workday). These must be true on the event date. | `server.py` `INTEGRATION_PATHS` | NEEDS CHECK |
| 5.4 | Deep links to `docs.snowflake.com` and `other-docs.snowflake.com`. Every one must resolve - a 404 on a handout is worse than no link. Re-run the link check before each event. | `server.py` `INTEGRATION_PATHS`, `guides` | NEEDS CHECK |

## 6. Third-party and Marketplace content

| # | Item | Where | Status |
|---|---|---|---|
| 6.1 | The game **recommends named third-party Marketplace listings** with their provider names, six per industry, and puts them in the visitor's document. Partner and legal implications of Snowflake appearing to endorse specific providers at its own event. | `game/marketplace-index.md` | NEEDS DECISION |
| 6.2 | All current picks are **free listings**, chosen deliberately so a trial user can build immediately. Confirm that is the right commercial posture. | `scripts/build_marketplace_index.py` `CURATED` | NEEDS CHECK |
| 6.3 | Listing availability is **region-locked to the event region** and verified importable before shipping. Re-verify before each event; listings get withdrawn. Five were found broken during one build. | `scripts/build_marketplace_index.py` | FYI |
| 6.4 | Third-party **company names appear as industry examples** in placeholder text (e.g. "NHS Trust, Barclays, Tesco"). These are prompts for the visitor, not customer claims, but they are on screen. | `intake.fields` company placeholder | NEEDS DECISION |

## 7. Data capture, privacy and security

This is the section most likely to need legal rather than marketing.

| # | Item | Where | Status |
|---|---|---|---|
| 7.1 | We capture **first name, company and a free-text business problem** and store them in Snowflake (`LOCO4COCO.BOOTH.SESSIONS`). No consent text or privacy notice is shown anywhere in the flow. At a UK event this needs a lawful-basis decision and probably a visible notice. | `server.py` `log_session()`, `deploy/sources/definitions/booth.sql` | NEEDS DECISION |
| 7.2 | The **free-text problem field** invites the visitor to describe a business problem. They may type commercially sensitive or personal information. Retention and access need a decision. | `intake.problem_label` | NEEDS DECISION |
| 7.3 | **Email is no longer collected.** The `SESSIONS.EMAIL` column still exists but is always empty. If marketing expects leads from this activation, that is now a gap - raise it before the event. | `server.py` `_intake()` | NEEDS DECISION |
| 7.4 | The handover is a **presigned URL valid for 7 days, unauthenticated** - anyone with the link can download that visitor's document. Confirm acceptable. | `delivery.presign_seconds` | NEEDS CHECK |
| 7.5 | A QR code is displayed for the visitor to scan with a personal phone. Confirm no tracking or consent implication. | `index.html` `#bp-qr` | NEEDS CHECK |
| 7.6 | Visitor input is sent to an LLM to generate the document. Confirm this is covered for a public event and whether the visitor must be told. | `server.py` `run_exec()` | NEEDS DECISION |
| 7.7 | State is **single-visitor per server process** and reset between visitors. Confirm the reset is acceptable as a data-separation control on a shared laptop. | `server.py` `write_state(replace=True)` | NEEDS CHECK |

## 8. Accessibility

Public-facing Snowflake surfaces usually carry an accessibility bar. None of this
has been formally tested.

| # | Item | Where | Status |
|---|---|---|---|
| 8.1 | **Contrast** not measured against WCAG AA. Dim grey `--dim` on dark panels is the most likely failure. | `index.html` CSS | NEEDS CHECK |
| 8.2 | The map requires **WASD/arrow-key movement**. There is a keyboard path to everything, but no pointer-only or assistive route to walk the penguin. | `index.html` movement handler | NEEDS DECISION |
| 8.3 | **A 5-minute countdown** drives the experience. Time limits are an accessibility consideration; confirm a visitor can opt out or be given more time. | `event.time_limit_seconds` | NEEDS CHECK |
| 8.4 | Colour is used to convey progress state (visited / current). Check it is not the only signal. | stage bar | NEEDS CHECK |
| 8.5 | Animation includes **flicker on the forge and the welding arc**. Check against photosensitivity guidance. | `drawScene('workshop')` | NEEDS CHECK |
| 8.6 | Pixel-art body text is monospace at 13-15 px in places. Check minimum legible size at booth viewing distance. | panels | NEEDS CHECK |

## 9. Operational, for the stand

| # | Item | Status |
|---|---|---|
| 9.1 | Someone must **drain the outbox** if email delivery is ever re-enabled. Today nothing is sent and the QR is the only delivery. | FYI |
| 9.2 | The activation **spends Snowflake credits** per visitor (warehouse plus model calls). Confirm the budget owner and that a resource monitor is in place. | NEEDS DECISION |
| 9.3 | Run `python3 game/smoke_test.py` and the delivery preflight on the stand before doors open. | FYI |
| 9.4 | Decide what happens when the **5-minute timer expires mid-visit** - it currently shows `OVER` while the flow continues. Confirm intended. | NEEDS DECISION |

---

## How to review this efficiently

1. **Blockers first.** Items 2.1 (redrawn mark), 7.1 (no privacy notice) and 1.6
   (personal byline) are the ones most likely to stop the activation.
2. **Then the handout**, section 4 and 5 - it is the artefact that leaves the
   stand and outlives the conversation.
3. **Then tone**, section 1 - cheaper to change than anything structural.

To see any item live: `python3 game/server.py`, open `http://127.0.0.1:4747/`.
The decision tree, including every branch a visitor can take and what each one
prints, is generated into `game/decision_tree.md` by `python3 game/decision_tree.py`.
