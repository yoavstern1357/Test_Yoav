#!/usr/bin/env python3
"""GPU images input for Episode 1 v4.4: a START and an END keyframe for every I2V clip (both orientations), from scripts/episode-01-v4.4.md.
The END keyframe is generated from the START keyframe (@ reference) so characters and place stay identical.
    python3 make_ep01v44_stills_input.py [name] [C01 C02 ...]    -> inputs/<name> (default ep01v44-stills; no clip ids = all)"""
import json, os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "paper"))
from parse_ep01v44 import parse

STYLE = ("Style: delicate soft anime with watercolor washes, thin warm-brown line art, gentle pastel-warm palette, paper grain, airy light, "
         "expressive anime-comedy faces. Original house style. No text, no letters, no logos.")
CAST = {
 "boy": "the Boy (small, about 7, conical leaf hat with orange chin ribbon, indigo tunic, orange sash)",
 "uncle": "the Uncle (VERY FAT, bald, thin mustache, brown linen jacket, orange sash; comically exaggerated anime expressions)",
 "grandma": "Grandma (short, round, old, grey bun, no hat, green jacket, cream apron)",
}
R = {
 "boy": {"path": "refs/boy_only.jpg", "role": "the Boy: his face, hat, village clothes and colors to keep exactly (only the boy)"},
 "uncle": {"path": "refs/both_eating.jpg", "role": "the Uncle (the big fat bald man with the mustache): face, body shape and clothes to keep exactly; the boy beside him is the Boy"},
 "pair": {"path": "refs/fat_uncle_pool.jpg", "role": "body-type reference: the Uncle is this FAT (big round belly, heavy round body); the boy is the Boy; keep both exactly"},
 "grandma": {"path": "refs/grandma_ref.jpg", "role": "Grandma: her face, grey bun, jacket and apron to keep exactly"},
 "style": {"path": "refs/style_s1.jpg", "role": "painting style, line quality and light reference only (do not copy the characters or the place)"},
}


def who(text):
    t = text
    w = []
    if re.search(r"\bBoy\b", t): w.append("boy")
    if re.search(r"\bUncle", t): w.append("uncle")
    if re.search(r"Grandma", t): w.append("grandma")
    return w


def comp(zone):
    return (" Composition: keep the lowest third of the frame calm (floor, counter or background); faces and action in the upper two thirds." if zone == "bottom"
            else " Composition: keep the top third of the frame calm (sky, wall or background); faces and action in the lower two thirds.")


FIX = {"C07": ["landscape"], "C08": None, "C13": None, "C16": ["landscape"], "C21": ["portrait"], "C24": ["portrait"], "C26": ["landscape"],
       "C30": ["landscape"], "C32": ["end", "portrait"], "C35": ["portrait"], "C37": ["end", "portrait"]}      # second pass: items of the first pass with duplicates, text or glitches
NEGATIVE = "duplicate characters, two uncles, two boys, extra people, text, letters, black patches, cropped faces"


def main():
    fix = len(sys.argv) > 1 and sys.argv[1] == "fix"
    if fix:
        sys.argv.pop(1)
    name = sys.argv[1] if len(sys.argv) > 1 else ("ep01v44-stills-fix" if fix else "ep01v44-stills")
    only = [a for a in sys.argv[2:]] or (list(FIX) if fix else [])
    out = os.path.join(HERE, "inputs", name)
    os.makedirs(os.path.join(out, "refs"), exist_ok=True)
    src = os.path.join(HERE, "inputs", "ep01v43-stills", "refs")
    for f in ("boy_only.jpg", "fat_uncle_pool.jpg", "both_eating.jpg", "style_s1.jpg"):
        shutil.copyfile(os.path.join(src, f), os.path.join(out, "refs", f))
    shutil.copyfile(os.path.join(HERE, "inputs", "ep01v43-stills-fix", "refs", "grandma_ref.jpg"), os.path.join(out, "refs", "grandma_ref.jpg"))
    items, seed = [], 5000
    for c in parse():
        if c["method"] == "CODE" or (only and c["id"] not in only):
            continue
        seed += 7
        text = c["start_kf"] + " " + c["end_kf"]
        ws = who(text)
        if re.search(r"Dad's silhouette|silhouette from behind", text):
            ws = []
        c = dict(c, end_kf=re.sub(r"ink-bloom title in the sky:.*", "an empty soft sky above (no text anywhere).", c["end_kf"]))
        refs = []
        if "uncle" in ws and "boy" in ws:
            refs = [R["pair"], R["boy"]] if fix else [R["pair"], R["uncle"]]
        elif "uncle" in ws:
            refs = [R["pair"]] if fix else [R["uncle"], R["pair"]]
        elif "boy" in ws:
            refs = [R["boy"]]
        if "grandma" in ws:
            refs.append(R["grandma"])
        keep = bool(refs)
        if not refs:
            refs = [R["style"]]
        cast = " ".join(f"{CAST[k]}." for k in ws)
        base = (cast + " " if cast else "") + c["start_kf"] + comp(c["zone"]) + " " + STYLE
        it = {"id": c["id"], "seed": seed + (900 if fix else 0), "variants": 2 if fix else 1, "refs": refs[:3], "prompt": base}
        if fix:
            it["negative"] = NEGATIVE
        if not keep:
            it["keep_characters"] = False
        items.append(it)
        endp = ("Same scene, same place, same characters with the exact same faces, hats and clothes as image 1 (the start frame), a moment later: "
                + c["end_kf"] + comp(c["zone"]) + " " + STYLE)
        e = {"id": c["id"] + "_end", "seed": seed + (900 if fix else 0), "variants": 2 if fix else 1, "refs": [{"path": "@" + c["id"], "role": "the START frame of the same shot: keep place, characters, outfits and style identical"}] + refs[:2], "prompt": cast + " " + endp if cast else endp}
        if not keep:
            e["keep_characters"] = False
        if fix:
            e["negative"] = NEGATIVE
            e["refs"][0]["path"] = "@" + c["id"] + "__v1"
        items.append(e)
    if fix:                                    # keep only the listed items / orientations
        kept = []
        for it in items:
            base = it["id"].replace("_end", "")
            spec = FIX.get(base, "x")
            if spec == "x":
                continue
            isend = it["id"].endswith("_end")
            if spec is not None:
                if "end" in spec and not isend and "start" not in spec and "end" in spec and base not in ("C32", "C37"):
                    pass
                orient = [o for o in spec if o in ("portrait", "landscape")]
                if orient:
                    it["orientations"] = orient
                if spec == ["end"] and not isend:
                    continue
            kept.append(it)
        items = kept
    job = {"defaults": {"backend": "klein", "width": 768, "height": 1344, "variants": 1, "ref_max": 704, "orientations": ["portrait", "landscape"]}, "images": items}
    json.dump(job, open(os.path.join(out, "images.json"), "w"), indent=1, ensure_ascii=False)
    print(len(items), "items ->", out)


if __name__ == "__main__":
    main()
