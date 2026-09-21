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
    print("\n[8/9] Pointing game/config.json at this account")
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
    print("\n[9/9] Smoke test")
    if skip:
        print("  skipped (--skip-smoke). The account is NOT proven.")
        return
    print("  Needs the game server running: python3 game/server.py")
    r = run([sys.executable, "smoke_test.py"], cwd=GAME)
    if r.returncode != 0:
        sys.exit("\nSmoke test failed - the account is not ready.")
    print("\nDeployment proven end to end.")


def step_keypair(conn, skip):
    """Swap the booth onto key-pair auth so the keychain never interrupts a visit.

    A DataOps event account is handed out with OAuth
    (`client_store_temporary_credential = true`), which caches its token in the
    macOS keychain. macOS then asks permission once per *process* that reads it,
    and the booth is process-heavy: 3 per visitor, ~312 over a 100-visitor day.
    Any one of those is a modal password dialog in front of a visitor.

    Key-pair auth has no token to cache, so it never touches the keychain. This
    runs it automatically rather than leaving it as a step an operator can skip.

    It converts the connection from step 0 in place rather than creating a second
    one. An earlier version created a connection called BOOTH; that left the
    operator's own connection still selected in the Cortex Code picker, still on
    OAuth, so the browser prompts carried on regardless.

    It cannot be made completely invisible: registering a public key needs an
    authenticated session first, and on a fresh laptop the only credential
    available is OAuth. So a couple of prompts before this point are structural.
    What this guarantees is that none happen once the doors open.
    """
    if skip:
        print("\n[7/9] Key-pair auth: SKIPPED (--skip-keypair)")
        print("   The booth will keep using the keychain: expect ~3 macOS "
              "password prompts per visitor.")
        return conn
    print("\n[7/9] Key-pair auth: removing the keychain from the auth path")
    script = os.path.join(os.path.dirname(HERE), "scripts", "setup_keypair.py")
    if not os.path.exists(script):
        print(f"   ! {script} missing, leaving auth as it is")
        return conn
    r = run([sys.executable, script, "--connection", conn])
    if r.returncode:
        # Never fatal. A pool account that will not allow ALTER USER still runs
        # the booth perfectly well - it just prompts. Losing a deploy over an
        # ergonomics fix would be the wrong trade.
        tail = (r.stderr or r.stdout or "").strip().splitlines()[-3:]
        print("   ! could not set up key-pair auth, continuing on the existing "
              "connection:")
        for line in tail:
            print(f"     {line[:150]}")
        print("   The booth still works. Expect macOS keychain prompts, "
              "including mid-visit.")
        print("   Most likely cause: this account does not permit "
              "ALTER USER ... SET RSA_PUBLIC_KEY.")
        return conn
    print(f"   {conn} converted and verified - no keychain from here on.")
    print(f"   Keep using -c {conn}: the name has not changed.")
    # Prove it, rather than assume it. The booth being on key-pair is not enough:
    # the CLI default and Cortex Code hold their own connection names, and either
    # can open a browser mid-event.
    audit = os.path.join(os.path.dirname(HERE), "scripts",
                         "check_auth_safety.py")
    if os.path.exists(audit):
        r2 = run([sys.executable, audit])
        if r2.returncode:
            print("   ! something can still prompt - see the audit above")
    return conn


def main():
    ap = argparse.ArgumentParser(description="Deploy the Loco4CoCo booth.")
    ap.add_argument("--target", help="target from manifest.yml")
    ap.add_argument("--connection", "-c", required=True, help="snow CLI connection")
    ap.add_argument("--alias", default="bootstrap")
    ap.add_argument("--plan-only", action="store_true", help="stop after plan")
    ap.add_argument("--skip-smoke", action="store_true")
    ap.add_argument("--skip-keypair", action="store_true",
                    help="do not convert to key-pair auth (you will get macOS "
                         "keychain prompts, ~3 per visitor)")
    a = ap.parse_args()

    target, tgt, vals = load_target(a.target)
    pinned = (tgt.get("account_identifier") or "").strip()
    print(f"Target      : {target}")
    print(f"Account     : {pinned or '(not pinned - deploying wherever this connection points)'}")
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
    # Only enforced when a target names an account. The EVENT target deliberately
    # does not: every event gets its own freshly provisioned, randomly named AWS
    # Frankfurt account, so there is nothing stable to pin and demanding one would
    # just be friction. The pinned targets are long-lived accounts where deploying
    # to the wrong one is a real risk worth refusing.
    if pinned and live.upper() != pinned.upper():
        sys.exit(f"\nRefusing to deploy: connection {a.connection!r} is on {live}, "
                 f"but target {target!r} expects {pinned}.\n"
                 f"Deploying booth objects to the wrong account is not something "
                 f"to discover afterwards.")
    print(f"Verified    : connection is on {live}")

    step1_project_schema(a.connection, tgt["project_name"])
    step2_archive_v1(a.connection, vals)
    step_plan(a.connection, target, a.plan_only)
    step_deploy(a.connection, target, a.alias)
    step_post_hook(a.connection, vals)
    # Before step_config, which writes the connection name into game/config.json:
    # if we converted to key-pair, that is the name the booth must record.
    booth_conn = step_keypair(a.connection, a.skip_keypair)
    step_config(booth_conn, vals)
    step_smoke(a.skip_smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
