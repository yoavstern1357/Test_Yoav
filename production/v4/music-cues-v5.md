# Music cues v5 (background bed options), prepared 2026-11-28

Creator feedback on the animatic: "I don't like the background music" (the synthesized bed from `synth.py`). Earlier preference: minimal music.

## 1. Done now: animatics without the music bed
`tools/episode_maker/animatic/render.py` no longer mixes the synthesized bed (set `MUSIC_BED=1` to bring it back). Kept: voices, SFX (whoosh, impact, steam, gong, ticks), ambience, the silence beat before the Dad moment, the held tone in Ep 1 C19-C20, and the 7.5 s opening-song sting in Ep 1. Re-rendered (9:16 and 16:9), loudness -14.7 LUFS, `qc_flash.py` PASS on both 9:16 files:
`tools/episode_maker/out/animatic-ep01-v5.mp4`, `animatic-ep02-v5.mp4`, and `-land` versions.

## 2. GPU job (prepared, NOT pushed)
Input: `tools/episode_maker/gpu/inputs/music-cues-v5/music.json` (ACE-Step v1 3.5B, instrumental, lyrics `[inst]`, infer_step 50, 2 seeds 501/502). 12 generations:

| id | length | BPM | style prompt (core) |
|---|---|---|---|
| bed_a_guzheng120 | 36 s | 120 | warm playful folk, plucked guzheng arpeggios, soft woodblock, round bass |
| bed_b_pipa120 | 36 s | 120 | witty light-comedy, pipa + pizzicato, tiny shaker, muted bass |
| bed_c_kalimba90 | 36 s | 90 | calm cozy, kalimba + soft marimba, warm sub bass, brushed percussion |
| bed_d_dizi90 | 36 s | 90 | gentle folk, sparse bamboo flute, guzheng, frame drum, warm pad |
| emotional_dad90 | 20 s | 90 | felt piano + erhu-like strings, no drums (Dad beat) |
| sting_outro3 | 5 s (generator minimum; trim to 3 s) | - | guzheng gloss + woodblock tap, major resolve |

Every bed prompt adds: instrumental, no vocals, sparse, quiet, low dynamics, no big melody, seamless loop. Loop with a 0.5 s crossfade at the end; duck 12-14 dB under voice as in the pace spec.
Estimated GPU time: about 12 s of model load/warm-up aside, roughly 1.2 min per 36 s track x 8 + 0.7 min x 2 + 0.3 min x 2 + ~4 min install/load = about 14 min (estimate scaled from opening-song-002: 35 min for 16 mostly 60 s jobs). Cap `max_minutes` 15; if it hits the cap, the resume logic keeps finished tracks (rerun with `only`).

Exact `tools/episode_maker/gpu/jobs/run.json` to push later (unique run_id; push only when no other GPU job is running):
```
{"run_id": "music-cues-v5-001", "task": "music", "input": "tools/episode_maker/gpu/inputs/music-cues-v5", "backend": "acestep", "smoke": false, "only": "", "max_minutes": 15}
```
Validated with `generate_music.py --dry-run` (12 jobs). Results land on branch `gpu-results/music-cues-v5-001/`. Log the run in `gpu-ledger.md` when pushed.

## 3. Free-music sources (checked from this container)
`freemusicarchive.org`, `incompetech.com` and `pixabay.com` do not resolve here (outside the session network allow-list), so no track could be verified or downloaded and nothing was saved to `out/music-cc0/`. No specific tracks are listed because licenses could not be checked. To enable: allow those hosts in the environment's network settings, then rerun the check. Rules when we do: CC0 needs no credit; CC-BY (e.g. Incompetech/Kevin MacLeod) needs a credit line in the description (title, artist, license, link) and a `LICENSES.md`; avoid anything NC/ND or "content ID" registered. Pixabay Music has its own license (free commercial use, no credit required, not CC0): acceptable but note the license date per track.

## 4. Decision for the creator
Options: (1) no music at all (current animatic), (2) one of the generated beds A-D, (3) a free licensed track. Answer with a letter, or "no music".
