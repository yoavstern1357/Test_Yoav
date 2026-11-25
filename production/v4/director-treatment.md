# Director's treatment: Episode 1 in motion (V4)

Status: DRAFT for the creator and the team. Written 2026-11-25 by the director. English only, internal, not for publication.
Inputs read: `CLAUDE.md`, `production/v4/BRIEF.md`, `production/v2-direction.md`, `production/animation-roadmap.md`, `production/character-bible.md`, `scripts/episode-01-v4.md` (the script this breakdown follows), `production/v4/comedy-style.md`, `scripts/episode-01-xiaolongbao.md`, `scripts/episode-01-v2.md`, `tools/episode_maker/specs/episode-01-v3.json` (rejected still-frame version, used only as a structural reference) and `tools/episode_maker/README.md`.

**Dialogue status: RE-MAPPED to `scripts/episode-01-v4.md` (v2 of this document was built on the old v2 script).** Every shot below carries the real v4 dialogue and cards, and a "Beat" column that points to the 56 script beats. The script's beats are split into 69 shots where a cut makes the joke land; the script's own timing is kept (beat windows unchanged, total 2:05 including the 5 s sting), with three small retimes to fix dense dialogue: beat 17 gets +0.8 s (taken from beat 18), beat 43 gets +0.8 s (taken from beats 36 and 41). `production/v4/content-research.md` does not exist yet, so facts are checked only against the sources listed at the bottom of the v4 script (legend 1871 hedged with "Legend says" and "*competing versions exist"; "xiaolong mantou" as "many"; Silk Roads as a network of land and sea routes; Nanxiang in Jiading District). Re-check when that file lands.

**Pipeline status: assumption.** The video engineer is still evaluating free animation routes. This treatment is method-agnostic: each shot carries a method code, so the plan survives whichever route is chosen.

| Code | Method | Meaning |
|---|---|---|
| R | Rig | Character is assembled from separate parts (head, eyes, mouth, arms, legs, hat) from approved art and animated: cycles, poses, swaps, squash. |
| K | Keyframes | Two or three drawn key images with interpolation or AI in-betweening; held poses with moving secondary elements. |
| C | Camera | Static plates and sprites, animated by camera move, parallax, particles and masks. |
| H | Hero | Needs fluid full animation; first choice is hand-keyed frames or a free open model; fallback is an AI image-to-video clip. See section 4. |
| G | Graphic | Built in the editor/engine (cards, stamps, route line, text badges). |

Result for this episode: **69 shots, 2:05.0 total, average 1.81 s per shot** (43 R, 11 K, 4 C, 4 H, 7 G). Spoken words in the shots: 285 (script says about 285).

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
- **Uncle's big round silhouette dominates a frame at medium size**, so cut to singles often and use the stacked two-shot for interaction. His size is never the joke (comedy bible, rule 3); it is only a composition fact.

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
- **Wide (exaggerated) feel:** low angle, characters scaled up near the lens and shrunk behind, dutch tilt 8-10 degrees. Use for gags and hero poses (v4 beats 20, 23, 32, 40, 54).
- **Normal feel:** eye level, no distortion. Host-to-camera and dialogue.
- **Long lens feel:** flat, compressed, strongly blurred background layers (blur the bg plate 4-8 px, keep subject sharp). Use for macro food and tender close-ups.
- **Rack focus** = cross-fade a blurred copy of the bg layer in, or blur the fg layer out. Use it for the cold open (beat 2: calm Boy sharp, hovering Uncle blurred behind him) and the heart moment.

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
| Legend (paper-cut) | 1.8-2.8 s | Calmer, stepped at 8 fps, but the paper is always sliding |
| Dad / heart | 2.0-3.8 s | Longest allowed (the Dad silhouette and the bridge); everything else stays under 3.0 s |
| Cliffhanger | 1.0-2.8 s | Accelerates, then holds on the hook line |

This episode: average 1.81 s; fast segments (cold open, montage, gag, lesson) average 1.38 s; quiet segments (Dad, heart, fact, legend) average 2.34 s. A curiosity gap is opened about every 15 s (see the beat list in section 2).

### 1.7 Cutting patterns that give the Avatar/Naruto-style kick (rhythm only, nothing copied)
- **The three-beat insert run:** three ECUs on three consecutive words (Lift / Spoon / Tiny hole), each with a taiko hit and a number badge. Rhythm does the teaching.
- **Smash cut from silence:** drop the music for 0.3 s before the impact frame (beats 21-22) and cut from a quiet close-up to a loud wide. The same device returns for 'That's not what he looked like.' (beat 40) and the sting.
- **Reaction ladder:** a gag escalates through three reactions of increasing size (eyes, cheeks, ears), each shorter than the last.
- **Match cuts on circles and shapes:** steamer lid to clock to lantern to hat.
- **Aside to camera:** after a gag the Boy glances to the lens (2.0 s hold). This is the show-host voice and the main laugh engine.
- **Whip transitions** only between scenes, never within a conversation.
- **Cutaway button:** a 1 s side gag (the Camel stepping off the metro and strolling away) after a big move, then back.

### 1.8 Acting rules
**General (applies to every character)**
- Every gesture has **anticipation (4-6 frames) - action (2-4 frames) - overshoot (2 frames) - settle (4-6 frames)**. Round characters allow strong squash and stretch: 15-25% on hits, 35% only on gags.
- **Key poses first**: each shot is built from 2-3 strong poses with clear silhouettes; in-betweens are minimal and on twos (12 drawings per second) while camera and FX run smoother.
- **Follow-through and overlap**: hat ribbon, mustache, belt tails, bag strap and robe hem lag 2-4 frames behind the body.
- **Eye-lines**: characters look at what matters; looks to the lens only for host lines and asides.
- **Blinks** every 2.5-4 s in held shots, never on a beat; a hold longer than 1.5 s must have a blink, a breath or an eyebrow move.
- **Breathing** 2-frame loop, 0.5 Hz, only when the character is in a hold.
- **Lip sync**: 4 mouth shapes (closed, small open, wide open, O), changed on twos, with the drawn mouth hitting a wide shape on stressed syllables. Close the mouth 2 frames before the cut.

**The Boy (host)**
- Calm and precise. Small gestures: one arm sweep, one pointed finger, one raised eyebrow. His comedy is stillness: a 1.5-2.0 s deadpan hold beats any wild reaction.
- Walk: even, 8 frames, hat ribbon trailing. Presenting: weight on one foot, palm open, a tiny head tilt.
- Eyes-closed smile is reserved for Dad moments and 'Co-host.', so it always means something. The Boy never turns to look at something unless the script says so; he keeps his eyes on the lens (8-frame look-to-lens) while chaos happens behind him.

**Uncle (chaos co-host)**
- Everything is bigger than the Boy's, with telegraphed anticipation: before any dash, lunge or grab he coils (crouch or lean back) for 4-6 frames so the audience sees it coming.
- **Nose-led.** His body follows his nose and appetite; robe and belt tails drag 2 frames late; chopsticks are always in his hand or tucked in his belt. Secondary motion (stomach growl, belt tails) is physics, never a body joke.
- Signature poses: chopsticks aloft like a trophy, chest puffed; the humbled hunch with a tongue fan; the balloon-face hover. 3-frame chibi squash for his tiniest moments.
- Reactions climb in size: eyes dots (small) to cheeks puffed (medium) to ear steam (huge).

**Grandma**
- Tiny, still and precise. Her hands do everything: fast folding cycle on ones, then a dead stop. Her cliffhanger stare is the only time she looks at the lens.

**The Camel (silent cameo)**
- Never speaks, never reacts: it looks at the lens like a co-host who has seen everything. Blink every 3-4 s, move only head and legs. It targets nobody. Appears on the map caravan, stepping off the metro, looking south, and in the sting.

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
| Reuse and reverse | Play the cold-open clip backwards at 3x with film-reel stripes as the rewind (beat 5 reuses beats 2-4) | Rewind |
| Mask reveals | Handwriting and route lines drawn by mask | Journal, map, ink strokes |
| Color holds | Flash to white or tint a face red instead of redrawing | Burn gag |
| Limited-palette swaps | Scroll look is a filter of the same assets | Legend |
| Push-ins on static art | Scale up with eased blur-free zoom | Food macros, torn page |

### 1.10 The three registers (and their cousins)
| | Host to camera | Gag | Ancient legend (scroll) | Dad / heart |
|---|---|---|---|---|
| Look | Clean, bright, full color, TV lower-thirds and cards in paper-cut/ink style, location plates, rim light; the Boy holds chopsticks as a microphone | Same, with exaggerated perspective, squash, smears, speed lines, sweat drops | Paper-cut storybook: sepia and vermilion, layered paper silhouettes, red LEGEND SAYS seal, torn-paper entry, drifting petals, paper grain | Sepia (Dad) or dusk indigo with lantern orange (bridge) |
| Frame rate feel | Characters on twos, camera smooth | Characters on ones for hits, on twos otherwise; hit-stop | Stepped: everything on fours (about 8 fps), nothing smooth | Slow, almost still, 24 fps with soft drift |
| Camera | Steady, slow push-in, parallax drift, backward-walk tracking | Crash zooms, dutch, shake, whips, snap zooms | Flat side-scroll, slow pan, no perspective, no rotation | Locked or very slow push-in |
| Characters | Rig with full expression set, direct address | Rig with extreme poses and impact frames | Paper-cut figures; the legend hero wears the Uncle's face; Boy and Uncle only through a paper/ink filter of their normal art | Silhouettes, close faces, minimal motion |
| Text | Lower-third (UNCLE - co-host), word cards, fact card, intermission and safety signs, all paper-cut/ink stamps | Sound-effect words only (TOOT, GRRROWL) | Brush text only: red LEGEND SAYS seal, scroll banner, asterisk card | One fragile handwriting insert |
| Music | Light adventure, plucked strings, 120 BPM; elevator parody for the intermission | Taiko stabs and silence; tension then release | Plucked strings, low drone, gong; no drums | One sustained piano note, then a single koto |
| Transition in/out | Title slam, steam wipe, whip, film-reel rewind | Smash cut, impact frame | Seal stamp and paper tear in, smash cut out | Slow dissolve in, soft match-cut out |

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
| Legend | Sepia paper, vermilion seal, ink brown, orange accents, gold jelly | Paper filter, 8 fps | No cool tones |
| Dad memory | Backlit golden, haze, dust | Sepia | Faceless silhouette |
| Heart (bridge) | Deep indigo night, orange lantern pools, water glints | Cool with warm accents | The only night scene; keep it small and calm |
| Cliffhanger | Return to warm, add a violet-to-teal sky hint | Warm | Last shot is the brightest |

