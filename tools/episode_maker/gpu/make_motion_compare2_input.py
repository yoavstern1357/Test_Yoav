#!/usr/bin/env python3
"""Round 2 of the motion comparison (inputs/motion-compare-002): only LTX 0.9.8 13B distilled (nf4), tuning the settings:
fixed-camera prompt, motion levels, end keyframe before the clip end, 12 fps + RIFE, Real-ESRGAN, 4-step schedule, 576x1024."""
import json, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
src, out = [os.path.join(HERE, "inputs", n) for n in ("motion-compare-001", "motion-compare-002")]
os.makedirs(out, exist_ok=True)
shutil.copytree(os.path.join(src, "images"), os.path.join(out, "images"), dirs_exist_ok=True)
d = json.load(open(os.path.join(src, "clips.json")))
byid = {c["id"]: c for c in d["clips"]}
FIX = " The camera stays completely still, fixed framing, no zoom."
clips = []


def add(id, base, **kw):
    c = dict(byid[base]); c.update(id=id, backend="ltx98d"); c.pop("steps", None); c.pop("guidance", None); c.pop("post", None); c.pop("gen_fps", None); c.pop("motion", None)
    c.update(kw); clips.append(c)


def fix(base):
    return byid[base]["prompt"] + FIX


add("uncle_fixcam_med", "uncle_ltx098d", prompt=fix("uncle_ltx098d"), motion="medium")
add("uncle_fixcam_high", "uncle_ltx098d", prompt=fix("uncle_ltx098d"), motion="high")
add("chase_fixcam_med", "chase_ltx098d", prompt=fix("chase_ltx098d"), motion="medium")
add("gag_kf_end28", "gag_ltx098d_kf", motion="high", keyframes=[{"image": "images/gag_a.jpg", "t": 0}, {"image": "images/gag_b.jpg", "t": 2.8}],
    prompt=byid["gag_ltx098d_kf"]["prompt"] + " After the jump he keeps cheering and wiggling in the air, ears still puffing steam." + FIX)
add("uncle_12fps_rife", "uncle_ltx098d", prompt=fix("uncle_ltx098d"), motion="medium", gen_fps=12, post={"rife": 2})
add("chase_12fps_esrgan_rife", "chase_ltx098d", prompt=fix("chase_ltx098d"), motion="medium", gen_fps=12, post={"esrgan": True, "rife": 2}, upscale=[720, 1280])
add("uncle_4step", "uncle_ltx098d", prompt=fix("uncle_ltx098d"), motion="medium", timesteps=[1000, 975, 725, 0.03], steps=4)
add("chase_576", "chase_ltx098d", prompt=fix("chase_ltx098d"), motion="medium", width=576, height=1024)
data = {"defaults": dict(d["defaults"], upscale=None), "clips": clips}
json.dump(data, open(os.path.join(out, "clips.json"), "w"), indent=1)
print(len(clips), "clips ->", out)
