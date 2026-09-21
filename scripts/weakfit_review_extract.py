import re, html, json

h = open('audit/marketplace-se-review.html').read()
panes = {}
for m in re.finditer(r'<section\s+class="pane[^"]*"\s+id="(pane-\w+)"\s*>(.*?)</section>', h, re.S):
    panes[m.group(1)] = m.group(2)
names = {'pane-uk': 'London', 'pane-fr': 'Paris', 'pane-de': 'Berlin'}


def txt(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def parse_rows(block):
    recs = []
    for r in re.findall(r'<tr>(.*?)</tr>', block, re.S):
        tds = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
        if not tds:
            continue
        reason = re.search(r'title="([^"]*)"', r)
        recs.append({
            'title': txt(tds[0].split('<span')[0]),
            'provider': txt(tds[1]) if len(tds) > 1 else '',
            'access': txt(tds[2]) if len(tds) > 2 else '',
            'local': txt(tds[3]) if len(tds) > 3 else '',
            'weak': 'weak fit' in r,
            'reason': reason.group(1) if reason else '',
        })
    return recs


out = {}
for pid, body in panes.items():
    city = names[pid]
    out[city] = {}
    for seg in re.split(r'<h3[^>]*>', body)[1:]:
        ind = txt(seg.split('</h3>')[0])
        parts = re.split(r'<p class="sub">\s*Reserves:', seg)
        primary = parse_rows(parts[0])
        reserve = parse_rows(parts[1]) if len(parts) > 1 else []
        out[city][ind] = {'primary': primary, 'reserve': reserve}

json.dump(out, open('/tmp/weakfit.json', 'w'), indent=1)

print('CITY          PRIMARY  weak   RESERVE  weak')
for city, inds in out.items():
    p = sum(len(v['primary']) for v in inds.values())
    pw = sum(1 for v in inds.values() for r in v['primary'] if r['weak'])
    rs = sum(len(v['reserve']) for v in inds.values())
    rw = sum(1 for v in inds.values() for r in v['reserve'] if r['weak'])
    print(f'{city:12} {p:6}  {pw:4}   {rs:6}  {rw:4}')

print()
print('#' * 72)
print('WEAK FITS IN PRIMARY PICKS ONLY (these are what visitors are shown)')
print('#' * 72)
for city, inds in out.items():
    hits = [(i, r) for i, v in inds.items() for r in v['primary'] if r['weak']]
    print(f'\n===== {city}: {len(hits)} weak primary picks')
    for ind, r in hits:
        kind = 'other country' if 'other country' in r['reason'] else 'off-theme'
        print(f"  [{ind}] {r['title']}")
        print(f"      {r['provider']} | {r['access']} | local={r['local']} | {kind}")
