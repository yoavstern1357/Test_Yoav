#!/usr/bin/env python3
"""Anime mouth-flap compositor (fix-plan.md Fix 5a): clip + Rhubarb mouth cues + mouth sprites + tracked mouth point -> talking clip.
CPU only (OpenCV, numpy, ffmpeg). Sprite spec: production/v4/mouth-sprite-spec.md.

    python3 mouth_overlay.py specs/clips/ep01v44/C36.mp4 --wav tts/gpu/034b8c85a93d3ec5.wav \
        --text "Dad was right... the best part is worth the wait." --char boy --offset 0.6 --dur 5 \
        --out out/mouth-demo.mp4                       # tracks the mouth itself (mouth_track.py) and runs Rhubarb
    python3 mouth_overlay.py clip.mp4 --wav line.wav --cues line.rhubarb.json --track clip.track.json \
        --sprites specs/mouths/boy --out talk.mp4       # with precomputed cues / track and drawn sprites
    python3 mouth_overlay.py --fetch-rhubarb           # once: Rhubarb Lip Sync 1.14.0 (MIT) into assets/rhubarb/

Rhubarb shapes -> our 6 sprites (MOUTH_MAP): A (M/B/P, closed) and X (rest) -> rest; B (most consonants, teeth) and G (F/V) ->
teeth; C (EH, open) and H (L) -> open; D (AA, wide) -> wide; E (AO/ER, round) -> round; F (UW/W, pucker) -> pucker.
"rest" keeps the ORIGINAL drawn mouth of the clip (no paste), so silence and closed consonants look exactly like the animation;
all other shapes first erase the original mouth stroke (inpainting of the line pixels on the flat skin) and paste the sprite at
the tracked point, scaled with the face and rotated with the head. --sprites DIR loads <shape>.png (RGBA, mouth centred, see
the spec); without it a procedural sprite set is drawn in the line colour sampled from the clip (prototype).
--on-twos changes the mouth only every 2nd frame (TV-anime timing, matches 12 fps "on twos" picture).
--loop pingpong|hold|loop extends a short clip to --dur. The audio line is placed at --offset seconds.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, urllib.request, zipfile
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
RHUBARB_DIR = os.path.join(HERE, "assets", "rhubarb")
RHUBARB = os.path.join(RHUBARB_DIR, "rhubarb")
RHUBARB_URL = "https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.14.0/Rhubarb-Lip-Sync-1.14.0-Linux.zip"
MOUTH_MAP = {"X": "rest", "A": "rest", "B": "teeth", "G": "teeth", "C": "open", "H": "open", "D": "wide", "E": "round", "F": "pucker"}
SHAPES = ["rest", "teeth", "open", "wide", "round", "pucker"]
# procedural sprite sizes as a fraction of the frame-1 mouth width (the drawn closed mouth), per character (width, height)
PROC = {
    "boy":     {"teeth": (0.62, 0.20), "open": (0.52, 0.36), "wide": (0.60, 0.52), "round": (0.42, 0.40), "pucker": (0.30, 0.28)},
    "uncle":   {"teeth": (0.70, 0.18), "open": (0.60, 0.34), "wide": (0.70, 0.55), "round": (0.46, 0.42), "pucker": (0.32, 0.30)},
    "grandma": {"teeth": (0.58, 0.16), "open": (0.50, 0.30), "wide": (0.56, 0.44), "round": (0.38, 0.34), "pucker": (0.26, 0.24)},
}


def fetch_rhubarb():
    if os.path.exists(RHUBARB):
        print("have", RHUBARB); return
    tmp = tempfile.mkdtemp()
    z = os.path.join(tmp, "r.zip")
    print("fetch", RHUBARB_URL)
    urllib.request.urlretrieve(RHUBARB_URL, z)
    with zipfile.ZipFile(z) as f:
        f.extractall(tmp)
    src = [os.path.join(tmp, d) for d in os.listdir(tmp) if d.startswith("Rhubarb")][0]
    shutil.copytree(src, RHUBARB_DIR, dirs_exist_ok=True)
    os.chmod(RHUBARB, 0o755)
    print("installed", RHUBARB)


def run_rhubarb(wav, text=None, out_json=None, recognizer="pocketSphinx"):
    if not os.path.exists(RHUBARB):
        sys.exit("Rhubarb missing: python3 mouth_overlay.py --fetch-rhubarb")
    out_json = out_json or os.path.splitext(wav)[0] + ".rhubarb.json"
    cmd = [RHUBARB, "-q", "-f", "json", "-r", recognizer, "-o", out_json]
    if text:
        tf = out_json + ".txt"
        open(tf, "w").write(text + "\n")
        cmd += ["--dialogFile", tf]
    subprocess.run(cmd + [wav], check=True)
    return out_json


def load_cues(path):
    j = json.load(open(path))
    return [(float(c["start"]), float(c["end"]), c["value"]) for c in j["mouthCues"]]


def cue_at(cues, t):
    for a, b, v in cues:
        if a <= t < b:
            return v
    return "X"


def loudness(wav, fps):
    """Per-video-frame RMS of the line (0-1 rank among voiced frames), for --energy."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float32) / 32768.0
    hop = 16000 / fps
    rms = np.array([np.sqrt(np.mean(x[int(i * hop):int((i + 1) * hop)] ** 2) + 1e-9) for i in range(int(len(x) / hop))])
    voiced = rms[rms > 0.1 * rms.max()]
    return lambda t: float((voiced < rms[min(len(rms) - 1, max(0, int(t * fps)))]).mean()) if len(voiced) and t >= 0 else 0.0


