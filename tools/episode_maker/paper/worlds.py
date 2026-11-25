"""Painted paper backgrounds: ink-wash Silk Road map, dawn storybook village, desk, skyline."""
import math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from .core import *
from .shapes import cached

K = 2   # background supersample for camera push-ins


def _wash(layer_rgba, blur=2.0):
    return layer_rgba.filter(ImageFilter.GaussianBlur(blur))


def _ridge(seed, x0, x1, ybase, amp, n=14, rough=0.5):
    g = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, n)
    n = n * 2
    xs = np.linspace(x0, x1, n)
    ys = ybase - amp * (0.12 + 0.88 * g.random(n) ** 1.6) * (0.55 + 0.45 * np.sin(np.linspace(0, 6.0, n) + g.random() * 3))
    return catmull(list(zip(xs, ys)), 4)


def map_world():
    def build():
        Wd, Hd = W, H
        base = paper_bg(Wd * K, Hd * K, (238, 214, 160), seed=21, vignette=0.0)
        arr = np.asarray(base, np.float32)
        # mottled warm stains + burnt edges
        st = noise_field(Wd * K, Hd * K, 420, 5, 3)
        arr *= (1 + 0.06 * st)[..., None] * np.array([1.0, 0.97, 0.9])[None, None, :] ** (np.clip(st, 0, 1)[..., None] * 1.5)
        yy, xx = np.mgrid[0:Hd * K, 0:Wd * K].astype(np.float32)
        ed = np.minimum(np.minimum(xx, Wd * K - xx), np.minimum(yy, Hd * K - yy)) / (Wd * K * 0.5)
        arr *= (0.62 + 0.38 * np.clip(ed * 7.5, 0, 1) ** 0.6)[..., None] * np.array([1.0, 0.94, 0.86])
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        ink = (92, 74, 58)
        lay = Cv(Wd, Hd, ss=2)
        # --- mountains (3 ink-wash layers)
        for i, (yb, amp, col, a) in enumerate(((330, 210, (120, 108, 96), 110), (420, 170, (96, 84, 72), 150), (470, 120, (70, 60, 52), 190))):
            top = _ridge(11 + i * 7, -20, 1100, yb, amp, 14)
            poly = top + [(1100, yb + 170), (-20, yb + 170)]
            m = Image.new("L", (Wd * K, Hd * K), 0)
            ImageDraw.Draw(m).polygon([(x * K, y * K) for x, y in poly], fill=a)
            m = m.filter(ImageFilter.GaussianBlur((3 + i) * K))
            # fade toward bottom of range
            ramp = np.clip(1.0 - (np.mgrid[0:Hd * K, 0:Wd * K][0] / K - (yb - amp)) / (amp + 190), 0, 1) ** 0.8
            m = Image.fromarray((np.asarray(m, np.float32) * ramp).astype(np.uint8))
            img.paste(col, (0, 0), m)
            ImageDraw.Draw(img).line([(x * K, y * K) for x, y in top], fill=(64, 52, 44), width=int(2.2 * K), joint="curve")
        # mist bands
        mist = Image.new("L", (Wd * K, Hd * K), 0)
        md = ImageDraw.Draw(mist)
        for yb in (520, 700):
            md.ellipse((-200 * K, (yb - 40) * K, 1300 * K, (yb + 40) * K), fill=160)
        img.paste((250, 238, 206), (0, 0), mist.filter(ImageFilter.GaussianBlur(26 * K)))
        # --- dunes
        dn = Cv(Wd, Hd, ss=2)
        for j, (yb, col) in enumerate(((760, (222, 184, 112, 255)), (900, (214, 170, 98, 255)), (1040, (206, 158, 86, 255)), (1180, (198, 148, 78, 255)))):
            top = catmull([(-20, yb + 60), (240, yb - 70 + j * 12), (520, yb + 10), (790, yb - 60 - j * 10), (1100, yb + 30)], 10)
            dn.poly(top + [(1100, yb + 400), (-20, yb + 400)], col)
            dn.line(top, (170, 120, 62, 255), 3)
        dl = dn.out(2)
        fade = np.clip((1380 - np.mgrid[0:Hd * K, 0:Wd * K][0] / K) / 170.0, 0, 1)
        dal = np.asarray(_wash(dl.getchannel("A"), 1.4), np.float32) * 0.78 * fade
        img.paste(dl.convert("RGB"), (0, 0), Image.fromarray(dal.astype(np.uint8)))
        # green-grey coastal hills on the lowland
        hl = Cv(Wd, Hd, ss=2)
        for j, (yb, col) in enumerate(((1440, (150, 160, 118, 230)), (1560, (128, 142, 104, 230)), (1700, (110, 126, 92, 230)))):
            top = catmull([(-20, yb + 40), (200, yb - 50), (420, yb + 20), (640, yb - 40), (860, yb + 10), (1100, yb - 30)], 8)
            hl.poly(top + [(1100, yb + 360), (-20, yb + 360)], col)
            hl.line(top, (74, 88, 62, 255), 3)
        hll = hl.out(2)
        img.paste(hll.convert("RGB"), (0, 0), _wash(hll.getchannel("A"), 1.4).point(lambda v: int(v * 0.6)))
        # dune ripples
        g = np.random.default_rng(3)
        d = ImageDraw.Draw(img, "RGBA")
        for _ in range(70):
            x, y = g.uniform(40, 1040), g.uniform(780, 1280)
            if y > 1250 and x < 300: continue
            w = g.uniform(30, 90)
            pts = catmull([(x, y), (x + w * 0.5, y - 6), (x + w, y)], 6)
            d.line([(a * K, b * K) for a, b in pts], fill=(150, 102, 56, 110), width=2 * K)
        # --- sea (bottom right), washed teal-grey
        sea = [(1080, 1330), (940, 1360), (820, 1450), (700, 1500), (640, 1600), (560, 1700), (520, 1800), (470, 1920), (1080, 1920)]
        lay.poly(catmull(sea[:-2], 8) + [(1080, 1920), (1080, 1330)], (150, 176, 172, 190))
        lay2 = lay.out(2)
        img.paste(lay2.convert("RGB"), (0, 0), _wash(lay2.getchannel("A"), 6).point(lambda v: int(v * 0.9)))
        d = ImageDraw.Draw(img, "RGBA")
        # river from the dunes to the sea
        riv = catmull([(120, 1250), (240, 1330), (230, 1450), (360, 1560), (480, 1620), (610, 1640)], 10)
        rv = Image.new("L", (Wd * K, Hd * K), 0)
        ImageDraw.Draw(rv).line([(x * K, y * K) for x, y in riv], fill=150, width=34 * K, joint="curve")
        rv = rv.filter(ImageFilter.GaussianBlur(5 * K))
        img.paste((140, 170, 168), (0, 0), rv)
        # --- pines near mountains, tiny pagodas, tufts
        for _ in range(26):
            x, y = g.uniform(60, 1020), g.uniform(560, 640)
            h = g.uniform(26, 48)
            d.polygon([((x) * K, (y - h) * K), ((x - h * .3) * K, y * K), ((x + h * .3) * K, y * K)], fill=(66, 70, 56, 210))
        # --- coast hills + harbor mark
        sh = [(560, 1700), (640, 1600), (700, 1500), (820, 1450), (940, 1360), (1080, 1330)]
        d.line([(x * K, y * K) for x, y in catmull(sh, 8)], fill=(80, 96, 94, 200), width=3 * K, joint="curve")
        for i in range(34):                       # shore ripples
            x, y = g.uniform(640, 1060), g.uniform(1420, 1900)
            if y < 1350 + (1080 - x) * 0.3 or x < 560 + (1920 - y) * -0.1: continue
            d.arc((x * K, y * K, (x + 52) * K, (y + 16) * K), 190, 350, fill=(255, 255, 255, 150), width=2 * K)
        return img
    return cached("mapworld", build)


