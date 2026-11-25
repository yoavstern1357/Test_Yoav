#!/usr/bin/env python3
"""Batch song generation on a free GPU (Kaggle T4): music.json -> one audio file per track and seed.

    python3 generate_music.py --input /path/to/input --out /path/to/output            # all tracks, resume
    python3 generate_music.py --input ... --out ... --dry-run                         # validate + plan, no GPU needed
    python3 generate_music.py --input ... --out ... --backend mock                    # CPU test of the batch logic
    python3 generate_music.py --backend acestep --install                             # install packages (keeps the preinstalled torch)

Used for the series opening song (sung in Japanese). Models (open weights, commercial use allowed):
  acestep     ACE-Step v1 3.5B (ACE-Step/ACE-Step-v1-3.5B, Apache-2.0, safetensors): text prompt (style tags) + lyrics with
              [verse] [chorus] [bridge] [inst] tags -> full song with vocals; Japanese is one of its top-10 languages.
  mock        no GPU: a tone burst pattern per track (tests the batch / resume / zip logic).
Security: only the official GitHub repo (ace-step/ACE-Step, Apache-2.0) and the official HF weights; no token; the model
commit is written to results.json.

`music.json`:
  {"defaults": {"backend": "acestep", "infer_step": 60, "guidance_scale": 15.0, "format": "flac"},
   "tracks": [{"id": "full_a", "duration": 60, "prompt": "style tags", "lyrics": "[verse]\\n...", "seeds": [101, 102],
               "infer_step": 60, "guidance_scale": 15.0, "guidance_interval": 0.5, "omega_scale": 10.0}]}
Result files: audio/<id>__s<seed>.<format>, results.json (QC numbers), dumpling_music.zip.
"""
import argparse, json, os, re, shutil, subprocess, sys, time, traceback, zipfile
import numpy as np

BACKENDS = {
    "acestep": dict(repo="ACE-Step/ACE-Step-v1-3.5B", license="Apache-2.0", sr=44100),
    "mock": dict(repo="-", license="-", sr=44100),
}
ID = re.compile(r"^[A-Za-z0-9_.\-]+$")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def load_job(input_dir, args):
    data = json.load(open(os.path.join(input_dir, "music.json"), encoding="utf-8"))
    d = dict(backend="acestep", infer_step=60, guidance_scale=15.0, format="flac")
    d.update(data.get("defaults", {}))
    if args.backend:
        d["backend"] = args.backend
    if d["backend"] not in BACKENDS:
        raise ValueError(f"backend must be one of {sorted(BACKENDS)}")
    only = set(x for x in (args.only or "").split(",") if x)
    tracks, seen = [], set()
    for i, t in enumerate(data["tracks"]):
        tid = str(t["id"])
        if not ID.match(tid) or tid in seen:
            raise ValueError(f"track #{i + 1}: bad or duplicate id {tid!r}")
        seen.add(tid)
        if not str(t.get("prompt", "")).strip():
            raise ValueError(f"track {tid}: empty prompt (style tags)")
        if not str(t.get("lyrics", "")).strip():
            raise ValueError(f"track {tid}: empty lyrics (use '[inst]' for an instrumental)")
        dur = float(t.get("duration", 30))
        if not 5 <= dur <= 240:
            raise ValueError(f"track {tid}: duration must be 5-240 s")
        if only and tid not in only and not any(tid.startswith(o) for o in only):
            continue
        tracks.append({**d, **t, "id": tid, "duration": dur, "seeds": [int(s) for s in t.get("seeds", [7])]})
    jobs = [dict(t, seed=s, name=f"{t['id']}__s{s}") for t in tracks for s in t["seeds"]]
    return d, jobs


def model_sha(repo):
    try:
        from huggingface_hub import HfApi
        return HfApi().model_info(repo).sha
    except Exception as ex:           # noqa: BLE001
        return f"unknown ({ex.__class__.__name__})"


# ------------------------------------------------------------------ backends
class Mock:
    sr = 44100

    def __init__(self, a, d):
        pass

    def make(self, job, path):
        import soundfile as sf
        n = int(self.sr * job["duration"])
        t = np.arange(n) / self.sr
        w = 0.3 * np.sin(2 * np.pi * 220 * t) * (np.sin(2 * np.pi * 3 * t) > 0)
        sf.write(path, np.stack([w, w], 1).astype("float32"), self.sr)
        return path


