"""Shared pieces of the notebook builders (build_notebook.py for clips, build_images_notebook.py for stills)."""
import os
import nbformat

HERE = os.path.dirname(os.path.abspath(__file__))

# Fail fast (and say why) when the session has no GPU: nothing is installed or downloaded without one.
GPU_CHECK = '''
import os, sys, subprocess, glob, shutil, zipfile
ON_KAGGLE = os.path.exists("/kaggle/working")
ON_COLAB = "COLAB_GPU" in os.environ or "google.colab" in sys.modules
print("Kaggle" if ON_KAGGLE else "Colab" if ON_COLAB else "other machine")
OUT = "/kaggle/working/dumpling_out" if ON_KAGGLE else "/content/dumpling_out" if ON_COLAB else os.path.abspath("dumpling_out")
os.makedirs(OUT, exist_ok=True)

def _gpu_list():
    try:
        return subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=30).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""

GPU_LIST = _gpu_list()
print(GPU_LIST or "NO GPU FOUND")
if "GPU" not in GPU_LIST:                      # fail fast
    msg = ("NO GPU: this session has no accelerator (nvidia-smi is missing or lists no device). "
           "Kaggle: the kernel must be pushed with enable_gpu=true and machine_shape=NvidiaTeslaT4 (kaggle_run.py does this), "
           "the account must be phone verified and the weekly GPU quota must not be used up. "
           "Colab: Runtime > Change runtime type > T4 GPU. Stopping now.")
    open(os.path.join(OUT, "NO_GPU.txt"), "w").write(msg + "\\n")
    raise RuntimeError(msg)
'''

# Finds the input folder at any depth Kaggle may mount a dataset at ({F} = the json file name).
FIND_INPUT = '''
def find_input():
    pats = ["/kaggle/input/" + "*/" * d + "{F}" for d in range(0, 5)]
    pats += ["/content/dumpling_input/{F}", "/content/drive/MyDrive/dumpling_input/{F}", "./dumpling_input/{F}", "./{F}"]
    for pat in pats:
        hit = sorted(glob.glob(pat))
        if hit:
            return os.path.dirname(hit[0])
    return None
'''

KERNEL_META = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
               "language_info": {"name": "python"},
               "accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4"},
               "kaggle": {"accelerator": "nvidiaTeslaT4", "isInternetEnabled": True, "language": "python",
                          "sourceType": "notebook", "isGpuEnabled": True}}


class Builder:
    def __init__(self):
        self.cells = []

    def md(self, s):
        self.cells.append(nbformat.v4.new_markdown_cell(s.strip("\n")))

    def py(self, s):
        self.cells.append(nbformat.v4.new_code_cell(s.strip("\n")))

    def write(self, name):
        nb = nbformat.v4.new_notebook(cells=self.cells)
        nb.metadata = KERNEL_META
        nbformat.validate(nb)
        nbformat.write(nb, os.path.join(HERE, name))
        print("wrote", name, "with", len(self.cells), "cells")
