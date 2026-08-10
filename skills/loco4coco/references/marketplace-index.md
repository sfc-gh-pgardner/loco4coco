---
name: marketplace-index
description: "Curated Snowflake Marketplace listings offered to booth visitors, each with a verified provider name, listing URL, access terms and region availability. Bundled so the booth never has to invent a listing. Rebuild with scripts/build_marketplace_index.py before each event."
---

# Curated Marketplace listings

**Catalogue checked:** 2026-08-06 — every listing below is present in `SHOW AVAILABLE LISTINGS`, is not by-request or discover-only, and is available in `AWS_EU_WEST_2`.
**Providers and access terms read from the listing pages:** 2026-08-06.

## What is verified, and what is not

| Claim | How it is checked |
|---|---|
| The listing exists | `SHOW AVAILABLE LISTINGS`, every run |
| Region availability | `regions` column, every run |
| Not by-request / discover-only | access flags, every run |
| Provider name | read from the rendered listing page, dated above |
| Access terms | read from the rendered listing page, dated above |
| **Fit to the industry** | **editorial judgement — review this** |

Provider names cannot be re-derived by script: SQL exposes `organization_profile_name` for only 137 of 4,256 listings, and the public page is a client-rendered React app whose raw HTML contains no provider at all. They are recorded constants with a date, refreshed by loading the pages in a real browser.

## Rules

- **Never name a listing or provider that is not in this file.**
- **Filter by region before offering a listing.** A visitor in London cannot use a us-east-1-only share, and sending them to one wastes the five minutes we just spent with them.
- **Label anything that is not free.** Visitors are on a trial; an unmarked paid listing is a dead end.
- If a listing has no stated access terms at all, leave it out. That is why Factori mobility data is excluded despite being relevant.

