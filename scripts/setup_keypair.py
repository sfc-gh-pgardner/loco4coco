"""Create a separate booth connection on key-pair auth alongside the operator's own.

WHY A SEPARATE CONNECTION

An earlier version converted the operator's connection in place.  That worked
when connections.toml was only edited by this script, but Cortex Code's
"Snowflake Managed Config" continuously manages the connection it is pointed
at: it overwrites authenticator, injects tokens, and strips keys it does not
recognise.  The result is that the operator's connection reverts from
SNOWFLAKE_JWT back to OAuth within seconds, the snow CLI fails ("Private Key
authentication requires authenticator set to SNOWFLAKE_JWT"), and the Python
connector falls back to keychain prompts - silently undoing the conversion.

The fix is to leave the operator's connection alone and create a new one called
LOCO4COCO_BOOTH.  Cortex Code does not manage a connection it did not create,
so LOCO4COCO_BOOTH stays on key-pair permanently.  bootstrap.py writes
LOCO4COCO_BOOTH into game/config.json, so the game server, snow CLI calls, and
cortex exec all use it.

WHY AT ALL

DataOps event accounts are handed out with `authenticator =
oauth_authorization_code` and `client_store_temporary_credential = true`.  The
OAuth token is cached in the macOS keychain, so macOS asks permission once per
process - about 3 per visitor, ~312 over a hundred-visitor day - and when the
token expires the recovery path is a browser window.  Key-pair auth has no token
to cache and nothing to expire.

Usage:
    python3 scripts/setup_keypair.py --connection MYBOOTH
"""
import argparse
import datetime
import pathlib
import re
import shutil
import subprocess
import sys
import tomllib

HOME = pathlib.Path.home()
TOML = HOME / ".snowflake" / "connections.toml"
KEYDIR = HOME / ".snowflake" / "keys"
BROWSERY = ("oauth", "externalbrowser", "sso")
BOOTH_CONN = "LOCO4COCO_BOOTH"
# Keys to copy from the source connection into the booth connection.
COPY_KEYS = ("account", "user", "role", "warehouse")


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def generate_key(name):
    """Unencrypted PKCS#8 private key plus its base64 public body.

    Unencrypted is deliberate. A passphrase would reintroduce exactly the prompt
    this exists to remove, and the booth has to run unattended on a stand.
    """
    KEYDIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", name).lower()
    priv = KEYDIR / f"{safe}_rsa_key.p8"
    if priv.exists():
        print(f"   reusing existing key {priv}")
    else:
        r = sh(["openssl", "genrsa", "2048"])
        if r.returncode:
            sys.exit(f"openssl genrsa failed: {r.stderr[:300]}")
        r2 = subprocess.run(
            ["openssl", "pkcs8", "-topk8", "-inform", "PEM", "-outform", "PEM",
             "-nocrypt"], input=r.stdout, capture_output=True, text=True)
        if r2.returncode:
            sys.exit(f"openssl pkcs8 failed: {r2.stderr[:300]}")
        priv.write_text(r2.stdout)
        priv.chmod(0o600)
        print(f"   wrote {priv} (0600)")
    r3 = sh(["openssl", "rsa", "-in", str(priv), "-pubout"])
    if r3.returncode:
        sys.exit(f"openssl rsa -pubout failed: {r3.stderr[:300]}")
    body = "".join(l.strip() for l in r3.stdout.splitlines()
                   if "-----" not in l)
    return priv, body


def append_booth_connection(text, src_conf, priv):
    """Append a LOCO4COCO_BOOTH block to connections.toml.

    If the block already exists, replace it. The source connection is left
    untouched so Cortex Code can keep managing it.
    """
    # Remove existing booth block if present.
    pat = re.compile(rf'^\[{re.escape(BOOTH_CONN)}\]\s*$', re.M)
    m = pat.search(text)
    if m:
        start = m.start()
        nxt = re.search(r'^\[', text[m.end():], re.M)
        end = m.end() + (nxt.start() if nxt else len(text[m.end():]))
        text = text[:start].rstrip("\n") + "\n" + text[end:].lstrip("\n")

    # Build the new block from the source connection's identity fields.
    lines = [f"\n[{BOOTH_CONN}]"]
    for key in COPY_KEYS:
        val = src_conf.get(key)
        if val:
            lines.append(f'{key} = "{val}"')
    lines.append('authenticator = "SNOWFLAKE_JWT"')
    lines.append(f'private_key_file = "{priv}"')
    lines.append(f'private_key_path = "{priv}"')

    return text.rstrip("\n") + "\n" + "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--connection", "-c", required=True,
                    help="the operator's connection from step 0; left untouched")
    # Registering a public key needs an authenticated session, and if the
    # connection being converted is the OAuth one that costs a prompt. --via lets
    # you borrow a connection on the same account that does not prompt.
    ap.add_argument("--via", default=None,
                    help="authenticate the key registration through this connection instead")
    a = ap.parse_args()

    if not TOML.exists():
        sys.exit(f"no {TOML}")
    conf = tomllib.loads(TOML.read_text())
    src = conf.get(a.connection)
    if not isinstance(src, dict):
        sys.exit(f"connection {a.connection} not found in {TOML}. "
                 f"Known: {', '.join(k for k, v in conf.items() if isinstance(v, dict))}")

    # If booth connection already exists and works, skip.
    booth = conf.get(BOOTH_CONN)
    if (isinstance(booth, dict)
            and "snowflake_jwt" in str(booth.get("authenticator") or "").lower()
            and booth.get("private_key_file")):
        print(f"[{BOOTH_CONN}] already exists with key-pair auth - nothing to do.")
        return 0

    print(f"1. generating a key for {a.connection}")
    priv, pub_body = generate_key(a.connection)

    via = a.via or a.connection
    print(f"2. registering the public key on the account user (via {via})")
    import snowflake.connector as sc
    cn = sc.connect(connection_name=a.via or a.connection)
    cur = cn.cursor()
    cur.execute("SELECT CURRENT_USER(), CURRENT_ACCOUNT(), CURRENT_ROLE()")
    user, acct, role = cur.fetchone()
    cur.execute(f"ALTER USER {user} SET RSA_PUBLIC_KEY='{pub_body}'")
    print(f"   set on {user} (account {acct}, role {role})")
    cur.close()
    cn.close()

    print(f"3. creating [{BOOTH_CONN}] alongside [{a.connection}]")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = TOML.with_suffix(f".toml.bak-{stamp}")
    shutil.copy2(TOML, backup)
    TOML.write_text(append_booth_connection(TOML.read_text(), src, priv))
    print(f"   [{BOOTH_CONN}] added; [{a.connection}] left untouched")
    print(f"   backup at {backup.name}")

    print(f"4. verifying {BOOTH_CONN} with no keychain and no browser in the path")
    cn2 = sc.connect(connection_name=BOOTH_CONN)
    c2 = cn2.cursor()
    c2.execute("SELECT CURRENT_USER(), CURRENT_ACCOUNT(), CURRENT_REGION()")
    print(f"   connected as {c2.fetchone()}")
    c2.close()
    cn2.close()

    print(f"\nDone. The game uses [{BOOTH_CONN}] (key-pair, no prompts).")
    print(f"[{a.connection}] is untouched - Cortex Code keeps managing it.")
    print(f"bootstrap.py will write {BOOTH_CONN} into game/config.json automatically.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
