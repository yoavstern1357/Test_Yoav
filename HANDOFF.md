# HANDOFF: The Dumpling Boy

Last updated: 2026-11-28. Working branch: `claude/charming-euler-0laws8` (GPU outputs on branch `gpu-results`). Read `CLAUDE.md` and `production/v4/PRODUCTION-BIBLE.md` (all decisions, incl. "v4.4 DIRECTIVES") first.

## 0. Current status
### 0.0 v5 decisions (creator, 2026-11-28) and the v6 plan: START HERE
- Decisions are at the end of `production/v4/PRODUCTION-BIBLE.md` ("v5 DECISIONS"). The approved structure is `production/v4/series-structure-plan.md` (**v6**); `series-format.md`, `season-map.md`, `character-bible.md`, `scripts/README.md` were updated to match (older text kept, marked superseded).
- **Structure:** seasons 12 / 9 / 9 / 9; **no Uncle secret, no torn page**; Dad vanished and left his dumpling book ("What is Dad's Dumpling, and where is Dad?"); rival host "Pepper" arrives in Ep 5, with friendly "Bell Round" battles before and between; **recipe = a separate 60-s Short after every 2 story episodes** (new bonus dumpling); **1 upload per week**, 6 uploads banked before launch.
- **S1 = Ep 1a, 1b, 2-11 (12 story) + recipe Shorts R1-R6 = 18 weeks, 17 dumplings** (calendar in plan 5.2). Old Ep 3 (guotie) is now R1; old Ep n = new Ep n-1 for n >= 4.
- **Characters:** Boy polished (age 7), Uncle variant B (fully bald, curled mustache, mandarin-collar jacket, towel), Grandma as in `production/v4/character-redesign-plan.md`; model sheets are the next art task.
- **Work rules:** free tools only; run autonomously and cheaply via sub-agents; the creator approves results only: **each script is shown in Hebrew in chat and approved BEFORE any production**, then animatic, then final. Nothing is uploaded without approval.
- **Next steps:** (1) Hebrew scripts for Ep 1a and Ep 1b (114 spoken words each), then R1, Ep 2, Ep 3, R2 = the 6-upload bank; (2) character model sheets (Boy, Uncle B, Grandma) and the rival's design (needed by Ep 5); (3) voice samples (Qwen3-TTS default, as many free samples as possible) for the creator to choose; (4) re-cut the Ep 1 v4.5 material into 1a and 1b.
- **Open creator confirmations** (plan section 7): rival arrival at Ep 5, the R1-R6 list, the S1 finale answer, final rival names, how the series finale closes "where is Dad?".
- Opening song: style 2 (male) stays as placeholder.

### 0.1 Earlier status (v4.4, 2026-11-26)
- **Episode 1 v4.4 rendered** (2:46, both 9:16 and 16:9): anime-TV opening with an original Japanese punk song (ACE-Step), full AI motion clips (LTX-Video 0.9.8 distilled on Kaggle), anime-comedy script `scripts/episode-01-v4.4.md`, Qwen3-TTS voices, safe caption placement. Files (git-ignored): `tools/episode_maker/out/episode-01-v4.4{,-land}{,-mobile}.mp4`. Sent to the creator; awaiting notes. Not uploaded.
- Decisions pending from the creator: opening-song style (placeholder: style B, intro_b__s212), final voice approval, notes on v4.4.
- Scripts v4.2 exist for Episodes 2-3 (need the v4.4 anime-comedy pass); creator said: focus on Episode 1 only for now.
- Agents hit the weekly model limit (resets 2026-11-30 05:00 UTC).

## 0.2 Pipeline (free)
- **GPU (Kaggle T4 x2, ~30 h/week, max 2 sessions)** driven by GitHub Actions: edit `tools/episode_maker/gpu/jobs/run.json` (unique run_id, task images|clips|tts|music, input folder) and push; results land on branch `gpu-results/<run_id>/`. Secret `KAGGLE_API_TOKEN` is set in the repo. See `tools/episode_maker/gpu/README.md`, `production/v4/motion-tech.md`, `production/v4/voice-tech.md`, `production/v4/gpu-ledger.md`.
- Stills: FLUX.2 klein 4B (Apache-2.0) with reference images; Uncle locked to gpu-results/intro-v3 variant 2; style "soft watercolor anime".
- Clips: backend `ltx98d`; KNOWN BUG: RIFE x2 corrupts interpolated frames, so drop every 2nd frame on install (12 fps "on twos"); see motion-tech.md.
- Spec + render: `tools/episode_maker/paper/build_spec_ep01v44.py` then `python3 make_episode.py specs/episode-01-v4.4.json out/episode-01-v4.4.mp4 --both`; mobile versions re-encoded at ~780 kbps to stay under 20 MB.
- Canva is only a fallback (rate-limited).

