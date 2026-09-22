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
