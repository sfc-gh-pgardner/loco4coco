"""Write the TL;DR setup doc body, with real heading styles.

Inserted text inherits the style of the paragraph next to it, which is how ~280
dataset rows once ended up in a Google Doc outline as HEADING_3. So this inserts
the whole body first, forces every paragraph to NORMAL_TEXT, and only then
promotes the specific lines that are headings.
"""
import json
import sys

DOC = "1TwRR5uurF8NHGTbQBiBQBs0fHV9lqqUZ7357WxY5e_E"

H1 = "H1:"
H2 = "H2:"
BULLET = "* "

BODY = """H1:Loco4CoCo — TL;DR setup
Everything an operator needs to run the booth, in one page. The long version, with the reasoning behind each choice, is in SETUP.md in the repo.
H2:The setup is three things
Install Cortex Code and get an event account. Clone the repo and run bootstrap. Load your city's datasets and open the admin panel.
Nothing asks you for your account name or its region. You are assigned a random account from a pool, and every step below works the same whichever one you get.
H2:Let Cortex Code do it
Most people would rather hand this to Cortex Code than type it. Paste this into Cortex Code once you have it installed and connected:
Set up the Loco4CoCo booth from https://github.com/sfc-gh-pgardner/loco4coco. Clone it into my Cortex Code plugins directory, run the bootstrap against my event connection, load the datasets for my city, and tell me the admin URL when you are done.
It will ask permission before running commands. Approve them.
H2:Or the five commands
pip3 install -r requirements.txt
git clone https://github.com/sfc-gh-pgardner/loco4coco.git ~/.snowflake/cortex/plugins/loco4coco
cd ~/.snowflake/cortex/plugins/loco4coco
python3 deploy/bootstrap.py -c MYBOOTH
python3 game/server.py
Clone first, then install from requirements.txt inside the clone. The QR code needs segno specifically - not qrcode, which is a different library - and without it the handover degrades to a typed link.
Register for your event account at https://go.dataops.live/emea-swt/register first, then create a connection with snow connection add and call it MYBOOTH.
H2:Bootstrap handles the awkward parts for you
* It converts your connection to key-pair auth, which is what stops macOS asking for your keychain password during a visit.
* It deploys the booth objects and the warehouse, and makes sure no credit limit is attached to it - nothing should ever be able to suspend the booth mid-visit.
* It points game/config.json at whichever account you were given.
* It checks that the model the booth talks to actually answers, and falls back if it does not.
* It runs a smoke test, so a broken account fails here rather than in front of someone.
If it cannot set up key-pair auth, it says so and carries on. The booth still works, you will just get keychain prompts.
H2:You should not see a keychain or browser prompt
If you do, something is still on OAuth. This matters more than it sounds: the booth authenticates about three times per visitor, which is roughly 312 times over a hundred-visitor day, and any one of those can put a password dialog on screen while somebody is standing in front of you.
Run this to find what is still unsafe:
python3 scripts/check_auth_safety.py
It checks all three places a connection gets resolved from, because fixing only the booth's own connection is not enough. Then fix whatever it names:
python3 scripts/setup_keypair.py --connection <the-name-from-step-0>
One thing that will not show up in that audit: the connection picker inside Cortex Code is a runtime choice and is not written to settings.json. If you are getting browser reauth prompts while Cortex Code helps you, check what the picker is set to.
H2:Set your city before the doors open
Load the datasets for your city first, then open http://127.0.0.1:4747/admin, choose your venue and press Apply:
python3 deploy/load_context.py --connection <your-connection>
That order matters. Apply is the only thing that clears the dataset cache, so pressing it last is what guarantees the stall shows what you just loaded.
This step is not optional. Without it the stall shows London's datasets whichever city you are in.
H2:The six things to check before the doors open
* The admin panel's Model proven row reads yes, followed by a model name, in green.
* The dataset profile matches your city, and datasets loaded is not zero.
* A test visit produces a QR code that opens on your phone.
* The admin panel names the connection you created in step 0, and nothing else.
* Pre-flight reports failures. Run python3 deploy/verify_context.py --all. Only FAIL lines matter, and there should be none. The note lines about listings not importable by this account are expected and harmless: the booth shows listings, it never imports one.
* The admin panel's Warm agent row. Ready is ideal; off or not running is fine too, and is shown in grey rather than red because the booth works either way.
H2:If something breaks
* The stall shows the wrong city's datasets. You skipped load_context.py, or Apply was not pressed.
* Replies are slow, around twenty seconds each. Either the model the booth is configured for has stopped working, or the warm agent could not start on this laptop's version of Cortex Code. Both fall back automatically and the admin panel and startup log will say which. The booth still works either way.
* Any version of Cortex Code is fine. The booth checks at startup whether this one can hold a warm agent open, says so in plain words, and uses the slower path if it cannot. There is nothing to install or pin.
* macOS keeps asking for a password. Run check_auth_safety.py and fix what it names.
* The server disappeared. It no longer stops itself on idle, so this means the process died or the laptop slept. Start it again.
H2:Restarting
Use the Restart server button in the admin panel. There is no need to find the process.
H2:If you want this in French or German
Nobody on this project is doing the translation, so this is a handover list rather than a plan. The language codes are already wired: event.venue sets event.language to fr for Paris and de for Berlin and Frankfurt, and the booth passes that around. What is missing is the words. Today every language resolves to the same English copy. These are the surfaces that would have to change, and the order matters because each one is a different kind of work.
* The copy deck, game/config.json. Roughly 400 strings: the intro, the letter, what CoCo says at each of the four locations, the sovereignty lines, the screen furniture and the send-off. This is the bulk of the visible text and the only part that is genuinely just translation. It is structured as one deck per language code, so a fr and a de deck sit alongside the existing en one.
* The strings that never made it into the deck, game/index.html. About twenty short ones are still written into the page itself: button labels, the progress wording, the page indicator, error text. These are the actual blocker. They have to be lifted into config.json before any translator can see them, and that is code work, not language work.
* The prompts, in config.json. Every model call carries its own instruction text. Translating the visitor-facing copy but leaving the prompts in English gets you an English reply under a French label, which is worse than not translating at all. Each prompt needs an explicit instruction to answer in the event language, and then re-testing, because a model told to answer in French will also drift in length and tone.
* The QA agent. It reviews the blueprint before delivery and it does two different things. The deterministic checks match on English words and would silently stop firing against French or German text. The model review call is a prompt and needs the same treatment as above. A QA step that quietly passes everything is the most dangerous failure on this list, because nothing looks broken.
* The document, rendered in game/server.py. Around twenty-five headings and fixed sentences are built into the Word file: section titles, the standing explanations, the first-step wording. The visitor's own words pass through untouched, but everything framing them is English and hardcoded.
* The postcard. The shareable PNG is drawn in the browser per archetype, with its text baked into the drawing code. It also has to survive longer words: German compounds will overrun boxes that were laid out for English, so this one needs re-checking visually rather than just re-stringing.
* The corpus, archetypes.md and marketplace-index.md. Archetype names, the pain text and the dataset descriptions. Note that regenerating these is a pipeline, not an edit: markdown, then the bundle, then the Snowflake tables, in that order.
* This guide, the setup guide and the decision tree. All three are generated from the repo, so they follow the corpus rather than needing separate translation.
What deliberately stays in English: the Snowflake developer guides and feature documentation, because that is how Snowflake publishes them; and the kick-off prompt the visitor pastes into their own Cortex Code session, because that is where it is going to be read.
"""


