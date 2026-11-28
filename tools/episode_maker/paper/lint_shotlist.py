#!/usr/bin/env python3
"""Shot-list lint for v4.5+ episode scripts (production/v4/shot-rules.md, fix-plan.md Fix 2-4). CPU only, no dependencies.

    python3 tools/episode_maker/paper/lint_shotlist.py scripts/episode-01-v4.5.md
    python3 tools/episode_maker/paper/lint_shotlist.py scripts/episode-01-v4.5.md --json out/ep01v45_shots.json
    python3 tools/episode_maker/paper/lint_shotlist.py SCRIPT --profile extended     # long-form cut: 45-50 AI clips, <= 3:00

Reads every Markdown table whose header has the columns
  Clip | Dur | Start | Method | Faces | Shot | START keyframe | END keyframe | ACTION | VOICE | Mouth | Motion | EDIT | SFX | Caption
(columns are found by header name, so their order may change). Rows: AI/HERO clips `Cnn`, CODE clips `Knn`.
FAIL rules (exit code 1): see RULES below; WARN rules are printed but do not fail.
`parse(path)` returns the clips as dicts (used by the prompt compiler / spec builders).

PACE conventions (production/v4/attention-and-pace-spec.md, section 9), all inside the EDIT cell, tokens separated by ';' (never '|'):
  PACE fast|medium|calm      first token; required on every row as soon as one row has it (pace-aware script)
  CUTS 0.0:A/0.9:punch/1.6:ins   picture cuts inside the slot (seconds from clip start; types A punch ins rx card); gaps >= 0.25 s
  TRIM 0.3-2.3              only seconds a-b of a clip generated at max(b, 2.0) s are used; Dur must equal b-a (AI Dur may then be 0.8-3.5)
  MICRO 1.4                 micro-motion / sound texture second (CALM rows longer than 2.5 s)
  FLASH@0.1 2f cream        flash or impact effect: frames <= 2, colour not red, <= 2 per absolute second
The lint prints the average shot length (ASL) overall and per mode and warns when it leaves the spec targets."""
import argparse, json, re, sys

PROFILES = {   # episode-level limits
    "short": dict(ai_min=20, ai_max=26, total_max=75.0, total_warn=65.0, words_max=175, words_warn_min=140, high_max=3),
    "extended": dict(ai_min=45, ai_max=50, total_max=180.0, total_warn=160.0, words_max=380, words_warn_min=250, high_max=5),
}
AI_DUR = (2.0, 3.5)
AI_DUR_TRIM = (0.8, 3.5)      # slot length of an AI row that carries TRIM (the generated clip is still 2.0-3.5 s)
PACES = {"fast", "medium", "calm"}
CUT_TYPES = {"A", "punch", "ins", "rx", "card"}
MIN_CUT_GAP = 0.25
# ASL targets (spec section 0 / 2): overall range and per-mode ranges, seconds
ASL_OVERALL = (1.2, 2.2)
ASL_MODE = {"fast": (0.4, 1.3), "medium": (1.3, 2.7), "calm": (2.5, 6.6)}
MAX_GAP = {"fast": 1.6, "medium": 2.8, "calm": 3.6}        # longest picture shot allowed without a cut / micro change
MAX_RUN = 12.0                                              # continuous fast (or calm) seconds
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
        clips[-1].update(pace_info(r["edit"]))
    return clips


def pace_info(edit):
    """Reads PACE / CUTS / TRIM / MICRO / FLASH tokens from an EDIT cell."""
    out = dict(pace=None, cuts=None, trim=None, micro=None, flashes=[], pace_errors=[])
    m = re.search(r"\bPACE\s+(\w+)", edit)
    if m:
        out["pace"] = m.group(1).lower()
    m = re.search(r"\bCUTS\s+([0-9.:/A-Za-z]+)", edit)
    if m:
        cuts = []
        for tok in m.group(1).split("/"):
            mm = re.match(r"^(\d+(?:\.\d+)?)(?::(\w+))?$", tok)
            if not mm:
                out["pace_errors"].append(f"bad CUTS token {tok!r} (want 0.9:punch)"); continue
            cuts.append((float(mm.group(1)), mm.group(2) or "A"))
        out["cuts"] = cuts
    m = re.search(r"\bTRIM\s+(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)", edit)
    if m:
        out["trim"] = (float(m.group(1)), float(m.group(2)))
    m = re.search(r"\bMICRO\s+(\d+(?:\.\d+)?)", edit)
    if m:
        out["micro"] = float(m.group(1))
    for m in re.finditer(r"\b(?:FLASH|IMPACT)@(\d+(?:\.\d+)?)\s+(\d+)f(?:\s+(\w+))?", edit):
        out["flashes"].append((float(m.group(1)), int(m.group(2)), (m.group(3) or "").lower()))
    return out


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
        if ai and c.get("trim"):
            lo, hi = AI_DUR_TRIM
            a_, b_ = c["trim"]
            if not (0 <= a_ < b_ <= 3.5):
                F(cid, f"TRIM {a_}-{b_} must satisfy 0 <= a < b <= 3.5 (the generated clip is 2.0-3.5 s)")
            elif abs((b_ - a_) - c["dur"]) > 0.05:
                F(cid, f"TRIM {a_}-{b_} is {b_ - a_:.2f} s but Dur is {c['dur']} s")
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
    pace_stats = pace_checks(clips, F, W)
    stats = dict(clips=len(clips), ai=len(ai), code=len(clips) - len(ai), total_s=total, words=nw, high_motion_ai=high,
                 talk_shots=sum(1 for c in ai if any(l["tag"] == "on" for l in c["lines"])),
                 two_face=[c["id"] for c in ai if c.get("faces") == 2],
                 words_by=dict(sorted({w: sum(words(l["text"]) for l in spoken if l["who"] == w) for w in {l["who"] for l in spoken}}.items())),
                 pace=pace_stats)
    return fails, warns, stats


