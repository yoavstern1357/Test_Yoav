# Opening song: "Dumpling Boy" (working title: ギョーザ！ショーロンポー！)

Original anime-TV-opening song for the series intro (see `series-intro.md`, PRODUCTION-BIBLE v4.4 directive 3). Sung in JAPANESE, Asian punk style. Original lyrics and music only; no quotes from or references to any existing song, anime or artist. Family-safe; the only joke is on the Uncle (he sneaks dumplings and calls it "research", the series catchphrase).

## Sound brief
- Tempo 170-190 BPM, 4/4, major key, bright.
- Distorted guitars (power chords), driving punk drums, melodic bass.
- Energetic lead vocal (female primary, male alternate), shouted gang-vocal hook on "ギョーザ！ ショーロンポー！ ダンプリング！".
- The intro cut (10-12 s) ends on a big accent (full-band hit + crash) that lands on the title card "THE DUMPLING BOY" (I7).
- Style tags sent to the model are in `tools/episode_maker/gpu/inputs/opening-song/music.json`.

## Lyrics, full version (about 60 s)

Structure: intro (instrumental, 4 bars) - verse 1 - pre-chorus - chorus - verse 2 - chorus - outro.

| Section | Japanese | Romaji | English |
|---|---|---|---|
| verse 1 | ぼうしをかぶって かけだした | Boushi o kabutte kakedashita | Hat on my head, I ran out the door |
| | ぺこぺこおなかの おじさんと | Pekopeko onaka no ojisan to | with my starving, rumbling-tummy uncle |
| | ゆげのむこうに みちがある | Yuge no mukou ni michi ga aru | there is a road beyond the steam |
| | とうさんのノートが よんでるよ | Tousan no nooto ga yonderu yo | Dad's notebook is calling us |
| pre-chorus | ひとくち かじれば ほら | Hitokuchi kajireba hora | Take one bite, and look |
| | せかいが ひろがる | Sekai ga hirogaru | the whole world opens up |
| chorus | ギョーザ！ ショーロンポー！ ダンプリング！ | Gyouza! Shouronpou! Danpuringu! | Gyoza! Soup dumpling! Dumpling! |
| | あつあつ ゆげを あげて とびこめ！ | Atsuatsu yuge o agete tobikome! | Piping hot, steam rising, jump right in! |
| | ギョーザ！ ショーロンポー！ ダンプリング！ | Gyouza! Shouronpou! Danpuringu! | Gyoza! Soup dumpling! Dumpling! |
| | ぼくらの たびは とまらない！ | Bokura no tabi wa tomaranai! | Our journey will not stop! |
| verse 2 | おじさん またまた つまみぐい | Ojisan mata mata tsumamigui | Uncle is sneaking a bite again |
| | けんきゅうだよって いいわけだ | Kenkyuu da yo tte iiwake da | "It's research!" is his excuse |
| | でっかい ぎょうざが おいかけてくる | Dekkai gyouza ga oikakete kuru | A giant dumpling is chasing us |
| | にげろ にげろ ぜんそくりょく！ | Nigero nigero zensokuryoku! | Run, run, at full speed! |
| chorus | (repeat the chorus) | | |
| outro | ダンプリング ボーイ！ | Danpuringu Booi! | Dumpling Boy! |

Notes on the words: "つまみぐい" (tsumamigui) = nibbling food on the sly; "ぜんそくりょく" (zensokuryoku) = at full speed; "ほかほか/あつあつ" = steaming hot. Mostly hiragana/katakana so the model reads and sings it clearly. Lines map to the intro: "とびこめ！" = the dive into the dumpling pool (I4), "おいかけてくる / にげろ" = the chase (I5-I6).

## Intro cut lyrics (10-12 s)
Generated as a 16 s track, then cut to about 11 s with a hard accent ending.

| Japanese | Romaji | English |
|---|---|---|
| ギョーザ！ ショーロンポー！ ダンプリング！ | Gyouza! Shouronpou! Danpuringu! | Gyoza! Soup dumpling! Dumpling! |
| あつあつ ゆげを あげて とびこめ！ | Atsuatsu yuge o agete tobikome! | Piping hot, steam rising, jump right in! |
| ダンプリング ボーイ！ | Danpuringu Booi! | Dumpling Boy! |

Sync idea against `series-intro.md`: hook shout on I1 (0.0-1.4 s), "とびこめ" on the pool dive (I4), the last "ダンプリング ボーイ！" + crash on the title bloom (I7). Optional small burned-in English translation: use the English column above, one line at a time.

## How it is made
Model: ACE-Step v1 3.5B (`ACE-Step/ACE-Step-v1-3.5B`, Apache-2.0, safetensors), run on Kaggle through the `music` task (`tools/episode_maker/gpu/README.md`, section "Music"). Four style variants (A female pop-punk-anime, B male j-rock, C pop-punk, D mixed vocals), two seeds each.
