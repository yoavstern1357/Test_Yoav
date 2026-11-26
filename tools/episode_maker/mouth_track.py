#!/usr/bin/env python3
"""Mouth-point tracker for anime talk shots (fix-plan.md Fix 5a). CPU only: OpenCV + numpy, YuNet (MIT) for the first guess.

    python3 mouth_track.py specs/clips/ep01v44/C36.mp4 --out out/C36.track.json --debug out/C36.track.jpg
    python3 mouth_track.py clip.mp4 --point 455,606 --face-h 207 --out track.json   # manual mouth point (one click on frame 1)

How it works:
  1. Start point: --point (manual) or YuNet on frame 1 at several scales (anime faces are found far more reliably when the
     face is about 100 px tall, so the frame is downscaled); mouth = middle of the two mouth-corner landmarks, then
     refined to the darkest line-art stroke below the nose (the drawn mouth). --near x,y picks the face nearest a point.
  2. Every frame: pyramidal Lucas-Kanade optical flow on corner features inside the face box (forward-backward checked),
     a RANSAC similarity transform (shift + scale + rotation) moves the mouth point; features are re-seeded when they
     run out. On-twos duplicate frames give an identity transform.
  3. Drift correction: when YuNet finds a confident face whose mouth lies near the tracked point, the point is pulled
     15% toward it (the landmark offset measured on frame 1 is kept).
Output JSON: {"fps", "w", "h", "face_h", "mouth_w", "frames": [{"x", "y", "s", "a", "ok"}]}  s = face scale vs frame 1,
a = head roll in degrees, ok = false when tracking lost (the overlay then hides the sprite).
Limits: assumes a fixed camera and a calm head (talk shots under fix-plan Fix 2); big head turns or a face leaving the
frame end the track (ok = false).
"""
import argparse, json, os, sys
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
YUNET = os.path.join(HERE, "assets", "qc_models", "yunet.onnx")


def read_frames(path):
    cap, out = cv2.VideoCapture(path), []
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(f)
    return out, fps


class Yunet:
    """YuNet at several scales; returns faces as dicts in full-frame coordinates (box, 5 landmarks, score)."""
    def __init__(self, thresh=0.5):
        if not os.path.exists(YUNET):
            sys.exit("YuNet model missing: run  python3 qc_clips.py --fetch-models")
        self.det = cv2.FaceDetectorYN.create(YUNET, "", (320, 320), thresh, 0.3, 50)

    def detect(self, f, scales=(0.5, 0.33, 0.25, 1.0)):
        found = []
        for sc in scales:
            g = cv2.resize(f, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA) if sc != 1.0 else f
            self.det.setInputSize((g.shape[1], g.shape[0]))
            _, d = self.det.detect(g)
            for x in ([] if d is None else d):
                v = x[:14] / sc
                found.append(dict(box=[float(t) for t in v[:4]], lm=v[4:14].reshape(5, 2).astype(float), score=float(x[14]), scale=sc))
        return nms(found)


def nms(faces, iou_th=0.3):
    faces = sorted(faces, key=lambda d: -d["score"])
    keep = []
    for d in faces:
        if all(iou(d["box"], k["box"]) < iou_th for k in keep):
            keep.append(d)
    return keep


