# V4 senior advisor review

Date: 2026-11-25. Reviewer: senior advisor. Internal, English only, not for publication.
Read: `CLAUDE.md`, `production/v4/BRIEF.md` (ground truth), `production/v4/video-tech.md`, `production/v4/director-treatment.md`, `production/v4/comedy-style.md`, `scripts/episode-01-v4.md`, `production/v4/content-research.md`, `production/v4/marketing.md`, `HANDOFF.md`, `production/animation-roadmap.md`, `production/character-bible.md`. Watched: `tools/episode_maker/out/rig-test.mp4` (frames at 1.5, 4.5, 5.9, 7.3 s), `tools/episode_maker/out/grandma-test.mp4`, the contact sheet `rig-test-contact.png`, and the source cut-outs in `tools/episode_maker/specs/puppets/`. Also checked what the Canva `create-video` tool actually does today.

## 0. Bottom line
1. **The writing is close.** The host + chaos co-host + mock-epic narrator formula is right, and it can make adults laugh as well as kids. It needs trimming, not a rewrite (section 1.1).
2. **The video plan is wrong for this creator.** The free skeletal rig is "puppets again": the characters face the camera, the arms are stiff flaps, and the background is drawn in a different style. The creator has already rejected this look twice: the v3 stills and the breathing/blinking puppet demo. More layered art will not fix it, because Canva cannot reliably produce that art.
3. **Decision: change the main route to keyframes + image-to-video.** Approved Canva stills become the first frame (and the last frame when needed) of short AI image-to-video clips for every shot where a character acts. The existing local pipeline does everything else: voices, music, captions, TV graphics and impact frames. The rig moves to the paper-cut legend world, where a cut-out look is the intended style. This costs a small amount of money (about 25 USD per episode). Free options are tested first, but none of them can carry a weekly show (section 2).
4. **The director's 69-shot / 116-asset plan cannot be produced.** Reorganize it as about 30 "generation units" of 4-5 s each, and make the 60-70 edit cuts inside those clips.
5. **Prove it on 20 seconds before anything else** (cold open + burn), shown side by side with the rig version, before 18 Dec 2026.

---

## 1. Verdict on each deliverable

