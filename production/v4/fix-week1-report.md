# Fix plan, Week 1: pipeline engineer report (2026-11-26)

Scope: tasks A-D of `fix-plan.md` Week 1 for the pipeline. Mid-task the creator decided on a PROFESSIONAL CHARACTER REDESIGN, so the character model sheets (A) and the GPU smoke tests on old-design stills (D) were stopped; B and C (design-independent) were finished, and LatentSync was checked on CPU only.

## Summary
| Task | Result | GPU |
|---|---|---|
| A. Character model sheets | One klein job had already been pushed before the stop (`charsheets-v45-001`, 42 images, all OK). Results kept on `gpu-results/charsheets-v45-001/` as **reference only, not adopted** (old designs); nothing saved to `specs/refs/`. Lessons below feed the redesign sheets. | about 28 GPU-min (2 x 14 min session) |
| B. Stills gate `qc_stills.py` | Built and tested on the 127 v4.4 keyframe stills: duplicates/extra people caught with precision 0.81 / recall 0.62 (FAIL flag), 0.68 / 0.76 with the new costume-identity warning. | 0 |
| C. Mouth animation | Rhubarb Lip Sync 1.14.0 (MIT) installed and verified on a Qwen3-TTS line; tracker `mouth_track.py` and compositor `mouth_overlay.py` built; 5 s demo rendered and checked frame by frame: works on a calm close-up. Sprite spec written. | 0 |
| D. Smoke tests | Cancelled (creator decision). LatentSync checked on CPU: license, dependencies, and an InsightFace-free YuNet adapter whose face alignment was verified on our clips. Not run on a GPU. | 0 |
| **Total GPU this week (this agent)** | | **about 28 min** (logged in `gpu-ledger.md`) |

## A. Model sheets (stopped; lessons for the redesign)
Input: `tools/episode_maker/gpu/inputs/charsheets-v45/` (builder `gpu/make_charsheets_v45_input.py`): 12 items x 2-4 variants, 1536x864, each with 2 reference crops that contain only that one character (Boy from intro-v3 `I1_bite__v2` + `boy_only.jpg` with the Uncle cut off; Uncle from the locked intro-v3 `I1_bite__v2` / `I6_chomp__v2`; Grandma from v4.4 `C12` + `grandma_ref.jpg`). Results: `gpu-results/charsheets-v45-001/dumpling_out/` (`contact_sheet_land.jpg`). Measured: 14 min session on T4 x2 for 42 images at 1536x864 (about 38 s per image per GPU, model load included).
What we learned (reuse for the redesign sheets):
- **Turnarounds work**: single-character crops as refs + "Exactly ONE character on the whole sheet" gave clean front / 3/4 / side / back rows on cream for all three characters, 12 of 12, no second person. This is the recipe for the new sheets.
- **Expression grids drift**: the Uncle got a hat in all 4 expression variants (the model "completes" a costume); the Boy and Grandma grids were consistent. Expression sheets need the approved turnaround as a reference and a "no hat" style negative line per character.
- **Hand sheets** mix in full figures in about half the variants: generate hands with a hands-only crop as reference, or 1-2 hand poses per image.
- **Mouth charts fail as grids** (full bodies, changing jackets). Generate one mouth shape per image as an edit of the approved face close-up (see `mouth-sprite-spec.md`).

## B. Stills gate: `tools/episode_maker/qc_stills.py`
```
python3 tools/episode_maker/qc_stills.py --fetch-models     # YuNet + PP-OCR (as qc_clips) + YOLOX-s (Apache-2.0, 36 MB), git-ignored
cd tools/episode_maker && python3 qc_stills.py specs/frames/ep01v44 --script ../../scripts/episode-01-v4.4.md \
   --gt specs/qc/ep01v44_stills_gt.json --md out/qc_stills.md --json out/qc_stills.json --sheet out/qc_stills.png
```
- Detectors (all CPU, OpenCV dnn, no PyTorch): **YuNet at 4 scales** (the key finding: on our anime faces YuNet scores 0.85-0.9 when the face is downscaled to about 100 px, but only 0.35-0.55 at full size; the v4.4 QC ran it at full size only), **YOLOX-s COCO person class** (Apache-2.0, opencv_zoo) for bodies, backs and profiles, PP-OCRv3 for text, Laplacian sharpness relative to the folder median, and a **costume-colour identity check** (torso colour under each face: indigo = Boy, earth-brown = Uncle, sage-green = Grandma; two faces with the same costume = `DUP_ID?`, a warning). The costume table is design-specific and must be updated after the redesign.
- Expected counts: `--expect` JSON (exact counts per still, what the v4.5 shot list should provide), or the script (v4.5 "Faces" column via `qc_clips.script_rows`; for older tables the union of the START and END cells), or `--images-json`.
- Output: Markdown/JSON table (expect, faces, persons, count, face size, sharpness, text, flags), a contact sheet with boxes (faces green, persons blue) and flags in red, exit code 1 on any FAIL. 127 stills in about 45 s on 4 cores.
- **Measured on the v4.4 stills** (`specs/frames/ep01v44`, 63 portrait + 64 landscape). Ground truth by eye (`specs/qc/ep01v44_stills_gt.json`): 34 stills with a duplicated character or an unscripted extra person (14 portrait, 20 landscape; more than the 20 "source stills" in fix-plan.md because END stills and both orientations are counted separately).

