#!/usr/bin/env python3
"""Build a ~2 minute vertical episode video from a JSON spec.

    python3 make_episode.py specs/episode-01.json out.mp4 [--preview]

Pipeline: neural TTS (Kokoro) -> timeline -> audio mix (voices, sfx, ambience,
ducked music) -> frame renderer (Ken Burns, captions, cards, fx) -> ffmpeg.
Nothing here needs a paid video service.
"""
import argparse, hashlib, json, math, os, subprocess, sys, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import signal
import soundfile as sf

sys.path.insert(0, os.path.dirname(__file__))
import synth
from synth import SR

FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
TTS_DIR = os.environ.get("TTS_DIR", os.path.join(os.path.dirname(__file__), "tts"))
CACHE = os.environ.get("TTS_CACHE", "/tmp/dumpling_tts_cache")

# Voice casting: (kokoro voice, speed, pitch ratio via resample trick)
VOICES = {
    "boy":     ("am_puck",    1.00, 1.08),   # older, less chipmunk (v1 used 1.22: spec "voice_pitch": {"boy": 1.22})
    "uncle":   ("am_michael", 0.92, 0.90),
    "grandma": ("af_sarah",   0.92, 0.93),
    "dad":     ("bm_daniel",  0.88, 1.00),
    "narrator": ("bm_george", 0.90, 0.96),   # calm, slightly deeper
}
PITCH_OVERRIDE = {}
FILL = {"boy": (255, 255, 255), "uncle": (255, 226, 140), "grandma": (255, 214, 224), "dad": (255, 236, 196), "narrator": (232, 240, 255)}


# ------------------------------------------------------------------ TTS
_kokoro = None


def tts(who, text):
    global _kokoro
    voice, speed, pitch = VOICES[who]
    pitch = PITCH_OVERRIDE.get(who, pitch)
    key = hashlib.md5(f"{voice}|{speed}|{pitch}|{text}".encode()).hexdigest()
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, key + ".npy")
    if os.path.exists(path):
        return np.load(path)
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(os.path.join(TTS_DIR, "kokoro-v1.0.onnx"), os.path.join(TTS_DIR, "voices-v1.0.bin"))
    wav, sr = _kokoro.create(text, voice=voice, speed=speed, lang="en-us")
    wav = np.asarray(wav, dtype=np.float64)
    if pitch != 1.0:   # pitch shift, then restore duration with time-stretch via ffmpeg atempo
        tmp_in, tmp_out = path + ".in.wav", path + ".out.wav"
        sf.write(tmp_in, wav, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp_in, "-af",
                        f"asetrate={int(sr*pitch)},aresample={sr},atempo={1/pitch:.5f}", tmp_out], check=True)
        wav, sr = sf.read(tmp_out)
        os.remove(tmp_in); os.remove(tmp_out)
    wav = signal.resample_poly(wav, SR, sr)
    # trim leading/trailing silence
    a = np.abs(wav)
    idx = np.where(a > 0.01 * a.max())[0]
    wav = wav[max(0, idx[0] - int(0.03 * SR)): idx[-1] + int(0.08 * SR)]
    wav = (wav / (np.abs(wav).max() or 1) * 0.9).astype(np.float32)
    np.save(path, wav)
    return wav


