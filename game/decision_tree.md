# Loco 4 CoCo - the booth decision tree

Every option a visitor is offered, every line CoCo speaks, and every dataset the booth recommends. Generated from the live app: `config.json`, `marketplace-index.md`, `archetypes.md` and `server.py`.

Regenerate with `python3 game/decision_tree.py`.

## 1. What the visitor does

Six stops. The letter is the whole intake on one screen; the four locations are walked to on a map in the order below.

| # | Stop | What the visitor gives us | Options come from | Select |
| --- | --- | --- | --- | --- |
| 0 | The letter | First name, employer, industry, the problem in two sentences, where the data lives and which countries they operate in | `industries` for the list, `platforms` and `country` for the chips; the problem is free text | Single industry, multi-select chips, free text |
| 1 | The house | Nothing. CoCo reads back what the letter said and makes the security and AI point | - | - |
| 2 | The Data Library | The data they already hold | `industries.<key>.data_sources` | Multi-select plus free text |
| 3 | The Marketplace | Datasets to join to it | `marketplace-index.md` | Multi-select plus free text |
| 4 | The Workshop | One line describing what the proof of concept should do | Free text | Free text |
| 5 | The Postbox | Confirmation to send | - | Button |

The map unlocks in this order: **The Data Library**, **The Marketplace**, **The Workshop**, **The Postbox**.

The visitor's answers reach the document by two routes. The library, marketplace and workshop answers are named back to them by the model, which picks from the closed lists in this document and never invents an entry. The archetype, its features and its first step are precomputed, so they are correct whether or not a model answers.

## 2. Every scripted line, in running order

Fixed copy, identical for every visitor, straight from `config.json`. Braced placeholders such as `{first_name}`, `{company}`, `{country}`, `{platform}` and `{region}` are filled from the visitor's own answers.

The one-line replies CoCo speaks at the Library, Marketplace and Workshop are not listed here. Those are generated per visit, reflecting back what the visitor just picked.

### 2.1 Intro card

- **Title:** Loco for CoCo
- **Button:** START
- This is a fun way to experience the power of Cortex Code (CoCo) through the medium of an arcade game.
- You have 5 minutes to explore what building a Proof of Concept on Snowflake really looks like, with CoCo as your guide to our features, marketplace datasets, and how enterprise-grade AI can bring your ideas to life.
- You will leave with a personalised action plan for building it for real. Be daring, this is a flexible process with a genuinely useful outcome.
- *Anything you type stays private*, only shared with you and Snowflake.

Text wrapped in asterisks renders as a highlight colour rather than body text.

### 2.2 The house: CoCo arrives and reads a letter

- **arctic:** Somewhere in the Arctic...
- **arctic_sub:** (Yes, penguins live in Antarctica, but CoCo is special!)
- **bubble:** Wow, a letter from my friend! Shame I can't make out some of these words... (Please fill this in with your details)
- **greeting:** Hey CoCo,
- **body[0]:** It's your friend {first_name}!
- **body[1]:** I've heard you and the Cortex Crew have been cooking up some amazing products recently.
- **body[2]:** Me and my team at {company} wanted to learn more.
- **body[3]:** We're particularly interested in {industry} and wanted to understand what a Proof of Concept (POC) would look like for this on Snowflake.
- **body[4]:** Could you help us out?
- **signoff:** Signed {first_name}
- **button:** THAT'S BETTER
- **line1:** A letter, from my friend {first_name}! Better get to work...
- **line2:** Anyway, let's go and get this show on the road.
- **map_line:** First stop is my Data Library. That's where I keep all the unstructured, semi-structured and structured data that would be useful for {first_name} and {company}.

### 2.3 The letter: what the visitor types

- **Your first name** (`first_name`) - placeholder: e.g. Priya
- **Where you work** (`company`) - placeholder: e.g. NHS Trust, Barclays, Tesco
- **industry_question:** And what world do you work in? I'll fill the library with the right shelves.
- **confirm_industry:** I'm guessing {industry} from {company} - have I got that right?
- **problem_label:** The problem you want to solve (two sentences)
- **problem_placeholder:** e.g. our engineers waste hours hunting through old inspection reports. We want answers in seconds, with the source.

The problem example above is the fallback. Once an industry is chosen it is replaced by that industry's own, and a "CoCo, you choose" button will draft a starting problem statement from the archetype pain lines, into an editable field.

