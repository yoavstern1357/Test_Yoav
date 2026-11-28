# Animatic report: Episode 1 and Episode 2 (v5 scripts), CPU only

Date 2026-11-28. Status: first watchable animatic for **timing, pace and voice**, NOT final quality. No GPU, no paid service, nothing uploaded or published. Files are local and git-ignored.

## 1. Files
| What | Path |
|---|---|
| Episode 1, 9:16, 720x1280, 24 fps | `tools/episode_maker/out/animatic-ep01-v5.mp4` (4.1 MB) |
| Episode 2, 9:16, 720x1280, 24 fps | `tools/episode_maker/out/animatic-ep02-v5.mp4` (3.7 MB) |
| 16:9 bonus (1280x720, same cut) | `...animatic-ep01-v5-land.mp4` (3.1 MB), `...animatic-ep02-v5-land.mp4` (2.9 MB) |
| Per-line wav + word timestamps (git-ignored) | `tools/episode_maker/out/animatic-v5/voices/ep0N/<clip>.wav/.json` |
| Timeline + word times (committed, 40 KB) | `production/v4/animatic-v5-timing.json` |
| Code | `tools/episode_maker/animatic/` (`lines.py`, `voices.py`, `shots.py`, `art.py`, `render.py`) |

Rebuild: `python3 animatic/voices.py render` then `python3 animatic/render.py ep01` (and `ep02`, `--land`). The shot list is read from `scripts/episode-0N-v5.md` (PACE, CUTS, TRIM, MICRO, card and badge times, SFX column, caption zone), so a script edit flows through.

## 2. Durations (hard max 75 s)
| | Planned (script) | Animatic | Shots | Sub-shots (cuts incl.) | Average shot length | Words spoken |
|---|---|---|---|---|---|---|
| Episode 1 | 74.0 s | **70.96 s** | 26 | 59 | 1.20 s (spec premiere 1.2-1.7) | 108 |
| Episode 2 | 69.5 s | **67.00 s** | 24 | 46 | 1.46 s (spec normal 1.5-2.2, slightly fast) | 113 |

Rule used: shot length = lead (0.20 fast / 0.28 medium / 0.45 calm) + voice + reaction beat (0.30 / 0.40 / 0.75 s); silent shots keep their planned or trimmed length; the 7.5 s opening (C21-C23, K01) is fixed. Special beats: Episode 1 C11 keeps the 0.3 s comic silence after "don't..."; Episode 2 C11 ends with a 1.0 s tail so the one deliberate silence (about 0.7 s of true silence for music, SFX and ambience) sits right before the Dad beat. Both episodes pass without speeding any voice up.

## 3. Voices (CPU only, natural speed)
Engines available and tried: Kokoro, Supertonic-2, Pocket TTS, (Piper from the sample round). Speed multiplier is never above 1.0 (lines use 0.9-1.0 of the engine base, never above 1.1); pitch shift only through the voice ratios: Boy +1.65 semitones, Uncle -1.4, Grandma -1.4, Narrator -2.2.

| Character | Chosen | Why |
|---|---|---|
| Boy | Kokoro `bf_lily`, pitch x1.10 | best proxy score of 4 candidates (word error 0.07 on the sample lines, F0 203 Hz, lively range); the smallest shift needed to sound light, so the fewest processing artefacts. `af_heart` x1.20 is higher (244 Hz) but needs a bigger shift and had 2x the word error here; `am_puck` is too low; Pocket TTS follows a reference well but is real-time slow and had the largest pitch jitter. |
| Uncle | Kokoro `bm_lewis`, pitch x0.92 | deepest warm Kokoro voice (F0 about 86 Hz), clearest of the deep ones (word error 0.12); `am_fenrir` and `am_michael` are higher and mumbled more; Supertonic 8 had 0.32 error. |
| Grandma | Kokoro `bf_isabella`, x0.92, speed 0.95 | clearest adult female (word error 0.095, F0 195 Hz, calm); `af_sarah` is brighter, `bf_emma` lower and flatter. |
| Narrator | Kokoro `bm_fable`, x0.88, speed 0.92-0.95 | storyteller timbre, slow, different from the Uncle (`bm_lewis`). Supertonic 9 won the proxy score (deepest) but mis-spoke "Legend" ("Limp says") and runs at only 1.2 words/s, which would blow the 3.5 s hook and the 6.5 s legend slot (K04 would take 7.2 s instead of 5.2 s). The extra -1 semitone shift that was first used made "Defeated" unintelligible ("To feed us"), so the Narrator now has no extra shift. |

