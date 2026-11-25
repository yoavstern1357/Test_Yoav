# Free-GPU image-to-video pipeline (Kaggle / Colab)

Turns approved still frames into 4-5 second animated clips with an open model that runs on a **free** Kaggle or Colab GPU.
You upload a small package (`clips.json` + images), press **Run all**, and download a zip of mp4 clips. The local pipeline
(`make_episode.py`) then cuts the clips together with voices, music and captions (section 7).

Files in this folder:
| File | What it is |
|---|---|
| `dumpling_clips.ipynb` | THE notebook. One file, works on Kaggle and on Colab. |
| `generate_clips.py` | The generator the notebook runs (also usable on any other GPU machine). The notebook contains a copy. |
| `pack_inputs.py` | Runs on your computer: builds the upload package (`clips.json` + `images/`) and a zip. |
| `build_notebook.py` | Rebuilds the notebook from `generate_clips.py` (only needed after code edits). |
| `sample/clips.json` | Three test clips using our existing art (`specs/puppets/uncle.png`, `boy.png`, `grandma.png`). |
| `QUICKSTART-he.md` | Short Hebrew guide. |
| `generate_images.py`, `dumpling_images.ipynb`, `build_images_notebook.py`, `nb_common.py` | The "stills" task (section 10): reference-guided images with an open model, replaces Canva image generation. |
| `kaggle_run.py`, `jobs/run.json` | Automated Kaggle run (GitHub Actions). `task` selects clips or images (section 10). |

## 1. Which model, and why
Researched 2026-11-25. Nothing could be run on a GPU while writing this (the build container has none and cannot reach huggingface.co),
so speeds below are **estimates from public numbers, not measurements**. API usage was checked against the diffusers 0.43 source code.
Run the 3-minute smoke test (section 3, step 8) before trusting a long batch.

| Rank | Model | 2D cartoon look | Keeps the start image (character) | Speed per 5 s clip at 480x832 on a T4 (estimate) | Fits a 16 GB T4? | Verdict |
|---|---|---|---|---|---|---|
| **1 (primary)** | **LTX-Video 0.9.5, 2B** (`Lightricks/LTX-Video-0.9.5`, diffusers pipeline `LTXConditionPipeline`) | OK. Soft, sometimes slightly rubbery motion; detail softens at 480p | Best of the free models: the start image is injected directly as the first video frame; an **end image** is supported too | 4-8 min (30 steps); two clips in parallel on Kaggle T4 x2 | Yes: about 4 GB model, prompts are encoded first and the 9 GB text encoder is then released | Default for every clip |
| 2 (fallback) | **Wan 2.2 TI2V-5B** (`Wan-AI/Wan2.2-TI2V-5B-Diffusers`) | Better motion and better handling of animated styles | Good (start image only in this setup) | 20-40 min (offload needed, fp16/bf16 on a T4 is slow) | Only with CPU offload | Use for hero shots where LTX motion is too weak or stiff |
| 3 (Kaggle only, experimental) | LTX-Video 0.9.8 13B distilled (8 steps) | Better than 2B | Good | 8-15 min | Needs about 26 GB CPU RAM (Colab free has 12 GB) and T4 has no fp8 | `--backend ltx13b`, try later |
| not used | Wan 2.1/2.2 14B image-to-video (GGUF Q4) | Best open quality | Good | 60+ min per clip | Marginal | Too slow for a batch |
| not used | CogVideoX-5B-I2V | Fair | Fair | 15-30 min | With offload | Fixed 720x480 landscape, 8 fps, old |
| not used | FramePack (HunyuanVideo based) | Fair | Good | Very slow on T4 | Yes (low VRAM design) | Needs its own repo and is built for fast GPUs |
| not used | LTX-2.x (19B + a 12B text encoder) | Good | Good | Very slow | No (T4 has no fp8) | Too large for free GPUs |
| later, optional | ToonCrafter (two keyframes in, in-betweens out) | Made for cartoons | Good, but only 512x320 landscape, 16 frames | 5-10 min | About 12 GB+ | Possible add-on for "pose A to pose B" shots |
| not used | AnimateDiff | Fair | Weak (not true image-to-video) | fast | Yes | Cannot hold a character |

