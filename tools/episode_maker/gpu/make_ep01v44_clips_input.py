#!/usr/bin/env python3
"""GPU clips input for Episode 1 v4.4: first+last-frame image-to-video for every I2V clip, from the chosen keyframes in specs/frames/ep01v44/.
    python3 make_ep01v44_clips_input.py <name> [--backend ltx98d] [--orient portrait,landscape] [--steps N] [C01 C02 ...]   -> inputs/<name>
Keyframes: <id>.png (start) and <id>_end.png (end), each with its <id>_land twin. Clip length = script duration + 0.5 s (max 5.5 s), 1 variant."""
import argparse, json, os, re, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "paper"))
from parse_ep01v44 import parse
FRAMES = os.path.join(HERE, "..", "specs", "frames", "ep01v44")
STYLE = "soft watercolor anime, delicate gentle line art, warm muted palette, consistent character design, expressive anime-comedy faces, smooth fluid animation"
NEG = ("realistic, photorealistic, 3D render, photo, style change, deformed hands, extra limbs, extra fingers, extra people, text, watermark, subtitles, logo, "
       "blurry, low quality, distorted face, changing clothes, morphing, flickering, scene cut, camera shake, static image, frozen")


def words(t, n=110):
    w = t.split()
    return " ".join(w[:n])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name"); ap.add_argument("ids", nargs="*")
    ap.add_argument("--backend", default="ltx98d"); ap.add_argument("--orient", default="portrait,landscape")
    ap.add_argument("--steps", type=int); ap.add_argument("--motion", default="medium")
    a = ap.parse_args()
    out = os.path.join(HERE, "inputs", a.name)
    os.makedirs(os.path.join(out, "images"), exist_ok=True)
    clips, seed = [], 8000
    for c in parse():
        if c["method"] == "CODE" or (a.ids and c["id"] not in a.ids):
            continue
        seed += 3
        item = {"id": c["id"], "prompt": words(c["action"]), "seconds": min(5.5, c["dur"] + 0.5), "seed": seed, "variants": 1, "motion": a.motion, "start": {}, "end": {}}
        if a.steps:
            item["steps"] = a.steps
        for o, suf in (("portrait", ""), ("landscape", "_land")):
            if o not in a.orient:
                continue
            for key, base in (("start", c["id"]), ("end", c["id"] + "_end")):
                p = os.path.join(FRAMES, base + suf + ".png")
                if not os.path.exists(p):
                    if o == "landscape":
                        continue
                    sys.exit(f"missing keyframe {p}")
                Image.open(p).convert("RGB").save(os.path.join(out, "images", base + suf + ".jpg"), quality=92)
                item[key][o] = f"images/{base}{suf}.jpg"
        clips.append(item)
    job = {"defaults": {"backend": a.backend, "width": 480, "height": 832, "fps": 24, "fit": "cover", "upscale": [720, 1280],
                        "orientations": a.orient.split(","), "style": STYLE, "negative": NEG}, "clips": clips}
    json.dump(job, open(os.path.join(out, "clips.json"), "w"), indent=1)
    print(len(clips), "clips ->", out)


if __name__ == "__main__":
    main()
