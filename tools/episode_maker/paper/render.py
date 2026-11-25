"""CLI: python3 -m paper.render [C03 ...] [--out DIR] [--sheet x.png] [--scale 0.5] [--landscape | --both]
Writes Cxx.mp4 (1080x1920) and/or Cxx_land.mp4 (1920x1080)."""
import argparse, os, sys, time
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paper import clips, clips2
from paper.core import W, H, ROOT


def registry():
    reg = {}
    for mod in (clips, clips2):
        for n in dir(mod):
            o = getattr(mod, n)
            if n.startswith("C") and n[1:3].isdigit() and isinstance(o, type) and o.__module__ == mod.__name__:
                reg[n] = o()
    return reg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "ep01v4", "code"))
    ap.add_argument("--sheet", help="write a contact sheet PNG instead of an mp4 (path)")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--cols", type=int, default=8)
    og = ap.add_mutually_exclusive_group()
    og.add_argument("--landscape", action="store_true", help="render only the horizontal 16:9 version (Cxx_land.mp4)")
    og.add_argument("--both", action="store_true", help="render the vertical and the horizontal version")
    a = ap.parse_args()
    orients = ["portrait", "landscape"] if a.both else ["landscape"] if a.landscape else ["portrait"]
    reg = registry()
    names = a.names or sorted(reg)
    for n in names:
        c = reg[n]
        for orient in orients:
            t0 = time.time()
            suf = "_land" if orient == "landscape" else ""
            if a.sheet:
                frames = clips.render_clip(c, None, fps=30, scale=0.25, orient=orient)
                idx = [int(i * (len(frames) - 1) / (a.cols * 2 - 1)) for i in range(a.cols * 2)]
                tw, th = frames[0].size
                sh = Image.new("RGB", (tw * a.cols, th * 2))
                for k, i in enumerate(idx):
                    sh.paste(frames[i], ((k % a.cols) * tw, (k // a.cols) * th))
                sh.save(a.sheet.replace(".png", f"-{n}{suf}.png"))
            else:
                clips.render_clip(c, os.path.join(a.out, f"{n}{suf}.mp4"), scale=a.scale, orient=orient)
            print(n + suf, f"{c.dur}s", f"{time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
