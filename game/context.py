"""The booth's closed lists, and keyword retrieval over them.

Three sources for the same content, tried in this order:

    1. Snowflake  LOCO4COCO.BOOTH.{LISTINGS,GUIDES,FEATURES,ARCHETYPES,ROUTES}
       Current and shareable. How another SE's laptop, or Paris, gets the same
       lists without pulling a git branch.
    2. context-bundle.json  (generated, committed, next to the markdown)
       Parsed once at build time so boot costs no regex. The offline path.
    3. The reference markdown itself
       The human-editable source of truth, and the last resort.

Any layer failing falls through to the next, so a flat venue network or an empty
table degrades the booth rather than breaking it. Layer 3 is in the repo, so
there is always something.

WHY NOT A SEARCH SERVICE
------------------------
The whole corpus is around 150 rows. A Cortex Search service over it would add a
service to keep refreshed, a network round trip on a network we do not trust, and
nondeterminism to the one thing that must be predictable on a Snowflake-branded
stand. Scoring 150 rows in process takes microseconds and the same input always
gives the same output.

So retrieval here is deliberately dumb and deliberately deterministic. The model
never searches; Python picks a shortlist and the prompt carries only that. The
model's job is to choose from a handful, not to find among many, which is both
faster and clampable. `cortex mcp serve` does expose `cortex_search_docs` for
documentation beyond our closed list - that is a bonus, not the backbone.
"""

import json
import os
import re
import subprocess
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(HERE)
REFS = os.path.join(PLUGIN_ROOT, "skills", "loco4coco", "references")
BUNDLE_PATH = os.path.join(REFS, "context-bundle.json")

KINDS = ("listings", "guides", "features", "archetypes", "routes")

_cache = {"at": 0, "source": "", "data": None}
_lock = threading.Lock()

# Words that carry no signal in a keyword match here. Short but real: without it
# "data" matches nearly every listing and every feature, which makes the top of
# the shortlist arbitrary.
_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "for", "with", "in", "on", "at",
    "my", "our", "we", "i", "is", "are", "be", "it", "this", "that", "from",
    "by", "as", "data", "snowflake", "want", "need", "would", "like", "get",
    "some", "all", "any", "how", "what", "can", "do", "does", "have", "has",
}


def _words(text):
    """Lowercase alphanumeric tokens of 3+ characters, minus stopwords."""
    return [w for w in re.findall(r"[a-z0-9_]{3,}", (text or "").lower())
            if w not in _STOP]


# ------------------------------------------------------------------ layer 3: md

def _from_markdown():
    """Parse the reference markdown. Mirrors deploy/load_context.py.

    Imported from there when available so there is one parser, not two.
    """
    import sys
    dep = os.path.join(PLUGIN_ROOT, "deploy")
    if dep not in sys.path:
        sys.path.insert(0, dep)
    import load_context as L

    feats = [{"name": n, "docs_url": u} for n, u in L.parse_features()]
    names = {f["name"] for f in feats}
    arch = []
    for (aid, ordinal, friendly, pain, what, raw_feats, fork, needs,
            prompt) in L.parse_archetypes():
        good, _ = L.canonical_features(raw_feats, names)
        arch.append({"id": aid, "ordinal": ordinal, "friendly": friendly,
                     "pain": pain, "what_gets_built": what, "features": good,
                     "fork_slug": fork, "needs": needs,
                     "prompt_skeleton": prompt})
    return {
        "listings": [
            {"industry": i, "ordinal": o, "title": t, "provider": p,
             "access": a, "global_name": g, "regions": r, "url": u}
            for i, o, t, p, a, g, r, u in L.parse_listings()],
        "guides": [
            {"archetype": a, "title": t, "slug": s, "is_primary": bool(pr)}
            for a, t, s, pr in L.parse_guides()],
        "features": feats,
        "archetypes": arch,
        "routes": [{"platform": p, "guidance": g, "docs_url": d}
                   for p, g, d in L.parse_routes()],
    }


# -------------------------------------------------------------- layer 2: bundle

