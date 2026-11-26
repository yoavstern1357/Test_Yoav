#!/usr/bin/env python3
"""Build inputs/charsheets-v45/images.json: single-character model sheets for v4.5 (fix-plan.md Fix 1 and Fix 5a).

Per character (Boy, Uncle, Grandma): turnaround (front, 3/4, side, back), expression sheet (8 expressions),
hand-pose sheet, and a mouth-shape sheet for lip-sync sprites. Each sheet shows ONE character only, on plain cream.
References are crops that contain only that character:
  boy_a      gpu-results intro-v3 I1_bite__v2 (left part, the Boy only)
  boy_b      ep01v44-stills-fix refs/boy_only.jpg (right edge with the Uncle cut off)
  uncle_a/b  gpu-results intro-v3 I1_bite__v2 / I6_chomp__v2 (the LOCKED Uncle, right part only)
  grandma_a  specs/frames/ep01v44/C12.png (right part, Grandma only)
  grandma_b  ep01v44-stills-fix refs/grandma_ref.jpg (the v4.4 Grandma sheet)
    python3 make_charsheets_v45_input.py   # rewrites images.json (the refs/ crops are committed)
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "charsheets-v45")

LOOK = {
    "boy": ("the Boy: a small boy about 7 years old (child proportions, head large for the body, reaches an adult's belt), round soft "
            "child face, big curious dark eyes, short black hair, conical woven leaf hat with an orange chin ribbon, loose faded indigo "
            "cotton village tunic with side buttons, light hemp trousers rolled to the shin, soft orange cloth sash tied at the waist, "
            "straw sandals, small cream cloth shoulder bag"),
    "uncle": ("the Uncle: a VERY FAT grown man with a big round belly, heavy round body, chubby cheeks, bald head with a little dark "
              "hair at the back, thin black mustache, loose earth-brown linen work jacket with cloth knot buttons, wide dark trousers, "
              "wide orange cloth sash tied at the side with long ends, brown sandals, a white towel over one shoulder"),
    "grandma": ("Grandma: a short, round, kind old woman, grey hair in a neat bun, rosy cheeks, gentle smiling eyes, pale sage-green "
                "long-sleeved tunic with buttons, a long white apron, sage-green trousers, brown shoes"),
}
NAME = {"boy": "Boy", "uncle": "Uncle", "grandma": "Grandma"}
HANDS = {"boy": "small child hands with short soft fingers and indigo tunic cuffs",
         "uncle": "big chubby man's hands with thick short fingers and brown linen jacket cuffs",
         "grandma": "small soft old woman's hands, a little flour on the fingertips, sage-green sleeve cuffs"}
REFS = {
    "boy": [{"path": "refs/boy_a.jpg", "role": "the Boy (face, hat, clothes, colors, proportions); only this one child"},
            {"path": "refs/boy_b.jpg", "role": "the same Boy standing (full body); only this one child"}],
    "uncle": [{"path": "refs/uncle_a.jpg", "role": "the Uncle (face, mustache, body size, clothes, colors); only this one man"},
              {"path": "refs/uncle_b.jpg", "role": "the same Uncle in another pose (body shape, sash, towel); only this one man"}],
    "grandma": [{"path": "refs/grandma_a.jpg", "role": "Grandma (face, hair bun, clothes, colors); only this one woman"},
                {"path": "refs/grandma_b.jpg", "role": "the same Grandma standing (full body); only this one woman"}],
}
STYLE = ("Delicate soft anime character-design sheet in the same painted style as the references: gentle clean thin warm-brown line "
         "art, soft painterly shading, warm muted palette, subtle paper grain. Plain flat cream background (#FFFAF0) everywhere, "
         "no scenery, no props unless named, no frames or borders. No text, no labels, no numbers, no letters, no logos.")
ONLY = "Exactly ONE character on the whole sheet: {n}. No other person anywhere on the sheet."

EXPR = ("eight head-and-shoulders portraits of {who}, arranged in a clean 4 x 2 grid, every portrait the same size, facing the viewer "
        "(front view, very slight three-quarter turn), same lighting: top row left to right: neutral calm; big laugh (eyes squeezed shut, "
        "mouth wide open); shocked (eyes very wide, jaw dropped); scared (wide trembling eyes, sweat drop, mouth open in fear); bottom "
        "row left to right: smug (half-closed eyes, sly closed-mouth smile, chin lifted); sad-tender (soft wet eyes, small gentle sad "
        "smile); determined (furrowed brows, firm closed mouth); deadpan (flat half-lidded eyes, straight mouth, no emotion). "
        "Expressive anime-comedy faces but the same face design, hat/hair and clothes in all eight")
TURN = ("character turnaround of {who}, drawn four times side by side in one row, full body from head to feet, standing in a relaxed "
        "neutral pose with arms slightly away from the body, the same height and scale in all four, feet on the same baseline: "
        "1) front view, 2) three-quarter view, 3) side profile view, 4) back view. Calm neutral friendly expression")
HAND = ("hand-pose sheet: only the hands of {who} ({hands}), each hand with exactly five fingers, eight drawings in a 4 x 2 grid: "
        "open palm wave; pointing index finger; thumbs up; closed fist; holding chopsticks; holding a small round steamed dumpling "
        "between two fingers; relaxed hand seen from the side; counting three on the fingers. Only hands with a little of the sleeve, "
        "no faces, no bodies")
MOUTH = ("lip-sync mouth chart of {who}: the same close-up face drawn six times in a 3 x 2 grid, front view, IDENTICAL head, "
         "eyes, eyebrows, {hair} and lighting in all six panels; ONLY the mouth changes: 1) closed relaxed mouth (M, B, P); "
         "2) slightly open, teeth almost together (S, T, E); 3) open mouth (A as in 'cat'); 4) wide open mouth (AH, shout); "
         "5) round open O mouth (OH); 6) small pursed round mouth (OO, W). Calm neutral eyes in every panel")
HAIR = {"boy": "hat", "uncle": "bald head and mustache", "grandma": "hair bun"}


def item(cid, ch, kind, text, seed, variants):
    who = f"the {NAME[ch]} ({LOOK[ch].split(': ', 1)[1]})" if kind != "hands" else f"the {NAME[ch]}"
    who = who.replace("the Grandma", "Grandma")
    body = text.format(who=who, hands=HANDS[ch], hair=HAIR[ch])
    return {"id": f"{ch}_{kind}", "seed": seed, "variants": variants, "refs": REFS[ch],
            "prompt": f"Character model sheet. {ONLY.format(n='the ' + NAME[ch] if ch != 'grandma' else 'Grandma')} Sheet content: {body}.",
            "style": STYLE}


def main():
    items = []
    for k, ch in enumerate(["boy", "uncle", "grandma"]):
        base = 4500 + 100 * k
        items.append(item("turn", ch, "turn", TURN, base + 1, 4))
        items.append(item("expr", ch, "expr", EXPR, base + 11, 4))
        items.append(item("hands", ch, "hands", HAND, base + 21, 4))
        items.append(item("mouths", ch, "mouths", MOUTH, base + 31, 2))
    data = {"defaults": {"backend": "klein", "width": 768, "height": 1344, "size_landscape": [1536, 864], "variants": 4,
                         "ref_max": 704, "orientations": ["landscape"]},
            "images": items}
    json.dump(data, open(os.path.join(OUT, "images.json"), "w"), indent=1)
    print(len(items), "items,", sum(i["variants"] for i in items), "images ->", OUT)


if __name__ == "__main__":
    main()
