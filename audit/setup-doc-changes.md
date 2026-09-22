# Setup Guide — changes to action

Audit of **Loco for CoCo: Setup Guide**
(`docs.google.com/document/d/102kpn7MXJFYcA9ZHoa6kCKoQe3EgK3Dtj8bwm9wF6bQ`)
against the repo as of commit `eddb0ac`.

Read against the actual booth flow: **per SWT event, the operator registers at
`https://go.dataops.live/emea-swt/register` and is assigned a Snowflake account at
random from a pool.** The accounts are **not identical and not interchangeable** — each
is a separate Snowflake account with its own name, objects and users. What they have in
common is only that they are AWS Frankfurt accounts provisioned the same way, and even
that should not be relied on: the pool decides, and the region is never needed. Each one
is torn down after its event. It is the only Snowflake
HOL accounts we already use, but it is a *different* account with a random name
(`NDL_HACKATHON_WEHBMG` and so on), and the operator does not know which one until
they are in front of it. It is the only Snowflake account on a wiped event laptop,
and the game is set up from inside a CoCo CLI session.

Anything in the guide that asks them to know, choose or type an account identifier
is friction that cannot be satisfied at that moment. Anything that asks them to
pre-declare the account's *region* is worse, because it invites pinning a value
that the pool may not give them.

Two items are not merely stale, they are **actively wrong**: following them
degrades the game. Those are marked **BLOCKING**. One item is a **false promise** —
the guide would tell the operator about a screen that does not exist.

---

## 1. BLOCKING — Localisation §4 "Event.region"

**Currently says:**
> Set to the region the where account actually runs in (e.g. AWS_EU_WEST_3 for
> Paris or eu-central-1 Frankfurt for Berlin), not the city. It must equal the
> account's region or the Marketplace stall is empty. City is cosmetic
> (event.city).

**Why it is wrong:** this conflates two different regions, and the claim "it must
equal the account's region or the stall is empty" is no longer true — the stall no
longer filters listings out by region at all (see item 3).

**Replace with:**
> **You do not set this.** Set `event.venue` to `london`, `paris` or `berlin` and
> the city, language and region are resolved for you.
>
> There are two regions and they are not the same thing:
> - **The event's region** (London `AWS_EU_WEST_2`, Paris `AWS_EU_WEST_3`, Berlin
>   `AWS_EU_CENTRAL_1`) decides which Marketplace datasets are *preferred* in the
>   recommendations, because that is where the visitors live. It is fixed per
>   event and already set for you.
> - **The account's region** is whatever the DataOps pool hands you. **You never
>   need to know it, and nothing asks you for it.** It only decides where
>   SESSIONS, TURNS and blueprints are written. It must never filter
>   recommendations.
>
> This decoupling is what makes the setup portable: the game was verified
> answering for all three event regions from a single AWS Frankfurt account,
> because the Marketplace catalogue is global.

---

## 2. BLOCKING — Localisation §2 "Marketplace datasets"

**Currently says:**
> Re-curate for the local audience; the current picks and geo weighting are
> UK-tuned. […] Re-run `scripts/build_marketplace_index.py` against the your LOCAL
> account and re-verify every listing (SHOW AVAILABLE LISTINGS +
> is_ready_for_import) as availability is regional, so London's picks aren't
> guaranteed in other regions

**Why it is wrong:** **the visitor never imports anything at the booth.** They tick
datasets, those become links in a takeaway document, and they open them later from
their own account. So whether the *booth* account can attach a listing is
irrelevant to whether it is a good recommendation.

Re-verifying against the booth account actively destroys the curation: measured
against the live catalogue, only **28 of the 48** curated UK picks are importable
in `AWS_EU_WEST_2`, and this instruction would delete the other 20 — including
Jaywing Census, CARTO Boundaries, Spatial Features GBR and Met Office UK Land
Surface, four of the best UK datasets on the list.

**Replace with:**
> **Do not re-verify the curated listings against your own account, and do not
> delete a listing because your account cannot import it.** The visitor never
> imports anything at the booth — they leave with links and open them later from
> their own account. A pick is judged on whether it is *relevant to the event's
> city*, not on what the booth can attach.
>
> Curation per city is precomputed and committed in
> `skills/loco4coco/references/marketplace.json`. Picking the venue selects the
> right set. There is nothing to re-run on the day.

