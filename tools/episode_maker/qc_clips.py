#!/usr/bin/env python3
"""Automatic QC gate for AI video clips (CPU only, free tools).

Scans clips (portrait and _land) and prints one row per clip with measurable defect signals:
  stripes   corrupted interpolated frames (horizontal stripe energy, the RIFE bug)
  sharp     frame sharpness (Laplacian variance at a fixed 480 px width) and its worst drop vs frame 1
  faces     face count per sampled frame (YuNet, MIT license, opencv_zoo) -> duplicates appearing / faces lost
  face_h    median face height as % of the frame height (small faces smear first)
  face_sh   worst face-region sharpness vs the first frame (melting faces)
  jump      biggest frame-to-frame change (mid-clip cut, morph, layout change)
  text      frames with text-like boxes (PP-OCRv3 DB detector, Apache-2.0, opencv_zoo) -> garbled AI text
  key       match of frame 1 with the START keyframe and of the last frame with the END keyframe
  timing    (with --spec) how the edit uses the clip: slow-motion stretch, truncated tail, frozen hold

    python3 qc_clips.py specs/clips/ep01v44 --frames specs/frames/ep01v44 \
        --clips-json gpu/inputs/ep01v44-clips-1/clips.json --spec specs/episode-01-v4.4.json --md out/qc.md
    python3 qc_clips.py --fetch-models          # downloads the two small ONNX models into assets/qc_models/
Exit code 1 when any clip FAILS (use it as a gate before rendering; re-roll the failed ids).
Heuristics, not ground truth: a FAIL means "a human must look"; a PASS is not a guarantee. Tune thresholds in TH.
"""
import argparse, glob, json, os, re, subprocess, sys, urllib.request
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(HERE, "assets", "qc_models")
MODELS = {   # small ONNX models (no pickles), loaded with OpenCV dnn
    "yunet.onnx": "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "ppocr_det.onnx": "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/text_detection_ppocr/text_detection_en_ppocrv3_2023may.onnx",
}
TH = dict(
    stripes=2.2,        # row/column gradient ratio of the worst frame (clean anime frames: about 0.8-1.4)
    sharp_drop=0.55,    # worst frame sharpness / first frame sharpness
    face_sharp=0.45,    # worst face sharpness / first-frame face sharpness
    small_face=9.0,     # median face height in % of frame height: below this the face is "small" (smear risk)
    jump=0.45,          # 1 - correlation between consecutive unique frames (64 px thumbnails)
    key_start=0.80,     # correlation of frame 1 with the START keyframe
    key_end=0.70,       # correlation of the last frame with the END keyframe
    key_pair=0.80,      # correlation START vs END keyframe: below this the pair is a different shot (morph / duplicate risk)
    slowmo=0.85,        # edit speed below this = stretched motion (12 fps on twos becomes about 8 fps)
    trunc=0.85,         # share of the clip shown below this = end keyframe / payoff cut off
    freeze=0.30,        # seconds of frozen last frame in the edit
)
CHAR_WORDS = {"boy": r"\b(boy|bo)\b", "uncle": r"\buncle\b", "grandma": r"\bgrandma\b", "dad": r"\bdad('s)? silhouette\b"}


def fetch_models():
    os.makedirs(MODEL_DIR, exist_ok=True)
    for name, url in MODELS.items():
        dst = os.path.join(MODEL_DIR, name)
        if os.path.exists(dst) and os.path.getsize(dst) > 10000:
            print("have", dst); continue
        print("fetch", url)
        urllib.request.urlretrieve(url, dst)
        if os.path.getsize(dst) < 10000:
            os.remove(dst); print("  download failed (got a pointer file?)")


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
                        "-show_entries", "format=duration", "-of", "json", path], capture_output=True, text=True)
    j = json.loads(r.stdout or "{}")
    s = (j.get("streams") or [{}])[0]
    num, den = (s.get("r_frame_rate") or "0/1").split("/")
    return dict(w=s.get("width"), h=s.get("height"), fps=float(num) / float(den or 1), frames=int(s.get("nb_frames") or 0),
                dur=float(j.get("format", {}).get("duration") or 0))


