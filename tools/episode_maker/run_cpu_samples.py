#!/usr/bin/env python3
"""CPU voice samples for the creator's listening test (Kokoro, Piper voices via sherpa-onnx, KittenTTS, Supertonic, Pocket TTS).

    python3 run_cpu_samples.py survey     # pitch survey of every speaker (cached in survey.json)
    python3 run_cpu_samples.py render     # picks candidates per character, renders <model>__<character>__<n>.wav in out/voice-samples/raw/

Models are downloaded by fetch_voice_models.sh and the sherpa-onnx "tts-models" release (GitHub only) into MODELS (default tts/models).
Only voices whose dataset licence allows commercial use are rendered (see production/v4/voice-samples-report.md).
Nothing here clones a real person: the voices are the published model voices; Pocket TTS refs are synthetic Kokoro clips.
"""
import json, os, sys, time
import numpy as np, soundfile as sf, librosa
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "gpu"))
import voice_samples_lib as L

MODELS = os.environ.get("VS_MODELS", os.path.join(HERE, "tts", "models"))
OUT = os.environ.get("VS_OUT", os.path.join(HERE, "out", "voice-samples"))
RAW = os.path.join(OUT, "raw")
SURVEY = os.path.join(OUT, "survey.json")
PROBE = "Wait, the soup is inside the dumpling? How?"
# voice-selection targets: median pitch after shifting (Hz), allowed shift range (semitones), speed
CHAR_TARGET = {"boy": (270, 0, 5, 1.0), "host": (215, 0, 4, 1.0), "grandma": (175, -2, 2, 0.95),
               "uncle": (100, -3, 0, 1.0), "narrator": (100, -3, 0, 0.9)}
# piper-style models: (model id, onnx name, licence as written in the MODEL_CARD, max picks per character)
PIPER = [
    ("piper-libritts_r", "vits-piper-en_US-libritts_r-medium", "en_US-libritts_r-medium", "CC BY 4.0 (LibriTTS-R, 904 speakers)", 3),
    ("piper-vctk", "vits-piper-en_GB-vctk-medium", "en_GB-vctk-medium", "CC BY 4.0 (VCTK, 109 speakers)", 3),
    ("piper-aru", "vits-piper-en_GB-aru-medium", "en_GB-aru-medium", "CC BY 4.0 (ARU, 12 speakers)", 2),
    ("piper-arctic", "vits-piper-en_US-arctic-medium", "en_US-arctic-medium", "CMU Arctic (permissive, see LICENSE file)", 2),
    ("piper-alba", "vits-piper-en_GB-alba-medium", "en_GB-alba-medium", "CC BY 4.0", 1),
    ("piper-cori", "vits-piper-en_GB-cori-high", "en_GB-cori-high", "public domain (LibriVox)", 1),
    ("piper-joe", "vits-piper-en_US-joe-medium", "en_US-joe-medium", "CC0", 1),
    ("piper-kathleen", "vits-piper-en_US-kathleen-low", "en_US-kathleen-low", "CC0", 1),
    ("piper-kristin", "vits-piper-en_US-kristin-medium", "en_US-kristin-medium", "public domain", 1),
    ("piper-ljspeech", "vits-piper-en_US-ljspeech-high", "en_US-ljspeech-high", "public domain (LJ Speech)", 1),
    ("piper-norman", "vits-piper-en_US-norman-medium", "en_US-norman-medium", "public domain", 1),
    ("piper-bryce", "vits-piper-en_US-bryce-medium", "en_US-bryce-medium", "public domain", 1),
    ("piper-sam", "vits-piper-en_US-sam-medium", "en_US-sam-medium", "Apache-2.0", 1),
]
_c = {}


def f0_of(w, sr):
    w = np.asarray(w, np.float32)
    if len(w) < sr // 4:
        return 0.0
    f = librosa.yin(w, fmin=60, fmax=450, sr=sr, frame_length=2048)
    rms = librosa.feature.rms(y=w, frame_length=2048, hop_length=512)[0][:len(f)]
    ok = rms > 0.3 * np.median(rms[rms > 0]) if (rms > 0).any() else rms > 0
    f = f[:len(ok)][ok[:len(f)]]
    return float(np.median(f)) if len(f) else 0.0


