"""Convert the connection the operator already made onto key-pair auth, in place.

WHY IN PLACE

An earlier version of this created a second connection called BOOTH. That was
wrong. The operator already sets up a connection in step 0 against their assigned
DataOps account, Cortex Code is already pointed at it, and it is already selected
in the connection picker. Adding a second name meant a hardcoded value in config,
a name nobody recognised, and a picker that still had the OAuth connection
selected - so the browser prompts continued.

So this rewrites that one connection: same name, same account, same user, key-pair
instead of OAuth. Nothing downstream has to learn a new name, and the connection
already selected in the picker stops prompting.

WHY AT ALL

DataOps event accounts are handed out with `authenticator =
oauth_authorization_code` and `client_store_temporary_credential = true`. The
OAuth token is cached in the macOS keychain, so macOS asks permission once per
process - about 3 per visitor, ~312 over a hundred-visitor day - and when the
token expires the recovery path is a browser window. Key-pair auth has no token
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
# Keys that only make sense for a browser/OAuth flow and must not survive the
# conversion - leaving client_store_temporary_credential behind would keep the
# keychain in the path.
OAUTH_ONLY = ("client_store_temporary_credential", "token", "token_file_path",
              "oauth_client_id", "oauth_client_secret", "oauth_redirect_uri",
              "password")


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


def rewrite_block(text, name, priv):
    """Replace one connection's auth lines, leaving every other block alone."""
    pat = re.compile(rf'^\[{re.escape(name)}\]\s*$', re.M)
    m = pat.search(text)
    if not m:
        sys.exit(f"connection [{name}] not found in {TOML}")
    start = m.end()
    nxt = re.search(r'^\[', text[start:], re.M)
    end = start + (nxt.start() if nxt else len(text[start:]))
    block, kept = text[start:end], []
    for line in block.splitlines():
        s = line.strip()
        if not s:
            continue
        key = s.split("=", 1)[0].strip().lower()
        if key in OAUTH_ONLY or key in ("authenticator", "private_key_file",
                                        "private_key_path"):
            continue
        kept.append(line)
    kept.append('authenticator = "SNOWFLAKE_JWT"')
    kept.append(f'private_key_file = "{priv}"')
    return text[:start] + "\n" + "\n".join(kept) + "\n\n" + text[end:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--connection", "-c", required=True,
                    help="the connection you created in step 0; converted in place")
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

    auth = str(src.get("authenticator") or "password").lower()
    if not any(t in auth for t in BROWSERY) and src.get("private_key_file"):
        print(f"[{a.connection}] is already on key-pair auth - nothing to do.")
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

    print(f"3. converting [{a.connection}] to SNOWFLAKE_JWT, in place")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = TOML.with_suffix(f".toml.bak-{stamp}")
    shutil.copy2(TOML, backup)
    TOML.write_text(rewrite_block(TOML.read_text(), a.connection, priv))
    print(f"   {a.connection} now uses key-pair; backup at {backup.name}")

    print(f"4. verifying, with no keychain and no browser in the path")
    cn2 = sc.connect(connection_name=a.connection)
    c2 = cn2.cursor()
    c2.execute("SELECT CURRENT_USER(), CURRENT_ACCOUNT(), CURRENT_REGION()")
    print(f"   connected as {c2.fetchone()}")
    c2.close()
    cn2.close()

    print(f"\nDone. {a.connection} keeps its name, so Cortex Code, the connection "
          f"picker and game/config.json all keep working.")
    print("If Cortex Code is open, restart it so it picks up the change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
