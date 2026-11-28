#!/usr/bin/env python3
"""Animatic voices: pick the best CPU voice per character, render every line at natural speed, write word timestamps.

    python3 animatic/voices.py pick      # renders all lines with each candidate, scores them (Whisper word error, pitch), writes out/animatic-v5/voice_pick.json
    python3 animatic/voices.py render    # renders the chosen cast: out/animatic-v5/voices/<ep>/<clip>.wav + .json (words + start/end)

Candidates come from production/v4/voice-samples-report.md (section 5). Speed is never above 1.1x; pitch shifts only where noted.
Word timestamps: energy-snapped proportional alignment (no aligner exists on CPU here; Whisper via sherpa-onnx gives no timestamps),
checked by a Whisper transcript of every line.
"""
import json, os, re, sys, time
import numpy as np, soundfile as sf, librosa
HERE = os.path.dirname(os.path.abspath(__file__))
EM = os.path.dirname(HERE)
sys.path.insert(0, EM); sys.path.insert(0, HERE)
from lines import LINES
import tts_engines as te

OUT = os.path.join(EM, "out", "animatic-v5")
SR = 24000
VS = os.path.join(EM, "out", "voice-samples")
TARGET_HZ = {"boy": 250, "uncle": 100, "grandma": 190, "narrator": 100}
# candidates: (label, engine, voice, pitch ratio, base speed)
CANDS = {
    "boy": [("kokoro af_heart x1.20", "kokoro", "af_heart", 1.20, 1.0), ("kokoro am_puck x1.12", "kokoro", "am_puck", 1.12, 1.0),
            ("pocket ref am_liam x1.2", "pocket", "pocketref_boy_2.wav", 1.0, 1.0), ("kokoro bf_lily x1.10", "kokoro", "bf_lily", 1.10, 1.0)],
    "uncle": [("kokoro bm_lewis x0.90", "kokoro", "bm_lewis", 0.90, 1.0), ("kokoro am_fenrir x0.90", "kokoro", "am_fenrir", 0.90, 1.0),
              ("supertonic 8 x0.94", "supertonic", 8, 0.94, 0.95), ("kokoro am_michael x0.90", "kokoro", "am_michael", 0.90, 1.0)],
    "grandma": [("kokoro af_sarah x0.96", "kokoro", "af_sarah", 0.96, 0.95), ("kokoro bf_isabella x0.92", "kokoro", "bf_isabella", 0.92, 0.95),
                ("pocket ref af_sarah", "pocket", "pocketref_grandma_1.wav", 1.0, 0.95), ("kokoro bf_emma x0.90", "kokoro", "bf_emma", 0.90, 0.95)],
    "narrator": [("kokoro bm_fable x0.88", "kokoro", "bm_fable", 0.88, 0.92), ("kokoro bm_george x0.90", "kokoro", "bm_george", 0.90, 0.92),
                 ("supertonic 9 x0.90", "supertonic", 9, 0.90, 0.9), ("kokoro bm_lewis x0.85", "kokoro", "bm_lewis", 0.85, 0.92)],
}
_k = {}


