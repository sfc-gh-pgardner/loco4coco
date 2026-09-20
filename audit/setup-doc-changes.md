# Setup Guide — changes to action

Audit of **Loco for CoCo: Setup Guide**
(`docs.google.com/document/d/102kpn7MXJFYcA9ZHoa6kCKoQe3EgK3Dtj8bwm9wF6bQ`)
against the repo as of commit `eddb0ac`.

Read against the actual booth flow: a user gets a **wiped event laptop**, logs into
a **DataOps Live account whose ID they do not know in advance**, and sets the game
up from inside a **CoCo CLI session** — that account being the only Snowflake
account on the device. Anything in the guide that asks them to know or type an
account identifier is friction that cannot be satisfied at that moment.

Two items are not merely stale, they are **actively wrong**: following them
degrades the game. Those are marked **BLOCKING**.

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
> the city, language and region are resolved for you — or just pick the event in
> `/admin`.
>
> There are two regions and they are not the same thing:
> - **The event's region** (London `AWS_EU_WEST_2`, Paris `AWS_EU_WEST_3`, Berlin
>   `AWS_EU_CENTRAL_1`) decides which Marketplace datasets are *preferred* in the
>   recommendations, because that is where the visitors live.
> - **The account's region** is always `AWS_EU_CENTRAL_1` (every event runs on its
>   own AWS Frankfurt account). It only decides where SESSIONS, TURNS and
>   blueprints are written. It must never filter recommendations.

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
> and region. It never makes them wait — the call takes 75-110s — and any real
> listings it finds are added to the takeaway document at the postbox. If it does
> not finish in time, nothing is lost.

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
> is an identical AWS Frankfurt account, so there is nothing worth pinning.
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
>   Changeable from `/admin` at the booth.
> - **`event.operator`** — "Your Name / Stand label". Written to
>   `SESSIONS.SE_OPERATOR` for every visitor and **cannot be reconstructed after
>   the event**; the server warns at startup if it is blank.
> - `snowflake.connection_name` — bootstrap normally sets this.

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
COMPLETE → precomputed), the one-in-flight-agent-call rule, the precomputing
section, and the SDR handover query are all accurate.

---

## Summary

| # | Section | Severity | Action |
|---|---|---|---|
| 1 | Localisation §4 Event.region | **BLOCKING** | Rewrite — two different regions |
| 2 | Localisation §2 Marketplace | **BLOCKING** | Rewrite — do NOT re-verify/re-curate |
| 3 | Marketplace stall description | Stale | Add the 7th option, soften region |
| 4 | Setup §3 deploy target | Obsolete | Delete the step |
| 5 | Setup §4 deploy commands | Stale | Drop `--target`, fix monitor |
| 6 | Setup §5 point it at your event | Obsolete | Collapse to `event.venue` |
| 7 | Model names (×2) | Stale | `llama3.3-70b` |
| 8 | Localisation §5 deploy target | Obsolete | Delete |
| 9 | Requirements | Gap | Add emailless user + Cortex auth |
