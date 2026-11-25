# V4 video tech: how to get real animation (free first)

Author: video / animation engineer. Date: 2026-11-25. Status: route chosen and proven on a 10-second test clip.

## 1. Verdict in five lines
1. **Free route that runs in this container and works today: a code-driven 2D skeletal rig** (head, torso, two arms, two legs per character, cut from the approved art) with procedural eyes, brows, mouth and a pseudo-3D head turn, on top of a perspective-correct layered background, with voices, sound and captions from the existing pipeline. No GPU, no paid service.
2. **What it is, honestly:** high-quality "limited animation": characters walk, bounce, turn their heads, point, gesture, react, eat, jump and run; the camera moves through a living street. It is closer to a polished motion-comic or a cut-out cartoon than to hand-drawn anime. Fast cuts, smears, speed lines, impact frames and sound carry the anime rhythm. It will not do full-body turns, 3D camera orbits, crowds, cloth, liquids or fighting choreography.
3. **Free AI video models cannot run here:** the model weights live on huggingface.co / ModelScope, both blocked from this container, and even with weights a 4-core CPU would need hours per 5-second clip. They can only be used as creator-run jobs on a free Kaggle/Colab GPU, for hero shots, with identity drift.
4. **Frame interpolation (RIFE) does run here on CPU** (about 0.4 s per interpolated 720x1280 frame) and is available for smoothing pose-swaps and AI clips.
5. **The real blocker is art, not tooling.** The rig is limited by how the current flat cut-outs are sliced. The art team must deliver layered parts, expression sets, turnarounds and layered backgrounds (section 6). With those, the same pipeline gets a large quality jump. A paid image-to-video tool becomes worth it only for specific hero shots (section 8).

## 2. What was verified in this container (2026-11-25)
| Resource | Reachable? | Notes |
|---|---|---|
| huggingface.co, hf.co, hf-mirror.com | No | blocked by the egress proxy |
| modelscope.cn | No | blocked |
| GitHub (release assets, raw) | Yes | 430 MB RIFE zip downloaded fine |
| PyPI | Yes | opencv, bpy (427 MB wheel) installed |
| npm, conda-forge, Maven | Yes | |
| apt (Ubuntu mirror) | Yes (root) | `apt-get update` then install works |
| download.blender.org, jsdelivr CDN, sourceforge | No | use the PyPI `bpy` wheel instead |
| Google Colab / Kaggle sites | Not reachable from here | irrelevant: the creator would run them in their own browser |

Hardware: 4 CPU, 15 GB RAM, no GPU, no Vulkan device (only software Mesa).

## 3. Options table
Quality = fit for "real animated sequences, same drawing". Speed = on this container.

