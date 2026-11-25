#!/usr/bin/env python3
"""Generates dumpling_music.ipynb (Kaggle AND Colab) from generate_music.py.
Run after editing generate_music.py:  python3 build_music_notebook.py"""
import os
from nb_common import Builder, GPU_CHECK, FIND_INPUT, HERE

code = open(os.path.join(HERE, "generate_music.py"), encoding="utf-8").read()
b = Builder()
md, py = b.md, b.py

md("""
# The Dumpling Boy: songs on a free GPU
Generates the series opening song (Japanese punk, sung) with an **open-weight, commercially licensed** music model
(ACE-Step v1 3.5B, Apache-2.0). Works on **Kaggle** (GPU T4) and **Colab** (free T4).

1. Turn on the GPU and Internet.
2. Provide the input folder (`music.json`) as a Kaggle Dataset, a Drive folder `dumpling_input`, or a zip upload in step 4.
3. Run all. Finished tracks are skipped, so you can run again at any time.
4. Download `dumpling_out/audio/*.flac` (or `dumpling_music.zip`).

Guide: `tools/episode_maker/gpu/README.md`, section "Music"; lyrics and style: `production/v4/opening-song.md`.
""")
md("## 1. Settings (the only cell you may want to edit)")
py('''
BACKEND = "acestep"     # acestep | mock
MAX_MINUTES = 150       # stop starting new tracks after this many minutes
ONLY = ""               # e.g. "intro_a,full_b" (track ids or id prefixes)
FORCE = False           # True = render tracks again
SMOKE_TEST = False      # True = render only the first (long) job to check that everything works
''')
md("## 2. Check the GPU (stops here when there is none)")
py(GPU_CHECK)
md("## 3. Write the generator script")
py('''
import os
if ON_KAGGLE:
    os.environ["HF_HOME"] = "/tmp/hf_home"
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
''')
py("%%writefile generate_music.py\n" + code)
md("## 4. Find the inputs")
py(FIND_INPUT.replace("{F}", "music.json") + '''
INPUT = find_input()
if INPUT is None and ON_COLAB:
    try:
        from google.colab import drive
        drive.mount("/content/drive")
        INPUT = find_input()
    except Exception as ex:
        print("Drive not mounted:", ex)
if INPUT is None and ON_COLAB:
    from google.colab import files
    print("Upload a zip with music.json")
    up = files.upload()
    for name in up:
        if name.endswith(".zip"):
            zipfile.ZipFile(name).extractall("/content/dumpling_input")
    INPUT = find_input()
assert INPUT, "music.json not found. Upload the dataset / folder as described in README.md"
print("inputs:", INPUT)
''')
md("## 5. Install (keeps the preinstalled torch) and render")
py('''
import json
def stream(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in p.stdout:
        print(line.rstrip(), flush=True)
    return p.wait()

extra = (["--only", ONLY] if ONLY else []) + (["--force"] if FORCE else []) + (["--limit", "1"] if SMOKE_TEST else [])
SUMMARY = {}
for be in [b.strip() for b in BACKEND.split(",") if b.strip()]:
    print("\\n" + "=" * 20, be, "=" * 20, flush=True)
    out = OUT
    if be != "mock":
        stream([sys.executable, "-u", "generate_music.py", "--backend", be, "--install"])
    rc = stream([sys.executable, "-u", "generate_music.py", "--input", INPUT, "--out", out, "--backend", be, "--max-minutes", str(MAX_MINUTES)] + extra)
    SUMMARY[be] = "ok" if rc == 0 else f"exit {rc}"
print("\\nSUMMARY", SUMMARY)
''')
md("## 6. Listen and download")
py('''
from IPython.display import Audio, display
rp = os.path.join(OUT, "results.json")
if os.path.exists(rp):
    res = json.load(open(rp))
    print("backend:", res["backend"], "| license:", res["license"], "| model:", res.get("model"), res.get("model_revision"))
    for r in res["results"]:
        print(r["id"], r["status"], {k: v for k, v in r.items() if k in ("seconds", "peak", "rms_db", "clipped_pct", "tempo_bpm", "mid_band_ratio", "error")})
        if r["status"] == "ok":
            for e in ("flac", "wav"):
                p = os.path.join(OUT, "audio", r["id"] + "." + e)
                if os.path.exists(p):
                    display(Audio(p)); break
else:
    print("no results.json")
''')
b.write("dumpling_music.ipynb")