def read_frames(path):
    cap, out = cv2.VideoCapture(path), []
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(f)
    return out, fps


def frame_order(n, total, mode):
    if mode == "loop":
        return [i % n for i in range(total)]
    if mode == "hold":
        return [min(i, n - 1) for i in range(total)]
    seq = list(range(n)) + list(range(n - 2, 0, -1))        # pingpong
    return [seq[i % len(seq)] for i in range(total)]


# ------------------------------------------------------------------ sprites
def line_color(frame, pt, mouth_w):
    x, y = int(pt[0]), int(pt[1])
    r = max(6, int(0.6 * mouth_w))
    win = frame[max(0, y - r // 2):y + r // 2, max(0, x - r):x + r].reshape(-1, 3).astype(np.float32)
    g = win.mean(axis=1)
    dark = win[g <= np.percentile(g, 3)]
    return tuple(int(v) for v in dark.mean(axis=0)) if len(dark) else (40, 50, 70)


def procedural_sprites(char, line_bgr, mouth_w, line_px=2.0):
    """Prototype sprite set drawn with OpenCV. Canvas scale: the frame-1 mouth width = 400 canvas px, so a sprite of
    w_frac f is pasted f * mouth_w wide. Each sprite: dict(img=RGBA, w_frac, anchor=(x, y) on the top lip line)."""
    out, U = {}, 400.0
    t = max(3, int(round(line_px * U / max(8.0, mouth_w))))     # outline about line_px output pixels wide
    inner, tongue, teeth = (45, 40, 105), (120, 125, 225), (235, 245, 250)   # BGR
    for name, (wf, hf) in PROC[char].items():
        W, H = int(U * wf), int(U * hf)
        pad = t * 2
        img = np.zeros((H + 2 * pad, W + 2 * pad, 4), np.uint8)
        cx, cy = W // 2 + pad, pad
        if name == "teeth":            # wide flat lens, upper teeth showing
            top = [(cx + (u - 0.5) * W, cy + 0.15 * H * np.sin(np.pi * u)) for u in np.linspace(0, 1, 41)]
            bot = [(cx + (u - 0.5) * 0.9 * W, cy + H * (0.2 + 0.8 * np.sin(np.pi * u))) for u in np.linspace(1, 0, 41)]
            poly = np.array(top + bot, np.int32)
        elif name in ("open", "wide"):  # anime "D" mouth: gently curved top lip, round lower jaw
            top = [(cx + (u - 0.5) * W, cy + 0.08 * H * np.sin(np.pi * u)) for u in np.linspace(0, 1, 41)]
            bot = [(cx + 0.5 * W * np.cos(a), cy + 0.08 * H + 0.92 * H * np.sin(a)) for a in np.linspace(0, np.pi, 41)]
            poly = np.array(top + bot, np.int32)
        else:                          # round / pucker: ellipse hanging from the anchor
            poly = cv2.ellipse2Poly((cx, cy + H // 2), (W // 2, H // 2), 0, 0, 360, 6)
        fill = np.zeros(img.shape[:2], np.uint8)
        cv2.fillPoly(fill, [poly], 255)
        img[fill > 0, :3] = inner
        if name in ("open", "wide", "round"):
            tg = np.zeros_like(fill)
            cv2.ellipse(tg, (cx, int(cy + 1.0 * H)), (int(0.32 * W), int(0.38 * H)), 0, 0, 360, 255, -1)
            img[(tg > 0) & (fill > 0), :3] = tongue
        if name == "teeth":
            img[:int(cy + 0.55 * H)][fill[:int(cy + 0.55 * H)] > 0, :3] = teeth
        img[fill > 0, 3] = 255
        cv2.polylines(img, [poly], True, (*line_bgr, 255), t, cv2.LINE_AA)
        out[name] = dict(img=img, w_frac=img.shape[1] / U, anchor=(cx, cy))
    return out


def load_sprites(folder):
    """<folder>/<shape>.png (RGBA) + optional sprites.json {"<shape>": {"w_frac": .., "anchor": [x, y]}}."""
    meta = {}
    mp = os.path.join(folder, "sprites.json")
    if os.path.exists(mp):
        meta = json.load(open(mp))
    out = {}
    for s in SHAPES[1:]:
        p = os.path.join(folder, s + ".png")
        if not os.path.exists(p):
            continue
        img = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        m = meta.get(s, {})
        out[s] = dict(img=img, w_frac=float(m.get("w_frac", 0.6)), anchor=tuple(m.get("anchor", (img.shape[1] / 2, img.shape[0] * 0.3))))
    return out


# ------------------------------------------------------------------ compositing
def erase_mouth(frame, pt, mouth_w, s):
    """Remove the drawn mouth stroke near pt by inpainting the dark line pixels (skin around the mouth is flat)."""
    x, y = pt
    rx, ry = int(0.75 * mouth_w * s) + 3, int(0.35 * mouth_w * s) + 3
    X0, Y0, X1, Y1 = max(0, int(x - 2 * rx)), max(0, int(y - 2 * ry)), int(x + 2 * rx), int(y + 2 * ry)
    roi = frame[Y0:Y1, X0:X1]
    g = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY).astype(np.float32)
    ell = np.zeros(g.shape, np.uint8)
    cv2.ellipse(ell, (int(x - X0), int(y - Y0)), (rx, ry), 0, 0, 360, 255, -1)
    skin = np.median(g[ell > 0])
    m = ((g < skin - 14) & (ell > 0)).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    frame[Y0:Y1, X0:X1] = cv2.inpaint(roi, m, 5, cv2.INPAINT_TELEA)
    return frame


def paste(frame, spr, pt, mouth_w, s, angle):
    img = spr["img"]
    target_w = spr["w_frac"] * mouth_w * s
    k = target_w / img.shape[1]
    ax, ay = spr["anchor"]
    M = cv2.getRotationMatrix2D((ax, ay), -angle, k)
    M[0, 2] += pt[0] - ax
    M[1, 2] += pt[1] - ay
    H, W = frame.shape[:2]
    warped = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    a = warped[:, :, 3:4].astype(np.float32) / 255.0
    return (frame.astype(np.float32) * (1 - a) + warped[:, :, :3].astype(np.float32) * a).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--wav", help="the voice line (also muxed into the output)")
    ap.add_argument("--text", help="line text for Rhubarb's dialog option (better phonemes)")
    ap.add_argument("--cues", help="Rhubarb JSON (default: run Rhubarb on --wav)")
    ap.add_argument("--recognizer", default="pocketSphinx", choices=["pocketSphinx", "phonetic"])
    ap.add_argument("--track", help="mouth_track.py JSON (default: track now)")
    ap.add_argument("--point", help="manual mouth point x,y on frame 1 (passed to the tracker)")
    ap.add_argument("--sprites", help="folder with <shape>.png sprites (default: procedural)")
    ap.add_argument("--char", default="boy", choices=sorted(PROC))
    ap.add_argument("--offset", type=float, default=0.3, help="seconds from clip start to the start of the line")
    ap.add_argument("--dur", type=float, help="output length (default: clip length)")
    ap.add_argument("--loop", default="pingpong", choices=["pingpong", "hold", "loop"])
    ap.add_argument("--on-twos", action="store_true", help="change the mouth only on every 2nd frame")
    ap.add_argument("--energy", type=float, default=0.0, metavar="RANK",
                    help="open the mouth more on loud frames: a teeth (B) cue on a frame louder than this rank of the voiced "
                         "frames (0-1, e.g. 0.6) becomes open, and an open (C) cue above (1+RANK)/2 becomes wide; 0 = off")
    ap.add_argument("--sprite-scale", type=float, default=1.0)
    ap.add_argument("--debug-sheet", help="write a JPG strip of face crops (frame, cue) for review")
    ap.add_argument("--fetch-rhubarb", action="store_true")
    a = ap.parse_args()
    if a.fetch_rhubarb:
        fetch_rhubarb()
        if not a.clip:
            return 0
    if not (a.clip and a.out):
        ap.error("clip and --out are required")
    frames, fps = read_frames(a.clip)
    if not frames:
        sys.exit("cannot read " + a.clip)
    # track
    if a.track:
        tr = json.load(open(a.track))
    else:
        tj = os.path.splitext(a.out)[0] + ".track.json"
        cmd = [sys.executable, os.path.join(HERE, "mouth_track.py"), a.clip, "--out", tj]
        if a.point:
            cmd += ["--point", a.point]
        subprocess.run(cmd, check=True)
        tr = json.load(open(tj))
    mouth_w = tr.get("mouth_w") or 0.25 * tr["face_h"]
    # cues
    cues = []
    if a.cues:
        cues = load_cues(a.cues)
    elif a.wav:
        cues = load_cues(run_rhubarb(a.wav, a.text, os.path.splitext(a.out)[0] + ".rhubarb.json", a.recognizer))
    # sprites
    p0 = (tr["frames"][0]["x"], tr["frames"][0]["y"])
    sprites = load_sprites(a.sprites) if a.sprites else procedural_sprites(a.char, line_color(frames[0], p0, mouth_w), mouth_w)
    for s in sprites.values():
        s["w_frac"] *= a.sprite_scale
    loud = loudness(a.wav, fps) if (a.wav and a.energy > 0) else None
    n = len(frames)
    total = int(round((a.dur or n / fps) * fps))
    order = frame_order(n, total, a.loop)
    H, W = frames[0].shape[:2]
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
    if a.wav:
        cmd += ["-i", a.wav, "-filter_complex", f"[1:a]adelay={int(a.offset * 1000)}:all=1,apad[aud]", "-map", "0:v", "-map", "[aud]",
                "-c:a", "aac", "-b:a", "160k"]
    cmd += ["-t", f"{total / fps:.3f}", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    used, review = {}, []
    held = "rest"
    for i in range(total):
        src = order[i]
        f = frames[src].copy()
        p = tr["frames"][src]
        t = i / fps - a.offset
        shape = MOUTH_MAP.get(cue_at(cues, t), "rest") if cues else "rest"
        if loud and shape in ("teeth", "open"):
            q = loud(t)
            if shape == "teeth" and q > a.energy:
                shape = "open"
            elif shape == "open" and q > (1 + a.energy) / 2:
                shape = "wide"
        if a.on_twos and i % 2 == 1:
            shape = held
        held = shape
        if shape != "rest" and shape in sprites and p["ok"]:
            f = erase_mouth(f, (p["x"], p["y"]), mouth_w, p["s"])
            f = paste(f, sprites[shape], (p["x"], p["y"]), mouth_w, p["s"], p["a"])
        used[shape] = used.get(shape, 0) + 1
        if a.debug_sheet and i % 3 == 0 and 0 <= t <= (cues[-1][1] if cues else 0):
            r = int(0.45 * tr["face_h"] * p["s"])
            x, y = int(p["x"]), int(p["y"] - 0.2 * tr["face_h"])
            c = cv2.resize(f[max(0, y - r):y + r, max(0, x - r):x + r], (200, 200))
            cv2.putText(c, f"{i} {cue_at(cues, t)}>{shape}", (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            review.append(c)
        ff.stdin.write(f.tobytes())
    ff.stdin.close()
    ff.wait()
    if a.debug_sheet and review:
        rows = [np.hstack(review[k:k + 8] + [np.zeros_like(review[0])] * (8 - len(review[k:k + 8]))) for k in range(0, len(review), 8)]
        cv2.imwrite(a.debug_sheet, np.vstack(rows))
    print(f"wrote {a.out}: {total} frames at {fps:g} fps, mouth shapes used {used}")
    return ff.returncode


if __name__ == "__main__":
    sys.exit(main())
