"""CODE clips of Episode 1 v4.3 and the series intro (soft watercolor look, village costumes). Built on clips.py / clips2.py.
Names follow the script (scripts/episode-01-v4.3.md): C03 journal + map, C04 Qinglong port, C06 title plate, C19 stall -> scroll,
C20 dawn shop (scroll world), C21 shrinking bun + jelly, C22 famous small bun + scroll closes, C27I route south, C90 intro title.
Render: python3 -m paper.render3 [C03 ...] [--both]  ->  out/ep01v43/code/Cxx[_land].mp4"""
import math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from .core import *
from .shapes import *
from .worlds import *
from . import clips as c1
from . import clips2 as c2
from .clips import Clip, View, LW, LH, land_compose

FRAMES = os.path.join(ROOT, "specs", "frames", "ep01v43")
EARTH = (150, 108, 66, 255)


# ------------------------------------------------------------------ helpers
def still(name, land=False, size=None):
    """AI still (frames/ep01v43/<name>[_land].png) cover-fitted to the screen, or None when it does not exist (yet)."""
    key = ("still", name, land, size)

    def build():
        for n in ([name + "_land", name] if land else [name]):
            p = os.path.join(FRAMES, n + ".png")
            if os.path.exists(p):
                im = Image.open(p).convert("RGB")
                tw, th = size or ((LW, LH) if land else (W, H))
                s = max(tw / im.width, th / im.height)
                im = im.resize((int(im.width * s + .5), int(im.height * s + .5)), Image.LANCZOS)
                x0, y0 = (im.width - tw) // 2, (im.height - th) // 2
                return im.crop((x0, y0, x0 + tw, y0 + th))
        return None
    return cached(key, build)


def fallback_plate(w, h, col=(236, 206, 160)):
    return paper_bg(w, h, col, seed=7, vignette=.25).copy()


