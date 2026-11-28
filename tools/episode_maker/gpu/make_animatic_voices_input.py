#!/usr/bin/env python3
"""GPU tts input for the animatic lines of Episode 1 and 2 (v5) with the FINAL Qwen3 VoiceDesign cast (voice_casts.json "v5").

    python3 make_animatic_voices_input.py [name]     -> inputs/<name> (default animatic-voices-v5), 43 lines, 1 variant, ~4 GPU minutes
Job file (NOT pushed yet, other GPU work may be running):
    {"run_id": "animatic-voices-v5-001", "task": "tts", "input": "tools/episode_maker/gpu/inputs/animatic-voices-v5", "backend": "qwen3", "smoke": false, "only": "", "max_minutes": 12}
Result: dumpling_out/qwen3/audio/<ep>__<clip>.wav -> copy to tools/episode_maker/out/animatic-v5/gpu-voices/, then
    python3 animatic/voices.py render && python3 animatic/render.py ep01 && python3 animatic/render.py ep02
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
EM = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(EM, "animatic"))
import voice_samples_lib as L
from lines import LINES
CAST = json.load(open(os.path.join(EM, "voice_casts.json")))["v5"]
VOICES = {who: {"qwen_voice": L.QWEN_DESIGNS[who][CAST[who]["qwen3_design"] - 1], "exaggeration_scale": 1.0} for who in ("boy", "uncle", "grandma", "narrator")}
BRISK = " Natural, brisk comedic timing like real quick talk, no long pauses, no sing-song."


def style(who, kind, text, o):
    g, sp = o.get("gain", 0.0), o.get("speed", 1.0)
    if who == "narrator":
        return L.QWEN_STYLE["excited"] if g >= 3 else L.QWEN_STYLE["solemn"]
    if g >= 3:
        return L.QWEN_STYLE["laugh"] if who == "uncle" else L.QWEN_STYLE["excited"]
    if o.get("st", 0) >= 3:
        return L.QWEN_STYLE["tiny"]
    if g <= -2 or sp <= 0.92:
        return L.QWEN_STYLE["tender"]
    return L.QWEN_STYLE["host"] if who == "boy" and text.endswith("!") else L.QWEN_STYLE["neutral"]


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "animatic-voices-v5"
    out = os.path.join(HERE, "inputs", name); os.makedirs(out, exist_ok=True)
    lines = []
    for ep, ls in LINES.items():
        for c, who, kind, text, o in ls:
            lines.append({"id": f"{ep}__{c}", "who": who, "text": o.get("tts", text), "clip": c, "style": "neutral", "qwen": style(who, kind, text, o) + BRISK})
    json.dump({"defaults": {"backend": "qwen3", "seed": 21, "variants": 1}, "voices": VOICES, "lines": lines},
              open(os.path.join(out, "tts.json"), "w"), indent=1, ensure_ascii=False)
    print(len(lines), "lines ->", out)
