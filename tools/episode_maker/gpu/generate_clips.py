#!/usr/bin/env python3
"""Batch image-to-video on a free GPU (Kaggle / Colab): clips.json + images -> mp4 clips -> zip.

    python3 generate_clips.py --input /path/to/input --out /path/to/output          # all clips, resume
    python3 generate_clips.py --input ... --out ... --dry-run                        # validate + plan, no GPU needed
    python3 generate_clips.py --input ... --out ... --only c01,c02 --force           # redo some clips
    python3 generate_clips.py --input ... --out ... --backend wan                    # fallback model

`input` holds clips.json and the images it references (paths relative to clips.json).
Results: <out>/clips/<id>.mp4 (+ <id>.json), <out>/results.json, <out>/dumpling_clips.zip.
Safe to stop and start again: finished clips are skipped.  With 2 GPUs (Kaggle T4 x2) the
work is split over both automatically.  Needs: torch, diffusers, transformers, accelerate,
sentencepiece, pillow, numpy, ffmpeg (all preinstalled or installed by the notebook).
"""
import argparse, json, os, sys, time, shutil, subprocess, threading, traceback, inspect, zipfile, re

ROOT_DEFAULTS = dict(
    backend="ltx", width=480, height=832, fps=24, seconds=5.0, fit="cover", bg="#FFF3DC", crf=16,
    upscale=[720, 1280], variants=1,
    style=("soft children's picture-book 2D cartoon, round shapes, bright flat pastel colors, thick brown outlines, "
           "clean stable character design, smooth gentle animation"),
    negative=("photorealistic, 3d render, blurry, low quality, distorted face, extra limbs, extra fingers, deformed hands, "
              "changing clothes, morphing, flickering, text, watermark, subtitles, jitter, shaky camera, cut, scene change"),
)
# model ids are the diffusers-format repos on huggingface.co
BACKENDS = {
    # PRIMARY: fastest, best fidelity to the start image, supports an end image, fits a T4 (2B model)
    "ltx": dict(model="Lightricks/LTX-Video-0.9.5", steps=30, guidance=3.0, mod=8, res_mult=32, end_image=True, pipeline="ltx"),
    # EXPERIMENTAL (Kaggle only: needs ~26 GB CPU RAM): 13B distilled, 8 steps, no CFG
    "ltx13b": dict(model="Lightricks/LTX-Video-0.9.8-13B-distilled", steps=8, guidance=1.0, mod=8, res_mult=32, end_image=True, pipeline="ltx", offload=True),
    # FALLBACK: better motion / 2D style, much slower (about 5x), start image only
    "wan": dict(model="Wan-AI/Wan2.2-TI2V-5B-Diffusers", steps=25, guidance=5.0, mod=4, res_mult=32, end_image=False, pipeline="wan"),
    # test double: no GPU, writes a colour-gradient video (checks the whole batch / resume / zip logic)
    "mock": dict(model="-", steps=1, guidance=1.0, mod=8, res_mult=32, end_image=True, pipeline="mock"),
}
FILE_NAME = re.compile(r"^[A-Za-z0-9_.\-]+$")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ------------------------------------------------------------------ job list
def load_jobs(input_dir, overrides):
    path = os.path.join(input_dir, "clips.json")
    data = json.load(open(path, encoding="utf-8"))
    clips = data["clips"] if isinstance(data, dict) else data
    defaults = dict(ROOT_DEFAULTS)
    if isinstance(data, dict):
        defaults.update(data.get("defaults", {}))
    defaults.update({k: v for k, v in overrides.items() if v is not None})
    jobs, seen = [], set()
    for i, c in enumerate(clips):
        for key in ("id", "start", "prompt"):
            if not c.get(key):
                raise ValueError(f"clip #{i + 1}: missing '{key}'")
        if not FILE_NAME.match(c["id"]):
            raise ValueError(f"clip id '{c['id']}' may only contain letters, digits, _ . -")
        j = dict(defaults); j.update(c)
        j.update({k: v for k, v in overrides.items() if v is not None and k in ("steps", "guidance", "width", "height", "seconds", "backend")})
        if j["backend"] not in BACKENDS:
            raise ValueError(f"clip {c['id']}: unknown backend {j['backend']}")
        b = BACKENDS[j["backend"]]
        j["steps"] = j.get("steps") or b["steps"]
        j["guidance"] = j.get("guidance") if j.get("guidance") is not None else b["guidance"]
        m = b["res_mult"]
        j["width"], j["height"] = int(round(j["width"] / m) * m), int(round(j["height"] / m) * m)
        n = max(9, round(float(j["seconds"]) * j["fps"]))
        j["frames"] = b["mod"] * round((n - 1) / b["mod"]) + 1
        j["start_path"] = os.path.join(input_dir, j["start"])
        j["end_path"] = os.path.join(input_dir, j["end"]) if j.get("end") else None
        for p in (j["start_path"], j["end_path"]):
            if p and not os.path.exists(p):
                raise FileNotFoundError(f"clip {c['id']}: image not found: {p}")
        style = j.get("style", "")
        j["full_prompt"] = (j["prompt"].rstrip(". ") + (". " + style if style else "")).strip()
        j["seed"] = int(j.get("seed", 1000 + i))
        nv = int(j.get("variants", 1))
        for v in range(nv):
            jj = dict(j)
            jj["id"] = c["id"] if nv == 1 else f"{c['id']}__v{v + 1}"
            jj["seed"] = j["seed"] + v
            if jj["id"] in seen:
                raise ValueError(f"duplicate id {jj['id']}")
            seen.add(jj["id"])
            jobs.append(jj)
    return jobs


