# Fix plan: duplicated characters, melting faces, desync (Episode 1 v4.4)

Author: technical director. Date: 2026-11-26. Scope: the three defects the creator confirmed on Episode 1 v4.4, investigated on the real files, and a prioritized fix plan for the FREE pipeline (Kaggle T4 x2, LTX-Video 0.9.8 13B distilled nf4, FLUX.2 klein 4B, CPU tools). Paid options are handed over to `production/v4/tools-buying-plan.md`; the quality rubric is in `production/v4/quality-research.md`.

**How this was measured.** All 78 installed clips (`tools/episode_maker/specs/clips/ep01v44/*.mp4`, 39 portrait + 39 `_land`), their START/END stills (`specs/frames/ep01v44/`), the raw and post-processed GPU outputs (branch `gpu-results`, `ep01v44-clips-001/`), the GPU input (`gpu/inputs/ep01v44-clips-1/clips.json`, `ep01v44-stills*/images.json` + refs) and the render timeline (`make_episode.build_timeline` on `specs/episode-01-v4.4.json`). Every clip was viewed as a contact sheet (START still, 7 frames, END still), suspect frames were viewed at full size, and every clip was scanned with the new `tools/episode_maker/qc_clips.py` (section (f)). "Visual" counts below are from eyeballing; "QC" counts are the script's automatic flags.

## (a) Defect census

| Defect | Clips affected (of 78) | Portrait | Landscape | Worst clips (story impact) |
|---|---|---|---|---|
| **1. Duplicated / extra characters** | **21 clips** (27%) + 1 doubled limb | 9: C07, C08, C11, C13, C19, C20, C21, C32, C35 (+ C16 extra arm) | 12: C02, C06, C08, C11, C13, C15, C16, C17, C23, C32, C34, C35 | **C19** (two Uncles during the main gag, PEAK 2), **C35** (two Boys at the cliffhanger), **C21** (two Grandmas, frame turns into a split-screen collage), **C32/C32_land** (second Uncle at PEAK 3), **C11** (two Grandmas at "stall of destiny") |
| where the duplicate comes from | 16 already in the START still, 4 only in the END still (C07, C19, C35, C35_land), **1 invented by the video model** (C16_land) | | | 20 of 21 are baked into the keyframe stills before any video GPU is spent |
| **2. Smeared / melting faces** | **12 clips visually** (C01, C01_land, C07_land, C12, C14, C19, C21, C32, C34_land, C35, C35_land, I5); QC adds 7 more soft or low face-sharpness clips (C08, C08_land, C10_land, C25, C31_land, I3_land, I5b_land) | 8 | 4 (+ QC) | **C12** (whole frame melts at 0.7 s, then the camera "cuts" itself), **C01/C01_land** (ECU dissolves into a wide shot: ghosted double face), **C35_land** (Grandma dissolves into the aura), **C32** (mid-clip scene jump at 2.0 s) |
| contributing: faces too small | portrait median face height **10.7% of frame** (about 89 px at the 480x832 generation size = about 3 latent rows of the LTX VAE, which compresses 32x); 15 of 35 portrait clips with detectable faces are under 10% | | landscape median 15.3% of 480 px = about 73 px (even fewer pixels) | dialogue clips C11, C18, C22, C25, C35 (faces 8% of frame) |
| **3. Out of sync** | **all 39 clip pairs**: generated silent, no lip-sync (0 of 47 on-screen character lines synced) | | | |
| 3a. edit truncates the clip (END pose / payoff never shown) | 20 clip ids (QC `TRUNC`, shown under 85% of the clip): C03, C06, C07, C08, C10, C20, C25, C26, C30, C31, C34, C36, C37, I1-I6 | | | **C07** cannonball exit cut, **C25** chibi squash cut, **C03** rewind gag cut |
| 3b. slow-motion stretch to fit the voice | 7 clip ids (QC `SLOWMO`, 0.60-0.94x): C02, C09 (0.68x), C11, C14 (0.6x), C16, C23, C24 | | | 12 fps "on twos" stretched to 0.68x = about 8 drawings per second |
| 3c. frozen last frame (trim past the clip end) | 4 (QC `FREEZE`): C14 (2.0 s), C19 (1.7 s), C32 (1.7 s), C35 (0.9 s) | | | the spec trims to 5.0 s but the clips are 4.08 s long |
| 3d. wrong speed | 1: **C01_land plays at 2x** and at 832x480 (post-processing silently failed, then the "drop every 2nd frame" install filter halved a 12 fps clip) | | 1 | the first shot of the landscape episode |
| 3e. staging makes sync impossible | 12 shots have 2+ on-screen speakers inside one ~4 s clip; 36 of 47 character lines play over clips whose faces are under 12% of the frame | | | C10, C11, C17 (4 speakers in 4.3 s), C18, C20, C22, C25 |
| Also found | garbled AI text: raw C14 (a fake "fact card", hidden by an emergency crop that makes C14 soft and mis-framed), C21_land (fake sign), C26_land (scribbled paper); wrong actor: C17 (the Boy lifts the "sock" instead of the Uncle), C20 (Uncle standing, not in the barrel) | | | |

QC totals (78 clips, thresholds in `qc_clips.py` `TH`): 24 FAIL, 47 WARN, 7 PASS. The interpolation stripes of the RIFE bug are absent from the installed clips (0 striped frames; the raw `gpu-results` C14 has 48), so that bug is not part of what the creator saw.

## (b) Root causes, with evidence

