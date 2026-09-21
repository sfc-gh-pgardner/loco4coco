# Savepoint 2026-09-21e — EXEC DEFECT ROOT CAUSE FOUND

**The defect is not "wasted exec". Every COMPLETE call is failing, and exec is
silently carrying the load.**

Evidence from `game/cost.jsonl`, one smoke-test run:

```
library          complete     0.9s ok=False err=None
library          exec        26.6s ok=True
marketplace      complete     0.4s ok=False err=None
marketplace      exec        21.5s ok=True
workshop         warm        14.4s ok=True
workshop_refine  complete     0.3s ok=False err=None
workshop_refine  exec        19.6s ok=True
qa               complete     0.3s ok=False err=None      <-- no fallback at all
```

Four of four COMPLETE calls return `ok=False` in 0.3–0.9s — far too fast to be a
real generation. So COMPLETE is broken outright, and the 20–27s exec calls I had
called "a path the config never asked for" are in fact the *correct* fallback
doing the real work. My earlier reading of the symptom was wrong.

Two consequences:

1. `qa` has **no** exec fallback in the observed run, so QA findings are likely
   empty for every visitor. That is worse than the latency.
2. `run_turn`'s fall-through is behaving as designed; the bug is inside
   `run_complete`.

## `run_turn` control flow (confirmed by reading it)

```python
if wants == "complete":
    ok, reply, meta = run_complete(...)
    if ok or meta.get("ok"):   return ...      # success
    if not meta.get("error"):  return ...      # "superseded, not a failure"
    print("COMPLETE failed ... falling back")  # -> falls to layer 2 exec
elif coco.get("warm_agent", True):
    ...
if remaining() > 20:
    run_exec(...)
```

Contradiction still to resolve: the cost log records `err=None` for the failed
COMPLETEs, yet library / marketplace / workshop_refine *did* fall through to exec
— which only happens when `meta["error"]` is truthy. So `log_cost` is not
recording the error field that `run_turn` branches on. `qa` did not fall through,
so its meta genuinely had no error (the "superseded" branch). Two distinct
failure modes are in play.

## Next step (exact)

1. Read `run_complete` in `game/server.py`. Determine why it returns `ok=False`
   in under a second. Prime suspect: the three-argument
   `SNOWFLAKE.CORTEX.COMPLETE(model, prompt, options)` form, or response-shape
   parsing, against `claude-4-sonnet`. Note COMPLETE was measured working at
   ~5.1s via `snow sql` during the model bench — the SQL is fine, so the fault is
   in how `server.py` calls or parses it.
2. Fix `log_cost` so the error reaches the cost log; the silent `err=None` is why
   this went unnoticed.
3. Give `qa` a fallback, or make its failure visible.
4. Re-run `game/smoke_test.py`. Expect total CoCo wait to drop from 202.5s.

## Still outstanding — user's TOP PRIORITY list

- Paris manufacturing padding with off-theme reserves.
- `deploy/manifest.yml` is `skip-worktree` (flagged `S`) so local edits **do not
  ship**. Clear with
  `git update-index --no-skip-worktree deploy/manifest.yml`, then commit the
  quota-100 change, the pool-account header, and the removed `/admin` claims.

## Also outstanding

- Keychain: count expected prompts, when it was introduced, CoCo CLI behaviour,
  permanent fix. Candidate: key-pair auth removes the keychain entirely; current
  `Frankfurt_L4C` uses `oauth_authorization_code` with
  `client_store_temporary_credential=true`. Every `snow sql` subprocess is a new
  process and therefore a new keychain read — the likely reason for "so many".
- Operator/stand: check whether any logic consumes `SE_OPERATOR`.
- Translation status; post-event processes.
- New TL;DR setup Google Doc (humanizer style) plus a change list for the
  original doc `102kpn7MXJFYcA9ZHoa6kCKoQe3EgK3Dtj8bwm9wF6bQ`.
- User still wants to manually test `/admin`.
