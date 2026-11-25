#!/usr/bin/env python3
"""Side-by-side comparison video of the motion-compare job: one segment per shot, one column per backend.

    python3 build_motion_compare.py <results dir 1> [<results dir 2> ...] [out.mp4]      (dirs contain clips/, e.g. .../motion-compare-001/dumpling_out)

Default output: tools/episode_maker/out/motion-compare.mp4.  Clips are looked up as clips/<shot>_<tag>.mp4; a missing clip becomes a "no result" card.
Time per clip is read from the clip's .json (GPU seconds) and shown in the label.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CELL_W, CELL_H, LABEL_H = 360, 624, 70
# (clip id, label); clips are looked up in every results directory given on the command line (round 1, round 2)
SEGMENTS = [
    ("Uncle reaction close-up (4 s, 480x832)", [("uncle_ltx095", "LTX 0.9.5 2B (current)"), ("uncle_ltx098d", "LTX 0.9.8 13B distilled nf4"), ("uncle_fastwan", "FastWan2.2 5B, 3 steps (384x672)")]),
    ("Chase: two characters, action", [("chase_ltx095", "LTX 0.9.5 2B (current)"), ("chase_ltx098d", "LTX 0.9.8 13B distilled nf4"), ("chase_fastwan", "FastWan2.2 5B, 3 steps (384x672)")]),
    ("Food macro", [("macro_ltx095", "LTX 0.9.5 2B (current)"), ("macro_ltx098d", "LTX 0.9.8 13B distilled nf4"), ("macro_fastwan", "FastWan2.2 5B, 3 steps (384x672)")]),
    ("Keyframes: start + end still of the uncle gag", [("gag_ltx095_kf", "LTX 0.9.5 + end frame"), ("gag_ltx098d_kf", "LTX 0.9.8d + end frame at 4.0 s"), ("gag_kf_end28", "LTX 0.9.8d + end frame at 2.8 s")]),
    ("LTX 0.9.8d settings: camera and motion strength", [("uncle_ltx098d", "no camera sentence, motion medium"), ("uncle_fixcam_med", "fixed camera, medium"), ("uncle_fixcam_high", "fixed camera, high"), ("uncle_4step", "fixed camera, 4 steps")]),
    ("Cheaper: 12 fps generated + RIFE x2 (and Real-ESRGAN anime)", [("uncle_ltx098d", "24 fps generated"), ("uncle_12fps_rife", "12 fps + RIFE (CPU)"), ("chase_fixcam_med", "chase 24 fps"), ("chase_12fps_esrgan_rife", "chase 12 fps + ESRGAN + RIFE"), ("chase_576", "chase generated at 576x1024")]),
]
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


def find(dirs, cid):
    for d in dirs:
        p = os.path.join(d, "clips", cid + ".mp4")
        if os.path.exists(p):
            return p, os.path.join(d, "clips", cid + ".json")
    return None, os.path.join(dirs[0], "clips", cid + ".json")


def main():
    args = sys.argv[1:]
    out = args.pop() if args and args[-1].endswith(".mp4") else os.path.join(HERE, "..", "out", "motion-compare.mp4")
    dirs = args
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    tmp = tempfile.mkdtemp()
    segs = []
    for si, (title, cols) in enumerate(SEGMENTS):
        cells = []
        for ci, (cid, name) in enumerate(cols):
            clip, meta = find(dirs, cid)
            sub, ok = "no result", clip is not None
            if ok:
                try:
                    m = json.load(open(meta))
                    sub = f"{m.get('seconds', '?')} s on a T4 (incl. model load for the first clip)" if False else f"{m.get('seconds', '?')} s GPU, {m.get('steps', '?')} steps, {m.get('gen_fps', 24):g} fps"
                except Exception:
                    sub = "ok"
            lab = os.path.join(tmp, f"l{si}_{ci}.png")
            label_png(lab, CELL_W, name, sub, ok)
            cell = os.path.join(tmp, f"c{si}_{ci}.mp4")
            if ok:
                vf = f"fps=24,scale={CELL_W}:{CELL_H}:flags=lanczos,setsar=1"
                run(["ffmpeg", "-v", "error", "-y", "-i", clip, "-i", lab, "-filter_complex", f"[0:v]{vf}[v];[1:v]format=rgb24[l];[l][v]vstack,format=yuv420p[o]",
                     "-map", "[o]", "-t", "4.05", "-r", "24", "-c:v", "libx264", "-crf", "17", cell])
            else:
                bp = os.path.join(tmp, f"b{si}_{ci}.png"); Image.new("RGB", (CELL_W, CELL_H), (60, 60, 60)).save(bp)
                run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", bp, "-i", lab, "-filter_complex", "[0:v]format=rgb24[v];[1:v]format=rgb24[l];[l][v]vstack,format=yuv420p[o]",
                     "-map", "[o]", "-t", "4.05", "-r", "24", "-c:v", "libx264", "-crf", "17", cell])
            cells.append(cell)
        seg = os.path.join(tmp, f"seg{si}.mp4")
        tp = os.path.join(tmp, f"t{si}.png")
        W = max(CELL_W * len(cols), 1080)
        im = Image.new("RGB", (W, 44), (0, 0, 0)); ImageDraw.Draw(im).text((10, 10), title, font=ImageFont.truetype(FONT, 20), fill=(255, 255, 255)); im.save(tp)
        inputs = sum([["-i", c] for c in cells], []) + ["-loop", "1", "-i", tp]
        n = len(cells)
        fc = "".join(f"[{i}:v]" for i in range(n)) + f"hstack=inputs={n}[h];[h]pad={W}:ih:0:0:color=black[hp];[{n}:v]format=yuv420p[t];[t][hp]vstack,format=yuv420p,scale=1440:-2[o]"
        run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", fc, "-map", "[o]", "-t", "4.05", "-r", "24", "-c:v", "libx264", "-crf", "18", seg])
        segs.append(seg)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out])
    print("wrote", out)


if __name__ == "__main__":
    main()
