"""Animated paper-cut TV graphics for the edit: lower-third, intermission, safety sign, step word cards, rating card,
recap tab, next-episode tab and sound-words. Used by make_episode.py through card {"type": "paper", "kind": ...}."""
import math
from PIL import Image, ImageDraw
from .core import *
from .shapes import cached, finish, OUT, CREAM, ORANGE

BR, OR, YE, CR = PAL["brown"] + (255,), PAL["orange"] + (255,), PAL["yellow"] + (255,), PAL["cream"] + (255,)


def _lower_third(text, text2):
    w, h = 880, 190
    c = Cv(w, h, ss=2)
    c.rrect((6, 14, w - 6, h - 6), 30, (255, 246, 224, 255), OR, 7)
    c.rrect((6, 14, 250, h - 6), 30, OR)
    c.rrect((200, 14, 250, h - 6), 0, OR)
    c.text((128, h / 2 + 4), text, font(F_BLACK, 48), CR, "mm")
    c.text((270, h / 2 + 4), text2, font(F_BOLD, 44), BR, "lm")
    return finish(c.out(), edge=4, shadow=(8, 12, 10, .35), rough=.8)


def _intermission():
    w, h = 940, 640
    c = Cv(w, h, ss=2)
    c.rrect((8, 8, w - 8, h - 8), 46, (255, 248, 232, 255), BR, 8)
    cols = [(236, 198, 106), (255, 250, 240), (217, 72, 15), (59, 42, 26), (255, 227, 184), (150, 190, 200), (200, 140, 90)]
    bw = (w - 120) / len(cols)
    for i, col in enumerate(cols):
        c.rrect((60 + i * bw, 50, 60 + (i + 1) * bw - 4, 170), 6, col + (255,))
    for i, s in enumerate(("PLEASE ENJOY", "THIS BRIEF", "INTERMISSION")):
        c.text((w / 2, 270 + i * 110), s, font(F_BLACK, 92 if i != 2 else 82), BR if i != 2 else OR, "mm")
    c.text((w / 2, 590), "please stand by", font(F_BOLD, 36), (150, 110, 80, 255), "mm")
    return finish(c.out(), edge=5, shadow=(10, 16, 14, .4), rough=.9)


def _safety():
    w, h = 960, 330
    c = Cv(w, h, ss=2)
    c.rrect((6, 6, w - 6, h - 6), 36, YE, BR, 8)
    for i in range(-2, 30):
        x = 30 + i * 70
        c.poly([(x, 24), (x + 36, 24), (x + 6, 70), (x - 30, 70)], BR)
        c.poly([(x, h - 70), (x + 36, h - 70), (x + 6, h - 24), (x - 30, h - 24)], BR)
    c.rrect((34, 74, w - 34, h - 74), 18, (255, 250, 240, 255))
    c.text((w / 2, h / 2 + 2), "SAFETY SEGMENT", font(F_BLACK, 100), OR, "mm")
    return finish(c.out(), edge=5, shadow=(10, 16, 14, .4), rough=.8)


def _fineprint():
    t = "brought to you by Uncle's tongue"
    f = font(F_BOLD, 44)
    sp = text_sprite(t, f, BR, pad=34)
    c = Cv(sp.width, sp.height + 10, ss=1)
    c.rrect((0, 0, c.w - 1, c.h - 1), 22, (255, 250, 238, 255), OR, 5)
    im = c.out(); im.alpha_composite(sp, (0, 5))
    return finish(im, edge=4, shadow=(6, 10, 10, .3), rough=.6)


def _step(text):
    f = font(F_BLACK, 150 if len(text) < 7 else 118)
    sp = text_sprite(text, f, CR, 12, BR, pad=40)
    c = Cv(sp.width + 40, sp.height + 30, ss=1)
    c.rrect((0, 0, c.w - 1, c.h - 1), 44, OR, BR, 8)
    im = c.out(); im.alpha_composite(sp, (20, 15))
    return finish(im, edge=5, shadow=(8, 14, 12, .4), rough=.8)


def _rating(text="10/10"):
    w, h = 640, 440
    c = Cv(w, h, ss=2)
    c.rrect((6, 6, w - 6, h - 6), 26, (255, 250, 236, 255), BR, 6)
    c.ell((90, 60, w - 90, h - 60), None, PAL["vermilion"] + (255,), 10)
    c.text((w / 2, h / 2 + 6), text, font(F_BLACK, 160), BR, "mm")
    return finish(c.out(), edge=5, shadow=(8, 12, 12, .4), rough=1.2)


