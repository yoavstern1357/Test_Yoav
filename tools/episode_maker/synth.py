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


def impact(d=0.9):
    t = _t(d)
    f = 38 + 85 * np.exp(-t * 16)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5.5)
    crack = _bp(RNG.standard_normal(len(t)), 120, 3500) * np.exp(-t * 38) * 0.9
    thud = _lp(RNG.standard_normal(len(t)), 220) * np.exp(-t * 12) * 1.2
    return _norm(boom * 1.2 + crack + thud, 0.9)


def riser(d=2.0):
    t = _t(d)
    n = RNG.standard_normal(len(t))
    fc = 300 * (14 ** (t / d))
    out = np.zeros(len(t))
    for k in range(0, len(t), 2048):       # swept band-pass in blocks
        c = min(float(fc[k]), 15000)
        blk = n[max(0, k - 512):k + 2048]
        out[k:k + 2048] = _bp(blk, c * 0.7, min(c * 1.4, 20000), 2)[min(k, 512):][:len(out[k:k + 2048])]
    tone = np.sin(2 * np.pi * np.cumsum(180 * (4 ** (t / d))) / SR) * 0.25
    return _norm((out + tone) * (t / d) ** 1.6 * _env(len(t), 0.02, 0.03), 0.65)


def taiko(d=0.9):
    t = _t(d)
    f = 62 + 95 * np.exp(-t * 20)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    skin = _bp(RNG.standard_normal(len(t)), 200, 1600) * np.exp(-t * 55) * 0.7
    return _norm(body + skin, 0.9)


def swoosh_big(d=0.9):
    t = _t(d)
    n = RNG.standard_normal(len(t))
    env = np.sin(np.pi * np.clip(t / d, 0, 1) ** 0.7) ** 2
    out = np.zeros(len(t))
    for k in range(0, len(t), 2048):
        c = 400 * (12 ** (k / len(t)))
        blk = n[max(0, k - 512):k + 2048]
        out[k:k + 2048] = _bp(blk, c * 0.6, min(c * 1.8, 18000), 2)[min(k, 512):][:len(out[k:k + 2048])]
    low = _lp(n, 200) * 0.5
    return _norm((out + low) * env, 0.75)


def crack(d=0.45):
    t = _t(d)
    x = _hp(RNG.standard_normal(len(t)), 1800) * np.exp(-t * 70)
    x += _bp(RNG.standard_normal(len(t)), 600, 4000) * np.exp(-t * 14) * 0.25
    x += np.sin(2 * np.pi * 220 * t) * np.exp(-t * 60) * 0.5
    return _norm(x, 0.8)


def gong(d=3.5):
    t = _t(d)
    x = sum(a * np.sin(2 * np.pi * f * t + p) * np.exp(-t * dc)
            for f, a, dc, p in [(110, 1, 0.9, 0), (166, 0.7, 1.1, 1), (237, 0.6, 1.3, 2), (301, 0.5, 1.8, 0.5),
                                (413, 0.35, 2.2, 1.7), (587, 0.25, 3.0, 0.2), (113.5, 0.8, 0.95, 0)])
    x *= (1 + 0.15 * np.sin(2 * np.pi * 3.1 * t))
    x += _bp(RNG.standard_normal(len(t)), 300, 3000) * np.exp(-t * 20) * 0.4
    return _norm(x * _env(len(t), 0.004, 0.3), 0.7)


SFX = dict(hiss=hiss, lid=lid, toot=toot, growl=growl, rattle=rattle, tick=tick, tock=tock, ding=ding,
           bike_bell=bike_bell, boat_horn=boat_horn, whoosh=whoosh, pop=pop, sip=sip, sparkle=sparkle,
           boing=boing, page=page, chug=chug, clink=clink, heart=heart,
           impact=impact, riser=riser, taiko=taiko, swoosh_big=swoosh_big, crack=crack, gong=gong)


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


LEGACY_BPM = 96
MOOD_BPM = {"adventure": 120, "tension": 90, "epic": 110}
NEW_MOODS = set(MOOD_BPM)


def mood_bpm(mood):
    return MOOD_BPM.get(mood, LEGACY_BPM)


_pluck_cache = {}


def pluck(f, d=0.7, v=0.4):
    """Karplus-Strong plucked string (koto / guitar-ish)."""
    key = (round(f, 2), d)
    if key not in _pluck_cache:
        n = int(SR / f)
        x = np.zeros(int(d * SR))
        x[:n] = RNG.uniform(-1, 1, n)
        a = np.zeros(n + 2)
        a[0] = 1.0
        a[n] = -0.4985
        a[n + 1] = -0.4985
        y = signal.lfilter([1.0], a, x)
        y *= np.exp(-_t(d) * 2.2)
        _pluck_cache[key] = y / (np.abs(y).max() or 1)
    return _pluck_cache[key] * v


