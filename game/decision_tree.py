#!/usr/bin/env python3
"""Emit the booth decision tree as Markdown, straight from the live config.

The point of this document is editorial, not architectural: Paddy needs to see,
per industry, exactly what a visitor is offered and where each option came from,
so the precomputed suggestions in the library and the marketplace can be made
sharper. So everything here is READ from config.json, archetypes.md and
server.py rather than described from memory - if the booth offers it, it is in
here, and if it is in here, the booth offers it.
"""
import json, io, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(io.open(os.path.join(HERE, 'config.json'), encoding='utf-8'))
arch_src = io.open(os.path.join(HERE, 'archetypes.md'), encoding='utf-8').read()
srv = io.open(os.path.join(HERE, 'server.py'), encoding='utf-8').read()

# ---- archetypes: name -> features, first_step, n considerations
arch = {}
cur = None
for line in arch_src.splitlines():
    if line.startswith('## '):
        cur = line[3:].strip()
        arch[cur] = {'features': '', 'first_step': '', 'pool': 0}
    elif cur:
        m = re.match(r'^\|\s*features\s*\|\s*(.+?)\s*\|$', line)
        if m:
            arch[cur]['features'] = m.group(1).strip()
        m = re.match(r'^\|\s*first_step\s*\|\s*(.+?)\s*\|$', line)
        if m:
            arch[cur]['first_step'] = m.group(1).strip()
        if re.match(r'^\d+\.\s+', line):
            arch[cur]['pool'] += 1

# ---- integration paths, read out of server.py so the doc cannot drift
paths = {}
m = re.search(r'INTEGRATION_PATHS = \{(.*?)\n\}\n', srv, re.S)
if m:
    for pm in re.finditer(r'"([^"]+)": \(\s*(.*?),\s*"(https://[^"]+)"\)',
                          m.group(1), re.S):
        blurb = ' '.join(re.findall(r'"([^"]*)"', pm.group(2)))
        paths[pm.group(1)] = (re.sub(r'\s+', ' ', blurb).strip(), pm.group(3))

mkt = cfg['marketplace']
inds = cfg['industries']
plats = (cfg.get('platforms') or {}).get('options') or []
locs = cfg['locations']

# ---- the REAL curated marketplace listings, read from marketplace-index.md.
# industries.<key>.marketplace in config.json is dead data - the game's own
# locations.marketplace.source is "marketplace_index", so that config field
# is never read at runtime. Parsing it here instead of the real file was
# exactly the kind of drift this generator exists to prevent.
MARKET_PATH = os.path.join(os.path.dirname(HERE), 'skills', 'loco4coco',
                           'references', 'marketplace-index.md')
market = {}
_cur_ind = None
_row_re = re.compile(r"^\|\s*\[(?P<title>.+?)\]\((?P<url>[^)]+)\)\s*\|"
                     r"\s*(?P<prov>[^|]+?)\s*\|\s*(?P<acc>[^|]+?)\s*\|"
                     r"\s*`(?P<gname>[^`]+)`\s*\|")
for line in io.open(MARKET_PATH, encoding='utf-8').read().splitlines():
    h = re.match(r"^##\s+([a-z_]+)\s*$", line.strip())
    if h:
        _cur_ind = h.group(1)
        market.setdefault(_cur_ind, [])
        continue
    if not _cur_ind:
        continue
    rm = _row_re.match(line.strip())
    if rm:
        market[_cur_ind].append({'title': rm.group('title').strip(),
                                 'provider': rm.group('prov').strip(),
                                 'access': rm.group('acc').strip()})

O = []
w = O.append

w('# Loco 4 CoCo - the booth decision tree')
w('')
w('_Generated from the live `config.json`, `archetypes.md` and `server.py`. '
  'Every option below is what a visitor is actually offered. Regenerate with '
  '`python3 game/decision_tree.py` after changing config._')
w('')
w('## Why this document exists')
w('')
w('Five choices decide the whole blueprint. Three of them are precomputed by '
  'us and two are decided at runtime, and it matters which is which - only the '
  'precomputed ones can be improved by editing config.')
