# Tools buying plan: paid AI animation services (2026-11-26)

Author role: head of production and finance planning. Status: plan only. Nothing was bought, no account was opened, nothing was committed or pushed.
Scope: what to buy to fix the three defects the creator confirmed on Episode 1 v4.4 (duplicated characters, smeared faces, out-of-sync mouths and action), with costs per episode and per month, a cheap fair trial, account and key setup, a rights checklist, and a comparison with hiring a freelance animator.
Read with: `production/v4/pro-upgrade-plan.md` (audit), `motion-tech.md` (current free pipeline), `voice-tech.md`, `marketing.md` section 6 (budget cap), `PRODUCTION-BIBLE.md` (look, both orientations, intro).

## How to read the evidence

- **Price date.** Every price is a web-search snapshot taken on **2026-11-26**. Where the source page shows its own date it is given. Vendors change prices every few weeks: confirm on the vendor's page on the day you buy.
- **Fetch was blocked.** The fetch tool could not open vendor pages from this container (e.g. ai.google.dev did not resolve). Everything below comes from **search-result snippets**, not from reading the pages.
- **Tags.** **[S-off]** = snippet quoting the vendor's own page or docs. **[S]** = snippet from a third-party blog, reseller or press article (often disagree with each other). **[M]** = my background knowledge, not re-checked today. **[E]** = my estimate. Treat [S] and [M] items as "verify before paying".
- **No independent anime test exists** for any of these tools in what I found. Every "good at anime" claim is vendor marketing. Hence the 5-shot trial in section 4 is the real decision tool, not this table.

## Executive summary

1. **The three defects have three different causes, and only one of them is "the model is too weak".** Smeared faces come mostly from generating at 480x832 with a 4-bit, 8-step model and upscaling: a paid model at native 720p-1080p fixes most of it. Duplicates come from three places (keyframe stills that already contain a second copy, start/end keyframes with characters in different places, and outpainted landscape reframes): paid **reference-to-video** models (Kling O3 "elements", Seedance, Vidu Q3, Veo "ingredients") reduce it, but a keyframe QC gate is needed in every tier. Desync is mainly a **workflow** problem (video is generated silent and voices are laid over it): record voices first, cut each clip to the line length, then run a lip-sync pass. No purchase fixes desync without the voice-first workflow.
2. **One pay-per-use account covers almost the whole trial: fal.ai.** It hosts Kling 3.0 / O3, Veo 3.1, Seedance 2.0, Wan 2.6, Hailuo, Vidu Q3, LTX-2.x, sync.so lip-sync, Kling Avatar, OmniHuman, Topaz upscaling and FLUX LoRA training behind one key, prepaid, no subscription, automatable from this container. Buy it first.
3. **Recommended stacks** (per episode = 32 AI clips + 5 code-rendered clips, Ep 1 v4.4 structure, both orientations):
   - **Starter, about $46/episode** (about $200/month at weekly cadence): keep the free Kaggle pipeline for wides, macros and silhouettes; pay Kling 3.0 Turbo Standard (or the cheapest trial winner) for the 19 clips with characters; sync lipsync-2 on close-ups; ElevenLabs Creator voices; Nano Banana Pro to clean keyframes.
   - **Pro, about $114-140/episode** (about $490-600/month): all 32 AI clips paid; Kling O3 reference-to-video for every multi-character shot, Kling 3.0 Turbo Pro 1080p for the rest, Veo 3.1 Fast for 4 hero gags; sync lipsync-2-pro on every visible mouth.
   - **Studio, about $385/episode** (about $1,650/month): Pro plus Seedance 2.0 for group shots, Veo 3.1 Standard hero shots, every shot generated in both orientations, Runway Act-Two for acted hero shots, human voice actors, Topaz finishing.
4. **First 3 purchases:** (1) **fal.ai prepaid credit, $30** (runs the whole 5-shot trial and LoRA training); (2) **ElevenLabs Creator, $22 for one month** (voices with direction tags, dialogue, SFX, music; commercial licence; cancel if the creator prefers human voices); (3) **a Gemini API / Google Cloud billing account using the new-customer trial credit** (Nano Banana Pro keyframes and Veo 3.1; $0 out of pocket if the $300 trial applies, which must be verified).
5. **Money honesty.** Even Starter at a weekly cadence (about $200/month) is 4x the $50/month cap `marketing.md` proposed for the first 3 months, and Shorts ad revenue will not cover it in year 1 (section 6). Recommendation: make Episodes 1-3 at **Pro** to pass the launch quality bar, then run weekly at **Starter**, upgrading single hero shots to Pro tools; use Studio only for the launch episode or when a sponsor pays. The creator decides the cap.

---

## 0. Cost model used everywhere (so the numbers can be re-checked)

| Input | Value | Source |
|---|---|---|
| Clips per episode | 37 body clips; **32 are AI image-to-video**, 5 are code-rendered (journal map, paper-cut legend: C04, C05, C27, C28, C29) | `scripts/episode-01-v4.4.md` |
| Clip groups (Ep 1) | **A talking/eating close-ups (6):** C01, C19, C22, C23, C31, C36 · **B multi-character dialogue and reactions (13):** C03, C07, C12, C15, C16, C18, C25, C26, C30, C32, C34, C35, C37 · **C big-motion gags with start+end keyframes (6):** C02, C06, C10, C11, C17, C24 · **D no-face / wide / macro / silhouette (7):** C08, C09, C13, C14, C20, C21, C33 | my grouping of the script's shot list |
| Billed seconds per clip | 5 s (most APIs bill 5 s steps or have 4-6 s minimums; clips are trimmed to 3-5 s in the edit) | [S] per vendor |
| Re-roll factor | Starter 2.0, Pro 1.7, Studio 1.5 (better models fail less; still budget one failed take in two) | [E] |
| Landscape 16:9 | Bible rule: generate landscape only where the portrait composition cannot be re-framed. Starter/Pro: 40% of clips; Studio: 100% | `PRODUCTION-BIBLE.md` GPU rule 4 |
| Episodes per month | 4.3 (weekly goal) | brief |
| Series intro | Made once and reused in every episode: costed as one-time | bible |
| "Per finished minute" in the tables | price per second x 60 x 2 (re-roll) x 1.25 (5 s billed for about 4 s used) = **price/s x 150**, one orientation | [E] |

---

## 1. Comparison table

### 1a. Image-to-video and animation

