#!/usr/bin/env python3
"""Animatic renderer (voice-first). Usage:
    python3 animatic/render.py ep01 [--land] [--preview]
Builds the timeline from scripts/episode-0N-v5.md + the voice files (animatic/voices.py), draws storyboard cards, word-pop captions,
punch/Ken-Burns moves, a timer + shot id, mixes voice + SFX (synth.py) + music + opening sting, ducks, normalises to -14 LUFS, encodes with ffmpeg.
"""
import json, os, re, subprocess, sys, time
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw
from scipy import signal
HERE = os.path.dirname(os.path.abspath(__file__))
EM = os.path.dirname(HERE)
sys.path.insert(0, EM); sys.path.insert(0, HERE)
import synth, sfx_extra, sfx_extra2  # noqa: F401
import shots as S
import art
from art import CREAM, LEAF, ORANGE, PEACH, BROWN, font, FONT

SR = synth.SR
FPS = 24
OUT = S.OUT
STING = os.path.join(EM, "out", "opening-song-variants", "flac", "intro_b__s212.flac")     # style 2 (male) song sting, the current placeholder
CAP_FILL, CAP_ACTIVE = CREAM, LEAF

# ---------------------------------------------------------------- audio
SFXRULES = [  # (regex on SFX+EDIT text, sfx name, offset (s, or 'mid'/'end'), gain, duration or None)
    (r"thunder", "impact", 0.1, 0.55, None), (r"\bgong\b", "gong", 0.0, 0.45, 2.5), (r"whoosh|scroll-edge wipe|whizz", "whoosh", 0.05, 0.5, None),
    (r"\bhiss|steamer hiss|steam-swirl", "hiss", 0.25, 0.22, 1.0), (r"chop-chop", "chop", 0.2, 0.7, None), (r"splash", "splash", 1.3, 0.5, None),
    (r"crunch", "crunch", 0.1, 0.5, None), (r"chomp", "chomp", "mid", 0.6, None), (r"shing", "shing", 0.9, 0.45, None), (r"rolling|thumping rolls", "rolling", 0.0, 0.35, None),
    (r"riser|rising whine|tremolo", "riser", 0.0, 0.3, "dur"), (r"crack", "crack", "mid", 0.6, None), (r"tiny kettle toot|ear toot|one long toot|toot", "toot", "mid", 0.45, 1.0),
    (r"sparkle", "sparkle", 0.6, 0.35, None), (r"clink", "clink", 0.1, 0.45, None), (r"creak|wood creak", "creak", "mid", 0.35, None),
    (r"bike bell", "bike_bell", 0.4, 0.3, None), (r"camel sting|camel", "camel_bell", 0.8, 0.7, None), (r"page-turn|paper unrolling|page rustle", "page", 0.0, 0.35, None),
    (r"squeak", "squeak", "end", 0.5, None), (r"plink|comic ding|\bding\b", "ding", 0.1, 0.3, None), (r"bubble", "bloop", "mid", 0.4, None),
    (r"sub drop|impact crack|big chomp", "impact", 0.0, 0.7, None), (r"violin sting|sting", "sting", 0.1, 0.35, None), (r"\bsip\b|gentle sip", "sip", "end", 0.4, None),
    (r"rattl", "rattle", 0.3, 0.3, None), (r"soft poke", "pop", 0.0, 0.4, None), (r"ink splat|stamp", "stamp", 0.0, 0.5, None),
    (r"reverse cymbal|crash cymbal", "swoosh_big", 0.0, 0.5, None),
]


