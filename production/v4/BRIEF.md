# V4 brief: from "moving pictures" to a real short anime-style series (creator notes, 2026-11-25)

## Creator's verdict on what exists
- Episode 1 v3 (65 shots, 2:00, still frames + camera + FX): **only the captions are right.** Everything else must improve.
- Puppet demo (cut-out characters that breathe, blink, flap mouth, squash): **not the style at all.**
- What the creator expects: **full animated sequences, like a short anime series. A VIDEO, not image frames with effects.** Breathing, blinking, lip sync etc. matter, but as part of real animation (characters walk, turn, gesture, react, the camera moves through a living scene), not as expression on a still picture.

## Consequences
- Still a ~2:00 vertical episode (9:16, mobile 720x1280 delivery, full 1080x1920 master).
- Real video with fast cutting needs MORE: more dialogue/lines, more story content, more source frames/keyframes/assets to drive the animation. The script must be reviewed and expanded accordingly.

## Script notes
- General direction is good, but it feels too much for little kids. Target: **everyone** (teens and adults too, family-safe).
- **Funnier.** Research how critics/reviewers explain what makes all-ages animation and food/travel shows funny, and build a deliberate comedy style.
- **Two atmospheres at once:** (1) the ancient Silk Road / old-history mood (legends, old towns, travelers, caravans, dynasties), and (2) the BOY is a **tour-guide host of a show**, like a world food-travel program that visits places (talks to camera, presents places and food, Uncle is the chaotic co-host).

## Fixed constraints (do not break)
- The DRAWING stays: the approved round, soft, cute picture-book characters (Boy: Vietnamese conical leaf hat with orange chin ribbon, white kimono with orange belt; Uncle: big, bald, thin mustache, white kimono with wide orange belt, "For science!"; Grandma; Dad only as a sepia silhouette from behind). Only the FEEL changes: fast, living, kicking, anime-like rhythm (inspired by Avatar: The Last Airbender / Naruto pacing, never copying characters, designs, compositions, music or recognizable patterns).
- Full anonymity: no personal name/email anywhere. Public identity only: The Dumpling Boy, @TheDumplingBoy.studio, thedumplingboy.netlify.app, ko-fi.com/thedumplingboy.
- All deliverables in English. Kid-safe and respectful: jokes on the Uncle, never on a country or people. History uses "Legend says / Many people believe" unless firmly established, with real sources. No upload or public posting.
- Never commit private links (claude.ai artifact URLs) or secrets.

## Technical reality of this environment
- Cloud container: 4 CPU, 15 GB RAM, **no GPU**. GitHub, PyPI, npm reachable; huggingface.co blocked. ffmpeg present, node 22, python3.
- Existing local pipeline: `tools/episode_maker` (Kokoro TTS voices, synthesized music/SFX, captions, camera FX, layers, puppets). Captions are approved.
- Canva connector: image generation works (two characters together or no-face frames succeed best; boy alone fails often). Canva video quota returns 2026-12-16.
- Character reference images in Canva: Boy MAHbzwNGxJo, Uncle MAHbzx4PTVI, Grandma MAHb0FNIPP4. Cut-outs: `tools/episode_maker/specs/puppets/*.png`.
- The creator will consider paying for an external tool ONLY if something free truly blocks quality; first find free repos/tools.

## Team (each writes to production/v4/)
- video-tech.md: video/animation engineer (free repos, how to get real animation)
- content-research.md: content researcher (Ep 1-3 material)
- comedy-style.md + scripts: copywriter
- director-treatment.md: director
- marketing.md: marketing and business
- advisor-review.md: senior advisor review
