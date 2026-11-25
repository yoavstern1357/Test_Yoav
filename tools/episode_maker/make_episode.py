#!/usr/bin/env python3
"""Build a ~2 minute episode video from a JSON spec, vertical 9:16 (1080x1920, Shorts) and/or horizontal 16:9 (1920x1080).

    python3 make_episode.py specs/episode-01.json out.mp4 [--preview]            # portrait (default, as before)
    python3 make_episode.py specs/episode-01.json out.mp4 --landscape            # 1920x1080
    python3 make_episode.py specs/episode-01.json out.mp4 --both [--mobile]      # out.mp4 (9:16) + out-land.mp4 (16:9), audio mixed once

Pipeline: neural TTS (Kokoro by default; optional engines in tts_engines.py, see voice_casts.json) -> timeline -> audio mix (voices, sfx, ambience,
ducked music) -> frame renderer (Ken Burns, captions, cards, fx) -> ffmpeg.
Nothing here needs a paid video service.
"""
import argparse, hashlib, json, math, os, subprocess, sys, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from scipy import signal
import soundfile as sf

sys.path.insert(0, os.path.dirname(__file__))
import synth
import sfx_extra  # noqa: F401  (adds more sound effects to synth.SFX)
import sfx_extra2  # noqa: F401  (intro + v4.3 effects)
from synth import SR

FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
TTS_DIR = os.environ.get("TTS_DIR", os.path.join(os.path.dirname(__file__), "tts"))
CACHE = os.environ.get("TTS_CACHE", "/tmp/dumpling_tts_cache")

# ------------------------------------------------------------------ orientations (portrait 9:16 / landscape 16:9)
LAND_SUFFIX = "_land"
_WARNED = set()


def warn_once(msg):
    if msg not in _WARNED:
        _WARNED.add(msg)
        print("WARNING:", msg, flush=True)


def land_name(name):
    """'C01.png' -> 'C01_land.png' (the naming convention for the horizontal version of a still or clip)."""
    stem, ext = os.path.splitext(name)
    return stem + LAND_SUFFIX + ext


def asset_candidates(val, orient):
    """Names to try for a still/clip in an orientation, best first: [(name, exact)]. `val` is a file name ("C01.png": portrait,
    with "C01_land.png" as its horizontal twin) or {"portrait": name, "landscape": name}. exact=False means the other orientation's
    file is used and gets a center-cover crop."""
    other = "landscape" if orient == "portrait" else "portrait"
    if isinstance(val, dict):
        c = [(val[orient], True)] if val.get(orient) else []
        if val.get(other):
            c.append((val[other], False))
        return c
    if orient == "portrait":
        return [(val, True)]
    return [(land_name(val), True), (val, False)]


def orient_apply(shot, orient):
    """Landscape: every shot key "X_land" overrides "X" (e.g. focus_land, zoom_land, caption_y_land, cards_land, puppets_land)."""
    if orient != "landscape":
        return shot
    s = dict(shot)
    if "caption_y_land" not in s:
        s.pop("caption_y", None)             # caption_y is a portrait height; landscape uses spec caption_y_land (default 0.84)
    for k in list(s):
        if k.endswith(LAND_SUFFIX) and len(k) > len(LAND_SUFFIX):
            s[k[:-len(LAND_SUFFIX)]] = s[k]
    return s


def video_size(spec, orient, preview=False):
    """(W, H) for an orientation. spec "size" is the portrait size [1080, 1920]; "size_landscape" overrides the 16:9 size."""
    if preview:
        return (540, 960) if orient == "portrait" else (960, 540)
    lo, hi = sorted(int(v) for v in spec.get("size", [1080, 1920]))
    if orient == "portrait":
        return lo, hi
    sl = spec.get("size_landscape")
    return tuple(int(v) for v in sl) if sl else (int(round(lo * 16 / 9)), lo)

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