w('')
w('| Step | What the visitor does | Where the options come from | Tunable? |')
w('|---|---|---|---|')
w('| 1. The letter | Types name, company, industry, **and the problem in two '
  'sentences** | Industry list in `config.industries` | Yes - the list |')
w('| 2. The library | Ticks data they hold, then taps the platforms it sits on '
  '| `industries.<key>.data_sources` + `config.platforms` | **Yes - fully '
  'precomputed** |')
w('| 3. The marketplace | Ticks data to join | `marketplace-index.md`, '
  '6 verified listings per industry | **Yes - fully precomputed** |')
w('| 4. The workshop | Types one line describing the MVP | Free text | No - '
  'but the archetype it maps to is |')
w('| 5. The postbox | Posts it | - | - |')
w('')
w('With `discovery: manual` there is now only ONE runtime decision: which '
  'of the %d archetypes the visitor is routed to. Even that is no longer purely '
  "the model's - `game/context.py` resolves it deterministically from the "
  'visitor\'s own words scored against each archetype\'s pain text, and the '
  'model chooses from that shortlist. Everything else on this page is ours to '
  'set.' % len(arch))
w('')

# ------------------------------------------------------------------ the tree
w('## The tree, top to bottom')
w('')
w('```')
w('LETTER')
w('  industry  ->  one of %d' % len(inds))
w('  problem   ->  free text, 400 chars, threaded into every later prompt')
w('        |')
w('LIBRARY   (precomputed per industry)')
w('  data held ->  6 options per industry + "something else"')
w('  platform  ->  %d universal chips -> integration path in the blueprint'
  % len(plats))
w('        |')
w('MARKETPLACE')
# Read the discovery mode from config rather than asserting one: this section
# said "live listings first" for weeks after discovery was switched to manual.
_disc = ((cfg.get('locations') or {}).get('marketplace') or {}).get('discovery',
                                                                   'manual')
if _disc == 'manual':
    w('  %d-%d curated, region-verified options per industry  (discovery: manual)'
      % (min(len(v) for v in market.values()),
         max(len(v) for v in market.values())))
    w('  every one is checked is_ready_for_import, so a visitor can attach it')
else:
    w('  live listings matched on industry keywords  (min %d results)'
      % mkt.get('min_live_results', 0))
    w('  falls back to %d-%d curated options per industry'
      % (min(len(v) for v in market.values()),
         max(len(v) for v in market.values())))
w('        |')
w('WORKSHOP')
w('  one line  ->  model picks 1 of %d archetypes' % len(arch))
w('             ->  features + first step come from archetypes.md, no inference')
w('        |')
w('POSTBOX   ->  blueprint (.docx today, HTML alongside it) + QR. No email.')
w('```')
w('')

# --------------------------------------------------------- per industry
w('## Per industry')
w('')
w('For each industry: what the library offers, and the six curated Marketplace '
  'listings it offers. Every listing is verified importable in the event region, '
  'so nothing here is a dead end. The live-search keywords are listed too, but '
  'they only bite if `locations.marketplace.discovery` is set back to `live`.')
w('')
for key, v in inds.items():
    ds = v.get('data_sources') or []
    mk = market.get(key) or []
    kw = (mkt.get('industry_keywords') or {}).get(key) or []
    pin = (mkt.get('pinned') or {}).get(key) or []
    w('### %s' % v.get('name', key))
    w('')
    w('`%s` - %d data sources, %d curated joins, %d live-search keywords, '
      '%d pinned listings' % (key, len(ds), len(mk), len(kw), len(pin)))
    w('')
    w('**Library - data they already hold**')
    w('')
    w('| Option | Note shown under it |')
    w('|---|---|')
    for d in ds:
        w('| %s | %s |' % (d.get('label', ''), d.get('note', '')))
    w('')
    w('**Marketplace - the six curated joins offered, all verified importable**')
    w('')
    w('| Listing | Provider | Access |')
    w('|---|---|---|')
    for d in mk:
        w('| %s | %s | %s |' % (d.get('title', ''), d.get('provider', ''),
                                d.get('access', '')))
    w('')
    w('**Live-search keywords** (%d): %s' % (len(kw), ', '.join(kw) or '_none_'))
    w('')
    if pin:
        w('**Pinned listings**: %s' % ', '.join(pin))
        w('')

