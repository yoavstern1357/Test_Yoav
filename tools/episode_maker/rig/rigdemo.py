#!/usr/bin/env python3
"""Rig animation test clip: Uncle + Boy (from the approved art) walk in, sniff, gesture, catch a dumpling, chew, run off.

    python3 rigdemo.py out/rig-test.mp4 [--fps 24] [--preview] [--frames a:b]

Everything is code: skeletal parts (split_parts.py), procedural faces (rig.py), a
perspective street (street.py), Kokoro voices + synthesized sfx (make_episode / synth).
"""
import argparse, math, os, subprocess, sys, shutil
import numpy as np, cv2
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
from rig import Character, T, R, S, about, smooth
import street

W, H = street.W, street.H
DUR = 9.6

# ----------------------------------------------------------------- helpers
def K(t, pts, ease=True):
    """keyframe interpolation: pts = [(t, v), ...]"""
    if t <= pts[0][0]: return pts[0][1]
    if t >= pts[-1][0]: return pts[-1][1]
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            return v0 + (v1 - v0) * (smooth(u) if ease else u)


def spring(t, t0, amp, f=2.6, damp=7.0):
    if t < t0: return 0.0
    u = t - t0
    return amp * math.exp(-damp * u) * math.cos(2 * math.pi * f * u)


def pulse(t, t0, t1, rise=0.12, fall=0.15):
    return smooth((t - t0) / rise) * (1 - smooth((t - (t1 - fall)) / fall))


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))


# ----------------------------------------------------------------- audio
LINES = [("uncle", "I smell... destiny.", 3.75), ("uncle", "For science!", 5.45), ("boy", "Uncle, wait!", 6.55), ("uncle", "Mine!", 8.0)]
SFX = [(3.3, "pop_step"), (6.95, "pop"), (7.05, "munch"), (8.0, "boing"), (8.35, "swoosh_big"), (7.7, "gulp")]


def build_audio(path):
    import soundfile as sf
    import make_episode as me, synth
    sr = me.SR
    n = int((DUR + 0.3) * sr)
    mix = np.zeros(n, np.float32)
    env = {}
    for who, text, t0 in LINES:
        w = me.tts(who, text).astype(np.float32)
        i = int(t0 * sr); mix[i:i + len(w)] += w[: n - i] * 0.9
        # mouth envelope at 240 Hz
        hop = sr // 240
        e = np.array([np.sqrt(np.mean(w[k:k + hop] ** 2)) for k in range(0, len(w), hop)])
        e = e / (np.percentile(e, 95) + 1e-6)
        env[(who, t0)] = (t0, np.clip(e, 0, 1), len(w) / sr)
    def put(x, t0, g=0.6):
        i = int(t0 * sr); x = x.astype(np.float32) * g
        mix[i:i + len(x)] += x[: max(0, n - i)]
    # footstep thumps while walking (soft low ticks on every foot lift), sniff, sfx
    rng = np.random.default_rng(3)
    for k in range(int(3.3 / 0.36)):
        tt = 0.2 + k * 0.36
        thump = np.sin(2 * np.pi * (90 * np.exp(-np.arange(int(0.12 * sr)) / sr * 20) + 50) * np.arange(int(0.12 * sr)) / sr) * np.exp(-np.arange(int(0.12 * sr)) / sr * 28)
        put(thump, tt, 0.35 * (1 - smooth((tt - 2.8) / 0.5)))
    put(synth.pop(), 6.95, 0.6)
    put(synth.boing(), 8.0, 0.5)
    put(synth.swoosh_big(0.7), 8.3, 0.5)
    put(synth.sparkle(0.6), 5.4, 0.25)
    for k in range(4):   # chew
        put(synth.tick(0.1), 7.15 + k * 0.14, 0.5)
    put(synth.sip(0.3), 3.6, 0.4)   # sniff
    put(synth.whoosh(0.5), 5.95, 0.4)  # dumpling flies in
    # gentle market ambience
    try:
        amb = synth.ambience("street", DUR + 0.3)
        put(amb, 0.0, 0.5)
    except Exception as ex:
        print("ambience skipped", ex)
    m = np.max(np.abs(mix)) or 1
    mix = (mix / m * 0.85).astype(np.float32)
    sf.write(path, mix, sr)
    return env


