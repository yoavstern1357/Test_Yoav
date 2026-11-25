#!/usr/bin/env python3
"""Side-by-side comparison video of the motion-compare job: one segment per shot, one column per backend.

    python3 build_motion_compare.py <results dir with clips/ (e.g. dumpling_out)> [out.mp4]

Default output: tools/episode_maker/out/motion-compare.mp4.  Clips are looked up as clips/<shot>_<tag>.mp4; a missing clip becomes a "no result" card.
Time per clip is read from the clip's .json (GPU seconds) and shown in the label.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CELL_W, CELL_H, LABEL_H = 360, 624, 70
COLS = [("ltx095", "LTX 0.9.5 2B (now)"), ("ltx098d", "LTX 0.9.8 13B distilled nf4"), ("wan5b", "Wan2.2 TI2V-5B"), ("fastwan", "FastWan2.2 5B (3 steps)")]
SEGMENTS = [("uncle", "Uncle reaction close-up", COLS), ("chase", "Chase (two characters, action)", COLS), ("macro", "Food macro", COLS),
            ("gag", "Keyframes start + end (uncle gag)", [("ltx095_kf", "LTX 0.9.5 + end frame"), ("ltx098d_kf", "LTX 0.9.8d + end frame"), ("wan5b_kf", "Wan 5B + end frame (hack)")]),
            ("uncle", "Uncle: 12 fps generated + RIFE x2 (half the GPU time)", [("ltx098d", "24 fps generated"), ("ltx098d_12fps", "12 fps + RIFE")])]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-500:])


def label_png(path, w, text, sub, ok=True):
    im = Image.new("RGB", (w, LABEL_H), (28, 22, 16) if ok else (90, 20, 20))
    d = ImageDraw.Draw(im)
    d.text((8, 6), text, font=ImageFont.truetype(FONT, 17), fill=(255, 227, 184))
    d.text((8, 36), sub, font=ImageFont.truetype(FONT, 15), fill=(236, 198, 106))
    im.save(path)


def main():
    res = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "out", "motion-compare.mp4")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    tmp = tempfile.mkdtemp()
    segs = []
    for si, (shot, title, cols) in enumerate(SEGMENTS):
        cells = []
        for ci, (tag, name) in enumerate(cols):
            clip = os.path.join(res, "clips", f"{shot}_{tag}.mp4")
            meta = os.path.join(res, "clips", f"{shot}_{tag}.json")
            sub = "no result"
            ok = os.path.exists(clip)
            if ok:
                try:
                    m = json.load(open(meta))
                    sub = f"{m.get('seconds', '?')} s on a T4, {m.get('steps', '?')} steps"
                except Exception:
                    sub = "ok"
            else:
                try:
                    sub = "failed: " + json.load(open(meta)).get("error", "")[:40]
                except Exception:
                    pass
            lab = os.path.join(tmp, f"l{si}_{ci}.png")
            label_png(lab, CELL_W, name, sub, ok)
            cell = os.path.join(tmp, f"c{si}_{ci}.mp4")
            if ok:
                vf = f"fps=24,scale={CELL_W}:{CELL_H}:flags=lanczos,setsar=1"
                run(["ffmpeg", "-v", "error", "-y", "-i", clip, "-i", lab, "-filter_complex", f"[0:v]{vf}[v];[1:v]format=rgb24[l];[l][v]vstack,format=yuv420p[o]",
                     "-map", "[o]", "-t", "4.05", "-r", "24", "-c:v", "libx264", "-crf", "17", cell])
            else:
                blank = Image.new("RGB", (CELL_W, CELL_H), (60, 60, 60)); bp = os.path.join(tmp, f"b{si}_{ci}.png"); blank.save(bp)
                run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", bp, "-i", lab, "-filter_complex", "[0:v]format=rgb24[v];[1:v]format=rgb24[l];[l][v]vstack,format=yuv420p[o]",
                     "-map", "[o]", "-t", "4.05", "-r", "24", "-c:v", "libx264", "-crf", "17", cell])
            cells.append(cell)
        seg = os.path.join(tmp, f"seg{si}.mp4")
        # title bar on top
        tp = os.path.join(tmp, f"t{si}.png")
        w = CELL_W * len(cols)
        im = Image.new("RGB", (max(w, 720), 44), (0, 0, 0)); ImageDraw.Draw(im).text((10, 10), title, font=ImageFont.truetype(FONT, 20), fill=(255, 255, 255)); im.save(tp)
        inputs = sum([["-i", c] for c in cells], []) + ["-loop", "1", "-i", tp]
        W = max(w, 720)
        fc = "".join(f"[{i}:v]" for i in range(len(cells))) + f"hstack=inputs={len(cells)}[h];[h]pad={W}:ih:0:0:color=black[hp];[{len(cells)}:v]format=yuv420p[t];[t][hp]vstack,format=yuv420p,scale={1440}:-2[o]"
        run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", fc, "-map", "[o]", "-t", "4.05", "-r", "24", "-c:v", "libx264", "-crf", "18", seg])
        segs.append(seg)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out])
    print("wrote", out)


if __name__ == "__main__":
    main()