| Route | Quality for our need | Speed here | Cost | Verdict |
|---|---|---|---|---|
| **A. Own Python skeletal rig** (numpy + OpenCV + PIL), built from our PNGs | Good for limited animation; keeps the exact approved drawing; limited by part slicing and by front-view-only art | About 0.3 to 0.4 s per 720p frame (2:00 = 15 to 20 min, 5 min on 4 processes); 1080x1920 about 2.3x | Free | **CHOSEN.** Proven (section 5) |
| B. Blender via `pip install bpy` (armature, mesh deform, shape keys, Grease Pencil, 3D camera) | Same ceiling as A, plus true 3D camera, nicer deformation and a GUI the creator could use | Works headless after `apt install libegl1`: Workbench 1.2 s, Cycles CPU 7.8 s, EEVEE 22 s per 720p frame (software GL) | Free | **Upgrade path**, not needed now. Heavier authoring than A, 5 to 50x slower per frame. Use only if a shot needs a real 3D camera |
| C. Wan 2.1 / 2.2 (1.3B, 5B, 14B), LTX-Video, HunyuanVideo, CogVideoX, AnimateDiff, ToonCrafter (open image-to-video / video diffusion) | Best "real motion" of the free options, but identity and line-style drift, 480p to 720p, 2 to 5 s clips, 16 to 24 fps; needs upscaling and cleanup | **Impossible here**: weights unreachable (HF blocked) and CPU would need hours per clip (estimate, not measured). Wan 1.3B alone is about 4 min per 5 s clip on an RTX 4090, roughly 100x faster than this CPU | Free software, free GPU hours are limited | Creator-run only (section 7). Hero shots, optional |
| D. Free hosted GPU (Kaggle about 30 GPU-hours a week, T4/P100; Colab free T4, variable) | Same models as C | Estimate: 10 to 30 min per 5 s clip on a T4 for the small models; the 14B models do not fit without heavy quantization | Free, no guarantees, a studio Google account and phone verification are needed | Optional pilot, see section 7 |
| E. RIFE frame interpolation (rife-ncnn-vulkan, CPU mode) | Good for small motion (12 to 24 fps, smoothing); ghosts on big pose changes | About 0.4 s per interpolated 720x1280 frame (verified) | Free | **Use as a tool**, not as the animation source |
| F. FILM interpolation | Similar to E, better on large motion | Not tested (weights hosted on Google storage / HF) | Free | Skip, RIFE is enough |
| G. Synfig (apt `synfig` 1.5.1 exists) | Vector-first; bone layers for bitmaps exist but authoring is XML or GUI | Not tested; CLI render is slow | Free | No: A does the same job under our control |
| H. OpenToonz | Needs hand-drawn frames; GUI first, no headless mode | n/a | Free | No |
| I. Spine / DragonBones / Live2D | The same idea as A (bones + mesh), with a GUI editor | Needs a separate runtime/renderer | Spine from about 70 USD (Essential) one-time; Live2D free tier limited | No: no benefit over A at our scale |
| J. Lottie / Rive | UI-animation formats, vector oriented; Rive editor is a web GUI | Not headless friendly | Free tiers | No |
| K. Remotion (React to headless Chromium to MP4) / Motion Canvas (TypeScript timelines) | Same class as A (transform animation of images), nicer timeline authoring; no mesh warp without custom WebGL | Needs a Chromium download; untested | Free (Remotion licence is free for individuals and very small companies, check the terms) | No: A already integrates with our voices, sound and captions |
| L. Hybrid: AI keyframes in Canva + code animation + RIFE | This is the practical form of A: Canva makes the layered art and poses, code moves them | As A | Free (Canva generation is in the existing subscription) | **Part of the chosen pipeline** (section 4) |
| M. Paid image-to-video (Kling, Runway, Hailuo, Pika, Veo) | Best motion quality available, still style drift on a hand-drawn look | Cloud | See section 8 | Fallback for hero shots |

## 4. Chosen pipeline
```
Canva (layered art: parts, expressions, poses, background plates)
   |  split / clean (split_parts.py, later: use the layers directly)
   v
rig.py   : part hierarchy + procedural face + pseudo-3D turn  (OpenCV warps, premultiplied alpha)
street.py: layered background with real perspective, lanterns, drifting petals (stand-in for painted plates)
rigdemo.py: shot timeline in code (keyframes, springs, squash and stretch, motion blur by sub-sampling)
make_episode.py: Kokoro voices, synthesized music and sfx, captions (already approved), final mix and encode
RIFE (optional): 12 -> 24 fps smoothing, AI clip smoothing
```
Design notes (what the rig does, so the art team knows what to feed it):
- **Skeleton:** root (about the feet) > torso > head, left arm, right arm; root > left leg, right leg. Each part has a pivot and is transformed with rotation, translation, scale, so squash and stretch, anticipation, overshoot and spring settling are real.
- **Face:** eyes, brows and mouth are redrawn per frame (4x supersampled) over a cleaned head, so blink, look direction, brow raise, 6+ mouth shapes and talking from the voice envelope all work. A radial displacement field shifts the inner features horizontally to fake a head turn of roughly 20 to 25 degrees while the silhouette stays fixed.
- **Walk toward the camera:** front-view art does not allow a side walk, so the test uses a "waddle" walk toward the viewer (alternating foot lift, weight shift, body bob, arm swing) while the camera retreats and the street recedes in perspective.
- **Motion blur:** 9 temporal sub-samples on fast shots (jump, run). Speed lines, dust puffs, impact beats.
- **Voices and lip sync:** the mouth opening follows the Kokoro audio envelope (240 Hz). A phoneme-based viseme driver is the planned upgrade.

