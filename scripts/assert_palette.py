"""Audit every colour literal in the shipped game against config.json's palette.

Source of truth is config.json: theme + penguin. Anything else must be a
*declared* exception with a reason, or it is a violation. Three declared sets:

  PAPER  - paper props inside the dark scenes (the letter, the envelope, the
           notes on the workshop bench). Paper is a prop, not a background.
  PRINT  - the blueprint handout's paper field. It is printed on real paper; a
           dark field there is a ruined cartridge.
  QR     - QR module and quiet-zone colours, kept near-black on white for
           scanner reliability. A styled QR is a QR that fails on a phone.

rgba(0,0,0,a) and rgba(255,255,255,a) are compositing operations - darken or
lighten whatever is beneath - not colour choices, so they are not audited.
"""
import json, re, sys, os
from collections import defaultdict

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'game')
cfg = json.load(open(f'{ROOT}/config.json'))
palette = {v.upper() for v in cfg['theme'].values()}
palette |= {v.upper() for v in cfg['penguin'].values() if isinstance(v, str)}

PAPER = {
    '#EFE6D2', '#EADFC6', '#EADFCF', '#B9A98A', '#9C8C6E', '#C6B79A',
    '#2A2418', '#1C4E7A', '#B4442E', '#8A3524', '#0E2436', '#1E6F94',
    '#274A5F', '#F2FAFF',
}
PRINT = {'#F4F8FB'}
QR = {'#0A121A'}
# White survives in exactly three roles, none of them a background: the QR
# quiet zone, the printable's card faces, and the letter paper.
WHITE = {'#FFF', '#FFFFFF'}
COMPOSITE = {'#000000', '#FFFFFF'}

HEX = re.compile(r'#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b')
RGBA = re.compile(r'rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)')
# Strip // line comments and /* */ so a hex quoted in prose is not a finding.
LINE_COMMENT = re.compile(r'(^\s*(//|\*|#)|/\*.*?\*/)')

FILES = ['index.html', 'favicon.svg', 'server.py', 'card_examples/gallery.html']

found, rgba_found = defaultdict(list), defaultdict(list)

for rel in FILES:
    for n, line in enumerate(open(os.path.join(ROOT, rel)), 1):
        code = line
        if LINE_COMMENT.match(line.strip()) or line.strip().startswith('//'):
            continue
        code = re.sub(r'//.*$', '', code) if rel.endswith('.html') else code
        for h in HEX.findall(code):
            found[h.upper()].append((rel, n, code.strip()[:88]))
        for m in RGBA.finditer(code):
            r, g, b = (int(float(x)) for x in m.groups())
            key = '#%02X%02X%02X' % (r, g, b)
            if key in COMPOSITE:
                continue
            rgba_found[key].append((rel, n, code.strip()[:88]))

def classify(h):
    if h in palette:  return 'palette'
    if h in PAPER:    return 'paper-prop'
    if h in PRINT:    return 'print'
    if h in QR:       return 'qr'
    if h in WHITE:    return 'white-prop'
    return 'VIOLATION'

buckets = defaultdict(list)
for h, sites in sorted(found.items()):
    buckets[classify(h)].append((h, sites))
rgba_bad = [(h, s) for h, s in sorted(rgba_found.items())
            if classify(h) == 'VIOLATION']

print(f'palette: {len(palette)} tokens declared, '
      f'{len(buckets["palette"])} used as hex literals')
unused = sorted(palette - set(found) - set(rgba_found))
if unused:
    print('  declared but unused here:', ', '.join(unused))

for label in ('paper-prop', 'print', 'qr', 'white-prop'):
    print(f'\ndeclared exception: {label} ({len(buckets[label])} colours)')
    for h, sites in buckets[label]:
        print(f'  {h}  x{len(sites)}  '
              + ', '.join(f'{f}:{n}' for f, n, _ in sites[:4]))

print(f'\nrgba() overlays on palette colours: '
      f'{len(rgba_found) - len(rgba_bad)} distinct')

print(f'\n=== VIOLATIONS: {len(buckets["VIOLATION"])} hex, '
      f'{len(rgba_bad)} rgba ===')
for h, sites in buckets['VIOLATION'] + rgba_bad:
    print(f'  {h}  x{len(sites)}')
    for f, n, txt in sites[:6]:
        print(f'      {f}:{n}  {txt}')

ok = not buckets['VIOLATION'] and not rgba_bad
print('\nRESULT:', 'PASS - every colour is palette or declared' if ok
      else 'FAIL')
sys.exit(0 if ok else 1)