# ------------------------------------------------------------------ timeline
def build_timeline(spec):
    shots, t = [], 0.0
    snap = spec.get("snap_to_beat", False)
    mood, origin = "cozy", 0.0
    for sh in spec["shots"]:
        s = dict(sh)
        if s.get("mood") and s["mood"] != mood:
            if s["mood"] in synth.NEW_MOODS or mood in synth.NEW_MOODS:
                origin = t           # music bar grid restarts at a tempo change
            mood = s["mood"]
        s["start"] = t
        lines, cur = [], t + s.get("lead", 0.3)
        for ln in s.get("lines", []):
            a = tts(ln["who"], ln["text"])
            at = t + ln["at"] if "at" in ln else cur
            dur = len(a) / SR
            lines.append(dict(ln, start=at, dur=dur, audio=a))
            cur = at + dur + ln.get("gap", 0.18)
        s["lines"] = lines
        end_voice = (lines[-1]["start"] + lines[-1]["dur"] + s.get("tail", 0.35)) if lines else t
        s["dur"] = max(s["dur"], end_voice - t)
        if snap and mood != "off":   # round the cut to the nearest half-beat of the mood's tempo
            half = 30.0 / synth.mood_bpm(mood)
            need = s["dur"]
            k = round((t + need - origin) / half)
            end = origin + k * half
            if end - t < need - 1e-6:
                end += half
            s["dur"] = max(end - t, half)
        s["end"] = t + s["dur"]
        shots.append(s)
        t = s["end"]
    return shots, t


# ------------------------------------------------------------------ audio
def render_audio(spec, shots, total, out_wav):
    n = int(total * SR) + SR
    voice, sfx, amb = (np.zeros(n, np.float32) for _ in range(3))

    def put(buf, sig, at, gain=1.0):
        i = int(at * SR)
        if i < 0 or i >= n:
            return
        j = min(n, i + len(sig))
        buf[i:j] += sig[: j - i] * gain

    for sh in shots:
        for ln in sh["lines"]:
            put(voice, ln["audio"], ln["start"], 1.0)
        for ev in sh.get("sfx", []):
            put(sfx, synth.SFX[ev["name"]](*([ev["d"]] if "d" in ev else [])), sh["start"] + ev["t"], ev.get("gain", 1.0))
        if sh.get("whip") and sh["start"] > 0:
            put(sfx, synth.swoosh_big(0.5), sh["start"] - 0.08, 0.7)
        for im in ([sh["impact"]] if isinstance(sh.get("impact"), dict) else []):
            put(sfx, synth.impact(), sh["start"] + im["t"], im.get("gain", 0.9))
        if sh.get("ambience"):
            a = synth.ambience(sh["ambience"], sh["dur"] + 0.6)
            put(amb, a, sh["start"] - 0.3, 1.0)
    # music with mood automation
    moods = [(s["start"], s.get("mood")) for s in shots if s.get("mood")]

    def mood_at(t):
        m = "cozy"
        for st, md in moods:
            if t + 1e-6 >= st:
                m = md
        return m
    mus = np.zeros(n, np.float32)
    mm = synth.music(total, mood_at, change_times=[st for st, _ in moods])
    mus[: len(mm)] = mm
    # duck music under voice
    mask = (np.abs(voice) > 0.02).astype(np.float32)
    k = int(0.18 * SR)
    smooth = np.convolve(mask, np.ones(k) / k, mode="same")
    duck = 1.0 - 0.62 * np.clip(smooth * 3.0, 0, 1)
    mix = voice * 1.0 + sfx * 0.55 + amb * 0.5 + mus * 0.55 * duck
    # gentle fade-out
    f = int(1.2 * SR)
    end = int(total * SR)
    mix[end - f:end] *= np.linspace(1, 0, f)
    mix = mix[:end]
    mix = np.tanh(mix * 1.15) / np.tanh(1.15)
    sf.write(out_wav, mix, SR)


# ------------------------------------------------------------------ rendering helpers
_font_cache = {}