def _tab(lines, col=OR, fill=(255, 246, 224, 255), size=52):
    sps = [text_sprite(s, font(F_BLACK, size if i == 0 else int(size * .62)), col if i == 0 else BR, 0, None, pad=14) for i, s in enumerate(lines)]
    w = max(s.width for s in sps) + 70
    h = sum(s.height for s in sps) + 40
    c = Cv(w, h, ss=1)
    c.rrect((0, 0, w - 1, h - 1), 30, fill, OR, 6)
    im = c.out(); y = 20
    for s in sps:
        im.alpha_composite(s, ((w - s.width) // 2, y)); y += s.height
    return finish(im, edge=4, shadow=(6, 10, 10, .35), rough=.7)


def _word(text, size=190):
    f = font(F_BLACK, size)
    sp = text_sprite(text, f, OR, 14, BR, pad=30)
    return finish(sp, edge=7, edge_col=(255, 246, 226), shadow=(8, 12, 10, .4), rough=1)


def card_sprite(c):
    k = c["kind"]
    if k == "lower":
        return cached(("lt", c.get("text"), c.get("text2")), lambda: _lower_third(c.get("text", "UNCLE"), c.get("text2", "")))
    if k == "intermission":
        return cached(("im",), _intermission)
    if k == "safety":
        return cached(("sf",), _safety)
    if k == "fineprint":
        return cached(("fp",), _fineprint)
    if k == "step":
        return cached(("st", c["text"]), lambda: _step(c["text"]))
    if k == "rating":
        return cached(("rt", c.get("text", "10/10")), lambda: _rating(c.get("text", "10/10")))
    if k == "recap":
        return cached(("rc",), lambda: _tab(["RECAP", "(gets shorter every episode)"], size=50))
    if k == "next":
        return cached(("nx",), lambda: _tab(["NEXT: GUANGZHOU"], size=64))
    if k == "word":
        return cached(("wd", c["text"]), lambda: _word(c["text"], c.get("size", 190)))
    raise KeyError(k)


def draw(frame, c, dt, Wd, Hd):
    """Composite card `c` at local time dt (seconds since card start) onto PIL RGB `frame`."""
    k = c["kind"]
    d = c["d"]
    sp = card_sprite(c)
    if k == "lower" and c.get("flip_t") is not None and dt >= c["flip_t"] + 0.12:
        sp = cached(("lt", c.get("text"), c.get("text2b")), lambda: _lower_third(c.get("text", "UNCLE"), c.get("text2b", "")))
    land = Wd > Hd                                  # horizontal 16:9: sprites keep their 1080-reference pixel size relative to the HEIGHT
    sc = (Hd if land else Wd) / 1080.0
    if land:
        # make_episode merges "<key>_land" overrides (x_land, y_land, text_land...) into the card before calling draw().
        # Defaults: lower-thirds sit left of center; everything stays above the caption zone (lower 25%) and inside the 5% safe margin.
        x = c.get("x", 0.3 if k == "lower" else 0.5) * Wd
        y = (c.get("y", 0.62) if "y_land" in c else min(max(c.get("y", 0.62), 0.12), 0.58)) * Hd
    else:
        x = c.get("x", 0.5) * Wd
        y = c.get("y", 0.62) * Hd
    sx = sy = 1.0
    rot = c.get("rot", 0.0)
    alpha = 1.0
    out = seg(d - dt, 0.0, 0.18)
    alpha = out
    pin = c.get("in", "pop")
    q = dt / 0.24
    if k == "lower":
        e = out_cubic(seg(dt, 0, 0.35))
        x = lerp(-0.6 * Wd, x, e)
        if c.get("flip_t") is not None and abs(dt - c["flip_t"]) < 0.12:
            sy = abs((dt - c["flip_t"]) / 0.12)
        if c.get("flip_t") is not None and 0.12 <= dt - c["flip_t"] < 0.3:
            sy = 1 + 0.06 * math.sin((dt - c["flip_t"] - .12) / .18 * math.pi)
    elif pin == "slam":
        s = lerp(2.0, 1.0, in_cubic(seg(dt, 0, 0.1)))
        sx = sy = s
        if 0.1 < dt < 0.4:
            x += (hrand(int(dt * 60), 1) - .5) * 24 * (1 - seg(dt, .1, .4)) * sc
            y += (hrand(int(dt * 60), 2) - .5) * 24 * (1 - seg(dt, .1, .4)) * sc
        alpha *= min(1, dt / 0.05)
    elif pin == "slide_down":
        y = lerp(y - 0.5 * Hd, y, out_back(seg(dt, 0, 0.3)))
    else:
        s = out_back(seg(dt, 0, 0.26), 2.0)
        sx = sy = max(s, 0.01)
        if k == "word":
            rot += math.sin(dt * 28) * 4 * (1 - seg(dt, 0, 0.5))
            sx = sy = sx * (1 + 0.05 * math.sin(dt * 18))
        alpha *= min(1, dt / 0.08)
    if c.get("slide_t") is not None and dt >= c["slide_t"]:     # card slides down out of frame (10/10 gag)
        q2 = in_cubic(seg(dt, c["slide_t"], c["slide_t"] + c.get("slide_d", 0.5)))
        y += q2 * 0.55 * Hd
        rot += q2 * 6
    blit(frame, sp, x, y, rot=rot, sx=sx * sc, sy=sy * sc, alpha=max(0.0, min(1.0, alpha)))
