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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, default=1)
    ap.add_argument("--picks")
    a = ap.parse_args()
    if a.stage == 1:
        stage1()
    else:
        raise SystemExit("stage 2 builder is added after the Stage 1 picks")
