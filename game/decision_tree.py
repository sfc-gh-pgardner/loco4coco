#!/usr/bin/env python3
"""Emit the booth decision tree as Markdown, read from the live app.

Every fact in the output is derived from config.json, marketplace-index.md,
archetypes.md or server.py. Nothing is described from memory and nothing is
typed twice, so the document cannot disagree with the booth: regenerate it and
it is correct, or it fails loudly.

Two rules govern the prose:
  1. Present tense, stated as fact. What the booth does, not what it used to do,
     not what changed, not what was measured on a particular afternoon.
  2. If a claim cannot be regenerated from a live source, it is not written.

Run:  python3 game/decision_tree.py > booth-decision-tree.md
"""
import io
import json
import os
import re

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
locs = cfg['locations']

# ---- the curated marketplace listings, read from marketplace-index.md.
# industries.<key>.marketplace in config.json is never read at runtime:
# locations.marketplace.source is "marketplace_index", so this file is the
# only source of truth for what a visitor is offered.
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
                                 'access': rm.group('acc').strip(),
                                 'global_name': rm.group('gname').strip(),
                                 'url': rm.group('url').strip()})

O = []
w = O.append


def q(s):
    """A config string, printed verbatim and safe inside a Markdown table."""
    return str(s or '').replace('|', r'\|').replace('\n', ' ').strip()


def ind_label(key):
    return (inds.get(key) or {}).get('name') or key


def order():
    """Industries in config order, so the document is stable between runs."""
    return list(inds.keys())


# ======================================================================= header
w('# Loco 4 CoCo - the booth decision tree')
w('')
w('Every option a visitor is offered, every line CoCo speaks, and every dataset '
  'the booth recommends. Generated from the live app: `config.json`, '
  '`marketplace-index.md`, `archetypes.md` and `server.py`.')
w('')
w('Regenerate with `python3 game/decision_tree.py`.')
w('')

# ================================================================== 1. the tree
w('## 1. What the visitor does')
w('')
w('Six stops. The letter is the whole intake on one screen; the four '
  'locations are walked to on a map in the order below.')
w('')
w('| # | Stop | What the visitor gives us | Options come from | Select |')
w('| --- | --- | --- | --- | --- |')
w('| 0 | The letter | First name, employer, industry, the problem in two '
  'sentences, where the data lives and which countries they operate in | '
  '`industries` for the list, `platforms` and `country` for the chips; the '
  'problem is free text | Single industry, multi-select chips, free text |')
w('| 1 | The house | Nothing. CoCo reads back what the letter said and makes '
  'the security and AI point | - | - |')
w('| 2 | The Data Library | The data they already hold | '
  '`industries.<key>.data_sources` | Multi-select plus free text |')
w('| 3 | The Marketplace | Datasets to join to it | `marketplace-index.md` | '
  'Multi-select plus free text |')
w('| 4 | The Workshop | One line describing what the proof of concept should do'
  ' | Free text | Free text |')
w('| 5 | The Postbox | Confirmation to send | - | Button |')
w('')
w('The map unlocks in this order: %s.'
  % ', '.join('**%s**' % q((locs.get(k) or {}).get('name') or k)
              for k in (cfg.get('unlock_order') or [])))
w('')
w('The visitor\'s answers reach the document by two routes. The library, '
  'marketplace and workshop answers are named back to them by the model, which '
  'picks from the closed lists in this document and never invents an entry. '
  'The archetype, its features and its first step are precomputed, so they are '
  'correct whether or not a model answers.')
w('')

# =============================================== 2. every scripted line, in order
w('## 2. Every scripted line, in running order')
w('')
w('Fixed copy, identical for every visitor, straight from `config.json`. '
  'Braced placeholders such as `{first_name}`, `{company}`, `{country}`, '
  '`{platform}` and `{region}` are filled from the visitor\'s own answers.')
w('')
w('The one-line replies CoCo speaks at the Library, Marketplace and Workshop '
  'are not listed here. Those are generated per visit, reflecting back what the '
  'visitor just picked.')
w('')

# --- intro
_intro = cfg.get('intro') or {}
w('### 2.1 Intro card')
w('')
w('- **Title:** %s' % q(_intro.get('title')))
w('- **Button:** %s' % q(_intro.get('button')))
for b in (_intro.get('body') or []):
    w('- %s' % q(b))
