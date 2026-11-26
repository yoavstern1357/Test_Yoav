# Motion tech: AI video clips on the free Kaggle T4 x2 (v4.4, measured 2026-11-25)

## HOW TO USE (for the producer / integrator)
**Use backend `ltx98d` for every clip.** It is LTX-Video 0.9.8 13B distilled (4-bit), 8 steps, no CFG. Measured on Kaggle T4: 71-85 s for a 4 s 480x832 clip at 24 fps and about 40 s when generated at 12 fps and interpolated. It beats the old `ltx` (0.9.5 2B, 105 s) in motion, expressions and stability.

Job file (`tools/episode_maker/gpu/jobs/run.json`), same format as before; only the backend changes:
```json
{"run_id": "ep01v44-clips-001", "task": "clips", "input": "tools/episode_maker/gpu/inputs/<folder>", "backend": "ltx98d", "smoke": false, "only": "", "max_minutes": 150}
```
`"backend": "auto"` means "use the `backend` written on each clip in clips.json" (to compare models in one job; with several backends the 2 GPUs split them).

Recommended `clips.json` defaults (portrait first, see GPU BUDGET RULES in the bible):
```json
"defaults": {"backend": "ltx98d", "orientations": ["portrait"], "seconds": 3, "fps": 24, "gen_fps": 12,
             "width": 480, "height": 832, "upscale": [720, 1280], "motion": "medium", "crf": 14,
             "post": {"rife": 2, "esrgan": true},
             "style": "soft watercolor anime, delicate gentle line art, warm muted palette, consistent character design, smooth natural animation"}
```
Per-clip fields (all optional except `id`, `prompt` and a start image):
| field | meaning |
|---|---|
| `start` / `end` | as before (`end` = last frame). |
| `keyframes` | `[{"image": "images/a.jpg", "t": 0}, {"image": "images/b.jpg", "t": 1.2, "strength": 1.0}, {"image": "images/c.jpg", "t": "end"}]`: any number of still keyframes at times in seconds (rounded to 8-frame steps). Portrait/landscape stills are picked by the same `_land` rule as `start`. Replaces `start`/`end`. |
| `motion` | `"low"` / `"medium"` (default recommendation) / `"high"` or a number 0-1. Sets `cond_noise` (how far the video may drift from the start still: 0.02 / 0.12 / 0.30) and, for high, adds "lively, continuous, expressive full-body motion" to the prompt. |
| `gen_fps` + `post` | `gen_fps: 12` generates half the frames (half the GPU time); `post: {"rife": 2}` interpolates back to 24 fps on the CPU (background thread, RIFE v4.6); `post: {"esrgan": true}` upscales with Real-ESRGAN anime (on the GPU when present, tiny cost) to `upscale`. The raw clip stays in `dumpling_out/raw/`. |
| `steps`, `timesteps` | default 8 steps (the official distilled schedule). `"steps": 4, "timesteps": [1000, 975, 725, 0.03]` also works (47 s instead of 71-85 s, similar look): good for calm/establishing shots. |
| `seconds` | 2-3 s is the sweet spot (most of the acting happens in the first 2 s; 4 s clips tend to freeze or drift at the end). Cut clips together instead of making long ones. |
| `variants` | keep 1; make a 2nd only after a failed QC. |

**Prompt recipe** (the distilled model has no negative prompt, so say what you want in the prompt):
1. First sentence: the camera. "The camera stays completely still, fixed framing, no zoom." (without it the 13B zooms in and smears faces; with it the framing is stable). For chases/tracking say "the camera tracks them".
2. Then the acting as a sequence with facial beats: "eyes pop wide open, eyebrows shoot up, jaw drops, then a huge delighted grin; he waves the chopsticks; the boy giggles and looks up at him".
3. Name each character the same way as in the still ("the big fat bald uncle with the thin mustache", "the small boy in the conical leaf hat").
4. Keep one main action per 2-3 s clip. Big pose change = use `keyframes` (start still + end still), see below.

**Keyframes**: LTX 0.9.8d handles start + end stills cleanly (squash, jump, steam, end pose reached by about 1.8 s of a 4 s clip, then it holds). Use 2-2.5 s clips for such gags. The old 0.9.5 melts into a smear between two different poses: never use it for keyframes. Stills for keyframes must show the same characters/setting (the uncle gag pair C14 -> C14_end worked well).

