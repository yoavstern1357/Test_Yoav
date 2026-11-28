# Episode 02 V5: "The Stool Nobody Sits On" (1-minute episode; China arc, part 2 of 4: the hat, Dad's book, Guangzhou)

**Length:** **1:09.5 planned** (hard max 1:15, target about 1:00; the final length is set by the voices at natural speed) · hook first, then a 1.0 s title hit · vertical 9:16 first, 16:9 re-framed where possible · **Location:** the same stall in Nanxiang, Shanghai · **Dumpling:** Xiaolongbao (this episode is about the people and the patience, not a new dumpling)
**Clips:** **23 AI clips** (2.0-3.5 s, START + END keyframes) + 1 CODE clip (title hit). **113 spoken words**, **no legend scroll** (it was in Episode 1), one **Dad beat of 6.0 s** (C12-C13), "For dumpling research!" once (volcanic), last spoken line "Dad was right...", camel sting as the final clip.
**Rules:** `production/v4/PRODUCTION-BIBLE.md` (v5 DECISIONS at the end override everything above them), `production/v4/shot-rules.md` (every AI clip obeys it; `tools/episode_maker/paper/lint_shotlist.py` enforces it), `production/v4/comedy-style.md`.
**Status:** DRAFT for the creator. The script is shown to the creator in Hebrew in chat and approved there BEFORE any production.
**Standalone test:** a viewer who skips Episode 1 still gets (0-3 s) a funny, curious hook (the Uncle frozen mid-sit, a spoon on his forehead, "Nobody sits on that stool. Nobody."), the host, the place, the book, a patience lesson with a payoff, and a hook to Guangzhou. Anything from Episode 1 is re-told in one line.
**Voices:** `boy` (WARM, curious, soft about Dad), `uncle` (operatic: GRAND, TINY), `grandma` (brisk, flat, kind, never the joke; softens at the hat), `narrator` is not used in this episode.
**Characters (v5 lock):** Boy about 7: conical leaf hat with orange chin ribbon, faded indigo village tunic, rolled hemp trousers, orange cloth sash, straw sandals. Uncle: big, fully bald round head, thin long curled-tip black mustache, thick brows, earth-brown linen jacket with mandarin collar, wide orange sash, white towel on one shoulder, charcoal trousers, straw sandals, **never a hat** (the travel bundle sits on his back, never on his head). Grandma: white-grey bun with two crossed wooden pins, jade-green jacket, cream apron, orange sash. Dad: a sepia silhouette from behind, never a face, never named in a prompt.
**Story rules (v5):** NO secret for the Uncle (no torn page, no quarrel). Dad simply went away and left his book; the Boy believes the answers are in it. Said once, gently (C12), never blunt, and **no jokes within 10 s of the Dad beat** (last joke 0:24.5, beat 0:35.0-0:41.0, next joke 0:51.5).
**Series position:** Episode 1 (`scripts/episode-01-v5.md`) ends with the Boy finding Dad's doodle on the stool. Episode 2 opens on that stool.

## Production order (voice-first, do not reorder)
0. **Creator gate:** the Hebrew reading copy is approved in chat. Nothing below starts before that.
1. **Lint:** `python3 tools/episode_maker/paper/lint_shotlist.py scripts/episode-02-v5.md` must print `RESULT: PASS`.
2. **Final voices at natural speed** (Qwen3-TTS, 2-3 takes per line); no `voice_speed`. Cut words, never speed up. The Dad beat is recorded as the quietest, slowest takes.
3. **Word timestamps** (forced alignment, CPU).
4. **Animatic** from the START stills + voices (creator gate). Check the joke-free window: last joke to the Dad beat and Dad beat to next joke are both >= 10 s.
5. **Stills** (one clean sheet per visible character, head count in the prompt, END made as an edit of START; `tools/episode_maker/qc_stills.py --script scripts/episode-02-v5.md`). The book page has no readable writing; only brush strokes and a sketch.
6. **Clips at exact length**, prompts compiled from the fields below.
7. **QC gate:** `tools/episode_maker/qc_clips.py` (with `--script scripts/episode-02-v5.md --spec ...`); TRUNC, SLOWMO, FREEZE, DUP?, DUP_IN_STILL?, MORPH_RISK, TEXT, FACE_SMEAR must be 0; re-roll failed ids (seed + 1, max 2).
8. Mouths, EDIT effects, captions, mix (-14 LUFS / -1 dBTP), both orientations.

