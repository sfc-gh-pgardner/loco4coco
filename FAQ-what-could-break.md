# What could break, and what to do about it

Written from defects actually found, not imagined ones. Each entry says how it shows
up at the stand, how to confirm it, and what to do. Anything marked **MEASURED** was
observed on a real event account.

The general rule: **this booth degrades silently rather than erroring.** Almost every
failure below looks like a working stand. That is why the checks matter more than the
error messages.

---

## Before doors open

### The stall shows the wrong city's data
**How it shows up:** nothing. The game runs perfectly and offers London datasets to a
Paris visitor.
**Confirm:** `/admin` — **Dataset profile** should match your city, and **Datasets
loaded** should be 88–100 (London 92, Paris 97, Berlin 91). `0` means it never loaded.
**Do:** run `deploy/load_context.py --connection <conn>`, then press **Apply** in
`/admin`. In that order — Apply is the only thing that clears the dataset cache, so
loading after you Apply can leave the old data being served for the life of the
process.

### Apply says "Saved" but nothing changed
**MEASURED and fixed 2026-09-22.** The status poll used to reset the venue dropdown
whenever it was not the focused element, and clicking Apply moves focus to the button
— so a poll landing between your choice and the click reverted it, and the booth saved
the *old* venue while reporting success.
**Confirm:** the panel now tells you if the server saved something different from what
you asked for. Also check **City** and **Marketplace region** actually changed.
**Do:** if you see the mismatch warning, press Apply again. If it persists, restart.

### The reply model has gone legacy
**MEASURED twice.** `claude-4-sonnet` and `mistral-large2` have both entered legacy
state mid-project and now return a 400 in about half a second, on every call. When
that happened, every fast turn failed and the 20–27s agentic fallback silently carried
the booth for a whole test run — visitors just experienced a slow stand.
**Confirm:** `/admin` — **Model proven** must read *yes, <model> answered*, in green.
**Do:** `scripts/rebench_complete.py` against the event account, then set
`coco.complete_model`. Current default `openai-gpt-5.4`, fallbacks `openai-gpt-5`,
`claude-sonnet-5`, `claude-opus-5` (all 1.4–2.1s in eu-central-1). Do **not** set
`llama3.3-70b` — 69.5s median, ranging to 111s. **Model availability moves under you;
re-measure per event, per region.**

### The first visitor is painfully slow
**MEASURED:** the first COMPLETE call on a cold warehouse takes about 56s; later ones
about 4s.
**Do:** run one throwaway visit before doors open. `scripts/seed_visits.py --only 0`
does it in about 20s.

### macOS asks for a keychain or browser password mid-visit
The booth authenticates roughly three times per visitor — about 312 times over a
hundred-visitor day — and any one of those can put a dialog on screen while somebody
is standing in front of you.
**Confirm:** `scripts/check_auth_safety.py` must PASS on all four resolution paths.
**Do:** `scripts/setup_keypair.py --connection <your-connection>`. One thing the audit
cannot see: the **connection picker inside Cortex Code is a runtime choice** and is not
written to `settings.json`, so if you get browser reauth while CoCo is helping you,
check what the picker is set to.

---

## During the event

### A visitor leaves with nothing
**Confirm:** `sql_statements/03-event-health.sql` — the delivery breakdown. Anything
other than `DELIVERED` is a visitor who got no takeaway.
**Do:** the SESSIONS row is written at the postbox, so the blueprint is almost always
still recoverable. `sql_statements/04-recover-a-session.sql` rebuilds everything the
document contained from columns, and reissues a presigned URL. Presigned links last
seven days, so a visitor returning later needs a fresh one.

### Replies stop coming back
**Do:** **Restart server** in `/admin`, not *Clear visitor*. Restart replaces the
process; the first reply afterwards is slow. A known cause: a cancelled in-flight call
wedges the warm-agent pool.

### The panel says a visitor is in progress when the booth is empty
**MEASURED and fixed.** `visitor_active` was a truth test on a dict the default state
always populates, so it was permanently true and *Clear visitor* looked broken.
**Confirm:** an idle booth should now read **Visitor: none**.