def iou(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    ix, iy = max(0, min(ax + aw, bx + bw) - max(ax, bx)), max(0, min(ay + ah, by + bh) - max(ay, by))
    inter = ix * iy
    return inter / (aw * ah + bw * bh - inter + 1e-6)


def mouth_of(face):
    return (face["lm"][3] + face["lm"][4]) / 2.0


def refine_mouth(f, guess, face_h):
    """Move the guess to the centre of the drawn mouth: the darkest stroke pixels in a window below the nose."""
    x0, y0 = guess
    rw, rh = int(0.22 * face_h), int(0.12 * face_h)
    X0, Y0 = max(0, int(x0 - rw)), max(0, int(y0 - rh))
    win = cv2.cvtColor(f[Y0:int(y0 + rh), X0:int(x0 + rw)], cv2.COLOR_BGR2GRAY).astype(np.float32)
    if win.size == 0:
        return guess, None
    skin, darkest = np.median(win), np.percentile(win, 0.5)   # the stroke is thin: a few % of the window at most
    if skin - darkest < 30:                      # no clear stroke (soft or tiny face): keep the landmark guess
        return guess, None
    m = (win <= skin - max(18.0, 0.2 * (skin - darkest))).astype(np.uint8)
    k = max(3, int(0.05 * face_h)) | 1           # join the broken pieces of a thin mouth line
    m = cv2.dilate(m, np.ones((3, k), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n <= 1:
        return guess, None
    c = np.array([rw, rh], float)
    best = max(range(1, n), key=lambda j: st[j, cv2.CC_STAT_AREA] / (1.0 + np.linalg.norm(cen[j] - c) / (0.1 * face_h)))
    x, y, w, h = st[best, :4]
    w = max(1, w - k + 1)                         # undo the dilation width
    return (X0 + x + (w + k - 1) / 2.0, Y0 + y + h / 2.0), float(w)


def track(frames, start, face_h, box, yunet=None, det_offset=None, fps=24.0):
    H, W = frames[0].shape[:2]
    pt = np.array(start, float)
    S, A = 1.0, 0.0
    out = [dict(x=round(pt[0], 1), y=round(pt[1], 1), s=1.0, a=0.0, ok=True)]
    prev = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
    bx, by, bw, bh = box

    def seed(gray, center, scale):
        m = np.zeros_like(gray)
        hw, hh = 0.75 * bw * scale, 0.75 * bh * scale
        cx, cy = center[0], center[1] - 0.25 * bh * scale     # face centre is above the mouth
        cv2.rectangle(m, (int(cx - hw), int(cy - hh)), (int(cx + hw), int(cy + hh)), 255, -1)
        cv2.ellipse(m, (int(center[0]), int(center[1])), (int(0.18 * bh * scale), int(0.10 * bh * scale)), 0, 0, 360, 0, -1)  # not the mouth itself
        return cv2.goodFeaturesToTrack(gray, 200, 0.01, 5, mask=m)

    pts = seed(prev, pt, S)
    ok_track = True
    lk = dict(winSize=(21, 21), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
    for i in range(1, len(frames)):
        gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
        if ok_track and pts is not None and len(pts) >= 6:
            nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev, gray, pts, None, **lk)
            back, st2, _ = cv2.calcOpticalFlowPyrLK(gray, prev, nxt, None, **lk)
            fb = np.linalg.norm((pts - back).reshape(-1, 2), axis=1)
            good = (st.ravel() == 1) & (st2.ravel() == 1) & (fb < 1.0)
            p0, p1 = pts[good].reshape(-1, 2), nxt[good].reshape(-1, 2)
            if len(p0) >= 6:
                M, inl = cv2.estimateAffinePartial2D(p0, p1, method=cv2.RANSAC, ransacReprojThreshold=2.0)
                if M is not None:
                    pt = M[:, :2] @ pt + M[:, 2]
                    S *= float(np.sqrt(abs(np.linalg.det(M[:, :2]))))
                    A += float(np.degrees(np.arctan2(M[1, 0], M[0, 0])))
                    pts = p1[inl.ravel() == 1].reshape(-1, 1, 2) if inl is not None else p1.reshape(-1, 1, 2)
                else:
                    ok_track = False
            else:
                ok_track = False
            if pts is None or len(pts) < 40:
                pts = seed(gray, pt, S)
        # drift correction toward a confident detection near the tracked point
        if yunet is not None and det_offset is not None:
            for d in yunet.detect(frames[i], scales=(0.5,)):
                if d["score"] < 0.6:
                    continue
                dm = mouth_of(d) + det_offset * S
                if np.linalg.norm(dm - pt) < 0.25 * face_h * S:
                    pt = 0.85 * pt + 0.15 * dm
                    ok_track = True
                    break
        inside = 0 <= pt[0] < W and 0 <= pt[1] < H
        out.append(dict(x=round(float(pt[0]), 1), y=round(float(pt[1]), 1), s=round(S, 4), a=round(A, 2), ok=bool(ok_track and inside)))
        prev = gray
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("--out", required=True)
    ap.add_argument("--point", help="manual mouth point on frame 1: x,y (pixels)")
    ap.add_argument("--face-h", type=float, help="face height in pixels (with --point; default 16%% of frame height)")
    ap.add_argument("--near", help="x,y: pick the detected face nearest this point (2-shots)")
    ap.add_argument("--no-refine", action="store_true", help="keep the YuNet landmark mouth (no stroke search)")
    ap.add_argument("--no-drift", action="store_true", help="optical flow only, no YuNet drift correction")
    ap.add_argument("--debug", help="write a contact sheet JPG with the tracked point on 8 frames")
    a = ap.parse_args()
    frames, fps = read_frames(a.clip)
    if not frames:
        sys.exit("cannot read " + a.clip)
    H, W = frames[0].shape[:2]
    yunet = None if (a.point and a.no_drift) else Yunet()
    det_offset, mouth_w, source = None, None, "manual"
    if a.point:
        x, y = [float(v) for v in a.point.split(",")]
        face_h = a.face_h or 0.16 * H
        box = [x - 0.4 * face_h, y - 0.75 * face_h, 0.8 * face_h, face_h]
        start = (x, y)
        if yunet is not None:
            fs = yunet.detect(frames[0])
            near = [d for d in fs if np.linalg.norm(mouth_of(d) - start) < 0.3 * face_h]
            if near:
                det_offset = (np.array(start) - mouth_of(near[0]))
    else:
        fs = yunet.detect(frames[0])
        if not fs:
            sys.exit("no face found on frame 1: give --point x,y (and --face-h)")
        if a.near:
            nx, ny = [float(v) for v in a.near.split(",")]
            d = min(fs, key=lambda f: np.linalg.norm(mouth_of(f) - (nx, ny)))
        else:
            d = max(fs, key=lambda f: f["score"] * f["box"][3])
        box, face_h = d["box"], d["box"][3]
        start = tuple(mouth_of(d))
        if not a.no_refine:
            start, mouth_w = refine_mouth(frames[0], start, face_h)
        det_offset = np.array(start) - mouth_of(d)
        source = f"yunet score {d['score']:.2f} at scale {d['scale']}"
    fr = track(frames, start, face_h, box, None if a.no_drift else yunet, det_offset, fps)
    res = dict(clip=os.path.basename(a.clip), fps=fps, w=W, h=H, face_h=round(float(face_h), 1), face_box=[round(float(v), 1) for v in box],
               mouth_w=round(mouth_w, 1) if mouth_w else None, source=source, frames=fr)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=0)
    lost = sum(not f["ok"] for f in fr)
    xs, ys = [f["x"] for f in fr], [f["y"] for f in fr]
    print(f"{a.clip}: {len(fr)} frames, start ({start[0]:.0f},{start[1]:.0f}) face_h {face_h:.0f}px ({source}); "
          f"path range x {min(xs):.0f}-{max(xs):.0f} y {min(ys):.0f}-{max(ys):.0f}; lost frames {lost} -> {a.out}")
    if a.debug:
        idx = np.linspace(0, len(frames) - 1, 8).astype(int)
        tiles = []
        for i in idx:
            f = frames[i].copy(); p = fr[i]
            c = (int(p["x"]), int(p["y"]))
            cv2.circle(f, c, max(3, int(0.03 * face_h)), (0, 0, 255) if p["ok"] else (128, 128, 128), -1)
            r = int(0.6 * face_h * p["s"])
            y0, x0 = max(0, c[1] - r), max(0, c[0] - r)
            crop = cv2.resize(f[y0:c[1] + r, x0:c[0] + r], (240, 240))
            cv2.putText(crop, str(i), (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            tiles.append(crop)
        cv2.imwrite(a.debug, np.hstack(tiles))
    return 0


if __name__ == "__main__":
    sys.exit(main())
