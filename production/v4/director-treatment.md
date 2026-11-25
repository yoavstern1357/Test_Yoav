# Director's treatment: Episode 1 in motion (V4)

Status: DRAFT for the creator and the team. Written 2026-11-25 by the director. English only, internal, not for publication.
Inputs read: `CLAUDE.md`, `production/v4/BRIEF.md`, `production/v2-direction.md`, `production/animation-roadmap.md`, `production/character-bible.md`, `scripts/episode-01-xiaolongbao.md`, `scripts/episode-01-v2.md`, `tools/episode_maker/specs/episode-01-v3.json` (rejected still-frame version, used only as a structural reference) and `tools/episode_maker/README.md`.

**Dialogue status: TO BE UPDATED.** `scripts/episode-01-v4.md` did not exist when this was written. The breakdown below keeps the v2/v1 story beats and quotes (marked as placeholders) and adds a host layer, a Silk Road legend opening and short asides that the copywriter should replace or approve. The SHOT STRUCTURE (cut rhythm, camera, acting) is the deliverable; the words are scaffolding. When the v4 script lands, re-map lines onto shots 5, 8, 9, 10, 15, 25, 31, 32, 44-47, 50-52, 65, 67 first (these carry the new host and legend copy) and keep every timing within the same shot windows.

**Pipeline status: assumption.** The video engineer is still evaluating free animation routes. This treatment is method-agnostic: each shot carries a method code, so the plan survives whichever route is chosen.

| Code | Method | Meaning |
|---|---|---|
| R | Rig | Character is assembled from separate parts (head, eyes, mouth, arms, legs, hat) from approved art and animated: cycles, poses, swaps, squash. |
| K | Keyframes | Two or three drawn key images with interpolation or AI in-betweening; held poses with moving secondary elements. |
| C | Camera | Static plates and sprites, animated by camera move, parallax, particles and masks. |
| H | Hero | Needs fluid full animation; first choice is hand-keyed frames or a free open model; fallback is an AI image-to-video clip. See section 4. |
| G | Graphic | Built in the editor/engine (cards, stamps, route line, text badges). |

Result for this episode: **67 shots, 2:00.0 total, average 1.79 s per shot** (39 R, 10 K, 8 C, 5 H, 5 G).

---

## 1. Visual language bible

### 1.1 Five rules for everything in this series
1. **Something moves in every frame, and it is not only the camera.** A held pose is allowed only if steam, hat ribbon, mustache, a blink, a drifting particle or a parallax layer moves.
2. **Hold, then hit.** Fast comes from contrast: a calm 0.6 s hold makes a 0.2 s smash feel violent. Never keep everything at the same speed.
3. **One idea per shot.** If a shot needs two ideas, cut it in two.
4. **The camera finds the reaction.** In a gag, the cut to the face is the joke; show the cause for as short as possible and the reaction for as long as it lands.
5. **Readable on a phone in a second.** Silhouettes first (round Boy with hat cone, big round Uncle), faces large, one focal point per frame.

### 1.2 Vertical frame (1080x1920, mobile delivery 720x1280)
- **Safe zones.** Keep the top 7% clear (platform UI), captions live in the bottom 22% (the approved caption position is `caption_y` about 0.8; do not change the caption look). Faces and key props sit in the middle third, slightly above center. Never put a face under the caption band.
- **Vertical composition beats horizontal habits.** Use depth and height: stack the two characters (Uncle big in the back or foreground, Boy small and lower), use tall subjects (pagodas, steamer towers, steam columns), let steam and lanterns carry the eye up. Side-by-side two-shots only in close or medium-wide.
- **Horizontal motion needs wide plates.** Pans, tracking and whips need a plate at least 2x frame width (marked "wide pan plate" in the asset list). Vertical tilts work on a normal tall plate.
- **Uncle fills the frame, Boy owns the space around him.** Uncle at medium size already takes two thirds of the width, so cut to singles often and use the stacked two-shot for interaction.

### 1.3 Shot sizes (vertical framing) and typical lengths
| Size | Framing in 9:16 | Use | Typical length |
|---|---|---|---|
| ECU | Eyes, mouth, hands, food, a single prop fills the frame | Gag triggers, food macro, step badges, torn page | 0.5-1.6 s |
| CU | Head and shoulders | Reactions, whispered lines, tender lines | 1.2-3.0 s |
| MCU | Head to chest | Host to camera, dialogue, deadpan asides | 1.8-3.0 s |
| MS | Waist up, one or two characters stacked | Interaction, gestures, takes | 1.4-2.6 s |
| MLS | Knees up | Walking, flying, tracking | 1.6-2.4 s |
| WS | Full body with set | Entrances, comic physics, whole-body takes (ear steam) | 1.4-2.2 s |
| ELS | Tiny figures in a big world | Establishing, caravan, skyline, bridge at night | 1.4-3.0 s |
| LA / HA | Low or high angle | Hero poses (LA), shrinking Uncle (HA), the clock | 0.8-2.0 s |

### 1.4 Lens feel (virtual lenses, built in 2D)
- **Wide (exaggerated) feel:** low angle, characters scaled up near the lens and shrunk behind, dutch tilt 8-10 degrees. Use for gags and hero poses (shots 4, 26, 30, 40).
- **Normal feel:** eye level, no distortion. Host-to-camera and dialogue.
- **Long lens feel:** flat, compressed, strongly blurred background layers (blur the bg plate 4-8 px, keep subject sharp). Use for macro food and tender close-ups.
- **Rack focus** = cross-fade a blurred copy of the bg layer in, or blur the fg layer out. Use it for the cold-open reveal (shot 5) and heart moment.

### 1.5 Camera behaviors (how each is built in 2D)
| Behavior | Build | Use |
|---|---|---|
| Pan / track | Scroll a wide plate with 3 layers at different speeds (parallax) | Walks, alley tow, caravan |
| Tilt | Move a tall plate vertically | Pagodas, steam rising, hero rise |
| Push-in / pull-out | Scale around a focus point, ease in-out | Emotion, reveals |
| Crash zoom | 1.0 to 1.3 in 4 frames, ease out, optional 1 frame blur | Shouts, "Wait!", the grab |
| Whip pan | Fast slide with horizontal motion blur, cut hidden inside | Scene changes, rewind |
| Dutch | Rotate 6-10 degrees | Danger and gag moments only |
| Handheld | 2-6 px noise, 1-2 px at rest | Chaos beats |
| Shake | 8-14 px decaying over 0.3 s | Impacts, tower wobble |
| Hit-stop | Freeze everything 0.12 s on the contact frame | Every real impact |
| Circle match cut | Lid, clock, plate, moon share a circle; morph between | Lesson, transitions |
| Orbit feel | 3-layer parallax while a character turns its head | Beauty beats |

### 1.6 Hold versus cut, and target shot lengths
- **Cut** when the information is delivered, when the eye has landed on the new thing, or when the next beat is a reaction. **Hold** for deadpan, for the quiet heart moment, and while a line is spoken (cut on the last syllable, not after).
- Cut on action: start the next shot already in motion; trim the first and last 2-3 frames of every shot.
- Dialogue shots hold at least 0.4 s of reaction after the last word, except in the cold open.
- Speech rate stays at or under about 3 words per second; with more lines than v3, split them across shots (shot, reply shot, reaction shot) rather than speeding up.

| Beat type | Target shot length | Notes |
|---|---|---|
| Cold open | 0.5-1.4 s | Shorter than a heartbeat, escalating |
| Montage | 1.0-2.0 s | Beat-synced cuts, always a new direction of motion |
| Gag setup | 1.4-2.0 s | Clear, simple, slightly slow so the viewer understands |
| Gag trigger and impact | 0.4-1.0 s | Short, silent or very loud |
| Reaction / deadpan | 1.8-2.2 s | The hold is the joke |
| Lesson inserts | 1.0-1.8 s | One per word, taiko-synced |
| Host to camera | 2.4-3.2 s | Held and framed; the host is the anchor |
| Legend scroll | 2.0-3.4 s | Calmer, but the scroll is always sliding |
| Dad / heart | 2.0-3.0 s | Longest allowed; nothing over 3.4 s anywhere |
| Cliffhanger | 1.0-2.8 s | Accelerates, then holds on the hook line |

This episode: average 1.79 s; fast segments (cold open, montage, gag, lesson) average 1.46 s; quiet segments (Dad, heart, fact, legend) average 2.35 s. A curiosity gap is opened about every 15 s (see the beat list in section 2).

### 1.7 Cutting patterns that give the Avatar/Naruto-style kick (rhythm only, nothing copied)
- **The three-beat insert run:** three ECUs on three consecutive words (Lift / Spoon / Tiny hole), each with a taiko hit and a number badge. Rhythm does the teaching.
- **Smash cut from silence:** drop the music for 0.3 s before an impact (shots 27-29) and cut from a quiet close-up to a loud wide.
- **Reaction ladder:** a gag escalates through three reactions of increasing size (eyes, cheeks, ears), each shorter than the last.
- **Match cuts on circles and shapes:** steamer lid to clock to lantern to hat.
- **Aside to camera:** after a gag the Boy glances to the lens (2.0 s hold). This is the show-host voice and the main laugh engine.
- **Whip transitions** only between scenes, never within a conversation.
- **Cutaway button:** a 1 s side gag (cyclist double-take) after a big move, then back.