### Costs run away
**Nothing caps the booth, deliberately.** There is no resource monitor, no credit
quota, and no idle shutdown, because each of those ends the activation in public
rather than saving money worth having.
**MEASURED:** the booth warehouse used **0.78 credits in 14 days**, against **64
credits for Cortex Code Desktop** over the same period. The booth is not where an
account gets into trouble.
**Confirm:** `SHOW WAREHOUSES LIKE 'LOCO4COCO_WH'` must report `resource_monitor` as
`null`.
**Do:** watch `game/cost.jsonl` and `sql_statements/03-event-health.sql`. Do **not**
add a `DO SUSPEND` trigger. This was got wrong twice — first a monitor whose notify
triggers Snowflake silently dropped, because a pool account's user has no email, so it
looked like a guardrail while doing nothing; then a suspend trigger, which would have
cut the stand off mid-visit. If a shared account needs a ceiling, put it on a different
warehouse.

### The stand is dead when someone walks up
**Fixed 2026-09-22.** The server used to shut itself down after 45 minutes idle, and
45 minutes of quiet at a stand is an ordinary lunchtime — so the booth could be dead
with nobody watching the terminal to notice.
**Confirm:** `server.idle_shutdown_minutes` should be `0`.
**Do:** if the process has genuinely died, restart it. The warehouse's own 60s
auto-suspend is fine and unrelated — it auto-resumes, which costs latency on the first
call, not availability.

## The things that look fine and are not

### The warm agent on a laptop with a different Cortex Code version

**Fixed 2026-09-22.** The booth runs on whatever `cortex` is installed on the
laptop it is handed, and `cortex mcp serve` is not a stable contract between
versions. The fallback chain was documented as four layers deep, but one failure
mode went *underneath* it.

`_read_until()` in `agent_pool.py` computed a deadline and then blocked in
`self._p.stdout.readline()`, which has **no timeout** — so the deadline was only
ever checked *between* lines. A `cortex` that started `mcp serve` and then went
quiet hung forever: no `exec`, no COMPLETE, no precomputed answer, just a visitor
watching an empty bubble with a queue behind them. `start()` used the same
function, so on such a version the booth hung before a fallback even existed.

stdout is now drained by a daemon thread into a queue, which is what makes the
deadline real. **Do not simplify that back to a direct `readline()`.**

All four failure modes were then tested with stub binaries on PATH, and each now
degrades in bounded time to `cortex exec`:

| What the CLI does | Result | Cost |
|---|---|---|
| no `cortex` on PATH | `start()` → False | 0.0s |
| starts, exits immediately | `start()` → False | 0.0s |
| serves, no `cortex_code_agent` | detected at startup, latched | 0.1s/turn |
| serves, initialises, never replies | `TimeoutError` | bounded |

The third is the likeliest real-world case, and it used to be rediscovered on
every single turn. `_check_capability()` now checks `tools/list` once at startup
and logs plainly that **the warm agent is unavailable on this version and every
turn will use exec** — a visible indicator rather than silent degradation. A CLI
that will not answer `tools/list` is *not* condemned on that evidence; it is
logged and allowed to try, because slow is not the same as broken.

Also fixed: `agent_pool.py` hardcoded `"cortex"` while the exec and marketplace
paths both honour `coco.binary`. On a laptop where the CLI is not on PATH, setting
an absolute path in config gave a working `exec` beside a warm agent that silently
never started. All three now read the same setting.

Verified on v1.1.91: warm start 1.9s, calls at 5.1s/3.9s/3.9s; forcing the warm
layer unavailable falls through to `exec` in 22.0s with `transport='exec'`; full
`smoke_test.py` passes at 32.0s of the 300s budget.

### Curated picks not reaching visitors
**MEASURED.** The home-bucket score treated a bucket's primaries and its reserves
identically, so one theme match was enough to push a curated pick out of its own
stall: energy served 3 of its 6 primaries, financial 3 of 6. Every review and region
check applies to the primaries, so half the curation was being discarded silently.
**Confirm:** `scripts/assert_listing_slots.py` — it fails if any stall drops a primary.
**Fixed:** primaries now take precedence; ranking reorders within them.

### A dataset a visitor cannot actually get
**MEASURED.** A Paris manufacturing primary was `is_by_request` — the visitor must ask
the provider and wait, not tick and import. `curate_locality.py` read that flag and
never filtered on it.
**Confirm:** `scripts/audit_marketplace_regions.py -c <conn>` before every event. It
judges each profile against **its own event region**, so one Frankfurt account can
check all three.
**Two traps in that audit, both of which caught me out first:**
`is_ready_for_import` is **account-local** — from a Frankfurt booth it condemns London
picks a London visitor can import perfectly well. `is_monetized` does not mean
unavailable — several picks are paid products carrying a free trial that the curated
`access` label already records. Neither is a valid cross-region signal. Only `regions`
travels.

