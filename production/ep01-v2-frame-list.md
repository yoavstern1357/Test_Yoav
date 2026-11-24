# Episode 1 V2: frame list

Look is **unchanged from V1** (creator decision 2026-11-24): the round, soft, cute picture-book characters stay exactly as approved. Only the feeling changes: fast pace, living camera, anime-like rhythm (all done by the engine from the spec, not by redrawing).

**57 shots, 20 NEW images, 37 REUSE** (REUSE = copy the existing v1 frame from `tools/episode_maker/specs/frames/ep01/` to the `f##_` filename in `frames/ep01v2/`; the engine crops/zooms it differently, so the same picture can play as a wide and an extreme close-up). Rows marked `(crop of ...)` need no new art.

## Prompt recipe for NEW frames (generator prepends this)

> Use the boy and the man from the reference images exactly (boy: Vietnamese conical leaf hat with orange chin ribbon, white kimono with orange belt; man: bald, thin mustache, white kimono with wide orange belt; Grandma: small, grey bun, soft green jacket, apron, per her reference image). Soft gentle children's picture-book animation style, 2D cartoon, very round friendly shapes, big expressive eyes, bright cheerful pastel colors, soft warm lighting, vertical 9:16. **[scene prompt]** No text.

References: Boy `MAHbzwNGxJo`, Uncle `MAHbzx4PTVI`, Grandma `MAHb0FNIPP4`. Single-boy frames avoided on purpose. For frames with no characters, omit the character sentence. Dad is only ever a sepia silhouette from behind.

