#!/usr/bin/env python3
"""Build the v5 character model-sheet jobs (creator approval set), SINGLE-character images only (no grids).

  python3 make_charsheets_v5_input.py --stage 1     # concept: hero full-body + bust candidates per lead -> inputs/charsheets-v5-s1/
  python3 make_charsheets_v5_input.py --stage 2 --picks picks.json   # sheets for the picked heroes -> inputs/charsheets-v5-s2/

Decisions (PRODUCTION-BIBLE "v5 DECISIONS", character-redesign-plan.md lock lists):
  Boy    = direction A, polished: same look as look-test-3 / intro-v3, chin ribbon always with two tails, sandals, no bag/strap/pocket.
  Uncle  = bold variant B: fully bald round head + one highlight, thin long curled-tip black mustache, thick brows, big round body,
           earth-brown linen jacket with mandarin collar and 3 knot buttons, wide orange sash with two long tails, white towel on
           his LEFT shoulder, wide charcoal trousers, straw sandals, NEVER a hat.
  Grandma = plan B "the master": tall round white-grey bun with two crossed wooden pins, calm crescent eyes, deep jade-green high-collar
           jacket, cream apron with orange sash, orange sleeve cord, short thin rolling pin.
Stage 2 refs are the Stage 1 picks (full-body + bust), chosen by eye + qc_stills.py, copied to inputs/charsheets-v5-s2/refs/.
"""
import argparse, json, os

HERE = os.path.dirname(os.path.abspath(__file__))

STYLE = ("Soft watercolor anime, refined TV anime character illustration in the same painted style as the references: gentle clean thin "
         "warm-brown line art, soft painterly shading, warm muted palette (leaf yellow, cream, orange, peach, brown), natural cinematic "
         "light. Plain flat cream background (#FFFAF0) everywhere, no scenery, no props unless named, no frame, no border. "
         "No text, no labels, no numbers, no letters, no logos.")
ONLY = "Exactly ONE character in the whole image: {n}. No other person, no second figure, no duplicate, no reflection."

LOOK = {
    "boy": ("the Boy: a small 7-year-old boy, about 4.5 heads tall, child proportions (he reaches an adult's belt), round soft child face "
            "with full cheeks, big dark-brown oval eyes, short black hair, a pale-straw conical leaf hat (Vietnamese non la) tied with a "
            "wide orange cloth chin ribbon that is ALWAYS visible under the chin, with two ribbon tails hanging down to the chest, a "
            "faded indigo cotton tunic with a diagonal side opening and two cloth knot buttons, a soft orange cloth sash knotted at the "
            "left hip, light hemp trousers rolled to mid-shin, flat brown straw sandals on bare feet. No bag, no shoulder strap, no "
            "pocket, no shoes"),
    "uncle": ("the Uncle: a very large, fat, heavy round man with a big round belly and chubby rosy cheeks, warm, dignified and funny, "
              "a completely bald shiny round head with one small bright highlight (bare skin, NO hair on the head, NO hat, NO cap, NO "
              "headband), thick expressive black eyebrows, small kind dark eyes, a thin long black mustache with the tips curled "
              "upward past his cheeks, an earth-brown linen work jacket with a mandarin collar and exactly three cloth knot buttons, "
              "sleeves pushed to the elbows, a wide orange cloth sash tied in front with two long tails, wide charcoal trousers, "
              "brown straw sandals, a white cotton towel over his LEFT shoulder (the viewer's right when he faces us)"),
    "grandma": ("Grandma, the old dumpling master: a sturdy short elderly woman, about 4.5 heads tall, calm and kind, white-grey hair "
                "pulled back flat into a tall round bun pierced by two crossed plain wooden pins, calm half-closed crescent eyes with "
                "smile lines, small straight brows, round-square face with soft cheeks, a deep jade-green cotton jacket with a high "
                "collar and a side opening, sleeves tied back above the elbows with an orange cord, a long plain cream apron to "
                "mid-shin with an orange apron sash, dark trousers, black cloth shoes, a little flour on her hands, a short thin "
                "wooden rolling pin tucked in the apron sash. No glasses, no earrings, no headscarf, no sage or pale-green clothes"),
}
NAME = {"boy": "the Boy", "uncle": "the Uncle", "grandma": "Grandma"}
AVOID = {
    "boy": "second person, adult, bag, shoulder strap, pocket, shoes, missing chin ribbon, thin string, white clothes, kimono, text",
    "uncle": "hat, cap, headband, hair on the head, beard, side fringe, thick bushy mustache, kimono, gi, karate uniform, second person, "
             "child, text",
    "grandma": "glasses, earrings, headscarf, light green jacket, sage-green, second person, child, kimono, text",
}


