"""Parse the v5 scripts' shot lists and lay out the animatic timeline from the real voice files (voice-first)."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
EM = os.path.dirname(HERE)
OUT = os.path.join(EM, "out", "animatic-v5")
FPS = 24
SCRIPTS = {"ep01": os.path.join(EM, "..", "..", "scripts", "episode-01-v5.md"), "ep02": os.path.join(EM, "..", "..", "scripts", "episode-02-v5.md")}
SPLIT = " | "


def parse_script(path):
    shots, hdr = [], None
    for l in open(path, encoding="utf-8"):
        if l.startswith("| Clip |"):
            hdr = [x.strip() for x in l.strip().strip("|").split("|")]
            continue
        if hdr and re.match(r"\| (C|K)\d+ ", l):
            c = [x.strip() for x in l.strip().strip("|").split(SPLIT)]
            if len(c) != len(hdr):
                raise SystemExit(f"column mismatch in {path}: {c[0]} {len(c)} vs {len(hdr)}")
            r = dict(zip(hdr, c))
            e = r["EDIT"]
            s = dict(id=r["Clip"], plan=float(r["Dur"]), start=r["Start"], method=r["Method"], faces=r["Faces"], shot=r["Shot"], kf=r["START keyframe"],
                     action=r["ACTION + facial beats"], voice=r["VOICE"], edit=e, sfx=r["SFX"], caption=r["Caption"], song=r.get("SONG", ""))
            m = re.search(r"PACE (fast|medium|calm)", e); s["pace"] = m.group(1) if m else "medium"
            m = re.search(r"CUTS ([^;]+);", e + ";"); s["cuts"] = [(float(a), b) for a, b in (x.split(":") for x in m.group(1).split("/"))] if m else [(0.0, "A")]
            m = re.search(r"TRIM ([\d.]+)-([\d.]+)", e); s["trim"] = (float(m.group(1)), float(m.group(2))) if m else None
            m = re.search(r"MICRO ([\d.]+)", e); s["micro"] = float(m.group(1)) if m else None
            s["names"] = re.findall(r"(Boy|Uncle|Grandma|Dad|Camel)", r["Faces"].split("(+")[0] if "(+" in r["Faces"] and not re.match(r"\d", r["Faces"].split(":")[0]) else r["Faces"].split("(")[0])
            s["hands"] = re.findall(r"\+hands: (\w+)", r["Faces"])
            s["back"] = re.findall(r"\+back: (\w+)", r["Faces"])
            s["overlays"] = [(m2.group(1).lower(), m2.group(2), float(m2.group(3)), float(m2.group(4))) for m2 in
                             re.finditer(r'(Place card|Fact card|end card|Badge)\s+"([^"]+)"[^;]*?([\d.]+)-([\d.]+) s', e, re.I)]
            s["flash"] = [float(x) for x in re.findall(r"(?:FLASH|IMPACT)@([\d.]+)", e)]
            # cut notes: "1.5 punch-in 1.15x on ..." -> note for the cut at that time
            notes = {}
            for t, typ in s["cuts"]:
                m3 = re.search(r"(?<![\d.])" + re.escape(("%.2f" % t).rstrip("0").rstrip(".") if t != int(t) else "%.1f" % t) + r" (?!s)([^.;]*)", e)
                if m3 and t > 0:
                    notes[t] = m3.group(1).strip()[:60]
            s["cutnotes"] = notes
            shots.append(s)
    return shots


def load_voice(ep, cid):
    p = os.path.join(OUT, "voices", ep, cid + ".json")
    return json.load(open(p)) if os.path.exists(p) else None


LEAD = {"fast": 0.20, "medium": 0.28, "calm": 0.45}
TAIL = {"fast": 0.30, "medium": 0.40, "calm": 0.75}
OPEN = {"C21", "C22", "C23", "K01"}


def fr(t):
    return round(t * FPS) / FPS


def layout(ep, shots):
    """Place every shot: duration = lead + voice + reaction beat (pace dependent); silent shots keep the planned (or trimmed) length."""
    t, out = 0.0, []
    for i, s in enumerate(shots):
        v = load_voice(ep, s["id"])
        plan = s["plan"] if not s["trim"] else s["trim"][1] - s["trim"][0]
        lead, tail = LEAD[s["pace"]], TAIL[s["pace"]]
        o = dict(s)
        o["voicej"] = v
        if ep == "ep01" and s["id"] in OPEN:
            dur = plan; o["line_at"] = None
        elif v:
            if ep == "ep01" and s["id"] == "C01":
                lead, tail = 0.55, 0.35                       # thunder + gong first
            if ep == "ep01" and s["id"] == "C11":
                tail = 0.55                                   # the comic 0.3 s silence after "don't..."
            if ep == "ep02" and s["id"] == "C11":
                tail = 1.0                                    # the one deliberate silence before the Dad beat
            if ep == "ep02" and s["id"] == "C22":
                tail = 0.5
            if ep == "ep02" and s["id"] == "C01":
                lead = 0.35
            if ep == "ep01" and s["id"] == "C20":
                tail = 0.9                                    # held tone, smash to black
            dur = lead + v["dur"] + tail
            if s["id"] == "K04":
                dur = max(dur, 5.2)                           # four paper scenes need >= 1.2 s each
            if s["id"] == "K03":
                dur = max(dur, 1.6)
            dur = max(dur, 1.2)
            o["line_at"] = lead
        else:
            dur = plan; o["line_at"] = None
        dur = max(round(dur * FPS) / FPS, 6 / FPS)
        o["t0"], o["dur"], o["plan_dur"] = fr(t) if False else t, dur, plan
        # cut segments: scale the planned cut times, snap to word starts when there is a voice, keep gaps >= 0.25 s (6 frames)
        cuts = []
        scale = 1.0 if (ep == "ep01" and s["id"] in OPEN) else dur / max(plan, 0.5)
        starts = [lead + w["s"] for w in v["words"]] if v else []
        for k, (ct, typ) in enumerate(s["cuts"]):
            tt = ct * scale
            if k > 0 and starts and typ in ("punch", "ins", "rx", "A"):
                near = min(starts, key=lambda x: abs(x - tt))
                if abs(near - tt) <= 0.45:
                    tt = near
            if k == 0:
                tt = 0.0
            cuts.append([tt, typ, ct])
        cuts2 = [cuts[0]]
        for c in cuts[1:]:
            if c[0] - cuts2[-1][0] >= 0.30 and dur - c[0] >= 0.30:
                cuts2.append(c)
        o["segs"] = [(c[0], (cuts2[k + 1][0] if k + 1 < len(cuts2) else dur), c[1], c[2]) for k, c in enumerate(cuts2)]
        out.append(o)
        t += dur
    return out, t