---

## 3. Marketplace stall description

**Currently says:**
> 3. THE MARKETPLACE: User ticks listings to join, from 6 curated,
> region-verified options per industry. […] Every listing is checked
> `is_ready_for_import`, so nothing offered is a dead end.

**Why it is stale:** region now *prefers* rather than *excludes* (excluding is what
reduced the London media stall to a single dataset), and there is now a 7th option.

**Replace with:**
> 3. THE MARKETPLACE: the visitor ticks datasets from **6 curated options** for
> their industry, ordered so that ones available in the event's own region come
> first. One COMPLETE call for the reply (~2-3s). Every listing is a real,
> checked Marketplace entry — none are invented.
>
> **The 7th option:** anything the visitor *types* into "something else" triggers
> agentic Marketplace discovery in the background, seeded with the event's country
> and region. **Measured at 6.2-6.4s** (timed against both eu-west-2 and eu-central-1
> filters on an event account), and run in the background anyway so it can never make
> them wait. Any real listings it finds are added to the takeaway document at the
> postbox. If it does not finish in time, nothing is lost.

---

## 4. Setup §3 "Add your deploy target" — delete this step

**Currently says:**
> Edit `deploy/manifest.yml`. Copy the LONDON block, set `account_identifier`,
> city, language and `monitor_notify_user` (a real user in your account — a
> monitor with an empty notify list warns nobody).

**Why it is wrong for the real flow:** the account is provisioned by DataOps Live
with a random name (`NDL_HACKATHON_WEHBMG`), which the operator does not know until
they are in front of it. Asking them to paste it into a tracked file is friction
and invites committing someone's account ID.

**Replace with:**
> **Skip this — there is nothing to add.** The default `EVENT` target deliberately
> pins no account and deploys wherever your connection points. Every event account
> pins no account and deploys wherever your connection points. Every event account is a
> *separate* account — different name, different objects, different users — so there is
> nothing stable worth pinning, and pasting a pool-assigned ID into a tracked file invites
> committing someone else's account identifier.
>
> (An empty notify list is fine. The post-hook falls back to a notify-less
> resource monitor rather than failing, which matters because a freshly
> provisioned user often has no email address at all.)

---

## 5. Setup §4 "Deploy Snowflake objects" — drop `--target`

**Currently says:**
```
python3 deploy/bootstrap.py --target YOURS --connection YOURCONN --plan-only
python3 deploy/bootstrap.py --target YOURS --connection YOURCONN
```

**Replace with:**
```
python3 deploy/bootstrap.py -c YOURCONN --plan-only
python3 deploy/bootstrap.py -c YOURCONN
```

Also update the object list: the monitor is **quota 25 with a suspend trigger**,
not "notify at 100% — no suspend".

---

## 6. Setup §5 "Point it at your event" — collapse to one toggle

**Currently** lists `event.region`, `event.city`, `event.language` as separate
things to edit, with a long explanation of the region.

**Replace with:**
> Edit `game/config.json`:
>
> - **`event.venue`** — `london`, `paris` or `berlin`. **This is the only toggle
>   you need.** City, language and the recommendation region follow from it.
>   Restart the server after changing it.
> - **`event.operator`** — "Your Name / Stand label". Written to
>   `SESSIONS.SE_OPERATOR` for every visitor and **cannot be reconstructed after
>   the event**; the server warns at startup if it is blank.
> - `snowflake.connection_name` — bootstrap normally sets this.

---

## 6a. FALSE PROMISE — remove every mention of `/admin`

`deploy/manifest.yml` and `game/config.json` both state that the venue is
"changeable from `/admin` at the booth". **There is no `/admin` route.** The
server serves `/`, `/api/state`, `/api/config`, `/api/options`, `/api/blueprint`,
`/api/qr` and `/api/delivery/check` — nothing else.

The venue is changed by editing `game/config.json` and restarting the server.
Do not write `/admin` into the guide, and fix the two repo comments that claim it
(see Repo fixes below).

---

## 7. Model names — two places

Both `qa.model` and the COMPLETE model are now **`llama3.3-70b`**.

- §5 currently: *"model defaults to mistral-large2"*
- §"WHAT FUNCTIONS ARE USED" currently: *"Model is mistral-large2"*

