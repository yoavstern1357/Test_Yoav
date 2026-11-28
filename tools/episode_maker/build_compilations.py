#!/usr/bin/env python3
"""Voice-sample post-processing: GPU results -> per-voice files, ear-proxy metrics, loudness-normalised mp3, compilations, index.

    python3 build_compilations.py import-gpu <dir with qwen3/ chatterbox/ orpheus/ audio folders>   # line wavs -> raw/<model>__<char>__<n>.wav
    python3 build_compilations.py metrics        # pitch, speaking rate, ASR word error rate (Whisper small.en via sherpa-onnx), clipping
    python3 build_compilations.py build          # mp3 per voice, compare-<character>.m4a (spoken label + sample), INDEX.md / index.tsv

Everything stays in tools/episode_maker/out/voice-samples (git-ignored). Nothing here judges by ear: the metrics are proxies only.
"""
import glob, json, os, re, subprocess, sys
import numpy as np, soundfile as sf, librosa
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "gpu"))
import voice_samples_lib as L

OUT = os.environ.get("VS_OUT", os.path.join(HERE, "out", "voice-samples"))
RAW = os.path.join(OUT, "raw")
MODELS = os.environ.get("VS_MODELS", os.path.join(HERE, "tts", "models"))
SR = 24000
MODEL_ORDER = ["qwen3", "chatterbox", "orpheus", "kokoro", "supertonic", "pocket", "kitten-mini", "kitten-nano"]
SAY = {"qwen3": "Qwen three", "chatterbox": "Chatterbox", "orpheus": "Orpheus", "kokoro": "Kokoro", "supertonic": "Supertonic", "pocket": "Pocket T T S",
       "kitten-mini": "Kitten mini", "kitten-nano": "Kitten nano", "piper-libritts_r": "Piper Libri T T S R", "piper-vctk": "Piper V C T K",
       "piper-aru": "Piper Aru", "piper-arctic": "Piper Arctic", "piper-alba": "Piper Alba", "piper-cori": "Piper Cori", "piper-joe": "Piper Joe",
       "piper-kathleen": "Piper Kathleen", "piper-kristin": "Piper Kristin", "piper-ljspeech": "Piper L J Speech", "piper-norman": "Piper Norman",
       "piper-bryce": "Piper Bryce", "piper-sam": "Piper Sam"}
GPU_LICENSE = {"qwen3": "Apache-2.0", "chatterbox": "MIT", "orpheus": "Apache-2.0 declared (Llama 3.2 base: terms may apply)"}
NUM = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
       "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]


def spell(n):
    if n < 20:
        return NUM[n]
    t = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"][n // 10]
    return t + ("" if n % 10 == 0 else " " + NUM[n % 10])


def model_key(m):
    return (MODEL_ORDER.index(m) if m in MODEL_ORDER else 100, m)


def import_gpu(src):
    os.makedirs(RAW, exist_ok=True)
    manifest = []
    for be in ("qwen3", "chatterbox", "orpheus"):
        rp = os.path.join(src, be, "results.json")
        if not os.path.exists(rp):
            print("no results for", be)
            continue
        res = {r["id"]: r for r in json.load(open(rp))["results"]}
        groups = {}
        for rid, r in res.items():
            if r["status"] != "ok":
                continue
            m = re.match(r"^(.+)__(\w+)__(\d+)__(l\d)$", rid)
            groups.setdefault((m.group(1), m.group(2), int(m.group(3))), {})[m.group(4)] = (rid, r)
        for (model, ch, n), ls in sorted(groups.items()):
            if set(ls) != {"l1", "l2", "l3", "l4"}:
                print("incomplete set (skipped)", model, ch, n, sorted(ls))
                continue
            parts, durs, secs = [], [], 0.0
            for lid in ("l1", "l2", "l3", "l4"):
                rid, r = ls[lid]
                w, sr = sf.read(os.path.join(src, be, "audio", rid + ".wav"), dtype="float32")
                w = w.mean(axis=1) if w.ndim > 1 else w
                if sr != SR:
                    w = librosa.resample(w, orig_sr=sr, target_sr=SR)
                w, _ = librosa.effects.trim(w, top_db=40)
                parts += [w, np.zeros(int(0.55 * SR), np.float32)]
                durs.append(round(len(w) / SR, 2))
                secs += r.get("seconds", 0)
            fid = f"{model}__{ch}__{n}"
            sf.write(os.path.join(RAW, fid + ".wav"), np.concatenate(parts[:-1]), SR, subtype="PCM_16")
            key = f"{model}__{ch}__{n}__l1"
            voice = ""
            tj = json.load(open(os.path.join(src, "tts.json")))
            v = tj["voices"].get(f"{model}__{ch}__{n}", {})
            voice = v.get("qwen_voice") or v.get("orpheus_voice") or v.get("ref", "")
            manifest.append(dict(id=fid, model=model, char=ch, n=n, line_seconds=durs, voice=voice, gen_seconds=round(secs, 1), license=GPU_LICENSE[model]))
    json.dump(manifest, open(os.path.join(OUT, "manifest-gpu.json"), "w"), indent=1)
    print(len(manifest), "GPU voice sets imported")


