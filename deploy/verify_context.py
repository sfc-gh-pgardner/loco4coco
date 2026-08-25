#!/usr/bin/env python3
"""Verify the booth's closed lists before an event.

Run this as part of the pre-flight. It answers the questions that decide whether
a visitor's document can be trusted:

  * do all three context layers agree?            (parity)
  * does every archetype resolve to a guide?      (no dead ends)
  * does every feature carry a working doc link?  (no bare names)
  * does every listing still exist, and is it still free to acquire?
  * does every guide URL still resolve?
  * can every archetype be reached from its own pain text?

Link and listing checks touch the network, so they are opt-in:

    python3 deploy/verify_context.py                 # offline checks only
    python3 deploy/verify_context.py --links         # + HTTP HEAD every doc URL
    python3 deploy/verify_context.py --listings      # + query the Marketplace
    python3 deploy/verify_context.py --all

Exit code is the number of failures, so it drops straight into a shell gate.
A WARN never fails the run; a FAIL always does.
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "game"))
sys.path.insert(0, HERE)

import context as ctx  # noqa: E402

FAILS, WARNS = [], []


def fail(check, detail):
    FAILS.append((check, detail))
    print("  FAIL  %-22s %s" % (check, detail))


def warn(check, detail):
    WARNS.append((check, detail))
    print("  warn  %-22s %s" % (check, detail))


def ok(check, detail=""):
    print("  ok    %-22s %s" % (check, detail))


# ------------------------------------------------------------------ offline

def check_parity(conn):
    """All three layers must describe the same corpus.

    A mismatch means someone edited the markdown and did not regenerate the
    bundle, or did not reload the tables - so two booth laptops would hand out
    different documents. That is the failure this whole check exists for.
    """
    seen = {}
    for label, kw in (("snowflake", dict(conn=conn, prefer_snowflake=True)),
                      ("bundle", dict(prefer_snowflake=False))):
        try:
            data, src = ctx.load(force=True, **kw)
            seen[src] = {k: len(data.get(k) or []) for k in ctx.KINDS}
        except Exception as e:
            warn("parity/" + label, str(e)[:120])
    try:
        md = ctx._from_markdown()
        seen["markdown"] = {k: len(md.get(k) or []) for k in ctx.KINDS}
    except Exception as e:
        fail("parity/markdown", str(e)[:160])

    if len(seen) < 2:
        warn("parity", "only %s available, cannot compare" % list(seen))
        return
    ref_name, ref = sorted(seen.items())[0]
    for name, counts in seen.items():
        if counts != ref:
            diff = {k: (ref.get(k), counts.get(k)) for k in ctx.KINDS
                    if ref.get(k) != counts.get(k)}
            fail("parity", "%s vs %s differ: %s" % (ref_name, name, diff))
            return
    ok("parity", "%s agree: %s" % ("/".join(sorted(seen)), ref))


def check_guides(data):
    """Every archetype needs a fork, or the visitor leaves with nowhere to go."""
    arch = data.get("archetypes") or []
    slugs = {g.get("slug") for g in data.get("guides") or []}
    bad = 0
    for a in arch:
        g = ctx.guide_for_archetype(a.get("id"))
        if not g:
            fail("guides/reachable", "%s has no guide" % a.get("id"))
            bad += 1
        elif a.get("fork_slug") and a["fork_slug"] not in slugs:
            warn("guides/fork_slug",
                 "%s names fork %r which is not in guides-index.md"
                 % (a.get("id"), a["fork_slug"]))
    if not bad:
        ok("guides/reachable", "all %d archetypes have a fork" % len(arch))


def check_features(data):
    """A feature without a link gets dropped at render time, so an archetype
    pointing at one silently loses it. Catch that here."""
    names = {f.get("name") for f in data.get("features") or []}
    nolink = [f.get("name") for f in data.get("features") or []
              if not str(f.get("docs_url") or "").startswith("https://")]
    if nolink:
        fail("features/links", "%d without an https doc url: %s"
             % (len(nolink), nolink[:5]))
    else:
        ok("features/links", "%d features, all linked" % len(names))

    missing = 0
    for a in data.get("archetypes") or []:
        for f in a.get("features") or []:
            if f not in names:
                fail("features/closed", "%s names %r, absent from the list"
                     % (a.get("id"), f))
                missing += 1
    if not missing:
        ok("features/closed", "every archetype feature is in the closed list")


def check_routing(data):
    """Each archetype must be reachable from its own pain text.

    If an archetype cannot win on the words that describe it, no visitor will
    ever be routed to it, and it is dead weight pretending to be coverage.
    """
    bad = []
    for a in data.get("archetypes") or []:
        pain = a.get("pain") or ""
        if not pain:
            warn("routing/pain", "%s has no pain text" % a.get("id"))
            continue
        hit, ranked = ctx.resolve_archetype(pain)
        if not hit or hit.get("id") != a.get("id"):
            bad.append((a.get("id"), (hit or {}).get("id"), ranked[:2]))
    for aid, got, top in bad:
        fail("routing/self", "%s resolves to %s (top: %s)" % (aid, got, top))
    if not bad:
        ok("routing/self", "all %d archetypes win on their own pain text"
           % len(data.get("archetypes") or []))


def check_listing_shape(data):
    rows = data.get("listings") or []
    by_ind = {}
    for r in rows:
        by_ind.setdefault(r.get("industry"), []).append(r)
    uneven = {k: len(v) for k, v in by_ind.items() if len(v) != 6}
    if uneven:
        warn("listings/count", "not 6 per industry: %s" % uneven)
    else:
        ok("listings/count", "%d industries x 6" % len(by_ind))

    paid = [r.get("title") for r in rows
            if not str(r.get("access") or "").lower().startswith("free")]
    if paid:
        fail("listings/free", "not free to acquire: %s" % paid[:4])
    else:
        trials = sum(1 for r in rows if "trial" in
                     str(r.get("access") or "").lower())
        ok("listings/free", "all free to acquire (%d are time-limited trials)"
           % trials)

    nogn = [r.get("title") for r in rows if not r.get("global_name")]
    if nogn:
        fail("listings/global_name", "missing: %s" % nogn[:4])
    else:
        ok("listings/global_name", "all present")


# ------------------------------------------------------------------- network

def head(url, timeout=12):
    """Return (ok, note). Follows redirects; falls back to GET, because some
    Snowflake doc hosts reject HEAD outright."""
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(
                url, method=method,
                headers={"User-Agent": "loco4coco-preflight"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return (200 <= r.status < 400), str(r.status)
        except urllib.error.HTTPError as e:
            if e.code in (403, 405) and method == "HEAD":
                continue
            return False, "HTTP %s" % e.code
        except Exception as e:
            if method == "HEAD":
                continue
            return False, type(e).__name__
    return False, "unreachable"


def check_links(data, base):
    urls = {}
    for f in data.get("features") or []:
        urls.setdefault(f.get("docs_url"), "feature " + str(f.get("name")))
    for r in data.get("routes") or []:
        urls.setdefault(r.get("docs_url"), "route " + str(r.get("platform")))
    for g in data.get("guides") or []:
        if g.get("is_primary"):
            urls.setdefault(base + str(g.get("slug")) + "/",
                            "guide " + str(g.get("title")))
    urls.pop(None, None)
    print("  ...checking %d urls" % len(urls))
    with ThreadPoolExecutor(max_workers=12) as ex:
        results = list(ex.map(lambda u: (u, head(u)), urls))
    bad = [(u, urls[u], note) for u, (good, note) in results if not good]
    for u, what, note in bad:
        fail("links", "%s -> %s (%s)" % (what, u, note))
    if not bad:
        ok("links", "%d urls resolve" % len(urls))


def check_listings_live(data, conn):
    """Confirm every curated listing is still visible and still importable.

    The is_ready_for_import flag matters: a listing can be live and still not
    acquirable, which is a dead end a visitor would only discover at home.
    """
    gns = sorted({r.get("global_name") for r in data.get("listings") or []
                  if r.get("global_name")})
    if not gns:
        return
    lit = ", ".join("'%s'" % g.replace("'", "''") for g in gns)
    # SHOW AVAILABLE LISTINGS piped through RESULT_SCAN, which is what the booth
    # server itself uses. There is no ACCOUNT_USAGE view for this - the obvious
    # guess, SNOWFLAKE.DATA_SHARING_USAGE.LISTING_CATALOG, does not exist.
    sql = ('SHOW AVAILABLE LISTINGS; '
           'SELECT "global_name" AS G, "title" AS T, '
           '"is_ready_for_import" AS R '
           'FROM TABLE(RESULT_SCAN(LAST_QUERY_ID())) '
           'WHERE "global_name" IN (%s)' % lit)
    cmd = ["snow", "sql", "-q", sql, "--format", "json",
           "--enable-templating", "NONE"]
    if conn:
        cmd += ["-c", conn]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            warn("listings/live", (p.stderr or p.stdout or "")[-160:])
            return
        out = json.loads(p.stdout)
        # snow sql returns one result set per statement; take the last non-empty.
        rows = []
        if isinstance(out, list) and out and isinstance(out[0], list):
            for chunk in reversed(out):
                if chunk and isinstance(chunk[0], dict) and "G" in chunk[0]:
                    rows = chunk
                    break
        elif isinstance(out, list):
            rows = [r for r in out if isinstance(r, dict) and "G" in r]
    except Exception as e:
        warn("listings/live", "%s: %s" % (type(e).__name__, str(e)[:120]))
        return
    found = {r.get("G"): r for r in rows}
    gone = [g for g in gns if g not in found]
    for g in gone:
        fail("listings/live", "%s is no longer in the catalog" % g)
    notready = [g for g, r in found.items()
                if str(r.get("R")).lower() in ("false", "0", "none", "")]
    for g in notready:
        fail("listings/importable", "%s is not ready for import" % g)
    if not gone and not notready:
        ok("listings/live", "%d listings live and importable" % len(found))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--connection", default="PG_LONDON")
    ap.add_argument("--links", action="store_true")
    ap.add_argument("--listings", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--guides-base",
                    default="https://www.snowflake.com/en/developers/guides/")
    a = ap.parse_args()
    do_links = a.links or a.all
    do_listings = a.listings or a.all

    print("Loco4CoCo context verification")
    print("\nlayers")
    check_parity(a.connection)

    data, src = ctx.load(conn=a.connection, force=True)
    print("\ncontent  (source: %s)" % src)
    check_guides(data)
    check_features(data)
    check_routing(data)
    check_listing_shape(data)

    if do_links:
        print("\nlinks")
        check_links(data, a.guides_base)
    if do_listings:
        print("\nmarketplace")
        check_listings_live(data, a.connection)

    if not do_links or not do_listings:
        skipped = [n for n, on in (("--links", do_links),
                                   ("--listings", do_listings)) if not on]
        print("\nskipped network checks: %s" % ", ".join(skipped))

    print("\n%d failures, %d warnings" % (len(FAILS), len(WARNS)))
    return len(FAILS)


if __name__ == "__main__":
    sys.exit(main())
