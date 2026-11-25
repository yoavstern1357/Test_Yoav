#!/usr/bin/env python3
"""Batch text-to-speech on a free GPU (Kaggle T4): tts.json (+ synthetic reference clips) -> one WAV per spoken line.

    python3 generate_tts.py --input /path/to/input --out /path/to/output            # all lines, resume
    python3 generate_tts.py --input ... --out ... --dry-run                         # validate + plan, no GPU needed
    python3 generate_tts.py --input ... --out ... --backend orpheus --only 01,02    # other engine / some lines
    python3 generate_tts.py --backend chatterbox --print-requirements               # pip line for the notebook

Why: the CPU voice (Kokoro, 82M) is clean but flat. These open-weight models are clearly more expressive and run in
a few minutes per episode on the free GPU. The WAVs are read by make_episode.py (voice_casts.json preset "gpu").
  chatterbox  Chatterbox 0.5B (ResembleAI/chatterbox, MIT, safetensors). Voice = a reference clip that WE synthesize (never a
              real person); per-line emotion with `exaggeration` and `cfg_weight`.
  turbo       Chatterbox-Turbo 350M (ResembleAI/chatterbox-turbo, MIT): faster, inline tags [laugh] [chuckle] [sigh] ...
  orpheus     Orpheus 3B (canopylabs/orpheus-3b-0.1-ft + SNAC 24 kHz): 8 built-in voices (no reference at all), inline tags
              <laugh> <sigh> <gasp> ... Check the license text on the model card first (see production/v4/voice-tech.md).
  mock        no GPU: a short tone per line (tests the batch / resume / zip logic).
Security: only the official repos below; safetensors weights; torch.load is forced to weights_only=True (so a pickle
file in a repo cannot run code); no trust_remote_code; no token. The resolved model commit is written to results.json.

`tts.json`:
  {"defaults": {"backend": "chatterbox", "seed": 7, "variants": 1},
   "voices": {"boy": {"ref": "refs/boy.wav", "exaggeration_scale": 1.0, "orpheus_voice": "leo"}, ...},
   "styles": {"tender": {"exaggeration": 0.35, "cfg_weight": 0.3}},          (optional, adds to / overrides STYLES below)
   "lines": [{"id": "<line key>", "who": "boy", "text": "...", "style": "host", "text_gpu": "optional text with tags"}]}
"""
import argparse, json, os, re, shutil, sys, time, traceback, wave, zipfile
import numpy as np