**R1. The stills put every reference character into the picture, sometimes twice (cause of 20 of 21 duplicates).**
- The klein references are full scenes, not character sheets: `refs/both_eating.jpg` = Boy + Uncle, `refs/fat_uncle_pool.jpg` = Boy + Uncle, `refs/boy_only.jpg` = Boy + half of the Uncle. Most items use two of them, so the Uncle (and often the Boy) is offered twice; multi-reference editing composes what it is given.
- Every prompt starts with the full description of the Boy, the Uncle and Grandma even when the shot is a macro (C13 "the Uncle's blurred face just entering at the edge"; C21 "Grandma's chopsticks pinching a dumpling"): the model paints full characters instead of a hand or a blur (C13: an extra dark-haired man; C21: two Grandmas and a collage).
- END stills are generated from `@START` plus the same two scene refs and a new pose: C35_end gains a second Boy, C19_end a flying Uncle beside the standing one, C07_end a dark second figure.
- Nothing checks the stills: one variant per keyframe was picked and sent to video.

**R2. START and END stills that are different shots make the video model morph (smear + ghost duplicates).** QC `key_pair` (correlation of START vs END still): C01 -0.16, C01_land 0.03, C21 0.23, C07_land 0.54, C19 0.61, C35 0.82; every one of them dissolves, ghosts or duplicates. The script designs them that way (C01: "Extreme close-up" -> "Medium shot pulled back"; C19: "ECU mouth" -> "Wide: the Uncle rocketing upward"). LTX keyframe conditioning cross-fades between incompatible layouts.

**R3. Video prompts ask the model for things a single 3-4 s shot cannot do.** In `clips.json`: 6 of 39 prompts say "camera stays completely still" and then "pull-back / push-in / tracking"; about 6 carry editing instructions ("6-8 fast macro cuts", "one clip with 3-4 cuts", "snap zooms", "Cut to black"), which the model renders as self-cuts and melts (C12, C32); 3 request on-screen text ("[CARD: ...]", badge, title), which it renders as gibberish (C14, C21_land); C19 packs 8 beats into 4 s; 19 of 39 use `motion: high` (cond_noise 0.30, the most drift allowed). The prompts also do not name the characters the way the stills were described (motion-tech prompt rule 3).

**R4. Faces are generated with too few pixels, then upscaled.** 480x832 (portrait) and 832x480 (landscape), 12 fps, 8 distilled steps, 4-bit transformer, Real-ESRGAN anime x1.5. A medium shot face is about 89 px tall at generation, i.e. about 3 latent rows; any motion of a 3-row face is reconstructed by the VAE as a smear, and ESRGAN then sharpens the smear into a "painted" melt. Landscape is worse in pixels (480 px tall). The motion R&D already showed faces smear when the model zooms (`motion-tech.md`), and 14 of 32 I2V shot designs put 3 characters in frame, which forces medium-wide framing.

**R5. The timeline is built backwards: clips first, voices laid on top.**
- Clip lengths were fixed in `clips.json` (2.5-4.0 s) before the voices existed; the spec (`paper/build_spec_ep01v44.py`) still assumes 5 s clips for C32/C35 (trims to 5.0 s on 4.08 s files) -> frozen frames.
- `make_episode.py` then makes each shot as long as its voice: `fit_clip` stretches a short clip down to 0.6x (choppy slow motion) or plays a long clip at 1.0x and cuts the tail (the END keyframe, where the gag pays off, is never seen: 20 clip ids).
- To fit 371 words, the voices are sped up 1.28-1.38x (`voice_speed`), so lines sound rushed and still do not match any mouth.
- Lines start 0.1 s after every cut regardless of where the action is; the model decides on its own when the action happens (motion-tech: "end pose reached by about 1.8 s").
- Nothing moves the mouths: the clips are silent and no lip-sync or mouth animation exists anywhere in the pipeline. Banter between 2-4 characters inside one clip cannot be synced even in principle.
- Install bug: the on-twos workaround filter is applied blindly (C01_land at 2x).

**R6. No automatic gate and no re-roll.** One variant per clip, no stills check, no clip check; the contact-sheet review in `motion-tech.md` was not run on v4.4 before rendering.

## (c) Fixes, ranked by impact per cost (free pipeline)

| # | Fix | Fixes | Impact | GPU cost | Effort |
|---|---|---|---|---|---|
| 1 | **Stills hygiene + stills gate** | duplicates (about 19 of 21), part of smear | very high | ~1 GPU-h to redo all keyframes | 1 day |
| 2 | **Shot-design rules** in the script skill (2 faces max, close framing for talk, one action, matched START/END) | duplicates, smear, sync | very high | none (fewer, simpler clips) | 0.5 day |
| 3 | **Voice-first animatic and exact-length clips** | desync 3a-3d, rushed voices | very high | none (saves re-rolls) | 1-2 days |
| 4 | **Prompt compiler rules** (no edit/text/camera contradictions, named characters, motion low/medium) | smear, text, self-cuts | high | none | 0.5 day |
| 5 | **Mouth animation**: Rhubarb visemes + per-character mouth sprites (CPU), then LatentSync on close-ups | desync 3 (mouths) | high | 0 (sprites) / ~1-1.5 GPU-h per episode (LatentSync) | 2-3 days |
| 6 | **Bigger faces in pixels**: talk shots at 576x1024, tighter framing everywhere | smear | high | +60% per close-up clip (measured 135 s vs 85 s) | config |
| 7 | **QC gate with auto re-roll** (`qc_clips.py` + seed+1, max 2) | catches what slips through | medium-high | +20-30% clip GPU | 1 day |
| 8 | **Identity LoRAs** for klein (Boy, Uncle, Grandma) | drift, duplicates, fewer refs | medium-high | ~2-3 GPU-h per character (estimate) | 2 days R&D |
| 9 | **Face detail pass** (face crop -> LTX video-to-video low strength or LTX latent upsampler) | residual smear on hero close-ups | medium | ~1 GPU-h per episode (estimate) | R&D |
| 10 | Fix the install / post-processing path (fps check, RIFE bug or keep on-twos honestly) | 3d, choppiness | low-medium | none | 2 h |

