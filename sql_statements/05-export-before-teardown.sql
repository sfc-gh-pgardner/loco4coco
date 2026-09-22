-- RUN THIS BEFORE THE EVENT ACCOUNT IS DESTROYED.
--
-- Event accounts are assigned from a pool per event and torn down afterwards.
-- Nothing in them survives. Run this, save the output somewhere durable, and do it
-- more than once if the event runs over several days.
--
--     snow sql -c <conn> --enable-templating NONE --format csv \
--         -f sql_statements/05-export-before-teardown.sql > swt-<city>-leads.csv

-- Everything about every visitor, flattened for a spreadsheet. Arrays are joined so
-- the CSV stays one row per visitor.
SELECT SESSION_ID,
       SESSION_TS,
       EVENT_CITY,
       LANGUAGE_CODE,
       SE_OPERATOR                                  AS BOOTH_ACCOUNT,
       FIRST_NAME,
       COMPANY,
       COMPANY_COUNTRY,
       INDUSTRY,
       RESIDENCY,
       ARRAY_TO_STRING(PLATFORMS, '; ')             AS PLATFORMS,
       PROBLEM_STATEMENT,
       ARRAY_TO_STRING(DATA_HELD, '; ')             AS DATA_HELD,
       ARRAY_TO_STRING(MARKETPLACE_JOINED, '; ')    AS LISTINGS_JOINED,
       POC_NAME,
       POC_ARCHETYPE,
       POC_SUMMARY,
       ARRAY_TO_STRING(FEATURES, '; ')              AS FEATURES,
       ARRAY_TO_STRING(CONSIDERATIONS, '; ')        AS CONSIDERATIONS,
       FIRST_STEP,
       GUIDE_FORKED,
       GUIDE_URL,
       DOCUMENT_URL,
       DELIVERY_STATUS,
       DURATION_SECONDS,
       COCO_SECONDS,
       INPUT_TOKENS,
       OUTPUT_TOKENS,
       QA_PASSED,
       QA_REPAIRS,
       QA_RELEVANT,
       QA_NOTE,
       NOTES
FROM LOCO4COCO.BOOTH.SESSIONS
ORDER BY SESSION_TS;

-- The conversations too, if you want the detail rather than just the outcomes.
SELECT t.SESSION_ID, s.FIRST_NAME, s.COMPANY, t.TURN_TS, t.LOCATION,
       t.VISITOR_INPUT, t.REPLY, t.DURATION_SECONDS, t.SUCCEEDED
FROM LOCO4COCO.BOOTH.TURNS t
LEFT JOIN LOCO4COCO.BOOTH.SESSIONS s ON s.SESSION_ID = t.SESSION_ID
ORDER BY t.SESSION_ID, t.TURN_TS;

-- Confirm you exported everything: compare this count against your saved file.
SELECT COUNT(*) AS SESSIONS_TO_EXPORT,
       MIN(SESSION_TS) AS FIRST_VISITOR,
       MAX(SESSION_TS) AS LAST_VISITOR
FROM LOCO4COCO.BOOTH.SESSIONS;