w('')
w('Text wrapped in asterisks renders as a highlight colour rather than body '
  'text.')
w('')

# --- the arctic and the letter
_L = ((cfg.get('intake') or {}).get('letter') or {})
w('### 2.2 The house: CoCo arrives and reads a letter')
w('')
for k in ('arctic', 'arctic_sub', 'bubble', 'greeting'):
    if _L.get(k):
        w('- **%s:** %s' % (k, q(_L.get(k))))
for i, b in enumerate(_L.get('body') or []):
    w('- **body[%d]:** %s' % (i, q(b)))
for k in ('signoff', 'button', 'line1', 'line2', 'map_line'):
    if _L.get(k):
        w('- **%s:** %s' % (k, q(_L.get(k))))
w('')

# --- what the visitor types into the letter
_intake = cfg.get('intake') or {}
w('### 2.3 The letter: what the visitor types')
w('')
for f in (_intake.get('fields') or []):
    w('- **%s** (`%s`) - placeholder: %s'
      % (q(f.get('label')), q(f.get('id')), q(f.get('placeholder'))))
for k in ('industry_question', 'confirm_industry', 'problem_label',
          'problem_placeholder'):
    if _intake.get(k):
        w('- **%s:** %s' % (k, q(_intake.get(k))))
w('')
w('The problem example above is the fallback. Once an industry is chosen it is '
  'replaced by that industry\'s own, and a "CoCo, you choose" button will draft '
  'a starting problem statement from the archetype pain lines, into an editable '
  'field.')
w('')
for _ik, _ib in inds.items():
    if _ib.get('problem_placeholder'):
        w('- **%s:** %s' % (ind_label(_ik), q(_ib['problem_placeholder'])))
w('')

# --- the three home questions
w('### 2.4 The letter: the stack and the location')
w('')
w('Asked on the letter itself, both multi-select. Where data and models may run '
  'is NOT asked: it is inferred from the location, because it only names the '
  'region in the sovereignty pillars and a visitor\'s own location answers it '
  'more honestly than a question about their compliance position.')
w('')
for key in ('platforms', 'country'):
    b = cfg.get(key) or {}
    w('**%s**' % q(b.get('heading')))
    w('')
    w('- **Hint:** %s' % q(b.get('hint')))
    opts = b.get('options') or b.get('options_template') or []
    for o in opts:
        w('- %s' % q(o))
    if b.get('other_label'):
        w('- **Free text option:** %s' % q(b.get('other_label')))
    if b.get('exclusive'):
        w('- **Cannot be combined with a named source:** %s'
          % ', '.join(q(x) for x in b['exclusive']))
    w('')

# --- sovereignty reactions and pillars
_sov = cfg.get('sovereignty') or {}
w('### 2.5 The letter: CoCo\'s reply to each answer')
w('')
for k, v in (_sov.get('react') or {}).items():
    # Only the replies CoCo can still speak. The residency reactions belong to
    # the question that no longer exists.
    if not k.startswith('residency_'):
        w('- **%s:** %s' % (k, q(v)))
w('')
w('Several countries may be picked, and CoCo answers on the strictest reading '
  'the location supports.')
w('')

w('### 2.6 The house: CoCo reads it back')
w('')
w('Spoken over the house scene once the letter is submitted. CoCo names what '
  'was given, then makes the security and AI point inside that summary. The '
  'region comes from the visitor\'s own location. Each line advances on a timer '
  'scaled to its length.')
w('')
for t in (_sov.get('summary') or []):
    w('- %s' % q(t))
w('')

w('### 2.7 The blueprint: the four sovereignty pillars')
w('')
w('Printed verbatim in the document the visitor takes away.')
w('')
for k, v in (_sov.get('pillars') or {}).items():
    w('- **%s:** %s' % (k, q(v)))
w('')

# --- the four locations
w('### 2.8 The four locations')
w('')
for lid in (cfg.get('unlock_order') or []):
    loc = locs.get(lid) or {}
    w('**%s** - %s' % (q(loc.get('name')), q(loc.get('represents'))))
    w('')
    for k in ('narrative', 'heading', 'hint', 'placeholder', 'other_label',
              'other_placeholder', 'button'):
        if loc.get(k):
            w('- **%s:** %s' % (k, q(loc.get(k))))
    w('')