- **Healthcare & Life Sciences:** e.g. our clinicians re-read discharge summaries to find one detail. We want the answer in seconds, with the source.
- **Financial Services:** e.g. every complaint is read by hand to spot the urgent ones. We want them sorted and routed the moment they land.
- **Retail & Consumer Goods:** e.g. nobody can say why a line sold out in one region and sat still in another. We want that answered without a data team.
- **Public Sector & Government:** e.g. our guidance sits in years of PDFs nobody can search. We want caseworkers to ask a question and get a cited answer.
- **Manufacturing & Industrial:** e.g. we find out a machine was failing after it stopped. We want the warning while there is still time to act.
- **Energy & Utilities:** e.g. engineer notes and meter data live apart, so we cannot connect a fault to what led to it. We want them joined up.
- **Media, Telco & Entertainment:** e.g. we know what was watched but not why anyone churned. We want the two joined so we can see it coming.
- **Something else:** e.g. the answer exists somewhere in our systems and it takes days to get it out. We want it in seconds, with the source.

### 2.4 The letter: the stack and the location

Asked on the letter itself, both multi-select. Where data and models may run is NOT asked: it is inferred from the location, because it only names the region in the sovereignty pillars and a visitor's own location answers it more honestly than a question about their compliance position.

**We currently keep data on…**

- **Hint:** Tap every platform it sits on. This is what decides how we get it into Snowflake.
- Microsoft / Azure
- AWS
- Google Cloud
- Oracle
- SAP
- On-premise / our own servers
- SaaS apps (Salesforce, Workday, etc.)
- Already in Snowflake
- Not sure yet
- **Cannot be combined with a named source:** Not sure yet

**As you'll remember CoCo, we're based in**

- **Hint:** Tap every country you have a base in. It helps me keep your data where your rules need it.
- United Kingdom
- Ireland
- France
- Germany
- Netherlands
- Nordics
- Rest of EU
- Somewhere else
- **Free text option:** Somewhere else

### 2.5 The letter: CoCo's reply to each answer

- **platform_already:** Perfect - it's already in Snowflake, so we skip the plumbing and go straight to building.
- **platform_unsure:** No problem - we'll work the plumbing out together, it's usually the easy part.
- **platform_named:** Good - I know exactly how to get data out of {platform} and into Snowflake, in region and without copying it around.
- **country:** {country}, lovely. I'll keep everything where {country}'s rules need it.

Several countries may be picked, and CoCo answers on the strictest reading the location supports.

### 2.6 The house: CoCo reads it back

Spoken over the house scene once the letter is submitted. CoCo names what was given, then makes the security and AI point inside that summary. The region comes from the visitor's own location. Each line advances on a timer scaled to its length.

- So, {first_name}, let me make sure I have this. {company_bit}{industry_bit}{platform_bit}I have the problem you want to solve, and that is the bit everything else hangs off.
- Here is the part that matters before we start building. By default, all of this happens inside your own Snowflake account in {region}. Your data does not get copied out to be processed, and the AI models run in your own region, so nothing has to cross a border to be understood.
- Snowflake never uses your Customer Data to train models made available to our customer base. Your data is not available to other customers or model developers. And you have control over your team's use of Snowflake AI Features through familiar role-based access control.
- You will not have to move house for any of it either. Snowflake talks to what you already run, and with Iceberg your tables stay in open formats other engines can read, so there is no one way door.

### 2.7 The blueprint: the four sovereignty pillars

Printed verbatim in the document the visitor takes away.

- **data:** By default your data does not leave {region}: it stays in your own Snowflake account, in region, not copied out to be processed.
- **models:** By default, Cortex runs the AI models in your own region, so nothing has to cross a border to be understood.
- **marketplace:** Marketplace data is shared live rather than copied, and you are only ever offered listings available in {region}.
- **governance:** One set of controls - role-based access, masking, row-level policies - governs all of it, in one place.

### 2.8 The four locations

**The Data Library** - Data your company already holds

- **narrative:** This is my magic data library, {first_name}. Every shelf can mimic something {company} already holds. You can ask me for anything, from MP3 to CSV, PDF to Parquet.
- **heading:** Which of these do you work with at the moment?
- **hint:** Tick everything that applies. Add your own if it's missing.
- **other_label:** Something else you hold
- **other_placeholder:** e.g. 20 years of inspection photographs

**The Marketplace** - Data to enhance it

- **narrative:** This is the Snowflake Marketplace, and every stall is a real company's data. You attach it and query it live, seconds later. You never copy it, you never build a pipeline for it, and you never pay to store it.
- **heading:** What shall we join to your data?
- **hint:** Live listings, filtered to what you can attach in this region. No ETL, no storage cost, refreshed by the provider. The same door works outwards: this is how you share your own data without handing over a copy.
- **other_label:** Something else you'd join
- **other_placeholder:** e.g. UK postcode boundaries, company registry data

**The Workshop** - Build the POC

