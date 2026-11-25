"""CLI for the v4.3 code clips: python3 -m paper.render3 [C03 C06 ...] [--both | --landscape] [--scale 0.5] [--sheet out.png] [--out DIR]
Writes out/ep01v43/code/Cxx.mp4 (1080x1920) and Cxx_land.mp4 (1920x1080)."""
import argparse, os, sys, time
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib
m = None
from paper.core import W, H, ROOT, Writer
from paper.clips import LW, LH, land_compose, FPS


def registry():
    global m
    return {n: getattr(m, n)() for n in dir(m) if n.startswith("C") and n[1:3].isdigit() and isinstance(getattr(m, n), type) and getattr(m, n).__module__ == m.__name__}


def render(c, path, orient, scale=1.0):
    land = orient == "landscape"
    n = int(round(c.dur * FPS))
    ow, oh = (LW, LH) if land else (W, H)
    w, h = int(ow * scale), int(oh * scale)
    wr = Writer(path, FPS, w, h) if path else None
    out, last, lastkey = [], None, None
    for i in range(n):
        t = i / FPS
        if isinstance(c, m.Native):
            img = c.draw(t, land)
        else:
            c.land_t = t
            ts = c.tstep(t)
            if c.cacheable(t) and lastkey == ts and last is not None:
                img = last
            else:
                img = c.frame(t, ts)
                if img.size != (W, H):
                    img = img.resize((W, H))
                last, lastkey = img, ts
            if land:
                nat = c.frame_land(t, ts)
                img = nat if nat is not None else land_compose(img, c.land_zoom, c.land_focus(t))
        if scale != 1.0:
            img = img.resize((w, h), Image.LANCZOS)
        (wr.write(img) if wr else out.append(img))
    if wr:
        wr.close()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--module", default="clips3")
    ap.add_argument("--out", default=None)
    ap.add_argument("--sheet"); ap.add_argument("--scale", type=float, default=1.0); ap.add_argument("--cols", type=int, default=8)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--landscape", action="store_true"); g.add_argument("--both", action="store_true")
    a = ap.parse_args()
    global m
    m = importlib.import_module("paper." + a.module)
    a.out = a.out or os.path.join(ROOT, "out", "ep01v43" if a.module == "clips3" else "ep01v44", "code")
    orients = ["portrait", "landscape"] if a.both else ["landscape"] if a.landscape else ["portrait"]
    reg = registry()
    os.makedirs(a.out, exist_ok=True)
    for n in (a.names or sorted(reg)):
        c = reg[n]
        for o in orients:
            t0 = time.time()
            suf = "_land" if o == "landscape" else ""
            if a.sheet:
                sc = 0.25 if o == "portrait" else 0.2
                fr = render(c, None, o, sc)
                idx = [int(i * (len(fr) - 1) / (a.cols - 1)) for i in range(a.cols)]
                tw, th = fr[0].size
                sh = Image.new("RGB", (tw * a.cols, th))
                for k, i in enumerate(idx):
                    sh.paste(fr[i], (k * tw, 0))
                sh.save(a.sheet.replace(".png", f"-{n}{suf}.png"))
            else:
                render(c, os.path.join(a.out, f"{n}{suf}.mp4"), o, a.scale)
            print(n + suf, f"{c.dur}s", f"{time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
