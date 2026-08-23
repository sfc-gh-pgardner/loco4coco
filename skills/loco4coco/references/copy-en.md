---
name: copy-en
description: "Every visitor-facing string for Loco4CoCo, in English. The skill references string IDs and never hardcodes literals, so a French deck (copy-fr.md) is a drop-in for Paris. Also holds the question sets for both rounds and the tone rules."
---

# Copy deck — English (London)

**Language code:** `en` · **Event:** Snowflake World Tour London

The skill must reference these by ID (e.g. `OPEN.WELCOME`) and never hardcode visitor-facing text. Paris supplies `copy-fr.md` with the same IDs and nothing else changes. If a string is missing from a deck, fall back to `en` and note it — never show an ID to a visitor.

## Tone rules (apply to every string and to anything improvised)

- Light and warm, never zany. The fortune-teller framing is a wink, not a bit.
- Short sentences. A booth is loud and the visitor is standing up.
- UK English.
- Never use the words "quiz", "form", "survey" or "questionnaire" to the visitor.
- Never say "AI-powered" or "leverage". Say what the thing does.
- No emojis in the blueprint. Sparingly on screen is fine.
- If a visitor gives a joke answer, play along once, then steer back. Do not lecture.
- **Never claim the POC is built.** They are leaving with a plan and a prompt. Overpromising here is the fastest way to lose their trust.

---

## Opening

**`OPEN.WELCOME`**
> Welcome to Loco for CoCo.
>
> I'm CoCo — Snowflake's agentic assistant. Give me five minutes and I'll read your fortune: by the end you'll have a real plan for something worth building, and the exact prompt to build it with.
>
> First — who am I talking to?

**`OPEN.FIELDS`** — intake labels: `First name`, `What you do`, `Email`

**`OPEN.EMAIL_WHY`** (helper text under the email field)
> So I can send your blueprint. Nothing else, ever.

**`OPEN.CONSENT`** — see `session-log.md`. Must be shown before the email field is submitted. Placeholder pending events/marketing sign-off; do not invent final wording.

**`OPEN.BUTTON`** — `What's my fortune?`

## The fortune

Personalised by role, then archetype. Delivered *before* the questions as the hook, and it deliberately promises a plan rather than a finished app.

**`FORTUNE.GENERIC`**
> I see light blue. A flash — of inspiration, and a next-generation data product.
>
> You'll leave this hall with an idea, and you'll build it in the weeks that follow.

**`FORTUNE.ROLE.ANALYST`**
> I see someone who has been asked "can you just pull a quick number?" one too many times.

**`FORTUNE.ROLE.ENGINEER`**
> I see a pipeline. I see it breaking at 6am. I see you already knowing why.

**`FORTUNE.ROLE.LEADER`**
> I see a business case with a gap in it, and I see you closing the gap this quarter.

**`FORTUNE.ROLE.PUBLIC_SECTOR`**
> I see a duty to the public, and a spreadsheet standing in the way of it.

**`FORTUNE.ROLE.OTHER`**
> I see someone who came to the stand because something at work is harder than it should be.

## Round 1 — three questions, one call

Batched in a single `ask_user_question`. Every question carries an Other option.

**`R1.Q1`** — header `Your world`
> Where do you spend your days?

Options: `Public sector`, `Financial services`, `Health & life sciences`, `Retail & consumer`, `Manufacturing & energy`, `Tech & telco`

**`R1.Q2`** — header `The painful bit` — **primary archetype signal**
> What's the bit that makes you sigh?

| Option | Routes to |
|---|---|
| "Getting a straight answer out of our data takes days" | `talk-to-my-data` |
| "The answer's buried in documents nobody reads" | `ask-my-documents` |
| "Someone retypes paperwork into a spreadsheet" | `extract-from-paperwork` |
| "Too much comes in to sort by hand" | `triage-and-classify` |
| "Our data lives in five different systems" | `join-the-silos` |
| "We find out about problems too late" | `watch-it-live` |

