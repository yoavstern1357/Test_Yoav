#!/usr/bin/env python3
"""Stills gate (fix-plan.md Fix 1): check keyframe stills BEFORE any video GPU is spent. CPU only, free models.

For every still: count people two ways and compare with the expected number of characters, measure sharpness, look for text.
  faces    YuNet (MIT, opencv_zoo) at several scales (anime faces are found far more reliably when they are ~100 px tall)
  persons  YOLOX-s COCO "person" class (Apache-2.0, opencv_zoo, ONNX via OpenCV dnn): counts bodies, also backs and profiles
  count    the gate's people estimate = max(faces, persons) (faces miss backs and tiny faces; persons merge overlapping bodies)
  text     PP-OCRv3 DB text detector (Apache-2.0, shared with qc_clips.py)
  sharp    Laplacian variance at 480 px width, relative to the median of the folder (SOFT below TH["soft"])
Flags: DUP (count > expected: duplicate / extra character), MISSING (count < expected), FACE_DUP (faces alone > expected),
       DUP_ID? (two faces whose torsos have the same costume colour: a doubled character even when the count is right; WARN),
       SOFT, TEXT, SMALL_FACE (largest face under TH["small_face"] % of the frame height: smear risk in video).
Output: Markdown/JSON report and a contact sheet PNG with the boxes (faces green, persons blue) and the flags drawn in red.

    python3 qc_stills.py --fetch-models                         # once: YuNet + PP-OCR (qc_clips) + YOLOX-s, into assets/qc_models/
    python3 qc_stills.py specs/frames/ep01v44 --script ../../scripts/episode-01-v4.4.md \
        --md out/qc_stills.md --json out/qc_stills.json --sheet out/qc_stills.png
    python3 qc_stills.py stills/ --expect expect.json            # {"C11": 3, "C11_end": {"count": 3, "chars": ["boy", "uncle", "grandma"]}}
Expected counts: --expect JSON (ids without _land apply to both orientations), else --script (START column for <id>, END column
for <id>_end, character names as in qc_clips.py), else --images-json (names in each prompt). Exit code 1 when any still FAILS.
Not available here: OWLv2 / Grounding DINO (open-vocabulary, Apache-2.0) and DINOv2 identity matching need model weights from
huggingface.co, which this container cannot reach; they can run in a Kaggle job (see production/v4/fix-week1-report.md).
"""
import argparse, glob, json, os, re, sys, urllib.request
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qc_clips as QC  # noqa: E402  (shared models dir, text detector, script parsing)

MODEL_DIR = QC.MODEL_DIR
YOLOX_URL = "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/object_detection_yolox/object_detection_yolox_2022nov.onnx"
TH = dict(
    face_score=0.70,     # YuNet confidence (anime faces score lower than real ones; 0.7 keeps false faces rare)
    person_score=0.45,   # YOLOX person confidence
    person_min_h=0.12,   # ignore person boxes shorter than this share of the frame height (background crowd, props)
    soft=0.45,           # sharpness / folder median below this = SOFT
    small_face=8.0,      # largest face height in % of the frame height
    min_face=0.040,      # ignore face boxes shorter than this share of the frame height (lanterns, buttons, background)
)


def fetch_models():
    QC.fetch_models()
    dst = os.path.join(MODEL_DIR, "yolox_s.onnx")
    if os.path.exists(dst) and os.path.getsize(dst) > 1e6:
        print("have", dst); return
    print("fetch", YOLOX_URL)
    urllib.request.urlretrieve(YOLOX_URL, dst)


# ------------------------------------------------------------------ detectors
class Faces:
    def __init__(self, scales=(1.0, 0.5, 0.33, 0.25)):
        p = os.path.join(MODEL_DIR, "yunet.onnx")
        self.ok = os.path.exists(p)
        self.scales = scales
        if self.ok:
            self.det = cv2.FaceDetectorYN.create(p, "", (320, 320), 0.3, 0.3, 50)

    def __call__(self, img):
        out = []
        for sc in self.scales:
            g = img if sc == 1.0 else cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
            self.det.setInputSize((g.shape[1], g.shape[0]))
            _, d = self.det.detect(g)
            for x in ([] if d is None else d):
                if x[14] >= TH["face_score"] and x[3] / sc >= TH["min_face"] * img.shape[0]:
                    out.append((x[:4] / sc, float(x[14])))
        keep = nms(out, 0.3, contain=0.6)
        # a face whose centre lies inside a bigger kept face is a part of it (mouth or eye found at another scale)
        return [(b, s) for b, s in keep if not any(k[2] > b[2] and k[0] < b[0] + b[2] / 2 < k[0] + k[2] and k[1] < b[1] + b[3] / 2 < k[1] + k[3]
                                                      for k, _ in keep)]