def _from_bundle():
    with open(BUNDLE_PATH, encoding="utf-8") as f:
        b = json.load(f)
    data = {k: b.get(k) or [] for k in KINDS}
    if not all(data[k] for k in KINDS):
        raise ValueError("context-bundle.json is missing a section")
    return data


def write_bundle(data=None):
    """Generate context-bundle.json from the markdown. Called at build time.

    Committed deliberately: it is the offline path, and committing it means a
    drift between it and the markdown shows up in review and in the parity
    check, rather than silently on the stand.
    """
    data = data or _from_markdown()
    payload = dict(data)
    payload["_generated"] = {
        "note": "GENERATED by game/context.py write_bundle(). Do not hand-edit; "
                "edit the markdown in this directory and regenerate.",
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "counts": {k: len(data[k]) for k in KINDS},
    }
    with open(BUNDLE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    return payload["_generated"]["counts"]


# ---------------------------------------------------------- layer 1: snowflake

def _from_snowflake(conn, timeout=25):
    """Read the five tables in one round trip.

    One statement, not five: on a venue network the cost is the round trip, not
    the rows. Uses the Snowflake CLI rather than a connector so the booth laptop
    needs no extra Python package.
    """
    sql = """
    SELECT OBJECT_CONSTRUCT(
      'listings',  (SELECT ARRAY_AGG(OBJECT_CONSTRUCT('industry',INDUSTRY,
                      'ordinal',ORDINAL,'title',TITLE,'provider',PROVIDER,
                      'access',ACCESS,'global_name',GLOBAL_NAME,
                      'regions',REGIONS,'url',URL))
                    FROM LOCO4COCO.BOOTH.LISTINGS),
      'guides',    (SELECT ARRAY_AGG(OBJECT_CONSTRUCT('archetype',ARCHETYPE,
                      'title',TITLE,'slug',SLUG,'is_primary',IS_PRIMARY))
                    FROM LOCO4COCO.BOOTH.GUIDES),
      'features',  (SELECT ARRAY_AGG(OBJECT_CONSTRUCT('name',NAME,
                      'docs_url',DOCS_URL))
                    FROM LOCO4COCO.BOOTH.FEATURES),
      'archetypes',(SELECT ARRAY_AGG(OBJECT_CONSTRUCT('id',ID,'ordinal',ORDINAL,
                      'friendly',FRIENDLY,'pain',VISITOR_PAIN,
                      'what_gets_built',WHAT_GETS_BUILT,
                      'features',FEATURES,'fork_slug',FORK_SLUG,
                      'needs',NEEDS_FROM_THEM,
                      'prompt_skeleton',PROMPT_SKELETON))
                    FROM LOCO4COCO.BOOTH.ARCHETYPES),
      'routes',    (SELECT ARRAY_AGG(OBJECT_CONSTRUCT('platform',PLATFORM,
                      'guidance',GUIDANCE,'docs_url',DOCS_URL))
                    FROM LOCO4COCO.BOOTH.ROUTES)
    ) AS CTX
    """
    cmd = ["snow", "sql", "-q", sql, "--format", "json",
           "--enable-templating", "NONE"]
    if conn:
        cmd += ["-c", conn]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout or "")[-400:])
    rows = json.loads(p.stdout)
    blob = rows[0]["CTX"] if rows else None
    if isinstance(blob, str):
        blob = json.loads(blob)
    if not blob:
        raise ValueError("no context rows")
    data = {}
    for k in KINDS:
        v = blob.get(k) or []
        if not v:
            raise ValueError("table for %r is empty" % k)
        data[k] = v
    # ARCHETYPES.FEATURES is stored comma-separated; normalise to a list so both
    # layers hand back the same shape and callers need no idea which won.
    for a in data["archetypes"]:
        f = a.get("features")
        if isinstance(f, str):
            a["features"] = [x.strip() for x in f.split(",") if x.strip()]
    return data


# --------------------------------------------------------------------- loading

