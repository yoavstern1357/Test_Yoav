# GPU ledger (Kaggle)

| run_id | task | GPU minutes (approx) | date |
|---|---|---|---|
| ep01v43-stills-001 | images (klein, 129 images, both orientations) | 30 | 2026-11-25 |
| ep01v43-voices-001 | tts (qwen3 VoiceDesign, 50 lines x 2 takes) | 18 | 2026-11-25 |
| ep01v43-voices-002 | tts (qwen3, brisk pace, 3 takes) | 25 | 2026-11-25 |
| ep01v43-stills-fix-001 | images (klein, 40 images) | 10 | 2026-11-25 |
| ep01v43-clips-A-001 | clips (LTX 2B, 30 steps, 16 clips x 2 orientations, 1 variant) | running (est. 160) | 2026-11-25 |
| ep01v43-clips-B-001 | clips (LTX 2B, 30 steps, 13 clips x 2 orientations, 1 variant) | running (est. 140) | 2026-11-25 |
| motion-compare-001 | clips (R&D: LTX 0.9.5 vs LTX 0.9.8 13B-distilled nf4 vs Wan2.2 5B vs FastWan, 16 clips portrait) | planned about 90 per GPU x 2 (measured value to be filled in) | 2026-11-25 |
| opening-song-001 | music (ACE-Step, bf16 decoder failed, no audio) | 33 | 2026-11-25 |
| opening-song-002 | music (ACE-Step v1 3.5B, 8 tracks x 2 seeds, 60 s + 16 s) | running (est. 35) | 2026-11-25 |
| motion-compare-001 | measured: 2 GPUs x about 35 min (16 clips, 4 failed: Wan base worker killed by CPU RAM) | about 70 | 2026-11-25 |
| motion-compare-002 | clips (LTX 0.9.8d tuning, 8 clips, measured) | about 35 (2 GPUs x 17 min) | 2026-11-25 |
| ep01v44-voices-001 | tts (qwen3, 50 lines x 2 takes) | planned about 25 | 2026-11-25 |
| ep01v44-stills-001 | images (klein, 64 keyframes x 2 orientations, 1 variant) | planned about 40 | 2026-11-25 |
| ep01v44-voices-fix-001 | tts (qwen3, 8 lines x 4 takes) | planned about 12 | 2026-11-25 |
| ep01v44-stills-001 | measured: 128 keyframes about 50 min wall | about 50 | 2026-11-25 |
| ep01v44-voices-001 / -fix-001 | measured about 25 + 8 | about 33 | 2026-11-25 |
| ep01v44-stills-fix-001 | images (klein, 22 items x 2 variants, re-rolls) | planned about 20 | 2026-11-25 |
| ep01v44-stills-fix-001 | measured about 25 | about 25 | 2026-11-26 |
| ep01v44-clips-001 | clips (ltx98d, 8 steps, gen 12 fps + RIFE + ESRGAN, 39 clips x 2 orientations, 1 variant) | planned about 45 (two T4) | 2026-11-26 |
| charsheets-v45-001 | images (klein, 42 single-character sheets at 1536x864: turnaround/expressions/hands/mouths, old designs; superseded by the redesign decision) | about 28 (2 GPUs x 14 min session) | 2026-11-26 |
| charsheets-v5-s1-001 | images (klein, 19 single-character concept candidates 768x1344/768x960: Boy A-polished, Uncle bold bald/curled mustache, Grandma master) | planned about 9 T4-min (about 5 min wall on T4 x2 + start-up) | 2026-11-28 |
| voice-samples-001 | tts (qwen3 VoiceDesign 25 designs x 4 lines [capped 9.5 min], chatterbox 10 refs x 4 lines [3 min], orpheus 4 voices x 4 lines [3.5 min]; free voice samples for the creator) | planned about 20 (1 session, caps per engine) | 2026-11-28 |
