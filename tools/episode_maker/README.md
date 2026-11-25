# Episode Maker

Builds a ~2-minute episode video from a JSON spec, in **both formats** (vertical 9:16 for Shorts and horizontal 16:9 for regular YouTube), with **no paid video service**:

- **Voices:** Kokoro neural TTS (open model, runs locally; cast in `VOICES`). Optional engines per episode or character: Supertonic, Pocket TTS (CPU) and Chatterbox/Orpheus (free Kaggle GPU); see "Voice engines" below
- **Music + sound effects + ambience:** synthesized from scratch (`synth.py`), so nothing is licensed or sampled
- **Picture:** Ken Burns camera moves, crossfades, burned-in captions, fun-fact cards, steam/hearts/flash effects
- **Output:** 1080x1920 (9:16) and/or 1920x1080 (16:9) H.264 + AAC, loudness-normalized; mobile versions 720x1280 / 1280x720

## Setup (once)
```
pip install kokoro-onnx soundfile scipy pillow numpy
mkdir tts && cd tts
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```
(also needs `ffmpeg`)

## Voice engines (optional)
Default is Kokoro, unchanged. Add `"voice_engine": "supertonic" | "pocket" | "gpu"` to a spec (or env `VOICE_ENGINE`) to switch the whole cast, and
`"voice_cast": {"uncle": {"engine": "supertonic", "sid": 9, "speed": 0.95, "pitch": 0.94}}` to change single characters. Presets: `voice_casts.json`.
CPU engines: `pip install sherpa-onnx && sh fetch_voice_models.sh` (GitHub only). GPU engine ("gpu" = pre-rendered WAVs from the Kaggle `tts` task, see `gpu/README.md` section 11) reads `tts/gpu/<line key>.wav`.
Compare engines on 6 sample lines: `python3 voice_test.py` (writes `out/voice-test/comparison.m4a`). Choice, licenses and cast: `production/v4/voice-tech.md`.

## Use
```
python3 make_episode.py specs/episode-01.json out/episode-01.mp4            # full quality
python3 make_episode.py specs/episode-01.json out/preview.mp4 --preview     # fast low-res check
python3 make_episode.py specs/episode-01.json out/episode-01.mp4 --mobile   # also writes out/episode-01-mobile.mp4
python3 make_episode.py specs/episode-01-v4.json out/ep.mp4 --both --mobile  # out/ep.mp4 (9:16) + out/ep-land.mp4 (16:9) + both -mobile.mp4
```
`--mobile`: 720x1280 (portrait) or 1280x720 (landscape), H.264 Main, crf 27, AAC 128k mono, faststart.
Frames (the 1080x1920 PNGs, one per shot) live in `specs/frames/ep01/` and are named in the spec (`img`).

## Both formats: vertical 9:16 and horizontal 16:9 (production bible, "BOTH FORMATS")
Every episode and the series intro are delivered twice with the same length, voices, music and timing; only the picture is re-framed.
| Option | What it does |
|---|---|
| (nothing) | Portrait 1080x1920, exactly as before. Old specs render unchanged. |
| `--landscape` | Horizontal 1920x1080 to `<out>` (preview 960x540, mobile 1280x720). |
| `--portrait` | Force vertical (overrides a spec `orientation`). |
| `--both` | Portrait to `<out>` and landscape to `<out stem>-land<ext>`; the timeline and the audio mix are built once. |
| spec `"orientation": "portrait" \| "landscape" \| "both"` | Same as the flags (flags win). Spec `size` is the portrait size; `size_landscape` overrides 1920x1080. |

