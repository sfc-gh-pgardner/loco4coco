#!/usr/bin/env python3
"""Assert that config copy actually reaches the screen.

WHY THIS EXISTS: the letter's sentences were hardcoded in index.html while
config.intake.letter.body sat unread. Editing config changed the generated
decision tree and never changed what a visitor read, so the document claimed
"Proof of Concept (POC)" while the letter still said "MVP/POC" - a discrepancy
no amount of config-to-document checking could catch, because both sides of that
comparison agreed with each other and disagreed with the app.

So this checks the third edge: config -> screen. For every block of visitor
copy in config, the client must READ it rather than restate it, and no sentence
long enough to be prose may be hardcoded in the markup.

    python3 scripts/assert_config_reaches_screen.py
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
cfg = json.load(io.open(os.path.join(ROOT, 'game', 'config.json'),
                        encoding='utf-8'))
html = io.open(os.path.join(ROOT, 'game', 'index.html'), encoding='utf-8').read()

fails = []
notes = []

# ---------------------------------------------------------------- 1. read, not restate
# Copy blocks that must be reached through CFG, with the access path the client
# is expected to use. A block listed here and NOT read is the defect above.
MUST_READ = [
    ('intro.body', r'\bintro\b[^\n]{0,40}\bbody\b|CFG\.intro'),
    ('intake.letter.body', r'\bl\.body\b|letter\.body|L\(\)\.body'),
    ('intake.letter.signoff', r'l\.signoff|letter\.signoff'),
    ('sovereignty.summary', r'sovereignty\|\|\{\}\)\.summary|\.summary\b'),
    ('sovereignty.react', r"sov\(|sovereignty[^\n]{0,20}react"),
    ('sovereignty.pillars', r'pillars'),
    ('platforms.options', r'CFG\.platforms|platforms\|\|\{\}\)\.options'),
    ('country.options', r'CFG\.country|country\|\|\{\}\)'),
    ('platforms.heading', r'P\.heading|platforms[^\n]{0,24}heading'),
    ('country.heading', r'C\.heading|country[^\n]{0,24}heading'),
]
for label, pattern in MUST_READ:
    node = cfg
    for part in label.split('.'):
        node = (node or {}).get(part) if isinstance(node, dict) else None
    if not node:
        notes.append(f'{label}: absent from config, nothing to read')
        continue
    if not re.search(pattern, html):
        fails.append(f'{label} exists in config but the client never reads it')

# ------------------------------------------------- 2. no prose hardcoded in markup
# Scan ALL markup, not a region of it. The first version of this check scanned
# from id="ov-letter" to the first HTML comment, which stopped short of the very
# sentence it existed to catch and therefore passed while the defect was live.
markup = re.sub(r'<script\b.*?</script>', '', html, flags=re.S)
markup = re.sub(r'<style\b.*?</style>', '', markup, flags=re.S)
markup = re.sub(r'<!--.*?-->', '', markup, flags=re.S)
for m in re.finditer(r'>([^<>{}]{40,})<', markup):
    text = ' '.join(m.group(1).split())
    if text.count(' ') < 6:
        continue
    if not re.search(r'\b[a-z]{3,}\b\s+\b[a-z]{2,}\b', text):
        continue                          # not prose: ids, classes, urls
    fails.append(f'prose hardcoded in markup: {text[:74]!r}')

# --------------------------------------------- 3. config strings must not be duplicated
# A sentence that appears in BOTH config and the markup is the same defect in
# waiting: whichever the client happens to use, the other is a lie.
def walk(node, path=''):
    if isinstance(node, dict):
        for k, v in node.items():
            if not k.startswith('_'):
                walk(v, f'{path}.{k}' if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f'{path}[{i}]')
    elif isinstance(node, str) and node.count(' ') >= 6:
        # Placeholders differ between config and markup, so compare the stem.
        stem = node.split('{')[0].strip()
        if len(stem) >= 45 and stem in html:
            fails.append(f'{path} is in config AND hardcoded in markup: '
                         f'{stem[:60]!r}')


walk(cfg)

# ------------------------------------------------------------------------ report
print(f'checked {len(MUST_READ)} copy blocks against '
      f'{len(html)} chars of client')
for n in notes:
    print('  note:', n)
if fails:
    print(f'\nFAILURES ({len(fails)}):')
    for f in fails:
        print('  -', f)
    sys.exit(1)
print('\nevery config copy block is read by the client, and no config sentence '
      'is hardcoded in the markup')
