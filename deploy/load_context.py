#!/usr/bin/env python3
"""Load the booth's shared context from the repo markdown into Snowflake.

The markdown under skills/loco4coco/references/ is the source of truth. This
script parses it and replaces the contents of the LISTINGS, GUIDES, FEATURES,
ARCHETYPES and ROUTES tables, then records provenance in CONTEXT_MANIFEST.

Why the tables exist at all: another SE, or Paris, needs the same closed lists
without pulling a git branch. A borrowed booth laptop is not guaranteed to have
MCP available (managed settings can disable user and plugin servers) but it is
guaranteed to have a Snowflake connection, because nothing works without one.
So the shareable unit is a table, and sharing is an ordinary secure share.

The server reads these at boot and falls back to the markdown on any failure,
so a stale or empty table degrades the booth, it never breaks it.

Usage:
    python3 deploy/load_context.py --connection <your-connection>
    python3 deploy/load_context.py --check         # parse and report, no writes
    python3 deploy/load_context.py --connection X  # a different account

Run this after any edit to the reference markdown, and before sharing.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REFS = os.path.join(ROOT, "skills", "loco4coco", "references")
GAME = os.path.join(ROOT, "game")

DB = "LOCO4COCO"
SCHEMA = "BOOTH"


# --------------------------------------------------------------------- parsing
# These parsers deliberately mirror the ones in game/server.py rather than
# importing them: server.py binds a config, a state file and a lock at import
# time, and this script must run without a booth server on the machine. The
# duplication is checked by --check, which prints the row counts the server
# should agree with, and by the parity test in the persona suite.

def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_listings():
    """marketplace-index.md -> [(industry, ordinal, title, provider, access,
    global_name, regions, url)]"""
    text = _read(os.path.join(REFS, "marketplace-index.md"))
    row_re = re.compile(r"^\|\s*\[(?P<title>.+?)\]\((?P<url>[^)]+)\)\s*\|"
                        r"\s*(?P<prov>[^|]+?)\s*\|\s*(?P<acc>[^|]+?)\s*\|"
                        r"\s*`(?P<gname>[^`]+)`\s*\|\s*(?P<regs>[^|]*)\|")
    out, current, n = [], None, 0
    for line in text.splitlines():
        h = re.match(r"^##\s+([a-z_]+)\s*$", line.strip())
        if h:
            current, n = h.group(1), 0
            continue
        if not current:
            continue
        m = row_re.match(line.strip())
        if m:
            n += 1
            out.append((current, n, m.group("title").strip(),
                        m.group("prov").strip(), m.group("acc").strip(),
                        m.group("gname").strip(), m.group("regs").strip(),
                        m.group("url").strip()))
    return out


def parse_guides():
    """guides-index.md -> [(archetype, title, slug, is_primary)]

    Unlike the server, which keeps only the primary fork, this keeps the
    alternates too. They cost nothing to store and a future refine step may
    want them.
    """
    text = _read(os.path.join(REFS, "guides-index.md"))
    out, current = [], None
    for line in text.splitlines():
        m = re.match(r"^##\s+\d+\.\s+(\S+)", line)
        if m:
            current = m.group(1).strip()
            continue
        if current and line.startswith("|") and "`" in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            slug = cells[1].strip("` ")
            note = cells[2] if len(cells) > 2 else ""
            if not slug or slug.startswith("-"):
                continue
            out.append((current, cells[0], slug, "Primary fork" in note))
    return out


def parse_features():
    """feature-docs.md -> [(name, docs_url)]"""
    text = _read(os.path.join(REFS, "feature-docs.md"))
    out = []
    for line in text.splitlines():
        if not line.startswith("|") or "https://" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[1].startswith("https://"):
            out.append((cells[0], cells[1]))
    return out


def parse_archetypes():
    """poc-archetypes.md -> [(id, ordinal, friendly, what, features, fork,
    needs, prompt)]"""
    text = _read(os.path.join(REFS, "poc-archetypes.md"))
    # Each archetype is a "## <n>. <id>" heading followed by an **ID** line and
    # a bullet list. Split on the headings so a missing bullet yields "" rather
    # than silently borrowing the next archetype's value.
    chunks = re.split(r"^##\s+(\d+)\.\s+(\S+)\s*$", text, flags=re.M)
    out = []
    for i in range(1, len(chunks) - 1, 3):
        ordinal, aid, body = int(chunks[i]), chunks[i + 1].strip(), chunks[i + 2]

        def bullet(label):
            m = re.search(r"^-\s+\*\*" + label + r":?\*\*\s*(.+?)\s*$",
                          body, flags=re.M)
            return m.group(1).strip() if m else ""

        friendly = ""
        fm = re.search(r'\*\*Friendly\*\*\s*"([^"]+)"', body)
        if fm:
            friendly = fm.group(1).strip()
        fork = bullet("Fork").strip("` ")
        # The pain bullet is what makes keyword retrieval work at all. A visitor
        # says "we retype invoices all day"; that shares no words with
        # AI_EXTRACT, but it shares plenty with the pain text. The archetype is
        # the bridge from their language to ours.
        out.append((aid, ordinal, friendly, bullet("Visitor pain"),
                    bullet("What gets built"), bullet("Features"), fork,
                    bullet("Needs from them"), bullet("Prompt skeleton")))
    return out


def parse_routes():
    """INTEGRATION_PATHS in game/server.py -> [(platform, guidance, docs_url)]

    Read by AST rather than imported, because importing server.py starts its
    config and state machinery. The dict is a literal, so this is exact.
    """
    import ast
    src = _read(os.path.join(GAME, "server.py"))
    tree = ast.parse(src)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "INTEGRATION_PATHS" not in names:
            continue
        d = ast.literal_eval(node.value)
        return [(k, v[0], v[1]) for k, v in d.items()]
    return []


# --------------------------------------------------------------- canonical names
# poc-archetypes.md writes its "Features:" bullets as prose - "semantic views",
# "Streamlit", "anomaly detection" - while feature-docs.md is the closed list the
# Workshop actually clamps against. Nothing is broken at runtime, because the
# server sends the model the feature list from feature-docs.md and never these
# bullets. But the ARCHETYPES table is meant to be the *shared* guardrail, so it
# stores canonical spellings; otherwise the first person to wire these into
# rendering silently loses half of them.
#
# Case differences resolve automatically. This map covers only wording
# differences, and only where the intent is unambiguous.
FEATURE_ALIASES = {
    "streamlit": "Streamlit in Snowflake",
    "anomaly detection": "ML Anomaly Detection",
    "internal marketplace": "Snowflake Marketplace",
    "listings": "Snowflake Marketplace",
}


def canonical_features(raw, feat_names):
    """Return (canonical list, unresolved list) for one archetype's bullet.

    Unresolved names are reported, not dropped silently and not guessed at: a
    feature genuinely missing from feature-docs.md is a content decision for a
    human, not something a loader should invent a link for.
    """
    lower = {n.lower(): n for n in feat_names}
    good, bad = [], []
    for f in [x.strip() for x in (raw or "").split(",") if x.strip()]:
        hit = lower.get(f.lower()) or lower.get(
            FEATURE_ALIASES.get(f.lower(), "").lower())
        (good if hit else bad).append(hit or f)
    return good, bad


# ---------------------------------------------------------------------- loading

def sql_lit(v):
    """Quote a value for inline SQL. Everything here is repo content we wrote,
    but escaping is not optional just because the input is trusted today."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("\\", "\\\\").replace("'", "''") + "'"


