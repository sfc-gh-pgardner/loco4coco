#!/usr/bin/env python3
"""Harvest and verify the Marketplace listings offered to visitors.

The game used to name only vague categories ("Population & demographics")
because inventing a listing or provider name is a defect. This produces the
honest alternative: real listings whose existence, region availability, provider
and access terms are all verified, bundled so the booth resolves them instantly.

    python3 scripts/build_marketplace_index.py             # verify
    python3 scripts/build_marketplace_index.py --write     # rewrite the index
    python3 scripts/build_marketplace_index.py --candidates weather

WHY PROVIDER NAMES ARE RECORDED RATHER THAN SCRAPED
---------------------------------------------------
`SHOW AVAILABLE LISTINGS` exposes `organization_profile_name` for only 137 of
4,256 listings, and the public listing page is a client-rendered React app - a
plain HTTP GET returns 66KB of HTML containing no provider name at all. The
names below were read from the rendered pages on the date in VERIFIED_ON and are
recorded as constants.

So this script verifies what SQL can prove - the listing exists, is not
by-request or discover-only, and which regions it is available in - and treats
the provider and access terms as human-verified values with a date attached. To
re-verify those, load the pages in a real browser again.

CURATION IS JUDGEMENT, VERIFICATION IS FACT. The industry groupings are
editorial and should be reviewed by an SE.
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
OUT = os.path.join(PLUGIN, "skills", "loco4coco", "references", "marketplace-index.md")
BASE = "https://app.snowflake.com/marketplace/listing/"
VERIFIED_ON = "2026-08-06"


def booth_defaults():
    """Read the connection and region from game/config.json.

    These used to be hardcoded to one person's account, which meant anyone else
    who cloned the repo and rebuilt the index silently pointed at the wrong
    account and filtered for the wrong region.
    """
    conn, region = None, None
    try:
        with open(os.path.join(PLUGIN, "game", "config.json"),
                  encoding="utf-8") as f:
            cfg = json.load(f)
        conn = ((cfg.get("snowflake") or {}).get("connection_name")) or None
        region = ((cfg.get("event") or {}).get("region")) or None
        if region:
            region = region.strip().split(".")[-1]
    except (OSError, json.JSONDecodeError):
        pass
    return conn, region

# global_name -> (provider, access, canonical path)
# Access is normalised from what the listing page shows. "Accepts MCD" means it
# is chargeable, so it is labelled Paid unless a trial makes it usable for free.
LISTINGS = {
    "GZSVZAJO3":      ("Jaywing", "Free",
                       "jaywing-uk-england-and-wales-only-census-2021-trial"),
    "GZSVZ1K7VF":     ("CACI Ltd", "Free",
                       "caci-ltd-acorn-geodemographic-segmentation-in-the-uk"),
    "GZSVZ1K7UA":     ("CACI Ltd", "Free",
                       "caci-ltd-paycheck-%E2%80%93-uk-household-income-estimates-at-postcode-level-sample-data"),
    "GZSVZ1K7UQ":     ("CACI Ltd", "Free",
                       "caci-ltd-address-spine-%E2%80%93-uk-address-level-property-information-sample-data"),
    "GZTDZJKVH3":     ("Met Office", "Free 14-day trial",
                       "met-office-uk-land-surface-observations"),
    "GZTDZJKVCM":     ("Met Office", "Free 14-day trial",
                       "met-office-global-spot-weather-forecasts"),
    "GZTDZJKVCU":     ("Met Office", "Free",
                       "met-office-national-severe-weather-warning-service"),
    "GZTDZJKVCY":     ("Met Office", "Free 14-day trial",
                       "met-office-postcode-sector-weather-forecasts"),
    "GZSTZ67BY9OQW":  ("Snowflake", "Free",
                       "snowflake-pubmed-biomedical-research-corpus"),
    "GZ2FRZQNY1":     ("Facts and Dimensions Ltd", "Free",
                       "facts-and-dimensions-ltd-uk-health-facts-and-dimensions-sample"),
    "GZSVZ1K7UU":     ("CACI Ltd", "Free", ""),
    "GZTSZ290BVCAO":  ("Snowflake Public Data Products", "Free 60-day trial",
                       "snowflake-public-data-products-snowflake-public-data-foreign-exchange-rates"),
    "GZTDZ7DJU9":     ("Turnleaf Analytics", "Free",
                       "turnleaf-analytics-inflation-forecasting-headline-core-cpi-by-country"),
    "GZ2FSZH8URW":    ("North Data GmbH", "Free 7-day trial",
                       "north-data-gmbh-company-data-uk-incl-guernsey-xl-dataset"),
    "GZSTZLT2II6":    ("IBISWorld", "Free",
                       "ibisworld-industry-classification-systems-naics-anzsic-isic-uk-sic-etc"),
    "GZT0ZI0XJ6Q":    ("CSRHub LLC", "Free 30-day trial",
                       "csrhub-llc-csrhub-esg-environment-social-governance-fast-start"),
    "GZTYZAPS3FP":    ("InSights", "Free", ""),
    "GZT0Z4CM1E9L4":  ("CARTO", "Free", "carto-carto-boundaries"),
    "GZT0Z4CM1E9KJ":  ("CARTO", "Free", "carto-overture-maps-transportation"),
    "GZT0Z4CM1E9NA":  ("CARTO", "Free", "carto-carto-analytics-toolbox"),
    "GZT0ZKUCHKL":    ("CARTO", "Free", ""),
    "GZTSZRC7HQ3":    ("CEIC Data", "Free", "ceic-data-ceic-commodities-data"),
    "GZSOZ71OJH":     ("Yes Energy", "Free", "yes-energy-yes-energy-sample-data"),
    "GZSVZ8MX1I":     ("Rystad Energy", "Free", ""),
    "GZSYZSRWU5":     ("Weather Solutions", "Free", ""),
    "GZTDZ1PNFO":     ("General Index", "Free Trial", ""),
    "GZ1MOZBWYYT":    ("Ordnance Survey", "Free", ""),
    "GZT0ZGCQ51RQ":   ("FactSet", "Free", ""),
    "GZT0ZPWB4J7":    ("Dun & Bradstreet", "Free", ""),
    "GZU6Z630VEJ0W":  ("Solid Data LLC", "Free 30-day trial", ""),
    "GZT1ZFQ0JE5":    ("Socialgist", "Free", ""),
    "GZSNZ4PHA6":     ("data.world, Inc", "Free", ""),
}

# Curated per industry. Keys match config.json industries.
# Deliberately excluded: Factori mobility data (GZT8Z4NUG5) - its page showed no
# access terms at all, and an unlabelled listing is a dead end for a visitor on
# a trial. Better to offer four we can describe than five we cannot.
#
# 2026-08-23: added a 6th, free-weighted pick per industry (agentic search,
# offline - see game/agentic-marketplace-enhancement.md Path D). Verified the
# same way as every entry above, PLUS one check this script was missing until
# today: "is_ready_for_import" - a listing can pass region/by-request/
# discover-only and still be genuinely unattachable if this is false.
#
# That check also caught PRE-EXISTING drift, not just new picks: five
# already-curated listings turned out not importable - "Snowflake Public
# Data: Core Weather Data" (used in manufacturing/media/other, and already
# flagged as drifted; that check now lives in deploy/verify_context.py --listings),
# "Carbon Footprint Data" (manufacturing/energy), "Coal Global Data"
# (energy), the OTT Market Analysis listing (media), and - notably -
# healthcare's one Paid listing, Element Data HCPCS, which was not just
# expensive but not actually attachable either. All five were dropped and
# replaced. healthcare is now 6-for-6 free. media and other are also 6-for-6
# free. manufacturing and energy are 5 free + 1 free-trial each (one
# genuinely relevant pick per industry had a stated trial rather than a
# permanent-free term - kept per the file's rule that stated terms are what
# matter, not zero cost).
CURATED = {
    "healthcare":    ["GZSVZAJO3", "GZSVZ1K7VF", "GZTDZJKVCY", "GZSTZ67BY9OQW",
                      "GZ2FRZQNY1", "GZSVZ1K7UU"],
    "financial":     ["GZTSZ290BVCAO", "GZTDZ7DJU9", "GZ2FSZH8URW",
                      "GZSTZLT2II6", "GZT0ZI0XJ6Q", "GZTYZAPS3FP"],
    "retail":        ["GZTDZJKVCY", "GZSVZ1K7VF", "GZSVZ1K7UA", "GZSVZAJO3",
                      "GZSTZLT2II6", "GZT0ZKUCHKL"],
    "public":        ["GZSVZAJO3", "GZSVZ1K7UQ", "GZT0Z4CM1E9L4", "GZTDZJKVH3",
                      "GZTDZJKVCU", "GZ1MOZBWYYT"],
    "manufacturing": ["GZTSZRC7HQ3", "GZ2FSZH8URW", "GZT0Z4CM1E9KJ",
                      "GZT0ZGCQ51RQ", "GZT0ZPWB4J7", "GZTDZJKVCM"],
    "energy":        ["GZTDZJKVCU", "GZTDZJKVH3", "GZSOZ71OJH", "GZSVZ8MX1I",
                      "GZSYZSRWU5", "GZTDZ1PNFO"],
    "media":         ["GZSVZ1K7VF", "GZSVZAJO3", "GZT0Z4CM1E9L4",
                      "GZT0ZKUCHKL", "GZT1ZFQ0JE5", "GZSNZ4PHA6"],
    "other":         ["GZSVZAJO3", "GZ2FSZH8URW", "GZT0Z4CM1E9L4",
                      "GZTSZ290BVCAO", "GZT0Z4CM1E9NA", "GZSVZ1K7VF"],
}


def show_listings(connection):
    cmd = ["snow", "sql", "-q", "SHOW AVAILABLE LISTINGS",
           "--format", "json", "-c", connection]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        sys.exit(f"SHOW AVAILABLE LISTINGS failed: {(r.stderr or r.stdout)[:300]}")
    rows = json.loads(r.stdout or "[]")
    return {str(x.get("global_name")): x for x in rows if isinstance(x, dict)}


def regions_of(row):
    regs = str(row.get("regions") or "")
    if regs.strip().upper() == "ALL":
        return ["ALL"]
    return sorted({r.split(".")[-1] for r in regs.split(",") if r.strip()})


def available_in(row, region):
    """"ALL" means literally every region, not a comma list to substring-match -
    a plain `in` check on the raw string missed this and wrongly failed
    universally-available listings (found 2026-08-23)."""
    regs = str(row.get("regions") or "")
    return regs.strip().upper() == "ALL" or region in regs


def url_for(g):
    prov, _acc, slug = LISTINGS[g]
    return BASE + g + ("/" + slug if slug else "")


def main():
    def_conn, def_region = booth_defaults()
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--candidates", help="search listings by keyword")
    ap.add_argument("--connection", "-c", default=def_conn,
                    help=f"snow CLI connection (default from game/config.json: {def_conn})")
    ap.add_argument("--region", default=def_region,
                    help=f"region to require, e.g. AWS_EU_WEST_2 (default from game/config.json: {def_region})")
    a = ap.parse_args()

    if not a.connection:
        sys.exit("No connection. Pass --connection, or set "
                 "snowflake.connection_name in game/config.json.")
    if not a.region:
        sys.exit("No region. Pass --region, or set event.region in "
                 "game/config.json.")
    print(f"Connection  : {a.connection}")
    print(f"Region      : {a.region}")

    print("Reading SHOW AVAILABLE LISTINGS...")
    catalog = show_listings(a.connection)
    print(f"  {len(catalog)} listings in the catalogue")

    if a.candidates:
        kw = a.candidates.lower()
        hits = [(g, r) for g, r in catalog.items()
                if kw in str(r.get("title")).lower()
                and available_in(r, a.region)]
        print(f"\n{len(hits)} London-available listings matching {kw!r}:")
        for g, r in sorted(hits, key=lambda x: str(x[1].get("title"))):
            print(f"  {str(r.get('title'))[:62]:64} {g}")
        return 0

    wanted = sorted({g for lst in CURATED.values() for g in lst})
    print(f"\nVerifying {len(wanted)} curated listings "
          f"({sum(len(v) for v in CURATED.values())} industry slots)\n")

    problems = []
    for g in wanted:
        if g not in LISTINGS:
            problems.append((g, "no recorded provider - re-run the browser pass"))
            continue
        row = catalog.get(g)
        if not row:
            problems.append((g, "not in SHOW AVAILABLE LISTINGS any more"))
            continue
        if str(row.get("is_by_request")).lower() == "true":
            problems.append((g, "now by-request only"))
        if str(row.get("discover_only")).lower() == "true":
            problems.append((g, "now discover-only"))
        # is_ready_for_import is the flag that actually decides whether a
        # visitor can attach it - region/by-request/discover-only can all
        # pass while this is false. Missed until 2026-08-23; see the comment
        # above CURATED.
        if str(row.get("is_ready_for_import")).lower() != "true":
            problems.append((g, "is_ready_for_import is false - not actually importable"))
        if not available_in(row, a.region):
            problems.append((g, f"no longer available in {a.region}"))

    for g, why in problems:
        title = str(catalog.get(g, {}).get("title", "?"))[:46]
        print(f"  FAIL  {g:16} {title:48} {why}")

    for g in wanted:
        if g in LISTINGS and not any(p[0] == g for p in problems):
            prov, acc, _s = LISTINGS[g]
            n = len(regions_of(catalog[g]))
            print(f"  ok    {str(catalog[g].get('title'))[:44]:46} "
                  f"{prov:30} {acc:18} {n} regions")

    print(f"\n{len(wanted) - len(problems)} of {len(wanted)} verified, "
          f"{len(problems)} failing")
    if problems:
        print("\nRefusing to write an index with unverified entries. Naming a "
              "listing or provider we cannot confirm is exactly the defect this "
              "file exists to prevent.")
        return 1

    if a.write:
        write_md(catalog, a.region)
        print(f"\nwrote {OUT}")
    else:
        print("\n(verify only - pass --write to regenerate the index)")
    return 0


def write_md(catalog, region):
    from datetime import date
    lines = [
        "---",
        "name: marketplace-index",
        'description: "Curated Snowflake Marketplace listings offered to booth '
        'visitors, each with a verified provider name, listing URL, access terms '
        'and region availability. Bundled so the booth never has to invent a '
        'listing. Rebuild with scripts/build_marketplace_index.py before each '
        'event."',
        "---",
        "",
        "# Curated Marketplace listings",
        "",
        f"**Catalogue checked:** {date.today().isoformat()} - every listing below "
        "is present in `SHOW AVAILABLE LISTINGS`, is not by-request or "
        f"discover-only, and is available in `{region}`.",
        f"**Providers and access terms read from the listing pages:** {VERIFIED_ON}.",
        "",
        "## What is verified, and what is not",
        "",
        "| Claim | How it is checked |",
        "|---|---|",
        "| The listing exists | `SHOW AVAILABLE LISTINGS`, every run |",
        "| Region availability | `regions` column, every run |",
        "| Not by-request / discover-only | access flags, every run |",
        "| Provider name | read from the rendered listing page, dated above |",
        "| Access terms | read from the rendered listing page, dated above |",
        "| **Fit to the industry** | **editorial judgement - review this** |",
        "",
        "Provider names cannot be re-derived by script: SQL exposes "
        "`organization_profile_name` for only 137 of 4,256 listings, and the "
        "public page is a client-rendered React app whose raw HTML contains no "
        "provider at all. They are recorded constants with a date, refreshed by "
        "loading the pages in a real browser.",
        "",
        "## Rules",
        "",
        "- **Never name a listing or provider that is not in this file.**",
        "- **Filter by region before offering a listing.** A visitor in London "
        "cannot use a us-east-1-only share, and sending them to one wastes the "
        "five minutes we just spent with them.",
        "- **Label anything that is not free.** Visitors are on a trial; an "
        "unmarked paid listing is a dead end.",
        "- If a listing has no stated access terms at all, leave it out. That is "
        "why Factori mobility data is excluded despite being relevant.",
        "",
    ]
    for industry, names in CURATED.items():
        lines += [f"## {industry}", "",
                  "| Listing | Provider | Access | Global name | Regions |",
                  "|---|---|---|---|---|"]
        for g in names:
            row = catalog[g]
            prov, acc, _s = LISTINGS[g]
            title = str(row.get("title")).strip()
            regs = regions_of(row)
            shown = ", ".join(regs[:4]) + (f" +{len(regs) - 4}" if len(regs) > 4 else "")
            lines.append(f"| [{title}]({url_for(g)}) | {prov} | {acc} | "
                         f"`{g}` | {shown} |")
        lines.append("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