def sherpa(kind, d, **kw):
    import sherpa_onnx as s
    key = (kind, d)
    if key in _c:
        return _c[key]
    mc = s.OfflineTtsModelConfig()
    mc.num_threads = 4
    ed = f"{d}/espeak-ng-data"
    if kind == "vits":
        mc.vits = s.OfflineTtsVitsModelConfig(model=kw["onnx"], tokens=f"{d}/tokens.txt", data_dir=ed)
    elif kind == "kitten":
        mf = f"{d}/model.onnx" if os.path.exists(f"{d}/model.onnx") else (f"{d}/model.int8.onnx" if os.path.exists(f"{d}/model.int8.onnx") else f"{d}/model.fp16.onnx")
        mc.kitten = s.OfflineTtsKittenModelConfig(model=mf, voices=f"{d}/voices.bin", tokens=f"{d}/tokens.txt", data_dir=ed,
                                                  lexicon=os.path.join(MODELS, "kokoro-multi-lang-v1_1", "lexicon-us-en.txt"))
    elif kind == "kokoro11":
        mc.kokoro = s.OfflineTtsKokoroModelConfig(model=f"{d}/model.onnx", voices=f"{d}/voices.bin", tokens=f"{d}/tokens.txt",
                                                  lexicon=f"{d}/lexicon-us-en.txt", data_dir=ed, dict_dir=f"{d}/dict")
    _c[key] = s.OfflineTts(s.OfflineTtsConfig(model=mc))
    return _c[key]


def gen(tts, text, sid, speed):
    if isinstance(tts, Piper):
        return tts.generate(text, sid, speed)
    a = tts.generate(text, sid=int(sid), speed=float(speed))
    return np.asarray(a.samples, np.float32), a.sample_rate


class Piper:
    """Piper voice run directly with onnxruntime (the sherpa-onnx wheel has no espeak frontend): espeak IPA -> phoneme ids -> VITS."""

    def __init__(self, d, onnx):
        import onnxruntime as ort, espeakng_loader
        from phonemizer.backend import EspeakBackend
        from phonemizer.backend.espeak.wrapper import EspeakWrapper
        EspeakWrapper.set_library(espeakng_loader.get_library_path())
        EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
        self.cfg = json.load(open(f"{d}/{onnx}.onnx.json"))
        v = self.cfg["espeak"]["voice"]
        self.ph = EspeakBackend({"en": "en-us"}.get(v, v), preserve_punctuation=True, with_stress=True, language_switch="remove-flags")
        self.sess = ort.InferenceSession(f"{d}/{onnx}.onnx", providers=["CPUExecutionProvider"])
        self.num_speakers = int(self.cfg.get("num_speakers", 1))
        self.sample_rate = self.cfg["audio"]["sample_rate"]
        self.map = self.cfg["phoneme_id_map"]

    def generate(self, text, sid=0, speed=1.0):
        ipa = self.ph.phonemize([text], strip=True)[0]
        ids = list(self.map["^"])
        for ch in ipa:
            if ch in self.map:
                ids += self.map[ch] + self.map["_"]
        ids += self.map["$"]
        inf = self.cfg.get("inference", {})
        feed = {"input": np.array([ids], np.int64), "input_lengths": np.array([len(ids)], np.int64),
                "scales": np.array([inf.get("noise_scale", 0.667), inf.get("length_scale", 1.0) / float(speed), inf.get("noise_w", 0.8)], np.float32)}
        if self.num_speakers > 1:
            feed["sid"] = np.array([int(sid)], np.int64)
        return np.asarray(self.sess.run(None, feed)[0], np.float32).squeeze(), self.sample_rate


def piper_tts(m):
    mid, folder, onnx, lic, k = m
    if mid not in _c:
        _c[mid] = Piper(os.path.join(MODELS, folder), onnx)
    return _c[mid]


