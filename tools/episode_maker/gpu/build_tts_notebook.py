#!/usr/bin/env python3
"""Generates dumpling_tts.ipynb (Kaggle AND Colab) from generate_tts.py.
Run after editing generate_tts.py:  python3 build_tts_notebook.py"""
import os
from nb_common import Builder, GPU_CHECK, FIND_INPUT, HERE

code = open(os.path.join(HERE, "generate_tts.py"), encoding="utf-8").read()
b = Builder()
md, py = b.md, b.py

md("""
# The Dumpling Boy: expressive voices on a free GPU
Renders every spoken line of an episode with an **open-weight, commercially licensed** text-to-speech model
(Chatterbox, Qwen3-TTS, Orpheus ...). Voices are synthetic: a reference clip we generated ourselves, or the model's built-in voices.
Works on **Kaggle** (GPU T4) and **Colab** (free T4).

1. Turn on the GPU and Internet (Kaggle: right panel, *Session options*; Colab: *Runtime, Change runtime type, T4 GPU*).
2. Provide the input folder (`tts.json` and `refs/`) as a Kaggle Dataset, a Drive folder `dumpling_input`, or a zip upload in step 4.
3. Run all. Finished lines are skipped, so you can run again at any time.
4. Download `dumpling_out/audio/*.wav` (or `dumpling_tts.zip`) and put the WAVs into `tools/episode_maker/tts/gpu/`.

Guide: `tools/episode_maker/gpu/README.md`, section "Voices"; choice and licenses: `production/v4/voice-tech.md`.
""")
md("## 1. Settings (the only cell you may want to edit)")
py('''
BACKEND = "chatterbox"  # one engine or several, comma separated and run one after the other: chatterbox | turbo | orpheus | qwen3 | qwen3custom | mock
MAX_MINUTES = 120       # stop starting new lines after this many minutes (per engine)
ONLY = ""               # e.g. "01,02" to run only some line ids
FORCE = False           # True = render lines again
SMOKE_TEST = False      # True = render only the first 2 lines first, to check that everything works
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
py("%%writefile generate_tts.py\n" + code)
md("## 4. Find the inputs")
py(FIND_INPUT.replace("{F}", "tts.json") + '''
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
    print("Upload a zip with tts.json and refs/")
    up = files.upload()
    for name in up:
        if name.endswith(".zip"):
            zipfile.ZipFile(name).extractall("/content/dumpling_input")
    INPUT = find_input()
assert INPUT, "tts.json not found. Upload the dataset / folder as described in README.md"
print("inputs:", INPUT)
''')
md("## 5. Install (keeps the preinstalled torch) and render, one engine after the other")
py('''
import json
def stream(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in p.stdout:
        print(line.rstrip(), flush=True)
    return p.wait()

extra = (["--only", ONLY] if ONLY else []) + (["--force"] if FORCE else [])
if SMOKE_TEST and not ONLY:
    extra += ["--only", ",".join(str(l["id"]) for l in json.load(open(os.path.join(INPUT, "tts.json")))["lines"][:2])]
SUMMARY = {}
for be in [b.strip() for b in BACKEND.split(",") if b.strip()]:
    print("\\n" + "=" * 20, be, "=" * 20, flush=True)
    out = os.path.join(OUT, be)
    rc = stream([sys.executable, "-u", "generate_tts.py", "--backend", be, "--install"]) if be != "mock" else 0
    rc = stream([sys.executable, "-u", "generate_tts.py", "--input", INPUT, "--out", out, "--backend", be, "--max-minutes", str(MAX_MINUTES)] + extra)
    SUMMARY[be] = "ok" if rc == 0 else f"exit {rc}"
print("\\nSUMMARY", SUMMARY)
''')
md("## 6. Listen and download")
py('''
from IPython.display import Audio, display
for be in SUMMARY:
    rp = os.path.join(OUT, be, "results.json")
    if os.path.exists(rp):
        res = json.load(open(rp))
        print("backend:", res["backend"], "| license:", res["license"], "| model:", res.get("model"), res.get("model_revision"))
        for r in res["results"][:12]:
            print(f"{r['id']:<28} {r['status']:<6} {r.get('audio_seconds', '')}s {r.get('flags', '')} {r.get('error', '')[:200]}")
            if r["status"] == "ok":
                display(Audio(os.path.join(OUT, be, "audio", r["id"] + ".wav")))
    else:
        print(be, "produced no results.json")
''')
b.write("dumpling_tts.ipynb")
