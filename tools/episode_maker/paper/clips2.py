"""CODE clips part 2: journal insert, title slam, the paper-cut legend, fun-fact card, handwriting glow."""
import math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from .core import *
from .shapes import *
from .worlds import *
from .clips import Clip, View, final_grain, journal_open_sprite

BOY_PNG = os.path.join(ROOT, "specs", "puppets", "boy.png")


def fx_sprite(key, fn):
    return cached(key, fn)


def dust(fr, t, n=26, seed=1, alpha=150):
    d = ImageDraw.Draw(fr, "RGBA")
    g = np.random.default_rng(seed)
    for i in range(n):
        x0, y0, z = g.uniform(0, W), g.uniform(0, H), g.uniform(0.4, 1)
        x = (x0 + 14 * z * t + 20 * math.sin(t * .6 + i)) % W
        y = (y0 - 22 * z * t) % H
        r = 3 + 5 * z
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 244, 214, int(alpha * (0.5 + 0.5 * math.sin(t * 2 + i)) * z)))


# ------------------------------------------------------------------ handwriting
def hand_line(text, size=118, ink=(58, 40, 30), seed=0, font_path=F_HAND2):
    """Handwriting line as per-character RGBA sprites with jitter: [(sprite, x, y, rot)] and total width."""
    f = font(font_path, size)
    d = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    x, out = 0, []
    g = np.random.default_rng(seed)
    for ch in text:
        wch = d.textlength(ch, font=f)
        if ch != " ":
            sp = text_sprite(ch, f, ink + (255,), 0, None, pad=10)
            out.append((sp, x, g.uniform(-5, 5), g.uniform(-3, 3)))
        x += wch
    return out, x


def draw_hand_line(fr, chars, width, x0, y0, reveal=1.0, lift=None):
    """reveal 0..1 left to right. lift(q) callback per char? (handled by caller)."""
    for sp, x, dy, rot in chars:
        if x / max(width, 1) > reveal:
            continue
        blit(fr, sp, x0 + x, y0 + dy, rot=rot, anchor=(0, 0.5))


# ------------------------------------------------------------------ C06: journal insert
def aged_page(w, h, seed=3, torn=False):
    def build():
        c = Cv(w, h, ss=1)
        im = paper_bg(w, h, (246, 232, 196), seed=seed, vignette=0.0).convert("RGBA")
        a = np.asarray(im, np.float32)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        ed = np.minimum(np.minimum(xx, w - xx), np.minimum(yy, h - yy)) / (w * 0.14)
        a[..., :3] *= (0.78 + 0.22 * np.clip(ed, 0, 1) ** 0.7)[..., None] * np.array([1, .96, .9])
        # ruled faint lines
        for y in range(260, h - 80, 96):
            cv2.line(a, (90, y), (w - 70, y), (210, 190, 150, 255), 2)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    return cached(("page", w, h, seed, torn), build)


def torn_page(w, h):
    def build():
        base = aged_page(w, h, 5).copy()
        al = np.ones((h, w), np.float32)
        g = np.random.default_rng(12)
        # ragged tear along the left side: x edge wandering
        edge = 170 + np.cumsum(g.normal(0, 9, h)).clip(-40, 40) + 18 * np.sin(np.arange(h) / 23.0)
        for y in range(h):
            al[y, : int(max(0, edge[y]))] = 0
        # leftover stub fibers near spine: thin strip
        for y in range(h):
            e2 = 60 + 10 * math.sin(y / 17.0) + g.normal(0, 3)
            al[y, :int(e2)] = 1
            al[y, int(e2): int(edge[y] - 28)] = 0
        base.putalpha(Image.fromarray((al * 255).astype(np.uint8)))
        return finish(base, edge=3, shadow=(8, 12, 10, .4), rough=1.6)
    return cached(("torn", w, h), build)


class C06(Clip):
    name, dur, step = "C06", 2.5, None
    LINES = ["Shanghai.", "Be patient.", "The soup is", "the secret."]

    def frame(self, t, ts):
        fr = desk_bg().copy()
        pw, ph = 930, 1520
        px, py = 540, 960
        if t < 1.55:
            pg = cached(("pg1",), lambda: finish(aged_page(pw, ph, 3), edge=0, shadow=(10, 18, 14, .5), rough=1))
            blit(fr, pg, px, py)
            # flicking pages (first 0.75 s) then settle
            if t < 0.75:
                for k in range(8):
                    q = seg(t, k * 0.085, k * 0.085 + 0.16)
                    if 0 < q < 1:
                        wcur = abs(math.cos(q * math.pi))
                        side = 1 if q < .5 else -1
                        sp = cached(("flip", k % 3), lambda k=k: finish(aged_page(pw, ph, 20 + k % 3), edge=0, shadow=(0, 0, 0, 0), rough=0))
                        shade = int(255 * (0.82 + 0.18 * wcur))
                        x = px - pw / 2 + (pw * wcur / 2) * side
                        blit(fr, sp, px - pw / 2 + (pw * wcur) / 2 * 1.0 if side > 0 else px - pw / 2 - (pw * wcur) / 2, py, sx=wcur, sy=1.0, anchor=(0.5, .5))
                        d = ImageDraw.Draw(fr, "RGBA")
                        d.rectangle((px - pw / 2 - 4, py - ph / 2, px - pw / 2 + 4, py + ph / 2), fill=(70, 46, 28, 120))
            else:
                # handwriting reveals line by line
                d = ImageDraw.Draw(fr, "RGBA")
                for li, tx in enumerate(self.LINES):
                    chars, wid = cached(("hl", li), lambda tx=tx, li=li: hand_line(tx, 130, seed=li + 4))
                    rv = seg(t, 0.8 + li * 0.18, 0.95 + li * 0.18 + 0.1)
                    draw_hand_line(fr, chars, wid, 170, 420 + li * 180, rv)
                # little dumpling doodle
                dd = cached(("doodle",), lambda: xlb(150))
                if t > 1.2:
                    blit(fr, dd, 800, 1240, rot=-12, alpha=min(1, (t - 1.2) * 4) * 0.8)
        else:
            # flick to the last page: torn edge, fingertip slides along the tear
            q = seg(t, 1.55, 1.8)
            tp = torn_page(pw, ph)
            if q < 1:
                pg = cached(("pg1",), lambda: finish(aged_page(pw, ph, 3), edge=0, shadow=(10, 18, 14, .5), rough=1))
                blit(fr, pg, px, py)
                wcur = abs(math.cos(q * math.pi))
                blit(fr, cached(("flip", 0), lambda: finish(aged_page(pw, ph, 20), edge=0, shadow=(0, 0, 0, 0), rough=0)), px - pw / 2 - (pw * wcur) / 2 * (1 if q > .5 else -1) * -1 if False else px - pw / 2 + (pw * wcur / 2) * (1 if q < .5 else -1), py, sx=max(wcur, .02))
            else:
                under = cached(("under",), lambda: finish(aged_page(pw, ph, 9), edge=0, shadow=(10, 18, 14, .4), rough=1))
                blit(fr, under, px, py)
                blit(fr, tp, px, py)
                # fingertip slides down the tear
                f = seg(t, 1.9, 2.5)
                fx = px - pw / 2 + 215 + math.sin(f * 14) * 10
                fy = lerp(py - 560, py + 520, smooth(f))
                hsp = cached(("hp",), lambda: finish(hand(1, 220, True), edge=4, shadow=(10, 14, 12, .4)))
                blit(fr, hsp, fx + 40, fy + 40, rot=32, anchor=(0.29, 0.1))
        dust(fr, t, 30, 3)
        d = ImageDraw.Draw(fr, "RGBA")
        return final_grain(fr, 0.04)


