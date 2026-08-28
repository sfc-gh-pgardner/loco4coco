-- Post-hook: objects DCM Projects cannot define.
--
-- Resource monitors are not in the DCM supported-entity list, so they are
-- created here instead. Snowflake's documented pattern for unsupported types is
-- a separate templated script run after the deploy:
--
--   snow sql -f deploy/hooks/post_hook.sql --enable-templating JINJA \
--     -D monitor=LOCO4COCO_RM -D monitor_quota=100 \
--     -D wh=LOCO4COCO_WH -D monitor_notify_user=PGARDNER -c <connection>
--
-- bootstrap.py runs this for you with the values from manifest.yml.
--
-- Idempotent by design: safe to re-run on every deploy.

-- notify_users has been silently empty on a hand-created monitor before, which
-- makes every trigger useless. It is set explicitly here and verified below.
CREATE RESOURCE MONITOR IF NOT EXISTS {{ monitor }}
  WITH
    CREDIT_QUOTA = {{ monitor_quota }}
    FREQUENCY = MONTHLY
    START_TIMESTAMP = IMMEDIATELY
    NOTIFY_USERS = ({{ monitor_notify_user }})
    TRIGGERS
      ON 75 PERCENT DO NOTIFY
      ON 90 PERCENT DO NOTIFY
      ON 100 PERCENT DO NOTIFY;

-- Re-assert the settings in case the monitor already existed with other values.
-- Notify-only by design: the booth warns but never suspends the warehouse, so a
-- busy stand is never cut off mid-visit. The triggers are re-set here too, so a
-- monitor created earlier with SUSPEND triggers is brought back to notify-only.
ALTER RESOURCE MONITOR {{ monitor }} SET
  CREDIT_QUOTA = {{ monitor_quota }}
  NOTIFY_USERS = ({{ monitor_notify_user }})
  TRIGGERS
    ON 75 PERCENT DO NOTIFY
    ON 90 PERCENT DO NOTIFY
    ON 100 PERCENT DO NOTIFY;

-- Bind it to the booth warehouse. Without this the quota monitors nothing.
ALTER WAREHOUSE {{ wh }} SET RESOURCE_MONITOR = {{ monitor }};

-- Proof, not assumption: a monitor with no notify_users cannot warn anyone.
SHOW RESOURCE MONITORS LIKE '{{ monitor }}';
SELECT "name", "credit_quota", "notify_users", "level"
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));