def run_sql(conn, statements, dry=False):
    """Run statements through the Snowflake CLI, which already holds the auth the
    rest of deploy/ uses. Avoids adding a Python connector dependency to a laptop
    that only needs to run one file.

    Written to a temp file rather than passed with -q: this is a few hundred
    statements carrying prose, which is well past a comfortable argv length.

    Templating is switched off explicitly. The reference markdown contains `&`
    and angle-bracket placeholders like `<their tables>`, which snow sql would
    otherwise try to resolve as variables and fail on with "SQL rendering error".
    """
    joined = ";\n".join(statements) + ";"
    if dry:
        print(joined[:2000])
        return True
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".sql", prefix="loco_context_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(joined)
        cmd = ["snow", "sql", "-f", path, "--enable-templating", "NONE"]
        if conn:
            cmd += ["-c", conn]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        if p.returncode != 0:
            sys.stderr.write((p.stderr or p.stdout or "")[-3000:] + "\n")
            return False
        return True
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def insert_batches(table, cols, rows, batch=200):
    """DELETE then INSERT, one statement per batch. Not a MERGE: these are
    closed lists where the file is the whole truth, so replace is the correct
    semantic - a listing removed from the markdown must disappear here too."""
    stmts = ["DELETE FROM {}.{}.{}".format(DB, SCHEMA, table)]
    collist = ", ".join(cols)
    for i in range(0, len(rows), batch):
        vals = ", ".join(
            "(" + ", ".join(sql_lit(c) for c in r) + ")"
            for r in rows[i:i + batch])
        stmts.append("INSERT INTO {}.{}.{} ({}) VALUES {}".format(
            DB, SCHEMA, table, collist, vals))
    return stmts


def git_ref():
    try:
        p = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=10)
        return p.stdout.strip() if p.returncode == 0 else ""
    except Exception:
        return ""


