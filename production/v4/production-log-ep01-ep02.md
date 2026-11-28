# Production log: Episodes 1 and 2 (v5, free Kaggle GPU pipeline)

Lead: production sub-agent. Rules: nothing uploaded or published; every GPU job logged in `gpu-ledger.md`; stop and report at 22 GPU-h used in the week.

## Checkpoint 0 (2026-11-28, ~20:55 UTC): preparation while the two GPU sessions run
- Jobs `music-cues-v5-001` (pushed 20:09) and `animatic-voices-v5-001` (pushed 20:17) were both still `in_progress` on GitHub Actions at 20:50 UTC (no `gpu-results` folder yet). Rule kept: no new `run.json` until both finish.
- Stage 2 character-sheet prompts adjusted in `tools/episode_maker/gpu/make_charsheets_v5_input.py`: Uncle jacket "rich EARTH-BROWN (#7A5230), NOT khaki/olive/tan" (+ negative), Grandma jacket "DEEP JADE-GREEN (#2F6B4F), NOT pale sage", Uncle bald, thin curled mustache, never a hat; Boy chin ribbon with two tails, straw sandals (already in the prompt). Input rebuilt: `tools/episode_maker/gpu/inputs/charsheets-v5-s2/` (74 images, refs from `out/charsheets-v5/picks.json`).