## 5. Proof: the test clip
Folder: `tools/episode_maker/out/` (git-ignored; regenerate with the commands below).
- `tools/episode_maker/out/rig-test.mp4`: 720x1280, 24 fps, 10.0 s, H.264 + AAC (voices, footsteps, sfx, ambience). Contact sheet: `tools/episode_maker/out/rig-test-contact.png`.
- `tools/episode_maker/out/grandma-test.mp4`: 720x1280, 24 fps, 4 s, Grandma at her stall (head turn, blink, talking mouth, pleating hands, steam).
- `tools/episode_maker/out/rife-12to24-check.mp4`: 2 s, 12 fps frames interpolated to 24 fps with RIFE on CPU.

Shot list of `rig-test.mp4`:
| Time | Action |
|---|---|
| 0.0 to 3.3 | Boy and Uncle waddle toward the camera down a lantern street; camera retreats, perspective recedes, petals drift, lanterns sway; the boy glances around, the Uncle bobs and weight-shifts |
| 3.3 to 3.6 | Stop with squash and spring settle, dust puffs |
| 3.6 to 5.2 | Uncle lifts his head and turns it, brows up, sniffs (chest pulses) and says "I smell... destiny." with lip sync; the boy turns his head to him |
| 5.3 to 6.4 | Anticipation, then the Uncle's arm snaps up with overshoot, body lifts, "For science!" |
| 6.0 to 7.0 | A dumpling arcs in; the Uncle's eyes open and track it, mouth opens wide; the boy gasps, hops, flaps his arms and says "Uncle, wait!" |
| 6.95 to 7.8 | Chopsticks catch the dumpling, it goes to the mouth, cheeks puff and chew with a bob |
| 7.8 to 10.0 | Squash, stretch jump, "Mine!", motion-blurred run off to the right with dust and speed lines; the boy runs after him |

Quality assessment (honest):
- Reads as animation: yes. Characters have weight, anticipation, overshoot, eye tracking, talking, blinking, chewing. The approved drawing is preserved exactly.
- Reads as "short anime series": not yet. Motion is that of a cut-out puppet: front view only, sleeves and hands are rigid, no hair or cloth motion, no real turn-around.
- Visible artifacts, all caused by the source art and fixable with proper layers: the Uncle's raised sleeve looks like a flat flap, ragged inpainted patches at the shoulder when an arm is raised, boy's raised arms are stiff, leg cut lines at the hem when a leg is raised, the procedural open eyes are close but not identical to the art style, the boy's eyes cannot widen (no open-eye variants), head turn is limited to about plus or minus 25 degrees.
- Grandma's current art is painted in a different, more detailed style than the Boy and the Uncle. She works as a bust-and-stall layer set (head, body, hands) but the style mismatch will show in a mixed scene. Redraw her in the picture-book style.

Reproduce:
```
cd tools/episode_maker
pip install opencv-python-headless kokoro-onnx soundfile scipy pillow numpy   # + the TTS model files, see README
python3 rig/split_parts.py                  # specs/puppets/*.png -> specs/rigs/<name>/ (parts + parts.json)
python3 rig/rigdemo.py out/rig-test.mp4     # about 2 minutes for 240 frames
python3 rig/grandma_demo.py out/grandma-test.mp4
```
Code: `rig/rig.py` (rig, face), `rig/street.py` (background), `rig/rigdemo.py` (timeline), `rig/split_parts.py` (part slicing), `rig/grandma_demo.py`.

## 6. Exact install steps
Base (already needed by the episode maker):
```
pip install kokoro-onnx soundfile scipy pillow numpy opencv-python-headless
mkdir -p tools/episode_maker/tts && cd tools/episode_maker/tts
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```
RIFE on CPU (frame interpolation):
```
mkdir -p ~/rife && cd ~/rife
curl -L -o rife.zip https://github.com/nihui/rife-ncnn-vulkan/releases/download/20221029/rife-ncnn-vulkan-20221029-ubuntu.zip
unzip rife.zip && cd rife-ncnn-vulkan-20221029-ubuntu && chmod +x rife-ncnn-vulkan
mkdir in out        # in/00000000.png, 00000001.png, ... (copy files, symlinks are ignored)
./rife-ncnn-vulkan -i in -o out -m rife-v4.6 -g -1 -f %08d.png    # -g -1 = CPU; "vkCreateInstance failed" lines are harmless
```
Optional Blender (only if a shot needs a 3D camera or Grease Pencil):
```
apt-get update && apt-get install -y libegl1 libgl1 libxkbcommon0 libsm6 libxi6 libxxf86vm1 libxfixes3 libxrender1
python3 -m venv ~/bpyenv && ~/bpyenv/bin/pip install bpy        # bpy 5.3.0, 427 MB wheel, Python 3.13
```

