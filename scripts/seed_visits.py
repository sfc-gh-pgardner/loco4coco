#!/usr/bin/env python3
"""Drive several varied visitors through the booth, to seed the handover tables.

smoke_test.py proves one visitor works. This exists for a different job: putting
enough realistic rows in LOCO4COCO.BOOTH.SESSIONS and TURNS that the SDR handover
queries can be demonstrated on real data rather than described.

Visitors differ in industry, company and problem so the rows are worth grouping
by. Each visit spends real Cortex time, so this is deliberately serial - the warm
agent pool mis-correlates concurrent calls.

    python3 scripts/seed_visits.py                 # every visitor below
    python3 scripts/seed_visits.py --only 2        # just the third one
    python3 scripts/seed_visits.py --venue paris   # switch venue first
"""
import argparse
import json
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:4747"

VISITORS = [
    {"first_name": "Amara", "company": "Northwind Energy",
     "problem": "We cannot see which substations are about to be overloaded "
                "until someone phones us about it.",
     "library": ["Meter readings", "Asset register"],
     "compose": "flag substations heading for overload before customers notice"},
    {"first_name": "Tobias", "company": "Rheinpark Logistik",
     "problem": "Our suppliers tell us about delays too late to reroute a "
                "shipment.",
     "library": ["Shipment records", "Supplier data"],
     "compose": "warn us early when a supplier shipment is going to slip"},
    {"first_name": "Claire", "company": "Meridian Health Trust",
     "problem": "We plan clinics on last year's attendance and keep getting "
                "the staffing wrong.",
     "library": ["Appointment records", "Patient demographics"],
     "compose": "predict clinic attendance so staffing matches demand"},
    {"first_name": "Rahul", "company": "Kestrel Retail Group",
     "problem": "Stock decisions are made per store with no view of what is "
                "selling three streets away.",
     "library": ["Sales transactions", "Store locations"],
     "compose": "see demand across nearby stores before committing stock"},
]


def post(path, obj=None, timeout=40):
    data = json.dumps(obj or {}).encode()
    req = urllib.request.Request(BASE + path, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def get(path, timeout=30):
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def wait(limit=240):
    """The booth writes `thinking` while a Cortex call is in flight."""
    t0 = time.time()
    while time.time() - t0 < limit:
        time.sleep(2)
        if not get("/api/state").get("thinking"):
            return round(time.time() - t0, 1)
    return None


def one(v, n):
    print("\n--- visitor %d: %s, %s" % (n + 1, v["first_name"], v["company"]))
    post("/api/reset")
    r = post("/api/intake", {"first_name": v["first_name"],
                             "company": v["company"],
                             "problem": v["problem"]})
    print("    industry inferred : %s" % r.get("industry_name"))

    post("/api/select", {"location": "library", "labels": v["library"]})
    print("    library           : %ss" % wait())

    # Pick from what the running config actually offers - hard-coded titles drift
    # every time the index is recurated.
    market = (get("/api/options").get("marketplace") or [])[:2]
    picks = [o["label"] for o in market]
    post("/api/select", {"location": "marketplace", "labels": picks})
    print("    marketplace       : %ss  %s" % (wait(), [p[:28] for p in picks]))

    post("/api/compose", {"text": v["compose"]})
    t = wait()
    poc = get("/api/state").get("poc") or {}
    print("    workshop          : %ss  %s (%s)"
          % (t, poc.get("poc_name"), poc.get("archetype")))

    post("/api/send")
    print("    postbox           : %ss" % wait())
    s = get("/api/state")
    if not s.get("queued"):
        print("    WARNING: handover document was not staged")
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, help="index into the visitor list")
    ap.add_argument("--venue", help="apply a venue before seeding")
    a = ap.parse_args()

    if a.venue:
        got = post("/api/admin/apply", {"venue": a.venue})
        if got.get("venue") != a.venue:
            sys.exit("venue did not apply: asked %r, got %r"
                     % (a.venue, got.get("venue")))
        print("venue: %s (%s, profile %s)"
              % (got.get("venue"), got.get("city"), got.get("market_profile")))

    todo = [VISITORS[a.only]] if a.only is not None else VISITORS
    ok = 0
    t0 = time.time()
    for n, v in enumerate(todo):
        try:
            if one(v, a.only if a.only is not None else n):
                ok += 1
        except Exception as e:                                   # noqa: BLE001
            print("    FAILED: %s" % str(e)[:160])
    print("\n%d of %d visits completed in %.0fs"
          % (ok, len(todo), time.time() - t0))
    return 0 if ok == len(todo) else 1


if __name__ == "__main__":
    sys.exit(main())
