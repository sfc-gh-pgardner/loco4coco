"""Count the processes that authenticate to Snowflake in a booth run.

Under OAuth each one of these is a separate macOS keychain read, and therefore a
separate password dialog. Under key-pair auth every one of them is zero.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Where an auth-bearing subprocess is spawned, and how often it fires.
SITES = [
    ("deploy/bootstrap.py", "snow sql / dcm create / plan / deploy / post_hook",
     5, "setup, once per event account"),
    ("deploy/load_context.py", "snow sql -f, one per SQL file",
     None, "setup, once per event account"),
    ("game/context.py", "snow sql (bundle build)", 1, "setup"),
    ("deploy/verify_context.py", "snow sql (verify)", 1, "setup"),
    ("scripts/build_marketplace_index.py", "SHOW AVAILABLE LISTINGS", 1,
     "setup, per region"),
    ("game/smoke_test.py", "snow sql (row check)", 1, "setup / pre-doors"),
    ("game/agent_pool.py", "cortex mcp serve (warm agent)", 1,
     "once per server lifetime"),
    ("game/server.py:sf_conn", "pooled connector connection", 1,
     "once per server lifetime"),
    ("game/server.py:stage_and_presign", "snow stage copy", 1, "PER VISITOR"),
    ("game/server.py:1917", "snow sql (presign URL)", 1, "PER VISITOR"),
    ("game/server.py:3193", "snow sql (LIST stage)", 1, "PER VISITOR"),
]


def count_sql_files():
    d = ROOT / "deploy" / "sources" / "definitions"
    if not d.exists():
        d = ROOT / "deploy" / "sources"
    return len(list(d.rglob("*.sql"))) if d.exists() else 0


n_sql = count_sql_files()
setup = per_visitor = server = 0
print(f"{'site':44} {'what':38} {'n':>4}  when")
print("-" * 108)
for path, what, n, when in SITES:
    n = n_sql if n is None else n
    print(f"{path:44} {what:38} {n:>4}  {when}")
    if "PER VISITOR" in when:
        per_visitor += n
    elif "server lifetime" in when:
        server += n
    else:
        setup += n

print("-" * 108)
print(f"  setup, one-off per event account : {setup}")
print(f"  server start, once               : {server}")
print(f"  PER VISITOR                      : {per_visitor}")
for v in (30, 60, 100):
    print(f"    {v:3} visitors -> {setup + server + per_visitor * v:4} "
          f"authenticating processes")
print("\nUnder OAuth + client_store_temporary_credential, each is a keychain")
print("read and can raise a modal password dialog - including mid-visit.")
print("Under SNOWFLAKE_JWT key-pair auth, all of them are zero.")
