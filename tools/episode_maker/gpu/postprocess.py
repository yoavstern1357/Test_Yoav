#!/usr/bin/env python3
"""CPU post-processing for AI clips: Real-ESRGAN anime upscale + RIFE frame interpolation (no GPU minutes used).

    python3 postprocess.py in.mp4 out.mp4 --fps-in 12 --fps-out 24 --rife 2 --esrgan --size 720x1280
    python3 postprocess.py --bench                       # prints seconds per frame for both stages

Models (downloaded once to ~/.cache/dumpling, or $DUMPLING_CACHE):
  * realesr-animevideov3 (BSD-3-Clause, xinntao/Real-ESRGAN v0.2.5.0): tiny anime video upscaler, 4x, plain PyTorch. Measured on a 4-core CPU:
    about 8 s per 480x832 frame (13 min per 97-frame clip); on a GPU it takes a fraction of a second (the GPU is used when present, ESRGAN_DEVICE=cpu forces the CPU).
  * rife-ncnn-vulkan 20221029 (MIT, nihui): model "rife-v4.6" (the only family that supports -n; "rife-anime" does not), run with `-g -1` (CPU).  Needs libvulkan1 (apt-get install -y libvulkan1).
Order: upscale first (n frames), RIFE second (on the final size): the upscaler is the expensive stage, so it sees the fewest frames.
Also imported by generate_clips.py (PostQueue) so a Kaggle session post-processes clip N on the CPU while the GPU makes clip N+1.
"""
import argparse, glob, os, shutil, subprocess, sys, tempfile, time, urllib.request, zipfile

CACHE = os.environ.get("DUMPLING_CACHE") or os.path.join(os.path.expanduser("~"), ".cache", "dumpling")
ESRGAN_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth"
RIFE_URL = "https://github.com/nihui/rife-ncnn-vulkan/releases/download/20221029/rife-ncnn-vulkan-20221029-ubuntu.zip"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def fetch(url, dst):
    if os.path.exists(dst):
        return dst
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    log("downloading", url)
    urllib.request.urlretrieve(url, dst + ".part")
    os.replace(dst + ".part", dst)
    return dst


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise RuntimeError(f"{cmd[0]} failed ({r.returncode}): {(r.stderr or r.stdout)[-400:]}")
    return r


def video_size(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path])
    w, h = r.stdout.strip().split(",")[:2]
    return int(w), int(h)


# ------------------------------------------------------------------ Real-ESRGAN (realesr-animevideov3 = SRVGGNetCompact)
_net = None


def esrgan_net():
    global _net
    if _net is not None:
        return _net
    import torch
    from torch import nn

    class SRVGGNetCompact(nn.Module):
        def __init__(self, num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=16, upscale=4):
            super().__init__()
            self.upscale = upscale
            self.body = nn.ModuleList([nn.Conv2d(num_in_ch, num_feat, 3, 1, 1), nn.PReLU(num_parameters=num_feat)])
            for _ in range(num_conv):
                self.body.append(nn.Conv2d(num_feat, num_feat, 3, 1, 1)); self.body.append(nn.PReLU(num_parameters=num_feat))
            self.body.append(nn.Conv2d(num_feat, num_out_ch * upscale * upscale, 3, 1, 1))
            self.upsampler = nn.PixelShuffle(upscale)

        def forward(self, x):
            out = x
            for layer in self.body:
                out = layer(out)
            out = self.upsampler(out)
            return out + nn.functional.interpolate(x, scale_factor=self.upscale, mode="nearest")

    net = SRVGGNetCompact()
    dev = "cuda" if torch.cuda.is_available() and os.environ.get("ESRGAN_DEVICE", "auto") != "cpu" else "cpu"
    sd = torch.load(fetch(ESRGAN_URL, os.path.join(CACHE, "realesr-animevideov3.pth")), map_location="cpu", weights_only=True)
    net.load_state_dict(sd.get("params", sd), strict=True)
    _net = net.eval().to(dev)
    log(f"Real-ESRGAN anime on {dev}")
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    return _net


