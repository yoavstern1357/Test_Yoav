#!/usr/bin/env python3
"""Run a notebook on Kaggle's free GPU, fully automated (used by .github/workflows/kaggle-gpu.yml).

    KAGGLE_API_TOKEN=... python3 kaggle_run.py jobs/run.json --out results/

Job file (all keys except run_id and input are optional):
  {"run_id": "smoke-001", "input": "tools/episode_maker/gpu/inputs/sample",
   "task": "clips",            # "clips" (default, image-to-video, input has clips.json) or "images" (stills, input has images.json)
   "notebook": "",            # default: dumpling_clips.ipynb / dumpling_images.ipynb (a file in this folder)
   "backend": "ltx",          # default ltx for clips, klein for images (images: klein | qwen)
   "smoke": true, "only": "", "max_minutes": 300,
   "accelerator": "NvidiaTeslaT4"}   # Kaggle machine_shape: T4 x2
Steps: upload the input folder as a private dataset, push a private notebook with GPU T4 x2 + internet, wait until it
finishes, download its output into --out. Exit code 2 = the session had no GPU (see NO_GPU.txt in the output).
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
# task -> (notebook file, input json, default backend, kernel/dataset slug prefix)
TASKS = {
    "clips": ("dumpling_clips.ipynb", "clips.json", "ltx", "dumpling-clips-"),
    "images": ("dumpling_images.ipynb", "images.json", "klein", "dumpling-images-"),
}
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def sh(*args, check=True):
    print("+", " ".join(args), flush=True)
    r = subprocess.run(args, capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-3000:], flush=True)
    if check and r.returncode:
        sys.exit(f"command failed: {args}")
    return r.stdout + r.stderr


def username():
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    u = api.get_config_value("username")
    if not u:
        sys.exit("could not read the Kaggle username from the token")
    return u


def patch_notebook(src, dst, job, default_backend="ltx"):
    nb = json.load(open(src, encoding="utf-8"))
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        s = "".join(c["source"])
        if "SMOKE_TEST =" in s and "BACKEND =" in s:
            lines = []
            for line in s.splitlines():
                key = line.split("=")[0].strip()
                if key == "SMOKE_TEST":
                    line = f"SMOKE_TEST = {bool(job.get('smoke'))}"
                elif key == "BACKEND":
                    line = f"BACKEND = {json.dumps(job.get('backend') or default_backend)}"
                elif key == "ONLY":
                    line = f"ONLY = {json.dumps(job.get('only', ''))}"
                elif key == "MAX_MINUTES":
                    line = f"MAX_MINUTES = {int(job.get('max_minutes', 300))}"
                lines.append(line)
            s = "\n".join(lines) + "\n"
        # older notebook builds only looked two levels deep; current ones search 0-4 levels (nb_common.FIND_INPUT)
        s = s.replace('"/kaggle/input/*/*/clips.json",',
                      '"/kaggle/input/*/*/clips.json", "/kaggle/input/*/*/*/clips.json", "/kaggle/input/*/*/*/*/clips.json",')
        c["source"] = s.splitlines(keepends=True)
    json.dump(nb, open(dst, "w", encoding="utf-8"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--out", default="kaggle_results")
    ap.add_argument("--timeout-min", type=int, default=330)
    a = ap.parse_args()
    job = json.load(open(a.job))
    task = job.get("task", "clips")
    if task not in TASKS:
        sys.exit(f"unknown task {task!r}: use one of {sorted(TASKS)}")
    nb_file, input_json, default_backend, slug_prefix = TASKS[task]
    nb_file = job.get("notebook") or nb_file
    if not os.path.exists(os.path.join(HERE, nb_file)):
        sys.exit(f"notebook not found: {os.path.join(HERE, nb_file)}")
    if not os.path.exists(os.path.join(REPO, job["input"], input_json)):
        sys.exit(f"task {task!r} needs {input_json} in {job['input']}")
    user = username()
    print("kaggle user ok", flush=True)
    work = tempfile.mkdtemp()

    # 1. dataset
    ds_slug = "dumpling-input-" + job["run_id"].lower().replace("_", "-")
    ds_dir = os.path.join(work, "ds")
    shutil.copytree(os.path.join(REPO, job["input"]), ds_dir)
    json.dump({"title": ds_slug, "id": f"{user}/{ds_slug}", "licenses": [{"name": "CC0-1.0"}]},
              open(os.path.join(ds_dir, "dataset-metadata.json"), "w"))
    out = sh("kaggle", "datasets", "create", "-p", ds_dir, "-r", "zip", check=False)
    if "already" in out.lower() or "exists" in out.lower():
        sh("kaggle", "datasets", "version", "-p", ds_dir, "-r", "zip", "-m", job["run_id"])
    for _ in range(60):
        st = sh("kaggle", "datasets", "status", f"{user}/{ds_slug}", check=False)
        if "ready" in st.lower():
            break
        time.sleep(10)

    # 2. notebook
    k_slug = slug_prefix + job["run_id"].lower().replace("_", "-")
    k_dir = os.path.join(work, "k")
    os.makedirs(k_dir)
    patch_notebook(os.path.join(HERE, nb_file), os.path.join(k_dir, nb_file), job, default_backend)
    # machine_shape picks the accelerator explicitly (enable_gpu alone can leave a session without a GPU)
    json.dump({"id": f"{user}/{k_slug}", "title": k_slug, "code_file": nb_file,
               "language": "python", "kernel_type": "notebook", "is_private": True,
               "enable_gpu": True, "machine_shape": job.get("accelerator", "NvidiaTeslaT4"),
               "enable_internet": True, "enable_tpu": False,
               "dataset_sources": [f"{user}/{ds_slug}"], "competition_sources": [], "kernel_sources": []},
              open(os.path.join(k_dir, "kernel-metadata.json"), "w"), indent=1)
    sh("kaggle", "kernels", "push", "-p", k_dir)

    # 3. wait
    t0 = time.time()
    status = ""
    while time.time() - t0 < a.timeout_min * 60:
        time.sleep(60)
        status = sh("kaggle", "kernels", "status", f"{user}/{k_slug}", check=False).lower()
        if any(w in status for w in ("complete", "error", "cancel")):
            break
    print("final status:", status, flush=True)

    # 4. output
    os.makedirs(a.out, exist_ok=True)
    sh("kaggle", "kernels", "output", f"{user}/{k_slug}", "-p", a.out, check=False)
    open(os.path.join(a.out, "kaggle_status.txt"), "w").write(status)
    for root, _, files in os.walk(a.out):
        if "NO_GPU.txt" in files:
            print("\n" + open(os.path.join(root, "NO_GPU.txt")).read(), flush=True)
            sys.exit(2)
    if "error" in status:
        sys.exit(1)


if __name__ == "__main__":
    main()
