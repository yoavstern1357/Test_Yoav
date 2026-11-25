#!/usr/bin/env python3
"""Batch reference-guided image generation on a free GPU (Kaggle T4 x2): images.json + reference images -> PNG stills.

    python3 generate_images.py --input /path/to/input --out /path/to/output           # all images, resume
    python3 generate_images.py --input ... --out ... --dry-run                         # validate + plan, no GPU needed
    python3 generate_images.py --input ... --out ... --only C10,C14 --force            # redo some images
    python3 generate_images.py --input ... --out ... --backend qwen                    # slow quality fallback

Why: Canva image generation is rate limited. This makes the start stills for the image-to-video clips with an OPEN-WEIGHT
model that keeps our existing characters consistent by looking at reference images (the approved art).
  klein = FLUX.2 [klein] 4B (black-forest-labs/FLUX.2-klein-4B, Apache-2.0, commercial use OK, multi-reference editing, 4 steps)
  qwen  = Qwen-Image-Edit-2511 in 4-bit NF4 (Qwen/Qwen-Image-Edit-2511, Apache-2.0, multi-reference, very slow on a T4)
Do NOT use FLUX.2 klein 9B or any FLUX dev / Kontext dev model: they are non-commercial.

`input` holds images.json and the reference images it uses (paths relative to images.json):
  {"defaults": {...},   (per image: "keep_characters": false when the refs are style-only and the character is new)
   "images": [{"id": "C10", "prompt": "...", "negative": "", "width": 768, "height": 1344, "seed": 7, "variants": 2,
               "refs": ["refs/uncle.jpg", {"path": "refs/style.jpg", "role": "art style reference"}, "@G00_grandma_ref__v1"]}]}
A ref is a path, or {"path", "role"} (the role is written into the prompt as "image N is <role>"), or "@<id>" = an image
generated earlier in the same job (second phase; with variants use "@<id>__v1").
Orientations: every image is made in BOTH formats by default ("orientations": ["portrait", "landscape"], globally in "defaults" or per
image). Portrait = <id>.png (768x1344), landscape = <id>_land.png (1344x768), same seed and refs, composition sentence adjusted
("Vertical 9:16 composition" / "Wide horizontal 16:9 composition"). Use "orientations": ["portrait"] for e.g. character sheets.
Results: <out>/images/<id>.png (+ <id>.json), <out>/results.json, <out>/contact_sheet.jpg (+ contact_sheet_land.jpg), <out>/dumpling_images.zip.
Safe to stop and start again: finished images are skipped. With 2 GPUs the work is split over both automatically.
Security: only the official model repos below, safetensors only (use_safetensors=True, pickle files are never downloaded),
no trust_remote_code. The resolved model commit hash is written to results.json (pin it with "revision" to freeze a version).
"""
import argparse, json, math, os, re, shutil, subprocess, sys, threading, time, traceback, zipfile

ROOT_DEFAULTS = dict(
    backend="klein", width=768, height=1344, variants=1, ref_max=704, bg="#FFF3DC", orientations=["portrait", "landscape"],
    style=("Soft picture-book 2D animation still in the same painted style, line quality and warm golden light as the style "
           "reference: round friendly shapes, soft brown outlines, bright pastel colors, clean simple shapes, warm light. "
           "Natural, restrained facial expressions unless the scene asks for a big one. "
           "No text, no letters, no captions, no logos."),
    negative=None,          # None = backend default (klein: none, it has no negative prompt; qwen: see QWEN_NEGATIVE)
)
QWEN_NEGATIVE = "blurry, low quality, photorealistic, 3d render, distorted face, extra fingers, deformed hands, changed clothes, text, watermark"
# Only official repos. Folders listed in `files` are the only ones downloaded; *.bin / *.pt / *.pkl are never fetched.
BACKENDS = {
    # PRIMARY: 4B rectified-flow transformer + Qwen3-4B text encoder, step-distilled (4 steps, no CFG), multi-reference editing
    "klein": dict(model="black-forest-labs/FLUX.2-klein-4B", pipeline="klein", steps=4, guidance=1.0, mult=32, max_refs=4,
                  files=["model_index.json", "scheduler/*", "text_encoder/*", "tokenizer/*", "transformer/*", "vae/*"],
                  license="Apache-2.0"),
    # FALLBACK (experimental, slow): 20B edit model, quantized to 4 bit on load (bitsandbytes NF4), model CPU offload
    "qwen": dict(model="Qwen/Qwen-Image-Edit-2511", pipeline="qwen", steps=16, guidance=2.5, mult=16, max_refs=3,
                 files=["model_index.json", "scheduler/*", "text_encoder/*", "tokenizer/*", "processor/*", "transformer/*", "vae/*"],
                 license="Apache-2.0", vae_area=640 * 896),
    # test double: no GPU, writes a gradient image with the first reference pasted in (checks batch/resume/phases/zip logic)
    "mock": dict(model="-", pipeline="mock", steps=1, guidance=1.0, mult=32, max_refs=8, files=[], license="-"),
}
FILE_NAME = re.compile(r"^[A-Za-z0-9_.\-]+$")
NO_GPU_MESSAGE = (
    "NO GPU FOUND (nvidia-smi is missing or lists no device). The session was started without an accelerator.\n"
    "Kaggle: the kernel needs 'enable_gpu': true AND 'machine_shape': 'NvidiaTeslaT4' in kernel-metadata.json (kaggle_run.py sets both), "
    "the account must be phone verified, and the weekly GPU quota must not be used up (kaggle.com/me/account or `kaggle quota`).\n"
    "Colab: Runtime > Change runtime type > T4 GPU.  Stopping now instead of wasting time on a CPU run.")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ------------------------------------------------------------------ job list