| Tool (access) | Price model, price date | $ per 10 s | $ per finished min | Limits | API from this container | Commercial / YouTube | 2D anime, identity, multi-character | Lip-sync | Known failure modes | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **Kling 3.0** (Kuaishou) via **fal.ai** | Pay per second. V3 Turbo Standard 720p $0.112/s; V3 Turbo Pro 1080p $0.14/s; **O3 (Omni) Pro reference-to-video** $0.224/s audio off, $0.28 on; 4K $0.42/s [S-off fal pages, 2026-11] | 1.12 / 1.40 / 2.24 | 17 / 21 / 34 | 720p-4K; start + end frame; durations about 3-15 s [M]; "elements" built from up to 4 images or a 3-8 s video per character [S-off kling.ai blog] | **Yes** via fal (one key). Kling's own API signs a JWT from access key + secret key on the client [M], which does not fit the proxy-injected key model: use fal | Paid Kling web plans: unrestricted commercial use; free plan non-commercial + watermark [S, quoting kling.ai payment policy 2026-04-21]. Via fal: fal terms + model terms (verify) | Kling says O3 locks each character in group scenes and V3 handles 3+ character coreference [S-off, vendor claim]; no independent anime test | Native audio lip-sync needs a human-like face; one vendor test says Kling's lip-sync tool cannot find cartoon faces [S, competitor blog] | Identity merge when characters touch; style re-render; drift late in long clips [S generic] | **Primary candidate** (Pro, Starter) |
| Kling web plans | Standard $6.99 first month then $8.80/mo, 660 credits; Pro about $24-37/mo, 3,000 credits; Premier about $92/mo, 8,000 [S, 2026 blogs]; V3 6 credits/s at 720p no audio, 8 at 1080p [S] | about 0.50-0.80 | 8-12 | as above; credits expire monthly | Web UI only (Kling 4.0 adds MCP/CLI hooks [S], unverified) | as above | as above | as above | as above | Manual top-up option only |
| **Kling 4.0** | General availability reported 2026-10-15 (sources conflict); 30 s clips, 10 keyframes, multi-reference, lip-sync, MCP/CLI [S]. Official API price not published; reseller about $0.157/s [S] | about 1.57 (unverified) | about 24 | 30 s native | Reseller APIs; fal coverage to confirm | as Kling | 10 keyframes per clip would help gag timing | multilingual lip-sync claimed | new model, no track record | Trial in round 2 if on fal |
| **Veo 3.1** (Google) via Gemini API, Vertex AI or fal | Pay per second. Lite $0.05 (720p) / $0.08 (1080p); Fast $0.10 / $0.12 / $0.30 (4K) after an April cut; Standard $0.40 (720p-1080p), $0.60 (4K); not on the Gemini free tier [S, the-decoder / benchlm; a third source lists lower Lite/Fast prices] | 0.50-0.80 / 1.00-1.20 / 4.00 | 7.5-12 / 15-18 / 60 | 4, 6 or 8 s [M]; 9:16 and 16:9; first + last frame; up to 3 reference images (not on Fast per one guide) [S]; model IDs in preview [S] | **Yes** (Gemini API key in a header; Vertex needs a service-account file, avoid) | Google terms; invisible SynthID watermark [M] | Strong motion and lighting; anime fidelity unknown. **Risk [M]:** Veo image-to-video has had person-generation limits for images of people in some regions; a child cartoon character may be refused | Native speech generation exists but would not use our cast's voices; generate silent | Over-cinematic camera, style drift toward 3D [M] | **Hero shots** (Pro Fast, Studio Standard) |
| **Seedance 2.0 / 2.5** (ByteDance) via BytePlus ModelArk, fal, Dreamina | Token-billed. 2.0 at 720p: about $0.11-0.30/s by reseller (fal $0.3034/s, fast $0.2419; BytePlus derived about $0.15) [S]. 2.5 (launched 2026-07-31): $10.70 per M tokens without video input [S], 30 s per run, up to 50 references (30 images), API 480p/720p only; 2.5 Flash announced 2026-11-12, no price [S] | 1.12-3.03 (2.0) | 17-45 | 2.0 up to 15 s [S]; 2.5 up to 30 s | **Yes** (fal key, or BytePlus key) | BytePlus terms, verify; ByteDance-hosted data | Vendor claims strong cross-shot identity with many references; no anime test | Native audio; no cast-voice lip-sync | unknown for 2D; 720p cap on 2.5 | **Multi-character candidate** (Studio, trial) |
| **Hailuo 2.3 / MiniMax H3** via MiniMax API, fal, Krea | 2.3: 768p 6 s $0.28, 1080p 6 s $0.49, Fast 768p 6 s $0.19 [S, Krea/Novita]; H3 base $0.08/s (768p), $0.13/s (2K); H3 Lite $0.04/s [S, one blog dated 2026-10-30] | 0.32-0.82 (2.3); 0.40-1.30 (H3) | 5-12 | 2.3: 1080p only 6 s, 10 s at 768p [S]; 2.3 reported moving to legacy [S] | **Yes** | MiniMax terms, verify | Expressive physics [M]; no anime evidence | none built in | unknown | Cheap trial entrant |
| **Wan 2.6 / 2.7** (Alibaba) via fal, Alibaba Cloud, RunPod | Wan 2.6: $0.10/s (720p), $0.15/s (1080p); Flash $0.05 / $0.075 [S-off fal + Alibaba Cloud] | 1.00-1.50; Flash 0.50-0.75 | 15-22; Flash 7.5-11 | reference-to-video endpoint exists [S-off fal] | **Yes** | Wan 2.2 open weights Apache-2.0 (motion-tech.md); 2.6 hosted terms verify | In our own Kaggle test FastWan 2.2 re-rendered the scene and lost the Uncle's design (motion-tech.md) | none (see Wan-S2V below) | design drift | Cheap fallback for group D |
| **LTX-2 / LTX-2.5** (Lightricks) via fal or LTX API | LTX-2 Pro $0.06/s 1080p, Fast $0.04/s; LTX-2.5 Pro $0.12 (720p) / $0.17 (1080p), Fast $0.09 / $0.13 [S-off fal + ltx.io] | 0.40-0.60 (2); 0.90-1.70 (2.5) | 6-9; 13-25 | Fast up to 20 s; audio on by default (switch off) [S-off] | **Yes** | LTX licence free under US$10M revenue (motion-tech.md) | Same family as our free pipeline: easiest continuity; anime unknown | "lip-sync" tag on 2.5, unexplained [S] | same as LTX 0.9.8 but at higher res | Cheap upgrade for group D |
| **Runway Gen-4.5 / Act-Two** | Plans: Standard $15/mo (625 credits), Pro about $35, Max $95/mo ($76 annual); Unlimited replaced by Max from 2026-06-01; Gen-4.5 12 credits/s, Act-Two 5 credits/s; API credits $0.01 [S] -> Gen-4.5 about $0.12/s, Act-Two about $0.05/s | 1.20 (API) / 2.88 (Standard plan) ; Act-Two 0.50 | 18 ; Act-Two 7.5 | 5 or 10 s [M]; Act-Two needs a driving performance video | **Yes** (developer API, separate credits) | paid plans commercial [M] | Act-Two transfers a performed face/body/hands onto a reference image, stylized art supported [S, vendor] | **Act-Two = performance-driven mouth and face** | needs a human performance video; no cartoon test found | **Studio**: 3-4 acted hero shots |
| Luma Ray3.x | API billed per 5 s block; Ray3.2 about $0.30 per 5 s at 720p, $1.20 at 1080p [S, conflicting]; Dream Machine subs separate from API [S-off] | 0.60-2.40 | 9-36 | | Yes | verify | no anime evidence | none | | Not in first wave |
| **Vidu Q3** (ShengShu) via fal, WaveSpeed, Krea | Reference-to-video $0.07/s at 360-540p, 2.2x at 720p/1080p (= $0.154/s) [S-off fal] | 0.70 / 1.54 | 10 / 23 | 1-4 reference images per shot (one page says up to 7 subjects) [S] | **Yes** | verify | Krea's docs call it a model "excelling at anime" [S]; only anime-positioned commercial model found | none | unknown | **Anime-specific trial entrant** |
| Midjourney V1 video / Niji 7 | Plans from $10/mo; a video job about 8 GPU-min for 4 SD clips, 26 for 4 HD [S-off docs]; Niji 7 anime image model since 2026-01 [S]; Omni-reference for characters [S] | about 0.15 [E] | about 2 [E] | SD/HD (about 480p-720p [S]), 5-21 s | **No API**; automation via bots breaks the terms [M] | paid plans; companies over $1M revenue need Pro/Mega [M] | Niji 7 is a strong anime keyframe tool | none | low resolution video | Optional manual keyframe exploration only |
| Sora 2 | API shut down 2026-09-24 per OpenAI's model page [S-off]; last price sora-2 $0.10/s, sora-2-pro $0.30-0.70/s | n/a | n/a | | No | | | | | **Not available** |
| Higgsfield (aggregator) | Credit plans; tiers and prices conflict across sources ($5-$59+); "unlimited" models only on the website, not via MCP/CLI; Seedance 2.0 1080p 5 s = 45 credits [S] | varies | | | MCP/CLI exist but metered | paid tiers commercial; Starter may exclude commercial use and Seedance [S] | resells Kling/Seedance | via resold models | | Skip (markup; unlimited not automatable) |
| Krea (aggregator) | Basic $9 (5,000 CU), Pro $35, Max $70, Business $200 [S]; API Kling 3.0 standard about $0.176/s [S-off docs] | | | | Yes | verify | resells | | | Skip (fal is cheaper) |
| Freepik / Magnific, Leonardo | Premium+ about $33.75/mo annual, video metered (Runway 4.5 = 1,100 credits per 5 s) [S]; Leonardo $12/$30/$60, API separate [S] | | | | Leonardo API yes | verify | resellers | | | Skip for video |
| Pika | Standard $8 (700 credits) to Fancy $76 (annual) [S, June 2026] | | | | limited | paid tiers commercial [S] | effects, weak identity [M] | | | Skip |
| DomoAI, Viggle | No reliable 2026 prices found | | | | | | Domo = anime style transfer of an existing video; Viggle = motion templates onto a character [M] | Domo claims anime lip-sync [S vendor] | style transfer changes our designs [M] | Skip |
| Replicate / RunPod / Modal (pay-per-use GPUs) | Replicate Kling 2.5 Turbo Pro $0.07/s [S]; RunPod public Wan 2.2 720p about $0.30 per 5 s; pods about $0.34-0.69/h small GPUs (marketing.md); Modal monthly free credit [M] | 0.60-0.70 | 9-10 | | Yes | open-weight licences apply | self-hosted Wan 2.2 14B FLF2V or LTX-2 with our own LoRAs | Wan-S2V self-host | setup time | Later: self-host once the shot recipe is fixed |
| Open anime video models (AniSora, ToonCrafter) | free weights | 0 | GPU only | | self-host | **licences not verified** | anime-trained [M] | | | Research track, not a purchase |

