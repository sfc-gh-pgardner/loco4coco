-- The lead list: one row per visitor, for SDR follow-up.
--
--     snow sql -c <conn> --enable-templating NONE -f sql_statements/01-lead-list.sql
--
-- PROBLEM_STATEMENT is what they said in their own words, and it is the most useful
-- column in the table for a follow-up: it is the thing they came to the stand about.

SELECT TO_CHAR(SESSION_TS, 'YYYY-MM-DD HH24:MI') AS SEEN,
       EVENT_CITY,
       FIRST_NAME,
       COMPANY,
       COMPANY_COUNTRY,
       INDUSTRY,
       PROBLEM_STATEMENT,
       POC_NAME,
       POC_ARCHETYPE          AS ARCHETYPE,
       FEATURES               AS SNOWFLAKE_FEATURES_SHOWN,
       MARKETPLACE_JOINED     AS LISTINGS_THEY_PICKED,
       FIRST_STEP,
       GUIDE_URL,
       DOCUMENT_URL,
       DELIVERY_STATUS
FROM LOCO4COCO.BOOTH.SESSIONS
ORDER BY SESSION_TS DESC;

-- Just today, when you are working the stand and want the morning's conversations.
SELECT TO_CHAR(SESSION_TS, 'HH24:MI') AS SEEN, FIRST_NAME, COMPANY, INDUSTRY,
       POC_NAME, DELIVERY_STATUS
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE SESSION_TS >= CURRENT_DATE()
ORDER BY SESSION_TS DESC;

-- Leads worth calling first: they described a real problem, took a blueprint, and
-- the handover reached them. A visitor with no problem statement was probably a
-- passer-by trying the game.
SELECT FIRST_NAME, COMPANY, INDUSTRY, PROBLEM_STATEMENT, POC_NAME, GUIDE_URL
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE DELIVERY_STATUS = 'DELIVERED'
  AND LENGTH(COALESCE(PROBLEM_STATEMENT, '')) > 40
  AND COALESCE(COMPANY, '') <> ''
ORDER BY LENGTH(PROBLEM_STATEMENT) DESC;
