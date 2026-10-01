# Server Stability and Timeout Analysis

Analysis of the Loco4CoCo booth server's resilience, timeout behaviour, and
the admin-panel controls that mitigate operational risks.

## Timeout Map

| Operation | Timeout | On expiry |
|---|---|---|
| Warm agent call | 75 s | Falls back to `cortex exec` |
| `cortex exec` turn | 180 s | `p.kill()`, falls back to COMPLETE SQL |
| COMPLETE SQL | Snowflake session default | No explicit statement timeout set |
| Blueprint staging (`snow stage copy`) | 90 s | Exception caught, delivery fails gracefully |
| Presigned URL generation | 120 s | Exception caught |
| QA check | 12 s | Skipped |
| Agentic marketplace search | 45 s | Subprocess killed |
| Warm agent startup (MCP handshake) | 40 s | Falls back to `cortex exec` |

Worst-case visitor-facing delay: the 180 s `cortex exec` ceiling, hit only when
the warm agent is down _and_ exec hangs. The COMPLETE SQL fallback then responds
in 1–2 s.

## Four-Layer AI Fallback Chain

The server never depends on a single AI path. Every conversational turn tries:

1. **Warm agent** (`cortex mcp serve`) — ~3.4 s steady-state
2. **`cortex exec`** (cold one-shot) — ~26 s
3. **`SNOWFLAKE.CORTEX.COMPLETE`** (in-process SQL) — ~1–2 s
4. **Precomputed archetype defaults** — no model needed

The COMPLETE model itself has a fallback chain configured in `config.json`
(`complete_model_fallbacks`).

## Admin Panel Coverage

The admin page (`/admin`) is the operator's primary tool during an event. It
polls `/api/admin/status` every 5 seconds and surfaces:

| Risk | Admin mitigation | Sufficient for a staffed booth? |
|---|---|---|
| Warm agent wedged / stopped | **Restart server** — `os.execv` re-execs the process | Yes |
| Stale visitor state | **Clear visitor** — wipes `state.json`, purges temp files, restarts the warm agent | Yes |
| Snowflake connection dropped | Status card shows auth status in real-time | Yes — operator sees it immediately |
| Delivery chain broken | **Run setup check** — proves snow CLI, stage, presign, and key-pair auth end-to-end | Yes |
| Warm agent down | Shown as "not running (falls back, still works)" — deliberately not red | Yes (fallback chain covers it) |
| Wrong venue/config | **Apply** hot-swaps venue without restart | Yes |
| Model went legacy | Status card shows verified model vs configured model, with fallback indication | Yes |

## Residual Risks

These are not covered by the admin panel and are documented for awareness:

### Unattended crash recovery

If the Python process dies (OOM, unhandled thread exception), the admin panel
is also dead — it is served by the same process. At a staffed booth the
operator notices the terminal; for unattended setups a wrapper script provides
automatic recovery:

```bash
#!/bin/bash
cd "$(dirname "$0")/game"
while true; do
    python3 server.py "$@"
    echo "[$(date)] Server exited ($?), restarting in 3s..."
    sleep 3
done
```

### Unbounded HTTP threads

`ThreadingHTTPServer` creates one thread per connection with no cap. With
single-visitor use plus one admin panel this is theoretical, not practical.

### No statement-level timeout on COMPLETE SQL

The `sf_conn()` cursor calls rely on Snowflake's session defaults. Adding
`network_timeout` or `socket_timeout` to the connector config would bound this
explicitly if needed.

### Subprocess zombies

If `p.wait(timeout=10)` fails after `p.kill()`, a zombie process is left. This
has not been observed in practice but could accumulate over a long-running
event day.