BACKENDS = {
    "chatterbox": dict(repo="ResembleAI/chatterbox", pip="chatterbox-tts", sr=24000, license="MIT", needs_ref=True),
    "turbo": dict(repo="ResembleAI/chatterbox-turbo", pip="chatterbox-tts", sr=24000, license="MIT", needs_ref=True),
    "orpheus": dict(repo="canopylabs/orpheus-3b-0.1-ft", pip="transformers accelerate snac soundfile", sr=24000,
                    license="see model card (Apache-2.0 declared, Llama 3.2 base)", needs_ref=False),
    "qwen3": dict(repo="Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", pip="qwen-tts", sr=24000, license="Apache-2.0", needs_ref=False),
    "qwen3custom": dict(repo="Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", pip="qwen-tts", sr=24000, license="Apache-2.0", needs_ref=False),
    "mock": dict(repo="-", pip="", sr=24000, license="-", needs_ref=False),
}
# Orpheus: the official repo may be gated (needs a token); then the widely used ungated mirror of the same weights is tried.
ORPHEUS_REPOS = ["canopylabs/orpheus-3b-0.1-ft", "unsloth/orpheus-3b-0.1-ft"]
# Qwen3-TTS: the VoiceDesign model builds a voice from a text description (`qwen_voice` of each voice + a style sentence).
# Emotion presets (Chatterbox: exaggeration 0.25-1.0, cfg_weight 0.2-0.7; lower cfg = slower, more deliberate). Orpheus uses `tag`.
STYLES = {
    "neutral": dict(exaggeration=0.5, cfg_weight=0.5, qwen="Natural, relaxed and conversational."),
    "host": dict(exaggeration=0.55, cfg_weight=0.5, qwen="Warm, friendly and curious, like a cheerful host welcoming the audience, with a smile in the voice."),
    "excited": dict(exaggeration=0.8, cfg_weight=0.35, tag="<gasp> ", qwen="Excited and delighted, fast and lively, with big expressive ups and downs in pitch."),
    "tender": dict(exaggeration=0.4, cfg_weight=0.3, qwen="Soft, gentle and patient, tender and wise, slightly slower."),
    "dreamy": dict(exaggeration=0.6, cfg_weight=0.3, qwen="Dreamy and wondering, slow, savouring each word, as if smelling something wonderful."),
    "tiny": dict(exaggeration=0.35, cfg_weight=0.3, qwen="Small, quiet and amazed, a hushed whisper of surprise, with a short pause at the start."),
    "solemn": dict(exaggeration=0.45, cfg_weight=0.25, qwen="Slow, solemn and mysterious, a storyteller telling an ancient legend, measured pace."),
    "laugh": dict(exaggeration=0.75, cfg_weight=0.4, tag="<laugh> ", qwen="Laughing, joyful and playful."),
}
ORPHEUS_VOICES = ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"]
ID = re.compile(r"^[A-Za-z0-9_.\-]+$")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def secure_torch_load():
    """Force weights_only=True: a malicious pickle in a downloaded file then cannot execute code."""
    import torch
    orig = torch.load

    def safe(*a, **k):
        k["weights_only"] = True
        return orig(*a, **k)
    torch.load = safe


def load_job(input_dir, args):
    data = json.load(open(os.path.join(input_dir, "tts.json"), encoding="utf-8"))
    d = dict(backend="chatterbox", seed=7, variants=1)
    d.update(data.get("defaults", {}))
    if args.backend:
        d["backend"] = args.backend
    if d["backend"] not in BACKENDS:
        raise ValueError(f"backend must be one of {sorted(BACKENDS)}")
    styles = dict(STYLES)
    styles.update(data.get("styles", {}))
    voices, lines, seen = data["voices"], [], set()
    only = set(x for x in (args.only or "").split(",") if x)
    for i, ln in enumerate(data["lines"]):
        lid = str(ln["id"])
        if not ID.match(lid) or lid in seen:
            raise ValueError(f"line #{i + 1}: bad or duplicate id {lid!r}")
        seen.add(lid)
        if ln["who"] not in voices:
            raise ValueError(f"line {lid}: no voice {ln['who']!r} in tts.json")
        if not str(ln.get("text", "")).strip():
            raise ValueError(f"line {lid}: empty text")
        v = voices[ln["who"]]
        if BACKENDS[d["backend"]]["needs_ref"]:
            ref = os.path.join(input_dir, v.get("ref", ""))
            if not os.path.isfile(ref):
                raise ValueError(f"voice {ln['who']}: reference clip {v.get('ref')!r} not found")
        if d["backend"] == "orpheus" and v.get("orpheus_voice", "tara") not in ORPHEUS_VOICES:
            raise ValueError(f"voice {ln['who']}: orpheus_voice must be one of {ORPHEUS_VOICES}")
        if only and lid not in only:
            continue
        lines.append(dict(ln, id=lid))
    return d, voices, styles, lines


def settings(line, voices, styles):
    """Emotion settings of one line: the style preset, scaled by the voice's `exaggeration_scale`, then per-line overrides."""
    s = dict(styles.get(line.get("style", "neutral"), styles["neutral"]))
    v = voices[line["who"]]
    s["exaggeration"] = min(1.0, s["exaggeration"] * float(v.get("exaggeration_scale", 1.0)))
    for k in ("temperature", "orpheus_voice", "qwen_voice", "qwen_speaker"):
        if k in v:
            s[k] = v[k]
    for k in ("exaggeration", "cfg_weight", "temperature"):
        if k in line:
            s[k] = line[k]
    return s


