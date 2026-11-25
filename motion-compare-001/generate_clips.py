#!/usr/bin/env python3
"""Batch image-to-video on a free GPU (Kaggle / Colab): clips.json + images -> mp4 clips -> zip.

    python3 generate_clips.py --input /path/to/input --out /path/to/output          # all clips, resume
    python3 generate_clips.py --input ... --out ... --dry-run                        # validate + plan, no GPU needed
    python3 generate_clips.py --input ... --out ... --only c01,c02 --force           # redo some clips
    python3 generate_clips.py --input ... --out ... --backend wan                    # fallback model

`input` holds clips.json and the images it references (paths relative to clips.json).
Orientations: every clip is made in BOTH formats by default ("orientations": ["portrait", "landscape"], in "defaults" or per clip).
Portrait = <id>.mp4 (480x832 -> 720x1280), landscape = <id>_land.mp4 (832x480 -> 1280x720), same seed. The start (and end) image is
picked per orientation: "start": "images/C01.png" uses images/C01_land.png for the landscape clip when that file exists, or give
"start": {"portrait": "...", "landscape": "..."}. A missing landscape still falls back to a center crop of the portrait one (with a warning).
Results: <out>/clips/<id>.mp4 (+ <id>.json), <out>/results.json, <out>/dumpling_clips.zip.
Motion options (v4.4, see production/v4/motion-tech.md): "keyframes": [{"image": ..., "t": 0}, {"image": ..., "t": 2.0}, {"image": ..., "t": 4.0}] (any number, LTX backends;
"start"/"end" still work), "motion": "low|medium|high" (or a number 0-1), "gen_fps": 12 + "interp": 2 (generate half the frames, RIFE on CPU), "post": {"esrgan": true}.
Safe to stop and start again: finished clips are skipped.  With 2 GPUs (Kaggle T4 x2) the
work is split over both automatically.  Needs: torch, diffusers, transformers, accelerate,
sentencepiece, pillow, numpy, ffmpeg (all preinstalled or installed by the notebook).
"""
import argparse, json, os, sys, time, shutil, subprocess, threading, traceback, inspect, zipfile, re

ROOT_DEFAULTS = dict(
    backend="ltx", width=480, height=832, fps=24, seconds=5.0, fit="cover", bg="#FFF3DC", crf=16,
    upscale=[720, 1280], variants=1, orientations=["portrait", "landscape"], crop_focus=[0.5, 0.5],
    gen_fps=None,       # frames are generated at this rate (default = fps); with "interp": 2 the clip is RIFE-interpolated back to fps on the CPU
    interp=0,           # RIFE factor applied after generation (0 = off, 2 = double the frame rate)
    motion=None,        # None | "low" | "medium" | "high" | 0..1: how far the video may drift from the keyframes (LTX: image_cond_noise_scale)
    post=None,          # {"esrgan": true, "rife": 2}: CPU post-processing in a background thread (see postprocess.py)
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
    "ltx13b": dict(model="Lightricks/LTX-Video-0.9.8-13B-distilled", steps=8, guidance=1.0, mod=8, res_mult=32, end_image=True, pipeline="ltx", offload=True, distilled=True),
    # v4.4: LTX-Video 0.9.8 13B distilled, transformer quantized to 4 bit (bitsandbytes nf4, ~7 GB, fits one T4), 8 steps, no CFG,
    # any number of keyframes. License: LTX-Video Open Weights License (free commercial use below USD 10M annual revenue).
    "ltx98d": dict(model="Lightricks/LTX-Video-0.9.8-13B-distilled", steps=8, guidance=1.0, mod=8, res_mult=32, end_image=True, pipeline="ltx", distilled=True, quant="nf4"),
    # FALLBACK: better motion / 2D style, much slower (about 5x), start image (+ experimental end image, see WanFLPipeline)
    "wan": dict(model="Wan-AI/Wan2.2-TI2V-5B-Diffusers", steps=25, guidance=5.0, mod=4, res_mult=32, end_image=True, pipeline="wan"),
    # EXPERIMENTAL: FastVideo's 3-step DMD distillation of Wan2.2 TI2V-5B (Apache-2.0); needs its own sampler settings, may not work with plain diffusers
    "fastwan": dict(model="FastVideo/FastWan2.2-TI2V-5B-FullAttn-Diffusers", steps=3, guidance=1.0, mod=4, res_mult=32, end_image=True, pipeline="wan"),
    # test double: no GPU, writes a colour-gradient video (checks the whole batch / resume / zip logic)
    "mock": dict(model="-", steps=1, guidance=1.0, mod=8, res_mult=32, end_image=True, pipeline="mock"),
}
FILE_NAME = re.compile(r"^[A-Za-z0-9_.\-]+$")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ------------------------------------------------------------------ job list
ORIENTATIONS = ("portrait", "landscape")
LAND_SUFFIX = "_land"
COMPOSITION = {"portrait": "vertical 9:16 composition", "landscape": "wide horizontal 16:9 composition"}