def pace_checks(clips, F, W):
    """PACE / CUTS / FLASH rules. Returns stats (None when the script has no PACE tags)."""
    good = [c for c in clips if "error" not in c]
    if not any(c.get("pace") for c in good):
        return None
    shots, by_mode, t_mode = [], {}, {}
    flashes_abs = []
    run_mode, run_len = None, 0.0
    for c in good:
        cid = c["id"]
        for e in c.get("pace_errors", []):
            F(cid, e)
        p = c.get("pace")
        if p not in PACES:
            F(cid, f"PACE {p!r} missing or not fast|medium|calm"); continue
        dur = c["dur"]
        cuts = c.get("cuts") or [(0.0, "A")]
        if cuts[0][0] != 0.0:
            F(cid, "CUTS must start at 0.0")
        times = [t for t, _ in cuts]
        for (t, ty) in cuts:
            if ty not in CUT_TYPES:
                F(cid, f"CUTS type {ty!r} not in {sorted(CUT_TYPES)}")
            if t >= dur:
                F(cid, f"cut at {t} s is outside the {dur} s slot")
        for a_, b_ in zip(times, times[1:]):
            if b_ - a_ < MIN_CUT_GAP - 1e-9:
                F(cid, f"cuts {a_} and {b_} are closer than {MIN_CUT_GAP} s (6 frames): too fast to read and a flicker risk")
        bounds = times + [dur]
        lens = [round(b_ - a_, 3) for a_, b_ in zip(bounds, bounds[1:])]
        shots += [(p, x) for x in lens]
        by_mode.setdefault(p, []).extend(lens)
        t_mode[p] = t_mode.get(p, 0.0) + dur
        # longest shot without a change
        longest = max(lens)
        if p == "calm" and c["method"] != "CODE":
            if dur > 2.5 and c.get("micro") is None and len(times) == 1:
                W(cid, "CALM row over 2.5 s without MICRO <t> (a slow push, particle or sound texture keeps it alive)")
        elif longest > MAX_GAP[p] + 1e-9 and c["method"] != "CODE":
            W(cid, f"{p.upper()} row holds one shot for {longest:.1f} s (> {MAX_GAP[p]} s): add a CUTS entry or a card / sprite pop")
        if p == "fast" and dur > 1.8 and len(times) < 2:
            W(cid, f"FAST row of {dur} s without any CUTS")
        for (t, n, col) in c.get("flashes", []):
            if n > 2:
                F(cid, f"FLASH/IMPACT of {n} frames: at most 2")
            if "red" in col:
                F(cid, "FLASH/IMPACT colour red: no red flashes")
            flashes_abs.append(c["start"] + t)
        # run of one mode
        if p == run_mode:
            run_len += dur
        else:
            run_mode, run_len = p, dur
        if p in ("fast", "calm") and run_len > MAX_RUN + 0.01:
            W(cid, f"{run_len:.1f} s of continuous {p.upper()} (limit {MAX_RUN:.0f} s; the premiere hook + opening is the known exception)")
    flashes_abs.sort()
    for i, t in enumerate(flashes_abs):
        n = sum(1 for u in flashes_abs[i:] if u - t < 1.0)
        if n > 2:
            F("EPISODE", f"{n} flash/impact effects within 1 s at {t:.1f} s (budget 2 per second)")
            break
    total = sum(x for _, x in shots)
    asl = total / len(shots) if shots else 0
    mode_asl = {m: round(sum(v) / len(v), 2) for m, v in by_mode.items()}
    if not ASL_OVERALL[0] <= asl <= ASL_OVERALL[1]:
        W("EPISODE", f"ASL {asl:.2f} s is outside the target {ASL_OVERALL[0]}-{ASL_OVERALL[1]} s")
    for m, v in mode_asl.items():
        lo_, hi_ = ASL_MODE[m]
        if not lo_ <= v <= hi_:
            W("EPISODE", f"{m.upper()} ASL {v} s is outside {lo_}-{hi_} s")
    return dict(shots=len(shots), asl=round(asl, 2), asl_by_mode=mode_asl, seconds_by_mode={k: round(v, 1) for k, v in t_mode.items()},
                share_by_mode={k: round(100 * v / (sum(t_mode.values()) or 1)) for k, v in t_mode.items()}, flashes=len(flashes_abs))


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
    if st.get("pace"):
        pc = st["pace"]
        print(f"PACE: {pc['shots']} shots, ASL {pc['asl']} s overall, by mode {pc['asl_by_mode']}, time share % {pc['share_by_mode']}, flash/impact effects {pc['flashes']}")
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
