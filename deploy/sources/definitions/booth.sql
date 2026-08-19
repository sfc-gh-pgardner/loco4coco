-- Loco4CoCo booth objects.
--
-- Only DEFINE, GRANT and ATTACH statements are permitted in a DCM definition
-- file, and every object must be fully qualified. DEFINE behaves as
-- CREATE OR ALTER, so this file is the desired end state: removing a statement
-- DROPS the object on the next deploy.
--
-- Resource monitors are NOT a supported DEFINE entity, so LOCO4COCO_RM lives in
-- hooks/post_hook.sql instead. That is Snowflake's documented pattern for
-- unsupported object types.

-- ---------------------------------------------------------------- containers

DEFINE DATABASE {{db}}
  COMMENT = 'Loco4CoCo booth activation. Managed by the LOCO4COCO_BOOTH DCM project.';

DEFINE SCHEMA {{db}}.{{schema}}
  COMMENT = 'Visitor sessions, per-turn telemetry and generated blueprints.';

-- ---------------------------------------------------------------- compute
-- X-Small, 60s auto-suspend. INITIALLY_SUSPENDED is immutable in DCM, which
-- suits the default-posture-off cost rule: the warehouse only runs when
-- something actually needs it.
--
-- Generation is deliberately NOT pinned. The London warehouse was created as
-- STANDARD_GEN_2 (which bills ~1.35 credits/hour rather than 1.0), and
-- RESOURCE_CONSTRAINT cannot be used to change it - Snowflake rejects it and
-- directs you to a GENERATION property whose accepted syntax did not work here
-- either. At one INSERT per visitor the difference is a rounding error, so this
-- is left as-is on purpose rather than chased. A NEW account gets whatever the
-- default generation is, which is fine.

DEFINE WAREHOUSE {{wh}}
  WITH
    warehouse_size = '{{wh_size}}'
    auto_suspend = {{auto_suspend}}
    auto_resume = TRUE
    initially_suspended = TRUE
    comment = 'Loco4CoCo booth. Tiny workload; kept small and fast to suspend.';

-- ---------------------------------------------------------------- stage
-- ENCRYPTION type is IMMUTABLE in DCM, and SNOWFLAKE_SSE is what makes
-- GET_PRESIGNED_URL work. Getting this wrong at creation cannot be patched
-- later, so it is pinned here rather than left to a default.

DEFINE STAGE {{db}}.{{schema}}.BLUEPRINTS
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
  DIRECTORY = (ENABLE = TRUE)
  COMMENT = 'Generated .docx blueprints. Presigned for download, 7 day max.';

-- ---------------------------------------------------------------- sessions
-- One row per visitor. Shaped around what the game actually knows: the v1 table
-- carried PAIN_CHOSEN / DREAM_CHOSEN / AUDIENCE / ROLE_STATED, which the game
-- can never populate, and lacked company, industry, Marketplace picks and cost.

DEFINE TABLE {{db}}.{{schema}}.SESSIONS (
  SESSION_ID          TEXT          COMMENT 'Joins to TURNS.SESSION_ID',
  SESSION_TS          TIMESTAMP_LTZ COMMENT 'When the visitor finished',
  EVENT_CITY          TEXT,
  LANGUAGE_CODE       TEXT,

  FIRST_NAME          TEXT,
  COMPANY             TEXT,
  INDUSTRY            TEXT          COMMENT 'Inferred from company, confirmable by the visitor',
  EMAIL               TEXT,

  DATA_HELD           ARRAY         COMMENT 'Library picks - data they already hold',
  MARKETPLACE_JOINED  ARRAY         COMMENT 'Marketplace picks - data to enhance it',

  POC_ARCHETYPE       TEXT          COMMENT 'One of the ten archetypes; drives the guide',
  POC_NAME            TEXT,
  POC_SUMMARY         TEXT,
  GUIDE_FORKED        TEXT,
  GUIDE_URL           TEXT,
  FEATURES            ARRAY,
  READINESS_SCORE     NUMBER(2,0)   COMMENT 'Strict 1-5, INTERNAL ONLY - never shown to the visitor; used to rank leads warmest-first',
  FIRST_STEP          TEXT,

  DOCUMENT_URL        TEXT          COMMENT 'Presigned .docx link, expires after 7 days',
  DELIVERY_STATUS     TEXT          COMMENT 'QUEUED | DRAFTED | SENT | FAILED - updated by the ops drain',

  DURATION_SECONDS    NUMBER(6,0)   COMMENT 'Wall clock from intake to postbox',
  COCO_SECONDS        NUMBER(6,0)   COMMENT 'Of which spent waiting on Cortex Code',
  INPUT_TOKENS        NUMBER(12,0),
  OUTPUT_TOKENS       NUMBER(12,0),

  SE_OPERATOR         TEXT,
  NOTES               TEXT,

  -- Appended, not inserted: CREATE OR ALTER TABLE (which DEFINE runs) rejects
  -- adding a column anywhere but the end. Replaces the old WEAKEST_POINT.
  CONSIDERATIONS      ARRAY         COMMENT 'What the visitor is told to think about, in place of a score',

  -- Also appended. These two are the qualification payload: the problem in the
  -- visitor's OWN WORDS, and the platforms their data sits on. Everything else
  -- in this table is a pick from a list we wrote; these are the only columns an
  -- SDR can quote back to them.
  PROBLEM_STATEMENT   TEXT          COMMENT 'Two sentences, typed by the visitor at the letter stage',
  PLATFORMS           ARRAY         COMMENT 'Where the data lives today - decides the integration path'
)
  COMMENT = 'One row per booth visitor.';

-- ---------------------------------------------------------------- turns
-- One row per location per visitor. This is what makes "which beat is slowest
-- and most expensive" answerable - a live question, since the postbox is a ~50s
-- wait and it lands last in the five-minute budget.

DEFINE TABLE {{db}}.{{schema}}.TURNS (
  SESSION_ID        TEXT,
  TURN_TS           TIMESTAMP_LTZ,
  LOCATION          TEXT          COMMENT 'library | marketplace | workshop | postbox',
  VISITOR_INPUT     TEXT          COMMENT 'Their selection or sentence',
  REPLY             TEXT,
  DURATION_SECONDS  NUMBER(6,0),
  INPUT_TOKENS      NUMBER(12,0),
  OUTPUT_TOKENS     NUMBER(12,0),
  CACHE_READ_TOKENS NUMBER(12,0),
  SUCCEEDED         BOOLEAN
)
  COMMENT = 'Per-turn latency and token cost for each visitor.';