def norm_ref(r, i):
    if isinstance(r, str):
        r = {"path": r}
    if not isinstance(r, dict) or not r.get("path"):
        raise ValueError(f"ref #{i + 1} must be a path or {{path, role}}")
    p = r["path"]
    return dict(path=p, role=r.get("role"), dep=p[1:] if p.startswith("@") else None)


ORIENTATIONS = ("portrait", "landscape")
LAND_SUFFIX = "_land"
COMPOSITION = {
    "portrait": "Vertical 9:16 composition, tall framing with the subjects stacked top to bottom.",
    "landscape": ("Wide horizontal 16:9 composition, cinematic widescreen framing with the subjects spread across the width "
                  "and open space on both sides, not a cropped vertical picture."),
}
_VERT = re.compile(r"\bvertical(?:\s+9\s*:\s*16)?(?:\s+(?:composition|frame|framing))?\b[.,]?\s*", re.I)


def orient_text(text, orient):
    """Re-frame a prompt for an orientation. Landscape: 'Vertical composition' style phrases become 'Wide horizontal 16:9 composition.'
    Returns (text, has_composition_phrase). Portrait text is left untouched (old prompts keep working)."""
    if orient == "landscape":
        new, n = _VERT.subn("Wide horizontal 16:9 composition. ", text)
        return new.strip(), n > 0
    return text, bool(_VERT.search(text))


def land_id(i):
    """'C10' -> 'C10_land', 'C10__v2' -> 'C10_land__v2'."""
    base, sep, v = i.partition("__v")
    return base + LAND_SUFFIX + (sep + v if sep else "")


def orient_size(w, h, orient):
    lo, hi = sorted((int(w), int(h)))
    return (lo, hi) if orient == "portrait" else (hi, lo)