## Spine (bible 60-s structure, Episode 2 version)
| Bible slot | Here | Clips |
|---|---|---|
| Hook 0-3 s | 0:00.0 The Uncle frozen mid-sit, a wooden spoon on his forehead: "Nobody sits on that stool. Nobody." | C01 |
| Title hit <= 2 s | 0:03.0 logo + song sting (1.0 s) | K01 |
| Host + place + book | 0:04.0 "Welcome to Nanxiang. He's... stuck."; "I follow my dad's dumpling book."; the Uncle: "It's research."; "Grandma, why can't anyone sit there?" | C02-C05 |
| Learning beat | 0:16.5 Grandma folds: "The waiting seat. Eighteen folds, by hand."; the Uncle: "I'll... perish."; Grandma: "Then perish quietly." | C06-C08 |
| Lead-in (joke-free) | 0:25.0 Grandma sees the hat; "A man sat there once. Same hat." | C09-C11 |
| **Dad beat (6.0 s, no jokes)** | 0:35.0 sepia silhouette on the stool, "Dad went away. His book stayed."; page one of the book: "Be patient." | C12-C13 |
| Aftermath (joke-free) | 0:41.0 "He waited all afternoon for one dumpling."; "The answers are in his book."; the safe way: tiny hole, cool, sip | C14-C16 |
| Payoff gag | 0:51.0 the Uncle's nine seconds of patience | C17-C18 |
| Next-episode hook + ending | 0:57.0 "Then he went south. To Guangzhou."; "FOR DUMPLING RESEARCH!"; "He's already packed. Of course."; "Dad was right..."; camel sting | C19-C23 |

## Laugh map (at least 2 in every 15 s window, except around the Dad beat; V = verbal, S = visual)
| Window | Beats |
|---|---|
| 0:00-0:15 | 0:01.2 S the Uncle frozen mid-bend, sweat drop; 0:02.0 V "Nobody sits on that stool. Nobody."; 0:06.0 V "He's... stuck." over the blurred frozen Uncle; 0:12.0 V "I'm not sitting. It's research." |
| 0:15-0:30 | 0:21.5 V "Eighteen folds? I'll... perish." + violin sting; 0:24.0 V "Then perish quietly." (**last joke before the Dad beat**) |
| 0:25-0:51 | **Joke-free by design:** lead-in 0:25-0:35, Dad beat 0:35-0:41 (C12-C13), aftermath 0:41-0:51. The safe-sip macro (C16) has the badge but no gag. |
| 0:45-1:00 | 0:52.5 V "I've been patient for NINE seconds." + S trembling mustache (**first joke after the Dad beat, 10.0 s later**); 0:55.5 V "It was four. I counted." |
| 1:00-1:09.5 | 1:00.0 V/S "FOR DUMPLING RESEARCH!" with aura and fleeing birds; 1:03.0 V "He's already packed. Of course."; 1:07.5 S the camel sting |

## How to read the shot list
Same columns and rules as `scripts/episode-01-v4.5.md`. This episode has one new convention: the Dad beat and its joke-free window are marked in the EDIT column of C09-C16.

## Shot list

