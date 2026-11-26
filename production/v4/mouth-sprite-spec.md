# Mouth sprite spec (fix-plan.md Fix 5a): 6 shapes x 3 characters

Purpose: anime-style mouth flaps on calm talk shots, driven by Rhubarb Lip Sync (MIT) cues and composited on CPU by `tools/episode_maker/mouth_overlay.py` at the point tracked by `tools/episode_maker/mouth_track.py`. Status: pipeline prototype works with procedural sprites (demo `tools/episode_maker/out/mouth-demo.mp4`, git-ignored). Drawn sprites wait for the character redesign; this spec applies to whatever designs are approved.

## Shapes and Rhubarb mapping
| Sprite file | Rhubarb cues | Sound examples | Drawing (front view, mouth only) |
|---|---|---|---|
| `rest.png` (optional) | X (silence), A (M, B, P) | pauses, "m", "b", "p" | Closed mouth. By default NOT pasted: the clip's own drawn mouth stays, so rests always match the animation. Only drawn if a character's clip mouth is unusable. |
| `teeth.png` | B (most consonants, EE), G (F, V) | "s", "t", "k", "ee", "f" | Wide flat lens, slightly open, upper teeth visible as a white band, no tongue. |
| `open.png` | C (EH, AE), H (L) | "eh", "a" in "cat", "l" | Medium "D"-shaped opening: gently curved top lip line, round lower jaw, dark interior, tongue at the bottom. |
| `wide.png` | D (AA) | "ah", shouts | Same family as `open`, about 1.5x taller; for loud syllables. |
| `round.png` | E (AO, ER) | "oh", "or" | Rounded oval, a little narrower than `open`, tongue just visible. |
| `pucker.png` | F (UW, W, OO) | "oo", "w" | Small round "o", lips pushed forward. |

`--energy 0.6` (optional) promotes `teeth` to `open` and `open` to `wide` on the loudest voiced frames, because Rhubarb on our TTS lines gives few D/C cues (measured on the C36 line: B 1.49 s, C 0.21 s, D 0 s of 2.96 s).

## Per-character notes (sizes = sprite width as a share of the character's closed drawn mouth on the clip, `w_frac`)
| Character | teeth | open | wide | round | pucker | Line / colours | Notes |
|---|---|---|---|---|---|---|---|
| Boy (about 7) | 0.62 | 0.52 | 0.60 | 0.42 | 0.30 | thin warm-brown line sampled from the clip; interior dark red-brown; tongue soft pink; teeth cream | Small child mouth, always below the closed-smile line; never wider than the smile. |
| Uncle | 0.70 | 0.60 | 0.70 | 0.46 | 0.32 | same | The mouth sits UNDER the thin mustache: anchor the sprite on the lower lip line, never over the mustache; the mustache stays from the clip (it is above the anchor). The tracker's stroke search can lock onto the mustache: give `--point` below it with `--no-refine` on Uncle talk shots. |
| Grandma | 0.58 | 0.50 | 0.56 | 0.38 | 0.26 | same | Soft small mouth; keep the smile lines of the cheeks from the clip. |

## File format (drawn sprites)
- Folder per character, e.g. `tools/episode_maker/specs/mouths/boy/`: `teeth.png open.png wide.png round.png pucker.png` (+ optional `rest.png`), RGBA, transparent background, line art and fill only (no skin patch: the compositor erases the clip's mouth by inpainting its line pixels on the flat skin first).
- Draw at about 4x the on-screen size (a 50 px clip mouth -> sprites about 200 px wide) so the downscale anti-aliases.
- `sprites.json` next to them: `{"open": {"w_frac": 0.52, "anchor": [x, y]}, ...}`; `anchor` is the pixel on the top lip line, horizontally centred (the point placed on the tracked mouth point).
- Same line weight as the character's line art at final size (about 2 px at 720x1280 for a medium close-up).
- Made from the approved model sheet: one klein "mouth chart" job per character (6 panels, same face, only the mouth changes), then cut, cleaned and keyed by hand or a script. The first try (`charsheets-v45-001`, old designs) showed klein does not keep a 3x2 face grid for mouth charts (it drew full bodies); generate ONE mouth shape per image instead (an edit of the approved front-face close-up: "Same image. Change only the mouth: ..."), then crop.

## Where it may be used (shot rules, fix-plan Fix 2)
Calm talk shots only: speaking face at least about 12% of the frame height (better 25%), facing the camera or 3/4, motion `low`, one speaker. The video prompt for these shots says "mouth gently closed, not talking" (Fix 4) so the clip's own mouth stays still under the flaps. Profiles, fast head turns and shots where the tracker reports `ok: false` get no sprite (V.O. / reaction instead).