### 1b. Character consistency (keyframes and identity)

| Tool | Price, date | API | What it fixes | Weakness | Verdict |
|---|---|---|---|---|---|
| **Nano Banana Pro** (Gemini 3 Pro Image) via Gemini API or fal | $0.134 per image at 1K/2K, $0.24 at 4K; input images 560 tokens each [S, quoting Google pricing]; Nano Banana 2 about $0.067 [S, unverified] | **Yes** | Up to 14 input images, keeps up to 5 people consistent [S-off Google blog]: feed the model sheet (`tools/episode_maker/gpu/inputs/intro-v3/refs/characters.jpg`) + locked Uncle stills and **edit out duplicates or wrong costumes in keyframes** before any video spend | sometimes ignores refs [S]; may push toward its own style | **Buy (keyframe QC and repair)** |
| **FLUX LoRA training on fal** | FLUX.1 fast trainer $2 per 1,000 steps; FLUX.2 trainer $6.40 per 1,000; klein trainer $0.0043/step = $4.30 per 1,000 [S-off fal, 2026] | Yes | One LoRA per character (Boy, Uncle, Grandma) for the free FLUX.2 klein still pipeline: same face every still (pro-upgrade-plan track A) | check the base model licence (klein 4B vs 9B differ [M]) | **Buy once, about $13** |
| Kling O3 "elements", Vidu Q3 / Seedance / Veo reference images | inside the video price | Yes | identity inside the motion, not only on frame 1 | vendor claims only | Use in Pro/Studio |
| Scenario | Free 50 daily credits; Starter $15, Pro $45 (custom training), Max $75 [S-off help centre, updated 2026-11-22] | Yes | style + character models, team workspace | redundant with fal LoRA | Only if fal LoRA fails |
| Midjourney Niji 7 + Omni-reference | from $10/mo | No | strong anime design exploration | manual, no API | Optional, creator-run |

### 1c. Lip-sync and talking shots

| Tool | Price, date | $ per 10 s | API | Fit for 2D anime | Failure modes | Verdict |
|---|---|---|---|---|---|---|
| **sync.so lipsync-2-pro** (direct or fal) | $0.067-0.083/s by plan, billed on output frames at 25 fps; fal $5/min; lipsync-2 about 1.67x cheaper (fal about $3/min) [S-off sync.so docs] | 0.67-0.83 (pro); about 0.50 (lipsync-2) | **Yes** | Works on an existing video: keeps our animation, replaces the mouth; stylized support claimed by a reseller [S] | "sub-par results with extreme profile angles"; sync-3 handles hard angles better [S-off] | **Primary lip-sync pass** |
| **Kling Avatar 2.0** (fal) | Standard $0.0562/s, Pro $0.115/s [S-off fal] | 0.56 / 1.15 | Yes | image + audio -> talking video, so the mouth matches by construction | needs a human-like face [S]; cartoon detection risk | Trial for group A |
| Kling LipSync (fal) | $0.014 per 5 s [S-off fal] | 0.03 | Yes | video + audio | cannot detect most cartoon faces [S, competitor blog]; about 12 min per job | Trial only (almost free) |
| **Hedra Character-3** | API about $0.05/s at 720p (article dated 2026-11); plans Basic $15 / 1,500 credits, Creator $30 / 5,400, Professional $75 / 14,400; 3-6 credits/s [S, conflicting] | about 0.50 | Yes (prepaid API balance [S-off]) | image-first, reported to suit illustrated faces [S] | lower motion; one-face shots only | **Trial for group A** |
| OmniHuman 1.5 (ByteDance) via fal | $0.16/s [S-off fal] | 1.60 | Yes | image + audio, full-body gestures | cost; style drift unknown | Trial |
| Wan 2.2 S2V | $0.15 per 5 s at 480p, $0.30 per 5 s at 720p (WaveSpeed) [S] | 0.30-0.60 | Yes | open weights (Apache-2.0 [M]) | 14B, too big for a T4 | Cheap trial |
| Runway Act-Two | see 1a, about $0.05/s API | 0.50 | Yes | performance capture onto a still | needs someone to act the line on camera (keep that video private) | Studio hero shots |
| HeyGen | presenter avatars [M] | | Yes | built for realistic presenters | | Skip |
| Open MuseTalk / LatentSync | free | 0 | self-host | licences to verify (pro-upgrade-plan track C) | | Free track |

