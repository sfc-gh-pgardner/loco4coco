"""Audit every AI call path the booth uses, against the live event account.

WHY THIS EXISTS

A model going to legacy state took the Reflection turn down silently for a whole
test run: claude-4-sonnet expired, every COMPLETE call failed in about half a
second, the exec fallback absorbed it, and the only trace was ok=False with no
reason. The booth has four distinct AI paths and they do not share a model
namespace, so "the model works" is not one question but several.

The paths, and what each depends on:

  1. COMPLETE          SNOWFLAKE.CORTEX.COMPLETE, SQL namespace.
                       Model: coco.complete_model, with coco.complete_model_fallbacks.
  2. QA model review   Also COMPLETE. Model: qa.model.
  3. cortex exec       Cortex Code agent namespace. Model: coco.model, null = CLI
                       default. A narrower namespace: several models that work in
                       COMPLETE are rejected here.
  4. warm agent        cortex mcp serve. Same binary, same namespace as exec.

Run it after being assigned an account, and after any model change.

    python3 scripts/audit_ai_paths.py
"""
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "game" / "config.json").read_text())
CONN = (CFG.get("snowflake") or {}).get("connection_name")
COCO = CFG.get("coco") or {}
QA = CFG.get("qa") or {}
PROBE = "Reply with exactly one word: ok"


def complete(cur, model):
    t = time.time()
    try:
        cur.execute("SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, %s)", (model, PROBE))
        reply = (cur.fetchone()[0] or "").strip()
        return (bool(reply), time.time() - t, reply[:40] or "empty reply")
    except Exception as e:
        msg = str(e)
        tag = ("legacy" if "legacy" in msg.lower() else
               "unknown model" if "unknown model" in msg.lower() or
               "not available" in msg.lower() else msg.split("\n")[0][:60])
        return (False, time.time() - t, tag)


def exec_probe(model):
    cmd = ["cortex", "exec", "--no-mcp", "-c", CONN]
    if model:
        cmd += ["-m", model]
    cmd += [PROBE]
    t = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return (False, time.time() - t, "timeout >180s")
    out = (r.stdout or "").strip()
    if r.returncode:
        err = (r.stderr or out or "").strip().replace("\n", " ")
        return (False, time.time() - t, err[:60] or f"exit {r.returncode}")
    return (bool(out), time.time() - t, out[:40] or "empty reply")


def row(path, model, ok, secs, note):
    mark = "PASS" if ok else "FAIL"
    print(f"{path:<22} {str(model or 'CLI default'):<18} {mark:<5} "
          f"{secs:>6.1f}s  {note}")


def main():
    print(f"connection {CONN}\n")
    import snowflake.connector as sc
    cn = sc.connect(connection_name=CONN)
    cur = cn.cursor()
    cur.execute("SELECT CURRENT_ACCOUNT(), CURRENT_REGION()")
    acct, region = cur.fetchone()
    print(f"account {acct}   region {region}\n")

    print(f"{'path':<22} {'model':<18} {'':<5} {'':>7}  note")
    print("-" * 78)

    fails = []

    # 1 and 2. Both go through COMPLETE, so both live or die by the SQL namespace.
    primary = COCO.get("complete_model")
    ok, s, n = complete(cur, primary)
    row("COMPLETE (reply)", primary, ok, s, n)
    if not ok:
        fails.append("COMPLETE primary")

    qam = QA.get("model")
    if qam and qam != primary:
        ok2, s2, n2 = complete(cur, qam)
        row("COMPLETE (QA review)", qam, ok2, s2, n2)
        if not ok2:
            fails.append("QA model")
    else:
        row("COMPLETE (QA review)", qam, ok, s, "same model as reply")

    # The fallback chain is only worth having if it is known-good. An untested
    # fallback is a second outage waiting for the first one.
    usable = [primary] if ok else []
    for m in (COCO.get("complete_model_fallbacks") or []):
        okf, sf, nf = complete(cur, m)
        row("  fallback", m, okf, sf, nf)
        if okf:
            usable.append(m)

    cur.close()
    cn.close()

    # 3 and 4. Agent namespace. coco.model null means the CLI default, which is
    # deliberately not pinned - pinning is what went legacy last time.
    okx, sx, nx = exec_probe(COCO.get("model"))
    row("cortex exec", COCO.get("model"), okx, sx, nx)
    if not okx:
        fails.append("cortex exec")

    print()
    print(f"COMPLETE models usable here: {len(usable)} "
          f"({', '.join(usable) if usable else 'NONE'})")
    if fails:
        print(f"\nFAIL - these paths are down: {', '.join(fails)}")
        if not usable:
            print("No COMPLETE model works. Reflection turns will fall back to "
                  "cortex exec and cost ~25s each; QA review will not run.")
        return 1
    print("\nPASS - every AI path the booth uses answers on this account.")
    if len(usable) < 2:
        print("Warning: only one usable COMPLETE model. If it goes legacy "
              "mid-event there is nothing to fall back to.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
