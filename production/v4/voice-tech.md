# V4 voice tech: the best free, safe, commercial voices

Author: voice engineer. Date: 2026-11-25. Status: CPU engines installed and compared here; GPU engine implemented but **not run** (no GPU, huggingface.co blocked).

## 1. Verdict in six lines
1. **Highest quality, free, commercial-safe: Chatterbox (Resemble AI, MIT, safetensors) on the free Kaggle GPU**, one batch job per episode (about 5 to 15 min). Each character's voice is a short reference clip that WE synthesize (never a real person). Emotion is set per line (`exaggeration`, `cfg_weight`). Alternates: Chatterbox-Turbo (MIT, inline `[laugh]` tags) and Orpheus 3B (8 built-in voices, inline `<laugh>` `<sigh>` tags; license text to be checked, see 3).
2. **Best that runs HERE on CPU today: still Kokoro-82M (Apache-2.0)** as the default. Two newer CPU engines are installed beside it and can be switched on per episode or per character: **Supertonic-2** (10 built-in synthetic voices, about 6 to 20x real time, OpenRAIL-M) and **Pocket TTS** (Kyutai, CC-BY-4.0, about real time, needs a synthetic reference clip). They are not clearly better than Kokoro; the creator should listen to the comparison file (section 5) and decide.
3. **Honest limit:** nothing here was judged by ear. The ranking below uses public model cards and reports plus simple pitch metrics (`out/voice-test/metrics.txt`). The GPU engines were not run at all.
4. Weights only come from hosts this container can reach (GitHub releases, PyPI). huggingface.co is blocked, so the GPU job downloads from Hugging Face inside Kaggle's own session.
5. All integration is backwards compatible: with no config, `make_episode.py` renders exactly the same Kokoro audio as before (checked sample by sample against the previous version).
6. No voice cloning of real people anywhere: Supertonic = built-in synthetic voices; Pocket and Chatterbox = reference clips synthesized by Kokoro; Orpheus = built-in voices. Real-person sample clips shipped in a model package were deleted.

## 2. Options table (open-weight TTS, 2025-2026)
"Run" = where it can run for us. "Ear" = my expectation from model cards and reports, not tested. Verified = I read the license file or the code in this session.

| Model | Weights license | Commercial YouTube | Safe format | Emotion control | Voices | Run | Verdict |
|---|---|---|---|---|---|---|---|
| **Chatterbox** 0.5B (Resemble AI) | MIT (code and weights) | Yes | safetensors + one `conds.pt` loaded with `weights_only=True` (verified in the package code) | `exaggeration`, `cfg_weight` per line | reference clip (we synthesize it) | GPU (T4 fine); CPU too slow | **PICK (GPU primary)** |
| Chatterbox-Turbo 350M | MIT | Yes | safetensors | inline tags `[laugh] [chuckle] [sigh]...` | reference clip (needs > 5 s) | GPU | Alternate, faster |
| **Orpheus 3B ft** (Canopy Labs) + SNAC | Declared Apache-2.0; base is Llama 3.2 so its terms ("Built with Llama") may apply. Sources conflict, **read the model card first** | Probably yes | model safetensors; SNAC 24 kHz is a `.bin` (we force `weights_only=True`) | inline `<laugh> <sigh> <gasp>...` | 8 built-in voices, no cloning | GPU (3B, about real time on a T4) | Alternate (cleanest "no cloning" story) |
| **Kokoro-82M** | Apache-2.0 | Yes | ONNX (GitHub release) | none (speed only) | 54 built-in | CPU, about 2 to 4x real time | **Keep as CPU default** |
| **Supertonic-2** 66M (Supertone) | OpenRAIL-M (use-based restrictions, commercial allowed; the packaged LICENSE is only the MIT sample code, read the model license on its card) | Yes | ONNX int8 (GitHub release) | none | 10 built-in synthetic | CPU, about 6 to 20x real time | **Installed, optional** |
| **Pocket TTS** 100M (Kyutai) | CC-BY-4.0 weights (verified in the package README), MIT/Apache code | Yes, credit "Kyutai Pocket TTS" in the description | ONNX int8 (GitHub release) | none (style follows the reference clip) | reference clip only | CPU, about real time | **Installed, optional** |
| Maya1 3B (Maya Research) | Apache-2.0 (per search results) | Yes | safetensors + SNAC `.bin` | 20+ inline emotion tags, voice from a text description | designed voices | GPU | Interesting, but reviews say descriptions are often ignored and voices drift between lines; not chosen |
| Dia 1.6B (Nari Labs) | Apache-2.0 | Yes | safetensors | non-verbal tags | random unless a prompt clip is given | GPU 10 GB | Voice not stable between lines; rejected for a series |
| Sesame CSM-1B | Apache-2.0 | Yes | safetensors, gated download | context based | needs audio context | GPU | Gated + inconsistent identity; rejected |
| Parler-TTS Mini/Large v1 | Apache-2.0 | Yes | safetensors | text description ("a warm man, slow") | named speakers | GPU | Older quality, artifacts; fallback only |
| Zonos v0.1 (Zyphra) | Apache-2.0 | Yes | safetensors | emotion sliders | cloning-centric | GPU 8 GB+ | Not needed |
| StyleTTS2 | MIT code, weights trained on LJSpeech/LibriTTS | Yes | `.pth` pickles | style vector | few | CPU/GPU | Pickle weights, flat; rejected |
| MeloTTS / Piper voices | MIT / voice-dependent (Piper code is now GPL-3) | Mixed | ONNX | none | many | CPU | Flatter than Kokoro; rejected |
| VibeVoice (Microsoft) | MIT | Yes | safetensors | none | Realtime-0.5B has presets; the larger models were restricted after misuse reports | GPU | Unclear availability; rejected |
| Higgs Audio v2 (Boson AI) | Community license (limits for large user counts) | Doubtful | safetensors | good | cloning | GPU 24 GB | Rejected: license |
| IndexTTS2 | Custom license, commercial use needs permission | No | | strong | cloning | GPU | Rejected: license |
| F5-TTS / E2 | **CC-BY-NC** weights | No | | | cloning | | **Rejected (non-commercial)** |
| XTTS-v2 | **CPML** non-commercial | No | pickle | | cloning | | **Rejected** |
| Fish Audio S2, Voxtral TTS | research / **CC BY-NC** | No | | | | | **Rejected** |