### 1.12 Transitions catalog
| Name | How | Use |
|---|---|---|
| Steam wipe | Steam sprite sweeps across the lens, cut inside it | Between stall scenes |
| Whip | 0.15 s horizontal slide with blur | Scene changes |
| Seal and tear | Red LEGEND SAYS seal stamps, the frame tears like paper (6-frame rip) into the paper-cut world | Into the legend |
| Smash back | Hard cut from paper-cut hero pose to Uncle's real pose with a napkin cape, record scratch, color floods back | Out of the legend |
| Title slam | Gong, paper banner unrolls, Uncle drops onto the 'O' and sags it | Title |
| Film-reel rewind | Film stripes sweep the frame, steam sucks back into Uncle's ears | Cold open to story |
| Silhouette match cut | Camel line becomes metro-car line on the same dotted route | Old road to today |
| Circle match cut | Lid, clock, lantern, plate, hat | Lesson, heart |
| Rewind | Reverse a clip at 3x with tape sound | Cold open to story |
| Smash cut | Hard cut from quiet to loud, with music cut 0.3 s earlier | Gags |

### 1.13 Sound design cues (sync rules)
- **Pre-hit whoosh, hit, tail**: every cut with camera motion has a whoosh starting 4 frames before the cut; every impact has a hit on the first frame, then a tail.
- **Silence is a sound.** Music cuts 0.3 s before the impact frame (beat 22) and returns with the toot (beat 23). Tick-tock and a rising whine are the only sounds before it (beat 21).
- **Taiko on poses**: each step badge (Lift, Spoon, Tiny hole, Wait) and each hero pose lands on a drum hit.
- **Ear steam = whistle**, pitch rises with the steam: kettles in the cold open (beats 2-3), the long train-whistle toot at the burn (beat 23); the same two sounds are the callback.
- **Foley that tells the story:** steamer lids, chopstick clicks, tummy growl, bike bell, slap of the journal. Every cycle (walk, pedal, folding hands) gets a matching loop.
- **Voices:** `boy` (calm, precise, deadpan host, close-miked), `uncle` (big, warm, loud; tiny when humbled), `narrator` (deep, solemn, a little echo, low gong before he speaks), `grandma`. Dad has no voice of his own; the Boy reads his journal in a quiet V.O. Captions are burned in on every spoken line (the show is watched muted), and sound-words (TOOT, GRRROWL) appear as animated text.
- **Music order (from the v4 script):** tension (cold open) -> plucked strings (old road) -> adventure (host walk) -> silence at the impact frame -> elevator-music parody for the intermission -> sparse (staring contest) -> plucked strings (legend) -> soft piano (Dad and bridge) -> adventure and epic (cliffhanger) -> tender piano (sign-off) -> one tiny toot.
- Cuts are beat-snapped (`snap_to_beat`), but gag beats may sit 1-2 frames off the grid on purpose when a hit needs to land earlier.

### 1.14 Comedy staging (visual only; copy is the copywriter's)
- **Straight man and chaos:** the Boy is calm, the Uncle is chaos; the funny face is the Boy's deadpan hold, not Uncle's. Always cut to the Boy after the chaos. One gag per shot, hold every reaction at least 0.4 s, 8-frame look-to-lens, sweat drop for 'I have made a mistake', 3-frame chibi squash.
- **Running gags (visual, from the v4 callback map):** the 'Co-host' lower-third (self-appointed -> approved, beats 3, 10, 48); 'There's soup inside' (warned, repeated humbled, made right by the Safety Segment); 'For science!' bold then whispered; Uncle in the legend hero pose then the napkin-cape smash back; the Camel (beats 7, 8, 12, 53, 56); the burned tongue (Uncle, then Dad's line, then Grandma's story, then the ice bucket).
- **Rule of three:** the three-beat insert run (Lift, Spoon, Tiny hole); Uncle's three escalating reactions.
- **Callback:** "For science!" is shouted at the burn, whispered at the sip; the ear-whistle returns; the fan returns with the journal.
- **Misdirection:** the cold open looks like an explosion of rage but turns out to be a hot dumpling.
- **Jokes are only on Uncle's behavior (appetite and hubris), never on any place, people, Grandma, Dad, children, or his size.** Pronounce and write local names correctly; no 'exotic' framing of food.

### 1.15 The two atmospheres together: travel show host and Silk Road
- **Host layer:** the Boy talks to the lens on location (pier, canal lane, pagodas) holding chopsticks as a microphone, walks backward giving the tour with TV lower-thirds, and Uncle photobombs the frame edge or the title. TV graphics (lower-third, intermission, safety sign, rating card, LEGEND SAYS seal) are paper-cut/ink stamps in the series palette.
- **Silk Road layer:** the old road is an ink-wash map with a dotted route and a camel caravan (match-cut to the metro), the Scroll Narrator opens with 'For centuries, travelers crossed deserts and seas...', the legend is a paper-cut storybook, Dad's journal is the family treasure map. The Camel is the road's silent witness. The characters keep the approved round, soft drawing everywhere.
- **Never copy:** no elemental-bending style poses, no hand-seal gestures, no recognizable title cards, music or compositions. We borrow only: fast contrast between holds and bursts, short episodes with cliffhangers, comic reaction timing.

---

## 2. Animation breakdown: Episode 1 (69 shots, 2:05.0)

Notes on reading the tables:
- `Time` is the cumulative start. The render may stretch a shot slightly to fit the voice (as the engine does), but the shot windows below are the budget. Beat windows follow the v4 script (see the retimes in the header).
- Plates are EMPTY backgrounds (no characters); characters, props and FX are composited on top (IDs from section 3).
- Dialogue is quoted from `scripts/episode-01-v4.md`; `[CARD: ...]` is on-screen graphics (text added in the editor, art from section 3.2 GR templates). Boy V.O. that runs across a cut stays in the first shot of the beat.
- Dense dialogue to watch (words per second above 3.3 in the beat window): beat 17 (6 words in 1.8 s), beat 37 (13 words in 3.6 s), beat 40 (10 words in 3.0 s), beat 43 (13 words in 3.6 s), beat 55 (10 words in 2.6 s). The engine stretches a shot to fit the voice; if the cut must stay within the v4 time, ask the copywriter for a trim.

### Segment overview
| Segment | Shots | Start | Length | Intent |
|---|---|---|---|---|
| A. Cold open: result first, host stays calm | 1-6 | 0:00.0 | 8.0 s | Floating Uncle behind a calm host, 'Co-host' thread starts, rewind. |
| B. The journal and the old road | 7-12 | 0:08.0 | 13.0 s | Silk Road intro, camel caravan, match cut to metro, torn page, title slam. |
| C. The host walk | 13-20 | 0:21.0 | 16.2 s | Backward-walking tour with lower-thirds; Uncle towed by a smell. |
| D. The burn | 21-29 | 0:37.2 | 10.8 s | Setup, trigger, silence, impact, toot, 'We'll be right back.' |
| E. Safety segment | 30-40 | 0:48.0 | 16.0 s | Lift, Spoon, Tiny hole, Wait, Sip; staring contest; growl; 10/10. |
| F. Legend says | 41-50 | 1:04.0 | 20.6 s | Seal and tear into the paper-cut world; Uncle-faced hero; smash back; asterisk. |
| G. Fun fact | 51-53 | 1:24.6 | 6.6 s | Card, then the two-names bit. |
| H. Dad's page and the bridge | 54-59 | 1:31.2 | 15.6 s | No jokes 1:31-1:43; 'Co-host.' pays off the thread. |
| I. Cliffhanger and sign-off | 60-69 | 1:46.8 | 18.2 s | Grandma freezes, 'Burned his tongue', south, 'Dad was right...', sting. |

### Spine of the episode (v4 script) and where each gap opens and closes
1. 0:00 Why is Uncle floating and exploding while the host welcomes me calmly? Answered at the impact frame, shot 26 (0:42.6).
2. 0:08 A road of silk, spices and probably snacks; Dad's journal has a torn last page (series thread, left open).
3. 0:25 Tour-guide walk: what is floating behind the host? A smell, which leads to the stall (shot 21).
4. 0:44 The burn, then the Intermission card.
5. 0:48 The safe way: Lift. Spoon. Tiny hole. Wait. Sip.
6. 1:04 A little history: Legend says, with Uncle's face on the hero.
7. 1:31 Dad's page, then the bridge, then "Co-host."
8. 1:47 Grandma recognizes the hat, then south, then "Dad was right..."

### A. Cold open: result first, host stays calm