# ------------------------------------------------------------------ C07: title slam
def banner_sprite():
    f1 = font(F_BLACK, 124)
    f0 = font(F_BLACK, 52)
    c = Cv(1020, 620, ss=2)
    c.rrect((30, 60, 990, 560), 26, (255, 246, 222, 255), PAL["orange"] + (255,), 10)
    c.rrect((54, 84, 966, 536), 18, None, PAL["yellow"] + (255,), 4)
    c.text((510, 170), "#01", f0, PAL["orange"] + (255,), "mm")
    c.text((510, 300), "XIAOLONGBAO", f1, PAL["brown"] + (255,), "mm")
    c.text((510, 430), "SHANGHAI, CHINA", font(F_BLACK, 56), PAL["orange"] + (255,), "mm")
    # rolled ends
    for x in (0, 960):
        c.rrect((x, 30, x + 60, 590), 28, (226, 172, 90, 255), OUT, 6)
        c.line([(x + 20, 56), (x + 20, 560)], (252, 220, 150, 255), 6)
    return c.out()


def o_center():
    f1 = font(F_BLACK, 124)
    d = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    full = d.textlength("XIAOLONGBAO", font=f1)
    pre = d.textlength("XIA", font=f1)
    wo = d.textlength("O", font=f1)
    return 510 - full / 2 + pre + wo / 2


