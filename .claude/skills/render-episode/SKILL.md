---
name: render-episode
description: Write the episode JSON spec and render the episode MP4 locally (neural voices, synthesized music and sound effects, captions, camera moves), then verify and send it to the user for approval. Use after frames exist.
---

# Render an episode

1. Make sure the Kokoro model exists in `tools/episode_maker/tts/` (see `tools/episode_maker/README.md` for the two curl commands) and `pip install kokoro-onnx soundfile scipy pillow numpy` (needs ffmpeg).
2. Copy `tools/episode_maker/specs/episode-01.json` to `episode-NN.json` and fill the shots from the script: `img`, `dur`, `motion`, `lines` (who: boy|uncle|grandma|dad), `sfx`, `fx`, `shake`, `cards`, `ambience`, `mood`. Use `frames_dir: "frames/epNN"`. Target total 1:50-2:10.
3. Check timing quickly: `python3 make_episode.py specs/episode-NN.json out/preview.mp4 --preview` (about 40 s). Extract a few frames with ffmpeg and look at captions, cards, characters.
4. Full render in the background: `nohup python3 make_episode.py specs/episode-NN.json out/episode-NN.mp4 > out/render.log 2>&1 &` (about 5 min), watch with Monitor for "done".
5. Verify with ffprobe (1080x1920, duration, audio present). Make a lighter copy for sharing: `ffmpeg -i out/episode-NN.mp4 -c:v libx264 -crf 24 -c:a copy -movflags +faststart out/episode-NN-share.mp4`.
6. Send `episode-NN-share.mp4` to the user with SendUserFile and ask for approval. Never upload to YouTube. Commit the spec (the MP4 and frames are git-ignored) and push.