Why Chatterbox over the others: MIT is the cleanest license of the expressive models; the package code loads only safetensors (and `conds.pt` with `weights_only=True`); it holds one identity per reference clip across a whole series (Dia, CSM and Maya1 do not); emotion has an explicit knob. Its cost: it needs a GPU, and every output carries an inaudible Resemble "PerTh" watermark (harmless, but known).

## 3. Licenses and credits to keep
- **Chatterbox / Turbo:** MIT. No credit needed. Keep the repo name and commit hash from `results.json` in `production/` notes.
- **Kokoro:** Apache-2.0, no credit needed.
- **Pocket TTS:** CC-BY-4.0, so put "Voice: Kyutai Pocket TTS (CC BY 4.0)" in the episode sources list if it is used.
- **Supertonic:** OpenRAIL-M: allowed for commercial use, but forbids harmful uses (impersonation, deception...) and the restrictions pass to whoever receives the model. We only make cartoon characters, so this is fine; read the license file once before the first monetized upload.
- **Orpheus:** read the model card of `canopylabs/orpheus-3b-0.1-ft` before use. If it shows the Llama 3.2 license, commercial use is allowed but "Built with Llama" must appear with the video sources.
- Open question for the creator: YouTube asks creators to disclose realistic synthetic voices in some cases. Our voices are clearly cartoon voices, but check the current upload form wording before the first upload.

## 4. Cast per character
Default today (unchanged): Kokoro, as `VOICES` in `make_episode.py`.

| Character | Kokoro (default) | Supertonic preset (`voice_engine: "supertonic"`) | Pocket preset | GPU: Chatterbox reference (synthetic) | Orpheus voice |
|---|---|---|---|---|---|
| Boy (10-12, warm, curious) | `am_puck`, pitch 1.08 | voice 5 (lightest male), pitch 1.12 | ref `am_puck`, pitch 1.08 | Kokoro boy clip, style "host" | leo (guess) |
| Uncle (big, warm, funny) | `am_michael`, 0.92 speed, pitch 0.90 | voice 8, speed 0.95, pitch 0.94 | ref `am_michael`, pitch 0.92 | Kokoro uncle clip, emotion scale 1.15 | dan (guess) |
| Grandma | `af_sarah`, 0.92 speed | voice 4 (lowest female), speed 0.95 | ref `af_sarah` | Kokoro grandma clip, scale 1.1 | tara (guess) |
| Scroll Narrator (deep, solemn) | `bm_george`, 0.90 speed | voice 6 (deepest male), speed 0.9 | ref `bm_george` | Kokoro narrator clip, style "solemn", scale 0.8 | zac (guess) |
| Dad (journal reading) | `bm_daniel` | voice 9 | ref `bm_daniel` | same as Boy reading, scale 0.8 | dan |
The Orpheus voice names are unverified guesses: audition the 8 voices once (change `orpheus_voice` in `tts.json`, run `--backend orpheus --only 01,03,05,06`).
Supertonic voice numbers 0-4 are female and 5-9 male (from measured pitch: 138 to 211 Hz median for 0-4 versus 86 to 138 Hz for 5-9).
Narrator echo stays a post effect in `make_episode.py` (`narrator_echo`), independent of the engine.

