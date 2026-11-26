---
name: make-episode-v4
description: Produce a full-motion Dumpling Boy episode (v4.4 pipeline) end to end on the free Kaggle GPU via GitHub Actions - stills, voices, AI clips, opening song, render in 9:16 and 16:9 plus mobile files. Use for any new episode or a re-cut.
---

# Make an episode (v4.4 full-motion pipeline)

Read first: `CLAUDE.md`, `production/v4/PRODUCTION-BIBLE.md` (all decisions; "v4.4 DIRECTIVES" and the later rules override older docs), `tools/episode_maker/gpu/README.md`, `production/v4/motion-tech.md`, `production/v4/voice-tech.md`.

1. **Script**: write `scripts/episode-NN-v4.4.md` in the format of `scripts/episode-01-v4.4.md` (clip table with START/END keyframes, ACTION + expressions, VOICE with [delivery notes], SFX, CAPTION ZONE; total incl. opening under 3:00). Anime-comedy for adults + learning: 4 sourced facts + 1 legend (scroll + epic Narrator), Uncle fat and comically ridiculous (never weight jokes), Boy dry witty host, local teacher character, "For dumpling research!", "Dad was right...". Send the creator a Hebrew reading copy (scratchpad).
2. **GPU jobs** (Kaggle T4 x2, ~30 h/week, max 2 sessions): write an input folder under `tools/episode_maker/gpu/inputs/<name>/`, set `tools/episode_maker/gpu/jobs/run.json` (`run_id` unique, `task` images|tts|clips|music), commit, rebase onto origin and push. Results arrive on branch `gpu-results/<run_id>/` (`git fetch origin +gpu-results:refs/remotes/origin/gpu-results`). Log GPU minutes in `production/v4/gpu-ledger.md`.
   - stills: backend `klein` (FLUX.2 klein 4B), refs = locked characters (Uncle: gpu-results/intro-v3 `*__v2.png`), style "soft watercolor anime", orientations portrait+landscape; pick variants from the contact sheets; regenerate any with text/glitches.
   - voices: Qwen3-TTS VoiceDesign (`tts` task), 2-3 takes, pick by duration/levels.
   - clips: backend `ltx98d`, gen_fps 12, start+end keyframes, "camera stays completely still" in the prompt. KNOWN BUG: RIFE corrupts every 2nd frame - set post.rife 0 or install with `select='not(mod(n\,2))',setpts=N/12/TB,fps=24`. Check every clip for stripes and AI text before use.
3. **Render**: build the spec (pattern: `tools/episode_maker/paper/build_spec_ep01v44.py`), then `python3 make_episode.py specs/<spec>.json out/<name>.mp4 --both`; make mobile files with ffmpeg at ~780 kbps (720x1280 / 1280x720, under 20 MB).
4. **QA**: duration < 3:00, contact sheet (Read tool), striped-frame scan, audio levels, captions never over faces/hands/food, no placeholders. Then send both mobile files to the creator in chat. Never upload or publish.