- **narrative:** Bench cleared, forge lit. Tell me what the finished thing does and I'll draw up the plan.
- **heading:** What do we want our Proof of Concept to do?
- **hint:** Think big and say it in one line. An AI agent that answers for you, a dashboard that explains itself, an app your team actually opens every morning, something that spots trouble before it lands. Whatever it is, we forge it here.
- **placeholder:** e.g. an agent that answers policy questions with citations

**The Postbox** - Send the present

- **narrative:** Wrapped, labelled and ready. Say the word and I'll put it in your hands.
- **heading:** Shall I post it?
- **hint:** I'll write it up properly and put it in the post.
- **button:** CREATE MY BLUEPRINT
- **button_sent:** SEE MY POSTCARD

### 2.9 The Data Library: the synthetic-data offer

- CoCo can mimic any shelf as synthetic data so a POC can start before the real feed exists. Generate it in Snowflake with GENERATOR and RANDOM, or let Cortex fabricate realistic rows from a description.

### 2.10 The Postbox: what CoCo says on send

- **On success:** Wrapped and labelled, {first_name}. Scan the code on screen and it is yours - the link works for seven days.
- **If staging fails:** I could not wrap it up this time - grab a Snowflake person and we will sort it.

### 2.11 Screen furniture

Prose that belongs to a screen rather than to a stop.

- **history_banner:** Looking back — press ▶ to return to now
- **handover_heading:** Take it with you now
- **handover_body:** Scan this with your phone camera to download your Word blueprint. The link works for seven days.
- **card_heading:** Scan to keep your card.
- **card_body:** It saves straight to your phone. Yours to post - tag us and we will see it. Works for seven days.

## 3. The datasets the booth recommends

48 slots across 8 industries, filled by 32 distinct listings, for THIS venue. Each is a real listing on the Snowflake Marketplace - never invented - and is chosen for relevance to the event city. A pick is NOT judged on whether the booth account can attach it: the visitor never imports anything here, they leave with links and open them later from their own account.

### Healthcare & Life Sciences

| Listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| GfK Population by Age Group & Gender Germany | NIQ-GFK | Free | `GZSYZG5AL` |
| COVID-19 Epidemiological Data | Starschema | Free | `GZSNZ7F5UH` |
| MBI Sociodemographic Data for Germany | Michael Bauer International GmbH | Free | `GZSYZ12OI8L` |
| Basic Sociodemographics-Bundle for Countries Worldwide | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOH` |
| Demographics Data Bundle | InSights | Free | `GZTYZAPS3FT` |
| Population - Statistics - OECD - Free | Data Army Intel | Free | `GZSUZCN9EG` |

### Financial Services

| Listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| QuantCube CPI Nowcast | QuantCube Technology | Free | `GZTWZ4KVS1` |
| Company data | OpenCorporates | Free | `GZTDZM1AK5` |
| ESG Performance Score Core & Plus | ESG Book | Free | `GZTDZ1ELIY` |
| Consumer Credit & Debit Card Transaction Data \| European Spend | Consumer Edge | Free | `GZTSZPM12Y` |
| CEIC World Macro Economic Data | CEIC Data | Free | `GZTSZRC7HRG` |
| Purchasing Power for Countries Worldwide | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOT` |

### Retail & Consumer Goods

| Listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| MBI Sociodemographic Data for Germany | Michael Bauer International GmbH | Free | `GZSYZ12OI8L` |
| Shopping center footfall - London and Paris | Mytraffic | Free | `GZSYZGJWCJ` |
| Weather-based demand indices - Data sample | Wetter.com | Free | `GZSVZA7RAG` |
| Retail Price Promo Sample | Daltix | Free | `GZSVZ5J5F` |
| Basic Sociodemographics-Bundle for Countries Worldwide | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOH` |
| Purchasing Power for Countries Worldwide | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOT` |

Pinned first when the live tier is enabled: `GZTDZJKVCY`, `GZSVZAJO3`.

### Public Sector & Government

| Listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| MBI Global Area Boundaries | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOX` |
| Fiber Internet Coverage Dataset | GroupBWT | Free | `GZSYZ12SH0Y` |
| Driving Behavior Events | Vianova | Free | `GZSYZ5FFSV` |
| European Public Tenders Dataset – 800+ Sources, Daily Updates, OCDS Format | GroupBWT | Free | `GZSYZ12SH0I` |
| GfK Population by Age Group & Gender Germany | NIQ-GFK | Free | `GZSYZG5AL` |
| World Boundaries Premium | Precisely | Free | `GZT0Z2BR4AC92` |

Pinned first when the live tier is enabled: `GZSVZAJO3`, `GZ1MOZBWYYT`, `GZSVZ1K7UQ`.

### Manufacturing & Industrial

| Listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| CEIC Shipping Data | CEIC Data | Free | `GZTSZRC7HRC` |
| CEIC Commodities Data | CEIC Data | Free | `GZTSZRC7HQ3` |
| Company data | OpenCorporates | Free | `GZTDZM1AK5` |
| Germany H3 Travel Matrix | Dekart XYZ | Free | `GZSYZ43W9K16` |
| Industry Classification Systems (NAICS, ANZSIC, ISIC, UK-SIC, etc.) | IBISWorld | Free | `GZSTZLT2II6` |
| Overture Maps - Transportation | CARTO | Free | `GZT0Z4CM1E9KJ` |

### Energy & Utilities

| Listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| Historical Weather Data Sample | Wetter.com | Free | `GZSVZA7RAK` |
| Corporate Climate Commitment ESG Data \| Net Zero, Carbon Neutrality, and Carbon Positivity | Tracenable | Free | `GZTSZ36AC98` |
| Global Weather & Climate Data by Pelmorex Weather Source | Pelmorex Weather Source | Free | `GZSOZ1LLD8` |
| POIs - EV charging stations in Paris | Mytraffic | Free | `GZSYZGJWCN` |
| Purchasing Power for Countries Worldwide | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOT` |
| Weather-based demand indices - Data sample | Wetter.com | Free | `GZSVZA7RAG` |

Pinned first when the live tier is enabled: `GZTDZJKVCM`, `GZTDZJKVCU`, `GZTDZJKVCY`.

### Media, Telco & Entertainment

| Listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| Fiber Internet Coverage Dataset | GroupBWT | Free | `GZSYZ12SH0Y` |
| Intelligent Event Data: Attended Events, Munich - Sample | PredictHQ | Free | `GZSTZIDI09G` |
| Mastercard Audiences | Mastercard | Free | `GZTSZT83AIS` |
| MBI Sociodemographic Data for Germany | Michael Bauer International GmbH | Free | `GZSYZ12OI8L` |
| Basic Sociodemographics-Bundle for Countries Worldwide | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOH` |
| European Broadband Markets 2017 | Expert Intelligence | Free | `GZSVZ6EW2A` |

### Something else

| Listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| MBI Global Area Boundaries | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOX` |
| Company data | OpenCorporates | Free | `GZTDZM1AK5` |
| Historical Weather Data Sample | Wetter.com | Free | `GZSVZA7RAK` |
| Germany H3 Travel Matrix | Dekart XYZ | Free | `GZSYZ43W9K16` |
| GfK Population by Age Group & Gender Germany | NIQ-GFK | Free | `GZSYZG5AL` |
| World Boundaries Premium | Precisely | Free | `GZT0Z2BR4AC92` |

Pinned first when the live tier is enabled: `GZTDZJKVCY`.

### The fallbacks behind each stall

43 further listings sit behind the 48 on offer, as the fallback pool. A visitor is not shown these. They exist so that a stall still fills if a pick is withdrawn or turns out not to be offered in the event region, and so a promotion has somewhere to come from. They are listed here because a fallback that nobody has read is not a fallback.

**Healthcare & Life Sciences**

| Fallback listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| Germany H3 Travel Matrix | Dekart XYZ | Free | `GZSYZ43W9K16` |
| Historical Weather Data Sample | Wetter.com | Free | `GZSVZA7RAK` |
| Purchasing Power for Countries Worldwide | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOT` |
| Acxiom EMEA: Geo-Spatial Sample Data DE | Acxiom EMEA | Free | `GZSYZ5S9QG` |

**Financial Services**

| Fallback listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| MBI Sociodemographic Data for Germany | Michael Bauer International GmbH | Free | `GZSYZ12OI8L` |
| CEIC Shipping Data | CEIC Data | Free | `GZTSZRC7HRC` |
| GfK Population by Age Group & Gender Germany | NIQ-GFK | Free | `GZSYZG5AL` |
| EU Taxonomy Data \| Turnover, OPEX & CAPEX Taxonomy-Aligned & Eligible \| ESG Data Sample | Tracenable | Free | `GZTSZ36AC8J` |
| ESG & Emissions Disclosure Data | ESG Book | Free | `GZTDZ1ELJB` |
| Pan European Debit and Credit Card Transaction Datasets | Fable Data | Free | `GZ1MOZ8VQG9` |

**Retail & Consumer Goods**

| Fallback listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| Acxiom EMEA: Geo-Spatial Sample Data DE | Acxiom EMEA | Free | `GZSYZ5S9QG` |
| GfK Population by Age Group & Gender Germany | NIQ-GFK | Free | `GZSYZG5AL` |
| Demographics Data Bundle | InSights | Free | `GZTYZAPS3FT` |
| Movement Daily Activity Index 2020 (Sample) | Mapbox | Free | `GZT0ZIFQPAI` |
| Germany H3 Travel Matrix | Dekart XYZ | Free | `GZSYZ43W9K16` |

**Public Sector & Government**

| Fallback listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| MBI Sociodemographic Data for Germany | Michael Bauer International GmbH | Free | `GZSYZ12OI8L` |
| Basic Sociodemographics-Bundle for Countries Worldwide | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOH` |
| Purchasing Power for Countries Worldwide | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOT` |
| Acxiom EMEA: Geo-Spatial Sample Data DE | Acxiom EMEA | Free | `GZSYZ5S9QG` |
| Germany H3 Travel Matrix | Dekart XYZ | Free | `GZSYZ43W9K16` |
| Movement Daily Activity Index 2020 (Sample) | Mapbox | Free | `GZT0ZIFQPAI` |

**Manufacturing & Industrial**

| Fallback listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| Purchasing Power for Countries Worldwide | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOT` |
| Intelligent Event Data: Attended Events, Munich - Sample | PredictHQ | Free | `GZSTZIDI09G` |
| MBI Sociodemographic Data for Germany | Michael Bauer International GmbH | Free | `GZSYZ12OI8L` |
| GfK Population by Age Group & Gender Germany | NIQ-GFK | Free | `GZSYZG5AL` |
| Fiber Internet Coverage Dataset | GroupBWT | Free | `GZSYZ12SH0Y` |

