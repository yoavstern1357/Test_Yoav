#!/usr/bin/env python3
"""Run the image-to-video notebook on Kaggle's free GPU, fully automated (used by .github/workflows/kaggle-gpu.yml).

    KAGGLE_API_TOKEN=... python3 kaggle_run.py jobs/run.json --out results/

Job file: {"run_id": "smoke-001", "input": "tools/episode_maker/gpu/inputs/sample",
           "smoke": true, "backend": "ltx", "only": "", "max_minutes": 300}
Steps: upload the input folder (clips.json + images/) as a private dataset, push a private notebook with
GPU T4 x2 + internet, wait until it finishes, download its output into --out.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
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


def patch_notebook(src, dst, job):
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
                    line = f"BACKEND = {json.dumps(job.get('backend', 'ltx'))}"
                elif key == "ONLY":
                    line = f"ONLY = {json.dumps(job.get('only', ''))}"
                elif key == "MAX_MINUTES":
                    line = f"MAX_MINUTES = {int(job.get('max_minutes', 300))}"
                lines.append(line)
            s = "\n".join(lines) + "\n"
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
    k_slug = "dumpling-clips-" + job["run_id"].lower().replace("_", "-")
    k_dir = os.path.join(work, "k")
    os.makedirs(k_dir)
    patch_notebook(os.path.join(HERE, "dumpling_clips.ipynb"), os.path.join(k_dir, "dumpling_clips.ipynb"), job)
    json.dump({"id": f"{user}/{k_slug}", "title": k_slug, "code_file": "dumpling_clips.ipynb",
               "language": "python", "kernel_type": "notebook", "is_private": True,
               "enable_gpu": True, "enable_internet": True, "enable_tpu": False,
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
    if "error" in status:
        sys.exit(1)


if __name__ == "__main__":
    main()