def _load_casts():
    """Optional per-character engine config (backwards compatible: with no config every voice is Kokoro as before).
    Presets live in voice_casts.json; pick one with spec "voice_engine" or env VOICE_ENGINE, then override single
    characters with spec "voice_cast": {"uncle": {"engine": "supertonic", "sid": 8}}."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_casts.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


CAST = {}          # who -> {"engine": "kokoro" | "supertonic" | "pocket" | "prerendered", ...}; empty = Kokoro VOICES above


def set_cast(spec):
    CAST.clear()
    name = spec.get("voice_engine") or os.environ.get("VOICE_ENGINE")
    if name and name != "kokoro":
        presets = _load_casts()
        if name not in presets:
            raise SystemExit(f"voice_engine {name!r} not found in voice_casts.json (have: {sorted(presets)})")
        CAST.update({k: dict(v) for k, v in presets[name].items() if not k.startswith("_")})
    for who, c in spec.get("voice_cast", {}).items():
        CAST[who] = dict(c)


def _stretch(wav, sr, factor):
    """Pitch-preserving speed change (ffmpeg atempo) for engines without a native speed control."""
    tmp_in, tmp_out = f"/tmp/dumpling_st_{os.getpid()}.in.wav", f"/tmp/dumpling_st_{os.getpid()}.out.wav"
    sf.write(tmp_in, wav, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp_in, "-af", f"atempo={factor:.5f}", tmp_out], check=True)
    out, sr2 = sf.read(tmp_out)
    os.remove(tmp_in); os.remove(tmp_out)
    return out, sr2


def _finish(wav, sr, pitch):
    """Shared tail of every engine: optional pitch shift (duration kept), resample to SR, trim silence, normalize."""
    wav = np.asarray(wav, dtype=np.float64)
    if pitch != 1.0:   # pitch shift, then restore duration with time-stretch via ffmpeg atempo
        tmp_in, tmp_out = f"/tmp/dumpling_ps_{os.getpid()}.in.wav", f"/tmp/dumpling_ps_{os.getpid()}.out.wav"
        sf.write(tmp_in, wav, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp_in, "-af",
                        f"asetrate={int(sr*pitch)},aresample={sr},atempo={1/pitch:.5f}", tmp_out], check=True)
        wav, sr = sf.read(tmp_out)
        os.remove(tmp_in); os.remove(tmp_out)
    wav = signal.resample_poly(wav, SR, sr)
    a = np.abs(wav)       # trim leading/trailing silence
    idx = np.where(a > 0.01 * a.max())[0]
    wav = wav[max(0, idx[0] - int(0.03 * SR)): idx[-1] + int(0.08 * SR)]
    return (wav / (np.abs(wav).max() or 1) * 0.9).astype(np.float32)


def tts(who, text, speed_mult=None, pitch_override=None):
    """Voice line. With a "prerendered" (GPU) cast a missing WAV falls back to Kokoro with a warning (spec has "voice_fallback": true by default)."""
    try:
        return _tts(who, text, speed_mult, pitch_override)
    except FileNotFoundError as ex:
        if CAST.get(who, {}).get("engine") != "prerendered" or not FALLBACK_KOKORO:
            raise
        warn_once(f"voice fallback to Kokoro for {who}: {text[:50]!r}")
        saved = CAST.pop(who)
        try:
            return _tts(who, text, speed_mult, pitch_override)
        finally:
            CAST[who] = saved


FALLBACK_KOKORO = True
VOICE_SPEED = {}          # spec "voice_speed": {"uncle": 1.2}: default speed multiplier per character (lines can still set their own "speed")
MAX_PAUSE = 0.40          # spec "max_pause": longer silences INSIDE a pre-rendered (GPU) line are shortened to this many seconds


def compress_pauses(wav, sr, max_pause=0.40, keep=0.30):
    """Shorten silences longer than max_pause inside a line to `keep` seconds (TTS models stretch "..." into long gaps)."""
    wav = np.asarray(wav, dtype=np.float32)
    win = max(1, int(0.01 * sr))
    env = np.sqrt(np.convolve(wav ** 2, np.ones(win) / win, mode="same"))
    quiet = env < 0.012 * (env.max() or 1.0)
    out, i, n = [], 0, len(wav)
    while i < n:
        j = i
        while j < n and quiet[j] == quiet[i]:
            j += 1
        seg = wav[i:j]
        if quiet[i] and 0 < i and j < n and (j - i) / sr > max_pause:
            k = int(keep * sr)
            f = int(0.03 * sr)
            seg = np.concatenate([seg[:k // 2], seg[-(k - k // 2):]]) if k > 2 * f else seg[:k]
        out.append(seg)
        i = j
    return np.concatenate(out) if out else wav


def _tts(who, text, speed_mult=None, pitch_override=None):
    global _kokoro
    cast = CAST.get(who)
    if speed_mult is None and who in VOICE_SPEED:
        speed_mult = VOICE_SPEED[who]
    engine = (cast or {}).get("engine", "kokoro")
    voice, speed, pitch = VOICES[who]
    if engine == "kokoro" and cast:      # per-character Kokoro override: {"engine": "kokoro", "voice": "am_adam", "speed": 0.95, "pitch": 0.9}
        voice, speed, pitch = cast.get("voice", voice), cast.get("speed", speed), cast.get("pitch", pitch)
    elif engine != "kokoro":
        pitch = cast.get("pitch", 1.0)
    pitch = PITCH_OVERRIDE.get(who, pitch)
    if pitch_override:
        pitch = float(pitch_override)
    if engine == "kokoro":
        if speed_mult:
            speed = speed * float(speed_mult)
        key = hashlib.md5(f"{voice}|{speed}|{pitch}|{text}".encode()).hexdigest()   # unchanged: old caches stay valid
    else:
        stamp = ""
        if engine == "prerendered":      # a re-picked take (new file) must not hit the cache of the old one
            import tts_engines as _te
            _p = os.path.join(os.path.expanduser(cast.get("dir", "tts/gpu")) if os.path.isabs(os.path.expanduser(cast.get("dir", "tts/gpu"))) else os.path.join(os.path.dirname(os.path.abspath(__file__)), cast.get("dir", "tts/gpu")), _te.line_key(who, text) + ".wav")
            stamp = f"{os.path.getmtime(_p):.0f}|{os.path.getsize(_p)}" if os.path.exists(_p) else "missing"
        key = hashlib.md5(f"{engine}|{json.dumps(cast, sort_keys=True)}|{speed_mult}|{MAX_PAUSE}|{pitch}|{who}|{text}|{stamp}".encode()).hexdigest()
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, key + ".npy")
    if os.path.exists(path):
        return np.load(path)
    if engine == "kokoro":
        if _kokoro is None:
            from kokoro_onnx import Kokoro
            _kokoro = Kokoro(os.path.join(TTS_DIR, "kokoro-v1.0.onnx"), os.path.join(TTS_DIR, "voices-v1.0.bin"))
        wav, sr = _kokoro.create(text, voice=voice, speed=speed, lang="en-us")
    else:
        import tts_engines
        if engine == "prerendered":
            wav, sr = tts_engines.prerendered(cast, who, text)
            wav = compress_pauses(wav, sr, MAX_PAUSE)
            if speed_mult and abs(float(speed_mult) - 1.0) > 0.01:
                wav, sr = _stretch(wav, sr, float(speed_mult))
        else:
            wav, sr = tts_engines.synth(cast, text, float(speed_mult or 1.0))
    wav = _finish(wav, sr, pitch)
    np.save(path, wav)
    return wav


# ------------------------------------------------------------------ AI clips (`clip` shots)
def echo_voice(a, delays=((0.13, 0.30), (0.27, 0.16), (0.43, 0.08))):
    """Solemn hall echo for the Scroll Narrator: a few soft, darker repeats after the dry voice."""
    n = len(a) + int(0.6 * SR)
    out = np.zeros(n, np.float32)
    out[: len(a)] += a
    lp = signal.lfilter(*signal.butter(1, 2200, btype="low", fs=SR), a).astype(np.float32)
    for d, g in delays:
        i = int(d * SR)
        out[i: i + len(a)] += lp * g
    return out / max(1.0, float(np.abs(out).max()) / 0.95)


def reversed_clip(path):
    """Return a reversed copy of a (short) clip, cached in /tmp."""
    os.makedirs("/tmp/dumpling_rev", exist_ok=True)
    out = os.path.join("/tmp/dumpling_rev", hashlib.md5(path.encode()).hexdigest() + f"-{int(os.path.getmtime(path))}.mp4")
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", "reverse", "-an", "-c:v", "libx264", "-crf", "14", out], check=True)
    return out


def find_clip(spec, spec_dir, name):
    """Resolve a clip path: absolute, or relative to spec "clips_dir" (default "clips"), the frames dir, or the spec folder."""
    if os.path.isabs(name) and os.path.exists(name):
        return name
    for base in (spec.get("clips_dir", "clips"), spec.get("frames_dir", "frames"), "."):
        p = os.path.join(spec_dir, base, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"clip not found: {name} (looked in clips_dir, frames_dir and next to the spec)")


def find_clips(spec, spec_dir, val):
    """Look a clip up for BOTH orientations: {"portrait": path | None, "landscape": path | None}, exact matches only
    ("C01.mp4" -> C01.mp4 / C01_land.mp4, or a {"portrait", "landscape"} dict)."""
    out = {}
    for orient in ("portrait", "landscape"):
        out[orient] = None
        for name, exact in asset_candidates(val, orient):
            if not exact:
                continue
            try:
                out[orient] = find_clip(spec, spec_dir, name)
                break
            except FileNotFoundError:
                pass
    return out


def probe_clip(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate,duration:format=duration",
                        "-of", "json", path], capture_output=True, text=True, check=True)
    j = json.loads(r.stdout)
    dur = float((j.get("streams") or [{}])[0].get("duration") or j["format"]["duration"])
    num, den = (j["streams"][0]["r_frame_rate"].split("/") + ["1"])[:2]
    return dur, float(num) / float(den or 1)


class ClipReader:
    """Streams the frames of one AI clip (trim, speed, loop, last-frame hold) as PIL images at render size and fps.
    Frames are requested in time order; asking for an earlier frame restarts the decoder."""

    def __init__(self, path, W, H, fps, trim, speed, loop, focus=(0.5, 0.5)):
        self.path, self.W, self.H, self.fps, self.loop = path, W, H, fps, bool(loop)
        self.focus = focus
        src_dur, _ = probe_clip(path)
        t0 = float(trim[0]) if trim else 0.0
        t1 = float(trim[1]) if trim and len(trim) > 1 and trim[1] is not None else src_dur
        self.t0, self.t1, self.speed = t0, max(t1, t0 + 0.05), float(speed or 1.0)
        self.n = max(1, int((self.t1 - self.t0) / self.speed * fps))
        self.proc, self.pos, self.last = None, 0, None
        self.fsize = W * H * 3

    def _start(self):
        self.close()
        vf = (f"setpts=PTS/{self.speed},fps={self.fps},scale={self.W}:{self.H}:force_original_aspect_ratio=increase:flags=lanczos,"
              f"crop={self.W}:{self.H}:(iw-ow)*{float(self.focus[0]):.4f}:(ih-oh)*{float(self.focus[1]):.4f}")
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{self.t0:.3f}", "-t", f"{self.t1 - self.t0:.3f}", "-i", self.path,
                                      "-vf", vf, "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.pos = 0

    def _next(self):
        buf = self.proc.stdout.read(self.fsize) if self.proc else b""
        if len(buf) < self.fsize:
            self.close(); return False
        self.last = Image.frombytes("RGB", (self.W, self.H), buf)
        self.pos += 1
        return True

    def frame(self, t):
        idx = int(max(t, 0) * self.fps)
        if self.loop:
            idx %= self.n
        idx = min(idx, self.n - 1)
        if self.proc is None and self.pos == 0 or idx < self.pos - 1:
            self._start()
        while self.pos <= idx and self.proc is not None:
            if not self._next():
                break
        return self.last.copy() if self.last is not None else Image.new("RGB", (self.W, self.H), (0, 0, 0))

    def close(self):
        if self.proc is not None:
            try:
                self.proc.stdout.close(); self.proc.kill(); self.proc.wait()
            except Exception:
                pass
        self.proc = None


def clip_audio(path, trim, speed, gain_dur):
    """Audio track of an AI clip (if it has one) as a mono float array at SR, or None."""
    t0 = float(trim[0]) if trim else 0.0
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}"] + (["-t", f"{float(trim[1]) - t0:.3f}"] if trim and len(trim) > 1 and trim[1] is not None else []) + \
          ["-i", path, "-vn", "-ac", "1", "-ar", str(SR)]
    sp = float(speed or 1.0)
    if abs(sp - 1.0) > 1e-3 and 0.5 <= sp <= 2.0:
        cmd += ["-af", f"atempo={sp}"]
    cmd += ["-f", "f32le", "-"]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    return np.frombuffer(r.stdout, dtype=np.float32)


# ------------------------------------------------------------------ timeline
def build_timeline(spec, spec_dir="."):
    shots, t = [], 0.0
    snap = spec.get("snap_to_beat", False)
    mood, origin = "cozy", 0.0
    for sh in spec["shots"]:
        s = dict(sh)
        if s.get("clip"):      # AI-generated video clip: dur defaults to the (trimmed, sped-up) clip length
            # both orientations are looked up (X.mp4 / X_land.mp4); the first one found (portrait first) sets duration and clip audio
            paths = find_clips(spec, spec_dir, s["clip"])
            if paths["portrait"] or paths["landscape"]:
                s["clip_paths"] = paths
                s["clip_path"] = paths["portrait"] or paths["landscape"]
            else:
                if not s.get("img"):
                    find_clip(spec, spec_dir, asset_candidates(s["clip"], "portrait")[0][0])      # raises the usual FileNotFoundError
                # animatic fallback: the start still with local motion, until the AI clip exists
                s.pop("clip"); s.pop("trim", None); s.pop("speed", None); s.pop("reverse", None); s.pop("freeze", None)
                s.update(s.pop("fb", {}))
                s["fallback"] = True
        if s.get("clip"):
            if s.get("reverse"):
                s["clip_paths"] = {k: (reversed_clip(v) if v else None) for k, v in s["clip_paths"].items()}
                s["clip_path"] = s["clip_paths"]["portrait"] or s["clip_paths"]["landscape"]
            if "dur" not in s:
                cd, _ = probe_clip(s["clip_path"])
                tr = s.get("trim")
                a0 = float(tr[0]) if tr else 0.0
                a1 = float(tr[1]) if tr and len(tr) > 1 and tr[1] is not None else cd
                s["dur"] = max(0.2, (a1 - a0) / float(s.get("speed") or 1.0))
            s.setdefault("motion", "static")      # no automatic camera move on top of a moving clip (opt in with motion/zoom/punch)
            s.setdefault("zoom0", 1.0)
        s.pop("fb", None)
        if s.get("mood") and s["mood"] != mood:
            if s["mood"] in synth.NEW_MOODS or mood in synth.NEW_MOODS:
                origin = t           # music bar grid restarts at a tempo change
            mood = s["mood"]
        s["start"] = t
        lines, cur = [], t + s.get("lead", 0.3)
        for ln in s.get("lines", []):
            a = tts(ln["who"], ln["text"], ln.get("speed"), ln.get("pitch"))
            if ln.get("gain"):
                a = (a * float(ln["gain"])).astype(np.float32)
            at = t + ln["at"] if "at" in ln else cur
            dur = len(a) / SR
            if ln.get("echo", ln["who"] == "narrator" and spec.get("narrator_echo", False)):
                a = echo_voice(a)
            lines.append(dict(ln, start=at, dur=dur, audio=a))
            cur = at + dur + ln.get("gap", 0.18)
        s["lines"] = lines
        end_voice = (lines[-1]["start"] + lines[-1]["dur"] + s.get("tail", 0.35)) if lines else t
        s["dur"] = max(s["dur"], end_voice - t)
        if s.get("clip") and s.get("fit_clip") and s.get("clip_path"):
            # stretch a shorter AI clip over the shot (slow motion, at most 0.6x) instead of freezing its last frame
            cd, _ = probe_clip(s["clip_path"])
            tr = s.get("trim")
            src = (float(tr[1]) if tr and len(tr) > 1 and tr[1] is not None else cd) - (float(tr[0]) if tr else 0.0)
            if src > 0 and s["dur"] > src:
                s["speed"] = round(max(float(s.get("min_speed", 0.6)), src / s["dur"]), 3)
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
        if sh.get("clip_path") and sh.get("clip_audio"):
            ca = clip_audio(sh["clip_path"], sh.get("trim"), sh.get("speed"), sh["dur"])
            if ca is not None:
                put(sfx, ca[: int(sh["dur"] * SR)], sh["start"], float(sh["clip_audio"]) if not isinstance(sh["clip_audio"], bool) else 1.0)
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


def caption_layer(text, who, W, H=None):
    """Burned-in caption (approved style: white/colour fill, thick brown stroke, extra bold). Portrait: 84% of the width.
    Landscape (W > H): slightly smaller text, at most 60% of the width so it stays a compact block, lower center."""
    land = bool(H) and W > H
    key = ("cap", text, who, W, H if land else None)
    if key in _layer_cache:
        return _layer_cache[key]
    size = int(H * 0.074) if land else int(W * 0.088)
    fnt = font(FONT, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    lines = wrap_text(dummy, text, fnt, W * (0.60 if land else 0.84))
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


def card_layer(card, W, H=None):
    land = bool(H) and W > H
    key = ("card", json.dumps(card, sort_keys=True), W, H if land else None)
    if key in _layer_cache:
        return _layer_cache[key]
    u = H if land else W                          # type scale: 1080 px in both orientations at full resolution
    pad = int(u * 0.05)
    cw = int(W * 0.50) if land else int(W * 0.84)
    label_f, text_f = font(FONT, int(u * 0.040)), font(FONT, int(u * 0.062))
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    body = wrap_text(dummy, card["text"], text_f, cw - 2 * pad)
    lh = int(u * 0.078)
    ch = pad * 2 + int(u * 0.06) + lh * len(body)
    img = Image.new("RGBA", (cw + 30, ch + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((12, 20, cw + 12, ch + 20), radius=44, fill=(59, 42, 26, 90))     # shadow
    d.rounded_rectangle((8, 8, cw + 8, ch + 8), radius=44, fill=(255, 248, 236, 245), outline=(217, 72, 15, 255), width=8)
    d.text((8 + pad, 8 + pad * 0.8), card.get("label", "FUN FACT"), font=label_f, fill=(217, 72, 15, 255))
    for i, ln in enumerate(body):
        d.text((8 + pad, 8 + pad * 0.8 + int(u * 0.07) + i * lh), ln, font=text_f, fill=(59, 42, 26, 255))
    _layer_cache[key] = img
    return img


def title_layer(card, W, H=None):
    land = bool(H) and W > H
    key = ("title", json.dumps(card, sort_keys=True), W, H if land else None)
    if key in _layer_cache:
        return _layer_cache[key]
    u = H if land else W
    f1, f2 = font(FONT, int(u * 0.105)), font(FONT_BOLD, int(u * 0.058))
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    l1 = wrap_text(dummy, card["text"], f1, W * (0.88 if land else 0.86))
    h = len(l1) * int(u * 0.125) + int(u * 0.12)
    img = Image.new("RGBA", (W, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(l1):
        w = d.textlength(ln, font=f1)
        d.text(((W - w) / 2, 10 + i * int(u * 0.125)), ln, font=f1, fill=(255, 255, 255, 255), stroke_width=10, stroke_fill=(217, 72, 15, 255))
    sub = card.get("sub", "")
    if sub:
        w = d.textlength(sub, font=f2)
        d.text(((W - w) / 2, 10 + len(l1) * int(u * 0.125) + 6), sub, font=f2, fill=(255, 245, 230, 255), stroke_width=6, stroke_fill=(59, 42, 26, 255))
    _layer_cache[key] = img
    return img


def importance_map(img):
    """Where the eye goes: spectral-residual saliency + edge density + skin tones (faces, hands) + bright, saturated blobs, 0..1 at ~1/6 size."""
    import cv2
    a = np.asarray(img.convert("RGB"))
    h, w = a.shape[:2]
    k = max(1, int(round(max(h, w) / 220)))
    sm = cv2.resize(a, (max(8, w // k), max(8, h // k)), interpolation=cv2.INTER_AREA)
    g = cv2.cvtColor(sm, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    f = np.fft.fft2(g)
    logamp = np.log(np.abs(f) + 1e-6)
    phase = np.angle(f)
    resid = logamp - cv2.blur(logamp, (3, 3))
    sal = np.abs(np.fft.ifft2(np.exp(resid + 1j * phase))) ** 2
    sal = cv2.GaussianBlur(sal.astype(np.float32), (0, 0), 2.0)
    sal = (sal - sal.min()) / (sal.max() - sal.min() + 1e-9)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    edge = cv2.GaussianBlur(np.sqrt(gx ** 2 + gy ** 2), (0, 0), 2.0)
    edge = np.clip(edge / (np.percentile(edge, 98) + 1e-6), 0, 1)
    r, gg, b = [sm[..., i].astype(np.float32) for i in range(3)]
    skin = ((r > 190) & (r > gg + 8) & (gg > b + 6) & (r < 255) & (gg > 140) & (b > 100) & (r - b < 110)).astype(np.float32)
    skin = cv2.GaussianBlur(skin, (0, 0), 2.5)
    hsv = cv2.cvtColor(sm, cv2.COLOR_RGB2HSV).astype(np.float32)
    sat = np.clip((hsv[..., 1] - 90) / 120, 0, 1) * np.clip((hsv[..., 2] - 60) / 120, 0, 1)
    imp = 0.45 * sal + 0.6 * edge + 1.1 * skin + 0.25 * cv2.GaussianBlur(sat, (0, 0), 2.0)
    imp = cv2.GaussianBlur(imp, (0, 0), 2.5)
    return np.clip(imp / (np.percentile(imp, 97) + 1e-6), 0, 1.5), skin


def safe_caption_y(frame, lay, land, zone=None, avoid=()):
    """Vertical centre (fraction of the height) of the emptiest band for this caption, near the usual spot; faces, hands and dumplings are
    what the importance map marks, so the caption lands beside them (never over them when an empty band exists)."""
    imp, skin = importance_map(frame)
    h, w = imp.shape
    H = frame.height
    bbox = lay.getchannel("A").getbbox()
    lh_frac = (bbox[3] - bbox[1]) / H if bbox else 0.12
    lh_px = max(2, int(round(lh_frac * h)))
    x0, x1 = (int(w * 0.17), int(w * 0.83)) if land else (int(w * 0.08), int(w * 0.92))
    if bbox:
        cw = (bbox[2] - bbox[0]) / lay.width
        x0 = max(0, int(w * (0.5 - cw / 2))); x1 = min(w, int(w * (0.5 + cw / 2)))
    default = 0.85 if land else 0.80
    lo = 0.10 if land else 0.12
    hi = 0.93 if land else 0.88
    if zone == "top":                       # script zone hint: TOP = upper band, BOTTOM = lower band
        lo, hi = (0.10, 0.30) if land else (0.12, 0.36)
    elif zone == "bottom":
        lo, hi = (0.66, 0.93) if land else (0.58, 0.88)
    best, bs = default, 1e9
    for cy in np.arange(lo, hi + 1e-6, 0.01):
        y0 = int((cy - lh_frac / 2 * (1.0)) * h); y1 = y0 + lh_px
        if y0 < 0 or y1 > h:
            continue
        if any(abs(cy - ay) < 0.5 * (ah + lh_frac) for ay, ah in avoid):
            continue
        reg = imp[y0:y1, x0:x1]
        sk = skin[y0:y1, x0:x1]
        sc = 3.0 * float(sk.max() > 0.30) + float(reg.mean()) + 1.0 * float(np.percentile(reg, 93)) + 0.35 * abs(cy - default)
        if sc < bs:
            best, bs = float(cy), sc
    return best


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


def ease_fn(name):
    """Camera easing. Default (None) is the original smoothstep."""
    return {
        "linear": lambda x: min(max(x, 0.0), 1.0),
        "in": lambda x: min(max(x, 0.0), 1.0) ** 2,
        "out": lambda x: 1 - (1 - min(max(x, 0.0), 1.0)) ** 2,
        "inout": ease,
    }.get(name, ease)


def camera_box(img_size, W, H, shot, p, mult=1.0, off=(0.0, 0.0), min_zoom=1.0, pan_mult=1.0, zoom_mult=1.0):
    sw, sh = img_size
    base = max(W / sw, H / sh)           # scale to cover
    zoom0, zoom1 = shot.get("zoom0", 1.0), shot.get("zoom", 1.12)
    motion = shot.get("motion", "zoom_in")
    fx, fy = shot.get("focus", [0.5, 0.5])
    amt = shot.get("pan", 0.06) * pan_mult
    e = ease_fn(shot.get("ease"))(p)
    if motion == "zoom_out":
        z = zoom1 + (zoom0 - zoom1) * e
    elif motion in ("static",):
        z = zoom0
    else:
        z = zoom0 + (zoom1 - zoom0) * e
    z = max(z * zoom_mult * mult, min_zoom)
    vw, vh = W / (base * z), H / (base * z)        # visible window in source px
    cx, cy = fx * sw + off[0] * sw, fy * sh + off[1] * sh
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


GRADES = {   # soft, warm-leaning: (mul r,g,b), (add r,g,b)
    "warm": ((1.05, 1.015, 0.93), (5, 2, -4)),
    "cool": ((0.94, 0.99, 1.06), (-3, 1, 7)),
}
WHIP_T = 0.15

# ------------------------------------------------------------------ puppets (cut-out animation)
PUPPET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "specs", "puppets")
MOUTH_LEVELS = 5


def _back(x, c1=1.70158):
    x = min(max(x, 0.0), 1.0)
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def _out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


class Puppet:
    """A transparent cut-out plus a sidecar rig (<name>.json: eyes, mouth, skin colour).
    Variants (blink x mouth level x flip) are painted once and cached."""

    def __init__(self, name):
        base = os.path.join(PUPPET_DIR, os.path.splitext(name)[0])
        self.img = Image.open(base + ".png").convert("RGBA")
        self.rig = json.load(open(base + ".json")) if os.path.exists(base + ".json") else {}
        self.cache = {}

    @property
    def size(self):
        return self.img.size

    def variant(self, lvl, blink, flip):
        key = (lvl, blink, flip)
        if key in self.cache:
            return self.cache[key]
        im = self.img
        rig = self.rig
        if (lvl > 0 and rig.get("mouth")) or (blink and rig.get("eyes")):
            Z = 2
            ov = Image.new("RGBA", (im.width * Z, im.height * Z), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            pat = Image.new("RGBA", ov.size, tuple(rig.get("skin", [250, 208, 178])) + (0,))
            pd = ImageDraw.Draw(pat)
            skin = tuple(rig.get("skin", [250, 208, 178])) + (255,)
            line = (70, 40, 28, 255)
            if blink and rig.get("eyes"):
                for ex, ey, ew, eh in rig["eyes"]:
                    pd.ellipse(((ex - ew * 0.62) * Z, (ey - eh * 0.8) * Z, (ex + ew * 0.62) * Z, (ey + eh * 0.62) * Z), fill=skin)
                    d.arc(((ex - ew * 0.5) * Z, (ey - eh * 0.42) * Z, (ex + ew * 0.5) * Z, (ey + eh * 0.42) * Z), 18, 162, fill=line, width=int(5 * Z))
            if lvl > 0 and rig.get("mouth"):
                m = rig["mouth"]
                mx, my = m["x"], m["y"]
                pw, ph = m.get("patch", [100, 36])
                pd.ellipse(((mx - pw / 2) * Z, (my - ph / 2) * Z, (mx + pw / 2) * Z, (my + ph / 2) * Z), fill=skin)
                f = lvl / MOUTH_LEVELS
                w = m["w"] * (0.62 + 0.38 * f)
                h = max(5.0, m["h"] * f)
                top = my - m.get("up", 0.25) * h
                box = (( mx - w / 2) * Z, top * Z, (mx + w / 2) * Z, (top + h) * Z)
                mask = Image.new("L", ov.size, 0)
                ImageDraw.Draw(mask).ellipse(box, fill=255)
                inner = Image.new("RGBA", ov.size, (118, 38, 40, 255))
                if h > 14:
                    td = ImageDraw.Draw(inner)
                    td.ellipse((box[0] + w * 0.12 * Z, box[1] + h * 0.52 * Z, box[2] - w * 0.12 * Z, box[3] + h * 0.35 * Z), fill=(232, 120, 122, 255))
                ov.paste(inner, (0, 0), mask)
                d.ellipse(box, outline=line, width=int(max(3, 4) * Z * 0.8))
            pat = pat.filter(ImageFilter.GaussianBlur(2.2 * Z))
            pat.alpha_composite(ov)
            ov = pat.resize(im.size, Image.LANCZOS)
            im = im.copy()
            # paint only where the cut-out is opaque (keeps the silhouette)
            a = im.getchannel("A")
            ov.putalpha(ImageChops_multiply(ov.getchannel("A"), a))
            im.alpha_composite(ov)
        if flip:
            im = ImageOps.mirror(im)
        self.cache[key] = im
        return im


def ImageChops_multiply(a, b):
    from PIL import ImageChops
    return ImageChops.multiply(a, b)


def voice_envelope(audio):
    """Mouth-openness 0..1 at 60 Hz from a voice line's samples."""
    hop = SR // 60
    n = len(audio) // hop
    if n < 2:
        return np.zeros(2, np.float32)
    x = audio[: n * hop].reshape(n, hop)
    rms = np.sqrt((x ** 2).mean(axis=1))
    ref = np.percentile(rms[rms > 0.02], 90) if (rms > 0.02).any() else 1.0
    e = np.clip(rms / (ref or 1.0), 0, 1) ** 0.85
    e = np.convolve(e, np.array([0.25, 0.5, 0.25]), mode="same")
    return e.astype(np.float32)



