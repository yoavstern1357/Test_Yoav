# V2 Direction (creator request, 2026-11-24)

V2 goal: keep the v1 drawing, but make the episode a **gripping, living, kicking story for everyone** (fast pace, living camera, curiosity first). v1 felt like slides with crossfades.

## Creator's brief (verbatim intent)
- Real animation feel, not just transitions between frames. More frames, a genuinely engaging video.
- **Human-style but drawn** (semi-realistic 2D, human proportions), not round/chibi. Currently it reads as made for little kids; the audience is everyone.
- **Faster pace.** Inspiration from *Avatar: The Last Airbender* and *Naruto* in rhythm and look, **never copying** characters, designs, compositions, music or any recognizable pattern.
- Must make any viewer curious. Everything in English.

## Look (UPDATED by the creator: keep the drawing exactly as in v1)
The art does NOT change. Keep the approved v1 characters and style: soft children's picture-book 2D cartoon, very round friendly shapes, big expressive eyes, bright pastel colors, soft warm lighting. Character reference IDs stay: Boy `MAHbzwNGxJo`, Uncle `MAHbzx4PTVI`, Grandma `MAHb0FNIPP4`. Only the FEELING changes: a lively, kicking, live-story energy with fast pace, living camera and anime-like rhythm.
(The earlier "semi-realistic redraw" idea was cancelled; ignore any mention of it.)

## Pace and editing
Average shot 1.5-2.5 s (about 50-60 shots for 2:00), a cold-open hook in the first 3 s, a curiosity gap every ~15 s (a question the next beat answers), motion on every shot, beat-synced cuts, no dead air. Quiet heart moments are allowed but short (<= 6 s).
Anime-style limited-animation tricks: smash zoom/punch-ins, speed lines, impact frames (hold + white flash + shake), whip-pan transitions, parallax drift, particles (dust, embers, petals, steam), film grain, vignette, color grading, light rays.

## Spec option names (shared contract between tool and scripts)
Shot-level (all optional): `punch: [{t, scale}]`, `speedlines: {t, d, dir: "radial|horizontal"}`, `impact: {t}`, `whip: true` (transition into this shot is a whip-pan with motion blur), `particles: {type: "dust|embers|petals|steam|snow", n}`, `rays: true`, `grade: "warm|cool|sepia|none"`, `layers: {bg, fg}` (fg PNG with alpha, different drift speeds). Global: `grain: true`, `vignette: 0-1`.
Music moods: `adventure` (taiko + plucked strings + flute, ~120 BPM), `tension`, `epic`, `tender`, `cozy`, `sparse`, `off`.
SFX names added: `impact`, `riser`, `taiko`, `swoosh_big`, `crack`, `gong`.
Voices: `boy` (older, less pitched up), `uncle`, `grandma`, `dad`, `narrator` (calm, deeper).

## Work breakdown (art director step cancelled: no new character references)
1. Art director: v2 character reference images in Canva -> `production/v2-references.md` (IDs) and `character-bible.md` v2 block.
2. Engine: implement the options above in `tools/episode_maker`, backwards compatible with `episode-01.json`.
3. Story editor: `scripts/episode-01-v2.md`, `tools/episode_maker/specs/episode-01-v2.json`, `production/ep01-v2-frame-list.md` (~55 frames with prompts).
4. Frame generation + Canva export (after 1 and 3), then render, then send to the creator for approval.