### Fix 1. Stills hygiene and a stills gate (do first)
- **References = clean character sheets, one per character, each character exactly once.** Make three single-character model sheets (front, 3/4, side, plain cream background, no other person) from the locked art with klein: `boy_sheet.png`, `uncle_sheet.png` (from the locked intro-v3 variant 2), `grandma_sheet.png`. Use only the sheets of the characters that are visible in the shot, plus at most one background/style plate that contains **no people**. Never pass `both_eating.jpg`, `fat_uncle_pool.jpg` or `boy_only.jpg` again.
- **Prompt says the head count.** "Exactly two people in the frame: the Boy (image 1) and the Uncle (image 2). No other people." Describe only characters that are visible; a character that appears only as a hand gets no character description ("an old woman's floury hand holding a cleaver, only the hand is visible").
- **END still = an edit of the START still.** References: `@START` only (+ the one sheet of the character whose pose changes); instruction: "Same image. Change only: the Uncle's arms are crossed and his chin is lifted. Everything else identical." Reject the END if `key_pair < 0.80` (QC), and turn big changes into a cut between two clips instead.
- **Gate before video:** run YuNet face count on every still (`qc_clips.py` already counts faces on the START still: `DUP_IN_STILL?`) and build a contact sheet; the human (or Claude) looks at 70 thumbnails for 5 minutes. A still that fails is re-rolled (variant 2) before any clip is generated. Cost of this gate: zero GPU.

### Fix 2. Shot-design rules (update `write-episode-script` and `make-episode-v4` skills)
1. **At most 2 characters with visible faces per AI clip.** A third character may appear only as hands, a back, or out of focus and is not described with a face. Group moments (stall with three people) become two clips or a code-composited plate.
2. **Talk shots are medium close-up or close-up**: the speaking face at least 25% of the frame height in portrait (at least 200 px at 832 generation height), facing the camera or 3/4. Wides carry no on-screen dialogue (use V.O., the Narrator, or reaction shots).
3. **One speaker per clip.** Banter becomes shot / reverse shot: "It's a stall." and "Of DESTINY." are two clips. Overlaps happen in the cut, not inside a clip.
4. **One action per clip, 2-3 s**; gags with a pose change = START/END pair with the same framing and the same characters in the same places (`key_pair >= 0.80`). ECU -> wide, appear/disappear, flying off screen: build as a cut (two clips) or as a code effect (impact frame, dust cloud, speed lines) in `make_episode.py`.
5. **No text inside AI shots** (cards, signs, badges, titles are overlays).
6. **Camera moves are done in the edit** (punch-in, push, whip) on top of a fixed-camera clip.
7. Risky shot types to avoid or keep for paid hero shots: flying/rocketing characters, levitation with full body, morphs (chibi squash), characters entering or leaving the frame, crowd/caravan, eating with the face covered.

Applied to the v4.4 script (`scripts/episode-01-v4.4.md`), the risky designs are: 3-character frames in 14 shots (C11, C15-C20, C22, C23, C25, C26, C30, C32, C35); START/END that are different shots in C01, C07, C14, C19, C21, C26 (scroll burst), C35; multi-speaker clips in 12 shots; edit instructions inside one clip in C14, C19, C32, C35.

### Fix 3. Voice-first timing (animatic before GPU)
1. **Final voices first**, at natural speed (remove `voice_speed` 1.28-1.38; if the episode runs long, cut words, not speed). Pick takes.
2. **Word timestamps** for every line (forced alignment with openai-whisper word timestamps, MIT, CPU; or the TTS text + VAD), saved next to the WAVs.
3. **Animatic = the edit decision list.** Build the spec from the voices: each shot's length = its line(s) + the reaction beat; each gag gets an action time from the words ("Patient." -> exit happens at the word + 0.2 s). Render the animatic from stills (exists already: `-animatic` render) and get creator gate 2 on it.
4. **Generate each clip to its exact shot length** (`seconds` = shot length + 0.3 s handle, rounded to the 8-frame step) with keyframes placed at the action times (`keyframes` with `t` in seconds is already supported by `generate_clips.py`; validated for 2 keyframes on real weights).
5. **Edit at 1:1 speed:** `fit_clip` off for AI clips, no trim past the clip end, no stretch below 0.95x. QC `TRUNC`, `SLOWMO`, `FREEZE` must all be 0 before the final render (`qc_clips.py --spec`).
6. Fix the installer: never apply the frame-drop filter to a clip that is already 12 fps; reject a clip whose two orientations differ in length (QC `SPEED`).

### Fix 4. Prompt compiler rules (for the clips input builder `make_ep01v44_clips_input.py` and its successors)
- Build the video prompt from fields, not from the script prose: `camera` (fixed by default) + `who` (named exactly as in the still) + `one action with facial beats` + `style`. Strip: "PEAK", "cut", "cuts", "insert", "edit:", "snap zoom", "whip-pan", "[CARD", "badge", "title", "frames)" (a lint step fails the build if any remain).
- `motion`: `low` for talk shots, `medium` default, `high` only for at most 5 gag shots per episode.
- Add "mouth gently closed, not talking" for shots that will get a mouth overlay (Fix 5a), and "talking naturally" only for shots that will go through LatentSync (Fix 5b).

### Fix 5. Mouths and lip-sync
**5a (primary, free, CPU, genre-authentic): anime mouth flaps.** TV anime uses 3-5 mouth shapes; we can do the same deterministically.
- Rhubarb Lip Sync (MIT, verified on its LICENSE: "you can use it ... including commercial") turns each line WAV into timed mouth shapes (A-H + X).
- Draw a mouth sprite set per character (6 shapes x 3 characters, klein edit from the model sheets, cleaned by hand if needed).
- Track the mouth point: annotate it on the START still (one click per talk shot, or YuNet landmarks when they fire) and follow it with OpenCV optical flow through the clip (the camera is fixed, motion is small).
- `make_episode.py` composites the sprite at the tracked point, scaled with the face box, for the speaker of each line. Only on talk shots (Fix 2.2), so the face is big and still enough.
- Cost: no GPU; about 2-3 days to build once. Risk: looks pasted if the head turns a lot; keep talk shots calm (motion low).

