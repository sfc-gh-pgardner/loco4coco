-- What visitors actually wanted, for curating the next event.
--
-- MARKETPLACE_JOINED is an ARRAY of listing titles, so it flattens rather than
-- splitting a delimited string.

-- Which listings visitors chose to join. A pick nobody ever takes is a slot worth
-- reusing; a pick taken in every city is one to keep in all three profiles.
SELECT EVENT_CITY, f.VALUE::string AS LISTING, COUNT(*) AS TIMES_JOINED
FROM LOCO4COCO.BOOTH.SESSIONS s,
     LATERAL FLATTEN(input => s.MARKETPLACE_JOINED) f
GROUP BY ALL
ORDER BY TIMES_JOINED DESC;

-- Which industries turned up. If the stall keeps drawing an industry you have thin
-- data for, that is a curation gap rather than bad luck.
SELECT EVENT_CITY, INDUSTRY, COUNT(*) AS VISITORS
FROM LOCO4COCO.BOOTH.SESSIONS
GROUP BY ALL
ORDER BY VISITORS DESC;

-- Which POC shapes came up. This is what to build demo assets for next.
SELECT POC_ARCHETYPE, COUNT(*) AS VISITORS,
       ARRAY_AGG(DISTINCT INDUSTRY) AS FROM_INDUSTRIES
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE COALESCE(POC_ARCHETYPE, '') <> ''
GROUP BY ALL
ORDER BY VISITORS DESC;

-- Visitors who typed into "something else" rather than picking from the six. Their
-- words are the strongest signal that the curated stall missed them.
SELECT EVENT_CITY, INDUSTRY, FIRST_NAME, COMPANY, PROBLEM_STATEMENT,
       MARKETPLACE_JOINED
FROM LOCO4COCO.BOOTH.SESSIONS
WHERE ARRAY_SIZE(COALESCE(MARKETPLACE_JOINED, ARRAY_CONSTRUCT())) = 0
ORDER BY SESSION_TS DESC;