def sfx_for(o, ep):
    """List of (abs time, sfx name, gain, d) for one laid-out shot: named SFX from the SFX column + a tick on every cut (+-40 ms)."""
    ev, t0, dur = [], o["t0"], o["dur"]
    txt = (o["sfx"] + " ; " + o["edit"]).lower()
    opening = ep == "ep01" and o["id"] in S.OPEN
    for rx, nm, off, g, d in SFXRULES:
        if re.search(rx, o["sfx"].lower()):
            if nm == "chop":
                for i, tt in enumerate((0.2, 0.55, 0.9)):
                    ev.append((t0 + tt, "chop", g, None))
                continue
            at = dur * 0.5 if off == "mid" else (max(0.0, dur - 0.9) if off == "end" else off)
            ev.append((t0 + at, nm, g * (0.6 if opening else 1.0), dur if d == "dur" else d))
    for (a, b, typ, ct) in o["segs"][1:] if len(o["segs"]) > 1 else []:
        nm = "thud" if ("thud" in o["sfx"].lower() and typ == "punch") else ("pop" if typ in ("card", "ins") else "tick")
        if ep == "ep01" and o["id"] in ("C21", "C22", "C23"):
            nm = "pop"
        ev.append((t0 + a - 0.01, nm, 0.55, None))
    if not any(abs(e[0] - t0) < 0.05 for e in ev) and not (opening and o["id"] == "C21"):
        ev.append((t0 - 0.01, "tick", 0.4, None))       # a sound on the hard cut into this shot
    return ev


