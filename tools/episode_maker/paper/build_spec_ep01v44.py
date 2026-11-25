#!/usr/bin/env python3
"""Writes specs/episode-01-v4.4.json: series intro + Episode 1 v4.4 (37 clips C01-C37, scripts/episode-01-v4.4.md), generated from the script tables
(paper/parse_ep01v44.py). Every I2V clip plays `clips/ep01v44/<id>.mp4` (+ `_land`); the start keyframe `<id>.png` is only the emergency fallback.
    python3 paper/build_spec_ep01v44.py"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
from parse_ep01v44 import parse

CODE = "../out/ep01v44/code/%s.mp4"
FLOOR = 0.85          # the script's clip lengths are minimums; the voices set the real length
shots = []
intro_end = [0]


def sh(id, dur, **kw):
    d = dict(id=id, dur=dur, tail=0.08, lead=0.1, transition="cut")
    d.update(kw)
    shots.append(d)
    return d


def ai(c, dur, id=None, trim=None, speed=None, fb=None, still=None, **kw):
    base = dict(motion="zoom_in", zoom0=1.0, zoom=1.1, sway=0.4)
    base.update(fb or {})
    d = dict(clip=f"{c}.mp4", img=still or f"{c}.png", fb=base)
    if trim: d["trim"] = trim
    if speed: d["speed"] = speed
    if not trim and not speed:
        d["fit_clip"] = True
    d.update(kw)
    return sh(id or c, dur, **d)


def S(t, name, d=None, gain=None):
    e = dict(t=t, name=name)
    if d is not None: e["d"] = d
    if gain is not None: e["gain"] = gain
    return e


def FACT(t, d, label, text, y=0.2):
    return dict(type="fact", t=t, d=d, label=label, text=text, y=y, y_land=0.28)


def badge(t, d, text):
    return dict(type="fact", t=t, d=d, label="SAFETY", text=text, y=0.12, y_land=0.2)


# ---- keyword -> sound effect (the script's SFX column is free text)
SFX_WORDS = [("thunder", "impact"), ("gong", "gong"), ("toot", "toot"), ("whoosh", "whoosh"), ("bike bell", "bike_bell"), ("chimes", "chimes"), ("chime", "ding"),
             ("hiss", "hiss"), ("sizzle", "hiss"), ("chop", "chop"), ("clink", "clink"), ("sip", "sip"), ("ding", "ding"), ("rooster", "rooster"),
             ("page", "page"), ("pen scratch", "pen"), ("creak", "creak"), ("gull", "gull"), ("sparkle", "sparkle"), ("pop", "pop"), ("riser", "riser"),
             ("impact", "impact"), ("crack", "crack"), ("thud", "thud"), ("thump", "thud"), ("boing", "boing"), ("camel", "camel_bell"), ("rewind", "rewind"),
             ("tape squeal", "rewind"), ("squeak", "squeak"), ("flap", "flap"), ("wings", "flap"), ("drum", "taiko"), ("fireworks", "pop"), ("gust", "whoosh"),
             ("aura", "riser"), ("roar", "growl"), ("rumble", "growl"), ("slap", "pop"), ("shing", "shing"), ("plink", "ding"), ("skid", "squeak"), ("gulp", "sip"),
             ("sniff", "sniff"), ("sails snap", "flap"), ("paper", "page"), ("lid", "lid"), ("drip", "tick"), ("tick", "tick"), ("splash", "splash"), ("zing", "ding")]


def sfx_for(text, dur, skip=()):
    t = text.lower()
    found = []
    for kw, nm in SFX_WORDS:
        i = t.find(kw)
        if i >= 0 and nm not in [n for _, n in found] and nm not in skip:
            found.append((i, nm))
    found.sort()
    out = []
    n = len(found)
    for k, (_, nm) in enumerate(found[:5]):
        tt = 0.1 + (dur * 0.7) * (k / max(n - 1, 1)) if n > 1 else 0.1
        d = {"toot": 0.8, "riser": 1.5, "hiss": 1.4, "growl": 1.0, "train": 3.0, "chimes": 1.8, "rewind": 1.0, "creak": 0.9, "gull": 0.8}.get(nm)
        out.append(S(round(tt, 2), nm, d, 0.7))
    return out


def mood_for(text, cur):
    t = text.lower()
    if "adventure" in t: return "adventure"
    if "piano" in t or "choir" in t or "swell" in t or "violin" in t: return "tender"
    if "strings" in t: return "sparse"
    if "taiko" in t or "title" in t: return "adventure"
    return "off"


def amb_for(text):
    t = text.lower()
    if "canal" in t: return "water"
    if "train" in t or "station" in t: return "street"
    if "lantern" in t or "night" in t: return "night"
    if "stall" in t or "steam" in t or "steamer" in t or "sizzle" in t: return "shop"
    return None


def lines_of(c, over=None):
    out = []
    for i, l in enumerate(c["lines"]):
        who = "boy" if l["who"] == "dad" else l["who"]
        d = dict(who=who, text=l["text"], gap=0.05)
        if re.search(r"off-screen|to lens|to the lens", l["tag"] + l["note"]):
            pass
        if over and i in over:
            d.update(over[i])
        out.append(d)
    return out


# ---------------------------------------------------------------- the intro (placeholder cut until the opening song is mixed in)
def intro():
    ai("I1", 1.6, fb=dict(motion="zoom_in", zoom=1.14, focus=[0.55, 0.45], sway=0.3, particles=dict(type="steam", n=8)), mood="adventure",
       sfx=[S(0.0, "tick", None, 0.5), S(0.3, "crunch", None, 0.9), S(0.55, "hiss", 0.8, 0.5)], punch=[dict(t=0.3, scale=1.06)])
    ai("I2", 1.3, fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.2, focus=[0.5, 0.45]), whip=True, sfx=[S(0.1, "splash", None, 0.8), S(0.3, "sparkle", None, 0.5)])
    ai("I3", 2.0, fb=dict(motion="pan_right", zoom0=1.05, zoom=1.12, focus=[0.55, 0.55], pan=0.06), whip=True,
       sfx=[S(0.1, "plop", None, 0.6), S(0.35, "laugh", None, 0.8), S(0.7, "plop", None, 0.5), S(1.0, "bloop", None, 0.5)])
    ai("I5", 1.9, fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.2, focus=[0.5, 0.5], particles=dict(type="dust", n=14)), whip=True,
       sfx=[S(0.0, "rolling", 1.3, 0.8), S(0.2, "chomp", None, 0.7), S(0.7, "chomp", None, 0.7)], speedlines=dict(t=0.0, d=1.2, dir="radial"))
    ai("I5b", 1.2, fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.15, focus=[0.5, 0.5]), sfx=[S(0.0, "rolling", 0.8, 0.8), S(0.35, "chomp", None, 0.8)])
    ai("I5c", 1.0, fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.25, focus=[0.35, 0.55]),
       sfx=[S(0.05, "shing", None, 0.8), S(0.25, "shing", None, 0.8), S(0.45, "shing", None, 0.8)], speedlines=dict(t=0.0, d=0.7, dir="horizontal"))
    ai("I6", 1.0, fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.2, focus=[0.55, 0.5]), sfx=[S(0.2, "chomp", None, 1.0), S(0.25, "impact", None, 0.6)],
       impact=dict(t=0.2, amp=18), speedlines=dict(t=0.0, d=0.5, dir="radial"))
    sh("C90", 1.6, clip=CODE % "C90", mood="adventure", sfx=[S(0.0, "gong", None, 0.8), S(0.05, "taiko", None, 0.8), S(0.1, "sting", None, 0.8)])


def build():
    clips = parse()
    intro()
    mood = "adventure"
    for c in clips:
        cid, dur = c["id"], round(c["dur"] * FLOOR, 2)
        text = c["sfx"]
        m = mood_for(text, mood)
        kw = dict(lines=lines_of(c), caption_zone=c["zone"], ambience=amb_for(text))
        kw = {k: v for k, v in kw.items() if v}
        if m != mood or cid == "C01":
            kw["mood"] = m
            mood = m
        sfx = sfx_for(text, dur)
        if cid == "C01":
            kw["black"] = 0.3
        if cid == "C04":
            kw["transition"] = "cut"
        if cid == "C08":                     # ink-bloom title cards in the sky (code overlay)
            kw["cards"] = [dict(type="title", text="#01 XIAOLONGBAO", sub="NANXIANG · SHANGHAI, CHINA", t=1.0, d=2.2, y=0.2, y_land=0.24)]
        if c["method"] == "CODE":
            sh(cid, dur, clip=CODE % cid, sfx=sfx, **kw)
            if cid == "C05":
                shots[-1]["cards"] = [FACT(0.5, 3.5, "QINGLONG PORT", "Pottery to Japan and Korea")]
            continue
        fb = dict(motion="zoom_in", zoom=1.1, focus=[0.5, 0.5], sway=0.4)
        if cid == "C14":      # PEAK 1: lid lift, then fast macro cuts, whip-pans, slow-motion ripple, a held breath, the giant eye
            kw0 = dict(kw)
            ai(cid, 1.6, id="C14a", trim=[0.0, 1.6], fb=dict(motion="zoom_in", zoom=1.12, focus=[0.5, 0.5]), sfx=sfx[:2],
               cards=[FACT(0.2, 3.2, "SOUP SECRET", "The soup goes in solid", y=0.16)], **{k: v for k, v in kw0.items() if k != "lines"}, lines=lines_of(c, {}) [:1])
            ai(cid, 0.7, id="C14b", trim=[1.6, 2.3], whip=True, fb=dict(motion="zoom_in", zoom0=1.7, zoom=1.95, focus=[0.45, 0.55]))
            ai(cid, 0.7, id="C14c", trim=[2.3, 3.0], whip=True, fb=dict(motion="zoom_in", zoom0=2.2, zoom=2.5, focus=[0.55, 0.5]))
            ai(cid, 1.4, id="C14d", trim=[3.0, 3.8], speed=0.6, whip=True, fb=dict(motion="zoom_in", zoom0=1.9, zoom=2.1, focus=[0.5, 0.45]),
               lines=lines_of(c)[1:2], sfx=[S(0.2, "sparkle", None, 0.7)])
            ai(cid, 0.9, id="C14e", trim=[3.8, 4.5], fb=dict(motion="zoom_out", zoom0=1.4, zoom=1.0, focus=[0.5, 0.5]))
            continue
        if cid == "C19":      # PEAK 2: ECU mouth, ECU eye, impact frame, rocket; silence then one long toot
            ai(cid, 1.0, id="C19a", trim=[0.0, 1.0], fb=dict(motion="zoom_in", zoom0=1.4, zoom=1.7, focus=[0.5, 0.35]), sfx=[S(0.0, "sip", None, 0.8), S(0.1, "riser", 1.9, 0.7)],
               lines=lines_of(c)[:1], mood="tension", ambience="shop")
            ai(cid, 0.55, id="C19b", trim=[1.0, 1.55], fb=dict(motion="zoom_in", zoom0=2.3, zoom=2.6, focus=[0.52, 0.3]), shake=[dict(t=0.2, d=0.3, amp=6)])
            ai(cid, 0.55, id="C19c", trim=[1.55, 2.1], fb=dict(motion="zoom_in", zoom0=2.1, zoom=2.4, focus=[0.5, 0.12]), shake=[dict(t=0.05, d=0.4, amp=8)])
            ai(cid, 1.9, id="C19d", trim=[2.1, 4.5], mood="off", fb=dict(motion="zoom_out", zoom0=1.3, zoom=1.0, focus=[0.5, 0.3], sway=0.0),
               impact=dict(t=0.04, amp=34), impact_frame=dict(t=0.0, d=0.2), speedlines=dict(t=0.2, d=0.9, dir="radial"),
               sfx=[S(0.0, "crack", None, 0.9), S(0.02, "gong", None, 0.7), S(0.3, "toot", 1.6, 1.0)], lines=lines_of(c)[1:2], lead=1.6)
            continue
        if cid == "C32":      # PEAK 3: snap zooms (eyes, hat brim, eyes), then a long warm hold
            ai(cid, 0.6, id="C32a", trim=[0.0, 0.6], mood="off", fb=dict(motion="zoom_in", zoom0=2.0, zoom=2.3, focus=[0.5, 0.3]), sfx=[S(0.0, "whoosh", None, 0.6)])
            ai(cid, 0.5, id="C32b", trim=[0.6, 1.1], fb=dict(motion="zoom_in", zoom0=2.0, zoom=2.2, focus=[0.55, 0.68]), sfx=[S(0.0, "impact", None, 0.5), S(0.0, "riser", 0.6, 0.5)])
            ai(cid, 0.5, id="C32c", trim=[1.1, 1.6], fb=dict(motion="zoom_in", zoom0=2.4, zoom=2.7, focus=[0.5, 0.28]), sfx=[S(0.0, "impact", None, 0.6)])
            ai(cid, 3.0, id="C32d", trim=[1.6, 5.0], mood="tender", ambience="shop", fb=dict(motion="zoom_in", zoom0=1.05, zoom=1.14, focus=[0.5, 0.45], sway=0.2),
               lines=lines_of(c, {0: dict(lead=0.3), 1: dict(gap=0.4)}), fit_clip=False)
            continue
        if cid == "C35":      # Grandma points -> map insert (code) -> the Uncle's power-up
            ls = lines_of(c)
            ai(cid, 2.0, id="C35a", trim=[0.0, 2.0], mood="adventure", fb=dict(motion="zoom_in", zoom=1.1, focus=[0.5, 0.5]), lines=ls[:1], sfx=[S(0.2, "sparkle", None, 0.5)], caption_zone=c["zone"])
            sh("C35I", 1.2, clip=CODE % "C35I", sfx=[S(0.0, "sparkle", None, 0.7), S(0.3, "pen", 1.0, 0.5)], lead=0.0, tail=0.0)
            ai(cid, 2.8, id="C35b", trim=[2.0, 5.0], fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.12, focus=[0.5, 0.45]), lines=ls[1:],
               sfx=[S(0.1, "riser", 1.0, 0.8), S(0.9, "crack", None, 0.9), S(1.0, "flap", 0.7, 0.6)], caption_zone=c["zone"], shake=[dict(t=0.9, d=0.6, amp=10)],
               speedlines=dict(t=0.8, d=1.2, dir="radial"), fit_clip=False)
            continue
        if cid == "C37":
            ai(cid, 2.0, trim=[0.0, 2.0], fb=dict(motion="static", zoom0=1.05, zoom=1.05, focus=[0.5, 0.55], sway=0.0), mood="off", fade_out=0.3, tail=0.0, sfx=[S(0.5, "toot", 0.35, 0.8)], **{k: v for k, v in kw.items() if k not in ("mood",)})
            continue
        ai(cid, dur, fb=fb, sfx=sfx, **kw)
    return shots


spec = dict(title="The Dumpling Boy: intro + Episode 01 v4.4 (How Does Soup Get Inside a Dumpling?)", size=[1080, 1920], fps=30, orientation="both",
            frames_dir="frames/ep01v44", frames_fallback="frames/ep01v43", clips_dir="clips/ep01v44", voice_engine="gpu", voice_cast={"narrator": {"engine": "prerendered", "dir": "tts/gpu", "pitch": 0.84}}, voice_fallback=True, caption_safe=True,
            voice_speed={"boy": 1.28, "uncle": 1.33, "grandma": 1.38, "narrator": 1.3}, max_pause=0.3, crf=23, grain=True, vignette=0.2, sway=0.0,
            caption_y=0.8, caption_y_land=0.86, narrator_echo=True, snap_to_beat=False,
            # series opening song (ACE-Step, original): swap the file here when the creator picks another variant (tools/episode_maker/make_opening_cuts.py)
            audio_tracks=[{"file": "assets/music/opening_intro.wav", "at": 0.0, "gain": 0.7, "mute_music": True, "sfx_gain": 0.45}])

if __name__ == "__main__":
    build()
    spec["shots"] = shots
    out = os.path.join(ROOT, "specs", "episode-01-v4.4.json")
    json.dump(spec, open(out, "w"), indent=1)
    print("wrote", out, len(shots), "shots, scripted total", round(sum(s["dur"] for s in shots), 2), "s")
