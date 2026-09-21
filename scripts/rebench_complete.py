"""Re-bench COMPLETE models after claude-4-sonnet went legacy.

Checks availability, speed, and one quality probe whose right answer is Dynamic
Tables - the probe that previously separated the good models from the ones that
recommended Materialized Views or Time Travel.
"""
import json
import statistics
import sys
import time

import snowflake.connector as sc

CFG = json.load(open("game/config.json"))
CONN = (CFG.get("snowflake") or {}).get("connection_name")

# Current generation, taken from the Cortex Code model picker. Most of these
# names work in SNOWFLAKE.CORTEX.COMPLETE too - the two namespaces overlap more
# than expected, and benching the previous generation is what produced a default
# that later went legacy.
CANDIDATES = [
    "claude-opus-5", "claude-sonnet-5", "openai-gpt-5.4", "grok-4.6",
    "openai-gpt-5", "openai-gpt-5-mini", "llama3.1-70b",
]

PROBE = (
    "A manufacturer wants a table that refreshes automatically as new rows land "
    "upstream, without them writing scheduling or merge logic. Name the single "
    "Snowflake feature they should use. Answer in under 25 words."
)
REPS = 2

cn = sc.connect(connection_name=CONN)
cur = cn.cursor()
results = []

for mdl in CANDIDATES:
    times, reply, err = [], "", None
    for _ in range(REPS):
        t = time.time()
        try:
            cur.execute(
                "SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, ARRAY_CONSTRUCT("
                "OBJECT_CONSTRUCT('role','user','content',%s)), "
                "OBJECT_CONSTRUCT())", (mdl, PROBE))
            raw = (cur.fetchone() or [""])[0]
            d = json.loads(raw) if isinstance(raw, str) else raw
            ch = (d.get("choices") or [{}])[0]
            reply = str(ch.get("messages") or ch.get("message") or "").strip()
            times.append(time.time() - t)
        except Exception as e:
            err = str(e)[:110].replace("\n", " ")
            break
    if err:
        print(f"{mdl:28} UNAVAILABLE  {err}")
        continue
    med = statistics.median(times)
    low = reply.lower()
    verdict = ("DYNAMIC TABLE" if "dynamic table" in low
               else "WRONG: materialized" if "materialized" in low
               else "WRONG: time travel" if "time travel" in low
               else "WRONG: stream/task" if "task" in low or "stream" in low
               else "unclear")
    results.append((med, mdl, verdict, reply))
    print(f"{mdl:28} {med:6.1f}s  {verdict:20} {reply[:80]}")

print("\n--- ranked by speed among those that answered Dynamic Tables ---")
for med, mdl, v, _ in sorted(results):
    if v == "DYNAMIC TABLE":
        print(f"  {mdl:28} {med:6.1f}s")

cur.close()
cn.close()