def mouth_level(env, who, t):
    for (w, t0), (tt0, e, d) in env.items():
        if w == who and tt0 <= t < tt0 + d:
            i = int((t - tt0) * 240)
            seg = e[max(0, i - 3):i + 4]
            return float(np.mean(seg)) if len(seg) else 0.0
    return None


# ----------------------------------------------------------------- scene
class Scene:
    def __init__(self, env):
        self.env = env
        self.uncle = Character("uncle", 0.50)
        self.boy = Character("boy", 0.40)
        # per-character expression state memory
        self.last_eyes = None
        self.lblink = [0.0]

    # camera / world
    def cam(self, t):
        v = K(t, [(0, 0.0), (0.5, 1.55), (2.9, 1.55), (3.5, 0.0)])
        # integrate speed numerically (cheap closed-form via sampling)
        zs = 0.0
        n = int(t / 0.02)
        for i in range(n): zs += K(i * 0.02, [(0, 0.0), (0.5, 1.55), (2.9, 1.55), (3.5, 0.0)]) * 0.02
        camz = 14.0 - zs
        camx = 0.05 * math.sin(t * 0.9) + (0.9 * smooth((t - 8.3) / 1.2) if t > 8.3 else 0)
        return camz, camx, K(t, [(0, 0.0), (3.5, 0.0)]) 

    def gait(self, t, c):
        """walk envelope e and phase p."""
        e = K(t, [(0, 1.0), (2.8, 1.0), (3.45, 0.0)])
        # phase = integral of speed
        n = int(t / 0.01); ph = 0.0
        for i in range(n):
            tt = i * 0.01
            ph += K(tt, [(0, 1.0), (2.8, 1.0), (3.45, 0.0)]) * 0.01
        if t > 8.1 and c == "uncle":
            return 1.0, 0.0
        return e, ph

    # ------------------------------------------------------------ uncle
    def uncle_pose(self, t):
        e, ph = self.gait(t, "uncle")
        p = ph / 0.74 * 2 * math.pi
        sL, sR = math.sin(p), -math.sin(p)
        liftL, liftR = max(0, sL), max(0, sR)
        pose = {}
        root = {}
        pose["legL"] = dict(rot=e * 6 * liftL, ty=-e * 60 * liftL, sx=1 + 0.05 * e * liftL, sy=1 + 0.05 * e * liftL)
        pose["legR"] = dict(rot=-e * 6 * liftR, ty=-e * 60 * liftR, sx=1 + 0.05 * e * liftR, sy=1 + 0.05 * e * liftR)
        root["ty"] = -e * 14 * abs(math.sin(p))
        pose["torso"] = dict(tx=e * 16 * math.sin(p), rot=e * 2.2 * math.sin(p), sy=1 + e * 0.012 * math.sin(2 * p + 1))
        head = dict(rot=-e * 1.8 * math.sin(p) + 1.4 * e * math.sin(p - 0.9), ty=e * 3 * math.sin(2 * p))
        armR = dict(rot=-e * 7 * math.sin(p) + 0.0)
        armL = dict(rot=e * 4 * math.sin(p))
        # stop squash
        sq = spring(t, 3.35, 0.07, 2.4, 6.0)
        root["sy"] = 1 - sq; root["sx"] = 1 + sq * 0.8
        # sniff 3.6-5.2: chest inflates twice, head up and to the right
        sn = pulse(t, 3.55, 5.3, 0.25, 0.3)
        sniff = max(0, math.sin((t - 3.6) * 9)) * sn if 3.6 < t < 4.5 else 0
        pose["torso"]["sy"] = pose["torso"].get("sy", 1) + 0.025 * sniff
        head["rot"] += 5 * sn * math.sin((t - 3.6) * 2.0)
        head["ty"] += -8 * sniff
        # "For science!" 5.4-6.6: anticipation, arm up with overshoot, body lifts
        ant = pulse(t, 5.15, 5.45, 0.12, 0.1)
        raise_ = K(t, [(5.3, 0), (5.45, -14), (5.62, 92), (5.78, 78), (6.3, 80), (6.75, 62), (7.0, 28), (7.25, 12), (7.55, 4), (8.0, 4)])
        if t > 5.3: armL["rot"] = raise_ + armL["rot"] * (1 - smooth((t - 5.3) / 0.2))
        up = pulse(t, 5.45, 6.6, 0.15, 0.3)
        root["ty"] += -26 * up
        head["rot"] += -6 * up
        pose["armR"] = armR
        # catch: arm snaps down toward the mouth 6.9-7.1 (included in raise_), chew bob
        chew = pulse(t, 7.05, 7.75, 0.05, 0.1) * abs(math.sin((t - 7.05) * 18))
        head["ty"] += 5 * chew
        # jump gag 7.8-8.4, then run-off
        jt = t - 7.95
        if 7.55 <= t < 7.95:
            u = (t - 7.55) / 0.4
            a = math.sin(u * math.pi / 2)
            root["sy"] = 1 - 0.2 * a; root["sx"] = 1 + 0.14 * a
            pose["armR"] = dict(rot=-20 * a)
        run = 0.0
        if t >= 7.95:
            u = t - 7.95
            if u < 0.55:
                hgt = 220 * 4 * (u / 0.55) * (1 - u / 0.55)
                root["ty"] = -hgt
                st = 1 + 0.16 * math.sin(math.pi * u / 0.55)
                root["sy"] = st if u < 0.5 else 1 - 0.18 * smooth((u - 0.5) / 0.05)
                root["sx"] = 1 / math.sqrt(root["sy"])
                pose["legL"] = dict(rot=18, ty=-30); pose["legR"] = dict(rot=-18, ty=-30)
                pose["armR"] = dict(rot=-60 * smooth(u / 0.2))
                pose["torso"] = dict(rot=6)
            else:
                run = 1.0
                pr = (t - 7.95 - 0.55) / 0.34 * 2 * math.pi
                s = math.sin(pr)
                pose["legL"] = dict(rot=26 * s, ty=-70 * max(0, s)); pose["legR"] = dict(rot=-26 * s, ty=-70 * max(0, -s))
                root["ty"] = -28 * abs(math.sin(pr)); root["sy"] = 1; root["sx"] = 1
                pose["torso"] = dict(rot=7 + 2 * s, tx=0)
                pose["armR"] = dict(rot=-40 * s - 20); armL["rot"] = 30 * s + 25
                head["rot"] = 3
        pose["head"] = head; pose["armL"] = armL
        pose.setdefault("armR", armR)
        pose["torso"].setdefault("tx", 0)
        # screen position
        x = K(t, [(0, 0.66 * W), (8.2, 0.66 * W), (9.55, 1.45 * W)]) if t > 8.2 else 0.66 * W
        x = 0.66 * W + (0.0 if t < 8.2 else (1.5 * W) * (smooth((t - 8.2) / 1.35) ** 1.2))
        if t > 7.95 and t < 8.5:  # jump forward a touch
            x += 40 * smooth((t - 7.95) / 0.55)
        y = 1118
        return pose, root, (x, y), e

    def uncle_face(self, t, scrpos_dump, e):
        f = dict(eyes="laugh", mouth=0.0, smile=0.8, mwidth=1.0)
        turn = K(t, [(0, 0.0), (3.4, 0.0), (3.9, 0.75), (5.2, 0.5), (5.5, -0.15), (6.0, 0.1), (6.4, 0.75), (7.0, 0.5), (7.6, 0.0), (8.0, 0.5), (8.2, 0.6)])
        pitch = K(t, [(0, 0), (3.5, 0), (3.75, -0.9), (4.5, -0.9), (5.0, -0.2), (5.2, 0), (6.9, 0), (7.0, 0.0)])
        f["turn"], f["pitch"] = turn, pitch
        # mouth from voice
        m = mouth_level(self.env, "uncle", t)
        # eyes
        eyes = "laugh"; look = (0.0, 0.0); brow = 0.0; tilt = 0.0
        if 3.55 <= t < 5.3: brow, tilt = 8 * pulse(t, 3.55, 5.3), 6
        if 5.3 <= t < 5.95: brow = 6
        if 5.95 <= t < 7.0:   # sees the dumpling: eyes open and tracking
            eyes = "open"; brow = 13 * smooth((t - 5.95) / 0.2); tilt = -4
            dx, dy = self.dump_pos(t)
            look = (clamp((dx - self.upos[0]) / 300, -1, 1), clamp((dy - (self.upos[1] - 520)) / 250, -1, 1))
        if 7.0 <= t < 7.8: eyes = "laugh"; brow = 4
        if t >= 7.95: eyes = "open" if t < 8.4 else "laugh"; brow = 6; look = (1, 0)
        # eye mode change: one closed frame to hide the pop
        if self.last_eyes is not None and eyes != self.last_eyes:
            f["blink"] = 1.0; eyes = "open"
        self.last_eyes = eyes if f.get("blink") is None else self.last_eyes if False else eyes
        f["eyes"] = eyes; f["look"] = look; f["brow"] = brow; f["brow_tilt"] = tilt
        mouth = 0.0
        if m is not None: mouth = clamp(m * 1.05)
        elif 6.2 <= t < 6.95:
            mouth = 0.9 * smooth((t - 6.3) / 0.4)    # wide open for the dumpling
        elif 7.05 <= t < 7.75:
            f["cheek"] = 0.9 * abs(math.sin((t - 7.05) * 9)) ; mouth = 0.0; f["smile"] = 1.0
        elif 7.75 <= t < 7.95:
            mouth = 0.25
        f["mouth"] = mouth
        if mouth > 0.06 and m is not None:
            f["mwidth"] = 0.9 - 0.25 * mouth
        return f

    # ------------------------------------------------------------ boy
    def boy_pose(self, t):
        e, ph = self.gait(t, "boy")
        p = ph / 0.60 * 2 * math.pi + 0.8
        sL, sR = math.sin(p), -math.sin(p)
        liftL, liftR = max(0, sL), max(0, sR)
        pose, root = {}, {}
        pose["legL"] = dict(rot=e * 7 * liftL, ty=-e * 70 * liftL)
        pose["legR"] = dict(rot=-e * 7 * liftR, ty=-e * 70 * liftR)
        root["ty"] = -e * 16 * abs(math.sin(p))
        pose["torso"] = dict(tx=e * 12 * math.sin(p), rot=e * 2.0 * math.sin(p))
        head = dict(rot=-e * 2.2 * math.sin(p) + 2.5 * e * math.sin(p - 1.1), ty=e * 3 * math.sin(2 * p))
        armL = dict(rot=e * 9 * math.sin(p)); armR = dict(rot=-e * 9 * math.sin(p))
        sq = spring(t, 3.4, 0.06, 2.8, 6.5)
        root["sy"] = 1 - sq; root["sx"] = 1 + sq * 0.8
        # panic at 6.45: arms fly up, little hop, tilt
        pan = pulse(t, 6.5, 7.9, 0.12, 0.3)
        if pan > 0:
            wob = math.sin((t - 6.5) * 14) * 6
            armL = dict(rot=armL["rot"] * (1 - pan) + pan * (95 + wob)); armR = dict(rot=armR["rot"] * (1 - pan) + pan * (-95 - wob))
            hop = max(0, math.sin((t - 6.5) * 9)) * pulse(t, 6.5, 7.3, 0.05, 0.3)
            root["ty"] = root.get("ty", 0) - 30 * hop
            head["rot"] += 4 * math.sin((t - 6.5) * 9) * pan
        # run after uncle
        x = 0.27 * W
        if t > 8.55:
            u = t - 8.55
            run = smooth(u / 0.3)
            pr = u / 0.30 * 2 * math.pi
            s = math.sin(pr)
            pose["legL"] = dict(rot=24 * s * run, ty=-60 * max(0, s) * run); pose["legR"] = dict(rot=-24 * s * run, ty=-60 * max(0, -s) * run)
            root["ty"] = -22 * abs(math.sin(pr)) * run; pose["torso"] = dict(rot=7 * run, tx=0)
            armL = dict(rot=30 * s + 20); armR = dict(rot=-30 * s - 20)
            x = 0.27 * W + 1.4 * W * (smooth(u / 1.0) ** 1.3)
        pose["head"] = head; pose["armL"] = armL; pose["armR"] = armR
        pose["torso"].setdefault("tx", 0)
        return pose, root, (x, 1176), e

    def boy_face(self, t):
        f = dict(turn=0.0, pitch=0.0, mouth=0.0, blink=0.0)
        f["turn"] = K(t, [(0, -0.25), (1.0, 0.25), (2.0, -0.2), (3.0, 0.2), (3.7, 0.0), (4.0, 0.8), (5.0, 0.9), (5.4, 0.2), (6.0, 0.9), (6.45, 0.6), (7.4, 0.2), (7.9, 0.9), (8.4, 0.9), (9.0, 0.4)])
        f["pitch"] = K(t, [(0, 0), (6.4, 0), (6.5, -0.4), (7.2, -0.2), (7.6, 0)])
        # blinks
        bt = 0.0
        for c in (0.9, 2.7, 4.4, 5.6, 7.75, 8.9):
            d = abs(t - c)
            if d < 0.09: bt = max(bt, 1 - d / 0.09)
        f["blink"] = bt
        m = mouth_level(self.env, "boy", t)
        if m is not None: f["mouth"] = clamp(m * 1.0)
        elif 6.0 < t < 6.5: f["mouth"] = 0.8      # gasp
        return f

    # ------------------------------------------------------------ dumpling
    def dump_pos(self, t):
        if t < 6.0: return (W + 60, 250)
        u = clamp((t - 6.0) / 0.95)
        if u < 1:
            p0 = np.array([W + 70.0, 300.0]); p1 = np.array([W * 0.95, 80.0]); p2 = np.array(self.catch_pt)
            q = (1 - u) ** 2 * p0 + 2 * (1 - u) * u * p1 + u * u * p2
            return (float(q[0]), float(q[1]))
        return self.catch_pt

    def draw_dumpling(self, canvas, pos, t):
        s = 34
        sp = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(sp)
        d.pieslice([30, 50, 170, 190], 180, 360, fill=(255, 244, 222, 255), outline=(74, 48, 28, 255), width=4)
        d.chord([30, 100, 170, 150], 0, 180, fill=(255, 244, 222, 255), outline=(74, 48, 28, 255), width=4)
        for i in range(6):
            x = 50 + i * 20
            d.line([x, 58 + abs(i - 2.5) * 4, x + 4, 95], fill=(200, 160, 120, 255), width=3)
        d.line([32, 120, 168, 120], fill=(74, 48, 28, 255), width=4)
        sp = sp.resize((int(s * 3), int(s * 3)), Image.LANCZOS)
        ang = (t - 6.0) * 540 if t < 6.95 else 0
        a = np.array(sp.rotate(-ang, resample=Image.BICUBIC)).astype(np.float32)
        a[..., :3] *= a[..., 3:4] / 255
        M = np.float32([[1, 0, pos[0] - a.shape[1] / 2], [0, 1, pos[1] - a.shape[0] / 2]])
        w = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR)
        al = w[..., 3:4] / 255
        canvas[:] = w + canvas * (1 - al)

    # ------------------------------------------------------------ frame
    def frame(self, t, bgcache={}):
        camz, camx, _ = self.cam(t)
        bg = np.array(street.render(t, camz, camx)).astype(np.float32)
        canvas = np.zeros((H, W, 4), np.float32)
        up, ur, upos, ue = self.uncle_pose(t)
        bp, br, bpos, be = self.boy_pose(t)
        self.upos = upos
        # catch point: chopstick tip when the arm is at the catch angle
        cp_pose = dict(up); cp_pose["armL"] = dict(rot=62)
        self.catch_pt = self.uncle.screen_point(upos, cp_pose, "armL", (140, 335), root=ur)
        # shadows
        sh = np.zeros((H, W), np.float32)
        for (pos, w, lift) in ((upos, 300, -ur.get("ty", 0)), (bpos, 160, -br.get("ty", 0))):
            a = 0.30 * math.exp(-max(0, lift) / 200)
            cv2.ellipse(sh, (int(pos[0]), int(pos[1] - 8)), (int(w * (1 - max(0, lift) / 700)), int(w * 0.14)), 0, 0, 360, a, -1, cv2.LINE_AA)
        sh = cv2.GaussianBlur(sh, (0, 0), 6)
        bgf = bg * (1 - sh[..., None]) + np.array([90, 60, 40], np.float32) * sh[..., None] * 0.0
        bgf = bg * (1 - sh[..., None] * 0.9)
        nsub = 3 if (t > 8.0) else 1
        acc = np.zeros_like(canvas)
        for k in range(nsub):
            dt = (k - (nsub - 1) / 2) * (1 / 24 / nsub) * 1.0 if nsub > 1 else 0
            tt = t + dt
            up, ur, upos2, _ = self.uncle_pose(tt); bp, br, bpos2, _ = self.boy_pose(tt)
            c = np.zeros_like(canvas)
            self.uncle.render(c, upos2, up, face=self.uncle_face(tt, None, 0) if k == nsub // 2 else self.uface, root=ur)
            if k == nsub // 2: self.uface = self.uncle_face(tt, None, 0)
            self.boy.render(c, bpos2, bp, face=self.boy_face(tt), root=br)
            acc += c / nsub
        # dumpling (in front of uncle's face, behind hand) - keep simple: on top
        if 5.99 < t < 7.05:
            dpos = self.dump_pos(t) if t < 6.95 else self.mouth_pt(upos, up, ur)
            if t >= 6.95:
                u = (t - 6.95) / 0.1
                cp = np.array(self.catch_pt); mp = np.array(self.mouth_pt(upos, up, ur))
                dpos = tuple(cp * (1 - clamp(u)) + mp * clamp(u))
            self.draw_dumpling(acc, dpos, t)
        out = bgf * (1 - acc[..., 3:4] / 255) + acc[..., :3]
        # petals + light
        pt = street.petals(t)
        pa = pt[..., 3:4] / 255
        out = out * (1 - pa * 0.8) + pt[..., :3] * pa * 0.8
        # dust puffs at stop and take-off
        out = self.fx(out, t, upos, bpos)
        # vignette + warm grade
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        v = 1 - 0.25 * (((xx - W / 2) / (W / 1.2)) ** 2 + ((yy - H / 2) / (H / 1.2)) ** 2)
        out = out * v[..., None] * np.array([1.02, 1.0, 0.96], np.float32)
        return np.clip(out, 0, 255).astype(np.uint8)

    def mouth_pt(self, upos, pose, root):
        return self.uncle.screen_point(upos, pose, "head", (451, 226), root=root, face=True)

    def fx(self, out, t, upos, bpos):
        ov = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        def puff(x, y, u, r0, a0, n=5):
            for i in range(n):
                ang = math.pi * (0.1 + 0.8 * i / (n - 1)) if n > 1 else 1.0
                dx = math.cos(ang) * (60 + 140 * u) * (1 if i % 2 else -1) * 0.9
                rr = r0 * (0.6 + 1.4 * u)
                cx = x + dx * (i / (n - 1) - 0.5) * 2.0
                cy = y - 20 - 60 * u * (0.4 + 0.6 * math.sin(ang))
                d.ellipse([(cx - rr) * 2, (cy - rr) * 2, (cx + rr) * 2, (cy + rr) * 2], fill=(255, 244, 226, int(a0 * (1 - u))))
        for t0, pos in ((3.35, upos), (3.4, bpos)):
            if t0 <= t < t0 + 0.6: puff(pos[0], pos[1], (t - t0) / 0.6, 26, 150)
        # take-off dust (uncle 7.95-8.6 at his launch spot)
        if 7.95 <= t < 8.8:
            u = (t - 7.95) / 0.85
            puff(0.66 * W + 20, 1130, u, 36, 190, 7)
        # speed lines while uncle runs
        if t > 8.5:
            a = clamp((t - 8.5) / 0.2) * (1 - clamp((t - 9.3) / 0.3))
            rnd = np.random.default_rng(int(t * 24))
            for i in range(14):
                y = rnd.uniform(500, 1200); x0 = rnd.uniform(0, W * 1.2); ln = rnd.uniform(160, 420)
                d.line([(x0 * 2, y * 2), ((x0 - ln) * 2, y * 2)], fill=(255, 250, 238, int(170 * a)), width=int(rnd.uniform(3, 7)))
        a = np.array(ov.resize((W, H), Image.LANCZOS)).astype(np.float32)
        al = a[..., 3:4] / 255
        return out * (1 - al) + a[..., :3] * al


# Character.screen_point: map an original-art point on a part to screen coordinates
def _screen_point(self, pos, pose, part, pt, root=None, face=False, flip=False):
    s = self.s
    fx, fy = self.feet
    P = T(pos[0], pos[1]) @ S(s, s) @ T(-fx, -fy)
    r = root or {}
    Rt = about((fx, fy), T(r.get("tx", 0), r.get("ty", 0)) @ R(r.get("rot", 0)) @ S(r.get("sx", 1), r.get("sy", 1)))
    world = {"root": Rt}
    for pn in self.order:
        p = self.parts[pn]; ps = pose.get(pn, {}); piv = p["pivot"]
        L = about(piv, T(ps.get("tx", 0), ps.get("ty", 0)) @ R(ps.get("rot", 0)) @ S(ps.get("sx", 1), ps.get("sy", 1)))
        world[pn] = world[p["parent"]] @ L
    v = P @ world[part] @ np.array([pt[0], pt[1], 1.0])
    return (float(v[0]), float(v[1]))


Character.screen_point = _screen_point


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--frames", default=None)
    ap.add_argument("--dump", default=None, help="dump PNG frames to this dir instead of encoding")
    ap.add_argument("--no-audio", action="store_true")
    a = ap.parse_args()
    work = os.path.join(os.path.dirname(os.path.abspath(a.out)), "rig_frames")
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    wav = os.path.join(work, "audio.wav")
    env = build_audio(wav) if not a.no_audio else {}
    sc = Scene(env); sc.uface = dict(eyes="laugh")
    n = int(DUR * a.fps)
    i0, i1 = (0, n)
    if a.frames:
        i0, i1 = [int(x) for x in a.frames.split(":")]
    for i in range(i0, min(i1, n)):
        fr = sc.frame(i / a.fps)
        cv2.imwrite(os.path.join(work, f"f{i:05d}.png"), cv2.cvtColor(fr, cv2.COLOR_RGB2BGR))
        if i % 24 == 0: print("frame", i, "/", n, flush=True)
    if a.frames or a.dump: return
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps), "-i", os.path.join(work, "f%05d.png")]
    if not a.no_audio: cmd += ["-i", wav]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"]
    if not a.no_audio: cmd += ["-c:a", "aac", "-b:a", "128k", "-shortest"]
    cmd += ["-movflags", "+faststart", a.out]
    subprocess.check_call(cmd)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