def norm(t):
    return re.sub(r"[^a-z0-9 ]", "", t.lower().replace("-", " ")).split()


def wer(ref, hyp):
    r, h = norm(ref), norm(hyp)
    d = np.arange(len(h) + 1)
    for i in range(1, len(r) + 1):
        p, d = d, np.zeros(len(h) + 1, int)
        d[0] = i
        for j in range(1, len(h) + 1):
            d[j] = min(p[j] + 1, d[j - 1] + 1, p[j - 1] + (r[i - 1] != h[j - 1]))
    return d[-1] / max(1, len(r))


def load_manifest():
    man = []
    for f in ("manifest-cpu.json", "manifest-gpu.json"):
        p = os.path.join(OUT, f)
        if os.path.exists(p):
            man += json.load(open(p))
    return man


def metrics():
    import sherpa_onnx as s
    d = os.path.join(MODELS, "sherpa-onnx-whisper-small.en")
    rec = s.OfflineRecognizer.from_whisper(encoder=f"{d}/small.en-encoder.int8.onnx", decoder=f"{d}/small.en-decoder.int8.onnx",
                                           tokens=f"{d}/small.en-tokens.txt", language="en", task="transcribe", num_threads=4)
    man = load_manifest()
    mp = os.path.join(OUT, "manifest-all.json")
    done = {m["id"]: m for m in json.load(open(mp))} if os.path.exists(mp) else {}
    for i, m in enumerate(man):
        if m["id"] in done and "wer" in done[m["id"]]:
            man[i] = done[m["id"]]
            continue
        w, sr = sf.read(os.path.join(RAW, m["id"] + ".wav"), dtype="float32")
        ref = " ".join(t for _, t, _, _ in L.LINES[m["char"]])
        per_line = []
        # ASR per line: split the set at the 0.55 s gaps by the known line durations
        pos, hyps = 0.0, []
        for dur in m["line_seconds"]:
            seg = w[int(pos * sr): int((pos + dur) * sr)]
            st = rec.create_stream()
            st.accept_waveform(sr, seg)
            rec.decode_stream(st)
            hyps.append(st.result.text.strip())
            pos += dur + 0.55
        texts = [t for _, t, _, _ in L.LINES[m["char"]]]
        per_line = [round(wer(t, h), 2) for t, h in zip(texts, hyps)]
        words = sum(len(norm(t)) for t in texts)
        f0 = librosa.yin(w, fmin=60, fmax=500, sr=sr, frame_length=2048)
        rms = librosa.feature.rms(y=w, frame_length=2048, hop_length=512)[0][:len(f0)]
        v = f0[: len(rms)][rms > 0.3 * np.median(rms[rms > 0])]
        cent = float(np.mean(librosa.feature.spectral_centroid(y=w, sr=sr)))
        m.update(speech_seconds=round(sum(m["line_seconds"]), 1), words_per_sec=round(words / sum(m["line_seconds"]), 2),
                 f0_median=round(float(np.median(v)), 0), f0_range_st=round(float(12 * np.log2(np.percentile(v, 90) / np.percentile(v, 10))), 1),
                 wer=round(float(np.mean(per_line)), 2), wer_lines=per_line, asr=hyps, peak=round(float(np.abs(w).max()), 2),
                 centroid_hz=round(cent), line_seconds_sum=round(sum(m["line_seconds"]), 1))
        print(m["id"], "wer", m["wer"], "f0", m["f0_median"], "range", m["f0_range_st"], "wps", m["words_per_sec"], flush=True)
    json.dump(man, open(os.path.join(OUT, "manifest-all.json"), "w"), indent=1)


def lufs_norm(w, sr, target=-18.0):
    import pyloudnorm as pyln
    if len(w) < int(0.45 * sr):
        w = np.pad(w, (0, int(0.45 * sr) - len(w)))
    meter = pyln.Meter(sr)
    l = meter.integrated_loudness(w)
    w = w * 10 ** ((target - l) / 20) if np.isfinite(l) else w
    pk = np.abs(w).max()
    return (w * (0.89 / pk) if pk > 0.89 else w).astype(np.float32)