def orient_size(w, h, orient):
    """Portrait = short side first (480x832), landscape = long side first (832x480)."""
    lo, hi = sorted((int(w), int(h)))
    return (lo, hi) if orient == "portrait" else (hi, lo)


def pick_image(value, orient, input_dir):
    """Resolve a start/end image for an orientation. value = path | {"portrait": path, "landscape": path}.
    A plain path means the portrait image; for landscape the sibling <name>_land<ext> is used when it exists.
    Returns (relative path, exact) where exact=False means the other orientation's image will be center-cropped."""
    ex = lambda r: bool(r) and os.path.exists(os.path.join(input_dir, r))
    if isinstance(value, dict):
        mine, other = value.get(orient), value.get("landscape" if orient == "portrait" else "portrait")
        if ex(mine):
            return mine, True
        return (other, False) if ex(other) else (mine or other, True)
    if orient == "portrait":
        return value, True
    stem, ext = os.path.splitext(value)
    cand = stem + LAND_SUFFIX + ext
    return (cand, True) if ex(cand) else (value, False)


MOTION = {"low": 0.02, "medium": 0.12, "high": 0.30}     # image_cond_noise_scale per motion level
MOTION_WORDS = {"low": "", "medium": "", "high": "Lively, continuous, expressive full-body motion, constantly moving, no still moments. "}


def motion_value(m):
    if m is None:
        return None
    if isinstance(m, str):
        return MOTION[m]
    return 0.02 + 0.28 * max(0.0, min(1.0, float(m)))


