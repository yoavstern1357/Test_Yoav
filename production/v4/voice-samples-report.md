# Free voice samples: report for the creator's listening test (2026-11-28)

Author: voice engineer agent. Scope: as many FREE, commercially usable voices as possible, with the same 4 lines per character, to listen to and choose from.
**Honest limit: nobody here can listen.** Quality notes below are ear PROXIES only (a Whisper ASR re-read of every line gives a word-error rate = intelligibility; pitch median and pitch range = livelier or flatter; words per second = speed; peak and clipping). They cannot say whether a voice is charming, a good child, or funny. **The final judgement is the creator's ears.**

## 1. What was made and where
- Audio: `tools/episode_maker/out/voice-samples/` (git-ignored, not in the repo). One file per voice: `samples/<model>__<character>__<n>.mp3` (4 lines, loudness-normalised to -18 LUFS). Characters: `boy`, `uncle`, `grandma`, `narrator`, `host` (= the Boy's voice-over host tone).
- One compilation per character: `compare-boy.m4a`, `compare-uncle.m4a`, `compare-grandma.m4a`, `compare-narrator.m4a`, `compare-host.m4a` (3 to 6 MB each, 7 to 11 minutes; a plain Kokoro voice says "Number 7. Pocket T T S, voice 2." and then the sample). `INDEX.md` / `index.tsv` map the NUMBER to the file, model, licence and metrics.
- Sample script (identical for every voice): Boy "Wait, the soup is inside the dumpling? How?" / "Uncle, no! That is MY dumpling!" (outburst) / "I think Dad stood right here, a long time ago." (soft) / "Hello! I am the Dumpling Boy, and today we taste a legend."; Uncle "For dumpling research!" (outburst) / "There was soup inside." / "I smell... destiny. And a little bit of ginger." / "Little one, a good meal is a good friend. Come, sit." (soft); Grandma "Everybody asks. We never pour it in. First we turn it into jelly." / "Hah! Too hot? I did tell you, my dear." (teasing) / "Your father sat right there. He was very patient." (soft) / "Eight folds, no more, no less. Watch my fingers."; Narrator "Legend says, in a small shop, one very large bun." / "Many people believe it was the best bun in all the land." / "And so the hungry traveler walked on, toward the next town." (soft) / "Behold! The Great Bun of Nanxiang!" (grand outburst); Host "Welcome back to the Silk Road. Today, one dumpling, one big question." / "Wait for it... here comes the steam!" / "Dad was right. The best part is always the part you wait for." (soft) / "Let's go find out!".
- Code: `tools/episode_maker/gpu/voice_samples_lib.py` (lines + the 25 Qwen3 design prompts), `gpu/make_voice_samples_input.py` (GPU job input), `run_cpu_samples.py` (CPU engines), `build_compilations.py` (import GPU results, metrics, mp3, compilations, index).
- Counts: CPU sets rendered here: 150 (Kokoro, Supertonic, Pocket TTS, KittenTTS, Piper voices); GPU sets in this build: 0.
- GPU job `voice-samples-001` (Qwen3 VoiceDesign 25 designs, Chatterbox 10 reference voices, Orpheus 4 voices; per-engine time caps 9.5 / 3 / 3.5 min, one session, about 20 GPU minutes planned, logged in `gpu-ledger.md`). **STATUS: the job was pushed at 12:29 UTC and was still running / queued 80 minutes later (the character-sheet job was running on the other GPU session at the same time; the runner waits for a free Kaggle session). Its results were NOT in this build. When the run finishes (results land in branch `gpu-results`, folder `voice-samples-001/`), run: `git fetch origin gpu-results; git archive origin/gpu-results voice-samples-001/dumpling_out | tar -x -C /tmp/vs; python3 -I tools/episode_maker/build_compilations.py import-gpu /tmp/vs/voice-samples-001/dumpling_out; python3 -I tools/episode_maker/build_compilations.py metrics; python3 -I tools/episode_maker/build_compilations.py build` and the Qwen3 / Chatterbox / Orpheus voices are added to every compilation (numbers shift: Qwen3 comes first).**


## 2. Method of the ear-proxy checks
1. Whisper `small.en` (MIT, via sherpa-onnx, CPU) transcribes each of the 4 lines; word error rate against the script text. 0.00 = every word understood; above 0.25 = clearly mispronounced words or a mumbling voice (the ASR itself is imperfect on names such as "Nanxiang" and "dumpling research", so compare voices with each other, not with zero).
2. Pitch (YIN) median and 10-90 percentile range in semitones. A wide range suggests acting, a narrow range a monotone; octave errors can inflate it (for example `piper-joe`), so treat extreme values with suspicion.
3. Words per second of speech (normal 2.5 to 3.5; the Narrator should be slower).
4. All files peak-limited and loudness-matched, so louder never means better.

## 3. Every candidate: licence, commercial use, how it was handled

"Licence" is what the model card / MODEL_CARD / repo says as far as this session could read it (huggingface.co and most GitHub repo pages are blocked in this container; the Kaggle job and the sherpa-onnx release tarballs carry the model cards; web search gave secondary sources for the others). **Read the exact licence file once before the first monetised upload.** "Tested" = samples exist in this round.

| Model | Weights licence | Commercial OK? | Tested | Voices / emotion control | Where it ran | Note |
|---|---|---|---|---|---|---|
| **Qwen3-TTS 1.7B VoiceDesign** | Apache-2.0 | Yes | 25 designs (5 per character, d0 = current default) | voice from a text prompt, style sentence per line | Kaggle T4, about 2.5 s of GPU per second of audio | current default; the only candidate that is DESIGNED to sound like a 7-year-old |
| **Chatterbox 0.5B** (Resemble AI) | MIT | Yes (inaudible PerTh watermark; one blog claims the project was retired in 2026, the weights stay MIT) | 10 voices | reference clip (a synthetic Kokoro clip here), `exaggeration` and `cfg_weight` per line | Kaggle T4, about 1 s per second of audio | here "a Kokoro voice with Chatterbox acting" |
| **Orpheus 3B ft** (Canopy Labs) | declared Apache-2.0, built on Llama 3.2 ("Built with Llama" may apply); official repo is gated, the ungated mirror is used | Probably yes, read the card | 4 voices (dan, zac, tara, leo) | 8 built-in adult voices, inline tags `<laugh> <chuckle> <gasp>` | Kaggle T4, about 3.5 s per second of audio | no child voice exists |
| **Kokoro-82M v1.0** | Apache-2.0 | Yes | 30 sets | 54 built-in voices, speed only (we add pitch shift) | CPU here, real time x2 to x4 | cleanest and most intelligible, flat acting |
| **Supertonic-2 (66M)** | OpenRAIL-M (commercial allowed, use-based restrictions) | Yes | 15 sets | 10 built-in voices | CPU here, 6 to 20x real time | very fast |
| **Pocket TTS (Kyutai, 100M)** | CC-BY-4.0 (credit "Kyutai Pocket TTS" in the description) | Yes with credit | 10 sets | follows a reference clip (synthetic Kokoro clip) | CPU here, about real time | most expressive of the CPU engines by pitch range |
| **KittenTTS v0.8 mini / nano** | Apache-2.0 | Yes | 20 sets | 8 built-in voices | CPU here | tiny; highest word error here; the sherpa build skips some phoneme symbols |
| **Piper voices** (VITS, run with onnxruntime + espeak) | per voice dataset, see section 3b | only the voices of 3b | 13 voices of 13 datasets, 85 sets | speakers; speed; our pitch shift | CPU here, 5x real time | LibriTTS-R has 904 and VCTK 109 speakers: only a pitch-selected few rendered |
| Dia 1.6B (Nari Labs) | Apache-2.0 | Yes | no (GPU budget) | `[S1]/[S2]` dialogue + non-verbal tags; random voice unless a prompt clip is given | 10 GB GPU | rejected earlier: no stable identity between lines |
| Zonos v0.1 (Zyphra) | Apache-2.0 | Yes | no (GPU budget) | emotion sliders, cloning-centric | 8 GB+ GPU | possible next round |
| Sesame CSM-1B | Apache-2.0 (needs gated Llama-3.2-1B) | Yes | no (gated, needs audio context) | context based | GPU | |
| Kyutai TTS 1.6B (en/fr) | sources conflict (CC-BY 4.0 vs CC-BY-SA); the voices repo is CC-BY 4.0 | probably, verify | no | built-in voice embeddings | GPU | Pocket TTS (same lab) tested instead |
| Maya1 3B | Apache-2.0 per search results | Yes | no (GPU budget) | voice from a text description + about 20 inline emotion tags | GPU | strongest untested rival of Qwen3 VoiceDesign: first candidate for a second GPU round |
| Parler-TTS mini/large v1 | Apache-2.0 | Yes | no | text description of the voice | GPU | older quality |
| VibeVoice 1.5B / Realtime-0.5B (Microsoft) | MIT on paper; the 1.5B repo was disabled / removed in 2025-26 and the card discourages commercial use | avoid | no | | | status unclear |
| Higgs Audio v2 / v3 (Boson) | community licence; v3 "non-commercial" | No / doubtful | no (reason: licence) | | | skipped |
| F5-TTS / E2-TTS | code MIT, weights CC-BY-NC | No | no (reason: non-commercial weights) | | | skipped |
| XTTS-v2 | CPML non-commercial | No | no (reason: non-commercial) | | | skipped |
| Fish Audio S2 / OpenAudio | CC-BY-NC-SA / paid licence | No | no (reason: non-commercial) | | | skipped |
| IndexTTS2 / 2.5 | custom "Bilibili" licence | No / unclear | no (reason: licence) | | | skipped |
| Step-Audio-EditX | contested (Apache-2.0 vs a research licence) | unclear | no | emotion editing | | verify before any use |
| Spark-TTS | CC-BY-NC-SA weights | No | no (reason: non-commercial) | | | skipped |
| Piper `hfc_female`, `hfc_male`, `ryan` | CC BY-NC(-SA) (MODEL_CARD) | No | no (reason: non-commercial) | | | skipped |
| Piper `lessac`, `amy`, `alan`, `danny`, `kusal`, `jenny_dioco`, `northern_english_male` | "see URL" / Blizzard licence / CC-BY-SA | unclear | no (reason: dataset licence not verified or share-alike) | | | skipped |

### 3b. Piper voices rendered (licence copied from each MODEL_CARD)
LibriTTS-R, VCTK, ARU, ALBA: CC BY 4.0 (credit the dataset in the video sources if one is chosen). Cori, Kristin, LJ Speech, Norman, Bryce: public domain. Joe, Kathleen: CC0. Sam: Apache-2.0. Arctic: CMU Arctic (permissive, see its LICENSE file). These are voices of real volunteer readers whose recordings were published for this kind of reuse; **we clone nobody**, but each sounds like a real adult. None is a child, so the Piper "Boy" and "host" samples are adult voices pitch-shifted up and will sound artificial.

## 4. Results by model and character (ear proxies, not ears)

### Model summary (all rendered sets)

| Model | Sets | ASR word error (mean) | Pitch range, semitones (mean) | Words/s |
|---|---|---|---|---|
| kokoro | 30 | 0.04 | 11.7 | 3.2 |
| piper-libritts_r | 15 | 0.16 | 9.7 | 4.2 |
| piper-vctk | 15 | 0.33 | 7.4 | 3.6 |
| piper-aru | 10 | 0.22 | 9.0 | 3.2 |
| piper-arctic | 10 | 0.12 | 5.5 | 3.1 |
| piper-alba | 3 | 0.10 | 8.1 | 3.1 |
| piper-cori | 3 | 0.19 | 8.3 | 2.8 |
| piper-joe | 1 | 0.02 | 29.0 | 3.3 |
| piper-kathleen | 3 | 0.09 | 7.3 | 3.0 |
| piper-kristin | 3 | 0.12 | 9.1 | 2.7 |
| piper-ljspeech | 3 | 0.16 | 14.4 | 2.8 |
| piper-norman | 3 | 0.23 | 17.0 | 2.9 |
| piper-bryce | 3 | 0.09 | 15.0 | 2.4 |
| piper-sam | 3 | 0.10 | 5.3 | 3.1 |
| kitten-mini | 10 | 0.28 | 10.4 | 2.9 |
| kitten-nano | 10 | 0.34 | 10.2 | 2.7 |
| supertonic | 15 | 0.09 | 10.6 | 2.4 |
| pocket | 10 | 0.07 | 12.6 | 2.9 |

### Best proxy scores: Boy

| File | No. in compare-boy | ASR error | Median pitch Hz | Range st | Words/s | Voice detail |
|---|---|---|---|---|---|---|
| kokoro__boy__3 | 3 | 0.05 | 234 | 18.3 | 3.41 | af_heart |
| supertonic__boy__1 | 7 | 0.04 | 146 | 18.1 | 2.38 | 5 |
| pocket__boy__2 | 11 | 0.02 | 207 | 17.8 | 3.18 | ref:am_liam@1.2 |
| kokoro__boy__6 | 6 | 0.02 | 129 | 13.4 | 3.17 | am_echo |
| supertonic__boy__2 | 8 | 0.15 | 100 | 13.0 | 2.5 | 6 |
| kokoro__boy__2 | 2 | 0.06 | 143 | 12.3 | 3.59 | am_liam |
| kokoro__boy__5 | 5 | 0.04 | 199 | 11.7 | 3.29 | bf_lily |
| kokoro__boy__4 | 4 | 0.0 | 193 | 10.8 | 3.3 | af_sky |

### Best proxy scores: Uncle

| File | No. in compare-uncle | ASR error | Median pitch Hz | Range st | Words/s | Voice detail |
|---|---|---|---|---|---|---|
| piper-joe__uncle__1 | 21 | 0.02 | 93 | 29.0 | 3.32 | 0 |
| supertonic__uncle__3 | 9 | 0.08 | 82 | 14.5 | 2.29 | 6 |
| piper-bryce__uncle__1 | 20 | 0.03 | 111 | 14.4 | 2.36 | 0 |
| kokoro__uncle__5 | 5 | 0.0 | 90 | 14.1 | 2.93 | bm_lewis |
| kokoro__uncle__4 | 4 | 0.0 | 120 | 13.9 | 3.42 | am_adam |
| kokoro__uncle__3 | 3 | 0.0 | 126 | 13.2 | 3.59 | am_fenrir |
| pocket__uncle__1 | 10 | 0.06 | 100 | 10.8 | 2.99 | ref:am_michael@0.9 |
| kokoro__uncle__1 | 1 | 0.0 | 109 | 10.7 | 3.14 | am_michael |

### Best proxy scores: Grandma

| File | No. in compare-grandma | ASR error | Median pitch Hz | Range st | Words/s | Voice detail |
|---|---|---|---|---|---|---|
| kokoro__grandma__4 | 4 | 0.06 | 140 | 18.9 | 2.07 | af_nicole |
| pocket__grandma__2 | 11 | 0.11 | 172 | 17.9 | 2.84 | ref:bf_emma@0.9 |
| pocket__grandma__1 | 10 | 0.06 | 169 | 16.8 | 3.03 | ref:af_sarah@0.96 |
| piper-libritts_r__grandma__1 | 25 | 0.14 | 170 | 16.1 | 3.99 | 0 |
| kokoro__grandma__1 | 1 | 0.03 | 185 | 12.9 | 3.27 | af_sarah |
| kokoro__grandma__3 | 3 | 0.03 | 193 | 12.6 | 3.22 | bf_isabella |
| kokoro__grandma__6 | 6 | 0.06 | 142 | 12.5 | 3.45 | af_kore |
| supertonic__grandma__3 | 9 | 0.08 | 163 | 11.2 | 2.28 | 2 |

### Best proxy scores: Scroll Narrator

| File | No. in compare-narrator | ASR error | Median pitch Hz | Range st | Words/s | Voice detail |
|---|---|---|---|---|---|---|
| kokoro__narrator__2 | 2 | 0.1 | 106 | 14.8 | 2.6 | bm_fable |
| kokoro__narrator__3 | 3 | 0.13 | 84 | 12.9 | 2.8 | bm_lewis |
| pocket__narrator__1 | 10 | 0.09 | 102 | 10.7 | 2.87 | ref:bm_george@0.9 |
| pocket__narrator__2 | 11 | 0.08 | 106 | 9.8 | 2.65 | ref:bm_fable@0.86 |
| supertonic__narrator__3 | 9 | 0.04 | 80 | 9.4 | 2.34 | 6 |
| kokoro__narrator__4 | 4 | 0.08 | 100 | 9.3 | 3.26 | am_adam |
| supertonic__narrator__1 | 7 | 0.04 | 84 | 9.1 | 2.01 | 9 |
| kokoro__narrator__1 | 1 | 0.06 | 134 | 8.4 | 2.62 | bm_george |

### Best proxy scores: Boy voice-over host

| File | No. in compare-host | ASR error | Median pitch Hz | Range st | Words/s | Voice detail |
|---|---|---|---|---|---|---|
| piper-norman__host__1 | 29 | 0.02 | 158 | 19.5 | 3.08 | 0 |
| piper-libritts_r__host__1 | 25 | 0.04 | 201 | 17.6 | 4.24 | 0 |
| piper-bryce__host__1 | 21 | 0.06 | 166 | 15.9 | 2.46 | 0 |
| pocket__host__2 | 11 | 0.14 | 139 | 15.6 | 2.93 | ref:am_echo@1.08 |
| piper-ljspeech__host__1 | 28 | 0.1 | 225 | 15.4 | 2.92 | 0 |
| supertonic__host__1 | 7 | 0.06 | 134 | 15.0 | 2.47 | 5 |
| piper-vctk__host__2 | 32 | 0.04 | 214 | 14.9 | 4.24 | 15 |
| kokoro__host__4 | 4 | 0.0 | 133 | 14.3 | 3.37 | am_liam |


## 5. Recommendation (top 3 per character) and what to listen to first
Rule: nothing below is final. It says where to start listening.

| Character | Start with (compilation number is in `INDEX.md`) | Why (proxy only) |
|---|---|---|
| **Boy** (about 7, warm, shy) | 1) Qwen3 designs d1 to d4 (`qwen3__boy__2` to `__5`) 2) `pocket__boy__2` 3) `kokoro__boy__3` | Only Qwen3 is built to sound like a child; of the CPU voices Pocket TTS has a wide pitch range with very low word error, Kokoro af_heart pitched up is the clearest. All CPU boy voices are shifted adult voices. |
| **Uncle** (deep, warm, comic bursts) | 1) Qwen3 d1 to d4 (`qwen3__uncle__2` to `__5`) 2) `kokoro__uncle__5` (bm_lewis) / `kokoro__uncle__3` (am_fenrir) 3) `supertonic__uncle__3` or `piper-joe__uncle__1` | Deep pitch (80 to 125 Hz), zero ASR error, wide range; the outburst line shows whether the voice can go big. |
| **Grandma** (calm, teasing, precise) | 1) Qwen3 d1 to d4 (`qwen3__grandma__2` to `__5`) 2) `kokoro__grandma__1` (af_sarah) / `kokoro__grandma__3` (bf_isabella) 3) `pocket__grandma__1` | Clear voices with a wide range; Pocket follows the Kokoro reference with more acting. |
| **Scroll Narrator** (deep, royal, slow, amused) | 1) Qwen3 d1 to d4 (`qwen3__narrator__2` to `__5`) 2) `supertonic__narrator__3` / `__1` (slowest and deepest) 3) `kokoro__narrator__2` (bm_fable) | Lowest pitch and slow pace; Kokoro bm_fable has the widest range. |
| **Boy voice-over host** | 1) Qwen3 d1 to d4 (`qwen3__host__2` to `__5`) 2) `kokoro__host__4` (am_liam) 3) `pocket__host__1` | Clear, young-sounding and still intelligible. |

Honest limits: (a) no ears were used; (b) Chatterbox and Orpheus as run here do not use a designed voice: Chatterbox copies a synthetic Kokoro reference, Orpheus has only adult voices; (c) Qwen3 voices drift a little between lines (known from the earlier production test), so for a pick the creator should listen for the SAME voice across the 4 lines, not only for the best single line; (d) the pitch-shifted voices are the cheapest to use but will sound processed.

How to use the answer: reply with the character and the compilation number (for example "Boy 12, Uncle 5, Grandma 3, Narrator 9"). The pick is then wired as the cast of that character (`voice_casts.json` for CPU voices, the design prompt in `gpu/inputs/*/tts.json` for Qwen3) and re-listened to inside a real episode line.

## 6. Next candidates if none of these sounds right (not run: GPU budget)
Maya1 (Apache-2.0, voice from text + emotion tags), Zonos, Dia with a short synthetic prompt clip, Qwen3 CustomVoice (9 built-in premium speakers, Apache-2.0, already supported by `generate_tts.py --backend qwen3custom`), Chatterbox with a reference made from the best Qwen3 design (so the child voice is a Qwen3 design with Chatterbox's emotion knob). Each is one more 10 to 15 GPU-minute job.