## healthcare

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [UK (England and Wales only) Census 2021 - Trial](https://app.snowflake.com/marketplace/listing/GZSVZAJO3/jaywing-uk-england-and-wales-only-census-2021-trial) | Jaywing | Free | `GZSVZAJO3` | AWS_EU_WEST_1, AWS_EU_WEST_2, AZURE_UKSOUTH, GCP_EUROPE_WEST2 |
| [Acorn - Geodemographic Segmentation in the UK](https://app.snowflake.com/marketplace/listing/GZSVZ1K7VF/caci-ltd-acorn-geodemographic-segmentation-in-the-uk) | CACI Ltd | Free | `GZSVZ1K7VF` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +28 |
| [Postcode Sector Weather Forecasts](https://app.snowflake.com/marketplace/listing/GZTDZJKVCY/met-office-postcode-sector-weather-forecasts) | Met Office | Free 14-day trial | `GZTDZJKVCY` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +29 |
| [PubMed Biomedical Research Corpus](https://app.snowflake.com/marketplace/listing/GZSTZ67BY9OQW/snowflake-pubmed-biomedical-research-corpus) | Snowflake | Free | `GZSTZ67BY9OQW` | AWS_AP_NORTHEAST_1, AWS_AP_SOUTHEAST_1, AWS_AP_SOUTHEAST_2, AWS_EU_CENTRAL_1 +8 |
| [Healthcare Common Procedure Coding System Level II (HCPCS)](https://app.snowflake.com/marketplace/listing/GZSTZJUPD23/element-data-healthcare-common-procedure-coding-system-level-ii-hcpcs) | Element Data | Paid | `GZSTZJUPD23` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +28 |

## financial

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [Snowflake Public Data: Foreign Exchange Rates](https://app.snowflake.com/marketplace/listing/GZTSZ290BVCAO/snowflake-public-data-products-snowflake-public-data-foreign-exchange-rates) | Snowflake Public Data Products | Free 60-day trial | `GZTSZ290BVCAO` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +47 |
| [Inflation Forecasting - Headline & Core CPI by Country](https://app.snowflake.com/marketplace/listing/GZTDZ7DJU9/turnleaf-analytics-inflation-forecasting-headline-core-cpi-by-country) | Turnleaf Analytics | Free | `GZTDZ7DJU9` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +13 |
| [Company Data UK (incl. Guernsey) - XL Dataset](https://app.snowflake.com/marketplace/listing/GZ2FSZH8URW/north-data-gmbh-company-data-uk-incl-guernsey-xl-dataset) | North Data GmbH | Free 7-day trial | `GZ2FSZH8URW` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +33 |
| [Industry Classification Systems (NAICS, ANZSIC, ISIC, UK-SIC, etc.)](https://app.snowflake.com/marketplace/listing/GZSTZLT2II6/ibisworld-industry-classification-systems-naics-anzsic-isic-uk-sic-etc) | IBISWorld | Free | `GZSTZLT2II6` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +33 |
| [CSRHub ESG (Environment, Social, Governance) Fast Start](https://app.snowflake.com/marketplace/listing/GZT0ZI0XJ6Q/csrhub-llc-csrhub-esg-environment-social-governance-fast-start) | CSRHub LLC | Free 30-day trial | `GZT0ZI0XJ6Q` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +28 |

## retail

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [Postcode Sector Weather Forecasts](https://app.snowflake.com/marketplace/listing/GZTDZJKVCY/met-office-postcode-sector-weather-forecasts) | Met Office | Free 14-day trial | `GZTDZJKVCY` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +29 |
| [Acorn - Geodemographic Segmentation in the UK](https://app.snowflake.com/marketplace/listing/GZSVZ1K7VF/caci-ltd-acorn-geodemographic-segmentation-in-the-uk) | CACI Ltd | Free | `GZSVZ1K7VF` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +28 |
| [PayCheck – UK household income estimates at postcode level - SAMPLE data](https://app.snowflake.com/marketplace/listing/GZSVZ1K7UA/caci-ltd-paycheck-%E2%80%93-uk-household-income-estimates-at-postcode-level-sample-data) | CACI Ltd | Free | `GZSVZ1K7UA` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +39 |
| [UK (England and Wales only) Census 2021 - Trial](https://app.snowflake.com/marketplace/listing/GZSVZAJO3/jaywing-uk-england-and-wales-only-census-2021-trial) | Jaywing | Free | `GZSVZAJO3` | AWS_EU_WEST_1, AWS_EU_WEST_2, AZURE_UKSOUTH, GCP_EUROPE_WEST2 |
| [Industry Classification Systems (NAICS, ANZSIC, ISIC, UK-SIC, etc.)](https://app.snowflake.com/marketplace/listing/GZSTZLT2II6/ibisworld-industry-classification-systems-naics-anzsic-isic-uk-sic-etc) | IBISWorld | Free | `GZSTZLT2II6` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +33 |

## public

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [UK (England and Wales only) Census 2021 - Trial](https://app.snowflake.com/marketplace/listing/GZSVZAJO3/jaywing-uk-england-and-wales-only-census-2021-trial) | Jaywing | Free | `GZSVZAJO3` | AWS_EU_WEST_1, AWS_EU_WEST_2, AZURE_UKSOUTH, GCP_EUROPE_WEST2 |
| [Address Spine – UK address level property information - Sample Data](https://app.snowflake.com/marketplace/listing/GZSVZ1K7UQ/caci-ltd-address-spine-%E2%80%93-uk-address-level-property-information-sample-data) | CACI Ltd | Free | `GZSVZ1K7UQ` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +39 |
| [CARTO Boundaries](https://app.snowflake.com/marketplace/listing/GZT0Z4CM1E9L4/carto-carto-boundaries) | CARTO | Free | `GZT0Z4CM1E9L4` | AWS_EU_WEST_2, AWS_US_EAST_1 |
| [Acorn - Geodemographic Segmentation in the UK](https://app.snowflake.com/marketplace/listing/GZSVZ1K7VF/caci-ltd-acorn-geodemographic-segmentation-in-the-uk) | CACI Ltd | Free | `GZSVZ1K7VF` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +28 |
| [National Severe Weather Warning Service](https://app.snowflake.com/marketplace/listing/GZTDZJKVCU/met-office-national-severe-weather-warning-service) | Met Office | Free | `GZTDZJKVCU` | AWS_AF_SOUTH_1, AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3 +50 |

## manufacturing

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [CEIC Commodities Data](https://app.snowflake.com/marketplace/listing/GZTSZRC7HQ3/ceic-data-ceic-commodities-data) | CEIC Data | Free | `GZTSZRC7HQ3` | AWS_AF_SOUTH_1, AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3 +38 |
| [Company Data UK (incl. Guernsey) - XL Dataset](https://app.snowflake.com/marketplace/listing/GZ2FSZH8URW/north-data-gmbh-company-data-uk-incl-guernsey-xl-dataset) | North Data GmbH | Free 7-day trial | `GZ2FSZH8URW` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +33 |
| [Snowflake Public Data: Core Weather Data](https://app.snowflake.com/marketplace/listing/GZTSZ290BVSAO/snowflake-public-data-products-snowflake-public-data-core-weather-data) | Snowflake Public Data Products | Free 60-day trial | `GZTSZ290BVSAO` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +49 |
| [Carbon Footprint Data Scope 1/2/3 | Sustainability & Performance Reporting](https://app.snowflake.com/marketplace/listing/GZ1MMZD99V46/yuzedata-carbon-footprint-data-scope-1-2-3-sustainability-performance-reporting) | YuzeData | Free | `GZ1MMZD99V46` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +42 |
| [Overture Maps - Transportation](https://app.snowflake.com/marketplace/listing/GZT0Z4CM1E9KJ/carto-overture-maps-transportation) | CARTO | Free | `GZT0Z4CM1E9KJ` | AWS_AP_NORTHEAST_1, AWS_CA_CENTRAL_1, AWS_EU_CENTRAL_1, AWS_EU_NORTH_1 +10 |

## energy

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [Postcode Sector Weather Forecasts](https://app.snowflake.com/marketplace/listing/GZTDZJKVCY/met-office-postcode-sector-weather-forecasts) | Met Office | Free 14-day trial | `GZTDZJKVCY` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +29 |
| [National Severe Weather Warning Service](https://app.snowflake.com/marketplace/listing/GZTDZJKVCU/met-office-national-severe-weather-warning-service) | Met Office | Free | `GZTDZJKVCU` | AWS_AF_SOUTH_1, AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3 +50 |
| [Yes Energy - Sample Data](https://app.snowflake.com/marketplace/listing/GZSOZ71OJH/yes-energy-yes-energy-sample-data) | Yes Energy | Free | `GZSOZ71OJH` | AWS_CA_CENTRAL_1, AWS_EU_CENTRAL_1, AWS_EU_NORTH_1, AWS_EU_WEST_1 +22 |
| [Coal Global Data](https://app.snowflake.com/marketplace/listing/GZSVZ5WLU0/kpler-coal-global-data) | Kpler | Free | `GZSVZ5WLU0` | AWS_EU_WEST_1, AWS_EU_WEST_2, AWS_EU_WEST_3, AWS_US_EAST_1 +1 |
| [Carbon Footprint Data Scope 1/2/3 | Sustainability & Performance Reporting](https://app.snowflake.com/marketplace/listing/GZ1MMZD99V46/yuzedata-carbon-footprint-data-scope-1-2-3-sustainability-performance-reporting) | YuzeData | Free | `GZ1MMZD99V46` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +42 |

## media

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [Acorn - Geodemographic Segmentation in the UK](https://app.snowflake.com/marketplace/listing/GZSVZ1K7VF/caci-ltd-acorn-geodemographic-segmentation-in-the-uk) | CACI Ltd | Free | `GZSVZ1K7VF` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +28 |
| [UK (England and Wales only) Census 2021 - Trial](https://app.snowflake.com/marketplace/listing/GZSVZAJO3/jaywing-uk-england-and-wales-only-census-2021-trial) | Jaywing | Free | `GZSVZAJO3` | AWS_EU_WEST_1, AWS_EU_WEST_2, AZURE_UKSOUTH, GCP_EUROPE_WEST2 |
| [Over-the-Top (OTT) Market Analysis: Purchase Behavior Of Sports Fans](https://app.snowflake.com/marketplace/listing/GZT0Z12POH90/sports-innovation-lab-over-the-top-ott-market-analysis-purchase-behavior-of-sports-fans) | Sports Innovation Lab | Free | `GZT0Z12POH90` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +38 |
| [Snowflake Public Data: Core Weather Data](https://app.snowflake.com/marketplace/listing/GZTSZ290BVSAO/snowflake-public-data-products-snowflake-public-data-core-weather-data) | Snowflake Public Data Products | Free 60-day trial | `GZTSZ290BVSAO` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +49 |
| [CARTO Boundaries](https://app.snowflake.com/marketplace/listing/GZT0Z4CM1E9L4/carto-carto-boundaries) | CARTO | Free | `GZT0Z4CM1E9L4` | AWS_EU_WEST_2, AWS_US_EAST_1 |

## other

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [Snowflake Public Data: Core Weather Data](https://app.snowflake.com/marketplace/listing/GZTSZ290BVSAO/snowflake-public-data-products-snowflake-public-data-core-weather-data) | Snowflake Public Data Products | Free 60-day trial | `GZTSZ290BVSAO` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +49 |
| [UK (England and Wales only) Census 2021 - Trial](https://app.snowflake.com/marketplace/listing/GZSVZAJO3/jaywing-uk-england-and-wales-only-census-2021-trial) | Jaywing | Free | `GZSVZAJO3` | AWS_EU_WEST_1, AWS_EU_WEST_2, AZURE_UKSOUTH, GCP_EUROPE_WEST2 |
| [Company Data UK (incl. Guernsey) - XL Dataset](https://app.snowflake.com/marketplace/listing/GZ2FSZH8URW/north-data-gmbh-company-data-uk-incl-guernsey-xl-dataset) | North Data GmbH | Free 7-day trial | `GZ2FSZH8URW` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +33 |
| [CARTO Boundaries](https://app.snowflake.com/marketplace/listing/GZT0Z4CM1E9L4/carto-carto-boundaries) | CARTO | Free | `GZT0Z4CM1E9L4` | AWS_EU_WEST_2, AWS_US_EAST_1 |
| [Snowflake Public Data: Foreign Exchange Rates](https://app.snowflake.com/marketplace/listing/GZTSZ290BVCAO/snowflake-public-data-products-snowflake-public-data-foreign-exchange-rates) | Snowflake Public Data Products | Free 60-day trial | `GZTSZ290BVCAO` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +47 |