### 1d. Voices

| Option | Price, date | API | Commercial | Strength / weakness | Verdict |
|---|---|---|---|---|---|
| **ElevenLabs** | Starter $6 (first commercial tier), **Creator $22/mo, about 121,000 credits (about 121 min)**, Pro $99 [S, 2026 blogs, conflicting] | **Yes** (key header `xi-api-key`) | commercial from Starter up; Free has none [S] | Eleven v3 audio tags ([whispers], [laughs], [shouts]) and a Text-to-Dialogue API for multi-speaker scenes [S-off docs]; also SFX and Music in the same account. Weakness: still synthetic; design voices, never clone a real person | **Buy #2** |
| Hume Octave 2 | Creator about $14/mo (first month $7), about 140,000 characters [S] | Yes | paid tiers [M] | emotion-from-prompt acting [M] | Alternate if ElevenLabs sounds flat |
| Cartesia Sonic 3 | Pro $5/mo (commercial starts here), Startup $49, Scale $299; 1 credit per character [S] | Yes | Pro and up | low-latency agent voice, less acting range [M] | Cheap alternate |
| Free open TTS (Qwen3-TTS, Chatterbox) | $0 | runs on Kaggle | MIT/Apache | current default | Keep for scratch tracks |
| **Human voice actors** (Fiverr, Upwork) | Fiverr guide: $75-200 for a project under 2 minutes; broadcast/unlimited rights can double or triple; full commercial packages $500-800 [S-off Fiverr cost guide 2026]; small gigs from $5 per 50-100 words [S, listings] | No (files delivered) | needs a written buyout covering monetized YouTube, Shorts, TikTok, Instagram, perpetual | best comic timing; schedule and re-take delays | **Studio** (per-episode cast budget about $140 [E]) |

### 1e. Music, songs, sound effects

