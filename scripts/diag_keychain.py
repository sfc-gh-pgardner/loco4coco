"""What in this repo touches the macOS keychain, and how often.

The keychain item is `com.snowflake.connector.python` - the Python connector's
temporary-credential (SSO token) cache. It is read on EVERY new process that
calls connect() while client_store_temporary_credential is on, which is why the
count tracks process spawns, not query counts.
"""
import pathlib
import tomllib

p = pathlib.Path.home() / ".snowflake" / "connections.toml"
d = tomllib.loads(p.read_text())

print("=== connections: which ones use the keychain ===")
for name, c in d.items():
    auth = str(c.get("authenticator") or "(default: password)")
    store = c.get("client_store_temporary_credential")
    has_key = bool(c.get("private_key_file") or c.get("private_key"))
    has_pw = bool(c.get("password"))
    # The keychain cache is only used for browser/OAuth style auth.
    browsery = any(t in auth.lower() for t in ("oauth", "externalbrowser", "sso"))
    uses = "KEYCHAIN" if (browsery and store is not False) else "no keychain"
    print(f"  {name:16} auth={auth:26} store_temp={store!s:5} "
          f"keyfile={has_key!s:5} pw={has_pw!s:5} -> {uses}")
