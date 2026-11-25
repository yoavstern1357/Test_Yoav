"""Paper-cut animation toolkit (PIL + numpy + OpenCV): paper textures, cut-paper sprites with
white edges and drop shadows, easing, text, a supersampled drawing canvas and an ffmpeg writer.
Everything is procedural: no sampled art, no licensed assets."""
import math, os, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops, ImageOps

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)            # tools/episode_maker

PAL = dict(yellow=(236, 198, 106), cream=(255, 250, 240), orange=(217, 72, 15), peach=(255, 227, 184),
           brown=(59, 42, 26), skin=(250, 208, 178), sepia=(150, 104, 60), vermilion=(196, 44, 28),
           ink=(48, 36, 28), paper=(244, 228, 196), gold=(240, 176, 48), white=(255, 252, 244),
           sky=(150, 190, 200), wash=(120, 110, 96), bamboo=(214, 170, 96))

F_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
F_XBOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_SERIF = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"
F_HAND = "/usr/share/fonts/truetype/crosextra/Caladea-BoldItalic.ttf"
F_HAND2 = "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"
_fc = {}


def font(path, size):
    k = (path, int(size))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, int(size))
    return _fc[k]


# ------------------------------------------------------------------ easing
def c01(x):
    return min(max(x, 0.0), 1.0)


def smooth(x):
    x = c01(x)
    return x * x * (3 - 2 * x)


def out_cubic(x):
    x = c01(x)
    return 1 - (1 - x) ** 3


def in_cubic(x):
    return c01(x) ** 3


def out_back(x, c1=1.70158):
    x = c01(x)
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def out_bounce(x):
    x = c01(x)
    n1, d1 = 7.5625, 2.75
    if x < 1 / d1:
        return n1 * x * x
    if x < 2 / d1:
        x -= 1.5 / d1
        return n1 * x * x + 0.75
    if x < 2.5 / d1:
        x -= 2.25 / d1
        return n1 * x * x + 0.9375
    x -= 2.625 / d1
    return n1 * x * x + 0.984375


def lerp(a, b, t):
    return a + (b - a) * t


def seg(t, t0, t1):
    """0..1 progress of t inside [t0, t1]."""
    return c01((t - t0) / max(t1 - t0, 1e-6))


def step_t(t, fps):
    """Quantize time to a stepped (stop-motion) frame rate."""
    return math.floor(t * fps + 1e-6) / fps