def write_wav(path, wav, sr):
    pcm = (np.clip(np.asarray(wav, np.float32), -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def model_sha(repo):
    try:
        from huggingface_hub import HfApi
        return HfApi().model_info(repo).sha
    except Exception as ex:           # noqa: BLE001
        return f"unknown ({ex.__class__.__name__})"


# ------------------------------------------------------------------ backends
class Mock:
    def __init__(self, a): self.sr = 24000
    def say(self, line, st, ref, seed):
        n = int(self.sr * (0.25 + 0.06 * len(line["text"].split())))
        t = np.arange(n) / self.sr
        return 0.2 * np.sin(2 * np.pi * (180 + 12 * (len(line["who"]) % 5)) * t) * np.hanning(n)


class Chatterbox:
    def __init__(self, a):
        import torch
        secure_torch_load()
        if a.backend == "turbo":
            from chatterbox.tts_turbo import ChatterboxTurboTTS as M
        else:
            from chatterbox.tts import ChatterboxTTS as M
        self.torch, self.turbo = torch, a.backend == "turbo"
        self.m = M.from_pretrained(device="cuda")
        self.sr = self.m.sr

    def say(self, line, st, ref, seed):
        self.torch.manual_seed(seed)
        text = line.get("text_gpu") or line["text"]
        kw = {} if self.turbo else dict(exaggeration=st["exaggeration"], cfg_weight=st["cfg_weight"])
        if "temperature" in st and not self.turbo:
            kw["temperature"] = st["temperature"]
        wav = self.m.generate(text, audio_prompt_path=ref, **kw)
        return wav.squeeze().float().cpu().numpy()


class Orpheus:
    START, END1, END2, SOS, EOS, OFFSET = 128259, 128009, 128260, 128257, 128258, 128266

    def __init__(self, a):
        import torch
        secure_torch_load()
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from snac import SNAC
        repo = BACKENDS["orpheus"]["repo"]
        self.torch, self.sr = torch, 24000
        self.tok = AutoTokenizer.from_pretrained(repo, revision=a.revision)
        self.m = AutoModelForCausalLM.from_pretrained(repo, torch_dtype=torch.float16, use_safetensors=True, revision=a.revision).cuda().eval()
        self.snac = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").eval().cuda()

    def say(self, line, st, ref, seed):
        t = self.torch
        t.manual_seed(seed)
        voice = st.get("orpheus_voice", "tara")
        text = line.get("text_gpu") or (st.get("tag", "") + line["text"])
        ids = self.tok(f"{voice}: {text}", return_tensors="pt").input_ids
        inp = t.cat([t.tensor([[self.START]]), ids, t.tensor([[self.END1, self.END2]])], 1).cuda()
        with t.no_grad():
            out = self.m.generate(input_ids=inp, attention_mask=t.ones_like(inp), max_new_tokens=1400, do_sample=True,
                                  temperature=st.get("temperature", 0.6), top_p=0.95, repetition_penalty=1.1, eos_token_id=self.EOS)
        pos = (out == self.SOS).nonzero(as_tuple=True)[1]
        row = out[0, pos[-1].item() + 1:] if len(pos) else out[0]
        row = row[row != self.EOS]
        row = row[: (row.numel() // 7) * 7] - self.OFFSET
        c = row.view(-1, 7).tolist()
        l1 = [r[0] for r in c]
        l2 = [x for r in c for x in (r[1] - 4096, r[4] - 4 * 4096)]
        l3 = [x for r in c for x in (r[2] - 2 * 4096, r[3] - 3 * 4096, r[5] - 5 * 4096, r[6] - 6 * 4096)]
        codes = [t.tensor(l, dtype=t.long).unsqueeze(0).cuda() for l in (l1, l2, l3)]
        with t.no_grad():
            audio = self.snac.decode(codes)
        return audio.squeeze().float().cpu().numpy()


def make_backend(a):
    return {"mock": Mock, "chatterbox": Chatterbox, "turbo": Chatterbox, "orpheus": Orpheus}[a.backend](a)


def qc(wav, sr, text):
    """Cheap sanity check: duration vs word count (normal speech is about 2-3.5 words per second) and clipping/silence."""
    dur, words = len(wav) / sr, max(1, len(text.split()))
    flags = []
    if dur / words > 0.9:
        flags.append("slow_or_rambling")
    if dur / words < 0.18:
        flags.append("too_fast_or_cut")
    if np.abs(wav).max() < 0.02:
        flags.append("silent")
    return round(dur, 2), flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input"); ap.add_argument("--out")
    ap.add_argument("--backend", default=None, help="chatterbox | turbo | orpheus | mock (default: tts.json defaults)")
    ap.add_argument("--only", default=""); ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--max-minutes", type=float, default=240)
    ap.add_argument("--revision", default=None, help="pin the main model to a commit hash")
    ap.add_argument("--print-requirements", action="store_true")
    a = ap.parse_args()
    if a.print_requirements:
        print(BACKENDS[a.backend or "chatterbox"]["pip"])
        return
    d, voices, styles, lines = load_job(a.input, a)
    a.backend = d["backend"]
    out_audio = os.path.join(a.out, "audio")
    os.makedirs(out_audio, exist_ok=True)
    todo = [ln for ln in lines if a.force or not os.path.exists(os.path.join(out_audio, ln["id"] + ".wav"))]
    log(f"backend {a.backend} ({BACKENDS[a.backend]['license']}): {len(lines)} lines, {len(todo)} to do, {int(d['variants'])} variant(s)")
    for ln in todo:
        log(" ", ln["id"], ln["who"], ln.get("style", "neutral"), "|", ln["text"][:70])
    if a.dry_run:
        return
    if not todo:
        log("nothing to do")
    t0, results, be = time.time(), [], None
    if todo:
        if a.backend != "mock" and not shutil.which("nvidia-smi"):
            sys.exit("NO GPU FOUND: stopping instead of wasting time on a CPU run.")
        be = make_backend(a)
    for ln in todo:
        if time.time() - t0 > a.max_minutes * 60:
            log("time limit reached, stopping (run again to resume)")
            break
        st = settings(ln, voices, styles)
        v = voices[ln["who"]]
        ref = os.path.join(a.input, v["ref"]) if v.get("ref") else None
        for k in range(int(d["variants"])):
            name = ln["id"] if k == 0 else f"{ln['id']}__v{k + 1}"
            t1 = time.time()
            try:
                wav = be.say(ln, st, ref, int(d["seed"]) + 101 * k)
                dur, flags = qc(wav, be.sr, ln["text"])
                write_wav(os.path.join(out_audio, name + ".wav"), wav, be.sr)
                results.append(dict(id=name, who=ln["who"], status="ok", seconds=round(time.time() - t1, 1), audio_seconds=dur, flags=flags, settings=st))
                log(f"ok {name} {dur}s in {time.time() - t1:.1f}s {flags or ''}")
            except Exception as ex:      # noqa: BLE001
                traceback.print_exc()
                results.append(dict(id=name, who=ln["who"], status="error", error=repr(ex)))
    info = dict(backend=a.backend, license=BACKENDS[a.backend]["license"], model=BACKENDS[a.backend]["repo"],
                model_revision=a.revision or (model_sha(BACKENDS[a.backend]["repo"]) if a.backend != "mock" else "-"), results=results)
    rp = os.path.join(a.out, "results.json")
    if os.path.exists(rp):                       # keep earlier results when resuming
        old = json.load(open(rp))
        keep = [r for r in old.get("results", []) if r["id"] not in {x["id"] for x in results}]
        info["results"] = keep + results
    json.dump(info, open(rp, "w"), indent=1)
    zp = os.path.join(a.out, "dumpling_tts.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(out_audio)):
            z.write(os.path.join(out_audio, f), "audio/" + f)
        z.write(rp, "results.json")
    bad = [r for r in info["results"] if r["status"] != "ok"]
    log(f"done: {len(info['results']) - len(bad)} ok, {len(bad)} failed; zip {zp}")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
