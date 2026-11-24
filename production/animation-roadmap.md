# Animation roadmap: from "moving stills" to a living, kicking story

Creator goal: same drawing, but it must FEEL like a live, fast, gripping story (rhythm inspired by Avatar / Naruto, never copying). Audience: everyone.

## Where we are (v2 of Episode 1)
Done: 57 shots in 2:11, cold-open hook, speed lines, impact frame, whip pans, particles, grain, taiko/flute music, narrator, burned-in captions.
Gap: every shot is still a flat picture with a camera move. Characters never move inside the frame (no breathing, blinking, talking, gestures). That is the difference between "fast slideshow" and "animation". Stills alone cannot close it.

## Plan (4 phases, each ends with a result for the creator to approve)

### Phase 1: Tighten v2 (me, ~1-2 h, after the creator's notes)
- Apply the creator's notes (pace, voices, captions, shots to cut). Target 2:00-2:05.
- Fix the 11 off-reference frames; unify color grade; re-balance music vs voice.
- Result: v2.1 of Episode 1.

### Phase 2: Puppet animation prototype (me, ~half a day) - the real jump
Idea: stop using one flat picture per shot. Build scenes from separate layers so the characters move.
1. Generate **backgrounds without characters** and **character cut-outs** (Boy, Uncle, Grandma) in a few poses each (neutral, talking, shocked, laughing, eating) using Canva `remove-background` / `separate-image-layers` (or generate on plain background, then cut out).
2. Engine: use the existing `layers {bg, fg}` option and add character idle motion: breathing (slow scale), head bob, blink (eye overlay), mouth flap synced to the voice (swap neutral/talking poses while a line plays), squash-and-stretch on hits, entrance slides.
3. Prototype on 8-10 shots of Episode 1 (hook, burn gag, safety beat, hat recognition) = a 20-30 s sample.
- Result: a sample clip. If approved, this becomes the series pipeline: backgrounds and pose library are reusable across all 39 episodes (perfect character consistency, far fewer failed Canva generations).
- Risk: cut-out edges and pose variety. Fallback: keep Phase 1 look.

### Phase 3: Roll the puppet pipeline to full episodes (me)
- Re-make Episode 1 with it, then Episodes 2-3 (China arc). Update skills so every new episode follows the same flow.
- Result: Episode 1 v3 + Episode 2.

### Phase 4: Hero shots with AI video (creator's tools, optional)
- For 6-8 key moments per episode (the burn gag, legend sequence, finale) generate 5-10 s image-to-video clips from our stills and cut them into the timeline.
- Canva `create-video` quota returns on **2026-12-16**; the creator may also use CapCut/other tools. I prepare the stills and prompts, and do the editing.
- Risk: AI video may drift from the characters; used only where it helps.

## What this will and will not be
Will be: limited animation in the spirit of anime (strong poses, smears, impact frames, camera, effects, sound), with moving characters after Phase 2.
Will not be: full frame-by-frame animation like a TV studio. That needs an animation team or heavy AI video.

## Decisions for the creator
1. Approve Phase 2 as the next step (recommended), after notes on v2.
2. Whether to keep the 11 off-reference frames or regenerate them in Phase 2.
3. Whether they want to try an external AI video tool for hero shots (Phase 4) before 2026-12-16.
