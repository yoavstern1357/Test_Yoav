#!/usr/bin/env python3
"""Grandma stall test (4 s): head turn, blink, talking mouth, hands pleating a dumpling, steam, lantern sway.
Grandma's art is a painted bust behind a cart, so she is animated as 3 layers (body, head, hands) + FX.

    python3 grandma_demo.py out/grandma-test.mp4
"""
import math, os, subprocess, shutil, sys
import numpy as np, cv2
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import street
from rig import smooth

W, H, FPS, DUR = 720, 1280, 24, 4.0
SRC = cv2.cvtColor(cv2.imread(os.path.join(HERE, "..", "specs", "puppets", "grandma.png"), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
SH, SW = SRC.shape[:2]
SKIN = np.array([236, 180, 134], np.float32)


def ell(shape, c, r):
    m = np.zeros(shape[:2], np.uint8); cv2.ellipse(m, c, r, 0, 0, 360, 255, -1); return m


def premult(img):
    f = img.astype(np.float32); a = f[..., 3:4] / 255
    return np.concatenate([f[..., :3] * a, f[..., 3:4]], -1)


# head layer: ellipse around the face + bun
head_m = cv2.GaussianBlur(ell(SRC.shape, (480, 215), (190, 235)), (0, 0), 1.5)
hands_m = cv2.GaussianBlur(ell(SRC.shape, (560, 545), (150, 70)), (0, 0), 6)
head = SRC.copy(); head[..., 3] = (SRC[..., 3] * (head_m / 255.0)).astype(np.uint8)
# clean face: erase mouth (masked blur refill) so we can redraw it
rgb = SRC[..., :3].copy()
mbox = (515, 238, 590, 292)
diff = np.abs(rgb.astype(np.float32) - SKIN).sum(-1)
mm = np.zeros(SRC.shape[:2], np.uint8); mm[mbox[1]:mbox[3], mbox[0]:mbox[2]] = (diff[mbox[1]:mbox[3], mbox[0]:mbox[2]] > 70)
mm = cv2.dilate(mm, np.ones((7, 7), np.uint8))
valid = ((diff < 45) & (mm == 0)).astype(np.float32)
num = cv2.GaussianBlur(rgb.astype(np.float32) * valid[..., None], (0, 0), 10); den = cv2.GaussianBlur(valid, (0, 0), 10)[..., None]
clean = np.where(mm[..., None] > 0, num / np.maximum(den, 1e-3), rgb).astype(np.uint8)
head[..., :3] = clean
body = SRC.copy()
hand = SRC.copy(); hand[..., 3] = (SRC[..., 3] * (hands_m / 255.0)).astype(np.uint8)
EYES = [(505, 185), (585, 185)]


def draw_face(turn, mouth, blink):
    im = Image.fromarray(head); L = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    if blink > 0.05:
        for (cx, cy) in EYES:
            k = min(1, blink)
            d.ellipse([cx - 26, cy - 24, cx + 26, cy - 24 + 48 * k], fill=tuple(int(v) for v in SKIN) + (255,))
            if k > 0.7: d.arc([cx - 22, cy - 6, cx + 22, cy + 14], 200, 340, fill=(80, 50, 40, 255), width=4)
    mx, my = 553, 262
    r = 6 + 12 * mouth
    d.ellipse([mx - 18, my - 16, mx + 18, my + 22], fill=tuple(int(v) for v in SKIN) + (255,))
    if mouth > 0.08:
        d.ellipse([mx - 11 - 6 * mouth, my - 8, mx + 11 + 6 * mouth, my - 8 + 8 + 28 * mouth], fill=(168, 70, 62, 255), outline=(80, 40, 30, 255), width=3)
    else:
        d.arc([mx - 14, my - 6, mx + 14, my + 8], 20, 160, fill=(120, 60, 50, 255), width=3)
    out = np.array(im).astype(np.float32); lay = np.array(L).astype(np.float32); a = lay[..., 3:4] / 255 * (out[..., 3:4] > 0)
    out[..., :3] = out[..., :3] * (1 - a) + lay[..., :3] * a
    out = out.astype(np.uint8)
    if abs(turn) > 1e-3:
        yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
        r2 = ((xx - 520) / 150) ** 2 + ((yy - 230) / 130) ** 2
        sx = turn * 36 * np.clip(1 - r2, 0, 1) ** 0.8
        pm = premult(out)
        o = cv2.remap(pm, (xx - sx).astype(np.float32), yy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        oa = o[..., 3:4] / 255
        out = np.clip(np.concatenate([np.where(oa > 1e-3, o[..., :3] / np.maximum(oa, 1e-3), 0), o[..., 3:4]], -1), 0, 255).astype(np.uint8)
    return out


def affine(src_pm, M, size):
    return cv2.warpAffine(src_pm, M[:2], size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


def T(x, y): return np.array([[1, 0, x], [0, 1, y], [0, 0, 1]], np.float64)
def Rm(deg, c):
    a = math.radians(deg); co, si = math.cos(a), math.sin(a)
    return T(c[0], c[1]) @ np.array([[co, -si, 0], [si, co, 0], [0, 0, 1]]) @ T(-c[0], -c[1])
def Sm(s, c): return T(c[0], c[1]) @ np.diag([s, s, 1.0]) @ T(-c[0], -c[1])


def blit(canvas, pm, M):
    w = affine(pm, M, (W, H)); a = w[..., 3:4] / 255
    canvas[:] = w + canvas * (1 - a)


def main(out):
    work = os.path.join(os.path.dirname(os.path.abspath(out)), "grandma_frames"); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    k = 0.62          # art -> screen scale (1080 wide -> ~670)
    base = T(20, H - SH * k - 30) @ np.diag([k, k, 1.0])
    pm_body, pm_hand = premult(body), premult(hand)
    # backdrop: the street, blurred and warmed
    bgs = {}
    for i in range(int(DUR * FPS)):
        t = i / FPS
        bg = np.array(street.render(t * 0.4 + 2.0, 6.0, 0.0)).astype(np.float32)
        bg = cv2.GaussianBlur(bg, (0, 0), 7) * np.array([1.0, 0.96, 0.9], np.float32)
        canvas = bg.copy()
        c4 = np.zeros((H, W, 4), np.float32)
        breathe = 1 + 0.006 * math.sin(t * 2.4)
        blit(c4, pm_body, base @ Sm(breathe, (480, 1100)))
        turn = np.interp(t, [0, 0.6, 1.6, 2.4, 3.2, 4], [0.0, 0.0, -0.8, -0.8, 0.25, 0.25])
        talk = 0.0
        if 1.7 < t < 3.0:
            talk = 0.5 + 0.5 * math.sin(t * 22) * (0.5 + 0.5 * math.sin(t * 5.3))
        blink = max(0.0, 1 - abs(t - 1.2) / 0.1, 1 - abs(t - 3.4) / 0.1)
        hb = 4 * math.sin(t * 2.4)
        hd = premult(draw_face(turn, talk, blink))
        blit(c4, hd, base @ T(0, hb * 0.5) @ Rm(2.0 * math.sin(t * 1.3) + 5 * turn * 0.3, (480, 400)) @ Sm(breathe, (480, 1100)))
        # hands: pleat motion (small circle + squeeze)
        ph = t * 6.0
        blit(c4, pm_hand, base @ T(10 * math.cos(ph), 8 * math.sin(ph)) @ Rm(3 * math.sin(ph), (560, 545)) @ Sm(1 + 0.02 * math.sin(2 * ph), (560, 545)))
        out_f = canvas * (1 - c4[..., 3:4] / 255) + c4[..., :3]
        # steam from the steamer (right)
        ov = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for j in range(9):
            u = ((t * 0.5 + j / 9) % 1)
            x = 560 + 40 * math.sin(u * 6 + j) + j * 6; y = 760 - 330 * u
            r = 20 + 46 * u
            d.ellipse([(x - r) * 2, (y - r) * 2, (x + r) * 2, (y + r) * 2], fill=(255, 255, 252, int(120 * math.sin(math.pi * u))))
        a = np.array(ov.resize((W, H), Image.LANCZOS)).astype(np.float32); al = a[..., 3:4] / 255
        pmv = cv2.GaussianBlur(a[..., :3] * al, (0, 0), 6); alb = cv2.GaussianBlur(al[..., 0], (0, 0), 6)[..., None]
        out_f = out_f * (1 - alb) + pmv
        cv2.imwrite(os.path.join(work, f"f{i:05d}.png"), cv2.cvtColor(np.clip(out_f, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(work, "f%05d.png"), "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", out])
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../out/grandma-test.mp4")