def read_frames(path):
    cap, out = cv2.VideoCapture(path), []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(f)
    return out


def gray480(f):
    h, w = f.shape[:2]
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    return cv2.resize(g, (480, int(round(h * 480 / w))), interpolation=cv2.INTER_AREA).astype(np.float32)


def stripe_score(f):
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32)
    rows = np.abs(np.diff(g, axis=0)).mean()
    cols = np.abs(np.diff(g, axis=1)).mean()
    return float(rows / (cols + 1e-6))


def sharp(g):
    return float(cv2.Laplacian(g, cv2.CV_32F).var())


def thumb(f, n=64):
    g = cv2.cvtColor(cv2.resize(f, (n, n), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32).ravel()
    g -= g.mean()
    return g / (np.linalg.norm(g) + 1e-6)


def corr(a, b):
    return float(np.dot(thumb(a), thumb(b)))


class Faces:
    def __init__(self):
        p = os.path.join(MODEL_DIR, "yunet.onnx")
        self.ok = os.path.exists(p) and hasattr(cv2, "FaceDetectorYN")
        if self.ok:
            self.det = cv2.FaceDetectorYN.create(p, "", (320, 320), 0.55, 0.3, 50)

    def __call__(self, f):
        self.det.setInputSize((f.shape[1], f.shape[0]))
        _, d = self.det.detect(f)
        return [] if d is None else [tuple(int(v) for v in x[:4]) for x in d]


class Text:
    def __init__(self):
        p = os.path.join(MODEL_DIR, "ppocr_det.onnx")
        self.ok = os.path.exists(p) and hasattr(cv2, "dnn") and hasattr(cv2.dnn, "TextDetectionModel_DB")
        if self.ok:
            self.m = cv2.dnn.TextDetectionModel_DB(p)
            self.m.setBinaryThreshold(0.3); self.m.setPolygonThreshold(0.5); self.m.setMaxCandidates(200); self.m.setUnclipRatio(2.0)

    def __call__(self, f):
        h, w = f.shape[:2]
        s = 736 / max(h, w)
        W, H = max(32, int(w * s) // 32 * 32), max(32, int(h * s) // 32 * 32)
        self.m.setInputParams(1.0 / 255.0, (W, H), (122.67891434, 116.66876762, 104.00698793), True)
        boxes, _ = self.m.detect(f)
        n = 0
        for b in boxes:      # keep only line-shaped boxes of readable size (rejects leaves, steam, tiles)
            x, y, bw, bh = cv2.boundingRect(np.array(b, np.int32))
            if bw >= 2.0 * bh and 0.015 * h <= bh <= 0.15 * h and bw >= 0.08 * w:
                n += 1
        return n


def expected_chars(prompt):
    p = (prompt or "").lower()
    return sorted(k for k, rx in CHAR_WORDS.items() if re.search(rx, p))


def load_clip_prompts(path):
    if not path or not os.path.exists(path):
        return {}
    j = json.load(open(path))
    return {c["id"]: c.get("prompt", "") for c in j.get("clips", [])}


def load_script_chars(path):
    """Expected on-screen characters per clip from an episode script table (scripts/episode-XX.md):
    rows '| Cxx (..) | time | method | START KEYFRAME | END KEYFRAME | ...' -> names in START or END."""
    out = {}
    if not path or not os.path.exists(path):
        return out
    for ln in open(path, encoding="utf-8"):
        m = re.match(r"\|\s*(C\d+)\b", ln)
        if not m:
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        names = set(expected_chars(cells[3])) | set(expected_chars(cells[4]))
        out[m.group(1)] = sorted(names)
    return out


def timing_from_spec(spec_path):
    """Use make_episode.build_timeline to see how each clip is used in the edit (needs the voices on disk)."""
    sys.path.insert(0, HERE)
    import make_episode as me
    spec = json.load(open(spec_path))
    me.PITCH_OVERRIDE.update(spec.get("voice_pitch", {})); me.set_cast(spec)
    me.FALLBACK_KOKORO = bool(spec.get("voice_fallback", True)); me.VOICE_SPEED.update(spec.get("voice_speed", {}))
    me.MAX_PAUSE = float(spec.get("max_pause", 0.40))
    shots, _ = me.build_timeline(spec, os.path.dirname(os.path.abspath(spec_path)))
    per = {}
    for s in shots:
        if not s.get("clip_path"):
            continue
        cid = os.path.splitext(os.path.basename(s["clip_path"]))[0]
        cd, _ = me.probe_clip(s["clip_path"])
        tr = s.get("trim")
        a0 = float(tr[0]) if tr else 0.0
        a1 = min(cd, float(tr[1])) if tr and len(tr) > 1 and tr[1] is not None else cd
        sp = float(s.get("speed") or 1.0)
        shown = min(s["dur"] * sp, a1 - a0)
        frozen = max(0.0, s["dur"] - (a1 - a0) / sp)
        d = per.setdefault(cid, dict(shown=0.0, clip=cd, speed=9.9, frozen=0.0, voice=0.0, shots=0))
        d["shown"] += shown; d["speed"] = min(d["speed"], sp); d["frozen"] += frozen; d["shots"] += 1
        d["voice"] += sum(l["dur"] for l in s["lines"])
    return per


def analyse(path, faces, text, frames_dir=None, prompt=None, sample_faces=16, sample_text=5, chars=None):
    cid = os.path.splitext(os.path.basename(path))[0]
    meta = probe(path)
    fr = read_frames(path)
    r = dict(id=cid, w=meta["w"], h=meta["h"], fps=round(meta["fps"], 2), n=len(fr), dur=round(meta["dur"], 2), flags=[])
    if not fr:
        r["flags"].append("UNREADABLE"); return r
    # duplicates (on twos) and unique frames
    uniq, dup = [0], 0
    for i in range(1, len(fr)):
        if np.abs(fr[i].astype(np.int16) - fr[i - 1].astype(np.int16)).mean() < 0.1:   # on-twos copies differ only by encoding noise
            dup += 1
        else:
            uniq.append(i)
    r["twos"] = round(dup / max(1, len(fr) - 1), 2)
    r["eff_fps"] = round(meta["fps"] * len(uniq) / max(1, len(fr)), 1)
    # stripes on every frame
    st = [stripe_score(f) for f in fr]
    r["stripes"] = round(max(st), 2)
    r["striped_frames"] = int(sum(s > TH["stripes"] for s in st))
    U = [fr[i] for i in uniq]
    gs = [gray480(f) for f in U]
    sh = [sharp(g) for g in gs]
    r["sharp"] = round(float(np.median(sh)), 1)
    r["sharp_drop"] = round(min(sh) / (sh[0] + 1e-6), 2)
    # jumps between consecutive unique frames
    j = [1.0 - corr(U[k - 1], U[k]) for k in range(1, len(U))]
    r["jump"] = round(max(j) if j else 0.0, 2)
    r["jump_at"] = round(uniq[int(np.argmax(j)) + 1] / meta["fps"], 2) if j else 0
    # motion: mean change in the last third vs the whole clip (late freeze)
    mv = [float(np.abs(gs[k] - gs[k - 1]).mean()) for k in range(1, len(gs))]
    r["motion"] = round(float(np.mean(mv)) if mv else 0.0, 2)
    # faces
    if faces.ok:
        idx = sorted(set(np.linspace(0, len(U) - 1, min(sample_faces, len(U))).astype(int)))
        counts, heights, fsh = [], [], []
        base = None
        for k in idx:
            f = U[k]
            bx = faces(f)
            counts.append(len(bx))
            H = f.shape[0]
            for (x, y, w, h) in bx:
                heights.append(100.0 * h / H)
            if bx:
                vals = []
                for (x, y, w, h) in bx:
                    crop = f[max(0, y):y + h, max(0, x):x + w]
                    if crop.size:
                        c = cv2.resize(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), (96, 96)).astype(np.float32)
                        vals.append(sharp(c))
                if vals:
                    v = float(np.median(vals))
                    if base is None:
                        base = v
                    fsh.append(v / (base + 1e-6))
        q = max(3, len(counts) // 4)          # robust counts: mode of the first and of the last quarter (detector flicker)
        mode = lambda c: int(np.bincount(c).argmax())
        r["faces_first"], r["faces_last"], r["faces_max"] = mode(counts[:q]), mode(counts[-q:]), max(counts)
        r["faces_mode"] = mode(counts)
        r["face_h"] = round(float(np.median(heights)), 1) if heights else 0.0
        r["face_sharp"] = round(min(fsh), 2) if fsh else None
    # text-like boxes
    if text.ok:
        idx = sorted(set(np.linspace(0, len(U) - 1, min(sample_text, len(U))).astype(int)))
        r["text_frames"] = int(sum(text(U[k]) > 0 for k in idx))
    # keyframe match
    if frames_dir:
        land = cid.endswith("_land")
        base_id = cid[:-5] if land else cid
        sfx = "_land" if land else ""
        ks = os.path.join(frames_dir, f"{base_id}{sfx}.png")
        ke = os.path.join(frames_dir, f"{base_id}_end{sfx}.png")
        if os.path.exists(ks):
            r["key_start"] = round(corr(cv2.imread(ks), fr[0]), 2)
        if os.path.exists(ke):
            r["key_end"] = round(corr(cv2.imread(ke), fr[-1]), 2)
        if os.path.exists(ks) and os.path.exists(ke):   # very different START/END stills make the model morph or duplicate
            r["key_pair"] = round(corr(cv2.imread(ks), cv2.imread(ke)), 2)
        if faces.ok and os.path.exists(ks):              # duplicates are mostly baked into the stills: count faces there too
            r["faces_key"] = len(faces(cv2.imread(ks)))
    # expected characters from the clip prompt
    if chars is not None or prompt is not None:
        ex = chars if chars is not None else expected_chars(prompt)
        r["expect"] = len(ex)
        r["chars"] = ",".join(ex)
    # flags
    F = r["flags"]
    if r["striped_frames"]:
        F.append(f"STRIPES({r['striped_frames']})")
    if r["sharp_drop"] < TH["sharp_drop"]:
        F.append("SOFT")
    if r.get("face_sharp") is not None and r["face_sharp"] < TH["face_sharp"]:
        F.append("FACE_SMEAR")
    if faces.ok:
        if r["faces_last"] > r["faces_first"]:
            F.append("FACE_ADDED")
        if r["faces_last"] < r["faces_first"]:
            F.append("FACE_LOST")
        if r.get("expect") and r["faces_mode"] > r["expect"]:
            F.append("DUP?")
        if r["faces_mode"] >= 3:
            F.append("CROWD")
        if 0 < r["face_h"] < TH["small_face"]:
            F.append("SMALL_FACE")
    if r["jump"] > TH["jump"]:
        F.append("JUMP")
    if r.get("text_frames"):
        F.append("TEXT")
    if r.get("key_start") is not None and r["key_start"] < TH["key_start"]:
        F.append("START_MISMATCH")
    if r.get("key_end") is not None and r["key_end"] < TH["key_end"]:
        F.append("END_MISS")
    if r.get("key_pair") is not None and r["key_pair"] < TH["key_pair"]:
        F.append("MORPH_RISK")
    if r.get("expect") and r.get("faces_key", 0) > r["expect"]:
        F.append("DUP_IN_STILL?")
    if r["w"] and r["h"] and max(r["w"], r["h"]) < 1280:
        F.append("LOWRES")
    return r


def score(r):
    """FAIL = a defect the creator would see; WARN = risk; PASS otherwise."""
    hard = {"STRIPES", "FACE_SMEAR", "JUMP", "TEXT", "DUP?", "DUP_IN_STILL?", "MORPH_RISK", "SPEED", "LOWRES"}
    soft = {"SOFT", "FACE_ADDED", "FACE_LOST", "CROWD", "SMALL_FACE", "START_MISMATCH", "END_MISS", "SLOWMO", "TRUNC", "FREEZE"}
    names = {re.sub(r"\(.*", "", f) for f in r["flags"]}
    if names & hard:
        return "FAIL"
    if len(names & soft) >= 2:
        return "WARN"
    return "WARN" if names & soft else "PASS"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="*", help="clip files or folders")
    ap.add_argument("--frames", help="folder with <id>.png / <id>_end.png keyframes (+ _land)")
    ap.add_argument("--clips-json", help="clips.json of the GPU job (prompts -> expected characters)")
    ap.add_argument("--script", help="episode script .md: expected characters per clip from the START/END keyframe columns")
    ap.add_argument("--spec", help="episode spec: adds edit timing (slow motion, truncation, frozen tail)")
    ap.add_argument("--only", nargs="*", default=[], help="clip ids to check (prefix match)")
    ap.add_argument("--json", help="write the full report as JSON")
    ap.add_argument("--md", help="write the table as Markdown")
    ap.add_argument("--fetch-models", action="store_true")
    a = ap.parse_args()
    if a.fetch_models:
        fetch_models()
        if not a.inputs:
            return 0
    files = []
    for p in a.inputs:
        files += sorted(glob.glob(os.path.join(p, "*.mp4"))) if os.path.isdir(p) else [p]
    if a.only:
        files = [f for f in files if any(os.path.basename(f).startswith(o) for o in a.only)]
    if not files:
        ap.error("no clips")
    faces, text = Faces(), Text()
    if not faces.ok:
        print("note: no face model (run --fetch-models); face checks skipped", file=sys.stderr)
    if not text.ok:
        print("note: no text model (run --fetch-models); text check skipped", file=sys.stderr)
    prompts = load_clip_prompts(a.clips_json)
    script_chars = load_script_chars(a.script)
    timing = {}
    if a.spec:
        try:
            timing = timing_from_spec(a.spec)
        except Exception as e:      # timing needs the voices; the visual checks still run
            print("note: timing skipped:", e, file=sys.stderr)
    rows = []
    for f in files:
        cid = os.path.splitext(os.path.basename(f))[0]
        base = cid[:-5] if cid.endswith("_land") else cid
        r = analyse(f, faces, text, a.frames, prompts.get(base) if prompts else None, chars=script_chars.get(base))
        t = timing.get(base)
        if t:
            r["edit_speed"] = round(t["speed"], 2)
            r["shown"] = round(t["shown"] / max(1e-6, r["dur"]), 2)
            r["frozen"] = round(t["frozen"], 2)
            if t["speed"] < TH["slowmo"]:
                r["flags"].append("SLOWMO")
            if r["shown"] < TH["trunc"]:
                r["flags"].append("TRUNC")
            if t["frozen"] > TH["freeze"]:
                r["flags"].append("FREEZE")
        # speed anomaly: the two orientations of a clip should have the same length
        rows.append(r)
    by = {r["id"]: r for r in rows}
    for r in rows:
        if r["id"].endswith("_land") and r["id"][:-5] in by and abs(by[r["id"][:-5]]["dur"] - r["dur"]) > 0.3:
            r["flags"].append("SPEED")
        r["verdict"] = score(r)
    cols = ["id", "verdict", "dur", "eff_fps", "stripes", "sharp_drop", "faces_first", "faces_last", "faces_max", "faces_key", "expect", "face_h", "face_sharp",
            "jump", "jump_at", "text_frames", "key_start", "key_end", "key_pair", "edit_speed", "shown", "frozen", "flags"]
    cols = [c for c in cols if any(c in r for r in rows)]

    def cell(r, c):
        v = r.get(c, "")
        return " ".join(v) if isinstance(v, list) else ("" if v is None else str(v))
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(cell(r, c) for c in cols) + " |" for r in rows]
    print("\n".join(lines))
    n = {k: sum(r["verdict"] == k for r in rows) for k in ("FAIL", "WARN", "PASS")}
    allf = {}
    for r in rows:
        for fl in r["flags"]:
            k = re.sub(r"\(.*", "", fl); allf[k] = allf.get(k, 0) + 1
    summary = f"{len(rows)} clips: {n['FAIL']} FAIL, {n['WARN']} WARN, {n['PASS']} PASS. Flags: " + ", ".join(f"{k} {v}" for k, v in sorted(allf.items(), key=lambda x: -x[1]))
    print(summary)
    if a.md:
        open(a.md, "w").write("\n".join(lines) + "\n\n" + summary + "\n")
    if a.json:
        json.dump(dict(thresholds=TH, rows=rows, summary=summary), open(a.json, "w"), indent=1)
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
