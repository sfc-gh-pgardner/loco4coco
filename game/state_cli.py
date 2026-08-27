#!/usr/bin/env python3
"""Booth control CLI - reset between visitors, days and rehearsals.

  python3 state_cli.py reset                  # between visitors (default)
  python3 state_cli.py reset --level day      # start of an event day
  python3 state_cli.py reset --level all      # after a rehearsal
  python3 state_cli.py reset --level all --purge-rows   # also clear Snowflake
  python3 state_cli.py show                   # current state

Reset levels
------------
  visitor  state.json only. Same thing the NEW VISITOR button does.
  day      + cost.jsonl.
  all      + optionally clears SESSIONS and TURNS with --purge-rows.

Information governance: nothing about a visitor is kept on the booth between
sessions. state.json is replaced wholesale, and any stray local file is purged.
The outbox is gone - email was removed, so there is no local blueprint record to
drain; the QR to the presigned stage .docx is the delivery. The ONLY intended
persistence is the governed Snowflake SESSIONS/TURNS row, one per visitor.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from server import (BLANK_STATE, load_config, purge_temp_artifacts, read_state,  # noqa: E402
                    write_state)

STATE = os.path.join(HERE, "state.json")


def purge_outbox(cfg):
    """Delete any stray outbox files. The outbox was removed with email, so this
    is belt-and-braces: if an old build or a manual copy left PII on disk, it is
    cleared rather than left to accumulate on a shared laptop. Returns a count."""
    out = os.path.join(HERE, (cfg.get("delivery") or {}).get("outbox_dir", "outbox"))
    if not os.path.isdir(out):
        return 0
    removed = 0
    for name in os.listdir(out):
        if name == ".gitkeep":
            continue
        path = os.path.join(out, name)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            removed += 1
        except OSError:
            pass
    return removed


def purge_rows(cfg):
    sf = cfg.get("snowflake") or {}
    db, sch = sf.get("database"), sf.get("schema")
    conn = sf.get("connection_name")
    sql = f"DELETE FROM {db}.{sch}.SESSIONS; DELETE FROM {db}.{sch}.TURNS;"
    cmd = ["snow", "sql", "-q", sql]
    if conn:
        cmd += ["-c", conn]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        return r.returncode == 0, (r.stderr or r.stdout or "").strip()[:200]
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return False, str(e)[:200]


def do_reset(a):
    cfg = load_config()
    level = a.level

    write_state(dict(BLANK_STATE), replace=True)
    print("visitor state cleared")

    removed = purge_outbox(cfg)
    if removed:
        print(f"purged {removed} stray local file(s) - no visitor PII kept on disk")
    tmp = purge_temp_artifacts()
    if tmp:
        print(f"cleared {tmp} temp blueprint file(s) from the OS temp dir")

    if level in ("day", "all"):
        cost = os.path.join(HERE, (cfg.get("coco") or {}).get("cost_log", "cost.jsonl"))
        if os.path.exists(cost):
            os.replace(cost, cost + "." + time.strftime("%Y-%m-%d") + ".bak")
            print("cost log rolled")

    if level == "all" and a.purge_rows:
        ok, err = purge_rows(cfg)
        print("Snowflake rows cleared" if ok else f"row purge FAILED: {err}")
        if not ok:
            return 1
    elif level == "all":
        print("Snowflake rows left intact (pass --purge-rows to clear them)")

    return 0


def do_show(_a):
    st = read_state()
    vis = st.get("visitor") or {}
    poc = st.get("poc") or {}
    print(f"stage      : {st.get('stage')}")
    print(f"session_id : {st.get('session_id') or '-'}")
    print(f"visitor    : {vis.get('first_name') or '-'} / {vis.get('company') or '-'}"
          f" / {vis.get('industry') or '-'}")
    print(f"held       : {len(st.get('held') or [])} | joined: {len(st.get('joined') or [])}")
    print(f"poc        : {poc.get('poc_name') or '-'} (readiness {poc.get('readiness') or '-'})")
    print(f"delivered  : {bool(st.get('blueprint_url'))}")
    print(f"logged     : {st.get('logged')}"
          + (f"  ERROR: {st.get('log_error')}" if st.get("log_error") else ""))
    print(f"coco       : {st.get('coco_seconds')}s, "
          f"{st.get('input_tokens')} in / {st.get('output_tokens')} out tokens")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Loco4CoCo booth control.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("reset", help="clear state at one of three levels")
    r.add_argument("--level", choices=("visitor", "day", "all"), default="visitor")
    r.add_argument("--purge-rows", action="store_true",
                   help="with --level all, also DELETE SESSIONS and TURNS rows")
    r.add_argument("--yes", action="store_true",
                   help="accepted for backwards compatibility; reset no longer prompts")

    sub.add_parser("show", help="print the current session")

    a = ap.parse_args()
    return {"reset": do_reset, "show": do_show}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
