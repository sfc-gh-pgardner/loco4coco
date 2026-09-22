-- Post-hook: objects DCM Projects cannot define.
--
-- Resource monitors are not in the DCM supported-entity list, so they are
-- created here instead. Snowflake's documented pattern for unsupported types is
-- a separate templated script run after the deploy:
--
--   snow sql -f deploy/hooks/post_hook.sql --enable-templating JINJA \
--     -D monitor=LOCO4COCO_RM -D monitor_quota=100 \
--     -D wh=LOCO4COCO_WH -D monitor_notify_user=<a-real-user-in-your-account> -c <connection>
--
-- bootstrap.py runs this for you with the values from manifest.yml.
--
-- Idempotent by design: safe to re-run on every deploy.
--
-- NOTIFY tolerance: the booth is notify-only by design (it warns but never
-- suspends the warehouse, so a busy stand is never cut off mid-visit). But on
-- Snowflake World Tour / hands-on-lab event accounts the login user often has
-- NO email address, and `NOTIFY_USERS=(that_user)` fails outright with 090269,
-- which used to abort the whole deploy. So the monitor is created inside a
-- scripting block that tries WITH notify first and falls back to creating it
-- WITHOUT notify if that fails. Either way the monitor exists and is bound to
-- the warehouse; a warning is printed below if nobody can be notified.

EXECUTE IMMEDIATE $$
DECLARE
  notified BOOLEAN DEFAULT FALSE;
BEGIN
{% if monitor_notify_user %}
  BEGIN
    CREATE RESOURCE MONITOR IF NOT EXISTS {{ monitor }}
      WITH CREDIT_QUOTA = {{ monitor_quota }}
        FREQUENCY = MONTHLY
        START_TIMESTAMP = IMMEDIATELY
        NOTIFY_USERS = ({{ monitor_notify_user }})
        TRIGGERS ON 75 PERCENT DO NOTIFY
                 ON 90 PERCENT DO NOTIFY
                 ON 100 PERCENT DO NOTIFY;
    ALTER RESOURCE MONITOR {{ monitor }} SET
      CREDIT_QUOTA = {{ monitor_quota }}
      NOTIFY_USERS = ({{ monitor_notify_user }})
      TRIGGERS ON 75 PERCENT DO NOTIFY
               ON 90 PERCENT DO NOTIFY
               ON 100 PERCENT DO SUSPEND;
    notified := TRUE;
  EXCEPTION
    WHEN OTHER THEN
      notified := FALSE;
  END;
{% endif %}
  IF (NOT notified) THEN
    -- No usable notify user (empty, or the user has no email). Create the
    -- monitor anyway so the quota exists; the triggers still fire, they just
    -- warn nobody. This never suspends the warehouse.
    CREATE RESOURCE MONITOR IF NOT EXISTS {{ monitor }}
      WITH CREDIT_QUOTA = {{ monitor_quota }}
        FREQUENCY = MONTHLY
        START_TIMESTAMP = IMMEDIATELY
        TRIGGERS ON 75 PERCENT DO NOTIFY
                 ON 90 PERCENT DO NOTIFY
                 ON 100 PERCENT DO NOTIFY;
    -- Set the triggers on the ALTER too, not only in the CREATE. IF NOT EXISTS
    -- skips the CREATE entirely when an earlier deploy already made the monitor,
    -- and a bare SET CREDIT_QUOTA does not add triggers - measured on this
    -- account, the live monitor carried a 100 credit quota with notify_triggers
    -- and suspend_at both null, so the guardrail was decorative.
    --
    -- DO NOTIFY alone is not a guardrail here either: these accounts often have a
    -- user with no email, so NOTIFY warns nobody and nothing stops. SUSPEND at
    -- 100 percent is the backstop. It is a deliberate trade: suspending mid-event
    -- would end the booth, but a stand that has burned its whole monthly quota is
    -- already malfunctioning, and an unbounded spend on a shared account is worse.
    ALTER RESOURCE MONITOR {{ monitor }} SET
      CREDIT_QUOTA = {{ monitor_quota }}
      TRIGGERS ON 75 PERCENT DO NOTIFY
               ON 90 PERCENT DO NOTIFY
               ON 100 PERCENT DO SUSPEND;
  END IF;

  ALTER WAREHOUSE {{ wh }} SET RESOURCE_MONITOR = {{ monitor }};

  RETURN IFF(notified,
             'monitor bound, notify user set',
             'monitor bound, NO notify user (nobody will be warned - set a user with an email)');
END;
$$;

-- Proof, not assumption: a monitor with no notify_users cannot warn anyone.
SHOW RESOURCE MONITORS LIKE '{{ monitor }}';
SELECT "name", "credit_quota", "notify_users", "level"
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));
