# Episode 1 V4: the 19 image-to-video clips

`clips.json` has one entry per I2V clip (C01, C05, C08-C17, C20, C23, C25-C29), 2 variants each, LTX-Video, in BOTH formats: vertical 480x832 -> 720x1280 (`Cxx.mp4`) and horizontal 832x480 -> 1280x720 (`Cxx_land.mp4`), same seeds.
Start images come from `tools/episode_maker/specs/frames/ep01v4/Cxx.png` (C13 also uses `C13_end.png` as its last frame). The horizontal clip takes `Cxx_land.png` (and `C13_end_land.png`) from the same folder when it exists (generate them with the stills task, which makes both orientations), otherwise a center crop of the vertical still. Add `"orientations": ["portrait"]` to a clip to skip the horizontal one.

1. Pack (skips clips whose still has not arrived yet):
   `python3 tools/episode_maker/gpu/pack_inputs.py tools/episode_maker/gpu/ep01v4/clips.json --skip-missing --out tools/episode_maker/out/gpu_input_ep01v4`
   -> `tools/episode_maker/out/gpu_input_ep01v4.zip` (upload as the Kaggle dataset, see `../README.md` section 3).
2. Run `dumpling_clips.ipynb` on Kaggle, download `dumpling_clips.zip`.
3. Install the clips: `python3 tools/episode_maker/gpu/ep01v4/install_clips.py dumpling_clips.zip [--pick C13=2]`
   (copies them to `tools/episode_maker/specs/clips/ep01v4/Cxx.mp4` and `Cxx_land.mp4`, git-ignored; `--pick C13_land=2` picks a variant for one orientation).
4. Re-render both formats: `python3 tools/episode_maker/make_episode.py tools/episode_maker/specs/episode-01-v4.json tools/episode_maker/out/episode-01-v4.mp4 --both --mobile` (writes `episode-01-v4.mp4` 9:16 and `episode-01-v4-land.mp4` 16:9 plus the `-mobile` versions)
   Every clip that exists replaces its still-image fallback automatically; missing clips keep the animatic motion.
Trim points inside each shot (`trim`) assume clips of 4-5 s; adjust them in `tools/episode_maker/paper/build_spec_ep01v4.py` and rebuild the spec if a clip is shorter.
