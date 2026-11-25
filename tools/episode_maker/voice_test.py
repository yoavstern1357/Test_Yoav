#!/usr/bin/env python3
"""Render the 6 sample lines (voice_test_lines.json) with several voice engines and build one comparison file.

    python3 voice_test.py                          # kokoro (current) + supertonic + pocket -> out/voice-test/
    python3 voice_test.py --engines kokoro,pocket
    python3 voice_test.py --engines kokoro,gpu --gpu-dir /path/to/results/audio   # also compare the Kaggle GPU render

Outputs (out/voice-test/, git-ignored): <engine>/<id>_<who>.wav, comparison.m4a (+ .mp3), comparison.txt (timestamps),
metrics.txt (real-time factor, pitch median/range per line). Order in the comparison: for each line, every engine in turn,
each one announced by 1, 2, 3... short beeps (1 = first engine listed, ...).
"""
import argparse, json, os, subprocess, sys, time
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_episode as me          # noqa: E402  (reuses the exact production cast, pitch shifts and trimming)
from synth import SR               # noqa: E402


def f0_stats(y, sr, fmin=60, fmax=450):
    """Median pitch (Hz) and 10-90 percentile range (semitones) with a plain autocorrelation tracker (a rough proxy for liveliness)."""
    fl, hop, lo, hi = int(sr * 0.04), int(sr * 0.01), int(sr / fmax), int(sr / fmin)
    out = []
    for i in range(0, len(y) - fl - hi, hop):
        x = y[i:i + fl] - y[i:i + fl].mean()
        if np.sqrt((x ** 2).mean()) < 0.02:
            continue
        x2 = y[i:i + fl + hi] - y[i:i + fl + hi].mean()
        ac = np.correlate(x2, x, "valid")[:hi + 1]
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] > 0.5 * ac[0]:
            out.append(sr / k)
    if len(out) < 5:
        return 0.0, 0.0
    f = np.array(out)
    return float(np.median(f)), float(12 * np.log2(np.percentile(f, 90) / np.percentile(f, 10)))


def beeps(n):
    t = np.arange(int(0.12 * SR)) / SR
    b = (0.25 * np.sin(2 * np.pi * 880 * t) * np.hanning(len(t))).astype(np.float32)
    gap = np.zeros(int(0.08 * SR), np.float32)
    return np.concatenate([np.concatenate([b, gap]) for _ in range(n)] + [np.zeros(int(0.25 * SR), np.float32)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engines", default="kokoro,supertonic,pocket")
    ap.add_argument("--lines", default=os.path.join(HERE, "voice_test_lines.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "out", "voice-test"))
    ap.add_argument("--gpu-dir", default=None, help="folder with <line_key>.wav from the GPU job (engine 'gpu')")
    a = ap.parse_args()
    lines = json.load(open(a.lines))["lines"]
    engines = a.engines.split(",")
    os.makedirs(a.out, exist_ok=True)
    me.CACHE = os.path.join(a.out, ".cache")            # never reuse or pollute the production cache
    rendered, metrics = {}, []
    for eng in engines:
        spec = {} if eng == "kokoro" else {"voice_engine": eng}
        me.set_cast(spec)
        if eng == "gpu" and a.gpu_dir:
            for c in me.CAST.values():
                c["dir"] = os.path.abspath(a.gpu_dir)
        os.makedirs(os.path.join(a.out, eng), exist_ok=True)
        t_all = 0.0
        for ln in lines:
            t0 = time.time()
            try:
                w = me.tts(ln["who"], ln["text"])
            except FileNotFoundError as ex:
                print(f"[{eng}] skipped {ln['id']}: {ex}")
                continue
            dt = time.time() - t0
            dur = len(w) / SR
            med, rng = f0_stats(w.astype(np.float64), SR)
            rendered[(eng, ln["id"])] = w
            sf.write(os.path.join(a.out, eng, f"{ln['id']}_{ln['who']}.wav"), w, SR)
            metrics.append(f"{eng:10s} {ln['id']} {ln['who']:9s} {dur:5.2f}s audio  render {dt:5.2f}s  RTF {dt / dur:5.2f}  f0 median {med:5.0f} Hz  range {rng:4.1f} st")
            t_all += dt
        print(f"[{eng}] done")
    open(os.path.join(a.out, "metrics.txt"), "w").write("\n".join(metrics) + "\n")
    print("\n".join(metrics))
    # concatenated comparison
    parts, index, t = [], [], 0.0
    for ln in lines:
        for n, eng in enumerate(engines, 1):
            w = rendered.get((eng, ln["id"]))
            if w is None:
                continue
            seg = np.concatenate([beeps(n), w, np.zeros(int(0.9 * SR), np.float32)])
            index.append(f"{t:6.1f}s  line {ln['id']} {ln['who']:9s} engine {eng} ({n} beep{'s' if n > 1 else ''}): {ln['text']}")
            parts.append(seg)
            t += len(seg) / SR
        parts.append(np.zeros(int(0.8 * SR), np.float32)); t += 0.8
    wavp = os.path.join(a.out, "comparison.wav")
    sf.write(wavp, np.concatenate(parts), SR)
    for ext, args in (("m4a", ["-c:a", "aac", "-b:a", "128k"]), ("mp3", ["-c:a", "libmp3lame", "-b:a", "128k"])):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wavp, *args, os.path.join(a.out, f"comparison.{ext}")], check=True)
    os.remove(wavp)
    open(os.path.join(a.out, "comparison.txt"), "w").write("\n".join(index) + "\n")
    print("\n".join(index))
    print("wrote", os.path.join(a.out, "comparison.m4a"))


if __name__ == "__main__":
    main()