| # | Time | Dur | Beat | Type / method | Shot size and camera | Plate | Exact action | Dialogue (v4 script) | Assets | FX | Sound / music |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0:00.0 | 0.6 | 1 | COLD / G | Black frame, locked | - | Black. One low gong. A thin line of steam rises from the bottom edge. | - | FX-01 | steam line | gong |
| 2 | 0:00.6 | 1.2 | 2 | COLD / R | SMASH IN, MS, eye level, locked; Uncle out of focus behind | BG-01 | Boy stands dead-center facing the lens, chopsticks held like a microphone, hat ribbon fluttering in a warm updraft. Behind him, blurred, Uncle hovers a meter off the ground. Steamers rattle on the shelf. | BOY: "Welcome to The Dumpling Boy." | BG-01, BO-06, BO-03, BO-04, UN-25, PR-02, FX-01 | updraft, steam, rack-focus blur on bg | whistling kettle, rattle; music tension, low |
| 3 | 0:01.8 | 0.8 | 2 | COLD / R | CU Uncle, slow rotate-in, handheld | BG-01 | Uncle's balloon-face, purple-red and puffed, slowly rotates; both ears whistle steam like kettles. | - | BG-01, UN-25, UN-03, FX-03 | ear steam kettles | whistling kettles |
| 4 | 0:02.6 | 2.8 | 3 | COLD / R | Slow push-in on Boy, then toot shake | BG-01 | Boy taps the chopstick mic twice. A TV lower-third slides in under the floating Uncle. A huge ear toot blasts steam sideways and tips the Boy's hat; he straightens it without breaking eye contact (8-frame look-to-lens). | BOY: "That's my uncle. He is not the host." / UNCLE: "Co-host!" [CARD: UNCLE - co-host (self-appointed)] | BG-01, BO-06, BO-02, BO-05, UN-25, UN-04, FX-03, GR-01 | toot shake, lower-third slide | TOOT, tap tap |
| 5 | 0:05.4 | 1.2 | 4 | COLD / R | MS, whip-pan to follow Uncle | BG-01 | Boy raises two fingers like a director. Uncle whirls past the lens, ears jetting. | BOY: "He is luggage." | BG-01, BO-09, BO-05, UN-29, FX-03 | speed lines, smear | whoosh |
| 6 | 0:06.6 | 1.4 | 5 | COLD / K | MS, snap, then film-reel whip into the map | BG-01 | REWIND: the Boy snaps his fingers; film-reel stripes sweep the frame, steam sucks back into Uncle's ears, everything zips backward, whip into the map. | BOY: "Six hours earlier." | BO-09, UN-25, FX-09, FX-01 | reverse clip, film-reel sweep, whip | tape rewind, whip, swoosh |

### B. The journal and the old road