| Flag set | Flagged | True | Precision | Recall |
|---|---|---|---|---|
| `DUP` (FAIL: head/body count > expected) | 26 | 21 | **0.81** | **0.62** |
| `DUP` or `DUP_ID?` (count or same costume twice) | 38 | 26 | 0.68 | **0.76** |
For comparison, `qc_clips.py` on the finished clips caught 14 of 21 duplicate clips with 10 other flags.
- False alarms of `DUP` (5): C01_end, C36, C36_land, C36_end_land are real still-vs-script mismatches (the Boy, or the Uncle's body at the frame edge, visible but not named in the v4.4 script), which a gate should report; C24_end is a detector error (a raised fist counted as a face).
- Misses (8 with both flags): C13 x4 (an unscripted stranger seen from behind, blurred: no face, YOLOX misses the blur), C19_end (second Uncle with his face cut off by the frame), C20 (second Uncle head half hidden behind the first), C23_land (a doubled body merged into one silhouette), C07_end (an intended silhouette counted as a duplicate by the fix plan).
- Report files: `tools/episode_maker/specs/qc/ep01v44_stills_qc.md` (table + scores), `specs/qc/ep01v44_stills_qc_sheet.jpg` (contact sheet with boxes and flags, downscaled).
- **Open-vocabulary counters (OWLv2, Grounding DINO) and DINOv2 identity**: not possible in this container: their weights are on huggingface.co, which the proxy blocks (403), and there is no PyTorch here. They can run in a Kaggle job (internet on) on CPU or GPU; recommended as the next upgrade only if the gate's misses matter after the v4.5 rules (2 faces max, explicit head counts) remove most crowded frames. Licenses to re-check on the model cards at that time.

## C. Mouth animation (Fix 5a)
- **Rhubarb Lip Sync 1.14.0** (MIT; LICENSE.md: all third-party parts MIT/BSD-style, "you can use Rhubarb Lip Sync in almost any way you want, including commercial"). Downloaded from the GitHub release into `tools/episode_maker/assets/rhubarb/` (git-ignored; `python3 mouth_overlay.py --fetch-rhubarb` reinstalls it). Verified on the Qwen3-TTS line `tts/gpu/034b8c85a93d3ec5.wav` (Boy, "Dad was right... the best part is worth the wait.", 2.96 s at natural speed): `pocketSphinx` recognizer with the line text 6.8 s CPU, `phonetic` 1.0 s; cue timing matches the voiced segments (silence 0.56-1.29 s found by both). On TTS it under-uses the open shapes (C 0.21 s, D 0 s), hence the optional `--energy` boost.
- **`mouth_track.py`**: start point from YuNet at the best scale + a search for the drawn mouth stroke below it (or a manual `--point`), then pyramidal LK optical flow on face features with a RANSAC similarity (shift, scale, roll), forward-backward checked; drift corrected toward the re-found mouth stroke (YuNet landmarks shift between scales, so they are only used at the frame-1 scale). Measured on C36 (98 frames, 2.4 s CPU): the point stays on the drawn mouth within about 2 px on every frame (checked on 8 frames). On C12 (Grandma, a clip that self-cuts) it correctly reports `ok: false` for 56 lost frames. On C31 the largest face is the Uncle, not the speaking Boy: talk shots need `--near x,y` (or the shot list's speaker position). On the Uncle the stroke search can lock onto the mustache: use `--point` + `--no-refine`.
- **`mouth_overlay.py`**: Rhubarb cues -> 6 sprites (`MOUTH_MAP`); the rest/closed shape keeps the clip's own mouth; open shapes first erase the drawn mouth line (inpainting of the dark stroke pixels on the flat skin), then paste the sprite at the tracked point, scaled and rotated with the face; `--on-twos` (mouth changes on 12 fps, like the picture), `--loop pingpong|hold|loop`, audio muxed at `--offset`. Procedural sprites are drawn in the line colour sampled from the clip.
- **Demo** `tools/episode_maker/out/mouth-demo.mp4` (5.0 s, 720x1280, 24 fps, with the voice; git-ignored): v4.4 clip C36 (Boy close-up, face 210 px tall) + the line above at natural speed, offset 0.6 s, on twos, energy 0.6. Command in the `mouth_overlay.py` docstring. Judged on frames at full size: the erase is invisible, sprites sit on the mouth position on every frame, the line weight matches, and the result reads as TV-anime mouth flaps. Weak points: `pucker` is small (a dot) at this face size; long Rhubarb B runs hold the same `teeth` sprite for 0.3-0.5 s; the procedural shapes are generic (drawn sprites per character will look better, see `production/v4/mouth-sprite-spec.md`).
- CPU cost: about 9 s for 120 frames (tracking included 2.4 s); no GPU.
- Not yet done: wiring into `make_episode.py` (per line: speaker -> clip -> track -> overlay; needs the v4.5 spec format and the redesigned sprites).

## D. LatentSync (CPU check only, no GPU run)
- **License**: code Apache-2.0 (repo LICENSE). Model weights on huggingface.co (`ByteDance/LatentSync-1.5` / `-1.6`); the model-card license could not be read from here (huggingface.co blocked) and must be checked before use. Inference also downloads Whisper tiny (MIT) and the SD VAE (check its card).
- **InsightFace**: `latentsync/utils/face_detector.py` uses `insightface.app.FaceAnalysis` (detection + `landmark_2d_106`, models are non-commercial); inference only reads 3 points (eyebrow centres, nose) and a contour box. Written: `tools/episode_maker/gpu/latentsync_yunet.py`, a drop-in `FaceDetector` with the same interface built on YuNet (MIT) or a fixed box from our tracker. For anime faces the 3 points are synthesized so that LatentSync's own alignment puts the eye centres just above its mouth mask and the mouth in the middle of it. Verified on CPU on C36, C31, C14_land: faces found on every frame (98/98, 82/82, 98/98), aligned 256x256 crops look like LatentSync's training crops with the mouth inside the mask (preview command in the file). Not verified: the actual lip-sync result.
- **Install**: requirements pin torch 2.5.1/cu121, diffusers 0.32.2, transformers 4.48.0, mediapipe, insightface 0.7.3, onnxruntime-gpu; on Kaggle this means a separate venv or `--no-deps` pins like the other notebooks; remove insightface. VRAM: 8 GB for 1.5 (fits a T4), 18 GB for 1.6 (does not).
- **Risks for anime** (to test once the redesign exists): it regenerates the whole lower face inside the mask, so the Uncle's mustache will be repainted (likely smeared); it was trained on real faces (the README's anime demos come from VASA-1 stills). The sprite route (C) has no such risk and should stay the default.

## Files
New: `tools/episode_maker/qc_stills.py`, `mouth_track.py`, `mouth_overlay.py`, `gpu/latentsync_yunet.py`, `gpu/make_charsheets_v45_input.py`, `gpu/inputs/charsheets-v45/` (images.json + 6 single-character reference crops, 356 KB), `specs/qc/ep01v44_stills_gt.json`, `specs/qc/ep01v44_stills_qc.md`, `specs/qc/ep01v44_stills_qc_sheet.jpg`, `production/v4/mouth-sprite-spec.md`, this report. Git-ignored: `assets/rhubarb/`, `assets/qc_models/yolox_s.onnx`, `out/mouth-demo.mp4`, `out/qc_stills_ep01v44.png`.

## Problems and open items
1. Model sheets: wait for the approved redesign; reuse the turnaround recipe (single-character crops + "exactly one character"), give expressions/hands/mouths the approved turnaround as reference.
2. The stills gate needs exact head counts from the shot list (v4.5 "Faces" column) to stop flagging script omissions; the costume table must be re-measured on the new designs.
3. Mouth overlay: speaker selection on 2-shots (`--near`), Uncle mustache anchoring, integration into `make_episode.py`.
4. LatentSync: GPU smoke test on 3 redesigned close-ups (about 0.5 GPU-h incl. install) only after the redesign; read the weights' license on the model card first.
