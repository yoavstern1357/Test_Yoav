# Series intro (every episode), about 8 s

Purpose: a strong hook before every episode, independent of that episode's story. Fast frames, music sting, then the show title.
Style: delicate soft anime in our own look (see PRODUCTION-BIBLE.md "Updates"); characters in the approved village clothes.

| # | Time | Shot | Motion (image-to-video) | Sound |
|---|---|---|---|---|
| I1 | 0.0-1.4 | HOOK. Close-up: the Boy and the Uncle bite into soup dumplings at the same moment, steam bursting, eyes wide with joy | both bite, steam puffs | crunch-squish, sizzle, first hit of the theme |
| I2 | 1.4-2.4 | Macro: a dumpling bursts, golden soup splashes in slow motion | slow-motion splash | splash, sparkle |
| I3 | 2.4-3.8 | Wide: both float in a giant pool filled with dumplings like a ball pit, laughing; the Uncle lounges on a big dumpling like a float | gentle bobbing, dumplings rolling | water-ish plops, laughter |
| I4 | 3.8-4.8 | The Boy dives into the dumpling pool; dumplings fly up around him | dive, dumplings fly | whoosh, plop |
| I5 | 4.8-6.4 | Old Asian city street at dusk with lanterns: both run toward the camera, truly SCARED (wide eyes, open mouths); behind them a GIANT round dumpling with a huge chomping mouth rolls after them (original design, soft and funny, not scary) | run cycle, giant dumpling chomps and rolls | thumping rolls, chomp chomp, music builds |
| I5c | 6.0-6.6 | Insert: a hand (the Boy's) flicks three gyoza like throwing stars; they spin through the air with motion trails toward the giant dumpling | spin, whoosh | shing-shing-shing |
| I6 | 6.6-7.2 | Low angle: the giant dumpling's mouth snaps shut just behind them as they leap out of frame | chomp, leap | big CHOMP |
| I7 | 7.2-8.5 | Title: "THE DUMPLING BOY" in brush lettering blooms out of steam (code) | steam reveal | gong + theme end |

Production: stills I1-I6 from tools/episode_maker/gpu/inputs/intro-stills (FLUX.2 klein on Kaggle), then image-to-video clips (LTX-Video), title in code, music sting synthesized locally.

Creator notes: Uncle fatter; both scared in the chase; the giant dumpling must clearly look like a dumpling (pleated top, steam); added the gyoza-shuriken insert.

## Episode 1 premiere version (7.5 s)
Creator decision (2026-11-28): Episode 1 includes the series opening. It plays right after the 3.5 s hook (C01 "Defeated... by ONE tiny dumpling.") and replaces the 1.0 s logo hit; the title bloom is the end of the opening. Later episodes keep only the 3-s sting (hook, then a title hit <= 2 s) unless the creator says otherwise. No spoken English: the song is sung in Japanese (first 7 s of the intro cut of `opening-song.md` plus a 0.5 s crash ring-out); optional tiny English caption translation. Compressed so every AI clip is 2.0-3.5 s (shot rules) and the opening has 3 AI clips + 1 code clip:

| Premiere clip | Time in Episode 1 | From the full intro | What | Song |
|---|---|---|---|---|
| C21 (AI 2.0 s) | 0:03.5-0:05.5 | I1 + I2 | Both bite soup dumplings at once, eyes wide with joy; last 0.4 s a code soup-splash flash (I2 still) | shout hook "ギョーザ！ ショーロンポー！ ダンプリング！" |
| C22 (AI 2.0 s) | 0:05.5-0:07.5 | I3 (I4 dive dropped) | Giant dumpling pool: the Boy laughing, the Uncle lounging on a big dumpling like a float | "あつあつ ゆげを あげて とびこめ！" |
| C23 (AI 2.0 s) | 0:07.5-0:09.5 | I5 + I5c | Dusk lantern street: both run toward the camera, truly scared; the giant pleated dumpling chomps behind them; a 0.4 s code insert of three gyoza thrown like shuriken | instrumental build, riser |
| K01 (CODE 1.5 s) | 0:09.5-0:11.0 | I6 + I7 | 0.3 s giant CHOMP impact frame, then the brush-lettering title "THE DUMPLING BOY" blooms out of steam | last "ダンプリング ボーイ！" + crash on the chomp/title |

Rules kept: max 2 faces per AI clip (the giant dumpling is a blurred mouth-only prop; if the stills QC counts it as a face, composite it in code), fixed camera, one action per clip, Uncle fully bald with a thin curled mustache and never a hat. Stills come from `tools/episode_maker/gpu/inputs/intro-stills` (I1_bite, I3_pool, I5_chase as START frames; I2_splash and I6_chomp as code inserts). The same 7.5 s sequence is reusable as the intro of the 16:9 compilations. Script: `scripts/episode-01-v5.md`.
