#!/usr/bin/env python3
"""Verify the feature -> documentation URL map used in visitor blueprints.

Every Snowflake feature named in a blueprint must carry a working docs link, and
a fabricated URL in something a visitor takes away is worse than no link at all.
So the map is bundled (instant at the booth, survives venue wifi) and verified
here before each event.

    python3 scripts/build_feature_docs.py            # verify the bundled map
    python3 scripts/build_feature_docs.py --write    # rewrite feature-docs.md

Checks with GET, never HEAD: a signed or redirecting URL can 403 on HEAD while
serving fine on GET, which has produced a false failure here before.

Exits non-zero if ANY url fails, so a broken link cannot pass unnoticed.
"""

import argparse
import concurrent.futures
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
OUT = os.path.join(PLUGIN, "skills", "loco4coco", "references", "feature-docs.md")
BASE = "https://docs.snowflake.com"

# The closed list. The Workshop prompt may only choose features from here, so a
# link exists by construction rather than by lookup-and-hope.
# group -> [(canonical feature name, docs path)]
FEATURES = {
    "Cortex AI services": [
        ("Cortex Search", "/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview"),
        ("Cortex Analyst", "/en/user-guide/snowflake-cortex/cortex-analyst"),
        ("Cortex Agents", "/en/user-guide/snowflake-cortex/cortex-agents"),
        ("Snowflake Intelligence", "/en/user-guide/snowflake-cortex/snowflake-cowork"),
        ("Cortex Playground", "/en/user-guide/snowflake-cortex/cortex-playground"),
        ("Cortex Fine-tuning", "/en/user-guide/snowflake-cortex/cortex-finetuning"),
        ("Document AI", "/en/user-guide/snowflake-cortex/ai-documents"),
    ],
    "AISQL functions": [
        ("AISQL functions", "/en/user-guide/snowflake-cortex/aisql"),
        ("AI_COMPLETE", "/en/sql-reference/functions/ai_complete"),
        ("AI_EXTRACT", "/en/sql-reference/functions/ai_extract"),
        ("AI_CLASSIFY", "/en/sql-reference/functions/ai_classify"),
        ("AI_FILTER", "/en/sql-reference/functions/ai_filter"),
        ("AI_AGG", "/en/sql-reference/functions/ai_agg"),
        ("AI_SUMMARIZE_AGG", "/en/sql-reference/functions/ai_summarize_agg"),
        ("AI_SENTIMENT", "/en/sql-reference/functions/ai_sentiment"),
        ("AI_PARSE_DOCUMENT", "/en/sql-reference/functions/ai_parse_document"),
        ("AI_TRANSCRIBE", "/en/sql-reference/functions/ai_transcribe"),
        ("AI_TRANSLATE", "/en/sql-reference/functions/ai_translate"),
        ("AI_EMBED", "/en/sql-reference/functions/ai_embed"),
        ("AI_SIMILARITY", "/en/sql-reference/functions/ai_similarity"),
        ("AI_REDACT", "/en/sql-reference/functions/ai_redact"),
    ],
    "Modelling and semantics": [
        ("Semantic Views", "/en/user-guide/views-semantic/overview"),
        ("Dynamic Tables", "/en/user-guide/dynamic-tables/overview"),
        ("Materialized Views", "/en/user-guide/views-materialized"),
        ("Iceberg Tables", "/en/user-guide/tables-iceberg"),
        ("External Tables", "/en/user-guide/tables-external-intro"),
        ("Hybrid Tables", "/en/user-guide/tables-hybrid"),
    ],
    "Apps and interfaces": [
        ("Streamlit in Snowflake", "/en/developer-guide/streamlit/about-streamlit"),
        ("Snowflake Notebooks", "/en/user-guide/ui-snowsight/notebooks"),
        ("Snowpark Python", "/en/developer-guide/snowpark/python/index"),
    ],
    "Pipelines and ingestion": [
        ("Streams", "/en/user-guide/streams-intro"),
        ("Tasks", "/en/user-guide/tasks-intro"),
        ("Snowpipe Streaming", "/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-overview"),
        ("Snowpipe", "/en/user-guide/data-load-snowpipe-intro"),
        ("Openflow", "/en/user-guide/data-integration/openflow/about"),
        ("Alerts", "/en/user-guide/alerts"),
    ],
    "Machine learning": [
        ("ML Forecasting", "/en/user-guide/ml-functions/forecasting"),
        ("ML Anomaly Detection", "/en/user-guide/ml-functions/anomaly-detection"),
        ("ML Classification", "/en/user-guide/ml-functions/classification"),
        ("ML Top Insights", "/en/user-guide/ml-functions/top-insights"),
        ("Snowflake Model Registry", "/en/developer-guide/snowflake-ml/model-registry/overview"),
        ("Snowflake Feature Store", "/en/developer-guide/snowflake-ml/feature-store/overview"),
    ],
    "Sharing and collaboration": [
        ("Secure Data Sharing", "/en/user-guide/data-sharing-intro"),
        ("Snowflake Marketplace", "/en/collaboration/collaboration-listings-about"),
        ("Data Clean Rooms", "/en/user-guide/cleanrooms/overview"),
    ],
    "Governance and quality": [
        ("Masking Policies", "/en/user-guide/security-column-ddm-intro"),
        ("Row Access Policies", "/en/user-guide/security-row-intro"),
        ("Data Classification", "/en/user-guide/classify-intro"),
        ("Object Tagging", "/en/user-guide/object-tagging/introduction"),
        ("Data Metric Functions", "/en/user-guide/data-quality-intro"),
        ("Access History", "/en/user-guide/access-history"),
        ("Time Travel", "/en/user-guide/data-time-travel"),
        ("Search Optimization Service", "/en/user-guide/search-optimization-service"),
    ],
}


