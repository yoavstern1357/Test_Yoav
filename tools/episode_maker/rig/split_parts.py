#!/usr/bin/env python3
"""Split the flat cut-out characters into rig parts (head, arms, torso, legs).

Pure image processing (numpy + OpenCV): polygon masks are hand-placed in the
coordinates of specs/puppets/<name>.png.  Output: specs/rigs/<name>/<part>.png
(cropped RGBA) + parts.json (crop offset, pivot, parent, z) used by rigdemo.py.

This is a stop-gap: the polygons cut through shading and the hidden areas
behind arms/legs are only inpainted.  A proper rig needs art drawn in layers
(see production/v4/video-tech.md).
"""
import json, os, sys
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS = os.path.join(HERE, "..", "specs")
OUT = os.path.join(SPECS, "rigs")


def poly_mask(shape, pts, feather=0):
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255)
    if feather:
        m = cv2.GaussianBlur(m, (0, 0), feather)
    return m


def ellipse_mask(shape, c, r):
    m = np.zeros(shape[:2], np.uint8)
    cv2.ellipse(m, (int(c[0]), int(c[1])), (int(r[0]), int(r[1])), 0, 0, 360, 255, -1)
    return m


def hem_mask(shape, hem, above=True, off=0):
    """mask of pixels above (or below) the polyline hem (list of (x,y))."""
    h, w = shape[:2]
    xs = np.arange(w)
    hy = np.interp(xs, [p[0] for p in hem], [p[1] for p in hem]) + off
    yy = np.arange(h)[:, None]
    return ((yy <= hy[None, :]) if above else (yy > hy[None, :])).astype(np.uint8) * 255


def crop(img, mask):
    a = (img[..., 3].astype(np.float32) * mask.astype(np.float32) / 255).astype(np.uint8)
    out = img.copy()
    out[..., 3] = a
    ys, xs = np.where(a > 0)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    return out[y0:y1, x0:x1], (int(x0), int(y0))


def save_part(d, name, img, mask, meta, parts):
    c, (x0, y0) = crop(img, mask)
    cv2.imwrite(os.path.join(d, name + ".png"), cv2.cvtColor(c, cv2.COLOR_RGBA2BGRA))
    meta = dict(meta)
    meta["off"] = [x0, y0]
    parts[name] = meta


def outline_poly(img, pts, color=(58, 38, 22), w=5):
    cv2.polylines(img, [np.array(pts, np.int32)], False, color + (255,), w, cv2.LINE_AA)


