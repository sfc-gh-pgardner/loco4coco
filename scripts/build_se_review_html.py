#!/usr/bin/env python3
"""Generate audit/marketplace-se-review.html from marketplace.json (+ the media
candidates file), so the SE review sheet always matches the shipping data and
every listing links to its Marketplace page.

    python3 scripts/build_se_review_html.py
"""

import html
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REFS = os.path.join(ROOT, "skills", "loco4coco", "references")
JSON_PATH = os.path.join(REFS, "marketplace.json")
CAND_PATH = os.path.join(REFS, "marketplace-candidates.json")
OUT = os.path.join(ROOT, "audit", "marketplace-se-review.html")
LISTING = "https://app.snowflake.com/marketplace/listing/"

INDUSTRY_LABEL = {
    "healthcare": "Healthcare & Life Sciences", "financial": "Financial Services",
    "retail": "Retail & Consumer Goods", "public": "Public Sector & Government",
    "manufacturing": "Manufacturing & Industrial", "energy": "Energy & Utilities",
    "media": "Media, Telco & Entertainment", "other": "Something else (other)",
}
ORDER = ["healthcare", "financial", "retail", "public", "manufacturing",
         "energy", "media", "other"]


def avail(regions, token):
    return regions == "ALL" or token in (regions or "")


def cell(regions, ready, token):
    if not avail(regions, token):
        return '<td class="c no">✗</td>'
    return '<td class="c warn">⚠</td>' if not ready else '<td class="c yes">✓</td>'


def link(gn, title):
    return '<a href="%s%s" target="_blank" rel="noopener">%s</a>' % (
        LISTING, html.escape(gn or ""), html.escape(title or ""))


def rows_table(rows):
    out = ['<div class="table-wrap"><table>',
           '<thead><tr><th>Dataset</th><th>Provider</th><th>Access</th>'
           '<th class="c">Lon</th><th class="c">Par</th><th class="c">Fra/Ber</th>'
           '<th class="verdict">SE verdict</th></tr></thead><tbody>']
    for r in rows:
        reg, rd = r.get("regions") or "", bool(r.get("ready"))
        out.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td>%s%s%s<td class=\"verdict\"></td></tr>" % (
                link(r.get("global_name"), r.get("title")),
                html.escape(r.get("provider") or ""),
                html.escape(r.get("access") or ""),
                cell(reg, rd, "AWS_EU_WEST_2"),
                cell(reg, rd, "AWS_EU_WEST_3"),
                cell(reg, rd, "AWS_EU_CENTRAL_1")))
    out.append("</tbody></table></div>")
    return "\n".join(out)


def survivor_count(rows, token):
    return sum(1 for r in rows if avail(r.get("regions") or "", token))