def keyframe_specs(c, seconds):
    """Normalise start / end / keyframes of a clip into [{"image": value, "t": seconds, "strength": s}] sorted by time."""
    kfs = []
    if c.get("keyframes"):
        for k in c["keyframes"]:
            k = {"image": k} if isinstance(k, (str, dict)) and not (isinstance(k, dict) and "image" in k) else dict(k)
            t = k.get("t", 0.0)
            t = seconds if t in ("end", "last") else float(t)
            if "pos" in k:
                t = float(k["pos"]) * seconds
            kfs.append(dict(image=k["image"], t=max(0.0, min(float(seconds), t)), strength=float(k.get("strength", 1.0))))
    else:
        kfs.append(dict(image=c["start"], t=0.0, strength=1.0))
        if c.get("end"):
            kfs.append(dict(image=c["end"], t=float(seconds), strength=float(c.get("end_strength", 1.0))))
    kfs.sort(key=lambda k: k["t"])
    if not kfs:
        raise ValueError("no start image / keyframes")
    kfs[0]["t"] = 0.0
    return kfs


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
        for key in ("id", "prompt"):
            if not c.get(key):
                raise ValueError(f"clip #{i + 1}: missing '{key}'")
        if not c.get("start") and not c.get("keyframes"):
            raise ValueError(f"clip #{i + 1}: missing 'start' (or 'keyframes')")
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
        gfps = float(j.get("gen_fps") or j["fps"])
        j["gen_fps"] = gfps
        n = max(9, round(float(j["seconds"]) * gfps))
        j["frames"] = b["mod"] * round((n - 1) / b["mod"]) + 1
        style = j.get("style", "")
        j["seed"] = int(j.get("seed", 1000 + i))
        mv = motion_value(j.get("motion"))
        if mv is not None and j.get("cond_noise") is None:
            j["cond_noise"] = mv
        mw = MOTION_WORDS.get(j.get("motion"), "") if isinstance(j.get("motion"), str) else ("Lively, continuous, expressive full-body motion, constantly moving, no still moments. " if (mv or 0) > 0.2 else "")
        kfs = keyframe_specs(c, float(j["seconds"]))
        if len(kfs) > 1 and not b.get("end_image"):
            log(f"  note: clip {c['id']}: backend {j['backend']} uses only the first keyframe")
        orients = j.get("orientations") or ["portrait"]
        if isinstance(orients, str):
            orients = [orients]
        bad = [o for o in orients if o not in ORIENTATIONS]
        if bad:
            raise ValueError(f"clip {c['id']}: unknown orientation {bad} (use portrait / landscape)")
        nv = int(j.get("variants", 1))
        for orient in orients:
            conds, exact_all = [], True
            for k in kfs:
                rel, exact = pick_image(k["image"], orient, input_dir)
                exact_all = exact_all and exact
                idx = min(j["frames"] - 1, b["mod"] * round(k["t"] * gfps / b["mod"]))
                if k["t"] >= float(j["seconds"]) - 1e-6:
                    idx = j["frames"] - 1
                conds.append(dict(rel=rel, path=os.path.join(input_dir, rel), index=int(idx), strength=k["strength"]))
            stem = c["id"] + (LAND_SUFFIX if orient == "landscape" else "")
            base = dict(j)
            base.update(orientation=orient, start=conds[0]["rel"], end=conds[-1]["rel"] if len(conds) > 1 else None,
                        start_path=conds[0]["path"], end_path=conds[-1]["path"] if len(conds) > 1 else None,
                        conds=conds, crop_fallback=not exact_all, stem=stem)
            base["width"], base["height"] = orient_size(j["width"], j["height"], orient)
            if j.get("upscale"):
                base["upscale"] = list(orient_size(*j["upscale"], orient))
            for cd in conds:
                if not os.path.exists(cd["path"]):
                    raise FileNotFoundError(f"clip {c['id']} ({orient}): image not found: {cd['path']}")
            base["full_prompt"] = (mw + j["prompt"].rstrip(". ") + (". " + style if style else "") + ". " + COMPOSITION[orient].capitalize() + ".").strip()
            for v in range(nv):
                jj = dict(base)
                jj["id"] = stem if nv == 1 else f"{stem}__v{v + 1}"
                jj["base_id"] = c["id"]
                jj["seed"] = j["seed"] + v                          # same seed in both orientations
                if jj["id"] in seen:
                    raise ValueError(f"duplicate id {jj['id']}")
                seen.add(jj["id"])
                jobs.append(jj)
    return jobs


def prep_image(path, w, h, fit, bg, focus=(0.5, 0.5)):
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
        l, t = round((nw - w) * focus[0]), round((nh - h) * focus[1])
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
    def generate(self, job, imgs):
        from PIL import Image
        n = job["frames"]
        first, last = imgs[0][0], imgs[-1][0]
        out = []
        for i in range(n):
            t = i / max(1, n - 1)
            out.append(Image.blend(first, last if len(imgs) > 1 else first.transpose(Image.FLIP_LEFT_RIGHT), t))
        return out
    def close(self): pass


DISTILLED_TIMESTEPS = [1000, 993, 987, 981, 975, 909, 725, 0.03]       # LTX-Video 0.9.7 / 0.9.8 distilled, 8 steps (diffusers docs)


