#!/usr/bin/env python3
"""Quality check of a render: duration, size, loudness (EBU R128), silence gaps, and a contact sheet JPG.
    python3 qa_render.py out/episode-01-v4.3.mp4 [--sheet sheet.jpg] [--cols 10] [--rows 8]"""
import argparse, json, re, subprocess, sys, os
from PIL import Image


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mp4"); ap.add_argument("--sheet"); ap.add_argument("--cols", type=int, default=10); ap.add_argument("--rows", type=int, default=8)
    ap.add_argument("--thumb", type=int, default=192)
    a = ap.parse_args()
    p = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate:format=duration,size", "-of", "json", a.mp4]).stdout)
    dur = float(p["format"]["duration"]); size = int(p["format"]["size"]) / 1e6
    v = [s for s in p["streams"] if s.get("width")][0]
    print(f"{os.path.basename(a.mp4)}: {dur:.2f} s  {v['width']}x{v['height']}  {size:.1f} MB")
    r = run(["ffmpeg", "-nostats", "-vn", "-i", a.mp4, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r), re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)
    print("loudness:", m[0][-1] if m[0] else "?", "LUFS integrated; true peak", m[1][-1] if m[1] else "?", "dBFS")
    s = run(["ffmpeg", "-nostats", "-vn", "-i", a.mp4, "-af", "silencedetect=noise=-45dB:d=1.2", "-f", "null", "-"]).stderr
    print("silences > 1.2 s:", re.findall(r"silence_start: ([\d.]+)", s) or "none")
    if a.sheet:
        n = a.cols * a.rows
        tw = a.thumb if v["width"] < v["height"] else int(a.thumb * 16 / 9)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.mp4, "-vf", f"fps={n / dur:.5f},scale={tw}:-1,tile={a.cols}x{a.rows}", "-frames:v", "1", a.sheet], check=True)
        print("sheet", a.sheet)


if __name__ == "__main__":
    main()