## 5. What was rendered and measured here (4 CPUs)
Output: `tools/episode_maker/out/voice-test/` (git-ignored). **Comparison file: `out/voice-test/comparison.m4a`** (also `.mp3`); `comparison.txt` lists the timestamps. For each of 6 lines (Boy x2, Uncle x2, Grandma, Narrator) it plays Kokoro (1 beep), Supertonic (2 beeps), Pocket TTS (3 beeps). Per-engine WAVs are in `out/voice-test/<engine>/`.

| Engine | Real-time factor (render time / audio) | Pitch range of the lines (10-90 percentile, semitones; wider = livelier, a rough proxy only) |
|---|---|---|
| Kokoro | 0.2 to 0.7 | 8 to 12 |
| Supertonic-2 | 0.05 to 0.17 | 6 to 15 |
| Pocket TTS | 0.7 to 2.5 (about 1 on long lines) | 4 to 19 |
An episode (about 100 s of speech) costs Kokoro roughly 30 s, Supertonic 10 s, Pocket TTS 2 to 3 min. The GPU batch (45 lines of episode 1) is estimated at 5 to 15 min on a T4 for Chatterbox; **estimates, not measurements**.

## 6. How to use it
- **Switch a whole episode:** in the spec add `"voice_engine": "supertonic"` (or `"pocket"`, `"gpu"`), or set env `VOICE_ENGINE`. Override one character: `"voice_cast": {"uncle": {"engine": "supertonic", "sid": 9}}`. Presets: `tools/episode_maker/voice_casts.json`. No key = Kokoro, exactly as before.
- **Install the CPU engines:** `pip install sherpa-onnx` then `sh tools/episode_maker/fetch_voice_models.sh` (GitHub only).
- **Compare again:** `python3 tools/episode_maker/voice_test.py` (add `--engines kokoro,gpu --gpu-dir <folder of WAVs>` to include the GPU render).
- **GPU job (not triggered):** `python3 tools/episode_maker/gpu/make_tts_input.py --spec tools/episode_maker/specs/episode-01-v4.json --out tools/episode_maker/gpu/inputs/ep01v4-voices` (already generated, 45 lines, 2 takes each), then put `{"run_id": "ep01v4-voices-001", "task": "tts", "input": "tools/episode_maker/gpu/inputs/ep01v4-voices", "backend": "chatterbox", "smoke": true, "max_minutes": 60}` in `gpu/jobs/run.json` (first run with `smoke: true`, then `false`). Unzip the WAVs into `tools/episode_maker/tts/gpu/` and render with `"voice_engine": "gpu"`. A line that was not rendered fails loudly (no silent fallback). Take 1 is `<id>.wav`, take 2 is `<id>__v2.wav` (copy the better one over `<id>.wav`).
- Listening test first: run the 6-line input `gpu/inputs/voice-test` (smoke run) and compare with `voice_test.py --engines kokoro,gpu`. Only switch the series to the GPU voices if the creator prefers them.

## 7. Risks and what was not tested
- The GPU task has never run: package pins (chatterbox-tts 0.1.7 pins torch 2.6 and transformers 5.2), model repo files and the Orpheus decoding were checked against the package source or from memory only. Expect one fix-up round on the first smoke run.
- The reference-clip route means Chatterbox voices inherit the Kokoro timbre of their reference. If that is too close to the current sound, design new references with Supertonic or Pocket (any synthetic source), or use Orpheus's built-in voices.
- Supertonic/Pocket quality versus Kokoro is unjudged. Pocket TTS with a Kokoro reference mostly changes delivery, not timbre.
- Facts marked "per search results" or "from memory" in section 2 were not re-checked against the model cards (huggingface.co is blocked here). Re-check the license line of the chosen model before the first monetized upload.