class Persons:
    """YOLOX-s (COCO) through OpenCV dnn, person class only. Pre/post-processing as in opencv_zoo's yolox.py."""
    def __init__(self):
        p = os.path.join(MODEL_DIR, "yolox_s.onnx")
        self.ok = os.path.exists(p)
        if self.ok:
            self.net = cv2.dnn.readNet(p)
            self.size = 640
            grids, strides = [], []
            for s in (8, 16, 32):
                n = self.size // s
                yv, xv = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
                grids.append(np.stack((xv, yv), 2).reshape(-1, 2)); strides.append(np.full((n * n, 1), s))
            self.grids, self.strides = np.concatenate(grids), np.concatenate(strides)

    def __call__(self, img):
        h, w = img.shape[:2]
        r = min(self.size / h, self.size / w)
        pad = np.full((self.size, self.size, 3), 114, np.uint8)
        pad[:int(h * r), :int(w * r)] = cv2.resize(img, (int(w * r), int(h * r)), interpolation=cv2.INTER_LINEAR)
        blob = cv2.dnn.blobFromImage(cv2.cvtColor(pad, cv2.COLOR_BGR2RGB))
        self.net.setInput(blob)
        o = self.net.forward()[0]
        xy = (o[:, :2] + self.grids) * self.strides
        wh = np.exp(o[:, 2:4]) * self.strides
        score = o[:, 4] * o[:, 5]                   # objectness x P(person)
        keep = score >= TH["person_score"]
        boxes = np.concatenate([xy - wh / 2, wh], 1)[keep] / r
        sc = score[keep]
        out = [(b, float(s)) for b, s in zip(boxes, sc) if b[3] >= TH["person_min_h"] * h]
        return nms(out, 0.45, contain=0.85)


def nms(items, iou_th, contain=1.0):
    """Greedy NMS on (box[x,y,w,h], score); also drops a box mostly inside a kept one (multi-scale repeats, body parts)."""
    items = sorted(items, key=lambda t: -t[1])
    keep = []
    for b, s in items:
        ok = True
        for k, _ in keep:
            ix = max(0, min(b[0] + b[2], k[0] + k[2]) - max(b[0], k[0]))
            iy = max(0, min(b[1] + b[3], k[1] + k[3]) - max(b[1], k[1]))
            inter = ix * iy
            if inter / (b[2] * b[3] + k[2] * k[3] - inter + 1e-6) > iou_th or inter / (b[2] * b[3] + 1e-6) > contain:
                ok = False; break
        if ok:
            keep.append((b, s))
    return keep


# Costume colours per character (OpenCV HSV, H 0-180): the torso just below each face is classified, two faces with the same
# costume = "DUP_ID?" (a doubled character even when the head count is right). Design-specific: update after the redesign.
COSTUME = {
    "boy": dict(h=(95, 130), s_min=40, v_max=256),       # faded indigo tunic
    "uncle": dict(h=(8, 28), s_min=70, v_max=210),       # earth-brown linen jacket
    "grandma": dict(h=(35, 90), s_min=25, v_max=256),    # sage-green tunic
}


def costume_of(img, b, min_share=0.15):
    x, y, w, h = b[:4]
    H, W = img.shape[:2]
    x0, x1 = int(max(0, x - 0.2 * w)), int(min(W, x + 1.2 * w))
    y0, y1 = int(min(H, y + 1.15 * h)), int(min(H, y + 2.3 * h))
    if y1 - y0 < 4 or x1 - x0 < 4:
        return None
    hsv = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2HSV).reshape(-1, 3).astype(int)
    share = {k: float(((hsv[:, 0] >= c["h"][0]) & (hsv[:, 0] <= c["h"][1]) & (hsv[:, 1] > c["s_min"]) & (hsv[:, 2] < c["v_max"])).mean())
             for k, c in COSTUME.items()}
    k = max(share, key=share.get)
    return k if share[k] > min_share else None


def sharpness(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, (480, int(round(g.shape[0] * 480 / g.shape[1]))), interpolation=cv2.INTER_AREA).astype(np.float32)
    return float(cv2.Laplacian(g, cv2.CV_32F).var())


# ------------------------------------------------------------------ expected counts
def base_id(sid):
    return re.sub(r"(__v\d+)$", "", sid).replace("_land", "")


