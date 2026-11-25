"""Procedural paper-cut sprites: the Uncle doll, camel, ship, bun, steamer, dumpling, seal, etc.
All return RGBA PIL images already finished as cut paper (rim + shadow) unless noted."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from .core import *

OUT = PAL["brown"] + (255,)
CREAM = PAL["cream"] + (255,)
ORANGE = PAL["orange"] + (255,)
SKIN = (255, 214, 170, 255)
_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


# ------------------------------------------------------------------ faces
def draw_uncle_face(c, cx, cy, r, expr="happy", ink=OUT, skin=SKIN, blush=(255, 188, 160, 255), look=0):
    """Round bald face with a thin mustache. expr: happy | sleep | grin | proud | sweat | gasp"""
    c.ell((cx - r * 1.06, cy - r * 0.18, cx - r * 0.82, cy + r * 0.34), skin, ink, 3)        # ears
    c.ell((cx + r * 0.82, cy - r * 0.18, cx + r * 1.06, cy + r * 0.34), skin, ink, 3)
    c.ell((cx - r, cy - r, cx + r, cy + r * 1.02), skin, ink, 4)
    c.ell((cx - r * 0.45, cy - r * 0.9, cx + r * 0.1, cy - r * 0.6), (255, 238, 210, 200))   # bald shine
    for sx in (-1, 1):
        c.ell((cx + sx * r * 0.62 - r * 0.22, cy + r * 0.2, cx + sx * r * 0.62 + r * 0.22, cy + r * 0.46), blush)
    ey = cy - r * 0.05
    if expr in ("happy", "grin", "proud", "sleep"):
        for sx in (-1, 1):
            ex = cx + sx * r * 0.42
            if expr == "sleep":
                c.arc((ex - r * 0.2, ey - r * 0.12, ex + r * 0.2, ey + r * 0.2), 10, 170, ink, 4)
            else:
                c.arc((ex - r * 0.2, ey - r * 0.1, ex + r * 0.2, ey + r * 0.22), 190, 350, ink, 4)
    elif expr == "gasp":
        for sx in (-1, 1):
            ex = cx + sx * r * 0.42
            c.ell((ex - r * 0.17, ey - r * 0.2, ex + r * 0.17, ey + r * 0.2), CREAM, ink, 3)
            c.ell((ex - r * 0.07 + look * r * 0.06, ey - r * 0.08, ex + r * 0.07 + look * r * 0.06, ey + r * 0.08), ink)
    else:  # sweat: dots
        for sx in (-1, 1):
            ex = cx + sx * r * 0.42
            c.ell((ex - r * 0.07, ey - r * 0.07, ex + r * 0.07, ey + r * 0.09), ink)
    # nose + mustache
    c.ell((cx - r * 0.1, cy + r * 0.08, cx + r * 0.1, cy + r * 0.26), (255, 190, 150, 255), ink, 2)
    my = cy + r * 0.34
    for sx in (-1, 1):
        pts = [(cx + sx * r * 0.04, my), (cx + sx * r * 0.28, my + r * 0.04), (cx + sx * r * 0.52, my - r * 0.05), (cx + sx * r * 0.6, my - r * 0.14)]
        c.line(catmull(pts, 8), ink, max(3, r * 0.05))
    # mouth
    if expr in ("grin", "proud"):
        c.d.pieslice([v * c.ss for v in (cx - r * 0.34, my + r * 0.06, cx + r * 0.34, my + r * 0.62)], 0, 180, fill=(120, 40, 44, 255), outline=ink, width=3 * c.ss)
        c.ell((cx - r * 0.18, my + r * 0.3, cx + r * 0.18, my + r * 0.5), (236, 120, 120, 255))
    elif expr == "sleep":
        c.ell((cx - r * 0.12, my + r * 0.14, cx + r * 0.12, my + r * 0.4), (120, 40, 44, 255), ink, 3)
    elif expr == "gasp":
        c.ell((cx - r * 0.2, my + r * 0.1, cx + r * 0.2, my + r * 0.52), (120, 40, 44, 255), ink, 3)
    elif expr == "sweat":
        c.line(catmull([(cx - r * 0.25, my + r * 0.3), (cx, my + r * 0.2), (cx + r * 0.25, my + r * 0.3)], 8), ink, 4)
    else:
        c.arc((cx - r * 0.3, my - r * 0.05, cx + r * 0.3, my + r * 0.5), 20, 160, ink, 4)


def uncle_doll(pose="stand", expr="happy", w=520, kimono=None, belt=None, extra=None, arm_l=(150, 1), arm_r=(30, 1),
               fingers_r=0, point_r=False, cape=False, seed=1):
    """Full Uncle as a flat paper doll (front view), design box 520x760. arm_*=(angle_deg_from_down, length scale).
    pose: stand | sit | sleep. Returns UNFINISHED RGBA (caller finishes / tints)."""
    key = ("uncle", pose, expr, w, kimono, belt, tuple(arm_l), tuple(arm_r), fingers_r, point_r, cape)
    def build():
        S = 2
        kimono_c = kimono or CREAM
        belt_c = belt or ORANGE
        c = Cv(860, 800, ss=2)
        cx = 430
        # legs + sandals
        if pose == "stand":
            for sx in (-1, 1):
                c.rrect((cx + sx * 70 - 50, 560, cx + sx * 70 + 50, 700), 40, kimono_c, OUT, 4)
                c.rrect((cx + sx * 70 - 64, 690, cx + sx * 70 + 64, 730), 18, (214, 160, 96, 255), OUT, 4)
        elif pose == "sit":
            for sx in (-1, 1):
                c.rrect((cx + sx * 80 - 48, 520, cx + sx * 80 + 48, 680), 42, kimono_c, OUT, 4)
                c.rrect((cx + sx * 80 - 62, 670, cx + sx * 80 + 62, 712), 18, (214, 160, 96, 255), OUT, 4)
        # arms behind body
        def arm(side, ang, ln, back=True):
            sh = (cx + side * 175, 330)
            a = math.radians(ang)
            L = 230 * ln
            ex, ey = sh[0] + math.sin(a) * L * side, sh[1] + math.cos(a) * L
            c.line([sh, (ex, ey)], OUT, 100)
            c.line([sh, (ex, ey)], kimono_c, 92)
            c.ell((ex - 46, ey - 46, ex + 46, ey + 46), kimono_c, OUT, 4)
            return ex, ey
        ax_l = arm(-1, arm_l[0], arm_l[1])
        # body
        c.ell((cx - 205, 270, cx + 205, 640), kimono_c, OUT, 5)
        c.line([(cx - 40, 290), (cx + 25, 430), (cx + 110, 330)], OUT, 4)                   # V collar
        c.line([(cx + 25, 430), (cx + 30, 520)], OUT, 3)
        # sauce stains
        for (sx_, sy_, rr) in ((-90, 380, 16), (110, 440, 20), (-40, 560, 14), (60, 330, 11)):
            c.ell((cx + sx_ - rr, sy_ - rr * .8, cx + sx_ + rr, sy_ + rr * .8), (214, 110, 40, 255))
            c.ell((cx + sx_ + rr * .5, sy_ + rr * .9, cx + sx_ + rr * 0.9, sy_ + rr * 1.3), (214, 110, 40, 255))
        # belt + knot
        c.rrect((cx - 200, 470, cx + 200, 535), 24, belt_c, OUT, 4)
        c.ell((cx + 20, 462, cx + 100, 542), belt_c, OUT, 4)
        c.poly([(cx + 40, 520), (cx + 110, 520), (cx + 120, 640), (cx + 70, 620), (cx + 30, 650)], belt_c, OUT, 4)
        ax_r = arm(1, arm_r[0], arm_r[1])
        # hands
        if fingers_r:
            ex, ey = ax_r
            for i in range(fingers_r):
                fx = ex + (i - (fingers_r - 1) / 2) * 34 - 2
                c.rrect((fx - 15, ey - 120, fx + 15, ey - 20), 15, SKIN, OUT, 4)
            c.ell((ex - 42, ey - 50, ex + 42, ey + 36), SKIN, OUT, 4)
        elif point_r:
            ex, ey = ax_r
            c.ell((ex - 42, ey - 40, ex + 42, ey + 44), SKIN, OUT, 4)
            c.rrect((ex, ey - 22, ex + 110, ey + 4), 13, SKIN, OUT, 4)
        else:
            ex, ey = ax_r
            c.ell((ex - 40, ey - 40, ex + 40, ey + 40), SKIN, OUT, 4)
        ex, ey = ax_l
        c.ell((ex - 40, ey - 40, ex + 40, ey + 40), SKIN, OUT, 4)
        # head
        draw_uncle_face(c, cx, 190, 125, expr)
        im = c.out()
        return im
    im = cached(key, build)
    sc = w / 520.0
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)


def uncle_hand_pos(side, ang, ln):
    """Hand position in the 760x800 doll design box."""
    a = math.radians(ang)
    return (430 + side * 175 + math.sin(a) * 230 * ln * side, 330 + math.cos(a) * 230 * ln)


# ------------------------------------------------------------------ camel
def camel(phase=0, head="side", colors=None, rider=False, blink=False, size=460):
    """Side-view paper camel walking right. phase 0..3 = walk cycle frame. head: side | front | down"""
    key = ("camel", phase, head, rider, blink, size)
    def build():
        base, dark, light = (206, 150, 86, 255), (160, 106, 58, 255), (236, 190, 120, 255)
        c = Cv(560, 460, ss=2)
        # legs (4) with simple walk offsets
        sw = [(-16, 10), (12, -10), (16, -8), (-14, 12)]
        legs_x = [150, 205, 360, 415]
        for i, lx in enumerate(legs_x):
            a = math.sin((phase / 4 + i * 0.25 + (0.5 if i % 2 else 0)) * 2 * math.pi) * 20
            top = (lx, 300); bot = (lx + a, 430)
            c.line([top, ((top[0] + bot[0]) / 2 + a * 0.2, 365), bot], dark if i in (0, 2) else base, 30)
            c.ell((bot[0] - 20, bot[1] - 8, bot[0] + 20, bot[1] + 14), (120, 80, 48, 255), OUT, 3)
        # tail
        c.line(catmull([(95, 230), (60, 260), (58, 310), (72, 336)], 8), dark, 12)
        c.ell((60, 322, 92, 356), dark)
        # body + humps
        c.ell((100, 190, 470, 350), base, OUT, 5)
        c.ell((170, 120, 290, 240), base, OUT, 5)
        c.ell((300, 120, 420, 240), base, OUT, 5)
        c.ell((110, 200, 460, 346), base)  # cover seams
        c.ell((190, 140, 270, 200), light)
        # blanket
        c.poly([(205, 205), (385, 205), (395, 300), (195, 300)], ORANGE, OUT, 4)
        for k in range(5):
            c.poly([(205 + k * 38, 300), (225 + k * 38, 300), (215 + k * 38, 318)], PAL["yellow"] + (255,), OUT, 2)
        c.rrect((205, 232, 385, 250), 4, PAL["yellow"] + (255,))
        c.rrect((205, 262, 385, 276), 4, CREAM)
        # neck + head
        neck = [(430, 230), (470, 150), (480, 95)] if head != "down" else [(430, 230), (480, 215), (505, 240)]
        c.line(catmull(neck, 8), base, 58)
        c.line(catmull(neck, 8), OUT, 3)
        if head == "front":
            hx, hy = 480, 88
            c.ell((hx - 52, hy - 52, hx + 52, hy + 52), base, OUT, 4)
            c.ell((hx - 56, hy - 66, hx - 34, hy - 30), base, OUT, 3)
            c.ell((hx + 34, hy - 66, hx + 56, hy - 30), base, OUT, 3)
            c.ell((hx - 38, hy + 6, hx + 38, hy + 60), light, OUT, 3)
            c.ell((hx - 20, hy + 26, hx - 8, hy + 40), OUT); c.ell((hx + 8, hy + 26, hx + 20, hy + 40), OUT)
            for sx in (-1, 1):
                ex = hx + sx * 24
                c.ell((ex - 14, hy - 22, ex + 14, hy + 8), CREAM, OUT, 3)
                if blink:
                    c.line([(ex - 14, hy - 8), (ex + 14, hy - 8)], OUT, 4)
                else:
                    c.ell((ex - 6, hy - 14, ex + 6, hy), OUT)
            c.line([(hx - 20, hy - 34), (hx - 5, hy - 40)], OUT, 3)
        else:
            hx, hy = (488, 78) if head == "side" else (520, 230)
            c.ell((hx - 44, hy - 36, hx + 44, hy + 40), base, OUT, 4)
            c.ell((hx + 8, hy - 2, hx + 66, hy + 44), light, OUT, 4)
            c.ell((hx - 22, hy - 52, hx - 4, hy - 20), base, OUT, 3)
            c.ell((hx + 44, hy + 14, hx + 52, hy + 24), OUT)
            if blink:
                c.line([(hx - 8, hy - 8), (hx + 10, hy - 8)], OUT, 4)
            else:
                c.ell((hx - 6, hy - 16, hx + 8, hy), OUT)
        # bells
        c.ell((300, 292, 318, 312), PAL["yellow"] + (255,), OUT, 2)
        im = c.out()
        return im
    im = cached(key, build)
    return im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)


# ------------------------------------------------------------------ small props
def bowl(w=90, rim=ORANGE, body=CREAM):
    def build():
        h = int(w * .62)
        c = Cv(w, h, ss=3)
        pts = [(w / 2 + math.cos(a) * (w / 2 - 3), 4 + math.sin(a) * (h - 10)) for a in [i / 30 * math.pi for i in range(31)]]
        c.poly(pts, body, OUT, 3)
        c.rrect((3, 2, w - 3, 16), 7, rim, OUT, 3)
        c.line([(w * .22, h * .45), (w * .78, h * .45)], rim, 3)
        c.rrect((w * .3, h * .86, w * .7, h * .98), 4, body, OUT, 2)
        return c.out()
    return cached(("bowl", w, rim, body), build)


def xlb(d=120, glow=0.0, pleats=18, gold=False):
    """Top-down soup dumpling: round skin, spiral pleats and a top knot."""
    def build():
        S = 3
        c = Cv(d, d, ss=S)
        r = d / 2 - 3
        col = (255, 236, 196, 255) if not gold else (252, 214, 118, 255)
        c.ell((d / 2 - r, d / 2 - r, d / 2 + r, d / 2 + r), col, OUT, 3)
        for i in range(pleats):
            a = i / pleats * 2 * math.pi
            p0 = (d / 2 + math.cos(a + 0.8) * r * 0.22, d / 2 + math.sin(a + 0.8) * r * 0.22)
            p1 = (d / 2 + math.cos(a + 0.35) * r * 0.62, d / 2 + math.sin(a + 0.35) * r * 0.62)
            p2 = (d / 2 + math.cos(a) * r * 0.93, d / 2 + math.sin(a) * r * 0.93)
            c.line(catmull([p0, p1, p2], 6), (190, 140, 84, 255) if not gold else (178, 110, 30, 255), max(2, d / 90))
        c.ell((d / 2 - r * 0.2, d / 2 - r * 0.2, d / 2 + r * 0.2, d / 2 + r * 0.2), (250, 224, 176, 255) if not gold else (255, 232, 150, 255), OUT, 2)
        c.ell((d * 0.3, d * 0.2, d * 0.44, d * 0.3), (255, 255, 255, 140))
        return c.out()
    return cached(("xlb", d, gold, pleats), build)


def steamer_basket(w=300, lid=True):
    def build():
        h = int(w * 0.62)
        c = Cv(w, h, ss=2)
        c.rrect((6, h * .28, w - 6, h - 6), 26, PAL["bamboo"] + (255,), OUT, 4)
        for i in range(1, 7):
            x = 6 + i * (w - 12) / 7
            c.line([(x, h * .3), (x, h - 10)], (176, 128, 64, 255), 3)
        c.line([(10, h * .62), (w - 10, h * .62)], (176, 128, 64, 255), 4)
        if lid:
            c.ell((0, 4, w, h * .52), (230, 188, 108, 255), OUT, 4)
            c.ell((w * .38, 0, w * .62, h * .13), (186, 134, 70, 255), OUT, 3)
        return c.out()
    return cached(("steamer", w, lid), build)


def seal_sprite(text=("LEGEND", "SAYS"), size=520, ast=False):
    """Red ink stamp, rough edges, white letters."""
    def build():
        c = Cv(size, size, ss=2)
        red = PAL["vermilion"] + (255,)
        m = size * .04
        c.rrect((m, m, size - m, size - m), size * .08, red)
        c.rrect((m + size * .035, m + size * .035, size - m - size * .035, size - m - size * .035), size * .05, None, (255, 235, 215, 255), 6)
        f = font(F_BLACK, int(size * .215))
        cv2_ = c
        c.text((size / 2, size * .36), text[0], f, (255, 240, 222, 255), "mm")
        c.text((size / 2, size * .64), text[1], f, (255, 240, 222, 255), "mm")
        # ink speckle
        g = np.random.default_rng(4)
        im = c.out()
        a = np.asarray(im).copy()
        sp = g.random(a.shape[:2]) < 0.05
        a[..., 3] = np.where(sp & (a[..., 0] > 180) & (a[..., 1] < 80), (a[..., 3] * 0.2).astype(np.uint8), a[..., 3])
        im = Image.fromarray(a, "RGBA")
        return im
    return cached(("seal", text, size), build)


def paper_dragon(t, size=420, steps=14):
    """Tiny dragon made of steam puffs: a head with whiskers and a trailing coil."""
    c = Cv(size, size, ss=2)
    pts = []
    for i in range(steps):
        u = i / steps
        ang = u * 5.2 - t * 3.0
        rr = size * (0.06 + 0.32 * (1 - u) * 0.9)
        pts.append((size * 0.5 + math.cos(ang) * rr + (u - .5) * size * .2, size * 0.7 - u * size * 0.55 + math.sin(ang * 1.3) * rr * 0.25))
    for i in range(steps - 1, -1, -1):
        u = i / steps
        r = size * (0.045 + 0.05 * (1 - u))
        x, y = pts[i]
        c.ell((x - r, y - r, x + r, y + r), (255, 248, 232, 255), (214, 190, 150, 255), 2)
    hx, hy = pts[0]
    c.ell((hx - 28, hy - 24, hx + 28, hy + 24), (255, 250, 236, 255), OUT, 3)
    c.ell((hx - 11, hy - 10, hx - 3, hy - 2), OUT); c.ell((hx + 3, hy - 10, hx + 11, hy - 2), OUT)
    c.line(catmull([(hx - 24, hy + 6), (hx - 50, hy + 14), (hx - 62, hy + 4)], 6), OUT, 3)
    c.line(catmull([(hx + 24, hy + 6), (hx + 50, hy + 14), (hx + 62, hy + 4)], 6), OUT, 3)
    c.poly([(hx - 10, hy - 22), (hx - 2, hy - 44), (hx + 6, hy - 22)], ORANGE, OUT, 2)
    return c.out()


def hand(side=1, size=300, pointing=False, sleeve=True):
    """A Boy's hand + white kimono sleeve, coming in from the bottom. pointing=True: index finger out, others curled, thumb up
    (rotate it when drawing); False: open flat hand."""
    def build():
        c = Cv(size, int(size * 1.6), ss=2)
        w, h = size, int(size * 1.6)
        c.rrect((w * .1, h * .56, w * .9, h + 40), 40, CREAM, OUT, 4)
        c.line([(w * .1, h * .66), (w * .9, h * .66)], (220, 205, 180, 255), 3)
        if pointing:
            c.rrect((w * .2, h * .3, w * .8, h * .62), 60, SKIN, OUT, 4)
            c.rrect((w * .2, h * .06, w * .38, h * .44), 28, SKIN, OUT, 4)          # index, outer edge
            for i in range(3):                                                        # curled fingers
                x = w * (.4 + i * .12)
                c.rrect((x, h * .27 + i * 5, x + w * .14, h * .4 + i * 5), 20, SKIN, OUT, 3)
            c.rrect((w * .62, h * .36, w * .92, h * .5), 26, SKIN, OUT, 4)           # thumb across
        else:
            c.rrect((w * .2, h * .24, w * .8, h * .62), 60, SKIN, OUT, 4)
            for i in range(4):
                x = w * (.24 + i * .13)
                c.rrect((x, h * .02 + abs(i - 1.5) * 18, x + w * .12, h * .4), 24, SKIN, OUT, 3)
            c.rrect((w * .06, h * .3, w * .26, h * .52), 28, SKIN, OUT, 4)
        return c.out()
    return cached(("hand", side, size, pointing), build)


def sun(size=300, phase=0):
    c = Cv(size, size, ss=2)
    cx = size / 2
    n = 14
    for i in range(n):
        a = (i / n + phase / n * 0.5) * 2 * math.pi
        r0, r1 = size * .30, size * (0.48 if i % 2 == 0 else 0.42)
        w = 0.1
        c.poly([(cx + math.cos(a - w) * r0, cx + math.sin(a - w) * r0), (cx + math.cos(a) * r1, cx + math.sin(a) * r1), (cx + math.cos(a + w) * r0, cx + math.sin(a + w) * r0)], PAL["orange"] + (255,))
    c.ell((cx - size * .3, cx - size * .3, cx + size * .3, cx + size * .3), PAL["yellow"] + (255,), (200, 120, 40, 255), 4)
    c.ell((cx - size * .2, cx - size * .24, cx - size * .02, cx - size * .1), (255, 236, 170, 200))
    return c.out()


def gull(phase=0, size=90):
    c = Cv(size, int(size * .5), ss=3)
    up = (phase % 2 == 0)
    pts = [(2, size * .32 if up else size * .08), (size * .25, size * .1 if up else size * .26), (size * .5, size * .28), (size * .75, size * .1 if up else size * .26), (size - 2, size * .32 if up else size * .08)]
    c.line(catmull(pts, 8), (250, 246, 236, 255), 8)
    return c.out()


def ship(fill=0.0, bowls=0, size=420, flag=0):
    """Paper junk ship facing right. fill 0..1 = how full the batten sail is."""
    key = ("ship", round(fill, 1), bowls, size, flag)
    def build():
        c = Cv(420, 420, ss=2)
        wood, dk = (150, 98, 56, 255), (104, 66, 38, 255)
        # sail
        bulge = 8 + 46 * fill
        left = 120
        pts = [(210, 52), (210 + 150 - (1 - fill) * 50, 60)]
        for i in range(0, 11):
            u = i / 10
            pts.append((210 + 150 - (1 - fill) * 50 + math.sin(u * math.pi) * bulge, 60 + u * 190))
        pts += [(210, 250)]
        c.poly(pts, (238, 96, 44, 255), OUT, 4)
        for k in range(1, 5):
            y = 60 + k * 38
            xe = 210 + 150 - (1 - fill) * 50 + math.sin((k * 38 / 190) * math.pi) * bulge
            c.line([(210, y), (xe, y)], (160, 52, 20, 255), 4)
        c.line([(210, 40), (210, 300)], dk, 10)
        c.poly([(210, 40), (250, 48 + flag * 6), (210, 62)], PAL["vermilion"] + (255,), OUT, 2)
        # hull
        hull = [(36, 296), (392, 296), (372, 340), (330, 380), (100, 380), (60, 340)]
        c.poly(hull, wood, OUT, 5)
        c.poly([(44, 306), (384, 306), (378, 322), (52, 322)], PAL["orange"] + (255,))
        c.line([(80, 352), (350, 352)], dk, 4)
        c.poly([(392, 296), (420, 270), (396, 310)], dk, OUT, 3)
        c.rrect((60, 262, 150, 300), 6, dk, OUT, 3)
        c.poly([(54, 262), (156, 262), (140, 244), (70, 244)], PAL["orange"] + (255,), OUT, 3)
        for i in range(bowls):
            x = 170 + (i % 6) * 34; y = 292 - (i // 6) * 22
            c.rrect((x, y - 18, x + 30, y + 4), 7, CREAM, OUT, 2)
            c.rrect((x, y - 20, x + 30, y - 12), 4, ORANGE, OUT, 2)
        return c.out(2)
    im = cached(key, build)
    return im


def stack(n=4, w=74):
    """A stack of paper bowls (upside down) for loading."""
    def build():
        h = 18 * n + 14
        c = Cv(w, h, ss=3)
        for i in range(n):
            y = h - 14 - (i + 1) * 17
            c.rrect((4, y, w - 4, y + 24), 9, CREAM, OUT, 2)
            c.rrect((4, y + 12, w - 4, y + 24), 6, ORANGE, OUT, 2)
        return c.out()
    return cached(("stack", n, w), build)


def house(w=150, roof=(150, 70, 44), body=(246, 232, 200), seed=0):
    def build():
        h = int(w * .95)
        c = Cv(w, h, ss=2)
        c.rrect((w * .12, h * .38, w * .88, h - 4), 5, body + (255,), OUT, 4)
        c.poly([(0, h * .42), (w, h * .42), (w * .84, h * .08), (w * .16, h * .08)], roof + (255,), OUT, 4)
        c.rrect((w * .4, h * .58, w * .62, h - 4), 4, (110, 76, 48, 255), OUT, 3)
        c.rrect((w * .2, h * .52, w * .34, h * .68), 3, (255, 214, 130, 255), OUT, 2)
        return c.out()
    return cached(("house", w, roof, body), build)


def cloud(w=260, col=(252, 244, 226, 255)):
    def build():
        h = int(w * .45)
        c = Cv(w, h, ss=2)
        c.rrect((w * .05, h * .4, w * .95, h * .95), h * .28, col)
        c.ell((w * .16, h * .12, w * .5, h * .72), col); c.ell((w * .38, 0, w * .76, h * .7), col); c.ell((w * .6, h * .22, w * .9, h * .72), col)
        return c.out()
    return cached(("cloud", w, col), build)


def journal_closed(w=820, h=1100):
    def build():
        c = Cv(w, h, ss=2)
        lea = (116, 66, 36, 255)
        c.rrect((6, 6, w - 6, h - 6), 40, lea, OUT, 6)
        c.rrect((6, 6, w * .09, h - 6), 36, (92, 50, 28, 255), OUT, 6)
        # stitched border
        m = 50
        for i in range(0, 60):
            u = i / 60
            for (x0, y0, x1, y1) in ((w * .13 + (w * .8 - m) * u, m, w * .13 + (w * .8 - m) * u + 14, m), (w * .13 + (w * .8 - m) * u, h - m, w * .13 + (w * .8 - m) * u + 14, h - m)):
                c.line([(x0, y0), (x1, y1)], (230, 190, 120, 255), 5, False)
        for i in range(0, 80):
            y = m + (h - 2 * m) * i / 80
            c.line([(w - m, y), (w - m, y + 14)], (230, 190, 120, 255), 5, False)
        # emblem: round dumpling with a hat
        cx, cy = w * .55, h * .42
        c.ell((cx - 150, cy - 150, cx + 150, cy + 150), (160, 98, 56, 255), (230, 190, 120, 255), 6)
        c.poly([(cx - 130, cy + 10), (cx, cy - 150), (cx + 130, cy + 10)], (236, 198, 106, 255), OUT, 5)
        c.arc((cx - 100, cy - 10, cx + 100, cy + 90), 20, 160, (255, 250, 240, 255), 8)
        # strap
        c.rrect((w * .75, h * .28, w + 4, h * .36), 14, ORANGE, OUT, 5)
        c.ell((w * .72, h * .27, w * .79, h * .37), (236, 198, 106, 255), OUT, 4)
        return c.out()
    return cached(("jc", w, h), build)


# ------------------------------------------------------------------ legend cast and props
LEG_SKIN = (238, 190, 140, 255)


def bun_big(w=420, steam=0):
    """A (giant) meat bun: dome, pleat swirl, soft shading. Unfinished RGBA."""
    key = ("bunbig", w)
    def build():
        c = Cv(w, int(w * .86), ss=2)
        h = int(w * .86)
        c.ell((6, h * .12, w - 6, h - 6), (252, 232, 190, 255), OUT, 5)
        c.ell((w * .1, h * .62, w * .9, h - 10), (226, 192, 142, 255))
        c.ell((6, h * .12, w - 6, h * .92), None, OUT, 5)
        for i in range(16):
            a = i / 16 * 2 * math.pi
            p0 = (w / 2 + math.cos(a + .6) * w * .06, h * .42 + math.sin(a + .6) * h * .05)
            p1 = (w / 2 + math.cos(a + .25) * w * .28, h * .42 + math.sin(a + .25) * h * .2)
            p2 = (w / 2 + math.cos(a) * w * .43, h * .46 + math.sin(a) * h * .33)
            c.line(catmull([p0, p1, p2], 6), (196, 150, 98, 255), max(2, w / 90))
        c.ell((w * .22, h * .2, w * .46, h * .32), (255, 250, 235, 170))
        return c.out()
    im = cached(key, build)
    return im


def bun_hero(w=200, arms=True):
    """Small bun with two stick arms raised and a tiny cape, a hero pose."""
    def build():
        c = Cv(w * 2, int(w * 1.7), ss=2)
        cx = w
        c.poly([(cx - 40, 50), (cx + 40, 50), (cx + 110, 330), (cx - 110, 330)], PAL["vermilion"] + (255,), OUT, 4)
        c.line([(cx - 60, 190), (cx - 120, 100)], OUT, 12); c.line([(cx + 60, 190), (cx + 120, 100)], OUT, 12)
        c.ell((cx - 20 - 100, 85, cx + 8 - 100, 113), CREAM, OUT, 3); c.ell((cx + 100 - 8, 85, cx + 100 + 20, 113), CREAM, OUT, 3)
        b = bun_big(int(w * 1.2))
        c.im.alpha_composite(b.resize((int(w * 1.2 * 2), int(w * 1.2 * .86 * 2))), (int((w * 2 - w * 1.2 * 2) / 2), int(w * 1.7 * 2 - w * 1.2 * .86 * 2 - 10)))
        by = w * 1.7 - w * 1.2 * .86 - 5
        for sx in (-1, 1):
            c.ell((cx + sx * 34 - 6, by + 62, cx + sx * 34 + 6, by + 74), OUT)
        c.arc((cx - 16, by + 70, cx + 16, by + 92), 20, 160, OUT, 4)
        return c.out()
    return cached(("bunhero", w), build)


def customer(w=300, shrug=0.0, look=0):
    """Small paper villager: robe, round head, topknot; shrug 0..1 raises the shoulders."""
    c = Cv(w, int(w * 1.7), ss=2)
    h = int(w * 1.7)
    cx = w / 2
    robe = (206, 140, 96, 255)
    c.poly([(cx - w * .26, h * .34), (cx + w * .26, h * .34), (cx + w * .38, h - 8), (cx - w * .38, h - 8)], robe, OUT, 4)
    c.rrect((cx - w * .3, h * .62, cx + w * .3, h * .7), 6, PAL["vermilion"] + (255,), OUT, 3)
    sh = shrug * 26
    for sx in (-1, 1):
        c.line([(cx + sx * w * .24, h * .4 - sh), (cx + sx * w * .36, h * .58 - sh * .5), (cx + sx * w * .18, h * .64)], robe, w * .14)
        c.ell((cx + sx * w * .18 - 14, h * .62, cx + sx * w * .18 + 14, h * .68), LEG_SKIN, OUT, 3)
    c.ell((cx - w * .2, h * .09 + look * 4, cx + w * .2, h * .33 + look * 4), LEG_SKIN, OUT, 4)
    c.ell((cx - w * .07, h * .02 + look * 4, cx + w * .07, h * .1 + look * 4), (70, 44, 34, 255), OUT, 3)
    for sx in (-1, 1):
        c.ell((cx + sx * w * .08 - 6, h * .2 + look * 4, cx + sx * w * .08 + 6, h * .245 + look * 4), OUT)
    c.line([(cx - w * .06, h * .28 + look * 4), (cx + w * .06, h * .28 + look * 4)], OUT, 3)
    return c.out()


def rooster(crow=False, w=240):
    c = Cv(w, w, ss=2)
    c.ell((w * .22, w * .42, w * .74, w * .86), (214, 96, 46, 255), OUT, 4)
    for i, a in enumerate((-50, -25, 0, 25)):
        ang = math.radians(a - 100)
        c.poly([(w * .26, w * .55), (w * .26 + math.cos(ang) * w * .4 - 14, w * .55 + math.sin(ang) * w * .5), (w * .26 + math.cos(ang) * w * .4 + 14, w * .55 + math.sin(ang) * w * .5)], [(150, 50, 28, 255), (226, 150, 40, 255), (196, 70, 30, 255), (240, 180, 60, 255)][i], OUT, 3)
    hy = w * (.2 if not crow else .12)
    c.line([(w * .62, w * .52), (w * .7, hy + w * .14)], (214, 96, 46, 255), w * .13)
    c.ell((w * .6, hy, w * .84, hy + w * .24), (240, 140, 70, 255), OUT, 4)
    c.poly([(w * .62, hy - 4), (w * .66, hy - w * .1), (w * .7, hy), (w * .74, hy - w * .09), (w * .78, hy)], PAL["vermilion"] + (255,), OUT, 3)
    by = hy + w * .1
    if crow:
        c.poly([(w * .83, by - 10), (w * .98, by - 22), (w * .84, by)], (240, 190, 60, 255), OUT, 3)
        c.poly([(w * .83, by + 2), (w * .97, by + 16), (w * .84, by + 8)], (240, 190, 60, 255), OUT, 3)
    else:
        c.poly([(w * .83, by - 6), (w * .97, by + 4), (w * .83, by + 8)], (240, 190, 60, 255), OUT, 3)
    c.ell((w * .74, hy + w * .06, w * .78, hy + w * .1), OUT)
    c.line([(w * .4, w * .86), (w * .4, w * .98)], (200, 150, 50, 255), 6); c.line([(w * .56, w * .86), (w * .56, w * .98)], (200, 150, 50, 255), 6)
    return c.out()


def rolling_pin(l=420, w=44):
    c = Cv(l, w + 20, ss=2)
    c.rrect((36, 6, l - 36, w + 14), 16, (222, 170, 100, 255), OUT, 4)
    c.rrect((4, w / 2 - 2, 44, w / 2 + 22), 8, (180, 120, 70, 255), OUT, 3)
    c.rrect((l - 44, w / 2 - 2, l - 4, w / 2 + 22), 8, (180, 120, 70, 255), OUT, 3)
    return c.out()


def knife(l=360):
    c = Cv(l, 90, ss=2)
    c.poly([(0, 30), (l * .72, 22), (l * .76, 60), (0, 60)], (214, 220, 224, 255), OUT, 4)
    c.rrect((l * .74, 26, l, 62), 10, (150, 88, 50, 255), OUT, 4)
    return c.out()


def jelly(w=520, h=360, wob=0.0):
    c = Cv(w + 60, h + 60, ss=2)
    c.rrect((30, 30, w + 30, h + 30), 54, (236, 160, 46, 255), (170, 96, 20, 255), 6)
    c.rrect((54, 50, w * .55, h * .38), 40, (252, 206, 110, 200))
    g = np.random.default_rng(2)
    for _ in range(14):
        x, y, r = g.uniform(90, w - 20), g.uniform(90, h - 10), g.uniform(5, 14)
        c.ell((x - r, y - r, x + r, y + r), (252, 214, 130, 200))
    return c.out()


def petal(sz=34, col=(214, 84, 70, 255)):
    c = Cv(sz, sz, ss=3)
    c.ell((sz * .1, sz * .3, sz * .9, sz * .7), col)
    return c.out()


def cape(w=420, h=520, t=0, col=None):
    col = col or (PAL["vermilion"] + (255,))
    c = Cv(w, h, ss=2)
    pts = [(w * .38, 0), (w * .62, 0)]
    for i in range(9):
        u = i / 8
        pts.append((w * (.66 + .3 * u) + math.sin(t * 3 + u * 4) * w * .05, h * u))
    pts.append((w * .96 + math.sin(t * 3 + 4.5) * 12, h))
    for i in range(8, -1, -1):
        u = i / 8
        pts.append((w * (.34 - .3 * u) + math.sin(t * 3 + u * 4 + 1.5) * w * .05, h * u * (1 if i < 8 else 1) + (14 * math.sin(t * 5 + i) if i else 0)))
    c.poly(pts, col, OUT, 4)
    return c.out()
