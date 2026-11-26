# Production bible v4.2 (creator decisions, 2026-11-25) — overrides earlier docs where they conflict

## Audience and goal
- For EVERYONE (not a kids' show): every episode must hook any viewer (strong cold open, curiosity gaps, real payoffs). Family-safe.
- Main takeaway per episode: KNOWLEDGE about the food and the place (history, how it's made, how to eat it, what makes the place special). Medium depth: 3-4 real, sourced facts + ONE legend per episode.

## Format
- Length 2:00-2:30, vertical 9:16 (YouTube Shorts).
- More dialogue than v4.1 (about 320-380 spoken words), with clearer messages. Every fact must land clearly (said once, plainly, then a beat to absorb).
- Pace: FLOWING with peaks. Natural travel-show rhythm, scenes breathe; fast cutting, impact frames and big camera only at peak moments (Avatar-like). Not fast all the time.
- On-screen text: MINIMAL. Captions (approved style) + episode title + place name + at most 1-2 fact cards. No TV-graphics clutter (no lower-third gags, no sign gags unless essential).
- History: a SCROLL OPENS on screen (paper/ink scroll unrolling) for the legend/ancient segment, with the Scroll Narrator.
- Recipe: every 3rd episode, as a distinct BREAK from the story ("intermission"-style segment with its own look: kitchen, ingredients, tools, steps), then back to the story. Keep grown-up-step badges, doneness temps (71 C / 160 F pork, 74 C / 165 F chicken), allergy line.
- One LOCAL character per episode who teaches something (a cook, a vendor, a tea master...). Grandma is the Ep 1 local.

## Characters and acting
- Boy (host): WARM and CURIOUS. Genuinely interested, explains clearly, light humor. Natural most of the time.
- Uncle: FUNNY but also WISE. Mostly the comic one, but sometimes says something true and touching, and knows real things about food.
- Emotions: NATURAL by default. Big reactions are allowed (first bite, main gag, surprising discovery, Dad moment) but always PROPORTIONAL to the moment. No constant mugging.
- Dad: sepia silhouette from behind only. Ending line "Dad was right...".

## Look (CHANGED by the creator)
- Creator feedback on the first look test: the Uncle looks good; the Boy must be YOUNGER and SMALLER (about 7, reaching the Uncle's belt, round soft child face, big curious eyes).
- COSTUMES CHANGED (creator, 2026-11-25): no white kimonos, nothing that looks like a karate uniform. Rural East Asian village clothes of old times, muted earthy natural fabrics. Boy: conical leaf hat with orange chin ribbon (kept), loose faded indigo cotton tunic with side buttons, light hemp trousers rolled to the shin, soft orange cloth sash, straw sandals, small cloth bag. Uncle: loose earth-brown linen work jacket with cloth knot buttons, wide dark trousers, wide orange cloth sash, straw sandals, towel over one shoulder. The orange sash stays as the shared family color.
- "Refined anime": same characters and outfits (Boy: Vietnamese conical leaf hat with orange chin ribbon, white kimono, orange belt; Uncle: big, bald, thin mustache, white kimono, wide orange belt), but LESS childish: more natural proportions, cinematic lighting, rich painted backgrounds (in the spirit of Avatar / Ghibli-quality TV anime, never copying any design).

## Sound
- Music: MINIMAL. Mostly ambience and SFX; music only under key moments.
- Voices: the best FREE, secure, commercially licensed open-source TTS available (replace current Kokoro voices if a clearly better one exists).

## Updates (creator, 2026-11-25, later)
- Catchphrase is now **"For dumpling research!"** (was "For science!"); the whispered callback is "For dumpling research."
- Drawing style: DELICATE, soft anime, but OUR OWN look, not fully Ghibli. Gentle clean line art, soft painterly shading, warm muted palette with the orange sash as the accent, slightly storybook texture. Avoid imitating any studio's signature look.
- Characters (approved look test 3, village clothes): see production/v4/ep01-stills-ids.txt and gpu-results/look-test-3.
- SERIES INTRO (every episode): about 8 s of fast frames of dumpling experiences, independent of the episode story: strong hook of both eating dumplings -> both enjoying themselves in a giant pool of dumplings -> both running through a city, fleeing a giant round dumpling with a big chomping mouth that chases them (original design, not any game character). Then the show title. See production/v4/series-intro.md.
- BOTH FORMATS from now on (creator, 2026-11-25): every episode and the series intro are delivered as a VERTICAL 9:16 version (1080x1920, Shorts) AND a HORIZONTAL 16:9 version (1920x1080, regular YouTube). Every still and AI clip is generated in both orientations (same seed, same refs, composition re-framed for each), not cropped from one to the other. Captions, cards and titles have a layout per orientation. Length is the same in both.
- Creator corrections (2026-11-25, evening): the UNCLE must be FATTER (big round belly, heavy round body, chubby cheeks; still warm and dignified, and the jokes are never about his weight). In the intro chase both look truly SCARED (wide eyes, open mouths, panic), not calm. The giant dumpling must read instantly as a DUMPLING: classic pleated top, white soft skin, fully visible in frame, steam rising, a big chomping mouth. New intro cut: a hand throwing gyoza like shuriken (spinning, motion trails).
- DEFAULT DECISIONS taken while the creator was away (2026-11-25 18:35 UTC; creator may override): drawing style = option 1 "soft watercolor anime" (gpu-results/style-options-002, S1): closest to the request "delicate anime, our own, not Ghibli". Voice engine = Qwen3-TTS 1.7B VoiceDesign (Apache-2.0): clearest separation of the characters (child, big man, older woman, deep narrator). Uncle = the fatter version of gpu-results/intro-v3.

## v4.4 DIRECTIVES (creator, 2026-11-25 ~19:40 UTC) — highest priority, override anything above
1. FULL-MOTION ANIMATION, not stills with camera moves. Every shot of the episode and intro is moving animation (AI video), continuous and fluid. Generate as many keyframes as needed (start/end and in-between stills) and use image-to-video models with first+last frame conditioning, interpolation and character-motion tools so motion flows across cuts. Stills with Ken Burns are only an emergency fallback.
2. The UNCLE is FAT and COMICALLY RIDICULOUS (over-the-top anime comedy reactions, big physical gags). Never mock his weight in dialogue; the comedy is his behavior.
3. SERIES INTRO in the style of an anime TV opening, with an ORIGINAL SONG about dumplings sung in JAPANESE, Asian punk style (fast, energetic, guitars, drums, shouted hooks). Burned-in English translation of the lyrics is optional and small. Original lyrics and music only (open-source music model with commercial license).
4. VIBE: learning + lightness with LOTS of laughs and wit, for adults as much as kids. Less innocent/sweet, more like the comedy and energy adults love in Dragon Ball Z, Naruto, One Piece (exaggerated reactions, comic timing, banter, food-as-power-up hype, chibi/sweat-drop beats, deadpan vs. manic) and like the smart, fun learning content people love online. Never copy anything from those shows.
5. CAPTIONS must never cover important elements (faces, hands, the dumpling, key action): position per shot in a safe area.
6. Animate as many FACIAL EXPRESSIONS and body movements as possible; constant visual interest, no static moments.
7. Use as many tools and agents as needed to reach the best possible continuous first version.
8. Work autonomously to completion based on everything the creator said so far.
- UNCLE REFERENCE LOCKED (creator): use the Uncle exactly as in the corrected intro stills, variant 2 (gpu-results/intro-v3/dumpling_out/images/*__v2.png, e.g. I1_bite__v2, I3_pool__v2, I5_chase__v2, I6_chomp__v2). Do NOT redesign or regenerate a new Uncle model; use these images as the Uncle reference for every new still.
- GPU BUDGET RULES (Kaggle free tier ~30 GPU h/week, 2 sessions): (1) distilled / few-step video models by default (e.g. LTX distilled, 8-12 steps), full models only for 4-6 hero shots; (2) 1 variant per clip, a 2nd only after a failed QC; (3) generate at the model's native low resolution and upscale + RIFE-interpolate on CPU (GitHub Actions runners / this container), not on the GPU; (4) portrait first for every shot; landscape clips are generated only for shots whose composition cannot be re-framed from the portrait clip with extended/outpainted backgrounds; (5) batch many clips per Kaggle session (model load once); (6) every job logs GPU minutes to production/v4/gpu-ledger.md; stop and re-plan at 22 h used in a week. Overflow option (needs a creator sign-up later, only if truly necessary): a second free provider with API automation (e.g. Modal monthly free credits).

## FORMAT CHANGE: ~1-MINUTE EPISODES (creator, 2026-11-26) — overrides every earlier length rule
- Episode length target **1:00, hard max 1:15** (vertical Short first; a 16:9 version of the same cut). The old 2:30-2:50 cut of Episode 1 stays only as an "extended cut" reference.
- **No separate 8-11 s opening.** Hook first (0-3 s, the funniest or most surprising image), then a title hit of <= 2 s using the 3-s sting of the Japanese song; the full opening song is kept for 3-episode compilations (16:9, about 3 min) and promos.
- Structure (60 s): hook 0-3 s | host + place 3-10 s | one learning beat (1-2 facts, said once, plainly) 10-25 s | central gag / lesson 25-42 s | legend in ONE short scroll beat (<= 8 s, optional on non-legend episodes) | heart beat with Dad (<= 6 s, every episode or alternating) | next-episode hook + "Dad was right..." 52-60 s.
- About **150-170 spoken words**, roughly **20-26 AI clips** of 2-3 s, max 2 faces per clip (shot-rules). Fewer clips means fewer GPU hours and fewer defects.
- Recipe break every 3rd episode: a 20-25 s "recipe in 20 seconds" segment inside the minute, or its own 60-s recipe Short.
- Series planning: counts and arcs are re-planned for 1-minute episodes (more episodes per arc is fine, a weekly cadence becomes 2 per week feasible).
