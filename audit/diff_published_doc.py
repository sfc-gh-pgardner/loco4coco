"""Which decision-tree content has ACTUALLY drifted, ignoring render styling.

The plain-text renderer differs from the Doc cosmetically by design: bullets use
a different glyph, headings are upper-cased, and table rows gain "Stop: " /
"Selection: " / "Setting: " column labels. None of that is drift. Normalise it
away so what is left is real: sentences present in one and not the other.
"""
import json
import re
import sys
import difflib

env = json.load(open(sys.argv[1]))
d = env["output"]
if isinstance(d, str):
    d = json.loads(d)

doc = []
for el in d["body"]["content"]:
    p = el.get("paragraph")
    if not p:
        continue
    doc.append("".join(e.get("textRun", {}).get("content", "")
                       for e in p["elements"]).rstrip())

want = [l.rstrip() for l in open(sys.argv[2])]


def norm(s):
    s = s.strip().lstrip("\u2022-*\u00b7 ").strip()
    s = re.sub(r"\b(Stop|Selection|Setting|#|What the visitor gives us):\s*", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.lower()


a = [x for x in (norm(s) for s in doc) if x]
b = [x for x in (norm(s) for s in want) if x]
amap, bmap = {}, {}
for s in doc:
    if norm(s):
        amap.setdefault(norm(s), s.strip())
for s in want:
    if norm(s):
        bmap.setdefault(norm(s), s.strip())

sm = difflib.SequenceMatcher(None, a, b)
print("real similarity: %.1f%%\n" % (sm.ratio() * 100))
d_only, r_only = [], []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    d_only += a[i1:i2]
    r_only += b[j1:j2]

print("=== IN THE DOC, NOT IN THE CURRENT RENDER (%d) ===" % len(d_only))
for x in d_only:
    print("  - " + amap.get(x, x)[:170])
print("\n=== IN THE CURRENT RENDER, MISSING FROM THE DOC (%d) ===" % len(r_only))
for x in r_only:
    print("  + " + bmap.get(x, x)[:170])