def flute(f, d=0.5, v=0.3):
    """Breathy flute: sine + a little filtered noise, with vibrato."""
    t = _t(d)
    vib = 1 + 0.008 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.2)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    tone = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    breath = _bp(RNG.standard_normal(len(t)), f * 1.5, f * 5, 2) * 0.35
    e = _env(len(t), 0.06, 0.12)
    return (tone * 0.8 + breath) * e * v


def _taiko_hit(v=1.0, big=False):
    d = 1.0 if big else 0.6
    t = _t(d)
    f = (52 if big else 70) + 90 * np.exp(-t * 22)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (4.5 if big else 8))
    skin = _bp(RNG.standard_normal(len(t)), 200, 1800) * np.exp(-t * 60) * 0.6
    return (body + skin) * v


def _drone(f, d, v=0.2):
    t = _t(d)
    x = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.003 * t) + 0.3 * np.sin(2 * np.pi * f * 1.5 * t)
         + 0.15 * np.sin(2 * np.pi * f * 2 * t)) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.35 * t))
    return x * _env(len(t), 0.6, 0.6) * v


def _tick_s(v=0.18):
    t = _t(0.05)
    return (_bp(RNG.standard_normal(len(t)), 2000, 6000) * np.exp(-t * 110) + np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 90) * 0.4) * v


def _strum(f, d, v):
    t = _t(d)
    x = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t) + 0.33 * np.sin(2 * np.pi * 3 * f * t))
    x = _lp(x, 1800, 1)
    return x * _env(len(t), 0.01, 0.08) * v


# adventure: D major pentatonic over D / Bm / G / A
ADV_CH = [("D", ["D3", "A3", "D4", "F4", "A4", "D5"]), ("Bm", ["B2", "F4", "B3", "D4", "F4", "B4"]),
          ("G", ["G2", "D4", "G3", "B3", "D4", "G4"]), ("A", ["A2", "E4", "A3", "C5", "E4", "A4"])]
ADV_ARP = {"D": ["D4", "F4", "A4", "D5", "A4", "F4", "A4", "D5"], "Bm": ["B3", "D4", "F4", "B4", "F4", "D4", "F4", "B4"],
           "G": ["G3", "B3", "D4", "G4", "D4", "B3", "D4", "G4"], "A": ["A3", "C5", "E4", "A4", "E4", "C5", "E4", "A4"]}
ADV_MEL = [["A4", "D5", "F5", "E5", "D5", "A4", "D5", "F5"], ["B4", "D5", "F5", "D5", "B4", "A4", "F4", "A4"],
           ["D5", "G5", "F5", "D5", "B4", "D5", "G5", "D5"], ["E5", "C5", "A4", "C5", "E5", "A5", "E5", "C5"]]
ADV_FIX = {"F4": "F4", "F5": "F5"}   # F natural is the minor-ish colour; keep it (Dorian-like adventure)

EPIC_CH = [("Dm", "D2", ["D3", "F3", "A3", "D4"]), ("Bb", "A#1", ["A#2", "D3", "F3", "A#3"]),
           ("F", "F2", ["F3", "A3", "C4", "F4"]), ("C", "C2", ["C3", "E3", "G3", "C4"])]


def hz2(name):
    sharp = name[1] == "#"
    n, o = name[0], int(name[-1])
    return 440.0 * 2 ** ((NOTE[n] + (1 if sharp else 0) + 12 * (o - 4) - 9) / 12)


