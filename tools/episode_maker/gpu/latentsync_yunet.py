#!/usr/bin/env python3
"""Drop-in replacement for LatentSync's face detector (latentsync/utils/face_detector.py) WITHOUT InsightFace.

Why: LatentSync 1.5/1.6 code is Apache-2.0, but its preprocessing calls InsightFace FaceAnalysis (detection +
landmark_2d_106); InsightFace's pretrained models are for non-commercial research only (fix-plan.md Fix 5b). This module
gives the same interface from YuNet (MIT, opencv_zoo, 5 landmarks) or from a fixed face box (our QC / mouth tracker):
  FaceDetector(device).__call__(frame RGB uint8) -> (x1, y1, x2, y2), landmark_2d_106 (106 x 2 int array)
Only the 106-point indices that LatentSync reads are filled: the eyebrow centres (43 48 49 51 50 / 101-105), the nose
(73 74 77 83 86) and the contour/brow order LMK_ADAPT_ORIGIN_ORDER used for the crop box. The 3-point alignment
(left brow, right brow, nose) is then exactly LatentSync's own code path.

Use on Kaggle (after cloning LatentSync):  cp latentsync_yunet.py LatentSync/latentsync/utils/face_detector.py
(the file keeps the class name FaceDetector and the LMK_ADAPT_ORIGIN_ORDER constant), and put yunet.onnx next to it or set
YUNET_ONNX. Remove insightface from requirements. Untested on a GPU (task D was cancelled by the creator's redesign
decision); the alignment preview below was checked on CPU on our clips:
    python3 latentsync_yunet.py ../specs/clips/ep01v44/C36.mp4 --preview out.jpg
Anime tuning: anime eyes are big and low, so "eyebrows" and "nose" are not taken from the face directly. Instead the eye
centres and the mouth centre are mapped to where LatentSync's crop expects them (eyes just above its mouth mask, mouth in
the middle of it: EYE_T / MOUTH_T in template units) and the 3 template points are projected back into the image.
"""
import os, sys
import numpy as np
import cv2

YUNET_ONNX = os.environ.get("YUNET_ONNX") or next(
    (p for p in (os.path.join(os.path.dirname(os.path.abspath(__file__)), "yunet.onnx"),
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "qc_models", "yunet.onnx")) if os.path.exists(p)),
    "yunet.onnx")
# LatentSync's 3-point template (units before its x2.8 crop ratio): brows (17, 20), (58, 20), nose (37.5, 40); the
# 210 x 280 crop's mouth mask starts at about y 37 in these units. Our targets for the anime eye centres and the mouth:
TEMPLATE = np.array([[17, 20], [58, 20], [37.5, 40]], np.float32)
EYE_T = [(21, 27), (54, 27)]
MOUTH_T = (37.5, 64)
SCALES = (0.5, 0.33, 0.25, 1.0)

LMK_ADAPT_ORIGIN_ORDER = [1, 10, 12, 14, 16, 3, 5, 7, 0, 23, 21, 19, 32, 30, 28, 26, 17, 43, 48, 49, 51, 50, 102, 103, 104, 105,
                          101, 73, 74, 86]   # copied from LatentSync (the points it uses for the crop box)
CONTOUR = [1, 10, 12, 14, 16, 3, 5, 7, 0, 23, 21, 19, 32, 30, 28, 26, 17]   # jaw line, left to right through the chin (0)


def synth_106(box, eye_l, eye_r, mouth):
    """Fill the 106-point indices LatentSync reads, from a face box, the two eye centres and the mouth centre."""
    x, y, w, h = box
    src = np.array([eye_l, eye_r, mouth], np.float32)
    M, _ = cv2.estimateAffinePartial2D(src, np.array(EYE_T + [MOUTH_T], np.float32))
    Mi = cv2.invertAffineTransform(M)
    brow_l, brow_r, nose = (Mi[:, :2] @ TEMPLATE.T + Mi[:, 2:]).T
    lmk = np.zeros((106, 2), np.float32)
    for i in (43, 48, 49, 51, 50):
        lmk[i] = brow_l
    for i in range(101, 106):
        lmk[i] = brow_r
    for i in (73, 74, 77, 83, 86):
        lmk[i] = nose
    cx, top, bot = x + w / 2, nose[1], y + h           # jaw contour (crop box only): half ellipse through the chin
    for k, i in enumerate(CONTOUR):
        a = np.pi * k / (len(CONTOUR) - 1)
        lmk[i] = (cx - 0.5 * w * np.cos(a), top + (bot - top) * np.sin(a))
    return lmk