### A. Hook, title, host and the stool (0:00.0-0:16.5)
| Clip | Dur | Start | Method | Faces | Shot | START keyframe | END keyframe | ACTION + facial beats | VOICE | Mouth | Motion | EDIT | SFX | Caption |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C01 | 3.0 | 0:00.0 | AI | 1: Uncle (+hands: Grandma) | CU · face 45% | Close-up of the Uncle, completely bald with a thin curled mustache and an earth-brown linen jacket, frozen bent halfway down toward a small worn wooden stool, eyes wide and guilty; the tip of a wooden spoon held by an old woman's floury hand is pressed against his forehead; only the hand is visible; an old canal lane softly blurred behind him, morning light. | Same framing and light; change only: one bead of sweat on his bald head and his eyes slid sideways to the spoon. | He freezes bent over the stool; his eyes slide slowly to the spoon pressed against his forehead. | GRANDMA (off) [flat, absolute]: “Nobody sits on that stool. Nobody.” | closed | low | Wooden "tock" on the spoon touch at 0.0 s; sweat-drop sprite 1.2-3.0 s; camera bump on the second "Nobody"; slow digital push 1.00 to 1.06. | wooden tock, canal water, tiny gulp | BOTTOM (face and spoon in the upper two thirds) |
| K01 | 1.0 | 0:03.0 | CODE | 0 | full | Cream paper plate with brush-ink texture. | The show logo stamped in the centre, one curl of steam rising from it. | Title hit: the logo stamps in on the opening-song sting, ink splash, steam curl. | — | closed | medium | "THE DUMPLING BOY" logo (code card) with the small tag "#2"; 1.0 s cut of the song sting; hard cut out on the downbeat. | song sting, ink splat | none (logo centre) |
| C02 | 3.5 | 0:04.0 | AI | 2: Boy, Uncle | CU · face 35% | Close-up of the Boy in his conical leaf hat with an orange chin ribbon facing the lens with calm host poise; behind him, soft and out of focus, the Uncle still frozen bent halfway down toward a small wooden stool. | Same framing; change only: the Boy's eyebrow raised and the out-of-focus Uncle behind him has not moved at all. | The Boy gives the lens one calm, deadpan look; behind him, blurred, the Uncle stays frozen mid-bend. | BOY (on) [calm host, deadpan]: “Welcome to Nanxiang. He's... stuck.” | overlay | low | Place card "NANXIANG · SHANGHAI, CHINA" ink-blooms in the TOP band 0.3-2.8 s; 8-frame look-to-lens hold on the last word. | canal water, bike bell, comic plink | BOTTOM (Boy's face upper half) |
| C03 | 3.0 | 0:07.5 | AI | 1: Boy | MCU · face 30% | Medium close-up of the Boy at a small steaming food stall in an old canal town, holding a small worn leather book tied with a string in both hands, a warm smile; bamboo steamers softly blurred behind him, warm morning light. | Same framing and light; change only: he lifts the book a little higher toward the lens. | A warm host smile; he lifts the little book toward the lens, proud and a bit shy. | BOY (on) [warm, a little proud]: “I follow my dad's dumpling book.” | overlay | low | Camera bump on "dumpling book"; the book gets a soft glow outline 1.2-2.4 s (code). | soft chopstick tap, steamer hiss | BOTTOM |
| C04 | 3.0 | 0:10.5 | AI | 1: Uncle | CU · face 42% | Close-up of the Uncle, completely bald with a thin curled mustache, bent halfway down, a sly innocent face, one eyebrow raised, lips pressed in a thin hopeful smile. | Same framing; change only: his sly smile broadened and his eyes darted sideways. | He keeps the innocent face; his eyes dart sideways to check he is not watched. | UNCLE (on) [sly whisper, thoroughly unconvincing]: “I'm not sitting. It's research.” | overlay | low | Tiny sweat-drop sprite at the end; creak sound on the stool. | stool creak, comic plink | BOTTOM |
| C05 | 3.0 | 0:13.5 | AI | 1: Boy | CU · face 38% | Close-up of the Boy at the stall, turned toward someone just beside the lens, curious, eyebrows lifted, steam drifting behind him. | Same framing; change only: his head tilted a little and his lips parted to ask. | He tilts his head and asks, openly curious. | BOY (on) [warm, genuinely curious]: “Grandma, why can't anyone sit there?” | overlay | low | none | stall ambience | BOTTOM |

### B. Patience: eighteen folds (0:16.5-0:25.0)
| Clip | Dur | Start | Method | Faces | Shot | START keyframe | END keyframe | ACTION + facial beats | VOICE | Mouth | Motion | EDIT | SFX | Caption |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C06 | 3.5 | 0:16.5 | AI | 0 (+hands: Grandma) | MACRO | Macro in warm light: an old woman's floury hands hold a round dough wrapper around a small ball of pork filling, her thumb and finger pinching the edge into the first pleat; only the hands are visible. | Same framing and light; change only: a ring of fine pleats now circles the dumpling, closed at the top. | Her fingers pleat the edge round, one small fold after another, steady and unhurried. | GRANDMA (off) [calm, unhurried]: “The waiting seat. Eighteen folds, by hand.” | closed | low | Fold counter ticks 1 to 18 in the TOP band in step with the folds (code); slow digital push 1.00 to 1.05. | soft dough squeeze, ambient steam | BOTTOM (counter top; hands centre) |
| C07 | 3.0 | 0:20.0 | AI | 1: Uncle | CU · face 44% | Close-up of the Uncle, completely bald with a thin curled mustache, slumped on a low wooden stool, his chin on his fist, wet dramatic eyes fixed on the lens. | Same framing; change only: his head tipped back and his eyes shut in theatrical agony. | He tips his head back, eyes shut, in slow theatrical agony. | UNCLE (on) [operatic, tiny, fading]: “Eighteen folds? I'll... perish.” | overlay | low | Flat sweat-drop sprite; faint violin sting. | violin sting, wheeze | BOTTOM |
| C08 | 2.0 | 0:23.0 | AI | 1: Grandma | MCU · face 28% | Medium close-up of Grandma, her white-grey bun held by two crossed wooden pins, behind her counter, pleating a dumpling in her floury fingers, eyes down, a flat calm face. | Same framing; change only: her eyes lifted to the lens and one eyebrow raised a millimeter. | Her eyes rise slowly to the lens; one eyebrow lifts a hair. | GRANDMA (on) [bone dry]: “Then perish quietly.” | overlay | low | Tiny 4-frame camera bump on "quietly"; last laugh of the episode before the Dad beat. | steamer lids, comic ding | BOTTOM |

### C. The hat, Dad, the book (0:25.0-0:41.0)
| Clip | Dur | Start | Method | Faces | Shot | START keyframe | END keyframe | ACTION + facial beats | VOICE | Mouth | Motion | EDIT | SFX | Caption |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C09 | 3.0 | 0:25.0 | AI | 1: Grandma | CU · face 40% | Close-up of Grandma, looking up from her dough for the first time at something just above the lens, flour on her cheek, a stern face, warm light. | Same framing and light; change only: her face softened and her eyes glistening. | She stops; her stern face slowly softens. | GRANDMA (on) [slowing, then quiet]: “That... that hat.” | overlay | low | Music and ambience fall away on "That"; no jokes from here to the end of the aftermath beat C15. | wind gust, then silence | BOTTOM (eyes in the upper two thirds) |
| C10 | 3.5 | 0:28.0 | AI | 1: Boy | CU · face 38% | Close-up of the Boy in his conical leaf hat looking up at someone just above the lens, hopeful, lips parted. | Same framing; change only: his eyes wide and a small, brave breath. | His eyes widen and he draws a small breath, hoping. | BOY (on) [careful, hopeful]: “You've seen this hat?” | overlay | low | Soft piano begins at 1.0 s. | soft piano | BOTTOM |
| C11 | 3.5 | 0:31.5 | AI | 1: Grandma | CU · face 40% | Close-up of Grandma, eyes glistening, a faint warm smile, looking toward the lens, warm lantern light. | Same framing and light; change only: her gaze lowered toward a small wooden stool and her smile deeper. | Her gaze drifts down toward the stool and her smile deepens. | GRANDMA (on) [quiet, remembering]: “A man sat there once. Same hat.” | overlay | low | Warm grade shifts toward sepia in the last 0.6 s. | soft piano, lantern crackle | BOTTOM |
| C12 | 3.0 | 0:35.0 | AI | 0 (+back: Dad) | MS | Sepia, warm dusk: a man's silhouette seen from behind wearing a conical leaf hat, seated on a small wooden stool at the same food stall, lantern light, a spoon held above a steaming dumpling; his face is never visible. | Same framing and light; change only: the spoon lowered to the dumpling, steam rising, his shoulders relaxed. | The spoon lowers very slowly; steam curls; the lantern flickers once. | BOY (V.O.) [quiet, gentle, a little tight]: “Dad went away. His book stayed.” | closed | low | Sepia grade + paper grain + vignette; one leaf particle drifting down. DAD BEAT starts here (6.0 s, no jokes from 10 s before to 10 s after). | lantern crackle, soft piano, steam | BOTTOM (silhouette and spoon in the upper two thirds) |
| C13 | 3.0 | 0:38.0 | AI | 0 (+hands: Boy) | MACRO | Macro of an open old book on a wooden counter in warm light: a faded ink sketch of a small food stall with a little stool and a steaming dumpling, a tiny doodle of a conical hat above a dumpling in the corner, and a few lines of faded brush strokes; a child's finger rests beneath the first line. | Same framing and light; change only: the child's finger has slid along the first line and a thin curl of steam drifts across the page. | The small finger slides slowly along the first line of the page; steam curls across the paper. | BOY (V.O.) [reading, tender, steady]: “Page one: be patient.” | closed | low | Paper grain; one leaf particle; the first line gets a faint warm glow as the finger passes it (code). DAD BEAT ends at the end of this clip. | page rustle, soft piano | TOP (page in the lower two thirds) |

### D. Aftermath and the safe sip (0:41.0-0:51.0)
| Clip | Dur | Start | Method | Faces | Shot | START keyframe | END keyframe | ACTION + facial beats | VOICE | Mouth | Motion | EDIT | SFX | Caption |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C14 | 3.5 | 0:41.0 | AI | 1: Grandma | CU · face 38% | Close-up of Grandma, a soft faraway look, flour on her cheek, warm lantern light. | Same framing and light; change only: a small tender smile. | A small tender smile spreads slowly across her face. | GRANDMA (on) [soft, with a smile in the voice]: “He waited all afternoon for one dumpling.” | overlay | low | Piano continues; no jokes. | soft piano, steam | BOTTOM |
| C15 | 3.5 | 0:44.5 | AI | 1: Boy | CU · face 40% | Close-up of the Boy in warm late light, the small worn book held against his chest, a quiet hopeful look, eyes lowered. | Same framing and light; change only: his eyes lifted to the lens, steady and certain. | He lifts his eyes to the lens, quietly certain. | BOY (on) [quiet, a believing little smile]: “The answers are in his book.” | overlay | low | Piano lifts a half-step; the last no-joke clip. | soft piano, breeze | BOTTOM |
| C16 | 3.0 | 0:48.0 | AI | 0 (+hands: Grandma) | MACRO | Macro: an old woman's hand sets a white porcelain spoon holding one soup dumpling on a worn wooden counter, soft steam rising; only the hand is visible. | Same framing and light; change only: the hand has withdrawn and a tiny hole in the skin sends up a thread of steam. | The hand sets the spoon down gently; a thread of steam rises from the dumpling. | GRANDMA (off) [a teacher's calm]: “Tiny hole. Let it cool. Sip.” | closed | low | Badge "GROWN-UP HELP: HOT SOUP" in the top-right corner 0.3-2.8 s (code). | soft clink, steam hiss | TOP (badge top-right; captions top-left of centre) |

