#!/usr/bin/env python3
"""Builds inputs/motion-compare-001: 3 representative shots (+1 keyframe shot) x backends, portrait only, 1 variant.
Stills: intro-v3 variant 2 (the locked Uncle) from branch gpu-results (git fetch origin gpu-results) + ep01 stills in this repo."""
import json, os, subprocess, io
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "motion-compare-001")
os.makedirs(os.path.join(OUT, "images"), exist_ok=True)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def from_results(path):
    return Image.open(io.BytesIO(subprocess.check_output(["git", "-C", REPO, "show", "origin/gpu-results:" + path]))).convert("RGB")


srcs = {
    "uncle": from_results("intro-v3/dumpling_out/images/I1_bite__v2.png"),
    "chase": from_results("intro-v3/dumpling_out/images/I5_chase__v2.png"),
    "macro": Image.open(os.path.join(HERE, "inputs/ep01v43-clips-A/images/C01.jpg")).convert("RGB"),
    "gag_a": Image.open(os.path.join(HERE, "inputs/ep01v43-clips-B/images/C14.jpg")).convert("RGB"),
    "gag_b": Image.open(os.path.join(HERE, "inputs/ep01v43-clips-B/images/C14_end.jpg")).convert("RGB"),
}
for k, im in srcs.items():
    im.save(os.path.join(OUT, "images", k + ".jpg"), quality=92)

STYLE = "soft watercolor anime, delicate gentle line art, warm muted palette, consistent character design, smooth natural animation"
NEG = ("realistic, photorealistic, 3D render, photo, style change, deformed hands, extra limbs, extra fingers, extra people, text, watermark, subtitles, logo, "
       "blurry, low quality, distorted face, changing clothes, morphing, flickering, scene cut, camera shake")
SHOTS = {
    "uncle": ("images/uncle.jpg", "Close-up. The big fat bald uncle with the thin mustache chews with his eyes closed in bliss, then his eyes pop wide open, his eyebrows "
              "shoot up, his cheeks puff out and he waves his chopsticks in shock, then a huge delighted grin. The small boy in the conical leaf hat giggles and looks up at him. "
              "Steam swirls. Expressive faces, big body movement."),
    "chase": ("images/chase.jpg", "The small boy and the big fat uncle run in panic toward the camera, arms flailing, mouths wide open screaming, eyes wide, sweat drops fly, "
              "the uncle's belly bounces with every step, the giant white dumpling with a huge chomping mouth rolls right behind them snapping its jaws, steam streams, dust kicks up."),
    "macro": ("images/macro.jpg", "Macro. The soup dumpling lifts on the chopsticks, the thin skin sags and wobbles like a water balloon, golden soup ripples inside, steam curls "
              "and drifts, a drop falls back into the basket."),
}
clips = []


def add(id, shot, backend, **kw):
    img, prompt = SHOTS[shot]
    c = dict(id=id, backend=backend, start=img, prompt=prompt, seed=4242); c.update(kw); clips.append(c)


for shot in SHOTS:
    add(f"{shot}_ltx095", shot, "ltx", steps=30)                                   # current pipeline (baseline)
for shot in SHOTS:
    add(f"{shot}_ltx098d", shot, "ltx98d", motion="medium")                        # LTX 0.9.8 13B distilled, nf4, 8 steps
add("uncle_ltx098d_12fps", "uncle", "ltx98d", motion="medium", gen_fps=12, post={"rife": 2})   # half the frames + RIFE
for shot in SHOTS:
    add(f"{shot}_wan5b", shot, "wan", steps=16, guidance=5.0)                      # Wan2.2 TI2V-5B
for shot in SHOTS:
    add(f"{shot}_fastwan", shot, "fastwan", steps=3, guidance=1.0)                 # 3-step distilled Wan2.2 5B (experimental)
# keyframe test: start + end still of the uncle gag
gag = "the big fat bald uncle with the mustache pops the whole dumpling into his mouth, his cheeks puff out, one eye twitches, a sweat drop swells on his bald head, then he rockets up into the air, both ears blasting long jets of white steam, his mustache standing up like antennae."
clips.append(dict(id="gag_ltx095_kf", backend="ltx", prompt=gag, steps=30, cond_noise=0.35, seed=4242,
                  keyframes=[{"image": "images/gag_a.jpg", "t": 0}, {"image": "images/gag_b.jpg", "t": "end"}]))
clips.append(dict(id="gag_ltx098d_kf", backend="ltx98d", prompt=gag, motion="high", seed=4242,
                  keyframes=[{"image": "images/gag_a.jpg", "t": 0}, {"image": "images/gag_b.jpg", "t": "end"}]))
clips.append(dict(id="gag_wan5b_kf", backend="wan", prompt=gag, steps=16, guidance=5.0, seed=4242,
                  keyframes=[{"image": "images/gag_a.jpg", "t": 0}, {"image": "images/gag_b.jpg", "t": "end"}]))
data = {"defaults": {"orientations": ["portrait"], "seconds": 4, "fps": 24, "width": 480, "height": 832, "upscale": None, "style": STYLE, "negative": NEG, "crf": 14},
        "clips": clips}
json.dump(data, open(os.path.join(OUT, "clips.json"), "w"), indent=1)
print(len(clips), "clips ->", OUT)
