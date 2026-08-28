#!/usr/bin/env python3
"""One-command deployment of the Loco4CoCo booth to any Snowflake account.

    python3 deploy/bootstrap.py --target LONDON --connection <your-connection>
    python3 deploy/bootstrap.py --target <your-target> -c <your-connection> --plan-only

Steps, in order:

  1. Create the database and schema that HOLD the DCM project object. This is a
     prerequisite DCM cannot create for itself, so it is done in plain SQL.
  2. Archive any pre-v2 SESSIONS table. Detected by the presence of ROLE_STATED,
     a v1-only column. Renamed, never dropped.
  3. snow dcm create --if-not-exists
  4. snow dcm plan, shown in full and confirmed before anything is applied.
  5. snow dcm deploy
  6. Run hooks/post_hook.sql for the resource monitor, which DCM cannot define.
  7. Patch game/config.json to point at this account.
  8. Run game/smoke_test.py so the account is proven, not assumed.

Teardown:  EXECUTE DCM PROJECT <name> PURGE;  then  DROP DCM PROJECT <name>;
"""

import argparse
import json
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
GAME = os.path.join(PLUGIN, "game")
MANIFEST = os.path.join(HERE, "manifest.yml")


def run(cmd, **kw):
    print(f"\n$ {' '.join(cmd)}")
    return subprocess.run(cmd, text=True, **kw)


def sql(conn, statement, quiet=False):
    cmd = ["snow", "sql", "-q", statement, "--format", "json", "-c", conn]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        return None, (r.stderr or r.stdout or "").strip()[:400]
    try:
        return json.loads(r.stdout or "[]"), ""
    except json.JSONDecodeError:
        return [], ""


def load_target(target):
    with open(MANIFEST, encoding="utf-8") as f:
        man = yaml.safe_load(f)
    name = target or man.get("default_target")
    targets = man.get("targets") or {}
    if name not in targets:
        sys.exit(f"unknown target {name!r}. Available: {', '.join(targets)}")
    tgt = dict(targets[name])
    tmpl = man.get("templating") or {}
    vals = dict(tmpl.get("defaults") or {})
    cfgname = tgt.get("templating_config")
    if cfgname:
        vals.update((tmpl.get("configurations") or {}).get(cfgname) or {})
    return name, tgt, vals


def step1_project_schema(conn, project_name):
    db, schema, _ = project_name.split(".")
    print(f"\n[1/8] Project object home: {db}.{schema}")
    _, err = sql(conn, f"CREATE DATABASE IF NOT EXISTS {db} "
                       f"COMMENT='Holds the Loco4CoCo DCM project object'")
    if err:
        sys.exit(f"  failed: {err}")
    _, err = sql(conn, f"CREATE SCHEMA IF NOT EXISTS {db}.{schema}")
    if err:
        sys.exit(f"  failed: {err}")
    print("  ready")


def step2_archive_v1(conn, vals):
    """A pre-v2 SESSIONS carries ROLE_STATED, which the game can never populate.
    Rename it so DCM can create a clean table without losing the old rows."""
    db, schema = vals["db"], vals["schema"]
    print(f"\n[2/8] Checking for a pre-v2 {db}.{schema}.SESSIONS")
    rows, err = sql(conn, f"SELECT COUNT(*) AS N FROM {db}.INFORMATION_SCHEMA.COLUMNS "
                          f"WHERE TABLE_SCHEMA='{schema}' AND TABLE_NAME='SESSIONS' "
                          f"AND COLUMN_NAME='ROLE_STATED'")
    if err:
        print("  no existing database yet - nothing to archive")
        return
    n = 0
    if rows:
        first = rows[0] if isinstance(rows, list) else rows
        if isinstance(first, list):
            first = first[0] if first else {}
        n = int(first.get("N") or 0)
    if n == 0:
        print("  nothing to archive")
        return
    _, err = sql(conn, f"ALTER TABLE IF EXISTS {db}.{schema}.SESSIONS "
                       f"RENAME TO {db}.{schema}.SESSIONS_V1_ARCHIVE")
    print("  archived to SESSIONS_V1_ARCHIVE" if not err else f"  failed: {err}")


def step_plan(conn, target, plan_only):
    print("\n[3/8] Creating the DCM project object")
    run(["snow", "dcm", "create", "--if-not-exists", "--target", target, "-c", conn],
        cwd=HERE)
    print("\n[4/8] Planning (nothing is applied yet)")
    r = run(["snow", "dcm", "plan", "--target", target, "-c", conn], cwd=HERE)
    if r.returncode != 0:
        sys.exit("\nPlan failed. Fix the definitions before deploying.")
    if plan_only:
        print("\n--plan-only: stopping here.")
        sys.exit(0)