## 7. Free AI video, only as a creator-run pilot
Not part of the automated pipeline. If the creator wants to try for hero shots:
- Kaggle notebook (free T4 x2, about 30 GPU-hours a week, 9 to 12 h sessions, internet on after phone verification) or Colab free. Use a studio account, not a personal one.
- Models worth trying, smallest first: Wan 2.2 TI2V-5B or Wan 2.1 1.3B (image-to-video, 480p to 720p), LTX-Video distilled (fast), CogVideoX-5B-I2V, ToonCrafter (two keyframes in, in-between out, 512x320, 12 to 27 GB depending on setup).
- Feed it the exact Canva still of the shot as the first frame; expect 2 to 5 s clips, drift of the face and line weight, and low resolution. Upscale and interpolate afterwards (RIFE). Judge on 3 test shots before committing any time.
- Output goes back into the timeline as a clip layer, with captions and sound from our pipeline.

## 8. Paid fallback, and the exact point where it is worth it
Indicative public prices (third-party aggregators, 2026; they vary by region and plan, verify before buying):
| Tool | Approx. price | What it would unlock |
|---|---|---|
| Kling (3.x) | about 0.07 to 0.14 USD per second of video | best stylized image-to-video, start and end frame control |
| Veo 3.1 (Fast / Lite) | about 0.05 to 0.10 USD per second (Fast and Lite tiers), 0.40 per second full | strong motion, can generate sound |
| Hailuo (MiniMax) | about 0.13 USD per second | good character motion, fast |
| Runway Gen-4 / 4.5 | about 0.05 to 0.12 USD per second | image-to-video, editing tools |
| Pika 2.5 | about 0.04 USD per second | cheapest, lower fidelity |
Rule of thumb for 2:00 episode: if 30% of the runtime (36 s) is AI video and each usable second costs 3x retakes, that is about 36 x 0.10 x 3 = about 11 USD per episode (range 5 to 25 USD), or one 10 to 40 USD monthly plan.

**When to pay:** when the rig pipeline with the proper layered art (section 9) is in place and the creator still marks specific shot types as not good enough, namely: full-body turns, running or fighting action with perspective change, crowds, flowing cloth, pouring and steam interaction, camera orbits. Pay only for those hero shots (about 6 to 8 shots, 5 to 10 s each), never for the whole episode.
**Which one:** first a free pilot with the Canva video quota that returns on 2026-12-16. If that is not enough, one month of **Kling** (best price-to-quality for stylized image-to-video with first and last frame) as a trial on 5 shots; keep Veo as the second choice when synchronized sound or longer shots are needed. Do not buy anything before the creator has seen the layered-art rig result.

## 9. Assets the art team must produce (this is what lifts quality)
Everything as separate transparent PNGs, same canvas scale per character, drawn in the approved round, soft picture-book style (thick brown outline, flat pastel fills). Size: character about 2400 px tall, so a 1080x1920 master still has zoom headroom.