def main():
    data = json.load(open(JSON_PATH, encoding="utf-8"))
    uk = data["profiles"]["uk"]
    cand = {}
    if os.path.exists(CAND_PATH):
        cand = json.load(open(CAND_PATH, encoding="utf-8")).get("profiles", {})

    parts = []
    # summary
    parts.append('<h2 id="summary">Summary — datasets surviving per industry × region</h2>')
    parts.append('<div class="table-wrap"><table><thead><tr><th>Industry</th>'
                 '<th class="c">London</th><th class="c">Paris</th>'
                 '<th class="c">Frankfurt / Berlin</th></tr></thead><tbody>')
    for ind in ORDER:
        rows = uk[ind]["primary"]
        n = len(rows)
        parts.append("<tr><td>%s</td><td class=\"c\">%d/%d</td><td class=\"c\">%d/%d</td>"
                     "<td class=\"c\">%d/%d</td></tr>" % (
                         INDUSTRY_LABEL[ind],
                         survivor_count(rows, "AWS_EU_WEST_2"), n,
                         survivor_count(rows, "AWS_EU_WEST_3"), n,
                         survivor_count(rows, "AWS_EU_CENTRAL_1"), n))
    parts.append("</tbody></table></div>")

    # per-industry current picks
    parts.append('<h2 id="industries">Current picks per industry (uk profile)</h2>')
    parts.append('<p class="sub">Titles link to the Marketplace listing. The SE '
                 'verdict column is blank for you to fill.</p>')
    for ind in ORDER:
        parts.append("<h3>%s</h3>" % INDUSTRY_LABEL[ind])
        parts.append(rows_table(uk[ind]["primary"]))
        res = uk[ind].get("reserve") or []
        if res:
            parts.append('<p class="sub">Reserves:</p>')
            parts.append(rows_table(res))

    # media candidates
    if cand:
        parts.append('<h2 id="media-candidates">Media candidates for review (deterministic)</h2>')
        parts.append('<div class="callout">New, region-verified, importable media '
                     'listings to fill the sparse media stall. Provider/access are '
                     'flagged for SE confirmation (they cannot be scraped). Assign '
                     '6 primary + reserves per profile, then promote into marketplace.json.</div>')
        for prof in ("uk", "fr", "de"):
            rows = (cand.get(prof) or {}).get("media") or []
            if not rows:
                continue
            parts.append("<h3>profile: %s</h3>" % prof)
            out = ['<div class="table-wrap"><table><thead><tr><th>Candidate</th>'
                   '<th>Global name</th><th>SWT regions</th><th class="verdict">SE verdict</th>'
                   '</tr></thead><tbody>']
            for r in rows:
                out.append("<tr><td>%s</td><td><code>%s</code></td><td>%s</td>"
                           "<td class=\"verdict\"></td></tr>" % (
                               link(r.get("global_name"), r.get("title")),
                               html.escape(r.get("global_name") or ""),
                               html.escape(r.get("regions_swt") or "")))
            out.append("</tbody></table></div>")
            parts.append("\n".join(out))

    body = "\n".join(parts)
    doc = TEMPLATE.replace("{{GENERATED}}", time.strftime("%Y-%m-%d")).replace("{{BODY}}", body)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print("wrote", OUT)


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="snowflake-source" content="cortex-agent-authored" />
  <title>Loco for CoCo — Marketplace SE review</title>
  <style>
    :root { color-scheme: light dark; }
    body { font-family: -apple-system, system-ui, sans-serif; max-width: 1000px;
      width: 100%; box-sizing: border-box; margin: 0 auto; padding: clamp(16px,4vw,28px);
      color: light-dark(#1f2937,#e5e7eb); line-height: 1.5; }
    h1,h2,h3 { color: light-dark(#0f172a,#f1f5f9); }
    h2 { margin-top: 30px; border-bottom: 2px solid #29B5E8; padding-bottom: 4px; }
    a { color: light-dark(#166184,#67B5ED); }
    .sub { color: light-dark(#64748b,#94a3b8); }
    .callout { background: light-dark(#f1f5f9,#1f2937); border-left: 4px solid #ED8D30;
      border-radius: 8px; padding: 12px 16px; margin: 14px 0; }
    .legend { background: light-dark(#f1f5f9,#1f2937); border:1px solid light-dark(#d1d5db,#374151);
      border-radius: 8px; padding: 12px 16px; margin: 14px 0; }
    .table-wrap { overflow-x: auto; margin: 8px 0; }
    table { border-collapse: collapse; width: 100%; font-size: 14px; }
    th,td { border: 1px solid light-dark(#d1d5db,#374151); padding: 6px 9px; text-align: left; }
    td.c, th.c { text-align: center; white-space: nowrap; }
    .yes { color: light-dark(#2f8f39,#79BE7E); font-weight: 700; }
    .no  { color: light-dark(#b4231a,#DF6C5A); font-weight: 700; }
    .warn{ color: light-dark(#a86a12,#E5C872); font-weight: 700; }
    .verdict { background: light-dark(#fffdf5,#23262f); min-width: 130px; }
    code { background: light-dark(#eef2f7,#0f172a); padding: 1px 4px; border-radius: 4px; font-size: 12px; }
  </style>
</head>
<body>
  <h1>Marketplace — SE review</h1>
  <p class="sub">Loco for CoCo · per industry × cloud region · generated {{GENERATED}} · from marketplace.json</p>
  <div class="legend"><strong>Regions</strong>: London → <code>AWS_EU_WEST_2</code> ·
    Paris → <code>AWS_EU_WEST_3</code> · Frankfurt &amp; Berlin → <code>AWS_EU_CENTRAL_1</code>.<br>
    <strong>Key</strong>: <span class="yes">✓</span> available &amp; importable ·
    <span class="warn">⚠</span> region-available but not ready-for-import (needs request/trial) ·
    <span class="no">✗</span> not offered in that region. Titles link to the Marketplace listing.</div>
  {{BODY}}
  <h2>What the review feeds</h2>
  <p>Confirm fit, provider and access per row; for each ✗/⚠ where an industry thins out,
  pick a region-appropriate replacement (local FR/DE datasets for Paris/Berlin). Approved
  media candidates are promoted into <code>marketplace.json</code> then mirrored and reloaded.</p>
</body>
</html>
"""

if __name__ == "__main__":
    main()