### A reserve is not a quiet backup
**MEASURED.** A Paris **energy** visitor was offered two listings that existed nowhere
except `manufacturing/reserve`, both by-request. Stalls borrow across industries, so
**every curated pick is visitor-facing.** Never fix an unobtainable listing by demoting
it — delete it.

### A visitor is offered data from the wrong sector
A stall widens its pool by **borrowing** listings from other industries when they score
well on what the visitor typed. That is right for data that travels — weather,
boundaries, addresses, population, company registrations, industry classifications — and
wrong for sector-specific reference data. The config's example is real: scoring alone
once offered PubMed biomedical papers to a council holding policy PDFs, because both
matched on "population".
`marketplace.bucket_only` is the guard, and it is now **keyed by market profile**.
**MEASURED:** it used to be a flat list of twelve London names, so Paris and Berlin had
no protection at all while the config read as though they were covered. With the new
entries removed, Paris borrows a financial macro dataset into manufacturing and Berlin
leaks 8 protected listings across stalls once realistic visitor text is in play.
**Confirm:** `scripts/assert_listing_slots.py`. It fails if a protected listing appears
outside its own bucket, and fails if any profile has no protection at all.
**Do:** when you curate a new city, add its sector-specific listings to
`marketplace.bucket_only.<profile>`. It cannot be derived from the data — 37 London
listings sit in exactly one industry and only 11 are protected, so it is a judgement:
protect market and reference data that would be nonsense in another sector, leave the
things that genuinely travel.

### The lists are being read from a stale committed copy
The booth reads context from Snowflake and falls back to a bundle, then to markdown,
so a flat venue network degrades it rather than breaking it — but a stale fallback
looks identical to working.
**Confirm:** `/admin` — **Lists read from** must say `snowflake`. `bundle` or
`markdown` means the account read failed.

### The language setting does nothing
`event.language` is resolved from the venue, stored on every session row and shown in
the panel — but it never enters a prompt, and there is no per-language copy deck.
**MEASURED:** all five Paris sessions carry `fr`, and no POC name is French; one came
back in **German** because the model followed the company name. Treat the booth as
English-only until this is built (283 prose strings in `config.json` totalling
~32k characters, plus 5 prompts totalling ~4.2k; see the translation checklist).

### The title card reappears over a live game

**Fixed 2026-09-22 (`290f056`), recorded because the failure mode is instructive.**
The "Loco for CoCo" card was re-opened from the poll loop whenever
`!haveVisitor() && firstLoad`, and *both* of those guards read fields off server
state (`ST.visitor.first_name`, `ST.updated_at`). A single failed or partial
`/api/state` poll mid-visit therefore satisfied them and the attract screen
covered a live game — observed at the postbox on 5/4. It is now a one-way latch
(`titleDone`) that also closes on first sight of any non-attract stage.
**If you ever see it again**, it means state is being wiped rather than merely
dropped: check `/tmp/l4c.log` for `/api/state` errors, and do NOT reload — the
latch survives a poll failure but not an F5.

### The page slides downwards as CoCo answers, or the map's bottom is cut off

**Fixed 2026-09-22 (`290f056`, corrected in `b1a9f34`).** Two faults with one
cause: the chrome budget above the board.

`#bubble .msg` reserved ~2.6 lines but could grow to ~5, and `fitCanvas()` cached
that measurement, so a longer reply re-fitted the whole board mid-turn. The first
attempt pinned the bubble at six lines. That did stop the slide but was the wrong
trade — it left a permanently near-empty frame (two lines of text in a six-line
box) *and* the cached budget was still dishonest, because it was taken on the
attract screen where the tray is short; in play the tray fills with four location
cards and grows, so the board was sized too tall and its bottom edge ran
off-screen.

Now the bubble's border **hugs its text, growing to a four-line ceiling**, and
`chromeBudget()` reserves that four-line ceiling regardless of what the bubble
currently shows, measuring the tray/hud/stagebar/gaps live instead of against a
magic `+58`. The slack sits outside the border as column gap, so the board is
sized once and never moves. Verified: budget constant at 320px across 1-, 3- and
6-line replies while the bubble itself ranges 103→182px.

