"""Refuse to ship a personal Snowflake connection in game/config.json.

The postbox stages the visitor's .docx with `snow stage copy -c <name>` and
presigns it, reading the name from snowflake.connection_name. When a real,
personal connection was committed there (it shipped as "Frankfurt_L4C", a HOL
account that later expired), every fresh clone that did not re-run bootstrap end
to end failed at the postbox with "JWT token is invalid" - in front of a visitor.

So the repo ships the neutral placeholder MYBOOTH; bootstrap.py rewrites it to
the operator's own connection locally, and that local value is kept out of git
with `git update-index --skip-worktree game/config.json`. This gate enforces the
invariant on what would actually be COMMITTED (the index, falling back to HEAD),
so a local skip-worktree'd real value does not trip it, but a staged personal
value does.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLACEHOLDER = "MYBOOTH"
REL = "game/config.json"


def committed_config():
    """The config.json content that would be committed: index first, then HEAD.

    Reads via git so a skip-worktree'd working copy (the operator's real, local
    connection) is ignored - we only judge what git would actually record.
    """
    for ref in (f":{REL}", f"HEAD:{REL}"):
        r = subprocess.run(["git", "show", ref], cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout), ref
    # Not in git yet (e.g. a brand-new checkout mid-rebase): fall back to disk.
    return json.loads((ROOT / REL).read_text()), "working-tree"


def main():
    try:
        cfg, src = committed_config()
    except Exception as e:                                        # noqa: BLE001
        print(f"FAIL - could not read {REL}: {e}")
        return 1

    name = (cfg.get("snowflake") or {}).get("connection_name")
    print(f"checked {REL} from {src}: connection_name={name!r}")
    if name == PLACEHOLDER:
        print(f"PASS - committed connection_name is the placeholder {PLACEHOLDER!r}")
        return 0

    print(f"FAIL - committed connection_name is {name!r}, not the placeholder "
          f"{PLACEHOLDER!r}.")
    print("       A personal/stale connection here is the postbox failure mode.")
    print("       Fix before committing:")
    print(f"         python3 -c \"import json,io;"
          f"p='{REL}';c=json.load(open(p));"
          f"c['snowflake']['connection_name']='{PLACEHOLDER}';"
          f"json.dump(c,open(p,'w'),indent=2)\"")
    print("       Keep your real connection local, uncommitted:")
    print(f"         git update-index --skip-worktree {REL}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