def put(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i < 0 or i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def mood_for(o, ep):
    i = o["id"]
    if ep == "ep01":
        if i in ("C01", "C19", "C20") or i in S.OPEN:
            return "off"
        if i in ("C10", "C11", "C12", "K02", "K03", "K04"):
            return "adventure"
        if i in ("C17", "C15", "C16"):
            return "tender"
    else:
        if i in ("C09", "C23", "C01") or i == "K01":
            return "off"
        if i in ("C10", "C11", "C12", "C13", "C14", "C15", "C22"):
            return "tender" if i not in ("C12", "C13") else "sparse"
        if i == "C20":
            return "adventure"
    return {"fast": "cozy", "medium": "cozy", "calm": "tender"}[o["pace"]]


def audio(ep, lay, total, out_wav, silences):
    n = int(total * SR) + SR
    voice, sfx, amb, mus = (np.zeros(n, np.float32) for _ in range(4))
    for o in lay:
        v = o["voicej"]
        if v and o["line_at"] is not None:
            w, sr0 = sf.read(os.path.join(OUT, "voices", ep, o["id"] + ".wav"), dtype="float32")
            put(voice, signal.resample_poly(w, SR, sr0).astype(np.float32), o["t0"] + o["line_at"])
        for at, nm, g, d in sfx_for(o, ep):
            f = synth.SFX[nm]
            put(sfx, f(d) if d else f(), at, g)
        txt = o["sfx"].lower()
        kind = "water" if "canal" in txt else ("shop" if re.search(r"steamer|stall|kettle|barrel", txt) else None)
        if kind:
            put(amb, synth.ambience(kind, o["dur"] + 0.6), o["t0"] - 0.3, 0.55)
    # music with mood automation (legacy beds on the 96 BPM grid, "adventure" 120 BPM)
    moods = [(o["t0"], mood_for(o, ep)) for o in lay]
    chg = [moods[0]] + [m for p_, m in zip(moods, moods[1:]) if p_[1] != m[1]]

    def mood_at(t):
        m = chg[0][1]
        for st, md in chg:
            if t + 1e-6 >= st:
                m = md
        return m
    mm = synth.music(total, mood_at, change_times=[c[0] for c in chg])
    mus[: len(mm)] = mm
    # held tone: Episode 1 C19-C20 (music drops out on "Wait", one tone, cut at the end)
    if ep == "ep01":
        a = [o for o in lay if o["id"] in ("C19", "C20")]
        t_a, t_b = a[0]["t0"] + 0.5, a[-1]["t0"] + a[-1]["dur"]
        tt = np.arange(int((t_b - t_a) * SR)) / SR
        put(amb, (np.sin(2 * np.pi * 392 * tt) * 0.5 * np.minimum(1, tt / 0.6)).astype(np.float32), t_a, 0.12)
    # opening song sting: first 7.5 s from the first opening shot, music/ambience muted, sfx at half level
    if ep == "ep01":
        t_o = next(o["t0"] for o in lay if o["id"] == "C21")
        w, sr0 = sf.read(STING, dtype="float32", always_2d=True)
        w = w.mean(axis=1)[: int(7.5 * sr0)]
        w = signal.resample_poly(w, SR, sr0).astype(np.float32)
        w *= np.minimum(1, np.linspace(0, 1, len(w))[::-1] * 7.5 / 0.25)
        a0, b0 = int(t_o * SR), int((t_o + 7.5) * SR)
        mus[a0:b0] = 0; amb[a0:b0] = 0; sfx[a0:b0] *= 0.5
        put(sfx, w, t_o, 0.0)
        song = np.zeros(n, np.float32); put(song, w, t_o, 1.0)
    else:
        song = np.zeros(n, np.float32)
    # silences (true silence for music + sfx + ambience; voice stays)
    for a, b in silences:
        i, j = int(a * SR), int(b * SR)
        for buf in (mus, sfx, amb):
            buf[i:j] *= 0.0
    # duck music and ambience under voice: -13 dB, attack 80 ms, release 250 ms
    env = np.abs(voice)
    hop = SR // 100
    act = (np.add.reduceat(env, np.arange(0, len(env), hop)) / hop > 0.004).astype(np.float64)
    g = np.zeros_like(act); cur = 0.0
    for i, a in enumerate(act):
        cur += (a - cur) * (1 - np.exp(-0.01 / (0.08 if a > cur else 0.25)))
        g[i] = cur
    duck = 1.0 - (1 - 10 ** (-13 / 20)) * np.interp(np.arange(len(voice)) / hop, np.arange(len(g)), g)
    mix = voice * 1.0 + sfx * 0.5 + amb * 0.5 * duck + mus * 0.5 * duck + song * 0.9
    end = int(total * SR)
    mix = mix[:end]
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    sf.write(out_wav, mix.astype(np.float32), SR)


def loudnorm(inp, outp):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", inp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rindex("{"): r.stderr.rindex("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", inp, "-af", af, "-ar", "44100", outp], check=True)
    return j


# ---------------------------------------------------------------- captions + overlays
_cap = {}


def caption_img(words, active, W, H, land, top):
    key = (tuple(words), active, W, H, top)
    if key in _cap:
        return _cap[key]
    size = int(H * 0.074) if land else int(W * 0.088)
    fnt = font(FONT, size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    sp = tmp.textlength(" ", font=fnt)
    tw = sum(tmp.textlength(w, font=fnt) for w in words) + sp * (len(words) - 1)
    while tw > W * 0.9:
        size = int(size * 0.92); fnt = font(FONT, size)
        tw = sum(tmp.textlength(w, font=fnt) for w in words) + sp * (len(words) - 1)
    img = Image.new("RGBA", (W, int(size * 1.6)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = (W - tw) / 2
    for i, w in enumerate(words):
        d.text((x, size * 0.25), w, font=fnt, fill=(CAP_ACTIVE if i == active else CAP_FILL) + (255,), stroke_width=max(4, size // 9), stroke_fill=BROWN + (255,))
        x += tmp.textlength(w, font=fnt) + sp
    _cap[key] = img
    return img


def groups_of(words, t_off):
    gs, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or re.search(r"[.?!,:;]$|\.\.\.$", w["w"]) or sum(len(x["w"]) for x in cur) > 20:
            gs.append(cur); cur = []
    if cur:
        gs.append(cur)
    return [dict(words=[re.sub(r"[,;:]$", "", x["w"]) for x in g], ts=[t_off + x["s"] for x in g], te=[t_off + x["e"] for x in g]) for g in gs]


def render(ep, land=False, preview=False):
    sh = S.parse_script(S.SCRIPTS[ep])
    lay, total = S.layout(ep, sh)
    # silences
    sil = []
    for i, o in enumerate(lay):
        v = o["voicej"]
        if ep == "ep01" and o["id"] == "C11":
            e = o["t0"] + o["line_at"] + v["dur"]; sil.append((e + 0.02, e + 0.38))
        if ep == "ep02" and o["id"] == "C11":
            e = o["t0"] + o["line_at"] + v["dur"]; sil.append((e + 0.1, lay[i + 1]["t0"] + 0.3))
    os.makedirs(OUT, exist_ok=True)
    name = f"animatic-{ep.replace('ep', 'ep')}-v5"
    wav = os.path.join(OUT, f"{ep}.mix.wav"); wav14 = os.path.join(OUT, f"{ep}.mix14.wav")
    if not os.path.exists(wav14) or os.environ.get("REMIX"):
        audio(ep, lay, total, wav, sil)
        info = loudnorm(wav, wav14)
        json.dump(info, open(os.path.join(OUT, f"{ep}.loudness.json"), "w"))
    W, H = (1280, 720) if land else (720, 1280)
    if preview:
        W, H = (W // 2, H // 2)
    K = 1.25
    LW, LH = (1280, 720) if land else (720, 1280)
    kk = K * W / LW
    # pre-render cards
    cards = {}
    for o in lay:
        base, meta = art.base_card(o, LW, LH, kk, land)
        segimgs = []
        parts = None
        if o["id"] == "K04":
            a = re.sub(r"^Stepped paper-cut animation:\s*", "", o["action"])
            parts = [x.strip() for x in a.split(";")]
        for idx, (a, b, typ, ct) in enumerate(o["segs"]):
            if typ in ("A", "punch", "rx") and o["method"] != "CODE":
                segimgs.append(base)
            elif typ == "ins" and o["method"] != "CODE":
                segimgs.append(art.ins_card(o, o["cutnotes"].get(ct, ""), LW, LH, kk, land)[0])
            else:   # code cards
                if ep == "ep01" and o["id"] == "K01":
                    segimgs.append([art.code_card("IMPACT FRAME", "2-frame cream impact: the giant's open mouth", LW, LH, kk, land, CREAM, ORANGE)[0],
                                    art.code_card("INSERT", "close-up of the chomp", LW, LH, kk, land, PEACH, ORANGE)[0], art.title_card(LW, LH, kk, land)[0]][min(idx, 2)])
                elif o["id"] == "K01":
                    segimgs.append(art.title_card(LW, LH, kk, land, "#2" if idx else None)[0])
                elif o["id"] == "K02":
                    segimgs.append(art.code_card("IMPACT", o["action"][:150], LW, LH, kk, land, CREAM if idx == 0 else PEACH, ORANGE)[0])
                elif o["id"] == "K03":
                    segimgs.append(art.code_card("LEGEND SCROLL", "scroll bursts open and wipes into the paper-cut world", LW, LH, kk, land, (222, 190, 130), BROWN)[0])
                elif o["id"] == "K04":
                    segimgs.append(art.code_card(f"PAPER-CUT {idx + 1}/{len(o['segs'])}", (parts[idx] if idx < len(parts) else parts[-1]), LW, LH, kk, land, (240, 222, 178), BROWN)[0])
                else:
                    segimgs.append(art.code_card(o["id"], o["action"][:150], LW, LH, kk, land)[0])
        cards[o["id"]] = (segimgs, meta)
    # caption groups per shot
    capg = {}
    for o in lay:
        v = o["voicej"]
        if v and o["line_at"] is not None:
            capg[o["id"]] = groups_of(v["words"], o["t0"] + o["line_at"])
    N = int(round(total * FPS))
    out = os.path.join(EM, "out", f"animatic-{ep}-v5{'-land' if land else ''}{'-preview' if preview else ''}.mp4")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav14, "-c:v", "libx264", "-preset", "medium", "-crf", "27", "-maxrate", "1400k", "-bufsize", "2800k", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-t", f"{N / FPS:.4f}", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    fnt_t = font(FONT, int(H * 0.022) + 4)
    starts = [o["t0"] for o in lay]
    flashes = []
    for o in lay:
        for ft in o["flash"]:
            flashes.append(o["t0"] + ft)
    pad = 0.0
    cy_cap = (0.19 if True else 0)
    for fi in range(N):
        t = fi / FPS
        si = max(i for i, s0 in enumerate(starts) if s0 <= t + 1e-9)
        o = lay[si]
        lt = t - o["t0"]
        sgi = max(i for i, sg in enumerate(o["segs"]) if sg[0] <= lt + 1e-9)
        a, b, typ, ct = o["segs"][sgi]
        sl = max(0.0, lt - a)
        segimgs, meta = cards[o["id"]]
        big = segimgs[sgi]
        pace = o["pace"]
        push = {"fast": 0.08, "medium": 0.05, "calm": 0.05}[pace]
        z0 = {"A": 1.0, "punch": 1.15, "rx": 1.30, "ins": 1.0, "card": 1.0}[typ]
        z = z0 + (push if typ in ("A", "punch", "rx") else 0.03) * min(1.0, sl / max(0.5, b - a))
        if typ != "A" and sl < 4 / FPS and (typ in ("punch", "rx") or sgi > 0):
            z *= 1 + 0.05 * (1 - sl / (4 / FPS))
        fx, fy = 0.5, (0.34 if not land else 0.36)
        bw, bh = big.size
        z = max(1.0, z)
        cw, ch = bw / z, bh / z
        x0 = min(max(fx * bw - cw / 2, 0), bw - cw); y0 = min(max(fy * bh - ch / 2, 0), bh - ch)
        if x0 < 0 or y0 < 0:
            raise SystemExit(f'bad box {o["id"]} fi={fi} z={z} sgi={sgi} big={big.size} typ={typ} sl={sl}')
        fr = big.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        if meta.get('strip') is not None:
            st_ = meta['strip']; sh_ = int(round((LH - 960) * W / LW)); fr.paste(st_.resize((W, sh_), Image.BILINEAR), (0, H - sh_))
        # impact / flash frames: 2 frames of flat cream
        if any(0 <= t - ft < 2 / FPS - 1e-6 for ft in flashes):
            fr = Image.new("RGB", (W, H), CREAM)
        d = ImageDraw.Draw(fr, "RGBA")
        sc = W / LW
        # overlays (cards / badges)
        for (kind, txt, ta, tb) in o["overlays"]:
            sa, sb = ta * (o["dur"] / max(o["plan_dur"], 0.5)) if o["id"] not in S.OPEN else ta, tb * (o["dur"] / max(o["plan_dur"], 0.5))
            sb = min(sb, o["dur"])
            if sa <= lt < sb:
                grow = min(1.0, (lt - sa) / 0.2)
                f2 = font(FONT, int(26 * sc * (0.85 + 0.15 * grow)))
                tw = d.textlength(txt, font=f2)
                if kind == "badge":
                    x1, y1 = W - 14 * sc, (150 if not land else 84) * sc
                    d.rounded_rectangle((x1 - tw - 28 * sc, y1, x1, y1 + 46 * sc), radius=12 * sc, fill=ORANGE + (255,), outline=BROWN, width=2)
                    d.text((x1 - tw / 2 - 14 * sc, y1 + 23 * sc), txt, font=f2, fill=CREAM, anchor="mm")
                else:
                    cy_ = (178 if not land else 100) * sc
                    d.rounded_rectangle((W / 2 - tw / 2 - 24 * sc, cy_ - 30 * sc, W / 2 + tw / 2 + 24 * sc, cy_ + 30 * sc), radius=16 * sc, fill=LEAF + (int(255 * grow),), outline=BROWN, width=3)
                    d.text((W / 2, cy_), txt, font=f2, fill=BROWN + (int(255 * grow),), anchor="mm")
        # camel easter egg in K04
        if ep == "ep01" and o["id"] == "K04":
            ca, cb = 4.6 * o["dur"] / 6.5, 5.4 * o["dur"] / 6.5
            if ca <= lt < cb:
                p_ = (lt - ca) / (cb - ca)
                cp = art.Pen(fr, 1.0); art.icon(cp, "Camel", W * (0.1 + 0.8 * p_), H * 0.62, 90 * sc)
        # captions
        if o["id"] in capg:
            for g in capg[o["id"]]:
                nxt = g["te"][-1] + 0.22
                if g["ts"][0] - 0.02 <= t < nxt:
                    act = max([i for i, ts in enumerate(g["ts"]) if ts <= t] or [0])
                    top = o["caption"].upper().startswith("TOP")
                    ci = caption_img(g["words"], act, W, H, land, top)
                    cyc = (0.19 if top else (0.80 if land else 0.64)) * H
                    if not land and not top:
                        assert cyc + ci.height / 2 <= 0.75 * H + 1, "caption bottom edge above 1440/1920 of the frame"
                    fr.paste(ci, (0, int(cyc - ci.height / 2)), ci)
                    break
        # timer + shot id (animatic only) and pace badge
        d = ImageDraw.Draw(fr, "RGBA")
        m, s_ = divmod(t, 60)
        lab = f"{int(m)}:{s_:04.1f}  {ep[2:].lstrip('0') and 'EP' + ep[2:].lstrip('0')}  {o['id']}"
        d.rounded_rectangle((8, 8, 8 + d.textlength(lab, font=fnt_t) + 16, 8 + fnt_t.size + 10), radius=8, fill=BROWN + (215,))
        d.text((16, 13), lab, font=fnt_t, fill=CREAM)
        pl = pace.upper() + ("  " + typ if typ != "A" else "")
        pw = d.textlength(pl, font=fnt_t)
        d.rounded_rectangle((W - pw - 24, 8, W - 8, 8 + fnt_t.size + 10), radius=8, fill=art.PACEC[pace] + (235,))
        d.text((W - pw - 16, 13), pl, font=fnt_t, fill=BROWN if pace != "fast" else CREAM)
        v = o["voicej"]
        if v and o["line_at"] is not None and o["t0"] + o["line_at"] <= t < o["t0"] + o["line_at"] + v["dur"]:
            tag = f"{v['who'].upper()} ({v['kind']})"
            tw = d.textlength(tag, font=fnt_t)
            ph = int(t * 24) % 4
            y_ = 8 + (fnt_t.size + 10) * 1.3
            d.rounded_rectangle((W - tw - 60, y_, W - 8, y_ + fnt_t.size + 10), radius=8, fill=CREAM + (225,), outline=ORANGE, width=2)
            for q in range(3):
                hh = (6, 14, 9, 16)[(ph + q) % 4] * (H / 1280 + 0.4)
                d.rectangle((W - tw - 52 + q * 7, y_ + 8 + (14 - hh) / 2 + 4, W - tw - 47 + q * 7, y_ + 8 + (14 + hh) / 2 + 4), fill=ORANGE)
            d.text((W - 16 - tw + 4, y_ + 5), tag, font=fnt_t, fill=BROWN)
        # ends: hard cut to black on the last frames (Episode 2 camel, Episode 1 smash to black)
        if fi >= N - 2:
            fr = Image.new("RGB", (W, H), (0, 0, 0))
        pr.stdin.write(fr.tobytes())
    pr.stdin.close(); pr.wait()
    json.dump([{k: v for k, v in o.items() if k in ("id", "t0", "dur", "plan_dur", "pace", "line_at", "segs")} for o in lay], open(os.path.join(OUT, f"{ep}.timeline.json"), "w"), indent=1, default=float)
    return out, total


if __name__ == "__main__":
    ep = sys.argv[1]
    t0 = time.time()
    o, tot = render(ep, "--land" in sys.argv, "--preview" in sys.argv)
    print(o, round(tot, 2), "s", round(time.time() - t0), "s render")