def wan_flf_class():
    """WanImageToVideoPipeline + an EXPERIMENTAL last-frame condition for Wan2.2 TI2V-5B.
    Diffusers ignores `last_image` for that model (it only replaces the first latent frame). Same trick for the last latent frame:
    the clean latent of the end image is put into the last latent frame and its per-token timestep is set to 0."""
    from diffusers import WanImageToVideoPipeline
    from diffusers.pipelines.wan.pipeline_wan_i2v import retrieve_latents

    class WanFLPipeline(WanImageToVideoPipeline):
        def prepare_latents(self, image, batch_size, num_channels_latents=16, height=480, width=832, num_frames=81, dtype=None,
                            device=None, generator=None, latents=None, last_image=None):
            if last_image is None or not self.config.expand_timesteps:
                return super().prepare_latents(image, batch_size, num_channels_latents, height, width, num_frames, dtype, device,
                                               generator, latents, last_image)
            lat, cond, mask = super().prepare_latents(image, batch_size, num_channels_latents, height, width, num_frames, dtype,
                                                      device, generator, latents, None)
            torch = self._torch
            clip = last_image.unsqueeze(2).repeat(1, 1, 5, 1, 1)       # 5 identical frames = latent frames [first, one 4-frame step]
            clip = clip.to(device=self.vae.device, dtype=self.vae.dtype)
            z = retrieve_latents(self.vae.encode(clip), sample_mode="argmax")[:, :, 1:2]
            mean = torch.tensor(self.vae.config.latents_mean).view(1, self.vae.config.z_dim, 1, 1, 1).to(z.device, z.dtype)
            std = 1.0 / torch.tensor(self.vae.config.latents_std).view(1, self.vae.config.z_dim, 1, 1, 1).to(z.device, z.dtype)
            z = ((z - mean) * std).to(device=cond.device, dtype=cond.dtype)
            cond = cond.clone()
            cond[:, :, -1:] = z.expand(cond.shape[0], -1, -1, -1, -1)
            mask = mask.clone(); mask[:, :, -1] = 0
            return lat, cond, mask

    import torch
    WanFLPipeline._torch = torch
    return WanFLPipeline


