#!/usr/bin/env python3
"""Builds the input folder of the GPU "tts" task (tts.json + refs/*.wav) from an episode spec or the 6 test lines.

    python3 make_tts_input.py --lines ../voice_test_lines.json --out inputs/voice-test
    python3 make_tts_input.py --spec ../specs/episode-01-v4.json --out inputs/ep01v4-voices

Line ids are tts_engines.line_key(who, text), the same name make_episode.py looks for when the cast preset is "gpu".
Reference clips (Chatterbox voices) are SYNTHETIC: the production Kokoro voice of each character reading a neutral sentence
(never a recording of a real person). Run it on the machine that has the Kokoro model (tools/episode_maker/tts).
"""
import argparse, json, os, sys
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import tts_engines as te      # noqa: E402

# Orpheus built-in voices per character (unverified guesses: audition with --backend orpheus and change here)
ORPHEUS = {"boy": "leo", "uncle": "dan", "grandma": "tara", "dad": "dan", "narrator": "zac"}
SCALE = {"boy": 1.0, "uncle": 1.15, "grandma": 1.1, "dad": 0.8, "narrator": 0.8}   # emotion multiplier per character
STYLE_BY_WHO = {"narrator": "solemn", "uncle": "excited", "grandma": "excited", "boy": "host", "dad": "tender"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec"); ap.add_argument("--lines"); ap.add_argument("--out", required=True)
    ap.add_argument("--backend", default="chatterbox")
    a = ap.parse_args()
    lines = []
    if a.lines:
        for ln in json.load(open(a.lines))["lines"]:
            lines.append(dict(ln, id=te.line_key(ln["who"], ln["text"]), name=ln["id"]))
    if a.spec:
        spec = json.load(open(a.spec))
        seen = set()
        for sh in spec["shots"]:
            for ln in sh.get("lines", []):
                k = te.line_key(ln["who"], ln["text"])
                if k not in seen:
                    seen.add(k)
                    lines.append(dict(id=k, who=ln["who"], text=ln["text"], style=ln.get("style") or STYLE_BY_WHO.get(ln["who"], "neutral")))
    if not lines:
        sys.exit("give --spec or --lines")
    import make_episode as me          # production cast, pitch shifts, trimming
    me.CACHE = "/tmp/dumpling_tts_refs_cache"
    me.set_cast({})
    os.makedirs(os.path.join(a.out, "refs"), exist_ok=True)
    voices = {}
    for who in sorted({ln["who"] for ln in lines}):
        w = me.tts(who, te.REF_TEXT)
        sf.write(os.path.join(a.out, "refs", f"{who}.wav"), signal.resample_poly(w, 24000, me.SR), 24000, subtype="PCM_16")
        voices[who] = {"ref": f"refs/{who}.wav", "exaggeration_scale": SCALE.get(who, 1.0), "orpheus_voice": ORPHEUS.get(who, "tara")}
    job = {"defaults": {"backend": a.backend, "seed": 7, "variants": 2}, "voices": voices, "lines": lines}
    json.dump(job, open(os.path.join(a.out, "tts.json"), "w"), indent=1, ensure_ascii=False)
    print(f"{len(lines)} lines, {len(voices)} voices -> {a.out}")


if __name__ == "__main__":
    main()
