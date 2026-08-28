#!/usr/bin/env python3
"""Smoke test: drive one full visitor through the API and assert the invariants."""
import json, os, re, subprocess, sys, time, urllib.request

BASE = "http://127.0.0.1:4747"
GAME = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(GAME, "state.json")


def post(path, obj=None):
    data = json.dumps(obj or {}).encode()
    req = urllib.request.Request(BASE + path, data=data,
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"{}")


def state():
    with open(STATE, encoding="utf-8") as f:
        return json.load(f)


def wait(label, limit=180):
    t0 = time.time()
    while time.time() - t0 < limit:
        time.sleep(2)
        if not state().get("thinking"):
            return round(time.time() - t0, 1)
    return None


LEAK = re.compile(r"(the user wants|as CoCo|plain English|no bullet|mcp__|"
                  r"create_draft|gmail|toolset|booth)", re.I)
fails, timings = [], {}

post("/api/reset")
r = post("/api/intake", {"first_name": "Sarah", "company": "Lloyds Bank",
                         "email": "sarah.test@example.org",
                         "problem": "We want to spot customers heading for "
                                    "payment trouble before they miss one."})
assert r["industry"] == "financial", f"industry inference: {r['industry']}"
print(f"intake        : {r['industry_name']}")

post("/api/select", {"location": "library",
                     "labels": ["Transaction history", "Customer communications"]})
timings["library"] = wait("library")
s = state()
print(f"library  {timings['library']}s : {s['reply'][:88]}")
if "marketplace" not in s["unlocked"]:
    fails.append("marketplace did not unlock")

# Marketplace options are now REAL listings read from the verified index, so
# pick whatever the running config actually offers rather than hard-coding
# titles that drift whenever the index is recurated.
opts = json.loads(urllib.request.urlopen(BASE + "/api/options", timeout=20).read())
market = opts.get("marketplace") or []
if len(market) < 2:
    fails.append(f"marketplace offered only {len(market)} listings")
for o in market:
    if not o.get("url", "").startswith("https://app.snowflake.com/marketplace/"):
        fails.append(f"listing {o.get('label')!r} has no marketplace URL")
    if not o.get("provider"):
        fails.append(f"listing {o.get('label')!r} has no provider")
picks = [o["label"] for o in market[:2]]
print(f"market picks   : {picks}")

post("/api/select", {"location": "marketplace", "labels": picks})
timings["marketplace"] = wait("marketplace")
s = state()
print(f"market   {timings['marketplace']}s : {s['reply'][:88]}")

post("/api/compose", {"text": "spot customers heading for trouble before they miss a payment"})
timings["workshop"] = wait("workshop")
s = state()
poc = s["poc"]
print(f"workshop {timings['workshop']}s : {poc.get('poc_name')}")
print(f"                archetype={poc.get('archetype')} "
      f"features={poc.get('features')}")
print(f"                considerations={len(poc.get('considerations') or [])}")
if not poc.get("archetype"):
    fails.append("workshop returned no archetype")
if not poc.get("guide_url", "").startswith("https://"):
    fails.append("no guide url resolved")
if len(poc.get("considerations") or []) < 2:
    fails.append(f"expected 2+ considerations, got {poc.get('considerations')}")
if not poc.get("features"):
    fails.append("no features survived the closed-list filter")

post("/api/send")
timings["postbox"] = wait("postbox")
s = state()
print(f"postbox  {timings['postbox']}s : {s['reply'][:110]}")

# --- invariants -------------------------------------------------------------
# Email and the outbox were removed: the QR to the presigned .docx is the only
# delivery. `queued` now reflects whether that document was staged for handover.
if not s.get("queued"):
    fails.append("document was not staged for handover (delivery failed)")

leaks = [l for l in (s.get("reasoning") or []) if LEAK.search(l)]
if leaks:
    fails.append(f"tray leaked {len(leaks)} line(s): {leaks[:2]}")

bp = json.loads(urllib.request.urlopen(BASE + "/api/blueprint", timeout=20).read())
for k in ("poc", "prompt", "document_url"):
    if not bp.get(k):
        fails.append(f"blueprint missing {k}")
if "invent" not in bp.get("prompt", ""):
    fails.append("prompt lost its do-not-invent constraint")

# Every feature must carry a documentation link, by construction.
if not bp.get("features"):
    fails.append("blueprint has no linked features")
for f in bp.get("features") or []:
    if not f.get("url", "").startswith("https://docs.snowflake.com/"):
        fails.append(f"feature {f.get('name')!r} has no docs link")