Cartoon-specific LoRAs exist for some of these models, but none were verified, so the pipeline relies on the style sentence that is
added to every prompt (`defaults.style` in `clips.json`). Honest expectation: the **character stays recognizable in most clips, but about 1 in 3 clips
needs a retry** (hat or belt shape, mustache, extra fingers). That is why `variants` exists (section 5).

## 2. Quotas and time (estimates)
| | Kaggle | Colab free |
|---|---|---|
| GPU | 2x T4 (16 GB each), sometimes P100 | 1x T4 |
| Weekly allowance | about 30 GPU-hours (the account page shows the exact number; it can change) | not published; roughly a few hours a day, can be cut without notice |
| One session | up to 9-12 hours, keeps running in the background with *Save Version* | about 12 hours at most, but disconnects when idle or when the browser closes |
| Needs | phone number verification, Internet = On | Google account |
| RAM / disk | about 29 GB / 20 GB output | about 12 GB / 70 GB |

| Per episode (about 30 clips) | LTX (primary) | Wan (fallback) |
|---|---|---|
| One try per clip | 3-4 h on one T4, 1.5-2 h on Kaggle T4 x2 | 10-20 h |
| With 2 variants per clip (recommended) | 6-8 h on one T4, 3-4 h on T4 x2 | not realistic: use Wan for 5-8 hero shots only |
| Share of the weekly Kaggle allowance | about 10-25% | 30-60% for hero shots |
The first run of every session also downloads the model (about 14 GB for LTX, 10-20 min on Kaggle).

## 3. Step by step on Kaggle (recommended)
1. **Account.** Go to kaggle.com and register with a studio / non-personal email.
2. **Phone verification (needed for GPU and Internet).** Click your profile picture, then *Settings*, then *Phone verification*, and enter the code you receive.
3. **Make the upload package on your computer** (once per batch; a developer or Claude can do it):
   `python3 tools/episode_maker/gpu/pack_inputs.py clips.json` creates `tools/episode_maker/out/gpu_input.zip` (clips.json + images). For a first test use the sample: `python3 tools/episode_maker/gpu/pack_inputs.py tools/episode_maker/gpu/sample/clips.json`.
4. **Upload it as a Dataset.** On Kaggle click *Create* (+), *New Dataset*, drag `gpu_input.zip`, name it `dumpling-input`, keep it **Private**, click *Create*.
5. **Create the notebook.** *Create*, *New Notebook*, then menu *File*, *Import Notebook*, choose `dumpling_clips.ipynb`.
6. **Attach the data.** On the right, *Add Input*, *Your Datasets*, choose `dumpling-input`.
7. **Turn on the GPU and Internet.** Right panel, *Session options*: *Accelerator* = **GPU T4 x2**; *Internet* = **On**.
8. **Smoke test (recommended first).** In the first code cell set `SMOKE_TEST = True`, then *Run All*. About 3 minutes after the model download. A short clip should appear. Set `SMOKE_TEST = False` again.
9. **Real run.** Press *Run All* (stay on the page), or better for long batches: *Save Version*, choose **Save & Run All (Commit)**, and close the browser. The notebook keeps working for up to the session limit.
10. **Download.** When it finishes, open the notebook's *Output* tab (right panel or version page) and download **`dumpling_clips.zip`** (or *Download All*).
11. **More clips later.** Upload a new dataset version and run again. Clips that already exist are skipped (`FORCE = False`).
Stopping is safe: finished clips are kept in `/kaggle/working`; Kaggle does not keep them between separate non-committed sessions, so download or commit before you close.

