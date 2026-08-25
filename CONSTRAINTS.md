# Constraints of the brief

Read this before designing any feature. These are properties of the **venue**,
not preferences, and they have already been broken once - by a "SAVE MY CARD"
button that called `a.download`, which cannot work on the machine it shipped on.

Every change should be checked against all six.

## What this is

**Snowflake World Tour London.** A booth activation on a Snowflake-branded stand.

A visitor walks up to the stand, gives us **five minutes**, and in that time
experiences the power of **Cortex Code** and leaves with the **scaffolding for a
POC** - their idea in their own words, a Snowflake developer guide to fork, named
features with doc links, an honest readiness score, and a kick-off prompt to paste
into CoCo on a free trial.

- **One visitor at a time**, on one laptop, with a queue behind them.
- **It does not build an app.** The payload is the plan plus the prompt.
- **The bar for success, from the brief:** the visitor can explain CoCo to a
  colleague afterwards.
- Paris follows London, in French, as a copy-deck swap - not a rebuild.

Everything below follows from that. When a change would be right for a workshop,
a webinar or a self-serve demo but wrong for a stranger on a clock in public,
the stranger wins.

### The five stops are locations in the game, not event formats

The visitor walks a penguin round a map through four stops. When a discussion
says "the workshop", it means the third stop, not a training session:

`THE LETTER` (intake) -> `THE LIBRARY` (what data you hold, and where it lives)
-> `THE MARKETPLACE` (what to join to it) -> `THE WORKSHOP` (CoCo forges the POC)
-> `THE POSTBOX` (the handover)

## 1. The booth machine is a shared demo laptop

The visitor does not own it, will not log into it, and walks away from it.

**Nothing may depend on the visitor saving, downloading or keeping a file on that
machine.** No `a.download`. No "it's in your Downloads folder". No local install,
no browser extension, no signing into anything.

Every takeaway must leave the building on **their** device - a QR code to a
presigned URL, or an email. If a feature's success path ends in the laptop's
filesystem, the feature has failed, however well it works in dev.

## 2. Five minutes, in public, with a queue behind them

The only input device is that laptop's keyboard. No long typing, no passwords, no
account creation, no "sign in to continue". Every question must be answerable
with a click or a handful of words.

## 3. Their phone is the second screen, and the only durable one

Design the handover as: **on-screen QR -> their camera -> a URL that works with
no Snowflake account and no login.** Anything they receive should be legible on a
phone held one-handed; that is why the blueprint page is mobile-first and why the
share card is 1200x630 rather than A4.

## 4. The venue network may be hostile

Anything on the critical path must work from the laptop's own connection, and
must degrade to something the visitor can still leave with. Three independent
delivery tiers exist for this reason (QR, queued email, durable stage record) - do not collapse them into one.

## 5. We do not control content-type on a presigned stage URL

**Measured on PG_LONDON:** `GET_PRESIGNED_URL` always serves
`application/octet-stream`, whatever the file extension, and offers no way to
change it. `HEAD` returns 403; the signature covers `GET` only.

Consequences:

- A presigned `.html` **downloads** instead of rendering. Useless as a QR target.
- A presigned `.docx` or `.png` is **fine** - on a phone, downloading is exactly
  what we want: the file lands in Files or Photos and is theirs.
- Anything that must *render* in a browser needs a real serving surface (SPCS
  with a public endpoint, or a Streamlit/SAR page reading the SESSIONS row), not
  a stage URL. Until that exists, the HTML page ships as the email body, where
  the mail client supplies the content type.

## 6. The visitor is not a developer

They are a data lead, an analyst, a manager, a procurement officer. They may
never have written SQL. They did not come to the stand to learn a tool; they came
because a penguin caught their eye.

Consequences:

- **Never ask them to name a Snowflake feature, a file format or an architecture.**
  Offer choices in the language of their own job and let CoCo do the translation.
- Every question must be answerable by clicking, not typing. Free text is always
  optional and always has a click-only path beside it.
- Jargon in the visitor-facing copy is a defect, even when it is accurate.
- The document they leave with is read by them and shown to a colleague, so it
  must stand on its own without us stood next to it explaining it.
- A five-minute clock means CoCo must never make them wait without telling them
  what it is doing. Silence reads as broken.