| # | Time | Dur | Beat | Type / method | Shot size and camera | Plate | Exact action | Dialogue (v4 script) | Assets | FX | Sound / music |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 7 | 0:08.0 | 3.8 | 6 | HOST / K | Top-down, locked, slow push | BG-17 | Dad's leather journal slams open on the table; an ink-wash map unrolls across the page like a scroll; a dotted red route draws itself with a pen scratch. | NARRATOR: "For centuries, travelers crossed deserts and seas, carrying silk, spices, and ideas." | BG-02, BG-17, PR-06, FX-08 | slam dust, map unroll, route line draw | page slam, pen scratch, gong; strings (old-road mood) |
| 8 | 0:11.8 | 2.4 | 7 | LEGEND / R | ELS pan L->R along the route, 3-layer parallax, stepped 8 fps | BG-19 | Paper-cut caravan of camels trudges along the dotted route under a rising paper sun. The last camel carries the Uncle, asleep, hugging a steamer basket, drooling. That camel turns its head and stares straight into the lens, unimpressed. | BOY (dry, off-screen): "And, probably, snacks." | BG-19, LG-03, LG-04, UN-26, CM-04, CM-02, PR-02 | stepped 8 fps, paper sun rise | camel bells, low snore |
| 9 | 0:14.2 | 1.0 | 8 | MON / C | MATCH CUT: same dotted route, same framing | BG-19 | The camel line becomes a line of metro cars gliding along the same route (same silhouettes, same rhythm). | - | BG-19, LG-06, PR-10 | silhouette morph (3 frames) | train rhythm; music adventure |
| 10 | 0:15.2 | 1.8 | 8 | MON / R | MS, locked, tiny train sway | BG-20 | Interior: Boy sits with the journal on his knees; Uncle snores beside him; a camel stands in the aisle holding a hand strap, staring ahead. Nobody reacts. | BOY (V.O. runs from the match cut): "Dad left me this journal. One page, one dumpling." | BG-20, BO-17, UN-27, CM-03, PR-06 | window light flicker, sway | train rhythm, snore |
| 11 | 0:17.0 | 2.2 | 9 | HOST / R | Insert, hands: page flicks, then slow push on the tear | BG-02 | Boy flips pages in fast flicks. Page one in Dad's handwriting; then the last page: a ragged torn edge; his fingertip slides along the tear; dust motes drift. | BOY: "The last page is torn out." [CARD: Shanghai. Be patient. The soup is the secret.] | BG-02, PR-06, BO-05 | dust motes, sepia grade | page flicks, riser; music sparse |
| 12 | 0:19.2 | 1.8 | 10 | HOST / G | Low angle hero, slam + settle | BG-02 | SLAM title: gong, a paper-cut banner unrolls. Uncle drops in from above and sits on the O; the banner sags under him. Boy slides it straight again with one finger. | [CARD: #01 XIAOLONGBAO - SHANGHAI, CHINA] | GR-02, UN-28, BO-05, BO-06 | banner sag, impact ring, punch 1.1 | taiko, gong; music epic sting |

### C. The host walk

| # | Time | Dur | Beat | Type / method | Shot size and camera | Plate | Exact action | Dialogue (v4 script) | Assets | FX | Sound / music |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 13 | 0:21.0 | 2.0 | 11 | HOST / R | Whip into WS, slow push, 3-layer parallax | BG-03 | Wide Shanghai skyline at golden hour across the river. Boy and Uncle stand on the pier seen from behind, hat ribbon and robe blowing. | BOY: "Shanghai. Page one." | BG-03, BO-24, UN-34, PR-16 | boat glide, rays, flare on glass | boat horn, gulls |
| 14 | 0:23.0 | 1.8 | 12 | MON / C | Insert whip, then MS on the platform | BG-04 | Metro sign. The doors slide open; the camel steps off the train, nods once to the Boy, and strolls away through the crowd. | [CARD: NANXIANG - Line 11] | BG-04, PR-10, CM-03, CM-02 | speed lines horizontal, whip | doors, bike bell |
| 15 | 0:24.8 | 2.0 | 13 | HOST / R | MS tracking, host walks BACKWARD toward the lens, plate scrolls toward camera | BG-07 | Old Nanxiang canal town, warm light, lanterns. Boy walks backward at a brisk host pace, mic in hand, hat bouncing, eyes on the lens. | BOY: "Welcome to old Nanxiang." | BG-07, BO-22, BO-06, PR-14, PR-19 | parallax, lantern flicker | canal water, bike bell |
| 16 | 0:26.8 | 1.6 | 13 | HOST / R | Same tracking, side of frame | BG-07 | Behind the Boy, Uncle drifts past on the left, feet dangling, eyes closed, nose forward, towed by a ribbon of steam; a stone bridge slides by. | BOY: "On your left, a stone bridge." | BG-07, BO-22, UN-09, FX-02 | steam leash, parallax | canal water |
| 17 | 0:28.4 | 3.0 | 14 | HOST / R | Low-angle hero on the pagodas, tilt up; mic points right | BG-06 | Boy points right with the mic. Two old brick pagodas rise. Uncle floats past on the right, still sleepily smiling, the steam ribbon stretched like a leash. | BOY: "On your right, two very old pagodas." | BG-06, BO-08, BO-06, UN-09, FX-02 | rays, birds, steam leash | wind chimes |
| 18 | 0:31.4 | 2.6 | 15 | HOST / R | MCU on Boy, locked; Uncle drifts behind him | BG-07 | Boy pauses mid-stride. Without turning, he tilts the mic back toward Uncle behind him (the Boy never looks unless the script says so). | BOY: "Behind me, my uncle, kidnapped by a smell." | BG-07, BO-06, BO-03, UN-09, FX-02 | focus pull to Uncle | whoosh |
| 19 | 0:34.0 | 1.4 | 16 | GAG / K | CU on nose then eyes | BG-07 | Uncle's nose sniffs; his eyes spiral into heart-shaped steam. | UNCLE: "I smell... destiny." | UN-02, UN-03, UN-05, FX-05 | heart steam | sniff |
| 20 | 0:35.4 | 1.8 | 17 | GAG / R | MCU Boy, 8-frame look to lens; hold | BG-07 | Cut to the Boy, flat, eyes to lens. | BOY: "That's the steamer." / UNCLE (dreamy, off): "Destiny is steamed." | BO-10, BO-03, BO-04 | none | tick |

### D. The burn

| # | Time | Dur | Beat | Type / method | Shot size and camera | Plate | Exact action | Dialogue (v4 script) | Assets | FX | Sound / music |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21 | 0:37.2 | 1.0 | 18 | GAG / K | ECU macro push; Grandma's blur far back | BG-08 | Tiny dumpling stall. A bamboo steamer tower; the top lid lifts; steam parts like a curtain; glossy dumplings glow; one dumpling's pleats gleam. Far back, a Grandma's hands blur through folding. | - | BG-08, PR-01, PR-02, PR-03, GM-05, GM-04, FX-01 | rays, steam curtain, bg blur | lid lift, hiss; music tension |
| 22 | 0:38.2 | 1.8 | 19 | GAG / R | ECU chopsticks, then MCU Boy, whip | BG-08 | Uncle's chopsticks dart in. Boy swings the mic into frame like a barrier arm. | BOY: "Uncle, wait. There's soup inside." | BG-08, PR-05, UN-06, BO-15, BO-05 | speed lines | whoosh |
| 23 | 0:40.0 | 1.2 | 20 | GAG / R | Low angle, dutch 10 deg, hold | BG-08 | Uncle grips the dumpling, lifts it like a trophy, chest puffed. | UNCLE: "For science!" | BG-08, UN-11, UN-03, PR-03, PR-05 | speed lines radial | taiko |
| 24 | 0:41.2 | 0.9 | 21 | GAG / K | ECU on mouth, rapid | BG-08 | The dumpling vanishes into his mouth (1-frame smear); cheeks puff to a ball. | - | UN-02, UN-04, PR-03 | smear | pop |
| 25 | 0:42.1 | 0.5 | 21 | GAG / K | ECU eye + head, rapid | BG-08 | His eye twitches; a sweat drop swells on his bald head. Silence and a rising whine. | - | UN-05, UN-03, FX-04 | sweat drop swell | riser |
| 26 | 0:42.6 | 0.8 | 22 | GAG / K | IMPACT FRAME: 2 inverted frames, then radial burst; camera shake | BG-08 | White flash, radial speed lines, Uncle's silhouette goes flat red. Music cuts to nothing. | - | UN-24, FX-06 | inverted flash, burst, shake 10 px | impact, crack, gong; music out |
| 27 | 0:43.4 | 1.6 | 23 | GAG / H | WS, dutch 8 deg, handheld; a long tilt up with the rocket | BG-08 | Uncle rockets up two meters, both ears blasting a long TOOOOOT like a train whistle; mustache stands up like antennae; tongue out; he lands and runs in a circle. | - | BG-08, UN-12, UN-31, FX-03, FX-08 | ear jets, shake, dust | long toot; music adventure |
| 28 | 0:45.0 | 1.2 | 24 | GAG / R | MCU, skid then hold | BG-08 | He skids to a stop. Steam still leaks from one ear. Tiny voice. | UNCLE: "...There's soup inside." | BG-08, UN-10, UN-13, UN-03, FX-11 | tiny toots | squeak |
| 29 | 0:46.2 | 1.8 | 25 | GAG / R | MS Boy, locked, deadpan; Uncle orbits behind | BG-08 | Boy to camera, utterly calm, as Uncle orbits in the background fanning his tongue. A graphic card pops over the whole frame, soft elevator music. | BOY: "We'll be right back." [CARD: PLEASE ENJOY THIS BRIEF INTERMISSION] | BG-08, BO-06, BO-03, UN-31, GR-04 | card pop, tiny toots | elevator music, tiny toots |

### E. Safety segment

| # | Time | Dur | Beat | Type / method | Shot size and camera | Plate | Exact action | Dialogue (v4 script) | Assets | FX | Sound / music |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 30 | 0:48.0 | 0.8 | 26 | LESSON / G | Locked card slam | - | A big sign slams in with tiny print underneath. | [CARD: SAFETY SEGMENT] [CARD: brought to you by Uncle's tongue] | GR-05 | slam, impact ring | clink; music adventure |
| 31 | 0:48.8 | 1.2 | 26 | LESSON / R | MS two-shot at the table, slow push | BG-09 | Boy at a small table, spoon in hand; Uncle sits stiff and upright opposite, an ice pack on his cheek, hands folded like a student. | BOY: "How to eat a soup dumpling." | BG-09, BO-11, UN-14, PR-17, PR-18, PR-02 | rays | clink |
| 32 | 0:50.0 | 1.0 | 27 | LESSON / R | ECU hands | BG-09 | Chopsticks lift a dumpling; word card pops. | BOY: "Lift." [CARD: LIFT] | BG-09, PR-03, PR-05, BO-05, GR-06 | card stamp | taiko |
| 33 | 0:51.0 | 1.0 | 28 | LESSON / K | ECU spoon | BG-09 | The dumpling settles into a soup spoon; its skin jiggles. | BOY: "Spoon." [CARD: SPOON] | PR-03, PR-04, GR-06 | card stamp | taiko |
| 34 | 0:52.0 | 1.0 | 29 | LESSON / H | ECU macro | BG-09 | Chopstick tip pokes a tiny hole; a thin ribbon of steam spirals up like a miniature dragon. | BOY: "Tiny hole." [CARD: TINY HOLE] | PR-03, PR-04, PR-05, FX-01, GR-06 | steam dragon, glow | taiko, pop |
| 35 | 0:53.0 | 1.6 | 30 | LESSON / R | MS, clock thunks in; Uncle leans toward the spoon | BG-09 | A giant cartoon clock thunks into frame, ticking. Uncle leans in, nose almost touching the spoon, eyes crossed, sweat drops flying. | BOY: "Wait." [CARD: WAIT] | BG-09, PR-07, UN-15, FX-04, GR-06 | sweat spray | tick, tock |
| 36 | 0:54.6 | 1.4 | 31 | LESSON / K | ECU eyes + spoon, locked | BG-09 | Staring contest: Uncle's eyes and the spoon. Music drops to a low string drone. | NARRATOR: "Neither blinked." | UN-03, UN-05, PR-04, FX-01 | steam on lashes | gong, tick; music sparse |
| 37 | 0:56.0 | 1.4 | 31 | LESSON / R | MCU Boy, deadpan hold | BG-09 | Boy to lens, flat, slow blink. | BOY: "One of them has no eyelids." | BG-09, BO-10, BO-03 | none | tick |
| 38 | 0:57.4 | 2.0 | 32 | LESSON / R | Low angle, Uncle foreground, tower mid | BG-09 | Uncle whispers to the dumpling, sweating. His tummy growls so loud the steamer tower wobbles; the Boy steadies it with one finger, not looking. | UNCLE: "Be cool. Be cool." | BG-09, UN-16, UN-15, PR-02, BO-12, FX-04 | shake, tier slide | growl, rattle, finger tink |
| 39 | 0:59.4 | 1.8 | 33 | LESSON / R | MCU, soft light | BG-09 | Boy nods. Uncle sips; eyes close; petals and tiny hearts float up. | BOY: "Sip." / UNCLE: "For science." | BG-09, UN-17, UN-04, BO-10, PR-04, FX-05, FX-10 | hearts, petals, rays | sip, ding, heart |
| 40 | 1:01.2 | 2.8 | 34 | LESSON / R | MS two-shot, locked | BG-09 | Uncle holds up a hand-drawn rating card. The Boy slides it down with one finger, to camera. | UNCLE: "Worth it." / BOY: "He rates everything ten. Yesterday, a napkin." [CARD: 10/10] | BG-09, UN-06, UN-03, BO-05, BO-03, GR-07 | card pop | pop |

### F. Legend says

| # | Time | Dur | Beat | Type / method | Shot size and camera | Plate | Exact action | Dialogue (v4 script) | Assets | FX | Sound / music |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 41 | 1:04.0 | 2.2 | 35 | LEGEND / K | MCU journal to camera, then the seal and the tear | BG-13 | Boy turns a journal page to camera. A low gong. A red seal stamps the screen. The frame tears like paper and whips into a paper-cut storybook world (sepia and vermilion, stepped 8 fps, drifting petals). | BOY: "A little history." [CARD: LEGEND SAYS] | BG-13, BO-21, PR-06, GR-03, FX-07, FX-10 | stamp impact, tear, color to sepia, stepped fps | gong, stamp, page whoosh; plucked strings |
| 42 | 1:06.2 | 2.2 | 36 | LEGEND / C | Flat side-scroll pan, stepped | BG-14 | Paper-cut dawn: layered pagoda silhouettes, a paper rooster, a round paper sun rising behind them. | NARRATOR: "Legend says, around 1871, in Nanxiang..." | BG-14, LG-04, FX-10 | paper grain, stepped | rooster, strings |
| 43 | 1:08.4 | 1.8 | 37 | LEGEND / R | Paper-cut MS, stepped | BG-15 | A paper-cut shop owner with a thin mustache (his face is suspiciously Uncle's) rises from a paper bed. | NARRATOR: "...a shop owner rose before dawn," | BG-15, LG-01 | paper grain | swoosh, strings swell |
| 44 | 1:10.2 | 1.8 | 37 | LEGEND / R | Paper-cut LA hero, stepped | BG-15 | He strikes a hero pose with a rolling pin raised like a sword; his paper cape flutters in a paper wind. | NARRATOR: "...and dared to make his buns small." | BG-15, LG-01, FX-10 | cape flutter, petals | swoosh, strings swell |
| 45 | 1:12.0 | 2.4 | 38 | LEGEND / R | Paper-cut macro, stepped | BG-16 | A round of dough folds in stepped frames into a pleated bun. | NARRATOR: "Paper-thin skin." | BG-16, LG-02 | paper grain | fold flutter |
| 46 | 1:14.4 | 2.4 | 38 | LEGEND / H | Paper-cut macro, push-in | BG-16 | A cube of glowing jelly drops inside; steam coils up into a tiny paper dragon. | NARRATOR: "And a secret: soup, set in jelly, that melts in the steam." | BG-16, LG-05, LG-02 | glow, dragon loop | sparkle |
| 47 | 1:16.8 | 2.0 | 39 | LEGEND / G | Locked card, scroll unrolls | BG-13 | A scroll banner rolls open. A gong. | NARRATOR: "Xiaolongbao. Little basket bun." [CARD: XIAOLONGBAO = little basket bun] | BG-13, GR-08 | brush reveal | gong, sparkle |
| 48 | 1:18.8 | 1.2 | 40 | GAG / R | SMASH CUT to the real stall, LA, locked | BG-08 | Uncle holds the exact same hero pose, a napkin for a cape, a soup spoon for a sword, one ear still faintly steaming. | - | BG-08, UN-30, PR-04 | color flood back, steam wisp | record scratch, toot |
| 49 | 1:20.0 | 1.8 | 40 | GAG / R | MS two-shot, Boy flat to lens | BG-08 | Boy, flat, eyes to lens; Uncle proud beside him. | BOY: "That's not what he looked like." / UNCLE: "He had my energy." | BG-08, BO-10, BO-03, UN-30, UN-03 | none | tick |
| 50 | 1:21.8 | 2.8 | 41 | LEGEND / G | MCU Boy, stamp drop | BG-13 | Boy, to camera. A small asterisk drops onto the red seal. | BOY: "Legend. That's historian for 'please don't quote me.'" [CARD: LEGEND SAYS*] [CARD: *competing versions exist] | BO-10, BO-03, GR-03 | asterisk drop | stamp, tick |

### G. Fun fact

| # | Time | Dur | Beat | Type / method | Shot size and camera | Plate | Exact action | Dialogue (v4 script) | Assets | FX | Sound / music |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 51 | 1:24.6 | 3.0 | 42 | FACT / G | MS Boy in the lower third, card pops | BG-18 | A paper-cut card pops up next to the pagodas. Boy taps it with the mic. | BOY: "Fun fact: many in Nanxiang still say 'xiaolong mantou.'" [CARD: FUN FACT - Nanxiang: "xiaolong mantou"] | BG-18, BO-06, BO-07, BO-04, GR-08 | card pop, sparkle | pop, sparkle |
| 52 | 1:27.6 | 1.4 | 43 | FACT / R | CU Uncle | BG-18 | Uncle holds up two fingers, then points at two dumplings. | UNCLE: "Two names? Two dumplings." | BG-18, UN-06, UN-03, PR-03 | none | boing |
| 53 | 1:29.0 | 2.2 | 43 | FACT / R | Close two-shot, Boy to lens | BG-18 | Boy looks to the lens, flat; Uncle insists. | BOY: "That's not how names work." / UNCLE: "That's how dumplings work." | BG-18, BO-10, BO-03, UN-03 | none | tick |

### H. Dad's page and the bridge

| # | Time | Dur | Beat | Type / method | Shot size and camera | Plate | Exact action | Dialogue (v4 script) | Assets | FX | Sound / music |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 54 | 1:31.2 | 3.8 | 44 | DAD / R | WS, slow push-in, sepia | BG-12 | Music drops to soft piano. Dad's silhouette from behind, in the conical hat, slowly lowering a spoon. The page glows; the handwriting lifts off the paper in steam. | BOY (V.O., quiet): "Dad wrote: life is like a soup dumpling." | BG-12, DD-01, PR-06, FX-01 | dust, rays, steam handwriting, sepia | piano tender; page |
| 55 | 1:35.0 | 2.2 | 45 | DAD / C | Insert, handwriting reveal | BG-02 | Handwriting; the words fade in one by one. | BOY (V.O.): "If you rush it, you get burned." | BG-02, PR-06 | stroke reveal | soft |
| 56 | 1:37.2 | 2.8 | 46 | DAD / K | ECU macro, slow push; end on the Boy's closed eyes | BG-12 | A golden dumpling in glowing steam; the Boy closes his eyes. | BOY (V.O.): "If you're patient, you get the best part." | PR-03, FX-01, BO-20 | glow, steam | sparkle |
| 57 | 1:40.0 | 3.8 | 47 | HEART / R | WS from behind, locked, very slow push; lanterns light one by one | BG-10 | Dusk on the stone bridge, lanterns light one by one. Boy and Uncle sit feet dangling, seen from behind. Uncle sets one dumpling on a spoon, waits two full beats without moving (no gag), then hands it over. | UNCLE (soft): "Your dad picked a good first page." | BG-10, BO-13, UN-18, PR-03, PR-04 | lanterns ignite, water glints | clink; piano |
| 58 | 1:43.8 | 1.6 | 48 | HEART / R | CU Boy, soft | BG-10 | Boy's eyes closed, a small smile. Quietly, to the Uncle. | BOY: "Co-host." | BO-20, BO-03 | rays | sparkle |
| 59 | 1:45.4 | 1.4 | 48 | HEART / R | MCU Uncle, small push | BG-10 | The lower-third flips under the Uncle. His eyes shine; he sniffs. | [CARD: UNCLE - co-host (approved)] | UN-03, UN-04, GR-01, FX-05 | lower-third flip, eye shine | ding |

### I. Cliffhanger and sign-off

| # | Time | Dur | Beat | Type / method | Shot size and camera | Plate | Exact action | Dialogue (v4 script) | Assets | FX | Sound / music |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 60 | 1:46.8 | 2.2 | 49 | CLIFF / R | MS, smash cut, snappy | BG-10 | Smash cut, music jumps back to adventure. Uncle immediately swallows the next dumpling whole, then fans his tongue with the journal. Quick tiny toot. | UNCLE: "Patience. Got it." | BG-10, UN-19, PR-06, FX-11 | tiny toot, fan flap | toot, whoosh |
| 61 | 1:49.0 | 1.0 | 50 | CLIFF / R | ECU hands, speed lines, then FREEZE | BG-11 | Across the lane, Grandma's hands blur folding dumplings (speed lines). She FREEZES mid-fold. | - | BG-11, GM-05, GM-04, PR-13 | blur trails, speed lines | whoosh, whoosh |
| 62 | 1:50.0 | 1.4 | 50 | CLIFF / H | Anime snap-zoom: eyes, hat brim, eyes | BG-11 | Snap zoom to her eyes, then the hat brim, then her eyes again. She hurries over and touches the brim. | GRANDMA: "That hat!" | BG-11, GM-06, GM-07, GM-08, PR-14, GM-02 | snap zooms, punch | riser, punch |
| 63 | 1:51.4 | 3.0 | 51 | CLIFF / R | MS two-shot | BG-11 | She points at the stool where Uncle sits. | GRANDMA: "He sat right there. Couldn't wait. Burned his tongue." | BG-11, GM-08, GM-02, GM-03, UN-13, PR-18 | none | tick |
| 64 | 1:54.4 | 1.4 | 52 | CLIFF / R | MS reaction, locked | BG-11 | Boy and Uncle look at each other; sweat drop on the Uncle; Boy raises one eyebrow. | BOY: "Sound familiar?" | BG-11, BO-10, BO-03, UN-03, FX-04 | sweat drop | boing |
| 65 | 1:55.8 | 1.4 | 53 | CLIFF / R | CU, push-in | BG-11 | Grandma leans in, then points far south. | GRANDMA: "Then he went south. To the dim sum city." | BG-11, GM-08, GM-02, GM-03 | none | swoosh |
| 66 | 1:57.2 | 2.0 | 53 | CLIFF / G | Top-down journal, slow tilt | BG-17 | In the journal, the dotted line glows and slides south down the coast. In the background the camel lifts its head and looks south too. | - | BG-17, PR-06, CM-03, CM-02 | route glow, sparkle | sparkle, chug; music epic |
| 67 | 1:59.2 | 1.2 | 54 | CLIFF / R | Hero push-in, low angle | BG-10 | Hero push-in on the Boy, to camera. | BOY: "Next stop, Guangzhou." | BG-10, BO-14 | punch zoom, speed lines | taiko, ding |
| 68 | 2:00.4 | 2.6 | 55 | CLIFF / R | Soft CU, warm light, locked | BG-10 | Soft close-up, tiny smile, eyes to lens. | BOY: "Dad was right... the best part is worth the wait." | BG-10, BO-20, BO-03, BO-04 | warm rays | piano tender |
| 69 | 2:03.0 | 2.0 | 56 | CLIFF / R | Pull back to reveal; cut to black | BG-10 | STING: pull back; Uncle sits behind the Boy with his tongue in an ice bucket giving a thumbs-up; the camel stares into the lens beside him. One tiny toot. Cut to black with the end card. | [CARD: NEXT: GUANGZHOU] | BG-10, BO-20, UN-32, PR-17, CM-03, FX-11, GR-09 | tiny toot | toot, cut |

### Breakdown totals

| Type | Shots | Seconds | Avg shot |
|---|---|---|---|
| Cold open | 6 | 8.0 | 1.33 |
| Host to camera | 8 | 19.0 | 2.38 |
| Montage | 3 | 4.6 | 1.53 |
| Gag | 13 | 17.0 | 1.31 |
| Safety segment | 11 | 16.0 | 1.45 |
| Legend (paper-cut / ink) | 9 | 20.0 | 2.22 |
| Fun fact | 3 | 6.6 | 2.20 |
| Dad memory | 3 | 8.8 | 2.93 |
| Heart | 3 | 6.8 | 2.27 |
| Cliffhanger and sting | 10 | 18.2 | 1.82 |
| **Total** | **69** | **125.0** | **1.81** |

| Method | Shots | Seconds | Share |
|---|---|---|---|
| R Rig | 43 | 81.2 | 65% |
| K Keyframes | 11 | 17.2 | 14% |
| C Camera | 4 | 7.2 | 6% |
| H Hero | 4 | 6.4 | 5% |
| G Graphic | 7 | 13.0 | 10% |

---

## 3. Asset list (derived from the breakdown)

**Totals: 116 MUST items and 3 nice items.** By group (MUST / nice): plates 18/1, camel 4/0, graphic templates 9/0, Boy 20/0, Uncle 27/0, Grandma 8/0, Dad 1/0, legend cast 6/0, props 12/2, FX sprites 11/0.
Each line is one generation task or one sheet (a sheet = several variants on one image, cut apart later). "Used in shots" is computed from the breakdown, so every item has a use.

### 3.1 How to generate in one go (Canva)
1. **Style lock:** paste the global style line from `character-bible.md` and pass the reference IDs (Boy `MAHbzwNGxJo`, Uncle `MAHbzx4PTVI`, Grandma `MAHb0FNIPP4`) every time. The drawing must stay identical: round, soft, bright pastel, brown outline.
2. **Order:** plates first (no characters, easiest and most stable), then two-character sheets (Boy + Uncle together succeed best), then single-character sheets on a plain flat background, then props and FX sheets.
3. **Plain background for characters:** pose and expression sheets on a flat plain neutral color (one color per sheet), full body, no cast shadow, so `remove-background` cuts cleanly. Keep the hat and ribbon, and the mustache, on separate layers where the rig needs them (head kits).
4. **Boy alone fails often in Canva:** generate the Boy WITH the Uncle (or with a prop) in the same image and crop him, or use the existing cut-outs in `tools/episode_maker/specs/puppets/` as the base for poses.
5. **No text inside art.** Signs, cards, banners and the seal are blank templates; the editor adds all text (clean, no wrong characters).
6. **Plates:** wide pan plates should be generated at the widest ratio Canva allows (16:9 or wider) and extended; tall plates 9:16 at the highest resolution. Ask for "empty, no people", layered if possible (sky, far, mid, foreground), otherwise the engineer splits layers with `separate-image-layers`.
7. **Legend plates** are paper-cut: "layered paper-cut storybook, sepia and vermilion, soft paper texture, round shapes"; the old-road map and caravan are ink-wash on warm paper.
8. **Nothing is final until Canva exports pass a consistency check** against the reference IDs; reject anything with a changed hat, ribbon, belt or mustache.

### 3.2 Background plates (empty, no characters)


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| BG-01 | MUST | Dumpling shop interior, tall (cold open and burn): counter, shelf with steamer baskets that can rattle, hanging lanterns. Layers: back wall / counter + shelf / fg basket rim. Warm orange light. | 2, 3, 4, 5 |
| BG-02 | MUST | Journal table, top-down, scuffed wood, nothing on it. | 7, 11, 55 |
| BG-03 | MUST | Shanghai pier at golden hour, wide pan plate: river, skyline across the water, boat lane, pier planks + railing in the foreground (room for two characters seen from behind). | 13 |
| BG-04 | MUST | Metro platform + station sign panel (blank, text added in editor), wide pan plate, train door slot. | 14 |
| BG-06 | MUST | Twin old brick pagodas, extreme low angle, tall. Layers: sky / pagodas / roof edge + foliage fg. | 17 |
| BG-07 | MUST | Canal-side lane in one-point perspective for the backward-walk tour: receding path, lanterns, stone bridge on one side, pagodas far on the other. Layers: sky / far / side walls / ground strip that can scroll toward the camera. | 15, 16, 18 |
| BG-08 | MUST | Dumpling stall exterior, tall: counter with an empty mount for steamers, lantern, street behind. | 21, 22, 23, 27, 28, 29, 48, 49 |
| BG-09 | MUST | Shop dining corner, tall: wooden table (empty top) + two stools, window light (Safety Segment set). | 31, 32, 35, 37, 38, 39, 40 |
| BG-10 | MUST | Stone bridge at dusk, tall, a side lane visible where Grandma's stall sits across the way. Lanterns are a SEPARATE layer in two states (off / on) so they can light one by one. | 57, 60, 67, 68, 69 |
| BG-11 | MUST | Grandma's tiny stall across the lane: folding table, flour dust, bamboo shelves, a stool in front. Table top empty. | 61, 62, 63, 64, 65 |
| BG-12 | MUST | Sepia memory lane, warm golden backlight, soft haze, tall. No figure. | 54 |
| BG-13 | MUST | Paper-cut storybook frame: sepia paper texture, vermilion border, torn-edge overlay for the page rip, tall. | 41, 47 |
| BG-14 | MUST | Paper-cut dawn, wide plate: layered pagoda silhouettes, empty round slot for a paper sun, a rooster slot, drifting-petal layer. | 42 |
| BG-15 | MUST | Paper-cut 1871 shop: bedroom with a paper bed + shopfront, tall. Sepia and vermilion. | 43, 44 |
| BG-16 | MUST | Paper-cut kitchen worktable, macro background, tall. | 45, 46 |
| BG-17 | MUST | Journal page with an ink-wash map of the old road, no text, warm paper, tall; the dotted route is drawn by the engine. Also reused for the final route south. | 7, 66 |
| BG-18 | nice | Paper-cut fun-fact card background with pagoda silhouettes (existing Canva asset MAHb0NdiCnA can be reused). | 51, 52, 53 |
| BG-19 | MUST | Ink-wash old-road landscape strip, wide pan plate (3x): dunes, mountains and coast along a dotted-route path, paper-sun slot (the caravan walks across it). | 8, 9 |
| BG-20 | MUST | Metro carriage interior, tall: seats, hand straps, window, plain, no passengers. | 10 |

### 3.3 The Boy


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| BO-01 | MUST | Boy turnaround sheet: front, 3/4 left, profile, 3/4 back, back (full body, hat, ribbon, bag). | all (reference sheet) |
| BO-02 | MUST | Boy head kit, blank face: front, 3/4, profile, back; hat, chin ribbon, hair fringe as SEPARATE layers (hat gets knocked by steam). | 4 |
| BO-03 | MUST | Boy expression sheet (10 heads): neutral, host grin, flat deadpan to lens, shock, worried, awe, dry amused, eyes-closed smile, mischief, tender. | 2, 18, 20, 29, 37, 40, 49, 50, 53, 58, 64, 68 |
| BO-04 | MUST | Boy mouth set (8): closed, small smile, A, O, E, big open, gasp, laugh. | 2, 20, 51, 68 |
| BO-05 | MUST | Boy hand set (13): present palm, point, fist, finger-up, two-finger director, finger snap, spoon grip, chopstick grip, chopstick-MIC grip, journal hold, flat on table, one-finger steady, card-sliding finger. | 4, 5, 11, 12, 22, 32, 40 |
| BO-06 | MUST | Pose: host stance facing the lens, chopsticks held like a microphone (cold open, host walk). | 2, 4, 12, 15, 17, 18, 29, 51 |
| BO-07 | MUST | Pose: host present, arm sweeps out, palm up, body angled. | 51 |
| BO-08 | MUST | Pose: points right with the mic arm fully extended, head still facing the lens. | 17 |
| BO-09 | MUST | Pose: snaps fingers (mic in the other hand) with a director's two-finger raise. | 5, 6 |
| BO-10 | MUST | Pose: deadpan side-glance to lens, 3/4 body, one eyebrow up. | 20, 37, 39, 49, 50, 53, 64 |
| BO-11 | MUST | Pose: seated at the table, spoon in hand, demo posture (Safety Segment). | 31 |
| BO-12 | MUST | Pose: eyes forward, one arm reaching out with a single finger on the top steamer (steadying the tower). | 38 |
| BO-13 | MUST | Pose: sitting on the bridge from behind, feet dangling, journal on knees. | 57 |
| BO-14 | MUST | Pose: hero low angle, hand on hat brim, confident (Guangzhou push-in). | 67 |
| BO-15 | MUST | Pose: mic swung out like a barrier arm, leaning in, mouth wide. | 22 |
| BO-17 | MUST | Pose: seated on the metro seat, journal on his knees, calm. | 10 |
| BO-20 | MUST | Bust: smile with eyes closed (Dad memory, 'Co-host.' beat). | 56, 58, 68, 69 |
| BO-21 | MUST | Pose: turns a journal page toward the camera, one hand lifting the page. | 41 |
| BO-22 | MUST | Cycle: BACKWARD walk facing the lens, 8 frames, hat bouncing, mic in hand. | 15, 16 |
| BO-24 | MUST | Pose: standing on the pier seen from behind, robe and ribbon blowing. | 13 |

### 3.4 The Uncle


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| UN-01 | MUST | Uncle turnaround sheet: front, 3/4 left, profile, 3/4 back, back (round silhouette and wide belt readable in every view). | all (reference sheet) |
| UN-02 | MUST | Uncle head kit, blank face: front, 3/4, profile, back; mustache as a SEPARATE layer (it stands up like antennae). | 19, 24 |
| UN-03 | MUST | Uncle expression sheet (14 heads): hungry-neutral, hover balloon (purple-red, puffed), dreamy asleep, smug sniff, heart-spiral eyes, eager, shock, burned-red, humbled tiny, sweat-nervous, bliss, eyes-shine (tender), proud hero grin, deadpan thumbs-up. | 3, 19, 23, 25, 28, 36, 40, 49, 52, 53, 59, 64 |
| UN-04 | MUST | Uncle mouth set (12): closed, A, O, E, big open, gasp, laugh, puffed cheeks, tongue out, chewing, mouth-full, whistle-O. | 4, 24, 39, 59 |
| UN-05 | MUST | Uncle eye variants (7): twitch dots, spiral to heart-steam, streaming tears, half-lid, bulging, happy arcs, asleep with drool. | 19, 25, 36 |
| UN-06 | MUST | Uncle hand set (9): chopstick grip, spoon hold, two fingers up, reach, holds journal as a fan, holds 10/10 card, thumbs-up, ice pack hold, waves. | 22, 40, 52 |
| UN-09 | MUST | Pose: towed by the steam ribbon, feet dangling, eyes closed, nose pointing forward, sleepy smile (also usable in a profile view). | 16, 17, 18 |
| UN-10 | MUST | Pose: skid-to-stop, steam leaking from one ear. | 28 |
| UN-11 | MUST | Pose: low angle, lifts a dumpling on chopsticks like a trophy, chest puffed ("For science!"). | 23 |
| UN-12 | MUST | Pose: rocket-up, arms out, mustache straight up, tongue out, both ears blasting steam. | 27 |
| UN-13 | MUST | Pose: humbled, hunched, tongue out and fanning. | 28, 63 |
| UN-14 | MUST | Pose: seated stiff and upright at the table, ice pack on cheek, hands folded like a student. | 31 |
| UN-15 | MUST | Pose: leaning in, nose almost touching the spoon, eyes crossed, sweating. | 35, 38 |
| UN-16 | MUST | Pose: hands on tummy, mid-growl (Low angle). | 38 |
| UN-17 | MUST | Pose: bliss swoon, eyes closed, head tilted. | 39 |
| UN-18 | MUST | Pose: sitting on the bridge from behind, feet dangling, spoon in hand. | 57 |
| UN-19 | MUST | Pose: swallows a dumpling whole, then fans his tongue with the journal. | 60 |
| UN-24 | MUST | Pose: burned silhouette base for the impact frame (stiff, cheeks puffed, bulging eyes, leaning back). | 26 |
| UN-25 | MUST | Pose: hovering a meter above the ground, balloon-face, slowly rotating (front, 3/4, back), both ears whistling like kettles. | 2, 3, 4, 6 |
| UN-26 | MUST | Pose: asleep on a camel, hugging a steamer basket, drooling (rides the camel cycle CM-04). | 8 |
| UN-27 | MUST | Pose: snoring seated on the metro seat, head back. | 10 |
| UN-28 | MUST | Pose: dropping in from above and sitting on the letter O of the title banner. | 12 |
| UN-29 | MUST | Pose: whirl-past smear pose (3 frames), ears jetting steam. | 5 |
| UN-30 | MUST | Pose: the real-life hero pose, napkin for a cape, soup spoon for a sword, one ear still faintly steaming (low angle). | 48, 49 |
| UN-31 | MUST | Cycle: runs in a circle / orbits fanning his tongue, 6 frames. | 27, 29 |
| UN-32 | MUST | Pose: seated with his tongue in an ice bucket, thumbs-up (sting). | 69 |
| UN-34 | MUST | Pose: standing on the pier seen from behind, robe blowing. | 13 |

### 3.5 Grandma


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| GM-01 | MUST | Grandma turnaround: front, 3/4, side (small, round, apron, gray bun). | all (reference sheet) |
| GM-02 | MUST | Grandma head kit + 6 expressions: warm smile, focused fold, freeze-stare, delighted, knowing smile, mild surprise. | 62, 63, 65 |
| GM-03 | MUST | Grandma mouth set (6). | 63, 65 |
| GM-04 | MUST | Grandma hand set: folding cycle A-D (4 frames), touch hat brim, point south, point at the stool, hold dumpling. | 21, 61 |
| GM-05 | MUST | Pose: behind the stall, bust-up, arms free for blurred folding. | 21, 61 |
| GM-06 | MUST | Pose: freeze-stare at the hat. | 62 |
| GM-07 | MUST | Cycle: hurry-walk, small quick steps, 6 frames, 3/4. | 62 |
| GM-08 | MUST | Poses: touches the hat brim; points at the stool; points far south (3 poses). | 62, 63, 65 |

### 3.6 Dad


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| DD-01 | MUST | Dad: sepia silhouette from behind, tall, conical hat, spoon in hand (2 states: spoon raised, spoon lowered); hat ribbon as SEPARATE flutter layer. Never a face. | 54 |

### 3.6b The Camel (silent cameo, every episode)
Calm, unimpressed, soft and round like the rest of the cast; it never speaks.

| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| CM-01 | MUST | Camel turnaround: front, 3/4, side. Calm, unimpressed, round and soft like the rest of the cast. | all (reference sheet) |
| CM-02 | MUST | Camel head kit + expressions: stare-to-lens (default), blink, glance, nod; head turn front / 3/4 / profile. | 8, 14, 66 |
| CM-03 | MUST | Camel poses: stares into the lens (front), stands in the metro holding a hand strap, steps off the train (6-frame walk cycle), looks south (3/4), sits beside Uncle for the sting. | 10, 14, 66, 69 |
| CM-04 | MUST | Colour camel walk cycle with a saddle for the sleeping Uncle (side view, 6 frames). | 8 |

### 3.7 Legend cast (paper-cut / ink-wash)
Same round, soft shapes in a paper-cut look (sepia and vermilion). The Boy and Uncle appear in the legend only through a paper/ink filter of their normal assets, except the Uncle-faced shop owner, which is new art.

| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| LG-01 | MUST | Paper-cut shop owner with UNCLE'S FACE and thin mustache: rising from a paper bed; hero pose with a rolling pin raised like a sword; separate paper-cape flutter layer. | 43, 44 |
| LG-02 | MUST | Paper-cut dough stages (3): round, half-fold, pleated bun, plus a paper-thin skin glow variant. | 45, 46 |
| LG-03 | MUST | Ink-wash caravan: 4 camels (the last distinct, with a rider slot) walking on stepped fours, side view; paper-cut and ink-wash flavor. | 8 |
| LG-04 | MUST | Paper-cut set: round paper sun, paper rooster (2 frames), 3 cloud layers. | 8, 42 |
| LG-05 | MUST | Paper-cut sprites: glowing jelly cube, tiny paper steam dragon (3-frame loop). | 46 |
| LG-06 | MUST | Ink silhouettes pair: camel line and metro-car line, SAME silhouette rhythm and spacing, for the match cut. | 9 |

### 3.8 Props


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| PR-01 | MUST | Steamer basket: closed, lid-off, lid mid-lift (3 states). | 21 |
| PR-02 | MUST | Tower of 3 steamers, tiers as separate layers (rattle and wobble). | 2, 8, 21, 31, 38 |
| PR-03 | MUST | Xiaolongbao set: whole top-down, whole side, bitten, pierced with a soup trickle, golden-glow. | 21, 23, 24, 32, 33, 34, 52, 56, 57 |
| PR-04 | MUST | Soup spoon: empty, with dumpling, with soup pool. | 33, 34, 36, 39, 48, 57 |
| PR-05 | MUST | Chopsticks: closed, pinching, holding a dumpling, held as a mic (Boy). | 22, 23, 32, 34 |
| PR-06 | MUST | Journal: closed, open blank, page-one page, torn-stub page, handwriting-scribble page (no legible text), glowing-page state. | 7, 10, 11, 41, 54, 55, 60, 66 |
| PR-07 | MUST | Giant cartoon clock face with separate hands. | 35 |
| PR-10 | MUST | Metro carriage exterior, side view, doors closed and open, 2-frame cycle. | 9, 14 |
| PR-13 | MUST | Grandma's tray: wrappers, filling bowl, folded dumplings. | 61 |
| PR-14 | MUST | Boy's conical hat as a standalone sprite (brim, ribbon). | 15, 62 |
| PR-16 | nice | River boat silhouette with a small funnel. | 13 |
| PR-17 | MUST | Ice pack (cartoon, blue, round) and ice bucket (2 props). | 31, 69 |
| PR-18 | MUST | Stools: one pair for the table (BG-09), one for Grandma's stall. | 31, 63 |
| PR-19 | nice | Lanterns, 2 sizes, 3 swing frames. | 15 |

### 3.9 FX sprites (hand-drawn)


| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| FX-01 | MUST | Steam puff sheet: soft cream puffs, 6 frames, 3 sizes. | 1, 2, 6, 21, 34, 36, 54, 56 |
| FX-02 | MUST | Steam ribbon: long curly ribbon, 4-frame undulation, tightens into a leash. | 16, 17, 18 |
| FX-03 | MUST | Ear-steam jets: kettle whistle puffs + long train-whistle plume, 4-frame loops. | 3, 4, 5, 27 |
| FX-04 | MUST | Sweat drops (3 sizes), tick marks, tear streams. | 25, 35, 38, 64 |
| FX-05 | MUST | Hearts, heart-shaped steam and sparkle stars set. | 19, 39, 59 |
| FX-06 | MUST | Impact starburst + ring shapes (3 variants, black and white). | 26 |
| FX-07 | MUST | Paper-tear transition: a page ripping from the center, 6 frames (seal tear and scroll rip). | 41 |
| FX-08 | MUST | Dust puff, 5 frames. | 7, 27 |
| FX-09 | MUST | Film-reel rewind stripes + sprocket sweep, 6 frames (rewind transition). | 6 |
| FX-10 | MUST | Paper petals / leaves sheet (legend drift). | 39, 41, 42, 44 |
| FX-11 | MUST | Tiny toot puffs (3 sizes) and a tongue-steam wisp. | 28, 60, 69 |

### 3.9b Graphic templates (paper-cut / ink stamps, text added in the editor)
Palette #D9480F, #ECC66A, #FFFAF0, #3B2A1A. Blank frames only; no text inside the art.

| ID | Pri | What to generate | Used in shots |
|---|---|---|---|
| GR-01 | MUST | Lower-third tab, TV style, paper-cut (text 'UNCLE / co-host (self-appointed)' then '(approved)' added in editor). | 4, 59 |
| GR-02 | MUST | Title banner: paper-cut scroll banner that unrolls, with a large round letter slot the Uncle sits on. | 12 |
| GR-03 | MUST | Red LEGEND SAYS seal stamp, blank, plus a small asterisk tag for '*competing versions exist'. | 41, 50 |
| GR-04 | MUST | Intermission card frame (retro TV test-card feel, palette colors). | 29 |
| GR-05 | MUST | SAFETY SEGMENT sign frame with a small print strip. | 30 |
| GR-06 | MUST | Step word-card frame (LIFT / SPOON / TINY HOLE / WAIT), 1 frame, reused 4 times. | 32, 33, 34, 35 |
| GR-07 | MUST | Hand-drawn rating card, blank, for '10/10'. | 40 |
| GR-08 | MUST | Fun-fact card frame + scroll banner for 'XIAOLONGBAO = little basket bun' (1 shared frame set). | 47, 51 |
| GR-09 | MUST | End card frame: 'NEXT: GUANGZHOU'. | 69 |

### 3.10 Built in the editor (no art needed)
Speed lines, impact flashes, camera shake, grain, vignette, light rays, particles, captions (approved style, every spoken line), all text on the paper-cut graphic templates GR-01 to GR-09 (lower-third, banner, seal, intermission, safety, word cards, 10/10, fact card, end card), route line draw, handwriting reveal, sound-word animated text, paper filter and 8 fps stepping for the legend.

### 3.11 Reuse for the next episodes
The Boy, Uncle and Grandma rigs, the steamer, spoon, chopsticks and journal sets, the map page, the Camel, the TV graphic templates, the paper-cut frame and the FX sprites carry over to Episodes 2-3 unchanged; only plates and a few guest props change. The China arc (Guangzhou, Beijing) should therefore cost far less than Episode 1.

---

## 4. Hero moments (full, fluid animation)

These 8 moments carry the "this is real animation" feeling. They are the first candidates for an AI image-to-video tool (the Canva video quota returns 2026-12-16) if free hand-keyed or rig-based work cannot reach the quality. Everything else in the breakdown is built from rigs, keyframes, cycles and camera.

Rules for using AI video clips:
- Feed the **exact approved still** (plate with characters composited, or the pose) as first frame, and where the tool allows it a last frame; never text-only.
- Keep the clip short (2-4 s), one action, camera notes in the prompt. Cut the clip in the editor and layer our captions, sounds and impact frames on top.
- Any clip where the hat, belt, mustache or round shapes drift is rejected and replaced by the rig/keyframe version.

### H1. Cold open: the floating, whistling Uncle behind the calm host (shots 2-5, v4 beats 2-4, 6.0 s in the cut)
- **Why:** The hook has to look like a real animated shot from frame 1: a levitating, rotating balloon-faced Uncle with kettle ears, steamers rattling, the Boy dead calm and tapping his mic.
- **Frames:** First frame: Boy centered with mic, Uncle blurred and hovering behind. Last frame: Uncle whirling past the lens, ears jetting (UN-29).
- **Prompt skeleton:** Cartoon picture-book style: a calm boy in a conical leaf hat holds chopsticks like a microphone and speaks to the camera in a small dumpling shop; behind him a big round bald man with a thin mustache floats a meter above the floor, face purple-red and puffed like a balloon, slowly rotating, steam whistling from both ears like kettles; bamboo steamers rattle; hat ribbon flutters; slow push-in; 5 s.
- **Camera:** MS push-in, whip at the end
- **Cut value:** the shot window is 6.0 s; request a clip of 6 s and trim.

### H2. Match cut: ink-wash camel caravan becomes a metro line (shots 8-10, v4 beats 7-8, 5.2 s in the cut)
- **Why:** Defines the show's look in one image: the old road turning into today. Needs a clean silhouette morph and the sleeping Uncle on the last camel.
- **Frames:** First: stepped paper-cut caravan on the dotted route, last camel with Uncle asleep, camel looking at the lens. Last: metro carriage interior, camel holding a hand strap, Boy and Uncle seated.
- **Prompt skeleton:** Ink-wash and paper-cut animation on an old map: a line of camels walks along a dotted red route under a rising paper sun, the last camel carries a sleeping round man hugging a bamboo steamer; the line of camels morphs into a line of metro cars gliding along the same route, then cut into the carriage where a calm camel holds a hand strap; stepped 8 fps feel; 6 s.
- **Camera:** ELS pan to MS interior
- **Cut value:** the shot window is 5.2 s; request a clip of 6 s and trim.

### H3. The backward-walk host tour with the towed Uncle (shots 15-18, v4 beats 13-15, 9.2 s in the cut)
- **Why:** The signature 'show' shot: the Boy walks backward toward the lens while a canal town slides by and Uncle floats past on a steam leash. Full-body walking, parallax and a long take; the hardest thing to fake with a flat rig.
- **Frames:** First: Boy mid-stride, mic raised, canal lane behind. Last: Boy paused, mic tilted back, Uncle towed behind him.
- **Prompt skeleton:** A boy in a conical leaf hat walks backward toward the camera along a golden-hour canal lane with red lanterns, talking to the lens with a chopstick microphone; behind him a big round man drifts past, feet dangling, eyes closed, towed by a ribbon of steam like a balloon on a leash; soft children's picture-book 2D style; 6 s.
- **Camera:** MS tracking, steady
- **Cut value:** the shot window is 9.2 s; request a clip of 10 s and trim.

### H4. The burn: dumpling, silence, impact, toot (shots 24-27, v4 beats 21-23, 3.8 s in the cut)
- **Why:** The comic centerpiece. Needs the smear, the two impact frames and a full-body rocket-up with ear steam; the rest of the beat stays keyframed.
- **Frames:** First: UN-11 trophy lift (or the pleated-dumpling ECU). Last: UN-12 mid-rocket with ear plumes at full length. Impact frames added in the editor.
- **Prompt skeleton:** A big round bald man swallows a whole dumpling; his cheeks puff to a ball, one eye twitches, a sweat drop swells, then white flash; he rockets two meters into the air with long train-whistle steam from both ears, mustache standing straight up, tongue out, lands and runs in a circle; picture-book 2D style; 4 s.
- **Camera:** ECU to WS
- **Cut value:** the shot window is 3.8 s; request a clip of 4 s and trim.

### H5. Tiny hole: the steam dragon macro (shot 34, v4 beat 29, 1.0 s in the cut)
- **Why:** The educational beat must be clear and appetizing; liquid and steam are hard in a rig.
- **Frames:** First: dumpling on the spoon. Last: pierced dumpling, steam spiraling like a tiny dragon.
- **Prompt skeleton:** Extreme close-up of a soup dumpling on a ceramic spoon, a chopstick tip pokes a tiny hole, a thin ribbon of steam spirals up like a miniature dragon, warm window light, soft cartoon rendering; 2 s.
- **Camera:** ECU macro
- **Cut value:** the shot window is 1.0 s; request a clip of 2 s and trim.

### H6. Tummy growl, wobbling tower, one calm finger (shot 38, v4 beat 32, 2.0 s in the cut)
- **Why:** Secondary-motion chain with a deadpan payoff; great if the physics reads.
- **Frames:** First: UN-16 hands on tummy, tower upright. Last: BO-12 finger on the top steamer, tower still.
- **Prompt skeleton:** Low angle: a big round man whispers to a dumpling, his stomach growls so loudly a tower of three bamboo steamers wobbles and slides; a small boy in a conical leaf hat steadies the top with one finger without looking; cartoon picture-book style; 3 s.
- **Camera:** LA
- **Cut value:** the shot window is 2.0 s; request a clip of 2 s and trim.

### H7. Legend says: seal, tear, Uncle-faced hero, jelly and paper dragon (shots 41-46, v4 beats 35-38, 12.8 s in the cut)
- **Why:** The whole 'different medium' transition and the legend payoff as one flowing paper-cut sequence. The change of frame rate is the style statement.
- **Frames:** First: Boy turning the journal page, red seal. Last: paper-cut macro, glowing jelly cube inside a pleated bun, tiny paper steam dragon.
- **Prompt skeleton:** Paper-cut storybook animation, sepia and vermilion, stepped 8 fps: a red seal stamps, the page tears open into a world of layered paper pagodas, a paper rooster and a rising paper sun; a paper-cut shop owner with a thin mustache rises from a paper bed and strikes a hero pose with a rolling pin like a sword, paper cape fluttering; then dough folds into a pleated bun, a jelly cube drops in and steam coils into a tiny paper dragon; 10 s (or three 3-4 s clips).
- **Camera:** paper-cut pan to macro
- **Cut value:** the shot window is 12.8 s; request a clip of 13 s and trim.

### H8. Grandma freezes: hands blur, snap zoom to the hat (shots 61-62, v4 beat 50, 2.4 s in the cut)
- **Why:** Speed-to-stillness plus anime snap zooms sells the cliffhanger. Needs very fast hands and a hard stop.
- **Frames:** First: GM-05 folding, hands blurred. Last: GM-06 frozen, eyes on the lens, then the brim of the hat.
- **Prompt skeleton:** A tiny grandmother folds dumplings with blurred, lightning-fast hands, then freezes mid-fold; fast snap zooms to her eyes, to a conical hat brim, to her eyes again; she hurries over and touches the brim and smiles; soft cartoon style, warm dusk light; 3 s.
- **Camera:** ECU to MCU snap zooms
- **Cut value:** the shot window is 2.4 s; request a clip of 3 s and trim.

Combined span of the hero moments in the cut: about 42 s of 125 s (about 34%). Free route first: if the video engineer's rig/keyframe pipeline can do H1, H3, H4, H6 and H8 well, paid clips shrink to H2 and H7 (the two most "different medium" moments), and could be skipped altogether. The sting (beat 56), the intermission and the staring contest need no AI.

---

## 5. Dependencies and open points
1. **Copywriter:** the three densest beats (see section 2 notes) run above 3.3 words per second; trim or accept a small stretch. Beat 41 ("Legend. That's historian for 'please don't quote me.'") and the asterisk card are the factual safety net: keep them. Facts to re-check when `production/v4/content-research.md` lands: the 1871 legend, the name "xiaolong mantou", the Silk Roads wording, Nanxiang in Jiading District.
2. **Video engineer:** confirm which of R, K, C, H are possible in the free route; supply a rig spec for the part lists in section 3 (Boy, Uncle, Grandma, Camel); needs `scroll` music mood (plucked strings), stepped-8-fps option for the legend, mask reveal, circle/silhouette morph, hit-stop and impact frames, film-reel and paper-tear transitions, animated sound-word text.
3. **Art team (Canva):** use section 3 in one pass in the order from 3.1; mark rejected assets by ID. Note the new characters: the Camel and the paper-cut Uncle-faced shop owner.
4. **Creator decisions:** approve the register split (host / gag / legend / heart), the TV-graphics style (paper-cut stamps), the Uncle-faced legend hero, and whether paid AI clips are used only for H2 and H7.
5. **Anonymity and safety:** no personal names or accounts anywhere; no public posting; all art and text English; no real text on any plate (signs and cards are blank); the burn stays safe (ice pack next shot, safe method in full).