### 1.1 Script + comedy bible (`scripts/episode-01-v4.md`, `comedy-style.md`): B+, keep, trim
**What works**
- **Host + ancient mood works.** The Boy as a deadpan prime-time presenter, the Uncle as a self-appointed co-host, and a gong-and-scroll narrator who treats a burned tongue like an epic. The "live show" world uses clean TV graphics and the "Scroll" world uses paper-cut at 8 fps. This is a real format with two registers, and it answers the brief directly.
- **Adults will laugh at:** "He is not the host." / "Co-host!" / "He is luggage."; the lower-third that goes from "self-appointed" to "approved"; "That's historian for 'please don't quote me'"; "Yesterday, a napkin."; "Destiny is steamed."; "brought to you by Uncle's tongue". These are real two-level jokes: kids get the surface, adults get the TV-cliché layer. **Kids get** the ear toots, the floating Uncle, the camel and the intermission card.
- **The burned-tongue chain is the best structural idea in the package.** The Uncle burns his tongue, then Dad's line ("rush it, you get burned"), then Grandma reveals that Dad burned his tongue too, then the ice-bucket sting. It turns the gag into the episode's heart. Protect it.
- The comedy bible is solid and properly sourced. Its ban list (no jokes on places, people, size or Dad's death) matches `CLAUDE.md`.

**What to fix**
1. **Too dense.** The script has 56 beats in 2:05 and 17 laugh beats in the first 60 s, against the bible's own target of 10. Deadpan comedy needs air: the 0.4-2 s holds after a line *are* the joke. At this density, the TTS voices and fast cuts will run the jokes over each other. Target: **about 45 beats, 2:00 including the sting.**
2. **Cut:** beat 31 ("One of them has no eyelids": muddled, the dumpling has no eyes either); beat 41's four-claimant tug-of-war (four name flags in 1.6 s are unreadable on a phone; keep only the asterisk line, which is the factual safety net); one or two camel appearances. The camel appears five times, which breaks the bible's own "max three per episode" rule, and every camel shot means keeping a fourth recurring character consistent.
3. **The cold open does not match its payoff.** The cold open shows the Uncle floating in a **shop interior** with a balloon face. The real burn happens at an **outdoor stall**, where he rockets up and runs in circles. "Six hours earlier" promises a flash-forward, so it must show the same moment. Fix: cut the cold open from the burn clip itself (same stall, same toot pose). This also saves one AI generation.
4. **The "Silk Road" promise has no real Silk Road fact in it.** The research says plainly that nothing ties the xiaolongbao to the Silk Road. It offers a FIRM bridge instead: the Tang/Song port of Qinglong near Shanghai, a Maritime Silk Road starting point that shipped ceramics to Japan and Korea. Put one narrator sentence about it into the old-road segment, or swap it for the fun-fact beat. Marketing wants "Silk Road" as the searchable promise, so the episode has to deliver on it.
5. **Voice is the hidden comedy risk.** The Uncle's range (huge, then tiny) and the 8-frame deadpan timing depend on performance. The Kokoro voices are flat. Test the Uncle's voice in the pilot. A better Uncle voice is the second-best upgrade after motion (marketing agrees).

### 1.2 Content research: A-, the most reliable document
It uses honest confidence tags (FIRM / LEGEND / DISPUTED / WEAK) and gives the script the right fixes: no "thin skin" in 1871, the pagodas are about 11 m, Beijing has banned fireworks, the Ep 3 filling amount is wrong. The script took these on board. One open item: most facts come from search excerpts because the hosts were blocked. Re-open the WEAK-tagged URLs before upload, as the file itself says.

### 1.3 Director's treatment: strong craft, plan cannot be produced as written
- **Good:** the visual bible (hold-then-hit, one idea per shot, vertical safe zones, the three registers, transitions, sound sync rules) is professional. Keep sections 1.1-1.15 as the series style guide.
- **Problem 1: method.** 43 of 69 shots (65%) are marked "R Rig". That is exactly the puppet look the creator rejected.
- **Problem 2: volume.** 69 shots averaging 1.81 s. The v3 episode had 65 fast shots, and the creator said that only its captions were right. More cuts do not equal more animation. A dialogue-led deadpan comedy needs some 2.5-3.5 s holds.
- **Problem 3: assets.** 116 MUST items, including turnarounds, 14-head expression sheets, 13-hand sets, back views and walk cycles. Canva generates "the Boy alone" poorly, needs about 3 attempts per asset and hits quota cooldowns. That is roughly 350 generations for one episode, and turnaround or part consistency is the one thing it is worst at. It will not get done.
- **Problem 4: stale text.** Legend shots 42-46 still carry the old narration ("rose before dawn", "dared to make his buns small", **"Paper-thin skin"**), which the research flagged as probably wrong and the script removed. The header also says `content-research.md` "does not exist yet". Re-sync the legend shots to script beats 36-41 before anyone builds them.
- **Problem 5: hero shot H7** asks for one 13 s AI clip. AI clips are reliable at 4-5 s, so split it.
- **Fix:** keep the shot intents, regroup them into **about 30 generation units** (one continuous action each, 4-5 s), and make the cuts, punch-ins and reaction cutaways inside those clips in the edit. One 5 s burn clip can yield 3-4 cuts (ECU mouth, eye twitch, wide rocket) with digital zoom. The edit can still have about 60 cuts.

### 1.4 Marketing: B+, honest about money, two calls to reverse
- **Good:** the "not made for kids" analysis and the audience memo; honest Shorts revenue figures (low hundreds of USD in year 1); the "launch only with 3 finished + 2 storyboarded" gate; Lunar New Year (6 Feb 2027) as the anchor; the 50 USD/month cap for months 1-3; "voice is the second upgrade".
- **Reverse:** renaming the show to "The Dumpling Road". The public identity (The Dumpling Boy, @TheDumplingBoy.studio, the site, Ko-fi) is fixed in `CLAUDE.md`. Put "Silk Road" in titles and the series tag instead.
- **Postpone:** the three-file package (Short + re-edited cutdown + 16:9 compilation). It triples editing before the production method even exists. Start cutdowns after Ep 3 is done.
- **Adjust:** the 12 Jan 2027 launch is realistic only if the 20 s pilot is approved by about 18 Dec. Otherwise target 26 Jan, still before Lunar New Year.
- **Watch:** the hook test with 8-10 strangers must be run privately, offline on a phone. Never use an unlisted or public link, and never use personal accounts.
- Note that the 50 USD/month cap and a weekly cadence do not fit together (see 2.4). The creator must choose (question 2).

### 1.5 Video tech: excellent engineering, wrong primary route
- **Good:** an honest environment check (Hugging Face blocked, no GPU, RIFE runs on CPU, `bpy` works), a working rig with weight, overshoot, eye tracking and audio-driven mouths, clear install steps, and a paid fallback with a trigger rule.
- **The verdict the brief asked for:** the rig will not satisfy the creator. The engineer's own words are "motion is that of a cut-out puppet: front view only". In the frames I watched, both characters face the lens in a fixed stance. The Uncle's raised sleeve is a flat white flap, and the Boy's arms go out like a scarecrow's. The vector street is a flat geometric style that clashes with the painted characters, and Grandma is drawn in yet another style. It is the rejected puppet demo with joints. Its proposed fix (layered parts, 3/4, profile and back views, key poses, about 2400 px art) runs into the same wall as the director's asset list: Canva cannot reliably produce consistent turnarounds and body parts. The current Boy cut-out is only 562x1350 px.
- **Ordering error:** it says to build the layered art first and buy AI only later. The cheaper and faster test is the reverse, because image-to-video needs only full stills, which the existing `make-episode-frames` workflow already produces (35 frames for Ep 1, media IDs in `HANDOFF.md`).
- **Keep:** RIFE, the audio-driven mouth code (for the paper-cut world), `street.py` for map and graphic backgrounds, and the whole audio/caption pipeline.

### 1.6 Contradictions between documents
| # | Contradiction | Resolution |
|---|---|---|
| 1 | Director plans 69 shots; engineer's throughput (video-tech section 10) assumes about 30 shots of 4 s | About 30 generation units, about 60 edit cuts |
| 2 | Director: 116 MUST assets incl. turnarounds and hand sets; engineer: "10-15 new assets per episode once kits exist"; Canva: Boy alone fails often, about 3 tries each, cooldowns | About 35-45 full keyframe stills per episode (a proven workflow), no part kits for the main cast |
| 3 | Director: 65% rig; brief: puppets rejected | Rig only for the paper-cut legend and map |
| 4 | Script 2:05 (293 words) vs director 285 words vs brief "about 2:00" | 2:00 including the sting, about 260 words |
| 5 | Director legend narration ("Paper-thin skin") vs script and research (thin skin removed) | Use script beats 36-41 |
| 6 | Cold open (shop, floating) vs burn (stall, rocket) | Cold open is cut from the burn clip |
| 7 | Comedy bible "max 3 appearances" vs camel in 5 beats | Camel 3x: caravan, metro, sting |
| 8 | Marketing renames the show; `CLAUDE.md` fixes the identity | Keep the name, add "Silk Road" to titles |
| 9 | `HANDOFF.md`: "we do not need Canva video anymore" | Outdated: Canva video is a free pilot engine from 16 Dec |
| 10 | Marketing caps spend at 50 USD/month; a weekly episode needs about 100 USD/month | Creator chooses cadence or budget (question 2) |
| 11 | Grandma art is drawn in a different style from Boy and Uncle | Regenerate Grandma stills in the picture-book style before Ep 1 |

---

## 2. The core decision: how to get real anime-style video

### 2.1 The options, judged against the brief
| Option | Real animation (walk, turn, gesture, camera through a living scene)? | Same drawing? | Weekly-sustainable? | Cost | Verdict |
|---|---|---|---|---|---|
| A. Code skeletal rig (current) | No: front view, stiff, reads as a puppet | Yes, exactly | Yes | Free | **Reject for the main cast.** Keep for paper-cut legend, map and graphics |
| A+. Rig with layered art from Canva | Somewhat better, still a cut-out | Yes | No: the art cannot be produced reliably | Free, huge art effort | Reject |
| B. Free GPU (Kaggle/Colab, Wan 2.2 5B, LTX-Video) | Yes, at 480-720p | Medium drift | **No.** About 75 attempts per episode at 10-30 min each on a T4 is 12-35 GPU hours, against Kaggle's roughly 30 hours a week. The creator would have to run notebooks by hand, which breaks "the creator only approves results" | Free | Optional experiment only |
| C. Canva `create-video` (engine: Seedance, 5-30 s, up to 12 shots, Canva reference images for identity, 720p, 9:16) | Yes | Medium (references, not an exact first frame) | **No:** each video can use "a significant portion or all" of the monthly AI limit, and that limit also feeds the keyframe image generation | Free in the plan | **Free pilot engine** from 16 Dec, 1-2 tests a month. Run it only *after* that month's keyframes exist |
| D. Paid image-to-video with first/last-frame control (Kling, Veo 3.1 Fast/Lite, Hailuo, Wan endpoints, Runway) | **Yes** | **Good** when the approved still is frame 1 | **Yes**, and it can be run end to end by the agent through an API | About 0.03-0.14 USD per generated second (vendor figures, verify) | **Chosen for character shots** |
| E. Human animator | Yes, best | Yes | No (cost) | High | Only for a future channel trailer |

### 2.2 The recommended pipeline (Keyframe + I2V hybrid)
1. **Script lock, then a generation-unit list:** about 30 units of 4-5 s each. For every unit: start still, end still (only for big actions), one action, camera note, the edit cuts it feeds.
2. **Keyframes in Canva** (the existing `make-episode-frames` skill): 35-45 full 1080x1920 stills in the approved style, always with the Boy, Uncle and Grandma reference IDs. Put the Boy with the Uncle or a prop, because he fails less often that way. No text inside the art. Reuse the Ep 1 v3 frames where they fit (hook_steam, grab, gag_burn, toot_face, sheepish, spoon_lift, tower_wobble, night_bridge, grandma_fold and others). **The creator approves one contact sheet of keyframes before any money is spent.**
3. **Image-to-video through one API aggregator** (one prepaid key, several engines, pay per clip, run by the agent; the host must be allowlisted and the key saved through the environment's credential form, never in a file). First frame = the approved still. Last frame when the action ends in a different pose. 5 s, 720p, low-to-medium motion, one action per prompt, generated audio off. 2-3 tries per unit, the best one kept.
4. **QC gate per clip (reject if any of these fail):** hat shape and orange chin ribbon; white kimono and orange belt; the Uncle's bald head, thin mustache and kimono soup stains; the round face shape; no extra fingers or limbs; no invented text; no style shift towards a generic anime face.
5. **Anime timing in post (free, local):** optionally step character clips "on twos" (12 fps holds inside a 24 fps edit). This makes AI motion feel more like hand animation and less floaty, and it hides small drift. Test it in the pilot. RIFE only where something needs smoothing. Punch-ins, hit-stops, impact frames, speed lines, sweat drops and sound-word text are added on top.
6. **Local pipeline does the rest:** Kokoro voices, music, SFX, the approved captions, TV graphics (lower-third, intermission, safety cards, seal), the **legend in stepped paper-cut using the existing rig** (the cut-out look *is* paper-cut theatre there), the journal map and route line. Upscale 720p to 1080x1920 (try Real-ESRGAN ncnn on CPU the same way RIFE was installed; fall back to Lanczos).
7. **Lip sync:** anime sync is loose by convention. Generate talking shots with a "speaking to camera" prompt and cut them to the line. If the pilot shows that this is not enough for the host close-ups, test a lip-sync pass on 3 shots before paying for it everywhere.

### 2.3 Share of each method (Episode 1, about 2:00)
| Method | Runtime | Share | Shots it covers |
|---|---|---|---|
| **AI image-to-video from approved keyframes** | about 75 s (about 28-32 units, about 40 edit cuts) | **about 60%** | All acting shots of the Boy, Uncle and Grandma; the host walk; the burn; the safety-segment hands and steam; Dad's silhouette; the bridge; the Grandma freeze; the cold open (from the burn clip) |
| **Local paper-cut rig, stepped 8 fps** | about 25 s | **about 20%** | Caravan on the map, legend (shop, shrinking bun, jelly, paper dragon), route south |
| **Local graphics and inserts** | about 20 s | **about 20%** | Title slam, lower-thirds, intermission, safety and step cards, 10/10 card, fact card, end card, impact frames, torn-page insert |

### 2.4 Cost per episode
- Generated seconds: about 30 units x 5 s x 2.5 tries on average = **about 375 s** per episode.
- At 0.03-0.10 USD per second (cheap to mid engines): **about 12-38 USD per episode. Planning figure: 25 USD.** Kling-class at the top end can reach about 50 USD. The pilot decides which engine.
- Episodes 2-3 of the same arc get cheaper (reused plates and stills, fewer retakes once the prompt patterns are known).
- **Monthly:** 2 episodes a month is about 50 USD (fits the marketing cap); weekly is about 100 USD.
- **Pilot:** about 20 USD of API credit plus the free Canva video quota.
- Everything else stays free (voices, music, captions, graphics, legend, render).

### 2.5 Time per episode (steady state, after Ep 1)
| Step | Agent time | Creator time |
|---|---|---|
| Script and generation-unit list | 2-3 h | 15 min approval |
| Canva keyframes (35-45 stills, with cooldowns) | 4-6 h | 15 min contact-sheet approval |
| I2V generation and QC (parallel API calls) | 3-5 h | none |
| Edit, audio, captions, graphics, legend, 1080 render | 4-6 h | none |
| Review loop | 1-2 h | 20-30 min per round, 1-2 rounds |
| **Total** | **about 2.5-3 working days** | **about 1-1.5 h** |
Episode 1 takes about 1-1.5 weeks because of the new tooling, the pilot and the legend paper-cut build.

### 2.6 Character consistency risk: MEDIUM, managed
- **Where it breaks:** turning away from the camera and back views (hat and ribbon reshape); big full-body action (the rocket, running); fine details (mustache, belt knot, the Uncle's stains); faces drifting to a generic anime face; hands. Expect about 1 clip in 3 to be rejected.
- **Controls:** identity always comes from an approved still, never from text; first frame plus last frame for big actions; 4-5 s maximum; one action per clip; the QC gate in 2.2; the Boy seen from behind only in wide shots; the on-twos stepping hides micro-drift.
- **Fallback per shot:** if a unit fails 3 times, downgrade it to a held keyframe with local FX and a cut. It never blocks the episode.
- **Worst case:** if the pilot shows drift that the creator cannot accept on any engine, the honest alternatives are a part-time human animator for hero shots or a slower release schedule. More rig work is not an alternative.

### 2.7 Pilot gate (decides everything)
- **Scene:** cold open + the burn (script beats 2-5 and 18-25, about 20 s).
- **Versions:** (A) the current rig; (B) I2V on 2 engines through the aggregator; (C) Canva `create-video` once the quota returns on 16 Dec. All share the same audio and captions.
- **Pass** = the creator picks B or C as "a real short anime series" and no shot shows a broken hat, belt or face. Then Episode 1 goes into production on that engine.

---

## 3. Next 5 concrete steps (in order)
1. **Re-cut the script to 2:00 / about 45 beats** (section 1.1 fixes 1-4) and re-sync the director's legend shots to it. Then write the **generation-unit list** (about 30 units) for the whole episode, with the pilot's 20 s first.
2. **Make the pilot keyframes in Canva:** about 8 stills for the cold open and burn, reusing the v3 frames where they fit. Send the creator one contact sheet to approve.
3. **Set up the I2V route:** choose one API aggregator, get the creator's OK on about 20 USD of credit, allowlist its host and save the key through the environment's credential form (never in a file). Generate the pilot on 2 engines and run the QC gate.
4. **Assemble the side-by-side pilot** (rig vs I2V engines, same audio and captions, optional on-twos variant). Add the Canva video version on 16-17 Dec. The creator picks by about 18 Dec. Nothing is posted anywhere.
5. **If it passes:** generate the remaining keyframes and units for Episode 1, build the paper-cut legend with the rig, regenerate Grandma in the picture-book style, test one better Uncle voice, and deliver Ep 1 v4 for approval. Then update `HANDOFF.md`, the `make-episode-frames` and `render-episode` skills, and the launch date (12 or 26 Jan 2027).

## 4. Three questions for the creator (simple wording)
1. **"Which one feels like a real anime show to you: A, B or C?"** (You watch the same 20 seconds made three ways.)
2. **"Can you spend about 25 dollars per episode on AI video? If yes: one episode a week (about 100 dollars a month) or two a month (about 50 dollars a month)?"**
3. **"Is it OK if the main show is AI video made from our approved drawings, while the legend parts stay in a paper-cut puppet style on purpose?"**
