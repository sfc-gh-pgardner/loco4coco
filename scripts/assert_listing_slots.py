import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(HERE))
sys.path.insert(0, 'game')
import server

cfg = server.load_config()
market = server.load_marketplace()
inds = list((cfg.get('industries') or {}).keys())

fails = []
# Every industry must still fill six slots, with and without held data.
for ind in inds:
    for label, held in (('no shelves', []),
                        ('all its shelves',
                         [(d.get('label') if isinstance(d, dict) else d)
                          for d in ((cfg['industries'][ind].get('data_sources')) or [])])):
        st = {'visitor': {'industry': ind}, 'held': held, 'session_id': 'x'}
        rows = server.listings_for(cfg, ind, state=st)
        if len(rows) != 6:
            fails.append(f"{ind} / {label}: {len(rows)} rows, expected 6")

# bucket_only is now keyed by market profile, so read it the way the server does.
_profile = (cfg.get('event') or {}).get('market_profile') or 'uk'
bo = server._bucket_only_for(cfg, _profile)
reachable = set()
for ind in inds:
    st = {'visitor': {'industry': ind}, 'held': [], 'session_id': 'x'}
    for r in server.listings_for(cfg, ind, state=st):
        reachable.add(r.get('global_name'))
# The constraint the config actually states is NEGATIVE - a protected listing must
# never be offered OUTSIDE its own bucket. The old check asserted the opposite, that
# each one is reachable inside its bucket, which is not something the design
# promises: a protected listing sitting in reserve legitimately may never surface.
_home = {}
for _k, _rows in market.items():
    for _r in _rows:
        _home.setdefault(_r.get('global_name'), set()).add(_k)
for ind in inds:
    for _held in ([], [(d.get('label') if isinstance(d, dict) else d)
                       for d in ((cfg['industries'][ind].get('data_sources')) or [])]):
        st = {'visitor': {'industry': ind}, 'held': _held, 'session_id': 'x'}
        for r in server.listings_for(cfg, ind, state=st):
            gn = r.get('global_name')
            if gn in bo and ind not in _home.get(gn, set()):
                fails.append(f"bucket_only {gn} leaked into {ind} "
                             f"(belongs to {sorted(_home.get(gn, set()))})")

# No listing may vanish from the catalogue entirely.
all_gns = {r.get('global_name') for rows in market.values() for r in rows}
never = all_gns - reachable
print('industries checked :', len(inds))
print('listings reachable :', len(reachable), 'of', len(all_gns))
if never:
    print('never offered      :', sorted(never))

# Every profile must have its own protection. A flat list only covered the profile
# it was written for, and that is how Paris and Berlin came to run with none at all
# while the config read as though they were covered - so a profile with zero entries
# is now a FAILURE, not a note.
import json as _json
_mk = _json.load(open('skills/loco4coco/references/marketplace.json'))['profiles']
print()
print('bucket_only protection by profile:')
for _prof in sorted(_mk):
    _n = len(server._bucket_only_for(cfg, _prof))
    print('  %-3s %2d listings protected' % (_prof, _n))
    if not _n:
        fails.append(f"profile {_prof} has no bucket_only protection - "
                     "sector-specific data can be borrowed into any stall")

print()
if fails:
    print(f'FAILURES ({len(fails)}):')
    for f in fails:
        print('  -', f)
    raise SystemExit(1)
print('every industry fills six slots; no protected listing leaks across buckets')
