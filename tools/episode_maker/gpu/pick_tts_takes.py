#!/usr/bin/env python3
"""Pick the better of the two TTS takes per line and copy it to tts/gpu/<line key>.wav.
    python3 pick_tts_takes.py <dir with <id>.wav and <id>__v2.wav> [--out ../tts/gpu] [--report report.txt]
Score (lower is better): QC flags from results.json, speaking rate far from the character's median (rambling or rushed),
pitch far from the character's median pitch (keeps one voice per character), clipping, leading/trailing noise, silence inside."""
import argparse, glob, json, os, shutil, sys
import numpy as np
import soundfile as sf


def trim(w, sr):
    a = np.abs(w)
    idx = np.where(a > 0.02 * a.max())[0]
    return w[idx[0]: idx[-1] + 1] if len(idx) else w


def f0_median(w, sr):
    w = w[:: int(sr // 8000)] if sr >= 16000 else w
    sr = 8000
    fl, hop = 320, 160
    ps = []
    for i in range(0, len(w) - fl, hop):
        f = w[i:i + fl] - w[i:i + fl].mean()
        if np.sqrt((f ** 2).mean()) < 0.02:
            continue
        ac = np.correlate(f, f, "full")[fl - 1:]
        lo, hi = int(sr / 400), int(sr / 70)
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] / (ac[0] + 1e-9) > 0.45:
            ps.append(sr / k)
    return float(np.median(ps)) if len(ps) > 5 else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("--out"); ap.add_argument("--report"); ap.add_argument("--tts-json"); ap.add_argument("--only-lines", help="comma list of line ids (default: all)")
    a = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = a.out or os.path.join(root, "tts", "gpu")
    meta = {}
    tj = a.tts_json or os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs", "ep01v43-voices", "tts.json")
    for ln in json.load(open(tj))["lines"]:
        meta[ln["id"]] = ln
    res = {}
    rj = os.path.join(a.src, "..", "results.json")
    if os.path.exists(rj):
        for r in json.load(open(rj))["results"]:
            res[r["id"]] = r
    info = {}
    for lid, ln in meta.items():
        for take, suf in ((1, ""), (2, "__v2"), (3, "__v3"), (4, "__v4"), (5, "__v5"), (6, "__v6")):
            p = os.path.join(a.src, lid + suf + ".wav")
            if not os.path.exists(p):
                continue
            w, sr = sf.read(p, dtype="float32")
            w = w.mean(axis=1) if w.ndim > 1 else w
            t = trim(w, sr)
            info[(lid, take)] = dict(path=p, dur=len(t) / sr, raw=len(w) / sr, f0=f0_median(t, sr), peak=float(np.abs(w).max()),
                                     flags=res.get(lid + suf, {}).get("flags", []), cps=len(ln["text"]) / max(len(t) / sr, 0.1))
    med = {}
    for who in {m["who"] for m in meta.values()}:
        xs = [v for (lid, _), v in info.items() if meta[lid]["who"] == who]
        med[who] = dict(f0=float(np.median([x["f0"] for x in xs if x["f0"] > 0] or [0])), cps=float(np.median([x["cps"] for x in xs])))
    os.makedirs(out, exist_ok=True)
    rep = []
    for lid, ln in meta.items():
        cands = []
        for take in (1, 2, 3, 4, 5, 6):
            v = info.get((lid, take))
            if not v:
                continue
            m = med[ln["who"]]
            s = 3.0 * len(v["flags"])
            s += abs(np.log(v["cps"] / m["cps"])) * 2.0
            if v["f0"] > 0 and m["f0"] > 0:
                s += abs(12 * np.log2(v["f0"] / m["f0"])) * 0.25
            s += 3.0 if v["peak"] > 0.99 else 0
            s += max(0.0, np.log(v['dur'] / min(i['dur'] for (l2, _), i in info.items() if l2 == lid))) * 3.0   # prefer the tighter take
            s += 1.0 if v["raw"] - v["dur"] > 1.2 else 0          # long silent tail
            cands.append((s, take, v))
        if not cands:
            rep.append(f"MISSING {lid} {ln['who']} {ln['text']!r}")
            continue
        cands.sort(key=lambda c: c[0])
        s, take, v = cands[0]
        shutil.copyfile(v["path"], os.path.join(out, lid + ".wav"))
        rep.append(f"{lid} {ln['who']:8s} take{take} score {s:4.1f} dur {v['dur']:4.1f}s f0 {v['f0']:5.0f} cps {v['cps']:4.1f} flags {v['flags']} | "
                   + " vs ".join(f"t{c[1]}:{c[0]:.1f}" for c in cands) + f" | {ln['text'][:50]}")
    rep.append("medians: " + json.dumps(med))
    txt = "\n".join(rep)
    print(txt)
    if a.report:
        open(a.report, "w").write(txt)


if __name__ == "__main__":
    main()
