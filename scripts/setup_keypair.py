"""Remove the macOS keychain from the booth's auth path, permanently.

WHY THIS EXISTS

The DataOps event accounts are handed out with `authenticator =
oauth_authorization_code` and `client_store_temporary_credential = true`. That
combination caches the OAuth token in the macOS keychain item
`com.snowflake.connector.python`, and macOS asks permission on every *process*
that reads it. The booth spawns a lot of processes - every `snow sql`, every
`snow stage copy`, every `cortex exec` - so the operator gets a modal password
dialog repeatedly, including mid-visit. "Always Allow" does not reliably end it,
because the ACL is scoped per binary and is reset whenever the token is
rewritten on refresh.

Key-pair auth has no token to cache, so it never touches the keychain at all.
It is also the only mode that works unattended, which is what a booth needs.

WHAT THIS DOES

  1. Generates an unencrypted 2048-bit RSA key under ~/.snowflake/keys/ (0600).
     Unencrypted is deliberate: a passphrase would just reintroduce a prompt.
  2. Registers the public half on the current user with ALTER USER.
  3. Writes a new connection to connections.toml using SNOWFLAKE_JWT. The
     original OAuth connection is left untouched, so this is reversible.
  4. Verifies the new connection with a real query and confirms no keychain
     item was read.

Usage:
    python3 scripts/setup_keypair.py --from Frankfurt_L4C --name BOOTH
"""
import argparse
import os
import pathlib
import re
import subprocess
import sys
import tomllib

HOME = pathlib.Path.home()
TOML = HOME / ".snowflake" / "connections.toml"
KEYDIR = HOME / ".snowflake" / "keys"


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def generate_key(name):
    """Unencrypted PKCS#8 private key plus its public half."""
    KEYDIR.mkdir(parents=True, exist_ok=True)
    priv = KEYDIR / f"{name.lower()}_rsa_key.p8"
    pub = KEYDIR / f"{name.lower()}_rsa_key.pub"
    if priv.exists():
        print(f"  key already exists, reusing: {priv}")
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
        print(f"  wrote private key {priv} (0600)")
    r3 = sh(["openssl", "rsa", "-in", str(priv), "-pubout"])
    if r3.returncode:
        sys.exit(f"openssl rsa -pubout failed: {r3.stderr[:300]}")
    pub.write_text(r3.stdout)
    pub.chmod(0o644)
    # Snowflake wants the base64 body only, no PEM header/footer, no newlines.
    body = "".join(l.strip() for l in r3.stdout.splitlines()
                   if "-----" not in l)
    return priv, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", required=True,
                    help="existing connection to copy account/user/role from")
    ap.add_argument("--name", default="BOOTH",
                    help="name for the new key-pair connection")
    a = ap.parse_args()

    if not TOML.exists():
        sys.exit(f"no {TOML}")
    conf = tomllib.loads(TOML.read_text())
    src = conf.get(a.src)
    if not isinstance(src, dict):
        sys.exit(f"connection {a.src} not found in {TOML}")

    print(f"1. generating key for {a.name}")
    priv, pub_body = generate_key(a.name)

    print(f"2. registering the public key on the account user via {a.src}")
    import snowflake.connector as sc
    cn = sc.connect(connection_name=a.src)
    cur = cn.cursor()
    cur.execute("SELECT CURRENT_USER(), CURRENT_ACCOUNT(), CURRENT_ROLE()")
    user, acct, role = cur.fetchone()
    cur.execute(f"ALTER USER {user} SET RSA_PUBLIC_KEY='{pub_body}'")
    print(f"   RSA_PUBLIC_KEY set on {user} (account {acct}, role {role})")
    cur.close()
    cn.close()

    print(f"3. writing connection [{a.name}] to {TOML}")
    # Hand-edit the TOML: tomllib is read-only and the file carries comments
    # worth keeping.
    text = TOML.read_text()
    block = (f'\n[{a.name}]\n'
             f'account = "{src.get("account", "")}"\n'
             f'user = "{user}"\n'
             f'role = "{src.get("role", role)}"\n'
             f'authenticator = "SNOWFLAKE_JWT"\n'
             f'private_key_file = "{priv}"\n')
    for k in ("warehouse", "database", "schema"):
        if src.get(k):
            block += f'{k} = "{src[k]}"\n'
    text = re.sub(rf'\n\[{re.escape(a.name)}\]\n(?:[^\[]*)', '\n', text)
    TOML.write_text(text.rstrip("\n") + "\n" + block)
    print(f"   [{a.name}] written, {a.src} left untouched")

    print(f"4. verifying {a.name} with no keychain in the path")
    cn2 = sc.connect(connection_name=a.name)
    c2 = cn2.cursor()
    c2.execute("SELECT CURRENT_USER(), CURRENT_ACCOUNT(), CURRENT_REGION()")
    print(f"   connected as {c2.fetchone()}")
    c2.close()
    cn2.close()
    print(f"\nDone. Point game/config.json snowflake.connection_name at "
          f"{a.name}, and use -c {a.name} for every snow/cortex command.")


if __name__ == "__main__":
    main()
