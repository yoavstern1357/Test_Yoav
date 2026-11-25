#!/usr/bin/env python3
"""Generates dumpling_images.ipynb (one notebook for Kaggle AND Colab) from generate_images.py.
Run after editing generate_images.py:  python3 build_images_notebook.py"""
import os
from nb_common import Builder, GPU_CHECK, FIND_INPUT, HERE

code = open(os.path.join(HERE, "generate_images.py"), encoding="utf-8").read()
b = Builder()
md, py = b.md, b.py

md("""
# The Dumpling Boy: reference-guided stills on a free GPU
Makes the start stills for the image-to-video clips with an **open-weight** model (FLUX.2 klein 4B, Apache-2.0, commercial use OK)
that keeps our existing characters consistent by looking at reference images. Works on **Kaggle** (GPU T4 x2) and **Colab** (free T4).

1. Turn on the GPU: Kaggle: right panel, *Session options*, *Accelerator* = GPU T4 x2, *Internet* = On. Colab: *Runtime, Change runtime type, T4 GPU*.
2. Provide the inputs (`images.json` and a `refs/` folder): Kaggle Dataset, Google Drive folder `dumpling_input`, or a zip upload in step 4.
3. Run all. Finished images are skipped, so you can stop and run again at any time.
4. Download the PNGs from the Output tab (folder `dumpling_out/images`, plus `contact_sheet.jpg`).

If the session has no GPU the notebook stops in step 2 with a clear message. Guide: `tools/episode_maker/gpu/README.md`, section "Stills".
""")
md("## 1. Settings (the only cell you may want to edit)")
py('''
BACKEND = "klein"      # "klein" = primary (FLUX.2 klein 4B, about 1-2 min per image). "qwen" = Qwen-Image-Edit-2511 4-bit, slow experimental fallback
GPUS = "auto"          # "auto" uses both T4s on Kaggle; "1" forces one
MAX_MINUTES = 300      # stop starting new images after this many minutes
ONLY = ""              # e.g. "C10,C14" to run only some images
FORCE = False          # True = regenerate images that already exist
DTYPE = "auto"         # "auto" (fp16, falls back to bf16 if the output is black) | "fp16" | "bf16"
SMOKE_TEST = False     # True = make ONE image at low resolution first, to check that everything works
''')
md("## 2. Check the GPU (stops here when there is none)")
py(GPU_CHECK)
md("## 3. Install (official diffusers / transformers only) and the generator script")
py('''
import os
if ON_KAGGLE:
    os.environ["HF_HOME"] = "/tmp/hf_home"        # model cache outside /kaggle/working (keeps the notebook output small)
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
# FLUX.2 klein needs a recent diffusers (Flux2KleinPipeline); bitsandbytes is only used by the qwen fallback
!pip install -q -U "diffusers>=0.43" "transformers>=4.57" "accelerate>=1.0" huggingface_hub safetensors sentencepiece protobuf pillow numpy bitsandbytes
import diffusers, torch, transformers
print("diffusers", diffusers.__version__, "| transformers", transformers.__version__, "| torch", torch.__version__,
      "| cuda", torch.cuda.is_available(), "| gpus", torch.cuda.device_count())
assert torch.cuda.is_available(), "torch cannot see the GPU: restart the session with the accelerator on"
''')
py("%%writefile generate_images.py\n" + code)
md("""
## 4. Find the inputs
Order tried: Kaggle dataset (`/kaggle/input/.../images.json`), `/content/dumpling_input`, Google Drive `MyDrive/dumpling_input`, otherwise (Colab) an upload prompt for a zip.
""")
py(FIND_INPUT.replace("{F}", "images.json") + '''
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
    print("Upload a zip with images.json and refs/")
    up = files.upload()
    for name in up:
        if name.endswith(".zip"):
            zipfile.ZipFile(name).extractall("/content/dumpling_input")
    INPUT = find_input()
assert INPUT, "images.json not found. Upload the dataset / folder as described in README.md"
print("inputs:", INPUT)
''')
md("## 5. Plan (no GPU time used)")
py('''
extra = (f" --only {ONLY}" if ONLY else "") + (" --force" if FORCE else "")
!python generate_images.py --input "{INPUT}" --out "{OUT}" --backend {BACKEND} --dry-run {extra}
''')
md("## 6. Smoke test (only runs when SMOKE_TEST = True)")
py('''
if SMOKE_TEST:
    import json
    items = json.load(open(os.path.join(INPUT, "images.json")))
    items = items["images"] if isinstance(items, dict) else items
    first = next(i["id"] for i in items if not any(str(r if isinstance(r, str) else r.get("path", "")).startswith("@") for r in i.get("refs", [])))
    !python generate_images.py --input "{INPUT}" --out "{OUT}_smoke" --backend {BACKEND} --only {first} --width 512 --height 896 --gpus 1 --force
    print("If an image appeared in", OUT + "_smoke/images, everything works. Set SMOKE_TEST = False and run all.")
''')
md("## 7. Generate all images (this is the long step: first the model download, about 16 GB for klein)")
py('''
if not SMOKE_TEST:
    !python -u generate_images.py --input "{INPUT}" --out "{OUT}" --backend {BACKEND} --gpus {GPUS} --dtype {DTYPE} --max-minutes {MAX_MINUTES} {extra}
''')
md("## 8. Look at the results and download")
py('''
import json
from IPython.display import Image as IPImage, display
rp = os.path.join(OUT, "results.json")
if os.path.exists(rp):
    res = json.load(open(rp))
    print("model commit:", res.get("model_revision"))
    for r in res["results"]:
        print(f"{r['id']:<32} {r['status']:<8} {r.get('seconds', '')}")
cs = os.path.join(OUT, "contact_sheet.jpg")
if os.path.exists(cs):
    display(IPImage(filename=cs))
zp = os.path.join(OUT, "dumpling_images.zip")
print("\\nZIP:", zp, f"{os.path.getsize(zp) / 1e6:.1f} MB" if os.path.exists(zp) else "(not created yet)")
''')
py('''
# Colab: download the zip. Kaggle: the files are in the notebook Output tab (after "Save Version") under dumpling_out/images.
if ON_COLAB and os.path.exists(zp):
    from google.colab import files
    files.download(zp)
elif ON_KAGGLE:
    print("Kaggle: open the Output tab / file panel on the right and download dumpling_out/images (or dumpling_images.zip)")
''')

b.write("dumpling_images.ipynb")