**Energy & Utilities**

| Fallback listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| MBI Sociodemographic Data for Germany | Michael Bauer International GmbH | Free | `GZSYZ12OI8L` |
| Fiber Internet Coverage Dataset | GroupBWT | Free | `GZSYZ12SH0Y` |
| GfK Population by Age Group & Gender Germany | NIQ-GFK | Free | `GZSYZG5AL` |
| National Severe Weather Warning Service | Met Office | Free | `GZTDZJKVCU` |
| Intelligent Event Data: Attended Events, Munich - Sample | PredictHQ | Free | `GZSTZIDI09G` |

**Media, Telco & Entertainment**

| Fallback listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| GfK Population by Age Group & Gender Germany | NIQ-GFK | Free | `GZSYZG5AL` |
| Movement Daily Activity Index 2020 (Sample) | Mapbox | Free | `GZT0ZIFQPAI` |
| Acxiom EMEA: Geo-Spatial Sample Data DE | Acxiom EMEA | Free | `GZSYZ5S9QG` |
| GWI Core – Consumer Trends, Insights, and Market Data | GWI | Free | `GZ2FSZGU5YB` |
| Consumer Credit & Debit Card Transaction Data \| European Spend | Consumer Edge | Free | `GZTSZPM12Y` |
| MBI Global Area Boundaries | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOX` |

**Something else**

| Fallback listing | Provider | Access | Global name |
| --- | --- | --- | --- |
| Purchasing Power for Countries Worldwide | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOT` |
| Acxiom EMEA: Geo-Spatial Sample Data DE | Acxiom EMEA | Free | `GZSYZ5S9QG` |
| MBI Sociodemographic Data for Germany | Michael Bauer International GmbH | Free | `GZSYZ12OI8L` |
| Movement Daily Activity Index 2020 (Sample) | Mapbox | Free | `GZT0ZIFQPAI` |
| Fiber Internet Coverage Dataset | GroupBWT | Free | `GZSYZ12SH0Y` |
| Basic Sociodemographics-Bundle for Countries Worldwide | Michael Bauer International GmbH | Free | `GZSYZ7UQCDOH` |

### Which industries each listing appears in

