#!/usr/bin/env python3
"""One-off latency benchmark for Loco4CoCo turns.

Reuses the real prompt builders from server.py and times `cortex exec` across
effort levels for the three model-backed turns (library, marketplace, workshop).
Read-only: never writes game state or history (--no-history). Bounded: hard
per-call timeout, sequential, prints a table then exits.
"""
import json
import subprocess
import sys
import time

import server as S

EFFORTS = ["minimal", "low", "medium"]
PER_CALL_TIMEOUT = 150  # seconds; kill any call that overruns

cfg = S.load_config()
conn = (cfg.get("snowflake") or {}).get("connection_name")

# Synthetic but realistic session: a healthcare visitor who has ticked a few
# library shelves and picked real marketplace listings for that industry.
IND = "healthcare"
state = {
    "visitor": {"first_name": "Sam", "company": "Northgate NHS Trust",
                "email": "sam@example.org", "industry": IND},
}
held_opts = [o["label"] for o in S.options_for(cfg, "library", state)][:4]
state["held"] = held_opts or ["patient records", "bed occupancy", "staff rotas"]
join_opts = [o["label"] for o in S.options_for(cfg, "marketplace", state)][:3]
state["joined"] = join_opts or ["population health data"]

locs = cfg.get("locations") or {}


def build_prompt(loc_id):
    loc = locs.get(loc_id) or {}
    if loc_id == "workshop":
        feats = ", ".join(sorted(S.load_features()))
        body = S.fill(loc.get("prompt", ""), cfg, state,
                      input="answer questions about our policies with citations",
                      feature_list=feats)
    else:
        sel = state["held"] if loc_id == "library" else state["joined"]
        body = S.fill(loc.get("prompt", ""), cfg, state,
                      selection=", ".join(sel) or "nothing")
    return "\n".join(S.base_context(cfg, state)) + "\n\n" + body


def time_exec(prompt, effort):
    cmd = [cfg.get("coco", {}).get("binary", "cortex"), "exec", prompt,
           "--format", "json", "--no-mcp", "--no-history", "--effort", effort]
    if conn:
        cmd += ["--connection", conn]
    t0 = time.time()
    out_tokens, ok = 0, False
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True, cwd=S.HERE)
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
                out_tokens = (ev.get("usage") or {}).get("output_tokens", 0)
            if time.time() - t0 > PER_CALL_TIMEOUT:
                p.kill()
                break
        p.wait(timeout=10)
    except Exception as e:  # noqa: BLE001
        return None, 0, f"err:{e}"
    return round(time.time() - t0, 1), out_tokens, ("ok" if ok else "FAIL")


print(f"industry={IND}  held={state['held']}  joined={state['joined']}\n")
print(f"{'turn':<12}{'effort':<10}{'seconds':>9}{'out_tok':>9}  status")
print("-" * 52)
results = {}
for loc_id in ("library", "marketplace", "workshop"):
    prompt = build_prompt(loc_id)
    for eff in EFFORTS:
        secs, toks, status = time_exec(prompt, eff)
        results[(loc_id, eff)] = secs
        print(f"{loc_id:<12}{eff:<10}{str(secs):>9}{toks:>9}  {status}",
              flush=True)

print("\nbaseline (prior smoke, default effort): "
      "library~30s marketplace~31s workshop~53s")