**5b (close-ups, free GPU): LatentSync 1.5** (ByteDance, Apache-2.0 per the repo LICENSE; README: 8 GB VRAM minimum for inference, its demo set includes anime clips). Run on Kaggle on the talk close-ups only (about 15-20 per episode). Two cautions: its preprocessing uses InsightFace for landmarks, whose pretrained models are non-commercial (InsightFace README), so replace the detector with YuNet (MIT) or with fixed face boxes from our QC; and it was trained on real faces, so judge anime results on a 3-clip smoke test before adopting. Estimated 2-4 min per 4 s clip on a T4 (not measured).
- Candidates checked: **MuseTalk** (MIT code; README: "The trained model are available for any purpose, even commercially"; depends on whisper, sd-vae, dwpose, S3FD, each with its own license; real-face training, anime fit unknown) = second candidate. **Wav2Lip**: open-source version is non-commercial (README) = rejected. **LivePortrait**: MIT code but uses InsightFace models (non-commercial) = rejected unless the detector is replaced. InsightFace-based tools in general: rejected for the same reason.
- What stays out of reach for free: convincing lip-sync on profiles, on 2-shots with both talking, and on fast-moving heads (hand over to paid lipsync, section (e)).

### Fix 6. More pixels per face
- Talk close-ups (after Fix 2 these are most dialogue shots): generate at **576x1024** portrait (measured on T4: 135 s vs 85 s per 4 s clip at 24 fps, i.e. +60%; at 12 fps about 84 s vs 52 s). Combined with close framing the face goes from about 89 px to about 260-330 px tall (8-10 latent rows instead of 3).
- Landscape: generate only shots that cannot be re-framed from portrait (bible GPU rule 4) and give them 1024x576.
- Keep `steps: 8` (not 4) for faces; keep clips 2-3 s (drift grows after 3 s).
- Later test (R&D, same license): LTX 0.9.8 spatial latent upsampler instead of Real-ESRGAN for hero close-ups (ESRGAN sharpens smears; a latent pass can repaint them).

### Fix 7. Automatic QC gate with auto re-roll
- `qc_clips.py` (built now, section (f)) runs on CPU after every clips job: stripes, sharpness drop, face count on START still and through the clip vs the script's expected characters, face size, face sharpness, frame jumps, text detection, START/END match and START/END pair distance, and (with `--spec`) truncation, slow motion and frozen holds. Exit code 1 on any FAIL.
- Wire it into `kaggle_run.py`: after the job, failed ids are re-queued with `seed + 1` (max 2 re-rolls, then a human decides), as the bible already allows ("a 2nd variant only after a failed QC").
- Measured honesty: YuNet is a real-face detector; on our soft anime faces it misses some faces, so the duplicate flags caught **14 of the 21** duplicates seen by eye (with 10 other flags, 3 of them real morph defects) and the smear flags 8 of 12. Upgrades, in order: (1) the stills gate (Fix 1) where duplicates actually start; (2) an open-vocabulary person counter on Kaggle, OWLv2 or Grounding DINO (both Apache-2.0, verify the model cards), counting bodies rather than faces; (3) identity similarity: DINOv2 (Apache-2.0) embeddings of each detected character crop against the model sheets, flagging "two crops match the same character" and "crop matches nobody". Not used: InsightFace (non-commercial models), MediaPipe face mesh (Apache-2.0, but it does not find anime faces).

### Fix 8. Identity LoRAs (after 1-3 work)
- Train one LoRA per character for FLUX.2 klein 4B (Apache-2.0 base) on 20-30 approved sheet images each (turnaround + expressions + hands), 512-768 px, rank 16. Trainer: an MIT/Apache trainer that supports FLUX.2 klein (to verify; T4 has no bf16, so fp16 + gradient checkpointing + cached text embeddings). Estimate 2-3 GPU-h per character on one T4 (not measured; smoke-test 300 steps first).
- Benefit: references can drop to one or none, so the duplicate mechanism of R1 disappears and faces stop drifting between shots. LTX LoRA training does not fit a T4 (13B); the video model keeps getting identity from the stills.