def main():
    lines = [l for l in BODY.split("\n") if l.strip() != ""]
    text = ""
    spans = []            # (start, end, kind) offsets within the inserted text
    for raw in lines:
        if raw.startswith(H1):
            body, kind = raw[len(H1):], "HEADING_1"
        elif raw.startswith(H2):
            body, kind = raw[len(H2):], "HEADING_2"
        elif raw.startswith(BULLET):
            body, kind = raw[len(BULLET):], "BULLET"
        else:
            body, kind = raw, "NORMAL_TEXT"
        start = len(text)
        text += body + "\n"
        spans.append((start, start + len(body), kind))

    reqs = [{"insertText": {"location": {"index": 1}, "text": text}}]
    # Flatten everything first. Insert inherits neighbouring style, so without
    # this the whole body can land in the outline as a heading.
    reqs.append({"updateParagraphStyle": {
        "range": {"startIndex": 1, "endIndex": 1 + len(text)},
        "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
        "fields": "namedStyleType"}})
    for start, end, kind in spans:
        if kind in ("HEADING_1", "HEADING_2"):
            reqs.append({"updateParagraphStyle": {
                "range": {"startIndex": 1 + start, "endIndex": 1 + end},
                "paragraphStyle": {"namedStyleType": kind},
                "fields": "namedStyleType"}})
        elif kind == "BULLET":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": 1 + start, "endIndex": 1 + end},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})

    print(json.dumps({"documentId": DOC, "requests": reqs}))


if __name__ == "__main__":
    main()