## 4. Step by step on Colab (backup)
1. colab.research.google.com, *File*, *Upload notebook*, choose `dumpling_clips.ipynb`.
2. *Runtime*, *Change runtime type*, **T4 GPU**, *Save*.
3. *Runtime*, *Run all*. When asked, either upload `gpu_input.zip` (renamed `dumpling_input.zip` is fine; any zip works) or put the unzipped folder in Google Drive as `MyDrive/dumpling_input` and allow Drive access.
4. Keep the tab open. If it disconnects, run again: clips already on the machine are lost unless you uncommented the Drive copy in the last cell, so for long batches use that cell (it saves clips to `MyDrive/dumpling_out`).
5. The last cell downloads `dumpling_clips.zip`.
Colab has one T4 and less RAM, so use LTX only; the notebook already releases the text encoder to fit.

## 5. The input package: `clips.json`
```json
{
  "defaults": {"backend": "ltx", "width": 480, "height": 832, "seconds": 5, "fps": 24, "fit": "cover"},
  "clips": [
    {"id": "c01_burn_gag",
     "start": "images/burn_start.png",
     "end": "images/burn_end.png",
     "prompt": "The big bald uncle in a white kimono with an orange belt bites a steaming dumpling, his eyes go wide, steam shoots from his ears, he hops up and down. Gentle natural motion, the camera stays still.",
     "negative": "optional: replaces the default negative prompt",
     "seconds": 5, "seed": 7, "variants": 3, "cond_noise": 0.1}
  ]
}
```
| Field | Meaning |
|---|---|
| `id` | file name of the result (letters, digits, `_ . -`). With `variants: 3` you get `id__v1`, `__v2`, `__v3` with different seeds, and you pick the best one. |
| `start` | **Required.** The approved still, becomes frame 1. Path is relative to `clips.json`. Use the full 1080x1920 Canva frame. |
| `end` | Optional last frame (LTX only): use for big actions that end in a different pose. |
| `prompt` | **Required.** One paragraph, present tense, one action, describe the look of the characters, say "the camera stays still". A style sentence (soft picture-book cartoon, thick brown outlines) is appended automatically. |
| `negative` | Optional. Default blocks photorealism, morphing, extra limbs, text and scene cuts. |
| `seconds` | 4-5 recommended, 6 maximum on a T4. |
| `seed` | Same seed and prompt give the same clip; change it for a different take. |
| `variants` | Number of takes per clip (default 1, recommended 2 for hard shots). |
| `fit` | `cover` (crop to 9:16, for full frames) or `contain` (pad, for cut-outs on transparent background; `bg` sets the colour). |
| `cond_noise` | LTX only. Lower (0.05) = stays closer to the start image but moves less; higher (0.3) = more motion. Default 0.15. |
| `backend` | Per clip override: `ltx`, `wan`, `ltx13b`. |
| `width`, `height` | Generation size (multiple of 32). 480x832 is the sweet spot; 576x1024 is better looking and about 1.5x slower. Output is upscaled to 720x1280 (`upscale`) with Lanczos. |
Image rules: 9:16, at least 720x1280, character not touching the edges, **no text inside the picture** (the model scrambles it; captions are added later), no more than 2-3 characters. Cut-outs (the files in `specs/puppets`) work only as a technical test.
Before uploading you can check everything without a GPU: `python3 generate_clips.py --input <folder> --out /tmp/x --dry-run` (prints each clip, size, frame count and the time estimate).

## 6. Optional steps
- **Upscale:** built in and cheap: 480x832 to 720x1280 with Lanczos and a light sharpen (`upscale` in `clips.json`, `null` to keep the native size). A neural upscaler (Real-ESRGAN ncnn) can be run later on a computer; the build container verified the same way of running RIFE on CPU (`production/v4/video-tech.md`).
- **Interpolate:** not needed. LTX writes 24 fps natively. If a clip feels floaty, `make_episode.py` can step it "on twos" later, or run RIFE locally (CPU, about 0.4 s per frame).

