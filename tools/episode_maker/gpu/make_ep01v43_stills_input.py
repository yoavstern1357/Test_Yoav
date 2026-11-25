#!/usr/bin/env python3
"""Builds inputs/ep01v43-stills/images.json: every Episode 1 (v4.3) image-to-video start still (+ C14 end still, title plate,
Grandma sheet) in the approved style S1 "soft watercolor anime", both orientations. Run: python3 make_ep01v43_stills_input.py"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "ep01v43-stills")

STYLE = ("Style: delicate soft anime with watercolor washes, thin warm-brown line art, gentle pastel-warm palette, visible paper grain, "
         "airy light, storybook feeling. Original house style, not imitating any specific studio. No text, no letters, no logos.")
BOY = ("the Boy (about 7, small, reaching only the man's belt, round soft child face, big curious dark eyes, short black hair, Vietnamese conical leaf hat "
       "with an orange chin ribbon, faded indigo village tunic with side buttons, light hemp trousers rolled to the shin, soft orange cloth sash, straw sandals, small cloth bag)")
UNCLE = ("the Uncle (a very big, FAT, bald man: big round belly, heavy round body, chubby cheeks, thin black mustache, earth-brown linen work jacket "
         "with cloth knot buttons stretched over his belly, wide dark trousers, wide orange cloth sash, towel over one shoulder, straw sandals)")
GRANDMA = ("Grandma (a short, round, kind old woman with a round rosy face, small gentle smile, grey hair in a small bun with a wooden pin, "
           "sage-green village jacket, cream apron, flour on her hands)")

R_BOTH = {"path": "refs/both_standing.jpg", "role": "the Boy and the Uncle: their faces, hat, village clothes and colors to keep exactly"}
R_FAT = {"path": "refs/fat_uncle_pool.jpg", "role": "body-type reference: the Uncle is this FAT (big round belly, heavy round body, chubby cheeks); same face and clothes"}
R_STYLE = {"path": "refs/style_s1.jpg", "role": "painting style, line quality and light reference only (do not copy the characters or the place)"}
R_G = {"path": "@G00_grandma_ref__v1", "role": "Grandma: her face, grey bun, jacket and apron to keep exactly"}

CHARS = [R_BOTH, R_FAT]


def item(i, seed, prompt, refs, v=2, **kw):
    d = {"id": i, "seed": seed, "variants": v, "refs": refs, "prompt": prompt.strip() + " " + STYLE}
    if refs is NOCHAR:
        pass
    d.update(kw)
    return d


NOCHAR = [R_STYLE]
items = []
n = [3000]


def add(i, prompt, refs, v=2, **kw):
    n[0] += 1
    d = {"id": i, "seed": n[0], "variants": v, "refs": refs, "prompt": prompt.strip() + " " + STYLE}
    if refs is NOCHAR:
        d["keep_characters"] = False
    d.update(kw)
    items.append(d)


# phase 0: Grandma character sheet (portrait only), reused as a reference by every Grandma still
add("G00_grandma_ref",
    f"Character reference sheet of {GRANDMA}. One character only, full body, standing relaxed, facing slightly to the side, hands gently together at her apron, "
    "plain warm cream background, no props. She is drawn in the same delicate soft anime style as the characters of the style reference, a kind village cook.",
    NOCHAR, v=3, orientations=["portrait"])

add("C01", "Macro close-up: one xiaolongbao soup dumpling lifted on a pair of chopsticks above a bamboo steamer basket, the skin so thin that the golden soup shows through, "
    "the dumpling sags like a small water balloon, thin steam drifting, warm morning light, shallow depth of field. No people.", NOCHAR)
add("C02", f"Medium shot in an old canal-town lane (stone bridge and canal softly blurred behind): {BOY} stands facing the viewer with a small warm smile, holding a pair of chopsticks like a microphone. "
    f"Behind him, sitting on a low stool, {UNCLE} presses an ice pack to his cheek and fans his tongue with a napkin, faint steam from his ears, dignified and slightly sulky. Morning light.", CHARS)
add("C05", f"Interior of a Shanghai metro car sliding out of the city past low houses seen through the windows, soft daylight. {BOY} sits on a seat with an old leather journal open on his knees, one finger under the handwriting. "
    f"Beside him {UNCLE} sits upright, fast asleep, hugging a thermos, mouth slightly open. Calm, quiet mood.", CHARS)
add("C07", f"Old canal lane in warm morning light, a stone bridge at the left, willow branches. {BOY} walks toward the viewer mid-stride, looking at the lens with a relaxed smile, a chopstick microphone in his hand. "
    f"Far behind him in the lane {UNCLE} ambles along rubbing his stomach.", CHARS)
add("C08", f"Wide shot of an old canal town: two stout old brick pagodas standing side by side (small and squat, no hero angle) under a soft sky with wind chimes at a nearby eave. "
    f"In the foreground, small in the frame, {BOY} points up at them and beside him {UNCLE} looks up in quiet wonder.", CHARS)
add("C09", f"A tiny generic old dumpling stall with no sign text, stacked bamboo steamers breathing steam. {GRANDMA} folds a dumpling with quick hands behind the counter. "
    f"{BOY} stands at the counter, leaning in, curious and a little shy. Behind him, soft and out of focus, {UNCLE} has his nose in the steam.", CHARS + [R_G], v=3)
add("C10", "Macro on a wooden chopping board: a block of amber pork-skin jelly, translucent and glossy, and a heavy kitchen knife beside it, a bowl of pink minced pork at the side. Warm kitchen light, steam far behind. "
    "No people, hands not visible.", NOCHAR, v=3)
add("C11", "Macro on a bamboo steamer basket with its lid just lifted, steam parting, one soup dumpling in the middle with its thin skin glowing warmly from inside, golden light. No people.", NOCHAR, v=3)
add("C12", f"Close shot across the stall counter: {GRANDMA}'s hands pleating a dumpling with quick fingers in the foreground; {BOY}'s chin and eyes just above the counter edge watching closely; "
    f"{UNCLE} at the edge of the frame counting on his fingers.", CHARS + [R_G], v=3)
add("C13", f"At a dumpling stall counter, {GRANDMA} sets down a bamboo basket of six steaming dumplings, steam parting. {UNCLE}'s chopsticks are already darting toward it, "
    f"and {BOY} holds out a hand with his chopstick microphone to block them like a barrier arm, worried.", CHARS + [R_G], v=3)
add("C14", f"Close medium shot: {UNCLE} holds a whole steaming dumpling at his lips with chopsticks, eyes shining, just about to bite, proud and eager. Dumpling stall behind, warm light.", CHARS, v=3)
add("C14_end", f"{UNCLE} flies two meters up in the air above a dumpling stall, arms and legs spread, eyes squeezed, red face, both ears jetting long jets of white steam, his thin mustache standing straight up like antennae. "
    "This is the big comic burn gag: a big reaction, playful, never scary.", CHARS, v=3)
add("C15", f"At the dumpling stall, {UNCLE} skids to a stop, sandals sliding, tongue sticking out, red-faced, steam leaking from one ear, fanning his tongue with one hand, humbled. "
    f"{GRANDMA} already holds out a cup of cold water to him, kind and a little teasing. {BOY} stands beside him, concerned, hiding a smile.", CHARS + [R_G], v=3)
add("C16", "Macro: a pair of chopsticks gently pinching a soup dumpling by its twisted top knot, lifting it a little, a soup spoon waiting right below, steam rising, warm stall light. No people, no faces.", NOCHAR, v=3)
add("C17", "Macro on a soup dumpling resting on a white soup spoon, a chopstick tip just above its skin about to open a tiny hole, a thread of steam, a glint of golden soup. No people.", NOCHAR, v=3)
add("C18", f"Medium close-up: {UNCLE} with a soup spoon at his lips, eyes closed, shoulders relaxed, a small blissful smile, soft warm light. "
    f"In the foreground, partly out of focus, {BOY} watches him and nods hopefully. {GRANDMA} is a soft shape in the background.", CHARS + [R_G], v=3)
add("C23", f"At the dumpling stall, a rolled-up paper scroll lies on the counter. {UNCLE} stands in a proud hero pose with a napkin tied on as a cape and a soup spoon raised like a sword, chin lifted, dignified. "
    f"{BOY} stands beside him giving him a warm, amused, dry look.", CHARS)
add("C24", f"Medium shot across the stall counter: {GRANDMA} stops mid-fold with a half-folded dumpling in her hands and looks up straight at {BOY}'s conical hat, amazed. "
    f"{BOY} stands at the counter looking up at her.", [R_BOTH, R_G], v=3)
add("C25", "Sepia and warm amber dusk. The silhouette of a man seen from BEHIND (no face visible), wearing a Vietnamese conical leaf hat, sitting on a small wooden stool at a dumpling stall counter, "
    "lantern light glowing, holding a spoon over a steaming dumpling. Quiet, tender and nostalgic. Only a warm sepia silhouette, no face.", [R_STYLE], v=3, keep_characters=False)
add("C26", f"{BOY} and {UNCLE} stand side by side at the stall in warm evening light; {UNCLE} holds a spoon with a cooled soup dumpling, calm, a little hoarse and tender, looking at the boy. "
    f"{BOY} looks up at him. Quiet warm mood.", CHARS)
add("C27", f"{GRANDMA} leans over the counter and points far away to the south with a secret smile. In the foreground {BOY} and {UNCLE} look where she points, {UNCLE} perking up with hungry eyes.",
    CHARS + [R_G], v=3)
add("C28", f"Soft close-up portrait of {BOY} in warm evening light, a small tender smile, looking straight into the lens, the orange chin ribbon of his hat stirring. Calm, heartfelt.",
    [R_BOTH], v=3)
add("C29", f"{BOY} stands in the foreground looking at the viewer. Behind him {UNCLE} sits with his tongue in a bucket of ice, giving a happy thumbs up, and beside him a calm cartoon camel stares straight into the lens. "
    "Funny, warm, soft evening light.", CHARS)
add("C06_plate", "Quiet watercolor plate of an old canal town at dawn: a stone arch bridge, willows, low brick houses with grey tile roofs, a few small wooden boats, mist on the water, "
    "soft rose and gold sky. Wide, calm, a lot of empty sky at the top for a title. No people.", NOCHAR, v=2)


# ---- fix pass (python3 make_ep01v43_stills_input.py fix): re-roll the stills where the first pass had the wrong cast / a hat on the Uncle / one pagoda
if len(sys.argv) > 1 and sys.argv[1] == "fix":
    R_BOY = {"path": "refs/boy_only.jpg", "role": "the Boy: his face, hat, village clothes and colors to keep exactly (only the boy, no other person)"}
    NOHAT = " The Uncle's head is bald and completely bare: he wears NO hat at all."
    GRAN = " Grandma has grey hair in a bun and wears NO hat; only the Boy wears a conical leaf hat."
    keep = {"C08": dict(extra=" There are exactly TWO separate small brick pagodas standing side by side in the background, both clearly visible."),
            "C12": dict(extra=GRAN + " Grandma clearly stands behind the counter pleating a dumpling in the foreground.", portrait_only=True),
            "C14_end": dict(extra=NOHAT, land_only=True),
            "C15": dict(extra=NOHAT + GRAN, land_only=True),
            "C24": dict(extra=GRAN + " Only two people are in the picture: Grandma and the Boy. The Uncle is NOT in the picture.", refs=[R_BOY, R_G], portrait_only=True),
            "C28": dict(extra=" Only the Boy is in the picture, alone, no other person, soft blurred village background.", refs=[R_BOY])}
    out = []
    for it in items:
        k = keep.get(it["id"])
        if not k:
            continue
        it = dict(it, prompt=it["prompt"].replace(STYLE, k["extra"].strip() + " " + STYLE), variants=4, seed=it["seed"] + 500)
        if "refs" in k:
            it["refs"] = k["refs"]
        if k.get("portrait_only"):
            it["orientations"] = ["portrait"]
        if k.get("land_only"):
            it["orientations"] = ["landscape"]
        out.append(it)
    items = out
    OUT = OUT + "-fix"
    # the Grandma reference is the first-pass sheet: copy it from the results into refs/ so this job is self-contained
    for it in items:
        for r in it["refs"]:
            if isinstance(r, dict) and r["path"].startswith("@"):
                r["path"] = "refs/grandma_ref.jpg"

job = {"defaults": {"backend": "klein", "width": 768, "height": 1344, "variants": 2, "ref_max": 704, "orientations": ["portrait", "landscape"]}, "images": items}
os.makedirs(OUT, exist_ok=True)
json.dump(job, open(os.path.join(OUT, "images.json"), "w"), indent=1, ensure_ascii=False)
print(len(items), "items;", sum(i["variants"] * (1 if i.get("orientations") == ["portrait"] else 2) for i in items), "images")
