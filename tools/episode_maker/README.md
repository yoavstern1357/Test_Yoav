# Episode Maker

Builds a ~2-minute vertical episode video from a JSON spec, with **no paid video service**:

- **Voices:** Kokoro neural TTS (open model, runs locally; cast in `VOICES`)
- **Music + sound effects + ambience:** synthesized from scratch (`synth.py`), so nothing is licensed or sampled
- **Picture:** Ken Burns camera moves, crossfades, burned-in captions, fun-fact cards, steam/hearts/flash effects
- **Output:** 1080x1920 H.264 + AAC, loudness-normalized for Shorts

## Setup (once)
```
pip install kokoro-onnx soundfile scipy pillow numpy
mkdir tts && cd tts
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```
(also needs `ffmpeg`)

## Use
```
python3 make_episode.py specs/episode-01.json out/episode-01.mp4            # full quality
python3 make_episode.py specs/episode-01.json out/preview.mp4 --preview     # fast low-res check
python3 make_episode.py specs/episode-01.json out/episode-01.mp4 --mobile   # also writes out/episode-01-mobile.mp4
```
`--mobile`: 720x1280, H.264 Main, crf 27, AAC 128k mono, faststart.
Frames (the 1080x1920 PNGs, one per shot) live in `specs/frames/ep01/` and are named in the spec (`img`).

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