def step_deploy(conn, target, alias):
    print("\n[5/8] Deploying")
    r = run(["snow", "dcm", "deploy", "--target", target, "-c", conn,
             "--alias", alias], cwd=HERE)
    if r.returncode != 0:
        sys.exit("\nDeploy failed.")


def step_post_hook(conn, vals):
    print("\n[6/8] Resource monitor (DCM cannot define one)")
    cmd = ["snow", "sql", "-f", os.path.join(HERE, "hooks", "post_hook.sql"),
           "--enable-templating", "JINJA", "-c", conn, "--format", "json"]
    for k in ("monitor", "monitor_quota", "wh", "monitor_notify_user"):
        cmd += ["-D", f"{k}={vals[k]}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"  WARNING: post-hook failed: {(r.stderr or r.stdout)[:300]}")
        print("  The booth will still run, but nothing is capping its spend.")
        return
    # A monitor with empty notify_users cannot warn anyone, so check rather than assume.
    rows, _ = sql(conn, f"SHOW RESOURCE MONITORS LIKE '{vals['monitor']}'")
    notify = ""
    if rows:
        first = rows[0] if isinstance(rows, list) else rows
        if isinstance(first, list):
            first = first[0] if first else {}
        notify = first.get("notify_users") or ""
    print(f"  {vals['monitor']}: quota {vals['monitor_quota']}, "
          f"notify_users={notify or 'EMPTY - nobody will be warned'}")


def step_config(conn, vals):
    print("\n[7/8] Pointing game/config.json at this account")
    path = os.path.join(GAME, "config.json")
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["snowflake"]["connection_name"] = conn
    cfg["snowflake"]["database"] = vals["db"]
    cfg["snowflake"]["schema"] = vals["schema"]
    cfg["event"]["city"] = vals["city"]
    cfg["event"]["language"] = vals["language"]
    cfg["delivery"]["stage"] = f"@{vals['db']}.{vals['schema']}.BLUEPRINTS"
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)
    print(f"  connection={conn} db={vals['db']}.{vals['schema']} city={vals['city']}")


def step_smoke(skip):
    print("\n[8/8] Smoke test")
    if skip:
        print("  skipped (--skip-smoke). The account is NOT proven.")
        return
    print("  Needs the game server running: python3 game/server.py")
    r = run([sys.executable, "smoke_test.py"], cwd=GAME)
    if r.returncode != 0:
        sys.exit("\nSmoke test failed - the account is not ready.")
    print("\nDeployment proven end to end.")


def main():
    ap = argparse.ArgumentParser(description="Deploy the Loco4CoCo booth.")
    ap.add_argument("--target", help="target from manifest.yml")
    ap.add_argument("--connection", "-c", required=True, help="snow CLI connection")
    ap.add_argument("--alias", default="bootstrap")
    ap.add_argument("--plan-only", action="store_true", help="stop after plan")
    ap.add_argument("--skip-smoke", action="store_true")
    a = ap.parse_args()

    target, tgt, vals = load_target(a.target)
    print(f"Target      : {target}")
    print(f"Account     : {tgt.get('account_identifier')}")
    print(f"Connection  : {a.connection}")
    print(f"Objects     : {vals['db']}.{vals['schema']}  +  {vals['wh']}")

    rows, err = sql(a.connection, "SELECT CURRENT_ORGANIZATION_NAME()||'-'||"
                                  "CURRENT_ACCOUNT_NAME() AS ACCT")
    if err:
        sys.exit(f"Cannot reach the account: {err}")
    live = ""
    if rows:
        first = rows[0] if isinstance(rows, list) else rows
        if isinstance(first, list):
            first = first[0] if first else {}
        live = first.get("ACCT") or ""
    if live.upper() != str(tgt.get("account_identifier")).upper():
        sys.exit(f"\nRefusing to deploy: connection {a.connection!r} is on {live}, "
                 f"but target {target!r} expects {tgt.get('account_identifier')}.\n"
                 f"Deploying booth objects to the wrong account is not something "
                 f"to discover afterwards.")
    print(f"Verified    : connection is on {live}")

    step1_project_schema(a.connection, tgt["project_name"])
    step2_archive_v1(a.connection, vals)
    step_plan(a.connection, target, a.plan_only)
    step_deploy(a.connection, target, a.alias)
    step_post_hook(a.connection, vals)
    step_config(a.connection, vals)
    step_smoke(a.skip_smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
