#!/usr/bin/env python3
"""Flatten game/decision_tree.md into plain text for the Google Doc copy.

The decision tree is published in two places: game/decision_tree.md in the repo,
and a Google Doc that people actually read on a phone at the stand. The Doc kept
drifting because it was hand-patched, so this script exists to make the Doc a
render of the markdown rather than a second copy of it.

Markdown tables become bullet lists on purpose: the Doc is read on a phone as
often as on a laptop, and a six-column table is unreadable there.

    python3 scripts/publish_decision_tree.py > /tmp/dt.txt

Then replace the Google Doc body with that text. There is no API call here
deliberately - pushing it needs Google credentials this repo does not hold, and
an SE regenerating the tree should not need them to see the output.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "game", "decision_tree.md")


def strip_inline(s):
    """Remove markdown emphasis and code ticks, keep the words."""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    # _italics_ too, but only when the underscores wrap the whole run - snake_case
    # identifiers like is_ready_for_import must survive untouched.
    s = re.sub(r"(?<![\w])_([^_]+)_(?![\w])", r"\1", s)
    s = s.replace("`", "")
    # A whole line wrapped in underscores is an italic caption. The general regex
    # above cannot handle it, because the run often contains snake_case names.
    if len(s) > 2 and s.startswith("_") and s.endswith("_"):
        s = s[1:-1].strip()
    # [text](url) -> text (url), because a bare URL in a phone-read doc is noise
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", s)
    return s.strip()


def flatten(md):
    out, table = [], []

    def flush_table():
        """Emit a markdown table as 'header: value' bullets, one per row."""
        if not table:
            return
        rows = [[c.strip() for c in r.strip().strip("|").split("|")]
                for r in table]
        table.clear()
        if len(rows) < 2:
            return
        head = rows[0]
        body = [r for r in rows[1:]
                if not all(set(c) <= set("-: ") for c in r)]
        for r in body:
            parts = []
            for i, cell in enumerate(r):
                if not cell:
                    continue
                label = strip_inline(head[i]) if i < len(head) else ""
                cell = strip_inline(cell)
                if not cell or cell == "-":
                    continue
                parts.append(f"{label}: {cell}" if label else cell)
            if parts:
                out.append("\u2022  " + " \u00b7 ".join(parts))

    for raw in md.splitlines():
        line = raw.rstrip()
        if line.lstrip().startswith("|"):
            table.append(line)
            continue
        flush_table()
        if not line.strip():
            out.append("")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            text = strip_inline(m.group(2))
            out.append("")
            # Headings become upper case rather than styled: the insert is plain
            # text, so this is the only way structure survives.
            out.append(text.upper() if len(m.group(1)) <= 2 else text)
            continue
        if re.match(r"^\s*[-*]\s+", line):
            out.append("\u2022  " + strip_inline(re.sub(r"^\s*[-*]\s+", "", line)))
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            out.append(strip_inline(line.strip()))
            continue
        out.append(strip_inline(line))

    flush_table()

    # Collapse runs of blank lines, which the heading rule above creates.
    tidy, blank = [], False
    for l in out:
        if not l.strip():
            if blank:
                continue
            blank = True
        else:
            blank = False
        tidy.append(l)
    return "\n".join(tidy).strip() + "\n"


def main():
    if not os.path.exists(SRC):
        sys.exit("No decision_tree.md. Run: python3 game/decision_tree.py")
    text = flatten(open(SRC, encoding="utf-8").read())
    sys.stdout.write(text)
    sys.stderr.write("\n%d chars, %d lines\n"
                     % (len(text), text.count("\n")))


if __name__ == "__main__":
    main()
