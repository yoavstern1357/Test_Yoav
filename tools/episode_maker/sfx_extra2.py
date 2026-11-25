"""More original synthesized sound effects for the series intro and Episode 1 v4.3 (added to synth.SFX)."""
import numpy as np
import synth
from synth import SR, _t, _norm, _bp, _lp, _hp, _env, RNG


def shing(d=0.35):
    """Metal-star whoosh: a short bright ring with a falling edge."""
    t = _t(d)
    ring = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((2400, 1), (3150, .7), (4300, .5), (5200, .3))) * np.exp(-t * 14)
    sw = _hp(RNG.standard_normal(len(t)), 2500) * np.exp(-t * 18) * 0.6
    return _norm((ring * 0.5 + sw) * _env(len(t), 0.002, 0.08), 0.8)


def chomp(d=0.5):
    """Big cartoon chomp: low thump, hollow snap, wet click."""
    t = _t(d)
    thump = np.sin(2 * np.pi * (140 - 90 * t / d) * t) * np.exp(-t * 14)
    snap = _bp(RNG.standard_normal(len(t)), 500, 4000) * np.exp(-t * 40)
    clack = np.zeros(len(t))
    k = int(0.11 * SR)
    clack[k:k + int(0.05 * SR)] = (_bp(RNG.standard_normal(int(0.05 * SR)), 900, 5000) * np.exp(-_t(0.05) * 60))[:len(clack[k:k + int(0.05 * SR)])]
    return _norm(thump * 0.9 + snap * 0.6 + clack * 0.7, 0.95)


def crunch(d=0.5):
    """Bite into a soft dumpling: two crunchy clicks and a squishy burst."""
    t = _t(d)
    x = np.zeros(len(t))
    for st, g in ((0.0, 1.0), (0.12, 0.7)):
        n = int(0.09 * SR)
        s = int(st * SR)
        c = _bp(RNG.standard_normal(n), 1500, 7000) * np.exp(-_t(0.09) * 45) * g
        x[s:s + n] += c[:max(0, min(n, len(x) - s))]
    sq = _bp(RNG.standard_normal(len(t)), 200, 1400) * np.exp(-t * 9) * (np.sin(2 * np.pi * 22 * t) * 0.5 + 0.5)
    sq[:int(0.14 * SR)] = 0
    return _norm(x + sq * 0.5, 0.85)


def splash(d=0.9):
    t = _t(d)
    n = _bp(RNG.standard_normal(len(t)), 400, 6500) * (np.exp(-t * 4.5) * (1 - np.exp(-t * 60)))
    drops = np.zeros(len(t))
    for st in (0.18, 0.31, 0.47, 0.62):
        s = int(st * SR)
        L = int(0.07 * SR)
        if s + L < len(t):
            drops[s:s + L] += np.sin(2 * np.pi * (900 + 600 * RNG.random()) * _t(0.07)) * np.exp(-_t(0.07) * 45) * 0.4
    return _norm(n + drops, 0.8)


def plop(d=0.3):
    t = _t(d)
    f = 520 - 380 * np.minimum(t / 0.12, 1)
    return _norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * _env(len(t), 0.002, 0.05), 0.8)


def rolling(d=1.0):
    """Heavy round thing rolling and thumping."""
    t = _t(d)
    x = _lp(RNG.standard_normal(len(t)), 180) * 2.0
    pulse = (np.sin(2 * np.pi * 4.2 * t) > 0.6).astype(float)
    th = np.sin(2 * np.pi * 70 * t) * np.exp(-((t * 4.2) % 1) * 9)
    return _norm((x * 0.7 + th) * _env(len(t), 0.05, 0.2) * (0.6 + 0.4 * pulse), 0.85)


def sting(d=1.6):
    """Short bright title sting: a rising pentatonic arpeggio ending on a chord (marimba/koto-like)."""
    t = _t(d)
    x = np.zeros(len(t))
    for i, (f, st) in enumerate(((523.25, 0.0), (587.33, 0.1), (659.25, 0.2), (783.99, 0.3), (880.0, 0.4))):
        s = int(st * SR)
        tt = _t(d - st)
        x[s:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 4) * 0.5 + np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt * 9) * 0.15
    for f in (261.63, 392.0, 523.25, 659.25):
        x += np.sin(2 * np.pi * f * t) * np.exp(-t * 1.6) * 0.18 * (t > 0.5)
    return _norm(x * _env(len(t), 0.003, 0.5), 0.8)


def bloop(d=0.25):
    t = _t(d)
    f = 300 + 500 * np.minimum(t / 0.1, 1)
    return _norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16), 0.7)


def laugh(d=0.9):
    """Cartoon giggle for the pool shot: a short run of pitched pulses (not a voice, just a hint)."""
    t = _t(d)
    x = np.zeros(len(t))
    for i in range(6):
        s = int((0.05 + i * 0.12) * SR)
        L = int(0.09 * SR)
        f0 = 640 + 80 * np.sin(i * 1.7) - i * 20
        tt = _t(0.09)
        if s + L < len(t):
            x[s:s + L] += (np.sin(2 * np.pi * f0 * tt) + 0.4 * np.sin(2 * np.pi * 2 * f0 * tt)) * np.exp(-tt * 22)
    return _norm(_lp(x, 3000) * 0.9, 0.35)


synth.SFX.update(shing=shing, chomp=chomp, crunch=crunch, splash=splash, plop=plop, rolling=rolling, sting=sting, bloop=bloop, laugh=laugh)