| Listing | Industries | Appears in |
| --- | --- | --- |
| Basic Sociodemographics-Bundle for Countries Worldwide | 3 | Healthcare & Life Sciences, Retail & Consumer Goods, Media, Telco & Entertainment |
| Company data | 3 | Financial Services, Manufacturing & Industrial, Something else |
| GfK Population by Age Group & Gender Germany | 3 | Healthcare & Life Sciences, Public Sector & Government, Something else |
| MBI Sociodemographic Data for Germany | 3 | Healthcare & Life Sciences, Retail & Consumer Goods, Media, Telco & Entertainment |
| Purchasing Power for Countries Worldwide | 3 | Financial Services, Retail & Consumer Goods, Energy & Utilities |
| Fiber Internet Coverage Dataset | 2 | Public Sector & Government, Media, Telco & Entertainment |
| Germany H3 Travel Matrix | 2 | Manufacturing & Industrial, Something else |
| Historical Weather Data Sample | 2 | Energy & Utilities, Something else |
| MBI Global Area Boundaries | 2 | Public Sector & Government, Something else |
| Weather-based demand indices - Data sample | 2 | Retail & Consumer Goods, Energy & Utilities |
| World Boundaries Premium | 2 | Public Sector & Government, Something else |
| CEIC Commodities Data | 1 | Manufacturing & Industrial |
| CEIC Shipping Data | 1 | Manufacturing & Industrial |
| CEIC World Macro Economic Data | 1 | Financial Services |
| COVID-19 Epidemiological Data | 1 | Healthcare & Life Sciences |
| Consumer Credit & Debit Card Transaction Data \| European Spend | 1 | Financial Services |
| Corporate Climate Commitment ESG Data \| Net Zero, Carbon Neutrality, and Carbon Positivity | 1 | Energy & Utilities |
| Demographics Data Bundle | 1 | Healthcare & Life Sciences |
| Driving Behavior Events | 1 | Public Sector & Government |
| ESG Performance Score Core & Plus | 1 | Financial Services |
| European Broadband Markets 2017 | 1 | Media, Telco & Entertainment |
| European Public Tenders Dataset – 800+ Sources, Daily Updates, OCDS Format | 1 | Public Sector & Government |
| Global Weather & Climate Data by Pelmorex Weather Source | 1 | Energy & Utilities |
| Industry Classification Systems (NAICS, ANZSIC, ISIC, UK-SIC, etc.) | 1 | Manufacturing & Industrial |
| Intelligent Event Data: Attended Events, Munich - Sample | 1 | Media, Telco & Entertainment |
| Mastercard Audiences | 1 | Media, Telco & Entertainment |
| Overture Maps - Transportation | 1 | Manufacturing & Industrial |
| POIs - EV charging stations in Paris | 1 | Energy & Utilities |
| Population - Statistics - OECD - Free | 1 | Healthcare & Life Sciences |
| QuantCube CPI Nowcast | 1 | Financial Services |
| Retail Price Promo Sample | 1 | Retail & Consumer Goods |
| Shopping center footfall - London and Paris | 1 | Retail & Consumer Goods |

## 4. What the visitor already holds

The Data Library offers these per industry, plus a free-text option.

### Healthcare & Life Sciences

| Option | Shown underneath |
| --- | --- |
| Patient records | Structured clinical records in a PAS or EPR system |
| Clinical notes & letters | Free text - discharge summaries, referrals, correspondence |
| Referral & waiting list data | Pathways, breaches, appointment scheduling |
| Clinical trial data | Protocols, recruitment, outcomes |
| Imaging & diagnostics | Scan metadata and reports |
| Estates & operations | Beds, theatres, staffing rotas, supplies |

### Financial Services

| Option | Shown underneath |
| --- | --- |
| Transaction history | Card, payment and account movement |
| Customer & account master | KYC records, product holdings, segments |
| Positions & trades | Holdings, orders, execution history |
| Risk & capital models | Exposures, limits, stress test inputs |
| Customer communications | Call transcripts, complaints, chat logs |
| Regulatory reporting | Submissions and the reconciliations behind them |

### Retail & Consumer Goods

| Option | Shown underneath |
| --- | --- |
| Sales & till transactions | Basket-level sales by store and channel |
| Inventory & stock positions | Availability, shrink, replenishment |
| Loyalty & customer data | Membership, spend history, segments |
| Web & app clickstream | Browse, search and cart behaviour |
| Supplier & logistics data | Purchase orders, lead times, delivery performance |
| Reviews & customer service | Free text feedback, returns reasons, contact logs |

### Public Sector & Government

| Option | Shown underneath |
| --- | --- |
| Case management records | Casework across service lines |
| Policy & guidance documents | Years of PDFs, circulars and statutory guidance |
| Citizen contact & correspondence | Calls, emails, webforms, complaints |
| Assets & estates | Property, highways, fleet, maintenance |
| Finance & procurement | Budgets, spend over threshold, contracts |
| Performance & statutory returns | KPIs and central government reporting |

### Manufacturing & Industrial

| Option | Shown underneath |
| --- | --- |
| Machine & sensor telemetry | High frequency readings off the line |
| Quality & defect records | Inspection results, scrap, rework |
| Maintenance logs | Work orders and engineer free text |
| ERP & production planning | Orders, BOMs, schedules, yields |
| Supplier & inbound logistics | Component lead times and quality by supplier |
| Energy consumption | Meter data by line and site |

### Energy & Utilities

| Option | Shown underneath |
| --- | --- |
| Smart meter readings | Interval consumption at premise level |
| Network & asset data | Substations, pipes, cables, condition |
| Outage & fault records | Interruptions, causes, restoration times |
| Generation & dispatch | Output, availability, curtailment |
| Customer & billing | Accounts, tariffs, arrears, vulnerability flags |
| Field engineer reports | Free text inspection and repair notes |

### Media, Telco & Entertainment

| Option | Shown underneath |
| --- | --- |
| Viewing & listening events | Play, pause, completion by title and device |
| Subscriber & account data | Plans, churn, lifetime value |
| Content catalogue & metadata | Titles, rights, genres, availability windows |
| Network performance | Throughput, latency, coverage, faults |
| Advertising & campaign data | Impressions, fill rate, yield |
| Customer support interactions | Call transcripts and chat logs |

