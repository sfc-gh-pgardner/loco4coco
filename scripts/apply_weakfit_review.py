"""Apply the weak-fit review verdicts to marketplace.json.

Decisions and reasoning are in audit/weak-fit-review.md. Rejected picks are moved
to reserve rather than deleted: they are still real, checked, local data, just not
a headline pick for that sector. Paris manufacturing is deliberately left at four
primary picks - Overture Transportation and FactSet Supply Chain are not offered in
AWS_EU_WEST_3 and Industry Classification Systems is absent from that catalogue, so
the sixth and fifth slots cannot be filled on theme. Four honest picks beat six with
hospital locations in a manufacturing stall.
"""
import json
import sys

PATH = 'skills/loco4coco/references/marketplace.json'

# (profile, industry, title-fragment) -> remove from the stall ENTIRELY.
#
# Demotion to reserve is NOT enough here, and finding that out cost a round: the
# stall is built from primary THEN reserve and sliced to six, so reserve doubles as
# the filler for a short stall. Paris manufacturing has only four on-theme picks, so
# a demoted row simply reappeared at position five. "Reject" has to mean removed.
# The rows stay documented in audit/weak-fit-review.md and in git history.
DELETE = [
    ('fr', 'manufacturing', 'Franciemes IRIS'),
    ('fr', 'manufacturing', 'French National Health and Social Facilities'),
]

# (profile, industry, title-fragment) -> demote from primary to reserve. Safe only
# where a promotion refills the sixth slot, otherwise see DELETE.
DEMOTE = [
    ('fr', 'media', 'ANNUAL REGIONAL PRODUCTION OF RENEWABLE ENERGIES'),
    ('de', 'manufacturing', 'Intelligent Event Data: Attended Events, Munich'),
    ('de', 'manufacturing', 'Purchasing Power for Countries Worldwide'),
]

# (profile, industry, title-fragment) -> promote from reserve into primary
PROMOTE = [
    ('fr', 'media', 'Shopping center footfall'),
    ('de', 'manufacturing', 'Industry Classification Systems'),
]

# (profile, industry, title-fragment) -> copy in from another profile's entry
CROSS = [
    ('de', 'manufacturing', 'Overture Maps - Transportation', 'uk'),
]

d = json.load(open(PATH))
P = d['profiles']


def find(rows, frag):
    for i, r in enumerate(rows):
        if frag.lower() in (r.get('title') or '').lower():
            return i
    return None


changes = []

for prof, ind, frag in DELETE:
    block = P[prof][ind]
    gone = False
    for key in ('primary', 'reserve'):
        while True:
            i = find(block.get(key) or [], frag)
            if i is None:
                break
            row = block[key].pop(i)
            changes.append(f'DELETE  {prof}/{ind} [{key}]: {row["title"][:46]}')
            gone = True
    if not gone:
        sys.exit(f'DELETE not found: {prof}/{ind}/{frag}')

for prof, ind, frag in DEMOTE:
    block = P[prof][ind]
    i = find(block['primary'], frag)
    if i is None:
        sys.exit(f'DEMOTE not found in primary: {prof}/{ind}/{frag}')
    row = block['primary'].pop(i)
    row['demoted'] = 'rejected by SE review: off-theme for this sector'
    block.setdefault('reserve', []).insert(0, row)
    changes.append(f'demote  {prof}/{ind}: {row["title"][:50]}')

for prof, ind, frag in PROMOTE:
    block = P[prof][ind]
    i = find(block.get('reserve') or [], frag)
    if i is None:
        sys.exit(f'PROMOTE not found in reserve: {prof}/{ind}/{frag}')
    row = block['reserve'].pop(i)
    row.pop('demoted', None)
    block['primary'].append(row)
    changes.append(f'promote {prof}/{ind}: {row["title"][:50]}')

for prof, ind, frag, src in CROSS:
    block = P[prof][ind]
    if find(block['primary'], frag) is not None:
        continue
    srow = None
    for sind, sblock in P[src].items():
        for key in ('primary', 'reserve'):
            j = find(sblock.get(key) or [], frag)
            if j is not None:
                srow = dict((sblock[key])[j])
                break
        if srow:
            break
    if not srow:
        sys.exit(f'CROSS source not found: {src}/{frag}')
    srow.pop('demoted', None)
    block['primary'].append(srow)
    changes.append(f'add     {prof}/{ind}: {srow["title"][:50]} (from {src})')

d['_generated'].setdefault('weak_fit_review', {})
d['_generated']['weak_fit_review'] = {
    'at': '2026-09-21',
    'applied': changes,
    'note': ('Verdicts from audit/weak-fit-review.md. 97 report flags resolved to 7 '
             'decisions: 90 were in reserve tables a visitor never sees. Paris '
             'manufacturing is intentionally left at 4 primary picks - the on-theme '
             'data is not offered in AWS_EU_WEST_3.'),
}

with open(PATH, 'w') as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
    f.write('\n')

for c in changes:
    print(c)
print()
for prof in ('uk', 'fr', 'de'):
    for ind in ('manufacturing', 'media'):
        b = P[prof][ind]
        print(f'{prof}/{ind:14} primary={len(b["primary"])} reserve={len(b.get("reserve") or [])}')
