"""Assert the generated decision tree against the live app.

Two classes of check:
  1. COMPLETENESS - every scripted string and every listing appears.
  2. HYGIENE      - no dates, no timings, no historical narrative.

Generates the document itself, so it cannot pass against a stale copy.

    python3 scripts/assert_decision_tree.py
"""
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
doc = subprocess.run([sys.executable, 'game/decision_tree.py'],
                     capture_output=True, text=True, check=True).stdout
cfg = json.load(io.open('game/config.json', encoding='utf-8'))

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)


# ---------------------------------------------------------- 1. completeness
def norm(s):
    return re.sub(r'\s+', ' ', str(s or '')).strip()


# Intro, letter, trust, pillars, reactions, question copy: every string present.
groups = {
    'intro.body': (cfg['intro'].get('body') or []),
    'sovereignty.trust': (cfg['sovereignty'].get('trust') or []),
    'sovereignty.pillars': list((cfg['sovereignty'].get('pillars') or {}).values()),
    'sovereignty.react': list((cfg['sovereignty'].get('react') or {}).values()),
    'intake.letter.body': ((cfg['intake'].get('letter') or {}).get('body') or []),
    'platforms.options': (cfg['platforms'].get('options') or []),
    'country.options': (cfg['country'].get('options') or []),
    'residency.options': (cfg['residency'].get('options_template') or []),
}
nd = norm(doc)
for label, items in groups.items():
    for s in items:
        check(norm(s) in nd, f"MISSING {label}: {norm(s)[:60]!r}")

# Headings and hints for the three home questions.
for key in ('platforms', 'country', 'residency'):
    for f in ('heading', 'hint'):
        v = cfg[key].get(f)
        check(norm(v) in nd, f"MISSING {key}.{f}: {norm(v)[:60]!r}")

# Every location's scripted fields.
for lid in (cfg.get('unlock_order') or []):
    loc = cfg['locations'][lid]
    for f in ('name', 'narrative', 'heading', 'hint'):
        if loc.get(f):
            check(norm(loc[f]) in nd, f"MISSING {lid}.{f}")

# Every curated listing title and global name.
sys.path.insert(0, 'game')
import server  # noqa: E402
market = server.load_marketplace()
slots = 0
titles = set()
for k, rows in market.items():
    for r in rows:
        slots += 1
        titles.add(r['title'])
        check(norm(r['title']) in nd, f"MISSING listing: {r['title'][:50]!r}")
        gn = r.get('global_name')
        if gn:
            check(gn in doc, f"MISSING global_name: {gn}")

# Every industry's data sources.
for k, b in (cfg.get('industries') or {}).items():
    for d in (b.get('data_sources') or []):
        lab = d.get('label') if isinstance(d, dict) else d
        check(norm(lab) in nd, f"MISSING data_source {k}: {norm(lab)[:40]!r}")

# The computed counts must match reality, not be typed.
check(f"{slots} slots" in doc, f"slot count {slots} not stated")
check(f"{len(titles)} distinct listings" in doc,
      f"distinct count {len(titles)} not stated")

# Screen furniture is visitor-facing copy too, so the "every scripted line"
# claim is false without it.
for _k, _v in (cfg.get('screens') or {}).items():
    if not _k.startswith('_'):
        check(norm(_v) in nd, f'MISSING screens.{_k}: {norm(_v)[:50]!r}')

# ---------------------------------------------------------------- 2. hygiene
BANNED = [
    (r'\b20\d\d-\d\d-\d\d\b', 'an ISO date'),
    # Decimal timings are measurement anecdotes ("117.1s", "26.0s"). An integer
    # ceiling read from config is a present-tense fact and is allowed.
    (r'\b\d+\.\d+s\b', 'a measured timing'),
    (r'\bit used to\b|\bwe used to\b|\bused to be\b', '"used to"'),
    (r'\bpreviously\b', '"previously"'),
    (r'\bnow fixed\b', '"now fixed"'),
    (r'\bMEASURED\b|\bMeasured\b', '"measured"'),
    (r'\bre-timed\b|\bRe-timed\b', '"re-timed"'),
    (r'\bonce sat\b', '"once sat"'),
    (r'\bBefore the guardrails\b', 'the guardrails history'),
    (r'\bwe fixed\b|\bwe changed\b|\bwe removed\b', 'first-person change talk'),
    (r'\bno longer\b', '"no longer"'),
    (r'\bPaddy\b', 'a personal name'),
]
for pat, what in BANNED:
    for m in re.finditer(pat, doc):
        line = doc[:m.start()].count('\n') + 1
        seg = doc.splitlines()[line - 1][:90]
        fails.append(f"HYGIENE line {line}: {what} -> {seg!r}")

# The ask stop is disabled: it must not be documented as a live section.
check('### The workshop - the one line we ask for' not in doc,
      'the old ask/workshop conflated heading survives')
check('ASK COCO' not in doc, 'the disabled ask stop button is documented')
check('SKIP THIS' not in doc, 'the disabled ask stop skip is documented')

# The postbox must not be claimed as an exec stop. Check the transport table in
# section 7 specifically, not the stop table in section 1.
sec7 = doc.split('## 7.')[-1].split('## 8.')[0]
mtab = re.search(r'\| The Postbox \| ([^|]+) \|', sec7)
check(mtab is not None, 'postbox row missing from the transport table')
if mtab:
    check(mtab.group(1).strip() in ('-', ''),
          f"postbox transport claimed as {mtab.group(1).strip()!r}")

print(f"completeness+hygiene checks run against {len(doc)} chars")
print(f"slots={slots} distinct={len(titles)}")
if fails:
    print(f"\nFAILURES ({len(fails)}):")
    for f in fails[:40]:
        print("  -", f)
    sys.exit(1)
print("\nALL CHECKS PASS")