**Per character (Boy, Uncle, Grandma; Dad only as a silhouette)**
1. **Parts, fully painted including hidden areas** (the area under a sleeve, behind the head, under the hem must exist so nothing shows a hole): head base without eyes, brows, mouth; ears; hat / front hair / back hair (Boy hat and ribbon, Uncle's head hair fringe); neck; torso with collar; belt and belt tails as separate swaying pieces; bag and strap (Boy); upper arm with sleeve; forearm with hand; thigh and shin as pants; foot with sandal; chopsticks as a prop.
2. **Expression sets** on the head, aligned to the same anchor: eyes (open, half, closed, happy arc, wide shock, side glance with separate pupils, tears), brows (neutral, up, angry, sad, worry), mouths (visemes: closed, M B P, A, E, O, U, F V, L, wide laugh, chew, smile, frown, yelp), cheeks (puffed, blush), nose scrunch, sweat drop and anger vein as overlays.
3. **Hands:** open, fist, pointing, gripping chopsticks, palm up, wave, holding a dumpling (4 to 6 drawings per hand).
4. **Views:** front (exists), three-quarter left and right, profile (left is a mirror of right), back. A turnaround sheet first, so the head, hat and body stay consistent. Boy hat in each view.
5. **Key poses for pose-swap animation** (full-body drawings, used with smears and RIFE): walk contact / down / passing / up in profile, run 4 poses, jump (crouch, stretch, land), shocked freeze, eating, laughing, pointing, sitting, bowing, falling, spin.
6. **Style fix for Grandma:** redraw in the same picture-book style as the Boy and Uncle, with the same part breakdown; stall cart, steamer and bowl as separate props.

**Backgrounds as layered plates** (no characters, no baked light that conflicts with the character, 1.3x frame size for camera moves)
- Per location: sky, far layer (mountains, skyline), mid layer (buildings, stalls), near layer (props, fences), ground, foreground overlays (foliage, hanging lanterns, cloth, smoke), plus a separate light-rays or haze layer.
- A **street kit** for one-point perspective: modular facade tiles (4 to 6 types), awning and lantern sprites, so the engine can scroll a street forever with true parallax.
- Interiors (stall, kitchen, tea house) as a back wall + counter layer + front objects layer.
- Sky variants: dawn, day, golden hour, dusk, night.

**FX sprites:** steam puffs, dust puffs, sparkles, impact starburst, speed lines, hearts, sweat drops, food bits, plus a dumpling set (raw, steamed, bitten, half) and a few hero food props per episode.

**How to get this from Canva (honest):** the image generator does not reliably produce clean disjoint body parts. More reliable order: (1) generate a character turnaround and expression sheet with the Boy / Uncle / Grandma reference images, (2) generate each needed full pose with a plain background, (3) use `remove-background` and `separate-image-layers` to cut, (4) clean hidden areas by hand or with the inpaint step already in `split_parts.py`. Backgrounds: generate frames with no characters and layer-separate them. Expect about 3 attempts per asset; the Boy alone fails more often, so generate him together with the Uncle or as a sheet.

## 10. Throughput for a 2:00 episode
Assumptions: about 30 shots averaging 4 s; roughly half full-rig shots, the rest close-ups with mouth and eye animation on layered art, insert cards and food shots.
- **Render:** 2,880 frames at 24 fps. Measured 0.3 to 0.4 s per 720x1280 frame (single process, 9-sample motion blur on fast shots). 720p: 15 to 20 min, or about 5 min with 4 processes. 1080x1920 master: about 2.3x, so 35 to 45 min single, 10 to 12 min parallel. Voices (Kokoro) about 1 s per line, cached.
- **Authoring:** the shot timeline is code (keyframes). With a reusable action library (walk, run, turn, point, eat, react, jump, sit, bow) plus a JSON shot spec, estimate 1 to 2 minutes of agent time per shot after the first episode; the first episode includes building the action library and the viseme lip-sync: allow 3 to 4 working sessions, later episodes 1 to 2.
- **Art:** the true bottleneck. Layered character set (one time per character) and a background kit per location; about 10 to 15 new generated assets per episode once the kits exist.
- **Review loop:** render the 720p preview of a changed shot in seconds (`--frames a:b`), full episode preview in minutes.

## 11. Next steps (in order)
1. Creator reviews `rig-test.mp4` and decides if the level (cut-out rig plus fast cutting) is acceptable as the base look.
2. Art team produces the layered Uncle and Boy sets (section 9, items 1 to 4) and one layered street kit; re-slice with the real layers instead of `split_parts.py` guesses.
3. Build the action library and a `rig` shot type in `make_episode.py` (JSON driven, same captions and mix), plus phoneme-based visemes.
4. Re-make Episode 1 as the pilot. Only then decide on paid hero shots (section 8).

## 12. Known limits and risks
- Front view only until three-quarter and profile art exists; side walking and real turns are impossible before that.
- Pseudo-3D head turn breaks beyond about 25 degrees; faces need the three-quarter views.
- The rig can not simulate cloth or hair; add secondary motion by hand (extra layers for belt tails, sleeve ends).
- Free AI video is unavailable in this container, so any AI shots depend on the creator running them.
- Price figures in section 8 come from third-party pages and may be out of date.
