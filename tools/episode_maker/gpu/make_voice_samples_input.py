#!/usr/bin/env python3
"""Builds inputs/voice-samples (tts.json + refs/) for the GPU voice-sample job: Qwen3 VoiceDesign designs, Chatterbox with
synthetic Kokoro reference clips, Orpheus built-in voices. Same 4 lines per character for every voice.

    python3 make_voice_samples_input.py        (needs the Kokoro model in tools/episode_maker/tts)
"""
import json, os, sys
import numpy as np, soundfile as sf, librosa
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import voice_samples_lib as L
OUT = os.path.join(HERE, "inputs", "voice-samples")
TTS = os.path.join(HERE, "..", "tts")
REF_TEXT = ("Welcome, friends. Today we are going to taste something wonderful, so please sit down, "
            "take a deep breath, and listen to the story.")


def main():
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(TTS, "kokoro-v1.0.onnx"), os.path.join(TTS, "voices-v1.0.bin"))
    os.makedirs(os.path.join(OUT, "refs"), exist_ok=True)
    voices, lines = {}, []
    styles = {}
    order = []                                   # design-major order: d1..d4 of every character first, d0 (current default) last
    for d in (1, 2, 3, 4, 0):
        for c in L.CHARS:
            order.append((c, d))
    for c, d in order:
        vid = f"qwen3__{c}__{d + 1}"
        voices[vid] = dict(qwen_voice=L.QWEN_DESIGNS[c][d], backends=["qwen3"])
        for lid, text, style, _ in L.LINES[c]:
            lines.append(dict(id=f"{vid}__{lid}", who=vid, text=text, style=style, qwen=L.QWEN_STYLE[style]))
    for c in L.CHARS:
        for i, (kv, pitch) in enumerate(L.CB_REFS[c]):
            wav, sr = k.create(REF_TEXT, voice=kv, speed=1.0, lang="en-us")
            if pitch != 1.0:
                wav = librosa.effects.pitch_shift(wav, sr=sr, n_steps=12 * np.log2(pitch))
            wav = librosa.resample(wav, orig_sr=sr, target_sr=24000)
            rp = f"refs/{c}_{i + 1}.wav"
            sf.write(os.path.join(OUT, rp), wav, 24000, subtype="PCM_16")
            vid = f"chatterbox__{c}__{i + 1}"
            voices[vid] = dict(ref=rp, backends=["chatterbox"])
            for lid, text, style, _ in L.LINES[c]:
                lines.append(dict(id=f"{vid}__{lid}", who=vid, text=text, style=style))
    for c in ["uncle", "narrator", "grandma", "host"]:
        for i, ov in enumerate(L.ORPHEUS_CAST[c]):
            vid = f"orpheus__{c}__{i + 1}"
            voices[vid] = dict(orpheus_voice=ov, backends=["orpheus"])
            for lid, text, style, _ in L.LINES[c]:
                ln = dict(id=f"{vid}__{lid}", who=vid, text=text, style=style)
                if (c, lid) in L.ORPHEUS_TEXT:
                    ln["text_orpheus"] = L.ORPHEUS_TEXT[(c, lid)]
                lines.append(ln)
    job = {"defaults": {"backend": "qwen3", "seed": 21, "variants": 1}, "voices": voices, "lines": lines}
    json.dump(job, open(os.path.join(OUT, "tts.json"), "w"), indent=1, ensure_ascii=False)
    print(len(voices), "voices,", len(lines), "lines ->", OUT)


if __name__ == "__main__":
    main()
