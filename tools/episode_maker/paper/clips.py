"""The CODE clips of Episode 1 V4 (paper-cut legend, ink-wash map, journal, title...). Each Clip renders PIL RGB frames."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from .core import *
from .shapes import *
from .worlds import *

FPS = 30


class Clip:
    name, dur, step = "clip", 3.0, None

    def frame(self, t, ts):
        raise NotImplementedError

    smooth_until = 0.0
    # --- horizontal 16:9 version (render_clip(..., orient="landscape")) ---
    # Default: the finished 1080x1920 frame is re-composed into 1920x1080: the sharp portrait frame (fitted to the height, or zoomed by
    # land_zoom and cropped around land_focus(t)) stands on a blurred, darkened, widened copy of itself. A clip that has its own wide
    # layout overrides frame_land(t, ts) and returns a 1920x1080 PIL image (or None to use the default).
    land_zoom = 1.0

    def land_focus(self, t):
        return 0.5

    def frame_land(self, t, ts):
        return None

    def cacheable(self, t):
        return self.step is not None and t >= self.smooth_until

    def tstep(self, t):
        return t if (not self.step or t < self.smooth_until) else step_t(t, self.step)


LW, LH = 1920, 1080
_land_cache = {}


def land_compose(img, zoom=1.0, focus=0.5):
    """Portrait frame (W x H) -> landscape frame (1920 x 1080): sharp center column over a blurred, widened copy."""
    key = (zoom,)
    if key not in _land_cache:
        fw = int(round(W * LH / H * zoom))                      # fitted column: full height at zoom 1, wider and cropped above
        fh = int(round(LH * zoom))
        m = Image.new("L", (LW, LH), 0)
        ImageDraw.Draw(m).rectangle(((LW - fw) // 2, 0, (LW + fw) // 2, LH), fill=255)
        glow = m.filter(ImageFilter.GaussianBlur(34)).point(lambda v: int(v * 0.42))
        _land_cache[key] = (fw, fh, glow)
    fw, fh, glow = _land_cache[key]
    # background: the frame, covered to 1920 wide at 1/8 size, cropped at the focus height, then scaled up (so it is already soft)
    small = img.resize((LW // 8, int(round(LW // 8 * H / W))), Image.BILINEAR)
    bh = LH // 8
    top = int(round((small.height - bh) * min(max(focus, 0.0), 1.0)))
    bg = small.crop((0, top, small.width, top + bh)).resize((LW, LH), Image.BICUBIC).filter(ImageFilter.GaussianBlur(10))
    bg = Image.blend(bg, Image.new("RGB", bg.size, (255, 244, 224)), 0.10)
    bg.paste(Image.new("RGB", bg.size, (46, 32, 22)), (0, 0), glow)     # soft shadow around the column
    fg = img.resize((fw, int(round(H * fw / W))), Image.LANCZOS)
    y0 = int(round((fg.height - LH) * min(max(focus, 0.0), 1.0))) if fg.height > LH else 0
    bg.paste(fg.crop((0, y0, fw, y0 + min(LH, fg.height))), ((LW - fw) // 2, 0))
    return bg


def render_clip(clip, path, fps=FPS, scale=1.0, only=None, orient="portrait"):
    """Render a clip to `path` (or return the PIL frames when path is None). orient: "portrait" 1080x1920 | "landscape" 1920x1080."""
    land = orient == "landscape"
    n = int(round(clip.dur * fps))
    ow, oh = (LW, LH) if land else (W, H)
    w, h = int(ow * scale), int(oh * scale)
    wr = Writer(path, fps, w, h) if path else None
    last, lastkey, out = None, None, []
    for i in range(n):
        t = i / fps
        ts = clip.tstep(t)
        if clip.cacheable(t) and lastkey == ts and last is not None:
            img = last
        else:
            img = clip.frame(t, ts)
            if img.size != (W, H):
                img = img.resize((W, H))
            last, lastkey = img, ts
        if land:
            nat = clip.frame_land(t, ts)
            img = nat if nat is not None else land_compose(img, clip.land_zoom, clip.land_focus(t))
        if scale != 1.0:
            img = img.resize((w, h), Image.LANCZOS)
        if wr:
            wr.write(img)
        else:
            out.append(img)
    if wr:
        wr.close()
    return out


# ------------------------------------------------------------------ view helper (world 1080x1920 -> screen)
class View:
    def __init__(self, cx=540, cy=960, s=1.0):
        self.cx, self.cy, self.s = cx, cy, s

    def pt(self, x, y):
        return ((x - self.cx) * self.s + W / 2, (y - self.cy) * self.s + H / 2)

    def bg(self, world_img):
        """Crop + scale the supersampled world image to the screen."""
        k = world_img.width / W
        vw, vh = W / self.s, H / self.s
        x0 = min(max(self.cx - vw / 2, 0), W - vw); y0 = min(max(self.cy - vh / 2, 0), H - vh)
        self.cx, self.cy = x0 + vw / 2, y0 + vh / 2
        return world_img.resize((W, H), Image.BICUBIC, box=(x0 * k, y0 * k, (x0 + vw) * k, (y0 + vh) * k))


def route_points():
    pts = [(120, 360), (330, 440), (560, 470), (800, 520), (930, 650), (820, 780), (560, 830), (330, 870), (200, 990), (330, 1100),
           (560, 1140), (780, 1170), (880, 1290), (780, 1400), (640, 1470), (560, 1580), (620, 1650)]
    return catmull(pts, 16)


class Route:
    def __init__(self):
        self.p = route_points()
        d = [0.0]
        for a, b in zip(self.p, self.p[1:]):
            d.append(d[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        self.d = np.array(d)
        self.L = d[-1]

    def at(self, u):
        s = min(max(u, 0), 1) * self.L
        i = int(np.searchsorted(self.d, s, side="right") - 1)
        i = min(max(i, 0), len(self.p) - 2)
        f = (s - self.d[i]) / max(self.d[i + 1] - self.d[i], 1e-6)
        a, b = self.p[i], self.p[i + 1]
        return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, b[0] - a[0], b[1] - a[1])


ROUTE = Route()


def draw_route(fr, v, p, t, dot=11, step=34):
    """Dotted red route, drawn up to fraction p. Dots are paper-cut circles."""
    d = ImageDraw.Draw(fr)
    n = int(ROUTE.L * p / step)
    r = max(2, dot * v.s * 0.5)
    for i in range(n + 1):
        x, y, _, _ = ROUTE.at(min(i * step / ROUTE.L, 1))
        sx, sy = v.pt(x, y)
        if -50 < sx < W + 50 and -50 < sy < H + 50:
            d.ellipse((sx - r - 2, sy - r - 2 + 3, sx + r + 2, sy + r + 3 + 2), fill=(120, 80, 50))
            d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=PAL["orange"], outline=(255, 244, 226), width=max(1, int(2 * v.s * 0.5)))
    if 0 < p < 1:
        x, y, _, _ = ROUTE.at(p)
        sx, sy = v.pt(x, y)
        rr = 20 * v.s * (0.8 + 0.4 * hrand(round(t * 8)))
        d.ellipse((sx - rr, sy - rr, sx + rr, sy + rr), fill=(255, 150, 60))
        d.ellipse((sx - rr * .5, sy - rr * .5, sx + rr * .5, sy + rr * .5), fill=(255, 236, 190))


def cam_sprite(phase, head, flip, rider, size_px, blink=False):
    key = ("camelhr", phase, head, rider, blink)
    def build():
        sp = camel(phase, head, rider=rider, blink=blink, size=1120)
        return finish(sp, edge=7, shadow=(10, 14, 12, 0.34), pad=40)
    sp = cached(key, build)
    if flip:
        sp = ImageOps.mirror(sp)
    return sp


def draw_camel(fr, v, x, y, phase, head, flip, wsize, rider=None, blink=False, bob=0.0, zz=False, t=0):
    """Draw a camel at world (x,y)=feet centre. wsize=world width of the camel."""
    sp = cam_sprite(phase, head, flip, rider, 1120, blink)
    sc = wsize * v.s / 1160.0
    sx, sy = v.pt(x, y - bob)
    blit(fr, sp, sx, sy, scale=sc, anchor=(0.5, 0.93))
    if rider:
        # Uncle asleep on top, hugging a steamer basket
        u = cached(("unc_sleep",), lambda: finish(uncle_doll("sit", "sleep", w=420, arm_l=(32, .75), arm_r=(32, .75)), edge=5, shadow=(8, 10, 10, .3)))
        bsk = cached(("basket",), lambda: finish(steamer_basket(230), edge=4, shadow=(6, 8, 8, .3)))
        ux = sx + (0.02 if not flip else -0.02) * wsize * v.s
        uy = sy - 0.40 * wsize * v.s
        blit(fr, u, ux, uy, scale=0.5 * wsize * v.s / 695, anchor=(0.5, 0.80))
        blit(fr, bsk, ux, uy - 0.03 * wsize * v.s, scale=0.34 * wsize * v.s / 230, anchor=(0.5, 0.5))
        if zz:
            for i in range(3):
                ph = (t * 0.7 + i / 3) % 1.0
                f = font(F_BLACK, int(wsize * v.s * (0.07 + 0.04 * ph)))
                tx, ty = ux + wsize * v.s * (0.12 + ph * 0.2), uy - wsize * v.s * (0.3 + ph * 0.35)
                a = int(255 * math.sin(ph * math.pi))
                sp_ = text_sprite("Z", f, (80, 64, 120, a), 3, (250, 244, 232, a))
                blit(fr, sp_, tx, ty, rot=10 - ph * 20)


class C03(Clip):
    name, dur, step = "C03", 4.5, 8
    N = 4
    smooth_until = 0.58

    def frame(self, t, ts):
        world = map_world()
        if t < 0.58:
            return self.opening(t, ts)
        if t < 1.1:
            return self.unroll(t, ts)
        return self._map(ts)

    def _map(self, ts):
        world = map_world()
        # camera: full map, then push to the last camel
        stop_t = 2.7
        u_stop = 0.115
        def cu(i, tt):
            return min(0.085 + 0.085 * (tt - 0.5) - i * 0.034, u_stop + (3 - i) * 0.034 if False else 9) if i < 3 else min(0.085 + 0.085 * (tt - 0.5) - i * 0.034, u_stop)
        last_u = cu(3, min(ts, stop_t + 1.0))
        lx, ly, _, _ = ROUTE.at(last_u)
        k = ease_zoom = smooth(seg(ts, 2.1, 3.7))
        s = lerp(1.0, 3.3, k)
        v = View(lerp(540, lx, k), lerp(960, ly - 60, k), s)
        fr = v.bg(world)
        # sun + clouds (world positions with a little parallax)
        sunsp = cached(("sun", int(ts * 8) % 14), lambda: finish(sun(300, int(ts * 8) % 14), edge=5, shadow=(8, 10, 10, .25)))
        sx, sy = v.pt(900, 190)
        blit(fr, sunsp, sx, sy, scale=v.s)
        for i, (cx_, cy_, w_, sp_) in enumerate(((160, 240, 280, 6), (620, 330, 220, 9), (860, 420, 180, 12))):
            c_ = cached(("cl", w_), lambda w_=w_: finish(cloud(w_), edge=4, shadow=(6, 10, 10, .22)))
            px, py = v.pt(cx_ + sp_ * ts * 2, cy_)
            blit(fr, c_, px, py, scale=v.s)
        # compass mark
        # route draws itself
        draw_route(fr, v, smooth(seg(ts, 0.6, 2.8)) * 1.0, ts)
        # camels (back to front: last camel is nearest the camera, drawn last)
        for i in range(self.N):
            u = cu(i, ts)
            x, y, dx, dy = ROUTE.at(u)
            moving = not (i == 3 and ts >= stop_t)
            ph = int(ts * 8 + i) % 4 if moving else 0
            flip = dx < 0
            head = "side"
            blink = False
            if i == 3 and ts >= stop_t + 0.4:
                head = "front"
                blink = (int(ts * 8) % 13 == 9)
            bob = (3 if ph % 2 else 0) if moving else 0
            draw_camel(fr, v, x, y + 40, ph, head, flip, 260, rider=(i == 3), blink=blink, bob=bob, zz=(i == 3 and ts > 1.2), t=ts)
        return final_grain(fr, 0.04)

    def map_frame(self, ts):
        return self._map(ts)

    def unroll(self, t, ts):
        base = self.opening(0.57, 0.57)
        q = out_cubic(seg(ts, 0.58, 1.08))
        m = self._map(max(ts, 0.6))
        hh, hw = lerp(380, 960, q), lerp(380, 540, q)
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).rounded_rectangle((540 - hw, 960 - hh, 540 + hw, 960 + hh), radius=int(lerp(30, 0, q)), fill=255)
        base.paste(m, (0, 0), mask)
        d = ImageDraw.Draw(base, "RGBA")
        for sgn in (-1, 1):
            y = 960 + sgn * hh
            for k in range(26):  # rolled paper edge (cylinder shading)
                a = k / 25
                shade = int(60 + 190 * math.sin(a * math.pi))
                d.line((540 - hw, y + sgn * (k - 4), 540 + hw, y + sgn * (k - 4)), fill=(shade, int(shade * .88), int(shade * .66), 255), width=2)
        return final_grain(base, 0.04)

    def opening(self, t, ts):
        fr = desk_bg().copy()
        jc = cached(("jcf",), lambda: finish(journal_closed(), edge=6, shadow=(14, 26, 18, .5)))
        drop = out_cubic(seg(t, 0.0, 0.13))
        sc = lerp(1.5, 1.0, drop)
        shake = 0
        if 0.13 < t < 0.45:
            k = 1 - seg(t, 0.13, 0.45)
            shake = (hrand(int(t * 60)) - .5) * 40 * k
        if t < 0.34:
            blit(fr, jc, 540 + shake, 960 + shake * .6, scale=sc * 0.98)
            # dust ring
            if t > 0.13:
                q = seg(t, 0.13, 0.5)
                d = ImageDraw.Draw(fr, "RGBA")
                for i in range(10):
                    a = i / 10 * 2 * math.pi
                    r0 = 420 + 360 * q
                    px, py = 540 + math.cos(a) * r0, 960 + math.sin(a) * r0 * 1.15
                    rr = 36 + 30 * q
                    d.ellipse((px - rr, py - rr, px + rr, py + rr), fill=(240, 226, 196, int(150 * (1 - q))))
        else:
            # cover flips open (scale X to 0 then pages)
            q = seg(t, 0.34, 0.55)
            pages = journal_open_sprite()
            blit(fr, pages, 540, 960, scale=1.0)
            if q < 1:
                cw = max(0.02, abs(math.cos(q * math.pi * .5)))
                blit(fr, jc, 540 - 410 * (1 - cw) * 1.0 - 0, 960, sx=cw * 0.98, sy=0.98)
        return final_grain(fr, 0.04)


def journal_open_sprite(w=880, h=1100):
    def build():
        c = Cv(w, h, ss=2)
        c.rrect((4, 4, w - 4, h - 4), 30, (110, 62, 34, 255), OUT, 5)
        c.rrect((26, 24, w / 2 - 2, h - 24), 12, (250, 238, 206, 255), (200, 170, 120, 255), 3)
        c.rrect((w / 2 + 2, 24, w - 26, h - 24), 12, (252, 242, 212, 255), (200, 170, 120, 255), 3)
        for k in range(1, 5):
            c.line([(w / 2 - 12 * k, 40), (w / 2 - 12 * k, h - 40)], (214, 190, 150, 255), 2)
        return c.out()
    return cached(("jopen", w, h), lambda: finish(build(), edge=0, shadow=(14, 26, 18, .5)))


# ------------------------------------------------------------------ C04: Qinglong port
class C04(Clip):
    name, dur, step = "C04", 4.5, 8

    def frame(self, t, ts):
        world = map_world()
        k = smooth(seg(ts, 0.0, 1.3))
        v = View(lerp(560, 700, k), lerp(1000, 1180, k), lerp(1.0, 1.35, k))
        fr = v.bg(world)
        draw_route(fr, v, 1.0, ts)
        # coast town: houses + pagoda (paper cut)
        for (x, y, w_) in ((690, 1450, 120), (800, 1405, 100), (905, 1385, 110)):
            h_ = cached(("hs", w_), lambda w_=w_: finish(house(w_), edge=4, shadow=(8, 10, 10, .3)))
            px, py = v.pt(x, y)
            blit(fr, h_, px, py, scale=v.s, anchor=(0.5, 1.0))
        pg = cached(("pg",), lambda: finish(pagoda(230, 4, (112, 78, 54, 255)), edge=4, shadow=(8, 10, 10, .3)))
        px, py = v.pt(985, 1380)
        blit(fr, pg, px, py, scale=v.s, anchor=(.5, 1))
        # pier
        d = ImageDraw.Draw(fr, "RGBA")
        pier = [(620, 1590), (880, 1560), (900, 1590), (640, 1625)]
        d.polygon([v.pt(*p) for p in pier], fill=(150, 98, 56), outline=(60, 40, 28))
        for i in range(8):
            a = v.pt(640 + i * 32, 1612 - i * 6); b = v.pt(640 + i * 32, 1655 - i * 6)
            d.line([a, b], fill=(104, 66, 38), width=max(2, int(5 * v.s)))
        # waves
        for i in range(16):
            gx = 700 + (i % 4) * 90 + ((int(ts * 4) + i) % 3) * 6
            gy = 1640 + (i // 4) * 62
            ox, oy = v.pt(gx, gy)
            d.arc((ox, oy, ox + 60 * v.s, oy + 18 * v.s), 190, 350, fill=(255, 255, 255, 190), width=max(2, int(3 * v.s)))
        # ships
        sail_fill = smooth(seg(ts, 2.4, 3.1))
        depart = in_cubic(seg(ts, 2.9, 4.5))
        for j, (bx, by, ph0) in enumerate(((800, 1690, 0.0), (950, 1760, 0.3))):
            n_b = int(min(12, max(0, (ts - 1.0 - ph0) * 7))) if j == 0 else int(min(12, max(0, (ts - 1.5 - ph0) * 7)))
            sp = ship(round(sail_fill * (1.0 if j == 0 else (0.9 if ts > 3.0 else 0.0)), 1), n_b, flag=int(ts * 8) % 2)
            sx = bx + depart * (1000 + j * 120)
            sy = by - depart * 380 * (0.8 if j == 0 else 0.5) + math.sin(ts * 4 + j) * 4
            px, py = v.pt(sx, sy)
            fsp = cached(("shipf", round(sail_fill, 1) if j == 0 else (0.9 if ts > 3.0 else 0.0), n_b, int(ts * 8) % 2, j), lambda sp=sp: finish(sp, edge=5, shadow=(10, 14, 12, .3)))
            blit(fr, fsp, px, py, scale=v.s * 330 / 880, rot=math.sin(ts * 3 + j) * 2.5 - depart * 5, anchor=(.5, .85))
        # bowl stacks hop from the pier to the ship
        for i in range(3):
            t0 = 1.0 + i * 0.5
            q = seg(ts, t0, t0 + 0.55)
            if 0 < q < 1:
                x0, y0 = 700 + i * 45, 1560
                x1, y1 = 840 + i * 30, 1640
                bx_ = lerp(x0, x1, q); by_ = lerp(y0, y1, q) - math.sin(q * math.pi) * 120
                st = cached(("stf", 4), lambda: finish(stack(4, 74), edge=4, shadow=(8, 10, 10, .3)))
                px, py = v.pt(bx_, by_)
                blit(fr, st, px, py, scale=v.s * 0.8, rot=math.sin(q * 6) * 10)
            elif q <= 0:
                st = cached(("stf", 4), lambda: finish(stack(4, 74), edge=4, shadow=(8, 10, 10, .3)))
                px, py = v.pt(700 + i * 45, 1560)
                blit(fr, st, px, py, scale=v.s * 0.8)
        # tag
        tg = seg(ts, 0.9, 1.15)
        if tg > 0:
            tag = cached(("tag",), lambda: finish(tag_sprite("QINGLONG PORT"), edge=5, shadow=(8, 10, 10, .3)))
            px, py = v.pt(600, 1470)
            blit(fr, tag, px, py, scale=v.s * out_back(tg), rot=-4)
        # gulls
        for i in range(3):
            gx = (180 + i * 150 + ts * 70) % 1200 - 60
            gy = 1180 - i * 110 + math.sin(ts * 3 + i) * 12
            g = cached(("gull", int(ts * 8 + i) % 2), lambda: finish(gull(int(ts * 8 + i) % 2, 110), edge=0, shadow=(6, 8, 8, .0), rough=0))
            px, py = v.pt(gx, gy)
            blit(fr, g, px, py, scale=v.s)
        return final_grain(fr, 0.04)


def tag_sprite(text, size=44):
    f = font(F_BLACK, size)
    ts_ = text_sprite(text, f, PAL["brown"] + (255,), 0, None, pad=26)
    c = Cv(ts_.width + 20, ts_.height + 10, ss=1)
    c.rrect((0, 0, c.w - 1, c.h - 1), 18, (252, 242, 214, 255), (196, 120, 60, 255), 5)
    im = c.out()
    im.alpha_composite(ts_, (10, 5))
    return im
