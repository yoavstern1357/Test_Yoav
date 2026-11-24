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
```
Frames (the 1080x1920 PNGs, one per shot) live in `specs/frames/ep01/` and are named in the spec (`img`).

## Spec format (per shot)
`img`, `dur` (minimum; extends automatically to fit the voice), `motion` (`zoom_in|zoom_out|pan_left|pan_right|pan_up|pan_down|static`),
`zoom`, `focus [x,y]`, `lines [{who,text,at?,caption?}]` (who: boy|uncle|grandma|dad), `sfx [{t,name,d?,gain?}]`,
`fx [{type: steam|hearts|flash}]`, `shake [{t,d,amp}]`, `cards [{type: title|fact,...}]`,
`ambience` (shop|street|water|night), `mood` (cozy|tender|sparse|off), `transition` (fade|cut).

## Making the pictures
Frames are generated in Canva (character reference images keep the Boy and the Uncle consistent; see `production/character-bible.md`),
placed one per page in a 1080x1920 Canva design and exported as PNG.