def prep_image(path, w, h, fit, bg):
    from PIL import Image
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        col = tuple(int(bg.lstrip("#")[k:k + 2], 16) for k in (0, 2, 4))
        base = Image.new("RGB", im.size, col); base.paste(im, mask=im.split()[-1]); im = base
    else:
        im = im.convert("RGB")
    sw, sh = im.size
    s = max(w / sw, h / sh) if fit == "cover" else min(w / sw, h / sh)
    nw, nh = max(1, round(sw * s)), max(1, round(sh * s))
    im = im.resize((nw, nh), Image.LANCZOS)
    if fit == "cover":
        l, t = (nw - w) // 2, (nh - h) // 2
        return im.crop((l, t, l + w, t + h))
    col = tuple(int(bg.lstrip("#")[k:k + 2], 16) for k in (0, 2, 4))
    can = Image.new("RGB", (w, h), col); can.paste(im, ((w - nw) // 2, (h - nh) // 2))
    return can


def write_video(frames, out_path, fps, size, crf):
    """frames: list of PIL images. Encodes (and Lanczos-upscales) with ffmpeg, no temp files."""
    w, h = frames[0].size
    uw, uh = size if size else (w, h)
    vf = f"scale={uw}:{uh}:flags=lanczos" + (",unsharp=5:5:0.35:5:5:0.0" if (uw, uh) != (w, h) else "")
    tmp = out_path + ".part.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
           "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    os.replace(tmp, out_path)


# ------------------------------------------------------------------ backends
class BlackFrames(RuntimeError):
    pass


def check_not_black(frames):
    import numpy as np
    for f in (frames[0], frames[len(frames) // 2], frames[-1]):
        if np.asarray(f).mean() < 2.0:
            raise BlackFrames("output is black (fp16 overflow?)")


class MockBackend:
    name = "mock"
    def __init__(self, cfg, dtype): pass
    def prepare(self, jobs): pass
    def generate(self, job, start_img, end_img):
        from PIL import Image
        n = job["frames"]; w, h = job["width"], job["height"]
        out = []
        for i in range(n):
            t = i / max(1, n - 1)
            f = Image.blend(start_img, end_img or start_img.transpose(Image.FLIP_LEFT_RIGHT), t)
            out.append(f)
        return out
    def close(self): pass


class DiffusersBackend:
    """LTX-Video (LTXConditionPipeline) or Wan 2.2 TI2V (WanImageToVideoPipeline)."""
    def __init__(self, cfg, dtype):
        import torch
        self.torch, self.cfg = torch, cfg
        cap = torch.cuda.get_device_capability()[0] if torch.cuda.is_available() else 0
        self.auto = dtype == "auto"
        self.dtype = {"fp16": torch.float16, "bf16": torch.bfloat16, "fp32": torch.float32}.get(dtype) or (torch.bfloat16 if cap >= 8 else torch.float16)
        self.pipe, self.embeds = None, {}
        log(f"backend {cfg['pipeline']} model={cfg['model']} dtype={self.dtype} gpu={torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none'}")

    def _cls(self):
        if self.cfg["pipeline"] == "ltx":
            from diffusers import LTXConditionPipeline
            return LTXConditionPipeline
        from diffusers import WanImageToVideoPipeline
        return WanImageToVideoPipeline

    def _filter(self, fn, kw):
        ok = set(inspect.signature(fn).parameters)
        dropped = [k for k in kw if k not in ok]
        if dropped:
            log("  (pipeline ignores:", ", ".join(dropped) + ")")
        return {k: v for k, v in kw.items() if k in ok}

    def prepare(self, jobs):
        """Encode all prompts first with ONLY the text encoder loaded, then drop it (saves ~10 GB RAM/VRAM)."""
        torch, cls = self.torch, self._cls()
        try:
            txt = cls.from_pretrained(self.cfg["model"], transformer=None, vae=None, torch_dtype=self.dtype)
            txt.to("cuda")
            for j in jobs:
                with torch.no_grad():
                    r = txt.encode_prompt(j["full_prompt"], negative_prompt=j["negative"], do_classifier_free_guidance=True, device="cuda")
                self.embeds[j["id"]] = tuple(None if x is None else x.detach().cpu() for x in r)
            del txt; self._free()
            log(f"prompts encoded for {len(jobs)} clips (text encoder released)")
        except Exception as ex:
            log("prompt pre-encoding not available, using the normal path:", repr(ex)[:200])
            self.embeds = {}
            self._free()

    def _free(self):
        import gc
        gc.collect(); self.torch.cuda.empty_cache()

    def _load(self):
        torch, cls = self.torch, self._cls()
        kw = dict(torch_dtype=self.dtype)
        if self.embeds:
            kw.update(text_encoder=None, tokenizer=None)
        if self.cfg["pipeline"] == "wan":
            from diffusers import AutoencoderKLWan
            kw["vae"] = AutoencoderKLWan.from_pretrained(self.cfg["model"], subfolder="vae", torch_dtype=torch.float32)
        pipe = cls.from_pretrained(self.cfg["model"], **kw)
        if self.cfg.get("offload") or not self.embeds or self.cfg["pipeline"] == "wan":
            pipe.enable_model_cpu_offload()
        else:
            pipe.to("cuda")
        try:
            pipe.vae.enable_tiling()
        except Exception:
            pass
        self.pipe = pipe
        log("pipeline loaded")

    def reload_dtype(self, dtype):
        self.pipe = None; self._free(); self.dtype = dtype

    def generate(self, job, start_img, end_img):
        torch = self.torch
        if self.pipe is None:
            self._load()
        gen = torch.Generator(device="cuda").manual_seed(job["seed"])
        emb = self.embeds.get(job["id"])
        kw = dict(width=job["width"], height=job["height"], num_frames=job["frames"], num_inference_steps=job["steps"],
                  guidance_scale=job["guidance"], generator=gen, output_type="pil")
        if emb:
            if self.cfg["pipeline"] == "ltx":
                pe, pm, ne, nm = [None if x is None else x.to("cuda") for x in emb]
                kw.update(prompt_embeds=pe, prompt_attention_mask=pm, negative_prompt_embeds=ne, negative_prompt_attention_mask=nm)
            else:
                pe, ne = [None if x is None else x.to("cuda") for x in emb[:2]]
                kw.update(prompt_embeds=pe, negative_prompt_embeds=ne)
        else:
            kw.update(prompt=job["full_prompt"], negative_prompt=job["negative"])
        if self.cfg["pipeline"] == "ltx":
            from diffusers.pipelines.ltx.pipeline_ltx_condition import LTXVideoCondition
            conds = [LTXVideoCondition(image=start_img, frame_index=0)]
            if end_img is not None:
                conds.append(LTXVideoCondition(image=end_img, frame_index=job["frames"] - 1))
            kw.update(conditions=conds, decode_timestep=0.05, decode_noise_scale=0.025, frame_rate=job["fps"])
            if job.get("cond_noise") is not None:       # lower = stays closer to the start image (less motion)
                kw["image_cond_noise_scale"] = float(job["cond_noise"])
            try:
                out = self.pipe(**self._filter(self.pipe.__call__, kw))
            except (ValueError, AssertionError) as ex:
                if end_img is None:
                    raise
                log("  end-image conditioning rejected, retrying with the start image only:", str(ex)[:120])
                kw["conditions"] = conds[:1]
                out = self.pipe(**self._filter(self.pipe.__call__, kw))
        else:
            if end_img is not None:
                log("  note: the wan backend ignores 'end' (start image only)")
            kw["image"] = start_img
            out = self.pipe(**self._filter(self.pipe.__call__, kw))
        frames = out.frames[0]
        check_not_black(frames)
        return frames

    def close(self):
        self.pipe = None; self._free()


def make_backend(name, dtype):
    cfg = BACKENDS[name]
    return MockBackend(cfg, dtype) if cfg["pipeline"] == "mock" else DiffusersBackend(cfg, dtype)


# ------------------------------------------------------------------ worker
def out_paths(out_dir, jid):
    d = os.path.join(out_dir, "clips")
    return os.path.join(d, jid + ".mp4"), os.path.join(d, jid + ".json")


def run_worker(args, jobs, shard):
    out = args.out
    os.makedirs(os.path.join(out, "clips"), exist_ok=True)
    os.makedirs(os.path.join(out, "prepped"), exist_ok=True)
    deadline = time.time() + args.max_minutes * 60
    todo = [j for j in jobs if args.force or not os.path.exists(out_paths(out, j["id"])[0])]
    todo = todo[shard[0]::shard[1]]
    log(f"worker {shard[0] + 1}/{shard[1]}: {len(todo)} clips to do")
    by_backend = {}
    for j in todo:
        by_backend.setdefault(j["backend"], []).append(j)
    for bname, js in by_backend.items():
        be = make_backend(bname, args.dtype)
        be.prepare(js)
        for j in js:
            if time.time() > deadline:
                log("time budget reached, stopping cleanly (run again to continue)")
                return
            mp4, meta = out_paths(out, j["id"])
            t0 = time.time()
            res = dict(id=j["id"], backend=bname, seed=j["seed"], frames=j["frames"], size=[j["width"], j["height"]], steps=j["steps"])
            try:
                s_img = prep_image(j["start_path"], j["width"], j["height"], j["fit"], j["bg"])
                e_img = prep_image(j["end_path"], j["width"], j["height"], j["fit"], j["bg"]) if j["end_path"] else None
                s_img.save(os.path.join(out, "prepped", j["id"] + ".png"))
                log(f"[{j['id']}] {j['frames']} frames {j['width']}x{j['height']} steps={j['steps']} seed={j['seed']}")
                try:
                    frames = be.generate(j, s_img, e_img)
                except BlackFrames:
                    if not getattr(be, "auto", False):
                        raise
                    log("  black output with fp16, reloading in bf16 and retrying")
                    be.reload_dtype(be.torch.bfloat16); frames = be.generate(j, s_img, e_img)
                except RuntimeError as ex:
                    if "out of memory" not in str(ex).lower():
                        raise
                    log("  out of memory, retrying once at 80% size")
                    be._free()
                    j2 = dict(j); m = BACKENDS[bname]["res_mult"]
                    j2["width"], j2["height"] = [int(round(v * 0.8 / m) * m) for v in (j["width"], j["height"])]
                    frames = be.generate(j2, prep_image(j["start_path"], j2["width"], j2["height"], j["fit"], j["bg"]), None)
                write_video(frames, mp4, j["fps"], j.get("upscale"), j["crf"])
                res.update(status="ok", seconds=round(time.time() - t0, 1))
                log(f"[{j['id']}] done in {res['seconds']} s -> {mp4}")
            except Exception as ex:
                traceback.print_exc()
                res.update(status="failed", error=repr(ex)[:300], seconds=round(time.time() - t0, 1))
                try:
                    be._free()
                except Exception:
                    pass
            json.dump(dict(res, prompt=j["full_prompt"], negative=j["negative"], start=j["start"], end=j.get("end")), open(meta, "w"), indent=1)
        be.close()


# ------------------------------------------------------------------ main / multi-GPU / zip
def gpu_count():
    try:
        r = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=20)
        return len([l for l in r.stdout.splitlines() if l.startswith("GPU")])
    except Exception:
        return 0


def make_zip(out):
    zp = os.path.join(out, "dumpling_clips.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        cdir = os.path.join(out, "clips")
        for f in sorted(os.listdir(cdir)) if os.path.isdir(cdir) else []:
            z.write(os.path.join(cdir, f), "clips/" + f)
        for f in ("results.json", "clips.json"):
            if os.path.exists(os.path.join(out, f)):
                z.write(os.path.join(out, f), f)
    return zp


def collect_results(out, jobs):
    rows = []
    for j in jobs:
        mp4, meta = out_paths(out, j["id"])
        if os.path.exists(meta):
            rows.append(json.load(open(meta)))
        elif os.path.exists(mp4):
            rows.append(dict(id=j["id"], status="ok"))
        else:
            rows.append(dict(id=j["id"], status="missing"))
    json.dump(rows, open(os.path.join(out, "results.json"), "w"), indent=1)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--only", default=None, help="comma separated clip ids (base id matches all its variants)")
    ap.add_argument("--force", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backend", default=None, choices=sorted(BACKENDS)); ap.add_argument("--dtype", default="auto", choices=["auto", "fp16", "bf16", "fp32"])
    ap.add_argument("--steps", type=int, default=None); ap.add_argument("--guidance", type=float, default=None)
    ap.add_argument("--width", type=int, default=None); ap.add_argument("--height", type=int, default=None); ap.add_argument("--seconds", type=float, default=None)
    ap.add_argument("--gpus", default="auto", help="auto | 1 | 2 (number of worker processes, one per GPU)")
    ap.add_argument("--max-minutes", type=float, default=600, help="stop starting new clips after this many minutes")
    ap.add_argument("--shard", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args()
    jobs = load_jobs(a.input, dict(steps=a.steps, guidance=a.guidance, width=a.width, height=a.height, seconds=a.seconds, backend=a.backend))
    if a.only:
        keep = set(a.only.split(","))
        jobs = [j for j in jobs if j["id"] in keep or j["id"].split("__v")[0] in keep]
    os.makedirs(a.out, exist_ok=True)
    shutil.copy(os.path.join(a.input, "clips.json"), os.path.join(a.out, "clips.json"))
    done = [j for j in jobs if os.path.exists(out_paths(a.out, j["id"])[0])]
    if a.dry_run:
        log(f"{len(jobs)} clips ({len(done)} already done)")
        tot = 0
        for j in jobs:
            est = {"ltx": 6, "ltx13b": 10, "wan": 30, "mock": 0}[j["backend"]] * (j["steps"] / BACKENDS[j["backend"]]["steps"]) * (j["frames"] / 121) * (j["width"] * j["height"] / (480 * 832))
            tot += 0 if j["id"] in {d["id"] for d in done} else est
            print(f"  {j['id']:<28} {j['backend']:<7} {j['width']}x{j['height']} {j['frames']}f steps={j['steps']} seed={j['seed']} "
                  f"{'DONE' if j in done else '~%.0f min on a T4 (estimate)' % est}")
            print(f"      {j['full_prompt'][:140]}")
        log(f"estimated remaining GPU time: {tot:.0f} min (one T4; halve it with 2 GPUs). Estimates are not measured.")
        return
    if a.shard:
        i, n = [int(x) for x in a.shard.split("/")]
        run_worker(a, jobs, (i, n))
        return
    n = {"auto": max(1, gpu_count()), "1": 1, "2": 2}[a.gpus]
    if any(BACKENDS[j["backend"]]["pipeline"] == "mock" for j in jobs):
        n = min(n, 2)
    if n == 1:
        run_worker(a, jobs, (0, 1))
    else:
        log(f"{n} GPUs: starting {n} workers")
        passthrough, skip = [], False
        for x in sys.argv[1:]:
            if skip:
                skip = False
            elif x == "--gpus":
                skip = True
            elif not x.startswith("--gpus="):
                passthrough.append(x)
        procs = []
        for i in range(n):
            env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(i), PYTHONUNBUFFERED="1")
            cmd = [sys.executable, os.path.abspath(__file__)] + passthrough + ["--shard", f"{i}/{n}"]
            p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            procs.append(p)
            threading.Thread(target=lambda p=p, i=i: [print(f"[gpu{i}] {l}", end="", flush=True) for l in p.stdout], daemon=True).start()
        for p in procs:
            p.wait()
        time.sleep(0.5)
    rows = collect_results(a.out, jobs)
    zp = make_zip(a.out)
    ok = sum(r["status"] == "ok" for r in rows)
    log(f"finished: {ok}/{len(rows)} clips ok. ZIP: {zp} ({os.path.getsize(zp) / 1e6:.1f} MB)")
    for r in rows:
        if r["status"] != "ok":
            log("  not done:", r["id"], r.get("status"), r.get("error", ""))


if __name__ == "__main__":
    main()
