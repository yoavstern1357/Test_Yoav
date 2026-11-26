# Character redesign plan (art direction and character design)

Written: 2026-11-26 · Role: art director and character designer · Status: **PLAN ONLY, waiting for creator approval (Gate 0)**. No GPU job was run and no image was generated for this plan.
Read with: `production/v4/PRODUCTION-BIBLE.md` (all creator decisions), `production/v4/fix-plan.md` (Fix 1 sheets, Fix 5 mouths, Fix 8 LoRAs), `production/v4/quality-research.md` (rubric C1-C7, G2), `production/v4/director-treatment.md` (acting notes, Camel, Grandma beats).

**What is fixed by the creator and is NOT up for redesign:** Boy about 7, conical leaf hat with orange chin ribbon, village clothes (faded indigo tunic, rolled hemp trousers, orange sash, straw sandals). Uncle fat, bald, thin mustache, comically ridiculous, earth-brown linen jacket, dark trousers, wide orange sash, towel; the intro-v3 variant-2 Uncle "looks good" and is the anchor. Grandma = the old master. Dad = sepia silhouette from behind only. Style = delicate soft anime, our own look, not Ghibli, no studio imitation. Orange sash = shared family accent, adults included. No kimono, nothing karate-like. Jokes on the Uncle's behavior only, never his weight, never on a people or place.

**What the redesign changes:** construction, proportions, shape language, values, the number of small details, signature props and the expression and pose system, so that the same family reads instantly on a phone and stays identical across hundreds of AI frames.

---

## 0. Summary (one screen)

