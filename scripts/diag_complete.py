"""Reproduce the exact COMPLETE call game/server.py makes, and show the truth."""
import json
import sys
import time

sys.path.insert(0, "game")
import snowflake.connector as sc  # noqa: E402

CFG = json.load(open("game/config.json"))
MDL = (CFG.get("coco") or {}).get("complete_model") or "mistral-large2"
CONN = (CFG.get("snowflake") or {}).get("connection_name")
PROMPT = "In one sentence, name the Snowflake feature for incremental transforms."

cn = sc.connect(connection_name=CONN)
cur = cn.cursor()

for label, sql, args in [
    ("3-arg, empty options (what server.py does)",
     "SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, ARRAY_CONSTRUCT("
     "OBJECT_CONSTRUCT('role','user','content',%s)), OBJECT_CONSTRUCT())",
     (MDL, PROMPT)),
    ("3-arg, options with temperature",
     "SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, ARRAY_CONSTRUCT("
     "OBJECT_CONSTRUCT('role','user','content',%s)), "
     "OBJECT_CONSTRUCT('temperature',0))",
     (MDL, PROMPT)),
    ("2-arg, bare string",
     "SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, %s)", (MDL, PROMPT)),
]:
    t = time.time()
    try:
        cur.execute(sql, args)
        raw = (cur.fetchone() or [""])[0]
        secs = time.time() - t
        print(f"\n=== {label}\n    {secs:.1f}s  type={type(raw).__name__}")
        print(f"    raw[:400]={str(raw)[:400]}")
        if isinstance(raw, str) and raw.strip().startswith("{"):
            d = json.loads(raw)
            ch = (d.get("choices") or [{}])[0]
            print(f"    choices[0] keys = {list(ch.keys())}")
            parsed = str(ch.get("messages") or ch.get("message") or "").strip()
            print(f"    server.py would parse reply = {parsed[:120]!r}")
            print(f"    -> ok would be {bool(parsed)}")
    except Exception as e:
        print(f"\n=== {label}\n    FAILED after {time.time() - t:.1f}s")
        print(f"    {type(e).__name__}: {str(e)[:300]}")

cur.close()
cn.close()