def enc(wav_path, out_path, codec, br):
    args = ["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path, "-ac", "1"]
    args += (["-c:a", "libmp3lame", "-b:a", br] if codec == "mp3" else ["-c:a", "aac", "-b:a", br, "-movflags", "+faststart"]) + [out_path]
    subprocess.run(args, check=True)


def label_wav(text, cache={}):
    from kokoro_onnx import Kokoro
    if "k" not in cache:
        t = os.path.join(HERE, "tts")
        cache["k"] = Kokoro(os.path.join(t, "kokoro-v1.0.onnx"), os.path.join(t, "voices-v1.0.bin"))
    w, sr = cache["k"].create(text, voice="af_heart", speed=0.95, lang="en-us")
    return lufs_norm(librosa.resample(np.asarray(w, np.float32), orig_sr=sr, target_sr=SR), SR, -20.0)


def build():
    man = load_manifest()
    mp = os.path.join(OUT, "manifest-all.json")
    if os.path.exists(mp):
        met = {m["id"]: m for m in json.load(open(mp))}
        man = [met.get(m["id"], m) for m in man]
    os.makedirs(os.path.join(OUT, "samples"), exist_ok=True)
    rows = []
    for ch in L.CHARS:
        items = sorted([m for m in man if m["char"] == ch], key=lambda m: (model_key(m["model"]), m["n"]))
        parts, parts_len, part_of = [], 0.0, {}
        files = []
        for i, m in enumerate(items, 1):
            w, sr = sf.read(os.path.join(RAW, m["id"] + ".wav"), dtype="float32")
            w = lufs_norm(w, sr)
            smp = os.path.join(OUT, "samples", m["id"] + ".wav")
            sf.write(smp, w, SR, subtype="PCM_16")
            enc(smp, os.path.join(OUT, "samples", m["id"] + ".mp3"), "mp3", "96k")
            os.remove(smp)
            lab = label_wav(f"Number {spell(i)}. {SAY.get(m['model'], m['model'])}, voice {spell(m['n'])}.")
            seg = np.concatenate([lab, np.zeros(int(0.45 * SR), np.float32), w, np.zeros(int(1.3 * SR), np.float32)])
            if parts_len + len(seg) / SR > 17 * 60:           # keep every compilation file well under 15 MB
                files.append(parts)
                parts, parts_len = [], 0.0
            part_of[i] = len(files) + 1
            parts.append(seg)
            parts_len += len(seg) / SR
            rows.append(dict(character=ch, seq=i, model=m["model"], n=m["n"], file=f"samples/{m['id']}.mp3", id=m["id"],
                             voice=m.get("voice", ""), license=m.get("license", ""), wer=m.get("wer"), f0=m.get("f0_median"), range_st=m.get("f0_range_st"),
                             wps=m.get("words_per_sec")))
        files.append(parts)
        for k, pp in enumerate(files, 1):
            name = f"compare-{ch}" + (f"-part{k}" if len(files) > 1 else "")
            wp = os.path.join(OUT, name + ".wav")
            sf.write(wp, np.concatenate(pp), SR, subtype="PCM_16")
            enc(wp, os.path.join(OUT, name + ".m4a"), "m4a", "64k")
            os.remove(wp)
            print(name, round(os.path.getsize(os.path.join(OUT, name + ".m4a")) / 1e6, 1), "MB,", len(pp), "voices", flush=True)
        for r in rows:
            if r["character"] == ch:
                r["compilation"] = f"compare-{ch}" + (f"-part{part_of[r['seq']]}" if len(files) > 1 else "") + ".m4a"
    write_index(rows)


def write_index(rows):
    json.dump(rows, open(os.path.join(OUT, "index.json"), "w"), indent=1)
    with open(os.path.join(OUT, "index.tsv"), "w") as f:
        f.write("character\tnumber\tmodel\tvoice_no\tfile\tvoice\tlicense\tASR_word_error\tpitch_hz\tpitch_range_st\twords_per_s\n")
        for r in rows:
            f.write("\t".join(str(r.get(k, "")) for k in ("character", "seq", "model", "n", "file", "voice", "license", "wer", "f0", "range_st", "wps")) + "\n")
    md = ["# Voice samples index", "", "Each character has one compilation file `compare-<character>.m4a`: a spoken label (number, model, voice) and then the sample. Answer with the character and the NUMBER.", ""]
    for ch in L.CHARS:
        md += [f"## {L.CHAR_NAMES[ch]}  (compare-{ch}.m4a)", "", "| No. | Model | Voice | File | ASR error | Pitch Hz |", "|---|---|---|---|---|---|"]
        for r in [r for r in rows if r["character"] == ch]:
            md.append(f"| {r['seq']} | {r['model']} | {r['n']} | {r['id']}.mp3 ({r['compilation']}) | {r['wer']} | {r['f0']} |")
        md.append("")
    open(os.path.join(OUT, "INDEX.md"), "w").write("\n".join(md))


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"import-gpu": lambda: import_gpu(sys.argv[2]), "metrics": metrics, "build": build}[cmd]()
