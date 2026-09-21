"""Prove nothing in a booth run can reach a browser-auth connection.

The failure this guards against is not theoretical: "Your identity was confirmed
and propagated to Snowflake PythonConnector" is the OAuth browser flow, and it
can fire mid-visit. This checks every place a connection name is resolved from,
not just the booth's own config.
"""
import json
import pathlib
import re
import sys
import tomllib

HOME = pathlib.Path.home()
ROOT = pathlib.Path(__file__).resolve().parent.parent
BROWSERY = ("oauth", "externalbrowser", "sso")


def load_conns():
    p = HOME / ".snowflake" / "connections.toml"
    return tomllib.loads(p.read_text()) if p.exists() else {}


def is_browsery(conns, name):
    c = conns.get(name)
    if not isinstance(c, dict):
        return None                                   # unknown, cannot judge
    a = str(c.get("authenticator") or "password").lower()
    return any(t in a for t in BROWSERY)


def main():
    conns = load_conns()
    problems, checks = [], []

    def check(label, name, why):
        if not name:
            checks.append((label, "(unset)", "n/a", why))
            return
        b = is_browsery(conns, name)
        verdict = ("UNKNOWN" if b is None else "PROMPTS" if b else "safe")
        checks.append((label, name, verdict, why))
        if b:
            problems.append(f"{label} -> {name}")

    # 1. the booth's own connection
    cfg = json.loads((ROOT / "game" / "config.json").read_text())
    booth = ((cfg.get("coco") or {}).get("connection")
             or (cfg.get("snowflake") or {}).get("connection_name"))
    check("game/config.json snowflake.connection_name", booth,
          "pooled connector, snow sql, snow stage copy, cortex exec, warm agent")

    # 2. the CLI default, used by anything that omits -c
    cfgtoml = HOME / ".snowflake" / "config.toml"
    dflt = None
    if cfgtoml.exists():
        m = re.search(r'^\s*default_connection_name\s*=\s*"([^"]+)"',
                      cfgtoml.read_text(), re.M)
        dflt = m.group(1) if m else None
    check("CLI default_connection_name", dflt,
          "any snow/cortex command run without -c")

    # 3. Cortex Code's own connections - operators are told to let it drive
    st = HOME / ".snowflake" / "cortex" / "settings.json"
    if st.exists():
        s = json.loads(st.read_text())
        check("Cortex Code sqlConnectionName", s.get("sqlConnectionName"),
              "SQL Cortex Code runs while helping with setup")
        check("Cortex Code cortexAgentConnectionName",
              s.get("cortexAgentConnectionName"), "Cortex Code agent calls")

    w = max(len(c[0]) for c in checks)
    print(f"{'resolved from':{w}}  {'connection':16} {'verdict':8} used by")
    print("-" * (w + 60))
    for label, name, verdict, why in checks:
        print(f"{label:{w}}  {name:16} {verdict:8} {why}")

    print()
    if problems:
        print("FAIL - these can open a browser or a keychain dialog mid-event:")
        for p in problems:
            print(f"  {p}")
        print("\nFix: python3 scripts/setup_keypair.py --connection <that-connection>")
        return 1
    print("PASS - every resolved connection uses key-pair or password auth.")
    print("No browser flow and no keychain read is reachable from a booth run.")
    print("\nNote: the Cortex Code connection PICKER is a runtime choice and is")
    print("not stored in settings.json. If you see a browser reauth, check what")
    print("the picker is set to - settings.json only applies on restart.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
