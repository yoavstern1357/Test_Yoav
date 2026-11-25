#!/usr/bin/env python3
"""Bundle clips.json + the images it uses into one upload-ready folder and zip (runs on any computer, no GPU).

    python3 pack_inputs.py clips.json                      # -> out/gpu_input/ and out/gpu_input.zip
    python3 pack_inputs.py clips.json --out my_input --max-side 1920

Image paths in clips.json are resolved relative to clips.json (or absolute) and rewritten to images/<name>.
Upload the ZIP (or the folder) as a Kaggle Dataset / to Colab / to Google Drive.  See README.md.
"""
import argparse, hashlib, json, os, shutil, sys, zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips_json")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "gpu_input"))
    ap.add_argument("--max-side", type=int, default=1920, help="shrink bigger images (the models only use ~480x832 anyway)")
    a = ap.parse_args()
    src_dir = os.path.dirname(os.path.abspath(a.clips_json))
    data = json.load(open(a.clips_json, encoding="utf-8"))
    clips = data["clips"] if isinstance(data, dict) else data
    out = os.path.abspath(a.out)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.join(out, "images"))
    names = {}

    def put(rel):
        p = rel if os.path.isabs(rel) else os.path.normpath(os.path.join(src_dir, rel))
        if not os.path.exists(p):
            sys.exit(f"image not found: {p}")
        if p in names:
            return names[p]
        base = os.path.splitext(os.path.basename(p))[0].replace(" ", "_")
        ext = ".png" if Image.open(p).mode in ("RGBA", "LA", "P") else ".jpg"
        name = f"{base}-{hashlib.md5(open(p, 'rb').read()).hexdigest()[:6]}{ext}"
        im = Image.open(p)
        if max(im.size) > a.max_side:
            s = a.max_side / max(im.size)
            im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        im.save(os.path.join(out, "images", name), **({} if ext == ".png" else {"quality": 95}))
        names[p] = "images/" + name
        return names[p]

    for c in clips:
        for k in ("start", "end"):
            if c.get(k):
                c[k] = put(c[k])
    json.dump(data, open(os.path.join(out, "clips.json"), "w", encoding="utf-8"), indent=2)
    zp = out + ".zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(out):
            for f in files:
                fp = os.path.join(root, f)
                z.write(fp, os.path.relpath(fp, out))
    print(f"{len(clips)} clips, {len(names)} images")
    print("folder:", out)
    print("zip   :", zp, f"({os.path.getsize(zp) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
