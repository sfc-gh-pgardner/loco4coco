#!/usr/bin/env python3
"""Benchmark SNOWFLAKE.CORTEX.COMPLETE latency + reply quality for the hybrid
direct-inference path. Times each model via `snow sql -c PG_LONDON`. Bounded:
one simple-turn prompt across several models + a workshop-JSON feasibility check
on two. Records wall time (minus a snow-sql baseline) and the reply text.
"""
import json
import subprocess
import time

CONN = "PG_LONDON"

SIMPLE_MODELS = ["claude-3-5-haiku", "llama3.1-8b", "llama3.3-70b",
                 "mistral-large2", "claude-3-5-sonnet"]
JSON_MODELS = ["claude-3-5-sonnet", "llama3.3-70b"]

SIMPLE_PROMPT = (
    "You are CoCo, the Snowflake penguin, at a booth. Be warm, brief, concrete. "
    "No bullet points, no headings, no emoji, no em dashes. "
    "The visitor works in Financial Services at a retail bank and already holds: "
    "transaction history, customer profiles, fraud case notes. "
    "Reply in at most 2 short sentences: reflect back the most valuable thing in "
    "that list and name the one Snowflake capability that would unlock it."
)

JSON_PROMPT = (
    "The visitor works in Financial Services at a retail bank. They hold "
    "transaction history and customer profiles. In a workshop they said the POC "
    "should: give early warning of customers at risk of missed payments. "
    "Return ONLY minified JSON, no prose, with keys: archetype (one of "
    "talk-to-my-data, ask-my-documents, predict-what-happens-next, join-the-silos), "
    "poc_name (max 8 words), summary (2 sentences), first_step (one action), "
    "readiness (integer 1-5), reply (max 40 words, warm, no em dashes)."
)


def run(model, prompt):
    q = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', $${prompt}$$) AS R"
    t0 = time.time()
    p = subprocess.run(["snow", "sql", "-c", CONN, "--format", "json", "-q", q],
                       capture_output=True, text=True, timeout=120)
    secs = round(time.time() - t0, 1)
    if p.returncode != 0:
        err = (p.stderr or p.stdout or "").strip().replace("\n", " ")
        return secs, None, err[:160]
    try:
        rows = json.loads(p.stdout)
        reply = (rows[0].get("R") or "").strip()
    except Exception as e:  # noqa: BLE001
        return secs, None, f"parse: {e}"
    return secs, reply, "ok"


# Measure snow-sql CLI baseline so we can isolate model time.
base, _, _ = run("_baseline_", "x")  # will error but times the CLI round-trip
b2 = time.time()
subprocess.run(["snow", "sql", "-c", CONN, "--format", "json", "-q", "SELECT 1 AS R"],
               capture_output=True, text=True, timeout=60)
baseline = round(time.time() - b2, 1)
print(f"snow-sql baseline (SELECT 1): ~{baseline}s  [subtract to approx model time]\n")

print("=== SIMPLE turn (library-style, 2 sentences) ===")
print(f"{'model':<20}{'wall_s':>7}{'~model_s':>9}  status / reply")
print("-" * 78)
for m in SIMPLE_MODELS:
    secs, reply, status = run(m, SIMPLE_PROMPT)
    approx = round(max(secs - baseline, 0.0), 1)
    if reply:
        print(f"{m:<20}{secs:>7}{approx:>9}  {reply}", flush=True)
    else:
        print(f"{m:<20}{secs:>7}{approx:>9}  FAIL: {status}", flush=True)

print("\n=== WORKSHOP JSON feasibility ===")
for m in JSON_MODELS:
    secs, reply, status = run(m, JSON_PROMPT)
    approx = round(max(secs - baseline, 0.0), 1)
    ok_json = False
    if reply:
        try:
            json.loads(reply[reply.find("{"):reply.rfind("}") + 1])
            ok_json = True
        except Exception:  # noqa: BLE001
            ok_json = False
    tag = "valid-JSON" if ok_json else ("no-JSON" if reply else f"FAIL:{status}")
    print(f"{m:<20}{secs:>7}{approx:>9}  [{tag}] {(reply or '')[:120]}", flush=True)