def hrand(*a):
    """Deterministic pseudo-random in [0,1) from numbers (for per-step jitter)."""
    h = 2166136261
    for v in a:
        h = ((h ^ (int(v * 1000) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    h ^= h >> 13; h = (h * 1274126177) & 0xFFFFFFFF; h ^= h >> 16
    return (h & 0xFFFFFF) / float(0x1000000)


# ------------------------------------------------------------------ canvas
class Cv:
    """Supersampled RGBA drawing canvas; coordinates are in output pixels."""

    def __init__(self, w, h, ss=2, bg=(0, 0, 0, 0)):
        self.w, self.h, self.ss = int(w), int(h), ss
        self.im = Image.new("RGBA", (self.w * ss, self.h * ss), bg)
        self.d = ImageDraw.Draw(self.im)

    def _p(self, pts):
        return [(x * self.ss, y * self.ss) for x, y in pts]

    def _b(self, box):
        return [v * self.ss for v in box]

    def poly(self, pts, fill=None, outline=None, width=0):
        self.d.polygon(self._p(pts), fill=fill)
        if outline and width:
            self.line(list(pts) + [pts[0]], outline, width)

    def ell(self, box, fill=None, outline=None, width=0):
        self.d.ellipse(self._b(box), fill=fill, outline=outline, width=int(width * self.ss))

    def rrect(self, box, r, fill=None, outline=None, width=0):
        self.d.rounded_rectangle(self._b(box), radius=r * self.ss, fill=fill, outline=outline, width=int(width * self.ss))

    def line(self, pts, fill, width, round_caps=True):
        pp = self._p(pts)
        self.d.line(pp, fill=fill, width=max(1, int(width * self.ss)), joint="curve")
        if round_caps and width >= 3:
            r = width * self.ss / 2
            for q in (pp[0], pp[-1]):
                self.d.ellipse((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=fill)

    def arc(self, box, a0, a1, fill, width):
        self.d.arc(self._b(box), a0, a1, fill=fill, width=max(1, int(width * self.ss)))

    def text(self, xy, s, fnt, fill, anchor="la", stroke=0, stroke_fill=None):
        self.d.text((xy[0] * self.ss, xy[1] * self.ss), s, font=fnt, fill=fill, anchor=anchor,
                    stroke_width=int(stroke * self.ss), stroke_fill=stroke_fill)

    def out(self, scale=1):
        size = (int(self.w * scale), int(self.h * scale))
        return self.im.resize(size, Image.LANCZOS) if size != self.im.size else self.im


def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t * t; d = t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def catmull(pts, n=12):
    """Smooth curve through points (Catmull-Rom)."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(tuple(pts[-1]))
    return out


# ------------------------------------------------------------------ textures
_tex = {}


def noise_field(w, h, scale, seed, octaves=4):
    g = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = max(2, int(scale / (2 ** o)))
        small = g.standard_normal((h // s + 2, w // s + 2)).astype(np.float32)
        acc += cv2.resize(small, (w, h), interpolation=cv2.INTER_CUBIC) * amp
        tot += amp
        amp *= 0.55
    return acc / tot


def paper_tex(w, h, seed=1):
    """Greyscale multiplicative paper texture around 1.0 (fibres + mottling)."""
    k = ("tex", w, h, seed)
    if k not in _tex:
        n = noise_field(w, h, 160, seed, 5) * 0.045 + noise_field(w, h, 5, seed + 1, 2) * 0.03
        g = np.random.default_rng(seed + 7)
        fib = np.zeros((h, w), np.uint8)
        for _ in range(int(w * h / 9000)):
            x, y = g.integers(0, w), g.integers(0, h)
            a = g.uniform(0, math.pi); l = g.uniform(8, 40)
            cv2.line(fib, (x, y), (int(x + math.cos(a) * l), int(y + math.sin(a) * l)), int(g.integers(40, 110)), 1)
        fib = cv2.GaussianBlur(fib, (0, 0), 0.7).astype(np.float32) / 255.0
        _tex[k] = (1.0 + n - fib * 0.07).astype(np.float32)
    return _tex[k]


def paper_bg(w, h, color, seed=1, vignette=0.18):
    k = ("bg", w, h, tuple(color), seed, vignette)
    if k not in _tex:
        arr = np.ones((h, w, 3), np.float32) * np.array(color, np.float32)
        arr *= paper_tex(w, h, seed)[..., None]
        if vignette:
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            r = ((xx / w - 0.5) ** 2 + (yy / h - 0.5) ** 2) * 2
            arr *= (1 - vignette * np.clip(r, 0, 1) ** 1.2)[..., None]
        _tex[k] = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(_tex[k], "RGB")


def to_rgba(im):
    return im if im.mode == "RGBA" else im.convert("RGBA")


def tint(im, dark, light, mid=None, amt=1.0):
    """Colourise an RGBA sprite (keeps alpha) with a 2/3-stop gradient map (sepia legend filter)."""
    im = to_rgba(im)
    g = ImageOps.grayscale(im.convert("RGB"))
    c = ImageOps.colorize(g, dark, light, mid)
    if amt < 1:
        c = Image.blend(im.convert("RGB"), c, amt)
    out = c.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


SEPIA = dict(dark=(46, 30, 20), mid=(150, 104, 62), light=(250, 236, 204))


def sepia(im, amt=1.0):
    return tint(im, SEPIA["dark"], SEPIA["light"], SEPIA["mid"], amt)


def rough_edges(alpha, amt=1.6, seed=3):
    """Hand-cut feel: displace the alpha edge a little."""
    h, w = alpha.shape
    n1 = noise_field(w, h, 14, seed, 2) * amt
    n2 = noise_field(w, h, 14, seed + 5, 2) * amt
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return cv2.remap(alpha, xx + n1, yy + n2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


def finish(sp, edge=5, edge_col=(255, 249, 232), shadow=(7, 11, 12, 0.38), rough=1.2, tex=0.05, seed=3, pad=None):
    """Turn a flat RGBA drawing into a cut-paper sprite: rough cut edge, white paper rim, paper grain, soft drop shadow."""
    sp = to_rgba(sp)
    dx, dy, blur, sa = shadow
    p = pad if pad is not None else int(edge + blur * 3 + max(abs(dx), abs(dy)) + 4)
    big = Image.new("RGBA", (sp.width + 2 * p, sp.height + 2 * p), (0, 0, 0, 0))
    big.paste(sp, (p, p))
    a = np.asarray(big.getchannel("A"), np.float32) / 255.0
    if rough:
        a = rough_edges(a, rough, seed)
    rgb = np.asarray(big.convert("RGB"), np.float32)
    if edge > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (edge * 2 + 1, edge * 2 + 1))
        da = cv2.dilate((a > 0.5).astype(np.float32), k)
        da = cv2.GaussianBlur(da, (0, 0), 0.7)
        da = np.maximum(da, a)
        rim = np.clip(da - a, 0, 1)[..., None]
        rgb = rgb * a[..., None] / np.maximum(a[..., None], 1e-3) * 1.0
        rgb = np.where(a[..., None] > 0.5, rgb, np.array(edge_col, np.float32))
        body_a = da
    else:
        body_a = a
    if tex:
        t = paper_tex(rgb.shape[1], rgb.shape[0], seed + 11)
        rgb = rgb * (1 + (t - 1) * (tex / 0.05))[..., None]
    out = np.zeros(rgb.shape[:2] + (4,), np.float32)
    out[..., :3] = np.clip(rgb, 0, 255)
    out[..., 3] = body_a * 255
    res = Image.fromarray(out.astype(np.uint8), "RGBA")
    if sa > 0:
        sh = cv2.GaussianBlur(body_a, (0, 0), max(blur, 0.1))
        sh = np.roll(np.roll(sh, int(dy), axis=0), int(dx), axis=1)
        sl = np.zeros(rgb.shape[:2] + (4,), np.uint8)
        sl[..., 0], sl[..., 1], sl[..., 2] = 52, 36, 24
        sl[..., 3] = np.clip(sh * 255 * sa, 0, 255).astype(np.uint8)
        base = Image.fromarray(sl, "RGBA")
        base.alpha_composite(res)
        res = base
    return res


def blit(dst, sp, x, y, rot=0.0, scale=1.0, sx=None, sy=None, anchor=(0.5, 0.5), alpha=1.0, flip=False):
    """Draw sprite `sp` onto RGB image `dst`: anchor (fractions of sprite) placed at (x, y)."""
    if flip:
        sp = ImageOps.mirror(sp)
    sxx = (sx if sx is not None else scale)
    syy = (sy if sy is not None else scale)
    w0, h0 = sp.size
    nw, nh = max(1, int(w0 * sxx)), max(1, int(h0 * syy))
    if abs(sxx - 1) > 1e-3 or abs(syy - 1) > 1e-3:
        sp = sp.resize((nw, nh), Image.LANCZOS if (nw < w0 * 0.6) else (Image.BILINEAR if (nw < w0 or nh < h0) else Image.BICUBIC))
    ax, ay = anchor[0] * nw, anchor[1] * nh
    if abs(rot) > 0.01:
        pad = int(math.hypot(nw, nh)) + 2
        cv = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
        cv.paste(sp, (pad - int(ax), pad - int(ay)))
        cv = cv.rotate(rot, resample=Image.BICUBIC, center=(pad, pad))
        px, py = int(round(x - pad)), int(round(y - pad))
        sp = cv
    else:
        px, py = int(round(x - ax)), int(round(y - ay))
    if alpha < 1:
        sp = sp.copy()
        sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
    dst.paste(sp, (px, py), sp)


def shadow_ellipse(dst, cx, cy, w, h, a=0.28):
    m = Image.new("L", (int(w) + 60, int(h) + 60), 0)
    ImageDraw.Draw(m).ellipse((30, 30, 30 + w, 30 + h), fill=int(255 * a))
    m = m.filter(ImageFilter.GaussianBlur(h * 0.25 + 3))
    dst.paste(PAL["brown"], (int(cx - m.width / 2), int(cy - m.height / 2)), m)


def grade_frame(img, mul=(1, 1, 1), add=(0, 0, 0)):
    a = np.asarray(img, np.float32) * np.array(mul, np.float32) + np.array(add, np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def final_grain(img, strength=0.05, seed=5):
    """Multiply the whole frame by a paper-grain texture (cached)."""
    t = paper_tex(img.width, img.height, seed)
    a = np.asarray(img, np.float32) * (1 + (t - 1) * (strength / 0.05))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------ text
def text_sprite(s, fnt, fill, stroke=0, stroke_fill=None, pad=8, spacing=0):
    d = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    bb = d.textbbox((0, 0), s, font=fnt, stroke_width=stroke)
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), s, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im


def wrap(s, fnt, maxw):
    d = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ video out
class Writer:
    def __init__(self, path, fps=30, w=W, h=H, crf=14):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
                                   "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p", "-an",
                                   "-movflags", "+faststart", path], stdin=subprocess.PIPE)

    def write(self, img):
        self.p.stdin.write(img.convert("RGB").tobytes())

    def close(self):
        self.p.stdin.close(); self.p.wait()
