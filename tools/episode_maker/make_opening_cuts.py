#!/usr/bin/env python3
"""Cut the 10-12 s intro sting and the promo version from generated opening-song takes, normalize and add the end accent.

    python3 make_opening_cuts.py --intro out/opening-song-variants/intro_a__s111.flac --full out/opening-song-variants/full_a__s101.flac \
        [--intro-len 11.0] [--full-len 50] [--full-start 0] [--assets assets/music]

Writes assets/music/opening_intro.wav (about 11.5 s, -12 LUFS, ends on a synthesized full-band accent: kick + distorted power
chord + crash, cut on the nearest beat) and assets/music/opening_full.wav (promo version, -14 LUFS, fade-out ending).
All sounds are generated here or by the music model; nothing is sampled from existing songs.
"""
import argparse, os, subprocess, tempfile
import numpy as np
import soundfile as sf

SR = 44100


def load(path):
    w, sr = sf.read(path, always_2d=True)
    if sr != SR:
        import librosa
        w = np.stack([librosa.resample(w[:, c], orig_sr=sr, target_sr=SR) for c in range(w.shape[1])], 1)
    if w.shape[1] == 1:
        w = np.repeat(w, 2, 1)
    return w[:, :2].astype("float64")


def beats(w):
    import librosa
    m = w.mean(1).astype("float32")
    tempo, fr = librosa.beat.beat_track(y=m, sr=SR, units="time", tightness=120)
    return float(np.atleast_1d(tempo)[0]), np.asarray(fr)


def accent(length=1.6):
    """Full-band hit: kick thump, noise crash and a distorted power chord (A, E, A) that decays."""
    n = int(SR * length)
    t = np.arange(n) / SR
    rng = np.random.default_rng(5)
    kick = np.sin(2 * np.pi * (45 + 90 * np.exp(-t * 25)) * t) * np.exp(-t * 7)
    crash = rng.standard_normal(n)
    b, a = (np.array([1, -1.0]), np.array([1, -0.6]))          # crude high-pass
    from scipy.signal import lfilter
    crash = lfilter(b, a, crash) * np.exp(-t * 2.6) * 0.35
    chord = np.zeros(n)
    for f in (110.0, 164.81, 220.0, 329.63):
        for det in (-0.4, 0.4):
            chord += 2 * ((t * (f + det)) % 1.0) - 1               # saw
    chord = np.tanh(2.5 * chord / 6) * np.exp(-t * 2.2) * 0.55      # distortion
    s = 0.9 * kick + crash + chord
    s[:200] *= np.linspace(0, 1, 200)
    return s / np.max(np.abs(s)) * 0.9


def lufs(w, target, tp=-1.0):
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "a.wav"), os.path.join(d, "b.wav")
        sf.write(a, w, SR, subtype="PCM_24")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a, "-af", f"loudnorm=I={target}:TP={tp}:LRA=7", "-ar", str(SR), b], check=True)
        out, _ = sf.read(b, always_2d=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--intro"); ap.add_argument("--full")
    ap.add_argument("--intro-len", type=float, default=11.0, help="where the music is cut (s); snapped to the nearest beat")
    ap.add_argument("--full-start", type=float, default=0.0)
    ap.add_argument("--full-len", type=float, default=50.0)
    ap.add_argument("--assets", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "music"))
    ap.add_argument("--no-accent", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.assets, exist_ok=True)
    if a.intro:
        w = load(a.intro)
        bpm, bt = beats(w)
        cut = bt[np.argmin(np.abs(bt - a.intro_len))] if len(bt) else a.intro_len
        print(f"intro: tempo {bpm:.0f} bpm, cut at beat {cut:.2f}s")
        n = int(cut * SR)
        body = w[:n].copy()
        fade = int(0.03 * SR)
        body[-fade:] *= np.linspace(1, 0, fade)[:, None]
        hit = accent() if not a.no_accent else np.zeros(1)
        out = np.zeros((n + len(hit), 2))
        out[:n] = body
        out[n:n + len(hit), 0] += hit * 0.9
        out[n:n + len(hit), 1] += hit * 0.9
        out = lufs(out, -12.0)
        print("intro seconds", round(len(out) / SR, 2))
        sf.write(os.path.join(a.assets, "opening_intro.wav"), out, SR, subtype="PCM_16")
    if a.full:
        w = load(a.full)
        s, e = int(a.full_start * SR), int(min(len(w), (a.full_start + a.full_len) * SR))
        seg = w[s:e].copy()
        f = int(2.0 * SR)
        seg[-f:] *= np.linspace(1, 0, f)[:, None] ** 1.5
        seg[: int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))[:, None]
        out = lufs(seg, -14.0)
        print("full seconds", round(len(out) / SR, 2))
        sf.write(os.path.join(a.assets, "opening_full.wav"), out, SR, subtype="PCM_16")


if __name__ == "__main__":
    main()
