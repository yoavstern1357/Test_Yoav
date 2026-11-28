#!/usr/bin/env python3
"""Automatic checks for character model-sheet candidates (v5). CPU only; reuses the detectors of qc_stills.py.

    python3 qc_charsheets.py <folder-or-files> [--md out.md] [--json out.json] [--expect-default 1]
File-name prefix decides the character: boy_*, uncle_*, grandma_*; names containing 'lineup' expect 2 faces.
Checks per image:
  people   YuNet faces + YOLOX persons (qc_stills) vs the expected count (1; lineup 2); DUP / MISSING
  text     PP-OCR (labels or letters in the picture = FAIL)
  costume  share of the characteristic colours inside the foreground mask (cream background removed):
           boy: indigo tunic + orange sash + straw hat; uncle: brown jacket + orange sash + white towel + dark trousers;
           grandma: deep jade jacket (NOT pale sage) + cream apron + orange
  hat      Uncle only: HAT? when the top of the head is not bare skin (dark/straw pixels in the top 12% of the figure, or the head
           silhouette is wider than the face box suggests)
Verdict FAIL for DUP, MISSING, TEXT, HAT?; WARN for colour warnings. A human still looks at every image.
"""
import argparse, glob, json, os, sys
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qc_stills as Q  # noqa: E402

BG = np.array([0xF0, 0xFA, 0xFF], np.float32)  # FFFAF0 in BGR


def fg_mask(img):
    d = np.abs(img.astype(np.float32) - BG).max(axis=2)
    m = (d > 38).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return m > 0


def shares(img, m):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    n = max(1, int(m.sum()))
    def sh(c): return round(float((c & m).sum()) / n, 3)
    return dict(
        indigo=sh((h >= 95) & (h <= 130) & (s > 40)),
        orange=sh((h >= 4) & (h <= 16) & (s > 150) & (v > 170)),
        straw=sh((h >= 18) & (h <= 30) & (s > 50) & (s < 150) & (v > 170)),
        brown=sh((h >= 8) & (h <= 24) & (s > 70) & (v >= 90) & (v < 200)),
        dark=sh(v < 80),
        white=sh((s < 30) & (v > 205)),
        jade=sh((h >= 62) & (h <= 95) & (s > 55) & (v < 150)),
        sage=sh((h >= 40) & (h <= 75) & (s > 20) & (s <= 70) & (v >= 140)),
    )


def check_hat(img, m, face_boxes):
    ys, xs = np.where(m)
    if len(ys) == 0:
        return None
    y0, y1 = ys.min(), ys.max()
    top = m.copy(); top[int(y0 + 0.12 * (y1 - y0)):] = False
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    dark = float(((hsv[..., 2] < 80) & top).sum()) / max(1, int(top.sum()))
    tx = np.where(top.any(axis=0))[0]
    top_w = (tx.max() - tx.min()) if len(tx) else 0
    out = dict(top_dark=round(dark, 3), top_w=int(top_w))
    if face_boxes:
        fw = max(b[2] for b in face_boxes)
        out["top_w_over_face"] = round(float(top_w) / fw, 2)
    return out


def expected(name):
    n = name.lower()
    return 2 if "lineup" in n else 1


def char_of(name):
    for c in ("boy", "uncle", "grandma"):
        if name.lower().startswith(c):
            return c
    return None


def run(files, a):
    faces, persons, text = Q.Faces(), Q.Persons(), Q.QC.Text()
    rows = []
    for f in files:
        r, img = Q.analyse(f, faces, persons, text)
        name = r["id"]; c = char_of(name)
        m = fg_mask(img)
        r["char"] = c; r["fg_share"] = round(float(m.mean()), 2)
        r["colors"] = shares(img, m)
        F = []
        exp = expected(name)
        r["count"] = max(r.get("faces", 0), r.get("persons", 0)); r["expect"] = exp
        if r["count"] > exp:
            F.append("DUP")
        if r["count"] < exp:
            F.append("MISSING")
        if r.get("text"):
            F.append("TEXT")
        col = r["colors"]
        if c == "uncle":
            h = check_hat(img, m, [b for b in r.get("face_boxes", [])])
            r["head"] = h
            if h and (h["top_dark"] > 0.30 or h.get("top_w_over_face", 0) > 1.9):
                F.append("HAT?")
            if col["brown"] < 0.10: F.append("no_brown_jacket")
            if col["orange"] < 0.01: F.append("no_orange_sash")
        elif c == "boy":
            if col["indigo"] < 0.06: F.append("no_indigo_tunic")
            if col["orange"] < 0.005: F.append("no_orange")
            if col["straw"] < 0.04: F.append("no_straw_hat")
        elif c == "grandma":
            if col["jade"] < 0.06: F.append("no_jade_jacket")
            if col["sage"] > 0.15: F.append("SAGE?")
        r["flags"] = F
        r["verdict"] = "FAIL" if {"DUP", "MISSING", "TEXT", "HAT?"} & set(F) else ("WARN" if F else "PASS")
        rows.append(r)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--md"); ap.add_argument("--json")
    a = ap.parse_args()
    files = []
    for p in a.inputs:
        files += sorted(f for e in ("png", "jpg") for f in glob.glob(os.path.join(p, "*." + e))) if os.path.isdir(p) else [p]
    rows = run(files, a)
    lines = ["| id | verdict | faces | persons | exp | face_h% | flags | key colour shares |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        c = r["colors"]
        keys = {"boy": ("indigo", "orange", "straw"), "uncle": ("brown", "orange", "white", "dark"), "grandma": ("jade", "sage", "white", "orange")}.get(r["char"], ("brown",))
        lines.append(f"| {r['id']} | {r['verdict']} | {r.get('faces')} | {r.get('persons')} | {r['expect']} | {r.get('face_h')} | "
                     f"{','.join(r['flags'])} | " + " ".join(f"{k}={c[k]}" for k in keys) + " |")
    out = "\n".join(lines)
    print(out)
    if a.md:
        open(a.md, "w").write(out + "\n")
    if a.json:
        json.dump(rows, open(a.json, "w"), indent=1)
    return 1 if any(r["verdict"] == "FAIL" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
