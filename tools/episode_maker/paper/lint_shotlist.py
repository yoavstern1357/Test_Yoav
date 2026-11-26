#!/usr/bin/env python3
"""Shot-list lint for v4.5+ episode scripts (production/v4/shot-rules.md, fix-plan.md Fix 2-4). CPU only, no dependencies.

    python3 tools/episode_maker/paper/lint_shotlist.py scripts/episode-01-v4.5.md
    python3 tools/episode_maker/paper/lint_shotlist.py scripts/episode-01-v4.5.md --json out/ep01v45_shots.json
    python3 tools/episode_maker/paper/lint_shotlist.py SCRIPT --profile extended     # long-form cut: 45-50 AI clips, <= 3:00

Reads every Markdown table whose header has the columns
  Clip | Dur | Start | Method | Faces | Shot | START keyframe | END keyframe | ACTION | VOICE | Mouth | Motion | EDIT | SFX | Caption
(columns are found by header name, so their order may change). Rows: AI/HERO clips `Cnn`, CODE clips `Knn`.
FAIL rules (exit code 1): see RULES below; WARN rules are printed but do not fail.
`parse(path)` returns the clips as dicts (used by the prompt compiler / spec builders)."""
import argparse, json, re, sys

PROFILES = {   # episode-level limits
    "short": dict(ai_min=20, ai_max=26, total_max=75.0, total_warn=65.0, words_max=175, words_warn_min=140, high_max=3),
    "extended": dict(ai_min=45, ai_max=50, total_max=180.0, total_warn=160.0, words_max=380, words_warn_min=250, high_max=5),
}
AI_DUR = (2.0, 3.5)
CODE_DUR = (0.5, 8.0)
CHARS = ["boy", "uncle", "grandma", "dad", "narrator", "camel"]
SHOTS = {"ECU", "CU", "MCU", "MS", "MWS", "WS", "EWS", "MACRO", "OTS", "FULL"}
TALK_SHOTS = {"CU", "MCU"}
WIDE = {"MS", "MWS", "WS", "EWS", "FULL"}
MOUTHS = {"closed", "overlay", "lipsync"}
MOTIONS = {"low", "medium", "high"}
TAGS = {"on", "off", "V.O."}
MIN_FACE_PCT = 25
# natural-speed words per second (measured on the v4.4 Qwen3-TTS takes, no voice_speed): estimate only
RATE = {"boy": 2.4, "grandma": 2.3, "uncle": 2.0, "narrator": 1.9}
PAUSE = 0.35          # seconds per "..." in a line
MIN_LINE = 0.9        # a one-word line still takes about this long
# words that must never reach an AI prompt (START / END / ACTION of AI and HERO rows): edit instructions, text, cards
FORBIDDEN = [r"\bPEAK\b", r"\bcuts?\b", r"\bcutting\b", r"\binserts?\b", r"edit:", r"snap[- ]zoom", r"\bwhip\w*", r"\[CARD",
             r"\bcards?\b", r"\bbadges?\b", r"\btitles?\b", r"\btext\b", r"\bframes\b", r"\bcaptions?\b", r"\blogos?\b",
             r"\bsigns?\b", r"\bletter(s|ing)\b", r"\bwriting\b", r"\bmontage\b", r"split[- ]screen",
             # camera moves belong to the edit (fixed camera in every AI clip)
             r"\bzoom\w*", r"\bpan(s|ning)?\b", r"push[- ]in", r"pull[- ]?back", r"\btracking\b", r"\bdolly\b", r"\borbit\w*",
             r"slow[- ]motion", r"speed[- ]ramp",
             # code effects belong to the edit
             r"\baura\b", r"sweat[- ]drops?", r"speed[- ]lines?", r"impact[- ]frames?", r"star[- ]eyes?", r"\bsparkl\w*"]
# risky shot types (fix-plan Fix 2.7): only allowed on HERO rows (paid model or code effect)
RISKY = [r"\brocket\w*", r"\blevitat\w*", r"\bflying\b", r"\bflies\b", r"fly off", r"\bchibi\b", r"\bmorph\w*", r"\btransform\w*",
         r"\benter(s|ing)?\b", r"steps in", r"walks in", r"\bexit(s|ing)?\b", r"leaves the", r"out of (the )?frame", r"into (the )?frame",
         r"\bcrowd\w*", r"\bcaravan\w*", r"\bswallow\w*", r"\bgulp\w*", r"face (is )?covered"]
