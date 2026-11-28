"""Storyboard cards for the animatic: flat palette cards with simple character icons (NOT final art, no stand-in stills used)."""
import re
from PIL import Image, ImageDraw, ImageFont

CREAM, LEAF, ORANGE, PEACH, BROWN = (255, 250, 240), (236, 198, 106), (217, 72, 15), (255, 227, 184), (59, 42, 26)
INDIGO, JADE, SEPIA, GREY = (62, 78, 128), (79, 154, 127), (107, 74, 43), (190, 186, 180)
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONTB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
PACEC = {"fast": ORANGE, "medium": LEAF, "calm": (150, 120, 90)}
_f = {}


def font(p, s):
    k = (p, int(s))
    if k not in _f:
        _f[k] = ImageFont.truetype(p, int(s))
    return _f[k]


def wrap(d, text, fnt, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            out.append(cur); cur = w
    return out + ([cur] if cur else [])


class Pen:
    """Draws in logical units (u) onto an image rendered at scale k."""
    def __init__(self, img, k):
        self.img, self.k, self.d = img, k, ImageDraw.Draw(img, "RGBA")

    def c(self, *v):
        return [x * self.k for x in v]

    def ell(self, cx, cy, rx, ry, fill, out=BROWN, w=3):
        self.d.ellipse(self.c(cx - rx, cy - ry, cx + rx, cy + ry), fill=fill, outline=out, width=max(1, int(w * self.k)) if out else 0)

    def rect(self, x0, y0, x1, y1, fill, out=BROWN, w=3, r=0):
        self.d.rounded_rectangle(self.c(x0, y0, x1, y1), radius=r * self.k, fill=fill, outline=out, width=max(1, int(w * self.k)) if out else 0)

    def poly(self, pts, fill, out=BROWN, w=3):
        self.d.polygon([(x * self.k, y * self.k) for x, y in pts], fill=fill, outline=out if out else None)
        if out:
            self.d.line([(x * self.k, y * self.k) for x, y in pts + [pts[0]]], fill=out, width=max(1, int(w * self.k)))

    def line(self, pts, fill=BROWN, w=3):
        self.d.line([(x * self.k, y * self.k) for x, y in pts], fill=fill, width=max(1, int(w * self.k)))

    def arc(self, box, a0, a1, fill=BROWN, w=3):
        self.d.arc(self.c(*box), a0, a1, fill=fill, width=max(1, int(w * self.k)))

    def text(self, x, y, s, size, fill=BROWN, bold=True, anchor="mm", stroke=0, sfill=None):
        self.d.text((x * self.k, y * self.k), s, font=font(FONT if bold else FONTB, size * self.k), fill=fill, anchor=anchor,
                    stroke_width=int(stroke * self.k), stroke_fill=sfill or BROWN)

    def para(self, x, y, s, size, maxw, fill=BROWN, bold=False, gap=1.25, maxlines=6, anchor="ma"):
        fnt = font(FONT if bold else FONTB, size * self.k)
        lines = wrap(self.d, s, fnt, maxw * self.k)[:maxlines]
        for i, ln in enumerate(lines):
            self.d.text((x * self.k, (y + i * size * gap) * self.k), ln, font=fnt, fill=fill, anchor=anchor)
        return y + len(lines) * size * gap


def icon(p, kind, cx, cy, S):
    if kind == "Boy":
        p.rect(cx - .27 * S, cy + .16 * S, cx + .27 * S, cy + .52 * S, INDIGO, r=.08 * S)
        p.rect(cx - .27 * S, cy + .36 * S, cx + .27 * S, cy + .42 * S, ORANGE, None)
        p.ell(cx, cy, .19 * S, .2 * S, PEACH)
        p.poly([(cx, cy - .5 * S), (cx - .36 * S, cy - .07 * S), (cx + .36 * S, cy - .07 * S)], LEAF)
        p.line([(cx - .3 * S, cy - .08 * S), (cx - .18 * S, cy + .16 * S)], ORANGE, 4); p.line([(cx + .3 * S, cy - .08 * S), (cx + .18 * S, cy + .16 * S)], ORANGE, 4)
        for sx in (-1, 1):
            p.ell(cx + sx * .07 * S, cy + .01 * S, .018 * S, .025 * S, BROWN, None)
        p.arc((cx - .07 * S, cy + .03 * S, cx + .07 * S, cy + .12 * S), 10, 170)
    elif kind == "Uncle":
        p.rect(cx - .42 * S, cy + .2 * S, cx + .42 * S, cy + .55 * S, (112, 78, 46), r=.1 * S)
        p.rect(cx - .42 * S, cy + .4 * S, cx + .42 * S, cy + .48 * S, ORANGE, None)
        p.rect(cx + .16 * S, cy + .17 * S, cx + .4 * S, cy + .27 * S, CREAM, r=.03 * S)
        p.ell(cx, cy, .27 * S, .27 * S, PEACH)
        for sx in (-1, 1):
            p.line([(cx + sx * .06 * S, cy - .07 * S), (cx + sx * .15 * S, cy - .1 * S)], BROWN, 6)
            p.ell(cx + sx * .09 * S, cy - .02 * S, .02 * S, .028 * S, BROWN, None)
            p.arc((cx + (sx * .26 - .13) * S, cy + .04 * S, cx + (sx * .26 + .13) * S, cy + .2 * S), 200 if sx < 0 else 340, 360 if sx > 0 else 340 + 0, BROWN, 5)
        p.line([(cx - .22 * S, cy + .12 * S), (cx - .02 * S, cy + .09 * S), (cx + .02 * S, cy + .09 * S), (cx + .22 * S, cy + .12 * S)], (30, 22, 16), 6)
        p.arc((cx - .32 * S, cy + .05 * S, cx - .18 * S, cy + .2 * S), 90, 300, (30, 22, 16), 5); p.arc((cx + .18 * S, cy + .05 * S, cx + .32 * S, cy + .2 * S), 240, 450, (30, 22, 16), 5)
    elif kind == "Grandma":
        p.rect(cx - .27 * S, cy + .17 * S, cx + .27 * S, cy + .52 * S, JADE, r=.08 * S)
        p.rect(cx - .15 * S, cy + .27 * S, cx + .15 * S, cy + .52 * S, CREAM, r=.04 * S)
        p.ell(cx, cy - .27 * S, .1 * S, .1 * S, GREY)
        p.line([(cx - .12 * S, cy - .4 * S), (cx + .12 * S, cy - .24 * S)], (150, 100, 60), 4); p.line([(cx + .12 * S, cy - .4 * S), (cx - .12 * S, cy - .24 * S)], (150, 100, 60), 4)
        p.ell(cx, cy, .19 * S, .2 * S, PEACH)
        p.arc((cx - .19 * S, cy - .2 * S, cx + .19 * S, cy + .05 * S), 180, 360, GREY, 9)
        for sx in (-1, 1):
            p.line([(cx + sx * .04 * S, cy), (cx + sx * .1 * S, cy)], BROWN, 4)
        p.line([(cx - .05 * S, cy + .1 * S), (cx + .05 * S, cy + .1 * S)], BROWN, 3)
    elif kind == "Dad":
        p.ell(cx, cy + .45 * S, .34 * S, .3 * S, SEPIA, None)
        p.ell(cx, cy + .02 * S, .16 * S, .17 * S, SEPIA, None)
        p.poly([(cx, cy - .45 * S), (cx - .32 * S, cy - .08 * S), (cx + .32 * S, cy - .08 * S)], (140, 104, 62), None)
    elif kind == "Camel":
        p.ell(cx, cy + .1 * S, .34 * S, .17 * S, (170, 125, 70)); p.ell(cx - .06 * S, cy - .12 * S, .09 * S, .1 * S, (170, 125, 70))
        p.line([(cx + .26 * S, cy), (cx + .38 * S, cy - .3 * S)], (170, 125, 70), 10); p.ell(cx + .42 * S, cy - .33 * S, .08 * S, .06 * S, (170, 125, 70))
        for x in (-.22, -.1, .12, .24):
            p.line([(cx + x * S, cy + .2 * S), (cx + x * S, cy + .42 * S)], BROWN, 5)
    elif kind == "Dumpling":
        p.ell(cx, cy, .3 * S, .22 * S, CREAM)
        for i in range(-3, 4):
            p.line([(cx + i * .07 * S, cy - .22 * S), (cx + i * .05 * S, cy - .08 * S)], BROWN, 3)
        for i in (-1, 0, 1):
            p.arc((cx + i * .12 * S - .05 * S, cy - .46 * S, cx + i * .12 * S + .05 * S, cy - .26 * S), 270, 90, (190, 170, 150), 4)
    elif kind == "Hands":
        for sx in (-1, 1):
            p.rect(cx + sx * .22 * S - .09 * S, cy - .1 * S, cx + sx * .22 * S + .09 * S, cy + .25 * S, PEACH, r=.07 * S)
            for f in range(3):
                p.rect(cx + sx * .22 * S - .09 * S + f * .06 * S, cy - .2 * S, cx + sx * .22 * S - .09 * S + f * .06 * S + .05 * S, cy - .05 * S, PEACH, r=.02 * S)
    elif kind == "Stool":
        p.rect(cx - .3 * S, cy - .05 * S, cx + .3 * S, cy + .05 * S, (150, 100, 60), r=.02 * S)
        for x in (-.24, .24):
            p.line([(cx + x * S, cy + .05 * S), (cx + x * S * 1.2, cy + .38 * S)], BROWN, 6)


def label_for(name, role):
    return name.upper() + (f" ({role})" if role else "")


def base_card(sh, W, H, k, land, speaker=None):
    """Generic shot card. Returns (RGB image at scale k, meta)."""
    img = Image.new("RGB", (int(W * k), int(H * k)), CREAM)
    p = Pen(img, k)
    lw, lh = W, H
    p.rect(0, 0, lw, 6, LEAF, None)
    names = list(sh["names"]); hands = sh["hands"]; back = sh["back"]
    items = [(n, "") for n in names] + [(n, "hands only") for n in hands] + [(n, "from behind") for n in back]
    icons = []
    for n, role in items:
        icons.append(("Hands" if role == "hands only" else n, n, role))
    if not names and not hands and not back:
        icons = [("Dumpling", "close-up object", "")]
    elif not names and hands:
        icons = [("Dumpling", "object", ""), ] + icons
    S = (150 if land else 230)
    if len(icons) > 2:
        S = int(S * .75)
    cy = 250 if land else 420
    pos = {}
    for i, (kind, nm, role) in enumerate(icons):
        cx = lw * (i + 1) / (len(icons) + 1)
        p.ell(cx, cy + .02 * S, .62 * S, .62 * S, PEACH if kind != "Dad" else (233, 205, 165), None)
        icon(p, kind, cx, cy, S)
        p.text(cx, cy + .78 * S, nm.upper() if kind != "Hands" else "HANDS: " + nm.upper(), 25 if not land else 21, BROWN)
        if role:
            p.text(cx, cy + .78 * S + 27, role, 19, (120, 95, 70), bold=False)
        pos[nm] = (cx, cy, S)
    # shot type + action text
    typ = f"{sh['shot']}  |  {sh['method']}"
    if land:
        p.text(lw / 2, 72, typ, 20, (120, 95, 70))
        p.para(lw / 2, 430, sh["action"], 24, lw * .8, BROWN, maxlines=3)
    else:
        p.text(lw / 2, 138, typ, 24, (120, 95, 70))
        p.para(lw / 2, 598, sh["action"], 27, lw * .88, BROWN, maxlines=5)
        # caption-zone guide and the phone UI strip (animatic info lives in the UI-covered strip)
        p.rect(18, 776, lw - 18, 944, None, (230, 205, 170), 2, 14)
        p.text(lw - 30, 786, "caption zone", 14, (200, 170, 130), bold=False, anchor="rt")
        p.rect(0, 960, lw, H, (244, 231, 208), None)
        p.line([(0, 960), (lw, 960)], (217, 72, 15), 2)
        p.text(14, 970, "phone UI zone (480 px of 1920 clear): animatic info only", 14, ORANGE, bold=False, anchor="lt")
        y = p.para(18, 998, "SAYS: " + (sh["voice"][:140] if sh["voice"] and sh["voice"] != "—" else "(no voice)"), 21, lw - 36, BROWN, maxlines=3, gap=1.2, anchor="la")
        p.para(18, y + 8, "SFX: " + sh["sfx"], 19, lw - 36, (110, 80, 50), maxlines=3, gap=1.2, anchor="la")
        p.para(18, 1175, "EDIT: " + re.sub(r"\s+", " ", sh["edit"])[:170], 16, lw - 36, (130, 105, 80), maxlines=4, gap=1.2, anchor="la")
    return img, dict(icons=pos)


def ins_card(sh, note, W, H, k, land):
    img = Image.new("RGB", (int(W * k), int(H * k)), PEACH)
    p = Pen(img, k)
    p.rect(0, 0, W, 6, ORANGE, None)
    cy = 250 if land else 420
    p.rect(W * .12, cy - (95 if land else 160), W * .88, cy + (95 if land else 160), CREAM, BROWN, 4, 30)
    kind = "Dumpling"
    if "face" in note or "lip" in note or "eye" in note or "cheek" in note or "squeak" in note:
        kind = (sh["names"] or ["Boy"])[0]
    icon(p, kind, W / 2, cy, 150 if land else 230)
    p.text(W / 2, cy - (115 if land else 195), "INSERT / CUT-IN", 22 if land else 28, ORANGE)
    p.para(W / 2, (cy + 110) if land else 640, note or "insert", 24 if land else 28, W * .8, BROWN, maxlines=3)
    return img, dict(icons={})


def code_card(label, sub, W, H, k, land, bg=CREAM, tint=ORANGE):
    img = Image.new("RGB", (int(W * k), int(H * k)), bg)
    p = Pen(img, k)
    p.rect(0, 0, W, 6, tint, None)
    p.text(W / 2, H * .30, label, 44 if not land else 36, tint, stroke=0)
    p.para(W / 2, H * .38, sub, 26 if not land else 22, W * .8, BROWN, maxlines=5)
    return img, dict(icons={})


def title_card(W, H, k, land, tag=None):
    img = Image.new("RGB", (int(W * k), int(H * k)), LEAF)
    p = Pen(img, k)
    p.text(W / 2, H * .42, "THE", 52 if not land else 40, CREAM, stroke=5)
    p.text(W / 2, H * .50, "DUMPLING BOY", 72 if not land else 56, ORANGE, stroke=6, sfill=CREAM) if False else None
    p.text(W / 2, H * .50, "DUMPLING BOY", 66 if not land else 52, ORANGE, stroke=6, sfill=BROWN)
    if tag:
        p.text(W / 2, H * .60, tag, 40, BROWN)
    icon(p, "Dumpling", W / 2, H * .30, 200 if not land else 130)
    return img, dict(icons={})
