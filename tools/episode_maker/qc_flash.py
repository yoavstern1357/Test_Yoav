#!/usr/bin/env python3
"""Photosensitivity (flash) QC for a rendered video: prints PASS / FAIL. CPU only; needs ffmpeg + numpy.

    python3 tools/episode_maker/qc_flash.py tools/episode_maker/out/episode-01-v4.4.mp4
    python3 tools/episode_maker/qc_flash.py VIDEO --json report.json --strict     # strict: max 2 flashes per second

What it checks (production/v4/attention-and-pace-spec.md, section "Flicker rules"). It is a screening tool modelled on
WCAG 2.2 SC 2.3.1 "Three Flashes or Below Threshold" and ITU-R BT.1702 / the Harding test; it is NOT a certified Harding FPA run.
  1. General flash: a pair of opposing changes of relative luminance >= 10 % of the maximum (0.10 on a 0-1 scale) where the darker
     frame is below 0.80 (WCAG 2.0/2.1 wording), over an area of at least 25 % of a 10-degree field. At 1024x768 that field is
     341x256 px, so the area threshold here is 0.25 * 341*256 / (1024*768) = 2.8 % of the picture (conservative for a phone).
  2. Red flash: opposing changes of the saturated-red area (R/(R+G+B) >= 0.8, WCAG working definition) over the same area.
  3. Limit: more than 3 flashes in any 1-second window FAILS (--strict: more than 2). Exactly at the limit is a WARN.
  4. Large red: a saturated-red area >= 25 % of the picture that appears or disappears within 0.25 s is a WARN (design rule: no
     full-frame red flashes); it FAILs if it also alternates (a red flash as in 2).
Method: ffmpeg decodes the video at a small size (rgb24), per frame we compute linear relative luminance per pixel, compare each frame
with the previous one, and record the signed area of pixels that got brighter / darker by >= 0.10 (darker side < 0.80). Each frame
with a signed area >= 2.8 % is one "transition"; a flash = two opposing transitions; flashes per window = reversals / 2.
Not covered: spatial patterns (stripes, checkerboards), luminance changes below 10 %, whole-screen drift over >1 s (not a flash).
Exit code 0 = PASS (WARNs allowed), 1 = FAIL."""
import argparse, json, subprocess, sys
import numpy as np

AREA_FRAC = 0.25 * 341 * 256 / (1024 * 768)   # 0.0278 of the picture
DELTA = 0.10                                   # 10 % of max relative luminance
DARK_MAX = 0.80
RED_RATIO = 0.8
BIG_RED = 0.25


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(n) / float(d), float(s.get("duration") or 0)


def lin(u8):
    c = u8.astype(np.float32) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def frames(path, w, h, fps_cap):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-an", "-vf", f"fps={fps_cap},scale={w}:{h}:flags=area", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = w * h * 3
    while True:
        b = p.stdout.read(size)
        if len(b) < size:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)
    p.wait()


