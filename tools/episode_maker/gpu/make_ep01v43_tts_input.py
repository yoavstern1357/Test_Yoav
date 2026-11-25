#!/usr/bin/env python3
"""Builds inputs/ep01v43-voices/tts.json (Qwen3-TTS VoiceDesign): every spoken line of Episode 1 v4.3, delivery note as the style instruction, 2 takes."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "paper"))
import tts_engines as te
from ep01v43_lines import LINES, VOICES
NAME = sys.argv[1] if len(sys.argv) > 1 else "ep01v43-voices"
PACE = len(sys.argv) > 2 and sys.argv[2] == "brisk"
OUT = os.path.join(HERE, "inputs", NAME)
lines, seen = [], set()
for clip, ls in LINES.items():
    for who, note, text in ls:
        k = te.line_key(who, text)
        if k in seen:
            continue
        seen.add(k)
        lines.append({"id": k, "who": who, "text": text, "clip": clip, "style": "neutral", "qwen": f"Delivery: {note}." + (" Brisk, natural conversational pace like real quick talk, no long pauses, keep it flowing." if PACE else "")})
voices = {w: {"qwen_voice": d, "exaggeration_scale": 1.0} for w, d in VOICES.items()}
os.makedirs(OUT, exist_ok=True)
json.dump({"defaults": {"backend": "qwen3", "seed": 7, "variants": 3 if PACE else 2}, "voices": voices, "lines": lines}, open(os.path.join(OUT, "tts.json"), "w"), indent=1, ensure_ascii=False)
print(len(lines), "lines")
