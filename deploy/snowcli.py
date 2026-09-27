"""Resolve the `snow` CLI binary, robust to a fresh laptop where it is off PATH.

`pip install snowflake-cli` drops `snow` next to the python that ran pip, which on
macOS is the framework `bin/` directory - usually NOT on the default PATH. So a
setup script that calls bare "snow" (bootstrap, load_context, verify_context)
fails on a fresh laptop with "command not found", even though snow is installed.

This mirrors game/server.py's snow_bin() so setup and runtime resolve the CLI the
same way: PATH first, then beside the running python (where pip put it), then the
sysconfig scripts dir and ~/.local/bin, then the bare name as a last resort.
"""
import os
import shutil
import sys

_CACHE = {}


def snow_bin():
    """Absolute path to the snow CLI if we can find it, else the bare name."""
    if "path" in _CACHE:
        return _CACHE["path"]
    found = shutil.which("snow")
    if not found:
        cands = [os.path.join(os.path.dirname(sys.executable), "snow")]
        try:
            import sysconfig
            sp = sysconfig.get_path("scripts")
            if sp:
                cands.append(os.path.join(sp, "snow"))
        except Exception:                                         # noqa: BLE001
            pass
        cands.append(os.path.expanduser("~/.local/bin/snow"))
        found = next((c for c in cands if c and os.path.exists(c)), None)
    _CACHE["path"] = found or "snow"
    return _CACHE["path"]
