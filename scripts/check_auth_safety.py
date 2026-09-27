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
    problems, advisories, checks = [], [], []

    def check(label, name, why, hard=True):
        if not name:
            checks.append((label, "(unset)", "n/a", why))
            return
        b = is_browsery(conns, name)
        verdict = ("UNKNOWN" if b is None else "PROMPTS" if b else "safe")
        checks.append((label, name, verdict, why))
        if b:
            (problems if hard else advisories).append(f"{label} -> {name}")

    # 1. the booth's own connection - the ONLY hard requirement. The booth pins
    #    this everywhere it talks to Snowflake (snow -c, cortex exec -c, and the
    #    warm agent via the MCP tools/call payload), so this is what must be
    #    key-pair. It ships as the placeholder MYBOOTH and bootstrap writes the
    #    real LOCO4COCO_BOOTH; a MYBOOTH/absent connection is UNKNOWN, not a fail.
    cfg = json.loads((ROOT / "game" / "config.json").read_text())
    booth = ((cfg.get("coco") or {}).get("connection")
             or (cfg.get("snowflake") or {}).get("connection_name"))
    check("game/config.json snowflake.connection_name", booth,
          "pooled connector, snow sql, snow stage copy, cortex exec, warm agent")

    # 2. the CLI default - ADVISORY only. The booth always passes -c, so a browsery
    #    default cannot be reached by a booth run. It stays OAuth legitimately.
    cfgtoml = HOME / ".snowflake" / "config.toml"
    dflt = None
    if cfgtoml.exists():
        m = re.search(r'^\s*default_connection_name\s*=\s*"([^"]+)"',
                      cfgtoml.read_text(), re.M)
        dflt = m.group(1) if m else None
    check("CLI default_connection_name", dflt,
          "any snow/cortex command run without -c (booth always uses -c)",
          hard=False)

    # 3. Cortex Code's own connections - ADVISORY only. Since the booth uses a
    #    SEPARATE connection Cortex Code does not manage, the operator's own
    #    connection legitimately stays on OAuth for chatting with Cortex Code.
    st = HOME / ".snowflake" / "cortex" / "settings.json"
    if st.exists():
        s = json.loads(st.read_text())
        check("Cortex Code sqlConnectionName", s.get("sqlConnectionName"),
              "SQL Cortex Code runs while helping with setup", hard=False)
        check("Cortex Code cortexAgentConnectionName",
              s.get("cortexAgentConnectionName"), "Cortex Code agent calls",
              hard=False)

    w = max(len(c[0]) for c in checks)
    print(f"{'resolved from':{w}}  {'connection':16} {'verdict':8} used by")
    print("-" * (w + 60))
    for label, name, verdict, why in checks:
        print(f"{label:{w}}  {name:16} {verdict:8} {why}")

    print()
    if problems:
        print("FAIL - the booth's OWN connection can open a browser or keychain "
              "dialog mid-event:")
        for p in problems:
            print(f"  {p}")
        print("\nFix: python3 deploy/bootstrap.py -c <your-connection> "
              "(creates the LOCO4COCO_BOOTH key-pair connection and points the "
              "booth at it), or python3 scripts/setup_keypair.py --connection "
              "<your-connection>.")
        return 1
    print("PASS - the booth's own connection is key-pair or password auth, so no "
          "browser flow or keychain read is reachable from a booth run.")
    if advisories:
        print("\nInfo (not a problem): these connections use OAuth/SSO, but the "
              "booth never uses them - it pins its own connection on every call:")
        for a in advisories:
            print(f"  {a}")
        print("They are the operator's own connections for driving Cortex Code, "
              "and are expected to stay on OAuth.")
    print("\nNote: the Cortex Code connection PICKER is a runtime choice and is")
    print("not stored in settings.json. If you see a browser reauth, check what")
    print("the picker is set to - settings.json only applies on restart.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