def script_expect(path):
    """Characters named in the START or END column -> both <id> and <id>_end. The END column often describes only what
    changes, so the union is the expectation for both stills (as in qc_clips.load_script_chars)."""
    out = {}
    for cid, s, e in QC.script_rows(path):     # v4.5+ tables: the Faces column; older tables: START / END cells
        if cid in out:                          # first table wins (later tables, e.g. timing, reuse the clip ids)
            continue
        out[cid] = out[cid + "_end"] = sorted(set(s) | set(e))
    return out


def load_expect(a):
    if a.expect:
        j = json.load(open(a.expect))
        return {k: (v.get("chars") or [None] * int(v["count"])) if isinstance(v, dict) else [None] * int(v) for k, v in j.items()}
    if a.script:
        return script_expect(a.script)
    if a.images_json:
        j = json.load(open(a.images_json))
        return {i["id"]: QC.expected_chars(i.get("prompt", "")) for i in j.get("images", [])}
    return {}


# ------------------------------------------------------------------ main
def analyse(path, faces, persons, text):
    img = cv2.imread(path)
    r = dict(id=os.path.splitext(os.path.basename(path))[0], w=img.shape[1], h=img.shape[0])
    r["sharp"] = round(sharpness(img), 1)
    if faces.ok:
        f = faces(img)
        r["faces"] = len(f); r["face_boxes"] = [[round(float(v)) for v in b] + [round(s, 2)] for b, s in f]
        r["face_h"] = round(float(100.0 * max((b[3] for b, _ in f), default=0) / img.shape[0]), 1)
        r["costumes"] = [costume_of(img, b) for b, _ in f]
    if persons.ok:
        p = persons(img)
        r["persons"] = len(p); r["person_boxes"] = [[round(float(v)) for v in b] + [round(s, 2)] for b, s in p]
    if text.ok:
        r["text"] = text(img)
    return r, img


def flag(r, exp, med_sharp):
    F = []
    n_exp = len(exp) if exp is not None else None
    count = max(r.get("faces", 0), r.get("persons", 0))
    r["count"] = count
    if n_exp is not None:
        r["expect"] = n_exp; r["chars"] = ",".join(c for c in exp if c)
        if count > n_exp:
            F.append("DUP")
        elif r.get("faces", 0) > n_exp:
            F.append("FACE_DUP")
        if count < n_exp:
            F.append("MISSING")
    cs = [c for c in r.get("costumes", []) if c]
    same = sorted({c for c in cs if cs.count(c) > 1})
    if same and "DUP" not in F:
        F.append("DUP_ID?(" + ",".join(same) + ")")
    if med_sharp and r["sharp"] / med_sharp < TH["soft"]:
        F.append("SOFT")
    if r.get("text"):
        F.append("TEXT")
    if r.get("faces") and 0 < r.get("face_h", 0) < TH["small_face"]:
        F.append("SMALL_FACE")
    r["flags"] = F
    r["verdict"] = "FAIL" if {"DUP", "TEXT"} & set(F) else ("WARN" if F else "PASS")   # DUP_ID? = WARN (a human looks)
    return r


def draw_tile(img, r, tw=270):
    s = tw / img.shape[1]
    t = cv2.resize(img, (tw, int(img.shape[0] * s)), interpolation=cv2.INTER_AREA)
    for b in r.get("person_boxes", []):
        x, y, w, h = [int(v * s) for v in b[:4]]
        cv2.rectangle(t, (x, y), (x + w, y + h), (255, 140, 0), 2)
    for b in r.get("face_boxes", []):
        x, y, w, h = [int(v * s) for v in b[:4]]
        cv2.rectangle(t, (x, y), (x + w, y + h), (0, 200, 0), 2)
    bar = np.full((44, tw, 3), 255, np.uint8)
    col = {"FAIL": (0, 0, 220), "WARN": (0, 140, 230), "PASS": (0, 150, 0)}[r["verdict"]]
    cv2.putText(bar, f"{r['id']}  exp {r.get('expect', '?')} f{r.get('faces', '-')} p{r.get('persons', '-')}", (4, 17),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (30, 30, 30), 1, cv2.LINE_AA)
    cv2.putText(bar, " ".join(r["flags"]) or "ok", (4, 37), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 1, cv2.LINE_AA)
    if r["verdict"] == "FAIL":
        cv2.rectangle(t, (0, 0), (t.shape[1] - 1, t.shape[0] - 1), (0, 0, 220), 4)
    return np.vstack([t, bar])


