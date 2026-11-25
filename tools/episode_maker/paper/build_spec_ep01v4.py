#!/usr/bin/env python3
"""Writes specs/episode-01-v4.json: the full 2:00 edit of Episode 1 V4 (29 clips C01-C29, 44 beats).
    python3 paper/build_spec_ep01v4.py            # writes the spec and prints a timing check (voice vs shot length)
AI clips (specs/clips/ep01v4/Cxx.mp4) are used when present; otherwise the start still plays with local motion (`fb`)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

CODE = "../out/ep01v4/code/%s.mp4"
shots = []


def sh(id, dur, **kw):
    d = dict(id=id, dur=dur, tail=0.0, transition="cut")
    d.update(kw)
    shots.append(d)
    return d


def ai(c, dur, id=None, trim=None, speed=None, fb=None, still=None, **kw):
    """Image-to-video clip shot with automatic animatic fallback to the start still (+ local motion `fb`)."""
    base = dict(motion="zoom_in", zoom0=1.0, zoom=1.1, sway=0.4)
    base.update(fb or {})
    d = dict(clip=f"{c}.mp4", img=still or f"{c}.png", fb=base)
    if trim:
        d["trim"] = trim
    if speed:
        d["speed"] = speed
    d.update(kw)
    return sh(id or c, dur, **d)


def code(c, dur, **kw):
    return sh(c, dur, clip=CODE % c, **kw)


def L(who, text, at, speed=None, gain=None, caption=None, pitch=None, echo=None):
    d = dict(who=who, text=text, at=at)
    if speed: d["speed"] = speed
    if gain: d["gain"] = gain
    if caption: d["caption"] = caption
    if pitch: d["pitch"] = pitch
    if echo is not None: d["echo"] = echo
    return d


def S(t, name, d=None, gain=None):
    e = dict(t=t, name=name)
    if d is not None: e["d"] = d
    if gain is not None: e["gain"] = gain
    return e


def P(kind, t, d, y=0.6, **kw):
    return dict(type="paper", kind=kind, t=t, d=d, y=y, **kw)


# ============================================================ A. COLD OPEN (0:00-0:07.5)
ai("C01", 5.0, id="C01", black=0.6, mood="tension", ambience="street",
   fb=dict(motion="zoom_in", zoom=1.16, focus=[0.5, 0.36], sway=0.5, particles=dict(type="steam", n=10)),
   lines=[L("boy", "Welcome to The Dumpling Boy.", 0.7, 1.05),
          L("boy", "That's my uncle. He's not the host.", 2.5, 1.22),
          L("uncle", "Co-host!", 4.4, 1.1)],
   sfx=[S(0.0, "gong"), S(0.25, "hiss", 2.0, 0.6), S(1.0, "toot", 0.8, 0.45), S(2.55, "toot", 1.1, 0.9), S(4.4, "boing", None, 0.5)],
   punch=[dict(t=2.6, scale=1.07)], shake=[dict(t=2.6, d=0.35, amp=10)],
   cards=[P("lower", 2.5, 2.5, y=0.405, text="UNCLE", text2="co-host (self-appointed)"), P("word", 2.65, 0.9, y=0.12, x=0.8, text="TOOT", size=150, rot=8)])
ai("C01", 1.2, id="C02a", trim=[3.4, 4.6], mood="tension",
   fb=dict(motion="zoom_in", zoom0=1.55, zoom=1.8, focus=[0.5, 0.42]),
   lines=[L("boy", "He is luggage.", 0.15, 1.1)],
   sfx=[S(0.0, "whoosh", None, 0.5)])
ai("C01", 1.3, id="C02b", trim=[0.0, 1.3], reverse=True,
   fb=dict(motion="zoom_out", zoom0=1.4, zoom=1.0, focus=[0.5, 0.4]),
   fx=[dict(type="reel", t=0.0, d=1.3), dict(type="suck", t=0.1, d=1.1, x=0.5, y=0.14, n=20)],
   lines=[L("boy", "Six hours earlier.", 0.3, 1.1)],
   sfx=[S(0.0, "tick", None, 0.9), S(0.05, "rewind", 1.2, 0.8)], speedlines=dict(t=0.05, d=0.5, dir="horizontal"))

# ============================================================ B. THE OLD ROAD AND THE JOURNAL (0:07.5-0:25)
code("C03", 4.5, mood="sparse",
     lines=[L("narrator", "For centuries, travelers carried silk, spices, and ideas.", 0.1, 1.4),
            L("boy", "And, probably, snacks.", 3.45, 1.2)],
     sfx=[S(0.12, "thud", None, 0.9), S(0.14, "page", None, 0.8), S(0.1, "gong", None, 0.7), S(0.9, "pen", 1.8, 0.7), S(1.3, "camel_bell", 1.0, 0.7),
          S(2.3, "snore", 1.8, 0.45), S(3.15, "camel_bell", 1.0, 0.8)])
code("C04", 4.5, lines=[L("narrator", "Near Shanghai, old Qinglong port shipped ceramics along the sea Silk Road.", 0.15, 1.28)],
     sfx=[S(0.2, "gull", 0.8, 0.5), S(1.0, "creak", 1.0, 0.6), S(2.5, "flap", 0.7, 0.6), S(3.3, "creak", 1.0, 0.5), S(3.6, "gull", 0.8, 0.5)])
ai("C05", 4.0, mood="adventure", ambience="street",
   fb=dict(motion="zoom_in", zoom=1.14, focus=[0.46, 0.58], sway=0.6, particles=dict(type="dust", n=14)),
   lines=[L("boy", "Dad left me this journal. One page, one dumpling.", 0.35, 1.12)],
   sfx=[S(0.0, "train", 3.5, 0.55)],
   cards=[P("recap", 0.15, 2.9, y=0.11)])
code("C06", 2.5, mood="sparse",
     lines=[L("boy", "The last page is torn out.", 0.85, 1.15)],
     sfx=[S(0.0, "page", None, 0.7), S(0.22, "page", None, 0.7), S(0.44, "page", None, 0.7), S(0.66, "page", None, 0.7), S(1.0, "riser", 1.0, 0.5), S(1.55, "page", None, 0.7), S(1.9, "tear", 0.5, 0.5)])
code("C07", 2.0, mood="epic",
     sfx=[S(0.06, "gong", None, 1.0), S(0.1, "taiko", None, 0.9), S(0.1, "impact", None, 0.6), S(0.78, "thud", None, 0.9), S(0.82, "boing", None, 0.6), S(1.3, "chime" if False else "ding", None, 0.35), S(1.62, "sparkle", None, 0.5)])

# ============================================================ C. ARRIVAL: THE HOST WALK (0:25-0:38)
ai("C08", 5.0, mood="adventure", ambience="water", whip=True,
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.22, focus=[0.5, 0.55], sway=0.7, particles=dict(type="dust", n=16)),
   lines=[L("boy", "Welcome to old Nanxiang. On your left, a stone bridge.", 0.3, 1.0)],
   sfx=[S(3.9, "bike_bell", None, 0.6)])
ai("C09", 2.5, id="C09a", trim=[0.0, 2.5], ambience="water",
   fb=dict(motion="pan_right", zoom0=1.1, zoom=1.2, focus=[0.55, 0.5], pan=0.08),
   lines=[L("boy", "On your right, two old pagodas.", 0.25, 1.0)], sfx=[S(0.5, "chimes", 1.8, 0.5)])
ai("C09", 2.5, id="C09b", trim=[2.5, 5.0], ambience="water",
   fb=dict(motion="zoom_in", zoom0=1.18, zoom=1.3, focus=[0.45, 0.45]),
   lines=[L("boy", "Behind me, my uncle. Kidnapped by a smell.", 0.2, 1.12)], sfx=[S(0.0, "whoosh", None, 0.6)])
ai("C10", 1.9, id="C10a", trim=[0.0, 1.9],
   fb=dict(motion="zoom_in", zoom0=1.05, zoom=1.2, focus=[0.5, 0.45]),
   lines=[L("uncle", "I smell... destiny.", 0.15, 0.95)], sfx=[S(0.1, "sniff", 0.5, 0.7), S(0.9, "sniff", 0.5, 0.6), S(1.5, "ding", None, 0.3)],
   fx=[dict(type="hearts", t=1.2, n=5, x=0.5, y=0.45)])
sh("C10b", 1.1, img="C08.png", motion="zoom_in", zoom0=1.5, zoom=1.58, focus=[0.52, 0.5], sway=0.0,
   lines=[L("boy", "That's the steamer.", 0.15, 1.15)], sfx=[S(0.0, "tick", None, 0.8)])

# ============================================================ D. THE BURN (0:38-0:54.5)
ai("C11", 4.0, mood="tension",
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.16, focus=[0.5, 0.52], particles=dict(type="steam", n=12)),
   fx=[dict(type="steam", x=[0.3, 0.7], y=0.62, n=6, alpha=0.4)],
   lines=[L("boy", "How does soup get inside a dumpling?", 0.9, 1.0, gain=0.95)],
   sfx=[S(0.3, "lid", None, 0.7), S(0.4, "hiss", 1.6, 0.6)])
ai("C12", 2.0, id="C12a", trim=[0.0, 2.0], mood="adventure",
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.1, focus=[0.5, 0.45]),
   lines=[L("boy", "Uncle, wait. There's soup inside.", 0.3, 1.12)],
   sfx=[S(0.05, "whoosh", None, 0.6), S(0.15, "taiko", None, 0.6), S(1.05, "clink", None, 0.6)])
ai("C12", 2.0, id="C12b", trim=[2.0, 4.0],
   fb=dict(motion="static", zoom0=1.5, zoom=1.7, focus=[0.2, 0.2]),
   punch=[dict(t=0.0, scale=1.25)], speedlines=dict(t=0.0, d=0.6, dir="radial", color="dark"),
   lines=[L("uncle", "For science!", 0.15, 1.0)], sfx=[S(0.0, "taiko", None, 0.9), S(0.0, "whoosh", None, 0.5)])
# The burn: one AI clip (C13), cut into 4 shots in the edit; its last frame is the cold open
ai("C13", 0.9, id="C13a", trim=[0.0, 0.9], mood="tension",
   fb=dict(motion="zoom_in", zoom0=1.3, zoom=1.5, focus=[0.72, 0.3]), still="C13.png",
   sfx=[S(0.0, "pop", None, 0.7), S(0.1, "riser", 1.9, 0.7)])
ai("C13", 0.55, id="C13b", trim=[0.9, 1.45], still="C13.png",
   fb=dict(motion="zoom_in", zoom0=2.2, zoom=2.5, focus=[0.76, 0.24]), shake=[dict(t=0.2, d=0.3, amp=6)])
ai("C13", 0.55, id="C13c", trim=[1.45, 2.0], still="C13.png",
   fb=dict(motion="zoom_in", zoom0=2.1, zoom=2.4, focus=[0.72, 0.13]), shake=[dict(t=0.05, d=0.4, amp=8)])
ai("C13", 2.5, id="C13d", trim=[2.0, 4.5], still="C13_end.png", mood="off",
   fb=dict(motion="zoom_out", zoom0=1.35, zoom=1.0, focus=[0.5, 0.28], sway=0.0),
   impact=dict(t=0.04, amp=34), impact_frame=dict(t=0.0, d=0.2),
   speedlines=dict(t=0.2, d=0.9, dir="radial"),
   sfx=[S(0.0, "crack", None, 0.9), S(0.02, "gong", None, 0.8), S(0.2, "toot", 1.9, 1.0)],
   cards=[P("word", 0.35, 1.6, y=0.15, x=0.5, text="TOOOOOT", size=170, rot=-5)])
ai("C14", 1.7, id="C14a", trim=[0.0, 1.7], mood="off",
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.08, focus=[0.5, 0.5], fx=[dict(type="steam", x=[0.4, 0.6], y=0.3, n=3, alpha=0.5)]),
   lines=[L("uncle", "...There's soup inside.", 0.1, 0.95, gain=0.85, pitch=1.3)], sfx=[S(0.0, "squeak", None, 0.8)])
ai("C14", 2.3, id="C14b", trim=[1.7, 4.0], still="C14.png",
   fb=dict(motion="zoom_in", zoom0=1.05, zoom=1.15, focus=[0.5, 0.58]),
   lines=[L("boy", "We'll be right back.", 0.2, 1.0)],
   sfx=[S(0.0, "elevator", 2.3, 0.55), S(1.1, "toot", 0.25, 0.3), S(1.6, "toot", 0.25, 0.3)],
   cards=[P("intermission", 0.0, 2.3, y=0.34)])

# ============================================================ E. SAFETY SEGMENT (0:54.5-1:08.5)
ai("C15", 5.0, mood="epic", ambience="shop", caption_y=0.84,
   trim=[0.0, 2.5], speed=0.5,
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.12, focus=[0.5, 0.5]),
   lines=[L("boy", "How to eat a soup dumpling.", 0.5, 0.92), L("boy", "Lift.", 2.55, 0.9), L("boy", "Spoon.", 3.25, 0.9), L("boy", "Tiny hole.", 3.95, 0.9)],
   sfx=[S(0.0, "taiko", None, 0.9), S(2.55, "taiko", None, 0.8), S(2.6, "clink", None, 0.6), S(3.25, "taiko", None, 0.8), S(3.95, "taiko", None, 0.9), S(4.0, "hiss", 0.8, 0.5)],
   cards=[P("safety", 0.0, 2.3, y=0.2, **{"in": "slam"}), P("fineprint", 0.5, 1.8, y=0.29),
          P("step", 2.5, 0.65, y=0.2, text="LIFT", **{"in": "slam"}), P("step", 3.2, 0.65, y=0.2, text="SPOON", **{"in": "slam"}), P("step", 3.9, 1.0, y=0.2, text="TINY HOLE", **{"in": "slam"})],
   shake=[dict(t=0.0, d=0.3, amp=12)])
ai("C16", 2.0, id="C16a", trim=[0.0, 1.0], speed=0.5, mood="tension",
   fb=dict(motion="zoom_in", zoom0=1.15, zoom=1.35, focus=[0.55, 0.45]),
   lines=[L("boy", "Wait.", 0.65, 0.9)],
   sfx=[S(0.2, "tick", None, 0.8), S(0.7, "tock", None, 0.8), S(1.2, "tick", None, 0.8), S(1.7, "tock", None, 0.8)],
   cards=[P("step", 0.2, 1.6, y=0.22, text="WAIT", **{"in": "slam"})])
ai("C16", 2.0, id="C16b", trim=[1.0, 3.0], still="C16.png",
   fb=dict(motion="static", zoom0=1.1, zoom=1.1, focus=[0.55, 0.5], shake=[dict(t=0.1, d=1.4, amp=7)]),
   lines=[L("uncle", "Be cool. Be cool.", 0.45, 1.05, gain=0.55)],
   sfx=[S(0.0, "growl", 1.6, 0.9), S(0.2, "rattle", 0.9, 0.6)],
   cards=[P("word", 0.1, 1.5, y=0.2, x=0.5, text="GRRROWL", size=140, rot=-4)])
ai("C17", 2.0, id="C17a", trim=[0.0, 2.0], mood="tender",
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.12, focus=[0.55, 0.45], particles=dict(type="petals", n=10)),
   fx=[dict(type="hearts", t=1.2, n=5, x=0.6, y=0.5)],
   lines=[L("boy", "Sip.", 0.2, 1.0), L("uncle", "For science.", 0.95, 0.95, gain=0.6)],
   sfx=[S(0.75, "sip", None, 0.8), S(1.35, "ding", None, 0.5), S(1.5, "heart", None, 0.6)])
ai("C17", 3.0, id="C17b", trim=[2.0, 5.0],
   fb=dict(motion="zoom_in", zoom0=1.1, zoom=1.2, focus=[0.55, 0.45]),
   lines=[L("boy", "He rates everything ten. Yesterday, a napkin.", 0.5, 1.22)],
   sfx=[S(0.1, "pop", None, 0.7), S(0.12, "heart", None, 0.4)],
   cards=[P("rating", 0.05, 2.9, y=0.3, rot=-5, **{"in": "pop"}, slide_t=0.45, slide_d=0.5)])

# ============================================================ F. "A LITTLE HISTORY": LEGEND SAYS (1:08.5-1:31.5)
code("C18", 6.0, mood="sparse",
     lines=[L("boy", "A little history.", 0.15, 1.0),
            L("narrator", "Legend says, around eighteen seventy-one, a shop in Nanxiang sold one big meat bun.", 2.0, 1.3, caption="Legend says, around 1871, a shop in Nanxiang sold one big meat bun.")],
     sfx=[S(0.0, "gong", None, 0.7), S(0.9, "stamp", None, 1.0), S(1.0, "impact", None, 0.5), S(1.5, "tear", 0.5, 0.7), S(1.55, "swoosh_big", 0.5, 0.5), S(1.95, "gong", None, 0.55), S(3.0, "rooster", 1.4, 0.45), S(5.0, "boing", None, 0.3)])
code("C19", 6.0,
     lines=[L("narrator", "So he made it smaller, and added soup, set as jelly, that melts when steamed.", 0.3, 1.12)],
     sfx=[S(0.1, "swoosh_big", 0.5, 0.5), S(1.05, "boing", None, 0.4), S(3.6, "chop", None, 0.9), S(3.8, "chop", None, 0.9), S(4.0, "chop", None, 0.9), S(4.2, "chop", None, 0.9),
          S(4.7, "flutter", 0.5, 0.7), S(5.05, "hiss", 0.9, 0.5), S(5.2, "sparkle", None, 0.7)])
ai("C20", 2.0, id="C20a", trim=[0.0, 2.0], mood="adventure",
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.12, focus=[0.5, 0.5]),
   fx=[dict(type="flash", t=0.0, d=0.25)],
   lines=[L("boy", "That's not what he looked like.", 1.45, 1.2)],
   sfx=[S(0.0, "scratch", None, 0.9), S(0.5, "toot", 0.3, 0.5)])
sh("C20b", 1.0, img="C14.png", motion="zoom_in", zoom0=1.55, zoom=1.6, focus=[0.45, 0.78], sway=0.0,
   sfx=[S(0.0, "tick", None, 0.7)])
ai("C20", 1.0, id="C20c", trim=[3.0, 4.0],
   fb=dict(motion="zoom_in", zoom0=1.25, zoom=1.4, focus=[0.45, 0.3]),
   lines=[L("uncle", "He had my energy.", 0.0, 1.15)], punch=[dict(t=0.0, scale=1.15)])
code("C21", 3.0, lines=[L("boy", "Legend. That's historian for 'please don't quote me.'", 0.25, 1.12)],
     sfx=[S(1.2, "stamp", None, 0.9), S(1.9, "tick", None, 0.7)])
code("C22", 4.0, lines=[L("boy", "Many in Nanxiang still say 'xiaolong mantou.'", 0.15, 1.12, caption="Many in Nanxiang still say \"xiaolong mantou.\""),
                        L("uncle", "Two names? Two dumplings.", 2.35, 1.05)],
     sfx=[S(0.15, "pop", None, 0.8), S(3.2, "boing", None, 0.8), S(3.38, "boing", None, 0.6)])

# ============================================================ G. DAD'S PAGE AND THE BRIDGE (1:31.5-1:45.5)
ai("C23", 4.5, mood="tender", transition="fade", fade=0.5, grade="sepia",
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.12, focus=[0.45, 0.55], particles=dict(type="dust", n=24), sway=0.2),
   fx=[dict(type="steam", x=[0.55, 0.75], y=0.62, n=5, alpha=0.35)],
   lines=[L("boy", "Dad wrote: life is like a soup dumpling.", 0.7, 0.95, gain=0.85)])
code("C24", 4.5, lines=[L("boy", "Rush it, you get burned. Be patient, you get the best part.", 0.7, 1.0, gain=0.9)],
     sfx=[S(1.0, "sparkle", None, 0.5), S(2.3, "sparkle", None, 0.6), S(3.0, "chimes", 1.8, 0.4)])
ai("C25", 5.0, mood="tender", ambience="water", caption_y=0.84,
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.14, focus=[0.52, 0.56], particles=dict(type="dust", n=14)),
   lines=[L("uncle", "Your dad picked a good first page.", 0.4, 1.0, gain=0.9), L("boy", "Co-host.", 3.0, 0.95)],
   sfx=[S(0.3, "clink", None, 0.5), S(3.1, "ding", None, 0.6), S(3.15, "sparkle", None, 0.6), S(4.0, "sniff", 0.4, 0.4)],
   cards=[P("lower", 1.9, 3.0, y=0.36, text="UNCLE", text2="co-host (self-appointed)", text2b="co-host (approved)", flip_t=3.0)])

# ============================================================ H. THE CLIFFHANGER AND THE SIGN-OFF (1:45.5-2:00)
sh("C26a", 1.0, img="C13.png", mood="adventure", motion="zoom_in", zoom0=1.5, zoom=1.7, focus=[0.76, 0.26], sway=0.0, whip=True,
   speedlines=dict(t=0.0, d=0.5, dir="radial"), sfx=[S(0.0, "whoosh", None, 0.7), S(0.25, "toot", 0.25, 0.5)])
ai("C26", 3.0, id="C26b", trim=[0.0, 3.0],
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.12, focus=[0.5, 0.5]),
   lines=[L("grandma", "That hat! He sat right there. Burned his tongue.", 0.25, 1.0)],
   punch=[dict(t=0.9, scale=1.18), dict(t=1.3, scale=1.3)], speedlines=dict(t=0.0, d=0.7, dir="horizontal"),
   sfx=[S(0.0, "riser", 0.8, 0.6), S(0.9, "impact", None, 0.5), S(1.3, "impact", None, 0.5)])
ai("C27", 1.5, id="C27a", trim=[0.0, 1.5], mood="adventure",
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.1, focus=[0.5, 0.5]),
   lines=[L("boy", "Sound familiar?", 0.3, 1.0)], sfx=[S(0.1, "boing", None, 0.6)])
ai("C27", 1.8, id="C27b", trim=[1.5, 3.3], mood="epic",
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.15, focus=[0.45, 0.5]),
   lines=[L("grandma", "Then he went south. To the dim sum city.", 0.1, 1.0)], sfx=[S(0.0, "whoosh", None, 0.5)])
code("C27I", 1.7, sfx=[S(0.0, "sparkle", None, 0.7), S(0.3, "chug", 1.3, 0.5)])
ai("C28", 4.0, mood="tender", transition="fade", fade=0.3,
   fb=dict(motion="zoom_in", zoom0=1.0, zoom=1.1, focus=[0.5, 0.45], particles=dict(type="dust", n=14)),
   lines=[L("boy", "Dad was right... the best part is worth the wait.", 0.75, 0.97)],
   cards=[P("next", 2.3, 1.7, y=0.6)])
ai("C29", 1.5, fade_out=0.3,
   fb=dict(motion="static", zoom0=1.05, zoom=1.05, focus=[0.5, 0.55], sway=0.0, shake=[dict(t=0.5, d=0.2, amp=6)]),
   sfx=[S(0.5, "toot", 0.35, 0.8)], mood="off")

spec = dict(title="Episode 01 V4: Uncle vs. Soup Dumpling (animatic)", size=[1080, 1920], fps=30,
            frames_dir="frames/ep01v4", frames_fallback="frames/ep01v4_placeholder", clips_dir="clips/ep01v4",
            grain=True, vignette=0.22, sway=0.0, caption_y=0.8, narrator_echo=True, snap_to_beat=False, shots=shots)

if __name__ == "__main__":
    out = os.path.join(ROOT, "specs", "episode-01-v4.json")
    json.dump(spec, open(out, "w"), indent=1)
    print("wrote", out, len(shots), "shots, scripted total", round(sum(s["dur"] for s in shots), 2), "s")
    # timing check: spoken lines versus shot lengths
    import make_episode as m
    from synth import SR
    t0, bad = 0.0, 0
    for s in shots:
        end_voice, prev_end = 0.0, 0.0
        for ln in s.get("lines", []):
            a = m.tts(ln["who"], ln["text"], ln.get("speed"), ln.get("pitch"))
            st, en = ln["at"], ln["at"] + len(a) / SR
            if en > s["dur"] + 0.02:
                print(f"  OVERFLOW {s['id']}: '{ln['text'][:34]}' ends {en:.2f} > shot {s['dur']:.2f}"); bad += 1
            if st < prev_end - 0.02:
                print(f"  OVERLAP  {s['id']}: '{ln['text'][:34]}' starts {st:.2f} < previous end {prev_end:.2f}"); bad += 1
            prev_end = en
        t0 += s["dur"]
    print("timing problems:", bad, "| total", round(t0, 2))