1. **The current cast is likeable but not yet "designed".** All three leads are built from the same soft round shapes and mid values, the Boy and the Uncle are drawn in two different face systems (anime child vs. semi-realistic caricature), Grandma is generic (she is the character the model duplicates and morphs most: C11, C21), and many identity details are tiny and drift even in the approved images (the Boy's chin ribbon is missing in intro-v3 I1 and I5, his sandals turn into shoes in C11/C16, the Uncle's jacket changes from olive to tan).
2. **Pro fix = the classic trio of shapes plus one family construction kit:** Boy = **triangle** (Dad's oversized hat) on a small bean; Uncle = **circle/egg** with a white vertical towel and a horizontal orange band; Grandma = **square block** with a small triangle crown (bun and two pins). One shared eye, brow, nose, mouth and line system so they are one family in one frame.
3. **"Simple enough to draw 1000 times" = simple enough for the AI 1000 times:** each lead gets at most 7 locked features, each big enough to survive at phone size (at least about 3% of the character's height); everything smaller is either removed or declared free (allowed to vary).
4. **Three directions per character** (A = refine the current look, B = bold shape-language redesign, C = cinematic, more naturalistic and detailed). **Recommendation: B for all three leads, with the Uncle changing the least** (same body, jacket, towel, sash; only a fully bald dome, a thin curled mustache per the written rule, and a face rebuilt on the family kit). Supporting cast: B for the guest-teacher kit, the Camel and the Giant Dumpling.
5. **Process: 4 creator gates, about 12-14 GPU-h in total over about 2 weeks**, of which only about 1.2 GPU-h comes before the creator chooses a direction. The LoRA step replaces fix-plan Fix 8 (same budget line), so the redesign adds only about 4-5 GPU-h to the plan. Keyframe stills for Ep 1 should wait for Gate 3 so we don't make them twice.

---

## 1. Audit of the current designs

Looked at: intro-v3 `I1_bite__v2`, `I3_pool__v2`, `I5_chase__v2`, `I6_chomp__v2` (the locked Uncle), look-test-3 (4 variants), style-options-002 (8 images), the ep01v44-stills and stills-fix contact sheets, and full-size ep01v44 `C11`, `C12`, `C16`, `C37`. Colors were sampled from the images (15x15 px median patches) where stated.

### 1.1 Scorecard (1 = weak, 5 = pro)

| Principle | Boy | Uncle | Grandma | Evidence |
|---|---|---|---|---|
| **Silhouette test** (black fill, still nameable?) | 4 | 4 | 2 | Boy: the cone hat is the strongest shape in the show. Uncle: egg body + towel strip reads. Grandma: only a small bun; filled black she is "an old person". |
| **Shape language** (does the shape say the personality? are the three different?) | 3 | 4 | 2 | All three are built from soft circles: Boy round face + round body, Uncle round, Grandma round. No contrast between them; the triangle of the hat is the only non-round shape in the cast. |
| **Color and value** (own value block, separates from backgrounds) | 3 | 3 | 1 | Boy's "indigo" renders grey (`#72777F`-`#7D7D83` in I1). Uncle's jacket vs. the light wood wall in C16: luma 196 vs 193 (no separation). Grandma's sage jacket luma 190 on a luma 224 wall, plus a near-white apron: she washes out in every bright interior. |
| **Readability at phone size** (full body at about 10% of screen height) | 3 | 4 | 2 | Hat and Uncle's belly survive; the Boy's 1-2 mm chin ribbon, button rows, pocket and bag strap do not; Grandma has nothing that survives except the bun. |
| **Expression range** (designed for gags and for quiet moments) | 3 | 2 | 2 | Boy: good anime eyes, but no signature gesture. Uncle: small realistic eyes and heavy jowls look great in neutral but limit anime gag faces (v4.4 directive: comically ridiculous); his brows and mustache are not used as acting tools. Grandma: one kind smile. |
| **Simplicity for AI consistency** (few, big locked features) | 2 | 3 | 2 | Drift seen in approved or shipped stills: Boy's chin ribbon missing (I1, I5), sandals turn into closed shoes (C11, C16), breast pocket comes and goes (I5/I6 vs I1), bag on/off; Uncle side-hair fringe appears and disappears, mustache thickness and jacket hue (olive to tan) change, knot-button count varies; Grandma is duplicated or merged in C11, C21 and C32. |
| **Simplicity for animation** (few moving parts, designed secondary motion) | 3 | 4 | 3 | Good secondary-motion parts already exist (ribbon tails, sash tails, towel). Bad parts: crossing bag strap and button rows flicker in video (they appear and vanish between frames). |
| **Props that carry personality** | 2 | 2 | 1 | Boy: a bag (no story). Uncle: chopsticks, but not a fixed prop. Grandma: none. The story already has the best props unused: **Dad's hat** (Grandma recognizes it in the cliffhanger) and **Dad's journal**. |
| **One family** (same construction) | 2 (cast-wide) | | | The Boy is drawn as an anime child, the Uncle as a semi-realistic caricature, Grandma as a picture-book granny: three face systems in one frame. |

### 1.2 What to keep (equity the audience will recognize)
- The cone hat with orange ribbon; the faded indigo top and light trousers (dark top / light bottom value split); the orange sash on everyone.
- The Uncle's whole body language from intro-v3 v2: egg body, big belly, dark trousers, earth-brown jacket with knot buttons, white towel on his left shoulder, wide orange sash with long tails. The creator likes him: change his face system only as far as the family needs it.
- Grandma's bun, apron and calm.
- The warm palette (`#ECC66A`, `#FFFAF0`, `#D9480F`, `#FFE3B8`, line `#3B2A1A`).

### 1.3 What to fix (cast-wide)
1. **Give each lead a different primary shape** (triangle / circle / square) so the trio reads as three different people even as black shapes.
2. **One family construction kit** (section 3.0): same eye construction, same line weights, same nose and ear shorthand, same shadow logic for all humans. The Uncle keeps his heavier jaw and smaller eyes *inside* that kit.
3. **Value blocks:** each lead owns a different value pattern (Boy dark top/light bottom, Uncle mid top/near-black bottom with a white stripe, Grandma dark top/long white apron), and background plates keep at least 25 luma steps (of 255) between a character's main mass and the area right behind it.
4. **Character rendering vs. background rendering:** characters cleaner (flat cel color + one soft shadow tone + soft blush), backgrounds watercolor-painterly. Today the watercolor texture is applied to the characters too, which costs figure-ground separation and invites drift. This is still "delicate soft anime" and is what TV production does (cel characters on painted plates).
5. **Lock list / free list / banned list per character** (section 3), so prompts, QC (rubric C4) and LoRA captions all name the same things.
6. **Supporting cast:** make Grandma a real "master" design, make the Giant Dumpling read as a dumpling first and a monster second, and fix the Camel's species and silhouette.
7. **Documents:** `production/character-bible.md` is stale (10-year-old boy, white kimono, "For science!"). After Gate 3 it is replaced by the new sheets and prompt blocks.

---

## 2. Research: how professionals build characters that read (and stay on model)

The fetch tool could not open pages in this session (huggingface.co does not resolve here), so the claims below come from search-result summaries, the same way as in `quality-research.md`. Labels: [Primary] = studio or vendor documentation, [Reported] = press or established blogs, [Community] = tutorials and forums.

| # | Principle | What professionals do | What it means for us | Sources |
|---|---|---|---|---|
| R1 | **Model sheets (settei) keep many hands on model** | The character designer produces sheets per character (turnarounds, expressions, poses, color sheet); animation directors (sakkan) correct drawings back to the sheet, and a chief animation director keeps the whole series uniform. The designer also "ties down" extreme storyboard poses so they stay on model while keeping their energy. | In our pipeline the AI is the "many hands" and the QC gate plus a human contact-sheet pass are the sakkan. Sheets must exist before any episode stills, and we need a gag-pose sheet so extreme poses are designed, not improvised by the model. | [Reported] https://blog.sakugabooru.com/2017/07/21/the-pre-production-of-anime-3-design-work/ · https://en.wikipedia.org/wiki/Model_sheet · https://jojowiki.com/Model_Sheet_Archive · [Community] https://www.clipstudio.net/how-to-draw/archives/164740 |
| R2 | **Silhouette test** | Black out the character; if a stranger can still name it, the design works. Hair, hats and props that break the outline are the usual anchors; they also keep the character recognizable when the body changes. | Hat (Boy), towel + egg (Uncle) and bun + pins (Grandma) must each break the outline. Our gate measures it automatically (section 5.3). | [Community] https://www.creativebloq.com/art/character-design/how-to-design-instantly-recognisable-characters-using-strong-silhouettes · https://fandomwire.com/10-most-iconic-anime-designs-everyone-can-recognize-ranked/ · https://fiveable.me/2d-animation/unit-13/creating-character-silhouettes-shapes/study-guide/1oo2tSb8S1byAuIV |
| R3 | **Shape language** | Circle = friendly, soft; square = stable, trustworthy, solid; triangle = dynamic, energetic, curious or dangerous. Combinations: circle + triangle = happy and energetic; circle + square = gentle and trustworthy. A Disney teaching guide: "circles and ovals are great to use for friendly faces". | Boy = triangle over circle (curious traveler, warm); Uncle = circle (warm, comic, soft); Grandma = square with a small triangle on top (immovable master with a sharp mind). | [Primary] https://waltdisney.org/sites/default/files/2020-04/T&T_ShapeLang_v9.pdf · [Community] https://binus.ac.id/bandung/dkv/2025/11/04/character-design-101-turning-simple-shapes-into-personality/ · https://3dsense.net/blogs/shape-language-in-character-design-communicating-through-geometry · https://www.creativebloq.com/art/digital-art/how-shape-can-make-or-break-your-character-art |
| R4 | **Readability = silhouette + value first, hue second** | Valve designed every Team Fortress 2 character for a unique silhouette (proportions, props, outline) and used value hierarchy (darker lower bodies, lighter torsos) for readability; Valve lists "Readability" with gameplay and branding as reasons for the style. Color guides: check designs in grayscale and at the smallest display size; a few colors with strong light-dark contrast read better at any size than many mid-tones; 2-3 main colors + 1 accent. | Each lead gets 3 main colors + the shared orange, and a value pattern that differs from the other two (section 1.3.3). Every concept is shown to the creator also as a black silhouette, in grayscale and at 64 px tall. | [Primary] https://www.advances.realtimerendering.com/s2007/Mitchell-IllustrativeRenderingInTF2(Siggraph07%20Course%20Notes).pdf · https://cdn.fastly.steamstatic.com/apps/valve/2008/GDC2008_StylizationWithAPurpose_TF2.pdf · [Community] https://medium.com/@xavierck/character-readability-in-team-fortress-2-and-overwatch-68c41d454465 · https://nerdbot.com/2026/09/25/character-design-for-small-images/ |
| R5 | **Simple enough to draw 1000 times** | Animation designs are stripped to essential elements because they are drawn hundreds or thousands of times; detail like every ruffle would overwhelm animators. Limited (TV) animation reduces detail and uses modular parts. Simplicity is selective: keep a few deliberate details that make the simple form believable. | For AI this is literal: every small detail is a coin flip per frame. Lock at most 7 big features; remove pockets, button rows, crossing straps; keep one or two deliberate textures (hat weave, linen slub) as free details. | [Reported] https://www.awn.com/animationworld/how-draw-animation-simplifying-characters-animation · https://creativebloq.com/how-to/simplfy-figures-for-animation · https://studio.blender.org/blog/sprite-fright-the-illusion-of-simplicity · [Community] https://fiveable.me/2d-animation/unit-13/designing-animation-styles/study-guide/OP4ZkG6BIHaEoteX |
| R6 | **AI identity: few colors, readable silhouette, 1-3 signature features, one frozen description** | AI-practice guides converge: a design with about three main colors, a readable silhouette and one or two distinctive features that appear in every reference beats a fully detailed layered design; freeze one description and paste it word for word; watch for accessories (glasses, jewelry, facial hair) appearing or vanishing, which is the typical drift. | Our lock list = the frozen description. Glasses, earrings, patterns, pockets are banned for the leads. The Uncle's mustache must be big enough not to vanish. | [Vendor/Community] https://www.vidu.com/blog/character-design-ai-video · https://www.ssw.com.au/rules/consistent-ai-generated-characters · https://runwayml.com/resources/create-consistent-ai-characters · https://kling.ai/blog/ai-character-consistency-guide |
| R7 | **Proportions (heads tall)** | Realistic adult about 7 heads, anime adults about 6.5-8; children and "cute" characters lower (sources cite 3-6 heads depending on stylization); chibi about 2-3 heads. | 7-year-old Boy: 4.0-5.0 heads depending on direction. Uncle 5.25-6.5. Grandma 4.25-5.5. Chibi gag versions 2.5 heads for all. | [Community] https://ogiuemaniax.com/2012/07/10/anime-and-idealized-figures/ · https://animeartacademy.artstation.com/projects/qeLrNN · https://www.justcolor.net/?p=9953 |
| R8 | **Designed off-model** | Deliberate off-model drawing (chibi, sweat drops, huge mouths) is a comedy tool for big emotion, used on purpose; critics of AI anime noted that anime characters are not meant to look exactly the same all the time: acting deformation is designed, identity stays fixed. | A gag sheet per lead (chibi, shock, collapse, triumph) with the lock list surviving inside the gag (hat, sash, towel, mustache, bun). Only scripted gag beats use it (rubric C7). | [Reported] https://en.wikipedia.org/wiki/Off-model · https://www.animenewsnetwork.com:443/feature/2023-03-15/no-you-cant-make-anime-with-ai/.195921 |
| R9 | **Character LoRA datasets** | Practitioners: 15-30 curated images beat 50 mediocre ones; cover angles (front, 3/4, profile, back), expressions, zoom levels and backgrounds; face-only data does not lock body proportions; caption what varies. FLUX.2 klein: BFL documents training on the Base models, 12 GB VRAM + 32 GB RAM for klein 4B Base; AI-Toolkit is the listed community trainer; learning rate sensitivity (keep 1e-4 to 5e-4). | Our dataset comes from the approved sheets (section 4) plus 8-10 in-scene images per character on varied backgrounds. Train on klein 4B Base, test the LoRA on the distilled 4-step model we actually use (transfer is not guaranteed: test first). | [Primary] https://docs.bfl.ai/flux_2/flux2_klein_training · https://huggingface.co/blog/black-forest-labs/flux-2-klein-lora · [Vendor/Community] https://developer.civitai.com/orchestration/recipes/training-flux2-klein · https://www.runcomfy.com/trainer/ai-toolkit/flux-2-klein-16gb-vram-training · https://rishidesai.github.io/posts/character-lora · https://dev.to/qcrao/5-lora-training-pitfalls-when-youre-trying-to-lock-down-a-comic-character-43bl |
| R10 | **Short-form (phone) specifics** | Small differences are hard to perceive on mobile: exaggerate what matters, big shapes first; test readability at small sizes before shading; vertical frames favor simple backgrounds. | Concept boards include a 64 px and 32 px test strip; the leads' signature features are sized for that (hat brim, towel, bun, belly), and the faces get big eyes and brows because the face carries the acting in vertical close-ups. | [Community] https://www.creativebloq.com/art/character-design/how-to-design-instantly-recognisable-characters-using-strong-silhouettes · https://cursa.app/en/page/vertical-first-thinking-for-mobile-audiences · https://nerdbot.com/2026/09/25/character-design-for-small-images/ |

**Not claimed:** I found no primary source for a fixed "number of details" limit in TV anime; the "7 locked features" rule below is our own working limit [Assumption], to be checked against QC drift data after Gate 3.

---

## 3. Three design directions per character

### 3.0 Shared rules for every direction

**Family construction kit (all humans):**
- **Line:** warm brown `#3B2A1A`, never black; 2 weights: outer contour 1.5x the inner lines; hair and clothing folds with few lines (max 3 fold lines per garment panel).
- **Eyes:** vertical oval irises in dark warm brown `#3A2618`, one large white highlight upper-left + one small lower-right; thick upper lid line (2x line weight), lower lid only hinted. Size scales by character (Boy largest, Uncle smallest), construction identical.
- **Brows:** solid shapes (not hair strokes), separated from the eyes by a clear gap: they are the main acting tool.
- **Nose:** a small shadow-side hook; **ears:** simple C shape; **mouth:** single line at rest; open mouths follow the mouth chart (section 4).
- **Shading:** flat base + one shadow tone + soft blush gradient on cheeks; one rim light allowed in key-lit scenes. No painted texture on characters (texture lives in backgrounds).
- **Orange:** sash orange is the same on everyone: base `#E07038`, shadow `#B4511F`, brand dark `#D9480F` for small items (ribbon, cords). (Soft rendering lightens `#D9480F`; these values are what the frame should actually show, for rubric G2.)
- **Banned on all leads:** glasses, jewelry, patterns or prints, logos, text, pockets, belts other than the sash, crossing straps, shoes with laces, Japanese martial-arts garments (gi, hakama, kimono).

**Size chart (all directions; Uncle's head top = 1.00):** Uncle's sash line 0.58 · Boy's head top (without hat) at 0.58, i.e. at the Uncle's belt as the creator asked; hat tip about 0.68 · Grandma head top 0.70, bun top 0.78 · Dad (silhouette) head top 1.00 (as tall as the Uncle, slim) · Camel hump top 1.10 · Giant Dumpling 2.5-3.0.

**Directions:**
- **A, "Refine":** today's characters, cleaned and locked. Lowest risk, least pop.
- **B, "Bold shapes":** triangle / circle / square trio, oversized signature features, minimum small details, gag-ready faces. Best for phone readability and AI identity.
- **C, "Cinematic":** taller, more naturalistic proportions, more texture and costume detail, comedy from acting rather than deformation. Most "prestige" in a still, hardest to keep consistent.

The three directions per character are built from the same kit so the creator may pick per character, with one rule: **B and C proportions do not mix in one cast** (a 4-head B Boy next to a 6.5-head C Uncle looks like two shows). A works with either.

The **12-expression list** and the **idle/walk/run** set belong to the character, not the direction; they are given once per character, with per-direction notes in the direction table.

---

### 3.1 The Boy (host, about 7, warm and curious; deadpan comedy, eyes-closed smile reserved for Dad moments)

| | **A. Village boy, refined** | **B. "Dad's hat" (RECOMMENDED)** | **C. Little traveler, cinematic** |
|---|---|---|---|
| Idea | Today's Boy, younger and locked | The hat is Dad's and one size too big for him: the cone becomes the show's logo shape, and the story (Grandma: "That hat!") is in the design | A naturalistic 7-year-old for prestige close-ups |
| Silhouette | Medium cone on a slim kid | **Wide flat-ish cone (brim about 2.0x his shoulder width) sitting low on his brows, on a small bean body; two long ribbon tails** | Proportionate cone (1.5x shoulders), layered clothes |
| Heads tall | 4.75 (hat +0.5) | **4.0 (hat +0.6)** | 5.0 (hat +0.5) |
| Face | Round, soft; current anime face | **Round face, full cheeks, small chin; largest eyes of the cast (eye height about 1/5 of head height), set low on the face (child placement)** | Softer oval face, smaller eyes (1/7 of head height), more defined nose |
| Eyes / brows / mouth | Current | **Big oval eyes, short thick rounded brows (hidden under the brim at rest: when they appear it reads as surprise), small mouth, one tooth gap allowed as a free detail** | Natural eyes with lashes, thin brows, lips indicated |
| Hair / hat | Short black hair, cone with thin orange string | **Blue-black hair `#1D1F2B` showing only as 3-4 soft spikes below the brim and over the ears; pale straw cone with 6 visible radial ribs (no weave pattern), WIDE orange cloth chin ribbon (about 1/3 of face width) tied under the chin, two tails hanging to the chest** | Hair with strand detail, cone with visible weave and a frayed edge, ribbon with knot detail |
| Outfit, materials, wear | Indigo tunic with side buttons and pocket, hemp trousers, sash, sandals, canvas bag on a strap | **Faded indigo cotton tunic, short, loose, diagonal side opening with 2 cloth knot buttons (no pocket), sleeves a little long (pushed up); wide orange sash knotted at his left hip; Dad's journal in a small cream cloth pouch tucked into the sash (no strap); light hemp trousers rolled to mid-shin; flat straw sandals. Wear: faded elbows, one darker patch on the right knee (free detail)** | Indigo tunic over a cream undershirt collar, mended seams, rolled hemp trousers with drawstring, straw sandals with cords, cloth bag on a strap, journal visible |
| Palette (hex) | tunic `#5B6E8F`, trousers `#CFC2A6`, hat `#E2C27E`, skin `#F6D6B8` | **hat `#E9C46A` / shadow `#C49E48`; tunic `#3E5C8C` / `#2C4268`; trousers `#D9CDB2` / `#B5A788`; skin `#F7D9BC` / `#E6B48F`; blush `#F2A58E`; hair `#1D1F2B`; pouch `#EFE6D0`; sandals `#C29A5B`; orange per kit** | tunic `#4A6088`, undershirt `#EDE5D3`, trousers `#CDBF9F`, hat `#DDBB78` |
| Signature prop / pose | Bag, chopsticks | **Dad's journal (leather `#7A4B2A`, orange bookmark ribbon); signature gesture: pushes the brim up with one finger when something interests him (the brim reveal = his "eyes open" beat); run: one hand holding the hat on** | Journal held open, pencil behind the ear |
| AI / animation risk | Low risk, low pop; thin ribbon will keep vanishing | **Lowest drift: 6 locked features, all large. Risk: oversized hat hides the eyes in high angles; rule: camera at or below his eye line for talk shots** | Highest drift (layers, strap, weave, cords) |
| Lock list (B) | | **1 oversized pale-straw cone, 2 wide orange chin ribbon with two tails, 3 faded indigo tunic with diagonal opening, 4 wide orange sash knotted at left hip + cream pouch, 5 light hemp trousers rolled mid-shin, 6 straw sandals** | |
| Free / banned (B) | | Free: knee patch, tooth gap, hair spike count. Banned: pocket, bag strap, shoes, visible buttons rows, any second hat | |

**Prompt core, B (frozen text):**
```
the Boy: a small 7-year-old boy, 4 heads tall, round soft face with full cheeks, very big dark-brown oval eyes,
short blue-black hair showing only as a few soft spikes under the brim, wearing an oversized pale-straw conical
leaf hat that is too big for him (brim twice as wide as his shoulders, sitting low on his eyebrows) tied with a
wide orange cloth chin ribbon with two long tails, a short loose faded indigo cotton tunic with a diagonal side
opening and two cloth knot buttons, a wide orange cloth sash knotted at his left hip with a small cream cloth
pouch tucked into it, light hemp trousers rolled to mid-shin, flat straw sandals
```
Prompt core A: `a small 7-year-old boy, 4.75 heads tall, round face, big dark eyes, short black hair, conical leaf hat with an orange chin ribbon, faded indigo tunic with side buttons, light hemp trousers rolled to the shin, orange cloth sash, straw sandals` · Prompt core C: `a 7-year-old boy with natural child proportions, 5 heads tall, soft oval face, natural dark eyes, black hair with fine strands, a woven straw conical hat with frayed edge and knotted orange ribbon, faded indigo tunic over a cream undershirt with mended seams, rolled hemp drawstring trousers, corded straw sandals, cloth shoulder bag`

**12 expressions (Boy):** 1 curious-neutral (default; brows hidden by the brim) · 2 warm smile · 3 eyes-closed smile (Dad moments only) · 4 wonder (sparkle highlights, small "o" mouth, brim pushed up) · 5 deadpan (flat upper lids, straight mouth: his comedy) · 6 explaining (one brow up, half smile, open palm) · 7 surprised (brows pop above the brim) · 8 tasting bliss (eyes closed, cheeks puffed, blush) · 9 worried (brows up-in, small mouth) · 10 missing Dad (eyes down, brim shadow over the eyes) · 11 scared (intro chase: eyes wide with small pupils, open mouth, sweat drops) · 12 determined (brows down, firm mouth, pulls the ribbon tight).
In A the brows are always visible (less "brim reveal"); in C the range is subtler (no sparkle eyes, no sweat drops except chase).

**Idle / walk / run (Boy):** idle = weight on one leg, both hands on the journal pouch, ribbon tails drift, blink every 3-4 s · walk = even 8-frame cycle, short steps, hat bobs one beat behind the head, ribbon tails trail · run = 6-frame cycle, 15-degree forward lean, one hand holding the hat brim on, tails horizontal; chibi gag version 2.5 heads keeps hat, ribbon, sash.

---

### 3.2 The Uncle (big, fat, bald, comically ridiculous but sometimes wise; "For dumpling research!")

The creator locked the intro-v3 variant-2 Uncle. **All three directions keep his body, jacket, trousers, sash and towel.** They differ only in head construction and how far the face can act.

| | **A. Locked v2, cleaned** | **B. v2 body, gag-ready face (RECOMMENDED)** | **C. Cinematic Uncle** |
|---|---|---|---|
| Idea | Exactly the approved Uncle, with drift removed | Same Uncle the creator liked; the face joins the family kit so he can do big anime comedy faces and still be him | A heavier, more naturalistic big man; comedy from timing and acting |
| Silhouette | Egg body, slightly balding head with dark side fringe, towel | **Egg body + a perfectly round bald dome (pure circle on an egg), towel as a white vertical stripe on his left shoulder, wide orange band with long tails** | Taller pear shape, stubble, more realistic weight |
| Heads tall | 6.0 (as now) | **5.25 (head slightly bigger than v2, so faces read in wides)** | 6.5 |
| Face | Semi-realistic: small eyes, heavy jowls, big nose | **Round face with double chin and apple cheeks; small kind eyes (1/8 of head height) on the family construction; thick, very mobile black brows (his acting tool); button nose; mouth that can open huge** | Realistic jowls, nasolabial folds, stubble shading, detailed ears |
| Mustache | Thick black bristle mustache | **Thin but long black mustache whose tips curl up past the cheek outline (visible in silhouette). It acts: curls up = delight, droops = humbled, bristles straight = shock, flutters = sneeze/steam.** (Matches the written rule "thin mustache"; Gate 1 shows it side by side with the v2 thick mustache so the creator chooses.) | Full natural mustache, grey hairs |
| Head | Bald top, dark hair fringe at the sides | **Fully bald, shiny, one fixed comma-shaped highlight `#FFF6E8` (it can "ping" in gags); no fringe** | Bald with short grey sides |
| Outfit, materials, wear | As v2 | **Loose earth-brown linen work jacket, mandarin collar, exactly 3 cloth knot buttons, sleeves pushed to the elbow; wide orange cloth sash tied in front with two long tails; wide charcoal trousers; straw sandals; white cotton towel on his LEFT shoulder (viewer's right) always. Wear: two small sauce dots on the jacket front (free detail)** | Same garments with visible linen slub, sweat marks, frayed towel, worn sandals |
| Palette (hex) | jacket as rendered (`#AA815B`-`#BC905E`), trousers `#484243` | **jacket `#9C7148` / shadow `#74512F` (one value step darker than v2 so it separates from light wood); trousers `#2E2C31`; towel `#F6F1E6` / `#D9D2C2`; skin `#F0C6A0` / `#DDA27C`; cheeks `#E58F78`; brows and mustache `#221A16`; head highlight `#FFF6E8`; orange per kit** | jacket `#8E6A45` with texture, trousers `#33302E` |
| Signature prop / pose | Chopsticks sometimes | **His personal "research chopsticks": long lacquered wooden chopsticks `#6B3A22` with a tiny orange cord, tucked upright in the sash at his right hip, drawn with a flourish before every bite; signature pose: chopsticks raised like a trophy, chest out, brows up, mustache curled ("For dumpling research!")** | Chopsticks in hand |
| AI / animation risk | Low; side fringe and mustache thickness keep drifting; limited gag range | **Low: big locked features; the thin mustache must be at least 1/3 of face width with visible curled tips or it will vanish at phone size (Gate 1 checks it at 64 px)** | Medium-high: stubble, texture and realism fight the soft style, smears more in video |
| Lock list (B) | | **1 fully bald round head with one highlight, 2 thin long curled-tip black mustache + thick brows, 3 earth-brown linen jacket with mandarin collar and 3 knot buttons, 4 wide orange sash with two long tails, 5 white towel on his left shoulder, 6 wide charcoal trousers, 7 straw sandals** | |
| Free / banned (B) | | Free: sauce dots, sleeve roll height, chopsticks in hand or in sash. Banned: hair on the head, hat, apron, closed shoes, vest, anything gi- or kimono-like | |

**Prompt core, B:**
```
the Uncle: a very large, fat, round man, 5.25 heads tall, egg-shaped body with a big round belly, completely bald
shiny round head with one small highlight, thick expressive black eyebrows, a thin long black mustache with tips
curling upward past his cheeks, small kind dark eyes, round rosy cheeks and a double chin, a loose earth-brown linen
work jacket with a mandarin collar and three cloth knot buttons, sleeves pushed to the elbows, a wide orange cloth
sash tied in front with two long tails, wide charcoal trousers, straw sandals, a white towel over his left shoulder,
long wooden chopsticks tucked in the sash
```
Prompt core A: `the Uncle exactly as in the reference: a very large fat man, bald on top with short dark hair at the sides, thick black mustache, earth-brown linen jacket with cloth knot buttons, wide orange sash, dark trousers, straw sandals, white towel over his left shoulder` (+ intro-v3 `I1_bite__v2` as image reference) · Prompt core C: `a very large heavy man with naturalistic proportions, 6.5 heads tall, bald with short grey sides, full natural mustache, light stubble, textured earth-brown linen jacket with knot buttons, wide orange sash, dark trousers, worn straw sandals, frayed white towel over his left shoulder`

**12 expressions (Uncle):** 1 hungry-hopeful (default: nose leads, eyes on the food) · 2 big belly laugh (eyes closed arcs, mouth huge) · 3 "For dumpling research!" heroic (chest out, brows high, mustache curled) · 4 first-bite bliss (eyes closed, happy tears, cheeks glow) · 5 burned tongue (tongue out, steam from the ears, spiral eyes: gag sheet) · 6 humbled (shrinks, brows tilted, mustache droops) · 7 shock (white eyes, jaw drop, mustache bristles straight) · 8 panic (intro chase: tiny pupils, open mouth, sweat drops flying) · 9 sneaky (side-eye, one brow down, hand creeping toward the steamer) · 10 wise and tender (soft eyes, small closed smile: the rare "true" moments, drawn on-model, never gag) · 11 indignant (puffed red cheeks, brows down) · 12 food-coma (half lids, content smile, small drool, hands on belly).
A: 2, 5, 7 and 8 stay semi-realistic (no white eyes, no spiral eyes). C: no off-model gag faces at all.

**Idle / walk / run (Uncle):** idle = slow belly breathing, hands clasped on the belly or rubbing together, nose sniffing toward food, towel and sash tails settle 2 frames late · walk = 10-12-frame waddle with side-to-side sway, belly follow-through 2 frames late (physics, never a weight joke) · run = arms pumping, short fast steps (feet can blur), towel flapping, sash tails horizontal, 4-6-frame anticipation crouch before any dash (director-treatment); chibi version 2.5 heads keeps dome highlight, mustache, towel, sash.

---

### 3.3 Grandma, the old master (tiny, still, precise; her hands do everything; her eyes opening is an event)

| | **A. Kind grandma, refined** | **B. "The master" (RECOMMENDED)** | **C. Tiny legend** |
|---|---|---|---|
| Idea | Today's Grandma, darker jacket and locked | A square, immovable little master; calm half-closed eyes that open only for the big moments (the cliffhanger "That hat!") | A comic, more stylized very small master with a flash of mastery |
| Silhouette | Round grandma with a bun | **Square block: short, wide, low center of gravity; tall round bun with two crossed plain wooden pins (a small triangle crown that rhymes with the Boy's hat); long white apron = a tall rectangle on the dark jacket** | Very small and bent, oversized round spectacles that flash white, walking stick |
| Heads tall | 5.0 | **4.25** | 3.5 (semi-chibi) |
| Face | Round, soft, kind | **Round-square face, strong cheekbones with smile lines (2 curved lines per side, no wrinkle texture), calm crescent eyes (half closed) on the family kit; when opened they are sharp and bright; small straight brows; small firm mouth** | Big round glasses hide the eyes (white glint), tiny mouth |
| Hair | Grey bun | **White-grey hair `#E9E6DF` / shadow `#BDB8AE` pulled back flat into a tall round bun; two plain wooden pins `#8A5A33` crossed through it** | Small bun, wisps |
| Outfit, materials, wear | Sage jacket, white apron, light trousers | **Deep jade-green cotton jacket with a high collar and side opening, sleeves tied back above the elbows with an orange cord; long plain cream apron to mid-shin with an orange apron sash tied at the back (the family accent); dark trousers; black cloth shoes. Wear: flour on hands and forearms, a faded spot on the apron (free)** | Patched cardigan-style jacket, apron with flour handprints, slippers |
| Palette (hex) | jacket `#8FA88E`, apron `#F3ECDD`, trousers `#9A958A` | **jacket `#3F5E4E` / shadow `#2C4337`; apron `#F3ECDD` / `#D8CFBC`; trousers `#3A3633`; shoes `#24211F`; skin `#EFC9A8` / `#D9A882`; flour `#FFFDF7`; orange per kit** | cardigan `#6E7F66`, apron `#F1E8D6`, glasses rims `#3B2A1A` |
| Signature prop / pose | None | **A short thin wooden dumpling rolling pin (the real tool for xiaolongbao-style wrappers) carried in the apron sash like a conductor's baton and used to point; signature pose: hands folded on the apron, perfectly still, one eye opening** | Walking stick that is secretly a rolling pin |
| AI / animation risk | Medium: still generic, still the duplicate risk | **Low-medium: a distinct square silhouette and dark jacket stop the model merging her with the Uncle or cloning her; the crossed pins must stay big (at least 1/2 of head height)** | Medium: glasses are a classic drift item; the semi-chibi body clashes with B leads |
| Lock list (B) | | **1 tall round white-grey bun with two crossed wooden pins, 2 calm crescent eyes, 3 deep jade-green high-collar jacket, 4 long cream apron with orange sash, 5 orange sleeve cord, 6 short thin rolling pin, 7 dark trousers and black cloth shoes** | |
| Free / banned (B) | | Free: flour amount, apron stain. Banned: glasses, earrings, cardigan, headscarf, any second hair ornament | |

**Prompt core, B:**
```
Grandma, the old dumpling master: a tiny, sturdy elderly woman, 4.25 heads tall, square solid body with a low wide
stance, white-grey hair pulled back into a tall round bun pierced by two crossed plain wooden pins, calm half-closed
crescent eyes with smile lines, small straight brows, a deep jade-green cotton jacket with a high collar, sleeves tied
back with an orange cord, a long plain cream apron to mid-shin with an orange apron sash, dark trousers, black cloth
shoes, flour on her hands and forearms, a short thin wooden rolling pin tucked in her apron sash
```
Prompt core A: `Grandma: a short round elderly woman, 5 heads tall, grey bun, kind round face, sage-green jacket, white apron with an orange tie, grey trousers, black cloth shoes` · Prompt core C: `a very small, slightly bent elderly woman, 3.5 heads tall, small grey bun with wisps, big round spectacles that flash white, patched green jacket, floury apron, cloth slippers, a walking stick`

**12 expressions (Grandma):** 1 calm master (default: crescent eyes, faint smile) · 2 warm grandmother smile · 3 focused folding (eyes down, lips pressed) · 4 knowing smirk (one brow up) · 5 freeze-stare (eyes fully OPEN, the event: cliffhanger only) · 6 delighted laugh (hand over the mouth) · 7 stern (one eye opens) · 8 mild surprise · 9 teaching (pointing with the rolling pin, mouth open) · 10 moved, remembering Dad (soft wet eyes) · 11 deadpan at the Uncle (flat lids) · 12 proud nod (eyes closed, chin up).

**Idle / walk / run (Grandma):** idle = completely still, hands folded on the apron, blink only (stillness is her character) · walk = small quick shuffling steps, upright, 8-frame · run = she never runs: limited-animation "appears" gag (2 frames of speed lines, then she is there) · hands: 4-frame folding cycle on ones, then a dead stop (director-treatment).

---

### 3.4 Supporting cast slots

**Local teacher (one per episode).** Design rules shared by all directions: researched, respectful local working dress of the place and trade (sources noted in the episode file); no caricatured ethnic features, no accent jokes; jokes stay on the Uncle; at most 2 faces per clip (fix-plan rule 1), so the guest needs a strong single-character reference.

| | A. Documentary local | **B. Shape-coded guest kit (RECOMMENDED)** | C. Stylized archetypes |
|---|---|---|---|
| Idea | Naturalistic person, 5-6 heads, real clothing | Each guest is built from a template so he or she pops next to the trio and costs little to design | Exaggerated body types (tall-thin, tiny-round, broad) |
| Silhouette | Varies | **One primary shape the trio does not use (tall rectangle, inverted triangle, diamond, crescent), one break in the outline (hat, headscarf, tool)** | Extreme proportions |
| Proportions | 5.5-6 heads | **4.5-5.5 heads (between Grandma and the Uncle), on the family kit** | 3.5-7 heads |
| Palette | Location colors | **3 colors taken from that episode's location color script + one small orange touch (cord, tie, thread bracelet; never a wide sash: the sash marks the family)** | Free |
| Signature prop | Any | **One oversized tool of the craft they teach (cleaver, ladle, tea kettle, noodle stretch dough, mortar)** | Any |
| Face | Natural | **One face hook (brow shape, freckles, a gap, a beard shape); same eye construction as the family** | Big gag features |
| Cost | Same as B | **About 0.2 GPU-h per guest (4 concepts + mini sheet)** | Same |
| Risk | Blends into the background; generic | Low | Caricature risk: **not recommended** for real cultures |

Prompt template B: `[Name], a [trade] from [place], [N] heads tall, [primary shape] silhouette, [3 colors] [garments researched for place and trade], a small orange [cord/tie], holding [oversized tool], [face hook], calm confident expression`.

**The Camel (silent co-host who has seen everything; every episode).**

| | A. Current cute camel | **B. Deadpan co-host (RECOMMENDED)** | C. Plush toy camel |
|---|---|---|---|
| Species | Unspecified (one or two humps drift) | **Bactrian camel, two humps (the classic Silk Road caravan camel): an "M" silhouette no other character has** | Round one-hump plush |
| Shape / proportion | Realistic | **Simplified: long neck curve, two soft humps, head about 1/6 of body length, knobby knees** | Very round, short legs |
| Face | Natural | **Heavy half-closed lids with long lashes (permanent unimpressed look), side-to-side chewing jaw, small ears; the only expression change is a slow blink or one raised brow lump** | Big sparkly eyes |
| Palette | Tan | **coat `#C9A574` / shadow `#A48356`, winter tufts on humps and knees `#B08A5C`, muzzle `#E3CBA2`, eyes `#2A1E16`; halter: plain rope with one orange tassel** | Light beige |
| Signature | None | **Stare into the lens + slow chew; in the Uncle's caravan scenes carries a small saddle with a steamer basket** | |
| Movement | Generic | **Accurate pacing walk (both legs on one side move together), 6-frame side cycle; idle = chewing 4-frame loop + blink every 3-4 s** | |

**The Giant Dumpling (intro antagonist; must read instantly as a dumpling, original design, kid-safe scary-funny).**

| | A. Current egg monster | **B. Soup-dumpling titan (RECOMMENDED)** | C. Gyoza jaws |
|---|---|---|---|
| Silhouette | White egg with a vague top, shark teeth | **Squat teardrop, wider than tall, with about 18 clear pleats spiraling up to a twisted top knot (the classic soup-dumpling crown), so the outline alone says "dumpling"** | Crescent gyoza whose pleated edge opens as the mouth (pleats = teeth) |
| Mouth | Shark-tooth hole | **A wide horizontal mouth across the lower third that opens like a soft dough lid; rounded dough-bump teeth (no fangs); dark warm interior `#7A2E1F` with soup glow** | Pleat teeth |
| Face | None | **Two small glossy dark eyes high under the pleats and one pleat that works as a brow (gives it acting: smug, hungry, surprised)** | Eyes on the flat side |
| Skin | Matte white | **Slightly translucent dough `#FBF6EC` / shadow `#E5DCCB`, a golden soup glow `#F2C46B` visible through the lower skin, steam from the top knot (puffs harder when angry)** | Golden pan-fried bottom `#D49A4A` |
| Movement | Slides | **Bouncing hops with big squash on landing and wobble (jelly physics), 4-frame chomp cycle** | Snapping, hopping |
| Risk | Reads as a bun, an egg or a marshmallow | Low; check that it is not a round wedge-mouth shape like a well-known game character (the mouth is horizontal and the body is pleated: different by construction) | Good alternative for a later season villain; less "round" than the creator asked |

**Dad (memory only):** not a design direction: a tall slim vertical rectangle seen from behind, wearing the same cone hat at full size (shows that the Boy's hat is too big for the Boy), sepia `#8B6B4A` to `#E9D8B8`, soft blur, never the face. **Proposal for approval:** the chin-ribbon tails are the only color in the sepia frame (`#D9480F`), so the family accent links him to the Boy in every memory.

---

### 3.5 Recommendation and why

**B for the Boy, the Uncle and Grandma; B for the guest kit, the Camel and the Giant Dumpling.**
1. **Silhouettes become three different shapes** (triangle, circle, square), which is the most reliable pro tool for readability (R2-R4) and for the AI telling the characters apart (fewer merges and clones: the C11/C21/C32 failure mode).
2. **Fewest small details, biggest locked features** (6-7 per lead), which is what both "draw it 1000 times" (R5) and AI identity practice (R6) ask for. Expected effect: fewer rubric C4 costume failures and cleaner LoRA training data.
3. **Story lives in the design:** Dad's oversized hat (Grandma recognizes it), Dad's journal in the sash pouch, the Uncle's research chopsticks, the master's rolling pin. Props carry personality without dialogue.
4. **Comedy range is designed** (mobile brows, acting mustache, brim reveal, master's eye-opening, chibi gag sheet), matching the v4.4 directive for big anime comedy while keeping identity locked (R8).
5. **The Uncle the creator likes stays himself:** same body, jacket, sash, towel; only three changes (fully bald dome, thin curled mustache per the written rule, family-kit face). If the creator wants zero change, Uncle A is fully compatible with Boy B and Grandma B.
6. **C** is the right choice only if the show moves toward fewer, longer, prestige episodes with paid video tools; on the free pipeline its detail will drift and smear (fix-plan R4: small faces at 480x832).

---

## 4. Deliverables: the model-sheet package

Location after approval: `production/v4/model-sheets/<character>/` (Boy, Uncle, Grandma; Camel, Giant Dumpling, guest template, Dad). All labels, arrows and hex numbers are added on CPU in compositing, never generated (rubric B5/H6). Each view is generated as its own image on a flat cream background and assembled on CPU (multi-view sheets in one generation drift between views).

**Per lead (Boy, Uncle, Grandma):**
| File | Content | Used by |
|---|---|---|
| `<c>_turnaround.png` | Full body, 5 views: front, 3/4 front, side, 3/4 back, back; head-unit guide lines | stills, QC, LoRA |
| `<c>_head_turn.png` | Head, 5 views + up/down tilt | close-ups, LoRA |
| `<c>_construction.png` | Head construction and proportions (eye placement, brow gap, mustache/bun/brim size rules), lock / free / banned list | everyone |
| `<c>_expressions.png` | The 12 expressions above, head and shoulders, 3/4 view | stills, video prompts, LoRA |
| `<c>_mouths.png` + `mouths/*.png` | Mouth chart for Rhubarb shapes A-H + X, front and 3/4, cut out as transparent sprites | fix-plan Fix 5a |
| `<c>_hands.png` | 8 hand poses: relaxed, point, open palm, fist, holding chopsticks, holding the signature prop, thumbs-up, scared spread; 4 fingers + thumb drawn simply | stills, QC C6 |
| `<c>_poses.png` | Idle, walk (contact, down, passing, up), run (4 keys), signature pose, 4 gag poses (chibi, shock, collapse, triumph) | video keyframes |
| `<c>_gag.png` | Chibi 2.5-head version + 3 designed off-model faces, lock list kept | gag beats (C7) |
| `<c>_color.png` | Base / shadow / blush / line swatches with hex; the character under 4 lights: day exterior, warm interior, lantern night, sepia memory | color QC (G2), backgrounds |
| `<c>_props.png` | Signature props in 3 views with scale to the hand | stills |
| `<c>_dos_donts.png` | The 6 most likely off-model errors with the fix (e.g. Boy: thin ribbon, small hat, shoes; Uncle: side hair, thick mustache, towel on the wrong shoulder; Grandma: glasses, light jacket, no pins) | QC humans |
| `<c>.prompt.md` | Frozen prompt block, negative block, LoRA trigger word, reference file list | stills and clips agents |
| `refs/<c>_front.png`, `refs/<c>_34.png` | Clean single-character references (one character, flat background) | klein references (fix-plan Fix 1) |

**Cast-wide:** `cast_size_chart.png` (lineup to scale with the height lines of section 3.0, composited on CPU from single-character images, never generated as a group) · `cast_silhouettes.png` (black fills side by side, also at 64 px and 32 px) · `cast_values.png` (grayscale lineup) · `cast_palette.png` (all swatches) · `family_kit.png` (shared eye, brow, nose, mouth, line and shading rules) · `cast_expressions_compare.png` (same emotion across the three leads, to check one family).
**Supporting:** Camel (turnaround 3 views, 5 expressions, pacing walk 6 keys, saddle); Giant Dumpling (3 views, 6 face/mouth states, hop and chomp keys, steam states); guest template (blank kit + one worked example from the next episode's script); Dad (3 silhouette poses, sepia grade recipe).

---

## 5. Process, cost and hand-offs

### 5.1 Gates

| Gate | What the creator sees | Decides |
|---|---|---|
| **0 (now)** | This plan (Hebrew reading copy provided) | Approve the plan; optional early answers to the questions in 5.5 |
| **1. Concept thumbnails** | One board per character: 3 directions x 4 variants (full body + face), each shown in color, black silhouette, grayscale and at 64 px; the cast lineup to scale per direction; supporting cast 3 directions x 2 | Direction per character (or "mix") and the toggles in 5.5 |
| **2. Refined direction** | The picked direction, 6 variants per character + a face close-up row; lineup | Pick the final face/variant per character; small change notes |
| **3. Full sheets** | The model-sheet package of section 4 | Lock: "Model sheets v1.0". Only then are Ep 1 keyframes regenerated |
| **4. LoRA check** | 12 test stills per character made with the LoRA (new scenes, both orientations) next to the sheets, plus the identity scores | Approve the LoRAs for production |

Between gates the automatic checks run first (5.3), so the creator only sees images that passed.

### 5.2 GPU budget (free pipeline: FLUX.2 klein 4B on Kaggle T4; measured basis: about 20-25 s per 768x1344 klein image at 4 steps, `C12.json` 19.1 s; ep01v44-stills-001 128 images in about 50 min; about 8 min start-up per session)

| Step | Images / work | GPU-h |
|---|---|---|
| Gate 1 concepts | 3 leads x 3 directions x 4 variants full body (36) + face close-ups (18) + supporting 3 slots x 3 directions x 2 (18) = 72 images | **about 0.6-0.75** |
| Gate 2 refinement | 3 leads x (6 full + 4 face) + supporting 3 x 4 = 42 images | **about 0.4-0.5** |
| Gate 3 full sheets | per lead about 80 images (turnarounds 5x3, head turn 5x2, expressions 12x2, mouths 9, hands 8, poses 14, props 4) = 240; supporting about 70; + 25% re-rolls | **about 2.5-3.5** |
| Gate 4 LoRA data | 10 in-scene images per lead x 2 variants on varied backgrounds (so the LoRA does not learn the cream background) | **about 0.4** |
| LoRA smoke test | Boy, 300 steps, fp16 on T4 (no bf16), then test on the distilled model | **about 0.5-1.0 (est.)** |
| LoRA training | Boy, Uncle, Grandma; klein 4B Base, rank 16, 512-768 px, about 1,500-2,000 steps, lr 1e-4 (fix-plan estimate 2-3 GPU-h each) | **about 6-9 (est.)** |
| LoRA validation | 3 x 24 test stills with and without LoRA | **about 0.3** |
| **Total** | | **about 11-15 GPU-h** |

- **Before any creator choice only about 0.75 GPU-h is spent.** Gates 1-3 together are about 3.5-4.75 GPU-h and fit in fix-plan week 1 (planned about 8 h, stop line 22 h).
- **The LoRA line replaces fix-plan Fix 8** (6-9 GPU-h already planned for week 2), trained on the new designs instead of the old ones. Net addition of the redesign to the fix plan: about 4-5 GPU-h.
- **Sequencing with the fix plan:** the shot list rewrite, voices, word timestamps and the animatic (no GPU) continue now. Fix-plan day 2 "all keyframe stills" (1.5 GPU-h) waits for Gate 3, otherwise Ep 1 stills are made twice. The in-flight job `charsheets-v45-001` (sheets of the current designs) is not wasted: it is the Direction A baseline at Gate 1 and the bridge if the creator keeps A.
- GPU-h are counted the way `production/v4/gpu-ledger.md` counts them; every job logs there. Trainer: an MIT/Apache trainer with FLUX.2 klein support (AI-Toolkit is the one BFL lists; verify its license file and T4/fp16 support in the smoke test). Camel LoRA only if the Camel drifts in practice (+1.5 GPU-h); the Giant Dumpling needs no LoRA (prompt + one reference).

### 5.3 Automatic checks at each gate (CPU, no GPU)
- **Silhouette distinctness:** black fill on the flat background, scaled to the same height; overlap (IoU) between any two leads below 0.70 [Assumption: calibrate], and a person (or Claude) names each character from the 64 px strip.
- **Value separation:** the main mass of each lead at least 25 luma steps from the other two leads' main masses and from the background band planned behind him or her.
- **Palette:** median color of each locked part within Delta E 2000 of 6 of the swatch (rubric G2).
- **Proportion:** head-to-body ratio within plus or minus 0.25 head of the spec; Boy's head top at the Uncle's sash line plus or minus 10% in the lineup (rubric C5).
- **Head count:** exactly one character per sheet image (YuNet + the person counter planned in fix-plan Fix 7).
- **Identity spread (Gate 3 and 4):** DINOv2 embeddings of every sheet image per character; reject outliers beyond 2 SD of the centroid; the centroid becomes the rubric C2 reference.

### 5.4 Hand-offs to the other agents (after Gate 3)
| Agent / skill | Receives |
|---|---|
| Script writer (`write-episode-script`) | New signature beats: Boy's brim push and hand-on-hat run, the Uncle's chopstick draw and mustache acting, Grandma's eye-opening event, the Camel's chew-and-stare; the gag-sheet list (which off-model moments exist); size chart for staging 2-shots |
| Stills / keyframes (`make-episode-v4`, fix-plan Fix 1) | `<c>.prompt.md` blocks, `refs/` files, negative block, LoRA trigger words, "one character sheet per visible character" rule, background value rule (25 luma behind characters) |
| Video / motion | Idle, walk, run definitions; secondary-motion list (ribbon tails, sash tails, towel, mustache, bun pins stay rigid); gag deformation list; "camera at or below the Boy's eye line for his talk shots" |
| Lip-sync (fix-plan Fix 5a) | Mouth charts and transparent mouth sprites per character |
| QC (`qc_clips.py`, rubric C1-C7, G2) | Lock lists (C4 checklist), hex swatches (G2), size chart (C5), DINOv2 centroids (C2), dos-and-don'ts sheets for the human pass |
| Site and marketing (only with creator approval) | New `avatar.svg`, og-image and channel art from the approved sheets; deploy only after approval |
| Docs | Replace `production/character-bible.md` with a pointer to the sheets and the frozen prompt blocks; add the decision to `PRODUCTION-BIBLE.md` |

### 5.5 Questions for the creator (answer at Gate 0 or Gate 1)
1. Direction per character (recommendation: B, B, B).
2. Uncle: thin curled mustache (the written rule) or the thick v2 mustache? Fully bald or keep the side fringe of v2? (Gate 1 shows both.)
3. Boy: oversized "Dad's hat" yes or no?
4. Grandma: recurring "old master" across the series (mentor), or only the Ep 1 local?
5. Dad: may the orange ribbon be the only color in his sepia memories?
6. Camel: two humps (Bactrian, the classic Silk Road caravan camel)?