### 1.8 Acting rules
**General (applies to every character)**
- Every gesture has **anticipation (4-6 frames) - action (2-4 frames) - overshoot (2 frames) - settle (4-6 frames)**. Round characters allow strong squash and stretch: 15-25% on hits, 35% only on gags.
- **Key poses first**: each shot is built from 2-3 strong poses with clear silhouettes; in-betweens are minimal and on twos (12 drawings per second) while camera and FX run smoother.
- **Follow-through and overlap**: hat ribbon, mustache, belt tails, bag strap and soft belly lag 2-4 frames behind the body.
- **Eye-lines**: characters look at what matters; looks to the lens only for host lines and asides.
- **Blinks** every 2.5-4 s in held shots, never on a beat; a hold longer than 1.5 s must have a blink, a breath or an eyebrow move.
- **Breathing** 2-frame loop, 0.5 Hz, only when the character is in a hold.
- **Lip sync**: 4 mouth shapes (closed, small open, wide open, O), changed on twos, with the drawn mouth hitting a wide shape on stressed syllables. Close the mouth 2 frames before the cut.

**The Boy (host)**
- Calm and precise. Small gestures: one arm sweep, one pointed finger, one raised eyebrow. His comedy is stillness: a 1.5-2.0 s deadpan hold beats any wild reaction.
- Walk: even, 8 frames, hat ribbon trailing. Presenting: weight on one foot, palm open, a tiny head tilt.
- Eyes closed smile is reserved for Dad moments only, so it always means something.

**Uncle (chaos co-host)**
- Everything is bigger than the Boy's, with telegraphed anticipation: before any dash, lunge or grab he coils (crouch or lean back) for 4-6 frames so the audience sees it coming.
- **Nose-led.** His body follows his nose and belly; the belly drags 2 frames late; chopsticks are always in his hand or pocketed in his belt.
- Waddle walk 8 frames, left-right sway, belly bounce late. Signature pose: chopsticks aloft, one leg back.
- Reactions climb in size: eyes dots (small) to cheeks puffed (medium) to ear steam (huge).

**Grandma**
- Tiny, still and precise. Her hands do everything: fast folding cycle on ones, then a dead stop. Her cliffhanger stare is the only time she looks at the lens.

**Dad (memory)**
- Never moves except cloth and ribbon in the breeze; a slow push-in on a locked silhouette, no face, no turn.

### 1.9 Limited-animation toolkit (cheap and good-looking)
| Trick | How | Where |
|---|---|---|
| Held pose + moving secondary | Hold a pose, animate steam, ribbon, sweat, hat, blink | All reaction shots |
| Pose-to-pose on twos or threes | Characters at 12 or 8 fps over a smooth 24 fps camera | Everywhere; this is what makes it feel like anime |
| Cycles | Walk (8f), run (6f), air-pedal (4f), steam (4-6f), water ripple (4f), lantern flicker (3f), caravan (4f), folding hands (4f) | Montage, legend, heart |
| Parallax layers | 3 layers moving at 1x / 1.6x / 2.5x | Tracking shots, canal, alley |
| Smear frames | 1-2 frames of a stretched, blurred shape between poses | Grab, dash, hand blur |
| Impact frame | 2 frames inverted (black/white) then radial burst, shake, silence | Shots 3, 29, stamp |
| Speed lines | Radial or horizontal, flicker on ones | Zooms, dashes, floats |
| Reuse and reverse | Play a clip backwards at 3x as the rewind (shot 6 reuses shot 4) | Rewinds, recaps |
| Mask reveals | Handwriting and route lines drawn by mask | Journal, map, ink strokes |
| Color holds | Flash to white or tint a face red instead of redrawing | Burn gag |
| Limited-palette swaps | Scroll look is a filter of the same assets | Legend |
| Push-ins on static art | Scale up with eased blur-free zoom | Food macros, torn page |

### 1.10 The three registers (and their cousins)
| | Host to camera | Gag | Ancient legend (scroll) | Dad / heart |
|---|---|---|---|---|
| Look | Clean, bright, full color, location plates, bright rim light | Same, with exaggerated perspective, squash, smears, speed lines | Rice-paper scroll, paper-cut figures, ink outlines, 2-3 flat colors, paper grain, red seal, wooden roller edges | Sepia (Dad) or night indigo with lantern orange (bridge) |
| Frame rate feel | Characters on twos, camera smooth | Characters on ones for hits, on twos otherwise; hit-stop | Stepped: everything on fours (about 8 fps), nothing smooth | Slow, almost still, 24 fps with soft drift |
| Camera | Steady, slow push-in, parallax drift, lower-third placement | Crash zooms, dutch, shake, whips | Flat side-scroll of the scroll, slow pan, no perspective, no rotation | Locked or very slow push-in |
| Characters | Rig with full expression set, direct address | Rig with extreme poses and impact frames | Existing designs through a paper/ink filter; legend cast drawn as paper-cut figures | Silhouettes, close faces, minimal motion |
| Text | Lower-third place card, step badges, fact cards (paper-cut) | Sound-effect words only if tiny | Brush text only: "Legend says...", red seal card | One fragile handwriting insert |
| Music | Light adventure, marimba and plucked strings, 120 BPM | Taiko stabs and silence; tension then release | Guzheng-style plucks, low drone, wind, no drums | One sustained string, then a single koto |
| Transition in/out | Passport stamp, steam wipe, whip | Smash cut, impact frame | Ink bleed in, paper rip out | Slow dissolve in, soft match-cut out |

### 1.11 Color and light per mood
Use the series palette as the base (leaf yellow `#ECC66A`, cream `#FFFAF0`, orange `#D9480F`, peach `#FFE3B8`, brown `#3B2A1A`).
| Mood | Light | Grade | Notes |
|---|---|---|---|
| Hook / tension | Hot orange side light from the steamer, dark vignette | Warm, contrast up | Face tint shifts peach to red; steam is cream white |
| Host, arrival (golden hour) | Low warm sun, long rim lights, soft rays | Warm | Teal-blue only in shadow areas (skyline, river) |
| Montage (day-to-dusk) | Slightly cooler daylight at the metro, warming through canal | Cool to warm | Color temperature itself says "we have arrived" |
| Gag build | Bright, flat, friendly | None | The silence and the impact frame do the work |
| Burn impact | High-contrast white/black inversion, then red face | Contrast up | Two frames only |
| Lesson | Window daylight, soft, steam backlit | Warm | Food is the brightest, warmest thing |
| Legend | Cream paper, ink brown, orange accents, gold jelly | Paper filter | No cool tones |
| Dad memory | Backlit golden, haze, dust | Sepia | Faceless silhouette |
| Heart (bridge) | Deep indigo night, orange lantern pools, water glints | Cool with warm accents | The only night scene; keep it small and calm |
| Cliffhanger | Return to warm, add a violet-to-teal sky hint | Warm | Last shot is the brightest |

### 1.12 Transitions catalog
| Name | How | Use |
|---|---|---|
| Steam wipe | Steam sprite sweeps across the lens, cut inside it | Between stall scenes |
| Whip | 0.15 s horizontal slide with blur | Scene changes |
| Ink bleed | Journal page ink spreads and becomes the scroll | Into the legend |
| Paper rip | Uncle's finger tears the scroll, color floods in | Out of the legend |
| Passport stamp | Stamp slams, flash, cut on impact | Title |
| Circle match cut | Lid, clock, lantern, plate, hat | Lesson, heart |
| Rewind | Reverse a clip at 3x with tape sound | Cold open to story |
| Smash cut | Hard cut from quiet to loud, with music cut 0.3 s earlier | Gags |

### 1.13 Sound design cues (sync rules)
- **Pre-hit whoosh, hit, tail**: every cut with camera motion has a whoosh starting 4 frames before the cut; every impact has a hit on the first frame, then a tail.
- **Silence is a sound.** Music cuts 0.3 s before shot 3 and shot 29 and returns after the toot. Tick-tock is the only sound before the burn.
- **Taiko on poses**: each step badge (Lift, Spoon, Tiny hole, Wait) and each hero pose lands on a drum hit.
- **Ear steam = train whistle**, pitch rises with the steam; the same whistle sounds in shots 4 and 30 (callback).
- **Foley that tells the story:** steamer lids, chopstick clicks, tummy growl, bike bell, slap of the journal. Every cycle (walk, pedal, folding hands) gets a matching loop.
- **Voices** stay on `narrator`, `boy`, `uncle`, `grandma` as in `episode_maker`; Boy's host lines are close-miked and slightly brighter; legend V.O. has plate reverb and slows 5%.
- **Music palette** (existing moods): `tension` for the cold open, `adventure` for host and montage, `sparse` for waiting, `tender` for sip, Dad and heart, `epic` for stamp and finale; the legend gets guzheng-style plucks and a low drone (new mood proposal for the engineer: `scroll`).
- Cuts are beat-snapped (`snap_to_beat`), but gag beats may sit 1-2 frames off the grid on purpose when a hit needs to land earlier.

