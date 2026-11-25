#!/usr/bin/env python3
"""Generates dumpling_clips.ipynb (one notebook for Kaggle AND Colab) from generate_clips.py.
Run after editing generate_clips.py:  python3 build_notebook.py"""
import json, os
import nbformat
from nb_common import GPU_CHECK, FIND_INPUT

HERE = os.path.dirname(os.path.abspath(__file__))
code = open(os.path.join(HERE, "generate_clips.py"), encoding="utf-8").read()
cells = []


def md(s): cells.append(nbformat.v4.new_markdown_cell(s.strip("\n")))
def py(s): cells.append(nbformat.v4.new_code_cell(s.strip("\n")))


md("""
# The Dumpling Boy: batch image-to-video on a free GPU
Works on **Kaggle** (GPU T4 x2 / P100) and **Google Colab** (free T4). Press **Run all** (or follow the cells top to bottom).

1. Turn on the GPU: Kaggle: right panel, *Session options*, *Accelerator* = GPU T4 x2, *Internet* = On. Colab: *Runtime, Change runtime type, T4 GPU*.
2. Provide the inputs (`clips.json` and the `images/` folder, made with `pack_inputs.py`): Kaggle Dataset, Google Drive folder `dumpling_input`, or a zip upload in step 4.
3. Run all. Finished clips are skipped, so you can stop and run again at any time.
4. Download `dumpling_clips.zip` (last cell).

Every clip is made in both formats by default: `<id>.mp4` (vertical 9:16, 480x832) and `<id>_land.mp4` (horizontal 16:9, 832x480);
the start image `images/X.png` is paired with `images/X_land.png` for the landscape clip when it exists. Per clip, `"orientations": ["portrait"]` makes only one.

Step-by-step guide: `tools/episode_maker/gpu/README.md`.
""")
md("## 1. Settings (the only cell you may want to edit)")
py('''
BACKEND = "ltx"        # "ltx" = primary (fast, 2B). "wan" = slower fallback with better motion. "ltx13b" = experimental (Kaggle only)
GPUS = "auto"          # "auto" uses both T4s on Kaggle; "1" forces one
MAX_MINUTES = 540      # stop starting new clips after this many minutes (Kaggle sessions end at 9-12 h)
ONLY = ""              # e.g. "c01,c02" to run only some clips
FORCE = False          # True = regenerate clips that already exist
DTYPE = "auto"         # "auto" | "fp16" | "bf16" | "fp32" (try "bf16" if clips come out black or noisy)
SMOKE_TEST = False     # True = first run ONE clip with 8 steps at low resolution, to check that everything works (~3 min)
''')
md("## 2. Check the GPU (stops here when there is none) and install")
py(GPU_CHECK)
py('''
# diffusers >= 0.35 is needed for the LTX conditioning pipeline and Wan 2.2
!pip install -q -U "diffusers>=0.35" "transformers>=4.51" accelerate sentencepiece protobuf ftfy imageio imageio-ffmpeg pillow numpy
import diffusers, torch, transformers
print("diffusers", diffusers.__version__, "| torch", torch.__version__, "| cuda", torch.cuda.is_available(), "| gpus", torch.cuda.device_count())
''')
md("## 3. The generator script (written to disk; also usable on any other GPU machine)")
py("%%writefile generate_clips.py\n" + code)
md("""
## 4. Find the inputs
Order tried: Kaggle dataset (`/kaggle/input/*/clips.json`), `/content/dumpling_input`, Google Drive `MyDrive/dumpling_input`, otherwise (Colab) an upload prompt for `dumpling_input.zip`.
""")
py('''
''' + FIND_INPUT.replace('{F}', 'clips.json') + '''
INPUT = find_input()
if INPUT is None and ON_COLAB:
    try:                                   # option: Google Drive
        from google.colab import drive
        drive.mount("/content/drive")
        INPUT = find_input()
    except Exception as ex:
        print("Drive not mounted:", ex)
if INPUT is None and ON_COLAB:             # option: upload the zip
    from google.colab import files
    print("Upload dumpling_input.zip (made by pack_inputs.py)")
    up = files.upload()
    for name in up:
        if name.endswith(".zip"):
            zipfile.ZipFile(name).extractall("/content/dumpling_input")
    INPUT = find_input()
assert INPUT, "clips.json not found. Upload the dataset / folder as described in README.md"
print("inputs:", INPUT)
''')
md("## 5. Plan (no GPU time used)")
py('''
extra = (f" --only {ONLY}" if ONLY else "") + (" --force" if FORCE else "")
!python generate_clips.py --input "{INPUT}" --out "{OUT}" --backend {BACKEND} --dry-run {extra}
''')
md("## 6. Smoke test (only runs when SMOKE_TEST = True)")
py('''
if SMOKE_TEST:
    first = __import__("json").load(open(os.path.join(INPUT, "clips.json")))
    first = (first["clips"] if isinstance(first, dict) else first)[0]["id"]
    !python generate_clips.py --input "{INPUT}" --out "{OUT}_smoke" --backend {BACKEND} --only {first} --limit 1 --steps 8 --width 352 --height 608 --seconds 2 --gpus 1 --force
    print("If a clip appeared in", OUT + "_smoke/clips, everything works. Set SMOKE_TEST = False and run all.")
''')
md("## 7. Generate all clips (this is the long step)")
py('''
if not SMOKE_TEST:
    !python -u generate_clips.py --input "{INPUT}" --out "{OUT}" --backend {BACKEND} --gpus {GPUS} --dtype {DTYPE} --max-minutes {MAX_MINUTES} {extra}
''')
md("## 8. Look at the results and download")
py('''
import json
from IPython.display import HTML, display
res = json.load(open(os.path.join(OUT, "results.json"))) if os.path.exists(os.path.join(OUT, "results.json")) else []
for r in res:
    print(f"{r['id']:<32} {r['status']:<8} {r.get('seconds', '')}")
zp = os.path.join(OUT, "dumpling_clips.zip")
print("\\nZIP:", zp, f"{os.path.getsize(zp) / 1e6:.1f} MB" if os.path.exists(zp) else "(not created yet)")
''')
py('''
# Preview the first finished clip right here
import base64, glob
vids = sorted(glob.glob(os.path.join(OUT, "clips", "*.mp4")))
if vids:
    data = base64.b64encode(open(vids[0], "rb").read()).decode()
    display(HTML(f'<p>{os.path.basename(vids[0])}</p><video width="270" controls loop src="data:video/mp4;base64,{data}"></video>'))
''')
py('''
# Colab: download the zip. Kaggle: the zip is in the notebook Output tab (after "Save Version"), or in /kaggle/working.
if ON_COLAB and os.path.exists(zp):
    from google.colab import files
    files.download(zp)
elif ON_KAGGLE:
    print("Kaggle: open the Output tab / file panel on the right and download dumpling_clips.zip")
''')
py('''
# Optional (Colab): keep a copy on Google Drive so the next session can resume from it
# shutil.copytree(os.path.join(OUT, "clips"), "/content/drive/MyDrive/dumpling_out/clips", dirs_exist_ok=True)
''')

nb = nbformat.v4.new_notebook(cells=cells)
nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
               "language_info": {"name": "python"},
               "accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4"},
               "kaggle": {"accelerator": "nvidiaTeslaT4", "isInternetEnabled": True, "language": "python", "sourceType": "notebook", "isGpuEnabled": True}}
nbformat.validate(nb)
nbformat.write(nb, os.path.join(HERE, "dumpling_clips.ipynb"))
print("wrote dumpling_clips.ipynb with", len(cells), "cells")