def pshift(w, st):
    if abs(st) <= 0.05:
        return w
    pad = np.zeros(SR // 4, np.float32)
    x = np.nan_to_num(np.concatenate([pad, w, pad]).astype(np.float32))
    try:
        y = librosa.effects.pitch_shift(x, sr=SR, n_steps=float(st))
    except Exception:           # librosa 1.0 phase-vocoder edge case on some inputs: other FFT size
        y = librosa.effects.pitch_shift(x, sr=SR, n_steps=float(st), n_fft=1024, hop_length=256)
    return y[len(pad):len(pad) + len(w)]


def raw(cand, text, speed_mult=1.0, extra_st=0.0):
    label, eng, voice, ratio, base = cand
    sp = min(1.1, base * speed_mult)
    if eng == "kokoro":
        if "k" not in _k:
            from kokoro_onnx import Kokoro
            _k["k"] = Kokoro(os.path.join(EM, "tts", "kokoro-v1.0.onnx"), os.path.join(EM, "tts", "voices-v1.0.bin"))
        w, sr = _k["k"].create(text, voice=voice, speed=sp, lang="en-us")
    elif eng == "supertonic":
        w, sr = te.synth({"engine": "supertonic", "sid": voice, "speed": sp}, text)
    else:
        w, sr = te.synth({"engine": "pocket", "ref": os.path.join(VS, voice), "speed": sp}, text)
    w = np.asarray(w, np.float32)
    if sr != SR:
        w = librosa.resample(w, orig_sr=sr, target_sr=SR)
    st = 12 * np.log2(ratio) + extra_st if eng != "pocket" else extra_st
    return pshift(w, st)


def trim(w):
    t, _ = librosa.effects.trim(w, top_db=38)
    return t


def mkrec():
    import sherpa_onnx as s
    d = os.path.join(EM, "tts", "models", "sherpa-onnx-whisper-small.en")
    return s.OfflineRecognizer.from_whisper(encoder=f"{d}/small.en-encoder.int8.onnx", decoder=f"{d}/small.en-decoder.int8.onnx",
                                            tokens=f"{d}/small.en-tokens.txt", language="en", task="transcribe", num_threads=4)


def asr(rec, w):
    st = rec.create_stream(); st.accept_waveform(SR, w.astype(np.float32)); rec.decode_stream(st)
    return st.result.text.strip()


def norm(t):
    t = t.lower().replace("seventy-one", "seventy one").replace("nanxiang", "").replace("guangzhou", "")
    return re.sub(r"[^a-z0-9' ]", " ", t).split()


def wer(ref, hyp):
    r, h = norm(ref), norm(hyp)
    d = np.zeros((len(r) + 1, len(h) + 1), int)
    d[:, 0] = range(len(r) + 1); d[0, :] = range(len(h) + 1)
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + (r[i - 1] != h[j - 1]))
    return d[-1, -1] / max(1, len(r))


def pitch_stats(w):
    f = librosa.yin(w, fmin=60, fmax=500, sr=SR, frame_length=2048)
    rms = librosa.feature.rms(y=w, frame_length=2048, hop_length=512)[0][:len(f)]
    ok = rms > 0.3 * np.median(rms)
    f = f[:len(ok)][ok[:len(f)]]
    if len(f) < 5:
        return 0.0, 0.0, 0.0
    st = 12 * np.log2(f / np.median(f))
    return float(np.median(f)), float(np.percentile(st, 90) - np.percentile(st, 10)), float(np.mean(np.abs(np.diff(st))))


def pick():
    os.makedirs(OUT, exist_ok=True)
    rec = mkrec()
    res = {}
    allines = [(ep, c, who, kind, text, o) for ep, ls in LINES.items() for (c, who, kind, text, o) in ls]
    for who, cands in CANDS.items():
        mine = [x for x in allines if x[2] == who]
        res[who] = []
        for cand in cands:
            t0 = time.time(); ws, durs, words = [], [], 0
            wers = []
            f0s, rngs, jit = [], [], []
            for ep, c, _, kind, text, o in mine[:8]:        # first 8 lines per character are enough for a pick
                w = trim(raw(cand, o.get("tts", text), o.get("speed", 1.0), o.get("st", 0.0)))
                wers.append(wer(text, asr(rec, w)))
                f0, rg, jt = pitch_stats(w)
                f0s.append(f0); rngs.append(rg); jit.append(jt)
                durs.append(len(w) / SR); words += len(norm(text))
            e = dict(label=cand[0], wer=round(float(np.mean(wers)), 3), f0=round(float(np.median(f0s))), range_st=round(float(np.mean(rngs)), 1),
                     jitter=round(float(np.mean(jit)), 2), wps=round(words / sum(durs), 2), secs=round(time.time() - t0))
            tgt = TARGET_HZ[who]
            # score: understood (low WER) + alive (pitch range 5-9 st) + not robotic (frame-to-frame jitter below 1.3 st) + near target pitch
            e["score"] = round(float(-5 * e["wer"] + 0.15 * min(e["range_st"], 9) - 0.6 * max(0, e["jitter"] - 1.3) - abs(np.log2(max(e["f0"], 1) / tgt))), 3)
            res[who].append(e)
            print(who, e, flush=True)
    json.dump(res, open(os.path.join(OUT, "voice_pick.json"), "w"), indent=1)