## 1. Status
| Item | State |
|---|---|
| Creator page | Live: https://thedumplingboy.netlify.app (English, links to the channel, Ko-fi, sponsor email) |
| Channel | `@TheDumplingBoy.studio` created on the business account; profile picture + banner in `brand/`; description text in `CHANNEL_KIT.md` |
| Scripts | Episodes 1-9 written (~2:00 each) in `scripts/`; Ep 21 draft (momo) there too; older drafts in `scripts/archive/` |
| Season plan | `production/season-map.md` (39 episodes, Silk Road) |
| Format | `production/series-format.md` |
| Characters | `production/character-bible.md` |
| **Episode 1 video** | **Rendered: 2:04, 1080x1920, 35 shots, neural voices + synthesized music/SFX + burned-in captions. Sent to the creator for approval. Not uploaded to YouTube.** |
| Growth plan, media kit, fact-check | `production/growth-plan.md`, `media-kit.md`, `fact-check-report.md` |
| Ko-fi | Page `ko-fi.com/thedumplingboy`; button is live on the site (creator confirmed the address) |

**Waiting on the creator:** approval (or notes) on the Episode 1 video; then they upload to YouTube themselves using `production/first-upload-checklist.md` and the text at the bottom of `scripts/episode-01-xiaolongbao.md`.

## 2. Next step
Make **Episode 2 (har gow, Guangzhou)** the same way as Episode 1: ~35 frames, ~2:00.
1. Read `scripts/episode-02-har-gow-guangzhou.md` and `tools/episode_maker/specs/episode-01.json` (the template).
2. Plan ~35 shots (a frame every 3-4 s: wide, medium, close-ups, inserts, fun-fact card backgrounds).
3. Generate frames in Canva (section 4), place them on pages of design `DAHb0JF2jpw`, export PNGs, download to `tools/episode_maker/specs/frames/ep02/`.
4. Write `specs/episode-02.json` (shots, voice lines from the script, SFX, moods, cards), run the maker, check, send the MP4 to the creator.
5. Then Episode 3 (guotie recipe + China recap), then Korea (4-6), Japan (7-9).

## 3. tools/episode_maker (local video pipeline)
Builds a vertical episode MP4 from a JSON spec. No paid video service. Full docs: `tools/episode_maker/README.md`.
- **Run:** `cd tools/episode_maker && python3 make_episode.py specs/episode-01.json out/episode-01.mp4` (full quality, about 5 min; run it in the background and watch the log) or add `--preview` (540x960, ~40 s) to check timing.
- **Voices:** Kokoro neural TTS (`kokoro-onnx`), cast in `VOICES` in `make_episode.py` (boy `am_puck` pitched up, uncle `am_michael` pitched down, grandma `af_sarah`, dad `bm_daniel`). Lines are cached in `/tmp/dumpling_tts_cache`.
- **Music and SFX:** generated in `synth.py` (marimba/music-box/pad bed, moods `cozy|tender|sparse|off`; SFX such as hiss, toot, growl, tick/tock, ding, sip). Original, no licensing.
- **Picture:** Ken Burns moves, crossfades, burned-in captions (color per speaker), fun-fact/title cards, steam/hearts/flash/shake effects.
- **Setup after a fresh container** (the model is not in git):
  ```
  pip install kokoro-onnx soundfile scipy pillow numpy      # also needs ffmpeg
  mkdir -p tools/episode_maker/tts && cd tools/episode_maker/tts
  curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
  curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
  ```
  (huggingface.co is blocked in this environment; GitHub releases and PyPI work. `tts` is git-ignored; it may currently be a symlink into the session scratchpad.)
- **Spec per shot:** `img`, `dur` (minimum, auto-extends to fit the voice), `motion`, `zoom`, `focus`, `lines`, `sfx`, `fx`, `shake`, `cards`, `ambience`, `mood`, `transition`.
- Output goes to `tools/episode_maker/out/` (git-ignored). `episode-01.mp4` (87 MB, full quality) and `episode-01-share.mp4` (42 MB) are there.

## 4. Canva workflow (pictures)
- **Folder:** "The Dumpling Boy" (`FAHbz3qqLyU`). **Frame design:** `DAHb0JF2jpw` ("Episode 1 storyboard"): page 1 unused collage, pages 2-9 early captioned storyboard, **pages 10-42 are the 33 full-bleed 1080x1920 Episode 1 frames** (page title = frame name).
- **Character reference images (use these in every prompt):** Boy `MAHbzwNGxJo`, Uncle `MAHbzx4PTVI`, Grandma `MAHb0FNIPP4`. Route map art `MAHb0D5LH5I`.
- **Prompt recipe:** start with "Use the boy and the man from the reference images exactly (boy: Vietnamese conical hat with orange chin ribbon, white kimono with orange belt; man: bald, thin mustache, white kimono with orange belt)." then "Soft gentle children's picture-book animation style, 2D cartoon, very round friendly shapes, bright cheerful pastel colors, soft warm lighting, vertical 9:16." and the scene. End with "No text."
- **Gotchas:**
  - `generate-image` fails often (`SERVER_GENERIC`). Images with **the Boy alone** fail most; **two characters together** or **a frame without faces** (hands, objects, places) succeed. Send 3-4 at a time, not 6+, and retry.
  - Job IDs are very long: copy them exactly (a wrong ID returns "Unexpected image job ID"). Media IDs come back as `MAHb...`.
  - Output thumbnails shown to Claude are tiny; real resolution comes only from export.
