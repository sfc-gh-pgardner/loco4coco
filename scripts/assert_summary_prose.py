"""Check the summary assembly reads as prose for every shape of answer.

Mirrors platformBit()/buildSummary() in index.html against the config templates,
so a dangling clause or a chip label read as a noun fails here rather than at a
booth.
"""
import io
import json
import re

cfg = json.load(io.open('game/config.json', encoding='utf-8'))
TPL = cfg['sovereignty']['summary']


def join_list(a):
    return a[0] if len(a) == 1 else ', '.join(a[:-1]) + ' and ' + a[-1]


def platform_bit(plats):
    already = any(re.search(r'already in snowflake', p, re.I) for p in plats)
    unsure = any(re.search(r'not sure', p, re.I) for p in plats)
    named = [p for p in plats
             if not re.search(r'already in snowflake|not sure', p, re.I)]
    if named and already:
        return ('Your data sits on ' + join_list(named)
                + ', and some of it is already in Snowflake. ')
    if named and unsure:
        return ('Your data sits on ' + join_list(named)
                + ', and we will pin down the rest together. ')
    if named:
        return 'Your data sits on ' + join_list(named) + '. '
    if already:
        return ('Your data is already in Snowflake, so we can start on it '
                'straight away. ')
    if unsure:
        return 'We will work out where your data lives together. '
    return ''


def build(first, company, industry, plats, region):
    bits = {
        '{first_name}': first or 'right',
        '{company_bit}': (f'You are at {company}' + ('' if industry else '. ')) if company else '',
        '{industry_bit}': (((', in ' if company else 'You work in ') + industry + '. ')
                           if industry else ''),
        '{platform_bit}': platform_bit(plats),
        '{region}': region,
    }
    out = []
    for t in TPL:
        s = t
        for k, v in bits.items():
            s = s.replace(k, v)
        out.append(re.sub(r'\s{2,}', ' ', s).strip())
    return out


CASES = [
    ('everything given', 'Priya', 'NHS Trust', 'Healthcare & Life Sciences',
     ['Oracle', 'Already in Snowflake'], 'the UK'),
    ('only snowflake', 'Sam', 'Acme', 'Financial Services',
     ['Already in Snowflake'], 'the UK'),
    ('only not sure', 'Sam', 'Acme', 'Retail & Consumer Goods',
     ['Not sure yet'], 'the region you choose'),
    ('named + not sure', 'Sam', 'Acme', 'Energy & Utilities',
     ['AWS', 'Not sure yet'], 'the EU'),
    ('no company', 'Sam', '', 'Public Sector & Government', ['AWS'], 'the UK'),
    ('no industry', 'Sam', 'Acme', '', ['AWS'], 'the UK'),
    ('nothing but a name', 'Sam', '', '', [], 'the region you choose'),
    ('three platforms', 'Sam', 'Acme', 'Manufacturing & Industrial',
     ['Microsoft / Azure', 'AWS', 'SAP'], 'Germany'),
]

fails = []
for label, first, co, ind, plats, region in CASES:
    lines = build(first, co, ind, plats, region)
    print(f"\n[{label}]")
    print("  " + lines[0])
    for ln in lines:
        if re.search(r'\s,|,\s*\.|\.\s*\.|\bin \.|\bat \.', ln):
            fails.append(f"{label}: punctuation -> {ln[:90]}")
        if re.search(r'on (Already in Snowflake|Not sure yet)', ln):
            fails.append(f"{label}: chip label read as a platform -> {ln[:90]}")
        if '{' in ln or '}' in ln:
            fails.append(f"{label}: unfilled placeholder -> {ln[:90]}")
        if re.search(r'  ', ln):
            fails.append(f"{label}: double space -> {ln[:90]}")

print("\n" + "=" * 60)
if fails:
    print(f"FAILURES ({len(fails)}):")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("all summary shapes read as prose")
