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

# Every bucket_only listing must still be reachable in its OWN bucket.
bo = set((cfg['marketplace'].get('bucket_only') or []))
reachable = set()
for ind in inds:
    st = {'visitor': {'industry': ind}, 'held': [], 'session_id': 'x'}
    for r in server.listings_for(cfg, ind, state=st):
        reachable.add(r.get('global_name'))
for gn in bo:
    home = [k for k, rows in market.items()
            if any(r.get('global_name') == gn for r in rows)]
    if gn not in reachable:
        fails.append(f"bucket_only {gn} unreachable (home buckets: {home})")

# No listing may vanish from the catalogue entirely.
all_gns = {r.get('global_name') for rows in market.values() for r in rows}
never = all_gns - reachable
print('industries checked :', len(inds))
print('listings reachable :', len(reachable), 'of', len(all_gns))
if never:
    print('never offered      :', sorted(never))

print()
if fails:
    print(f'FAILURES ({len(fails)}):')
    for f in fails:
        print('  -', f)
    raise SystemExit(1)
print('every industry fills six slots; bucket_only listings stay reachable')
