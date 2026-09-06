"""Audit the exported card PNGs at pixel level.

Auditing source tells you what the code says; auditing the PNG tells you what
the visitor actually receives. This checks the dominant colours in each of the
nine cards against the declared palette, so a drifted colour cannot hide in a
gradient or an alpha composite.

Anti-aliased edges blend two legal colours into an illegal midpoint, so a raw
"every pixel must be palette" test would fail on a correct card. Instead this
reports coverage: what share of each card is within a small distance of a
palette colour. A correct card is dominated by palette; a drifted one is not.
"""
import json, os, sys
from collections import Counter
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'game')
cfg = json.load(open(f'{ROOT}/config.json'))
pal = {}
for group in ('theme', 'penguin'):
    for k, v in cfg[group].items():
        if isinstance(v, str) and v.startswith('#'):
            pal[v.upper()] = f'{group}.{k}'
# Card faces legitimately use paper white for the ground and the letter.
pal['#FFFFFF'] = 'white-prop'

def rgb(h):
    return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

PAL = [(rgb(h), name, h) for h, name in pal.items()]

def nearest(px):
    best, bd = None, 10**9
    for c, name, h in PAL:
        d = sum((a - b) ** 2 for a, b in zip(px, c))
        if d < bd:
            bd, best = d, (h, name)
    return best, bd ** 0.5

CARDS = ['talk-to-my-data', 'ask-my-documents', 'extract-from-paperwork',
         'triage-and-classify', 'an-agent-that-acts',
         'predict-what-happens-next', 'join-the-silos',
         'share-without-copying', 'watch-it-live']

TOL = 26          # within this distance of a palette colour = "on palette"
fails = []

for name in CARDS:
    p = f'{ROOT}/card_examples/{name}.png'
    im = Image.open(p).convert('RGB')
    w, h = im.size
    # Sample on a grid rather than every pixel: 1200x630 is 756k pixels and a
    # grid of 60k is already far below sampling error for a coverage figure.
    step = 5
    px = [im.getpixel((x, y))
          for y in range(0, h, step) for x in range(0, w, step)]
    on, off = 0, Counter()
    for q in px:
        (hexv, nm), d = nearest(q)
        if d <= TOL:
            on += 1
        else:
            off['#%02X%02X%02X' % q] += 1
    pct = 100.0 * on / len(px)
    corner = im.getpixel((3, 3))
    corner_hex = '#%02X%02X%02X' % corner
    dom = Counter('#%02X%02X%02X' % q for q in px).most_common(1)[0]
    dom_pct = 100.0 * dom[1] / len(px)

    bg_ok = corner_hex == '#2C3444'
    status = 'ok' if bg_ok and pct >= 92 else 'CHECK'
    if status == 'CHECK':
        fails.append(name)
    print(f'{status:5} {name:28} {w}x{h}  bg={corner_hex}'
          f'{"" if bg_ok else " <- not #2C3444"}'
          f'  on-palette {pct:5.1f}%  dominant {dom[0]} {dom_pct:4.1f}%')
    if off and status == 'CHECK':
        print('        furthest off-palette:',
              ', '.join(f'{c}x{n}' for c, n in off.most_common(5)))

print('\nRESULT:', 'PASS - all nine cards sit on #2C3444 and are '
      'palette-dominated' if not fails else f'FAIL: {fails}')
sys.exit(1 if fails else 0)