### 1.14 Comedy staging (visual only; copy is the copywriter's)
- **Straight man and chaos:** the Boy is calm, the Uncle is chaos; the funny face is the Boy's, not Uncle's. Always cut to the Boy after the chaos.
- **Running gags (use visually, one per segment):** Uncle's feet leaving the ground (nose-led); steamers rattling; Boy's deadpan aside to the lens; Uncle's chopsticks always ready; the clock; the cricket after a silence.
- **Rule of three:** the three-beat insert run (Lift, Spoon, Tiny hole); Uncle's three escalating reactions.
- **Callback:** "For science!" is shouted at the burn, whispered at the sip; the ear-whistle returns; the fan returns with the journal.
- **Misdirection:** the cold open looks like an explosion of rage but turns out to be a hot dumpling.
- **Jokes are only on Uncle**, never on any place or people. The cyclist and Grandma are never the butt of a joke.

### 1.15 The two atmospheres together: travel show host and Silk Road
- **Host layer:** the Boy talks to the lens on location (skyline, pagodas, canal) in lower-third framing, uses a passport-stamp bumper, number badges and fact cards, and Uncle photobombs the frame edge. Occasionally the "camera" is jostled by Uncle (a 2-frame bump), implying a camera operator.
- **Silk Road layer:** the legend is a scroll that begins on the dunes with a caravan (the old road), then pans to the 1871 town; the map has a route line like a trade route; Dad's journal is the family treasure map. The look is paper, ink and brass, but the characters stay the approved round, soft drawings.
- **Never copy:** no elemental-bending style poses, no hand-seal gestures, no recognizable title cards, music or compositions. We borrow only: fast contrast between holds and bursts, short episodes with cliffhangers, comic reaction timing.

---

## 2. Animation breakdown: Episode 1 (67 shots, 2:00.0)

Notes on reading the tables:
- `Time` is the cumulative start. The render may stretch a shot slightly to fit voice (as the engine does), but the shot windows below are the budget.
- Plates are EMPTY backgrounds (no characters); characters, props and FX are composited on top (IDs from section 3).
- Dialogue in quotation marks is placeholder from the v2 script or a new proposal; replace with `scripts/episode-01-v4.md`.
- Shot 21 (cyclist) is optional and is the first to drop if time runs over.

### Segment overview
| Segment | Shots | Start | Length | Intent |
|---|---|---|---|---|
| A. Cold open and rewind | 1-6 | 0:00.0 | 6.5 s | Hook in 3 s. Pay off at shot 29 (impact) and shot 30. |
| B. Host intro: journal, map, welcome, title | 7-11 | 0:06.5 | 11.0 s | The Boy becomes the show host; passport stamp is the show bumper. |
| C. Arrival montage: Nanxiang, the nose, the steam ribbon | 12-22 | 0:17.5 | 18.4 s | Travel-show montage with host asides; Uncle is dragged by his nose. |
| D. The burn gag | 23-32 | 0:35.9 | 14.5 s | Setup, trigger, silence, impact, toot, deadpan aside. |
| E. The right way (host lesson) | 33-42 | 0:50.4 | 16.4 s | Four badges: Lift, Spoon, Tiny hole, Wait. The wait is the second gag. |
| F. Legend scroll: ink and paper | 43-49 | 1:06.8 | 15.4 s | Different look: stepped, paper, ink. Uncle rips it open to exit. |
| G. Fun fact and Dad's wisdom | 50-54 | 1:22.2 | 12.2 s | Card, joke, then sepia memory. |
| H. Heart moment: the bridge | 55-58 | 1:34.4 | 10.0 s | Quiet, 10 s: the longest calm stretch of the episode. |
| I. Button and cliffhanger | 59-67 | 1:44.4 | 15.6 s | Snap back to speed; Grandma stares at the hat. |

### Curiosity gaps (about every 15 s)
1. 0:00 Why is Uncle about to explode? Answered by the impact at shot 29 (0:44).
2. 0:10 What was on the torn last page of Dad's journal? (series thread, left open)
3. 0:28 Whose steam ribbon is dragging Uncle by the nose? (answer: the stall, shot 22)
4. 0:41 "There's soup inside!" Uncle: "For science!" Silence. What happens? (shots 27-29)
5. 1:01 The tower wobbles: will Uncle make it through the wait? (the sip, shots 40-42)
6. 1:07 Legend says... where did the soup dumpling really come from? (scroll, shots 43-49)
7. 1:46 Why does Grandma stare at the hat? Where did Dad go? (cliffhanger)

### A. Cold open and rewind

| # | Time | Dur | Type / method | Shot size and camera | Plate | Exact action and line | Assets | FX | Sound |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0:00.0 | 1.0 | COLD / K | ECU, crash-push 1.0 to 1.25 in 4 frames, slight dutch | BG-01 | Uncle's huge eyes fill the frame, pupils quiver. A wall of steam rolls L->R across the lens twice (fg layer, 0.3 s each). | BG-01, UN-03, UN-05, FX-01 | steam fg x2, vignette pulse | riser starts, steam hiss; no music, no voice |
| 2 | 0:01.0 | 0.8 | COLD / K | ECU, tilt down to cheeks | BG-01 | Cheeks swell (squash-up 100% to 115%), face tint peach to red over 0.5 s, mustache vibrates (2-frame jitter on ones), sweat drop pops on the temple. | BG-01, UN-03, UN-04, UN-02, FX-04 | red tint ramp, jitter | pressure whine rising, tick tick |
| 3 | 0:01.8 | 0.5 | COLD / K | IMPACT FRAME: 2 inverted frames (white face, black bg) then 6-frame radial burst | BG-01 | Uncle's silhouette bursts out of the frame; hard hit-stop. | UN-03, FX-06 | inverted flash, radial burst, camera shake 8 px | music cut to silence, crack + gong, then 0.2 s hush |
| 4 | 0:02.3 | 1.4 | COLD / H | WS, dutch 8 deg, handheld shake | BG-01 | Uncle stands rigid (arms stiff, face red). Whistle plumes shoot from both ears, 2 loops of 4 frames on twos; steamer lids rattle and pop up one by one. | BG-01, UN-12, FX-03, PR-01, FX-01 | ear jets, lid pops, shake | TOOOOT train whistle (rising), lid rattle |
| 5 | 0:03.7 | 2.0 | HOST / R | MCU, static, 4-frame slow push; Uncle blurred behind (rack-focus feel) | BG-01 | Boy in foreground, unbothered. He turns his head slowly to the lens (hold 0.5 s), one blink, says the rewind line. Steaming Uncle stays blurred behind him. | BG-01, BO-10, BO-03, BO-04, UN-12 | focus blur on bg layer | whistle fades; Boy: [v2: "Six hours earlier." or new aside]; tape-rewind whirr starts |
| 6 | 0:05.7 | 0.8 | COLD / C | Whip L->R into next shot | BG-01 | Rewind: shot 4 played in reverse at 3x speed, steam sucked back into the steamer, motion-blur whip out. | (reuse shot 4 clip) | reverse, whip blur | reverse whoosh, tape rewind |

### B. Host intro: journal, map, welcome, title

| # | Time | Dur | Type / method | Shot size and camera | Plate | Exact action and line | Assets | FX | Sound |
|---|---|---|---|---|---|---|---|---|---|
| 7 | 0:06.5 | 1.4 | HOST / R | Top-down, locked, 2-frame settle | BG-02 | Boy's two hands slap the closed journal onto the table, cover flips open in 3 smear frames, dust puff, pages riffle. | BG-02, PR-06, BO-05, FX-08 | dust puff, page riffle | slap, riffle; bright marimba bumper starts |
| 8 | 0:07.9 | 2.6 | HOST / G | Top-down map, slow tilt + 6% zoom | BG-17 | Route line draws from home to Shanghai (1.2 s, engine path); paper train rides the line, puffing. Voice: "Dad's dumpling journal. Every page, one dumpling." | BG-17, PR-08, FX-01, BO-05 | line draw, puffs, sparkle at arrival | chug cycle, sparkle on arrival; Boy V.O. |
| 9 | 0:10.5 | 1.6 | HOST / C | ECU macro, push-in | BG-02 | Boy's finger runs along the ragged torn-out edge of the last page. Hold. Dust motes drift. Line: "The last page? Torn out." | BG-02, PR-06, BO-05 | dust motes, rays | riser, paper crinkle; Boy V.O. |
| 10 | 0:12.1 | 3.2 | HOST / R | MS, slow push + 3-layer parallax (railing faster) | BG-03 | Boy stands lower-right with Shanghai skyline behind. He looks up at the towers (awe), turns to the lens, presents with a sweep of his arm: host welcome line (placeholder: "This is Shanghai: tall, loud, and very hungry."). A boat glides across the river. | BG-03, BO-16, BO-07, BO-03, BO-04, PR-16 | rays, boat glide, light flare on glass | boat horn, city hum under bumper music; Boy: host welcome line |
| 11 | 0:15.3 | 2.2 | HOST / G | Low angle hero, tilt up + settle | BG-19 | Boy and Uncle stand shoulder to shoulder (Uncle larger, Boy smaller, stacked). Uncle waves chopsticks. Passport stamp slams down with the show title and episode tag (text in editor). | BG-19, BO-14, UN-07, PR-09 | stamp slam + impact ring, dust, punch-in 1.1 | taiko + gong; "show bumper" sting |