### E. Impatience, hook, ending (0:51.0-1:09.5)
| Clip | Dur | Start | Method | Faces | Shot | START keyframe | END keyframe | ACTION + facial beats | VOICE | Mouth | Motion | EDIT | SFX | Caption |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C17 | 3.5 | 0:51.0 | AI | 1: Uncle | CU · face 46% | Close-up of the Uncle, completely bald with a thin curled mustache, bent over a white spoon with a soup dumpling just below his chin, nostrils flared, eyes locked on the dumpling, lips pressed tight and trembling. | Same framing; change only: his whole face trembling harder and one tear on his cheek. | He trembles with effort, nose an inch from the dumpling, lips pressed tight. | UNCLE (on) [strained, vibrating, proud of himself]: “I've been patient for NINE seconds.” | overlay | low | Sweat-drop sprite from 0.5 s (first gag of the episode after the Dad beat: no effects before 0:51.5); mustache-tip wobble (code); rising string tremolo. | string tremolo, steam hiss | BOTTOM |
| C18 | 2.5 | 0:54.5 | AI | 1: Boy | CU · face 36% | Close-up of the Boy facing the lens, flat-faced, steam drifting behind him. | Same framing; change only: his eyelids lowered to a half-lidded deadpan. | He turns his eyes to the lens, lids dropping, deadpan. | BOY (on) [flat]: “It was four. I counted.” | overlay | low | 8-frame look-to-lens hold. | comic ding | BOTTOM |
| C19 | 3.0 | 0:57.0 | AI | 1: Grandma | MCU · face 27% | Medium close-up of Grandma leaning over her counter, one arm raised and pointing far off to the right, a small secret smile, steam behind her. | Same framing; change only: her eyebrows lifted and her smile wider. | She holds the point; her secret smile slowly grows. | GRANDMA (on) [smiling, a little secret]: “Then he went south. To Guangzhou.” | overlay | low | Journal-map inset in the TOP band 1.0-3.0 s: a dotted line glows and slides down the coast to Guangzhou (code); adventure-music sting starts. | pen scratch, sparkle, music sting | BOTTOM |
| C20 | 2.5 | 1:00.0 | AI | 1: Uncle | CU · face 44% | Close-up of the Uncle, completely bald with a thin curled mustache, chin up, one fist raised beside his face, a bulging travel bundle on his back with a bamboo steamer strapped to it, mouth closed in a fierce grin, eyes blazing. | Same framing; change only: his fist raised higher and his eyes squeezed shut in fierce joy. | He pumps his fist once, fierce and joyful. | UNCLE (on) [volcanic, full power, short and explosive]: “FOR DUMPLING RESEARCH!” | overlay | low | Golden aura + ground-crack overlay along the bottom + fleeing-bird silhouettes (code); 4 px camera shake on ones on "RESEARCH". | aura blast, crack, wings flapping | TOP (fist and face fill the lower two thirds) |
| C21 | 2.5 | 1:02.5 | AI | 2: Boy, Uncle | CU · face 35% | Close-up of the Boy facing the lens, flat; behind him, soft and out of focus, the Uncle with a bulging travel bundle on his back and a fist raised. | Same framing; change only: the Boy's eyebrow raised and the blurred Uncle turned toward the right, ready to go. | The Boy raises one eyebrow at the lens; behind him the blurred Uncle turns to the right. | BOY (on) [flat, fond]: “He's already packed. Of course.” | overlay | low | 8-frame look-to-lens hold. | comic ding, bundle rattle | BOTTOM |
| C22 | 2.5 | 1:05.0 | AI | 1: Boy | CU · face 40% | Soft close-up of the Boy in warm late light, the small worn book held to his chest, the stall blurred behind him, a small smile, eyes lowered. | Same framing and light; change only: his eyes meet the lens, a tender smile, the hat ribbon lifted by a breeze. | He takes a quiet breath and lifts his eyes to the lens; the ribbon stirs. | BOY (on) [soft, to the lens, a small smile]: “Dad was right...” | overlay | low | Soft piano swells; last 0.3 s: steam-puff transition. | soft piano, breeze | TOP (face in the lower two thirds) |
| C23 | 2.0 | 1:07.5 | AI | 2: Uncle, Camel | MS · faces 22% | Medium shot: the Uncle, completely bald with a thin curled mustache, sitting on a small stool beside a bulging travel bundle, giving a thumbs up with eyes shut in pride; beside him a calm camel with a small bamboo steamer on its back, staring into the lens. | Same framing; change only: a tiny puff of steam rises from the Uncle's ear and the camel's eyes are closed mid-blink. | One tiny puff of steam from the Uncle's ear; the camel blinks slowly. | — | closed | low | Camel sting (the 1 s loop beat): hard cut to black on the last frame; the loop restarts on the spoon-and-stool hook. | tiny toot, camel bell, cut | none |

