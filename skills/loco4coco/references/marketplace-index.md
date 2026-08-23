---
name: marketplace-index
description: "Curated Snowflake Marketplace listings offered to booth visitors, each with a verified provider name, listing URL, access terms and region availability. Bundled so the booth never has to invent a listing. Rebuild with scripts/build_marketplace_index.py before each event."
---

# Curated Marketplace listings

**Catalogue checked:** 2026-08-23 - every listing below is present in `SHOW AVAILABLE LISTINGS`, is not by-request or discover-only, and is available in `AWS_EU_WEST_2`.
**Providers and access terms read from the listing pages:** 2026-08-06.

## What is verified, and what is not

| Claim | How it is checked |
|---|---|
| The listing exists | `SHOW AVAILABLE LISTINGS`, every run |
| Region availability | `regions` column, every run |
| Not by-request / discover-only | access flags, every run |
| Provider name | read from the rendered listing page, dated above |
| Access terms | read from the rendered listing page, dated above |
| **Fit to the industry** | **editorial judgement - review this** |

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
| [UK Health Facts and Dimensions Sample](https://app.snowflake.com/marketplace/listing/GZ2FRZQNY1/facts-and-dimensions-ltd-uk-health-facts-and-dimensions-sample) | Facts and Dimensions Ltd | Free | `GZ2FRZQNY1` | AWS_EU_CENTRAL_1, AWS_EU_WEST_2, AZURE_UKSOUTH, GCP_EUROPE_WEST2 |
| [Household Acorn - geodemographic segmentation at household level SAMPLE DATA](https://app.snowflake.com/marketplace/listing/GZSVZ1K7UU) | CACI Ltd | Free | `GZSVZ1K7UU` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +39 |

## financial

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [Snowflake Public Data: Foreign Exchange Rates](https://app.snowflake.com/marketplace/listing/GZTSZ290BVCAO/snowflake-public-data-products-snowflake-public-data-foreign-exchange-rates) | Snowflake Public Data Products | Free 60-day trial | `GZTSZ290BVCAO` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +47 |
| [Inflation Forecasting - Headline & Core CPI by Country](https://app.snowflake.com/marketplace/listing/GZTDZ7DJU9/turnleaf-analytics-inflation-forecasting-headline-core-cpi-by-country) | Turnleaf Analytics | Free | `GZTDZ7DJU9` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +13 |
| [Company Data UK (incl. Guernsey) - XL Dataset](https://app.snowflake.com/marketplace/listing/GZ2FSZH8URW/north-data-gmbh-company-data-uk-incl-guernsey-xl-dataset) | North Data GmbH | Free 7-day trial | `GZ2FSZH8URW` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +33 |
| [Industry Classification Systems (NAICS, ANZSIC, ISIC, UK-SIC, etc.)](https://app.snowflake.com/marketplace/listing/GZSTZLT2II6/ibisworld-industry-classification-systems-naics-anzsic-isic-uk-sic-etc) | IBISWorld | Free | `GZSTZLT2II6` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +33 |
| [CSRHub ESG (Environment, Social, Governance) Fast Start](https://app.snowflake.com/marketplace/listing/GZT0ZI0XJ6Q/csrhub-llc-csrhub-esg-environment-social-governance-fast-start) | CSRHub LLC | Free 30-day trial | `GZT0ZI0XJ6Q` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +28 |
| [Banking Analytics Bundle](https://app.snowflake.com/marketplace/listing/GZTYZAPS3FP) | InSights | Free | `GZTYZAPS3FP` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +31 |

## retail

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [Postcode Sector Weather Forecasts](https://app.snowflake.com/marketplace/listing/GZTDZJKVCY/met-office-postcode-sector-weather-forecasts) | Met Office | Free 14-day trial | `GZTDZJKVCY` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +29 |
| [Acorn - Geodemographic Segmentation in the UK](https://app.snowflake.com/marketplace/listing/GZSVZ1K7VF/caci-ltd-acorn-geodemographic-segmentation-in-the-uk) | CACI Ltd | Free | `GZSVZ1K7VF` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +28 |
| [PayCheck - UK household income estimates at postcode level - SAMPLE data](https://app.snowflake.com/marketplace/listing/GZSVZ1K7UA/caci-ltd-paycheck-%E2%80%93-uk-household-income-estimates-at-postcode-level-sample-data) | CACI Ltd | Free | `GZSVZ1K7UA` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +39 |
| [UK (England and Wales only) Census 2021 - Trial](https://app.snowflake.com/marketplace/listing/GZSVZAJO3/jaywing-uk-england-and-wales-only-census-2021-trial) | Jaywing | Free | `GZSVZAJO3` | AWS_EU_WEST_1, AWS_EU_WEST_2, AZURE_UKSOUTH, GCP_EUROPE_WEST2 |
| [Industry Classification Systems (NAICS, ANZSIC, ISIC, UK-SIC, etc.)](https://app.snowflake.com/marketplace/listing/GZSTZLT2II6/ibisworld-industry-classification-systems-naics-anzsic-isic-uk-sic-etc) | IBISWorld | Free | `GZSTZLT2II6` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +33 |
| [Spatial Features (GBR, Quadgrid 15 and H3 Res. 8)](https://app.snowflake.com/marketplace/listing/GZT0ZKUCHKL) | CARTO | Free | `GZT0ZKUCHKL` | AWS_EU_WEST_1, AWS_EU_WEST_2, AWS_US_EAST_1 |

## public

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [UK (England and Wales only) Census 2021 - Trial](https://app.snowflake.com/marketplace/listing/GZSVZAJO3/jaywing-uk-england-and-wales-only-census-2021-trial) | Jaywing | Free | `GZSVZAJO3` | AWS_EU_WEST_1, AWS_EU_WEST_2, AZURE_UKSOUTH, GCP_EUROPE_WEST2 |
| [Address Spine - UK address level property information - Sample Data](https://app.snowflake.com/marketplace/listing/GZSVZ1K7UQ/caci-ltd-address-spine-%E2%80%93-uk-address-level-property-information-sample-data) | CACI Ltd | Free | `GZSVZ1K7UQ` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +39 |
| [CARTO Boundaries](https://app.snowflake.com/marketplace/listing/GZT0Z4CM1E9L4/carto-carto-boundaries) | CARTO | Free | `GZT0Z4CM1E9L4` | AWS_EU_WEST_2, AWS_US_EAST_1 |
| [Acorn - Geodemographic Segmentation in the UK](https://app.snowflake.com/marketplace/listing/GZSVZ1K7VF/caci-ltd-acorn-geodemographic-segmentation-in-the-uk) | CACI Ltd | Free | `GZSVZ1K7VF` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +28 |
| [National Severe Weather Warning Service](https://app.snowflake.com/marketplace/listing/GZTDZJKVCU/met-office-national-severe-weather-warning-service) | Met Office | Free | `GZTDZJKVCU` | AWS_AF_SOUTH_1, AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3 +50 |
| [Administrative boundaries - Great Britain: Boundary Line - Open](https://app.snowflake.com/marketplace/listing/GZ1MOZBWYYT) | Ordnance Survey | Free | `GZ1MOZBWYYT` | ALL |

## manufacturing

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [CEIC Commodities Data](https://app.snowflake.com/marketplace/listing/GZTSZRC7HQ3/ceic-data-ceic-commodities-data) | CEIC Data | Free | `GZTSZRC7HQ3` | AWS_AF_SOUTH_1, AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3 +38 |
| [Company Data UK (incl. Guernsey) - XL Dataset](https://app.snowflake.com/marketplace/listing/GZ2FSZH8URW/north-data-gmbh-company-data-uk-incl-guernsey-xl-dataset) | North Data GmbH | Free 7-day trial | `GZ2FSZH8URW` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +33 |
| [Overture Maps - Transportation](https://app.snowflake.com/marketplace/listing/GZT0Z4CM1E9KJ/carto-overture-maps-transportation) | CARTO | Free | `GZT0Z4CM1E9KJ` | AWS_AP_NORTHEAST_1, AWS_CA_CENTRAL_1, AWS_EU_CENTRAL_1, AWS_EU_NORTH_1 +11 |
| [FactSet Supply Chain Relationships (sample)](https://app.snowflake.com/marketplace/listing/GZT0ZGCQ51RQ) | FactSet | Free | `GZT0ZGCQ51RQ` | ALL |
| [D&B Shipping Insights Sample](https://app.snowflake.com/marketplace/listing/GZT0ZPWB4J7) | Dun & Bradstreet | Free | `GZT0ZPWB4J7` | ALL |
| [Solid United Nations Codes for Trade and Transport Locations](https://app.snowflake.com/marketplace/listing/GZU6Z630VEJ0W) | Solid Data LLC | Free 30-day trial | `GZU6Z630VEJ0W` | AWS_AF_SOUTH_1, AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3 +52 |

## energy

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [Postcode Sector Weather Forecasts](https://app.snowflake.com/marketplace/listing/GZTDZJKVCY/met-office-postcode-sector-weather-forecasts) | Met Office | Free 14-day trial | `GZTDZJKVCY` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +29 |
| [National Severe Weather Warning Service](https://app.snowflake.com/marketplace/listing/GZTDZJKVCU/met-office-national-severe-weather-warning-service) | Met Office | Free | `GZTDZJKVCU` | AWS_AF_SOUTH_1, AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3 +50 |
| [Yes Energy - Sample Data](https://app.snowflake.com/marketplace/listing/GZSOZ71OJH/yes-energy-yes-energy-sample-data) | Yes Energy | Free | `GZSOZ71OJH` | AWS_CA_CENTRAL_1, AWS_EU_CENTRAL_1, AWS_EU_NORTH_1, AWS_EU_WEST_1 +22 |
| [Sample of GasMarketCube - Global Gas Supply, Demand and Trade](https://app.snowflake.com/marketplace/listing/GZSVZ8MX1I) | Rystad Energy | Free | `GZSVZ8MX1I` | ALL |
| [Wind Power Forecast, Day-ahead - Sample](https://app.snowflake.com/marketplace/listing/GZSYZSRWU5) | Weather Solutions | Free | `GZSYZSRWU5` | ALL |
| [Crude oil price data](https://app.snowflake.com/marketplace/listing/GZTDZ1PNFO) | General Index | Free Trial | `GZTDZ1PNFO` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +34 |

## media

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [Acorn - Geodemographic Segmentation in the UK](https://app.snowflake.com/marketplace/listing/GZSVZ1K7VF/caci-ltd-acorn-geodemographic-segmentation-in-the-uk) | CACI Ltd | Free | `GZSVZ1K7VF` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +28 |
| [UK (England and Wales only) Census 2021 - Trial](https://app.snowflake.com/marketplace/listing/GZSVZAJO3/jaywing-uk-england-and-wales-only-census-2021-trial) | Jaywing | Free | `GZSVZAJO3` | AWS_EU_WEST_1, AWS_EU_WEST_2, AZURE_UKSOUTH, GCP_EUROPE_WEST2 |
| [CARTO Boundaries](https://app.snowflake.com/marketplace/listing/GZT0Z4CM1E9L4/carto-carto-boundaries) | CARTO | Free | `GZT0Z4CM1E9L4` | AWS_EU_WEST_2, AWS_US_EAST_1 |
| [Spatial Features (GBR, Quadgrid 15 and H3 Res. 8)](https://app.snowflake.com/marketplace/listing/GZT0ZKUCHKL) | CARTO | Free | `GZT0ZKUCHKL` | AWS_EU_WEST_1, AWS_EU_WEST_2, AWS_US_EAST_1 |
| [GLP-1 Social Conversations Sample Dataset](https://app.snowflake.com/marketplace/listing/GZT1ZFQ0JE5) | Socialgist | Free | `GZT1ZFQ0JE5` | AWS_AF_SOUTH_1, AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3 +41 |
| [American Community Survey, 2016](https://app.snowflake.com/marketplace/listing/GZSNZ4PHA6) | data.world, Inc | Free | `GZSNZ4PHA6` | ALL |

## other

| Listing | Provider | Access | Global name | Regions |
|---|---|---|---|---|
| [UK (England and Wales only) Census 2021 - Trial](https://app.snowflake.com/marketplace/listing/GZSVZAJO3/jaywing-uk-england-and-wales-only-census-2021-trial) | Jaywing | Free | `GZSVZAJO3` | AWS_EU_WEST_1, AWS_EU_WEST_2, AZURE_UKSOUTH, GCP_EUROPE_WEST2 |
| [Company Data UK (incl. Guernsey) - XL Dataset](https://app.snowflake.com/marketplace/listing/GZ2FSZH8URW/north-data-gmbh-company-data-uk-incl-guernsey-xl-dataset) | North Data GmbH | Free 7-day trial | `GZ2FSZH8URW` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +33 |
| [CARTO Boundaries](https://app.snowflake.com/marketplace/listing/GZT0Z4CM1E9L4/carto-carto-boundaries) | CARTO | Free | `GZT0Z4CM1E9L4` | AWS_EU_WEST_2, AWS_US_EAST_1 |
| [Snowflake Public Data: Foreign Exchange Rates](https://app.snowflake.com/marketplace/listing/GZTSZ290BVCAO/snowflake-public-data-products-snowflake-public-data-foreign-exchange-rates) | Snowflake Public Data Products | Free 60-day trial | `GZTSZ290BVCAO` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +47 |
| [CARTO Analytics Toolbox](https://app.snowflake.com/marketplace/listing/GZT0Z4CM1E9NA/carto-carto-analytics-toolbox) | CARTO | Free | `GZT0Z4CM1E9NA` | AWS_AP_NORTHEAST_1, AWS_AP_SOUTHEAST_3, AWS_CA_CENTRAL_1, AWS_EU_CENTRAL_1 +27 |
| [Acorn - Geodemographic Segmentation in the UK](https://app.snowflake.com/marketplace/listing/GZSVZ1K7VF/caci-ltd-acorn-geodemographic-segmentation-in-the-uk) | CACI Ltd | Free | `GZSVZ1K7VF` | AWS_AP_NORTHEAST_1, AWS_AP_NORTHEAST_2, AWS_AP_NORTHEAST_3, AWS_AP_SOUTHEAST_1 +28 |