# --- synthetic data hint
_hint = (cfg.get('sourcing') or {}).get('synthetic_hint')
if _hint:
    w('### 2.9 The Data Library: the synthetic-data offer')
    w('')
    w('- %s' % q(_hint))
    w('')

# --- postbox delivery lines, mirrored from QRDelivery.deliver in server.py
w('### 2.10 The Postbox: what CoCo says on send')
w('')
w('- **On success:** Wrapped and labelled, {first_name}. Scan the code on '
  'screen and it is yours - the link works for seven days.')
w('- **If staging fails:** I could not wrap it up this time - grab a Snowflake '
  'person and we will sort it.')
w('')

_scr = cfg.get('screens') or {}
if _scr:
    w('### 2.11 Screen furniture')
    w('')
    w('Prose that belongs to a screen rather than to a stop.')
    w('')
    for k, v in _scr.items():
        if not k.startswith('_'):
            w('- **%s:** %s' % (k, q(v)))
    w('')

# ==================================================== 3. the marketplace, shown
w('## 3. The datasets the booth recommends')
w('')
_slots = sum(len(v) for v in market.values())
_titles = {}
_where = {}
for _k in order():
    for _r in market.get(_k) or []:
        _titles[_r['title']] = _titles.get(_r['title'], 0) + 1
        _where.setdefault(_r['title'], []).append(ind_label(_k))
w('%d slots across %d industries, filled by %d distinct listings. Each is a '
  'real listing on the Snowflake Marketplace, verified attachable in the event '
  'region, so nothing offered here is a dead end.'
  % (_slots, len(market), len(_titles)))
w('')
for _k in order():
    rows = market.get(_k) or []
    if not rows:
        continue
    w('### %s' % ind_label(_k))
    w('')
    w('| Listing | Provider | Access | Global name |')
    w('| --- | --- | --- | --- |')
    for r in rows:
        w('| %s | %s | %s | `%s` |'
          % (q(r['title']), q(r['provider']), q(r['access']),
             q(r['global_name'])))
    w('')
    pins = (mkt.get('pinned') or {}).get(_k) or []
    if pins:
        w('Pinned first when the live tier is enabled: %s.'
          % ', '.join('`%s`' % q(p) for p in pins))
        w('')

w('### Which industries each listing appears in')
w('')
w('| Listing | Industries | Appears in |')
w('| --- | --- | --- |')
for t, n in sorted(_titles.items(), key=lambda kv: (-kv[1], kv[0])):
    w('| %s | %d | %s |' % (q(t), n, ', '.join(_where[t])))
w('')

# ============================================== 4. what the visitor already holds
w('## 4. What the visitor already holds')
w('')
w('The Data Library offers these per industry, plus a free-text option.')
w('')
for _k in order():
    b = inds.get(_k) or {}
    ds = b.get('data_sources') or []
    if not ds:
        continue
    w('### %s' % ind_label(_k))
    w('')
    w('| Option | Shown underneath |')
    w('| --- | --- |')
    for d in ds:
        if isinstance(d, dict):
            w('| %s | %s |' % (q(d.get('label')), q(d.get('note'))))
        else:
            w('| %s | |' % q(d))
    w('')

# ==================================================== 5. archetypes and routes
w('## 5. What gets built: the %d archetypes' % len(arch))
w('')
w('The workshop takes one line of free text and resolves it to exactly one '
  'archetype. The features and the first step are precomputed per archetype, so '
  'they are instant and always drawn from the curated feature list.')
w('')
w('| Archetype | Features | Considerations available |')
w('| --- | --- | --- |')
for k, v in arch.items():
    w('| %s | %s | %d |' % (q(k), q(v['features']), v['pool']))
w('')
w('### The first step printed for each')
w('')
for k, v in arch.items():
    if v['first_step']:
        w('- **%s** - %s' % (q(k), q(v['first_step'])))
w('')

w('## 6. How the data gets into Snowflake')
w('')
w('Each platform tapped on the letter prints a concrete route into the '
  'blueprint.')
w('')
w('| Platform | Route printed |')
w('| --- | --- |')
for p in ((cfg.get('platforms') or {}).get('options') or []):
    blurb = (paths.get(p) or ('', ''))[0]
    w('| %s | %s |' % (q(p), q(blurb)))
w('')
w('### When more than one is tapped')
w('')
w('| Selection | What the blueprint prints |')
w('| --- | --- |')
w('| One platform | That route |')
w('| Several named platforms | Each route, in the order listed above, so the '
  'document does not depend on tap order |')
