#!/usr/bin/env python3
"""Contact sheets for the v5 character approval set (CPU, PIL). Labels are drawn here, never generated.

    python3 make_charsheets_v5_contact.py concept  <results_dir_s1> <out_dir>      # all Stage 1 candidates per character
    python3 make_charsheets_v5_contact.py sheets   <spec.json> <out_dir>           # final per-character + combined overview
spec.json: {"boy": {"hero": path, "turn": [4 paths], "expr": [(label, path)...], "poses": [paths]}, "uncle": {...}, "grandma": {...},
            "lineups": [paths]}
Each PNG is kept under 5 MB (JPEG-quality PNG fallback: saved as PNG, shrunk until it fits).
"""
import json, os, sys, glob
from PIL import Image, ImageDraw, ImageFont

FONT = None
for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"):
    if os.path.exists(p):
        FONT = p; break
BG = (255, 250, 240)
INK = (59, 42, 26)


def font(sz):
    return ImageFont.truetype(FONT, sz) if FONT else ImageFont.load_default()


def fit(img, w, h):
    img = img.convert("RGB"); s = min(w / img.width, h / img.height)
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)


def grid(items, cols, cw, ch, title=None, pad=10, label_h=26):
    """items: [(label, path-or-Image)] -> one RGB image"""
    rows = (len(items) + cols - 1) // cols
    th = 56 if title else 0
    W, H = cols * (cw + pad) + pad, th + rows * (ch + label_h + pad) + pad
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    if title:
        d.text((pad, 10), title, fill=INK, font=font(32))
    for k, (lab, src) in enumerate(items):
        r, c = divmod(k, cols)
        x, y = pad + c * (cw + pad), th + pad + r * (ch + label_h + pad)
        if src is None:
            continue
        t = fit(Image.open(src) if isinstance(src, str) else src, cw, ch)
        im.paste(t, (x + (cw - t.width) // 2, y + label_h + (ch - t.height) // 2))
        d.text((x + 2, y + 2), lab, fill=INK, font=font(16))
    return im


def save_under(im, path, mb=5.0):
    while True:
        im.save(path, optimize=True)
        if os.path.getsize(path) < mb * 1e6 * 0.95:
            return
        im = im.resize((int(im.width * 0.85), int(im.height * 0.85)), Image.LANCZOS)


def concept(res, out):
    os.makedirs(out, exist_ok=True)
    allims = []
    for c in ("boy", "uncle", "grandma"):
        fs = sorted(glob.glob(os.path.join(res, f"{c}_full__v*.png"))) + sorted(glob.glob(os.path.join(res, f"{c}_bust__v*.png")))
        items = [(os.path.basename(f)[:-4], f) for f in fs]
        im = grid(items, 4 if c == "uncle" else 3, 300, 520 if True else 400, title=f"Stage 1 concept: {c}")
        save_under(im, os.path.join(out, f"concept_{c}.png"))
        allims.append(im)


def sheets(spec, out):
    S = json.load(open(spec)); os.makedirs(out, exist_ok=True)
    per = {}
    for c in ("boy", "uncle", "grandma"):
        s = S[c]; blocks = []
        hero = Image.open(s["hero"]).convert("RGB")
        top = grid([("hero", s["hero"])] + [(f"turn {i + 1}", p) for i, p in enumerate(s.get("turn", []))] +
                   [(f"pose {i + 1}", p) for i, p in enumerate(s.get("poses", []))], 7, 250, 440, title=f"{c.upper()}: hero, turnaround, poses")
        ex = grid(s.get("expr", []), 6, 250, 250, title=f"{c.upper()}: 12 expressions")
        W = max(top.width, ex.width)
        im = Image.new("RGB", (W, top.height + ex.height), BG); im.paste(top, (0, 0)); im.paste(ex, (0, top.height))
        save_under(im, os.path.join(out, f"sheet_{c}.png")); per[c] = im
    lu = S.get("lineups", [])
    if lu:
        im = grid([(f"lineup {i + 1}", p) for i, p in enumerate(lu)], len(lu), 700, 700, title="Scale lineups")
        save_under(im, os.path.join(out, "sheet_lineups.png")); per["lineups"] = im
    # combined: heroes + 3 expressions each + lineups
    items = []
    for c in ("boy", "uncle", "grandma"):
        items.append((c + " hero", S[c]["hero"]))
    for c in ("boy", "uncle", "grandma"):
        items.append((c + " front", S[c]["turn"][0] if S[c].get("turn") else None))
    for c in ("boy", "uncle", "grandma"):
        ex = S[c].get("expr", [])
        items.append((c + " " + (ex[1][0] if len(ex) > 1 else ""), ex[1][1] if len(ex) > 1 else None))
    comb = grid(items, 3, 420, 640, title="THE DUMPLING BOY: character approval set (v5)")
    if lu:
        lb = grid([(f"lineup {i + 1}", p) for i, p in enumerate(lu)], len(lu), 640, 480)
        c2 = Image.new("RGB", (max(comb.width, lb.width), comb.height + lb.height), BG); c2.paste(comb, (0, 0)); c2.paste(lb, (0, comb.height)); comb = c2
    save_under(comb, os.path.join(out, "sheet_combined.png"))


if __name__ == "__main__":
    if sys.argv[1] == "concept":
        concept(sys.argv[2], sys.argv[3])
    else:
        sheets(sys.argv[2], sys.argv[3])