VOICE_RX = re.compile(r"([A-Z]+)\s*\((on|off|V\.O\.)\)\s*\[([^\]]*)\]\s*:\s*[“\"](.*?)[”\"]")


def norm(h):
    h = h.lower()
    for key in ["clip", "dur", "start keyframe", "end keyframe", "start", "method", "faces", "shot", "action", "voice", "mouth",
                "motion", "edit", "sfx", "caption"]:
        if h.startswith(key):
            return {"start keyframe": "start_kf", "end keyframe": "end_kf"}.get(key, key)
    return h


def secs(ts):
    m, s = ts.strip().split(":")
    return int(m) * 60 + float(s)


def parse_faces(cell):
    """'2: Boy, Uncle (+hands: Grandma)' -> (2, ['boy','uncle'], ['grandma'])"""
    m = re.match(r"\s*(\d+)\s*:?\s*([^()]*)", cell)
    if not m:
        return None, [], []
    n = int(m.group(1))
    names = [x.strip().lower() for x in m.group(2).split(",") if x.strip()]
    names = [x for x in names if x in CHARS]
    partial = []
    for p in re.findall(r"\(\+\s*(?:hands|back|blurred)\s*:\s*([^)]*)\)", cell):
        partial += [x.strip().lower() for x in p.split(",") if x.strip()]
    return n, names, partial


def parse_shot(cell):
    m = re.match(r"\s*([A-Za-z]+)", cell)
    size = m.group(1).upper() if m else ""
    f = re.search(r"face[s]?\s*(\d+)\s*%", cell)
    return size, (int(f.group(1)) if f else None)


def parse_voice(cell):
    c = cell.strip()
    if c in ("", "—", "-", "–") or c.lower().startswith("(no words"):
        return []
    out = [dict(who=m.group(1).lower(), tag=m.group(2), note=m.group(3).strip(), text=m.group(4).strip()) for m in VOICE_RX.finditer(c)]
    if not out:
        out = [dict(who="?", tag="?", note="", text=c, bad=True)]
    return out


def words(text):
    return len([w for w in re.split(r"\s+", re.sub(r"[“”\"!?.,:;…]", " ", text)) if w])


def est_seconds(line):
    n = words(line["text"])
    return max(MIN_LINE, n / RATE.get(line["who"], 2.2)) + PAUSE * line["text"].count("...")


def parse(path):
    clips, cols = [], None
    for ln in open(path, encoding="utf-8"):
        if not ln.startswith("|"):
            cols = None if not ln.strip() else cols
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells and cells[0].lower() == "clip" and any(c.lower().startswith("start keyframe") for c in cells):
            cols = [norm(c) for c in cells]
            continue
        if not cols or not re.match(r"^[CK]\d+$", cells[0]):
            continue
        if len(cells) != len(cols):
            clips.append(dict(id=cells[0], error=f"{len(cells)} cells, header has {len(cols)} (a '|' inside a cell?)"))
            continue
        r = dict(zip(cols, cells))
        n, names, partial = parse_faces(r.get("faces", ""))
        size, fpct = parse_shot(r.get("shot", ""))
        clips.append(dict(id=r["clip"], dur=float(r["dur"]), start=secs(r["start"]), method=r["method"].upper(),
                          faces=n, names=names, partial=partial, faces_raw=r.get("faces", ""), shot=size, face_pct=fpct,
                          start_kf=r["start_kf"], end_kf=r["end_kf"], action=r["action"], lines=parse_voice(r["voice"]),
                          mouth=r["mouth"].lower(), motion=r["motion"].lower(), edit=r["edit"], sfx=r["sfx"], caption=r["caption"]))
    return clips


def names_in(text):
    return {c for c in CHARS if re.search(rf"\b{c}('s)?\b", text, re.I)}


