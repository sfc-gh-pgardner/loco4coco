#!/usr/bin/env python3
"""Check the curated marketplace index against the live Snowflake catalogue.

The curated index is the booth-safe fallback, so it must not offer listings the
visitor cannot actually attach. It was verified by hand on 2026-08-05 and has
drifted since: "Snowflake Public Data: Core Weather Data" is not importable in
AWS_EU_WEST_2 but is still listed.

    python3 scripts/verify_marketplace_index.py
    python3 scripts/verify_marketplace_index.py --region AWS_US_WEST_2

Read-only. Reports, changes nothing.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "game"))

import server as S                                          # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default=None,
                    help="override event.region, e.g. AWS_US_WEST_2")
    args = ap.parse_args()

    cfg = S.load_config()
    if args.region:
        cfg.setdefault("event", {})["region"] = args.region
    region = S.region_short(cfg)

    live, err = S.refresh_live_listings(cfg, force=True)
    if not live:
        print(f"could not read the live catalogue: {err}")
        return 2
    importable = {r["global_name"] for r in live}
    by_title = {(r["title"] or "").strip().lower(): r for r in live}
    print(f"region {region}: {len(live)} listings importable\n")

    market = S.load_marketplace()
    seen, stale, ok = set(), [], 0
    for industry, rows in market.items():
        for r in rows:
            gn, title = r.get("global_name", ""), (r.get("title") or "").strip()
            if gn in seen:
                continue
            seen.add(gn)
            if gn in importable:
                ok += 1
                continue
            # A renamed listing keeps its title but changes global_name, so try
            # the title before calling it stale.
            match = by_title.get(title.lower())
            stale.append((industry, title, gn,
                          f"renamed? live global_name is {match['global_name']}"
                          if match else "not importable in this region"))

    print(f"{ok} of {len(seen)} curated listings are importable in {region}")
    if not stale:
        print("no stale entries")
        return 0
    print(f"\n{len(stale)} need attention:")
    for industry, title, gn, why in stale:
        print(f"  [{industry:<14}] {title[:46]:<46} {gn:<14} {why}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