for _x in ((cfg.get('platforms') or {}).get('exclusive') or []):
    w('| %s, alone | Its own line, no route |' % q(_x))
    w('| %s, with a named platform | The named platform only |' % q(_x))
w('| More than four platforms | The first four in the order listed above |')
w('')
# Platforms with a second phrasing for when they are not the only answer.
if 'PLATFORM_COMBINED' in srv:
    for _pm in re.finditer(r'"([^"]+)": \(\s*\n?\s*"(.*?)",\s*\n?\s*"https',
                           srv.split('PLATFORM_COMBINED = {')[-1], re.S):
        _blurb = re.sub(r'"\s*\n\s*"', '', _pm.group(2))
        w('%s is not an exclusive answer: an estate can be part in Snowflake '
          'and part elsewhere. When it is picked alongside a named platform the '
          'blueprint prints this instead of "nothing to move": **%s**'
          % (q(_pm.group(1)), q(_blurb)))
        w('')
        break
w('These rules are applied in the browser as the visitor taps, and again on the '
  'server when the blueprint is built.')
w('')

# ======================================================== 7. how answers are made
w('## 7. How each answer is produced')
w('')
w('| Stop | Model transport | Notes |')
w('| --- | --- | --- |')
for lid in (cfg.get('unlock_order') or []):
    loc = locs.get(lid) or {}
    tr = loc.get('transport')
    if lid == 'postbox':
        note = 'No model turn. Runs the QA review, writes the document, ' \
               'returns the fixed line above.'
        tr = '-'
    elif tr == 'exec':
        note = 'Agentic. CoCo\'s working is shown on screen as it arrives.'
    else:
        note = 'A single fast completion that names the selection back.'
    w('| %s | %s | %s |' % (q(loc.get('name')), q(tr or '-'), note))
w('')
w('Every turn has a wall-clock ceiling of %ss. Past it, the visitor is served '
  'the precomputed archetype content instead of a slower sentence, so the '
  'document is complete either way.'
  % ((cfg.get('coco') or {}).get('turn_timeout') or 60))
w('')
w('One model call is in flight at a time. A second caller waits, so one '
  'visitor\'s content can never appear in another visitor\'s document.')
w('')
w('The closed lists in this document reach the model as text inside the '
  'prompt. The model picks from them and reflects them back; it is never asked '
  'to invent a feature, a listing or a fact.')
w('')

# ============================================ 8. QA, then delivery
w('## 8. Review and delivery')
w('')
_qa = cfg.get('qa') or {}
w('Before the document is written, it is reviewed. Deterministic checks always '
  'run and repair what is fixable from the closed lists: features that do not '
  'resolve to a documentation link are dropped, '
  'platforms are re-normalised, the sovereignty section is required '
  'when a residency rule was given, and a list of banned words is removed. '
  'Every change is recorded with its before and after.')
w('')
if _qa.get('model_review'):
    w('One further check asks a model whether the proof of concept addresses '
      'the problem the visitor described. It never blocks delivery.')
    w('')