class Renderer:
    def __init__(self, spec, shots, W, H, fps, frames_dir, orient=None):
        self.orient = orient or ("landscape" if W > H else "portrait")
        self.land = self.orient == "landscape"
        self.U = H if self.land else W            # size unit for fx sprites, text and cards: 1080 px at full resolution in both orientations
        self.shots = [orient_apply(s, self.orient) for s in shots]       # landscape: "<key>_land" overrides "<key>"
        shots = self.shots
        self.spec, self.W, self.H, self.fps = spec, W, H, fps
        self.frames_dir = frames_dir
        self.imgs = {}
        self.picked = {}
        self._capcy = {}
        self.readers = {}
        for s in shots:
            if s.get("img") and not self.clip_file(s):
                self.load(self.pick(s["img"]))
            for k in ("bg", "fg"):
                if s.get("layers", {}).get(k):
                    self.load(self.pick(s["layers"][k]), rgba=(k == "fg"))
        self.pups = {}
        self.envs = {}
        self._cam = None
        for s_ in shots:
            for pp in s_.get("puppets", []):
                if pp["img"] not in self.pups:
                    self.pups[pp["img"]] = Puppet(pp["img"])
        self.rng = np.random.default_rng(3)
        self.parts = {}
        self.grid = None
        self.vig = None
        self.noise = None
        self.fidx = 0
        if spec.get("grain"):
            g = np.random.default_rng(11)
            self.noise = [g.standard_normal((H // 2 + 1, W // 2 + 1)).astype(np.float32) for _ in range(6)]
        v = float(spec.get("vignette", 0) or 0)
        if v > 0:
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            r2 = ((xx / W - 0.5) * 2) ** 2 * 0.8 + ((yy / H - 0.5) * 2) ** 2 * 0.9
            self.vig = (1 - v * 0.5 * np.clip(r2 - 0.25, 0, 1.2) ** 1.3)[..., None].astype(np.float32)

    def pick(self, val):
        """Resolve a still (or layer) for this orientation to an existing path: X.png / X_land.png, a {"portrait","landscape"} dict,
        or the other orientation's picture (center-cover crop, with a warning)."""
        key = json.dumps(val, sort_keys=True)
        if key in self.picked:
            return self.picked[key]
        cands = asset_candidates(val, self.orient)
        for name, exact in cands:
            if os.path.exists(self.resolve(name)):
                if not exact:
                    warn_once(f"no {self.orient} file {cands[0][0]}: using {name} with a center-cover crop")
                self.picked[key] = name
                return name
        self.picked[key] = cands[0][0]
        return cands[0][0]

    def clip_file(self, s):
        """Path of the AI clip for this orientation (X.mp4 / X_land.mp4), or None. Falls back to the other orientation's clip (cropped)."""
        cp = s.get("clip_paths")
        if not cp:
            return s.get("clip_path")
        mine = cp.get(self.orient)
        if mine:
            return mine
        other = cp.get("landscape" if self.land else "portrait")
        if other:
            warn_once(f"no {self.orient} clip for {s.get('id') or s.get('clip')}: using {os.path.basename(other)} with a center-cover crop")
        return other

    def resolve(self, name):
        p = os.path.join(self.frames_dir, name)
        if not os.path.exists(p) and self.spec.get("frames_fallback"):
            alt = os.path.join(os.path.dirname(self.frames_dir.rstrip("/")), os.path.basename(self.spec["frames_fallback"].rstrip("/")), os.path.basename(name))
            if os.path.exists(alt):
                return alt
        return p

    def load(self, name, rgba=False):
        p = self.resolve(name)
        if p not in self.imgs:
            self.imgs[p] = Image.open(p).convert("RGBA" if rgba else "RGB")
        return self.imgs[p]

    def clip_frame(self, s, t_local):
        for fz in s.get("freeze", []):          # 8-frame look-to-lens holds: the clip stops for d seconds
            if t_local >= fz["t"] + fz["d"]:
                t_local -= fz["d"]
            elif t_local >= fz["t"]:
                t_local = fz["t"]
        if s.get("on_twos"):                     # step the clip like hand-drawn animation (e.g. 12 fps)
            t_local = math.floor(t_local * s["on_twos"] + 1e-6) / s["on_twos"]
        key = id(s)
        rd = self.readers.get(key)
        if rd is None:
            rd = self.readers[key] = ClipReader(self.clip_file(s), self.W, self.H, self.fps, s.get("trim"), s.get("speed"), s.get("loop"),
                                                 s.get("crop_focus", (0.5, 0.5)))
        return rd.frame(t_local)

    def release_clips(self, gt):
        """Close decoders of shots that are over (keeps the number of ffmpeg processes small)."""
        for sh in self.shots:
            if self.clip_file(sh) and id(sh) in self.readers and gt > sh["end"] + 1.0:
                self.readers.pop(id(sh)).close()

    # ---- camera
    def cam_time(self, s, t):
        """Hit-stop: the camera freezes for 0.12 s at each impact."""
        imps = [s["impact"]["t"]] if isinstance(s.get("impact"), dict) else []
        for it in sorted(imps):
            if t >= it + 0.12:
                t -= 0.12
            elif t >= it:
                t = it
        return t

    def base_frame(self, s, t_local):
        W, H = self.W, self.H
        layers = s.get("layers") or {}
        if self.clip_file(s):
            img = self.clip_frame(s, t_local)
        else:
            img = self.imgs[self.resolve(self.pick(layers.get("bg") or s["img"]))]
        tc = self.cam_time(s, t_local)
        p = tc / max(s["dur"], 0.01)
        mult = 1.0
        for pu in s.get("punch", []):
            dt = t_local - pu["t"]
            if 0 <= dt < 1.5:
                mult *= 1 + (pu.get("scale", 1.15) - 1) * math.exp(-dt / 0.14)
        sway = float(s.get("sway", self.spec.get("sway", 0)) or 0)
        off, minz = (0.0, 0.0), 1.0
        if sway > 0:
            ph = s["start"] * 1.7
            off = (sway * 0.0045 * (math.sin(2 * math.pi * 0.37 * t_local + ph) + 0.6 * math.sin(2 * math.pi * 0.93 * t_local + ph * 2)),
                   sway * 0.0035 * (math.sin(2 * math.pi * 0.29 * t_local + ph * 3) + 0.5 * math.sin(2 * math.pi * 1.1 * t_local + ph)))
            minz = 1 + 0.03 * sway
        box = camera_box(img.size, W, H, s, p, mult, off, minz)
        shakes = list(s.get("shake", []))
        if isinstance(s.get("impact"), dict):
            shakes.append({"t": s["impact"]["t"], "d": 0.4, "amp": s["impact"].get("amp", 26)})
        sx = sy = 0.0
        for sh in shakes:
            if sh["t"] <= t_local <= sh["t"] + sh["d"]:
                k = (1 - (t_local - sh["t"]) / sh["d"]) * sh.get("amp", 14)
                dx, dy = self.rng.uniform(-k, k, 2)
                sx += dx; sy += dy
        if sx or sy:
            sc = (box[2] - box[0]) / W
            bw, bh = box[2] - box[0], box[3] - box[1]
            nx = min(max(box[0] + sx * sc, 0), img.size[0] - bw)
            ny = min(max(box[1] + sy * sc, 0), img.size[1] - bh)
            box = (nx, ny, nx + bw, ny + bh)
        fr = img.resize((W, H), Image.BICUBIC, box=box)
        self._cam = (box, img.size)
        if layers.get("fg"):      # foreground plane: moves faster than the background
            fg = self.imgs[self.resolve(self.pick(layers["fg"]))]
            drift = math.sin(t_local * 0.6 + s["start"]) * 0.012
            fbox = camera_box(fg.size, W, H, s, p, mult, (off[0] + drift, off[1]), minz, pan_mult=2.2, zoom_mult=1.05)
            if sx or sy:
                sc = (fbox[2] - fbox[0]) / W
                fw, fh = fbox[2] - fbox[0], fbox[3] - fbox[1]
                nx = min(max(fbox[0] + sx * sc * 1.4, 0), fg.size[0] - fw)
                ny = min(max(fbox[1] + sy * sc * 1.4, 0), fg.size[1] - fh)
                fbox = (nx, ny, nx + fw, ny + fh)
            fgr = fg.resize((W, H), Image.BICUBIC, box=fbox)
            fr.paste(fgr, (0, 0), fgr)
        return fr

    # ---- world fx (part of the "scene", drawn under captions)
    def grade(self, fr, name):
        if name in GRADES:
            mul, add = GRADES[name]
            lut = []
            for c in range(3):
                lut += [int(min(255, max(0, v * mul[c] + add[c]))) for v in range(256)]
            return fr.point(lut)
        if name == "sepia":
            tone = ImageOps.colorize(ImageOps.grayscale(fr), (58, 36, 20), (255, 240, 212), (178, 128, 82))
            return Image.blend(fr, tone, 0.55)
        return fr

    def rays(self, fr, t):
        W, H = self.W, self.H
        w, h = max(W // 6, 8), max(H // 6, 8)
        if self.grid is None or self.grid[0] != (w, h):
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            self.grid = ((w, h), xx / w, yy / h)
        _, X, Y = self.grid
        u = X * 0.62 + Y * 0.40
        m = np.zeros((h, w), np.float32)
        for f, ph, sp, a in ((7.0, 0.3, 0.05, 1.0), (11.5, 1.7, -0.035, 0.7), (4.3, 4.0, 0.025, 0.8)):
            m += a * np.clip(np.sin(2 * math.pi * (f * u + sp * t) + ph) - 0.15, 0, 1) ** 2
        m *= np.clip(1.15 - Y * 1.1, 0, 1) * np.clip(1.2 - X * 0.5, 0, 1)
        m = np.clip(m * 0.17, 0, 0.30)
        mask = Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        fr.paste((255, 240, 205), (0, 0), mask)
        return fr

    def particles(self, fr, s, t):
        cfg = s["particles"]
        kind, n = cfg.get("type", "dust"), cfg.get("n", 30)
        key = id(s)
        if key not in self.parts:
            g = np.random.default_rng(int(s["start"] * 1000) + n)
            self.parts[key] = g.uniform(0, 1, (n, 6))
        W, H = self.W, self.H
        for x0, y0, z, a, b, c in self.parts[key]:
            z = 0.35 + 0.65 * z                       # depth: near = bigger, faster, brighter
            if kind == "dust":
                x = (x0 + 0.012 * z * t + 0.03 * math.sin(t * 0.4 + a * 6)) % 1.0
                y = (y0 - 0.010 * z * t + 0.02 * math.sin(t * 0.3 + b * 6)) % 1.0
                r, al, col = self.U * (0.004 + 0.007 * z), 0.35 + 0.25 * math.sin(t * 1.5 + c * 9) ** 2, (255, 244, 214)
            elif kind == "embers":
                x = (x0 + 0.03 * math.sin(t * 1.1 + a * 9) * z) % 1.0
                y = (y0 - 0.085 * z * t) % 1.12 - 0.05
                r, al, col = self.U * (0.004 + 0.007 * z), 0.55 + 0.4 * math.sin(t * 9 + c * 20), (255, 168 + int(60 * b), 80)
            elif kind == "petals":
                x = (x0 + 0.035 * z * t + 0.05 * math.sin(t * 1.2 + a * 9)) % 1.0
                y = (y0 + 0.075 * z * t) % 1.1 - 0.05
                r, al, col = self.U * (0.011 + 0.012 * z), 0.85, (255, 190 + int(25 * b), 205)
            elif kind == "steam":
                x = (x0 + 0.04 * math.sin(t * 0.5 + a * 9)) % 1.0
                y = (y0 - 0.06 * z * t) % 1.2 - 0.1
                r, al, col = self.U * (0.07 + 0.07 * z), 0.10 + 0.05 * z, (255, 255, 255)
            else:  # snow
                x = (x0 + 0.03 * math.sin(t * 0.8 + a * 9) + 0.01 * t * z) % 1.0
                y = (y0 + 0.07 * z * t) % 1.06 - 0.03
                r, al, col = self.U * (0.004 + 0.008 * z), 0.8, (255, 255, 255)
            R = max(2, int(r / 0.45 / 2) * 2)
            aq = int(max(0.0, min(1.0, al)) * 8)
            if aq <= 0:
                continue
            spr = self.sprite(kind, R, aq, int((t * 2 + c * 12) % 12) if kind == "petals" else 0)
            fr.paste(col, (int(x * W - R), int(y * H - R)), spr)
        return fr

    def sprite(self, kind, R, aq, ang):
        key = ("psp", kind, R, aq, ang)
        if key not in _layer_cache:
            if kind == "petals":
                s = Image.new("L", (R * 2, R * 2), 0)
                ImageDraw.Draw(s).ellipse((R * 0.55, R * 0.8, R * 1.45, R * 1.2), fill=255)
                s = s.rotate(ang * 30, resample=Image.BILINEAR).filter(ImageFilter.GaussianBlur(R * 0.06))
            else:
                s = soft_sprite(R, 1.0)
            _layer_cache[key] = s.point(lambda v: int(v * aq / 8))
        return _layer_cache[key]

    def speedlines(self, fr, t, cfg, strength=1.0):
        W, H = self.W, self.H
        dt = t - cfg["t"]
        d = cfg.get("d", 0.5)
        if not (0 <= dt <= d):
            return fr
        a = min(1.0, dt / 0.06, (d - dt) / 0.12 + 0.2) * strength
        w, h = W // 2, H // 2
        g = np.random.default_rng(int(t * 14) * 7919 + 1)          # flicker: new line set ~14x / s
        m = Image.new("L", (w, h), 0)
        dr = ImageDraw.Draw(m)
        if cfg.get("dir", "radial") == "horizontal":
            for _ in range(22):
                y = g.uniform(0, h); ln = g.uniform(0.25, 0.8) * w; x = g.uniform(-0.1, 1.0) * w
                th = g.uniform(1.5, 6)
                dr.rectangle((x, y, x + ln, y + th), fill=int(g.uniform(150, 255)))
        else:
            cx, cy = w * cfg.get("cx", 0.5), h * cfg.get("cy", 0.5)
            for _ in range(54):
                ang = g.uniform(0, 2 * math.pi)
                r0 = g.uniform(0.30, 0.55) * h
                r1 = h * 1.3
                wd = g.uniform(0.012, 0.045)
                p0 = (cx + math.cos(ang) * r0, cy + math.sin(ang) * r0)
                p1 = (cx + math.cos(ang - wd) * r1, cy + math.sin(ang - wd) * r1)
                p2 = (cx + math.cos(ang + wd) * r1, cy + math.sin(ang + wd) * r1)
                dr.polygon([p0, p1, p2], fill=int(g.uniform(160, 255)))
        m = m.filter(ImageFilter.GaussianBlur(0.8)).resize((W, H), Image.BILINEAR)
        m = m.point(lambda v: int(v * 0.72 * a))
        col = (59, 42, 26) if cfg.get("color") == "dark" else (255, 255, 255)
        fr.paste(col, (0, 0), m)
        return fr

    def impact_fx(self, fr, s, t):
        im = s["impact"]
        dt = t - im["t"]
        if dt < 0 or dt > 0.4:
            return fr
        self.speedlines(fr, t, {"t": im["t"], "d": 0.3, "dir": "radial"}, 0.9)
        if dt < 0.05:
            col, a = (255, 255, 255), 0.85
        elif dt < 0.10 and im.get("dark", True):
            col, a = (59, 42, 26), 0.30
        else:
            col, a = (255, 250, 240), 0.5 * max(0.0, 1 - (dt - 0.10) / 0.22)
        if a > 0.01:
            fr = Image.blend(fr, Image.new("RGB", fr.size, col), a)
        return fr

    # ---- puppets
    def line_amp(self, s, ln, t_abs):
        key = (id(s), ln["start"], ln["who"], ln["text"])
        if key not in self.envs:
            self.envs[key] = voice_envelope(ln["audio"])
        env = self.envs[key]
        i = (t_abs - ln["start"]) * 60.0
        if i < 0 or i >= len(env) - 1:
            return 0.0
        i0 = int(i)
        return float(env[i0] * (1 - (i - i0)) + env[i0 + 1] * (i - i0))

    def puppets(self, fr, s, t):
        box, (sw, sh) = self._cam
        W, H = self.W, self.H
        k = W / (box[2] - box[0])
        for pi, pp in enumerate(s["puppets"]):
            pup = self.pups[pp["img"]]
            ph = s["start"] * 1.3 + pi * 2.1 + pp.get("phase", 0.0)
            x, y = pp.get("x", 0.5), pp.get("y", 0.9)
            path = pp.get("path")
            if path:                      # keyframes [{t,x,y}] with smooth interpolation
                pts = sorted(path, key=lambda q: q["t"])
                if t <= pts[0]["t"]:
                    x, y = pts[0].get("x", x), pts[0].get("y", y)
                elif t >= pts[-1]["t"]:
                    x, y = pts[-1].get("x", x), pts[-1].get("y", y)
                else:
                    for a, b in zip(pts, pts[1:]):
                        if a["t"] <= t <= b["t"]:
                            e = ease((t - a["t"]) / max(b["t"] - a["t"], 1e-6))
                            x = a.get("x", x) + (b.get("x", x) - a.get("x", x)) * e
                            y = a.get("y", y) + (b.get("y", y) - a.get("y", y)) * e
                            break
            scale = pp.get("scale", 1.0)
            sx = sy = 1.0
            rot = 0.0
            alpha = 1.0
            # entrance / exit
            en, et, ed = pp.get("enter", "none"), pp.get("enter_t", 0.0), pp.get("enter_d", 0.45)
            if en != "none":
                q = (t - et) / ed
                if q < 0:
                    continue
                if en == "left":
                    x -= 0.75 * (1 - _back(q, 1.0))
                elif en == "right":
                    x += 0.75 * (1 - _back(q, 1.0))
                elif en == "bottom":
                    y += 0.6 * (1 - _back(q, 1.0))
                elif en == "pop":
                    ps = _back(q, 2.2)
                    sx *= max(ps, 0.001); sy *= max(ps, 0.001)
                    if q < 1:
                        rot += (1 - q) * 6
            ex_, ext = pp.get("exit", "none"), pp.get("exit_t", 1e9)
            if ex_ != "none" and t >= ext:
                q = min((t - ext) / pp.get("exit_d", 0.35), 1.0)
                if q >= 1.0:
                    continue
                e = q * q
                x += {"left": -0.8, "right": 0.8}.get(ex_, 0) * e
                y += 0.6 * e if ex_ == "bottom" else 0
            # idle
            idle = pp.get("idle", {})
            br = idle.get("breathe", 0.0)
            if br:
                b = math.sin(2 * math.pi * 0.42 * t + ph)
                sy *= 1 + br * 0.03 * b
                sx *= 1 - br * 0.012 * b
            bob = idle.get("bob", 0.0)
            lift = 0.0
            if bob:
                lift = bob * 0.012 * (0.5 + 0.5 * math.sin(2 * math.pi * 1.1 * t + ph))
            sway = idle.get("sway", 0.0)
            if sway:
                rot += sway * 1.6 * math.sin(2 * math.pi * 0.31 * t + ph * 1.7)
            # hit: damped squash-and-stretch spring (squash first, then stretch)
            for h in pp.get("hit", []):
                dt = t - h["t"]
                if 0 <= dt < 1.2:
                    sq = h.get("squash", 0.2)
                    env = math.exp(-dt / 0.16) * math.cos(2 * math.pi * dt / 0.34)
                    sy *= 1 - sq * env
                    sx *= 1 + sq * 0.7 * env
                    lift += h.get("hop", 0.0) * 0.1 * max(0.0, math.sin(min(dt / 0.35, 1.0) * math.pi)) if dt < 0.35 else 0.0
                    rot += h.get("tilt", 0.0) * math.exp(-dt / 0.2) * math.sin(2 * math.pi * dt / 0.4)
            # talking: mouth from the voice amplitude (+ a tiny nod)
            amp = 0.0
            tk = pp.get("talk")
            t_abs = s["start"] + t
            if tk:
                sel = tk.get("line", "auto") if isinstance(tk, dict) else "auto"
                who = pp.get("who")
                for li, ln in enumerate(s["lines"]):
                    if (sel == "auto" and ln["who"] == who) or sel == li:
                        amp = max(amp, self.line_amp(s, ln, t_abs))
            for m in pp.get("mouth", []):       # manual mouth timeline: {t, d, level 0-5}
                if m["t"] <= t < m["t"] + m["d"]:
                    amp = max(amp, m.get("level", 4) / MOUTH_LEVELS * (0.85 + 0.15 * math.sin(t * 40)) if m.get("jitter") else m.get("level", 4) / MOUTH_LEVELS)
            if amp > 0.05:
                sy *= 1 + 0.018 * amp
                lift += 0.004 * amp
            lvl = int(round(amp * MOUTH_LEVELS)) if amp > 0.12 else 0
            # blink
            blink = False
            if pp.get("blink", True):
                per = 3.3 + 0.9 * (pi % 3)
                blink = ((t + ph) % per) < 0.13
            im = pup.variant(lvl, blink, bool(pp.get("flip")))
            base_h = scale * 0.6 * sh * k * (pp.get("mul", 1.0))
            ih = max(2, int(base_h * sy))
            iw = max(2, int(base_h * pup.size[0] / pup.size[1] * sx))
            spr = im.resize((iw, ih), Image.LANCZOS)
            cx = (x * sw - box[0]) * k
            cy = (y * sh - box[1]) * k - lift * sh * k
            ground = (y * sh - box[1]) * k
            # drop shadow (shrinks when lifted)
            if pp.get("shadow", True):
                sw_ = int(iw * 0.78 * (1 - min(lift * 6, 0.4)))
                shh = max(6, int(sw_ * 0.11))
                shd = Image.new("L", (sw_ + 40, shh * 3 + 40), 0)
                ImageDraw.Draw(shd).ellipse((20, 20 + shh, 20 + sw_, 20 + shh * 2), fill=int(255 * 0.30))
                shd = shd.filter(ImageFilter.GaussianBlur(shh * 0.35 + 2))
                fr.paste((59, 42, 26), (int(cx - shd.width / 2), int(ground - shd.height / 2 - shh * 0.1)), shd)
            if abs(rot) > 0.02:
                pad = int(max(iw, ih) * 0.08) + 4
                cv = Image.new("RGBA", (iw + 2 * pad, ih + pad), (0, 0, 0, 0))
                cv.paste(spr, (pad, pad // 2 + 1))
                cv = cv.rotate(rot, resample=Image.BICUBIC, center=(cv.width / 2, ih + pad // 2 + 1))
                fr.paste(cv, (int(cx - cv.width / 2), int(cy - ih - pad // 2 - 1)), cv)
            else:
                fr.paste(spr, (int(cx - iw / 2), int(cy - ih)), spr)
        return fr

    def scene(self, s, t_local):
        if s.get("black") and t_local < s["black"]:
            return Image.new("RGB", (self.W, self.H), (0, 0, 0))
        fr = self.base_frame(s, t_local)
        if s.get("fade_out") and t_local > s["dur"] - s["fade_out"]:
            fr = Image.blend(fr, Image.new("RGB", fr.size, (0, 0, 0)), min(1.0, (t_local - (s["dur"] - s["fade_out"])) / s["fade_out"]))
        if s.get("puppets"):
            fr = self.puppets(fr, s, t_local)
        if s.get("grade"):
            fr = self.grade(fr, s["grade"])
        if s.get("rays"):
            fr = self.rays(fr, t_local + s["start"])
        if s.get("particles"):
            fr = self.particles(fr, s, t_local)
        if s.get("speedlines"):
            sl = s["speedlines"]
            for c in (sl if isinstance(sl, list) else [sl]):
                fr = self.speedlines(fr, t_local, c)
        if isinstance(s.get("impact"), dict):
            fr = self.impact_fx(fr, s, t_local)
        if s.get("impact_frame"):
            fr = self.impact_poster(fr, t_local, s["impact_frame"])
        return fr

    def whip(self, prev, cur, q):
        """Whip-pan: both frames slide horizontally with motion blur."""
        W = self.W
        wide = np.concatenate([np.asarray(prev), np.asarray(cur)], axis=1)
        e = q * q * (3 - 2 * q)
        off = int(e * W)
        blur = int(W * 0.30 * math.sin(math.pi * min(max(q, 0.0), 1.0))) + 2
        K = int(min(48, max(9, blur // 5)))
        acc = np.zeros((self.H, W, 3), np.float32)
        for i in range(K):
            o = min(max(off + int((i / (K - 1) - 0.5) * blur), 0), W)
            acc += wide[:, o:o + W]
        return Image.fromarray((acc / K).astype(np.uint8))

    def reel(self, fr, t, cfg):
        """Film-reel rewind: sepia flicker, sprocket strips racing upward, tape glitch bars and a REW mark."""
        dt = t - cfg["t"]
        d = cfg.get("d", 1.2)
        if not (0 <= dt <= d):
            return fr
        W, H = self.W, self.H
        a = min(1.0, dt / 0.08, (d - dt) / 0.12 + 0.2)
        tone = ImageOps.colorize(ImageOps.grayscale(fr), (40, 26, 16), (255, 238, 205), (150, 106, 64))
        fr = Image.blend(fr, tone, 0.55 * a)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(ov)
        sw = int(self.U * 0.085)
        sp = int(H * 0.06)
        off = (dt * H * 3.2) % sp
        for x0 in (0, W - sw):
            dr.rectangle((x0, 0, x0 + sw, H), fill=(20, 14, 10, int(235 * a)))
            for k in range(-1, H // sp + 2):
                y = k * sp - off
                dr.rounded_rectangle((x0 + sw * 0.28, y, x0 + sw * 0.72, y + sp * 0.5), 6, fill=(250, 238, 210, int(230 * a)))
        g = np.random.default_rng(int(dt * 24) * 31 + 5)
        for _ in range(5):                           # tape glitch bars sweeping upward
            y = int((g.uniform(0, 1) - dt * 2.0) % 1.0 * H)
            dr.rectangle((sw, y, W - sw, y + int(g.uniform(0.004, 0.03) * H)), fill=(255, 250, 238, int(g.uniform(40, 120) * a)))
        f = font(FONT, int(self.U * 0.075))
        if int(dt * 6) % 2 == 0:
            dr.text((sw + 30, int(H * 0.055)), "\u25C0\u25C0 REW", font=f, fill=(255, 240, 214, int(255 * a)), stroke_width=5, stroke_fill=(59, 42, 26, int(255 * a)))
        fr = fr.convert("RGBA"); fr.alpha_composite(ov)
        return fr.convert("RGB")

    def suck(self, fr, t, cfg):
        """Soft white puffs fly INTO a point (steam sucked back into the ears)."""
        dt = t - cfg["t"]
        d = cfg.get("d", 1.0)
        if not (0 <= dt <= d):
            return fr
        W, H = self.W, self.H
        tx, ty = cfg.get("x", 0.5) * W, cfg.get("y", 0.3) * H
        for i in range(cfg.get("n", 18)):
            g = np.random.default_rng(i * 13 + 1)
            ang, r0 = g.uniform(0, 2 * math.pi), g.uniform(0.18, 0.5) * self.U
            ph = ((dt / d) * 1.4 + g.uniform(0, 0.6)) % 1.0
            rr = r0 * (1 - ph)
            x, y = tx + math.cos(ang) * rr, ty + math.sin(ang) * rr
            rad = int(self.U * (0.03 + 0.06 * (1 - ph)))
            spr = soft_sprite(rad, 1.0).point(lambda v: int(v * 0.5 * math.sin(ph * math.pi)))
            fr.paste((255, 255, 255), (int(x - rad), int(y - rad)), spr)
        return fr

    def impact_poster(self, fr, t, cfg):
        """Impact frame: a white flash, then a flat posterized red/brown/cream frame with radial burst lines (about 0.15 s)."""
        dt = t - cfg["t"]
        d = cfg.get("d", 0.16)
        if not (0 <= dt <= d):
            return fr
        W, H = self.W, self.H
        if dt < 0.04:
            return Image.new("RGB", (W, H), (255, 252, 244))
        g = ImageOps.autocontrast(ImageOps.grayscale(fr), cutoff=2)
        g = g.point(lambda v: 0 if v < 70 else (110 if v < 150 else (190 if v < 225 else 255)))
        pos = ImageOps.colorize(g, (30, 12, 8), (255, 240, 214), (217, 72, 15), blackpoint=0, whitepoint=255, midpoint=110)
        self.speedlines(pos, t, {"t": cfg["t"] + 0.04, "d": d, "dir": "radial", "color": "dark"}, 1.0)
        return pos

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
                    x = (x0 + (x1 - x0) * seed) * W + math.sin(ph * 5 + i) * self.U * 0.03
                    y = (ybase - ph * fx.get("rise", 0.35)) * H
                    r = int(self.U * (0.10 + 0.10 * ph + 0.04 * seed))
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
                    sz = int(self.U * (0.045 + 0.02 * ((i * 37) % 5) / 5))
                    spr = heart_sprite(sz).point(lambda v: int(v * math.sin(ph * math.pi)))
                    frame.paste((255, 130, 160), (int(x - sz), int(y - sz)), spr)
            elif kind == "flash":
                dt = t_local - fx["t"]
                if 0 <= dt <= fx.get("d", 0.12):
                    a = 1 - dt / fx.get("d", 0.12)
                    frame.paste(Image.blend(frame, Image.new("RGB", frame.size, (255, 255, 255)), 0.75 * a))
            elif kind == "reel":
                frame = self.reel(frame, t_local, fx)
            elif kind == "suck":
                frame = self.suck(frame, t_local, fx)
            elif kind == "vignette_warm":
                pass
        # cards
        for c in s.get("cards", []):
            dt = t_local - c["t"]
            if self.land:                       # per-card landscape overrides: "y_land", "x_land", "text_land", ...
                c = dict(c, **{k[:-len(LAND_SUFFIX)]: v for k, v in c.items() if k.endswith(LAND_SUFFIX)})
            if c.get("type") == "paper":
                if 0 <= dt <= c["d"]:
                    import paper.cards as pcards
                    pcards.draw(frame, c, dt, W, H)
                continue
            if 0 <= dt <= c["d"]:
                lay = title_layer(c, W, H) if c["type"] == "title" else card_layer(c, W, H)
                pop = ease(dt / 0.22)
                out = ease((c["d"] - dt) / 0.2)
                a = min(pop, out)
                sc = 0.88 + 0.12 * pop
                lw, lh = int(lay.width * sc), int(lay.height * sc)
                l2 = lay.resize((lw, lh), Image.BILINEAR)
                if a < 1:
                    l2.putalpha(l2.getchannel("A").point(lambda v: int(v * a)))
                if self.land:      # horizontal: fact cards sit in the upper third, titles a little higher than center; captions own the bottom
                    cy = c["y"] if "y_land" in c else (0.42 if c["type"] == "title" else 0.30)
                    cy = min(max(cy * H, lh / 2 + 0.05 * H), H - lh / 2 - 0.05 * H)
                    frame.paste(l2, (int(c.get("x", 0.5) * W) - lw // 2, int(cy) - lh // 2), l2)
                    continue
                pos_y = int(c.get("y", 0.62) * H) - lh // 2
                frame.paste(l2, ((W - lw) // 2, pos_y), l2)
        # captions (burned in; portrait: safe zone above the Shorts UI, landscape: lower center, inside the 5% title-safe margin)
        for ln in s["lines"]:
            if ln.get("caption") is False:
                continue
            dt = t_local - (ln["start"] - s["start"])
            if -0.02 <= dt <= ln["dur"] + 0.04:
                lay = caption_layer(ln.get("caption", ln["text"]), ln["who"], W, H)
                pop = ease(max(dt, 0) / 0.12)
                sc = 0.9 + 0.1 * pop
                lw, lh = int(lay.width * sc), int(lay.height * sc)
                l2 = lay.resize((lw, lh), Image.BILINEAR) if sc != 1 else lay
                manual = s.get("caption_y_land") if self.land else s.get("caption_y")      # manual per-shot position wins
                if manual is None and self.spec.get("caption_safe") and s.get("caption_auto", True):
                    ck = (s.get("id"), s.get("start"), ln.get("text"), ln.get("start"))
                    if ck not in self._capcy:
                        avoid = []
                        for cd in s.get("cards", []):          # keep clear of fact cards / titles of this shot
                            if self.land:
                                cyc = cd.get("y_land", 0.42 if cd.get("type") == "title" else 0.30) if cd.get("type") != "paper" else 0.3
                            else:
                                cyc = cd.get("y", 0.62)
                            avoid.append((cyc, 0.16 if cd.get("type") in ("fact", "title") else 0.1))
                        self._capcy[ck] = safe_caption_y(frame, lay, self.land, s.get("caption_zone"), avoid)
                    cy = self._capcy[ck] * self.H
                elif self.land:
                    cy = self.H * (manual if manual is not None else self.spec.get("caption_y_land", 0.84))
                else:
                    cy = self.H * (manual if manual is not None else self.spec.get("caption_y", 0.67))
                if self.land:
                    cy = min(max(cy, lh / 2 + 0.05 * self.H), self.H * 0.955 - lh / 2)
                frame.paste(l2, ((W - lw) // 2, int(cy) - lh // 2), l2)
        return frame

    def post(self, fr):
        if self.vig is None and self.noise is None:
            return fr
        arr = np.asarray(fr, dtype=np.float32)
        if self.vig is not None:
            arr = arr * self.vig
        if self.noise is not None:
            g = np.roll(self.noise[self.fidx % 6], (self.fidx * 37) % 17, axis=0)
            g = np.repeat(np.repeat(g, 2, axis=0), 2, axis=1)[: self.H, : self.W]
            arr = arr + (g * 3.0)[..., None]            # light, soft grain
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    def frame_at(self, gt):
        s = None
        for i, sh in enumerate(self.shots):
            if gt < sh["end"] or i == len(self.shots) - 1:
                s, idx = sh, i
                break
        t_local = gt - s["start"]
        fr = self.scene(s, t_local)
        tf = s.get("fade", 0.18)
        if idx > 0 and s.get("whip") and t_local < WHIP_T:
            prev = self.shots[idx - 1]
            pf = self.scene(prev, prev["dur"] + t_local)
            fr = self.whip(pf, fr, t_local / WHIP_T)
        elif idx > 0 and s.get("transition", "fade") == "fade" and t_local < tf:
            prev = self.shots[idx - 1]
            pf = self.scene(prev, prev["dur"] + t_local)
            fr = Image.blend(pf, fr, ease(t_local / tf))
        fr = self.overlays(fr, s, t_local)
        if self.readers and self.fidx % 30 == 0:
            self.release_clips(gt)
        return self.post(fr)


def render_video(spec, shots, total, wav, W, H, fps, fdir, orient, out, mobile):
    """Render one orientation to `out` (audio already mixed in `wav`); optionally the mobile version (720x1280 / 1280x720)."""
    r = Renderer(spec, shots, W, H, fps, fdir, orient)
    nframes = int(total * fps)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", str(spec.get("crf", 18)), "-pix_fmt", "yuv420p",
           "-af", "loudnorm=I=-16:TP=-2:LRA=11", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(nframes):
        r.fidx = i
        p.stdin.write(r.frame_at(i / fps).tobytes())
        if i % (fps * 10) == 0:
            print(f"  [{orient}] frame {i}/{nframes}", flush=True)
    p.stdin.close(); p.wait()
    for rd in list(r.readers.values()):
        rd.close()
    print("done", out)
    if mobile:
        mob = os.path.splitext(out)[0] + "-mobile.mp4"
        size = "scale=1280:720:flags=lanczos" if orient == "landscape" else "scale=720:1280:flags=lanczos"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-vf", size, "-c:v", "libx264",
                        "-profile:v", "main", "-crf", "27", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-16:TP=-2:LRA=11", "-c:a", "aac", "-b:a", "128k", "-ac", "1",
                        "-movflags", "+faststart", mob], check=True)
        print("mobile", mob)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("out")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--audio-only", action="store_true")
    ap.add_argument("--frames-dir", default=None)
    ap.add_argument("--mobile", action="store_true", help="also write <out>-mobile.mp4 (720x1280 portrait / 1280x720 landscape, H.264 Main, crf 27, AAC 128k mono)")
    og = ap.add_mutually_exclusive_group()
    og.add_argument("--landscape", action="store_true", help="render the horizontal 16:9 version (1920x1080) to <out>")
    og.add_argument("--portrait", action="store_true", help="render the vertical 9:16 version (1080x1920) to <out> (default; overrides spec orientation)")
    og.add_argument("--both", action="store_true", help="render both: <out> (9:16) and <out stem>-land<ext> (16:9); audio is mixed once")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    PITCH_OVERRIDE.update(spec.get("voice_pitch", {}))
    set_cast(spec)
    global FALLBACK_KOKORO
    FALLBACK_KOKORO = bool(spec.get("voice_fallback", True))
    VOICE_SPEED.update(spec.get("voice_speed", {}))
    global MAX_PAUSE
    MAX_PAUSE = float(spec.get("max_pause", 0.40))
    want = spec.get("orientation", "portrait")        # spec field: "portrait" | "landscape" | "both"
    if want not in ("portrait", "landscape", "both"):
        raise SystemExit(f"spec orientation must be portrait, landscape or both, not {want!r}")
    if a.both:
        want = "both"
    elif a.landscape:
        want = "landscape"
    elif a.portrait:
        want = "portrait"
    stem, ext = os.path.splitext(a.out)
    jobs = {"portrait": [("portrait", a.out)], "landscape": [("landscape", a.out)],
            "both": [("portrait", a.out), ("landscape", f"{stem}-land{ext or '.mp4'}")]}[want]
    fps = 15 if a.preview else spec.get("fps", 30)
    fdir = a.frames_dir or os.path.join(os.path.dirname(os.path.abspath(a.spec)), spec.get("frames_dir", "frames"))
    shots, total = build_timeline(spec, os.path.dirname(os.path.abspath(a.spec)))
    print(f"timeline: {len(shots)} shots, {total:.1f}s", flush=True)
    wav = a.out + ".audio.wav"
    render_audio(spec, shots, total, wav)
    print("audio done", flush=True)
    if a.audio_only:
        return
    for orient, out in jobs:
        W, H = video_size(spec, orient, a.preview)
        print(f"rendering {orient} {W}x{H} -> {out}", flush=True)
        render_video(spec, shots, total, wav, W, H, fps, fdir, orient, out, a.mobile)


if __name__ == "__main__":
    main()