def sha_of(rel):
    path = os.path.join(ROOT, rel)
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()
    except OSError:
        return ""


def _configured_connection():
    """Default to the connection the game is configured with (bootstrap sets it),
    so a fresh setup loads context into the right account. Falls back to
    $LOCO_CONNECTION, then None (snow's own default)."""
    try:
        cfg_path = os.path.join(os.path.dirname(__file__), "..", "game", "config.json")
        with open(cfg_path) as f:
            c = (json.load(f).get("snowflake") or {}).get("connection_name")
        if c:
            return c
    except Exception:                                            # noqa: BLE001
        pass
    return os.environ.get("LOCO_CONNECTION")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--connection", default=_configured_connection())
    ap.add_argument("--check", action="store_true",
                    help="Parse and report counts without writing")
    ap.add_argument("--print-sql", action="store_true",
                    help="Print the SQL instead of running it")
    args = ap.parse_args()

    specs = [
        ("LISTINGS", "skills/loco4coco/references/marketplace-index.md",
         ["INDUSTRY", "ORDINAL", "TITLE", "PROVIDER", "ACCESS", "GLOBAL_NAME",
          "REGIONS", "URL"], parse_listings),
        ("GUIDES", "skills/loco4coco/references/guides-index.md",
         ["ARCHETYPE", "TITLE", "SLUG", "IS_PRIMARY"], parse_guides),
        ("FEATURES", "skills/loco4coco/references/feature-docs.md",
         ["NAME", "DOCS_URL"], parse_features),
        ("ARCHETYPES", "skills/loco4coco/references/poc-archetypes.md",
         ["ID", "ORDINAL", "FRIENDLY", "VISITOR_PAIN", "WHAT_GETS_BUILT",
          "FEATURES", "FORK_SLUG", "NEEDS_FROM_THEM", "PROMPT_SKELETON"],
         parse_archetypes),
        ("ROUTES", "game/server.py",
         ["PLATFORM", "GUIDANCE", "DOCS_URL"], parse_routes),
    ]

    parsed, problems = {}, []
    for table, src, cols, fn in specs:
        try:
            rows = fn()
        except Exception as e:
            problems.append("{}: parse failed: {}".format(table, e))
            rows = []
        parsed[table] = rows
        print("{:<12} {:>4} rows  <- {}".format(table, len(rows), src))
        if not rows:
            problems.append("{}: parsed 0 rows".format(table))

    # A blueprint may only name a feature from the closed list. Canonicalise the
    # archetype bullets against it so the shared table carries exact spellings,
    # and surface anything genuinely absent as a warning - it does not block the
    # load, because the runtime path never reads these bullets.
    feat_names = {n for n, _ in parsed.get("FEATURES", [])}
    warnings = []
    if feat_names:
        fixed = []
        for row in parsed.get("ARCHETYPES", []):
            row = list(row)
            good, bad = canonical_features(row[5], feat_names)
            row[5] = ", ".join(good)
            for f in bad:
                warnings.append(
                    "ARCHETYPES {}: feature {!r} is not in feature-docs.md - "
                    "dropped from the shared table".format(row[0], f))
            fixed.append(tuple(row))
        parsed["ARCHETYPES"] = fixed

    if problems:
        print("\nProblems:")
        for p in problems:
            print("  - " + p)
    if warnings:
        print("\nWarnings (load proceeds):")
        for w in warnings:
            print("  - " + w)

    if args.check:
        return 1 if problems else 0

    stmts, manifest = [], []
    ref, who = git_ref(), os.environ.get("USER", "")
    for table, src, cols, _ in specs:
        rows = parsed[table]
        if not rows:
            print("skipping {} - refusing to empty a table from a failed parse"
                  .format(table))
            continue
        stmts += insert_batches(table, cols, rows)
        manifest.append((src, table, sha_of(src), len(rows), who, ref))

    stmts.append("DELETE FROM {}.{}.CONTEXT_MANIFEST".format(DB, SCHEMA))
    vals = ", ".join(
        "({}, {}, {}, {}, CURRENT_TIMESTAMP(), {}, {})".format(
            sql_lit(s), sql_lit(t), sql_lit(h), n, sql_lit(u), sql_lit(g))
        for s, t, h, n, u, g in manifest)
    stmts.append(
        "INSERT INTO {}.{}.CONTEXT_MANIFEST (SOURCE_FILE, TARGET_TABLE, "
        "CONTENT_SHA, ROW_COUNT, LOADED_AT, LOADED_BY, GIT_REF) "
        "SELECT * FROM VALUES {}".format(DB, SCHEMA, vals))

    ok = run_sql(args.connection, stmts, dry=args.print_sql)
    if not args.print_sql:
        print("\n" + ("loaded" if ok else "LOAD FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
