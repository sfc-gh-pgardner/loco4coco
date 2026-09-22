-- SDR handover queries for a Loco for CoCo event.
--
-- Every visitor leaves a row in LOCO4COCO.BOOTH.SESSIONS and one row per turn in
-- TURNS. These are the questions an SDR or SE actually asks afterwards. Run them
-- against the event account BEFORE it is torn down: the accounts are ephemeral,
-- so export anything you want to keep.
--
--     snow sql --connection <conn> --enable-templating NONE -f deploy/handover.sql

-- 1. The lead list. One row per visitor, newest first - who they were, what they
--    came in with, and what they left holding.
SELECT TO_CHAR(SESSION_TS, 'YYYY-MM-DD HH24:MI') AS SEEN,
       EVENT_CITY, FIRST_NAME, COMPANY, INDUSTRY, COMPANY_COUNTRY,
       PROBLEM_STATEMENT, POC_NAME, POC_ARCHETYPE, GUIDE_URL,
       DELIVERY_STATUS, DURATION_SECONDS
FROM LOCO4COCO.BOOTH.SESSIONS
ORDER BY SESSION_TS DESC;

-- 2. What the event was interested in. Which archetypes came up most tells you
--    what to follow up with, and which industries showed up tells you whether the
--    stall was reaching the audience you wanted.
SELECT EVENT_CITY, INDUSTRY, POC_ARCHETYPE, COUNT(*) AS VISITORS
FROM LOCO4COCO.BOOTH.SESSIONS
GROUP BY ALL
ORDER BY VISITORS DESC, EVENT_CITY;

-- 3. Which Marketplace listings visitors chose to join. MARKETPLACE_JOINED is an
--    ARRAY of the titles they ticked, so this is the demand signal for curation: a
--    listing nobody picks is a slot worth reusing next event.
SELECT EVENT_CITY, f.VALUE::string AS LISTING, COUNT(*) AS TIMES_JOINED
FROM LOCO4COCO.BOOTH.SESSIONS s,
     LATERAL FLATTEN(input => s.MARKETPLACE_JOINED) f
GROUP BY ALL
ORDER BY TIMES_JOINED DESC;

-- 4. Did the handover actually reach them. DELIVERED means the document was
--    staged and the QR resolves; anything else is a visitor who left with nothing.
SELECT DELIVERY_STATUS, COUNT(*) AS N,
       ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS PCT
FROM LOCO4COCO.BOOTH.SESSIONS
GROUP BY ALL
ORDER BY N DESC;

-- 5. Whether the five minutes held. DURATION_SECONDS is the whole visit and
--    COCO_SECONDS is how much of it was spent waiting on a model, which is the
--    number to watch: the budget is 300s and waiting is the part we control.
SELECT EVENT_CITY,
       COUNT(*) AS VISITS,
       ROUND(AVG(DURATION_SECONDS)) AS AVG_VISIT_S,
       MAX(DURATION_SECONDS) AS WORST_VISIT_S,
       ROUND(AVG(COCO_SECONDS)) AS AVG_WAIT_S,
       MAX(COCO_SECONDS) AS WORST_WAIT_S
FROM LOCO4COCO.BOOTH.SESSIONS
GROUP BY ALL
ORDER BY VISITS DESC;

-- 6. Quality flags raised by the reviewing model, so a weak blueprint can be
--    spotted before the follow-up rather than after it.
SELECT EVENT_CITY, FIRST_NAME, COMPANY, QA_PASSED, QA_REPAIRS, QA_RELEVANT, QA_NOTE
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE QA_PASSED IS DISTINCT FROM TRUE OR COALESCE(QA_NOTE, '') <> ''
ORDER BY SESSION_TS DESC;

-- 7. The conversation itself, for one visitor. Useful when an SE picks up a lead
--    and wants to know what was actually said rather than just the outcome. One
--    row per turn, holding both sides of it.
SELECT t.TURN_TS, t.LOCATION, t.VISITOR_INPUT, t.REPLY,
       t.DURATION_SECONDS, t.SUCCEEDED
FROM LOCO4COCO.BOOTH.TURNS t
JOIN LOCO4COCO.BOOTH.SESSIONS s ON s.SESSION_ID = t.SESSION_ID
WHERE s.COMPANY = 'Northwind Energy'     -- change me
ORDER BY t.TURN_TS;