def check(url, attempts=3):
    """Retry on 429 and 5xx only. Those are the docs site rate-limiting a
    parallel sweep, and a transient 503 must not block a release. A 404 is a
    real broken link and is never retried into passing."""
    last = (0, False, "no attempt")
    for i in range(attempts):
        req = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": "loco4coco-verify/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                final = r.geturl()
                return r.status, (final.rstrip("/") != url.rstrip("/")), final
        except urllib.error.HTTPError as e:
            last = (e.code, False, url)
            if e.code not in (429, 500, 502, 503, 504):
                return last
        except Exception as e:                                   # noqa: BLE001
            last = (0, False, f"{type(e).__name__}: {e}")
        time.sleep(1.5 * (i + 1))
    return last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="rewrite feature-docs.md")
    a = ap.parse_args()

    items = [(g, n, BASE + p) for g, lst in FEATURES.items() for n, p in lst]
    print(f"Verifying {len(items)} feature documentation URLs...\n")

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(check, url): (g, n, url) for g, n, url in items}
        for fut in concurrent.futures.as_completed(futs):
            g, n, url = futs[fut]
            results[n] = (g, url) + fut.result()

    failing, redirecting = [], []
    for n, (g, url, code, moved, final) in sorted(results.items()):
        if code != 200:
            failing.append((n, url, code, final))
        elif moved:
            redirecting.append((n, url, final))

    for n, url, code, final in failing:
        print(f"  FAIL {code}  {n}\n         {url}\n         {final}")
    for n, url, final in redirecting:
        print(f"  MOVED    {n}\n         {url}\n      -> {final}")

    ok = len(items) - len(failing)
    print(f"\n{ok} of {len(items)} OK, {len(failing)} failing, "
          f"{len(redirecting)} redirecting")

    if failing:
        print("\nRefusing to write a map containing broken links. A dead URL in "
              "a blueprint a visitor keeps is worse than no link.")
        return 1

    if a.write:
        write_md(results)
        print(f"\nwrote {OUT}")
    else:
        print("\n(verify only - pass --write to regenerate feature-docs.md)")
    return 0


def write_md(results):
    from datetime import date
    lines = [
        "---",
        "name: feature-docs",
        'description: "Closed list of Snowflake features the Workshop may name, '
        'each with a verified docs.snowflake.com URL. Bundled so blueprints '
        'resolve instantly and cannot contain a fabricated link. Rebuild with '
        'scripts/build_feature_docs.py before each event."',
        "---",
        "",
        "# Feature documentation map",
        "",
        f"**Verified:** {date.today().isoformat()} - every URL returned HTTP 200 "
        "on that date.",
        f"**Count:** {len(results)} features.",
        "",
        "## Why a closed list",
        "",
        "Features used to arrive as free text from the model, so there was "
        "nothing reliable to link. The Workshop prompt now selects **only** from "
        "the names below, which means every feature in a blueprint has a working "
        "link by construction. A name outside this list is dropped rather than "
        "rendered bare - silently omitting one is better than shipping a guess.",
        "",
        "Match on the exact name in the first column.",
        "",
    ]
    groups = {}
    for name, (g, url, _c, _m, _f) in results.items():
        groups.setdefault(g, []).append((name, url))
    for g in FEATURES:
        lines += [f"## {g}", "", "| Feature | Documentation |", "|---|---|"]
        for name, url in sorted(groups.get(g, [])):
            lines.append(f"| {name} | {url} |")
        lines.append("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
