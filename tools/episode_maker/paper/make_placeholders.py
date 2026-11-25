#!/usr/bin/env python3
"""Temporary start stills for clips whose real Canva still has not arrived yet, made from the stills that exist
(crops/flips) and the Grandma cut-out. Written to specs/frames/ep01v4_placeholder/ ; real stills in specs/frames/ep01v4/
always win automatically (the spec's frames_fallback). Run again any time:  python3 paper/make_placeholders.py
Also writes the horizontal 16:9 twins Cxx_land.png (1920x1080, same recipe, wide crop) for the stills that are still placeholders."""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from paper.core import font, F_BLACK
REAL = os.path.join(ROOT, "specs", "frames", "ep01v4")
OUT = os.path.join(ROOT, "specs", "frames", "ep01v4_placeholder")
W, H = 1080, 1920


def crop916(img, cx, cy, zoom=1.0, flip=False):
    """Crop to the current output aspect (W x H: 9:16 normally, 16:9 while the landscape twins are made) and scale to W x H."""
    ar = W / H
    vw = img.width / zoom; vh = vw / ar
    if vh > img.height / zoom * 1.0001:
        vh = img.height / zoom; vw = vh * ar
    x0 = min(max(cx * img.width - vw / 2, 0), img.width - vw); y0 = min(max(cy * img.height - vh / 2, 0), img.height - vh)
    im = img.crop((int(x0), int(y0), int(x0 + vw), int(y0 + vh))).resize((W, H), Image.LANCZOS)
    return ImageOps.mirror(im) if flip else im


def label(im, name):
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((24, 24, 24 + 470, 24 + 70), 16, fill=(255, 250, 240, 200))
    d.text((44, 36), f"PLACEHOLDER {name}", font=font(F_BLACK, 40), fill=(217, 72, 15, 255))
    return im


def grandma(bg, flip=False):
    bg = bg.filter(ImageFilter.GaussianBlur(10))
    g = Image.open(os.path.join(ROOT, "specs", "puppets", "grandma.png")).convert("RGBA")
    h = int(H * 0.5); w = int(g.width * h / g.height)
    g = g.resize((w, h), Image.LANCZOS)
    if flip: g = ImageOps.mirror(g)
    bg = bg.copy(); bg.paste(g, (int(W * 0.5 - w / 2), int(H * 0.42)), g)
    return bg


# name -> (source still, recipe)
RECIPES = {
    "C09": lambda s: crop916(s["C08"], 0.62, 0.5, 1.15, flip=True),
    "C10": lambda s: crop916(s["C12"], 0.2, 0.22, 2.2),
    "C14": lambda s: crop916(s["C01"], 0.5, 0.5, 1.0, flip=True),
    "C16": lambda s: crop916(s["C15"], 0.75, 0.4, 1.9),
    "C17": lambda s: crop916(s["C15"], 0.7, 0.45, 1.4),
    "C20": lambda s: crop916(s["C12"], 0.45, 0.4, 1.2, flip=True),
    "C26": lambda s: grandma(crop916(s["C11"], 0.5, 0.5, 1.0)),
    "C27": lambda s: grandma(crop916(s["C08"], 0.5, 0.5, 1.0), flip=True),
    "C28": lambda s: crop916(s["C05"], 0.2, 0.62, 1.9),
    "C29": lambda s: crop916(s["C05"], 0.72, 0.4, 1.4),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    src = {}
    for n in ("C01", "C05", "C08", "C11", "C12", "C15"):
        p = os.path.join(REAL, n + ".png")
        if os.path.exists(p):
            src[n] = Image.open(p).convert("RGB")
    global W, H
    made, skipped = [], []
    for name, fn in RECIPES.items():
        out = os.path.join(OUT, name + ".png")
        out_land = os.path.join(OUT, name + "_land.png")
        if os.path.exists(os.path.join(REAL, name + ".png")):
            for f in (out, out_land):
                if os.path.exists(f): os.remove(f)
            skipped.append(name); continue
        try:
            W, H = 1080, 1920
            label(fn(src), name).save(out)
            made.append(name)
            if os.path.exists(os.path.join(REAL, name + "_land.png")):
                if os.path.exists(out_land): os.remove(out_land)       # the real horizontal still wins
            else:
                W, H = 1920, 1080
                label(fn(src), name + " (16:9)").save(out_land)
        except KeyError as e:
            print("missing source still", e)
        finally:
            W, H = 1080, 1920
    print("placeholders made (vertical + horizontal):", made, "| real stills present, placeholder removed:", skipped)


if __name__ == "__main__":
    main()
