"""Repeat-measure the COMPLETE models that actually answer in this region.

One call proves availability, not latency: the first call on a cold warehouse is
dominated by resume time. Three reps, report each and the median.
"""
import json
import statistics
import subprocess
import time

CANDIDATES = [
    "llama3.3-70b",
    "mistral-large2",
    "claude-4-sonnet",
    "claude-4-5-sonnet",
    "claude-3-7-sonnet",
    "openai-gpt-4.1-mini",
    "openai-gpt-5-mini",
    "llama3.1-70b",
]
REPS = 3

cfg = json.load(open('game/config.json'))
PROMPT = cfg['locations']['library']['prompt'].format(
    industry="Manufacturing & Industrial",
    company="Hoffmann Maschinenbau",
    problem="We cannot see which supplier delays are about to stop a production line.",
    selection="ERP order data, supplier delivery records, machine sensor logs",
    platforms="SAP and on-premise SQL Server",
)

rows = []
for m in CANDIDATES:
    times, out = [], None
    for _ in range(REPS):
        t0 = time.time()
        p = subprocess.run(
            ["snow", "sql", "-q",
             f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{m}', $${PROMPT}$$) AS r",
             "--format", "json", "--enable-templating", "NONE"],
            capture_output=True, text=True, timeout=240)
        dt = time.time() - t0
        if p.returncode != 0:
            times = None
            out = (p.stderr or p.stdout).strip().replace('\n', ' ')
            break
        times.append(dt)
        try:
            out = json.loads(p.stdout)[0]['R']
        except Exception:
            out = p.stdout[:100]
    if times:
        rows.append((m, times, statistics.median(times), out))
        reps = "  ".join(f"{t:5.1f}" for t in times)
        print(f"{m:22} {reps}   median {statistics.median(times):5.1f}s  {len(out):4}ch")
    else:
        code = out.split('(P0000)')[0].strip()[-20:] if out else '?'
        print(f"{m:22} unavailable  {code}")

print("\n" + "=" * 74)
for m, t, med, out in sorted(rows, key=lambda r: r[2]):
    print(f"\n### {m}  median {med:.1f}s\n{out.strip()}")