### Something else

| Option | Shown underneath |
| --- | --- |
| Core operational records | Whatever your main system of record holds |
| Documents & PDFs | Years of unstructured files nobody can query |
| Customer or member data | Who you serve and what they have done |
| Finance & billing | Revenue, spend, invoices |
| Emails, calls & tickets | Free text interactions |
| Device or sensor data | Anything machine-generated and high volume |

## 5. What gets built: the 9 archetypes

The workshop takes one line of free text and resolves it to exactly one archetype. The features and the first step are precomputed per archetype, so they are instant and always drawn from the curated feature list.

| Archetype | Features | Considerations available |
| --- | --- | --- |
| talk-to-my-data | Cortex Analyst, Semantic Views, Snowflake Intelligence | 5 |
| ask-my-documents | Cortex Search, AI_PARSE_DOCUMENT, Cortex Agents | 5 |
| extract-from-paperwork | AI_EXTRACT, AI_PARSE_DOCUMENT, Dynamic Tables | 5 |
| triage-and-classify | AI_CLASSIFY, Dynamic Tables, Streams | 5 |
| an-agent-that-acts | Cortex Agents, Snowflake Intelligence, Semantic Views | 5 |
| predict-what-happens-next | ML Forecasting, ML Anomaly Detection, Snowflake Notebooks | 5 |
| join-the-silos | Dynamic Tables, Snowflake Marketplace, Semantic Views | 5 |
| share-without-copying | Secure Data Sharing, Snowflake Marketplace, Dynamic Tables | 5 |
| watch-it-live | Snowpipe Streaming, Dynamic Tables, Streams | 5 |

### The first step printed for each

- **talk-to-my-data** - Write down the three questions people ask most, then model just the tables those need.
- **ask-my-documents** - Put fifty representative documents on a stage and see what the parser returns before building anything.
- **extract-from-paperwork** - List the fields you actually need, then test extraction on your ugliest ten documents rather than your cleanest.
- **triage-and-classify** - Agree the categories with the people who act on them, then hand-label two hundred examples as your yardstick.
- **an-agent-that-acts** - Pick one action worth automating, and write down exactly what the agent must never do.
- **predict-what-happens-next** - Check you have enough history for the thing you want to predict before modelling anything.
- **join-the-silos** - Find the one key that links your two most important systems, and check how often it is missing.
- **share-without-copying** - Pick one dataset and one partner, and write down exactly which columns they may see.
- **watch-it-live** - Define the one event worth reacting to, and how quickly someone must know about it.

## 6. How the data gets into Snowflake

Each platform tapped on the letter prints a concrete route into the blueprint.

| Platform | Route printed |
| --- | --- |
| Microsoft / Azure | Openflow has a first-party connector for Azure Blob Storage and SQL Server. For Fabric or OneLake, register the Iceberg tables through a catalog integration and query them in place - no copy. |
| AWS | Point an external stage at the S3 bucket with a storage integration, then Snowpipe for continuous load. If the data is already Iceberg in Glue, use a catalog integration and leave it where it is. |
| Google Cloud | A storage integration over the GCS bucket plus an external stage. BigQuery data moves cleanly as Parquet exported to GCS, or through Openflow if you need it on a schedule. |
| Oracle | Openflow's Oracle connector does change data capture, so you get an ongoing replica rather than a nightly dump. Start with the handful of tables the proof of concept actually reads. |
| SAP | Either the SAP connector for Snowflake, or SAP Business Data Cloud sharing the data as Iceberg that Snowflake reads without a copy. The second route is usually faster to stand up. |
| On-premise / our own servers | Openflow can run inside your network and push out, so nothing has to be exposed inbound. For a first proof of concept, a one-off bulk load of a representative extract is usually enough. |
| SaaS apps (Salesforce, Workday, etc.) | Openflow has connectors for the common SaaS sources, and the Marketplace carries some of them as ready-made shares. Check the Marketplace first - it is the cheaper answer when it exists. |
| Already in Snowflake | Nothing to move. Point the proof of concept at the existing tables and spend the saved time on the model and the interface instead. |
| Not sure yet | Worth ten minutes with whoever owns the source before you build. The answer changes the effort more than any other decision here. |

### When more than one is tapped

| Selection | What the blueprint prints |
| --- | --- |
| One platform | That route |
| Several named platforms | Each route, in the order listed above, so the document does not depend on tap order |
| Not sure yet, alone | Its own line, no route |
| Not sure yet, with a named platform | The named platform only |
| More than four platforms | The first four in the order listed above |

