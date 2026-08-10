#!/usr/bin/env python3
"""Maintain the Loco4CoCo curated guides index.

TWO JOBS, ONE OF WHICH THIS SCRIPT CANNOT DO ALONE
--------------------------------------------------
1. VERIFY (automated, the safety-critical half) - every slug committed in
   guides-index.md is fetched and must return HTTP 200. Redirects and failures
   are reported so no unverified URL is ever shipped to a visitor. This works
   with the standard library alone and is the default mode.

2. HARVEST (needs a browser - see below) - discovering the full corpus so the
   curation can be refreshed with newly published guides.

Why harvest needs a browser: the listing at /en/developers/guides/ is an AEM
single-page app. Its pagination LOOKS server-driven (the URL becomes
?page=15&pageSize=12&offset=180) but the server ignores those parameters and
re-renders the same first 15 cards every time; pageSize is capped server-side
too. Verified 2026-08-05: paging via plain HTTP yields 15 guides, not 565. An
earlier version of this script did exactly that and exited successfully having
found 15 of 565 - a check that passed without checking. Do not reintroduce it.

To refresh the corpus, drive the real listing with the CoCo browser tool and
click through the pagination, then feed the result back here:

  a. browser_navigate to https://www.snowflake.com/en/developers/guides/
  b. browser_evaluate the harvester below. Note browser_evaluate does NOT await
     promises, so start a self-scheduling loop and poll it separately.
  c. Poll until __DONE__, then dump window.__ALL__ to a JSON file.
  d. Re-run this script with --corpus <that file> to diff against the curation.

     var findNext = function () {
       var p = [].slice.call(document.querySelectorAll(
         'p.snowflake-filterable-and-searchable-grid-pagination-navigation-label'
       )).filter(function (e) { return e.textContent.trim() === 'Next'; })[0];
       return p ? (p.closest('div') || p.parentElement) : null;
     };
     window.__ALL__ = {}; window.__PAGES__ = 0; window.__DONE__ = false;
     function harvest() {
       document.querySelectorAll('a[href*="/developers/guides/"]').forEach(function (a) {
         var href = (a.getAttribute('href') || '').split('?')[0];
         if (!/\\/developers\\/guides\\/[a-z0-9-]+\\/$/.test(href)) return;
         var h = a.querySelector('h1,h2,h3,h4,h5');
         if (h) window.__ALL__[href] = {
           t: h.innerText.trim().replace(/\\s+/g, ' '),
           m: (a.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 180)
         };
       });
     }
     (function step() {
       harvest(); window.__PAGES__++;
       var n = findNext();
       if (!n || window.__PAGES__ > 58) { window.__DONE__ = true; return; }
       n.click(); setTimeout(step, 750);
     })();

   Pagination wraps rather than stopping at the last page, so start from page 1
   and watch the running total plateau. The 2026-08-05 run collected 565 of the
   653 guides the site reported; the shortfall is landing/industry pages and
   cards with no parseable heading.

Usage
  python3 build_guides_index.py                     # verify curated slugs
  python3 build_guides_index.py --corpus corpus.json # verify + diff vs corpus
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = "https://www.snowflake.com/en/developers/guides/"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120 Safari/537.36"
)
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INDEX = os.path.join(
    HERE, os.pardir, "skills", "loco4coco", "references", "guides-index.md"
)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, None)


def status(url, timeout=25):
    """Return (code, location). Uses GET: HEAD is rejected by some endpoints
    and would misreport a working URL as broken."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, None
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location")
    except Exception as e:                                      # noqa: BLE001
        return 0, f"error: {e}"


def curated_slugs(index_path):
    """Slugs currently committed in guides-index.md, as `backticked` tokens."""
    with open(index_path, encoding="utf-8") as f:
        text = f.read()
    # Skip the 'Redirects resolved' section: those are deliberately retired.
    text = text.split("## Redirects resolved")[0]
    return sorted(set(re.findall(r"`([a-z0-9][a-z0-9-]{7,})`", text)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=DEFAULT_INDEX)
    ap.add_argument("--corpus", help="JSON from the browser harvest (see docstring)")
    args = ap.parse_args()

    index_path = os.path.normpath(args.index)
    if not os.path.exists(index_path):
        print(f"index not found: {index_path}", file=sys.stderr)
        return 2

    curated = curated_slugs(index_path)
    if not curated:
        print("no curated slugs parsed - has the index format changed?", file=sys.stderr)
        return 2

    print(f"Verifying {len(curated)} curated slugs from {index_path}\n")
    bad, redirected = [], []
    for slug in curated:
        code, loc = status(f"{BASE}{slug}/")
        if code == 200:
            mark = "ok"
        elif code in (301, 302, 307, 308):
            target = (loc or "").rstrip("/").rsplit("/", 1)[-1]
            mark = f"REDIRECT -> {target}"
            redirected.append((slug, target))
        else:
            mark = f"FAIL {code}"
            bad.append((slug, code))
        print(f"  {slug:<70} {mark}")
        time.sleep(0.15)

    if args.corpus:
        with open(args.corpus, encoding="utf-8") as f:
            raw = json.load(f)
        corpus = {
            re.sub(r"^/en/developers/guides/|/$", "", k): v for k, v in raw.items()
        }
        print(f"\nCorpus supplied: {len(corpus)} guides.")
        missing = [s for s in curated if s not in corpus]
        if missing:
            print("\nCurated but absent from the corpus (verify before removing):")
            for s in missing:
                print(f"  {s}")
        coco = [
            s
            for s, v in sorted(corpus.items())
            if s not in curated
            and re.search(r"coco|cortex.code|cowork", (str(v) + s), re.I)
        ]
        if coco:
            print(f"\nUncurated CoCo/CoWork guides worth reviewing ({len(coco)}):")
            for s in coco[:40]:
                print(f"  {s}")
    else:
        print("\nNo --corpus supplied: verification only, corpus not refreshed.")

    print(
        f"\nSummary: {len(curated)} curated, {len(bad)} failing, "
        f"{len(redirected)} redirecting."
    )
    if redirected:
        print("Point guides-index.md at the redirect targets.")
    if bad:
        print("Replace the failing slugs. Never ship an unverified URL.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