**The board's bottom edge was clipped at every laptop size — fixed 2026-09-22.**
This was the outstanding "check it at real booth width" item, and the answer was
yes, it was clipped. The cause is not the bubble: `fitCanvas()` first runs in
`init()`, **before the hud, tray and stagebar have any content**, so
`chromeBudget()` was understated and the board was sized too tall. MEASURED at
1440x900: budget **280 at init against 341** once the chrome exists, giving a
**620px** board where **558px** fits. Idle that is invisible, because the bubble
sits below its four-line ceiling and the slack absorbs it — which is exactly why
it survived every previous check. But any reply reaching four lines pushed the
bottom edge **57px off-screen at 1280x800, 1440x900 and 1512x982 alike**.

`render()` now re-fits **once**, as soon as the hud and tray have real height.
That is not a mid-turn re-fit: it happens before the visitor has a reply to read
and never again. After the fix, a four-line reply leaves the bottom edge at
896/900, 978/982 and 796/800.

Note for anyone verifying this: a naive "clipped" check comparing `#wrap` against
`innerHeight` reports **false clean**, because `html` and `body` are
`overflow:hidden` — the document never scrolls, so the overflow is silently
cropped rather than measurable. Compare `$('cv').getBoundingClientRect().bottom`
against `innerHeight` instead.

**Long replies are now paginated, not scrolled (2026-09-22).** Past the four-line
ceiling the reply is cut into pages and the visitor presses **MORE 1/2 ▸** to
advance; the box never changes height, so paging through one reply cannot slide
the board. Three things make that hold, and each was measured rather than assumed:

- `splitPages()` measures the **real font against the real box width** with canvas
  `measureText`. The old "99 chars/line" figure holds only at the full 1056px rail
  — the panel width varies, and at 550px the same reply needs six pages, not three.
- While a reply has more than one page, `#bubble.paged .msg` pins the message to
  the four-line height and the MORE control keeps its slot (invisible on the last
  page). Without both, the final — usually short — page shrank the bubble and slid
  the board up: measured 159px, 159px, **146px** across three pages before the fix,
  constant **160px** after.
- `chromeBudget()` reserves the MORE control unconditionally, because it appears
  mid-turn and a budget that counted it only when visible left the board ~20px too
  tall on every long reply.

Verified in headless Chromium at 420/550/760/1100/1400px: no page exceeds four
lines, nothing is clipped, bubble height is constant across all pages, and **every
character survives** — including a 500-character unbreakable token, and all 75
visitor-facing config strings. A window resize mid-read re-cuts the pages and
resumes on the page holding the text being read (measured: never skips ahead).

`max-height`/`overflow-y:auto` remain only as a safety net for a page whose
measured wrap overruns by a hair. Still do **not** "tidy" the CSS to
`overflow:hidden` — with pagination in place it should never trigger, but if a
measurement is ever off it would silently truncate rather than scroll.

### Half of the workshop brief is invisible

**Fixed 2026-09-22 (`b1a9f34`).** `LET COCO CHOOSE` composes a sentence
(`Build the most impactful thing for {industry} using {held} joined with {joined}`)
that routinely runs past 100 characters, and `#c-compose` was an
`<input type="text">` — a single-line field that cannot wrap, so the tail simply
scrolled out of sight and the visitor saw half of the brief being submitted on
their behalf. It is a wrapping `<textarea rows="2">` now. Enter still submits;
shift+Enter inserts a newline. Related trap in the same area: `.cchoose` is
`font:700 12px/1` with fixed padding, so a *button* label long enough to wrap
would clip the same way — relevant the moment the UI is translated.

### CoCo has no voice inside a location

**Fixed 2026-09-22 (`290f056`).** The bubble used to be hidden along with the
work tray whenever a POV location opened (`#wrap.povfocus`), to buy the interior
~150px. Only the tray drops now. If an interior ever looks crushed, that is
`sizePovCard()` honouring the panel's floor first by design — the room takes a
tighter crop rather than the CONFIRM button scrolling out of reach.

---

## After the event

### The account is destroyed with the leads still in it
Event accounts are assigned from a pool per event and torn down afterwards. Nothing
survives.
**Do:** run `sql_statements/05-export-before-teardown.sql` and save the output. More
than once if the event runs over several days. It ends with a count so you can check
the export against the table.
