-- Post-hook: objects DCM Projects cannot define.
--
-- Snowflake's documented pattern for unsupported entity types is a separate
-- templated script run after the deploy:
--
--   snow sql -f deploy/hooks/post_hook.sql --enable-templating JINJA \
--     -D wh=LOCO4COCO_WH -c <connection>
--
-- bootstrap.py runs this for you with the values from manifest.yml.
--
-- Idempotent by design: safe to re-run on every deploy.
--
-- ─────────────────────────────────────────────────────────────────────────────
-- THERE IS DELIBERATELY NO RESOURCE MONITOR, AND NOTHING THAT CAN STOP THE GAME.
--
-- The booth runs all day with a queue of people in front of it. A credit limit
-- that suspends the warehouse does not save money in any meaningful sense - it
-- ends the activation, in public, mid-visit, with a stranger watching. The cost
-- of that is far higher than the compute it would have saved: an X-Small
-- warehouse doing a handful of COMPLETE calls per visitor is not where an account
-- gets into trouble.
--
-- This has been got wrong twice, in opposite directions, so it is written down
-- rather than left to judgement:
--
--   1. A monitor was created with DO NOTIFY triggers only. On an event account
--      the pool user usually has no email address, and Snowflake silently DROPS
--      notify triggers when there are no notify users - so the monitor reported a
--      quota, fired nothing, warned nobody, and looked like a guardrail.
--   2. A DO SUSPEND trigger was then added to make it real. That made it
--      genuinely dangerous: it could have cut the stand off mid-visit.
--
-- Neither is wanted. Cost is observed, not enforced:
--
--   * game/cost.jsonl records every model call the booth makes, per visitor.
--   * sql_statements/03-event-health.sql shows the per-visit and per-turn spend.
--   * SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY has the credits, after
--     the usual latency.
--
-- If you genuinely need a cap on a shared account, put it on a DIFFERENT
-- warehouse and leave this one alone. Do not bind a monitor to LOCO4COCO_WH.
-- ─────────────────────────────────────────────────────────────────────────────

-- Make sure no monitor is attached, including one left behind by an earlier
-- deploy of this project that did create one. UNSET is safe when there is none.
ALTER WAREHOUSE {{ wh }} UNSET RESOURCE_MONITOR;

-- Proof, not assumption: resource_monitor must read null, and the warehouse must
-- be able to come back on its own after the 60s idle suspend.
SHOW WAREHOUSES LIKE '{{ wh }}';
SELECT "name", "resource_monitor", "auto_suspend", "auto_resume"
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));
