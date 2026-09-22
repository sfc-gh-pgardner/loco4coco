# Set it up by asking CoCo

Paste this into an interactive Cortex Code session in the cloned repo. It does
the same job as the setup guide, but CoCo reads your account and fills in the
values instead of you editing files by hand.

Use the guide if you want to understand what is happening. Use this if you just
want a working booth.

---

## The prompt

```
Set up the Loco for CoCo booth activation on this laptop, against my Snowflake
account. The repo is already cloned and you are in it.

Read CONSTRAINTS.md first. Then work through this, stopping to ask me only when
you genuinely cannot determine a value:

1. Check my prerequisites and tell me what is missing before doing anything else:
   python3 --version (need 3.11+), snow --version, cortex --version, and the four
   pip packages snowflake-connector-python, python-docx, PyYAML, segno.

2. Find my Snowflake connections with `snow connection list`. If there is more
   than one, ask me which to use. Prove it works with `snow connection test`, and
   prove Cortex Code can use it with:
   cortex exec "Reply with the single word: ready." --no-mcp -c <conn>
   If that returns "No models available", stop and tell me - nothing else will
   work until it is fixed.

3. Do not look up my account's region, and do not put it anywhere in the config.
   The account's region only decides where SESSIONS and TURNS are written. The
   region that chooses Marketplace datasets is the EVENT's, and event.venue
   already resolves it. Setting the stall's region from the account is the one
   mistake that quietly gives visitors the wrong city's data.

4. Do not add a deploy target. The default EVENT target in deploy/manifest.yml
   deliberately pins no account and deploys wherever my connection points.
   Pasting a pool-assigned account ID into a tracked file is friction, and risks
   committing someone else's account identifier.

5. Show me `python3 deploy/bootstrap.py -c <conn> --plan-only` output and WAIT
   for my approval before deploying for real.

6. After I approve, run the real deploy: `python3 deploy/bootstrap.py -c <conn>`.
   As well as creating the Snowflake objects, this converts my connection to
   key-pair auth (SNOWFLAKE_JWT) in place — that is what stops the macOS keychain
   from interrupting a visit with a password prompt, so it is part of setup, not
   optional. Do NOT pass --skip-keypair. When it finishes, confirm the connection
   landed on key-pair: `snow connection list` should show authenticator
   SNOWFLAKE_JWT with a private_key_file, and there will be a timestamped
   connections.toml backup. Tell me the result. If the conversion failed, say so
   but do NOT stop — the booth still works on OAuth, you will just get occasional
   keychain prompts.

7. Set event.venue in game/config.json to my event (london, paris or berlin).
   Do not set event.marketplace_region, event.city or event.language by hand —
   the venue resolves all three. bootstrap already wrote snowflake.connection_name,
   so leave it. There is no operator or stand field to ask me for;
   SESSIONS.SE_OPERATOR is stamped with the account automatically.

8. Load the shared context: python3 deploy/load_context.py --connection <conn>

9. Run the gate: python3 deploy/verify_context.py --all
   Report every failure. Do not tell me the booth is ready if this is non-zero.

10. Start the server and confirm http://127.0.0.1:4747/ answers. The console
   should show "warm agent ready". If instead it says the warm agent is
   unavailable on this version of Cortex Code, that is NOT a setup failure:
   every turn falls back to cortex exec and the booth still works, just more
   slowly. Report which of the two you saw, and do not try to fix it.

Then tell me, in a short list: which connection and region you used, what you
created in Snowflake, anything you changed in a file, anything you could not
verify, and what I still have to do myself.

Do not change any visitor-facing copy, prompts, archetypes, marketplace listings
or feature lists. Setup only.
```

---

## What it will not do

- **It will not sign off the privacy notice.** The letter captures a first name,
  an employer and free text, and there is no notice, consent record or retention
  policy. See the "Privacy notice" section of the Setup Guide (Google Doc). That is a
  human decision.
- It will not re-curate the marketplace for a non-UK region. The current picks
  and the geo weighting are UK-weighted.
- It will not translate anything.

## If it goes wrong

Everything it does is reversible except the Snowflake deploy, which is why step 5
stops for approval. `snow dcm plan` shows the change before `snow dcm deploy`
applies it, and DCM drops objects that are removed from the definition file, so
read the plan rather than skipping it.