### Fix 9. Face detail pass (R&D, hero close-ups only)
Crop the face region of a finished clip (box from QC, padded 30%, tracked), upscale the crop 2x, run LTX 0.9.8 video-to-video at low strength (0.2-0.3) with the character prompt, and paste back with a feathered mask (the open equivalent of a "face detailer"). Estimated 1-2 min per clip on a T4. Do not use GFPGAN/CodeFormer: they are real-face restorers (and CodeFormer's license is non-commercial); they turn anime faces photographic.

### Fix 10. Small pipeline fixes
- Installer: check fps and frame count before the on-twos filter; QC `SPEED` and `LOWRES` catch it (C01_land).
- Either fix the RIFE x2 corruption or keep 12 fps on twos as a style choice, but then never stretch clips (Fix 3), because stretched on-twos falls to about 8 drawings per second.
- Re-generate C14 without the fake card instead of cropping (the crop is why C14 is soft and mis-framed).

## (d) Two-week schedule and GPU budget

Measured basis: ep01v44-clips-001 used about 68 GPU-min for 78 clips (about 52 s per clip at 480x832, 12 fps, with START+END keyframes, post-processing included) plus about 8 min start-up per GPU; 128 keyframe stills took about 50 min. Budget: about 30 GPU-h per week, stop and re-plan at 22 h (bible). Estimates marked (est.) are not measured.

| Day | Work | GPU-h |
|---|---|---|
| **Week 1** | | |
| 1 | Rewrite the Ep 1 shot list with Fix 2 rules (more, shorter clips: about 45-50 AI clips, 2-3 s each, max 2 faces, talk shots in close-up, shot/reverse shot banter). Prompt lint (Fix 4). | 0 |
| 1 | Character model sheets (Boy, Uncle, Grandma) with klein, 4 variants each | 0.3 |
| 2 | Voices re-rendered at natural speed for changed lines (Qwen3-TTS), word timestamps (CPU) | 0.5 |
| 2 | All keyframe stills, portrait only, new refs, END = edit of START, 2 variants (about 100 stills x 2) | 1.5 |
| 2 | Stills gate: face count + contact sheet; re-roll failures (est. 20%) | 0.3 |
| 3 | Animatic from voices + stills; creator gate 2 | 0 |
| 3 | R&D smoke tests: 576x1024 close-up (3 clips), LatentSync 1.5 on 3 close-ups (install + run), OWLv2 person counter on 30 stills | 2.5 |
| 4 | Rhubarb + mouth sprites + tracker in `make_episode.py` (CPU); sprites with klein | 0.3 |
| 4-5 | Portrait clips at exact lengths: about 15 close-ups at 576x1024 (about 84 s each) + 33 others at 480x832 (about 52 s) + start-up | 1.1 |
| 5 | QC + auto re-roll (est. 30% of clips, 1 round) | 0.4 |
| 5 | Optional: Boy LoRA smoke (300 steps) | 1.0 (est.) |
| | **Week 1 total** | **about 8 h** (of 22) |
| **Week 2** | | |
| 6 | Lip-sync: mouth sprites on all talk shots (CPU); LatentSync on 15-20 close-ups if the smoke test passed | 1.0-1.5 (est.) |
| 6-7 | Landscape: re-frame from portrait where possible; generate only the rest (est. 20 clips at 1024x576) + QC re-roll | 1.0 |
| 7 | Face detail pass R&D on 5 hero close-ups | 1.0 (est.) |
| 8-9 | Identity LoRAs for Uncle and Grandma (and Boy if the smoke test was good); regenerate the 10 worst stills with them and their clips | 6-9 (est.) |
| 9 | Final QC (all flags), render both orientations (CPU), creator gate 3 | 0.2 |
| 10 | Buffer for re-rolls and fixes | 2 |
| | **Week 2 total** | **about 11-15 h** (of 22) |

Everything above fits under the 22 h stop line in each week; the LoRA work is the first thing to drop if a week runs hot. Every job is logged in `production/v4/gpu-ledger.md`.

## (e) What cannot be fixed for free (hand over to `tools-buying-plan.md`)
1. **Lip-sync on every visible mouth**, including 2-shots, 3/4 and profile views and moving heads: the free route covers calm close-ups (sprites) and maybe frontal close-ups (LatentSync, anime fit unproven). Paid lip-sync (lipsync-2 class) is the fallback for the rest.
2. **Multi-character action at quality** (three people interacting, contact, hand-offs, a character flying off screen, chases): the 13B 4-bit distilled model at 480-576 px will keep inventing or merging people in these; paid reference-to-video models with one element per character are the fix for the remaining 3-character shots and the 4-6 hero gags (C19 rocket, C35 power-up, intro chase).
3. **Native 720p-1080p faces in wide and medium shots**: on a T4, 576x1024 is the practical ceiling; anything wider keeps small faces.
4. **Fully fluid 24 fps acting** (no on-twos), until the RIFE bug is fixed and verified.
5. **Human-level comic timing in the voices** (human actors or a paid expressive TTS).
Free fixes 1-4 come first in every tier: a paid model does not fix duplicates baked into the stills or desync caused by building clips before voices.

## (f) QC tool: `tools/episode_maker/qc_clips.py` and its v4.4 report
```
python3 tools/episode_maker/qc_clips.py --fetch-models            # once: YuNet (MIT) + PP-OCRv3 text detector (Apache-2.0), ~2.6 MB, into assets/qc_models/ (git-ignored)
cd tools/episode_maker && python3 qc_clips.py specs/clips/ep01v44 --frames specs/frames/ep01v44 \
   --clips-json gpu/inputs/ep01v44-clips-1/clips.json --script ../../scripts/episode-01-v4.4.md \
   --spec specs/episode-01-v4.4.json --md out/qc.md --json out/qc.json
```
CPU only (about 2-3 minutes for 78 clips on 4 cores), OpenCV + numpy, no PyTorch. Without the models it still runs the stripe, sharpness, jump, keyframe and timing checks. Columns: `stripes` = worst row/column gradient ratio (>2.2 = corrupted frames); `sharp drop` = worst frame sharpness / frame 1; `faces key/first/last (expected)` = faces on the START still / in the first and last quarter of the clip / characters named in the script's START+END columns; `face h %` = median face height in % of frame height; `face sharp` = worst face-region sharpness / first; `jump` = biggest frame-to-frame change (>0.45 = self-cut); `text` = sampled frames with text-like boxes; `key pair` = START vs END still correlation (<0.80 = morph risk); `edit speed`, `shown` (share of the clip the edit shows), `frozen s` (seconds of frozen last frame) from the render timeline. Flags are heuristics: FAIL means a human must look.

| clip | verdict | stripes | sharp drop | faces key/first/last (expected) | face h % | face sharp | jump | text | key pair | edit speed | shown | frozen s | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C01 | FAIL | 0.89 | 0.63 | 1/1/1 (1) | 21.2 | 0.15 | 0.33 | 0 | -0.16 | 1.0 | 0.92 | 0.0 | FACE_SMEAR MORPH_RISK |
| C01_land | FAIL | 0.95 | 0.64 | 1/1/1 (1) | 26.7 | 0.07 | 0.16 | 0 | 0.03 | 1.0 | 1.81 | 0.0 | FACE_SMEAR MORPH_RISK LOWRES SPEED |
| C02 | WARN | 0.92 | 0.8 | 1/1/2 (2) | 11.5 | 0.78 | 0.09 | 0 | 0.99 | 0.84 | 1.0 | 0.0 | FACE_ADDED SLOWMO |
| C02_land | FAIL | 0.99 | 0.9 | 3/2/2 (2) | 13.3 | 0.57 | 0.01 | 0 | 0.99 | 0.84 | 1.0 | 0.0 | DUP_IN_STILL? SLOWMO |
| C03 | WARN | 0.93 | 1.0 | 1/1/1 (2) | 13.9 | 0.71 | 0.02 | 0 | 0.99 | 1.0 | 0.78 | 0.0 | TRUNC |
| C03_land | WARN | 1.03 | 1.0 | 2/1/1 (2) | 17.4 | 0.98 | 0.02 | 0 | 0.99 | 1.0 | 0.78 | 0.0 | TRUNC |
| C06 | WARN | 0.88 | 0.79 | 2/2/2 (2) | 12.7 | 0.52 | 0.01 | 0 | 0.99 | 1.0 | 0.83 | 0.0 | TRUNC |
| C06_land | FAIL | 0.92 | 0.87 | 3/3/3 (2) | 11.8 | 1.0 | 0.06 | 0 | 0.99 | 1.0 | 0.83 | 0.0 | DUP? CROWD DUP_IN_STILL? TRUNC |
| C07 | WARN | 0.9 | 0.94 | 2/2/2 (2) | 10.7 | 0.87 | 0.01 | 0 | 0.95 | 1.0 | 0.75 | 0.0 | TRUNC |
| C07_land | FAIL | 0.99 | 0.76 | 2/1/1 (2) | 18.8 | 0.95 | 0.19 | 0 | 0.54 | 1.0 | 0.75 | 0.0 | MORPH_RISK TRUNC |
| C08 | FAIL | 1.13 | 0.97 | 2/1/1 (2) | 7.3 | 0.05 | 0.03 | 0 | 1.0 | 1.0 | 0.73 | 0.0 | FACE_SMEAR SMALL_FACE TRUNC |
| C08_land | FAIL | 1.24 | 0.81 | 2/2/2 (2) | 12.5 | 0.31 | 0.13 | 0 | 0.93 | 1.0 | 0.73 | 0.0 | FACE_SMEAR TRUNC |
| C09 | WARN | 1.12 | 1.0 | 1/1/1 (1) | 6.3 | 0.86 | 0.05 | 0 | 0.99 | 0.68 | 1.0 | 0.0 | SMALL_FACE SLOWMO |
| C09_land | WARN | 1.13 | 0.99 | 1/1/1 (1) | 9.7 | 0.77 | 0.01 | 0 | 0.99 | 0.68 | 1.0 | 0.0 | SLOWMO |
| C10 | WARN | 0.96 | 1.0 | 2/1/0 (2) | 10.2 | 0.73 | 0.02 | 0 | 0.96 | 1.0 | 0.75 | 0.0 | FACE_LOST TRUNC |
| C10_land | FAIL | 1.29 | 0.97 | 2/1/1 (2) | 16.5 | 0.38 | 0.03 | 0 | 0.97 | 1.0 | 0.75 | 0.0 | FACE_SMEAR TRUNC |
| C11 | FAIL | 0.9 | 0.98 | 4/3/3 (3) | 8.0 | 1.0 | 0.01 | 0 | 0.99 | 0.82 | 1.0 | 0.0 | CROWD SMALL_FACE DUP_IN_STILL? SLOWMO |
| C11_land | FAIL | 1.08 | 0.96 | 4/3/3 (3) | 11.2 | 0.64 | 0.19 | 0 | 0.98 | 0.82 | 1.0 | 0.0 | CROWD DUP_IN_STILL? SLOWMO |
| C12 | WARN | 1.01 | 0.4 | 1/1/1 (2) | 12.9 | 0.93 | 0.34 | 0 | 0.99 | 1.0 | 0.91 | 0.0 | SOFT |
| C12_land | PASS | 1.21 | 1.0 | 2/1/1 (2) | 16.3 | 0.68 | 0.03 | 0 | 0.98 | 1.0 | 0.91 | 0.0 |  |
| C13 | PASS | 1.06 | 0.85 | 2/2/2 (2) | 9.7 | 0.88 | 0.04 | 0 | 1.0 | 0.89 | 1.0 | 0.0 |  |
| C13_land | PASS | 1.19 | 0.99 | 2/2/2 (2) | 17.6 | 0.85 | 0.09 | 0 | 0.97 | 0.89 | 1.0 | 0.0 |  |
| C14 | WARN | 1.34 | 0.7 | 1/0/0 (1) | 0.0 |  | 0.09 | 0 | 1.0 | 0.6 | 1.0 | 2.01 | START_MISMATCH END_MISS SLOWMO FREEZE |
| C14_land | WARN | 1.25 | 0.91 | 1/1/1 (1) | 26.1 | 0.59 | 0.18 | 0 | 0.99 | 0.6 | 1.0 | 2.01 | SLOWMO FREEZE |
| C15 | PASS | 0.89 | 0.98 | 2/2/2 (3) | 9.8 | 0.91 | 0.0 | 0 | 0.99 | 0.92 | 1.0 | 0.0 |  |
| C15_land | FAIL | 1.0 | 1.0 | 4/3/4 (3) | 16.2 | 0.55 | 0.0 | 0 | 0.99 | 0.92 | 1.0 | 0.0 | FACE_ADDED CROWD DUP_IN_STILL? |
| C16 | WARN | 0.94 | 0.87 | 2/2/2 (3) | 13.3 | 0.76 | 0.03 | 0 | 0.99 | 0.8 | 1.0 | 0.0 | SLOWMO |
| C16_land | WARN | 1.2 | 0.98 | 3/2/3 (3) | 21.1 | 0.75 | 0.04 | 0 | 0.89 | 0.8 | 1.0 | 0.0 | FACE_ADDED CROWD SLOWMO |
| C17 | PASS | 0.82 | 0.86 | 2/2/2 (3) | 9.3 | 0.94 | 0.02 | 0 | 0.97 | 0.94 | 1.0 | 0.0 |  |
| C17_land | WARN | 1.18 | 0.94 | 3/3/3 (3) | 13.2 | 0.84 | 0.02 | 0 | 0.97 | 0.94 | 1.0 | 0.0 | CROWD |
| C18 | WARN | 0.96 | 1.0 | 3/2/1 (3) | 7.9 | 0.56 | 0.03 | 0 | 0.97 | 0.87 | 1.0 | 0.0 | FACE_LOST SMALL_FACE |
| C18_land | PASS | 0.97 | 1.0 | 2/2/2 (3) | 16.5 | 1.0 | 0.01 | 0 | 0.99 | 0.87 | 1.0 | 0.0 |  |
| C19 | FAIL | 0.8 | 0.92 | 2/2/1 (3) | 12.3 | 0.58 | 0.11 | 0 | 0.61 | 1.0 | 1.0 | 1.7 | FACE_LOST MORPH_RISK FREEZE |
| C19_land | WARN | 1.0 | 1.0 | 3/1/1 (3) | 24.6 | 0.64 | 0.08 | 0 | 0.9 | 1.0 | 1.0 | 1.7 | FREEZE |
| C20 | WARN | 0.95 | 0.99 | 2/2/2 (3) | 9.1 | 0.72 | 0.0 | 0 | 0.99 | 1.0 | 0.84 | 0.0 | TRUNC |
| C20_land | WARN | 1.02 | 0.98 | 2/2/2 (3) | 12.8 | 0.65 | 0.0 | 0 | 0.99 | 1.0 | 0.84 | 0.0 | TRUNC |
| C21 | FAIL | 0.9 | 0.59 | 3/3/3 (2) | 12.7 | 0.67 | 0.72 | 0 | 0.23 | 1.0 | 0.94 | 0.0 | DUP? CROWD JUMP MORPH_RISK DUP_IN_STILL? |
| C21_land | FAIL | 1.11 | 1.0 | 2/2/2 (2) | 24.7 | 0.85 | 0.12 | 4 | 0.99 | 1.0 | 0.94 | 0.0 | TEXT |
| C22 | WARN | 0.91 | 1.0 | 2/2/2 (3) | 8.4 | 0.48 | 0.0 | 0 | 0.99 | 0.92 | 1.0 | 0.0 | SMALL_FACE |
| C22_land | WARN | 0.96 | 1.0 | 3/3/3 (3) | 15.3 | 1.0 | 0.0 | 0 | 1.0 | 0.92 | 1.0 | 0.0 | CROWD |
| C23 | WARN | 0.92 | 1.0 | 2/2/2 (3) | 11.6 | 0.73 | 0.04 | 0 | 0.97 | 0.77 | 1.0 | 0.0 | SLOWMO |
| C23_land | WARN | 1.01 | 1.0 | 2/2/2 (3) | 18.2 | 0.98 | 0.15 | 0 | 0.98 | 0.77 | 1.0 | 0.0 | SLOWMO |
| C24 | WARN | 0.99 | 0.99 | 2/1/1 (2) | 9.4 | 1.0 | 0.0 | 0 | 0.99 | 0.8 | 1.0 | 0.0 | SLOWMO |
| C24_land | WARN | 1.33 | 0.99 | 2/1/2 (2) | 15.0 | 0.75 | 0.0 | 0 | 1.0 | 0.8 | 1.0 | 0.0 | FACE_ADDED SLOWMO |
| C25 | FAIL | 1.0 | 0.78 | 2/2/3 (3) | 7.9 | 0.4 | 0.06 | 0 | 0.99 | 1.0 | 0.75 | 0.0 | FACE_SMEAR FACE_ADDED CROWD SMALL_FACE TRUNC |
| C25_land | WARN | 1.14 | 0.97 | 3/3/2 (3) | 12.6 | 0.79 | 0.06 | 0 | 0.99 | 1.0 | 0.75 | 0.0 | FACE_LOST CROWD TRUNC |
| C26 | WARN | 0.87 | 1.0 | 2/2/2 (3) | 11.8 | 0.84 | 0.0 | 0 | 0.96 | 1.0 | 0.73 | 0.0 | TRUNC |
| C26_land | WARN | 1.2 | 0.95 | 3/2/2 (3) | 20.6 | 1.0 | 0.08 | 0 | 0.99 | 1.0 | 0.73 | 0.0 | TRUNC |
| C30 | WARN | 0.91 | 0.96 | 2/2/2 (3) | 10.7 | 0.93 | 0.06 | 0 | 0.99 | 1.0 | 0.73 | 0.0 | TRUNC |
| C30_land | WARN | 1.11 | 0.98 | 2/2/2 (3) | 10.8 | 0.93 | 0.0 | 0 | 0.99 | 1.0 | 0.73 | 0.0 | TRUNC |
| C31 | WARN | 0.81 | 0.97 | 2/1/1 (2) | 16.0 | 0.98 | 0.0 | 0 | 0.99 | 1.0 | 0.75 | 0.0 | TRUNC |
| C31_land | FAIL | 1.04 | 0.95 | 2/1/1 (2) | 28.1 | 0.17 | 0.02 | 0 | 0.99 | 1.0 | 0.75 | 0.0 | FACE_SMEAR TRUNC |
| C32 | FAIL | 0.98 | 0.62 | 5/3/0 (3) | 8.2 | 0.23 | 0.13 | 0 |  | 1.0 | 1.0 | 1.67 | FACE_SMEAR FACE_LOST SMALL_FACE DUP_IN_STILL? FREEZE |
| C32_land | FAIL | 0.95 | 0.96 | 4/4/4 (3) | 13.9 | 0.8 | 0.02 | 0 | 0.99 | 1.0 | 1.0 | 1.67 | DUP? CROWD DUP_IN_STILL? FREEZE |
| C33 | PASS | 1.08 | 0.99 | 0/0/0 (1) | 0.0 |  | 0.0 | 0 | 0.99 | 0.96 | 1.0 | 0.0 |  |
| C33_land | FAIL | 1.11 | 0.91 | 2/1/1 (1) | 10.7 | 0.75 | 0.01 | 0 | 0.99 | 0.96 | 1.0 | 0.0 | DUP_IN_STILL? |
| C34 | WARN | 0.85 | 0.96 | 1/1/1 (2) | 15.2 | 0.74 | 0.01 | 0 | 0.99 | 1.0 | 0.75 | 0.0 | TRUNC |
| C34_land | FAIL | 1.11 | 0.63 | 3/2/2 (2) | 12.5 | 0.21 | 0.05 | 0 | 0.99 | 1.0 | 0.75 | 0.0 | FACE_SMEAR DUP_IN_STILL? TRUNC |
| C35 | WARN | 0.95 | 0.86 | 3/3/3 (3) | 8.1 | 0.45 | 0.16 | 0 | 0.82 | 1.0 | 1.0 | 0.87 | CROWD SMALL_FACE FREEZE |
| C35_land | FAIL | 1.02 | 1.0 | 4/4/4 (3) | 11.9 | 0.66 | 0.15 | 0 | 0.9 | 1.0 | 1.0 | 0.87 | DUP? CROWD DUP_IN_STILL? FREEZE |
| C36 | WARN | 0.81 | 0.95 | 1/0/0 (1) | 16.3 | 1.0 | 0.01 | 0 | 0.99 | 1.0 | 0.83 | 0.0 | TRUNC |
| C36_land | WARN | 0.89 | 0.97 | 1/1/1 (1) | 28.6 | 1.0 | 0.01 | 0 | 0.99 | 1.0 | 0.83 | 0.0 | TRUNC |
| C37 | WARN | 0.9 | 0.96 | 2/3/1 (2) | 10.2 | 0.85 | 0.0 | 0 | 0.99 | 1.0 | 0.73 | 0.0 | FACE_LOST TRUNC |
| C37_land | WARN | 0.91 | 0.99 | 2/2/2 (2) | 12.6 | 0.73 | 0.0 | 0 | 1.0 | 1.0 | 0.73 | 0.0 | TRUNC |
| I1 | WARN | 0.85 | 0.95 | /1/0 (2) | 15.4 | 0.52 | 0.03 | 0 |  | 1.0 | 0.58 | 0.0 | FACE_LOST TRUNC |
| I1_land | WARN | 0.97 | 0.97 | /1/1 (2) | 28.3 | 0.63 | 0.01 | 0 |  | 1.0 | 0.58 | 0.0 | TRUNC |
| I2 | WARN | 0.88 | 0.43 | /0/0 (0) | 0.0 |  | 0.3 | 0 |  | 1.0 | 0.47 | 0.0 | SOFT TRUNC |
| I2_land | WARN | 1.12 | 0.34 | /0/0 (0) | 0.0 |  | 0.25 | 0 |  | 1.0 | 0.47 | 0.0 | SOFT TRUNC |
| I3 | WARN | 1.09 | 0.97 | /2/2 (2) | 9.1 | 1.0 | 0.06 | 0 |  | 1.0 | 0.73 | 0.0 | TRUNC |
| I3_land | FAIL | 1.25 | 1.0 | /2/1 (2) | 11.2 | 0.36 | 0.01 | 0 |  | 1.0 | 0.73 | 0.0 | FACE_SMEAR FACE_LOST TRUNC |
| I5 | FAIL | 0.88 | 0.53 | /2/0 (2) | 11.1 | 0.4 | 0.14 | 0 |  | 1.0 | 0.69 | 0.0 | SOFT FACE_SMEAR FACE_LOST TRUNC |
| I5_land | WARN | 1.02 | 0.82 | /2/2 (2) | 14.7 | 0.5 | 0.05 | 0 |  | 1.0 | 0.69 | 0.0 | TRUNC |
| I5b | WARN | 0.91 | 0.86 | /2/2 (2) | 7.5 | 0.45 | 0.01 | 0 |  | 1.0 | 0.44 | 0.0 | SMALL_FACE TRUNC |
| I5b_land | FAIL | 1.05 | 0.65 | /1/0 (2) | 7.6 | 0.44 | 0.06 | 0 |  | 1.0 | 0.44 | 0.0 | FACE_SMEAR FACE_LOST SMALL_FACE TRUNC |
| I5c | WARN | 0.71 | 0.91 | /0/0 (0) | 0.0 |  | 0.23 | 0 |  | 1.0 | 0.36 | 0.0 | TRUNC |
| I5c_land | WARN | 1.52 | 0.24 | /0/0 (0) | 0.0 |  | 0.21 | 0 |  | 1.0 | 0.36 | 0.0 | SOFT TRUNC |
| I6 | WARN | 0.91 | 0.47 | /1/1 (2) | 15.1 | 1.0 | 0.13 | 0 |  | 1.0 | 0.36 | 0.0 | SOFT TRUNC |
| I6_land | WARN | 1.14 | 0.41 | /0/1 (2) | 18.9 | 0.59 | 0.26 | 0 |  | 1.0 | 0.36 | 0.0 | SOFT FACE_ADDED TRUNC |

78 clips: 24 FAIL, 47 WARN, 7 PASS. Flags: TRUNC 40, SLOWMO 14, CROWD 13, FACE_SMEAR 12, DUP_IN_STILL? 11, SMALL_FACE 10, FACE_LOST 10, FREEZE 8, SOFT 7, FACE_ADDED 6, MORPH_RISK 5, DUP? 4, LOWRES 1, SPEED 1, START_MISMATCH 1, END_MISS 1, JUMP 1, TEXT 1
