"""A warm Cortex Code agent, held open between visitors.

WHY THIS EXISTS
---------------
`cortex exec` is a one-shot CI/CD entry point. It has no `--resume`, no
`--session` and no `--daemon`, so every call is a cold Node process that re-reads
config, authenticates, and discovers skills and MCP servers before it thinks
about the prompt. Measured on a trivial prompt:

    cortex exec                                         22.7s
    cortex exec --no-mcp                                 19.4s
    + --no-history --effort minimal --max-turns 1        18.1s

So roughly **18 seconds is startup**, not inference, and flags recover under five
of it. On a five-minute visit where the Workshop stop was measured at a 26s
median, that is the single largest slice of the visitor's time.

`cortex mcp serve` runs the same binary in server mode over stdio. Same measured
work, warm:

    startup, once                                         1.3s
    first call                                            9.4s
    second call                                           6.0s

That is the entire point of this module: pay the startup once, when the booth
opens, instead of once per visitor.

THE LOCK IS NOT OPTIONAL
------------------------
Two `tools/call` requests were issued on one process without waiting. `id=10`
asked the agent to reply ALPHA; `id=20` asked it to reply BRAVO. **Both came back
ALPHA.** The second request received the first one's payload.

On a stand that is the worst class of bug available to us: one visitor's content
in another visitor's document, with nothing raising an error. So this pool holds a
single mutex and permits exactly one in-flight call per process, always. Do not
"optimise" that away. If concurrency is ever needed, run a second process.

WHAT IT DOES NOT CARRY
----------------------
The agent is stateless between calls - a codeword stored in one call was answered
with NO CONTEXT in the next - so warming cannot leak one visitor's data into the
next visitor's turn. Verified before this was built, because on a shared booth
laptop that had to be true rather than hoped for.

Ambient MCP servers are not exposed: this laptop has eleven configured and the
agent reported none of them. It does hold `bash`, `edit`, `write`, `sql_execute`
and `web_fetch`, which is why `allowed_tools` defaults to a narrow list here.
"""

import json
import os
import subprocess
import threading
import time
import uuid

# One in-flight call per process. See the module docstring - this is load
# bearing, not defensive.
_START_TIMEOUT = 40
_DEFAULT_TIMEOUT = 75

# The agent has bash, edit, write and sql_execute available. A booth kiosk taking
# free text from strangers should not, so the default is nothing at all: every
# prompt the booth sends is answerable from the prompt itself, with the closed
# lists already injected by context.shortlist_block().
SAFE_TOOLS = []


