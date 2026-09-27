#!/usr/bin/env python3
"""Fresh-laptop gate: prove `snow` resolves even when it is NOT on PATH.

Why this exists: on a genuinely new machine `pip install snowflake-cli` drops the
`snow` binary next to the python that ran pip (e.g. a macOS framework bin/), which
is NOT on the default shell PATH. Every check we had ran in an already-provisioned
shell where snow happened to be on PATH, so a resolver that only *warned* via
shutil.which (PATH-only) looked fine and shipped anyway. This gate removes PATH
from under the resolvers and asserts each one still returns a real, runnable path.

Seamless contract: if snow is genuinely not installed ANYWHERE we can detect, this
is an un-provisioned box, not a regression -> we SKIP (info), we do not hard-fail.
The failure we care about is: snow IS installed off-PATH but a resolver returns the
bare name "snow" (which would blow up at runtime on the fresh laptop).
"""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "game"))
sys.path.insert(0, os.path.join(ROOT, "deploy"))


def _load_resolvers():
    """Import the three independent snow resolvers. Returns list of (label, fn)."""
    resolvers = []
    from context import _snow_binary  # game/context.py (reads config, no arg)
    resolvers.append(("context._snow_binary", lambda: _snow_binary()))
    from server import snow_bin as server_snow_bin  # game/server.py (takes cfg)
    resolvers.append(("server.snow_bin", lambda: server_snow_bin({})))
    from snowcli import snow_bin as setup_snow_bin  # deploy/snowcli.py (no arg)
    resolvers.append(("deploy/snowcli.snow_bin", lambda: setup_snow_bin()))
    return resolvers


def _snow_installed_anywhere():
    """Is snow findable at all, ignoring PATH gaps? Checks PATH + the two off-PATH
    spots pip uses (beside the running python, and the sysconfig scripts dir)."""
    if shutil.which("snow"):
        return True
    cands = [os.path.join(os.path.dirname(sys.executable), "snow")]
    try:
        import sysconfig
        sp = sysconfig.get_path("scripts")
        if sp:
            cands.append(os.path.join(sp, "snow"))
    except Exception:
        pass
    cands.append(os.path.expanduser("~/.local/bin/snow"))
    return any(os.path.exists(c) for c in cands)


def main():
    installed = _snow_installed_anywhere()
    original_path = os.environ.get("PATH", "")
    empty = tempfile.mkdtemp(prefix="no-snow-")
    problems = []
    results = []

    # Clear the resolver caches if already warm, then strip PATH so shutil.which
    # returns None and only the off-PATH heuristics can succeed.
    os.environ["PATH"] = empty
    try:
        resolvers = _load_resolvers()
        # Reset any module-level caches so the stripped PATH actually takes effect.
        try:
            import server as _srv
            if hasattr(_srv, "_SNOW_BIN"):
                _srv._SNOW_BIN["path"] = None
        except Exception:
            pass
        try:
            import snowcli as _sc
            if hasattr(_sc, "_CACHE"):
                _sc._CACHE.clear()
        except Exception:
            pass

        for label, fn in resolvers:
            try:
                got = fn()
            except Exception as e:
                got = None
                problems.append(f"{label}: raised {type(e).__name__}: {e}")
                results.append((label, "ERROR"))
                continue
            ok = bool(got) and os.path.isabs(got) and os.path.exists(got)
            results.append((label, got))
            if installed and not ok:
                problems.append(
                    f"{label}: returned {got!r} with PATH stripped, but snow IS "
                    f"installed off-PATH -> would fail on a fresh laptop"
                )
    finally:
        os.environ["PATH"] = original_path
        try:
            os.rmdir(empty)
        except Exception:
            pass

    print("Fresh-env snow resolution (PATH stripped):")
    for label, got in results:
        print(f"  {label:28s} -> {got}")

    if not installed:
        print(
            "\nInfo (not a problem): snow is not installed anywhere detectable on "
            "this machine, so this is an un-provisioned box. Skipping the strict "
            "check. On a set-up laptop `pip install snowflake-cli` puts snow beside "
            "python and the resolvers will find it."
        )
        return 0

    if problems:
        print("\nFAIL: snow would not resolve on a fresh (off-PATH) laptop:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print("\nPASS: every resolver finds snow with PATH stripped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
