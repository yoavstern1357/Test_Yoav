"""Optional voice engines for make_episode.py (Kokoro stays the built-in default there).

Every engine returns (float32 mono samples, sample_rate). Nothing here clones a real person: Supertonic uses its
10 built-in synthetic voices, Pocket TTS is conditioned on a reference clip that WE synthesize with Kokoro (never a
recording of a real person), and "prerendered" reads WAV files made by the Kaggle GPU job (gpu/generate_tts.py).

  supertonic   Supertonic-2 int8 ONNX via sherpa-onnx (CPU, about 6 to 20x faster than real time). Weights OpenRAIL-M.
  pocket       Kyutai Pocket TTS int8 ONNX via sherpa-onnx (CPU, about real time). Weights CC-BY-4.0 (credit it).
  prerendered  <dir>/<line_key>.wav from the GPU job (Chatterbox / Orpheus). line_key() below is the shared file name.

Models: run tools/episode_maker/fetch_voice_models.sh (GitHub releases only), then `pip install sherpa-onnx`.
"""
import hashlib, os
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
TTS_DIR = os.environ.get("TTS_DIR", os.path.join(HERE, "tts"))

REF_TEXT = ("Welcome, friends. Today we are going to taste something wonderful, so please sit down, "
            "take a deep breath, and listen to the story.")


def line_key(who, text):
    """File stem shared by make_episode.py and gpu/generate_tts.py for one spoken line."""
    return hashlib.md5(f"{who}|{text}".encode()).hexdigest()[:16]


_cache = {}


def _supertonic():
    if "st" not in _cache:
        import sherpa_onnx as s
        d = os.path.join(TTS_DIR, "supertonic")
        m = s.OfflineTtsSupertonicModelConfig(
            duration_predictor=f"{d}/duration_predictor.int8.onnx", text_encoder=f"{d}/text_encoder.int8.onnx",
            vector_estimator=f"{d}/vector_estimator.int8.onnx", vocoder=f"{d}/vocoder.int8.onnx",
            tts_json=f"{d}/tts.json", unicode_indexer=f"{d}/unicode_indexer.bin", voice_style=f"{d}/voice.bin")
        mc = s.OfflineTtsModelConfig()
        mc.supertonic = m
        mc.num_threads = int(os.environ.get("TTS_THREADS", "4"))
        _cache["st"] = s.OfflineTts(s.OfflineTtsConfig(model=mc))
    return _cache["st"]


def _pocket():
    if "pk" not in _cache:
        import sherpa_onnx as s
        d = os.path.join(TTS_DIR, "pocket")
        m = s.OfflineTtsPocketModelConfig(
            lm_flow=f"{d}/lm_flow.int8.onnx", lm_main=f"{d}/lm_main.int8.onnx", encoder=f"{d}/encoder.onnx",
            decoder=f"{d}/decoder.int8.onnx", text_conditioner=f"{d}/text_conditioner.onnx",
            vocab_json=f"{d}/vocab.json", token_scores_json=f"{d}/token_scores.json")
        mc = s.OfflineTtsModelConfig()
        mc.pocket = m
        mc.num_threads = int(os.environ.get("TTS_THREADS", "4"))
        _cache["pk"] = s.OfflineTts(s.OfflineTtsConfig(model=mc))
    return _cache["pk"]


def kokoro_ref(voice, speed=1.0):
    """Synthetic reference clip for Pocket TTS: a Kokoro voice reading REF_TEXT (cached next to the models)."""
    path = os.path.join(TTS_DIR, "refs", f"kokoro_{voice}_{speed:.2f}.wav")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        from kokoro_onnx import Kokoro
        k = Kokoro(os.path.join(TTS_DIR, "kokoro-v1.0.onnx"), os.path.join(TTS_DIR, "voices-v1.0.bin"))
        wav, sr = k.create(REF_TEXT, voice=voice, speed=speed, lang="en-us")
        sf.write(path, wav, sr)
    return path


def synth(cfg, text, speed=1.0):
    """cfg: {"engine": "supertonic", "sid": 5, "steps": 5} | {"engine": "pocket", "ref": "x.wav" | "ref_voice": "am_puck"}."""
    eng = cfg["engine"]
    if eng == "supertonic":
        import sherpa_onnx as s
        g = s.GenerationConfig()
        g.sid = int(cfg.get("sid", 5))
        g.speed = float(cfg.get("speed", 1.0)) * float(speed)
        g.num_steps = int(cfg.get("steps", 5))
        g.extra = {"lang": "en"}
        a = _supertonic().generate(text, g)
        return np.asarray(a.samples, np.float32), a.sample_rate
    if eng == "pocket":
        import sherpa_onnx as s
        ref = cfg.get("ref") or kokoro_ref(cfg.get("ref_voice", "am_puck"), float(cfg.get("ref_speed", 1.0)))
        if not os.path.isabs(ref):
            ref = os.path.join(TTS_DIR, ref)
        r, rsr = sf.read(ref, dtype="float32")
        if r.ndim > 1:
            r = r.mean(axis=1)
        g = s.GenerationConfig()
        g.reference_audio = r.tolist()
        g.reference_sample_rate = int(rsr)
        g.speed = float(cfg.get("speed", 1.0)) * float(speed)
        g.num_steps = int(cfg.get("steps", 5))
        g.extra = {}
        a = _pocket().generate(text, g)
        return np.asarray(a.samples, np.float32), a.sample_rate
    raise ValueError(f"unknown engine {eng!r}")


def prerendered(cfg, who, text):
    """WAV made by the GPU job for this exact line (same who + text). Raises FileNotFoundError when it is missing."""
    d = os.path.expanduser(cfg.get("dir", os.path.join(TTS_DIR, "gpu")))
    path = os.path.join(d if os.path.isabs(d) else os.path.join(HERE, d), line_key(who, text) + ".wav")
    if not os.path.exists(path):
        raise FileNotFoundError(f"no pre-rendered voice for {who}: {text!r} (expected {path}); run the GPU tts task or set a fallback engine")
    w, sr = sf.read(path, dtype="float32")
    return (w.mean(axis=1) if w.ndim > 1 else w), sr