def load_jobs(input_dir, overrides):
    path = os.path.join(input_dir, "images.json")
    data = json.load(open(path, encoding="utf-8"))
    items = data["images"] if isinstance(data, dict) else data
    defaults = dict(ROOT_DEFAULTS)
    if isinstance(data, dict):
        defaults.update(data.get("defaults", {}))
    defaults.update({k: v for k, v in overrides.items() if v is not None and k in ("backend", "width", "height")})
    jobs, seen = [], set()
    for i, c in enumerate(items):
        for key in ("id", "prompt"):
            if not c.get(key):
                raise ValueError(f"image #{i + 1}: missing '{key}'")
        if not FILE_NAME.match(c["id"]):
            raise ValueError(f"image id '{c['id']}' may only contain letters, digits, _ . -")
        j = dict(defaults); j.update(c)
        j.update({k: v for k, v in overrides.items() if v is not None and k in ("steps", "guidance", "width", "height", "backend")})
        if j["backend"] not in BACKENDS:
            raise ValueError(f"image {c['id']}: unknown backend {j['backend']}")
        b = BACKENDS[j["backend"]]
        j["steps"] = j.get("steps") or b["steps"]
        j["guidance"] = j.get("guidance") if j.get("guidance") is not None else b["guidance"]
        m = b["mult"]
        j["width"], j["height"] = int(round(j["width"] / m) * m), int(round(j["height"] / m) * m)
        refs = [norm_ref(r, k) for k, r in enumerate(j.get("refs") or [])]
        if len(refs) > b["max_refs"]:
            raise ValueError(f"image {c['id']}: {len(refs)} refs, the {j['backend']} backend supports at most {b['max_refs']}")
        for r in refs:
            if r["dep"] is None:
                r["file"] = os.path.join(input_dir, r["path"])
                if not os.path.exists(r["file"]):
                    raise FileNotFoundError(f"image {c['id']}: reference not found: {r['file']}")
        j["refs"] = refs
        j["phase"] = 2 if any(r["dep"] for r in refs) else 1
        if j["negative"] is None:
            j["negative"] = QWEN_NEGATIVE if j["backend"] == "qwen" else ""
        j["seed"] = int(j.get("seed", 1000 + i))
        orients = j.get("orientations") or ["portrait"]
        if isinstance(orients, str):
            orients = [orients]
        bad = [o for o in orients if o not in ORIENTATIONS]
        if bad:
            raise ValueError(f"image {c['id']}: unknown orientation {bad} (use portrait / landscape)")
        nv = int(j.get("variants", 1))
        for orient in orients:
            for v in range(nv):
                jj = dict(j)
                stem = c["id"] + (LAND_SUFFIX if orient == "landscape" else "")
                jj["orientation"] = orient
                jj["id"] = stem if nv == 1 else f"{stem}__v{v + 1}"
                jj["base_id"] = c["id"]
                jj["stem"] = stem
                jj["seed"] = j["seed"] + v                      # same seed in both orientations
                if orient == "landscape" and j.get("size_landscape"):
                    jj["width"], jj["height"] = [int(round(x / m) * m) for x in j["size_landscape"]]
                else:
                    jj["width"], jj["height"] = orient_size(j["width"], j["height"], orient)
                if orient == "landscape" and j.get("prompt_landscape"):
                    jj["prompt"] = j["prompt_landscape"]
                if jj["id"] in seen:
                    raise ValueError(f"duplicate id {jj['id']}")
                seen.add(jj["id"])
                jj["full_prompt"] = build_prompt(jj)
                jobs.append(jj)
    for j in jobs:
        j["refs"] = [dict(r) for r in j["refs"]]
        for r in j["refs"]:
            if r["dep"] and j["orientation"] == "landscape" and land_id(r["dep"]) in seen:
                r["dep"] = land_id(r["dep"])              # a landscape image uses the landscape version of a generated reference
            if r["dep"] and r["dep"] not in seen:
                raise ValueError(f"image {j['id']}: ref '@{r['dep']}' is not an id in images.json (with variants use '@<id>__v1')")
            if r["dep"] == j["id"]:
                raise ValueError(f"image {j['id']}: refers to itself")
    return jobs


def build_prompt(j):
    """'Reference images: image 1 is ...' + scene + style + composition (+ 'Avoid: ...' for backends without a negative prompt)."""
    orient = j.get("orientation", "portrait")
    parts = []
    if j["refs"]:
        roles = "; ".join(f"image {k + 1} is {r['role'] or 'a reference'}" for k, r in enumerate(j["refs"]))
        keep = (" Create a NEW image; keep every character exactly as in its reference (same face, hat, clothes, colors and proportions)."
                if j.get("keep_characters", True) else "")
        parts.append(f"Reference images: {roles}.{keep}")
    scene, has_a = orient_text(j["prompt"].strip(), orient)
    parts.append(scene)
    if orient == "landscape" and j.get("prompt_extra_landscape"):
        parts.append(j["prompt_extra_landscape"].strip())
    has_b = False
    if j.get("style"):
        st, has_b = orient_text(j["style"].strip(), orient)
        parts.append(st)
    if not (has_a or has_b):
        parts.append(COMPOSITION[orient])
    if j["backend"] == "klein" and j.get("negative"):
        parts.append("Avoid: " + j["negative"].strip())
    return " ".join(p if p.endswith((".", "!", "?")) else p + "." for p in parts)


