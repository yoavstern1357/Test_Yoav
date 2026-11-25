"""Procedural layered 'old street' background with real perspective (PIL, 2x supersampled).

A camera moves through a row of picture-book buildings, lanterns hang over the
street, petals drift.  Stand-in for the layered background plates the art team
will deliver (see production/v4/video-tech.md).
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw

W, H = 720, 1280
HORIZON = 520
F = 640.0
CAMH = 2.3
SS = 2
BROWN = (74, 48, 28)
SKY_TOP = (255, 226, 178); SKY_BOT = (255, 242, 214)
HAZE = (250, 232, 205)

WALLS = [(250, 214, 168), (244, 196, 150), (236, 224, 190), (226, 190, 140), (246, 208, 178)]
ROOFS = [(196, 84, 44), (176, 72, 40), (208, 112, 52)]

random.seed(11)
BUILD = []
for side in (-1, 1):
    z = -14.0
    while z < 70:
        d = random.uniform(3.4, 5.0)
        BUILD.append(dict(side=side, z0=z, z1=z + d, h=random.uniform(3.4, 5.2), wall=random.choice(WALLS), roof=random.choice(ROOFS),
                          door=random.random() < 0.6, win=random.random() < 0.8, awn=random.random() < 0.5))
        z += d + 0.15
LANT = [(z, random.uniform(-0.2, 0.2)) for z in np.arange(-6, 70, 6.5)]


def mix(c, h, k):
    return tuple(int(c[i] * (1 - k) + h[i] * k) for i in range(3))


def sky():
    a = np.linspace(0, 1, H * SS)[:, None, None]
    top = np.array(SKY_TOP, np.float32); bot = np.array(SKY_BOT, np.float32)
    g = top * (1 - a) + bot * a
    img = np.repeat(g, W * SS, 1).astype(np.uint8)
    return Image.fromarray(img)


_SKY = None


def render(t, cam_z, cam_x, rays=True):
    global _SKY
    if _SKY is None:
        _SKY = sky()
    img = _SKY.copy()
    d = ImageDraw.Draw(img)
    k = SS

    def P(X, Y, Z):
        z = max(Z - cam_z, 0.35)
        return ((W / 2 + F * (X - cam_x) / z) * k, (HORIZON + F * (CAMH - Y) / z) * k)

    def zz(Z):
        return max(Z - cam_z, 0.35)

    # sun + far mountains / pagoda silhouettes (distant, almost static)
    sx = (W * 0.72 - cam_x * 6) * k
    d.ellipse([sx - 90 * k, (HORIZON - 190) * k, sx + 90 * k, (HORIZON - 10) * k], fill=(255, 210, 150))
    for i, (mx, mw, mh, col) in enumerate([(120, 420, 150, (231, 205, 190)), (520, 480, 200, (224, 196, 184)), (330, 300, 110, (214, 188, 176))]):
        x0 = (mx - cam_x * (3 + i)) * k
        d.polygon([(x0 - mw * k / 2, HORIZON * k), (x0 - mw * k * 0.1, (HORIZON - mh) * k), (x0 + mw * k * 0.15, (HORIZON - mh * 0.7) * k),
                   (x0 + mw * k / 2, HORIZON * k)], fill=col)
    # ground
    gy = HORIZON * k
    d.rectangle([0, gy, W * k, H * k], fill=(233, 205, 160))
    # road bands with slabs
    left = P(-4.2, 0, 0.0 + cam_z + 0.35); right = P(4.2, 0, cam_z + 0.35)
    far_l = P(-4.2, 0, cam_z + 90); far_r = P(4.2, 0, cam_z + 90)
    d.polygon([left, far_l, far_r, right], fill=(240, 216, 172))
    # centre stone strip
    cl = P(-1.2, 0, cam_z + 0.35); cr = P(1.2, 0, cam_z + 0.35)
    fl = P(-1.2, 0, cam_z + 90); fr = P(1.2, 0, cam_z + 90)
    d.polygon([cl, fl, fr, cr], fill=(224, 192, 148))
    step = 1.2
    z0 = math.floor((cam_z + 0.4) / step) * step
    z = z0
    while z < cam_z + 60:
        a = P(-4.2, 0, z); b = P(4.2, 0, z)
        if z - cam_z > 0.4:
            d.line([a, b], fill=mix((205, 170, 125), HAZE, min(1, (z - cam_z) / 60)), width=max(1, int(5 * k / max(1, (z - cam_z)) ** 0.8)))
        z += step
    # buildings (far to near)
    items = []
    for b in BUILD:
        items.append((b["z1"], "b", b))
    for z, off in LANT:
        items.append((z, "l", off))
    items.sort(key=lambda x: -x[0])
    for zc, kind, o in items:
        dist = zc - cam_z
        if dist < 0.5:
            continue
        if kind == "b":
            b = o; s = b["side"]; X = s * 4.2
            fog = min(1.0, max(0.0, (b["z0"] - cam_z - 6) / 62))
            z0, z1 = max(b["z0"], cam_z + 0.5), b["z1"]
            if z1 - cam_z < 0.5:
                continue
            wall = mix(b["wall"], HAZE, fog * 0.7)
            line = mix(BROWN, HAZE, fog * 0.7)
            lw = max(2, int(7 * k / max(zz(z0), 1.5) ** 0.6))
            quad = [P(X, 0, z0), P(X, b["h"], z0), P(X, b["h"], z1), P(X, 0, z1)]
            d.polygon(quad, fill=wall)
            # wall panel shading toward far end
            if b["win"]:
                for wz in (b["z0"] + 0.8, b["z0"] + 2.2):
                    if wz + 0.9 < z1 and wz > z0:
                        q = [P(X, 2.2, wz), P(X, 3.2, wz), P(X, 3.2, wz + 0.9), P(X, 2.2, wz + 0.9)]
                        d.polygon(q, fill=mix((120, 80, 50), HAZE, fog * 0.7))
            if b["door"] and b["z0"] + 1.0 > z0 - 0.01:
                q = [P(X, 0, b["z0"] + 1.0), P(X, 2.0, b["z0"] + 1.0), P(X, 2.0, b["z0"] + 2.1), P(X, 0, b["z0"] + 2.1)]
                d.polygon(q, fill=mix((140, 84, 48), HAZE, fog * 0.7))
            if b["awn"] and b["z0"] + 0.6 > z0 - 0.01:
                q = [P(X, 2.2, b["z0"] + 0.6), P(X - s * 0.9, 2.0, b["z0"] + 0.6), P(X - s * 0.9, 2.0, z1 - 0.6), P(X, 2.2, z1 - 0.6)]
                d.polygon(q, fill=mix((220, 120, 60), HAZE, fog * 0.7), outline=line)
            d.line(quad + [quad[0]], fill=line, width=lw)
            # eave / roof slab
            e = [P(X, b["h"], z0 - 0.15), P(X - s * 1.0, b["h"] + 0.35, z0 - 0.15), P(X - s * 1.0, b["h"] + 0.35, z1 + 0.15), P(X, b["h"], z1 + 0.15)]
            d.polygon(e, fill=mix(b["roof"], HAZE, fog * 0.7), outline=line)
            top = [P(X, b["h"], z0 - 0.15), P(X, b["h"] + 0.9, z0 + 0.2), P(X, b["h"] + 0.9, z1 - 0.2), P(X, b["h"], z1 + 0.15)]
            d.polygon(top, fill=mix(b["roof"], HAZE, fog * 0.6 + 0.1), outline=line)
        else:
            if dist < 2.6:
                continue
            sway = math.sin(t * 1.7 + zc) * 0.12
            fog = min(1.0, dist / 70)
            Z = zc
            ya = 4.7
            a = P(-4.2, ya, Z); b2 = P(4.2, ya, Z)
            mid = P(0, ya - 0.35, Z)
            d.line([a, mid, b2], fill=mix(BROWN, HAZE, fog), width=max(1, int(3 * k / max(1, dist) ** 0.5)))
            for lx in (-2.4, 0.0 + o, 2.4):
                px, py = P(lx + sway, 4.0, Z)
                r = max(2, 0.34 * F / zz(Z) * k)
                d.line([P(lx + sway * 0.3, ya - 0.3, Z), (px, py - r)], fill=mix(BROWN, HAZE, fog), width=max(1, int(2 * k)))
                d.ellipse([px - r * 0.85, py - r, px + r * 0.85, py + r], fill=mix((222, 64, 40), HAZE, fog * 0.8), outline=mix(BROWN, HAZE, fog), width=max(1, int(r * 0.07)))
                d.rectangle([px - r * 0.3, py + r, px + r * 0.3, py + r * 1.15], fill=(240, 190, 70))
    return img.resize((W, H), Image.LANCZOS)


def petals(t, n=22):
    """soft drifting petals / dust motes as RGBA premultiplied float image."""
    img = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    for i in range(n):
        x0 = rnd.uniform(0, W); y0 = rnd.uniform(0, H); sp = rnd.uniform(18, 46); ph = rnd.uniform(0, 6.28); s = rnd.uniform(5, 11)
        x = (x0 - sp * 0.8 * t + 30 * math.sin(t * 0.9 + ph)) % W
        y = (y0 + sp * t) % H
        a = int(rnd.uniform(130, 220))
        col = (255, 188, 190, a) if i % 3 else (255, 240, 200, a)
        r = s * (0.6 + 0.4 * abs(math.sin(t * 2 + ph)))
        d.ellipse([(x - s) * 2, (y - r) * 2, (x + s) * 2, (y + r) * 2], fill=col)
    return np.array(img.resize((W, H), Image.LANCZOS)).astype(np.float32)