## Numbers (from `lint_shotlist.py`)
23 AI clips + 1 CODE clip, 69.5 s, 113 spoken words (Boy 50, Grandma 45, Uncle 18), 0 `high` motion clips, 3 two-face AI clips (C02, C21, C23), 0 three-face clips, 17 on-screen talk shots (all CU/MCU, motion low, one speaker), 4 off-screen / V.O. lines. Lint: `RESULT: PASS (0 fail, 2 warn)`; the warns are the 69.5 s total (over the 65 s target, under the 75 s limit; the animatic sets the real length) and the word count (113, the creator's v5 figure, below the old 140-word guide). The joke-free window around the Dad beat is 26 s by the creator's rule, so this episode runs a little long; if the animatic is over 1:15, cut C04 (3.0 s) and C21's second sentence first.

## Fact-landing check
| Fact | Where | Beat to land | Tag |
|---|---|---|---|
| **Xiaolongbao are pleated by hand, classically 18 folds** (more folds, thinner skin) | C06, 0:16.5 | the fold counter ticking to 18 and the Uncle's "I'll... perish." | WIDELY CITED, counts vary by shop (14 to 32 in the sources); said by Grandma about her own stall and hedged in the description |
| **How to eat one safely**: tiny hole, let it cool, sip first | C16, 0:48.0 | the grown-up badge, right after the quiet beat | FIRM (safety) |
| Nanxiang is an old canal town in today's Shanghai | C02 place card | the place card | FIRM |
| Guangzhou is the next stop (south of Shanghai by sea) | C19 | the glowing journal-map line | FIRM (geography) |
| The man on the stool, the book page, "be patient", the doodle | C09-C15 | the Dad beat | FICTION (the story) |

## Safety and sensitivity checks
- **Dad beat:** C12-C13 only (6.0 s). Sepia silhouette from behind, no face, never named in a prompt; the line is gentle ("Dad went away. His book stayed.") and said once; there is no mention of death or danger. No joke inside 10 s on either side (last joke 0:24.5, first joke after 0:51.5).
- **No secret for the Uncle, no torn page:** the Uncle knows nothing more than the Boy; the book is whole; page one is simply "be patient".
- **Grown-up step:** C16 repeats the safe method (tiny hole, cool, sip) with the GROWN-UP HELP: HOT SOUP badge, so the burn lesson from Episode 1 is closed in this episode too.
- **Jokes only on the Uncle** (his hovering, his "research", his dramatic hunger, his nine seconds of patience). Grandma delivers one dry line ("Then perish quietly.") as the straight reply, never as the butt.
- **No text in AI shots:** the book page is a sketch and brush strokes; the stool carving is a doodle; the map inset, fold counter, place card and badge are code overlays.
- **Uncle design:** every Uncle START says "completely bald with a thin curled mustache"; no hat of any kind.
- **Hat:** the Boy's hat is "the same hat" the man wore; nothing claims it is Dad's, so the creator can decide in later episodes.

## Cut / restore list (priority order)
1. C04 "I'm not sitting. It's research." (3.0 s): first to cut if over 1:15, restore for laughs.
2. The second sentence of C21 ("Of course.") and C18's "I counted." (about 1.0 s each).
3. A Boy aside about the book's cover and the string (2.5 s).
4. Grandma's longer story of the man and the dumpling (v4.4 "He burned his tongue too", 3.5 s): a possible Episode 1 / Episode 2 bridge line.
5. The Silk Road map card (v4.4, 20 s): arc compilation.

## Upload details
- **Title options (pick one):**
  1. `Nobody Sits On This Stool... Here's Why 🥟`
  2. `Dad's Dumpling Book: Page One 📖🥟 | The Dumpling Boy #2`
  3. `18 Folds, No Hurry 🥟 (The Uncle Cannot Wait)`
- **Description:**
```
🥟 Support the journey → https://thedumplingboy.netlify.app
A fast, funny food-travel show on the old Silk Road: a boy, his (very hungry) uncle, and Dad's dumpling book. Stop 1, part 2: Grandma's stall in Nanxiang, Shanghai.

Why won't Grandma let anyone sit on that stool? And what is on page one of Dad's book? (Episode 1, the soup dumpling and the legend, is in the previous Short.)
A classic soup dumpling is folded by hand with about 18 pleats; the number varies from shop to shop, and more folds usually mean a thinner skin.
Safe way to eat one (grown-ups help with hot soup): tiny hole, let it cool, sip the soup first.
The stall, the stool, Grandma, the book and the camel are fiction.

Next: Guangzhou.
#dumplings #xiaolongbao #shanghai #silkroad #animation #foodtravel #shorts
```
- **Loop idea:** C23 hard-cuts to black on the camel blink and the Short restarts on the spoon-on-forehead hook ("Nobody sits on that stool"), so the answer to "what was Dad right about?" invites a replay. Group Episode 1 and Episode 2 with the YouTube "Shorts series" feature.
- **Pinned comment:** `The Uncle lasted 9 seconds. How long can YOU wait for a soup dumpling to cool? ⏱️🥟 And did you spot the camel? 🐪`
- Channel: The Dumpling Boy (@TheDumplingBoy.studio). Business contact: thedumplingboy.studio@gmail.com.

## Sources
Verified 2026-11-28 by web search (summaries read; most pages could not be opened from this session's network, so re-open each once before upload).
- Pleat count (18 is the number most often cited for Nanxiang-style xiaolongbao; counts vary, more pleats = thinner skin): https://www.citynewsservice.cn/articles/7krv667m ; https://global.chinadaily.com.cn/m/shanghai/jiading/2014-11/18/content_18936526.htm ; variation: https://amp.scmp.com/lifestyle/food-drink/article/3097791/history-xiaolongbao-or-soup-dumplings-outskirts-shanghai (WIDELY CITED, not an official standard)
- Nanxiang as the home of xiaolongbao, Jiading District of Shanghai (FIRM): https://english.shanghai.gov.cn/en-GlobalTasteinShanghai2026-LocalFlavors/20260316/00b0c6d1698d406c8d532a6e169e1a1e.html ; https://theculturetrip.com/asia/china/articles/a-brief-history-of-xiao-long-bao-shanghais-signature-dish
- How to eat one safely (lift, spoon, small opening, wait, soup first, vinegar and ginger): https://www.scmp.com/lifestyle/food-drink/article/2099549/how-eat-xiaolongbao-foolproof-guide-eating-soup-dumplings ; https://thetakeout.com/how-to-eat-xiao-long-bao-soup-dumplings-1827959964
- Fiction (not claimed as fact): the stool, the man in the hat, Dad's book and page one, Grandma, the camel.