class C07(Clip):
    name, dur, step = "C07", 2.0, None

    def frame(self, t, ts):
        # dawn sky + paper skyline plate
        sky = cached(("sky7",), lambda: Image.fromarray(np.dstack([np.tile(np.linspace(*c, H)[:, None], (1, W)) for c in ((255, 214, 150), (255, 190, 140), (250, 170, 120))]).astype(np.uint8)) if False else self.mksky())
        fr = sky.copy()
        d = ImageDraw.Draw(fr)
        sk = cached(("sk7",), lambda: finish(skyline(), edge=0, shadow=(0, -6, 10, .3), rough=0))
        blit(fr, sk, 540, 1920 - 420, anchor=(.5, .5), scale=1.12)
        fl = 1.0 - seg(t, 0.0, 0.12)
        shake = 0
        if 0.1 < t < 0.45:
            shake = (hrand(int(t * 60)) - .5) * 26 * (1 - seg(t, .1, .45))
        # banner slam: scale from 1.7 to 1 with unroll reveal
        bn = cached(("bn7",), lambda: finish(banner_sprite(), edge=6, shadow=(10, 16, 18, .4), rough=1))
        q = out_cubic(seg(t, 0.08, 0.3))
        un = out_cubic(seg(t, 0.12, 0.6))
        by = 760
        # sag
        sag = self.sag(t)
        xo = o_center() + 30
        bw, bh = bn.size
        arr = np.asarray(bn)
        xs = np.arange(bw, dtype=np.float32)
        dy = sag * np.exp(-((xs - (xo + (bw - 1020) / 2)) / 190.0) ** 2) * 1.0
        dy = dy + sag * 0.12
        mapx = np.tile(xs, (bh, 1))
        mapy = np.tile(np.arange(bh, dtype=np.float32)[:, None], (1, bw)) - dy[None, :]
        warped = cv2.remap(arr, mapx, mapy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        wsp = Image.fromarray(warped, "RGBA")
        # unroll mask
        if un < 1:
            m = Image.new("L", wsp.size, 0)
            half = bw / 2 * un
            ImageDraw.Draw(m).rectangle((bw / 2 - half, 0, bw / 2 + half, bh), fill=255)
            wsp.putalpha(ImageChops.multiply(wsp.getchannel("A"), m))
        blit(fr, wsp, 540 + shake, by + shake * .6, scale=lerp(1.7, 1.0, q) if q < 1 else 1.0)
        # Uncle falls onto the O
        land = 0.78
        fall = seg(t, 0.35, land)
        if t > 0.3:
            u = cached(("u7",), lambda: finish(uncle_doll("sit", "grin", w=430, arm_l=(40, .8), arm_r=(40, .8)), edge=5, shadow=(8, 12, 12, .35)))
            ox = 540 + (o_center() - 510)
            seat = by - bh / 2 + 160 + 60
            ytop = seat + sag * 0.95
            y = lerp(-260, ytop, in_cubic(fall)) if t < land else ytop - 40 * max(0, math.exp(-(t - land) / .18) * math.sin((t - land) * 22))
            sq = 1.0
            if land <= t < land + .2:
                sq = 1 - .16 * math.exp(-(t - land) / .08)
            blit(fr, u, ox, y, sx=1.0 / sq, sy=sq, anchor=(.5, .83))
        # Boy's hand straightens the banner
        if t > 1.25:
            h = cached(("h7",), lambda: finish(hand(1, 330, False), edge=5, shadow=(10, 14, 14, .35)))
            e = out_back(seg(t, 1.25, 1.55))
            hy = lerp(1500, by + 330 - sag * .3, e)
            hx = 980 - 220 * (1 - e) * 0
            blit(fr, h, hx, hy, rot=-14, anchor=(.5, .0))
        if fl > 0:
            fr = Image.blend(fr, Image.new("RGB", fr.size, (255, 250, 238)), fl * .85)
        # grain
        return final_grain(fr, 0.035)

    def sag(self, t):
        if t < 0.78:
            return 0.0
        a = t - 0.78
        s = 96 * (1 - math.exp(-a / .06)) if a < 0.45 else 96
        if t > 1.35:
            q = seg(t, 1.35, 1.75)
            s = 96 * (1 - smooth(q)) * 1.0 + (-14 * math.sin(q * 3.1416) if q < 1 else 0)
            if t > 1.75:
                s = -6 * math.exp(-(t - 1.75) / .12) * math.sin((t - 1.75) * 24)
        elif a >= .1:
            s = 96 + 8 * math.sin(a * 20) * math.exp(-a / .4)
        return s

    def mksky(self):
        top, mid, bot = np.array((255, 226, 168)), np.array((255, 196, 140)), np.array((248, 150, 104))
        y = np.linspace(0, 1, H)[:, None]
        col = np.where(y < .5, top + (mid - top) * (y / .5), mid + (bot - mid) * ((y - .5) / .5))
        arr = np.tile(col[:, None, :], (1, W, 1))
        im = Image.fromarray(arr.astype(np.uint8))
        d = ImageDraw.Draw(im)
        d.ellipse((430, 1060, 650, 1280), fill=(255, 236, 180))
        return im


from PIL import ImageChops


# ------------------------------------------------------------------ legend world (sepia + vermilion)
def _hill_layer(seed, base, amp, col, n=7, ground_to=1920):
    g = np.random.default_rng(seed)
    xs = np.linspace(-40, 1120, n)
    ys = [base - amp * g.random() for _ in xs]
    top = catmull(list(zip(xs, ys)), 10)
    c = Cv(W, H, ss=1)
    c.poly(top + [(1120, ground_to), (-40, ground_to)], col)
    return top, c.out()


def legend_plates():
    def build():
        sky = np.zeros((H, W, 3), np.float32)
        stops = [(0.0, (250, 224, 176)), (0.45, (248, 190, 128)), (0.62, (236, 128, 82)), (1.0, (200, 80, 52))]
        y = np.linspace(0, 1, H)
        for ch in range(3):
            sky[..., ch] = np.interp(y, [s[0] for s in stops], [s[1][ch] for s in stops])[:, None]
        sky *= paper_tex(W, H, 41)[..., None]
        skyim = Image.fromarray(np.clip(sky, 0, 255).astype(np.uint8))
        plates = []
        for i, (base, amp, col) in enumerate(((1150, 90, (204, 98, 66, 255)), (1250, 80, (160, 66, 46, 255)), (1370, 60, (112, 48, 38, 255)))):
            top, lay = _hill_layer(30 + i * 5, base, amp, col)
            plates.append(finish(lay, edge=4, shadow=(0, -8, 12, .35), rough=1.4, seed=40 + i, pad=0))
        return skyim, plates
    return cached("legend_plates", build)


def shop_plate():
    def build():
        c = Cv(W, H, ss=1)
        wall, wood = (238, 206, 158, 255), (150, 92, 54, 255)
        c.rrect((330, 1330, 960, 1740), 6, wall, OUT, 5)
        c.rrect((470, 1400, 820, 1700), 6, (96, 54, 40, 255), OUT, 5)              # dark doorway
        c.poly([(260, 1340), (1030, 1340), (930, 1120), (360, 1120)], (186, 62, 40, 255), OUT, 6)
        for k in range(9):
            c.line([(360 + k * 70, 1120), (290 + k * 94, 1336)], (140, 40, 28, 255), 5)
        c.poly([(260, 1340), (1030, 1340), (1050, 1380), (240, 1380)], (214, 88, 56, 255), OUT, 5)
        for k in range(8):                                                           # awning scallops
            c.ell((246 + k * 100, 1356, 346 + k * 100, 1420), (252, 240, 214, 255) if k % 2 else (214, 88, 56, 255), OUT, 4)
        c.rrect((300, 1590, 1010, 1750), 10, wood, OUT, 6)
        c.rrect((290, 1560, 1020, 1604), 10, (186, 124, 72, 255), OUT, 6)
        return finish(c.out(), edge=4, shadow=(0, 10, 14, .35), rough=1.0, seed=51, pad=0)
    return cached("shop_plate", build)


def legend_frame(ts, view, sun_y=1000, crow=False, petals=True, clouds=True):
    skyim, hills = legend_plates()
    fr = view.bg(skyim)
    # clouds + sun
    sunsp = cached(("sunL", int(ts * 8) % 14), lambda: finish(sun(360, int(ts * 8) % 14), edge=5, shadow=(8, 10, 12, .2)))
    sx, sy = view.pt(540, sun_y)
    blit(fr, sunsp, sx, sy, scale=view.s)
    if clouds:
        for i, (cx, cy, w, sp) in enumerate(((180, 560, 300, 7), (800, 400, 260, 10), (520, 780, 230, 5))):
            c = cached(("clL", w), lambda w=w: finish(cloud(w, (252, 236, 206, 255)), edge=4, shadow=(6, 10, 10, .2)))
            px, py = view.pt((cx + sp * ts * 3) % 1300 - 100, cy)
            blit(fr, c, px, py, scale=view.s)
    # hills with pagodas between
    k = 1080.0
    for i, hl in enumerate(hills):
        x0, y0 = view.pt(0, 0)
        fr.paste(hl.resize((int(W * view.s), int(H * view.s)), Image.BILINEAR), (int(x0), int(y0)), hl.resize((int(W * view.s), int(H * view.s)), Image.BILINEAR))
        if i == 0:
            for (px, ph, th) in ((150, 330, 4), (310, 290, 4)):
                pg = cached(("pgL", ph), lambda ph=ph, th=th: finish(pagoda(ph, th, (120, 52, 40, 255)), edge=3, shadow=(6, 8, 8, .25)))
                a, b = view.pt(px, 1140)
                blit(fr, pg, a, b, scale=view.s, anchor=(.5, 1))
    return fr


def draw_petals(fr, view, ts, n=14):
    for i in range(n):
        g = hrand(i, 7)
        x = (g * 1200 + ts * 40 + math.sin(ts * 1.6 + i) * 40) % 1300 - 100
        y = (hrand(i, 3) * 2200 + ts * 80) % 2200 - 150
        p = cached(("pet", i % 3), lambda i=i: finish(petal(40, [(214, 84, 70, 255), (236, 140, 120, 255), (252, 214, 170, 255)][i % 3]), edge=1, shadow=(2, 3, 3, .2), rough=0.6, pad=8))
        a, b = view.pt(x, y)
        blit(fr, p, a, b, rot=(ts * 90 + i * 40) % 360, scale=view.s)


def shop_scene(ts, view, **kw):
    fr = legend_frame(ts, view, **kw)
    sp = shop_plate()
    x0, y0 = view.pt(0, 0)
    spr = sp.resize((int(W * view.s), int(H * view.s)), Image.BILINEAR)
    fr.paste(spr, (int(x0), int(y0)), spr)
    return fr


class C18(Clip):
    name, dur, step = "C18", 6.0, 8
    smooth_until = 1.95

    def page_frame(self, t):
        fr = desk_bg().copy()
        pw, ph = 930, 1520
        pg = cached(("pg18",), lambda: finish(self.sketch_page(pw, ph), edge=0, shadow=(10, 18, 14, .5), rough=1))
        q = out_back(seg(t, 0.0, 0.35), 1.2)
        wcur = max(0.3, q) if t < 0.35 else 1.0
        blit(fr, pg, 540 + (1 - wcur) * 400, 960 - (1 - wcur) * 60, sx=wcur, sy=1.0 + (1 - wcur) * .04, rot=(1 - wcur) * 8)
        h = cached(("h18",), lambda: finish(hand(1, 300, False), edge=5, shadow=(10, 14, 14, .35)))
        blit(fr, h, 900, 1760 + (1 - min(1, t * 5)) * 200, rot=8, anchor=(.5, .0))
        dust(fr, t, 24, 9)
        return fr

    def sketch_page(self, w, h):
        im = aged_page(w, h, 17).copy()
        c = Cv(w, h, ss=2)
        ink = (80, 54, 36, 255)
        b = bun_big(560)
        bs = sepia(b, 0.9)
        im.alpha_composite(bs, (w // 2 - 280, 560))
        c.line(catmull([(180, 330), (360, 300), (560, 340), (760, 310)], 8), ink, 6)
        c.line(catmull([(180, 420), (420, 400), (600, 430)], 8), ink, 6)
        c.ell((620, 1180, 700, 1260), None, ink, 5)
        c.arc((820, 1190, 900, 1270), 200, 340, ink, 5)
        o = c.out()
        im.alpha_composite(o)
        return im

    def frame(self, t, ts):
        if t < 1.5:
            fr = self.page_frame(t)
            seal = cached(("seal18",), lambda: finish(seal_sprite(("LEGEND", "SAYS"), 560), edge=0, shadow=(10, 14, 12, .45), rough=1.8))
            if t > 0.85:
                q = seg(t, 0.85, 0.95)
                sc = lerp(2.6, 1.0, in_cubic(q))
                shake = 0
                if t > 0.95:
                    k = 1 - seg(t, 0.95, 1.4)
                    shake = (hrand(int(t * 60), 1) - .5) * 44 * k
                    # ink splat
                    d = ImageDraw.Draw(fr, "RGBA")
                    for i in range(14):
                        a = i / 14 * 6.283 + hrand(i, 2)
                        r0 = 300 + 80 * hrand(i, 4) + 120 * seg(t, .95, 1.1)
                        x, y = 540 + math.cos(a) * r0, 900 + math.sin(a) * r0
                        rr = 8 + 10 * hrand(i, 5)
                        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=PAL["vermilion"] + (int(210 * (1 - seg(t, .95, 1.5))),))
                blit(fr, seal, 540 + shake, 900 + shake * .7, scale=sc, rot=-7)
                if 0.95 <= t < 1.05:
                    fr = Image.blend(fr, Image.new("RGB", fr.size, (255, 244, 230)), .6)
            return final_grain(fr, 0.04)
        if t < 1.95:
            # the frame tears like paper (stepped, 12 fps) and the storybook shows through
            tt = step_t(t, 12)
            pagef = self.frame(1.45, 1.45)
            world = self.world(2.0, step_t(2.0, 8))
            q = seg(tt, 1.5, 1.95)
            e = out_cubic(q)
            rng = np.random.default_rng(6)
            xs = [540 + float(np.sin(i * 1.7) * 60 + rng.normal(0, 22)) for i in range(0, 14)]
            ys = np.linspace(-20, H + 20, 14)
            poly_l = [(0, 0)] + [(x, y) for x, y in zip(xs, ys)] + [(0, H)]
            poly_r = [(W, 0)] + [(x, y) for x, y in zip(xs, ys)] + [(W, H)]
            out = world.copy()
            for poly, sgn in ((poly_l, -1), (poly_r, 1)):
                m = Image.new("L", (W, H), 0)
                ImageDraw.Draw(m).polygon(poly, fill=255)
                piece = pagef.convert("RGBA"); piece.putalpha(m)
                # drop shadow
                sh = Image.new("RGBA", (W, H), (30, 20, 14, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .5)))
                rot = sgn * -14 * e
                for im_ in (sh, piece):
                    r = im_.rotate(rot, resample=Image.BICUBIC, center=(W / 2 + sgn * 540, H * 0.5))
                    out.paste(r, (int(sgn * 700 * e), int(120 * e * sgn * -1)), r)
            return final_grain(out, 0.04)
        return self.world(t, ts)

    def world(self, t, ts):
        ts = step_t(t, 8)
        q = seg(ts, 2.0, 6.0)
        view = View(540, lerp(1330, 1300, smooth(q)), lerp(1.0, 1.12, smooth(q)))
        # sun rises
        fr = shop_scene(ts, view, sun_y=lerp(1230, 820, smooth(seg(ts, 1.9, 6.0))))
        # rooster on the roof ridge
        crow = 3.0 < ts < 3.8 and int(ts * 8) % 2 == 0
        r = cached(("roo", crow), lambda: finish(rooster(crow, 240), edge=3, shadow=(5, 6, 6, .3)))
        a, b = view.pt(860, 1130)
        blit(fr, r, a, b + (3 if crow else 0), scale=view.s * 0.9, anchor=(.5, .95))
        # giant bun on the counter, steam wisps
        bun = cached(("bigbun",), lambda: finish(bun_big(330), edge=4, shadow=(6, 10, 10, .3)))
        a, b = view.pt(660, 1556)
        blit(fr, bun, a, b, scale=view.s, anchor=(.5, 1.0), sy=view.s * (1.0 + .012 * math.sin(ts * 5)))
        for i in range(4):
            ph = (ts * .5 + i / 4) % 1.0
            sx_, sy_ = view.pt(560 + i * 50 + math.sin(ts * 2 + i) * 14, 1400 - ph * 220)
            rr = (30 + 40 * ph) * view.s
            ov = Image.new("RGBA", fr.size, (0, 0, 0, 0))
            ImageDraw.Draw(ov).ellipse((sx_ - rr, sy_ - rr, sx_ + rr, sy_ + rr), fill=(255, 248, 232, int(150 * math.sin(ph * math.pi))))
            fr.paste(ov.filter(ImageFilter.GaussianBlur(6)), (0, 0), ov.filter(ImageFilter.GaussianBlur(6)))
        # customer stares at the bun, shrugs
        shr = seg(ts, 4.3, 4.7) * (1 - seg(ts, 5.4, 5.8))
        look = 1 if (ts > 3.2 and int(ts * 3) % 2 == 0) else 0
        cu = cached(("cust", round(shr * 4), look), lambda: finish(sepia(customer(300, shr, look), .55), edge=4, shadow=(6, 8, 8, .3)))
        a, b = view.pt(210, 1760)
        blit(fr, cu, a, b, scale=view.s * 1.3, anchor=(.5, 1.0))
        if 4.5 < ts < 5.9:
            f = font(F_BLACK, int(70 * view.s))
            qm = text_sprite("...", f, PAL["brown"] + (255,), 4, (255, 244, 224, 255))
            a, b = view.pt(290, 1190)
            blit(fr, qm, a, b - (ts - 4.5) * 8)
        if True:
            draw_petals(fr, view, ts)
        return final_grain(fr, 0.04)


# ------------------------------------------------------------------ C19: hero pose, shrinking bun, jelly
class C19(Clip):
    name, dur, step = "C19", 6.0, 8

    def frame(self, t, ts):
        if ts < 3.0:
            return self.hero(ts)
        return self.jelly(ts - 3.0)

    def hero(self, ts):
        view = View(540, lerp(1350, 1300, smooth(seg(ts, 0, 3))), lerp(1.15, 1.3, smooth(seg(ts, 0, 3))))
        fr = shop_scene(ts + 6.0, view, sun_y=820)
        # giant bun shrinks in stepped squashes
        steps = [(0.0, 1.0), (0.7, 0.86), (1.0, 0.7), (1.3, 0.55), (1.6, 0.42), (1.9, 0.3)]
        sc = 1.0
        for tt, v in steps:
            if ts >= tt:
                sc = v
        if ts < 2.2:
            bun = cached(("bigbunH",), lambda: finish(bun_big(400), edge=4, shadow=(6, 10, 10, .3)))
            sq = 1 + (0.12 if int(ts * 8) % 2 else 0) * (1 if 0.7 <= ts < 2.0 else 0)
            a, b = view.pt(250, 1740)
            blit(fr, bun, a, b, scale=view.s * sc * 0.8, sx=view.s * sc * 0.8 * sq, sy=view.s * sc * 0.8 / sq, anchor=(.5, 1))
        else:
            bh = cached(("bunhero",), lambda: finish(bun_hero(200), edge=4, shadow=(6, 8, 8, .3)))
            a, b = view.pt(290, 1740)
            pose = int(ts * 8) % 2
            blit(fr, bh, a, b - pose * 5, scale=view.s * 1.0, anchor=(.5, 1.0))
        # Uncle-faced shop owner: wind-up then hero pose
        raised = ts >= 1.0
        arm = (150, 1.0) if raised else (70, 1.0)
        pose_key = ("owner", raised)
        ow = cached(pose_key, lambda: finish(sepia(uncle_doll("stand", "grin", w=430, kimono=(244, 222, 180, 255), belt=PAL["vermilion"] + (255,), arm_l=(30, .95), arm_r=arm), .55), edge=5, shadow=(8, 12, 12, .35)))
        cp = cached(("capeL", int(ts * 8) % 3), lambda: finish(cape(460, 430, (ts * 8) % 3), edge=4, shadow=(6, 8, 8, .3)))
        ox, oy = 640, 1760
        a, b = view.pt(ox, oy)
        osc = view.s * 1.0
        blit(fr, cp, a + 70 * osc, b - 360 * osc, scale=osc, anchor=(.5, 0.0), rot=-8 + (int(ts * 8) % 3 - 1) * 4)
        bob = 4 * (int(ts * 8) % 2)
        blit(fr, ow, a, b - bob, scale=osc, anchor=(.5, .93))
        # rolling pin sword in the raised hand
        sc_d = 430 / 520.0
        hx, hy = uncle_hand_pos(1, 150 if raised else 70, 1.0)
        spr_w, spr_h = ow.width, ow.height
        # sprite origin in screen
        pad = (spr_w - 860 * sc_d) / 2
        px = a - spr_w / 2 * osc + (pad + hx * sc_d) * osc
        py = b - bob - .93 * spr_h * osc + (pad + hy * sc_d) * osc
        pin = cached(("pin",), lambda: finish(sepia(rolling_pin(420), .6), edge=3, shadow=(4, 6, 6, .3)))
        blit(fr, pin, px, py, scale=osc, rot=(52 if raised else 4) + (6 if int(ts * 8) % 2 else 0), anchor=(.1, .5))
        if raised and ts < 1.3:
            d = ImageDraw.Draw(fr, "RGBA")
            for i in range(9):
                an = -.9 + i * .2
                d.line((px + math.cos(an) * 220 * osc, py + math.sin(an) * 220 * osc, px + math.cos(an) * 360 * osc, py + math.sin(an) * 360 * osc), fill=(255, 244, 220, 220), width=7)
        draw_petals(fr, view, ts + 6)
        return final_grain(fr, 0.04)

    def jelly(self, u):
        fr = paper_bg(W, H, (246, 226, 188), seed=61, vignette=.25).copy()
        d = ImageDraw.Draw(fr, "RGBA")
        d.rectangle((0, 1480, W, H), fill=(150, 98, 56))
        for y in range(1500, H, 50):
            d.line((0, y, W, y + 6), fill=(120, 74, 40, 140), width=4)
        d.rectangle((0, 1470, W, 1490), fill=(96, 60, 34))
        d.rounded_rectangle((26, 26, W - 26, H - 26), 30, outline=PAL["vermilion"], width=10)
        cx, cy = 540, 860
        q_cut = [(0.5, 0), (0.7, 1), (0.9, 2)]
        cuts = sum(1 for tt, _ in q_cut if u >= tt)
        hcut = u >= 1.1
        sep = smooth(seg(u, 1.15, 1.35)) * 16
        if u < 1.5:
            pop = out_back(seg(u, 0.0, 0.3))
            wob = (int(u * 8) % 2) * 2.0 - 1.0
            jl = cached(("jelly",), lambda: finish(jelly(), edge=4, shadow=(8, 12, 12, .35)))
            if cuts == 0 and not hcut:
                blit(fr, jl, cx, cy, scale=pop, rot=wob * 1.5)
                gl = Image.new("RGBA", fr.size, (0, 0, 0, 0))
                ImageDraw.Draw(gl).ellipse((cx - 420, cy - 300, cx + 420, cy + 300), fill=(255, 190, 80, 70))
                gl = gl.filter(ImageFilter.GaussianBlur(60)); fr.paste(gl, (0, 0), gl)
            else:
                # sliced into cubes
                bw, bh = 520, 360
                ncol = [1, 2, 3, 4, 4][cuts + (1 if cuts == 3 else 0)] if cuts < 3 else 4
                ncol = cuts + 1
                nrow = 2 if hcut else 1
                cw_, ch_ = bw / ncol, bh / nrow
                for r in range(nrow):
                    for c_ in range(ncol):
                        x = cx - bw / 2 + c_ * cw_ + cw_ / 2 + (c_ - (ncol - 1) / 2) * sep
                        y = cy - bh / 2 + r * ch_ + ch_ / 2 + (r - (nrow - 1) / 2) * sep
                        if u >= 1.3 and r == 0 and c_ == 1:
                            continue
                        cube = cached(("cube", int(cw_), int(ch_)), lambda cw_=cw_, ch_=ch_: finish(self.cube(int(cw_) - 4, int(ch_) - 4), edge=3, shadow=(5, 8, 8, .3), rough=.8))
                        blit(fr, cube, x, y)
                # the knife
                for tt, i in q_cut:
                    if tt - .12 <= u < tt + .2:
                        kx = cx - 260 + (i + 1) * 520 / 4 if i < 3 else cx
                        k_ = cached(("knife",), lambda: finish(knife(420), edge=3, shadow=(5, 8, 8, .3)))
                        ky = lerp(cy - 520, cy, 1 - abs(seg(u, tt - .12, tt + .2) * 2 - 1))
                        blit(fr, k_, kx, ky - 180, rot=90, anchor=(1.0, .5))
                if 0.98 <= u < 1.2:
                    k_ = cached(("knife",), lambda: finish(knife(420), edge=3, shadow=(5, 8, 8, .3)))
                    kx = lerp(W + 300, cx + 200, 1 - abs(seg(u, .98, 1.2) * 2 - 1))
                    blit(fr, k_, kx, cy, anchor=(.2, .5))
        if 1.3 <= u < 2.2:
            # one cube hops into a dough disc
            q = seg(u, 1.3, 1.8)
            x0, y0 = cx - 260 + 520 / 4 * 1.5, cy - 90
            x1, y1 = 540, 1330
            x = lerp(x0, x1, smooth(q)); y = lerp(y0, y1, smooth(q)) - math.sin(q * math.pi) * 180
            disc = cached(("disc",), lambda: finish(self.disc(380), edge=4, shadow=(8, 12, 12, .3)))
            blit(fr, disc, 540, 1330, scale=out_back(seg(u, 1.3, 1.5)))
            cube = cached(("cubeS",), lambda: finish(self.cube(130, 110), edge=3, shadow=(5, 8, 8, .3)))
            blit(fr, cube, x, y, rot=q * 40)
        if u >= 1.9:
            # folded bun then steamer, melt, dragon
            pop = out_back(seg(u, 1.9, 2.15))
            bun = cached(("xlbL",), lambda: finish(xlb(360, gold=False), edge=4, shadow=(8, 12, 12, .3)))
            stm = cached(("stmL",), lambda: finish(steamer_basket(620, lid=False), edge=5, shadow=(10, 14, 14, .35)))
            if u < 2.1:
                blit(fr, bun, 540, 1330, scale=pop)
            else:
                # cut-away steamer with the bun inside; jelly melts into a golden pool
                blit(fr, stm, 540, 1250)
                melt = smooth(seg(u, 2.2, 2.9))
                gl = Image.new("RGBA", fr.size, (0, 0, 0, 0))
                ImageDraw.Draw(gl).ellipse((540 - 300 * melt, 1180 - 180 * melt, 540 + 300 * melt, 1180 + 180 * melt), fill=(255, 196, 80, int(150 * melt)))
                gl = gl.filter(ImageFilter.GaussianBlur(40)); fr.paste(gl, (0, 0), gl)
                bn = cached(("xlbG", int(melt * 4)), lambda: finish(xlb(300, gold=melt > .4), edge=4, shadow=(8, 12, 12, .3)))
                blit(fr, bn, 540, 1160 + (int(u * 8) % 2) * 3)
                if u > 2.2:
                    dr = cached(("dragon", int((u - 2.2) * 8)), lambda: finish(paper_dragon((u - 2.2), 520), edge=3, shadow=(4, 6, 6, .25), rough=0.8))
                    rise = smooth(seg(u, 2.3, 3.0))
                    blit(fr, dr, 540, lerp(1000, 520, rise), scale=lerp(.7, 1.2, rise), rot=math.sin(u * 5) * 6)
                    for i in range(7):
                        ph = (u * 1.3 + i / 7) % 1
                        sx_, sy_ = 540 + 260 * math.sin(i * 2.3 + u * 3) * ph, 1050 - ph * 700
                        r_ = 14 * (1 - ph) + 4
                        d.polygon([(sx_, sy_ - r_ * 1.8), (sx_ + r_ * .5, sy_ - r_ * .5), (sx_ + r_ * 1.8, sy_), (sx_ + r_ * .5, sy_ + r_ * .5), (sx_, sy_ + r_ * 1.8), (sx_ - r_ * .5, sy_ + r_ * .5), (sx_ - r_ * 1.8, sy_), (sx_ - r_ * .5, sy_ - r_ * .5)], fill=(255, 226, 120, int(230 * (1 - ph))))
        return final_grain(fr, 0.04)

    def cube(self, w, h):
        c = Cv(max(w, 8), max(h, 8), ss=2)
        c.rrect((2, 2, w - 2, h - 2), 16, (240, 164, 48, 255), (176, 100, 22, 255), 4)
        c.rrect((10, 8, w * .6, h * .4), 12, (252, 210, 120, 220))
        return c.out()

    def disc(self, d):
        c = Cv(d, d, ss=2)
        c.ell((3, 3, d - 3, d - 3), (252, 236, 200, 255), OUT, 4)
        c.ell((d * .12, d * .12, d * .88, d * .88), None, (226, 196, 150, 255), 3)
        return c.out()


# ------------------------------------------------------------------ C21: the asterisk on the seal
def asterisk(size=170, col=None):
    col = col or (PAL["vermilion"] + (255,))
    c = Cv(size, size, ss=2)
    for a in (0, 60, 120):
        r = math.radians(a + 90)
        c.line([(size / 2 + math.cos(r) * size * .42, size / 2 + math.sin(r) * size * .42), (size / 2 - math.cos(r) * size * .42, size / 2 - math.sin(r) * size * .42)], col, size * .17)
    return c.out()


def sepia_world_bg():
    def build():
        im = paper_bg(W, H, (232, 204, 156), seed=71, vignette=.3).copy()
        d = ImageDraw.Draw(im, "RGBA")
        top = catmull([(-40, 1250), (200, 1170), (460, 1230), (760, 1150), (1120, 1220)], 10)
        d.polygon(top + [(1120, H), (-40, H)], fill=(190, 96, 62, 120))
        top = catmull([(-40, 1400), (300, 1330), (640, 1390), (1120, 1320)], 10)
        d.polygon(top + [(1120, H), (-40, H)], fill=(130, 58, 42, 150))
        return im
    return cached("sepiabg", build)


class C21(Clip):
    name, dur, step = "C21", 3.0, 8

    def frame(self, t, ts):
        fr = sepia_world_bg().copy()
        # the Boy, as a paper sticker in colour (he has stepped out of the story to review it)
        boy = cached(("boyst",), lambda: finish(self.boy_img(), edge=6, shadow=(10, 14, 14, .4), rough=1.2))
        sc = 800 / 1350.0
        pop = out_back(seg(ts, 0.0, 0.3))
        br = 1.0 + 0.008 * math.sin(ts * 3.2)
        blit(fr, boy, 540, 1905, scale=sc * pop, sy=sc * pop * br, anchor=(.5, 1.0))
        seal = cached(("seal21",), lambda: finish(seal_sprite(("LEGEND", "SAYS"), 560), edge=0, shadow=(10, 14, 12, .45), rough=1.8))
        shake = 0
        if 1.2 <= ts < 1.6:
            shake = (hrand(int(ts * 8), 2) - .5) * 26
        blit(fr, seal, 540 + shake, 520 + shake * .6, scale=1.0, rot=-6)
        # asterisk drops onto the seal's corner
        if ts > 0.7:
            q = seg(ts, 0.7, 1.2)
            y = lerp(-120, 410, in_cubic(q)) if ts < 1.2 else 410 - 36 * math.exp(-(ts - 1.2) / .1) * abs(math.sin((ts - 1.2) * 14))
            ast = cached(("ast",), lambda: finish(asterisk(190), edge=5, edge_col=(255, 244, 226), shadow=(8, 12, 12, .4)))
            blit(fr, ast, 790, y, rot=ts * 120 if ts < 1.2 else 8)
        # tag slides up
        if ts > 1.8:
            q = out_back(seg(ts, 1.8, 2.15))
            tag = cached(("tag21",), lambda: finish(tag_sprite("*competing versions exist", 46), edge=5, shadow=(8, 12, 12, .35)))
            blit(fr, tag, 540, lerp(1300, 900, q), rot=-2)
        dust(fr, ts, 14, 5, 90)
        return final_grain(fr, 0.04)

    def boy_img(self):
        im = Image.open(BOY_PNG).convert("RGBA")
        return im


def tag_sprite(text, size=44):
    f = font(F_BLACK, size)
    ts_ = text_sprite(text, f, PAL["brown"] + (255,), 0, None, pad=28)
    c = Cv(ts_.width + 20, ts_.height + 10, ss=1)
    c.rrect((0, 0, c.w - 1, c.h - 1), 18, (252, 242, 214, 255), (196, 120, 60, 255), 5)
    im = c.out()
    im.alpha_composite(ts_, (10, 5))
    return im


# ------------------------------------------------------------------ C22: fun fact
def fact_card(w=880, h=520):
    c = Cv(w, h, ss=2)
    c.rrect((10, 10, w - 10, h - 10), 40, (255, 248, 232, 255), PAL["orange"] + (255,), 10)
    c.rrect((34, 34, w - 34, h - 34), 28, None, PAL["yellow"] + (255,), 4)
    c.text((w / 2, 100), "FUN FACT", font(F_BLACK, 66), PAL["orange"] + (255,), "mm")
    c.text((w / 2, 220), "In Nanxiang, many say", font(F_BOLD, 54), PAL["brown"] + (255,), "mm")
    c.text((w / 2, 340), "xiaolong", font(F_BLACK, 112), PAL["brown"] + (255,), "mm")
    c.text((w / 2, 450), "mantou", font(F_BLACK, 112), PAL["orange"] + (255,), "mm")
    return c.out()


class C22(Clip):
    name, dur, step = "C22", 4.0, None

    def frame(self, t, ts):
        fr = self.bg().copy()
        pgs = cached(("pg22",), lambda: finish(pagoda(300, 4, (170, 92, 62, 255)), edge=4, shadow=(6, 10, 10, .3)))
        blit(fr, pgs, 150, 1010, anchor=(.5, 1), scale=1.0)
        blit(fr, pgs, 930, 1010, anchor=(.5, 1), scale=1.0, flip=True)
        # card pops
        q = out_back(seg(t, 0.15, 0.5), 2.0)
        card = cached(("fc",), lambda: finish(fact_card(), edge=6, shadow=(10, 16, 16, .35)))
        blit(fr, card, 540, 520, scale=q, rot=(1 - q) * -6 if q < 1 else math.sin(t * 2) * 0.6)
        # Uncle: relaxed, then two fingers, then pointing at two dumplings
        if t < 2.3:
            state = dict(arm_r=(25, 1.0), arm_l=(25, 1.0), fingers_r=0, point_r=False, expr="proud")
        elif t < 3.2:
            state = dict(arm_r=(150, .95), arm_l=(25, 1.0), fingers_r=2, point_r=False, expr="grin")
        else:
            state = dict(arm_r=(62, .95), arm_l=(25, 1.0), fingers_r=0, point_r=True, expr="grin")
        key = ("u22", str(state))
        u = cached(key, lambda: finish(uncle_doll("stand", w=560, **state), edge=5, shadow=(10, 14, 14, .35)))
        pop = out_back(seg(t, 0.0, 0.4), 1.6)
        bob = math.sin(t * 5) * 6 if 2.3 <= t < 3.2 else math.sin(t * 2.5) * 3
        blit(fr, u, 500, 1990 + (1 - pop) * 400 - bob, scale=1.0, anchor=(.5, 1.0))
        # two dumplings pop on a plate
        for i in range(2):
            tt = 3.2 + i * .18
            if t > tt:
                pq = out_back(seg(t, tt, tt + .22), 3.0)
                dp = cached(("dpl22",), lambda: finish(xlb(170), edge=4, shadow=(6, 10, 10, .3)))
                blit(fr, dp, 770 + i * 150, 1560 - i * 6, scale=pq * 1.0)
        if t > 3.1:
            pl = cached(("plate",), lambda: finish(self.plate(480), edge=4, shadow=(8, 12, 12, .3)))
            blit(fr, pl, 850, 1640, scale=out_back(seg(t, 3.1, 3.3)))
            pl_ = None
        # card words hop
        dust(fr, t, 16, 6, 120)
        return final_grain(fr, 0.04)

    def bg(self):
        def build():
            top, bot = np.array((196, 226, 232)), np.array((255, 238, 204))
            y = np.linspace(0, 1, H)[:, None, None]
            arr = (top + (bot - top) * np.clip(y * 1.4, 0, 1)) * np.ones((1, W, 1))
            im = Image.fromarray((arr * paper_tex(W, H, 81)[..., None]).clip(0, 255).astype(np.uint8))
            d = ImageDraw.Draw(im, "RGBA")
            g = catmull([(-40, 1060), (240, 1000), (540, 1050), (860, 990), (1120, 1040)], 10)
            d.polygon(g + [(1120, H), (-40, H)], fill=(168, 196, 120, 255))
            g = catmull([(-40, 1180), (300, 1130), (700, 1190), (1120, 1130)], 10)
            d.polygon(g + [(1120, H), (-40, H)], fill=(140, 176, 96, 255))
            g = catmull([(-40, 1360), (400, 1320), (800, 1370), (1120, 1330)], 10)
            d.polygon(g + [(1120, H), (-40, H)], fill=(236, 206, 150, 255))
            return im
        return cached("bg22", build)

    def plate(self, w):
        c = Cv(w, int(w * .32), ss=2)
        c.ell((4, 4, w - 4, w * .3), (250, 244, 230, 255), (92, 120, 170, 255), 6)
        c.ell((w * .14, w * .06, w * .86, w * .24), (236, 228, 208, 255))
        return c.out()


# ------------------------------------------------------------------ C24: handwriting lifts off as steam
class C24(Clip):
    name, dur, step = "C24", 4.5, None
    LINES = ["Life is like a", "soup dumpling.", "Rush it, you get burned.", "Be patient, you get", "the best part."]

    def frame(self, t, ts):
        # push-in: page + handwriting zoom while the page glows; the dumpling appears in the haze
        fr = paper_bg(W, H, (244, 226, 188), seed=91, vignette=.3).copy()
        d = ImageDraw.Draw(fr, "RGBA")
        for y in range(180, H - 100, 110):
            d.line((90, y, W - 90, y + 3), fill=(206, 184, 142, 150), width=3)
        glow = smooth(seg(t, 0.3, 2.2))
        # handwriting lines: each char lifts off as steam, line by line
        y0 = 520
        for li, tx in enumerate(self.LINES):
            chars, wid = cached(("hl24", li), lambda tx=tx, li=li: hand_line(tx, 104 if li != 2 else 92, seed=li + 11))
            x0 = (W - wid) / 2
            ly = y0 + li * 190
            for ci, (sp, x, dy, rot) in enumerate(chars):
                start = 0.8 + li * 0.5 + ci * 0.025
                q = seg(t, start, start + 1.1)
                if q <= 0:
                    blit(fr, sp, x0 + x, ly + dy, rot=rot, anchor=(0, .5))
                elif q < 1:
                    rise = out_cubic(q) * 260
                    sway = math.sin(q * 5 + ci) * 24 * q
                    sp2 = sp.filter(ImageFilter.GaussianBlur(1 + 9 * q))
                    # steam colour: ink -> white gold
                    col = Image.new("RGBA", sp2.size, (255, 244, 220, 255))
                    mix = sp2.copy()
                    sp2 = Image.composite(col, sp2.convert("RGBA"), Image.new("L", sp2.size, int(255 * q))) if False else Image.blend(sp2, tint(sp2, (255, 230, 180), (255, 250, 236)), min(1, q * 1.4))
                    sp2.putalpha(sp2.getchannel("A").point(lambda v: int(v * (1 - q) ** 0.8)))
                    blit(fr, sp2, x0 + x + sway, ly + dy - rise, rot=rot * (1 - q) + sway * .4, scale=1 + q * .5, anchor=(0, .5))
        # warm golden glow
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        r = 300 + 500 * glow
        ImageDraw.Draw(gl).ellipse((W / 2 - r, 880 - r, W / 2 + r, 880 + r), fill=(255, 200, 96, int(120 * glow)))
        gl = gl.filter(ImageFilter.GaussianBlur(90))
        fr.paste(gl, (0, 0), gl)
        # steam puffs
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        for i in range(26):
            ph = (t * .35 + hrand(i, 1)) % 1
            x = 120 + hrand(i, 2) * 840 + math.sin(t * 1.3 + i) * 50
            y = 1400 - ph * 1200
            rr = 50 + 90 * ph
            a = int(math.sin(ph * math.pi) * 60 * (0.3 + 0.7 * smooth(seg(t, 0.7, 2.0))))
            od.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 250, 238, a))
        ov = ov.filter(ImageFilter.GaussianBlur(46))
        fr.paste(ov, (0, 0), ov)
        # golden dumpling emerges, camera pushes in
        k = seg(t, 2.3, 4.5)
        if k > 0:
            dp = cached(("xlb24",), lambda: finish(xlb(560, gold=True), edge=0, shadow=(0, 0, 0, 0), rough=0))
            blit(fr, dp, W / 2, 900 + 40 * (1 - smooth(k)), scale=lerp(0.5, 1.25, smooth(k)), alpha=smooth(seg(t, 2.3, 3.1)), rot=math.sin(t * 2) * 2)
            ov2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for i in range(12):
                ph = (t * .5 + i / 12) % 1
                x = W / 2 + math.sin(i * 2 + t * 2) * 260 * ph + (hrand(i, 3) - .5) * 100
                y = 960 - ph * 760
                rr = 40 + 70 * ph
                ImageDraw.Draw(ov2).ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 252, 244, int(140 * math.sin(ph * math.pi) * smooth(seg(t, 2.6, 3.4)))))
            ov2 = ov2.filter(ImageFilter.GaussianBlur(20)); fr.paste(ov2, (0, 0), ov2)
        # whole-frame push in
        z = 1.0 + 0.22 * smooth(seg(t, 1.2, 4.5))
        if z > 1.0:
            vw, vh = W / z, H / z
            fr = fr.resize((W, H), Image.BICUBIC, box=((W - vw) / 2, (H - vh) / 2 - 40 * (z - 1), (W + vw) / 2, (H + vh) / 2 - 40 * (z - 1)))
        dust(fr, t, 30, 8, 190)
        return final_grain(fr, 0.035)