def reversals_windows(events, fps, limit):
    """events: list of (frame_index, sign). Returns (max_flashes_per_second, worst_window_start_s, list_of_window_starts_over_limit)."""
    best, best_t, over = 0.0, 0.0, []
    win = int(round(fps))
    ev = events
    for i in range(len(ev)):
        j = i
        rev = 0
        while j + 1 < len(ev) and ev[j + 1][0] - ev[i][0] < win:
            if ev[j + 1][1] != ev[j][1]:
                rev += 1
            j += 1
        flashes = rev / 2.0
        if flashes > best:
            best, best_t = flashes, ev[i][0] / fps
        if flashes > limit:
            over.append(round(ev[i][0] / fps, 2))
    return best, best_t, over


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--strict", action="store_true", help="limit 2 flashes per second instead of 3")
    ap.add_argument("--max-fps", type=float, default=30.0, help="analyse at most this many frames per second (default 30)")
    ap.add_argument("--size", type=int, default=96, help="short side of the analysis picture in px (default 96)")
    ap.add_argument("--json", help="write the report to this file")
    a = ap.parse_args()
    limit = 2 if a.strict else 3
    W0, H0, fps0, dur = probe(a.video)
    fps = min(fps0, a.max_fps)
    if W0 <= H0:
        w, h = a.size, int(round(a.size * H0 / W0 / 2) * 2)
    else:
        h, w = a.size, int(round(a.size * W0 / H0 / 2) * 2)
    prev_y, prev_r = None, None
    ev_gen, ev_red = [], []
    big_red_frames = []
    n = 0
    for n, fr in enumerate(frames(a.video, w, h, fps)):
        l = lin(fr)
        y = 0.2126 * l[..., 0] + 0.7152 * l[..., 1] + 0.0722 * l[..., 2]
        s = fr.astype(np.float32).sum(axis=2) + 1e-6
        red = ((fr[..., 0].astype(np.float32) / s) >= RED_RATIO) & (fr[..., 0] > 100)
        red_area = float(red.mean())
        if red_area >= BIG_RED:
            big_red_frames.append(n)
        if prev_y is not None:
            d = y - prev_y
            dark = np.minimum(y, prev_y) < DARK_MAX
            up = float(((d >= DELTA) & dark).mean())
            dn = float(((d <= -DELTA) & dark).mean())
            if max(up, dn) >= AREA_FRAC:
                ev_gen.append((n, 1 if up >= dn else -1))
            dr = red_area - prev_r
            if abs(dr) >= AREA_FRAC:
                ev_red.append((n, 1 if dr > 0 else -1))
        prev_y, prev_r = y, red_area
    if n == 0:
        print("FAIL: no frames decoded"); return 1
    g_best, g_t, g_over = reversals_windows(ev_gen, fps, limit)
    r_best, r_t, r_over = reversals_windows(ev_red, fps, limit)
    # big red appearing / vanishing quickly
    big_red_warn = []
    if big_red_frames:
        run_start = big_red_frames[0]; prevf = big_red_frames[0]
        for f in big_red_frames[1:] + [None]:
            if f is None or f != prevf + 1:
                if (prevf - run_start + 1) <= int(0.25 * fps):
                    big_red_warn.append(round(run_start / fps, 2))
                if f is not None:
                    run_start = f
            if f is not None:
                prevf = f
    fails, warns = [], []
    if g_over:
        fails.append(f"general flash: up to {g_best:.1f} flashes/s (limit {limit}) at {g_over[0]:.2f} s (+{len(g_over) - 1} more windows)")
    elif g_best >= limit:
        warns.append(f"general flash: {g_best:.1f} flashes/s at {g_t:.2f} s is AT the limit ({limit})")
    if r_over:
        fails.append(f"red flash: up to {r_best:.1f} red flashes/s (limit {limit}) at {r_over[0]:.2f} s")
    elif r_best >= limit:
        warns.append(f"red flash: {r_best:.1f} red flashes/s at {r_t:.2f} s is AT the limit ({limit})")
    if big_red_warn:
        (fails if r_best >= 1.0 else warns).append(f"large saturated red (>= 25 % of the picture) for <= 0.25 s at {big_red_warn[:5]} s: avoid full-frame red flashes")
    report = dict(video=a.video, size=f"{W0}x{H0}", fps=round(fps0, 3), analysed_frames=n + 1, duration_s=round(dur, 2), limit=limit,
                  general_transitions=len(ev_gen), max_general_flashes_per_s=round(g_best, 2), max_general_at_s=round(g_t, 2),
                  max_red_flashes_per_s=round(r_best, 2), fails=fails, warns=warns, result="FAIL" if fails else "PASS")
    print(f"{a.video}: {W0}x{H0} @ {fps0:.2f} fps, {n + 1} frames analysed ({w}x{h}), {len(ev_gen)} luminance transitions >= 10 % over >= {AREA_FRAC * 100:.1f} % of the picture")
    print(f"max general flashes in any 1 s: {g_best:.1f} (at {g_t:.2f} s) | max red flashes in any 1 s: {r_best:.1f} | limit {limit}")
    for x in warns:
        print("WARN ", x)
    for x in fails:
        print("FAIL ", x)
    print("RESULT:", report["result"])
    if a.json:
        json.dump(report, open(a.json, "w"), indent=1)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