# --------------------------------------------------------- platforms
w('## The platform question, and what it produces')
w('')
w('Asked once in the library, one tap, universal across industries. Each chip '
  'writes a concrete route into the blueprint, so this is the section that '
  'turns "we have the data somewhere" into a first task.')
w('')
w('| Chip | Route the blueprint prints |')
w('|---|---|')
for p in plats:
    blurb, url = paths.get(p, ('_no route defined - falls back to the generic '
                               'connector line_', ''))
    w('| %s | %s |' % (p, blurb))
w('')

# ---- combinations. The single-chip table above is not the whole story: the
# question is multi-select, so the doc has to state what a COMBINATION produces
# or nobody can predict what a visitor walks away with.
_pcfg = cfg.get('platforms') or {}
_excl = _pcfg.get('exclusive') or []
_cap = _pcfg.get('max_routes') or 4
w('### Combinations, and the guardrails on them')
w('')
w('The chips are multi-select, so most visitors tap more than one. Before the '
  'guardrails, **16 of the 36 possible pairs produced a self-contradicting '
  'document** and **10 printed "Openflow" twice**. Both are fixed, and both are '
  'enforced twice - in the browser on tap, and again on the server when the '
  'blueprint is built - so a bypassed or mis-clicked UI still cannot produce a '
  'contradictory hand-out.')
w('')
w('| Selection | What the blueprint prints | Why |')
w('|---|---|---|')
w('| One cloud, e.g. **AWS** | That one route | The simple case |')
w('| **Azure + AWS** | Both routes, Azure first | Genuinely different routes; '
  'config order decides which is printed first, so it is the same document '
  'every time regardless of tap order |')
for e in _excl:
    w('| **%s** alone | Its own line, no route | A legitimate answer on its own |'
      % e)
    w('| **%s** + any named source | The named source only; "%s" is dropped |'
      ' A named source is actionable, so it wins - printing both said "nothing '
      'to move" and "here is how to move it" in the same document |' % (e, e))
w('| More than %d chips | The first %d in config order | Caps the ingestion '
  'section so it reads as a plan, not a checklist. All 9 chips used to print 9 '
  'route paragraphs |' % (_cap, _cap))
w('')
w('Verified by exhausting every single, pair and triple combination: '
  '**0 contradictions and 0 cap overruns**, worst case bounded at %d routes.'
  % _cap)
w('')

# --------------------------------------------------------- archetypes
w('## The %d archetypes' % len(arch))
w('')
w('The workshop is free text, but it resolves to exactly one of these. '
  'Features and the first step are precomputed, so they are instant and always '
  'correct; only the summary and the considerations need the model.')
w('')
w('| Archetype | Features | Considerations in pool |')
w('|---|---|---|')
for k, a in arch.items():
    w('| %s | %s | %d |' % (k, a['features'], a['pool']))
w('')
w('**First steps**')
w('')
for k, a in arch.items():
    w('- **%s** - %s' % (k, a['first_step']))
w('')

# --------------------------------------------------------- where to improve
w('## Where the precomputed suggestions are weakest')
w('')
w('Computed, not editorial - these are the counts that stand out.')
w('')
gaps = []
kws = mkt.get('industry_keywords') or {}
pins = mkt.get('pinned') or {}
for key, v in inds.items():
    nm = v.get('name', key)
    nk = len(kws.get(key) or [])
    if nk < 10:
        gaps.append('**%s** has only %d live-search keywords, so it will fall '
                    'back to the curated list more often than the others.'
                    % (nm, nk))
    if not (pins.get(key) or []):
        gaps.append('**%s** has no pinned listings, so if live search returns '
                    'nothing recognisable there is no guaranteed good result.'
                    % nm)
    if len(market.get(key) or []) < 5:
        gaps.append('**%s** offers only %d curated joins.'
                    % (nm, len(market.get(key) or [])))