def load(conn=None, prefer_snowflake=True, ttl=900, force=False):
    """Return (data, source). Cached; safe to call on every request."""
    with _lock:
        if (not force and _cache["data"]
                and time.time() - _cache["at"] < ttl):
            return _cache["data"], _cache["source"]
        attempts = []
        if prefer_snowflake:
            attempts.append(("snowflake", lambda: _from_snowflake(conn)))
        attempts += [("bundle", _from_bundle), ("markdown", _from_markdown)]
        errors = []
        for name, fn in attempts:
            try:
                data = fn()
                _cache.update({"at": time.time(), "source": name, "data": data})
                return data, name
            except Exception as e:
                errors.append("%s: %s" % (name, e))
        # Every layer failed, which means the repo itself is broken. Serve empty
        # rather than raise: the caller clamps against these lists, and an empty
        # closed list drops features instead of inventing them.
        empty = {k: [] for k in KINDS}
        _cache.update({"at": time.time(), "source": "empty", "data": empty})
        return empty, "empty:" + "; ".join(errors)[:300]


# ------------------------------------------------------------------- retrieval

def search(text, kind, limit=8, industry=None, conn=None):
    """Deterministic keyword shortlist over one closed list.

    Scoring, highest first:
      * 3 per query word found in the row's most identifying field
        (title / name / friendly), where a match means the most
      * 1 per query word found anywhere else in the row
      * ties broken by the row's own order, then alphabetically, so the same
        input always yields the same shortlist - required, not merely nice, for
        something printed in a document a visitor keeps

    Returns [] rather than guessing when nothing matches. The caller decides
    whether that means "fall back to the industry default" or "say nothing".
    """
    if kind not in KINDS:
        raise ValueError("unknown kind %r" % kind)
    data, _ = load(conn=conn)
    rows = data.get(kind) or []
    if industry and kind == "listings":
        rows = [r for r in rows if r.get("industry") == industry] or rows

    words = _words(text)
    if not words:
        return list(rows)[:limit]

    key_field = {"listings": "title", "guides": "title", "features": "name",
                 "archetypes": "friendly", "routes": "platform"}[kind]

    scored = []
    for i, r in enumerate(rows):
        key = str(r.get(key_field) or "").lower()
        rest = " ".join(str(v).lower() for k, v in r.items()
                        if k != key_field).lower()
        score = sum(3 for w in words if w in key) + \
            sum(1 for w in words if w in rest)
        if score:
            scored.append((-score, i, str(r.get(key_field) or ""), r))
    scored.sort(key=lambda t: (t[0], t[1], t[2]))
    return [r for _, _, _, r in scored[:limit]]


def resolve_archetype(text, conn=None):
    """Score the visitor's own words against every archetype. Returns
    (archetype dict or None, [(id, score)] ranked).

    This is the load-bearing lookup. Matching a visitor's sentence directly
    against feature names does not work - "we retype invoices all day" shares no
    token with AI_EXTRACT - so the archetype's pain text is the bridge from their
    language into ours. Everything else (which features, which guide) follows
    from the archetype rather than being searched for separately.

    Deterministic and explainable: the score is a count, and the ranking is
    returned so the booth can log why a visitor was routed where they were.
    """
    data, _ = load(conn=conn)
    words = _words(text)
    ranked = []
    for a in data.get("archetypes") or []:
        pain = str(a.get("pain") or "").lower()
        built = str(a.get("what_gets_built") or "").lower()
        friendly = str(a.get("friendly") or "").lower()
        ident = str(a.get("id") or "").lower().replace("-", " ")
        # Pain is weighted hardest because it is the only field written in the
        # visitor's register rather than ours.
        score = (sum(3 for w in words if w in pain)
                 + sum(2 for w in words if w in built)
                 + sum(2 for w in words if w in friendly)
                 + sum(2 for w in words if w in ident))
        ranked.append((a.get("id"), score, a.get("ordinal") or 99, a))
    ranked.sort(key=lambda t: (-t[1], t[2]))
    best = ranked[0] if ranked else None
    hit = best[3] if best and best[1] > 0 else None
    return hit, [(r[0], r[1]) for r in ranked]