class FaceDetector:
    """Same interface as LatentSync's InsightFace FaceDetector. fixed_box=(x, y, w, h) skips detection (tracked boxes)."""
    def __init__(self, device="cuda", fixed_box=None, fixed_points=None):
        self.fixed_box, self.fixed_points = fixed_box, fixed_points
        self.det = cv2.FaceDetectorYN.create(YUNET_ONNX, "", (320, 320), 0.5, 0.3, 50) if fixed_box is None else None

    def detect(self, frame):
        best = None
        for sc in SCALES:
            g = cv2.resize(frame, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA) if sc != 1.0 else frame
            self.det.setInputSize((g.shape[1], g.shape[0]))
            _, d = self.det.detect(g)
            for f in ([] if d is None else d):
                v = f[:14] / sc
                if best is None or f[14] * v[3] > best[0]:
                    best = (f[14] * v[3], v)
            if best is not None and best[0] > 0:
                break                       # first scale with a face wins (landmarks are only comparable at one scale)
        return None if best is None else best[1]

    def __call__(self, frame, threshold=0.5):
        f_h, f_w = frame.shape[:2]
        if self.fixed_box is not None:
            box = self.fixed_box
            eye_l, eye_r, mouth = self.fixed_points
        else:
            v = self.detect(frame)
            if v is None:
                return None, None
            box = v[:4]
            a_, b_ = v[4:6], v[6:8]                           # YuNet order: right eye, left eye, nose, mouth R, mouth L
            eye_l, eye_r = (a_, b_) if a_[0] < b_[0] else (b_, a_)   # LatentSync "left" = image-left
            mouth = (v[10:12] + v[12:14]) / 2
        x, y, w, h = [float(t) for t in box]
        if w < 50 or h < 80 * 0.6:                            # LatentSync skips tiny faces (it uses 50 x 80 on InsightFace boxes)
            return None, None
        lmk = synth_106((x, y, w, h), eye_l, eye_r, mouth)
        x1, y1 = max(0, int(x)), max(0, int(y))
        x2, y2 = min(f_w, int(x + w)), min(f_h, int(y + h + 0.1 * w))
        return (x1, y1, x2, y2), np.round(lmk).astype(np.int_)


def aligned_crop(frame, lmk, resolution=256):
    """LatentSync's 3-point similarity alignment (AlignRestore, align_points=3), reproduced with OpenCV for previews."""
    ratio = resolution / 256 * 2.8
    tmpl = np.array([[17, 20], [58, 20], [37.5, 40]], np.float32) * ratio
    size = (int(75 * ratio), int(100 * ratio))
    p = np.array([lmk[[43, 48, 49, 51, 50]].mean(0), lmk[101:106].mean(0), lmk[[74, 77, 83, 86]].mean(0)], np.float32)
    M, _ = cv2.estimateAffinePartial2D(p, tmpl)
    face = cv2.warpAffine(frame, M, size, flags=cv2.INTER_LINEAR, borderValue=(127, 127, 127))
    return cv2.resize(face, (resolution, resolution), interpolation=cv2.INTER_LANCZOS4)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip"); ap.add_argument("--preview", required=True); ap.add_argument("--mask", help="LatentSync mask.png (optional overlay)")
    a = ap.parse_args()
    cap = cv2.VideoCapture(a.clip)
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    fd = FaceDetector("cpu")
    mask = cv2.imread(a.mask, 0) if a.mask else None
    tiles, miss = [], 0
    for i in np.linspace(0, len(frames) - 1, 6).astype(int):
        box, lmk = fd(frames[i])
        if box is None:
            miss += 1; tiles.append(np.full((256, 256, 3), 127, np.uint8)); continue
        c = aligned_crop(frames[i], lmk)
        if mask is not None:                 # black area of the mask = the region LatentSync regenerates (mouth)
            m = cv2.resize(mask, (256, 256)) < 128
            c[m] = (0.6 * c[m] + 0.4 * np.array([0, 0, 255])).astype(np.uint8)
        tiles.append(c)
    det = sum(fd(f)[0] is not None for f in frames)
    cv2.imwrite(a.preview, np.hstack(tiles))
    print(f"{a.clip}: face found on {det}/{len(frames)} frames; preview {a.preview}")
