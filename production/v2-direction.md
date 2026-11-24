# V2 Direction (creator request, 2026-11-24)

The v1 Episode 1 felt too kiddie and like "slides with crossfades". V2 goal: **a gripping, living animation for everyone**, curiosity first.

## Creator's brief (verbatim intent)
- Real animation feel, not just transitions between frames. More frames, a genuinely engaging video.
- **Human-style but drawn** (semi-realistic 2D, human proportions), not round/chibi. Currently it reads as made for little kids; the audience is everyone.
- **Faster pace.** Inspiration from *Avatar: The Last Airbender* and *Naruto* in rhythm and look, **never copying** characters, designs, compositions, music or any recognizable pattern.
- Must make any viewer curious. Everything in English.

## Look (v2)
Semi-realistic 2D adventure animation: cel-shaded characters with clean ink lines, human proportions and expressive faces, painterly atmospheric backgrounds, cinematic light (rim light, golden hour, lantern glow), dynamic camera angles (low angle, dutch tilt, extreme close-ups of eyes and hands), hand-painted textures. Food shots are lush and appetizing. Humor stays, but played straighter (comic timing, not cartoon-baby).
Characters keep their identity (so the series stays coherent) but are redrawn older and less cute:
- **Boy (Bo), about 13:** lean, determined, curious eyes; conical leaf hat with orange chin ribbon; white kimono-style wrap jacket with orange belt; small canvas shoulder bag.
- **Uncle Fong, about 45:** broad and heavy, bald, thin mustache, warm sly face; white kimono with wide orange belt (sauce stains).
- **Grandma (Auntie), about 70:** small, grey bun, soft green jacket, apron, sharp kind eyes.
- **Dad:** only a sepia silhouette from behind in the conical hat; never his face.
Palette still anchored on orange `#D9480F`, cream `#FFFAF0`, leaf yellow `#ECC66A`, brown `#3B2A1A`, plus deeper cinematic tones.
Avoid: One Piece / Avatar / Naruto characters, symbols, costumes, or shot-for-shot compositions.

## Pace and editing
Average shot 1.5-2.5 s (about 50-60 shots for 2:00), a cold-open hook in the first 3 s, a curiosity gap every ~15 s (a question the next beat answers), motion on every shot, beat-synced cuts, no dead air. Quiet heart moments are allowed but short (<= 6 s).
Anime-style limited-animation tricks: smash zoom/punch-ins, speed lines, impact frames (hold + white flash + shake), whip-pan transitions, parallax drift, particles (dust, embers, petals, steam), film grain, vignette, color grading, light rays.

## Spec option names (shared contract between tool and scripts)
Shot-level (all optional): `punch: [{t, scale}]`, `speedlines: {t, d, dir: "radial|horizontal"}`, `impact: {t}`, `whip: true` (transition into this shot is a whip-pan with motion blur), `particles: {type: "dust|embers|petals|steam|snow", n}`, `rays: true`, `grade: "warm|cool|sepia|none"`, `layers: {bg, fg}` (fg PNG with alpha, different drift speeds). Global: `grain: true`, `vignette: 0-1`.
Music moods: `adventure` (taiko + plucked strings + flute, ~120 BPM), `tension`, `epic`, `tender`, `cozy`, `sparse`, `off`.
SFX names added: `impact`, `riser`, `taiko`, `swoosh_big`, `crack`, `gong`.
Voices: `boy` (older, less pitched up), `uncle`, `grandma`, `dad`, `narrator` (calm, deeper).

## Work breakdown
1. Art director: v2 character reference images in Canva -> `production/v2-references.md` (IDs) and `character-bible.md` v2 block.
2. Engine: implement the options above in `tools/episode_maker`, backwards compatible with `episode-01.json`.
3. Story editor: `scripts/episode-01-v2.md`, `tools/episode_maker/specs/episode-01-v2.json`, `production/ep01-v2-frame-list.md` (~55 frames with prompts).
4. Frame generation + Canva export (after 1 and 3), then render, then send to the creator for approval.