def music(total, mood_at, bpm=LEGACY_BPM, change_times=()):
    """Render a music bed. mood_at(t) -> mood name.
    Legacy moods (cozy/tender/sparse) keep the original 96 BPM grid from t=0.
    New moods (adventure/tension/epic) use their own tempo, and the bar grid
    restarts at each mood change so cuts snapped to beats stay in time."""
    out = np.zeros(int(total * SR) + SR * 6, dtype=np.float64)

    g = [1.0]

    def place(sig, at, limit=None):
        sig = sig * g[0]
        if limit is not None and at >= limit - 1e-6:
            return
        i = int(at * SR)
        if i >= len(out):
            return
        j = min(len(out), i + len(sig))
        out[i:j] += sig[: j - i]

    t0, b, bar_i = 0.0, 0, 0
    changes = sorted(change_times)
    while t0 < total + 1:
        mood = mood_at(t0)
        bpm_ = mood_bpm(mood)
        g[0] = 0.62 if mood in NEW_MOODS else 1.0
        beat = 60.0 / bpm_
        bar = beat * 4
        limit = None
        nxt = [c for c in changes if c > t0 + 1e-6 and c < t0 + bar - 1e-6]
        if nxt and (mood in NEW_MOODS or mood_at(nxt[0] + 1e-6) in NEW_MOODS):
            limit = nxt[0]
        if mood == "off":
            pass
        elif mood in NEW_MOODS:
            k = bar_i % 4
            if mood == "adventure":
                name, notes = ADV_CH[k]
                for i in (0, 2):                                    # big taiko on 1 and 3
                    place(_taiko_hit(1.0, big=(i == 0 and k % 2 == 0)) * 0.9, t0 + i * beat, limit)
                place(_taiko_hit(0.45), t0 + 1.5 * beat, limit)
                place(_taiko_hit(0.5), t0 + 3.5 * beat, limit)
                place(_taiko_hit(0.35), t0 + 3 * beat, limit)
                for i in range(8):                                  # koto arpeggio, eighths
                    place(pluck(hz2(ADV_ARP[name][i]), 0.7, 0.34 if i % 2 == 0 else 0.24), t0 + i * beat / 2, limit)
                place(_strum(hz2(notes[0]), beat * 2, 0.16), t0, limit)    # warm bass
                place(_strum(hz2(notes[0]), beat * 2, 0.14), t0 + beat * 2, limit)
                mel = ADV_MEL[k]
                if bar_i >= 1:                                      # flute enters after one bar
                    for i, nn in enumerate(mel):
                        if i % 2 == 0 or k % 2 == 1:
                            place(flute(hz2(nn), beat * (0.95 if i % 2 == 0 else 0.5), 0.26), t0 + i * beat / 2, limit)
                for i in range(4):                                  # light shaker
                    place(_hp(RNG.standard_normal(int(0.05 * SR)), 5000) * np.exp(-_t(0.05) * 80) * 0.1, t0 + i * beat + beat / 2, limit)
            elif mood == "tension":
                f = [55.0, 55.0, 58.27, 51.91][k]
                place(_drone(f, bar + 0.8, 0.30), t0, limit)
                place(_drone(f * 1.5 * 1.0595 if k % 2 else f * 1.5, bar + 0.5, 0.07), t0, limit)
                for i in range(4):
                    place(_tick_s(0.22 if i == 0 else 0.14), t0 + i * beat, limit)
                if k == 3:                                          # accelerating ticks into the next bar
                    for i in range(8):
                        place(_tick_s(0.1), t0 + 3 * beat + i * beat / 8 + beat / 8, limit)
                if k % 2 == 1:                                      # eerie high swell
                    tt = _t(bar)
                    place(np.sin(2 * np.pi * 932 * tt) * np.sin(np.pi * tt / bar) ** 2 * 0.04, t0, limit)
            else:  # epic
                name, root, chord = EPIC_CH[k]
                phase = (bar_i % 8) / 7.0                           # rising over 8 bars
                place(_taiko_hit(1.0, True) * 1.0, t0, limit)
                place(_taiko_hit(0.8, True), t0 + 2 * beat, limit)
                place(_taiko_hit(0.6), t0 + 1.5 * beat, limit)
                place(_taiko_hit(0.7), t0 + 2.5 * beat, limit)
                for i in range(4):                                  # drum roll into beat 1 of next bar
                    place(_taiko_hit(0.25 + 0.1 * i), t0 + 3 * beat + i * beat / 4, limit)
                for i in range(8):                                  # low string ostinato
                    place(_strum(hz2(root), beat / 2, 0.2 if i % 2 == 0 else 0.13), t0 + i * beat / 2, limit)
                fs = [hz2(x) for x in chord]
                place(pad(fs + [f * 2 for f in fs[:2]], bar * 1.1, 0.12 + 0.18 * phase), t0, limit)
                if bar_i % 2 == 1:
                    for i, nn in enumerate([chord[2], chord[3], chord[1], chord[3]]):
                        place(flute(hz2(nn[:-1] + str(int(nn[-1]) + 1)), beat * 0.9, 0.16 + 0.1 * phase), t0 + i * beat, limit)
        else:
            chord = PROG[b % 4]
            low, arp = CHORDS[chord]
            if mood == "cozy":
                for i in range(8):                       # marimba eighths
                    f = hz(arp[(i * 2 + b) % len(arp)])
                    place(marimba(f, 0.55, 0.42 if i % 2 == 0 else 0.3), t0 + i * beat / 2)
                for i in (0, 2):                         # soft bass pluck
                    place(marimba(hz(low[0]), 0.6, 0.55), t0 + i * beat)
                for i in range(4):                       # light shaker
                    s = _hp(RNG.standard_normal(int(0.05 * SR)), 5000) * np.exp(-_t(0.05) * 80) * 0.12
                    place(s, t0 + i * beat + beat / 2)
                place(pad([hz(x) for x in low], bar, 0.10), t0)
            elif mood == "sparse":
                place(marimba(hz(low[0]), 0.9, 0.4), t0)
                place(marimba(hz(arp[2]), 0.7, 0.25), t0 + beat * 2)
            elif mood == "tender":
                place(pad([hz(x) for x in low] + [hz(arp[0])], bar * 1.1, 0.22), t0)
                for i, kk in enumerate([0, 2, 4, 3]):
                    place(musicbox(hz(arp[kk]) * 2, 1.4, 0.30), t0 + i * beat)
        b += 1
        bar_i = bar_i + 1 if mood in NEW_MOODS else 0
        t0 = limit if limit is not None else t0 + bar
    return out[: int(total * SR)].astype(np.float32)
