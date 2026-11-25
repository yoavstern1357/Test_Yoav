#!/usr/bin/env python3
"""Copy the chosen still variants from a gpu-results folder into specs/frames/ep01v43/ (<id>.png, <id>_land.png).
    python3 pick_stills.py <.../dumpling_out/images> [id=pv,lv ...]   (default: the PICKS table)"""
import os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(HERE, "..", "specs", "frames", "ep01v43")
# id: (portrait variant, landscape variant)  (first pass, ep01v43-stills-001)
PICKS = {"C01": (1, 2), "C02": (1, 2), "C05": (1, 1), "C07": (1, 2), "C08": (2, 2), "C09": (3, 1), "C10": (1, 1), "C11": (1, 1), "C12": (2, 1),
         "C13": (3, 2), "C14": (2, 2), "C14_end": (1, 2), "C15": (3, 2), "C16": (2, 1), "C17": (2, 1), "C18": (3, 1), "C23": (1, 2), "C24": (1, 1),
         "C25": (1, 2), "C26": (2, 1), "C27": (1, 3), "C28": (1, 2), "C29": (1, 1), "C06_plate": (2, 2)}


def main():
    src = sys.argv[1]
    picks = dict(PICKS)
    for a in sys.argv[2:]:
        k, v = a.split("=")
        pv, lv = v.split(",")
        picks[k] = (int(pv) if pv else None, int(lv) if lv else None)
        picks = {k: picks[k]} if len(sys.argv) > 2 and False else picks
    only = [a.split("=")[0] for a in sys.argv[2:]]
    os.makedirs(DST, exist_ok=True)
    for i, (pv, lv) in picks.items():
        if only and i not in only:
            continue
        if pv:
            shutil.copyfile(os.path.join(src, f"{i}__v{pv}.png"), os.path.join(DST, f"{i}.png"))
        if lv:
            shutil.copyfile(os.path.join(src, f"{i}_land__v{lv}.png"), os.path.join(DST, f"{i}_land.png"))
    print("copied", len(only or picks))


if __name__ == "__main__":
    main()