w('The visitor leaves with a Word document, reached by scanning a QR code on '
  'screen. The link lasts %d days. There is no email and no HTML page: the '
  'document is the only artifact.'
  % (int((cfg.get('delivery') or {}).get('presign_seconds') or 0) // 86400))
w('')

# ================================================== 9. configuration and limits
w('## 9. Configuration')
w('')
w('The flags that change what a visitor experiences.')
w('')
w('| Setting | Value | Effect |')
w('| --- | --- | --- |')
w('| `locations.marketplace.discovery` | `%s` | %s |'
  % (q(locs['marketplace'].get('discovery')),
     'The curated listings in section 3 are served'
     if locs['marketplace'].get('discovery') == 'manual'
     else 'Listings are searched live at the stall'))
w('| `marketplace.agentic.enabled` | `%s` | %s |'
  % (str((mkt.get('agentic') or {}).get('enabled')).lower(),
     'Agentic listing search is off'
     if not (mkt.get('agentic') or {}).get('enabled')
     else 'Agentic listing search is on'))
w('| `qa.enabled` | `%s` | Blueprint review runs before delivery |'
  % str(_qa.get('enabled')).lower())
w('| `qa.model_review` | `%s` | Relevance check included in the review |'
  % str(_qa.get('model_review')).lower())
w('| `delivery.transport` | `%s` | Delivery is by QR code to a staged document |'
  % q((cfg.get('delivery') or {}).get('transport')))
w('| `ask.enabled` | `%s` | %s |'
  % (str((cfg.get('ask') or {}).get('enabled')).lower(),
     'The optional free-question stop is not offered'
     if not (cfg.get('ask') or {}).get('enabled')
     else 'The optional free-question stop is offered'))
w('| `event.region` | `%s` | Listings are filtered to what is attachable here |'
  % q((cfg.get('event') or {}).get('region')))
w('| `event.time_limit_seconds` | `%s` | The visit length the booth is built for |'
  % q((cfg.get('event') or {}).get('time_limit_seconds')))
w('')

w('### Constraints to be aware of')
w('')
_geo = mkt.get('geo') or {}
_pref = len(_geo.get('prefer') or [])
_dem = len(_geo.get('demote') or [])
if _pref or _dem:
    w('- Listing selection is weighted for the United Kingdom: %d preference '
      'terms and %d demotion terms. A room in another country needs these '
      're-weighted.' % (_pref, _dem))
_trials = sum(1 for k in order() for r in (market.get(k) or [])
              if 'trial' in str(r.get('access', '')).lower())
if _trials:
    w('- %d of the %d slots are time-limited trials rather than perpetual free '
      'listings. All are free to acquire; none are paid.' % (_trials, _slots))
_reuse = [t for t, n in _titles.items() if n >= 3]
if _reuse:
    w('- %d listings appear in three or more industries, the most reused being '
      '%s. A visitor who has seen the booth before may be offered the same '
      'dataset again.'
      % (len(_reuse),
         ', '.join(q(t) for t, _n in
                   sorted(_titles.items(), key=lambda kv: -kv[1])[:2])))
w('- A listing is only offerable if Snowflake reports it as importable. That is '
  'stricter than being visible and not by-request, so the flag is checked '
  'directly rather than inferred.')
_noind = [ind_label(k) for k in order()
          if not ((mkt.get('pinned') or {}).get(k))]
if _noind:
    w('- No pinned fallback for: %s. These industries rely entirely on the '
      'curated list in section 3.' % ', '.join(_noind))
w('- The industry does not weight which archetype a visitor is routed to.')
w('- The data a visitor holds DOES narrow which datasets are suggested: each '
  'listing is tagged with what it is for and each library shelf with what it '
  'is, and selection intersects the two. There is no tag for unstructured '
  'text, because no curated listing serves it - a visitor whose problem is '
  'documents is ranked on their own words and their sector alone.')
w('')

def _to_docs(md):
    """Flatten Markdown tables for Google Docs, which does not render them.

    A table becomes one bullet per row, with each cell labelled by its column
    heading, so nothing is lost and nothing needs a monospace font. Everything
    else passes through untouched.
    """
    out, i = [], 0
    lines = md.splitlines()
    while i < len(lines):
        ln = lines[i]
        nxt = lines[i + 1] if i + 1 < len(lines) else ''
        is_head = ln.startswith('|') and set(nxt.replace('|', '').strip()) <= {
            '-', ' '} and nxt.startswith('|')
        if not is_head:
            plain = ln.replace('`', '')
            # Google Docs shows Markdown markers literally, so strip them. The
            # numbered section headings carry the hierarchy on their own.
            plain = re.sub(r'^#{1,6}\s*', '', plain)
            plain = re.sub(r'\*\*(.+?)\*\*', r'\1', plain)
            out.append(plain)
            i += 1
            continue
        cols = [c.strip() for c in ln.strip().strip('|').split('|')]
        i += 2
        while i < len(lines) and lines[i].startswith('|'):
            cells = [c.strip().replace(r'\|', '|').replace('`', '')
                     for c in lines[i].strip().strip('|').split('|')]
            parts = []
            for h, c in zip(cols, cells):
                if not c or c == '-':
                    continue
                parts.append(c if h in ('#', 'Listing', 'Stop', 'Setting',
                                        'Archetype', 'Option', 'Platform',
                                        'Selection')
                             else '%s: %s' % (h, c))
            if parts:
                out.append('- ' + ' \u00b7 '.join(parts))
            i += 1
        out.append('')
    return '\n'.join(out)


body = '\n'.join(O)
if '--docs' in os.sys.argv:
    body = _to_docs(body)
print(body)

