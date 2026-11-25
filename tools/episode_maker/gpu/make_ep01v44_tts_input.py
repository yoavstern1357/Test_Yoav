#!/usr/bin/env python3
"""GPU tts input for Episode 1 v4.4: every spoken line of scripts/episode-01-v4.4.md that has no pre-rendered take yet (tts/gpu/<key>.wav).
    python3 make_ep01v44_tts_input.py [name]   -> inputs/<name> (default ep01v44-voices)"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "paper"))
import tts_engines as te
from parse_ep01v44 import parse
VOICES = {
 "boy": "A 7-year-old boy with a bright, clear child's voice, quick and dry, a cheeky little deadpan, never shouting unless the note says so, like a witty kid host.",
 "uncle": "A huge, warm, middle-aged man with a deep, rich, theatrical voice, a little husky, operatic and over the top when grand, tiny and wheezy when defeated, quiet and sincere when moved.",
 "grandma": "An elderly woman, a village cook, flat, dry and unimpressed, a little raspy, brisk, kind underneath, never raising her voice.",
 "narrator": "A huge, booming, epic anime-trailer narrator voice, deep and thunderous and theatrical, with slow dramatic pauses.",
}
name = sys.argv[1] if len(sys.argv) > 1 else "ep01v44-voices"
OUT = os.path.join(HERE, "inputs", name)
have = set(os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.path.dirname(HERE), "tts", "gpu"))) if os.path.isdir(os.path.join(os.path.dirname(HERE), "tts", "gpu")) else set()
lines, seen = [], set()
for c in parse():
    for ln in c["lines"]:
        who = "boy" if ln["who"] == "dad" else ln["who"]
        k = te.line_key(who, ln["text"])
        if k in seen:
            continue
        seen.add(k)
        lines.append({"id": k, "who": who, "text": ln["text"], "clip": c["id"], "style": "neutral",
                      "qwen": f"Delivery: {ln['note']}. Natural, brisk comedic timing like real quick talk, no long pauses.",
                      "reuse": k in have})
new = [l for l in lines if not l["reuse"]]
os.makedirs(OUT, exist_ok=True)
json.dump({"defaults": {"backend": "qwen3", "seed": 11, "variants": 2}, "voices": {w: {"qwen_voice": d, "exaggeration_scale": 1.0} for w, d in VOICES.items()},
           "lines": new}, open(os.path.join(OUT, "tts.json"), "w"), indent=1, ensure_ascii=False)
print(len(lines), "lines,", len(new), "new ->", OUT)