def contact_sheet(tiles, path, cols=8):
    th = max(t.shape[0] for t in tiles)
    tw = max(t.shape[1] for t in tiles)
    rows = []
    for k in range(0, len(tiles), cols):
        row = [cv2.copyMakeBorder(t, 0, th - t.shape[0], 0, tw - t.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255)) for t in tiles[k:k + cols]]
        row += [np.full((th, tw, 3), 255, np.uint8)] * (cols - len(row))
        rows.append(np.hstack([cv2.copyMakeBorder(t, 3, 3, 3, 3, cv2.BORDER_CONSTANT, value=(255, 255, 255)) for t in row]))
    cv2.imwrite(path, np.vstack(rows))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="*", help="still images or folders")
    ap.add_argument("--expect", help="JSON: id -> expected count or {count, chars}")
    ap.add_argument("--script", help="episode script .md (START/END keyframe columns)")
    ap.add_argument("--images-json", help="images.json of the stills job (character names in the prompts)")
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--no-land", action="store_true", help="skip *_land stills")
    ap.add_argument("--md"); ap.add_argument("--json"); ap.add_argument("--sheet", help="contact sheet PNG with boxes and flags")
    ap.add_argument("--sheet-cols", type=int, default=8)
    ap.add_argument("--gt", help="JSON {\"dup\": [still ids with a duplicated/extra person seen by eye]}: prints precision/recall of DUP")
    ap.add_argument("--fetch-models", action="store_true")
    a = ap.parse_args()
    if a.fetch_models:
        fetch_models()
        if not a.inputs:
            return 0
    files = []
    for p in a.inputs:
        files += sorted(f for e in ("png", "jpg", "jpeg", "webp") for f in glob.glob(os.path.join(p, "*." + e))) if os.path.isdir(p) else [p]
    if a.only:
        files = [f for f in files if any(os.path.basename(f).startswith(o) for o in a.only)]
    if a.no_land:
        files = [f for f in files if "_land" not in os.path.basename(f)]
    if not files:
        ap.error("no stills")
    faces, persons, text = Faces(), Persons(), QC.Text()
    for name, d in (("YuNet", faces), ("YOLOX", persons), ("PP-OCR", text)):
        if not d.ok:
            print(f"note: no {name} model (run --fetch-models); that check is skipped", file=sys.stderr)
    expect = load_expect(a)
    rows, imgs = [], []
    for f in files:
        r, img = analyse(f, faces, persons, text)
        rows.append(r); imgs.append(img)
    med = float(np.median([r["sharp"] for r in rows]))
    for r in rows:
        sid = r["id"]
        key = sid if sid in expect else base_id(sid) if base_id(sid) in expect else None
        flag(r, expect.get(key) if key else None, med)
    cols = ["id", "verdict", "expect", "chars", "faces", "persons", "count", "face_h", "sharp", "text", "flags"]
    cols = [c for c in cols if any(c in r for r in rows)]
    cell = lambda r, c: " ".join(r[c]) if isinstance(r.get(c), list) else ("" if r.get(c) is None else str(r.get(c)))
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + ["| " + " | ".join(cell(r, c) for c in cols) + " |" for r in rows]
    n = {k: sum(r["verdict"] == k for r in rows) for k in ("FAIL", "WARN", "PASS")}
    fl = {}
    for r in rows:
        for x in r["flags"]:
            fl[x] = fl.get(x, 0) + 1
    summary = f"{len(rows)} stills: {n['FAIL']} FAIL, {n['WARN']} WARN, {n['PASS']} PASS. Flags: " + ", ".join(f"{k} {v}" for k, v in sorted(fl.items(), key=lambda x: -x[1]))
    if a.gt:
        gt = set(json.load(open(a.gt))["dup"])
        ids = {r["id"] for r in rows}
        gt &= ids
        for label, test in (("DUP (count)", lambda F: "DUP" in F),
                            ("DUP or DUP_ID? (count or costume)", lambda F: any(x == "DUP" or x.startswith("DUP_ID") for x in F))):
            flagged = {r["id"] for r in rows if test(r["flags"])}
            tp = flagged & gt
            summary += (f"\n{label} vs ground truth ({len(gt)} stills with a duplicate/extra person by eye): flagged {len(flagged)}, "
                        f"true {len(tp)}, precision {len(tp) / max(1, len(flagged)):.2f}, recall {len(tp) / max(1, len(gt)):.2f}. "
                        f"Missed: {' '.join(sorted(gt - flagged)) or '-'}. False alarms: {' '.join(sorted(flagged - gt)) or '-'}")
    print("\n".join(lines)); print(summary)
    if a.md:
        open(a.md, "w").write("\n".join(lines) + "\n\n" + summary + "\n")
    if a.json:
        json.dump(dict(thresholds=TH, rows=rows, summary=summary), open(a.json, "w"), indent=1)
    if a.sheet:
        contact_sheet([draw_tile(im, r) for im, r in zip(imgs, rows)], a.sheet, a.sheet_cols)
        print("contact sheet:", a.sheet)
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
