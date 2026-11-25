#!/usr/bin/env python3
"""Writes specs/episode-01-v4.3.json: series intro (about 8.5 s) + Episode 1 v4.3 (2:30, 29 clips C01-C29, scripts/episode-01-v4.3.md).
    python3 paper/build_spec_ep01v43.py
AI clips (clips/ep01v43/<id>.mp4 and <id>_land.mp4) are used when present; otherwise the still (frames/ep01v43/<id>.png / _land) plays with the
local camera move `fb` (the "animatic"). Voice lines come from paper/ep01v43_lines.py and are laid out automatically after each other."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
from ep01v43_lines import LINES

CODE = "../out/ep01v43/code/%s.mp4"
shots = []
FLOOR = 0.86


def sh(id, dur, **kw):
    if dur >= 3.0 and not id.startswith(("C27", "C19", "C22")):      # the script's minimum lengths are generous: voices set the real length
        dur = round(dur * FLOOR, 2)
    d = dict(id=id, dur=dur, tail=0.15, lead=0.2, transition="cut")
    d.update(kw)
    shots.append(d)
    return d


def ai(c, dur, id=None, trim=None, speed=None, fb=None, still=None, **kw):
    """Image-to-video clip shot; falls back to the start still + local camera move `fb` until the AI clip exists."""
    base = dict(motion="zoom_in", zoom0=1.0, zoom=1.1, sway=0.4)
    base.update(fb or {})
    d = dict(clip=f"{c}.mp4", img=still or f"{c}.png", fb=base)
    if trim: d["trim"] = trim
    if speed: d["speed"] = speed
    if not trim and not speed:
        d["fit_clip"] = True
    d.update(kw)
    return sh(id or c, dur, **d)


def code(c, dur, **kw):
    return sh(c, dur, clip=CODE % c, **kw)


def V(clip, idx=None, **over):
    """Spoken lines of a clip (all, or the given indexes); over: {index: {gap/lead/gain/at/...}} applied per line."""
    out = []
    for i, (who, note, text) in enumerate(LINES[clip]):
        if idx is not None and i not in idx:
            continue
        d = dict(who=who, text=text, gap=0.08)
        d.update(over.get(i, {}))
        out.append(d)
    return out


def S(t, name, d=None, gain=None):
    e = dict(t=t, name=name)
    if d is not None: e["d"] = d
    if gain is not None: e["gain"] = gain
    return e


def FACT(t, d, label, text, y=0.2):
    return dict(type="fact", t=t, d=d, label=label, text=text, y=y, y_land=0.28)


# ============================================================ SERIES INTRO (about 8.5 s): independent of the story
ai("I1", 1.2, fb=dict(motion="zoom_in", zoom=1.14, focus=[0.55, 0.45], sway=0.3, particles=dict(type="steam", n=8)), mood="adventure",
   sfx=[S(0.0, "tick", None, 0.5), S(0.3, "crunch", None, 0.9), S(0.55, "hiss", 0.8, 0.5)], punch=[dict(t=0.3, scale=1.06)])
ai("I2", 1.0, fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.2, focus=[0.5, 0.45]), whip=True,
   sfx=[S(0.1, "splash", None, 0.8), S(0.3, "sparkle", None, 0.5)])
ai("I3", 1.3, fb=dict(motion="pan_right", zoom0=1.05, zoom=1.12, focus=[0.55, 0.55], pan=0.06), whip=True,
   sfx=[S(0.1, "plop", None, 0.6), S(0.35, "laugh", None, 0.8), S(0.7, "plop", None, 0.5), S(1.0, "bloop", None, 0.5)])
ai("I5", 1.3, fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.2, focus=[0.5, 0.5], particles=dict(type="dust", n=14)), whip=True,
   sfx=[S(0.0, "rolling", 1.3, 0.8), S(0.2, "chomp", None, 0.7), S(0.7, "chomp", None, 0.7)], speedlines=dict(t=0.0, d=1.2, dir="radial"))
ai("I5b", 0.8, fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.15, focus=[0.5, 0.5]),
   sfx=[S(0.0, "rolling", 0.8, 0.8), S(0.35, "chomp", None, 0.8)])
ai("I5c", 0.7, fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.25, focus=[0.35, 0.55]),
   sfx=[S(0.05, "shing", None, 0.8), S(0.25, "shing", None, 0.8), S(0.45, "shing", None, 0.8)], speedlines=dict(t=0.0, d=0.7, dir="horizontal"))
ai("I6", 0.7, fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.2, focus=[0.55, 0.5]),
   sfx=[S(0.2, "chomp", None, 1.0), S(0.25, "impact", None, 0.6)], impact=dict(t=0.2, amp=18), speedlines=dict(t=0.0, d=0.5, dir="radial"))
code("C90", 1.5, mood="adventure", sfx=[S(0.0, "gong", None, 0.8), S(0.05, "taiko", None, 0.8), S(0.1, "sting", None, 0.8)])

# ============================================================ A. COLD OPEN (0:00-0:12)
ai("C01", 5.5, black=0.5, mood="off", ambience="shop",
   fb=dict(motion="zoom_in", zoom=1.18, focus=[0.5, 0.4], sway=0.4, particles=dict(type="steam", n=10)),
   lines=V("C01", over={0: dict(lead=0.6)}), sfx=[S(0.5, "hiss", 2.5, 0.5), S(1.2, "creak", 0.8, 0.3)])
ai("C02", 6.5, ambience="water",
   fb=dict(motion="zoom_in", zoom=1.1, focus=[0.45, 0.5], sway=0.4),
   lines=V("C02", over={0: dict(gap=-0.3)}), sfx=[S(5.9, "thud", None, 0.7), S(5.95, "page", None, 0.6)])

# ============================================================ B. THE OLD ROAD AND THE JOURNAL (0:12-0:30)
code("C03", 5.5, mood="sparse", transition="fade", fade=0.35, lead=0.3, lines=V("C03"),
     sfx=[S(0.1, "thud", None, 0.8), S(0.14, "page", None, 0.8), S(1.4, "pen", 1.8, 0.6), S(2.6, "camel_bell", 1.0, 0.5), S(4.3, "camel_bell", 1.0, 0.7)])
code("C04", 6.0, lead=0.3, lines=V("C04"),
     cards=[FACT(1.0, 4.2, "QINGLONG PORT", "Its ceramics turn up in Japan and Korea")],
     sfx=[S(0.3, "gull", 0.8, 0.5), S(1.4, "creak", 1.0, 0.6), S(3.2, "flap", 0.7, 0.6), S(5.0, "creak", 1.0, 0.5), S(5.4, "gull", 0.8, 0.5)])
ai("C05", 5.5, mood="off", ambience="street", fb=dict(motion="zoom_in", zoom=1.14, focus=[0.46, 0.58], sway=0.6, particles=dict(type="dust", n=10)),
   lines=V("C05", over={0: dict(lead=0.4), 1: dict(gap=0.1)}), sfx=[S(0.0, "train", 5.2, 0.5)])

# ============================================================ C. ARRIVAL: NANXIANG (0:30-0:46.5)
code("C06", 2.5, mood="adventure", sfx=[S(0.0, "gong", None, 0.9), S(0.05, "taiko", None, 0.9), S(0.1, "sting", None, 0.7)])
ai("C07", 5.0, mood="off", ambience="water", fb=dict(motion="zoom_out", zoom0=1.12, zoom=1.0, focus=[0.5, 0.5], sway=0.5),
   lines=V("C07"), sfx=[S(3.6, "bike_bell", None, 0.5)])
ai("C08", 9.0, ambience="water", fb=dict(motion="zoom_in", zoom=1.18, focus=[0.5, 0.5], sway=0.3),
   lines=V("C08", over={2: dict(gap=0.5), 3: dict(lead=0.2)}), sfx=[S(0.2, "chimes", 3.0, 0.5), S(5.0, "chimes", 3.0, 0.4)])

# ============================================================ D. GRANDMA'S STALL: THE SOUP SECRET (0:46.5-1:14.5)
ai("C09", 7.0, ambience="shop", fb=dict(motion="zoom_in", zoom=1.12, focus=[0.5, 0.55], sway=0.4, particles=dict(type="steam", n=6)),
   lines=V("C09"), sfx=[S(0.3, "lid", None, 0.5), S(2.0, "hiss", 1.5, 0.4)])
ai("C10", 6.0, ambience="shop", fb=dict(motion="zoom_in", zoom0=1.05, zoom=1.2, focus=[0.5, 0.55]),
   lines=V("C10"), sfx=[S(0.5, "chop", None, 0.9), S(0.7, "chop", None, 0.9), S(0.9, "chop", None, 0.9), S(1.1, "chop", None, 0.9), S(2.6, "page", None, 0.3)])
# PEAK 1: the jelly reveal (wonder): lines first, then 5 fast macro cuts, whip-pans, one slow-motion ripple, a held beat
ai("C11", 4.4, id="C11a", mood="tender", fb=dict(motion="zoom_in", zoom=1.12, focus=[0.5, 0.5], particles=dict(type="steam", n=12)),
   trim=[0.0, 4.4], lines=V("C11", [0]), sfx=[S(0.2, "lid", None, 0.7), S(0.3, "hiss", 2.0, 0.6)],
   cards=[FACT(0.3, 3.5, "SOUP SECRET", "The soup goes in solid", y=0.18)])
ai("C11", 0.8, id="C11b", trim=[0.5, 1.3], whip=True, fb=dict(motion="zoom_in", zoom0=1.6, zoom=1.9, focus=[0.45, 0.55]), sfx=[S(0.0, "sparkle", None, 0.6)])
ai("C11", 0.8, id="C11c", trim=[1.3, 2.1], whip=True, fb=dict(motion="zoom_in", zoom0=2.2, zoom=2.5, focus=[0.55, 0.5]), sfx=[S(0.0, "whoosh", None, 0.5)])
ai("C11", 2.4, id="C11d", trim=[2.1, 3.3], speed=0.6, whip=True, fb=dict(motion="zoom_in", zoom0=1.9, zoom=2.1, focus=[0.5, 0.45]),
   lines=V("C11", [1], over={0: dict(lead=0.3)}), sfx=[S(0.1, "ding", None, 0.5), S(0.3, "sparkle", None, 0.7)])
ai("C11", 0.8, id="C11e", trim=[3.3, 4.1], whip=True, mood="off", fb=dict(motion="zoom_out", zoom0=1.5, zoom=1.15, focus=[0.5, 0.5]), sfx=[S(0.0, "whoosh", None, 0.5)])
ai("C11", 1.2, id="C11f", still="C11.png", trim=[4.1, 5.3], fb=dict(motion="zoom_in", zoom0=1.05, zoom=1.1, focus=[0.5, 0.5], particles=dict(type="steam", n=8)))
ai("C12", 7.0, mood="off", ambience="shop", fb=dict(motion="zoom_in", zoom=1.12, focus=[0.5, 0.5], sway=0.4),
   lines=V("C12", over={1: dict(gap=0.2), 2: dict(gap=0.1)}), sfx=[S(1.5, "page", None, 0.3), S(4.0, "page", None, 0.3)])

# ============================================================ E. THE BURN AND THE SAFE WAY (1:14.5-1:42.5)
ai("C13", 4.0, ambience="shop", fb=dict(motion="zoom_in", zoom=1.1, focus=[0.55, 0.5], sway=0.4),
   lines=V("C13", over={0: dict(gap=-0.15), 1: dict(gap=0.1)}), sfx=[S(0.0, "thud", None, 0.6), S(0.6, "whoosh", None, 0.6)])
# PEAK 2: the burn (the main gag): ECU mouth, ECU eye, impact frame, wide rocket; silence, then one long toot
ai("C14", 1.0, id="C14a", still="C14.png", trim=[0.0, 1.0], mood="tension", fb=dict(motion="zoom_in", zoom0=1.4, zoom=1.7, focus=[0.5, 0.35]),
   sfx=[S(0.0, "pop", None, 0.8), S(0.1, "riser", 1.9, 0.7)])
ai("C14", 0.55, id="C14b", still="C14.png", trim=[1.0, 1.55], fb=dict(motion="zoom_in", zoom0=2.3, zoom=2.6, focus=[0.52, 0.3]), shake=[dict(t=0.2, d=0.3, amp=6)])
ai("C14", 0.55, id="C14c", still="C14.png", trim=[1.55, 2.1], fb=dict(motion="zoom_in", zoom0=2.1, zoom=2.4, focus=[0.5, 0.12]), shake=[dict(t=0.05, d=0.4, amp=8)])
ai("C14", 1.9, id="C14d", still="C14_end.png", trim=[2.1, 4.0], mood="off", fb=dict(motion="zoom_out", zoom0=1.3, zoom=1.0, focus=[0.5, 0.3], sway=0.0),
   impact=dict(t=0.04, amp=34), impact_frame=dict(t=0.0, d=0.2), speedlines=dict(t=0.2, d=0.9, dir="radial"),
   sfx=[S(0.0, "crack", None, 0.9), S(0.02, "gong", None, 0.7), S(0.3, "toot", 1.6, 1.0)])
ai("C15", 4.0, ambience="shop", fb=dict(motion="zoom_in", zoom=1.1, focus=[0.5, 0.5], sway=0.4),
   lines=V("C15", over={0: dict(lead=0.4)}), sfx=[S(0.0, "squeak", None, 0.7), S(2.2, "chug", 0.8, 0.3)])
ai("C16", 5.0, ambience="shop", fb=dict(motion="zoom_in", zoom0=1.05, zoom=1.2, focus=[0.5, 0.5]),
   lines=V("C16", over={0: dict(lead=0.5)}), sfx=[S(2.8, "clink", None, 0.6)])
ai("C17", 5.0, ambience="shop", fb=dict(motion="zoom_in", zoom0=1.1, zoom=1.3, focus=[0.5, 0.5]),
   lines=V("C17"), sfx=[S(0.5, "pop", None, 0.4), S(0.8, "hiss", 1.2, 0.5)])
ai("C18", 6.0, mood="tender", ambience="shop", fb=dict(motion="zoom_in", zoom=1.14, focus=[0.45, 0.45], sway=0.3),
   lines=V("C18", over={1: dict(gap=0.3)}), sfx=[S(0.4, "sip", None, 0.8), S(0.9, "ding", None, 0.4)])

# ============================================================ F. THE SCROLL: LEGEND SAYS (1:42.5-2:05.5)
code("C19", 3.0, mood="sparse", lines=V("C19", over={0: dict(lead=0.2)}), sfx=[S(1.0, "gong", None, 0.7), S(1.0, "swoosh_big", 1.0, 0.5), S(1.1, "page", None, 0.7)])
code("C20", 6.0, lead=0.4, lines=V("C20"), sfx=[S(2.0, "rooster", 1.4, 0.4)])
code("C21", 5.0, lead=0.3, lines=V("C21"), sfx=[S(0.9, "swoosh_big", 0.5, 0.5), S(2.6, "boing", None, 0.4), S(3.2, "chop", None, 0.8), S(3.4, "chop", None, 0.8),
                                                S(4.2, "sparkle", None, 0.7)])
code("C22", 3.0, lead=0.2, lines=V("C22"), sfx=[S(1.6, "page", None, 0.7), S(2.6, "gong", None, 0.5)])
ai("C23", 6.0, mood="off", ambience="shop", fb=dict(motion="zoom_in", zoom=1.12, focus=[0.45, 0.5], sway=0.3),
   lines=V("C23", over={1: dict(gap=0.3)}), sfx=[S(0.2, "page", None, 0.5), S(2.6, "toot", 0.2, 0.3)])

# ============================================================ G. DAD'S SEAT (2:05.5-2:21)
# PEAK 3: Grandma sees the hat: snap zooms (eyes, hat brim, eyes), then a long warm hold; piano
ai("C24", 0.6, id="C24a", still="C24.png", mood="off", fb=dict(motion="zoom_in", zoom0=2.0, zoom=2.3, focus=[0.5, 0.3]), sfx=[S(0.0, "whoosh", None, 0.6)])
ai("C24", 0.5, id="C24b", still="C24.png", fb=dict(motion="zoom_in", zoom0=2.0, zoom=2.2, focus=[0.55, 0.68]), sfx=[S(0.0, "impact", None, 0.5), S(0.0, "riser", 0.6, 0.5)])
ai("C24", 0.5, id="C24c", still="C24.png", fb=dict(motion="zoom_in", zoom0=2.4, zoom=2.7, focus=[0.5, 0.28]), sfx=[S(0.0, "impact", None, 0.6)])
ai("C24", 5.4, id="C24d", still="C24.png", mood="tender", ambience="shop", fb=dict(motion="zoom_in", zoom0=1.05, zoom=1.14, focus=[0.5, 0.45], sway=0.2),
   lines=V("C24", over={0: dict(lead=0.3), 1: dict(gap=0.4)}))
ai("C25", 6.0, mood="tender", ambience="night", transition="fade", fade=0.5, grade="sepia",
   fb=dict(motion="zoom_in", zoom=1.12, focus=[0.5, 0.55], particles=dict(type="dust", n=20), sway=0.2),
   fx=[dict(type="steam", x=[0.55, 0.75], y=0.62, n=5, alpha=0.35)], lines=V("C25", over={0: dict(lead=0.4)}))
ai("C26", 3.0, mood="tender", ambience="shop", transition="fade", fade=0.4, fb=dict(motion="zoom_in", zoom=1.08, focus=[0.5, 0.5], sway=0.2),
   lines=V("C26", over={0: dict(lead=0.6), 1: dict(gap=0.3)}), sfx=[S(0.3, "clink", None, 0.4)])

# ============================================================ H. THE CLIFFHANGER AND THE SIGN-OFF (2:21-2:30)
ai("C27", 2.0, id="C27a", mood="adventure", fb=dict(motion="zoom_in", zoom=1.12, focus=[0.5, 0.5], sway=0.4),
   lines=V("C27", [0], over={0: dict(lead=0.2)}), sfx=[S(0.2, "sparkle", None, 0.5)])
code("C27I", 1.6, lines=V("C27", [1]), sfx=[S(0.0, "sparkle", None, 0.7), S(0.3, "pen", 1.0, 0.5)])
ai("C28", 4.0, mood="tender", transition="fade", fade=0.3, fb=dict(motion="zoom_in", zoom=1.1, focus=[0.5, 0.45], particles=dict(type="dust", n=10)),
   lines=V("C28", over={0: dict(lead=0.5)}))
ai("C29", 1.5, mood="off", fade_out=0.3, tail=0.0, fb=dict(motion="static", zoom0=1.05, zoom=1.05, focus=[0.5, 0.55], sway=0.0, shake=[dict(t=0.5, d=0.2, amp=6)]),
   sfx=[S(0.5, "toot", 0.35, 0.8)])

spec = dict(title="The Dumpling Boy: intro + Episode 01 v4.3 (How Does Soup Get Inside a Dumpling?)", size=[1080, 1920], fps=30, orientation="both",
            frames_dir="frames/ep01v43", frames_fallback="frames/ep01v43", clips_dir="clips/ep01v43",
            voice_engine="gpu", voice_fallback=True, caption_safe=True, voice_speed={"boy": 1.17, "uncle": 1.3, "grandma": 1.3, "narrator": 1.2}, max_pause=0.35, crf=23, grain=True, vignette=0.2, sway=0.0, caption_y=0.8, caption_y_land=0.86,
            narrator_echo=True, snap_to_beat=False, shots=shots)

if __name__ == "__main__":
    out = os.path.join(ROOT, "specs", "episode-01-v4.3.json")
    json.dump(spec, open(out, "w"), indent=1)
    print("wrote", out, len(shots), "shots, scripted total", round(sum(s["dur"] for s in shots), 2), "s")