- **Get full-res frames:** (1) `read-design` with `open_transaction`; (2) `edit-design` `add_page` 1080x1920 titled with the frame name; (3) `read-design` pages to get page IDs; (4) ONE `edit-design` call with many `insert_fill` ops (page_id, asset_id, left 0 top 0 width 1080 height 1920); (5) `edit-design` `finalize: commit`; (6) `export-design` type `png`, pages [...], width 1080, height 1920, `export_quality: pro`; (7) download the returned URLs with curl into `specs/frames/epNN/<frame>.png`. The host `export-download.canva.com` was added to the environment allowlist (personal environment "Test_Yoav"); it persists.
- **Canva video quota** (`create-video`) is used up until **2026-12-16**; images still work. We do not need Canva video anymore: the local pipeline replaces it.
- Episode 1 frame -> Canva media ID (for re-export): hook_steam `MAHbz7FGxT8`, journal_station `MAHbz9FRn_U`, route_map `MAHb0D5LH5I`, cover `MAHbzyd1uFg`, skyline `MAHb2Jdftjk`, metro `MAHb2BFpulE`, arrive_canal `MAHb0LLufyg`, float `MAHb2Rm56Sk`, grab `MAHb2Co51Jg`, toot_face `MAHb2J-kZKM`, gag_burn `MAHbzx-pSj4`, sheepish `MAHb2P7zaFI`, spoon_lift `MAHb2FGFFV4`, sip `MAHb2ZaSRQI`, uncle_careful `MAHb2VeC7XA`, right_way `MAHbzyCXudc`, spoon_clock `MAHb2ARMP3k`, wait_uncle `MAHb0FpmVD0`, tower_wobble `MAHb2Krq_0o`, ding_sip `MAHb2PJOehU`, legend_shop `MAHbz79mePU`, legend_fold `MAHb2H1HKZI`, legend_jelly `MAHb2DH2hf8`, factbg `MAHb0NdiCnA`, two_names `MAHb2M2zSFI`, dad_sepia `MAHbz_GCMh8`, dad_journal `MAHb2EFCVUM`, night_bridge `MAHb0J-f0Cs`, fanning `MAHb2RSGEmg`, grandma_fold `MAHb2ZL5vT0`, grandma_stare `MAHb0FNIPP4`, grandma_hat `MAHb2RyDsZI`, route_south `MAHb2F1yAhQ`. `boy_smile` and `boy_wave` are stand-ins (copies of night_bridge and cover with camera zoom); unused: tower_end `MAHbz7uEKeE`.

## 5. Website (Netlify)
- Site `thedumplingboy` (id `9af8b629-a2e6-448f-96ab-4eb54fe09622`), https://thedumplingboy.netlify.app. It is linked to the repo's `master` branch (which holds only an old test file), so **deploy by zip upload to the API**, not by git push.
- Deploy: zip `index.html app.js config.js style.css avatar.svg og-image.png` (flat) and `POST https://api.netlify.com/api/v1/sites/<id>/deploys` with `Content-Type: application/zip` and header `Authorization: Bearer proxy-injected` (the real token is injected by the environment proxy; it was saved with `request_credential`). Poll the deploy until `state: ready`.
- Content comes from `config.js` (language, name, links; empty sections are hidden). Do not put the video on the public site before the creator approves it.

## 6. What is NOT in git, and how to restore it
| Not in git | Why | Restore |
|---|---|---|
| `tools/episode_maker/out/*.mp4` | big binaries | re-render from spec + frames + model (about 5 min) |
| `tools/episode_maker/specs/frames/ep01/*.png` (~100 MB) | big binaries | re-export from Canva design `DAHb0JF2jpw` pages 10-42 (section 4), or from the media IDs |
| `tools/episode_maker/tts/` (Kokoro model, ~350 MB) | big binary | curl commands in section 3 |
| `/tmp/dumpling_tts_cache` | cache | regenerated automatically |
| Netlify token | secret | stored in the cloud environment (network secret for `api.netlify.com`) |
| Session scratchpad files (screenshots, test renders) | temporary | not needed |
Everything else (scripts, specs, tool code, docs, site files, brand assets) is in git.

## 7. Open items and warnings
- Creator should check the stand-in frames (`boy_smile`, `boy_wave`) and the voices in the Episode 1 video; regenerate if they dislike them (voices are cast in `VOICES`).
- The Boy's white kimono with a Vietnamese hat was flagged by the fact-checker as possibly mixing Japanese and Vietnamese dress; the creator chose it, keep it.
- "Made for kids" (COPPA) must be answered honestly per upload; see `production/series-format.md`.
- Some source links could not be opened from this environment; re-click key sources before publishing.