### C. Arrival montage: Nanxiang, the nose, the steam ribbon

| # | Time | Dur | Type / method | Shot size and camera | Plate | Exact action and line | Assets | FX | Sound |
|---|---|---|---|---|---|---|---|---|---|
| 12 | 0:17.5 | 1.2 | MON / C | Static plate, whip in; horizontal speed lines | BG-04 | Metro train rips L->R across the platform (cycle), windows flicker. Sign text NANXIANG - Line 11 appears (editor text). | BG-04, PR-10 | speedlines horizontal, whip | metro rush-by, ding-dong chime |
| 13 | 0:18.7 | 2.0 | MON / R | WS, slow dolly forward (3-layer parallax) | BG-05 | Canal street at golden hour. Boy and Uncle walk away from camera along the canal (small figures, 8-frame walk and waddle cycles, Uncle's belly bounces 2 frames late). A cyclist crosses in the foreground. | BG-05, BO-18, UN-22, PR-11, PR-12 | rays, petals drift | bike bell, canal water, footsteps; narrator/Boy: "Old Nanxiang." |
| 14 | 0:20.7 | 1.4 | MON / C | ELS, tilt up the pagodas | BG-06 | Camera tilts up the twin brick pagodas, birds lift off, clouds slide. Hold on the top. | BG-06, FX-11 | rays, birds, grade warm | temple-bell hum, wind |
| 15 | 0:22.1 | 2.6 | HOST / R | MCU walking-and-talking, tracking L->R, 2-layer plate scroll | BG-05 | Boy walks toward the lens, talking: placeholder "Two brick pagodas. Very old. Very photogenic." Behind him Uncle drifts into frame sniffing, out of focus. | BG-05, BO-06, BO-02, BO-03, BO-04, UN-07 | focus blur bg, rays | footsteps, stall hum; Boy host line |
| 16 | 0:24.7 | 1.0 | MON / R | ECU nose, push-in | BG-05 | Uncle's nose twitches twice, nostrils flare (squash), eyes slide shut. | UN-02, UN-03, UN-04 | none | two sniffs, rising pluck |
| 17 | 0:25.7 | 2.0 | MON / R | MS, slight low angle | BG-05 | Uncle drops into an anticipation crouch (4 frames), rises on tiptoe (8 frames), eyes closed, nose to sky. Line: "I smell... destiny." | BG-05, UN-08, UN-21, UN-03 | shine glint on nose | sniff, tiptoe creak; Uncle line |
| 18 | 0:27.7 | 1.2 | MON / C | Ground-level tracking down the alley | BG-07 | A steam ribbon snakes from the far stall down the alley toward camera, curling around a lantern, then points like an arrow. | BG-07, FX-02, PR-12 | ribbon loop, parallax | hiss, magic curl |
| 19 | 0:28.9 | 2.4 | GAG / H | MLS tracking L->R, 3-layer parallax, speed lines | BG-07 | Ribbon hooks Uncle's nose. Feet leave the ground (8-frame anticipation then lift), legs pedal in the air (4-frame cycle), belly trails by 2 frames, arms flail; he is towed past stalls. Dust puff where his sandals lifted. | BG-07, UN-09, UN-23, UN-21, FX-02, FX-08 | speedlines horizontal, dust | slide-whistle rise, "wheee", air-pedal pitter |
| 20 | 0:31.3 | 1.6 | GAG / R | MS tracking, low and quick | BG-07 | Boy trots alongside, hat ribbon trailing (follow-through), points down at Uncle's feet, deadpan: "Uncle. Feet. Ground." | BG-07, BO-18, BO-05, BO-03 | none | footsteps; Boy line |
| 21 | 0:32.9 | 1.2 | GAG / K | Cutaway MS | BG-05 | Uncle floats past a cyclist. Cyclist does a double-take (2 frames), wobbles, rings the bell. [Optional shot: first to drop if over time.] | BG-05, PR-11, UN-09 | none | bike bell x2, boing |
| 22 | 0:34.1 | 1.8 | GAG / R | WS, locked, shake on landing | BG-08 | Ribbon snaps; Uncle drops and lands with a belly squash (UN-10), dust ring, steamer lids hop. Boy slides in and stops, hat tips. | BG-08, UN-10, BO-06, FX-08, PR-02, BO-19 | dust ring, shake | thud, steamer rattle, ribbon snap |

### D. The burn gag

| # | Time | Dur | Type / method | Shot size and camera | Plate | Exact action and line | Assets | FX | Sound |
|---|---|---|---|---|---|---|---|---|---|
| 23 | 0:35.9 | 1.6 | GAG / K | ECU, slow push | BG-08 | Basket lid lifts and floats away on the steam, steam billows past the lens, golden dumplings glisten. | BG-08, PR-01, PR-03, FX-01 | rays, steam fg | lid slide, hiss, sparkle |
| 24 | 0:37.5 | 1.6 | GAG / R | ECU chopsticks, handheld | BG-08 | Uncle's hand trembles; chopsticks pinch a dumpling, it jiggles (2-frame squash), soup wobbles visibly inside. | BG-08, PR-05, PR-03, UN-06 | none | chopstick clack, soft squish |
| 25 | 0:39.1 | 1.8 | GAG / R | MCU, crash zoom 1.0 to 1.3 in 4 frames | BG-08 | Boy lunges (anticipation, then stretch), hat pops up, mouth wide: "Wait! There's soup inside!" | BG-08, BO-15, BO-03, BO-04, PR-14 | crash zoom, speedlines | taiko hit; Boy line |
| 26 | 0:40.9 | 1.0 | GAG / R | Low angle, dutch 10 deg, hold | BG-08 | Uncle strikes the hero pose, chopsticks aloft, one leg back, huge grin: "For science!" | BG-08, UN-11, UN-03 | speedlines radial | taiko + sting; Uncle line, then music out |
| 27 | 0:41.9 | 0.8 | GAG / R | ECU on mouth | BG-08 | Dumpling disappears (1-frame smear), cheeks puff to a ball, ears rise. | UN-04, UN-02, PR-03 | none | pop, gulp |
| 28 | 0:42.7 | 1.2 | GAG / K | ECU eyes, locked | BG-08 | Pupils shrink to dots, one eye twitches, sweat beads. Complete silence except a clock tick. | UN-05, UN-03, FX-04 | none | tick, tick; silence |
| 29 | 0:43.9 | 0.5 | GAG / K | IMPACT FRAME (reuse language of shot 3) | BG-08 | Inverted flash, hit-stop, burst. Payoff of the cold open. | UN-03, FX-06 | inverted flash, burst, shake | crack, gong |
| 30 | 0:44.4 | 2.0 | GAG / H | WS, dutch 8 deg, handheld | BG-08 | Uncle rigid and red, whistle plumes from both ears, hops in place twice, flaps hands. Boy in foreground corner calmly plugs his ears with fingers. | BG-08, UN-12, UN-24, FX-03, BO-06, BO-05 | ear jets, shake | TOOOT x2; trains-whistle |
| 31 | 0:46.4 | 2.0 | GAG / R | CU, soft push | BG-08 | Uncle shrinks (squash to 90%), tongue out and fanning with one hand, tiny voice: "...there's soup inside." | UN-13, UN-03, UN-04, UN-06, FX-10 | none | tiny squeak voice |
| 32 | 0:48.4 | 2.0 | GAG / R | MS, locked, deadpan hold | BG-08 | Boy to lens: slow blink, one eyebrow up: "Every. Single. Time." Behind him Uncle keeps fanning his tongue with the journal. | BG-08, BO-10, BO-03, UN-19 | none | single cricket chirp; Boy line |

### E. The right way (host lesson)

| # | Time | Dur | Type / method | Shot size and camera | Plate | Exact action and line | Assets | FX | Sound |
|---|---|---|---|---|---|---|---|---|---|
| 33 | 0:50.4 | 2.2 | LESSON / R | MS two-shot, slow push | BG-09 | Boy pulls a stool, Uncle plops on it (squash, stool creaks). A tower of steamers on the table. Boy: "Let me show you." | BG-09, BO-06, UN-14, PR-02, PR-15 | dust puff, rays | stool creak, clink; Boy line; adventure music back in |
| 34 | 0:52.6 | 1.2 | LESSON / R | ECU hands | BG-09 | Chopsticks lift a dumpling onto a spoon. Step badge 1 LIFT stamps on screen. | BG-09, PR-03, PR-04, PR-05, BO-05 | badge stamp | taiko on the word "Lift" |
| 35 | 0:53.8 | 1.0 | LESSON / K | ECU spoon | BG-09 | Dumpling settles on the spoon and jiggles. Badge 2 SPOON. | PR-03, PR-04 | badge stamp | taiko |
| 36 | 0:54.8 | 1.6 | LESSON / H | ECU macro, locked | BG-09 | Chopstick tip pokes a tiny hole; golden soup trickles, steam curls up. Badge 3 TINY HOLE. | PR-03, PR-04, FX-01 | steam, glow | pop, soft sizzle, taiko |
| 37 | 0:56.4 | 1.4 | LESSON / R | MS | BG-09 | Boy raises one finger, calm. Badge 4 WAIT. Uncle vibrates beside him, barely holding still. | BG-09, BO-05, BO-11, UN-15 | badge stamp | tick, taiko |
| 38 | 0:57.8 | 1.8 | LESSON / R | ECU eyes + spoon | BG-09 | Sweat drops roll down Uncle's forehead, steam on his lashes, he whispers to the dumpling: "Be cool. Be cool." | BG-09, UN-03, UN-05, FX-04, PR-04 | sweat drops, steam | tick-tock; whisper line |
| 39 | 0:59.6 | 1.4 | LESSON / C | Circle match cut: steamer lid to clock face | BG-09 | Steamer lid circle morphs into a big cartoon clock; hands tick forward 3 times, then crawl. | PR-01, PR-07 | circle morph | tick tock, tick tock |
| 40 | 1:01.0 | 2.2 | LESSON / R | LA, locked; tower in foreground | BG-09 | Uncle's tummy growls: belly shakes (secondary motion), tower of steamers wobbles, tiers slide. Boy calmly steadies the top with one finger. | BG-09, UN-16, PR-02, BO-12 | shake, tier slide | GRRROWL, rattle, finger tink |
| 41 | 1:03.2 | 1.4 | LESSON / R | CU, push in | BG-09 | Uncle sips: lips purse, eyes close, whisper callback: "For science." | UN-03, UN-04, PR-04 | steam | sip, soft sting |
| 42 | 1:04.6 | 2.2 | LESSON / R | MCU, soft light, slow pull-out | BG-09 | Uncle melts in bliss, hearts float up, light rays. "Worth it." | BG-09, UN-17, FX-05 | hearts, petals, rays | ding, heart pops; tender music; Uncle line |

### F. Legend scroll: ink and paper

| # | Time | Dur | Type / method | Shot size and camera | Plate | Exact action and line | Assets | FX | Sound |
|---|---|---|---|---|---|---|---|---|---|
| 43 | 1:06.8 | 2.0 | LEGEND / K | MCU front over the journal edge, then ink bleed | BG-13 | Boy turns the journal page; ink bleeds out of the page and unrolls into a scroll. Frame rate drops to stepped 8-12 fps. V.O.: "Legend says..." | BG-13, PR-06, FX-07, BO-17 | ink bleed, grade sepia | page turn, brush swish; tender pluck |
| 44 | 1:08.8 | 3.4 | LEGEND / R | ELS, pan L->R across the scroll, 3-layer parallax | BG-14 | Ink caravan crosses the dunes (4-frame walk cycle on fours), sun disc sinks, a paper cloud slides. V.O. [pending copywriter: hedged Silk Road line, "Many people believe..."]. | BG-14, LG-03, LG-05 | paper grain, stepped motion | wind, camel bells, guzheng pluck |
| 45 | 1:12.2 | 2.0 | LEGEND / C | Pan continues, scroll lands in a town | BG-15 | Scroll pans into a small town at dawn: paper rooftops, a rooster paper-cut pops up. V.O.: "Around 1871, in Nanxiang..." (hedged). | BG-15, LG-04, LG-05 | petals, paper grain | rooster, morning bell |
| 46 | 1:14.2 | 2.2 | LEGEND / R | MCU kitchen | BG-16 | Old cook's hands roll the dough thin; he holds the skin up to the window: light shines through it. V.O.: "Tiny buns with paper-thin skin." | BG-16, LG-01, LG-02 | paper grain, glow | rolling pin tap, soft pluck |
| 47 | 1:16.4 | 2.2 | LEGEND / H | ECU macro | BG-16 | Gold jelly glows, melts in the steam, ink washes bloom from gold to orange as the soup fills the bun. V.O.: "And a secret: soup that melts when steamed." | BG-16, LG-06, LG-02 | ink bloom, rays | sparkle, melt |
| 48 | 1:18.6 | 1.6 | LEGEND / G | Locked card, brush-stroke reveal | BG-13 | Red seal stamp lands. A basket is drawn stroke by stroke. Card: "Xiaolongbao = little basket bun" (editor text). | BG-13, FX-07 | brush strokes, seal impact | seal thud, pluck |
| 49 | 1:20.2 | 2.0 | LEGEND / R | MCU, camera shoves back | BG-13 | From behind the paper, Uncle's finger pokes through, rips the scroll open (torn edge), his eye peeks in. Color world floods back. Uncle: "Is this the part with food?" | BG-13, UN-06, UN-03, FX-09 | rip, color flood | paper rip, brush plink; Uncle line |

### G. Fun fact and Dad's wisdom

| # | Time | Dur | Type / method | Shot size and camera | Plate | Exact action and line | Assets | FX | Sound |
|---|---|---|---|---|---|---|---|---|---|
| 50 | 1:22.2 | 2.4 | FACT / G | MS locked, card pops | BG-18 | Paper-cut fact card pops up beside the pagoda silhouettes: "In Nanxiang many people still say xiaolong mantou." Boy in the lower third presents it to the lens. | BG-18, BO-07, BO-03, BO-04 | card pop, sparkle | pop, sparkle; Boy line |
| 51 | 1:24.6 | 2.0 | FACT / R | MCU | BG-18 | Uncle holds up two fingers, eyes light up with sparkles: "Two names? So... two dumplings." | UN-06, UN-03, UN-04, FX-05 | sparkles | boing; Uncle line |
| 52 | 1:26.6 | 3.2 | DAD / R | WS, slow push-in, sepia | BG-12 | Dad's silhouette stands in golden light, hat ribbon fluttering; dust motes drift. V.O.: "Dad wrote: Life is like a soup dumpling." | BG-12, DD-01 | dust, rays, grade sepia | wind, soft strings; V.O. |
| 53 | 1:29.8 | 2.0 | DAD / C | Insert, handwriting reveal | BG-02 | Pencil strokes draw themselves across the page (mask reveal), a tiny spoon doodle in the margin. V.O.: "If you rush it, you get burned." | BG-02, PR-06 | stroke reveal | pencil scratch |
| 54 | 1:31.8 | 2.6 | DAD / K | ECU macro, slow orbit feel (parallax) | BG-12 | A golden dumpling glows, steam spirals. V.O.: "If you're patient, you get the best part." | PR-03, FX-01 | glow bloom, steam | chime, strings swell |

### H. Heart moment: the bridge

| # | Time | Dur | Type / method | Shot size and camera | Plate | Exact action and line | Assets | FX | Sound |
|---|---|---|---|---|---|---|---|---|---|
| 55 | 1:34.4 | 2.8 | HEART / R | WS from behind, locked, slow push | BG-10 | Night. Boy sits on the bridge, journal on his knees; Uncle lowers himself beside him, slowly. Lantern light ripples on the water. | BG-10, BO-13, UN-18, PR-12 | water ripple loop, lantern flicker, fireflies | crickets, water, soft koto |
| 56 | 1:37.2 | 1.8 | HEART / R | ECU hands | BG-10 | Uncle sets a last dumpling on a spoon, waits, hands it over. | PR-03, PR-04, UN-06, BO-05 | steam, lantern glow | spoon clink |
| 57 | 1:39.0 | 3.4 | HEART / R | MCU Uncle, slow push | BG-10 | Uncle, tender, quiet: "Your dad picked a good first page." | UN-03, UN-04 | lantern bokeh | music thins to one note; Uncle line |
| 58 | 1:42.4 | 2.0 | HEART / R | CU Boy | BG-10 | Boy smiles with his eyes closed; a single petal drifts past. | BO-20, FX-11 | rays, petal | soft sparkle |

### I. Button and cliffhanger

| # | Time | Dur | Type / method | Shot size and camera | Plate | Exact action and line | Assets | FX | Sound |
|---|---|---|---|---|---|---|---|---|---|
| 59 | 1:44.4 | 1.4 | CLIFF / R | MS, snappy | BG-10 | Uncle fans his tongue with the journal, flapping: "Patience. Got it." Boy winces. | BG-10, UN-19, BO-10 | none | whoosh, flap; music snaps to adventure |
| 60 | 1:45.8 | 1.0 | CLIFF / R | ECU hand, whip-pan | BG-10 | Uncle's long arm stretches off-frame for the next dumpling (smear). | UN-20, UN-06 | speedlines horizontal | swoosh |
| 61 | 1:46.8 | 1.2 | CLIFF / R | ECU hands, speed lines | BG-11 | Grandma's hands fold dumplings in a blur: 4-frame cycle on ones, finished dumplings pile up. | BG-11, GM-04, PR-13, GM-05 | blur trails | whoosh whoosh whoosh |
| 62 | 1:48.0 | 1.0 | CLIFF / R | MCU, 6-frame push-in | BG-11 | Grandma freezes mid-fold, eyes slide to the lens. | BG-11, GM-06, GM-02 | none | riser, tick |
| 63 | 1:49.0 | 1.0 | CLIFF / R | Insert, low angle | BG-10 | Boy's conical hat, ribbon swinging, light catches the brim. | PR-14, BO-02 | glint | sparkle |
| 64 | 1:50.0 | 2.4 | CLIFF / R | MS two-shot | BG-10 | Grandma hurries over (6-frame walk), touches the brim, smiles: "That hat! He ate here." | BG-10, GM-07, GM-08, GM-04, BO-06 | none | footsteps; Grandma line |
| 65 | 1:52.4 | 3.0 | CLIFF / R | CU, push-in | BG-10 | Grandma points south: "Then he went south. To the dim sum city." Boy's eyes go wide. | GM-08, GM-02, GM-03, BO-03, BO-09 | none | swoosh; Grandma line |
| 66 | 1:55.4 | 1.8 | CLIFF / G | Top-down map | BG-17 | The dotted route lights and runs south along the coast, paper train chugs after it. | BG-17, PR-08 | route glow, sparkle | chug, sparkle, epic swell |
| 67 | 1:57.2 | 2.8 | CLIFF / R | Low angle hero, push-in, then smash cut | BG-10 | Boy to lens: "Dad went south? Next stop: Guangzhou!" Uncle photobombs from the side with a dumpling. Smash to end card. | BG-10, BO-14, UN-07, BO-08 | punch zoom, speedlines | taiko + ding; end sting |

### Breakdown totals

| Type | Shots | Seconds | Avg shot |
|---|---|---|---|
| Cold open | 5 | 4.5 | 0.90 |
| Host to camera | 7 | 15.6 | 2.23 |
| Montage | 6 | 8.8 | 1.47 |
| Gag | 14 | 21.5 | 1.54 |
| Lesson (host + gag) | 10 | 16.4 | 1.64 |
| Legend scroll | 7 | 15.4 | 2.20 |
| Fun fact | 2 | 4.4 | 2.20 |
| Dad memory | 3 | 7.8 | 2.60 |
| Heart | 4 | 10.0 | 2.50 |
| Button / cliffhanger | 9 | 15.6 | 1.73 |
| **Total** | **67** | **120.0** | **1.79** |

| Method | Shots | Seconds | Share |
|---|---|---|---|
| R Rig | 39 | 75.8 | 63% |
| K Keyframes | 10 | 12.4 | 10% |
| C Camera | 8 | 11.6 | 10% |
| H Hero | 5 | 9.6 | 8% |
| G Graphic | 5 | 10.6 | 9% |

---

## 3. Asset list (derived from the breakdown)

**Totals: 93 MUST items and 12 nice items.** By group (MUST / nice): plates 17/2, Boy 18/2, Uncle 23/1, Grandma 8/0, Dad 1/0, legend ink cast 5/1, props 12/4, FX sprites 9/2.
Each line is one generation task or one sheet (a sheet = several variants on one image, cut apart later). "Used in shots" is computed from the breakdown, so every item has a use.

### 3.1 How to generate in one go (Canva)
1. **Style lock:** paste the global style line from `character-bible.md` and pass the reference IDs (Boy `MAHbzwNGxJo`, Uncle `MAHbzx4PTVI`, Grandma `MAHb0FNIPP4`) every time. The drawing must stay identical: round, soft, bright pastel, brown outline.
2. **Order:** plates first (no characters, easiest and most stable), then two-character sheets (Boy + Uncle together succeed best), then single-character sheets on a plain flat background, then props and FX sheets.
3. **Plain background for characters:** pose and expression sheets on a flat plain neutral color (one color per sheet), full body, no cast shadow, so `remove-background` cuts cleanly. Keep the hat and ribbon, and the mustache, on separate layers where the rig needs them (head kits).
4. **Boy alone fails often in Canva:** generate the Boy WITH the Uncle (or with a prop) in the same image and crop him, or use the existing cut-outs in `tools/episode_maker/specs/puppets/` as the base for poses.
5. **No text inside art.** Signs, cards and the passport stamp are blank; the editor adds all text (clean, no wrong characters).
6. **Plates:** wide pan plates should be generated at the widest ratio Canva allows (16:9 or wider) and extended; tall plates 9:16 at the highest resolution. Ask for "empty, no people", layered if possible (sky, far, mid, foreground), otherwise the engineer splits layers with `separate-image-layers`.
7. **Legend plates** are the same objects in ink style: "ink wash and paper-cut on rice paper, 2-3 colors, cream, ink brown and orange".
8. **Nothing is final until Canva exports pass a consistency check** against the reference IDs; reject anything with a changed hat, ribbon, belt or mustache.

### 3.2 Background plates (empty, no characters)


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| BG-01 | MUST | Stall counter interior, close, tall. Layers: back wall + hanging lanterns / counter + shelf (steamer mount point) / fg basket rim. Warm orange light. | 1, 2, 4, 5 |
| BG-02 | MUST | Journal table, top-down, scuffed wood, nothing on it. | 7, 9, 53 |
| BG-03 | MUST | Shanghai skyline at dusk across the river, wide pan plate. Layers: sky / skyline / river + small boat lane / fg railing. | 10 |
| BG-04 | MUST | Metro platform + track, side view, wide pan plate, blank sign panel (text added in editor). | 12 |
| BG-05 | MUST | Nanxiang canal street, golden hour: canal, stone bridge, lanterns, shopfronts. Wide pan plate (2.5x width). Layers: sky / far roofs / mid street / fg railing + hanging lantern. | 13, 15, 17, 21 |
| BG-06 | MUST | Twin old brick pagodas, extreme low angle, tall. Layers: sky / pagodas / roof edge + foliage fg. | 14 |
| BG-07 | MUST | Narrow alley, cobbles, doorways, a steaming stall far end, ground-level view, wide pan plate (3x width). Layers: far stall / mid walls / fg doorframes. | 18, 19, 20 |
| BG-08 | MUST | Dumpling stall exterior, street front, tall. Counter with an empty mount for steamers (steamers come from PR-01/02). | 22, 23, 24, 25, 26, 30, 32 |
| BG-09 | MUST | Dumpling shop dining corner, tall: wooden table (empty top) + two stools, window light. | 33, 34, 37, 38, 40, 42 |
| BG-10 | MUST | Stone bridge at night over the canal, lantern reflections, tall. Layers: sky / far shore / bridge deck + rail / water with reflections / fg lantern. | 55, 59, 64, 67 |
| BG-11 | MUST | Grandma's tiny stall: folding table, flour dust, bamboo shelves, tall. Table top empty (tray comes from PR-13). | 61, 62 |
| BG-12 | MUST | Sepia memory lane, warm golden backlight, soft haze, tall. No figure. | 52 |
| BG-13 | MUST | Ink scroll frame: blank rice-paper scroll with wooden roller ends and paper texture, tall (also used as overlay frame for all legend plates). | 43, 48, 49 |
| BG-14 | MUST | Ink-wash Silk Road dunes and sky, wide pan plate (3x width). Layers: sky + sun slot / far dunes / near dunes / fg grass tufts. | 44 |
| BG-15 | MUST | Ink-wash Nanxiang courtyard dumpling shop at dawn (1871 feel), wide plate. Layers: sky / roofs / shop / garden fg. | 45 |
| BG-16 | MUST | Ink-wash kitchen interior: worktable, steamer, window light, tall. | 46, 47 |
| BG-17 | MUST | Hand-drawn map page of Asia (no text), warm paper, tall. Route lines are drawn by the engine. | 8, 66 |
| BG-18 | nice | Paper-cut fun-fact card background with pagoda silhouettes (existing Canva asset MAHb0NdiCnA can be reused). | 50 |
| BG-19 | nice | Passport page texture with faint stamp rings, tall (title bumper). | 11 |

### 3.3 The Boy


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| BO-01 | MUST | Boy turnaround sheet: front, 3/4 left, profile, 3/4 back, back (full body, hat, bag). | all (reference) |
| BO-02 | MUST | Boy head kit, blank face: front, 3/4, profile, back; hat, chin ribbon, hair fringe as SEPARATE layers. | 15, 63 |
| BO-03 | MUST | Boy expression sheet (9 heads): neutral, host-grin, deadpan, shock, worried, awe, eyes-closed smile, mischief, tender. | 5, 10, 15, 20, 25, 32, 50, 65 |
| BO-04 | MUST | Boy mouth set (8 shapes): closed, small smile, A, O, E, big open, gasp, laugh. | 5, 10, 15, 25, 50 |
| BO-05 | MUST | Boy hand set (9): present palm, point, fist, finger-up, spoon grip, chopstick grip, journal hold, flat on table, one-finger steady. | 7, 8, 9, 20, 30, 34, 37, 56 |
| BO-06 | MUST | Pose: host neutral, front, arms relaxed, bag strap visible. | 15, 22, 30, 33, 64 |
| BO-07 | MUST | Pose: host present, one arm sweeps out, palm up, body angled. | 10, 50 |
| BO-08 | MUST | Pose: point at camera (arm foreshortened toward lens). | 67 |
| BO-09 | MUST | Pose: shock, hat lifts off head, both arms up, mouth O. | 65 |
| BO-10 | MUST | Pose: deadpan side-glance to lens, 3/4 body, one eyebrow up. | 5, 32, 59 |
| BO-11 | MUST | Pose: seated at table, 3/4, holding spoon up (demo). | 37 |
| BO-12 | MUST | Pose: reaching out, one finger on top steamer (steadying the tower), deadpan. | 40 |
| BO-13 | MUST | Pose: sitting on the bridge, seen from behind (hat + bag), journal on knees. | 55 |
| BO-14 | MUST | Pose: hero low angle, one hand on hat brim, confident smile. | 11, 67 |
| BO-15 | MUST | Pose: lunging call-out, arm stretched, mouth wide ("Wait!"). | 25 |
| BO-16 | nice | Pose: awe, head tilted up, 3/4 (skyline / pagodas reaction). | 10 |
| BO-17 | MUST | Pose: holds open journal with both hands, front. | 43 |
| BO-18 | MUST | Cycle: walk, 3/4 view, 8 frames (rig-driven preferred; 8 keyframes as fallback). | 13, 20 |
| BO-19 | nice | Cycle: run, side, 6 frames. | 22 |
| BO-20 | MUST | Bust: smile with eyes closed, soft (Dad memory / heart). | 58 |

### 3.4 The Uncle


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| UN-01 | MUST | Uncle turnaround sheet: front, 3/4 left, profile, 3/4 back, back (belly and belt readable in every view). | all (reference) |
| UN-02 | MUST | Uncle head kit, blank face: front, 3/4, profile, back; mustache as SEPARATE layer (it twitches). | 2, 16, 27 |
| UN-03 | MUST | Uncle expression sheet (12 heads): hungry-neutral, eyes-huge hunger (hook), eager, shock, burned-red, sheepish, sweat-nervous, bliss closed-eyes, tender, tongue-out fanning, thinking, smug-sniff. | 1, 2, 3, 16, 17, 26, 28, 29, 31, 38, 41, 49, 51, 57 |
| UN-04 | MUST | Uncle mouth set (12): closed, A, O, E, big open, gasp, laugh, puffed cheeks, tongue out, chewing, mouth-full, whistle-O. | 2, 16, 27, 31, 41, 51, 57 |
| UN-05 | MUST | Uncle eye variants (6): twitch dots, spiral, streaming tears, half-lid, bulging, happy arcs. | 1, 28, 38 |
| UN-06 | MUST | Uncle hand set (8): chopstick grip, spoon hold, two fingers up, belly pat, reach, finger poke, hold journal as fan, flat open. | 24, 31, 49, 51, 56, 60 |
| UN-07 | MUST | Pose: idle front, belly forward, chopsticks in hand. | 11, 15, 67 |
| UN-08 | MUST | Pose: sniff, head back, nose up, rising on tiptoe. | 17 |
| UN-09 | MUST | Pose: floating, tilted forward, pulled by the nose, arms trailing, feet off the ground. | 19, 21 |
| UN-10 | MUST | Pose: landing squash, feet splayed, belly wobble. | 22 |
| UN-11 | MUST | Pose: low angle, chopsticks aloft, one leg back ("For science!"). | 26 |
| UN-12 | MUST | Pose: rigid frozen, arms stiff at sides, face red, ears ready for steam jets. | 4, 5, 30 |
| UN-13 | MUST | Pose: sheepish shrink, hunched, tiny, fanning tongue. | 31 |
| UN-14 | MUST | Pose: seated at table, 3/4, holding spoon. | 33 |
| UN-15 | MUST | Pose: leaning toward the spoon, sweating (waiting). | 37 |
| UN-16 | MUST | Pose: hands on belly, mid-growl, belly bulging. | 40 |
| UN-17 | MUST | Pose: bliss swoon, eyes closed, head tilted, melting. | 42 |
| UN-18 | MUST | Pose: sitting on the bridge, 3/4 from behind, calm, one last spoon in hand. | 55 |
| UN-19 | MUST | Pose: fanning tongue with the journal, flapping. | 32, 59 |
| UN-20 | MUST | Pose: long reach, one arm stretched toward the next dumpling. | 60 |
| UN-21 | nice | Pose: anticipation crouch before a leap. | 17, 19 |
| UN-22 | MUST | Cycle: waddle walk, 3/4 view, 8 frames (belly bounce delayed 2 frames). | 13 |
| UN-23 | MUST | Cycle: air-pedal (floating legs), 4 frames. | 19 |
| UN-24 | MUST | Pose: burned mid-reaction, cheeks puffed, eyes bulging, leaning back, stiff. | 30 |

### 3.5 Grandma


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| GM-01 | MUST | Grandma turnaround: front, 3/4, side (small, round, apron, gray bun). | all (reference) |
| GM-02 | MUST | Grandma head kit + 6 expressions: warm smile, focused fold, freeze-stare, delighted, knowing smile, mild surprise. | 62, 65 |
| GM-03 | MUST | Grandma mouth set (6). | 65 |
| GM-04 | MUST | Grandma hand set: folding cycle A-D (4 frames), touch hat brim, point south, hold dumpling. | 61, 64 |
| GM-05 | MUST | Pose: behind stall, bust-up, arms free for blurred folding. | 61 |
| GM-06 | MUST | Pose: freeze-stare at the hat. | 62 |
| GM-07 | MUST | Cycle: hurry-walk, small quick steps, 6 frames, 3/4. | 64 |
| GM-08 | MUST | Pose: touching the hat brim, then pointing south (2 poses). | 64, 65 |

### 3.6 Dad


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| DD-01 | MUST | Dad: sepia silhouette from behind, tall, conical hat, holding a spoon; hat ribbon as SEPARATE flutter layer. Never a face. | 52 |

### 3.7 Legend ink cast
Same round, soft shapes in a flat ink and paper look. The Boy and Uncle appear in the scroll through a paper/ink filter of their normal assets, so no new art is needed for them there.

| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| LG-01 | MUST | Ink paper-cut: old cook, front + side, same round soft shapes, flat 2-3 colors. | 46 |
| LG-02 | MUST | Ink paper-cut: cook's hands rolling and pleating dough, 3 stages with dough disc. | 46, 47 |
| LG-03 | MUST | Ink paper-cut: caravan, 3 camels + 2 merchants, side view walk cycle 4 frames. | 44 |
| LG-04 | nice | Ink paper-cut: 4 townsfolk silhouettes (bystanders). | 45 |
| LG-05 | MUST | Ink paper-cut: sun disc, moon, 3 cloud layers. | 44, 45 |
| LG-06 | MUST | Ink sprites: gold jelly glow, steam curls (3 frames). | 47 |

### 3.8 Props


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| PR-01 | MUST | Steamer basket: closed, lid-off, lid mid-lift (3 states). | 4, 23, 39 |
| PR-02 | MUST | Tower of 3 steamers, tiers as separate layers (for wobble and slide). | 22, 33, 40 |
| PR-03 | MUST | Xiaolongbao set: whole top-down, whole side, bitten, pierced with soup trickle, golden-glow. | 23, 24, 27, 34, 35, 36, 54, 56 |
| PR-04 | MUST | Soup spoon: empty, with dumpling, with soup pool. | 34, 35, 36, 38, 41, 56 |
| PR-05 | MUST | Chopsticks: closed, pinching, holding a dumpling. | 24, 34 |
| PR-06 | MUST | Journal: closed, open blank, map page, torn-stub page, handwriting-scribble page (no legible text). | 7, 9, 43, 53 |
| PR-07 | MUST | Big cartoon clock face with separate hands. | 39 |
| PR-08 | MUST | Little paper train for the map route, side view. | 8, 66 |
| PR-09 | MUST | Round passport stamp, blank center (text added in editor). | 11 |
| PR-10 | MUST | Metro carriage side view, blank windows, 2-frame wheel/window cycle. | 12 |
| PR-11 | nice | Bicycle + cyclist, side view, wheel cycle 2 frames. | 13, 21 |
| PR-12 | nice | Red lanterns, 2 sizes, 3 swing frames. | 13, 18, 55 |
| PR-13 | MUST | Grandma's tray: wrappers, filling bowl, folded dumplings. | 61 |
| PR-14 | MUST | Boy's conical hat as a standalone sprite (brim, ribbon). | 25, 63 |
| PR-15 | nice | Dipping dish with ginger vinegar. | 33 |
| PR-16 | nice | River boat silhouette with a small funnel. | 10 |

### 3.9 FX sprites (hand-drawn)


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| FX-01 | MUST | Steam puff sheet: soft cream puffs, 6 frames, 3 sizes. | 1, 4, 8, 23, 36, 54 |
| FX-02 | MUST | Steam ribbon: long curly ribbon, 4-frame undulation, with a nose-hook loop variant. | 18, 19 |
| FX-03 | MUST | Ear-steam jets: cartoon whistle plumes, 4-frame loop. | 4, 30 |
| FX-04 | MUST | Sweat drops (3 sizes), tick marks, anger-vein pop, tear streams. | 2, 28, 38 |
| FX-05 | MUST | Hearts + sparkle stars set. | 42, 51 |
| FX-06 | MUST | Impact starburst + ring shapes (3 variants, black and white). | 3, 29 |
| FX-07 | MUST | Ink-wipe brush masks, 4 variants (scene transition). | 43, 48 |
| FX-08 | MUST | Dust puff, 5 frames (slap, landing, footfall). | 7, 19, 22 |
| FX-09 | MUST | Torn-paper edge overlay (for the scroll rip). | 49 |
| FX-10 | nice | Hot-breath waft lines. | 31 |
| FX-11 | nice | Petals / leaves sheet. | 14, 58 |

### 3.10 Built in the editor (no art needed)
Speed lines, impact flashes, camera shake, grain, vignette, light rays, particles, captions (approved style), lower-third place card, step badges (1 LIFT, 2 SPOON, 3 TINY HOLE, 4 WAIT), passport stamp text, fun-fact card text, route line, handwriting reveal, red seal card text, sign text "NANXIANG - Line 11", paper filter.

### 3.11 Reuse for the next episodes
The Boy, Uncle and Grandma rigs, the steamer, spoon, chopsticks and journal sets, the map page, the passport stamp, the ink scroll frame and the FX sprites carry over to Episodes 2-3 unchanged; only plates and a few guest props change. The China arc (Guangzhou, Beijing) should therefore cost far less than Episode 1.

---

## 4. Hero moments (full, fluid animation)

These 8 moments carry the "this is real animation" feeling. They are the first candidates for an AI image-to-video tool (the Canva video quota returns 2026-12-16) if free hand-keyed or rig-based work cannot reach the quality. Everything else in the breakdown is built from rigs, keyframes, cycles and camera.

Rules for using AI video clips:
- Feed the **exact approved still** (plate with characters composited, or the pose) as first frame, and where the tool allows it a last frame; never text-only.
- Keep the clip short (2-4 s), one action, camera notes in the prompt. Cut the clip in the editor and layer our captions, sounds and impact frames on top.
- Any clip where the hat, belt, mustache or round shapes drift is rejected and replaced by the rig/keyframe version.

### H1. Cold open: eyes, cheeks, impact, ear steam (shots 1-4, 3.7 s in the cut)
- **Why:** Uncle's face goes from pure hunger to a pressure-cooker; steam bursts from his ears. The hook has to be unmistakably animated in the first second.
- **Frames:** First frame: shot 1 key (Uncle eyes huge, steam wisps). Last frame: UN-12 rigid, ear plumes at full length.
- **Prompt skeleton:** Cartoon close-up of a big round bald man with a thin mustache, eyes huge and hungry, red tint spreading over his face, steam shooting from both ears like a train whistle, steamer baskets rattling; soft picture-book style, flat colors, bold brown outlines; 3 s; camera shakes on the burst.
- **Camera:** ECU to WS
- **Cut value:** the shot window is 3.7 s; request a clip of 4 s and trim.

### H2. Uncle towed by the steam ribbon (shot 19, 2.4 s in the cut)
- **Why:** Full-body flight with nose hook, air-pedaling legs, belly drag, parallax alley. The cheapest rig version looks like a sliding sticker.
- **Frames:** First: UN-08 on tiptoe, ribbon at his nose. Last: UN-09 mid-air, tilted, arms trailing.
- **Prompt skeleton:** Round bald man in white kimono with orange belt is lifted off the ground by a curling ribbon of steam hooked on his nose, legs pedaling in the air, belly bouncing behind him, tracking shot along a narrow old alley with red lanterns; soft children's picture-book 2D style; 2.5 s.
- **Camera:** MLS tracking
- **Cut value:** the shot window is 2.4 s; request a clip of 3 s and trim.

### H3. The burn: grab, gulp, eyes, impact, toot (shots 26-30, 5.5 s in the cut)
- **Why:** The comic centerpiece. Needs smears, held poses, impact frames and ear steam to land the joke.
- **Frames:** First: UN-11 chopsticks aloft. Last: UN-12 rigid with ear plumes. (Impact frame and eye close-ups can stay keyframed; only the gulp-to-toot motion needs video.)
- **Prompt skeleton:** Big round bald man grins and swallows a whole dumpling; cheeks balloon, eyes shrink to dots, face turns red, then steam shoots from his ears with a train-whistle toot; picture-book 2D style; 3 s clip, plus 2 impact frames added in the editor.
- **Camera:** LA to ECU to WS
- **Cut value:** the shot window is 5.5 s; request a clip of 6 s and trim.

### H4. Tiny hole: soup macro (shot 36, 1.6 s in the cut)
- **Why:** Liquid and steam behavior in a macro close-up; the educational beat must be clear and appetizing.
- **Frames:** First: PR-03 whole dumpling on spoon. Last: pierced dumpling with golden soup pooling in the spoon.
- **Prompt skeleton:** Extreme close-up of a soup dumpling on a ceramic spoon, a chopstick tip pokes a tiny hole, golden broth trickles out and steam curls upward, warm light, soft cartoon rendering; 2 s.
- **Camera:** ECU macro
- **Cut value:** the shot window is 1.6 s; request a clip of 2 s and trim.

### H5. Tummy growl wobbles the tower, Boy steadies it (shot 40, 2.2 s in the cut)
- **Why:** Secondary motion chain: belly shake, tower tier slide, one calm finger. Great gag if the physics read.
- **Frames:** First: UN-16 hands on belly, tower upright. Last: tower stable, BO-12 finger on top.
- **Prompt skeleton:** Low angle: a big round man's belly shakes with a loud growl, a tower of three bamboo steamers wobbles and slides, a small boy in a conical leaf hat calmly steadies the top with one finger without looking; cartoon picture-book style; 2.5 s.
- **Camera:** LA
- **Cut value:** the shot window is 2.2 s; request a clip of 3 s and trim.

### H6. Legend: caravan to town to cook to melting jelly (shots 44-47, 9.8 s in the cut)
- **Why:** The whole scroll sequence as one flowing ink-wash morph. This is where AI video shines (soft transitions, ink blooms).
- **Frames:** First: ink dunes with caravan on the left. Last: ink macro of gold jelly melting into broth.
- **Prompt skeleton:** Ink-wash and paper-cut animation on a rice-paper scroll: a camel caravan crosses golden dunes, the scroll pans into a small old town at dawn, then into a kitchen where an old cook rolls dough paper-thin, then macro on gold jelly melting in steam; warm cream, ink brown, orange accents; stepped 8-12 fps feel; 8 s (or two 4 s clips).
- **Camera:** ELS pan to macro
- **Cut value:** the shot window is 9.8 s; request a clip of 10 s and trim.

### H7. Grandma's hands blur, then freeze and stare (shots 61-62, 2.2 s in the cut)
- **Why:** Speed-to-stillness contrast that sells the cliffhanger. Needs very fast hands and a snap stop.
- **Frames:** First: GM-05 folding. Last: GM-06 frozen, eyes on the lens.
- **Prompt skeleton:** A tiny grandmother folds dumplings with blurred, lightning-fast hands, then freezes mid-motion and slowly turns her eyes toward the camera; soft cartoon style, warm night light; 2.5 s.
- **Camera:** ECU to MCU push
- **Cut value:** the shot window is 2.2 s; request a clip of 3 s and trim.

### H8. Finale: route south, Boy to lens, Uncle photobomb (shots 66-67, 4.6 s in the cut)
- **Why:** The series sign-off; it must feel like a trailer for the next episode.
- **Frames:** First: map with glowing route. Last: BO-14 hero pose with Uncle's face at the frame edge holding a dumpling.
- **Prompt skeleton:** Hand-drawn map, a dotted route glows and runs south along the coast with a paper train, then cut to a boy in a conical hat looking at the camera in a low-angle hero push-in while a big round man photobombs from the side holding a dumpling; 4 s.
- **Camera:** Top-down to LA push
- **Cut value:** the shot window is 4.6 s; request a clip of 5 s and trim.

Combined span of the hero moments in the cut: about 32 s of 120 s (about 27%). Free route first: if the video engineer's rig/keyframe pipeline can do H1-H3 and H5 well, the paid clips shrink to H6 (legend) and H8, and could be skipped altogether.

---

## 5. Dependencies and open points
1. **Copywriter:** re-map the v4 lines onto the shot windows (section 2 header); give the Silk Road line (shot 44) a hedged form ("Many people believe..."); propose host welcome, asides (shots 5, 10, 15, 32) and the Uncle exit line (shot 49). Keep Uncle the only target of jokes.
2. **Video engineer:** confirm which of R, K, C, H are possible in the free route; supply a rig spec for the parts in the Boy, Uncle and Grandma lists; add `scroll` music mood, stepped-fps option (fours), mask-reveal and circle-morph transitions; check hit-stop, smear and impact-frame support from the v2 engine.
3. **Art team (Canva):** use section 3 in one pass in the order from 3.1; mark rejected assets by ID.
4. **Creator decisions:** approve the register split (host / gag / legend / heart), the passport-stamp bumper, whether the host line "Welcome to Shanghai" belongs on a viewpoint plate, and whether the optional cyclist shot stays.
5. **Anonymity and safety:** no personal names or accounts anywhere; no public posting; all art and text English; check no sign in any plate shows real text.
