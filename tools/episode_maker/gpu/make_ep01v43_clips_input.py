#!/usr/bin/env python3
"""Builds the GPU "clips" input for Episode 1 v4.3 + series intro (LTX image-to-video) from the chosen stills in specs/frames/ep01v43/.
    python3 make_ep01v43_clips_input.py A     -> inputs/ep01v43-clips-A  (priority clips)
    python3 make_ep01v43_clips_input.py B     -> inputs/ep01v43-clips-B  (the rest)
Stills are copied as JPEG (quality 92) into <input>/images/<id>.jpg and <id>_land.jpg."""
import json, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(HERE, "..", "specs", "frames", "ep01v43")

STYLE = ("soft watercolor anime, delicate gentle line art, warm muted palette, consistent character design, smooth natural animation, the camera stays steady")
NEG = ("realistic, photorealistic, 3D render, photo, style change, deformed hands, extra limbs, extra fingers, extra people, text, watermark, subtitles, logo, "
       "blurry, low quality, distorted face, changing clothes, morphing, flickering, scene cut, camera shake")
BOY = "the small boy in the conical leaf hat"
UNCLE = "the big fat bald uncle with the mustache"

# id: (prompt, seconds, cond_noise, group)
CLIPS = {
 "I1": ("Close-up. The boy and the big fat uncle bite into soup dumplings at the same moment, steam bursts out of the dumplings, their eyes go wide with joy, they chew happily.", 4, 0.2, "A"),
 "I2": ("Macro slow motion. A soup dumpling bursts and golden soup splashes up in a crown of droplets that hang in the air, steam curls up, droplets sparkle.", 4, 0.25, "A"),
 "I3": ("Both float in a giant pool full of white dumplings like a ball pit, laughing. The dumplings bob and roll gently, the boy waves his arm, the fat uncle lounges back on a big dumpling float and laughs, his belly shaking.", 4, 0.25, "A"),
 "I5": ("The boy and the fat uncle run toward the camera down a lantern-lit street in full panic, eyes wide, mouths open screaming, arms flailing. Right behind them a giant white dumpling with a huge chomping mouth rolls after them, its mouth opening and closing, steam rising from its top, dust kicks up.", 4, 0.3, "A"),
 "I5b": ("Wide view of the lantern street. The boy and the fat uncle run away in panic, and behind them the giant dumpling with the big chomping mouth bounces after them, lanterns swinging.", 4, 0.3, "A"),
 "I5c": ("A hand flicks three small gyoza dumplings like throwing stars, they spin fast through the air with glowing motion trails toward the giant dumpling.", 4, 0.3, "A"),
 "I6": ("Low angle. The giant dumpling's huge mouth snaps shut with a chomp just behind the boy and the fat uncle as they leap forward out of frame, dust and crumbs fly.", 4, 0.3, "A"),
 "C01": ("Macro. One soup dumpling is lifted slowly on chopsticks above a bamboo basket, the thin skin sags like a small water balloon and the golden soup sways inside, steam drifts up. Slow and calm.", 5, 0.12, "A"),
 "C02": (f"{BOY} smiles warmly at the camera and glances sideways at his uncle. Behind him on the stool {UNCLE} holds an ice pack on his cheek, fans his tongue with a napkin, faint steam from his ears, and lifts one limp hand.", 5, 0.18, "A"),
 "C07": (f"{BOY} walks backward toward the camera at an easy pace, smiling, the chopstick microphone in his hand, the camera tracks backward with him. Far behind, {UNCLE} strolls across the lane rubbing his stomach. Willow branches sway.", 5, 0.22, "A"),
 "C08": (f"Slow push-in on the two old brick pagodas, wind chimes swing in the breeze. {BOY} points up at them, {UNCLE} beside him looks up, and his gaze softens. A bird flies by.", 5, 0.2, "A"),
 "C13": (f"The chopsticks of {UNCLE} dart toward the basket; {BOY} blocks them with his chopstick microphone like a barrier arm; the uncle lifts one dumpling like a trophy with his chest out. Grandma steps back. Steam drifts.", 4, 0.22, "A"),
 "C14": (f"{UNCLE} pops the whole dumpling into his mouth, his cheeks puff out, one eye twitches, a sweat drop swells on his bald head, then he rockets up into the air, both ears blasting long jets of white steam, his mustache standing up like antennae.", 4, 0.35, "A"),
 "C15": (f"{UNCLE} settles after skidding, fans his tongue with his hand, and takes the cup of cold water from Grandma, steam leaking from one ear. Grandma smiles kindly, {BOY} watches him with concern.", 4, 0.2, "A"),
 "C23": (f"The napkin cape of {UNCLE} flutters in the breeze while he holds the spoon up like a sword, proud. {BOY} gives him a warm amused look, then turns toward the camera and smiles.", 5, 0.2, "A"),
 "C05": (f"The metro car sways gently, {BOY} reads the journal then looks out of the window with a small smile, buildings slide past outside. Beside him {UNCLE} sleeps upright hugging a thermos, his mouth moves in his sleep.", 5, 0.18, "B"),
 "C09": ("Grandma pleats one dumpling in two quick turns of her fingers and holds it up. The boy at the counter follows her fingers with his eyes. Steam rises from the bamboo steamers, the big uncle behind sniffs the steam.", 5, 0.2, "B"),
 "C10": ("The knife chops the block of amber jelly into tiny cubes, the cubes tumble into the bowl of pink minced pork. Steam drifts in the background.", 4, 0.22, "B"),
 "C11": ("The steamer lid lifts, steam parts, inside the dumpling skin the jelly cubes slowly melt into a golden pool and the skin glows warmly.", 5, 0.2, "B"),
 "C12": (f"Grandma's fingers spin the pleats of a dumpling quickly. {BOY} counts with his lips, {UNCLE} counts on his fingers, loses count, starts again, then gives up with a shrug.", 5, 0.2, "B"),
 "C16": ("Grandma's chopsticks lift the dumpling gently by its twisted top knot and set it down on the soup spoon, steam rises.", 4, 0.2, "B"),
 "C17": ("A chopstick tip touches the dumpling skin and opens a tiny hole, a thread of steam curls out and a drop of golden soup glints.", 4, 0.2, "B"),
 "C18": (f"{UNCLE} sips from the spoon with his eyes closed, his shoulders drop and he smiles a small blissful smile in soft warm light. {BOY} in the foreground nods.", 5, 0.15, "B"),
 "C24": (f"Grandma freezes mid-fold, then slowly looks up at the boy's conical hat with wide amazed eyes. {BOY} looks up at her, his eyes widen.", 5, 0.2, "B"),
 "C25": ("Warm sepia dusk. The silhouette of the man seen from behind slowly lowers the spoon over the steaming dumpling, steam rises, lantern light flickers softly.", 5, 0.12, "B"),
 "C26": (f"{UNCLE} waits calmly without moving, then slowly hands the spoon to {BOY}, who takes it with a small smile.", 4, 0.18, "B"),
 "C27": ("Grandma leans in over the counter and points far away to the south with a secret smile. The boy looks where she points, and the fat uncle perks up with hungry eyes.", 4, 0.22, "B"),
 "C28": ("Soft close-up. The boy's eyes come to the camera with a small smile, the ribbon of his hat stirs in the breeze, warm light.", 4, 0.12, "B"),
 "C29": ("The boy stands in front. Behind him the fat uncle with his tongue in a bucket of ice gives a thumbs up, one tiny puff of steam from his ear, and the camel beside him blinks slowly at the camera.", 4, 0.18, "B"),
}
END = {"C14": "C14_end"}