def desk_bg():
    def build():
        base = paper_bg(W, H, (74, 50, 32), seed=33, vignette=0.45)
        a = np.asarray(base, np.float32)
        g = np.random.default_rng(4)
        for _ in range(140):
            y = int(g.integers(0, H)); x = int(g.integers(0, W)); l = int(g.integers(200, 900))
            cv2.line(a, (x, y), (min(W, x + l), y + int(g.integers(-6, 6))), (g.uniform(-14, 14),) * 3, int(g.integers(1, 3)))
        for x in range(0, W, 270):
            cv2.line(a, (x, 0), (x, H), (-40, -40, -40), 5)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return cached("desk", build)


def dawn_world(t=0.0, w=W, h=H):
    """Legend storybook backdrop (sepia/vermilion): layered paper hills, pagodas, rising sun. Returns RGB for time t (sun rises)."""
    rise = 1.0
    return None


def pagoda(h=420, tiers=4, col=(112, 78, 54, 255), flat=True):
    """Stout paper pagoda silhouette."""
    def build():
        w = int(h * .62)
        c = Cv(w, h, ss=2)
        th = h * .8 / tiers
        for i in range(tiers):
            y1 = h - 6 - i * th
            ww = w * (0.92 - i * (0.55 / tiers))
            cx = w / 2
            c.rrect((cx - ww * .36, y1 - th * .72, cx + ww * .36, y1), 4, col)
            c.poly([(cx - ww * .6, y1 - th * .72), (cx + ww * .6, y1 - th * .72), (cx + ww * .42, y1 - th * .95), (cx - ww * .42, y1 - th * .95)], tuple(int(v * .8) for v in col[:3]) + (255,))
            c.poly([(cx - ww * .6, y1 - th * .72), (cx - ww * .72, y1 - th * .62), (cx - ww * .5, y1 - th * .7)], col)
            c.poly([(cx + ww * .6, y1 - th * .72), (cx + ww * .72, y1 - th * .62), (cx + ww * .5, y1 - th * .7)], col)
            c.ell((cx - ww * .07, y1 - th * .5, cx + ww * .07, y1 - th * .25), (232, 190, 112, 255))
        c.line([(w / 2, h - tiers * th - 4), (w / 2, h - tiers * th - h * .15)], col[:3] + (255,), 5)
        return c.out()
    return cached(("pagoda", h, tiers, col), build)


