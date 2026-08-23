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
w('| 3. The marketplace | Ticks data to join | `industries.<key>.marketplace` '
  'as the fallback, but **live listings first** | Partly - see below |')
w('| 4. The workshop | Types one line describing the MVP | Free text | No - '
  'but the archetype it maps to is |')
w('| 5. The postbox | Posts it | - | - |')
w('')
w('The two runtime decisions are: which live Marketplace listings match the '
  'industry keywords, and which of the %d archetypes the model picks from the '
  "visitor's one-line description. Everything else is ours to set." % len(arch))
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
w('POSTBOX   ->  blueprint (.docx today, HTML alongside it) + QR + email')
w('```')
w('')

# --------------------------------------------------------- per industry
w('## Per industry')
w('')
w('For each industry: what the library offers, what the marketplace offers as '
  'the curated fallback, and the keywords used to find live listings. The '
  'keywords are the lever on live results - a thin keyword list is why an '
  'industry falls back to the curated list.')
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
    w('**Marketplace - curated joins (the fallback when live search is thin)**')
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

io.open(os.path.join(HERE, 'decision_tree.md'), 'w',
        encoding='utf-8').write('\n'.join(O) + '\n')
print('wrote decision_tree.md  (%d lines)' % len(O))
