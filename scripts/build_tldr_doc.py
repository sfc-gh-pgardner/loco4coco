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
pip install snowflake-connector-python python-docx qrcode pyyaml
git clone https://github.com/sfc-gh-pgardner/loco4coco.git ~/.snowflake/cortex/plugins/loco4coco
cd ~/.snowflake/cortex/plugins/loco4coco
python3 deploy/bootstrap.py -c MYBOOTH
python3 game/server.py
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
H2:The four things to check before the doors open
* The admin panel says Model proven, in green.
* The dataset profile matches your city, and datasets loaded is not zero.
* A test visit produces a QR code that opens on your phone.
* The admin panel names the connection you created in step 0, and nothing else.
H2:If something breaks
* The stall shows the wrong city's datasets. You skipped load_context.py, or Apply was not pressed.
* Replies are slow, around twenty seconds each. The model the booth is configured for has stopped working and it has fallen back to the slow path. The admin panel will say so.
* macOS keeps asking for a password. Run check_auth_safety.py and fix what it names.
* The server disappeared. It no longer stops itself on idle, so this means the process died or the laptop slept. Start it again.
H2:Restarting
Use the Restart server button in the admin panel. There is no need to find the process.
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