| # | Filename | Source | Characters | Camera angle | Scene prompt |
|---|---|---|---|---|---|
| 1 | `f01_cold_open_eyes.png` | REUSE:hook_steam | uncle | extreme close-up, eyes only | (crop of the steamer-steam frame) Uncle's huge round eyes bulging through swirling steam, sweat beads, dead silence. |
| 2 | `f02_cold_ears_steam.png` | REUSE:toot_face | uncle+boy | wide, dutch tilt | (existing frame) Uncle's face tomato red, steam shooting from both ears like train whistles, the boy ducking. |
| 3 | `f03_rewind_train.png` | REUSE:metro | boy+uncle | medium, whip in | (existing frame) Boy and Uncle riding a train at dawn. |
| 4 | `f04_journal_open.png` | REUSE:journal_station | boy+uncle | extreme close-up, hands and book | (crop on the journal) The Boy's hands opening a cracked leather journal; a hand-drawn map unfolds inside. |
| 5 | `f05_map_route.png` | REUSE:route_map | none | top-down insert | (existing frame) The hand-drawn map, a dotted line glowing from home toward Shanghai, tiny train chugging along it. |
| 6 | `f06_torn_page.png` | NEW | none | extreme close-up, macro | Extreme close-up of the last journal page: a ragged torn edge, a half-finished recipe sketch of a mystery dumpling, one smudged ink line, a thumb pressing the corner. |
| 7 | `f07_train_snore.png` | NEW | uncle+boy | medium, eye level | Inside a morning train carriage: the Uncle sleeps against the window hugging an empty bamboo steamer, drooling a little, while the Boy sits beside him reading the journal. |
| 8 | `f08_skyline.png` | REUSE:skyline | none | establishing wide | (existing frame) Shanghai skyline glowing across the river at dusk. |
| 9 | `f09_title.png` | REUSE:cover | boy+uncle | low angle hero shot | (existing cover frame) Boy and Uncle standing proud, city lights behind them. |
| 10 | `f10_metro_sign.png` | REUSE:metro | none | insert, whip | (crop of the metro frame) A glowing station sign for the Nanxiang stop on Line 11, platform lights streaking past. |
| 11 | `f11_canal_wide.png` | REUSE:arrive_canal | none | establishing wide, golden hour | (existing frame) Old Nanxiang: canal, stone bridge, red lanterns, twin brick pagodas at golden hour. |
| 12 | `f12_pagodas_low.png` | NEW | none | extreme low angle | Looking up from the canal bank at two tall old octagonal brick pagodas side by side against a glowing orange sky, lantern strings overhead. |
| 13 | `f13_steam_alley.png` | NEW | none | tracking, ground level | A narrow cobbled lantern-lit alley; a single glowing ribbon of steam curls out of a shop door and drifts down the lane like a beckoning finger. |
| 14 | `f14_nose_sniff.png` | NEW | uncle | extreme close-up | Extreme close-up of the Uncle's big nose and mustache, nostrils flaring, eyes half-closed in bliss, a wisp of steam entering his nose. |
| 15 | `f15_float.png` | REUSE:float | uncle+boy | medium, low angle | (existing frame) Uncle floating a foot off the ground, pulled by a steam ribbon, Boy hanging onto his belt. |
| 16 | `f16_stall_wide.png` | NEW | uncle+boy | wide, eye level | A tiny street dumpling stall at golden hour: a tower of bamboo steamers on the counter, a cook's hands blurred behind, Uncle and Boy pressed up to the counter, eyes shining. |
| 17 | `f17_basket_glow.png` | NEW | none | extreme close-up, food macro | Bamboo steamer lid lifting to reveal six plump pleated soup dumplings glistening in golden steam. |
| 18 | `f18_chopsticks.png` | NEW | none | extreme close-up, hands | Chopsticks pinching a single dumpling by its pleated top, the thin skin trembling and sagging with the hot soup inside. |
| 19 | `f19_grab.png` | REUSE:grab | uncle+boy | low angle, dutch tilt | (existing frame) Uncle triumphantly raising a dumpling toward his open mouth, Boy lunging to stop him. |
| 20 | `f20_gulp.png` | NEW | uncle | extreme close-up, mouth and cheeks | The Uncle's round cheeks bulging, his mouth clamped shut on the whole dumpling, eyes starting to widen. |
| 21 | `f21_eyes_twitch.png` | NEW | uncle | extreme close-up, eyes | Extreme close-up: the Uncle's eyes frozen wide, one eyelid twitching, a single bead of sweat sliding down. |
| 22 | `f22_burn_impact.png` | REUSE:gag_burn | uncle | impact frame, full face | (existing burn frame) Uncle's face tomato red, mouth open in a silent scream, soup bursting out. |
| 23 | `f23_ears_toot.png` | REUSE:toot_face | uncle+boy | wide, dutch tilt | (existing frame) Steam blasting out of Uncle's ears, Boy's hat blowing back. |
| 24 | `f24_sheepish.png` | REUSE:sheepish | uncle+boy | medium close-up | (existing frame) Sheepish Uncle, tongue out, Boy deadpan beside him. |
| 25 | `f25_deadpan_spoon.png` | NEW | boy+uncle | two-shot, medium | The Boy calmly holds out a ceramic spoon to the Uncle, one eyebrow raised; the Uncle fans his open mouth with both hands, tongue out. |
| 26 | `f26_lift.png` | REUSE:spoon_lift | boy | extreme close-up, hands | (existing frame) Chopsticks lifting a dumpling by the top. |
| 27 | `f27_spoon.png` | REUSE:right_way | boy+uncle | extreme close-up, food | (existing frame) The dumpling resting in a ceramic spoon, steam curling. |
| 28 | `f28_tiny_hole.png` | NEW | none | extreme close-up, macro | A chopstick tip poking a tiny hole in the dumpling's skin; a thin thread of hot golden soup and steam escapes. |
| 29 | `f29_wait.png` | REUSE:wait_uncle | uncle+boy | medium, eye level | (existing frame) Uncle staring at the spoon, sweating, Boy holding up one finger. |
| 30 | `f30_be_cool.png` | REUSE:spoon_clock | uncle | extreme close-up, eyes and spoon | (existing frame) A big clock behind the steaming spoon, Uncle's sweating face whispering to his dumpling. |
| 31 | `f31_growl_tower.png` | REUSE:tower_wobble | uncle+boy | low angle | (existing frame) The tower of steamers wobbling from Uncle's growling tummy, Boy steadying it with one finger. |
| 32 | `f32_sip.png` | REUSE:sip | uncle+boy | medium close-up | (existing frame) Uncle bringing the spoon to his lips, eyes closed, Boy watching. |
| 33 | `f33_bliss.png` | REUSE:ding_sip | uncle | medium close-up, soft light | (existing frame) Uncle's eyes closed in bliss, warm glow. |
| 34 | `f34_journal_turn.png` | NEW | boy+uncle | over-the-shoulder, insert | The Boy turns a journal page; black ink spreads across it like a brush wash while the Uncle watches over his shoulder with a spoon in his mouth. |
| 35 | `f35_legend_shop.png` | REUSE:legend_shop | none | storybook establishing | (existing frame) Storybook old dumpling shop in a little garden town. |
| 36 | `f36_dawn_courtyard.png` | NEW | none | storybook wide, dawn | Storybook scene of a tiny old courtyard kitchen at dawn: a faceless cook seen from behind rolling dough by lantern light, rows of tiny buns on bamboo trays, pale pink sky over rooftops. |
| 37 | `f37_legend_fold.png` | REUSE:legend_fold | none | storybook close-up | (existing frame) Hands pleating a tiny bun with super-thin skin. |
| 38 | `f38_legend_jelly.png` | REUSE:legend_jelly | none | storybook macro, glow | (existing frame) Golden soup jelly melting inside a bun in the steam. |
| 39 | `f39_basket_card.png` | NEW | none | storybook still, card | A single woven bamboo steamer basket drawn in warm storybook colors with a soft empty cream banner space above it, steam curling. |
| 40 | `f40_fact_pagodas.png` | REUSE:factbg | none | symmetrical wide, card | (existing paper-cut fact background) Twin brick pagodas, soft paper-cut look. |
| 41 | `f41_two_names.png` | REUSE:two_names | uncle+boy | medium close-up | (existing frame) Uncle holding up two fingers, Boy rolling his eyes. |
| 42 | `f42_dad_silhouette.png` | REUSE:dad_sepia | none | wide, silhouette from behind | (existing frame) Dad's sepia silhouette from behind in a conical hat, holding a spoon. |
| 43 | `f43_dad_journal1.png` | REUSE:dad_journal | none | insert, handwriting | (existing frame) Journal page with Dad's handwriting. |
| 44 | `f44_golden_dumpling.png` | NEW | none | macro, glowing | A single perfect dumpling in a spoon glowing like treasure, golden light and rising steam against a deep warm background. |
| 45 | `f45_bridge_wide.png` | REUSE:night_bridge | boy+uncle | wide, from behind | (existing frame) Boy and Uncle sitting on the stone bridge at night, lantern light rippling on the canal. |
| 46 | `f46_spoon_handoff.png` | NEW | uncle+boy | extreme close-up, hands | The Uncle's big hand carefully passing a spoon with one cooled dumpling to the Boy's smaller hands, lantern glow on both. |
| 47 | `f47_bridge_line.png` | REUSE:night_bridge | uncle+boy | medium close-up, push in | (crop of the bridge frame) Uncle turning to the Boy with a gentle smile. |
| 48 | `f48_boy_smile.png` | REUSE:boy_smile | boy+uncle | close-up, eyes closed | (existing frame) The Boy smiling with eyes closed, Uncle's shoulder soft in foreground. |
| 49 | `f49_fanning.png` | REUSE:fanning | uncle+boy | medium, snappy | (existing frame) Uncle fanning his tongue with the journal. |
| 50 | `f50_reach_next.png` | NEW | uncle | extreme close-up, hand | The Uncle's big hand reaching toward a fresh dumpling in a steamer, blurred street lights behind, fingers spread. |
| 51 | `f51_grandma_hands.png` | NEW | grandma | extreme close-up, hands blurring | A small old grandmother's hands folding dumpling after dumpling at lightning speed on a flour-dusted board, motion blur. |
| 52 | `f52_grandma_stare.png` | REUSE:grandma_stare | grandma | medium close-up, push in | (existing frame) Grandma frozen mid-fold, eyes fixed on something off-screen. |
| 53 | `f53_hat_brim.png` | NEW | grandma+boy | insert, low angle | Grandma's wrinkled hand reaching up and gently touching the brim of the Boy's conical leaf hat, the orange ribbon swaying, the Boy frozen and wide-eyed. |
| 54 | `f54_grandma_hat1.png` | REUSE:grandma_hat | grandma+boy | medium two-shot | (existing frame) Grandma smiling warmly at the Boy's hat. |
| 55 | `f55_grandma_hat2.png` | REUSE:grandma_hat | grandma+boy+uncle | close two-shot | (existing frame, closer) Grandma pointing a finger south, Boy and Uncle leaning in. |
| 56 | `f56_route_south.png` | REUSE:route_south | none | top-down insert | (existing frame) The journal map, the dotted line glowing south down the coast. |
| 57 | `f57_wave.png` | REUSE:boy_wave | boy+uncle | low angle hero push-in | (existing frame) Boy and Uncle facing camera, Boy pointing south. |