**`R1.Q3`** — header `The dream` — **disambiguates Q2**
> If it worked perfectly, what would it do?

| Option | Effect |
|---|---|
| "Answer questions in plain English" | confirms `talk-to-my-data` / `ask-my-documents` |
| "Do the whole task, not just tell me about it" | overrides to `an-agent-that-acts` |
| "Show me a picture I can act on" | overrides to `talk-to-my-data` |
| "Warn me before it goes wrong" | overrides to `predict-what-happens-next` / `watch-it-live` |
| "Let me share it safely with others" | overrides to `share-without-copying` |

## Round 2 — two questions, one call

**`R2.Q1`** — header `Your data`
> What have you actually got to hand?

Options: `Tables in a database`, `Spreadsheets and CSVs`, `A pile of documents`, `A live feed of events`, `Honestly, not sure yet`

Feeds the readiness score and picks between beginner and advanced forks. `Honestly, not sure yet` scores zero on data-on-hand but must not be treated as a wrong answer — it is very common and often the most honest.

**`R2.Q2`** — header `Who's it for`
> Who'd feel the benefit first?

Options: `Just me and my team`, `A department`, `The whole organisation`, `Our customers or citizens`, `Our partners or suppliers`

`The whole organisation` on its own scores zero on clear-user — gently narrow it in the reveal rather than marking them down silently.

## Reveal

**`REVEAL.HEADER`**
> Right. Here's your fortune, {first_name}.

**`REVEAL.NAMED`**
> **{poc_name}** — {archetype_friendly}

**`REVEAL.BECAUSE`**
> You said {their_pain_quoted}. That's not a small thing, and it's very buildable.

**`REVEAL.GUIDE`**
> Someone at Snowflake has already built most of this. You're forking **{guide_title}**.

**`REVEAL.SCORE`**
> POC readiness: **{score}/5**. {weakest_point_note}

**`REVEAL.SCORE_PERFECT`** (score = 5 — no weakest point exists, so `REVEAL.SCORE` would render a dangling sentence)
> POC readiness: **5/5**. You've got the data, you know who it's for, and you can measure it. There's nothing standing between you and starting this.

**`REVEAL.SCORE_LOW`** (score <= 2)
> Low score is good news, not bad — it means the first move is cheap. Nail down {weakest_point} and this gets real fast.

**`REVEAL.KEPT_PAIN`** (use when Q3 pointed at a different archetype but Q2 won)
> You also said you wanted {their_dream}. You'll get that too — but the real win is {q2_outcome} first.

## Handoff

**`HANDOFF.SENT`**
> Sent to {email}. It has the plan, the guide, the docs, and a prompt.

**`HANDOFF.NEXT`**
> Three steps: start a free trial at signup.snowflake.com, open CoCo, paste the prompt. That's it — CoCo takes it from there.

**`HANDOFF.SIGNUP_URL`** — `https://signup.snowflake.com/`
> **Open question:** a UTM is wanted so activation signups are attributable. Not yet supplied by marketing. Ship the bare URL until it is; do not invent parameters.

**`HANDOFF.CLOSE`**
> Go and build it. Come back and tell me if it worked.

## Error and edge strings

**`ERR.NO_EMAIL`**
> No email, no problem — have a read on screen and photograph it.

**`ERR.SEND_FAILED`**
> The send didn't go through. Your blueprint's on screen — grab a photo and I'll flag it to the team.

**`ERR.TIME_UP`** (past five minutes)
> We're out of time and there's a queue behind you. Here's what I've got — it's enough to start.

## Reusable fragments

**`FRAG.COCO_IS`**
> CoCo is Snowflake's agentic assistant. You describe what you want; it writes and runs the code in your account.

**`FRAG.COWORK_IS`**
> CoWork is for asking and analysing. CoCo is for building and automating.

**`FRAG.TRIAL_NOTE`**
> Everything here runs on a Snowflake free trial. No procurement required to try it.
