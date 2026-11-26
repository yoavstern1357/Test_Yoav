# Shot rules (v4.5+): how every AI clip is designed, prompted and checked

One page. Source: `production/v4/fix-plan.md` Fix 1-4 and 7 (the v4.4 defect census: duplicated characters, melting faces, desync), `production/v4/quality-research.md` rubric, the 1-minute format in `production/v4/PRODUCTION-BIBLE.md`. Enforced by `tools/episode_maker/paper/lint_shotlist.py` (shot list), `tools/episode_maker/qc_stills.py` (stills) and `tools/episode_maker/qc_clips.py` (clips). Reference shot list: `scripts/episode-01-v4.5.md`.

## The rules
1. **At most 2 visible faces per AI clip.** A third character only as hands, a back or a blur, and then **not named and not described with a face** in the prompt ("an old woman's floury hand, only the hand is visible"). Group moments become two clips or a code composite. Dad is never a face (sepia silhouette from behind).
2. **Talk shots are CU or MCU**: the speaking face is at least 25% of the picture height, facing the lens or 3/4. **Wides carry no on-screen dialogue** (use V.O., the Narrator, or an off-screen line over a reaction or a macro).
3. **One speaker per clip.** Banter is shot / reverse shot; overlaps happen in the edit, never inside a clip. A line heard while someone else is on screen is tagged `off` and that visible face keeps its mouth closed (listener acting).
4. **One action per clip, 2-3 s (hard limits 2.0-3.5 s).** A pose change = a START/END pair with the same framing, the same characters in the same places; **END is an edit of START** ("Same framing ...; change only: ..."; stills QC `key_pair >= 0.80`). ECU to wide, appear/disappear, flying off: two clips or a code effect.
5. **No text, cards, signs, badges, titles, logos or edit instructions in AI prompts** (no PEAK, cut, insert, edit:, snap zoom, whip, [CARD, frames). They go to the EDIT column.
6. **Fixed camera in every AI clip.** Push, punch-in, bump, shake, whip, rack focus are done in `make_episode.py` on ones; so are auras, sweat drops, star eyes, speed lines, impact frames, petals, steam bursts.
7. **Risky shot types are not AI clips** (or are marked `HERO` = paid model or code effect): flying/rocketing, levitation, morphs and chibi squash, characters entering or leaving, crowds and caravans, eating with the face covered.
8. **Motion** `low` for every talk shot, `medium` by default, `high` for at most 3 AI clips in a 1-minute episode (5 in an extended cut).
9. **Mouth mode per clip:** `closed` (no on-screen speaker), `overlay` (prompt keeps the mouth closed; sprite flaps from Rhubarb cues by `mouth_overlay.py`), `lipsync` (prompt says "talking naturally"; LatentSync pass on calm frontal close-ups only).
10. **Length (1-minute format):** 20-26 AI clips, total <= 75 s (target about 60-65 s), <= 175 words; last spoken line "Dad was right...", "For dumpling research!" at least once. Lines are cut to fit at natural voice speed, never sped up.

## Order of work (voice-first)
Shot list + lint -> **final voices at natural speed** (no `voice_speed`; cut words if long) -> **word timestamps** (forced alignment, CPU) -> **animatic** from START stills + voices = the edit decision list (each clip's length = line + reaction beat; gag actions placed on the words; creator gate) -> stills (one clean sheet per visible character, head count in the prompt, END as an edit of START) + **stills gate** (`qc_stills.py`, contact sheet) -> **clips at exact length** (animatic length + 0.3 s handle, rounded to the 8-frame step; keyframes at the action times) -> **clip QC gate** (`qc_clips.py --script --spec`; re-roll failed ids with seed + 1, max 2) -> mouths, EDIT effects, captions, mix -> render both orientations at 1:1 speed (no stretch below 0.95x, no trim past the clip end).

## Prompt compiler (shot-list fields -> stills and video prompts)
- Build each prompt from fields, never from script prose: `camera` ("Static camera, fixed framing.") + `who` ("Exactly N people in the picture: the Boy (image 1) and the Uncle (image 2). No other people.", or "No people; only an old woman's hand is visible.") + START (still) or ACTION with facial beats (video) + mouth phrase ("mouth gently closed, not talking" for `closed`/`overlay`, "talking naturally" for `lipsync`) + style ("soft watercolor anime, our own look", palette words repeated verbatim) + negative ("duplicate, twin, clone, extra person, crowd, text, letters, watermark").
- Names exactly as in the stills prompts and the character sheets; only the sheets of the visible faces are passed as references (plus at most one background plate with no people). END still = `@START` + "Same image. Change only: ...".
- Re-run the lint on the compiled prompts: any forbidden or risky word fails the build.

## Checklist (what the lint enforces; FAIL unless marked WARN)
| # | Check | Rule |
|---|---|---|
| 1 | Faces: count present, count = number of names, <= 2, Dad never a face | 1 |
| 2 | Every visible face is named in START; no other character is named in START / END / ACTION | 1 |
| 3 | One speaker per clip (VOICE parsed as `SPEAKER (on/off/V.O.) [note]: “words”`) | 3 |
| 4 | `on` line: shot CU/MCU, face >= 25%, speaker in Faces, mouth overlay/lipsync, motion low | 2, 8, 9 |
| 5 | `off` speaker is not a visible face; no on-screen line -> mouth closed | 3, 9 |
| 6 | END starts with "Same" and contains "only" | 4 |
| 7 | AI clip 2.0-3.5 s; CODE clip 0.5-8 s; Start times continuous | 4 |
| 8 | Forbidden words in START/END/ACTION: PEAK, cut(s), insert, edit:, snap zoom, whip, [CARD, card, badge, title, text, frames, caption, logo, sign, lettering, montage, split-screen, camera moves (zoom, pan, push-in, pull-back, tracking, dolly, orbit, slow motion), code effects (aura, sweat drop, speed lines, impact frame, star eyes, sparkle) | 5, 6 |
| 9 | Risky types on AI rows (rocket, levitate, flying, chibi, morph, enter/exit, crowd, caravan, swallow, gulp, face covered) | 7 |
| 10 | Line fits the clip at natural speed (estimate: Boy 2.4, Grandma 2.3, Uncle 2.0, Narrator 1.9 words/s, +0.35 s per "..."); WARN under 0.3 s spare | 10 |
| 11 | Episode: 20-26 AI clips, total <= 75 s (WARN > 65 s), <= 175 words (WARN < 140), high-motion AI <= 3, last line "Dad was right...", catchphrase present (`--profile extended`: 45-50 clips, <= 180 s) | 8, 10 |
| 12 | WARN: ACTION reads as more than one action | 4 |
| - | Not lintable, human check on the contact sheet: 180-degree rule and eyelines across shot / reverse shot, caption band clear of faces/hands/food, laughs per 15 s | rubric F3, H2 |
