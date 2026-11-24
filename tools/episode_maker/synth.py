"""Original, copyright-free sound design for The Dumpling Boy.

Everything here is generated from math (sines, noise, envelopes), so there is
no sampled or licensed audio. Mono float32 arrays at SR Hz.
"""
import numpy as np
from scipy import signal

SR = 44100
RNG = np.random.default_rng(7)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _norm(x, peak=0.9):
    m = float(np.max(np.abs(x))) or 1.0
    return (x / m * peak).astype(np.float32)


def _bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def _lp(x, hi, order=2):
    sos = signal.butter(order, hi, btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def _hp(x, lo, order=2):
    sos = signal.butter(order, lo, btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def _env(n, a=0.01, r=0.1):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] = np.minimum(e[-nr:], np.linspace(1, 0, nr))
    return e


# ---------------------------------------------------------------- SFX
def hiss(d=1.6):
    t = _t(d)
    n = _hp(RNG.standard_normal(len(t)), 2500)
    return _norm(n * _env(len(t), 0.15, 0.5) * (0.6 + 0.4 * np.sin(2 * np.pi * 1.3 * t)), 0.5)


def lid(d=0.6):
    t = _t(d)
    clack = _bp(RNG.standard_normal(len(t)), 900, 2600) * np.exp(-t * 40)
    creak = np.sin(2 * np.pi * (300 + 220 * t / d) * t) * np.exp(-t * 6) * 0.25
    return _norm(clack + creak, 0.6)


def toot(d=1.3):
    t = _t(d)
    vib = 1 + 0.015 * np.sin(2 * np.pi * 6 * t)
    f = 740 * vib * (1 - 0.08 * t / d)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.6 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) + 0.2 * np.sin(2 * np.pi * np.cumsum(f * 3) / SR)
    return _norm(x * _env(len(t), 0.03, 0.35), 0.6)


def growl(d=1.6):
    t = _t(d)
    f = 70 - 25 * t / d
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t))
    x += _lp(RNG.standard_normal(len(t)), 160) * 2.0 * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t))
    return _norm(x * _env(len(t), 0.2, 0.4), 0.7)


def rattle(d=0.9):
    t = _t(d)
    x = np.zeros(len(t))
    for k in range(14):
        s = int(RNG.uniform(0, d - 0.1) * SR)
        c = _bp(RNG.standard_normal(2000), 700, 3200) * np.exp(-np.arange(2000) / 260)
        x[s:s + 2000] += c[: len(x) - s] * RNG.uniform(0.4, 1)
    return _norm(x, 0.5)


def tick(d=0.12):
    t = _t(d)
    x = _bp(RNG.standard_normal(len(t)), 1500, 5000) * np.exp(-t * 90) + np.sin(2 * np.pi * 1700 * t) * np.exp(-t * 70) * 0.5
    return _norm(x, 0.55)


def tock(d=0.14):
    t = _t(d)
    x = _bp(RNG.standard_normal(len(t)), 700, 2500) * np.exp(-t * 80) + np.sin(2 * np.pi * 1100 * t) * np.exp(-t * 60) * 0.5
    return _norm(x, 0.55)


def ding(d=1.4):
    t = _t(d)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * dcy) for f, a, dcy in [(1568, 1, 3.5), (2352, 0.5, 5), (3136, 0.25, 7)])
    return _norm(x, 0.55)


def bike_bell(d=0.9):
    t = _t(d)
    ring = (np.sin(2 * np.pi * 2100 * t) + 0.5 * np.sin(2 * np.pi * 3150 * t)) * np.exp(-t * 6) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * t))
    return _norm(ring, 0.45)


def boat_horn(d=1.6):
    t = _t(d)
    x = np.sin(2 * np.pi * 196 * t) + 0.8 * np.sin(2 * np.pi * 247 * t) + 0.3 * np.sin(2 * np.pi * 392 * t)
    return _norm(x * _env(len(t), 0.15, 0.7), 0.5)


def whoosh(d=0.6):
    t = _t(d)
    n = RNG.standard_normal(len(t))
    sweep = np.sin(np.pi * t / d)
    return _norm(_bp(n, 400, 5000) * sweep, 0.5)


def pop(d=0.18):
    t = _t(d)
    f = 700 * np.exp(-t * 14) + 180
    return _norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18), 0.6)


def sip(d=0.5):
    t = _t(d)
    n = _bp(RNG.standard_normal(len(t)), 900, 2600) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t)) * _env(len(t), 0.05, 0.2)
    return _norm(n, 0.45)


def sparkle(d=0.9):
    x = np.zeros(int(d * SR))
    for i, f in enumerate([2093, 2637, 3136, 3951]):
        s = int(i * 0.07 * SR)
        t = _t(0.5)
        p = np.sin(2 * np.pi * f * t) * np.exp(-t * 9)
        x[s:s + len(p)] += p[: len(x) - s]
    return _norm(x, 0.35)


def boing(d=0.5):
    t = _t(d)
    f = 240 + 160 * np.sin(2 * np.pi * 5 * t) * np.exp(-t * 6)
    return _norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6), 0.5)