class DiffusersBackend:
    """LTX-Video (LTXConditionPipeline, any number of keyframes, optional 4-bit quantization) or Wan 2.2 TI2V (first + experimental last frame)."""
    def __init__(self, cfg, dtype):
        import torch
        self.torch, self.cfg = torch, cfg
        cap = torch.cuda.get_device_capability()[0] if torch.cuda.is_available() else 0
        self.auto = dtype == "auto"
        self.dtype = {"fp16": torch.float16, "bf16": torch.bfloat16, "fp32": torch.float32}.get(dtype) or (torch.bfloat16 if cap >= 8 else torch.float16)
        self.pipe, self.embeds = None, {}
        self.dev = "cuda" if torch.cuda.is_available() else "cpu"
        log(f"backend {cfg['pipeline']} model={cfg['model']} dtype={self.dtype} gpu={torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none'}")

    def _cls(self):
        if self.cfg["pipeline"] == "ltx":
            from diffusers import LTXConditionPipeline
            return LTXConditionPipeline
        return wan_flf_class()

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
        quant = self.cfg.get("quant")
        if self.cfg["pipeline"] == "wan":
            from diffusers import AutoencoderKLWan
            kw["vae"] = AutoencoderKLWan.from_pretrained(self.cfg["model"], subfolder="vae", torch_dtype=torch.float32)
        if quant == "nf4":
            # 13B transformer in 4 bit (~7 GB). Quantized while loading, shard by shard, so CPU RAM stays low.
            from diffusers import BitsAndBytesConfig, LTXVideoTransformer3DModel
            q = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=self.dtype)
            kw["transformer"] = LTXVideoTransformer3DModel.from_pretrained(self.cfg["model"], subfolder="transformer",
                                                                            quantization_config=q, torch_dtype=self.dtype)
            log("transformer loaded in nf4")
        pipe = cls.from_pretrained(self.cfg["model"], **kw)
        if quant:
            pipe.vae.to("cuda")                      # the quantized transformer is already on the GPU
        elif self.cfg.get("offload") or not self.embeds or self.cfg["pipeline"] == "wan":
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

    def generate(self, job, imgs):
        """imgs: [(PIL image, frame index, strength)], the first one is frame 0."""
        torch = self.torch
        if self.pipe is None:
            self._load()
        gen = torch.Generator(device=self.dev).manual_seed(job["seed"])
        emb = self.embeds.get(job["id"])
        kw = dict(width=job["width"], height=job["height"], num_frames=job["frames"], num_inference_steps=job["steps"],
                  guidance_scale=job["guidance"], generator=gen, output_type="pil")
        if emb:
            if self.cfg["pipeline"] == "ltx":
                pe, pm, ne, nm = [None if x is None else x.to(self.dev) for x in emb]
                kw.update(prompt_embeds=pe, prompt_attention_mask=pm, negative_prompt_embeds=ne, negative_prompt_attention_mask=nm)
            else:
                pe, ne = [None if x is None else x.to(self.dev) for x in emb[:2]]
                kw.update(prompt_embeds=pe, negative_prompt_embeds=ne)
        else:
            kw.update(prompt=job["full_prompt"], negative_prompt=job["negative"])
        if self.cfg["pipeline"] == "ltx":
            from diffusers.pipelines.ltx.pipeline_ltx_condition import LTXVideoCondition
            conds = [LTXVideoCondition(image=im, frame_index=ix, strength=st) for im, ix, st in imgs]
            kw.update(conditions=conds, decode_timestep=0.05, decode_noise_scale=0.025, frame_rate=job["gen_fps"])
            if self.cfg.get("distilled"):
                if job["steps"] == BACKENDS_DEFAULT_STEPS and not job.get("timesteps"):
                    kw["timesteps"] = DISTILLED_TIMESTEPS; kw.pop("num_inference_steps")
                elif job.get("timesteps"):
                    kw["timesteps"] = job["timesteps"]; kw.pop("num_inference_steps")
                kw["guidance_rescale"] = 0.7
                kw["image_cond_noise_scale"] = float(job["cond_noise"]) if job.get("cond_noise") is not None else 0.0
            elif job.get("cond_noise") is not None:     # lower = stays closer to the start image (less motion)
                kw["image_cond_noise_scale"] = float(job["cond_noise"])
            try:
                out = self.pipe(**self._filter(self.pipe.__call__, kw))
            except (ValueError, AssertionError) as ex:
                if len(conds) == 1:
                    raise
                log("  keyframe conditioning rejected, retrying with the first and last keyframe only:", str(ex)[:120])
                kw["conditions"] = [conds[0], conds[-1]] if len(conds) > 2 else conds[:1]
                out = self.pipe(**self._filter(self.pipe.__call__, kw))
        else:
            kw["image"] = imgs[0][0]
            if len(imgs) > 1:
                kw["last_image"] = imgs[-1][0]
                if len(imgs) > 2:
                    log("  note: the wan backend uses only the first and last keyframe")
            out = self.pipe(**self._filter(self.pipe.__call__, kw))
        frames = out.frames[0]
        check_not_black(frames)
        return frames

    def close(self):
        self.pipe = None; self._free()


BACKENDS_DEFAULT_STEPS = 8


def make_backend(name, dtype):
    cfg = BACKENDS[name]
    return MockBackend(cfg, dtype) if cfg["pipeline"] == "mock" else DiffusersBackend(cfg, dtype)


# ------------------------------------------------------------------ worker
def out_paths(out_dir, jid):
    d = os.path.join(out_dir, "clips")
    return os.path.join(d, jid + ".mp4"), os.path.join(d, jid + ".json")