def refs_stage1(c):
    if c == "boy":
        return [{"path": "refs/boy_head.jpg", "role": "the Boy's face, hat and painting style (head only; ignore its background and any other person; "
                 "its shoulder strap must NOT be copied)"},
                {"path": "refs/boy_head2.jpg", "role": "the same Boy, second angle of the face and hat (ignore its background and any strap)"}]
    if c == "uncle":
        return [{"path": "refs/uncle_body.jpg", "role": "the Uncle's body: linen jacket cloth, mandarin collar, knot buttons, towel, orange sash, "
                 "trousers, sandals, and the painting style. His head is NOT in this reference: draw the head as described in the text"}]
    return [{"path": "refs/grandma_face.jpg", "role": "painting style and the kind round face language only. Her clothes and hair in this "
             "reference are OLD and must NOT be copied: use the new clothes and the bun described in the text"}]


def stage1():
    out = os.path.join(HERE, "inputs", "charsheets-v5-s1")
    items = []
    seeds = {"boy": 5100, "uncle": 5200, "grandma": 5300}
    for c in ("boy", "uncle", "grandma"):
        full = (f"Character design hero image. {ONLY.format(n=NAME[c])} {LOOK[c]}. Full body from head to feet, front view, standing "
                "in a relaxed neutral pose with arms slightly away from the body, calm friendly expression, both feet visible on a "
                "plain floor line. Vertical composition")
        bust = (f"Character design portrait. {ONLY.format(n=NAME[c])} {LOOK[c]}. Head and shoulders portrait, slight three-quarter "
                "view, warm calm expression, the face large and clear. Vertical composition")
        nfull = 4 if c == "uncle" else 3
        items.append(dict(id=f"{c}_full", seed=seeds[c], variants=nfull, refs=refs_stage1(c), keep_characters=(c == "boy"),
                          prompt=full, style=STYLE, negative=AVOID[c], width=768, height=1344, orientations=["portrait"]))
        items.append(dict(id=f"{c}_bust", seed=seeds[c] + 50, variants=3, refs=refs_stage1(c), keep_characters=(c == "boy"),
                          prompt=bust, style=STYLE, negative=AVOID[c], width=768, height=960, orientations=["portrait"]))
    os.makedirs(out, exist_ok=True)
    json.dump({"defaults": {"backend": "klein", "ref_max": 640, "orientations": ["portrait"]}, "images": items},
              open(os.path.join(out, "images.json"), "w"), indent=1)
    print("stage 1:", sum(i["variants"] for i in items), "images ->", out)


EXPR = {
    "boy": ["curious and neutral, calm friendly closed-mouth look", "warm gentle smile", "eyes closed in a soft tender smile",
            "wonder: eyes wide and sparkling, small round open mouth", "deadpan: flat half-lidded eyes, straight mouth",
            "explaining: one eyebrow raised, half smile, mouth slightly open as if talking",
            "surprised: eyebrows high, eyes wide, mouth open", "tasting bliss: eyes closed, cheeks puffed and blushing, happy",
            "worried: eyebrows tilted up-in, small trembling mouth", "missing Dad: eyes looking down, sad, quiet, shadow over the eyes",
            "scared: eyes wide with tiny pupils, mouth open, a sweat drop", "determined: eyebrows down, firm closed mouth, chin set"],
    "uncle": ["hungry and hopeful: nose raised, eyes bright, mouth slightly open", "big belly laugh: eyes closed in happy arcs, mouth wide open",
              "heroic: chest out, eyebrows high, proud grin, mustache tips curled up (For dumpling research!)",
              "first-bite bliss: eyes closed, happy tears, glowing cheeks, mouth full",
              "burned tongue: tongue out, steam from the ears, spiral eyes, comic",
              "humbled: head lowered, eyebrows tilted, mustache drooping", "shock: eyes white and round, jaw dropped, mustache bristling straight",
              "panic: tiny pupils, mouth wide open, sweat drops flying", "sneaky: side-eye, one eyebrow down, sly grin",
              "wise and tender: soft kind eyes, small closed smile, calm", "indignant: puffed red cheeks, eyebrows down",
              "food coma: half-closed eyes, content smile, tiny drool"],
    "grandma": ["calm master: crescent half-closed eyes, faint smile", "warm grandmother smile, crescent eyes",
                "focused: eyes cast down, lips pressed, concentrating", "knowing smirk: one eyebrow raised",
                "freeze-stare: eyes fully open, wide awake and sharp, mouth closed", "delighted laugh: one hand over her mouth, eyes crinkled",
                "stern: one eye open, firm mouth", "mild surprise: eyebrows lifted, eyes opening a little",
                "teaching: mouth open mid-sentence, pointing with the short rolling pin", "moved, remembering: soft wet eyes, trembling gentle smile",
                "deadpan: flat half-lidded eyes, straight mouth", "proud nod: eyes closed, chin up, content smile"],
}
VIEWS = [("front", "front view, standing straight, arms relaxed at the sides"),
         ("q34", "three-quarter view (body and face turned about 45 degrees to the viewer's left), arms relaxed"),
         ("side", "pure side profile view facing the viewer's left, arms relaxed"),
         ("back", "back view seen from directly behind, arms relaxed")]