# Listings must carry a provider and a real marketplace URL.
for r in bp.get("listings") or []:
    if not r.get("provider"):
        fails.append(f"listing {r.get('title')!r} lost its provider")
    if not r.get("url", "").startswith("https://app.snowflake.com/marketplace/"):
        fails.append(f"listing {r.get('title')!r} lost its URL")
if not bp.get("listings"):
    fails.append("no resolved marketplace listings in the blueprint")

if not bp.get("considerations"):
    fails.append("blueprint has no considerations")

# --- tracking actually landed ------------------------------------------------
# This block exists because an earlier version of this test printed "PASS - all
# invariants hold" while ZERO rows had reached Snowflake. A smoke test that does
# not check the tracking cannot claim a deployment is proven.
session_id = s.get("session_id") or ""
if not session_id:
    fails.append("no session_id was generated at intake")
if s.get("logged") is not True:
    fails.append(f"SESSIONS insert did not succeed: {s.get('log_error') or 'not attempted'}")

cfg = json.load(open(os.path.join(GAME, "config.json"), encoding="utf-8"))
sfc = cfg["snowflake"]
conn, db, sch = sfc["connection_name"], sfc["database"], sfc["schema"]


def count(table, where):
    q = f"SELECT COUNT(*) AS N FROM {db}.{sch}.{table} WHERE {where}"
    r = subprocess.run(["snow", "sql", "-q", q, "--format", "json", "-c", conn],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return -1
    try:
        out = json.loads(r.stdout or "[]")
        row = out[0] if isinstance(out, list) else out
        if isinstance(row, list):
            row = row[0] if row else {}
        return int(row.get("N") or 0)
    except (json.JSONDecodeError, ValueError, IndexError):
        return -1


n_sessions = count("SESSIONS", f"SESSION_ID = '{session_id}'")
n_turns = count("TURNS", f"SESSION_ID = '{session_id}'")
print(f"snowflake      : {n_sessions} session row, {n_turns} turn rows "
      f"({conn} {db}.{sch})")
if n_sessions != 1:
    fails.append(f"expected exactly 1 SESSIONS row, found {n_sessions}")
if n_turns != 4:
    fails.append(f"expected 4 TURNS rows (one per location), found {n_turns}")

post("/api/reset")
blob = json.dumps(state()).lower()
for term in ("sarah", "lloyds", "sarah.test"):
    if term in blob:
        fails.append(f"reset left residue: {term}")

total = sum(v for v in timings.values() if v)
print(f"\nCoCo wait total: {total}s of the {300}s budget")
print("blueprint keys :", sorted(k for k, v in bp.items() if v))

# --- Tier 0 (agentic marketplace), fired at intake -------------------------
# Tier 0 is OPTIONAL and OFF by default (marketplace.agentic.enabled=false):
# measured 70-110s+ on PG_LONDON, too slow and variable to beat a real visitor.
# Only assert it fired when it is actually enabled; otherwise confirm it stayed
# dormant. Either way the tier chain does not depend on it (see the fallback
# check below).
cost_path = os.path.join(GAME, "cost.jsonl")


def agentic_logged():
    if not os.path.exists(cost_path):
        return False
    with open(cost_path, encoding="utf-8") as f:
        return any(json.loads(l).get("kind") == "marketplace_agentic"
                  for l in f if l.strip())


agentic_on = bool(((cfg.get("marketplace") or {}).get("agentic") or {}).get("enabled"))
if agentic_on:
    fired = agentic_logged()
    t0 = time.time()
    while not fired and time.time() - t0 < 130:
        time.sleep(5)
        fired = agentic_logged()
    print(f"tier 0 fired   : {fired} ({round(time.time() - t0, 1)}s waited)")
    if not fired:
        fails.append("marketplace_agentic never appeared in cost.jsonl within "
                     "130s - start_agentic_search() did not run from /api/intake")
else:
    print("tier 0         : disabled by config (marketplace.agentic.enabled=false), skipped")

sys.path.insert(0, GAME)
import server as _srv                                            # noqa: E402
_cfg = _srv.load_config()
# session_id=None must skip Tier 0 by construction (listings_agentic returns
# [] with no session) and fall through to Tier 1/2 - proves the chain never
# depends on Tier 0 actually completing.
fallback = _srv.listings_for(_cfg, "healthcare", session_id=None)
if not fallback:
    fails.append("listings_for() with no session_id returned nothing - "
                 "Tier 1/2 fallback is broken")
else:
    print(f"tier 1/2 fallback: {len(fallback)} listings with session_id=None")

if fails:
    print("\nFAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("\nPASS - all invariants hold")