class PostQueue:
    """CPU post-processing (Real-ESRGAN anime upscale + RIFE) in a background thread, so the GPU can start the next clip."""
    def __init__(self):
        import queue
        self.q, self.errors = queue.Queue(), []
        self.t = threading.Thread(target=self._run, daemon=True); self.t.start()

    def _run(self):
        while True:
            item = self.q.get()
            if item is None:
                return
            raw, final, j = item
            try:
                import postprocess
                post = j.get("post") or {}
                t0 = time.time()
                postprocess.process(raw, final, fps_in=j["gen_fps"], fps_out=j["fps"], interp=int(post.get("rife", j.get("interp") or 0)),
                                    esrgan=bool(post.get("esrgan")), size=j.get("upscale"), crf=j["crf"], rife_model=post.get("rife_model", "rife-anime"))
                log(f"[{j['id']}] post-processed on CPU in {time.time() - t0:.0f} s -> {final}")
            except Exception as ex:
                traceback.print_exc()
                self.errors.append((j["id"], repr(ex)[:200]))
                shutil.copy(raw, final)          # keep the raw clip rather than losing it

    def add(self, raw, final, j):
        self.q.put((raw, final, j))

    def finish(self):
        self.q.put(None); self.t.join()


def needs_post(j):
    post = j.get("post") or {}
    return bool(post.get("esrgan") or post.get("rife") or j.get("interp"))


