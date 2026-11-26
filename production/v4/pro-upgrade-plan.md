# Pro-level upgrade plan (creator request, 2026-11-26)

Goal: take The Dumpling Boy from "good AI prototype" to the level of a professional animation content creator. Based on a review of Episode 1 v4.4.

## Honest audit of v4.4
1. **Mouths do not match the voices.** Clips are generated silent from keyframes and voices are laid on top; there is no lip-sync.
2. **Character drift.** Faces, outfit details and proportions vary from shot to shot; Grandma varies the most.
3. **Motion quality.** Clips run at 12 fps "on twos" (the RIFE pass is broken), some faces wobble or melt, a few clips carried garbled AI text, and the camera is mostly still.
4. **Voice acting.** Synthetic voices are clean but flat compared with human acting; comic timing depends on performance.
5. **Sound.** Minimal foley, no designed mix; loudness only normalized.
6. **Editing and finish.** No color grade, simple cuts, little camera design, no per-shot review gate before render.
7. **Packaging.** No thumbnails, titles or channel assets built for the new format.

## Upgrade tracks (in priority order)
A. **Character lock (free).** Train a small LoRA per character (Boy, Uncle, Grandma) on Kaggle from the approved art; build model sheets (turnaround + 12 expressions + hands). All new stills use the LoRA, so faces stay identical.
B. **Motion (free, plus optional paid hero shots).** Fix the RIFE bug and deliver 24 fps; use LTX-Video 0.9.8 for most shots; use a stronger model (Veo through the Gemini API with new-account credit, or Wan on a pay-per-use GPU) for 6-8 hero shots per episode (burn, chase, legend). Add an automatic QC gate per clip: stripe scan, face-stability score, text detector, then auto re-roll of failures.
C. **Lip-sync (check licenses first).** Close-up talking shots get an open-source audio-driven lip-sync pass (candidates: MuseTalk, LatentSync, Wav2Lip family; verify commercial license and anime fit). Wider shots are staged so mouths are off-camera or small. A stylized mouth-flap overlay is the fallback.
D. **Voice.** Best result: human voice actors (creator, friends or freelancers) with a direction sheet, then AI only for scratch tracks. Free fallback: expressive open TTS with per-line direction, plus a manual take-picking pass for timing.
E. **Sound design.** CC0 foley library, designed ambiences per location, ducking, stems (dialogue, music, effects), mastered to -14 LUFS; music cue sheet.
F. **Editing and finish.** Locked animatic before any GPU spend; planned camera moves (push-ins, whip pans, impact frames) on top of clips; consistent color grade; transitions only where motivated; 24 fps masters.
G. **Packaging.** Thumbnail template, title formulas, hook cut-downs (40-55 s), channel banner and avatar refresh, pinned comment, playlist structure.
H. **Review gates with the creator.** Gate 1 script + storyboard; gate 2 animatic with final voices; gate 3 final render. Fixes are batched per gate.

## Budget tiers
- **Free:** A, most of B, D fallback, E, F, G, H.
- **About 30-80 USD per episode:** adds Veo hero shots and stronger lip-sync compute.
- **Hire:** voice actors and a sound designer per episode (price per freelancer varies).

## Open decisions for the creator
1. Budget tier.
2. Human voices or best free AI voices.
3. Lip-sync priority (high effort, high visible payoff).