class AceStep:
    """ACE-Step v1 3.5B through its own pipeline class (acestep.pipeline_ace_step.ACEStepPipeline)."""

    def __init__(self, a, d):
        import torch
        from acestep.pipeline_ace_step import ACEStepPipeline
        self.torch = torch
        self.ck = os.path.join(os.environ.get("HF_HOME", os.path.expanduser("~/.cache")), "ace_step_ckpt")
        os.makedirs(self.ck, exist_ok=True)
        last = None
        # T4 has no native bf16: bf16 still runs (emulated); if it fails, fp32 with CPU offload is the fallback
        for dtype, off in (("bfloat16", False), ("float32", True)):
            try:
                self.pipe = ACEStepPipeline(checkpoint_dir=self.ck, dtype=dtype, torch_compile=False, cpu_offload=off, overlapped_decode=True)
                self.dtype, self.off = dtype, off
                log("ACE-Step pipeline ready", dtype, "cpu_offload" if off else "")
                return
            except Exception as ex:      # noqa: BLE001
                last = ex
                log("pipeline init", dtype, "failed:", repr(ex)[:300])
        raise last

    def make(self, job, path):
        tmp = path + ".tmp.wav"
        self.torch.manual_seed(job["seed"])
        res = self.pipe(
            format="wav", audio_duration=job["duration"], prompt=job["prompt"], lyrics=job["lyrics"],
            infer_step=int(job["infer_step"]), guidance_scale=float(job["guidance_scale"]),
            scheduler_type="euler", cfg_type="apg", omega_scale=float(job.get("omega_scale", 10.0)),
            manual_seeds=str(job["seed"]), guidance_interval=float(job.get("guidance_interval", 0.5)),
            guidance_interval_decay=0.0, min_guidance_scale=3.0, use_erg_tag=True, use_erg_lyric=False,
            use_erg_diffusion=True, oss_steps="", guidance_scale_text=0.0, guidance_scale_lyric=0.0,
            save_path=tmp)
        wav_path = res[0]
        import soundfile as sf
        w, sr = sf.read(wav_path, always_2d=True)
        sf.write(path, w.astype("float32"), sr, **({"subtype": "PCM_16"} if path.endswith(".wav") else {}))
        for f in (wav_path, tmp, wav_path.replace(".wav", "_input_params.json")):
            if os.path.isfile(f):
                os.remove(f)
        self.sr = sr
        return path


# ------------------------------------------------------------------ installer (Kaggle / Colab: NEVER replace the preinstalled torch)
PIN_FILE = "/tmp/dumpling_pins.txt"
ACE_GIT = "git+https://github.com/ace-step/ACE-Step.git"
RECIPES = {
    "acestep": ([ACE_GIT],
                ["transformers==4.50.0", "diffusers>=0.33.0", "accelerate==1.6.0", "librosa==0.11.0", "loguru==0.7.3", "pypinyin==0.53.0",
                 "pytorch_lightning==2.5.1", "soundfile", "py3langid==0.3.0", "hangul-romanize==0.1.0", "num2words==0.5.14",
                 "cutlet", "fugashi", "unidic-lite", "peft", "datasets", "click", "tqdm", "matplotlib", "huggingface_hub", "spacy"]),
}
MODULE_TO_PIP = {"sklearn": "scikit-learn", "cv2": "opencv-python-headless", "yaml": "pyyaml", "pkg_resources": "setuptools<81"}
IMPORT_TEST = {"acestep": "import acestep.pipeline_ace_step"}


def _run(cmd, tail=1500):
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if r.returncode and out:
        print(out[-tail:], flush=True)
    return r


def write_pins():
    from importlib.metadata import PackageNotFoundError, version
    lines = []
    for p in ("torch", "torchvision", "torchaudio", "torchcodec", "triton", "numpy"):
        try:
            lines.append(f"{p}=={version(p)}")
        except PackageNotFoundError:
            pass
    open(PIN_FILE, "w").write("\n".join(lines) + "\n")
    log("pinned:", " ".join(lines))