def lint(clips, prof):
    fails, warns = [], []
    F = lambda cid, msg: fails.append(f"{cid}: {msg}")
    W = lambda cid, msg: warns.append(f"{cid}: {msg}")
    t = 0.0
    for c in clips:
        cid = c["id"]
        if "error" in c:
            F(cid, c["error"]); continue
        ai = c["method"] in ("AI", "HERO")
        if c["method"] not in ("AI", "HERO", "CODE"):
            F(cid, f"method {c['method']!r} not AI|HERO|CODE")
        if abs(c["start"] - t) > 0.05:
            F(cid, f"start {c['start']:.1f} s but the clips before end at {t:.1f} s")
        t = c["start"] + c["dur"]
        lo, hi = AI_DUR if ai else CODE_DUR
        if not lo <= c["dur"] <= hi:
            F(cid, f"duration {c['dur']} s outside {lo}-{hi} s")
        if c["mouth"] not in MOUTHS:
            F(cid, f"mouth {c['mouth']!r} not closed|overlay|lipsync")
        if c["motion"] not in MOTIONS:
            F(cid, f"motion {c['motion']!r} not low|medium|high")
        if not re.match(r"(TOP|BOTTOM|none)\b", c["caption"], re.I):
            F(cid, "caption zone must start with TOP, BOTTOM or none")
        if not c["sfx"].strip():
            F(cid, "SFX column empty (write 'none')")
        if not c["end_kf"].strip():
            F(cid, "END keyframe missing")
        # voice
        speakers = {l["who"] for l in c["lines"]}
        for l in c["lines"]:
            if l.get("bad"):
                F(cid, "VOICE not in the form SPEAKER (on|off|V.O.) [note]: “words”")
        if len(speakers) > 1:
            F(cid, f"multi-speaker clip ({', '.join(sorted(speakers))}): one speaker per clip, use shot / reverse shot")
        for l in c["lines"]:
            e = est_seconds(l)
            if e > c["dur"] + 1e-6:
                F(cid, f"line needs about {e:.1f} s at natural speed, clip is {c['dur']} s: cut words (never speed up)")
            elif e > c["dur"] - 0.3:
                W(cid, f"line about {e:.1f} s leaves under 0.3 s in a {c['dur']} s clip")
        on = [l for l in c["lines"] if l["tag"] == "on"]
        if not ai:
            continue
        # ---- AI / HERO rules
        if c["faces"] is None:
            F(cid, "Faces must start with the count, e.g. '2: Boy, Uncle'"); continue
        if c["faces"] > 2:
            F(cid, f"{c['faces']} visible faces: max 2 per AI clip (a third only as hands / back / blurred, never with a face)")
        if c["faces"] != len(c["names"]):
            F(cid, f"face count {c['faces']} but {len(c['names'])} names listed ({c['faces_raw']})")
        if "dad" in c["names"]:
            F(cid, "Dad is never a face (sepia silhouette from behind: '+back: Dad')")
        if c["shot"] not in SHOTS:
            F(cid, f"shot size {c['shot']!r} unknown ({', '.join(sorted(SHOTS))})")
        prompt = " ".join([c["start_kf"], c["end_kf"], c["action"]])
        for fld, txt in (("START", c["start_kf"]), ("END", c["end_kf"]), ("ACTION", c["action"])):
            for rx in FORBIDDEN:
                m = re.search(rx, txt, re.I)
                if m:
                    F(cid, f"forbidden word {m.group(0)!r} in {fld} (move it to EDIT)")
            if c["method"] == "AI":
                for rx in RISKY:
                    m = re.search(rx, txt, re.I)
                    if m:
                        F(cid, f"risky shot type {m.group(0)!r} in {fld}: restage, or mark the row HERO (paid / code effect)")
        extra = names_in(prompt) - set(c["names"])
        if extra:
            F(cid, f"prompt names {', '.join(sorted(extra))} who is not a visible face (describe hands/backs generically)")
        missing = set(c["names"]) - names_in(c["start_kf"])
        if missing:
            F(cid, f"START does not name visible face(s): {', '.join(sorted(missing))}")
        if not re.match(r"\s*Same\b", c["end_kf"]) or not re.search(r"\bonly\b", c["end_kf"]):
            F(cid, "END must be an edit of START: 'Same framing ...; change only: ...'")
        if len(re.findall(r"\bthen\b", c["action"], re.I)) >= 2 or len(re.findall(r"[.;]", c["action"])) > 3:
            W(cid, "ACTION looks like more than one action (one action per clip)")
        if on:
            sp = on[0]["who"]
            if c["shot"] not in TALK_SHOTS:
                F(cid, f"talk shot is {c['shot']}: on-screen dialogue only in CU / MCU (wides carry no dialogue)")
            if c["face_pct"] is None or c["face_pct"] < MIN_FACE_PCT:
                F(cid, f"talk shot face {c['face_pct']}%: the speaking face must be >= {MIN_FACE_PCT}% of the picture height")
            if sp not in c["names"]:
                F(cid, f"on-screen speaker {sp} is not in Faces")
            if c["mouth"] not in ("overlay", "lipsync"):
                F(cid, f"on-screen line with mouth {c['mouth']!r}: use overlay or lipsync")
            if c["motion"] != "low":
                F(cid, f"talk shot motion {c['motion']!r}: talk shots are motion low")
        else:
            if c["mouth"] != "closed":
                F(cid, f"mouth {c['mouth']!r} without an on-screen line: use closed")
            for l in c["lines"]:
                if l["tag"] == "off" and l["who"] in c["names"]:
                    F(cid, f"{l['who']} is tagged off but is a visible face")
    # ---- episode level
    ai = [c for c in clips if c.get("method") in ("AI", "HERO")]
    total = round(sum(c.get("dur", 0) for c in clips), 2)
    nw = sum(words(l["text"]) for c in clips for l in c.get("lines", []))
    high = [c["id"] for c in clips if c.get("motion") == "high" and c.get("method") in ("AI", "HERO")]
    if not prof["ai_min"] <= len(ai) <= prof["ai_max"]:
        F("EPISODE", f"{len(ai)} AI clips, profile wants {prof['ai_min']}-{prof['ai_max']}")
    if total > prof["total_max"]:
        F("EPISODE", f"total {total} s > {prof['total_max']} s")
    elif total > prof["total_warn"]:
        W("EPISODE", f"total {total} s is over the {prof['total_warn']:.0f} s target (fine up to {prof['total_max']:.0f} s)")
    if len(high) > prof["high_max"]:
        F("EPISODE", f"{len(high)} AI clips with motion high ({', '.join(high)}), max {prof['high_max']}")
    if nw > prof["words_max"]:
        F("EPISODE", f"{nw} words > {prof['words_max']}")
    elif nw < prof["words_warn_min"]:
        W("EPISODE", f"{nw} words < {prof['words_warn_min']}: fine at natural voice speed; restore lines only if the animatic runs short")
    spoken = [l for c in clips for l in c.get("lines", [])]
    if not spoken or not spoken[-1]["text"].startswith("Dad was right"):
        F("EPISODE", "the last spoken line must be “Dad was right...”")
    if not any("for dumpling research" in l["text"].lower() for l in spoken):
        F("EPISODE", "catchphrase “For dumpling research!” missing")
    stats = dict(clips=len(clips), ai=len(ai), code=len(clips) - len(ai), total_s=total, words=nw, high_motion_ai=high,
                 talk_shots=sum(1 for c in ai if any(l["tag"] == "on" for l in c["lines"])),
                 two_face=[c["id"] for c in ai if c.get("faces") == 2],
                 words_by=dict(sorted({w: sum(words(l["text"]) for l in spoken if l["who"] == w) for w in {l["who"] for l in spoken}}.items())))
    return fails, warns, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script")
    ap.add_argument("--profile", choices=sorted(PROFILES), default="short")
    ap.add_argument("--json", help="write the parsed clips to this file")
    a = ap.parse_args()
    clips = parse(a.script)
    if not clips:
        print("no shot-list rows found (header must contain 'Clip' and 'START keyframe')"); return 1
    fails, warns, st = lint(clips, PROFILES[a.profile])
    for c in clips:
        if "error" in c:
            continue
        v = "; ".join(f"{l['who']}({l['tag']}): {l['text']}" for l in c["lines"]) or "-"
        print(f"{c['id']:4} {c['method']:5} {c['dur']:4.1f}s @{c['start']:5.1f}  faces {c['faces'] if c['faces'] is not None else '-'}"
              f" {','.join(c['names']) or '-':14} {c['shot']:5} {c['mouth']:8} {c['motion']:6} {v}")
    print(f"\n{st['clips']} clips ({st['ai']} AI, {st['code']} CODE), {st['total_s']} s, {st['words']} words {st['words_by']}, "
          f"talk shots {st['talk_shots']}, 2-face AI clips {len(st['two_face'])} {st['two_face']}, high-motion AI {st['high_motion_ai']}")
    for w in warns:
        print("WARN ", w)
    for f in fails:
        print("FAIL ", f)
    print(f"RESULT: {'FAIL' if fails else 'PASS'} ({len(fails)} fail, {len(warns)} warn, profile {a.profile})")
    if a.json:
        json.dump(dict(stats=st, clips=clips), open(a.json, "w"), indent=1, ensure_ascii=False)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