## 7. Using the clips in an episode
Unzip `dumpling_clips.zip` into a folder next to your spec (default `clips/`), then use a `clip` shot in the episode spec:
```json
{"id": "burn", "clip": "c01_burn_gag__v2.mp4", "trim": [0.4, 4.2], "speed": 1.0,
 "lines": [{"who": "uncle", "text": "Hot hot hot!"}], "punch": [{"t": 1.2, "scale": 1.12}],
 "sfx": [{"t": 1.2, "name": "impact"}], "mood": "adventure"}
```
`clip` (path; looked up in the spec's `clips_dir`, default `clips`, then `frames_dir`, then next to the spec; absolute paths also work),
`trim` `[start, end]` in seconds of the source clip, `speed` (2 = twice as fast, 0.5 = slow motion), `loop` (repeat if the shot is longer than the clip; otherwise the last frame is held),
`clip_audio` (gain, mixes the clip's own sound if it has any; AI clips from this notebook have none). `dur` defaults to the trimmed clip length. Everything else (captions, `punch`, `speedlines`, `impact`, `shake`, `grade`, `particles`, `cards`, `fx`, transitions, `whip`) works on clip shots exactly as on stills, and still shots and clip shots can be mixed freely.
No automatic camera move is applied to a clip (`motion` defaults to `static`); set `motion` / `zoom` for a digital push-in.

## 8. If something goes wrong
| Symptom | Fix |
|---|---|
| "NO GPU FOUND" | Turn on the accelerator (Kaggle right panel / Colab runtime type), restart, run again. |
| Download or install fails | Kaggle: *Internet* must be On (needs phone verification). |
| Clips are black or noisy | Set `DTYPE = "bf16"` (the notebook already retries once in bf16 if the output is black). |
| Out of memory | The script retries once at 80% size. Otherwise lower `width`/`height` (384x672) or `seconds` (4). |
| Character changes shape | Add detail to the prompt (hat, belt colours), lower `cond_noise`, use `variants: 3`, or give an `end` image. |
| Almost no movement | Raise `cond_noise` (0.25), describe the motion more strongly, try `backend: "wan"` for that clip. |
| Wrong model id / API error after a diffusers update | Open an issue for the engineer: model ids are in `BACKENDS` at the top of `generate_clips.py`. |
| Session ended mid-way | Run again, finished clips are skipped (upload the previous zip's clips folder as part of the dataset, or use *Save & Run All* so outputs persist). |

## 9. What has and has not been tested
- Tested here (no GPU): JSON validation, image preparation, frame counts, planning/time estimate, resume, 2-worker split, zip, notebook JSON and code syntax (a mock backend writes a dummy video), and the `clip` shot type in `make_episode.py`.
- Checked against diffusers 0.43 source: pipeline classes, arguments, `encode_prompt` signatures, conditioning objects. Model id `Lightricks/LTX-Video-0.9.5` appears in the diffusers docs; `Wan-AI/Wan2.2-TI2V-5B-Diffusers` was confirmed by search; `Lightricks/LTX-Video-0.9.8-13B-distilled` is **unverified**.
- **Not tested:** any real generation. Expect to fix small things on the first GPU run, which is why the smoke test exists.

## 10. Stills: reference-guided images on the same free GPU (replaces rate-limited Canva generation)
Researched 2026-11-25 (web search + diffusers 0.43 source; nothing could be run on a GPU here, so times are **estimates**).
Goal: new start stills in OUR style with OUR characters, using the approved art as reference images, with a license that allows monetized YouTube.

| Rank | Model | License | Characters from references | T4 16 GB (fp16 only) | Verdict |
|---|---|---|---|---|---|
| **1 (primary)** | **FLUX.2 [klein] 4B** (`black-forest-labs/FLUX.2-klein-4B`, `Flux2KleinPipeline`) | **Apache-2.0** (official card; the 9B is non-commercial) | Native multi-reference editing (up to 4 refs), 4 steps, no CFG | Transformer 8 GB fp16; text encoder (Qwen3-4B, 8 GB) is run first and released. Estimate **1-2 min per 768x1344 image** | Default (`backend: klein`) |
| 2 (fallback) | **Qwen-Image-Edit-2511** (`Qwen/Qwen-Image-Edit-2511`, `QwenImageEditPlusPipeline`) | **Apache-2.0** | Best identity fidelity, up to 3 refs | 20B: needs NF4 (bitsandbytes) for transformer and text encoder + CPU offload; ~60 GB download; bf16 is emulated on a T4. Estimate **15-45 min per image** | Hero stills only (`backend: qwen`), experimental |
| not used | OmniGen2 | Apache-2.0 | Multi-reference, weaker style fidelity | Fits with offload, but needs its own repo/flash-attn, not in diffusers | Third choice, not implemented |
| not used | SDXL + IP-Adapter Plus, Kolors IP-Adapter | OpenRAIL++ / Apache-2.0 adapters | Style and face hint only; mixes two characters, poor for new poses | Fast | Weak consistency |
| rejected | FLUX.2 klein 9B, FLUX.2 dev, FLUX.1 dev, FLUX.1 Kontext dev | **non-commercial** | | | Not allowed for monetized video |
| rejected | PuLID / InstantID (InsightFace) | face-recognition weights are research/non-commercial (from memory, not re-checked) | Real faces only | | Not suitable for cartoons |
Honest expectations: nobody has published T4 timings for klein; fp16 can overflow, so the script encodes prompts in bf16, runs the transformer and falls back to bf16 if the image is black (slower). Multi-reference degrades with many refs: keep to 2-4, give each ref a `role`, and expect about 1 in 3 images to need a re-roll (hence `variants: 2`).

**Security.** Only the two official repos above; only `safetensors` (`use_safetensors=True`, `*.bin/*.pt/*.pkl/*.ckpt` are excluded from the download), no `trust_remote_code`, no third-party quantized re-uploads, no token needed. The exact commit that was used is written to `results.json` (`model_revision`); pass `--revision <hash>` to freeze it. The input dataset is private and contains only our own art.

### Input: `images.json` + `refs/`
```json
{"defaults": {"backend": "klein", "width": 768, "height": 1344, "variants": 2, "ref_max": 704},
 "images": [{"id": "C14", "seed": 1014, "prompt": "...", "negative": "", "keep_characters": true,
             "refs": [{"path": "refs/boy.jpg", "role": "the Boy character reference"},
                      "refs/style.jpg",
                      "@G00_grandma_ref__v1"]}]}
```
`refs`: up to 4 (klein) / 3 (qwen) images, each a path or `{path, role}`. The script writes "image 1 is <role>; image 2 is ..." into the prompt, so scene text may say "the Boy from image 1". `@<id>` uses an image generated earlier in the same job as a reference (these run in a second phase; with variants write `@<id>__v1`), which is how Grandma stays the same in C26 and C27. `negative` is used by qwen; klein has no negative prompt (a non-empty value is appended as "Avoid: ..."). `ref_max` (default 704 px long side) keeps the token count, time and memory down. `keep_characters: false` for style-only refs. `upscale: [1080, 1920]` optionally Lanczos-upscales the output. Check without a GPU: `python3 generate_images.py --input <folder> --out /tmp/x --dry-run`. A mock backend (`--backend mock`) tests the whole batch/resume/phases/zip logic on a CPU.

### Run it (automated)
Put the job in `tools/episode_maker/gpu/jobs/run.json` and push (the workflow does the rest and pushes to branch `gpu-results`):
```json
{"run_id": "ep01v4-stills-001", "task": "images", "input": "tools/episode_maker/gpu/inputs/ep01v4-stills", "backend": "klein", "smoke": false, "only": "", "max_minutes": 120}
```
First run: set `"smoke": true` (one low-resolution image, to see that the model downloads and loads). Results: `images/<id>.png`, `results.json`, `contact_sheet.jpg`. `task` defaults to `clips`, so old job files keep working. If the session has no GPU the notebook stops in step 2 with a clear message and `NO_GPU.txt`, and `kaggle_run.py` exits with code 2. The kernel metadata now sets `machine_shape: NvidiaTeslaT4` next to `enable_gpu` (the Kaggle CLI 2.x field that selects the accelerator); the missing `machine_shape` is the likely cause of the first smoke run having no GPU. Manual use: run `dumpling_images.ipynb` on Kaggle/Colab like the clips notebook (sections 3-4).
Rebuild the notebooks after editing a generator: `python3 build_images_notebook.py` / `python3 build_notebook.py`.

### Episode 1 stills
`inputs/ep01v4-stills/` (about 1.2 MB) makes the 9 missing stills (C10, C14, C16, C17, C20, C26, C27, C28, C29) with 2 variants each, plus `G00_grandma_ref`, a new Grandma character sheet in the same round picture-book style as the Boy and the Uncle (the old painterly cut-out is deliberately NOT used as a reference). Refs: `boy.jpg`, `uncle.jpg` (from `specs/puppets`), `camel.jpg` (from the metro still) and finished stills as style references, all downscaled to <= 1024 px. Expressions are restrained by default; big ones only in C14 (the burn aftermath) and C20 (the proud hero pose). Pick the best variant per still, copy it to `specs/frames/ep01v4/Cxx.png`, then run the clips task.

## 11. Voices: expressive TTS on the same free GPU (task `tts`)
Choice and licenses: `production/v4/voice-tech.md`. Backends: `chatterbox` (default, MIT, voice = a reference clip we synthesize), `turbo` (MIT, `[laugh]` tags), `orpheus` (built-in voices, `<laugh>` tags; check its license text first), `mock` (no GPU, tests the logic). Only official repos, safetensors, `torch.load` forced to `weights_only=True`, no token.

Input `tts.json` + `refs/*.wav` (build it with `python3 make_tts_input.py --spec ../specs/episode-01-v4.json --out inputs/ep01v4-voices`; refs are Kokoro-synthesized, never real people). Each line has `id` (= `tts_engines.line_key(who, text)`, the file name make_episode.py looks for), `who`, `text`, optional `style` (`host tender dreamy tiny solemn excited laugh` = emotion presets for `exaggeration`/`cfg_weight`), optional `text_gpu` (text with `[laugh]` or `<laugh>` tags), per-line `exaggeration`, `cfg_weight`, `temperature`. Voices: `ref`, `exaggeration_scale`, `orpheus_voice`. `variants: 2` writes `<id>.wav` and `<id>__v2.wav`.
Check without a GPU: `python3 generate_tts.py --input inputs/voice-test --out /tmp/x --dry-run` (or `--backend mock` for a full run with tone placeholders).

Job (not triggered by the engineer; first run with `smoke: true`, which renders 2 lines):
```json
{"run_id": "ep01v4-voices-001", "task": "tts", "input": "tools/episode_maker/gpu/inputs/ep01v4-voices", "backend": "chatterbox", "smoke": true, "only": "", "max_minutes": 60}
```
Listening test first: `inputs/voice-test` has the 6 comparison lines. Results: `audio/<id>.wav`, `results.json` (model commit, duration, QC flags), `dumpling_tts.zip` (the workflow deletes zips; download the wavs from the `gpu-results` branch or Kaggle). Copy the WAVs to `tools/episode_maker/tts/gpu/` and render with `"voice_engine": "gpu"`. Rebuild the notebook after editing the generator: `python3 build_tts_notebook.py`.
Not tested: any real generation (see voice-tech.md section 7).