Candidate scores (first 8 lines per character, Whisper small.en word error, YIN pitch; proxies only, nobody has listened):

| Character | Candidate | Word error | F0 Hz | Range (st) | Jitter (st) | Words/s | Score |
|---|---|---|---|---|---|---|---|
| boy | kokoro af_heart x1.20 | 0.151 | 244 | 16.4 | 2.26 | 2.89 | -0.016 |
| boy | kokoro am_puck x1.12 | 0.29 | 142 | 8.2 | 1.74 | 3.32 | -1.3 |
| boy | pocket ref am_liam x1.2 | 0.098 | 190 | 20.8 | 4.4 | 0.75 | -1.396 |
| boy | kokoro bf_lily x1.10 | 0.071 | 203 | 13.7 | 2.04 | 2.43 | 0.251 |
| uncle | kokoro bm_lewis x0.90 | 0.119 | 86 | 14.8 | 3.11 | 2.29 | -0.549 |
| uncle | kokoro am_fenrir x0.90 | 0.19 | 130 | 18.1 | 2.85 | 3.01 | -0.909 |
| uncle | supertonic 8 x0.94 | 0.315 | 118 | 9.3 | 1.65 | 1.54 | -0.674 |
| uncle | kokoro am_michael x0.90 | 0.194 | 115 | 19.9 | 3.06 | 2.52 | -0.878 |
| grandma | kokoro af_sarah x0.96 | 0.19 | 189 | 13.4 | 1.8 | 2.83 | 0.092 |
| grandma | kokoro bf_isabella x0.92 | 0.095 | 195 | 9.0 | 2.17 | 2.67 | 0.316 |
| grandma | pocket ref af_sarah | 0.238 | 162 | 14.5 | 2.01 | 2.38 | -0.496 |
| grandma | kokoro bf_emma x0.90 | 0.137 | 167 | 8.0 | 2.28 | 2.76 | -0.259 |
| narrator | kokoro bm_fable x0.88 | 0.168 | 107 | 15.2 | 2.63 | 1.55 | -0.386 |
| narrator | kokoro bm_george x0.90 | 0.25 | 131 | 10.9 | 0.97 | 1.7 | -0.29 |
| narrator | supertonic 9 x0.90 | 0.108 | 82 | 9.2 | 1.38 | 1.16 | 0.476 |
| narrator | kokoro bm_lewis x0.85 | 0.05 | 101 | 23.0 | 4.68 | 1.73 | -0.942 |

Delivery notes (all by synthesis settings, no acting engine on CPU): the catchphrase lines get +1 semitone and +3 dB; the Uncle's tiny wheeze +3 semitones and -3 dB; the Boy's last "Dad was right..." speed 0.9 and -6 dB (a whisper by level only); the Narrator's "LEGEND SAYS!" +3 dB. Spoken respellings used to steer pronunciation: "Nan-shyang" and "Gwahng-joh" (captions keep the real spelling), numbers as words ("eighteen seventy-one", "nine").
Intelligibility after synthesis (Whisper re-read of the final lines): 33 of 43 lines at word error 0.0-0.17 (31 exact). The rest are known false alarms of the checker or real small risks: "Nanxiang" heard as "Nenshiong" / "Nanshong" (C02 in both episodes), British "stall" heard as "stole" (Narrator, Ep1 C04), "Three... two..." returned as digits (fine), "Steam melts it back into soup" -> "in a soup" (Uncle V.O.), "I'm not sitting" -> "seeing" (Ep2 C04, whispered line), "Pork skin" -> "Port skin" (Ep1 C07). Candidates for a re-take with a different respelling: Ep1 C02 and Ep2 C02 (name), Ep1 C07, Ep2 C04.

## 4. Word timestamps
No forced aligner exists on this CPU and the Whisper build here returns no token times, so each line is aligned by **syllable-weighted proportional timing inside the trimmed voice, with boundaries snapped to the quietest 10 ms frame within +-70 ms** and punctuation pauses weighted (ellipsis 1.6, full stop 0.9, comma 0.5). Expected accuracy about +-80 ms per word: good enough for word-pop captions at 2.2 words/s and for cutting punches on word starts (cuts within 0.45 s of a planned time snap to the nearest word start), not good enough for lip sync. Whisper confirms the text of every line (see `asr` in the timing json). Averages: 108 words in Episode 1 (mean word 0.36 s), 113 words in Episode 2 (mean 0.35 s). Complete times: `production/v4/animatic-v5-timing.json`.

