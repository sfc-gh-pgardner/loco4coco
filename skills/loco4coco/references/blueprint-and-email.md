---
name: blueprint-and-email
description: "The blueprint artefact and how it reaches the visitor. Structure of the HTML email body, the Gmail MCP send call with runtime tool discovery, the on-screen fallback, and the verified constraints that rule out every other delivery route."
---

# The blueprint and getting it to the visitor

## Why email, and why only email

Four delivery routes were tested on 2026-08-05. Three are dead:

| Route | Result |
|---|---|
| Google Doc shared to the visitor | **Blocked.** `"an item cannot be shared outside of Snowflake Inc."` Fails with notification off too, so it is permission creation that is blocked. Not fixable without Workspace admin. |
| Google Doc public link + QR | **Blocked.** `type: anyone` returns `Bad Request`, creates no permission, file stays `shared: false`. |
| Snowflake presigned stage URL | **Works but wrong.** Genuinely public, no login, HTTP 200 - but always `Content-Type: application/octet-stream`, so browsers download rather than render. Unfixable on an internal stage. Fine for a PDF, useless for a page. Note `curl -I` returns 403 because the signature is method-specific - always test with GET. |
| `SYSTEM$SEND_EMAIL` to the visitor | **Impossible.** Reaches only verified email addresses of users in the same account, regardless of `ALLOWED_RECIPIENTS`. Supports `text/html`, so it remains the right channel for emailing *ourselves*. |

That leaves the **Natoma Gmail MCP** as the only route to an arbitrary inbox. It is registered in `~/.snowflake/cortex/mcp.json` as `Gmail` at `.../my-connections/google-gmail/mcp`.

**Unverified as of 2026-08-05.** It was enabled during this build but HTTP MCPs need OAuth on first connect and a fresh session before their tools load, so the send path has not yet been exercised end to end. `loco4coco-ops` pre-flight must prove it before doors open, and it must be proven with a real send to a real external address - not by observing that the tool exists.

## Sending

Do not assume tool names. **Discover them at runtime**, because this MCP's surface has not been confirmed:

1. Look for an available tool whose name contains `gmail` and whose purpose is sending (typically `send_email` / `send_message`).
2. Expected arguments: a recipient, a subject, a body, and a content-type or HTML flag.
3. Send the blueprint as an **HTML body**, not an attachment - it must be readable on a phone on a train without opening anything.
4. If no send tool is available, fall back immediately. Do not stall the visitor.

Subject line: `Your POC blueprint: {poc_name}`

Fallback order:
1. Gmail MCP send.
2. On-screen blueprint plus `ERR.SEND_FAILED`; tell them to photograph it.
3. Log the session either way with `email_sent` set truthfully. Never record a send that did not happen.

## Structure of the blueprint

HTML, single column, max ~600px, system fonts, no external images (a remote image makes it look like spam and may not load). Snowflake brand blue `#29B5E8`, mid blue `#11567F`, near-black text `#1A1A1A` on white.

Sections in this order:

```
1. HEADER          "Your POC Blueprint" + their first name + event and date
2. THE IDEA        POC name, one-sentence description in THEIR words
3. WHY IT MATTERS  the pain they described, quoted back
4. READINESS       score /5, and the one thing to firm up
5. THE PROMPT      the kick-off prompt in a monospace block  <- the payload
6. HOW TO START    1) free trial  2) open CoCo  3) paste the prompt
7. THE GUIDE       title + full URL of the fork-base
8. THE FEATURES    each named feature + its doc link
9. COCO ITSELF     the onboarding guide
10. FOOTER         who to contact, and why they got this email
```

**Section 5 sits above the guide deliberately.** It is the payload; a visitor skimming on a phone must hit it before they lose interest. Everything below it is supporting material.

## The prompt block

The single most-fumbled element. It must survive being copied on a phone.

- Wrap in `<pre>` with `white-space: pre-wrap; word-break: break-word;` so it reflows without inserting characters.
- Light background (`#F4F8FB`), 1px border, generous padding.
- **No syntax highlighting and no `<code>` inside `<pre>`** - some clients inject zero-width characters that break a paste.
- Never split the prompt across elements. One contiguous text node.
- Precede it with: *"Copy everything in the box below."*

## Feature doc links

Take doc topics from the archetype in `poc-archetypes.md`, then resolve current URLs with `snowflake_product_docs` at runtime so links do not rot.

If the docs lookup fails (no network at the venue), fall back to naming the feature with **no link at all**. Never guess a docs URL - a broken link in the one artefact they keep is worse than no link.

## Rendering it on screen

Show the blueprint on the booth screen as well as emailing it. It is the visual payoff, it covers a failed send, and it lets the visitor photograph the prompt immediately.

For a richer on-screen artefact, the `html-authoring` skill can style it - but note that skill targets the Snowflake sandbox, whose `/libs/` assets render blank outside it. The email HTML must stay fully self-contained and inline-styled.

## Pre-send checklist

- [ ] No unresolved `{...}` anywhere in the HTML
- [ ] Prompt passes the `prompt-builder.md` self-check
- [ ] Guide URL is a verified slug from `guides-index.md`
- [ ] Every doc link resolved at runtime, or omitted
- [ ] POC name is in the visitor's language, not Snowflake's
- [ ] Nothing claims the POC has been built
- [ ] Their pain is quoted accurately - misquoting it is worse than omitting it
- [ ] Footer explains why they received the email
