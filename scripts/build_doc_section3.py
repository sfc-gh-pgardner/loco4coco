"""Generate the replacement for section 3 of the Decision Tree & Script doc.

The doc is entirely plain NORMAL_TEXT paragraphs with a literal "- " prefix and
" \u00b7 " separators - no tables, no real Docs lists - so this matches that
convention rather than introducing a table that would look foreign.

Writes /tmp/doc_section3.txt for insertion.
"""
import json
from collections import Counter

MK = 'skills/loco4coco/references/marketplace.json'
CITY = [('uk', 'London'), ('fr', 'Paris'), ('de', 'Berlin')]
INDUSTRY = [
    ('healthcare', 'Healthcare & Life Sciences'),
    ('financial', 'Financial Services'),
    ('retail', 'Retail & Consumer Goods'),
    ('public', 'Public Sector & Government'),
    ('manufacturing', 'Manufacturing & Industrial'),
    ('energy', 'Energy & Utilities'),
    ('media', 'Media, Telco & Entertainment'),
    ('other', 'Something else'),
]

d = json.load(open(MK))
P = d['profiles']
L = []


def w(s=''):
    L.append(s)


slots = sum(len(P[p][i]['primary']) for p, _ in CITY for i, _ in INDUSTRY)
distinct = len({r['global_name'] for p, _ in CITY for i, _ in INDUSTRY
                for r in P[p][i]['primary']})

w('These are the datasets a visitor is offered, per city and per industry. They are '
  'real Snowflake Marketplace listings - never invented - and they are chosen for '
  'relevance to the city the visitor is standing in.')
w()
w('%d slots across 3 cities and 8 industries, filled by %d distinct listings. '
  'Picking the venue selects the set; there is nothing to re-run on the day.'
  % (slots, distinct))
w()
w('A pick is judged on whether it is relevant to the event\u2019s city, not on whether '
  'the booth\u2019s own account could attach it. The visitor never imports anything at '
  'the booth - they leave with links and open them later from their own account - so '
  'availability in the booth account is not a criterion, and listings are deliberately '
  'not dropped for failing it.')
w()
w('Every stall carries six picks, in all three cities. Paris manufacturing was '
  'once thought to be a regional gap, on the grounds that the data did not exist '
  'in that region. Two of the three listings behind that claim really are absent '
  'from AWS_EU_WEST_3 - Overture Maps \u2013 Transportation and FactSet Supply '
  'Chain Relationships. The third, Industry Classification Systems, is available '
  'there and is now a Paris pick. A re-run of the region-filtered search found '
  'six on-theme Paris listings, so the shortfall was a thin search rather than a '
  'thin catalogue.')
w()

for prof, city in CITY:
    w('%s' % city.upper())
    w()
    for ind, label in INDUSTRY:
        rows = P[prof][ind]['primary']
        w('%s \u2014 %s (%d)' % (city, label, len(rows)))
        w()
        for r in rows:
            w('- %s \u00b7 Provider: %s \u00b7 Access: %s \u00b7 Global name: %s'
              % (r.get('title') or '', r.get('provider') or '',
                 r.get('access') or '', r.get('global_name') or ''))
        w()

# cross-reference: which industries each listing appears in, per city
w('WHICH INDUSTRIES EACH LISTING APPEARS IN')
w()
w('A listing leading several stalls in one city is not automatically wrong - generic '
  'population and geography data is genuinely useful across sectors - but it is capped '
  'at three, because past that the six stop looking chosen. Worst repeat per city is '
  'shown below.')
w()
for prof, city in CITY:
    cnt = Counter()
    where = {}
    for ind, label in INDUSTRY:
        for r in P[prof][ind]['primary']:
            t = r.get('title') or ''
            cnt[t] += 1
            where.setdefault(t, []).append(label)
    w('%s' % city.upper())
    w()
    for t, n in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
        if n > 1:
            w('- %s \u00b7 Industries: %d \u00b7 Appears in: %s'
              % (t, n, ', '.join(where[t])))
    w()

text = '\n'.join(L)
open('/tmp/doc_section3.txt', 'w').write(text)
print('chars:', len(text), '| lines:', len(L))
print('slots:', slots, '| distinct:', distinct)