def push(im, zoom, focus=(0.5, 0.5)):
    """Crop-zoom a PIL image about a focus point, keep the size."""
    w, h = im.size
    cw, ch = w / zoom, h / zoom
    x0 = min(max(focus[0] * w - cw / 2, 0), w - cw)
    y0 = min(max(focus[1] * h - ch / 2, 0), h - ch)
    return im.resize((w, h), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


def roller(length, thick=56):
    """A rolled paper edge (cylinder shading), horizontal, as RGBA."""
    im = Image.new("RGBA", (length, thick), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(thick):
        a = k / (thick - 1)
        s = 0.35 + 0.65 * math.sin(a * math.pi) ** 0.8
        d.line((0, k, length, k), fill=(int(236 * s + 20), int(214 * s + 16), int(168 * s + 10), 255))
    d.rectangle((0, 0, 8, thick), fill=(120, 70, 40, 255)); d.rectangle((length - 8, 0, length, thick), fill=(120, 70, 40, 255))
    return im


def scroll_open(base, world, q, vertical=True):
    """`world` visible in a band that grows from the center (q 0..1) over `base`; two paper rollers mark the band's edges."""
    w, h = base.size
    out = base.copy()
    if q <= 0.001:
        return out
    if vertical:
        half = int(q * h / 2)
        box = (0, h // 2 - half, w, h // 2 + half)
        out.paste(world.crop(box), box[:2])
        for y in (box[1], box[3]):
            if q < 0.995:
                r = cached(("roll", w, 56), lambda: roller(w, 56))
                out.paste(r, (0, y - 28), r)
                sh = Image.new("RGBA", (w, 40), (0, 0, 0, 0))
                ImageDraw.Draw(sh).rectangle((0, 0, w, 40), fill=(40, 24, 14, 70))
    else:
        half = int(q * w / 2)
        box = (w // 2 - half, 0, w // 2 + half, h)
        out.paste(world.crop(box), box[:2])
        for x in (box[0], box[2]):
            if q < 0.995:
                r = cached(("rollv", h, 56), lambda: roller(h, 56).rotate(90, expand=True))
                out.paste(r, (x - 28, 0), r)
    return out


# ------------------------------------------------------------------ C03: Dad's journal opens, the map unrolls, a tiny caravan walks the route
class C03(c1.C03):
    name, dur, step = "C03", 5.5, 8
    K = 4.5 / 5.5
    land_t = 0.0

    @property
    def land_zoom(self):
        return 1.0 if self.land_t < 1.3 else 1.7

    def land_focus(self, t):
        return 0.30 if t > 3.4 else 0.2

    def frame(self, t, ts):
        tt = t * self.K
        tts = tt if tt < self.smooth_until else step_t(tt, 8)
        orig = c1.draw_camel

        def no_rider(*a, **k):
            k["rider"] = None; k["zz"] = False
            return orig(*a, **k)
        c1.draw_camel = no_rider
        try:
            return super().frame(tt, tts)
        finally:
            c1.draw_camel = orig

    def tstep(self, t):
        return t if t * self.K < self.smooth_until else step_t(t, 8)


# ------------------------------------------------------------------ C04: Qinglong port, ships slide off the map
class C04(c1.C04):
    name, dur, step = "C04", 7.0, 8
    K = 4.5 / 7.0
    land_zoom = 1.7

    def land_focus(self, t):
        return 0.78

    def frame(self, t, ts):
        orig = c1.tag_sprite
        c1.tag_sprite = lambda *a, **k: Image.new("RGBA", (6, 6), (0, 0, 0, 0))   # the fact card carries the name (minimal on-screen text)
        try:
            tt = t * self.K
            return super().frame(tt, step_t(tt, 8))
        finally:
            c1.tag_sprite = orig


# ------------------------------------------------------------------ ink lettering
def ink_text(text, size, fill=(59, 42, 26), glow=(255, 244, 222), font_path=None, seed=1, tracking=0):
    """Brush-like lettering: heavy serif, roughened (displaced) edges, soft cream glow. Returns RGBA."""
    f = font(font_path or F_SERIF_I, size)
    tmp = Image.new("L", (10, 10))
    dr = ImageDraw.Draw(tmp)
    wtxt = int(dr.textlength(text, font=f)) + tracking * len(text)
    pad = int(size * .35)
    m = Image.new("L", (wtxt + 2 * pad, int(size * 1.5) + 2 * pad), 0)
    d = ImageDraw.Draw(m)
    x = pad
    for ch in text:
        d.text((x, pad), ch, font=f, fill=255, stroke_width=max(1, size // 40), stroke_fill=255)
        x += d.textlength(ch, font=f) + tracking
    a = np.asarray(m, np.float32)
    rng = np.random.default_rng(seed)
    nx = cv2.GaussianBlur(rng.standard_normal(a.shape).astype(np.float32), (0, 0), 3) * size * .07
    ny = cv2.GaussianBlur(rng.standard_normal(a.shape).astype(np.float32), (0, 0), 3) * size * .07
    gx, gy = np.meshgrid(np.arange(a.shape[1], dtype=np.float32), np.arange(a.shape[0], dtype=np.float32))
    a = cv2.remap(a, gx + nx, gy + ny, cv2.INTER_LINEAR)
    a = cv2.GaussianBlur(a, (0, 0), size * .012)
    a = np.clip((a - 110) * 2.2, 0, 255)
    mask = Image.fromarray(a.astype(np.uint8))
    out = Image.new("RGBA", m.size, fill + (0,))
    out.putalpha(mask)
    gl = Image.new("RGBA", m.size, glow + (0,))
    gl.putalpha(mask.filter(ImageFilter.GaussianBlur(size * .09)).point(lambda v: int(min(255, v * 1.3))))
    base = Image.new("RGBA", m.size, (0, 0, 0, 0))
    base.alpha_composite(gl)
    base.alpha_composite(out)
    return base


def bloom(fr, sp, cx, cy, q, steam=True, seed=1):
    """Letters bloom in from soft ink / steam: blur and scale shrink to the sharp text while alpha rises."""
    if q <= 0:
        return
    e = out_cubic(q)
    s = lerp(1.18, 1.0, e)
    blur = (1 - e) * 26
    a = sp.copy()
    if blur > 0.5:
        a = a.filter(ImageFilter.GaussianBlur(blur))
    al = a.getchannel("A").point(lambda v: int(v * min(1.0, q * 1.6)))
    a.putalpha(al)
    a = a.resize((int(a.width * s), int(a.height * s)), Image.LANCZOS)
    fr.paste(a, (int(cx - a.width / 2), int(cy - a.height / 2)), a)


def mist(fr, t, strength=0.5, seed=3):
    """Slow drifting soft mist across the whole frame (cheap: heavily blurred low-contrast noise)."""
    w, h = fr.size
    k = 8
    rng = np.random.default_rng(seed)
    n = cv2.GaussianBlur(rng.random((h // k, w // k)).astype(np.float32), (0, 0), 9)
    n = (n - n.min()) / (n.max() - n.min() + 1e-6)
    n = np.roll(n, int(t * 3) % (w // k), axis=1)
    al = Image.fromarray((np.clip(0.35 + 0.65 * n, 0, 1) * 255 * strength).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    fr.paste(Image.new("RGB", (w, h), (255, 246, 232)), (0, 0), al)


# ------------------------------------------------------------------ C06: title plate (canal at dawn): "#01 XIAOLONGBAO", then the place
class Native(Clip):
    """Clip drawn natively at 1080x1920 and 1920x1080 by `draw(t, land)`; frame_land returns the native wide frame."""
    def frame(self, t, ts):
        return self.draw(t, False)

    def frame_land(self, t, ts):
        return self.draw(t, True)


class C06(Native):
    name, dur, step = "C06", 2.5, None

    def draw(self, t, land):
        w, h = (LW, LH) if land else (W, H)
        bg = still("C06_plate", land)
        fr = bg.copy() if bg else fallback_plate(w, h, (240, 214, 176))
        fr = push(fr, 1.0 + 0.04 * t / self.dur, (0.5, 0.55))
        mist(fr, t, 0.22)
        u = min(w, h)
        s1 = cached(("t06a", u), lambda: ink_text("#01  XIAOLONGBAO", int(u * (0.085 if not land else 0.12)), seed=2))
        s2 = cached(("t06b", u), lambda: ink_text("NANXIANG · SHANGHAI, CHINA", int(u * (0.044 if not land else 0.06)), font_path=F_SERIF, seed=3))
        cy1 = h * (0.30 if not land else 0.36)
        # keep the first line inside the frame width
        if s1.width > w * 0.92:
            s1 = s1.resize((int(w * .92), int(s1.height * w * .92 / s1.width)), Image.LANCZOS)
        if s2.width > w * 0.92:
            s2 = s2.resize((int(w * .92), int(s2.height * w * .92 / s2.width)), Image.LANCZOS)
        bloom(fr, s1, w / 2, cy1, seg(t, 0.15, 0.85))
        bloom(fr, s2, w / 2, cy1 + u * 0.11, seg(t, 1.1, 1.7))
        return final_grain(fr, 0.03)


# ------------------------------------------------------------------ C90: series title "THE DUMPLING BOY" blooming out of steam (intro, 1.5 s)
class C90(Native):
    name, dur, step = "C90", 1.5, None

    def draw(self, t, land):
        w, h = (LW, LH) if land else (W, H)
        y = np.linspace(0, 1, h)[:, None, None]
        top, bot = np.array((255, 236, 200), np.float32), np.array((246, 190, 120), np.float32)
        base = (top * (1 - y) + bot * y) * np.ones((1, w, 1), np.float32)
        xx = np.linspace(-1, 1, w)[None, :, None]
        base *= (1 - 0.18 * (xx ** 2 + (2 * y - 1) ** 2) * 0.5)
        fr = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
        u = min(w, h)
        if land:
            parts = [("THE", .10, -0.19), ("DUMPLING BOY", .22, 0.0)]
        else:
            parts = [("THE", .075, -0.12), ("DUMPLING", .165, -0.02), ("BOY", .21, 0.12)]
        for i, (txt, k, dy) in enumerate(parts):
            sp = cached(("c90", txt, u, land), lambda txt=txt, k=k: ink_text(txt, int(u * k), fill=(217, 72, 15), glow=(255, 250, 238), seed=5 + i, tracking=int(u * .012)))
            if sp.width > w * .94:
                sp = sp.resize((int(w * .94), int(sp.height * w * .94 / sp.width)), Image.LANCZOS)
            bloom(fr, sp, w / 2, h * (0.5 + dy), seg(t, 0.1 + 0.12 * i, 0.75 + 0.12 * i))
        # steam: soft rising puffs that thin out as the letters appear
        k = 1 - smooth(seg(t, 0.15, 1.0))
        if k > 0.02:
            mist(fr, t * 6, 0.95 * k, seed=11)
            ov = Image.new("RGBA", fr.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            for j in range(9):
                px = w * (0.1 + 0.8 * hrand(j, 1)) + math.sin(t * 3 + j) * 30
                py = h * (1.1 - ((t * .9 + hrand(j, 2)) % 1.0) * 1.4)
                r = u * (0.12 + 0.12 * hrand(j, 3))
                d.ellipse((px - r, py - r, px + r, py + r), fill=(255, 250, 240, int(150 * k)))
            ov = ov.filter(ImageFilter.GaussianBlur(u * .05))
            fr.paste(ov, (0, 0), ov)
        # little sparkle at the end
        if t > 1.0:
            d = ImageDraw.Draw(fr, "RGBA")
            for j in range(5):
                a = hrand(j, 9) * 6.28
                r = u * (0.30 + 0.12 * hrand(j, 8))
                x, yy = w / 2 + math.cos(a) * r * (1.3 if land else 1.0), h / 2 + math.sin(a) * r * .8
                sz = u * 0.012 * (1 + math.sin((t - 1.0) * 14 + j)) + 2
                d.ellipse((x - sz, yy - sz, x + sz, yy + sz), fill=(255, 255, 255, 230))
        return final_grain(fr, 0.03)


# ------------------------------------------------------------------ scroll world (C19-C22)
def _owner_costume():
    orig = c2.uncle_doll

    def doll(*a, **k):
        k["kimono"] = EARTH
        k["belt"] = PAL["orange"] + (255,)
        return orig(*a, **k)
    return orig, doll


def world_frame(ts_world):
    """Dawn paper-cut shop (the old C18 world, 8 fps)."""
    return c2.C18().world(ts_world, step_t(ts_world, 8))


def stall_base(land, t, zoom0, zoom1, dur, name="C09"):
    im = still(name, land)
    if im is None:
        im = fallback_plate(LW if land else W, LH if land else H, (214, 170, 120))
    return push(im, lerp(zoom0, zoom1, smooth(t / dur)), (0.5, 0.45))


class C19(Native):
    """The Boy turns to Grandma (the stall), then a paper scroll unrolls across the screen into the scroll world."""
    name, dur, step = "C19", 3.0, None

    def draw(self, t, land):
        base = stall_base(land, t, 1.0, 1.12, self.dur)
        ts = step_t(t, 8)
        q = smooth(seg(t, 1.0, 2.2))
        if q <= 0:
            return base
        wf = world_frame(0.2 + max(0, t - 1.0) * 1.0)
        world = land_compose(wf, 1.0, 0.7) if land else wf
        out = scroll_open(base, world, q, vertical=not land)
        return final_grain(out, 0.03)


class C20(Native):
    """Legend, part 1: dawn, the shop, ONE giant bun, a customer shrugs (6 s)."""
    name, dur, step = "C20", 6.0, None

    def draw(self, t, land):
        wf = world_frame(2.0 + t * (4.0 / 6.0) + 0.0)
        return land_compose(wf, 1.0, 0.72) if land else wf


class C21(Native):
    """Legend, part 2: the owner raises the rolling pin, the bun shrinks, jelly glows inside, steam curls into a paper dragon (5 s)."""
    name, dur, step = "C21", 5.0, None

    def draw(self, t, land):
        tt = t * 1.2
        ts = step_t(tt, 8)
        orig, doll = _owner_costume()
        c2.uncle_doll = doll
        try:
            c = c2.C19()
            fr = c.hero(ts) if ts < 3.0 else c.jelly(ts - 3.0)
        finally:
            c2.uncle_doll = orig
        return land_compose(fr, 1.0, 0.72) if land else fr


class C22(Native):
    """Legend, part 3: the small bun on a plate, a paper crowd gathers, the scroll rolls closed onto the stall (3 s)."""
    name, dur, step = "C22", 3.0, None

    def scene(self, t):
        ts = step_t(t + 20.0, 8)
        view = View(540, 1330, 1.0)
        fr = c2.shop_scene(ts, view, sun_y=700)
        sp = cached(("smallbun",), lambda: finish(bun_hero(220, arms=False), edge=4, shadow=(6, 8, 8, .3)))
        a, b = view.pt(660, 1585)
        blit(fr, sp, a, b - (int(ts * 8) % 2) * 3, anchor=(.5, 1.0))
        # crowd walks in from both sides, hopping
        for i in range(6):
            side = -1 if i % 2 == 0 else 1
            q = out_cubic(seg(t, 0.1 + i * 0.12, 1.5 + i * 0.1))
            x = lerp(-160 if side < 0 else 1240, 150 + 180 * (i // 2) if side < 0 else 930 - 170 * (i // 2), q)
            hop = abs(math.sin(ts * 9 + i)) * 12 * (1 - q)
            cu = cached(("crowd", i % 3), lambda i=i: finish(sepia(customer(230 + 20 * (i % 3), 0.0, i % 2), .5), edge=4, shadow=(6, 8, 8, .3)))
            blit(fr, cu, x, 1770 - hop - (i // 2) * 20, anchor=(.5, 1.0), flip=side > 0)
        c2.draw_petals(fr, view, ts + 6)
        return final_grain(fr, 0.04)

    def draw(self, t, land):
        fr = self.scene(t)
        world = land_compose(fr, 1.0, 0.72) if land else fr
        close = smooth(seg(t, 1.6, 2.9))
        if close <= 0:
            return world
        base = stall_base(land, 0.0, 1.0, 1.0, 1.0, name="C23")
        return scroll_open(base, world, 1.0 - close, vertical=not land)


class C27I(c2.C27I):
    name, dur, step = "C27I", 1.6, 12

    def frame(self, t, ts):
        return super().frame(t * 1.1 / 1.6, step_t(t * 1.1 / 1.6, 12))