def run_worker(args, jobs, shard):
    out = args.out
    os.makedirs(os.path.join(out, "clips"), exist_ok=True)
    os.makedirs(os.path.join(out, "prepped"), exist_ok=True)
    os.makedirs(os.path.join(out, "raw"), exist_ok=True)
    deadline = time.time() + args.max_minutes * 60
    todo = [j for j in jobs if args.force or not os.path.exists(out_paths(out, j["id"])[0])]
    by_backend = {}
    for j in todo:
        by_backend.setdefault(j["backend"], []).append(j)
    if len(by_backend) > 1 and shard[1] > 1:
        names = list(by_backend)                          # several backends and several GPUs: one backend group per GPU (model loads once)
        by_backend = {n: by_backend[n] for n in names[shard[0]::shard[1]]}
        log(f"worker {shard[0] + 1}/{shard[1]}: backends {list(by_backend)}")
    else:
        by_backend = {n: js[shard[0]::shard[1]] for n, js in by_backend.items()}
    log(f"worker {shard[0] + 1}/{shard[1]}: {sum(len(v) for v in by_backend.values())} clips to do")
    post = PostQueue()
    for bname, js in by_backend.items():
        try:
            be = make_backend(bname, args.dtype)
            be.prepare(js)
        except Exception as ex:
            traceback.print_exc()
            for j in js:
                json.dump(dict(id=j["id"], orientation=j["orientation"], backend=bname, status="failed", error="backend setup: " + repr(ex)[:250]), open(out_paths(out, j["id"])[1], "w"), indent=1)
            continue
        for j in js:
            if time.time() > deadline:
                log("time budget reached, stopping cleanly (run again to continue)")
                post.finish()
                return
            mp4, meta = out_paths(out, j["id"])
            t0 = time.time()
            res = dict(id=j["id"], orientation=j["orientation"], backend=bname, seed=j["seed"], frames=j["frames"], size=[j["width"], j["height"]],
                       steps=j["steps"], keyframes=[[c["rel"], c["index"]] for c in j["conds"]], gen_fps=j["gen_fps"])
            try:
                fc = j.get("crop_focus") or (0.5, 0.5)
                mk = lambda jj: [(prep_image(c["path"], jj["width"], jj["height"], j["fit"], j["bg"], fc), c["index"], c["strength"])
                                 for c in (j["conds"] if BACKENDS[bname].get("end_image") else j["conds"][:1])]
                imgs = mk(j)
                imgs[0][0].save(os.path.join(out, "prepped", j["id"] + ".png"))
                log(f"[{j['id']}] {j['frames']} frames {j['width']}x{j['height']} steps={j['steps']} seed={j['seed']} keyframes={[c['index'] for c in j['conds']]}")
                try:
                    frames = be.generate(j, imgs)
                except BlackFrames:
                    if not getattr(be, "auto", False):
                        raise
                    log("  black output with fp16, reloading in bf16 and retrying")
                    be.reload_dtype(be.torch.bfloat16); frames = be.generate(j, imgs)
                except RuntimeError as ex:
                    if "out of memory" not in str(ex).lower():
                        raise
                    log("  out of memory, retrying once at 80% size")
                    be._free()
                    j2 = dict(j); m = BACKENDS[bname]["res_mult"]
                    j2["width"], j2["height"] = [int(round(v * 0.8 / m) * m) for v in (j["width"], j["height"])]
                    frames = be.generate(j2, mk(j2))
                gen_s = round(time.time() - t0, 1)
                if needs_post(j):
                    raw = os.path.join(out, "raw", j["id"] + ".mp4")
                    write_video(frames, raw, j["gen_fps"], None, 12)
                    post.add(raw, mp4, j)
                else:
                    write_video(frames, mp4, j["fps"], j.get("upscale"), j["crf"])
                res.update(status="ok", seconds=gen_s, gpu_seconds=gen_s)
                log(f"[{j['id']}] done in {res['seconds']} s -> {mp4}")
            except Exception as ex:
                traceback.print_exc()
                res.update(status="failed", error=repr(ex)[:300], seconds=round(time.time() - t0, 1))
                try:
                    be._free()
                except Exception:
                    pass
            json.dump(dict(res, prompt=j["full_prompt"], negative=j["negative"], start=j["start"], end=j.get("end"), cropped_from_other_orientation=j.get("crop_fallback", False)), open(meta, "w"), indent=1)
        be.close()
    post.finish()


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
    ap.add_argument("--only", default=None, help="comma separated clip ids (a base id matches all its variants and both orientations; C01_land = landscape only)")
    ap.add_argument("--force", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backend", default=None, choices=sorted(BACKENDS) + ["auto"], help="auto = the backend named in clips.json per clip"); ap.add_argument("--dtype", default="auto", choices=["auto", "fp16", "bf16", "fp32"])
    ap.add_argument("--limit", type=int, default=None, help="run only the first N jobs (smoke test: one variant, one orientation)")
    ap.add_argument("--steps", type=int, default=None); ap.add_argument("--guidance", type=float, default=None)
    ap.add_argument("--width", type=int, default=None); ap.add_argument("--height", type=int, default=None); ap.add_argument("--seconds", type=float, default=None)
    ap.add_argument("--gpus", default="auto", help="auto | 1 | 2 (number of worker processes, one per GPU)")
    ap.add_argument("--max-minutes", type=float, default=600, help="stop starting new clips after this many minutes")
    ap.add_argument("--shard", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.backend == "auto":
        a.backend = None
    jobs = load_jobs(a.input, dict(steps=a.steps, guidance=a.guidance, width=a.width, height=a.height, seconds=a.seconds, backend=a.backend))
    if a.only:
        keep = set(a.only.split(","))
        jobs = [j for j in jobs if j["id"] in keep or j["id"].split("__v")[0] in keep or j["base_id"] in keep]
    if a.limit:
        jobs = jobs[:a.limit]
    if not a.shard:
        crops = sorted({j["stem"] for j in jobs if j.get("crop_fallback")})
        if crops:
            log(f"WARNING: {len(crops)} clip(s) have no start image for their orientation and use a center crop of the other one: {', '.join(crops)}")
    os.makedirs(a.out, exist_ok=True)
    shutil.copy(os.path.join(a.input, "clips.json"), os.path.join(a.out, "clips.json"))
    done = [j for j in jobs if os.path.exists(out_paths(a.out, j["id"])[0])]
    if a.dry_run:
        log(f"{len(jobs)} clips ({len(done)} already done)")
        tot = 0
        for j in jobs:
            est = {"ltx": 6, "ltx13b": 10, "ltx98d": 5, "wan": 30, "fastwan": 8, "mock": 0}[j["backend"]] * (j["steps"] / BACKENDS[j["backend"]]["steps"]) * (j["frames"] / 121) * (j["width"] * j["height"] / (480 * 832))
            tot += 0 if j["id"] in {d["id"] for d in done} else est
            print(f"  {j['id']:<28} {j['backend']:<7} {j['width']}x{j['height']} {j['frames']}f steps={j['steps']} seed={j['seed']} "
                  f"{'DONE' if j in done else '~%.0f min on a T4 (estimate)' % est}"
                  f"{'  [center crop of the other orientation]' if j.get('crop_fallback') else ''}")
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
