"""Tiny 2D skeletal rig renderer (numpy + OpenCV + PIL).

Parts are RGBA crops in original-art coordinates with a pivot and a parent.
A pose gives each part (rot_deg, tx, ty, sx, sy) about its pivot; children
inherit the parent's transform.  Drawing is premultiplied-alpha affine warps,
so a 720x1280 frame with two characters renders in ~30 ms.
"""
import json, os, math
import numpy as np, cv2
from PIL import Image, ImageDraw

RIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "specs", "rigs")
BROWN = (58, 38, 22)


def T(tx, ty):
    return np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], np.float64)


def R(deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], np.float64)


def S(sx, sy):
    return np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]], np.float64)


def about(p, M):
    return T(p[0], p[1]) @ M @ T(-p[0], -p[1])


def smooth(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def eio(x):  # ease in-out
    return smooth(x)


class Face:
    """Procedural face for a head sprite: eyes, brows, mouth, pseudo-3D turn."""

    def __init__(self, kind, head_rgba, off, skin):
        self.kind = kind
        self.off = off
        self.skin = tuple(skin)
        self.orig = head_rgba.copy()
        self.clean = head_rgba.copy()
        h, w = head_rgba.shape[:2]
        self.h, self.w = h, w
        ox, oy = off
        if kind == "uncle":
            self.eye_c = [(402 - ox, 133 - oy), (519 - ox, 133 - oy)]
            self.brow_box = [(355 - ox, 80 - oy, 422 - ox, 108 - oy), (488 - ox, 80 - oy, 552 - ox, 108 - oy)]
            self.eye_box = [(358 - ox, 112 - oy, 446 - ox, 150 - oy), (486 - ox, 112 - oy, 556 - ox, 150 - oy)]
            self.mouth_box = (388 - ox, 206 - oy, 514 - ox, 268 - oy)
            self.mouth_c = (451 - ox, 226 - oy)
            self.turn_c = (450 - ox, 178 - oy); self.turn_r = (165, 150)
        else:
            self.eye_c = [(228 - ox, 270 - oy), (336 - ox, 268 - oy)]
            self.brow_box = []
            self.eye_box = [(188 - ox, 235 - oy, 268 - ox, 305 - oy), (298 - ox, 233 - oy, 376 - ox, 303 - oy)]
            self.mouth_box = (250 - ox, 316 - oy, 322 - ox, 340 - oy)
            self.mouth_c = (285 - ox, 328 - oy)
            self.turn_c = (280 - ox, 285 - oy); self.turn_r = (150, 130)
        self._prep()

    def _prep(self):
        rgb = self.clean[..., :3].copy(); a = self.clean[..., 3]
        skin = np.array(self.skin, np.float32)
        # eyebrows (uncle): dark pixels inside the brow boxes become movable sprites
        self.brows = []
        for (x0, y0, x1, y1) in self.brow_box:
            sub = rgb[y0:y1, x0:x1].astype(np.float32)
            dark = (sub.sum(-1) < 330).astype(np.uint8)
            dark = cv2.dilate(dark, np.ones((5, 5), np.uint8))
            m = np.zeros(rgb.shape[:2], np.uint8); m[y0:y1, x0:x1] = dark * 255
            spr = self.orig.copy(); spr[..., 3] = (m.astype(np.float32) * a / 255).astype(np.uint8)
            self.brows.append((spr[y0:y1, x0:x1].copy(), (x0, y0)))
            rgb = cv2.inpaint(rgb, m, 4, cv2.INPAINT_TELEA)
        if self.kind == "uncle":
            # eyes: keep original laugh arcs as sprites, erase them from the clean head
            self.arcs = []
            for (x0, y0, x1, y1) in self.eye_box:
                sub = rgb[y0:y1, x0:x1].astype(np.float32)
                dark = (sub.sum(-1) < 420).astype(np.uint8)
                dark = cv2.dilate(dark, np.ones((3, 3), np.uint8))
                m = np.zeros(rgb.shape[:2], np.uint8); m[y0:y1, x0:x1] = dark * 255
                spr = self.orig.copy(); spr[..., 3] = (m.astype(np.float32) * a / 255).astype(np.uint8)
                self.arcs.append((spr[y0:y1, x0:x1].copy(), (x0, y0)))
                rgb = cv2.inpaint(rgb, m, 4, cv2.INPAINT_TELEA)
            # mouth: erase everything non-skin in the mouth box, refill with masked-blur skin
            x0, y0, x1, y1 = self.mouth_box
            diff = np.abs(rgb.astype(np.float32) - skin).sum(-1)
            mm = np.zeros(rgb.shape[:2], np.uint8)
            mm[y0:y1, x0:x1] = (diff[y0:y1, x0:x1] > 55)
            mm = cv2.dilate(mm, np.ones((5, 5), np.uint8))
            gx = np.arange(rgb.shape[1])[None, :]; gy = np.arange(rgb.shape[0])[:, None]
            keep = (np.abs(gx - (451 - self.off[0])) > 36) & (gy < 214 - self.off[1])
            mm[keep] = 0
            mm[:y0, :] = 0; mm[y1:, :] = 0; mm[:, :x0] = 0; mm[:, x1:] = 0
            valid = ((diff < 40) & (mm == 0)).astype(np.float32)
            num = cv2.GaussianBlur(rgb.astype(np.float32) * valid[..., None], (0, 0), 9)
            den = cv2.GaussianBlur(valid, (0, 0), 9)[..., None]
            fill = num / np.maximum(den, 1e-3)
            rgb = np.where(mm[..., None] > 0, fill, rgb).astype(np.uint8)
        self.clean[..., :3] = rgb

    # -- drawing helpers (4x supersampled) --
    def _canvas(self):
        return Image.new("RGBA", (self.w * 4, self.h * 4), (0, 0, 0, 0))

    def draw(self, turn=0.0, pitch=0.0, mouth=0.0, mwidth=1.0, eyes="laugh", blink=0.0, look=(0.0, 0.0), brow=0.0, brow_tilt=0.0,
             cheek=0.0, smile=0.6):
        """Return RGBA head image for the given expression."""
        img = self.clean.copy()
        base = Image.fromarray(img)
        L = self._canvas(); d = ImageDraw.Draw(L)
        B = BROWN + (255,)
        if self.kind == "uncle":
            # brows
            for i, (spr, (x0, y0)) in enumerate(self.brows):
                sx = -1 if i == 0 else 1
                M = about((spr.shape[1] / 2, spr.shape[0] / 2), R(sx * brow_tilt))
                M = T(x0, y0 + (-brow)) @ M
                self._paste(base, spr, M)
            # eyes
            for i, (cx, cy) in enumerate(self.eye_c):
                if eyes == "laugh":
                    spr, (x0, y0) = self.arcs[i]
                    M = T(x0, y0 + 3 * blink)
                    self._paste(base, spr, M)
                elif eyes == "open":
                    rx, ry = 27, 25 * (1 - 0.92 * blink) + 2
                    px, py = cx * 4, cy * 4
                    d.ellipse([px - rx * 4, py - ry * 4, px + rx * 4, py + ry * 4], fill=(255, 255, 250, 255), outline=B, width=20)
                    if blink < 0.85:
                        pr = 13
                        ex, ey = px + look[0] * 11 * 4, py + look[1] * 8 * 4
                        # keep pupil inside the eye
                        d.ellipse([ex - pr * 4, ey - pr * 4, ex + pr * 4, ey + pr * 4], fill=(48, 30, 20, 255))
                        d.ellipse([ex - 4 * 5 + 16, ey - 4 * 7, ex + 4 * 1 + 16, ey - 4 * 1], fill=(255, 255, 255, 255))
                    else:
                        d.line([px - rx * 4, py, px + rx * 4, py], fill=B, width=22)
            # mouth
            mx, my = self.mouth_c[0] * 4, self.mouth_c[1] * 4
            wid = 52 * mwidth
            if mouth < 0.06:
                # closed smile: arc
                sm = 10 + 14 * smile
                d.arc([mx - wid * 4, my - sm * 4 - 20, mx + wid * 4, my + sm * 4 - 20 + 40], 20, 160, fill=B, width=22)
            else:
                hgt = 6 + 36 * mouth
                top = my - 14 * 4
                pts = []
                n = 24
                for k in range(n + 1):
                    t = k / n; x = mx - wid * 4 + t * 2 * wid * 4
                    pts.append((x, top + 4 * 4 * math.sin(math.pi * t) * -0.6))
                for k in range(n + 1):
                    t = 1 - k / n; x = mx - wid * 4 + t * 2 * wid * 4
                    pts.append((x, top + 4 * hgt * math.sin(math.pi * t) ** 0.8))
                d.polygon(pts, fill=(196, 78, 74, 255), outline=B, width=18)
                if mouth > 0.25:
                    # tongue
                    d.ellipse([mx - wid * 4 * 0.55, top + 4 * hgt * 0.55, mx + wid * 4 * 0.55, top + 4 * hgt * 1.05], fill=(235, 128, 120, 255))
                    # redraw outline on top of tongue
                    d.line(pts[n + 1:] + [pts[n + 1]], fill=B, width=16)
                # teeth strip
                if mouth > 0.15:
                    d.polygon([(mx - wid * 4 * 0.86, top + 4), (mx + wid * 4 * 0.86, top + 4), (mx + wid * 4 * 0.78, top + 4 * (4 + hgt * 0.16)),
                               (mx - wid * 4 * 0.78, top + 4 * (4 + hgt * 0.16))], fill=(255, 255, 248, 255))
        else:
            # boy: eyes keep the art; blink paints a skin lid + lash line over each eye
            if blink > 0.05:
                for (cx, cy) in self.eye_c:
                    px, py = cx * 4, cy * 4
                    k = min(1.0, blink)
                    d.ellipse([px - 44 * 4, py - 40 * 4, px + 44 * 4, py + (-40 + 80 * k) * 4], fill=self.skin + (255,))
                    d.arc([px - 36 * 4, py - 10 * 4, px + 36 * 4, py + 18 * 4], 200, 340, fill=B, width=20) if k > 0.7 else None
            # talk mouth for boy (small open shape over the smile)
            if mouth > 0.06:
                mx, my = self.mouth_c[0] * 4, self.mouth_c[1] * 4
                wid = 20 + 8 * mouth; hgt = 4 + 22 * mouth
                d.ellipse([mx - wid * 4, my - 2 * 4, mx + wid * 4, my + hgt * 4], fill=self.skin + (255,))
                d.ellipse([mx - wid * 4 + 8, my - 2 * 4 + 8, mx + wid * 4 - 8, my + hgt * 4 - 8], fill=(186, 70, 64, 255), outline=B, width=14)
                d.ellipse([mx - wid * 2, my + hgt * 4 * 0.45, mx + wid * 2, my + hgt * 4 - 14], fill=(235, 128, 120, 255))
        L = L.resize((self.w, self.h), Image.LANCZOS)
        base.alpha_composite(L) if False else None
        out = np.array(base).astype(np.float32)
        lay = np.array(L).astype(np.float32)
        la = lay[..., 3:4] / 255
        # layer sits inside the head only
        la = la * (out[..., 3:4] > 0)
        out[..., :3] = out[..., :3] * (1 - la) + lay[..., :3] * la
        out = out.astype(np.uint8)
        if abs(turn) > 1e-3 or abs(pitch) > 1e-3 or cheek > 1e-3:
            out = self._turn(out, turn, pitch, cheek)
        return out

    def _paste(self, base, spr, M):
        """alpha-paste RGBA sprite via translate+rotate matrix M (3x3, sprite->head coords)."""
        h, w = self.h, self.w
        warped = cv2.warpAffine(spr, M[:2], (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        base.alpha_composite(Image.fromarray(warped))

    def _turn(self, rgba, turn, pitch, cheek):
        h, w = self.h, self.w
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        cx, cy = self.turn_c; rx, ry = self.turn_r
        r2 = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
        wgt = np.clip(1 - r2, 0, 1) ** 0.8
        sx = turn * 0.28 * rx * wgt
        sy = pitch * 0.14 * ry * wgt
        # cheek puff (chewing): push outward horizontally in the lower face
        if cheek:
            low = np.clip((yy - cy) / ry, 0, 1) * np.clip(1 - r2, 0, 1)
            sx = sx + np.sign(xx - cx) * cheek * 16 * low
        mapx = xx - sx; mapy = yy - sy
        # premultiply to avoid dark fringes
        f = rgba.astype(np.float32); a = f[..., 3:4] / 255
        pm = np.concatenate([f[..., :3] * a, f[..., 3:4]], -1)
        out = cv2.remap(pm, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        oa = out[..., 3:4] / 255
        res = np.concatenate([np.where(oa > 1e-3, out[..., :3] / np.maximum(oa, 1e-3), 0), out[..., 3:4]], -1)
        return np.clip(res, 0, 255).astype(np.uint8)


class Character:
    def __init__(self, name, scale):
        self.name = name
        d = os.path.join(RIGS, name)
        meta = json.load(open(os.path.join(d, "parts.json")))
        self.meta = meta.pop("_meta")
        self.s = scale
        self.parts = {}
        for pn, m in meta.items():
            img = cv2.cvtColor(cv2.imread(os.path.join(d, pn + ".png"), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
            self.parts[pn] = dict(m, rgba=img)
        self.order = sorted(self.parts, key=lambda k: self.parts[k]["z"])
        self.face = Face(name, self.parts["head"]["rgba"], self.parts["head"]["off"], self.meta["skin"])
        self._scaled = {}
        for pn, p in self.parts.items():
            if pn != "head":
                self._scaled[pn] = self._scale_img(p["rgba"])
        self.W, self.H = self.meta["size"]
        self.feet = self.meta["feet"]

    def _scale_img(self, rgba):
        f = rgba.astype(np.float32); a = f[..., 3:4] / 255
        pm = np.concatenate([f[..., :3] * a, f[..., 3:4]], -1)
        h, w = rgba.shape[:2]
        pm = cv2.resize(pm, (max(1, round(w * self.s)), max(1, round(h * self.s))), interpolation=cv2.INTER_AREA)
        return pm  # premultiplied float32

    def render(self, canvas, pos, pose, face=None, flip=False, root=None):
        """canvas: float32 HxWx4 premultiplied.  pos = (x,y) of feet on canvas.
        pose: part -> dict(rot,tx,ty,sx,sy). root: dict(rot,tx,ty,sx,sy) about the feet."""
        s = self.s
        fx, fy = self.feet
        # character space (original px) -> screen
        P = T(pos[0], pos[1]) @ (S(-1, 1) if flip else np.eye(3)) @ S(s, s) @ T(-fx, -fy)
        r = root or {}
        Rt = about((fx, fy), T(r.get("tx", 0), r.get("ty", 0)) @ R(r.get("rot", 0)) @ S(r.get("sx", 1), r.get("sy", 1)))
        world = {"root": Rt}
        for pn in self.order:
            p = self.parts[pn]
            ps = pose.get(pn, {})
            piv = p["pivot"]
            L = about(piv, T(ps.get("tx", 0), ps.get("ty", 0)) @ R(ps.get("rot", 0)) @ S(ps.get("sx", 1), ps.get("sy", 1)))
            world[pn] = world[p["parent"]] @ L
            if pn == "head":
                spr = self._head_pm(face or {}); sc = 1.0
                ox, oy = p["off"]
                # head sprite is at original resolution: warp with scale s
                M = P @ world[pn] @ T(ox, oy)
            else:
                spr = self._scaled[pn]
                ox, oy = p["off"]
                M = P @ world[pn] @ T(ox, oy) @ S(1 / s, 1 / s)
            warped = cv2.warpAffine(spr, M[:2], (canvas.shape[1], canvas.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            a = warped[..., 3:4] / 255
            canvas[:] = warped + canvas * (1 - a)

    def _head_pm(self, face):
        img = self.face.draw(**face)
        f = img.astype(np.float32); a = f[..., 3:4] / 255
        return np.concatenate([f[..., :3] * a, f[..., 3:4]], -1)

    def foot_dy(self):
        return 0