**Why:** `mistral-large2` is **legacy in eu-central-1** and `mistral-large` is
deprecated. `llama3.3-70b` is verified working in both eu-west-2 and eu-central-1.
Worth stating that the **first** COMPLETE call on a cold warehouse takes ~56s and
subsequent ones ~4s, so the operator should run one turn before doors open.

---

## 8. Localisation §5 "Deploy target" — delete

Says to add a Paris target with its own `account_identifier` and
`monitor_notify_user`. Superseded by items 4 and 6: set `event.venue`, deploy with
no target.

---

## 9. Requirements — worth adding

The guide lists the prerequisites but not the two things that actually bite:

> - The account's user **may have no email address**. That is fine — the resource
>   monitor falls back to a notify-less monitor.
> - `cortex exec` must be **authenticated for that connection**. The guide's
>   existing "No models available" check is the right test and should stay: if it
>   fails, agentic discovery and the Workshop silently fall back to COMPLETE.

---

## Not stale — leave alone

The objective, the five-stage walkthrough (home stage, letter, library, workshop,
postbox), the QA-review section, the failsafe chain (warm agent → `cortex exec` →
COMPLETE → precomputed), the one-in-flight-agent-call rule and the precomputing
section are all accurate.

---

## 10. NEW — Setup step 0: get your account

The guide currently starts at "clone the repo". It should start one step earlier,
because this is the step the operator actually does first and it is not written
down anywhere.

**Add as the first setup step:**
> **0. Get your event account.** Register at
> `https://go.dataops.live/emea-swt/register`. You will be assigned a Snowflake
> account from a pool — the name is random and you will not know it in advance.
> **Do this once per event** (London, Paris and Berlin each get their own
> account). Everything below works the same whichever account you are given;
> nothing in the setup asks you for its name or region.
>
> Then point a connection at it:
> ```
> snow connection add
> snow connection test -c <yourconn>
> cortex exec "Reply with the single word: ready." --no-mcp
> ```
> All three must succeed before you go further. The third is the one that catches
> a Cortex Code session that is not authenticated — without it, agentic discovery
> and the Workshop quietly fall back to COMPLETE and you will not notice until a
> visitor is standing there.

---

## 11. NEW — `TO-DO: SDR HANDOVER` — the section needs writing, and the reason is now urgent

The heading exists with a signal→column mapping table and a query against
`LOCO4COCO.BOOTH.SESSIONS`. **Both are correct and should stay.** What is missing
is the part that matters.

**The accounts are ephemeral.** Each event runs on a pool-assigned DataOps account
that is torn down afterwards. Every lead the booth captured lives in `SESSIONS` on
*that* account. If nobody exports before teardown, the leads are gone — and because
there is now one account per event, this happens three times.

**Add to the section:**
> **Export the leads before the account is torn down.** This is not optional and
> there is no second chance. The account you were assigned is temporary.
>
> At minimum, on the last day of the event, run the handover query and save the
> result off the laptop. The presigned `DOCUMENT_URL` values expire after 7 days
> independently of the account, so if you export later than that the links are
> dead — re-mint them from the stage:
> ```
> LIST @LOCO4COCO.BOOTH.BLUEPRINTS;
> SELECT GET_PRESIGNED_URL(@LOCO4COCO.BOOTH.BLUEPRINTS, '<filename>', 604800);
> ```
>
> **The same person may visit more than one stand.** Deduplicate on first name and
> company before handing anything to an SDR, or one visitor reads as several
> unrelated leads.
>
> **Do not share the raw table.** It holds a first name, an employer and free text
> the visitor typed. For anything circulated more widely than the SDR who is
> following up, drop the name and company and keep industry, problem statement,
> POC and features.

Tooling for this (an aggregated per-event view, an export that writes somewhere
durable, and an `--anonymise` mode) is scoped but not built. Until it exists the
manual query is the handover, and the guide should say so plainly rather than
leaving a bare TO-DO heading that reads as though something is coming.

---

## 12. Repo fixes that go with these doc changes

| File | Fix |
|---|---|
| `deploy/manifest.yml` | Comment claims venue is "changeable from `/admin` at the booth" — remove. Also drop the assertion that every event account is Frankfurt; say the region does not matter. |
| `game/config.json` | `venues._comment` claims the account region "is always `AWS_EU_CENTRAL_1`" — soften to "whatever the pool assigns; it never filters recommendations". |