def uncle():
    src = cv2.cvtColor(cv2.imread(os.path.join(SPECS, "puppets", "uncle.png"), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
    H, W = src.shape[:2]
    shape = src.shape
    d = os.path.join(OUT, "uncle"); os.makedirs(d, exist_ok=True)
    parts = {}
    cream = (251, 238, 222)

    head_m = ellipse_mask(shape, (450, 172), (206, 168))
    armL = [(300, 285), (230, 305), (150, 340), (80, 400), (30, 480), (5, 560), (0, 620), (20, 700), (75, 755), (115, 768), (150, 765),
            (185, 745), (195, 700), (200, 600), (215, 500), (240, 400), (275, 330)]
    armR = [(595, 283), (680, 298), (770, 345), (845, 430), (885, 540), (898, 640), (895, 735), (850, 770), (835, 840), (790, 892),
            (745, 892), (725, 830), (722, 765), (718, 700), (710, 600), (690, 480), (655, 380), (615, 330)]
    armL_m = poly_mask(shape, armL); armR_m = poly_mask(shape, armR)
    hem = [(100, 1030), (200, 1052), (300, 1075), (400, 1090), (500, 1090), (600, 1085), (700, 1068), (800, 1030)]
    below = hem_mask(shape, hem, above=False, off=6)
    legL_m = hem_mask(shape, hem, above=False, off=-34) & poly_mask(shape, [(178, 0), (452, 0), (452, H), (178, H)])
    legR_m = hem_mask(shape, hem, above=False, off=-34) & poly_mask(shape, [(452, 0), (716, 0), (716, H), (452, H)])

    # base / torso: remove head (top part), arms, legs
    base = src.copy()
    base_a = base[..., 3].astype(np.float32)
    kill = np.zeros((H, W), np.uint8)
    kill |= head_m & (np.arange(H)[:, None] < 275).astype(np.uint8) * 255
    kill |= below
    base_a[kill > 0] = 0
    # arms removed: fill with kimono colour and stroke the body edge
    for am in (armL_m, armR_m):
        dil = cv2.dilate(am, np.ones((3, 3), np.uint8))
        base_a[dil > 0] = 0
    base[..., 3] = base_a.astype(np.uint8)
    # body edge strokes
    outline_poly(base, [(215, 520), (203, 600), (196, 700), (186, 745)], w=6)
    outline_poly(base, [(700, 480), (712, 600), (722, 700), (725, 760)], w=6)
    save_part(d, "torso", base, (base[..., 3] > 0).astype(np.uint8) * 255, dict(pivot=[450, 1000], parent="root", z=20), parts)

    # arms
    for nm, am, piv in (("armL", armL_m, [262, 335]), ("armR", armR_m, [640, 315])):
        a = src.copy()
        save_part(d, nm, a, cv2.GaussianBlur(am, (0, 0), 0.8), dict(pivot=piv, parent="torso", z=30), parts)

    # head
    save_part(d, "head", src, cv2.GaussianBlur(head_m, (0, 0), 0.8), dict(pivot=[450, 305], parent="torso", z=40), parts)

    # legs
    for nm, lm, piv in (("legL", legL_m, [310, 1068]), ("legR", legR_m, [600, 1068])):
        save_part(d, nm, src, lm, dict(pivot=piv, parent="root", z=10), parts)

    parts["_meta"] = dict(size=[W, H], feet=[450, 1335], hip=[450, 1070], skin=[254, 186, 132])
    json.dump(parts, open(os.path.join(d, "parts.json"), "w"), indent=1)
    return parts


def boy():
    src = cv2.cvtColor(cv2.imread(os.path.join(SPECS, "puppets", "boy.png"), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
    H, W = src.shape[:2]
    shape = src.shape
    d = os.path.join(OUT, "boy"); os.makedirs(d, exist_ok=True)
    parts = {}
    cream = (252, 240, 226)
    head_m = poly_mask(shape, [(0, 0), (W, 0), (W, 270), (520, 330), (420, 372), (330, 392), (230, 392), (140, 372), (40, 330), (0, 270)])
    # keep everything above y=392 inside head only where hat/face (alpha handles the rest)
    head_m = (np.arange(H)[:, None] < 392).astype(np.uint8)[:, :].repeat(W, 1) * 255
    armL = [(165, 440), (115, 490), (70, 560), (15, 685), (25, 705), (75, 740), (70, 800), (75, 865), (95, 893), (110, 880),
            (105, 820), (112, 770), (150, 720), (165, 640), (172, 520)]
    armR = [(385, 450), (420, 440), (455, 490), (500, 590), (548, 700), (500, 740), (480, 745), (480, 800), (478, 870),
            (450, 893), (425, 893), (420, 850), (428, 780), (420, 740), (405, 700), (395, 600), (390, 500)]
    armL_m = poly_mask(shape, armL); armR_m = poly_mask(shape, armR)
    hem = [(100, 898), (140, 900), (283, 910), (430, 895), (480, 890)]
    below = hem_mask(shape, hem, above=False, off=6)
    legL_m = hem_mask(shape, hem, above=False, off=-30) & poly_mask(shape, [(120, 0), (283, 0), (283, H), (120, H)])
    legR_m = hem_mask(shape, hem, above=False, off=-30) & poly_mask(shape, [(283, 0), (450, 0), (450, H), (283, H)])

    base = src.copy()
    a = base[..., 3].astype(np.float32)
    a[(head_m > 0)] = 0
    a[below > 0] = 0
    # neck piece under the hat so a bobbing head never shows a hole
    neck = np.zeros((H, W), np.uint8); cv2.rectangle(neck, (228, 352), (336, 396), 255, -1)
    base[neck > 0, :3] = (246, 200, 165); a[neck > 0] = 255
    for am in (armL_m, armR_m):
        a[cv2.dilate(am, np.ones((3, 3), np.uint8)) > 0] = 0
    base[..., 3] = a.astype(np.uint8)
    save_part(d, "torso", base, (base[..., 3] > 0).astype(np.uint8) * 255, dict(pivot=[283, 860], parent="root", z=20), parts)
    for nm, am, piv in (("armL", armL_m, [170, 455]), ("armR", armR_m, [385, 455])):
        save_part(d, nm, src, cv2.GaussianBlur(am, (0, 0), 0.8), dict(pivot=piv, parent="torso", z=30), parts)
    save_part(d, "head", src, cv2.GaussianBlur(head_m, (0, 0), 0.8), dict(pivot=[280, 385], parent="torso", z=40), parts)
    for nm, lm, piv in (("legL", legL_m, [205, 905]), ("legR", legR_m, [360, 905])):
        save_part(d, nm, src, lm, dict(pivot=piv, parent="root", z=10), parts)
    parts["_meta"] = dict(size=[W, H], feet=[283, 1335], hip=[283, 905], skin=[250, 205, 170])
    json.dump(parts, open(os.path.join(d, "parts.json"), "w"), indent=1)
    return parts


if __name__ == "__main__":
    for n, f in (("uncle", uncle), ("boy", boy)):
        p = f()
        print(n, {k: v.get("off") for k, v in p.items() if k != "_meta"})
