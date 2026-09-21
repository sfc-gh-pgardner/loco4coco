"""Assert the SE review HTML and the Decision Tree doc section agree.

Both are generated from marketplace.json, but by different scripts at different
times, so "they must agree" is a claim worth testing rather than assuming.
Compares primary-pick counts per city and the distinct-listing total, and checks
the rejected picks appear in neither.
"""
import html
import json
import re

MK = 'skills/loco4coco/references/marketplace.json'
HTML = 'audit/marketplace-se-review.html'
DOC = '/tmp/doc_section3.txt'
CITY = [('uk', 'London', 'pane-uk'), ('fr', 'Paris', 'pane-fr'),
        ('de', 'Berlin', 'pane-de')]
INDUSTRY = ['healthcare', 'financial', 'retail', 'public',
            'manufacturing', 'energy', 'media', 'other']
# Scoped to the EXACT stall each was rejected FROM. These titles are legitimate
# primary picks in other industries - Franciemes IRIS in French financial/public,
# Purchasing Power Worldwide in German financial/retail/energy - so a global
# substring search reports false failures. It did, first time.
REJECTED = [
    ('fr', 'manufacturing', 'Franciemes IRIS'),
    ('fr', 'manufacturing', 'French National Health and Social Facilities'),
    ('de', 'manufacturing', 'Intelligent Event Data: Attended Events, Munich'),
    ('de', 'manufacturing', 'Purchasing Power for Countries Worldwide'),
    ('fr', 'media', 'ANNUAL REGIONAL PRODUCTION OF RENEWABLE ENERGIES'),
]

d = json.load(open(MK))
P = d['profiles']
h = open(HTML).read()
doc = open(DOC).read()

panes = {}
for m in re.finditer(
        r'<section\s+class="pane[^"]*"\s+id="(pane-\w+)"\s*>(.*?)</section>',
        h, re.S):
    panes[m.group(1)] = m.group(2)

fail = []
json_slots = 0
distinct = set()


for prof, city, pid in CITY:
    # marketplace.json
    j_rows = []
    for ind in INDUSTRY:
        j_rows += P[prof][ind]['primary']
    json_slots += len(j_rows)
    distinct |= {r['global_name'] for r in j_rows}

    # HTML: primary tables only (before each industry's "Reserves:" marker)
    body = panes.get(pid, '')
    h_count = 0
    for seg in re.split(r'<h3[^>]*>', body)[1:]:
        label = html.unescape(re.sub(r'<[^>]+>', '', seg.split('</h3>')[0])).strip()
        if 'awaiting review' in label:
            continue
        primary = re.split(r'<p class="sub">\s*Reserves:', seg)[0]
        h_count += len(re.findall(r'<td[^>]*>', primary)) and len(
            [r for r in re.findall(r'<tr>(.*?)</tr>', primary, re.S) if '<td' in r])

    # doc text: "City — Label (n)" headers
    d_count = sum(int(n) for n in re.findall(
        re.escape(city) + r' \u2014 [^(\n]+\((\d+)\)', doc))

    status = 'OK' if len(j_rows) == h_count == d_count else 'MISMATCH'
    if status == 'MISMATCH':
        fail.append(f'{city}: json={len(j_rows)} html={h_count} doc={d_count}')
    print(f'{city:8} json={len(j_rows):3}  html={h_count:3}  doc={d_count:3}  {status}')

print()
doc_slots = sum(int(n) for n in re.findall(r'\u2014 [^(\n]+\((\d+)\)', doc))
doc_claim = re.search(r'(\d+) slots across 3 cities', doc)
print(f'json slots={json_slots}  doc slots={doc_slots}  doc claims={doc_claim.group(1) if doc_claim else "?"}')
if doc_claim and int(doc_claim.group(1)) != json_slots:
    fail.append('doc slot claim does not match json')
if doc_slots != json_slots:
    fail.append('doc per-city headers do not sum to json slots')

print(f'json distinct={len(distinct)}')
d_distinct = re.search(r'filled by (\d+) distinct', doc)
if d_distinct and int(d_distinct.group(1)) != len(distinct):
    fail.append(f'doc distinct claim {d_distinct.group(1)} != {len(distinct)}')

print()
city_of = {p: c for p, c, _ in CITY}
for prof, ind, t in REJECTED:
    in_json = any(t.lower() in (r.get('title') or '').lower()
                  for r in P[prof][ind]['primary'])
    # the doc block for that one city+industry only
    label = {'manufacturing': 'Manufacturing & Industrial',
             'media': 'Media, Telco & Entertainment'}[ind]
    blk = re.search(re.escape(city_of[prof] + ' \u2014 ' + label) +
                    r'[^\n]*\n\n(.*?)(?=\n\n[A-Z])', doc, re.S)
    in_doc = bool(blk) and t.lower() in blk.group(1).lower()
    ok = not in_json and not in_doc
    print(f'{prof}/{ind[:13]:13} {t[:42]:42} json={in_json} doc={in_doc} '
          + ('OK' if ok else 'STILL PRESENT'))
    if not ok:
        fail.append(f'rejected pick still on {prof}/{ind}: {t}')

print()
print('FAIL: ' + '; '.join(fail) if fail else 'PASS - HTML, doc and marketplace.json agree')
