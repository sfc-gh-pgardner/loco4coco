# Savepoint 2026-09-22a — Paris manufacturing, and three docs brought back in line

## Done and verified

**Paris manufacturing now carries six primaries, in Snowflake as well as in the
repo.** `deploy/load_context.py --connection Frankfurt_L4C` reports `LISTINGS 288
rows`, and `LOCO4COCO.BOOTH.LISTINGS` returns 6 primary / 6 reserve for all three
profiles. The six Paris picks, in order: CEIC Shipping Data, Commodity & energy
price benchmarks, Industry Classification Systems, France Point-of-Interest (19
industry verticals), CEIC Commodities Data, EU + UK B2B Company Database. Each was
asserted `Free`, `is_ready_for_import` and present in `AWS_EU_WEST_3` before being
written.

The source of truth was the question the last session left open: it is
`skills/loco4coco/references/marketplace.json`. `marketplace-index.md` is a
generated mirror of it (`build_marketplace_json.py --mirror`), so never edit the
md. The path is `curate_locality.py --profile fr --industry manufacturing -c
<conn>`, which supports scoping to one industry and leaves every other profile
untouched.

**Two recorded claims turned out to be wrong, and both mattered.**

The first: `_generated.weak_fit_review` said Paris was *intentionally* left at
four because the on-theme data was not offered in `AWS_EU_WEST_3`. Re-running the
region-filtered search returned six on-theme, Free, importable listings. A search
that comes up short and a region that lacks the data look identical from the
output; distinguishing them takes a second run.

The second is sharper. The same review claimed Industry Classification Systems was
absent from the Paris catalogue. `SHOW AVAILABLE LISTINGS` reports it available in
`AWS_EU_WEST_3` and importable — and `marketplace.json` already carried
`AWS_EU_WEST_3` in its own stored `regions` string for that listing. The review
contradicted data the repo already held, via the cheapest possible check. It is
now a Paris primary in place of European Gas Analytics, which reads as energy
rather than manufacturing and moved to reserve. The review *was* right about the
other two London picks: FactSet Supply Chain Relationships and Overture Maps –
Transportation really are absent from `AWS_EU_WEST_3`, re-measured.

**The behavioural point is the one worth carrying forward.** A stall is assembled
primary-then-reserve and sliced to six, so four primaries never showed a visitor
four options — it showed six, with positions five and six filled from reserve by
purchasing-power data. "Let Paris show four" was never the behaviour on the stand.
The shortfall was a live defect, not an accepted consequence.

The composition was a hand-merge, not the search's raw output, on the operator's
instruction. The search had dropped CEIC Commodities Data, a prior primary that
was already good, and had re-added Franciemes IRIS, which the earlier review
deleted. Franciemes IRIS stays deleted.

## Docs

`audit/marketplace-se-review.html` regenerated from `build_se_review_html.py`.
`check_doc_html_sync.py` **PASS** — HTML, the doc section and `marketplace.json`
agree at 144 slots and 79 distinct listings. Before the fix it failed with Paris
at doc=46 against json=48.

**TL;DR Google Doc `1TwRR5uurF8NHGTbQBiBQBs0fHV9lqqUZ7357WxY5e_E` rewritten and
verified.** 46 paragraphs, one H1, nine H2, 13 bullets, and no occurrence of
`--from`, `--name BOOTH`, `Connection: BOOTH` or `grok`. It now describes the
in-place key-pair conversion. One stale line was found in the in-repo body too:
it told the operator to check the admin panel reads `Connection: BOOTH`, a
connection that no longer exists.

**Decision tree Google Doc `1vyAFvNr83nTKP4eJ-jsNN7LV528XZLEO4FwQtqVMXRs` patched
in place and verified.** Section 3 was diffed against the regenerated text and
only the seven differing blocks were touched, applied in descending index order
so earlier edits could not shift later ranges. Read back: section 3 matches the
generated section with **0 remaining diffs**, 21 headings intact, no over-long
heading, so nothing bled into a heading style. `build_doc_section3.py` also
carried the falsified prose about Paris carrying four picks; rewritten.

**`SETUP-PROMPT.md` had drifted far enough to be actively harmful.** Step 3 told
CoCo to query `CURRENT_REGION()` and write the account's region into the config,
warning the stall would be empty otherwise. That is backwards, and it named
`event.region`, a key that does not exist. Following it is the one mistake that
quietly serves visitors another city's data. Step 4 told CoCo to add a deploy
target and paste a pool-assigned account identifier into a tracked file, which
both SETUP.md and `deploy/manifest.yml` say in terms not to do. Both rewritten,
along with three `event.operator` references across SETUP.md and SETUP-PROMPT.md.

## Pre-existing failures, untouched and unrelated

Both fail identically before this session's changes, confirmed by baselining at
the prior commit:

- `assert_listing_slots.py` — bucket-only listings reported unreachable.
- `assert_decision_tree.py` — **80 failures**, all reserve listings absent from
  the tree. The tree appears to document primaries only while the assertion
  expects every listing. Worth a decision: fix the tree, or scope the assertion
  to primaries.

## Next

1. The setup guide Google Doc `102kpn7MXJFYcA9ZHoa6kCKoQe3EgK3Dtj8bwm9wF6bQ` —
   the repo side is now correct but the Doc is not. `audit/setup-doc-changes.md`
   holds the audit. There is no publisher script for this one, unlike the other
   two, so it needs patching in place.
2. Translation status.
3. Post-event processes.
4. Operator still wants to test `/admin` by hand.

## Watch out

- `curate_locality.py` **replaces** a stall rather than topping it up, and will
  happily re-add a listing an earlier review deleted. Diff its output against
  `git show HEAD:...marketplace.json` before accepting it.
- The `marketplace.json` diff looks enormous for a small change because key order
  is rewritten. Compare semantically by `global_name` per profile/industry, not by
  line.
- Google Docs: apply patches in **descending** index order, and do not delete a
  paragraph adjacent to a heading — inserted text inherits neighbouring style.
- `snow sql` needs `--enable-templating NONE`. The LISTINGS column is `RESERVE`
  (boolean), not `TIER`.