def pip_install(pkgs, no_deps=False):
    base = [sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check"]
    if no_deps:
        return _run(base + ["--no-deps"] + pkgs).returncode == 0
    if _run(base + ["-c", PIN_FILE] + pkgs).returncode == 0:
        return True
    log("grouped install failed, trying one by one:", pkgs)
    ok = True
    for p in pkgs:
        if _run(base + ["-c", PIN_FILE, p]).returncode:
            ok = False
            log("install failed (continuing):", p)
    return ok


def install_backend(backend):
    import importlib
    recipe = RECIPES.get(backend)
    if not recipe:
        return
    write_pins()
    nodeps, deps = recipe
    pip_install(deps)
    if nodeps:
        pip_install(nodeps, no_deps=True)
    importlib.invalidate_caches()
    for _ in range(15):                      # heal: install a module the import test says is missing, then test again
        r = _run([sys.executable, "-c", IMPORT_TEST[backend]], tail=2500)
        if r.returncode == 0:
            log("import test ok")
            break
        m = re.search(r"No module named '([^'.]+)", r.stdout + r.stderr)
        if not m:
            log("import test failed for another reason (see above)")
            break
        pkg = MODULE_TO_PIP.get(m.group(1), m.group(1).replace("_", "-"))
        log("missing module", m.group(1), "-> pip install", pkg)
        if not pip_install([pkg]):
            pip_install([pkg], no_deps=True)
    try:
        import torch
        log("torch", torch.__version__, "cuda", torch.version.cuda, "ok" if torch.cuda.is_available() else "NO CUDA")
    except Exception as ex:                  # noqa: BLE001
        log("version report failed:", repr(ex)[:200])


def make_backend(a, d):
    return {"mock": Mock, "acestep": AceStep}[a.backend](a, d)


def qc(path):
    """Loudness, peak, clipping, tempo estimate and a rough 'vocal band present' number for a quick pick."""
    import soundfile as sf
    w, sr = sf.read(path, always_2d=True)
    m = w.mean(1)
    info = dict(seconds=round(len(m) / sr, 2), peak=round(float(np.abs(w).max()), 3), rms_db=round(float(20 * np.log10(np.sqrt(np.mean(m ** 2)) + 1e-9)), 1),
                clipped_pct=round(100 * float(np.mean(np.abs(w) > 0.999)), 3))
    try:
        import librosa
        tempo, _ = librosa.beat.beat_track(y=m[: sr * 60].astype("float32"), sr=sr)
        info["tempo_bpm"] = round(float(np.atleast_1d(tempo)[0]), 1)
        S = np.abs(librosa.stft(m[: sr * 60].astype("float32"), n_fft=2048)) ** 2
        f = librosa.fft_frequencies(sr=sr, n_fft=2048)
        band = S[(f > 300) & (f < 3400)].sum() / (S.sum() + 1e-9)
        info["mid_band_ratio"] = round(float(band), 3)
    except Exception as ex:                  # noqa: BLE001
        info["qc_note"] = repr(ex)[:100]
    if info["rms_db"] < -45:
        info["flag"] = "silent"
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input"); ap.add_argument("--out")
    ap.add_argument("--backend", default=None, help="acestep | mock (default: music.json defaults)")
    ap.add_argument("--only", default="", help="track ids (or id prefixes) separated by commas")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--max-minutes", type=float, default=240)
    ap.add_argument("--limit", type=int, default=0, help="render only the first N jobs (smoke test)")
    ap.add_argument("--revision", default=None)
    ap.add_argument("--install", action="store_true", help="install the backend's packages (keeps the preinstalled torch) and exit")
    a = ap.parse_args()
    if a.install:
        install_backend(a.backend or "acestep")
        return
    d, jobs = load_job(a.input, a)
    a.backend = d["backend"]
    ext = d.get("format", "flac")
    out_audio = os.path.join(a.out, "audio")
    os.makedirs(out_audio, exist_ok=True)
    todo = [j for j in jobs if a.force or not os.path.exists(os.path.join(out_audio, j["name"] + "." + ext))]
    if a.limit:
        todo = todo[: a.limit]
    log(f"backend {a.backend} ({BACKENDS[a.backend]['license']}): {len(jobs)} jobs, {len(todo)} to do")
    for j in todo:
        log(" ", j["name"], f"{j['duration']}s", "|", j["prompt"][:60], "|", len(j["lyrics"].splitlines()), "lyric lines")
    if a.dry_run:
        return
    t0, results, be = time.time(), [], None
    if todo:
        if a.backend != "mock" and not shutil.which("nvidia-smi"):
            sys.exit("NO GPU FOUND: stopping instead of wasting time on a CPU run.")
        be = make_backend(a, d)
    for j in todo:
        if time.time() - t0 > a.max_minutes * 60:
            log("time limit reached, stopping (run again to resume)")
            break
        t1 = time.time()
        path = os.path.join(out_audio, j["name"] + "." + ext)
        try:
            be.make(j, path)
            info = qc(path)
            results.append(dict(id=j["name"], track=j["id"], seed=j["seed"], status="ok", gen_seconds=round(time.time() - t1, 1), **info))
            log(f"ok {j['name']} {info} in {time.time() - t1:.0f}s")
        except Exception as ex:      # noqa: BLE001
            traceback.print_exc()
            results.append(dict(id=j["name"], track=j["id"], seed=j["seed"], status="error", error=repr(ex)))
            try:
                import torch
                torch.cuda.empty_cache()
            except Exception:         # noqa: BLE001
                pass
    info = dict(backend=a.backend, license=BACKENDS[a.backend]["license"], model=BACKENDS[a.backend]["repo"],
                model_revision=a.revision or (model_sha(BACKENDS[a.backend]["repo"]) if a.backend != "mock" else "-"), results=results)
    rp = os.path.join(a.out, "results.json")
    if os.path.exists(rp):                       # keep earlier results when resuming
        old = json.load(open(rp))
        keep = [r for r in old.get("results", []) if r["id"] not in {x["id"] for x in results}]
        info["results"] = keep + results
    json.dump(info, open(rp, "w"), indent=1)
    with zipfile.ZipFile(os.path.join(a.out, "dumpling_music.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(out_audio)):
            z.write(os.path.join(out_audio, f), "audio/" + f)
        z.write(rp, "results.json")
    bad = [r for r in info["results"] if r["status"] != "ok"]
    log(f"done: {len(info['results']) - len(bad)} ok, {len(bad)} failed")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
