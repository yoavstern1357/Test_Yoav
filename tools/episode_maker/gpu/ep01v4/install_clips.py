#!/usr/bin/env python3
"""Put the clips from the notebook's dumpling_clips.zip where the episode spec expects them.
    python3 install_clips.py dumpling_clips.zip                 # variant 1 of every clip -> specs/clips/ep01v4/Cxx.mp4
    python3 install_clips.py dumpling_clips.zip --pick C13=2 C08=2   # use variant 2 for these clips
Then re-render:  python3 make_episode.py specs/episode-01-v4.json out/episode-01-v4.mp4 --mobile
(clips that are missing simply keep the animatic fallback)."""
import argparse, os, re, shutil, sys, zipfile, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ap = argparse.ArgumentParser()
ap.add_argument("zip"); ap.add_argument("--pick", nargs="*", default=[])
a = ap.parse_args()
pick = dict(p.split("=") for p in a.pick)
dest = os.path.join(ROOT, "specs", "clips", "ep01v4"); os.makedirs(dest, exist_ok=True)
tmp = tempfile.mkdtemp()
zipfile.ZipFile(a.zip).extractall(tmp)
n = 0
for root, _, files in os.walk(tmp):
    for f in files:
        m = re.match(r"^(C\d+)(?:__v(\d+))?\.mp4$", f)
        if not m:
            continue
        cid, v = m.group(1), m.group(2) or "1"
        if v == pick.get(cid, "1"):
            shutil.copy(os.path.join(root, f), os.path.join(dest, cid + ".mp4")); n += 1
print(n, "clips installed in", dest)
