#!/usr/bin/env python3
"""Booth control CLI - reset between visitors, days and rehearsals.

  python3 state_cli.py reset                  # between visitors (default)
  python3 state_cli.py reset --level day      # start of an event day
  python3 state_cli.py reset --level all      # after a rehearsal
  python3 state_cli.py reset --level all --purge-rows   # also clear Snowflake
  python3 state_cli.py show                   # current state
  python3 state_cli.py outbox                 # what is waiting to be drained

The old `stage` subcommand is gone. It drove a v1 flow where CoCo pushed stage
changes into the display; the game now drives itself through its own HTTP
endpoints, and the command referenced config["stages"], which no longer exists.
A command that crashes on every invocation is worse than no command.

Reset levels
------------
  visitor  state.json only. Same thing the NEW VISITOR button does.
  day      + cost.jsonl, and archives the outbox.
  all      + optionally clears SESSIONS and TURNS with --purge-rows.

The outbox is ALWAYS archived, never deleted. An undrained record is somebody's
blueprint that has not reached them yet, and losing it silently is the same
class of failure as telling a visitor their email was sent when it was not.
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
from server import BLANK_STATE, load_config, read_state, write_state  # noqa: E402

STATE = os.path.join(HERE, "state.json")


def outbox_dir(cfg):
    return os.path.join(HERE, (cfg.get("delivery") or {}).get("outbox_dir", "outbox"))


def pending(cfg):
    """Outbox records that have not been drained yet."""
    out = outbox_dir(cfg)
    if not os.path.isdir(out):
        return []
    found = []
    for name in sorted(os.listdir(out)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(out, name)
        try:
            with open(path, encoding="utf-8") as f:
                rec = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if not rec.get("sent"):
            found.append((name, rec))
    return found


def archive_outbox(cfg):
    """Move every outbox record into a dated archive folder. Returns counts."""
    out = outbox_dir(cfg)
    if not os.path.isdir(out):
        return 0, 0
    dest = os.path.join(out, "archive", time.strftime("%Y-%m-%d"))
    os.makedirs(dest, exist_ok=True)
    moved = undrained = 0
    for name in sorted(os.listdir(out)):
        if not name.endswith(".json"):
            continue
        src = os.path.join(out, name)
        try:
            with open(src, encoding="utf-8") as f:
                if not json.load(f).get("sent"):
                    undrained += 1
        except (OSError, json.JSONDecodeError):
            pass
        target = os.path.join(dest, name)
        if os.path.exists(target):
            target = os.path.join(dest, f"{int(time.time())}-{name}")
        shutil.move(src, target)
        moved += 1
    return moved, undrained


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

    waiting = pending(cfg)
    if waiting and level in ("day", "all") and not a.yes:
        print(f"{len(waiting)} outbox record(s) have NOT been drained yet:")
        for name, rec in waiting:
            print(f"  {name}  ->  {rec.get('to')}")
        print("\nThese are blueprints nobody has received. Drain them first "
              "(see the loco4coco-ops skill), or re-run with --yes to archive "
              "them anyway. They will be moved, not deleted.")
        return 1

    write_state(dict(BLANK_STATE), replace=True)
    print("visitor state cleared")

    if level in ("day", "all"):
        cost = os.path.join(HERE, (cfg.get("coco") or {}).get("cost_log", "cost.jsonl"))
        if os.path.exists(cost):
            os.replace(cost, cost + "." + time.strftime("%Y-%m-%d") + ".bak")
            print("cost log rolled")
        moved, undrained = archive_outbox(cfg)
        if moved:
            print(f"outbox archived: {moved} record(s)"
                  + (f", {undrained} of which were NEVER DRAINED" if undrained else ""))

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
    print(f"queued     : {st.get('queued')} | drafted: {st.get('draft_created')}"
          f" | email_sent: {st.get('email_sent')}")
    print(f"logged     : {st.get('logged')}"
          + (f"  ERROR: {st.get('log_error')}" if st.get("log_error") else ""))
    print(f"coco       : {st.get('coco_seconds')}s, "
          f"{st.get('input_tokens')} in / {st.get('output_tokens')} out tokens")
    return 0


def do_outbox(_a):
    cfg = load_config()
    waiting = pending(cfg)
    if not waiting:
        print("outbox is empty - nothing waiting to be drained")
        return 0
    print(f"{len(waiting)} record(s) waiting to be drained:\n")
    for name, rec in waiting:
        print(f"  {name}")
        print(f"    to      : {rec.get('to')}")
        print(f"    subject : {rec.get('subject')}")
        print(f"    doc     : {'yes' if rec.get('document_url') else 'no'}")
    print("\nDrain these from an INTERACTIVE CoCo session - the Gmail MCP tools "
          "do not load under `cortex exec`.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Loco4CoCo booth control.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("reset", help="clear state at one of three levels")
    r.add_argument("--level", choices=("visitor", "day", "all"), default="visitor")
    r.add_argument("--purge-rows", action="store_true",
                   help="with --level all, also DELETE SESSIONS and TURNS rows")
    r.add_argument("--yes", action="store_true",
                   help="archive undrained outbox records without asking")

    sub.add_parser("show", help="print the current session")
    sub.add_parser("outbox", help="list records waiting to be drained")

    a = ap.parse_args()
    return {"reset": do_reset, "show": do_show, "outbox": do_outbox}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