Already in Snowflake is not an exclusive answer: an estate can be part in Snowflake and part elsewhere. When it is picked alongside a named platform the blueprint prints this instead of "nothing to move": **Some of it is already here, so the proof of concept starts on those tables today while the rest lands alongside them.**

These rules are applied in the browser as the visitor taps, and again on the server when the blueprint is built.

## 7. How each answer is produced

| Stop | Model transport | Notes |
| --- | --- | --- |
| The Data Library | complete | A single fast completion that names the selection back. |
| The Marketplace | complete | A single fast completion that names the selection back. |
| The Workshop | exec | Agentic. CoCo's working is shown on screen as it arrives. |
| The Postbox | - | No model turn. Runs the QA review, writes the document, returns the fixed line above. |

Every turn has a wall-clock ceiling. The quick stops are held to 30s, because a proven model answers in about two and the only thing that ever reaches the ceiling is a fault; the Workshop is allowed 60s, because it is the one agentic turn and legitimately takes twenty to thirty. Past the ceiling the visitor is served the precomputed archetype content instead of a slower sentence, so the document is complete either way.

One model call is in flight at a time. A second caller waits, so one visitor's content can never appear in another visitor's document.

The transport named above is the first thing tried, not the only one. Beneath each stop sit four layers, and every one of them falls through to the next:

1. A warm agent, held open between visitors so the startup cost is paid once when the booth opens rather than once per visitor.
2. A cold one-shot agent process, which pays that startup on every call.
3. A single non-agentic completion in Snowflake.
4. The archetype's own precomputed content, which needs no model at all and is present in this repository.

So the visitor is served something whichever layers are unavailable. The booth checks at startup whether this laptop's Cortex Code can hold a warm agent open, states the answer in the console, and uses the next layer down for every turn if it cannot.

The closed lists in this document reach the model as text inside the prompt. The model picks from them and reflects them back; it is never asked to invent a feature, a listing or a fact.

## 8. Review and delivery

Before the document is written, it is reviewed. Deterministic checks always run and repair what is fixable from the closed lists: features that do not resolve to a documentation link are dropped, platforms are re-normalised, the sovereignty section is required when a residency rule was given, and a list of banned words is removed. Every change is recorded with its before and after.

One further check asks a model whether the proof of concept addresses the problem the visitor described. It never blocks delivery.

The visitor leaves with a Word document, reached by scanning a QR code on screen. The link lasts 7 days. There is no email and no HTML page: the document is the only artifact.

## 9. Configuration

The flags that change what a visitor experiences.

| Setting | Value | Effect |
| --- | --- | --- |
| `locations.marketplace.discovery` | `manual` | The curated listings in section 3 are served |
| `marketplace.agentic.enabled` | `true` | Agentic listing search is on |
| `qa.enabled` | `true` | Blueprint review runs before delivery |
| `qa.model_review` | `true` | Relevance check included in the review |
| `delivery.transport` | `qr` | Delivery is by QR code to a staged document |
| `ask.enabled` | `false` | The optional free-question stop is not offered |
| `event.marketplace_region` | `AWS_EU_WEST_2` | Biases which Marketplace datasets are recommended |
| `event.time_limit_seconds` | `300` | The visit length the booth is built for |

### Constraints to be aware of

- Listing selection is weighted for the United Kingdom: 19 preference terms and 20 demotion terms. A room in another country needs these re-weighted.
- 5 listings appear in three or more industries, the most reused being GfK Population by Age Group & Gender Germany, MBI Sociodemographic Data for Germany. A visitor who has seen the booth before may be offered the same dataset again.
- A listing is offerable if the catalogue still carries it, it is offered in the EVENT’s region, and a visitor can obtain it directly - not by-request and not discover-only. It is deliberately NOT judged on whether this account could import it: that flag answers “can THIS account attach it”, and every booth account is in one region while the three events are in three, so using it would reject listings the visitor can attach perfectly well.
- A stall widens its pool by borrowing from other industries when a listing matches what the visitor typed, which is right for data that travels - weather, boundaries, addresses, population, company registrations - and wrong for sector-specific reference data. 14 listings are protected from that for this venue and are offered in their own stall only.
- The curated six always win their own stall. Ranking changes the ORDER a visitor sees them in, and borrowed listings compete only for slots the six do not fill.
- No pinned fallback for: Healthcare & Life Sciences, Financial Services, Manufacturing & Industrial, Media, Telco & Entertainment. These industries rely entirely on the curated list in section 3.
- The industry does not weight which archetype a visitor is routed to.
- The data a visitor holds DOES narrow which datasets are suggested: each listing is tagged with what it is for and each library shelf with what it is, and selection intersects the two. There is no tag for unstructured text, because no curated listing serves it - a visitor whose problem is documents is ranked on their own words and their sector alone.