def page(d=0.5):
    t = _t(d)
    n = _bp(RNG.standard_normal(len(t)), 1200, 6000) * np.sin(np.pi * t / d) ** 2
    return _norm(n, 0.4)


def chug(d=2.0):
    t = _t(d)
    n = _bp(RNG.standard_normal(len(t)), 300, 1800)
    gate = (np.sin(2 * np.pi * 5 * t) > 0.2).astype(float) * 0.7 + 0.3
    return _norm(n * gate * _env(len(t), 0.2, 0.4), 0.35)


def clink(d=0.4):
    t = _t(d)
    x = np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 18) + 0.6 * np.sin(2 * np.pi * 4700 * t) * np.exp(-t * 24)
    return _norm(x, 0.35)


def heart(d=0.6):
    t = _t(d)
    f = 520 + 280 * t / d
    return _norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5), 0.3)


SFX = dict(hiss=hiss, lid=lid, toot=toot, growl=growl, rattle=rattle, tick=tick, tock=tock, ding=ding,
           bike_bell=bike_bell, boat_horn=boat_horn, whoosh=whoosh, pop=pop, sip=sip, sparkle=sparkle,
           boing=boing, page=page, chug=chug, clink=clink, heart=heart)


# ---------------------------------------------------------------- Ambience
def ambience(kind, d):
    t = _t(d)
    n = RNG.standard_normal(len(t))
    if kind == "shop":       # warm room murmur
        x = _lp(n, 520) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.23 * t))
    elif kind == "street":   # city hum
        x = _bp(n, 150, 1400) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.4 * t))
    elif kind == "water":    # canal
        x = _lp(n, 700) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.35 * t) ** 2)
    elif kind == "night":
        x = _lp(n, 300) * 0.8 + 0.1 * np.sin(2 * np.pi * 4200 * t) * (np.sin(2 * np.pi * 0.7 * t) > 0.9)
    else:
        return np.zeros(len(t), dtype=np.float32)
    return _norm(x * _env(len(t), 0.4, 0.4), 0.3)


# ---------------------------------------------------------------- Music
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def hz(name):
    n, o = name[0], int(name[-1])
    return 440.0 * 2 ** ((NOTE[n] + 12 * (o - 4) - 9) / 12)


def marimba(f, d=0.5, v=0.5):
    t = _t(d)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 26) + 0.12 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 12)
    return x * v


def musicbox(f, d=1.2, v=0.3):
    t = _t(d)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 3.2) + 0.25 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 9)) * v


def pad(freqs, d, v=0.12):
    t = _t(d)
    x = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) for f in freqs) / len(freqs)
    return x * _env(len(t), 0.5, 0.8) * v


CHORDS = {
    "C": (["C3", "E3", "G3"], ["C4", "E4", "G4", "A4", "C5"]),
    "Am": (["A2", "C3", "E3"], ["A3", "C4", "E4", "G4", "A4"]),
    "F": (["F2", "A2", "C3"], ["F4", "A4", "C5", "G4", "A4"]),
    "G": (["G2", "B2", "D3"], ["G4", "B4", "D5", "A4", "B4"]),
}
PROG = ["C", "Am", "F", "G"]


def music(total, mood_at, bpm=96):
    """Render a music bed. mood_at(t) -> 'cozy' | 'tender' | 'sparse' | 'off'."""
    out = np.zeros(int(total * SR) + SR * 3, dtype=np.float64)
    beat = 60.0 / bpm
    bar = beat * 4
    nbar = int(total / bar) + 2
    for b in range(nbar):
        t0 = b * bar
        mood = mood_at(t0)
        if mood == "off":
            continue
        chord = PROG[b % 4]
        low, arp = CHORDS[chord]
        place = lambda sig, at: out.__setitem__(slice(int(at * SR), int(at * SR) + len(sig)), out[int(at * SR): int(at * SR) + len(sig)] + sig[: len(out) - int(at * SR)])
        if mood == "cozy":
            for i in range(8):                       # marimba eighths
                f = hz(arp[(i * 2 + b) % len(arp)])
                place(marimba(f, 0.55, 0.42 if i % 2 == 0 else 0.3), t0 + i * beat / 2)
            for i in (0, 2):                         # soft bass pluck
                place(marimba(hz(low[0]) , 0.6, 0.55), t0 + i * beat)
            for i in range(4):                       # light shaker
                s = _hp(RNG.standard_normal(int(0.05 * SR)), 5000) * np.exp(-_t(0.05) * 80) * 0.12
                place(s, t0 + i * beat + beat / 2)
            place(pad([hz(x) for x in low], bar, 0.10), t0)
        elif mood == "sparse":
            place(marimba(hz(low[0]), 0.9, 0.4), t0)
            place(marimba(hz(arp[2]), 0.7, 0.25), t0 + beat * 2)
        elif mood == "tender":
            place(pad([hz(x) for x in low] + [hz(arp[0])], bar * 1.1, 0.22), t0)
            for i, k in enumerate([0, 2, 4, 3]):
                place(musicbox(hz(arp[k]) * 2, 1.4, 0.30), t0 + i * beat)
    return out[: int(total * SR)].astype(np.float32)