---

## Summary

| # | Section | Severity | Action |
|---|---|---|---|
| 13 | **NEW: missing step — load the datasets** | **BLOCKING** | `load_context.py` is absent from the guide, and skipping it silently serves the wrong city's data |
| 14 | Model names (supersedes #7) | **Wrong** | `claude-4-sonnet`, not `llama3.3-70b` — measured 5.1s vs 69.5s median |
| 15 | `event.region` | Renamed | now `event.marketplace_region` |
| 16 | `/admin` (supersedes #6a) | **Now exists** | venue + operator + restart + status; it is the configuration surface |
| 17 | Resource monitor | **Wrong** | notify-at-100% cannot notify anyone; quota 100, no suspend, and say plainly it is a ceiling not a guard |
| 18 | "identical accounts" | **Wrong** | separate accounts, not interchangeable |
| 19 | 7th option latency | **Wrong** | 6.2–6.4s measured, not 75–110s |
| 20 | Requirements | Trim | fold into the install step |
| 21 | **NEW: let CoCo do it** | Missing | paste-in prompt + repo link as the primary route |
| 22 | TL;DR | Rewrite | see below |

### The TL;DR to replace the existing one

> Currently: *"translate config.json, reweight + re-verify the marketplace for the region,
> set event.region to the account's real region, add a deploy target with its own notify user"*.
> **Every one of those four is now wrong.** Replace with:
>
> Register for an account, add a connection, run `bootstrap.py`, run **`load_context.py`**,
> then pick your venue and type your name in `/admin`. Nothing to translate, no region to
> set, no deploy target to add, no marketplace to re-verify.

---

## Summary (first round, items 1–12)

| # | Section | Severity | Action |
|---|---|---|---|
| 1 | Localisation §4 Event.region | **BLOCKING** | Rewrite — two different regions, account region is irrelevant |
| 2 | Localisation §2 Marketplace | **BLOCKING** | Rewrite — do NOT re-verify/re-curate |
| 3 | Marketplace stall description | Stale | Add the 7th option, soften region |
| 4 | Setup §3 deploy target | Obsolete | Delete the step |
| 5 | Setup §4 deploy commands | Stale | Drop `--target`, fix monitor |
| 6 | Setup §5 point it at your event | Obsolete | Collapse to `event.venue` |
| 6a | Any mention of `/admin` | Superseded by 16 | It exists now |
| 7 | Model names (×2) | Superseded by 14 | `claude-4-sonnet` |
| 8 | Localisation §5 deploy target | Obsolete | Delete |
| 9 | Requirements | Gap | Add emailless user + Cortex auth |
| 10 | Setup step 0 | **Missing** | Add DataOps registration, once per event |
| 11 | TO-DO: SDR HANDOVER | **Missing** | Write it — export before teardown, dedupe, anonymise |
| 12 | Repo comments | Wrong | Fix `/admin` and the pinned-region claims |

Net effect on the operator: the setup goes from "know your account, paste its ID
and region into a tracked file, add a deploy target, re-verify the marketplace
against your own account" to **register, add a connection, run bootstrap, load the
datasets, pick your venue and name in `/admin`, start the server**. Nothing to look
up, nothing to paste.

## Applied 2026-09-22 to the live Setup Guide doc

Seven passages patched in place, verified by reading the doc back. Bulleted items
were patched by replacing the text inside the paragraph rather than the paragraph
itself, so the bullets survived; paragraph count is unchanged at 322.

Two were actively wrong rather than merely stale. The troubleshooting entry for an
empty Marketplace stall blamed `event.region` not matching the account's region,
and the localisation TLDR told the reader to set `event.region` to the account's
real region. Both invert the rule the whole design rests on: the account's region
decides only where rows are written, and the event's region — resolved from
`event.venue` — decides which datasets are offered. Following either entry serves
visitors another city's data.

The rest: the deploy-target step told the reader to add a target with a
pool-assigned `account_identifier` and run `bootstrap.py --target PARIS`, which
contradicts both SETUP.md and the manifest; a pre-flight step said to re-verify
curated listings against the booth account, which is the check that bins listings
a visitor could import perfectly well from their own; two duplicate `event.operator`
passages described a field that no longer exists; and the slow-reply entry still
offered `mistral-large2`, which is legacy on a Frankfurt event account.