def font(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size)
    return _font_cache[k]


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def wrap_text(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= maxw:
            cur = trial
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


_layer_cache = {}


def caption_layer(text, who, W):
    key = ("cap", text, who, W)
    if key in _layer_cache:
        return _layer_cache[key]
    size = int(W * 0.088)
    fnt = font(FONT, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    lines = wrap_text(dummy, text, fnt, W * 0.84)
    lh = int(size * 1.22)
    h = lh * len(lines) + 40
    img = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        w = d.textlength(ln, font=fnt)
        d.text(((W - w) / 2, 20 + i * lh), ln, font=fnt, fill=FILL.get(who, (255, 255, 255)) + (255,),
               stroke_width=max(5, size // 9), stroke_fill=(59, 42, 26, 255))
    _layer_cache[key] = img
    return img


def card_layer(card, W):
    key = ("card", json.dumps(card, sort_keys=True), W)
    if key in _layer_cache:
        return _layer_cache[key]
    pad = int(W * 0.05)
    cw = int(W * 0.84)
    label_f, text_f = font(FONT, int(W * 0.040)), font(FONT, int(W * 0.062))
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    body = wrap_text(dummy, card["text"], text_f, cw - 2 * pad)
    lh = int(W * 0.078)
    ch = pad * 2 + int(W * 0.06) + lh * len(body)
    img = Image.new("RGBA", (cw + 30, ch + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((12, 20, cw + 12, ch + 20), radius=44, fill=(59, 42, 26, 90))     # shadow
    d.rounded_rectangle((8, 8, cw + 8, ch + 8), radius=44, fill=(255, 248, 236, 245), outline=(217, 72, 15, 255), width=8)
    d.text((8 + pad, 8 + pad * 0.8), card.get("label", "FUN FACT"), font=label_f, fill=(217, 72, 15, 255))
    for i, ln in enumerate(body):
        d.text((8 + pad, 8 + pad * 0.8 + int(W * 0.07) + i * lh), ln, font=text_f, fill=(59, 42, 26, 255))
    _layer_cache[key] = img
    return img


def title_layer(card, W):
    key = ("title", json.dumps(card, sort_keys=True), W)
    if key in _layer_cache:
        return _layer_cache[key]
    f1, f2 = font(FONT, int(W * 0.105)), font(FONT_BOLD, int(W * 0.058))
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    l1 = wrap_text(dummy, card["text"], f1, W * 0.86)
    h = len(l1) * int(W * 0.125) + int(W * 0.12)
    img = Image.new("RGBA", (W, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(l1):
        w = d.textlength(ln, font=f1)
        d.text(((W - w) / 2, 10 + i * int(W * 0.125)), ln, font=f1, fill=(255, 255, 255, 255), stroke_width=10, stroke_fill=(217, 72, 15, 255))
    sub = card.get("sub", "")
    if sub:
        w = d.textlength(sub, font=f2)
        d.text(((W - w) / 2, 10 + len(l1) * int(W * 0.125) + 6), sub, font=f2, fill=(255, 245, 230, 255), stroke_width=6, stroke_fill=(59, 42, 26, 255))
    _layer_cache[key] = img
    return img


def soft_sprite(r, alpha=0.5, color=(255, 255, 255)):
    key = ("spr", r, alpha, color)
    if key in _layer_cache:
        return _layer_cache[key]
    s = Image.new("L", (r * 2, r * 2), 0)
    ImageDraw.Draw(s).ellipse((r * 0.55, r * 0.55, r * 1.45, r * 1.45), fill=int(255 * alpha))
    s = s.filter(ImageFilter.GaussianBlur(r * 0.17))
    _layer_cache[key] = s
    return s


def heart_sprite(sz):
    key = ("heart", sz)
    if key in _layer_cache:
        return _layer_cache[key]
    m = Image.new("L", (sz * 2, sz * 2), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((sz * 0.2, sz * 0.3, sz * 1.0, sz * 1.1), fill=255)
    d.ellipse((sz * 1.0, sz * 0.3, sz * 1.8, sz * 1.1), fill=255)
    d.polygon([(sz * 0.25, sz * 0.85), (sz * 1.75, sz * 0.85), (sz, sz * 1.8)], fill=255)
    _layer_cache[key] = m
    return m


def load_cover(path, W, H):
    img = Image.open(path).convert("RGB")
    sw, sh = img.size
    # scale so that image covers W x H with generous margin for camera moves
    return img


def camera_box(img_size, W, H, shot, p):
    sw, sh = img_size
    base = max(W / sw, H / sh)           # scale to cover
    zoom0, zoom1 = shot.get("zoom0", 1.0), shot.get("zoom", 1.12)
    motion = shot.get("motion", "zoom_in")
    fx, fy = shot.get("focus", [0.5, 0.5])
    amt = shot.get("pan", 0.06)
    e = ease(p)
    if motion == "zoom_out":
        z = zoom1 + (zoom0 - zoom1) * e
    elif motion in ("static",):
        z = zoom0
    else:
        z = zoom0 + (zoom1 - zoom0) * e
    vw, vh = W / (base * z), H / (base * z)        # visible window in source px
    cx, cy = fx * sw, fy * sh
    if motion == "pan_left":
        cx += (0.5 - e) * amt * sw
    elif motion == "pan_right":
        cx += (e - 0.5) * amt * sw
    elif motion == "pan_up":
        cy += (0.5 - e) * amt * sh
    elif motion == "pan_down":
        cy += (e - 0.5) * amt * sh
    x0 = min(max(cx - vw / 2, 0), sw - vw)
    y0 = min(max(cy - vh / 2, 0), sh - vh)
    return (x0, y0, x0 + vw, y0 + vh)


class Renderer:
    def __init__(self, spec, shots, W, H, fps, frames_dir):
        self.spec, self.shots, self.W, self.H, self.fps = spec, shots, W, H, fps
        self.frames_dir = frames_dir
        self.imgs = {}
        for s in shots:
            p = os.path.join(frames_dir, s["img"])
            if p not in self.imgs:
                self.imgs[p] = Image.open(p).convert("RGB")
        self.rng = np.random.default_rng(3)

    def base_frame(self, s, t_local):
        W, H = self.W, self.H
        img = self.imgs[os.path.join(self.frames_dir, s["img"])]
        p = t_local / max(s["dur"], 0.01)
        box = camera_box(img.size, W, H, s, p)
        # shake windows
        for sh in s.get("shake", []):
            if sh["t"] <= t_local <= sh["t"] + sh["d"]:
                k = (1 - (t_local - sh["t"]) / sh["d"]) * sh.get("amp", 14)
                dx, dy = self.rng.uniform(-k, k, 2)
                sc = (box[2] - box[0]) / W
                bw, bh = box[2] - box[0], box[3] - box[1]
                nx = min(max(box[0] + dx * sc, 0), img.size[0] - bw)
                ny = min(max(box[1] + dy * sc, 0), img.size[1] - bh)
                box = (nx, ny, nx + bw, ny + bh)
        return img.resize((W, H), Image.BICUBIC, box=box)

    def overlays(self, frame, s, t_local):
        W, H = self.W, self.H
        # fx: steam / hearts / flash
        for fx in s.get("fx", []):
            kind = fx["type"]
            if kind == "steam":
                x0, x1 = fx.get("x", [0.3, 0.7])
                ybase = fx.get("y", 0.62)
                n = fx.get("n", 7)
                for i in range(n):
                    life = 2.6
                    ph = (t_local / life + i / n) % 1.0
                    seed = (i * 7919) % 100 / 100
                    x = (x0 + (x1 - x0) * seed) * W + math.sin(ph * 5 + i) * W * 0.03
                    y = (ybase - ph * fx.get("rise", 0.35)) * H
                    r = int(W * (0.10 + 0.10 * ph + 0.04 * seed))
                    a = math.sin(ph * math.pi) * fx.get("alpha", 0.55)
                    spr = soft_sprite(r, 1.0)
                    spr = spr.point(lambda v: int(v * a))
                    frame.paste((255, 255, 255), (int(x - r), int(y - r)), spr)
            elif kind == "hearts" and t_local >= fx.get("t", 0):
                lt = t_local - fx.get("t", 0)
                for i in range(fx.get("n", 5)):
                    ph = (lt * 0.5 + i * 0.19) % 1.0
                    x = (fx.get("x", 0.5) + math.sin(i * 2.3 + ph * 4) * 0.14) * W
                    y = (fx.get("y", 0.5) - ph * 0.28) * H
                    sz = int(W * (0.045 + 0.02 * ((i * 37) % 5) / 5))
                    spr = heart_sprite(sz).point(lambda v: int(v * math.sin(ph * math.pi)))
                    frame.paste((255, 130, 160), (int(x - sz), int(y - sz)), spr)
            elif kind == "flash":
                dt = t_local - fx["t"]
                if 0 <= dt <= fx.get("d", 0.12):
                    a = 1 - dt / fx.get("d", 0.12)
                    frame.paste(Image.blend(frame, Image.new("RGB", frame.size, (255, 255, 255)), 0.75 * a))
            elif kind == "vignette_warm":
                pass
        # cards
        for c in s.get("cards", []):
            dt = t_local - c["t"]
            if 0 <= dt <= c["d"]:
                lay = title_layer(c, W) if c["type"] == "title" else card_layer(c, W)
                pop = ease(dt / 0.22)
                out = ease((c["d"] - dt) / 0.2)
                a = min(pop, out)
                sc = 0.88 + 0.12 * pop
                lw, lh = int(lay.width * sc), int(lay.height * sc)
                l2 = lay.resize((lw, lh), Image.BILINEAR)
                if a < 1:
                    l2.putalpha(l2.getchannel("A").point(lambda v: int(v * a)))
                pos_y = int(c.get("y", 0.62) * H) - lh // 2
                frame.paste(l2, ((W - lw) // 2, pos_y), l2)
        # captions (burned in, safe zone above the Shorts UI)
        for ln in s["lines"]:
            if ln.get("caption") is False:
                continue
            dt = t_local - (ln["start"] - s["start"])
            if -0.02 <= dt <= ln["dur"] + 0.12:
                lay = caption_layer(ln.get("caption", ln["text"]), ln["who"], W)
                pop = ease(max(dt, 0) / 0.12)
                sc = 0.9 + 0.1 * pop
                lw, lh = int(lay.width * sc), int(lay.height * sc)
                l2 = lay.resize((lw, lh), Image.BILINEAR) if sc != 1 else lay
                frame.paste(l2, ((W - lw) // 2, int(self.H * 0.67) - lh // 2), l2)
        return frame

    def frame_at(self, gt):
        s = None
        for i, sh in enumerate(self.shots):
            if gt < sh["end"] or i == len(self.shots) - 1:
                s, idx = sh, i
                break
        t_local = gt - s["start"]
        fr = self.base_frame(s, t_local)
        tf = s.get("fade", 0.18)
        if idx > 0 and s.get("transition", "fade") == "fade" and t_local < tf:
            prev = self.shots[idx - 1]
            pf = self.base_frame(prev, prev["dur"] + t_local)
            fr = Image.blend(pf, fr, ease(t_local / tf))
        return self.overlays(fr, s, t_local)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("out")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--audio-only", action="store_true")
    ap.add_argument("--frames-dir", default=None)
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    W, H = spec.get("size", [1080, 1920])
    fps = spec.get("fps", 30)
    if a.preview:
        W, H, fps = 540, 960, 15
    fdir = a.frames_dir or os.path.join(os.path.dirname(os.path.abspath(a.spec)), spec.get("frames_dir", "frames"))
    shots, total = build_timeline(spec)
    print(f"timeline: {len(shots)} shots, {total:.1f}s", flush=True)
    wav = a.out + ".audio.wav"
    render_audio(spec, shots, total, wav)
    print("audio done", flush=True)
    if a.audio_only:
        return
    r = Renderer(spec, shots, W, H, fps, fdir)
    nframes = int(total * fps)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", a.out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(nframes):
        p.stdin.write(r.frame_at(i / fps).tobytes())
        if i % (fps * 10) == 0:
            print(f"  frame {i}/{nframes}", flush=True)
    p.stdin.close(); p.wait()
    print("done", a.out)


if __name__ == "__main__":
    main()
