"""CLI: python3 -m paper.render [C03 ...] [--out DIR] [--sheet] [--scale 0.5]"""
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
    a = ap.parse_args()
    reg = registry()
    names = a.names or sorted(reg)
    for n in names:
        c = reg[n]
        t0 = time.time()
        if a.sheet:
            frames = clips.render_clip(c, None, fps=30, scale=0.25)
            idx = [int(i * (len(frames) - 1) / (a.cols * 2 - 1)) for i in range(a.cols * 2)]
            tw, th = frames[0].size
            sh = Image.new("RGB", (tw * a.cols, th * 2))
            for k, i in enumerate(idx):
                sh.paste(frames[i], ((k % a.cols) * tw, (k // a.cols) * th))
            sh.save(a.sheet.replace(".png", f"-{n}.png"))
        else:
            clips.render_clip(c, os.path.join(a.out, f"{n}.mp4"), scale=a.scale)
        print(n, f"{c.dur}s", f"{time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
