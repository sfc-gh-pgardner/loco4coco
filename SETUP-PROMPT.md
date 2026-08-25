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

3. Determine my account region by querying CURRENT_REGION(). Do not guess it, and
   do not copy AWS_EU_WEST_2 from the config - if event.region does not match my
   account the Marketplace stall will be empty.

4. Add a deploy target to deploy/manifest.yml by copying the LONDON block. Set
   account_identifier from my connection, and set monitor_notify_user to a real
   user in my account - ask me if you cannot determine it. A resource monitor
   with an empty notify list warns nobody.

5. Show me `python3 deploy/bootstrap.py --target <mine> --connection <conn>
   --plan-only` output and WAIT for my approval before deploying for real.

6. Update game/config.json: event.region to my region, event.city and
   event.language for my event, snowflake.connection_name to my connection, and
   ask me for event.operator in the form "My Name / Stand label". Tell me
   explicitly that event.operator cannot be reconstructed after the event.

7. Load the shared context: python3 deploy/load_context.py --connection <conn>

8. Run the gate: python3 deploy/verify_context.py --all
   Report every failure. Do not tell me the booth is ready if this is non-zero.

9. Start the server, confirm http://127.0.0.1:4747/ answers, and confirm the
   console shows "warm agent ready" rather than a warning.

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
  policy. See `PRIVACY-REVIEW.md`. That is a human decision.
- It will not re-curate the marketplace for a non-UK region. The current picks
  and the geo weighting are UK-weighted.
- It will not translate anything.

## If it goes wrong

Everything it does is reversible except the Snowflake deploy, which is why step 5
stops for approval. `snow dcm plan` shows the change before `snow dcm deploy`
applies it, and DCM drops objects that are removed from the definition file, so
read the plan rather than skipping it.