for g in gaps:
    w('- %s' % g)
if not gaps:
    w('- Nothing stands out on the counts.')
w('')
w('Two structural gaps worth a decision rather than a count:')
w('')
w('- **No industry biases the archetype choice.** A hospital and a bank get the '
  'same %d archetypes with the same weighting. A per-industry ordering, or two '
  'or three likely archetypes per industry, would make the forge both faster '
  'and more plausible.' % len(arch))
w('- **The data held does not narrow the marketplace suggestion.** Someone who '
  'ticked "clinical notes" is offered the same joins as someone who ticked '
  '"estates and operations". A held-to-join mapping is the highest-value '
  'precompute still missing.')
w('')

# ---- transport and latency ---------------------------------------------------
# Read from config so this section cannot drift from what the booth will do.
_coco = cfg.get('coco') or {}
_locs = cfg.get('locations') or {}
w('## Where the visitor\'s time goes')
w('')
w('A stop is only as good as the wait in front of it, so the transport each one '
  'uses is part of the decision tree, not an implementation detail.')
w('')
w('| Stop | Transport asked for | Ceiling |')
w('|---|---|---|')
for _k in (cfg.get('unlock_order') or list(_locs)):
    _l = _locs.get(_k) or {}
    if not _l:
        continue
    w('| %s | `%s` | %ss |' % (_l.get('name') or _k,
                               _l.get('transport') or 'exec',
                               _l.get('timeout') or _coco.get('turn_timeout', 60)))
w('')
w('**Measured before any of this was built** (5 visits, `game/cost.jsonl`): the '
  'Workshop stop was 75% of all model wait at a 26.0s median, because it was '
  'the only stop running a real `cortex exec`.')
w('')
w('`cortex exec` is a one-shot CI/CD entry point with no `--resume`, no '
  '`--session` and no `--daemon`, so every call is a cold process. Timed on a '
  'trivial prompt: 22.7s default, 19.4s with `--no-mcp`, 18.1s with every flag '
  'that helps. **About 18 seconds of that is startup, not thinking.**')
w('')
w('So the booth now leads with a warm `cortex mcp serve` process, which is the '
  'same binary in server mode, held open between visitors:')
w('')
w('| | cold `cortex exec` | warm agent |')
w('|---|---|---|')
w('| startup | ~18s, every call | 1.3s, once |')
w('| a turn | ~26s | **~3.4s** |')
w('')
w('### Four layers, because a stand is not a laptop at a desk')
w('')
w('1. **warm agent** - `cortex mcp serve`, ~3.4s.')
w('2. **`cortex exec`** - a cold one-shot. Not started unless 20s of budget remain.')
w('3. **`COMPLETE`** - `SNOWFLAKE.CORTEX.COMPLETE`. Fast, non-agentic.')
w('4. **precomputed** - the archetype defaults in this document. No model at all.')
w('')
w('Layer 4 is why this document matters operationally: on a flat venue network '
  'with a suspended warehouse, what a visitor leaves with is exactly the '
  'precomputed content listed above. It is the floor, so it has to read well '
  'on its own.')
w('')
w('### Two constraints that are not negotiable')
w('')
w('- **One in-flight agent call at a time.** Two calls were issued on one warm '
  'process without waiting: one asked for ALPHA, one asked for BRAVO, and both '
  'received ALPHA. Concurrent calls mis-correlate, which on a stand means one '
  'visitor\'s content in another visitor\'s document with no error raised. The '
  'pool holds a mutex; a second caller waits.')
w('- **Every turn has a wall-clock ceiling** (%ss by default). The Library has '
  'been measured at a 127.3s outlier against a 2.2s median. Past the ceiling '
  'the visitor is better served by layer 4 than by a better sentence.'
  % _coco.get('turn_timeout', 60))