# ------------------------------------------------------------------ images
def open_rgb(path, bg):
    from PIL import Image
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        col = tuple(int(bg.lstrip("#")[k:k + 2], 16) for k in (0, 2, 4))
        base = Image.new("RGB", im.size, col); base.paste(im, mask=im.split()[-1]); im = base
    return im.convert("RGB")


def prep_ref(path, ref_max, mult, bg):
    """Downscale so the long side is <= ref_max and both sides are multiples of `mult` (fewer tokens = faster, less memory)."""
    from PIL import Image
    im = open_rgb(path, bg)
    s = min(1.0, ref_max / max(im.size))
    w, h = max(mult, int(im.width * s) // mult * mult), max(mult, int(im.height * s) // mult * mult)
    return im.resize((w, h), Image.LANCZOS)


def ref_path(j, r, out_dir):
    return os.path.join(out_dir, "images", r["dep"] + ".png") if r["dep"] else r["file"]


def check_not_black(img):
    import numpy as np
    a = np.asarray(img.convert("RGB"), dtype="float32")
    if not np.isfinite(a).all() or a.mean() < 3.0 or a.std() < 3.0:
        raise BlackImage("output is black or flat (fp16 overflow?)")


class BlackImage(RuntimeError):
    pass


# ------------------------------------------------------------------ backends
def _free(torch):
    import gc
    gc.collect(); torch.cuda.empty_cache()


class MockBackend:
    name = "mock"
    def __init__(self, cfg, dtype): pass
    def prepare(self, jobs): pass
    def generate(self, job, refs):
        from PIL import Image
        w, h, s = job["width"], job["height"], job["seed"] % 200
        im = Image.new("RGB", (w, h), (255 - s // 2, 230 - s // 4, 190 + s // 4))
        if refs:
            r = refs[0].copy(); r.thumbnail((w // 2, h // 2)); im.paste(r, (w // 4, h // 4))
        return im
    def close(self): pass


class KleinBackend:
    """FLUX.2 [klein] 4B via diffusers Flux2KleinPipeline. Prompts are encoded first with ONLY the 4B text encoder loaded, which is
    then released, so the 4B transformer (8 GB in fp16) fits a 16 GB T4 together with the reference tokens. fp16 first (T4 has
    no fast bf16); if the result is black/NaN the transformer is reloaded in bf16 (works on a T4 but slower)."""
    name = "klein"
    def __init__(self, cfg, dtype):
        import torch
        self.torch, self.cfg = torch, cfg
        self.auto = dtype == "auto"
        self.dtype = {"fp16": torch.float16, "bf16": torch.bfloat16}.get(dtype, torch.float16)
        self.pipe, self.embeds, self.offload = None, {}, False
        log(f"backend klein model={cfg['model']} dtype={self.dtype} gpu={torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none'}")

    def prepare(self, jobs):
        torch = self.torch
        from diffusers import Flux2KleinPipeline
        for te_dtype in (torch.bfloat16, torch.float16):      # bf16 is emulated on a T4 but fine for 512 tokens; fp16 is the safety net
            try:
                txt = Flux2KleinPipeline.from_pretrained(self.cfg["model"], transformer=None, vae=None, torch_dtype=te_dtype, use_safetensors=True)
                txt.to("cuda")
                embeds = {}
                for j in jobs:
                    with torch.no_grad():
                        pe, _ = txt.encode_prompt(j["full_prompt"], device="cuda")
                    embeds[j["id"]] = pe.detach().to("cpu", torch.bfloat16)
                del txt; _free(torch)
                self.embeds = embeds
                finite16 = all(torch.isfinite(e.to(torch.float16)).all() for e in embeds.values())
                if not finite16 and self.dtype == torch.float16:
                    log("  text embeddings do not fit fp16, the transformer will run in bf16 (slower)")
                    self.dtype = torch.bfloat16
                log(f"prompts encoded for {len(jobs)} images with the text encoder in {te_dtype} (encoder released)")
                return
            except Exception as ex:
                log(f"  text encoding in {te_dtype} failed: {repr(ex)[:200]}")
                _free(torch)
        raise RuntimeError("could not encode the prompts with the text encoder")

    def _load(self):
        torch = self.torch
        from diffusers import Flux2KleinPipeline, AutoencoderKLFlux2
        vae = AutoencoderKLFlux2.from_pretrained(self.cfg["model"], subfolder="vae", torch_dtype=torch.float32, use_safetensors=True)
        pipe = Flux2KleinPipeline.from_pretrained(self.cfg["model"], text_encoder=None, tokenizer=None, vae=vae,
                                                  torch_dtype=self.dtype, use_safetensors=True)
        if self.offload:
            pipe.enable_model_cpu_offload()
        else:
            pipe.to("cuda")
        try:
            pipe.vae.enable_tiling()
        except Exception:
            pass
        dec = pipe.vae.decode                        # transformer latents are fp16/bf16, the VAE runs in fp32 for safety
        pipe.vae.decode = lambda z, *a, **k: dec(z.to(torch.float32), *a, **k)
        self.pipe = pipe
        log("pipeline loaded", "(cpu offload)" if self.offload else "")

    def reload(self, dtype=None, offload=None):
        self.pipe = None; _free(self.torch)
        if dtype is not None: self.dtype = dtype
        if offload is not None: self.offload = offload

    def generate(self, job, refs):
        torch = self.torch
        if self.pipe is None:
            self._load()
        pe = self.embeds[job["id"]].to("cuda", self.dtype)
        gen = torch.Generator(device="cuda").manual_seed(job["seed"])
        kw = dict(prompt_embeds=pe, height=job["height"], width=job["width"], num_inference_steps=job["steps"],
                  guidance_scale=job["guidance"], generator=gen, output_type="pil")
        if refs:
            kw["image"] = refs
        img = self.pipe(**kw).images[0]
        check_not_black(img)
        return img

    def close(self):
        self.pipe = None; _free(self.torch)


class QwenBackend:
    """Qwen-Image-Edit-2511 (QwenImageEditPlusPipeline), transformer and VLM text encoder quantized to NF4 on load, model CPU offload.
    The prompt is encoded together with the images inside the pipeline, so there is no separate pre-encoding step.
    Needs about 60 GB of disk for the download and ~29 GB CPU RAM while loading; slow on a T4 (compute in bf16 is emulated)."""
    name = "qwen"
    def __init__(self, cfg, dtype):
        import torch
        self.torch, self.cfg = torch, cfg
        self.dtype = {"fp16": torch.float16}.get(dtype, torch.bfloat16)     # Qwen-Image is known to overflow in fp16
        self.pipe = None
        log(f"backend qwen model={cfg['model']} compute dtype={self.dtype}")

    def prepare(self, jobs): pass

    def _load(self):
        torch = self.torch
        import diffusers
        from diffusers import QwenImageEditPlusPipeline, QwenImageTransformer2DModel
        from diffusers import BitsAndBytesConfig as DiffBnB
        from transformers import BitsAndBytesConfig as TfBnB, Qwen2_5_VLForConditionalGeneration
        mod = sys.modules.get("diffusers.pipelines.qwenimage.pipeline_qwenimage_edit_plus")
        if mod is not None and hasattr(mod, "VAE_IMAGE_SIZE"):
            mod.VAE_IMAGE_SIZE = self.cfg["vae_area"]            # default is 1024*1024 per reference: far too many tokens for a T4
        m = self.cfg["model"]
        q = dict(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=self.dtype)
        tr = QwenImageTransformer2DModel.from_pretrained(m, subfolder="transformer", quantization_config=DiffBnB(**q),
                                                         torch_dtype=self.dtype, use_safetensors=True)
        te = Qwen2_5_VLForConditionalGeneration.from_pretrained(m, subfolder="text_encoder", quantization_config=TfBnB(**q),
                                                                torch_dtype=self.dtype, use_safetensors=True)
        pipe = QwenImageEditPlusPipeline.from_pretrained(m, transformer=tr, text_encoder=te, torch_dtype=self.dtype, use_safetensors=True)
        pipe.enable_model_cpu_offload()
        try:
            pipe.vae.enable_tiling()
        except Exception:
            pass
        self.pipe = pipe
        log("pipeline loaded (nf4 + cpu offload)")

    def reload(self, dtype=None, offload=None):
        self.pipe = None; _free(self.torch)

    def generate(self, job, refs):
        torch = self.torch
        if self.pipe is None:
            self._load()
        gen = torch.Generator(device="cuda").manual_seed(job["seed"])
        cfg = float(job["guidance"])
        kw = dict(image=refs or None, prompt=job["full_prompt"], height=job["height"], width=job["width"],
                  num_inference_steps=job["steps"], generator=gen, output_type="pil")
        if cfg > 1.0:
            kw.update(true_cfg_scale=cfg, negative_prompt=job["negative"] or " ")
        else:
            kw.update(true_cfg_scale=1.0)
        img = self.pipe(**kw).images[0]
        check_not_black(img)
        return img

    def close(self):
        self.pipe = None; _free(self.torch)


def make_backend(name, dtype):
    cfg = BACKENDS[name]
    return {"mock": MockBackend, "klein": KleinBackend, "qwen": QwenBackend}[cfg["pipeline"]](cfg, dtype)


# ------------------------------------------------------------------ worker
def out_paths(out_dir, jid):
    d = os.path.join(out_dir, "images")
    return os.path.join(d, jid + ".png"), os.path.join(d, jid + ".json")


def run_worker(args, jobs, shard, phase):
    out = args.out
    os.makedirs(os.path.join(out, "images"), exist_ok=True)
    deadline = time.time() + args.max_minutes * 60
    todo = [j for j in jobs if (phase is None or j["phase"] == phase) and (args.force or not os.path.exists(out_paths(out, j["id"])[0]))]
    todo.sort(key=lambda j: j["phase"])
    todo = todo[shard[0]::shard[1]]
    log(f"worker {shard[0] + 1}/{shard[1]} phase {phase or 'all'}: {len(todo)} images to do")
    by_backend = {}
    for j in todo:
        by_backend.setdefault(j["backend"], []).append(j)
    for bname, js in by_backend.items():
        be = make_backend(bname, args.dtype)
        be.prepare(js)
        for j in js:
            if time.time() > deadline:
                log("time budget reached, stopping cleanly (run again to continue)")
                be.close()
                return
            png, meta = out_paths(out, j["id"])
            t0 = time.time()
            res = dict(id=j["id"], orientation=j["orientation"], backend=bname, seed=j["seed"], size=[j["width"], j["height"]], steps=j["steps"])
            try:
                mult = BACKENDS[bname]["mult"]
                refs = []
                for r in j["refs"]:
                    p = ref_path(j, r, out)
                    if not os.path.exists(p):
                        raise FileNotFoundError(f"reference missing (generated in an earlier phase?): {p}")
                    refs.append(prep_ref(p, j["ref_max"], mult, j["bg"]))
                log(f"[{j['id']}] {j['width']}x{j['height']} steps={j['steps']} seed={j['seed']} refs={[im.size for im in refs]}")
                try:
                    img = be.generate(j, refs)
                except BlackImage:
                    if bname != "klein" or not getattr(be, "auto", False) or be.dtype == be.torch.bfloat16:
                        raise
                    log("  black output with fp16, reloading the transformer in bf16 and retrying")
                    be.reload(dtype=be.torch.bfloat16); img = be.generate(j, refs)
                except RuntimeError as ex:
                    if "out of memory" not in str(ex).lower():
                        raise
                    log("  out of memory: retrying with CPU offload and smaller references")
                    be.reload(offload=True)
                    refs = [prep_ref(ref_path(j, r, out), int(j["ref_max"] * 0.75), mult, j["bg"]) for r in j["refs"]]
                    img = be.generate(j, refs)
                if j.get("upscale"):
                    from PIL import Image
                    img = img.resize(tuple(orient_size(*j["upscale"], j["orientation"])), Image.LANCZOS)
                img.save(png + ".part", format="PNG", optimize=True); os.replace(png + ".part", png)
                res.update(status="ok", seconds=round(time.time() - t0, 1))
                log(f"[{j['id']}] done in {res['seconds']} s -> {png}")
            except Exception as ex:
                traceback.print_exc()
                res.update(status="failed", error=repr(ex)[:300], seconds=round(time.time() - t0, 1))
                try:
                    be.reload()
                except Exception:
                    pass
            json.dump(dict(res, prompt=j["full_prompt"], negative=j["negative"], refs=[r["path"] for r in j["refs"]]), open(meta, "w"), indent=1)
        be.close()


# ------------------------------------------------------------------ main / multi-GPU / zip
def gpu_count():
    try:
        r = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=20)
        return len([l for l in r.stdout.splitlines() if l.startswith("GPU")])
    except Exception:
        return 0


def fetch_model(bname, revision):
    """Download the official repo once (before the GPU workers start). Returns the commit hash that was used."""
    cfg = BACKENDS[bname]
    if cfg["pipeline"] == "mock":
        return None
    from huggingface_hub import snapshot_download
    log(f"downloading {cfg['model']} (safetensors only){' @ ' + revision if revision else ''} ...")
    p = snapshot_download(cfg["model"], revision=revision, allow_patterns=cfg["files"],
                          ignore_patterns=["*.bin", "*.pt", "*.pth", "*.pkl", "*.pickle", "*.ckpt", "*.onnx", "*.msgpack", "*.h5"])
    rev = os.path.basename(p.rstrip("/"))
    log(f"model ready, commit {rev}")
    return rev


def make_zip(out):
    zp = os.path.join(out, "dumpling_images.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        d = os.path.join(out, "images")
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            z.write(os.path.join(d, f), "images/" + f)
        for f in ("results.json", "images.json", "contact_sheet.jpg", "contact_sheet_land.jpg"):
            if os.path.exists(os.path.join(out, f)):
                z.write(os.path.join(out, f), f)
    return zp


def contact_sheet(out, jobs):
    """contact_sheet.jpg (portrait images) and contact_sheet_land.jpg (landscape images), small JPEGs."""
    from PIL import Image, ImageDraw
    for orient, name, cols, cell in (("portrait", "contact_sheet.jpg", 5, (216, 384)), ("landscape", "contact_sheet_land.jpg", 4, (384, 216))):
        done = [j for j in jobs if j.get("orientation", "portrait") == orient and os.path.exists(out_paths(out, j["id"])[0])]
        if not done:
            continue
        rows = math.ceil(len(done) / cols)
        sheet = Image.new("RGB", (cols * cell[0], rows * (cell[1] + 16)), "white")
        d = ImageDraw.Draw(sheet)
        for i, j in enumerate(done):
            im = Image.open(out_paths(out, j["id"])[0]).convert("RGB"); im.thumbnail(cell)
            x, y = (i % cols) * cell[0], (i // cols) * (cell[1] + 16)
            sheet.paste(im, (x, y + 16)); d.text((x + 3, y + 2), j["id"], fill="black")
        sheet.save(os.path.join(out, name), quality=80)


def collect_results(out, jobs, revision):
    rows = []
    for j in jobs:
        png, meta = out_paths(out, j["id"])
        if os.path.exists(meta):
            rows.append(json.load(open(meta)))
        elif os.path.exists(png):
            rows.append(dict(id=j["id"], status="ok"))
        else:
            rows.append(dict(id=j["id"], status="missing"))
    json.dump(dict(model_revision=revision, results=rows), open(os.path.join(out, "results.json"), "w"), indent=1)
    return rows


def estimate_minutes(j, out):
    """Very rough T4 estimate from token counts (NOT measured): effective 12 TFLOPS fp16 (klein), 4 TFLOPS emulated bf16 (qwen)."""
    from PIL import Image
    b = BACKENDS[j["backend"]]
    toks = j["width"] * j["height"] / 256
    for r in j["refs"]:
        try:
            w, h = Image.open(ref_path(j, r, out)).size if (not r["dep"]) else (j["width"], j["height"])
        except Exception:
            w, h = j["width"], j["height"]
        s = min(1.0, j["ref_max"] / max(w, h))
        toks += (w * s) * (h * s) / 256
    if b["pipeline"] == "klein":
        step = (2 * 4e9 * toks + 4 * toks * toks * 3072 * 25) / 12e12
        return (j["steps"] * step + 15) / 60
    if b["pipeline"] == "qwen":
        step = (2 * 20e9 * toks + 4 * toks * toks * 3072 * 60) / 4e12 * (2 if float(j["guidance"]) > 1 else 1)
        return (j["steps"] * step + 120) / 60
    return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--only", default=None, help="comma separated image ids (a base id matches all its variants and both orientations; C10_land = landscape only)")
    ap.add_argument("--force", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backend", default=None, choices=sorted(BACKENDS)); ap.add_argument("--dtype", default="auto", choices=["auto", "fp16", "bf16"])
    ap.add_argument("--limit", type=int, default=None, help="run only the first N jobs (smoke test: one variant, one orientation)")
    ap.add_argument("--steps", type=int, default=None); ap.add_argument("--guidance", type=float, default=None)
    ap.add_argument("--width", type=int, default=None); ap.add_argument("--height", type=int, default=None)
    ap.add_argument("--gpus", default="auto", help="auto | 1 | 2 (number of worker processes, one per GPU)")
    ap.add_argument("--max-minutes", type=float, default=600, help="stop starting new images after this many minutes")
    ap.add_argument("--revision", default=None, help="model commit hash to pin (default: latest main; the used hash is logged)")
    ap.add_argument("--shard", default=None, help=argparse.SUPPRESS); ap.add_argument("--phase", type=int, default=None, help=argparse.SUPPRESS)
    a = ap.parse_args()
    all_jobs = load_jobs(a.input, dict(steps=a.steps, guidance=a.guidance, width=a.width, height=a.height, backend=a.backend))
    jobs = all_jobs
    if a.only:
        keep = set(a.only.split(","))
        jobs = [j for j in jobs if j["id"] in keep or j["base_id"] in keep or j["stem"] in keep]
    if a.limit:
        jobs = jobs[:a.limit]
    os.makedirs(a.out, exist_ok=True)
    shutil.copy(os.path.join(a.input, "images.json"), os.path.join(a.out, "images.json"))
    done_ids = {j["id"] for j in jobs if os.path.exists(out_paths(a.out, j["id"])[0])}
    if a.dry_run:
        log(f"{len(jobs)} images ({len(done_ids)} already done)")
        tot = 0.0
        for j in jobs:
            est = estimate_minutes(j, a.out)
            tot += 0 if j["id"] in done_ids else est
            print(f"  {j['id']:<28} {j['backend']:<6} {j['width']}x{j['height']} steps={j['steps']} seed={j['seed']} phase={j['phase']} "
                  f"refs={len(j['refs'])} {'DONE' if j['id'] in done_ids else '~%.1f min on a T4 (estimate)' % est}")
            print(f"      {j['full_prompt'][:170]}")
            words = len(j["full_prompt"].split())
            if words > 330:
                print(f"      WARNING: prompt has {words} words, long prompts are truncated at 512 tokens")
        log(f"estimated GPU time: {tot:.0f} min on one T4 (about half with 2 GPUs) plus the model download. Estimates are not measured.")
        return
    if a.shard:
        i, n = [int(x) for x in a.shard.split("/")]
        run_worker(a, jobs, (i, n), a.phase)
        return
    uses_gpu = [b for b in {j["backend"] for j in jobs} if BACKENDS[b]["pipeline"] != "mock"]
    if uses_gpu and gpu_count() == 0:
        sys.exit(NO_GPU_MESSAGE)                      # fail fast: never start a long CPU run
    revision = None
    for b in uses_gpu:
        revision = fetch_model(b, a.revision)
    n = {"auto": max(1, gpu_count()), "1": 1, "2": 2}[a.gpus]
    if not uses_gpu:
        n = min(n, 2)
    phases = sorted({j["phase"] for j in jobs})
    if n == 1:
        run_worker(a, jobs, (0, 1), None)
    else:
        passthrough, skip = [], False
        for x in sys.argv[1:]:
            if skip:
                skip = False
            elif x == "--gpus":
                skip = True
            elif not x.startswith("--gpus="):
                passthrough.append(x)
        for ph in phases:                                 # phase 2 = images that use phase-1 results as references
            log(f"{n} GPUs: phase {ph}, starting {n} workers")
            procs = []
            for i in range(n):
                env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(i), PYTHONUNBUFFERED="1")
                cmd = [sys.executable, os.path.abspath(__file__)] + passthrough + ["--shard", f"{i}/{n}", "--phase", str(ph)]
                p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                procs.append(p)
                threading.Thread(target=lambda p=p, i=i: [print(f"[gpu{i}] {l}", end="", flush=True) for l in p.stdout], daemon=True).start()
            for p in procs:
                p.wait()
            time.sleep(0.5)
    rows = collect_results(a.out, all_jobs, revision)
    try:
        contact_sheet(a.out, all_jobs)
    except Exception as ex:
        log("contact sheet failed:", repr(ex)[:120])
    zp = make_zip(a.out)
    ok = sum(r["status"] == "ok" for r in rows)
    log(f"finished: {ok}/{len(rows)} images ok. ZIP: {zp} ({os.path.getsize(zp) / 1e6:.1f} MB)")
    for r in rows:
        if r["status"] != "ok":
            log("  not done:", r["id"], r.get("status"), r.get("error", ""))
    if ok == 0 and rows:
        sys.exit(1)


if __name__ == "__main__":
    main()