## 5. Lines that run long against the script's slot (and what to cut)
The animatic total still fits (the shorter lines pay for the longer ones), but these shots are longer than the script planned:
| Clip | Line | Voice | Needed vs planned slot | Suggested trim (never speed up) |
|---|---|---|---|---|
| Ep1 C01 (hook) | Defeated... by ONE tiny dumpling. | 3.06 s (the Narrator speaks 1.6 words/s) | hook 3.96 s vs 3.5 s planned (+0.46 s, shifts the opening) | "Defeated... by one dumpling." (saves about 0.35 s) or start the voice 0.2 s earlier under the gong |
| Ep1 C02 | Welcome to Nanxiang, soup dumpling town! | 2.74 s | 3.22 vs 3.0 (+0.22) | "Welcome to Nanxiang, dumpling town!" or drop the place card overlap |
| Ep1 C05 | It's just a stall. | 1.65 s | 2.13 vs 2.0 (+0.13) | fine, absorbed |
| Ep1 K03 | LEGEND SAYS! | 1.65 s (two words, 1.2 words/s) | 2.13 vs 1.5 (+0.6) | keep: it is the grand beat; shorten the scroll wipe K03 instead of the word |
| Ep2 C01 (hook) | Nobody sits on that stool. Nobody. | 2.85 s | 3.33 vs 3.0 (+0.33) | "Nobody sits on that stool." (saves 0.8 s) if the second "Nobody" is not essential for the joke |
| Ep2 C08 | Then perish quietly. | 1.59 s | 2.07 vs 2.0 (+0.07) | fine |
All other lines fit their slot. The Narrator is the slowest voice (1.2-1.6 words/s against the spec's 1.9): it is the first thing to replace when GPU voices exist.

## 6. Picture, captions, sound
- **Pictures:** flat storyboard cards in the CLAUDE.md palette (cream, leaf yellow, orange, peach, brown): shot id, who is on screen as a simple icon (Boy hat, bald Uncle with mustache, Grandma bun, Dad from behind, camel, hands, dumpling), the script's action text, the caption-zone guide, and (inside the bottom 480 px that a phone UI covers) the spoken line, SFX and EDIT text. **No stand-in stills were used:** the v5 characters (Uncle B, new Grandma) were redesigned and the v4.x stills would mislead about the look.
- **Cut rhythm:** every `CUTS` entry becomes a sub-shot: punch (zoom 1.15), reaction crop (1.30), insert card (peach card with the script's insert note), code card; a 4-frame bump at each cut; slow push 1.00 to 1.05-1.08 inside each; hard cuts only; 2-frame flat cream impact frames where the script says IMPACT or FLASH (hook, K01, K02). Place card, fact card, badge and end card appear at the script's times.
- **Captions:** word-pop in step with the voice, 1-3 words per pop, cream text with brown outline and the current word in leaf yellow; BOTTOM zone centred at 64 % of the height, bottom edge asserted <= 75 % of the height (the 1440/1920 rule), TOP zone shots at 19 %. 16:9 captions at 80 %.
- **Timer and shot id** top-left, pace badge and speaker tag (with animated bars) top-right: animatic only.
- **Sound:** Episode 1's opening uses `out/opening-song-variants/flac/intro_b__s212.flac` (style 2 male sting, the standing placeholder) for the first 7.5 s from C21 with a 0.25 s fade, music and ambience muted, SFX at half level. SFX come from `synth.py` / `sfx_extra*.py` chosen by keywords in the SFX column (thunder, gong, whoosh, hiss, chop, splash, crunch, chomp, shing, toot, creak, bell, page, sip, ...) plus a tick/pop/thud on every cut and on every hard cut into a shot (within 10 ms). Music is the synth placeholder bed (cozy 96 BPM, adventure 120 BPM for the hubris/legend beats, tender and sparse for the calm beats, off for the hook, the cliffhanger and the camel). Held tone under Episode 1 C19-C20. Music and ambience duck 13 dB under voice (attack 80 ms, release 250 ms). Silence beats: Ep1 after "don't..." (0.36 s), Ep2 before the Dad beat (about 0.7 s).
- **Loudness:** both files measure **-14.7 LUFS integrated**, true peak <= -1.5 dBTP (ffmpeg loudnorm, dynamic mode; not exactly -14 because a linear pass would exceed the peak ceiling), LRA 4 LU.
- **QC:** `qc_flash.py` PASS on both (max 1.0 and 0.5 general flashes per second, no red flashes). `ffprobe`: 720x1280, 24 fps, H.264 + AAC, durations 70.96 s and 67.00 s, audio present.

## 7. Weaknesses (be honest)
1. Nobody has listened. All voice choices come from Whisper word error, pitch statistics and the earlier sample report; the Boy is a pitch-shifted adult voice and may sound processed or too female. The creator's ears decide.
2. Word timing is approximate (+-80 ms); captions may be slightly early or late on fast words; punches are placed on word starts but not on stressed syllables.
3. The Narrator is slow and slightly stiff; Kokoro cannot act (no volcanic shout, whisper or tiny wheeze: only gain and pitch tweaks).
4. The opening sting is the style-2 placeholder cut to 7.5 s with a fade; its lyric hits were not re-aligned to the script's 0.33 s beat grid or to the cuts (the cuts follow the script's times, not the music).
5. Cards show who is in the shot, not the acting: gag timing that depends on facial acting (the deadpan hold, the swelling Uncle, the eyebrow) cannot be judged yet. The 8 fps paper-cut legend is shown as four text cards.
6. SFX and music are the simple synthesized kit; some SFX (chomp, crack, thunder) are weak, and keyword matching puts each SFX at a fixed spot in its shot, not on the exact frame of the action.
7. Average shot length in Episode 2 is 1.46 s, just under the normal 1.5-2.2 s band, because the lines are short: acceptable for the first test, check on the retention curve.
8. Loudness is -14.7, not -14.0.

## 8. What is blocked on the GPU (Kaggle blocked)
- All real pictures: START/END stills (FLUX.2 klein), the 22 + 23 AI clips (LTX), the paper-cut scroll renders, character model sheets use.
- Final voices: Qwen3-TTS VoiceDesign (the only candidate designed to sound like a 7-year-old), Chatterbox/Orpheus acting variants, per-line takes; then re-time the cut on those voices (the shot lengths are computed from the voice files, so the cut re-flows automatically).
- Lip-sync / mouth overlay on `lipsync` rows, and any final-quality music (ACE-Step song cut to the 7.5 s sting).
- What can still be done on CPU now: replace slow lines per section 5, re-take the four lines at the end of section 3 with new respellings, hand-tune caption timing, add the Hebrew captions only if the creator wants them (deliverables stay English).


## 9. Update 2026-11-28 (late): v5 voice cast chosen, GPU render of the animatic lines pending
The creator called the CPU voices "completely robotic". The Qwen3 voices of `voice-samples-002` won (see `voice-samples-report.md` section 7; cast in `voice_casts.json` key `v5`). The animatic LINES cannot be rendered with them on this machine (Qwen3-TTS needs a GPU and a download from huggingface.co, which is blocked here, and torch is not installed), and no GPU job was pushed (another GPU job owns `jobs/run.json`). Ready to go, nothing else to code:
1. `python3 tools/episode_maker/gpu/make_animatic_voices_input.py` (done, `gpu/inputs/animatic-voices-v5/tts.json`: 43 lines, 4 Qwen3 designs, one delivery style sentence per line, about 4-6 GPU minutes).
2. Push `gpu/jobs/run.json`: `{"run_id": "animatic-voices-v5-001", "task": "tts", "input": "tools/episode_maker/gpu/inputs/animatic-voices-v5", "backend": "qwen3", "smoke": false, "only": "", "max_minutes": 12}`.
3. Copy `dumpling_out/qwen3/audio/<ep>__<clip>.wav` to `out/animatic-v5/gpu-voices/`, then `python3 animatic/voices.py render` (it now picks the GPU wavs automatically; `VOICE_SRC=cpu` forces the old voices), `python3 animatic/render.py ep01`, `... ep02`. Shot lengths re-flow from the voice files. Music stays off (`MUSIC_BED=1` brings it back).
**Expected trims with the Qwen3 pace (predicted from the sample lines, Grandma about 2.0 words/s and the Narrator about 2.3 words/s are slower than the Kokoro voices; Boy 2.8 and Uncle 2.1 are close):** Ep1 C01 "Defeated... by one dumpling." (drop TINY); Ep1 C06 "Everyone asks. We make it solid." ; Ep1 K04 "In 1871, a shop made its bun tiny. Jelly inside!" ; Ep2 C01 "Nobody sits on that stool." (drop the second Nobody); Ep2 C06 "The waiting seat. Eighteen folds." ; Ep2 C14 "He waited all afternoon." The per-line numbers will be measured after the render; the existing section 5 trims still apply.