def prep(src, dst):
    im = Image.open(src).convert("RGB")
    im.save(dst, quality=92)


def main():
    grp = sys.argv[1].upper()
    names = sys.argv[2:]
    out = os.path.join(HERE, "inputs", f"ep01v43-clips-{grp}")
    os.makedirs(os.path.join(out, "images"), exist_ok=True)
    clips = []
    seed = 7000
    for cid, (prompt, secs, cn, g) in CLIPS.items():
        seed += 1
        if (g != grp and not (names and cid in names)) or (names and cid not in names):
            continue
        item = {"id": cid, "prompt": prompt, "seconds": secs, "seed": seed, "variants": 1, "cond_noise": cn, "start": {}}
        ends = {}
        for o, suf in (("portrait", ""), ("landscape", "_land")):
            for key, base, store in (("start", cid, item["start"]), ("end", END.get(cid), ends)):
                if not base:
                    continue
                p = os.path.join(FRAMES, base + suf + ".png")
                if not os.path.exists(p) and o == "landscape":
                    continue
                if not os.path.exists(p):
                    sys.exit(f"missing still {p}")
                prep(p, os.path.join(out, "images", base + suf + ".jpg"))
                store[o] = f"images/{base}{suf}.jpg"
        if ends:
            item["end"] = ends
        clips.append(item)
    job = {"defaults": {"backend": "ltx", "width": 480, "height": 832, "seconds": 4, "fps": 24, "fit": "cover", "upscale": [720, 1280],
                        "orientations": ["portrait", "landscape"], "style": STYLE, "negative": NEG}, "clips": clips}
    json.dump(job, open(os.path.join(out, "clips.json"), "w"), indent=1)
    print(len(clips), "clips ->", out)


if __name__ == "__main__":
    main()