class CocoAgent:
    """One warm `cortex mcp serve` process, serialised by a mutex."""

    def __init__(self, connection=None, model=None, workdir=None,
                 allowed_tools=None, log=None):
        self.connection = connection
        self.model = model
        self.workdir = workdir or os.getcwd()
        self.allowed_tools = (SAFE_TOOLS if allowed_tools is None
                              else list(allowed_tools))
        self.log = log or (lambda *a, **k: None)

        self._p = None
        self._call_lock = threading.Lock()   # one in-flight tools/call
        self._io_lock = threading.Lock()     # guards process creation/teardown
        self._next_id = 1
        self._calls = 0
        self._failures = 0
        self.started_at = 0

    # ------------------------------------------------------------- lifecycle

    def _spawn(self):
        cmd = ["cortex", "mcp", "serve"]
        self.log("pool: starting %s" % " ".join(cmd))
        p = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1,
            cwd=self.workdir)
        self._p = p
        self._next_id = 1
        # Handshake. Without notifications/initialized the server accepts the
        # connection but never answers a tools/call.
        self._send({"jsonrpc": "2.0", "id": self._take_id(),
                    "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05",
                               "capabilities": {},
                               "clientInfo": {"name": "loco4coco",
                                              "version": "1"}}})
        self._read_until(1, timeout=_START_TIMEOUT)
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        self.started_at = time.time()
        self.log("pool: ready")

    def start(self):
        with self._io_lock:
            if self.alive():
                return True
            try:
                self._spawn()
                return True
            except Exception as e:
                self.log("pool: start failed: %s" % e)
                self._kill_locked()
                return False

    def alive(self):
        return self._p is not None and self._p.poll() is None

    def _kill_locked(self):
        p, self._p = self._p, None
        if not p:
            return
        for fn in (p.kill, p.wait):
            try:
                fn()
            except Exception:
                pass

    def stop(self):
        with self._io_lock:
            self._kill_locked()

    def restart(self):
        self.stop()
        return self.start()

    # ------------------------------------------------------------------- io

    def _take_id(self):
        i, self._next_id = self._next_id, self._next_id + 1
        return i

    def _send(self, obj):
        self._p.stdin.write(json.dumps(obj) + "\n")
        self._p.stdin.flush()

    def _read_until(self, want_id, timeout):
        """Read lines until the reply with want_id arrives.

        Only ever called with the call lock held, so there is exactly one
        outstanding id and no correlation ambiguity. A reply carrying a different
        id is a protocol violation, and it is logged rather than silently used -
        that is precisely the failure mode this class is shaped to avoid.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not self.alive():
                raise RuntimeError("agent process exited")
            line = self._p.stdout.readline()
            if not line:
                raise RuntimeError("agent closed stdout")
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            if "id" not in msg:
                continue          # a notification
            if msg["id"] != want_id:
                self.log("pool: DISCARDING reply for id=%s while awaiting %s"
                         % (msg["id"], want_id))
                continue
            return msg
        raise TimeoutError("no reply within %ss" % timeout)

    # ----------------------------------------------------------------- calls

    def ask(self, prompt, timeout=None, model=None):
        """Run one prompt. Returns (ok, text, meta).

        Serialised: a second caller waits. Never raises - the caller has a
        fallback chain and a visitor in front of them, so a failure here must be
        an ordinary return value.
        """
        t0 = time.time()
        timeout = timeout or _DEFAULT_TIMEOUT
        meta = {"transport": "warm", "id": str(uuid.uuid4())[:8]}

        # Waiting for the lock is part of the visitor's wall clock, so it is
        # measured separately from the call itself.
        got = self._call_lock.acquire(timeout=timeout)
        if not got:
            meta.update({"waited": round(time.time() - t0, 2),
                         "error": "pool busy"})
            return False, "", meta
        meta["waited"] = round(time.time() - t0, 2)
        try:
            if not self.alive() and not self.start():
                meta["error"] = "agent unavailable"
                return False, "", meta

            args = {"prompt": prompt, "workdir": self.workdir}
            if self.connection:
                args["connection"] = self.connection
            if model or self.model:
                args["model"] = model or self.model
            # `[]` and `None` mean different things here, so this cannot be a
            # truthiness test. An empty list is an instruction - "no tools at
            # all" - and dropping it would leave the agent holding bash, write,
            # edit and sql_execute while taking free text from strangers.
            # `cortex_code_agent` accepts no effort or max_turns argument, so
            # denying tools is also the only lever available for stopping it
            # spending the visitor's time in an agentic loop it does not need.
            if self.allowed_tools is not None:
                args["allowed_tools"] = self.allowed_tools

            call_id = self._take_id()
            sent = time.time()
            try:
                self._send({"jsonrpc": "2.0", "id": call_id,
                            "method": "tools/call",
                            "params": {"name": "cortex_code_agent",
                                       "arguments": args}})
                msg = self._read_until(call_id, timeout=timeout)
            except Exception as e:
                self._failures += 1
                meta.update({"error": "%s: %s" % (type(e).__name__, e),
                             "seconds": round(time.time() - sent, 2)})
                # A broken pipe or a half-read reply leaves the stream out of
                # step with the ids, so the process is no longer trustworthy.
                self.log("pool: dropping process after %s" % meta["error"])
                self.stop()
                return False, "", meta

            self._calls += 1
            meta["seconds"] = round(time.time() - sent, 2)
            if "error" in msg:
                self._failures += 1
                meta["error"] = str(msg["error"])[:300]
                return False, "", meta
            text = _text_of(msg.get("result") or {})
            if not text.strip():
                self._failures += 1
                meta["error"] = "empty reply"
                return False, "", meta
            return True, text, meta
        finally:
            self._call_lock.release()

    # ----------------------------------------------------------------- admin

    def warm(self):
        """Start the process and take one cheap turn.

        The first call after startup is measurably slower than the rest (9.4s
        against 6.0s), so the booth spends that before doors open rather than on
        the first visitor.
        """
        if not self.start():
            return False, "could not start"
        ok, text, meta = self.ask("Reply with exactly: READY", timeout=60)
        return ok, ("warm in %ss" % meta.get("seconds")
                    if ok else meta.get("error", "warm failed"))

    def stats(self):
        return {"alive": self.alive(), "calls": self._calls,
                "failures": self._failures,
                "uptime": (round(time.time() - self.started_at)
                           if self.started_at else 0),
                "busy": self._call_lock.locked()}


def _text_of(result):
    """Pull the text out of an MCP tool result."""
    if isinstance(result, str):
        return result
    parts = []
    for c in (result.get("content") or []):
        if isinstance(c, dict) and c.get("type") == "text":
            parts.append(c.get("text") or "")
        elif isinstance(c, str):
            parts.append(c)
    return "\n".join(parts).strip()


# A single module-level agent, because the booth serves one visitor at a time on
# one laptop. Deliberately not a pool of N: see the docstring on concurrency.
_agent = None
_agent_lock = threading.Lock()


def get_agent(connection=None, model=None, workdir=None, log=None):
    global _agent
    with _agent_lock:
        if _agent is None:
            _agent = CocoAgent(connection=connection, model=model,
                               workdir=workdir, log=log)
        return _agent
