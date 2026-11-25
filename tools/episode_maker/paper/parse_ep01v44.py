#!/usr/bin/env python3
"""Parses the beat tables of scripts/episode-01-v4.4.md into a list of clip dicts (also written to specs/ep01v44_clips.json).
    python3 paper/parse_ep01v44.py
Each clip: id, dur, start (m:ss.t as seconds), method, start_kf, end_kf, action, lines [(who, vo, note, text)], sfx (raw text), zone ("top"|"bottom"), peak."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(ROOT, "..", "..", "scripts", "episode-01-v4.4.md")


def secs(ts):
    m, s = ts.split(":")
    return int(m) * 60 + float(s)


def parse_voice(v):
    out = []
    v = v.strip()
    if not v or v.startswith("(no words") or v.startswith("(none"):
        return out
    for part in re.split(r"\s+/\s+(?=[A-Z]+\b)", v):
        m = re.match(r"([A-Z]+)(?:\s*\((V\.O\.|off|asleep|[^)]*)\))?\s*\[([^\]]*)\]\s*:\s*[“\"](.*?)[”\"]\s*$", part.strip(), re.S)
        if not m:
            raise ValueError(f"cannot parse voice part: {part!r}")
        who = m.group(1).lower()
        out.append(dict(who=who, tag=m.group(2) or "", note=m.group(3).strip(), text=m.group(4).strip()))
    return out


def parse(path=SCRIPT):
    clips = []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\| (C\d\d) \(([\d.]+) s\) \| ([\d:.]+) \| ", line)
        if not m:
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        assert len(c) == 9, (m.group(1), len(c))
        zone = "top" if c[8].upper().startswith("TOP") else "bottom"
        action = c[5].replace("**", "")
        clips.append(dict(id=m.group(1), dur=float(m.group(2)), start=secs(m.group(3)), method=c[2], start_kf=c[3], end_kf=c[4],
                          action=action, lines=parse_voice(c[6]), sfx=c[7], zone=zone, zone_note=c[8], peak="PEAK" in c[5]))
    return clips


if __name__ == "__main__":
    cl = parse()
    json.dump(cl, open(os.path.join(ROOT, "specs", "ep01v44_clips.json"), "w"), indent=1, ensure_ascii=False)
    n = sum(len(c["lines"]) for c in cl)
    print(len(cl), "clips,", n, "lines,", round(sum(c["dur"] for c in cl), 1), "s;", sum(len(c["text"].split()) for k in cl for c in k["lines"]), "words")
    print({m: sum(1 for c in cl if c["method"] == m) for m in {c["method"] for c in cl}})