def esrgan_frames(src_dir, dst_dir, size):
    """Upscale every PNG in src_dir 4x with the anime model, then Lanczos to `size` (w, h) if given."""
    import numpy as np, torch
    from PIL import Image
    net = esrgan_net()
    os.makedirs(dst_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src_dir, "*.png")))
    for f in files:
        im = Image.open(f).convert("RGB")
        x = torch.from_numpy(np.asarray(im, dtype=np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0).to(next(net.parameters()).device)
        with torch.no_grad():
            y = net(x).clamp_(0, 1)[0].permute(1, 2, 0).cpu().numpy()
        out = Image.fromarray((y * 255.0 + 0.5).astype(np.uint8))
        if size:
            out = out.resize(tuple(size), Image.LANCZOS)
        out.save(os.path.join(dst_dir, os.path.basename(f)), compress_level=1)
    return len(files)


# ------------------------------------------------------------------ RIFE (ncnn, CPU)
def rife_bin():
    exe = os.environ.get("RIFE_BIN")
    if exe and os.path.exists(exe):
        return exe
    hit = glob.glob(os.path.join(CACHE, "rife", "*", "rife-ncnn-vulkan"))
    if hit:
        return hit[0]
    z = fetch(RIFE_URL, os.path.join(CACHE, "rife.zip"))
    zipfile.ZipFile(z).extractall(os.path.join(CACHE, "rife"))
    hit = glob.glob(os.path.join(CACHE, "rife", "*", "rife-ncnn-vulkan"))
    os.chmod(hit[0], 0o755)
    return hit[0]


def rife_frames(src_dir, dst_dir, factor, model="rife-v4.6"):
    n = len(glob.glob(os.path.join(src_dir, "*.png")))
    os.makedirs(dst_dir, exist_ok=True)
    try:
        exe = rife_bin()
        run([exe, "-i", src_dir, "-o", dst_dir, "-m", model, "-n", str(n * factor), "-g", "-1", "-j", "2:2:2"], cwd=os.path.dirname(exe))
    except Exception as ex:                       # e.g. libvulkan missing: fall back to duplicating frames (no smoothing, still the right rate)
        log("RIFE failed, duplicating frames instead:", str(ex)[:200])
        k = 0
        for f in sorted(glob.glob(os.path.join(src_dir, "*.png"))):
            for _ in range(factor):
                shutil.copy(f, os.path.join(dst_dir, "%08d.png" % k)); k += 1
    return len(glob.glob(os.path.join(dst_dir, "*.png")))


# ------------------------------------------------------------------ pipeline
def process(src, dst, fps_in=24, fps_out=24, interp=0, esrgan=False, size=None, crf=16, rife_model="rife-v4.6"):
    """src mp4 -> dst mp4. size = (w, h) of the final video (None = keep). interp = RIFE factor (2 doubles the frames)."""
    tmp = tempfile.mkdtemp(prefix="post_")
    try:
        a = os.path.join(tmp, "a"); os.makedirs(a)
        run(["ffmpeg", "-v", "error", "-y", "-i", src, os.path.join(a, "%08d.png")])
        cur = a
        w, h = video_size(src)
        size = tuple(size) if size else None
        if esrgan:
            b = os.path.join(tmp, "b")
            esrgan_frames(cur, b, size or (w * 2, h * 2))
            cur = b
        if interp and interp > 1:
            c = os.path.join(tmp, "c")
            rife_frames(cur, c, int(interp), rife_model)
            cur = c
        vf = f"scale={size[0]}:{size[1]}:flags=lanczos" if (size and not esrgan) else "null"
        part = dst + ".part.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps_out if interp and interp > 1 else fps_in), "-i", os.path.join(cur, "%08d.png"),
             "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", part])
        os.replace(part, dst)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?"); ap.add_argument("dst", nargs="?")
    ap.add_argument("--fps-in", type=float, default=24); ap.add_argument("--fps-out", type=float, default=24)
    ap.add_argument("--rife", type=int, default=0, help="interpolation factor (2 = 12 -> 24 fps)")
    ap.add_argument("--esrgan", action="store_true"); ap.add_argument("--size", default=None, help="final size, e.g. 720x1280")
    ap.add_argument("--crf", type=int, default=16); ap.add_argument("--rife-model", default="rife-v4.6")
    ap.add_argument("--bench", action="store_true")
    a = ap.parse_args()
    if a.bench:
        return bench()
    size = [int(v) for v in a.size.lower().split("x")] if a.size else None
    t0 = time.time()
    process(a.src, a.dst, a.fps_in, a.fps_out, a.rife, a.esrgan, size, a.crf, a.rife_model)
    log(f"done in {time.time() - t0:.0f} s -> {a.dst}")


def bench():
    from PIL import Image
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s"); os.makedirs(src)
    import numpy as np
    for i in range(6):
        Image.fromarray((np.random.rand(832, 480, 3) * 255).astype("uint8")).save(os.path.join(src, "%08d.png" % i))
    t = time.time(); esrgan_frames(src, os.path.join(tmp, "e"), (720, 1280)); log("esrgan 480x832 -> 720x1280: %.2f s/frame" % ((time.time() - t) / 6))
    t = time.time(); n = rife_frames(os.path.join(tmp, "e"), os.path.join(tmp, "r"), 2); log("rife 720x1280: %.2f s per output frame" % ((time.time() - t) / n))


if __name__ == "__main__":
    main()