def guide_for_archetype(archetype, conn=None):
    """The primary fork for an archetype, or None."""
    data, _ = load(conn=conn)
    prim = [g for g in data.get("guides") or []
            if g.get("archetype") == archetype and g.get("is_primary")]
    alts = [g for g in data.get("guides") or []
            if g.get("archetype") == archetype and not g.get("is_primary")]
    return (prim or alts or [None])[0]


def shortlist_block(text, industry=None, conn=None,
                    n_listings=6, n_features=10, n_guides=3):
    """One prompt-ready block naming the only listings, features and guides a
    turn may use, derived from what the visitor actually said.

    This is how the closed lists reach `cortex exec`: as content in the prompt,
    not as a tool. `cortex exec` cannot be given tools except through MCP, and
    MCP is not guaranteed on a borrowed booth laptop - but the corpus is small
    enough that injecting the relevant slice costs a few hundred tokens and
    removes the search step from the model's job entirely.

    Composition, in order of trust:
      1. The resolved archetype's own features and fork. Curated by us.
      2. Keyword hits, to catch what the archetype misses.
      3. The industry's listings, which are curated per industry already.
    Never empty: with no keyword signal at all it still emits the industry
    listings and the archetype defaults, because a visitor who typed nothing
    still leaves with a document.
    """
    data, _ = load(conn=conn)
    arche, _ranked = resolve_archetype(text, conn=conn)

    feat_rows, seen = [], set()
    by_name = {f.get("name"): f for f in data.get("features") or []}
    for name in (arche or {}).get("features") or []:
        if name in by_name and name not in seen:
            seen.add(name)
            feat_rows.append(by_name[name])
    for f in search(text, "features", n_features, conn=conn):
        if f.get("name") not in seen and len(feat_rows) < n_features:
            seen.add(f.get("name"))
            feat_rows.append(f)

    guides, gseen = [], set()
    g = guide_for_archetype((arche or {}).get("id"), conn=conn)
    if g:
        gseen.add(g.get("slug"))
        guides.append(g)
    for row in search(text, "guides", n_guides, conn=conn):
        if row.get("slug") not in gseen and len(guides) < n_guides:
            gseen.add(row.get("slug"))
            guides.append(row)

    li = [r for r in (data.get("listings") or [])
          if not industry or r.get("industry") == industry][:n_listings]
    if not li:
        li = search(text, "listings", n_listings, conn=conn)

    def block(rows, fmt):
        return "\n".join(fmt(r) for r in rows) or "  (none)"

    head = ""
    if arche:
        head = ("LIKELY SHAPE: %s (%s)\n  what it builds: %s\n\n"
                % (arche.get("friendly"), arche.get("id"),
                   arche.get("what_gets_built")))
    return (
        head
        + "MARKETPLACE LISTINGS you may name (these only):\n"
        + block(li, lambda r: "  - %s (%s, %s)" % (
            r.get("title"), r.get("provider"), r.get("access")))
        + "\n\nFEATURES you may name, spelled exactly like this (these only):\n"
        + block(feat_rows, lambda r: "  - " + str(r.get("name")))
        + "\n\nGUIDES that could be forked:\n"
        + block(guides, lambda r: "  - %s [%s]" % (
            r.get("title"), r.get("slug")))
    )


def status(conn=None):
    """What the booth is running on, for the ops pre-flight."""
    data, source = load(conn=conn)
    return {"source": source,
            "counts": {k: len(data.get(k) or []) for k in KINDS}}


if __name__ == "__main__":
    import sys
    if "--bundle" in sys.argv:
        print("wrote bundle:", write_bundle())
    elif "--status" in sys.argv:
        print(json.dumps(status(
            conn=(os.environ.get("LOCO_CONNECTION") or "PG_LONDON")), indent=1))
    else:
        q = " ".join(a for a in sys.argv[1:] if not a.startswith("-")) \
            or "invoices piling up"
        for k in ("listings", "features", "guides"):
            print("\n== %s: %r" % (k, q))
            for r in search(q, k, 5):
                print("   ", r.get("title") or r.get("name"))