| Option | Price, date | API | Rights | Verdict |
|---|---|---|---|---|
| **Suno** | Pro $10/mo ($8 annual), 2,500 credits; Premier $30 ($24 annual), 10,000; since 2026-09 Pro allows 20 song downloads/mo, Premier 60; model v5.5 [S] | No official API [M]; manual | Commercial use only for songs made while subscribed (no retroactive licence); **usage rights, not ownership**; downloads need a paid plan after the Warner deal [S] | **One month of Pro for the Japanese punk intro song**, keep ACE-Step as the free fallback |
| Udio | After its label settlement it became a closed fan platform; download/commercial terms unclear [S] | | | Avoid |
| ElevenLabs Music | in the ElevenLabs plan | Yes | self-serve commercial use allowed except film/TV/radio/games; no distribution to music streaming platforms [S-off terms] | Use for cues (included in #2) |
| ElevenLabs Sound Effects | in plan credits (exact credit cost not found) [S] | Yes | as above | Use for designed SFX |
| CC0 libraries (Freesound CC0, game-audio bundles) | free | | check each file's licence [M] | Keep |

### 1f. Upscaling, face repair, finishing

| Option | Price, date | API | Note | Verdict |
|---|---|---|---|---|
| Real-ESRGAN anime + RIFE (current, free) | $0 | local | RIFE bug must be fixed (motion-tech.md) | Keep in every tier |
| **Topaz Starlight** via fal | Precise 2.5 $1.20 per 10 s up to 1080p, $2.60 per 10 s at 4K; Fast at half [S-off fal] | Yes | generative upscale can rebuild soft faces but may alter the design: QC against the model sheet | Pro (selected shots), Studio |
| Topaz Video desktop | about $299/yr (Video AI discontinued 2025-09) [S] | No | needs a local GPU PC | Skip |
| GFPGAN / CodeFormer face restore | free | local | trained on photo faces, poor on anime; CodeFormer licence is non-commercial [M] | **Do not use** |
| DaVinci Resolve | Free; Studio $295 one-time [S] | No | creator-side grade and final check | Free version is enough; Studio optional |
| CapCut Pro | $7.99-19.99/mo by region [S]; its terms grant CapCut a broad licence over uploaded content [S] | No | quick captions/templates | Avoid for masters; ffmpeg pipeline stays the automated finisher |

---

## 2. Three recommended stacks

All three stacks share these **free fixes** (no purchase, do them first): voice-first animatic (voices recorded, every clip's length set from its line), keyframe QC gate (contact sheet + anime-face count per keyframe, reject any frame with an extra character), fixed RIFE for 24 fps, one character per prompt name ("the Uncle" said once, never two descriptions of him), no outpainting of characters in landscape reframes, max 2 main characters per AI clip unless a reference-to-video model is used.

### 2.1 Starter: at most $50 per episode

| Shot group (Ep 1) | Tool | Why |
|---|---|---|
| D wides, macros, silhouette (7) + code clips (5) | **Free**: LTX-Video 0.9.8 on Kaggle; code renders | no faces to smear |
| A close-ups (6) and B multi-character (13) | **Kling 3.0 Turbo Standard 720p via fal** (or the cheapest trial winner scoring 3.5+: Hailuo 2.3 Fast, Wan 2.6 Flash, Veo 3.1 Lite) | native 720p faces, start+end frame |
| C big gags (6) | Free LTX 0.9.8 (start+end keyframes worked there, motion-tech.md); re-roll on Kling if QC fails | saves money |
| Talking close-ups (10 shots incl. 4 tight two-shots) | **sync lipsync-2** via fal | mouth matches the WAV |
| Keyframes | free FLUX.2 klein + **character LoRAs (fal)**; **Nano Banana Pro** to repair the ~19 paid keyframes | no duplicates going in |
| Voices | **ElevenLabs Creator** (v3 tags, dialogue) | performance + timing |
| Music | ACE-Step (free) | |

| Cost line (per episode) | Arithmetic | USD |
|---|---|---|
| Kling 3.0 Turbo Std | (19 portrait + 8 landscape) clips x 5 s x 2.0 = 270 s x $0.112 | 30.20 |
| sync lipsync-2 | 14 clips x 5 s x 1.5 = 105 s x $0.05 | 5.25 |
| Nano Banana Pro | 19 x 1.4 orientations x 1.5 = 40 images x $0.134 | 5.40 |
| ElevenLabs Creator | $22 / 4.3 episodes | 5.10 |
| **Total** | | **about 46** |
| One-time | 3 LoRAs about $13; intro upgrade (6 shots x 2 orientations x 5 s x 2 x $0.14) about $17; Suno Pro one month $10 | about 40 |
| **Monthly (weekly cadence)** | 4.3 x $46 | **about $200** (biweekly about $100) |

### 2.2 Pro: at most $150 per episode

| Shot group | Tool |
|---|---|
| B multi-character (13) | **Kling O3 Pro reference-to-video** with one element per character (Boy, Uncle, Grandma) |
| A close-ups (6) and C gags (6) | **Kling 3.0 Turbo Pro 1080p** with start + end frame |
| 4 hero gags (C10 salute, C11 slide-in, C17 training arc, C24 golden levitation) | **Veo 3.1 Fast** 1080p, first + last frame (if the trial shows Veo accepts the Boy) |
| D (7) | Wan 2.6 Flash or LTX-2 Fast (cheap, 720p-1080p) |
| All visible mouths (19 portrait + 8 landscape) | **sync lipsync-2-pro**; for single-face lines, Hedra Character-3 or Kling Avatar Pro if they win the trial |
| Keyframes | LoRAs + Nano Banana Pro for every keyframe |
| Finishing | Topaz Starlight Fast on 720p shots only |
| Voices / music | ElevenLabs Creator; Suno Pro for cues |

| Cost line (per episode) | Arithmetic | USD |
|---|---|---|
| Kling O3 Pro (group B) | 157 s x $0.224 (41% of 382 s) | 35.00 |
| Kling 3.0 Turbo Pro (A + C) | 143 s x $0.14 | 20.00 |
| Wan 2.6 Flash / LTX-2 Fast (D) | 83 s x $0.05 | 4.20 |
| Veo 3.1 Fast hero gags | 6 clips x 6 s x 1.7 = 61 s x $0.12 | 7.30 |
| sync lipsync-2-pro | 27 clips x 5 s x 1.4 = 189 s x $0.083 | 15.70 |
| Nano Banana Pro | 67 images x $0.134 | 9.00 |
| Topaz Starlight Fast (selected) | about 80 s x $0.06 | 5.00 |
| ElevenLabs Creator + Suno Pro | ($22 + $10) / 4.3 | 7.40 |
| Contingency 10% | | 10.40 |
| **Total (40% of clips also generated in 16:9)** | | **about 114** |
| **Total (every clip also generated in 16:9)** | + 19 clips x 5 s x 1.7 x about $0.17 | **about 140** |
| **Monthly (weekly)** | 4.3 x $114-140 | **about $490-600** |

### 2.3 Studio: at most $400 per episode

| Shot group | Tool |
|---|---|
| B multi-character (13, both orientations) | **Trial winner of Seedance 2.0/2.5 vs Kling O3 Pro** (up to 30 references on 2.5) |
| A + C (12, both orientations) | **Kling 4.0** (10 keyframes per clip, if on fal) else Kling 3.0 Turbo Pro |
| 6 hero shots (cold open C01, C10, C17, C24, the hat cliffhanger C35, the sting C37) | **Veo 3.1 Standard**, 6 s, both orientations |
| 3-4 acted hero shots (C24 quiet line, C10 salute) | **Runway Act-Two** driven by a private performance video, then lip-sync check |
| D (7, both orientations) | LTX-2.5 Pro 1080p or Wan 2.6 |
| All visible mouths | sync lipsync-2-pro (or sync-3 for profiles) |
| Voices | **Human voice actors** (Boy, Uncle, Narrator, local guest), ElevenLabs for scratch/animatic |
| Finishing | Topaz Starlight Precise on hero shots; DaVinci Resolve grade |
| Music | Suno Premier (60 downloads) + ElevenLabs SFX |

| Cost line (per episode) | Arithmetic | USD |
|---|---|---|
| Group B video | 26 clips x 5 s x 1.5 = 195 s x about $0.26 | 51.00 |
| Group A + C video | 180 s x about $0.157 | 28.00 |
| Group D video | 105 s x about $0.15 | 16.00 |
| Veo 3.1 Standard heroes | 12 clips x 6 s x 1.5 = 108 s x $0.40 | 43.00 |
| Runway Standard (Act-Two) | $15 / 4.3 | 3.50 |
| sync lipsync-2-pro | 38 clips x 5 s x 1.3 = 247 s x $0.083 | 20.50 |
| Human voice cast | about 4 actors, recurring-cast rate [E, Fiverr ranges] | 140.00 |
| ElevenLabs Creator (scratch) | | 5.10 |
| Nano Banana Pro | 96 images x $0.134 | 13.00 |
| Topaz Starlight Precise (heroes) | | 15.00 |
| Suno Premier | $30 / 4.3 | 7.00 |
| DaVinci Resolve Studio (optional, amortized over 39 episodes) | $295 / 39 | 7.60 |
| Contingency about 10% | | 35.00 |
| **Total** | | **about 385** |
| **Monthly (weekly)** | 4.3 x $385 | **about $1,650** |

---

## 3. What each stack fixes (and what it does not)

| Defect | Root causes seen in v4.4 | Starter | Pro | Studio | Still NOT fixed by any stack |
|---|---|---|---|---|---|
| **Duplicated characters, extra people, doubled limbs** | (1) keyframe stills from FLUX.2 klein already contain a second copy; (2) start and end keyframes place a character in different spots, the model "morphs" by spawning a second copy; (3) prompts that describe the same character twice; (4) outpainted landscape reframes that paint an extra character into the new area [E, hypotheses to confirm on the v4.4 clips] | **Mostly fixed for 1-3**: LoRA + Nano Banana Pro keyframe repair + QC gate + one name per character. Single-image video models still invent extras in 2-3 character shots: those 13 shots stay the main risk | **Largely fixed**: every multi-character shot uses reference-to-video with one element per character, so the model knows "exactly these three people". Duplicates should drop to occasional re-rolls | Same as Pro plus a second reference model (Seedance) for the hardest group shots, and both orientations generated natively (no outpainting) | Crowds and background extras; characters touching or overlapping (identity merge at contact points is a known weak spot [S]); hands crossing faces; fast chases. Keep these staged or code-rendered |
| **Smeared / melting faces** | 480x832 generation with a 4-bit, 8-step model; camera zoom; faces small in frame; Real-ESRGAN upscale; broken RIFE frames (stripes) | **Fixed on the 19 character shots** (native 720p, no 4-bit); still possible on the free LTX gags and wides | **Fixed on all AI shots** (1080p on A/C, reference model on B, Topaz on 720p leftovers) | Fixed, plus Topaz Precise and grade on heroes | Faces at very high speed (chase), eating shots where food covers the mouth, the hat shadow over the Boy's eyes; any model drifts after about 5 s, so keep clips short |
| **Out-of-sync mouths and action** | Clips generated silent and of fixed length; voices laid on top; no lip-sync; action beats not timed to lines | **Fixed for close-ups** (voice-first timing + lipsync-2); two-shots and wides keep generic mouth motion | **Fixed on every visible mouth** (lipsync-2-pro or audio-driven Hedra/Kling Avatar for single-face lines); action beats timed from the animatic | Plus Act-Two performance for the quiet/acted moments and human voices with real comic timing | Two characters talking in the same 4 s clip (most lip-sync tools drive one face per pass: split the clip or do two passes); overlapping banter; profile views; chewing while talking. Mouths on the Dad silhouette are never shown (by design) |

---

## 4. Purchase order, trial and decision rules

### 4.1 What to buy, in order

| # | Purchase | Cost | Why first | How to keep it cheap |
|---|---|---|---|---|
| 1 | **fal.ai prepaid credit** | $30 (no subscription) | one key, all trial models, lip-sync, LoRA training, Topaz | prepaid balance only; no auto top-up; per-model test cost below |
| 2 | **ElevenLabs Creator** | $22, one month | voice-first animatic is the cheapest desync fix; v3 tags + dialogue + SFX + music | cancel before renewal if human voices are chosen; listen-test on the free tier first (free output is non-commercial, never publish it) |
| 3 | **Gemini API / Google Cloud billing account** | $0 if the new-customer $300, 90-day trial covers it [S-off cloud.google.com]; whether Veo on Vertex is covered must be verified | Nano Banana Pro keyframes; Veo 3.1 hero shots | set a budget alert at $20; use the Gemini API key route (simpler than Vertex) |
| 4 (after the trial) | the winner's plan: usually stay on fal pay-per-use; a Kling web plan only if the creator wants to iterate by hand | $0-37/mo | | monthly plans only, cancel any time |
| 5 (Pro) | sync.so direct plan if lip-sync volume makes it cheaper than fal | about $5/min of output | | |
| 6 (Studio) | Runway Standard (Act-Two), Suno Premier, voice actors | $15 + $30 + per job | | one month at a time |

Free credits to use before paying (verify each): Google Cloud trial credit (new customers only); Kling developer trial (about $1 reported [S]); Kling web daily free credits (watermarked, non-commercial: for eyeballing only); Scenario 50 daily credits; Hedra and ElevenLabs free tiers (non-commercial); Hume first month $7; Kling Standard first month $6.99. **Never publish anything generated on a free tier.**

### 4.2 The 5 test shots (run on every candidate, identical inputs)

Inputs live in `tools/episode_maker/gpu/inputs/ep01v44-clips-1/images/` (portrait `Cxx.jpg` / `Cxx_end.jpg`, landscape `_land`), the cast sheet is `tools/episode_maker/gpu/inputs/intro-v3/refs/characters.jpg`, and the locked Uncle is intro-v3 variant 2 (bible). **Step 0:** check each start/end still for duplicates; if one has a defect, repair it once with Nano Banana Pro and use the repaired still for every candidate (so the test measures the video model, not the still).

| Test | Source shot | What it stresses | Inputs | Prompt core (same text for all; camera sentence first) |
|---|---|---|---|---|
| **T1 Two-shot banter** | C10 "Veterans." | duplicates with 2 characters side by side, identity of both, deadpan vs manic acting | C10.jpg -> C10_end.jpg; refs: cast sheet | "The camera stays still. The big fat bald Uncle with a thin mustache snaps a trembling salute, anime waterfall tears pour, his mustache quivers; the small boy in the conical leaf hat beside him slowly turns his head to him, deadpan. Exactly two characters." |
| **T2 Talking close-up** | C36 "Dad was right..." | face stability on a child face under the hat, subtle acting, then lip-sync | C36.jpg -> C36_end.jpg + `boy` WAV of the line | "The camera stays still. Soft close-up of the small boy in the conical leaf hat; he takes a quiet breath, a small tender smile settles, his eyes come to the lens; the orange hat ribbon stirs. Nothing else moves." |
| **T3 Keyframe gag, big pose change** | C01 cold open | smear between two poses, sweat drop and steam effects, comic timing | C01.jpg -> C01_end.jpg | "Slow pull-back. The Uncle on a small stool, ice pack on his cheek: his right eye twitches, a giant sweat drop slides down his head, his lip trembles, then he lifts his chin and crosses his arms in wounded dignity; one tiny puff of steam from his left ear." |
| **T4 Three characters + hands + food** | C17 "That's a sock." | 3 identities (Grandma is the worst for drift), hands, dough, duplicates | C17.jpg -> C17_end.jpg; refs: cast sheet + Grandma still | "The camera stays still. At the counter the Uncle pinches dough with trembling intensity, it stretches, wraps his thumb and pops; he thrusts a lumpy dumpling up in triumph. Grandma behind the counter stays flat-faced; the small boy stares, dead-eyed. Exactly three characters." |
| **T5 Fast motion chase** | intro chase (I5_chase variant 2) | faces and bodies at speed, camera tracking, duplicates in motion, both orientations | the I5_chase__v2 still (from the intro-v3 Kaggle results) or a Nano Banana Pro regeneration from the cast sheet | "The camera tracks them. The small boy in the conical leaf hat and the big fat Uncle sprint toward the lens through an old town street, truly scared, wide eyes, open mouths; behind them a giant white pleated dumpling with steam and a big chomping mouth bounces after them." |

Fixed settings for fairness: 9:16 at the model's 720p tier (plus T5 also in 16:9), 5 s (Veo 6 s), audio OFF, same seed where the API allows, 1 take in round 1, 2 takes in round 2, no prompt tuning per vendor in round 1 (tuning is round 2).

Lip-sync screen: run T2 (the best video take) and the T1 Uncle line through sync lipsync-2, lipsync-2-pro, Kling LipSync; and run the T2 still + WAV through Hedra Character-3, Kling Avatar 2.0 Pro, OmniHuman 1.5, Wan 2.2 S2V. Total about $4.

### 4.3 Trial cost

| Round | What | Approx. cost |
|---|---|---|
| 0 | 3 LoRAs (fal) + 15 Nano Banana Pro repairs | $13 + $2 |
| 1 | 5 shots x 1 take on: Kling 3.0 Turbo Std ($2.80), Kling O3 Pro ref ($5.60), Veo 3.1 Fast ($3.00), Veo 3.1 Lite ($1.50), Seedance 2.0 fal ($7.60), Hailuo 2.3 Fast ($1.00), Wan 2.6 Flash ($1.25), Vidu Q3 ref ($3.85), LTX-2.5 Fast ($2.25) | about $29 |
| 1b | lip-sync screen | about $4 |
| 2 | top 2 video models x 5 shots x 2 takes x 2 orientations, prompt-tuned | about $40 |
| **Total** | | **about $90** (round 0 + 1 alone: about $50) |

### 4.4 Scoring sheet (copy per candidate)

Score each take 0-5. Weighted total out of 5. A take with a duplicate character or an extra limb scores 0 on that criterion automatically.

| Criterion | Weight | T1 | T2 | T3 | T4 | T5 | Mean |
|---|---|---|---|---|---|---|---|
| Identity match to the cast sheet (face, hat, sash, Uncle's body) | 25% | | | | | | |
| No duplicates / extra people / extra limbs | 20% | | | | | | |
| Face stability (no smear, no melt, eyes stay put) | 20% | | | | | | |
| Acting and motion (expressions, comic timing, physics) | 15% | | | | | | |
| Adherence (reaches the end keyframe, follows the prompt, camera) | 10% | | | | | | |
| Style fidelity (soft watercolor anime, line art, palette; no 3D drift, no text) | 10% | | | | | | |
| **Weighted score** | | | | | | | |
| Usable takes / total takes | gate | | | | | | |
| Cost per usable second (price x takes / usable seconds) | gate | | | | | | |
| API from container, commercial licence, child character accepted | gate (yes/no) | | | | | | |

Lip-sync sheet (T2 and T1 line): sync accuracy on plosives (p/b/m), mouth shape stays in style (no realistic teeth/lips), rest of the face unchanged, no flicker at clip edges, works on the Uncle's mustache. 0-5 each.

### 4.5 Decision rules

- **Adopt a video model for a tier** if: weighted score at least 3.8; zero duplicates in at least one of two takes on T1 **and** T4; T2 face score at least 4; usable-take rate at least 50%; cost per usable second within the tier's line in section 2; all gates "yes".
- **Group B (multi-character) goes to the model with the best T1 + T4 duplicate and identity scores**, even if it costs more: this is the creator's top defect.
- **Lip-sync:** adopt the tool with the best T2 score that keeps the face in style; if no tool scores at least 3.5 on anime mouths, keep the free fallback (stage mouths small or off-camera, stylized mouth-flap overlay) and do not buy.
- **Stop rule:** if no candidate passes, do not buy a plan; spend on the free fixes (LoRA, QC gate, voice-first) and re-test in 4-6 weeks (new models arrive monthly).
- Show the creator a side-by-side contact video of the 5 shots per finalist before any monthly plan (the creator approves results, CLAUDE.md rule 3).

---

## 5. Accounts, API keys and rights

### 5.1 Sign-up steps for the creator (in this order)

1. Use only the business identity for every account: **thedumplingboy.studio@gmail.com**, display name "The Dumpling Boy". Turn on two-factor login. Payment details stay private with the vendor; never type them into chat or any file.
2. **fal.ai**: sign up, add $30 prepaid credit, keep auto top-up OFF, create one API key named for this project.
3. **ElevenLabs**: subscribe to Creator (monthly). Create an API key with only the permissions needed (text to speech, dialogue, sound effects, music) [M: scoped keys exist; verify].
4. **Google AI Studio / Google Cloud**: create a project, enable billing (trial credit if eligible), set a budget alert, create a Gemini API key restricted to the Generative Language API.
5. Later only if chosen: sync.so, Hedra, Runway developer portal, Suno (manual only, no key), Fiverr/Upwork client profile under the channel name.

### 5.2 Giving a key to Claude safely

- **Never paste a key into chat, a commit, a file, a Kaggle notebook, a GitHub issue or a script.** CLAUDE.md rule 4 applies to every vendor, not only Netlify.
- When the creator says "the fal key is ready", Claude opens the environment's **secure credential form** for that exact host; the creator types the key only into that form. The key is stored on the cloud environment and the network proxy adds it to requests to that host; Claude never sees it and the code uses a dummy value (as with `Authorization: Bearer proxy-injected` for Netlify).
- Hosts and headers to request [M, confirm on each vendor's API docs at setup]:

| Vendor | Host | Header (prefix) |
|---|---|---|
| fal.ai | `queue.fal.run` (and `fal.run`) | `Authorization` (prefix `Key`) |
| Google Gemini API | `generativelanguage.googleapis.com` | `x-goog-api-key` |
| ElevenLabs | `api.elevenlabs.io` | `xi-api-key` |
| sync.so | `api.sync.so` | `x-api-key` |
| Hedra | `api.hedra.com` | `X-API-Key` |
| Runway | `api.dev.runwayml.com` | `Authorization` (prefix `Bearer`) |

- fal returns result files on a separate media host (e.g. a `fal.media` CDN host [M]); those downloads need no key but the host must be allowed in the environment's network settings. Claude will propose that exact host through the environment approval prompt the first time a download is blocked; the creator approves it there.
- Kling's own API (access key + secret key signed into a token on the client [M]) cannot use proxy injection without putting the secret in the sandbox: use Kling through fal instead.
- If a job must run in GitHub Actions instead of this container, the creator adds the key as an Actions secret in the GitHub web settings personally. Not needed for this plan: paid APIs need no GPU, so calls run from the cloud container directly (no Kaggle start-up cost).
- After the trial: revoke keys of tools not adopted; rotate kept keys every 6 months.

### 5.3 Legal and commercial-rights checklist (per tool, before the first monetized upload)

- [ ] **Paid tier at generation time.** Kling, Higgsfield, Pika, Suno, ElevenLabs, Cartesia and Midjourney grant commercial use only on paid plans, and Suno does not license free-plan songs retroactively [S]. Nothing from a free tier goes into a published video.
- [ ] **API route terms.** When a model is used through fal (or Replicate), read fal's terms on output ownership and the model owner's terms that pass through (Kling, Google, ByteDance, MiniMax, Alibaba, Lightricks). Save a PDF copy with the date in the creator's private records (not in the repo if it contains account details).
- [ ] **Ownership is not the same as permission.** Suno grants usage rights, not ownership [S]; AI-only output may not be protectable by copyright in the US [M]; the protectable parts are our scripts, edits, designs and voice performances. Do not register AI-only music in Content ID [M: high claim-dispute risk].
- [ ] **ElevenLabs Music** may not be distributed to music streaming platforms and is not for film/TV/radio/games on self-serve plans [S-off]. YouTube episodes are fine.
- [ ] **YouTube.** Since the July 2026 clarification of the inauthentic-content policy, AI use is allowed but channels of generic, repetitive, mass-produced content can lose monetization channel-wide [S, Tubefilter/TechRepublic]. Keep proof of human creative input per episode (script, storyboard, animatic, edit notes, voice direction). The altered/synthetic disclosure is for realistic content; clearly animated cartoons are reported as exempt [S, VERIFY in the upload form]. Keep the "made for kids" decision memo from `marketing.md` 1.4.
- [ ] **Voices.** No cloning of any real person. Human actors sign a short written agreement: work-for-hire or buyout covering YouTube (monetized), Shorts, TikTok, Instagram, the site and trailers, worldwide, perpetual; whether their voice may be used to train or clone (default: no); credit line wording (the channel's public name only for us). Pay through the platform under the channel name.
- [ ] **Act-Two performance videos** (a person acting a line) are kept private and deleted after use; only the cartoon result is published.
- [ ] **Licences of open models** used next to paid tools: LTX (under US$10M revenue), FLUX.2 klein variant, Real-ESRGAN, RIFE, any lip-sync model; re-check before the first monetized upload (motion-tech.md, voice-tech.md).
- [ ] **Watermarks.** Veo adds invisible SynthID [M]; do not try to remove watermarks from any tool.
- [ ] **Licence log per episode** in `production/` (tool, model version, plan, date, shot IDs). Contains no account names, emails or keys.
- [ ] **Anonymity check** before any commit: `grep` for the personal name must be empty (CLAUDE.md rule 1).

---

## 6. Break-even view: AI stacks versus a freelance animator

| Option | Per episode (about 2.5 min body) | Per finished minute | Weekly for a month | Quality / risk |
|---|---|---|---|---|
| Free pipeline (v4.4) | about $0 + creator time | $0 | $0 | the three defects |
| **Starter** | about $46 | about $18 | about $200 | defects reduced on character shots |
| **Pro** | about $114-140 | about $45-56 | about $490-600 | defects largely fixed |
| **Studio** | about $385 | about $155 | about $1,650 | best AI result + human voices |
| AI Studio + freelance cleanup artist (repaint 5-8 bad frames/shots, $45-90/h, 3-5 h) | about $520-835 | about $210-335 | about $2,200-3,600 | closes the last 10% |
| **Freelance 2D animator, full episode** | about $5,000-12,500 (at $2,000-5,000 per finished minute for quality freelance 2D; studio character animation $8,000-20,000 per minute) [S, vendor rate guides 2026; hourly $45-90 mid-level] | $2,000-5,000 | $21,500-54,000 | best quality; weeks of turnaround; one orientation |

Readings:
1. **A full freelance episode costs 13x (vs Studio) to 270x (vs Starter) more** than an AI stack. At a weekly cadence there is no break-even point: a human animator is not a substitute, only a complement.
2. **Where a human pays off: the series intro.** It is reused in every episode (39 planned). A hand-animated 8-12 s opening at about $1,500-3,000 [E] amortizes to about $40-80 per episode over the season and is the most-watched 10 seconds of the channel. Consider it once there is income or a sponsor.
3. **Revenue reality** (from `marketing.md`): Shorts RPM about $0.03-0.10 per 1,000 views. To pay for one Starter episode from Shorts ads takes about 0.5-1.5 million views; Pro about 1.1-4.7 million; Studio about 3.9-12.8 million, and only after YPP eligibility. In year 1 the spend is an investment funded by the creator, sponsors or Ko-fi, not by ads.
4. **Budget recommendation:** Episodes 1-3 (launch arc) at **Pro** (about $340-420 total, plus the about $90 trial and about $40 one-time). Then weekly **Starter** (about $200/month) with up to 4 hero shots per episode on Pro tools (+$10-15). Studio only for the launch episode or a sponsored episode. This exceeds the $50/month cap in `marketing.md`; the creator must choose: raise the cap, go biweekly (halves every monthly figure), or stay free and accept the defects.

---

## 7. Sources (all opened via search snippets on 2026-11-26)

Video: https://fal.ai/models/fal-ai/kling-video/v3/turbo/standard/image-to-video · https://fal.ai/models/fal-ai/kling-video/v3/turbo/pro/image-to-video/llms.txt · https://fal.ai/models/fal-ai/kling-video/o3/pro/reference-to-video/playground · https://fal.ai/kling-3 · https://kling.ai/blog/kling-3-subject-binding-character-consistency · https://kling.ai/quickstart/klingai-video-3-omni-model-user-guide · https://kling.ai/blog/kling-v3-vs-o3-comparison-guide · https://eesel.ai/blog/kling-ai-pricing · https://magichour.ai/blog/kling-ai-pricing · https://kling.ai/docs/payment-policy · https://www.atlascloud.ai/blog/tips/kling-ai-api-pricing · https://kie.ai/blog/kling-4-0-release-analysis-30-second-clips-keyframes-pricing · https://letsdatascience.com/news/kling-ai-opens-kling-40-to-all-users-d9dc6422 · https://the-decoder.com/googles-veo-3-1-lite-cuts-video-generation-costs-by-more-than-half/ · https://benchlm.ai/md/media-pricing/veo.md · https://wavespeed.ai/blog/cost-and-billing/google-veo-3-pricing/ · https://developers.googleblog.com/en/introducing-veo-3-1-and-new-creative-capabilities-in-the-gemini-api/ · https://getimg.ai/blog/google-veo-3-1-review · https://www.atlascloud.ai/blog/guides/seedance-2-cost-per-second · https://apiframe.ai/models/seedance-2.0/pricing · https://technode.com/2026/07/31/bytedance-launches-seedance-2-5-video-generation-model/ · https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5 · https://www.cometapi.com/seedance-2-5-api-pricing/ · https://www.krea.ai/docs/api-reference/video/hailuo-23.md · https://www.wireflow.ai/blog/hailuo-pricing · https://fal.ai/models/wan/v2.6/image-to-video/playground · https://www.alibabacloud.com/help/en/model-studio/wan2-6-i2v-flash · https://fal.ai/learn/devs/ltx-video-2-pro-image-to-video-developer-guide · https://ltx.io/model/api/pricing · https://eesel.ai/blog/runway-ai-pricing · https://magichour.ai/blog/runway-gen-45-pricing · https://help.runwayml.com/hc/en-us/articles/42311337895827 · https://lumalabs.ai/api/pricing · https://wavespeed.ai/blog/posts/introducing-vidu-q3-reference-to-video-on-wavespeedai/ · https://fal.ai/models/fal-ai/vidu/q3/reference-to-video/mix/llms.txt · https://www.krea.ai/docs/api-reference/video/vidu-q3.md · https://docs.midjourney.com/docs/fast-relax · https://developers.openai.com/api/docs/models/sora-2-pro · https://higgsfield.ai/blog/higgsfield-pricing-explained · https://wavespeed.ai/blog/cost-and-billing/krea-ai-pricing-2026/ · https://eesel.ai/blog/pika-ai-pricing · https://eesel.ai/blog/leonardo-ai-pricing · https://www.eesel.ai/ja/blog/freepik-ai-ryokin · https://invideo.io/faq/why-do-ai-video-models-fail-when-two-characters-interact/ · https://arxiv.org/html/2510.05093v1

Consistency: https://blog.google/technology/ai/nano-banana-pro · https://techcrunch.com/2025/11/20/google-releases-nano-banana-pro-its-latest-image-generation-model/ · https://fal.ai/models/fal-ai/flux-2-trainer/llms.txt · https://fal.ai/models/blackforestlabs/flux-3/klein/base/trainer/llms.txt · https://www.fal.ai/models/fal-ai/flux-lora-fast-training · https://help.scenario.com/en/articles/frequently-asked-questions-faq/

Lip-sync: https://sync.so/docs/billing · https://sync.so/docs/models/lipsync · https://fal.ai/models/fal-ai/sync-lipsync/v2/pro · https://fal.ai/models/fal-ai/kling-video/ai-avatar/v2/pro · https://fal.ai/docs/model-api-reference/video-generation-api/kling-video-lipsync · https://lemonslice.com/blog/lemonslice-vs-kling · https://www.tomsguide.com/ai/ai-image-video/lip-sync-battle-i-put-3-leading-ai-video-tools-to-the-test · https://hedra.com/docs/pages/studio/getting-started/video-models · https://www.activepieces.com/blog/hedra-pricing-2026-plans-credits-and-cost-per-video · https://fal.ai/models/fal-ai/bytedance/omnihuman/v1.5 · https://www.wavespeed.ai/models/wavespeed-ai/wan-2.2/speech-to-video

Voice, music, SFX: https://bigvu.tv/blog/elevenlabs-pricing-2026-plans-credits-commercial-rights-api-costs/ · https://elevenlabs.io/docs/overview/capabilities/text-to-dialogue.md · https://elevenlabs.io/blog/v3-audiotags · https://elevenlabs.io/eleven-music-model-specific-terms · https://elevenlabs.io/docs/overview/capabilities/music/marketplace · https://www.eesel.ai/blog/cartesia-sonic-3-pricing · https://www.eesel.ai/blog/hume-ai-pricing · https://www.fiverr.com/resources/guides/costs/actor · https://www.musicinafrica.net/magazine/suno-adjusts-ai-music-ownership-terms-after-warner-music-partnership · https://www.activepieces.com/blog/suno-pricing-2026-free-pro-and-premier-compared.md · https://stacksheriff.com/ai-tools/suno-pricing/

Finishing, platform, rates: https://fal.ai/topaz · https://fal.ai/models/topaz/upscale/video/generative · https://costbench.com/software/ai-video-generators/topaz-video-ai/ · https://costbench.com/compare/capcut-vs-davinci-resolve/ · https://bigvu.tv/blog/capcut-free-vs-pro-what-2026s-restructure-gives-you/ · https://cloud.google.com/free-trial/ · https://www.tubefilter.com/2026/07/13/youtube-inauthentic-content-monetization-policy-update/ · https://techrepublic.com/article/news-youtube-ai-video-monetization-rules · https://support.google.com/youtube/answer/1311392 · https://www.fiverr.com/resources/guides/costs/2d-animation · https://www.sidestackers.com/rates/animator · https://www.imagine.art/blogs/2d-animation-cost
