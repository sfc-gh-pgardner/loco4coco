"""The exact case the browser found: an energy visitor whose problem text does
not mention weather must still be offered the weather data their bucket exists
to give them, not a listing that coincidentally shares the word "systems".
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(HERE))
sys.path.insert(0, 'game')
import server

cfg = server.load_config()

CASE = {
    'industry': 'energy',
    'held': ['Smart meter readings', 'Outage & fault records'],
    'problem': ('We spend hours manually reviewing customer emails to identify '
                'urgent issues. We would like a system that automatically flags '
                'critical emails for immediate attention.'),
}
st = {'visitor': {'industry': CASE['industry'], 'problem': CASE['problem']},
      'held': CASE['held'], 'session_id': 'browsercase'}

rows = server.listings_for(cfg, CASE['industry'], state=st)
titles = [r['title'] for r in rows]
print('offered to the energy visitor:')
for t in titles:
    print('  -', t[:62])

own = {r['global_name'] for r in server.load_marketplace()['energy']}
got = {r['global_name'] for r in rows}
borrowed = got - own
print('\nborrowed from other buckets:', len(borrowed))
print('tokens from that problem   :',
      sorted(server._problem_tokens(st))[:12])

fails = []
# Both Met Office energy listings must survive - but they are UK listings, and
# this gate asserts them by global name. On a Paris or Berlin booth the energy
# bucket is French or German by design, so asserting them there reports two
# failures for a stall that is correct, and a gate that cries wolf on the
# morning of an event is worse than no gate (same reasoning as verify_context.py).
# The regression this file exists to catch is the RANKING bug, not the UK list,
# so the coincidental-word-match assertion below still runs for every venue.
_profile = (cfg.get('event') or {}).get('market_profile') or 'uk'
if _profile == 'uk':
    for gn, name in (('GZTDZJKVCU', 'National Severe Weather Warning Service'),
                     ('GZTDZJKVH3', 'UK Land Surface Observations')):
        if gn not in got:
            fails.append(f'{name} missing from an energy visitor\'s stall')
else:
    print(f'\nnote: market_profile={_profile!r}, so the two UK Met Office '
          f'assertions are skipped; the ranking assertions still run')
# A coincidental word match must not displace the bucket.
for bad in ('Industry Classification', 'Spatial Features'):
    if any(bad in t for t in titles):
        fails.append(f'{bad!r} borrowed in on a coincidental word match')

print()
if fails:
    print(f'FAILURES ({len(fails)}):')
    for f in fails:
        print('  -', f)
    raise SystemExit(1)
print('the energy visitor keeps their weather data')