def words_of(text):
    return [w for w in text.split() if re.search(r"[A-Za-z0-9]", w)]


def align(w, text):
    """Word start/end (s) inside the trimmed line: weights by syllables + chars, pauses at punctuation, boundaries snapped to energy minima."""
    ws = words_of(text)
    rms = librosa.feature.rms(y=w, frame_length=480, hop_length=240)[0]       # 10 ms
    n = len(rms); dur = len(w) / SR
    wt = []
    for x in ws:
        core = re.sub(r"[^A-Za-z0-9']", "", x)
        syl = max(1, len(re.findall(r"[aeiouy]+", core.lower())))
        wt.append(1.0 * syl + 0.12 * len(core))
        p = re.search(r"(\.\.\.|[.,!?:;])$", x)
        wt.append({"...": 1.6, ".": 0.9, "!": 0.6, "?": 0.6, ",": 0.5, ":": 0.5, ";": 0.5}.get(p.group(1), 0) if p else 0)
    tot = sum(wt); cum = np.cumsum([0] + wt) / tot * dur
    bounds = []
    for k in range(1, len(wt)):
        pass
    # word k starts at cum[2k], ends at cum[2k+1] (pause weight follows)
    out = []
    for k, x in enumerate(ws):
        a, b = cum[2 * k], cum[2 * k + 1]
        out.append([x, a, b])
    # snap each interior boundary (end of word k / start of word k+1) to the quietest frame within +-70 ms
    for k in range(len(out) - 1):
        mid = (out[k][2] + out[k + 1][1]) / 2
        i0, i1 = max(0, int((mid - 0.07) * 100)), min(n, int((mid + 0.07) * 100) + 1)
        if i1 > i0 + 1:
            m = i0 + int(np.argmin(rms[i0:i1])); m = m / 100.0
            gap = out[k + 1][1] - out[k][2]
            if gap > 0.02:                      # a pause follows the word: keep word edges, they were weighted
                continue
            out[k][2] = m; out[k + 1][1] = m
    return [dict(w=a, s=round(float(b), 3), e=round(float(c), 3)) for a, b, c in out]


def render(cast=None):
    pk = json.load(open(os.path.join(OUT, "voice_pick.json")))
    chosen = {}
    for who, lst in pk.items():
        best = max(lst, key=lambda e: e["score"])
        chosen[who] = next(c for c in CANDS[who] if c[0] == best["label"])
    if cast:
        chosen.update(cast)
    json.dump({k: v[0] for k, v in chosen.items()}, open(os.path.join(OUT, "voice_cast.json"), "w"), indent=1)
    rec = mkrec()
    report = []
    for ep, ls in LINES.items():
        d = os.path.join(OUT, "voices", ep); os.makedirs(d, exist_ok=True)
        for c, who, kind, text, o in ls:
            cand = chosen[who]
            w = trim(raw(cand, o.get("tts", text), o.get("speed", 1.0), o.get("st", 0.0)))
            pk_ = np.abs(w).max() or 1
            w = w / pk_ * 0.8 * 10 ** (o.get("gain", 0.0) / 20 - 0.0)
            w = np.clip(w, -0.98, 0.98)
            w = np.concatenate([w, np.zeros(int(0.03 * SR), np.float32)])
            hyp = asr(rec, w)
            f0, rg, jt = pitch_stats(w)
            words = align(w, text)
            sf.write(os.path.join(d, c + ".wav"), w, SR, subtype="PCM_16")
            json.dump(dict(clip=c, who=who, kind=kind, text=text, voice=cand[0], dur=round(len(w) / SR, 3), words=words, asr=hyp,
                           wer=round(wer(text, hyp), 3), f0=round(f0), range_st=round(rg, 1), jitter=round(jt, 2)),
                      open(os.path.join(d, c + ".json"), "w"), indent=1)
            report.append((ep, c, who, round(len(w) / SR, 2), round(wer(text, hyp), 2), hyp))
            print(ep, c, who, round(len(w) / SR, 2), "wer", round(wer(text, hyp), 2), "|", hyp, flush=True)


if __name__ == "__main__":
    {"pick": pick, "render": render}[sys.argv[1]]()