POSES = {
    "boy": [("stand", "a natural relaxed standing pose in three-quarter view, one hand pushing the brim of his hat up with one finger, curious "
                      "friendly look"),
            ("comic", "a comedic pose: jumping back in cartoon surprise, both arms up, eyes wide, mouth open, a sweat drop, hat bouncing")],
    "uncle": [("stand", "a natural standing pose in three-quarter view, hands clasped on his big belly, content warm smile, nose sniffing"),
              ("comic", "his signature comedic pose: chest out, long wooden chopsticks raised high like a trophy, eyebrows high, proud grin, "
                        "mustache curled up, shouting 'For dumpling research!'")],
    "grandma": [("stand", "a natural standing pose in three-quarter view, hands folded on her apron, perfectly still, one eye just opening"),
                ("comic", "a comedic pose: pointing sharply with her short rolling pin, deadpan flat stare, one eyebrow raised")],
}
LINEUPS = [("lineup_boy_uncle", ["boy", "uncle"],
            "the Boy (small, his head top at the Uncle's belt) standing next to the Uncle (very large, a head and a half taller than anyone), both "
            "full body, side by side, front view, relaxed, friendly, both feet visible"),
           ("lineup_grandma_boy", ["grandma", "boy"],
            "Grandma (short and sturdy, her bun reaching above the Boy's hat) standing next to the Boy (small), both full body, side by side, "
            "front view, relaxed, friendly, both feet visible")]
ROLE = {"boy": "the Boy exactly (face, hat, chin ribbon, tunic, sash, trousers, sandals, colors, proportions); only this one child",
        "uncle": "the Uncle exactly (bald head, mustache, jacket, towel, sash, trousers, sandals, colors, proportions); only this one man",
        "grandma": "Grandma exactly (bun with crossed pins, face, jade jacket, apron, colors, proportions); only this one woman"}


def stage2(picks):
    out = os.path.join(HERE, "inputs", "charsheets-v5-s2")
    os.makedirs(os.path.join(out, "refs"), exist_ok=True)
    import shutil
    P = json.load(open(picks)); items = []; seed = {"boy": 6100, "uncle": 6200, "grandma": 6300}
    for c in ("boy", "uncle", "grandma"):
        for k in ("full", "bust"):
            shutil.copy(P[c][k], os.path.join(out, "refs", f"{c}_{k}.png"))
        rf = [{"path": f"refs/{c}_full.png", "role": ROLE[c] + " (full body)"}, {"path": f"refs/{c}_bust.png", "role": "the same character, face close-up"}]
        for k, (vid, vt) in enumerate(VIEWS):
            items.append(dict(id=f"{c}_turn_{vid}", seed=seed[c] + 10 * k, variants=2 if c == "uncle" else 1, refs=rf, prompt=(
                f"Character model sheet view. {ONLY.format(n=NAME[c])} {LOOK[c]}. Full body from head to feet, {vt}, calm neutral friendly "
                "expression, feet on a plain floor line, exactly the same design, size and colors as the references. Vertical composition"),
                style=STYLE, negative=AVOID[c], width=768, height=1344, ref_max=640))
        for k, (vid, vt) in enumerate(POSES[c]):
            items.append(dict(id=f"{c}_pose_{vid}", seed=seed[c] + 100 + k, variants=1, refs=rf, prompt=(
                f"Character pose illustration. {ONLY.format(n=NAME[c])} {LOOK[c]}. Full body from head to feet, {vt}. Exactly the same design "
                "and colors as the references. Vertical composition"), style=STYLE, negative=AVOID[c], width=768, height=1344, ref_max=640))
        for k, e in enumerate(EXPR[c]):
            items.append(dict(id=f"{c}_expr{k + 1:02d}", seed=seed[c] + 200 + k, variants=2 if c == "uncle" else 1, refs=rf[1:] + rf[:1], prompt=(
                f"Character expression portrait. {ONLY.format(n=NAME[c])} {LOOK[c]}. Head and shoulders portrait, front view with a very slight "
                f"three-quarter turn, expression: {e}. The same face design, headwear or bare head, hair and costume as the references. "
                "Square composition, vertical composition"), style=STYLE, negative=AVOID[c], width=768, height=768, ref_max=512))
    for lid, who, txt in LINEUPS:
        rf = [{"path": f"refs/{w}_full.png", "role": ROLE[w] + " (full body)"} for w in who]
        for w in who:
            if not os.path.exists(os.path.join(out, "refs", f"{w}_full.png")):
                pass
        items.append(dict(id=lid, seed=6900 + len(items), variants=2, refs=rf, orientations=["landscape"], keep_characters=True, prompt=(
            f"Scale lineup. Exactly TWO characters in the whole image, no third person: {txt}. Each keeps exactly the design of its reference. "
            "Wide horizontal 16:9 composition"), style=STYLE, negative="third person, duplicate, hat on the Uncle, text",
            width=768, height=1344, ref_max=576))
    json.dump({"defaults": {"backend": "klein", "orientations": ["portrait"]}, "images": items}, open(os.path.join(out, "images.json"), "w"), indent=1)
    print("stage 2:", sum(i["variants"] if "variants" in i else 1 for i in items), "images ->", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, default=1)
    ap.add_argument("--picks")
    a = ap.parse_args()
    if a.stage == 1:
        stage1()
    else:
        stage2(a.picks)
