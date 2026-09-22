-- Did the booth behave? Run during the event, not just after it.

-- Did the handover reach people. Anything other than DELIVERED is a visitor who
-- left with nothing, which is the one failure the stand cannot absorb.
SELECT DELIVERY_STATUS, COUNT(*) AS N,
       ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS PCT
FROM LOCO4COCO.BOOTH.SESSIONS
GROUP BY ALL
ORDER BY N DESC;

-- Did the five minutes hold. COCO_SECONDS is the part spent waiting on a model,
-- which is the number to watch: the budget is 300s and waiting is what we control.
SELECT EVENT_CITY,
       COUNT(*)                        AS VISITS,
       ROUND(AVG(DURATION_SECONDS))    AS AVG_VISIT_S,
       MAX(DURATION_SECONDS)           AS WORST_VISIT_S,
       ROUND(AVG(COCO_SECONDS))        AS AVG_WAIT_S,
       MAX(COCO_SECONDS)               AS WORST_WAIT_S
FROM LOCO4COCO.BOOTH.SESSIONS
GROUP BY ALL
ORDER BY VISITS DESC;

-- Visits that overran the budget. One is bad luck; a pattern means the model has
-- slowed down and the fallback is carrying the booth.
SELECT TO_CHAR(SESSION_TS, 'HH24:MI') AS SEEN, FIRST_NAME, COMPANY,
       DURATION_SECONDS, COCO_SECONDS
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE DURATION_SECONDS > 300 OR COCO_SECONDS > 120
ORDER BY DURATION_SECONDS DESC;

-- Which beat is slow, and whether any turn failed outright. A LOCATION with a high
-- average is the one to look at; SUCCEEDED = FALSE means the model did not answer
-- and the visitor saw a fallback.
SELECT LOCATION,
       COUNT(*)                              AS TURNS,
       ROUND(AVG(DURATION_SECONDS), 1)       AS AVG_S,
       MAX(DURATION_SECONDS)                 AS WORST_S,
       SUM(IFF(SUCCEEDED, 0, 1))             AS FAILED
FROM LOCO4COCO.BOOTH.TURNS
GROUP BY ALL
ORDER BY AVG_S DESC;

-- Quality flags raised by the reviewing model, so a weak blueprint is caught before
-- the follow-up rather than after it.
SELECT TO_CHAR(SESSION_TS, 'YYYY-MM-DD HH24:MI') AS SEEN, FIRST_NAME, COMPANY,
       QA_PASSED, QA_REPAIRS, QA_RELEVANT, QA_NOTE
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE QA_PASSED IS DISTINCT FROM TRUE OR COALESCE(QA_NOTE, '') <> ''
ORDER BY SESSION_TS DESC;

-- What the reviewer actually checked and changed, per finding.
SELECT f.FINDING_TS, s.FIRST_NAME, s.COMPANY, f.CHECK_NAME, f.SEVERITY,
       f.REPAIRED, f.DETAIL, f.BEFORE_VAL, f.AFTER_VAL
FROM LOCO4COCO.BOOTH.QA_FINDINGS f
LEFT JOIN LOCO4COCO.BOOTH.SESSIONS s ON s.SESSION_ID = f.SESSION_ID
ORDER BY f.FINDING_TS DESC
LIMIT 50;

-- Is the booth writing at all. If this returns nothing during an event, the account
-- write path has failed and every visitor so far is unrecorded.
SELECT MAX(SESSION_TS) AS LAST_VISITOR,
       TIMESTAMPDIFF('minute', MAX(SESSION_TS), CURRENT_TIMESTAMP()) AS MINUTES_AGO,
       COUNT(*) AS TOTAL_SESSIONS
FROM LOCO4COCO.BOOTH.SESSIONS;
