# Savepoint 2026-09-22b — per-region audit, hangover sweep, admin panel, seeded handover

Working tree clean. Server left running on <http://127.0.0.1:4747> for manual
testing, venue back on London.

## The marketplace audit, and two false-positive classes of my own

New `scripts/audit_marketplace_regions.py` checks all three profiles against one
`SHOW AVAILABLE LISTINGS` pull, each judged on **its own event region**. One
Frankfurt account can audit all three events because the regions column is global.

**The curation itself was sound: 0 of 288 picks withdrawn, 0 missing from their own
event region.** Everything else found was a flag problem, not a curation problem.

**I got the audit wrong twice before it was right, and both traps are now written
into the script rather than quietly removed.**

`is_ready_for_import` is **account-local**. Run from a Frankfurt booth it flagged
26 primaries, and every London one it named was present in `eu-west-2` and absent
from `eu-central-1`. Judging an event's picks on it bins listings its visitors can
import perfectly well — the exact trap the memory already warned about, walked into
anyway.

`is_monetized` does not mean unavailable. Several picks are paid products carrying a
7, 14, 30 or 60 day free trial that the curated `access` string already records, and
`is_limited_trial` does not always reflect it. The curated label is the claim worth
testing, so that is what is tested now.

## The finding that mattered, and it came from running the thing

A Paris manufacturing primary was `is_by_request` — the visitor must ask the
provider and wait, not tick and import. It arrived in the previous session's commit,
because `curate_locality.py` read that flag and never filtered on it. Replaced with
Chemical Price Assessments, same input-cost ground, imports directly.

**Then the assumption behind the first fix turned out to be false.** I sank the
remaining by-request picks to the back of reserve, believing a reserve is only
reached when a primary is filtered out. Seeding a visit disproved it: a Paris
**energy** visitor was offered two listings that exist nowhere except
`manufacturing/reserve`, both by-request. **Stalls borrow across industries within
the profile, so every curated pick is visitor-facing and sinking an unobtainable one
hides nothing.** All three by-request listings are now removed outright, and the
audit no longer grades reserves as lower severity. 277 picks, 0 problems.

Nine reserves labelled `Paid` were dropped rather than replaced — a shorter reserve
list is honest where padding with off-theme picks is not. Totals are now London 92,
Paris 97, Berlin 91.

## Hangover sweep

- **`server.py` defaulted COMPLETE to `mistral-large2`**, which is legacy and 400s
  on every call. A config missing `complete_model` would have failed every fast turn
  while the exec fallback quietly carried the booth. Now `openai-gpt-5`.
- SETUP.md and README.md told the operator the default was `claude-4-sonnet` at
  5.1s, in three places, and offered `mistral-large2` as a fast alternative. Both
  legacy. They now name the real default `openai-gpt-5.4` and its three verified
  fallbacks.
- `config.json` said the seventh option's region filter came from `event.region`, a
  key that does not exist.
- Dataset-count guidance said 90–96, which would have made a correctly-loaded Paris
  look wrong at 97. Now leads with the stable invariant: 48 picks offered.

## Three defects found by driving /admin

The agentic browser **did** attach over plain HTTP on `127.0.0.1` — the note saying
it would not is out of date for this version.

1. **Apply could silently save the wrong venue.** The status poll reset the dropdown
   whenever the select was not focused, and clicking Apply moves focus to the button
   — so a poll landing between choice and click reverted the selection, Apply sent
   the old venue, and the panel still said "Saved". An operator could set Paris, be
   told it saved, and run the whole event on London data. Now tracks an explicit
   pending-choice flag, and reports what the server actually saved.
2. **The panel could never report an idle booth.** `visitor_active` was `bool()` of a
   dict the default state always populates with empty strings, so it was permanently
   true and "Clear visitor" appeared to do nothing.
3. The panel still told the operator to set an operator field that does not exist.

## Decision tree

`assert_decision_tree` was failing with 80 errors because it counted primaries and
reserves together while the tree documented only the six a visitor sees. The tree now
has a **fallback section** per industry, the headline count stays at what a visitor is
offered, and the fallback pool is counted separately — two honest claims instead of
one conflated. Two listings reported missing were present: a pipe in a title is
escaped `\|` for the Markdown table, and the comparison used the escaped form.
**Sentinel-tested**: planting an absent listing produces exactly one failure naming
it, removing it returns the suite to clean.

## Handover

`scripts/seed_visits.py` drives four varied visitors end to end. All four completed,
103s for the set. `deploy/handover.sql` holds seven SDR queries, validated against
the seeded rows — which caught two wrong assumptions: `MARKETPLACE_JOINED` is an
ARRAY, and `TURNS` records `VISITOR_INPUT`/`REPLY` per turn rather than a speaker
column. Runs clean end to end.

11 sessions, 2 cities. London 6 visits averaging 62s (worst 206s), Paris 5 averaging
23s — all well inside the 300s budget.

## Translation status: recorded but inert

`event.language` is resolved from the venue, written to `SESSIONS.LANGUAGE_CODE`, and
shown in the panel and startup banner. **It is never passed into a prompt, and there
is no per-language copy deck anywhere.** Evidence: all five Paris sessions carry
`LANGUAGE_CODE = fr`, and not one POC name is French — four are English and one,
"Frühwarnung bei Lieferverzögerungen", is **German**, because the model followed the
company name Rheinpark Logistik rather than the configured language.