**Stills and clips per orientation.** A shot's `img` / `clip` (and `layers.bg|fg`) is a file name or `{"portrait": "...", "landscape": "..."}`.
Naming convention: `C01.png` is the vertical still and `C01_land.png` its horizontal twin (same for clips: `C01.mp4` / `C01_land.mp4`; the GPU jobs in `gpu/` write exactly these names).
The horizontal render looks for `X_land` first (also in `frames_fallback` and `clips_dir`); if only the vertical file exists it uses a **center-cover crop** of it and prints one warning per file
(steer the crop with the shot's `focus`, or `focus_land`). The vertical render never uses a landscape file unless the dict form only names that one. Clips are cropped the same way (`crop_focus: [x, y]`, default center).
Clip fallback: if neither orientation of a clip exists, the still (with `fb` motion) plays in both, as before. Durations and clip audio come from the vertical clip (else the horizontal one), so give both the same length.

**Per-orientation overrides.** In the horizontal render every shot key `<key>_land` replaces `<key>` (e.g. `focus_land`, `zoom_land`, `motion_land`, `caption_y_land`, `cards_land`, `puppets_land`), and the same inside a card (`y_land`, `x_land`, `text_land`).

**Layout per orientation** (type size is 1080 px-based in both, so the look is identical):
| | Vertical 9:16 | Horizontal 16:9 |
|---|---|---|
| Captions (approved style: heavy white/colour text with brown stroke) | 84% of the width, `caption_y` default 0.67 (specs use 0.8: above the Shorts UI) | smaller type (7.4% of the height), at most 60% of the width, lower center, `caption_y_land` default 0.84, kept inside a 5% margin |
| Title and fact cards | width 84%, `y` default 0.62 | fact card 50% of the width in the upper third (`y_land` default 0.30), title at 0.42; clamped inside a 5% margin |
| Paper TV graphics (`{"type":"paper"}`) | scaled by width | scaled by height; `y` clamped to 0.12-0.58 (above the captions), lower-thirds left of center (`x` 0.3) unless `x_land`/`y_land` are given |
| Particles, steam, hearts, reel, suck | sized by the width | sized by the height (same pixel size as vertical) |
Test layout without any art: `python3 make_episode.py specs/episode-01-v4.json out/test.mp4 --both --preview` (placeholders for missing stills, center crops for missing `_land` stills; `out/` is git-ignored).

## Spec format (per shot)
`img`, `dur` (minimum; extends automatically to fit the voice), `motion` (`zoom_in|zoom_out|pan_left|pan_right|pan_up|pan_down|static`),
`zoom`, `focus [x,y]`, `lines [{who,text,at?,caption?}]` (who: boy|uncle|grandma|dad|narrator), `sfx [{t,name,d?,gain?}]`,
`fx [{type: steam|hearts|flash}]`, `shake [{t,d,amp}]`, `cards [{type: title|fact,...}]`,
`ambience` (shop|street|water|night), `mood` (cozy|tender|sparse|adventure|tension|epic|off), `transition` (fade|cut).

## Making the pictures
Frames are generated in Canva (character reference images keep the Boy and the Uncle consistent; see `production/character-bible.md`),
placed one per page in a 1080x1920 Canva design and exported as PNG.

## v2 "living animation" options (all optional; old specs render as before)
Tuned for the soft round cartoon look: light grain, warm grades, bright flashes. See `specs/demo-v2.json` for every option in use.

**Shot-level**
- `punch: [{t, scale}]`: smash zoom at `t` (e.g. 1.15) that eases out fast (~0.14 s time constant).
- `speedlines: {t, d, dir: "radial|horizontal", color?: "dark"}`: animated, flickering lines (white by default, `"dark"` for brown). A list of these is also accepted.
- `impact: {t, amp?, dark?}`: hit-stop (camera freezes 0.12 s), white flash with a brief dark beat, radial burst lines, shake. Plays the `impact` sfx automatically.
- `whip: true`: the transition into this shot is a ~0.15 s horizontal whip-pan with motion blur (plays `swoosh_big` automatically).
- `particles: {type: dust|embers|petals|steam|snow, n}`: soft depth-layered drifting sprites.
- `rays: true`: soft diagonal light rays that slowly sweep.
- `grade: warm|cool|sepia|none`: gentle colour grade.
- `layers: {bg, fg}`: two-plane parallax. `fg` is a PNG with alpha that moves ~2x faster than `bg` (`bg` defaults to `img`).
- `ease: linear|in|out|inout`: camera easing (default is the original smoothstep). `sway: 0-1`: handheld micro-sway (also settable globally).

**Global (top level of the spec)**
- `grain: true` (subtle animated film grain), `vignette: 0-1`, `sway: 0-1`.
- `snap_to_beat: true`: every shot duration is rounded to the nearest half-beat of the current mood's tempo, so cuts land on the beat (never shorter than the voice needs). Moods: cozy/tender/sparse 96 BPM, adventure 120, tension 90, epic 110. The music bar grid restarts at a mood change.
- `voice_pitch: {"boy": 1.22}`: override a voice's pitch (the old chipmunk boy of episode 1).

**Music moods** (set per shot with `mood`): `adventure` (taiko, plucked koto arpeggio, breathy flute lead), `tension` (low drone + ticks), `epic` (big drums, rising pad); plus `cozy`, `tender`, `sparse`, `off`.
**New SFX**: `impact`, `riser` (`d` = length), `taiko`, `swoosh_big`, `crack`, `gong`.
**Voices**: `narrator` (bm_george, calm, deeper); `boy` is now older (pitch 1.08 instead of 1.22).

**Performance**: world effects are built at 1/2 to 1/6 resolution and upscaled; sprites and masks are cached. Preview of the 36 s demo takes well under a minute.

## Puppet (cut-out) animation: `puppets` shot option
Characters are transparent PNG cut-outs in `specs/puppets/<name>.png` (boy, uncle, grandma), drawn over the shot background (`img`) and moving with the camera. Optional sidecar `<name>.json` is the "rig": `skin` colour, `eyes [[x,y,w,h],..]` (for blinking), `mouth {x,y,w,h,patch,up}` (for talking), all in cut-out pixels. See `specs/puppet-demo.json`.

```
"puppets": [{"who":"uncle", "img":"uncle.png", "x":0.66, "y":0.95, "scale":0.85, "flip":false,
  "enter":"left|right|bottom|pop|none", "enter_t":0, "enter_d":0.45, "exit":"left|right|bottom", "exit_t":2.0,
  "idle":{"breathe":1, "bob":0.5, "sway":0.6},
  "blink":true, "talk":{"line":"auto"},
  "mouth":[{"t":0.1,"d":0.9,"level":5,"jitter":true}],
  "hit":[{"t":1.2,"squash":0.2,"hop":0.5,"tilt":3}],
  "path":[{"t":0,"x":0.6},{"t":1.5,"x":0.4}], "shadow":true}]
```
- `x`,`y`: feet position as a fraction of the background; `scale` 1.0 = 60% of frame height (boy ~0.65, uncle ~0.85, grandma stall ~0.9).
- `talk`: mouth follows the voice amplitude; `"line":"auto"` = every line whose `who` matches, or a line index. `mouth` = manual open/close timeline (level 0-5) for screams, laughs, steam toots.
- `hit`: damped squash-and-stretch spring (+ optional `hop`, `tilt`). `idle`: breathing, bob, sway multipliers.
- Shot option `caption_y` (default 0.67) moves the burned-in caption so it does not cover faces (puppet shots use 0.8).
- Needs the puppet files only (no extra Canva frames): new episodes = backgrounds + spec.

## Rig animation (v4 test): `rig/`
Skeletal 2D animation of the approved art (no GPU, no paid tool). See `production/v4/video-tech.md`.
```
pip install opencv-python-headless        # plus the packages above
python3 rig/split_parts.py                # cut specs/puppets/*.png into parts -> specs/rigs/<name>/
python3 rig/rigdemo.py out/rig-test.mp4   # 10 s test: walk-in, sniff, gesture, catch, chew, run-off (voices + sfx included)
```
`rig/rig.py` = part hierarchy + procedural face (eyes, brows, mouth, pseudo-3D head turn); `rig/street.py` = perspective street background;
`rig/rigdemo.py` = the timeline (keyframes in code).

## AI clips: `clip` shot type
A shot can be a video clip (for example from the free-GPU notebook in `gpu/`, see `gpu/README.md`) instead of a still:
`{"clip": "c01.mp4", "trim": [0.4, 4.2], "speed": 1.0, "loop": false, "clip_audio": 0.8}` plus all the usual shot options (`lines`, `sfx`, `punch`, `speedlines`, `impact`, `cards`, `grade`, `transition`, ...).
Clips are looked up in `clips_dir` (spec key, default `clips`), then `frames_dir`, then next to the spec; absolute paths work. The horizontal render uses `<name>_land.mp4` (see "Both formats"). `dur` defaults to the trimmed length, the last frame is held if the shot is longer (or `loop`), and no automatic camera move is added (`motion` defaults to `static`). Specs without `clip` render exactly as before.

## V4 episode: paper-cut code clips + animatic with automatic AI-clip upgrade
`specs/episode-01-v4.json` is the full 2:00 edit of Episode 1 V4 (29 clips C01-C29, script `scripts/episode-01-v4.1.md`). It is generated by `paper/build_spec_ep01v4.py` (timing check included).
- **CODE clips** (`paper/`): `python3 -m paper.render [C03 C04 ...]` renders MP4s to `out/ep01v4/code/` (`--sheet x.png` writes a contact sheet instead). `--landscape` writes `Cxx_land.mp4` (1920x1080), `--both` writes both; the spec's `"clip": "../out/ep01v4/code/C03.mp4"` then finds `C03_land.mp4` for the horizontal render automatically. The horizontal clips are **re-composed from the finished vertical frame** (`land_compose` in `paper/clips.py`: the sharp frame as a center column, the sides continue its backdrop from its own edge columns, soft shadow); a clip with a wide layout of its own overrides `Clip.frame_land(t, ts)` (returns a 1920x1080 image), and `land_zoom` / `land_focus(t)` crop the column when a vertical clip should be punched in. The paper TV graphics (`paper/cards.py`) render natively in both aspect ratios. Procedural paper-cut art (PIL/numpy/OpenCV): `core.py` (paper textures, cut-paper sprites with rim + shadow, easing, ffmpeg writer), `shapes.py` (Uncle doll, camel, ships, buns, seal...), `worlds.py` (ink-wash map, desk, skyline), `clips.py` / `clips2.py` (C03 map and caravan, C04 Qinglong port, C06 journal, C07 title, C18 seal + tear + dawn village, C19 hero + jelly, C21 asterisk, C22 fun fact, C24 handwriting glow, C27I route south). Legend/map clips are stepped at 8 fps; cards and graphics are smooth.
- **TV graphics** (`paper/cards.py`): shot card `{"type":"paper","kind":"lower|intermission|safety|fineprint|step|rating|recap|next|word", "t","d","y",...}` (lower-third can flip text at `flip_t`; `in: slam|pop|slide_down`; `slide_t` slides it out).
- **AI-clip fallback**: a shot with `clip` + `img` + `fb {...}` plays `clips/ep01v4/Cxx.mp4` when it exists, otherwise the still `img` with the motion in `fb` (so the episode always renders; real clips take over automatically). `frames_fallback` names a folder of temporary stills (`paper/make_placeholders.py`); real stills in `frames_dir` win.
- **New shot keys**: `reverse`, `freeze [{t,d}]` (8-frame look-to-lens hold), `on_twos` (e.g. 12), `black` (black lead-in), `fade_out`, `impact_frame {t,d}` (white flash then flat posterized red frame with burst lines), fx `reel` (film-reel rewind), fx `suck` (steam into a point). Spec keys: `caption_y` (default caption height), `narrator_echo`. Line keys: `speed`, `pitch`, `gain`, `echo`. More SFX in `sfx_extra.py` (stamp, scratch, snore, sniff, rewind, elevator, camel_bell, rooster, chop, ...).
- **GPU clips**: `gpu/ep01v4/` (clips.json, README, install script).
