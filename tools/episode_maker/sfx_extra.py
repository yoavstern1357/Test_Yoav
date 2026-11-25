"""More synthesized sound effects for the V4 episode (no samples, no licences). Registers itself into synth.SFX."""
import numpy as np
from scipy import signal
import synth
from synth import SR, _t, _norm, _bp, _lp, _hp, _env, RNG


def stamp(d=0.5):
    t = _t(d)
    thump = np.sin(2 * np.pi * (90 - 40 * t / d) * t) * np.exp(-t * 14)
    slap = _bp(RNG.standard_normal(len(t)), 800, 3500) * np.exp(-t * 40) * 0.6
    return _norm(thump + slap, 0.85)


def scratch(d=0.6):
    t = _t(d)
    f = 400 + 900 * np.sin(2 * np.pi * 3.2 * t) * np.exp(-t * 3)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + _hp(RNG.standard_normal(len(t)), 1200) * 0.5
    return _norm(x * _env(len(t), 0.01, 0.12), 0.6)


def snore(d=1.6):
    t = _t(d)
    x = np.zeros(len(t))
    for k in range(int(d / 0.8) + 1):
        a = int(k * 0.8 * SR); n = int(0.5 * SR)
        if a + n > len(t):
            break
        seg_t = np.arange(n) / SR
        e = np.sin(np.pi * seg_t / 0.5) ** 2
        x[a:a + n] += _lp(RNG.standard_normal(n), 420) * e * (0.7 + 0.3 * np.sin(2 * np.pi * 28 * seg_t))
    return _norm(x, 0.5)


def sniff(d=0.5):
    t = _t(d)
    x = _bp(RNG.standard_normal(len(t)), 1800, 5000) * np.sin(np.pi * t / d) ** 1.5
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 14 * t)
    return _norm(x, 0.5)


def squeak(d=0.25):
    t = _t(d)
    f = 1500 + 900 * t / d
    return _norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14), 0.5)


def rewind(d=1.2):
    t = _t(d)
    f = 300 + 1500 * np.sin(np.pi * t / d)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + _bp(RNG.standard_normal(len(t)), 1500, 6000) * 0.35
    x *= 0.7 + 0.3 * np.sin(2 * np.pi * 30 * t)
    return _norm(x * _env(len(t), 0.03, 0.15), 0.6)


def camel_bell(d=1.0):
    t = _t(d)
    x = np.zeros(len(t))
    for k, at in enumerate((0.0, 0.33, 0.62)):
        i = int(at * SR)
        tt = t[: len(t) - i]
        f = 1900 + 120 * k
        x[i:] += (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 2.76 * tt)) * np.exp(-tt * 9) * 0.5
    return _norm(x, 0.35)


def rooster(d=1.4):
    t = _t(d)
    f = np.interp(t, [0, 0.12, 0.35, 0.6, 1.0, d], [500, 900, 700, 1100, 800, 600])
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    x *= (0.6 + 0.4 * np.sin(2 * np.pi * 18 * t)) * _env(len(t), 0.02, 0.2)
    return _norm(_lp(x, 3500), 0.45)


def pen(d=0.9):
    t = _t(d)
    x = _bp(RNG.standard_normal(len(t)), 2500, 7000) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t) ** 2) * _env(len(t), 0.03, 0.1)
    return _norm(x, 0.4)


def gull(d=0.8):
    t = _t(d)
    f = 1100 + 500 * np.sin(2 * np.pi * 3 * t) + 400 * np.sin(np.pi * t / d)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 0.8
    return _norm(x, 0.3)


def creak(d=0.9):
    t = _t(d)
    f = 140 + 60 * np.sin(2 * np.pi * 5 * t) + 40 * t
    x = (signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * 0.4) * np.sin(np.pi * t / d)
    return _norm(_bp(x, 120, 900), 0.4)


def flap(d=0.7):
    t = _t(d)
    x = _bp(RNG.standard_normal(len(t)), 200, 1500) * (np.sin(2 * np.pi * 11 * t) > 0) * np.exp(-t * 3)
    return _norm(x, 0.5)


def chop(d=0.25):
    t = _t(d)
    x = _bp(RNG.standard_normal(len(t)), 400, 2600) * np.exp(-t * 38) + np.sin(2 * np.pi * 180 * t) * np.exp(-t * 30) * 0.6
    return _norm(x, 0.7)


def flutter(d=0.5):
    t = _t(d)
    x = _hp(RNG.standard_normal(len(t)), 2000) * (np.sin(2 * np.pi * 22 * t) > -0.2) * np.sin(np.pi * t / d)
    return _norm(x, 0.35)


def chimes(d=1.8):
    t = _t(d)
    x = np.zeros(len(t))
    for k, (f, at) in enumerate(((1568, 0.0), (2093, 0.35), (1760, 0.7), (2349, 1.1))):
        i = int(at * SR)
        if i >= len(t):
            continue
        tt = t[: len(t) - i]
        x[i:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 3.5) * 0.4
    return _norm(x, 0.3)


def train(d=2.0):
    t = _t(d)
    x = np.zeros(len(t))
    beat = 0.22
    for k in range(int(d / beat)):
        a = int(k * beat * SR); n = int(0.07 * SR)
        if a + n > len(t):
            break
        x[a:a + n] += _bp(RNG.standard_normal(n), 300, 1400) * np.exp(-np.arange(n) / SR * 50) * (1.0 if k % 2 == 0 else 0.6)
    x += _lp(RNG.standard_normal(len(t)), 300) * 0.15
    return _norm(x, 0.35)


def thud(d=0.4):
    t = _t(d)
    return _norm(np.sin(2 * np.pi * (70 - 30 * t / d) * t) * np.exp(-t * 12), 0.8)


def tear(d=0.5):
    t = _t(d)
    return _norm(_hp(RNG.standard_normal(len(t)), 1500) * np.exp(-t * 5) * (0.6 + 0.4 * np.sin(2 * np.pi * 60 * t)), 0.5)


def elevator(d=3.0):
    """Cheesy lounge elevator tune: electric piano chords with a soft bass and brush shaker."""
    t = _t(d)
    out = np.zeros(len(t))
    chords = [(261.6, 329.6, 392.0, 493.9), (220.0, 261.6, 329.6, 392.0), (174.6, 220.0, 261.6, 329.6), (196.0, 246.9, 293.7, 349.2)]
    beat = 0.5
    for k in range(int(d / beat)):
        ch = chords[(k // 2) % 4]
        a = int(k * beat * SR)
        n = int(0.5 * SR)
        if a + n > len(out):
            n = len(out) - a
        tt = np.arange(n) / SR
        for f in ch:
            out[a:a + n] += (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2 * tt)) * np.exp(-tt * 5) * 0.12
        out[a:a + n] += np.sin(2 * np.pi * ch[0] / 2 * tt) * np.exp(-tt * 6) * 0.25
        out[a:a + int(0.04 * SR)] += _hp(RNG.standard_normal(int(0.04 * SR)), 5000) * 0.05
    return _norm(out * _env(len(t), 0.05, 0.3), 0.4)


synth.SFX.update(stamp=stamp, scratch=scratch, snore=snore, sniff=sniff, squeak=squeak, rewind=rewind, camel_bell=camel_bell,
                 rooster=rooster, pen=pen, gull=gull, creak=creak, flap=flap, chop=chop, flutter=flutter, chimes=chimes,
                 train=train, thud=thud, tear=tear, elevator=elevator)