def skyline():
    def build():
        c = Cv(W, 900, ss=2)
        g = np.random.default_rng(8)
        x = -10
        cols = [(86, 66, 58, 255), (116, 86, 70, 255), (148, 110, 84, 255)]
        layer = 0
        for layer, (n, hmin, hmax, col) in enumerate(((10, 260, 520, cols[2]), (9, 340, 640, cols[1]), (8, 300, 560, cols[0]))):
            x = -20 + layer * 30
            while x < W:
                ww = g.uniform(70, 150); hh = g.uniform(hmin, hmax)
                c.rrect((x, 900 - hh, x + ww, 910), 6, col)
                for r in range(int(hh // 46)):
                    for k in range(int(ww // 34)):
                        if g.random() < .5:
                            c.rrect((x + 10 + k * 34, 900 - hh + 20 + r * 46, x + 28 + k * 34, 900 - hh + 36 + r * 46), 3, (255, 224, 150, 220))
                x += ww + g.uniform(-10, 18)
        # pearl-style tower with two spheres, as a paper silhouette
        tx = 650
        c.poly([(tx - 18, 910), (tx + 18, 910), (tx + 6, 300), (tx - 6, 300)], (72, 52, 46, 255))
        c.ell((tx - 70, 520, tx + 70, 660), (92, 64, 56, 255)); c.ell((tx - 44, 330, tx + 44, 418), (92, 64, 56, 255))
        c.line([(tx, 330), (tx, 190)], (72, 52, 46, 255), 8)
        return c.out()
    return cached("skyline", build)