def survey():
    os.makedirs(OUT, exist_ok=True)
    res = json.load(open(SURVEY)) if os.path.exists(SURVEY) else {}
    for m in PIPER:
        if m[0] in res or not os.path.isdir(os.path.join(MODELS, m[1])):
            continue
        t = piper_tts(m)
        n = t.num_speakers
        step = 3 if n > 300 else 1
        res[m[0]] = {}
        for sid in range(0, n, step):
            w, sr = gen(t, PROBE, sid, 1.0)
            res[m[0]][str(sid)] = round(f0_of(w, sr), 1)
        print(m[0], n, "speakers surveyed", flush=True)
    for name, folder in (("kitten-mini", "kitten-mini-en-v0_8"), ("kitten-nano", "kitten-nano-en-v0_8-int8")):
        if name in res or not os.path.isdir(os.path.join(MODELS, folder)):
            continue
        t = sherpa("kitten", os.path.join(MODELS, folder))
        res[name] = {str(s): round(f0_of(*gen(t, PROBE, s, 1.0)), 1) for s in range(t.num_speakers)}
        print(name, res[name], flush=True)
    json.dump(res, open(SURVEY, "w"), indent=1)


def shift_for(f0, ch):
    target, lo, hi, _ = CHAR_TARGET[ch]
    st = float(np.clip(12 * np.log2(target / f0), lo, hi))
    err = abs(12 * np.log2(f0 * 2 ** (st / 12) / target))
    return st, err


def pshift(w, sr, st):
    return librosa.effects.pitch_shift(w, sr=sr, n_steps=st) if abs(st) > 0.05 else w


def render_set(name, ch, n, fn, meta, manifest):
    """fn(text) -> (wav, sr); writes the 4 lines of the character into one wav."""
    parts, sr_out, durs = [], None, []
    for lid, text, style, note in L.LINES[ch]:
        w, sr = fn(text)
        if sr != 24000:
            w = librosa.resample(w, orig_sr=sr, target_sr=24000)
        w, _ = librosa.effects.trim(w, top_db=40)
        parts.append(w.astype(np.float32))
        parts.append(np.zeros(int(0.55 * 24000), np.float32))
        durs.append(round(len(w) / 24000, 2))
    wav = np.concatenate(parts[:-1])
    fid = f"{name}__{ch}__{n}"
    sf.write(os.path.join(RAW, fid + ".wav"), wav, 24000, subtype="PCM_16")
    manifest.append(dict(id=fid, model=name, char=ch, n=n, line_seconds=durs, **meta))
    print(fid, meta, flush=True)


