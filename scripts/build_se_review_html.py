#!/usr/bin/env python3
"""Generate audit/marketplace-se-review.html from marketplace.json (+ candidates).

Three tabs, one per SWT EVENT: London, Paris, Berlin. Each tab holds that event's
per-industry suggestions, chosen for LOCAL relevance to that city's country.

Why there is no per-region matrix any more: every SWT event account is stood up in
AWS Frankfurt, so the cloud region is CONSTANT (AWS_EU_CENTRAL_1) across all three
events. The only region question left is a single flag - "can this be imported on
an eu-central-1 account?" - so that is all this shows. Locality is what varies.

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

# event tab -> (profile, country, the EVENT LOCATION's region). The booth account
# is always AWS Frankfurt, but a visitor never imports at the booth - they open
# the links later from their own account - so a pick is judged on availability
# where the VISITORS are, not where the booth writes.
EVENTS = [("London", "uk", "United Kingdom", "AWS_EU_WEST_2"),
          ("Paris", "fr", "France", "AWS_EU_WEST_3"),
          ("Berlin", "de", "Germany", "AWS_EU_CENTRAL_1")]

INDUSTRY_LABEL = {
    "healthcare": "Healthcare &amp; Life Sciences", "financial": "Financial Services",
    "retail": "Retail &amp; Consumer Goods", "public": "Public Sector &amp; Government",
    "manufacturing": "Manufacturing &amp; Industrial", "energy": "Energy &amp; Utilities",
    "media": "Media, Telco &amp; Entertainment", "other": "Something else (other)",
}
ORDER = ["healthcare", "financial", "retail", "public", "manufacturing",
         "energy", "media", "other"]


def importable(r, region):
    reg = r.get("regions") or ""
    in_region = reg == "ALL" or region in reg
    if not in_region:
        return '<td class="c no" title="Not offered in %s">\u2717</td>' % region
    if not r.get("ready", True):
        return '<td class="c warn" title="Available but needs a request/trial">\u26a0</td>'
    return '<td class="c yes">\u2713</td>'


def link(gn, title):
    return '<a href="%s%s" target="_blank" rel="noopener">%s</a>' % (
        LISTING, html.escape(gn or ""), html.escape(title or ""))


def table(rows, region):
    out = ['<div class="table-wrap"><table><thead><tr><th>Dataset</th>'
           '<th>Provider</th><th>Access</th>'
           '<th class="c" title="Available in this event\'s region">Local</th>'
           '<th class="verdict">SE verdict</th></tr></thead><tbody>']
    for r in rows:
        out.append("<tr><td>%s</td><td>%s</td><td>%s</td>%s<td class=\"verdict\"></td></tr>" % (
            link(r.get("global_name"), r.get("title")),
            html.escape(r.get("provider") or ""),
            html.escape(r.get("access") or ""),
            importable(r, region)))
    out.append("</tbody></table></div>")
    return "\n".join(out)


def cand_table(rows):
    out = ['<div class="table-wrap"><table><thead><tr><th>Candidate</th>'
           '<th>Provider</th><th>Global name</th><th class="verdict">SE verdict</th>'
           '</tr></thead><tbody>']
    for r in rows:
        out.append("<tr><td>%s</td><td>%s</td><td><code>%s</code></td>"
                   "<td class=\"verdict\"></td></tr>" % (
                       link(r.get("global_name"), r.get("title")),
                       html.escape(r.get("provider") or "(to confirm)"),
                       html.escape(r.get("global_name") or "")))
    out.append("</tbody></table></div>")
    return "\n".join(out)


def main():
    data = json.load(open(JSON_PATH, encoding="utf-8"))["profiles"]
    cand = {}
    if os.path.exists(CAND_PATH):
        cand = json.load(open(CAND_PATH, encoding="utf-8")).get("profiles", {})

    tabs, panes = [], []
    for i, (event, profile, country, region) in enumerate(EVENTS):
        active = " active" if i == 0 else ""
        tabs.append('<button class="tab%s" data-pane="pane-%s">%s</button>'
                    % (active, profile, event))
        body = ['<p class="sub">Suggestions chosen for local relevance to '
                '<strong>%s</strong>, and judged on availability in '
                '<code>%s</code> \u2014 the region this event\'s visitors live in. '
                'The booth account is in AWS Frankfurt, but that is irrelevant here: '
                'nobody imports anything at the booth.</p>' % (country, region)]
        prof = data.get(profile) or {}
        curated_any = any((prof.get(ind) or {}).get("primary") for ind in ORDER)
        if not curated_any:
            body.append('<div class="callout">No curated picks for this event yet. '
                        'Agentic locality curation is pending; any candidates found '
                        'so far are listed below for review.</div>')
        for ind in ORDER:
            block = prof.get(ind) or {}
            prim = block.get("primary") or []
            res = block.get("reserve") or []
            if not prim and not res:
                continue
            body.append("<h3>%s</h3>" % INDUSTRY_LABEL[ind])
            if prim:
                body.append(table(prim, region))
            if res:
                body.append('<p class="sub">Reserves:</p>')
                body.append(table(res, region))
        # candidates awaiting promotion
        cprof = cand.get(profile) or {}
        cany = {k: v for k, v in cprof.items() if v}
        if cany:
            body.append('<h3>Candidates awaiting review</h3>')
            for ind, rows in cany.items():
                body.append("<p class=\"sub\"><strong>%s</strong></p>"
                            % INDUSTRY_LABEL.get(ind, ind))
                body.append(cand_table(rows))
        panes.append('<section class="pane%s" id="pane-%s">%s</section>'
                     % (active, profile, "\n".join(body)))

    doc = TEMPLATE.replace("{{GENERATED}}", time.strftime("%Y-%m-%d")) \
                  .replace("{{TABS}}", "\n".join(tabs)) \
                  .replace("{{PANES}}", "\n".join(panes))
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
    h3 { margin-top: 22px; }
    a { color: light-dark(#166184,#67B5ED); }
    .sub { color: light-dark(#64748b,#94a3b8); }
    .legend, .callout { background: light-dark(#f1f5f9,#1f2937);
      border: 1px solid light-dark(#d1d5db,#374151); border-radius: 8px;
      padding: 12px 16px; margin: 14px 0; }
    .callout { border-left: 4px solid #ED8D30; }
    .tabs { display: flex; flex-wrap: wrap; gap: 6px; margin: 18px 0 0; }
    .tab { font: inherit; cursor: pointer; padding: 9px 18px;
      background: light-dark(#e8edf3,#252b36); color: inherit;
      border: 1px solid light-dark(#d1d5db,#374151); border-bottom: none;
      border-radius: 8px 8px 0 0; }
    .tab.active { background: #29B5E8; color: #0b1220; font-weight: 700; }
    .pane { display: none; border: 1px solid light-dark(#d1d5db,#374151);
      border-radius: 0 8px 8px 8px; padding: clamp(12px,3vw,20px); }
    .pane.active { display: block; }
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
  <p class="sub">Loco for CoCo · one tab per SWT event · generated {{GENERATED}} · from marketplace.json</p>
  <div class="legend">
    Each event runs on its <strong>own ephemeral account, all in AWS Frankfurt</strong> — but
    <strong>that is not what decides these recommendations</strong>. Visitors never import
    anything at the booth: they leave with links and open them later from their own account.
    So each tab judges a dataset on local relevance to that city and on availability in
    <strong>the event's own region</strong> (London eu-west-2, Paris eu-west-3, Berlin eu-central-1).<br>
    <strong>Local</strong>: <span class="yes">✓</span> available in this event's region ·
    <span class="warn">⚠</span> available but needs a request/trial ·
    <span class="no">✗</span> not offered in this event's region.
    Titles link to the Marketplace listing.
  </div>
  <div class="tabs">{{TABS}}</div>
  {{PANES}}
  <script>
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(function (t) {
      t.addEventListener('click', function () {
        document.querySelectorAll('.tab').forEach(function (x) { x.classList.remove('active'); });
        document.querySelectorAll('.pane').forEach(function (p) { p.classList.remove('active'); });
        t.classList.add('active');
        const pane = document.getElementById(t.dataset.pane);
        if (pane) { pane.classList.add('active'); }
      });
    });
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
