# Sharing Loco for CoCo with another SE, or another city

Everything a second person needs to run this, and everything they need to change
when the city changes. Read [CONSTRAINTS.md](CONSTRAINTS.md) first — it says what
the event is and what the venue makes impossible.

There are two separate questions here, and conflating them is the usual mistake:

1. **Sharing the activation** — someone else runs the booth on their laptop.
2. **Sharing the context** — everyone's booth names the same listings, guides and
   features, without everyone pulling a git branch.

---

## 1. Sharing the activation

The repo is public: `github.com/sfc-gh-pgardner/loco4coco`, Apache 2.0. It is a Python
standard-library server plus a browser canvas — no npm, no build step, nothing
hosted.

```bash
git clone https://github.com/sfc-gh-pgardner/loco4coco.git
cd loco4coco
python3 deploy/bootstrap.py --target LONDON --connection <their-connection>
cd game && python3 server.py
```

Full first-run detail is in [SETUP.md](SETUP.md). Two things that bite:

- **They need their own Snowflake connection.** Nothing works without one — this
  is why the shared context lives in Snowflake rather than in an MCP server.
- **They do not need MCP.** `plugin.json` declares no `mcpServers`, deliberately.
  The warm agent is `cortex mcp serve`, which is the `cortex` binary itself in
  server mode, so it needs no per-laptop registration. A borrowed laptop with
  managed settings that disable MCP servers still runs the booth.

### Pre-flight, in order

```bash
python3 deploy/verify_context.py --all      # closed lists, links, live listings
cd game && python3 server.py                # watch for "warm agent ready"
```

`verify_context.py` exits with the number of failures, so it gates cleanly. Run
it the morning of the event, not the week before: it is the check that catches a
Marketplace listing that has been withdrawn or a doc URL that has moved.

---

## 2. Sharing the context

The closed lists — 48 listing rows over 30 distinct listings, 40 guides, 53
features, 9 archetypes, 9 integration routes — exist in three places at once, and
that is on purpose.

| Layer | Where | Role |
|---|---|---|
| 1 | `LOCO4COCO.BOOTH.{LISTINGS,GUIDES,FEATURES,ARCHETYPES,ROUTES}` | current, shareable |
| 2 | `skills/loco4coco/references/context-bundle.json` | committed, offline |
| 3 | `skills/loco4coco/references/*.md` | source of truth, human-editable |

`game/context.py` tries them in that order and falls through on any failure, so a
flat venue network degrades the booth instead of breaking it. All three must agree
— `verify_context.py` asserts it.

### Changing the content

Edit the markdown. Then, in this order:

```bash
python3 game/context.py --bundle                    # regenerate layer 2
python3 deploy/load_context.py --check              # parse, report, write nothing
python3 deploy/load_context.py --connection <conn>  # replace layer 1
python3 deploy/verify_context.py --all              # prove all three agree
```

Committing the bundle is deliberate: drift between it and the markdown then shows
up in review, rather than silently on the stand.

### Giving another account the same lists

The tables are ordinary tables, so this is ordinary Snowflake sharing:

```sql
CREATE SHARE LOCO4COCO_CONTEXT;
GRANT USAGE ON DATABASE LOCO4COCO TO SHARE LOCO4COCO_CONTEXT;
GRANT USAGE ON SCHEMA LOCO4COCO.BOOTH TO SHARE LOCO4COCO_CONTEXT;
GRANT SELECT ON LOCO4COCO.BOOTH.LISTINGS    TO SHARE LOCO4COCO_CONTEXT;
GRANT SELECT ON LOCO4COCO.BOOTH.GUIDES      TO SHARE LOCO4COCO_CONTEXT;
GRANT SELECT ON LOCO4COCO.BOOTH.FEATURES    TO SHARE LOCO4COCO_CONTEXT;
GRANT SELECT ON LOCO4COCO.BOOTH.ARCHETYPES  TO SHARE LOCO4COCO_CONTEXT;
GRANT SELECT ON LOCO4COCO.BOOTH.ROUTES      TO SHARE LOCO4COCO_CONTEXT;
GRANT SELECT ON LOCO4COCO.BOOTH.CONTEXT_MANIFEST TO SHARE LOCO4COCO_CONTEXT;
ALTER SHARE LOCO4COCO_CONTEXT ADD ACCOUNTS = <their_account>;
```

They point `context.py` at their own database name if it differs. Do **not** share
`SESSIONS` or `TURNS`: those hold visitor names and companies.

### Proving two laptops agree

`CONTEXT_MANIFEST` holds a SHA-256 per source file, so parity is checkable without
diffing content:

```sql
SELECT SOURCE_FILE, LEFT(CONTENT_SHA, 12) AS SHA, ROW_COUNT, LOADED_AT, GIT_REF
FROM LOCO4COCO.BOOTH.CONTEXT_MANIFEST ORDER BY SOURCE_FILE;
```

Same SHA as `shasum -a 256 skills/loco4coco/references/<file>` means the account
matches the laptop.

---

## 3. Taking it to another city

Paris is a copy-deck swap, not a rebuild. That was a design constraint from the
start and it is worth not spending it.

**What changes:**

- `game/config.json` → `event.city`, `event.language`.
- The visitor-facing copy: everything the visitor reads lives in `game/config.json`
  (intro, the letter, the locations, the sovereignty lines), so a French booth is a
  translation of that one file and never touches logic.
- `deploy/manifest.yml` → a new target with that account, `city`, `language` and
  its own `monitor_notify_user`. That last one is deliberately not defaulted: a
  resource monitor pointed at a non-existent user fails outright, which beats one
  that silently warns nobody.
- `marketplace.geo.prefer` / `geo.demote` in `config.json`. These are currently
  weighted for a UK audience — 19 preferred terms, 20 demoted. A Paris booth wants
  French and EU terms promoted, or it will offer UK postcode data to a room that
  cannot use it.

**What does not change:** the archetypes, the features, the guides, the transport
chain, the game.

**The one thing to re-verify per city:** listing availability is regional.
`verify_context.py --listings` runs `SHOW AVAILABLE LISTINGS` against *their*
account, so run it there — a listing visible in `AWS_EU_WEST_2` may not be visible
elsewhere, and `REGIONS` in the table records what we knew in London.

---

## 4. What to watch on the day

| Symptom | Cause | What to do |
|---|---|---|
| First visitor waits ~20s | Warm agent did not start | Check console for `warm agent FAILED`; it falls through to `cortex exec`, so the booth still works |
| Every turn slow, not just the first | Running on layer 2 (`cortex exec`) | `coco.warm_agent` in config, or `cortex mcp serve` unavailable |
| Blueprint names no features | Closed list empty — all three context layers failed | `python3 deploy/verify_context.py`; layer 3 is in the repo, so this means a broken checkout |
| A visitor's document mentions someone else's company | **Stop the booth.** | This should be impossible: the pool serialises calls precisely to prevent it. Capture `game/cost.jsonl` and the console before restarting |
| Warehouse credits climbing while idle | Not the agent | An idle warm process holds a session, not a warehouse. Look at `LOCO4COCO_RM` and `TURNS` |

Costs are capped by `LOCO4COCO_RM` (20 credits, notify at 75/90, suspend at 100),
defined in `deploy/hooks/post_hook.sql` because resource monitors are not a
supported DCM `DEFINE` entity.