So translation is not partially done; it is unstarted, with the field plumbed. Two
separate pieces of work: static UI copy needs a deck per language, and generated
content needs the language pinned in the prompt — the German POC name shows the model
will otherwise take its cue from whatever the visitor typed.

## Next

1. Translation, as two pieces of work above.
2. Post-event processes.
3. Operator wants to test `/admin` by hand; the server is up on
   <http://127.0.0.1:4747> for exactly that.
4. `assert_listing_slots.py` still reports bucket-only listings unreachable.
   Pre-existing, unrelated, untouched.

## Watch out

- **A reserve is not a quiet backup.** Stalls borrow across industries, so any
  curated pick can be served in any stall. Never fix an unobtainable listing by
  demoting it.
- **Never judge another region's picks on `is_ready_for_import`.** It answers "can
  THIS account import it", and every booth account is Frankfurt.
- `curate_locality.py` **replaces** a stall rather than topping it up. Diff against
  `git show HEAD:...marketplace.json` before accepting.
- `game/decision_tree.py` writes to **stdout**; redirect to `game/decision_tree.md`.
- Google Docs: patch in **descending** index order; for bulleted lines replace the
  text inside the paragraph, not the paragraph, or the bullet is lost.

---

# Continued 2026-09-22c — primaries were being displaced; repo bloat audit

## The big one: HALF the curated primaries never reached a visitor

`assert_listing_slots` had been failing for a while and it was RIGHT. One line did it:

    base = 2 if r in own else 0

`own` is `market[industry]`, which holds that bucket's **primaries AND reserves**, so
a reserve had identical standing to a primary — and a single theme overlap, also worth
2, was enough to push a curated pick out of its own stall. **Measured before the fix:
energy served 3 of its 6 primaries, financial 3 of 6**, displaced by reserves from
their own bucket rather than by anything the visitor said.

This quietly undid the point of curating. Every weak-fit verdict, every region check,
the whole Paris exercise applies to *primaries*, and only half were being offered.

Fix: `base = 1000` for an own-bucket primary (`r in own and not r.get("reserve")`),
2 for an own-bucket reserve, 0 for a borrow. Ranking now reorders WITHIN the primaries;
reserves and borrows compete only for slots primaries do not fill. Verified: 0 stalls
drop a primary, across all 8 industries under both probe states. **Variety survives** —
the same six appear in a different order per session id, which is what the docstring
always claimed. Smoke test PASS, 36.0s.

`rows` carry a `reserve` boolean, which is what made the fix cheap.

## bucket_only is UK-only — inert at two of three events

`marketplace.bucket_only` is a flat list of 12 global names that must never be
borrowed across buckets. **12 of 12 exist in the uk profile, 0 of 12 in fr or de**, so
at Paris and Berlin nothing is protected from cross-bucket borrowing. A flat list can
only protect the profile it was written for. `assert_listing_slots` now REPORTS this
per profile rather than failing — it is a curation gap for whoever localises next.

## Regression I introduced and fixed

I committed `game/config.json` with `venue: paris` mid-test, alongside `city: London`
from an earlier write. `resolve_venue` makes the venue win at runtime, so a fresh
clone came up as Paris while the file read London — and my own `bucket_only` probe
silently ran against the `fr` profile before I noticed. Repo default is London again
and the file is internally consistent. **Lesson: never `git add game/config.json`
while a venue test is in flight.**

## Translation: what exists, for handover

Every reference to language, exhaustively: `event.language` in config (+ per-venue
en/fr/de), `bootstrap.py:159` setting it, `resolve_venue` overwriting it,
`server.py:2033` writing `SESSIONS.LANGUAGE_CODE`, `server.py:2934` in the admin
payload, `server.py:3343` in the startup banner, `admin.html:141` displaying it.

**It never enters a prompt, and there is no per-language copy deck.** The field is a
label. Size of the job: **212 visitor-facing strings** in `config.json` (industries
158, locations 43, intro 6, screens 5) plus **5 prompts** that generate visitor-facing
text (`intake`, `locations.library`, `locations.marketplace`, `locations.workshop`,
`ask`). Evidence it is inert: all five Paris sessions carry `LANGUAGE_CODE = fr` and
no POC name is French — four English, one German ("Frühwarnung bei
Lieferverzögerungen") because the model followed the company name Rheinpark Logistik.

## Repo bloat audit

Tracked: **5.5 MB**, 113 files. `.gitignore` **already lists `audit/shots/`** but the
16 PNGs (~1.8 MB, the largest tracked files by far) are still tracked — an ignore rule
added after a commit does not untrack. Candidates to untrack, pending the operator's
call on scope:

- `audit/shots/*.png` — 16 files, ~1.8 MB, already gitignored, pure run output.
- `audit/marketplace-region-audit.json` — regenerable output of the new audit script,
  tracked by me this session in error.
- `audit/marketplace-se-review.html` — generated by `build_se_review_html.py`.
- `audit/weak-fit-review.md`, `audit/setup-doc-changes.md`, `audit/personas.md` —
  internal working records.
- `notes/2026-09/savepoint-*.md` — internal savepoints (4 files).

Deliberately KEEP: `audit/playwright.config.js` and `audit/playwright/personas.spec.js`
— the existing gitignore comment says they ship on purpose so another SE can run the
suite.

## Still to do

1. Untrack the bloat once scope is agreed, and extend `.gitignore`.
2. `sql_statements/` folder: SDR follow-up + manual session recovery. `deploy/handover.sql`
   already holds seven validated queries and should move/copy there.
3. The "what could break" FAQ.
