#!/usr/bin/env python3
"""Throughput audit: how long does a visitor actually wait, at worst?

A conference stand needs the WORST case, not the average. This varies input size
across both transports and repeats each bucket, then reports mean/min/max/p95 and
what that means for visitors per hour per stand.

    python3 bench3.py            # full run (about 40 model calls)
    python3 bench3.py --quick    # fewer reps

Never writes game state, so it is safe to run beside a live server.
"""
import argparse
import json
import statistics as st
import subprocess
import time

import server as S

SHORT_HELD = ["Transaction history"]
MED_HELD = ["Transaction history", "Customer profiles", "Fraud case notes"]
LONG_HELD = ["Transaction history", "Customer profiles", "Fraud case notes",
             "Call recordings", "Chat transcripts", "Complaint letters",
             "Branch footfall", "Card authorisations", "KYC documents",
             "Mortgage applications"]

SHORT_ASK = "spot fraud"
MED_ASK = "give early warning of customers at risk of missed payments"
LONG_ASK = ("give early warning of customers at risk of missed payments, "
            "combining their transaction history with the complaint letters and "
            "call recordings we already hold, so the collections team can reach "
            "out before someone defaults, and ideally explain in plain English "
            "why each customer was flagged so an adviser can have a sensible "
            "conversation rather than reading a score off a screen")


def complete_prompt(held, ask=None):
    ctx = ("You are CoCo, the Snowflake penguin, at a booth. Warm, brief, concrete. "
           "No bullet points, no headings, no em dashes. You are already "
           "mid-conversation: do not greet them.\n\n"
           f"The visitor works in Financial Services at a retail bank and holds: "
           f"{', '.join(held)}. ")
    if ask:
        ctx += (f"They chose to join these listings: {ask}. Reply in at most 2 short "
                "sentences saying what joining those lets them answer.")
    else:
        ctx += ("Reply in at most 2 short sentences: reflect back the most valuable "
                "thing and name one specific named Snowflake feature that unlocks it.")
    return ctx


def time_complete(cfg, prompt):
    mdl = (cfg.get("coco") or {}).get("complete_model") or "mistral-large2"
    t0 = time.time()
    try:
        cur = S.sf_conn(cfg).cursor()
        try:
            cur.execute("SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, %s)", (mdl, prompt))
            cur.fetchone()
        finally:
            cur.close()
    except Exception:                                            # noqa: BLE001
        return None
    return time.time() - t0


def time_exec(cfg, ask, held):
    """Real workshop turn: the full closed-list JSON prompt, via cortex exec."""
    loc = (cfg.get("locations") or {}).get("workshop") or {}
    feats = ", ".join(sorted(S.load_features()))
    state = {"visitor": {"first_name": "Sam", "company": "Lloyds Bank",
                         "industry": "financial"},
             "held": held, "joined": ["Foreign Exchange Rates"]}
    body = S.fill(loc.get("prompt", ""), cfg, state, input=ask, feature_list=feats)
    prompt = "\n".join(S.base_context(cfg, state)) + "\n\n" + body
    c = cfg.get("coco") or {}
    cmd = [c.get("binary", "cortex"), "exec", prompt, "--format", "json",
           "--no-mcp", "--no-history", "--bypass",
           "--max-turns", str(loc.get("max_turns") or 4),
           "--effort", str(loc.get("effort") or "medium")]
    conn = (cfg.get("snowflake") or {}).get("connection_name")
    if conn:
        cmd += ["--connection", conn]
    t0 = time.time()
    ok = False
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True)
        for raw in p.stdout:
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "result":
                ok = not ev.get("is_error")
            if time.time() - t0 > 180:
                p.kill()
                break
        p.wait(timeout=10)
    except Exception:                                            # noqa: BLE001
        return None
    return time.time() - t0 if ok else None


def report(name, xs):
    xs = [x for x in xs if x]
    if not xs:
        print(f"{name:<34} FAILED")
        return None
    p95 = sorted(xs)[min(len(xs) - 1, int(round(0.95 * (len(xs) - 1))))]
    print(f"{name:<34}{st.mean(xs):>7.1f}{min(xs):>8.1f}{max(xs):>8.1f}"
          f"{p95:>8.1f}{len(xs):>5}")
    return {"mean": st.mean(xs), "min": min(xs), "max": max(xs), "p95": p95}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    creps, ereps = (3, 2) if a.quick else (5, 3)

    cfg = S.load_config()
    S.sf_conn(cfg)                      # warm the connection first, as the booth does
    S.refresh_live_listings(cfg)        # and the listing cache
    print(f"fast model : {(cfg.get('coco') or {}).get('complete_model')}")
    print(f"workshop   : exec, effort={(cfg['locations']['workshop']).get('effort')}, "
          f"tools={(cfg['locations']['workshop']).get('tools')}\n")
    print(f"{'bucket':<34}{'mean':>7}{'min':>8}{'max':>8}{'p95':>8}{'n':>5}")
    print("-" * 70)

    res = {}
    for label, held in (("library short (1 item)", SHORT_HELD),
                        ("library medium (3 items)", MED_HELD),
                        ("library long (10 items)", LONG_HELD)):
        res[label] = report(label, [time_complete(cfg, complete_prompt(held))
                                    for _ in range(creps)])
    for label, join in (("marketplace short (1)", "Foreign Exchange Rates"),
                        ("marketplace long (4)",
                         "Foreign Exchange Rates, Cryptocurrency Market Data, "
                         "Inflation Forecasting, Postcode Sector Weather Forecasts")):
        res[label] = report(label, [time_complete(cfg, complete_prompt(MED_HELD, join))
                                    for _ in range(creps)])
    print()
    for label, ask, held in (("workshop short input", SHORT_ASK, SHORT_HELD),
                             ("workshop medium input", MED_ASK, MED_HELD),
                             ("workshop LONG input", LONG_ASK, LONG_HELD)):
        res[label] = report(label, [time_exec(cfg, ask, held) for _ in range(ereps)])

    # What a visitor actually waits for: library + marketplace + workshop + postbox.
    POSTBOX = 20.0          # measured, mechanical (docx, stage, presign, outbox)
    def pick(k, f):
        return (res.get(k) or {}).get(f, 0) or 0
    best = pick("library short (1 item)", "min") + pick("marketplace short (1)", "min") \
        + pick("workshop short input", "min") + 12
    mean = pick("library medium (3 items)", "mean") + pick("marketplace short (1)", "mean") \
        + pick("workshop medium input", "mean") + POSTBOX
    worst = pick("library long (10 items)", "max") + pick("marketplace long (4)", "max") \
        + pick("workshop LONG input", "max") + 30
    print("\nCoCo wait per visitor (of the 300s budget)")
    for lab, v in (("best case", best), ("typical", mean), ("worst case", worst)):
        head = 300 - v
        print(f"  {lab:<11}{v:>7.1f}s   leaves {head:>6.1f}s for the human"
              f"   {'OK' if head > 120 else 'TIGHT'}")
    print(f"\nAt 5 min per visitor a stand serves ~12/hour; the CoCo wait above is the")
    print(f"floor under that. Four stands: ~48/hour.")


if __name__ == "__main__":
    main()