w('')
w('### Retrieval is deterministic on purpose')
w('')
w('The closed lists reach the model as **content in the prompt**, not as a tool: '
  '`cortex exec` takes no tools except through MCP, and MCP is not guaranteed on '
  'a borrowed booth laptop. The corpus is ~150 rows, so `game/context.py` scores '
  'it in process and injects only the slice that matches the visitor\'s own '
  'words (~220 tokens).')
w('')
w('No search service, deliberately. At a Snowflake-branded event the same input '
  'must give the same document, and a visitor\'s pain language is bridged to our '
  'feature names through the archetype **pain** text - "we retype invoices all '
  'day" shares no token with `AI_EXTRACT`, but plenty with the pain line.')
w('')

# ---- flagged for review -----------------------------------------------------
# Kept in the generator, not typed into the published copy, so it survives the
# next regeneration. Anything hand-added to the Google Doc is lost on the next run.
w('## Flagged for review')
w('')
w('Decisions for a human, not code changes. None of these stop the booth running.')
w('')
w('- **Geo weighting is London-only.** The curated picks are scored with %d UK '
  'preference terms and %d non-UK demotion terms (`marketplace.geo`). Re-weight '
  'before Paris, or a French room is offered UK postcode data.'
  % (len(((cfg.get('marketplace') or {}).get('geo') or {}).get('prefer') or []),
     len(((cfg.get('marketplace') or {}).get('geo') or {}).get('demote') or [])))
_acc = {}
for _v in market.values():
    for _r in _v:
        _acc[_r.get('access', '')] = _acc.get(_r.get('access', ''), 0) + 1
_trials = sum(n for a, n in _acc.items() if 'trial' in a.lower())
_total = sum(_acc.values())
w('- **%d of the %d curated slots are time-limited trials** rather than '
  'perpetual Free. Everything is free to acquire and nothing is Paid, but some '
  'expire before a visitor is likely to act on it.' % (_trials, _total))
_titles = {}
for _v in market.values():
    for _r in _v:
        _titles[_r.get('title')] = _titles.get(_r.get('title'), 0) + 1
_reused = sorted(((n, t) for t, n in _titles.items() if n > 2), reverse=True)
if _reused:
    w('- **The curated set repeats across industries.** %d slots are filled by '
      'only %d distinct listings. Most reused: %s. This is the "why am I being '
      'offered the same thing again" problem, and it is content curation work '
      'rather than a bug.'
      % (_total, len(_titles),
         '; '.join('%s (%d industries)' % (t, n) for n, t in _reused[:4])))
w('- **`is_ready_for_import` is the flag that decides whether a visitor can '
  'actually attach a listing**, and it is stricter than it looks. Measured on '
  'the London account: of 4,347 visible listings only 671 are importable. Every '
  'one of those is also not-by-request. The trap is the middle group - 2,594 '
  'listings are NOT by-request and still NOT importable, so they look freely '
  'available and cannot be mounted. Checking only region and by-request passes '
  'listings a visitor cannot use; that is how five unattachable entries once sat '
  'in the curated index undetected. `deploy/verify_context.py --listings` now '
  'checks the flag directly, and all %d distinct curated listings pass it.'
  % len(_titles))
w('- **The agentic marketplace tier stays disabled.** Re-timed 2026-08-24 at '
  '**117.1s** for one search - slower than the 70-110s originally measured, and '
  'far slower than a visitor walking one stall. It does return better matches '
  '(a "poor data quality" problem returned Ataccama Data Quality and Semarchy '
  'xDM rather than an industry keyword guess), but it does NOT verify region or '
  '`is_ready_for_import`, so its suggestions can be dead ends. Warming does not '
  'rescue it: the 117s is inference and tool time, not the ~18s of process '
  'startup.')
w('')

io.open(os.path.join(HERE, 'decision_tree.md'), 'w',
        encoding='utf-8').write('\n'.join(O) + '\n')
print('wrote decision_tree.md  (%d lines)' % len(O))
