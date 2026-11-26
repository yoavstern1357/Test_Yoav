# Free tools research: free tiers, open models and "FREE STACK 2.0" (2026-11-26)

Author role: research analyst. Status: research and recommendations only. Nothing was signed up for, bought, uploaded, committed or pushed.
Scope: every free tier, free credit and open-source tool that could fix the three defects confirmed on Episode 1 v4.4 (duplicated characters, smeared faces, desync), with commercial-use and automation checks, a proposed free stack, a fair 5-shot comparison test and the sign-up list.
Read with: `fix-plan.md` (defect census, root causes, free fixes 1-10), `tools-buying-plan.md` (paid options, 5 test shots, scoring), `quality-research.md` (rubric A-J), `gpu-ledger.md` (Kaggle budget), `PRODUCTION-BIBLE.md` (look, both orientations, GPU rules), `motion-tech.md` and `voice-tech.md` (what was already tested).

## How to read the evidence

- **Date.** Every fact is a web-search snapshot taken on **2026-11-26** unless another date is given. Free tiers change monthly (Pika, Lightning AI, Grok and Suno all changed theirs in 2026). Re-check on the day of sign-up.
- **The fetch tool was blocked again** (`ai.google.dev` does not resolve from this container). **Everything below comes from search-result snippets, not from reading the pages.** Where snippets disagree, both values are given.
- **Tags.** **[S-off]** = snippet of the vendor's own page, docs, model card or licence. **[S]** = third-party blog, reseller or press (often a competitor; numbers often conflict). **[M]** = my background knowledge, not re-checked today. **[E]** = my estimate. **[T]** = tested in this repo (with the file that proves it). Nothing in sections 1-2 is [T] unless marked: no free tier listed here has been tested on our shots yet.
- **Marketing vs tested.** "Good at anime", "keeps characters consistent", "lip-syncs cartoons" are vendor claims everywhere below. The only tested facts we have are our own (`motion-tech.md`: LTX 0.9.8 13B distilled nf4 beat LTX 0.9.5 and FastWan 2.2 5B on our characters; Wan 2.2 5B ran out of memory on a T4). Section 4's 5-shot test exists to turn claims into results.

---

## Executive summary