Run time per job: the first clip of each GPU pays about 7-8 min start-up (26 GB model download + prompt encoding). Put at least 40 clips in one job. Check results with `ffmpeg` contact sheets, as done for this report.

## Result in one paragraph
Compared on the locked Uncle (intro-v3 variant 2) and the ep01 stills: LTX 0.9.5 (current) ghosts, melts the boy and barely moves food; **LTX 0.9.8 13B distilled nf4 is faster (71 s vs 105 s per clip), keeps the characters, adds real acting (grin, raised chopsticks, running, dripping soup) and handles start+end keyframes**; FastWan2.2 5B has the most exuberant faces but re-renders the scene (palette and character design drift, the Uncle's design is lost), needs 80% resolution after an out-of-memory error and takes about 300 s per clip; the full Wan2.2 5B did not complete (see below). Recommendation: `ltx98d` + 12 fps + RIFE + Real-ESRGAN anime. The side-by-side video is `tools/episode_maker/out/motion-compare.mp4` (git-ignored, 1440x984, 24 s, six segments; rebuild with `python3 tools/episode_maker/gpu/build_motion_compare.py <results dirs> out.mp4` from `gpu-results/motion-compare-001` and `-002`).

## Measurements (Kaggle T4, portrait 480x832, 97 frames = 4 s unless noted)
Runs: `motion-compare-001` (16 clips, 2 GPUs) and `motion-compare-002` (8 clips, 2 GPUs). Times are GPU seconds per clip after the model is loaded; the first clip of a session adds about 2 min of model loading on top of the 7 min start-up.

| Option | GPU time per clip | Look / motion | Verdict |
|---|---|---|---|
| `ltx` 0.9.5 2B, 30 steps, CFG | 105-123 s | soft, ghosting, the boy dissolves in the uncle shot, chase melts at the end, food macro almost static; start+end keyframes produce a smear | replaced |
| **`ltx98d` 8 steps, 24 fps** | **71-85 s** | stable characters, clear acting, soup drips and wobbles; without a camera sentence it zooms in and the uncle's face smears | **default** |
| `ltx98d` + "camera stays still", motion medium | 85 s | stable framing, chopsticks raised, grin, eyebrows; moderate amount of motion | **use this prompt** |
| `ltx98d` motion high | about 85 s | adds a bigger gesture (arm raised), still stable | for gags |
| `ltx98d` 4 steps (`timesteps` 4 values) | 47 s | very similar to 8 steps | calm shots, saves 40% |
| **`ltx98d` gen_fps 12 + RIFE x2** | **38-45 s** (+ CPU 64 s for RIFE in the background) | most readable "on twos" acting (open-mouth reaction, giggle); RIFE v4.6 shows no ghosting on these shots | **default for the series** |
| `ltx98d` 12 fps + Real-ESRGAN anime + RIFE, 720x1280 | 42 s GPU (+ 240 s CPU/GPU in a background thread) | cleaner lines and flat colors, loses a little paper grain | default final look |
| `ltx98d` at 576x1024 | 135 s | more detail but a smear at the end of the chase; not worth +60% | no |
| `ltx98d` end keyframe at 2.8 s instead of 4 s | 86 s | pose reached early, a zoom glitch in between | keep end at the clip end, use short clips |
| `fastwan` (FastWan2.2-TI2V-5B, 3 steps) | 300-390 s | most expressive faces, but re-renders the scene (different room, red sash, Uncle's design not preserved); only frame 1 matches the still | no |
| `wan` Wan2.2 TI2V-5B, 16 steps | not completed | one worker was killed (CPU RAM: both workers loaded the 11 GB text encoder at the same time); the other model ran out of GPU memory at 480x832x97 and needed a retry at 384x672. Extrapolating from FastWan (about 85 s per step) a 16-step clip would take 20+ min | rejected on budget |
| `wan` with last frame (`WanFLPipeline`) | not run on real weights | diffusers conditions only the first frame of Wan2.2 5B; the added last-frame trick is validated only on a tiny random model | experimental |

CPU stages (measured): RIFE v4.6 (ncnn, CPU) 0.3 s per output frame at 480x832 on a 4-core container (0.65 s on Kaggle); at 720x1280 about 1.5 s. Real-ESRGAN `realesr-animevideov3`: 8 s per 480x832 frame on a 4-core CPU, well under 1 s on the T4, so the notebook runs it on the GPU inside the same session.

## What this means for the GPU budget (30 h/week)
- One 35-clip episode in portrait at 12 fps + RIFE: 35 x about 40 s = 23 GPU-min split over 2 GPUs (about 12 min wall) + about 8 min start-up, so roughly 20-25 min of Kaggle session time. Landscape adds the same again, and only where the portrait composition cannot be re-framed.
- Old plan (0.9.5, 30 steps, both orientations, 2 variants): 35 x 105 s x 4 = 4 h. New plan: about 0.4 h. This leaves most of the week for stills, voices, music and retries.
- Keep each job large (40+ clips) because of the 7-8 min start-up per session, and log every job in `production/v4/gpu-ledger.md`.
- Ledger entries for these R&D runs: motion-compare-001 about 70 GPU-min of both T4s (35 min session), motion-compare-002 about 35 (17 min session).

## Licenses (commercial use) and VRAM fit
Checked with web search only (huggingface.co is not reachable from the build container); confirm the license text on the model pages before a first monetized upload.
| Model | License | Commercial use | VRAM on T4 |
|---|---|---|---|
| LTX-Video 0.9.5 / 0.9.8 13B distilled (Lightricks) | LTX-Video Open Weights License; code Apache-2.0 | Free for organizations under US$10M annual revenue (their FAQ); this channel qualifies. Re-check if revenue ever approaches the limit | 0.9.5 about 5 GB; 13B distilled in nf4 about 7 GB + activations, fits one T4 with the text encoder released |
| Wan2.1 / Wan2.2 (Alibaba), FastWan (FastVideo) | Apache-2.0 | yes | 5B needs offload and still ran out of memory at 480x832x97 |
| RIFE (rife-ncnn-vulkan, hzwer) | MIT | yes | CPU |
| Real-ESRGAN `realesr-animevideov3` | BSD-3-Clause | yes | about 0.2 GB |
| FramePack / HunyuanVideo | Tencent Hunyuan Community License excludes the EU, UK and South Korea and caps very large services | no (audience is global) | not tested |
| LTX-2.x (19B+) | LTX-2.x community license | possible, but too big for a T4 and no fp8 on T4 | no |
| ToonCrafter, anime LoRAs for LTX/Wan | not verified | unknown | not tested; no anime LoRA with a verified commercial license was found, the style sentence in `defaults.style` is used instead |
| FILM interpolation | Apache-2.0 | yes | not tested; RIFE is enough |

## Known problems and next steps
- 13B nf4 drifts a little over 4 s (hat, face detail); keep clips at 2-3 s and re-run seed+1 when QC fails.
- Faces can smear when the model zooms in: always include the fixed-camera sentence unless a camera move is wanted.
- Start-up cost: model download is not cached between Kaggle sessions; batch large.
- Not tested: Wan 2.1 FLF2V 14B (GGUF Q4 needs about 10 GB plus offload; expected 20+ min per clip, rejected on budget), LTX 0.9.8 latent upsampler (second pass 2x; could replace Real-ESRGAN but costs GPU time), keyframes with 3+ stills (code path validated on a tiny model and in the mock backend only; two-keyframe path validated on real weights).
- Two workers loading the same big model at the same time worked for ltx98d (shard-wise 4-bit loading); two Wan workers did not (RAM). Run Wan with `--gpus 1` if it is ever needed.

## KNOWN BUG (found 2026-11-26 in ep01v44-clips-001)
The RIFE x2 pass in postprocess.py writes every interpolated (even-numbered) frame corrupted (horizontal stripes). Until fixed, set "post": {"rife": 0} (or drop interpolated frames on install: `select='not(mod(n\,2))',setpts=N/12/TB,fps=24`, which gives clean anime-style "on twos" motion; this is what Episode 1 v4.4 uses).