def render():
    os.makedirs(RAW, exist_ok=True)
    mp = os.path.join(OUT, "manifest-cpu.json")
    manifest = []
    survey_d = json.load(open(SURVEY))
    t0 = time.time()
    # --- Kokoro v1.0 (kokoro-onnx): hand-picked voices
    from kokoro_onnx import Kokoro
    tts_dir = os.path.join(HERE, "tts")
    k = Kokoro(os.path.join(tts_dir, "kokoro-v1.0.onnx"), os.path.join(tts_dir, "voices-v1.0.bin"))
    KOK = {"boy": [("am_puck", 1.12), ("am_liam", 1.2), ("af_heart", 1.2), ("af_sky", 1.2), ("bf_lily", 1.1), ("am_echo", 1.2)],
           "host": [("am_puck", 1.05), ("am_echo", 1.1), ("af_heart", 1.1), ("am_liam", 1.08), ("bf_lily", 1.05), ("am_eric", 1.1)],
           "grandma": [("af_sarah", 0.96), ("bf_emma", 0.9), ("bf_isabella", 0.92), ("af_nicole", 0.9), ("bf_alice", 0.9), ("af_kore", 0.92)],
           "uncle": [("am_michael", 0.9), ("am_onyx", 0.92), ("am_fenrir", 0.9), ("am_adam", 0.9), ("bm_lewis", 0.9), ("bm_daniel", 0.9)],
           "narrator": [("bm_george", 0.9), ("bm_fable", 0.88), ("bm_lewis", 0.85), ("am_adam", 0.8), ("bm_daniel", 0.88), ("am_onyx", 0.85)]}
    for ch, vs in KOK.items():
        sp = CHAR_TARGET[ch][3]
        for i, (v, p) in enumerate(vs, 1):
            def fn(text, v=v, p=p, sp=sp):
                w, sr = k.create(text, voice=v, speed=sp, lang="en-us")
                return pshift(np.asarray(w, np.float32), sr, 12 * np.log2(p)), sr
            render_set("kokoro", ch, i, fn, dict(voice=v, pitch_ratio=p, speed=sp, license="Apache-2.0"), manifest)
    # --- Piper-style voices (sherpa-onnx), picked by pitch fit
    for m in PIPER:
        if m[0] not in survey_d:
            continue
        t = piper_tts(m)
        for ch in L.CHARS:
            sp = CHAR_TARGET[ch][3]
            cands = sorted(((shift_for(f0, ch)[1], int(sid), f0) for sid, f0 in survey_d[m[0]].items() if f0 > 0))
            used_other = {(x["model"], x["voice"]) for x in manifest if x["char"] in ("uncle", "narrator") and ch in ("uncle", "narrator") and x["char"] != ch}
            picks = [c for c in cands if (m[0], c[1]) not in used_other]
            n = 0
            for err, sid, f0 in picks:
                if n >= m[4] or err > 5:
                    break
                n += 1
                st, _ = shift_for(f0, ch)

                def fn(text, sid=sid, st=st, sp=sp):
                    w, sr = gen(t, text, sid, sp)
                    return pshift(w, sr, st), sr
                render_set(m[0], ch, n, fn, dict(voice=sid, f0=f0, shift_semitones=round(st, 1), speed=sp, license=m[3]), manifest)
    # --- KittenTTS (Apache-2.0)
    for name, folder in (("kitten-mini", "kitten-mini-en-v0_8"), ("kitten-nano", "kitten-nano-en-v0_8-int8")):
        if name not in survey_d:
            continue
        t = sherpa("kitten", os.path.join(MODELS, folder))
        for ch in L.CHARS:
            sp = CHAR_TARGET[ch][3]
            cands = sorted(((shift_for(f0, ch)[1], int(sid), f0) for sid, f0 in survey_d[name].items() if f0 > 0))
            for n, (err, sid, f0) in enumerate(cands[:2], 1):
                st, _ = shift_for(f0, ch)

                def fn(text, sid=sid, st=st, sp=sp):
                    w, sr = gen(t, text, sid, sp)
                    return pshift(w, sr, st), sr
                render_set(name, ch, n, fn, dict(voice=sid, f0=f0, shift_semitones=round(st, 1), speed=sp, license="Apache-2.0"), manifest)
    # --- Supertonic-2 (OpenRAIL-M) and Pocket TTS (CC-BY-4.0), via the existing engine wrapper
    sys.path.insert(0, HERE)
    import tts_engines as te
    ST = {"boy": [(5, 1.12), (6, 1.12), (3, 1.06)], "host": [(5, 1.05), (7, 1.05), (2, 1.0)], "grandma": [(4, 1.0), (3, 0.97), (2, 0.95)],
          "uncle": [(8, 0.94), (9, 0.94), (6, 0.9)], "narrator": [(9, 0.9), (8, 0.9), (6, 0.88)]}
    for ch, vs in ST.items():
        sp = CHAR_TARGET[ch][3]
        for i, (sid, p) in enumerate(vs, 1):
            def fn(text, sid=sid, p=p, sp=sp):
                w, sr = te.synth({"engine": "supertonic", "sid": sid, "speed": sp}, text)
                return pshift(w, sr, 12 * np.log2(p)), sr
            render_set("supertonic", ch, i, fn, dict(voice=sid, pitch_ratio=p, speed=sp, license="OpenRAIL-M"), manifest)
    for ch in L.CHARS:
        sp = CHAR_TARGET[ch][3]
        for i, (kv, p) in enumerate(L.CB_REFS[ch], 1):
            ref = os.path.join(OUT, f"pocketref_{ch}_{i}.wav")
            w, sr = k.create(te.REF_TEXT, voice=kv, speed=1.0, lang="en-us")
            w = pshift(np.asarray(w, np.float32), sr, 12 * np.log2(p))
            sf.write(ref, w, sr)

            def fn(text, ref=ref, sp=sp):
                return te.synth({"engine": "pocket", "ref": ref, "speed": sp}, text)
            render_set("pocket", ch, i, fn, dict(voice=f"ref:{kv}@{p}", speed=sp, license="CC-BY-4.0 (credit Kyutai Pocket TTS)"), manifest)
    json.dump(manifest, open(mp, "w"), indent=1)
    print(len(manifest), "samples in", round(time.time() - t0), "s")


if __name__ == "__main__":
    {"survey": survey, "render": render}[sys.argv[1]]()