1. **Almost every free tier of a commercial video, image, voice or music service is non-commercial and/or watermarked.** Kling, Hailuo, Luma, Vidu, PixVerse, Runway, Hedra, sync.so, HeyGen, ElevenLabs, Cartesia, Suno, Krea, Freepik and Scenario all limit free output to personal or evaluation use (section 1). **Nothing generated on those free tiers may go into a monetized episode.** Their only free value for us is **evaluation**: running the 5-shot test before paying. Two traps make this strict: Suno and Scenario say that **upgrading later does not license what was made on the free plan** [S-off], so any shot we like must be regenerated after paying.
2. **The real free path to commercial-quality output is free compute + permissively licensed open models.** We already use Kaggle (about 30 T4 GPU-h/week). The biggest new free resource found is **Modal's Starter plan: $30 of compute credit every month** [S-off modal.com/pricing], about 7-8 H100-hours or 12-14 A100-hours [S rates; E]. That is enough to run the models a T4 cannot: **Wan 2.2 14B image-to-video and first+last-frame with the 4-step Lightning LoRA (Apache-2.0), AniSora V3 (Bilibili's anime-trained video model, Apache-2.0), LatentSync 1.6 and InfiniteTalk lip-sync (Apache-2.0), Qwen-Image-Edit-2511 keyframe repair (Apache-2.0)**. It needs one sign-up and one GitHub secret, then Claude runs it alone.
3. **The Google $300 trial does NOT pay for the Gemini API in AI Studio.** Google's trial docs say the credit "can't pay for Gemini API in AI Studio costs" and is meant for Vertex AI [S-off docs.cloud.google.com/free]. This corrects `tools-buying-plan.md` purchase #3. Whether Vertex AI Veo 3.1 is covered by the trial is still unverified, the trial needs a payment card, and Vertex auth (service-account key) does not fit our "no secrets in files" rule without extra work (section 5.3). The Gemini API free tier itself has **no quota for image models (Nano Banana / Nano Banana Pro / Imagen) and no Veo** [S, forum + guides].
4. **Lip-sync has no usable free commercial service.** sync.so free = 3 watermarked 20 s generations per month [S-off docs]; Hedra free = no commercial use [S-off plans]. So lip-sync must come from open tools: **Rhubarb (MIT, CPU, mouth sprites) first, LatentSync 1.6 / InfiniteTalk on Modal second**. None of the open models is documented on anime faces [S-off LatentSync paper: benchmarks are real-face sets]; the smoke test decides.
5. **The licence traps that matter most for us** (section 6): HunyuanVideo / FramePack / HunyuanVideo-Foley (Tencent licence excludes the EU, UK and South Korea, including display of outputs there: incompatible with a worldwide YouTube channel); anything that uses InsightFace models (InstantID, PuLID, IP-Adapter-FaceID, LivePortrait, LatentSync's default preprocessing); FLUX.1 [dev] / FLUX.1 Kontext [dev] / FLUX.2 klein **9B** (non-commercial; our klein **4B** is Apache-2.0); CodeFormer, Wav2Lip, MMAudio, UNO, MusicGen, XTTS (non-commercial weights); Leonardo free (outputs public and owned by Leonardo as between the parties); free tiers that take a broad licence to what we upload (our unreleased character designs).

---

## 1. Free tiers and free credits of commercial services

Legend for "Commercial on free?": **No** = free output may not be monetized; **Unclear** = sources conflict or are silent; **Yes** = allowed. "Automatable" = can Claude call it from the cloud container or GitHub Actions with a key (no clicking).

### 1a. Video generators (consumer web apps)

| Service | What is free (2026-11-26 snapshot) | Res / length on free | Watermark | Queue on free | Commercial on free? | Automatable? | Use for us |
|---|---|---|---|---|---|---|---|
| **Kling** (Kuaishou) | 66 credits/day, reset every 24 h, no rollover [S, several blogs; no official page in results] | 5 s, 720p [S] (one source: 1080p [S]) | Yes [S] | Low priority; "queue busy" messages reported [S] | **No**: terms bar commercial use of output without permission; only paid members may use output commercially [S quoting ToS 4.6]. Users keep ownership [S]; one blog reports a broad sublicensable licence to Kuaishou over uploaded content [S, single source] | **No** (web UI). Developer API is separate, paid, JWT-signed [M] | 5-shot test only |
| **Hailuo / MiniMax** | One-time trial credits: 150 [S WaveSpeed], 200 expiring in 3 days [S Atlas], or a small daily pool [S ZSky]; no official page found | 768p class [M] | Yes [S Tom's Guide] | not found | **No** [S] | API is paid (MiniMax platform) [M] | 5-shot test if credits last |
| **Luma Dream Machine** (Ray3.x) | Conflicting: about 8 or 30 generations/month, or 80 credits/day; draft quality [S]. Plans restructured March 2026 ("Luma Agents") [S] | 720p draft [S] | "may include a watermark" [S-off licensing page] | not found | **No**: Free plan = "limited usage, non-commercial use" [S-off lumalabs.ai learning hub] | API is separate and paid [S-off] | Low priority |
| **Vidu** (ShengShu) | Sign-up trial credits + daily login credits, amount not published [S]; other sites say 40/month [S] | 540p-720p [S] | Yes [S] | Off-peak mode is paid-only per most sources [S] | **No** per most sources; one listing says yes [S, conflicting] | API is paid [M] | **5-shot test (anime-positioned model)** |
| **PixVerse** | 90 sign-up credits + 60/day, no stacking [S, mostly one reseller's guide] | 360p-720p, 5 s [S] | Yes [S] | not found | **No** [S] | Paid API [S] | Optional test |
| **Runway** | **125 credits once**, never refresh [S-off help.runwayml.com] (about 10 s of Gen-4.5 at 12 credits/s [S]) | 720p [M] | Yes, on all free videos [S-off] | n/a | Unclear on free [M]; paid plans commercial | API has its own paid credits [S] | Skip (too few credits) |
| **Pika** | Changed 2026-09: sources say free plan now has **0 monthly credits** (no watermark, all models) [S, usagepricing tracker]; earlier 80/month with watermark [S] | n/a | see left | n/a | Unclear | Limited | Skip |
| **Google Flow** (Veo 3.1) | **50 credits/day** [S]; Veo 3.1 Lite 10 credits, Fast 20, Quality 100 per clip [S citing Google help] = up to 5 Lite or 2 Fast clips/day; peak-hour blocking for free users reported [S] | 720p, 4-8 s [S] | **Visible watermark on all videos except Ultra members in Flow** [S-off blog.google]; invisible SynthID always [S] | Peak-hour blocks [S] | **Unclear**: no Google statement found; a developer asked on Google's forum and got no answer in the snippet [S] | **No** (Labs web app) | **5-shot test (Veo quality reference)** |
| Google Vids | 10 Veo 3.1 generations/month on personal accounts [S] | | likely watermarked [E] | | Unclear | No | Skip |
| **Dreamina** (ByteDance/CapCut, Seedance 2.0) | 120 credits/day (US) or 225 [S-off dreamina guide / S]; Seedance 2.0 on free, 2.5 by plan and region [S-off] | not found | not found | not found | **Unclear**: "supports commercial creation subject to applicable terms" [S-off marketing]; no plan lists commercial rights [S]. CapCut-family terms grant a broad licence over uploaded content [S, tools-buying-plan] | No | Optional test; ToS risk on uploads |
| Higgsfield | **0 credits**, no commercial use, watermark [S-off higgsfield.ai help + pricing] | | | | **No** | | Skip |
| Grok Imagine (xAI) | Free access ended; SuperGrok only [S, several]; fal offers 5 free/day as its own sandbox [S-off fal page] | | | | Unclear | via fal (paid) | Skip |

### 1b. Images, design, characters

| Service | Free allowance | Commercial on free? | Other traps | Automatable? | Use for us |
|---|---|---|---|---|---|
| **Gemini API free tier** (AI Studio key) | Text models free with rate limits; **image models (2.5 Flash Image, Nano Banana 2 = Gemini 3.1 Flash Image, Nano Banana Pro = Gemini 3 Pro Image, Imagen 4) have no free quota ("limit: 0")** [S forum Jan 2026 + guides]; one blog claims 500/day on 2.5 Flash Image, contradicted by forum reports [S]; **no Veo** [S] | API outputs usable (Google claims no ownership) [M] | Free-tier prompts and outputs **are used to improve Google products** (terms effective 2026-03-23) [S-off ai.google.dev/terms]; do not send personal data | Yes (key in `x-goog-api-key`) | Useless for frames; fine for text helpers |
| Gemini app (consumer) | Nano Banana Pro about 2 prompts/day for free users, then falls back to Nano Banana [S Engadget] | consumer terms; visible watermark [M] | | No | Manual sketching only |
| **Krea** | about 100 compute units/day [S] | **No**: commercial licence starts at Basic [S quoting Krea FAQ] | | Paid API | Skip |
| **Leonardo** | 150 tokens/day, no rollover [S] | **Officially yes** ("use images and videos you generate on our free plan for commercial purposes") [S-off leonardo.ai news] **but** free outputs are public and "Leonardo owns the assets as between the user and Leonardo" [S-off same page]; third parties read it as non-commercial [S] | Public gallery leaks our designs before launch | Paid API | Avoid for final art |
| **Freepik** | Free = personal use only, attribution required; AI credits not included on free per one regional page [S-off freepik help] | **No** | | Paid API | Skip |
| **Scenario** | **50 credits/day** [S-off help.scenario.com] | **No**: personal/evaluation only; **upgrading does not extend commercial rights back** to free-plan assets [S-off] | | Paid API | Skip |
| **Civitai** on-site generator | small daily Buzz allowance, more by activity [S] | Depends on each model's licence; many community checkpoints are non-commercial [S] | Images kept 30 days unless posted [S-off older page] | No | Skip (licence maze) |
| Cloudflare Workers AI | **10,000 Neurons/day free**, reset 00:00 UTC [S-off developers.cloudflare.com]; since **2026-07-28** some heavy models return 403 on the Free plan [S-off changelog]; list of affected models not in the snippet | Model licence governs (e.g. FLUX.1 schnell Apache-2.0 [M]) | | **Yes** (Bearer token, `api.cloudflare.com`) | Draft images at best; no video; skip |

### 1c. Voice, lip-sync, avatars, music

| Service | Free allowance | Commercial on free? | Automatable? | Use for us |
|---|---|---|---|---|
| **ElevenLabs** | 10,000 credits/month (about 10 min TTS), API included [S-off elevenlabs.io/pricing/api] | **No**: "non-commercially with attribution" [S-off billing docs] | Yes (`xi-api-key`) | Listening test and scratch animatic only |
| **Cartesia** | 20K credits/month + $1 agent usage [S-off cartesia.ai/pricing] | **No**: commercial licence starts at Pro $5/month [S-off] | Yes | Skip |
| **sync.so** (lipsync-2 / -2-pro) | **3 generations/month (incl. lipsync-2-pro) + 10 TTS, max 20 s each**, no rollover [S-off sync.so docs] | Free and Hobbyist outputs **watermarked** [S-off]; licence for free not found | API exists; free-tier API use not confirmed | **Lip-sync screen of T2 only** (3 gens) |
| **Hedra** (Character-3) | 300 credits/month per official plans page (others say 100 or 400) [S-off hedra.com/plans vs S]; about 6 credits/s [S] = about 50 s/month | **No** [S-off plans: "No commercial use"] | API needs prepaid balance [S-off, tools-buying-plan] | Lip-sync screen of T2 only |
| HeyGen | 3 videos/month or a few minutes, conflicting [S] | **No**, watermark [S] | | Skip (realistic presenters) |
| **Suno** | 50 credits/day (about 10 songs) still renew; **no free downloads since 2026-09-03** (pre-Sept accounts: 7 lifetime) [S-off suno.com/pricing + S] | **No**; Suno owns free songs; **no retroactive licence** when subscribing [S-off help.suno.com] | No API [M] | Skip; ACE-Step stays |
| Udio | closed fan platform after its settlement [S, tools-buying-plan] | unclear | | Avoid |

### 1d. Free compute and API credits (this is where commercial output comes from: the licence of the open model you run governs)

| Provider | What is free | Hardware | Automatable? | Notes / traps | Use for us |
|---|---|---|---|---|---|
| **Kaggle** (in use) | about 30 GPU-h/week, number not in docs, visible in account settings [S]; 12 h sessions [S] | T4 x2 / P100 [S] | **Yes, already** (GitHub Actions + `kaggle_run.py`) [T] | 16 GB T4: no bf16, 14B video models impractical [T motion-tech] | Keep: stills, voices, LTX 0.9.8, LoRA training |
| **Modal** (Starter) | **$30 credit every month**, $0 plan [S-off modal.com/pricing]; T4 $0.59/h, A100-40GB $2.10/h, H100 $3.95/h [S]; 10 GPU concurrency [S]. One page says $5/month until a card is added [S Mintlify, possibly outdated] | T4 to H100, per-second billing | **Yes**: Python SDK with token id + secret. Best run from **GitHub Actions with the token as an Actions secret** (the SDK talks gRPC to Modal; whether the proxy can inject it is unverified [M]) | Credits don't roll over [M]; expect a card to unlock the full $30 [S]; cold start + model download counted [M] | **New: the "big GPU" for hero/talk shots** |
| Lightning AI | Changed twice in 2026: one-time grant of up to 30 credits (5 on sign-up, 25 after adding a card), and on **2026-11-09** free GPU hours cut to 50, storage 50 GB [S pricing trackers]; older guides: 15 credits/month [S] | interruptible GPUs | Yes (Studio API) [M] | Unstable terms | Optional backup only |
| Google Colab free | T4 subject to availability; Google does not publish limits; 12 h max [S-off FAQ] | T4 | Partly: a Colab CLI exists since 2026-06 [S]; free tier is meant for interactive use [M] | Unpredictable disconnects | Manual backup |
| Paperspace Gradient free | 8 GB M4000, 5 GB storage, 6-12 h sessions, card may be required [S] | M4000 | Yes [M] | Too small for any video model | Skip |
| **Hugging Face** free account | Inference Providers credit **about $0.10/month** (PRO $9/month: $2) [S-off hf docs]; **ZeroGPU about 3.5 min/day** free, 25 min/day PRO (another source: 5 / 40) [S forum vs S] | shared H200-class slices [M] | Yes (HF token; `gradio_client` calls any public Space) [S-off hub docs] | API calls may burn quota faster than the web UI [S, anecdotal]; each Space has its own host (`*.hf.space`) to allow | Weights download token (needed anyway); not a production GPU |
| **fal.ai** | Starter credits for new accounts, amount not published (one estimate about $20) [S]; 2 concurrent requests for new accounts [S] | hosted models | Yes (`Authorization: Key ...`) | fal terms: output use at your own risk; model owner terms pass through [S] | Test credits, if any, go to the 5-shot test |
| Replicate | Conflicting: $5, $10, "free featured models" or "$500" [S, aggregators; the $500 figure looks like a startup programme] | hosted models | Yes (Bearer) | | Check balance after sign-up |
| RunPod | Random $5-500 bonus **after a first $10 spend** [S-off referral page] | pods | Yes | Not free | Skip |
| Google Cloud trial | **$300 for 90 days, new customers only**, card required [S-off cloud.google.com/free]; **cannot pay for Gemini API in AI Studio** [S-off docs]; covers Vertex AI [S-off]; Veo via Vertex reported by TechRadar [S], not confirmed for Veo 3.1 | Vertex AI | Hard: Vertex wants a service-account or OAuth token [M] | Trial billing account changes Google's data terms to "Paid Service" (no training on prompts) [S-off]; Veo may refuse child characters (person-generation settings) [M] | Possible "free" Veo/Nano Banana Pro route, after the free stack (5.3) |
| Vertex AI express mode | 90 days free without billing for new Gmail accounts, Gemini models at 10 RPM, API key access [S-off express-mode overview]; **Veo/Imagen not listed** in the snippet | | Yes (API key) [S-off] | Accounts previously used on Google Cloud are ineligible [S-off] | Not useful for video |
| OpenRouter / Groq / Together | OpenRouter `:free` text models: 20 req/min, 50/day (1,000/day after $10 lifetime purchase) [S-off docs]; Groq free text tier [M]; Together has no meaningful free credit [M] | LLM text only | Yes | | **Not relevant** to animation (Claude writes scripts) |

**Bottom line of section 1:** for publishable footage, the free commercial-service tiers give us nothing. Use them to **decide what to buy** (section 4), and get publishable footage from section 2 models on Kaggle + Modal.

---

## 2. Free and open-source tools we are not using yet

Columns: licence as seen in snippets (verify the LICENSE file and model card before the first monetized upload, as `tools-buying-plan.md` 5.3 requires), whether it runs on our free GPUs, and what it could fix.

### 2a. Open video models

| Model | Licence | Fits Kaggle T4? | Fits Modal ($30/mo)? | What it offers | Evidence level | Verdict |
|---|---|---|---|---|---|---|
| LTX-Video 0.9.8 13B distilled nf4 (current) | LTX open-weights licence, free under US$10M revenue [S-off licence PDF] | **Yes** [T] | yes | our baseline | [T] motion-tech | keep for wides/macros |
| **LTX-2.3** (22B, dev + 8-step distilled, released 2026-03-05) and LTX-2.5 (2026-08, multi-shot, open weights per VentureBeat) | LTX-2 Community Licence (free under $10M); one blog says Apache-2.0 [S, conflicting; HF LICENSE file = community licence] | No (too big, no fp8 on T4) [T motion-tech] | **Yes** (fp8 on L40S/H100 [M]) | "native portrait", sharper video, keyframes, same family as our pipeline (easiest continuity) [S] | vendor + press | **Trial on Modal** |
| **Wan 2.2 14B I2V (A14B MoE) + lightx2v 4-step Lightning LoRA** | Apache-2.0 (base and distill LoRAs) [S-off HF model cards] | No (14B; full 5B already OOM [T]) | **Yes** (lightx2v recommends 80 GB for the full config; 24 GB config exists) [S-off] | 720p, first+last-frame variants, strong motion; 2-step community variant about 37 s per 512x848 clip on unnamed GPU [S] | community | **Trial on Modal (main candidate)** |
| **Wan 2.1 VACE 14B** (reference-to-video, "anything to video") | Apache-2.0 [M] | No | Yes [M] | the free equivalent of Kling "elements": separate reference images per character, masks, pose control [M] | [M] | **Trial for duplicate-prone 2-shots** |
| **Index-AniSora V3 / V3.1 / V3.2** (Bilibili) | **Apache-2.0** for V2 and V3 weights [S-off GitHub changelog + HF]; the RLHF variant is gated by a form [S] | No (Wan-14B-class [M]) | Yes | **the only open model trained for anime**: image-to-video, keyframe interpolation, motion-score control (README: v3.1, motion 2.0-4.0) [S-off README]; samples use real anime clips, so avoid prompting existing shows [S] | vendor demos only | **Trial on Modal (style fit)** |
| Wan 2.2 Animate 14B / Wan-Animate-2 | Apache-2.0 [S-off HF]; NVIDIA NIM copy lists NVIDIA Open Model Licence [S-off] | No | Yes | character animation from a driving video, character replacement | vendor | Later: a creator-acted reference video drives the Uncle (Act-Two style, free) |
| Wan 2.5 / 2.6 / 2.7 | **No open weights found** (hosted API only) [S] | | | | | n/a |
| HunyuanVideo 1.5, FramePack (Hunyuan-based) | Tencent Hunyuan Community Licence: **territory excludes EU, UK, South Korea, including outputs** [S-off licence text] | | | | | **Reject** (worldwide channel) |
| SkyReels V3 (2026-01-29) | **Licence not stated in the README** [S]; V2 = Skywork Community Licence (commercial with conditions) [S-off] | No | Yes | V2V, I2V, talking avatar [S] | | Hold until licence is clear |
| Mochi 1 | Apache-2.0 [M] | No | Yes | text-to-video, 480p, photoreal bias [M] | | Skip |
| CogVideoX 5B | CogVideoX licence with commercial registration (2B is Apache) [M] | marginal | yes | outdated quality [M] | | Skip |
| ToonCrafter (cartoon in-betweening) | **Apache-2.0** on the official model card [S-off HF]; a third party says "not for commercial use" (conflicts with the licence) [S] | Marginal (512x320) | Yes | 2 keyframes -> 2 s in-between at 8 fps, 512x320, no text [S-off README] | research | Small R&D only (too low-res for our 1080p master) |
| RIFE (in use) | MIT [M] | Yes | | interpolation; ghosts on big poses [S quality-research] | [T] (bug) | keep for small motion |

### 2b. Keyframes, character consistency, LoRA

| Tool | Licence | What it fixes | Verdict |
|---|---|---|---|
| FLUX.2 klein **4B** (in use) | **Apache-2.0** (4B distilled and 4B base) [S-off github black-forest-labs/flux2] | multi-reference editing (up to 4 refs, 10 in the playground) [S] | keep; never switch to **9B** (FLUX Non-Commercial Licence) [S-off] |
| **FLUX.2 klein 4B LoRA** via **ostris ai-toolkit** | ai-toolkit licence not in snippets (MIT [M], verify); klein trainers documented by BFL and a HF blog "LoRA under 60 minutes" (2026-06) [S-off] | identity LoRA per character = fix 8 in `fix-plan.md` | **Do** (Kaggle T4 or Modal); BFL lists 12 GB+ VRAM for ai-toolkit [S-off] |
| **Qwen-Image-Edit-2511** | **Apache-2.0** [S-off HF card]; "better consistency in multi-person group photos, high-fidelity fusion of two separate people" [S-off] | repair keyframes: remove a duplicate Uncle, fix costumes, merge two single-character sheets into one 2-shot | **Trial on Modal** (20B-class, too big for T4 [M]); note: Qwen-Image **2.1** moved to a non-commercial research licence (2026-09-20) [S], so pin 2511 |
| OmniGen2 | Apache-2.0 [S-off repo]; an unofficial site claims a paid licence [S, ignore] | multi-reference generation | backup to Qwen-Image-Edit |
| USO (ByteDance) | code Apache-2.0 but **built on FLUX.1-dev** (non-commercial base) [S-off] | style + subject | Avoid |
| UNO (ByteDance) | code Apache, **weights CC BY-NC 4.0** [S-off] | subject | **Reject** |
| IP-Adapter (FaceID), InstantID, PuLID | **depend on InsightFace models = research/non-commercial** [S-off h94 discussion] | face identity | **Reject** |
| FLUX.1 Kontext [dev] | FLUX.1 Non-Commercial Licence [S-off bfl.ai] | editing | **Reject** |
| musubi-tuner / kohya sd-scripts | Apache-2.0 [M] | LoRA for Wan/Qwen-Image/HunyuanVideo [M] | Later: a Wan 2.2 character LoRA on Modal (identity in motion) |
| OWLv2 / Grounding DINO / DINOv2 | Apache-2.0 [M, as in fix-plan] | person counter + identity check in the QC gate | do (fix 7 upgrade) |

### 2c. Lip-sync and talking shots (open)

| Tool | Licence | Hardware | Anime evidence | Verdict |
|---|---|---|---|---|
| **Rhubarb Lip Sync** | MIT [S mirrors; fix-plan quotes the LICENSE] | CPU | genre-authentic mouth flaps (A-H + X shapes); English recogniser only [S] | **Do first** (fix 5a) |
| **LatentSync 1.6** (ByteDance) | Apache-2.0 [S] | about 18 GB VRAM for 1.6 (1.5: 8 GB) [S] -> Modal A10G/L4/A100 | benchmarks on real-face sets (HDTF, VoxCeleb2); README shows anime demo clips borrowed from VASA-1/EMO; "flicker in teeth and facial hair" [S-off paper/README]. Default preprocessing uses InsightFace (non-commercial) -> swap to YuNet (MIT) [fix-plan] | **Smoke test on 3 close-ups** |
| **InfiniteTalk** (MeiGen) | Apache-2.0 weights [S-off HF] | Wan2.1-I2V-14B-480P base; low-VRAM and FP8 flags [S-off README] -> Modal | image/video + audio -> talking video, body and head move with the voice; multi-person mode [S-off]; real-face oriented [M] | **Trial for single-face talk shots** (mouth correct by construction) |
| Wan 2.2 S2V 14B | Apache-2.0 [M, quality-research] | Modal 80 GB [E] | audio-driven full body | Trial after InfiniteTalk |
| MuseTalk 1.5 | MIT code, "models available for any purpose, even commercially" [S]; a mirror says BSD-3 [S] | about 4 GB, real time [S] | real faces; jitter reported [S] | backup |
| Wav2Lip | **non-commercial** (README) [S] | | | **Reject** |
| LivePortrait | MIT code, InsightFace models [fix-plan] | | | Reject unless detector is replaced |
| SadTalker | Apache-2.0 [M] but 3D-face model of real heads, dated [M] | | poor on anime [M] | Skip |

### 2d. 2D animation and rigging (free, desktop; creator-run unless scripted)

Use case: the "puppet route" for talk shots. A rigged 2D version of each character (cut from approved stills) gives perfect, deterministic lip-sync and blinks, and never duplicates anyone. The repo already has a code cut-out rig demo (`tools/episode_maker/rig/grandma_demo.py`).

| Tool | Licence | Scriptable by Claude? | Fit |
|---|---|---|---|
| **Blender Grease Pencil v3** (Blender 4.3+) + Rhubarb add-ons | GPL (outputs are ours) [M]; Rhubarb Blender add-ons exist (one lists Blender 3.3-4.2) [S] | **Yes**: headless Blender + Python on CPU in GitHub Actions or this container [M] | best automated option: cut-out planes of our stills, bones, mouth-shape library, camera on ones |
| **Inochi2D / Inochi Creator** | BSD-2-Clause (free; optional $20 paid build) [S-off itch/Steam] | Partly (Inochi Session is for live puppeteering) [M] | Live2D-style deformation puppets; own format, not Live2D/Spine-compatible [S] |
| nijigenerate (Inochi2D-derived) / Umamo (reads Live2D files, early preview) | BSD-2 / free [S] | No | watch list |
| OpenToonz | BSD-3 [M] | weak | traditional anime ink and paint; heavy manual work |
| Synfig Studio | GPL-3 [M] | CLI renderer [M] | vector bones; not our look |
| Krita animation | GPL-3 [M] | No | frame-by-frame cleanup of single bad frames (the "freelance cleanup" job, done free) |
| DragonBones | MIT, unmaintained since about 2019 [M] | | skip |

### 2e. Face detail and upscaling (commercial-safe only)

| Tool | Licence | Verdict |
|---|---|---|
| Real-ESRGAN (official anime 6B weights) | BSD-3 [S] | keep; but it sharpens smears (fix-plan R4) |
| LTX / Wan video-to-video at low strength on a face crop (fix 9) | as base model | the free "face detailer"; on Modal use Wan 2.2 14B at 0.2-0.3 strength [E] |
| LTX 0.9.8 / LTX-2.x latent upsampler | LTX licence | test as ESRGAN replacement on hero close-ups |
| APISR (anime SR) | GPL-3 code [S-off README]; weights licence not found | usable as a tool (GPL does not cover outputs [M]); verify weights |
| Community "AnimeSharp/Animex4" ESRGAN weights | often **CC-BY-NC-SA** [S] | **Reject** |
| CodeFormer | non-commercial [M, fix-plan] | **Reject** |
| GFPGAN | Apache-2.0 [M] but photo-face restorer (turns anime faces photographic) [fix-plan] | Reject on quality |

### 2f. Voice, sound effects, music

| Tool | Licence | Notes | Verdict |
|---|---|---|---|
| Qwen3-TTS 1.7B VoiceDesign (current default) | Apache-2.0 [S-off tech report] | [T] in use | keep |
| Chatterbox / Chatterbox-Turbo | MIT [S, voice-tech] | inaudible PerTh watermark [voice-tech]; one blog says the project was "retired in August 2026" [S, single source] (MIT weights stay usable) | alternate |
| Kokoro-82M | Apache-2.0 [S] | CPU default, flat | scratch |
| Dia | Apache-2.0 [S] | multi-speaker dialogue in one pass [M] | try for banter takes |
| NVIDIA Magpie-Multilingual | NVIDIA Open Model Licence, commercial [S] | | optional |
| IndexTTS2 / 2.5 | **unclear**: community says Apache-2.0, official 2.5 card says "Bilibili Model License" [S] | | Hold |
| XTTS-v2, Fish Audio S2, Higgs TTS 3 | **non-commercial / research** [S] | | **Reject** |
| VibeVoice | conflicting licence entries [S]; Microsoft pulled the repo in 2025 [M] | | Avoid |
| **Kenney audio packs** | **CC0** [S quoting Kenney] | | use |
| **Freesound (CC0 filter only)** | per-file: CC0, CC BY, CC BY-NC [S] | filter to CC0; log each file id | use |
| **Sonniss GDC bundles** (2026 bundle free, 347 files, 7.47 GB [S]) | royalty-free, commercial, no attribution (2020/2023 terms) [S]; 2024 licence forbids **AI training** [S] | read the 2026 licence once | use |
| Pixabay sound effects | Pixabay Content Licence, commercial, no resale of raw files [S] | Content ID can still match popular files [E] | use sparingly |
| BBC Sound Effects (RemArc) | personal/educational only [M] | | **Reject** |
| ACE-Step 1.5 | MIT per model card ("strictly use the generated music for commercial purposes") [S-off]; weights repo lacks a LICENSE file; LM variant built on Qwen2.5-Omni-3B would be research-only [S-off discussion] | pin a 7B/Apache or no-LM variant | upgrade from ACE-Step v1 |
| YuE | Apache-2.0 [M] | lyrics-to-song, multilingual incl. Japanese [M] | try for the Japanese punk opening |
| MMAudio | **weights CC-BY-NC 4.0** [S] | | **Reject** |
| HunyuanVideo-Foley | Tencent community licence (territory) [S-off] | | **Reject** |
| Stable Audio Open | Stability Community Licence (free under about $1M revenue) [M, not confirmed today] | SFX generation | optional |

---

## 3. FREE STACK 2.0

Principle (same as `fix-plan.md`): the free process fixes (stills gate, shot rules, voice-first animatic, prompt lint, QC gate) come first, cost no account and fix most duplicates and all timing desync. FREE STACK 2.0 adds **one new free GPU (Modal)** and **three open model families** for what a T4 cannot do.

### 3.1 Defect -> free tool -> creator cost

| Defect (fix-plan census) | Root cause (fix-plan) | Free tool, in order of trial | Where it runs | GPU / credit cost | Creator time |
|---|---|---|---|---|---|
| **1. Duplicated characters** (21 of 78 clips; 20 baked into stills) | R1 scene refs, R2 mismatched START/END, no gate | (a) fix 1 stills hygiene + gate (single-character sheets, head count in prompt, END = edit of START) | Kaggle klein 4B | about 2 GPU-h (fix-plan) | 0 |
| | | (b) **Qwen-Image-Edit-2511** to repair any still that fails the gate (remove the second Uncle, merge two sheets into one 2-shot) | Modal A100/H100 | about $0.02-0.05 per edit [E] | 0 |
| | | (c) **klein 4B character LoRAs** (ai-toolkit): fewer refs = no duplicate source | Kaggle T4 (or Modal L4) | 2-3 GPU-h per character on T4 (est. fix-plan); about $2-4 per LoRA on Modal [E] | 5 min to approve the sheets |
| | | (d) **Wan 2.1 VACE 14B** reference-to-video for the remaining 2-character shots | Modal H100 | about $0.10-0.20 per 5 s clip [E] | 0 |
| | | (e) OWLv2 person counter + DINOv2 identity check in `qc_clips.py` | Kaggle / Modal T4 | minutes | 0 |
| **2. Smeared / melting faces** (12 visual + 7 QC) | R4 89 px faces at 480x832, 4-bit 8-step, ESRGAN | (a) fix 2 shot rules (talk = close-up, max 2 faces) + fix 6 (576x1024 on T4) | Kaggle | +60% per close-up (fix-plan) | 0 |
| | | (b) **Wan 2.2 14B I2V / first+last frame with Lightning 4-step at 720x1280 native** for talk and hero shots | Modal H100 | about 1-2 min per 5 s clip [E] -> $0.07-0.13; $30 = about 230-430 clips/month [E] | 0 |
| | | (c) **AniSora V3.1** for the same shots (anime-trained, style fit) | Modal H100 | similar to Wan 14B [E] | 0 |
| | | (d) **LTX-2.3 distilled** (8-step, native portrait claim) as the cheap 720p tier | Modal L40S/H100 | less than Wan 14B [E] | 0 |
| | | (e) face detail pass (fix 9) with Wan 2.2 V2V at low strength on face crops | Modal | about $0.05 per hero clip [E] | 0 |
| **3. Desync** (all 39 pairs; 0 of 47 lines synced) | R5 clips before voices, no mouths | (a) fix 3 voice-first animatic, 1:1 edit speed (removes TRUNC/SLOWMO/FREEZE) | CPU | 0 | animatic approval (gate 2, about 10 min) |
| | | (b) **Rhubarb + mouth sprites** on all calm talk shots (fix 5a) | CPU (this container / Actions) | 0 | 10 min to approve 18 sprites |
| | | (c) **LatentSync 1.6** (YuNet detector) on frontal close-ups | Modal A10G/L4/A100 | about $0.02-0.05 per 4 s clip [E] | 0 |
| | | (d) **InfiniteTalk** for single-face lines generated from the still + WAV (mouth right by construction) | Modal H100 | about $0.10-0.25 per 5 s [E] | 0 |
| | | (e) puppet route for long talk scenes: Blender Grease Pencil cut-out rig + Rhubarb, rendered headless | CPU | 0 | 30-60 min once per character to approve the rig |

### 3.1b Planning unit after the 1-minute format change (PRODUCTION-BIBLE, 2026-11-26)

Planning unit: **24 AI clips of 3 s per episode, 2 episodes per week** = 48 clips/week, about 208 clips/month (4.33 weeks). With a re-roll factor of 1.5 [E] that is **about 72 generations/week, about 312/month**, portrait first (bible GPU rule 4). Landscape adds up to 40% where re-framing fails [tools-buying-plan assumption].

| Source | Free capacity [S + E] | Clips per week it can supply | Share of the 72 generations/week | Publishable? |
|---|---|---|---|---|
| Kaggle T4 (LTX 0.9.8, about 52 s per clip at 480x832 incl. post [T fix-plan]; about 84 s at 576x1024) | 30 GPU-h/week, 22 h stop line; stills, voices, LoRAs take about 4-6 h/week [E] | about 600+ clips at 480x832 or 400+ at 576x1024 [E]: **GPU time is no longer the bottleneck** at 1-minute episodes | all of it, at T4 quality | yes |
| Modal $30/month (H100 about $3.95/h [S]); Wan 2.2 14B + Lightning, 3 s 720x1280 clip about 1-1.5 min incl. load share [E] | about 7.5 H100-h/month = about 1.7 h/week | about 70-100 clips/week [E] (fewer with AniSora or InfiniteTalk) | **the ~30-40% that matter (talk close-ups + gag shots, about 10 per episode = 20/week, x1.5 = 30 gens/week)** fits with room for lip-sync passes (about 15 talk shots/week x LatentSync at about $0.03 [E]) | yes (Apache-2.0 models) |
| Kling free (66 credits/day; about 10 credits per 5 s Standard clip [S]) | about 6 clips/day = 42/week | 42 | would cover over half, **but watermarked and non-commercial** | **no** |
| Google Flow free (50 credits/day; Lite 10, Fast 20) | 5 Lite or 2 Fast/day = 35 Lite or 14 Fast/week | 14-35 | **watermarked, commercial status unclear** | no (until clarified) |
| Vidu / Hailuo / PixVerse free | about 1-2 clips/day each [S, PixVerse 60 credits/day at 25-35 per clip] | 7-14 each | small | no |
| sync.so free / Hedra free | 3 gens/month / about 50 s/month | under 1/week | negligible | no |

Readings: (1) at 1-minute episodes the free GPU pair (Kaggle + Modal) covers the whole 2-per-week cadence on paper [E, to confirm with the first Modal ledger rows]; (2) even the most generous consumer free tier (Kling, about 42 clips/week) could carry most of an episode's volume, but none of it is publishable, so free tiers stay evaluation-only; (3) the 5-shot test (section 4) uses about 1-2 days of each tier's daily credits, nothing more.

All Modal costs are [E]: no Modal job has run yet. The first Modal job must log real minutes in `gpu-ledger.md` (add a "provider" column: Kaggle / Modal).

Modal budget rule (proposed, mirrors the bible's Kaggle rule): $30/month = about 7.5 H100-h [S rate], i.e. about 3.75 USD per episode at 8 episodes/month. Spend at most $20 on production clips, keep $10 for re-rolls and smoke tests; stop and re-plan at $25. Hero and talk shots only; wides, macros and silhouettes stay on Kaggle LTX 0.9.8.

### 3.2 Order to try (each step only if the previous one did not already fix the defect)

| Step | What | Accounts needed | Creator time | Decides |
|---|---|---|---|---|
| 0 | fix-plan fixes 1-4, 7, 10 on Kaggle + CPU (already planned) | none | animatic gate only | baseline defect counts after process fixes |
| 1 | Rhubarb + mouth sprites (fix 5a) | none | 10 min (approve sprites) | is anime mouth-flap sync good enough on talk shots |
| 2 | **Modal sign-up**, token as a GitHub Actions secret; a `modal_run.py` twin of `kaggle_run.py` (Claude builds it) | **Modal** (+ Hugging Face token for weights) | about 15 min once | the big-GPU path works |
| 3 | Modal smoke tests: Wan 2.2 14B + Lightning, AniSora V3.1, LTX-2.3 distilled, Wan VACE on the **5 test shots** (section 4); LatentSync 1.6 and InfiniteTalk on T2 + the T1 Uncle line; Qwen-Image-Edit-2511 on the 5 worst stills | same | 0 (Claude), then 15 min to watch the side-by-side | which open model wins each shot type |
| 4 | klein 4B LoRAs for Boy, Uncle, Grandma (ai-toolkit, Kaggle) | none new | 5 min (approve sheets) | drift + duplicate source removed |
| 5 | **Free-tier evaluation** of commercial services on the same 5 shots: Google Flow (Veo 3.1 Lite/Fast), Kling, Vidu, Hailuo, PixVerse (+ sync.so 3 free gens and Hedra free on T2) | 5-7 consumer accounts | about 20-30 min per service, spread over 2-3 days because of daily credits [E]; about 3 h total | is any paid model worth its price vs the free Modal winner; **nothing from this step is published** |
| 6 | Only if step 5 shows a clear gap: buy per `tools-buying-plan.md`, or try the Google Cloud trial / Vertex route (5.3) | Google Cloud (card) | 30 min | |

Daily clicking: steps 0-4 need **no daily clicking** (Claude runs Kaggle and Modal through GitHub Actions). Step 5 is a one-off evaluation; there is no production plan that depends on daily free credits, because those outputs cannot be published.

---

## 4. The fair 5-shot comparison test

### 4.1 Shots (identical to `tools-buying-plan.md` 4.2, so free and paid results share one table)

| Test | Source shot | Stresses | Defect it probes |
|---|---|---|---|
| T1 Two-shot banter | C10 "Veterans." | 2 characters side by side, deadpan vs manic | duplicates |
| T2 Talking close-up | C36 "Dad was right..." | child face under the hat, subtle acting, then lip-sync | smear, sync |
| T3 Keyframe gag, big pose change | C01 cold open | smear between poses, sweat drop, steam | smear, morph |
| T4 Three characters + hands + food | C17 "That's a sock." | 3 identities, hands, dough | duplicates, identity |
| T5 Fast chase | intro I5_chase variant 2 | bodies at speed, tracking, both orientations | duplicates in motion, smear |

Inputs, prompts and the Step 0 still repair are exactly those in `tools-buying-plan.md` 4.2 (paths under `tools/episode_maker/gpu/inputs/ep01v44-clips-1/images/`, cast sheet `gpu/inputs/intro-v3/refs/characters.jpg`).

### 4.2 Fairness rules (free tiers differ in resolution, watermark and length)

1. **Same inputs, same prompt text, no per-vendor tuning in round 1**, 1 take per shot, audio off, 9:16 (T5 also 16:9), 5 s or the nearest length the tier allows (record it; only the first 3 s are scored, matching the 1-minute format's 2-3 s clips, and the full length is kept for the paid-plan comparison in `tools-buying-plan.md`). Use the same seed where the tool exposes one.
2. **Record the tier's native output** (resolution, fps, length) and **normalize for judging**: scale every clip to 720x1280 at 24 fps for viewing; judge native detail separately in the "native res" column, not inside the quality scores.
3. **Blind judging**: Claude renames files to random ids, and the same black bar is overlaid on every clip where any watermark sits (free tiers put marks in corners), so the judge cannot tell the vendor. The id key stays in a private note until scoring is done.
4. **Automatic metrics first**: run `qc_clips.py` on every clip (stripes, face count vs expected, face height %, face sharpness, frame jump, text boxes, START/END match). Then the human contact sheet at 4 frames per second (rubric "How to use it").
5. **Log the costs that free tiers hide**: queue wait (minutes from submit to result), credits used, creator minutes spent clicking, and whether the free result could ever be published (commercial yes/no).
6. Round 2 (top 2 only): prompt-tuned, 2 takes each, both orientations.

### 4.3 Scoring sheet (copy one per tool; criteria mapped to `quality-research.md` rubric IDs)

Score each take 0-5. **CRITICAL rubric items are gates**: a take that fails C1 (a second instance of a named character or an extra person), D1 (eye or mouth vanishes, doubles or smears for 2+ frames on a face of 10%+ height) or B5 (garbled AI text) scores **0 on that criterion and cannot be "usable"**.

| Criterion (rubric IDs) | Weight | How measured | T1 | T2 | T3 | T4 | T5 | Mean |
|---|---|---|---|---|---|---|---|---|
| Identity and costume lock vs model sheet (C2, C4, C5) | 25% | contact sheet vs cast sheet; costume checklist C4 | | | | | | |
| No duplicates, extra people, extra limbs (**C1** gate, C6) | 20% | `qc_clips.py` faces key/first/last vs expected + human count | | | | | | |
| Face integrity and within-clip stability (**D1** gate, C3) | 20% | QC face sharpness, FACE_SMEAR flag, frame-step on eyes and mouth | | | | | | |
| Acting and weight (D3, D4, D5) | 15% | anticipation, contact, settle; listener reacts; no frozen stretch over 1.5 s | | | | | | |
| Adherence (reaches END keyframe, camera as asked) (D6, D2) | 10% | QC key-pair match, motion vs prompt | | | | | | |
| Style and clean frame (G1, G2, **B5** gate, B6, B7) | 10% | palette vs sheet swatches, no text, no flicker or stripes | | | | | | |
| **Weighted score (out of 5)** | | | | | | | | |
| Usable takes / total (all gates pass, weighted at least 3.0) | gate | | | | | | | |
| Native resolution / fps / length | info | | | | | | | |
| Queue minutes / credits used / creator minutes | info | | | | | | | |
| Commercial use on this tier (Y/N) and on the cheapest paid tier (Y/N, price) | gate | | | | | | | |
| Automatable with a key (Y/N); accepts a child character (Y/N) | gate | | | | | | | |

Lip-sync sheet (T2 + the T1 Uncle line, per tool: Rhubarb sprites, LatentSync 1.6, InfiniteTalk, MuseTalk, sync.so free, Hedra free):

| Criterion (rubric) | Threshold | Score 0-5 |
|---|---|---|
| Onset/offset sync (**E1**) | mouth starts within -1/+2 frames at 24 fps of the voice, stops within 2 frames of the line end | |
| Silent mouths stay silent (**E2**) | no flap over 4 frames during another character's line | |
| Mouth stays in style | no realistic teeth or lips, line art kept | |
| Rest of face unchanged, no flicker at clip edges (B6) | | |
| Works on the Uncle's mustache and under the Boy's hat shadow | | |

Decision rules (aligned with `tools-buying-plan.md` 4.5): adopt an open model for a shot type if weighted at least 3.8, zero duplicates in at least one of two takes on T1 and T4, T2 face score at least 4, usable-take rate at least 50%. **A paid model is worth buying only if it beats the best free (Modal) model by at least 0.5 weighted points on the shot types it would be used for**, or passes a gate the free model fails. Lip-sync: adopt the best E1/E2 tool that keeps the face in style; if none scores 3.5 on anime mouths, keep Rhubarb sprites and stage the rest (rubric E3).

---

## 5. Who signs up for what

All accounts use the channel's business identity only (The Dumpling Boy, the studio Gmail), with two-factor login; no personal name, email or payment detail goes into chat, files or commits (CLAUDE.md rules 1 and 4). **The sign-up URLs below are from memory [M] because the fetch tool could not open vendor pages; open them from the vendor's home page if one has moved.**

### 5.1 Claude can run alone once a key exists (creator signs up once, then pastes the key only into the secure form or a GitHub secret)

| Service | Sign-up URL | Key goes to | Host / header [M, confirm at setup] | Why |
|---|---|---|---|---|
| **Modal** (free $30/month) | https://modal.com/signup | **GitHub Actions secrets** `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET` (creator adds them in the repo's Settings, Secrets and variables, Actions) | SDK uses gRPC to `api.modal.com`; proxy injection unverified, so run Modal jobs from Actions like Kaggle | big GPU for FREE STACK 2.0 |
| **Hugging Face** (free) | https://huggingface.co/join, token at https://huggingface.co/settings/tokens (read-only token) | Actions secret `HF_TOKEN` for weight downloads; optionally the environment's secure credential form | `huggingface.co`, `Authorization: Bearer` | gated weights, faster downloads; ZeroGPU only for tiny tests |
| Kaggle (existing) | already set up | existing Actions secret | | unchanged |
| Google AI Studio (free tier) | https://aistudio.google.com/apikey | secure credential form | `generativelanguage.googleapis.com`, `x-goog-api-key` | text helpers only; **image and video are not free** |
| Cloudflare Workers AI (optional) | https://dash.cloudflare.com/sign-up | secure credential form | `api.cloudflare.com`, Bearer | draft images only; low priority |
| fal.ai / Replicate (optional, for whatever starter credit they give) | https://fal.ai (Sign up), https://replicate.com/signin | secure credential form | `queue.fal.run` (`Authorization: Key`), `api.replicate.com` (Bearer) | free starter credit, if any, goes to the 5-shot test |
| ElevenLabs free (optional) | https://elevenlabs.io/sign-up | secure credential form | `api.elevenlabs.io`, `xi-api-key` | listening test only (non-commercial) |

Result-download hosts (for example fal's media CDN, `replicate.delivery`, `*.hf.space`) must be allowed in the environment's network settings; Claude proposes each exact host through the environment approval prompt the first time a download is blocked.

### 5.2 The creator must use personally (web UI, manual clicking; evaluation only, never published)

| Service | Sign-up URL [M] | Daily free | What to run | Est. creator time |
|---|---|---|---|---|
| Google Flow (Veo 3.1) | https://labs.google/flow | 50 credits/day | T1-T5 at Lite (10 credits) over 1-2 days; T2/T3 at Fast | 30 min |
| Kling | https://klingai.com | 66 credits/day | T1-T5 Standard 5 s over 1-2 days | 30 min |
| Vidu | https://www.vidu.com | daily login credits | T1, T4 (reference-to-video), T2 | 20 min |
| Hailuo | https://hailuoai.video | trial credits | T2, T3, T5 | 20 min |
| PixVerse (optional) | https://app.pixverse.ai | 60/day | T1, T3 | 15 min |
| Dreamina (optional, read its terms first) | https://dreamina.capcut.com | 120/day | T1, T4 (Seedance 2.0) | 20 min |
| sync.so | https://sync.so | 3 gens/month | T2 lip-sync, T1 Uncle line | 10 min |
| Hedra | https://www.hedra.com | 300 credits/month | T2 still + WAV | 10 min |

Claude prepares a per-service folder with the exact inputs and the prompt text to paste, then collects the downloaded clips for blind scoring. **Skip entirely** (no useful free tier for us): Higgsfield, Pika, Runway, Luma, Krea, Leonardo, Freepik, Scenario, Civitai, HeyGen, Suno, Cartesia, Lightning AI, Paperspace, Colab (manual backup only), OpenRouter/Groq/Together.

### 5.3 Google Cloud trial / Vertex AI (only after the free stack, step 6)

- $300 for 90 days, new customers, payment card required [S-off]. It pays for Vertex AI, **not** for the Gemini API in AI Studio [S-off]. Veo 3.1 coverage: unverified.
- Automation problem: Vertex normally authenticates with a service-account key file or short-lived OAuth tokens [M]; a key file in the sandbox breaks CLAUDE.md rule 4. Options to check before signing up: (a) a Vertex API key bound to a service account, if Google offers it for Veo in the creator's project [M, unverified], injected by the proxy on `aiplatform.googleapis.com`; (b) run Vertex calls from GitHub Actions with Workload Identity Federation (no stored key) [M]; (c) the creator runs Veo in the Vertex AI Studio console by hand.
- Veo person-generation settings may block images of a child character [M]: test T2 (the Boy) first.

---

## 6. ToS and licence traps (skeptic's checklist)

1. **Free tier = non-commercial** for Kling, Hailuo, Luma, Vidu, PixVerse, Hedra, HeyGen, ElevenLabs, Cartesia, Suno, Krea, Freepik, Scenario, Higgsfield (sections 1a-1c). Evaluation is fine; publishing is not.
2. **No retroactive licence**: Suno and Scenario state that a later subscription does not license free-plan output [S-off]. Assume the same everywhere: regenerate the chosen shot on a paid plan.
3. **Visible watermarks** (Kling, Hailuo, Vidu, PixVerse, Runway, Luma, Flow/Veo, sync.so, HeyGen): never crop or remove them (also `tools-buying-plan.md` 5.3); SynthID stays in Veo output on every tier [S].
4. **Inputs become training data or public**: Gemini API free tier uses prompts and outputs to improve Google products [S-off terms 2026-03-23]; Leonardo free outputs are public and owned by Leonardo as between the parties [S-off]; Kling reportedly takes a sublicensable licence over uploaded content [S, single source]; CapCut-family terms are broad [S]. Our unreleased character art is the asset at risk: for free-tier tests upload only the 5 test stills, nothing else.
5. **Territory licences**: Tencent Hunyuan family (HunyuanVideo, FramePack, HunyuanVideo-Foley) excludes the EU, UK and South Korea, including outputs [S-off]. A worldwide YouTube channel cannot comply. Reject.
6. **Hidden non-commercial dependencies**: InsightFace models (InstantID, PuLID, IP-Adapter-FaceID, LivePortrait, LatentSync preprocessing); FLUX.1 [dev] base under Apache-labelled wrappers (USO); a Qwen2.5-Omni-3B text encoder inside an ACE-Step 1.5 variant (research licence) [S-off]; community ESRGAN weights under CC-BY-NC-SA [S]. Check every component, not only the headline repo.
7. **Licence drift**: Qwen-Image 2.1 switched to a non-commercial research licence on 2026-09-20 while 2511 stayed Apache [S]; FLUX.2 klein 9B is non-commercial while 4B is Apache [S-off]; LTX-2.3's licence is described as both Apache and Community [S]. Pin exact model versions and save the LICENSE text and date in the per-episode licence log.
8. **Unclear status = do not use**: SkyReels V3 (no licence in README), IndexTTS2/2.5 (Bilibili licence), VibeVoice, Dreamina free output, Google Flow free output.
9. **Free compute terms**: Kaggle and Colab are free notebooks with no output restrictions that I found [M], but Colab's free tier is aimed at interactive use [M]; Modal and Lightning change credit rules (Lightning twice in 2026) [S]. Keep the Kaggle path working as the fallback.
10. **YouTube side** (unchanged from `tools-buying-plan.md` 5.3): keep proof of human authorship per episode; the July 2026 inauthentic-content clarification targets mass-produced template content [S].

---

## 7. What this changes in other documents (for the main session to apply)

- `tools-buying-plan.md` purchase #3: the $300 Google trial **cannot** pay for the Gemini API in AI Studio; Nano Banana Pro on the trial would have to go through Vertex AI. Free-tier Gemini API has no image quota.
- `PRODUCTION-BIBLE.md` GPU rule "overflow option: Modal monthly free credits": confirmed as $30/month on the Starter plan [S-off]; recommend activating it now for talk and hero shots (FREE STACK 2.0), with its own ledger column and a $25 stop line.
- `fix-plan.md` fix 5b and fix 9: run LatentSync 1.6 (18 GB) and the face detail pass on Modal instead of a T4; add InfiniteTalk as a third lip-sync candidate; add Qwen-Image-Edit-2511 to fix 1 for still repair.
- `motion-tech.md` licence table: add AniSora V3 (Apache-2.0), Wan 2.2 Lightning LoRAs (Apache-2.0), Wan VACE (Apache-2.0 [M]); keep HunyuanVideo rejected.

---

## 8. Sources (search-result snippets, 2026-11-26)

Video free tiers: https://eesel.ai/blog/kling-ai-pricing · https://whichoneisreal.com/posts/kling-ai-free-tier-2026/ · https://marcandrews.com/kling-ai-free-plan-2026-what-66-credits-buys/ · https://www.aitoolcurator.com/learn/kling-guide/free-plan-limits/ · https://www.glbgpt.com/hub/can-i-use-kling-ai-for-commercial-use/ · https://licenseorg.com/guide/ai-content/kling-ai · https://www.tomsguide.com/ai/this-ai-video-generator-is-going-viral-and-its-completely-free-to-use · https://wavespeed.ai/blog/cost-and-billing/hailuo-ai-pricing-2026/ · https://www.atlascloud.ai/blog/guides/hailuo-ai-free-credits · https://lumalabs.ai/learning-hub/licensing · https://eesel.ai/blog/luma-ai-pricing · https://wavespeed.ai/blog/cost-and-billing/vidu-ai-pricing-2026/ · https://www.costbench.com/software/ai-video-generators/vidu/free-plan/ · https://www.atlascloud.ai/nl/blog/guides/pixverse-ai-free · https://help.runwayml.com/hc/en-us/articles/50404627334547-Free-plan-details · https://pika.art/pricing · https://www.usagepricing.com/blueprint/activity/pika-labs-2026-09-20-free-tier-zero-credits · https://higgsfield.ai/creator-hub/help-center/plans/what-does-the-free-plan-include · https://wavespeed.ai/blog/cost-and-billing/google-flow-pricing-2026/ · https://blog.google/products/gemini/veo-3-expansion-mobile/ · https://discuss.ai.google.dev/t/inquiry-about-commercial-use-of-videos-generated-via-google-labs-flow-free-tier-for-a-contest/169174 · https://ppc.land/google-vids-gets-free-veo-3-1-video-generation-music-and-ai-avatars/ · https://dreamina.capcut.com/ai-video/free-ai-video-generator-usable-clips-guide-2026 · https://wavespeed.ai/blog/cost-and-billing/dreamina-pricing-2026/ · https://www.latestly.com/socially/technology/xai-restricts-grok-imagine-image-and-video-generation-to-supergrok-subscribers-ends-free-access-7365341.html · https://fal.ai/grok-imagine-free

Google: https://discuss.ai.google.dev/t/free-tier-api-image-generation/177423 · https://blog.laozhang.ai/en/posts/gemini-image-generation-free-limit-2026 · https://www.engadget.com/ai/google-limits-free-nano-banana-pro-image-generation-usage-due-to-high-demand-223442929.html · https://ai.google.dev/terms · https://discuss.ai.google.dev/t/clarification-on-only-paid-services-for-eea-ch-uk/107860 · https://cloud.google.com/free-trial/ · https://docs.cloud.google.com/free · https://docs.cloud.google.com/free/docs/free-cloud-features.md.txt · https://discuss.ai.google.dev/t/google-ai-studio-do-not-use-my-1300-credits-shown-on-google-cloud/140442 · https://cloud.google.com/use-cases/free-ai-tools · https://blog.google/innovation-and-ai/technology/developers-tools/google-cloud-credits-gdp-ai-studio/ · https://www.techradar.com/computing/artificial-intelligence/this-simple-trick-gets-you-3-months-of-google-gemini-veo-3-for-free-heres-how-you-can-create-the-best-ai-videos-without-dropping-a-dime · https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview · https://cloud.google.com/resources/cloud-express-faqs

Images: https://zsky.ai/blog/is-krea-free · https://www.leonardo.ai/news/can-you-use-ai-generated-images-commercially · https://terms.law/ai-output-rights/leonardo/ · https://www.freepik.com/ai/docs/pricing · https://help.scenario.com/en/articles/frequently-asked-questions-faq/ · https://help.scenario.com/en/articles/pricing-plans/ · https://flowith.io/blog/civitai-membership-2026-free-vs-supporter-vs-buzz-credits · https://education.civitai.com/using-civitai-the-on-site-image-generator/ · https://developers.cloudflare.com/workers-ai/platform/pricing/ · https://developers.cloudflare.com/changelog/post/2026-07-28-models-require-workers-paid/

Voice, lip-sync, music services: https://elevenlabs.io/docs/overview/administration/billing · https://elevenlabs.io/sv/pricing/api · https://www.cartesia.ai/pricing · https://sync.so/docs/free-trial · https://support.sync.so/articles/7391977257-sync-support-faq · https://www.hedra.com/plans · https://zsky.ai/blog/is-heygen-free · https://help.suno.com/en/articles/9601601 · https://suno.com/pricing · https://www.musicinafrica.net/magazine/suno-adjusts-ai-music-ownership-terms-after-warner-music-partnership · https://dupple.com/learn/is-suno-free

Compute: https://modal.com/pricing · https://www.costbench.com/software/ai-gpu-cloud/modal/free-plan/ · https://www.mintlify.com/cheahjs/free-llm-api-resources/providers/trial/modal · https://www.usagepricing.com/blueprint/activity/lightning-ai-2026-09-21-gpu-rate-card-reprice · https://pricingsaas.com/companies/lightning/diffs/2026W46 · https://aicreditmart.com/ai-credits-providers/lightning-ai-free-plan-22-gpu-hours-month-guide-2026/ · https://gpuperhour.com/blog/free-cloud-gpus-and-credits · https://huggingface.co/docs/inference-providers/pricing · https://huggingface.co/pricing · https://discuss.huggingface.co/t/getting-you-have-exceeded-your-pro-gpu-quota-error-even-with-credits-loaded/174850 · https://huggingface.co/docs/hub/spaces-zerogpu · https://huggingface.co/docs/hub/spaces-api-endpoints · https://yangmao.ai/en/providers/fal/free-tier/ · https://markaicode.com/pricing/fal-ai-pricing/ · https://www.fal.ai/legal/terms-of-service · https://yangmao.ai/en/deals/replicate-free-tier/ · https://www.runpod.io/referral-program · https://openrouter.ai/docs/api/reference/limits.md · https://www.truefoundry.com/ja/blog/openrouter-rate-limits-your-free-tier-depends-on-what-youve-already-paid

Open models and licences: https://github.com/bilibili/Index-anisora · https://huggingface.co/IndexTeam/Index-anisora/tree/main · https://animecorner.me/bilibili-ai-anime-generation-model-anisora/ · https://huggingface.co/Doubiiu/ToonCrafter · https://github.com/ToonCrafter/ToonCrafter · https://huggingface.co/Lightricks/LTX-2.3/blob/main/LICENSE · https://static.lightricks.com/legal/ltx-2-open-weights-license-0.X.pdf · https://invideo.io/blog/ltx-ai-video-generator/ · https://rits.shanghai.nyu.edu/ai/ltx-2-3-sharper-video-native-portrait-and-cleaner-audio-in-lightricks-latest-open-source-model/ · https://venturebeat.com/ai/ltx-2-5-can-generate-a-10-second-ai-video-from-an-image-in-just-6-8-seconds-on-nvidia-superchips-and-its-open-weights/ · https://huggingface.co/tencent/HunyuanVideo-1.5 · https://wavespeed.ai/blog/competitor-comparison/wan-3-0-vs-hunyuan-video/ · https://huggingface.co/Wan-AI/Wan2.2-Animate-14B-Diffusers/blob/main/README.md · https://build.nvidia.com/wan-ai/wan2.2-animate-2-14b/modelcard · https://huggingface.co/lightx2v/Wan2.2-Distill-Loras · https://huggingface.co/lightx2v/Wan2.2-Lightning · https://raw.githubusercontent.com/ModelTC/LightX2V/main/README.md · https://huggingface.co/Leon1000/Wan2.2_I2V_LightX2V_2Step · https://arxiv.org/abs/2601.17323 · https://www.sourcepulse.org/projects/25003051 · https://huggingface.co/Skywork/SkyReels-V2-T2V-14B-720P-Diffusers/blob/main/LICENSE · https://huggingface.co/Qwen/Qwen-Image-Edit-2511 · https://www.creativeainews.com/articles/qwen-image-2-1-research-license-commercial-use-2026/ · https://bfl.ai/blog/flux-1-kontext-dev · https://raw.githubusercontent.com/black-forest-labs/flux2/HEAD/README.md · https://bfl.ai/blog/flux2-klein-towards-interactive-visual-intelligence · https://huggingface.co/blog/black-forest-labs/flux-2-klein-lora · https://docs.bfl.ai/flux_2/flux2_klein_training · https://huggingface.co/bytedance-research/USO · https://huggingface.co/bytedance-research/UNO · https://arxiv.org/abs/2506.18871 · https://huggingface.co/h94/IP-Adapter-FaceID/discussions/77

Lip-sync open: https://github.com/bytedance/LatentSync · https://arxiv.org/html/2412.09262v2 · https://www.creativeainews.com/articles/open-source-lip-sync-licenses-commercial-use-2026/ · https://www.pixazo.ai/blog/best-open-source-lip-sync-models · https://huggingface.co/MeiGen-AI/InfiniteTalk · https://github.com/MeiGen-AI/InfiniteTalk · https://github.com/MeiGen-AI/MultiTalk · https://gitee.com/imjesson/rhubarb-lip-sync · https://github.com/scaredyfish/blender-rhubarb-lipsync

2D tools: https://alternativeto.net/software/live2d/?license=free · https://kitsunebi-games.itch.io/inochi-creator · https://alternativeto.net/software/nijigenerate/about

Upscaling: https://raw.githubusercontent.com/Kiteretsu77/APISR/main/README.md · https://huggingface.co/easygoing0114/AI_upscalers

Voice, SFX, music open: https://www.assemblyai.com/blog/free-open-source-text-to-speech · https://andrew.ooo/answers/best-open-source-text-to-speech-models-2026/ · https://huggingface.co/ngoctham/IndexTTS-2.5 · https://huggingface.co/bosonai/higgs-audio-v3-tts-4b · https://arxiv.org/abs/2601.15621 · https://rekkerd.org/sonniss-releases-gdc-2026-game-audio-bundle/ · https://licenseorg.com/guide/music-audio/sonniss · https://bedroomproducersblog.com/2024/06/27/sonniss-gdc-2024/ · https://app.cinevva.com/guides/free-sound-effects-music · https://en.Wikipedia.com/wiki/Freesound · https://invideo.io/blog/open-ai-voice-audio-models/ · https://huggingface.co/tencent/HunyuanVideo-Foley/tree/main · https://huggingface.co/ACE-Step/acestep-v15-base/blob/main/README.md · https://huggingface.co/ACE-Step/Ace-Step1.5/discussions/27 · https://arxiv.org/abs/2602.00744

Colab/Kaggle: https://gpuperhour.com/blog/free-cloud-gpus-and-credits · https://amitpandeytiktok.github.io/awesome-free-compute-2026/compute.html
